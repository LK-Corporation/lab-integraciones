#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 36, tras la revisión a ciegas: rehace las marcas que ca/parche_33_ca.py puso en el resultado de la etapa 33 con la
clasificación final (Microsoft: M-28, ya declarada; LinuxForHealth: convención), marca también la línea de «no se han confirmado» y
dice el bloque 7 del sello. Se aplica después de ca/parche_33_ca.py. Afirma cada texto. Idempotente.
  cd fase12 && python3 ca/parche_33_ca2.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(FASE, "RESULTADO-GENERADORES.md")
CAMBIOS = [
    ("**Completado el 7-nov (etapa 36):** las 2 candidatas que este resultado deja sin confirmar son ya declaradas por su proyecto;\n"
     "ninguna es nueva ([`RESULTADO-CANDIDATAS.md`](RESULTADO-CANDIDATAS.md)).\n",
     "**Completado el 7-nov (etapa 36):** de las 2 candidatas que este resultado deja sin confirmar, ninguna es nueva. La de\n"
     "Microsoft es M-28, una de las 31 ya declaradas, que el estudio ya contaba en las muestras de Microsoft; la de LinuxForHealth es\n"
     "una convención ([`RESULTADO-CANDIDATAS.md`](RESULTADO-CANDIDATAS.md)). Las cifras de abajo no cambian.\n"),
    ("> - Aparecen 2 candidatas, sin confirmar (la etapa 36 las da por ya declaradas).\n",
     "> - Aparecen 2 candidatas, sin confirmar (la etapa 36: M-28, ya declarada, y una convención).\n"),
    ("- **Las 2 candidatas** (Q-GA-7: anotadas, sin confirmar; la etapa 36 las da por ya declaradas por su proyecto):\n",
     "- **Las 2 candidatas** (Q-GA-7: anotadas, sin confirmar; la etapa 36 da la de Microsoft por M-28, ya declarada, y la de\n"
     "  LinuxForHealth por convención):\n"),
    ("- **Las 2 candidatas no se han confirmado:** ni par mínimo, ni búsqueda en el proyecto, ni revisión adversaria.\n",
     "- **Las 2 candidatas no se han confirmado:** ni par mínimo, ni búsqueda en el proyecto, ni revisión adversaria. (Lo hizo la\n"
     "  etapa 36.)\n"),
    ("el 4, el 5 y el 6, lo que cambió después del 3, tras la segunda pasada de la revisión y tras el segundo lector, cada fichero con su razón |",
     "el 4, el 5 y el 6, lo que cambió después del 3, tras la segunda pasada de la revisión y tras el segundo lector, cada fichero con su razón; el 7, desde la etapa 36, la descripción de M-28 corregida en `cv/cv3_clases.py` |"),
]
t = open(P, encoding="utf-8").read()
if "(la etapa 36: M-28, ya declarada, y una convención)" not in t:
    for viejo, nuevo in CAMBIOS:
        assert t.count(viejo) == 1, "no está (o no es único): %r" % viejo[:80]
        t = t.replace(viejo, nuevo)
    open(P, "w", encoding="utf-8").write(t)
print("RESULTADO-GENERADORES.md: las marcas de la etapa 36, con la clasificación final")
