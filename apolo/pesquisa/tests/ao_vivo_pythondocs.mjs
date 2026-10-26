// Verificação ao vivo: node tests/ao_vivo_pythondocs.mjs (precisa de internet).
import adaptador from '../adaptadores/pythondocs.js';
import { rodar } from './ao_vivo_auxiliar_c.mjs';
await rodar(adaptador, [
  { tema: 'statistics.mean', tipo: 'codigo' },
  { tema: 'list comprehension', tipo: 'codigo' },
  { tema: 'json.loads', tipo: 'codigo' },
  { tema: 'open', tipo: 'codigo' },
]);
