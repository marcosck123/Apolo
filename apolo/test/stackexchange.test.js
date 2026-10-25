import assert from 'node:assert/strict';
import { test } from 'node:test';
import { codigosDoStackExchange, decodificar, extrairBlocos, palavrasDaBusca } from '../pesquisa/stackexchange.js';

test('palavrasDaBusca: fica só com o assunto, sem palavra de pergunta nem acento', () => {
  assert.equal(palavrasDaBusca('Como calcular a média de uma lista em python?'), 'calcular media lista');
  assert.equal(palavrasDaBusca('como em python'), '');
});

test('decodificar: entidades HTML nomeadas, decimais e hexadecimais', () => {
  assert.equal(decodificar('a &lt; b &amp;&amp; c &#233; &#x41;'), 'a < b && c é A');
});

test('extrairBlocos: pega o código dos <pre><code> e o parágrafo anterior', () => {
  const html = '<p>Use <code>sum</code> e <code>len</code>:</p>\n<pre><code>nums = [1, 2]\nprint(sum(nums) / len(nums))\n</code></pre><p>Fim</p>';
  const [b] = extrairBlocos(html);
  assert.equal(b.texto, 'nums = [1, 2]\nprint(sum(nums) / len(nums))');
  assert.equal(b.explicacao, 'Use sum e len:');
  assert.deepEqual(extrairBlocos('<p>sem código</p>'), []);
});

function fetchFalso(rotas) {
  return async (url) => {
    const achada = Object.entries(rotas).find(([trecho]) => String(url).includes(trecho));
    if (!achada) throw new Error(`sem rota para ${url}`);
    return { ok: true, json: async () => achada[1] };
  };
}

test('codigosDoStackExchange: busca perguntas aceitas, lê a resposta e devolve candidatos com a fonte', async () => {
  const fetchFn = fetchFalso({
    '/search/advanced': { items: [{ accepted_answer_id: 7, link: 'https://pt.stackoverflow.com/q/1' }, { link: 'https://pt.stackoverflow.com/q/2' }] },
    '/answers/7': { items: [{ answer_id: 7, body: '<p>Assim:</p><pre><code>print(1 &lt; 2)</code></pre>' }] },
  });
  const r = await codigosDoStackExchange('como somar em python', { fetchFn, sites: ['pt.stackoverflow'] });
  assert.deepEqual(r, [{ linguagem: 'python', codigo: 'print(1 < 2)', explicacao: 'Assim:', fonte: 'https://pt.stackoverflow.com/q/1' }]);
});

test('codigosDoStackExchange: erro da API ou pergunta vazia não quebra', async () => {
  const fora = async () => { throw new Error('sem rede'); };
  assert.deepEqual(await codigosDoStackExchange('listas python', { fetchFn: fora }), []);
  assert.deepEqual(await codigosDoStackExchange('como em python', { fetchFn: fora }), []);
});
