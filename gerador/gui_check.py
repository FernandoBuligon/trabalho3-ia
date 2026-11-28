"""
Executa a MESMA consulta no simulador e no ExSINTA real (via interface, sem foco)
e mostra a previsão do simulador ao lado das capturas da janela de resultados.

Portátil: o driver (gui/sinta_driver.py) precisa de um Python *para Windows*.
  - Windows: usa o próprio Python que executa este script;
  - Linux/macOS: usa o Wine com o Python "embeddable" para Windows (win32),
    indicado por SINTA_PYWIN ou, por padrão, ferramenta/python-win32/python.exe.

Uso (programático):
    from gui_check import checar
    checar("../saida/Filmes.bcm", {"var": [...], ...}, "nome_caso")
"""
import json
import os
import shutil
import subprocess
import sys

import bcm
import simulador

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
OUT = os.environ.get("SINTA_GUI_SAIDA") or os.path.join(RAIZ, "testes", "gui")
FERRAMENTA = os.path.join(RAIZ, "ferramenta")
DRIVER = os.path.join(AQUI, "gui", "sinta_driver.py")


def caminho_win(p: str) -> str:
    """Caminho como o processo Windows o enxerga (no Wine, a unidade Z: é a raiz)."""
    p = os.path.abspath(p)
    if os.name == "nt":
        return p
    if shutil.which("winepath"):
        r = subprocess.run(["winepath", "-w", p], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return "Z:" + p.replace("/", "\\")


def driver(*args: str) -> subprocess.CompletedProcess:
    """Executa um comando do driver no Windows nativo ou pelo Wine."""
    if os.name == "nt":
        cmd = [sys.executable, DRIVER]
    else:
        py = os.environ.get("SINTA_PYWIN") or os.path.join(FERRAMENTA, "python-win32", "python.exe")
        if not os.path.exists(py):
            sys.exit(f"Python para Windows não encontrado em {py} (defina SINTA_PYWIN).")
        if not shutil.which("wine"):
            sys.exit("Wine não encontrado: necessário para operar o ExSINTA fora do Windows.")
        cmd = ["wine", py, caminho_win(DRIVER)]
    env = dict(os.environ, WINEDEBUG=os.environ.get("WINEDEBUG", "-all"))
    # saída em arquivo, não em pipe: o ExSINTA continua aberto depois do driver
    log = os.path.join(OUT, ".driver.log")
    os.makedirs(OUT, exist_ok=True)
    with open(log, "w+", encoding="utf-8", errors="replace") as f:
        p = subprocess.run(cmd + list(args), stdout=f, stderr=subprocess.STDOUT,
                           stdin=subprocess.DEVNULL, env=env)
        f.seek(0)
        saida = f.read()
    os.remove(log)
    return subprocess.CompletedProcess(cmd, p.returncode, saida, "")


def passos(base: bcm.Base, respostas, perguntas):
    V = {v.name.text: v for v in base.vars}
    steps = []
    for nome in perguntas:
        v = V[nome]
        ans = respostas.get(nome)
        if v.numeric:
            steps.append({"numero": "" if ans is None else str(ans)})
            continue
        vals = [x.name.text for x in sorted((x for x in base.values if x.var_code == v.code),
                                            key=lambda x: x.position)]
        if not vals:
            vals = ["Sim", "Não"]
        if ans is None:
            marcar = []
        elif isinstance(ans, str):
            marcar = [ans]
        else:
            marcar = [a if isinstance(a, str) else f"{a[0]}@@{a[1]}" for a in ans]
        steps.append({"opcoes": vals, "marcar": marcar})
    return steps


def checar(arquivo_base: str, respostas: dict, caso: str, abrir: bool = True,
           fotos: bool = False, manter_ultimo: bool = False):
    sys.stdout.reconfigure(encoding="utf-8")
    base = bcm.read_bcm(open(arquivo_base, "rb").read())
    res = simulador.simular(base, respostas)
    outdir = os.path.join(OUT, caso)
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):
        os.remove(os.path.join(outdir, f))
    steps_file = os.path.join(outdir, "passos.json")
    json.dump(passos(base, respostas, res.perguntas), open(steps_file, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump({"respostas": respostas, "perguntas": res.perguntas, "objetivos": res.objetivos},
              open(os.path.join(outdir, "simulador.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    if abrir:
        a = driver("abrir", "--ferramenta", caminho_win(FERRAMENTA), "--base", caminho_win(arquivo_base))
        if a.returncode != 0:
            sys.exit(a.stdout[-2000:])
    extra = (["--fotos"] if fotos else []) + (["--manter-ultimo"] if manter_ultimo else [])
    p = driver("consulta", "--passos", caminho_win(steps_file), "--titulo", base.name.text,
               "--saida", caminho_win(outdir),
               "--nresultados", str(sum(t.show_results for t in base.targets)), *extra)
    print(f"=== caso {caso}")
    print("perguntas previstas:", res.perguntas)
    print("--- GUI:")
    print(p.stdout.strip())
    print("--- simulador:")
    for alvo, vals in res.objetivos.items():
        print(f"  {alvo}:")
        for v, c in vals[:15]:
            print(f"    {c:6.2f}  {v}")
    return res, outdir
