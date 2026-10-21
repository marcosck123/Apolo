import { readFile } from 'node:fs/promises';
import { criarRepositorio } from '../src/repositorio.js';

const repo = criarRepositorio();
try {
  const sql = await readFile(new URL('../db/schema.sql', import.meta.url), 'utf8');
  await repo.pool.query(sql);
  console.log('Schema aplicado.');
} finally {
  await repo.fechar();
}
