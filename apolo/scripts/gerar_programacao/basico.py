"""Programação básica em Python: lições escritas à mão + perguntas e respostas + exercícios variados."""
from lib import exemplo, exercicio, qa, licao, lista_py, soma_texto, NOMES, FRUTAS, PRODUTOS, CIDADES, ANIMAIS, CORES, PALAVRAS, VARS_NUM


def licoes():
    b = []

    # ---------- o que é programar ----------
    b.append(licao(
        "O que é programar",
        "Programar é escrever instruções para o computador seguir.",
        "Essas instruções são escritas numa linguagem de programação, como Python ou JavaScript.",
        "O computador não adivinha nada: ele faz exatamente o que está escrito, na ordem em que está escrito.",
        "Um conjunto de instruções que resolve um problema se chama programa.",
        "Um passo a passo para resolver um problema se chama algoritmo.",
        "Uma receita de bolo é um bom exemplo de algoritmo: ela tem ingredientes, que são os dados, e passos, que são as instruções.",
    ))
    b.append(licao(
        "O que é Python",
        "Python é uma linguagem de programação criada por Guido van Rossum e lançada em 1991.",
        "Ela é conhecida por ser fácil de ler, porque o código parece quase com texto em inglês.",
        "Python é usado em sites, automação, ciência de dados, inteligência artificial e jogos.",
        "Para rodar um programa em Python, você salva o código num arquivo com final .py e executa com o comando python arquivo.py.",
        "Em Python, a indentação, que é o espaço no começo da linha, faz parte da regra da linguagem.",
    ))

    # ---------- print ----------
    b.append(licao(
        "A função print",
        "A função print mostra uma mensagem na tela.",
        "O texto que vai dentro do print fica entre aspas.",
        "Cada print escreve numa linha nova.",
    ))
    b.append(exemplo("Como mostrar uma mensagem na tela?", 'print("Olá, mundo!")',
                     "O print escreveu na tela o texto que estava entre as aspas."))
    b.append(exemplo("Como mostrar várias linhas?", 'print("Primeira linha")\nprint("Segunda linha")\nprint("Terceira linha")',
                     "Cada print escreve uma linha. Três print escrevem três linhas."))
    b.append(exemplo("Como mostrar vários valores num print só?", 'print("Tenho", 3, "gatos")',
                     "Quando o print recebe vários valores separados por vírgula, ele coloca um espaço entre eles."))
    b.append(exemplo("Como mostrar um número com print?", "print(42)\nprint(3.5)",
                     "Números não precisam de aspas. O print mostra o número do jeito que ele é."))
    b.append(exemplo("O print também faz contas?", "print(2 + 3)\nprint(10 - 4)",
                     "Sim. O Python primeiro calcula a conta e depois o print mostra o resultado."))
    b.append(exemplo("Qual a diferença entre print(2 + 3) e print(\"2 + 3\")?", 'print(2 + 3)\nprint("2 + 3")',
                     "Sem aspas, 2 + 3 é uma conta e o resultado é 5. Com aspas, \"2 + 3\" é só um texto e aparece do jeito que foi escrito."))
    b.append(exemplo("Como mudar o separador do print?", 'print("a", "b", "c", sep="-")\nprint("2026", "10", "23", sep="/")',
                     "O parâmetro sep troca o espaço que o print coloca entre os valores."))
    b.append(exemplo("Como fazer o print não pular linha?", 'print("Carregando", end="")\nprint("...")',
                     "O parâmetro end diz o que o print coloca no final. O padrão é pular linha. Com end=\"\", a próxima saída continua na mesma linha."))

    # ---------- comentários ----------
    b.append(licao(
        "Comentários",
        "Um comentário é um texto no código que o Python ignora.",
        "Em Python, o comentário começa com o símbolo #.",
        "Comentários servem para explicar o código para quem vai ler depois, inclusive você mesmo.",
    ))
    b.append(exemplo("Como escrever um comentário?", '# Este programa mostra uma saudação\nprint("Bom dia!")  # isto aparece na tela',
                     "As partes depois do # não aparecem na saída, porque o Python ignora os comentários."))

    # ---------- variáveis ----------
    b.append(licao(
        "Variáveis",
        "Uma variável é um nome que guarda um valor.",
        "Para criar uma variável, escreva o nome, o sinal de igual e o valor.",
        "O sinal de igual em programação significa atribuição: guarde este valor neste nome.",
        "Depois de criada, a variável pode ser usada no lugar do valor.",
        "O valor de uma variável pode mudar durante o programa. Por isso ela se chama variável.",
    ))
    b.append(exemplo("Como criar uma variável?", 'nome = "Ana"\nidade = 20\nprint(nome)\nprint(idade)',
                     "A variável nome guarda o texto Ana e a variável idade guarda o número 20."))
    b.append(exemplo("O valor de uma variável pode mudar?", "pontos = 10\nprint(pontos)\npontos = 25\nprint(pontos)",
                     "Sim. Quando atribuímos um novo valor, o valor antigo é substituído."))
    b.append(exemplo("Como aumentar o valor de uma variável?", "contador = 0\ncontador = contador + 1\ncontador = contador + 1\nprint(contador)",
                     "A linha contador = contador + 1 pega o valor atual, soma 1 e guarda de volta. Fizemos isso duas vezes, então o resultado é 2."))
    b.append(exemplo("O que significa += em Python?", "saldo = 100\nsaldo += 50\nprint(saldo)\nsaldo -= 30\nprint(saldo)",
                     "saldo += 50 é um jeito curto de escrever saldo = saldo + 50. Do mesmo jeito, saldo -= 30 é saldo = saldo - 30."))
    b.append(exemplo("Como trocar o valor de duas variáveis?", "a = 1\nb = 2\na, b = b, a\nprint(a, b)",
                     "Em Python, a, b = b, a troca os valores numa linha só, sem precisar de uma variável extra."))
    b.append(licao(
        "Regras para nomes de variáveis",
        "O nome de uma variável pode ter letras, números e o sublinhado _.",
        "O nome não pode começar com número.",
        "O nome não pode ter espaço. Em vez de nota final, escreva nota_final.",
        "Python diferencia maiúsculas de minúsculas: idade e Idade são variáveis diferentes.",
        "Use nomes que explicam o que a variável guarda. preco_total é melhor que x.",
        "Não use como nome as palavras reservadas da linguagem, como if, for, while, def e class.",
    ))

    # ---------- tipos ----------
    b.append(licao(
        "Tipos de dados",
        "Todo valor em Python tem um tipo.",
        "int é o tipo dos números inteiros, como 7, 0 e -3.",
        "float é o tipo dos números com casas decimais, como 3.14 e 0.5. Em Python, a casa decimal usa ponto, não vírgula.",
        "str é o tipo dos textos, chamados de strings. Eles ficam entre aspas.",
        "bool é o tipo dos valores lógicos: True, que é verdadeiro, e False, que é falso.",
        "A função type mostra o tipo de um valor.",
    ))
    b.append(exemplo("Como descobrir o tipo de um valor?", 'print(type(10))\nprint(type(2.5))\nprint(type("oi"))\nprint(type(True))',
                     "10 é int, 2.5 é float, \"oi\" é str e True é bool."))
    b.append(exemplo("\"10\" e 10 são a mesma coisa?", 'print(type("10"))\nprint(type(10))\nprint("10" == 10)',
                     "Não. \"10\" entre aspas é um texto e 10 sem aspas é um número. Por isso a comparação dá False."))

    # ---------- aritmética ----------
    b.append(licao(
        "Operações matemáticas",
        "O sinal + soma, o sinal - subtrai, o sinal * multiplica e o sinal / divide.",
        "O sinal // faz a divisão inteira, que descarta a parte decimal.",
        "O sinal % dá o resto da divisão.",
        "O sinal ** faz a potência. 2 ** 3 é 2 elevado a 3.",
        "A divisão com / sempre devolve um float, mesmo quando a conta é exata.",
        "Como na matemática, multiplicação e divisão acontecem antes de soma e subtração. Parênteses mudam a ordem.",
    ))
    b.append(exemplo("Quais são as operações básicas?", "print(7 + 2)\nprint(7 - 2)\nprint(7 * 2)\nprint(7 / 2)",
                     "7 + 2 é 9, 7 - 2 é 5, 7 * 2 é 14 e 7 / 2 é 3.5."))
    b.append(exemplo("Qual a diferença entre / e //?", "print(7 / 2)\nprint(7 // 2)\nprint(10 / 2)",
                     "/ faz a divisão normal e devolve float. // faz a divisão inteira: 7 // 2 é 3 porque o 2 cabe 3 vezes inteiras no 7. Repare que 10 / 2 dá 5.0, um float."))
    b.append(exemplo("Para que serve o operador %?", "print(7 % 2)\nprint(10 % 3)\nprint(8 % 4)",
                     "O % dá o resto da divisão. 7 dividido por 2 dá 3 e sobra 1. 10 dividido por 3 dá 3 e sobra 1. 8 dividido por 4 é exato, então o resto é 0."))
    b.append(exemplo("Como fazer potência em Python?", "print(2 ** 3)\nprint(5 ** 2)\nprint(9 ** 0.5)",
                     "2 ** 3 é 2 vezes 2 vezes 2, que dá 8. Elevar a 0.5 é o mesmo que tirar a raiz quadrada: a raiz de 9 é 3.0."))
    b.append(exemplo("Os parênteses mudam o resultado?", "print(2 + 3 * 4)\nprint((2 + 3) * 4)",
                     "Sim. Sem parênteses a multiplicação vem primeiro: 3 * 4 é 12, mais 2 dá 14. Com parênteses a soma vem primeiro: 2 + 3 é 5, vezes 4 dá 20."))
    b.append(exemplo("Como arredondar um número?", "print(round(3.7))\nprint(round(3.14159, 2))\nprint(abs(-8))",
                     "round arredonda. Com um segundo número, ele diz quantas casas decimais manter. abs devolve o valor absoluto, que é o número sem o sinal."))
    b.append(exemplo("Como calcular a média de três notas?", "n1 = 7\nn2 = 8\nn3 = 9\nmedia = (n1 + n2 + n3) / 3\nprint(media)",
                     "Somamos as notas e dividimos por 3. Os parênteses são necessários, senão só a última nota seria dividida."))

    # ---------- conversão ----------
    b.append(licao(
        "Conversão de tipos",
        "Às vezes precisamos transformar um valor de um tipo em outro.",
        "int() transforma em número inteiro. float() transforma em número decimal. str() transforma em texto.",
        "Isso é muito usado com input, porque tudo que o usuário digita chega como texto.",
    ))
    b.append(exemplo("Como transformar texto em número?", 'texto = "25"\nnumero = int(texto)\nprint(numero + 5)',
                     "int(\"25\") transforma o texto 25 no número 25. Aí a soma com 5 funciona e dá 30."))
    b.append(exemplo("O que acontece se somar texto com número?", 'idade = 20\nprint("Idade: " + idade)',
                     "Dá erro de tipo, TypeError, porque o Python não junta texto com número sozinho. A solução é converter o número com str(idade).",
                     erro_esperado=True))
    b.append(exemplo("Como juntar texto com número sem erro?", 'idade = 20\nprint("Idade: " + str(idade))',
                     "str(idade) transforma o número 20 no texto \"20\", e aí os dois textos podem ser juntados."))
    b.append(exemplo("O que int() faz com um número decimal?", "print(int(3.9))\nprint(float(4))\nprint(int(\"7\") * 2)",
                     "int() corta a parte decimal, sem arredondar: int(3.9) é 3. float(4) é 4.0."))

    # ---------- strings ----------
    b.append(licao(
        "Strings",
        "String é o nome que se dá a um texto em programação.",
        "Strings podem usar aspas duplas ou aspas simples: \"oi\" e 'oi' são iguais.",
        "O sinal + junta duas strings. Isso se chama concatenação.",
        "O sinal * repete uma string.",
        "A função len diz quantos caracteres a string tem, contando espaços.",
    ))
    b.append(exemplo("Como juntar duas strings?", 'primeiro = "Marcos"\nsobrenome = "Langner"\nprint(primeiro + " " + sobrenome)',
                     "O + junta as strings. Colocamos \" \" no meio para ter um espaço entre os nomes."))
    b.append(exemplo("Como repetir uma string?", 'print("ha" * 3)\nprint("-" * 10)',
                     "\"ha\" * 3 repete o texto três vezes. Isso é útil para desenhar linhas."))
    b.append(exemplo("Como saber o tamanho de uma string?", 'print(len("Apolo"))\nprint(len("bom dia"))\nprint(len(""))',
                     "Apolo tem 5 letras. \"bom dia\" tem 7 caracteres porque o espaço também conta. A string vazia tem tamanho 0."))
    b.append(licao(
        "f-strings",
        "Uma f-string é uma string com a letra f antes das aspas.",
        "Dentro dela, o que estiver entre chaves é trocado pelo valor.",
        "É o jeito mais fácil de montar frases com variáveis.",
    ))
    b.append(exemplo("Como colocar variáveis dentro de um texto?", 'nome = "Bia"\nidade = 19\nprint(f"{nome} tem {idade} anos.")',
                     "A f-string trocou {nome} por Bia e {idade} por 19."))
    b.append(exemplo("Dá para fazer conta dentro de uma f-string?", 'preco = 12.5\nquantidade = 3\nprint(f"Total: {preco * quantidade}")',
                     "Sim. O que está entre chaves é calculado antes de entrar no texto."))
    b.append(exemplo("Como mostrar um número com duas casas decimais?", 'valor = 7.0 / 3\nprint(valor)\nprint(f"{valor:.2f}")',
                     "O :.2f dentro das chaves formata o número com duas casas decimais."))
    b.append(licao(
        "Índices de uma string",
        "Cada caractere de uma string tem uma posição, chamada índice.",
        "O primeiro índice é 0, não 1.",
        "Índices negativos contam do fim: -1 é o último caractere.",
    ))
    b.append(exemplo("Como pegar uma letra de uma string?", 'palavra = "Python"\nprint(palavra[0])\nprint(palavra[1])\nprint(palavra[-1])',
                     "palavra[0] é a primeira letra, P. palavra[1] é a segunda, y. palavra[-1] é a última, n."))
    b.append(exemplo("O que acontece se o índice não existir?", 'palavra = "sol"\nprint(palavra[5])',
                     "Dá IndexError, porque sol só tem os índices 0, 1 e 2.", erro_esperado=True))
    b.append(licao(
        "Fatiamento",
        "Fatiar é pegar um pedaço da string com colchetes e dois pontos: texto[início:fim].",
        "O início entra no pedaço, mas o fim não entra.",
        "Se o início for omitido, começa do zero. Se o fim for omitido, vai até o final.",
        "texto[::-1] devolve a string de trás para frente.",
    ))
    b.append(exemplo("Como pegar um pedaço de uma string?", 'texto = "programação"\nprint(texto[0:4])\nprint(texto[4:])\nprint(texto[:3])\nprint(texto[-3:])',
                     "texto[0:4] pega os índices 0, 1, 2 e 3. texto[4:] vai do índice 4 até o fim. texto[-3:] pega os três últimos caracteres."))
    b.append(exemplo("Como inverter uma string?", 'print("Apolo"[::-1])\nprint("roma"[::-1])',
                     "O fatiamento com passo -1 percorre a string de trás para frente."))
    b.append(licao(
        "Métodos de string",
        "Métodos são funções que pertencem a um valor. Eles são chamados com ponto: texto.upper().",
        "upper deixa tudo maiúsculo e lower deixa tudo minúsculo.",
        "strip tira os espaços do começo e do fim.",
        "replace troca um pedaço do texto por outro.",
        "split quebra o texto numa lista de partes. join faz o contrário: junta uma lista num texto.",
        "Strings não mudam. Os métodos devolvem uma string nova e a original fica igual.",
    ))
    b.append(exemplo("Como deixar um texto em maiúsculas ou minúsculas?", 'nome = "Apolo"\nprint(nome.upper())\nprint(nome.lower())\nprint("maria da silva".title())',
                     "upper deixa tudo maiúsculo, lower tudo minúsculo e title deixa a primeira letra de cada palavra maiúscula."))
    b.append(exemplo("Como tirar espaços sobrando de um texto?", 'entrada = "   oi   "\nprint("[" + entrada + "]")\nprint("[" + entrada.strip() + "]")',
                     "Os colchetes mostram onde a string começa e termina. Depois do strip, os espaços das pontas sumiram."))
    b.append(exemplo("Como trocar uma palavra num texto?", 'frase = "Eu gosto de café"\nprint(frase.replace("café", "chá"))\nprint(frase)',
                     "replace devolveu uma frase nova com chá no lugar de café. A variável frase continuou igual, porque strings não mudam."))
    b.append(exemplo("Como separar as palavras de uma frase?", 'frase = "o rato roeu a roupa"\npalavras = frase.split()\nprint(palavras)\nprint(len(palavras))',
                     "split sem nada dentro separa pelos espaços e devolve uma lista com 5 palavras."))
    b.append(exemplo("Como separar um texto por vírgula?", 'dados = "Ana,20,Vilhena"\nprint(dados.split(","))',
                     "Passando \",\" para o split, ele quebra o texto em cada vírgula."))
    b.append(exemplo("Como juntar uma lista de palavras num texto?", 'partes = ["um", "dois", "três"]\nprint(" ".join(partes))\nprint("-".join(partes))',
                     "join usa a string da frente como cola entre os itens da lista."))
    b.append(exemplo("Como contar quantas vezes uma letra aparece?", 'palavra = "banana"\nprint(palavra.count("a"))\nprint(palavra.count("na"))',
                     "count conta as ocorrências. A letra a aparece 3 vezes em banana e o pedaço na aparece 2 vezes."))
    b.append(exemplo("Como saber se um texto contém outro?", 'frase = "aprender python é divertido"\nprint("python" in frase)\nprint("java" in frase)\nprint(frase.find("python"))',
                     "O operador in responde True ou False. find devolve a posição onde o pedaço começa, ou -1 se não achar."))
    b.append(exemplo("Como saber se um texto começa ou termina com algo?", 'arquivo = "relatorio.pdf"\nprint(arquivo.endswith(".pdf"))\nprint(arquivo.startswith("rel"))',
                     "startswith verifica o começo e endswith verifica o final. Os dois devolvem True ou False."))
    b.append(exemplo("Como saber se um texto só tem números?", 'print("2026".isdigit())\nprint("20a6".isdigit())\nprint("abc".isalpha())',
                     "isdigit devolve True quando todos os caracteres são dígitos. isalpha devolve True quando todos são letras."))

    # ---------- input ----------
    b.append(licao(
        "A função input",
        "A função input pede para o usuário digitar alguma coisa.",
        "O texto dentro do input aparece como pergunta.",
        "O que o usuário digita sempre chega como string. Para fazer contas, é preciso converter com int ou float.",
        "Nos exemplos abaixo, o que o usuário digitou aparece logo depois da pergunta.",
    ))
    b.append(exemplo("Como perguntar o nome do usuário?", 'nome = input("Qual é o seu nome? ")\nprint(f"Prazer, {nome}!")',
                     "O input mostrou a pergunta, o usuário digitou Marcos e o valor foi guardado na variável nome.", entradas=["Marcos"]))
    b.append(exemplo("Como ler um número digitado?", 'idade = int(input("Sua idade: "))\nprint(f"Ano que vem você terá {idade + 1} anos.")',
                     "O int transformou o texto digitado em número para a soma funcionar.", entradas=["20"]))
    b.append(exemplo("O que acontece se esquecer de converter o input?", 'a = input("Primeiro número: ")\nb = input("Segundo número: ")\nprint(a + b)',
                     "Como a e b são strings, o + juntou os textos e o resultado foi 23 em vez de 5. Faltou usar int.", entradas=["2", "3"]))
    b.append(exemplo("Como somar dois números digitados?", 'a = int(input("Primeiro número: "))\nb = int(input("Segundo número: "))\nprint(f"Soma: {a + b}")',
                     "Agora, com int, a soma é numérica: 2 + 3 dá 5.", entradas=["2", "3"]))

    # ---------- booleanos e comparações ----------
    b.append(licao(
        "Comparações",
        "Uma comparação pergunta algo e a resposta é True ou False.",
        "== pergunta se é igual. != pergunta se é diferente.",
        "> é maior que, < é menor que, >= é maior ou igual e <= é menor ou igual.",
        "Atenção: um sinal de igual, =, guarda um valor. Dois sinais, ==, comparam.",
    ))
    b.append(exemplo("Como comparar valores?", "print(5 > 3)\nprint(5 < 3)\nprint(5 == 5)\nprint(5 != 5)\nprint(4 >= 4)",
                     "Cada comparação devolve True ou False."))
    b.append(exemplo("Dá para comparar textos?", 'print("abc" == "abc")\nprint("Abc" == "abc")\nprint("abc" < "abd")',
                     "Sim. A comparação diferencia maiúsculas de minúsculas. O < compara em ordem alfabética."))
    b.append(licao(
        "Operadores lógicos",
        "and dá True só quando as duas condições são verdadeiras.",
        "or dá True quando pelo menos uma das condições é verdadeira.",
        "not inverte: not True é False e not False é True.",
    ))
    b.append(exemplo("Como funcionam and, or e not?", "print(True and True)\nprint(True and False)\nprint(True or False)\nprint(False or False)\nprint(not True)",
                     "and só é True se tudo for True. or é True se pelo menos um for True. not inverte o valor."))
    b.append(exemplo("Como verificar se um número está entre dois valores?", "idade = 25\nprint(idade >= 18 and idade <= 60)\nprint(18 <= idade <= 60)",
                     "As duas formas são iguais. Python permite escrever a comparação encadeada 18 <= idade <= 60."))

    # ---------- if ----------
    b.append(licao(
        "Condicionais com if",
        "O if executa um bloco de código só quando uma condição é verdadeira.",
        "A linha do if termina com dois pontos.",
        "O bloco de dentro do if fica indentado, com quatro espaços no começo da linha.",
        "O else é o caminho quando a condição é falsa.",
        "O elif, que quer dizer senão se, testa outra condição quando a anterior foi falsa.",
        "Só um dos caminhos de um if, elif e else é executado.",
    ))
    b.append(exemplo("Como usar o if?", 'temperatura = 32\nif temperatura > 30:\n    print("Está quente!")\nprint("Fim")',
                     "Como 32 é maior que 30, a condição é verdadeira e a mensagem aparece. O último print está fora do if e roda sempre."))
    b.append(exemplo("Como usar if e else?", 'idade = 15\nif idade >= 18:\n    print("Pode dirigir.")\nelse:\n    print("Ainda não pode dirigir.")',
                     "15 não é maior ou igual a 18, então o programa seguiu pelo else."))
    b.append(exemplo("Como usar elif?", 'nota = 7.5\nif nota >= 9:\n    print("Excelente")\nelif nota >= 7:\n    print("Aprovado")\nelif nota >= 5:\n    print("Recuperação")\nelse:\n    print("Reprovado")',
                     "A nota 7.5 não é maior ou igual a 9, mas é maior ou igual a 7. O primeiro teste verdadeiro foi o do Aprovado, e os outros foram pulados."))
    b.append(exemplo("Como saber se um número é par ou ímpar?", 'numero = 14\nif numero % 2 == 0:\n    print("par")\nelse:\n    print("ímpar")',
                     "Um número é par quando o resto da divisão por 2 é zero. 14 % 2 é 0, então 14 é par."))
    b.append(exemplo("Como colocar um if dentro de outro?", 'tem_ingresso = True\nidade = 16\nif tem_ingresso:\n    if idade >= 18:\n        print("Pode entrar.")\n    else:\n        print("Precisa de um responsável.")\nelse:\n    print("Compre um ingresso.")',
                     "O segundo if só é testado porque o primeiro foi verdadeiro. Cada nível de if ganha mais quatro espaços de indentação."))
    b.append(exemplo("O que acontece se esquecer a indentação?", 'x = 5\nif x > 3:\nprint("maior")',
                     "Dá IndentationError, porque o Python espera um bloco indentado depois dos dois pontos.", erro_esperado=True))

    # ---------- while ----------
    b.append(licao(
        "Repetição com while",
        "O while repete um bloco enquanto a condição for verdadeira.",
        "Antes de cada volta, a condição é testada de novo.",
        "Alguma coisa dentro do laço precisa mudar a condição, senão ele nunca termina. Isso se chama laço infinito.",
        "Laço, loop e repetição são a mesma coisa.",
    ))
    b.append(exemplo("Como contar de 1 a 5 com while?", "contador = 1\nwhile contador <= 5:\n    print(contador)\n    contador += 1",
                     "A cada volta, o contador é mostrado e aumenta 1. Quando chega a 6, a condição fica falsa e o laço para."))
    b.append(exemplo("Como fazer uma contagem regressiva?", 'n = 3\nwhile n > 0:\n    print(n)\n    n -= 1\nprint("Já!")',
                     "O n começa em 3 e diminui a cada volta. Quando vira 0, o laço termina e o programa segue."))
    b.append(exemplo("Como repetir até o usuário acertar?", 'senha = ""\nwhile senha != "apolo":\n    senha = input("Senha: ")\nprint("Acesso liberado.")',
                     "O laço repete enquanto a senha for diferente de apolo. Na terceira tentativa o usuário acertou.", entradas=["123", "abc", "apolo"]))

    # ---------- for ----------
    b.append(licao(
        "Repetição com for",
        "O for percorre uma sequência, um item de cada vez.",
        "range(n) gera os números de 0 até n - 1.",
        "range(início, fim) começa no início e para antes do fim.",
        "range(início, fim, passo) pula de passo em passo.",
        "Use for quando você sabe quantas vezes vai repetir, e while quando depende de uma condição.",
    ))
    b.append(exemplo("Como repetir algo 3 vezes?", 'for i in range(3):\n    print("Olá", i)',
                     "range(3) gera 0, 1 e 2. Então o bloco rodou três vezes, e i valeu 0, depois 1, depois 2."))
    b.append(exemplo("Como contar de 1 a 5 com for?", "for numero in range(1, 6):\n    print(numero)",
                     "range(1, 6) começa em 1 e para antes do 6."))
    b.append(exemplo("Como contar de 2 em 2?", "for numero in range(0, 11, 2):\n    print(numero)",
                     "O terceiro valor do range é o passo. De 0 até 10, pulando de 2 em 2."))
    b.append(exemplo("Como contar de trás para frente com range?", "for numero in range(5, 0, -1):\n    print(numero)",
                     "Com passo -1, o range desce. Ele começa em 5 e para antes do 0."))
    b.append(exemplo("Como percorrer as letras de uma palavra?", 'for letra in "sol":\n    print(letra)',
                     "O for passa por cada caractere da string, um por vez."))
    b.append(exemplo("Como somar os números de 1 a 10?", "soma = 0\nfor n in range(1, 11):\n    soma += n\nprint(soma)",
                     "A variável soma é um acumulador: começa em 0 e recebe cada número. 1 + 2 + 3 até 10 dá 55."))
    b.append(exemplo("Como mostrar a tabuada do 7?", 'for i in range(1, 11):\n    print(f"7 x {i} = {7 * i}")',
                     "O laço passa por i de 1 a 10 e mostra cada multiplicação."))
    b.append(exemplo("Como contar quantas vogais tem uma frase?", 'frase = "inteligencia artificial"\nvogais = 0\nfor letra in frase:\n    if letra in "aeiou":\n        vogais += 1\nprint(vogais)',
                     "O contador vogais aumenta 1 cada vez que a letra está dentro de \"aeiou\"."))
    b.append(licao(
        "break e continue",
        "break para o laço na hora, mesmo que ainda faltem voltas.",
        "continue pula o resto da volta atual e vai para a próxima.",
    ))
    b.append(exemplo("Para que serve o break?", 'for n in range(1, 10):\n    if n == 4:\n        break\n    print(n)\nprint("parou")',
                     "Quando n chegou a 4, o break encerrou o laço. Por isso só aparecem 1, 2 e 3."))
    b.append(exemplo("Para que serve o continue?", "for n in range(1, 6):\n    if n == 3:\n        continue\n    print(n)",
                     "Quando n é 3, o continue pula o print. O laço segue normalmente para o 4 e o 5."))
    b.append(exemplo("Como encontrar o primeiro número divisível por 7 a partir de 50?", 'n = 50\nwhile True:\n    if n % 7 == 0:\n        break\n    n += 1\nprint(n)',
                     "while True cria um laço que só termina pelo break. Ele testa 50, 51, 52 e assim por diante até achar 56, que é 7 vezes 8."))

    # ---------- listas ----------
    b.append(licao(
        "Listas",
        "Uma lista guarda vários valores em ordem, dentro de colchetes e separados por vírgula.",
        "Os itens de uma lista também têm índices que começam em 0.",
        "Diferente das strings, listas podem ser alteradas.",
        "Uma lista pode ter itens de tipos diferentes, mas o mais comum é todos serem do mesmo tipo.",
    ))
    b.append(exemplo("Como criar uma lista e acessar os itens?", 'frutas = ["maçã", "banana", "uva"]\nprint(frutas)\nprint(frutas[0])\nprint(frutas[-1])\nprint(len(frutas))',
                     "frutas[0] é o primeiro item e frutas[-1] é o último. len diz quantos itens a lista tem."))
    b.append(exemplo("Como alterar um item da lista?", 'cores = ["azul", "verde", "rosa"]\ncores[1] = "preto"\nprint(cores)',
                     "Atribuir a cores[1] troca o segundo item."))
    b.append(exemplo("Como adicionar itens numa lista?", 'compras = []\ncompras.append("arroz")\ncompras.append("feijão")\ncompras.insert(0, "café")\nprint(compras)',
                     "[] é uma lista vazia. append coloca no final e insert coloca na posição escolhida, aqui a posição 0."))
    b.append(exemplo("Como remover itens de uma lista?", 'numeros = [10, 20, 30, 40]\nnumeros.remove(20)\nprint(numeros)\nultimo = numeros.pop()\nprint(ultimo)\nprint(numeros)',
                     "remove apaga pelo valor. pop tira o último item e devolve ele."))
    b.append(exemplo("Como saber se um item está na lista?", 'convidados = ["Ana", "Caio", "Lia"]\nprint("Caio" in convidados)\nprint("Rui" in convidados)\nprint(convidados.index("Lia"))',
                     "in responde True ou False. index diz a posição do item."))
    b.append(exemplo("Como ordenar uma lista?", "notas = [7, 3, 9, 1]\nnotas.sort()\nprint(notas)\nnotas.sort(reverse=True)\nprint(notas)",
                     "sort ordena a própria lista. Com reverse=True, a ordem fica do maior para o menor."))
    b.append(exemplo("Qual a diferença entre sort e sorted?", "original = [3, 1, 2]\nnova = sorted(original)\nprint(nova)\nprint(original)",
                     "sorted devolve uma lista nova ordenada e não mexe na original. sort muda a própria lista e não devolve nada."))
    b.append(exemplo("Como somar, achar o maior e o menor de uma lista?", "valores = [4, 8, 15, 16, 23, 42]\nprint(sum(valores))\nprint(max(valores))\nprint(min(valores))",
                     "sum soma tudo, max devolve o maior e min devolve o menor."))
    b.append(exemplo("Como percorrer uma lista com for?", 'animais = ["gato", "pato", "rato"]\nfor animal in animais:\n    print(f"Eu vi um {animal}")',
                     "A variável animal recebe um item da lista a cada volta."))
    b.append(exemplo("Como fatiar uma lista?", "numeros = [0, 1, 2, 3, 4, 5]\nprint(numeros[1:4])\nprint(numeros[:2])\nprint(numeros[::-1])",
                     "O fatiamento de listas funciona igual ao de strings."))
    b.append(exemplo("Como montar uma lista com os números pares até 10?", "pares = []\nfor n in range(1, 11):\n    if n % 2 == 0:\n        pares.append(n)\nprint(pares)",
                     "Começamos com uma lista vazia e colocamos dentro só os números com resto 0 na divisão por 2."))
    b.append(exemplo("Como calcular a média de uma lista?", "notas = [6, 8, 7, 9]\nmedia = sum(notas) / len(notas)\nprint(media)",
                     "A média é a soma dividida pela quantidade. 30 dividido por 4 dá 7.5."))
    b.append(exemplo("Copiar uma lista com = cria uma cópia?", "a = [1, 2]\nb = a\nb.append(3)\nprint(a)\nc = a.copy()\nc.append(4)\nprint(a)\nprint(c)",
                     "Não. b = a faz as duas variáveis apontarem para a mesma lista, então mudar b muda a. Para ter uma cópia de verdade, use a.copy()."))

    # ---------- funções ----------
    b.append(licao(
        "Funções",
        "Uma função é um bloco de código com nome, que pode ser usado várias vezes.",
        "Para criar uma função, use def, o nome, parênteses e dois pontos.",
        "Os valores que a função recebe se chamam parâmetros.",
        "return devolve um resultado para quem chamou a função.",
        "Criar a função não executa o código dela. O código só roda quando a função é chamada.",
        "Funções evitam repetir código e deixam o programa mais organizado.",
    ))
    b.append(exemplo("Como criar e chamar uma função?", 'def saudar():\n    print("Olá!")\nsaudar()\nsaudar()',
                     "A função saudar foi definida uma vez e chamada duas vezes, então a mensagem apareceu duas vezes."))
    b.append(exemplo("Como passar um valor para uma função?", 'def saudar(nome):\n    print(f"Olá, {nome}!")\nsaudar("Ana")\nsaudar("Marcos")',
                     "nome é o parâmetro. Em cada chamada ele recebe um valor diferente."))
    b.append(exemplo("Como uma função devolve um resultado?", "def somar(a, b):\n    return a + b\nresultado = somar(3, 4)\nprint(resultado)\nprint(somar(10, 5))",
                     "return entrega o resultado da conta. Ele pode ser guardado numa variável ou usado direto."))
    b.append(exemplo("Qual a diferença entre print e return numa função?", 'def com_print(x):\n    print(x * 2)\ndef com_return(x):\n    return x * 2\na = com_print(5)\nb = com_return(5)\nprint(a)\nprint(b)',
                     "com_print mostra 10 na tela, mas não devolve nada, então a vale None. com_return não mostra nada, mas devolve 10, que fica guardado em b."))
    b.append(exemplo("Como dar um valor padrão a um parâmetro?", 'def potencia(base, expoente=2):\n    return base ** expoente\nprint(potencia(5))\nprint(potencia(2, 10))',
                     "Se o expoente não for passado, ele vale 2. potencia(5) é 25 e potencia(2, 10) é 1024."))
    b.append(exemplo("Como passar argumentos pelo nome?", 'def apresentar(nome, cidade):\n    print(f"{nome} mora em {cidade}.")\napresentar(cidade="Vilhena", nome="Marcos")',
                     "Usando nome=valor, a ordem dos argumentos não importa."))
    b.append(exemplo("Uma função pode devolver True ou False?", "def eh_par(n):\n    return n % 2 == 0\nprint(eh_par(4))\nprint(eh_par(7))",
                     "Sim. A comparação n % 2 == 0 já é True ou False, então a função devolve direto."))
    b.append(exemplo("Uma função pode chamar outra?", "def quadrado(n):\n    return n * n\ndef soma_dos_quadrados(a, b):\n    return quadrado(a) + quadrado(b)\nprint(soma_dos_quadrados(3, 4))",
                     "soma_dos_quadrados usa quadrado duas vezes: 9 + 16 dá 25."))
    b.append(exemplo("O return encerra a função?", 'def classificar(n):\n    if n < 0:\n        return "negativo"\n    if n == 0:\n        return "zero"\n    return "positivo"\nprint(classificar(-2))\nprint(classificar(0))\nprint(classificar(8))',
                     "Sim. Assim que um return é executado, a função termina e as linhas seguintes não rodam."))
    b.append(licao(
        "Escopo de variáveis",
        "Uma variável criada dentro de uma função só existe dentro dela. Isso se chama variável local.",
        "Uma variável criada fora de todas as funções é global e pode ser lida dentro das funções.",
        "O melhor jeito de passar valores para uma função é pelos parâmetros, e o melhor jeito de receber valores é pelo return.",
    ))
    b.append(exemplo("Uma variável de dentro da função existe fora dela?", "def calcular():\n    resultado = 42\n    return resultado\ncalcular()\nprint(resultado)",
                     "Não. resultado é local da função, então fora dela dá NameError.", erro_esperado=True))
    b.append(licao(
        "O valor None",
        "None é um valor especial que significa nada, ausência de valor.",
        "Uma função sem return devolve None.",
        "Para testar se algo é None, escreva if valor is None.",
    ))
    b.append(exemplo("O que uma função sem return devolve?", 'def nada():\n    x = 1\nprint(nada())\nprint(nada() is None)',
                     "Devolve None."))

    # ---------- erros ----------
    b.append(licao(
        "Lendo erros",
        "Erros fazem parte da programação. A mensagem de erro diz o tipo do erro e o motivo.",
        "SyntaxError: o código foi escrito fora das regras da linguagem, como um parêntese sem fechar.",
        "IndentationError: a indentação está errada.",
        "NameError: usou um nome que não existe, muitas vezes por erro de digitação.",
        "TypeError: misturou tipos que não combinam, como texto com número.",
        "ValueError: o tipo está certo, mas o valor não serve, como int(\"abc\").",
        "IndexError: pediu um índice que não existe na lista ou string.",
        "ZeroDivisionError: tentou dividir por zero.",
        "Ler a última linha do erro com calma resolve a maioria dos problemas.",
    ))
    b.append(exemplo("Que erro aparece ao usar uma variável que não existe?", "nome = \"Ana\"\nprint(nmoe)",
                     "NameError. A variável foi criada como nome, mas foi escrita errado no print.", erro_esperado=True))
    b.append(exemplo("Que erro aparece ao dividir por zero?", "print(10 / 0)",
                     "ZeroDivisionError. Não existe divisão por zero na matemática.", erro_esperado=True))
    b.append(exemplo("Que erro aparece ao converter um texto que não é número?", 'print(int("abc"))',
                     "ValueError, porque abc não pode virar número inteiro.", erro_esperado=True))
    b.append(exemplo("Que erro aparece ao esquecer de fechar um parêntese?", 'print("oi"',
                     "SyntaxError. O Python avisa que o parêntese aberto nunca foi fechado.", erro_esperado=True))
    b.append(exemplo("Que erro aparece ao pegar um índice que não existe numa lista?", "numeros = [1, 2, 3]\nprint(numeros[3])",
                     "IndexError. A lista tem 3 itens, então os índices válidos são 0, 1 e 2.", erro_esperado=True))

    # ---------- programinhas completos ----------
    b.append(licao(
        "Juntando tudo",
        "Um programa de verdade junta variáveis, condicionais, repetições, listas e funções.",
        "O jeito de construir é ir passo a passo: primeiro entender o problema, depois escrever a menor parte que funciona, testar, e só então continuar.",
    ))
    b.append(exemplo("Como fazer uma calculadora simples?", 'def calcular(a, operacao, b):\n    if operacao == "+":\n        return a + b\n    elif operacao == "-":\n        return a - b\n    elif operacao == "*":\n        return a * b\n    elif operacao == "/":\n        if b == 0:\n            return "não dá para dividir por zero"\n        return a / b\n    return "operação desconhecida"\nprint(calcular(8, "+", 2))\nprint(calcular(8, "/", 2))\nprint(calcular(8, "/", 0))\nprint(calcular(8, "?", 2))',
                     "A função escolhe a conta pelo if e elif. Ela também trata a divisão por zero e operações que não conhece."))
    b.append(exemplo("Como fazer um jogo de adivinhar o número?", 'secreto = 7\ntentativas = 0\nwhile True:\n    palpite = int(input("Seu palpite: "))\n    tentativas += 1\n    if palpite < secreto:\n        print("Mais alto.")\n    elif palpite > secreto:\n        print("Mais baixo.")\n    else:\n        print(f"Acertou em {tentativas} tentativas!")\n        break',
                     "O laço continua até o palpite ser igual ao número secreto. A cada volta o programa dá uma dica.", entradas=["3", "9", "7"]))
    b.append(exemplo("Como calcular o total de uma compra?", 'precos = [5.40, 1.20, 18.00]\ntotal = 0\nfor preco in precos:\n    total += preco\nprint(f"Total: R$ {total:.2f}")\nif total > 20:\n    print("Ganhou frete grátis.")',
                     "O laço soma os preços. Depois o if decide se a compra ganha frete grátis."))
    b.append(exemplo("Como encontrar a maior nota sem usar max?", "notas = [6.5, 9.0, 7.5, 8.0]\nmaior = notas[0]\nfor nota in notas:\n    if nota > maior:\n        maior = nota\nprint(maior)",
                     "Começamos achando que a primeira nota é a maior. Depois comparamos com cada uma e trocamos sempre que achamos uma maior."))
    b.append(exemplo("Como fazer o FizzBuzz?", 'for n in range(1, 16):\n    if n % 15 == 0:\n        print("FizzBuzz")\n    elif n % 3 == 0:\n        print("Fizz")\n    elif n % 5 == 0:\n        print("Buzz")\n    else:\n        print(n)',
                     "Múltiplos de 3 viram Fizz, de 5 viram Buzz e de 15, que são múltiplos dos dois, viram FizzBuzz. O teste do 15 vem primeiro, senão ele cairia no Fizz."))
    b.append(exemplo("Como desenhar um triângulo de asteriscos?", 'for linha in range(1, 5):\n    print("*" * linha)',
                     "Em cada linha repetimos o asterisco tantas vezes quanto o número da linha."))
    return b


def perguntas():
    return [
        qa("O que é um algoritmo?", "Um algoritmo é uma sequência de passos bem definidos para resolver um problema."),
        qa("O que é um programa?", "Um programa é um conjunto de instruções que o computador executa."),
        qa("O que é uma linguagem de programação?", "É uma linguagem com regras precisas que usamos para escrever instruções para o computador."),
        qa("O que é Python?", "Python é uma linguagem de programação fácil de ler, usada em sites, automação, dados e inteligência artificial."),
        qa("O que é código-fonte?", "Código-fonte é o texto do programa, escrito por uma pessoa numa linguagem de programação."),
        qa("O que é uma variável?", "Uma variável é um nome que guarda um valor na memória."),
        qa("O que faz o sinal de igual em Python?", "Um sinal de igual guarda um valor numa variável. Para comparar, usamos dois sinais: ==."),
        qa("Qual a diferença entre = e ==?", "O = atribui um valor a uma variável. O == compara dois valores e devolve True ou False."),
        qa("O que é um int?", "int é o tipo dos números inteiros, como 3, 0 e -10."),
        qa("O que é um float?", "float é o tipo dos números com casa decimal, como 2.5. Em Python a casa decimal usa ponto."),
        qa("O que é uma string?", "String é um texto. Em Python ela fica entre aspas simples ou duplas."),
        qa("O que é um bool?", "bool é o tipo que só tem dois valores: True e False."),
        qa("O que faz a função print?", "print mostra valores na tela."),
        qa("O que faz a função input?", "input pede para o usuário digitar algo e devolve o que foi digitado como string."),
        qa("Por que preciso usar int() com input()?", "Porque input sempre devolve texto. Para fazer contas, é preciso converter para número."),
        qa("O que faz a função len?", "len devolve o tamanho de uma string, lista ou outra coleção."),
        qa("O que faz a função type?", "type mostra o tipo de um valor, como int, float, str ou bool."),
        qa("O que é um comentário?", "Um comentário é um texto que o Python ignora. Ele começa com # e serve para explicar o código."),
        qa("O que faz o operador %?", "O % devolve o resto de uma divisão. Por exemplo, 7 % 3 é 1."),
        qa("O que faz o operador //?", "O // faz a divisão inteira, descartando a parte decimal. 7 // 2 é 3."),
        qa("O que faz o operador **?", "O ** faz potência. 2 ** 3 é 8."),
        qa("Como saber se um número é par?", "Um número é par quando numero % 2 == 0."),
        qa("O que é indentação?", "Indentação é o espaço no começo da linha. Em Python ela mostra quais linhas pertencem a um bloco, como o de um if ou de um for."),
        qa("Quantos espaços usar na indentação?", "O padrão em Python é usar quatro espaços para cada nível."),
        qa("O que é uma condição?", "Uma condição é uma expressão que dá True ou False, como idade >= 18."),
        qa("Para que serve o if?", "O if executa um bloco de código só quando a condição é verdadeira."),
        qa("Para que serve o else?", "O else é o caminho que o programa segue quando a condição do if é falsa."),
        qa("Para que serve o elif?", "O elif testa outra condição quando as anteriores foram falsas."),
        qa("O que faz o operador and?", "and dá True só quando as duas condições são verdadeiras."),
        qa("O que faz o operador or?", "or dá True quando pelo menos uma das condições é verdadeira."),
        qa("O que faz o operador not?", "not inverte o valor lógico. not True é False."),
        qa("O que é um laço?", "Um laço, ou loop, é uma estrutura que repete um bloco de código."),
        qa("Para que serve o while?", "O while repete um bloco enquanto a condição for verdadeira."),
        qa("Para que serve o for?", "O for percorre os itens de uma sequência, como uma lista, uma string ou um range."),
        qa("Quando usar for e quando usar while?", "Use for quando sabe quantas vezes vai repetir ou quer percorrer uma coleção. Use while quando a repetição depende de uma condição."),
        qa("O que é um laço infinito?", "É um laço cuja condição nunca fica falsa, então ele nunca termina."),
        qa("O que faz range(5)?", "range(5) gera os números 0, 1, 2, 3 e 4."),
        qa("O que faz range(1, 6)?", "range(1, 6) gera os números de 1 a 5. O último número não entra."),
        qa("O que faz o break?", "break interrompe o laço na hora."),
        qa("O que faz o continue?", "continue pula para a próxima volta do laço."),
        qa("O que é um acumulador?", "É uma variável que começa com um valor, geralmente 0, e vai somando valores dentro de um laço."),
        qa("O que é um contador?", "É uma variável que aumenta de 1 em 1 para contar quantas vezes algo aconteceu."),
        qa("O que é uma lista?", "Uma lista é uma coleção ordenada de valores, escrita entre colchetes."),
        qa("Qual é o índice do primeiro item de uma lista?", "O primeiro item tem índice 0."),
        qa("Qual é o índice do último item de uma lista?", "O último item pode ser acessado com o índice -1."),
        qa("Como adicionar um item no final de uma lista?", "Com o método append. Por exemplo: frutas.append(\"uva\")."),
        qa("Como remover um item de uma lista?", "Com remove, passando o valor, ou com pop, passando a posição."),
        qa("Qual a diferença entre sort e sorted?", "sort ordena a própria lista. sorted devolve uma lista nova e deixa a original igual."),
        qa("O que é uma função?", "Uma função é um bloco de código com nome que pode ser chamado várias vezes."),
        qa("Como se cria uma função em Python?", "Com a palavra def, o nome da função, os parâmetros entre parênteses e dois pontos."),
        qa("O que é um parâmetro?", "Um parâmetro é uma variável da função que recebe um valor quando ela é chamada."),
        qa("O que é um argumento?", "Um argumento é o valor que você passa para a função na hora de chamar."),
        qa("O que faz o return?", "return devolve um valor para quem chamou a função e encerra a função."),
        qa("O que uma função sem return devolve?", "Devolve None."),
        qa("O que é None?", "None é um valor especial que representa a ausência de valor."),
        qa("O que é uma variável local?", "É uma variável criada dentro de uma função. Ela só existe enquanto a função está rodando."),
        qa("O que é uma f-string?", "É uma string com f antes das aspas, onde o que está entre chaves é trocado pelo valor."),
        qa("O que é concatenar?", "Concatenar é juntar strings, geralmente com o sinal +."),
        qa("Strings podem ser alteradas?", "Não. Strings são imutáveis. Métodos como replace e upper devolvem uma string nova."),
        qa("O que faz o método split?", "split quebra uma string numa lista de partes."),
        qa("O que faz o método join?", "join junta os itens de uma lista numa string, usando um separador."),
        qa("O que faz o método strip?", "strip remove os espaços do começo e do fim de uma string."),
        qa("O que é um erro de sintaxe?", "É quando o código não segue as regras da linguagem, como esquecer dois pontos ou um parêntese."),
        qa("O que significa NameError?", "Significa que você usou um nome que não existe. Muitas vezes é erro de digitação."),
        qa("O que significa TypeError?", "Significa que você usou um tipo errado na operação, como somar texto com número."),
        qa("O que significa ValueError?", "Significa que o tipo está certo, mas o valor não serve, como int(\"abc\")."),
        qa("O que significa IndexError?", "Significa que você pediu uma posição que não existe na lista ou na string."),
        qa("O que é depurar um programa?", "Depurar é procurar e corrigir erros no programa. Em inglês se diz debug."),
        qa("O que é um bug?", "Um bug é um erro no programa que faz ele se comportar de um jeito errado."),
        qa("Como começar a resolver um problema de programação?", "Primeiro entenda o que entra e o que deve sair. Depois divida o problema em passos pequenos e teste cada passo."),
    ]


# ---------- exercícios com valores variados (as saídas são calculadas rodando o código) ----------
def exercicios(rng, n):
    familias = [
        _ex_soma, _ex_area_retangulo, _ex_par_impar, _ex_maior_de_dois, _ex_tabuada, _ex_soma_ate,
        _ex_media_lista, _ex_contar_letra, _ex_inverter, _ex_dobro_funcao, _ex_lista_append,
        _ex_maior_idade, _ex_conversao_temp, _ex_desconto, _ex_contagem_regressiva, _ex_pares_ate,
        _ex_fstring, _ex_maiusculas, _ex_tamanho_palavras, _ex_contar_maiores, _ex_divisao_resto,
        _ex_nota_conceito, _ex_somar_input, _ex_fatorial_loop, _ex_potencias_de_dois,
        _ex_total_compras, _ex_primeira_ultima, _ex_multiplos, _ex_preco_com_quantidade, _ex_imc,
    ]
    blocos = []
    for i in range(n):
        blocos.append(familias[i % len(familias)](rng))
    rng.shuffle(blocos)
    return blocos


def _ex_soma(rng):
    a, b = rng.randint(1, 500), rng.randint(1, 500)
    va, vb = rng.sample(VARS_NUM, 2)
    return exercicio(f"Crie duas variáveis, {va} valendo {a} e {vb} valendo {b}, e mostre a soma delas.",
                     f"{va} = {a}\n{vb} = {b}\nprint({va} + {vb})",
                     f"A soma de {a} com {b} é {a + b}.")


def _ex_area_retangulo(rng):
    l, a = rng.randint(2, 40), rng.randint(2, 40)
    return exercicio(f"Calcule a área de um retângulo com largura {l} e altura {a}.",
                     f"largura = {l}\naltura = {a}\narea = largura * altura\nprint(f\"Área: {{area}}\")",
                     f"A área do retângulo é largura vezes altura: {l} vezes {a} dá {l * a}.")


def _ex_par_impar(rng):
    n = rng.randint(1, 999)
    return exercicio(f"Escreva um programa que diga se o número {n} é par ou ímpar.",
                     f'numero = {n}\nif numero % 2 == 0:\n    print("par")\nelse:\n    print("ímpar")',
                     f"{n} % 2 é {n % 2}, então {n} é {'par' if n % 2 == 0 else 'ímpar'}.")


def _ex_maior_de_dois(rng):
    a, b = rng.sample(range(1, 300), 2)
    return exercicio(f"Escreva uma função maior que recebe dois números e devolve o maior. Teste com {a} e {b}.",
                     f"def maior(a, b):\n    if a > b:\n        return a\n    return b\nprint(maior({a}, {b}))",
                     f"Entre {a} e {b}, o maior é {max(a, b)}.")


def _ex_tabuada(rng):
    n = rng.randint(2, 12)
    ate = rng.choice([5, 10])
    return exercicio(f"Mostre a tabuada do {n} de 1 até {ate}.",
                     f'for i in range(1, {ate + 1}):\n    print(f"{n} x {{i}} = {{{n} * i}}")',
                     f"O range(1, {ate + 1}) faz o i ir de 1 até {ate}, e cada linha mostra {n} vezes i.")


def _ex_soma_ate(rng):
    n = rng.randint(5, 100)
    return exercicio(f"Some todos os números de 1 até {n} usando for.",
                     f"soma = 0\nfor i in range(1, {n + 1}):\n    soma += i\nprint(soma)",
                     f"O acumulador soma começa em 0 e recebe cada número de 1 a {n}. O total é {n * (n + 1) // 2}.")


def _ex_media_lista(rng):
    xs = [rng.randint(0, 10) for _ in range(rng.randint(3, 6))]
    return exercicio(f"Calcule a média das notas {lista_py(xs)}.",
                     f"notas = {lista_py(xs)}\nmedia = sum(notas) / len(notas)\nprint(round(media, 2))",
                     f"A soma é {soma_texto(xs)}. Dividindo por {len(xs)} notas, a média fica {round(sum(xs) / len(xs), 2)}.")


def _ex_contar_letra(rng):
    p = rng.choice(PALAVRAS + FRUTAS)
    letra = rng.choice(sorted(set(p)))
    return exercicio(f"Conte quantas vezes a letra {letra} aparece na palavra {p}.",
                     f'palavra = "{p}"\nprint(palavra.count("{letra}"))',
                     f"A letra {letra} aparece {p.count(letra)} vez{'es' if p.count(letra) != 1 else ''} em {p}.")


def _ex_inverter(rng):
    p = rng.choice(PALAVRAS + CIDADES + NOMES)
    return exercicio(f"Mostre o texto {p} de trás para frente.",
                     f'texto = "{p}"\nprint(texto[::-1])',
                     f"O fatiamento [::-1] percorre o texto do fim para o começo, então {p} vira {p[::-1]}.")


def _ex_dobro_funcao(rng):
    nomes = [("dobro", 2), ("triplo", 3), ("quadruplo", 4)]
    nome, k = rng.choice(nomes)
    xs = rng.sample(range(1, 50), 2)
    return exercicio(f"Crie uma função {nome} que recebe um número e devolve ele multiplicado por {k}. Teste com {xs[0]} e {xs[1]}.",
                     f"def {nome}(n):\n    return n * {k}\nprint({nome}({xs[0]}))\nprint({nome}({xs[1]}))",
                     f"{xs[0]} vezes {k} é {xs[0] * k} e {xs[1]} vezes {k} é {xs[1] * k}.")


def _ex_lista_append(rng):
    itens = rng.sample(FRUTAS, 3)
    return exercicio(f"Comece com uma lista vazia, adicione {itens[0]}, {itens[1]} e {itens[2]} e mostre a lista e o tamanho dela.",
                     f'cesta = []\ncesta.append("{itens[0]}")\ncesta.append("{itens[1]}")\ncesta.append("{itens[2]}")\nprint(cesta)\nprint(len(cesta))',
                     "Cada append coloca um item no final da lista. No fim ela tem 3 itens.")


def _ex_maior_idade(rng):
    nome = rng.choice(NOMES)
    idade = rng.randint(5, 80)
    return exercicio(f"{nome} tem {idade} anos. Escreva um programa que diga se {nome} é maior de idade.",
                     f'nome = "{nome}"\nidade = {idade}\nif idade >= 18:\n    print(f"{{nome}} é maior de idade.")\nelse:\n    print(f"{{nome}} é menor de idade.")',
                     f"Como {idade} {'é' if idade >= 18 else 'não é'} maior ou igual a 18, o programa seguiu pelo {'if' if idade >= 18 else 'else'}.")


def _ex_conversao_temp(rng):
    c = rng.choice(range(-10, 45))
    return exercicio(f"Converta {c} graus Celsius para Fahrenheit. A fórmula é F = C * 9 / 5 + 32.",
                     f"celsius = {c}\nfahrenheit = celsius * 9 / 5 + 32\nprint(fahrenheit)",
                     f"{c} vezes 9, dividido por 5, mais 32 dá {c * 9 / 5 + 32}.")


def _ex_desconto(rng):
    produto, preco = rng.choice(PRODUTOS)
    pct = rng.choice([5, 10, 15, 20, 25, 30, 50])
    final = preco * (1 - pct / 100)
    return exercicio(f"O produto {produto} custa R$ {preco:.2f}. Calcule o preço com {pct}% de desconto.",
                     f'preco = {preco}\ndesconto = {pct}\nfinal = preco * (1 - desconto / 100)\nprint(f"R$ {{final:.2f}}")',
                     f"Tirar {pct}% é o mesmo que pagar {100 - pct}% do preço. O valor final é R$ {final:.2f}.")


def _ex_contagem_regressiva(rng):
    n = rng.randint(3, 8)
    return exercicio(f"Faça uma contagem regressiva de {n} até 1 com while e no final mostre Fim!",
                     f'n = {n}\nwhile n >= 1:\n    print(n)\n    n -= 1\nprint("Fim!")',
                     f"O n começa em {n} e diminui 1 a cada volta. Quando vira 0 o laço para.")


def _ex_pares_ate(rng):
    n = rng.randint(8, 30)
    return exercicio(f"Monte uma lista com os números pares de 1 até {n}.",
                     f"pares = []\nfor i in range(1, {n + 1}):\n    if i % 2 == 0:\n        pares.append(i)\nprint(pares)",
                     f"Só entram na lista os números com resto zero na divisão por 2. São {len([i for i in range(1, n + 1) if i % 2 == 0])} números.")


def _ex_fstring(rng):
    nome, cidade = rng.choice(NOMES), rng.choice(CIDADES)
    idade = rng.randint(16, 70)
    return exercicio(f"Use uma f-string para mostrar a frase: {nome} tem {idade} anos e mora em {cidade}.",
                     f'nome = "{nome}"\nidade = {idade}\ncidade = "{cidade}"\nprint(f"{{nome}} tem {{idade}} anos e mora em {{cidade}}.")',
                     "Cada variável entre chaves foi trocada pelo seu valor.")


def _ex_maiusculas(rng):
    p = rng.choice(CIDADES + NOMES)
    return exercicio(f"Mostre {p} todo em maiúsculas e depois todo em minúsculas.",
                     f'texto = "{p}"\nprint(texto.upper())\nprint(texto.lower())',
                     "upper deixa todas as letras maiúsculas e lower deixa todas minúsculas.")


def _ex_tamanho_palavras(rng):
    ps = rng.sample(PALAVRAS + FRUTAS, 3)
    return exercicio(f"Mostre cada palavra da lista {lista_py(ps)} junto com o número de letras dela.",
                     f'palavras = {lista_py(ps)}\nfor p in palavras:\n    print(p, len(p))',
                     "O for passa por cada palavra e len conta os caracteres.")


def _ex_contar_maiores(rng):
    xs = [rng.randint(1, 100) for _ in range(rng.randint(5, 8))]
    lim = rng.choice([30, 40, 50, 60])
    k = len([x for x in xs if x > lim])
    return exercicio(f"Conte quantos números da lista {lista_py(xs)} são maiores que {lim}.",
                     f"numeros = {lista_py(xs)}\ncontador = 0\nfor n in numeros:\n    if n > {lim}:\n        contador += 1\nprint(contador)",
                     f"O contador aumenta só quando o número passa de {lim}. Isso acontece {k} vez{'es' if k != 1 else ''}.")


def _ex_divisao_resto(rng):
    a, b = rng.randint(10, 200), rng.randint(2, 12)
    return exercicio(f"Mostre o resultado inteiro e o resto da divisão de {a} por {b}.",
                     f"print({a} // {b})\nprint({a} % {b})",
                     f"{b} cabe {a // b} vezes em {a} e sobra {a % b}. Conferindo: {b} vezes {a // b} mais {a % b} dá {a}.")


def _ex_nota_conceito(rng):
    nota = rng.choice([x / 2 for x in range(0, 21)])
    conceito = "A" if nota >= 9 else "B" if nota >= 7 else "C" if nota >= 5 else "D"
    return exercicio(f"Transforme a nota {nota} em conceito: A para 9 ou mais, B para 7 ou mais, C para 5 ou mais e D para o resto.",
                     f'nota = {nota}\nif nota >= 9:\n    print("A")\nelif nota >= 7:\n    print("B")\nelif nota >= 5:\n    print("C")\nelse:\n    print("D")',
                     f"A nota {nota} cai no conceito {conceito}, que é o primeiro teste verdadeiro de cima para baixo.")


def _ex_somar_input(rng):
    a, b = rng.randint(1, 99), rng.randint(1, 99)
    return exercicio("Peça dois números ao usuário e mostre a soma.",
                     'a = int(input("Primeiro: "))\nb = int(input("Segundo: "))\nprint(f"Soma: {a + b}")',
                     f"O usuário digitou {a} e {b}. Com int, os textos viram números e a soma dá {a + b}.",
                     entradas=[str(a), str(b)])


def _ex_fatorial_loop(rng):
    n = rng.randint(3, 10)
    from math import factorial
    return exercicio(f"Calcule o fatorial de {n} usando um laço for.",
                     f"n = {n}\nresultado = 1\nfor i in range(1, n + 1):\n    resultado *= i\nprint(resultado)",
                     f"O fatorial de {n} é a multiplicação de 1 até {n}: {' x '.join(str(i) for i in range(1, n + 1))} = {factorial(n)}.")


def _ex_potencias_de_dois(rng):
    n = rng.randint(4, 10)
    return exercicio(f"Mostre as potências de 2 de 2 elevado a 0 até 2 elevado a {n}.",
                     f'for i in range({n + 1}):\n    print(f"2 elevado a {{i}} = {{2 ** i}}")',
                     "A cada volta o expoente aumenta 1 e o resultado dobra.")


def _ex_total_compras(rng):
    itens = rng.sample(PRODUTOS, rng.randint(2, 4))
    nomes = [p for p, _ in itens]
    precos = [v for _, v in itens]
    return exercicio(f"Calcule o total de uma compra com {', '.join(nomes)}, que custam {', '.join(f'R$ {v:.2f}' for v in precos)}.",
                     f'precos = {lista_py(precos)}\ntotal = sum(precos)\nprint(f"Total: R$ {{total:.2f}}")',
                     f"sum soma todos os preços da lista. O total é R$ {sum(precos):.2f}.")


def _ex_primeira_ultima(rng):
    p = rng.choice(PALAVRAS + CIDADES)
    return exercicio(f"Mostre a primeira e a última letra de {p}.",
                     f'texto = "{p}"\nprint(texto[0])\nprint(texto[-1])',
                     f"O índice 0 é a primeira letra, {p[0]}, e o índice -1 é a última, {p[-1]}.")


def _ex_multiplos(rng):
    k = rng.randint(3, 9)
    ate = rng.randint(20, 60)
    return exercicio(f"Mostre os múltiplos de {k} entre 1 e {ate}.",
                     f"for n in range({k}, {ate + 1}, {k}):\n    print(n)",
                     f"Usando range com passo {k}, começando em {k}, só passamos pelos múltiplos.")


def _ex_preco_com_quantidade(rng):
    produto, preco = rng.choice(PRODUTOS)
    q = rng.randint(2, 12)
    return exercicio(f"Uma unidade de {produto} custa R$ {preco:.2f}. Quanto custam {q} unidades?",
                     f'preco = {preco}\nquantidade = {q}\nprint(f"R$ {{preco * quantidade:.2f}}")',
                     f"Basta multiplicar o preço pela quantidade: R$ {preco * q:.2f}.")


def _ex_imc(rng):
    peso = rng.randint(45, 110)
    altura = rng.choice([1.50, 1.55, 1.60, 1.65, 1.70, 1.75, 1.80, 1.85, 1.90])
    return exercicio(f"Calcule o IMC de uma pessoa com {peso} kg e {altura} m de altura. IMC é o peso dividido pela altura ao quadrado.",
                     f"peso = {peso}\naltura = {altura}\nimc = peso / altura ** 2\nprint(round(imc, 1))",
                     f"A potência vem antes da divisão, então primeiro calculamos {altura} ao quadrado e depois dividimos {peso} por esse valor. O resultado é {round(peso / altura ** 2, 1)}.")
