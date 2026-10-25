# Tucano 2 e o Apolo: relatório técnico

Data da verificação: 23/10/2026. Tudo abaixo foi lido nas fontes primárias (API e cartões do Hugging Face, paper no arXiv, GitHub). Itens marcados **[ESTIMATIVA]** são contas minhas, e **[NÃO CONFIRMADO]** é o que não consegui verificar. Não é parecer jurídico.

## 1. Recomendação (decisão pronta)

| Papel | Veredito | Por quê |
|---|---|---|
| **Professor offline no Colab** (paráfrases de perguntas, explicar código, melhor-de-N) | **SIM, para paráfrases e explicações simples; com revisão humana por amostragem** | Apache-2.0 sem cláusula sobre treinar com a saída. Custo: uma T4 do Colab, minutos a poucas horas. Use o 3,7B-Instruct (ou 1,5B). Não serve como juiz de código (HumanEval 47,6% no 3,7B). |
| **Córtex substituto** | **NÃO** | O 3,7B não cabe com folga em 7 GB (bf16 = 7,5 GB) e em 4 bits dá poucos tokens/s **[ESTIMATIVA]**. O 0,5B cabe, mas troca um córtex que o dono treina e controla (identidade, intenções, caractere/BPE próprio) por um modelo genérico que nunca ouviu falar do Apolo. Contraria a ideia de "córtex próprio". |
| **GigaVerbo-v2 educativo como dado extra** | **SIM, em dose pequena (50 a 150 MB, peso 1)** | Público, sem termos a aceitar. Mas a licença do corpus é "other" (mistura de fontes, incluindo algumas não comerciais) e o registro é web, não o do Apolo. O filtro de caracteres do `montar_corpus.py` descarta boa parte das linhas. |

Atalho que dispensa rodar o modelo: o dataset `Polygl0t/gigaverbo-v2-sft` (Apache-2.0) já traz os subconjuntos `rewriting` (29 mil exemplos, 0,01 GB), `code` (81 mil, 0,15 GB) e `general` (1,2 milhão, 1,5 GB), gerados por Qwen2.5 (também Apache-2.0). Dá para baixar só `rewriting` e `code` e filtrar `instruct_int_score >= 4`.

**Comparação honesta com o `medio` (~85M):** o Tucano2-0.5B-Instruct tem 491 M de parâmetros (5,8 vezes mais) e foi treinado em dezenas de bilhões de tokens de português (50B de pré-treino contínuo, mais SFT/APO; Qwen3 vem de 36 trilhões). O `medio` aprende de algumas centenas de MB. Em conhecimento geral e instruções o Tucano ganha de longe (0,5B: MMLU-PT 41,5%, ENEM 53,6%, IFEval-PT 30%, HumanEval 10,4%). O `medio` só tem vantagem onde o Apolo é especialista: identidade, saudações, intenções, formato do grafo, e custo (170 MB em fp16, milhares de tokens/s na CPU). Não existe benchmark comum entre os dois **[NÃO CONFIRMADO]**; o `avaliar_colab.ipynb` serve para gerar essa comparação lado a lado.

## 2. Modelos Tucano 2 (todos em `Polygl0t/`)

Fonte: listagem https://huggingface.co/api/models?author=Polygl0t e cartões individuais. Autores: Corrêa, Sen, Fatimah, Falk, Landgraf, Kastner, Flek (Univ. de Bonn); paper "Tucano 2 Cool" https://arxiv.org/abs/2603.03543 (HTML: https://arxiv.org/html/2603.03543v1).

| ID no HF | Parâmetros (API) | Variante | Arquitetura | Licença |
|---|---|---|---|---|
| [Tucano2-qwen-0.5B-Base](https://huggingface.co/Polygl0t/Tucano2-qwen-0.5B-Base) / [Instruct](https://huggingface.co/Polygl0t/Tucano2-qwen-0.5B-Instruct) / [Think](https://huggingface.co/Polygl0t/Tucano2-qwen-0.5B-Think) | 490.799.104 | Base, Instruct, Think | Qwen3 (28 camadas, hidden 1024) | Apache-2.0 |
| [Tucano2-qwen-1.5B-Base](https://huggingface.co/Polygl0t/Tucano2-qwen-1.5B-Base) / [Instruct](https://huggingface.co/Polygl0t/Tucano2-qwen-1.5B-Instruct) / [Think](https://huggingface.co/Polygl0t/Tucano2-qwen-1.5B-Think) | 1.510.073.344 | idem | Qwen3 (28 camadas, hidden 2048) | Apache-2.0 |
| [Tucano2-qwen-3.7B-Base](https://huggingface.co/Polygl0t/Tucano2-qwen-3.7B-Base) / [Instruct](https://huggingface.co/Polygl0t/Tucano2-qwen-3.7B-Instruct) / [Think](https://huggingface.co/Polygl0t/Tucano2-qwen-3.7B-Think) | 3.759.341.056 | idem | Qwen3 (36 camadas, hidden 2560) | Apache-2.0 |
| [Tucano2-0.6B-Base](https://huggingface.co/Polygl0t/Tucano2-0.6B-Base) | 670.127.616 | só Base (sem Instruct/Think na listagem) | Llama, treinado do zero | Apache-2.0 |

- **Licença:** campo `license: apache-2.0` na API do HF para os 10 modelos e arquivo `LICENSE` Apache 2.0 em cada repositório. Seção "Intended Uses" do cartão: pode ajustar e adaptar "if your use follows the Apache 2.0 license". Repositório de código https://github.com/Polygl0t/llm-foundry também Apache-2.0 (API do GitHub).
- **Cláusula sobre usar a saída para treinar outros modelos: não há.** Nem no `LICENSE` Apache-2.0, nem no cartão. Atribuição: a Apache-2.0 exige atribuição ao redistribuir os **pesos** (ou derivados deles); texto gerado não é redistribuição dos pesos. Uso comercial: permitido pela Apache-2.0. Os modelos **não são gated** (`gated: False`), não há termos a aceitar.
- **Origem:** os "qwen" são continuação de pré-treino de bases Qwen3 (Apache-2.0) com troca de tokenizador por transplante OMP; ~50B tokens (0,5B e 3,7B) e ~100B tokens (1,5B) (paper, seção 8). O cartão de terceiro https://huggingface.co/2DTi/tucano2-0.5b-instruct-gguf afirma que o 0,5B vem do Qwen3-0.6B-Base (fonte secundária). O 0,6B-Base é Llama treinado do zero.
- **Tokenizador:** BPE com normalização SentencePiece, **49.152 tokens**, treinado em 40% português, 40% inglês, 20% código; fertilidade 1,51 e 2,88 caracteres por token (paper, seção 4); `vocab_size: 49152` nos `config.json`.
- **Contexto:** 4.096 tokens (`max_position_embeddings` e cartão). O paper reconhece fraqueza em contexto longo (RULER-PT cai a 0,42 a 0,69 em 4k nos Instruct).
- **Pós-treino:** SFT (5 épocas) seguido de Anchored Preference Optimization, com `gigaverbo-v2-sft` e `gigaverbo-v2-preferences`. Think = treino só em tarefas com raciocínio (`<think>`); o detalhe exato da recompensa [NÃO CONFIRMADO, seção 9.4.2 não lida em detalhe].
- **Parâmetros de geração do cartão:** temperature 0,1, top_k 50, repetition_penalty 1,2, max_new_tokens 150. O cartão avisa de alucinação e loops de repetição.

Benchmarks dos Instruct (cartão 0,5B; avaliações do próprio grupo, `verified: False`):

| | MMLU-PT | ENEM | ARC | BELEBELE | GSM8K-PT | IFEval-PT (prompt) | HumanEval |
|---|---|---|---|---|---|---|---|
| 0,5B | 41,5 | 53,6 | 38,6 | 62,3 | 18,5 | 30,0 | 10,4 |
| 1,5B | (ver cartão) | 62,7 | 50,3 | 77,6 | 19,7 | 34,3 | 26,2 |
| 3,7B | 64,6 | 72,9 | 60,3 | 85,2 | 53,8 | 41,7 | 47,6 |

(Os números de ENEM/ARC/BELEBELE/GSM8K/IFEval/HumanEval de 1,5B e 3,7B vêm da tabela "Individual Benchmarks" do cartão do 0,5B; MMLU de 0,5B e 3,7B, da API. O MMLU do 1,5B vi como 52,5 na mesma tabela, a API devolveu 41,46 por herança do cartão, então trate o MMLU do 1,5B como incerto.)

## 3. Tamanho, RAM e CPU do notebook (8 CPUs, 7 GB)

Tamanho em disco bf16 = parâmetros x 2 bytes (confirmado: `model.safetensors`, 3,7B em 2 partes). Os demais são **[ESTIMATIVA]**.

| Modelo | bf16 | int8 | 4 bits | KV cache a 4k |
|---|---|---|---|---|
| 0,5B | 0,98 GB | ~0,5 GB | ~0,3 GB (GGUF Q4_K_M real: 306 MB) | ~0,47 GB |
| 1,5B | 3,02 GB | ~1,5 GB | ~0,93 GB (GGUF Q4_K_M de terceiro: 930 MB) | ~0,47 GB |
| 3,7B | 7,52 GB | ~3,8 GB | ~2,3 GB | ~0,6 GB |

KV cache calculado da `config.json`: camadas x 2 x 8 cabeças KV x 128 x 2 bytes por token (aprox. 115 KB/token nos 0,5B e 1,5B, 147 KB/token no 3,7B).

- **Cabem na RAM de 7 GB:** 0,5B (qualquer formato), 1,5B (int8 ou 4 bits; bf16 apertado), 3,7B só em 4 bits ou int8 e já sem folga para o resto do Apolo.
- **Velocidade de geração na CPU [ESTIMATIVA, não medida]:** a geração é limitada pela banda de memória: tokens/s ≈ banda efetiva / bytes do modelo. Assumindo ~20 GB/s efetivos num notebook DDR4 de dois canais: 0,5B Q4 ~30 a 60 tok/s, 1,5B Q4 ~10 a 20, 3,7B Q4 ~4 a 8. Em PyTorch bf16 puro na CPU, bem pior. Não encontrei benchmark publicado de llama.cpp para Tucano 2 nem para modelos Qwen3 equivalentes [NÃO CONFIRMADO]. A célula opcional de CPU em `avaliar_colab.ipynb` mede de verdade.
- **GGUF:** a organização Polygl0t **não publica GGUF oficial** (listagem de modelos do autor). Existem de terceiros: [2DTi/tucano2-0.5b-instruct-gguf](https://huggingface.co/2DTi/tucano2-0.5b-instruct-gguf) (Q4_K_M, 306 MB; o cartão diz que o conversor padrão do llama.cpp não reconhece o tokenizador e que foi preciso um script próprio, `convert_tucano2.py`), [sandrogomes42/tucano2-0.5b-instruct-gguf](https://huggingface.co/sandrogomes42/tucano2-0.5b-instruct-gguf), [ayodkay/tucano2-qwen-1.5b-instruct-Q4_K_M](https://huggingface.co/ayodkay/tucano2-qwen-1.5b-instruct-Q4_K_M) (930 MB) e [mradermacher/Tucano2-0.6B-Base-GGUF](https://huggingface.co/mradermacher/Tucano2-0.6B-Base-GGUF). Não os testei: **não use em produção sem conferir a tokenização.** Há também MLX 4 bits de [pessini](https://huggingface.co/pessini/Tucano2-qwen-1.5B-Instruct-MLX-4bit) (para Apple, irrelevante aqui).

## 4. GigaVerbo-v2 (dataset de pré-treino)

Fonte: https://huggingface.co/datasets/Polygl0t/gigaverbo-v2 (cartão atualizado em 27/09/2026) e API do HF.

- **Acesso:** `gated: False`; qualquer um baixa, sem aceitar termos. Para o script no Colab não precisa de token (HF_TOKEN só melhora o limite de requisições).
- **Licença: `license: other`.** Texto do cartão (Licensing Information): "Please refer to the individual licenses of the source datasets ... The combined dataset does not have a single unified license, and users should ensure compliance with the terms of each source dataset." Fontes listadas: Common Crawl, FineWeb-2, FinePDFs, mC4, CulturaX (ODC-By 1.0 e termos do Common Crawl, com atribuição), HPLT, OSCAR, CrawlPT (CC0), LegalPT, Quati, Carolina, BDTD, cosmos_qa (CC-BY-4.0), Wikipedia e Wikiquote e Dolly-pt (CC-BY-SA-3.0, com compartilhamento pela mesma licença), **XL-Sum (CC-BY-NC-SA-4.0) e Bactrian-X (CC-BY-NC-4.0), ambos não comerciais**, UltrachatBR (MIT), blogset-br (Apache-2.0), livros de domínio público. Não sei quantos documentos dessas fontes NC estão no subconjunto educativo [NÃO CONFIRMADO]; o campo `subset` de cada documento permite descobrir (o script grava só o texto).
- **Subconjuntos (configs)**, cada um só com split `train`:

| Config | Critério | Linhas | Tamanho (cartão) | Tokens |
|---|---|---|---|---|
| `edu_high` (padrão) | `edu_int_score` >= 4 e `toxic_int_score` <= 3 | 16.245.599 | 70,96 GB | 27,9 bi |
| `edu_medium` | `edu_int_score` = 3 e toxic <= 3 | 70.973.605 | 223,66 GB | 89,0 bi |
| `edu_low` | `edu_int_score` <= 2 e toxic <= 3 | 284.889.372 | 469,97 GB | 200,8 bi |
| `nsfw` | `toxic_int_score` >= 4 | 2.892.095 | 7,25 GB | 3,0 bi |

  Total 375 milhões de documentos, 771,84 GB, 320,7 bi de tokens (o paper diz ~318 bi não tóxicos e ~119 bi educativos). Educativo (>= 3) = `edu_high` + `edu_medium`: **116,9 bi de tokens, ~295 GB**. Nunca baixe tudo; use streaming.
- **Campos:** `text`, `id`, `source`, `subset` (origem, ex. `fineweb_2_pt`), `token_count`, `edu_score` (float), **`edu_int_score` (int, 1 a 5)**, `toxic_score`, `toxic_int_score`.
- **Escala de valor educativo:** 1 = não educativo, 5 = altamente educativo (escala Likert de 5 pontos, "adequação para uso educacional, primário a secundário"). Rótulos gerados por Qwen2.5-32B-Instruct e propagados por um classificador BERTimbau-large ([Polygl0t/portuguese-bertimbau-large-edu-classifier](https://huggingface.co/Polygl0t/portuguese-bertimbau-large-edu-classifier)); o paper define educativo como score >= 3. Aviso: é um classificador sobre texto, sem garantia de correção factual.
- **Como filtrar >= 3:** concatenar as configs `edu_high` e `edu_medium` (o cartão mostra exatamente isso), ou carregar uma e filtrar por `edu_int_score >= 3`. É o que `baixar_gigaverbo_edu.py` faz, em streaming.
- **Outros datasets do grupo** (`Polygl0t/`): [gigaverbo-v2-synth](https://huggingface.co/datasets/Polygl0t/gigaverbo-v2-synth) (11,2 milhões de textos sintéticos, 26 GB, gerados por Qwen2.5-7B/14B/32B-Instruct, Apache-2.0 conforme o cartão e o `LICENSE`), [gigaverbo-v2-sft](https://huggingface.co/datasets/Polygl0t/gigaverbo-v2-sft) (4,09 milhões de exemplos, 4,4 GB, 12 subconjuntos, Apache-2.0), [gigaverbo-v2-preferences](https://huggingface.co/datasets/Polygl0t/gigaverbo-v2-preferences) (Apache-2.0). Todos `gated: False`.

## 5. Licença da saída do Tucano para treinar o córtex

1. Os pesos são Apache-2.0: sem cláusula de "não treinar outros modelos com a saída", sem exigência de atribuir texto gerado, uso comercial livre.
2. A cadeia a montante também é Apache-2.0: Qwen3 (segundo o paper), Qwen2.5-7B/14B/32B-Instruct (confirmado na API do HF: `apache-2.0`), geradores dos dados de SFT e sintéticos. O Qwen2.5-3B e o 72B têm licença própria, mas o cartão não cita esses. 
3. Resíduo de risco: o modelo foi pré-treinado em web com fontes de licenças variadas (inclusive NC). Saída nova (paráfrase, explicação) tem risco baixo; cópia literal de trecho memorizado é o risco real. Filtre cópias.
4. O risco prático dominante é **qualidade**, não licença: modelo de 0,5B a 1,5B alucina e erra código (HumanEval 10% e 26%). Por isso o `professor_colab.ipynb` marca tudo como `revisar`.
5. O dono disse "esquece o Claude": nada aqui usa a API do Claude.

## 6. O que NÃO consegui confirmar

- Benchmarks reais de velocidade em CPU (llama.cpp ou transformers) para Tucano 2 ou Qwen3 de mesmo tamanho; os tokens/s acima são conta de banda de memória.
- Apêndice C.1 do paper (fontes e licenças) e seção 9.4.2 (treino do Think) não foram lidos linha a linha; li só os trechos que casaram com buscas locais no HTML.
- Fração de documentos de fontes não comerciais dentro de `edu_high`/`edu_medium`.
- Se o MMLU do 1,5B é 41,5 ou 52,5 (os números do cartão divergem entre a API e a tabela).
- Funcionamento real dos GGUF de terceiros e a correção do tokenizador deles.
- O script de download não foi rodado contra o dataset real (só testado com textos de mentira). A taxa de aceitação depois do filtro de caracteres e dos 80 caracteres mínimos é desconhecida; faça uma execução de teste com `--mb 5`.

## 7. Arquivos desta pasta

- `LEIAME.md`: este relatório.
- `avaliar_colab.ipynb`: carrega o 0,5B e o 1,5B Instruct, roda 29 prompts fixos (saudação, identidade, fatos, programação, paráfrase, explicar código), mede latência, tokens/s e pico de memória da GPU, salva JSON em `Drive/apolo/tucano_avaliacao/`. Célula opcional de CPU no final.
- `professor_colab.ipynb`: aviso de licença no topo; modo paráfrases (JSON em `perguntas.json`, saída JSON e CSV) e modo explicar código (`codigos.json`); filtra caracteres como o `montar_corpus.py`; tudo sai com `status: revisar`.
- `baixar_gigaverbo_edu.py`: streaming de `edu_high` + `edu_medium`, limpeza igual à do `montar_corpus.py`, saída `gigaverbo_edu.txt`. Uso no Colab: `pip install datasets && python baixar_gigaverbo_edu.py --mb 100`.
- `tests/test_limpeza.py`: `python3 tucano/tests/test_limpeza.py` (10 testes, incluindo um que avisa se `PERMITIDOS`/`TROCAS`/`RUIM` do `montar_corpus.py` mudarem e a cópia ficar defasada).
