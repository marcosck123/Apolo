// Verificação ao vivo: node tests/ao_vivo_brasilescola.mjs (precisa de internet).
import adaptador from '../adaptadores/brasilescola.js';
import { rodar } from './ao_vivo_auxiliar_c.mjs';
await rodar(adaptador, [
  { url: 'https://brasilescola.uol.com.br/brasil/rondonia.htm', tema: 'rondônia', tipo: 'lugar' },
  { tema: 'Rondônia', tipo: 'lugar' },
]);
