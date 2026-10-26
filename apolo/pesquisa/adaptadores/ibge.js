// IBGE: municípios e estados do Brasil, pela API de dados (servicodados.ibge.gov.br).
// Não existe busca por nome na API de localidades, então o adaptador faz assim (até 3 requisições):
//   1. localidades/estados e localidades/municipios (listas inteiras, ~5.570 municípios; guardadas em memória por 24 h);
//   2. acha o município/estado pelo nome sem acento (aceita UF: "Rio Branco, Acre", "Rio Branco AC");
//   3. agregados/4714 (Censo Demográfico 2022): variáveis 93 (população), 6318 (área km²) e 614 (densidade),
//      numa chamada só para todos os candidatos.
// Homônimos sem UF: o MAIS POPULOSO vira o resultado principal (atributos e fatos completos); os demais
// entram só como um fato curto cada ("Existe também um município chamado X em UF, com N habitantes...").
// Nome que é de estado e de município ao mesmo tempo ("Rio de Janeiro", "São Paulo") devolve os dois;
// "estado de ..." ou "cidade de ..." desfaz a dúvida.
// O painel cidades.ibge.gov.br/api fica atrás de verificação anti-robô (Cloudflare), então não é usado.
// Licença: não consegui confirmar o texto oficial (as páginas de termos do ibge.gov.br bloqueiam acesso automatizado
// e a documentação da API não cita licença), por isso 'verificar'. Cite sempre a fonte: IBGE.
import { atributo, CONFIANCA, fato } from './contrato.js';

const API = 'https://servicodados.ibge.gov.br/api';
const TEMPO_LISTAS_MS = 24 * 3600_000;
const MAX_HOMONIMOS = 4;
// O User-Agent padrão do ctx tem "página" (não ASCII): o Node envia o byte em latin1 e o servidor do IBGE responde 400.
// Enquanto o ctx.js não trocar por ASCII, o adaptador manda a própria versão (aqui o `cabecalhos` vence o padrão).
const CABECALHOS = { 'user-agent': 'ApoloBot/0.1 (projeto pessoal de pesquisa; uma pagina por vez; contato: github.com/marcosck123/Apolo)' };

// Capitais por UF (as capitais não vêm na API de localidades). Conferidas contra a lista de municípios da própria UF.
const CAPITAIS = { AC: 'Rio Branco', AL: 'Maceió', AP: 'Macapá', AM: 'Manaus', BA: 'Salvador', CE: 'Fortaleza', DF: 'Brasília', ES: 'Vitória', GO: 'Goiânia', MA: 'São Luís', MT: 'Cuiabá', MS: 'Campo Grande', MG: 'Belo Horizonte', PA: 'Belém', PB: 'João Pessoa', PR: 'Curitiba', PE: 'Recife', PI: 'Teresina', RJ: 'Rio de Janeiro', RN: 'Natal', RS: 'Porto Alegre', RO: 'Porto Velho', RR: 'Boa Vista', SC: 'Florianópolis', SP: 'São Paulo', SE: 'Aracaju', TO: 'Palmas' };

export const normalizar = (t) =>
  String(t ?? '').toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replace(/[^a-z0-9]+/g, ' ').trim();

// Formatos brasileiros sem depender do ICU do Node.
const milhar = (n) => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
export const formatarInteiro = (n) => milhar(n);
export const formatarDecimal = (n, casas = 2) => {
  const [inteiro, frac] = Number(n).toFixed(casas).split('.');
  return `${milhar(inteiro)},${frac}`;
};
const numero = (v) => { const n = Number.parseFloat(v); return Number.isFinite(n) && /^\d/.test(String(v)) ? n : null; };

let listas = null; // { em, estados, municipios }
export function limparCache() { listas = null; }

async function carregarListas(ctx) {
  if (listas && Date.now() - listas.em < TEMPO_LISTAS_MS) return listas;
  const [e, m] = [await ctx.buscar(`${API}/v1/localidades/estados`, { json: true, cabecalhos: CABECALHOS }), await ctx.buscar(`${API}/v1/localidades/municipios`, { json: true, cabecalhos: CABECALHOS })];
  if (!e.ok || !m.ok) throw new Error(`IBGE localidades respondeu ${e.ok ? m.status : e.status}`);
  const estados = e.json().map((x) => ({ id: x.id, sigla: x.sigla, nome: x.nome, norm: normalizar(x.nome), regiao: x.regiao?.nome ?? null }));
  const municipios = m.json().map((x) => {
    const inter = x['regiao-imediata']?.['regiao-intermediaria'];
    const uf = x.microrregiao?.mesorregiao?.UF ?? inter?.UF;
    return {
      id: x.id, nome: x.nome, norm: normalizar(x.nome), uf: uf?.sigla, ufNome: uf?.nome, regiao: uf?.regiao?.nome ?? null,
      microrregiao: x.microrregiao?.nome ?? null, mesorregiao: x.microrregiao?.mesorregiao?.nome ?? null,
      imediata: x['regiao-imediata']?.nome ?? null, intermediaria: inter?.nome ?? null,
    };
  });
  listas = { em: Date.now(), estados, municipios };
  return listas;
}

// Se quem perguntou escreveu o nome COM acento, ele tem de bater: "França" (país) não é o município Franca (SP).
// Sem acento no nome digitado ("franca", "vilhena", "para"), vale o nome sem acento, como antes.
const palavras = (t) => String(t ?? '').toLowerCase().normalize('NFC').match(/[\p{L}\p{N}]+/gu) ?? [];
const semMarcas = (p) => p.normalize('NFD').replace(/\p{Diacritic}/gu, '');
export function acentoConfere(texto, nome) {
  const dele = palavras(texto), alvo = palavras(nome);
  const alvoSem = alvo.map(semMarcas);
  for (let i = 0; i + alvo.length <= dele.length; i++) {
    const trecho = dele.slice(i, i + alvo.length);
    if (!trecho.every((p, k) => semMarcas(p) === alvoSem[k])) continue;
    const digitouAcento = trecho.some((p) => p !== semMarcas(p));
    return !digitouAcento || trecho.every((p, k) => p === alvo[k]);
  }
  return true; // o nome não aparece escrito assim (veio de "cidade de X, UF" etc.): não há o que conferir
}

// Entende o tema: devolve { estados: [...], municipios: [...] } com tudo que o nome pode significar.
export function resolver(tema, { estados, municipios }) {
  let n = normalizar(tema);
  let dica = null;
  n = n.replace(/^(?:o |a )?(estado|municipio|cidade) (?:de |do |da )?/, (_, tipo) => { dica = tipo === 'estado' ? 'estado' : 'municipio'; return ''; }).trim();
  if (!n || n.split(' ').length > 8) return { estados: [], municipios: [] };

  const estado = dica === 'municipio' ? null : estados.find((s) => s.norm === n || (n.length === 2 && s.sigla.toLowerCase() === n && dica === 'estado'));
  const exatos = dica === 'estado' ? [] : municipios.filter((m) => m.norm === n);
  if (estado || exatos.length) return { estados: estado ? [estado] : [], municipios: exatos };

  // "rio branco acre", "rio branco ac", "vilhena ro"; o nome mais longo de estado vence ("mato grosso do sul")
  for (const s of [...estados].sort((a, b) => b.norm.length - a.norm.length)) {
    for (const sufixo of [s.norm, s.sigla.toLowerCase()]) {
      if (!n.endsWith(` ${sufixo}`)) continue;
      const nome = n.slice(0, -sufixo.length).trim().replace(/\s(?:de|do|da)$/, '');
      const achados = municipios.filter((m) => m.uf === s.sigla && m.norm === nome);
      if (achados.length) return { estados: [], municipios: achados };
    }
  }
  return { estados: [], municipios: [] };
}

function lerSeries(agregado) {
  const mapa = new Map(); // id → { populacao, ano, area, densidade }
  for (const variavel of agregado ?? []) {
    for (const serie of variavel.resultados?.[0]?.series ?? []) {
      const [ano, valor] = Object.entries(serie.serie ?? {}).sort().pop() ?? [];
      const n = numero(valor);
      if (n === null) continue;
      const item = mapa.get(String(serie.localidade.id)) ?? {};
      if (variavel.id === '93') { item.populacao = n; item.ano = ano; }
      if (variavel.id === '6318') item.area = n;
      if (variavel.id === '614') item.densidade = n;
      mapa.set(String(serie.localidade.id), item);
    }
  }
  return mapa;
}

export default {
  nome: 'ibge',
  licenca: 'verificar (dados abertos do IBGE)',
  tipos: ['lugar', 'definicao', 'geral'],
  dominios: ['servicodados.ibge.gov.br', 'cidades.ibge.gov.br', 'ibge.gov.br'],

  async extrair({ tema, consulta }, ctx) {
    if (!tema || normalizar(tema).length < 3) return null;
    const base = await carregarListas(ctx);
    const achados = resolver(tema, base);
    const estados = achados.estados.filter((x) => acentoConfere(consulta ?? tema, x.nome));
    const municipios = achados.municipios.filter((x) => acentoConfere(consulta ?? tema, x.nome));
    if (!estados.length && !municipios.length) return null;

    // população/área/densidade de todos os candidatos numa chamada só (mais populosos primeiro, depois).
    const candidatos = municipios.slice(0, 40);
    const localidades = [...estados.map((s) => `N3[${s.id}]`), `N6[${candidatos.map((m) => m.id).join(',')}]`].filter((l) => !l.endsWith('[]')).join('|');
    const urlDados = `${API}/v3/agregados/4714/periodos/-1/variaveis/93%7C6318%7C614?localidades=${encodeURIComponent(localidades).replace(/%2C/g, ',')}`;
    let dados = new Map();
    try {
      const r = await ctx.buscar(urlDados, { json: true, cabecalhos: CABECALHOS });
      if (r.ok) dados = lerSeries(r.json());
    } catch (erro) {
      ctx.registrar?.(`ibge: agregados falhou: ${erro.message}`);
    }

    const fonteLocalidades = `${API}/v1/localidades`;
    const resultado = { fatos: [], conceitos: [], atributos: [], codigos: [], pares: [], metadados: {} };
    const f = (texto, fonte, confianca = CONFIANCA.alta, secao = null) => resultado.fatos.push(fato(this, { texto, secao, fonte, confianca }));
    const a = (nome, valor, fonte) => { if (valor !== null && valor !== undefined && valor !== '') resultado.atributos.push(atributo(this, { nome, valor, fonte })); };
    const conceito = (nome, peso) => { if (nome) resultado.conceitos.push({ nome, peso }); };

    for (const s of estados) {
      const d = dados.get(String(s.id)) ?? {};
      const fonteUf = `${fonteLocalidades}/estados/${s.sigla}`;
      const doEstado = base.municipios.filter((m) => m.uf === s.sigla);
      const capital = CAPITAIS[s.sigla];
      const capitalConfere = capital && doEstado.some((m) => m.nome === capital);
      f(`${s.nome} é um estado brasileiro, de sigla ${s.sigla}, localizado na região ${s.regiao} do Brasil (fonte: IBGE).`, fonteUf, CONFIANCA.alta, 'Estado');
      if (capitalConfere) f(`A capital do estado de ${s.nome} é ${capital}.`, fonteUf, CONFIANCA.media, 'Estado');
      if (doEstado.length) f(`${s.nome} tem ${doEstado.length} municípios, segundo a divisão territorial do IBGE.`, fonteUf, CONFIANCA.alta, 'Estado');
      if (d.populacao) f(`${s.nome} tinha ${formatarInteiro(d.populacao)} habitantes no Censo de ${d.ano} (fonte: IBGE).`, urlDados, CONFIANCA.alta, 'População');
      if (d.area) f(`A área territorial de ${s.nome} é de ${formatarDecimal(d.area)} km² (fonte: IBGE, Censo ${d.ano}).`, urlDados, CONFIANCA.alta, 'Área');
      if (d.densidade) f(`A densidade demográfica de ${s.nome} é de ${formatarDecimal(d.densidade)} habitantes por km² no Censo de ${d.ano} (fonte: IBGE).`, urlDados, CONFIANCA.alta, 'População');
      a('Sigla', s.sigla, fonteUf);
      a('Região', s.regiao, fonteUf);
      a('Código IBGE', String(s.id), fonteUf);
      if (capitalConfere) a('Capital', capital, fonteUf);
      if (doEstado.length) a('Número de municípios', String(doEstado.length), fonteUf);
      if (d.populacao) a(`População (Censo ${d.ano})`, `${formatarInteiro(d.populacao)} habitantes`, urlDados);
      if (d.area) a('Área (km²)', formatarDecimal(d.area), urlDados);
      if (d.densidade) a('Densidade demográfica (hab./km²)', formatarDecimal(d.densidade), urlDados);
      conceito(s.regiao, 0.6);
      if (capitalConfere) conceito(capital, 0.8);
    }

    // principal = o mais populoso (sem número de população, o primeiro da lista do IBGE)
    const ordenados = [...candidatos].sort((x, y) => (dados.get(String(y.id))?.populacao ?? -1) - (dados.get(String(x.id))?.populacao ?? -1));
    const [principal, ...outros] = ordenados;
    if (principal) {
      const m = principal;
      const d = dados.get(String(m.id)) ?? {};
      const fonteMun = `${fonteLocalidades}/municipios/${m.id}`;
      const lugar = `${m.nome} (${m.uf})`;
      f(`${m.nome} é um município do estado de ${m.ufNome} (${m.uf}), na região ${m.regiao} do Brasil${d.populacao ? `, com ${formatarInteiro(d.populacao)} habitantes no Censo de ${d.ano}` : ''} (fonte: IBGE).`, d.populacao ? urlDados : fonteMun, CONFIANCA.alta, 'Município');
      if (d.area) f(`A área territorial de ${m.nome} (${m.uf}) é de ${formatarDecimal(d.area)} km² (fonte: IBGE, Censo ${d.ano}).`, urlDados, CONFIANCA.alta, 'Área');
      if (d.densidade) f(`A densidade demográfica de ${m.nome} (${m.uf}) é de ${formatarDecimal(d.densidade)} habitantes por km² no Censo de ${d.ano} (fonte: IBGE).`, urlDados, CONFIANCA.alta, 'População');
      if (m.imediata && m.intermediaria) f(`${m.nome} (${m.uf}) pertence à Região Geográfica Imediata de ${m.imediata} e à Região Geográfica Intermediária de ${m.intermediaria}, segundo o IBGE.`, fonteMun, CONFIANCA.alta, 'Território');
      if (m.microrregiao && m.mesorregiao) f(`${m.nome} (${m.uf}) fica na microrregião de ${m.microrregiao}, dentro da mesorregião ${m.mesorregiao}, segundo o IBGE.`, fonteMun, CONFIANCA.alta, 'Território');
      if (CAPITAIS[m.uf] === m.nome) f(`${m.nome} é a capital do estado de ${m.ufNome}.`, fonteMun, CONFIANCA.media, 'Município');
      for (const o of outros.slice(0, MAX_HOMONIMOS - 1)) {
        const od = dados.get(String(o.id)) ?? {};
        f(`Existe também um município chamado ${o.nome} no estado de ${o.ufNome} (${o.uf})${od.populacao ? `, com ${formatarInteiro(od.populacao)} habitantes no Censo de ${od.ano}` : ''} (fonte: IBGE).`, od.populacao ? urlDados : `${fonteLocalidades}/municipios/${o.id}`, CONFIANCA.alta, 'Município');
      }

      a('UF', `${m.ufNome} (${m.uf})`, fonteMun);
      a('Região', m.regiao, fonteMun);
      a('Código IBGE', String(m.id), fonteMun);
      if (d.populacao) a(`População (Censo ${d.ano})`, `${formatarInteiro(d.populacao)} habitantes`, urlDados);
      if (d.area) a('Área (km²)', formatarDecimal(d.area), urlDados);
      if (d.densidade) a('Densidade demográfica (hab./km²)', formatarDecimal(d.densidade), urlDados);
      a('Microrregião', m.microrregiao, fonteMun);
      a('Mesorregião', m.mesorregiao, fonteMun);
      a('Região Geográfica Imediata', m.imediata, fonteMun);
      a('Região Geográfica Intermediária', m.intermediaria, fonteMun);
      conceito(m.ufNome, 0.9);
      conceito(m.microrregiao, 0.5);
      conceito(m.regiao, 0.4);
      resultado.metadados = { titulo: lugar, idioma: 'pt-BR', url: d.populacao ? urlDados : fonteMun };
    } else if (estados[0]) {
      resultado.metadados = { titulo: `${estados[0].nome} (${estados[0].sigla})`, idioma: 'pt-BR', url: `${fonteLocalidades}/estados/${estados[0].sigla}` };
    }
    return resultado;
  },
};
