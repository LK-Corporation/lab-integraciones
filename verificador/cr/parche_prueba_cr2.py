#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 35, tras la revisión a ciegas (bloqueante 1; menores 2, 3 y 4): añade a cv/ci/prueba_ci.py P-CR-13 (sin push), P-CR-14 (el
remoto avanzó desde otro clon: lo que caza que se lea el remoto y no el clon) y P-CR-15 (entradas raras, argumentos mal puestos,
ningún flujo y dos ensayos del mismo flujo: 2), y comprobaciones a P-CR-2 (el umbral de los commits intermedios), P-CR-5 (el aviso
de otra historia) y P-CR-10 (la fusión con conflictos). Afirma cada texto. Idempotente.  cd fase12 && python3 cr/parche_prueba_cr2.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(FASE, "cv", "ci", "prueba_ci.py")

CAMBIOS = [
    ("P-CR-1..12, la comprobación de después del push", "P-CR-1..15, la comprobación de después del push"),
    ("cr8, cr9, cr10, cr11, cr12]\n", "cr8, cr9, cr10, cr11, cr12,\n           cr13, cr14, cr15]\n"),
    ('    mira("igual, y otro commit", (flujo_de(pub).get("igual"), flujo_de(pub).get("mismo_commit")), (True, False))\n',
     '    mira("igual, y otro commit", (flujo_de(pub).get("igual"), flujo_de(pub).get("mismo_commit")), (True, False))\n'
     '    mira("sin aviso de commits intermedios: uno es lo normal", "commits nuevos" in out, False)\n'),
    ('    mira("el commit es nuevo sobre el mismo árbol", "el commit es nuevo sobre él" in out, True)\n',
     '    mira("el commit es nuevo sobre el mismo árbol", "el commit es nuevo sobre él" in out, True)\n'
     '    mira("avisa de otra historia", "otra historia" in out, True)\n'),
    ('         (0, True, False))\n',
     '         (0, True, False))\n'
     '    escribir(r, "MARCA", "v3 en la rama\\n")\n'
     '    g(r, "commit", "-q", "-am", "la rama choca")\n'
     '    g(r, "checkout", "-q", "main")\n'
     '    escribir(r, "MARCA", "v3 en main\\n")\n'
     '    g(r, "commit", "-q", "-am", "main choca")\n'
     '    empujar(r)\n'
     '    g(r, "checkout", "-q", "rama")\n'
     '    e3 = ens_de(r)\n'
     '    empujar(r, "rama")\n'
     '    rc, out, pub = comprobar(r, [e3], "--rama", "rama", "--base", "main")\n'
     '    mira("la fusión con conflictos: avisa, sin árbol", (rc, "conflictos" in out, ((pub or {}).get("fusion") or {}).get("arbol", "x")),\n'
     '         (0, True, None))\n'),
]
NUEVAS = r'''

def cr13():
    """Sin push: el remoto sigue en el commit de antes; cae, con la ruta, y dice que el clon está en otro commit."""
    r = repo_minimo()
    remoto_para(r)
    empujar(r)
    escribir(r, "MARCA", "v2\n")
    g(r, "add", "MARCA")
    e = ens_de(r)
    g(r, "commit", "-q", "-m", "sin push")
    rc, out, pub = comprobar(r, [e])
    mira("devuelve 1, con la ruta", (rc, flujo_de(pub).get("diferencia")), (1, ["M\tMARCA"]))
    mira("dice que el clon está en otro commit", "el clon está en otro commit" in out, True)


def cr14():
    """El remoto avanzó desde otro clon: trae el commit, y cae con la ruta (lee el remoto, no el clon)."""
    r = repo_minimo()
    b = remoto_para(r)
    empujar(r)
    e = ens_de(r)
    r2 = os.path.join(tmp("cr_otro_clon"), "c")
    subprocess.run(["git"] + GIT_C + ["clone", "-q", b, r2], check=True, capture_output=True)
    escribir(r2, "MARCA", "v2 desde otro clon\n")
    g(r2, "commit", "-q", "-am", "otro clon")
    g(r2, "push", "-q", "origin", "HEAD:refs/heads/main")
    rc, out, pub = comprobar(r, [e])
    mira("devuelve 1, con la ruta", (rc, flujo_de(pub).get("diferencia")), (1, ["M\tMARCA"]))
    mira("el commit publicado no es el del clon", (pub or {}).get("commit") not in (None, g(r, "rev-parse", "HEAD")), True)


def cr15():
    """No se puede comprobar: ENSAYO.json raros, argumentos mal puestos, ningún flujo y dos ensayos del mismo flujo dan 2."""
    r = repo_minimo()
    remoto_para(r)
    empujar(r)
    e = ens_de(r)
    bueno = leer_json(e)
    for nombre, cambio in (("clon no es un objeto", {"clon": "x"}), ("flujo no es un texto", {"flujo": ["mini"]}),
                           ("clon.head no es un texto", {"clon": dict(bueno["clon"], head=7)}),
                           ("como_se_esperaba no es un objeto", {"como_se_esperaba": ["uno"]})):
        raro = escribir_json(os.path.join(tmp("cr_raro"), "ENSAYO.json"), dict(bueno, **cambio))
        rc, out, pub = comprobar(r, [raro])
        mira("%s: 2" % nombre, (rc, "no se pudo" in out), (2, True))
    mira("--jobs-minimos sin «=»: 2", comprobar(r, [e], minimos=("mini",))[0], 2)
    mira("--rama sin valor: 2", comprobar(r, [e], "--rama", minimos=())[0], 2)
    rc, out, pub = comprobar(r, [e], flujos="")
    mira("ningún flujo: 2", (rc, "no hay flujos" in out), (2, True))
    otra = escribir_json(os.path.join(tmp("cr_dos"), "ENSAYO.json"), bueno)
    mira("dos ensayos del mismo flujo: 2", comprobar(r, [e, otra])[0], 2)
'''
ANCLA = "\n\nPRUEBAS = [p01, "

t = open(P, encoding="utf-8").read()
if "def cr13():" not in t:
    for viejo, nuevo in CAMBIOS:
        assert t.count(viejo) == 1, "no está (o no es único): %r" % viejo[:80]
        t = t.replace(viejo, nuevo)
    assert t.count(ANCLA) == 1
    t = t.replace(ANCLA, NUEVAS + ANCLA, 1)
    open(P, "w", encoding="utf-8").write(t)
print("cv/ci/prueba_ci.py: P-CR-13..15, y P-CR-2, 5 y 10 con más comprobaciones")
