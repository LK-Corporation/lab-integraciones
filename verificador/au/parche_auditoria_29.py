#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 29: lo que la auditoría de validez cambia en lo publicado. No se retira ninguna nueva.
- L-15 (LinuxForHealth) se acota a OBX-11 «X»: sin OBX-2, v2.5 solo admite «X» (CH07.txt:2574), y el caso «I» solo salía en
  ORU-B22, que es inválida.
- L-19 (LinuxForHealth) se confirma con un par válido (AU3: «I» frente a «X», sin OBX), porque L10-caso era inválido. Se amplía:
  también «O» y «S» salen «unknown».
- VX-M15 y VX-L8 se confirman con pares válidos (AU1 y AU2).
Idempotente. Se corre con la raíz de los ficheros (fase12, o verificador/ del clon).
  python3 au/parche_auditoria_29.py <raíz>"""
import json
import os
import sys

raiz = sys.argv[1]
NOTA_AU = "Auditoría de validez de la etapa 29 (au/, RESULTADO-AUDITORIA.md)"
CAMBIOS = {
    "cv/RESULTADO-CV3.md": [
        ("| L-15 | LinuxForHealth | Un OBX sin OBX-2 y sin valor (resultado no obtenible «X», o pendiente «I») no da Observation. Va contra la guía "
         "y contra el comentario de su propia plantilla («OBX.2 is null/empty … CREATE») | ORU-B18, B22 |",
         "| L-15 | LinuxForHealth | Un OBX sin OBX-2 y sin valor, con resultado no obtenible («X»), no da Observation. Va contra la guía "
         "y contra el comentario de su propia plantilla («OBX.2 is null/empty … CREATE»). (Acotado en la auditoría de la etapa 29: sin OBX-2, "
         "v2.5 solo admite «X», y el caso «I» solo salía en ORU-B22, que es inválida) | ORU-B18 |"),
        ("| L-19 | LinuxForHealth | OBR-25 «I» se escribe «unknown»; la guía da «registered» | ORU-B22, B31 | `OBR_DiagnosticReport.csv:33`; "
         "CM `table-hl70123` | L10 |",
         "| L-19 | LinuxForHealth | OBR-25 «I» se escribe «unknown»; la guía da «registered». (En la auditoría de la etapa 29, también «O» y «S», "
         "los otros estados sin resultados) | ORU-B22, B31 | `OBR_DiagnosticReport.csv:33`; CM `table-hl70123` | AU3 (etapa 29: «I» frente a "
         "«X»; L10 tenía un caso inválido) |"),
    ],
}
NOTAS = {
    "cv/CLASES-CV3.json": {
        "L-15": {"nota_auditoria": NOTA_AU + ": acotado a OBX-11 «X». Sin OBX-2, v2.5 solo admite «X» (CH07.txt:2574); el caso «I» solo salía en ORU-B22, inválida. Sigue nueva, con ORU-B18 y el par L06. Los campos «casos» y «ejemplos» de arriba son los del estudio y cuentan aún ORU-B22."},
        "L-19": {"nota_auditoria": NOTA_AU + ": L10-caso era inválido (OBR-25 «I» con una OBX final). Se confirma frente al control «X» de AU3, válido: «I» sin OBX da «unknown» y «X» da «cancelled». «O» y «S», pensados como controles, resultaron casos: también dan «unknown», y la guía los lleva a «registered».",
                 "par_valido": "AU3 (au/pares_auditoria.py)"},
    },
    "vx/CLASES-VX3.json": {
        "VX-M15": {"nota_auditoria": NOTA_AU + ": el par VM15 quedó en duda (RE con 0,5 mL, lote y sitio). Se confirma con AU1, válido: RE sin nada administrado.",
                   "par_valido": "AU1 (au/pares_auditoria.py)"},
        "VX-L8": {"nota_auditoria": NOTA_AU + ": el par VL06 llevaba RXA-10 sin XCN-8 ni XCN-9 (CH02A §2.A.86.1), en el campo del hallazgo. Se confirma con AU2, con XCN-9.",
                  "par_valido": "AU2 (au/pares_auditoria.py)"},
    },
}

for rel, cambios in CAMBIOS.items():
    p = os.path.join(raiz, rel)
    t = open(p, encoding="utf-8").read()
    for viejo, nuevo in cambios:
        if nuevo in t:
            continue
        assert t.count(viejo) == 1, "%s: no encuentro %r" % (rel, viejo[:70])
        t = t.replace(viejo, nuevo)
    open(p, "w", encoding="utf-8").write(t)
    print("%s: al día" % rel)

def recorrer(x, ids, extra):
    if isinstance(x, dict):
        if x.get("id") in ids:
            x.update(extra[x["id"]])
            ids.discard(x["id"])
        for v in x.values():
            recorrer(v, ids, extra)
    elif isinstance(x, list):
        for v in x:
            recorrer(v, ids, extra)

p = os.path.join(raiz, "au", "RESULTADO-AU-pares.json")      # AU3: el «confirma» cuenta los tres controles; O y S resultaron casos
if os.path.exists(p):
    pares = json.load(open(p, encoding="utf-8"))
    for x in pares:
        if x["id"] == "AU3":
            x["nota"] = ("confirma=false porque cuenta los tres controles. «O» y «S» resultaron casos: la guía los lleva a «registered», "
                         "como «I», y LinuxForHealth también los da «unknown». Frente al control «X» («cancelled»), el par confirma L-19.")
            x["confirma_frente_a"] = {"x": x["linuxforhealth"]["caso"] and not x["linuxforhealth"]["controles"]["x"]}
    json.dump(pares, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("au/RESULTADO-AU-pares.json: nota de AU3")

for rel, extra in NOTAS.items():
    p = os.path.join(raiz, rel)
    d = json.load(open(p, encoding="utf-8"))
    pendientes = set(extra)
    recorrer(d, pendientes, extra)
    assert not pendientes, (rel, pendientes)
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("%s: notas puestas en %s" % (rel, ", ".join(sorted(extra))))
