#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 40, segundo parche del juez (pd/decision-jev-pd2b.md, Q-PD-4 a1): L-CV-18 nombra el caso que la revisión a ciegas vio sin
declarar. Con PD1-7 en Y o N y ACC o PDA con ese valor, una Observation de solo Y/N sin el sistema de la 0315 (sin sistema, o con el
de la 0136) es la de PD1-7, con código mal mapeado, y no de ACC o PDA. Solo cambia el texto: lo que hace el juez es el mismo.
Cada sustitución tiene que darse una sola vez; si no, no se escribe nada. Conserva los finales de línea.
  python3 pd/parche_juez_pd_2.py [<carpeta del juez>]     (por omisión, la de este laboratorio)"""
import os
import sys

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CV = [("L-CV-18 con el caso de Q-PD-4",
       '''                   "(recurso_inventado, o ACC/PDA por la 0136). Con PD1-7 en Y o N y ACC o PDA con ese valor, dos Observation de solo "
                   "Y/N sin sistema no se distinguen: la primera es la de PD1-7. Solo en ADT: la hoja de ORU también la crea "''',
       '''                   "(recurso_inventado, o ACC/PDA por la 0136). Con PD1-7 en Y o N y ACC o PDA con ese valor, una Observation de "
                   "solo Y/N sin el sistema de la 0315 (sin sistema, o con el de la 0136) es la de PD1-7, con código mal mapeado, y "
                   "no de ACC o PDA (Q-PD-4); si hay dos así, la primera, y la otra sigue la regla de la 0136. Solo en ADT: la hoja "
                   "de ORU también la crea "''')]


def main(carpeta=AQUI):
    p = os.path.join(carpeta, "conversion.py")
    t = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in t else "\n"
    hechos = []
    for nombre, antes, despues in CV:
        antes, despues = antes.replace("\n", nl), despues.replace("\n", nl)
        if despues in t:
            continue
        if t.count(antes) != 1:
            raise SystemExit("conversion.py: %s no está como se espera (%d veces); no se escribe nada" % (nombre, t.count(antes)))
        t = t.replace(antes, despues)
        hechos.append(nombre)
    open(p, "w", encoding="utf-8", newline="").write(t)
    print("conversion.py: %s" % (", ".join(hechos) if hechos else "ya estaba"))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
