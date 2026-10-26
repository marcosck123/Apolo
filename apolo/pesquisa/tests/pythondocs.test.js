import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { criarCtx } from '../adaptadores/ctx.js';
import pythondocs, { alvoDeUrl, candidatos, extrairDaPagina, limparCodigo } from '../adaptadores/pythondocs.js';

const ler = (nome) => readFileSync(new URL(`./fixtures/pythondocs/${nome}`, import.meta.url), 'utf8');

// ctx falso: devolve as páginas salvas pelo endereço; o resto é 404. Guarda os endereços pedidos.
function ctxFalso(paginas, { so = null } = {}) {
  const pedidos = [];
  return {
    pedidos,
    parsear: criarCtx().parsear,
    registrar: () => {},
    buscar: async (url) => {
      pedidos.push(url);
      const caminho = url.replace('https://docs.python.org/', '');
      const arquivo = paginas[caminho];
      if (!arquivo || (so && !so.test(caminho))) return { status: 404, ok: false, url, texto: '<html><body><h1>404</h1></body></html>' };
      return { status: 200, ok: true, url, texto: typeof arquivo === 'string' && arquivo.startsWith('<') ? arquivo : ler(arquivo) };
    },
  };
}
const PAGINAS = {
  'pt-br/3/library/statistics.html': 'statistics.html',
  'pt-br/3/library/json.html': 'json.html',
  'pt-br/3/glossary.html': 'glossary.html',
};

test('candidatos: nome com ponto, nome solto, frase e outra linguagem', () => {
  assert.deepEqual(candidatos('statistics.mean')[0], { caminho: 'library/statistics.html', id: 'statistics.mean', tipo: 'objeto' });
  assert.equal(candidatos('como usar json.loads em python')[0].id, 'json.loads');
  const solto = candidatos('json');
  assert.deepEqual(solto.map((a) => a.tipo), ['modulo', 'objeto', 'glossario']);
  assert.deepEqual(candidatos('list comprehension'), [{ caminho: 'glossary.html', id: 'term-list-comprehension', termo: 'list comprehension', tipo: 'glossario' }]);
  assert.deepEqual(candidatos('como usar map em javascript', 'como usar map em javascript'), []);
  assert.deepEqual(candidatos(''), []);
  assert.equal(alvoDeUrl('https://docs.python.org/pt-br/3/library/json.html#json.loads').id, 'json.loads');
  assert.equal(alvoDeUrl('https://exemplo.com/x'), null);
});

test('limparCodigo: tira >>> e ..., separa a saída e deixa código comum como está', () => {
  assert.deepEqual(limparCodigo('>>> for x in [1, 2]:\n...     print(x)\n1\n2\n>>> x\n2'), { codigo: 'for x in [1, 2]:\n    print(x)\nx', saida: '1 2 2' });
  assert.deepEqual(limparCodigo('import json\njson.loads("1")\n'), { codigo: 'import json\njson.loads("1")', saida: '' });
});

test('statistics.mean: descrição, assinatura, exemplo limpo e conceitos py:', async () => {
  const ctx = ctxFalso(PAGINAS);
  const r = await pythondocs.extrair({ tema: 'statistics.mean', tipo: 'codigo' }, ctx);
  assert.equal(ctx.pedidos.length, 1);
  assert.equal(r.metadados.idioma, 'pt-BR');
  assert.equal(r.metadados.url, 'https://docs.python.org/pt-br/3/library/statistics.html#statistics.mean');
  assert.match(r.fatos[0].texto, /^Retorna a média aritmética amostral de data/);
  assert.equal(r.fatos[0].confianca, 'alta');
  assert.equal(r.fatos[0].adaptador, 'pythondocs');
  assert.match(r.fatos[0].licenca, /Python Software Foundation License/);
  assert.ok(r.fatos.every((f) => f.fonte.includes('#statistics.mean')));
  assert.deepEqual(r.atributos.map((a) => [a.nome, a.valor]), [['statistics.mean (assinatura)', 'statistics.mean(data)']]);
  const c = r.codigos[0];
  assert.equal(c.linguagem, 'python');
  assert.ok(c.codigo.startsWith('mean([1, 2, 3, 4, 4])'));
  assert.ok(!c.codigo.includes('>>>') && !c.codigo.includes('2.625'));
  assert.match(c.explicacao, /Saída: 2\.8 2\.625/);
  assert.ok(r.conceitos.some((x) => x.nome === 'statistics.StatisticsError' && x.url.endsWith('#statistics.StatisticsError')));
  assert.ok(!JSON.stringify(r).includes('Texto escondido'));
});

test('json.loads: caminho do módulo pelo nome com ponto, em frase de pergunta', async () => {
  const ctx = ctxFalso(PAGINAS);
  const r = await pythondocs.extrair({ consulta: 'como usar json.loads em python', tema: 'como usar json.loads em python', tipo: 'codigo' }, ctx);
  assert.deepEqual(ctx.pedidos, ['https://docs.python.org/pt-br/3/library/json.html']);
  assert.equal(r.atributos[0].nome, 'json.loads (assinatura)');
  assert.match(r.atributos[0].valor, /^json\.loads\(s, \*,/);
  assert.ok(r.fatos.length >= 1 && r.fatos.every((f) => pareceFraseSimples(f.texto)));
  assert.ok(r.codigos.every((x) => !x.codigo.includes('>>>')));
});
const pareceFraseSimples = (t) => t.length >= 30 && t.length <= 400;

test('módulo inteiro: fatos da introdução e uma assinatura por função', async () => {
  const ctx = ctxFalso(PAGINAS);
  const r = await pythondocs.extrair({ tema: 'statistics', tipo: 'definicao' }, ctx);
  assert.match(r.fatos[0].texto, /Esse módulo fornece funções/);
  assert.deepEqual(r.atributos.map((a) => a.nome), ['statistics.mean (assinatura)', 'statistics.median (assinatura)', 'statistics.StatisticsError (assinatura)']);
  assert.equal(r.metadados.titulo, 'statistics');
});

test('glossário: acha por id em inglês e por texto em português (sem acento)', async () => {
  for (const tema of ['list comprehension', 'compreensao de lista']) {
    const ctx = ctxFalso(PAGINAS);
    const r = await pythondocs.extrair({ tema, tipo: 'definicao' }, ctx);
    assert.ok(r, tema);
    assert.match(r.fatos[0].texto, /^compreensão de lista: Uma maneira compacta de processar/);
    assert.equal(r.fatos[0].secao, 'Glossário');
    assert.match(r.fatos[0].texto, /format\(x\) for x in range\(256\)|'\{:#04x\}'\.format\(x\)/); // o exemplo do glossário é código em linha, não bloco
    assert.deepEqual(r.codigos, []);
  }
});

test('sem tradução: cai para o original em inglês e marca o idioma', async () => {
  const ctx = ctxFalso({ '3/library/statistics.html': 'statistics.html' });
  const r = await pythondocs.extrair({ tema: 'statistics.mean' }, ctx);
  assert.deepEqual(ctx.pedidos, ['https://docs.python.org/pt-br/3/library/statistics.html', 'https://docs.python.org/3/library/statistics.html']);
  assert.equal(r.metadados.idioma, 'en');
  assert.ok(r.metadados.url.startsWith('https://docs.python.org/3/'));
});

test('recebe url do roteador e vai direto no objeto', async () => {
  const ctx = ctxFalso(PAGINAS);
  const r = await pythondocs.extrair({ tema: 'qualquer', url: 'https://docs.python.org/pt-br/3/library/statistics.html#statistics.median' }, ctx);
  assert.equal(r.atributos[0].valor, 'statistics.median(data)');
  assert.equal(ctx.pedidos.length, 1);
});

test('página inexistente, outra linguagem e estrutura inesperada devolvem null, sem estourar o orçamento', async () => {
  const vazio = ctxFalso({});
  assert.equal(await pythondocs.extrair({ tema: 'foo.bar', tipo: 'codigo' }, vazio), null);
  assert.ok(vazio.pedidos.length <= 5);
  const js = ctxFalso(PAGINAS);
  assert.equal(await pythondocs.extrair({ consulta: 'como usar map em javascript', tema: 'como usar map em javascript', tipo: 'codigo' }, js), null);
  assert.equal(js.pedidos.length, 0);
  // existe, mas o objeto não está na página (o site mudou ou o nome está errado)
  const errado = ctxFalso(PAGINAS);
  assert.equal(await pythondocs.extrair({ tema: 'statistics.naoexiste' }, errado), null);
  // HTML sem a estrutura do Sphinx
  const ctx = ctxFalso({ 'pt-br/3/library/json.html': '<html><body><h1>json</h1><p>Página sem seções.</p></body></html>' });
  assert.equal(await pythondocs.extrair({ tema: 'json.loads' }, ctx), null);
  assert.equal(extrairDaPagina(criarCtx().parsear('<html></html>'), { id: 'x', tipo: 'objeto', url: 'https://docs.python.org/3/x.html', idioma: 'en' }), null);
});

test('conteúdo escondido (display:none, aria-hidden) não vira fato nem código', async () => {
  const html = ler('statistics.html').replace('<dd><p class="translated">Retorna', '<dd><p style="display:none">Este parágrafo escondido não deveria virar um fato nunca.</p><div aria-hidden="true"><p>Outro parágrafo escondido que também deve ser ignorado.</p></div><div class="highlight" style="display: none"><pre>>>> escondido()\nsegredo</pre></div><p class="translated">Retorna');
  const ctx = ctxFalso({ 'pt-br/3/library/statistics.html': html });
  const r = await pythondocs.extrair({ tema: 'statistics.mean' }, ctx);
  const tudo = JSON.stringify(r);
  assert.ok(!tudo.includes('escondido') && !tudo.includes('segredo'));
  assert.match(r.fatos[0].texto, /^Retorna a média/);
});

test('erro de rede propaga (o roteador isola); 503 também', async () => {
  const quebrado = { parsear: criarCtx().parsear, registrar: () => {}, buscar: async () => { throw new Error('rede caiu'); } };
  await assert.rejects(() => pythondocs.extrair({ tema: 'json.loads' }, quebrado), /rede caiu/);
  const indisponivel = { ...quebrado, buscar: async (url) => ({ status: 503, ok: false, url, texto: '' }) };
  await assert.rejects(() => pythondocs.extrair({ tema: 'json.loads' }, indisponivel), /503/);
});
