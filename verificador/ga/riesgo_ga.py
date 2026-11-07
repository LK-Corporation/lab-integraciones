#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33, para la previsión B (antes de correr la versión 2): con el juicio de la VERSIÓN 1 (el árbol que arma
cv/ar/arrastre.ensamblar), los casos de cada clase del estudio con la regla de cv3_clases, y cuáles dependen de mensajes que la
versión 2 cambia (los 80 de ADT: 72 de GENADT y 8 de A1). Solo lee la versión 1 y la lista de lo que cambia.
  python3 ga/riesgo_ga.py <juicio.jsonl de la v1> <CORPUS-IV.json v1> <CORPUS-IV.json v2> <salida.json>"""
import collections
import json
import os
import sys

GA = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(GA)
sys.path[:0] = [os.path.join(FASE, "cv"), FASE]
a, sys.argv = sys.argv, ["x", "--silencio"]
import cv3_clases as CL  # noqa: E402
import juzgar_cv2 as J  # noqa: E402
sys.argv = a
JU, C1, C2, SAL = sys.argv[1:5]
s1 = {f["id"]: f["sha256"] for f in json.load(open(C1, encoding="utf-8"))["filas"]}
s2 = {f["id"]: f["sha256"] for f in json.load(open(C2, encoding="utf-8"))["filas"]}
cambia = {os.path.basename(i)[:-4] for i in s1 if i.startswith("lab/adt/") and i in s2 and s1[i] != s2[i]}
uso = collections.defaultdict(lambda: collections.defaultdict(set))
for x in map(json.loads, open(JU, encoding="utf-8")):
    for h in x["cuentan"]:
        for q in h["que"]:
            r = CL.regla(x["conversor"], J.asignar(h, q), q, x["caso"])
            if r:
                uso[r[0]][x["corpus"]].add(x["caso"])
clase = {r[0]: r[5] for r in CL.R}
out = {"cambian": len(cambia), "clases": {}}
for rid, por in sorted(uso.items()):
    todos = {(c, k) for c, ks in por.items() for k in ks}
    afect = {(c, k) for c, k in todos if c == "adt" and k in cambia}
    out["clases"][rid] = {"clase": clase.get(rid), "casos": len(todos), "en_los_que_cambian": len(afect),
                          "todos_en_los_que_cambian": bool(todos) and afect == todos}
out["en_riesgo"] = sorted(k for k, v in out["clases"].items() if v["todos_en_los_que_cambian"])
out["tocadas"] = sorted(k for k, v in out["clases"].items() if v["en_los_que_cambian"] and not v["todos_en_los_que_cambian"])
json.dump(out, open(SAL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("clases con casos en la v1: %d; en riesgo (todos sus casos cambian): %s" % (len(out["clases"]), out["en_riesgo"]))
for k in out["tocadas"]:
    v = out["clases"][k]
    print("  tocada %-8s %-13s %d de %d casos en los que cambian" % (k, v["clase"], v["en_los_que_cambian"], v["casos"]))
