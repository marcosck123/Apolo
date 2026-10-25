"""Ferramentas comuns: executa cada exemplo de código de verdade e monta os blocos de texto.
Nenhuma saída é escrita à mão: tudo que aparece depois de "Saída:" foi produzido rodando o código.
"""
import contextlib
import io
import os
import tempfile

PASTA_EXEC = tempfile.mkdtemp(prefix="apolo_exec_")


class ErroInesperado(Exception):
    pass


def rodar(codigo, entradas=None):
    """Executa `codigo` e devolve (saida, erro). `entradas` simula o que o usuário digitaria em input()."""
    buf = io.StringIO()
    env = {"__name__": "__main__"}
    if entradas is not None:
        fila = iter(entradas)

        def input_simulado(prompt=""):
            valor = next(fila)
            buf.write(f"{prompt}{valor}\n")  # o terminal mostra o que foi digitado
            return valor

        env["input"] = input_simulado
    antes = os.getcwd()
    os.chdir(PASTA_EXEC)
    erro = None
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(codigo, "programa.py", "exec"), env)
    except Exception as e:  # noqa: BLE001 - queremos mostrar o erro como o Python mostraria
        erro = f"{type(e).__name__}: {e}"
    finally:
        os.chdir(antes)
    return buf.getvalue().rstrip("\n"), erro


def _sem_linha_vazia(texto, onde):
    if "\n\n" in texto:
        raise ErroInesperado(f"linha vazia dentro de {onde}:\n{texto}")


def exemplo(pergunta, codigo, explicacao=None, entradas=None, erro_esperado=False, rotulo="Exemplo:"):
    """Bloco: pergunta/título, código, saída real e explicação. Sem linhas vazias dentro do bloco,
    para que a linha vazia continue significando 'fim de um bloco' para o córtex."""
    codigo = codigo.strip("\n")
    _sem_linha_vazia(codigo, pergunta)
    saida, erro = rodar(codigo, entradas)
    if erro and not erro_esperado:
        raise ErroInesperado(f"{pergunta}\n{codigo}\n-> {erro}")
    if erro_esperado and not erro:
        raise ErroInesperado(f"esperava erro em: {pergunta}\n{codigo}")
    partes = [pergunta, rotulo, codigo]
    if saida:
        _sem_linha_vazia(saida, pergunta)
        partes += ["Saída:", saida]
    if erro:
        partes += ["Erro:", erro]
    if explicacao:
        texto = explicacao(saida, erro) if callable(explicacao) else explicacao
        _sem_linha_vazia(texto, pergunta)
        partes.append(texto)
    return "\n".join(partes)


def exercicio(enunciado, codigo, explicacao=None, entradas=None):
    return exemplo(f"Exercício: {enunciado}", codigo, explicacao, entradas, rotulo="Solução:")


def qa(pergunta, resposta):
    _sem_linha_vazia(resposta, pergunta)
    return f"{pergunta}\n{resposta}"


def licao(titulo, *paragrafos):
    texto = "\n".join(p.strip() for p in paragrafos)
    _sem_linha_vazia(texto, titulo)
    return f"Lição: {titulo}\n{texto}"


def lista_py(xs):
    return repr(xs)


def soma_texto(xs):
    return " + ".join(str(x) for x in xs) + f" = {sum(xs)}"


# ---------- bancos de palavras para variar os exercícios ----------
NOMES = ["Ana", "Bruno", "Carla", "Diego", "Eduarda", "Felipe", "Gabriela", "Heitor", "Isabela",
         "João", "Karina", "Lucas", "Mariana", "Nicolas", "Olívia", "Pedro", "Rafaela", "Samuel",
         "Tatiane", "Vitor", "Yasmin", "Marcos", "Beatriz", "Caio", "Larissa", "Rodrigo", "Sofia"]
FRUTAS = ["maçã", "banana", "laranja", "uva", "manga", "abacaxi", "pera", "melancia", "goiaba",
          "caju", "açaí", "limão", "mamão", "morango", "kiwi"]
PRODUTOS = [("arroz", 25.9), ("feijão", 8.5), ("café", 18.0), ("leite", 5.4), ("pão", 1.2),
            ("açúcar", 4.8), ("óleo", 7.9), ("sabão", 3.5), ("macarrão", 4.25), ("ovos", 12.0),
            ("queijo", 32.0), ("farinha", 6.3), ("sal", 2.1), ("manteiga", 11.5)]
CIDADES = ["Vilhena", "Porto Velho", "Cuiabá", "Manaus", "Belém", "Recife", "Salvador", "Curitiba",
           "Florianópolis", "Goiânia", "Natal", "Fortaleza", "Campinas", "Londrina", "Valência"]
ANIMAIS = ["cachorro", "gato", "cavalo", "pato", "coelho", "tartaruga", "peixe", "papagaio", "vaca"]
CORES = ["azul", "verde", "vermelho", "amarelo", "preto", "branco", "roxo", "laranja", "cinza"]
PALAVRAS = ["casa", "livro", "escola", "computador", "janela", "programa", "caderno", "jardim",
            "cidade", "estrada", "banana", "teclado", "mesa", "cadeira", "relógio", "planeta"]
PALINDROMOS = ["arara", "osso", "radar", "reviver", "ovo", "ana", "salas", "rir", "matam", "esse"]
VARS_NUM = ["x", "n", "numero", "valor", "total", "quantidade", "idade", "nota", "preco", "pontos"]


# ---------- outras linguagens: cada uma também é executada de verdade ----------
import json
import re
import sqlite3
import subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))


def _sem_vazias(texto):
    """Dentro de um bloco a linha vazia significa 'fim do bloco', então as saídas não podem ter."""
    return "\n".join(l.rstrip() for l in texto.splitlines() if l.strip())


def _bloco(pergunta, codigo, saida, erro, explicacao, rotulo="Exemplo:"):
    partes = [pergunta, rotulo, codigo]
    if saida:
        partes += ["Saída:", saida]
    if erro:
        partes += ["Erro:", erro]
    if explicacao:
        texto = explicacao(saida, erro) if callable(explicacao) else explicacao
        _sem_linha_vazia(texto, pergunta)
        partes.append(texto)
    return "\n".join(partes)


# ----- SQL (SQLite em memória; a parte básica da linguagem é igual à do PostgreSQL) -----
def rodar_sql(codigo):
    """Executa os comandos em ordem. Cada SELECT imprime uma linha de colunas e uma linha por registro."""
    con = sqlite3.connect(":memory:")
    saida, erro = [], None
    try:
        for comando in [c.strip() for c in codigo.split(";") if c.strip()]:
            cur = con.execute(comando)
            if cur.description:
                saida.append(" | ".join(d[0] for d in cur.description))
                for linha in cur.fetchall():
                    saida.append(" | ".join("NULL" if v is None else str(v) for v in linha))
    except sqlite3.Error as e:
        erro = f"{type(e).__name__}: {e}"
    finally:
        con.close()
    return "\n".join(saida), erro


def exemplo_sql(pergunta, codigo, explicacao=None, erro_esperado=False, rotulo="Exemplo:"):
    codigo = codigo.strip("\n")
    _sem_linha_vazia(codigo, pergunta)
    saida, erro = rodar_sql(codigo)
    if bool(erro) != erro_esperado:
        raise ErroInesperado(f"SQL: {pergunta}\n{codigo}\n-> {erro}")
    return _bloco(pergunta, codigo, saida, erro, explicacao, rotulo)


def exercicio_sql(enunciado, codigo, explicacao=None):
    return exemplo_sql(f"Exercício: {enunciado}", codigo, explicacao, rotulo="Solução:")


# ----- Terminal e Git (bash numa pasta nova, com data e autor fixos para a saída não variar) -----
AMBIENTE = {
    "PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C.UTF-8", "TZ": "UTC", "TERM": "dumb",
    "GIT_AUTHOR_NAME": "Ana", "GIT_AUTHOR_EMAIL": "ana@exemplo.com", "GIT_COMMITTER_NAME": "Ana",
    "GIT_COMMITTER_EMAIL": "ana@exemplo.com", "GIT_AUTHOR_DATE": "2026-01-10T12:00:00",
    "GIT_COMMITTER_DATE": "2026-01-10T12:00:00", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
}


def rodar_shell(comandos):
    pasta = tempfile.mkdtemp(prefix="apolo_sh_")
    env = dict(AMBIENTE, HOME=pasta)
    r = subprocess.run(["bash", "--norc", "-c", comandos], cwd=pasta, env=env, capture_output=True, text=True, timeout=20)
    saida = _sem_vazias(r.stdout + r.stderr)
    return saida.replace(pasta, "/home/ana/projeto"), None


def exemplo_shell(pergunta, comandos, explicacao=None, rotulo="Exemplo:"):
    comandos = comandos.strip("\n")
    _sem_linha_vazia(comandos, pergunta)
    saida, _ = rodar_shell(comandos)
    return _bloco(pergunta, comandos, saida, None, explicacao, rotulo)


def exercicio_shell(enunciado, comandos, explicacao=None):
    return exemplo_shell(f"Exercício: {enunciado}", comandos, explicacao, rotulo="Solução:")


# ----- JavaScript (Node dentro do Docker, um processo só para todos os exemplos) -----
class NodeRunner:
    def __init__(self):
        self.proc = None

    def _abrir(self):
        self.proc = subprocess.Popen(
            ["docker", "run", "-i", "--rm", "-v", f"{AQUI}/runner_js.js:/r.js:ro", "node:22-slim", "node", "/r.js"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)

    def rodar(self, codigo):
        if self.proc is None:
            self._abrir()
        self.proc.stdin.write(json.dumps({"codigo": codigo}) + "\n")
        self.proc.stdin.flush()
        r = json.loads(self.proc.stdout.readline())
        return r["saida"].rstrip("\n"), r["erro"]

    def fechar(self):
        if self.proc:
            self.proc.stdin.close()
            self.proc.wait(timeout=10)


NODE = NodeRunner()


def exemplo_js(pergunta, codigo, explicacao=None, erro_esperado=False, rotulo="Exemplo:"):
    codigo = codigo.strip("\n")
    _sem_linha_vazia(codigo, pergunta)
    saida, erro = NODE.rodar(codigo)
    if bool(erro) != erro_esperado:
        raise ErroInesperado(f"JS: {pergunta}\n{codigo}\n-> {erro}")
    _sem_linha_vazia(saida, pergunta)
    return _bloco(pergunta, codigo, saida, erro, explicacao, rotulo)


def exercicio_js(enunciado, codigo, explicacao=None):
    return exemplo_js(f"Exercício: {enunciado}", codigo, explicacao, rotulo="Solução:")
