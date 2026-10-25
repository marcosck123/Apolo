import assert from 'node:assert/strict';
import { test } from 'node:test';
import { criarPesquisa, criarPesquisador, extrairConsulta } from '../src/pesquisa.js';
import { ipPublico, urlPermitida } from '../pesquisa/rede.js';
import { desembrulhar, desembrulharBing } from '../pesquisa/links.js';

test('extrairConsulta: reconhece pedidos de pesquisa e tira o enfeite', () => {
  assert.equal(extrairConsulta('pesquise sobre gatos'), 'gatos');
  assert.equal(extrairConsulta('Pesquisa na internet sobre a história de Rondônia!'), 'história de Rondônia');
  assert.equal(extrairConsulta('por favor, busque o preço do dólar?'), 'preço do dólar');
  assert.equal(extrairConsulta('procure pela capital da França'), 'capital da França');
});

test('extrairConsulta: conversa comum não vira pesquisa', () => {
  assert.equal(extrairConsulta('oi, tudo bem?'), null);
  assert.equal(extrairConsulta('eu pesquisei ontem'), null);
  assert.equal(extrairConsulta('pesquise'), null);
});

test('criarPesquisador: sem PESQUISA_URL não cria', () => {
  assert.equal(criarPesquisador({ url: '' }), null);
});

test('pesquisador: manda a consulta ao navegador e devolve os resultados', async () => {
  let enviado;
  const fetchFn = async (url, opcoes) => {
    enviado = { url: String(url), corpo: JSON.parse(opcoes.body) };
    return { ok: true, json: async () => ({ resultados: [{ titulo: 'A', url: 'https://a.com', resumo: 'x' }] }) };
  };
  const pesquisar = criarPesquisador({ url: 'http://pesquisa:4000', fetchFn });
  assert.deepEqual(await pesquisar('gatos'), [{ titulo: 'A', url: 'https://a.com', resumo: 'x' }]);
  assert.equal(enviado.url, 'http://pesquisa:4000/pesquisar');
  assert.equal(enviado.corpo.consulta, 'gatos');
});

test('pesquisador: navegador fora do ar degrada para null', async () => {
  const fetchFn = async () => { throw new Error('ECONNREFUSED'); };
  assert.equal(await criarPesquisador({ url: 'http://pesquisa:4000', fetchFn })('gatos'), null);
});

function montar(pesquisador) {
  const lembrados = [];
  const eventos = [];
  const responder = criarPesquisa({
    pesquisador,
    lembrar: async (f) => lembrados.push(f),
    registrar: (tipo, dados) => eventos.push({ tipo, ...dados }),
  });
  return { responder, lembrados, eventos };
}

test('pesquisa: guarda os achados como fatos e responde com o melhor resumo e a fonte', async () => {
  const { responder, lembrados, eventos } = montar(async () => [
    { titulo: 'Gato', resumo: 'O gato é um mamífero.', url: 'https://www.exemplo.com/gato' },
    { titulo: 'Vazio', resumo: '', url: 'https://b.com' },
    { titulo: 'Felinos', resumo: 'Felinos caçam.', url: 'https://c.com/f' },
  ]);
  assert.equal(await responder('gatos'), 'O gato é um mamífero. (fonte: exemplo.com)');
  assert.deepEqual(lembrados.map((l) => l.tipo), ['fato', 'fato']);
  assert.deepEqual(lembrados.map((l) => l.origem), ['web', 'web']);
  assert.equal(lembrados[0].conteudo, 'Gato :: O gato é um mamífero. (fonte: https://www.exemplo.com/gato)');
  assert.equal(eventos[0].tipo, 'pesquisou');
  assert.equal(eventos[0].achados, 3);
});

test('pesquisa: sem navegador, falha ou nada útil, responde com honestidade e não grava', async () => {
  for (const [pesquisador, trecho] of [
    [null, 'não estou conectado'],
    [async () => null, 'não consegui pesquisar'],
    [async () => [{ titulo: 'x', resumo: '', url: 'https://x.com' }], 'não achei nada'],
  ]) {
    const { responder, lembrados } = montar(pesquisador);
    assert.match((await responder('gatos')).toLowerCase(), new RegExp(trecho));
    assert.equal(lembrados.length, 0);
  }
});

test('rede: só endereços públicos passam', async () => {
  for (const ip of ['127.0.0.1', '10.0.0.5', '172.18.0.3', '192.168.1.1', '169.254.169.254', '::1', 'fd00::1', '::ffff:10.0.0.1']) {
    assert.equal(ipPublico(ip), false, ip);
  }
  for (const ip of ['8.8.8.8', '2606:4700:4700::1111']) assert.equal(ipPublico(ip), true, ip);
});

test('rede: urlPermitida barra esquemas estranhos, hosts internos e DNS que aponta para dentro', async () => {
  const resolver = async (host) => [{ address: host === 'interno.com' ? '172.18.0.2' : '93.184.216.34' }];
  assert.equal(await urlPermitida('https://exemplo.com/a', resolver), true);
  assert.equal(await urlPermitida('file:///etc/passwd', resolver), false);
  assert.equal(await urlPermitida('http://localhost:5432', async () => [{ address: '127.0.0.1' }]), false);
  assert.equal(await urlPermitida('http://interno.com', resolver), false);
  assert.equal(await urlPermitida('http://169.254.169.254/latest', resolver), false);
  assert.equal(await urlPermitida('isto não é url', resolver), false);
});

test('desembrulhar: tira o destino do redirecionamento do DuckDuckGo', () => {
  assert.equal(desembrulhar('//duckduckgo.com/l/?uddg=https%3A%2F%2Fpt.wikipedia.org%2Fwiki%2FGato&rut=abc'), 'https://pt.wikipedia.org/wiki/Gato');
  assert.equal(desembrulhar('https://exemplo.com/x'), 'https://exemplo.com/x');
});

test('desembrulharBing: decodifica o destino do link de rastreio do Bing', () => {
  const real = 'https://pt.wikipedia.org/wiki/Rond%C3%B4nia';
  const u = 'a1' + Buffer.from(real).toString('base64url');
  assert.equal(desembrulharBing(`https://www.bing.com/ck/a?!&&p=abc&u=${u}&ntb=1`), real);
  assert.equal(desembrulharBing('https://exemplo.com/x'), 'https://exemplo.com/x');
});
