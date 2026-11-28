"""
Gerador de bases do Expert SINTA a partir de dados (CSV) + configuração (YAML).

    python build.py ../dados/filmes.yaml

Arquitetura de conhecimento em camadas (ver relatório):
  1. Perguntas ao usuário (variáveis de entrada, "X preferido").
  2. Regras intermediárias:
     - geradas: camada de COMPATIBILIDADE ("X preferido" -> "X compatível"),
       que absorve "indiferente", resposta em branco (DESCONHECIDO) e grupos
       (ex.: "estrangeira" -> todos os países que não o Brasil);
     - escritas à mão no YAML (faixas numéricas, perfis, classificação...).
  3. Regras por item geradas a partir de *modelos* e *evidências*; a combinação
     de CNF do SINTA para o mesmo valor (ca + cn - ca·cn) produz um ranking por
     acúmulo de evidências ("noisy-OR").

Saídas: <arquivo>.bcm, <arquivo>.txt (base legível) e <arquivo>.json (estatísticas).
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from collections import OrderedDict
from typing import Dict, List, Optional

import yaml

import bcm
from kb import KB, KBError, SIM, NAO, DESCONHECIDO

OPS_ORDER = [">=", "<=", "<>", "=", ">", "<"]
INDIF = "indiferente"


# ============================================================================
# DSL de condições:  "a = x OU a = y E b >= 10"
# ============================================================================
def parse_cond(text: str) -> List:
    """Converte texto em lista alternando premissas e conectivos para KB.rule."""
    text = " ".join(str(text).split())
    parts = re.split(r"\s+(E|OU)\s+", text)
    out: List = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            out.append(p)
            continue
        out.append(parse_premise(p))
    return out


def parse_premise(p: str):
    for op in OPS_ORDER:
        k = p.find(f" {op} ")
        if k >= 0:
            var = p[:k].strip()
            val = p[k + len(op) + 2:].strip()
            return (var, op, val)    # texto; o kb converte se a variável for numérica
    raise KBError(f"premissa inválida: {p!r}")


def parse_concl(text: str):
    """'var = valor [CNF n]'"""
    m = re.match(r"^(.*?)\s=\s(.*?)(?:\s+CNF\s+([\d.]+))?$", " ".join(str(text).split()))
    if not m:
        raise KBError(f"conclusão inválida: {text!r}")
    var, val, cnf = m.group(1).strip(), m.group(2).strip(), m.group(3)
    return (var, val, float(cnf) if cnf else 100.0)


# ============================================================================
# Leitura de itens
# ============================================================================
def load_items(cfg_items: dict, base_dir: str) -> List[Dict[str, object]]:
    path = os.path.join(base_dir, cfg_items["arquivo"])
    sep = cfg_items.get("separador_lista", "|")
    listas = set(cfg_items.get("colunas_lista", []))
    items = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if not any((v or "").strip() for v in row.values()):
                continue
            it = {}
            for k, v in row.items():
                if k is None:
                    raise KBError(f"{path}: linha com colunas a mais: {row}")
                v = (v or "").strip()
                it[k] = [x.strip() for x in v.split(sep) if x.strip()] if k in listas else v
            items.append(it)
    for d in cfg_items.get("derivados", []):
        for it in items:
            raw = it.get(d["de"], "")
            if raw in ("", None):
                it[d["coluna"]] = ""
                continue
            chave = it[cfg_items["chave"]]
            try:
                x = float(str(raw).replace(",", "."))
            except ValueError:
                raise KBError(f"{chave}: {d['de']}={raw!r} não é numérico")
            # faixas semiabertas pelo limite inferior: um valor entre duas faixas
            # (ex.: 100,5 com 0–100 e 101–130) fica na de baixo
            faixas = sorted(d["faixas"], key=lambda f: f[0])
            val = None
            if faixas[0][0] <= x <= faixas[-1][1]:
                val = [nome for lo, hi, nome in faixas if lo <= x][-1]
            if val is None:
                raise KBError(f"{chave}: {d['de']}={raw} fora das faixas")
            it[d["coluna"]] = val
    return items


def as_list(v) -> List[str]:
    if v in (None, ""):
        return []
    return list(v) if isinstance(v, list) else [v]


# ============================================================================
# Construção
# ============================================================================
class Builder:
    def __init__(self, cfg_path: str):
        self.cfg_path = os.path.abspath(cfg_path)
        self.base_dir = os.path.dirname(self.cfg_path)
        self.cfg = yaml.safe_load(open(cfg_path, encoding="utf-8"))
        b = self.cfg["base"]
        self.kb = KB(b["nome"], autores=b.get("autores", ""), abertura=b.get("abertura", []),
                     mostrar_abertura=b.get("mostrar_abertura", True),
                     cnf_minimo=b.get("cnf_minimo", 50), prioridade=b.get("prioridade", "OU"))
        self.warnings: List[str] = []
        self.rule_kinds: Dict[str, int] = OrderedDict()
        self.esquema = None
        if "esquema" in self.cfg:
            self.esquema = yaml.safe_load(open(os.path.join(self.base_dir, self.cfg["esquema"]),
                                               encoding="utf-8"))
        self.items: List[dict] = []
        self.compat_specs: List[dict] = []

    # --------------------------------------------------------------------
    def build(self) -> KB:
        if "itens" in self.cfg:
            self.items = load_items(self.cfg["itens"], self.base_dir)
        self._vars()
        self._compat_rules()
        self._explicit_rules()
        if "itens" in self.cfg:
            self._items()
        self._targets()
        return self.kb

    # ------------------------------------------------------------ variáveis
    def _base_values(self, v) -> List[str]:
        if "valores" in v:
            return [str(x) for x in v["valores"]]
        if "valores_esquema" in v:
            return [str(x) for x in self.esquema["colunas"][v["valores_esquema"]]["valores"]]
        if "valores_coluna" in v:
            col = v["valores_coluna"]
            vals = sorted({x for it in self.items for x in as_list(it[col])}, key=str.casefold)
            return vals
        return []

    def _vars(self):
        for v in self.cfg["variaveis"]:
            tipo = v.get("tipo", "uni")
            nome = v["nome"]
            if tipo == "numerica":
                faixa = v.get("faixa")
                self.kb.var(nome, numeric=True, faixa=tuple(faixa) if faixa else None)
            elif tipo == "logica":
                self.kb.var(nome)
            else:
                base = self._base_values(v)
                grupos = list((v.get("grupos") or {}).keys())
                vals = base + grupos + ([INDIF] if v.get("indiferente") else [])
                self.kb.var(nome, vals, multi=(tipo == "multi"))
                if v.get("compativel"):
                    self.kb.var(v["compativel"], base, multi=True)
                    self.compat_specs.append(dict(v, _base=base))
            if "pergunta" in v:
                self.kb.question(nome, v["pergunta"], v.get("porque", []),
                                 v.get("usar_cnf", tipo != "logica"))

    def _count(self, kind):
        self.rule_kinds[kind] = self.rule_kinds.get(kind, 0) + 1

    # ---------------------------------------------- camada de compatibilidade
    def _compat_rules(self):
        """Para cada pergunta P com `compativel: C`, gera:
             SE P = v            ENTÃO C = v                 (para cada valor)
             SE P = grupo        ENTÃO C = membros do grupo
             SE P = indiferente  ENTÃO C = todos
             SE P = DESCONHECIDO ENTÃO C = todos   (usuário não marcou nada)"""
        for v in self.compat_specs:
            p, c, base = v["nome"], v["compativel"], v["_base"]
            kind = "compatibilidade"
            for x in base:
                self.kb.rule(f"{c}: {x}", [(p, "=", x)], [(c, x, 100)])
                self._count(kind)
            for g, membros in (v.get("grupos") or {}).items():
                membros = [str(m) for m in membros]
                for m in membros:
                    if m not in base:
                        raise KBError(f"grupo {g}: {m!r} não é valor de {p}")
                self.kb.rule(f"{c}: grupo {g}", [(p, "=", g)], [(c, m, 100) for m in membros])
                self._count(kind)
            if v.get("indiferente"):
                self.kb.rule(f"{c}: indiferente", [(p, "=", INDIF)], [(c, x, 100) for x in base])
                self._count(kind)
            self.kb.rule(f"{c}: sem resposta", [(p, "=", DESCONHECIDO)], [(c, x, 100) for x in base])
            self._count(kind)

    # -------------------------------------------------------- regras do YAML
    def _explicit_rules(self):
        for grupo in self.cfg.get("regras", []):
            kind = grupo.get("grupo", "intermediárias")
            for r in grupo["itens"]:
                se = parse_cond(r["se"])
                if len(se) >= 3 and se[-2] == "OU":
                    self.warnings.append(f"regra '{r['nome']}' termina com premissa em grupo OU")
                entao = [parse_concl(c) for c in r["entao"]]
                self.kb.rule(r["nome"], se, entao)
                self._count(kind)

    # ------------------------------------------------------------- itens
    def _items(self):
        ci = self.cfg["itens"]
        items = self.items
        chave, alvo = ci["chave"], ci["objetivo"]
        nomes = [it[chave] for it in items]
        dup = {n for n in nomes if nomes.count(n) > 1}
        if dup:
            raise KBError(f"itens duplicados: {dup}")
        self.kb.var(alvo, nomes, multi=True)
        self._validate_items(items)
        for it in items:
            nome = it[chave]
            for t in ci.get("modelos", []):
                if self._passa_filtro(it, t.get("filtro")):
                    self._template_rule(it, nome, alvo, t)
            for ev in ci.get("evidencias", []):
                if self._passa_filtro(it, ev.get("filtro")):
                    self._evidence_rules(it, nome, alvo, ev)

    def _passa_filtro(self, it, f) -> bool:
        if not f:
            return True
        if isinstance(f, list):
            return all(self._passa_filtro(it, x) for x in f)
        vals = as_list(it[f["coluna"]])
        if "contem" in f:
            return str(f["contem"]) in vals
        if "nao_contem" in f:
            return str(f["nao_contem"]) not in vals
        if "contem_algum" in f:
            return any(str(x) in vals for x in f["contem_algum"])
        if f.get("nao_vazio"):
            return bool(vals)
        if f.get("vazio"):
            return not vals
        if "igual" in f:
            return vals == [str(f["igual"])]
        raise KBError(f"filtro inválido: {f}")

    def _validate_items(self, items):
        ci = self.cfg["itens"]
        cols = {}
        conds = [c for t in ci.get("modelos", []) for c in t["condicoes"]]
        conds += [c for ev in ci.get("evidencias", []) for c in ev.get("condicoes", [])]
        for c in conds:
            if "coluna" in c:
                cols.setdefault(c["coluna"], set()).add(c["var"])
        for ev in ci.get("evidencias", []):
            cols.setdefault(ev["coluna"], set()).add(ev["var"])
        for it in items:
            for col, vars_ in cols.items():
                if col not in it:
                    raise KBError(f"coluna inexistente: {col}")
                for var in vars_:
                    if var not in self.kb.vars:
                        raise KBError(f"variável inexistente nos modelos: {var}")
                    v = self.kb.vars[var]
                    for val in as_list(it[col]):
                        val = self._map(col, val)
                        if v.numeric:
                            float(val)
                        elif val not in v.values:
                            raise KBError(f"{it[ci['chave']]}: valor {val!r} (coluna {col}) "
                                          f"não existe na variável {var!r}")

    def _map(self, col, val):
        return self.cfg["itens"].get("mapas", {}).get(col, {}).get(val, val)

    def _valor_unico(self, it, col) -> str:
        """Valor de {coluna} em condições fixas; colunas de lista não são aceitas."""
        v = it[col]
        if isinstance(v, list):
            raise KBError(f"{it[self.cfg['itens']['chave']]}: {{{col}}} é uma coluna de lista "
                          f"e não pode ser usada como valor único")
        return str(v)

    def _clauses(self, it, conds) -> Optional[List[List]]:
        """Converte condições de modelo em cláusulas (listas de premissas ligadas
        por OU). Retorna None se a regra deve ser descartada para este item."""
        clauses = []
        for c in conds:
            if "apenas_se" in c and not self._passa_filtro(it, c["apenas_se"]):
                continue
            if "se" in c:                                   # condição fixa (DSL)
                # {coluna} é substituído pelo valor do item (ex.: "tempo >= {duracao}")
                txt = re.sub(r"\{(\w+)\}", lambda m: self._valor_unico(it, m.group(1)), c["se"])
                clauses.append(parse_cond(txt))
                continue
            vals = [self._map(c["coluna"], v) for v in as_list(it[c["coluna"]])]
            if not vals:
                if c.get("se_vazio", "pular_regra") == "pular_regra":
                    return None
                continue                                    # pular_condicao
            op = c.get("op", "=")
            if op != "=":                                   # numérica: var op valor_do_item
                if len(vals) > 1:
                    raise KBError(f"{it[self.cfg['itens']['chave']]}: condição {c['var']} {op} "
                                  f"exige um único valor na coluna {c['coluna']}, recebeu {vals}")
                clauses.append([(c["var"], op, vals[0])])
                continue
            alts = list(dict.fromkeys(vals))
            for extra in as_list(c.get("alternativa")):
                alts.append(extra)
            cl: List = []
            for i, a in enumerate(alts):
                if i:
                    cl.append("OU")
                cl.append((c["var"], "=", a))
            clauses.append(cl)
        return clauses

    @staticmethod
    def _join(clauses: List[List]) -> List:
        se: List = []
        for i, cl in enumerate(clauses):
            if i:
                se.append("E")
            se.extend(cl)
        return se

    def _close_simple(self, clauses, rotulo):
        # premissa final simples (evita bug do SINTA com OU no fim da regra)
        idx = next((i for i in range(len(clauses) - 1, -1, -1) if len(clauses[i]) == 1), None)
        if idx is None:
            self.warnings.append(f"{rotulo}: nenhuma condição simples para fechar a regra")
        else:
            clauses.append(clauses.pop(idx))

    def _template_rule(self, it, nome, alvo, t):
        clauses = self._clauses(it, t["condicoes"])
        if clauses is None or not clauses:
            return
        self._close_simple(clauses, f"{nome}/{t['nome']}")
        self.kb.rule(f"{nome} - {t['nome']}", self._join(clauses), [(alvo, nome, t["cnf"])])
        self._count(f"modelo: {t['nome']}")

    def _evidence_rules(self, it, nome, alvo, ev):
        vals = [self._map(ev["coluna"], v) for v in as_list(it[ev["coluna"]])]
        if ev.get("valores_aceitos"):
            vals = [v for v in vals if v in ev["valores_aceitos"]]
        base = []
        if ev.get("prefixo"):
            base.append(parse_cond(ev["prefixo"]))
        extra = self._clauses(it, ev.get("condicoes", []))
        if extra is None:
            return
        base += extra
        cnfs = ev["cnf"] if isinstance(ev["cnf"], list) else [ev["cnf"]]
        rotulo = ev.get("rotulo", ev["nome"])
        for i, v in enumerate(vals[: ev.get("max", len(vals))]):
            cnf = cnfs[min(i, len(cnfs) - 1)]
            clauses = [list(c) for c in base] + [[(ev["var"], "=", v)]]   # termina simples
            self.kb.rule(f"{nome} - {rotulo}: {v}", self._join(clauses), [(alvo, nome, cnf)])
            self._count(f"evidência: {ev['nome']}")

    # ----------------------------------------------------------- objetivos
    def _targets(self):
        for t in self.cfg.get("objetivos", []):
            self.kb.target(t["var"], t.get("mostrar", True))


# ============================================================================
def main(cfg_path: str, quiet: bool = False):
    sys.stdout.reconfigure(encoding="utf-8")
    bld = Builder(cfg_path)
    kb = bld.build()
    out = os.path.normpath(os.path.join(bld.base_dir, bld.cfg["base"]["arquivo_saida"]))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    data = kb.compile()
    if os.path.exists(out):
        os.chmod(out, 0o666)
    open(out, "wb").write(data)
    base = bcm.read_bcm(data)
    stem = os.path.splitext(out)[0]
    open(stem + ".txt", "w", encoding="utf-8").write(bcm.dump(base))
    st = kb.stats()
    st["regras_por_tipo"] = bld.rule_kinds
    st["bytes"] = len(data)
    st["itens"] = len(bld.items)
    st["avisos"] = bld.warnings
    json.dump(st, open(stem + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if not quiet:
        print(f"Base gerada: {out}")
        for k, v in st.items():
            if k not in ("regras_por_tipo", "avisos"):
                print(f"  {k}: {v}")
        print("  regras por tipo:")
        for k, v in bld.rule_kinds.items():
            print(f"    {v:5}  {k}")
        for w in bld.warnings:
            print("  AVISO:", w)
    return out


if __name__ == "__main__":
    main(sys.argv[1])
