// Extrator genérico: lê QUALQUER página pública quando nenhum adaptador específico cobre a URL.
//
// Como ele recebe a página: só age quando há uma URL, em `url` ou como endereço dentro da `consulta`.
// Procurar páginas por conta própria exigiria um buscador, e os que funcionam sem navegador (DuckDuckGo HTML, Bing,
// Google) bloqueiam robôs com desafio de verificação ou proíbem isso nos termos; não há API de busca aberta e estável.
// Sem URL, devolve null. O tipo 'geral' faz o roteador incluí-lo sempre, mas sem URL ele não custa nenhuma requisição.
//
// Educação com o site: no máximo 2 requisições por chamada (robots.txt + a página), sem seguir links, e
// o que o robots.txt proíbe para o ApoloBot (ou para '*') não é lido.
//
// Segurança: tudo que vem da página é DADO. Texto invisível (hidden, aria-hidden, display:none, fonte zero,
// fora da tela...) é removido antes da extração, e frases que parecem ordens a uma IA são descartadas.
// O adaptador só monta fatos; nunca interpreta nada do que leu.
import { atributo, CONFIANCA, fato, limparTexto, par, pareceFrase, resultadoVazio } from './contrato.js';

const MAX_SECOES = 12;
const LIMITES = { fatos: 25, conceitos: 15, pares: 10, codigos: 10, atributos: 25 };
const MAX_HTML = 2_000_000;

const adaptador = {
  nome: 'generico',
  licenca: 'verificar na fonte (texto de terceiros; citar o link)',
  tipos: ['geral'],
  dominios: [], // vazio: serve a qualquer domínio, desde que alguém entregue a URL
  async extrair({ consulta, url }, ctx) {
    const alvo = urlDaEntrada(url, consulta);
    if (!alvo) return null;
    if (!(await robotsPermite(alvo, ctx))) {
      ctx.registrar?.(`generico: robots.txt proíbe ${alvo}`);
      return null;
    }
    const resposta = await ctx.buscar(alvo);
    if (!resposta?.ok && resposta?.status !== 200) return null;
    return extrairDaPagina(String(resposta.texto ?? '').slice(0, MAX_HTML), resposta.url || alvo, ctx, adaptador);
  },
};
export default adaptador;

// ---------------------------------------------------------------------------------------------------------------
// URL de entrada e robots.txt

export function urlDaEntrada(url, consulta) {
  for (const candidato of [url, String(consulta ?? '').match(/https?:\/\/[^\s<>"')]+/i)?.[0]]) {
    if (!candidato) continue;
    try {
      const u = new URL(candidato);
      if (u.protocol === 'http:' || u.protocol === 'https:') return u.href;
    } catch { /* tenta o próximo */ }
  }
  return null;
}

// Interpreta um robots.txt: vale o grupo do ApoloBot, se existir, senão o do '*'. Regra mais longa vence; Allow empata a favor.
export function robotsPermiteTexto(texto, caminho, agente = 'apolobot') {
  const grupos = [];
  let atual = null;
  let lendoAgentes = false;
  for (const bruta of String(texto ?? '').split(/\r?\n/)) {
    const linha = bruta.replace(/#.*$/, '').trim();
    const m = linha.match(/^([a-z-]+)\s*:\s*(.*)$/i);
    if (!m) continue;
    const campo = m[1].toLowerCase();
    if (campo === 'user-agent') {
      if (!lendoAgentes) { atual = { agentes: [], regras: [] }; grupos.push(atual); }
      atual.agentes.push(m[2].trim().toLowerCase());
      lendoAgentes = true;
    } else if ((campo === 'allow' || campo === 'disallow') && atual) {
      lendoAgentes = false;
      if (m[2].trim()) atual.regras.push({ permite: campo === 'allow', padrao: m[2].trim() });
    } else {
      lendoAgentes = false;
    }
  }
  const grupo = grupos.find((g) => g.agentes.some((a) => a !== '*' && agente.includes(a))) ?? grupos.find((g) => g.agentes.includes('*'));
  if (!grupo) return true;
  let melhor = null;
  for (const regra of grupo.regras) {
    const re = new RegExp(`^${regra.padrao.replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*').replace(/\\\$$/, '$')}`);
    if (!re.test(caminho)) continue;
    if (!melhor || regra.padrao.length > melhor.padrao.length || (regra.padrao.length === melhor.padrao.length && regra.permite)) melhor = regra;
  }
  return melhor ? melhor.permite : true;
}

async function robotsPermite(alvo, ctx) {
  const u = new URL(alvo);
  try {
    const r = await ctx.buscar(`${u.origin}/robots.txt`);
    if (r?.status !== 200) return true;
    return robotsPermiteTexto(r.texto, u.pathname + u.search);
  } catch {
    return true; // sem robots.txt acessível, vale a regra geral de educação
  }
}

// ---------------------------------------------------------------------------------------------------------------
// Texto: frases, filtros de ruído e de instruções escondidas

const RUIDO = /(cookies?|aceitar|aceito|assine|newsletter|todos os direitos|direitos reservados|copyright|javascript|seu navegador|publicidade|an[uú]ncio|leia (também|mais)|veja (também|mais)|compartilh|siga[- ]nos|pol[ií]tica de privacidade|termos de uso|traduzid[oa]|tradu[cç][aã]o|translat|this (article|page) (is|was)|clique aqui|inscreva-se|fa[cç]a login)/i;
// Frases que parecem ordens a uma IA: pode ser texto escondido com instruções. Descartadas, nunca obedecidas.
const INSTRUCAO = /(ignore (all |tudo |todas |as |the )?(previous|prior|anteriores|above|instru)|ignore (as|suas|as suas) instru|disregard|desconsidere (as|todas)|system prompt|prompt do sistema|you are (now |an? )?(ai|assistant|chatgpt|claude)|voc[eê] (agora )?[eé] (um|uma) (ia|assistente)|responda (apenas|somente|sempre) com|as an ai|aja como|act as (a|an)|novas instru[cç][oõ]es|<\/?(system|assistant|instruction))/i;

const ABREVIACOES = /(?:^|\s)(?:dr|dra|sr|sra|prof|profa|etc|ex|av|ltda|vs|fig|cap|art|nº|no|st|mr|mrs|ms|p|pág|págs|aprox|obs|esp|tel|[A-ZÀ-Ú])$/i;

export function frases(texto) {
  const t = limparTexto(texto);
  const saida = [];
  let inicio = 0;
  for (const m of t.matchAll(/[.!?…]+["”')\]]*\s+(?=["“(]?[A-ZÀ-Ú0-9])/g)) {
    const fim = m.index + m[0].trimEnd().length;
    const trecho = t.slice(inicio, fim);
    if (/\.\s*$/.test(trecho) && ABREVIACOES.test(trecho.replace(/\.\s*$/, ''))) continue;
    saida.push(trecho.trim());
    inicio = m.index + m[0].length;
  }
  const resto = t.slice(inicio).trim();
  if (resto) saida.push(resto);
  return saida;
}

// Rótulos soltos ('Lançamentos mensais consecutivos') passam em pareceFrase; exigimos ao menos 5 palavras.
const boaFrase = (t) => pareceFrase(t) && t.trim().split(/\s+/).length >= 5 && !RUIDO.test(t) && !INSTRUCAO.test(t);

// Primeiras frases boas até ~max caracteres (ao menos uma).
function resumo(texto, max = 320) {
  const boas = [];
  let total = 0;
  for (const f of frases(texto)) {
    if (!boaFrase(f)) { if (boas.length) break; continue; }
    if (boas.length && total + f.length > max) break;
    boas.push(f);
    total += f.length + 1;
    if (total >= max * 0.6) break;
  }
  return boas.join(' ');
}

const normaliza = (t) => limparTexto(t).toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replace(/[^a-z0-9]+/g, ' ').trim();
const texto = (el) => limparTexto(el?.textContent ?? '');

// ---------------------------------------------------------------------------------------------------------------
// Limpeza do DOM

const TAGS_FORA = 'script, style, nav, header, footer, aside, form, noscript, iframe, template, svg, button, select, textarea, dialog, canvas, object, embed, link, meta';
const ESCONDIDO_ESTILO = /display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0(?![.\d])|opacity\s*:\s*0(?![.\d])|(?:left|top|right|text-indent)\s*:\s*-\d{3,}|color\s*:\s*transparent|(?:width|height)\s*:\s*0(?:px)?\s*(?:;|$)|clip\s*:\s*rect\(\s*0/i;
const CLASSES_ESCONDIDAS = new Set(['sr-only', 'visually-hidden', 'visuallyhidden', 'screen-reader-text', 'hidden', 'd-none', 'is-hidden', 'u-hidden', 'invisible']);
const FICHAS_RUIM = new Set(['cookie', 'cookies', 'consent', 'gdpr', 'lgpd', 'banner', 'advert', 'advertisement', 'ads', 'adsbygoogle', 'sponsor', 'sponsored', 'publicidade', 'promo', 'newsletter', 'popup', 'modal', 'menu', 'navbar', 'nav', 'navigation', 'breadcrumb', 'breadcrumbs', 'share', 'sharing', 'social', 'comments', 'comment', 'related', 'sidebar', 'widget', 'subscribe', 'toolbar', 'skip']);

function escondido(el) {
  if (el.hasAttribute('hidden') || el.getAttribute('aria-hidden') === 'true') return true;
  if (el.tagName === 'INPUT' && /hidden/i.test(el.getAttribute('type') ?? '')) return true;
  if (ESCONDIDO_ESTILO.test(el.getAttribute('style') ?? '')) return true;
  return (el.getAttribute('class') ?? '').toLowerCase().split(/\s+/).some((c) => CLASSES_ESCONDIDAS.has(c));
}

function limpar(doc) {
  for (const el of [...doc.querySelectorAll(TAGS_FORA)]) el.remove();
  for (const el of [...doc.querySelectorAll('body *')]) {
    if (!el.parentNode) continue; // já saiu junto com um ancestral
    if (escondido(el)) { el.remove(); continue; }
    if (['MAIN', 'ARTICLE', 'BODY', 'HTML'].includes(el.tagName)) continue;
    const fichas = `${el.getAttribute('class') ?? ''} ${el.getAttribute('id') ?? ''} ${el.getAttribute('role') ?? ''}`.toLowerCase().split(/[^a-z0-9]+/);
    const role = el.getAttribute('role');
    const ruim = fichas.some((f) => FICHAS_RUIM.has(f)) || role === 'navigation' || role === 'banner' || role === 'contentinfo' || role === 'dialog' || role === 'complementary';
    // Um invólucro grande com classe "has-sidebar" não pode levar o artigo junto.
    if (ruim && !el.querySelector('h1, article, main') && texto(el).length < 3000) el.remove();
  }
}

// ---------------------------------------------------------------------------------------------------------------
// Área principal

const SELETORES_PRINCIPAIS = 'article, main, [role="main"], [itemprop="articleBody"], .post-content, .entry-content, .article-body, .article-content, .post-body, #content, #main, #conteudo';

function areaPrincipal(doc) {
  const candidatos = [...doc.querySelectorAll(SELETORES_PRINCIPAIS)];
  let melhor = null;
  let melhorTam = 0;
  for (const c of candidatos) {
    const tam = texto(c).length;
    if (tam > melhorTam) { melhor = c; melhorTam = tam; }
  }
  if (melhor && melhorTam >= 400) return melhor;
  // Densidade de texto: cada parágrafo longo dá pontos ao pai e (metade) ao avô, como no Readability.
  const pontos = new Map();
  for (const p of doc.querySelectorAll('p, pre')) {
    const t = texto(p);
    if (t.length < 50) continue;
    const semLinks = t.length - [...p.querySelectorAll('a')].reduce((s, a) => s + texto(a).length, 0);
    const pai = p.parentElement;
    if (!pai) continue;
    pontos.set(pai, (pontos.get(pai) ?? 0) + semLinks);
    const avo = pai.parentElement;
    if (avo) pontos.set(avo, (pontos.get(avo) ?? 0) + semLinks / 2);
  }
  let topo = null;
  let topoPontos = 0;
  for (const [el, p] of pontos) if (p > topoPontos) { topo = el; topoPontos = p; }
  return topo ?? melhor ?? doc.body ?? doc.documentElement;
}

// ---------------------------------------------------------------------------------------------------------------
// Metadados e JSON-LD

const meta = (doc, chave) => {
  for (const m of doc.querySelectorAll('meta')) {
    if ([m.getAttribute('name'), m.getAttribute('property'), m.getAttribute('itemprop')].some((v) => v?.toLowerCase() === chave)) {
      const c = limparTexto(m.getAttribute('content'));
      if (c) return c;
    }
  }
  return null;
};

const semHtml = (s) => limparTexto(String(s ?? '').replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#0?39;/g, "'"));

function lerJsonLd(doc) {
  const nos = [];
  const visitar = (n) => {
    if (Array.isArray(n)) return n.forEach(visitar);
    if (!n || typeof n !== 'object') return;
    if (n['@type']) nos.push(n);
    if (n['@graph']) visitar(n['@graph']);
  };
  for (const s of doc.querySelectorAll('script[type="application/ld+json"]')) {
    try { visitar(JSON.parse(s.textContent.trim().replace(/^<!--|-->$/g, ''))); } catch { /* JSON-LD quebrado é comum */ }
  }
  return nos;
}

const tiposDe = (n) => [].concat(n['@type']).map((t) => String(t).toLowerCase());
const umTexto = (v) => {
  if (v == null) return '';
  if (Array.isArray(v)) return v.map(umTexto).filter(Boolean).join(', ');
  if (typeof v === 'object') {
    if (v['@type'] === 'PostalAddress') return [v.streetAddress, v.addressLocality, v.addressRegion, v.addressCountry?.name ?? v.addressCountry].filter(Boolean).join(', ');
    return umTexto(v.name ?? v.text ?? '');
  }
  return semHtml(v);
};

function passosHowTo(valor, saida = []) {
  for (const p of [].concat(valor ?? [])) {
    if (typeof p === 'string') saida.push(semHtml(p));
    else if (p?.itemListElement) passosHowTo(p.itemListElement, saida);
    else if (p) saida.push(semHtml(p.text ?? p.name ?? ''));
  }
  return saida.filter(Boolean);
}

// ---------------------------------------------------------------------------------------------------------------
// Extração principal

export function extrairDaPagina(html, url, ctx, adp = adaptador) {
  if (!/<(html|body|p|div|article|h1)[\s>]/i.test(html)) return null;
  const doc = ctx.parsear(html);
  const saida = resultadoVazio();
  const vistos = new Set();
  const novo = (t) => {
    const k = normaliza(t).slice(0, 60);
    if (!k || vistos.has(k)) return false;
    vistos.add(k);
    return true;
  };
  const addFato = (t, secao, confianca) => {
    const limpo = limparTexto(t);
    if (!boaFrase(limpo) || saida.fatos.length >= LIMITES.fatos || !novo(limpo)) return;
    saida.fatos.push(fato(adp, { texto: limpo, secao, fonte: url, confianca }));
  };
  const addAtributo = (nome, valor) => {
    const n = limparTexto(nome);
    const v = limparTexto(valor).replace(/[;,]+$/, '');
    if (!n || !v || n.length > 80 || v.length > 300 || INSTRUCAO.test(v) || saida.atributos.length >= LIMITES.atributos) return;
    if (saida.atributos.some((a) => a.nome === n && a.valor === v)) return;
    saida.atributos.push(atributo(adp, { nome: n, valor: v, fonte: url }));
  };

  // Metadados e JSON-LD vêm antes da limpeza (o título e as datas costumam estar em header/head).
  const nos = lerJsonLd(doc);
  const h1 = texto(doc.querySelector('h1'));
  const canonical = doc.querySelector('link[rel="canonical"]')?.getAttribute('href');
  let urlCanonica = url;
  try { if (canonical) urlCanonica = new URL(canonical, url).href; } catch { /* mantém a URL pedida */ }
  const artigo = nos.find((n) => tiposDe(n).some((t) => /article|blogposting|newsarticle|techarticle/.test(t)));
  const dataTime = doc.querySelector('time[datetime]')?.getAttribute('datetime');
  saida.metadados = {
    titulo: limparTexto(meta(doc, 'og:title') ?? texto(doc.querySelector('title')) ?? h1) || h1,
    idioma: doc.documentElement?.getAttribute('lang') ?? meta(doc, 'og:locale') ?? null,
    data: artigo?.datePublished ?? meta(doc, 'article:published_time') ?? dataTime ?? null,
    modificado: artigo?.dateModified ?? meta(doc, 'article:modified_time') ?? null,
    url: urlCanonica,
    site: meta(doc, 'og:site_name'),
    tipo: meta(doc, 'og:type'),
    descricao: meta(doc, 'description') ?? meta(doc, 'og:description'),
  };
  if (h1 && h1.length < 200) saida.metadados.h1 = h1;

  for (const no of nos) {
    const tipos = tiposDe(no);
    if (tipos.includes('faqpage')) {
      for (const q of [].concat(no.mainEntity ?? [])) {
        const pergunta = semHtml(q?.name);
        const resposta = semHtml(q?.acceptedAnswer?.text ?? q?.suggestedAnswer?.text);
        if (pergunta && resposta.length > 15 && !INSTRUCAO.test(resposta) && saida.pares.length < LIMITES.pares) {
          saida.pares.push(par(adp, { pergunta, resposta: resposta.length > 600 ? `${resposta.slice(0, 597).replace(/\s+\S*$/, '')}…` : resposta, fonte: url }));
        }
      }
    }
    if (tipos.includes('howto')) {
      const titulo = semHtml(no.name);
      passosHowTo(no.step).slice(0, 12).forEach((passo, i) => addFato(`Passo ${i + 1}: ${passo}`, titulo || 'Passo a passo', CONFIANCA.alta));
    }
    if (tipos.some((t) => /article|blogposting|newsarticle|techarticle/.test(t))) {
      if (no.description) addFato(semHtml(no.description), null, CONFIANCA.media);
      const autor = umTexto(no.author);
      if (autor) addAtributo('autor', autor);
      if (no.datePublished) addAtributo('publicado em', String(no.datePublished).slice(0, 10));
      if (no.dateModified) addAtributo('atualizado em', String(no.dateModified).slice(0, 10));
    }
    if (tipos.includes('person')) {
      const nome = umTexto(no.name);
      for (const [campo, rotulo] of [['jobTitle', 'cargo'], ['birthDate', 'nascimento'], ['birthPlace', 'local de nascimento'], ['nationality', 'nacionalidade'], ['worksFor', 'trabalha em'], ['alumniOf', 'formação']]) {
        const v = umTexto(no[campo]);
        if (v && nome) addAtributo(`${rotulo} de ${nome}`, v);
      }
      if (no.description) addFato(semHtml(no.description), null, CONFIANCA.media);
    }
    if (tipos.some((t) => /^(organization|corporation|localbusiness|ngo|educationalorganization)$/.test(t))) {
      const nome = umTexto(no.name);
      for (const [campo, rotulo] of [['legalName', 'razão social'], ['foundingDate', 'fundação'], ['address', 'endereço'], ['numberOfEmployees', 'funcionários'], ['slogan', 'slogan'], ['areaServed', 'área de atuação']]) {
        const v = umTexto(no[campo]);
        if (v && nome) addAtributo(`${rotulo} de ${nome}`, v);
      }
      if (no.description) addFato(semHtml(no.description), null, CONFIANCA.media);
    }
  }

  // Meta description: a página diz de si mesma, confiança média.
  if (saida.metadados.descricao) addFato(saida.metadados.descricao, null, CONFIANCA.media);

  // A partir daqui só o que está visível.
  limpar(doc);
  const principal = areaPrincipal(doc);
  const paragrafos = [...principal.querySelectorAll('p')].filter((p) => {
    const t = texto(p);
    const links = [...p.querySelectorAll('a')].reduce((s, a) => s + texto(a).length, 0);
    return t.length > 0 && links / t.length < 0.7;
  });

  const abertura = paragrafos.find((p) => {
    const t = texto(p);
    return t.length > 60 && !RUIDO.test(t) && !INSTRUCAO.test(t) && !/^(foto|imagem|crédito|fonte|publicado|atualizado|por )\b/i.test(t);
  });
  const conceitos = new Map();
  const addConceito = (nome, href, peso) => {
    const n = limparTexto(nome);
    if (n.length < 3 || n.length > 60 || !/[a-zA-ZÀ-ú]{3}/.test(n) || /^(clique|leia|veja|saiba|aqui|mais|ver|home|início|voltar)\b/i.test(n) || INSTRUCAO.test(n)) return;
    if (normaliza(n) === normaliza(saida.metadados.h1 ?? '') ) return;
    const chave = normaliza(n);
    if (!chave || conceitos.has(chave) || conceitos.size >= LIMITES.conceitos) return;
    let alvo;
    try { if (href && !href.startsWith('#')) { const u = new URL(href, url); if (/^https?:$/.test(u.protocol)) alvo = u.href; } } catch { /* sem link */ }
    conceitos.set(chave, { nome: n, ...(alvo ? { url: alvo } : {}), peso });
  };
  if (abertura) {
    const t = texto(abertura);
    addFato(resumo(t, 320), 'abertura', CONFIANCA.media);
    // Definição pelo termo em negrito: "X é ..." com X em <strong>.
    const negrito = [...abertura.querySelectorAll('strong, b')].map(texto).find((n) => n.length >= 3 && n.length <= 80);
    if (negrito) {
      const frase = frases(t).find((f) => f.includes(negrito) && /\b(é|são|significa|refere-se|define-se|chama-se|consiste|is|are|means)\b/i.test(f));
      if (frase) addFato(frase, 'definição', CONFIANCA.media);
      addConceito(negrito, null, 0.8);
    }
    for (const a of abertura.querySelectorAll('a[href]')) addConceito(texto(a), a.getAttribute('href'), 0.5);
  }

  // Uma frase por seção (h2/h3): o primeiro parágrafo depois do título.
  const TITULO_RUIM = /(coment|relacionad|veja (também|mais)|compartilh|índice|sumário|sobre o autor|about the (author|site)|sobre nós|leia (também|mais)|newsletter|navegação|menu|related|share|comments|table of contents|contents|referências|notas)/i;
  let secaoAtual = null;
  let secoes = 0;
  for (const el of principal.querySelectorAll('h2, h3, p')) {
    if (el.tagName === 'P') {
      if (!secaoAtual?.nome || secaoAtual.usada || secoes >= MAX_SECOES || !paragrafos.includes(el)) continue;
      const frase = resumo(texto(el), 300);
      if (frase) { addFato(frase, secaoAtual.nome, CONFIANCA.media); secaoAtual.usada = true; secoes++; }
    } else {
      const nome = texto(el);
      secaoAtual = nome && nome.length <= 120 && !TITULO_RUIM.test(nome) ? { nome, usada: false } : null;
    }
  }

  // Listas curtas: "Termo: descrição" em todos os itens vira atributos; as outras viram um fato com a lista.
  let listas = 0;
  for (const lista of principal.querySelectorAll('ul, ol')) {
    if (listas >= 5 || lista.closest('li') ) continue;
    const itens = [...lista.children].filter((i) => i.tagName === 'LI');
    if (itens.length < 3 || itens.length > 12) continue;
    const textos = itens.map(texto);
    const linksTam = itens.reduce((s, i) => s + [...i.querySelectorAll('a')].reduce((x, a) => x + texto(a).length, 0), 0);
    if (textos.some((t) => t.length < 3 || t.length > 220) || linksTam / textos.join('').length > 0.6 || textos.some((t) => RUIDO.test(t) || INSTRUCAO.test(t))) continue;
    listas++;
    const pares = textos.map((t) => t.match(/^([^:–—]{2,40}):\s+(.{2,200})$/));
    if (pares.every(Boolean)) {
      pares.slice(0, 10).forEach((m) => addAtributo(m[1], m[2]));
      continue;
    }
    const anterior = lista.previousElementSibling;
    const intro = anterior && /^(P|H2|H3|H4)$/.test(anterior.tagName) ? texto(anterior).replace(/[:.]\s*$/, '') : '';
    const cabeca = intro && intro.length <= 150 ? `${intro}: ` : '';
    const lead = ordenada(lista) ? textos.slice(0, 8).map((t, i) => `${i + 1}) ${t}`) : textos.slice(0, 8);
    const corpo = lead.join('; ');
    addFato(`${cabeca}${corpo}.`.slice(0, 400), intro && intro.length <= 80 ? intro : null, CONFIANCA.baixa);
  }

  // Tabelas curtas: duas colunas → atributos; até 4 colunas → uma frase por linha, com os cabeçalhos.
  let tabelas = 0;
  for (const tabela of principal.querySelectorAll('table')) {
    if (tabelas >= 3) break;
    const linhas = [...tabela.querySelectorAll('tr')].map((tr) => [...tr.children].filter((c) => /^(TD|TH)$/.test(c.tagName)).map(texto));
    if (linhas.length < 2 || linhas.length > 16) continue;
    const largura = Math.max(...linhas.map((l) => l.length));
    if (largura < 2 || largura > 4 || linhas.some((l) => l.some((c) => c.length > 160))) continue;
    tabelas++;
    if (largura === 2) {
      for (const [nome, valor] of linhas.slice(0, 10)) if (nome && valor && nome.length <= 60) addAtributo(nome, valor);
    } else {
      const [cab, ...resto] = linhas;
      for (const l of resto.slice(0, 5)) {
        if (!l[0]) continue;
        addFato(`${l[0]}: ${l.slice(1).map((v, i) => `${cab[i + 1] ?? ''} ${v}`.trim()).join('; ')}.`, texto(tabela.querySelector('caption')) || null, CONFIANCA.baixa);
      }
    }
  }

  // Blocos de código.
  for (const pre of principal.querySelectorAll('pre')) {
    if (saida.codigos.length >= LIMITES.codigos) break;
    const codigo = (pre.textContent ?? '').replace(/\r/g, '').trim();
    if (codigo.length < 10 || codigo.length > 3000) continue;
    const classes = `${pre.getAttribute('class') ?? ''} ${pre.querySelector('code')?.getAttribute('class') ?? ''} ${pre.getAttribute('data-lang') ?? ''}`;
    const linguagem = classes.match(/(?:lang(?:uage)?-|data-lang=)([a-z0-9+#-]+)/i)?.[1]?.toLowerCase() ?? classes.match(/\b(python|javascript|js|bash|sh|sql|html|css|json|java|go|rust|ruby|php|c|cpp|typescript)\b/i)?.[1]?.toLowerCase() ?? 'texto';
    let anterior = pre.previousElementSibling;
    while (anterior && !/^(P|H2|H3|H4)$/.test(anterior.tagName)) anterior = anterior.previousElementSibling;
    const explicacao = anterior ? resumo(texto(anterior), 300) || texto(anterior).slice(0, 300) : '';
    if (INSTRUCAO.test(codigo) || INSTRUCAO.test(explicacao)) continue;
    saida.codigos.push({ linguagem, codigo, explicacao, fonte: url });
  }

  saida.conceitos = [...conceitos.values()];
  saida.fatos = saida.fatos.slice(0, LIMITES.fatos);
  const nada = !saida.fatos.length && !saida.pares.length && !saida.atributos.length && !saida.codigos.length && !saida.conceitos.length;
  return nada ? null : saida;
}

const ordenada = (lista) => lista.tagName === 'OL';
