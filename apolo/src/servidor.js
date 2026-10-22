import express from 'express';
import { fileURLToPath } from 'node:url';
import { criarApolo } from './apolo.js';
import { criarRaciocinador } from './cortex.js';
import { criarDetector, normalizar } from './intencoes.js';
import { INTENCOES_PADRAO } from './intencoes_padrao.js';
import { criarLog } from './log.js';
import { criarRepositorio } from './repositorio.js';
import { carregarTreino } from './treino.js';

const repo = criarRepositorio();
const cortex = criarRaciocinador();
if (!cortex) console.warn('CORTEX_URL ausente: /pensar só devolve a memória, sem resposta.');
const log = criarLog();

// Intenções vivem no banco; o índice em memória é refeito sempre que algo é ensinado.
let detector = criarDetector([]);
async function recarregarIntencoes() {
  detector = criarDetector(await repo.carregarIntencoes());
}
if ((await repo.carregarIntencoes()).length === 0) {
  for (const g of INTENCOES_PADRAO) {
    await repo.garantirIntencao(g.nome);
    for (const f of g.frases) await repo.ensinarFrase(g.nome, f);
    for (const r of g.respostas) await repo.ensinarResposta(g.nome, r.texto, r.quando ?? null);
  }
}
await recarregarIntencoes();

// Primeiro tenta entender a intenção (saudação, despedida...); só o que sobra vai para o córtex.
async function raciocinar({ mensagem, memoria }) {
  const entendida = detector.detectar(mensagem);
  if (entendida) {
    log.registrar('entendeu', { texto: mensagem, intencao: entendida.intencao });
    return entendida.resposta;
  }
  return cortex ? cortex({ mensagem, memoria }) : null;
}
const apolo = criarApolo({ repo, raciocinar });

const app = express();
app.use(express.json());
app.use('/painel', express.static(fileURLToPath(new URL('../painel', import.meta.url))));

const assincrono = (fn) => (req, res, next) => fn(req, res).catch(next);
const textoValido = (v) => typeof v === 'string' && v.trim().length > 0;

app.post('/lembrar', assincrono(async (req, res) => {
  const { conteudo, tipo } = req.body ?? {};
  if (!textoValido(conteudo)) return res.status(400).json({ erro: 'conteudo é obrigatório' });
  if (tipo && !['conceito', 'habilidade', 'fato'].includes(tipo)) {
    return res.status(400).json({ erro: 'tipo deve ser conceito, habilidade ou fato' });
  }
  const neuronio = await apolo.lembrar({ conteudo, tipo });
  log.registrar('lembrou', { neuronioId: neuronio.id, neuronioTipo: neuronio.tipo, texto: conteudo });
  res.status(201).json(neuronio);
}));

app.post('/pensar', assincrono(async (req, res) => {
  const { mensagem } = req.body ?? {};
  if (!textoValido(mensagem)) return res.status(400).json({ erro: 'mensagem é obrigatória' });
  const pensamento = await apolo.pensar(mensagem);
  log.registrar('pensou', {
    texto: mensagem,
    resposta: pensamento.resposta,
    episodioId: pensamento.episodioId,
    ativados: pensamento.memoria.map((m) => ({ id: m.id, ativacao: m.ativacao })),
  });
  res.json(pensamento);
}));

app.get('/neuronios/:id', assincrono(async (req, res) => {
  const neuronio = await repo.buscarNeuronio(Number(req.params.id));
  if (!neuronio) return res.status(404).json({ erro: 'neurônio não encontrado' });
  res.json(neuronio);
}));

app.post('/dormir', assincrono(async (_req, res) => {
  const resultado = await apolo.dormir();
  log.registrar('dormiu', resultado);
  res.json(resultado);
}));

app.get('/grafo', assincrono(async (req, res) => {
  const limite = Math.min(Number(req.query.limite) || 300, 1000);
  res.json(await repo.carregarGrafo({ limite }));
}));

app.get('/intencoes', (_req, res) => res.json(detector.grupos()));

const nomeValido = (v) => typeof v === 'string' && /^[a-z0-9_]{2,40}$/.test(v);

app.post('/intencoes/:nome/frases', assincrono(async (req, res) => {
  const { nome } = req.params;
  const frase = normalizar(String(req.body?.frase ?? ''));
  if (!nomeValido(nome)) return res.status(400).json({ erro: 'nome do grupo: letras minúsculas, números e _ (2 a 40)' });
  if (!frase) return res.status(400).json({ erro: 'frase é obrigatória' });
  await repo.ensinarFrase(nome, frase);
  await recarregarIntencoes();
  log.registrar('ensinou', { texto: `frase "${frase}" no grupo ${nome}` });
  res.status(201).json({ intencao: nome, frase });
}));

app.post('/intencoes/:nome/respostas', assincrono(async (req, res) => {
  const { nome } = req.params;
  const { resposta, quando } = req.body ?? {};
  if (!nomeValido(nome)) return res.status(400).json({ erro: 'nome do grupo: letras minúsculas, números e _ (2 a 40)' });
  if (!textoValido(resposta)) return res.status(400).json({ erro: 'resposta é obrigatória' });
  await repo.ensinarResposta(nome, resposta.trim(), textoValido(quando) ? normalizar(quando) : null);
  await recarregarIntencoes();
  log.registrar('ensinou', { texto: `resposta "${resposta.trim()}" no grupo ${nome}` });
  res.status(201).json({ intencao: nome, resposta: resposta.trim() });
}));

app.get('/treino', assincrono(async (_req, res) => res.json(await carregarTreino())));

app.get('/eventos/recentes', (_req, res) => res.json(log.recentes()));

// Fluxo ao vivo (SSE): o painel recebe cada evento assim que acontece.
app.get('/eventos', (req, res) => {
  res.set({ 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' });
  res.flushHeaders();
  const cancelar = log.assinar((evento) => res.write(`data: ${JSON.stringify(evento)}\n\n`));
  const batida = setInterval(() => res.write(': batida\n\n'), 25000);
  req.on('close', () => {
    clearInterval(batida);
    cancelar();
  });
});

app.use((erro, _req, res, _next) => {
  console.error(erro);
  log.registrar('erro', { texto: String(erro.message ?? erro) });
  res.status(500).json({ erro: 'erro interno' });
});

const porta = Number(process.env.PORT ?? 3000);
app.listen(porta, () => console.log(`Apolo ouvindo em http://localhost:${porta}`));
