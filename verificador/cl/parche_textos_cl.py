#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 38 (cl/diseno-cl-fable.md §4): las marcas, sin reescribir lo sellado, en su sitio. Afirma cada texto. Idempotente.
- RESULTADO-CONVERSORES.md: una nota junto a «M-4 es ya declarada en los dos jueces».
- RESULTADO-JUEZ.md (etapa 37): una línea en «Lo que se vio de paso», donde dice que tres clases no dan sus casos.
Sin argumentos, en el laboratorio; con el clon público, en sus copias (verificador/…), que en RESULTADO-CONVERSORES.md llevan una
parte redactada: por eso se parchea en su sitio y no se copia.
  cd fase12 && python3 cl/parche_textos_cl.py [<clon público>]"""
import os
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = sys.argv[1] if len(sys.argv) > 1 else None
CAMBIOS = {
    "RESULTADO-CONVERSORES.md": [
        ("Ninguna discrepancia nueva aparece ni desaparece: M-36 y L-24 ya estaban apartadas, y M-4 es ya declarada en los dos jueces.\n"
         "**La frase no cambia.**\n",
         "Ninguna discrepancia nueva aparece ni desaparece: M-36 y L-24 ya estaban apartadas, y M-4 es ya declarada en los dos jueces.\n"
         "**La frase no cambia.**\n\n"
         "> *Etapa 38 (8-nov-2026): de la clase, es cierto; del aparato, se quedaba corto. Con el juez de CV4, la regla de M-4 de\n"
         "> `cv/cv3_clases.py` reconocía 8 de sus 16 hallazgos, y los otros 8 quedaban sin clase. Desde la etapa 38 los reconoce todos\n"
         "> ([`RESULTADO-CLASES.md`](RESULTADO-CLASES.md)).*\n"),
    ],
    "RESULTADO-JUEZ.md": [
        ("  La frase es la misma. Queda fuera de la etapa.\n",
         "  La frase es la misma. Queda fuera de la etapa.\n\n"
         "  *Etapa 38 (8-nov):* la causa está medida en [`RESULTADO-CLASES.md`](RESULTADO-CLASES.md). En M-4, el juez de CV4 y la\n"
         "  regla de `cv/cv3_clases.py`, que no reconocía su texto: 8 hallazgos sin clase, también en `jz/CLASES-JZ-*.json`. En M-36 y\n"
         "  L-24, el juez de CV4. Los `jz/CLASES-JZ-*.json` se quedan como se escribieron.\n"),
    ],
}
VIEJO_JUEZ = ("  *Etapa 38 (8-nov):* la causa está medida en [`RESULTADO-CLASES.md`](RESULTADO-CLASES.md). En M-4, la regla de\n"
              "  `cv/cv3_clases.py`, que no reconocía el texto del juez de CV4: 8 hallazgos sin clase, también en `jz/CLASES-JZ-*.json`. En\n"
              "  M-36 y L-24, el juez de CV4. Los `jz/CLASES-JZ-*.json` se quedan como se escribieron.\n")   # la primera redacción (revisión)
for rel, cambios in CAMBIOS.items():
    p = os.path.join(PUB, "verificador", rel) if PUB else os.path.join(FASE, rel)
    t = open(p, encoding="utf-8", newline="").read()
    if rel == "RESULTADO-JUEZ.md" and VIEJO_JUEZ in t:
        t = t.replace(VIEJO_JUEZ, cambios[0][1][len(cambios[0][0]) + 1:])
    for viejo, nuevo in cambios:
        if nuevo in t:
            continue
        assert t.count(viejo) == 1, "%s: no está (o no es único): %r" % (rel, viejo[:70])
        t = t.replace(viejo, nuevo)
    open(p, "w", encoding="utf-8", newline="").write(t)
    print("%s: marca de la etapa 38" % p)
