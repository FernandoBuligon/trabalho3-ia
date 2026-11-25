"""
Regenera e valida TUDO, do zero:

  1. valida os dados (CSV x esquema)
  2. testa o formato .BCM e o gerador
  3. gera saida/Famosos.bcm e saida/Filmes.bcm
  4. audita as bases geradas
  5. (opcional, --avaliar) avaliação quantitativa com o simulador

    python gerar_tudo.py [--avaliar]
"""
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
PY = sys.executable


def run(desc, args, cwd):
    print(f"\n### {desc}")
    p = subprocess.run([PY] + args, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    linhas = [l for l in p.stdout.splitlines() if l.strip()]
    for l in linhas[-12:]:
        print("   ", l)
    if p.returncode != 0:
        print(p.stderr[-2000:])
        print(f"FALHOU: {desc}")
        sys.exit(1)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    dados = os.path.join(RAIZ, "dados")
    run("Validação dos dados: famosos", ["validar_dados.py", "esquema_famosos.yaml"], dados)
    run("Validação dos dados: filmes", ["validar_dados.py", "esquema_filmes.yaml"], dados)
    run("Testes do formato .BCM", ["test_formato.py"], AQUI)
    run("Testes do gerador", ["test_build.py"], AQUI)
    run("Geração: Famosos.bcm", ["build.py", os.path.join(dados, "famosos.yaml")], AQUI)
    run("Geração: Filmes.bcm", ["build.py", os.path.join(dados, "filmes.yaml")], AQUI)
    run("Auditoria estática", ["auditoria.py", os.path.join(RAIZ, "saida", "Famosos.bcm"),
                               os.path.join(RAIZ, "saida", "Filmes.bcm")], AQUI)
    run("Regressões das recomendações", ["test_recomendacoes.py"], AQUI)
    run("Apêndices do relatório", ["gerar_apendices.py"], AQUI)
    if "--avaliar" in sys.argv:
        run("Avaliação quantitativa (simulador)", ["avaliacao.py", "2000"], AQUI)
        run("Registro da validação atual", ["registrar_validacao.py"], AQUI)
    print("\nTUDO OK. Bases em:", os.path.join(RAIZ, "saida"))


if __name__ == "__main__":
    main()
