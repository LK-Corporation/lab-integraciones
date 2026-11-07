#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33, tras el segundo lector a ciegas (menor 2): el manual de la herramienta, cv/VC.md, nombra --version-corpus y dice
qué cambia para quien ya la usa. Afirma el texto y que la línea nueva cuadra con lo que junta la herramienta. Idempotente.
  cd fase12 && python3 ga/parche_vc_md.py"""
import os
import sys
import tempfile

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(FASE, "cv"))
import verificar_conversor as V  # noqa: E402

P = os.path.join(FASE, "cv", "VC.md")
ANCLA = "  - `--sin-minimos` quita los 68 mínimos, que solo entran con los dos conversores del estudio;\n"
n = {}
for v in (1, 2):
    for m in (False, True):
        n[v, m] = len(V.generar_corpus(os.path.join(tempfile.mkdtemp(), "c"), lab=True, minimos=m, version=v)["casos"])
assert n == {(1, False): 383, (1, True): 451, (2, False): 390, (2, True): 458}, n
NUEVA = ("  - `--version-corpus 1|2` elige la versión de los generadores del laboratorio. Por omisión es la 2 (etapa 33,\n"
         "    [`../RESULTADO-GENERADORES.md`](../RESULTADO-GENERADORES.md)), que arregla lo que la etapa 30 encontró inválido; con la 1,\n"
         "    la herramienta junta lo de antes, byte a byte. Sin los mínimos, la 1 junta %d casos y la 2, %d; con ellos, %d y %d. Con\n"
         "    una línea base hecha con la 1, una corrida con la 2 sigue pasando en el modo `pasa`: anota los 7 casos nuevos y avisa del\n"
         "    corpus distinto (`corpus_distinto`);\n"
         % (n[1, False], n[2, False], n[1, True], n[2, True]))
t = open(P, encoding="utf-8").read()
if NUEVA not in t:
    assert t.count(ANCLA) == 1, "no encuentro la línea de --sin-minimos"
    t = t.replace(ANCLA, ANCLA + NUEVA)
    open(P, "w", encoding="utf-8").write(t)
print("cv/VC.md: --version-corpus (%s)" % ", ".join("v%d%s=%d" % (v, "+min" if m else "", k) for (v, m), k in sorted(n.items())))
