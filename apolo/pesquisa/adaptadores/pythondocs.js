// Adaptador da documentação oficial do Python (docs.python.org), em português quando existe (pt-br) e em inglês quando não.
//
// Como acha a página, sem API de busca (o searchindex.js tem 4 MB e o objects.inv é binário, então ficaram de fora):
//   - "statistics.mean", "json.loads", "os.path.join" → library/<módulo>.html e o id do objeto (dt.sig com id);
//   - "open", "len" (nome solto)                      → library/<nome>.html (módulo), depois as funções embutidas;
//   - "list comprehension", "compreensão de lista"    → glossário (dt#term-...), por id em inglês ou pelo texto.
//   - se o roteador mandar `url` de docs.python.org, vai direto nela.
// Gasta no máximo ORCAMENTO_REQUISICOES por consulta. Se a estrutura da página não for a esperada, devolve menos ou null.
import { atributo, CONFIANCA, fato, limparTexto, pareceFrase } from './contrato.js';

const BASE = 'https://docs.python.org';
const ORCAMENTO_REQUISICOES = 5;
const LICENCA = 'Python Software Foundation License Versão 2; exemplos, receitas e outros códigos na documentação: licença dupla PSF v2 e BSD de Zero Cláusula (desde o Python 3.8.6) — docs.python.org/pt-br/3/license.html';

const adaptador = {
  nome: 'pythondocs',
  licenca: LICENCA,
  tipos: ['codigo', 'definicao'],
  dominios: ['docs.python.org'],
  async extrair({ consulta = '', tema = '', url = null } = {}, ctx) {
    const alvos = url && hospedeiroPython(url) ? [alvoDeUrl(url)].filter(Boolean) : candidatos(tema || consulta, consulta);
    if (!alvos.length) return null;
    let requisicoes = 0;
    const jaVistas = new Map(); // a mesma página (ex.: glossary.html) pode servir a vários candidatos
    const buscarPagina = async (caminho) => {
      if (!jaVistas.has(caminho)) jaVistas.set(caminho, await baixarPagina(caminho));
      return jaVistas.get(caminho);
    };
    const baixarPagina = async (caminho) => {
      // pt-br primeiro; se a página não existir lá, tenta o original em inglês.
      for (const [prefixo, idioma] of [['pt-br/3', 'pt-BR'], ['3', 'en']]) {
        if (requisicoes >= ORCAMENTO_REQUISICOES) return null;
        requisicoes++;
        const endereco = `${BASE}/${prefixo}/${caminho}`;
        const r = await ctx.buscar(endereco);
        if (r.status === 404) continue;
        if (r.status >= 500 || r.status === 429) throw new Error(`docs.python.org respondeu ${r.status}`);
        if (r.status !== 200 || !r.texto) return null;
        return { document: ctx.parsear(r.texto), url: r.url || endereco, idioma };
      }
      return null;
    };
    for (const alvo of alvos) {
      if (requisicoes >= ORCAMENTO_REQUISICOES) break;
      const pagina = await buscarPagina(alvo.caminho);
      if (!pagina) continue;
      const resultado = extrairDaPagina(pagina.document, { ...alvo, url: pagina.url, idioma: pagina.idioma, tema });
      if (resultado) {
        ctx.registrar?.(`pythondocs: ${alvo.caminho}${alvo.id ? '#' + alvo.id : ''} (${pagina.idioma}), ${requisicoes} requisição(ões)`);
        return resultado;
      }
    }
    return null;
  },
};
export default adaptador;

// ───────────────────────── Achar a página ─────────────────────────

const dobrar = (t) => String(t ?? '').toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replace(/\s+/g, ' ').trim();
const OUTRAS_LINGUAGENS = /\b(javascript|typescript|sql|bash|docker|git|node|java|php|ruby|golang|rust)\b/;
const ENFEITES = /\b(como|usar|uso|utilizar|funcao|funcoes|metodo|modulo|biblioteca|classe|em|no|na|do|da|de|o|a|os|as|um|uma|python|py|que|e|sao|significa|exemplo|exemplos|para|fazer|se|faz)\b/g;

// Transforma o tema ("como usar json.loads em python", "list comprehension") em onde procurar. Puro.
export function candidatos(tema, consulta = '') {
  const bruto = dobrar(tema);
  if (!bruto) return [];
  if (OUTRAS_LINGUAGENS.test(dobrar(consulta || tema)) && !/\bpython\b/.test(dobrar(consulta || tema))) return [];
  const pontuado = bruto.match(/[a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)+/);
  const alvos = [];
  const somar = (a) => { if (!alvos.some((x) => x.caminho === a.caminho && x.id === a.id)) alvos.push(a); };
  if (pontuado) {
    const nome = pontuado[0];
    const partes = nome.split('.');
    somar({ caminho: `library/${partes.slice(0, -1).join('.')}.html`, id: nome, tipo: 'objeto' });
    somar({ caminho: `library/${nome}.html`, id: `module-${nome}`, tipo: 'modulo' });
    if (partes.length > 2) somar({ caminho: `library/${partes[0]}.html`, id: nome, tipo: 'objeto' });
    return alvos;
  }
  const limpo = bruto.replace(/\(\)/g, ' ').replace(ENFEITES, ' ').replace(/[^a-z0-9_\s-]/g, ' ').replace(/\s+/g, ' ').trim();
  if (!limpo) return [];
  if (/^[a-z_][a-z0-9_]*$/.test(limpo)) {
    somar({ caminho: `library/${limpo}.html`, id: `module-${limpo}`, tipo: 'modulo' });
    somar({ caminho: 'library/functions.html', id: limpo, tipo: 'objeto' });
  }
  // no glossário o nome pode ter "de"/"da" ("compreensão de lista"), então só tiramos a abertura da pergunta e a palavra "python"
  const frase = bruto.replace(/[^a-z0-9_\s-]/g, ' ').replace(/^\s*(o que (e|sao|significa)|como (usar|fazer)|me explique|explique)\s+(um |uma |o |a )?/, '').replace(/\bpython\b/g, ' ').replace(/\s+/g, ' ').trim();
  for (const termo of new Set([limpo, frase])) {
    if (termo && termo.split(' ').length <= 5) somar({ caminho: 'glossary.html', id: `term-${termo.replace(/\s+/g, '-')}`, termo, tipo: 'glossario' });
  }
  return alvos;
}

export function hospedeiroPython(url) {
  try { return new URL(url).hostname === 'docs.python.org'; } catch { return false; }
}

export function alvoDeUrl(url) {
  try {
    const u = new URL(url);
    const caminho = u.pathname.replace(/^\/(?:pt-br\/)?3(?:\.\d+)?\//, '');
    if (!/\.html$/.test(caminho) || caminho === u.pathname) return null;
    const id = decodeURIComponent(u.hash.replace(/^#/, '')) || null;
    return { caminho, id, tipo: id?.startsWith('term-') ? 'glossario' : id?.startsWith('module-') || !id ? 'modulo' : 'objeto' };
  } catch { return null; }
}

// ───────────────────────── Ler o DOM (funções puras) ─────────────────────────

const PULAR = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE']);
const BLOCOS = new Set(['P', 'LI', 'DIV', 'DD', 'DT', 'BR', 'TR', 'H1', 'H2', 'H3', 'H4', 'PRE']);

// Elemento escondido por atributo, estilo inline ou algum ancestral assim.
export function escondido(el) {
  for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
    if (e.hasAttribute?.('hidden') || e.getAttribute?.('aria-hidden') === 'true') return true;
    const estilo = (e.getAttribute?.('style') ?? '').replace(/\s+/g, '').toLowerCase();
    if (/display:none|visibility:hidden/.test(estilo)) return true;
  }
  return false;
}

// Texto visível de um nó, sem scripts, links de âncora (¶) e partes escondidas.
export function textoVisivel(no) {
  if (!no) return '';
  if (no.nodeType === 3) return no.data ?? '';
  if (no.nodeType !== 1 || PULAR.has(no.tagName)) return '';
  const estilo = (no.getAttribute('style') ?? '').replace(/\s+/g, '').toLowerCase();
  if (no.hasAttribute('hidden') || no.getAttribute('aria-hidden') === 'true' || /display:none|visibility:hidden/.test(estilo)) return '';
  if (/\bheaderlink\b/.test(no.getAttribute('class') ?? '')) return '';
  const dentro = [...no.childNodes].map(textoVisivel).join('');
  return BLOCOS.has(no.tagName) ? ` ${dentro} ` : dentro;
}

const primeiraFrase = (texto) => {
  const t = limparTexto(texto);
  if (t.length <= 400) return t;
  const corte = t.slice(0, 400).search(/[.!?](?=[^.!?]*$)/);
  return corte > 30 ? t.slice(0, corte + 1) : '';
};

// Limpa um bloco de exemplo: tira os prompts >>> e ... e separa a saída colada.
export function limparCodigo(bruto) {
  const linhas = String(bruto ?? '').replace(/\r/g, '').split('\n');
  if (!linhas.some((l) => /^>>> /.test(l) || l === '>>>')) return { codigo: linhas.join('\n').trim(), saida: '' };
  const codigo = [];
  const saida = [];
  for (const linha of linhas) {
    if (/^>>>( |$)/.test(linha)) codigo.push(linha.slice(4));
    else if (/^\.\.\.( |$)/.test(linha) && codigo.length) codigo.push(linha.slice(4));
    else if (linha.trim() === '') codigo.push('');
    else saida.push(linha.trim());
  }
  return { codigo: codigo.join('\n').replace(/\n{3,}/g, '\n\n').trim(), saida: saida.join(' ').slice(0, 200) };
}

const LINGUAGENS = { pycon: 'python', python: 'python', python3: 'python', default: 'python', sh: 'bash', console: 'bash', shell: 'bash', json: 'json', text: 'texto', none: 'texto', c: 'c', rst: 'rst', ini: 'ini', toml: 'toml', xml: 'xml', html: 'html', sql: 'sql', javascript: 'javascript' };
function linguagemDoBloco(bloco) {
  let e = bloco;
  for (let i = 0; i < 3 && e; i++, e = e.parentElement) {
    const m = (e.getAttribute?.('class') ?? '').match(/\bhighlight-([\w+-]+)/);
    if (m) return LINGUAGENS[m[1]] ?? m[1];
  }
  return 'python';
}

function codigosDe(raiz, adaptador, fonte, maximo = 4) {
  const saida = [];
  for (const pre of raiz.querySelectorAll('div.highlight pre')) {
    if (saida.length >= maximo) break;
    if (escondido(pre)) continue;
    const linguagem = linguagemDoBloco(pre);
    const { codigo, saida: resultado } = limparCodigo(textoVisivel(pre).trim());
    if (codigo.length < 4 || codigo.length > 1500 || !/[A-Za-z]/.test(codigo)) continue;
    // a explicação é o parágrafo que vem logo antes do bloco ("Alguns exemplos de uso:")
    let antes = pre.closest('div[class*="highlight-"]') ?? pre.parentElement;
    antes = antes?.previousElementSibling;
    const intro = antes?.tagName === 'P' ? primeiraFrase(textoVisivel(antes)) : '';
    const explicacao = limparTexto([intro, resultado && `Saída: ${resultado}`].filter(Boolean).join(' '));
    if (saida.some((c) => c.codigo === codigo)) continue;
    saida.push({ linguagem, codigo, explicacao, fonte });
  }
  return saida;
}

const assinatura = (dt) => limparTexto(textoVisivel(dt)).replace(/\s*¶$/, '');

// Links do corpo que apontam para outros objetos Python (code.xref.py) viram conceitos.
function conceitosDe(raiz, base, proprioId, maximo = 15) {
  const vistos = new Set();
  const saida = [];
  for (const a of raiz.querySelectorAll('a.reference.internal')) {
    if (saida.length >= maximo) break;
    const code = a.querySelector('code.xref');
    if (!code || escondido(a)) continue;
    const nome = limparTexto(textoVisivel(code));
    const alvo = a.getAttribute('title') || nome;
    if (!nome || nome.length > 60 || vistos.has(alvo) || alvo === proprioId || /^(None|True|False|int|str|float|bool|list|dict|tuple|set|bytes|object)$/.test(nome)) continue;
    vistos.add(alvo);
    let url;
    try { url = new URL(a.getAttribute('href') ?? '', base).href; } catch { url = undefined; }
    saida.push({ nome: alvo.includes('.') ? alvo : nome, ...(url && { url }), peso: 0.5 });
  }
  return saida;
}

function paragrafosDe(raiz, maximo = 3) {
  const saida = [];
  for (const p of [...raiz.children].filter((e) => e.tagName === 'P')) {
    if (saida.length >= maximo) break;
    if (escondido(p)) continue;
    const t = primeiraFrase(textoVisivel(p));
    if (pareceFrase(t) && !/:$/.test(t)) saida.push(t);
  }
  return saida;
}

const porId = (doc, id) => [...doc.querySelectorAll('[id]')].find((e) => e.getAttribute('id') === id) ?? null;

// Dado o documento da página e o alvo, devolve o resultado do contrato ou null.
export function extrairDaPagina(doc, alvo) {
  if (!doc?.querySelector) return null;
  const { id, tipo, url, idioma } = alvo;
  const fonte = id ? `${url.split('#')[0]}#${id}` : url;
  const titulo = limparTexto(textoVisivel(doc.querySelector('h1')));
  let r = null;
  if (tipo === 'objeto') r = lerObjeto(doc, id, url, fonte);
  else if (tipo === 'modulo') r = lerModulo(doc, id, url, fonte);
  else if (tipo === 'glossario') r = lerGlossario(doc, id, alvo.termo, url, fonte);
  if (!r) return null;
  const total = r.fatos.length + r.codigos.length + r.atributos.length;
  if (!total) return null;
  return { fatos: r.fatos, conceitos: r.conceitos, pares: [], codigos: r.codigos, atributos: r.atributos, metadados: { titulo: r.titulo ?? titulo, idioma, url: fonte } };
}

function lerObjeto(doc, id, url, fonte) {
  const dt = id && porId(doc, id);
  if (!dt || dt.tagName !== 'DT' || escondido(dt)) return null;
  const dd = dt.nextElementSibling?.tagName === 'DD' ? dt.nextElementSibling : null;
  if (!dd) return null;
  const sig = assinatura(dt);
  const frases = paragrafosDe(dd);
  const fatos = frases.map((texto, i) => fato(adaptador, { texto, secao: id, fonte, confianca: i === 0 ? CONFIANCA.alta : CONFIANCA.media }));
  const atributos = [atributo(adaptador, { nome: `${id} (assinatura)`, valor: sig, fonte })];
  // métodos e atributos aninhados no corpo (classes): cada dt com id vira atributo
  for (const sub of dd.querySelectorAll('dt.sig[id]')) {
    if (atributos.length >= 20) break;
    const sid = sub.getAttribute('id');
    if (sid && !escondido(sub)) atributos.push(atributo(adaptador, { nome: `${sid} (assinatura)`, valor: assinatura(sub), fonte: `${url.split('#')[0]}#${sid}` }));
  }
  return { fatos, atributos, codigos: codigosDe(dd, adaptador, fonte), conceitos: conceitosDe(dd, url, id), titulo: id };
}

function lerModulo(doc, id, url, fonte) {
  const secao = id && porId(doc, id);
  if (!secao || secao.tagName !== 'SECTION' || escondido(secao)) return null;
  const nome = id.replace(/^module-/, '');
  const frases = paragrafosDe(secao, 3);
  const fatos = frases.map((texto, i) => fato(adaptador, { texto, secao: nome, fonte, confianca: i === 0 ? CONFIANCA.alta : CONFIANCA.media }));
  const atributos = [];
  for (const dt of secao.querySelectorAll('dt.sig[id]')) {
    if (atributos.length >= 25) break;
    const sid = dt.getAttribute('id');
    if (sid && !escondido(dt)) atributos.push(atributo(adaptador, { nome: `${sid} (assinatura)`, valor: assinatura(dt), fonte: `${url.split('#')[0]}#${sid}` }));
  }
  return { fatos, atributos, codigos: codigosDe(secao, adaptador, fonte, 3), conceitos: conceitosDe(secao, url, nome), titulo: nome };
}

function lerGlossario(doc, id, termo, url) {
  const procurado = dobrar(termo ?? '');
  const dts = [...doc.querySelectorAll('dl.glossary > dt[id^="term-"], dt[id^="term-"]')].filter((d) => !escondido(d));
  const dt = dts.find((d) => d.getAttribute('id') === id)
    ?? (procurado ? dts.find((d) => dobrar(textoVisivel(d)).replace(/¶/g, '').trim() === procurado) : null);
  if (!dt) return null;
  const dd = dt.nextElementSibling?.tagName === 'DD' ? dt.nextElementSibling : null;
  if (!dd) return null;
  const sid = dt.getAttribute('id');
  const fonte = `${url.split('#')[0]}#${sid}`;
  const nome = limparTexto(textoVisivel(dt));
  const frases = paragrafosDe(dd, 2);
  const fatos = frases.map((texto, i) => fato(adaptador, { texto: i === 0 ? `${nome}: ${texto}` : texto, secao: 'Glossário', fonte, confianca: CONFIANCA.alta }));
  return { fatos: fatos.filter((f) => pareceFrase(f.texto)), atributos: [], codigos: codigosDe(dd, adaptador, fonte, 3), conceitos: conceitosDe(dd, url, sid), titulo: nome };
}
