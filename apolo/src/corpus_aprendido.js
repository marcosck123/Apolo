export const ORIGENS_PADRAO = ['executor', 'estudo'];

export function montarCorpusAprendido(neuronios, { origens = ORIGENS_PADRAO } = {}) {
  const vistos = new Set(), blocos = [], porOrigem = Object.fromEntries(origens.map((o) => [o, 0]));
  for (const n of neuronios) {
    if (!origens.includes(n.origem) || !['habilidade', 'conceito', 'fato'].includes(n.tipo)) continue;
    // Preserva indentação do Python; só retira linhas vazias e normaliza quebras.
    const bloco = String(n.conteudo ?? '').replace(/\r\n?/g, '\n').split('\n').filter((l) => l.trim()).join('\n').trimEnd();
    if (!bloco.trim() || vistos.has(bloco)) continue;
    vistos.add(bloco);
    blocos.push(bloco);
    porOrigem[n.origem]++;
  }
  return { texto: blocos.join('\n\n') + (blocos.length ? '\n' : ''), porOrigem };
}
