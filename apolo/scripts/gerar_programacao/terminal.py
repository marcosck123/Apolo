"""Terminal (bash), Git e Docker. Os comandos de terminal e de Git são executados de verdade numa pasta nova.
Docker não roda aqui, então as lições de Docker não têm saída."""
from lib import exemplo_shell, exercicio_shell, qa, licao, NOMES, PALAVRAS, FRUTAS, CIDADES


def licoes():
    b = []
    b.append(licao(
        "O que é o terminal",
        "O terminal é uma janela onde digitamos comandos em texto para o computador executar.",
        "O programa que interpreta os comandos se chama shell. O mais comum no Linux é o bash.",
        "O terminal sempre está dentro de uma pasta, chamada de diretório atual.",
    ))
    b.append(exemplo_shell("Como ver em que pasta estou?", "pwd",
                           "pwd mostra o caminho completo da pasta atual."))
    b.append(licao(
        "Navegar e listar",
        "ls lista os arquivos da pasta. cd entra em outra pasta. cd .. volta uma pasta.",
        "mkdir cria uma pasta e touch cria um arquivo vazio.",
        "ls -a mostra também os arquivos escondidos, que começam com ponto.",
    ))
    b.append(exemplo_shell("Como criar pastas e arquivos?", "mkdir projeto\ntouch projeto/a.txt projeto/b.txt\nls projeto",
                           "mkdir criou a pasta, touch criou dois arquivos dentro dela e ls listou o conteúdo."))
    b.append(exemplo_shell("Como entrar numa pasta e voltar?", "mkdir docs\ncd docs\npwd\ncd ..\npwd",
                           "cd docs entrou na pasta docs. cd .. voltou para a pasta de cima."))
    b.append(exemplo_shell("Como ver arquivos escondidos?", "touch .segredo visivel.txt\nls\nls -a",
                           "ls não mostra o .segredo. ls -a mostra todos, inclusive . e .., que são a pasta atual e a de cima."))
    b.append(licao(
        "Ler e escrever arquivos",
        "echo escreve um texto. O símbolo > manda a saída para um arquivo, apagando o que havia. O símbolo >> acrescenta no fim.",
        "cat mostra o conteúdo de um arquivo. head mostra as primeiras linhas e tail as últimas.",
        "wc -l conta as linhas de um arquivo.",
    ))
    b.append(exemplo_shell("Como escrever num arquivo?", 'echo "primeira linha" > nota.txt\necho "segunda linha" >> nota.txt\ncat nota.txt',
                           "O > criou o arquivo com a primeira linha. O >> acrescentou a segunda, e cat mostrou tudo."))
    b.append(exemplo_shell("Como contar as linhas de um arquivo?", 'printf "a\\nb\\nc\\n" > letras.txt\nwc -l letras.txt',
                           "wc -l conta as linhas. O arquivo tem 3."))
    b.append(exemplo_shell("Como ver só o começo de um arquivo?", 'printf "1\\n2\\n3\\n4\\n5\\n" > numeros.txt\nhead -n 2 numeros.txt\ntail -n 2 numeros.txt',
                           "head -n 2 mostra as duas primeiras linhas e tail -n 2 as duas últimas."))
    b.append(licao(
        "Copiar, mover e apagar",
        "cp copia um arquivo, mv move ou renomeia, e rm apaga.",
        "rm não manda para a lixeira: o arquivo some de vez. Para apagar uma pasta com tudo dentro use rm -r.",
        "Cuidado com rm -r: não existe desfazer.",
    ))
    b.append(exemplo_shell("Como copiar, renomear e apagar um arquivo?", "touch a.txt\ncp a.txt b.txt\nmv b.txt c.txt\nls\nrm a.txt\nls",
                           "cp fez a cópia b.txt, mv renomeou para c.txt e rm apagou o a.txt."))
    b.append(licao(
        "Buscar texto e pipes",
        "grep procura linhas que contêm um texto.",
        "O pipe, que é o símbolo |, passa a saída de um comando como entrada do próximo.",
        "sort ordena as linhas e uniq remove as repetidas que estão juntas.",
    ))
    b.append(exemplo_shell("Como procurar um texto num arquivo?", 'printf "maçã\\nbanana\\nmaracujá\\n" > frutas.txt\ngrep "ma" frutas.txt',
                           "grep mostrou só as linhas que têm ma."))
    b.append(exemplo_shell("Como usar o pipe?", 'printf "uva\\npera\\nuva\\nfigo\\n" | sort | uniq',
                           "A saída do printf entrou no sort, que ordenou, e depois no uniq, que tirou a repetição."))
    b.append(exemplo_shell("Como contar quantas vezes uma palavra aparece?", 'printf "sim\\nnão\\nsim\\nsim\\n" | grep -c "sim"',
                           "grep -c conta as linhas que têm sim."))
    b.append(licao(
        "Permissões e variáveis",
        "Cada arquivo tem permissões de leitura, escrita e execução. chmod muda essas permissões.",
        "chmod +x script.sh torna o arquivo executável.",
        "Variáveis do shell são criadas com nome=valor, sem espaços, e lidas com $nome.",
        "sudo executa um comando como administrador. Use com cuidado.",
    ))
    b.append(exemplo_shell("Como usar uma variável no shell?", 'nome="Ana"\necho "Olá, $nome!"',
                           "A variável nome guarda Ana, e $nome dentro das aspas duplas é trocado pelo valor."))
    b.append(exemplo_shell("Como rodar um script?", 'echo \'echo "Rodou o script"\' > teste.sh\nchmod +x teste.sh\n./teste.sh',
                           "chmod +x deu permissão de execução, e ./teste.sh executou o arquivo."))
    b.append(licao(
        "O que é o Git",
        "Git é um sistema que guarda a história de um projeto: cada versão salva se chama commit.",
        "Com o Git dá para voltar no tempo, ver o que mudou e trabalhar em equipe sem pisar no trabalho dos outros.",
        "GitHub é um site que guarda repositórios Git na internet.",
        "Um repositório é a pasta do projeto junto com a sua história.",
    ))
    b.append(exemplo_shell("Como começar um repositório Git?", "git init -b main\ngit status",
                           "git init criou o repositório na branch main. git status mostra que ainda não há commits."))
    b.append(licao(
        "O ciclo básico do Git",
        "Editamos arquivos, usamos git add para escolher o que entra no próximo commit e git commit para salvar.",
        "git status mostra o que mudou, e git log mostra a história de commits.",
        "A mensagem do commit explica o que mudou, com -m.",
    ))
    b.append(exemplo_shell("Como salvar a primeira versão com Git?", 'git init -q -b main\necho "# Meu projeto" > README.md\ngit add README.md\ngit commit -q -m "Primeiro commit"\ngit log --format=%s',
                           "git add colocou o README na lista do commit, git commit salvou a versão e git log mostrou a mensagem."))
    b.append(exemplo_shell("Como ver o que mudou antes de fazer o commit?", 'git init -q -b main\necho "a" > x.txt\ngit add x.txt\ngit commit -q -m "x"\necho "b" >> x.txt\ngit status --short\ngit diff',
                           "status --short mostra M para arquivo modificado. git diff mostra as linhas novas com + na frente."))
    b.append(exemplo_shell("Como ver a história dos commits?", 'git init -q -b main\nfor n in um dois tres; do echo $n > $n.txt; git add .; git commit -q -m "Adiciona $n"; done\ngit log --format=%s',
                           "git log lista os commits, do mais novo para o mais antigo."))
    b.append(licao(
        "Branches",
        "Uma branch é uma linha paralela de trabalho. Assim testamos uma ideia sem mexer na versão principal.",
        "git branch lista as branches, git switch -c nome cria e entra numa nova, e git merge junta uma branch na atual.",
    ))
    b.append(exemplo_shell("Como criar uma branch?", 'git init -q -b main\ngit commit -q --allow-empty -m "inicio"\ngit switch -c nova-ideia\ngit branch',
                           "switch -c criou a branch nova-ideia e entrou nela. git branch lista as branches e marca a atual com asterisco."))
    b.append(exemplo_shell("Como juntar uma branch na principal?", 'git init -q -b main\ngit commit -q --allow-empty -m "inicio"\ngit switch -q -c recurso\necho "novo" > recurso.txt\ngit add .\ngit commit -q -m "recurso"\ngit switch -q main\ngit merge -q recurso\nls',
                           "O merge trouxe o arquivo recurso.txt da branch recurso para a main."))
    b.append(licao(
        "GitHub e repositórios remotos",
        "Um remoto é uma cópia do repositório em outro lugar, como o GitHub. O nome padrão dele é origin.",
        "git clone baixa um repositório. git push envia os commits e git pull traz os que faltam.",
        "O arquivo .gitignore lista o que o Git deve ignorar, como node_modules e senhas.",
        "Nunca coloque senhas ou chaves de API num repositório, porque a história guarda tudo.",
    ))
    b.append(licao(
        "O que é o Docker",
        "Docker roda programas dentro de containers, que são caixas isoladas com tudo que o programa precisa.",
        "Uma imagem é o molde, e o container é a imagem em execução.",
        "docker run cria e roda um container a partir de uma imagem. docker ps lista os containers rodando.",
        "docker build cria uma imagem a partir de um Dockerfile.",
    ))
    b.append(licao(
        "Dockerfile e docker compose",
        "O Dockerfile é a receita da imagem: FROM escolhe a base, COPY copia arquivos, RUN executa comandos e CMD diz o que rodar.",
        "O docker compose sobe vários containers juntos, descritos no arquivo docker-compose.yml.",
        "docker compose up -d sobe tudo em segundo plano, docker compose logs mostra os registros e docker compose down desliga.",
        "Volumes guardam dados fora do container, para que não se percam quando ele é recriado.",
        "A seção ports liga uma porta do computador a uma porta do container, como 3000:3000.",
    ))
    b.append(licao(
        "Comandos úteis do Docker",
        "docker ps -a lista também os containers parados. docker stop para um container e docker rm apaga.",
        "docker images lista as imagens baixadas. docker logs nome mostra o que o container escreveu.",
        "docker exec -it nome bash abre um terminal dentro do container.",
        "docker system prune apaga o que não está em uso e libera espaço.",
    ))
    return b


def perguntas():
    return [
        qa("O que é o terminal?", "É uma janela onde digitamos comandos em texto para o computador executar."),
        qa("O que é o bash?", "É o shell mais comum no Linux, o programa que interpreta os comandos do terminal."),
        qa("Como ver em que pasta estou?", "Com o comando pwd."),
        qa("Como listar os arquivos de uma pasta?", "Com o comando ls. Com ls -a aparecem também os arquivos escondidos."),
        qa("Como entrar em uma pasta?", "Com cd nome_da_pasta. Para voltar uma pasta, use cd .."),
        qa("Como criar uma pasta?", "Com mkdir nome_da_pasta."),
        qa("Como criar um arquivo vazio?", "Com touch nome_do_arquivo."),
        qa("Como apagar um arquivo?", "Com rm nome_do_arquivo. Não existe lixeira: ele some de vez."),
        qa("Como apagar uma pasta com tudo dentro?", "Com rm -r nome_da_pasta. Cuidado: não dá para desfazer."),
        qa("Como copiar um arquivo?", "Com cp origem destino."),
        qa("Como renomear ou mover um arquivo?", "Com mv origem destino."),
        qa("Como ver o conteúdo de um arquivo?", "Com cat nome_do_arquivo."),
        qa("Como procurar um texto dentro de arquivos?", "Com grep texto arquivo."),
        qa("O que faz o pipe?", "O símbolo | passa a saída de um comando como entrada do próximo."),
        qa("O que faz o símbolo > no terminal?", "Manda a saída de um comando para um arquivo, apagando o que havia. O >> acrescenta no fim."),
        qa("Como tornar um arquivo executável?", "Com chmod +x nome_do_arquivo."),
        qa("O que faz o sudo?", "Executa um comando como administrador do sistema."),
        qa("O que é o Git?", "É um sistema que guarda a história de um projeto, versão por versão, e permite trabalhar em equipe."),
        qa("O que é um commit?", "É uma versão salva do projeto, com uma mensagem que explica o que mudou."),
        qa("Como criar um repositório Git?", "Com git init dentro da pasta do projeto."),
        qa("Como salvar uma alteração com o Git?", "Com git add arquivo, para escolher o que entra, e git commit -m 'mensagem', para salvar."),
        qa("Como ver o que mudou no Git?", "Com git status para a lista de arquivos e git diff para as linhas alteradas."),
        qa("Como ver a história de commits?", "Com git log. Com git log --oneline a lista fica resumida."),
        qa("O que é uma branch?", "É uma linha paralela de trabalho, para testar uma ideia sem mexer na versão principal."),
        qa("Como criar uma branch?", "Com git switch -c nome_da_branch."),
        qa("Como juntar uma branch na principal?", "Entre na principal com git switch main e rode git merge nome_da_branch."),
        qa("O que é o GitHub?", "É um site que guarda repositórios Git na internet e ajuda no trabalho em equipe."),
        qa("O que é o git clone?", "Baixa uma cópia completa de um repositório, com toda a história."),
        qa("Qual a diferença entre git push e git pull?", "push envia seus commits para o remoto. pull traz os commits que você ainda não tem."),
        qa("Para que serve o .gitignore?", "Lista o que o Git deve ignorar, como node_modules, arquivos temporários e senhas."),
        qa("O que é o Docker?", "É uma ferramenta que roda programas dentro de containers, caixas isoladas com tudo que o programa precisa."),
        qa("Qual a diferença entre imagem e container?", "A imagem é o molde. O container é a imagem em execução."),
        qa("O que é um Dockerfile?", "É a receita para construir uma imagem: base, arquivos, comandos e o que rodar."),
        qa("Para que serve o docker compose?", "Para subir vários containers juntos, descritos num arquivo docker-compose.yml."),
        qa("Como subir os serviços com o docker compose?", "Com docker compose up -d, que sobe tudo em segundo plano."),
        qa("Como ver os containers rodando?", "Com docker ps. Com docker ps -a aparecem também os parados."),
        qa("Como ver os registros de um container?", "Com docker logs nome_do_container, ou docker compose logs para os serviços do compose."),
        qa("Para que servem os volumes do Docker?", "Guardam dados fora do container, para não se perderem quando ele é recriado."),
        qa("O que significa ports 3000:3000 no compose?", "Liga a porta 3000 do computador à porta 3000 do container."),
    ]


def exercicios(rng, n):
    familias = [_ex_criar_pasta, _ex_escrever, _ex_contar_linhas, _ex_copiar, _ex_grep, _ex_sort, _ex_git_commit,
                _ex_git_branch, _ex_variavel, _ex_head, _ex_mover]
    blocos = [familias[i % len(familias)](rng) for i in range(n)]
    rng.shuffle(blocos)
    return blocos


def _ex_criar_pasta(rng):
    pasta = rng.choice(PALAVRAS)
    arqs = rng.sample(["a.txt", "b.txt", "notas.md", "dados.csv", "main.py", "index.js"], 3)
    return exercicio_shell(f"Crie a pasta {pasta}, crie os arquivos {', '.join(arqs)} dentro dela e liste o conteúdo.",
                           f"mkdir {pasta}\ntouch " + " ".join(f"{pasta}/{a}" for a in arqs) + f"\nls {pasta}",
                           "mkdir criou a pasta, touch criou os arquivos e ls listou em ordem alfabética.")


def _ex_escrever(rng):
    f1, f2 = rng.sample(FRUTAS, 2)
    return exercicio_shell(f"Escreva {f1} e {f2} em linhas separadas no arquivo frutas.txt e mostre o arquivo.",
                           f'echo "{f1}" > frutas.txt\necho "{f2}" >> frutas.txt\ncat frutas.txt',
                           "O primeiro echo usa > e cria o arquivo. O segundo usa >> e acrescenta.")


def _ex_contar_linhas(rng):
    k = rng.randint(2, 7)
    return exercicio_shell(f"Crie um arquivo com {k} linhas e conte as linhas com wc.",
                           f'for i in $(seq 1 {k}); do echo "linha $i" >> texto.txt; done\nwc -l texto.txt',
                           f"O laço escreveu {k} linhas, e wc -l contou todas.")


def _ex_copiar(rng):
    a = rng.choice(PALAVRAS)
    return exercicio_shell(f"Crie o arquivo {a}.txt com o texto oi, copie para backup.txt e mostre o backup.",
                           f'echo "oi" > {a}.txt\ncp {a}.txt backup.txt\ncat backup.txt',
                           "cp fez uma cópia idêntica, e cat mostrou o conteúdo dela.")


def _ex_grep(rng):
    fr = rng.sample(FRUTAS, 5)
    letra = rng.choice("aeo")
    return exercicio_shell(f"Escreva as frutas {', '.join(fr)} num arquivo, uma por linha, e mostre só as que têm a letra {letra}.",
                           "printf \"" + "\\n".join(fr) + f"\\n\" > frutas.txt\ngrep \"{letra}\" frutas.txt",
                           f"grep mostrou só as linhas que têm a letra {letra}.")


def _ex_sort(rng):
    fr = [rng.choice(FRUTAS[:6]) for _ in range(rng.randint(5, 8))]
    return exercicio_shell(f"Ordene as palavras {', '.join(fr)} e remova as repetidas.",
                           "printf \"" + "\\n".join(fr) + "\\n\" | sort | uniq",
                           "sort deixa as palavras iguais juntas, e uniq remove as repetições.")


def _ex_git_commit(rng):
    arq = rng.choice(["README.md", "notas.txt", "main.py", "app.js"])
    msg = rng.choice(["Primeiro commit", "Adiciona o arquivo inicial", "Começa o projeto", "Versão inicial"])
    return exercicio_shell(f"Crie um repositório Git, crie o arquivo {arq}, faça um commit com a mensagem '{msg}' e mostre o log.",
                           f'git init -q -b main\necho "teste" > {arq}\ngit add {arq}\ngit commit -q -m "{msg}"\ngit log --format=%s',
                           "init cria o repositório, add escolhe o arquivo, commit salva e log mostra a mensagem.")


def _ex_git_branch(rng):
    nome = rng.choice(["login", "pagina-inicial", "correcao", "testes", "api"])
    return exercicio_shell(f"Crie um repositório com um commit vazio, crie a branch {nome} e mostre as branches.",
                           f'git init -q -b main\ngit commit -q --allow-empty -m "inicio"\ngit switch -q -c {nome}\ngit branch',
                           f"A branch atual, {nome}, vem marcada com asterisco.")


def _ex_variavel(rng):
    nome, cidade = rng.choice(NOMES), rng.choice(CIDADES)
    return exercicio_shell(f"Guarde {nome} e {cidade} em variáveis e mostre a frase '{nome} mora em {cidade}'.",
                           f'nome="{nome}"\ncidade="{cidade}"\necho "$nome mora em $cidade"',
                           "As variáveis são trocadas pelos valores dentro das aspas duplas.")


def _ex_head(rng):
    k = rng.randint(6, 12)
    p = rng.randint(2, 4)
    return exercicio_shell(f"Crie um arquivo com os números de 1 a {k} e mostre só os {p} primeiros.",
                           f"seq 1 {k} > numeros.txt\nhead -n {p} numeros.txt",
                           f"seq escreve os números e head -n {p} mostra só as primeiras {p} linhas.")


def _ex_mover(rng):
    a, b = rng.sample(PALAVRAS, 2)
    return exercicio_shell(f"Crie o arquivo {a}.txt, renomeie para {b}.txt e liste a pasta.",
                           f"touch {a}.txt\nmv {a}.txt {b}.txt\nls",
                           "mv com o mesmo diretório renomeia o arquivo.")
