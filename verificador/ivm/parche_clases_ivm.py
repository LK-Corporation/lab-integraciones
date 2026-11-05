#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 31: las nuevas que siguen sin ningún mensaje válido de punta a punta al sumar sus muestras públicas llevan «nota_ivm» en
su clase (como la «nota_iv» de la 30, Q-IV-D-13). La clase no cambia si ninguna regla toca su campo (Q-IV-D-6). Las notas salen de
ivm/CRUCE-IVM.json, con la versión que declara cada muestra. Idempotente. Desde fase12:  python3 ivm/parche_clases_ivm.py"""
import collections
import json
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRUCE = json.load(open(os.path.join(FASE, "ivm", "CRUCE-IVM.json"), encoding="utf-8"))
NOTA = "Validador de IRIS sobre las muestras públicas, etapa 31 (ivm/, RESULTADO-IVMUESTRAS.md)"


def versiones(ms):
    c = collections.Counter(m["msh12"] for m in ms)
    if len(ms) == 1:
        return "la %s" % ms[0]["msh12"]
    partes = ["la %s (%d)" % (v, n) for v, n in sorted(c.items(), key=lambda x: (-x[1], x[0]))]
    return partes[0] if len(partes) == 1 else ", ".join(partes[:-1]) + " y " + partes[-1]


notas = {}
for n in CRUCE["nuevas"]:
    if n["con_algun_valido"]:
        continue
    malas = [m for m in n["apoyo_muestras"] if m["estado"] == "invalido_por_otra_regla"]
    reglas = sorted({r for m in malas for r in m["reglas"]})
    k = len(malas)
    campos = ("%s, el campo del hallazgo" % n["campos"][0] if len(n["campos"]) == 1 else
              "%s, los campos del hallazgo" % " ni ".join(n["campos"]))
    sus = "su muestra pública tampoco es válida" if k == 1 else "sus %d muestras públicas tampoco son válidas" % k
    decl = ("La muestra declara %s en MSH-12 y se valida contra v2.5, como la lee el juez (Q-MV-1)" % versiones(malas) if k == 1 else
            "Las muestras declaran en MSH-12 %s, y se validan contra v2.5, como las lee el juez (Q-MV-1)" % versiones(malas))
    notas[n["id"]] = ("%s: %s en v2.5 (por %s), así que su apoyo sigue sin ningún mensaje válido de punta a punta; el del "
                      "laboratorio queda sin decidir, no inválido. %s. Ninguna de esas reglas toca %s, y la clase sigue como "
                      "está (Q-IV-D-6)." % (NOTA, sus, ", ".join(reglas), decl, campos))
for pre, rel in {"VX": "vx/CLASES-VX3.json"}.items():
    p = os.path.join(FASE, rel)
    d = json.load(open(p, encoding="utf-8"))
    vistos = set()
    for c in d["clases"]:
        if c.get("id") in notas:
            assert c.get("clase") == "nueva", c["id"]
            c["nota_ivm"] = notas[c["id"]]
            vistos.add(c["id"])
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("%s: nota_ivm en %s" % (rel, ", ".join(sorted(vistos))))
assert set(notas) <= {"VX-M14", "VX-M15"}, "una nueva fuera de VXU sin ningún válido: ampliar el parche"
print("%d clases con nota_ivm" % len(notas))
