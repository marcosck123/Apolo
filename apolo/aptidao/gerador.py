"""Gerador de problemas NOVOS para medir o córtex.

Reaproveita as famílias de exercícios de scripts/gerar_programacao (sem alterá-las), com sementes
9000+ (o treino usou 6 a 11) e descarta qualquer problema cujo enunciado exato já apareça no
corpus de treino (textos/corpus_portugues.txt e textos/curriculo/*).

Cada problema: {id, categoria, tipo, enunciado, prompt, referencia, entradas, saida_esperada}.
"""
import json
import os
import random
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_GER = os.path.join(RAIZ, "scripts", "gerar_programacao")
if PASTA_GER not in sys.path:
    sys.path.insert(0, PASTA_GER)

import lib  # noqa: E402  (precisa vir antes dos módulos, para podermos observar as chamadas)

CATEGORIAS = ["python_basico", "python_intermediario", "python_extra", "sql", "terminal"]
MODULOS = {"python_basico": "basico", "python_intermediario": "intermediario",
           "python_extra": "python_extra", "sql": "sql", "terminal": "terminal"}
TIPO = {"python_basico": "python", "python_intermediario": "python", "python_extra": "python",
        "sql": "sql", "terminal": "shell"}

# ---- observação das chamadas de lib (a saída esperada vem de executar de verdade, como no treino) ----
_ultimo = {}
_registro = []


def _envolver_exec(nome, tipo):
    original = getattr(lib, nome)

    def f(codigo, *a, **k):
        saida, erro = original(codigo, *a, **k)
        entradas = a[0] if a else k.get("entradas")
        _ultimo.update(tipo=tipo, codigo=codigo, entradas=entradas, saida=saida, erro=erro)
        return saida, erro
    setattr(lib, nome, f)


def _envolver_exercicio(nome):
    original = getattr(lib, nome)

    def f(enunciado, codigo, *a, **k):
        bloco = original(enunciado, codigo, *a, **k)
        entradas = k.get("entradas", a[1] if len(a) > 1 else None)
        _registro.append({"enunciado": enunciado, "codigo": codigo.strip("\n"), "tipo": _ultimo["tipo"],
                          "entradas": list(entradas) if entradas else None, "saida": _ultimo["saida"]})
        return bloco
    setattr(lib, nome, f)


for _n, _t in (("rodar", "python"), ("rodar_sql", "sql"), ("rodar_shell", "shell")):
    _envolver_exec(_n, _t)
for _n in ("exercicio", "exercicio_sql", "exercicio_shell"):
    _envolver_exercicio(_n)

import importlib  # noqa: E402

_cache_modulos = {}


def _modulo(categoria):
    if categoria not in _cache_modulos:
        _cache_modulos[categoria] = importlib.import_module(MODULOS[categoria])
    return _cache_modulos[categoria]


# ---- anti-contaminação ----
_RE_ENUNC = re.compile(r"^Exercício: (.*)$")


def carregar_enunciados_treino(raiz=RAIZ, arquivos=None):
    """Conjunto com todos os enunciados 'Exercício: ...' do corpus e do currículo."""
    if arquivos is None:
        arquivos = [os.path.join(raiz, "textos", "corpus_portugues.txt")]
        pasta = os.path.join(raiz, "textos", "curriculo")
        if os.path.isdir(pasta):
            arquivos += [os.path.join(pasta, f) for f in sorted(os.listdir(pasta)) if f.endswith(".txt")]
    conjunto = set()
    for caminho in arquivos:
        if not os.path.exists(caminho):
            continue
        with open(caminho, encoding="utf-8", errors="replace") as f:
            for linha in f:
                if linha.startswith("Exercício: "):
                    conjunto.add(linha[len("Exercício: "):].rstrip("\n"))
    return conjunto


def gerar_categoria(categoria, quantidade, semente, proibidos, max_rodadas=40):
    """Devolve (problemas, descartados_por_contaminacao, duplicados)."""
    modulo = _modulo(categoria)
    vistos, problemas = set(), []
    contaminados = duplicados = 0
    indice = CATEGORIAS.index(categoria)
    for rodada in range(max_rodadas):
        if len(problemas) >= quantidade:
            break
        rng = random.Random(semente + indice * 100000 + rodada)
        _registro.clear()
        modulo.exercicios(rng, max(quantidade * 2, 60))
        for r in list(_registro):
            if len(problemas) >= quantidade:
                break
            if r["enunciado"] in vistos:
                duplicados += 1
                continue
            vistos.add(r["enunciado"])
            if r["enunciado"] in proibidos:
                contaminados += 1
                continue
            problemas.append({
                "id": f"{categoria}-{semente}-{len(problemas):04d}",
                "categoria": categoria,
                "tipo": r["tipo"],
                "enunciado": r["enunciado"],
                "prompt": f"Exercício: {r['enunciado']}\nSolução:\n",
                "referencia": r["codigo"],
                "entradas": r["entradas"],
                "saida_esperada": r["saida"],
            })
    return problemas, contaminados, duplicados


def gerar(n_total=100, semente=9000, categorias=None, proibidos=None):
    """n_total é dividido igualmente entre as categorias. Devolve (problemas, estatisticas)."""
    categorias = categorias or CATEGORIAS
    if proibidos is None:
        proibidos = carregar_enunciados_treino()
    por_cat = max(1, -(-n_total // len(categorias)))
    todos, stats = [], {}
    for c in categorias:
        p, cont, dup = gerar_categoria(c, por_cat, semente, proibidos)
        todos += p
        stats[c] = {"gerados": len(p), "contaminados": cont, "duplicados": dup}
    return todos, stats


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Gera problemas novos (JSONL).")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--semente", type=int, default=9000)
    ap.add_argument("--categorias", nargs="*", default=None)
    ap.add_argument("--saida", default="-")
    a = ap.parse_args()
    ps, st = gerar(a.n, a.semente, a.categorias)
    out = sys.stdout if a.saida == "-" else open(a.saida, "w", encoding="utf-8")
    for p in ps:
        out.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(json.dumps(st, ensure_ascii=False), file=sys.stderr)
