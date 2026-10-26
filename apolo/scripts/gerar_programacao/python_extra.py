"""Python além do básico: biblioteca padrão (datetime, math, random, re, csv, collections, itertools, urllib)
e erros reais com a correção de cada um. Todo exemplo é executado de verdade."""
from lib import exemplo, exercicio, qa, licao, lista_py, NOMES, FRUTAS, PRODUTOS, CIDADES, PALAVRAS


def _corrige(pergunta, errado, erro_resumo, certo, explicacao):
    """Dois blocos: o código com erro e o código corrigido."""
    return [
        exemplo(f"{pergunta} (com erro)", errado, f"Esse código quebra. {erro_resumo}", erro_esperado=True),
        exemplo(f"{pergunta} (corrigido)", certo, explicacao),
    ]


def licoes():
    b = []
    b.append(licao(
        "Módulos e a biblioteca padrão",
        "Um módulo é um arquivo Python com funções prontas. Para usar, escrevemos import nome_do_módulo.",
        "A biblioteca padrão já vem com o Python: math, random, datetime, re, json, csv, collections e muitas outras.",
        "Também dá para importar só uma parte: from math import sqrt.",
    ))
    b.append(exemplo("Como usar o módulo math?", "import math\nprint(math.sqrt(16))\nprint(math.pi)\nprint(math.ceil(4.2))\nprint(math.floor(4.8))\nprint(math.pow(2, 10))",
                     "sqrt tira a raiz quadrada, pi é o valor de pi, ceil arredonda para cima, floor para baixo e pow eleva à potência."))
    b.append(exemplo("Como importar só uma função?", "from math import sqrt, factorial\nprint(sqrt(81))\nprint(factorial(5))",
                     "from math import traz direto os nomes escolhidos, sem precisar escrever math. na frente."))
    b.append(licao(
        "Números aleatórios com random",
        "O módulo random sorteia números e escolhe itens de listas.",
        "random.seed(n) fixa a sequência sorteada, o que é útil para testes: com a mesma semente sai sempre o mesmo resultado.",
        "randint(a, b) sorteia um inteiro entre a e b, choice escolhe um item e shuffle embaralha uma lista.",
    ))
    b.append(exemplo("Como sortear um número?", "import random\nrandom.seed(7)\nn = random.randint(1, 10)\nprint(1 <= n <= 10)",
                     "randint sorteia entre 1 e 10, incluindo os dois. O print confirma que o número está dentro da faixa."))
    b.append(exemplo("Como escolher um item de uma lista?", 'import random\nfrutas = ["maçã", "uva", "pera"]\nescolhida = random.choice(frutas)\nprint(escolhida in frutas)',
                     "choice devolve um item da lista, sempre um dos que estão nela."))
    b.append(exemplo("Como embaralhar uma lista?", "import random\nnums = [1, 2, 3, 4, 5]\nrandom.shuffle(nums)\nprint(sorted(nums))\nprint(len(nums))",
                     "shuffle muda a ordem da própria lista, mas continuam os mesmos cinco números, o que sorted confirma."))
    b.append(licao(
        "Datas com datetime",
        "O módulo datetime trabalha com datas e horas.",
        "date(ano, mês, dia) cria uma data. Subtrair duas datas dá um timedelta, que guarda a diferença em dias.",
        "strftime transforma a data em texto com um formato, como %d/%m/%Y para dia/mês/ano.",
    ))
    b.append(exemplo("Como criar uma data?", "from datetime import date\nd = date(2026, 12, 25)\nprint(d)\nprint(d.year)\nprint(d.month)\nprint(d.day)",
                     "Uma data mostra ano-mês-dia, e year, month e day devolvem cada parte."))
    b.append(exemplo("Como calcular a diferença entre duas datas?", "from datetime import date\ninicio = date(2026, 1, 1)\nfim = date(2026, 3, 1)\nprint((fim - inicio).days)",
                     "Subtrair as datas dá um timedelta, e .days diz quantos dias há entre elas: 59."))
    b.append(exemplo("Como somar dias a uma data?", "from datetime import date, timedelta\nd = date(2026, 1, 28)\nprint(d + timedelta(days=5))",
                     "timedelta(days=5) representa cinco dias. Somar à data avança para o dia 2 de fevereiro."))
    b.append(exemplo("Como mostrar a data no formato brasileiro?", 'from datetime import date\nd = date(2026, 7, 4)\nprint(d.strftime("%d/%m/%Y"))',
                     "%d é o dia, %m o mês e %Y o ano com quatro dígitos."))
    b.append(licao(
        "Expressões regulares com re",
        "Uma expressão regular, ou regex, descreve um padrão de texto.",
        "Alguns símbolos: \\d é um dígito, \\w é uma letra ou número, + significa um ou mais, e . é qualquer caractere.",
        "re.search procura o padrão, re.findall devolve todas as ocorrências e re.sub troca o padrão por outro texto.",
    ))
    b.append(exemplo("Como achar todos os números de um texto?", 'import re\ntexto = "Comprei 3 maçãs e 12 peras por 25 reais"\nprint(re.findall(r"\\d+", texto))',
                     "\\d+ casa com um ou mais dígitos seguidos, e findall devolve todos os pedaços encontrados."))
    b.append(exemplo("Como trocar parte de um texto com regex?", 'import re\ntexto = "Meu telefone é 69 99999-1234"\nprint(re.sub(r"\\d", "X", texto))',
                     "sub trocou cada dígito pela letra X."))
    b.append(exemplo("Como validar um padrão?", 'import re\nfor cep in ["76980-000", "7698-000"]:\n    print(cep, bool(re.fullmatch(r"\\d{5}-\\d{3}", cep)))',
                     "O padrão exige cinco dígitos, um hífen e três dígitos. O segundo CEP tem só quatro no começo e não casa."))
    b.append(licao(
        "Arquivos CSV",
        "CSV é um formato de tabela em texto, com os valores de cada linha separados por vírgula.",
        "O módulo csv lê e escreve esse formato. DictReader usa a primeira linha como nome das colunas.",
    ))
    b.append(exemplo("Como ler dados CSV?", 'import csv, io\ndados = "nome,idade\\nAna,20\\nBruno,25"\nfor linha in csv.DictReader(io.StringIO(dados)):\n    print(linha["nome"], linha["idade"])',
                     "DictReader transformou cada linha num dicionário usando o cabeçalho. Os valores chegam como texto."))
    b.append(licao(
        "collections e itertools",
        "defaultdict é um dicionário que cria um valor inicial sozinho quando a chave não existe.",
        "deque é uma fila eficiente nas duas pontas. Counter conta itens.",
        "itertools tem ferramentas para combinar listas, como product, permutations e combinations.",
    ))
    b.append(exemplo("Como usar defaultdict?", 'from collections import defaultdict\ngrupos = defaultdict(list)\nfor palavra in ["uva", "pera", "urso", "pato"]:\n    grupos[palavra[0]].append(palavra)\nprint(dict(grupos))',
                     "Cada chave nova ganha uma lista vazia sozinha, então dá para usar append direto."))
    b.append(exemplo("Como usar deque?", "from collections import deque\nfila = deque([1, 2, 3])\nfila.append(4)\nprint(fila.popleft())\nprint(list(fila))",
                     "append coloca no fim e popleft tira do começo, como uma fila de verdade."))
    b.append(exemplo("Como gerar combinações?", "from itertools import combinations, permutations\nprint(list(combinations([1, 2, 3], 2)))\nprint(len(list(permutations([1, 2, 3]))))",
                     "combinations forma pares sem repetição. permutations testa todas as ordens: com 3 itens são 6."))
    b.append(licao(
        "Formatação de números e textos",
        "Dentro de uma f-string podemos formatar: {x:.2f} usa duas casas decimais, {x:>8} alinha à direita em 8 posições e {x:,} separa milhares.",
        "{x:05d} completa com zeros à esquerda, e {x:.1%} mostra como porcentagem.",
    ))
    b.append(exemplo("Como formatar números numa f-string?", 'preco = 1234.5\nprint(f"R$ {preco:.2f}")\nprint(f"{preco:,.2f}")\nprint(f"{7:03d}")\nprint(f"{0.256:.1%}")',
                     ".2f fixa duas casas, a vírgula separa milhares, 03d completa com zeros e .1% mostra porcentagem."))
    b.append(exemplo("Como alinhar colunas de texto?", 'itens = [("arroz", 25.9), ("feijão", 8.5)]\nfor nome, preco in itens:\n    print(f"{nome:<10}{preco:>8.2f}")',
                     "< alinha à esquerda em 10 posições e > alinha à direita em 8, o que deixa as colunas alinhadas."))
    b.append(licao(
        "Ambientes virtuais e pip",
        "pip instala bibliotecas de terceiros: pip install nome.",
        "Um ambiente virtual isola as bibliotecas de cada projeto. Cria-se com python -m venv .venv e ativa-se com source .venv/bin/activate.",
        "O arquivo requirements.txt lista as bibliotecas do projeto, e pip install -r requirements.txt instala todas.",
        "requests faz chamadas HTTP, e pandas e numpy trabalham com dados.",
    ))
    b.append(licao(
        "Lendo erros do Python",
        "Todo erro mostra o tipo e uma mensagem. Leia sempre a última linha primeiro: ela diz o que aconteceu.",
        "As linhas de cima mostram o caminho, de qual arquivo e linha o erro veio.",
        "NameError é um nome que não existe, TypeError é um tipo errado, ValueError é um valor inválido, e IndexError e KeyError são posições ou chaves que não existem.",
    ))
    b += _corrige("Por que dá NameError?", "total = 10\nprint(totl)", "A última linha diz que o nome totl não está definido: foi um erro de digitação.",
                  "total = 10\nprint(total)", "O nome da variável tem de ser escrito igual nas duas partes.")
    b += _corrige("Por que dá TypeError ao somar texto e número?", 'idade = 20\nprint("Tenho " + idade + " anos")',
                  "Não dá para somar texto com número.", 'idade = 20\nprint("Tenho " + str(idade) + " anos")',
                  "str(idade) converte o número em texto, e aí a soma de textos funciona. Uma f-string também resolveria.")
    b += _corrige("Por que dá IndexError?", "frutas = ['maçã', 'uva']\nprint(frutas[2])", "A lista tem duas posições, 0 e 1. A posição 2 não existe.",
                  "frutas = ['maçã', 'uva']\nprint(frutas[1])", "O último item de uma lista de tamanho 2 está na posição 1.")
    b += _corrige("Por que dá KeyError?", "preco = {'arroz': 25}\nprint(preco['feijão'])", "O dicionário não tem a chave feijão.",
                  "preco = {'arroz': 25}\nprint(preco.get('feijão', 0))", "get devolve um valor padrão, aqui 0, em vez de dar erro quando a chave não existe.")
    b += _corrige("Por que dá ValueError ao converter texto?", "n = int('abc')", "abc não é um número, então int não consegue converter.",
                  "texto = '42'\nn = int(texto)\nprint(n + 1)", "42 é um texto que representa um número, então a conversão funciona.")
    b += _corrige("Por que dá ZeroDivisionError?", "print(10 / 0)", "Não existe divisão por zero.",
                  "divisor = 0\nif divisor != 0:\n    print(10 / divisor)\nelse:\n    print('Divisão por zero')", "Testar o divisor antes evita o erro.")
    b += _corrige("Por que dá AttributeError?", "nome = 'Ana'\nnome.adicionar('!')", "Textos não têm um método chamado adicionar.",
                  "nome = 'Ana'\nprint(nome + '!')", "Para juntar textos usamos o operador +, e não um método que não existe.")
    b += _corrige("Por que dá IndentationError?", "if True:\nprint('oi')", "Depois do dois-pontos, a linha seguinte precisa estar indentada.",
                  "if True:\n    print('oi')", "Quatro espaços no começo da linha mostram que ela faz parte do if.")
    b += _corrige("Por que dá UnboundLocalError?", "contador = 0\ndef somar():\n    contador = contador + 1\nsomar()", "Dentro da função, contador é tratado como variável local que ainda não tem valor.",
                  "contador = 0\ndef somar():\n    global contador\n    contador = contador + 1\nsomar()\nprint(contador)", "global avisa que contador é a variável de fora. O melhor, porém, é devolver o valor com return.")
    return b


def perguntas():
    return [
        qa("O que é um módulo em Python?", "É um arquivo com funções prontas que importamos com import."),
        qa("O que é a biblioteca padrão?", "É o conjunto de módulos que já vem com o Python, como math, random, datetime, re e json."),
        qa("Como importar só uma função de um módulo?", "Com from modulo import funcao, por exemplo from math import sqrt."),
        qa("Como tirar a raiz quadrada em Python?", "Com math.sqrt(numero), depois de import math."),
        qa("Como sortear um número entre 1 e 10?", "Com random.randint(1, 10), depois de import random."),
        qa("Para que serve o random.seed?", "Fixa a sequência sorteada, para o resultado ser sempre o mesmo em testes."),
        qa("Como calcular os dias entre duas datas?", "Subtraia as datas: (fim - inicio).days."),
        qa("Como mostrar uma data em dia/mês/ano?", "Com data.strftime('%d/%m/%Y')."),
        qa("O que é uma expressão regular?", "Um padrão que descreve um tipo de texto, usado para buscar ou validar."),
        qa("O que faz o re.findall?", "Devolve uma lista com todos os trechos que casam com o padrão."),
        qa("O que é CSV?", "É um formato de tabela em texto, com valores separados por vírgula."),
        qa("O que é o defaultdict?", "Um dicionário que cria um valor inicial sozinho quando a chave não existe."),
        qa("O que é o pip?", "É o programa que instala bibliotecas de terceiros, como pip install requests."),
        qa("O que é um ambiente virtual?", "Uma pasta que isola as bibliotecas de cada projeto. Cria-se com python -m venv .venv."),
        qa("Para que serve o requirements.txt?", "Lista as bibliotecas do projeto, para instalar todas com pip install -r requirements.txt."),
        qa("O que significa NameError?", "O nome usado não existe. Quase sempre é erro de digitação ou variável não criada."),
        qa("O que significa TypeError?", "Uma operação foi feita com o tipo errado, como somar texto com número."),
        qa("O que significa IndexError?", "Foi pedida uma posição que não existe na lista."),
        qa("O que significa KeyError?", "Foi pedida uma chave que não existe no dicionário."),
        qa("O que significa ValueError?", "O tipo está certo, mas o valor não serve, como int('abc')."),
        qa("O que significa ZeroDivisionError?", "Houve uma divisão por zero."),
        qa("O que significa IndentationError?", "A indentação, o espaço no começo da linha, está errada."),
        qa("Qual a primeira coisa a ler num erro do Python?", "A última linha, que mostra o tipo do erro e a mensagem."),
        qa("Como formatar um número com duas casas decimais?", "Numa f-string, com {valor:.2f}."),
    ]


def exercicios(rng, n):
    familias = [_ex_dias_entre, _ex_somar_dias, _ex_data_br, _ex_raiz, _ex_numeros_regex, _ex_defaultdict, _ex_csv,
                _ex_formatar, _ex_combinacoes, _ex_deque, _ex_erro_indice, _ex_erro_chave, _ex_erro_tipo,
                _ex_trocar_regex, _ex_potencia, _ex_arredondar]
    blocos = [familias[i % len(familias)](rng) for i in range(n)]
    rng.shuffle(blocos)
    return blocos


def _data(rng):
    return rng.randint(2024, 2027), rng.randint(1, 12), rng.randint(1, 28)


def _ex_dias_entre(rng):
    a, b = _data(rng), _data(rng)
    if a > b:
        a, b = b, a
    return exercicio(f"Calcule quantos dias há entre {a[2]:02d}/{a[1]:02d}/{a[0]} e {b[2]:02d}/{b[1]:02d}/{b[0]}.",
                     f"from datetime import date\ninicio = date({a[0]}, {a[1]}, {a[2]})\nfim = date({b[0]}, {b[1]}, {b[2]})\nprint((fim - inicio).days)",
                     "Subtrair as datas dá um timedelta, e .days mostra a diferença em dias.")


def _ex_somar_dias(rng):
    y, m, d = _data(rng)
    k = rng.randint(3, 90)
    return exercicio(f"Mostre a data que vem {k} dias depois de {d:02d}/{m:02d}/{y}, no formato dia/mês/ano.",
                     f'from datetime import date, timedelta\ndata = date({y}, {m}, {d}) + timedelta(days={k})\nprint(data.strftime("%d/%m/%Y"))',
                     f"timedelta(days={k}) avança {k} dias, e strftime escreve no formato brasileiro.")


def _ex_data_br(rng):
    y, m, d = _data(rng)
    return exercicio(f"Crie a data {y}-{m:02d}-{d:02d} e mostre o dia da semana pelo número, onde segunda é 0.",
                     f"from datetime import date\nprint(date({y}, {m}, {d}).weekday())",
                     "weekday devolve 0 para segunda, 1 para terça, e assim até 6 para domingo.")


def _ex_raiz(rng):
    n = rng.choice([4, 9, 16, 25, 36, 49, 64, 81, 100, 144, 169])
    return exercicio(f"Calcule a raiz quadrada de {n}.", f"import math\nprint(math.sqrt({n}))",
                     "math.sqrt devolve sempre um número com vírgula, mesmo quando a raiz é exata.")


def _ex_numeros_regex(rng):
    partes = [rng.choice(FRUTAS) for _ in range(3)]
    ns = [rng.randint(1, 99) for _ in range(3)]
    texto = " e ".join(f"{n} {p}" for n, p in zip(ns, partes))
    return exercicio(f"Ache todos os números do texto '{texto}' e some.",
                     f'import re\ntexto = "{texto}"\nnumeros = [int(n) for n in re.findall(r"\\d+", texto)]\nprint(numeros)\nprint(sum(numeros))',
                     "findall acha os trechos de dígitos, int converte cada um e sum soma.")


def _ex_defaultdict(rng):
    ps = rng.sample(PALAVRAS, 6)
    return exercicio(f"Agrupe as palavras {lista_py(ps)} pela primeira letra.",
                     f"from collections import defaultdict\npalavras = {lista_py(ps)}\ngrupos = defaultdict(list)\nfor p in palavras:\n    grupos[p[0]].append(p)\nprint(dict(grupos))",
                     "A primeira letra é a chave, e cada palavra entra na lista da sua letra.")


def _ex_csv(rng):
    nomes = rng.sample(NOMES, 3)
    notas = [rng.randint(4, 10) for _ in nomes]
    linhas = "\\n".join(f"{n},{x}" for n, x in zip(nomes, notas))
    return exercicio("Leia os dados CSV de alunos e mostre a média das notas.",
                     f'import csv, io\ndados = "nome,nota\\n{linhas}"\nnotas = [int(l["nota"]) for l in csv.DictReader(io.StringIO(dados))]\nprint(sum(notas) / len(notas))',
                     "DictReader lê cada linha como dicionário, e a média é a soma das notas dividida pela quantidade.")


def _ex_formatar(rng):
    nome, preco = rng.choice(PRODUTOS)
    q = rng.randint(2, 9)
    return exercicio(f"Mostre o total de {q} unidades de {nome} a {preco} cada, com duas casas decimais.",
                     f'preco = {preco}\nquantidade = {q}\nprint(f"Total: R$ {{preco * quantidade:.2f}}")',
                     ".2f mostra sempre duas casas depois da vírgula.")


def _ex_combinacoes(rng):
    itens = rng.sample(FRUTAS, 3)
    return exercicio(f"Mostre todas as duplas diferentes que dá para formar com {lista_py(itens)}.",
                     f"from itertools import combinations\nfor dupla in combinations({lista_py(itens)}, 2):\n    print(dupla)",
                     "combinations forma os pares sem repetir e sem se importar com a ordem.")


def _ex_deque(rng):
    xs = rng.sample(range(1, 50), 4)
    return exercicio(f"Use uma fila com {xs}: atenda os dois primeiros e mostre quem sobrou.",
                     f"from collections import deque\nfila = deque({xs})\nfila.popleft()\nfila.popleft()\nprint(list(fila))",
                     "popleft tira sempre do começo da fila.")


def _ex_erro_indice(rng):
    xs = rng.sample(range(1, 50), rng.randint(3, 5))
    return exemplo(f"O que acontece ao pedir a posição {len(xs)} da lista {lista_py(xs)}?",
                   f"nums = {lista_py(xs)}\nprint(nums[{len(xs)}])",
                   f"A lista tem {len(xs)} itens, nas posições de 0 a {len(xs) - 1}. A posição {len(xs)} não existe.", erro_esperado=True)


def _ex_erro_chave(rng):
    nome, preco = rng.choice(PRODUTOS)
    outro = rng.choice([p for p, _ in PRODUTOS if p != nome])
    return exemplo(f"O que acontece ao buscar {outro} num dicionário que só tem {nome}?",
                   f'precos = {{"{nome}": {preco}}}\nprint(precos["{outro}"])',
                   "A chave não existe, então dá KeyError. O método get evitaria o erro.", erro_esperado=True)


def _ex_erro_tipo(rng):
    a, b = rng.randint(2, 50), rng.choice(FRUTAS)
    return exemplo(f"O que acontece ao somar o número {a} com o texto '{b}'?",
                   f'print({a} + "{b}")',
                   "Somar número com texto dá TypeError. É preciso converter um dos dois.", erro_esperado=True)


def _ex_trocar_regex(rng):
    cidade = rng.choice(CIDADES)
    tel = f"{rng.randint(10, 99)} 9{rng.randint(1000, 9999)}-{rng.randint(1000, 9999)}"
    return exercicio(f"Esconda os números do texto 'Fale com {cidade} no {tel}' trocando cada dígito por *.",
                     f'import re\ntexto = "Fale com {cidade} no {tel}"\nprint(re.sub(r"\\d", "*", texto))',
                     "re.sub troca cada dígito encontrado por um asterisco.")


def _ex_potencia(rng):
    b, e = rng.randint(2, 9), rng.randint(2, 8)
    return exercicio(f"Calcule {b} elevado a {e} de duas formas.",
                     f"import math\nprint({b} ** {e})\nprint(int(math.pow({b}, {e})))",
                     f"O operador ** e math.pow dão o mesmo resultado: {b ** e}.")


def _ex_arredondar(rng):
    x = round(rng.uniform(1, 100), 3)
    return exercicio(f"Arredonde {x} para duas casas, para cima e para baixo.",
                     f"import math\nx = {x}\nprint(round(x, 2))\nprint(math.ceil(x))\nprint(math.floor(x))",
                     "round arredonda para a casa pedida, ceil sobe para o inteiro seguinte e floor desce para o inteiro anterior.")
