r"""
Apolo · Córtex Frontal v0
Um GPT pequeno, escrito do zero, que aprende português lendo texto corrido.

v0 usa tokenização por caractere (simples de entender).
A v1 troca por um tokenizer BPE treinado em português.

Uso:
  python cortex_v0.py treinar --dados textos/ --tamanho mini --passos 3000
  python cortex_v0.py treinar --dados textos/corpus_portugues.txt --val_dados textos/corpus_validacao.txt --tamanho medio
      # --val_dados (opcional): validação vem de um arquivo à parte (sem vazamento do treino); o treino usa 100% de --dados.
      # Sem ele, os últimos 5% de --dados viram validação. A perda é mostrada em nats e em bits por caractere (nats/ln 2).
  python cortex_v0.py gerar --inicio "O menino olhou para" [--parar_em "\n\n"]
  python cortex_v0.py servir --porta 8000        # API HTTP que o Apolo (Node) usa como lobo frontal

API: POST /gerar {inicio, n?, temperatura?, parar_em?}. `parar_em` é uma lista de strings: a geração termina quando o texto
novo contém uma delas e o texto devolvido NÃO inclui a parada nem o que viria depois. Sem o campo vale o padrão do servidor
(["\n\n"]); `parar_em: []` desliga a parada antecipada.

Geração rápida: enquanto o texto cabe no contexto usa cache de chaves/valores (K/V) da atenção, em vez de recalcular tudo a cada
caractere. Passando do contexto, volta a recalcular a janela deslizante dos últimos `contexto` caracteres.
"""
import argparse, glob, json, math, os, time
from http.server import BaseHTTPRequestHandler, HTTPServer
import torch
import torch.nn as nn
import torch.nn.functional as F

TAMANHOS = {
    #            camadas, cabeças, dimensão, contexto
    "mini":     dict(n_camadas=4, n_cabecas=4, d=128, contexto=128),   # ~0,8M parâmetros, roda em CPU
    "pequeno":  dict(n_camadas=6, n_cabecas=6, d=384, contexto=256),   # ~10M, pede GPU
    "intermediario": dict(n_camadas=8, n_cabecas=8, d=512, contexto=256),  # ~25M, GPU (Colab)
    "medio":    dict(n_camadas=12, n_cabecas=12, d=768, contexto=512), # ~85M, GPU alugada
}
PASTA = "cerebro"
PARAR_EM_PADRAO = ["\n\n"]  # o app Node só usa o 1º parágrafo; parar aí poupa a maior parte do tempo


# ---------- tokenização ----------
class TokenizerCaractere:
    def __init__(self, texto=None, vocab=None):
        self.vocab = vocab or sorted(set(texto))
        self.id = {c: i for i, c in enumerate(self.vocab)}

    def codificar(self, s):
        return [self.id[c] for c in s if c in self.id]

    def codificar_tensor(self, s):
        """Igual a `codificar`, mas rápido para textos de centenas de MB (usa numpy em vez de laço em Python)."""
        try:
            import numpy as np
        except ImportError:  # imagem sem numpy: cai no laço (lento só para textos enormes)
            return torch.tensor(self.codificar(s), dtype=torch.long)
        pontos = np.frombuffer(s.encode("utf-32-le"), dtype=np.uint32)
        tabela = np.full(int(pontos.max()) + 1, -1, dtype=np.int64)
        for c, i in self.id.items():
            if ord(c) < len(tabela):
                tabela[ord(c)] = i
        ids = tabela[pontos]
        return torch.from_numpy(ids[ids >= 0])

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

    def forward(self, x, passado=None, devolver_kv=False):
        """`passado`: (k, v) já calculados dos tokens anteriores (cache da geração). Com `devolver_kv`
        devolve (saída, (k, v) atualizados); sem ele devolve só a saída (uso do treino)."""
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)
        q, k, v = (t.view(B, T, self.n_cabecas, C // self.n_cabecas).transpose(1, 2) for t in (q, k, v))
        if passado is not None:
            k = torch.cat([passado[0], k], dim=2)
            v = torch.cat([passado[1], v], dim=2)
        if passado is None:
            y = F.scaled_dot_product_attention(q, k, v, is_causal=True)  # causal: não vê o futuro
        elif T == 1:
            y = F.scaled_dot_product_attention(q, k, v)  # o último token enxerga todo o passado
        else:
            P = k.shape[2] - T
            mascara = torch.ones(T, P + T, dtype=torch.bool, device=x.device).tril(diagonal=P)
            y = F.scaled_dot_product_attention(q, k, v, attn_mask=mascara)
        y = self.saida(y.transpose(1, 2).contiguous().view(B, T, C))
        return (y, (k, v)) if devolver_kv else y


class Bloco(nn.Module):
    """Atenção (comunicação entre tokens) + MLP (pensamento individual de cada token)."""
    def __init__(self, d, n_cabecas):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.atencao = Atencao(d, n_cabecas)
        self.mlp = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))

    def forward(self, x, passado=None, devolver_kv=False):
        if devolver_kv:
            a, kv = self.atencao(self.ln1(x), passado, True)
            x = x + a
            return x + self.mlp(self.ln2(x)), kv
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

    def forward_cache(self, ids, passado=None):
        """Como `forward`, mas para geração: `ids` são só os tokens novos e `passado` é a lista de (k, v) por camada.
        Devolve (logits, novo_passado). As posições continuam de onde o passado parou (embedding de posição absoluta)."""
        P = 0 if passado is None else passado[0][0].shape[2]
        T = ids.shape[1]
        x = self.tok(ids) + self.pos(torch.arange(P, P + T, device=ids.device))
        novo = []
        for i, b in enumerate(self.blocos):
            x, kv = b(x, None if passado is None else passado[i], True)
            novo.append(kv)
        return self.cabeca(self.ln(x)), novo

    @torch.no_grad()
    def gerar(self, ids, n, temperatura=0.8, top_k=40, parar=None, usar_cache=True):
        """Gera até `n` tokens. `parar(token_id) -> bool` (opcional) é chamado a cada token novo; se devolver True a
        geração termina (o token que disparou a parada fica em `ids`). Com `usar_cache` o K/V é reaproveitado enquanto
        o texto inteiro cabe no contexto; depois disso recalcula a janela dos últimos `contexto` tokens."""
        passado = None
        for _ in range(n):
            if usar_cache and ids.shape[1] <= self.contexto:
                if passado is None:
                    logits, passado = self.forward_cache(ids)
                else:
                    logits, passado = self.forward_cache(ids[:, -1:], passado)
            else:
                passado = None
                logits, _ = self(ids[:, -self.contexto:])
            logits = logits[:, -1, :] / temperatura
            v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
            logits[logits < v[:, [-1]]] = -float("inf")
            novo = torch.multinomial(F.softmax(logits, -1), 1)
            ids = torch.cat([ids, novo], dim=1)
            if parar is not None and parar(novo[0, 0].item()):
                break
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
    texto_val = ler_textos(a.val_dados) if a.val_dados else None
    # vocabulário com treino + validação juntos, para não perder caracteres que só aparecem em um dos lados
    tk = TokenizerCaractere(texto + texto_val if texto_val else texto)
    dados = tk.codificar_tensor(texto)
    del texto
    if texto_val is not None:
        treino, validacao = dados, tk.codificar_tensor(texto_val)  # caracteres desconhecidos já são descartados
        del texto_val
    else:
        corte = int(0.95 * len(dados))
        treino, validacao = dados[:corte], dados[corte:]

    cfg = dict(TAMANHOS[a.tamanho], vocab=len(tk.vocab))
    if a.val_dados and len(validacao) <= cfg["contexto"] + 1:
        raise SystemExit(f"Validação curta demais ({len(validacao):,} caracteres): precisa de mais que {cfg['contexto'] + 1} (o contexto).")
    if not a.val_dados and len(validacao) <= cfg["contexto"] + 1:
        minimo = int((cfg["contexto"] + 2) / 0.05)
        raise SystemExit(f"Texto curto demais ({len(dados):,} caracteres): a validação (5%) não cabe em um contexto. Use pelo menos ~{minimo:,}.")
    modelo = Cortex(**cfg).to(dev)
    n_params = sum(p.numel() for p in modelo.parameters())
    origem_val = " (arquivo à parte)" if a.val_dados else " (últimos 5%)"
    print(f"dispositivo: {dev} | treino: {len(treino):,} | validação: {len(validacao):,}{origem_val} | vocab: {len(tk.vocab)} | parâmetros: {n_params/1e6:.2f}M")
    print(f"passos: {a.passos}")
    print(f"referência Chinchilla: ~{20*n_params/1e6:.0f}M tokens seriam o ideal para este tamanho")

    opt = torch.optim.AdamW(modelo.parameters(), lr=a.lr, weight_decay=0.1)
    C = cfg["contexto"]
    # Precisão mista na GPU: bem mais rápido e usa menos memória.
    usar_amp = dev == "cuda"
    escala = torch.amp.GradScaler("cuda", enabled=usar_amp)
    if a.retomar and os.path.exists(f"{PASTA}/cortex.pt"):
        modelo.load_state_dict(torch.load(f"{PASTA}/cortex.pt", map_location=dev))
        print(f"retomando os pesos de {PASTA}/cortex.pt (o agendamento da taxa de aprendizado recomeça)")

    def salvar():
        torch.save(modelo.state_dict(), f"{PASTA}/cortex.pt")
        json.dump({"cfg": cfg, "vocab": tk.vocab}, open(f"{PASTA}/config.json", "w", encoding="utf-8"), ensure_ascii=False)

    def lote(fonte):
        i = torch.randint(len(fonte) - C - 1, (a.lote,))
        x = torch.stack([fonte[j:j + C] for j in i])
        y = torch.stack([fonte[j + 1:j + C + 1] for j in i])
        return x.to(dev), y.to(dev)

    @torch.no_grad()
    def avaliar():
        modelo.eval()
        with torch.autocast(dev, dtype=torch.float16, enabled=usar_amp):
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
            print(f"passo {passo:>6} | perda treino {p['treino']:.3f} ({p['treino']/math.log(2):.3f} bits/car) | "
                  f"perda val {p['val']:.3f} ({p['val']/math.log(2):.3f} bits/car) | {time.time()-inicio:.0f}s")
        x, y = lote(treino)
        with torch.autocast(dev, dtype=torch.float16, enabled=usar_amp):
            _, perda = modelo(x, y)
        opt.zero_grad(set_to_none=True)
        escala.scale(perda).backward()
        escala.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(modelo.parameters(), 1.0)
        escala.step(opt)
        escala.update()
        if a.salvar_cada and passo > 0 and passo % a.salvar_cada == 0 and passo < a.passos:
            salvar()
            print(f"checkpoint salvo em {PASTA}/ (passo {passo})", flush=True)

    salvar()
    print(f"salvo em {PASTA}/")
    amostra(modelo, tk, dev, "\n", 300)


def amostra(modelo, tk, dev, inicio, n):
    ids = torch.tensor([tk.codificar(inicio) or [0]], device=dev)
    print("\n--- o córtex escreve ---\n" + tk.decodificar(modelo.gerar(ids, n)[0].tolist()))


def carregar():
    dev = dispositivo()
    meta = json.load(open(f"{PASTA}/config.json", encoding="utf-8"))
    tk = TokenizerCaractere(vocab=meta["vocab"])
    modelo = Cortex(**meta["cfg"]).to(dev)
    modelo.load_state_dict(torch.load(f"{PASTA}/cortex.pt", map_location=dev))
    modelo.eval()
    return modelo, tk, dev


def gerar(a):
    modelo, tk, dev = carregar()
    if a.parar_em:
        print(a.inicio + continuar(modelo, tk, dev, a.inicio, a.n, parar_em=a.parar_em))
    else:
        amostra(modelo, tk, dev, a.inicio, a.n)


def continuar(modelo, tk, dev, inicio, n, temperatura=0.8, parar_em=None, usar_cache=True):
    """Devolve só o que o córtex escreveu depois de `inicio` (o modelo só enxerga os últimos `contexto` caracteres).
    `parar_em`: lista de strings; ao aparecer uma delas no texto novo a geração termina e o texto devolvido é cortado
    antes dela (a parada e o que viria depois não entram). Vazio/None = sem parada antecipada."""
    ids = torch.tensor([tk.codificar(inicio) or [0]], device=dev)
    paradas = [p for p in (parar_em or []) if p]
    parar = None
    if paradas:
        vistos = []

        def parar(i):
            vistos.append(tk.vocab[i])
            texto = "".join(vistos)
            return any(texto.endswith(p) for p in paradas)
    novos = modelo.gerar(ids, n, temperatura=temperatura, parar=parar, usar_cache=usar_cache)[0, ids.shape[1]:]
    texto = tk.decodificar(novos.tolist())
    cortes = [texto.find(p) for p in paradas if p in texto]
    return texto[:min(cortes)] if cortes else texto


def servir(a):
    modelo, tk, dev = carregar()

    class Manipulador(BaseHTTPRequestHandler):
        def _responder(self, status, corpo):
            dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(dados)))
            self.end_headers()
            self.wfile.write(dados)

        def do_GET(self):
            self._responder(200, {"ok": True}) if self.path == "/saude" else self._responder(404, {"erro": "não encontrado"})

        def do_POST(self):
            if self.path != "/gerar":
                return self._responder(404, {"erro": "não encontrado"})
            try:
                req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                inicio = req["inicio"]
                n = max(1, min(int(req.get("n", 200)), 1000))
                temperatura = float(req.get("temperatura", 0.8))
                parar_em = req.get("parar_em", PARAR_EM_PADRAO)  # [] desliga; ausente = padrão do servidor
                if parar_em is None:
                    parar_em = PARAR_EM_PADRAO
                if not isinstance(inicio, str) or temperatura <= 0:
                    raise ValueError
                if not isinstance(parar_em, list) or not all(isinstance(p, str) for p in parar_em):
                    raise ValueError
            except (KeyError, ValueError, TypeError):
                return self._responder(400, {"erro": "corpo esperado: {inicio: str, n?: int, temperatura?: float > 0, parar_em?: [str]}"})
            self._responder(200, {"texto": continuar(modelo, tk, dev, inicio, n, temperatura, parar_em)})

    print(f"córtex ouvindo em http://0.0.0.0:{a.porta} ({dev})", flush=True)
    HTTPServer(("0.0.0.0", a.porta), Manipulador).serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("treinar")
    t.add_argument("--dados", required=True, help="arquivo .txt ou pasta com .txt")
    t.add_argument("--val_dados", default=None, help="arquivo .txt (ou pasta) só de validação, ex.: textos/corpus_validacao.txt; "
                   "se dado, o treino usa 100%% de --dados; sem ele, os últimos 5%% de --dados viram validação")
    t.add_argument("--tamanho", default="mini", choices=TAMANHOS)
    t.add_argument("--passos", type=int, default=3000)
    t.add_argument("--lote", type=int, default=32)
    t.add_argument("--lr", type=float, default=1e-3)
    t.add_argument("--avaliar_cada", type=int, default=250)
    t.add_argument("--salvar_cada", type=int, default=0, help="salva um checkpoint a cada N passos (0 = só no fim)")
    t.add_argument("--retomar", action="store_true", help="continua a partir dos pesos já salvos em --pasta")
    t.add_argument("--pasta", default=None, help="onde salvar cortex.pt e config.json (ex.: uma pasta do Google Drive)")
    g = sub.add_parser("gerar")
    g.add_argument("--inicio", default="O ")
    g.add_argument("--n", type=int, default=400)
    g.add_argument("--parar_em", nargs="*", default=[], help="strings que encerram a geração (o texto é cortado antes delas)")
    sv = sub.add_parser("servir")
    sv.add_argument("--porta", type=int, default=8000)
    a = ap.parse_args()
    if getattr(a, "pasta", None):
        PASTA = a.pasta
    {"treinar": treinar, "gerar": gerar, "servir": servir}[a.cmd](a)
