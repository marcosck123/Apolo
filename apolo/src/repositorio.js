// Persistência em PostgreSQL + pgvector. Não carrega o grafo inteiro: busca sementes por
// similaridade e puxa só a vizinhança delas, que vira um Cerebro em memória para a cascata.
import pg from 'pg';
import { Cerebro } from './nucleo/cerebro.js';

const comoVetor = (embedding) => `[${embedding.join(',')}]`;

// Confiança efetiva: o que o neurônio guarda, ou o padrão da origem (1,0 ensinado à mão, 0,5 para o resto).
const CONFIANCA = "COALESCE(confianca, CASE WHEN origem = 'usuario' THEN 1.0 ELSE 0.5 END)::float8";
const COLUNAS = `id, tipo, conteudo, origem, vezes_usado, ultimo_uso, criado_em, ${CONFIANCA} AS confianca, fontes, confirmacoes`;

export function criarRepositorio(connectionString = process.env.DATABASE_URL) {
  const pool = new pg.Pool({ connectionString });

  return {
    pool,

    async criarNeuronio({ tipo, conteudo, embedding, origem = 'usuario', confianca = null, fontes = 1 }) {
      const { rows } = await pool.query(
        `INSERT INTO neuronios (tipo, conteudo, embedding, origem, confianca, fontes)
         VALUES ($1, $2, $3::vector, $4, $5, $6)
         RETURNING ${COLUNAS}`,
        [tipo, conteudo, comoVetor(embedding), origem, confianca, fontes],
      );
      return rows[0];
    },

    async buscarNeuronio(id) {
      const { rows } = await pool.query(
        `SELECT ${COLUNAS} FROM neuronios WHERE id = $1`,
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
        `SELECT ${COLUNAS} FROM neuronios WHERE id = ANY($1)`,
        [[...vistos]],
      );
      for (const n of rows) cerebro.adicionarNeuronio(n);
      return cerebro;
    },

    // Visão geral para o painel: os neurônios mais usados/recentes e as sinapses entre eles.
    // O embedding nunca sai do banco.
    async carregarGrafo({ limite = 300 } = {}) {
      const { rows: neuronios } = await pool.query(
        `SELECT ${COLUNAS} FROM neuronios
         ORDER BY vezes_usado DESC, criado_em DESC LIMIT $1`,
        [limite],
      );
      const ids = neuronios.map((n) => n.id);
      const { rows: sinapses } = await pool.query(
        'SELECT de, para, peso, tipo FROM sinapses WHERE de = ANY($1) AND para = ANY($1)',
        [ids],
      );
      return { neuronios, sinapses };
    },

    // ---- intenções (grupos de frases) ----
    async carregarIntencoes() {
      const [{ rows: grupos }, { rows: frases }, { rows: respostas }] = await Promise.all([
        pool.query('SELECT nome FROM intencoes ORDER BY nome'),
        pool.query('SELECT frase, intencao FROM intencao_frases ORDER BY frase'),
        pool.query('SELECT intencao, resposta, quando FROM intencao_respostas ORDER BY id'),
      ]);
      return grupos.map((g) => ({
        nome: g.nome,
        frases: frases.filter((f) => f.intencao === g.nome).map((f) => f.frase),
        respostas: respostas.filter((r) => r.intencao === g.nome).map((r) => ({ texto: r.resposta, quando: r.quando ?? undefined })),
      }));
    },

    async garantirIntencao(nome) {
      await pool.query('INSERT INTO intencoes (nome) VALUES ($1) ON CONFLICT DO NOTHING', [nome]);
    },

    // Uma frase pertence a um grupo só: se já existir em outro, muda de grupo.
    async ensinarFrase(intencao, frase) {
      await this.garantirIntencao(intencao);
      await pool.query(
        'INSERT INTO intencao_frases (frase, intencao) VALUES ($1, $2) ON CONFLICT (frase) DO UPDATE SET intencao = EXCLUDED.intencao',
        [frase, intencao],
      );
    },

    async ensinarResposta(intencao, resposta, quando = null) {
      await this.garantirIntencao(intencao);
      await pool.query(
        'INSERT INTO intencao_respostas (intencao, resposta, quando) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING',
        [intencao, resposta, quando],
      );
    },

    async marcarUso(ids) {
      if (ids.length === 0) return;
      await pool.query(
        'UPDATE neuronios SET vezes_usado = vezes_usado + 1, ultimo_uso = now() WHERE id = ANY($1)',
        [ids],
      );
    },

    // Aprovação (+) ou correção (−) do usuário. Um UPDATE só, para não perder ajustes simultâneos.
    // O que foi ensinado à mão não perde confiança por aqui: só se apaga ou se ensina de novo.
    async ajustarConfianca(id, delta) {
      const { rows } = await pool.query(
        `UPDATE neuronios
            SET confianca = LEAST(1, GREATEST(0, ${CONFIANCA} + $2::float8)),
                confirmacoes = confirmacoes + CASE WHEN $2::float8 > 0 THEN 1 ELSE 0 END
          WHERE id = $1 AND (origem <> 'usuario' OR $2::float8 > 0)
          RETURNING ${COLUNAS}`,
        [id, delta],
      );
      return rows[0] ?? null;
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

    async enfileirarEstudo(neuronioId) {
      await pool.query('INSERT INTO estudos (neuronio_id) VALUES ($1) ON CONFLICT DO NOTHING', [neuronioId]);
    },

    async pegarEstudoPendente() {
      await pool.query(`UPDATE estudos SET estado = 'falhou', atualizado_em = now(),
        resultado = '{"motivo":"concessão interrompida na última tentativa"}'::jsonb
        WHERE estado = 'estudando' AND tentativas >= 3 AND atualizado_em < now() - interval '10 minutes'`);
      const { rows } = await pool.query(`UPDATE estudos SET estado = 'estudando',
        tentativas = tentativas + 1, atualizado_em = now()
        WHERE id = (SELECT id FROM estudos WHERE tentativas < 3 AND
          (estado = 'pendente' OR (estado = 'estudando' AND atualizado_em < now() - interval '10 minutes'))
          ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 1) RETURNING *`);
      return rows[0] ?? null;
    },

    async marcarEstudo(id, estado, resultado) {
      await pool.query('UPDATE estudos SET estado = $2, resultado = $3, atualizado_em = now() WHERE id = $1',
        [id, estado, JSON.stringify(resultado)]);
    },

    // Fatos e habilidades que contêm as palavras (sem acento nem caixa), os que contêm mais palavras primeiro.
    // A cascata do grafo só traz o que está ativo, e episódios de conversas antigas ocupam as vagas;
    // esta busca direta garante que um fato que responde à pergunta chegue à comparação.
    async buscarFatosPorPalavras(palavras, { limite = 40 } = {}) {
      const unicas = [...new Set(palavras.filter((p) => /^[a-z0-9]{3,}$/.test(p)))].slice(0, 8);
      if (!unicas.length) return [];
      const plano = "translate(lower(conteudo), 'áàâãäéèêëíìîïóòôõöúùûüçñ', 'aaaaaeeeeiiiiooooouuuucn')";
      const casa = unicas.map((_, i) => `(${plano} LIKE $${i + 1})`);
      const { rows } = await pool.query(
        `SELECT ${COLUNAS} FROM neuronios
         WHERE tipo IN ('fato', 'habilidade') AND (${casa.join(' OR ')})
         ORDER BY (${casa.map((c) => `CASE WHEN ${c} THEN 1 ELSE 0 END`).join(' + ')}) DESC, id DESC
         LIMIT ${Number(limite)}`,
        unicas.map((p) => `%${p}%`),
      );
      return rows;
    },

    async buscarConteudo(conteudo) {
      const { rows } = await pool.query('SELECT id, tipo, conteudo FROM neuronios WHERE conteudo = $1 ORDER BY id LIMIT 1', [conteudo]);
      return rows[0] ?? null;
    },

    // Quais destes ids ainda existem (pode ter havido um "esqueça" no meio de um pensamento).
    async existentes(ids) {
      if (!ids?.length) return new Set();
      const { rows } = await pool.query('SELECT id FROM neuronios WHERE id = ANY($1)', [ids]);
      return new Set(rows.map((r) => r.id));
    },

    // Esquecer: só apaga neurônios de origem `web`. O que foi ensinado à mão nunca é tocado. Devolve quantos apagou.
    async apagarNeuronios(ids) {
      if (!ids?.length) return 0;
      const { rowCount } = await pool.query("DELETE FROM neuronios WHERE id = ANY($1) AND origem = 'web'", [ids]);
      return rowCount;
    },

    async apagarWebPorTema(tema) {
      const plano = "translate(lower(conteudo), 'áàâãäéèêëíìîïóòôõöúùûüçñ', 'aaaaaeeeeiiiiooooouuuucn')";
      const { rowCount } = await pool.query(`DELETE FROM neuronios WHERE origem = 'web' AND ${plano} LIKE $1`, [`%${tema.toLowerCase().replace(/[\\%_]/g, '\\$&')}%`]);
      return rowCount;
    },

    fechar: () => pool.end(),
  };
}
