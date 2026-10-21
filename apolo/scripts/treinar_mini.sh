#!/usr/bin/env bash
# Treina o córtex "mini" mostrando o progresso ao vivo (python -u = sem buffer).
# Uso (dentro do Debian/WSL, na pasta do projeto): bash scripts/treinar_mini.sh [passos]
set -e
PASSOS="${1:-500}"
docker compose run --rm cortex python -u -W ignore cortex_v0.py treinar \
  --dados textos/exemplo.txt --tamanho mini --passos "$PASSOS" --avaliar_cada 50
echo
echo "=== gerar a partir do modelo salvo"
docker compose run --rm cortex python -u -W ignore cortex_v0.py gerar --inicio "O menino olhou para" --n 150
