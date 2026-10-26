import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { parseHTML } from 'linkedom';
import wikipedia, { frases, lerInfobox } from '../adaptadores/wikipedia.js';
import { conhecer } from '../adaptadores/index.js';
import { pareceProsa } from '../adaptadores/contrato.js';

const PASTA = new URL('./fixtures/wikipedia/', import.meta.url);
const ler = (nome) => readFileSync(new URL(nome, PASTA), 'utf8');
const slug = (t) => t.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replace(/\s+/g, '_');

// ctx falso: devolve as respostas reais salvas em fixtures/wikipedia/ (busca_<tema>.json e pagina_<Título>.html).
function ctxFalso({ semPagina = [], erro = null } = {}) {
  const pedidos = [];
  return {
    pedidos,
    registrar: () => {},
    parsear: (html) => parseHTML(html).document,
    async buscar(url) {
      pedidos.push(url);
      if (erro) throw new Error(erro);
      const u = new URL(url);
      if (u.searchParams.get('generator') === 'search') {
        const arquivo = `busca_${slug(u.searchParams.get('gsrsearch'))}.json`;
        let texto;
        try { texto = ler(arquivo); } catch { texto = '{"batchcomplete":true}'; }
        return { status: 200, ok: true, texto, json: () => JSON.parse(texto) };
      }
      const titulo = decodeURIComponent(u.pathname.split('/page/html/')[1]);
      if (semPagina.includes(titulo)) return { status: 404, ok: false, texto: 'Not found', json: () => null };
      const texto = ler(`pagina_${titulo}.html`);
      return { status: 200, ok: true, texto, json: () => null };
    },
  };
}

const extrair = (tema, tipo = 'definicao', ctx = ctxFalso()) => wikipedia.extrair({ consulta: tema, tema, tipo }, ctx);

test('astrologia: definição de abertura com confiança alta, metadados e licença', async () => {
  const ctx = ctxFalso();
  const r = await extrair('astrologia', 'definicao', ctx);
  assert.equal(ctx.pedidos.length, 2); // busca + HTML
  const def = r.fatos[0];
  assert.match(def.texto, /^Astrologia \(do grego astron/);
  assert.match(def.texto, /é uma gama de práticas divinatórias/);
  assert.equal(def.confianca, 'alta');
  assert.equal(def.secao, null);
  assert.equal(def.adaptador, 'wikipedia');
  assert.equal(def.licenca, 'CC BY-SA 4.0');
  assert.equal(r.metadados.titulo, 'Astrologia');
  assert.equal(r.metadados.idioma, 'pt');
  assert.equal(r.metadados.url, 'https://pt.wikipedia.org/wiki/Astrologia');
  assert.equal(r.metadados.data, '2026-04-07T12:37:32Z');
});

test('astrologia: nenhum texto traz referências [1], CSS ou espaços duplos', async () => {
  const r = await extrair('astrologia');
  for (const f of r.fatos) {
    assert.doesNotMatch(f.texto, /\[\d+\]|\[nota|mw-parser-output|\{.*\}|\s{2}/);
    assert.ok(f.texto.length >= 30 && f.texto.length <= 400, f.texto);
  }
});

test('astrologia: fatos de seções (máx. 4 seções, 2 frases cada) sem Ver também/Referências', async () => {
  const r = await extrair('astrologia');
  const secoes = [...new Set(r.fatos.map((f) => f.secao).filter(Boolean))];
  assert.ok(secoes.length >= 1 && secoes.length <= 4, secoes.join('|'));
  assert.ok(secoes.includes('Estudos científicos')); // 'História' só tem um aviso de artigo principal, sem texto: fica de fora
  for (const s of secoes) assert.doesNotMatch(s, /ver também|refer[êe]ncias|liga[çc][õo]es externas|notas|bibliografia/i);
  for (const s of secoes) assert.ok(r.fatos.filter((f) => f.secao === s).length <= 2);
});

test('astrologia: conceitos vêm dos links da abertura, ordenados por peso decrescente de 1.0 a ~0.3, sem duplicatas', async () => {
  const { conceitos } = await extrair('astrologia');
  assert.ok(conceitos.length >= 5);
  assert.equal(conceitos[0].peso, 1);
  assert.ok(conceitos.at(-1).peso >= 0.25 && conceitos.at(-1).peso <= 0.45, String(conceitos.at(-1).peso));
  for (let i = 1; i < conceitos.length; i++) assert.ok(conceitos[i].peso <= conceitos[i - 1].peso);
  const nomes = conceitos.map((c) => c.nome.toLowerCase());
  assert.equal(new Set(nomes).size, nomes.length);
  assert.ok(nomes.includes('língua grega'));
  assert.ok(nomes.includes('pseudociência'));
  assert.ok(nomes.includes('corpo celeste')); // usa o título da página ("Corpo celeste"), não o texto do link
  assert.ok(!nomes.includes('astrologia')); // o próprio termo não vira conceito
  assert.match(conceitos[0].url, /^https:\/\/pt\.wikipedia\.org\/wiki\//);
});

test('Porto Velho (lugar): infobox em atributos limpos, com grupos e subitens', async () => {
  const r = await extrair('porto velho', 'lugar');
  assert.match(r.fatos[0].texto, /^Porto Velho é um município brasileiro e a capital do estado de Rondônia\./);
  const mapa = Object.fromEntries(r.atributos.map((a) => [a.nome, a.valor]));
  assert.equal(mapa['País'], 'Brasil');
  assert.equal(mapa['Unidade federativa'], 'Rondônia');
  assert.equal(mapa['Gentílico'], 'porto-velhense');
  assert.equal(mapa['Área total'], '34 090,954 km²');
  assert.equal(mapa['População total (Censo IBGE/2022)'], '460 434 hab.');
  assert.equal(mapa['Altitude'], '87 m');
  assert.match(mapa['Coordenadas'], /8° 45′ 43″ S/);
  for (const a of r.atributos) {
    assert.doesNotMatch(`${a.nome} ${a.valor}`, /\[\d+\]|mw-parser-output|\{.*\}|Expandir|^•|\s{2}/, `${a.nome}: ${a.valor}`);
    assert.ok(!a.nome.startsWith('•') && a.nome.length <= 80 && a.valor.length <= 250);
    assert.equal(a.fonte, 'https://pt.wikipedia.org/wiki/Porto_Velho');
  }
  // "Posição" solta não existe: vem sempre qualificada pelo grupo
  assert.ok(!r.atributos.some((a) => a.nome === 'Posição'));
});

test('infobox suja (Porto Velho real): CSS dentro do rótulo, notas e "Lista" são limpos', () => {
  const doc = parseHTML(ler('infobox_suja.html')).document;
  const attrs = lerInfobox(doc, 'https://pt.wikipedia.org/wiki/Porto_Velho');
  assert.match(ler('infobox_suja.html'), /mw-parser-output \.nobold/); // a sujeira está de fato no HTML
  const mapa = Object.fromEntries(attrs.map((a) => [a.nome, a.valor]));
  assert.deepEqual(mapa, {
    'Distritos': '12',
    'Área total': '34 090,954 km²',
    'Área urbana est. Embrapa': '41,7 km²',
    'População total (Censo IBGE/2022)': '460 434 hab.',
    'População posição': 'BR: 49º; RO: 1º',
  });
});

test('Santos Dumont (pessoa): segue o redirecionamento, extrai nascimento da infobox e seções', async () => {
  const r = await extrair('santos dumont', 'pessoa');
  assert.equal(r.metadados.titulo, 'Santos Dumont');
  assert.match(r.fatos[0].texto, /^Alberto Santos Dumont \(Palmira, 20 de julho de 1873/);
  assert.equal(r.fatos[0].confianca, 'alta');
  assert.ok(r.atributos.some((a) => /^Nascimento/.test(a.nome) && /1873/.test(a.valor)), JSON.stringify(r.atributos.slice(0, 5)));
  const secoes = new Set(r.fatos.map((f) => f.secao).filter(Boolean));
  assert.ok(secoes.size >= 2 && secoes.size <= 4);
  assert.ok(r.conceitos.length >= 5);
});

test('Vilhena (lugar): infobox com população e nenhuma sujeira', async () => {
  const r = await extrair('vilhena', 'lugar');
  assert.match(r.fatos[0].texto, /Vilhena é um município/);
  assert.ok(r.atributos.some((a) => /^Popula/.test(a.nome) && /hab/.test(a.valor)));
  for (const a of r.atributos) assert.doesNotMatch(`${a.nome} ${a.valor}`, /\[\d+\]|mw-parser-output|\{.*\}|Expandir|\s\)|\(\s|\bkm km\b|R\$ [\d ,]+ R\$/);
  const mapa = Object.fromEntries(r.atributos.map((a) => [a.nome, a.valor]));
  assert.equal(mapa['Distância até a capital'], 'Federal: 1,733 km; Estadual: 699 km'); // o original repetia "km km"
  assert.match(mapa['PIB per capita (IBGE/2023)'], /^R\$ 53 382,85$/);
});

test('desambiguação: pula a página "pode referir-se a" e usa o primeiro sentido razoável', async () => {
  const ctx = ctxFalso();
  const r = await extrair('mercurio', 'definicao', ctx);
  assert.equal(r.metadados.titulo, 'Mercúrio (planeta)');
  assert.match(r.fatos[0].texto, /planeta/i);
  assert.ok(ctx.pedidos.every((p) => !/page\/html\/Merc%C3%BArio$/.test(p)), 'não deve baixar a página de desambiguação');
});

test('desambiguação: se a URL cai direto na página de desambiguação, devolve null', async () => {
  const r = await wikipedia.extrair({ consulta: 'x', tema: 'mercurio', tipo: 'definicao', url: 'https://pt.wikipedia.org/wiki/Mercúrio' }, ctxFalso());
  assert.equal(r, null);
});

test('página inexistente: busca sem resultado ou HTML 404 devolvem null', async () => {
  assert.equal(await extrair('xqzkwj'), null);
  assert.equal(await extrair('astrologia', 'definicao', ctxFalso({ semPagina: ['Astrologia'] })), null);
});

test('busca ignora resultados cujo título não tem a ver com o tema', async () => {
  // a busca por texto completo devolve páginas só "citadas"; sem título parecido, não inventa
  const ctx = ctxFalso();
  ctx.buscar = async (url) => {
    const texto = JSON.stringify({ query: { pages: [{ title: 'Carla Vilhena', index: 1 }, { title: 'Paulo Vilhena', index: 2 }] } });
    return { status: 200, ok: true, texto, json: () => JSON.parse(texto) };
  };
  assert.equal(await extrair('astrologia', 'definicao', ctx), null);
});

test('erro de rede: o adaptador lança e o roteador isola a falha', async () => {
  await assert.rejects(() => extrair('astrologia', 'definicao', ctxFalso({ erro: 'sem rede' })), /sem rede/);
  const r = await conhecer('o que é astrologia', ctxFalso({ erro: 'sem rede' }), { adaptadores: [wikipedia] });
  assert.equal(r.falhas[0].adaptador, 'wikipedia');
  assert.deepEqual(r.fatos, []);
});

test('pelo roteador: extrai de ponta a ponta e junta no formato do contrato', async () => {
  const r = await conhecer('o que é astrologia', ctxFalso(), { adaptadores: [wikipedia] });
  assert.equal(r.tipo, 'definicao');
  assert.deepEqual(r.adaptadores, ['wikipedia']);
  assert.ok(r.fatos.length >= 3 && r.conceitos.length >= 5);
});

test('frases: não corta em abreviaturas nem iniciais', () => {
  assert.deepEqual(frases('O Dr. Silva nasceu no séc. XIX. Morreu em 300 a.C. em Roma. Fim da história.'),
    ['O Dr. Silva nasceu no séc. XIX.', 'Morreu em 300 a.C. em Roma.', 'Fim da história.']);
});

test('metadados do adaptador seguem o contrato', () => {
  assert.equal(wikipedia.nome, 'wikipedia');
  assert.equal(wikipedia.licenca, 'CC BY-SA 4.0');
  assert.deepEqual(wikipedia.dominios, ['pt.wikipedia.org', 'en.wikipedia.org']);
  for (const t of ['definicao', 'pessoa', 'lugar', 'geral']) assert.ok(wikipedia.tipos.includes(t));
});

test('legenda de imagem não vira fato, frase de verdade sim', () => {
  assert.equal(pareceProsa('Estrutura de um neurônio motor'), false);
  assert.equal(pareceProsa('Os neurônios são células do sistema nervoso que transmitem impulsos elétricos.'), true);
});
