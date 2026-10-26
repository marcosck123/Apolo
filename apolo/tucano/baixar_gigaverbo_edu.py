#!/usr/bin/env python3
"""Baixa (em streaming) o subconjunto EDUCATIVO do GigaVerbo-v2 e grava no formato do corpus do Apolo.

RODE NO COLAB (ou em outra máquina com internet e disco), NÃO no notebook do dono.
O dataset inteiro tem ~772 GB; o modo streaming lê só o que for preciso para juntar N MB de texto.

Fonte verificada (cartão do dataset): https://huggingface.co/datasets/Polygl0t/gigaverbo-v2
  - configs: edu_high (edu_int_score >= 4), edu_medium (edu_int_score == 3), edu_low (<= 2), nsfw (toxic_int_score >= 4)
  - "educativo" (score >= 3) = edu_high + edu_medium. Campo inteiro: `edu_int_score` (1 a 5); float: `edu_score`.
  - campos: text, id, source, subset, token_count, edu_score, edu_int_score, toxic_score, toxic_int_score
  - NÃO é "gated": não precisa aceitar termos no Hugging Face. A licença é "other" (mistura das licenças das fontes,
    ver LEIAME.md: há fontes CC-BY-NC). Um token HF (HF_TOKEN) só ajuda a ter menos limite de requisições.

Uso no Colab:
  !pip -q install datasets
  !python baixar_gigaverbo_edu.py --mb 150 --saida gigaverbo_edu.txt
  # opções: --min_edu 3 (3 = high+medium; 4 = só high)  --max_toxic 3  --prob_high 0.5  --semente 7

Saída: parágrafos limpos, um por linha, documentos separados por linha em branco (mesmo formato de
textos/corpus_partes/wikipedia.txt). Depois copie para textos/corpus_partes/ e acrescente em PESOS do
scripts/montar_corpus.py (peso baixo, 1) -- isso é decisão do dono, este script não mexe no repositório.
"""
import argparse
import os
import re
import sys

# ---------------------------------------------------------------------------------------------
# Cópia da lógica de scripts/montar_corpus.py (PERMITIDOS, TROCAS, limpar_linha, digitos_demais, RUIM e o filtro
# de parágrafos de limpar_wikipedia). O teste tests/test_limpeza.py compara estas constantes com as do original
# para avisar se o córtex mudar o conjunto de caracteres e esta cópia ficar defasada.
# ---------------------------------------------------------------------------------------------
PERMITIDOS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ"
    "0123456789 \n.,;:!?()-'\"%/$+=*&@#_"
)
TROCAS = str.maketrans({
    "“": '"', "”": '"', "«": '"', "»": '"', "„": '"', "‘": "'", "’": "'",
    "´": "'", "`": "'",
    "–": "-", "—": "-", "−": "-", "‐": "-", "‑": "-",
    " ": " ", " ": " ", " ": " ", " ": " ", "…": "...",
    "º": "o", "ª": "a", "°": "o", "\t": " ",
})
RUIM = ("http", "www.", "{{", "}}", "|", "==", "&amp", "Categoria:", "Ficheiro:", "Imagem:")


def limpar_linha(linha):
    linha = linha.translate(TROCAS)
    linha = re.sub(r" {2,}", " ", linha).strip()
    if not linha or any(c not in PERMITIDOS for c in linha):
        return None
    return linha


def digitos_demais(linha):
    return sum(c.isdigit() for c in linha) > 0.2 * len(linha)


# Extras além do que limpar_wikipedia faz (a web é mais suja que a Wikipédia):
RUIM_WEB = ("<", ">", "[", "]", "{", "}", "\\", "Leia mais", "Clique aqui", "Compartilhe", "Copyright", "©")


def limpar_documento(texto, vistos, aproveitamento_min=0.5, min_paragrafos=2):
    """Devolve a lista de parágrafos aceitos de um documento, ou [] se o documento não presta.

    Mesmas regras de limpar_wikipedia: parágrafo >= 80 caracteres, termina em . ! ? " ), sem urls/markup,
    sem excesso de dígitos, sem repetição (hash em `vistos`). Mais: o documento é descartado se sobrar pouca
    coisa dele (aproveitamento_min = fração dos caracteres das linhas não vazias que sobreviveu), porque cortar
    metade das linhas de um texto web deixa um texto sem sentido.
    """
    paragrafos, total_linhas, total_aceito = [], 0, 0
    novos = []
    for linha in texto.split("\n"):
        if linha.strip():
            total_linhas += len(linha.strip())
        p = limpar_linha(linha)
        if (not p or len(p) < 80 or p[-1] not in '.!?")' or digitos_demais(p)
                or any(r in p for r in RUIM) or any(r in p for r in RUIM_WEB)):
            continue
        h = hash(p)
        if h in vistos or h in novos:
            continue
        novos.append(h)
        paragrafos.append(p)
        total_aceito += len(p)
    if len(paragrafos) < min_paragrafos or total_linhas == 0 or total_aceito / total_linhas < aproveitamento_min:
        return []
    vistos.update(novos)
    return paragrafos


def aceitar(exemplo, min_edu=3, max_toxic=3):
    """Filtro de metadados: valor educativo >= min_edu e toxicidade <= max_toxic (campos inteiros do dataset)."""
    edu = exemplo.get("edu_int_score")
    tox = exemplo.get("toxic_int_score")
    if edu is None or edu < min_edu:
        return False
    if tox is not None and tox > max_toxic:
        return False
    return bool(exemplo.get("text"))


def processar(exemplos, limite_bytes, min_edu=3, max_toxic=3, aproveitamento_min=0.5, saida=None, log_cada=2000):
    """Consome um iterável de dicts, escreve em `saida` (arquivo aberto) e devolve o relatório."""
    vistos = set()
    rel = {"vistos": 0, "reprovados_metadados": 0, "reprovados_limpeza": 0, "aceitos": 0, "bytes": 0, "paragrafos": 0}
    for ex in exemplos:
        rel["vistos"] += 1
        if not aceitar(ex, min_edu, max_toxic):
            rel["reprovados_metadados"] += 1
        else:
            ps = limpar_documento(ex["text"], vistos, aproveitamento_min)
            if not ps:
                rel["reprovados_limpeza"] += 1
            else:
                bloco = "\n".join(ps) + "\n\n"
                if saida is not None:
                    saida.write(bloco)
                rel["aceitos"] += 1
                rel["paragrafos"] += len(ps)
                rel["bytes"] += len(bloco.encode("utf-8"))
        if log_cada and rel["vistos"] % log_cada == 0:
            print(f"  ... vistos {rel['vistos']:,} | aceitos {rel['aceitos']:,} | {rel['bytes']/1e6:.1f} MB", flush=True)
        if rel["bytes"] >= limite_bytes:
            break
    return rel


def abrir_stream(min_edu, prob_high, semente, buffer):
    from datasets import load_dataset, interleave_datasets
    nome = "Polygl0t/gigaverbo-v2"
    # streaming=True: não baixa o dataset; lê os shards parquet sob demanda.
    high = load_dataset(nome, "edu_high", split="train", streaming=True)
    high = high.shuffle(seed=semente, buffer_size=buffer)  # embaralha a ordem dos shards e uma janela de documentos
    if min_edu >= 4:
        return high
    medium = load_dataset(nome, "edu_medium", split="train", streaming=True)
    medium = medium.shuffle(seed=semente + 1, buffer_size=buffer)
    return interleave_datasets([high, medium], probabilities=[prob_high, 1 - prob_high], seed=semente,
                               stopping_strategy="all_exhausted")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mb", type=float, required=True, help="tamanho alvo da saída em MB (o script para ao atingir)")
    ap.add_argument("--saida", default="gigaverbo_edu.txt")
    ap.add_argument("--min_edu", type=int, default=3, help="edu_int_score mínimo: 3 = edu_high+edu_medium; 4 = só edu_high")
    ap.add_argument("--max_toxic", type=int, default=3, help="toxic_int_score máximo aceito (as configs edu_* já são <= 3)")
    ap.add_argument("--prob_high", type=float, default=0.5, help="fração de documentos tirados de edu_high (o resto vem de edu_medium)")
    ap.add_argument("--aproveitamento_min", type=float, default=0.5)
    ap.add_argument("--semente", type=int, default=7)
    ap.add_argument("--buffer", type=int, default=5000, help="tamanho do buffer de embaralhamento do streaming")
    a = ap.parse_args()

    if os.environ.get("HF_TOKEN") is None:
        print("Aviso: sem HF_TOKEN; funciona (dataset público), mas o limite de requisições é menor.", file=sys.stderr)
    print(f"Lendo GigaVerbo-v2 em streaming (min_edu={a.min_edu}) até {a.mb} MB ...", flush=True)
    stream = abrir_stream(a.min_edu, a.prob_high, a.semente, a.buffer)
    with open(a.saida, "w", encoding="utf-8") as o:
        rel = processar(stream, int(a.mb * 1_000_000), a.min_edu, a.max_toxic, a.aproveitamento_min, o)
    print("\n=== Relatório ===")
    print(f"documentos vistos:              {rel['vistos']:,}")
    print(f"  reprovados por metadados:     {rel['reprovados_metadados']:,}")
    print(f"  reprovados na limpeza:        {rel['reprovados_limpeza']:,}")
    print(f"documentos aceitos:             {rel['aceitos']:,}")
    print(f"parágrafos gravados:            {rel['paragrafos']:,}")
    print(f"tamanho de {a.saida}:           {rel['bytes']/1e6:.1f} MB")
    if rel["vistos"]:
        print(f"taxa de aceitação:              {rel['aceitos']/rel['vistos']*100:.1f}%")


if __name__ == "__main__":
    main()
