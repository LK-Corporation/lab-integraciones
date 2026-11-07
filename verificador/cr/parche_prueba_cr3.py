#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 35, tras la segunda pasada de la revisión a ciegas (menor 3): añade a P-CR-15 de cv/ci/prueba_ci.py dos casos que tienen que
dar 2: -o sobre un fichero que ya existe, y un ENSAYO.json que no se puede leer (solo si el permiso se puede quitar: como root, no).
Se aplica después de cr/parche_prueba_cr2.py. Afirma cada texto. Idempotente.  cd fase12 && python3 cr/parche_prueba_cr3.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(FASE, "cv", "ci", "prueba_ci.py")
VIEJO = '    mira("dos ensayos del mismo flujo: 2", comprobar(r, [e, otra])[0], 2)\n'
NUEVO = VIEJO + (
    '    fichero = os.path.join(tmp("cr_fichero"), "no-es-carpeta")\n'
    '    open(fichero, "w").write("x")\n'
    '    buf = io.StringIO()\n'
    '    with redirect_stdout(buf):\n'
    '        rc = cargar_comprobacion().main([r, e, "--flujos", "mini", "--jobs-minimos", "mini=uno", "-o", fichero])\n'
    '    mira("-o sobre un fichero: 2", (rc, "no se pudo" in buf.getvalue()), (2, True))\n'
    '    no_lee = escribir_json(os.path.join(tmp("cr_no_lee"), "ENSAYO.json"), bueno)\n'
    '    os.chmod(no_lee, 0)\n'
    '    if not os.access(no_lee, os.R_OK):                                  # como root se lee igual, y no hay caso\n'
    '        mira("un ENSAYO.json que no se lee: 2", comprobar(r, [no_lee])[0], 2)\n'
    '    os.chmod(no_lee, 0o644)\n')
t = open(P, encoding="utf-8").read()
if NUEVO not in t:
    assert t.count(VIEJO) == 1, "no encuentro el final de P-CR-15"
    t = t.replace(VIEJO, NUEVO)
    open(P, "w", encoding="utf-8").write(t)
print("cv/ci/prueba_ci.py: P-CR-15 con -o sobre un fichero y un ENSAYO.json que no se lee")
