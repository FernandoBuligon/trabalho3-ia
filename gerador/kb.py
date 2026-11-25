"""
API de alto nível para montar bases do Expert SINTA e compilá-las para .BCM.

Exemplo:
    kb = KB("Minha base", autores="Fulano")
    kb.var("gênero", ["ação", "drama"], multi=False)
    kb.var("duração", numeric=True)
    kb.var("filme", ["A", "B"], multi=True)
    kb.rule("R1", se=[("gênero", "=", "ação"), "E", ("duração", "<", 120)],
            entao=[("filme", "A", 90)])
    kb.question("gênero", "Qual gênero você prefere?", why=["..."])
    kb.target("filme")
    open("x.bcm", "wb").write(kb.compile())
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple, Union

import bcm
from bcm import S

# Premissa: (var, op, valor) ou (var, op, valor, negada)
Premise = Tuple
Conclusion = Tuple  # (var, valor) ou (var, valor, cnf_percentual)

SIM, NAO, DESCONHECIDO = "Sim", "Não", "DESCONHECIDO"
OPS = {"=", "<>", ">", "<", ">=", "<="}


@dataclass
class _Var:
    name: str
    values: List[str]
    multi: bool
    numeric: bool
    logical: bool  # sem valores -> Sim/Não


@dataclass
class _Rule:
    name: str
    premises: List[Tuple[str, str, object, bool]]
    connectives: List[str]  # len = len(premises) - 1, "E"/"OU"
    conclusions: List[Tuple[str, object, float]]


class KBError(Exception):
    pass


class KB:
    def __init__(self, nome: str, autores: str = "", abertura: Sequence[str] = (),
                 mostrar_abertura: bool = True, cnf_minimo: float = 50,
                 prioridade: str = "E", examinar_tudo: bool = False):
        self.nome, self.autores = nome, autores
        self.abertura = list(abertura)
        self.mostrar_abertura = mostrar_abertura
        self.cnf_minimo = cnf_minimo
        self.prioridade = prioridade
        self.examinar_tudo = examinar_tudo
        self.vars: Dict[str, _Var] = {}
        self.rules: List[_Rule] = []
        self.questions: Dict[str, Tuple[str, List[str], bool]] = {}
        self.targets: List[Tuple[str, bool]] = []

    # ------------------------------------------------------------------ vars
    def var(self, nome: str, valores: Sequence[str] = (), multi: bool = False,
            numeric: bool = False, faixa: Optional[Tuple[float, float]] = None) -> str:
        """faixa (somente numéricas): intervalo aceito na pergunta, gravado como
        o valor "min;max" (o SINTA exibe uma barra deslizante)."""
        if nome in self.vars:
            raise KBError(f"variável duplicada: {nome}")
        if len(nome.encode(bcm.ENCODING)) > 255:
            raise KBError(f"nome de variável longo demais: {nome}")
        valores = list(valores)
        if len(set(valores)) != len(valores):
            raise KBError(f"valores duplicados em {nome}")
        for x in valores:
            if len(x.encode(bcm.ENCODING)) > 255:
                raise KBError(f"valor longo demais em {nome}: {x}")
            if x in (SIM, NAO, DESCONHECIDO) and len(valores) > 0:
                raise KBError(f"{nome}: valor reservado {x!r}")
        if numeric and valores:
            raise KBError("variável numérica não tem lista de valores (use faixa=)")
        if faixa is not None:
            if not numeric:
                raise KBError("faixa só vale para variável numérica")
            valores = [f"{_num_text(faixa[0])};{_num_text(faixa[1])}"]
        self.vars[nome] = _Var(nome, valores, multi and not numeric, numeric,
                               logical=not numeric and not valores)
        return nome

    def add_values(self, nome: str, valores: Sequence[str]):
        v = self.vars[nome]
        for x in valores:
            if x not in v.values:
                v.values.append(x)

    # ----------------------------------------------------------------- rules
    def rule(self, nome: str, se: Sequence, entao: Sequence[Conclusion]):
        """`se` alterna premissas e conectivos: [p1, "E", p2, "OU", p3].
        Se os conectivos forem omitidos ([p1, p2, p3]) assume-se "E"."""
        prem, conn = [], []
        expect_premise = True
        for item in se:
            if isinstance(item, str):
                if expect_premise or item not in ("E", "OU"):
                    raise KBError(f"{nome}: conectivo inesperado {item!r}")
                conn.append(item)
                expect_premise = True
            else:
                if not expect_premise:
                    conn.append("E")
                var, op, val = item[0], item[1], item[2]
                val = self._norm(var, val)
                neg = bool(item[3]) if len(item) > 3 else False
                self._check_premise(nome, var, op, val)
                prem.append((var, op, val, neg))
                expect_premise = False
        if not prem:
            raise KBError(f"{nome}: regra sem premissas")
        if expect_premise:
            raise KBError(f"{nome}: termina com conectivo")
        concl = []
        for c in entao:
            var, val = c[0], self._norm(c[0], c[1])
            cnf = float(c[2]) if len(c) > 2 else 100.0
            self._check_value(nome, var, val)
            if not 0 <= cnf <= 100:
                raise KBError(f"{nome}: CNF fora de 0..100")
            concl.append((var, val, cnf))
        if not concl:
            raise KBError(f"{nome}: regra sem conclusões")
        if len(nome.encode(bcm.ENCODING)) > 255:
            raise KBError("nome de regra longo demais")
        self.rules.append(_Rule(nome, prem, conn, concl))

    def _norm(self, var, val):
        """Valores de variáveis não numéricas são sempre texto ("12", não 12)."""
        v = self.vars.get(var)
        if v is not None and not v.numeric and isinstance(val, (int, float)):
            return _num_text(val)
        return val

    def _check_premise(self, rule, var, op, val):
        if op not in OPS:
            raise KBError(f"{rule}: operador inválido {op}")
        v = self._getvar(rule, var)
        if op not in ("=", "<>") and not v.numeric:
            raise KBError(f"{rule}: operador {op} exige variável numérica ({var})")
        self._check_value(rule, var, val)

    def _check_value(self, rule, var, val):
        v = self._getvar(rule, var)
        if val == DESCONHECIDO:
            return
        if v.numeric:
            try:
                float(val)
            except (TypeError, ValueError):
                raise KBError(f"{rule}: valor numérico inválido para {var}: {val!r}")
            return
        if v.logical:
            if val not in (SIM, NAO):
                raise KBError(f"{rule}: {var} é lógica (Sim/Não), recebeu {val!r}")
            return
        if val not in v.values:
            raise KBError(f"{rule}: valor {val!r} não pertence a {var}")

    def _getvar(self, rule, var) -> _Var:
        if var not in self.vars:
            raise KBError(f"{rule}: variável inexistente {var!r}")
        return self.vars[var]

    # ------------------------------------------------------------ interface
    def question(self, var: str, texto: str, why: Sequence[str] = (), usar_cnf: bool = True):
        self._getvar("pergunta", var)
        self.questions[var] = (texto, list(why), usar_cnf)

    def target(self, var: str, mostrar: bool = True):
        self._getvar("objetivo", var)
        self.targets.append((var, mostrar))

    # -------------------------------------------------------------- compile
    def compile(self) -> bytes:
        b = self.to_base()
        for nome, n in (("variáveis", len(b.vars)), ("valores", len(b.values)),
                        ("regras", len(b.rules)), ("premissas", len(b.tails)),
                        ("conclusões", len(b.heads)), ("fórmulas", len(b.formulas))):
            if n > 32767:
                raise KBError(f"limite int16 excedido em {nome}: {n}")
        return bcm.write_bcm(b)

    def to_base(self) -> bcm.Base:
        b = bcm.Base(version="1.1")
        b.name, b.authors = S(self.nome), S(self.autores)
        b.overture = [S(x) for x in self.abertura]
        b.show_intro = self.mostrar_abertura
        b.priority = bcm.CN_AND if self.prioridade == "E" else bcm.CN_OR
        b.min_value = self.cnf_minimo / 100.0
        b.examine_all = self.examinar_tudo

        var_code: Dict[str, int] = {}
        val_code: Dict[Tuple[str, str], int] = {}
        next_val = 1
        for i, v in enumerate(self.vars.values(), start=1):
            var_code[v.name] = i
            b.vars.append(bcm.Var(i, S(v.name), v.multi, v.numeric))
            for pos, x in enumerate(v.values, start=1):
                val_code[(v.name, x)] = next_val
                b.values.append(bcm.Value(next_val, S(x), i, pos))
                next_val += 1

        formulas: Dict[str, int] = {}

        def code_for(var: str, val) -> int:
            if val == DESCONHECIDO:
                return bcm.VAL_UNKNOWN
            v = self.vars[var]
            if v.numeric:
                txt = _num_text(val)
                if txt not in formulas:
                    formulas[txt] = len(formulas) + 1
                    b.formulas.append(bcm.Formula(formulas[txt], S(txt)))
                return formulas[txt]
            if v.logical:
                return bcm.VAL_YES if val == SIM else bcm.VAL_NO
            return val_code[(var, val)]

        for rc, r in enumerate(self.rules, start=1):
            b.rules.append(bcm.Rule(rc, S(r.name), rc))
            for i, (var, op, val, neg) in enumerate(r.premises):
                if i < len(r.connectives):
                    con = bcm.CN_AND if r.connectives[i] == "E" else bcm.CN_OR
                else:
                    con = bcm.CN_THEN
                b.tails.append(bcm.Tail(rc, var_code[var], S(op), code_for(var, val), con, neg))
            for var, val, cnf in r.conclusions:
                b.heads.append(bcm.Head(rc, var_code[var], code_for(var, val), cnf / 100.0))

        for var, (txt, why, uc) in self.questions.items():
            b.questions.append(bcm.Question(var_code[var], S(txt), [S(w) for w in why], uc))
        for var, show in self.targets:
            b.targets.append(bcm.Target(var_code[var], show))
        return b

    # ---------------------------------------------------------------- stats
    def stats(self) -> Dict[str, int]:
        return {
            "variaveis": len(self.vars),
            "valores": sum(len(v.values) for v in self.vars.values()),
            "regras": len(self.rules),
            "premissas": sum(len(r.premises) for r in self.rules),
            "conclusoes": sum(len(r.conclusions) for r in self.rules),
            "perguntas": len(self.questions),
            "objetivos": len(self.targets),
        }


def _num_text(val) -> str:
    if isinstance(val, float) and val.is_integer():
        val = int(val)
    return str(val)
