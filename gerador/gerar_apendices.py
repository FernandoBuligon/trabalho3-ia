"""
Gera os apêndices do relatório (Markdown) diretamente das bases .BCM geradas:
variáveis, perguntas, objetivos, contagem de regras por tipo e exemplos de regras.

    python gerar_apendices.py
"""
import json
import os
import sys

import bcm

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)


def regra_md(b, rule):
    V = {v.code: v for v in b.vars}
    VAL = {v.code: v for v in b.values}
    F = {f.code: f.formula.text for f in b.formulas}

    def val(vc, c):
        if c == bcm.VAL_UNKNOWN:
            return "DESCONHECIDO"
        if c == bcm.VAL_YES:
            return "Sim"
        if c == bcm.VAL_NO:
            return "Não"
        return F[c] if V[vc].numeric else VAL[c].name.text

    L = [f"REGRA {rule.position}: {rule.name.text}"]
    prev = "SE"
    for t in (x for x in b.tails if x.code == rule.code):
        L.append(f"  {prev:5} {V[t.var_code].name.text} {t.operator.text} {val(t.var_code, t.val_code)}")
        prev = {0: "E", 1: "OU", 2: "ENTÃO"}[t.conect]
    for i, h in enumerate(x for x in b.heads if x.code == rule.code):
        L.append(f"  {'ENTÃO' if i == 0 else 'E':5} {V[h.var_code].name.text} = "
                 f"{val(h.var_code, h.val_code)} CNF {h.cnf * 100:.0f}%")
    return "\n".join(L)


def apendice(nome_arq, titulo, exemplos):
    path = os.path.join(RAIZ, "saida", nome_arq + ".bcm")
    b = bcm.read_bcm(open(path, "rb").read())
    st = json.load(open(os.path.join(RAIZ, "saida", nome_arq + ".json"), encoding="utf-8"))
    V = {v.code: v for v in b.vars}
    q = {x.code: x for x in b.questions}
    concl = {h.var_code for h in b.heads}
    tgt = {t.code: t for t in b.targets}
    out = [f"# Apêndice: {titulo}", "",
           f"> Gerado automaticamente a partir de `saida/{nome_arq}.bcm` por `gerador/gerar_apendices.py`.", "",
           "## Números da base", "",
           "| Item | Quantidade |", "|---|---|",
           f"| Regras | {st['regras']} |", f"| Premissas (caudas) | {st['premissas']} |",
           f"| Conclusões (cabeças) | {st['conclusoes']} |", f"| Variáveis | {st['variaveis']} |",
           f"| Valores | {st['valores']} |", f"| Perguntas | {st['perguntas']} |",
           f"| Objetivos | {st['objetivos']} |", f"| Itens na base de dados | {st['itens']} |",
           f"| Tamanho do arquivo .BCM | {st['bytes'] / 1024:.0f} KB |", "",
           "## Regras por tipo", "", "| Tipo | Regras |", "|---|---|"]
    for k, n in st["regras_por_tipo"].items():
        out.append(f"| {k} | {n} |")
    out += ["", "## Objetivos (ordem de busca)", "", "| # | Variável | Exibe resultado? |", "|---|---|---|"]
    for i, t in enumerate(b.targets, 1):
        out.append(f"| {i} | {V[t.code].name.text} | {'sim' if t.show_results else 'não (fixa a ordem das perguntas)'} |")
    out += ["", "## Variáveis", "",
            "| Variável | Tipo | Papel | Valores |", "|---|---|---|---|"]
    vals = {}
    for x in sorted(b.values, key=lambda x: x.position):
        vals.setdefault(x.var_code, []).append(x.name.text)
    for v in b.vars:
        tipo = "numérica" if v.numeric else ("multivalorada" if v.multi else "univalorada")
        if not v.numeric and v.code not in vals:
            tipo = "lógica (Sim/Não)"
        papel = ("objetivo" if v.code in tgt and tgt[v.code].show_results
                 else "pergunta" if v.code in q else "intermediária (inferida)" if v.code in concl else "?")
        vs = vals.get(v.code, [])
        if v.numeric:
            txt = f"faixa {vs[0]}" if vs else "-"
        elif len(vs) > 14:
            txt = "; ".join(vs[:8]) + f"; … ({len(vs)} valores)"
        else:
            txt = "; ".join(vs) if vs else "Sim; Não"
        out.append(f"| {v.name.text} | {tipo} | {papel} | {txt} |")
    out += ["", "## Perguntas e explicações (\"Por quê?\")", ""]
    for x in b.questions:
        out.append(f"- **{V[x.code].name.text}**: \"{x.question.text}\"")
        for w in x.why:
            out.append(f"  - *por quê:* {w.text}")
    out += ["", "## Exemplos de regras (como aparecem no SINTA)", ""]
    pos = {r.name.text: r for r in b.rules}
    for nome in exemplos:
        out += ["```", regra_md(b, pos[nome]), "```", ""]
    dest = os.path.join(RAIZ, "relatorio", f"apendice_{nome_arq.lower()}.md")
    open(dest, "w", encoding="utf-8").write("\n".join(out))
    print("gerado:", dest)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    apendice("Famosos", "Sistema 1, Quem é o Famoso?", [
        "categoria compatível: grupo pessoa real (qualquer área)",
        "categoria compatível: indiferente",
        "faixa de altura: 161 a 170 cm",
        "estatura compatível: 161 a 170 cm",
        "estatura compatível: altura em branco",
        "Wagner Moura - perfil completo",
        "Wagner Moura - cabelo e olhos",
        "Wagner Moura - área (atuação)",
        "Wagner Moura - obra: Tropa de Elite",
        "Naruto - perfil completo",
        "Rita Lee - traço marcante: óculos",
    ])
    apendice("Filmes", "Sistema 2, Que Filme Eu Vejo?", [
        "faixa do mais novo: 12 ou 13 anos",
        "classificação: 12 ou 13 anos",
        "classificação: idade não informada",
        "duração: 130 a 159 min",
        "ocasião: em casal",
        "perfil: adrenalina (ação)",
        "perfil: fantasia e ficção",
        "época compatível: grupo recentes (de 2010 em diante)",
        "A Origem - perfil completo",
        "A Origem - gênero e clima",
        "Parasita - grande premiado",
        "A Origem - gênero em comum: ficção científica",
        "A Origem - ator: Leonardo DiCaprio",
        "A Origem - diretor: Christopher Nolan",
        "Central do Brasil - origem e gênero",
    ])
