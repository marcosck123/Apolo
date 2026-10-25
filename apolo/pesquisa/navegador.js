// O navegador do Apolo: abre o Chromium, pesquisa e lê páginas. Uma só instância, um contexto novo por tarefa.
import { chromium } from 'playwright';
import { desembrulhar, desembrulharBing } from './links.js';
import { urlPermitida } from './rede.js';

const TEMPO_MS = 20_000;
const BLOQUEADOS = new Set(['image', 'media', 'font', 'stylesheet']);

let navegador = null;
async function abrir() {
  if (!navegador || !navegador.isConnected()) {
    navegador = await chromium.launch({ args: ['--no-sandbox'] });
    navegador.on('disconnected', () => { navegador = null; });
  }
  return navegador;
}

// Executa `tarefa(pagina)` numa página isolada, sem cookies e sem acesso à rede interna.
export async function comPagina(tarefa) {
  const contexto = await (await abrir()).newContext({ locale: 'pt-BR', timezoneId: 'America/Porto_Velho' });
  const permitidas = new Map();
  await contexto.route('**/*', async (rota) => {
    const pedido = rota.request();
    if (BLOQUEADOS.has(pedido.resourceType())) return rota.abort();
    const host = new URL(pedido.url()).origin;
    if (!permitidas.has(host)) permitidas.set(host, urlPermitida(pedido.url()));
    return (await permitidas.get(host)) ? rota.continue() : rota.abort();
  });
  try {
    const pagina = await contexto.newPage();
    pagina.setDefaultTimeout(TEMPO_MS);
    return await tarefa(pagina);
  } finally {
    await contexto.close();
  }
}

async function buscarDuckDuckGo(pagina, consulta) {
  await pagina.goto(`https://html.duckduckgo.com/html/?q=${encodeURIComponent(consulta)}&kl=br-pt`, { waitUntil: 'domcontentloaded' });
  const itens = await pagina.$$eval('.result:not(.result--ad)', (els) =>
    els.map((el) => ({
      titulo: el.querySelector('.result__a')?.textContent ?? '',
      href: el.querySelector('.result__a')?.getAttribute('href') ?? '',
      resumo: el.querySelector('.result__snippet')?.textContent ?? '',
    })));
  return itens.map((i) => ({ titulo: i.titulo, url: desembrulhar(i.href), resumo: i.resumo }));
}

async function buscarBing(pagina, consulta) {
  await pagina.goto(`https://www.bing.com/search?q=${encodeURIComponent(consulta)}&setlang=pt-BR&cc=BR`, { waitUntil: 'domcontentloaded' });
  return pagina.$$eval('li.b_algo', (els) =>
    els.map((el) => ({
      titulo: el.querySelector('h2')?.textContent ?? '',
      url: el.querySelector('h2 a')?.getAttribute('href') ?? '',
      resumo: el.querySelector('.b_caption p, p')?.textContent ?? '',
    })))
    .then((itens) => itens.map((i) => ({ ...i, url: desembrulharBing(i.url) })));
}

const limpar = (t) => t.replace(/\s+/g, ' ').trim();

export async function pesquisar(consulta, { max = 5 } = {}) {
  for (const buscar of [buscarDuckDuckGo, buscarBing]) {
    try {
      const itens = await comPagina((p) => buscar(p, consulta));
      const resultados = itens
        .map((i) => ({ titulo: limpar(i.titulo), url: i.url, resumo: limpar(i.resumo) }))
        .filter((i) => i.titulo && i.url && /^https?:/.test(i.url))
        .slice(0, max);
      if (resultados.length) return resultados;
    } catch (erro) {
      console.warn(`${buscar.name} falhou: ${erro.message}`);
    }
  }
  return [];
}

export async function ler(url, { maxCaracteres = 4000 } = {}) {
  if (!(await urlPermitida(url))) throw new Error('endereço não permitido');
  return comPagina(async (pagina) => {
    await pagina.goto(url, { waitUntil: 'domcontentloaded' });
    const texto = await pagina.evaluate(() => {
      for (const el of document.querySelectorAll('script, style, nav, header, footer, aside, form, noscript')) el.remove();
      const raiz = document.querySelector('article, main, #mw-content-text') ?? document.body;
      return raiz.innerText;
    });
    return { titulo: limpar(await pagina.title()), url: pagina.url(), texto: limpar(texto).slice(0, maxCaracteres) };
  });
}

export async function lerBlocos(url) {
  if (!(await urlPermitida(url))) throw new Error('endereço não permitido');
  return comPagina(async (pagina) => {
    await pagina.goto(url, { waitUntil: 'domcontentloaded' });
    const blocos = await pagina.$$eval('pre', (elementos) => elementos.slice(0, 50).map((el) => ({
      texto: (el.textContent ?? '').slice(0, 20_001),
      linguagem: `${el.className} ${el.querySelector('code')?.className ?? ''}`.match(/(?:language|lang)-([\w+-]+)/)?.[1] ?? '',
      explicacao: (() => {
        let anterior = el.previousElementSibling;
        for (let i = 0; anterior && i < 5; i++, anterior = anterior.previousElementSibling) {
          if (anterior.tagName === 'P') return (anterior.textContent ?? '').slice(0, 1000);
        }
        return '';
      })(),
    })));
    return { url: pagina.url(), blocos };
  });
}
