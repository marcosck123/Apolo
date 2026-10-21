// Grafo em memória: neurônios + sinapses não-direcionadas (uma por par, de < para).
// Não sabe nada de banco, embeddings ou LLM — só as "leis da física" do sistema.

const chave = (a, b) => (a < b ? `${a}:${b}` : `${b}:${a}`);

export class Cerebro {
  constructor() {
    this.neuronios = new Map();
    this.sinapses = new Map();
    this.adjacencia = new Map();
  }

  adicionarNeuronio(neuronio) {
    this.neuronios.set(neuronio.id, neuronio);
    if (!this.adjacencia.has(neuronio.id)) this.adjacencia.set(neuronio.id, new Set());
    return neuronio;
  }

  sinapse(a, b) {
    return this.sinapses.get(chave(a, b));
  }

  definirSinapse(a, b, peso, tipo = 'relacionado') {
    if (a === b) return null;
    const [de, para] = a < b ? [a, b] : [b, a];
    const sinapse = { de, para, peso, tipo };
    this.sinapses.set(chave(a, b), sinapse);
    for (const [x, y] of [[de, para], [para, de]]) {
      if (!this.adjacencia.has(x)) this.adjacencia.set(x, new Set());
      this.adjacencia.get(x).add(y);
    }
    return sinapse;
  }

  removerSinapse(a, b) {
    if (!this.sinapses.delete(chave(a, b))) return false;
    this.adjacencia.get(a)?.delete(b);
    this.adjacencia.get(b)?.delete(a);
    return true;
  }

  *vizinhos(id) {
    for (const vizinho of this.adjacencia.get(id) ?? []) {
      yield { id: vizinho, peso: this.sinapse(id, vizinho).peso };
    }
  }
}

// Ativação em cascata. `sementes` = [{ id, forca }] (forca em 0..1, ex.: similaridade).
// A energia entregue em cada salto é proporcional ao peso da sinapse e decai a cada salto;
// só a energia nova segue adiante, então ciclos no grafo morrem sozinhos.
// A ativação é efêmera (por pensamento): começa do zero a cada chamada.
export function propagar(cerebro, sementes, { passos = 3, decaimento = 0.5, limiar = 0.05, topN = 15 } = {}) {
  const ativacao = new Map();
  let fronteira = new Map();
  for (const { id, forca = 1 } of sementes) {
    if (!cerebro.neuronios.has(id)) continue;
    ativacao.set(id, Math.min(1, forca));
    fronteira.set(id, Math.min(1, forca));
  }

  for (let passo = 0; passo < passos; passo++) {
    const proxima = new Map();
    for (const [id, energia] of fronteira) {
      if (energia < limiar) continue;
      for (const vizinho of cerebro.vizinhos(id)) {
        const entregue = energia * vizinho.peso * decaimento;
        if (entregue < limiar) continue;
        proxima.set(vizinho.id, (proxima.get(vizinho.id) ?? 0) + entregue);
      }
    }
    for (const [id, energia] of proxima) {
      ativacao.set(id, Math.min(1, (ativacao.get(id) ?? 0) + energia));
    }
    fronteira = proxima;
  }

  return [...ativacao]
    .map(([id, valor]) => ({ id, ativacao: valor }))
    .sort((a, b) => b.ativacao - a.ativacao)
    .slice(0, topN);
}

// Hebb: quem acende junto se conecta mais forte. O ganho é multiplicado por (1 - peso),
// então o peso satura suavemente em 1. Retorna as sinapses tocadas, para persistir.
export function hebb(cerebro, ativos, taxa = 0.1) {
  const alteradas = [];
  for (let i = 0; i < ativos.length; i++) {
    for (let j = i + 1; j < ativos.length; j++) {
      const a = ativos[i];
      const b = ativos[j];
      const sinapse = cerebro.sinapse(a.id, b.id) ?? cerebro.definirSinapse(a.id, b.id, 0);
      if (!sinapse) continue;
      sinapse.peso += taxa * a.ativacao * b.ativacao * (1 - sinapse.peso);
      alteradas.push(sinapse);
    }
  }
  return alteradas;
}

// Esquecimento: todo peso decai por `fator`; o que cai abaixo de `minimo` é podado.
// Retorna quantas sinapses foram podadas.
export function esquecer(cerebro, { fator = 0.98, minimo = 0.02 } = {}) {
  let podadas = 0;
  for (const sinapse of [...cerebro.sinapses.values()]) {
    sinapse.peso *= fator;
    if (sinapse.peso < minimo) {
      cerebro.removerSinapse(sinapse.de, sinapse.para);
      podadas++;
    }
  }
  return podadas;
}
