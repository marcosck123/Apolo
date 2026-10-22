// Camada de intenção: entende o tipo de mensagem (saudação, despedida...) e escolhe a resposta,
// sem passar pelo córtex. O que não for reconhecido segue para o córtex.
// Os grupos vêm do banco; aqui eles viram um índice em memória (frase → grupo), consultado direto.
export const normalizar = (texto) =>
  texto.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();

// Palavras de enfeite: não contam como assunto ("oi você", "muito obrigado", "tudo bem?").
const PALAVRAS_VAZIAS = new Set(['voce', 'a', 'o', 'ai', 'ae', 'pra', 'para', 'de', 'e', 'ta', 'tudo', 'bem', 'muito', 'por', 'favor']);

// grupos: [{ nome, frases: [string], respostas: [{ texto, quando? }] }]
export function criarDetector(grupos) {
  const indice = new Map(); // frase normalizada → grupo
  const porNome = new Map();
  let maiorFrase = 1;
  for (const g of grupos) {
    porNome.set(g.nome, g);
    for (const f of g.frases) {
      const frase = normalizar(f);
      if (!frase) continue;
      indice.set(frase, g);
      maiorFrase = Math.max(maiorFrase, frase.split(' ').length);
    }
  }

  return {
    grupos: () => grupos,

    // Varre as palavras uma vez, casando sempre a frase mais longa possível.
    detectar(mensagem, { sortear = Math.random } = {}) {
      const palavras = normalizar(mensagem).split(' ').filter(Boolean);
      const achadas = []; // { frase, grupo }
      let sobrou = false;
      for (let i = 0; i < palavras.length; ) {
        let casou = null;
        for (let n = Math.min(maiorFrase, palavras.length - i); n >= 1 && !casou; n--) {
          const frase = palavras.slice(i, i + n).join(' ');
          if (indice.has(frase)) casou = { frase, tamanho: n, grupo: indice.get(frase) };
        }
        if (casou) {
          achadas.push(casou);
          i += casou.tamanho;
        } else {
          if (!PALAVRAS_VAZIAS.has(palavras[i])) sobrou = true;
          i++;
        }
      }
      // Sem frase conhecida, ou com outro assunto junto ("oi, que horas são?"): vai para o córtex.
      if (achadas.length === 0 || sobrou) return null;

      const grupo = achadas[0].grupo;
      const ditas = new Set(achadas.filter((a) => a.grupo === grupo).map((a) => a.frase));
      const sob_medida = grupo.respostas.filter((r) => r.quando && ditas.has(r.quando));
      const gerais = grupo.respostas.filter((r) => !r.quando);
      const opcoes = sob_medida.length ? sob_medida : gerais.length ? gerais : grupo.respostas;
      if (opcoes.length === 0) return null;
      return { intencao: grupo.nome, resposta: opcoes[Math.floor(sortear() * opcoes.length)].texto };
    },
  };
}
