// Contrato dos adaptadores de conhecimento.
//
// Um adaptador sabe tirar conhecimento de UMA fonte (um site ou uma API). Ele exporta por padrão:
//
//   export default {
//     nome: 'wikipedia',                  // identifica o adaptador no log e nos fatos
//     licenca: 'CC BY-SA 4.0',            // licença do conteúdo (vai em cada fato)
//     tipos: ['definicao', 'pessoa'],     // para que tipos de pergunta serve (ver tipo.js)
//     dominios: ['pt.wikipedia.org'],     // quais endereços ele reconhece, quando recebe uma URL
//     async extrair({ consulta, tema, tipo, url }, ctx) { ... }   // devolve um resultado (abaixo) ou null
//   };
//
// `ctx` (veja ctx.js) dá o necessário sem o adaptador saber de rede nem de DOM:
//   ctx.buscar(url, { json?: true })  → { status, texto, json } (fetch com User-Agent, tempo limite, cache e proteção SSRF)
//   ctx.parsear(html)                 → document (linkedom), para extrair com querySelector
//   ctx.navegador(url, fn)            → roda `fn(pagina)` no Chromium (só para páginas que exigem JavaScript)
//   ctx.registrar(msg)                → linha de log
// Nos testes, `ctx` é falso e devolve páginas salvas em tests/fixtures/<adaptador>/.
//
// Resultado de `extrair` (todo campo é opcional; use listas vazias, nunca undefined):
//   fatos:     [{ texto, secao?, fonte, confianca }]        frases completas e autossuficientes
//   conceitos: [{ nome, url?, peso }]                       temas relacionados (viram neurônios e sinapses); peso 0..1
//   pares:     [{ pergunta, resposta, fonte }]              perguntas e respostas prontas (FAQ)
//   codigos:   [{ linguagem, codigo, explicacao, fonte }]
//   atributos: [{ nome, valor, fonte }]                     dados exatos (infobox, Wikidata): capital, população...
//   metadados: { titulo, idioma, data?, url }
//
// Use `fato()`, `par()` e `atributo()` abaixo para montar os itens: eles limpam o texto e preenchem a licença.

export const CONFIANCA = { alta: 'alta', media: 'media', baixa: 'baixa' };

// Ruído que aparece no texto copiado de páginas: notas [1], [nota 2], "Expandir", CSS solto, espaços estranhos.
export function limparTexto(texto) {
  return String(texto ?? '')
    .replace(/\[(?:\d+|nota \d+|[a-z]|carece de fontes|citation needed)\]/gi, '')
    .replace(/\.mw-parser-output[^}]*\}/g, '')
    .replace(/\b(?:Expandir|Ocultar|Mostrar|Recolher) (?:lista|tudo)\b ?\d*/gi, '')
    .replace(/[\u200b\u00a0¶]/g, ' ')
    .replace(/\s+/g, ' ')
    .replace(/\s+([,.;:!?])/g, '$1')
    .replace(/\(\s+/g, '(').replace(/\s+\)/g, ')') // "( 2026 )" → "(2026)"
    .trim();
}

// Uma frase só vira fato se tiver tamanho de frase e parecer texto (não menu nem lixo).
export function pareceFrase(texto) {
  const t = limparTexto(texto);
  return t.length >= 30 && t.length <= 400 && /[a-zA-ZÀ-ú]{3,}\s+[a-zA-ZÀ-ú]{2,}/.test(t) && !/^\W/.test(t) && !/(cookies|assine|newsletter|todos os direitos)/i.test(t)
    && !/^(clique|saiba|leia|conhe[cç]a|descubra|aprenda|veja|confira|acesse|inscreva)/i.test(t); // chamadas de marketing não são fatos
}

export const fato = (adaptador, { texto, secao = null, fonte, confianca = CONFIANCA.media }) =>
  ({ texto: limparTexto(texto), secao: secao ? limparTexto(secao) : null, fonte, confianca, adaptador: adaptador.nome, licenca: adaptador.licenca });

export const par = (adaptador, { pergunta, resposta, fonte }) =>
  ({ pergunta: limparTexto(pergunta), resposta: limparTexto(resposta), fonte, adaptador: adaptador.nome, licenca: adaptador.licenca });

export const atributo = (adaptador, { nome, valor, fonte }) =>
  ({ nome: limparTexto(nome), valor: limparTexto(valor), fonte, adaptador: adaptador.nome, licenca: adaptador.licenca });

export const resultadoVazio = () => ({ fatos: [], conceitos: [], pares: [], codigos: [], atributos: [], metadados: {} });

// Garante o formato inteiro, mesmo que o adaptador devolva só parte dele.
export const completar = (r) => ({ ...resultadoVazio(), ...(r ?? {}) });
