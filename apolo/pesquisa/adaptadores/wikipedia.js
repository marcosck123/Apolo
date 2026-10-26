// Adaptador da Wikipédia (pt; en quando a URL é da en).
// Usa só as APIs oficiais, com 2 requisições por consulta:
//   1) action=query&generator=search (+ pageprops): acha o título certo a partir do tema e já avisa quais páginas são de
//      desambiguação, sem gastar uma requisição por candidato;
//   2) rest_v1/page/html/<título>: o HTML do Parsoid, que traz o parágrafo de abertura (termo em negrito, links internos),
//      as seções (h2/h3), a infobox e a data da última edição. Segue redirecionamentos sozinho.
// Licença do conteúdo: CC BY-SA 4.0 (rodapé de qualquer artigo: "Text is available under the Creative Commons
// Attribution-ShareAlike License 4.0"; termos em foundation.wikimedia.org/wiki/Policy:Terms_of_Use).
import { CONFIANCA, atributo, fato, limparTexto, pareceFrase } from './contrato.js';

const adaptador = {
  nome: 'wikipedia',
  licenca: 'CC BY-SA 4.0',
  tipos: ['definicao', 'pessoa', 'lugar', 'geral'],
  dominios: ['pt.wikipedia.org', 'en.wikipedia.org'],
  extrair,
};
export default adaptador;

// Seções que não têm conhecimento: listas de remissões e bibliografia.
const SECOES_IGNORADAS = /^(ver tamb[ée]m|refer[êe]ncias?|liga[çc][õo]es externas|notas?( e refer[êe]ncias)?|bibliografia|fontes|leitura adicional|galeria|see also|references|external links|notes|further reading|bibliography|sources|gallery)$/i;
const MAX_SECOES = 4;
const MAX_CONCEITOS = 20;
const MAX_ATRIBUTOS = 30;

const normalizar = (t) => String(t ?? '').toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();

async function extrair({ tema, url }, ctx) {
  const alvo = url ? alvoDaUrl(url) : null;
  let host = alvo?.host ?? 'pt.wikipedia.org';
  let titulo = alvo?.titulo ?? null;
  let dataBusca = null;

  if (!titulo) {
    const escolhido = await acharTitulo(tema, host, ctx);
    if (!escolhido) return null;
    titulo = escolhido.title;
    dataBusca = escolhido.timestamp ?? null;
  }

  const r = await ctx.buscar(`https://${host}/api/rest_v1/page/html/${encodeURIComponent(titulo.replace(/ /g, '_'))}`, { cabecalhos: { accept: 'text/html' } });
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`wikipedia: html respondeu ${r.status}`);
  return lerPagina(r.texto, { host, ctx, dataBusca });
}

function alvoDaUrl(texto) {
  try {
    const u = new URL(texto);
    const m = u.pathname.match(/^\/wiki\/([^?#]+)/);
    if (!/(^|\.)wikipedia\.org$/.test(u.hostname) || !m) return null;
    return { host: u.hostname, titulo: decodeURIComponent(m[1]).replace(/_/g, ' ') };
  } catch {
    return null;
  }
}

// Escolhe o primeiro resultado da busca cujo título tem a ver com o tema e que não é página de desambiguação.
// A busca é de texto completo e traz páginas só "citadas" (ex.: livros que mencionam o termo), então o título precisa casar.
async function acharTitulo(tema, host, ctx) {
  const consulta = String(tema ?? '').trim();
  if (!consulta) return null;
  const params = new URLSearchParams({
    action: 'query', generator: 'search', gsrsearch: consulta, gsrlimit: '6', gsrnamespace: '0',
    prop: 'pageprops', ppprop: 'disambiguation', format: 'json', formatversion: '2',
  });
  const r = await ctx.buscar(`https://${host}/w/api.php?${params}`, { json: true });
  if (!r.ok) throw new Error(`wikipedia: busca respondeu ${r.status}`);
  const paginas = [...(r.json()?.query?.pages ?? [])].sort((a, b) => (a.index ?? 99) - (b.index ?? 99));
  const palavras = normalizar(consulta).split(' ').filter(Boolean);
  const casa = (titulo) => {
    // título sem o qualificador "(planeta)"; casa se um contém todas as palavras do outro
    const t = normalizar(titulo.replace(/\s*\(.*\)\s*$/, '')).split(' ').filter(Boolean);
    return t.length > 0 && (t.every((p) => palavras.includes(p)) || palavras.every((p) => t.includes(p)));
  };
  return paginas.find((p) => !p.pageprops?.disambiguation && casa(p.title)) ?? null;
}

// ---------- leitura do HTML ----------

function lerPagina(html, { host, ctx, dataBusca }) {
  const doc = ctx.parsear(html);
  if (doc.querySelector('meta[property="mw:PageProp/disambiguation"]')) return null;

  const titulo = limparTexto(doc.querySelector('title')?.textContent ?? '');
  const versao = doc.querySelector('link[rel="dc:isVersionOf"]')?.getAttribute('href') ?? '';
  const urlCanonica = versao ? `https:${versao}` : `https://${host}/wiki/${encodeURIComponent(titulo.replace(/ /g, '_'))}`;
  const idioma = host.split('.')[0];
  const metadados = {
    titulo, idioma, url: urlCanonica,
    data: doc.querySelector('meta[property="dc:modified"]')?.getAttribute('content') ?? dataBusca ?? undefined,
  };

  const raiz = doc.querySelector('body');
  const intro = [...raiz.querySelectorAll(':scope > section')].find((s) => s.querySelector(':scope > p')) ?? raiz;
  const paragrafos = [...intro.querySelectorAll(':scope > p')].filter((p) => textoLimpo(p).length > 40);
  if (!paragrafos.length) return null;
  // "X pode referir-se a:" sem a marca de desambiguação (páginas antigas)
  if (/pode(m)? referir-se a|may refer to|pode significar/i.test(textoLimpo(paragrafos[0]))) return null;

  const fonte = urlCanonica;
  const fatos = [];
  const vistos = new Set();
  const acrescentar = (texto, secao, confianca) => {
    const f = fato(adaptador, { texto, secao, fonte, confianca });
    if (!pareceFrase(f.texto) || vistos.has(f.texto)) return;
    vistos.add(f.texto);
    fatos.push(f);
  };

  // (a) Abertura: a 1ª frase define o termo (alta); a 2ª complementa.
  const frasesAbertura = frases(textoLimpo(paragrafos[0]));
  const definicao = frasesAbertura[0] ? encurtar(frasesAbertura[0]) : null;
  if (definicao) acrescentar(definicao, null, CONFIANCA.alta);
  if (frasesAbertura[1]) acrescentar(frasesAbertura[1], null, CONFIANCA.media);

  // Seções: até 2 frases de cada uma das primeiras MAX_SECOES que tenham texto.
  let usadas = 0;
  for (const secao of raiz.querySelectorAll(':scope > section')) {
    if (usadas >= MAX_SECOES) break;
    const nome = limparTexto(secao.querySelector(':scope > h2')?.textContent ?? '');
    if (!nome || SECOES_IGNORADAS.test(nome)) continue;
    const doSecao = [];
    for (const p of secao.querySelectorAll('p')) {
      for (const frase of frases(textoLimpo(p))) if (pareceFrase(frase)) doSecao.push(frase);
      if (doSecao.length >= 2) break;
    }
    if (!doSecao.length) continue;
    usadas++;
    for (const frase of doSecao.slice(0, 2)) acrescentar(frase, nome, CONFIANCA.media);
  }

  return {
    fatos,
    conceitos: conceitosDaAbertura(paragrafos, titulo),
    atributos: lerInfobox(doc, fonte),
    metadados,
  };
}

// Texto de um nó sem referências [1], estilos embutidos e elementos escondidos.
function textoLimpo(no) {
  const copia = no.cloneNode(true);
  copia.querySelectorAll('sup, style, script, .reference, .mw-ref, .noprint, .navbar, [style*="display:none"], [style*="display: none"], [hidden]').forEach((e) => e.remove());
  copia.querySelectorAll('br').forEach((e) => e.replaceWith(' '));
  return limparTexto(copia.textContent);
}

// Separa em frases sem cortar em abreviaturas ("Dr.", "séc.", "a.C.") nem em iniciais ("A. Santos").
const ABREVIATURAS = /(?:\b(?:dr|dra|sr|sra|srta|prof|profa|eng|av|séc|sec|cap|art|fig|vol|nº|n|etc|cf|ex|ca|ver|st|mr|mrs|ms|jr|vs|aprox|apr|p|pp|ed)|\b[a-zA-ZÀ-ú]|\b[ad]\.C)\.$/i;
export function frases(texto) {
  const partes = [];
  let atual = '';
  for (const pedaco of texto.split(/(?<=[.!?])\s+(?=[A-ZÀ-Ú0-9«"“(])/)) {
    atual = atual ? `${atual} ${pedaco}` : pedaco;
    if (ABREVIATURAS.test(atual)) continue;
    partes.push(atual);
    atual = '';
  }
  if (atual) partes.push(atual);
  return partes;
}

// Definições com etimologia entre parênteses passam de 400 caracteres: sem os parênteses cabem.
function encurtar(frase) {
  if (frase.length <= 400) return frase;
  return limparTexto(frase.replace(/\s*\([^()]*\)/g, ''));
}

// ---------- conceitos ----------

const MESES = /^(janeiro|fevereiro|mar[çc]o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)$/i;
const CALENDARIO = /^(\d{1,4}( a\.? ?C\.?)?|(s[ée]culo|d[ée]cada|mil[êe]nio|ano) [\dIVXLC]+.*|\d{1,2} de [a-zç]+( de \d{1,4})?|[a-zç]+ de \d{4}|\d{4}s?)$/i;

function conceitosDaAbertura(paragrafos, tituloPagina) {
  // Abertura = 1º parágrafo; se ele tiver poucos links, o 2º completa.
  const ordem = new Map();
  // Links entre parênteses (local e data de nascimento, etimologia) são menos centrais que os do corpo da frase:
  // entram depois dos demais, para não virarem o "conceito principal" de uma pessoa.
  const emParenteses = new Set();
  const marcarParenteses = (no, profundidade = 0) => {
    for (const filho of no.childNodes) {
      if (filho.nodeType === 3) {
        for (const c of filho.data) profundidade += c === '(' ? 1 : c === ')' ? -1 : 0;
        profundidade = Math.max(0, profundidade);
      } else if (filho.nodeType === 1) {
        if (filho.tagName === 'A' && profundidade > 0) emParenteses.add(filho);
        profundidade = marcarParenteses(filho, profundidade);
      }
    }
    return profundidade;
  };
  const considerar = (p) => {
    marcarParenteses(p);
    const links = [...p.querySelectorAll('a[rel="mw:WikiLink"], a[href^="./"]')];
    for (const a of [...links.filter((l) => !emParenteses.has(l)), ...links.filter((l) => emParenteses.has(l))]) {
      if (a.closest('sup, .reference, .mw-ref')) continue;
      const href = a.getAttribute('href') ?? '';
      if (!href.startsWith('./') || /^\.\/[^/#]*:/.test(decodeURIComponent(href))) continue; // Ficheiro:, Categoria:, Wikipédia:...
      const nome = limparTexto(a.getAttribute('title') ?? a.textContent);
      if (!nome || nome.length < 2 || nome.length > 80) continue;
      if (CALENDARIO.test(nome) || MESES.test(nome) || /\(desambigua[çc][ãa]o\)/i.test(nome) || /^Anexo:/i.test(nome)) continue;
      if (normalizar(nome) === normalizar(tituloPagina)) continue;
      const chave = normalizar(nome);
      const atual = ordem.get(chave);
      if (atual) atual.vezes++;
      else ordem.set(chave, { nome, url: new URL(href.split('#')[0], 'https://pt.wikipedia.org/wiki/').href, vezes: 1, posicao: ordem.size });
    }
  };
  considerar(paragrafos[0]);
  if (ordem.size < 8 && paragrafos[1]) considerar(paragrafos[1]);

  const lista = [...ordem.values()].slice(0, MAX_CONCEITOS);
  return lista.map((c, i) => {
    // 1.0 → 0.3 pela ordem em que aparecem; quem é citado mais de uma vez ganha um pequeno reforço
    const base = lista.length === 1 ? 1 : 1 - (0.7 * i) / (lista.length - 1);
    return { nome: c.nome, url: c.url, peso: Math.min(1, Number((base + 0.05 * (c.vezes - 1)).toFixed(3))) };
  }).sort((a, b) => b.peso - a.peso);
}

// ---------- infobox ----------

// Cada linha da infobox é "rótulo | valor". Linhas só com rótulo abrem um grupo ("População"), e as que começam com
// "• " (Total, Urbana, Posição) são subitens dele: viram "População total". Linhas sem rótulo (imagens, legendas) são descartadas.
export function lerInfobox(doc, fonte) {
  const tabela = doc.querySelector('table.infobox, table.infobox_v2, table.infobox_v3');
  if (!tabela) return [];
  const saida = [];
  const vistos = new Set();
  let grupo = '';
  for (const tr of tabela.querySelectorAll('tr')) {
    const th = tr.querySelector(':scope > th');
    const td = tr.querySelector(':scope > td');
    const rotuloBruto = th ? textoCelula(th) : '';
    const valor = td ? textoCelula(td) : '';

    if (!th && /^Coordenadas:/i.test(valor)) {
      adicionar('Coordenadas', valor.replace(/^Coordenadas:\s*/i, ''));
      continue;
    }
    if (!th || !rotuloBruto) continue;
    const subitem = /^\s*[•·▪]/.test(th.textContent.replace(/^\s+/, '')) || /^\s*[•·▪]/.test(rotuloBruto);
    const rotulo = rotuloBruto.replace(/^[•·▪\s]+/, '').trim();
    if (!valor) { // cabeçalho de grupo
      grupo = rotulo.replace(/\s*\(.*?\)/g, '').trim();
      continue;
    }
    if (subitem && grupo) adicionar(`${grupo} ${rotulo.charAt(0).toLowerCase()}${rotulo.slice(1)}`, valor);
    else {
      if (!subitem) grupo = rotulo.replace(/\s*\(.*?\)/g, '').trim();
      adicionar(rotulo, valor);
    }
  }
  return saida.slice(0, MAX_ATRIBUTOS);

  function adicionar(nome, valorTexto) {
    const a = atributo(adaptador, { nome: ajustarPontuacao(nome), valor: ajustarPontuacao(valorTexto), fonte });
    // descarta o que não é dado: vazio, só pontuação, enorme (lista de municípios) ou rótulo sem letras
    if (!a.nome || !a.valor || a.nome.length > 80 || a.valor.length > 250) return;
    if (!/[a-zA-ZÀ-ú0-9]/.test(a.valor) || !/[a-zA-ZÀ-ú]{2,}/.test(a.nome)) return;
    if (/^(mapa|imagem|bandeira|brasão|logotipo|logo|lema)$/i.test(a.nome) && a.valor.length < 3) return;
    const chave = `${a.nome}=${a.valor}`.toLowerCase();
    if (vistos.has(chave)) return;
    vistos.add(chave);
    saida.push(a);
  }
}

// Resíduos de modelos da Wikipédia que o limparTexto do contrato não pega: "( 2026 )", "699 km km", "R$ 53,00 R$".
function ajustarPontuacao(texto) {
  return limparTexto(String(texto)
    .replace(/\(\s+/g, '(').replace(/\s+\)/g, ')')
    .replace(/\b(km|m|ha|hab\.?)(\s+\1\b)+/gi, '$1')
    .replace(/^(R\$.*\d)\s+R\$$/, '$1'));
}

// Texto de uma célula: tira estilos, notas, botões "Expandir lista" e separa itens de lista/quebras de linha com "; ".
function textoCelula(celula) {
  const copia = celula.cloneNode(true);
  copia.querySelectorAll('style, script, sup, .reference, .mw-ref, .mw-collapsible-toggle, .NavToggle, .mw-empty-elt, .noprint, [style*="display:none"], [style*="display: none"], [hidden]').forEach((e) => e.remove());
  copia.querySelectorAll('br').forEach((e) => e.replaceWith(' ; '));
  copia.querySelectorAll('li').forEach((e) => e.append(' ; '));
  const texto = limparTexto(copia.textContent)
    .replace(/^\s*(?:Lista|Ver lista)\s+(?=\S)/i, '')
    .replace(/(\s*;\s*)+$/g, '')
    .replace(/^(\s*;\s*)+/g, '')
    .replace(/\s*;(\s*;)+/g, ';')
    .replace(/\s+;/g, ';');
  return limparTexto(texto);
}
