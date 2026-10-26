"""Roda DENTRO do container do corretor. Lê /dados/itens.json (somente leitura) e escreve um JSON em stdout.

Cada item: {id, tipo: python|sql|shell, codigo, entradas}. Cada solução roda num processo filho (fork) próprio,
com timeout; assim um laço infinito ou um crash não derruba os outros.
"""
import contextlib
import io
import json
import os
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import select

TIMEOUT = float(os.environ.get("APTIDAO_TIMEOUT", "10"))
LIMITE_SAIDA = 100_000
AMBIENTE = {
    "PATH": "/usr/local/bin:/usr/bin:/bin", "LC_ALL": "C.UTF-8", "TZ": "UTC", "TERM": "dumb",
    "GIT_AUTHOR_NAME": "Ana", "GIT_AUTHOR_EMAIL": "ana@exemplo.com", "GIT_COMMITTER_NAME": "Ana",
    "GIT_COMMITTER_EMAIL": "ana@exemplo.com", "GIT_AUTHOR_DATE": "2026-01-10T12:00:00",
    "GIT_COMMITTER_DATE": "2026-01-10T12:00:00", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
}


def _sem_vazias(texto):
    return "\n".join(l.rstrip() for l in texto.splitlines() if l.strip())


def rodar_python(codigo, entradas):
    buf = io.StringIO()
    env = {"__name__": "__main__"}
    if entradas is not None:
        fila = iter(entradas)

        def input_simulado(prompt=""):
            valor = next(fila)
            buf.write(f"{prompt}{valor}\n")
            return valor
        env["input"] = input_simulado
    os.chdir(tempfile.mkdtemp())
    erro = None
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(codigo, "programa.py", "exec"), env)
    except BaseException as e:  # noqa: BLE001
        erro = f"{type(e).__name__}: {e}"
    return buf.getvalue().rstrip("\n"), erro


def rodar_sql(codigo):
    con = sqlite3.connect(":memory:")
    saida, erro = [], None
    try:
        for comando in [c.strip() for c in codigo.split(";") if c.strip()]:
            cur = con.execute(comando)
            if cur.description:
                saida.append(" | ".join(d[0] for d in cur.description))
                for linha in cur.fetchall():
                    saida.append(" | ".join("NULL" if v is None else str(v) for v in linha))
    except Exception as e:  # noqa: BLE001
        erro = f"{type(e).__name__}: {e}"
    finally:
        con.close()
    return "\n".join(saida), erro


def rodar_shell(comandos):
    pasta = tempfile.mkdtemp()
    env = dict(AMBIENTE, HOME=pasta)
    r = subprocess.run(["bash", "--norc", "-c", comandos], cwd=pasta, env=env, capture_output=True,
                       text=True, timeout=TIMEOUT * 2, errors="replace", stdin=subprocess.DEVNULL)
    return _sem_vazias(r.stdout + r.stderr).replace(pasta, "/home/ana/projeto"), None


def executar_item(item):
    t = item["tipo"]
    try:
        if t == "python":
            saida, erro = rodar_python(item["codigo"], item.get("entradas"))
        elif t == "sql":
            saida, erro = rodar_sql(item["codigo"])
        else:
            saida, erro = rodar_shell(item["codigo"])
    except BaseException as e:  # noqa: BLE001
        saida, erro = "", f"{type(e).__name__}: {e}"
    return {"saida": saida[:LIMITE_SAIDA], "erro": erro}


def filho(item, fd):
    """Processo filho (fork do runner já carregado: evita pagar imports a cada solução)."""
    try:
        os.setsid()
        sys.stdin = open(os.devnull)
        dados = json.dumps(executar_item(item)).encode()
        while dados:
            dados = dados[os.write(fd, dados):]
    finally:
        os._exit(0)


def main():
    with open("/dados/itens.json", encoding="utf-8") as f:
        itens = json.load(f)
    paralelo = int(os.environ.get("APTIDAO_PARALELO", "3"))
    resultados, ativos, fila = {}, {}, list(itens)
    sys.stdout.flush()
    while fila or ativos:
        while fila and len(ativos) < paralelo:
            item = fila.pop(0)
            r, w = os.pipe()
            pid = os.fork()
            if pid == 0:
                os.close(r)
                filho(item, w)
            os.close(w)
            ativos[pid] = {"item": item, "r": r, "buf": b"", "fim": time.time() + TIMEOUT}
        fds = [a["r"] for a in ativos.values()]
        prontos, _, _ = select.select(fds, [], [], 0.2)
        for pid in list(ativos):
            a = ativos[pid]
            if a["r"] in prontos:
                pedaco = os.read(a["r"], 65536)
                if pedaco:
                    a["buf"] += pedaco
                    continue
                os.close(a["r"])
                os.waitpid(pid, 0)
                try:
                    r = json.loads(a["buf"].decode("utf-8", "replace"))
                    r["timeout"] = False
                except Exception:  # noqa: BLE001
                    r = {"saida": "", "erro": "Processo morreu sem resposta", "timeout": False}
            elif time.time() > a["fim"]:
                try:
                    os.killpg(pid, signal.SIGKILL)
                except OSError:
                    pass
                os.close(a["r"])
                os.waitpid(pid, 0)
                r = {"saida": "", "erro": "Timeout", "timeout": True}
            else:
                continue
            r["id"] = a["item"]["id"]
            resultados[r["id"]] = r
            del ativos[pid]
    sys.stdout.write(json.dumps([resultados[i["id"]] for i in itens]))


if __name__ == "__main__":
    main()
