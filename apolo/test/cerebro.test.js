import assert from 'node:assert/strict';
import { test } from 'node:test';
import { embutir, similaridade } from '../src/embeddings.js';
import { Cerebro, esquecer, hebb, propagar } from '../src/nucleo/cerebro.js';

const perto = (a, b) => Math.abs(a - b) < 1e-9;

// 1 —0.8— 2 —0.5— 3      4 (isolado)
function grafoExemplo() {
  const c = new Cerebro();
  for (const id of [1, 2, 3, 4]) c.adicionarNeuronio({ id });
  c.definirSinapse(1, 2, 0.8);
  c.definirSinapse(2, 3, 0.5);
  return c;
}

test('propagar: energia decai com a distância e neurônios desconectados não acendem', () => {
  const ativos = propagar(grafoExemplo(), [{ id: 1, forca: 1 }]);
  assert.deepEqual(ativos.map((a) => a.id), [1, 2, 3]);
  assert.ok(perto(ativos.find((a) => a.id === 3).ativacao, 0.1));
});

test('propagar: ativação não vaza entre pensamentos', () => {
  const c = grafoExemplo();
  propagar(c, [{ id: 1, forca: 1 }]);
  const ativos = propagar(c, [{ id: 4, forca: 1 }]);
  assert.deepEqual(ativos.map((a) => a.id), [4]);
});

test('hebb: cria a sinapse e reforça com saturação suave', () => {
  const c = grafoExemplo();
  const ativos = [{ id: 1, ativacao: 1 }, { id: 4, ativacao: 0.5 }];
  hebb(c, ativos, 0.1);
  assert.ok(perto(c.sinapse(1, 4).peso, 0.05));
  hebb(c, ativos, 0.1);
  assert.ok(perto(c.sinapse(1, 4).peso, 0.05 + 0.05 * 0.95));
});

test('esquecer: decai os pesos e poda o que fica abaixo do mínimo', () => {
  const c = grafoExemplo();
  c.definirSinapse(1, 3, 0.021);
  const podadas = esquecer(c, { fator: 0.5, minimo: 0.02 });
  assert.equal(podadas, 1);
  assert.equal(c.sinapse(1, 3), undefined);
  assert.ok(perto(c.sinapse(1, 2).peso, 0.4));
});

test('embeddings: textos sobre o mesmo assunto ficam mais próximos', () => {
  const base = embutir('deploy de Next.js na Vercel');
  const parecido = embutir('como fazer deploy do Next.js');
  const distante = embutir('receita de bolo de cenoura');
  assert.ok(similaridade(base, parecido) > similaridade(base, distante));
});
