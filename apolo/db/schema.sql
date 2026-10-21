-- Apolo: hipocampo (episódios) + memória semântica no mesmo grafo, por enquanto.
-- A dimensão do vetor (256) tem que bater com DIMENSOES em src/embeddings.js.
-- Ao trocar para um embedding real (ex.: 1024), altere os dois e recrie a coluna.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS neuronios (
  id          serial PRIMARY KEY,
  tipo        text NOT NULL CHECK (tipo IN ('conceito', 'episodio', 'habilidade', 'fato')),
  conteudo    text NOT NULL,
  embedding   vector(256) NOT NULL,
  criado_em   timestamptz NOT NULL DEFAULT now(),
  ultimo_uso  timestamptz,
  vezes_usado integer NOT NULL DEFAULT 0
);

-- Sinapses são não-direcionadas e guardadas uma vez só (de < para).
CREATE TABLE IF NOT EXISTS sinapses (
  de            integer NOT NULL REFERENCES neuronios(id) ON DELETE CASCADE,
  para          integer NOT NULL REFERENCES neuronios(id) ON DELETE CASCADE,
  peso          double precision NOT NULL CHECK (peso >= 0 AND peso <= 1),
  tipo          text NOT NULL DEFAULT 'relacionado',
  atualizado_em timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (de, para),
  CHECK (de < para)
);

CREATE INDEX IF NOT EXISTS sinapses_para_idx ON sinapses (para);
CREATE INDEX IF NOT EXISTS neuronios_embedding_idx
  ON neuronios USING hnsw (embedding vector_cosine_ops);
