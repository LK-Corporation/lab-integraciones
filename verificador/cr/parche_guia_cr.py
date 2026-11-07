#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 35 (cr/diseno-cr-fable.md §7, con las decisiones de Jev): en cv/ci/CI.md, la sección «Después del push: la comprobación»,
antes de «Cómo repetirlo en tu máquina», y una frase al final de lo que el ensayo no ve. Se aplica después de en/parche_guia_en.py y
en/parche_guia_en2.py. Afirma cada texto. Idempotente.  cd fase12 && python3 cr/parche_guia_cr.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(FASE, "cv", "ci", "CI.md")
NO_VE_VIEJO = "un PR. Tampoco ve si el commit fijado está ya en GitHub.\n\n"
NO_VE_NUEVO = ("un PR. Tampoco ve si el commit fijado está ya en GitHub. Lo que se publique después del ensayo lo mira la comprobación de\n"
               "la sección siguiente.\n\n")
ANCLA = "## Cómo repetirlo en tu máquina\n"
SECCION = (
    "## Después del push: la comprobación\n\n"
    "El ensayo no sabe qué se publicó después: un `git add` o un `commit --amend` posteriores cambian el árbol sin aviso.\n"
    "[`comprobar_publicado.py`](comprobar_publicado.py) cierra el círculo (desde la etapa 35). Lee el commit que el remoto tiene\n"
    "(`git ls-remote`), saca su árbol y lo compara con el que cada `ENSAYO.json` dice haber ensayado.\n\n"
    "```bash\n"
    "python3 cv/ci/comprobar_publicado.py <clon> <ENSAYO.json de la demo> <del ejemplo> <del rojo> [--rama main] [-o <carpeta>]\n"
    "```\n\n"
    "- **Sale con 0** si los tres flujos tienen un ensayo de sus jobs sobre el árbol publicado.\n"
    "- **Sale con 1** si falta un ensayo, si no ensayó nada o no dice su árbol, si le faltan jobs o si ensayó otro árbol. Entonces\n"
    "  lista las rutas que difieren y la orden para re-ensayar ese flujo.\n"
    "- **Sale con 2** si no pudo leer el remoto.\n"
    "- **Un ensayo en rojo** sobre el árbol publicado da un aviso, no un 1.\n\n"
    "El commit no cuenta, el árbol sí. Un amend que solo cambia el mensaje pasa. Un push de varios commits pasa si la cabeza es el\n"
    "árbol ensayado, con un aviso por los intermedios, que GitHub no corre.\n\n"
    "En un PR, compruébalo sobre la rama (`--rama <rama>`). Con `--base main` prevé el árbol del commit de fusión con\n"
    "`git merge-tree`, y avisa si `main` avanzó, porque ese árbol no está ensayado. Después de fusionar, compruébalo sobre `main` con\n"
    "los mismos `ENSAYO.json`.\n\n"
    "La comprobación no ve:\n"
    "- si los `ENSAYO.json` son los últimos: un ensayo viejo sobre el mismo árbol pasa, porque el árbol es el contenido;\n"
    "- el commit de fusión real de un PR;\n"
    "- nada de lo que pasa en el runner.\n\n"
    "`PUBLICADO.json` guarda lo comparado.\n\n")

t = open(P, encoding="utf-8").read()
if SECCION not in t:
    assert t.count("## Antes de cada push: el ensayo local\n") == 1, "falta la sección del ensayo (etapa 34)"
    for viejo, nuevo in ((NO_VE_VIEJO, NO_VE_NUEVO), (ANCLA, SECCION + ANCLA)):
        assert t.count(viejo) == 1, "no está (o no es único): %r" % viejo[:60]
        t = t.replace(viejo, nuevo)
    open(P, "w", encoding="utf-8").write(t)
print("cv/ci/CI.md: la comprobación de después del push")
