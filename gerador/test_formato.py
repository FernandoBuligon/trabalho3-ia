"""
Etapa 3: validação do leitor/escritor .BCM.

1. Round-trip byte a byte de todas as bases .BCM de exemplo do SINTA.
2. Base sintética com todos os recursos -> escrita -> leitura -> comparação.
3. (manual/automatizado via GUI) comparação com o arquivo regravado pelo próprio
   ExSINTA: `python test_formato.py --comparar TESTE.BCM TESTE_SINTA.BCM`
"""
import glob
import os
import sys

import bcm
from kb import KB, SIM, NAO, DESCONHECIDO

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)


def base_sintetica() -> KB:
    kb = KB("Base de Teste do Gerador", autores="Gerador Python",
            abertura=["Base sintética para validar o formato .BCM.",
                      "Acentuação: ação, ênfase, coração, pêssego."])
    kb.var("gosta de ação")  # lógica Sim/Não
    kb.var("gênero", ["ação", "comédia", "drama", "terror"])
    kb.var("ano", numeric=True)
    kb.var("duração", numeric=True)
    kb.var("perfil", ["aventureiro", "sensível", "corajoso"], multi=True)
    kb.var("filme", ["Filme A", "Filme B", "Filme C"], multi=True)
    kb.rule("Perfil aventureiro", [("gosta de ação", "=", SIM), "E", ("gênero", "=", "ação")],
            [("perfil", "aventureiro", 90)])
    kb.rule("Perfil sensível", [("gênero", "=", "drama"), "OU", ("gênero", "=", "comédia")],
            [("perfil", "sensível", 80)])
    kb.rule("Perfil corajoso", [("gênero", "=", "terror"), "E", ("gosta de ação", "=", NAO, True)],
            [("perfil", "corajoso", 75), ("perfil", "aventureiro", 40)])
    kb.rule("Filme A", [("perfil", "=", "aventureiro"), "E", ("ano", ">=", 2000),
                        "E", ("duração", "<", 130)], [("filme", "Filme A", 95)])
    kb.rule("Filme B", [("perfil", "=", "sensível"), "E", ("ano", "<", 2000)],
            [("filme", "Filme B", 85)])
    kb.rule("Filme C", [("perfil", "=", "corajoso"), "OU", ("gênero", "=", DESCONHECIDO)],
            [("filme", "Filme C", 60.5)])
    kb.rule("Filme A genérico", [("gênero", "<>", "terror")], [("filme", "Filme A", 30)])
    kb.question("gosta de ação", "Você gosta de cenas de ação?", ["Para traçar seu perfil."], False)
    kb.question("gênero", "Qual gênero você prefere?", ["Gênero é o principal critério.",
                                                         "Segunda linha do porquê."])
    kb.question("ano", "A partir de que ano o filme deve ser?", [])
    kb.question("duração", "Duração máxima desejada (minutos)?", ["Em minutos."])
    kb.target("perfil", mostrar=False)
    kb.target("filme")
    return kb


def semantica(b: bcm.Base):
    """Representação canônica independente de códigos e ordem de gravação."""
    V = {v.code: v for v in b.vars}
    VAL = {v.code: v for v in b.values}
    F = {f.code: f for f in b.formulas}

    def val(vc, c):
        if c in (bcm.VAL_UNKNOWN, bcm.VAL_YES, bcm.VAL_NO):
            return {-1: "DESCONHECIDO", -2: "Sim", -3: "Não"}[c]
        return ("F:" + F[c].formula.text) if V[vc].numeric else VAL[c].name.text

    vars_ = sorted((v.name.text, v.multi, v.numeric,
                    tuple(x.name.text for x in sorted((x for x in b.values if x.var_code == v.code),
                                                      key=lambda x: x.position)))
                   for v in b.vars)
    rules = []
    for r in sorted(b.rules, key=lambda r: r.position):
        tails = tuple((V[t.var_code].name.text, t.operator.text, val(t.var_code, t.val_code),
                       t.conect, t.neg) for t in b.tails if t.code == r.code)
        heads = tuple((V[h.var_code].name.text, val(h.var_code, h.val_code), round(h.cnf * 100, 3))
                      for h in b.heads if h.code == r.code)
        rules.append((r.name.text, tails, heads))
    qs = sorted((V[q.code].name.text, q.question.text, tuple(w.text for w in q.why), q.use_cnf)
                for q in b.questions)
    tg = [(V[t.code].name.text, t.show_results) for t in b.targets]
    info = (b.name.text, b.authors.text, tuple(x.text for x in b.overture), b.show_intro,
            b.priority, round(b.min_value, 4), b.examine_all, b.use_password)
    return {"info": info, "vars": vars_, "rules": rules, "questions": qs, "targets": tg}


def comparar(a: bcm.Base, b: bcm.Base) -> bool:
    sa, sb = semantica(a), semantica(b)
    ok = True
    for k in sa:
        if sa[k] != sb[k]:
            ok = False
            print(f"  DIFERENÇA em {k}:")
            print("    A:", sa[k])
            print("    B:", sb[k])
    return ok


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) == 4 and sys.argv[1] == "--comparar":
        a = bcm.read_bcm(open(sys.argv[2], "rb").read())
        b = bcm.read_bcm(open(sys.argv[3], "rb").read())
        ok = comparar(a, b)
        print("SEMÂNTICA IDÊNTICA" if ok else "DIFERENTE")
        sys.exit(0 if ok else 1)

    falhas = 0
    print("1) Round-trip das bases de exemplo")
    for f in sorted(set(glob.glob(os.path.join(RAIZ, "sinta", "**", "*.BCM"), recursive=True))):
        d = open(f, "rb").read()
        b = bcm.read_bcm(d)
        ok = bcm.write_bcm(b) == d
        falhas += not ok
        print(f"   {'OK ' if ok else 'ERRO'} {os.path.relpath(f, RAIZ)} "
              f"({len(b.rules)} regras, {len(b.vars)} variáveis)")

    print("2) Real48")
    for x in [0, 0.5, 1, 0.3, 0.605, 0.9, 100, 2024, 123.25, -7.5]:
        y = bcm.real48_decode(bcm.real48_encode(x))
        ok = abs(x - y) < 1e-9
        falhas += not ok
        print(f"   {'OK ' if ok else 'ERRO'} {x} -> {y}")

    print("3) Base sintética")
    kb = base_sintetica()
    dados = kb.compile()
    b1 = kb.to_base()
    b2 = bcm.read_bcm(dados)
    ok = bcm.write_bcm(b2) == dados and comparar(b1, b2)
    falhas += not ok
    print(f"   {'OK ' if ok else 'ERRO'} escrever -> ler -> reescrever ({len(dados)} bytes)")
    saida = os.path.join(RAIZ, "testes", "TESTE.BCM")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    open(saida, "wb").write(dados)
    print(f"   gravado: {saida}")
    print()
    print("RESULTADO:", "TUDO OK" if falhas == 0 else f"{falhas} FALHA(S)")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
