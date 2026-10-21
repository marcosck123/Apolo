import express from 'express';
import { criarApolo } from './apolo.js';
import { criarRepositorio } from './repositorio.js';

const repo = criarRepositorio();
const apolo = criarApolo({ repo });

const app = express();
app.use(express.json());

const assincrono = (fn) => (req, res, next) => fn(req, res).catch(next);
const textoValido = (v) => typeof v === 'string' && v.trim().length > 0;

app.post('/lembrar', assincrono(async (req, res) => {
  const { conteudo, tipo } = req.body ?? {};
  if (!textoValido(conteudo)) return res.status(400).json({ erro: 'conteudo é obrigatório' });
  if (tipo && !['conceito', 'habilidade', 'fato'].includes(tipo)) {
    return res.status(400).json({ erro: 'tipo deve ser conceito, habilidade ou fato' });
  }
  res.status(201).json(await apolo.lembrar({ conteudo, tipo }));
}));

app.post('/pensar', assincrono(async (req, res) => {
  const { mensagem } = req.body ?? {};
  if (!textoValido(mensagem)) return res.status(400).json({ erro: 'mensagem é obrigatória' });
  res.json(await apolo.pensar(mensagem));
}));

app.get('/neuronios/:id', assincrono(async (req, res) => {
  const neuronio = await repo.buscarNeuronio(Number(req.params.id));
  if (!neuronio) return res.status(404).json({ erro: 'neurônio não encontrado' });
  res.json(neuronio);
}));

app.post('/dormir', assincrono(async (_req, res) => {
  res.json(await apolo.dormir());
}));

app.use((erro, _req, res, _next) => {
  console.error(erro);
  res.status(500).json({ erro: 'erro interno' });
});

const porta = Number(process.env.PORT ?? 3000);
app.listen(porta, () => console.log(`Apolo ouvindo em http://localhost:${porta}`));
