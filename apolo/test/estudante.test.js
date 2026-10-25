import { test } from 'node:test';
import assert from 'node:assert/strict';
import { criarEstudante, criarVariacoes } from '../src/estudante.js';
import { montarCorpusAprendido } from '../src/corpus_aprendido.js';
import { criarRespostaDeCodigo } from '../src/codigo.js';

function ambiente(opcoes = {}) {
  const gravados = [], estados = [], eventos = [], sinapses = [];
  const repo = {
    pegarEstudoPendente: async () => ({ id: 1, neuronio_id: 2, tentativas: 1 }),
    buscarNeuronio: async () => ({ id: 2, conteudo: 'Como somar em Python?\nExemplo:\nprint(sum([1]))\nSaída:\n1' }),
    buscarConteudo: async () => null,
    salvarSinapses: async (s) => sinapses.push(...s),
    marcarEstudo: async (...args) => estados.push(args),
  };
  const estudante = criarEstudante({ repo, lembrar: async (n) => { gravados.push(n); return { id: 10 + gravados.length, ...n }; },
    analisar: async () => ({ chamadas: ['sum', 'desconhecida'], importacoes: [], estruturas: [], trechos: [{ tipo: 'numero', inicio: 11, fim: 12 }, { tipo: 'lista', inicio: 10, fim: 13 }] }),
    executar: async ({ codigo }) => codigo.includes('[]') ? { saida: '', erro: 'Traceback (most recent call last):\n  File "/tmp/apolo-x/exemplo.py", line 1, in <module>\nZeroDivisionError: division by zero' } : codigo.includes('"texto"') ? { saida: '', erro: 'TypeError: incompatible' } : { saida: '17\n', erro: '' },
    registrar: (...e) => eventos.push(e), ...opcoes });
  return { estudante, gravados, estados, eventos, sinapses, repo };
}
test('estudante guarda conceitos conhecidos, exemplos e erros reais com origem estudo', async () => {
  const a = ambiente(); await a.estudante.passo();
  assert.equal(a.estados[0][1], 'aprendido');
  assert.equal(a.gravados.length, 4);
  assert.ok(a.gravados.every((n) => n.origem === 'estudo'));
  assert.match(a.gravados[2].conteudo, /Erro:\nZeroDivisionError/);
  assert.ok(a.gravados.every((n) => !n.conteudo.includes('Traceback') && !n.conteudo.includes('/tmp/')), 'só a última linha do erro vai para a memória');
  assert.equal(a.eventos[0][0], 'estudou');
  assert.equal(a.sinapses.length, 1);
});
test('falha de serviço volta à fila e terceira tentativa falha', async () => {
  for (const tentativas of [1, 3]) {
    const a = ambiente({ analisar: async () => null });
    a.repo.pegarEstudoPendente = async () => ({ id: 1, neuronio_id: 2, tentativas });
    await a.estudante.passo();
    assert.equal(a.estados[0][1], tentativas === 3 ? 'falhou' : 'pendente');
  }
});
test('desligado, ocupado e sem ociosidade não retiram outro item', async () => {
  for (const opcoes of [{ habilitado: false }, { ocioso: () => false }]) {
    const a = ambiente(opcoes); a.repo.pegarEstudoPendente = () => assert.fail(); await a.estudante.passo();
  }
  let liberar, retiradas = 0;
  const a = ambiente({ analisar: () => new Promise((resolve) => { liberar = resolve; }) });
  a.repo.pegarEstudoPendente = async () => { retiradas++; return { id: 1, neuronio_id: 2, tentativas: 1 }; };
  const primeiro = a.estudante.passo();
  await new Promise(setImmediate); await a.estudante.passo(); liberar(null); await primeiro;
  assert.equal(retiradas, 1);
});
test('temporizador usa unref e variações preservam Unicode fora do trecho', () => {
  let unref = false;
  ambiente({ agendar: () => ({ unref() { unref = true; } }) }).estudante.iniciar();
  assert.ok(unref);
  assert.deepEqual(criarVariacoes('"😀"; x=1', [{ tipo: 'numero', inicio: 7, fim: 8 }]).exemplos, ['"😀"; x=17']);
});
test('corpus filtra origens, episódios, duplicatas e preserva indentação', () => {
  const n = { tipo: 'habilidade', origem: 'executor', conteudo: 'Pergunta\n\nExemplo:\nif True:\n    print(1)\nSaída:\n1' };
  const c = montarCorpusAprendido([n, n, { ...n, origem: 'web' }, { ...n, tipo: 'episodio' }]);
  assert.deepEqual(c.porOrigem, { executor: 1, estudo: 0 });
  assert.ok(!c.texto.includes('\n\n')); assert.match(c.texto, /\n    print/);
  assert.equal(montarCorpusAprendido([{ ...n, origem: 'usuario' }], { origens: ['usuario'] }).porOrigem.usuario, 1);
});
test('resposta de código enfileira o neurônio devolvido por lembrar', async () => {
  const ids = [];
  await criarRespostaDeCodigo({ buscar: async () => [{ linguagem: 'python', codigo: 'print(1)', fonte: 'https://exemplo.com' }], executar: async () => ({ saida: '1', erro: '' }), lembrar: async () => ({ id: 42 }), enfileirar: async (id) => ids.push(id) })('python');
  assert.deepEqual(ids, [42]);
});
