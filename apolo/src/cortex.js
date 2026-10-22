// Lobo frontal: o córtex próprio do Apolo (cortex_v0.py, servido por `python cortex_v0.py servir`).
// Plugado em `criarApolo` como `raciocinar`. É um modelo de linguagem puro, não um assistente:
// ele continua um texto. Então o "prompt" é a memória ativada seguida da mensagem, e a resposta
// é o que o córtex escreve a seguir. Ele só enxerga os últimos `contexto` caracteres, por isso a
// ordem importa: memória menos ativa primeiro, mais ativa e a mensagem por último.

export function montarPrompt({ mensagem, memoria }) {
  const lembrancas = [...memoria]
    .sort((a, b) => a.ativacao - b.ativacao)
    .map((n) => n.conteudo.split('\n')[0]);
  return [...lembrancas, mensagem].join('\n') + '\n';
}

export function criarRaciocinador({
  url = process.env.CORTEX_URL,
  maxCaracteres = 80,
  temperatura = 0.8,
  fetchFn = fetch,
} = {}) {
  if (!url) return null;

  return async function raciocinar({ mensagem, memoria }) {
    try {
      const resposta = await fetchFn(new URL('/gerar', url), {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ inicio: montarPrompt({ mensagem, memoria }), n: maxCaracteres, temperatura }),
        signal: AbortSignal.timeout(120_000),
      });
      if (!resposta.ok) throw new Error(`córtex respondeu ${resposta.status}: ${await resposta.text()}`);
      const { texto } = await resposta.json();
      // Treinado com diálogos, o córtex segue escrevendo outras perguntas; a resposta é o 1º parágrafo.
      return texto.trim().split('\n\n')[0].trim() || null;
    } catch (erro) {
      // O córtex é opcional: se estiver fora do ar, o Apolo ainda lembra e aprende, só não responde.
      console.warn(`córtex indisponível: ${erro.message}`);
      return null;
    }
  };
}
