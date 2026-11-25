"""Registra hashes e consultas do simulador sem atribuí-los à interface real."""
import hashlib
import json
from pathlib import Path

import bcm
from casos_gui import CASOS
from simulador import simular
from test_formato import semantica

RAIZ = Path(__file__).resolve().parent.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    destino = RAIZ / "testes/revisao"
    destino.mkdir(exist_ok=True)
    registro = {"ambiente": "simulador Python; não é execução do ExSINTA",
                "bases": {}, "casos": {}}
    for nome in ("Famosos", "Filmes"):
        atual = RAIZ / f"saida/{nome}.bcm"
        antiga = RAIZ / f"testes/sinta_regravado/{nome.upper()}_SINTA.BCM"
        a = bcm.read_bcm(atual.read_bytes())
        b = bcm.read_bcm(antiga.read_bytes())
        registro["bases"][nome] = {
            "sha256": sha(atual), "regras": len(a.rules),
            "regravacao_historica_sha256": sha(antiga),
            "regras_regravacao_historica": len(b.rules),
            "semantica_igual_a_regravacao_historica": semantica(a) == semantica(b),
        }
    for nome, (path, respostas) in CASOS.items():
        base = Path(path)
        resultado = simular(bcm.read_bcm(base.read_bytes()), respostas)
        dados = {"origem": "simulador Python", "base_sha256": sha(base),
                 "respostas": respostas, "perguntas": resultado.perguntas,
                 "objetivos": resultado.objetivos}
        (destino / f"{nome}.json").write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n")
        registro["casos"][nome] = {"arquivo": f"{nome}.json", "perguntas": len(resultado.perguntas)}
    registro["artefatos_sha256"] = {
        str(p.relative_to(RAIZ)): sha(p)
        for p in [RAIZ / "testes/avaliacao.json", RAIZ / "testes/regressao_recomendacoes.json",
                  RAIZ / "dados/famosos.csv", RAIZ / "dados/filmes.csv", RAIZ / "dados/fontes.csv"]
    }
    (destino / "manifesto.json").write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n")
    print("Manifesto e 8 consultas atuais do simulador gravados em testes/revisao/.")


if __name__ == "__main__":
    main()
