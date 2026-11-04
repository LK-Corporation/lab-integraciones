#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 30, Q-IV-D-13 (Jev, decision-jev-qiv12.md: también en las clases, 0,85): la salvedad de cada nueva publicada que no tiene
ningún mensaje de apoyo del laboratorio válido de punta a punta para IRIS. Va como «nota_iv» en su clase (cv/CLASES-CV3.json,
vx/CLASES-VX3.json, md/CLASES-MD3.json), igual que la «nota_auditoria» de la 29. La clase no cambia: IRIS no marca su campo
(Q-IV-D-6). Las notas salen de iv/CRUCE-IV.json, no van a mano. Idempotente. Desde fase12:  python3 iv/parche_clases_iv.py"""
import json
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRUCE = json.load(open(os.path.join(FASE, "iv", "CRUCE-IV.json"), encoding="utf-8"))
VD = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(FASE, "iv", "VEREDICTOS-IV.jsonl"), encoding="utf-8")}
FICHERO = {"CV3": "cv/CLASES-CV3.json", "VX3": "vx/CLASES-VX3.json", "MD3": "md/CLASES-MD3.json"}
NOTA = "Validador de IRIS de la etapa 30 (iv/, RESULTADO-IRISVAL.md)"


QUE = {"RXA-7": "UCUM, fuera de la 0396 de v2.5", "OBX-6": "UCUM, fuera de la 0396 de v2.5",
       "RXR-2": "SCT, fuera de la 0396 de v2.5", "SPM-4": "SCT, fuera de la 0396 de v2.5"}


def nota(n):
    malos = [d for d in n["detalle"] if d["estado"] in ("invalido_por_otra_regla", "no_decidible")]
    reglas = sorted({r for d in malos if d["estado"] == "invalido_por_otra_regla" for r in d.get("reglas", [])})
    inval = sum(1 for d in malos if d["estado"] == "invalido_por_otra_regla")
    nd = len(malos) - inval
    partes = []
    if inval:
        partes.append("%d inválido%s por %s" % (inval, "s" if inval > 1 else "", ", ".join(
            "%s (%s)" % (r, QUE[r]) if r in QUE else "%s (obligatorio vacío)" % r for r in reglas)))
    if nd:
        lugares = {l for d in malos if d["estado"] == "no_decidible" for l in d.get("sin_decidir", [])}
        porque = []
        if any(l.endswith("|0396") for l in lugares):
            valores = sorted({e["valor"] for d in malos for e in VD.get(d["mensaje"], {}).get("no_decidibles", [])
                              if e["lugar"].endswith("|0396")})
            porque.append("%s, fuera de la lista impresa de la 0396, que el texto permite extender (Q-IV-D-11)" % " y ".join(valores))
        if any(l.startswith("L|TXA|3|") for l in lugares):
            porque.append("TXA-3, cuyo valor está en su tabla y no cabe en su LEN (Q-IV-D-12)")
        otros = sorted(l for l in lugares if not l.endswith("|0396") and not l.startswith("L|TXA|3|"))
        if otros:
            porque.append("además %s" % ", ".join(otros))
        partes.append("%d sin decidir por %s" % (nd, "; ".join(porque)))
    campos = ("%s, el campo del hallazgo" % n["campos"][0] if len(n["campos"]) == 1 else
              "%s, los campos del hallazgo" % " ni ".join(n["campos"]))
    au = sorted(os.path.basename(d["mensaje"]).split("-")[0] for d in malos if d["mensaje"].startswith("au-pares/"))
    extra = (" Su par de la etapa 29 (%s), que allí se dio por válido, lo es con la 0396 aparte, como la leyó la 29." % ", ".join(au)
             if au else "")
    return ("%s: ningún mensaje de apoyo del laboratorio es válido de punta a punta en v2.5: %s. Ninguna de esas reglas toca %s, "
            "así que la clase sigue como está (Q-IV-D-6).%s" % (NOTA, "; ".join(partes), campos, extra))


notas = {n["id"]: (n["juez"], nota(n)) for n in CRUCE["nuevas"] if not n["con_algun_apoyo_valido"]}
por_fichero = {}
for i, (juez, texto) in notas.items():
    por_fichero.setdefault(FICHERO[juez], {})[i] = texto
for rel, cambios in sorted(por_fichero.items()):
    p = os.path.join(FASE, rel)
    d = json.load(open(p, encoding="utf-8"))
    vistos = set()
    for c in d["clases"]:
        if c.get("id") in cambios:
            assert c.get("clase") == "nueva", c["id"]
            c["nota_iv"] = cambios[c["id"]]
            vistos.add(c["id"])
    assert vistos == set(cambios), (rel, set(cambios) - vistos)
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("%s: nota_iv en %s" % (rel, ", ".join(sorted(vistos))))
print("%d clases con nota_iv" % len(notas))
