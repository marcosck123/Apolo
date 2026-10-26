import assert from 'node:assert/strict';
import { test } from 'node:test';
import { criarLog } from '../src/log.js';

test('log: guarda só os últimos eventos, na ordem', () => {
  const log = criarLog({ max: 2 });
  log.registrar('a');
  log.registrar('b');
  log.registrar('c');
  assert.deepEqual(log.recentes().map((e) => e.tipo), ['b', 'c']);
});

test('log: avisa quem assinou e para de avisar ao cancelar', () => {
  const log = criarLog();
  const vistos = [];
  const cancelar = log.assinar((e) => vistos.push(e.tipo));
  log.registrar('pensou', { texto: 'oi' });
  cancelar();
  log.registrar('dormiu');
  assert.deepEqual(vistos, ['pensou']);
});
