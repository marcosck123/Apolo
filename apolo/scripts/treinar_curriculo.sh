#!/usr/bin/env bash
# Treina o córtex "mini" com o currículo básico (textos/curriculo/), mostrando o progresso ao vivo.
# Uso (dentro do Debian/WSL, na pasta do projeto): bash scripts/treinar_curriculo.sh [passos]
set -e
PASSOS="${1:-3000}"
docker compose run --rm cortex python -u -W ignore cortex_v0.py treinar \
  --dados textos/curriculo --tamanho mini --passos "$PASSOS" --avaliar_cada 100 2>&1 | tee cerebro/treino.log
echo
echo "=== gerar a partir do modelo salvo"
docker compose run --rm cortex python -u -W ignore cortex_v0.py gerar --inicio "Qual é o seu nome?" --n 150
