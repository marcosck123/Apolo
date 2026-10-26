import assert from 'node:assert/strict';
import { test } from 'node:test';
import { concordam, criarAprendizado, criarConhecedor, montarResposta, paraMemoria, reconhecerEsquecer, selecionar } from '../src/conhecimento.js';
import { criarApolo } from '../src/apolo.js';
import { Cerebro } from '../src/nucleo/cerebro.js';
import { abrirFato, responderDaMemoria } from '../src/raciocinio.js';

const WIKI = 'https://pt.wikipedia.org/wiki/Porto_Velho';
const ESCOLA = 'https://brasilescola.uol.com.br/brasil/rondonia.htm';
const direitos = 'Todos os direitos reservados (sem licença aberta)';

const dados = () => ({
  tipo: 'lugar', tema: 'porto velho', adaptadores: ['wikipedia', 'ibge', 'brasilescola'], falhas: [],
  metadados: { titulo: 'Porto Velho – Wikipédia, a enciclopédia livre' },
  fatos: [
    { texto: 'Porto Velho é um município brasileiro e a capital do estado de Rondônia.', fonte: WIKI, adaptador: 'wikipedia', confianca: 'alta', licenca: 'CC BY-SA 4.0' },
    { texto: 'Porto Velho é a capital do estado de Rondônia, no Norte do Brasil.', fonte: ESCOLA, adaptador: 'brasilescola', confianca: 'media', licenca: direitos },
    { texto: 'A cidade foi fundada em 1907 durante a construção da ferrovia Madeira-Mamoré.', fonte: ESCOLA, adaptador: 'brasilescola', confianca: 'media', licenca: direitos },
    { texto: 'Clique aqui para conhecer a gastronomia incrível da região amazônica toda.', fonte: ESCOLA, adaptador: 'brasilescola', confianca: 'baixa', licenca: direitos },
    { texto: 'x'.repeat(300), fonte: ESCOLA, adaptador: 'brasilescola', confianca: 'media', licenca: direitos },
  ],
  atributos: [
    { nome: 'Capital', valor: 'Porto Velho', fonte: 'https://servicodados.ibge.gov.br/x', adaptador: 'ibge' },
    { nome: 'População', valor: '460 434 habitantes (2022)', fonte: 'https://servicodados.ibge.gov.br/x', adaptador: 'ibge' },
    { nome: 'Prefeito', valor: 'alguém', fonte: ESCOLA, adaptador: 'brasilescola' },
  ],
  pares: [{ pergunta: 'Qual é a capital de Rondônia?', resposta: 'Capital: Porto Velho', fonte: ESCOLA, licenca: direitos }],
  conceitos: [
    { nome: 'Rondônia', peso: 1 }, { nome: 'Rio Madeira', peso: 0.7 }, { nome: 'Porto Velho', peso: 0.9 }, { nome: 'Brasil', peso: 0.4 },
  ],
});

test('concordam: mesma ideia com palavras parecidas sim, assuntos diferentes não', () => {
  assert.equal(concordam('Porto Velho é um município brasileiro e a capital do estado de Rondônia.', 'Porto Velho é a capital do estado de Rondônia, no Norte do Brasil.'), true);
  assert.equal(concordam('Porto Velho é a capital do estado de Rondônia.', 'A cidade foi fundada em 1907 durante a ferrovia Madeira-Mamoré.'), false);
  assert.equal(concordam('Oi', 'Oi'), false, 'texto curto demais não prova nada');
});

test('selecionar: fonte confiável entra; fonte comum só se outra confirmar; sem repetição, sem texto longo', () => {
  const s = selecionar(dados());
  assert.deepEqual(s.fatos.map((f) => f.adaptador), ['wikipedia']);
  // O fato do Brasil Escola concorda com o da Wikipédia (mesma ideia): não repete.
  // O de 1907 só tem uma fonte comum, sem confirmação: fica de fora. O de marketing e o gigante também.
  assert.equal(s.fatos.length, 1);
  assert.deepEqual(s.atributos.map((a) => a.nome), ['Capital', 'População']);
  assert.deepEqual(s.conceitos.map((c) => c.nome), ['Rondônia', 'Rio Madeira', 'Brasil'], 'ordenado por peso, sem repetir o próprio tema');
  assert.deepEqual(s.fontes, ['pt.wikipedia.org', 'servicodados.ibge.gov.br', 'brasilescola.uol.com.br']);
});

test('selecionar: fato de fonte comum confirmado por outra fonte entra', () => {
  const d = dados();
  d.fatos = [
    { texto: 'A cidade foi fundada em 1907 durante a construção da ferrovia Madeira-Mamoré.', fonte: ESCOLA, adaptador: 'brasilescola', confianca: 'media', licenca: direitos },
    { texto: 'Fundada em 1907, a cidade surgiu da construção da ferrovia Madeira-Mamoré.', fonte: 'https://outro.com/a', adaptador: 'generico', confianca: 'media', licenca: 'verificar' },
  ];
  assert.equal(selecionar(d).fatos.length, 1);
});

test('selecionar: licença restrita aceita só frase curta (250 caracteres)', () => {
  const d = dados();
  const longa = `${'Porto Velho é a capital de Rondônia e tem muitas coisas. '.repeat(6)}`.trim();
  d.fatos = [{ texto: longa, fonte: ESCOLA, adaptador: 'wikipedia', confianca: 'alta', licenca: direitos }];
  assert.equal(selecionar(d).fatos.length, 0);
});

test('paraMemoria: o formato é o que abrirFato entende, com origem web', () => {
  const m = paraMemoria(selecionar(dados()), 'Porto Velho');
  assert.equal(m.fatos[0].origem, 'web');
  assert.equal(m.fatos[0].conteudo, `Porto Velho :: Porto Velho é um município brasileiro e a capital do estado de Rondônia. (fonte: ${WIKI})`);
  const aberto = abrirFato(m.fatos[0].conteudo);
  assert.equal(aberto.titulo, 'Porto Velho');
  assert.equal(aberto.fonte, WIKI);
  assert.equal(m.conceitos[0].tipo, 'conceito');
  assert.match(m.conceitos[0].conteudo, /relacionado a Porto Velho/);
});

test('o que foi aprendido responde depois, só com a memória: a pergunta casa com o atributo guardado', () => {
  const m = paraMemoria(selecionar(dados()), 'Porto Velho');
  const memoria = m.atributos.map((a, i) => ({ id: i + 1, tipo: 'fato', ativacao: 0.5, conteudo: a.conteudo }));
  const r = responderDaMemoria({ mensagem: 'qual a população de Porto Velho?', memoria });
  assert.match(r.resposta, /460 434 habitantes/);
});

test('montarResposta: atributo que só cita o assunto no nome não conta como pedido', () => {
  const d = dados();
  d.tema = 'fotossintese';
  d.atributos = [{ nome: 'Fotossíntese oxigênica', valor: 'Usa água e libera oxigênio', fonte: WIKI, adaptador: 'wikipedia' }];
  d.fatos = [{ texto: 'Fotossíntese é o processo pelo qual plantas captam a energia da luz.', fonte: WIKI, adaptador: 'wikipedia', confianca: 'alta', licenca: 'CC BY-SA 4.0' }];
  const r = montarResposta('o que é fotossíntese?', selecionar(d));
  assert.match(r, /^Fotossíntese é o processo/);
  assert.ok(!r.includes('oxigênica'));
});

test('montarResposta: dado exato pedido vem primeiro, com uma frase de contexto e as fontes', () => {
  const r = montarResposta('qual a capital de Rondônia?', selecionar(dados()));
  assert.match(r, /^Capital: Porto Velho\. Porto Velho é um município/);
  assert.match(r, /\(fontes: pt\.wikipedia\.org, servicodados\.ibge\.gov\.br, brasilescola\.uol\.com\.br; pesquisei na internet agora\)$/);
  assert.equal(montarResposta('o que é isso?', { fatos: [], atributos: [], fontes: [] }), null);
  // Definição: a frase vem primeiro, sem despejar atributos que ninguém pediu.
  const definicao = montarResposta('o que é Porto Velho?', selecionar(dados()));
  assert.match(definicao, /^Porto Velho é um município brasileiro/);
  assert.ok(!definicao.includes('População:'));
  // Texto longo é cortado em palavra inteira, com reticências.
  const longo = montarResposta('o que é x?', { fatos: [{ texto: 'palavra '.repeat(200) }], atributos: [], fontes: ['a.org'] });
  assert.match(longo, /palavra… \(fontes: a\.org/);
});

function ambiente(extra = {}) {
  const lembrados = [];
  const eventos = [];
  const sinapses = [];
  const apagados = [];
  const repo = {
    buscarConteudo: async (c) => (extra.existentes ?? []).includes(c) ? { id: 99 } : null,
    salvarSinapses: async (s) => sinapses.push(...s),
    apagarNeuronios: async (ids) => { apagados.push(...ids); return ids.length; },
    apagarWebPorTema: async (t) => (t === 'astrologia' ? 3 : 0),
  };
  const aprendizado = criarAprendizado({
    conhecer: extra.conhecer === undefined ? async () => dados() : extra.conhecer,
    lembrar: async (n) => { lembrados.push(n); return { id: 100 + lembrados.length, ...n }; },
    repo, registrar: (...e) => eventos.push(e), ...extra.opcoes,
  });
  return { aprendizado, lembrados, eventos, sinapses, apagados };
}

test('aprender: guarda fatos, atributos e conceitos com origem web, liga os conceitos ao fato principal e responde', async () => {
  const a = ambiente();
  const resposta = await a.aprendizado.aprender('qual a capital de Rondônia?');
  assert.match(resposta, /^Capital: Porto Velho\./);
  assert.ok(a.lembrados.every((n) => n.origem === 'web'));
  assert.deepEqual(a.lembrados.map((n) => n.tipo), ['fato', 'fato', 'fato', 'fato', 'conceito', 'conceito', 'conceito']);
  assert.equal(a.sinapses.length, 3, 'um conceito → um fato principal');
  assert.ok(a.sinapses.every((s) => s.de < s.para && s.peso > 0 && s.peso <= 0.6));
  const [tipo, dadosEvento] = a.eventos[0];
  assert.equal(tipo, 'conheceu');
  assert.equal(dadosEvento.novos, 7);
});

test('aprender: não repete o que já existe na memória', async () => {
  const jaTem = paraMemoria(selecionar(dados()), 'Porto Velho').fatos[0].conteudo;
  const a = ambiente({ existentes: [jaTem] });
  await a.aprendizado.aprender('o que é Porto Velho?');
  assert.ok(!a.lembrados.some((n) => n.conteudo === jaTem));
  assert.equal(a.eventos[0][1].novos, 6);
});

test('aprender: sem nada confiável devolve null e não grava; pesquisa fora do ar também', async () => {
  const vazio = ambiente({ conhecer: async () => ({ tipo: 'geral', tema: 'x', fatos: [], atributos: [], pares: [], conceitos: [], adaptadores: [] }) });
  assert.equal(await vazio.aprendizado.aprender('o que é x?'), null);
  assert.equal(vazio.lembrados.length, 0);
  assert.equal(vazio.eventos[0][1].achou, 0);
  const fora = ambiente({ conhecer: async () => null });
  assert.equal(await fora.aprendizado.aprender('o que é x?'), null);
});

test('aprender: desligado ou sem serviço não faz nada; ocupado pede para esperar', async () => {
  assert.equal(await ambiente({ opcoes: { habilitado: false } }).aprendizado.aprender('o que é x?'), null);
  assert.equal(await ambiente({ conhecer: null }).aprendizado.aprender('o que é x?'), null);
  let liberar;
  const lenta = ambiente({ conhecer: () => new Promise((ok) => { liberar = () => ok(dados()); }) });
  const primeira = lenta.aprendizado.aprender('o que é Porto Velho?');
  assert.match(await lenta.aprendizado.aprender('outra'), /pesquisando outra coisa/);
  liberar();
  assert.ok(await primeira);
});

test('esquecer: a última pesquisa apaga só o que ela criou; por tema usa o repositório', async () => {
  const a = ambiente();
  await a.aprendizado.aprender('o que é Porto Velho?');
  const n = await a.aprendizado.esquecer({ tipo: 'ultimo' });
  assert.equal(n, 7);
  assert.equal(a.apagados.length, 7);
  assert.equal(await a.aprendizado.esquecer({ tipo: 'ultimo' }), 0, 'depois de esquecer não há mais o que esquecer');
  assert.equal(await a.aprendizado.esquecer({ tipo: 'tema', tema: 'astrologia' }), 3);
  assert.equal(a.eventos.filter((e) => e[0] === 'esqueceu').length, 3);
});

test('reconhecerEsquecer: entende os pedidos e ignora o resto', () => {
  assert.deepEqual(reconhecerEsquecer('Esqueça isso'), { tipo: 'ultimo' });
  assert.deepEqual(reconhecerEsquecer('esqueça o que você acabou de aprender'), { tipo: 'ultimo' });
  assert.deepEqual(reconhecerEsquecer('Esqueça o que aprendeu sobre astrologia'), { tipo: 'tema', tema: 'astrologia' });
  assert.deepEqual(reconhecerEsquecer('esqueça tudo sobre Porto Velho'), { tipo: 'tema', tema: 'porto velho' });
  assert.equal(reconhecerEsquecer('oi, tudo bem?'), null);
  assert.equal(reconhecerEsquecer('não esqueça de mim'), null);
});

test('criarConhecedor: sem PESQUISA_URL não cria; manda a consulta; falha vira null', async () => {
  assert.equal(criarConhecedor({ url: '' }), null);
  let enviado;
  const ok = criarConhecedor({ url: 'http://pesquisa:4000', fetchFn: async (u, o) => { enviado = { u: String(u), corpo: JSON.parse(o.body) }; return { ok: true, json: async () => ({ fatos: [] }) }; } });
  assert.deepEqual(await ok('o que é astrologia?'), { fatos: [] });
  assert.equal(enviado.u, 'http://pesquisa:4000/conhecer');
  assert.equal(enviado.corpo.consulta, 'o que é astrologia?');
  assert.equal(await criarConhecedor({ url: 'http://x', fetchFn: async () => { throw new Error('fora'); } })('a'), null);
});

test('pensar: se a resposta apagou neurônios ("esqueça isso"), não reforça sinapses de quem deixou de existir', async () => {
  const cerebro = new Cerebro();
  for (const id of [1, 2, 3]) cerebro.adicionarNeuronio({ id, tipo: 'fato', conteudo: `fato ${id}` });
  cerebro.definirSinapse(1, 2, 0.5);
  cerebro.definirSinapse(2, 3, 0.5);
  const apagados = new Set([2]);
  const salvas = [];
  const usados = [];
  const repo = {
    similares: async () => [{ id: 1, sim: 0.9 }, { id: 2, sim: 0.8 }],
    carregarSubgrafo: async () => cerebro,
    criarNeuronio: async (n) => ({ id: 10, ...n }),
    marcarUso: async (ids) => usados.push(...ids),
    salvarSinapses: async (s) => salvas.push(...s),
    existentes: async (ids) => new Set(ids.filter((i) => !apagados.has(i))),
  };
  const apolo = criarApolo({ repo, embutirTexto: () => [1], raciocinar: async () => 'esqueci' });
  await apolo.pensar('esqueça isso');
  assert.ok(!usados.includes(2), 'o neurônio apagado não é marcado como usado');
  assert.ok(salvas.every((s) => s.de !== 2 && s.para !== 2), 'nenhuma sinapse aponta para o neurônio apagado');
  assert.ok(salvas.length > 0);
});
