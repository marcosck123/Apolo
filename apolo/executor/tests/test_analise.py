import unittest
from unittest.mock import patch
from executor.servidor import analisar


class TestAnalise(unittest.TestCase):
    def test_pecas_sem_executar(self):
        with patch('executor.servidor.executar', side_effect=AssertionError('não executar')):
            r = analisar('import statistics\nfrom math import sqrt\ndef media(xs):\n    if xs:\n        return statistics.mean([x for x in xs])\nraise RuntimeError("não rodar")')
        self.assertEqual(r['funcoes'], ['media'])
        self.assertEqual(r['importacoes'], ['math', 'statistics'])
        self.assertIn('statistics.mean', r['chamadas'])
        self.assertTrue({'def', 'return', 'if', 'comprehension'} <= set(r['estruturas']))

    def test_limites(self):
        for codigo in ['', 'x' * 20001, 'if :', 'x=' + '1+' * 100 + '1']:
            with self.assertRaises(ValueError):
                analisar(codigo)

    def test_posicoes_unicode_e_strings(self):
        codigo = 'nome = "😀á"; lista = [1, 2] # 99'
        r = analisar(codigo)
        valores = [codigo[t['inicio']:t['fim']] for t in r['trechos']]
        self.assertIn('"😀á"', valores)
        self.assertIn('[1, 2]', valores)
        self.assertNotIn('99', valores)

    def test_aliases_e_nomes_redefinidos(self):
        r = analisar('from statistics import mean as media\nimport math as m\nsum = lambda x: 0\nprint(media([1]), m.sqrt(4), sum([2]))')
        self.assertIn('statistics.mean', r['chamadas'])
        self.assertIn('math.sqrt', r['chamadas'])
        self.assertNotIn('sum', r['chamadas'])
