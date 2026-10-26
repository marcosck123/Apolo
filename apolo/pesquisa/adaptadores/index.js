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

// Quem recebe cada URL achada pela busca: o adaptador do domínio e, se ninguém o tem, o genérico (no máximo 2).
// Sites sem busca própria permitida (Brasil Escola, Mundo Educação) só funcionam assim.
const hospedeiro = (url) => { try { return new URL(url).hostname; } catch { return null; } };
export function distribuirUrls(urls, todos, { maxUrls = 4, maxGenericos = 2 } = {}) {
  const generico = todos.find((a) => Array.isArray(a.dominios) && a.dominios.length === 0);
  const tarefas = [];
  let genericos = 0;
  for (const url of urls.slice(0, maxUrls * 2)) {
    const host = hospedeiro(url);
    if (!host || tarefas.length >= maxUrls) continue;
    const dono = todos.find((a) => a.dominios?.some((d) => host === d || host.endsWith(`.${d}`)));
    if (dono) tarefas.push({ adaptador: dono, url });
    else if (generico && genericos < maxGenericos) { genericos++; tarefas.push({ adaptador: generico, url }); }
  }
  return tarefas;
}

// Uma página trazida pela busca só vale se falar do tema: o título ou algum fato tem de mencionar uma palavra dele.
// (A busca devolve de tudo: já veio a ajuda do YouTube para "o que é astrologia".)
const semAcento = (t) => String(t ?? '').toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '');
const raizDe = (p) => (p.length > 5 && p.endsWith('s') ? p.slice(0, -1) : p);
export function falaDoTema(resultado, tema) {
  const palavras = semAcento(tema).split(/[^a-z0-9]+/).filter((p) => p.length >= 4).map(raizDe);
  if (!palavras.length) return true;
  const texto = semAcento([resultado.metadados?.titulo, ...(resultado.fatos ?? []).map((f) => f.texto), ...(resultado.conceitos ?? []).map((c) => c.nome)].join(' '));
  return palavras.some((p) => texto.includes(p));
}

// `adaptadores` e `tipoForcado` existem para teste. `urls` são páginas já achadas por uma busca.
export async function conhecer(consulta, ctx, { adaptadores = null, tempoMs = 25_000, tipoForcado = null, urls = [] } = {}) {
  const { tipo, tema } = tipoForcado ? { tipo: tipoForcado, tema: consulta } : classificar(consulta);
  const todos = adaptadores ?? await carregarAdaptadores();
  const escolhidos = todos.filter((a) => a.tipos?.includes(tipo) || a.tipos?.includes('geral'));
  const tarefas = [
    ...escolhidos.map((a) => ({ adaptador: a, entrada: { consulta, tema, tipo } })),
    ...distribuirUrls(urls, todos).map(({ adaptador, url }) => ({ adaptador, entrada: { consulta, tema, tipo, url } })),
  ];
  const falhas = [];
  const resultados = await Promise.all(tarefas.map(async ({ adaptador: a, entrada }) => {
    try {
      const r = await comTempo(a.extrair(entrada, ctx), tempoMs, a.nome);
      if (!r) return null;
      // Só as páginas achadas pela busca precisam passar pelo filtro; o adaptador que busca pelo tema já a fez sozinho.
      if (entrada.url && !falaDoTema(r, tema)) {
        falhas.push({ adaptador: a.nome, erro: `página sem relação com "${tema}": ${entrada.url}` });
        return null;
      }
      return { ...completar(r), _adaptador: a.nome };
    } catch (erro) {
      falhas.push({ adaptador: a.nome, erro: String(erro.message ?? erro) });
      ctx.registrar?.(`adaptador ${a.nome} falhou: ${erro.message}`);
      return null;
    }
  }));
  const bons = resultados.filter(Boolean);
  return { tipo, tema, ...juntar(bons), adaptadores: bons.map((r) => r._adaptador), falhas };
}
