// Verificação ao vivo do adaptador mdn (usa a rede de verdade; não faz parte de "node --test").
import { criarCtx } from '../adaptadores/ctx.js';
import adaptador from '../adaptadores/mdn.js';
import { classificar } from '../adaptadores/tipo.js';

const ctx = criarCtx({ registrar: (m) => console.log('  log:', m) });
const consultas = ["array map", "Promise", "fetch", "Math.max", "Math.sumPrecise", "astrologia"];
const amostra = (lista, n = 2) => lista.slice(0, n);
let requisicoes = 0;
const buscarOriginal = ctx.buscar;
ctx.buscar = (...args) => { requisicoes++; return buscarOriginal(...args); };

for (const consulta of consultas) {
  requisicoes = 0;
  console.log('\n=== ' + consulta);
  try {
    const { tema, tipo } = classificar(consulta);
    const r = await adaptador.extrair({ consulta, tema: consulta, tipo }, ctx);
    if (!r) { console.log('  → null (' + requisicoes + ' requisições)'); continue; }
    console.log('  requisições:', requisicoes, '| fatos', r.fatos.length, '| atributos', r.atributos.length, '| conceitos', r.conceitos.length, '| códigos', r.codigos.length, '| pares', r.pares.length);
    console.log('  metadados:', JSON.stringify(r.metadados));
    for (const campo of ['fatos', 'atributos', 'conceitos', 'codigos']) {
      for (const item of amostra(r[campo])) console.log('  ' + campo + ':', JSON.stringify(item).slice(0, 420));
    }
  } catch (erro) {
    console.log('  ERRO:', erro.message);
  }
}
