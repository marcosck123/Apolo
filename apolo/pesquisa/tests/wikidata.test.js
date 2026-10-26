import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import wikidata, { formatarData, numero } from '../adaptadores/wikidata.js';
import { conhecer } from '../adaptadores/index.js';

const PASTA = new URL('./fixtures/wikidata/', import.meta.url);
const lerJson = (nome) => JSON.parse(readFileSync(new URL(nome, PASTA), 'utf8'));
const slug = (t) => t.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replace(/\s+/g, '_');
const resposta = (obj) => { const texto = JSON.stringify(obj); return { status: 200, ok: true, texto, json: () => JSON.parse(texto) }; };

// ctx falso com respostas reais reduzidas: busca_<tema>.json, entidade_<Q>.json e rotulos.json (união dos rótulos).
function ctxFalso({ erro = null, entidades = {} } = {}) {
  const pedidos = [];
  return {
    pedidos,
    registrar: () => {},
    async buscar(url) {
      pedidos.push(url);
      if (erro) throw new Error(erro);
      const q = new URL(url).searchParams;
      if (q.get('action') === 'wbsearchentities') {
        try { return resposta(lerJson(`busca_${slug(q.get('search'))}.json`)); } catch { return resposta({ search: [] }); }
      }
      if (q.get('props') === 'labels') {
        const todos = lerJson('rotulos.json').entities;
        const pedidos_ = q.get('ids').split('|');
        return resposta({ entities: Object.fromEntries(pedidos_.filter((i) => todos[i]).map((i) => [i, todos[i]])) });
      }
      const id = q.get('ids');
      if (entidades[id]) return resposta({ entities: { [id]: entidades[id] } });
      try { return resposta(lerJson(`entidade_${id}.json`)); } catch { return resposta({ entities: { [id]: { id, missing: '' } } }); }
    },
  };
}

const extrair = (tema, tipo, ctx = ctxFalso()) => wikidata.extrair({ consulta: tema, tema, tipo }, ctx);
const mapa = (r) => Object.fromEntries(r.atributos.map((a) => [a.nome, a.valor]));

test('Porto Velho (lugar): atributos legíveis em português, com unidade e ano de referência', async () => {
  const ctx = ctxFalso();
  const r = await extrair('porto velho', 'lugar', ctx);
  assert.equal(ctx.pedidos.length, 3); // busca + entidade + rótulos
  const a = mapa(r);
  assert.equal(a['País'], 'Brasil');
  assert.equal(a['Localizado na unidade administrativa'], 'Rondônia');
  assert.equal(a['Capital de'], 'Rondônia');
  assert.match(a['População'], /^\d{3} \d{3} habitantes \(20\d\d\)$/);
  assert.match(a['Área'], /^34 \d{3},\d+ km²$/);
  assert.equal(a['Altitude'], '83 m');
  assert.equal(a['Coordenadas geográficas'], '8,7619° S, 63,9039° O');
  assert.match(a['Instância de'], /município do Brasil/);
  assert.ok(r.atributos.length <= 12);
  for (const x of r.atributos) {
    assert.equal(x.adaptador, 'wikidata');
    assert.equal(x.licenca, 'CC0 1.0');
    assert.equal(x.fonte, 'https://www.wikidata.org/wiki/Q172512');
    assert.doesNotMatch(`${x.nome} ${x.valor}`, /\bQ\d+\b|\bP\d+\b|\[object|undefined|null|\+\d/, `${x.nome}: ${x.valor}`);
  }
  assert.equal(r.metadados.titulo, 'Porto Velho');
  assert.equal(r.metadados.url, 'https://www.wikidata.org/wiki/Q172512');
  assert.ok(r.metadados.data);
  assert.deepEqual(r.fatos ?? [], []);
});

test('Porto Velho: conceitos vêm das entidades ligadas (classe, país, estado) com peso', async () => {
  const r = await extrair('porto velho', 'lugar');
  const nomes = r.conceitos.map((c) => c.nome);
  assert.ok(nomes.includes('Município do Brasil') && nomes.includes('Brasil') && nomes.includes('Rondônia'));
  assert.ok(r.conceitos.every((c) => c.peso > 0 && c.peso <= 1 && /wikidata\.org\/wiki\/Q\d+/.test(c.url)));
  assert.equal(new Set(nomes.map((n) => n.toLowerCase())).size, nomes.length);
});

test('Vilhena (lugar): escolhe o município de Rondônia, não o homônimo da Espanha', async () => {
  const r = await extrair('vilhena', 'lugar');
  const a = mapa(r);
  assert.equal(r.metadados.url, 'https://www.wikidata.org/wiki/Q1749958');
  assert.equal(a['Localizado na unidade administrativa'], 'Rondônia');
  assert.equal(a['População'], '95 832 habitantes (2022)');
  assert.match(a['Área'], /^11 518,91 km²$/);
});

test('Santos Dumont (pessoa): escolhe a pessoa (não a cidade) e formata datas por extenso', async () => {
  const r = await extrair('santos dumont', 'pessoa');
  const a = mapa(r);
  assert.equal(r.metadados.url, 'https://www.wikidata.org/wiki/Q313211');
  assert.equal(r.metadados.titulo, 'Alberto Santos Dumont');
  assert.equal(a['Instância de'], 'humano');
  assert.equal(a['Data de nascimento'], '20 de julho de 1873');
  assert.equal(a['Data de morte'], '23 de julho de 1932');
  assert.equal(a['Local de morte'], 'Guarujá');
  assert.match(a['Ocupação'], /inventor/);
  assert.ok(a['Ocupação'].split('; ').length <= 4);
  assert.ok(r.atributos.length <= 12);
});

test('astrologia (definição): instância de / subclasse de viram atributos e conceitos', async () => {
  const r = await extrair('astrologia', 'definicao');
  const a = mapa(r);
  assert.match(a['Subclasse de'], /pseudociência/);
  assert.ok(r.conceitos.some((c) => c.nome === 'Pseudociência'));
});

test('sem resultado ou entidade inexistente: devolve null', async () => {
  assert.equal(await extrair('xqzkwj', 'lugar'), null);
  const ctx = ctxFalso();
  assert.equal(await wikidata.extrair({ consulta: 'x', tema: 'x', tipo: 'lugar', url: 'https://www.wikidata.org/wiki/Q999999999' }, ctx), null);
});

test('busca ignora páginas de desambiguação e resultados sem relação com o tema', async () => {
  const busca = { search: [
    { id: 'Q1', label: 'Mercúrio', description: 'página de desambiguação da Wikimedia', match: { type: 'label', text: 'Mercúrio' } },
    { id: 'Q2', label: 'Outra coisa qualquer', description: 'planeta', match: { type: 'label', text: 'Outra coisa qualquer' } },
  ] };
  const ctx = ctxFalso();
  const original = ctx.buscar;
  ctx.buscar = async (url) => (new URL(url).searchParams.get('action') === 'wbsearchentities' ? resposta(busca) : original(url));
  assert.equal(await extrair('mercurio', 'definicao', ctx), null);
});

test('erro de rede e erro da API: o adaptador lança e o roteador isola a falha', async () => {
  await assert.rejects(() => extrair('porto velho', 'lugar', ctxFalso({ erro: 'sem rede' })), /sem rede/);
  const ctx = ctxFalso();
  ctx.buscar = async () => resposta({ error: { code: 'ratelimited' } });
  await assert.rejects(() => extrair('porto velho', 'lugar', ctx), /ratelimited/);
  const r = await conhecer('quem foi santos dumont', ctxFalso({ erro: 'sem rede' }), { adaptadores: [wikidata] });
  assert.equal(r.falhas[0].adaptador, 'wikidata');
});

test('pelo roteador: serve lugar, pessoa e definição; não roda para código', async () => {
  const r = await conhecer('quem foi santos dumont', ctxFalso(), { adaptadores: [wikidata] });
  assert.deepEqual(r.adaptadores, ['wikidata']);
  assert.ok(r.atributos.length >= 5);
  const c = await conhecer('como usar map em javascript', ctxFalso(), { adaptadores: [wikidata] });
  assert.deepEqual(c.adaptadores, []);
});

// ---- regras de formatação e escolha com entidades sintéticas (mesma forma da API) ----

const item = (id) => ({ mainsnak: { snaktype: 'value', datatype: 'wikibase-item', datavalue: { value: { id } } }, rank: 'normal' });
const quantia = (amount, unit = '1', ano = null, rank = 'normal') => ({
  mainsnak: { snaktype: 'value', datatype: 'quantity', datavalue: { value: { amount, unit } } }, rank,
  ...(ano ? { qualifiers: { P585: [{ datavalue: { value: { time: `+${ano}-00-00T00:00:00Z`, precision: 9 } } }] } } : {}),
});
const entidadeSintetica = (claims) => ({ id: 'Q777', labels: { pt: { value: 'Lugarejo' } }, claims, modified: '2026-01-01T00:00:00Z' });
const rotulosSinteticos = { P1082: 'população', P6: 'chefe do governo', P36: 'capital', P2046: 'área', Q1: 'Fulano', Q2: 'Beltrano', Q3: 'Cidadela' };
function ctxSintetico(claims) {
  const base = ctxFalso({ entidades: { Q777: entidadeSintetica(claims) } });
  const original = base.buscar;
  base.buscar = async (url) => {
    const q = new URL(url).searchParams;
    if (q.get('action') === 'wbsearchentities') return resposta({ search: [{ id: 'Q777', label: 'Lugarejo', description: 'município', match: { type: 'label', text: 'Lugarejo' } }] });
    if (q.get('props') === 'labels') return resposta({ entities: Object.fromEntries(q.get('ids').split('|').map((i) => [i, { labels: { pt: { value: rotulosSinteticos[i] ?? i } } }])) });
    return original(url);
  };
  return base;
}

test('população sem data de referência: não inventa o ano; com várias medições fica a mais recente', async () => {
  const sem = await extrair('lugarejo', 'lugar', ctxSintetico({ P1082: [quantia('+1200')] }));
  assert.equal(mapa(sem)['População'], '1 200 habitantes');
  const varias = await extrair('lugarejo', 'lugar', ctxSintetico({ P1082: [quantia('+900', '1', 2010), quantia('+1500', '1', 2022), quantia('+1100', '1', 2015)] }));
  assert.equal(mapa(varias)['População'], '1 500 habitantes (2022)');
});

test('rank preferido vence; valores deprecados e cargos já encerrados (P582) são ignorados', async () => {
  const antigo = { ...item('Q1'), qualifiers: { P582: [{ datavalue: { value: { time: '+2020-12-31T00:00:00Z', precision: 11 } } }] } };
  const r = await extrair('lugarejo', 'lugar', ctxSintetico({
    P6: [antigo, item('Q2')],
    P36: [{ ...item('Q1'), rank: 'deprecated' }, { ...item('Q3'), rank: 'preferred' }],
  }));
  assert.equal(mapa(r)['Chefe do governo'], 'Beltrano');
  assert.equal(mapa(r)['Capital'], 'Cidadela');
});

test('valores sem rótulo, sem valor ou de tipo não simples (arquivo, identificador) são descartados', async () => {
  const semValor = { mainsnak: { snaktype: 'somevalue', datatype: 'wikibase-item' }, rank: 'normal' };
  const ident = { mainsnak: { snaktype: 'value', datatype: 'external-id', datavalue: { value: 'abc' } }, rank: 'normal' };
  const r = await extrair('lugarejo', 'lugar', ctxSintetico({ P6: [semValor], P36: [ident], P2046: [quantia('+10', 'http://www.wikidata.org/entity/Q712226')] }));
  assert.deepEqual(Object.keys(mapa(r)), ['Área']);
  assert.equal(mapa(r)['Área'], '10 km²');
});

test('máximo de 12 atributos por entidade', async () => {
  const claims = { P31: [item('Q1')], P17: [item('Q2')], P131: [item('Q3')], P36: [item('Q1')], P1376: [item('Q2')], P1082: [quantia('+5')], P2046: [quantia('+5')],
    P2044: [quantia('+5')], P6: [item('Q1')], P856: [{ mainsnak: { snaktype: 'value', datatype: 'url', datavalue: { value: 'https://x.org' } }, rank: 'normal' }],
    P571: [], P279: [item('Q3')], P361: [item('Q2')], P527: [item('Q1')], P138: [item('Q1')], P1269: [item('Q1')] };
  const r = await extrair('lugarejo', 'lugar', ctxSintetico(claims));
  assert.ok(r.atributos.length >= 8 && r.atributos.length <= 12, String(r.atributos.length));
});

test('formatarData: precisões, a.C. e séculos', () => {
  assert.equal(formatarData({ time: '+1873-07-20T00:00:00Z', precision: 11 }), '20 de julho de 1873');
  assert.equal(formatarData({ time: '+1932-07-00T00:00:00Z', precision: 10 }), 'julho de 1932');
  assert.equal(formatarData({ time: '+1914-00-00T00:00:00Z', precision: 9 }), '1914');
  assert.equal(formatarData({ time: '+1900-00-00T00:00:00Z', precision: 7 }), 'século XIX');
  assert.equal(formatarData({ time: '-0300-00-00T00:00:00Z', precision: 9 }), '300 a.C.');
  assert.equal(formatarData({ time: '+1500-00-00T00:00:00Z', precision: 6 }), null); // milênio: impreciso demais
  assert.equal(formatarData({}), null);
});

test('numero: padrão brasileiro, sem casas inúteis', () => {
  assert.equal(numero(460434), '460 434');
  assert.equal(numero(34090.954), '34 090,95');
  assert.equal(numero(12), '12');
  assert.equal(numero(1.5), '1,5');
});

test('metadados do adaptador seguem o contrato', () => {
  assert.equal(wikidata.nome, 'wikidata');
  assert.equal(wikidata.licenca, 'CC0 1.0');
  assert.deepEqual([...wikidata.tipos].sort(), ['definicao', 'lugar', 'pessoa']);
  assert.ok(wikidata.dominios.includes('www.wikidata.org'));
});
