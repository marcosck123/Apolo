"""Testes da aptidão. Rodar: python3 -m unittest discover -s aptidao/tests -v   (precisa de Docker)."""
import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
import corretor  # noqa: E402
import gerador  # noqa: E402
import modelos_falsos as mf  # noqa: E402
import rodar  # noqa: E402

_cache = {}


def problemas():
    if "p" not in _cache:
        _cache["p"], _cache["st"] = gerador.gerar(50, 9000)
    return _cache["p"]


def taxa(modelo, ps):
    res = corretor.corrigir(ps, {p["id"]: modelo(p) for p in ps})
    return sum(r["ok"] for r in res.values()) / len(ps), res


class TestExtracao(unittest.TestCase):
    def test_para_em_saida(self):
        self.assertEqual(corretor.extrair_codigo("a = 1\nprint(a)\nSaída:\n1\nExplicação"), "a = 1\nprint(a)")

    def test_para_em_linha_vazia(self):
        self.assertEqual(corretor.extrair_codigo("print(1)\n\nExercício: outro"), "print(1)")

    def test_vazio(self):
        self.assertEqual(corretor.extrair_codigo(""), "")

    def test_normalizar(self):
        self.assertEqual(corretor.normalizar("a  \n b\n\n"), "a\nb")


class TestGerador(unittest.TestCase):
    def test_categorias_e_formato(self):
        ps = problemas()
        self.assertEqual({p["categoria"] for p in ps}, set(gerador.CATEGORIAS))
        for p in ps:
            self.assertTrue(p["prompt"].startswith("Exercício: ") and p["prompt"].endswith("\nSolução:\n"))
            self.assertTrue(p["saida_esperada"])
        self.assertEqual(len({p["id"] for p in ps}), len(ps))

    def test_determinismo(self):
        a, _ = gerador.gerar(10, 9000, ["python_basico"])
        b, _ = gerador.gerar(10, 9000, ["python_basico"])
        self.assertEqual([p["enunciado"] for p in a], [p["enunciado"] for p in b])

    def test_anti_contaminacao(self):
        livres, _ = gerador.gerar(10, 9000, ["python_basico"], proibidos=set())
        banidos = {p["enunciado"] for p in livres[:5]}
        novos, st = gerador.gerar(10, 9000, ["python_basico"], proibidos=banidos)
        self.assertFalse(banidos & {p["enunciado"] for p in novos})
        self.assertGreaterEqual(st["python_basico"]["contaminados"], 5)

    def test_carregar_enunciados(self):
        with tempfile.TemporaryDirectory() as d:
            arq = os.path.join(d, "t.txt")
            with open(arq, "w", encoding="utf-8") as f:
                f.write("Lição: x\nExercício: Some 1 e 2.\nSolução:\nprint(3)\n\nExercício: Outro\n")
            self.assertEqual(gerador.carregar_enunciados_treino(arquivos=[arq]), {"Some 1 e 2.", "Outro"})

    def test_nada_do_treino_real(self):
        proibidos = gerador.carregar_enunciados_treino()
        self.assertGreater(len(proibidos), 1000)
        self.assertFalse({p["enunciado"] for p in problemas()} & proibidos)


class TestCorretor(unittest.TestCase):
    def test_oraculo_100(self):
        t, res = taxa(mf.oraculo, problemas())
        falhas = [(k, v) for k, v in res.items() if not v["ok"]]
        self.assertEqual(t, 1.0, falhas[:3])

    def test_vazio_0(self):
        self.assertEqual(taxa(mf.vazio, problemas())[0], 0.0)

    def test_lixo_0(self):
        self.assertEqual(taxa(mf.lixo, problemas())[0], 0.0)

    def test_quase_falha(self):
        # Trocar um dígito quase sempre muda a saída; alguns poucos casos são mutantes equivalentes
        # (o dígito não afeta o resultado), por isso o limite não é exatamente zero.
        t, res = taxa(mf.quase, problemas())
        self.assertLessEqual(t, 0.2)
        self.assertTrue(any(v["motivo"] == "saida_diferente" for v in res.values()))

    def test_isolamento_timeout_e_rede(self):
        p = [{"id": "x1", "tipo": "python", "saida_esperada": "oi", "entradas": None},
             {"id": "x2", "tipo": "python", "saida_esperada": "oi", "entradas": None},
             {"id": "x3", "tipo": "python", "saida_esperada": "oi", "entradas": None}]
        textos = {"x1": "while True: pass",
                  "x2": "import socket\ns=socket.socket()\ns.settimeout(3)\ns.connect(('1.1.1.1',80))\nprint('oi')",
                  "x3": "open('/escrita_proibida','w').write('x')\nprint('oi')"}
        res = corretor.corrigir(p, textos, timeout=3)
        self.assertEqual(res["x1"]["motivo"], "timeout")
        self.assertFalse(res["x2"]["ok"])   # sem rede
        self.assertFalse(res["x3"]["ok"])   # sistema de arquivos somente leitura
        self.assertTrue(os.path.exists("/") and not os.path.exists("/escrita_proibida"))


class TestEstatistica(unittest.TestCase):
    def test_wilson(self):
        lo, hi = rodar.wilson(50, 100)
        self.assertAlmostEqual(lo, 0.404, places=2)
        self.assertAlmostEqual(hi, 0.596, places=2)
        self.assertEqual(rodar.wilson(0, 0), (0.0, 0.0))
        self.assertEqual(rodar.wilson(10, 10)[1], 1.0)


class TestCliComServidorFalso(unittest.TestCase):
    def test_http_retomada_e_comparacao(self):
        ps, _ = gerador.gerar(10, 9100, ["python_basico", "sql"])
        por_prompt = {p["prompt"]: p for p in ps}
        chamadas = []

        class H(BaseHTTPRequestHandler):
            def do_POST(self):
                req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                chamadas.append(req["inicio"])
                p = por_prompt[req["inicio"]]
                corpo = json.dumps({"texto": mf.oraculo(p)}).encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(corpo)))
                self.end_headers()
                self.wfile.write(corpo)

            def log_message(self, *a):
                pass
        srv = HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{srv.server_port}"
        rot = "teste_unit_" + str(os.getpid())
        arq = os.path.join(os.path.dirname(AQUI), "resultados", rot + ".jsonl")
        try:
            args = [sys.executable, os.path.join(os.path.dirname(AQUI), "rodar.py"), "--url", url, "--n", "10",
                    "--semente", "9100", "--categorias", "python_basico", "sql", "--rotulo", rot]
            import subprocess
            r = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("100.0%", r.stdout)
            self.assertEqual(len(chamadas), 10)
            # retomada: nada novo deve ser pedido ao servidor
            r = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(len(chamadas), 10)
            self.assertIn("Retomando", r.stdout)
            r = subprocess.run([sys.executable, os.path.join(os.path.dirname(AQUI), "rodar.py"), "--comparar", arq, arq],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("TOTAL", r.stdout)
        finally:
            srv.shutdown()
            if os.path.exists(arq):
                os.remove(arq)


if __name__ == "__main__":
    unittest.main()
