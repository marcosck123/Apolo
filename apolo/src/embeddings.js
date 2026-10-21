// Embedding local e determinístico (bag-of-words com hashing), só para desenvolver e testar
// sem depender de API. Captura sobreposição de palavras, NÃO semântica — para o Apolo
// "entender de verdade", troque `embutir` por um modelo real (e ajuste DIMENSOES + schema.sql).

export const DIMENSOES = 256;

const PALAVRAS_VAZIAS = new Set([
  'a', 'o', 'as', 'os', 'e', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas',
  'um', 'uma', 'para', 'por', 'com', 'que', 'se', 'como', 'ao', 'ou',
]);

const fnv1a = (texto) => {
  let h = 0x811c9dc5;
  for (let i = 0; i < texto.length; i++) {
    h ^= texto.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h;
};

const tokenizar = (texto) =>
  texto
    .toLowerCase()
    .normalize('NFD')
    .replace(/\p{M}/gu, '')
    .split(/[^a-z0-9]+/)
    .filter((t) => t && !PALAVRAS_VAZIAS.has(t));

export function embutir(texto) {
  const vetor = new Array(DIMENSOES).fill(0);
  for (const token of tokenizar(texto)) {
    const h = fnv1a(token);
    vetor[h % DIMENSOES] += (h >>> 31) & 1 ? -1 : 1;
  }
  const norma = Math.hypot(...vetor);
  return norma === 0 ? vetor : vetor.map((v) => v / norma);
}

export const similaridade = (a, b) => a.reduce((soma, v, i) => soma + v * b[i], 0);
