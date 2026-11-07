#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 34 (en/diseno-en-fable.md §6): la sección del ensayo local en la guía de la CI, cv/ci/CI.md, antes de «Cómo repetirlo en tu
máquina». Las frases del README de las etapas 23 y 24 se quedan como están (DV-EN-2): lo nuevo lo dice la sección de la 34.
Afirma el texto. Idempotente.  cd fase12 && python3 en/parche_guia_en.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(FASE, "cv", "ci", "CI.md")
ANCLA = "## Cómo repetirlo en tu máquina\n"
SECCION = (
    "## Antes de cada push: el ensayo local\n\n"
    "[`ensayo_flujo.py`](ensayo_flujo.py) corre en una máquina los pasos `run:` de un flujo y emula los checkouts **con lo que se\n"
    "va a publicar** (desde la etapa 34):\n"
    "- **un `ref` de 40 hex que está en el clon** se saca con `git archive` de ese commit;\n"
    "- **sin `ref`, o con `github.sha`,** se saca el índice del clon (el HEAD, si coinciden). Lo que no está en el índice no se\n"
    "  ensaya, porque no se publica.\n\n"
    "Con cambios sin `git add` o ficheros sin seguimiento no ensaya nada y sale con 2, con la lista. Puedes añadirlos, apartarlos\n"
    "(`git stash -u`) o ensayar una exportación del índice (`git checkout-index -a --prefix=<carpeta>/`), que se ensaya tal cual.\n\n"
    "La primera línea y la última dicen sobre qué se ensayó: el commit, el árbol del índice o una carpeta sin `.git`.\n"
    "`ENSAYO.json` lo guarda en `clon`. La carpeta de trabajo va fuera del clon.\n\n"
    "Los códigos de salida son 0 si todo sale como se esperaba, 1 si algún job no y 2 si no se ensayó.\n\n"
    "El ensayo no ve lo de siempre: GitHub de verdad, la red, el Docker del runner, los permisos del token y el commit de fusión de\n"
    "un PR. Tampoco ve si el commit fijado está ya en GitHub.\n\n")

t = open(P, encoding="utf-8").read()
if SECCION not in t:
    assert t.count(ANCLA) == 1, "no encuentro «Cómo repetirlo en tu máquina»"
    t = t.replace(ANCLA, SECCION + ANCLA)
    open(P, "w", encoding="utf-8").write(t)
print("cv/ci/CI.md: la sección del ensayo local")
