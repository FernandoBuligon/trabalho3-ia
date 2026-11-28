"""
Prova de compatibilidade no ExSINTA real: cada base de saida/ é copiada para
testes/sinta_regravado/, aberta no ExSINTA, salva pelo próprio SINTA
(Arquivo › Salvar base) e comparada semanticamente com a original.
Portátil como casos_gui.py: Windows nativo ou Wine.

    python regravar_gui.py
"""
import os
import shutil
import sys

import bcm
from gui_check import FERRAMENTA, caminho_win, driver
from test_formato import comparar

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DEST = os.path.join(RAIZ, "testes", "sinta_regravado")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ok_geral = True
    for nome in ("Famosos", "Filmes"):
        orig = os.path.join(RAIZ, "saida", f"{nome}.bcm")
        copia = os.path.join(DEST, f"{nome.upper()}_SINTA.BCM")
        if os.path.exists(copia):
            os.chmod(copia, 0o644)  # uma cópia somente leitura impediria a sobrescrita
        shutil.copyfile(orig, copia)
        os.chmod(copia, 0o644)
        for args in (("abrir", "--ferramenta", caminho_win(FERRAMENTA), "--base", caminho_win(copia)),
                     ("capturar-base", "--arquivo", caminho_win(os.path.join(DEST, f"{nome.upper()}_SINTA_kib.png"))),
                     ("salvar", "--base", caminho_win(copia))):
            p = driver(*args)
            print(p.stdout.strip())
            if p.returncode != 0:
                sys.exit(f"falhou: {args[0]}")
        a = bcm.read_bcm(open(orig, "rb").read())
        b = bcm.read_bcm(open(copia, "rb").read())
        print(f"== {nome}: {len(a.rules)} regras na original, {len(b.rules)} na regravada pelo ExSINTA")
        ok_geral &= comparar(a, b)
    driver("fechar")
    print("RESULTADO:", "SEMÂNTICA IDÊNTICA nas duas bases" if ok_geral else "DIFERENÇAS ENCONTRADAS")
    sys.exit(0 if ok_geral else 1)


if __name__ == "__main__":
    main()
