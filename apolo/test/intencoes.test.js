import assert from 'node:assert/strict';
import { test } from 'node:test';
import { criarDetector } from '../src/intencoes.js';
import { INTENCOES_PADRAO } from '../src/intencoes_padrao.js';

const { detectar } = criarDetector(INTENCOES_PADRAO);
const detectarIntencao = (m, o) => detectar(m, o);

const sempreZero = { sortear: () => 0 };

test('intenções: "oi" é saudação e recebe uma saudação de volta', () => {
  for (const m of ['oi', 'Oi!', 'OLÁ', 'e aí?', 'eae', 'opa']) {
    const r = detectarIntencao(m, sempreZero);
    assert.equal(r?.intencao, 'saudacao', m);
    assert.match(r.resposta, /Olá|Oi/);
  }
});

test('intenções: a resposta acompanha o que foi dito', () => {
  assert.equal(detectarIntencao('Bom dia!').resposta, 'Bom dia! Como você está?');
  assert.equal(detectarIntencao('boa noite').resposta, 'Boa noite! Como você está?');
  assert.equal(detectarIntencao('oi, tudo bem?').resposta, 'Tudo bem, e com você?');
});

test('intenções: despedida, agradecimento e identidade', () => {
  assert.equal(detectarIntencao('tchau', sempreZero).intencao, 'despedida');
  assert.equal(detectarIntencao('Muito obrigado!', sempreZero).intencao, 'agradecimento');
  assert.match(detectarIntencao('Qual é o seu nome?').resposta, /Apolo/);
});

test('intenções: se a mensagem traz outro assunto, não é intenção pura (vai para o córtex)', () => {
  assert.equal(detectarIntencao('oi, que horas são?'), null);
  assert.equal(detectarIntencao('onde fica Vilhena?'), null);
  assert.equal(detectarIntencao('   '), null);
});

test('intenções: frase ensinada vira parte do grupo e o índice acha a mais longa', () => {
  const d = criarDetector([
    { nome: 'saudacao', frases: ['oi', 'fala meu parceiro'], respostas: [{ texto: 'Fala!' }] },
    { nome: 'agradecimento', frases: ['valeu'], respostas: [{ texto: 'Tmj' }] },
  ]);
  assert.equal(d.detectar('Fala meu parceiro!').intencao, 'saudacao');
  assert.equal(d.detectar('valeu').resposta, 'Tmj');
  assert.equal(d.detectar('fala meu amigo'), null);
});

test('intenções: grupo sem respostas não responde (vai para o córtex)', () => {
  assert.equal(criarDetector([{ nome: 'x', frases: ['oi'], respostas: [] }]).detectar('oi'), null);
});
