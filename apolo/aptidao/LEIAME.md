# Aptidão: medir se uma versão nova do córtex melhorou

Gera problemas de programação **novos**, pede a solução ao córtex, executa o código gerado num
container Docker isolado e compara a saída com a esperada (pass@1, com intervalo de confiança de Wilson).

## Como rodar

```bash
# 1. imagem do corretor (uma vez; python:3.13-slim + git)
docker build -t apolo-aptidao:py313 aptidao/          # ou: sg docker -c "docker build ..."
# 2. medir (córtex servido em localhost:8000)
python3 aptidao/rodar.py --url http://localhost:8000 --n 100 --semente 9000 --temperatura 0.2 --rotulo v2_medio
# 3. comparar duas versões (mesma --semente e --n!)
python3 aptidao/rodar.py --comparar aptidao/resultados/v1.jsonl aptidao/resultados/v2_medio.jsonl
# sem córtex: testar o corretor com modelos de mentira (oraculo | vazio | quase | lixo)
python3 aptidao/rodar.py --modelo-falso oraculo --n 100
# testes automáticos
python3 -m unittest discover -s aptidao/tests -v
```

Se a execução for interrompida, rode o mesmo comando de novo com o mesmo `--rotulo`: o que já foi
gerado em `aptidao/resultados/<rotulo>.jsonl` não é pedido outra vez. Para o Colab, veja `colab.md`.

## O que mede

- Categorias: `python_basico`, `python_intermediario`, `python_extra`, `sql`, `terminal` (JavaScript ficou de fora).
- Cada problema usa as mesmas famílias de exercícios do treino, mas com sementes 9000+ (o treino usou 6 a 11),
  e problemas cujo enunciado exato aparece em `textos/corpus_portugues.txt` ou `textos/curriculo/` são descartados.
- Acerto = o código gerado (do início até `Saída:` ou a primeira linha em branco) roda no container
  (sem rede, sistema de arquivos somente leitura, 10 s, memória limitada) e imprime a mesma saída
  que a referência (igualdade exata após strip por linha).

## O que NÃO mede

- Não mede resolução de problemas inéditos: só **generalização sobre variações de números, nomes e
  palavras dentro das famílias de exercícios conhecidas**. Um 100% aqui não significa que o córtex programa.
- Não mede qualidade do texto em português, explicações, nem conhecimento geral.
- O anti-contaminação compara só o enunciado exato; um enunciado diferente com a mesma solução passa.
  Famílias com poucas variações (ex.: SQL) esgotam: o gerador pode devolver menos problemas que o pedido.

## Como interpretar

- Compare sempre com a **mesma semente, `--n` e temperatura**. Com 100 problemas, o intervalo de 95% tem
  cerca de ±10 pontos: diferenças menores que isso são ruído. Use `--n 300` ou mais para versões parecidas.
- O arquivo `.jsonl` guarda texto gerado, saída obtida e `motivo` (`ok`, `saida_diferente`, `erro`,
  `timeout`, `vazio`): olhe os erros antes de confiar só no número.
- Temperatura baixa (0.2) mede o "melhor palpite" do modelo; o resultado varia pouco entre execuções.
