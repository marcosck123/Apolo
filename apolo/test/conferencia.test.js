import assert from 'node:assert/strict';
import { test } from 'node:test';
import { criarAprendizado, criarLimitador, selecionar } from '../src/conhecimento.js';

const fato = (adaptador, texto, fonte, extra = {}) => ({ texto, fonte, adaptador, confianca: 'media', ...extra });

test('limitador: bloqueia depois do máximo e libera quando a janela passa', () => {
  let agora = 0;
  const pode = criarLimitador({ max: 2, janelaMs: 1000, agora: () => agora });
  assert.deepEqual([pode(), pode(), pode()], [true, true, false]);
  agora = 1500;
  assert.equal(pode(), true);
});

test('selecionar: números que se contradizem derrubam a fonte de menos confiança', () => {
  const certo = fato('wikipedia', 'Porto Velho foi fundada em 1914 às margens do rio Madeira em Rondônia.', 'https://pt.wikipedia.org/wiki/Porto_Velho', { confianca: 'alta' });
  const errado = fato('brasilescola', 'Porto Velho foi fundada em 1850 às margens do rio Madeira em Rondônia.', 'https://brasilescola.uol.com.br/pv.htm');
  const s = selecionar({ tema: 'porto velho', fatos: [certo, errado] });
  assert.deepEqual(s.fatos.map((f) => f.adaptador), ['wikipedia']);
});

test('selecionar: sites de calculadora não entram, nem como fato nem como par', () => {
  const calc = fato('brasilescola', 'A astrologia calcula a posição dos astros com uma calculadora online grátis.', 'https://www.calculadoraonline.com.br/basica');
  const s = selecionar({ tema: 'astrologia', fatos: [calc], pares: [{ pergunta: 'O que é astrologia?', resposta: 'Uma calculadora de astros online.', fonte: 'https://www.calculadoraonline.com.br/x' }] });
  assert.deepEqual([s.fatos.length, s.pares.length], [0, 0]);
});

test('aprender: limite excedido responde com honestidade e não chama a pesquisa', async () => {
  let chamadas = 0;
  const a = criarAprendizado({ conhecer: async () => { chamadas++; return null; }, lembrar: async () => ({ id: 1 }), repo: {}, limitador: () => false });
  assert.match(await a.aprender('o que é x?'), /pergunte de novo em um minuto/);
  assert.equal(chamadas, 0);
  assert.equal(await criarAprendizado({ conhecer: async () => null, lembrar: async () => ({}), repo: {}, limitador: () => true }).aprender('o que é x?'), null);
});
