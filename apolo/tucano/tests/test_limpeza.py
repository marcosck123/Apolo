"""Testes locais (sem baixar nada): python3 tucano/tests/test_limpeza.py"""
import importlib.util
import io
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.dirname(AQUI))
import baixar_gigaverbo_edu as g  # noqa: E402

P1 = "A fotossíntese é o processo pelo qual as plantas convertem a luz do sol em energia química, produzindo oxigênio."
P2 = "Esse processo acontece principalmente nas folhas, dentro de estruturas chamadas cloroplastos, que contêm clorofila."


def test_trocas_e_permitidos():
    assert g.limpar_linha("“Olá” — tudo bem?") == '"Olá" - tudo bem?'
    assert g.limpar_linha("tem emoji 😀") is None
    assert g.limpar_linha("tem colchete [1]") is None
    assert g.limpar_linha("   ") is None
    assert g.limpar_linha("muitos    espaços   aqui") == "muitos espaços aqui"


def test_documento_bom():
    vistos = set()
    ps = g.limpar_documento(P1 + "\n" + P2, vistos)
    assert ps == [P1, P2]


def test_documento_com_lixo():
    vistos = set()
    texto = "Menu\nHome | Contato\n" + P1 + "\nVeja em http://exemplo.com.br/pagina tudo sobre esse assunto interessante da biologia.\n" + P2
    ps = g.limpar_documento(texto, vistos, aproveitamento_min=0.5)
    assert ps == [P1, P2], ps


def test_documento_pouco_aproveitado():
    texto = P1 + "\n" + P2 + "\n" + ("lixo http://x.com " * 40 + ".\n") * 5
    assert g.limpar_documento(texto, set()) == []  # sobrou < 50% do texto


def test_um_paragrafo_so_nao_basta():
    assert g.limpar_documento(P1, set()) == []


def test_duplicata():
    vistos = set()
    assert g.limpar_documento(P1 + "\n" + P2, vistos)
    assert g.limpar_documento(P1 + "\n" + P2, vistos) == []


def test_digitos():
    d = "Os números 1234567890 1234567890 1234567890 1234567890 1234567890 1234567890 1234567890 1234567890."
    assert g.limpar_linha(d) and g.digitos_demais(d)
    assert g.limpar_documento(d + "\n" + d + "x.", set()) == []


def test_aceitar():
    assert g.aceitar({"text": "x", "edu_int_score": 3, "toxic_int_score": 1})
    assert not g.aceitar({"text": "x", "edu_int_score": 2, "toxic_int_score": 1})
    assert not g.aceitar({"text": "x", "edu_int_score": 5, "toxic_int_score": 4})
    assert not g.aceitar({"text": "x", "edu_int_score": 4, "toxic_int_score": 1}, min_edu=5)
    assert not g.aceitar({"text": "", "edu_int_score": 4, "toxic_int_score": 1})


def test_processar_relatorio_e_limite():
    docs = [
        {"text": P1 + "\n" + P2, "edu_int_score": 4, "toxic_int_score": 1},
        {"text": P1 + "\n" + P2, "edu_int_score": 4, "toxic_int_score": 1},          # duplicado -> limpeza
        {"text": P1 + "\n" + P2.replace("clorofila", "clorofila verde"), "edu_int_score": 1, "toxic_int_score": 1},  # edu baixo
        {"text": P2.replace("estruturas", "organelas") + "\n" + P1.replace("sol", "sol brilhante"),
         "edu_int_score": 3, "toxic_int_score": 2},
    ]
    saida = io.StringIO()
    rel = g.processar(iter(docs), 10**9, saida=saida, log_cada=0)
    assert rel["vistos"] == 4 and rel["aceitos"] == 2
    assert rel["reprovados_metadados"] == 1 and rel["reprovados_limpeza"] == 1
    texto = saida.getvalue()
    assert texto.endswith("\n\n") and texto.count("\n\n") == 2
    # limite: para depois do primeiro documento
    rel2 = g.processar(iter(docs), 10, saida=io.StringIO(), log_cada=0)
    assert rel2["vistos"] == 1 and rel2["aceitos"] == 1


def test_sincronia_com_montar_corpus():
    """Avisa se scripts/montar_corpus.py mudou PERMITIDOS/TROCAS/RUIM e esta cópia ficou defasada."""
    caminho = os.path.join(RAIZ, "scripts", "montar_corpus.py")
    if not os.path.exists(caminho):
        print("  (montar_corpus.py não encontrado; pulando)")
        return
    spec = importlib.util.spec_from_file_location("montar_corpus", caminho)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert g.PERMITIDOS == m.PERMITIDOS, f"PERMITIDOS divergiu: {sorted(g.PERMITIDOS ^ m.PERMITIDOS)}"
    assert g.TROCAS == m.TROCAS, "TROCAS divergiu"
    assert tuple(g.RUIM) == tuple(m.RUIM), "RUIM divergiu"


if __name__ == "__main__":
    falhas = 0
    for nome, fn in sorted(globals().items()):
        if nome.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok  ", nome)
            except AssertionError as e:
                falhas += 1
                print("FALHA", nome, e)
    sys.exit(1 if falhas else 0)
