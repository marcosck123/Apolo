"""Programação intermediária em Python: estruturas de dados, funções avançadas, erros, arquivos,
orientação a objetos e algoritmos clássicos."""
from lib import exemplo, exercicio, qa, licao, lista_py, NOMES, FRUTAS, PRODUTOS, CIDADES, ANIMAIS, CORES, PALAVRAS, PALINDROMOS


def licoes():
    b = []

    # ---------- tuplas ----------
    b.append(licao(
        "Tuplas",
        "Uma tupla é parecida com uma lista, mas não pode ser alterada depois de criada.",
        "Ela é escrita com parênteses: (1, 2, 3).",
        "Tuplas são boas para dados que andam juntos e não mudam, como uma coordenada (x, y).",
        "Desempacotar é tirar os valores da tupla para variáveis separadas numa linha só.",
    ))
    b.append(exemplo("Como criar e usar uma tupla?", "ponto = (3, 7)\nprint(ponto[0])\nprint(ponto[1])\nprint(len(ponto))",
                     "Os itens da tupla são acessados por índice, igual na lista."))
    b.append(exemplo("Uma tupla pode ser alterada?", "ponto = (3, 7)\nponto[0] = 10",
                     "Não. Tentar mudar um item dá TypeError, porque tuplas são imutáveis.", erro_esperado=True))
    b.append(exemplo("O que é desempacotar uma tupla?", 'pessoa = ("Ana", 20, "Vilhena")\nnome, idade, cidade = pessoa\nprint(nome)\nprint(idade)\nprint(cidade)',
                     "Cada variável da esquerda recebe um item da tupla, na ordem."))
    b.append(exemplo("Uma função pode devolver dois valores?", "def min_max(numeros):\n    return min(numeros), max(numeros)\nmenor, maior = min_max([4, 9, 1, 7])\nprint(menor, maior)",
                     "Sim. Ela devolve uma tupla, que é desempacotada em duas variáveis."))

    # ---------- dicionários ----------
    b.append(licao(
        "Dicionários",
        "Um dicionário guarda pares de chave e valor, dentro de chaves.",
        "Em vez de acessar pela posição, como na lista, acessamos pela chave.",
        "As chaves não se repetem. Se você atribuir de novo a mesma chave, o valor é substituído.",
        "Dicionários são ótimos para representar uma coisa com vários dados, como uma pessoa com nome, idade e cidade.",
    ))
    b.append(exemplo("Como criar um dicionário e pegar um valor?", 'aluno = {"nome": "Bia", "idade": 19, "curso": "Computação"}\nprint(aluno["nome"])\nprint(aluno["idade"])',
                     "aluno[\"nome\"] busca o valor guardado na chave nome."))
    b.append(exemplo("Como adicionar ou mudar um valor num dicionário?", 'estoque = {"maçã": 10}\nestoque["banana"] = 5\nestoque["maçã"] = 8\nprint(estoque)',
                     "Atribuir a uma chave nova cria a chave. Atribuir a uma chave que já existe troca o valor."))
    b.append(exemplo("O que acontece se a chave não existir?", 'precos = {"pão": 1.2}\nprint(precos["leite"])',
                     "Dá KeyError, porque a chave leite não existe no dicionário.", erro_esperado=True))
    b.append(exemplo("Como buscar uma chave sem dar erro?", 'precos = {"pão": 1.2}\nprint(precos.get("leite"))\nprint(precos.get("leite", 0))\nprint("pão" in precos)',
                     "get devolve None, ou o valor padrão que você passar, quando a chave não existe. O in verifica se a chave existe."))
    b.append(exemplo("Como remover uma chave de um dicionário?", 'carro = {"marca": "Fiat", "ano": 2015, "cor": "prata"}\ndel carro["cor"]\nano = carro.pop("ano")\nprint(carro)\nprint(ano)',
                     "del apaga a chave. pop apaga e devolve o valor que estava nela."))
    b.append(exemplo("Como percorrer um dicionário?", 'idades = {"Ana": 20, "Caio": 31, "Lia": 25}\nfor nome in idades:\n    print(nome)\nfor nome, idade in idades.items():\n    print(f"{nome} tem {idade} anos")',
                     "Percorrer o dicionário direto passa pelas chaves. Com items, cada volta recebe a chave e o valor juntos."))
    b.append(exemplo("Como ver só as chaves ou só os valores?", 'notas = {"mat": 8, "port": 7, "hist": 9}\nprint(list(notas.keys()))\nprint(list(notas.values()))\nprint(sum(notas.values()))',
                     "keys devolve as chaves e values devolve os valores. list transforma o resultado numa lista para mostrar."))
    b.append(exemplo("Como contar quantas vezes cada palavra aparece?", 'texto = "o gato e o rato e o cão"\ncontagem = {}\nfor palavra in texto.split():\n    contagem[palavra] = contagem.get(palavra, 0) + 1\nprint(contagem)',
                     "Para cada palavra, get pega a contagem atual, ou 0 se for a primeira vez, e soma 1. Esse padrão de contagem é muito usado."))
    b.append(exemplo("Como guardar uma lista de dicionários?", 'alunos = [\n    {"nome": "Ana", "nota": 8},\n    {"nome": "Rui", "nota": 6},\n    {"nome": "Lia", "nota": 9},\n]\nfor a in alunos:\n    if a["nota"] >= 7:\n        print(a["nome"], "aprovado")',
                     "Cada item da lista é um dicionário. Esse formato parece muito com uma tabela de banco de dados ou com dados em JSON."))
    b.append(exemplo("Como juntar dois dicionários?", 'padrao = {"tema": "claro", "idioma": "pt"}\nescolhido = {"tema": "escuro"}\nfinal = {**padrao, **escolhido}\nprint(final)\npadrao.update(escolhido)\nprint(padrao)',
                     "{**a, **b} cria um dicionário novo e, quando a chave se repete, o valor de b ganha. update faz o mesmo mudando o próprio dicionário."))

    # ---------- conjuntos ----------
    b.append(licao(
        "Conjuntos",
        "Um conjunto, set em inglês, guarda valores sem repetir e sem ordem.",
        "Ele é escrito com chaves, como {1, 2, 3}, mas sem pares de chave e valor.",
        "Conjuntos servem para remover repetidos e para operações como união e interseção.",
        "Um conjunto vazio se cria com set(), porque {} cria um dicionário vazio.",
    ))
    b.append(exemplo("Como remover itens repetidos de uma lista?", "numeros = [3, 1, 3, 2, 1, 3]\nunicos = set(numeros)\nprint(unicos)\nprint(sorted(unicos))\nprint(len(unicos))",
                     "O set guarda cada valor uma vez só. sorted devolve os valores em ordem numa lista."))
    b.append(exemplo("Como fazer união, interseção e diferença?", "a = {1, 2, 3, 4}\nb = {3, 4, 5}\nprint(a | b)\nprint(a & b)\nprint(a - b)",
                     "| é a união, com tudo dos dois. & é a interseção, só o que está nos dois. a - b é o que está em a mas não em b."))
    b.append(exemplo("Como descobrir quais amigos duas pessoas têm em comum?", 'amigos_ana = {"Caio", "Lia", "Rui", "Bia"}\namigos_rui = {"Lia", "Bia", "Téo"}\ncomuns = amigos_ana & amigos_rui\nprint(sorted(comuns))',
                     "A interseção mostra quem aparece nos dois conjuntos."))

    # ---------- comprehensions ----------
    b.append(licao(
        "List comprehension",
        "List comprehension é um jeito curto de criar uma lista a partir de outra.",
        "A forma é [expressão for item in sequência].",
        "Dá para filtrar com if no final: [expressão for item in sequência if condição].",
        "Ela faz o mesmo que um for com append, mas numa linha só.",
    ))
    b.append(exemplo("Como criar uma lista com os quadrados de 1 a 5?", "quadrados = [n ** 2 for n in range(1, 6)]\nprint(quadrados)",
                     "Para cada n de 1 a 5, a comprehension calcula n ao quadrado e coloca na lista."))
    b.append(exemplo("List comprehension faz o mesmo que um for?", "com_for = []\nfor n in range(5):\n    com_for.append(n * 10)\ncom_comprehension = [n * 10 for n in range(5)]\nprint(com_for)\nprint(com_comprehension)\nprint(com_for == com_comprehension)",
                     "Sim, o resultado é igual. A comprehension só é mais curta."))
    b.append(exemplo("Como filtrar uma lista com comprehension?", "numeros = [5, 12, 7, 20, 3, 16]\ngrandes = [n for n in numeros if n > 10]\nprint(grandes)",
                     "O if no final deixa passar só os números maiores que 10."))
    b.append(exemplo("Como transformar uma lista de palavras?", 'nomes = ["ana", "caio", "lia"]\nprint([n.capitalize() for n in nomes])\nprint([len(n) for n in nomes])',
                     "A expressão da frente pode ser qualquer coisa, como um método ou uma função."))
    b.append(exemplo("O que é dict comprehension?", 'palavras = ["sol", "lua", "estrela"]\ntamanhos = {p: len(p) for p in palavras}\nprint(tamanhos)',
                     "É o mesmo que list comprehension, mas cria um dicionário com chave: valor."))
    b.append(exemplo("Como inverter as chaves e valores de um dicionário?", 'codigos = {"BR": "Brasil", "ES": "Espanha"}\ninvertido = {v: k for k, v in codigos.items()}\nprint(invertido)',
                     "A comprehension percorre os pares e troca a posição de cada um."))

    # ---------- listas aninhadas ----------
    b.append(licao(
        "Listas dentro de listas",
        "Uma lista pode ter outras listas dentro. Isso serve para representar tabelas e matrizes.",
        "matriz[linha][coluna] pega um valor: o primeiro índice escolhe a linha e o segundo escolhe a coluna.",
    ))
    b.append(exemplo("Como acessar um valor de uma matriz?", "matriz = [\n    [1, 2, 3],\n    [4, 5, 6],\n    [7, 8, 9],\n]\nprint(matriz[0])\nprint(matriz[1][2])\nprint(matriz[2][0])",
                     "matriz[1] é a segunda linha, [4, 5, 6]. Dentro dela, o índice 2 é o 6."))
    b.append(exemplo("Como percorrer uma matriz?", 'matriz = [[1, 2], [3, 4], [5, 6]]\nfor linha in matriz:\n    for valor in linha:\n        print(valor, end=" ")\n    print()',
                     "O for de fora passa pelas linhas e o for de dentro passa pelos valores de cada linha. O print() vazio pula para a próxima linha."))
    b.append(exemplo("Como somar todos os valores de uma matriz?", "matriz = [[1, 2, 3], [4, 5, 6]]\ntotal = sum(sum(linha) for linha in matriz)\nprint(total)",
                     "Somamos cada linha e depois somamos os resultados: 6 + 15 dá 21."))

    # ---------- enumerate e zip ----------
    b.append(licao(
        "enumerate e zip",
        "enumerate dá o índice e o item ao mesmo tempo dentro de um for.",
        "zip anda por duas ou mais listas juntas, pegando um item de cada.",
    ))
    b.append(exemplo("Como pegar o índice e o item num for?", 'tarefas = ["estudar", "treinar", "dormir"]\nfor i, tarefa in enumerate(tarefas, start=1):\n    print(f"{i}. {tarefa}")',
                     "enumerate entrega o número e o item. Com start=1, a contagem começa em 1."))
    b.append(exemplo("Como percorrer duas listas ao mesmo tempo?", 'nomes = ["Ana", "Rui", "Lia"]\nnotas = [8, 6, 9]\nfor nome, nota in zip(nomes, notas):\n    print(nome, nota)\nprint(dict(zip(nomes, notas)))',
                     "zip junta o primeiro nome com a primeira nota, o segundo com a segunda, e assim por diante. dict(zip(...)) cria um dicionário direto."))

    # ---------- funções avançadas ----------
    b.append(licao(
        "Argumentos variáveis",
        "*args deixa a função receber quantos argumentos quiser. Dentro dela, args é uma tupla.",
        "**kwargs recebe argumentos com nome. Dentro da função, kwargs é um dicionário.",
        "Os nomes args e kwargs são só costume. O que importa são os asteriscos.",
    ))
    b.append(exemplo("Como fazer uma função que soma qualquer quantidade de números?", "def somar(*numeros):\n    total = 0\n    for n in numeros:\n        total += n\n    return total\nprint(somar(1, 2))\nprint(somar(1, 2, 3, 4))\nprint(somar())",
                     "O asterisco junta todos os argumentos numa tupla chamada numeros."))
    b.append(exemplo("Para que serve **kwargs?", 'def ficha(**dados):\n    for chave, valor in dados.items():\n        print(f"{chave}: {valor}")\nficha(nome="Apolo", tipo="IA", versao=1)',
                     "Os argumentos com nome viram um dicionário."))
    b.append(exemplo("Como passar uma lista como vários argumentos?", "def area(largura, altura):\n    return largura * altura\nmedidas = [4, 5]\nprint(area(*medidas))",
                     "O asterisco na chamada espalha a lista: area(*medidas) é o mesmo que area(4, 5)."))
    b.append(licao(
        "Funções lambda",
        "lambda cria uma função pequena, sem nome, numa linha só.",
        "A forma é lambda parâmetros: expressão. O resultado da expressão é devolvido automaticamente.",
        "Ela é muito usada como argumento de outras funções, como sorted, map e filter.",
    ))
    b.append(exemplo("Como criar uma função com lambda?", "dobro = lambda x: x * 2\nsoma = lambda a, b: a + b\nprint(dobro(6))\nprint(soma(3, 4))",
                     "lambda x: x * 2 é o mesmo que uma função que recebe x e devolve x * 2."))
    b.append(exemplo("Como ordenar uma lista por um critério?", 'palavras = ["banana", "uva", "abacaxi", "kiwi"]\nprint(sorted(palavras))\nprint(sorted(palavras, key=len))\nprint(sorted(palavras, key=len, reverse=True))',
                     "Sem key, a ordem é alfabética. Com key=len, a ordem é pelo tamanho da palavra."))
    b.append(exemplo("Como ordenar uma lista de dicionários?", 'pessoas = [{"nome": "Ana", "idade": 31}, {"nome": "Caio", "idade": 19}, {"nome": "Lia", "idade": 25}]\nfor p in sorted(pessoas, key=lambda p: p["idade"]):\n    print(p["nome"], p["idade"])',
                     "A lambda diz qual valor usar para comparar: a idade de cada pessoa."))
    b.append(exemplo("Para que servem map e filter?", "numeros = [1, 2, 3, 4, 5, 6]\nprint(list(map(lambda n: n * 10, numeros)))\nprint(list(filter(lambda n: n % 2 == 0, numeros)))",
                     "map aplica uma função a cada item. filter mantém só os itens em que a função devolve True. As duas devolvem iteradores, então usamos list para ver o resultado."))
    b.append(exemplo("Para que servem any e all?", "notas = [7, 8, 5, 9]\nprint(any(n < 6 for n in notas))\nprint(all(n >= 5 for n in notas))",
                     "any devolve True se pelo menos um item passar no teste. all devolve True só se todos passarem."))
    b.append(exemplo("Uma função pode receber outra função?", 'def aplicar(funcao, valor):\n    return funcao(valor)\ndef gritar(texto):\n    return texto.upper() + "!"\nprint(aplicar(gritar, "oi"))\nprint(aplicar(len, "oi"))',
                     "Sim. Em Python, funções são valores e podem ser passadas como argumento. Repare que gritar vai sem parênteses, porque estamos passando a função e não chamando ela."))
    b.append(exemplo("Uma função pode criar outra função?", "def multiplicador(k):\n    def multiplicar(x):\n        return x * k\n    return multiplicar\ntriplo = multiplicador(3)\nprint(triplo(5))\nprint(multiplicador(10)(2))",
                     "multiplicador devolve uma função nova que lembra o valor de k. Isso se chama closure."))

    # ---------- recursão ----------
    b.append(licao(
        "Recursão",
        "Uma função recursiva é uma função que chama a si mesma.",
        "Toda recursão precisa de um caso base, que é quando a função para de se chamar.",
        "Sem caso base, a função se chama para sempre e o Python dá RecursionError.",
        "Cada chamada resolve um pedaço menor do problema.",
    ))
    b.append(exemplo("Como calcular o fatorial com recursão?", "def fatorial(n):\n    if n <= 1:\n        return 1\n    return n * fatorial(n - 1)\nprint(fatorial(5))",
                     "fatorial(5) é 5 * fatorial(4), que é 4 * fatorial(3), e assim até fatorial(1), o caso base, que devolve 1. O resultado é 5 x 4 x 3 x 2 x 1 = 120."))
    b.append(exemplo("Como calcular Fibonacci com recursão?", "def fib(n):\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)\nprint([fib(i) for i in range(10)])",
                     "Cada número de Fibonacci é a soma dos dois anteriores. Os casos base são fib(0) = 0 e fib(1) = 1."))
    b.append(exemplo("Como somar uma lista com recursão?", "def soma(lista):\n    if not lista:\n        return 0\n    return lista[0] + soma(lista[1:])\nprint(soma([3, 5, 2, 10]))",
                     "A soma é o primeiro item mais a soma do resto. Quando a lista fica vazia, a soma é 0."))
    b.append(exemplo("O que acontece com uma recursão sem caso base?", "def infinita(n):\n    return infinita(n + 1)\ninfinita(0)",
                     "Dá RecursionError, porque a função nunca para de se chamar.", erro_esperado=True))
    b.append(exemplo("Como deixar o Fibonacci recursivo rápido?", "from functools import lru_cache\n@lru_cache\ndef fib(n):\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)\nprint(fib(80))",
                     "O fib recursivo simples calcula os mesmos valores muitas vezes. lru_cache guarda os resultados já calculados, então cada valor é calculado uma vez só. Essa técnica se chama memoização."))

    # ---------- exceções ----------
    b.append(licao(
        "Tratando erros com try e except",
        "Quando um erro acontece, o programa para. Com try e except, podemos tratar o erro e continuar.",
        "O código que pode dar erro fica no try. O que fazer se der erro fica no except.",
        "É melhor dizer qual erro você espera, como except ValueError, do que pegar todos os erros.",
        "else roda quando não houve erro. finally roda sempre, com ou sem erro.",
        "raise é usado para lançar um erro de propósito, quando algo está errado.",
    ))
    b.append(exemplo("Como evitar que o programa pare com um erro?", 'texto = "abc"\ntry:\n    numero = int(texto)\n    print(numero)\nexcept ValueError:\n    print("Isso não é um número.")\nprint("O programa continua.")',
                     "int(\"abc\") deu ValueError, o except tratou o erro e o programa seguiu."))
    b.append(exemplo("Como pedir um número até o usuário digitar certo?", 'while True:\n    try:\n        idade = int(input("Idade: "))\n        break\n    except ValueError:\n        print("Digite só números.")\nprint(f"Idade registrada: {idade}")',
                     "Quando a conversão falha, o except avisa e o laço pergunta de novo. Quando funciona, o break sai do laço.", entradas=["vinte", "20"]))
    b.append(exemplo("Como tratar erros diferentes?", 'def dividir(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return "divisão por zero"\n    except TypeError:\n        return "tipos inválidos"\nprint(dividir(10, 2))\nprint(dividir(10, 0))\nprint(dividir(10, "x"))',
                     "Cada except trata um tipo de erro diferente."))
    b.append(exemplo("Para que servem else e finally?", 'def ler(valor):\n    try:\n        n = int(valor)\n    except ValueError:\n        print("falhou")\n    else:\n        print("deu certo:", n)\n    finally:\n        print("fim da tentativa")\nler("5")\nler("x")',
                     "else só rodou quando não teve erro. finally rodou nas duas vezes."))
    b.append(exemplo("Como ver a mensagem do erro?", 'try:\n    lista = [1, 2]\n    lista[10]\nexcept IndexError as erro:\n    print("Aconteceu:", erro)',
                     "except Tipo as erro guarda o erro numa variável, e assim dá para mostrar a mensagem."))
    b.append(exemplo("Como lançar um erro de propósito?", 'def sacar(saldo, valor):\n    if valor > saldo:\n        raise ValueError("saldo insuficiente")\n    return saldo - valor\nprint(sacar(100, 30))\ntry:\n    sacar(100, 500)\nexcept ValueError as e:\n    print("Erro:", e)',
                     "raise interrompe a função com um erro. Quem chamou pode tratar com try e except."))

    # ---------- arquivos ----------
    b.append(licao(
        "Arquivos",
        "open abre um arquivo. O segundo argumento é o modo: \"r\" para ler, \"w\" para escrever do zero e \"a\" para acrescentar no final.",
        "O jeito recomendado é usar with open(...) as f. O with fecha o arquivo sozinho no final do bloco.",
        "Para textos em português, use encoding=\"utf-8\" para os acentos funcionarem.",
        "O modo \"w\" apaga o que já existia no arquivo.",
    ))
    b.append(exemplo("Como escrever e ler um arquivo de texto?", 'with open("notas.txt", "w", encoding="utf-8") as f:\n    f.write("Primeira linha\\n")\n    f.write("Segunda linha\\n")\nwith open("notas.txt", "r", encoding="utf-8") as f:\n    conteudo = f.read()\nprint(conteudo)',
                     "O \\n no write é o que pula linha dentro do arquivo. read lê o arquivo inteiro como uma string."))
    b.append(exemplo("Como ler um arquivo linha por linha?", 'with open("frutas.txt", "w", encoding="utf-8") as f:\n    f.write("maçã\\nbanana\\nuva\\n")\nwith open("frutas.txt", encoding="utf-8") as f:\n    for numero, linha in enumerate(f, start=1):\n        print(numero, linha.strip())',
                     "Percorrer o arquivo com for entrega uma linha por vez. strip tira o \\n do final de cada linha."))
    b.append(exemplo("Como acrescentar texto num arquivo sem apagar o que tinha?", 'with open("log.txt", "w", encoding="utf-8") as f:\n    f.write("início\\n")\nwith open("log.txt", "a", encoding="utf-8") as f:\n    f.write("evento 1\\n")\n    f.write("evento 2\\n")\nwith open("log.txt", encoding="utf-8") as f:\n    print(f.read().strip())',
                     "O modo \"a\" escreve no final do arquivo e mantém o que já estava lá."))
    b.append(exemplo("O que acontece ao abrir um arquivo que não existe?", 'with open("nao_existe.txt") as f:\n    print(f.read())',
                     "Dá FileNotFoundError. Dá para tratar com try e except FileNotFoundError.", erro_esperado=True))
    b.append(exemplo("Como salvar e ler dados em JSON?", 'import json\naluno = {"nome": "Ana", "notas": [8, 9, 7], "ativo": True}\nwith open("aluno.json", "w", encoding="utf-8") as f:\n    json.dump(aluno, f, ensure_ascii=False)\nwith open("aluno.json", encoding="utf-8") as f:\n    lido = json.load(f)\nprint(lido["nome"], sum(lido["notas"]))\nprint(json.dumps(aluno, ensure_ascii=False))',
                     "json.dump salva um dicionário num arquivo e json.load lê de volta. json.dumps transforma em string. Repare que True do Python vira true no JSON."))
    b.append(exemplo("Como ler um arquivo CSV?", 'import csv\nwith open("produtos.csv", "w", encoding="utf-8", newline="") as f:\n    f.write("nome,preco\\narroz,25.9\\ncafé,18.0\\n")\nwith open("produtos.csv", encoding="utf-8") as f:\n    for linha in csv.DictReader(f):\n        print(linha["nome"], float(linha["preco"]))',
                     "CSV é um arquivo de texto com valores separados por vírgula. csv.DictReader transforma cada linha num dicionário usando a primeira linha como nomes das colunas."))

    # ---------- módulos ----------
    b.append(licao(
        "Módulos",
        "Um módulo é um arquivo Python com funções e variáveis que podem ser usadas em outro programa.",
        "import traz um módulo. from módulo import nome traz só uma parte dele.",
        "Python já vem com muitos módulos prontos, como math, random, json, csv e datetime. Isso se chama biblioteca padrão.",
        "Pacotes de fora são instalados com pip, como pip install requests.",
        "Qualquer arquivo .py que você cria também é um módulo. Se você tem utils.py, pode escrever import utils.",
    ))
    b.append(exemplo("Como usar o módulo math?", "import math\nprint(math.sqrt(16))\nprint(math.pi)\nprint(math.ceil(4.2))\nprint(math.floor(4.8))",
                     "sqrt é raiz quadrada. ceil arredonda para cima e floor arredonda para baixo."))
    b.append(exemplo("Como sortear números com random?", "import random\nrandom.seed(42)\nprint(random.randint(1, 6))\nprint(random.choice([\"pedra\", \"papel\", \"tesoura\"]))\nlista = [1, 2, 3, 4, 5]\nrandom.shuffle(lista)\nprint(lista)",
                     "randint sorteia um inteiro, choice sorteia um item e shuffle embaralha a lista. random.seed fixa o sorteio, então o resultado se repete toda vez que o programa roda. Isso é útil para testes."))
    b.append(exemplo("Como importar só uma função de um módulo?", "from math import sqrt, pi\nprint(sqrt(25))\nprint(round(pi, 3))",
                     "Com from math import sqrt, usamos sqrt direto, sem escrever math. na frente."))
    b.append(exemplo("Como trabalhar com datas?", "from datetime import date, timedelta\ninicio = date(2026, 10, 23)\nprint(inicio)\nprint(inicio + timedelta(days=10))\nprint(inicio.strftime(\"%d/%m/%Y\"))\nprint((date(2026, 12, 25) - inicio).days)",
                     "date cria uma data, timedelta representa um intervalo de tempo e strftime formata a data como texto. Subtrair duas datas dá a diferença em dias."))
    b.append(exemplo("Para que serve if __name__ == \"__main__\"?", 'def principal():\n    print("rodando o programa")\nif __name__ == "__main__":\n    principal()',
                     "Esse if só é verdadeiro quando o arquivo é executado direto. Se o arquivo for importado por outro, a função principal não roda sozinha."))

    # ---------- orientação a objetos ----------
    b.append(licao(
        "Classes e objetos",
        "Uma classe é um molde. Um objeto é uma coisa criada a partir do molde.",
        "Por exemplo, Cachorro é uma classe, e o cachorro Rex é um objeto dessa classe.",
        "Atributos são os dados do objeto, como nome e idade.",
        "Métodos são as funções do objeto, como latir.",
        "__init__ é o método que roda quando o objeto é criado. Ele prepara os atributos.",
        "self é o próprio objeto. Todo método recebe self como primeiro parâmetro.",
        "Juntar dados e comportamentos no mesmo lugar é a ideia da programação orientada a objetos.",
    ))
    b.append(exemplo("Como criar uma classe?", 'class Cachorro:\n    def __init__(self, nome, idade):\n        self.nome = nome\n        self.idade = idade\n    def latir(self):\n        return f"{self.nome} diz: au au!"\nrex = Cachorro("Rex", 3)\nprint(rex.nome)\nprint(rex.idade)\nprint(rex.latir())',
                     "Cachorro(\"Rex\", 3) cria um objeto e chama o __init__. Dentro dos métodos, self.nome é o nome daquele cachorro."))
    b.append(exemplo("Dois objetos da mesma classe são independentes?", 'class Contador:\n    def __init__(self):\n        self.valor = 0\n    def incrementar(self):\n        self.valor += 1\na = Contador()\nb = Contador()\na.incrementar()\na.incrementar()\nb.incrementar()\nprint(a.valor, b.valor)',
                     "Sim. Cada objeto tem seus próprios atributos. Mexer em a não muda b."))
    b.append(exemplo("Como fazer uma conta bancária com classe?", 'class Conta:\n    def __init__(self, titular, saldo=0):\n        self.titular = titular\n        self.saldo = saldo\n    def depositar(self, valor):\n        if valor <= 0:\n            raise ValueError("depósito precisa ser positivo")\n        self.saldo += valor\n    def sacar(self, valor):\n        if valor > self.saldo:\n            raise ValueError("saldo insuficiente")\n        self.saldo -= valor\nconta = Conta("Marcos")\nconta.depositar(200)\nconta.sacar(50)\nprint(conta.titular, conta.saldo)\ntry:\n    conta.sacar(1000)\nexcept ValueError as e:\n    print("Erro:", e)',
                     "Os métodos garantem as regras da conta: não dá para depositar valor negativo nem sacar mais do que o saldo."))
    b.append(exemplo("Para que serve o método __str__?", 'class Produto:\n    def __init__(self, nome, preco):\n        self.nome = nome\n        self.preco = preco\n    def __str__(self):\n        return f"{self.nome} (R$ {self.preco:.2f})"\np = Produto("café", 18)\nprint(p)',
                     "__str__ define como o objeto aparece no print. Sem ele, o print mostraria algo como <__main__.Produto object at 0x...>."))
    b.append(licao(
        "Herança",
        "Herança é quando uma classe aproveita tudo de outra classe e acrescenta ou muda alguma coisa.",
        "A classe de cima se chama classe mãe, ou superclasse. A de baixo se chama classe filha, ou subclasse.",
        "super() chama um método da classe mãe.",
        "Quando a filha escreve um método com o mesmo nome da mãe, ela substitui o comportamento. Isso se chama sobrescrever.",
    ))
    b.append(exemplo("Como uma classe herda de outra?", 'class Animal:\n    def __init__(self, nome):\n        self.nome = nome\n    def falar(self):\n        return "..."\n    def apresentar(self):\n        return f"{self.nome}: {self.falar()}"\nclass Gato(Animal):\n    def falar(self):\n        return "miau"\nclass Pato(Animal):\n    def falar(self):\n        return "quack"\nfor bicho in [Gato("Mimi"), Pato("Donaldo"), Animal("Coisa")]:\n    print(bicho.apresentar())',
                     "Gato e Pato herdaram __init__ e apresentar de Animal e só trocaram o falar. Cada objeto usa a sua própria versão de falar. Isso se chama polimorfismo."))
    b.append(exemplo("Para que serve o super()?", 'class Funcionario:\n    def __init__(self, nome, salario):\n        self.nome = nome\n        self.salario = salario\nclass Gerente(Funcionario):\n    def __init__(self, nome, salario, equipe):\n        super().__init__(nome, salario)\n        self.equipe = equipe\ng = Gerente("Carla", 9000, ["Rui", "Lia"])\nprint(g.nome, g.salario, len(g.equipe))',
                     "super().__init__ reaproveita o __init__ da classe mãe para nome e salario, e o Gerente só acrescenta a equipe."))
    b.append(exemplo("Como saber se um objeto é de uma classe?", 'class Veiculo:\n    pass\nclass Carro(Veiculo):\n    pass\nc = Carro()\nprint(isinstance(c, Carro))\nprint(isinstance(c, Veiculo))\nprint(isinstance(c, str))',
                     "isinstance devolve True se o objeto é daquela classe ou de uma filha dela. pass é um comando que não faz nada, usado quando o bloco precisa existir mas está vazio."))
    b.append(exemplo("O que é um atributo de classe?", "class Robo:\n    total = 0\n    def __init__(self, nome):\n        self.nome = nome\n        Robo.total += 1\nRobo(\"R1\")\nRobo(\"R2\")\nRobo(\"R3\")\nprint(Robo.total)",
                     "total pertence à classe, não a cada objeto. Todos os robôs compartilham o mesmo contador."))
    b.append(exemplo("O que é uma property?", 'class Retangulo:\n    def __init__(self, largura, altura):\n        self.largura = largura\n        self.altura = altura\n    @property\n    def area(self):\n        return self.largura * self.altura\nr = Retangulo(3, 4)\nprint(r.area)\nr.largura = 10\nprint(r.area)',
                     "@property faz um método ser lido como atributo, sem parênteses. A área é sempre calculada na hora, então acompanha a mudança na largura."))
    b.append(exemplo("O que é uma dataclass?", 'from dataclasses import dataclass\n@dataclass\nclass Ponto:\n    x: int\n    y: int\np = Ponto(2, 5)\nprint(p)\nprint(p.x + p.y)\nprint(p == Ponto(2, 5))',
                     "@dataclass cria o __init__, o jeito de mostrar e a comparação automaticamente a partir dos campos. É útil para classes que só guardam dados."))
    b.append(licao(
        "Encapsulamento",
        "Encapsular é esconder os detalhes de dentro do objeto e oferecer métodos para usá-lo.",
        "Em Python, um nome começando com sublinhado, como self._saldo, indica que é de uso interno e não deve ser mexido de fora.",
        "Isso é uma combinação entre programadores. O Python não proíbe o acesso, mas avisa pela convenção.",
    ))

    # ---------- iteradores e geradores ----------
    b.append(licao(
        "Geradores",
        "Um gerador é uma função que usa yield em vez de return.",
        "A cada yield, ela entrega um valor e pausa. Na próxima vez, continua de onde parou.",
        "Geradores produzem valores um de cada vez, sem guardar tudo na memória. Isso é bom para sequências grandes.",
    ))
    b.append(exemplo("Como criar um gerador?", "def contar_ate(n):\n    i = 1\n    while i <= n:\n        yield i\n        i += 1\nfor numero in contar_ate(4):\n    print(numero)\nprint(list(contar_ate(3)))",
                     "Cada yield entrega um número para o for. list junta todos os valores do gerador numa lista."))
    b.append(exemplo("Como usar next com um gerador?", "def cores():\n    yield \"vermelho\"\n    yield \"verde\"\n    yield \"azul\"\ng = cores()\nprint(next(g))\nprint(next(g))\nprint(next(g))",
                     "next pede o próximo valor. O gerador pausa entre um yield e outro."))
    b.append(exemplo("O que é uma expressão geradora?", "quadrados = (n * n for n in range(1, 1000001))\nprint(sum(quadrados))",
                     "Parece uma list comprehension, mas com parênteses. Ela calcula os valores conforme o sum pede, sem criar uma lista de um milhão de itens na memória."))

    # ---------- formatação ----------
    b.append(exemplo("Como alinhar texto numa tabela?", 'itens = [("arroz", 25.9), ("café", 18.0), ("pão", 1.2)]\nfor nome, preco in itens:\n    print(f"{nome:<10}{preco:>8.2f}")',
                     ":<10 alinha à esquerda ocupando 10 espaços. :>8.2f alinha à direita em 8 espaços com duas casas decimais."))
    b.append(exemplo("Como mostrar números grandes e porcentagens?", 'populacao = 1234567\ntaxa = 0.1875\nprint(f"{populacao:,}")\nprint(f"{taxa:.1%}")\nprint(f"{7:03d}")',
                     ":, separa os milhares, :.1% mostra como porcentagem com uma casa e :03d completa com zeros à esquerda."))

    # ---------- tipos ----------
    b.append(licao(
        "Dicas de tipo",
        "Dá para anotar os tipos esperados de parâmetros e do retorno: def somar(a: int, b: int) -> int.",
        "O Python não obriga os tipos na hora de rodar. As anotações servem para documentar e para ferramentas como o mypy acharem erros antes.",
    ))
    b.append(exemplo("Como escrever dicas de tipo?", 'def media(notas: list[float]) -> float:\n    return sum(notas) / len(notas)\ndef saudacao(nome: str, vezes: int = 1) -> str:\n    return ("Olá, " + nome + "! ") * vezes\nprint(media([7.0, 8.5, 9.0]))\nprint(saudacao("Apolo", 2).strip())',
                     "list[float] quer dizer lista de floats e -> float indica o tipo do retorno."))

    # ---------- testes ----------
    b.append(licao(
        "Testes",
        "Testar é verificar automaticamente se o código faz o que deveria.",
        "assert verifica uma condição. Se ela for falsa, o programa para com AssertionError.",
        "Bons testes cobrem o caso comum, os casos de borda, como lista vazia e zero, e os casos de erro.",
        "Em projetos maiores, usamos bibliotecas como pytest para organizar e rodar os testes.",
    ))
    b.append(exemplo("Como testar uma função com assert?", 'def eh_palindromo(texto):\n    limpo = texto.lower().replace(" ", "")\n    return limpo == limpo[::-1]\nassert eh_palindromo("arara")\nassert eh_palindromo("Socorram me subi no onibus em Marrocos")\nassert not eh_palindromo("python")\nassert eh_palindromo("")\nprint("todos os testes passaram")',
                     "Cada assert confere um caso. Como nenhum falhou, a mensagem final apareceu."))
    b.append(exemplo("O que acontece quando um assert falha?", 'def dobro(x):\n    return x + 2\nassert dobro(2) == 4\nassert dobro(5) == 10, "dobro(5) deveria ser 10"',
                     "O primeiro assert passou por coincidência, porque 2 + 2 também dá 4. O segundo pegou o bug: a função soma 2 em vez de multiplicar por 2. Por isso é importante testar mais de um caso.", erro_esperado=True))

    # ---------- estruturas úteis ----------
    b.append(licao(
        "Pilhas e filas",
        "Uma pilha funciona como uma pilha de pratos: o último a entrar é o primeiro a sair.",
        "Uma fila funciona como uma fila de banco: o primeiro a entrar é o primeiro a sair.",
        "Uma lista serve bem como pilha, com append e pop.",
        "Para fila, o melhor é deque, do módulo collections, com append e popleft.",
    ))
    b.append(exemplo("Como usar uma lista como pilha?", 'pilha = []\npilha.append("a")\npilha.append("b")\npilha.append("c")\nprint(pilha.pop())\nprint(pilha.pop())\nprint(pilha)',
                     "O último a entrar, c, foi o primeiro a sair."))
    b.append(exemplo("Como fazer uma fila?", 'from collections import deque\nfila = deque()\nfila.append("Ana")\nfila.append("Rui")\nfila.append("Lia")\nprint(fila.popleft())\nprint(fila.popleft())\nprint(list(fila))',
                     "A primeira a chegar, Ana, foi a primeira a ser atendida."))
    b.append(exemplo("Como verificar se os parênteses de uma expressão estão balanceados?", 'def balanceado(texto):\n    pares = {")": "(", "]": "[", "}": "{"}\n    pilha = []\n    for c in texto:\n        if c in "([{":\n            pilha.append(c)\n        elif c in pares:\n            if not pilha or pilha.pop() != pares[c]:\n                return False\n    return not pilha\nprint(balanceado("(a + [b * c])"))\nprint(balanceado("(a + b]"))\nprint(balanceado("((x)"))',
                     "Cada abertura entra na pilha. Cada fechamento precisa casar com a última abertura. No final, a pilha tem que estar vazia."))
    b.append(exemplo("Como contar coisas com Counter?", 'from collections import Counter\nvotos = ["azul", "verde", "azul", "rosa", "azul", "verde"]\ncontagem = Counter(votos)\nprint(contagem)\nprint(contagem.most_common(1))\nprint(contagem["verde"])',
                     "Counter faz a contagem sozinho. most_common(1) devolve o item mais frequente com sua contagem."))
    b.append(exemplo("O que é um defaultdict?", 'from collections import defaultdict\npalavras = ["sol", "sal", "lua", "luz", "mar"]\npor_letra = defaultdict(list)\nfor p in palavras:\n    por_letra[p[0]].append(p)\nprint(dict(por_letra))',
                     "defaultdict(list) cria uma lista vazia sozinho quando a chave ainda não existe. Assim não precisamos testar se a chave existe antes do append."))

    # ---------- algoritmos ----------
    b.append(licao(
        "Algoritmos de busca",
        "Busca linear olha item por item, do começo ao fim. Funciona em qualquer lista.",
        "Busca binária só funciona em lista ordenada. Ela olha o meio e descarta metade da lista a cada passo.",
        "Numa lista com um milhão de itens, a busca linear pode precisar de um milhão de comparações, e a binária precisa de umas 20.",
    ))
    b.append(exemplo("Como fazer uma busca linear?", "def busca_linear(lista, alvo):\n    for i, valor in enumerate(lista):\n        if valor == alvo:\n            return i\n    return -1\nnumeros = [8, 3, 15, 4, 42]\nprint(busca_linear(numeros, 15))\nprint(busca_linear(numeros, 7))",
                     "Devolve a posição onde achou o alvo, ou -1 se ele não estiver na lista."))
    b.append(exemplo("Como fazer uma busca binária?", "def busca_binaria(lista, alvo):\n    inicio, fim = 0, len(lista) - 1\n    while inicio <= fim:\n        meio = (inicio + fim) // 2\n        if lista[meio] == alvo:\n            return meio\n        if lista[meio] < alvo:\n            inicio = meio + 1\n        else:\n            fim = meio - 1\n    return -1\nordenada = [1, 3, 5, 7, 9, 11, 13, 15]\nprint(busca_binaria(ordenada, 11))\nprint(busca_binaria(ordenada, 4))",
                     "Se o meio é menor que o alvo, o alvo só pode estar na metade da direita. Se é maior, só pode estar na da esquerda. A cada volta, metade da lista é descartada."))
    b.append(licao(
        "Algoritmos de ordenação",
        "Ordenar é colocar os itens em ordem.",
        "O bubble sort compara vizinhos e troca quando estão fora de ordem. É simples, mas lento para listas grandes.",
        "O selection sort procura o menor item e coloca na frente, depois o segundo menor, e assim por diante.",
        "Na prática, usamos sorted ou sort, que são muito mais rápidos. Escrever os algoritmos à mão serve para aprender a pensar.",
    ))
    b.append(exemplo("Como funciona o bubble sort?", "def bubble_sort(lista):\n    itens = lista.copy()\n    n = len(itens)\n    for i in range(n - 1):\n        for j in range(n - 1 - i):\n            if itens[j] > itens[j + 1]:\n                itens[j], itens[j + 1] = itens[j + 1], itens[j]\n    return itens\nprint(bubble_sort([5, 2, 9, 1, 6]))",
                     "A cada passada, o maior valor que ainda está fora do lugar vai sendo empurrado para o final, como uma bolha subindo."))
    b.append(exemplo("Como funciona o selection sort?", "def selection_sort(lista):\n    itens = lista.copy()\n    for i in range(len(itens)):\n        menor = i\n        for j in range(i + 1, len(itens)):\n            if itens[j] < itens[menor]:\n                menor = j\n        itens[i], itens[menor] = itens[menor], itens[i]\n    return itens\nprint(selection_sort([29, 10, 14, 37, 13]))",
                     "Para cada posição i, procura o menor item do resto da lista e troca com o da posição i."))
    b.append(exemplo("Como juntar duas listas ordenadas numa só?", "def juntar(a, b):\n    resultado = []\n    i = j = 0\n    while i < len(a) and j < len(b):\n        if a[i] <= b[j]:\n            resultado.append(a[i])\n            i += 1\n        else:\n            resultado.append(b[j])\n            j += 1\n    return resultado + a[i:] + b[j:]\nprint(juntar([1, 4, 9], [2, 3, 10, 12]))",
                     "Compara o primeiro de cada lista e pega o menor. Quando uma acaba, o resto da outra entra direto. Essa é a parte principal do merge sort."))
    b.append(exemplo("Como verificar se um número é primo?", "def eh_primo(n):\n    if n < 2:\n        return False\n    d = 2\n    while d * d <= n:\n        if n % d == 0:\n            return False\n        d += 1\n    return True\nprint([n for n in range(1, 40) if eh_primo(n)])",
                     "Um número primo só é divisível por 1 e por ele mesmo. Basta testar divisores até a raiz quadrada do número, porque se houver um divisor maior, haverá um menor par dele."))
    b.append(exemplo("Como calcular o MDC de dois números?", "def mdc(a, b):\n    while b != 0:\n        a, b = b, a % b\n    return a\nprint(mdc(48, 18))\nprint(mdc(17, 5))",
                     "Esse é o algoritmo de Euclides: troca o par (a, b) por (b, resto de a por b) até o resto ser zero. 48 e 18 viram 18 e 12, depois 12 e 6, depois 6 e 0. O MDC é 6."))
    b.append(exemplo("Como transformar um número em binário?", 'def para_binario(n):\n    if n == 0:\n        return "0"\n    digitos = ""\n    while n > 0:\n        digitos = str(n % 2) + digitos\n        n //= 2\n    return digitos\nprint(para_binario(13))\nprint(bin(13))\nprint(int("1101", 2))',
                     "Dividimos por 2 várias vezes e juntamos os restos de trás para frente. A função pronta bin faz o mesmo, e int(texto, 2) faz o caminho de volta."))
    b.append(exemplo("Como remover itens repetidos mantendo a ordem?", "def sem_repetidos(lista):\n    vistos = set()\n    resultado = []\n    for item in lista:\n        if item not in vistos:\n            vistos.add(item)\n            resultado.append(item)\n    return resultado\nprint(sem_repetidos([3, 1, 3, 2, 1, 5]))",
                     "O set lembra o que já apareceu, e a lista guarda a ordem da primeira aparição."))
    b.append(exemplo("Como achar dois números de uma lista que somam um alvo?", "def dois_somam(numeros, alvo):\n    vistos = {}\n    for i, n in enumerate(numeros):\n        falta = alvo - n\n        if falta in vistos:\n            return vistos[falta], i\n        vistos[n] = i\n    return None\nprint(dois_somam([2, 7, 11, 15], 9))\nprint(dois_somam([3, 5, 8], 100))",
                     "Para cada número, calculamos quanto falta para o alvo e procuramos no dicionário. Assim a lista é percorrida uma vez só."))
    b.append(licao(
        "Complexidade de algoritmos",
        "Complexidade mede como o tempo de um algoritmo cresce quando a entrada cresce.",
        "Ela é escrita com a notação O grande, em inglês Big O.",
        "O(1) é tempo constante: não depende do tamanho, como pegar lista[0] ou buscar uma chave num dicionário.",
        "O(log n) cresce bem devagar, como a busca binária.",
        "O(n) cresce junto com a entrada, como a busca linear ou somar uma lista.",
        "O(n log n) é o tempo dos bons algoritmos de ordenação, como o que o sorted usa.",
        "O(n**2) acontece com um laço dentro de outro sobre a mesma lista, como o bubble sort. Fica lento rápido.",
        "Buscar com in numa lista é O(n), mas num set ou dicionário é O(1) em média. Por isso trocar lista por set às vezes deixa o programa muito mais rápido.",
    ))

    # ---------- boas práticas ----------
    b.append(licao(
        "Boas práticas",
        "Escreva nomes que explicam: total_de_alunos é melhor que t.",
        "Cada função deve fazer uma coisa só, e fazer bem.",
        "Não repita código. Se você copiou o mesmo trecho três vezes, ele deveria virar uma função.",
        "Trate os erros que você espera e deixe os inesperados aparecerem, para não esconder bugs.",
        "Teste os casos de borda: lista vazia, zero, número negativo, texto vazio.",
        "Siga o guia de estilo do Python, chamado PEP 8: quatro espaços de indentação, nomes de variáveis e funções em minúsculas com sublinhado, e nomes de classes com a primeira letra maiúscula.",
        "Código é lido muito mais vezes do que é escrito. Escreva pensando em quem vai ler.",
    ))
    b.append(exemplo("Como deixar um código mais legível?", 'def calcular_total(precos, desconto_percentual=0):\n    subtotal = sum(precos)\n    desconto = subtotal * desconto_percentual / 100\n    return subtotal - desconto\ncarrinho = [10.0, 25.5, 4.5]\nprint(calcular_total(carrinho))\nprint(calcular_total(carrinho, desconto_percentual=10))',
                     "Os nomes dizem o que cada coisa é, cada linha faz um passo e o argumento com nome deixa claro o que o 10 significa."))
    b.append(exemplo("Como depurar um programa com print?", 'def media(notas):\n    total = 0\n    for n in notas:\n        total += n\n        print(f"depuração: n={n}, total={total}")\n    return total / len(notas)\nprint(media([6, 8, 10]))',
                     "Colocar prints temporários mostra o valor das variáveis a cada passo. Depois de achar o problema, os prints de depuração são removidos."))
    return b


def perguntas():
    return [
        qa("O que é uma tupla?", "Uma tupla é uma sequência ordenada que não pode ser alterada. Ela é escrita com parênteses."),
        qa("Qual a diferença entre lista e tupla?", "A lista pode ser alterada e usa colchetes. A tupla não pode ser alterada e usa parênteses."),
        qa("O que é desempacotar?", "Desempacotar é distribuir os itens de uma sequência em variáveis separadas, como a, b = (1, 2)."),
        qa("O que é um dicionário?", "Um dicionário guarda pares de chave e valor. Os valores são acessados pela chave."),
        qa("O que acontece ao acessar uma chave que não existe num dicionário?", "Dá KeyError. Para evitar, use o método get ou verifique com in."),
        qa("O que faz o método get de um dicionário?", "get devolve o valor da chave, ou None, ou um valor padrão, quando a chave não existe."),
        qa("O que faz o método items de um dicionário?", "items devolve os pares de chave e valor, muito usado num for."),
        qa("O que é um set?", "Um set é um conjunto: guarda valores sem repetição e sem ordem."),
        qa("Como remover repetidos de uma lista?", "Transformando em set com set(lista). Se a ordem importar, percorra a lista guardando os já vistos num set."),
        qa("O que é list comprehension?", "É uma forma curta de criar uma lista: [expressão for item in sequência if condição]."),
        qa("O que é dict comprehension?", "É uma forma curta de criar um dicionário: {chave: valor for item in sequência}."),
        qa("O que faz enumerate?", "enumerate entrega o índice e o item ao mesmo tempo num for."),
        qa("O que faz zip?", "zip percorre várias sequências juntas, pegando um item de cada vez de cada uma."),
        qa("O que é *args?", "*args faz a função receber qualquer quantidade de argumentos, que chegam como uma tupla."),
        qa("O que é **kwargs?", "**kwargs faz a função receber argumentos com nome, que chegam como um dicionário."),
        qa("O que é uma lambda?", "Uma lambda é uma função pequena e sem nome, escrita numa linha: lambda x: x * 2."),
        qa("O que faz o parâmetro key do sorted?", "key recebe uma função que diz qual valor usar para comparar os itens na ordenação."),
        qa("O que faz map?", "map aplica uma função a cada item de uma sequência."),
        qa("O que faz filter?", "filter mantém só os itens para os quais a função devolve True."),
        qa("O que é recursão?", "Recursão é quando uma função chama a si mesma para resolver um pedaço menor do problema."),
        qa("O que é o caso base de uma recursão?", "É a condição em que a função para de se chamar e devolve um resultado direto."),
        qa("O que é memoização?", "É guardar resultados já calculados para não calcular de novo. Em Python, lru_cache faz isso."),
        qa("O que é uma closure?", "É uma função criada dentro de outra que lembra as variáveis da função de fora."),
        qa("Para que serve try e except?", "Para tratar erros: o código arriscado fica no try e o tratamento fica no except."),
        qa("Para que serve o finally?", "O bloco finally roda sempre, tenha dado erro ou não. É usado para liberar recursos."),
        qa("Para que serve o raise?", "raise lança um erro de propósito, quando o programa encontra uma situação inválida."),
        qa("Por que não usar except sem tipo?", "Porque ele pega todos os erros, inclusive bugs que você não esperava, e esconde o problema."),
        qa("Por que usar with para abrir arquivos?", "Porque o with fecha o arquivo automaticamente, mesmo se acontecer um erro."),
        qa("Qual a diferença entre os modos w e a ao abrir arquivo?", "w apaga o conteúdo e escreve do zero. a acrescenta no final, sem apagar."),
        qa("O que é JSON?", "JSON é um formato de texto para guardar e trocar dados, com objetos parecidos com dicionários e listas."),
        qa("O que é CSV?", "CSV é um arquivo de texto onde cada linha é um registro e os valores são separados por vírgula."),
        qa("O que é um módulo?", "Um módulo é um arquivo Python com código que pode ser importado e reaproveitado em outro programa."),
        qa("O que é a biblioteca padrão?", "É o conjunto de módulos que já vem com o Python, como math, random, json e datetime."),
        qa("O que é o pip?", "pip é o gerenciador de pacotes do Python. Ele instala bibliotecas de fora, como pip install requests."),
        qa("O que é um ambiente virtual?", "É uma pasta isolada com seu próprio Python e pacotes, para cada projeto ter suas versões sem atrapalhar os outros. Cria-se com python -m venv."),
        qa("O que é uma classe?", "Uma classe é um molde que define os dados e os comportamentos de um tipo de objeto."),
        qa("O que é um objeto?", "Um objeto é uma coisa criada a partir de uma classe, com seus próprios valores."),
        qa("O que é uma instância?", "Instância é outro nome para objeto. Rex é uma instância da classe Cachorro."),
        qa("O que é um atributo?", "Um atributo é um dado guardado dentro de um objeto, como self.nome."),
        qa("O que é um método?", "Um método é uma função que pertence a uma classe e age sobre o objeto."),
        qa("Para que serve o __init__?", "__init__ é chamado quando o objeto é criado e serve para preparar os atributos."),
        qa("O que é self?", "self é o próprio objeto. Por ele o método acessa os atributos e outros métodos daquele objeto."),
        qa("O que é herança?", "Herança é quando uma classe aproveita os atributos e métodos de outra e pode acrescentar ou mudar comportamentos."),
        qa("O que é polimorfismo?", "É quando objetos de classes diferentes respondem ao mesmo método, cada um do seu jeito."),
        qa("O que é encapsulamento?", "É esconder os detalhes internos de um objeto e deixar o acesso pelos métodos."),
        qa("Para que serve o super()?", "super() chama um método da classe mãe, muito usado no __init__ da classe filha."),
        qa("O que é uma dataclass?", "É uma classe criada com @dataclass, que gera automaticamente o __init__ e outras partes a partir dos campos."),
        qa("O que é um gerador?", "Um gerador é uma função com yield que produz valores um de cada vez, sem guardar todos na memória."),
        qa("Qual a diferença entre return e yield?", "return devolve um valor e termina a função. yield entrega um valor e pausa a função, que continua depois."),
        qa("O que é uma pilha?", "Uma pilha é uma estrutura em que o último a entrar é o primeiro a sair."),
        qa("O que é uma fila?", "Uma fila é uma estrutura em que o primeiro a entrar é o primeiro a sair."),
        qa("O que é busca binária?", "É uma busca em lista ordenada que olha o meio e descarta metade da lista a cada passo."),
        qa("Por que a busca binária precisa de lista ordenada?", "Porque ela decide para que lado ir comparando o meio com o alvo, e isso só faz sentido se os itens estiverem em ordem."),
        qa("O que é complexidade de um algoritmo?", "É a medida de como o tempo ou a memória crescem quando o tamanho da entrada cresce."),
        qa("O que significa O(n)?", "Significa que o tempo cresce na mesma proporção que a entrada. O dobro de itens leva mais ou menos o dobro do tempo."),
        qa("O que significa O(1)?", "Significa tempo constante: a operação leva o mesmo tempo, qualquer que seja o tamanho da entrada."),
        qa("O que significa O(n**2)?", "Significa que o tempo cresce com o quadrado da entrada. Acontece com um laço dentro de outro sobre os mesmos dados."),
        qa("Por que procurar num set é mais rápido que numa lista?", "Porque o set usa uma tabela de espalhamento e acha o item direto, em média O(1). A lista precisa olhar item por item, O(n)."),
        qa("O que é um teste automatizado?", "É um código que verifica se outro código está funcionando, sem precisar conferir na mão."),
        qa("O que faz o assert?", "assert verifica uma condição e para o programa com AssertionError se ela for falsa."),
        qa("O que é um caso de borda?", "É uma entrada no limite do que o programa aceita, como lista vazia, zero ou número negativo."),
        qa("O que é PEP 8?", "PEP 8 é o guia de estilo oficial do Python, com regras de nomes, indentação e organização do código."),
        qa("O que é refatorar?", "Refatorar é melhorar a organização do código sem mudar o que ele faz."),
        qa("O que é o Git?", "Git é um sistema de controle de versão. Ele guarda o histórico das mudanças do código."),
        qa("O que é um commit?", "Um commit é um registro de um conjunto de mudanças no Git, com uma mensagem explicando o que mudou."),
        qa("O que é uma branch?", "Uma branch é uma linha de desenvolvimento separada no Git, para trabalhar numa mudança sem mexer na principal."),
        qa("O que é uma API?", "API é uma forma combinada de um programa conversar com outro, como pedir dados a um servidor."),
        qa("O que é uma biblioteca?", "Uma biblioteca é um conjunto de código pronto que você usa no seu programa para não reinventar a roda."),
        qa("O que é um tipo mutável?", "É um tipo que pode ser alterado depois de criado, como lista, dicionário e set."),
        qa("O que é um tipo imutável?", "É um tipo que não pode ser alterado depois de criado, como int, float, str e tupla."),
    ]


# ---------- exercícios variados ----------
def exercicios(rng, n):
    familias = [
        _ex_dict_contagem, _ex_dict_media_alunos, _ex_comprehension_quadrados, _ex_comprehension_filtro,
        _ex_set_comuns, _ex_zip_dict, _ex_ordenar_key, _ex_fatorial_rec, _ex_fib_iterativo, _ex_palindromo,
        _ex_primos_ate, _ex_mdc, _ex_busca_binaria, _ex_bubble, _ex_try_divisao, _ex_classe_retangulo,
        _ex_classe_pessoa, _ex_heranca_forma, _ex_gerador_pares, _ex_arquivo_linhas, _ex_json_roundtrip,
        _ex_maior_palavra, _ex_inverter_palavras, _ex_contar_vogais_func, _ex_estoque, _ex_matriz_transposta,
        _ex_soma_digitos, _ex_lambda_filter, _ex_counter_letras, _ex_anagrama, _ex_achatar, _ex_segundo_maior,
        _ex_caesar, _ex_binario,
    ]
    blocos = [familias[i % len(familias)](rng) for i in range(n)]
    rng.shuffle(blocos)
    return blocos


def _ex_dict_contagem(rng):
    itens = [rng.choice(FRUTAS[:6]) for _ in range(rng.randint(6, 10))]
    return exercicio(f"Conte quantas vezes cada fruta aparece na lista {lista_py(itens)} usando um dicionário.",
                     f"frutas = {lista_py(itens)}\ncontagem = {{}}\nfor f in frutas:\n    contagem[f] = contagem.get(f, 0) + 1\nprint(contagem)",
                     "Para cada fruta, get devolve a contagem atual, ou 0 na primeira vez, e somamos 1.")


def _ex_dict_media_alunos(rng):
    nomes = rng.sample(NOMES, 3)
    notas = {nm: [rng.randint(4, 10) for _ in range(3)] for nm in nomes}
    return exercicio(f"Dado o dicionário de notas {notas}, mostre a média de cada aluno com uma casa decimal.",
                     f'notas = {notas}\nfor aluno, lista in notas.items():\n    media = sum(lista) / len(lista)\n    print(f"{{aluno}}: {{media:.1f}}")',
                     "items entrega cada aluno com sua lista de notas, e a média é a soma dividida pela quantidade.")


def _ex_comprehension_quadrados(rng):
    a, b = rng.randint(1, 5), rng.randint(8, 15)
    exp = rng.choice([2, 3])
    nome = "quadrados" if exp == 2 else "cubos"
    return exercicio(f"Use list comprehension para criar a lista dos {nome} dos números de {a} até {b}.",
                     f"{nome} = [n ** {exp} for n in range({a}, {b + 1})]\nprint({nome})",
                     f"Para cada n de {a} até {b}, a comprehension calcula n elevado a {exp}.")


def _ex_comprehension_filtro(rng):
    xs = [rng.randint(-20, 50) for _ in range(rng.randint(6, 10))]
    cond, desc = rng.choice([("n > 0", "positivos"), ("n % 2 == 0", "pares"), ("n % 2 != 0", "ímpares"), ("n % 5 == 0", "múltiplos de 5")])
    return exercicio(f"Use list comprehension para pegar só os números {desc} da lista {lista_py(xs)}.",
                     f"numeros = {lista_py(xs)}\nresultado = [n for n in numeros if {cond}]\nprint(resultado)",
                     f"O if {cond} deixa passar só os {desc}.")


def _ex_set_comuns(rng):
    a = sorted(rng.sample(range(1, 30), 7))
    b = sorted(rng.sample(range(1, 30), 7))
    return exercicio(f"Mostre, em ordem, os números que aparecem nas duas listas {lista_py(a)} e {lista_py(b)}.",
                     f"a = {lista_py(a)}\nb = {lista_py(b)}\ncomuns = set(a) & set(b)\nprint(sorted(comuns))",
                     "Transformando as listas em sets, o operador & dá a interseção. sorted devolve em ordem.")


def _ex_zip_dict(rng):
    ps = rng.sample(PRODUTOS, 3)
    nomes = [p for p, _ in ps]
    precos = [v for _, v in ps]
    return exercicio(f"Junte as listas {lista_py(nomes)} e {lista_py(precos)} num dicionário de produto para preço.",
                     f"produtos = {lista_py(nomes)}\nprecos = {lista_py(precos)}\ntabela = dict(zip(produtos, precos))\nprint(tabela)\nprint(tabela[\"{nomes[0]}\"])",
                     "zip junta cada produto com o preço na mesma posição, e dict transforma os pares num dicionário.")


def _ex_ordenar_key(rng):
    nomes = rng.sample(NOMES, 5)
    return exercicio(f"Ordene os nomes {lista_py(nomes)} pelo tamanho, do menor para o maior.",
                     f"nomes = {lista_py(nomes)}\nprint(sorted(nomes, key=len))",
                     "key=len faz o sorted comparar o tamanho de cada nome. Nomes com o mesmo tamanho mantêm a ordem em que estavam.")


def _ex_fatorial_rec(rng):
    n = rng.randint(3, 12)
    from math import factorial
    return exercicio(f"Escreva uma função recursiva que calcula o fatorial de {n}.",
                     f"def fatorial(n):\n    if n <= 1:\n        return 1\n    return n * fatorial(n - 1)\nprint(fatorial({n}))",
                     f"O caso base é n <= 1. Cada chamada multiplica n pelo fatorial de n - 1. O fatorial de {n} é {factorial(n)}.")


def _ex_fib_iterativo(rng):
    n = rng.randint(6, 20)
    return exercicio(f"Mostre os {n} primeiros números da sequência de Fibonacci sem usar recursão.",
                     f"a, b = 0, 1\nsequencia = []\nfor _ in range({n}):\n    sequencia.append(a)\n    a, b = b, a + b\nprint(sequencia)",
                     "A cada volta, o próximo número é a soma dos dois anteriores. O _ é usado como nome quando a variável do laço não importa.")


def _ex_palindromo(rng):
    p = rng.choice(PALINDROMOS + PALAVRAS[:6])
    eh = p == p[::-1]
    return exercicio(f"Escreva uma função que diz se uma palavra é palíndromo e teste com {p}.",
                     f'def eh_palindromo(palavra):\n    palavra = palavra.lower()\n    return palavra == palavra[::-1]\nprint(eh_palindromo("{p}"))',
                     f"Palíndromo é uma palavra que se lê igual nos dois sentidos. {p} ao contrário é {p[::-1]}, então {'é' if eh else 'não é'} palíndromo.")


def _ex_primos_ate(rng):
    n = rng.randint(20, 80)
    return exercicio(f"Mostre todos os números primos até {n}.",
                     f"def eh_primo(n):\n    if n < 2:\n        return False\n    for d in range(2, int(n ** 0.5) + 1):\n        if n % d == 0:\n            return False\n    return True\nprint([n for n in range(2, {n + 1}) if eh_primo(n)])",
                     "Para cada número, testamos divisores de 2 até a raiz quadrada. Se nenhum divide, o número é primo.")


def _ex_mdc(rng):
    k = rng.randint(2, 12)
    a, b = k * rng.randint(2, 15), k * rng.randint(2, 15)
    from math import gcd
    return exercicio(f"Calcule o MDC de {a} e {b} com o algoritmo de Euclides.",
                     f"def mdc(a, b):\n    while b:\n        a, b = b, a % b\n    return a\nprint(mdc({a}, {b}))",
                     f"Trocamos o par por (b, a % b) até b virar zero. O MDC de {a} e {b} é {gcd(a, b)}.")


def _ex_busca_binaria(rng):
    xs = sorted(rng.sample(range(1, 100), 10))
    alvo = rng.choice(xs + [101])
    pos = xs.index(alvo) if alvo in xs else -1
    return exercicio(f"Use busca binária para achar a posição de {alvo} na lista ordenada {lista_py(xs)}.",
                     f"def busca_binaria(lista, alvo):\n    inicio, fim = 0, len(lista) - 1\n    while inicio <= fim:\n        meio = (inicio + fim) // 2\n        if lista[meio] == alvo:\n            return meio\n        elif lista[meio] < alvo:\n            inicio = meio + 1\n        else:\n            fim = meio - 1\n    return -1\nprint(busca_binaria({lista_py(xs)}, {alvo}))",
                     f"{'O ' + str(alvo) + ' está na posição ' + str(pos) + '.' if pos >= 0 else 'O ' + str(alvo) + ' não está na lista, por isso a função devolve -1.'}")


def _ex_bubble(rng):
    xs = [rng.randint(1, 60) for _ in range(rng.randint(5, 8))]
    return exercicio(f"Ordene a lista {lista_py(xs)} com bubble sort, sem usar sort.",
                     f"lista = {lista_py(xs)}\nn = len(lista)\nfor i in range(n - 1):\n    for j in range(n - 1 - i):\n        if lista[j] > lista[j + 1]:\n            lista[j], lista[j + 1] = lista[j + 1], lista[j]\nprint(lista)",
                     "A cada passada, vizinhos fora de ordem trocam de lugar e o maior valor restante vai para o final.")


def _ex_try_divisao(rng):
    a = rng.randint(1, 100)
    b = rng.choice([0, rng.randint(1, 10)])
    return exercicio(f"Divida {a} por {b} tratando a divisão por zero com try e except.",
                     f'try:\n    print({a} / {b})\nexcept ZeroDivisionError:\n    print("Não é possível dividir por zero.")',
                     "Como o divisor é zero, o except tratou o erro." if b == 0 else f"A divisão funcionou, então o except não foi usado. {a} / {b} dá {a / b}.")


def _ex_classe_retangulo(rng):
    l, a = rng.randint(2, 20), rng.randint(2, 20)
    return exercicio(f"Crie uma classe Retangulo com métodos area e perimetro e teste com largura {l} e altura {a}.",
                     f"class Retangulo:\n    def __init__(self, largura, altura):\n        self.largura = largura\n        self.altura = altura\n    def area(self):\n        return self.largura * self.altura\n    def perimetro(self):\n        return 2 * (self.largura + self.altura)\nr = Retangulo({l}, {a})\nprint(r.area())\nprint(r.perimetro())",
                     f"A área é {l} vezes {a}, que dá {l * a}. O perímetro é 2 vezes ({l} + {a}), que dá {2 * (l + a)}.")


def _ex_classe_pessoa(rng):
    nome, cidade = rng.choice(NOMES), rng.choice(CIDADES)
    idade = rng.randint(10, 70)
    anos = rng.randint(1, 5)
    return exercicio(f"Crie uma classe Pessoa com nome, idade e cidade, um método fazer_aniversario e um __str__. Crie {nome}, de {idade} anos, de {cidade}, e faça {anos} aniversário{'s' if anos > 1 else ''}.",
                     f'class Pessoa:\n    def __init__(self, nome, idade, cidade):\n        self.nome = nome\n        self.idade = idade\n        self.cidade = cidade\n    def fazer_aniversario(self):\n        self.idade += 1\n    def __str__(self):\n        return f"{{self.nome}}, {{self.idade}} anos, de {{self.cidade}}"\np = Pessoa("{nome}", {idade}, "{cidade}")\nfor _ in range({anos}):\n    p.fazer_aniversario()\nprint(p)',
                     f"Cada aniversário soma 1 na idade. Depois de {anos}, {nome} fica com {idade + anos} anos.")


def _ex_heranca_forma(rng):
    lado, raio = rng.randint(2, 10), rng.randint(1, 6)
    return exercicio(f"Crie uma classe Forma e duas filhas, Quadrado e Circulo, cada uma com seu método area. Teste com lado {lado} e raio {raio}.",
                     f'import math\nclass Forma:\n    def area(self):\n        raise NotImplementedError\n    def descrever(self):\n        return f"{{type(self).__name__}} com área {{self.area():.2f}}"\nclass Quadrado(Forma):\n    def __init__(self, lado):\n        self.lado = lado\n    def area(self):\n        return self.lado ** 2\nclass Circulo(Forma):\n    def __init__(self, raio):\n        self.raio = raio\n    def area(self):\n        return math.pi * self.raio ** 2\nfor forma in [Quadrado({lado}), Circulo({raio})]:\n    print(forma.descrever())',
                     "As duas filhas herdam descrever de Forma e cada uma implementa sua própria area. O descrever chama a area certa para cada objeto.")


def _ex_gerador_pares(rng):
    n = rng.randint(5, 25)
    return exercicio(f"Crie um gerador que produz os números pares de 0 até {n}.",
                     f"def pares_ate(limite):\n    for i in range(0, limite + 1, 2):\n        yield i\nprint(list(pares_ate({n})))",
                     "A função entrega um par de cada vez com yield. list junta todos para mostrar.")


def _ex_arquivo_linhas(rng):
    itens = rng.sample(CIDADES, rng.randint(3, 5))
    conteudo = "\\n".join(itens) + "\\n"
    return exercicio(f"Escreva as cidades {', '.join(itens)} num arquivo, uma por linha, e depois leia o arquivo e conte as linhas.",
                     f'with open("cidades.txt", "w", encoding="utf-8") as f:\n    f.write("{conteudo}")\nwith open("cidades.txt", encoding="utf-8") as f:\n    linhas = [linha.strip() for linha in f]\nprint(linhas)\nprint(len(linhas))',
                     "O modo w escreve o arquivo do zero. Na leitura, cada linha vem com \\n no final, e o strip remove.")


def _ex_json_roundtrip(rng):
    nome = rng.choice(NOMES)
    dados = {"nome": nome, "idade": rng.randint(18, 60), "cidade": rng.choice(CIDADES)}
    return exercicio(f"Transforme o dicionário {dados} em texto JSON e depois de volta em dicionário.",
                     f'import json\ndados = {dados}\ntexto = json.dumps(dados, ensure_ascii=False)\nprint(texto)\nde_volta = json.loads(texto)\nprint(de_volta["nome"])\nprint(de_volta == dados)',
                     "json.dumps transforma o dicionário em string e json.loads faz o caminho contrário. Os dados voltaram iguais.")


def _ex_maior_palavra(rng):
    ps = rng.sample(PALAVRAS + FRUTAS + ANIMAIS, 5)
    frase = " ".join(ps)
    return exercicio(f"Encontre a maior palavra da frase: {frase}",
                     f'frase = "{frase}"\nmaior = max(frase.split(), key=len)\nprint(maior)',
                     "split separa as palavras e max com key=len escolhe a mais comprida. Se houver empate, fica a primeira.")


def _ex_inverter_palavras(rng):
    ps = rng.sample(PALAVRAS + CORES, 4)
    frase = " ".join(ps)
    return exercicio(f"Inverta a ordem das palavras da frase: {frase}",
                     f'frase = "{frase}"\nprint(" ".join(reversed(frase.split())))',
                     "split separa as palavras, reversed inverte a ordem e join junta de novo com espaços.")


def _ex_contar_vogais_func(rng):
    p = rng.choice(CIDADES + PALAVRAS)
    return exercicio(f"Escreva uma função que conta as vogais de um texto e teste com {p}.",
                     f'def contar_vogais(texto):\n    return sum(1 for letra in texto.lower() if letra in "aeiouáéíóúâêôãõà")\nprint(contar_vogais("{p}"))',
                     "Para cada letra que está no texto de vogais, somamos 1. O lower garante que maiúsculas também contem.")


def _ex_estoque(rng):
    ps = rng.sample([p for p, _ in PRODUTOS], 3)
    est = {p: rng.randint(0, 20) for p in ps}
    venda = rng.choice(ps)
    q = rng.randint(1, 25)
    return exercicio(f"O estoque é {est}. Escreva uma função vender que tira a quantidade do estoque ou lança ValueError se não houver o suficiente. Venda {q} de {venda}.",
                     f'estoque = {est}\ndef vender(produto, quantidade):\n    if estoque.get(produto, 0) < quantidade:\n        raise ValueError(f"estoque insuficiente de {{produto}}")\n    estoque[produto] -= quantidade\ntry:\n    vender("{venda}", {q})\n    print("venda feita")\nexcept ValueError as e:\n    print("Erro:", e)\nprint(estoque)',
                     f"Havia {est[venda]} de {venda} e a venda pedia {q}, então {'a venda foi feita' if est[venda] >= q else 'a função lançou o erro e o estoque não mudou'}.")


def _ex_matriz_transposta(rng):
    linhas, colunas = rng.randint(2, 3), rng.randint(2, 4)
    m = [[rng.randint(1, 9) for _ in range(colunas)] for _ in range(linhas)]
    return exercicio(f"Calcule a transposta da matriz {m}, trocando linhas por colunas.",
                     f"matriz = {m}\ntransposta = [[linha[j] for linha in matriz] for j in range(len(matriz[0]))]\nprint(transposta)\nprint([list(c) for c in zip(*matriz)])",
                     f"A matriz tem {linhas} linhas e {colunas} colunas, então a transposta tem {colunas} linhas e {linhas} colunas. zip(*matriz) é um atalho que faz o mesmo.")


def _ex_soma_digitos(rng):
    n = rng.randint(100, 999999)
    return exercicio(f"Some os dígitos do número {n}.",
                     f"n = {n}\nprint(sum(int(d) for d in str(n)))",
                     f"Transformando em texto, dá para percorrer cada dígito: {' + '.join(str(n))} = {sum(int(d) for d in str(n))}.")


def _ex_lambda_filter(rng):
    ps = rng.sample(PRODUTOS, 5)
    lim = rng.choice([5, 8, 10, 15])
    return exercicio(f"Da lista de produtos {ps}, use filter e lambda para pegar os que custam menos de R$ {lim}.",
                     f"produtos = {ps}\nbaratos = list(filter(lambda p: p[1] < {lim}, produtos))\nprint(baratos)",
                     "Cada produto é uma tupla de nome e preço. A lambda olha o preço, p[1], e o filter mantém só os que passam no teste.")


def _ex_counter_letras(rng):
    p = rng.choice(CIDADES + PALAVRAS)
    return exercicio(f"Use Counter para descobrir a letra mais comum em {p.lower()}.",
                     f'from collections import Counter\ntexto = "{p.lower()}".replace(" ", "")\nprint(Counter(texto).most_common(1))',
                     "Counter conta cada letra e most_common(1) devolve a mais frequente com sua contagem. Em caso de empate, vale a que apareceu primeiro.")


def _ex_anagrama(rng):
    pares = [("roma", "amor"), ("ator", "rato"), ("pedra", "padre"), ("sola", "losa"), ("lago", "gola"),
             ("porta", "tropa"), ("casa", "saca"), ("livro", "lirio"), ("python", "typhon"), ("gato", "pato")]
    a, b = rng.choice(pares)
    return exercicio(f"Escreva uma função que diz se {a} e {b} são anagramas, ou seja, têm as mesmas letras.",
                     f'def anagramas(a, b):\n    return sorted(a.lower()) == sorted(b.lower())\nprint(anagramas("{a}", "{b}"))',
                     f"Ordenando as letras das duas palavras, anagramas ficam iguais. {a} e {b} {'são' if sorted(a) == sorted(b) else 'não são'} anagramas.")


def _ex_achatar(rng):
    m = [[rng.randint(1, 9) for _ in range(rng.randint(1, 4))] for _ in range(rng.randint(2, 4))]
    return exercicio(f"Transforme a lista de listas {m} numa lista só.",
                     f"listas = {m}\nplana = [x for sub in listas for x in sub]\nprint(plana)",
                     "A comprehension com dois for percorre cada sublista e depois cada item dela, na mesma ordem de dois for aninhados.")


def _ex_segundo_maior(rng):
    xs = rng.sample(range(1, 100), rng.randint(4, 8))
    return exercicio(f"Encontre o segundo maior número da lista {lista_py(xs)} sem ordenar.",
                     f"numeros = {lista_py(xs)}\nmaior = segundo = float(\"-inf\")\nfor n in numeros:\n    if n > maior:\n        segundo, maior = maior, n\n    elif n > segundo:\n        segundo = n\nprint(segundo)",
                     "Guardamos os dois maiores. Quando aparece um novo maior, o antigo maior vira o segundo. float(\"-inf\") é menos infinito, menor que qualquer número.")


def _ex_caesar(rng):
    p = rng.choice(PALAVRAS)
    k = rng.randint(1, 5)
    return exercicio(f"Codifique a palavra {p} com a cifra de César, avançando {k} letra{'s' if k > 1 else ''} no alfabeto.",
                     f'def cesar(texto, k):\n    resultado = ""\n    for c in texto:\n        if "a" <= c <= "z":\n            resultado += chr((ord(c) - ord("a") + k) % 26 + ord("a"))\n        else:\n            resultado += c\n    return resultado\ncodificado = cesar("{p}", {k})\nprint(codificado)\nprint(cesar(codificado, -{k}))',
                     "ord transforma a letra em número e chr faz o contrário. O % 26 faz o alfabeto dar a volta depois do z. Usando -k, a mensagem volta ao original.")


def _ex_binario(rng):
    n = rng.randint(1, 255)
    return exercicio(f"Converta o número {n} para binário sem usar bin.",
                     f'n = {n}\nbits = ""\nwhile n > 0:\n    bits = str(n % 2) + bits\n    n //= 2\nprint(bits)\nprint(int(bits, 2))',
                     f"Os restos das divisões por 2, de trás para frente, formam o binário {bin(n)[2:]}. int(bits, 2) confirma que ele volta a ser {n}.")
