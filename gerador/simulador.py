"""
Simulador fiel da máquina de inferência do Expert SINTA 1.1b.

Port direto de LIBRARY/EXSYSTEM.PAS (StartEngine, Find, SeekRule, TailResult,
ExpressionResult/PostFix/PreAnswer/Evaluate, ComparationCNF, AttribVar,
ExecuteRule). Serve para testar as bases geradas com milhares de consultas
automáticas, sem depender da interface gráfica.

Respostas do usuário (dicionário `respostas`):
  variável multi/uni :  ["valor", ...]  ou  [("valor", cnf_percentual), ...]
  variável lógica    :  "Sim" / "Não"
  variável numérica  :  número
  ausente / None     :  DESCONHECIDO (equivale a não marcar nada)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import bcm

UNKNOWN, YES, NO = bcm.VAL_UNKNOWN, bcm.VAL_YES, bcm.VAL_NO
AND_S, OR_S, THEN_S = "E  ", "OU ", "ENTÃO"


class _Abort(Exception):
    pass


@dataclass
class Resultado:
    objetivos: Dict[str, List[Tuple[str, float]]]          # var -> [(valor, cnf%)] ordenado
    perguntas: List[str]                                    # ordem das perguntas feitas
    regras_disparadas: List[str]                            # nomes das regras aceitas
    regras_avaliadas: int = 0
    instancias: Dict[str, List[Tuple[str, float]]] = field(default_factory=dict)


class Motor:
    def __init__(self, base: bcm.Base):
        self.b = base
        self.vars = {v.code: v for v in base.vars}
        self.var_by_name = {v.name.text: v for v in base.vars}
        self.vals = {v.code: v for v in base.values}
        self.val_by_name: Dict[Tuple[int, str], int] = {
            (v.var_code, v.name.text.upper()): v.code for v in base.values}
        self.formulas = {f.code: f.formula.text for f in base.formulas}
        self.rules = {r.code: r for r in base.rules}
        self.tails: Dict[int, List[bcm.Tail]] = {}
        for t in base.tails:
            self.tails.setdefault(t.code, []).append(t)
        self.heads: Dict[int, List[bcm.Head]] = {}
        self.heads_by_var: Dict[int, List[int]] = {}
        for h in base.heads:
            self.heads.setdefault(h.code, []).append(h)
            lst = self.heads_by_var.setdefault(h.var_code, [])
            if h.code not in lst:
                lst.append(h.code)
        self.min_value = base.min_value
        self.priority = base.priority

    # ------------------------------------------------------------------ API
    def consultar(self, respostas: Dict[str, object]) -> Resultado:
        self.resp = {}
        for nome, val in (respostas or {}).items():
            if nome not in self.var_by_name:
                raise KeyError(f"variável inexistente na resposta: {nome}")
            self.resp[self.var_by_name[nome].code] = val
        self.varlist: Dict[int, List[List]] = {}    # code -> [[valcode, cnf], ...]
        self.varextra: Dict[int, List] = {}         # numéricas: code -> [valor_float, cnf]
        self.used = set()
        self.asked: List[str] = []
        self.fired: List[str] = []
        self.n_eval = 0
        out = {}
        for t in self.b.targets:
            self.find(t.code)
            if t.show_results:
                out[self.vars[t.code].name.text] = self.instancias(t.code)
        inst = {self.vars[c].name.text: self.instancias(c)
                for c in set(self.varlist) | set(self.varextra)}
        return Resultado(out, self.asked, self.fired, self.n_eval, inst)

    def instancias(self, code: int) -> List[Tuple[str, float]]:
        if code in self.varextra:
            v, c = self.varextra[code]
            return [(_fmt(v), round(c * 100, 2))]
        res = []
        for vc, cnf in self.varlist.get(code, []):
            res.append((self.val_text(code, vc), round(cnf * 100, 2)))
        res.sort(key=lambda x: -x[1])
        return res

    def val_text(self, var_code, vc):
        if vc == UNKNOWN:
            return "DESCONHECIDO"
        if vc == YES:
            return "Sim"
        if vc == NO:
            return "Não"
        return self.vals[vc].name.text

    # ------------------------------------------------------------- Find
    def find(self, v: int):
        already = v in self.varlist or v in self.varextra
        var = self.vars[v]
        rules = self.heads_by_var.get(v)
        if rules:
            order = sorted(rules, key=lambda rc: self.rules[rc].position)
            flag = False
            for rc in order:
                if not (var.multi or not flag):
                    break
                if rc in self.used:
                    continue
                cnf = self.tail_result(rc)
                if cnf >= self.min_value:
                    self.fired.append(self.rules[rc].name.text)
                    self.execute_rule(rc, cnf)
                    flag = True
                self.used.add(rc)
            if not flag and not already:
                self.attrib(v, UNKNOWN, 1.0)
        else:
            self.prompt(v)

    def prompt(self, v: int):
        var = self.vars[v]
        self.asked.append(var.name.text)
        ans = self.resp.get(v)
        if var.numeric:
            if ans is None or ans == "":
                self.attrib(v, UNKNOWN, 1.0)
            else:
                self.attrib_numeric(v, float(ans), 1.0)
            return
        if ans is None:
            self.attrib(v, UNKNOWN, 1.0)
            return
        if isinstance(ans, (str, tuple)):
            ans = [ans]
        any_ = False
        for item in ans:
            if isinstance(item, tuple):
                val, cnf = item[0], item[1] / 100.0
            else:
                val, cnf = item, 1.0
            self.attrib(v, self.code_of(v, val), cnf)
            any_ = True
        if not any_:
            self.attrib(v, UNKNOWN, 1.0)

    def code_of(self, v: int, val: str) -> int:
        if val == "DESCONHECIDO":
            return UNKNOWN
        has_values = any(x.var_code == v for x in self.b.values)
        if not has_values:
            if val == "Sim":
                return YES
            if val == "Não":
                return NO
        k = (v, val.upper())
        if k not in self.val_by_name:
            raise KeyError(f"valor {val!r} não existe em {self.vars[v].name.text}")
        return self.val_by_name[k]

    # ------------------------------------------------------- AttribVar
    def attrib(self, v: int, vc: int, cnf: float):
        var = self.vars[v]
        if var.numeric:
            if vc == UNKNOWN:
                self.varextra.pop(v, None)
                self.varlist[v] = [[UNKNOWN, cnf]]
            else:
                self.attrib_numeric(v, self.calc(vc), cnf)
            return
        lst = self.varlist.setdefault(v, [])
        if var.multi:
            for item in lst:
                if item[0] == vc:
                    item[1] = item[1] + cnf - item[1] * cnf
                    return
            lst.append([vc, cnf])
            return
        # univalorada (igualdade testada ANTES da transformação Sim/Não, como no original)
        equal = bool(lst) and lst[0][0] == vc
        vc, cnf = _yesno(vc, cnf)
        if lst:
            item = lst[0]
            if equal:
                final = item[1] + cnf - item[1] * cnf
                vc2, final = _yesno(vc, final)
                item[0], item[1] = vc2, final
            else:
                item[0], item[1] = vc, cnf
        else:
            lst.append([vc, cnf])

    def attrib_numeric(self, v: int, value: float, cnf: float):
        self.varlist.pop(v, None)
        self.varextra[v] = [value, cnf]

    def calc(self, formula_code: int) -> float:
        return float(self.formulas[formula_code].replace(",", "."))

    def execute_rule(self, rc: int, cnf: float):
        for h in self.heads.get(rc, []):
            self.attrib(h.var_code, h.val_code, cnf * h.cnf)

    # ------------------------------------------------- ComparationCNF
    def compare(self, t: bcm.Tail) -> float:
        v = t.var_code
        op = t.operator.text
        if t.neg:
            op = {"=": "<>", "<>": "=", ">=": "<", "<=": ">", "<": ">=", ">": "<="}[op]
        if v not in self.varlist and v not in self.varextra:
            self.find(v)
        var = self.vars[v]
        if v in self.varextra:   # numérica com valor
            x, c = self.varextra[v]
            ref = self.calc(t.val_code)
            if op == "=":
                return c if x == ref else 0.0
            if op == "<>":
                return c if x != ref else 0.0
            ok = {">": x > ref, "<": x < ref, ">=": x >= ref, "<=": x <= ref}[op]
            return 1.0 if ok else 0.0
        lst = self.varlist.get(v, [])
        found = None
        for item in lst:
            if item[0] == t.val_code:
                found = item
                break
        if op == "=":
            return found[1] if found else 0.0
        if op == "<>":
            return (1.0 - found[1]) if found else 1.0
        return 0.0  # numérica DESCONHECIDA com >,<,...

    # ------------------------------------------- ExpressionResult (pilhas)
    def tail_result(self, rc: int) -> float:
        self.n_eval += 1
        tails = self.tails.get(rc, [])
        if not tails:
            return 0.0
        # PostFix
        out: List[object] = []          # itens: índice de premissa (int) ou conectivo (str)
        idx: List[int] = []             # posição na pilha de cada premissa
        aux: List[str] = []
        conns = [{0: AND_S, 1: OR_S, 2: THEN_S}[t.conect] for t in tails]
        for i, t in enumerate(tails):
            out.append(None)            # '-1' = não avaliado
            idx.append(len(out) - 1)
            tok = conns[i]
            if tok == THEN_S:
                break
            if aux:
                if self.priority == bcm.CN_OR:
                    if aux[-1] == OR_S and tok == AND_S:
                        while aux:
                            out.append(aux.pop())
                else:
                    if aux[-1] == AND_S and tok == OR_S:
                        while aux:
                            out.append(aux.pop())
            aux.append(tok)
        while aux:
            out.append(aux.pop())
        stack = out  # valores: None (-1), float, ou conectivo

        order = 1
        while True:
            pos = idx[order - 1]
            if stack[pos] is None:
                stack[pos] = self.compare(tails[order - 1])
                if order == len(idx):
                    return self._evaluate(stack)
                if self._pre_answer(stack, 1.0) < self.min_value:
                    return 0.0  # abortada
                r = self._pre_answer(stack, 0.0)
                if r >= self.min_value:
                    return r
            order += 1
            if order > len(idx):
                # situação que no SINTA original gera erro de índice
                raise _Abort(f"regra {self.rules[rc].name.text}: última premissa marcada")

    def _and(self, a, b):
        return a * b

    def _or(self, a, b):
        return a + b - a * b

    def _evaluate(self, s) -> float:
        r = []
        for it in s:
            if isinstance(it, str):
                b_ = r.pop(); a_ = r.pop()
                r.append(self._and(a_, b_) if it == AND_S else self._or(a_, b_))
            else:
                r.append(it)
        return r[-1]

    def _pre_answer(self, stack, confidence: float) -> float:
        st = [confidence if it is None else it for it in stack]
        ev: List[float] = []
        shortcut: List[int] = []
        for cont, it in enumerate(st):
            if not isinstance(it, str):
                ev.append(it)
                shortcut.append(cont)
            else:
                b_ = ev.pop(); a_ = ev.pop()
                ev.append(self._and(a_, b_) if it == AND_S else self._or(a_, b_))
                top = ev[-1]
                if (top >= self.min_value and confidence == 0.0) or \
                        (top < self.min_value and confidence == 1.0):
                    while shortcut:
                        k = shortcut.pop()
                        if stack[k] is None:
                            stack[k] = confidence
        return ev[-1]


def _yesno(vc, cnf):
    if vc == YES and cnf < 0.5:
        return NO, 1 - cnf
    if vc == NO and cnf <= 0.5:
        return YES, 1 - cnf
    return vc, cnf


def _fmt(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else str(x)


def simular(base: bcm.Base, respostas: Dict[str, object]) -> Resultado:
    return Motor(base).consultar(respostas)
