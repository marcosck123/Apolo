// Verificação ao vivo do extrator genérico em páginas reais (UMA visita cada, mais o robots.txt do site).
// Uso: node tests/ao_vivo_generico.mjs [url...]
import { criarCtx } from '../adaptadores/ctx.js';
import generico from '../adaptadores/generico.js';

const PADRAO = process.argv.slice(2).length ? process.argv.slice(2) : [
  'https://www.joelonsoftware.com/2000/08/09/the-joel-test-12-steps-to-better-code/', // blog
  'https://agenciabrasil.ebc.com.br/geral/noticia/2026-10/cartorios-lancam-ferramenta-que-permite-pesquisar-imoveis-no-pais', // notícia
  'https://docs.docker.com/get-started/overview/', // documentação
  'https://about.gitlab.com/company/', // página de empresa
];
const ctx = criarCtx({ registrar: (m) => console.log('  [log]', m) });
const amostra = (lista, f) => lista.slice(0, 2).map((x) => '    · ' + f(x).slice(0, 170)).join('\n');
for (const url of PADRAO) {
  const t = Date.now();
  console.log(`\n=== ${url}`);
  try {
    const r = await generico.extrair({ consulta: url, url, tipo: 'geral' }, ctx);
    if (!r) { console.log('  null'); continue; }
    console.log(`  ${Date.now() - t} ms | fatos ${r.fatos.length} | conceitos ${r.conceitos.length} | pares ${r.pares.length} | atributos ${r.atributos.length} | codigos ${r.codigos.length}`);
    console.log('  metadados:', JSON.stringify(r.metadados).slice(0, 300));
    if (r.fatos.length) console.log('  fatos:\n' + amostra(r.fatos, (x) => `[${x.confianca}${x.secao ? ' / ' + x.secao : ''}] ${x.texto}`));
    if (r.conceitos.length) console.log('  conceitos:\n' + amostra(r.conceitos, (x) => `${x.nome} ${x.url ?? ''}`));
    if (r.pares.length) console.log('  pares:\n' + amostra(r.pares, (x) => `${x.pergunta} -> ${x.resposta}`));
    if (r.atributos.length) console.log('  atributos:\n' + amostra(r.atributos, (x) => `${x.nome} = ${x.valor}`));
    if (r.codigos.length) console.log('  codigos:\n' + amostra(r.codigos, (x) => `[${x.linguagem}] ${x.codigo.replace(/\s+/g, ' ')}`));
  } catch (e) { console.log('  FALHOU:', e.message); }
}
