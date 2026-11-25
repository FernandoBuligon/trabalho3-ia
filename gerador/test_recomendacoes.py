"""Regressões das bases finais: limite exato, exceções e codireção.

Executar depois de build.py. Os testes usam os .bcm entregáveis, não regras
reimplementadas. Saída detalhada em testes/regressao_recomendacoes.json.
"""
import hashlib
import json
from pathlib import Path

import avaliacao
import bcm
from simulador import Motor

RAIZ = Path(__file__).resolve().parent.parent


def main():
    path = RAIZ / "saida/Filmes.bcm"
    motor = Motor(bcm.read_bcm(path.read_bytes()))
    rows = avaliacao.ler_csv("filmes.csv")
    duracoes = {r["titulo"]: int(r["duracao"]) for r in rows}
    testes = []

    def consultar(nome, respostas, esperado=None, ausente=None, regra_esperada=None):
        resultado = motor.consultar(respostas)
        rec = dict(resultado.objetivos["filme recomendado"])
        limite = respostas.get("tempo disponível")
        if respostas.get("tem limite de tempo") == "Sim" and limite is not None:
            excessos = [t for t in rec if t in duracoes and duracoes[t] > limite]
            assert not excessos, (nome, limite, excessos)
        assert esperado is None or esperado in rec, (nome, esperado, rec)
        assert ausente is None or ausente not in rec, (nome, ausente, rec)
        assert regra_esperada is None or regra_esperada in resultado.regras_disparadas, (nome, regra_esperada)
        testes.append({"caso": nome, "resultado": "OK"})

    for row in rows:
        titulo, minutos = row["titulo"], int(row["duracao"])
        respostas = avaliacao.perfil_filme(row)
        # Todas as pistas fortes, para detectar qualquer caminho que burle o tempo.
        respostas["ator preferido"] = avaliacao.L(row["atores"])
        respostas["diretor preferido"] = avaliacao.L(row["diretor"])
        for delta in (-1, 0):
            respostas["tempo disponível"] = minutos + delta
            consultar(f"{titulo}: duração {delta:+d}", respostas,
                      esperado=titulo if delta == 0 else None,
                      ausente=titulo if delta == -1 else None)
        for flag, tempo in [("Não", 60), (None, None), ("Sim", None)]:
            respostas.update({"tem limite de tempo": flag, "tempo disponível": tempo})
            consultar(f"{titulo}: sem limite efetivo {flag}", respostas, esperado=titulo)
        for diretor in avaliacao.L(row["diretor"]):
            respostas = {"há menores assistindo": "Não", "tem limite de tempo": "Não",
                         "quer escolher diretor": "Sim", "diretor preferido": [diretor]}
            consultar(f"{titulo}: diretor {diretor}", respostas, esperado=titulo,
                      regra_esperada=f"{titulo} - diretor: {diretor}")

    caso = json.loads((RAIZ / "testes/gui/filmes_2/simulador.json").read_text())
    consultar("regressão filmes_2: criança, 100 minutos", caso["respostas"],
              esperado="Procurando Nemo", ausente="A Viagem de Chihiro")
    result = {"base_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "consultas": len(testes), "falhas": 0, "casos": testes}
    (RAIZ / "testes/regressao_recomendacoes.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"OK: {len(testes)} consultas; limites exatos, fallbacks e diretores individuais.")


if __name__ == "__main__":
    main()
