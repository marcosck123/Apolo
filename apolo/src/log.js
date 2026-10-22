// Diário do Apolo em memória: guarda os últimos eventos e avisa quem estiver ouvindo (o painel).
export function criarLog({ max = 500 } = {}) {
  const eventos = [];
  const ouvintes = new Set();
  let proximoId = 1;

  return {
    registrar(tipo, dados = {}) {
      const evento = { id: proximoId++, em: new Date().toISOString(), tipo, ...dados };
      eventos.push(evento);
      if (eventos.length > max) eventos.shift();
      for (const ouvir of ouvintes) ouvir(evento);
      return evento;
    },

    recentes: (limite = max) => eventos.slice(-limite),

    // Devolve a função que cancela a assinatura.
    assinar(ouvir) {
      ouvintes.add(ouvir);
      return () => ouvintes.delete(ouvir);
    },
  };
}
