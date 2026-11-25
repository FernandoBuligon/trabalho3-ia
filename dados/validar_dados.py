"""
Valida um CSV de itens contra seu esquema (vocabulário controlado, obrigatoriedade,
listas, duplicatas) e imprime um relatório de cobertura/distribuição.

    python validar_dados.py esquema_famosos.yaml
"""
import csv
import os
import sys
from collections import Counter

import yaml


def carregar(esquema_path):
    esq = yaml.safe_load(open(esquema_path, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(esquema_path))
    rows = list(csv.DictReader(open(os.path.join(base, esq["arquivo"]), encoding="utf-8-sig", newline="")))
    return esq, rows


def validar(esquema_path, verbose=True):
    esq, rows = carregar(esquema_path)
    cols = esq["colunas"]
    erros, avisos = [], []
    chave = esq["chave"]
    header = list(rows[0].keys()) if rows else []
    for c in cols:
        if c not in header:
            erros.append(f"coluna do esquema ausente no CSV: {c}")
    for c in header:
        if c not in cols:
            erros.append(f"coluna do CSV fora do esquema: {c}")

    vistos = Counter(r[chave].strip() for r in rows)
    for k, n in vistos.items():
        if n > 1:
            erros.append(f"item duplicado: {k}")

    def lst(r, c):
        v = (r.get(c) or "").strip()
        if not v:
            return []
        return [x.strip() for x in v.split("|")] if cols[c].get("lista") else [v]

    preench = Counter()
    dist = {c: Counter() for c in cols}
    for r in rows:
        nome = r[chave]
        if None in r:
            erros.append(f"{nome}: colunas a mais na linha")
        for c, spec in cols.items():
            vals = lst(r, c)
            if vals:
                preench[c] += 1
            obrig = spec.get("obrigatoria", False)
            cond = spec.get("obrigatoria_se")
            if cond:
                (cc, cv), = cond.items()
                obrig = cv in lst(r, cc)
            if obrig and not vals:
                erros.append(f"{nome}: coluna obrigatória vazia: {c}")
            if not obrig and cond and vals:
                (cc, cv), = cond.items()
                avisos.append(f"{nome}: {c} preenchida sem ser {cv}")
            if "valores" in spec:
                for v in vals:
                    if v not in [str(x) for x in spec["valores"]]:
                        erros.append(f"{nome}: valor fora do vocabulário em {c}: {v!r}")
            if "numerico" in spec:
                lo, hi = spec["numerico"]
                for v in vals:
                    try:
                        x = float(v)
                        if not lo <= x <= hi:
                            erros.append(f"{nome}: {c}={v} fora de [{lo}, {hi}]")
                    except ValueError:
                        erros.append(f"{nome}: {c} não numérico: {v!r}")
            if len(vals) != len(set(vals)):
                erros.append(f"{nome}: valor repetido em {c}")
            for v in vals:
                dist[c][v] += 1
                if len(v.encode("cp1252")) > 255:
                    erros.append(f"{nome}: valor longo demais em {c}")

    if verbose:
        print(f"Arquivo: {esq['arquivo']}  itens: {len(rows)}")
        print("Preenchimento por coluna:")
        for c in cols:
            print(f"  {c:16} {preench[c]:4}/{len(rows)}  ({100 * preench[c] / max(1, len(rows)):.0f}%)")
        print("Distribuição (colunas com vocabulário):")
        for c, spec in cols.items():
            if "valores" in spec:
                vs = [str(x) for x in spec["valores"]]
                nao_usados = [v for v in vs if dist[c][v] == 0]
                print(f"  {c}: " + ", ".join(f"{v}={dist[c][v]}" for v in vs))
                if nao_usados:
                    avisos.append(f"valores nunca usados em {c}: {nao_usados}")
        for a in avisos:
            print("  AVISO:", a)
        for e in erros:
            print("  ERRO:", e)
        print("RESULTADO:", "VÁLIDO" if not erros else f"{len(erros)} ERRO(S)")
    return erros, avisos, rows


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    erros, _, _ = validar(sys.argv[1])
    sys.exit(1 if erros else 0)
