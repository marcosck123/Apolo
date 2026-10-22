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
