// Aprender sozinho: quando o Apolo não sabe, o serviço `pesquisa` (rota /conhecer) consulta os adaptadores por site
// (Wikipédia, Wikidata, IBGE, MDN, Python, Brasil Escola...) e devolve fatos, conceitos, atributos e pares.
// Aqui se decide o que vale guardar, se guarda na memória com a origem `web`, e se monta a resposta com a fonte.
import { palavrasChave, tituloDoAssunto } from './raciocinio.js';
import { normalizar } from './intencoes.js';

// Fontes abertas ou oficiais: o que elas dizem entra sozinho. As demais só entram se outra fonte concordar.
const CONFIAVEIS = new Set(['wikipedia', 'wikidata', 'ibge', 'mdn', 'pythondocs']);
const LIMITES = { fatos: 6, atributos: 8, conceitos: 8, pares: 2 };
const MAX_FATO = 400;
const MAX_FATO_RESTRITO = 250; // licença "todos os direitos reservados": só frases curtas, sempre com a fonte

const restrito = (item) => /direitos reservados|sem licen[cç]a aberta/i.test(item.licenca ?? '');
const dominio = (url) => { try { return new URL(url).hostname.replace(/^www\./, ''); } catch { return null; } };
// Corta numa palavra inteira e avisa com reticências, em vez de partir "previsões" ao meio.
const cortar = (texto, max) => (texto.length <= max ? texto : `${texto.slice(0, max).replace(/\s+\S*$/, '')}…`);
const maiuscula = (t) => (t ? t[0].toLocaleUpperCase('pt-BR') + t.slice(1) : t);

// Dois textos concordam se compartilham a maior parte das palavras do menor (sem contar enfeites).
export function concordam(a, b) {
  const x = palavrasChave(a), y = palavrasChave(b);
  const menor = Math.min(x.size, y.size);
  if (menor < 3) return false;
  let comuns = 0;
  for (const p of x) if (y.has(p)) comuns++;
  return comuns / menor >= 0.5;
}

// Decide o que guardar. `dados` é a resposta de /conhecer.
export function selecionar(dados) {
  const fatos = [];
  const candidatos = (dados.fatos ?? []).filter((f) => f.texto && f.fonte && f.texto.length <= MAX_FATO && !(restrito(f) && f.texto.length > MAX_FATO_RESTRITO));
  const confianca = { alta: 0, media: 1, baixa: 2 };
  const ordenados = [...candidatos].sort((a, b) => (confianca[a.confianca] ?? 1) - (confianca[b.confianca] ?? 1)
    || (CONFIAVEIS.has(b.adaptador) ? 1 : 0) - (CONFIAVEIS.has(a.adaptador) ? 1 : 0));
  for (const f of ordenados) {
    if (fatos.length >= LIMITES.fatos) break;
    if (fatos.some((g) => concordam(g.texto, f.texto))) continue; // mesma ideia de outra fonte: não repete
    const confirmado = candidatos.some((o) => o.adaptador !== f.adaptador && concordam(o.texto, f.texto));
    if (CONFIAVEIS.has(f.adaptador) || confirmado) fatos.push({ ...f, confirmado });
  }

  // Atributos (capital, população...): de fonte confiável, curtos e com nome e valor úteis.
  const atributos = [];
  const vistos = new Set();
  for (const a of dados.atributos ?? []) {
    if (atributos.length >= LIMITES.atributos) break;
    if (!a.nome || !a.valor || a.valor.length > 120 || !CONFIAVEIS.has(a.adaptador)) continue;
    const chave = normalizar(`${a.nome} ${a.valor}`);
    if (vistos.has(chave)) continue;
    vistos.add(chave);
    atributos.push(a);
  }

  const pares = (dados.pares ?? []).filter((p) => p.pergunta && p.resposta && p.resposta.length >= 8 && p.resposta.length <= MAX_FATO
    && !(restrito(p) && p.resposta.length > MAX_FATO_RESTRITO)).slice(0, LIMITES.pares);

  const tema = normalizar(dados.tema ?? '');
  const conceitos = (dados.conceitos ?? [])
    .filter((c) => c.nome && c.nome.length >= 2 && c.nome.length <= 50 && normalizar(c.nome) !== tema)
    .sort((a, b) => (b.peso ?? 0) - (a.peso ?? 0)).slice(0, LIMITES.conceitos);

  const fontes = [...new Set([...fatos, ...atributos, ...pares].map((i) => dominio(i.fonte)).filter(Boolean))].slice(0, 3);
  return { fatos, atributos, pares, conceitos, fontes, tema };
}

// O que vai para a memória, no formato que `abrirFato` entende: "Título :: frase (fonte: url)".
export function paraMemoria(selecao, titulo) {
  const fato = (f) => ({ tipo: 'fato', origem: 'web', conteudo: `${titulo} :: ${f.texto} (fonte: ${f.fonte})` });
  return {
    fatos: selecao.fatos.map(fato),
    atributos: selecao.atributos.map((a) => ({ tipo: 'fato', origem: 'web', conteudo: `${titulo} :: ${a.nome}: ${a.valor} (fonte: ${a.fonte})` })),
    pares: selecao.pares.map((p) => ({ tipo: 'fato', origem: 'web', conteudo: `${p.pergunta} :: ${p.resposta} (fonte: ${p.fonte})` })),
    conceitos: selecao.conceitos.map((c) => ({ tipo: 'conceito', origem: 'web', conteudo: `${c.nome} (relacionado a ${titulo})`, peso: c.peso ?? 0.5 })),
  };
}

// Resposta curta: os atributos que a pergunta pediu ("capital", "população"...) e a(s) melhor(es) frase(s).
export function montarResposta(mensagem, selecao) {
  // Palavras do próprio assunto não contam como pedido: "Fotossíntese oxigênica" não foi pedida só por citar "fotossíntese".
  const doTema = palavrasChave(selecao.tema ?? '');
  const pedidas = new Set([...palavrasChave(mensagem)].filter((p) => !doTema.has(p)));
  const pediu = (a) => [...palavrasChave(a.nome)].some((p) => pedidas.has(p));
  const dosPedidos = selecao.atributos.filter(pediu);
  // Dados exatos só vêm na frente se a pergunta os pediu ("a capital", "a população"); numa definição, a definição vem primeiro.
  const atributos = dosPedidos.length ? dosPedidos.slice(0, 3) : [];
  const partes = [];
  if (atributos.length) partes.push(`${atributos.map((a) => `${a.nome}: ${a.valor}`).join('; ')}.`);
  // Quando a pergunta pediu um dado exato, uma frase de contexto basta; senão, duas.
  for (const f of selecao.fatos.slice(0, dosPedidos.length ? 1 : 2)) partes.push(f.texto);
  if (!partes.length) return null;
  return `${cortar(partes.join(' '), 600)} (fontes: ${selecao.fontes.join(', ')}; pesquisei na internet agora)`;
}

// Comandos para apagar o que foi aprendido: "esqueça isso" (a última pesquisa) ou "esqueça o que aprendeu sobre X".
export function reconhecerEsquecer(mensagem) {
  const t = normalizar(mensagem); // já sem acento nem cedilha: "esqueça" vira "esqueca"
  if (/^esqueca (isso|essa pesquisa|o que (voce )?(acabou de )?(aprendeu|aprender))$/.test(t)) return { tipo: 'ultimo' };
  const tema = t.match(/^esqueca (?:tudo |o que (?:voce )?(?:aprendeu|sabe) )?sobre (.{2,80})$/)?.[1];
  return tema ? { tipo: 'tema', tema } : null;
}

export function criarConhecedor({ url = process.env.PESQUISA_URL, fetchFn = fetch } = {}) {
  if (!url) return null;
  return async function conhecer(consulta) {
    try {
      const resposta = await fetchFn(new URL('/conhecer', url), {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ consulta }), signal: AbortSignal.timeout(120_000),
      });
      if (!resposta.ok) throw new Error(`conhecer respondeu ${resposta.status}`);
      return await resposta.json();
    } catch (erro) {
      console.warn(`conhecer indisponível: ${erro.message}`);
      return null;
    }
  };
}

// `conhecer`: o cliente acima (ou null). `lembrar`: apolo.lembrar. `repo`: buscarConteudo, salvarSinapses, apagarNeuronios, apagarWebPorTema.
export function criarAprendizado({ conhecer, lembrar, repo, registrar = () => {}, habilitado = true }) {
  let ocupado = false;
  let ultimos = [];
  const ativo = Boolean(conhecer) && habilitado;

  async function guardar(item) {
    const existente = await repo.buscarConteudo(item.conteudo);
    if (existente) return { id: existente.id, novo: false };
    const neuronio = await lembrar({ conteudo: item.conteudo, tipo: item.tipo, origem: item.origem });
    return { id: neuronio.id, novo: true };
  }

  return {
    ativo,

    // Devolve a resposta (texto) ou null se não achou nada em que confiar.
    async aprender(mensagem) {
      if (!ativo) return null;
      if (ocupado) return 'Estou pesquisando outra coisa agora. Pergunte de novo em instantes.';
      ocupado = true;
      try {
        const dados = await conhecer(mensagem);
        if (!dados) return null;
        const selecao = selecionar(dados);
        const titulo = maiuscula(tituloDoAssunto(dados.metadados?.titulo ?? '') || dados.tema || '');
        const memoria = paraMemoria(selecao, titulo || 'Assunto');
        const resposta = montarResposta(mensagem, selecao);
        if (!resposta) { registrar('conheceu', { texto: mensagem, achou: 0, adaptadores: dados.adaptadores ?? [] }); return null; }

        const ids = [];
        let novos = 0;
        const principal = [];
        for (const item of [...memoria.fatos, ...memoria.atributos, ...memoria.pares]) {
          const r = await guardar(item);
          ids.push(r.id);
          if (r.novo) novos++;
          principal.push(r.id);
        }
        const sinapses = [];
        for (const c of memoria.conceitos) {
          const r = await guardar(c);
          ids.push(r.id);
          if (r.novo) novos++;
          // O conceito se liga ao fato principal: assim, lembrar do assunto traz os temas relacionados.
          if (principal[0] && r.id !== principal[0]) {
            sinapses.push({ de: Math.min(r.id, principal[0]), para: Math.max(r.id, principal[0]), peso: Math.min(0.6, (c.peso ?? 0.5) * 0.6) });
          }
        }
        await repo.salvarSinapses(sinapses);
        ultimos = ids;
        registrar('conheceu', {
          texto: mensagem, tema: dados.tema, adaptadores: [...new Set(dados.adaptadores ?? [])], fontes: selecao.fontes,
          fatos: selecao.fatos.length, atributos: selecao.atributos.length, conceitos: selecao.conceitos.length, novos,
        });
        return resposta;
      } finally {
        ocupado = false;
      }
    },

    // Só apaga o que veio da web: o que você ensinou à mão nunca é tocado por estes comandos.
    async esquecer(pedido) {
      const apagados = pedido.tipo === 'ultimo' ? await repo.apagarNeuronios(ultimos) : await repo.apagarWebPorTema(pedido.tema);
      if (pedido.tipo === 'ultimo') ultimos = [];
      registrar('esqueceu', { texto: pedido.tipo === 'ultimo' ? 'a última pesquisa' : pedido.tema, quantidade: apagados });
      return apagados;
    },
  };
}
