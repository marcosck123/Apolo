import assert from 'node:assert/strict';
import { test } from 'node:test';
import { completar, limparTexto, pareceFrase } from '../adaptadores/contrato.js';
import { criarCtx } from '../adaptadores/ctx.js';
import { conhecer, distribuirUrls, falaDoTema, juntar } from '../adaptadores/index.js';
import { classificar } from '../adaptadores/tipo.js';

test('classificar: tipo e tema de perguntas comuns', () => {
  assert.deepEqual(classificar('O que é astrologia?'), { tipo: 'definicao', tema: 'astrologia' });
  assert.deepEqual(classificar('Quem foi Santos Dumont?'), { tipo: 'pessoa', tema: 'santos dumont' });
  assert.equal(classificar('qual a capital de Rondônia?').tipo, 'lugar');
  assert.equal(classificar('como usar map em javascript').tipo, 'codigo');
  assert.equal(classificar('oi tudo bem').tipo, 'geral');
});

test('limparTexto: tira notas, CSS solto e "Expandir lista"', () => {
  assert.equal(limparTexto('A astrologia[1][2] é antiga .mw-parser-output .nobold{font-weight:normal} Expandir Lista 12 .'), 'A astrologia é antiga.');
  assert.equal(pareceFrase('Menu'), false);
  assert.equal(pareceFrase('Astrologia é uma prática divinatória antiga.'), true);
});

test('conhecer: escolhe pelo tipo, junta sem repetir e isola o adaptador que falha', async () => {
  const a = { nome: 'a', tipos: ['definicao'], extrair: async () => ({ fatos: [{ texto: 'Fato um.', fonte: 'x' }], conceitos: [{ nome: 'Zodíaco', peso: 0.5 }] }) };
  const b = { nome: 'b', tipos: ['definicao'], extrair: async () => ({ fatos: [{ texto: 'fato um.', fonte: 'y' }, { texto: 'Fato dois.', fonte: 'y' }] }) };
  const c = { nome: 'c', tipos: ['definicao'], extrair: async () => { throw new Error('quebrou'); } };
  const d = { nome: 'd', tipos: ['codigo'], extrair: async () => ({ fatos: [{ texto: 'não deveria rodar', fonte: 'z' }] }) };
  const r = await conhecer('o que é astrologia', { registrar: () => {} }, { adaptadores: [a, b, c, d] });
  assert.equal(r.tipo, 'definicao');
  assert.deepEqual(r.fatos.map((f) => f.texto), ['Fato um.', 'Fato dois.']);
  assert.deepEqual(r.adaptadores, ['a', 'b']);
  assert.equal(r.falhas[0].adaptador, 'c');
  assert.deepEqual(juntar([]), completar({}));
});

test('pareceFrase e limparTexto: barram chamada de marketing e tiram o símbolo ¶', () => {
  assert.equal(pareceFrase('Clique aqui e conheça um pouco mais sobre o estado de Rondônia!'), false);
  assert.equal(pareceFrase('Saiba tudo sobre a média aritmética e como calculá-la.'), false);
  assert.equal(limparTexto('Sintaxe ¶ da função'), 'Sintaxe da função');
});

test('distribuirUrls: o adaptador do domínio recebe a URL; domínio sem adaptador cai no genérico (máx. 2)', () => {
  const wiki = { nome: 'wikipedia', dominios: ['pt.wikipedia.org'] };
  const escola = { nome: 'brasilescola', dominios: ['brasilescola.uol.com.br'] };
  const generico = { nome: 'generico', dominios: [] };
  const todos = [wiki, escola, generico];
  const t = distribuirUrls(['https://pt.wikipedia.org/wiki/X', 'https://www.brasilescola.uol.com.br/a.htm', 'https://blog.com/1', 'https://blog.com/2', 'https://blog.com/3', 'nao-e-url'], todos);
  assert.deepEqual(t.map((x) => x.adaptador.nome), ['wikipedia', 'brasilescola', 'generico', 'generico']);
});

test('conhecer: URLs achadas pela busca chegam ao adaptador do domínio com o campo url', async () => {
  const recebidas = [];
  const escola = { nome: 'escola', tipos: ['definicao'], dominios: ['escola.com'], extrair: async (e) => { recebidas.push(e.url ?? null); return e.url ? { fatos: [{ texto: 'Astrologia na escola.', fonte: e.url }] } : null; } };
  const r = await conhecer('o que é astrologia', { registrar: () => {} }, { adaptadores: [escola], urls: ['https://escola.com/a.htm'] });
  assert.deepEqual([...recebidas].sort(), ['https://escola.com/a.htm', null]);
  assert.deepEqual(r.fatos.map((f) => f.texto), ['Astrologia na escola.']);
});

test('falaDoTema: barra a página sem relação com o tema e aceita a que menciona', () => {
  const youtube = { metadados: { titulo: 'Ajuda do YouTube' }, fatos: [{ texto: 'Necesitas una Cuenta de Google para acceder a YouTube.' }], conceitos: [] };
  const certa = { metadados: { titulo: 'Astrologia – Wikipédia' }, fatos: [{ texto: 'Estudo dos astros.' }], conceitos: [] };
  assert.equal(falaDoTema(youtube, 'astrologia'), false);
  assert.equal(falaDoTema(certa, 'astrologia'), true);
  assert.equal(falaDoTema(youtube, 'ia'), true, 'tema curto demais não filtra');
});

test('conhecer: URL da busca sem relação com o tema é descartada e registrada como falha', async () => {
  const generico = { nome: 'generico', tipos: ['geral'], dominios: [], extrair: async (e) => e.url ? { fatos: [{ texto: 'Cuenta de Google para YouTube.', fonte: e.url }] } : null };
  const r = await conhecer('o que é astrologia', { registrar: () => {} }, { adaptadores: [generico], urls: ['https://ajuda.youtube.com/x'] });
  assert.deepEqual(r.fatos, []);
  assert.match(r.falhas[0].erro, /sem relação/);
});

test('ctx.buscar: 429 espera o Retry-After e tenta uma vez de novo', async () => {
  const chamadas = [];
  const esperas = [];
  const fetchFn = async () => {
    chamadas.push(1);
    return chamadas.length === 1
      ? { status: 429, ok: false, headers: new Headers({ 'retry-after': '3' }), url: 'https://exemplo.org/a', text: async () => 'devagar' }
      : { status: 200, ok: true, headers: new Headers(), url: 'https://exemplo.org/a', text: async () => '{"ok":1}' };
  };
  const ctx = criarCtx({ fetchFn, esperar: async (ms) => esperas.push(ms) });
  const r = await ctx.buscar('https://93.184.216.34/a?x=' + Date.now(), { json: true });
  assert.equal(r.status, 200);
  assert.deepEqual(esperas, [3000]);
  assert.equal(chamadas.length, 2);
});

test('limparTexto: tira o espaço de dentro dos parênteses', () => {
  assert.equal(limparTexto('População ( 2022 ) de 460 434 habitantes'), 'População (2022) de 460 434 habitantes');
});
