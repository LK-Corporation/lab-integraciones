#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 34, tras la revisión a ciegas (menores 3 y 4; DV-EN-3): añade a cv/ci/prueba_ci.py P-EN-9 (un renombrado marcado con
git add -N, que git da con la Y en R) y P-EN-10 (una rama huérfana), y tres comprobaciones a P-EN-6 (sin .git: el marcador de
github.sha no avisa, DV-EN-1; la cabecera y la última línea). Se aplica antes del arreglo, para verlas en rojo. Idempotente.
  cd fase12 && python3 en/parche_prueba_en2.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(FASE, "cv", "ci", "prueba_ci.py")

EN6_VIEJO = ('    mira("clon: sin git", clon_de(ens).get("git"), False)\n')
EN6_NUEVO = ('    mira("clon: sin git", clon_de(ens).get("git"), False)\n'
             '    mira("DV-EN-1: el marcador de github.sha no avisa", "no se puede resolver" in out, False)\n'
             '    mira("la cabecera y la última línea lo dicen", ("== la carpeta no tiene .git" in out,\n'
             '         out.strip().splitlines()[-1].startswith("ensayo sobre la carpeta sin .git")), (True, True))\n')
NUEVAS = r'''

def en9():
    """Un renombrado marcado con git add -N (git lo da con la Y en R): para con 2, sin rutas inventadas."""
    r = repo_minimo()
    escribir(r, "x", "un fichero que se renombra, con texto de sobra para que git vea el renombrado\n")
    g(r, "add", "x")
    g(r, "commit", "-q", "-m", "x")
    os.rename(os.path.join(r, "x"), os.path.join(r, "y nuevo.txt"))
    g(r, "add", "-N", "y nuevo.txt")
    rc, out, ens, w, reg = ensayar(r)
    sin_add = clon_de(ens).get("sin_add") or []
    mira("devuelve 2", rc, 2)
    mira("la ruta nueva está, y ninguna inventada", ("y nuevo.txt" in sin_add, set(sin_add) <= {"x", "y nuevo.txt"}), (True, True))


def en10():
    """Una rama huérfana: el HEAD no apunta a ningún commit; para con 2 y lo dice así."""
    r = repo_minimo()
    g(r, "checkout", "-q", "--orphan", "huerfana")
    rc, out, ens, w, reg = ensayar(r)
    mira("devuelve 2", rc, 2)
    mira("lo dice", "el HEAD no apunta a ningún commit" in out, True)
'''
ANCLA_EN8 = '\n\nPRUEBAS = [p01, '
PRUEBAS_VIEJA = "en1, en2, en3, en4, en5, en6, en7, en8]\n"
PRUEBAS_NUEVA = "en1, en2, en3, en4, en5, en6, en7, en8,\n           en9, en10]\n"
DOC_VIEJO = "P-EN-1..8, el ensayo local con lo que se publica"
DOC_NUEVO = "P-EN-1..10, el ensayo local con lo que se publica"

t = open(P, encoding="utf-8").read()
if "def en9():" not in t:
    for viejo, nuevo in ((EN6_VIEJO, EN6_NUEVO), (PRUEBAS_VIEJA, PRUEBAS_NUEVA), (DOC_VIEJO, DOC_NUEVO)):
        assert t.count(viejo) == 1, viejo[:60]
        t = t.replace(viejo, nuevo)
    assert t.count(ANCLA_EN8) == 1
    t = t.replace(ANCLA_EN8, NUEVAS + ANCLA_EN8, 1)
    open(P, "w", encoding="utf-8").write(t)
print("cv/ci/prueba_ci.py: P-EN-9 y 10, y P-EN-6 con tres comprobaciones más")
