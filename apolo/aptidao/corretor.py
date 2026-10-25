"""Corretor: extrai o código do texto gerado e o executa em container isolado (nunca no host)."""
import json
import os
import shlex
import shutil
import subprocess
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
IMAGEM_PADRAO = "apolo-aptidao:py313"   # python:3.13-slim + git (ver Dockerfile)
IMAGEM_BASE = "python:3.13-slim"
MARCADORES = ("Saída:", "Erro:", "Exercício:", "Lição:")


def extrair_codigo(texto):
    """Do início até a linha 'Saída:' (ou 'Erro:', outro bloco) ou a primeira linha em branco."""
    linhas = []
    for linha in texto.replace("\r", "").split("\n"):
        if linha.strip() == "" or linha.strip() in MARCADORES or linha.startswith(("Exercício:", "Lição:")):
            break
        linhas.append(linha)
    return "\n".join(linhas).strip("\n")


def normalizar(texto):
    return "\n".join(l.strip() for l in (texto or "").strip().split("\n")).strip()


def _docker(args):
    base = ["docker"] + args
    if subprocess.run(["docker", "version", "-f", "{{.Server.Version}}"], capture_output=True).returncode == 0:
        return base
    return ["sg", "docker", "-c", " ".join(shlex.quote(a) for a in base)]


def imagem_disponivel(imagem):
    r = subprocess.run(_docker(["image", "inspect", imagem]), capture_output=True)
    return r.returncode == 0


def escolher_imagem(imagem=None):
    imagem = imagem or os.environ.get("APTIDAO_IMAGEM") or IMAGEM_PADRAO
    if imagem_disponivel(imagem):
        return imagem
    if imagem == IMAGEM_PADRAO:
        r = subprocess.run(_docker(["build", "-q", "-t", IMAGEM_PADRAO, AQUI]), capture_output=True, text=True)
        if r.returncode == 0:
            return IMAGEM_PADRAO
    raise RuntimeError(f"Imagem Docker '{imagem}' indisponível. Rode: docker build -t {IMAGEM_PADRAO} aptidao/")


def executar_em_container(itens, imagem=None, timeout=10, paralelo=3):
    """itens: [{id, tipo, codigo, entradas}] -> {id: {saida, erro, timeout}}."""
    if not itens:
        return {}
    imagem = escolher_imagem(imagem)
    pasta = tempfile.mkdtemp(prefix="aptidao_")
    try:
        os.chmod(pasta, 0o755)
        with open(os.path.join(pasta, "itens.json"), "w", encoding="utf-8") as f:
            json.dump(itens, f)
        os.chmod(os.path.join(pasta, "itens.json"), 0o644)
        shutil.copy(os.path.join(AQUI, "runner_container.py"), os.path.join(pasta, "runner_container.py"))
        os.chmod(os.path.join(pasta, "runner_container.py"), 0o644)
        cmd = ["run", "--rm", "--network", "none", "--read-only", "--tmpfs", "/tmp", "--memory", "512m",
               "--cpus", "1", "--pids-limit", "256", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
               "-e", f"APTIDAO_TIMEOUT={timeout}", "-e", f"APTIDAO_PARALELO={paralelo}", "-e", "HOME=/tmp",
               "-v", f"{pasta}:/dados:ro", imagem, "python", "/dados/runner_container.py"]
        total = timeout * len(itens) / max(1, paralelo) + 120
        r = subprocess.run(_docker(cmd), capture_output=True, text=True, timeout=total)
        if r.returncode != 0:
            raise RuntimeError(f"Docker falhou: {r.stderr[-500:]}")
        return {x["id"]: x for x in json.loads(r.stdout)}
    finally:
        shutil.rmtree(pasta, ignore_errors=True)


def corrigir(problemas, textos, **kw):
    """problemas: lista de dicts do gerador; textos: {id: texto gerado}. Devolve {id: resultado}."""
    itens, res = [], {}
    for p in problemas:
        if p["id"] not in textos:
            continue
        codigo = extrair_codigo(textos[p["id"]])
        if not codigo.strip():
            res[p["id"]] = {"ok": False, "motivo": "vazio", "saida": "", "erro": None}
            continue
        itens.append({"id": p["id"], "tipo": p["tipo"], "codigo": codigo, "entradas": p.get("entradas")})
    saidas = executar_em_container(itens, **kw)
    por_id = {p["id"]: p for p in problemas}
    for it in itens:
        s = saidas.get(it["id"], {"saida": "", "erro": "sem resposta"})
        esperado = normalizar(por_id[it["id"]]["saida_esperada"])
        if s.get("timeout"):
            motivo, ok = "timeout", False
        elif s.get("erro"):
            motivo, ok = "erro", False
        elif normalizar(s["saida"]) != esperado:
            motivo, ok = "saida_diferente", False
        else:
            motivo, ok = "ok", True
        res[it["id"]] = {"ok": ok, "motivo": motivo, "saida": s.get("saida", "")[:500], "erro": s.get("erro")}
    return res
