// Verificação ao vivo (não roda nos testes automáticos: sem sufixo .test.js). Uso, no container de pesquisa:
//   node tests/ao_vivo_wikipedia.mjs
// Roda Wikipédia e Wikidata contra os sites reais para 4 consultas e imprime contagens e amostras.
import { criarCtx } from '../adaptadores/ctx.js';
import wikipedia from '../adaptadores/wikipedia.js';
import wikidata from '../adaptadores/wikidata.js';

const todas = [['astrologia', 'definicao'], ['santos dumont', 'pessoa'], ['porto velho', 'lugar'], ['vilhena', 'lugar']];
// opcional: node tests/ao_vivo_wikipedia.mjs <adaptador> [tema]  (as APIs respondem 429 se forem muitas consultas seguidas)
const [, , soAdaptador, soTema] = process.argv;
const consultas = todas.filter(([t]) => !soTema || t === soTema.replace(/_/g, ' '));
const espera = (ms) => new Promise((r) => setTimeout(r, ms));
const curto = (t, n = 150) => (t.length > n ? `${t.slice(0, n)}…` : t);

for (const adaptador of [wikipedia, wikidata].filter((a) => !soAdaptador || a.nome === soAdaptador)) {
  for (const [tema, tipo] of consultas) {
    let pedidos = 0;
    const real = criarCtx();
    const ctx = { ...real, buscar: (...a) => { pedidos++; return real.buscar(...a); } };
    const t0 = Date.now();
    try {
      const r = await adaptador.extrair({ consulta: tema, tema, tipo }, ctx);
      console.log(`\n=== ${adaptador.nome} | "${tema}" (${tipo}) | ${pedidos} requisições, ${Date.now() - t0} ms`);
      if (!r) { console.log('  null'); continue; }
      const { fatos = [], conceitos = [], atributos = [], metadados } = r;
      console.log(`  fatos=${fatos.length} conceitos=${conceitos.length} atributos=${atributos.length} metadados=${JSON.stringify(metadados)}`);
      for (const f of fatos.slice(0, 2)) console.log(`  fato [${f.confianca}${f.secao ? ' / ' + f.secao : ''}]: ${curto(f.texto)}`);
      for (const c of conceitos.slice(0, 2)) console.log(`  conceito: ${c.nome} (${c.peso})`);
      if (conceitos.length > 2) console.log(`  conceito (último): ${conceitos.at(-1).nome} (${conceitos.at(-1).peso})`);
      for (const a of atributos.slice(0, 2)) console.log(`  atributo: ${a.nome} = ${curto(a.valor, 100)}`);
    } catch (erro) {
      console.log(`\n=== ${adaptador.nome} | "${tema}" | ERRO: ${erro.message}`);
    }
    await espera(8000);
  }
}
