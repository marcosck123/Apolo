"""
Apolo · Córtex Frontal v0
Um GPT pequeno, escrito do zero, que aprende português lendo texto corrido.

v0 usa tokenização por caractere (simples de entender).
A v1 troca por um tokenizer BPE treinado em português.

Uso:
  python cortex_v0.py treinar --dados textos/ --tamanho mini --passos 3000
  python cortex_v0.py gerar --inicio "O menino olhou para"
"""
import argparse, glob, json, math, os, time
import torch
import torch.nn as nn
import torch.nn.functional as F

TAMANHOS = {
    #            camadas, cabeças, dimensão, contexto
    "mini":     dict(n_camadas=4, n_cabecas=4, d=128, contexto=128),   # ~0,8M parâmetros, roda em CPU
    "pequeno":  dict(n_camadas=6, n_cabecas=6, d=384, contexto=256),   # ~10M, pede GPU
    "medio":    dict(n_camadas=12, n_cabecas=12, d=768, contexto=512), # ~85M, GPU alugada
}
PASTA = "cerebro"


# ---------- tokenização ----------
class TokenizerCaractere:
    def __init__(self, texto=None, vocab=None):
        self.vocab = vocab or sorted(set(texto))
        self.id = {c: i for i, c in enumerate(self.vocab)}

    def codificar(self, s):
        return [self.id[c] for c in s if c in self.id]

    def decodificar(self, ids):
        return "".join(self.vocab[i] for i in ids)


# ---------- o modelo ----------
class Atencao(nn.Module):
    """Cada token olha para os anteriores e decide em quais prestar atenção."""
    def __init__(self, d, n_cabecas):
        super().__init__()
        self.n_cabecas = n_cabecas
        self.qkv = nn.Linear(d, 3 * d)
        self.saida = nn.Linear(d, d)

    def forward(self, x):
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)
        q, k, v = (t.view(B, T, self.n_cabecas, C // self.n_cabecas).transpose(1, 2) for t in (q, k, v))
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True)  # causal: não vê o futuro
        return self.saida(y.transpose(1, 2).contiguous().view(B, T, C))


class Bloco(nn.Module):
    """Atenção (comunicação entre tokens) + MLP (pensamento individual de cada token)."""
    def __init__(self, d, n_cabecas):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.atencao = Atencao(d, n_cabecas)
        self.mlp = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))

    def forward(self, x):
        x = x + self.atencao(self.ln1(x))
        return x + self.mlp(self.ln2(x))


class Cortex(nn.Module):
    def __init__(self, vocab, n_camadas, n_cabecas, d, contexto):
        super().__init__()
        self.contexto = contexto
        self.tok = nn.Embedding(vocab, d)       # cada token vira um vetor
        self.pos = nn.Embedding(contexto, d)    # posição na frase
        self.blocos = nn.ModuleList(Bloco(d, n_cabecas) for _ in range(n_camadas))
        self.ln = nn.LayerNorm(d)
        self.cabeca = nn.Linear(d, vocab, bias=False)
        self.cabeca.weight = self.tok.weight    # compartilha pesos (economiza parâmetros)
        self.apply(self._iniciar)
        # camadas que escrevem de volta no fluxo residual começam menores, para os blocos não somarem ruído demais
        for nome, p in self.named_parameters():
            if nome.endswith(("atencao.saida.weight", "mlp.2.weight")):
                nn.init.normal_(p, mean=0.0, std=0.02 / math.sqrt(2 * n_camadas))

    @staticmethod
    def _iniciar(m):
        # sem isto o embedding nasce com desvio 1 e, como a saída compartilha o peso, a perda inicial
        # fica enorme (~83) em vez de ~ln(vocab). Com 0.02 ela começa perto do chute aleatório.
        if isinstance(m, (nn.Linear, nn.Embedding)):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)
            if getattr(m, "bias", None) is not None:
                nn.init.zeros_(m.bias)

    def forward(self, ids, alvo=None):
        T = ids.shape[1]
        x = self.tok(ids) + self.pos(torch.arange(T, device=ids.device))
        for b in self.blocos:
            x = b(x)
        logits = self.cabeca(self.ln(x))
        perda = None if alvo is None else F.cross_entropy(logits.view(-1, logits.size(-1)), alvo.view(-1))
        return logits, perda

    @torch.no_grad()
    def gerar(self, ids, n, temperatura=0.8, top_k=40):
        for _ in range(n):
            logits, _ = self(ids[:, -self.contexto:])
            logits = logits[:, -1, :] / temperatura
            v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
            logits[logits < v[:, [-1]]] = -float("inf")
            ids = torch.cat([ids, torch.multinomial(F.softmax(logits, -1), 1)], dim=1)
        return ids


# ---------- treino ----------
def dispositivo():
    if torch.cuda.is_available(): return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available(): return "mps"
    return "cpu"


def ler_textos(caminho):
    arquivos = [caminho] if os.path.isfile(caminho) else sorted(glob.glob(os.path.join(caminho, "**/*.txt"), recursive=True))
    if not arquivos:
        raise SystemExit(f"Nenhum .txt encontrado em {caminho}")
    return "\n\n".join(open(a, encoding="utf-8", errors="ignore").read() for a in arquivos)


def treinar(a):
    dev = dispositivo()
    texto = ler_textos(a.dados)
    tk = TokenizerCaractere(texto)
    dados = torch.tensor(tk.codificar(texto), dtype=torch.long)
    corte = int(0.95 * len(dados))
    treino, validacao = dados[:corte], dados[corte:]

    cfg = dict(TAMANHOS[a.tamanho], vocab=len(tk.vocab))
    if len(validacao) <= cfg["contexto"] + 1:
        minimo = int((cfg["contexto"] + 2) / 0.05)
        raise SystemExit(f"Texto curto demais ({len(dados):,} caracteres): a validação (5%) não cabe em um contexto. Use pelo menos ~{minimo:,}.")
    modelo = Cortex(**cfg).to(dev)
    n_params = sum(p.numel() for p in modelo.parameters())
    print(f"dispositivo: {dev} | texto: {len(dados):,} caracteres | vocab: {len(tk.vocab)} | parâmetros: {n_params/1e6:.2f}M")
    print(f"referência Chinchilla: ~{20*n_params/1e6:.0f}M tokens seriam o ideal para este tamanho")

    opt = torch.optim.AdamW(modelo.parameters(), lr=a.lr, weight_decay=0.1)
    C = cfg["contexto"]

    def lote(fonte):
        i = torch.randint(len(fonte) - C - 1, (a.lote,))
        x = torch.stack([fonte[j:j + C] for j in i])
        y = torch.stack([fonte[j + 1:j + C + 1] for j in i])
        return x.to(dev), y.to(dev)

    @torch.no_grad()
    def avaliar():
        modelo.eval()
        perdas = {k: sum(modelo(*lote(f))[1].item() for _ in range(20)) / 20 for k, f in (("treino", treino), ("val", validacao))}
        modelo.train()
        return perdas

    os.makedirs(PASTA, exist_ok=True)
    inicio = time.time()
    aquecimento = max(1, min(200, a.passos // 10))
    for passo in range(a.passos + 1):
        lr = a.lr * min(1, passo / aquecimento) * 0.5 * (1 + math.cos(math.pi * passo / a.passos))  # aquece e depois desce
        for g in opt.param_groups: g["lr"] = max(lr, a.lr * 0.05)
        if passo % a.avaliar_cada == 0:
            p = avaliar()
            print(f"passo {passo:>6} | perda treino {p['treino']:.3f} | perda val {p['val']:.3f} | {time.time()-inicio:.0f}s")
        x, y = lote(treino)
        _, perda = modelo(x, y)
        opt.zero_grad(set_to_none=True)
        perda.backward()
        torch.nn.utils.clip_grad_norm_(modelo.parameters(), 1.0)
        opt.step()

    torch.save(modelo.state_dict(), f"{PASTA}/cortex.pt")
    json.dump({"cfg": cfg, "vocab": tk.vocab}, open(f"{PASTA}/config.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(f"salvo em {PASTA}/")
    amostra(modelo, tk, dev, "\n", 300)


def amostra(modelo, tk, dev, inicio, n):
    ids = torch.tensor([tk.codificar(inicio) or [0]], device=dev)
    print("\n--- o córtex escreve ---\n" + tk.decodificar(modelo.gerar(ids, n)[0].tolist()))


def gerar(a):
    dev = dispositivo()
    meta = json.load(open(f"{PASTA}/config.json", encoding="utf-8"))
    tk = TokenizerCaractere(vocab=meta["vocab"])
    modelo = Cortex(**meta["cfg"]).to(dev)
    modelo.load_state_dict(torch.load(f"{PASTA}/cortex.pt", map_location=dev))
    modelo.eval()
    amostra(modelo, tk, dev, a.inicio, a.n)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("treinar")
    t.add_argument("--dados", required=True, help="arquivo .txt ou pasta com .txt")
    t.add_argument("--tamanho", default="mini", choices=TAMANHOS)
    t.add_argument("--passos", type=int, default=3000)
    t.add_argument("--lote", type=int, default=32)
    t.add_argument("--lr", type=float, default=1e-3)
    t.add_argument("--avaliar_cada", type=int, default=250)
    g = sub.add_parser("gerar")
    g.add_argument("--inicio", default="O ")
    g.add_argument("--n", type=int, default=400)
    a = ap.parse_args()
    treinar(a) if a.cmd == "treinar" else gerar(a)
