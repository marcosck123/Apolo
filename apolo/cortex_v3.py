"""
Apolo · Córtex Frontal v3
Um GPT pequeno, escrito do zero, no estilo "moderno" (Llama/SmolLM): RMSNorm, RoPE, SwiGLU,
tokenizador BPE (ou caractere), agenda de aprendizado WSD e retomada EXATA do treino.
Arquivo autocontido: não importa o cortex_v0.py (só o tokenizador_bpe.py, que vai junto).

O que mudou em relação ao v0, e por quê:
  * RMSNorm no lugar de LayerNorm: só divide pela "altura" (raiz da média dos quadrados) do vetor;
    não subtrai média nem tem viés. Mais barato e rende igual.
  * RoPE no lugar da posição absoluta aprendida: em vez de somar um vetor de "posição 17" ao token,
    giramos q e k em um ângulo proporcional à posição. O produto q·k passa a depender só da DISTÂNCIA
    entre os tokens. Consequência boa: a janela deslizante na geração é natural (descartar o cache
    mais antigo não bagunça nada) e não há tabela de posições para treinar.
  * SwiGLU no MLP: saída = baixo( silu(porta(x)) * sobe(x) ). Um "portão" decide o que passa.
    Largura oculta ≈ 8/3·d (arredondada para múltiplo de 64) para gastar os mesmos parâmetros do MLP 4d clássico.
  * Sem viés em nenhuma camada linear (padrão atual; simplifica o weight decay).
  * KV cache na geração: cada passo calcula só o token novo, reaproveitando k e v dos anteriores.
  * Parada antecipada (`parar_em`): a geração termina ao produzir, por exemplo, "\\n\\n".
  * Agenda WSD (Warmup-Stable-Decay): aquece, mantém a taxa constante (platô) e desce só no fim.
    Como o platô não depende do total de passos, dá para CONTINUAR treinando de um checkpoint do platô.
  * Retomada exata: o checkpoint guarda modelo, otimizador, GradScaler, passo, RNGs, config e tokenizador.
  * Métrica em BITS POR CARACTERE (BPC): a perda por token não é comparável entre tokenizadores
    (um token BPE vale ~3,5 caracteres). BPC = perda_nats_por_token × tokens / (ln2 × caracteres).

Uso:
  python cortex_v3.py tamanhos
  python cortex_v3.py treinar --dados textos/corpus_portugues.txt --val_dados textos/corpus_validacao.txt \\
         --tamanho medio --tokenizador bpe --tokenizador_json cerebro_v3/tokenizador.json --passos 6000 --pasta cerebro_v3_medio
  python cortex_v3.py avaliar --val_dados textos/corpus_validacao.txt --pasta cerebro_v3_medio
  python cortex_v3.py gerar --pasta cerebro_v3_medio --inicio "Como criar uma lista em Python?\\n"
  python cortex_v3.py servir --porta 8000 --pasta cerebro_v3_medio     # mesma API HTTP do v0
"""
import argparse, glob, json, math, os, random, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import torch
import torch.nn as nn
import torch.nn.functional as F
from tokenizador_bpe import (TokenizerCaractere, TokenizerBPE, tokenizador_de_dict, carregar_tokenizador)

TAMANHOS = {
    #            camadas, cabeças, dimensão, contexto
    "mini":          dict(n_camadas=4,  n_cabecas=4,  d=128,  contexto=128),   # ~1M, roda em CPU (testes)
    "pequeno":       dict(n_camadas=6,  n_cabecas=6,  d=384,  contexto=256),   # ~11M (com vocab 16k: ~17M)
    "intermediario": dict(n_camadas=8,  n_cabecas=8,  d=512,  contexto=256),   # ~25M (com vocab 16k: ~34M)
    "medio":         dict(n_camadas=12, n_cabecas=12, d=768,  contexto=512),   # TAMANHO PRINCIPAL: ~85M sem embedding, ~97M com vocab 16k
    "grande":        dict(n_camadas=28, n_cabecas=16, d=1024, contexto=1024),  # ~370M; só documentado, não treinamos aqui
}
ROPE_BASE = 10000.0
PASTA_PADRAO = "cerebro_v3"
LN2 = math.log(2)


def largura_mlp(d):
    """≈ 8/3·d arredondado para o múltiplo de 64 mais próximo (hardware gosta de múltiplos de 64)."""
    return max(64, int(round(8 * d / 3 / 64)) * 64)


# ---------- o modelo ----------
class RMSNorm(nn.Module):
    def __init__(self, d, eps=1e-5):
        super().__init__()
        self.eps = eps
        self.peso = nn.Parameter(torch.ones(d))

    def forward(self, x):
        xf = x.float()  # a conta da média dos quadrados é feita em fp32 por estabilidade
        return (xf * torch.rsqrt(xf.pow(2).mean(-1, keepdim=True) + self.eps)).to(x.dtype) * self.peso


def tabelas_rope(posicoes, dim_cabeca, base, device):
    """cos e sin (em fp32) para cada posição. Cada par de dimensões (2i, 2i+1) gira com frequência base^(-2i/dim)."""
    inv = base ** (-torch.arange(0, dim_cabeca, 2, device=device, dtype=torch.float32) / dim_cabeca)
    ang = posicoes.to(device=device, dtype=torch.float32)[:, None] * inv[None, :]  # (T, dim/2)
    return ang.cos(), ang.sin()


def aplicar_rope(x, cos, sin):
    """x: (B, cabeças, T, dim). Gira o par (primeira metade, segunda metade) pelo ângulo da posição."""
    metade = x.size(-1) // 2
    x1, x2 = x[..., :metade], x[..., metade:]
    cos, sin = cos.to(x.dtype), sin.to(x.dtype)
    return torch.cat([x1 * cos - x2 * sin, x2 * cos + x1 * sin], dim=-1)


class CacheKV:
    """Guarda k e v (já com RoPE aplicado) de cada camada. `pos` é a posição ABSOLUTA do próximo token;
    como o RoPE só usa distâncias, descartar o início do cache (janela deslizante) não atrapalha."""
    def __init__(self, n_camadas):
        self.kv = [None] * n_camadas
        self.pos = 0


class Atencao(nn.Module):
    """Cada token olha para os anteriores e decide em quais prestar atenção."""
    def __init__(self, d, n_cabecas, contexto):
        super().__init__()
        self.n_cabecas, self.contexto = n_cabecas, contexto
        self.qkv = nn.Linear(d, 3 * d, bias=False)
        self.saida = nn.Linear(d, d, bias=False)

    def forward(self, x, cos, sin, cache=None, camada=0):
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)
        q, k, v = (t.view(B, T, self.n_cabecas, C // self.n_cabecas).transpose(1, 2) for t in (q, k, v))
        q, k = aplicar_rope(q, cos, sin), aplicar_rope(k, cos, sin)
        if cache is None:
            y = F.scaled_dot_product_attention(q, k, v, is_causal=True)  # causal: não vê o futuro
        else:
            passado = cache.kv[camada]
            if passado is not None:
                k, v = torch.cat([passado[0], k], dim=2), torch.cat([passado[1], v], dim=2)
            if k.size(2) > self.contexto:  # janela deslizante: esquece o mais antigo
                k, v = k[:, :, -self.contexto:], v[:, :, -self.contexto:]
            cache.kv[camada] = (k, v)
            if passado is None:
                y = F.scaled_dot_product_attention(q, k, v, is_causal=True)  # preenchimento do prompt
            else:
                assert T == 1, "com cache preenchido, passe um token por vez"
                y = F.scaled_dot_product_attention(q, k, v)  # o token novo enxerga todo o cache
        return self.saida(y.transpose(1, 2).contiguous().view(B, T, C))


class SwiGLU(nn.Module):
    def __init__(self, d):
        super().__init__()
        h = largura_mlp(d)
        self.porta_sobe = nn.Linear(d, 2 * h, bias=False)  # porta e "sobe" juntas numa só multiplicação
        self.baixo = nn.Linear(h, d, bias=False)

    def forward(self, x):
        porta, sobe = self.porta_sobe(x).chunk(2, dim=-1)
        return self.baixo(F.silu(porta) * sobe)


class Bloco(nn.Module):
    """Atenção (comunicação entre tokens) + MLP (pensamento individual de cada token)."""
    def __init__(self, d, n_cabecas, contexto):
        super().__init__()
        self.n1, self.n2 = RMSNorm(d), RMSNorm(d)
        self.atencao = Atencao(d, n_cabecas, contexto)
        self.mlp = SwiGLU(d)

    def forward(self, x, cos, sin, cache=None, camada=0):
        x = x + self.atencao(self.n1(x), cos, sin, cache, camada)
        return x + self.mlp(self.n2(x))


class Cortex(nn.Module):
    def __init__(self, vocab, n_camadas, n_cabecas, d, contexto, rope_base=ROPE_BASE):
        super().__init__()
        assert d % n_cabecas == 0 and (d // n_cabecas) % 2 == 0
        self.contexto, self.rope_base, self.n_cabecas = contexto, rope_base, n_cabecas
        self.tok = nn.Embedding(vocab, d)  # cada token vira um vetor (a posição entra pelo RoPE, não aqui)
        self.blocos = nn.ModuleList(Bloco(d, n_cabecas, contexto) for _ in range(n_camadas))
        self.norma = RMSNorm(d)
        # a saída reaproveita o peso do embedding ("amarrado"): F.linear(x, self.tok.weight) em forward
        self.apply(self._iniciar)
        # camadas que escrevem de volta no fluxo residual começam menores, para os blocos não somarem ruído demais
        for nome, p in self.named_parameters():
            if nome.endswith(("atencao.saida.weight", "mlp.baixo.weight")):
                nn.init.normal_(p, mean=0.0, std=0.02 / math.sqrt(2 * n_camadas))

    @staticmethod
    def _iniciar(m):
        # Com 0.02 a perda inicial fica perto de ln(vocab) (chute aleatório). Sem isto, como a saída
        # compartilha o peso do embedding, ela começaria enorme.
        if isinstance(m, (nn.Linear, nn.Embedding)):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)

    def novo_cache(self):
        return CacheKV(len(self.blocos))

    def forward(self, ids, alvo=None, cache=None):
        B, T = ids.shape
        assert T <= self.contexto, f"sequência ({T}) maior que o contexto ({self.contexto})"
        pos0 = cache.pos if cache is not None else 0
        cos, sin = tabelas_rope(torch.arange(pos0, pos0 + T), self.tok.weight.size(1) // self.n_cabecas, self.rope_base, ids.device)
        x = self.tok(ids)
        for i, b in enumerate(self.blocos):
            x = b(x, cos, sin, cache, i)
        if cache is not None:
            cache.pos += T
        logits = F.linear(self.norma(x), self.tok.weight)
        perda = None if alvo is None else F.cross_entropy(logits.float().view(-1, logits.size(-1)), alvo.view(-1))
        return logits, perda

    @torch.no_grad()
    def gerar(self, ids, n, temperatura=0.8, top_k=40, gerador=None, parar=None, usar_cache=True):
        """Gera até `n` tokens. `parar(lista_de_ids_novos) -> bool` encerra antes (parada antecipada).
        Sem cache recalcula a janela inteira a cada passo (lento, usado só para conferir o cache)."""
        ids = ids[:, -self.contexto:]
        inicio = ids.shape[1]
        cache = self.novo_cache() if usar_cache else None
        logits = self(ids, cache=cache)[0] if usar_cache else None
        for i in range(n):
            if not usar_cache:
                logits = self(ids[:, -self.contexto:])[0]
            lg = logits[:, -1, :].float() / temperatura
            v, _ = torch.topk(lg, min(top_k, lg.size(-1)))
            lg = lg.masked_fill(lg < v[:, [-1]], -float("inf"))
            prox = torch.multinomial(F.softmax(lg, -1), 1, generator=gerador)
            ids = torch.cat([ids, prox], dim=1)
            if parar is not None and parar(ids[0, inicio:].tolist()):
                break
            if usar_cache and i < n - 1:
                logits = self(prox, cache=cache)[0]
        return ids

    def grupos_otimizador(self, weight_decay):
        """Weight decay só nas MATRIZES (dim ≥ 2) de camadas lineares. Normas e embeddings ficam sem decay."""
        com, sem = [], []
        for nome, p in self.named_parameters():
            (com if p.dim() >= 2 and not nome.startswith("tok.") else sem).append(p)
        return [dict(params=com, weight_decay=weight_decay), dict(params=sem, weight_decay=0.0)]


def contar_parametros(cfg):
    with torch.device("meta"):
        m = Cortex(**cfg)
    total = sum(p.numel() for p in m.parameters())
    return total, total - cfg["vocab"] * cfg["d"]


# ---------- agenda de aprendizado WSD ----------
def resolver_estavel_ate(estavel_ate, passos, descida):
    """None -> platô vai até (1-descida)·passos; ≤1 -> fração dos passos; senão -> número do passo."""
    if estavel_ate is None:
        return int(round(passos * (1 - descida)))
    return int(round(estavel_ate * passos)) if estavel_ate <= 1.0 else int(estavel_ate)


def taxa_wsd(passo, lr, aquecimento, estavel_ate, passos, forma="linear", lr_final=0.0):
    """Warmup (linear) -> Stable (constante) -> Decay (linear ou 1-sqrt) até lr·lr_final no último passo.
    `passo` conta de 0. lr_final é fração de lr (0 = termina em zero)."""
    if passo < aquecimento:
        return lr * (passo + 1) / aquecimento
    if passo < estavel_ate or passos <= estavel_ate:
        return lr
    f = min(1.0, (passo - estavel_ate + 1) / (passos - estavel_ate))  # 0 -> 1 durante a descida
    queda = f if forma == "linear" else math.sqrt(f)  # 1-sqrt desce rápido no começo e suave no fim
    return lr * (1 - (1 - lr_final) * queda)


# ---------- dados ----------
def dispositivo():
    if torch.cuda.is_available(): return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available(): return "mps"
    return "cpu"


def ler_textos(caminho):
    arquivos = [caminho] if os.path.isfile(caminho) else sorted(glob.glob(os.path.join(caminho, "**/*.txt"), recursive=True))
    if not arquivos:
        raise SystemExit(f"Nenhum .txt encontrado em {caminho}")
    return "\n\n".join(open(a, encoding="utf-8", errors="ignore").read() for a in arquivos)


def lote_aleatorio(fonte, C, B, gerador, dev):
    i = torch.randint(len(fonte) - C - 1, (B,), generator=gerador)
    x = torch.stack([fonte[j:j + C] for j in i.tolist()]).long()
    y = torch.stack([fonte[j + 1:j + C + 1] for j in i.tolist()]).long()
    return x.to(dev), y.to(dev)


@torch.no_grad()
def perda_amostrada(modelo, fonte, C, B, dev, ctx_amp, n_lotes=20):
    """Perda média em `n_lotes` janelas sorteadas com semente FIXA (não mexe no RNG do treino)."""
    g = torch.Generator().manual_seed(1234)
    modelo.eval()
    with ctx_amp():
        total = sum(modelo(*lote_aleatorio(fonte, C, B, g, dev))[1].item() for _ in range(n_lotes)) / n_lotes
    modelo.train()
    return total


@torch.no_grad()
def perda_completa(modelo, fonte, C, B, dev, ctx_amp):
    """Percorre TODA a validação em janelas consecutivas de C tokens (sem sobreposição). Devolve (perda, n_alvos)."""
    modelo.eval()
    janelas = list(range(0, len(fonte) - C - 1, C))
    soma, n = 0.0, 0
    for k in range(0, len(janelas), B):
        ini = janelas[k:k + B]
        x = torch.stack([fonte[j:j + C] for j in ini]).long().to(dev)
        y = torch.stack([fonte[j + 1:j + C + 1] for j in ini]).long().to(dev)
        with ctx_amp():
            perda = modelo(x, y)[1].item()
        soma += perda * y.numel()
        n += y.numel()
    modelo.train()
    return soma / n, n


def bpc(perda_nats_por_token, n_tokens, n_caracteres):
    """Bits por caractere = perda(nats/token) × tokens / (ln2 × caracteres)."""
    return perda_nats_por_token * n_tokens / (LN2 * n_caracteres)


def contexto_amp(dev, precisao):
    if dev == "cuda" and precisao != "fp32":
        dtype = torch.bfloat16 if precisao == "bf16" else torch.float16
        return lambda: torch.autocast("cuda", dtype=dtype)
    return lambda: torch.autocast("cpu", enabled=False)


def escolher_precisao(dev, pedida):
    if pedida != "auto":
        return pedida
    if dev == "cuda":
        return "bf16" if torch.cuda.is_bf16_supported() else "fp16"
    return "fp32"


# ---------- checkpoint ----------
def gravar_atomico(objeto, caminho):
    """Escreve em .tmp e renomeia: se o Colab cair no meio, o arquivo antigo continua inteiro."""
    tmp = caminho + ".tmp"
    torch.save(objeto, tmp)
    with open(tmp, "rb") as f:
        os.fsync(f.fileno())
    if os.path.exists(caminho):
        os.replace(caminho, caminho.replace(".pt", "_anterior.pt"))  # guarda a versão anterior como seguro extra
    os.replace(tmp, caminho)


def carregar(pasta=PASTA_PADRAO, dev=None):
    """Carrega para inferência. Usa `modelo.pt` (leve) se existir, senão `checkpoint.pt` (completo)."""
    dev = dev or dispositivo()
    for nome in ("modelo.pt", "checkpoint.pt"):
        cam = os.path.join(pasta, nome)
        if os.path.exists(cam):
            ck = torch.load(cam, map_location="cpu", weights_only=True)
            modelo = Cortex(**ck["cfg"])
            modelo.load_state_dict(ck["modelo"])
            return modelo.to(dev).eval(), tokenizador_de_dict(ck["tokenizador"]), dev
    raise SystemExit(f"Nenhum modelo.pt/checkpoint.pt em {pasta}")


def exportar(a):
    """Gera o modelo.pt leve (só pesos + config + tokenizador) a partir do checkpoint completo."""
    ck = torch.load(os.path.join(a.pasta, "checkpoint.pt"), map_location="cpu", weights_only=True)
    gravar_atomico({k: ck[k] for k in ("modelo", "cfg", "tokenizador", "passo")}, os.path.join(a.pasta, "modelo.pt"))
    print(f"modelo.pt salvo em {a.pasta}")


# ---------- treino ----------
CAMPOS_AGENDA = ("passos", "lr", "aquecimento", "estavel_ate", "descida", "forma", "lr_final", "lote", "acumular", "semente")


def preparar_dados(a, tk_existente, pasta):
    """Devolve (tokenizador, treino, validacao, caracteres_validacao). Valida sem vazamento se --val_dados."""
    texto = ler_textos(a.dados)
    if a.val_dados:
        val_texto = ler_textos(a.val_dados)
    else:
        corte = int(0.98 * len(texto))
        texto, val_texto = texto[:corte], texto[corte:]
        print("AVISO: sem --val_dados; usando os 2% finais do próprio arquivo como validação. Se o corpus tiver "
              "trechos repetidos (ou for embaralhado/duplicado), a validação pode estar CONTAMINADA e a perda de "
              "validação fica otimista demais. Prefira --val_dados com um arquivo separado.")
    tk = tk_existente
    if tk is None:
        if a.tokenizador == "caractere":
            tk = TokenizerCaractere(texto + val_texto)  # vocabulário inclui os caracteres da validação (nenhum é descartado)
        elif a.tokenizador_json and os.path.exists(a.tokenizador_json):
            tk = carregar_tokenizador(a.tokenizador_json)
        else:
            print(f"treinando BPE (vocab {a.vocab}) a partir dos dados de treino...")
            tk = TokenizerBPE.treinar([texto[i:i + 1_000_000] for i in range(0, len(texto), 1_000_000)], a.vocab)
    treino = tk.codificar_tensor(texto)
    validacao = tk.codificar_tensor(val_texto)
    return tk, treino, validacao, tk.contar_caracteres(val_texto)


def treinar(a):
    dev = dispositivo()
    pasta = a.pasta
    os.makedirs(pasta, exist_ok=True)
    caminho_ck = os.path.join(pasta, "checkpoint.pt")
    ck = None
    if a.retomar and os.path.exists(caminho_ck):
        ck = torch.load(caminho_ck, map_location="cpu", weights_only=True)
        salvo = ck["args"]
        fixos = ("lr", "aquecimento", "lote", "acumular", "semente") if a.estender else CAMPOS_AGENDA
        for c in fixos:
            setattr(a, c, salvo[c])
        a.tamanho = salvo["tamanho"]
        print(f"retomando de {caminho_ck} no passo {ck['passo']} ("
              + ("agenda ESTENDIDA: passos/platô novos, sem reaquecer" if a.estender else "agenda idêntica à salva") + ")")
    elif a.retomar:
        print(f"--retomar: nenhum checkpoint em {pasta}; começando do zero.")

    tk, treino, validacao, car_val = preparar_dados(a, tokenizador_de_dict(ck["tokenizador"]) if ck else None, pasta)
    cfg = ck["cfg"] if ck else dict(TAMANHOS[a.tamanho], vocab=tk.n_vocab, rope_base=a.rope_base)
    C = cfg["contexto"]
    if len(validacao) <= C + 1:
        raise SystemExit(f"Validação curta demais ({len(validacao)} tokens) para um contexto de {C}.")

    torch.manual_seed(a.semente)
    modelo = Cortex(**cfg)
    n_total, n_sem_emb = contar_parametros(cfg)
    modelo = modelo.to(dev)
    precisao = escolher_precisao(dev, a.precisao)
    ctx_amp = contexto_amp(dev, precisao)
    opt = torch.optim.AdamW(modelo.grupos_otimizador(a.weight_decay), lr=a.lr, betas=(0.9, 0.95))
    escala = torch.amp.GradScaler("cuda", enabled=(dev == "cuda" and precisao == "fp16"))
    gerador = torch.Generator().manual_seed(a.semente + 1)
    passo_ini, historico = 0, []
    if ck:
        modelo.load_state_dict(ck["modelo"])
        opt.load_state_dict(ck["otimizador"])
        escala.load_state_dict(ck["escala"])
        gerador.set_state(ck["rng"]["gerador"])
        torch.set_rng_state(ck["rng"]["torch"])
        if dev == "cuda" and ck["rng"].get("cuda") is not None:
            torch.cuda.set_rng_state_all(ck["rng"]["cuda"])
        passo_ini, historico = ck["passo"], ck.get("historico", [])

    estavel = resolver_estavel_ate(a.estavel_ate, a.passos, a.descida)
    if ck and a.estender and passo_ini > estavel:
        print(f"AVISO: o checkpoint (passo {passo_ini}) já passou do fim do platô novo ({estavel}); a taxa será a da descida.")
    tokens_passo = a.lote * a.acumular * C
    print(f"dispositivo: {dev} ({precisao}) | tokenizador: {tk.tipo} (vocab {tk.n_vocab}) | treino: {len(treino):,} tokens | "
          f"validação: {len(validacao):,} tokens ({car_val:,} caracteres)")
    print(f"parâmetros: {n_total/1e6:.2f}M (sem embedding: {n_sem_emb/1e6:.2f}M) | tokens por passo: {tokens_passo:,}")
    print(f"agenda WSD: aquece {a.aquecimento} passos, platô até {estavel}, desce ({a.forma}) até {a.passos} | "
          f"total previsto: {a.passos*tokens_passo/1e6:.0f}M tokens = {a.passos*tokens_passo/n_total:.1f} tokens/parâmetro "
          f"(referência Chinchilla: 20) = {a.passos*tokens_passo/len(treino):.1f} voltas no corpus")

    def salvar(final=False):
        estado = dict(
            modelo=modelo.state_dict(), otimizador=opt.state_dict(), escala=escala.state_dict(), passo=passo_atual[0],
            rng=dict(torch=torch.get_rng_state(), gerador=gerador.get_state(),
                     cuda=torch.cuda.get_rng_state_all() if dev == "cuda" else None),
            cfg=cfg, tokenizador=tk.para_dict(), args={c: getattr(a, c) for c in CAMPOS_AGENDA} | {"tamanho": a.tamanho},
            historico=historico, versao=3)
        gravar_atomico(estado, caminho_ck)
        if final:
            gravar_atomico({k: estado[k] for k in ("modelo", "cfg", "tokenizador", "passo")}, os.path.join(pasta, "modelo.pt"))
        json.dump(tk.para_dict(), open(os.path.join(pasta, "tokenizador.json.tmp"), "w", encoding="utf-8"), ensure_ascii=False)
        os.replace(os.path.join(pasta, "tokenizador.json.tmp"), os.path.join(pasta, "tokenizador.json"))

    def avaliar(passo):
        pt = perda_amostrada(modelo, treino, C, a.lote, dev, ctx_amp, a.aval_lotes)
        pv = perda_amostrada(modelo, validacao, C, a.lote, dev, ctx_amp, a.aval_lotes)
        b = bpc(pv, len(validacao), car_val)
        historico.append(dict(passo=passo, treino=pt, val=pv, bpc=b))
        print(f"passo {passo:>6} | perda treino {pt:.3f} | perda val {pv:.3f} | BPC val {b:.3f} | {time.time()-inicio:.0f}s", flush=True)

    perdas, passo_atual = [], [passo_ini]
    inicio, sessao = time.time(), 0
    modelo.train()
    for passo in range(passo_ini, a.passos):
        if a.avaliar_cada and passo % a.avaliar_cada == 0:
            avaliar(passo)
        lr = taxa_wsd(passo, a.lr, a.aquecimento, estavel, a.passos, a.forma, a.lr_final)
        for g in opt.param_groups: g["lr"] = lr
        opt.zero_grad(set_to_none=True)
        perda_passo = 0.0
        for _ in range(a.acumular):  # acumulação de gradiente: lote efetivo maior sem gastar mais memória
            x, y = lote_aleatorio(treino, C, a.lote, gerador, dev)
            with ctx_amp():
                _, perda = modelo(x, y)
            escala.scale(perda / a.acumular).backward()
            perda_passo += perda.item() / a.acumular
        escala.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(modelo.parameters(), 1.0)
        escala.step(opt)
        escala.update()
        perdas.append(perda_passo)
        passo_atual[0] = passo + 1
        sessao += 1
        if a.log_cada and (passo + 1) % a.log_cada == 0:
            dt = time.time() - inicio
            print(f"passo {passo+1:>6} | lr {lr:.2e} | perda {perda_passo:.3f} | {sessao*tokens_passo/dt:,.0f} tokens/s", flush=True)
        if a.salvar_cada and (passo + 1) % a.salvar_cada == 0 and passo + 1 < a.passos:
            salvar()
            print(f"checkpoint salvo em {pasta}/ (passo {passo+1})", flush=True)
        if a.parar_apos and sessao >= a.parar_apos and passo + 1 < a.passos:
            salvar()
            print(f"parada pedida após {sessao} passos; checkpoint salvo (passo {passo+1}). Use --retomar para continuar.")
            return dict(perdas=perdas, pasta=pasta, concluido=False)

    final = passo_atual[0] >= a.passos
    if final:
        avaliar(a.passos)
    salvar(final=final)
    if final:
        pv, n = perda_completa(modelo, validacao, C, a.lote, dev, ctx_amp)
        print(f"VALIDAÇÃO COMPLETA: perda {pv:.4f} nats/token | BPC {bpc(pv, len(validacao), car_val):.4f} "
              f"(token = {car_val/len(validacao):.2f} caracteres)")
        print(f"salvo em {pasta}/ (checkpoint.pt completo e modelo.pt leve)")
    return dict(perdas=perdas, pasta=pasta, concluido=final)


def avaliar_cmd(a):
    """Avalia um modelo salvo na validação inteira e imprime perda e BPC."""
    modelo, tk, dev = carregar(a.pasta)
    precisao = escolher_precisao(dev, a.precisao)
    texto = ler_textos(a.val_dados)
    val = tk.codificar_tensor(texto)
    car = tk.contar_caracteres(texto)
    pv, n = perda_completa(modelo, val, modelo.contexto, a.lote, dev, contexto_amp(dev, precisao))
    print(f"validação: {len(val):,} tokens, {car:,} caracteres ({car/len(val):.2f} car/token)")
    print(f"perda {pv:.4f} nats/token | BPC {bpc(pv, len(val), car):.4f} bits por caractere")
    return pv, bpc(pv, len(val), car)


# ---------- geração e servidor ----------
def continuar(modelo, tk, dev, inicio, n, temperatura=0.8, parar_em=None, top_k=40, gerador=None):
    """Devolve só o que o córtex escreveu depois de `inicio`, cortando no primeiro texto de `parar_em`."""
    parar_em = [s for s in (parar_em or []) if s]
    ids = torch.tensor([tk.codificar(inicio) or [0]], device=dev)
    ini = ids.shape[1]
    parar = None
    if parar_em:
        parar = lambda novos: any(s in tk.decodificar(novos) for s in parar_em)
    saida = modelo.gerar(ids, n, temperatura=temperatura, top_k=top_k, gerador=gerador, parar=parar)[0, ini:].tolist()
    texto = tk.decodificar(saida)
    if saida and texto.endswith("�"):  # byte de um caractere UTF-8 cortado no meio pelo limite n
        texto = texto.rstrip("�")
    cortes = [texto.find(s) for s in parar_em if s in texto]
    return texto[:min(cortes)] if cortes else texto


def criar_manipulador(modelo, tk, dev, parar_padrao=("\n\n",)):
    trava = threading.Lock()  # um modelo só: gera uma requisição por vez (o /saude continua respondendo)

    class Manipulador(BaseHTTPRequestHandler):
        def _responder(self, status, corpo):
            dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(dados)))
            self.end_headers()
            self.wfile.write(dados)

        def log_message(self, *args):
            pass

        def do_GET(self):
            self._responder(200, {"ok": True, "versao": 3}) if self.path == "/saude" else self._responder(404, {"erro": "não encontrado"})

        def do_POST(self):
            if self.path != "/gerar":
                return self._responder(404, {"erro": "não encontrado"})
            try:
                req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                inicio = req["inicio"]
                n = max(1, min(int(req.get("n", 200)), 1000))
                temperatura = float(req.get("temperatura", 0.8))
                parar_em = req.get("parar_em")
                parar_em = list(parar_padrao) if parar_em is None else parar_em  # [] desliga a parada
                if not isinstance(inicio, str) or temperatura <= 0 or not isinstance(parar_em, list) \
                        or not all(isinstance(s, str) for s in parar_em):
                    raise ValueError
            except (KeyError, ValueError, TypeError):
                return self._responder(400, {"erro": "corpo esperado: {inicio: str, n?: int, temperatura?: float > 0, parar_em?: [str]}"})
            with trava, torch.inference_mode():
                texto = continuar(modelo, tk, dev, inicio, n, temperatura, parar_em)
            self._responder(200, {"texto": texto})

    return Manipulador


def servir(a):
    modelo, tk, dev = carregar(a.pasta)
    print(f"córtex v3 ouvindo em http://0.0.0.0:{a.porta} ({dev})", flush=True)
    ThreadingHTTPServer(("0.0.0.0", a.porta), criar_manipulador(modelo, tk, dev)).serve_forever()


def gerar_cmd(a):
    modelo, tk, dev = carregar(a.pasta)
    inicio = a.inicio.replace("\\n", "\n")
    with torch.inference_mode():
        print(inicio + continuar(modelo, tk, dev, inicio, a.n, a.temperatura, a.parar_em))


def tamanhos_cmd(a):
    print(f"{'tamanho':<14}{'camadas':>8}{'cab.':>6}{'d':>6}{'ctx':>6}{'MLP':>6}  {'params vocab 16000':>22}  {'params vocab 140':>18}")
    for nome, t in TAMANHOS.items():
        (t16, s16), (t140, _) = contar_parametros(dict(t, vocab=16000)), contar_parametros(dict(t, vocab=140))
        print(f"{nome:<14}{t['n_camadas']:>8}{t['n_cabecas']:>6}{t['d']:>6}{t['contexto']:>6}{largura_mlp(t['d']):>6}"
              f"  {t16/1e6:>8.1f}M (sem emb {s16/1e6:>6.1f}M)  {t140/1e6:>14.2f}M")


def criar_parser():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("treinar")
    t.add_argument("--dados", required=True, help="arquivo .txt ou pasta com .txt")
    t.add_argument("--val_dados", default=None, help="arquivo de validação SEM vazamento (ex.: textos/corpus_validacao.txt)")
    t.add_argument("--tamanho", default="mini", choices=TAMANHOS)
    t.add_argument("--tokenizador", default="bpe", choices=["caractere", "bpe"])
    t.add_argument("--tokenizador_json", default=None, help="BPE já treinado (tokenizador_bpe.py treinar); senão treina aqui")
    t.add_argument("--vocab", type=int, default=16000)
    t.add_argument("--rope_base", type=float, default=ROPE_BASE)
    t.add_argument("--passos", type=int, default=3000)
    t.add_argument("--lote", type=int, default=32, help="sequências por micro-lote")
    t.add_argument("--acumular", type=int, default=1, help="micro-lotes por passo (tokens/passo = lote·acumular·contexto)")
    t.add_argument("--lr", type=float, default=6e-4)
    t.add_argument("--weight_decay", type=float, default=0.1)
    t.add_argument("--aquecimento", type=int, default=200, help="passos de aquecimento linear")
    t.add_argument("--estavel_ate", type=float, default=None, help="fim do platô: passo (>1) ou fração (≤1) dos passos; padrão 1-descida")
    t.add_argument("--descida", type=float, default=0.2, help="fração final dos passos em descida (se --estavel_ate omitido)")
    t.add_argument("--forma", default="linear", choices=["linear", "1-sqrt"], help="formato da descida final")
    t.add_argument("--lr_final", type=float, default=0.0, help="taxa final como fração de --lr")
    t.add_argument("--estender", action="store_true", help="com --retomar: usa --passos/--estavel_ate novos sem reaquecer (continua o platô)")
    t.add_argument("--retomar", action="store_true", help="continua EXATAMENTE do checkpoint.pt de --pasta")
    t.add_argument("--precisao", default="auto", choices=["auto", "fp16", "bf16", "fp32"])
    t.add_argument("--avaliar_cada", type=int, default=250)
    t.add_argument("--aval_lotes", type=int, default=20)
    t.add_argument("--log_cada", type=int, default=50)
    t.add_argument("--salvar_cada", type=int, default=0)
    t.add_argument("--parar_apos", type=int, default=0, help="encerra (salvando) após N passos NESTA sessão; útil em testes/limites de tempo")
    t.add_argument("--semente", type=int, default=0)
    t.add_argument("--pasta", default=PASTA_PADRAO)
    v = sub.add_parser("avaliar")
    v.add_argument("--val_dados", required=True)
    v.add_argument("--pasta", default=PASTA_PADRAO)
    v.add_argument("--lote", type=int, default=16)
    v.add_argument("--precisao", default="auto", choices=["auto", "fp16", "bf16", "fp32"])
    g = sub.add_parser("gerar")
    g.add_argument("--pasta", default=PASTA_PADRAO)
    g.add_argument("--inicio", default="O ")
    g.add_argument("--n", type=int, default=200)
    g.add_argument("--temperatura", type=float, default=0.8)
    g.add_argument("--parar_em", action="append", default=None)
    sv = sub.add_parser("servir")
    sv.add_argument("--porta", type=int, default=8000)
    sv.add_argument("--pasta", default=PASTA_PADRAO)
    e = sub.add_parser("exportar")
    e.add_argument("--pasta", default=PASTA_PADRAO)
    sub.add_parser("tamanhos")
    return ap


if __name__ == "__main__":
    a = criar_parser().parse_args()
    {"treinar": treinar, "avaliar": avaliar_cmd, "gerar": gerar_cmd, "servir": servir,
     "exportar": exportar, "tamanhos": tamanhos_cmd}[a.cmd](a)
