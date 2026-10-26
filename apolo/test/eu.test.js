import test from 'node:test';
import assert from 'node:assert/strict';
import { responderSobreMim } from '../src/eu.js';

test('perguntas sobre o próprio Apolo têm resposta', () => {
  for (const m of ['como você funciona?', 'pesquise como voce funciona', 'quem é você?', 'oque significa voce', 'quem te criou?', 'o que você sabe fazer?']) {
    assert.ok(responderSobreMim(m), m);
  }
});

test('outras perguntas não são sobre o Apolo', () => {
  for (const m of ['como funciona o voo?', 'qual a capital do Brasil?', 'o que é fotossíntese?', 'como você fez o bolo?']) {
    assert.equal(responderSobreMim(m), null, m);
  }
});
