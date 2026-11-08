#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 40, tercer parche de las pruebas (pd/decision-jev-pd2b.md, Q-PD-4 a1), antes que el segundo parche del juez:
- P-CV-33: con PD1-7 = Y y ACC-5 = Y, una sola Observation (v2-0136, Y) es la de PD1-7, con código mal mapeado, y no de ACC (lo que
  ya hace el juez; la revisión a ciegas lo vio sin prueba);
- P-CV-34: L-CV-18 nombra ese caso;
- P-MD-25 (d): la huella de INFO, medida sobre una copia con pd/parche_juez_pd_2.py aplicado.
Cada sustitución tiene que darse una sola vez; si no, no se escribe nada. Conserva los finales de línea.
  python3 pd/parche_prueba_pd_3.py [<carpeta>]     (por omisión, la de este laboratorio)"""
import os
import sys

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CV = [
    ("P-CV-33: una sola (v2-0136, Y)",
     '''    mira("control PD1-7 vacío, ACC-5 = Y y una de solo Y: recurso_sin_mapa ACC, como hoy",''',
     '''    r = j(ev(my, adt_bundle(extra=[obs_sn("o2", "job-related", "Y")])))
    mira("... una sola (v2-0136, Y): es la de PD1-7, con código mal mapeado, y no de ACC (Q-PD-4 a1)", (cuentan(r), de_pd1(r)),
         ([("fidelidad", "codigo_mal_mapeado", "PD1-7")], ("PD1-7", "codigo", "urn:uuid:o2")))
    mira("control PD1-7 vacío, ACC-5 = Y y una de solo Y: recurso_sin_mapa ACC, como hoy",'''),
    ("P-CV-34: L-CV-18 nombra el caso de Q-PD-4",
     '''    mira("L-CV-18 nombra PD1-7, la 0315 y ORU", ("PD1-7" in l18, "0315" in l18, "ORU" in l18), (True, True, True))''',
     '''    mira("L-CV-18 nombra PD1-7, la 0315 y ORU", ("PD1-7" in l18, "0315" in l18, "ORU" in l18), (True, True, True))
    mira("L-CV-18 nombra el caso de Q-PD-4: una de solo Y/N sin el sistema de la 0315, también con el de la 0136, es la de PD1-7",
         ("sin el sistema de la 0315" in l18, "con el de la 0136" in l18, "Q-PD-4" in l18), (True, True, True))'''),
]
MD = [("P-MD-25 d: INFO con L-CV-18 de Q-PD-4",
       '''# 5dabbc37ec4a7909, cbb618aa5d7c14dc y 6fb1b433ac5d4d8f. Lo demás, igual.
ANTES = {"mdm": "75ab855348d66163", "C": "cfd33a3662852137", "INFO": "4fc316780b5e8ded",''',
       '''# 5dabbc37ec4a7909, cbb618aa5d7c14dc y 6fb1b433ac5d4d8f. Lo demás, igual. Y tras la revisión a ciegas (Q-PD-4 a1), INFO otra
# vez, por el texto de L-CV-18 (antes, 4fc316780b5e8ded).
ANTES = {"mdm": "75ab855348d66163", "C": "cfd33a3662852137", "INFO": "ad4d46c08f6702a3",''')]


def aplica(p, cambios):
    t = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in t else "\n"
    hechos = []
    for nombre, antes, despues in cambios:
        antes, despues = antes.replace("\n", nl), despues.replace("\n", nl)
        if despues in t:
            continue
        if t.count(antes) != 1:
            raise SystemExit("%s: %s no está como se espera (%d veces); no se escribe nada" % (os.path.basename(p), nombre, t.count(antes)))
        t = t.replace(antes, despues)
        hechos.append(nombre)
    return t, hechos


def main(carpeta=AQUI):
    salidas = []
    for f, cambios in (("prueba_conversion.py", CV), ("prueba_conversion_mdm.py", MD)):
        p = os.path.join(carpeta, f)
        t, hechos = aplica(p, cambios)
        salidas.append((p, t, hechos))
    for p, t, hechos in salidas:
        open(p, "w", encoding="utf-8", newline="").write(t)
        print("%s: %s" % (os.path.basename(p), ", ".join(hechos) if hechos else "ya estaba"))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
