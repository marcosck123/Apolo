// Adaptador do Brasil Escola (brasilescola.uol.com.br) — artigos escolares em português.
//
// Licença: os Termos de Uso (brasilescola.uol.com.br/termos-de-uso, cláusula 11) dizem que textos, questões e imagens "são protegidos e pertencem
// à Rede Omnia", proíbem "reproduzir" e "extrair em massa" e vedam "automação, raspagem ou extração massiva sem autorização". Não há licença aberta.
// Por isso: uma página por vez, sem crawl, só frases curtas (≤ 400 caracteres) sempre com a URL da fonte, e a `licenca` diz isso. O robots.txt
// libera o site (Allow: /) e só proíbe /busca/, /imprimir/, /anuncios/, /reactions/ e /cadastro/ativar.htm — por isso NÃO usamos a busca do site.
//
// Como acha a página: o site não tem API e a busca é proibida pelo robots.txt. Então:
//   - com `url` de brasilescola.uol.com.br (o roteador manda quando já sabe a página): usa direto, 1 requisição;
//   - sem `url`: só tenta ADIVINHAR (até 3 requisições) <categoria>/<tema-em-slug>.htm para perguntas de definição ou de lugar
//     (ex.: "Rondônia" → /brasil/rondonia.htm) e só aceita a página se o título bater com o tema. Se nada der certo, devolve null.
//
// Toda a lógica de leitura está em funções PURAS sobre o `document` (exportadas, e reaproveitadas pelo Mundo Educação, que é do mesmo grupo
// e tem a mesma estrutura: JSON-LD Article/FAQPage, meta description, parágrafo de abertura com negrito, h2/h3).
import { atributo, CONFIANCA, fato, limparTexto, par, pareceFrase } from './contrato.js';

const LICENCA = 'Todos os direitos reservados (Rede Omnia, Termos de Uso cláusula 11): sem licença aberta; guardar só frases curtas com a fonte';
const MAX_ADIVINHACOES = 3;

const adaptador = {
  nome: 'brasilescola',
  licenca: LICENCA,
  tipos: ['definicao', 'lugar', 'geral'],
  dominios: ['brasilescola.uol.com.br'],
  async extrair({ tema = '', consulta = '', tipo = 'geral', url = null } = {}, ctx) {
    return extrairDeSite(adaptador, { tema: tema || consulta, tipo, url, dominio: 'brasilescola.uol.com.br', categorias: CATEGORIAS, tiposQueAdivinham: ['definicao', 'lugar'], opcoes: { resumo: 'p.resumo-artigo' } }, ctx);
  },
};
export default adaptador;

// Categorias (primeiro trecho do caminho) onde adivinhar, por tipo de pergunta.
const CATEGORIAS = {
  lugar: ['brasil', 'geografia', 'geografiag'],
  definicao: ['geografia', 'historia', 'matematica', 'biologia', 'quimica', 'fisica', 'gramatica', 'sociologia', 'filosofia'],
};

// ───────────────────────── Roteiro compartilhado (rede + validação) ─────────────────────────

export async function extrairDeSite(adaptador, { tema, tipo, url, dominio, categorias, tiposQueAdivinham, opcoes = {} }, ctx) {
  let enderecos;
  let validar = false;
  if (url && hospedeiroDe(url, dominio)) {
    enderecos = [url];
  } else if (tiposQueAdivinham.includes(tipo)) {
    const slug = slugDoTema(tema);
    if (!slug) return null;
    enderecos = (categorias[tipo] ?? categorias.definicao ?? []).slice(0, MAX_ADIVINHACOES).map((c) => `https://${dominio}/${c}/${slug}.htm`);
    validar = true;
  } else {
    return null; // sem URL e sem um tipo em que valha adivinhar: melhor não gastar requisições
  }
  for (const endereco of enderecos) {
    const r = await ctx.buscar(endereco);
    if (r.status === 404 || r.status === 410) continue;
    if (r.status >= 500 || r.status === 429) throw new Error(`${dominio} respondeu ${r.status}`);
    if (r.status !== 200 || !r.texto) continue;
    const document = ctx.parsear(r.texto);
    const resultado = extrairArtigo(document, { adaptador, url: r.url || endereco, ...opcoes });
    if (!resultado) continue;
    if (validar && !tituloCombina(resultado.metadados.titulo, tema)) {
      ctx.registrar?.(`${adaptador.nome}: ${endereco} existe, mas o título "${resultado.metadados.titulo}" não bate com "${tema}"`);
      continue;
    }
    ctx.registrar?.(`${adaptador.nome}: ${endereco} → ${resultado.fatos.length} fatos, ${resultado.pares.length} pares, ${resultado.atributos.length} atributos`);
    return resultado;
  }
  return null;
}

export const dobrar = (t) => String(t ?? '').toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replace(/\s+/g, ' ').trim();

export function hospedeiroDe(url, dominio) {
  try { const h = new URL(url).hostname; return h === dominio || h === `www.${dominio}`; } catch { return false; }
}

export function slugDoTema(tema) {
  return dobrar(tema).replace(/[^a-z0-9\s-]/g, ' ').replace(/\s+/g, '-').replace(/^-+|-+$/g, '').slice(0, 80);
}

// Todas as palavras do tema (com 3+ letras) têm de aparecer no título da página adivinhada.
export function tituloCombina(titulo, tema) {
  const t = dobrar(titulo);
  const palavras = dobrar(tema).split(/[^a-z0-9]+/).filter((p) => p.length >= 3 && !['que', 'por', 'uma', 'dos', 'das', 'com', 'para'].includes(p));
  return palavras.length > 0 && palavras.every((p) => t.includes(p));
}

// ───────────────────────── Funções puras sobre o document ─────────────────────────

const IGNORAR_TAGS = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'IFRAME', 'SVG']);
const BLOCOS = new Set(['P', 'LI', 'DIV', 'BR', 'TR', 'TD', 'TH', 'H1', 'H2', 'H3', 'H4', 'UL', 'OL']);
const CLASSES_RUIDO = /\b(pub_insert\w*|lista-topicos|anuncie\w*|banner\w*|publicidade|leia-tambem|ads?-\w+)\b/i;
const MARCA_INI = '\u0001';
const MARCA_FIM = '\u0002';

function oculto(el) {
  const estilo = (el.getAttribute('style') ?? '').replace(/\s+/g, '').toLowerCase();
  return el.hasAttribute('hidden') || el.getAttribute('aria-hidden') === 'true' || /display:none|visibility:hidden/.test(estilo);
}

// Elemento escondido (ou dentro de algo escondido) ou dentro de propaganda/índice de tópicos.
export function descartavel(el) {
  for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
    if (oculto(e) || CLASSES_RUIDO.test(e.getAttribute('class') ?? '') || /^(anchor-ia)$/.test(e.getAttribute('id') ?? '')) return true;
  }
  return false;
}

// Texto visível. Com `marcar`, o conteúdo de <strong>/<b> vem entre marcas (para achar termos em negrito).
export function textoVisivel(no, { marcar = false } = {}) {
  if (!no) return '';
  if (no.nodeType === 3) return no.data ?? '';
  if (no.nodeType !== 1 || IGNORAR_TAGS.has(String(no.tagName).toUpperCase())) return '';
  if (oculto(no) || CLASSES_RUIDO.test(no.getAttribute('class') ?? '')) return '';
  let dentro = [...no.childNodes].map((n) => textoVisivel(n, { marcar })).join('');
  if (marcar && (no.tagName === 'STRONG' || no.tagName === 'B')) dentro = `${MARCA_INI}${dentro}${MARCA_FIM}`;
  return BLOCOS.has(no.tagName) ? ` ${dentro} ` : dentro;
}

const texto = (no) => limparTexto(textoVisivel(no));

// Quebra em frases sem partir em abreviações curtas ("Dr.", "hab.", "séc.") nem em decimais.
export function frases(t) {
  const partes = limparTexto(t).split(/(?<=[.!?…])\s+(?=[A-ZÀ-Ú“"(\d])/u);
  const saida = [];
  for (const p of partes) {
    const ant = saida[saida.length - 1];
    if (ant && /(?:\b\p{L}|\b(?:dr|dra|sr|sra|prof|profa|séc|sec|hab|km|aprox|cap|av|ex|ed|art|vol|fig|nº))\.$/iu.test(ant)) saida[saida.length - 1] = `${ant} ${p}`;
    else saida.push(p);
  }
  return saida;
}

const CHAMADA = /^(clique|saiba|aprenda|veja|confira|conhe[cç]a|descubra|entenda|leia|acesse|venha|vem)\b/i;
const LIXO_PARAGRAFO = /^(leia (também|mais)|veja (também|mais)|saiba mais|não pare agora|anuncie|publicidade|fonte:|imagem:|crédito)/i;

// Primeira frase que parece frase de verdade (30–400 caracteres, sem chamada de marketing).
export function primeiraFraseBoa(t) {
  for (const f of frases(t)) if (pareceFrase(f) && !CHAMADA.test(f)) return limparTexto(f);
  return null;
}

// JSON-LD: devolve todos os objetos (achatando listas e @graph). Ignora blocos quebrados.
export function lerJsonLd(doc) {
  const saida = [];
  const visitar = (x) => {
    if (Array.isArray(x)) return x.forEach(visitar);
    if (x && typeof x === 'object') { saida.push(x); if (x['@graph']) visitar(x['@graph']); }
  };
  for (const s of doc.querySelectorAll('script[type="application/ld+json"]')) {
    const bruto = s.textContent ?? '';
    try { visitar(JSON.parse(bruto)); } catch {
      try { visitar(JSON.parse(bruto.replace(/[\u0000-\u001f]+/g, ' '))); } catch { /* bloco inválido: segue sem ele */ }
    }
  }
  return saida;
}

const ehTipo = (o, tipo) => [].concat(o?.['@type'] ?? []).includes(tipo);

function paraTexto(doc, html) {
  try {
    const d = doc.createElement('div');
    d.innerHTML = String(html ?? '');
    return limparTexto(textoVisivel(d));
  } catch { return limparTexto(String(html ?? '').replace(/<[^>]+>/g, ' ')); }
}

// "2008-02-09-0309:27:58" (formato torto do site) → "2008-02-09".
export function dataIso(valor) {
  const m = String(valor ?? '').match(/^(\d{4})-(\d{2})-(\d{2})/);
  return m && +m[2] >= 1 && +m[2] <= 12 && +m[3] >= 1 && +m[3] <= 31 ? `${m[1]}-${m[2]}-${m[3]}` : undefined;
}

export function descricaoMeta(doc) {
  const m = doc.querySelector('meta[name="description"]') ?? doc.querySelector('meta[property="og:description"]');
  return limparTexto(m?.getAttribute('content') ?? '');
}

const SELETORES_CORPO = ['.ler-texto', '.texto-conteudo', 'article .area-texto', 'article', '.conteudo'];
export function corpoDoArtigo(doc) {
  for (const s of SELETORES_CORPO) {
    const el = doc.querySelector(s);
    if (el && !descartavel(el) && el.querySelector('p')) return el;
  }
  return null;
}

const SECAO_IGNORADA = /^(t[óo]picos deste artigo|exerc[ií]cios?|quest[õo]es|videoaulas?|v[íi]deos?|artigos? relacionados|refer[êe]ncias?|leia (também|mais)|veja (também|mais)|fontes?|ferramentas|[úu]ltimas not[íi]cias|gabarito|resolu[cç][ãa]o)\b/i;

// Quebra o corpo em seções: [{ titulo (null na abertura), nivel, blocos:[{ tipo:'p'|'li'|'par', texto, el }] }].
export function secoes(corpo) {
  const lista = [{ titulo: null, nivel: 0, blocos: [] }];
  for (const el of corpo.querySelectorAll('h2, h3, p, li, tr')) {
    if (descartavel(el)) continue;
    const tag = el.tagName;
    if (tag === 'H2' || tag === 'H3') {
      const titulo = texto(el);
      if (titulo) lista.push({ titulo, nivel: +tag[1], blocos: [] });
      continue;
    }
    const atual = lista[lista.length - 1];
    if (tag === 'TR') {
      const celulas = [...el.querySelectorAll('th, td')].map(texto).filter(Boolean);
      if (celulas.length === 2) atual.blocos.push({ tipo: 'par', nome: celulas[0], valor: celulas[1], texto: `${celulas[0]}: ${celulas[1]}`, el });
      continue;
    }
    if (tag === 'LI' && el.querySelector('p, h2, h3, ul, ol')) continue; // o conteúdo aparece pelos filhos
    if (tag === 'P' && el.closest('li') && !el.closest('li').querySelector('h2, h3')) {
      atual.blocos.push({ tipo: 'li', texto: texto(el), el });
      continue;
    }
    if (tag === 'P' && el.closest('td, th')) continue;
    const t = texto(el);
    if (t) atual.blocos.push({ tipo: tag === 'LI' ? 'li' : 'p', texto: t, el });
  }
  return lista;
}

// Termos em negrito de um parágrafo (juntando negritos vizinhos: "<b>r</b><b>egião</b>" → "região").
export function termosEmNegrito(p) {
  const marcado = textoVisivel(p, { marcar: true }).replace(new RegExp(`${MARCA_FIM}(\\s*)${MARCA_INI}`, 'g'), '$1');
  const termos = [];
  for (const m of marcado.matchAll(new RegExp(`(.?)${MARCA_INI}([^${MARCA_FIM}]*)${MARCA_FIM}(.?)`, 'g'))) {
    const antes = m[1].replace(/[\u0001\u0002]/g, '');
    const depois = m[3].replace(/[\u0001\u0002]/g, '');
    const t = limparTexto(m[2]).replace(/[:.,;]+$/, '');
    if (/\p{L}/u.test(antes) && /\p{L}/u.test(t[0] ?? '')) continue; // começa no meio de uma palavra
    if (/\p{L}/u.test(depois) && /\p{L}/u.test(t[t.length - 1] ?? '')) continue; // termina no meio de uma palavra
    termos.push(t);
  }
  return termos;
}

const PALAVRA_FRACA = /^(a|o|as|os|um|uma|de|do|da|dos|das|em|no|na|nos|nas|e|ou|que|se|é|são|foi|ao|à|com|para|por|integra|ser|como)$/i;
const ruimComoConceito = (t) => {
  const palavras = t.split(/\s+/);
  return t.length < 3 || t.length > 50 || palavras.length > 5 || PALAVRA_FRACA.test(palavras[0]) || PALAVRA_FRACA.test(palavras[palavras.length - 1]) || /^\d+$/.test(t) || CHAMADA.test(t) || LIXO_PARAGRAFO.test(t) || !/\p{L}{3}/u.test(t);
};

export function conceitosDoParagrafo(p, base) {
  const saida = [];
  const vistos = new Set();
  for (const t of termosEmNegrito(p)) {
    if (ruimComoConceito(t) || vistos.has(dobrar(t))) continue;
    vistos.add(dobrar(t));
    const link = [...p.querySelectorAll('a')].find((a) => !descartavel(a) && dobrar(texto(a)).includes(dobrar(t)));
    let url;
    try { url = link ? new URL(link.getAttribute('href') ?? '', base).href : undefined; } catch { url = undefined; }
    saida.push({ nome: t, ...(url && { url }), peso: saida.length === 0 ? 0.8 : 0.6 });
    if (saida.length >= 6) break;
  }
  return saida;
}

export function conceitosDoCaminho(doc, base) {
  const saida = [];
  for (const a of doc.querySelectorAll('[itemtype*="BreadcrumbList"] li a, ol[itemtype*="BreadcrumbList"] a, li[itemprop="itemListElement"] a')) {
    if (descartavel(a)) continue;
    const nome = texto(a);
    if (!nome || /^(home|in[íi]cio|p[áa]gina inicial)$/i.test(nome) || saida.some((c) => c.nome === nome)) continue;
    let url;
    try { url = new URL(a.getAttribute('href') ?? '', base).href; } catch { url = undefined; }
    saida.push({ nome, ...(url && { url }), peso: 0.5 });
  }
  return saida.slice(0, 4);
}

// "Nome: valor" (lista de dados) → { nome, valor }, ou null se não parecer um par.
export function pareceNomeValor(t) {
  const m = limparTexto(t).match(/^([^:]{2,40}):\s*(.{1,200})$/u);
  if (!m) return null;
  const nome = m[1].trim();
  const valor = m[2].trim().replace(/[.;]$/, '');
  if (!/^\p{Lu}/u.test(nome) || /[.!?]$/.test(nome) || nome.split(/\s+/).length > 5 || !valor || /^https?:/i.test(valor) || LIXO_PARAGRAFO.test(nome)) return null;
  return { nome, valor };
}

const SECAO_DE_DADOS = /^(dados (gerais|b[áa]sicos|do (pa[íi]s|estado|munic[íi]pio))|ficha (t[ée]cnica|resumo)|caracter[íi]sticas gerais|em resumo)\b/i;
const SECAO_EXEMPLO = /^exemplo\s*\d*\b/i;

// Corta a resposta numa frase inteira e no máximo 400 caracteres (só trechos curtos, por causa dos direitos autorais).
export function encurtar(t, max = 400) {
  const limpo = limparTexto(t);
  if (limpo.length <= max) return limpo;
  let acumulado = '';
  for (const f of frases(limpo)) {
    if ((acumulado + ' ' + f).trim().length > max) break;
    acumulado = (acumulado + ' ' + f).trim();
  }
  return acumulado;
}

// Exemplo resolvido: enunciado (+ dados curtos) e, se o texto disser, o resultado.
export function exemploDaSecao(secao) {
  const ps = secao.blocos.filter((b) => b.tipo === 'p' || b.tipo === 'li').map((b) => b.texto).filter((t) => !LIXO_PARAGRAFO.test(t));
  if (!ps.length || ps[0].length < 15) return null;
  let enunciado = ps[0];
  if (ps[1] && ps[1].length < 80 && /[\d{]/.test(ps[1]) && !/[.!?]$/.test(ps[1])) enunciado = `${enunciado} ${ps[1]}`;
  const resultado = ps.slice(1).reverse().find((t) => /^(portanto|logo|assim|dessa forma|desse modo|ent[ãa]o|resposta|resultado)\b/i.test(t) && t.length <= 200 && /\d/.test(t));
  let t = `Exemplo: ${enunciado}`;
  if (resultado && (t + ' Resultado: ' + resultado).length <= 400) t += ` Resultado: ${resultado}`;
  return t.length <= 400 && pareceFrase(t) ? t : null;
}

// Lê o artigo inteiro. `opcoes.resumo` é o seletor do parágrafo de resumo (Brasil Escola: p.resumo-artigo).
// Devolve o resultado do contrato ou null se a página não tiver a estrutura esperada.
export function extrairArtigo(doc, { adaptador, url, resumo = null, maxFatos = 18 } = {}) {
  if (!doc?.querySelector) return null;
  const ld = lerJsonLd(doc);
  const artigo = ld.find((o) => ehTipo(o, 'Article') || ehTipo(o, 'NewsArticle') || ehTipo(o, 'BlogPosting'));
  const corpo = corpoDoArtigo(doc);
  if (!artigo && !corpo) return null;
  const canonica = doc.querySelector('link[rel="canonical"]')?.getAttribute('href');
  const fonte = url ?? canonica ?? artigo?.url ?? artigo?.mainEntityOfPage;
  const h1 = texto(doc.querySelector('h1'));
  const titulo = limparTexto(artigo?.headline ?? '') || h1;
  if (!titulo) return null; // sem título não dá para saber de que página se trata

  const fatos = [];
  const novoFato = (t, secao, confianca = CONFIANCA.media, extra = {}) => {
    const limpo = limparTexto(t);
    if (!pareceFrase(limpo) || fatos.some((f) => f.texto === limpo) || fatos.length >= maxFatos) return;
    fatos.push({ ...fato(adaptador, { texto: limpo, secao, fonte, confianca }), ...extra });
  };

  // 1. resumo do artigo (Brasil Escola) e descrição meta (quando não é chamada de marketing)
  if (resumo) {
    const el = doc.querySelector(resumo);
    if (el && !descartavel(el)) novoFato(primeiraFraseBoa(texto(el)) ?? '', 'Resumo');
  }
  const meta = descricaoMeta(doc);
  if (meta) novoFato(primeiraFraseBoa(meta) ?? '', 'Descrição', CONFIANCA.media);

  const conceitos = [];
  const atributos = [];
  if (corpo) {
    const partes = secoes(corpo);
    // 2. parágrafo de abertura: a definição, e os termos em negrito viram conceitos
    const abertura = partes[0].blocos.find((b) => b.tipo === 'p' && b.texto.length >= 40 && !LIXO_PARAGRAFO.test(b.texto));
    if (abertura) {
      const f = primeiraFraseBoa(abertura.texto);
      const eDefinicao = f && /(?<!\p{L})(é|são|chama-se|chamam-se|denomina-se|define-se|consiste|refere-se|significa)(?!\p{L})/iu.test(f);
      if (f) novoFato(f, 'Abertura', eDefinicao ? CONFIANCA.media : CONFIANCA.baixa);
      conceitos.push(...conceitosDoParagrafo(abertura.el, fonte));
    }
    for (const c of conceitosDoCaminho(doc, fonte)) if (!conceitos.some((x) => dobrar(x.nome) === dobrar(c.nome))) conceitos.push(c);

    for (const s of partes.slice(1)) {
      if (SECAO_IGNORADA.test(s.titulo)) continue;
      if (SECAO_EXEMPLO.test(s.titulo)) {
        const ex = exemploDaSecao(s);
        if (ex) novoFato(ex, s.titulo, CONFIANCA.media, { tipo: 'exemplo' });
        continue;
      }
      // 3. dados em pares nome: valor ("Dados gerais", tabelas de duas colunas)
      if (SECAO_DE_DADOS.test(s.titulo) || s.blocos.some((b) => b.tipo === 'par')) {
        for (const b of s.blocos) {
          const nv = b.tipo === 'par' ? { nome: b.nome, valor: b.valor } : b.tipo === 'li' ? pareceNomeValor(b.texto) : null;
          if (nv && atributos.length < 30 && !atributos.some((a) => dobrar(a.nome) === dobrar(nv.nome))) atributos.push(atributo(adaptador, { ...nv, fonte }));
        }
        continue;
      }
      // 4. uma frase útil de cada seção (a primeira que parecer frase)
      const f = s.blocos.filter((b) => b.tipo === 'p' && !LIXO_PARAGRAFO.test(b.texto)).map((b) => primeiraFraseBoa(b.texto)).find(Boolean);
      if (f) novoFato(f, s.titulo, CONFIANCA.media);
    }
  }

  // 5. FAQPage → pares pergunta/resposta
  const pares = [];
  for (const faq of ld.filter((o) => ehTipo(o, 'FAQPage'))) {
    for (const q of [].concat(faq.mainEntity ?? [])) {
      if (!ehTipo(q, 'Question')) continue;
      const resposta = encurtar(paraTexto(doc, [].concat(q.acceptedAnswer ?? [])[0]?.text), 400);
      const pergunta = limparTexto(q.name);
      if (pergunta.length >= 8 && resposta.length >= 3 && !pares.some((p) => p.pergunta === pergunta)) pares.push(par(adaptador, { pergunta, resposta, fonte }));
    }
  }

  if (!fatos.length && !pares.length && !atributos.length) return null;
  const autor = [].concat(artigo?.author ?? [])[0]?.name;
  return {
    fatos, conceitos, pares, codigos: [], atributos,
    metadados: { titulo, idioma: 'pt-BR', data: dataIso(artigo?.dateModified) ?? dataIso(artigo?.datePublished), url: fonte, ...(autor && { autor: limparTexto(autor) }) },
  };
}
