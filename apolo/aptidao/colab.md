# Rodar a aptidão no Colab (sem servidor)

O Colab não tem Docker. O corretor roda código gerado, então **não o execute direto no Colab sem isolamento**.
O jeito mais seguro: gerar os textos no Colab (precisa de torch/GPU) e corrigir na sua máquina, onde há Docker.

## 1. No Colab: gerar com o modelo recém-treinado

```python
# repositório (ou a pasta do projeto) já copiado para /content/apolo, com cortex.pt e config.json em /content/cerebro
%cd /content/apolo
!python3 aptidao/rodar.py --modelo-local /content/cerebro --n 100 --semente 9000 --temperatura 0.2 --rotulo v3_medio --so-gerar
```

`--modelo-local PASTA` carrega `PASTA/cortex.pt` e `PASTA/config.json` com `cortex_v0.carregar()` e gera com
`cortex_v0.continuar()`. Sem `torch` instalado o modo se desliga com uma mensagem de erro clara.
Baixe `aptidao/resultados/v3_medio.jsonl` (contém só os textos gerados).

## 2. Na sua máquina: corrigir

```bash
cp v3_medio.jsonl aptidao/resultados/
python3 aptidao/rodar.py --n 100 --semente 9000 --rotulo v3_medio   # usa os textos já gerados; só corrige
```

Use os mesmos `--n`, `--semente` e `--categorias` das duas etapas. Se o Colab tiver Docker disponível
(não é o normal), basta tirar `--so-gerar`.
