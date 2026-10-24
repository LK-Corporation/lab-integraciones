#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CV1-c, auxiliar: imprime como literal de Python los mapas de vocabulario que usa el perfil «guía» (diseño §3.5), leídos de
los ConceptMap del paquete v2-to-FHIR 1.0.0. Uso: python3 cv/extraer_mapas.py <carpeta del paquete>"""
import json
import os
import sys

MAPAS = ["table-hl70001-to-administrative-gender", "table-hl70002-to-v3-maritalstatus", "table-hl70003-to-encounter-status",
         "table-hl70004-to-encounter-status", "table-hl70004-to-v3-actcode", "table-hl70007-to-v2-0007",
         "table-hl70069-to-service-type", "table-hl70136-to-special-values", "table-hl70190-to-address-use",
         "table-hl70190-to-address-type", "table-hl70200-to-name-use", "table-hl70201-to-contact-point-use",
         "table-hl70202-to-contact-point-system", "table-hl70078-to-v3-observationinterpretation",
         "table-hl70085-to-observation-status", "table-hl70123-queries-to-diagnostic-report-status"]


def mapa(carpeta, nombre):
    """{código origen: (system destino, código destino) | None (unmatched/sin destino)}."""
    cm = json.load(open(os.path.join(carpeta, "ConceptMap-%s.json" % nombre), encoding="utf-8"))
    out = {}
    for g in cm.get("group", []):
        for el in g.get("element", []):
            ts = [t for t in el.get("target", []) if t.get("code") and t.get("equivalence") not in ("unmatched", "disjoint")]
            if ts:
                out[el["code"]] = (g.get("target"), ts[0]["code"])
            elif el["code"] not in out:
                out[el["code"]] = None
    return out


def main(carpeta):
    print("# Generado por cv/extraer_mapas.py desde el paquete v2-to-FHIR %s; comprobado por autoprueba() contra el paquete."
          % json.load(open(os.path.join(carpeta, "package.json")))["version"])
    print("MAPAS = {")
    for n in MAPAS:
        print("    %r: %r," % (n, mapa(carpeta, n)))
    print("}")


if __name__ == "__main__":
    main(sys.argv[1])
