#!/usr/bin/env python3
"""Monta o corpus de português do córtex.

1. limpa o Tatoeba (frases) e a Wikipédia em português (parquet) para textos/corpus_partes/
2. separa uma fração de unidades únicas de cada fonte em textos/corpus_validacao.txt (cada uma UMA vez, fora do treino;
   use com `cortex_v0.py treinar --val_dados textos/corpus_validacao.txt`)
3. mistura o resto com pesos em textos/corpus_portugues.txt

Uso (dentro de um Python com pyarrow, ex.: docker run python:3.12-slim):
  python3 scripts/montar_corpus.py --tatoeba por_sentences_detailed.tsv.bz2 --wiki train-00001.parquet --wiki_mb 140
  python3 scripts/montar_corpus.py --so_misturar        # refaz só a mistura e a validação (sem baixar nada)
"""
import argparse
import bz2
import os
import random
import re
import sys

PARTES = "textos/corpus_partes"
FINAL = "textos/corpus_portugues.txt"

# Só caracteres que o córtex vai ter no vocabulário (nível de caractere: vocabulário pequeno ajuda o modelo).
PERMITIDOS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ"
    "0123456789 \n.,;:!?()-'\"%/$+=*&@#_"
)
TROCAS = str.maketrans({
    "“": '"', "”": '"', "«": '"', "»": '"', "„": '"', "‘": "'", "’": "'", "´": "'", "`": "'",
    "–": "-", "—": "-", "−": "-", "‐": "-", "‑": "-", " ": " ", " ": " ", " ": " ", " ": " ", "…": "...",
    "º": "o", "ª": "a", "°": "o", "\t": " ",
})
# Repetição de cada parte na mistura: o que é pequeno e valioso pesa mais que a Wikipédia.
PESOS = {
    "wikipedia.txt": 1,
    "tatoeba.txt": 1,
    "gramatica_gerada.txt": 30,
    "regras_gramaticais.txt": 60,
    "regionalismos.txt": 60,
    "dialogos_extra.txt": 100,
    "01_identidade.txt": 100,
    "02_saudacoes.txt": 100,
    "03_fatos.txt": 50,
    "04_frases_simples.txt": 30,
    "05_sequencias.txt": 50,
    # Programação em Python (gerados por scripts/gerar_programacao/gerar.py). Já repetem as lições por dentro,
    # então peso 2 basta: ~8 MB, uns 4% do corpus. Trazem [ ] { } < > | \ para o vocabulário.
    "06_programacao_basico.txt": 2,
    "07_programacao_intermediario.txt": 2,
    # Mais programação (mesmo gerador): biblioteca padrão e erros do Python, JavaScript/Node, SQL, terminal/Git/Docker.
    # São arquivos menores e com assuntos novos, então peso 3.
    "08_python_biblioteca_e_erros.txt": 3,
    "09_javascript.txt": 3,
    "10_sql.txt": 3,
    "11_terminal_git_docker.txt": 3,
    # Química, biologia e neurociência (scripts/gerar_ciencias.py): ~55 KB de perguntas e respostas, por isso o peso alto
    # (como 03_fatos). Com 60 voltas ficam em ~3 MB, cerca de 2% do corpus.
    "12_quimica.txt": 60,
    "13_biologia.txt": 60,
    "14_neurociencia.txt": 60,
}


def limpar_linha(linha):
    linha = linha.translate(TROCAS)
    linha = re.sub(r" {2,}", " ", linha).strip()
    if not linha or any(c not in PERMITIDOS for c in linha):
        return None
    return linha


def digitos_demais(linha):
    return sum(c.isdigit() for c in linha) > 0.2 * len(linha)


def limpar_tatoeba(caminho, saida):
    vistos, n = set(), 0
    with bz2.open(caminho, "rt", encoding="utf-8") as f, open(saida, "w", encoding="utf-8") as o:
        for linha in f:
            partes = linha.rstrip("\n").split("\t")
            if len(partes) < 3 or partes[1] != "por":
                continue
            frase = limpar_linha(partes[2])
            if not frase or not (8 <= len(frase) <= 300) or frase in vistos:
                continue
            vistos.add(frase)
            o.write(frase + "\n")
            n += 1
    print(f"tatoeba: {n:,} frases")


RUIM = ("http", "www.", "{{", "}}", "|", "==", "&amp", "Categoria:", "Ficheiro:", "Imagem:")


def limpar_wikipedia(caminho, saida, limite_mb):
    import pyarrow.parquet as pq
    limite = limite_mb * 1_000_000
    vistos, total, artigos = set(), 0, 0
    arq = pq.ParquetFile(caminho)
    with open(saida, "w", encoding="utf-8") as o:
        for lote in arq.iter_batches(batch_size=512, columns=["text"]):
            for texto in lote.column("text").to_pylist():
                paragrafos = []
                for linha in texto.split("\n"):
                    p = limpar_linha(linha)
                    # parágrafos de verdade: longos, terminados em pontuação, sem markup
                    if not p or len(p) < 80 or p[-1] not in '.!?")' or digitos_demais(p) or any(r in p for r in RUIM) or hash(p) in vistos:
                        continue
                    vistos.add(hash(p))
                    paragrafos.append(p)
                if len(paragrafos) >= 2:
                    o.write("\n".join(paragrafos) + "\n\n")
                    total += sum(len(p) + 1 for p in paragrafos)
                    artigos += 1
                if total >= limite:
                    print(f"wikipedia: {artigos:,} artigos, {total/1e6:.0f} MB")
                    return
    print(f"wikipedia: {artigos:,} artigos, {total/1e6:.0f} MB (acabou o arquivo)")


def unidades(caminho):
    """Pedaços que não podem ser cortados no meio: blocos (separados por linha em branco) ou linhas."""
    texto = open(caminho, encoding="utf-8").read().strip()
    if "\n\n" in texto:
        return texto.split("\n\n"), "\n\n"
    return texto.split("\n"), "\n"


# Fração de unidades únicas separada de cada fonte para a validação (antes de repetir/misturar).
FRACAO_VAL = {"wikipedia.txt": 0.02, "tatoeba.txt": 0.02}
FRACAO_VAL_PADRAO = 0.05
VALIDACAO = "textos/corpus_validacao.txt"


def separar_validacao(un, nome, rng):
    """Separa unidades únicas para a validação. Devolve (treino, validação). Fontes com até 20 unidades não cedem nada."""
    un = [u for u in un if u.strip()]
    if len(un) <= 20:
        return un, []
    idx = list(range(len(un)))
    rng.shuffle(idx)
    k = max(1, round(FRACAO_VAL.get(nome, FRACAO_VAL_PADRAO) * len(un)))
    val = {i for i in idx[:k]}
    return [u for i, u in enumerate(un) if i not in val], [un[i] for i in sorted(val)]


def misturar(semente=3, unidades_por_pedaco=40):
    rng = random.Random(semente)
    fontes = []
    for nome, peso in PESOS.items():
        for pasta in (PARTES, "textos/curriculo"):
            caminho = os.path.join(pasta, nome)
            if os.path.exists(caminho):
                fontes.append((caminho, peso))
    # 1) separa a validação ANTES de repetir/misturar: cada unidade de validação fica de fora do treino
    por_fonte, validacao, vistos_val = [], [], set()
    for caminho, peso in fontes:
        un, sep = unidades(caminho)
        nome = os.path.basename(caminho)
        treino_un, val_un = separar_validacao(un, nome, rng)
        for u in val_un:
            if u.strip() not in vistos_val:  # cada unidade UMA vez
                vistos_val.add(u.strip())
                validacao.append(u.strip())
        por_fonte.append((nome, peso, treino_un, sep, len(val_un)))
    # 2) copias exatas de unidades de validação em qualquer fonte de treino também saem (senão vazariam por repetição)
    pedacos, resumo, removidas = [], [], 0
    for nome, peso, treino_un, sep, nval in por_fonte:
        antes = len(treino_un)
        treino_un = [u for u in treino_un if u.strip() not in vistos_val]
        removidas += antes - len(treino_un)
        grupos = [sep.join(treino_un[i:i + unidades_por_pedaco]) for i in range(0, len(treino_un), unidades_por_pedaco)]
        pedacos += [(g, sep) for g in grupos] * peso
        resumo.append((nome, peso, sum(len(g) for g in grupos) * peso, nval))
    # 3) uma unidade de validação que é uma linha inteira (ex.: "Bom dia.") dentro de um bloco do treino também vazaria
    linhas_treino = {l.strip() for _, _, tu, _, _ in por_fonte for u in tu for l in u.split("\n")}
    antes_val = len(validacao)
    validacao = [u for u in validacao if u not in linhas_treino]
    removidas_val = antes_val - len(validacao)
    rng.shuffle(pedacos)
    rng.shuffle(validacao)
    with open(FINAL, "w", encoding="utf-8") as o:
        for g, sep in pedacos:
            o.write(g + "\n\n")
    with open(VALIDACAO, "w", encoding="utf-8") as o:
        o.write("\n\n".join(validacao) + "\n\n")
    tamanho = os.path.getsize(FINAL)
    print(f"\n{FINAL}: {tamanho/1e6:.1f} MB (treino)")
    for nome, peso, chars, nval in resumo:
        print(f"  {nome:<28} x{peso:<3} {chars/1e6:>7.2f} M caracteres ({chars/ (tamanho or 1) * 100:4.1f}%)  val: {nval} unidades")
    chars_val = sum(len(u) for u in validacao)
    print(f"\n{VALIDACAO}: {len(validacao):,} unidades únicas, {chars_val/1e6:.2f} M caracteres ({os.path.getsize(VALIDACAO)/1e6:.2f} MB)"
          f" = {chars_val / (tamanho or 1) * 100:.2f}% do treino; {removidas} cópias exatas removidas do treino; {removidas_val} unidades de validação descartadas por já existirem como linha no treino")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tatoeba")
    ap.add_argument("--wiki")
    ap.add_argument("--wiki_mb", type=int, default=140)
    ap.add_argument("--so_misturar", action="store_true")
    a = ap.parse_args()
    os.makedirs(PARTES, exist_ok=True)
    if not a.so_misturar:
        if a.tatoeba:
            limpar_tatoeba(a.tatoeba, os.path.join(PARTES, "tatoeba.txt"))
        if a.wiki:
            limpar_wikipedia(a.wiki, os.path.join(PARTES, "wikipedia.txt"), a.wiki_mb)
    misturar()
