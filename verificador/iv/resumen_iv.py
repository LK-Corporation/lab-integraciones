#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 30: el resumen de FILAS-IV.jsonl, por corpus y por lugar. La variante que manda es la de MSH-9.3 si viene; si no, la de la
0354 (Q-IV-D-2: las dos se publican; aquí se cuenta también cuántas discrepan).
  python3 iv/resumen_iv.py <FILAS-IV.jsonl> [--lugares N]"""
import collections
import json
import sys

F = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
N = int(sys.argv[sys.argv.index("--lugares") + 1]) if "--lugares" in sys.argv else 40


def principal(f):
    v = f["variantes"]
    return v.get("msh93") or v.get("esquema") or v.get("ninguna")


print("%d filas; importadas mal: %d; estructura discrepante: %d; con otros separadores: %d; no ASCII: %d" % (
    len(F), sum(1 for f in F if not f["importado"]["ok"]), sum(1 for f in F if f["doctype_discrepante"]),
    sum(1 for f in F if f["separadores"] != "|^~&"), sum(1 for f in F if f["no_ascii"])))
porc = collections.defaultdict(collections.Counter)
inc, sin, sin0396 = collections.Counter(), collections.Counter(), collections.Counter()
lug, cls, motivos = collections.Counter(), collections.Counter(), collections.Counter()
for f in F:
    v = principal(f)
    porc[f["corpus"]][v["veredicto_que_cuenta"]] += 1
    inc[f["corpus"]] += bool(v["incompleto"])
    sin[f["corpus"]] += bool(v["campos_sin_evaluar"])
    cuentan = [p for p in v["errores"] if p["cuenta"]]
    if cuentan and all(p["clase"] == "T_HL7" and p.get("tabla") == "0396" for p in cuentan):
        sin0396[f["corpus"]] += 1
    for p in v["errores"]:
        cls[(p["clase"], p["cuenta"])] += 1
        if not p["cuenta"]:
            motivos[(p["clase"], (p.get("motivo") or "")[:70])] += 1
        else:
            lug[(p["clase"], p.get("seg"), p.get("campo"), p.get("tabla"), p.get("valor") if p["clase"].startswith("T") else None)] += 1
tot = collections.Counter()
for c in sorted(porc):
    tot.update(porc[c])
    print("  %-14s válidos %3d, inválidos %3d (solo por la 0396: %3d); incompletos %d, con campos sin evaluar %d" % (
        c, porc[c]["valido"], porc[c]["invalido"], sin0396[c], inc[c], sin[c]))
print("  %-14s válidos %3d, inválidos %3d (solo por la 0396: %3d)" % ("TOTAL", tot["valido"], tot["invalido"], sum(sin0396.values())))
print("errores por clase (cuenta): %s" % sorted(cls.items()))
print("lo que no cuenta, por motivo:")
for k, n in motivos.most_common(15):
    print("  %5d %s" % (n, k))
print("lo que cuenta, por lugar (%d distintos):" % len(lug))
for k, n in lug.most_common(N):
    print("  %4d %s" % (n, k))
