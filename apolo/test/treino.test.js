import assert from 'node:assert/strict';
import { test } from 'node:test';
import { lerTreino } from '../src/treino.js';

const log = `dispositivo: cpu | texto: 95,056 caracteres | vocab: 54 | parâmetros: 0.82M
passos: 3000
passo      0 | perda treino 4.038 | perda val 4.017 | 28s
passo    100 | perda treino 2.510 | perda val 2.544 | 61s`;

test('lerTreino: lê os passos, o total e o dispositivo', () => {
  const t = lerTreino(log);
  assert.equal(t.passos.length, 2);
  assert.deepEqual(t.passos[1], { passo: 100, treino: 2.51, val: 2.544, segundos: 61 });
  assert.equal(t.total, 3000);
  assert.equal(t.dispositivo, 'cpu');
  assert.equal(t.concluido, false);
});

test('lerTreino: reconhece o fim e guarda a amostra gerada', () => {
  const t = lerTreino(`${log}\nsalvo em cerebro/\n\n--- o córtex escreve ---\nOlá! Tudo bem?`);
  assert.equal(t.concluido, true);
  assert.equal(t.amostra, 'Olá! Tudo bem?');
});
