#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 26, MD3: la lista numerada de los hallazgos que cuentan en MDM (H-n), por conversor y mecanismo (hecho sin índice,
subtipo), con las bases y las muestras donde salen y un ejemplo del «que». PV1 y PID quedan fuera: son el perfil de adt_conv
y los clasificó el estudio de conversores (cv/CLASES-CV3.json), como en VXU («fuera_de_vxu»). Es la entrada del contraste, de la
revisión adversaria y de los pares mínimos.
  python3 md/hallazgos_md3.py <corrida de las bases> <corrida de las muestras> -o <json>"""
import collections
import json
import os
import re
import sys

FUERA = re.compile(r"^(PV1|PID)-")


def leer(corrida, corpus):
    out = {}
    for c in ("microsoft", "linuxforhealth"):
        filas = [json.loads(l) for l in open(os.path.join(corrida, c, "juicio.jsonl"), encoding="utf-8")]
        out[c] = [f for f in filas if f["corpus"] == corpus and f.get("punto") == "mdm_conv"]
    return out


def main(bases, muestras, salida):
    grupos = collections.OrderedDict()
    fuera = collections.Counter()
    for origen, filas in (("bases", leer(bases, "mdm")), ("muestras", leer(muestras, "muestras"))):
        for c, fs in filas.items():
            for f in fs:
                for h in f.get("cuentan") or []:
                    hecho = re.sub(r"\(\d+\)", "", h.get("hecho") or "")
                    if FUERA.match(hecho):
                        fuera[(c, hecho, h.get("subtipo"))] += 1
                        continue
                    k = (c, hecho, h.get("subtipo"))
                    g = grupos.setdefault(k, {"conversor": c, "hecho": hecho, "subtipo": h.get("subtipo"), "bases": [], "muestras": [],
                                              "ejemplos": []})
                    g[origen].append(f["caso"])
                    q = h.get("que")
                    q = q[0] if isinstance(q, list) and q else q
                    if q and len(g["ejemplos"]) < 3 and q not in g["ejemplos"]:
                        g["ejemplos"].append(str(q)[:300])
    lista = []
    for i, g in enumerate(sorted(grupos.values(), key=lambda g: (g["conversor"], -len(set(g["bases"])), g["hecho"])), 1):
        g["id"] = "H%d" % i
        g["bases"], g["muestras"] = sorted(set(g["bases"])), sorted(set(g["muestras"]))
        lista.append(g)
    json.dump({"_que": __doc__.split("\n")[0], "hallazgos": lista,
               "fuera_de_mdm": [{"conversor": c, "hecho": h, "subtipo": s, "n": n} for (c, h, s), n in sorted(fuera.items())]},
              open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for g in lista:
        print("%-4s %-15s %-12s %-28s bases %2d muestras %2d" % (g["id"], g["conversor"], g["hecho"], g["subtipo"], len(g["bases"]), len(g["muestras"])))
    print("fuera de MDM (PV1, PID):", sum(fuera.values()), "hallazgos en", len(fuera), "mecanismos")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[sys.argv.index("-o") + 1])
