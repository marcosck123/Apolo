import assert from 'node:assert/strict';
import { test } from 'node:test';
import { criarRaciocinador, montarPrompt } from '../src/cortex.js';

const memoria = [
  { conteudo: 'pouco ativo', ativacao: 0.2 },
  { conteudo: 'muito ativo\nsegunda linha', ativacao: 0.9 },
];

test('criarRaciocinador: sem CORTEX_URL não cria o córtex', () => {
  assert.equal(criarRaciocinador({ url: '' }), null);
});

test('montarPrompt: memória por ativação crescente, mensagem por último', () => {
  assert.equal(montarPrompt({ mensagem: 'oi', memoria }), 'pouco ativo\nmuito ativo\noi\n');
  assert.equal(montarPrompt({ mensagem: 'oi', memoria: [] }), 'oi\n');
});

test('raciocinar: envia o prompt ao córtex e devolve o texto gerado', async () => {
  let enviado;
  const fetchFn = async (url, opcoes) => {
    enviado = { url: String(url), corpo: JSON.parse(opcoes.body) };
    return { ok: true, json: async () => ({ texto: ' o menino olhou. ' }) };
  };
  const raciocinar = criarRaciocinador({ url: 'http://cortex:8000', fetchFn });
  assert.equal(await raciocinar({ mensagem: 'oi', memoria }), 'o menino olhou.');
  assert.equal(enviado.url, 'http://cortex:8000/gerar');
  assert.equal(enviado.corpo.inicio, 'pouco ativo\nmuito ativo\noi\n');
});

test('raciocinar: córtex fora do ar não derruba o pensamento', async () => {
  const fetchFn = async () => { throw new Error('ECONNREFUSED'); };
  const raciocinar = criarRaciocinador({ url: 'http://cortex:8000', fetchFn });
  assert.equal(await raciocinar({ mensagem: 'oi', memoria: [] }), null);
});

test('raciocinar: erro HTTP também degrada para null', async () => {
  const fetchFn = async () => ({ ok: false, status: 500, text: async () => 'falhou' });
  const raciocinar = criarRaciocinador({ url: 'http://cortex:8000', fetchFn });
  assert.equal(await raciocinar({ mensagem: 'oi', memoria: [] }), null);
});

test('raciocinar: fica só com o primeiro parágrafo da geração', async () => {
  const fetchFn = async () => ({ ok: true, json: async () => ({ texto: 'Olá! Tudo bem?\n\nTchau.\nTchau, até a próxima.' }) });
  const raciocinar = criarRaciocinador({ url: 'http://cortex:8000', fetchFn });
  assert.equal(await raciocinar({ mensagem: 'oi', memoria: [] }), 'Olá! Tudo bem?');
});
