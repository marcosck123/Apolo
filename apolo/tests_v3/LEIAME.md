# Testes do córtex v3

Arquivos novos (nenhum do v0 foi tocado): `cortex_v3.py`, `tokenizador_bpe.py`, `treino_colab_v3.ipynb`, `Dockerfile.cortex` (acrescentou `tokenizers==0.21.1` e `numpy`) e esta pasta.

## Como rodar (no container, repo montado em /work)

```
sg docker -c "docker compose --profile cortex run --rm --no-deps cortex python -m unittest discover -s tests_v3 -v"
sg docker -c "docker compose --profile cortex run --rm --no-deps cortex python tests_v3/medir_latencia.py"   # 80 tokens do medio na CPU
sg docker -c "docker compose --profile cortex run --rm --no-deps cortex python cortex_v3.py tamanhos"        # parâmetros de cada tamanho
```

Se a imagem ainda for a antiga (sem `tokenizers`), reconstrua-a com `docker compose --profile cortex build cortex` (cuidado: não recrie o `cortex-api` em uso) ou rode `pip install tokenizers==0.21.1 numpy` dentro do container antes. Sem `tokenizers` o BPE cai no motor em Python puro (lento, mas funciona).

## O que é testado
Formas e perda inicial; ausência de embedding de posição; RoPE (só a distância importa); equivalência numérica com e sem KV cache (logits e amostras); janela deslizante; parada antecipada; agenda WSD; BPE (ida e volta em `textos/curriculo/*.txt`, caracteres especiais, emoji, JSON, motor puro); BPC; perda cai em 20 passos (`mini`); retomada exata (6 passos contínuos == 5 + retomar 1: perda do passo 6 e pesos finais idênticos); `--estender`; servidor `/saude`, `/gerar` e `parar_em`.
Os testes usam modelo `mini` aleatório e dados em `tests_v3/dados/` (gerados do currículo). Não treinam nada de verdade.

## Decisões
- RoPE gira q e k; o cache guarda k já girado. Ao estourar o contexto, descarta-se o cache mais antigo (a atenção passa a ver só os últimos `contexto` tokens; difere levemente de recalcular a janela, só depois de estourar).
- Sem viés em nenhuma camada. Weight decay (0,1) só em matrizes das camadas lineares; normas e embedding ficam fora.
- MLP SwiGLU com largura ≈ 8/3·d (múltiplo de 64 mais próximo): 2048 no `medio`.
- Checkpoint completo (`checkpoint.pt`: modelo, otimizador, GradScaler, passo, RNGs, config, tokenizador) + `modelo.pt` leve no fim. Escrita atômica (.tmp + rename), mantendo `_anterior.pt`.
- Validação: `--val_dados` (contrato com o agente 1: `textos/corpus_validacao.txt`); sem ele, 2% finais com AVISO de possível contaminação.
- Perda por token só é comparável dentro do mesmo tokenizador; compare v2 x v3 pelo BPC.
- Servidor: mesma API do v0 (`/saude`, `/gerar {inicio,n,temperatura}`) mais `parar_em` (padrão `["\n\n"]`; `[]` desliga). Para trocar no compose: `python -u -W ignore cortex_v3.py servir --porta 8000 --pasta cerebro_v3_medio`.
