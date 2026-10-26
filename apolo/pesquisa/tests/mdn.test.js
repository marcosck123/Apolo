import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { parseHTML } from 'linkedom';
import mdn, { termosDeBusca } from '../adaptadores/mdn.js';

const LER = (arquivo) => readFileSync(new URL(`./fixtures/mdn/${arquivo}`, import.meta.url), 'utf8');
const ORIGEM = 'https://developer.mozilla.org';
const BASE_JS = '/docs/Web/JavaScript/Reference/Global_Objects';

// Respostas reais da MDN (busca JSON e HTML SSR), reduzidas: sem CSS, scripts, SVG e menus.
const RESPOSTAS = {
  [`${ORIGEM}/api/v1/search?q=array%20map&locale=pt-BR`]: 'busca_array_map_pt.json',
  [`${ORIGEM}/api/v1/search?q=promise&locale=pt-BR`]: 'busca_promise_pt.json',
  [`${ORIGEM}/api/v1/search?q=math%20max&locale=pt-BR`]: 'busca_math_max_pt.json',
  [`${ORIGEM}/api/v1/search?q=math%20sumprecise&locale=pt-BR`]: 'busca_math_sumprecise_pt.json',
  [`${ORIGEM}/api/v1/search?q=math%20sumprecise&locale=en-US`]: 'busca_math_sumprecise_en.json',
  [`${ORIGEM}/api/v1/search?q=astrologia&locale=pt-BR`]: 'busca_astrologia_pt.json',
  [`${ORIGEM}/api/v1/search?q=astrologia&locale=en-US`]: 'busca_astrologia_en.json',
  [`${ORIGEM}/pt-BR${BASE_JS}/Array/map`]: 'array_map_pt.html',
  [`${ORIGEM}/pt-BR${BASE_JS}/Promise`]: 'promise_pt.html',
  [`${ORIGEM}/pt-BR${BASE_JS}/Math/max`]: 'math_max_pt.html',
  [`${ORIGEM}/en-US${BASE_JS}/Math/sumPrecise`]: 'math_sumprecise_en.html',
};

function criarCtxFalso({ falhar = false, sem = [] } = {}) {
  const chamadas = [];
  return {
    chamadas,
    registrar: () => {},
    parsear: (html) => parseHTML(html).document,
    async buscar(url) {
      chamadas.push(url);
      if (falhar) throw new Error('rede caiu');
      const arquivo = RESPOSTAS[url];
      const resposta = (texto, status) => ({ status, ok: status < 400, url, texto, json: () => JSON.parse(texto) });
      if (!arquivo || sem.includes(url)) return resposta('Not found', 404);
      return resposta(LER(arquivo), 200);
    },
  };
}

test('metadados do adaptador: tipos, domínio e licença', () => {
  assert.equal(mdn.nome, 'mdn');
  assert.deepEqual(mdn.tipos, ['codigo', 'definicao']);
  assert.deepEqual(mdn.dominios, ['developer.mozilla.org']);
  assert.match(mdn.licenca, /CC BY-SA 2\.5/);
  assert.match(mdn.licenca, /CC0/);
});

test('termosDeBusca tira palavras de ligação e o nome da linguagem', () => {
  assert.deepEqual(termosDeBusca('como usar array map em javascript'), ['array', 'map']);
  assert.deepEqual(termosDeBusca('Math.max'), ['math', 'max']);
  assert.deepEqual(termosDeBusca('javascript'), ['javascript']);
  assert.deepEqual(termosDeBusca('o que é'), []);
});

test('array map: descrição, sintaxe, parâmetros, códigos, conceitos e metadados', async () => {
  const ctx = criarCtxFalso();
  const r = await mdn.extrair({ tema: 'array map', tipo: 'codigo' }, ctx);
  assert.equal(ctx.chamadas.length, 2); // busca + página
  const url = `${ORIGEM}/pt-BR${BASE_JS}/Array/map`;

  // (a) o primeiro fato é a descrição, com confiança alta e sem o aviso de "traduzido pela comunidade"
  assert.equal(r.fatos[0].texto, 'O método map() invoca a função callback passada por argumento para cada elemento do Array e devolve um novo Array como resultado.');
  assert.equal(r.fatos[0].confianca, 'alta');
  assert.equal(r.fatos[0].fonte, url);
  assert.equal(r.fatos[0].licenca, mdn.licenca);
  for (const f of r.fatos) assert.doesNotMatch(f.texto, /traduzida do inglês/);

  // (c) atributos
  const sintaxe = r.atributos.find((a) => a.nome === 'Sintaxe');
  assert.equal(sintaxe.valor, 'arr.map(callback[, thisArg])');
  const params = r.atributos.find((a) => a.nome === 'Parâmetros').valor;
  assert.match(params, /^callback: Função cujo retorno produz/);
  assert.match(params, /thisArg: Opcional/);

  // (b) códigos: sintaxe + exemplos de uso, nenhum com "interactive-example", todos com linguagem e explicação
  assert.ok(r.codigos.length >= 3);
  assert.equal(r.codigos[0].codigo, 'arr.map(callback[, thisArg])');
  assert.equal(r.codigos[0].explicacao, 'Sintaxe');
  const raizes = r.codigos.find((c) => c.codigo.includes('numbers.map(Math.sqrt)'));
  assert.equal(raizes.linguagem, 'js');
  assert.match(raizes.explicacao, /^O código a seguir mapeia um array de números/);
  for (const c of r.codigos) {
    assert.ok(c.linguagem && c.codigo.length >= 8 && c.explicacao && c.fonte.startsWith(ORIGEM));
    assert.doesNotMatch(c.codigo, /^\s|\s$/); // sem linhas em branco nas pontas
  }

  // (d) conceitos: links internos, sem a própria página e com peso decrescente
  assert.ok(r.conceitos.length >= 3 && r.conceitos.length <= 12);
  assert.ok(r.conceitos.every((c) => c.url.startsWith(`${ORIGEM}/pt-BR/docs/`) && c.url !== url && c.peso > 0 && c.peso <= 1));
  assert.deepEqual(r.conceitos.map((c) => c.peso), [...r.conceitos.map((c) => c.peso)].sort((a, b) => b - a));
  assert.ok(r.conceitos.every((c) => c.nome.length <= 50));

  // (e) metadados
  assert.deepEqual(r.metadados, { titulo: 'Array.prototype.map()', idioma: 'pt-BR', data: '2026-05-22T18:48:50.000Z', url });
});

test('Promise: página grande, escolhe a global e não pega saída nem blocos de tabela', async () => {
  const r = await mdn.extrair({ tema: 'promise', tipo: 'definicao' }, criarCtxFalso());
  assert.equal(r.metadados.titulo, 'Promise');
  assert.match(r.fatos[0].texto, /^O objeto Promise representa a eventual conclusão/);
  assert.ok(r.codigos.length > 0 && r.codigos.length <= 8);
  assert.ok(r.codigos.every((c) => c.linguagem !== 'plain' && c.codigo.length <= 1800));
  assert.ok(r.conceitos.some((c) => /promise/i.test(c.nome)));
});

test('Math.max: segundo fato vem da Descrição e o resumo vem primeiro', async () => {
  const r = await mdn.extrair({ tema: 'math max' }, criarCtxFalso());
  assert.equal(r.fatos[0].texto, 'A função Math.max() retorna o maior de um ou mais números.');
  assert.equal(r.fatos[1].secao, 'Descrição');
  assert.equal(r.fatos[1].confianca, 'media');
  assert.match(r.atributos.find((a) => a.nome === 'Sintaxe').valor, /^Math\.max\(/);
  assert.ok(r.codigos.some((c) => c.codigo.includes('Math.max(10, 20)')));
});

test('sem tradução em pt-BR: usa en-US e marca o idioma', async () => {
  const ctx = criarCtxFalso();
  const r = await mdn.extrair({ tema: 'math sumPrecise' }, ctx);
  assert.equal(ctx.chamadas.length, 3); // busca pt-BR (nada que case), busca en-US, página en-US
  assert.equal(r.metadados.idioma, 'en-US');
  assert.match(r.metadados.url, /\/en-US\/docs\/.*\/Math\/sumPrecise$/);
  assert.match(r.fatos[0].texto, /^The Math\.sumPrecise\(\) static method/);
  assert.equal(r.fatos[0].secao, 'Resumo (em inglês)');
  assert.match(r.codigos[0].explicacao, /\(em inglês\)$/);
});

test('página pt-BR que dá 404 cai para a mesma página em en-US', async () => {
  const ctx = criarCtxFalso();
  const r = await mdn.extrair({ tema: 'x', url: `${ORIGEM}/pt-BR${BASE_JS}/Math/sumPrecise` }, ctx);
  assert.equal(r.metadados.idioma, 'en-US');
  assert.deepEqual(ctx.chamadas, [`${ORIGEM}/pt-BR${BASE_JS}/Math/sumPrecise`, `${ORIGEM}/en-US${BASE_JS}/Math/sumPrecise`]);
});

test('tema que não é da MDN → null (e não devolve uma página qualquer)', async () => {
  assert.equal(await mdn.extrair({ tema: 'astrologia' }, criarCtxFalso()), null);
  assert.equal(await mdn.extrair({ tema: 'o que é' }, criarCtxFalso()), null);
});

test('busca fora do ar → null; erro de rede → lança', async () => {
  const ctx = criarCtxFalso({ sem: [`${ORIGEM}/api/v1/search?q=array%20map&locale=pt-BR`, `${ORIGEM}/api/v1/search?q=array%20map&locale=en-US`] });
  assert.equal(await mdn.extrair({ tema: 'array map' }, ctx), null);
  await assert.rejects(() => mdn.extrair({ tema: 'array map' }, criarCtxFalso({ falhar: true })), /rede caiu/);
});

test('texto limpo: sem notas [1], sem espaços estranhos e sem quebras nos fatos, códigos e atributos', async () => {
  const r = await mdn.extrair({ tema: 'promise' }, criarCtxFalso());
  for (const f of r.fatos) assert.doesNotMatch(f.texto, /\[\d+\]|\s{2,}|\n/);
  for (const a of r.atributos) assert.doesNotMatch(a.valor, /\s{2,}|\n/);
});
