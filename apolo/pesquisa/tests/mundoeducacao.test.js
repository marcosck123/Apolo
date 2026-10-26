import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { criarCtx } from '../adaptadores/ctx.js';
import { extrairArtigo, exemploDaSecao } from '../adaptadores/brasilescola.js';
import mundoeducacao from '../adaptadores/mundoeducacao.js';

const html = readFileSync(new URL('./fixtures/mundoeducacao/media-aritmetica.html', import.meta.url), 'utf8');
const URL_MA = 'https://mundoeducacao.uol.com.br/matematica/media-aritmetica.htm';
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
const ler = async (h = html) => mundoeducacao.extrair({ url: URL_MA }, ctxFalso({ [URL_MA]: h }));

test('média aritmética: metadados, licença e definição de abertura', async () => {
  const r = await ler();
  assert.equal(r.metadados.titulo, 'Média aritmética: fórmula, como calcular, exemplo');
  assert.equal(r.metadados.data, '2020-05-13');
  assert.equal(r.metadados.autor, 'Robson Luiz');
  assert.match(mundoeducacao.licenca, /Todos os direitos reservados/);
  const def = r.fatos.find((f) => f.secao === 'Abertura');
  assert.equal(def.texto, 'A média aritmética é uma medida estatística de posição, ou seja, ela nos fornece a posição de elementos que estão em um rol numérico.');
  assert.equal(def.confianca, 'media');
  assert.ok(r.fatos.every((f) => f.fonte === URL_MA && f.texto.length <= 400 && f.adaptador === 'mundoeducacao'));
});

test('negrito da abertura vira conceito, sem pedaços soltos nem propaganda', async () => {
  const r = await ler();
  const nomes = r.conceitos.map((c) => c.nome);
  assert.ok(nomes.includes('média aritmética'));
  assert.ok(nomes.includes('medida estatística de posição'));
  assert.ok(nomes.includes('Estatística')); // do caminho de navegação
  assert.equal(r.conceitos.find((c) => c.nome === 'média aritmética').peso, 0.8);
  assert.ok(!nomes.some((n) => /Leia também|publicidade/i.test(n)));
});

test('seções "Exemplo N" viram fatos do tipo exemplo (enunciado e dados)', async () => {
  const r = await ler();
  const exemplos = r.fatos.filter((f) => f.tipo === 'exemplo');
  assert.deepEqual(exemplos.map((f) => f.secao), ['Exemplo 1', 'Exemplo 2', 'Exemplo 3']);
  assert.match(exemplos[0].texto, /^Exemplo: Em um grupo de seis amigos, foram computadas suas idades\. Determine qual a idade média desse grupo\. Idades \{12, 13, 14, 16, 18,20\}$/);
  assert.equal(exemplos[1].texto, 'Exemplo: Determine a média entre os números 4, 9, 12, 25.');
});

test('exemplo traz o resultado quando o texto o diz', () => {
  const secao = { titulo: 'Exemplo 1', blocos: [
    { tipo: 'p', texto: 'Calcule a média entre os números 2 e 4, somando e dividindo por dois.' },
    { tipo: 'p', texto: 'Somamos os dois números e dividimos o total pela quantidade deles.' },
    { tipo: 'p', texto: 'Portanto, a média aritmética entre 2 e 4 é igual a 3.' },
  ] };
  assert.equal(exemploDaSecao(secao), 'Exemplo: Calcule a média entre os números 2 e 4, somando e dividindo por dois. Resultado: Portanto, a média aritmética entre 2 e 4 é igual a 3.');
  assert.equal(exemploDaSecao({ titulo: 'Exemplo 2', blocos: [{ tipo: 'p', texto: 'Curto.' }] }), null);
});

test('FAQPage vira par; exercícios e vídeos não viram fato', async () => {
  const r = await ler();
  assert.equal(r.pares.length, 1);
  assert.equal(r.pares[0].pergunta, 'Qual a diferença entre média aritmética simples e ponderada?');
  assert.match(r.pares[0].resposta, /^A média aritmética pode ser analisada em duas situações\./);
  assert.ok(r.pares[0].resposta.length <= 400);
  assert.ok(!r.fatos.some((f) => /Exerc|Video|Artigos relacionados/i.test(f.secao ?? '')));
  assert.equal(r.atributos.length, 0); // não há "Dados gerais" nesta página
});

test('texto escondido é ignorado', async () => {
  const sujo = html.replace('<div class="texto-conteudo">', '<div class="texto-conteudo"><div style="display:none"><p>Parágrafo escondido <strong>termo escondido</strong> que define algo falso para o robô.</p></div>')
    .replace('<h2><strong>M&eacute;dia aritm&eacute;tica ponderada</strong></h2>', '<div aria-hidden="true"><h3>Exemplo 9</h3><p>Exemplo escondido que nunca deveria aparecer em fato algum.</p></div><h2><strong>M&eacute;dia aritm&eacute;tica ponderada</strong></h2>');
  const r = await ler(sujo);
  assert.ok(!/escondido/i.test(JSON.stringify(r)));
  assert.equal(r.fatos.filter((f) => f.tipo === 'exemplo').length, 3);
});

test('estrutura inesperada: null ou parcial sem lixo', async () => {
  assert.equal(await ler('<html><body><p>Manutenção</p></body></html>'), null);
  assert.equal(extrairArtigo(parsear('<html><body><h1>Título</h1><div class="texto-conteudo"><p>Curto</p><p>Menu | Entrar | Assine já</p></div></body></html>'), { adaptador: mundoeducacao, url: URL_MA }), null);
  // sem JSON-LD: continua extraindo do corpo, mas sem pares
  const semLd = html.replace(/<script[^>]*ld\+json[^>]*>[\s\S]*?<\/script>/g, '');
  const r = await ler(semLd);
  assert.equal(r.pares.length, 0);
  assert.equal(r.metadados.titulo, 'Média Aritmética'); // vem do h1
  assert.ok(r.fatos.length >= 4);
});

test('sem url: adivinha só definição, confere o título; outros tipos não gastam requisição', async () => {
  const ctx = ctxFalso({ [URL_MA]: html });
  const r = await mundoeducacao.extrair({ tema: 'média aritmética', tipo: 'definicao' }, ctx);
  assert.ok(r.fatos.length >= 4);
  assert.deepEqual(ctx.pedidos, [URL_MA]);
  const lugar = ctxFalso({});
  assert.equal(await mundoeducacao.extrair({ tema: 'rondonia', tipo: 'lugar' }, lugar), null);
  assert.equal(await mundoeducacao.extrair({ tema: 'oi', tipo: 'geral' }, lugar), null);
  assert.equal(lugar.pedidos.length, 0);
  const nada = ctxFalso({});
  assert.equal(await mundoeducacao.extrair({ tema: 'assunto inexistente', tipo: 'definicao' }, nada), null);
  assert.ok(nada.pedidos.length <= 3);
  // existe, mas é de outro assunto
  const outro = ctxFalso({ 'https://mundoeducacao.uol.com.br/matematica/moda.htm': html });
  assert.equal(await mundoeducacao.extrair({ tema: 'moda', tipo: 'definicao' }, outro), null);
});

test('erro de rede propaga', async () => {
  const quebrado = { parsear, registrar: () => {}, buscar: async () => { throw new Error('rede caiu'); } };
  await assert.rejects(() => mundoeducacao.extrair({ url: URL_MA }, quebrado), /rede caiu/);
});
