// Olhos do Apolo: "pesquise X" abre o navegador (serviço pesquisa, Playwright), lê os resultados,
// guarda o que achou como fatos na memória e responde com o melhor resumo e a fonte.
const PEDIDO = /^\s*(?:por favor,?\s*)?(?:pesquis(?:a|e|ar)|busc(?:a|ar)|busque|procur(?:a|e|ar))\s+(?:(?:na|pela)\s+(?:internet|web)\s+)?(?:(?:sobre|por|pelo|pela|a respeito de)\s+)?(?:(?:a|o|as|os|um|uma)\s+)?(.{2,200}?)[\s.!?]*$/iu;

// Devolve o assunto do pedido de pesquisa, ou null se a mensagem não for um pedido.
// O artigo do começo sai: "a capital de Rondônia" faz o buscador devolver mapas, "capital de Rondônia" devolve a resposta.
export function extrairConsulta(mensagem) {
  return mensagem.match(PEDIDO)?.[1].trim() ?? null;
}

export function criarPesquisador({ url = process.env.PESQUISA_URL, fetchFn = fetch } = {}) {
  if (!url) return null;

  return async function pesquisar(consulta) {
    try {
      const resposta = await fetchFn(new URL('/pesquisar', url), {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ consulta, max: 5 }),
        signal: AbortSignal.timeout(60_000),
      });
      if (!resposta.ok) throw new Error(`pesquisa respondeu ${resposta.status}: ${await resposta.text()}`);
      return (await resposta.json()).resultados;
    } catch (erro) {
      // A pesquisa é opcional: sem o navegador, o Apolo continua lembrando e conversando.
      console.warn(`pesquisa indisponível: ${erro.message}`);
      return null;
    }
  };
}

const dominio = (url) => new URL(url).hostname.replace(/^www\./, '');
const cortar = (texto, max) => (texto.length > max ? `${texto.slice(0, max - 1).trimEnd()}…` : texto);

// pesquisador: o de cima (ou null); lembrar: apolo.lembrar; registrar: log.registrar.
export function criarPesquisa({ pesquisador, lembrar, registrar, maxFatos = 3 }) {
  return async function responder(consulta) {
    if (!pesquisador) return 'Não estou conectado à internet agora.';
    const resultados = await pesquisador(consulta);
    if (!resultados) return 'Não consegui pesquisar agora, tente de novo daqui a pouco.';

    const uteis = resultados.filter((r) => r.resumo);
    registrar('pesquisou', { texto: consulta, achados: resultados.length, fontes: resultados.map((r) => r.url) });
    if (uteis.length === 0) return `Não achei nada útil sobre "${consulta}".`;

    for (const r of uteis.slice(0, maxFatos)) {
      await lembrar({ conteudo: `${r.titulo} :: ${r.resumo} (fonte: ${r.url})`, tipo: 'fato', origem: 'web' });
    }
    const melhor = uteis[0];
    return `${cortar(melhor.resumo, 280)} (fonte: ${dominio(melhor.url)})`;
  };
}
