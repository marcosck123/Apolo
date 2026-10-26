// Adaptador do Mundo Educação (mundoeducacao.uol.com.br) — artigos escolares em português.
//
// Pertence ao mesmo grupo do Brasil Escola (Rede Omnia) e tem a mesma estrutura de página, então reaproveita as funções puras de
// brasilescola.js. Licença e regras de uso são as mesmas: Termos de Uso (mundoeducacao.uol.com.br/termos-uso) = conteúdo protegido, sem
// licença aberta, "raspagem ou extração massiva" só com autorização. Aqui: uma página por vez, só frases curtas com a URL da fonte.
// robots.txt: Allow: / e só proíbe /imprimir/ e /busca?q= — por isso NÃO usamos a busca do site.
//
// Como acha a página: com `url` do Mundo Educação usa direto (1 requisição). Sem `url`, só tenta ADIVINHAR até 3 endereços
// <categoria>/<tema-em-slug>.htm para perguntas de definição ("média aritmética" → /matematica/media-aritmetica.htm) e só aceita se o
// título da página bater com o tema. Nos outros tipos de pergunta, sem `url`, devolve null sem gastar requisição.
//
// Além do que o Brasil Escola extrai: termos em negrito do parágrafo de abertura viram `conceitos`, a definição vira fato de confiança
// média e as seções "Exemplo N" viram fatos do tipo exemplo (enunciado + resultado quando o texto traz).
import { extrairDeSite } from './brasilescola.js';

const LICENCA = 'Todos os direitos reservados (Rede Omnia, Termos de Uso): sem licença aberta; guardar só frases curtas com a fonte';

const CATEGORIAS = {
  definicao: ['matematica', 'fisica', 'quimica', 'biologia', 'geografia', 'historia', 'gramatica', 'filosofia', 'sociologia'],
};

const adaptador = {
  nome: 'mundoeducacao',
  licenca: LICENCA,
  tipos: ['definicao', 'geral'],
  dominios: ['mundoeducacao.uol.com.br'],
  async extrair({ tema = '', consulta = '', tipo = 'geral', url = null } = {}, ctx) {
    return extrairDeSite(adaptador, { tema: tema || consulta, tipo, url, dominio: 'mundoeducacao.uol.com.br', categorias: CATEGORIAS, tiposQueAdivinham: ['definicao'] }, ctx);
  },
};
export default adaptador;
