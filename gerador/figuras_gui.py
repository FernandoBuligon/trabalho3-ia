"""
Recaptura, no ExSINTA real e com as bases atuais, as figuras usadas no relatório
(relatorio/img/). Portátil como casos_gui.py: Windows nativo ou Wine.

    python figuras_gui.py
"""
import os
import shutil
import sys

import bcm
from casos_gui import CASOS, FIL
from gui_check import OUT, caminho_win, checar, driver, FERRAMENTA

AQUI = os.path.dirname(os.path.abspath(__file__))
IMG = os.environ.get("SINTA_IMG") or os.path.join(AQUI, "..", "relatorio", "img")
X_ABA_HISTORICO = 95  # posição horizontal da aba "Histórico" na janela de resultados


def copiar(origem, destino):
    shutil.copyfile(origem, destino)
    print("  figura:", os.path.relpath(destino, os.path.join(AQUI, "..")))


def limpar_fotos(caso):
    """As fotos de cada pergunta são intermediárias: só as usadas no relatório são copiadas."""
    pasta = os.path.join(OUT, caso)
    for f in os.listdir(pasta):
        if f.startswith("pergunta_") or f == "aba_historico.png":
            os.remove(os.path.join(pasta, f))


def indice_regra(arquivo, nome):
    base = bcm.read_bcm(open(arquivo, "rb").read())
    for i, r in enumerate(sorted(base.rules, key=lambda r: r.position)):
        if r.name.text == nome:
            return i
    sys.exit(f"regra não encontrada: {nome}")


def ok(p, rotulo):
    print(p.stdout.strip())
    if p.returncode != 0:
        sys.exit(f"falhou: {rotulo}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    # Sistema 1: exemplo do relatório (seção 5), com perguntas e aba Histórico
    base, resp = CASOS["famosos_1"]
    checar(base, resp, "famosos_1", fotos=True, manter_ultimo=True)
    hist = os.path.join(OUT, "famosos_1", "aba_historico.png")
    ok(driver("aba", "--nome", "Histórico", "--x", str(X_ABA_HISTORICO), "--arquivo", caminho_win(hist)), "aba")
    copiar(os.path.join(OUT, "famosos_1", "pergunta_07.png"), os.path.join(IMG, "famosos", "pergunta_07.png"))
    copiar(os.path.join(OUT, "famosos_1", "resultado_0.png"), os.path.join(IMG, "famosos", "resultado_grande.png"))
    copiar(hist, os.path.join(IMG, "famosos", "aba_historico.png"))
    limpar_fotos("famosos_1")

    # Sistema 2: exemplo do relatório (seção 6)
    base, resp = CASOS["filmes_3"]
    checar(base, resp, "filmes_3", fotos=True)
    copiar(os.path.join(OUT, "filmes_3", "pergunta_03.png"), os.path.join(IMG, "filmes", "pergunta_03.png"))
    copiar(os.path.join(OUT, "filmes_3", "resultado_0.png"), os.path.join(IMG, "filmes", "resultado_0.png"))
    copiar(os.path.join(OUT, "filmes_3", "resultado_1.png"), os.path.join(IMG, "filmes", "resultado_grande.png"))
    limpar_fotos("filmes_3")

    # regras no editor do SINTA
    ok(driver("abrir", "--ferramenta", caminho_win(FERRAMENTA), "--base", caminho_win(FIL)), "abrir")
    for nome, arq in (("A Origem - perfil completo", "regra_a_origem.png"),
                      ("perfil: adrenalina (ação)", "regra_perfil.png")):
        destino = os.path.join(IMG, "filmes", arq)
        ok(driver("regra", "--indice", str(indice_regra(FIL, nome)), "--arquivo", caminho_win(destino)), nome)
        print("  figura:", os.path.relpath(destino, os.path.join(AQUI, "..")))
    driver("fechar")


if __name__ == "__main__":
    main()
