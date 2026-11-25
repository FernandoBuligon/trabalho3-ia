"""
Executa a MESMA consulta no simulador e no ExSINTA real (via interface, sem foco)
e mostra a previsão do simulador ao lado das capturas da janela de resultados.

Uso (programático):
    from gui_check import checar
    checar("../saida/Filmes.bcm", {"var": [...], ...}, "nome_caso")
"""
import json
import os
import subprocess
import sys

import bcm
import simulador

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
OUT = os.path.join(RAIZ, "testes", "gui")
PS = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"


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


def checar(arquivo_base: str, respostas: dict, caso: str, abrir: bool = True):
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
        subprocess.run([PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                        os.path.join(AQUI, "gui", "abrir_base.ps1"), "-Base",
                        os.path.abspath(arquivo_base)], check=True)
    p = subprocess.run([PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                        os.path.join(AQUI, "gui", "consulta.ps1"), "-Steps", steps_file,
                        "-Titulo", base.name.text, "-OutDir", outdir,
                        "-NResultados", str(sum(t.show_results for t in base.targets))],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(f"=== caso {caso}")
    print("perguntas previstas:", res.perguntas)
    print("--- GUI:")
    print(p.stdout.strip())
    if p.stderr.strip():
        print("STDERR:", p.stderr.strip()[:2000])
    print("--- simulador:")
    for alvo, vals in res.objetivos.items():
        print(f"  {alvo}:")
        for v, c in vals[:15]:
            print(f"    {c:6.2f}  {v}")
    return res, outdir
