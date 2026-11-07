#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 34, tras la revisión a ciegas (menores 5 y 7): en la sección del ensayo local de cv/ci/CI.md (la que pone
en/parche_guia_en.py), lo que pasa con un commit fijado en una exportación, y los códigos de salida como son. Se aplica después de
en/parche_guia_en.py. Afirma cada texto. Idempotente.  cd fase12 && python3 en/parche_guia_en2.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(FASE, "cv", "ci", "CI.md")
CAMBIOS = [
    ("(`git stash -u`) o ensayar una exportación del índice (`git checkout-index -a --prefix=<carpeta>/`), que se ensaya tal cual.\n\n",
     "(`git stash -u`) o ensayar una exportación del índice (`git checkout-index -a --prefix=<carpeta>/`), que se ensaya tal cual.\n"
     "En una exportación no hay commits: un commit fijado, como el del proyecto de ejemplo, no se saca, y se ensaya la carpeta, con\n"
     "un aviso en la línea del checkout. Para ensayar el commit fijado, ensaya el clon.\n\n"),
    ("Los códigos de salida son 0 si todo sale como se esperaba, 1 si algún job no y 2 si no se ensayó.\n\n",
     "Los códigos de salida:\n"
     "- 0, todo sale como se esperaba;\n"
     "- 1, algún job no, o falla el propio ensayo o git al mirar el clon;\n"
     "- 2, no se ensayó por el estado del clon: cambios sin `git add`, ficheros sin seguimiento o un HEAD sin commit.\n\n"),
]
t = open(P, encoding="utf-8").read()
if "Los códigos de salida:\n" not in t:
    assert t.count("## Antes de cada push: el ensayo local\n") == 1, "falta la sección de en/parche_guia_en.py"
    for viejo, nuevo in CAMBIOS:
        assert t.count(viejo) == 1, "no está (o no es único): %r" % viejo[:80]
        t = t.replace(viejo, nuevo)
    open(P, "w", encoding="utf-8").write(t)
print("cv/ci/CI.md: la exportación y los códigos, en la sección del ensayo local")
