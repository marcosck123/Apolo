"""Testes do córtex v3 (rodam na CPU, com o modelo `mini` de pesos aleatórios e no máximo 20 passos de verificação).
Como rodar (da raiz do repositório): python -m unittest discover -s tests_v3 -v
"""
import glob, json, math, os, shutil, sys, tempfile, threading, unittest, urllib.request
from http.server import ThreadingHTTPServer

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import torch
import cortex_v3 as C
from tokenizador_bpe import TokenizerBPE, TokenizerCaractere, tokenizador_de_dict, _MotorPuro

CURRICULO = sorted(glob.glob(os.path.join(RAIZ, "textos", "curriculo", "*.txt")))
DADOS = os.path.join(RAIZ, "tests_v3", "dados")


def preparar_dados():
    """Dados mínimos de teste (não usa textos/corpus_*.txt): currículo inteiro para treino e um trecho para validação."""
    os.makedirs(DADOS, exist_ok=True)
    tr, va = os.path.join(DADOS, "treino.txt"), os.path.join(DADOS, "val.txt")
    if not os.path.exists(tr):
        textos = [open(f, encoding="utf-8").read() for f in CURRICULO]
        open(tr, "w", encoding="utf-8").write("\n\n".join(textos))
        open(va, "w", encoding="utf-8").write("\n\n".join(t[-6000:] for t in textos[:6]))
    return tr, va


def modelo_mini(vocab=100, semente=0):
    torch.manual_seed(semente)
    return C.Cortex(vocab=vocab, **C.TAMANHOS["mini"]).eval()


class TestModelo(unittest.TestCase):
    def test_formas_e_perda_inicial(self):
        m = modelo_mini(100)
        ids = torch.randint(100, (3, 20))
        logits, perda = m(ids, ids)
        self.assertEqual(logits.shape, (3, 20, 100))
        # perto do chute aleatório ln(V); fica um pouco acima porque a saída é amarrada ao embedding
        # (o vetor final tende a se parecer com o token de entrada)
        self.assertLess(abs(perda.item() - math.log(100)), 2.5)

    def test_sem_posicao_aprendida_e_embedding_amarrado(self):
        m = modelo_mini(100)
        nomes = [n for n, _ in m.named_parameters()]
        self.assertFalse(any("pos" in n for n in nomes))
        self.assertFalse(any(n.startswith("cabeca") for n in nomes))  # saída usa tok.weight
        self.assertEqual(sum(p.numel() for p in m.parameters()), C.contar_parametros(dict(C.TAMANHOS["mini"], vocab=100))[0])

    def test_largura_mlp(self):
        self.assertEqual(C.largura_mlp(768), 2048)
        for d in (128, 384, 512, 768, 1024):
            self.assertEqual(C.largura_mlp(d) % 64, 0)

    def test_weight_decay_so_em_matrizes(self):
        m = modelo_mini(100)
        com, sem = m.grupos_otimizador(0.1)
        ids_tok = id(m.tok.weight)
        self.assertTrue(all(p.dim() >= 2 and id(p) != ids_tok for p in com["params"]))
        self.assertTrue(all(p.dim() < 2 or id(p) == ids_tok for p in sem["params"]))
        self.assertEqual(len(com["params"]) + len(sem["params"]), len(list(m.parameters())))

    def test_tamanho_medio(self):
        total, sem_emb = C.contar_parametros(dict(C.TAMANHOS["medio"], vocab=16000))
        self.assertTrue(84e6 < sem_emb < 86e6, sem_emb)
        self.assertTrue(96e6 < total < 99e6, total)


class TestRoPE(unittest.TestCase):
    def test_posicao_relativa(self):
        torch.manual_seed(0)
        dim = 32
        q, k = torch.randn(1, 1, 1, dim), torch.randn(1, 1, 1, dim)

        def produto(pq, pk):
            cq, sq = C.tabelas_rope(torch.tensor([pq]), dim, 10000.0, "cpu")
            ck, sk = C.tabelas_rope(torch.tensor([pk]), dim, 10000.0, "cpu")
            return (C.aplicar_rope(q, cq, sq) * C.aplicar_rope(k, ck, sk)).sum().item()

        self.assertAlmostEqual(produto(5, 2), produto(105, 102), places=3)  # só a distância (3) importa
        self.assertAlmostEqual(produto(0, 0), produto(40, 40), places=4)
        self.assertNotAlmostEqual(produto(5, 2), produto(5, 3), places=3)    # distâncias diferentes dão valores diferentes

    def test_norma_preservada_e_posicao_zero_identidade(self):
        x = torch.randn(1, 2, 3, 16)
        cos, sin = C.tabelas_rope(torch.arange(3), 16, 10000.0, "cpu")
        y = C.aplicar_rope(x, cos, sin)
        self.assertTrue(torch.allclose(x.norm(dim=-1), y.norm(dim=-1), atol=1e-5))
        self.assertTrue(torch.allclose(x[:, :, 0], y[:, :, 0], atol=1e-6))

    def test_base_configuravel(self):
        a = C.tabelas_rope(torch.tensor([7]), 16, 10000.0, "cpu")[0]
        b = C.tabelas_rope(torch.tensor([7]), 16, 500000.0, "cpu")[0]
        self.assertFalse(torch.allclose(a, b))


class TestCache(unittest.TestCase):
    def test_logits_com_e_sem_cache(self):
        m = modelo_mini(100)
        ids = torch.randint(100, (1, 40))
        completo = m(ids)[0]
        cache = m.novo_cache()
        partes = [m(ids[:, :25], cache=cache)[0]] + [m(ids[:, i:i + 1], cache=cache)[0] for i in range(25, 40)]
        self.assertTrue(torch.allclose(completo, torch.cat(partes, 1), atol=1e-4))

    def test_geracao_igual_com_e_sem_cache(self):
        m = modelo_mini(100)
        ids = torch.randint(100, (1, 12))
        a = m.gerar(ids, 60, gerador=torch.Generator().manual_seed(1), usar_cache=True)
        b = m.gerar(ids, 60, gerador=torch.Generator().manual_seed(1), usar_cache=False)
        self.assertTrue(torch.equal(a, b))

    def test_janela_deslizante_passa_do_contexto(self):
        m = modelo_mini(100)
        ids = torch.randint(100, (1, 20))
        out = m.gerar(ids, m.contexto + 40)  # estoura o contexto de 128: descarta o cache mais antigo
        self.assertEqual(out.shape[1], 20 + m.contexto + 40)
        cache = m.novo_cache()
        m(ids, cache=cache)
        for _ in range(m.contexto + 5):
            m(ids[:, :1], cache=cache)
        self.assertEqual(cache.kv[0][0].shape[2], m.contexto)

    def test_parada_antecipada(self):
        m = modelo_mini(100)
        out = m.gerar(torch.randint(100, (1, 5)), 50, parar=lambda novos: len(novos) >= 7)
        self.assertEqual(out.shape[1], 5 + 7)


class TestWSD(unittest.TestCase):
    def test_valores(self):
        f = lambda p, **k: C.taxa_wsd(p, 1.0, 10, 80, 100, **k)
        self.assertAlmostEqual(f(0), 0.1)
        self.assertAlmostEqual(f(9), 1.0)
        self.assertAlmostEqual(f(10), 1.0)
        self.assertAlmostEqual(f(79), 1.0)
        self.assertAlmostEqual(f(80), 1 - 1 / 20)            # primeiro passo da descida linear
        self.assertAlmostEqual(f(89), 0.5)                    # metade da descida
        self.assertAlmostEqual(f(99), 0.0)                    # último passo
        self.assertAlmostEqual(f(89, forma="1-sqrt"), 1 - math.sqrt(0.5))
        self.assertAlmostEqual(f(99, forma="1-sqrt", lr_final=0.1), 0.1)

    def test_estavel_ate(self):
        self.assertEqual(C.resolver_estavel_ate(None, 1000, 0.2), 800)
        self.assertEqual(C.resolver_estavel_ate(0.7, 1000, 0.2), 700)
        self.assertEqual(C.resolver_estavel_ate(650, 1000, 0.2), 650)


class TestTokenizador(unittest.TestCase):
    AMOSTRAS = ["def f(x): return {'a': [1, 2]} | x < 3 > 2 \\ `cmd` ~ ^ $ % # @ !",
                "Ação, coração, pão — “aspas”, emojis 😀 e kanji 日本, tab\t e \r\n quebras\n\n\n fim ",
                "", " ", "   espaços  ", "<|fim|> texto <|fim|>"]

    @classmethod
    def setUpClass(cls):
        cls.textos = [open(f, encoding="utf-8").read() for f in CURRICULO]
        cls.bpe = TokenizerBPE.treinar(cls.textos, vocab=600, verbose=False)

    def test_ida_e_volta_arquivos_reais(self):
        for f, t in zip(CURRICULO, self.textos):
            self.assertEqual(self.bpe.decodificar(self.bpe.codificar(t)), t, f)
            self.assertEqual(self.bpe.decodificar(self.bpe.codificar_tensor(t).tolist()), t, f)

    def test_ida_e_volta_amostras(self):
        for s in self.AMOSTRAS:
            self.assertEqual(self.bpe.decodificar(self.bpe.codificar(s)), s)

    def test_vocabulario_e_comprimento(self):
        self.assertLessEqual(self.bpe.n_vocab, 600)
        t = self.textos[5]
        self.assertGreater(len(t) / len(self.bpe.codificar(t)), 2.0)  # BPE comprime de fato

    def test_salvar_e_carregar_json(self):
        d = json.loads(json.dumps(self.bpe.para_dict()))
        outro = tokenizador_de_dict(d)
        for s in self.AMOSTRAS:
            self.assertEqual(outro.codificar(s), self.bpe.codificar(s))

    def test_motor_puro(self):
        amostra = ["\n\n".join(self.textos[:3])[:60000]]
        tk = TokenizerBPE.treinar(amostra, vocab=400, motor="puro", verbose=False)
        for s in self.AMOSTRAS + [self.textos[6][:80000], 'min_max __init__ a_b']:
            self.assertEqual(tk.decodificar(tk.codificar(s)), s)
        outro = tokenizador_de_dict(json.loads(json.dumps(tk.para_dict())))
        self.assertEqual(outro.codificar(self.textos[6][:80000]), tk.codificar(self.textos[6][:80000]))

    def test_caractere_mesma_interface(self):
        tk = TokenizerCaractere("abc{}[]|\\`<>")
        self.assertEqual(tk.decodificar(tk.codificar("a{b}")), "a{b}")
        self.assertEqual(tk.n_vocab, 12)
        self.assertEqual(tokenizador_de_dict(tk.para_dict()).vocab, tk.vocab)

    def test_bpc(self):
        # caractere: 1 token = 1 caractere -> BPC = perda/ln2
        self.assertAlmostEqual(C.bpc(math.log(2) * 1.5, 1000, 1000), 1.5)
        # BPE com 4 caracteres por token: a mesma perda por token vale 4x menos bits por caractere
        self.assertAlmostEqual(C.bpc(math.log(2) * 8, 250, 1000), 2.0)


def args_treino(pasta, *extra):
    tr, va = preparar_dados()
    return C.criar_parser().parse_args(["treinar", "--dados", tr, "--val_dados", va, "--tamanho", "mini", "--pasta", pasta,
                                        "--lote", "4", "--avaliar_cada", "0", "--log_cada", "0", "--aquecimento", "2",
                                        "--precisao", "fp32", *extra])


class TestTreino(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_perda_cai(self):
        r = C.treinar(args_treino(os.path.join(self.tmp, "a"), "--tokenizador", "caractere", "--passos", "20", "--lr", "3e-3"))
        p = r["perdas"]
        self.assertLess(sum(p[-3:]) / 3, sum(p[:3]) / 3 - 0.3)

    def test_retomada_exata_bpe(self):
        bpe = os.path.join(self.tmp, "bpe.json")
        tr, _ = preparar_dados()
        tk = TokenizerBPE.treinar([open(tr, encoding="utf-8").read()], vocab=500, verbose=False)
        json.dump(tk.para_dict(), open(bpe, "w", encoding="utf-8"))
        comum = ["--tokenizador", "bpe", "--tokenizador_json", bpe, "--passos", "6", "--lr", "2e-3", "--acumular", "2"]
        # treino contínuo de 6 passos
        cont = C.treinar(args_treino(os.path.join(self.tmp, "cont"), *comum))
        # treino interrompido após 5 passos (checkpoint) e retomado
        pasta = os.path.join(self.tmp, "ret")
        r1 = C.treinar(args_treino(pasta, *comum, "--parar_apos", "5"))
        self.assertFalse(r1["concluido"])
        r2 = C.treinar(args_treino(pasta, *comum, "--retomar"))
        self.assertEqual(len(r2["perdas"]), 1)
        self.assertEqual(r1["perdas"], cont["perdas"][:5])
        self.assertEqual(r2["perdas"][0], cont["perdas"][5])  # perda do passo 6 IDÊNTICA (comparação exata)
        a = torch.load(os.path.join(self.tmp, "cont", "modelo.pt"), weights_only=True)["modelo"]
        b = torch.load(os.path.join(pasta, "modelo.pt"), weights_only=True)["modelo"]
        self.assertTrue(all(torch.equal(a[k], b[k]) for k in a))
        self.assertFalse(os.path.exists(os.path.join(pasta, "checkpoint.pt.tmp")))

    def test_estender_nao_reaquece(self):
        pasta = os.path.join(self.tmp, "est")
        base = ["--tokenizador", "caractere", "--lr", "1e-3", "--aquecimento", "3"]
        C.treinar(args_treino(pasta, *base, "--passos", "4", "--parar_apos", "4", "--estavel_ate", "100", "--descida", "0.2"))
        a = args_treino(pasta, *base, "--passos", "8", "--estavel_ate", "7", "--retomar", "--estender")
        r = C.treinar(a)
        self.assertEqual(len(r["perdas"]), 4)
        self.assertEqual(a.lr, 1e-3)

    def test_avaliar_cmd(self):
        pasta = os.path.join(self.tmp, "av")
        C.treinar(args_treino(pasta, "--tokenizador", "caractere", "--passos", "3"))
        _, va = preparar_dados()
        a = C.criar_parser().parse_args(["avaliar", "--val_dados", va, "--pasta", pasta, "--precisao", "fp32"])
        perda, b = C.avaliar_cmd(a)
        self.assertAlmostEqual(b, perda / math.log(2), places=4)  # caractere: BPC = perda/ln2


class TestServidor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tk = TokenizerCaractere("abcdefghijklmnopqrstuvwxyz \n")
        m = modelo_mini(tk.n_vocab)
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), C.criar_manipulador(m, tk, "cpu"))
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.srv.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def post(self, corpo):
        req = urllib.request.Request(self.url + "/gerar", json.dumps(corpo).encode(), {"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            return e.code, json.load(e)

    def test_saude(self):
        with urllib.request.urlopen(self.url + "/saude") as r:
            self.assertTrue(json.load(r)["ok"])

    def test_gerar_basico_e_parar_em(self):
        st, r = self.post({"inicio": "ab", "n": 40, "temperatura": 1.0, "parar_em": []})
        self.assertEqual(st, 200)
        self.assertEqual(len(r["texto"]), 40)
        st, r = self.post({"inicio": "ab", "n": 300, "temperatura": 1.0, "parar_em": ["e"]})
        self.assertEqual(st, 200)
        self.assertNotIn("e", r["texto"])
        self.assertLess(len(r["texto"]), 300)

    def test_parar_em_padrao_quebra_dupla(self):
        for _ in range(5):
            st, r = self.post({"inicio": "ab", "n": 400, "temperatura": 1.0})
            self.assertEqual(st, 200)
            self.assertNotIn("\n\n", r["texto"])

    def test_requisicao_invalida(self):
        self.assertEqual(self.post({"n": 5})[0], 400)
        self.assertEqual(self.post({"inicio": "a", "temperatura": 0})[0], 400)
        self.assertEqual(self.post({"inicio": "a", "parar_em": "x"})[0], 400)


if __name__ == "__main__":
    unittest.main()
