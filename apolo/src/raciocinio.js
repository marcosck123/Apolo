// Raciocínio sobre a memória: o córtex só continua textos e não sabe usar o que o Apolo lembrou.
// Aqui a pergunta é comparada com os fatos ativados e, se um deles responde, a resposta é a frase
// desse fato (com a fonte, quando veio da internet). Sem fato que cubra a pergunta, devolve null
// e a mensagem segue para o córtex.
import { normalizar } from './intencoes.js';

// Palavras de pergunta e de ligação: não dizem sobre o que se pergunta.
const VAZIAS = new Set([
  'a', 'o', 'as', 'os', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas',
  'e', 'ou', 'que', 'qual', 'quais', 'quem', 'quando', 'onde', 'como', 'porque', 'por', 'para', 'pra', 'com', 'se',
  'me', 'te', 'diga', 'fale', 'sabe', 'explique', 'explica', 'conte', 'defina', 'descreva', 'mostre', 'significa', 'significado', 'conceito', 'definicao', 'pode', 'poderia', 'voce', 'eu', 'ao', 'aos', 'sobre', 'eh', 'foi', 'sao', 'era',
  'ser', 'tem', 'tinha', 'mais', 'muito', 'meu', 'minha', 'seu', 'sua', 'ele', 'ela',
]);

// Tira o plural simples para "capitais"/"capital" e "gatos"/"gato" se encontrarem.
const raiz = (p) => (p.length > 4 && p.endsWith('s') ? p.slice(0, -1) : p);

export const palavrasChave = (texto) =>
  new Set(normalizar(texto).split(' ').filter((p) => p && !VAZIAS.has(p)).map(raiz));

// O título vem separado do resumo por " :: " (títulos de página têm ":" e "–" à vontade).
const FATO_DA_WEB = /^(.*?) :: (.*) \(fonte: (\S+)\)$/s;
const FRASES = /(?<=[.!?])\s+(?=[A-ZÀ-Ý0-9])/u;

// Títulos de página terminam com o nome do SITE ("... - Brasil Escola", "Rondônia – Wikipédia, a enciclopédia livre").
// Isso não é assunto: sem tirar, "Brasil Escola" fazia um fato sobre Rondônia casar com "capital do Brasil".
export function tituloDoAssunto(titulo) {
  const partes = titulo.split(/\s+[-–—|]\s+/);
  return (partes.length > 1 ? partes.slice(0, -1) : partes).join(' - ').trim();
}

// Separa um fato em título, frases e fonte. Fatos ensinados à mão não têm título nem fonte.
export function abrirFato(conteudo) {
  // Também sai a pronúncia entre parênteses ("(AFI: [...])"): é ruído para quem lê a resposta.
  const limpo = conteudo.split('\n')[0].replace(/\[\d+\]/g, '').replace(/\s*\((?:AFI|IPA)\b[^)]*\)/g, '').replace(/\s+/g, ' ').trim();
  const partes = limpo.match(FATO_DA_WEB);
  const [titulo, corpo, fonte] = partes ? [partes[1], partes[2], partes[3]] : ['', limpo, null];
  return { titulo, frases: corpo.replace(/\s*…\s*Leia mais$/u, ' …').split(FRASES).filter(Boolean), fonte };
}

const dominio = (url) => {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return null;
  }
};
const cortar = (texto, max) => (texto.length > max ? `${texto.slice(0, max - 1).trimEnd()}…` : texto);

// Compara notas na ordem: a primeira diferença decide.
const maior = (a, b) => {
  const i = a.findIndex((n, k) => n !== b[k]);
  return i !== -1 && a[i] > b[i];
};

// memoria: neurônios ativados ({ id, tipo, conteudo, ativacao }). Devolve { resposta, neuronioId } ou null.
export function responderDaMemoria({ mensagem, memoria, minimoCobertura = 0.75 }) {
  const procura = palavrasChave(mensagem);
  if (procura.size === 0) return null;

  let melhor = null;
  for (const neuronio of memoria) {
    if (!['fato', 'habilidade'].includes(neuronio.tipo)) continue;
    if (neuronio.tipo === 'habilidade') {
      const chaves = palavrasChave(neuronio.conteudo.split('\n')[0]);
      const diretas = [...procura].filter((p) => chaves.has(p)).length;
      const cobertura = diretas / procura.size;
      const nota = [cobertura, diretas, neuronio.ativacao ?? 0];
      if (diretas && cobertura >= minimoCobertura && (!melhor || maior(nota, melhor.nota))) {
        melhor = { nota, habilidade: neuronio.conteudo, neuronioId: neuronio.id };
      }
      continue;
    }
    const { titulo, frases, fonte } = abrirFato(neuronio.conteudo);
    const doTitulo = palavrasChave(tituloDoAssunto(titulo));
    for (const frase of frases) {
      const daFrase = palavrasChave(frase);
      const diretas = [...procura].filter((p) => daFrase.has(p)).length;
      const cobertas = [...procura].filter((p) => daFrase.has(p) || doTitulo.has(p)).length;
      const cobertura = cobertas / procura.size;
      if (diretas === 0 || cobertura < minimoCobertura) continue;
      // Cobre mais a pergunta > a frase fala mais dela > a frase ABRE com o assunto (a definição) > fato mais ativado.
      const abre = procura.has([...palavrasChave(frase.slice(0, 40))][0]) ? 1 : 0;
      const nota = [cobertura, diretas, abre, neuronio.ativacao ?? 0];
      if (!melhor || maior(nota, melhor.nota)) {
        melhor = { nota, frase, fonte, neuronioId: neuronio.id };
      }
    }
  }
  if (!melhor) return null;
  if (melhor.habilidade) return { resposta: melhor.habilidade, neuronioId: melhor.neuronioId };
  const origem = melhor.fonte ? dominio(melhor.fonte) : null;
  return { resposta: cortar(melhor.frase, 280) + (origem ? ` (fonte: ${origem})` : ''), neuronioId: melhor.neuronioId };
}

const INTERROGATIVAS = /^(((me|pode|poderia|consegue) )*(explique|explica|explicar|fale|fala|falar|diga|dizer|conte|contar|defina|descreva|mostre) |qual|quais|quem|quando|onde|como|quanto|quantos|quantas|quanta|por que|porque|o que|que|existe|existem)\b/;

// Pergunta de fato: o córtex não sabe respondê-la, só inventa; sem memória, o certo é admitir.
export const ehPergunta = (mensagem) => mensagem.trim().endsWith('?') || INTERROGATIVAS.test(normalizar(mensagem));
