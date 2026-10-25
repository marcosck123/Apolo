// O ciclo de um pensamento:
// mensagem → embedding → sementes → cascata no grafo → memória de trabalho
//          → (LLM raciocina) → grava episódio + reforça sinapses (Hebb)
import { embutir } from './embeddings.js';
import { hebb, propagar } from './nucleo/cerebro.js';

export function criarApolo({ repo, embutirTexto = embutir, raciocinar = null }) {
  return {
    // Ensina um fato/conceito/habilidade: cria o neurônio e o liga aos mais parecidos.
    async lembrar({ conteudo, tipo = 'fato', origem = 'usuario' }) {
      const embedding = embutirTexto(conteudo);
      const parecidos = await repo.similares(embedding, { limite: 3 });
      const neuronio = await repo.criarNeuronio({ tipo, conteudo, embedding, origem });
      await repo.salvarSinapses(
        parecidos.map((p) => ({
          de: Math.min(p.id, neuronio.id),
          para: Math.max(p.id, neuronio.id),
          peso: p.sim * 0.5,
        })),
      );
      return neuronio;
    },

    // `raciocinar({ mensagem, memoria })` é o lobo frontal (o LLM); opcional.
    async pensar(mensagem, { tamanhoMemoria = 15 } = {}) {
      const embedding = embutirTexto(mensagem);
      const sementes = (await repo.similares(embedding)).map((s) => ({ id: s.id, forca: s.sim }));

      const cerebro = await repo.carregarSubgrafo(sementes.map((s) => s.id));
      const ativos = propagar(cerebro, sementes, { topN: tamanhoMemoria });
      const memoria = ativos.map((a) => ({ ...cerebro.neuronios.get(a.id), ativacao: a.ativacao }));

      const resposta = raciocinar ? await raciocinar({ mensagem, memoria }) : null;

      const episodio = await repo.criarNeuronio({
        tipo: 'episodio',
        conteudo: resposta ? `${mensagem}\n→ ${resposta}` : mensagem,
        embedding,
      });
      cerebro.adicionarNeuronio(episodio);

      const disparos = [...ativos, { id: episodio.id, ativacao: 1 }];
      await repo.marcarUso(ativos.map((a) => a.id));
      await repo.salvarSinapses(hebb(cerebro, disparos));

      return { memoria, resposta, episodioId: episodio.id };
    },

    dormir: (opcoes) => repo.consolidar(opcoes),
  };
}
