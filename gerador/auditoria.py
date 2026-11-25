"""
Auditoria estática de uma base .BCM (independe da interface):

ERROS
  - variável usada em premissa sem pergunta e sem regra que a conclua
    (o SINTA faria a pergunta genérica "Qual o valor de x?")
  - objetivo sem nenhuma regra que o conclua
  - regra cuja última premissa está num grupo OU (pode quebrar o SINTA)
  - regra sem premissas ou sem conclusões; referência a código inexistente
  - valor de objetivo visível que nenhuma regra conclui (item inalcançável)
AVISOS
  - variável definida e nunca usada
  - pergunta cadastrada para variável que é concluída por regras (nunca será feita)
  - variável perguntada sem texto de "por quê"

    python auditoria.py ../saida/Filmes.bcm [...]
"""
import sys

import bcm


def auditar(path: str, verbose=True):
    b = bcm.read_bcm(open(path, "rb").read())
    V = {v.code: v for v in b.vars}
    vals_by_var = {}
    for x in b.values:
        vals_by_var.setdefault(x.var_code, set()).add(x.code)
    forms = {f.code for f in b.formulas}
    rules = {r.code: r for r in b.rules}
    tails, heads = {}, {}
    for t in b.tails:
        tails.setdefault(t.code, []).append(t)
    for h in b.heads:
        heads.setdefault(h.code, []).append(h)
    concluded = {h.var_code for h in b.heads}
    used_in_prem = {t.var_code for t in b.tails}
    questions = {q.code: q for q in b.questions}
    targets = [t.code for t in b.targets]
    erros, avisos = [], []

    def ok_val(var_code, val_code):
        if val_code in (bcm.VAL_UNKNOWN, bcm.VAL_YES, bcm.VAL_NO):
            return True
        if V[var_code].numeric:
            return val_code in forms
        return val_code in vals_by_var.get(var_code, set())

    for rc, r in rules.items():
        ts, hs = tails.get(rc, []), heads.get(rc, [])
        if not ts:
            erros.append(f"regra sem premissas: {r.name}")
        if not hs:
            erros.append(f"regra sem conclusões: {r.name}")
        if len(ts) >= 2 and ts[-2].conect == bcm.CN_OR:
            erros.append(f"regra termina em grupo OU: {r.name}")
        if ts and ts[-1].conect != bcm.CN_THEN:
            erros.append(f"última premissa sem ENTÃO: {r.name}")
        for t in ts:
            if t.var_code not in V or not ok_val(t.var_code, t.val_code):
                erros.append(f"premissa com referência inválida em {r.name}")
        for h in hs:
            if h.var_code not in V or not ok_val(h.var_code, h.val_code):
                erros.append(f"conclusão com referência inválida em {r.name}")
            if not 0 <= h.cnf <= 1:
                erros.append(f"CNF fora de 0..100% em {r.name}")

    for vc, v in V.items():
        nome = v.name.text
        perguntada = vc in questions
        inferida = vc in concluded
        usada = vc in used_in_prem or vc in targets
        if not usada and not inferida:
            avisos.append(f"variável nunca usada: {nome}")
        if (vc in used_in_prem or vc in targets) and not perguntada and not inferida:
            erros.append(f"variável sem pergunta e sem regra (prompt genérico): {nome}")
        if perguntada and inferida:
            avisos.append(f"pergunta que nunca será feita (variável inferida): {nome}")
        if perguntada and not questions[vc].why:
            avisos.append(f"pergunta sem 'por quê': {nome}")

    for t in b.targets:
        if t.code not in concluded:
            erros.append(f"objetivo sem regras: {V[t.code].name.text}")
        if t.show_results:
            concl_vals = {h.val_code for h in b.heads if h.var_code == t.code}
            for vcode in vals_by_var.get(t.code, set()):
                if vcode not in concl_vals:
                    nome = next(x.name.text for x in b.values if x.code == vcode)
                    erros.append(f"valor de objetivo inalcançável: {V[t.code].name.text} = {nome}")

    if verbose:
        print(f"== {path}")
        print(f"   {len(b.rules)} regras, {len(b.tails)} premissas, {len(b.heads)} conclusões, "
              f"{len(b.vars)} variáveis, {len(b.questions)} perguntas, {len(b.targets)} objetivos")
        for a in avisos:
            print("   AVISO:", a)
        for e in erros:
            print("   ERRO:", e)
        print("   RESULTADO:", "OK" if not erros else f"{len(erros)} ERRO(S)")
    return erros, avisos


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    total = 0
    for p in sys.argv[1:]:
        e, _ = auditar(p)
        total += len(e)
    sys.exit(1 if total else 0)
