#!/usr/bin/env python3
"""Gera textos de gramática do português (conjugações, números, plurais, gênero, calendário)
por regras, em perguntas e respostas, para o corpus do córtex.

Uso: python3 scripts/gerar_gramatica.py textos/corpus_partes/gramatica_gerada.txt
Só verbos regulares sem mudança de grafia entram pelas regras; os irregulares estão escritos à mão.
"""
import random
import sys

PESSOAS = ["eu", "tu", "ele", "nós", "vós", "eles"]

# ---------- verbos regulares ----------
AR = """falar cantar andar trabalhar estudar comprar ajudar chamar olhar levar gostar precisar esperar entrar mostrar lavar
cozinhar pensar usar tomar pular nadar cuidar amar desenhar terminar visitar preparar observar morar encontrar contar lembrar
mudar parar passar pintar cortar tirar viajar votar voltar acordar adorar apresentar arrumar cheirar deixar desejar escutar
funcionar imaginar melhorar namorar pesquisar procurar recordar salvar sonhar tentar tratar mandar""".split()
ER = """comer beber vender aprender correr responder mexer temer ceder resolver viver entender esconder defender mover
prometer sofrer ofender atender acender bater comover depender suspender""".split()
IR = """partir discutir existir decidir dividir assistir admitir insistir permitir repartir resistir unir cumprir""".split()

TERMINACOES = {
    "ar": {
        "presente": ["o", "as", "a", "amos", "ais", "am"],
        "perfeito": ["ei", "aste", "ou", "amos", "astes", "aram"],
        "imperfeito": ["ava", "avas", "ava", "ávamos", "áveis", "avam"],
    },
    "er": {
        "presente": ["o", "es", "e", "emos", "eis", "em"],
        "perfeito": ["i", "este", "eu", "emos", "estes", "eram"],
        "imperfeito": ["ia", "ias", "ia", "íamos", "íeis", "iam"],
    },
    "ir": {
        "presente": ["o", "es", "e", "imos", "is", "em"],
        "perfeito": ["i", "iste", "iu", "imos", "istes", "iram"],
        "imperfeito": ["ia", "ias", "ia", "íamos", "íeis", "iam"],
    },
}
FUTURO = ["ei", "ás", "á", "emos", "eis", "ão"]
CONDICIONAL = ["ia", "ias", "ia", "íamos", "íeis", "iam"]
NOMES_TEMPO = {
    "presente": "no presente",
    "perfeito": "no pretérito perfeito",
    "imperfeito": "no pretérito imperfeito",
    "futuro": "no futuro do presente",
    "condicional": "no futuro do pretérito",
}


def conjugar_regular(verbo):
    radical, term = verbo[:-2], verbo[-2:]
    formas = {t: [radical + e for e in es] for t, es in TERMINACOES[term].items()}
    formas["futuro"] = [verbo + e for e in FUTURO]
    formas["condicional"] = [verbo + e for e in CONDICIONAL]
    gerundio = radical + {"ar": "ando", "er": "endo", "ir": "indo"}[term]
    participio = radical + ("ado" if term == "ar" else "ido")
    return formas, gerundio, participio


# ---------- verbos irregulares (à mão) ----------
IRREGULARES = {
    "ser": dict(presente="sou és é somos sois são", perfeito="fui foste foi fomos fostes foram",
                imperfeito="era eras era éramos éreis eram", futuro="serei serás será seremos sereis serão",
                gerundio="sendo", participio="sido"),
    "estar": dict(presente="estou estás está estamos estais estão", perfeito="estive estiveste esteve estivemos estivestes estiveram",
                  imperfeito="estava estavas estava estávamos estáveis estavam", futuro="estarei estarás estará estaremos estareis estarão",
                  gerundio="estando", participio="estado"),
    "ter": dict(presente="tenho tens tem temos tendes têm", perfeito="tive tiveste teve tivemos tivestes tiveram",
                imperfeito="tinha tinhas tinha tínhamos tínheis tinham", futuro="terei terás terá teremos tereis terão",
                gerundio="tendo", participio="tido"),
    "ir": dict(presente="vou vais vai vamos ides vão", perfeito="fui foste foi fomos fostes foram",
               imperfeito="ia ias ia íamos íeis iam", futuro="irei irás irá iremos ireis irão",
               gerundio="indo", participio="ido"),
    "fazer": dict(presente="faço fazes faz fazemos fazeis fazem", perfeito="fiz fizeste fez fizemos fizestes fizeram",
                  imperfeito="fazia fazias fazia fazíamos fazíeis faziam", futuro="farei farás fará faremos fareis farão",
                  gerundio="fazendo", participio="feito"),
    "dizer": dict(presente="digo dizes diz dizemos dizeis dizem", perfeito="disse disseste disse dissemos dissestes disseram",
                  imperfeito="dizia dizias dizia dizíamos dizíeis diziam", futuro="direi dirás dirá diremos direis dirão",
                  gerundio="dizendo", participio="dito"),
    "poder": dict(presente="posso podes pode podemos podeis podem", perfeito="pude pudeste pôde pudemos pudestes puderam",
                  imperfeito="podia podias podia podíamos podíeis podiam", futuro="poderei poderás poderá poderemos podereis poderão",
                  gerundio="podendo", participio="podido"),
    "querer": dict(presente="quero queres quer queremos quereis querem", perfeito="quis quiseste quis quisemos quisestes quiseram",
                   imperfeito="queria querias queria queríamos queríeis queriam", futuro="quererei quererás quererá quereremos querereis quererão",
                   gerundio="querendo", participio="querido"),
    "saber": dict(presente="sei sabes sabe sabemos sabeis sabem", perfeito="soube soubeste soube soubemos soubestes souberam",
                  imperfeito="sabia sabias sabia sabíamos sabíeis sabiam", futuro="saberei saberás saberá saberemos sabereis saberão",
                  gerundio="sabendo", participio="sabido"),
    "ver": dict(presente="vejo vês vê vemos vedes veem", perfeito="vi viste viu vimos vistes viram",
                imperfeito="via vias via víamos víeis viam", futuro="verei verás verá veremos vereis verão",
                gerundio="vendo", participio="visto"),
    "vir": dict(presente="venho vens vem vimos vindes vêm", perfeito="vim vieste veio viemos viestes vieram",
                imperfeito="vinha vinhas vinha vínhamos vínheis vinham", futuro="virei virás virá viremos vireis virão",
                gerundio="vindo", participio="vindo"),
    "dar": dict(presente="dou dás dá damos dais dão", perfeito="dei deste deu demos destes deram",
                imperfeito="dava davas dava dávamos dáveis davam", futuro="darei darás dará daremos dareis darão",
                gerundio="dando", participio="dado"),
    "pôr": dict(presente="ponho pões põe pomos pondes põem", perfeito="pus puseste pôs pusemos pusestes puseram",
                imperfeito="punha punhas punha púnhamos púnheis punham", futuro="porei porás porá poremos poreis porão",
                gerundio="pondo", participio="posto"),
    "ler": dict(presente="leio lês lê lemos ledes leem", perfeito="li leste leu lemos lestes leram",
                imperfeito="lia lias lia líamos líeis liam", futuro="lerei lerás lerá leremos lereis lerão",
                gerundio="lendo", participio="lido"),
    "trazer": dict(presente="trago trazes traz trazemos trazeis trazem", perfeito="trouxe trouxeste trouxe trouxemos trouxestes trouxeram",
                   imperfeito="trazia trazias trazia trazíamos trazíeis traziam", futuro="trarei trarás trará traremos trareis trarão",
                   gerundio="trazendo", participio="trazido"),
}


def linha_conjugacao(verbo, tempo, formas):
    corpo = ", ".join(f"{p} {f}" for p, f in zip(PESSOAS, formas))
    return f"Como se conjuga o verbo {verbo} {NOMES_TEMPO[tempo]}?\n{corpo[0].upper() + corpo[1:]}.\n"


def conjugacoes():
    saida = []
    for verbo in AR + ER + IR:
        formas, gerundio, participio = conjugar_regular(verbo)
        for tempo in ("presente", "perfeito", "imperfeito", "futuro", "condicional"):
            saida.append(linha_conjugacao(verbo, tempo, formas[tempo]))
        saida.append(f"Qual é o gerúndio de {verbo}?\n{gerundio[0].upper() + gerundio[1:]}.\n")
        saida.append(f"Qual é o particípio de {verbo}?\n{participio[0].upper() + participio[1:]}.\n")
        saida.append(f"Qual é o infinitivo de {gerundio}?\n{verbo[0].upper() + verbo[1:]}.\n")
        saida.append(f"{verbo[0].upper() + verbo[1:]} é um verbo regular da {'primeira' if verbo.endswith('ar') else 'segunda' if verbo.endswith('er') else 'terceira'} conjugação.\n")
    for verbo, d in IRREGULARES.items():
        for tempo in ("presente", "perfeito", "imperfeito", "futuro"):
            saida.append(linha_conjugacao(verbo, tempo, d[tempo].split()))
        saida.append(f"Qual é o gerúndio de {verbo}?\n{d['gerundio'].capitalize()}.\n")
        saida.append(f"Qual é o particípio de {verbo}?\n{d['participio'].capitalize()}.\n")
        saida.append(f"{verbo.capitalize()} é um verbo irregular.\n")
    return saida


# ---------- números por extenso ----------
UNID = "zero um dois três quatro cinco seis sete oito nove dez onze doze treze catorze quinze dezesseis dezessete dezoito dezenove".split()
DEZ = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa"]
CENT = ["", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos", "setecentos", "oitocentos", "novecentos"]


def por_extenso(n):
    if n < 20:
        return UNID[n]
    if n < 100:
        d, u = divmod(n, 10)
        return DEZ[d] + (f" e {UNID[u]}" if u else "")
    if n == 100:
        return "cem"
    if n < 1000:
        c, resto = divmod(n, 100)
        return CENT[c] + (f" e {por_extenso(resto)}" if resto else "")
    if n < 1_000_000:
        m, resto = divmod(n, 1000)
        milhar = "mil" if m == 1 else f"{por_extenso(m)} mil"
        if resto == 0:
            return milhar
        junta = " e " if resto < 100 or resto % 100 == 0 else " "
        return milhar + junta + por_extenso(resto)
    raise ValueError(n)


def numeros(rng):
    saida = []
    for n in list(range(0, 201)) + [250, 300, 365, 400, 500, 999, 1000, 1500, 2000, 2026, 5000, 10000, 100000, 1000000 - 1]:
        saida.append(f"Como se escreve {n} por extenso?\n{por_extenso(n).capitalize()}.\n")
        saida.append(f"{n} se escreve {por_extenso(n)}.\n")
    for _ in range(400):
        a, b = rng.randint(1, 99), rng.randint(1, 99)
        saida.append(f"Quanto é {a} mais {b}?\n{a} mais {b} é igual a {a + b}.\n")
        if a >= b:
            saida.append(f"Quanto é {a} menos {b}?\n{a} menos {b} é igual a {a - b}.\n")
    for _ in range(150):
        a, b = rng.randint(2, 12), rng.randint(2, 12)
        saida.append(f"Quanto é {a} vezes {b}?\n{a} vezes {b} é igual a {a * b}.\n")
    ordinais = "primeiro segundo terceiro quarto quinto sexto sétimo oitavo nono décimo".split()
    for i, o in enumerate(ordinais, 1):
        saida.append(f"Qual é o ordinal de {i}?\n{o.capitalize()}.\n")
    return saida


# ---------- gênero e número ----------
PARES_GENERO = [("menino", "menina"), ("homem", "mulher"), ("rei", "rainha"), ("pai", "mãe"), ("irmão", "irmã"), ("filho", "filha"),
                ("tio", "tia"), ("avô", "avó"), ("amigo", "amiga"), ("aluno", "aluna"), ("professor", "professora"),
                ("médico", "médica"), ("gato", "gata"), ("cachorro", "cachorra"), ("cavalo", "égua"), ("galo", "galinha"),
                ("ator", "atriz"), ("cantor", "cantora"), ("vizinho", "vizinha"), ("primo", "prima"), ("neto", "neta"),
                ("namorado", "namorada"), ("cliente", "cliente"), ("estudante", "estudante")]
PLURAIS = [("casa", "casas"), ("livro", "livros"), ("mesa", "mesas"), ("carro", "carros"), ("flor", "flores"), ("mulher", "mulheres"),
           ("papel", "papéis"), ("animal", "animais"), ("jornal", "jornais"), ("hotel", "hotéis"), ("pão", "pães"), ("cidadão", "cidadãos"),
           ("coração", "corações"), ("mão", "mãos"), ("lição", "lições"), ("país", "países"), ("mês", "meses"), ("lápis", "lápis"),
           ("ônibus", "ônibus"), ("homem", "homens"), ("jovem", "jovens"), ("cidade", "cidades"), ("rapaz", "rapazes"), ("luz", "luzes"),
           ("sol", "sóis"), ("canal", "canais"), ("limão", "limões"), ("irmão", "irmãos"), ("avião", "aviões"), ("escola", "escolas"),
           ("janela", "janelas"), ("porta", "portas"), ("criança", "crianças"), ("árvore", "árvores"), ("rio", "rios"), ("mar", "mares")]
ARTIGOS = [("casa", "a"), ("livro", "o"), ("mesa", "a"), ("carro", "o"), ("flor", "a"), ("dia", "o"), ("mão", "a"), ("problema", "o"),
           ("mapa", "o"), ("cidade", "a"), ("coração", "o"), ("noite", "a"), ("leite", "o"), ("ponte", "a"), ("sal", "o"), ("rio", "o"),
           ("praia", "a"), ("janela", "a"), ("trem", "o"), ("água", "a"), ("idioma", "o"), ("planeta", "o"), ("telefone", "o")]


def genero_numero():
    saida = []
    for m, f in PARES_GENERO:
        if m != f:
            saida.append(f"Qual é o feminino de {m}?\nO feminino de {m} é {f}.\n")
            saida.append(f"Qual é o masculino de {f}?\nO masculino de {f} é {m}.\n")
    for s, p in PLURAIS:
        saida.append(f"Qual é o plural de {s}?\nO plural de {s} é {p}.\n")
        saida.append(f"Qual é o singular de {p}?\nO singular de {p} é {s}.\n")
    for palavra, art in ARTIGOS:
        indef = "uma" if art == "a" else "um"
        saida.append(f"Qual é o artigo de {palavra}?\nDiz-se {art} {palavra}, no definido, e {indef} {palavra}, no indefinido.\n")
    return saida


# ---------- calendário e tempo ----------
DIAS = ["domingo", "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
ESTACOES = ["primavera", "verão", "outono", "inverno"]
CORES = ["vermelho", "azul", "verde", "amarelo", "preto", "branco", "cinza", "laranja", "roxo", "rosa", "marrom"]


def calendario():
    saida = []
    for i, d in enumerate(DIAS):
        saida.append(f"Qual é o dia depois de {d}?\nDepois de {d} vem {DIAS[(i + 1) % 7]}.\n")
        saida.append(f"Qual é o dia antes de {d}?\nAntes de {d} vem {DIAS[(i - 1) % 7]}.\n")
    for i, m in enumerate(MESES):
        saida.append(f"Qual é o mês depois de {m}?\nDepois de {m} vem {MESES[(i + 1) % 12]}.\n")
        saida.append(f"Qual é o mês antes de {m}?\nAntes de {m} vem {MESES[(i - 1) % 12]}.\n")
        saida.append(f"{m.capitalize()} é o {por_extenso(i + 1) if False else ['primeiro','segundo','terceiro','quarto','quinto','sexto','sétimo','oitavo','nono','décimo','décimo primeiro','décimo segundo'][i]} mês do ano.\n")
    saida.append("Quantos dias tem uma semana?\nUma semana tem sete dias.\n")
    saida.append("Quantos meses tem um ano?\nUm ano tem doze meses.\n")
    saida.append("Quantas horas tem um dia?\nUm dia tem vinte e quatro horas.\n")
    saida.append("Quantos minutos tem uma hora?\nUma hora tem sessenta minutos.\n")
    saida.append("Quantos segundos tem um minuto?\nUm minuto tem sessenta segundos.\n")
    saida.append("Quais são os dias da semana?\n" + ", ".join(DIAS[:-1]).capitalize() + " e " + DIAS[-1] + ".\n")
    saida.append("Quais são os meses do ano?\n" + ", ".join(MESES[:-1]).capitalize() + " e " + MESES[-1] + ".\n")
    saida.append("Quais são as estações do ano?\nPrimavera, verão, outono e inverno.\n")
    saida.append("Quais são as cores do arco-íris?\nVermelho, laranja, amarelo, verde, azul, anil e violeta.\n")
    saida.append("Quais são as vogais?\nAs vogais são a, e, i, o e u.\n")
    saida.append("Quantas letras tem o alfabeto?\nO alfabeto português tem vinte e seis letras.\n")
    return saida


def main():
    destino = sys.argv[1] if len(sys.argv) > 1 else "gramatica_gerada.txt"
    rng = random.Random(7)
    blocos = conjugacoes() + numeros(rng) + genero_numero() + calendario()
    rng.shuffle(blocos)
    with open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(blocos))
    print(f"{len(blocos)} blocos em {destino}")


if __name__ == "__main__":
    main()
