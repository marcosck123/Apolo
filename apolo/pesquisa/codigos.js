// Limpa transcrições de REPL sem carregar Playwright nos testes do app.
export function limparBloco(texto) {
  if (typeof texto !== 'string' || texto.length > 20_000) return '';
  const linhas = texto.replace(/\r\n?/g, '\n').split('\n');
  const repl = linhas.some((linha) => /^>>> ?/.test(linha));
  return linhas.filter((linha) => !repl || /^(?:>>>|\.\.\.) ?/.test(linha))
    .map((linha) => linha.replace(/^(?:>>>|\.\.\.|\$) ?/, '')).join('\n').trim();
}

export async function coletarCodigos(consulta, { pesquisar, lerBlocos, maxPaginas = 3 }) {
  const resultados = await pesquisar(`${consulta} python`, { max: maxPaginas });
  const vistos = new Set();
  const codigos = [];
  for (const resultado of resultados.slice(0, maxPaginas)) {
    try {
      const pagina = await lerBlocos(resultado.url);
      for (const bloco of pagina.blocos) {
        if (bloco.linguagem && !/python|py\b/i.test(bloco.linguagem)) continue;
        const codigo = limparBloco(bloco.texto);
        if (!codigo || vistos.has(codigo)) continue;
        vistos.add(codigo);
        codigos.push({ linguagem: 'python', codigo, explicacao: bloco.explicacao.slice(0, 1000), fonte: pagina.url });
        if (codigos.length >= 30) return codigos;
      }
    } catch { /* Uma página bloqueada ou fora do ar não elimina as outras fontes. */ }
  }
  return codigos;
}
