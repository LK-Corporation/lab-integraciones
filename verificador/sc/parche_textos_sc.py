#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 39 (sc/diseno-sc-fable.md §5): las marcas, sin reescribir lo sellado, en el laboratorio (sus copias públicas son iguales y se
copian). Afirma cada texto. Idempotente.
- RESULTADO-CANDIDATAS.md (36): desde la 39, M-28 mira el corpus del laboratorio.
- RESULTADO-GENERADORES.md (33): con el juez y el aparato de hoy, la versión 2 da 0 sin clase y 17 convenciones.
- RESULTADO-CLASES.md (38): el cabo de lo sin clase, cerrado.
  cd fase12 && python3 sc/parche_textos_sc.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMBIOS = {
    "RESULTADO-CANDIDATAS.md": [
        ("  - La etapa 33 la vio como candidata porque los 30 ADT con ACC son del corpus del laboratorio, que M-28 no miraba.\n",
         "  - La etapa 33 la vio como candidata porque los 30 ADT con ACC son del corpus del laboratorio, que M-28 no miraba.\n"
         "    *Desde la etapa 39 (8-nov) los mira: con el juez de hoy, los 30 caen en M-28\n"
         "    ([`RESULTADO-SINCLASE.md`](RESULTADO-SINCLASE.md)).*\n"),
    ],
    "RESULTADO-GENERADORES.md": [
        ("una convención ([`RESULTADO-CANDIDATAS.md`](RESULTADO-CANDIDATAS.md)). Las cifras de abajo no cambian.\n\n",
         "una convención ([`RESULTADO-CANDIDATAS.md`](RESULTADO-CANDIDATAS.md)). Las cifras de abajo no cambian.\n\n"
         "**Y el 8-nov (etapa 39):** con el juez y el aparato de hoy, la versión 2 da 0 hallazgos sin clase y 17 convenciones. La\n"
         "decimoséptima es la de LinuxForHealth con PID-8 fuera de la 0001, que la etapa 36 dio por convención y la 37 llevó al juez. Las\n"
         "cifras de abajo (16 convenciones y 2 candidatas) son las del juez y el aparato de entonces\n"
         "([`RESULTADO-SINCLASE.md`](RESULTADO-SINCLASE.md)).\n\n"),
    ],
    "RESULTADO-CLASES.md": [
        ("  etapas; queda fuera de esta. Desde esta etapa, `cl/reproducir_clases_cl.py` guarda lo que queda sin clase.\n",
         "  etapas; queda fuera de esta. Desde esta etapa, `cl/reproducir_clases_cl.py` guarda lo que queda sin clase.\n"
         "  *Etapa 39 (8-nov):* el aparato ya lo cuenta en su salida (`n_sin_clase`) y avisa al final, sin fallar\n"
         "  ([`RESULTADO-SINCLASE.md`](RESULTADO-SINCLASE.md)).\n"),
    ],
}
VIEJO_GEN = ("cifras de abajo (16 convenciones y 2 candidatas) son las del juez de entonces ([`RESULTADO-SINCLASE.md`](RESULTADO-SINCLASE.md)).\n")
NUEVO_GEN = ("cifras de abajo (16 convenciones y 2 candidatas) son las del juez y el aparato de entonces\n"
             "([`RESULTADO-SINCLASE.md`](RESULTADO-SINCLASE.md)).\n")   # tras la revisión a ciegas: con el juez de hoy y el aparato viejo, 1
for rel, cambios in CAMBIOS.items():
    p = os.path.join(FASE, rel)
    t = open(p, encoding="utf-8", newline="").read()
    if rel == "RESULTADO-GENERADORES.md" and VIEJO_GEN in t:
        t = t.replace(VIEJO_GEN, NUEVO_GEN)
    for viejo, nuevo in cambios:
        if nuevo in t:
            continue
        assert t.count(viejo) == 1, "%s: no está (o no es único): %r" % (rel, viejo[:70])
        t = t.replace(viejo, nuevo)
    open(p, "w", encoding="utf-8", newline="").write(t)
    print("%s: marca de la etapa 39" % rel)
