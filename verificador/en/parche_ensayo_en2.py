#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 34, tras la revisión a ciegas (DV-EN-3): en cv/ci/ensayo_flujo.py, el origen de un renombrado se salta también cuando la
R o la C van en la Y (git add -N), y un HEAD sin commit se dice como es (un clon sin commits o una rama huérfana); el docstring dice
cuándo sale con 1 sin ensayar. Afirma cada texto. Idempotente.  cd fase12 && python3 en/parche_ensayo_en2.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(FASE, "cv", "ci", "ensayo_flujo.py")
CAMBIOS = [
    ("        if x in \"RC\":                                                     # con -z, el origen del renombrado va aparte\n",
     "        if x in \"RC\" or y in \"RC\":                                        # con -z, el origen del renombrado va aparte (DV-EN-3)\n"),
    ("            motivo = \"el clon no tiene commits\"\n",
     "            motivo = \"el HEAD no apunta a ningún commit (un clon sin commits o una rama huérfana)\"\n"),
    ("  Códigos: 0, todo como se esperaba; 1, algún job no; 2, no se ensayó (cambios sin git add, ficheros sin seguimiento o sin commits).",
     "  Códigos: 0, todo como se esperaba; 1, algún job no, o un error del propio ensayo o de git al mirar el clon; 2, no se ensayó por\n"
     "  el estado del clon (cambios sin git add, ficheros sin seguimiento o un HEAD sin commit)."),
]
t = open(P, encoding="utf-8").read()
if "(DV-EN-3)" not in t:
    for viejo, nuevo in CAMBIOS:
        assert t.count(viejo) == 1, "no está (o no es único): %r" % viejo[:80]
        t = t.replace(viejo, nuevo)
    open(P, "w", encoding="utf-8").write(t)
print("cv/ci/ensayo_flujo.py: DV-EN-3")
