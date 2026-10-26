# Apolo

Memória em grafo inspirada no cérebro. O LLM é o córtex que pensa; o grafo é a memória de longo prazo.

## Estrutura

- `src/nucleo/cerebro.js` — o núcleo puro (sem banco): grafo, `propagar` (cascata), `hebb`, `esquecer`.
- `src/embeddings.js` — embedding local de desenvolvimento (hashing de palavras). Trocar por um modelo real.
- `src/repositorio.js` — PostgreSQL + pgvector: sementes por similaridade, vizinhança, sinapses, consolidação.
- `src/apolo.js` — o ciclo do pensamento (`pensar`) e `lembrar`. O LLM entra pelo callback `raciocinar`.
- `src/cortex.js` — o lobo frontal (`raciocinar`): manda a memória ativada + a mensagem como texto inicial ao córtex próprio (`cortex_v0.py servir`, via `CORTEX_URL`) e devolve o que ele escreve. Se o córtex estiver fora do ar, `/pensar` devolve só a memória.
- `cortex_v0.py` — o córtex: GPT pequeno treinado do zero (`treinar`, `gerar`, `servir`).
- `src/servidor.js` — API Express: `POST /lembrar`, `POST /pensar`, `GET /neuronios/:id`, `POST /dormir`.
- `src/pesquisa.js` — os olhos: "pesquise X" chama o serviço `pesquisa/`, guarda os 3 melhores resultados como fatos e responde com o resumo e a fonte.
- `pesquisa/` — serviço à parte (Playwright + Chromium, imagem oficial): `POST /pesquisar` e `POST /ler`. Busca no DuckDuckGo e, se vier vazio, no Bing. `rede.js` barra qualquer endereço da rede interna (SSRF). Sobe com `docker compose --profile pesquisa up -d pesquisa`; sem ele, o Apolo avisa que não consegue pesquisar.
- `db/schema.sql` — tabelas `neuronios` e `sinapses`.

## Rodando

Tudo roda em Docker (Docker Engine dentro do Debian no WSL2; nada é instalado no Windows).
Entre no Debian (`wsl -d Debian`), vá até esta pasta (`/mnt/c/Users/Beatr/OneDrive/Desktop/apolo`) e:

```bash
docker compose up -d --build              # Postgres+pgvector e o app; o schema é aplicado na subida
docker compose run --rm --no-deps app npm test   # núcleo, sem banco
docker compose run --rm app npm run dormir       # consolidação
docker compose --profile cortex up -d cortex-api  # liga o córtex (precisa de cerebro/cortex.pt); sem ele o Apolo só lembra
docker compose stop                       # desliga e libera RAM (os dados ficam no volume)
docker compose down -v                    # desliga e APAGA o banco
```

A API fica em `http://localhost:3000` (o WSL2 repassa a porta para o Windows).
Sem Docker: Node 22.9+, PostgreSQL com `pgvector`, `.env` baseado em `.env.example`.

## Decisões

- Ativação é efêmera: calculada a cada pensamento, não gravada no banco.
- Sinapses são não-direcionadas, uma linha por par (`de < para`).
- Só o hipocampo por enquanto: episódios, fatos e conceitos vivem na mesma tabela, diferenciados por `tipo`.
- Consolidação (`npm run dormir`): decai pesos, poda sinapses fracas, esquece episódios órfãos nunca usados.

## Código da internet, testado no executor

Suba os opcionais com `docker compose --profile pesquisa --profile executor up -d --build`. Perguntas de programação sem resposta na memória buscam exemplos Python, passam por uma triagem e executam até cinco candidatos. A resposta mostra código, saída real e fonte; rodar sem erro não garante correção. O executor roda sem privilégios, sem internet, com limites de recursos e prazo de cinco segundos. Habilidades aprovadas recebem origem `executor`; fatos pesquisados recebem `web`, e lembranças manuais, `usuario` (também há a origem reservada `estudo`). Aplique o schema em bancos existentes com `docker compose exec app npm run migrar`.

### Estudo em segundo plano e exportação

Habilidades do executor entram na fila `estudos`. Após 30 segundos sem `/pensar` em andamento, o estudante analisa Python com AST, cria conceitos de uma tabela revisável e executa até cinco variações determinísticas, além de duas tentativas de erro. Só guarda saídas e erros reais; tudo recebe origem `estudo`. As sinapses usam o mesmo critério de similaridade de `lembrar`. O painel mostra o evento `estudou` com as quantidades. Falhas de serviço voltam à fila até três tentativas; concessões interrompidas podem ser retomadas após dez minutos.

Configure `ESTUDO=0` para desligar ou `ESTUDO_INTERVALO_MS` para ajustar o intervalo (padrão 5000). Aplique a migração com `apolo-docker compose exec -T app npm run migrar`.

Exporte com `apolo-docker compose exec -T app node scripts/exportar_aprendido.js --origens executor,estudo --saida /tmp/aprendido.txt`. Sem `--saida`, grava `textos/curriculo/12_aprendido.txt` dentro do container. O exportador não treina modelos. Remove linhas vazias internas e duplicatas, preserva a indentação e informa blocos por origem. `usuario` é opcional; `web` fica de fora por padrão por licença/atribuição. Exemplos derivados de fontes externas também exigem revisão de licença antes de distribuição.
