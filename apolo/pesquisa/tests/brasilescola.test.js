import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { criarCtx } from '../adaptadores/ctx.js';
import brasilescola, { dataIso, extrairArtigo, frases, pareceNomeValor, slugDoTema, tituloCombina } from '../adaptadores/brasilescola.js';

const html = readFileSync(new URL('./fixtures/brasilescola/rondonia.html', import.meta.url), 'utf8');
const URL_RO = 'https://brasilescola.uol.com.br/brasil/rondonia.htm';
const { parsear } = criarCtx();

function ctxFalso(paginas) {
  const pedidos = [];
  return {
    pedidos, parsear, registrar: () => {},
    buscar: async (url) => {
      pedidos.push(url);
      return url in paginas ? { status: 200, ok: true, url, texto: paginas[url] } : { status: 404, ok: false, url, texto: '<h1>Não encontrado</h1>' };
    },
  };
}
const ler = (h = html) => extrairArtigo(parsear(h), { adaptador: brasilescola, url: URL_RO, resumo: 'p.resumo-artigo' });

test('Rondônia: metadados do JSON-LD (data torta vira ISO) e licença honesta', async () => {
  const r = await brasilescola.extrair({ url: URL_RO }, ctxFalso({ [URL_RO]: html }));
  assert.equal(r.metadados.titulo, 'Rondônia (RO): capital, mapa, bandeira, economia');
  assert.equal(r.metadados.data, '2024-08-28');
  assert.equal(r.metadados.autor, 'Paloma Guitarrara');
  assert.equal(r.metadados.idioma, 'pt-BR');
  assert.equal(r.metadados.url, URL_RO);
  assert.match(brasilescola.licenca, /Todos os direitos reservados/);
  assert.ok(r.fatos.every((f) => f.licenca === brasilescola.licenca && f.fonte === URL_RO && f.adaptador === 'brasilescola'));
  assert.equal(dataIso('2008-02-09-0309:27:58'), '2008-02-09');
  assert.equal(dataIso('lixo'), undefined);
});

test('Rondônia: resumo, abertura e uma frase por seção, todas curtas e sem ruído', () => {
  const r = ler();
  const por = (s) => r.fatos.find((f) => f.secao === s);
  assert.equal(por('Resumo').texto, 'Rondônia é um estado brasileiro da região Norte.');
  assert.match(por('Abertura').texto, /^Rondônia é uma das 27 unidades de federação do Brasil/);
  assert.equal(por('Abertura').confianca, 'media'); // tem "é": parece definição
  assert.match(por('Clima de Rondônia').texto, /Equatorial Quente e Úmido/);
  assert.match(por('Demografia de Rondônia').texto, /1\.581\.196 habitantes/);
  assert.ok(r.fatos.length >= 12);
  for (const f of r.fatos) {
    assert.ok(f.texto.length >= 30 && f.texto.length <= 400, f.texto);
    assert.ok(!/Anuncie|Tópicos deste artigo|Leia também|Dados gerais de Rondônia/.test(f.texto), f.texto);
  }
  assert.equal(new Set(r.fatos.map((f) => f.texto)).size, r.fatos.length);
  assert.ok(!r.fatos.some((f) => /^Tópicos/.test(f.secao ?? '')));
});

test('Rondônia: FAQPage vira par e "Dados gerais" viram atributos', () => {
  const r = ler();
  assert.deepEqual(r.pares.map((p) => [p.pergunta, p.resposta]), [['Qual é a capital de Rondônia?', 'Capital: Porto Velho']]);
  const attr = Object.fromEntries(r.atributos.map((a) => [a.nome, a.valor]));
  assert.equal(attr['Capital'], 'Porto Velho');
  assert.equal(attr['Região'], 'Norte');
  assert.equal(attr['Área territorial'], '237.754,17 km² (IBGE, 2022)');
  assert.equal(attr['População'], '1.581.196 habitantes (IBGE, 2022)');
  assert.ok(!('Anuncie' in attr));
});

test('Rondônia: conceitos do negrito de abertura e do caminho de navegação', () => {
  const nomes = ler().conceitos.map((c) => c.nome);
  assert.ok(nomes.includes('Rondônia'));
  assert.ok(nomes.includes('Região Norte'));
  assert.ok(nomes.includes('Geografia do Brasil'));
  assert.ok(!nomes.some((n) => /^egião|integra a$/i.test(n)), nomes.join(' | ')); // pedaços de palavra partida em dois <strong>
  const norte = ler().conceitos.find((c) => c.nome === 'Região Norte');
  assert.equal(norte.url, 'https://brasilescola.uol.com.br/brasil/regiao-norte.htm');
});

test('descrição meta com cara de chamada de marketing não vira fato', () => {
  const r = ler();
  assert.ok(!r.fatos.some((f) => /Clique aqui/.test(f.texto)));
  // mas uma descrição informativa vira fato de confiança média
  const h = html.replace(/(<meta name="description"\s+content=")[^"]*/, '$1A capital de Rondônia é Porto Velho, cidade às margens do rio Madeira.');
  const comMeta = ler(h);
  assert.ok(comMeta.fatos.some((f) => f.secao === 'Descrição' && f.confianca === 'media' && /Porto Velho/.test(f.texto)));
});

test('texto escondido e propaganda são ignorados', () => {
  const sujo = html
    .replace('<div class="ler-texto">', '<div class="ler-texto"><p style="display:none">Esconda-se este parágrafo gigante com uma definição falsa de Rondônia.</p><div aria-hidden="true"><p>Outro parágrafo escondido que tampouco pode aparecer em lugar algum.</p></div>')
    .replace('<h2 id="Economia', '<h2 hidden>Seção escondida</h2><p>Frase da seção escondida que não deve ser lida de jeito nenhum.</p><h2 id="Economia');
  const r = ler(sujo);
  const tudo = JSON.stringify(r);
  assert.ok(!/escond|Esconda/i.test(tudo), tudo.match(/.{30}escond.{30}/i)?.[0]);
  assert.match(r.fatos.find((f) => f.secao === 'Abertura').texto, /^Rondônia é uma das 27/);
  assert.ok(!tudo.includes('Anuncie'));
});

test('estrutura inesperada: devolve null ou só o que há, sem lixo', () => {
  assert.equal(ler('<html><body><div>nada aqui</div></body></html>'), null);
  assert.equal(ler('<html><head><title>x</title></head><body><nav><a>Menu</a><a>Entrar</a></nav><h1>Página</h1></body></html>'), null);
  assert.equal(ler(''), null);
  // só JSON-LD (o corpo mudou de lugar): ainda dá o par da FAQ e os metadados, sem inventar fatos do corpo
  const so = html.replace(/<article>[\s\S]*<\/article>/, '').replace(/<p class="resumo-artigo">[\s\S]*?<\/p>/, '');
  const r = ler(so);
  assert.equal(r.pares.length, 1);
  assert.equal(r.atributos.length, 0);
  assert.ok(r.fatos.every((f) => f.texto.length >= 30));
  // JSON-LD quebrado não derruba a leitura
  const quebrado = html.replace('"@type":"FAQPage"', '"@type":"FAQPage" ,,, quebrado');
  const rq = ler(quebrado);
  assert.equal(rq.pares.length, 0);
  assert.ok(rq.fatos.length > 5);
});

test('sem url: adivinha só para definição/lugar, confere o título e respeita o limite', async () => {
  const ctx = ctxFalso({ [URL_RO]: html });
  const r = await brasilescola.extrair({ tema: 'rondônia', tipo: 'lugar' }, ctx);
  assert.ok(r.fatos.length > 5);
  assert.deepEqual(ctx.pedidos, [URL_RO]);
  // página existe mas é de outro assunto: não aceita
  const outro = ctxFalso({ 'https://brasilescola.uol.com.br/brasil/amazonas.htm': html });
  assert.equal(await brasilescola.extrair({ tema: 'amazonas', tipo: 'lugar' }, outro), null);
  // tipo que não vale adivinhar: nem faz requisição
  const pessoa = ctxFalso({});
  assert.equal(await brasilescola.extrair({ tema: 'santos dumont', tipo: 'pessoa' }, pessoa), null);
  assert.equal(pessoa.pedidos.length, 0);
  // nada achado: no máximo 3 tentativas
  const nada = ctxFalso({});
  assert.equal(await brasilescola.extrair({ tema: 'tema inexistente', tipo: 'definicao' }, nada), null);
  assert.ok(nada.pedidos.length <= 3);
});

test('url de outro site é ignorada; erro de rede e 5xx propagam', async () => {
  const ctx = ctxFalso({});
  assert.equal(await brasilescola.extrair({ url: 'https://outro.com/x.htm', tema: 'x', tipo: 'geral' }, ctx), null);
  assert.equal(ctx.pedidos.length, 0);
  const quebrado = { parsear, registrar: () => {}, buscar: async () => { throw new Error('rede caiu'); } };
  await assert.rejects(() => brasilescola.extrair({ url: URL_RO }, quebrado), /rede caiu/);
  const fora = { ...quebrado, buscar: async (url) => ({ status: 503, ok: false, url, texto: '' }) };
  await assert.rejects(() => brasilescola.extrair({ url: URL_RO }, fora), /503/);
});

test('funções auxiliares', () => {
  assert.equal(slugDoTema('Média Aritmética!'), 'media-aritmetica');
  assert.ok(tituloCombina('Média aritmética: fórmula', 'media aritmetica'));
  assert.ok(!tituloCombina('Amazonas', 'rondonia'));
  assert.deepEqual(pareceNomeValor('Área territorial: 237.754,17 km² (IBGE, 2022).'), { nome: 'Área territorial', valor: '237.754,17 km² (IBGE, 2022)' });
  assert.equal(pareceNomeValor('Este é um texto comum sem dois pontos.'), null);
  assert.equal(pareceNomeValor('Leia também: http://x.com'), null);
  assert.deepEqual(frases('A área é de 237 km², ou 6,65 hab./km² no total. Outra frase aqui, com mais texto.'), ['A área é de 237 km², ou 6,65 hab./km² no total.', 'Outra frase aqui, com mais texto.']);
});
