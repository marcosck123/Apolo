// DuckDuckGo devolve o destino embrulhado em //duckduckgo.com/l/?uddg=<url>.
export function desembrulhar(href) {
  try {
    const url = new URL(href, 'https://duckduckgo.com');
    return url.searchParams.get('uddg') ?? url.href;
  } catch {
    return null;
  }
}

// O Bing embrulha o destino em bing.com/ck/a?...&u=a1<url em base64>.
export function desembrulharBing(href) {
  try {
    const url = new URL(href);
    if (!/(^|\.)bing\.com$/.test(url.hostname) || !url.pathname.startsWith('/ck/')) return href;
    const codificado = url.searchParams.get('u');
    if (!codificado?.startsWith('a1')) return href;
    return Buffer.from(codificado.slice(2), 'base64url').toString('utf8');
  } catch {
    return href;
  }
}
