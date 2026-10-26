import { normalizar } from './intencoes.js';

// Triagem conservadora; não substitui o container sem rede e os limites do executor.
export const REGRAS = [
  { nome: 'importação de sistema', padrao: /\b(?:import\s+os\b|from\s+(?:os|shutil)\s+import\b)/ },
  { nome: 'sistema e arquivos', padrao: /\b(?:os\s*\.\s*(?:system|popen|environ|remove|unlink|fork|exec\w*|spawn\w*)|shutil\s*\.\s*rmtree)\b/ },
  { nome: 'processos, rede ou memória nativa', padrao: /\b(?:subprocess|socket|requests|urllib|http|ctypes|multiprocessing)\b/ },
  { nome: 'execução dinâmica', padrao: /\b(?:__import__|eval|exec|compile)\s*\(|__(?:builtins|subclasses|globals|class|bases|mro|code|dict|getattribute|loader|spec)__/ },
  { nome: 'caminho absoluto', padrao: /\bopen\s*\(\s*['"](?:\/|[A-Za-z]:[\\/])/ },
];

export function filtrarCodigo(codigo, { entradas = [] } = {}) {
  if (typeof codigo !== 'string' || !codigo.trim() || codigo.length > 20_000) return { ok: false, motivo: 'código vazio ou muito grande' };
  const regra = REGRAS.find((r) => r.padrao.test(codigo));
  if (regra) return { ok: false, motivo: regra.nome };
  if (/\binput\s*\(/.test(codigo) && !entradas.length) return { ok: false, motivo: 'entrada não simulada' };
  return { ok: true, motivo: null };
}

export const ehPerguntaDeProgramacao = (mensagem) =>
  /\b(?:python|javascript|typescript|sql|git|docker|codigo|funcao|script|programacao)\b|\bprograma em\b/.test(normalizar(mensagem));

function criarCliente({ url, caminho, fetchFn, tempo }) {
  if (!url) return null;
  return async (dados) => {
    try {
      const resposta = await fetchFn(new URL(caminho, url), {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify(dados), signal: AbortSignal.timeout(tempo),
      });
      if (!resposta.ok) return null;
      return await resposta.json();
    } catch {
      return null;
    }
  };
}

export function criarExecutor({ url = process.env.EXECUTOR_URL, fetchFn = fetch } = {}) {
  return criarCliente({ url, caminho: '/executar', fetchFn, tempo: 8000 });
}

export function criarAnalisador({ url = process.env.EXECUTOR_URL, fetchFn = fetch } = {}) {
  return criarCliente({ url, caminho: '/analisar', fetchFn, tempo: 8000 });
}

export function criarBuscadorDeCodigos({ url = process.env.PESQUISA_URL, fetchFn = fetch } = {}) {
  const cliente = criarCliente({ url, caminho: '/codigos', fetchFn, tempo: 120_000 });
  return cliente ? async (consulta) => (await cliente({ consulta, max_paginas: 3 }))?.codigos ?? null : null;
}

export function criarRespostaDeCodigo({ buscar, executar, lembrar, enfileirar = async () => {}, registrar = () => {} }) {
  return async (mensagem) => {
    if (!buscar || !executar) return 'Pesquisa de código ou executor indisponível agora.';
    let candidatos;
    try { candidatos = await buscar(mensagem); } catch { return 'Não consegui pesquisar código agora.'; }
    if (!Array.isArray(candidatos)) return 'Não consegui pesquisar código agora.';
    for (const candidato of candidatos.slice(0, 5)) {
      if (!candidato || candidato.linguagem !== 'python' || !filtrarCodigo(candidato.codigo).ok) continue;
      let fonte;
      try {
        fonte = new URL(candidato.fonte);
        if (!['http:', 'https:'].includes(fonte.protocol)) continue;
      } catch { continue; }
      let resultado;
      try { resultado = await executar({ linguagem: 'python', codigo: candidato.codigo }); } catch { resultado = null; }
      if (!resultado) return 'Não consegui executar o código agora; o executor está indisponível.';
      if (resultado.erro || resultado.estourou_tempo || typeof resultado.saida !== 'string' || !resultado.saida.trim()) continue;
      const conteudo = `${mensagem}\nExemplo:\n${candidato.codigo}\nSaída:\n${resultado.saida.trimEnd()}`;
      // A fonte fica no próprio conteúdo para sobreviver à recuperação da memória e à exportação.
      const resposta = `${conteudo}\n(fonte: ${fonte.hostname.replace(/^www\./, '')})\nRodou sem erro; confira se o resultado resolve a pergunta.`;
      const neuronio = await lembrar({ tipo: 'habilidade', origem: 'executor', conteudo: `${conteudo}\n(fonte: ${fonte.href})\nRodou sem erro; confira se o resultado resolve a pergunta.` });
      if (neuronio?.id) await enfileirar(neuronio.id);
      registrar('codigo', { texto: mensagem, fonte: fonte.href, tempo_ms: resultado.tempo_ms });
      return resposta;
    }
    return null;
  };
}
