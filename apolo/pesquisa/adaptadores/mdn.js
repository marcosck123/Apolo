// MDN Web Docs: referência de JavaScript, HTML, CSS e APIs da web.
// Fluxo: a busca interna (/api/v1/search) escolhe a página; depois lemos o HTML renderizado no servidor (SSR).
// Até 4 requisições por consulta: busca pt-BR + página; se não houver em português, busca en-US + página.
// Licença (confirmada em developer.mozilla.org/en-US/docs/MDN/Writing_guidelines/Attrib_copyright_license):
// texto sob CC BY-SA 2.5 ou posterior; exemplos de código sob CC0 (domínio público) desde 20/08/2010.
import { atributo, CONFIANCA, fato, limparTexto, pareceFrase } from './contrato.js';

const ORIGEM = 'https://developer.mozilla.org';
const PALAVRAS_VAZIAS = new Set(['como', 'usar', 'uso', 'em', 'no', 'na', 'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'do', 'da', 'para', 'por', 'com', 'que', 'e', 'qual', 'quais', 'funciona', 'fazer', 'exemplo', 'exemplos', 'metodo', 'funcao', 'the', 'in', 'to', 'of', 'how', 'use']);
const LINGUAGEM_SEM_CODIGO = new Set(['plain', 'plaintext', 'text', 'output', 'txt', 'none']);

const semAcento = (t) => String(t ?? '').toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '');
const tokens = (t) => semAcento(t).split(/[^a-z0-9]+/).filter(Boolean);

// "como usar array map em JavaScript" → ["array", "map"]
export function termosDeBusca(tema) {
  const todos = tokens(tema);
  const uteis = todos.filter((t) => !PALAVRAS_VAZIAS.has(t));
  const semLinguagem = uteis.filter((t) => t !== 'javascript' && t !== 'js');
  return (semLinguagem.length ? semLinguagem : uteis).slice(0, 5);
}

// Nota de 0..1: que fração dos termos aparece, como palavra inteira, no título ou no caminho da página.
function afinidade(doc, termos) {
  const alvo = new Set([...tokens(doc.title), ...tokens(String(doc.slug ?? doc.mdn_url ?? '').replace(/^\/?[a-z-]+\/docs\//i, ''))]);
  return termos.filter((t) => alvo.has(t)).length / termos.length;
}

function escolher(documentos, termos) {
  let melhor = null;
  let notaMelhor = 0;
  for (const doc of documentos ?? []) {
    if (!doc?.mdn_url) continue;
    const nota = afinidade(doc, termos);
    if (nota > notaMelhor) { melhor = doc; notaMelhor = nota; } // empate: fica o primeiro (maior score da busca)
  }
  return notaMelhor >= 0.75 ? melhor : null;
}

async function buscarPagina(ctx, locale, termos) {
  const r = await ctx.buscar(`${ORIGEM}/api/v1/search?q=${encodeURIComponent(termos.join(' '))}&locale=${locale}`, { json: true });
  if (!r.ok) return null;
  return escolher(r.json()?.documents, termos);
}

const identificador = (secao) => semAcento(secao.getAttribute?.('aria-labelledby') ?? '');
const ehSintaxe = (id) => /^(sintaxe|syntax)$/.test(id);
const ehParametros = (id) => /^(parametros|parameters)$/.test(id);
const ehRetorno = (id) => /^(valor_de_retorno|return_value)$/.test(id);
const ehExemplos = (id) => /^(exemplos?|examples?)$/.test(id);
const ehRodape = (id) => /^(especificacoes|specifications|compatibilidade|browser_compat|veja_tambem|see_also|feedback)/.test(id);

function linguagemDoBloco(pre, url) {
  const rotulo = limparTexto(pre.parentElement?.querySelector?.('.language-name')?.textContent).toLowerCase();
  const brush = String(pre.getAttribute('class') ?? '').match(/brush:\s*([\w+-]+)/)?.[1]?.toLowerCase();
  const lang = rotulo || brush;
  if (lang) return lang;
  if (/\/Web\/JavaScript\//.test(url)) return 'js';
  if (/\/Web\/CSS\//.test(url)) return 'css';
  if (/\/Web\/(HTML|SVG|MathML)\//.test(url)) return 'html';
  return 'texto';
}

// O parágrafo que apresenta o bloco; se não houver, o título da seção.
function explicacaoDoBloco(pre, secao) {
  let no = pre.closest('.code-example') ?? pre;
  for (let irmao = no.previousElementSibling; irmao; irmao = irmao.previousElementSibling) {
    if (irmao.tagName === 'P') {
      const t = limparTexto(irmao.textContent);
      if (t.length >= 15) return t.length > 300 ? `${t.slice(0, 297).trim()}...` : t;
    }
  }
  return limparTexto(secao.querySelector('h2, h3')?.textContent);
}

function textoDe(el, max = 220) {
  const t = limparTexto(el?.textContent);
  return t.length > max ? `${t.slice(0, max - 3).trim()}...` : t;
}

export default {
  nome: 'mdn',
  licenca: 'CC BY-SA 2.5 (exemplos de código CC0)',
  tipos: ['codigo', 'definicao'],
  dominios: ['developer.mozilla.org'],

  async extrair({ tema, url }, ctx) {
    let alvo = null; // { caminho, locale }
    if (url && /(^|\.)developer\.mozilla\.org$/i.test(new URL(url).hostname)) {
      const caminho = new URL(url).pathname;
      alvo = { caminho, locale: caminho.split('/')[1] ?? 'pt-BR' };
    } else {
      const termos = termosDeBusca(tema);
      if (!termos.length) return null;
      let doc = await buscarPagina(ctx, 'pt-BR', termos);
      if (!doc) doc = await buscarPagina(ctx, 'en-US', termos);
      if (!doc) return null;
      alvo = { caminho: doc.mdn_url, locale: doc.mdn_url.split('/')[1] };
    }

    let pagina = await ctx.buscar(ORIGEM + alvo.caminho);
    if (!pagina.ok && alvo.locale !== 'en-US') {
      alvo = { caminho: alvo.caminho.replace(/^\/[^/]+/, '/en-US'), locale: 'en-US' };
      pagina = await ctx.buscar(ORIGEM + alvo.caminho);
    }
    if (!pagina.ok) return null;

    const fonte = ORIGEM + alvo.caminho;
    const doc = ctx.parsear(pagina.texto);
    const principal = doc.querySelector('main') ?? doc;
    const titulo = limparTexto(principal.querySelector('h1')?.textContent) || limparTexto(doc.querySelector('title')?.textContent).replace(/\s*\|\s*MDN$/, '');
    const emIngles = alvo.locale.toLowerCase() === 'en-us';
    const aviso = emIngles ? ' (em inglês)' : '';
    const resultado = { fatos: [], conceitos: [], codigos: [], atributos: [], pares: [], metadados: {} };

    // (a) descrição
    const meta = limparTexto(doc.querySelector('meta[name="description"]')?.getAttribute('content'));
    const secoes = [...principal.querySelectorAll('section.content-section')];
    let resumo = meta;
    if (!pareceFrase(resumo)) {
      const sResumo = secoes.find((s) => /^(resumo|sumario|summary)$/.test(identificador(s))) ?? secoes[0];
      resumo = limparTexto(sResumo?.querySelector('p')?.textContent);
    }
    if (pareceFrase(resumo)) resultado.fatos.push(fato(this, { texto: resumo, secao: `Resumo${aviso}`, fonte, confianca: CONFIANCA.alta }));

    // restante: percorre as seções uma vez
    let nosExemplos = false;
    for (const secao of secoes) {
      const id = identificador(secao);
      if (ehRodape(id)) { nosExemplos = false; continue; }
      const nivel2 = secao.querySelector('h2');
      if (nivel2) nosExemplos = ehExemplos(id);

      if (/^(descricao|description)$/.test(id)) {
        const p = limparTexto(secao.querySelector('p')?.textContent);
        if (pareceFrase(p) && p !== resumo) resultado.fatos.push(fato(this, { texto: p, secao: `Descrição${aviso}`, fonte, confianca: CONFIANCA.media }));
      }
      if (ehSintaxe(id)) {
        const linhas = limparTexto((secao.querySelector('pre')?.textContent ?? '').split('\n').filter((l) => l.trim()).slice(0, 4).join(' ; '));
        if (linhas) resultado.atributos.push(atributo(this, { nome: 'Sintaxe', valor: linhas.slice(0, 300), fonte }));
      }
      if (ehParametros(id)) {
        const lista = secao.querySelector('dl');
        const itens = [...(lista?.children ?? [])].filter((e) => e.tagName === 'DT').slice(0, 4).map((dt) => `${limparTexto(dt.textContent)}: ${textoDe(dt.nextElementSibling?.querySelector('p') ?? dt.nextElementSibling, 140)}`);
        if (itens.length) resultado.atributos.push(atributo(this, { nome: 'Parâmetros', valor: itens.join(' | '), fonte }));
      }
      if (ehRetorno(id)) {
        const t = textoDe(secao.querySelector('p'), 240);
        if (t) resultado.atributos.push(atributo(this, { nome: 'Valor de retorno', valor: t, fonte }));
      }

      // (b) códigos: a Sintaxe e as seções de Exemplos; sem blocos de saída, sem tabelas e sem o exemplo interativo
      if (ehSintaxe(id) || nosExemplos) {
        for (const pre of secao.querySelectorAll('pre')) {
          if (resultado.codigos.length >= 8) break;
          if (pre.closest('table') || /interactive-example/.test(pre.getAttribute('class') ?? '')) continue;
          const linguagem = linguagemDoBloco(pre, alvo.caminho);
          const codigo = String(pre.textContent ?? '').replace(/\s+$/, '').replace(/^\n+/, '');
          if (LINGUAGEM_SEM_CODIGO.has(linguagem) || codigo.length < 8 || codigo.length > 1800) continue;
          resultado.codigos.push({ linguagem, codigo, explicacao: ehSintaxe(id) ? `Sintaxe${aviso}` : explicacaoDoBloco(pre, secao), fonte });
        }
      }
    }

    // (d) conceitos: links internos do corpo, em ordem de aparição, sem a própria página
    const vistos = new Set([alvo.caminho.toLowerCase()]);
    for (const secao of secoes) {
      if (/^(feedback|especificacoes|specifications)$/.test(identificador(secao))) continue;
      for (const a of secao.querySelectorAll('a[href^="/"]')) {
        const href = (a.getAttribute('href') ?? '').split('#')[0];
        const nome = limparTexto(a.querySelector('code')?.textContent) || limparTexto(a.textContent); // prefere o nome da API, não a frase do link
        if (!/^\/[a-z]{2}(-[A-Za-z]{2})?\/docs\//.test(href) || vistos.has(href.toLowerCase()) || nome.length < 2 || nome.length > 50 || nome.split(' ').length > 4 || /contributors|MDN\/(Community|Writing)/.test(href)) continue;
        vistos.add(href.toLowerCase());
        if (resultado.conceitos.length < 12) resultado.conceitos.push({ nome, url: ORIGEM + href, peso: Number(Math.max(0.3, 1 - resultado.conceitos.length * 0.06).toFixed(2)) });
      }
    }

    // (e) metadados
    const data = doc.querySelector('.article-footer__last-modified time')?.getAttribute('datetime') ?? doc.querySelector('time')?.getAttribute('datetime');
    resultado.metadados = { titulo, idioma: alvo.locale, ...(data ? { data } : {}), url: fonte };

    if (!resultado.fatos.length && !resultado.codigos.length) return null;
    return resultado;
  },
};
