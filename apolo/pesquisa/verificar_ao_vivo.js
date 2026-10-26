// Verificador ao vivo dos adaptadores: roda cada um da pasta adaptadores/ com 2 consultas de exemplo na internet de verdade
// e imprime uma tabela. Serve para saber quando um site mudou e um adaptador quebrou.
//
//   node verificar_ao_vivo.js                  → todos os adaptadores
//   node verificar_ao_vivo.js wikipedia mdn    → só os citados
//
// Código de saída: 0 se tudo está bem; 1 se algum adaptador FALHOU (erro, tempo esgotado) ou ficou VAZIO nas duas consultas;
// 2 se um nome pedido não existe. Uma consulta VAZIA sozinha só avisa (a fonte pode simplesmente não ter o assunto).
// Educação: uma consulta por vez, sem paralelismo, com o cache de 10 min do ctx (rodar de novo logo em seguida não repete as visitas).
import { fileURLToPath } from 'node:url';
import { carregarAdaptadores } from './adaptadores/index.js';
import { criarCtx } from './adaptadores/ctx.js';
import { classificar } from './adaptadores/tipo.js';

// Consultas de exemplo por adaptador. As que começam por http são URLs entregues ao `url` do adaptador (genérico).
// Adaptador que não está aqui usa CONSULTAS_PADRAO: ao criar um adaptador novo, acrescente a linha dele.
export const CONSULTAS = {
  wikipedia: ['astrologia', 'Santos Dumont'],
  wikidata: ['Santos Dumont', 'Brasil'],
  ibge: ['capital de Rondônia', 'população de Recife'],
  mdn: ['Array.prototype.map', 'fetch javascript'],
  python_docs: ['como usar list comprehension em python', 'o que é um decorator em python'],
  pythondocs: ['como usar list comprehension em python', 'o que é um decorator em python'],
  python: ['como usar list comprehension em python', 'o que é um decorator em python'],
  // Estes dois sites não têm busca permitida pelo robots.txt: só funcionam quando recebem a URL (vinda da busca do navegador).
  brasilescola: ['https://brasilescola.uol.com.br/brasil/rondonia.htm', 'https://brasilescola.uol.com.br/brasil/acre.htm'],
  brasil_escola: ['https://brasilescola.uol.com.br/brasil/rondonia.htm', 'https://brasilescola.uol.com.br/brasil/acre.htm'],
  mundoeducacao: ['https://mundoeducacao.uol.com.br/matematica/media-aritmetica.htm', 'https://mundoeducacao.uol.com.br/matematica/estatistica.htm'],
  mundo_educacao: ['https://mundoeducacao.uol.com.br/matematica/media-aritmetica.htm', 'https://mundoeducacao.uol.com.br/matematica/estatistica.htm'],
  stackoverflow: ['calcular média lista python', 'how to reverse a string in python'],
  generico: ['https://martinfowler.com/bliki/CircuitBreaker.html', 'https://docs.python.org/3/tutorial/venv.html'],
};
export const CONSULTAS_PADRAO = ['o que é astrologia', 'Brasil'];

const CAMPOS = ['fatos', 'conceitos', 'pares', 'atributos', 'codigos'];
const comTempo = (promessa, ms) => {
  let t;
  const limite = new Promise((_, rej) => { t = setTimeout(() => rej(new Error(`passou de ${ms} ms`)), ms); });
  return Promise.race([promessa, limite]).finally(() => clearTimeout(t));
};

// Função pura (recebe adaptadores e ctx): devolve uma linha por adaptador × consulta.
export async function verificar(adaptadores, ctx, { consultas = CONSULTAS, padrao = CONSULTAS_PADRAO, tempoMs = 30_000, agora = () => Date.now() } = {}) {
  const linhas = [];
  for (const adaptador of adaptadores) {
    for (const consulta of consultas[adaptador.nome] ?? padrao) {
      const ehUrl = /^https?:\/\//i.test(consulta);
      const { tema } = classificar(consulta);
      const inicio = agora();
      const linha = { adaptador: adaptador.nome, consulta, ms: 0, contagens: Object.fromEntries(CAMPOS.map((c) => [c, 0])), estado: 'OK', motivo: '' };
      try {
        const r = await comTempo(adaptador.extrair({ consulta, tema: ehUrl ? consulta : tema, tipo: adaptador.tipos?.[0] ?? 'geral', ...(ehUrl ? { url: consulta } : {}) }, ctx), tempoMs);
        for (const c of CAMPOS) linha.contagens[c] = r?.[c]?.length ?? 0;
        if (!r) { linha.estado = 'VAZIO'; linha.motivo = 'devolveu null'; }
        else if (CAMPOS.every((c) => !linha.contagens[c])) { linha.estado = 'VAZIO'; linha.motivo = 'nenhum item'; }
        else {
          const estragados = CAMPOS.flatMap((c) => (r[c] ?? []).filter((x) => !x || (c === 'fatos' && !x.texto) || (c === 'pares' && (!x.pergunta || !x.resposta)) || (c === 'codigos' && !x.codigo))).length;
          if (estragados) { linha.estado = 'FALHOU'; linha.motivo = `${estragados} item(ns) fora do contrato`; }
        }
      } catch (erro) {
        linha.estado = 'FALHOU';
        linha.motivo = String(erro?.message ?? erro).slice(0, 80);
      }
      linha.ms = agora() - inicio;
      linhas.push(linha);
    }
  }
  return linhas;
}

// 1 se algum adaptador quebrou: FALHOU em qualquer consulta, ou VAZIO em todas as suas consultas.
export function codigoDeSaida(linhas) {
  const porAdaptador = new Map();
  for (const l of linhas) porAdaptador.set(l.adaptador, [...(porAdaptador.get(l.adaptador) ?? []), l]);
  for (const ls of porAdaptador.values()) {
    if (ls.some((l) => l.estado === 'FALHOU') || ls.every((l) => l.estado === 'VAZIO')) return 1;
  }
  return 0;
}

export function formatarTabela(linhas) {
  const cab = ['adaptador', 'consulta', 'tempo', 'fatos', 'conc.', 'pares', 'atrib.', 'cód.', 'estado'];
  const corpo = linhas.map((l) => [l.adaptador, l.consulta.length > 42 ? `${l.consulta.slice(0, 41)}…` : l.consulta, `${(l.ms / 1000).toFixed(1)}s`,
    ...CAMPOS.map((c) => String(l.contagens[c])), l.motivo ? `${l.estado}: ${l.motivo}` : l.estado]);
  const largura = cab.map((_, i) => Math.max(...[cab, ...corpo].map((r) => String(r[i]).length)));
  const fmt = (r) => r.map((c, i) => (i >= 2 && i <= 7 ? String(c).padStart(largura[i]) : String(c).padEnd(largura[i]))).join('  ').trimEnd();
  return [fmt(cab), largura.map((n) => '-'.repeat(n)).join('  '), ...corpo.map(fmt)].join('\n');
}

async function principal() {
  const pedidos = process.argv.slice(2);
  const todos = await carregarAdaptadores();
  const desconhecidos = pedidos.filter((p) => !todos.some((a) => a.nome === p));
  if (desconhecidos.length) {
    console.error(`adaptador(es) inexistente(s): ${desconhecidos.join(', ')}. Existem: ${todos.map((a) => a.nome).join(', ')}`);
    process.exit(2);
  }
  const escolhidos = pedidos.length ? todos.filter((a) => pedidos.includes(a.nome)) : todos;
  const linhas = await verificar(escolhidos, criarCtx());
  console.log(formatarTabela(linhas));
  const codigo = codigoDeSaida(linhas);
  console.log(codigo ? '\nHÁ ADAPTADOR QUEBRADO (FALHOU ou VAZIO nas duas consultas).' : '\nTodos os adaptadores responderam.');
  process.exit(codigo);
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) await principal();
