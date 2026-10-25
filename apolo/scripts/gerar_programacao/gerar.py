"""Monta os arquivos de treino de programação do Apolo.
Uso: python gerar.py <pasta_destino> [exercicios_basico] [exercicios_intermediario]
Os arquivos de JavaScript precisam do Docker (o Node roda dentro dele): rode com `sg docker -c "python3 gerar.py ..."`
ou, sem Docker, passe --sem-js.
"""
import os
import random
import sys

import basico
import intermediario
import python_extra
import sql
import terminal
from lib import NODE, licao

REPETIR_LICOES = 3      # lições escritas à mão aparecem 3 vezes (o córtex precisa ver o mesmo texto mais de uma vez)
REPETIR_PERGUNTAS = 4   # perguntas e respostas curtas aparecem 4 vezes, em ordem embaralhada


def montar(titulo, intro, modulo, n_exercicios, semente):
    rng = random.Random(semente)
    licoes = modulo.licoes()
    blocos = [licao(titulo, *intro)]
    for _ in range(REPETIR_LICOES):
        blocos += licoes
    for _ in range(REPETIR_PERGUNTAS):
        qs = modulo.perguntas()
        rng.shuffle(qs)
        blocos += qs
    blocos += modulo.exercicios(rng, n_exercicios)
    return "\n\n".join(blocos) + "\n"


def _intro(linguagem, nivel):
    return (f"Este texto ensina {linguagem}, nível {nivel}.",
            "Cada exemplo mostra o código, a saída que ele produz e uma explicação.",
            "Os exercícios mostram o enunciado, a solução, a saída e o porquê.")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sem_js = "--sem-js" in sys.argv
    destino = args[0] if args else "saida"
    n_bas = int(args[1]) if len(args) > 1 else 4000
    n_int = int(args[2]) if len(args) > 2 else 3500
    os.makedirs(destino, exist_ok=True)
    arquivos = {
        "06_programacao_basico.txt": lambda: montar(
            "Programação Básica", _intro("programação em Python", "básica"), basico, n_bas, 6),
        "07_programacao_intermediario.txt": lambda: montar(
            "Programação Intermediária", _intro("programação em Python", "intermediária"), intermediario, n_int, 7),
        "08_python_biblioteca_e_erros.txt": lambda: montar(
            "Python: biblioteca padrão e erros", _intro("a biblioteca padrão do Python e como corrigir erros", "intermediário"), python_extra, 1500, 8),
        "10_sql.txt": lambda: montar(
            "SQL e bancos de dados", _intro("SQL, a linguagem dos bancos de dados", "básico"), sql, 1200, 10),
        "11_terminal_git_docker.txt": lambda: montar(
            "Terminal, Git e Docker", _intro("o terminal do Linux, o Git e o Docker", "básico"), terminal, 1000, 11),
    }
    if not sem_js:
        import javascript
        arquivos["09_javascript.txt"] = lambda: montar(
            "JavaScript e Node.js", _intro("JavaScript e Node.js", "básico"), javascript, 1500, 9)
    for nome, fazer in sorted(arquivos.items()):
        texto = fazer()
        with open(os.path.join(destino, nome), "w", encoding="utf-8") as f:
            f.write(texto)
        print(f"{nome}: {len(texto):,} caracteres")
    NODE.fechar()


if __name__ == "__main__":
    main()
