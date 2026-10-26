import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { beforeEach, test } from 'node:test';
import { parseHTML } from 'linkedom';
import ibge, { formatarDecimal, formatarInteiro, limparCache, normalizar, resolver } from '../adaptadores/ibge.js';

const LER = (arquivo) => readFileSync(new URL(`./fixtures/ibge/${arquivo}`, import.meta.url), 'utf8');

// Respostas reais do IBGE, reduzidas: todos os municípios de RO + homônimos de Rio Branco, Santa Helena e Rio de Janeiro.
const AGREGADOS = {
  'N6[1100304]': 'agregados_vilhena.json',
  'N6[1100205]': 'agregados_porto_velho.json',
  'N3[11]': 'agregados_rondonia.json',
  'N6[1200401]': 'agregados_rio_branco.json', // (a fixture traz Rio Branco AC e MT; o lido é filtrado pelo adaptador)
  'N6[1200401,5107206]': 'agregados_rio_branco.json',
  'N3[33]|N6[3304557]': 'agregados_rio_de_janeiro.json',
  'N6[2109809,2513307,4123501,4215554]': 'agregados_santa_helena.json',
};

function criarCtxFalso({ agregados = true, falhar = false } = {}) {
  const chamadas = [];
  const ctx = {
    chamadas,
    registrar: () => {},
    parsear: (html) => parseHTML(html).document,
    async buscar(url) {
      chamadas.push(url);
      if (falhar) throw new Error('rede caiu');
      const resposta = (texto, status = 200) => ({ status, ok: status < 400, url, texto, json: () => JSON.parse(texto) });
      if (url.endsWith('/localidades/estados')) return resposta(LER('estados.json'));
      if (url.endsWith('/localidades/municipios')) return resposta(LER('municipios.json'));
      if (url.includes('/agregados/4714/')) {
        if (!agregados) return resposta('{"statusCode":500}', 500);
        const localidades = decodeURIComponent(url.split('localidades=')[1]);
        return AGREGADOS[localidades] ? resposta(LER(AGREGADOS[localidades])) : resposta('[]', 404);
      }
      return resposta('', 404);
    },
  };
  return ctx;
}

const textos = (r) => r.fatos.map((f) => f.texto);
const attr = (r, nome) => r.atributos.find((a) => a.nome === nome)?.valor;

beforeEach(() => limparCache());

test('metadados do adaptador: tipos, domínios e licença', () => {
  assert.equal(ibge.nome, 'ibge');
  assert.deepEqual(ibge.tipos, ['lugar', 'definicao', 'geral']);
  assert.ok(ibge.dominios.includes('servicodados.ibge.gov.br'));
  assert.match(ibge.licenca, /verificar/);
});

test('Vilhena: fatos e atributos com os números do Censo 2022', async () => {
  const ctx = criarCtxFalso();
  const r = await ibge.extrair({ tema: 'vilhena', tipo: 'lugar' }, ctx);
  assert.ok(textos(r).includes('Vilhena é um município do estado de Rondônia (RO), na região Norte do Brasil, com 95.832 habitantes no Censo de 2022 (fonte: IBGE).'));
  assert.ok(textos(r).includes('A área territorial de Vilhena (RO) é de 11.699,15 km² (fonte: IBGE, Censo 2022).'));
  assert.equal(attr(r, 'População (Censo 2022)'), '95.832 habitantes');
  assert.equal(attr(r, 'Área (km²)'), '11.699,15');
  assert.equal(attr(r, 'Densidade demográfica (hab./km²)'), '8,19');
  assert.equal(attr(r, 'Código IBGE'), '1100304');
  assert.equal(attr(r, 'UF'), 'Rondônia (RO)');
  assert.equal(attr(r, 'Região'), 'Norte');
  assert.equal(attr(r, 'Microrregião'), 'Vilhena');
  assert.equal(attr(r, 'Mesorregião'), 'Leste Rondoniense');
  assert.equal(attr(r, 'Região Geográfica Intermediária'), 'Ji-Paraná');
  for (const f of r.fatos) {
    assert.match(f.fonte, /^https:\/\/servicodados\.ibge\.gov\.br\/api\//);
    assert.equal(f.adaptador, 'ibge');
    assert.equal(f.licenca, 'verificar (dados abertos do IBGE)');
    assert.doesNotMatch(f.texto, /undefined|null|NaN/);
  }
  assert.equal(r.metadados.titulo, 'Vilhena (RO)');
  assert.ok(r.conceitos.some((c) => c.nome === 'Rondônia'));
  assert.equal(ctx.chamadas.length, 3); // estados + municípios + agregados
});

test('lista de municípios fica em memória: a segunda consulta faz só 1 requisição', async () => {
  const ctx = criarCtxFalso();
  await ibge.extrair({ tema: 'Vilhena' }, ctx);
  ctx.chamadas.length = 0;
  const r = await ibge.extrair({ tema: 'Porto Velho' }, ctx);
  assert.equal(ctx.chamadas.length, 1);
  assert.match(textos(r)[0], /^Porto Velho é um município do estado de Rondônia \(RO\).*460\.434 habitantes/);
  assert.ok(textos(r).some((t) => /capital do estado de Rondônia/.test(t)));
});

test('estado: capital, número de municípios, população e área', async () => {
  for (const tema of ['Rondônia', 'rondonia', 'estado de Rondônia']) {
    limparCache();
    const r = await ibge.extrair({ tema }, criarCtxFalso());
    assert.ok(textos(r).includes('A capital do estado de Rondônia é Porto Velho.'), tema);
    assert.ok(textos(r).includes('Rondônia tem 52 municípios, segundo a divisão territorial do IBGE.'), tema);
    assert.ok(textos(r).includes('Rondônia tinha 1.581.196 habitantes no Censo de 2022 (fonte: IBGE).'), tema);
    assert.equal(attr(r, 'Capital'), 'Porto Velho');
    assert.equal(attr(r, 'Número de municípios'), '52');
    assert.equal(attr(r, 'Sigla'), 'RO');
    assert.equal(attr(r, 'Área (km²)'), '237.754,17');
    assert.equal(r.fatos.find((f) => /capital/.test(f.texto)).confianca, 'media');
  }
});

test('homônimo com UF no tema: só o município pedido', async () => {
  for (const tema of ['Rio Branco, Acre', 'rio branco acre', 'Rio Branco AC', 'Rio Branco - AC']) {
    limparCache();
    const r = await ibge.extrair({ tema }, criarCtxFalso());
    assert.equal(attr(r, 'Código IBGE'), '1200401', tema);
    assert.ok(textos(r)[0].includes('Rio Branco é um município do estado de Acre (AC)'), tema);
    assert.ok(!textos(r).some((t) => /Mato Grosso/.test(t)), tema);
  }
  const r = await ibge.extrair({ tema: 'Rio Branco, Mato Grosso' }, criarCtxFalso());
  assert.equal(attr(r, 'Código IBGE'), '5107206');
});

test('homônimo sem UF: o mais populoso é o principal e os outros viram fatos curtos', async () => {
  const r = await ibge.extrair({ tema: 'Rio Branco' }, criarCtxFalso());
  assert.equal(attr(r, 'Código IBGE'), '1200401'); // Rio Branco (AC) tem mais habitantes que o de MT
  assert.match(textos(r)[0], /Acre \(AC\).*364\.756 habitantes/);
  const outro = textos(r).find((t) => t.startsWith('Existe também'));
  assert.match(outro, /^Existe também um município chamado Rio Branco no estado de Mato Grosso \(MT\), com [\d.]+ habitantes no Censo de 2022 \(fonte: IBGE\)\.$/);
  assert.equal(r.atributos.filter((a) => a.nome === 'Código IBGE').length, 1);
});

test('vários homônimos: principal + no máximo 3 menções', async () => {
  const r = await ibge.extrair({ tema: 'Santa Helena' }, criarCtxFalso());
  assert.equal(textos(r).filter((t) => t.startsWith('Existe também')).length, 3);
  assert.equal(r.atributos.filter((a) => a.nome === 'Código IBGE').length, 1);
});

test('nome de estado e de município ao mesmo tempo: devolve os dois', async () => {
  const r = await ibge.extrair({ tema: 'Rio de Janeiro' }, criarCtxFalso());
  assert.ok(textos(r).some((t) => /^Rio de Janeiro é um estado brasileiro/.test(t)));
  assert.ok(textos(r).some((t) => /^Rio de Janeiro é um município do estado de Rio de Janeiro \(RJ\)/.test(t)));
  assert.ok(r.atributos.some((a) => a.nome === 'Capital'));
  const soCidade = await ibge.extrair({ tema: 'cidade de Rio de Janeiro' }, criarCtxFalso());
  assert.ok(!textos(soCidade).some((t) => /estado brasileiro/.test(t)));
});

test('município inexistente, tema vazio ou comprido demais → null', async () => {
  assert.equal(await ibge.extrair({ tema: 'Atlântida' }, criarCtxFalso()), null);
  assert.equal(await ibge.extrair({ tema: '' }, criarCtxFalso()), null);
  assert.equal(await ibge.extrair({ tema: 'como funciona o sistema de coleta de lixo no interior do brasil hoje' }, criarCtxFalso()), null);
  assert.equal(await ibge.extrair({ tema: 'Vilhena Bahia' }, criarCtxFalso()), null); // Vilhena não existe na Bahia
});

test('se a API de dados falhar, não inventa número: só o que vem da lista de localidades', async () => {
  const r = await ibge.extrair({ tema: 'Vilhena' }, criarCtxFalso({ agregados: false }));
  assert.ok(!textos(r).some((t) => /habitantes|km²/.test(t)));
  assert.equal(attr(r, 'População (Censo 2022)'), undefined);
  assert.equal(attr(r, 'Código IBGE'), '1100304');
  assert.match(textos(r)[0], /^Vilhena é um município do estado de Rondônia \(RO\), na região Norte do Brasil \(fonte: IBGE\)\.$/);
});

test('município sem microrregião na lista do IBGE não gera "null" nos textos', async () => {
  const r = await ibge.extrair({ tema: 'Boa Esperança do Norte' }, criarCtxFalso({ agregados: false }));
  assert.equal(attr(r, 'Código IBGE'), '5101837');
  assert.equal(attr(r, 'UF'), 'Mato Grosso (MT)');
  for (const f of r.fatos) assert.doesNotMatch(f.texto, /null|undefined/);
});

test('erro de rede propaga (o roteador isola a falha)', async () => {
  await assert.rejects(() => ibge.extrair({ tema: 'Vilhena' }, criarCtxFalso({ falhar: true })), /rede caiu/);
});

test('resolver e formatadores', () => {
  assert.equal(normalizar('  São João d\'Aliança '), 'sao joao d alianca');
  assert.equal(formatarInteiro(1581196), '1.581.196');
  assert.equal(formatarDecimal(11699.15), '11.699,15');
  assert.equal(formatarDecimal(8.19), '8,19');
  const base = { estados: JSON.parse(LER('estados.json')).map((s) => ({ ...s, norm: normalizar(s.nome), regiao: s.regiao.nome })), municipios: [] };
  assert.deepEqual(resolver('estado de Mato Grosso do Sul', base).estados.map((s) => s.sigla), ['MS']);
  assert.deepEqual(resolver('mato grosso', base).estados.map((s) => s.sigla), ['MT']);
});
