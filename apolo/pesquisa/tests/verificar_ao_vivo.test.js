import assert from 'node:assert/strict';
import { test } from 'node:test';
import { codigoDeSaida, formatarTabela, verificar } from '../verificar_ao_vivo.js';

const ok = { nome: 'bom', tipos: ['definicao'], extrair: async () => ({ fatos: [{ texto: 'Um fato.' }], conceitos: [{ nome: 'x' }] }) };
const vazio = { nome: 'vazio', tipos: ['geral'], extrair: async () => null };
const quebrado = { nome: 'quebrado', tipos: ['codigo'], extrair: async () => { throw new Error('site mudou: 404'); } };
const lento = { nome: 'lento', tipos: ['geral'], extrair: () => new Promise(() => {}) };
const misto = { nome: 'misto', tipos: ['geral'], extrair: async ({ consulta }) => (consulta === 'a' ? { fatos: [{ texto: 'ok' }] } : { fatos: [] }) };

test('verificar: classifica OK, VAZIO e FALHOU, com contagens e motivo', async () => {
  const consultas = { bom: ['a', 'b'], vazio: ['a', 'b'], quebrado: ['a', 'b'], lento: ['a'] };
  const linhas = await verificar([ok, vazio, quebrado, lento], {}, { consultas, tempoMs: 20 });
  assert.equal(linhas.length, 7);
  assert.deepEqual(linhas.filter((l) => l.adaptador === 'bom').map((l) => l.estado), ['OK', 'OK']);
  assert.equal(linhas[0].contagens.fatos, 1);
  assert.equal(linhas[0].contagens.conceitos, 1);
  assert.equal(linhas.find((l) => l.adaptador === 'vazio').estado, 'VAZIO');
  const q = linhas.find((l) => l.adaptador === 'quebrado');
  assert.equal(q.estado, 'FALHOU');
  assert.match(q.motivo, /404/);
  assert.match(linhas.find((l) => l.adaptador === 'lento').motivo, /passou de 20 ms/);
});

test('verificar: usa consulta padrão para adaptador desconhecido e entrega URLs ao campo url', async () => {
  const vistos = [];
  const generico = { nome: 'generico', tipos: ['geral'], extrair: async (e) => { vistos.push(e); return { fatos: [{ texto: 'x' }] }; } };
  const novo = { nome: 'novo_adaptador', tipos: ['definicao'], extrair: async (e) => { vistos.push(e); return { fatos: [{ texto: 'x' }] }; } };
  const linhas = await verificar([generico, novo], {}, { consultas: { generico: ['https://a.test/x'] }, padrao: ['astrologia', 'Brasil'] });
  assert.deepEqual(linhas.map((l) => l.consulta), ['https://a.test/x', 'astrologia', 'Brasil']);
  assert.equal(vistos[0].url, 'https://a.test/x');
  assert.equal(vistos[1].url, undefined);
  assert.equal(vistos[1].tipo, 'definicao');
});

test('codigoDeSaida: falha em qualquer consulta ou vazio nas duas = 1; um vazio só avisa', async () => {
  const c = (a, estados) => estados.map((estado) => ({ adaptador: a, estado }));
  assert.equal(codigoDeSaida([...c('a', ['OK', 'OK']), ...c('b', ['OK', 'VAZIO'])]), 0);
  assert.equal(codigoDeSaida(c('a', ['VAZIO', 'VAZIO'])), 1);
  assert.equal(codigoDeSaida(c('a', ['OK', 'FALHOU'])), 1);
  const linhas = await verificar([misto], {}, { consultas: { misto: ['a', 'b'] } });
  assert.deepEqual(linhas.map((l) => l.estado), ['OK', 'VAZIO']);
  assert.equal(codigoDeSaida(linhas), 0);
});

test('formatarTabela: cabeçalho, uma linha por consulta e o motivo da falha', async () => {
  const linhas = await verificar([ok, quebrado], {}, { consultas: { bom: ['a'], quebrado: ['a'] } });
  const linhasTexto = formatarTabela(linhas).split('\n');
  assert.equal(linhasTexto.length, 4);
  assert.match(linhasTexto[0], /adaptador\s+consulta\s+tempo\s+fatos/);
  assert.match(linhasTexto[2], /bom\s+a\s+0\.0s\s+1\s+1\s+0\s+0\s+0\s+OK$/);
  assert.match(linhasTexto[3], /FALHOU: site mudou: 404$/);
});
