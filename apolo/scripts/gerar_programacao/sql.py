"""SQL: lições + perguntas e respostas + exercícios. Cada comando roda de verdade (SQLite em memória; a parte
básica da linguagem é igual à do PostgreSQL). A saída mostra os nomes das colunas e uma linha por registro."""
from lib import exemplo_sql, exercicio_sql, qa, licao, NOMES, PRODUTOS, CIDADES

PRODUTOS_SQL = (
    "CREATE TABLE produtos (id INTEGER PRIMARY KEY, nome TEXT, preco REAL, estoque INTEGER);\n"
    "INSERT INTO produtos VALUES (1, 'arroz', 25.9, 10), (2, 'feijão', 8.5, 0), (3, 'café', 18.0, 7), (4, 'leite', 5.4, 30);\n"
)
ALUNOS_SQL = (
    "CREATE TABLE alunos (id INTEGER PRIMARY KEY, nome TEXT, turma TEXT, nota REAL);\n"
    "INSERT INTO alunos VALUES (1, 'Ana', 'A', 8.5), (2, 'Bruno', 'B', 6.0), (3, 'Carla', 'A', 9.5), (4, 'Diego', 'B', 7.0);\n"
)


def licoes():
    b = []
    b.append(licao(
        "O que é SQL",
        "SQL é a linguagem usada para conversar com bancos de dados.",
        "Um banco de dados relacional guarda os dados em tabelas, que têm colunas e linhas.",
        "PostgreSQL, MySQL e SQLite são bancos que usam SQL.",
        "Cada comando SQL termina com ponto e vírgula.",
    ))
    b.append(licao(
        "Criar tabela e inserir dados",
        "CREATE TABLE cria uma tabela, dizendo o nome de cada coluna e o tipo dela.",
        "INSERT INTO coloca uma linha nova na tabela.",
        "Tipos comuns: INTEGER para inteiros, TEXT para textos e REAL para números com vírgula.",
        "PRIMARY KEY marca a coluna que identifica cada linha de forma única.",
    ))
    b.append(exemplo_sql("Como criar uma tabela e inserir uma linha?",
                         "CREATE TABLE pessoas (id INTEGER PRIMARY KEY, nome TEXT, idade INTEGER);\nINSERT INTO pessoas VALUES (1, 'Ana', 20);\nSELECT * FROM pessoas;",
                         "CREATE TABLE criou a tabela, INSERT adicionou a Ana e SELECT * mostrou tudo o que existe nela."))
    b.append(licao(
        "SELECT",
        "SELECT busca dados de uma tabela. SELECT * traz todas as colunas.",
        "Para trazer só algumas colunas, escreva os nomes depois do SELECT, separados por vírgula.",
        "FROM diz de qual tabela os dados vêm.",
    ))
    b.append(exemplo_sql("Como escolher só algumas colunas?", PRODUTOS_SQL + "SELECT nome, preco FROM produtos;",
                         "O SELECT trouxe só as colunas nome e preco de cada produto."))
    b.append(licao(
        "WHERE",
        "WHERE filtra as linhas: só as que passam na condição aparecem.",
        "Os operadores são =, <>, >, <, >= e <=. Para combinar condições use AND, OR e NOT.",
        "LIKE procura um pedaço de texto, e o símbolo % significa qualquer coisa.",
    ))
    b.append(exemplo_sql("Como filtrar linhas com WHERE?", PRODUTOS_SQL + "SELECT nome, preco FROM produtos WHERE preco > 10;",
                         "Só arroz e café custam mais de 10, então só eles aparecem."))
    b.append(exemplo_sql("Como combinar duas condições?", PRODUTOS_SQL + "SELECT nome FROM produtos WHERE preco < 20 AND estoque > 0;",
                         "AND exige as duas condições: preço menor que 20 e estoque maior que zero. O feijão tem estoque zero e ficou de fora."))
    b.append(exemplo_sql("Como procurar por parte de um texto?", PRODUTOS_SQL + "SELECT nome FROM produtos WHERE nome LIKE 'a%';",
                         "LIKE 'a%' acha os nomes que começam com a."))
    b.append(licao(
        "ORDER BY e LIMIT",
        "ORDER BY ordena o resultado. ASC é do menor para o maior, e DESC do maior para o menor.",
        "LIMIT corta o resultado em um número máximo de linhas.",
    ))
    b.append(exemplo_sql("Como ordenar o resultado?", PRODUTOS_SQL + "SELECT nome, preco FROM produtos ORDER BY preco DESC;",
                         "DESC colocou o produto mais caro primeiro."))
    b.append(exemplo_sql("Como pegar só os dois primeiros?", PRODUTOS_SQL + "SELECT nome FROM produtos ORDER BY preco LIMIT 2;",
                         "Ordenado do mais barato para o mais caro, LIMIT 2 ficou com os dois primeiros."))
    b.append(licao(
        "Funções de agregação",
        "COUNT conta linhas, SUM soma, AVG tira a média, MIN acha o menor e MAX acha o maior.",
        "Elas resumem várias linhas num valor só.",
    ))
    b.append(exemplo_sql("Como contar e somar?", PRODUTOS_SQL + "SELECT COUNT(*), SUM(estoque), MAX(preco) FROM produtos;",
                         "COUNT(*) conta os produtos, SUM(estoque) soma o estoque de todos e MAX(preco) acha o preço mais alto."))
    b.append(exemplo_sql("Como calcular a média?", ALUNOS_SQL + "SELECT AVG(nota) FROM alunos;",
                         "AVG somou as quatro notas e dividiu por 4."))
    b.append(licao(
        "GROUP BY",
        "GROUP BY junta as linhas que têm o mesmo valor numa coluna e permite resumir cada grupo.",
        "Costuma ser usado junto com COUNT, SUM ou AVG.",
        "HAVING filtra os grupos, do mesmo jeito que WHERE filtra as linhas.",
    ))
    b.append(exemplo_sql("Como calcular a média de cada turma?", ALUNOS_SQL + "SELECT turma, AVG(nota) FROM alunos GROUP BY turma;",
                         "GROUP BY separou os alunos por turma, e AVG calculou a média de cada uma."))
    b.append(exemplo_sql("Como contar alunos por turma?", ALUNOS_SQL + "SELECT turma, COUNT(*) FROM alunos GROUP BY turma;",
                         "Cada turma tem dois alunos."))
    b.append(licao(
        "UPDATE e DELETE",
        "UPDATE muda valores de linhas que já existem. DELETE apaga linhas.",
        "Sempre use WHERE nos dois. Sem WHERE, o comando vale para a tabela inteira.",
    ))
    b.append(exemplo_sql("Como alterar um valor?", PRODUTOS_SQL + "UPDATE produtos SET preco = 9.0 WHERE nome = 'feijão';\nSELECT nome, preco FROM produtos WHERE nome = 'feijão';",
                         "UPDATE mudou o preço só da linha do feijão, porque o WHERE limitou o alvo."))
    b.append(exemplo_sql("Como apagar linhas?", PRODUTOS_SQL + "DELETE FROM produtos WHERE estoque = 0;\nSELECT nome FROM produtos;",
                         "DELETE apagou o feijão, que tinha estoque zero. Os outros ficaram."))
    b.append(licao(
        "JOIN",
        "JOIN junta linhas de duas tabelas usando uma coluna que as liga.",
        "Normalmente uma tabela guarda o id da outra, que se chama chave estrangeira.",
        "INNER JOIN traz só as linhas que têm par nas duas tabelas. LEFT JOIN traz todas as da esquerda, mesmo sem par.",
    ))
    b.append(exemplo_sql("Como juntar duas tabelas?",
                         "CREATE TABLE clientes (id INTEGER PRIMARY KEY, nome TEXT);\nCREATE TABLE pedidos (id INTEGER PRIMARY KEY, cliente_id INTEGER, valor REAL);\nINSERT INTO clientes VALUES (1, 'Ana'), (2, 'Bruno');\nINSERT INTO pedidos VALUES (1, 1, 50.0), (2, 1, 30.0), (3, 2, 20.0);\nSELECT clientes.nome, pedidos.valor FROM pedidos JOIN clientes ON clientes.id = pedidos.cliente_id;",
                         "O JOIN ligou cada pedido ao cliente pelo cliente_id, e o resultado mostra o nome ao lado do valor."))
    b.append(exemplo_sql("Como somar os pedidos de cada cliente?",
                         "CREATE TABLE clientes (id INTEGER PRIMARY KEY, nome TEXT);\nCREATE TABLE pedidos (id INTEGER PRIMARY KEY, cliente_id INTEGER, valor REAL);\nINSERT INTO clientes VALUES (1, 'Ana'), (2, 'Bruno');\nINSERT INTO pedidos VALUES (1, 1, 50.0), (2, 1, 30.0), (3, 2, 20.0);\nSELECT clientes.nome, SUM(pedidos.valor) FROM clientes JOIN pedidos ON clientes.id = pedidos.cliente_id GROUP BY clientes.nome;",
                         "O JOIN juntou as tabelas e o GROUP BY somou os pedidos de cada cliente: Ana 80 e Bruno 20."))
    b.append(licao(
        "Erros comuns em SQL",
        "Esquecer o WHERE num UPDATE ou DELETE muda ou apaga todas as linhas.",
        "Escrever o nome de uma coluna ou tabela errado dá erro de coluna ou tabela inexistente.",
        "Textos ficam entre aspas simples, como 'Ana'. Aspas duplas servem para nomes de colunas.",
    ))
    b.append(exemplo_sql("O que acontece se a tabela não existe?", "SELECT * FROM fantasma;",
                         "O banco avisa que a tabela fantasma não existe.", erro_esperado=True))
    b.append(exemplo_sql("O que acontece se a coluna não existe?", PRODUTOS_SQL + "SELECT cor FROM produtos;",
                         "A coluna cor não existe na tabela produtos, então o banco devolve um erro.", erro_esperado=True))
    b.append(licao(
        "PostgreSQL",
        "PostgreSQL, ou Postgres, é um banco de dados relacional livre e muito usado.",
        "O psql é o programa de terminal para conversar com ele. \\dt lista as tabelas e \\q sai.",
        "Em PostgreSQL, SERIAL cria um id que aumenta sozinho a cada linha nova.",
        "O Postgres também guarda JSON e, com a extensão pgvector, guarda vetores para buscar por semelhança.",
    ))
    return b


def perguntas():
    return [
        qa("O que é SQL?", "É a linguagem usada para conversar com bancos de dados relacionais."),
        qa("O que é um banco de dados relacional?", "É um banco que guarda os dados em tabelas, com colunas e linhas."),
        qa("O que faz o SELECT?", "Busca dados de uma ou mais tabelas."),
        qa("Para que serve o WHERE?", "Filtra as linhas, deixando só as que passam na condição."),
        qa("Como ordenar o resultado de um SELECT?", "Com ORDER BY. DESC ordena do maior para o menor."),
        qa("Para que serve o LIMIT?", "Limita o número de linhas que o SELECT devolve."),
        qa("O que é uma chave primária?", "É a coluna que identifica cada linha da tabela de forma única."),
        qa("O que é uma chave estrangeira?", "É uma coluna que guarda o id de uma linha de outra tabela, ligando as duas."),
        qa("O que faz o JOIN?", "Junta linhas de duas tabelas usando uma coluna em comum."),
        qa("Qual a diferença entre INNER JOIN e LEFT JOIN?", "INNER JOIN traz só as linhas com par nas duas tabelas. LEFT JOIN traz todas as da esquerda, mesmo sem par."),
        qa("Para que serve o GROUP BY?", "Agrupa linhas com o mesmo valor, para resumir cada grupo com COUNT, SUM ou AVG."),
        qa("Qual a diferença entre WHERE e HAVING?", "WHERE filtra as linhas antes de agrupar. HAVING filtra os grupos depois."),
        qa("Como contar as linhas de uma tabela?", "Com SELECT COUNT(*) FROM nome_da_tabela."),
        qa("Como inserir uma linha?", "Com INSERT INTO nome_da_tabela VALUES (...)."),
        qa("Como alterar dados?", "Com UPDATE nome_da_tabela SET coluna = valor WHERE condição."),
        qa("Como apagar linhas?", "Com DELETE FROM nome_da_tabela WHERE condição."),
        qa("Por que usar WHERE no UPDATE e no DELETE?", "Sem WHERE, o comando muda ou apaga todas as linhas da tabela."),
        qa("O que é o PostgreSQL?", "É um banco de dados relacional livre, poderoso e muito usado."),
        qa("O que é o pgvector?", "Uma extensão do PostgreSQL que guarda vetores e busca por semelhança."),
        qa("O que é um índice?", "Uma estrutura que acelera as buscas numa coluna, como o índice de um livro."),
        qa("Como listar as tabelas no psql?", "Com o comando \\dt."),
        qa("Como sair do psql?", "Com o comando \\q."),
        qa("O que é NULL?", "É a ausência de valor. Para testar, use IS NULL, e não = NULL."),
        qa("O que é o SQLite?", "Um banco de dados pequeno que fica num único arquivo, sem servidor."),
    ]


def exercicios(rng, n):
    familias = [_ex_filtro_preco, _ex_ordenar, _ex_contar, _ex_media_nota, _ex_agrupar_turma, _ex_update,
                _ex_delete, _ex_like, _ex_maximo, _ex_estoque_zero, _ex_criar_inserir, _ex_total_estoque]
    blocos = [familias[i % len(familias)](rng) for i in range(n)]
    rng.shuffle(blocos)
    return blocos


def _tabela_produtos(rng, k=5):
    itens = rng.sample(PRODUTOS, k)
    linhas = ", ".join(f"({i}, '{nome}', {preco}, {rng.randint(0, 40)})" for i, (nome, preco) in enumerate(itens, 1))
    return ("CREATE TABLE produtos (id INTEGER PRIMARY KEY, nome TEXT, preco REAL, estoque INTEGER);\n"
            f"INSERT INTO produtos VALUES {linhas};\n"), itens


def _tabela_alunos(rng, k=5):
    nomes = rng.sample(NOMES, k)
    linhas = ", ".join(f"({i}, '{nome}', '{rng.choice('AB')}', {round(rng.uniform(3, 10), 1)})" for i, nome in enumerate(nomes, 1))
    return ("CREATE TABLE alunos (id INTEGER PRIMARY KEY, nome TEXT, turma TEXT, nota REAL);\n"
            f"INSERT INTO alunos VALUES {linhas};\n")


def _ex_filtro_preco(rng):
    t, itens = _tabela_produtos(rng)
    corte = rng.choice([5, 8, 10, 20])
    return exercicio_sql(f"Mostre o nome e o preço dos produtos que custam mais de {corte}.",
                         t + f"SELECT nome, preco FROM produtos WHERE preco > {corte};",
                         f"WHERE preco > {corte} deixa só os produtos acima desse valor.")


def _ex_ordenar(rng):
    t, _ = _tabela_produtos(rng)
    sentido, texto = rng.choice([("DESC", "do mais caro para o mais barato"), ("ASC", "do mais barato para o mais caro")])
    return exercicio_sql(f"Liste os nomes dos produtos {texto}.",
                         t + f"SELECT nome FROM produtos ORDER BY preco {sentido};",
                         f"ORDER BY preco {sentido} ordena pelo preço.")


def _ex_contar(rng):
    t, itens = _tabela_produtos(rng, rng.randint(3, 6))
    return exercicio_sql("Conte quantos produtos existem na tabela.",
                         t + "SELECT COUNT(*) FROM produtos;",
                         f"COUNT(*) conta as linhas da tabela: {len(itens)}.")


def _ex_media_nota(rng):
    t = _tabela_alunos(rng)
    return exercicio_sql("Mostre a média das notas de todos os alunos.",
                         t + "SELECT AVG(nota) FROM alunos;",
                         "AVG soma as notas e divide pela quantidade de alunos.")


def _ex_agrupar_turma(rng):
    t = _tabela_alunos(rng, 6)
    return exercicio_sql("Mostre quantos alunos há em cada turma.",
                         t + "SELECT turma, COUNT(*) FROM alunos GROUP BY turma ORDER BY turma;",
                         "GROUP BY separa os alunos por turma e COUNT conta cada grupo.")


def _ex_update(rng):
    t, itens = _tabela_produtos(rng)
    nome = rng.choice(itens)[0]
    novo = round(rng.uniform(2, 40), 1)
    return exercicio_sql(f"Mude o preço de {nome} para {novo} e mostre o resultado.",
                         t + f"UPDATE produtos SET preco = {novo} WHERE nome = '{nome}';\nSELECT nome, preco FROM produtos WHERE nome = '{nome}';",
                         f"UPDATE com WHERE mudou só a linha de {nome}.")


def _ex_delete(rng):
    t, itens = _tabela_produtos(rng)
    nome = rng.choice(itens)[0]
    return exercicio_sql(f"Apague o produto {nome} e mostre os que sobraram.",
                         t + f"DELETE FROM produtos WHERE nome = '{nome}';\nSELECT nome FROM produtos;",
                         f"DELETE apagou só a linha de {nome}.")


def _ex_like(rng):
    t, itens = _tabela_produtos(rng, 6)
    letra = rng.choice([n[0] for n, _ in itens])
    return exercicio_sql(f"Mostre os produtos cujo nome começa com {letra}.",
                         t + f"SELECT nome FROM produtos WHERE nome LIKE '{letra}%';",
                         f"LIKE '{letra}%' acha os nomes que começam com {letra}.")


def _ex_maximo(rng):
    t, _ = _tabela_produtos(rng)
    return exercicio_sql("Mostre o menor e o maior preço da tabela.",
                         t + "SELECT MIN(preco), MAX(preco) FROM produtos;",
                         "MIN e MAX devolvem o menor e o maior valor da coluna.")


def _ex_estoque_zero(rng):
    t, _ = _tabela_produtos(rng, 6)
    return exercicio_sql("Liste os produtos com estoque acima de 10, do maior estoque para o menor.",
                         t + "SELECT nome, estoque FROM produtos WHERE estoque > 10 ORDER BY estoque DESC;",
                         "O WHERE filtra e o ORDER BY ordena o que sobrou.")


def _ex_criar_inserir(rng):
    cidades = rng.sample(CIDADES, 3)
    valores = ", ".join(f"({i}, '{c}')" for i, c in enumerate(cidades, 1))
    return exercicio_sql("Crie uma tabela cidades com id e nome, insira três cidades e mostre todas.",
                         f"CREATE TABLE cidades (id INTEGER PRIMARY KEY, nome TEXT);\nINSERT INTO cidades VALUES {valores};\nSELECT * FROM cidades;",
                         "CREATE TABLE criou a tabela, INSERT colocou as três linhas e SELECT * mostrou tudo.")


def _ex_total_estoque(rng):
    t, _ = _tabela_produtos(rng)
    return exercicio_sql("Some a quantidade em estoque de todos os produtos.",
                         t + "SELECT SUM(estoque) FROM produtos;",
                         "SUM soma os valores da coluna estoque.")
