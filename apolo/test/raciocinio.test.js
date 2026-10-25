import assert from 'node:assert/strict';
import { test } from 'node:test';
import { abrirFato, ehPergunta, palavrasChave, responderDaMemoria, tituloDoAssunto } from '../src/raciocinio.js';

const web = (id, titulo, resumo, url, ativacao = 0.5) => ({
  id, tipo: 'fato', ativacao, conteudo: `${titulo} :: ${resumo} (fonte: ${url})`,
});
const rondonia = web(43, 'Rondônia – Wikipédia, a enciclopédia livre', 'Sua capital e município mais populoso é Porto Velho, banhada pelo rio Madeira. Além desta, há outras cidades.', 'https://pt.wikipedia.org/wiki/Rond%C3%B4nia', 0.9);
const portoVelho = web(44, 'Porto Velho – Wikipédia', 'Porto Velho é um município brasileiro e a capital do estado de Rondônia. Tem 460 mil habitantes.', 'https://www.exemplo.com/pv', 0.4);
const capivara = web(47, 'Capivara – Wikipédia', 'Capivara[3] é uma espécie de mamífero roedor.', 'https://pt.wikipedia.org/wiki/Capivara');

test('palavrasChave: tira palavras de pergunta, acento e plural simples', () => {
  assert.deepEqual([...palavrasChave('Qual é a capital de Rondônia?')].sort(), ['capital', 'rondonia']);
  assert.ok(palavrasChave('os gatos').has('gato'));
});

test('abrirFato: separa título, frases e fonte; tira referências [3]', () => {
  const f = abrirFato(capivara.conteudo);
  assert.equal(f.titulo, 'Capivara – Wikipédia');
  assert.deepEqual(f.frases, ['Capivara é uma espécie de mamífero roedor.']);
  assert.equal(f.fonte, 'https://pt.wikipedia.org/wiki/Capivara');
  assert.deepEqual(abrirFato('O céu é azul.'), { titulo: '', frases: ['O céu é azul.'], fonte: null });
});

test('responde com a frase do fato que mais fala da pergunta e cita a fonte', () => {
  const r = responderDaMemoria({ mensagem: 'qual a capital de Rondônia?', memoria: [rondonia, portoVelho, capivara] });
  assert.equal(r.neuronioId, 44);
  assert.equal(r.resposta, 'Porto Velho é um município brasileiro e a capital do estado de Rondônia. (fonte: exemplo.com)');
});

test('o título do fato conta como contexto da frase', () => {
  const r = responderDaMemoria({ mensagem: 'o que é uma capivara?', memoria: [capivara] });
  assert.match(r.resposta, /^Capivara é uma espécie de mamífero roedor\. \(fonte: pt\.wikipedia\.org\)$/);
});

test('fato ensinado à mão responde sem fonte', () => {
  const r = responderDaMemoria({ mensagem: 'o Apolo foi criado por quem?', memoria: [{ id: 1, tipo: 'fato', ativacao: 1, conteudo: 'O Apolo foi criado por Marcos.' }] });
  assert.equal(r.resposta, 'O Apolo foi criado por Marcos.');
});

test('não responde quando nenhum fato cobre a pergunta, nem com episódios', () => {
  const episodio = { id: 9, tipo: 'episodio', ativacao: 1, conteudo: 'qual a capital de Rondônia?\n→ Curitiba é a capital.' };
  assert.equal(responderDaMemoria({ mensagem: 'qual a capital da França?', memoria: [rondonia, portoVelho] }), null);
  assert.equal(responderDaMemoria({ mensagem: 'qual a capital de Rondônia?', memoria: [episodio] }), null);
  assert.equal(responderDaMemoria({ mensagem: 'e então?', memoria: [rondonia] }), null);
});

test('desempata pela ativação quando os fatos cobrem igual', () => {
  const a = { id: 1, tipo: 'fato', ativacao: 0.2, conteudo: 'O cavalo corre rápido.' };
  const b = { id: 2, tipo: 'fato', ativacao: 0.8, conteudo: 'O cavalo come capim.' };
  assert.equal(responderDaMemoria({ mensagem: 'cavalo', memoria: [a, b] }).neuronioId, 2);
});

test('abrirFato: título com dois-pontos não confunde a separação', () => {
  const f = abrirFato('Rondônia (RO): capital, mapa - Brasil Escola :: Fica em Rondônia. (fonte: https://b.com/r)');
  assert.equal(f.titulo, 'Rondônia (RO): capital, mapa - Brasil Escola');
  assert.deepEqual(f.frases, ['Fica em Rondônia.']);
});

test('ehPergunta: reconhece perguntas com e sem interrogação', () => {
  for (const m of ['qual a capital da França?', 'Quem descobriu o Brasil', 'o que é uma capivara', 'tem sol?']) assert.ok(ehPergunta(m), m);
  for (const m of ['oi, tudo bem', 'Obrigado!', 'o gato dorme']) assert.ok(!ehPergunta(m), m);
});

test('abrirFato: tira o "Leia mais" que os buscadores deixam no fim do resumo', () => {
  const f = abrirFato('T :: Fica em Rondônia, onde se …Leia mais (fonte: https://b.com/r)');
  assert.deepEqual(f.frases, ['Fica em Rondônia, onde se …']);
});

test('tituloDoAssunto: tira o nome do site do fim do título', () => {
  assert.equal(tituloDoAssunto('Rondônia (RO): capital, mapa, bandeira, economia - Brasil Escola'), 'Rondônia (RO): capital, mapa, bandeira, economia');
  assert.equal(tituloDoAssunto('Rondônia – Wikipédia, a enciclopédia livre'), 'Rondônia');
  assert.equal(tituloDoAssunto('Rio Madeira - Rondônia - Wikipédia'), 'Rio Madeira - Rondônia');
  assert.equal(tituloDoAssunto('Astrologia'), 'Astrologia');
});

test('o nome do site no título não vira assunto: fato de Rondônia não responde "capital do Brasil"', () => {
  const rondoniaEscola = web(61, 'Rondônia (RO): capital, mapa, bandeira, economia - Brasil Escola', 'Fica em Rondônia, na capital Porto Velho, a Jerusalém da Amazônia.', 'https://brasilescola.uol.com.br/brasil/rondonia.htm', 1);
  const brasilia = web(100, 'Brasília – Wikipédia, a enciclopédia livre', 'Brasília é a capital federal do Brasil e a sede de governo do Distrito Federal.', 'https://pt.wikipedia.org/wiki/Bras%C3%ADlia', 0);
  assert.equal(responderDaMemoria({ mensagem: 'qual a capital do brasil', memoria: [rondoniaEscola] }), null);
  const r = responderDaMemoria({ mensagem: 'qual a capital do brasil', memoria: [rondoniaEscola, brasilia] });
  assert.equal(r.neuronioId, 100);
  assert.match(r.resposta, /^Brasília é a capital federal do Brasil/);
});

test('abrirFato: tira a pronúncia fonética entre parênteses', () => {
  const f = abrirFato('Brasília – Wikipédia :: Brasília (AFI: [bɾaˈzilja] ou AFI: [bɾaˈziʎa]) é a capital federal do Brasil. (fonte: https://pt.wikipedia.org/wiki/Bras%C3%ADlia)');
  assert.deepEqual(f.frases, ['Brasília é a capital federal do Brasil.']);
});
