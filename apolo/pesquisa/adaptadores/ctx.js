// O que os adaptadores recebem para trabalhar: rede educada e segura, DOM e (só se preciso) o navegador.
import { parseHTML } from 'linkedom';
import { urlPermitida } from '../rede.js';

const USER_AGENT = 'ApoloBot/0.1 (projeto pessoal de pesquisa; uma página por vez; contato: github.com/marcosck123/Apolo)';
const CACHE = new Map();
const TEMPO_CACHE_MS = 10 * 60_000;

export function criarCtx({ fetchFn = fetch, navegador = null, registrar = () => {}, tempoMs = 15_000 } = {}) {
  return {
    async buscar(url, { json = false, cabecalhos = {} } = {}) {
      if (!(await urlPermitida(url))) throw new Error(`endereço não permitido: ${url}`);
      const chave = `${json ? 'j' : 't'}:${url}`;
      const guardado = CACHE.get(chave);
      if (guardado && Date.now() - guardado.em < TEMPO_CACHE_MS) return guardado.valor;
      const resposta = await fetchFn(url, {
        signal: AbortSignal.timeout(tempoMs),
        headers: { 'user-agent': USER_AGENT, accept: json ? 'application/json' : 'text/html,application/xhtml+xml', 'accept-language': 'pt-BR,pt;q=0.9,en;q=0.5', ...cabecalhos },
        redirect: 'follow',
      });
      const texto = await resposta.text();
      const valor = { status: resposta.status, ok: resposta.ok, url: resposta.url, texto, json: () => JSON.parse(texto) };
      if (resposta.ok) CACHE.set(chave, { em: Date.now(), valor });
      return valor;
    },
    parsear: (html) => parseHTML(html).document,
    navegador: navegador ?? (async () => { throw new Error('navegador indisponível neste contexto'); }),
    registrar,
  };
}
