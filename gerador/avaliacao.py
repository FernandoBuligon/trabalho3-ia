"""
Etapa 9: avaliação quantitativa das bases com o simulador (fiel ao ExSINTA).

  1. Autorreconhecimento: um "usuário perfeito" descreve cada item a partir dos
     dados; mede-se a posição do item no ranking (top-1, top-3, top-5), com e
     sem a evidência mais forte (obra / ator / diretor).
  2. Robustez: N consultas aleatórias (inclui CNFs fracionários e respostas em
     branco): falhas do motor, consultas sem recomendação, nº de perguntas,
     tamanho das listas e cobertura de regras (regras que nunca disparam).
  3. Segurança (filmes): nenhum filme acima da classificação permitida.

    python avaliacao.py [N_aleatorias]
"""
import csv
import json
import os
import random
import statistics
import sys
from collections import Counter

import bcm
import simulador

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
SAIDA = os.path.join(RAIZ, "saida")
DADOS = os.path.join(RAIZ, "dados")

ALTURA_TIPICA = {"baixa": 158, "média": 174, "alta": 190}
ORDEM_CLASSIF = ["L", "10", "12", "14", "16", "18"]
OBRA_VAR = {"ator/atriz": ("obras_atuacao", "obra: filme, série ou novela"),
            "cantor(a)": ("obras_musica", "obra: música ou álbum"),
            "atleta": ("obras_esporte", "obra: time ou competição"),
            "personagem fictício": ("franquia", "obra: franquia ou universo"),
            "apresentador(a)/influenciador(a)": ("programas", "obra: programa ou canal")}
AREA_VAR = {"ator/atriz": ("genero_atuacao", "gênero de atuação preferido"),
            "cantor(a)": ("genero_musical", "gênero musical preferido"),
            "atleta": ("esporte", "esporte preferido"),
            "personagem fictício": ("midia", "mídia preferida"),
            "apresentador(a)/influenciador(a)": ("formato", "formato preferido")}


def ler_csv(nome):
    return list(csv.DictReader(open(os.path.join(DADOS, nome), encoding="utf-8-sig")))


def L(s):
    return [x for x in (s or "").split("|") if x]


def era(ano):
    a = int(ano)
    return ("clássico (até 1979)" if a <= 1979 else "anos 80" if a < 1990 else "anos 90" if a < 2000
            else "anos 2000" if a < 2010 else "anos 2010" if a < 2020 else "anos 2020")


# ----------------------------------------------------------------------------
def perfil_famoso(r, com_obra=True):
    cat = L(r["categoria"])[0]
    resp = {
        "categoria preferida": [cat], "sexo preferido": r["sexo"],
        "faixa etária preferida": [r["faixa_etaria"]],
        "cabelo preferido": [r["cabelo"]] if r["cabelo"] else ["indiferente"],
        "olhos preferidos": [r["olhos"]] if r["olhos"] else ["indiferente"],
        "sabe a altura": "Sim" if r["estatura"] else "Não",
        "origem preferida": [r["origem"]], "época preferida": L(r["epoca"]),
        "espécie preferida": [r["especie"]],
        "traços marcantes": L(r["tracos"]) or ["nenhum em especial"],
        "quer citar uma obra": "Sim" if com_obra else "Não",
    }
    if r["estatura"]:
        resp["altura aproximada"] = ALTURA_TIPICA[r["estatura"]]
    col, var = AREA_VAR[cat]
    resp[var] = L(r[col])
    col, var = OBRA_VAR[cat]
    if com_obra:
        resp[var] = L(r[col])[:1]
    return resp


def perfil_filme(r, com_pessoas=True):
    menor = r["classificacao"] != "18"
    idade = {"L": 8, "10": 10, "12": 12, "14": 14, "16": 16}.get(r["classificacao"])
    resp = {
        "há menores assistindo": "Sim" if menor else "Não",
        "gênero preferido": L(r["generos"]), "clima desejado": L(r["clima"]),
        "tem limite de tempo": "Sim", "tempo disponível": int(r["duracao"]) + 10,
        "origem preferida": r["origem"], "época preferida": [era(r["ano"])],
        "tipo de história preferido": "baseada em fatos reais" if r["fatos_reais"] == "sim" else "ficção",
        "companhia": "sozinho(a)", "quer premiados": "Sim" if r["premios"] else "Não",
        "interesse em franquias": "gosto de sagas e franquias" if r["franquia"] else "prefiro filmes únicos",
        "quer escolher ator": "Sim" if (com_pessoas and r["atores"]) else "Não",
        "quer escolher diretor": "Sim" if com_pessoas else "Não",
    }
    if idade is not None:
        resp["idade do mais novo"] = idade
    if com_pessoas:
        if r["atores"]:
            resp["ator preferido"] = L(r["atores"])[:1]
        resp["diretor preferido"] = [r["diretor"]]
    return resp


def posicao(lista, nome):
    """Posição (1 = melhor) considerando empates: posição = 1 + nº de itens com CNF maior."""
    d = dict(lista)
    if nome not in d:
        return None
    return 1 + sum(1 for _, c in lista if c > d[nome] + 1e-9)


def autorreconhecimento(base, linhas, chave, alvo, fperfil, variantes):
    out = {}
    for rot, kw in variantes.items():
        pos, empates, piores = [], [], []
        for r in linhas:
            res = simulador.simular(base, fperfil(r, **kw))
            lst = res.objetivos[alvo]
            p = posicao(lst, r[chave])
            pos.append(p if p is not None else 999)
            if p == 1:
                top = lst[0][1]
                empates.append(sum(1 for _, c in lst if abs(c - top) < 1e-9))
            if p is None or p > 3:
                piores.append((r[chave], p))
        n = len(pos)
        out[rot] = {
            "top1": sum(p == 1 for p in pos) / n, "top3": sum(p <= 3 for p in pos) / n,
            "top5": sum(p <= 5 for p in pos) / n, "posicao_media": statistics.mean(min(p, 50) for p in pos),
            "empatados_no_topo_media": statistics.mean(empates) if empates else 0,
            "fora_do_top3": piores,
        }
    return out


# ----------------------------------------------------------------------------
def resposta_aleatoria(base, rnd: random.Random):
    """Gera respostas aleatórias para TODAS as perguntas (as não feitas são ignoradas)."""
    resp = {}
    vals = {}
    for x in base.values:
        vals.setdefault(x.var_code, []).append(x.name.text)
    for q in base.questions:
        v = next(vv for vv in base.vars if vv.code == q.code)
        nome = v.name.text
        if rnd.random() < 0.08:
            resp[nome] = None                      # deixa em branco
            continue
        if v.numeric:
            faixa = vals.get(v.code, ["0;300"])[0].split(";")
            resp[nome] = rnd.randint(int(faixa[0]), int(faixa[1]))
            continue
        opts = vals.get(v.code)
        if not opts:
            resp[nome] = rnd.choice(["Sim", "Não"])
            continue
        k = 1 if not v.multi else rnd.choice([1, 1, 2, 2, 3])
        escolha = rnd.sample(opts, min(k, len(opts)))
        if rnd.random() < 0.3:                     # CNFs fracionários
            resp[nome] = [(e, rnd.choice([60, 70, 80, 90])) for e in escolha]
        else:
            resp[nome] = escolha
    return resp


def robustez(base, alvo, n, seed):
    rnd = random.Random(seed)
    motor = simulador.Motor(base)
    falhas, vazias, tamanhos, nperg = 0, 0, [], []
    disparadas = Counter()
    for _ in range(n):
        resp = resposta_aleatoria(base, rnd)
        try:
            res = motor.consultar(resp)
        except simulador._Abort:
            falhas += 1
            continue
        lst = [x for x in res.objetivos[alvo] if x[0] != "DESCONHECIDO"]
        if not lst:
            vazias += 1
        tamanhos.append(len(lst))
        nperg.append(len(res.perguntas))
        disparadas.update(res.regras_disparadas)
    nunca = [r.name.text for r in base.rules if disparadas[r.name.text] == 0]
    return {
        "consultas": n, "falhas_do_motor": falhas, "sem_recomendacao": vazias,
        "tamanho_lista_mediana": statistics.median(tamanhos), "tamanho_lista_media": statistics.mean(tamanhos),
        "perguntas_media": statistics.mean(nperg), "perguntas_min": min(nperg), "perguntas_max": max(nperg),
        "regras_total": len(base.rules), "regras_nunca_disparadas": len(nunca),
        "exemplos_nunca_disparadas": nunca[:15],
    }


def alcancabilidade(base, linhas, fperfil, extras):
    """Consultas dirigidas: para cada item, um usuário que marca TODAS as
    evidências do item (todos os atores/obras/traços). Junta as regras que
    dispararam e informa quais nunca disparam (devem ser zero)."""
    motor = simulador.Motor(base)
    disparadas = set()
    for r in linhas:
        for variante in extras(r):
            res = motor.consultar(fperfil(r, variante))
            disparadas.update(res.regras_disparadas)
    nunca = [x.name.text for x in base.rules if x.name.text not in disparadas]
    return {"regras_total": len(base.rules), "nunca_disparadas": nunca}


def _var_famoso(r, todas):
    resp = perfil_famoso(r, com_obra=True)
    for cat in L(r["categoria"]):            # todas as categorias e obras do item
        col, var = OBRA_VAR[cat]
        resp[var] = L(r[col])
        col, var = AREA_VAR[cat]
        resp[var] = L(r[col])
    resp["categoria preferida"] = L(r["categoria"]) if todas else resp["categoria preferida"]
    return resp


def _var_filme(r, variante):
    resp = perfil_filme(r, com_pessoas=True)
    if r["atores"]:
        resp["ator preferido"] = L(r["atores"])
    resp["companhia"] = variante
    return resp


def seguranca_filmes(base, linhas, n, seed):
    rnd = random.Random(seed)
    classif = {r["titulo"]: r["classificacao"] for r in linhas}
    motor = simulador.Motor(base)
    violacoes = 0
    for _ in range(n):
        resp = resposta_aleatoria(base, rnd)
        resp["há menores assistindo"] = "Sim"
        idade = rnd.randint(3, 17)
        resp["idade do mais novo"] = idade
        lim = "L" if idade < 10 else "10" if idade < 12 else "12" if idade < 14 else "14" if idade < 16 else "16"
        res = motor.consultar(resp)
        for t, _ in res.objetivos["filme recomendado"]:
            if t != "DESCONHECIDO" and ORDEM_CLASSIF.index(classif[t]) > ORDEM_CLASSIF.index(lim):
                violacoes += 1
    return {"consultas_com_menores": n, "violacoes_de_classificacao": violacoes}


# ----------------------------------------------------------------------------
def main():
    sys.stdout.reconfigure(encoding="utf-8")
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    rel = {}
    fam = bcm.read_bcm(open(os.path.join(SAIDA, "Famosos.bcm"), "rb").read())
    fil = bcm.read_bcm(open(os.path.join(SAIDA, "Filmes.bcm"), "rb").read())
    lf, lm = ler_csv("famosos.csv"), ler_csv("filmes.csv")

    rel["famosos"] = {
        "autorreconhecimento": autorreconhecimento(fam, lf, "nome", "famoso recomendado", perfil_famoso,
                                                   {"com obra": {"com_obra": True},
                                                    "sem obra (só aparência e área)": {"com_obra": False}}),
        "robustez": robustez(fam, "famoso recomendado", n, 1),
        "alcancabilidade": alcancabilidade(fam, lf, _var_famoso, lambda r: [True]),
    }
    rel["filmes"] = {
        "autorreconhecimento": autorreconhecimento(fil, lm, "titulo", "filme recomendado", perfil_filme,
                                                   {"com ator e diretor": {"com_pessoas": True},
                                                    "sem ator e diretor": {"com_pessoas": False}}),
        "robustez": robustez(fil, "filme recomendado", n, 2),
        "alcancabilidade": alcancabilidade(fil, lm, _var_filme,
                                           lambda r: ["sozinho(a)", "em casal", "com amigos", "com a família"]),
        "seguranca": seguranca_filmes(fil, lm, n // 2, 3),
    }
    os.makedirs(os.path.join(RAIZ, "testes"), exist_ok=True)
    json.dump(rel, open(os.path.join(RAIZ, "testes", "avaliacao.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for sist, d in rel.items():
        print(f"===== {sist.upper()}")
        for var, a in d["autorreconhecimento"].items():
            print(f"  autorreconhecimento [{var}]: top1 {a['top1']:.0%}  top3 {a['top3']:.0%}  "
                  f"top5 {a['top5']:.0%}  posição média {a['posicao_media']:.2f}  "
                  f"empatados no topo (média) {a['empatados_no_topo_media']:.1f}")
            if a["fora_do_top3"]:
                print(f"     fora do top-3: {a['fora_do_top3'][:12]}")
        r = d["robustez"]
        print(f"  robustez: {r['consultas']} consultas, falhas do motor {r['falhas_do_motor']}, "
              f"sem recomendação {r['sem_recomendacao']}, lista mediana {r['tamanho_lista_mediana']}, "
              f"perguntas média {r['perguntas_media']:.1f} ({r['perguntas_min']}-{r['perguntas_max']})")
        print(f"  cobertura: {r['regras_total'] - r['regras_nunca_disparadas']}/{r['regras_total']} regras "
              f"dispararam; nunca: {r['regras_nunca_disparadas']} ex.: {r['exemplos_nunca_disparadas'][:6]}")
        a = d["alcancabilidade"]
        rr = set(r["exemplos_nunca_disparadas"]) if r["regras_nunca_disparadas"] <= 15 else None
        print(f"  alcançabilidade dirigida: {a['regras_total'] - len(a['nunca_disparadas'])}/{a['regras_total']} "
              f"regras dispararam nas consultas dirigidas")
        if rr is not None:
            resto = [x for x in rr if x in a["nunca_disparadas"]]
            print(f"  regras não disparadas em NENHUM teste (aleatório + dirigido): {len(resto)} {resto[:8]}")
        if "seguranca" in d:
            s = d["seguranca"]
            print(f"  segurança: {s['consultas_com_menores']} consultas com menores, "
                  f"violações de classificação: {s['violacoes_de_classificacao']}")


if __name__ == "__main__":
    main()
