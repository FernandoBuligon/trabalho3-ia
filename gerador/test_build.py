"""Etapa 4: testes do gerador (DSL, validação de dados, regras geradas, inferência)."""
import os
import sys

import bcm
import build
import simulador
from kb import KB, KBError

AQUI = os.path.dirname(os.path.abspath(__file__))
falhas = 0


def check(nome, cond, extra=""):
    global falhas
    print(f"  {'OK ' if cond else 'ERRO'} {nome} {extra}")
    falhas += not cond


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("1) DSL")
    check("premissas e conectivos",
          build.parse_cond("a = x OU a = y E b >= 10") ==
          [("a", "=", "x"), "OU", ("a", "=", "y"), "E", ("b", ">=", "10")])
    check("conclusão com CNF", build.parse_concl("filme = Toy Story CNF 80") == ("filme", "Toy Story", 80.0))
    check("conclusão sem CNF", build.parse_concl("x = y") == ("x", "y", 100.0))
    check("operador <>", build.parse_cond("a <> b") == [("a", "<>", "b")])
    try:
        build.parse_cond("a b c")
        check("premissa inválida rejeitada", False)
    except KBError:
        check("premissa inválida rejeitada", True)

    # o texto vira número só em variáveis numéricas; categorias ficam como estão
    k = KB("t")
    k.var("classe", ["010", "2.0"])
    k.var("n", numeric=True)
    k.var("r", ["sim"])
    k.rule("r1", build.parse_cond("classe = 010 E n >= 1,5"), [build.parse_concl("r = sim")])
    k.rule("r2", build.parse_cond("classe = 2.0 E n >= 148"), [build.parse_concl("r = sim")])
    check("categoria numérica mantida como texto",
          [p[2] for p in k.rules[0].premises] == ["010", 1.5]
          and [p[2] for p in k.rules[1].premises] == ["2.0", 148], str([r.premises for r in k.rules]))

    print("2) Geração da base de exemplo")
    out = build.main(os.path.join(AQUI, "exemplo", "mini.yaml"))
    base = bcm.read_bcm(open(out, "rb").read())
    check("22 regras", len(base.rules) == 22, f"({len(base.rules)})")
    check("2 objetivos (1 oculto)", [t.show_results for t in base.targets] == [False, True])
    check("faixa numérica gravada", any(v.name.text == "60;240" for v in base.values))
    # toda regra termina em premissa simples
    ult_ou = 0
    for r in base.rules:
        ts = [t for t in base.tails if t.code == r.code]
        if len(ts) >= 2 and ts[-2].conect == bcm.CN_OR:
            ult_ou += 1
    check("nenhuma regra termina com OU", ult_ou == 0)

    print("3) Inferência (simulador)")
    adultos_comedia = {"com crianças": "Não", "gênero preferido": ["comédia"], "tempo disponível": 150,
                       "origem preferida": ["indiferente"], "quer escolher ator": "Não"}
    r = simulador.simular(base, adultos_comedia)
    rec = dict(r.objetivos["filme recomendado"])
    check("comédias recomendadas", set(rec) == {"O Auto da Compadecida", "Forrest Gump", "Toy Story"}, str(rec))
    check("CNF 95 ⊕ 60 = 98", all(abs(c - 98.0) < 0.01 for c in rec.values()))
    # encadeamento para trás: a 1a regra de filme falha no gênero, então "origem" só é
    # perguntada depois da regra de ator (comportamento confirmado no ExSINTA real)
    check("ordem das perguntas (backward chaining)",
          r.perguntas == ["com crianças", "gênero preferido", "quer escolher ator",
                          "origem preferida", "tempo disponível"], str(r.perguntas))

    r = simulador.simular(base, dict(adultos_comedia, **{"com crianças": "Sim"}))
    rec = dict(r.objetivos["filme recomendado"])
    check("com crianças -> só classificação L", set(rec) == {"Toy Story"}, str(rec))

    r = simulador.simular(base, {"com crianças": "Não", "gênero preferido": ["crime"], "tempo disponível": 90,
                                 "origem preferida": ["nacional"], "quer escolher ator": "Sim",
                                 "ator preferido": ["Tom Hanks"]})
    rec = dict(r.objetivos["filme recomendado"])
    check("pouco tempo: crime sem perfil completo (só 60%)",
          abs(rec.get("Cidade de Deus", 0) - 60) < 0.01 and abs(rec.get("Tropa de Elite", 0) - 60) < 0.01, str(rec))
    check("ator Tom Hanks soma evidência", abs(rec.get("Toy Story", 0) - 70) < 0.01
          and abs(rec.get("Forrest Gump", 0) - 70) < 0.01)
    check("ator só perguntado se quer escolher", "ator preferido" in r.perguntas)
    r2 = simulador.simular(base, adultos_comedia)
    check("ator NÃO perguntado se não quer", "ator preferido" not in r2.perguntas)

    r = simulador.simular(base, {"com crianças": "Não", "gênero preferido": None, "tempo disponível": None,
                                 "origem preferida": None, "quer escolher ator": None})
    check("tudo DESCONHECIDO não gera erro", r.objetivos["filme recomendado"] == [("DESCONHECIDO", 100.0)],
          str(r.objetivos))

    print("4) Validação de dados")
    import yaml, tempfile, shutil
    tmp = tempfile.mkdtemp()
    shutil.copy(os.path.join(AQUI, "exemplo", "mini.csv"), tmp)
    cfg = yaml.safe_load(open(os.path.join(AQUI, "exemplo", "mini.yaml"), encoding="utf-8"))
    cfg["base"]["arquivo_saida"] = "x.bcm"
    csv_txt = open(os.path.join(tmp, "mini.csv"), encoding="utf-8").read().replace("crime|drama", "crime|faroeste")
    open(os.path.join(tmp, "mini.csv"), "w", encoding="utf-8").write(csv_txt)
    yaml.safe_dump(cfg, open(os.path.join(tmp, "c.yaml"), "w", encoding="utf-8"), allow_unicode=True)
    try:
        build.Builder(os.path.join(tmp, "c.yaml")).build()
        check("valor inexistente no CSV é rejeitado", False)
    except KBError as e:
        check("valor inexistente no CSV é rejeitado", "faroeste" in str(e), f"({e})")
    shutil.rmtree(tmp)

    def montar(csv_troca=None, modelo_extra=None):
        tmp = tempfile.mkdtemp()
        csv_txt = open(os.path.join(AQUI, "exemplo", "mini.csv"), encoding="utf-8").read()
        if csv_troca:
            csv_txt = csv_txt.replace(*csv_troca)
        open(os.path.join(tmp, "mini.csv"), "w", encoding="utf-8").write(csv_txt)
        c = yaml.safe_load(open(os.path.join(AQUI, "exemplo", "mini.yaml"), encoding="utf-8"))
        c["base"]["arquivo_saida"] = "x.bcm"
        if modelo_extra:
            c["itens"]["modelos"].append(modelo_extra)
        yaml.safe_dump(c, open(os.path.join(tmp, "c.yaml"), "w", encoding="utf-8"), allow_unicode=True)
        try:
            b = build.Builder(os.path.join(tmp, "c.yaml"))
            b.build()
            return b, None
        except KBError as e:
            return None, e
        finally:
            shutil.rmtree(tmp)

    b, e = montar(("Cidade de Deus,2002,130,", "Cidade de Deus,2002,\"99,5\","))
    faixa = {it["titulo"]: it["faixa_duracao"] for it in b.items} if b else {}
    check("duração com vírgula decimal entre duas faixas", faixa.get("Cidade de Deus") == "curta", f"({e or faixa})")
    b, e = montar(("Cidade de Deus,2002,130,", "Cidade de Deus,2002,cento,"))
    check("duração não numérica acusa o item", e is not None and "Cidade de Deus" in str(e), f"({e})")
    _, e = montar(modelo_extra={"nome": "lista", "cnf": 50, "condicoes": [{"se": "ator preferido = {atores}"}]})
    check("coluna de lista em {coluna} é rejeitada", e is not None and "coluna de lista" in str(e), f"({e})")

    print()
    print("RESULTADO:", "TUDO OK" if falhas == 0 else f"{falhas} FALHA(S)")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
