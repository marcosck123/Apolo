"""Modelos de mentira para testar o corretor sem córtex. Cada um: função (problema) -> texto gerado."""
import re


def oraculo(p):
    """Devolve a solução de referência, como o córtex perfeito faria (com o resto do bloco, que o corretor ignora)."""
    return p["referencia"] + "\nSaída:\n" + p["saida_esperada"] + "\nExplicação qualquer."


def vazio(p):
    return ""


def quase(p):
    """A referência com um dígito trocado (ou, sem dígitos, um comando inexistente): tem de falhar."""
    ref = p["referencia"]
    m = re.search(r"\d", ref)
    if m:
        d = (int(m.group()) + 1) % 10
        novo = ref[:m.start()] + str(d) + ref[m.end():]
    else:
        novo = "comando_que_nao_existe_xyz\n" + ref
    return novo + "\nSaída:\n"


def lixo(p):
    return "Não sei responder isso.\n\nOutra coisa."


MODELOS = {"oraculo": oraculo, "vazio": vazio, "quase": quase, "lixo": lixo}
