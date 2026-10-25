import express from 'express';
import { coletarCodigos } from './codigos.js';
import { codigosDoStackExchange } from './stackexchange.js';
import { ler, pesquisar, lerBlocos, comPagina } from './navegador.js';
import { conhecer } from './adaptadores/index.js';
import { criarCtx } from './adaptadores/ctx.js';

const app = express();
app.use(express.json());

// O Chromium é pesado: no máximo duas tarefas ao mesmo tempo, o resto espera na fila.
let ocupadas = 0;
const fila = [];
async function limitado(tarefa) {
  if (ocupadas >= 2) await new Promise((ok) => fila.push(ok));
  ocupadas++;
  try {
    return await tarefa();
  } finally {
    ocupadas--;
    fila.shift()?.();
  }
}

const assincrono = (fn) => (req, res, next) => fn(req, res).catch(next);

app.get('/saude', (_req, res) => res.json({ ok: true }));

app.post('/pesquisar', assincrono(async (req, res) => {
  const consulta = String(req.body?.consulta ?? '').trim().slice(0, 200);
  if (!consulta) return res.status(400).json({ erro: 'consulta é obrigatória' });
  const max = Math.min(Number(req.body?.max) || 5, 10);
  res.json({ consulta, resultados: await limitado(() => pesquisar(consulta, { max })) });
}));

app.post('/codigos', assincrono(async (req, res) => {
  const consulta = String(req.body?.consulta ?? '').trim().slice(0, 200);
  if (!consulta) return res.status(400).json({ erro: 'consulta é obrigatória' });
  const maxPaginas = Math.max(1, Math.min(Math.floor(Number(req.body?.max_paginas) || 3), 3));
  // Primeiro a API do Stack Exchange (respostas aceitas, código confiável); o navegador fica de reserva.
  let codigos = await codigosDoStackExchange(consulta);
  if (!codigos.length) codigos = await limitado(() => coletarCodigos(consulta, { pesquisar, lerBlocos, maxPaginas }));
  res.json({ codigos });
}));

// Conhecimento estruturado de várias fontes (adaptadores por site): fatos, conceitos, pares, atributos e código.
app.post('/conhecer', assincrono(async (req, res) => {
  const consulta = String(req.body?.consulta ?? '').trim().slice(0, 200);
  if (!consulta) return res.status(400).json({ erro: 'consulta é obrigatória' });
  res.json(await conhecer(consulta, criarCtx({ navegador: (url, fn) => limitado(() => comPagina((p) => p.goto(url, { waitUntil: 'domcontentloaded' }).then(() => fn(p)))), registrar: (m) => console.warn(m) })));
}));

app.post('/ler', assincrono(async (req, res) => {
  const url = String(req.body?.url ?? '');
  if (!url) return res.status(400).json({ erro: 'url é obrigatória' });
  res.json(await limitado(() => ler(url)));
}));

app.use((erro, _req, res, _next) => {
  console.error(erro);
  res.status(502).json({ erro: String(erro.message ?? erro) });
});

app.listen(4000, () => console.log('Pesquisa (Playwright) ouvindo em http://localhost:4000'));
