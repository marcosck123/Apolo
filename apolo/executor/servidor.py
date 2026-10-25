"""Executor descartável de exemplos Python; o isolamento de rede pertence ao container."""
import ast
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

LIMITE_SAIDA = 10_000


def limitar_recursos():
    resource.setrlimit(resource.RLIMIT_CPU, (6, 6))
    resource.setrlimit(resource.RLIMIT_AS, (128 * 1024**2, 128 * 1024**2))
    resource.setrlimit(resource.RLIMIT_NPROC, (16, 16))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def executar(codigo, entradas=None, tempo_limite=5):
    inicio = time.monotonic()
    estourou = False
    # Arquivos limitados evitam acumular stdout/stderr ilimitados na memória do servidor.
    with tempfile.TemporaryDirectory(prefix='apolo-') as pasta:
        caminho = Path(pasta)
        (caminho / 'exemplo.py').write_text(codigo, encoding='utf-8')
        (caminho / 'entrada').write_text(''.join(str(e) + '\n' for e in (entradas or [])), encoding='utf-8')
        with open(caminho / 'entrada', 'rb') as entrada, open(caminho / 'saida', 'w+b') as saida, open(caminho / 'erro', 'w+b') as erro:
            processo = subprocess.Popen(
                [sys.executable, '-I', '-B', str(caminho / 'exemplo.py')], cwd=pasta,
                stdin=entrada, stdout=saida, stderr=erro, env={'LANG': 'C.UTF-8'},
                start_new_session=True, preexec_fn=limitar_recursos,
            )
            try:
                processo.wait(timeout=tempo_limite)
            except subprocess.TimeoutExpired:
                estourou = True
            finally:
                # Também encerra descendentes que sobreviveram ao processo principal.
                try:
                    os.killpg(processo.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                processo.wait()
            saida.seek(0)
            erro.seek(0)
            texto_saida = saida.read(LIMITE_SAIDA * 4).decode('utf-8', errors='replace')[:LIMITE_SAIDA]
            texto_erro = erro.read(LIMITE_SAIDA * 4).decode('utf-8', errors='replace')[:LIMITE_SAIDA]
            if estourou:
                texto_erro = 'Tempo limite de execução excedido.'
            elif processo.returncode and not texto_erro:
                texto_erro = f'Processo encerrado com código {processo.returncode}.'
    return {'saida': texto_saida, 'erro': texto_erro, 'tempo_ms': round((time.monotonic() - inicio) * 1000), 'estourou_tempo': estourou}


def analisar(codigo):
    if not isinstance(codigo, str) or not codigo.strip() or len(codigo) > 20_000:
        raise ValueError('código inválido')
    try:
        arvore = ast.parse(codigo)
    except (SyntaxError, RecursionError) as erro:
        raise ValueError('sintaxe ou profundidade inválida') from erro
    pilha = [(arvore, 0)]
    nos = []
    while pilha:
        no, profundidade = pilha.pop()
        if profundidade > 60 or len(nos) >= 5000:
            raise ValueError('análise excedeu os limites')
        nos.append(no)
        pilha.extend((filho, profundidade + 1) for filho in ast.iter_child_nodes(no))
    def nome(no):
        if isinstance(no, ast.Name):
            return no.id
        if isinstance(no, ast.Attribute):
            return nome(no.value) + '.' + no.attr
        return ''
    aliases = {}
    for no in nos:
        if isinstance(no, ast.Import):
            for alias in no.names:
                aliases[alias.asname or alias.name.split('.')[0]] = alias.name if alias.asname else alias.name.split('.')[0]
        elif isinstance(no, ast.ImportFrom) and no.module:
            for alias in no.names:
                aliases[alias.asname or alias.name] = no.module + '.' + alias.name
    # Não atribui a descrição de uma função nativa a um nome redefinido pelo exemplo.
    redefinidos = {no.id for no in nos if isinstance(no, ast.Name) and isinstance(no.ctx, ast.Store)}
    redefinidos |= {no.arg for no in nos if isinstance(no, ast.arg)}
    redefinidos |= {no.name for no in nos if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
    def chamada(no):
        partes = nome(no).split('.')
        if partes[0] in redefinidos:
            return ''
        partes[0] = aliases.get(partes[0], partes[0])
        return '.'.join(partes)
    estruturas = {'For': 'for', 'AsyncFor': 'for', 'While': 'while', 'If': 'if',
                  'Try': 'try', 'With': 'with', 'AsyncWith': 'with', 'Lambda': 'lambda',
                  'ClassDef': 'class', 'FunctionDef': 'def', 'AsyncFunctionDef': 'def',
                  'Return': 'return', 'Yield': 'yield', 'YieldFrom': 'yield',
                  'ListComp': 'comprehension', 'SetComp': 'comprehension',
                  'DictComp': 'comprehension', 'GeneratorExp': 'comprehension'}
    linhas = codigo.splitlines(keepends=True)
    def posicao(linha, coluna):
        return len(''.join(linhas[:linha - 1])) + len(linhas[linha - 1].encode('utf-8')[:coluna].decode('utf-8'))
    trechos = []
    for no in nos:
        tipo = None
        if isinstance(no, ast.Constant) and type(no.value) in (int, float, str):
            tipo = 'texto' if isinstance(no.value, str) else 'numero'
        elif isinstance(no, ast.List):
            tipo = 'lista'
        if tipo:
            trechos.append({'tipo': tipo, 'inicio': posicao(no.lineno, no.col_offset),
                            'fim': posicao(no.end_lineno, no.end_col_offset)})
    return {
        'funcoes': sorted({no.name for no in nos if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))}),
        'importacoes': sorted({alias.name for no in nos if isinstance(no, ast.Import) for alias in no.names}
                             | {no.module for no in nos if isinstance(no, ast.ImportFrom) and no.module}),
        'chamadas': sorted({chamada(no.func) for no in nos if isinstance(no, ast.Call)} - {''}),
        'estruturas': sorted({estruturas[type(no).__name__] for no in nos if type(no).__name__ in estruturas}),
        'trechos': trechos,
    }


class Servidor(BaseHTTPRequestHandler):
    def responder(self, estado, dados):
        corpo = json.dumps(dados, ensure_ascii=False).encode('utf-8')
        self.send_response(estado)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        self.responder(200 if self.path == '/saude' else 404, {'ok': self.path == '/saude'})

    def do_POST(self):
        if self.path not in ('/executar', '/analisar'):
            return self.responder(404, {'erro': 'rota desconhecida'})
        try:
            tamanho = int(self.headers.get('Content-Length', '0'))
            if not 0 < tamanho <= 100_000:
                raise ValueError('corpo inválido ou muito grande')
            dados = json.loads(self.rfile.read(tamanho))
            if not isinstance(dados, dict) or dados.get('linguagem') != 'python':
                raise ValueError('linguagem deve ser python')
            codigo = dados.get('codigo')
            entradas = dados.get('entradas', [])
            if not isinstance(codigo, str) or not codigo.strip() or len(codigo) > 20_000:
                raise ValueError('código inválido')
            if not isinstance(entradas, list) or len(entradas) > 100 or any(not isinstance(e, str) or len(e) > 1000 for e in entradas):
                raise ValueError('entradas inválidas')
        except (ValueError, TypeError) as erro:
            return self.responder(400, {'erro': str(erro)})
        try:
            self.responder(200, analisar(codigo) if self.path == '/analisar' else executar(codigo, entradas))
        except ValueError as erro:
            self.responder(400, {'erro': str(erro)})
        except Exception:
            self.responder(500, {'erro': 'executor indisponível'})


if __name__ == '__main__':
    HTTPServer(('0.0.0.0', 5000), Servidor).serve_forever()
