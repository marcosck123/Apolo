import { criarEstudante } from './estudante.js';
import express from 'express';
import { criarAnalisador, criarBuscadorDeCodigos, criarExecutor, criarRespostaDeCodigo, ehPerguntaDeProgramacao } from './codigo.js';
import { fileURLToPath } from 'node:url';
import { criarApolo } from './apolo.js';
import { criarRaciocinador } from './cortex.js';
import { criarDetector, normalizar } from './intencoes.js';
import { INTENCOES_PADRAO } from './intencoes_padrao.js';
import { criarLog } from './log.js';
import { responderSobreMim } from './eu.js';
import { ehPergunta, palavrasChave, responderDaMemoria } from './raciocinio.js';
import { criarPesquisa, criarPesquisador, extrairConsulta } from './pesquisa.js';
import { criarAprendizado, criarConhecedor, criarLimitador, reconhecerEsquecer } from './conhecimento.js';
import { criarRepositorio } from './repositorio.js';
import { carregarTreino } from './treino.js';

const repo = criarRepositorio();
const cortex = criarRaciocinador();
if (!cortex) console.warn('CORTEX_URL ausente: /pensar só devolve a memória, sem resposta.');
const log = criarLog();
const pesquisador = criarPesquisador();
if (!pesquisador) console.warn('PESQUISA_URL ausente: "pesquise X" não consegue olhar a internet.');

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
async function raciocinar({ mensagem: original, memoria }) {
  const mensagem = original.replace(/\boque\b/gi, 'o que'); // "oque significa" é "o que significa"
  const entendida = detector.detectar(mensagem);
  if (entendida) {
    log.registrar('entendeu', { texto: mensagem, intencao: entendida.intencao });
    return entendida.resposta;
  }
  const sobreMim = responderSobreMim(mensagem);
  if (sobreMim) { log.registrar('entendeu', { texto: mensagem, intencao: 'sobre_mim' }); return sobreMim; }
  const esquecer = reconhecerEsquecer(mensagem);
  if (esquecer) {
    const apagados = await aprendizado.esquecer(esquecer);
    return apagados ? `Esqueci ${apagados} ${apagados === 1 ? 'coisa' : 'coisas'} que aprendi na internet.` : 'Não achei nada pesquisado para esquecer.';
  }
  const consulta = extrairConsulta(mensagem);
  if (consulta) return (await aprendizado.aprender(consulta)) ?? pesquisarNaInternet(consulta);
  // O que já sabe responde antes do córtex, que só sabe continuar textos.
  // Além do que o grafo ativou, procura direto por palavras: fatos recém-aprendidos nem sempre entram na cascata.
  const jaAtivos = new Set(memoria.map((m) => m.id));
  const achados = (await repo.buscarFatosPorPalavras([...palavrasChave(mensagem)])).filter((n) => !jaAtivos.has(n.id));
  const lembranca = responderDaMemoria({ mensagem, memoria: [...memoria, ...achados.map((n) => ({ ...n, ativacao: 0 }))] });
  if (lembranca) {
    log.registrar('recordou', { texto: mensagem, neuronioId: lembranca.neuronioId });
    return { resposta: lembranca.resposta, via: 'memoria', neuronioId: lembranca.neuronioId };
  }
  if (ehPerguntaDeProgramacao(mensagem)) {
    const resposta = await responderComCodigo(mensagem);
    if (resposta) return resposta;
    const aprendida = await aprendizado.aprender(mensagem);
    if (aprendida) return aprendida;
    log.registrar('desconheceu', { texto: mensagem });
    return `Ainda não sei isso. Se quiser, peça: pesquise ${mensagem.trim().replace(/[?\s]+$/, '')}`;
  }
  // Pergunta sem fato na memória: o córtex só inventaria, então o Apolo admite e oferece pesquisar.
  if (ehPergunta(mensagem)) {
    // Antes de admitir que não sabe, pesquisa e aprende (desligável com PESQUISA_AUTO=0).
    const aprendida = await aprendizado.aprender(mensagem);
    if (aprendida) return aprendida;
    log.registrar('desconheceu', { texto: mensagem });
    return `Ainda não sei isso. Se quiser, peça: pesquise ${mensagem.trim().replace(/[?\s]+$/, '')}`;
  }
  const continuacao = cortex ? await cortex({ mensagem, memoria }) : null;
  return continuacao ? { resposta: continuacao, via: 'cortex' } : null;
}
const apolo = criarApolo({ repo, raciocinar });
// `apolo` só existe depois de `raciocinar`; a pesquisa o usa para guardar o que achou como fatos.
const pesquisarNaInternet = criarPesquisa({
  pesquisador,
  lembrar: (fato) => apolo.lembrar(fato),
  registrar: log.registrar,
});

// Aprende sozinho: usa a rota /conhecer (adaptadores por site) e guarda fatos, atributos e conceitos com origem `web`.
const aprendizado = criarAprendizado({
  conhecer: criarConhecedor(), lembrar: (n) => apolo.lembrar(n), repo,
  registrar: log.registrar, habilitado: process.env.PESQUISA_AUTO !== '0', limitador: criarLimitador(),
});

const responderComCodigo = criarRespostaDeCodigo({
  buscar: criarBuscadorDeCodigos(), executar: criarExecutor(),
  enfileirar: (id) => repo.enfileirarEstudo(id),
  lembrar: (habilidade) => apolo.lembrar(habilidade), registrar: log.registrar,
});

let pensamentosAtivos = 0, ultimoPensamento = Date.now();
const estudante = criarEstudante({
  repo, lembrar: (n) => apolo.lembrar(n), analisar: criarAnalisador(), executar: criarExecutor(),
  registrar: log.registrar, habilitado: process.env.ESTUDO !== '0',
  intervalo: Math.max(100, Number(process.env.ESTUDO_INTERVALO_MS) || 5000),
  ocioso: () => pensamentosAtivos === 0 && Date.now() - ultimoPensamento >= 30_000,
});
estudante.iniciar();

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

app.use('/pensar', (_req, res, next) => {
  pensamentosAtivos++;
  ultimoPensamento = Date.now();
  let encerrado = false;
  const encerrar = () => { if (!encerrado) { encerrado = true; pensamentosAtivos--; ultimoPensamento = Date.now(); } };
  res.once('finish', encerrar);
  res.once('close', encerrar);
  next();
});

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
  const id = Number(req.params.id);
  if (!Number.isInteger(id) || id < 1) return res.status(400).json({ erro: 'id inválido' });
  const neuronio = await repo.buscarNeuronio(id);
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
