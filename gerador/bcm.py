"""
Leitura e escrita do formato binário .BCM do Expert SINTA (v1.0 / v1.1).

Layout derivado de sinta/SINTA/sintascr/LIBRARY/EXSYSTEM.PAS
(TExpertSystem.SaveToFile / LoadFromFile), compilado em Delphi 32 bits com
{$H-} (string = ShortString de 256 bytes) e {$A-} (records sem alinhamento).

Tipos:
  TMyInteger = smallint (int16, little-endian)
  boolean    = 1 byte
  string     = ShortString: 1 byte de tamanho + 255 bytes (texto em cp1252)
  real       = Real48 (6 bytes, Turbo Pascal / Delphi 2-3)

Ordem no arquivo:
  header(10) | protection | info | vars | values | heads | tails | rules |
  formulas | questions | targets | contexts | general options
"""
from __future__ import annotations

import math
import struct
from dataclasses import dataclass, field
from typing import List, Optional

HEADER_PREFIX = bytes([45, 12, 189, 22, 99, 40, 243, 151, 202])
VERSION_BYTE = {"1.0": 33, "1.1": 34}

# Conectivos (EXCONSTS.PAS): cnAND=0, cnOR=1, cnTHEN=2
CN_AND, CN_OR, CN_THEN = 0, 1, 2
# Valores especiais de ValCode
VAL_UNKNOWN, VAL_YES, VAL_NO = -1, -2, -3

ENCODING = "cp1252"


# ----------------------------------------------------------------------------
# Real48 (Turbo Pascal "real")
# ----------------------------------------------------------------------------
def real48_decode(b: bytes) -> float:
    """6 bytes: [0]=expoente (bias 129), [1..5]=mantissa, bit 7 de b[5]=sinal."""
    assert len(b) == 6
    exp = b[0]
    if exp == 0:
        return 0.0
    sign = -1.0 if b[5] & 0x80 else 1.0
    mant = ((b[5] & 0x7F) << 32) | (b[4] << 24) | (b[3] << 16) | (b[2] << 8) | b[1]
    return sign * (1.0 + mant / float(1 << 39)) * 2.0 ** (exp - 129)


def real48_encode(x: float) -> bytes:
    if x == 0:
        return bytes(6)
    sign = 0x80 if x < 0 else 0
    x = abs(x)
    m, e = math.frexp(x)  # x = m * 2**e, 0.5 <= m < 1
    # forma 1.f * 2**(e-1)
    exp = e - 1 + 129
    frac = m * 2.0 - 1.0
    mant = int(round(frac * (1 << 39)))
    if mant == (1 << 39):
        mant = 0
        exp += 1
    if not 1 <= exp <= 255:
        raise ValueError(f"real48 fora de faixa: {x}")
    return bytes([
        exp,
        mant & 0xFF,
        (mant >> 8) & 0xFF,
        (mant >> 16) & 0xFF,
        (mant >> 24) & 0xFF,
        ((mant >> 32) & 0x7F) | sign,
    ])


# ----------------------------------------------------------------------------
# ShortString preservando bytes "lixo" após o texto (para round-trip exato)
# ----------------------------------------------------------------------------
@dataclass
class PStr:
    text: str
    raw: Optional[bytes] = None  # 256 bytes originais (se lido de arquivo)

    def to_bytes(self, size: int = 256) -> bytes:
        enc = self.text.encode(ENCODING)
        if len(enc) > size - 1:
            raise ValueError(f"string > {size - 1} bytes: {self.text[:40]}...")
        if self.raw is not None and len(self.raw) == size and self.raw[0] == len(enc) \
                and self.raw[1:1 + len(enc)] == enc:
            return self.raw
        return bytes([len(enc)]) + enc + bytes(size - 1 - len(enc))

    def __str__(self):
        return self.text


def S(text: str) -> PStr:
    return PStr(text)


# ----------------------------------------------------------------------------
# Estruturas
# ----------------------------------------------------------------------------
@dataclass
class Var:
    code: int
    name: PStr
    multi: bool = False
    numeric: bool = False


@dataclass
class Value:
    code: int
    name: PStr
    var_code: int
    position: int


@dataclass
class Head:          # conclusão: rule_code -> var = val CNF
    code: int        # código da regra
    var_code: int
    val_code: int
    cnf: float       # 0..100
    cnf_raw: Optional[bytes] = None


@dataclass
class Tail:          # premissa
    code: int        # código da regra
    var_code: int
    operator: PStr   # string[2] -> 3 bytes
    val_code: int
    conect: int      # CN_AND / CN_OR / CN_THEN(primeira premissa = "SE")
    neg: bool = False


@dataclass
class Rule:
    code: int
    name: PStr
    position: int    # campo VarCode do registro = ordem da regra


@dataclass
class Formula:
    code: int
    formula: PStr


@dataclass
class Question:
    code: int        # código da variável
    question: PStr
    why: List[PStr] = field(default_factory=list)
    use_cnf: bool = True


@dataclass
class Target:
    code: int        # código da variável
    show_results: bool = True


@dataclass
class Context:
    code: int
    context: int


@dataclass
class Base:
    version: str = "1.1"
    password: PStr = field(default_factory=lambda: S(""))
    permission: int = 3
    use_password: bool = False
    name: PStr = field(default_factory=lambda: S(""))
    authors: PStr = field(default_factory=lambda: S(""))
    overture: List[PStr] = field(default_factory=list)
    help_file: PStr = field(default_factory=lambda: S(""))
    show_intro: bool = True
    formula_and: PStr = field(default_factory=lambda: S(""))
    default_and: bool = True
    formula_or: PStr = field(default_factory=lambda: S(""))
    default_or: bool = True
    formula_concl: PStr = field(default_factory=lambda: S(""))
    default_concl: bool = True
    vars: List[Var] = field(default_factory=list)
    values: List[Value] = field(default_factory=list)
    heads: List[Head] = field(default_factory=list)
    tails: List[Tail] = field(default_factory=list)
    rules: List[Rule] = field(default_factory=list)
    formulas: List[Formula] = field(default_factory=list)
    questions: List[Question] = field(default_factory=list)
    targets: List[Target] = field(default_factory=list)
    contexts: List[Context] = field(default_factory=list)
    priority: int = CN_AND
    min_value: float = 0.5
    min_value_raw: Optional[bytes] = None
    examine_all: bool = False


# ----------------------------------------------------------------------------
# Leitura
# ----------------------------------------------------------------------------
class Reader:
    def __init__(self, data: bytes):
        self.d = data
        self.p = 0

    def take(self, n: int) -> bytes:
        if self.p + n > len(self.d):
            raise EOFError(f"fim inesperado em {self.p} (+{n})")
        b = self.d[self.p:self.p + n]
        self.p += n
        return b

    def i16(self) -> int:
        return struct.unpack("<h", self.take(2))[0]

    def boolean(self) -> bool:
        return self.take(1)[0] != 0

    def pstr(self, size: int = 256) -> PStr:
        raw = self.take(size)
        n = raw[0]
        if n > size - 1:
            raise ValueError(f"tamanho de string inválido {n} em {self.p - size}")
        return PStr(raw[1:1 + n].decode(ENCODING), raw)

    def real(self):
        raw = self.take(6)
        return real48_decode(raw), raw


def read_bcm(data: bytes) -> Base:
    r = Reader(data)
    hdr = r.take(10)
    if hdr[:9] != HEADER_PREFIX:
        raise ValueError("não é um arquivo Expert SINTA")
    version = {33: "1.0", 34: "1.1"}.get(hdr[9])
    if version is None:
        raise ValueError(f"versão desconhecida {hdr[9]}")
    b = Base(version=version)
    v11 = version == "1.1"

    # proteção (259 bytes)
    b.password = r.pstr()
    b.permission = r.i16()
    b.use_password = r.boolean()

    # info
    b.name = r.pstr()
    b.authors = r.pstr()
    b.overture = [r.pstr() for _ in range(r.i16())]
    b.help_file = r.pstr()
    b.show_intro = r.boolean()
    if v11:
        b.formula_and = r.pstr(); b.default_and = r.boolean()
        b.formula_or = r.pstr(); b.default_or = r.boolean()
        b.formula_concl = r.pstr(); b.default_concl = r.boolean()

    for _ in range(r.i16()):
        code = r.i16(); name = r.pstr(); multi = r.boolean(); num = r.boolean()
        b.vars.append(Var(code, name, multi, num))

    for _ in range(r.i16()):
        code = r.i16(); name = r.pstr(); vc = r.i16()
        pos = r.i16() if v11 else 0
        b.values.append(Value(code, name, vc, pos))

    for _ in range(r.i16()):
        code = r.i16(); vc = r.i16(); val = r.i16(); cnf, raw = r.real()
        b.heads.append(Head(code, vc, val, cnf, raw))

    for _ in range(r.i16()):
        code = r.i16(); vc = r.i16(); op = r.pstr(3); val = r.i16()
        con = r.i16(); neg = r.boolean()
        b.tails.append(Tail(code, vc, op, val, con, neg))

    for _ in range(r.i16()):
        code = r.i16(); name = r.pstr(); pos = r.i16()
        b.rules.append(Rule(code, name, pos))

    for _ in range(r.i16()):
        code = r.i16(); f = r.pstr()
        b.formulas.append(Formula(code, f))

    for _ in range(r.i16()):
        code = r.i16(); q = r.pstr()
        why = [r.pstr() for _ in range(r.i16())]
        uc = r.boolean() if v11 else True
        b.questions.append(Question(code, q, why, uc))

    for _ in range(r.i16()):
        if v11:
            code = r.i16(); sr = r.boolean()
        else:
            code = r.i16(); sr = True
        b.targets.append(Target(code, sr))

    for _ in range(r.i16()):
        code = r.i16(); ctx = r.i16()
        b.contexts.append(Context(code, ctx))

    b.priority = r.i16()
    b.min_value, b.min_value_raw = r.real()
    b.examine_all = r.boolean()

    if r.p != len(data):
        raise ValueError(f"sobraram {len(data) - r.p} bytes após o fim (pos {r.p})")
    return b


# ----------------------------------------------------------------------------
# Escrita
# ----------------------------------------------------------------------------
def write_bcm(b: Base) -> bytes:
    out = bytearray()
    i16 = lambda v: out.extend(struct.pack("<h", v))
    bo = lambda v: out.append(1 if v else 0)
    ps = lambda s, n=256: out.extend(s.to_bytes(n))

    def real(v, raw=None):
        if raw is not None and abs(real48_decode(raw) - v) < 1e-9:
            out.extend(raw)
        else:
            out.extend(real48_encode(v))

    v11 = b.version == "1.1"
    out.extend(HEADER_PREFIX + bytes([VERSION_BYTE[b.version]]))
    ps(b.password); i16(b.permission); bo(b.use_password)
    ps(b.name); ps(b.authors)
    i16(len(b.overture))
    for line in b.overture:
        ps(line)
    ps(b.help_file); bo(b.show_intro)
    if v11:
        ps(b.formula_and); bo(b.default_and)
        ps(b.formula_or); bo(b.default_or)
        ps(b.formula_concl); bo(b.default_concl)

    i16(len(b.vars))
    for v in b.vars:
        i16(v.code); ps(v.name); bo(v.multi); bo(v.numeric)
    i16(len(b.values))
    for v in b.values:
        i16(v.code); ps(v.name); i16(v.var_code)
        if v11:
            i16(v.position)
    i16(len(b.heads))
    for h in b.heads:
        i16(h.code); i16(h.var_code); i16(h.val_code); real(h.cnf, h.cnf_raw)
    i16(len(b.tails))
    for t in b.tails:
        i16(t.code); i16(t.var_code); ps(t.operator, 3); i16(t.val_code)
        i16(t.conect); bo(t.neg)
    i16(len(b.rules))
    for r in b.rules:
        i16(r.code); ps(r.name); i16(r.position)
    i16(len(b.formulas))
    for f in b.formulas:
        i16(f.code); ps(f.formula)
    i16(len(b.questions))
    for q in b.questions:
        i16(q.code); ps(q.question)
        i16(len(q.why))
        for w in q.why:
            ps(w)
        if v11:
            bo(q.use_cnf)
    i16(len(b.targets))
    for t in b.targets:
        i16(t.code)
        if v11:
            bo(t.show_results)
    i16(len(b.contexts))
    for c in b.contexts:
        i16(c.code); i16(c.context)
    i16(b.priority)
    real(b.min_value, b.min_value_raw)
    bo(b.examine_all)
    return bytes(out)


# ----------------------------------------------------------------------------
# Visualização textual (para inspeção / relatório)
# ----------------------------------------------------------------------------
def dump(b: Base, max_rules: Optional[int] = None) -> str:
    vars_ = {v.code: v for v in b.vars}
    vals = {v.code: v for v in b.values}
    forms = {f.code: f for f in b.formulas}

    def valname(var_code, val_code):
        if val_code == VAL_UNKNOWN:
            return "DESCONHECIDO"
        if val_code == VAL_YES:
            return "Sim"
        if val_code == VAL_NO:
            return "Não"
        v = vars_.get(var_code)
        if v is not None and v.numeric:
            f = forms.get(val_code)
            return f"<{f.formula}>" if f else f"<formula {val_code}?>"
        x = vals.get(val_code)
        return x.name.text if x else f"<val {val_code}?>"

    L = [f"Base: {b.name} (v{b.version})", f"Autores: {b.authors}",
         f"Abertura: {' / '.join(s.text for s in b.overture)}",
         f"Opções: prioridade={'E' if b.priority == CN_AND else 'OU'} "
         f"cnf_min={b.min_value:.2f} examinar_tudo={b.examine_all}", ""]
    L.append(f"VARIÁVEIS ({len(b.vars)}):")
    for v in sorted(b.vars, key=lambda v: v.code):
        kind = "numérica" if v.numeric else ("multi" if v.multi else "uni")
        vs = sorted((x for x in b.values if x.var_code == v.code), key=lambda x: x.position)
        L.append(f"  [{v.code}] {v.name} ({kind}): " + "; ".join(x.name.text for x in vs))
    L.append("")
    L.append("OBJETIVOS: " + ", ".join(
        f"{vars_[t.code].name}{'' if t.show_results else ' (oculto)'}" for t in b.targets))
    L.append("")
    rules = sorted(b.rules, key=lambda r: r.position)
    L.append(f"REGRAS ({len(rules)}):")
    for r in rules[:max_rules]:
        L.append(f"  Regra {r.position} [cód {r.code}] {r.name}")
        # O conectivo de cada premissa liga-a à PRÓXIMA; a última tem cnTHEN.
        prev = "SE"
        for t in (x for x in b.tails if x.code == r.code):
            neg = "NÃO " if t.neg else ""
            L.append(f"    {prev:5} {neg}{vars_[t.var_code].name} {t.operator} "
                     f"{valname(t.var_code, t.val_code)}")
            prev = {CN_AND: "E", CN_OR: "OU", CN_THEN: "ENTÃO"}.get(t.conect, f"?{t.conect}")
        for i, h in enumerate(x for x in b.heads if x.code == r.code):
            L.append(f"    {'ENTÃO' if i == 0 else 'E':5} {vars_[h.var_code].name} = "
                     f"{valname(h.var_code, h.val_code)} CNF {h.cnf * 100:.0f}%")
    L.append("")
    L.append(f"PERGUNTAS ({len(b.questions)}):")
    for q in b.questions:
        L.append(f"  {vars_[q.code].name}: {q.question}  (CNF na resposta={q.use_cnf})")
        for w in q.why:
            L.append(f"      por quê: {w}")
    return "\n".join(L)
