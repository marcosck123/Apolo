"""
Gera um texto sintético em português, só para testar se o córtex aprende (a perda cai).
NÃO serve para treinar de verdade: frases montadas por gabarito têm pouca variedade.
Uso: python scripts/gerar_texto_exemplo.py textos/exemplo.txt
"""
import random
import sys

random.seed(42)

sujeitos = ["O menino", "A menina", "O velho", "A professora", "O cachorro", "A gata",
            "O pescador", "A mulher", "O vento", "A chuva", "O padeiro", "A criança"]
verbos = ["olhou para", "caminhou até", "esperou perto de", "falou sobre", "lembrou de", "voltou para"]
lugares = [("a", "casa"), ("o", "rio"), ("a", "montanha"), ("o", "jardim"), ("a", "escola"),
           ("o", "mercado"), ("a", "praia"), ("o", "caminho")]
tempos = ["de manhã", "à tarde", "à noite", "no verão", "depois da chuva", "antes do sol nascer"]
ligacoes = ["Então", "Depois", "Mais tarde", "Naquele dia", "Sem pressa"]


def frase():
    artigo, lugar = random.choice(lugares)
    verbo = random.choice(verbos)
    if verbo.endswith(" de"):  # de + a = da, de + o = do
        verbo, artigo = verbo[:-3], "d" + artigo
    alvo = f"{artigo} {lugar}"
    sujeito = random.choice(sujeitos)
    if random.random() < 0.3:
        sujeito = f"{random.choice(ligacoes)}, {sujeito[0].lower()}{sujeito[1:]}"
    return f"{sujeito} {verbo} {alvo} {random.choice(tempos)}."


destino = sys.argv[1] if len(sys.argv) > 1 else "textos/exemplo.txt"
paragrafos = [" ".join(frase() for _ in range(random.randint(3, 6))) for _ in range(1200)]
with open(destino, "w", encoding="utf-8") as f:
    f.write("\n\n".join(paragrafos))
print(f"{destino}: {sum(len(p) for p in paragrafos):,} caracteres")
