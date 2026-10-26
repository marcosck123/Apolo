// Verificação ao vivo: node tests/ao_vivo_mundoeducacao.mjs (precisa de internet).
import adaptador from '../adaptadores/mundoeducacao.js';
import { rodar } from './ao_vivo_auxiliar_c.mjs';
await rodar(adaptador, [
  { url: 'https://mundoeducacao.uol.com.br/matematica/media-aritmetica.htm', tema: 'média aritmética', tipo: 'definicao' },
  { tema: 'média aritmética', tipo: 'definicao' },
]);
