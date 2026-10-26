import { embutir, similaridade } from './embeddings.js';

// Descrições revisáveis; nomes desconhecidos não recebem explicações inventadas.
export const DESCRICOES = {
  sum: '`sum` soma os itens de um iterável, a partir de um valor inicial.',
  len: '`len` devolve a quantidade de itens de um objeto.',
  'statistics.mean': '`statistics.mean` calcula a média aritmética dos dados.',
  statistics: '`statistics` reúne funções de estatística em Python.',
  math: '`math` reúne funções matemáticas em Python.',
  for: '`for` percorre os itens de um iterável.',
  while: '`while` repete um bloco enquanto a condição for verdadeira.',
  if: '`if` executa um bloco quando a condição for verdadeira.',
  try: '`try` delimita um bloco em que exceções podem ser tratadas.',
  with: '`with` usa um gerenciador de contexto.',
  comprehension: 'Uma compreensão constrói uma coleção ou um gerador a partir de um iterável.',
  lambda: '`lambda` define uma função anônima.',
  class: '`class` define uma classe.',
  def: '`def` define uma função.',
  return: '`return` encerra a função e devolve um valor.',
  yield: '`yield` produz um valor e suspende um gerador.',
};
export const ERROS = {
  ZeroDivisionError: 'Ocorreu uma divisão por zero.',
  TypeError: 'Uma operação recebeu um tipo incompatível.',
  ValueError: 'Um argumento tem valor inadequado para a operação.',
  IndexError: 'Um índice está fora dos limites da sequência.',
  KeyError: 'Uma chave solicitada não foi encontrada.',
  NameError: 'Um nome utilizado não está definido.',
};

// Troca um único trecho AST por vez. A semente fixa 17 torna os exemplos reproduzíveis.
export function criarVariacoes(codigo, trechos = []) {
  const letras = Array.from(codigo);
  const trocar = (t, valor) => letras.slice(0, t.inicio).join('') + valor + letras.slice(t.fim).join('');
  const simples = trechos.filter((t) => ['numero', 'texto'].includes(t.tipo));
  return {
    exemplos: [...new Set(simples.slice(0, 5).map((t, i) => trocar(t, t.tipo === 'numero' ? String(17 + i) : '"exemplo de estudo"')))],
    erros: [...new Set([
      ...trechos.filter((t) => t.tipo === 'lista').slice(0, 1).map((t) => trocar(t, '[]')),
      ...simples.filter((t) => t.tipo === 'numero').slice(0, 1).map((t) => trocar(t, '"texto"')),
    ])],
  };
}

export function criarEstudante({ repo, lembrar, analisar, executar, registrar = () => {},
  ocioso = () => true, intervalo = 5000, habilitado = true, agendar = setInterval }) {
  let ocupado = false;
  async function passo() {
    if (!habilitado || ocupado || !ocioso()) return;
    ocupado = true;
    let estudo;
    try {
      estudo = await repo.pegarEstudoPendente();
      if (!estudo) return;
      const habilidade = await repo.buscarNeuronio(estudo.neuronio_id);
      const partes = habilidade?.conteudo.match(/^([^\n]+)\nExemplo:\n([\s\S]*?)\nSaída:\n/);
      if (!partes) {
        await repo.marcarEstudo(estudo.id, 'falhou', { motivo: 'habilidade sem exemplo e saída' });
        return;
      }
      const [, pergunta, codigo] = partes;
      const analise = await analisar?.({ linguagem: 'python', codigo });
      if (!analise) throw new Error('analisador indisponível');
      const resumo = { conceitos: 0, exemplos: 0, erros: 0 };
      async function guardar(tipo, conteudo) {
        return await repo.buscarConteudo(conteudo) ?? lembrar({ tipo, conteudo, origem: 'estudo' });
      }
      for (const nome of new Set([...analise.chamadas, ...analise.importacoes, ...analise.estruturas])) {
        if (!Object.hasOwn(DESCRICOES, nome)) continue;
        const conceito = await guardar('conceito', DESCRICOES[nome]);
        // Mesmo critério de lembrar: cosseno positivo, com fator 0,5; sem peso arbitrário adicional.
        const peso = Math.max(0, similaridade(embutir(habilidade.conteudo), embutir(conceito.conteudo))) * 0.5;
        await repo.salvarSinapses([{ de: Math.min(conceito.id, habilidade.id), para: Math.max(conceito.id, habilidade.id), peso }]);
        resumo.conceitos++;
      }
      const variacoes = criarVariacoes(codigo, analise.trechos);
      for (const [categoria, codigos] of Object.entries(variacoes)) {
        for (const variante of codigos) {
          const resultado = await executar?.({ linguagem: 'python', codigo: variante });
          if (!resultado || typeof resultado.saida !== 'string' || typeof resultado.erro !== 'string') throw new Error('executor indisponível');
          if (resultado.estourou_tempo) continue;
          if (!resultado.erro && categoria === 'exemplos') {
            await guardar('habilidade', `${pergunta}\nExemplo:\n${variante}\nSaída:\n${resultado.saida.trimEnd()}`);
            resumo.exemplos++;
          } else if (resultado.erro && categoria === 'erros') {
            // Só a última linha do traceback (`TypeError: ...`), como nos arquivos de treino: o resto leva caminhos temporários aleatórios.
            const ultimaLinha = resultado.erro.trimEnd().split('\n').at(-1);
            const tipo = ultimaLinha.match(/^(\w+Error):/)?.[1];
            if (!Object.hasOwn(ERROS, tipo)) continue;
            await guardar('habilidade', `${pergunta}\nExemplo:\n${variante}\nErro:\n${ultimaLinha}\n${ERROS[tipo]}`);
            resumo.erros++;
          }
        }
      }
      await repo.marcarEstudo(estudo.id, 'aprendido', resumo);
      registrar('estudou', { neuronioId: habilidade.id, texto: `${pergunta}: conceitos: ${resumo.conceitos}; exemplos: ${resumo.exemplos}; erros reais: ${resumo.erros}.` });
    } catch (erro) {
      if (estudo) {
        try { await repo.marcarEstudo(estudo.id, estudo.tentativas >= 3 ? 'falhou' : 'pendente', { motivo: String(erro.message) }); } catch { /* tenta novamente após a concessão expirar */ }
      }
      registrar('erro', { texto: `Estudo: ${erro.message}` });
    } finally { ocupado = false; }
  }
  let timer;
  return { passo, iniciar() { if (habilitado && !timer) { timer = agendar(passo, intervalo); timer.unref?.(); } }, parar() { clearInterval(timer); timer = null; } };
}
