"""Mede a latência de gerar 80 tokens com o `medio` (pesos ALEATÓRIOS) na CPU. Só estima velocidade, não qualidade.
Uso: python tests_v3/medir_latencia.py [tamanho] [vocab]"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import torch
import cortex_v3 as C

tam = sys.argv[1] if len(sys.argv) > 1 else "medio"
vocab = int(sys.argv[2]) if len(sys.argv) > 2 else 16000
torch.manual_seed(0)
m = C.Cortex(vocab=vocab, **C.TAMANHOS[tam]).eval()
print(f"{tam}: {sum(p.numel() for p in m.parameters())/1e6:.1f}M parâmetros, {torch.get_num_threads()} threads, "
      f"{(os.cpu_count() or 0)} CPUs")
prompt = torch.randint(vocab, (1, 40))  # ~um prompt curto
with torch.inference_mode():
    m.gerar(prompt, 4)  # aquecimento
    for rotulo, cache in (("com KV cache", True), ("sem cache", False)):
        ts = []
        for _ in range(3):
            t = time.time(); m.gerar(prompt, 80, usar_cache=cache); ts.append(time.time() - t)
        print(f"80 tokens {rotulo}: {min(ts):.2f}s (melhor de 3; médias {sum(ts)/3:.2f}s) -> {80/min(ts):.1f} tokens/s")
