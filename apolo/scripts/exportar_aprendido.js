import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { parseArgs } from 'node:util';
import { criarRepositorio } from '../src/repositorio.js';
import { montarCorpusAprendido } from '../src/corpus_aprendido.js';

const { values } = parseArgs({ options: {
  origens: { type: 'string', default: 'executor,estudo' },
  saida: { type: 'string', default: 'textos/curriculo/12_aprendido.txt' },
  help: { type: 'boolean', short: 'h' },
} });
if (values.help) {
  console.log('Uso: node scripts/exportar_aprendido.js [--origens executor,estudo,usuario] [--saida caminho]\nPadrão: executor,estudo; saída textos/curriculo/12_aprendido.txt.\nA origem web fica de fora por padrão por licença/atribuição. Revise também as fontes dos exemplos do executor antes de distribuir o corpus.');
} else {
  const origens = values.origens.split(',').map((o) => o.trim());
  if (origens.some((o) => !['executor', 'estudo', 'usuario', 'web'].includes(o))) throw new Error('origem inválida');
  const repo = criarRepositorio();
  try {
    const { rows } = await repo.pool.query('SELECT tipo, origem, conteudo FROM neuronios WHERE origem = ANY($1) ORDER BY id', [origens]);
    const corpus = montarCorpusAprendido(rows, { origens });
    await mkdir(dirname(values.saida), { recursive: true });
    await writeFile(values.saida, corpus.texto);
    console.log(JSON.stringify({ saida: values.saida, blocosPorOrigem: corpus.porOrigem }));
    if (origens.some((o) => ['executor', 'estudo'].includes(o))) {
      console.error('AVISO: os blocos de origem executor/estudo partem de respostas do Stack Overflow (CC BY-SA). A fonte fica no texto, mas confira a licença antes de treinar com eles ou distribuir o modelo.');
    }
  } finally { await repo.fechar(); }
}
