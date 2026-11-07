#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 35, tras la segunda pasada de la revisión a ciegas (menor 3): en la sección de la comprobación de cv/ci/CI.md, el código 2
también cuando un fichero no se lee o no se escribe. Se aplica después de cr/parche_guia_cr2.py. Afirma el texto. Idempotente.
  cd fase12 && python3 cr/parche_guia_cr3.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(FASE, "cv", "ci", "CI.md")
VIEJO = "  mismo flujo, no hay flujos que comprobar o los argumentos están mal.\n"
NUEVO = "  mismo flujo, no hay flujos que comprobar, los argumentos están mal, o un fichero no se lee o no se escribe.\n"
t = open(P, encoding="utf-8").read()
if NUEVO not in t:
    assert t.count(VIEJO) == 1, "no está (o no es único) el texto del código 2"
    t = t.replace(VIEJO, NUEVO)
    open(P, "w", encoding="utf-8").write(t)
print("cv/ci/CI.md: el código 2, con los ficheros")
