// Executa trechos de JavaScript, um por linha de entrada (JSON), e devolve a saída de console.log como o Node mostraria.
// Uso (feito pelo lib.py): docker run -i node:22-slim node runner.js
const vm = require('node:vm');
const util = require('node:util');
const readline = require('node:readline');

async function rodar(codigo) {
  const saida = [];
  const console = { log: (...a) => saida.push(util.format(...a)), error: (...a) => saida.push(util.format(...a)) };
  let erro = null;
  try {
    const contexto = vm.createContext({ console, setTimeout, Promise });
    const resultado = vm.runInContext(`(async () => {\n${codigo}\n})()`, contexto, { timeout: 2000 });
    await resultado;
    await new Promise((ok) => setTimeout(ok, 20));
  } catch (e) {
    erro = `${e?.name ?? 'Error'}: ${e?.message ?? e}`;
  }
  return { saida: saida.join('\n'), erro };
}

const linhas = readline.createInterface({ input: process.stdin });
let fila = Promise.resolve();
linhas.on('line', (linha) => {
  fila = fila.then(async () => process.stdout.write(JSON.stringify(await rodar(JSON.parse(linha).codigo)) + '\n'));
});
