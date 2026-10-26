"""Testes do cortex_v0 (só forward, pesos aleatórios; nenhum treino).

Rodar (raiz do repo):  python tests_cortex/test_cortex.py        ou  python -m pytest tests_cortex
Dentro do Docker:  docker compose --profile cortex run --rm --no-deps cortex python tests_cortex/test_cortex.py
"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import torch
import cortex_v0 as c

TEXTO = "o menino olhou para a lua.\n\nera uma noite clara, e ele sorriu.\nfim.\n\n"


def modelo_mini(semente=0, **extra):
    torch.manual_seed(semente)
    tk = c.TokenizerCaractere(TEXTO)
    cfg = dict(c.TAMANHOS["mini"], vocab=len(tk.vocab), **extra)
    m = c.Cortex(**cfg).eval()
    # pesos aleatórios com mais "personalidade" para os logits não ficarem quase planos
    for p in m.parameters():
        torch.nn.init.normal_(p, std=0.2) if p.dim() > 1 else None
    return m, tk


def test_forward_com_cache_igual_ao_completo():
    m, tk = modelo_mini()
    ids = torch.tensor([tk.codificar(TEXTO)[:50]])
    completo, _ = m(ids)
    # prefill de 20 + pedaço de 7 (máscara retangular) + um a um
    l1, kv = m.forward_cache(ids[:, :20])
    l2, kv = m.forward_cache(ids[:, 20:27], kv)
    partes = [l1, l2]
    for i in range(27, 50):
        l, kv = m.forward_cache(ids[:, i:i + 1], kv)
        partes.append(l)
    assert torch.allclose(torch.cat(partes, 1), completo, atol=1e-4)


def test_geracao_com_cache_identica_argmax_e_amostragem():
    m, tk = modelo_mini()
    inicio = torch.tensor([tk.codificar("o menino")])
    n = m.contexto + 60  # passa do contexto: testa a troca para a janela deslizante
    for temp in (1e-6, 0.8):
        torch.manual_seed(123)
        a = m.gerar(inicio, n, temperatura=temp, usar_cache=True)
        torch.manual_seed(123)
        b = m.gerar(inicio, n, temperatura=temp, usar_cache=False)
        assert a.tolist() == b.tolist(), f"divergiu com temperatura {temp}"


def test_prompt_maior_que_contexto():
    m, tk = modelo_mini()
    inicio = torch.tensor([(tk.codificar(TEXTO) * 6)[:m.contexto + 30]])
    torch.manual_seed(1); a = m.gerar(inicio, 20, temperatura=1e-6, usar_cache=True)
    torch.manual_seed(1); b = m.gerar(inicio, 20, temperatura=1e-6, usar_cache=False)
    assert a.tolist() == b.tolist()


def test_parar_em():
    m, tk = modelo_mini()
    inicio = "o menino"
    torch.manual_seed(5)
    livre = c.continuar(m, tk, "cpu", inicio, 200, 1.0, parar_em=[])
    assert len(livre) == 200
    parada = livre[40:43]          # trecho de 3 caracteres que sabemos que o modelo gera
    corte = livre.index(parada)    # primeira ocorrência
    for usar_cache in (True, False):
        torch.manual_seed(5)
        cortado = c.continuar(m, tk, "cpu", inicio, 200, 1.0, parar_em=[parada], usar_cache=usar_cache)
        assert cortado == livre[:corte] and parada not in cortado
    torch.manual_seed(5)  # várias paradas: vale a que aparece primeiro
    assert c.continuar(m, tk, "cpu", inicio, 200, 1.0, parar_em=["#nunca#", parada, livre[100:103]]) == livre[:corte]
    torch.manual_seed(5)  # parada de um caractere
    um = livre[10]
    assert c.continuar(m, tk, "cpu", inicio, 200, 1.0, parar_em=[um]) == livre[:livre.index(um)]
    torch.manual_seed(5)  # parada que nunca ocorre e lista vazia: texto inteiro
    assert c.continuar(m, tk, "cpu", inicio, 200, 1.0, parar_em=["#nunca#"]) == livre
    torch.manual_seed(5)
    assert c.continuar(m, tk, "cpu", inicio, 200, 1.0) == livre


def test_parar_em_poupa_tempo():
    m, tk = modelo_mini()
    n_chamadas = []
    original = m.forward_cache
    m.forward_cache = lambda *a, **k: (n_chamadas.append(1), original(*a, **k))[1]
    torch.manual_seed(5)
    c.continuar(m, tk, "cpu", "o menino", 200, 1.0, parar_em=["a"])
    assert len(n_chamadas) < 200


def medir():
    """Mede o ganho de velocidade: tamanho `medio` (12 camadas, d=768, ~85M) com pesos aleatórios, só forward."""
    torch.manual_seed(0)
    tk = c.TokenizerCaractere(TEXTO * 3)
    m = c.Cortex(**dict(c.TAMANHOS["medio"], vocab=90)).eval()
    inicio = torch.randint(0, 90, (1, 20))
    n = 80
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    res = {}
    for nome, uc in (("sem cache", False), ("com cache", True)):
        torch.manual_seed(1)
        t = time.time(); r = m.gerar(inicio, n, temperatura=1e-6, usar_cache=uc); res[nome] = (time.time() - t, r)
        print(f"medio, {n} caracteres, {nome}: {res[nome][0]:.2f}s")
    print("ids idênticos:", res["sem cache"][1].tolist() == res["com cache"][1].tolist())
    print(f"ganho: {res['sem cache'][0] / res['com cache'][0]:.1f}x")


if __name__ == "__main__":
    for nome, f in list(globals().items()):
        if nome.startswith("test_"):
            f(); print("ok", nome)
    if "--medir" in sys.argv:
        medir()
