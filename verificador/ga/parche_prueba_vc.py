#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33 (la segunda pasada de la revisión, menor 6): las pruebas de la herramienta miran también la versión 2 del corpus, la
que usa la línea de órdenes por omisión: 270 ADT, y 390 casos sin los mínimos y 458 con ellos (los de cv/ci/LINEA-BASE-*.json).
La función que junta el corpus sigue en la 1 por omisión (P10), y las comprobaciones de la 1 no cambian.
  cd fase12 && python3 ga/parche_prueba_vc.py"""
import os

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cv", "prueba_vc.py")
t = open(P, encoding="utf-8").read()
VIEJO = ('    mira("sin mínimos", sum(VC.generar_corpus(c3, lab=True, minimos=False)["n"].values()), 383)       '
         '# DV-VX-5: 303 + 40 de VXU; + 40 de MDM\n')
NUEVO = VIEJO + (
    '    c4 = os.path.join(tmp("corpus"), "c")                                   # etapa 33: la versión 2 (ga/), la de la línea de órdenes\n'
    '    n2 = VC.generar_corpus(c4, lab=True, minimos=True, version=2)["n"]\n'
    '    mira("versión 2: n", n2, {"adt": 270, "oru": 40, "vxu": 40, "minimos": 68, "muestras": 0, "propio": 0, "mdm": 40})\n'
    '    mira("versión 2: sin mínimos y con ellos", (sum(n2.values()) - n2["minimos"], sum(n2.values())), (390, 458))\n')
if NUEVO not in t:
    assert t.count(VIEJO) == 1, "no está la línea de «sin mínimos»"
    open(P, "w", encoding="utf-8").write(t.replace(VIEJO, NUEVO))
print("parcheado:", P)
