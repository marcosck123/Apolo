// Stack Overflow (em inglês e em português): respostas ACEITAS pela API pública do Stack Exchange.
// Embrulha a lógica de ../stackexchange.js (extração dos blocos, palavras da busca, entidades HTML) no contrato dos
// adaptadores; a diferença é que a rede passa por `ctx.buscar` (cache de 10 min e proteção SSRF) em vez de `fetch` direto.
//
// Licença: o conteúdo enviado ao Stack Overflow é CC BY-SA 4.0 (posts anteriores a maio de 2018 estão sob a 3.0);
// a atribuição exige o link da pergunta, que vai em `fonte` de cada item.
// Educação com a API: no máximo 4 requisições por chamada (2 sites × busca + respostas), sem chave, respeitando `backoff`.
import { par, resultadoVazio } from './contrato.js';
import { decodificar, extrairBlocos, palavrasDaBusca } from '../stackexchange.js';

const API = 'https://api.stackexchange.com/2.3';
const LINGUAGENS = { python: 'python', javascript: 'javascript', typescript: 'typescript', sql: 'sql', bash: 'bash', git: 'git', docker: 'docker', java: 'java', node: 'node.js', nodejs: 'node.js', rust: 'rust', golang: 'go', php: 'php', css: 'css', html: 'html' };
// A API procura por palavras: o que sobra de uma pergunta em inglês também precisa perder as palavras de ligação.
const FILLER_EN = new Set(['how', 'to', 'the', 'in', 'of', 'do', 'does', 'i', 'is', 'what', 'can', 'you', 'my', 'it', 'an', 'on', 'for', 'with', 'using', 'use', 'get', 'way', 'there', 'are', 'and']);
const INGLES = /\b(how|what|the|to|in|of|do|can|with|using|string|list|array)\b/i;

const adaptador = {
  nome: 'stackoverflow',
  licenca: 'CC BY-SA 4.0',
  tipos: ['codigo'],
  dominios: ['stackoverflow.com', 'pt.stackoverflow.com'],
  async extrair({ consulta, tema }, ctx) {
    const texto = String(consulta ?? tema ?? '');
    const q = palavrasDaBusca(texto).split(' ').filter((p) => !FILLER_EN.has(p)).join(' ');
    if (!q) return null;
    const linguagem = Object.entries(LINGUAGENS).find(([chave]) => new RegExp(`\\b${chave}\\b`, 'i').test(texto))?.[1] ?? 'python';
    const sites = INGLES.test(texto) && !/\b(como|uma|em|para|qual)\b/i.test(texto) ? ['stackoverflow', 'pt.stackoverflow'] : ['pt.stackoverflow', 'stackoverflow'];
    return buscarNosSites({ q, linguagem, sites }, ctx, adaptador);
  },
};
export default adaptador;

// Ponte para ctx.buscar: mesma validação do pegarJson de stackexchange.js (status HTTP e `error_message`).
async function pegarJson(url, ctx) {
  const r = await ctx.buscar(url, { json: true });
  if (r.status === 400 || r.status === 429 || r.status === 502) throw new Error(`stackexchange respondeu ${r.status}${r.texto ? `: ${String(r.texto).slice(0, 120)}` : ''}`);
  if (r.ok === false || (r.status && r.status >= 400)) throw new Error(`stackexchange respondeu ${r.status}`);
  const dados = r.json();
  if (dados.error_message) throw new Error(dados.error_message);
  if (dados.backoff) ctx.registrar?.(`stackoverflow: a API pediu espera de ${dados.backoff}s`);
  return dados;
}

// Texto da resposta sem HTML e sem os blocos de código, no máximo `max` caracteres (cortando em fim de frase quando der).
export function textoDaResposta(html, max = 300) {
  const limpo = decodificar(String(html ?? '').replace(/<pre[\s\S]*?<\/pre>/g, ' ').replace(/<\/(p|li|h\d|blockquote)>/g, '$& ').replace(/<[^>]+>/g, ''))
    .replace(/\s+/g, ' ').trim();
  if (limpo.length <= max) return limpo;
  const corte = limpo.slice(0, max);
  const fim = Math.max(corte.lastIndexOf('. '), corte.lastIndexOf('? '), corte.lastIndexOf('! '));
  return fim > max * 0.4 ? corte.slice(0, fim + 1) : `${corte.slice(0, max - 1).replace(/\s+\S*$/, '')}…`;
}

// A busca por relevância devolve vizinhos fracos ("converter inteiro em string" para "inverter string"): a pergunta só
// vale se o título tiver pelo menos 60% das palavras buscadas (comparando os 5 primeiros caracteres, para pegar plurais).
const semAcento = (t) => String(t).toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replace(/[^a-z0-9\s]/g, ' ');
export function tituloCombina(titulo, q) {
  const palavras = q.split(' ').filter(Boolean);
  const doTitulo = semAcento(decodificar(titulo)).split(/\s+/).filter(Boolean);
  const achadas = palavras.filter((p) => doTitulo.some((t) => t.startsWith(p.slice(0, 5)) || p.startsWith(t.slice(0, 5)) && t.length >= 4)).length;
  return achadas >= Math.ceil(palavras.length * 0.6);
}

export async function buscarNosSites({ q, linguagem, sites }, ctx, adp = adaptador) {
  const saida = resultadoVazio();
  const falhas = [];
  let respondeu = false;
  for (const site of sites) {
    try {
      const busca = await pegarJson(`${API}/search/advanced?order=desc&sort=relevance&q=${encodeURIComponent(q)}&tagged=${encodeURIComponent(linguagem)}&accepted=True&site=${site}&pagesize=3`, ctx);
      respondeu = true;
      const aceitas = (busca.items ?? []).filter((i) => i.accepted_answer_id && tituloCombina(i.title, q));
      if (!aceitas.length) continue;
      const respostas = await pegarJson(`${API}/answers/${aceitas.map((i) => i.accepted_answer_id).join(';')}?site=${site}&filter=withbody`, ctx);
      const porId = new Map((respostas.items ?? []).map((r) => [r.answer_id, r.body]));
      for (const pergunta of aceitas) {
        const corpo = porId.get(pergunta.accepted_answer_id) ?? '';
        const titulo = decodificar(pergunta.title ?? '');
        let blocos = 0;
        for (const bloco of extrairBlocos(corpo)) {
          if (blocos >= 3 || saida.codigos.length >= 12) break;
          if (bloco.texto.length < 8 || bloco.texto.length > 3000) continue;
          saida.codigos.push({ linguagem: linguagem === 'node.js' ? 'javascript' : linguagem, codigo: bloco.texto, explicacao: bloco.explicacao || titulo, fonte: pergunta.link });
          blocos++;
        }
        const resposta = textoDaResposta(corpo, 300);
        if (titulo && resposta.length >= 30 && saida.pares.length < 6) saida.pares.push(par(adp, { pergunta: titulo, resposta, fonte: pergunta.link }));
        for (const tag of pergunta.tags ?? []) {
          if (tag === linguagem || saida.conceitos.length >= 10 || saida.conceitos.some((c) => c.nome === tag)) continue;
          saida.conceitos.push({ nome: tag, peso: 0.4 });
        }
      }
      saida.metadados = saida.metadados.url ? saida.metadados : { titulo: `Stack Overflow: ${q}`, idioma: site.startsWith('pt.') ? 'pt' : 'en', url: aceitas[0].link };
    } catch (erro) {
      falhas.push(`${site}: ${erro.message}`);
      ctx.registrar?.(`stackoverflow: ${site} falhou: ${erro.message}`);
    }
    if (saida.codigos.length >= 3 || saida.pares.length >= 3) break; // já bastou: o segundo site só entra se o primeiro não deu nada
  }
  if (!respondeu && falhas.length) throw new Error(falhas.join(' | '));
  return saida.codigos.length || saida.pares.length ? saida : null;
}
