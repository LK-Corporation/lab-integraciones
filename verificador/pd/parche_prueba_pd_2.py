#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 40, segundo parche de las pruebas: los dos huecos que dejaron vivos los mutantes del juez (pd/mutantes_pd.py,
pd/MUTANTES-PD.txt). En P-CV-33:
- PD1-7 = X con el código X no da ni una nota de PD1-7 (vivía «nota aunque el código sea el mismo»);
- en 2.8, un PD1-7 con componentes (CWE) se lee por su primer componente (vivía «el campo entero»).
Cada sustitución tiene que darse una sola vez; si no, no se escribe nada. Conserva los finales de línea.
  python3 pd/parche_prueba_pd_2.py [<carpeta>]     (por omisión, la de este laboratorio)"""
import os
import sys

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CV = [
    ("PD1-7 = X con el código X, ni una nota",
     '''    mira("PD1-7 = X, fuera de la 0315, con el código X: nada", cuentan(j(ev(mx, adt_bundle(extra=[obs_pd1("X")])))), [])''',
     '''    r = j(ev(mx, adt_bundle(extra=[obs_pd1("X")])))
    mira("PD1-7 = X, fuera de la 0315, con el código X: nada, ni una nota", (cuentan(r), de_hecho(r, "PD1-7")), ([], []))'''),
    ("PD1-7 con componentes en 2.8",
     '''    mira("2.8 sin Observation: recurso_ausente cuenta igual", cuentan(j(ev(m28, adt_bundle()))), [AUS])''',
     '''    mira("2.8 sin Observation: recurso_ausente cuenta igual", cuentan(j(ev(m28, adt_bundle()))), [AUS])
    r = j(ev(con_pd1(msg(msh={12: "2.8"}), "F^Living will on file^HL70315"), adt_bundle(extra=[obs_pd1()])))
    mira("2.8, PD1-7 con componentes (CWE): se lee su primer componente", (cuentan(r), de_hecho(r, "PD1-7"), de_pd1(r)),
         ([], [], ("PD1-7", "sistema", "urn:uuid:op")))'''),
]


def main(carpeta=AQUI):
    p = os.path.join(carpeta, "prueba_conversion.py")
    t = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in t else "\n"
    hechos = []
    for nombre, antes, despues in CV:
        antes, despues = antes.replace("\n", nl), despues.replace("\n", nl)
        if despues in t:
            continue
        if t.count(antes) != 1:
            raise SystemExit("prueba_conversion.py: %s no está como se espera (%d veces); no se escribe nada" % (nombre, t.count(antes)))
        t = t.replace(antes, despues)
        hechos.append(nombre)
    open(p, "w", encoding="utf-8", newline="").write(t)
    print("prueba_conversion.py: %s" % (", ".join(hechos) if hechos else "ya estaba"))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
