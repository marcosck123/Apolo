// Persistência em PostgreSQL + pgvector. Não carrega o grafo inteiro: busca sementes por
// similaridade e puxa só a vizinhança delas, que vira um Cerebro em memória para a cascata.
import pg from 'pg';
import { Cerebro } from './nucleo/cerebro.js';

const comoVetor = (embedding) => `[${embedding.join(',')}]`;

export function criarRepositorio(connectionString = process.env.DATABASE_URL) {
  const pool = new pg.Pool({ connectionString });

  return {
    pool,

    async criarNeuronio({ tipo, conteudo, embedding }) {
      const { rows } = await pool.query(
        `INSERT INTO neuronios (tipo, conteudo, embedding)
         VALUES ($1, $2, $3::vector)
         RETURNING id, tipo, conteudo, vezes_usado, ultimo_uso, criado_em`,
        [tipo, conteudo, comoVetor(embedding)],
      );
      return rows[0];
    },

    async buscarNeuronio(id) {
      const { rows } = await pool.query(
        'SELECT id, tipo, conteudo, vezes_usado, ultimo_uso, criado_em FROM neuronios WHERE id = $1',
        [id],
      );
      return rows[0] ?? null;
    },

    // Sementes: neurônios mais parecidos com o estímulo. sim = similaridade de cosseno (0..1).
    async similares(embedding, { limite = 5, minimo = 0.2 } = {}) {
      const { rows } = await pool.query(
        `SELECT id, 1 - (embedding <=> $1::vector) AS sim
         FROM neuronios
         ORDER BY embedding <=> $1::vector
         LIMIT $2`,
        [comoVetor(embedding), limite],
      );
      return rows.filter((r) => r.sim >= minimo);
    },

    // Expande a vizinhança das sementes por `saltos` níveis e devolve um Cerebro em memória.
    async carregarSubgrafo(ids, { saltos = 3, maxPorSalto = 500 } = {}) {
      const cerebro = new Cerebro();
      const vistos = new Set(ids);
      let fronteira = [...ids];

      for (let i = 0; i < saltos && fronteira.length > 0; i++) {
        const { rows } = await pool.query(
          `SELECT de, para, peso, tipo FROM sinapses
           WHERE de = ANY($1) OR para = ANY($1)
           ORDER BY peso DESC LIMIT $2`,
          [fronteira, maxPorSalto],
        );
        const novos = new Set();
        for (const r of rows) {
          cerebro.definirSinapse(r.de, r.para, r.peso, r.tipo);
          for (const id of [r.de, r.para]) {
            if (!vistos.has(id)) {
              vistos.add(id);
              novos.add(id);
            }
          }
        }
        fronteira = [...novos];
      }

      const { rows } = await pool.query(
        'SELECT id, tipo, conteudo, vezes_usado, ultimo_uso FROM neuronios WHERE id = ANY($1)',
        [[...vistos]],
      );
      for (const n of rows) cerebro.adicionarNeuronio(n);
      return cerebro;
    },

    async marcarUso(ids) {
      if (ids.length === 0) return;
      await pool.query(
        'UPDATE neuronios SET vezes_usado = vezes_usado + 1, ultimo_uso = now() WHERE id = ANY($1)',
        [ids],
      );
    },

    async salvarSinapses(sinapses) {
      if (sinapses.length === 0) return;
      await pool.query(
        `INSERT INTO sinapses (de, para, peso)
         SELECT * FROM unnest($1::int[], $2::int[], $3::float8[])
         ON CONFLICT (de, para) DO UPDATE SET peso = EXCLUDED.peso, atualizado_em = now()`,
        [sinapses.map((s) => s.de), sinapses.map((s) => s.para), sinapses.map((s) => s.peso)],
      );
    },

    // "Sono": decai todos os pesos, poda sinapses fracas e episódios órfãos nunca usados.
    async consolidar({ fator = 0.98, minimo = 0.02, diasEpisodio = 30 } = {}) {
      const client = await pool.connect();
      try {
        await client.query('BEGIN');
        await client.query('UPDATE sinapses SET peso = peso * $1', [fator]);
        const podadas = await client.query('DELETE FROM sinapses WHERE peso < $1', [minimo]);
        const esquecidos = await client.query(
          `DELETE FROM neuronios n
           WHERE n.tipo = 'episodio' AND n.vezes_usado = 0
             AND n.criado_em < now() - make_interval(days => $1)
             AND NOT EXISTS (SELECT 1 FROM sinapses s WHERE s.de = n.id OR s.para = n.id)`,
          [diasEpisodio],
        );
        await client.query('COMMIT');
        return { sinapsesPodadas: podadas.rowCount, episodiosEsquecidos: esquecidos.rowCount };
      } catch (erro) {
        await client.query('ROLLBACK');
        throw erro;
      } finally {
        client.release();
      }
    },

    fechar: () => pool.end(),
  };
}
