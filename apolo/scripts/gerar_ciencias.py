#!/usr/bin/env python3
"""Gera o currículo de química, biologia e neurociência (perguntas e respostas) para o corpus do córtex.

Uso: python3 scripts/gerar_ciencias.py textos/curriculo
Escreve 12_quimica.txt, 13_biologia.txt e 14_neurociencia.txt. Tudo é escrito à mão em tabelas abaixo,
em nível de ensino médio / início de graduação; as perguntas são variadas por modelos, as respostas são frases inteiras.
"""
import os
import random
import sys

# ---------------------------------------------------------------- química
ELEMENTOS = [  # nome, símbolo, número atômico, papel
    ("hidrogênio", "H", 1, "É o elemento mais simples e mais abundante do universo e faz parte da água e de todas as moléculas orgânicas."),
    ("lítio", "Li", 3, "Sais de lítio são usados como medicamento para estabilizar o humor no transtorno bipolar."),
    ("carbono", "C", 6, "É a base de todas as moléculas orgânicas, como açúcares, gorduras, proteínas e DNA."),
    ("nitrogênio", "N", 7, "Está nas proteínas e nos ácidos nucleicos e compõe cerca de 78% do ar."),
    ("oxigênio", "O", 8, "É usado pelas células na respiração celular para produzir energia, e o cérebro consome cerca de 20% dele."),
    ("flúor", "F", 9, "Fortalece o esmalte dos dentes e aparece em alguns medicamentos."),
    ("sódio", "Na", 11, "Entra nos neurônios durante o potencial de ação e ajuda a controlar o equilíbrio de água do corpo."),
    ("magnésio", "Mg", 12, "Participa de centenas de enzimas e bloqueia o receptor NMDA quando o neurônio está em repouso."),
    ("fósforo", "P", 15, "Está no DNA, no ATP e nas membranas das células."),
    ("enxofre", "S", 16, "Está em dois aminoácidos, a cisteína e a metionina, e forma pontes que mantêm proteínas dobradas."),
    ("cloro", "Cl", 17, "O íon cloreto entra no neurônio pelo receptor GABA-A e deixa a célula menos excitável."),
    ("potássio", "K", 19, "Sai dos neurônios para restabelecer o potencial de repouso depois do potencial de ação."),
    ("cálcio", "Ca", 20, "Entra no terminal do neurônio e faz as vesículas liberarem neurotransmissores; também forma ossos e dentes."),
    ("manganês", "Mn", 25, "É necessário em pequenas quantidades para algumas enzimas, mas em excesso é tóxico para o cérebro."),
    ("ferro", "Fe", 26, "Está na hemoglobina, que carrega oxigênio no sangue, e é necessário para fazer dopamina."),
    ("cobre", "Cu", 29, "Participa de enzimas que fazem neurotransmissores, como a dopamina beta-hidroxilase."),
    ("zinco", "Zn", 30, "Ajuda enzimas e a comunicação entre neurônios, principalmente no hipocampo."),
    ("selênio", "Se", 34, "Faz parte de enzimas antioxidantes que protegem as células."),
    ("iodo", "I", 53, "É necessário para a tireoide fazer hormônios que controlam o desenvolvimento do cérebro."),
]

ELEMENTOS_EXTRA = [("hélio", "He", 2), ("neônio", "Ne", 10), ("alumínio", "Al", 13), ("silício", "Si", 14), ("argônio", "Ar", 18),
                   ("prata", "Ag", 47), ("ouro", "Au", 79), ("mercúrio", "Hg", 80), ("chumbo", "Pb", 82), ("urânio", "U", 92)]

QUIMICA_CONCEITOS = [
    ("O que é um átomo?", "Um átomo é a menor parte de um elemento químico que ainda mantém suas propriedades. Ele tem um núcleo com prótons e nêutrons e elétrons ao redor."),
    ("Qual é a carga elétrica do próton?", "O próton tem carga elétrica positiva."),
    ("Qual é a carga elétrica do elétron?", "O elétron tem carga elétrica negativa."),
    ("O nêutron tem carga elétrica?", "Não. O nêutron não tem carga elétrica, ele é neutro."),
    ("O que define o número atômico?", "O número atômico é a quantidade de prótons no núcleo. É ele que define qual é o elemento químico."),
    ("O que é número de massa?", "O número de massa é a soma de prótons e nêutrons de um átomo."),
    ("O que são isótopos?", "Isótopos são átomos do mesmo elemento com números diferentes de nêutrons, como o carbono-12 e o carbono-14."),
    ("O que é um íon?", "Um íon é um átomo ou molécula com carga elétrica, porque ganhou ou perdeu elétrons."),
    ("O que é um cátion?", "Um cátion é um íon com carga positiva, que perdeu elétrons. O sódio e o potássio formam cátions."),
    ("O que é um ânion?", "Um ânion é um íon com carga negativa, que ganhou elétrons. O cloreto é um ânion."),
    ("O que é uma molécula?", "Uma molécula é um conjunto de dois ou mais átomos unidos por ligações químicas."),
    ("O que é uma ligação covalente?", "Na ligação covalente, os átomos compartilham pares de elétrons. É a ligação típica das moléculas orgânicas."),
    ("O que é uma ligação iônica?", "Na ligação iônica, um átomo transfere elétrons para outro e os íons de cargas opostas se atraem, como no sal de cozinha, NaCl."),
    ("O que é uma ligação de hidrogênio?", "É uma atração fraca entre um hidrogênio ligado a um átomo muito eletronegativo e outro átomo eletronegativo. Ela mantém a água líquida e une as duas fitas do DNA."),
    ("Qual é a fórmula da água?", "A fórmula da água é H2O: dois átomos de hidrogênio e um de oxigênio."),
    ("Por que a água é chamada de solvente universal?", "Porque a água é polar e dissolve muitas substâncias, principalmente as que têm carga ou são polares, como sais e açúcares."),
    ("O que é uma molécula polar?", "Uma molécula polar tem um lado levemente positivo e outro levemente negativo, como a água."),
    ("O que significa hidrofílico?", "Hidrofílico significa que tem afinidade com a água, como os açúcares e os sais."),
    ("O que significa hidrofóbico?", "Hidrofóbico significa que foge da água, como as gorduras e o óleo."),
    ("O que é pH?", "O pH mede a acidez de uma solução, numa escala de 0 a 14. Abaixo de 7 é ácido, 7 é neutro e acima de 7 é básico."),
    ("Qual é o pH da água pura?", "O pH da água pura a 25 graus é 7, ou seja, neutro."),
    ("Qual é o pH normal do sangue?", "O pH normal do sangue é de cerca de 7,4, levemente básico."),
    ("O que é um ácido?", "Um ácido é uma substância que libera íons H+ em água, como o ácido clorídrico do estômago."),
    ("O que é uma base?", "Uma base é uma substância que recebe H+ ou libera íons OH- em água, como a soda cáustica."),
    ("O que é uma solução tampão?", "É uma solução que resiste a mudanças de pH quando se adiciona um pouco de ácido ou base. O sangue tem tampões, como o bicarbonato."),
    ("O que é um mol?", "Um mol é a quantidade de 6,02 x 10^23 partículas, que é a constante de Avogadro."),
    ("O que é concentração molar?", "A concentração molar é a quantidade de mols de soluto por litro de solução, medida em mol/L."),
    ("O que é uma reação química?", "É um processo em que substâncias se transformam em outras, com rearranjo de átomos e quebra e formação de ligações."),
    ("O que é uma reação de oxirredução?", "É uma reação em que há transferência de elétrons: quem perde elétrons se oxida e quem ganha se reduz."),
    ("O que é um catalisador?", "Um catalisador acelera uma reação química sem ser consumido por ela. Nos seres vivos, os catalisadores são as enzimas."),
    ("O que é energia de ativação?", "É a energia mínima necessária para uma reação começar. Os catalisadores diminuem essa energia."),
    ("O que é uma reação exotérmica?", "É uma reação que libera calor para o ambiente, como a queima de uma vela."),
    ("O que é uma reação endotérmica?", "É uma reação que absorve calor do ambiente, como a fotossíntese que absorve energia da luz."),
    ("O que diz a lei de conservação das massas?", "Em uma reação química a massa total se conserva: nada se perde e nada se cria, os átomos só se reorganizam."),
    ("O que é a tabela periódica?", "É a organização dos elementos químicos em ordem crescente de número atômico, em linhas chamadas períodos e colunas chamadas grupos."),
    ("O que são os gases nobres?", "São os elementos do grupo 18, como hélio, neônio e argônio, que quase não reagem porque têm a camada de elétrons completa."),
    ("O que são os metais alcalinos?", "São os elementos do grupo 1, como lítio, sódio e potássio, muito reativos com a água."),
    ("O que é eletronegatividade?", "É a tendência de um átomo de atrair elétrons em uma ligação. O flúor é o elemento mais eletronegativo."),
    ("O que é um eletrólito?", "É uma substância que, dissolvida em água, forma íons e conduz eletricidade, como o sal. Os neurônios dependem de eletrólitos para funcionar."),
    ("O que é osmose?", "Osmose é a passagem de água por uma membrana semipermeável do lado menos concentrado para o mais concentrado."),
    ("O que é difusão?", "Difusão é o movimento espontâneo de partículas do lugar onde há mais para o lugar onde há menos."),
    ("O que é um composto orgânico?", "É um composto que tem carbono ligado a hidrogênio, como açúcares, gorduras, proteínas e ácidos nucleicos."),
    ("O que são grupos funcionais?", "São conjuntos de átomos que dão propriedades características a uma molécula, como o grupo hidroxila (OH) dos álcoois e o grupo amino (NH2) dos aminoácidos."),
    ("Qual é a diferença entre ácido e base de Brønsted?", "O ácido de Brønsted doa um próton, H+, e a base de Brønsted recebe um próton."),
    ("O que é isomeria?", "Isômeros são moléculas com a mesma fórmula molecular, mas com átomos arranjados de forma diferente, e por isso com propriedades diferentes."),
    ("O que é quiralidade?", "Uma molécula é quiral quando não pode ser sobreposta à sua imagem no espelho, como as mãos. Os aminoácidos do corpo são quase todos da forma L."),
    ("O que é uma proteína?", "Uma proteína é um polímero de aminoácidos ligados por ligações peptídicas, que se dobra numa forma tridimensional própria."),
    ("O que é um carboidrato?", "Carboidratos são moléculas de carbono, hidrogênio e oxigênio, como glicose e amido, usadas principalmente como fonte de energia."),
    ("O que é um lipídio?", "Lipídios são moléculas pouco solúveis em água, como gorduras, óleos e fosfolipídios, que guardam energia e formam membranas."),
    ("Qual é a fórmula da glicose?", "A fórmula molecular da glicose é C6H12O6."),
    ("Qual é a principal fonte de energia do cérebro?", "A glicose é a principal fonte de energia do cérebro, que usa cerca de 20% da energia do corpo."),
]

# ---------------------------------------------------------------- biologia
ORGANELAS = [
    ("núcleo", "guarda o DNA e controla as atividades da célula"),
    ("mitocôndria", "produz a maior parte do ATP pela respiração celular, por isso é chamada de usina de energia da célula"),
    ("ribossomo", "faz a síntese de proteínas lendo o RNA mensageiro"),
    ("retículo endoplasmático rugoso", "tem ribossomos presos e produz proteínas que serão enviadas para fora da célula ou para a membrana"),
    ("retículo endoplasmático liso", "produz lipídios e ajuda a desintoxicar a célula"),
    ("complexo de Golgi", "modifica, empacota e envia proteínas e lipídios em vesículas"),
    ("lisossomo", "digere partículas e materiais da própria célula com enzimas"),
    ("membrana plasmática", "separa a célula do ambiente e controla o que entra e sai"),
    ("citoesqueleto", "dá forma à célula e permite o transporte interno de vesículas e organelas"),
    ("peroxissomo", "quebra peróxido de hidrogênio e ácidos graxos longos"),
    ("cloroplasto", "faz a fotossíntese nas células vegetais, transformando luz em açúcar"),
    ("vacúolo", "guarda água e substâncias, e nas células vegetais é grande e mantém a turgidez"),
]

BIOLOGIA = [
    ("O que é a célula?", "A célula é a menor unidade da vida. Todos os seres vivos são feitos de uma ou mais células."),
    ("Qual é a diferença entre célula procariótica e eucariótica?", "A célula procariótica não tem núcleo definido, como as bactérias. A eucariótica tem núcleo e organelas com membrana, como as células de animais, plantas e fungos."),
    ("O que é o DNA?", "O DNA, ou ácido desoxirribonucleico, é a molécula que guarda a informação genética na forma de uma sequência de nucleotídeos."),
    ("Quais são as quatro bases do DNA?", "As bases do DNA são adenina, timina, citosina e guanina."),
    ("Como as bases do DNA se pareiam?", "A adenina se liga à timina e a citosina se liga à guanina."),
    ("Qual é a forma do DNA?", "O DNA tem a forma de uma dupla hélice, com duas fitas unidas por ligações de hidrogênio entre as bases."),
    ("Qual é a diferença entre DNA e RNA?", "O RNA tem uma fita só, o açúcar ribose e a base uracila no lugar da timina. O DNA tem duas fitas, desoxirribose e timina."),
    ("O que é um gene?", "Um gene é um trecho do DNA que contém a instrução para fazer uma proteína ou um RNA."),
    ("O que é o dogma central da biologia molecular?", "A informação genética vai do DNA para o RNA e do RNA para a proteína: transcrição e depois tradução."),
    ("O que é transcrição?", "Transcrição é a síntese de uma molécula de RNA a partir de um gene do DNA, feita pela enzima RNA polimerase."),
    ("O que é tradução?", "Tradução é a síntese de uma proteína no ribossomo, a partir da sequência do RNA mensageiro."),
    ("O que é um códon?", "Um códon é um trio de nucleotídeos do RNA mensageiro que codifica um aminoácido ou um sinal de parada."),
    ("Quantos aminoácidos formam as proteínas?", "As proteínas são feitas com 20 aminoácidos diferentes."),
    ("O que é uma mutação?", "Mutação é uma alteração na sequência do DNA. Pode não ter efeito, causar doença ou, raramente, trazer uma vantagem."),
    ("O que é um cromossomo?", "Um cromossomo é uma molécula de DNA enrolada em proteínas, chamadas histonas, que carrega muitos genes."),
    ("Quantos cromossomos tem uma célula humana?", "Uma célula humana comum tem 46 cromossomos, em 23 pares."),
    ("O que é mitose?", "Mitose é a divisão da célula que gera duas células-filhas idênticas à original, usada no crescimento e na renovação de tecidos."),
    ("O que é meiose?", "Meiose é a divisão que gera células com metade dos cromossomos, os gametas, como óvulos e espermatozoides."),
    ("O que é uma enzima?", "Uma enzima é uma proteína que acelera uma reação química específica, sem ser gasta nela."),
    ("O que é ATP?", "ATP, ou trifosfato de adenosina, é a molécula que carrega energia para as reações da célula."),
    ("O que é respiração celular?", "É o conjunto de reações que quebra a glicose na presença de oxigênio para produzir ATP, gás carbônico e água."),
    ("Qual é a equação geral da respiração celular?", "Glicose mais oxigênio gera gás carbônico, água e energia na forma de ATP."),
    ("O que é fotossíntese?", "Fotossíntese é o processo em que plantas, algas e algumas bactérias usam luz, água e gás carbônico para produzir glicose e oxigênio."),
    ("O que é glicólise?", "Glicólise é a quebra da glicose em duas moléculas de piruvato no citoplasma, com um pequeno ganho de ATP."),
    ("O que é o ciclo de Krebs?", "É uma sequência de reações na mitocôndria que completa a oxidação do carbono dos alimentos e entrega elétrons à cadeia respiratória."),
    ("O que é homeostase?", "Homeostase é a capacidade do organismo de manter o meio interno estável, como a temperatura, o pH e a glicose no sangue."),
    ("O que é o sistema nervoso?", "É o conjunto de órgãos e células que recebe informações, processa e envia ordens ao corpo. Tem o sistema nervoso central e o periférico."),
    ("O que é o sistema endócrino?", "É o conjunto de glândulas que produzem hormônios e os liberam no sangue para regular o corpo."),
    ("O que é um hormônio?", "Hormônio é uma substância química produzida por uma glândula e levada pelo sangue a outros órgãos, onde altera o funcionamento."),
    ("Para que serve a insulina?", "A insulina, produzida no pâncreas, faz as células captarem glicose do sangue e baixa o açúcar no sangue."),
    ("Para que serve o cortisol?", "O cortisol é um hormônio das glândulas adrenais liberado em situações de estresse. Ele aumenta a glicose no sangue e prepara o corpo para agir."),
    ("O que a adrenalina faz?", "A adrenalina acelera o coração, abre as vias aéreas e aumenta o açúcar no sangue, preparando o corpo para lutar ou fugir."),
    ("O que a melatonina faz?", "A melatonina, produzida pela glândula pineal no escuro, ajuda a regular o ciclo do sono."),
    ("O que é a hipófise?", "A hipófise é uma glândula do tamanho de uma ervilha, na base do cérebro, que controla outras glândulas."),
    ("O que é evolução por seleção natural?", "É o processo em que indivíduos com características mais adequadas ao ambiente deixam mais descendentes, e essas características se tornam comuns na população."),
    ("Quem propôs a seleção natural?", "Charles Darwin e Alfred Russel Wallace propuseram a seleção natural, e Darwin a publicou em 1859 no livro A Origem das Espécies."),
    ("O que é uma espécie?", "Em geral, uma espécie é um grupo de seres vivos que se cruzam entre si e têm descendentes férteis."),
    ("O que é um ecossistema?", "É o conjunto dos seres vivos de uma região e do ambiente físico com o qual eles interagem."),
    ("O que é uma cadeia alimentar?", "É a sequência de quem se alimenta de quem, começando pelos produtores, que fazem fotossíntese, seguidos pelos consumidores e decompositores."),
    ("O que são bactérias?", "Bactérias são seres vivos unicelulares sem núcleo. Muitas são úteis, como as do intestino, e algumas causam doenças."),
    ("O que são vírus?", "Vírus são partículas de material genético dentro de uma cápsula de proteína, que só se multiplicam dentro de células vivas."),
    ("O que são antibióticos?", "Antibióticos são medicamentos que matam bactérias ou impedem a sua multiplicação. Eles não funcionam contra vírus."),
    ("O que é o sistema imunológico?", "É o conjunto de células e órgãos que defendem o corpo contra micróbios e células doentes."),
    ("O que é uma vacina?", "Uma vacina treina o sistema imunológico a reconhecer um micróbio antes da infecção real, usando uma versão inofensiva ou um pedaço dele."),
    ("O que faz o coração?", "O coração bombeia o sangue pelo corpo, levando oxigênio e nutrientes e recolhendo gás carbônico."),
    ("O que a hemoglobina faz?", "A hemoglobina, dentro das hemácias, carrega o oxigênio dos pulmões para os tecidos."),
    ("O que é o intestino?", "É o órgão onde terminam a digestão e a absorção dos nutrientes. Ele tem milhões de bactérias e uma rede de neurônios própria."),
    ("O que é o eixo intestino-cérebro?", "É a comunicação entre o intestino e o cérebro por nervos, hormônios e o sistema imunológico. O nervo vago é uma das vias."),
    ("O que são células-tronco?", "São células que ainda não se especializaram e podem se multiplicar e dar origem a outros tipos de células."),
    ("O que é neurogênese?", "É a formação de novos neurônios. No cérebro adulto ela ocorre em poucas regiões, como no giro denteado do hipocampo."),
]

# ---------------------------------------------------------------- neurociência
NEUROTRANSMISSORES = [
    ("glutamato", "é o principal neurotransmissor excitatório do cérebro e é essencial para aprender e lembrar", "receptores como NMDA e AMPA"),
    ("GABA", "é o principal neurotransmissor inibitório do cérebro e acalma a atividade dos neurônios", "receptores GABA-A e GABA-B"),
    ("dopamina", "participa da motivação, da recompensa e do controle dos movimentos", "receptores D1 a D5"),
    ("serotonina", "participa do humor, do sono e do apetite", "receptores 5-HT"),
    ("noradrenalina", "participa da atenção, do alerta e da resposta ao estresse", "receptores alfa e beta adrenérgicos"),
    ("acetilcolina", "participa da contração dos músculos, da atenção e da memória", "receptores nicotínicos e muscarínicos"),
    ("glicina", "é um neurotransmissor inibitório, principalmente na medula espinhal e no tronco encefálico", "receptores de glicina"),
    ("histamina", "participa da vigília, ou seja, de manter o cérebro acordado", "receptores H1 a H4"),
    ("endorfina", "alivia a dor e causa sensação de bem-estar", "receptores opioides"),
    ("adenosina", "se acumula durante a vigília e causa a pressão de sono", "receptores A1 e A2A"),
]

PRECURSORES = [
    ("dopamina", "tirosina", "A dopamina é feita a partir do aminoácido tirosina."),
    ("noradrenalina", "dopamina", "A noradrenalina é feita a partir da dopamina."),
    ("serotonina", "triptofano", "A serotonina é feita a partir do aminoácido triptofano."),
    ("GABA", "glutamato", "O GABA é feito a partir do glutamato pela enzima glutamato descarboxilase."),
    ("acetilcolina", "colina", "A acetilcolina é feita a partir da colina e da acetil-CoA."),
    ("melatonina", "serotonina", "A melatonina é feita a partir da serotonina."),
]

REGIOES = [  # nome, função
    ("córtex pré-frontal", "planejamento, tomada de decisões, atenção e controle dos impulsos"),
    ("córtex motor", "o controle dos movimentos voluntários"),
    ("córtex somatossensorial", "o processamento do tato, da dor e da posição do corpo"),
    ("córtex visual", "o processamento das imagens que vêm dos olhos, e fica no lobo occipital"),
    ("córtex auditivo", "o processamento dos sons, e fica no lobo temporal"),
    ("hipocampo", "a formação de novas memórias e a orientação no espaço"),
    ("amígdala", "o processamento do medo e das emoções"),
    ("tálamo", "a retransmissão das informações dos sentidos para o córtex"),
    ("hipotálamo", "o controle da fome, da sede, da temperatura e dos hormônios"),
    ("cerebelo", "a coordenação dos movimentos, o equilíbrio e a precisão motora"),
    ("tronco encefálico", "funções vitais como a respiração e os batimentos do coração"),
    ("bulbo", "o controle da respiração, da pressão do sangue e dos batimentos do coração"),
    ("gânglios da base", "o início e a suavidade dos movimentos e a formação de hábitos"),
    ("substância negra", "a produção de dopamina para o controle dos movimentos"),
    ("área de Broca", "a produção da fala"),
    ("área de Wernicke", "a compreensão da linguagem"),
    ("corpo caloso", "a ligação entre os dois hemisférios do cérebro"),
    ("núcleo accumbens", "a motivação e a sensação de recompensa"),
    ("giro do cíngulo", "a atenção, a emoção e a dor"),
    ("ínsula", "a percepção do estado interno do corpo e o nojo"),
    ("glândula pineal", "a produção de melatonina"),
    ("medula espinhal", "levar informações entre o corpo e o cérebro e controlar reflexos"),
]

LOBOS = [("frontal", "o planejamento, o movimento e a linguagem falada"), ("parietal", "o tato e a atenção espacial"),
         ("temporal", "a audição, a memória e o reconhecimento de rostos"), ("occipital", "a visão")]

NERVOS = ["olfatório", "óptico", "oculomotor", "troclear", "trigêmeo", "abducente", "facial", "vestibulococlear",
          "glossofaríngeo", "vago", "acessório", "hipoglosso"]
NERVOS_FUNCAO = {
    "olfatório": "o olfato", "óptico": "a visão", "oculomotor": "a maior parte dos movimentos do olho e o tamanho da pupila",
    "troclear": "o movimento do músculo oblíquo superior do olho", "trigêmeo": "a sensibilidade do rosto e a mastigação",
    "abducente": "o movimento lateral do olho", "facial": "as expressões do rosto e o paladar da parte da frente da língua",
    "vestibulococlear": "a audição e o equilíbrio", "glossofaríngeo": "o paladar do fundo da língua e a deglutição",
    "vago": "o controle do coração, dos pulmões e do intestino", "acessório": "o movimento do pescoço e dos ombros",
    "hipoglosso": "o movimento da língua",
}

ONDAS = [("delta", "0,5 a 4 Hz", "o sono profundo"), ("teta", "4 a 8 Hz", "a sonolência e a memória"),
         ("alfa", "8 a 13 Hz", "o relaxamento de olhos fechados"), ("beta", "13 a 30 Hz", "o estado de alerta e o pensamento ativo"),
         ("gama", "acima de 30 Hz", "a atenção intensa e a integração de informações")]

NEURO = [
    ("O que é um neurônio?", "O neurônio é a célula do sistema nervoso que recebe, processa e transmite sinais elétricos e químicos."),
    ("Quais são as partes de um neurônio?", "Um neurônio tem o corpo celular, os dendritos que recebem sinais, o axônio que envia o sinal e os terminais do axônio onde ficam as sinapses."),
    ("Quantos neurônios tem o cérebro humano?", "O cérebro humano tem cerca de 86 bilhões de neurônios."),
    ("Quanto pesa o cérebro humano adulto?", "O cérebro humano adulto pesa em média cerca de 1,4 quilo."),
    ("O que é uma sinapse?", "A sinapse é o ponto de comunicação entre dois neurônios, onde o sinal passa de um para o outro, em geral por neurotransmissores."),
    ("O que é a fenda sináptica?", "É o pequeno espaço entre o neurônio que envia e o que recebe o sinal, por onde os neurotransmissores se difundem."),
    ("O que é um neurotransmissor?", "É uma molécula que um neurônio libera na sinapse para mandar um sinal para outra célula."),
    ("O que é um receptor?", "Um receptor é uma proteína na membrana da célula que reconhece uma molécula específica, como um neurotransmissor, e provoca uma resposta."),
    ("O que é o potencial de repouso?", "É a diferença de carga entre o interior e o exterior do neurônio quando ele não está disparando, de cerca de -70 milivolts."),
    ("O que é o potencial de ação?", "É um pulso elétrico rápido que percorre o axônio. Canais de sódio se abrem, o sódio entra, e depois canais de potássio deixam o potássio sair."),
    ("Qual é a lei do tudo ou nada?", "Um neurônio ou dispara um potencial de ação completo, ou não dispara. A força do estímulo muda a frequência dos disparos, não o tamanho de cada um."),
    ("O que é a bomba de sódio e potássio?", "É uma proteína que gasta ATP para tirar 3 íons de sódio da célula e colocar 2 íons de potássio, mantendo o potencial de repouso."),
    ("Para que serve a bainha de mielina?", "A mielina envolve o axônio como um isolante e faz o sinal saltar de um nó de Ranvier para o outro, o que acelera a condução."),
    ("O que são os nós de Ranvier?", "São pequenos trechos do axônio sem mielina, onde o potencial de ação é renovado."),
    ("Quais células produzem mielina?", "No cérebro e na medula, os oligodendrócitos produzem a mielina. Nos nervos do resto do corpo, são as células de Schwann."),
    ("O que são astrócitos?", "Astrócitos são células da glia em forma de estrela que sustentam os neurônios, regulam o ambiente químico e ajudam a formar a barreira hematoencefálica."),
    ("O que é a micróglia?", "A micróglia são as células de defesa do cérebro: eliminam restos celulares, micróbios e sinapses em excesso."),
    ("O que é a glia?", "A glia é o conjunto de células de suporte do sistema nervoso, como astrócitos, oligodendrócitos e micróglia. Existem em número parecido com o dos neurônios."),
    ("O que é a barreira hematoencefálica?", "É uma barreira formada por células dos vasos do cérebro que controla quais substâncias passam do sangue para o tecido cerebral."),
    ("O que é o líquor?", "O líquor, ou líquido cefalorraquidiano, é um líquido transparente que envolve o cérebro e a medula e amortece impactos."),
    ("O que são as meninges?", "São três camadas de membranas que protegem o cérebro e a medula: dura-máter, aracnoide e pia-máter."),
    ("O que é substância cinzenta?", "É a parte do sistema nervoso rica em corpos de neurônios, como a superfície do córtex."),
    ("O que é substância branca?", "É a parte do sistema nervoso rica em axônios com mielina, que conectam regiões do cérebro."),
    ("Para que servem os sulcos e giros do cérebro?", "As dobras aumentam a área do córtex, e assim cabem mais neurônios dentro do crânio."),
    ("Quais são os dois hemisférios do cérebro?", "São o hemisfério direito e o esquerdo, ligados pelo corpo caloso. Em geral, cada um controla o lado oposto do corpo."),
    ("Qual hemisfério costuma controlar a linguagem?", "Na maioria das pessoas, o hemisfério esquerdo é o dominante para a linguagem."),
    ("O que é plasticidade neural?", "É a capacidade do cérebro de mudar suas conexões com a experiência e o aprendizado."),
    ("O que é potenciação de longa duração?", "A potenciação de longa duração, ou LTP, é o reforço duradouro de uma sinapse depois de ser muito usada. É um dos mecanismos básicos da memória."),
    ("O que é depressão de longa duração?", "A depressão de longa duração, ou LTD, é o enfraquecimento duradouro de uma sinapse pouco usada."),
    ("O que diz a regra de Hebb?", "Neurônios que disparam juntos se conectam: quando dois neurônios são ativados ao mesmo tempo, a sinapse entre eles se fortalece."),
    ("Qual é o papel do receptor NMDA na memória?", "O receptor NMDA só abre quando a sinapse é ativada e o neurônio já está despolarizado, deixando o cálcio entrar. Esse cálcio dispara a LTP."),
    ("Como o hipocampo ajuda na memória?", "O hipocampo liga as partes de uma experiência e as consolida em memória, que depois fica guardada no córtex. Por isso a lesão dele impede formar memórias novas."),
    ("Quem foi o paciente H.M.?", "Henry Molaison foi um paciente que perdeu o hipocampo numa cirurgia em 1953 e deixou de formar novas memórias, o que mostrou o papel do hipocampo."),
    ("Qual é a diferença entre memória de curto e de longo prazo?", "A memória de curto prazo guarda poucas informações por segundos ou minutos. A de longo prazo guarda por dias ou anos e depende de mudanças nas sinapses."),
    ("O que é memória de trabalho?", "É a capacidade de manter e manipular informações por pouco tempo, como lembrar um número de telefone enquanto o digita. Depende do córtex pré-frontal."),
    ("Qual é a diferença entre memória explícita e implícita?", "A memória explícita é a que podemos contar, como fatos e eventos. A implícita aparece no fazer, como andar de bicicleta."),
    ("O que acontece no cérebro durante o sono?", "O cérebro consolida memórias, reorganiza sinapses e elimina resíduos do metabolismo pelo sistema glinfático."),
    ("Quais são as fases do sono?", "O sono tem fases de sono leve, sono profundo e sono REM, que se repetem em ciclos de cerca de 90 minutos."),
    ("O que é o sono REM?", "É a fase do sono com movimentos rápidos dos olhos, sonhos mais vívidos e atividade cerebral parecida com a da vigília."),
    ("O que é o ritmo circadiano?", "É um relógio biológico de cerca de 24 horas, controlado pelo núcleo supraquiasmático do hipotálamo, que regula o sono e outras funções."),
    ("O que é o sistema nervoso autônomo?", "É a parte do sistema nervoso que controla funções involuntárias, como o coração e a digestão. Tem a divisão simpática e a parassimpática."),
    ("O que faz o sistema nervoso simpático?", "O simpático prepara o corpo para lutar ou fugir: acelera o coração e dilata as pupilas."),
    ("O que faz o sistema nervoso parassimpático?", "O parassimpático favorece o repouso e a digestão: desacelera o coração e estimula o intestino."),
    ("O que é um reflexo?", "Reflexo é uma resposta rápida e automática a um estímulo, que muitas vezes passa só pela medula espinhal, sem esperar o cérebro."),
    ("O que é nocicepção?", "É a detecção de estímulos que podem lesar o corpo, por terminações nervosas chamadas nociceptores. A dor é a experiência construída pelo cérebro a partir desses sinais."),
    ("Como funciona a visão no cérebro?", "A luz é captada pelos fotorreceptores da retina, o sinal vai pelo nervo óptico ao tálamo e daí ao córtex visual, no lobo occipital."),
    ("Qual a diferença entre cones e bastonetes?", "Os cones captam cores e funcionam com muita luz. Os bastonetes funcionam com pouca luz e não distinguem cores."),
    ("O que é o sistema de recompensa?", "É o circuito de dopamina que vai da área tegmental ventral ao núcleo accumbens e ao córtex pré-frontal e reforça comportamentos que foram bons."),
    ("O que é o estresse para o cérebro?", "O estresse ativa o eixo hipotálamo-hipófise-adrenal, que libera cortisol. Em excesso e por muito tempo, o cortisol pode prejudicar o hipocampo."),
    ("O que são neurônios-espelho?", "São neurônios que disparam tanto quando fazemos uma ação quanto quando vemos alguém fazê-la. Estudos em macacos os descobriram, e seu papel nos humanos é ainda debatido."),
    ("Qual é a diferença entre neurociência e psicologia?", "A neurociência estuda o sistema nervoso e como ele produz o comportamento. A psicologia estuda a mente e o comportamento, em geral em um nível mais amplo."),
    ("Quanto de energia o cérebro usa?", "O cérebro pesa cerca de 2% do corpo, mas usa cerca de 20% da energia, principalmente para manter o potencial de repouso dos neurônios."),
    ("O que é uma rede neural biológica?", "É um conjunto de neurônios ligados por sinapses que trabalham juntos. As redes neurais artificiais foram inspiradas nesse modelo, mas são muito mais simples."),
    ("O que é conectoma?", "O conectoma é o mapa completo das conexões entre os neurônios de um cérebro. O do verme C. elegans, com 302 neurônios, foi o primeiro a ser completado."),
    ("Quantas sinapses tem o cérebro humano?", "Estima-se que o cérebro humano tenha cerca de 100 trilhões de sinapses."),
    ("O que é o eletroencefalograma?", "O eletroencefalograma, ou EEG, registra a atividade elétrica do cérebro por eletrodos colocados no couro cabeludo."),
    ("O que é a ressonância magnética funcional?", "A ressonância magnética funcional, ou fMRI, mostra quais regiões do cérebro estão mais ativas pelas mudanças no fluxo de sangue oxigenado."),
    ("O que é a tomografia por emissão de pósitrons?", "A PET mede o metabolismo ou a ligação de moléculas no cérebro, usando um marcador radioativo injetado no sangue."),
    ("O que é a optogenética?", "É uma técnica que usa luz para ligar ou desligar neurônios que foram modificados para produzir proteínas sensíveis à luz."),
    ("O que é a estimulação magnética transcraniana?", "A EMT usa um campo magnético para estimular áreas do cérebro sem cirurgia, e é usada no tratamento de alguns casos de depressão."),
    ("O que é a doença de Alzheimer?", "É uma doença neurodegenerativa que causa perda progressiva da memória e de outras funções. Está ligada ao acúmulo de placas de beta-amiloide e emaranhados da proteína tau."),
    ("O que é a doença de Parkinson?", "É uma doença neurodegenerativa causada pela perda dos neurônios de dopamina da substância negra, que causa tremor, rigidez e lentidão dos movimentos."),
    ("O que é a epilepsia?", "É uma doença em que grupos de neurônios disparam de forma excessiva e sincronizada, causando crises."),
    ("O que é a esclerose múltipla?", "É uma doença em que o sistema imunológico ataca a mielina do sistema nervoso central, atrapalhando a condução dos sinais."),
    ("O que é um acidente vascular cerebral?", "O AVC acontece quando um vaso do cérebro entope ou se rompe, e as células ficam sem oxigênio e morrem."),
    ("O que é a depressão?", "É um transtorno do humor com tristeza profunda ou perda de interesse por muito tempo. Está ligada a fatores biológicos, como serotonina, e a fatores sociais."),
    ("Como agem os antidepressivos inibidores da recaptação de serotonina?", "Eles impedem que a serotonina seja recaptada pelo neurônio que a liberou, e assim ela fica mais tempo na fenda sináptica."),
    ("O que a cafeína faz no cérebro?", "A cafeína bloqueia os receptores de adenosina e por isso diminui a sensação de cansaço."),
    ("O que o álcool faz no cérebro?", "O álcool aumenta o efeito do GABA e diminui o do glutamato, o que deixa o cérebro mais lento."),
    ("O que a nicotina faz no cérebro?", "A nicotina ativa os receptores nicotínicos de acetilcolina e aumenta a liberação de dopamina."),
    ("O que são os opioides?", "Opioides são substâncias que ativam os receptores opioides, como a morfina e as endorfinas do próprio corpo. Aliviam a dor, mas podem causar dependência."),
    ("O que é a dependência química?", "É um estado em que o cérebro se adapta ao uso de uma substância, que passa a ser buscada de forma compulsiva, mesmo com prejuízos."),
    ("O que é o transtorno do espectro autista?", "É uma condição do neurodesenvolvimento que afeta a comunicação social e traz interesses e comportamentos repetitivos, com muita variação entre as pessoas."),
    ("O que é o TDAH?", "É o transtorno de déficit de atenção e hiperatividade, uma condição do neurodesenvolvimento com dificuldade de manter a atenção e controlar impulsos."),
    ("O que é a afasia?", "A afasia é a perda ou dificuldade da linguagem, em geral causada por lesão no hemisfério esquerdo, como um AVC."),
    ("Como o cérebro muda na adolescência?", "O córtex pré-frontal ainda amadurece até cerca dos 25 anos, e por isso o controle dos impulsos e o planejamento se desenvolvem mais tarde."),
    ("O exercício físico faz bem ao cérebro?", "Sim. O exercício aumenta o fluxo de sangue, estimula o fator neurotrófico BDNF e favorece a plasticidade e a memória."),
    ("O que é o BDNF?", "O BDNF é o fator neurotrófico derivado do cérebro, uma proteína que ajuda os neurônios a sobreviver, crescer e formar sinapses."),
    ("O que é a apoptose?", "A apoptose é a morte celular programada, um processo ordenado que elimina células que não são mais necessárias ou estão danificadas."),
    ("O que é neuroinflamação?", "É a resposta inflamatória do tecido nervoso, feita sobretudo pela micróglia e pelos astrócitos. Em excesso e por muito tempo, ela contribui para doenças neurodegenerativas."),
    ("O que é um canal iônico?", "É uma proteína da membrana que forma um poro e deixa certos íons passarem. Os canais podem ser abertos por voltagem ou por um neurotransmissor."),
    ("O que é despolarização?", "Despolarização é quando o interior do neurônio fica menos negativo. Ao passar de um limiar, de cerca de -55 milivolts, dispara-se um potencial de ação."),
    ("O que é hiperpolarização?", "É quando o interior do neurônio fica mais negativo do que no repouso, o que torna o disparo mais difícil."),
    ("O que é uma sinapse excitatória?", "É uma sinapse que aproxima o neurônio do limiar de disparo, como as de glutamato."),
    ("O que é uma sinapse inibitória?", "É uma sinapse que afasta o neurônio do limiar de disparo, como as de GABA."),
    ("O que é a recaptação?", "É o processo em que o neurônio que liberou um neurotransmissor o puxa de volta por transportadores, o que encerra o sinal."),
    ("O que são sinapses elétricas?", "São sinapses em que os neurônios se ligam por junções comunicantes e a corrente passa direto de um para o outro, mais rápido que na sinapse química."),
    ("Qual é a velocidade de um impulso nervoso?", "Pode ir de cerca de 1 metro por segundo em fibras finas sem mielina a mais de 100 metros por segundo em fibras grossas com mielina."),
    ("O que é o cérebro trino?", "É um modelo antigo que dividia o cérebro em reptiliano, límbico e neocórtex. Hoje é considerado simplificado demais pela neurociência."),
    ("Usamos só 10% do cérebro?", "Não. Isso é um mito. Imagens mostram que usamos praticamente todo o cérebro, em momentos diferentes."),
    ("O cérebro pára de mudar depois de adulto?", "Não. O cérebro continua mudando a vida inteira por plasticidade, embora aprenda mais rápido na infância."),
]


# ---------------------------------------------------------------- geração
def maiuscula(texto):
    return texto[0].upper() + texto[1:]


def quimica():
    pares = list(QUIMICA_CONCEITOS)
    for nome, simbolo, z, papel in ELEMENTOS:
        pares += [
            (f"Qual é o símbolo do {nome}?", f"O símbolo do {nome} é {simbolo}."),
            (f"Qual é o número atômico do {nome}?", f"O número atômico do {nome} é {z}."),
            (f"Qual elemento tem o símbolo {simbolo}?", f"O símbolo {simbolo} é do elemento {nome}."),
            (f"Qual elemento tem número atômico {z}?", f"O elemento de número atômico {z} é o {nome}."),
            (f"Qual é a importância do {nome} para o corpo?", papel),
        ]
    for nome, simbolo, z in ELEMENTOS_EXTRA:
        pares += [
            (f"Qual é o símbolo do {nome}?", f"O símbolo do {nome} é {simbolo}."),
            (f"Qual é o número atômico do {nome}?", f"O número atômico do {nome} é {z}."),
        ]
    return pares


ORGANELAS_MASC = {"núcleo", "ribossomo", "retículo endoplasmático rugoso", "retículo endoplasmático liso", "complexo de Golgi", "citoesqueleto", "peroxissomo", "cloroplasto", "vacúolo", "lisossomo"}


def biologia():
    pares = list(BIOLOGIA)
    for nome, funcao in ORGANELAS:
        art = "o" if nome in ORGANELAS_MASC else "a"
        A, de = ARTIGOS[art]
        pares += [
            (f"Qual é a função {de} {nome}?", f"{A} {nome} {funcao}."),
            (f"O que faz {art} {nome}?", f"{A} {nome} {funcao}."),
        ]
    return pares


FEMININOS = {"dopamina", "serotonina", "noradrenalina", "acetilcolina", "glicina", "histamina", "endorfina", "adenosina"}
# Regiões no feminino ou plural; as demais são masculinas no singular.
REGIOES_FEM = {"amígdala", "ínsula", "glândula pineal", "medula espinhal", "substância negra", "área de Broca", "área de Wernicke"}
ARTIGOS = {"o": ("O", "do"), "a": ("A", "da"), "os": ("Os", "dos")}
NOS = {"o": "no", "a": "na"}


def artigo_regiao(nome):
    if nome in REGIOES_FEM:
        return "a"
    return "os" if nome.startswith("gânglios") else "o"


def neurociencia():
    pares = list(NEURO)
    for nome, funcao, receptores in NEUROTRANSMISSORES:
        art = "a" if nome in FEMININOS else "o"
        A, de = ARTIGOS[art]
        pares += [
            (f"O que {art} {nome} faz no cérebro?", f"{A} {nome} {funcao}."),
            (f"Quais são os receptores {de} {nome}?", f"{A} {nome} age por {receptores}."),
            (f"{A} {nome} é um neurotransmissor?", f"Sim, {art} {nome} é um neurotransmissor: {funcao}."),
        ]
    for nome, origem, frase in PRECURSORES:
        art = "a" if nome in FEMININOS else "o"
        pares.append((f"Como se faz {art} {nome}?", frase))
    for nome, funcao in REGIOES:
        art = artigo_regiao(nome)
        A, de = ARTIGOS[art]
        verbo = "são importantes" if art == "os" else "é importante"
        pares.append((f"Para que {'servem' if art == 'os' else 'serve'} {art} {nome}?", f"{A} {nome} {verbo} para {funcao}."))
        pares.append((f"Qual é a função {de} {nome}?", f"{A} {nome} {verbo} para {funcao}."))
    for lobo, funcao in LOBOS:
        pares.append((f"Qual é a função do lobo {lobo}?", f"O lobo {lobo} é importante para {funcao}."))
    pares.append(("Quais são os quatro lobos do córtex cerebral?", "Os quatro lobos do córtex são o frontal, o parietal, o temporal e o occipital."))
    for i, nome in enumerate(NERVOS, 1):
        pares.append((f"Qual é o nervo craniano número {i}?", f"O nervo craniano número {i} é o {nome}."))
        pares.append((f"Qual é a função do nervo {nome}?", f"O nervo {nome} é responsável por {NERVOS_FUNCAO[nome]}."))
    pares.append(("Quantos pares de nervos cranianos existem?", "Existem 12 pares de nervos cranianos."))
    for nome, faixa, estado in ONDAS:
        pares.append((f"O que são as ondas {nome}?", f"As ondas {nome} do EEG têm frequência de {faixa} e se associam a {estado}."))
    pares.append(("Quais são as ondas cerebrais do EEG?", "As faixas do EEG são delta, teta, alfa, beta e gama, da mais lenta para a mais rápida."))
    return pares


def escrever(caminho, titulo, resumo, pares, semente):
    rng = random.Random(semente)
    vistos, unicos = set(), []
    for p, r in pares:
        if p not in vistos:
            vistos.add(p)
            unicos.append((p, r))
    rng.shuffle(unicos)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(f"Lição: {titulo}\n{resumo}\n\n")
        for p, r in unicos:
            f.write(f"{p}\n{r}\n\n")
    return len(unicos)


def main():
    saida = sys.argv[1] if len(sys.argv) > 1 else "textos/curriculo"
    os.makedirs(saida, exist_ok=True)
    n1 = escrever(os.path.join(saida, "12_quimica.txt"), "Química básica e química do corpo",
                  "Este texto ensina química em perguntas e respostas: átomos, ligações, água, pH, reações e os elementos importantes para o cérebro.", quimica(), 12)
    n2 = escrever(os.path.join(saida, "13_biologia.txt"), "Biologia celular e do corpo",
                  "Este texto ensina biologia em perguntas e respostas: células, organelas, DNA, proteínas, energia, hormônios e evolução.", biologia(), 13)
    n3 = escrever(os.path.join(saida, "14_neurociencia.txt"), "Neurociência: o estudo do cérebro",
                  "Este texto ensina neurociência em perguntas e respostas: neurônios, sinapses, neurotransmissores, regiões do cérebro, memória, sono, métodos e doenças.", neurociencia(), 14)
    print(f"química {n1}, biologia {n2}, neurociência {n3} perguntas")


if __name__ == "__main__":
    main()
