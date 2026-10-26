import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import stackoverflow, { textoDaResposta, tituloCombina } from '../adaptadores/stackoverflow.js';

const lerFixture = (nome) => readFileSync(new URL(`./fixtures/stackoverflow/${nome}`, import.meta.url), 'utf8');

// ctx falso com as respostas reais da API salvas; qualquer outro endereço devolve 400.
function ctxFalso({ falhaEm = [] } = {}) {
  const pedidos = [];
  const arquivos = { 'pt.stackoverflow': 'pt_media', stackoverflow: 'en_reverse' };
  return {
    pedidos,
    registrar: () => {},
    async buscar(url, opcoes) {
      pedidos.push(url);
      const site = new URL(url).searchParams.get('site');
      if (falhaEm.includes(site)) return { status: 429, ok: false, texto: '{"error_id":502,"error_message":"too many requests"}', json: () => ({ error_message: 'too many requests' }) };
      const base = arquivos[site];
      const texto = lerFixture(`${base}_${url.includes('/answers/') ? 'respostas' : 'busca'}.json`);
      assert.equal(opcoes?.json, true);
      return { status: 200, ok: true, url, texto, json: () => JSON.parse(texto) };
    },
  };
}

test('pergunta em português: busca no pt.stackoverflow, devolve códigos com explicação e fonte, e pares', async () => {
  const ctx = ctxFalso();
  const r = await stackoverflow.extrair({ consulta: 'calcular média lista python', tipo: 'codigo' }, ctx);
  assert.ok(r.codigos.length >= 1);
  for (const c of r.codigos) {
    assert.equal(c.linguagem, 'python');
    assert.ok(c.codigo.length >= 8 && c.explicacao.length > 0);
    assert.match(c.fonte, /^https:\/\/(pt\.)?stackoverflow\.com\//);
  }
  assert.ok(r.pares.some((p) => /^https:\/\/pt\.stackoverflow\.com\//.test(p.fonte) && p.pergunta.includes('calcular media')));
  assert.ok(r.pares.every((p) => !/dicion|Como tirar/.test(p.pergunta)), 'vizinhos sem as palavras da busca ficam de fora');
  assert.equal(r.pares.length, 1);
  for (const p of r.pares) {
    assert.ok(p.pergunta && p.resposta.length >= 30 && p.resposta.length <= 301);
    assert.doesNotMatch(p.resposta, /<[a-z]|&amp;|&#39;|&quot;/);
    assert.equal(p.licenca, 'CC BY-SA 4.0');
    assert.equal(p.adaptador, 'stackoverflow');
  }
  assert.equal(r.metadados.idioma, 'pt');
  // A ponte usa ctx.buscar: busca + respostas no primeiro site, e a palavra "python" vai como tag, não como termo.
  assert.equal(ctx.pedidos.length, 3); // busca + respostas no pt, e a busca do segundo site (o pt deu só uma pergunta que combina)
  assert.match(ctx.pedidos[0], /q=calcular\+media\+lista|q=calcular%20media%20lista/);
  assert.match(ctx.pedidos[0], /tagged=python/);
  assert.match(ctx.pedidos[0], /accepted=True/);
});

test('pergunta em inglês: começa pelo stackoverflow, tira palavras de ligação e as entidades HTML do título', async () => {
  const ctx = ctxFalso();
  const r = await stackoverflow.extrair({ consulta: 'how to reverse a string in python', tipo: 'codigo' }, ctx);
  assert.match(ctx.pedidos[0], /site=stackoverflow&/);
  assert.match(ctx.pedidos[0], /q=reverse\+string|q=reverse%20string/);
  assert.ok(r.codigos.length >= 1 && r.codigos.every((c) => /^https:\/\/stackoverflow\.com\//.test(c.fonte)));
  assert.deepEqual(r.pares.map((p) => p.pergunta), ['How do I reverse a string in Python?']);
  assert.ok(r.codigos.every((c) => c.fonte.includes('931092')), 'código só da pergunta que combina');
  assert.equal(r.metadados.idioma, 'en');
});

test('um site fora do ar não impede o outro; os dois fora do ar → erro; consulta sem palavras → null', async () => {
  const r = await stackoverflow.extrair({ consulta: 'calcular média lista python' }, ctxFalso({ falhaEm: ['stackoverflow'] }));
  assert.ok(r.pares.length >= 1 && /pt\.stackoverflow\.com/.test(r.pares[0].fonte));
  const r2 = await stackoverflow.extrair({ consulta: 'how to reverse a string in python' }, ctxFalso({ falhaEm: ['pt.stackoverflow'] }));
  assert.ok(r2.codigos.length >= 1);
  await assert.rejects(stackoverflow.extrair({ consulta: 'calcular média lista python' }, ctxFalso({ falhaEm: ['pt.stackoverflow', 'stackoverflow'] })), /too many requests|429/);
  assert.equal(await stackoverflow.extrair({ consulta: 'como fazer em python' }, ctxFalso()), null);
});

test('textoDaResposta: sem HTML, sem blocos de código, entidades decodificadas e limite de tamanho', () => {
  const html = '<p>Use <code>sum(l) &lt; 3</code> &amp; divida.</p><pre><code>media = sum(l)/len(l)</code></pre><p>' + 'Texto longo. '.repeat(60) + '</p>';
  const t = textoDaResposta(html, 300);
  assert.ok(t.startsWith('Use sum(l) < 3 & divida.'));
  assert.doesNotMatch(t, /media = sum/);
  assert.ok(t.length <= 300);
  assert.equal(textoDaResposta('<p>Curto.</p>'), 'Curto.');
});

test('tituloCombina: pelo menos 60% das palavras, sem acento, com título em entidades HTML', () => {
  assert.equal(tituloCombina('Calcular m&#233;dia de uma lista', 'calcular media lista'), true);
  assert.equal(tituloCombina('Convert integer to string in Python', 'reverse string'), false);
  assert.equal(tituloCombina('Como tirar uma lista de um documento', 'calcular media lista'), false);
});

test('contrato do adaptador', () => {
  assert.equal(stackoverflow.nome, 'stackoverflow');
  assert.deepEqual(stackoverflow.tipos, ['codigo']);
  assert.match(stackoverflow.licenca, /CC BY-SA/);
});
