import unittest
from executor.servidor import executar, LIMITE_SAIDA


class TestExecutor(unittest.TestCase):
    def test_timeout(self):
        resultado = executar('while True: pass')
        self.assertTrue(resultado['estourou_tempo'])
        self.assertTrue(resultado['erro'])

    def test_saida_truncada(self):
        resultado = executar('print("a" * 50000)')
        self.assertEqual(len(resultado['saida']), LIMITE_SAIDA)
        self.assertEqual(resultado['erro'], '')

    def test_excecao(self):
        self.assertIn('ValueError', executar('raise ValueError("exemplo")')['erro'])

    def test_entradas(self):
        self.assertEqual(executar('print(input() + input())', ['olá', '!'])['saida'], 'olá!\n')
