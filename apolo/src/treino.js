// Lê o log de treino do córtex (cerebro/treino.log, escrito por `cortex_v0.py treinar`) para o painel.
import { readFile, stat } from 'node:fs/promises';

const LINHA_PASSO = /^passo\s+(\d+) \| perda treino ([\d.]+) \| perda val ([\d.]+) \| (\d+)s/;

export function lerTreino(texto) {
  const passos = [];
  let total = null;
  for (const linha of texto.split('\n')) {
    const p = LINHA_PASSO.exec(linha);
    if (p) passos.push({ passo: +p[1], treino: +p[2], val: +p[3], segundos: +p[4] });
    const t = /^passos: (\d+)/.exec(linha);
    if (t) total = +t[1];
  }
  const dispositivo = /^dispositivo: (\S+)/m.exec(texto)?.[1] ?? null;
  const concluido = /^salvo em /m.test(texto);
  const amostra = concluido ? texto.split('--- o córtex escreve ---')[1]?.trim() ?? null : null;
  return { passos, total, dispositivo, concluido, amostra };
}

// `treinando` = o log mudou há pouco e ainda não saiu a linha "salvo em".
export async function carregarTreino(caminho = process.env.TREINO_LOG ?? 'cerebro/treino.log') {
  try {
    const [texto, info] = await Promise.all([readFile(caminho, 'utf8'), stat(caminho)]);
    const treino = lerTreino(texto);
    const recente = Date.now() - info.mtimeMs < 90_000;
    return { existe: true, treinando: !treino.concluido && recente, atualizadoEm: info.mtime.toISOString(), ...treino };
  } catch (erro) {
    if (erro.code === 'ENOENT') return { existe: false };
    throw erro;
  }
}
