import assert from 'node:assert/strict';
import { test } from 'node:test';
import { criarAprendizadoAutomatico, criarConhecedor, criarLimitador, verificarFatos } from '../src/conhecimento.js';

const fato = (adaptador, texto, fonte, extra = {}) => ({ texto, fonte, adaptador, confianca: 'media', ...extra });

const wiki = fato('wikipedia', 'Astrologia é um conjunto de práticas que relaciona a posição dos astros a eventos humanos.', 'https://pt.wikipedia.org/wiki/Astrologia', { confianca: 'alta' });
const escola = fato('brasilescola', 'A astrologia estuda a posição dos astros e a relação dela com eventos humanos e personalidade.', 'https://brasilescola.uol.com.br/astrologia.htm');
const solto = fato('generico', 'A astrologia é o assunto favorito de quem gosta de horóscopo e de tomates frescos no verão.', 'https://blog.exemplo.com/post');

test('criarConhecedor: sem PESQUISA_URL ou com PESQUISA_AUTO=0 não cria', () => {
  assert.equal(criarConhecedor({ url: '' }), null);
  process.env.PESQUISA_AUTO = '0';
  assert.equal(criarConhecedor({ url: 'http://pesquisa:4000' }), null);
  delete process.env.PESQUISA_AUTO;
});

test('conhecedor: manda a consulta ao /conhecer e devolve o resultado; fora do ar vira null', async () => {
  let enviado;
  const fetchFn = async (url, op) => { enviado = { url: String(url), corpo: JSON.parse(op.body) }; return { ok: true, json: async () => ({ tema: 'astrologia', fatos: [] }) }; };
  const conhecer = criarConhecedor({ url: 'http://pesquisa:4000', fetchFn });
  assert.equal((await conhecer('o que é astrologia')).tema, 'astrologia');
  assert.equal(enviado.url, 'http://pesquisa:4000/conhecer');
  assert.equal(enviado.corpo.consulta, 'o que é astrologia');
  const fora = criarConhecedor({ url: 'http://pesquisa:4000', fetchFn: async () => { throw new Error('ECONNREFUSED'); } });
  assert.equal(await fora('x'), null);
});

test('limitador: bloqueia depois do máximo e libera quando a janela passa', () => {
  let agora = 0;
  const pode = criarLimitador({ max: 2, janelaMs: 1000, agora: () => agora });
  assert.deepEqual([pode(), pode(), pode()], [true, true, false]);
  agora = 1500;
  assert.equal(pode(), true);
});

test('verificarFatos: fonte estruturada entra sozinha; fonte comum só com outra fonte concordando', () => {
  const r = verificarFatos({ tema: 'astrologia', fatos: [wiki, escola, solto] });
  const fontes = r.map((f) => f.adaptador);
  assert.ok(fontes.includes('wikipedia'));
  assert.ok(fontes.includes('brasilescola'), 'concorda com a Wikipédia nos termos principais');
  assert.ok(!fontes.includes('generico'), 'frase solta, sem outra fonte que a apoie, fica de fora');
});

test('verificarFatos: fonte comum sozinha não entra, calculadora é barrada, texto sem o tema também', () => {
  assert.deepEqual(verificarFatos({ tema: 'astrologia', fatos: [escola] }), []);
  const calc = fato('generico', 'A astrologia calcula a posição dos astros com uma calculadora online completa e grátis.', 'https://www.calculadoraonline.com.br/basica', { confianca: 'alta' });
  assert.deepEqual(verificarFatos({ tema: 'astrologia', fatos: [calc] }), []);
  const outroTema = fato('brasilescola', 'A geologia estuda as rochas e a formação da Terra ao longo de milhões de anos.', 'https://brasilescola.uol.com.br/geologia.htm');
  assert.deepEqual(verificarFatos({ tema: 'astrologia', fatos: [outroTema, wiki] }).map((f) => f.adaptador), ['wikipedia']);
});

test('verificarFatos: números que se contradizem derrubam a fonte de menos confiança', () => {
  const certo = fato('wikipedia', 'Porto Velho foi fundada em 1907 às margens do rio Madeira em Rondônia.', 'https://pt.wikipedia.org/wiki/Porto_Velho', { confianca: 'alta' });
  const errado = fato('generico', 'Porto Velho foi fundada em 1850 às margens do rio Madeira em Rondônia.', 'https://blog.exemplo.com/pv');
  const r = verificarFatos({ tema: 'porto velho', fatos: [certo, errado] });
  assert.deepEqual(r.map((f) => f.adaptador), ['wikipedia']);
});

function montar(resultado, opcoes = {}) {
  const guardados = [];
  const eventos = [];
  const aprender = criarAprendizadoAutomatico({
    conhecer: resultado === undefined ? undefined : async () => resultado,
    lembrar: async (n) => guardados.push(n),
    registrar: (tipo, dados) => eventos.push({ tipo, ...dados }),
    ...opcoes,
  });
  return { aprender, guardados, eventos };
}

test('aprender: guarda fatos, atributos, FAQ e conceitos com origem web e responde com a fonte e o aviso', async () => {
  const { aprender, guardados, eventos } = montar({
    tema: 'astrologia', metadados: { titulo: 'Astrologia' },
    fatos: [wiki, escola, solto],
    atributos: [{ nome: 'Origem', valor: 'Mesopotâmia', fonte: 'https://pt.wikipedia.org/wiki/Astrologia' }],
    pares: [{ pergunta: 'O que é astrologia?', resposta: 'Um sistema de crenças sobre os astros.', fonte: 'https://brasilescola.uol.com.br/astrologia.htm' }],
    conceitos: [{ nome: 'Horóscopo', peso: 0.9, url: 'https://pt.wikipedia.org/wiki/Hor%C3%B3scopo' }, { nome: 'Zodíaco', peso: 0.5 }],
  });
  const resposta = await aprender('o que é astrologia?');
  assert.match(resposta, /^Astrologia é um conjunto de práticas/);
  assert.match(resposta, /\(fonte: pt\.wikipedia\.org\)/);
  assert.match(resposta, /ainda não foi verificada/);
  assert.ok(guardados.every((n) => n.origem === 'web'));
  assert.ok(guardados.some((n) => n.tipo === 'fato' && n.conteudo.startsWith('Astrologia :: Astrologia é um conjunto')));
  assert.ok(guardados.some((n) => n.conteudo === 'Astrologia :: Origem: Mesopotâmia. (fonte: https://pt.wikipedia.org/wiki/Astrologia)'));
  assert.ok(guardados.some((n) => n.conteudo.startsWith('O que é astrologia? :: Um sistema de crenças')));
  assert.deepEqual(guardados.filter((n) => n.tipo === 'conceito').map((n) => n.conteudo.split(' :: ')[0]), ['Horóscopo', 'Zodíaco']);
  assert.ok(!guardados.some((n) => n.conteudo.includes('tomates')), 'o fato solto não é guardado');
  assert.equal(eventos[0].tipo, 'pesquisou');
  assert.equal(eventos[0].automatica, true);
});

test('aprender: não duplica o que já existe na memória', async () => {
  const { aprender, guardados } = montar({ tema: 'astrologia', fatos: [wiki] }, { jaExiste: async () => true });
  await aprender('o que é astrologia?');
  assert.equal(guardados.length, 0);
});

test('aprender: nada confiável, serviço fora do ar, sem pesquisa e limite excedido respondem com honestidade', async () => {
  assert.match(await montar({ tema: 'astrologia', fatos: [solto] }).aprender('o que é astrologia?'), /não achei nada confiável sobre astrologia/);
  assert.equal(await montar(null).aprender('o que é astrologia?'), null);
  assert.equal(await montar(undefined).aprender('o que é astrologia?'), null);
  assert.match(await montar({ tema: 'x', fatos: [] }, { limitador: () => false }).aprender('o que é x?'), /pergunte de novo em um minuto/);
  const semGuardar = montar({ tema: 'astrologia', fatos: [solto] });
  await semGuardar.aprender('o que é astrologia?');
  assert.equal(semGuardar.guardados.length, 0, 'sem fato confiável não grava nada');
});
