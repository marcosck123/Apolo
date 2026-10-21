// Consolidação noturna — agende no cron das 3h às 5h: `npm run dormir`
import { criarRepositorio } from '../src/repositorio.js';

const repo = criarRepositorio();
try {
  console.log(await repo.consolidar());
} finally {
  await repo.fechar();
}
