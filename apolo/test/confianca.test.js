import assert from 'node:assert/strict';
import { test } from 'node:test';
import { criarApolo } from '../src/apolo.js';
import { Cerebro } from '../src/nucleo/cerebro.js';
import { paraMemoria, selecionar } from '../src/conhecimento.js';
import { responderDaMemoria } from '../src/raciocinio.js';

const fato = (extra) => ({ id: 1, tipo: 'fato', ativacao: 1, conteudo: 'Brasil :: Brasília é a capital do Brasil. (fonte: https://pt.wikipedia.org/wiki/Bras%C3%ADlia)', ...extra });

test('memória: confiança normal responde só com a fonte; várias fontes dizem quantas; pouca confiança avisa', () => {
  const pergunta = 'qual a capital do brasil';
  assert.equal(responderDaMemoria({ mensagem: pergunta, memoria: [fato({ confianca: 0.65, fontes: 1 })] }).resposta,
    'Brasília é a capital do Brasil. (fonte: pt.wikipedia.org)');
  assert.match(responderDaMemoria({ mensagem: pergunta, memoria: [fato({ confianca: 0.8, fontes: 3 })] }).resposta, /\(confirmado por 3 fontes; fonte: pt\.wikipedia\.org\)$/);
  assert.match(responderDaMemoria({ mensagem: pergunta, memoria: [fato({ confianca: 0.2, fontes: 1 })] }).resposta, /^Não tenho certeza, mas encontrei isto: Brasília é a capital do Brasil\./);
});

test('paraMemoria: confiança sobe quando outra fonte confirma e fica menor em fonte comum', () => {
  const wiki = { texto: 'A astrologia é uma prática divinatória.', fonte: 'https://pt.wikipedia.org/wiki/Astrologia', adaptador: 'wikipedia', confianca: 'alta' };
  const escola = { texto: 'A astrologia estuda os astros.', fonte: 'https://brasilescola.uol.com.br/a.htm', adaptador: 'brasilescola' };
  const m = paraMemoria({ fatos: [{ ...wiki, confirmado: true }, wiki, escola], atributos: [], pares: [], conceitos: [] }, 'Astrologia');
  assert.deepEqual(m.fatos.map((f) => [f.confianca, f.fontes]), [[0.8, 2], [0.65, 1], [0.5, 1]]);
  assert.equal(selecionar({ tema: 'x', fatos: [] }).fatos.length, 0);
});

function repoFalso() {
  const neuronios = [];
  return {
    neuronios,
    similares: async () => [],
    carregarSubgrafo: async () => new Cerebro(),
    criarNeuronio: async (n) => { const novo = { id: neuronios.length + 1, ...n }; neuronios.push(novo); return novo; },
    existentes: async () => new Set(),
    marcarUso: async () => {},
    salvarSinapses: async () => {},
  };
}

test('pensar: resposta do córtex não vira memória; resposta da memória sim, e o pensamento diz quem respondeu', async () => {
  for (const [via, esperado] of [['cortex', 'olá'], ['memoria', 'olá\n→ resposta']]) {
    const repo = repoFalso();
    const apolo = criarApolo({ repo, embutirTexto: () => [1], raciocinar: async () => ({ resposta: 'resposta', via, neuronioId: 7 }) });
    const pensamento = await apolo.pensar('olá');
    assert.equal(repo.neuronios.find((n) => n.tipo === 'episodio').conteudo, esperado);
    assert.equal(pensamento.resposta, 'resposta');
    assert.equal(pensamento.via, via);
    assert.equal(pensamento.neuronioId, 7);
  }
});

test('pensar: raciocinar que devolve só texto continua funcionando', async () => {
  const repo = repoFalso();
  const apolo = criarApolo({ repo, embutirTexto: () => [1], raciocinar: async () => 'oi' });
  const p = await apolo.pensar('olá');
  assert.deepEqual([p.resposta, p.via], ['oi', null]);
});
