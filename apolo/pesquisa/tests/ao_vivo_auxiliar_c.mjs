// Auxiliar dos scripts ao_vivo_*.mjs: roda um adaptador com o ctx de verdade e imprime contagens e 2 amostras por campo.
import { criarCtx } from '../adaptadores/ctx.js';

export async function rodar(adaptador, entradas) {
  for (const entrada of entradas) {
    let pedidos = 0;
    const base = criarCtx({ registrar: (m) => console.log(`   [log] ${m}`) });
    const ctx = { ...base, buscar: async (u, o) => { pedidos++; console.log(`   [GET] ${u}`); return base.buscar(u, o); } };
    console.log(`\n=== ${adaptador.nome} ${JSON.stringify(entrada)}`);
    const t0 = Date.now();
    let r;
    try { r = await adaptador.extrair(entrada, ctx); } catch (e) { console.log('   ERRO:', e.message); continue; }
    console.log(`   ${Date.now() - t0} ms, ${pedidos} requisição(ões)`);
    if (!r) { console.log('   → null'); continue; }
    console.log('   metadados:', JSON.stringify(r.metadados));
    const amostra = { fatos: (x) => `[${x.confianca}${x.tipo ? '/' + x.tipo : ''}] (${x.secao}) ${x.texto}`, conceitos: (x) => `${x.nome} (${x.peso}) ${x.url ?? ''}`, pares: (x) => `${x.pergunta} => ${x.resposta}`, codigos: (x) => `[${x.linguagem}] ${x.codigo.slice(0, 160).replace(/\n/g, '⏎')} | expl: ${x.explicacao.slice(0, 100)}`, atributos: (x) => `${x.nome} = ${x.valor}` };
    for (const campo of Object.keys(amostra)) {
      console.log(`   ${campo}: ${r[campo].length}`);
      for (const x of r[campo].slice(0, 2)) console.log(`      - ${amostra[campo](x)}`);
    }
  }
}
