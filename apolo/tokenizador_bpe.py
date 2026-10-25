"""
Apolo · Tokenizadores do córtex v3
==================================
Dois tokenizadores com a MESMA interface (`codificar`, `decodificar`, `n_vocab`, `para_dict`):

  * TokenizerCaractere  -> um id por caractere (como no v0/v2).
  * TokenizerBPE        -> BPE em nível de BYTE, treinado em português + código.

Por que BPE? Um token passa a valer ~3-4 caracteres de português. Com o mesmo contexto de 512
tokens o modelo enxerga ~2000 caracteres (em vez de 512), e cada passo de treino "lê" mais texto.
O preço: a tabela de embeddings cresce. Com vocabulário de 16 000 e d=768, o embedding amarrado
custa 16 000 x 768 ≈ 12M parâmetros (o vocabulário de caractere custava ~0,1M). 16k é um meio-termo:
vocabulário maior comprime mais, mas gasta parâmetros e deixa palavras raras mal treinadas.

Por que nível de BYTE? Qualquer texto vira bytes UTF-8, e os 256 bytes sempre estão no vocabulário.
Logo NUNCA existe "caractere desconhecido" e codificar -> decodificar devolve o texto idêntico
(inclusive `[ ] { } < > \\ | ` e acentos).

Motores:
  * "hf"   : biblioteca `tokenizers` (Hugging Face, escrita em Rust, rápida). É o padrão.
  * "puro" : implementação em Python puro, SEM dependências, só para quando `tokenizers` não existe.
             É lenta para corpus grande (use `--amostra_mb` pequeno), mas produz o mesmo tipo de BPE.

Uso:
  python tokenizador_bpe.py treinar --dados textos/corpus_portugues.txt --saida cerebro_v3/tokenizador.json --vocab 16000
  python tokenizador_bpe.py testar  --tokenizador cerebro_v3/tokenizador.json --dados textos/curriculo
"""
import argparse, glob, json, os, re, time
from collections import Counter

ESPECIAIS = ["<|fim|>"]  # mínimo: marca de fim de documento (reservado; o corpus separa documentos por \n\n)


def _tem_hf():
    try:
        import tokenizers  # noqa: F401
        return True
    except ImportError:
        return False


# ---------- caractere ----------
class TokenizerCaractere:
    tipo = "caractere"

    def __init__(self, texto=None, vocab=None):
        self.vocab = vocab or sorted(set(texto))
        self.id = {c: i for i, c in enumerate(self.vocab)}

    @property
    def n_vocab(self):
        return len(self.vocab)

    def codificar(self, s):
        return [self.id[c] for c in s if c in self.id]  # caracteres fora do vocabulário são ignorados

    def codificar_tensor(self, s):
        """Rápido para centenas de MB: devolve tensor int32 (usa numpy se houver)."""
        import torch
        try:
            import numpy as np
        except ImportError:
            return torch.tensor(self.codificar(s), dtype=torch.int32)
        if not s:
            return torch.zeros(0, dtype=torch.int32)
        pontos = np.frombuffer(s.encode("utf-32-le"), dtype=np.uint32)
        tabela = np.full(int(pontos.max()) + 1, -1, dtype=np.int64)
        for c, i in self.id.items():
            if ord(c) < len(tabela):
                tabela[ord(c)] = i
        ids = tabela[pontos]
        return torch.from_numpy(ids[ids >= 0].astype(np.int32))

    def contar_caracteres(self, s):
        """Quantos caracteres de `s` o tokenizador realmente representa (para o cálculo de bits por caractere)."""
        return sum(1 for c in s if c in self.id)

    def decodificar(self, ids):
        return "".join(self.vocab[i] for i in ids)

    def para_dict(self):
        return {"tipo": "caractere", "vocab": self.vocab}


# ---------- BPE ----------
# Divide o texto em "palavras" antes de aplicar as fusões (como o GPT-2), para que um token
# nunca atravesse, por exemplo, uma palavra e a pontuação seguinte. Só usado pelo motor puro.
_PADRAO = re.compile(r" ?[^\W\d_]+| ?\d+| ?(?:[^\s\w]|_)+|\s+(?!\S)|\s+")  # letras | dígitos | símbolos (inclui _) | espaços


class _MotorPuro:
    """BPE em nível de byte, em Python puro. ids 0..255 = bytes; depois as fusões; por fim os especiais."""

    def __init__(self, fusoes, especiais):
        self.fusoes = [tuple(f) for f in fusoes]
        self.especiais = list(especiais)
        self.rank = {p: i for i, p in enumerate(self.fusoes)}
        self.pares_id = {p: 256 + i for i, p in enumerate(self.fusoes)}
        self.bytes_de = {i: bytes([i]) for i in range(256)}
        for i, (a, b) in enumerate(self.fusoes):
            self.bytes_de[256 + i] = self.bytes_de[a] + self.bytes_de[b]
        base = 256 + len(self.fusoes)
        self.id_especial = {s: base + i for i, s in enumerate(self.especiais)}
        self.especial_de_id = {i: s for s, i in self.id_especial.items()}
        self.cache = {}
        self.n_vocab = base + len(self.especiais)

    @staticmethod
    def treinar(textos, vocab, especiais):
        contagem = Counter()
        for t in textos:
            contagem.update(_PADRAO.findall(t))
        palavras = {tuple(w.encode("utf-8")): n for w, n in contagem.items()}
        seqs = [list(k) for k in palavras]
        freq = list(palavras.values())
        fusoes = []
        n_fusoes = vocab - 256 - len(especiais)
        for _ in range(max(0, n_fusoes)):
            pares = Counter()
            for s, n in zip(seqs, freq):
                for x, y in zip(s, s[1:]):
                    pares[(x, y)] += n
            if not pares:
                break
            melhor = max(pares.items(), key=lambda kv: (kv[1], -kv[0][0], -kv[0][1]))[0]
            novo = 256 + len(fusoes)
            fusoes.append(melhor)
            for s in seqs:
                i = 0
                while i < len(s) - 1:
                    if s[i] == melhor[0] and s[i + 1] == melhor[1]:
                        s[i:i + 2] = [novo]
                    else:
                        i += 1
        return _MotorPuro(fusoes, especiais)

    def _palavra(self, w):
        r = self.cache.get(w)
        if r is not None:
            return r
        s = list(w.encode("utf-8"))
        while len(s) > 1:
            melhor, pos = None, -1
            for i in range(len(s) - 1):
                rk = self.rank.get((s[i], s[i + 1]))
                if rk is not None and (melhor is None or rk < melhor):
                    melhor, pos = rk, i
            if melhor is None:
                break
            s[pos:pos + 2] = [self.pares_id[(s[pos], s[pos + 1])]]
        self.cache[w] = s
        return s

    def codificar(self, texto):
        ids = []
        if self.especiais:
            partes = re.split("(" + "|".join(re.escape(e) for e in self.especiais) + ")", texto)
        else:
            partes = [texto]
        for p in partes:
            if p in self.id_especial:
                ids.append(self.id_especial[p])
            else:
                for w in _PADRAO.findall(p):
                    ids.extend(self._palavra(w))
        return ids

    def decodificar(self, ids):
        saida = b""
        for i in ids:
            saida += self.especial_de_id[i].encode("utf-8") if i in self.especial_de_id else self.bytes_de[i]
        return saida.decode("utf-8", errors="replace")

    def para_dict(self):
        return {"fusoes": [list(f) for f in self.fusoes], "especiais": self.especiais}


class TokenizerBPE:
    tipo = "bpe"

    def __init__(self, motor, kind):
        self.motor, self.kind = motor, kind  # kind: "hf" ou "puro"

    @property
    def n_vocab(self):
        return self.motor.get_vocab_size() if self.kind == "hf" else self.motor.n_vocab

    @property
    def id_fim(self):
        return self.codificar(ESPECIAIS[0])[0]

    # --- treino ---
    @classmethod
    def treinar(cls, textos, vocab=16000, motor="auto", verbose=True):
        """`textos`: iterável de strings (pedaços de ~1 MB). `motor`: auto | hf | puro."""
        if motor == "auto":
            motor = "hf" if _tem_hf() else "puro"
            if motor == "puro" and verbose:
                print("AVISO: biblioteca `tokenizers` ausente; usando o BPE em Python puro (lento). "
                      "Instale com: pip install tokenizers==0.21.1")
        if motor == "hf":
            from tokenizers import Tokenizer, models, pre_tokenizers, decoders, trainers
            tk = Tokenizer(models.BPE())
            tk.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
            tk.decoder = decoders.ByteLevel()
            tr = trainers.BpeTrainer(vocab_size=vocab, special_tokens=ESPECIAIS,
                                     initial_alphabet=pre_tokenizers.ByteLevel.alphabet(), show_progress=verbose)
            tk.train_from_iterator(textos, tr)
            return cls(tk, "hf")
        return cls(_MotorPuro.treinar(textos, vocab, ESPECIAIS), "puro")

    # --- uso ---
    def codificar(self, s):
        if self.kind == "hf":
            return self.motor.encode(s).ids
        return self.motor.codificar(s)

    def codificar_tensor(self, s, pedaco=1_000_000):
        """Codifica textos enormes em pedaços cortados em quebras de linha (cada pedaço em paralelo no motor hf)."""
        import torch
        pedacos, i = [], 0
        while i < len(s):
            j = min(len(s), i + pedaco)
            if j < len(s):
                k = s.rfind("\n", i, j)
                j = k + 1 if k > i else j
            pedacos.append(s[i:j])
            i = j
        if self.kind == "hf":
            ids = [e.ids for e in self.motor.encode_batch(pedacos)]
        else:
            ids = [self.motor.codificar(p) for p in pedacos]
        try:
            import numpy as np
            return torch.from_numpy(np.concatenate([np.asarray(x, dtype=np.int32) for x in ids])) if ids else torch.zeros(0, dtype=torch.int32)
        except ImportError:
            return torch.tensor([t for x in ids for t in x], dtype=torch.int32)

    def contar_caracteres(self, s):
        return len(s)  # sem perdas: todo caractere é representado

    def decodificar(self, ids):
        if self.kind == "hf":
            return self.motor.decode(list(ids), skip_special_tokens=False)
        return self.motor.decodificar(list(ids))

    # --- salvar/carregar (JSON, vai junto do checkpoint) ---
    def para_dict(self):
        if self.kind == "hf":
            return {"tipo": "bpe", "motor": "hf", "dados": self.motor.to_str()}
        return {"tipo": "bpe", "motor": "puro", "dados": self.motor.para_dict()}

    @classmethod
    def de_dict(cls, d):
        if d["motor"] == "hf":
            if not _tem_hf():
                raise RuntimeError("Este tokenizador foi salvo com o motor `tokenizers`; instale: pip install tokenizers==0.21.1")
            from tokenizers import Tokenizer
            return cls(Tokenizer.from_str(d["dados"]), "hf")
        return cls(_MotorPuro(d["dados"]["fusoes"], d["dados"]["especiais"]), "puro")


def tokenizador_de_dict(d):
    if d["tipo"] == "caractere":
        return TokenizerCaractere(vocab=d["vocab"])
    return TokenizerBPE.de_dict(d)


def salvar_tokenizador(tk, caminho):
    tmp = caminho + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(tk.para_dict(), f, ensure_ascii=False)
    os.replace(tmp, caminho)


def carregar_tokenizador(caminho):
    with open(caminho, encoding="utf-8") as f:
        return tokenizador_de_dict(json.load(f))


# ---------- utilitários de linha de comando ----------
def listar_arquivos(caminho):
    return [caminho] if os.path.isfile(caminho) else sorted(glob.glob(os.path.join(caminho, "**/*.txt"), recursive=True))


def pedacos_de_texto(caminho, amostra_mb=0, tamanho=1_000_000):
    """Lê o(s) arquivo(s) em pedaços de ~1 MB. `amostra_mb` > 0 limita o total lido (para treinar o BPE mais rápido)."""
    limite = amostra_mb * 1_000_000 if amostra_mb else float("inf")
    lido = 0
    for arq in listar_arquivos(caminho):
        with open(arq, encoding="utf-8", errors="ignore") as f:
            while lido < limite:
                bloco = f.read(tamanho)
                if not bloco:
                    break
                bloco += f.readline()  # termina o pedaço numa quebra de linha
                lido += len(bloco)
                yield bloco
        if lido >= limite:
            break


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("treinar")
    t.add_argument("--dados", required=True)
    t.add_argument("--saida", required=True)
    t.add_argument("--vocab", type=int, default=16000)
    t.add_argument("--motor", default="auto", choices=["auto", "hf", "puro"])
    t.add_argument("--amostra_mb", type=int, default=0, help="usa só os primeiros N MB do corpus (0 = tudo)")
    e = sub.add_parser("testar", help="teste de ida e volta (codificar -> decodificar) em arquivos reais")
    e.add_argument("--tokenizador", required=True)
    e.add_argument("--dados", required=True)
    a = ap.parse_args()
    if a.cmd == "treinar":
        t0 = time.time()
        tk = TokenizerBPE.treinar(pedacos_de_texto(a.dados, a.amostra_mb), a.vocab, a.motor)
        os.makedirs(os.path.dirname(os.path.abspath(a.saida)), exist_ok=True)
        salvar_tokenizador(tk, a.saida)
        amostra = "".join(pedacos_de_texto(a.dados, 20))
        n = len(tk.codificar(amostra))
        print(f"BPE ({tk.kind}) treinado em {time.time()-t0:.0f}s | vocabulário {tk.n_vocab} | "
              f"{len(amostra)/max(n,1):.2f} caracteres por token (numa amostra de {len(amostra)/1e6:.0f} MB) | salvo em {a.saida}")
    else:
        tk = carregar_tokenizador(a.tokenizador)
        for arq in listar_arquivos(a.dados):
            txt = open(arq, encoding="utf-8", errors="ignore").read()
            ok = tk.decodificar(tk.codificar(txt)) == txt
            print(("OK   " if ok else "FALHOU ") + arq)


if __name__ == "__main__":
    main()
