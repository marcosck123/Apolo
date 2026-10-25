// Roteador: escolhe os adaptadores pelo tipo da pergunta, roda em paralelo com tempo limite,
// junta e deduplica o que voltou. Um adaptador que falha não derruba os outros.
// Os adaptadores são os arquivos desta pasta (menos os reservados): para acrescentar uma fonte, basta criar o arquivo.
import { readdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { completar } from './contrato.js';
import { classificar } from './tipo.js';

const RESERVADOS = new Set(['contrato.js', 'tipo.js', 'ctx.js', 'index.js']);
const PASTA = fileURLToPath(new URL('.', import.meta.url));

let carregados = null;
export async function carregarAdaptadores() {
  if (carregados) return carregados;
  const lista = [];
  for (const arquivo of (await readdir(PASTA)).filter((a) => a.endsWith('.js') && !RESERVADOS.has(a)).sort()) {
    try {
      const { default: adaptador } = await import(`./${arquivo}`);
      if (adaptador?.nome && typeof adaptador.extrair === 'function') lista.push(adaptador);
    } catch (erro) {
      console.warn(`adaptador ${arquivo} não carregou: ${erro.message}`);
    }
  }
  carregados = lista;
  return lista;
}

const comTempo = (promessa, ms, nome) => {
  let temporizador;
  const limite = new Promise((_, rej) => { temporizador = setTimeout(() => rej(new Error(`${nome}: passou de ${ms} ms`)), ms); });
  return Promise.race([promessa, limite]).finally(() => clearTimeout(temporizador));
};

// Junta resultados de vários adaptadores, sem repetir a mesma frase/par/atributo.
export function juntar(resultados) {
  const saida = completar({});
  const vistos = { fatos: new Set(), conceitos: new Set(), pares: new Set(), codigos: new Set(), atributos: new Set() };
  const chave = { fatos: (x) => x.texto.toLowerCase(), conceitos: (x) => x.nome.toLowerCase(), pares: (x) => x.pergunta.toLowerCase(), codigos: (x) => x.codigo, atributos: (x) => `${x.nome}=${x.valor}`.toLowerCase() };
  for (const r of resultados) {
    for (const campo of Object.keys(chave)) {
      for (const item of r[campo] ?? []) {
        const k = chave[campo](item);
        if (!k || vistos[campo].has(k)) continue;
        vistos[campo].add(k);
        saida[campo].push(item);
      }
    }
    saida.metadados = { ...r.metadados, ...saida.metadados };
  }
  return saida;
}

// `adaptadores` e `tipoForcado` existem para teste.
export async function conhecer(consulta, ctx, { adaptadores = null, tempoMs = 25_000, tipoForcado = null } = {}) {
  const { tipo, tema } = tipoForcado ? { tipo: tipoForcado, tema: consulta } : classificar(consulta);
  const todos = adaptadores ?? await carregarAdaptadores();
  const escolhidos = todos.filter((a) => a.tipos?.includes(tipo) || a.tipos?.includes('geral'));
  const falhas = [];
  const resultados = await Promise.all(escolhidos.map(async (a) => {
    try {
      const r = await comTempo(a.extrair({ consulta, tema, tipo }, ctx), tempoMs, a.nome);
      return r ? { ...completar(r), _adaptador: a.nome } : null;
    } catch (erro) {
      falhas.push({ adaptador: a.nome, erro: String(erro.message ?? erro) });
      ctx.registrar?.(`adaptador ${a.nome} falhou: ${erro.message}`);
      return null;
    }
  }));
  const bons = resultados.filter(Boolean);
  return { tipo, tema, ...juntar(bons), adaptadores: bons.map((r) => r._adaptador), falhas };
}
