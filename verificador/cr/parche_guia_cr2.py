#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 35, tras la revisión a ciegas (menores 3 y 8): en la sección de la comprobación de cv/ci/CI.md (la que pone
cr/parche_guia_cr.py), cuándo se listan las rutas y todos los casos del código 2. Se aplica después de cr/parche_guia_cr.py. Afirma
cada texto. Idempotente.  cd fase12 && python3 cr/parche_guia_cr2.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(FASE, "cv", "ci", "CI.md")
VIEJO = ("- **Sale con 1** si falta un ensayo, si no ensayó nada o no dice su árbol, si le faltan jobs o si ensayó otro árbol. Entonces\n"
         "  lista las rutas que difieren y la orden para re-ensayar ese flujo.\n"
         "- **Sale con 2** si no pudo leer el remoto.\n")
NUEVO = ("- **Sale con 1** si falta un ensayo, si no ensayó nada o no dice su árbol, si le faltan jobs o si ensayó otro árbol. Entonces\n"
         "  da la orden para re-ensayar ese flujo, y lista las rutas que difieren si el árbol ensayado sigue en el clon.\n"
         "- **Sale con 2** si no pudo comprobar: el remoto o la rama no se leen, un `ENSAYO.json` no es válido, hay dos ensayos del\n"
         "  mismo flujo, no hay flujos que comprobar o los argumentos están mal.\n")
t = open(P, encoding="utf-8").read()
if NUEVO not in t:
    assert t.count("## Después del push: la comprobación\n") == 1, "falta la sección de cr/parche_guia_cr.py"
    assert t.count(VIEJO) == 1, "no está (o no es único) el texto de los códigos"
    t = t.replace(VIEJO, NUEVO)
    open(P, "w", encoding="utf-8").write(t)
print("cv/ci/CI.md: los códigos de la comprobación")
