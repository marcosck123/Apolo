// Classifica a pergunta para o roteador escolher os adaptadores certos. Puro e sem rede.
// O serviço de pesquisa é uma imagem separada do app e não enxerga src/, então a normalização é local.
const normalizar = (texto) =>
  texto.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();

const PADROES = [
  ['codigo', /\b(python|javascript|typescript|sql|git|docker|codigo|funcao|script|programacao|array|lista em|bash|node)\b/],
  ['pessoa', /^(quem (foi|e|era|e o|e a|foram|sao))\s+(.+)/],
  ['lugar', /^(onde (fica|e|esta)|qual (e )?(a )?(capital|populacao|area|sigla)|(capital|populacao|area|municipios?) (de|do|da))\s*(.*)/],
  ['definicao', /^(o que (e|sao|significa|quer dizer)|qual (e )?(o )?(significado|conceito|definicao) (de|do|da)|defina|me explique|explique)\s+(.+)/],
];

const ARTIGOS = /^(a|o|as|os|um|uma|de|do|da|dos|das)\s+/;

// Devolve { tipo, tema }: o tipo decide os adaptadores, o tema é o que se procura ("astrologia").
export function classificar(mensagem) {
  const texto = normalizar(mensagem);
  for (const [tipo, padrao] of PADROES) {
    const m = texto.match(padrao);
    if (!m) continue;
    const resto = (tipo === 'codigo' ? texto : m[m.length - 1] ?? texto).replace(/\b(e|era|foi)\s+/, '');
    let tema = resto;
    for (let i = 0; i < 3; i++) tema = tema.replace(ARTIGOS, '');
    return { tipo, tema: tema.replace(/\s+/g, ' ').trim() || texto };
  }
  return { tipo: 'geral', tema: texto.replace(/^(me diga|fale sobre|sobre)\s+/, '').trim() };
}
