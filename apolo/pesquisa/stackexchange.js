// Código confiável para o Apolo: respostas aceitas do Stack Overflow (inglês e português) pela API pública.
// O texto das respostas é CC BY-SA, então cada candidato carrega o link da pergunta como fonte.
const API = 'https://api.stackexchange.com/2.3';
const SITES = ['pt.stackoverflow', 'stackoverflow'];

const ENTIDADES = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ' };
export const decodificar = (texto) => texto
  .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
  .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)))
  .replace(/&([a-z]+);/gi, (m, nome) => ENTIDADES[nome.toLowerCase()] ?? m);

const semTags = (html) => decodificar(html.replace(/<[^>]+>/g, '')).replace(/\s+/g, ' ').trim();

// Os blocos de código vêm como <pre><code>...</code></pre>; o parágrafo anterior serve de explicação.
export function extrairBlocos(html) {
  const blocos = [];
  for (const m of html.matchAll(/<pre[^>]*>\s*<code[^>]*>([\s\S]*?)<\/code>\s*<\/pre>/g)) {
    const antes = html.slice(0, m.index);
    const paragrafo = [...antes.matchAll(/<p>([\s\S]*?)<\/p>/g)].pop()?.[1] ?? '';
    blocos.push({ texto: decodificar(m[1].replace(/<[^>]+>/g, '')).trim(), explicacao: semTags(paragrafo).slice(0, 1000) });
  }
  return blocos;
}

// "como calcular a média de uma lista em python" → "calcular média lista": a API procura por palavras, não por frase.
const FILLER = new Set(['como', 'a', 'o', 'as', 'os', 'um', 'uma', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'com', 'para', 'pra', 'python', 'qual', 'quais', 'faco', 'fazer', 'posso', 'eu', 'e', 'que', 'se']);
export const palavrasDaBusca = (mensagem) =>
  mensagem.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/).filter((p) => p && !FILLER.has(p)).slice(0, 6).join(' ');

async function pegarJson(url, fetchFn) {
  const resposta = await fetchFn(url, { signal: AbortSignal.timeout(15_000), headers: { accept: 'application/json' } });
  if (!resposta.ok) throw new Error(`stackexchange respondeu ${resposta.status}`);
  const dados = await resposta.json();
  if (dados.error_message) throw new Error(dados.error_message);
  return dados;
}

export async function codigosDoStackExchange(mensagem, { fetchFn = fetch, sites = SITES, perguntas = 3, maximo = 20 } = {}) {
  const q = palavrasDaBusca(mensagem);
  if (!q) return [];
  const candidatos = [];
  for (const site of sites) {
    try {
      const busca = await pegarJson(`${API}/search/advanced?order=desc&sort=relevance&q=${encodeURIComponent(q)}&tagged=python&accepted=True&site=${site}&pagesize=${perguntas}`, fetchFn);
      const aceitas = busca.items.filter((i) => i.accepted_answer_id);
      if (!aceitas.length) continue;
      const ids = aceitas.map((i) => i.accepted_answer_id).join(';');
      const respostas = await pegarJson(`${API}/answers/${ids}?site=${site}&filter=withbody`, fetchFn);
      const porId = new Map(respostas.items.map((r) => [r.answer_id, r.body]));
      for (const pergunta of aceitas) {
        for (const bloco of extrairBlocos(porId.get(pergunta.accepted_answer_id) ?? '')) {
          if (bloco.texto) candidatos.push({ linguagem: 'python', codigo: bloco.texto, explicacao: bloco.explicacao, fonte: pergunta.link });
        }
      }
    } catch { /* um site fora do ar ou sem cota não impede o outro */ }
    if (candidatos.length >= maximo) break;
  }
  return candidatos.slice(0, maximo);
}
