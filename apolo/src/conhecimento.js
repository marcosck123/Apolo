// Aprender sozinho: pergunta de fato sem resposta na memória → o serviço `pesquisa` consulta os adaptadores
// (Wikipédia, IBGE, MDN...) → o Apolo confere, guarda como fatos `web` (não verificados) e responde com a fonte.
// Sem modelo "entendendo": só fontes, regras e comparação, tudo testável com resultados de mentira.
import { palavrasChave } from './raciocinio.js';

// Adaptadores de fonte estruturada: o que vem deles entra sem precisar de uma segunda fonte concordando.
const CONFIAVEIS = new Set(['wikipedia', 'wikidata', 'ibge', 'mdn', 'stackoverflow', 'pythondocs']);
// Calculadoras e sites de resultado genérico, aprendidos com buscas que já deram errado.
const SPAM = /calcul|calc-|solvecalc|w3calc|okcalc|mobills|4devs|online-python/i;

const dominio = (url) => {
  try { return new URL(url).hostname.replace(/^www\./, ''); } catch { return ''; }
};
const numeros = (texto) => new Set((texto.match(/\d[\d.,]*\d|\d/g) ?? []).map((n) => n.replace(/[.,]/g, '')));
const interseccao = (a, b) => [...a].filter((x) => b.has(x));

export function criarConhecedor({ url = process.env.PESQUISA_URL, fetchFn = fetch } = {}) {
  if (!url || process.env.PESQUISA_AUTO === '0') return null;
  return async function conhecer(consulta) {
    try {
      const resposta = await fetchFn(new URL('/conhecer', url), {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ consulta }),
        signal: AbortSignal.timeout(60_000),
      });
      if (!resposta.ok) throw new Error(`pesquisa respondeu ${resposta.status}`);
      return await resposta.json();
    } catch (erro) {
      console.warn(`conhecimento indisponível: ${erro.message}`);
      return null;
    }
  };
}

// No máximo `max` pesquisas automáticas por janela: cada uma abre a rede e pode levar vários segundos.
export function criarLimitador({ max = 6, janelaMs = 60_000, agora = Date.now } = {}) {
  const marcas = [];
  return () => {
    const t = agora();
    while (marcas.length && t - marcas[0] > janelaMs) marcas.shift();
    if (marcas.length >= max) return false;
    marcas.push(t);
    return true;
  };
}

const confiavel = (f) => CONFIAVEIS.has(f.adaptador) || f.confianca === 'alta';

// Etapa 5: só passa o que dá para confiar um pouco. Devolve os fatos aceitos, em ordem de qualidade.
export function verificarFatos(resultado, { acordoMinimo = 0.4, termosEmComum = 3 } = {}) {
  const tema = palavrasChave(resultado.tema ?? '');
  const todos = (resultado.fatos ?? [])
    .filter((f) => f?.texto && f.fonte && !SPAM.test(dominio(f.fonte)))
    .map((f, posicao) => ({ ...f, posicao, termos: palavrasChave(f.texto), numeros: numeros(f.texto) }));
  const mencionaTema = (f) => !tema.size || [...tema].every((t) => f.termos.has(t));
  const semTema = (f) => new Set([...f.termos].filter((t) => !tema.has(t)));

  const concordancia = (a, b) => {
    const A = semTema(a), B = semTema(b);
    const comum = interseccao(A, B).length;
    return { comum, razao: comum / Math.max(1, Math.min(A.size, B.size)) };
  };
  const outraFonte = (a, b) => b !== a && dominio(b.fonte) !== dominio(a.fonte);

  // Números ou datas que se contradizem entre fontes que falam da mesma coisa derrubam a de menos confiança.
  const contraditos = new Set();
  for (const a of todos) {
    for (const b of todos) {
      if (!outraFonte(a, b) || !a.numeros.size || !b.numeros.size) continue;
      if (concordancia(a, b).comum >= termosEmComum && !interseccao(a.numeros, b.numeros).length) {
        if (!confiavel(a) || confiavel(b)) contraditos.add(a);
      }
    }
  }

  const apoiado = (f) => todos.some((g) => {
    if (!outraFonte(f, g) || !mencionaTema(g)) return false;
    const c = concordancia(f, g);
    return c.comum >= termosEmComum && c.razao >= acordoMinimo;
  });
  const aceitos = todos.filter((f) => !contraditos.has(f) && (confiavel(f) || (mencionaTema(f) && apoiado(f))));

  const nota = (f) => (mencionaTema(f) ? 2 : 0) + (confiavel(f) ? 2 : 0) + 1 / (1 + f.posicao) + (f.texto.length >= 60 && f.texto.length <= 220 ? 1 : 0);
  return aceitos.sort((a, b) => nota(b) - nota(a));
}

const cortar = (texto, max) => (texto.length > max ? `${texto.slice(0, max - 1).trimEnd()}…` : texto);

// Etapas 4 a 6: escolhe, guarda e responde. `lembrar` é apolo.lembrar; `jaExiste` evita duplicar o que já foi aprendido.
export function criarAprendizadoAutomatico({ conhecer, lembrar, jaExiste = async () => false, registrar = () => {}, limitador = () => true, maxFatos = 3 }) {
  return async function aprender(mensagem) {
    if (!conhecer) return null;
    if (!limitador()) return 'Pesquisei bastante agora há pouco; pergunte de novo em um minuto.';
    const resultado = await conhecer(mensagem);
    if (!resultado) return null;

    const tema = resultado.tema || mensagem;
    const titulo = resultado.metadados?.titulo || tema;
    // No máximo 2 frases por fonte, para uma página comprida não encher a memória sozinha.
    const porFonte = new Map();
    const escolhidos = verificarFatos(resultado).filter((f) => {
      const d = dominio(f.fonte);
      porFonte.set(d, (porFonte.get(d) ?? 0) + 1);
      return porFonte.get(d) <= 2;
    }).slice(0, maxFatos);

    const itens = escolhidos.map((f) => ({ tipo: 'fato', conteudo: `${f.secao ? `${titulo} – ${f.secao}` : titulo} :: ${f.texto} (fonte: ${f.fonte})` }));
    // Dados exatos (infobox, Wikidata, IBGE) vêm de fonte estruturada.
    for (const a of (resultado.atributos ?? []).filter((x) => x?.valor && x.fonte && !SPAM.test(dominio(x.fonte))).slice(0, 5)) {
      itens.push({ tipo: 'fato', conteudo: `${titulo} :: ${a.nome}: ${a.valor}. (fonte: ${a.fonte})` });
    }
    // Perguntas e respostas prontas (FAQ).
    for (const p of (resultado.pares ?? []).filter((x) => x?.pergunta && x.resposta && x.fonte && !SPAM.test(dominio(x.fonte))).slice(0, 2)) {
      itens.push({ tipo: 'fato', conteudo: `${p.pergunta} :: ${p.resposta} (fonte: ${p.fonte})` });
    }
    // Conceitos relacionados: `lembrar` os liga por sinapse aos neurônios parecidos, inclusive aos fatos acima.
    const conceitos = (resultado.conceitos ?? []).filter((c) => c?.nome).sort((a, b) => (b.peso ?? 0) - (a.peso ?? 0)).slice(0, 5);

    if (!itens.length) {
      registrar('pesquisou', { texto: mensagem, achados: 0, guardados: 0, automatica: true, fontes: [] });
      return `Pesquisei, mas não achei nada confiável sobre ${tema}.`;
    }

    let guardados = 0;
    for (const item of itens) {
      if (await jaExiste(item.conteudo)) continue;
      await lembrar({ ...item, origem: 'web' });
      guardados++;
    }
    for (const c of conceitos) {
      const conteudo = `${c.nome} :: Tema relacionado a ${tema}.${c.url ? ` (fonte: ${c.url})` : ''}`;
      if (!(await jaExiste(conteudo))) await lembrar({ tipo: 'conceito', conteudo, origem: 'web' });
    }
    registrar('pesquisou', { texto: mensagem, achados: itens.length, guardados, automatica: true, fontes: [...new Set(escolhidos.map((f) => f.fonte))] });

    const frases = escolhidos.slice(0, 2).map((f) => `${cortar(f.texto, 240)} (fonte: ${dominio(f.fonte)})`);
    const resposta = frases.length ? frases.join(' ') : cortar(itens[0].conteudo.split(' :: ')[1].replace(/ \(fonte:.*$/, ''), 240);
    return `${resposta}\nPesquisei na internet para responder; esta informação ainda não foi verificada.`;
  };
}
