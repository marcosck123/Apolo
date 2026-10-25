#!/usr/bin/env python3
"""Mede o córtex do Apolo em problemas NOVOS de programação (pass@1).

  python3 aptidao/rodar.py --url http://localhost:8000 --n 100 --rotulo v2_medio
  python3 aptidao/rodar.py --modelo-local cerebro --rotulo v2_medio          (sem servidor; precisa de torch)
  python3 aptidao/rodar.py --comparar resultados/a.jsonl resultados/b.jsonl
  python3 aptidao/rodar.py --modelo-falso oraculo --n 20                     (teste do corretor, sem córtex)
"""
import argparse
import json
import math
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import corretor  # noqa: E402
import gerador  # noqa: E402
import modelos_falsos  # noqa: E402


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - m), min(1.0, c + m)


def resumo(registros):
    """{categoria: (acertos, total)} mais 'TOTAL'."""
    r = {}
    for x in registros:
        a, t = r.get(x["categoria"], (0, 0))
        r[x["categoria"]] = (a + (1 if x.get("ok") else 0), t + 1)
    r["TOTAL"] = (sum(a for a, _ in r.values()), sum(t for _, t in r.values()))
    return r


def tabela(titulo, registros):
    linhas = [titulo, f"{'categoria':<24}{'acertos':>9}{'total':>7}{'pass@1':>9}   IC 95% (Wilson)"]
    res = resumo(registros)
    for c in [k for k in res if k != "TOTAL"] + ["TOTAL"]:
        a, t = res[c]
        lo, hi = wilson(a, t)
        linhas.append(f"{c:<24}{a:>9}{t:>7}{100 * a / t:>8.1f}%   [{100 * lo:.1f}% a {100 * hi:.1f}%]")
    return "\n".join(linhas)


def ler_jsonl(caminho):
    if not os.path.exists(caminho):
        return []
    with open(caminho, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def comparar(a, b):
    ra, rb = ler_jsonl(a), ler_jsonl(b)
    print(tabela(f"A = {a}", ra))
    print()
    print(tabela(f"B = {b}", rb))
    print("\nDiferença (B - A), em pontos percentuais:")
    sa, sb = resumo(ra), resumo(rb)
    for c in [k for k in sa if k in sb and k != "TOTAL"] + ["TOTAL"]:
        pa, pb = 100 * sa[c][0] / sa[c][1], 100 * sb[c][0] / sb[c][1]
        print(f"  {c:<24}{pb - pa:>+7.1f}")
    ids_a = {x["id"]: x.get("ok") for x in ra}
    comuns = [i for i in ids_a if i in {x["id"]: 0 for x in rb}]
    if comuns:
        ok_b = {x["id"]: x.get("ok") for x in rb}
        ganhou = sum(1 for i in comuns if not ids_a[i] and ok_b[i])
        perdeu = sum(1 for i in comuns if ids_a[i] and not ok_b[i])
        print(f"\nNos {len(comuns)} problemas comuns: B acertou {ganhou} que A errou; A acertou {perdeu} que B errou.")
        if len(comuns) < len(ra) or len(comuns) < len(rb):
            print("Aviso: os conjuntos de problemas não são idênticos; use a mesma --semente e --n.")
    print("Lembrete: diferenças dentro dos intervalos de confiança podem ser só sorte.")


def gerador_http(url, n_tokens, temperatura):
    def f(prompt):
        req = urllib.request.Request(url.rstrip("/") + "/gerar", method="POST",
                                     data=json.dumps({"inicio": prompt, "n": n_tokens, "temperatura": temperatura,
                                                       "parar_em": ["\nSaída:", "\n\n"]}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read().decode("utf-8"))["texto"]
    return f


def gerador_local(pasta, n_tokens, temperatura):
    try:
        import torch  # noqa: F401
    except ImportError:
        sys.exit("O modo --modelo-local precisa do PyTorch (pip install torch), que não está instalado aqui. "
                 "Use --url com o servidor do córtex ou rode no Colab.")
    raiz = os.path.dirname(AQUI)
    sys.path.insert(0, raiz)
    import cortex_v0
    pasta = os.path.abspath(pasta)
    cortex_v0.PASTA = pasta          # carregar() lê PASTA/config.json e PASTA/cortex.pt
    modelo, tk, dev = cortex_v0.carregar()

    def f(prompt):
        # `continuar` devolve só o texto novo; paramos em "Saída:" para economizar tempo
        return cortex_v0.continuar(modelo, tk, dev, prompt, n_tokens, temperatura=temperatura,
                                   parar_em=["\nSaída:", "\n\n"])
    return f


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="http://localhost:8000")
    ap.add_argument("--n", type=int, default=100, help="total de problemas (dividido entre as categorias)")
    ap.add_argument("--semente", type=int, default=9000, help="use 9000 ou mais (o treino usou 6 a 11)")
    ap.add_argument("--temperatura", type=float, default=0.2)
    ap.add_argument("--tokens", type=int, default=600, help="caracteres pedidos ao córtex por problema")
    ap.add_argument("--categorias", nargs="*", default=None, choices=gerador.CATEGORIAS)
    ap.add_argument("--rotulo", default=None, help="nome do resultado: aptidao/resultados/<rotulo>.jsonl")
    ap.add_argument("--paralelo", type=int, default=1, help="chamadas simultâneas ao córtex")
    ap.add_argument("--modelo-local", default=None, help="pasta com cortex.pt e config.json (sem servidor)")
    ap.add_argument("--modelo-falso", choices=sorted(modelos_falsos.MODELOS), default=None)
    ap.add_argument("--comparar", nargs=2, metavar=("A.jsonl", "B.jsonl"))
    ap.add_argument("--so-gerar", action="store_true", help="só gera os textos (sem corrigir; para o Colab, sem Docker)")
    ap.add_argument("--imagem", default=None, help="imagem Docker do corretor")
    a = ap.parse_args()

    if a.comparar:
        return comparar(*a.comparar)
    if a.semente < 9000:
        sys.exit("A semente deve ser 9000 ou mais (sementes menores foram usadas no treino).")

    rotulo = a.rotulo or a.modelo_falso or time.strftime("%Y%m%d_%H%M%S")
    os.makedirs(os.path.join(AQUI, "resultados"), exist_ok=True)
    caminho = os.path.join(AQUI, "resultados", f"{rotulo}.jsonl")

    problemas, stats = gerador.gerar(a.n, a.semente, a.categorias)
    print("Problemas gerados (descartados por contaminação com o treino):")
    for c, s in stats.items():
        print(f"  {c:<24}{s['gerados']:>4}   ({s['contaminados']} descartados)")

    if a.modelo_falso:
        gerar_texto = lambda prompt: None  # noqa: E731
    elif a.modelo_local:
        gerar_texto = gerador_local(a.modelo_local, a.tokens, a.temperatura)
    else:
        gerar_texto = gerador_http(a.url, a.tokens, a.temperatura)

    feitos = {x["id"]: x for x in ler_jsonl(caminho)}
    pendentes = [p for p in problemas if p["id"] not in feitos]
    if feitos:
        print(f"Retomando: {len(feitos)} já gerados em {caminho}, faltam {len(pendentes)}.")

    def um(p):
        if a.modelo_falso:
            texto = modelos_falsos.MODELOS[a.modelo_falso](p)
        else:
            texto = gerar_texto(p["prompt"])
        return {"id": p["id"], "categoria": p["categoria"], "enunciado": p["enunciado"], "texto": texto}

    t0 = time.time()
    with open(caminho, "a", encoding="utf-8") as saida, ThreadPoolExecutor(max_workers=max(1, a.paralelo)) as ex:
        for i, reg in enumerate(ex.map(um, pendentes), 1):
            saida.write(json.dumps(reg, ensure_ascii=False) + "\n")
            saida.flush()
            feitos[reg["id"]] = reg
            if i % 10 == 0 or i == len(pendentes):
                print(f"  gerando {i}/{len(pendentes)} ({time.time() - t0:.0f}s)", file=sys.stderr)

    if a.so_gerar:
        print(f"Textos gerados em {caminho}. Corrija numa máquina com Docker, rodando o mesmo comando sem --so-gerar.")
        return
    print("Corrigindo em container isolado...")
    t1 = time.time()
    textos = {i: r["texto"] for i, r in feitos.items()}
    res = corretor.corrigir(problemas, textos, imagem=a.imagem)
    print(f"  correção: {time.time() - t1:.1f}s")
    finais = []
    for p in problemas:
        r = res.get(p["id"])
        if r is None:
            continue
        finais.append({**feitos[p["id"]], "ok": r["ok"], "motivo": r["motivo"], "saida_obtida": r["saida"],
                       "erro": r["erro"], "saida_esperada": p["saida_esperada"]})
    tmp = caminho + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for x in finais:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    os.replace(tmp, caminho)

    print()
    print(tabela(f"Resultado '{rotulo}' (temperatura {a.temperatura}, sementes {a.semente}+)", finais))
    motivos = {}
    for x in finais:
        motivos[x["motivo"]] = motivos.get(x["motivo"], 0) + 1
    print("Motivos:", ", ".join(f"{k}={v}" for k, v in sorted(motivos.items())))
    print(f"Arquivo: {caminho}")


if __name__ == "__main__":
    main()
