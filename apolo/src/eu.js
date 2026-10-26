// Perguntas sobre o próprio Apolo ("como você funciona?", "quem é você?"): a resposta vem do que ele realmente é.
// Sem isso, "você" era pesquisado na internet como o pronome e a resposta falava dos reis de Portugal.
import { normalizar } from './intencoes.js';

const SOBRE_MIM = [
  { quando: /\b(como|de que jeito|de que forma) (voce|tu) (funciona|e feito|foi feito|pensa|aprende|lembra)\b|\bcomo (e )?(o )?(seu|teu) funcionamento\b/,
    resposta: 'Eu tenho uma memória em forma de grafo: neurônios guardam fatos e lembranças, e sinapses ligam o que aparece junto. '
      + 'Quando você fala, a lembrança ativa os neurônios ligados, e eu respondo pelo que lembro. '
      + 'Se não sei, pesquiso na internet, guardo o que achei com a fonte e respondo. '
      + 'Para programação, rodo o código num ambiente isolado antes de mostrar. Meu córtex (um modelo de linguagem pequeno) só continua textos e ainda erra bastante.' },
  { quando: /\b(quem|o que) (e|eh|sao) (voce|tu)\b|\bvoce (e|eh) (o que|quem)\b|\bo que significa voce\b|\bquem (e|eh) (o )?apolo\b|\bo que (e|eh) (o )?apolo\b/,
    resposta: 'Eu sou o Apolo: uma memória em grafo (neurônios e sinapses) com um córtex próprio, um modelo de linguagem pequeno que o Marcos está treinando. '
      + 'Aprendo conversando e pesquisando, e posso esquecer o que aprendi na internet se você pedir.' },
  { quando: /\b(quem|o que) (te|lhe) (criou|fez|programou|desenvolveu|construiu)\b|\bquem (e|eh) (o )?(seu|teu) (criador|dono|autor)\b/,
    resposta: 'Fui criado pelo Marcos, em Vilhena-RO, como um projeto de memória em grafo com um córtex treinado do zero.' },
  { quando: /\b(o que|que) (voce|tu) (sabe|pode|consegue) (fazer|dizer)\b|\bpara que (voce )?(serve|voce serve)\b/,
    resposta: 'Converso, lembro do que já aprendi, pesquiso na internet o que não sei (com a fonte), mostro código que rodei de verdade e esqueço o que veio da web se você mandar. '
      + 'Não invento fatos: sem fonte eu digo que não sei.' },
];

// Devolve a resposta sobre si mesmo, ou null se a mensagem não é sobre o Apolo.
export function responderSobreMim(mensagem) {
  const t = normalizar(mensagem).replace(/^pesquise\s+/, '').replace(/\boque\b/g, 'o que');
  return SOBRE_MIM.find((s) => s.quando.test(t))?.resposta ?? null;
}
