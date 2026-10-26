// Verificação ao vivo do adaptador Stack Overflow (API pública do Stack Exchange).
import { criarCtx } from '../adaptadores/ctx.js';
import stackoverflow from '../adaptadores/stackoverflow.js';

const ctx = criarCtx({ registrar: (m) => console.log('  [log]', m) });
const amostra = (lista, f) => lista.slice(0, 2).map((x) => '    · ' + f(x).slice(0, 200)).join('\n');
for (const consulta of process.argv.slice(2).length ? process.argv.slice(2) : ['calcular média lista python', 'how to reverse a string in python']) {
  const t = Date.now();
  console.log(`\n=== ${consulta}`);
  try {
    const r = await stackoverflow.extrair({ consulta, tipo: 'codigo' }, ctx);
    if (!r) { console.log('  null'); continue; }
    console.log(`  ${Date.now() - t} ms | codigos ${r.codigos.length} | pares ${r.pares.length} | conceitos ${r.conceitos.length}`);
    console.log('  metadados:', JSON.stringify(r.metadados));
    console.log('  codigos:\n' + amostra(r.codigos, (x) => `[${x.linguagem}] ${x.codigo.replace(/\s+/g, ' ')}  // ${x.explicacao.slice(0, 60)}  <${x.fonte}>`));
    console.log('  pares:\n' + amostra(r.pares, (x) => `${x.pergunta} -> ${x.resposta}`));
    console.log('  conceitos:', r.conceitos.map((c) => c.nome).join(', '));
  } catch (e) { console.log('  FALHOU:', e.message); }
}
