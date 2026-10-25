"""JavaScript e Node: lições + perguntas e respostas + exercícios. Todo exemplo é executado no Node de verdade."""
from lib import exemplo_js, exercicio_js, qa, licao, NOMES, FRUTAS, PRODUTOS, CIDADES, PALAVRAS


def licoes():
    b = []
    b.append(licao(
        "O que é JavaScript",
        "JavaScript é uma linguagem de programação criada em 1995 para dar vida às páginas da web.",
        "Hoje ela roda também fora do navegador, no Node.js, e é usada em servidores, ferramentas e aplicativos.",
        "Para rodar um arquivo no Node, use o comando node arquivo.js.",
        "Em JavaScript, cada instrução costuma terminar com ponto e vírgula.",
    ))
    b.append(licao(
        "console.log",
        "console.log mostra um valor na tela, como o print do Python.",
        "Podemos passar vários valores separados por vírgula, e eles saem na mesma linha.",
    ))
    b.append(exemplo_js("Como mostrar uma mensagem em JavaScript?", 'console.log("Olá, mundo!");',
                        "console.log escreveu na tela o texto que estava entre aspas."))
    b.append(exemplo_js("Como mostrar vários valores de uma vez?", 'console.log("Idade:", 20, true);',
                        "Os valores separados por vírgula saem na mesma linha, com um espaço entre eles."))
    b.append(licao(
        "Variáveis com let e const",
        "let cria uma variável que pode mudar de valor depois.",
        "const cria uma constante: o valor não pode ser trocado por outro.",
        "Hoje quase ninguém usa var, que é o jeito antigo e tem regras confusas.",
        "Use const por padrão e let só quando o valor precisar mudar.",
    ))
    b.append(exemplo_js("Como criar variáveis em JavaScript?", 'let idade = 20;\nconst nome = "Ana";\nidade = 21;\nconsole.log(nome, idade);',
                        "idade foi criada com let e depois mudou para 21. nome é const e ficou sempre Ana."))
    b.append(exemplo_js("O que acontece se mudar uma const?", 'const pi = 3.14;\npi = 3;',
                        "Atribuir de novo a uma const dá TypeError, porque ela não pode ser reatribuída.", erro_esperado=True))
    b.append(licao(
        "Tipos de dados",
        "Os tipos básicos são number para números, string para textos e boolean para verdadeiro ou falso.",
        "undefined é o valor de uma variável que ainda não recebeu nada. null é um valor vazio de propósito.",
        "O operador typeof mostra o tipo de um valor.",
        "Em JavaScript não existe separação entre inteiro e decimal: todo número é number.",
    ))
    b.append(exemplo_js("Como descobrir o tipo de um valor?", 'console.log(typeof 42);\nconsole.log(typeof 3.5);\nconsole.log(typeof "oi");\nconsole.log(typeof true);\nconsole.log(typeof undefined);',
                        "typeof devolve o nome do tipo. Inteiros e decimais são os dois number."))
    b.append(exemplo_js("Qual a diferença entre == e === ?", 'console.log(5 == "5");\nconsole.log(5 === "5");\nconsole.log(5 === 5);',
                        "== converte os tipos antes de comparar, então 5 e o texto 5 parecem iguais. === compara valor e tipo, por isso é o mais seguro."))
    b.append(licao(
        "Strings e template literals",
        "Textos ficam entre aspas simples, duplas ou crases.",
        "Com crases podemos colocar valores no meio do texto usando ${expressão}. Isso se chama template literal.",
        "O atributo length diz o tamanho do texto, e métodos como toUpperCase e includes ajudam a trabalhar com ele.",
    ))
    b.append(exemplo_js("Como colocar uma variável dentro de um texto?", 'const nome = "Ana";\nconst idade = 20;\nconsole.log(`${nome} tem ${idade} anos.`);',
                        "Entre crases, o que está dentro de ${} é calculado e entra no texto."))
    b.append(exemplo_js("Como usar métodos de string?", 'const frase = "programar é bom";\nconsole.log(frase.length);\nconsole.log(frase.toUpperCase());\nconsole.log(frase.includes("bom"));\nconsole.log(frase.split(" "));',
                        "length conta os caracteres, toUpperCase deixa tudo maiúsculo, includes procura um pedaço e split quebra o texto numa lista."))
    b.append(licao(
        "Condicionais",
        "if executa um bloco só quando a condição é verdadeira. else cobre o caso contrário, e else if testa outra condição.",
        "Os blocos ficam entre chaves.",
        "Operadores lógicos: && é e, || é ou, ! é não.",
    ))
    b.append(exemplo_js("Como usar if e else?", 'const nota = 7;\nif (nota >= 7) {\n  console.log("Aprovado");\n} else {\n  console.log("Reprovado");\n}',
                        "A nota é 7, então a condição nota >= 7 é verdadeira e o primeiro bloco roda."))
    b.append(exemplo_js("Como combinar condições?", 'const idade = 20;\nconst temCarteira = true;\nif (idade >= 18 && temCarteira) {\n  console.log("Pode dirigir");\n}',
                        "&& exige que as duas condições sejam verdadeiras."))
    b.append(licao(
        "Repetição com for e while",
        "for repete um bloco com um contador: for (let i = 0; i < 5; i++).",
        "while repete enquanto a condição for verdadeira.",
        "for...of percorre os itens de uma lista, um de cada vez.",
        "i++ soma 1 ao contador.",
    ))
    b.append(exemplo_js("Como repetir algo 5 vezes?", 'for (let i = 0; i < 5; i++) {\n  console.log(i);\n}',
                        "i começa em 0 e o laço roda enquanto i < 5, então mostra de 0 a 4."))
    b.append(exemplo_js("Como percorrer uma lista com for...of?", 'const frutas = ["maçã", "uva", "pera"];\nfor (const fruta of frutas) {\n  console.log(fruta);\n}',
                        "A cada volta, fruta recebe o próximo item da lista."))
    b.append(exemplo_js("Como usar while?", 'let n = 3;\nwhile (n > 0) {\n  console.log(n);\n  n--;\n}\nconsole.log("Fim!");',
                        "n começa em 3 e diminui 1 a cada volta. Quando chega a 0, o laço para."))
    b.append(licao(
        "Arrays",
        "Um array é uma lista de valores entre colchetes, com posições que começam em 0.",
        "push adiciona no fim, pop remove do fim, e length diz quantos itens existem.",
        "Os métodos map, filter e reduce transformam arrays sem precisar de for.",
        "map cria um novo array aplicando uma função a cada item. filter guarda só os itens que passam num teste. reduce junta tudo num valor só.",
    ))
    b.append(exemplo_js("Como criar e mexer num array?", 'const nums = [10, 20, 30];\nnums.push(40);\nconsole.log(nums);\nconsole.log(nums[0]);\nconsole.log(nums.length);\nnums.pop();\nconsole.log(nums);',
                        "push colocou 40 no fim, nums[0] é o primeiro item, length vale 4 e pop tirou o 40."))
    b.append(exemplo_js("Como usar map?", 'const nums = [1, 2, 3, 4];\nconst dobros = nums.map((n) => n * 2);\nconsole.log(dobros);',
                        "map aplicou a função n => n * 2 em cada item e devolveu um array novo."))
    b.append(exemplo_js("Como usar filter?", 'const nums = [1, 2, 3, 4, 5, 6];\nconst pares = nums.filter((n) => n % 2 === 0);\nconsole.log(pares);',
                        "filter ficou só com os números que passaram no teste n % 2 === 0, os pares."))
    b.append(exemplo_js("Como usar reduce?", 'const nums = [1, 2, 3, 4];\nconst soma = nums.reduce((total, n) => total + n, 0);\nconsole.log(soma);',
                        "reduce começa com total valendo 0 e soma cada número, chegando a 10."))
    b.append(licao(
        "Objetos",
        "Um objeto guarda pares de chave e valor entre chaves, como um dicionário do Python.",
        "Acessamos um valor com ponto, como pessoa.nome, ou com colchetes, como pessoa['nome'].",
        "Object.keys, Object.values e Object.entries listam as chaves, os valores e os pares.",
    ))
    b.append(exemplo_js("Como criar e usar um objeto?", 'const pessoa = { nome: "Ana", idade: 20 };\nconsole.log(pessoa.nome);\npessoa.cidade = "Vilhena";\nconsole.log(pessoa);',
                        "pessoa.nome lê um valor. Atribuir a pessoa.cidade criou uma chave nova."))
    b.append(exemplo_js("Como listar as chaves de um objeto?", 'const carro = { marca: "Fiat", ano: 2020 };\nconsole.log(Object.keys(carro));\nconsole.log(Object.values(carro));\nconsole.log(Object.entries(carro));',
                        "keys devolve as chaves, values os valores e entries os pares [chave, valor]."))
    b.append(licao(
        "Funções",
        "Uma função é um bloco de código com nome que podemos chamar quantas vezes quisermos.",
        "function nome(parametros) { ... } cria uma função, e return devolve um resultado.",
        "Arrow function é um jeito curto de escrever: (a, b) => a + b.",
    ))
    b.append(exemplo_js("Como criar uma função?", 'function somar(a, b) {\n  return a + b;\n}\nconsole.log(somar(3, 4));',
                        "somar recebe dois valores e devolve a soma deles com return."))
    b.append(exemplo_js("O que é uma arrow function?", 'const dobro = (n) => n * 2;\nconsole.log(dobro(5));\nconsole.log([1, 2, 3].map(dobro));',
                        "A arrow function é uma função curta. Aqui ela foi guardada numa const e usada também dentro do map."))
    b.append(licao(
        "Desestruturação e spread",
        "Desestruturar é tirar valores de um array ou objeto direto para variáveis.",
        "O spread, com três pontos, espalha os itens de um array ou objeto dentro de outro.",
    ))
    b.append(exemplo_js("Como desestruturar um array e um objeto?", 'const [a, b] = [10, 20];\nconst { nome, idade } = { nome: "Ana", idade: 20 };\nconsole.log(a, b);\nconsole.log(nome, idade);',
                        "No array, as variáveis pegam os itens por posição. No objeto, pegam os valores pelo nome da chave."))
    b.append(exemplo_js("Como copiar e juntar arrays com spread?", 'const a = [1, 2];\nconst b = [3, 4];\nconst juntos = [...a, ...b, 5];\nconsole.log(juntos);',
                        "Os três pontos espalharam os itens de a e b dentro do array novo."))
    b.append(licao(
        "Classes",
        "Uma classe é um molde para criar objetos com os mesmos dados e comportamentos.",
        "O constructor roda quando criamos o objeto com new, e this se refere ao objeto atual.",
        "Funções dentro da classe são chamadas de métodos.",
    ))
    b.append(exemplo_js("Como criar uma classe?", 'class Pessoa {\n  constructor(nome) {\n    this.nome = nome;\n  }\n  apresentar() {\n    return `Oi, eu sou ${this.nome}`;\n  }\n}\nconst ana = new Pessoa("Ana");\nconsole.log(ana.apresentar());',
                        "new Pessoa cria um objeto e chama o constructor. O método apresentar usa this.nome."))
    b.append(licao(
        "Erros com try e catch",
        "try tenta executar um bloco. Se der erro, o catch roda no lugar de parar o programa.",
        "throw lança um erro de propósito, e finally roda sempre, com erro ou sem.",
    ))
    b.append(exemplo_js("Como tratar um erro?", 'try {\n  JSON.parse("isto não é json");\n} catch (e) {\n  console.log("Deu erro:", e.name);\n}\nconsole.log("O programa continua");',
                        "JSON.parse falhou, o catch tratou o erro e o programa seguiu em frente."))
    b.append(licao(
        "JSON",
        "JSON é um formato de texto para trocar dados entre programas, parecido com objetos do JavaScript.",
        "JSON.stringify transforma um objeto em texto, e JSON.parse transforma o texto de volta em objeto.",
    ))
    b.append(exemplo_js("Como converter um objeto para JSON e voltar?", 'const dados = { nome: "Ana", notas: [8, 9] };\nconst texto = JSON.stringify(dados);\nconsole.log(texto);\nconst volta = JSON.parse(texto);\nconsole.log(volta.notas[1]);',
                        "stringify gerou o texto. parse recriou o objeto, e volta.notas[1] é o segundo número."))
    b.append(licao(
        "Promises e async/await",
        "Uma Promise representa um resultado que ainda vai chegar, como uma resposta de um servidor.",
        "async marca uma função que usa await, e await espera a Promise terminar antes de seguir.",
        "Assim o código assíncrono fica quase tão fácil de ler quanto o normal.",
    ))
    b.append(exemplo_js("Como usar async e await?", 'const esperar = (ms) => new Promise((ok) => setTimeout(ok, ms));\nasync function main() {\n  console.log("Começou");\n  await esperar(10);\n  console.log("Passou um tempo");\n}\nawait main();',
                        "await esperar(10) pausou a função main até a Promise terminar, e só depois a segunda mensagem apareceu."))
    b.append(licao(
        "Node.js e módulos",
        "Node.js roda JavaScript fora do navegador. Com ele criamos servidores, scripts e ferramentas.",
        "npm é o gerenciador de pacotes: npm install instala bibliotecas e npm start roda o projeto.",
        "Um módulo é um arquivo que exporta coisas com export e é usado em outro com import.",
        "O arquivo package.json guarda o nome do projeto, as dependências e os scripts.",
        "O Express é uma biblioteca popular para criar servidores web em Node.",
    ))
    return b


def perguntas():
    return [
        qa("O que é JavaScript?", "Uma linguagem de programação criada para a web, que hoje também roda no servidor com o Node.js."),
        qa("O que é Node.js?", "É o ambiente que roda JavaScript fora do navegador, usado em servidores e ferramentas."),
        qa("Para que serve o npm?", "O npm instala e gerencia as bibliotecas de um projeto Node."),
        qa("Qual a diferença entre let e const?", "let cria uma variável que pode mudar. const cria uma constante que não pode ser reatribuída."),
        qa("Como mostrar algo na tela em JavaScript?", "Com console.log, por exemplo console.log('Olá')."),
        qa("O que é um array?", "É uma lista de valores entre colchetes, com posições que começam em 0."),
        qa("O que faz o map?", "Cria um novo array aplicando uma função a cada item do array original."),
        qa("O que faz o filter?", "Cria um novo array só com os itens que passam num teste."),
        qa("O que faz o reduce?", "Junta todos os itens de um array num único valor, como uma soma."),
        qa("O que é uma arrow function?", "Um jeito curto de escrever funções, com a seta =>."),
        qa("O que é um objeto em JavaScript?", "Uma coleção de pares de chave e valor entre chaves."),
        qa("O que é JSON?", "Um formato de texto para trocar dados, parecido com um objeto do JavaScript."),
        qa("Como converter JSON em objeto?", "Com JSON.parse. Para o caminho contrário, use JSON.stringify."),
        qa("O que é uma Promise?", "Um resultado que ainda vai chegar, como a resposta de um servidor."),
        qa("Para que serve o await?", "Espera uma Promise terminar antes de continuar o código."),
        qa("Qual a diferença entre == e ===?", "== converte os tipos antes de comparar. === compara valor e tipo, e é o mais seguro."),
        qa("O que é undefined?", "É o valor de uma variável que ainda não recebeu nenhum valor."),
        qa("O que é null?", "É um valor vazio colocado de propósito."),
        qa("O que é uma classe?", "Um molde para criar objetos com os mesmos dados e métodos."),
        qa("Para que serve o try e catch?", "Para tratar um erro sem derrubar o programa."),
        qa("O que é o Express?", "Uma biblioteca do Node para criar servidores web e APIs."),
        qa("O que é o package.json?", "O arquivo que guarda o nome, as dependências e os scripts de um projeto Node."),
        qa("Como instalar uma biblioteca no Node?", "Com npm install nome-da-biblioteca."),
        qa("Como rodar um arquivo JavaScript no Node?", "Com o comando node arquivo.js."),
        qa("Como somar 1 a uma variável?", "Com i++ ou i += 1."),
        qa("Como saber o tamanho de um array?", "Com a propriedade length, por exemplo nums.length."),
        qa("Como juntar dois arrays?", "Com o spread: [...a, ...b]."),
    ]


def exercicios(rng, n):
    familias = [_ex_soma, _ex_dobros, _ex_pares, _ex_soma_array, _ex_maior, _ex_template, _ex_contagem_for,
                _ex_objeto, _ex_filtrar_objetos, _ex_funcao_area, _ex_inverter, _ex_palindromo, _ex_fatorial,
                _ex_media, _ex_contar_palavras, _ex_total_compras, _ex_ordenar, _ex_includes, _ex_json,
                _ex_classe, _ex_while, _ex_somar_precos, _ex_fizz, _ex_unicos]
    blocos = [familias[i % len(familias)](rng) for i in range(n)]
    rng.shuffle(blocos)
    return blocos


def _nums(rng, k=None, lo=1, hi=30):
    return [rng.randint(lo, hi) for _ in range(k or rng.randint(4, 7))]


def _ex_soma(rng):
    a, b = rng.randint(1, 300), rng.randint(1, 300)
    return exercicio_js(f"Declare duas constantes, a valendo {a} e b valendo {b}, e mostre a soma.",
                        f"const a = {a};\nconst b = {b};\nconsole.log(a + b);",
                        f"a + b dá {a + b}.")


def _ex_dobros(rng):
    xs = _nums(rng)
    return exercicio_js(f"Use map para dobrar cada número do array {xs}.",
                        f"const nums = {xs};\nconsole.log(nums.map((n) => n * 2));",
                        "map devolve um array novo com cada número multiplicado por 2.")


def _ex_pares(rng):
    xs = _nums(rng, 8)
    return exercicio_js(f"Use filter para pegar só os números pares de {xs}.",
                        f"const nums = {xs};\nconsole.log(nums.filter((n) => n % 2 === 0));",
                        "n % 2 === 0 é verdadeiro quando o resto da divisão por 2 é zero, ou seja, o número é par.")


def _ex_soma_array(rng):
    xs = _nums(rng)
    return exercicio_js(f"Some todos os números de {xs} com reduce.",
                        f"const nums = {xs};\nconsole.log(nums.reduce((total, n) => total + n, 0));",
                        f"reduce começa em 0 e vai somando cada número. O total é {sum(xs)}.")


def _ex_maior(rng):
    xs = _nums(rng)
    return exercicio_js(f"Mostre o maior número do array {xs}.",
                        f"const nums = {xs};\nconsole.log(Math.max(...nums));",
                        f"O spread espalha os números dentro de Math.max, que devolve o maior: {max(xs)}.")


def _ex_template(rng):
    nome, cidade, idade = rng.choice(NOMES), rng.choice(CIDADES), rng.randint(15, 60)
    return exercicio_js(f"Mostre a frase '{nome} tem {idade} anos e mora em {cidade}.' usando variáveis e template literal.",
                        f'const nome = "{nome}";\nconst idade = {idade};\nconst cidade = "{cidade}";\nconsole.log(`${{nome}} tem ${{idade}} anos e mora em ${{cidade}}.`);',
                        "Os valores das variáveis entram no texto pelo ${} dentro das crases.")


def _ex_contagem_for(rng):
    a = rng.randint(1, 5)
    b = a + rng.randint(3, 7)
    return exercicio_js(f"Mostre os números de {a} até {b} usando for.",
                        f"for (let i = {a}; i <= {b}; i++) {{\n  console.log(i);\n}}",
                        f"i começa em {a} e o laço continua enquanto i <= {b}.")


def _ex_objeto(rng):
    nome, cidade, idade = rng.choice(NOMES), rng.choice(CIDADES), rng.randint(15, 60)
    return exercicio_js(f"Crie um objeto pessoa com nome {nome}, idade {idade} e cidade {cidade}, e mostre o objeto.",
                        f'const pessoa = {{ nome: "{nome}", idade: {idade}, cidade: "{cidade}" }};\nconsole.log(pessoa);',
                        "O console.log do Node mostra o objeto com as chaves e os valores.")


def _ex_filtrar_objetos(rng):
    nomes = rng.sample(NOMES, 4)
    idades = [rng.randint(10, 40) for _ in nomes]
    itens = ", ".join(f'{{ nome: "{n}", idade: {i} }}' for n, i in zip(nomes, idades))
    corte = 18
    return exercicio_js(f"Dada a lista de pessoas, mostre só os nomes de quem tem {corte} anos ou mais.",
                        f"const pessoas = [{itens}];\nconst adultos = pessoas.filter((p) => p.idade >= {corte});\nconsole.log(adultos.map((p) => p.nome));",
                        "filter ficou com os adultos, e map pegou só o nome de cada um.")


def _ex_funcao_area(rng):
    l, a = rng.randint(2, 20), rng.randint(2, 20)
    return exercicio_js(f"Escreva uma função que calcula a área de um retângulo e use com {l} e {a}.",
                        f"function area(largura, altura) {{\n  return largura * altura;\n}}\nconsole.log(area({l}, {a}));",
                        f"A área é largura vezes altura: {l} * {a} = {l * a}.")


def _ex_inverter(rng):
    p = rng.choice(PALAVRAS)
    return exercicio_js(f"Inverta o texto {p}.",
                        f'const palavra = "{p}";\nconsole.log(palavra.split("").reverse().join(""));',
                        "split quebra em letras, reverse inverte a ordem e join junta de novo.")


def _ex_palindromo(rng):
    p = rng.choice(["arara", "osso", "radar", "casa", "livro", "ovo", "mesa", "reviver"])
    return exercicio_js(f"Diga se {p} é um palíndromo.",
                        f'const palavra = "{p}";\nconst invertida = palavra.split("").reverse().join("");\nconsole.log(palavra === invertida);',
                        "Um palíndromo é igual de trás para frente. A comparação mostra true ou false.")


def _ex_fatorial(rng):
    n = rng.randint(3, 10)
    f = 1
    for i in range(2, n + 1):
        f *= i
    return exercicio_js(f"Calcule o fatorial de {n} com um for.",
                        f"let resultado = 1;\nfor (let i = 2; i <= {n}; i++) {{\n  resultado *= i;\n}}\nconsole.log(resultado);",
                        f"O fatorial de {n} é o produto de 1 até {n}, que dá {f}.")


def _ex_media(rng):
    xs = _nums(rng, 5, 0, 10)
    return exercicio_js(f"Calcule a média das notas {xs}.",
                        f"const notas = {xs};\nconst soma = notas.reduce((t, n) => t + n, 0);\nconsole.log(soma / notas.length);",
                        f"A soma é {sum(xs)} e são {len(xs)} notas.")


def _ex_contar_palavras(rng):
    ps = [rng.choice(PALAVRAS) for _ in range(rng.randint(3, 6))]
    frase = " ".join(ps)
    return exercicio_js(f"Conte quantas palavras tem a frase '{frase}'.",
                        f'const frase = "{frase}";\nconsole.log(frase.split(" ").length);',
                        "split(' ') separa a frase nos espaços, e length conta as partes.")


def _ex_total_compras(rng):
    itens = rng.sample(PRODUTOS, 3)
    lista = ", ".join(f'{{ nome: "{n}", preco: {p} }}' for n, p in itens)
    return exercicio_js("Some o preço de todos os produtos do carrinho.",
                        f"const carrinho = [{lista}];\nconst total = carrinho.reduce((soma, item) => soma + item.preco, 0);\nconsole.log(total.toFixed(2));",
                        "reduce soma o preço de cada item, e toFixed(2) deixa duas casas decimais.")


def _ex_ordenar(rng):
    xs = rng.sample(range(1, 60), rng.randint(5, 7))
    return exercicio_js(f"Ordene do menor para o maior os números {xs}.",
                        f"const nums = {xs};\nnums.sort((a, b) => a - b);\nconsole.log(nums);",
                        "sort sem função ordena como texto. Com (a, b) => a - b, ordena como número.")


def _ex_includes(rng):
    fr = rng.sample(FRUTAS, 4)
    procurada = rng.choice(fr + [rng.choice(FRUTAS)])
    return exercicio_js(f"Diga se a lista {fr} tem a fruta {procurada}.",
                        f"const frutas = {fr};\nconsole.log(frutas.includes(\"{procurada}\"));".replace("'", '"'),
                        "includes devolve true se o item está na lista e false se não está.")


def _ex_json(rng):
    nome, idade = rng.choice(NOMES), rng.randint(15, 60)
    return exercicio_js(f"Converta o objeto de {nome} em texto JSON.",
                        f'const pessoa = {{ nome: "{nome}", idade: {idade} }};\nconsole.log(JSON.stringify(pessoa));',
                        "stringify transforma o objeto em texto JSON, com as chaves entre aspas.")


def _ex_classe(rng):
    nome = rng.choice(NOMES)
    saldo, dep = rng.randint(50, 500), rng.randint(10, 200)
    return exercicio_js(f"Crie uma classe Conta com saldo e um método depositar. Depois deposite {dep} numa conta de {nome} com saldo {saldo}.",
                        f'class Conta {{\n  constructor(dono, saldo) {{\n    this.dono = dono;\n    this.saldo = saldo;\n  }}\n  depositar(valor) {{\n    this.saldo += valor;\n  }}\n}}\nconst conta = new Conta("{nome}", {saldo});\nconta.depositar({dep});\nconsole.log(conta.saldo);',
                        f"O saldo era {saldo}, depositou {dep} e ficou {saldo + dep}.")


def _ex_while(rng):
    n = rng.randint(3, 9)
    return exercicio_js(f"Faça uma contagem regressiva de {n} até 1 com while.",
                        f"let n = {n};\nwhile (n >= 1) {{\n  console.log(n);\n  n--;\n}}",
                        f"n começa em {n} e diminui até chegar a 1.")


def _ex_somar_precos(rng):
    preco, qtd = rng.choice(PRODUTOS)[1], rng.randint(2, 6)
    return exercicio_js(f"Calcule o total de {qtd} itens que custam {preco} cada.",
                        f"const preco = {preco};\nconst quantidade = {qtd};\nconsole.log((preco * quantidade).toFixed(2));",
                        "O total é preço vezes quantidade, com duas casas decimais.")


def _ex_fizz(rng):
    n = rng.randint(5, 15)
    return exercicio_js(f"Para os números de 1 até {n}, mostre Fizz se for múltiplo de 3 e o próprio número nos outros casos.",
                        f'for (let i = 1; i <= {n}; i++) {{\n  if (i % 3 === 0) {{\n    console.log("Fizz");\n  }} else {{\n    console.log(i);\n  }}\n}}',
                        "i % 3 === 0 é verdadeiro nos múltiplos de 3.")


def _ex_unicos(rng):
    xs = [rng.randint(1, 6) for _ in range(rng.randint(7, 10))]
    return exercicio_js(f"Remova os repetidos do array {xs}.",
                        f"const nums = {xs};\nconsole.log([...new Set(nums)]);",
                        "Um Set guarda cada valor uma só vez, e o spread transforma o Set de volta num array.")
