// Adaptador do Wikidata: dados exatos (população, capital, nascimento...) em vez de texto corrido.
// Três requisições por consulta, todas na API oficial:
//   1) wbsearchentities: acha a entidade (Q...) pelo nome;
//   2) wbgetentities (claims): as propriedades da entidade;
//   3) wbgetentities (labels): os rótulos em pt/en das propriedades e das entidades que aparecem como valor
//      ("país: Q155" vira "país: Brasil"), tudo num pedido só.
// Licença: CC0 1.0 (dados estruturados do Wikidata são domínio público: wikidata.org/wiki/Wikidata:Licensing).
import { atributo, limparTexto } from './contrato.js';

const adaptador = {
  nome: 'wikidata',
  licenca: 'CC0 1.0',
  tipos: ['lugar', 'pessoa', 'definicao'],
  dominios: ['www.wikidata.org', 'wikidata.org'],
  extrair,
};
export default adaptador;

const API = 'https://www.wikidata.org/w/api.php';
const MAX_ATRIBUTOS = 12;
const MAX_VALORES = 3;
const MAX_IDS_ROTULOS = 50; // limite da API por pedido

// Propriedades úteis, em ordem de prioridade. A lista do tipo da pergunta vem primeiro; as demais completam.
const POR_TIPO = {
  lugar: ['P31', 'P17', 'P131', 'P36', 'P1376', 'P1082', 'P2046', 'P2044', 'P6', 'P571', 'P625', 'P421', 'P856', 'P159'],
  pessoa: ['P31', 'P569', 'P19', 'P570', 'P20', 'P27', 'P106', 'P69', 'P166', 'P26', 'P1412', 'P800', 'P856'],
  definicao: ['P31', 'P279', 'P361', 'P527', 'P1269', 'P2579', 'P138', 'P571', 'P576', 'P17', 'P856'],
};
const TODAS = [...new Set(Object.values(POR_TIPO).flat())];
// Propriedades cujo valor "atual" é o que não tem data de término (prefeito, capital, sede...)
const SO_VIGENTES = new Set(['P6', 'P36', 'P159', 'P1376']);
// Propriedades de quantidade em que vários valores são medições de datas diferentes: fica a mais recente.
const MEDICOES = new Set(['P1082', 'P2046', 'P2044']);
// Os conceitos (vizinhos no grafo) saem destas, com o peso de cada uma.
const PESO_CONCEITO = { P31: 0.9, P279: 0.9, P361: 0.7, P17: 0.7, P131: 0.6, P27: 0.7, P106: 0.8, P1269: 0.6, P2579: 0.6, P36: 0.5 };

const UNIDADES = {
  Q712226: 'km²', Q25343: 'm²', Q828224: 'km', Q11573: 'm', Q174728: 'cm', Q11574: 's', Q11570: 'kg', Q41803: 'g',
  Q25235: 'ha', Q182429: 'm/s', Q25250: 'V', Q11229: '%', Q2636421: 'mi²', Q253276: 'mi',
};
// A população tem um "plural natural"; as demais unidades usam o símbolo ou o rótulo da unidade.
const MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];

const normalizar = (t) => String(t ?? '').toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();
const consultar = (parametros) => `${API}?${new URLSearchParams({ format: 'json', formatversion: '2', ...parametros })}`;

async function extrair({ tema, tipo, url }, ctx) {
  const id = idDaUrl(url) ?? await acharEntidade(tema, tipo, ctx);
  if (!id) return null;

  const entidades = await json(ctx, consultar({ action: 'wbgetentities', ids: id, props: 'claims|labels|descriptions|info', languages: 'pt|en' }));
  const entidade = entidades?.entities?.[id];
  if (!entidade || entidade.missing !== undefined) return null;

  const ordem = prioridade(tipo);
  const selecionados = selecionar(entidade.claims ?? {}, ordem);
  if (!selecionados.length) return null;

  const rotulos = await buscarRotulos(ctx, selecionados);
  const rotulo = (qid) => rotulos[qid]?.labels?.pt?.value ?? rotulos[qid]?.labels?.en?.value ?? null;
  const titulo = entidade.labels?.pt?.value ?? entidade.labels?.en?.value ?? id;
  const fonte = `https://www.wikidata.org/wiki/${id}`;

  const atributos = [];
  const conceitos = [];
  for (const { propriedade, valores } of selecionados) {
    const nomeProp = rotulo(propriedade);
    if (!nomeProp) continue;
    const textos = valores.map((v) => formatar(v, rotulo, propriedade)).filter(Boolean);
    if (!textos.length) continue;
    atributos.push(atributo(adaptador, { nome: maiuscula(nomeProp), valor: textos.join('; '), fonte }));
    if (PESO_CONCEITO[propriedade]) {
      for (const v of valores) {
        const alvo = v.snak.datatype === 'wikibase-item' ? v.snak.datavalue?.value?.id : null;
        const nome = alvo ? rotulo(alvo) : null;
        if (nome) conceitos.push({ nome: maiuscula(nome), url: `https://www.wikidata.org/wiki/${alvo}`, peso: PESO_CONCEITO[propriedade] });
      }
    }
  }
  if (!atributos.length) return null;

  const unicos = new Map();
  for (const c of conceitos) if (!unicos.has(c.nome.toLowerCase())) unicos.set(c.nome.toLowerCase(), c);
  return {
    atributos,
    conceitos: [...unicos.values()],
    metadados: {
      titulo, idioma: 'pt', url: fonte,
      descricao: entidade.descriptions?.pt?.value ?? entidade.descriptions?.en?.value,
      data: entidade.modified,
    },
  };
}

const idDaUrl = (url) => (url ? String(url).match(/\/(?:wiki|entity)\/(Q\d+)/)?.[1] ?? null : null);
const maiuscula = (t) => (t ? t.charAt(0).toUpperCase() + t.slice(1) : t);
const prioridade = (tipo) => [...new Set([...(POR_TIPO[tipo] ?? []), ...TODAS])];

async function json(ctx, url) {
  const r = await ctx.buscar(url, { json: true });
  if (!r.ok) throw new Error(`wikidata: resposta ${r.status}`);
  const dados = r.json();
  if (dados?.error) throw new Error(`wikidata: ${dados.error.code ?? 'erro da API'}`);
  return dados;
}

// ---------- busca da entidade ----------

const DESAMBIGUACAO = /desambigua|disambiguation|wikimedia (category|list|template)|categoria da wikimedia|lista da wikimedia/i;
const LUGARISH = /munic|cidade|city|town|capital|pa[ií]s|country|estado|state|regi[ãa]o|region|distrito|district|bairro|ilha|island|prov[ií]ncia|province|vila|village|territ|continente|localidade/i;
const OUTRAS_COISAS = /aeroporto|airport|estrada|rodovia|rio\b|river|banda|band\b|filme|film\b|[áa]lbum|album|asteroid|cratera|crater|rua\b|street|esta[çc][ãa]o|station|esp[ée]cie|species|g[êe]nero|genus|fam[ií]lia|quilombo|escola|school|clube|club|livro|book|s[ée]rie|series|v[ií]deo|jogo|game|sobrenome|surname|given name|nome pr[óo]prio|print in|work by|monumento|parada|stop\b|minis/i;
const PESSOA = /\(\d{3,4}\s*[–-]\s*\d{0,4}\)|\bhuman\b|\bhumano\b|brasileir[oa]|portugu[êe]s|inventor|escritor|escritora|pol[ií]tico|cantor|cantora|ator\b|atriz|m[úu]sico|cientista|pintor|jogador|engenheiro|aeronauta|fil[óo]sofo|cineasta|professor|empres[áa]rio/i;

async function acharEntidade(tema, tipo, ctx) {
  const consulta = String(tema ?? '').trim();
  if (!consulta) return null;
  const palavras = normalizar(consulta).split(' ').filter(Boolean);
  for (const idioma of ['pt', 'en']) {
    const dados = await json(ctx, consultar({ action: 'wbsearchentities', search: consulta, language: idioma, uselang: 'pt', type: 'item', limit: '6' }));
    const candidatos = (dados?.search ?? [])
      .map((c, i) => ({ c, i, rotulo: c.label ?? c.display?.label?.value ?? '', descricao: c.description ?? '' }))
      .filter(({ descricao }) => !DESAMBIGUACAO.test(descricao))
      .filter(({ rotulo }) => {
        const r = normalizar(rotulo).split(' ').filter(Boolean);
        return r.length > 0 && (r.every((p) => palavras.includes(p)) || palavras.every((p) => r.includes(p)));
      });
    if (!candidatos.length) continue;
    // Pontuação: casar exatamente com o que foi perguntado (no rótulo ou no apelido encontrado) pesa mais; depois o tipo da
    // pergunta; "Brasil" ganha um pouco porque o Apolo é usado em português do Brasil (Vilhena RO e Villena ES têm o mesmo rótulo).
    const pontos = ({ c, rotulo, descricao, i }) => {
      let p = -0.1 * i;
      if (normalizar(rotulo) === normalizar(consulta) || normalizar(c.match?.text) === normalizar(consulta)) p += 10;
      if (OUTRAS_COISAS.test(descricao)) p -= 3;
      if (tipo === 'lugar' && LUGARISH.test(descricao)) p += 3;
      if (tipo === 'pessoa' && PESSOA.test(descricao)) p += 4;
      if (/brasil/i.test(descricao)) p += 1.5;
      return p;
    };
    return candidatos.sort((a, b) => pontos(b) - pontos(a))[0].c.id;
  }
  return null;
}

// ---------- seleção das declarações ----------

// Devolve [{ propriedade, valores: [declaração...] }] já filtrado (rank, vigência, medição mais recente) e limitado.
function selecionar(claims, ordem) {
  const saida = [];
  for (const propriedade of ordem) {
    if (saida.length >= MAX_ATRIBUTOS) break;
    let declaracoes = (claims[propriedade] ?? []).filter((d) => d.rank !== 'deprecated' && d.mainsnak?.snaktype === 'value');
    if (!declaracoes.length) continue;
    const preferidas = declaracoes.filter((d) => d.rank === 'preferred');
    if (preferidas.length) declaracoes = preferidas;
    if (SO_VIGENTES.has(propriedade)) {
      const vigentes = declaracoes.filter((d) => !d.qualifiers?.P582);
      if (vigentes.length) declaracoes = vigentes;
    }
    if (MEDICOES.has(propriedade)) {
      declaracoes = [[...declaracoes].sort((a, b) => dataMedicao(b).localeCompare(dataMedicao(a)))[0]];
    }
    const valores = declaracoes.slice(0, propriedade === 'P106' ? 4 : MAX_VALORES).map((d) => ({ snak: d.mainsnak, qualifiers: d.qualifiers }));
    // só valores simples: o resto (arquivos, identificadores, fórmulas) não serve a quem pergunta
    if (valores.every((v) => !['wikibase-item', 'quantity', 'time', 'string', 'url', 'monolingualtext', 'globe-coordinate'].includes(v.snak.datatype))) continue;
    saida.push({ propriedade, valores });
  }
  return saida;
}

const dataMedicao = (d) => d.qualifiers?.P585?.[0]?.datavalue?.value?.time ?? '';

async function buscarRotulos(ctx, selecionados) {
  const ids = new Set();
  for (const { propriedade, valores } of selecionados) {
    ids.add(propriedade);
    for (const { snak } of valores) {
      if (snak.datatype === 'wikibase-item') ids.add(snak.datavalue.value.id);
      if (snak.datatype === 'quantity') {
        const unidade = idDaUnidade(snak.datavalue.value.unit);
        if (unidade && !UNIDADES[unidade]) ids.add(unidade);
      }
    }
  }
  const lista = [...ids].slice(0, MAX_IDS_ROTULOS);
  const dados = await json(ctx, consultar({ action: 'wbgetentities', ids: lista.join('|'), props: 'labels', languages: 'pt|en' }));
  return dados?.entities ?? {};
}

// ---------- formatação dos valores ----------

const idDaUnidade = (unit) => (unit && unit !== '1' ? String(unit).match(/(Q\d+)$/)?.[1] ?? null : null);

function formatar({ snak, qualifiers }, rotulo, propriedade) {
  const v = snak.datavalue?.value;
  switch (snak.datatype) {
    case 'wikibase-item': return v?.id ? rotulo(v.id) : null;
    case 'string': return limparTexto(v);
    case 'url': return limparTexto(v);
    case 'monolingualtext': return limparTexto(v?.text);
    case 'time': return formatarData(v);
    case 'globe-coordinate': return formatarCoordenada(v);
    case 'quantity': return formatarQuantidade(v, rotulo, propriedade, qualifiers);
    default: return null;
  }
}

const ROMANOS = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX', 'XXI'];

// "+1873-07-20T00:00:00Z" com precisão 11 → "20 de julho de 1873". Precisões menores mostram só o que é conhecido.
export function formatarData(v) {
  const m = String(v?.time ?? '').match(/^([+-])(\d{1,})-(\d\d)-(\d\d)T/);
  if (!m) return null;
  const ano = Number(m[2]);
  const aC = m[1] === '-';
  const sufixo = aC ? ' a.C.' : '';
  const precisao = v.precision ?? 11;
  if (precisao >= 11 && Number(m[3]) > 0 && Number(m[4]) > 0) return `${Number(m[4])} de ${MESES[Number(m[3]) - 1]} de ${ano}${sufixo}`;
  if (precisao === 10 && Number(m[3]) > 0) return `${MESES[Number(m[3]) - 1]} de ${ano}${sufixo}`;
  if (precisao === 9 || precisao >= 10) return `${ano}${sufixo}`;
  if (precisao === 8) return `década de ${Math.floor(ano / 10) * 10}${sufixo}`;
  if (precisao === 7) { const s = Math.floor((ano - 1) / 100) + 1; return ROMANOS[s] ? `século ${ROMANOS[s]}${sufixo}` : `${ano}${sufixo}`; }
  return null; // milênios e mais: impreciso demais para ser dado
}

function formatarCoordenada(v) {
  if (typeof v?.latitude !== 'number' || typeof v?.longitude !== 'number') return null;
  const grau = (n, pos, neg) => `${numero(Math.abs(n), 4)}° ${n >= 0 ? pos : neg}`;
  return `${grau(v.latitude, 'N', 'S')}, ${grau(v.longitude, 'L', 'O')}`;
}

// Número no padrão brasileiro: "460 434", "34 090,95". Sem casas inúteis.
export function numero(n, maxCasas = 2) {
  const arredondado = Number(n.toFixed(maxCasas));
  const [inteiro, decimal] = String(arredondado).split('.');
  const agrupado = inteiro.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  return decimal ? `${agrupado},${decimal}` : agrupado;
}

function formatarQuantidade(v, rotulo, propriedade, qualifiers) {
  const quantia = Number(v?.amount);
  if (!Number.isFinite(quantia)) return null;
  let texto = numero(quantia);
  const unidade = idDaUnidade(v.unit);
  if (propriedade === 'P1082') texto += quantia === 1 ? ' habitante' : ' habitantes';
  else if (unidade) {
    const nome = UNIDADES[unidade] ?? rotulo(unidade);
    if (nome) texto += ` ${nome}`;
  }
  // Só cita o ano de referência se o Wikidata informa (ponto no tempo); nunca inventa.
  const ref = qualifiers?.P585?.[0]?.datavalue?.value;
  if (ref) {
    const ano = String(ref.time ?? '').match(/^[+-](\d+)-/)?.[1];
    if (ano && (ref.precision ?? 9) >= 9) texto += ` (${Number(ano)})`;
  }
  return texto;
}
