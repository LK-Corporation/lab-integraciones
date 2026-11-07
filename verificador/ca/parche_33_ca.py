#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 36 (ANTES, «Hecho cuando»): marca el resultado de la etapa 33 con lo que se decidió de sus 2 candidatas, como hizo la 28
con el de la 26: una línea bajo el título y la marca donde dice «sin confirmar». Afirma cada texto. Idempotente.
  cd fase12 && python3 ca/parche_33_ca.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(FASE, "RESULTADO-GENERADORES.md")
CAMBIOS = [
    ("# RESULTADO de la etapa 33: los generadores del corpus, arreglados (5-nov-2026)\n\n",
     "# RESULTADO de la etapa 33: los generadores del corpus, arreglados (5-nov-2026)\n\n"
     "**Completado el 7-nov (etapa 36):** las 2 candidatas que este resultado deja sin confirmar son ya declaradas por su proyecto;\n"
     "ninguna es nueva ([`RESULTADO-CANDIDATAS.md`](RESULTADO-CANDIDATAS.md)).\n\n"),
    ("> - Aparecen 2 candidatas, sin confirmar.\n",
     "> - Aparecen 2 candidatas, sin confirmar (la etapa 36 las da por ya declaradas).\n"),
    ("- **Las 2 candidatas** (Q-GA-7: anotadas, sin confirmar):\n",
     "- **Las 2 candidatas** (Q-GA-7: anotadas, sin confirmar; la etapa 36 las da por ya declaradas por su proyecto):\n"),
]
t = open(P, encoding="utf-8").read()
if "**Completado el 7-nov (etapa 36):**" not in t:
    for viejo, nuevo in CAMBIOS:
        assert t.count(viejo) == 1, "no está (o no es único): %r" % viejo[:80]
        t = t.replace(viejo, nuevo)
    open(P, "w", encoding="utf-8").write(t)
print("RESULTADO-GENERADORES.md: las candidatas, con lo de la etapa 36")
