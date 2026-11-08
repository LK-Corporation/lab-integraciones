#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 37: los textos del laboratorio que cambian con el juez nuevo, en su sitio. Afirma cada texto. Idempotente.
- RESULTADO-CANDIDATAS.md (etapa 36), como hizo la 36 con el de la 33: una línea bajo el título y la marca donde dice que el juez
  no cambia.
- cv/ci/CI.md: qué pasa al subir el pin a un commit con otro juez.
  cd fase12 && python3 jz/parche_textos_jz.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMBIOS = {
    "RESULTADO-CANDIDATAS.md": [
        ("# RESULTADO de la etapa 36: las 2 candidatas de la etapa 33 (7-nov-2026)\n\n",
         "# RESULTADO de la etapa 36: las 2 candidatas de la etapa 33 (7-nov-2026)\n\n"
         "**Completado el 8-nov (etapa 37):** el juez deja de contar mal las dos conductas de este resultado\n"
         "([`RESULTADO-JUEZ.md`](RESULTADO-JUEZ.md)). La `S` a `unknown` de LinuxForHealth es ahora una nota de convención, y la\n"
         "Observation de ACC, un «recurso sin mapa».\n\n"),
        ("El hallazgo seguirá saliendo, porque el juez no cambia en\n    esta etapa.\n",
         "El hallazgo seguirá saliendo, porque el juez no cambia en\n    esta etapa (lo arregla la etapa 37).\n"),
        ("- **El juez no cambia en esta etapa** (lo fija el ANTES).\n",
         "- **El juez no cambia en esta etapa** (lo fija el ANTES; lo cambia la etapa 37).\n"),
    ],
    "cv/ci/CI.md": [
        ("otro que suba el pin. Es lo que le pasa a cualquier proyecto.\n",
         "otro que suba el pin. Es lo que le pasa a cualquier proyecto.\n\n"
         "Si el juez del commit nuevo es otro, la comparación lo avisa (`juez_distinto`), y un hallazgo nuevo puede venir del juez y no\n"
         "de tu conversor: lo dice el resultado de la etapa que lo cambió. La 37, por ejemplo, cambió lo que dice de dos conductas\n"
         "([`../../RESULTADO-JUEZ.md`](../../RESULTADO-JUEZ.md)). El ejemplo rehace sus bases en el mismo push que sube el pin.\n"),
    ],
}
for rel, cambios in CAMBIOS.items():
    p = os.path.join(FASE, rel)
    t = open(p, encoding="utf-8", newline="").read()
    hechos = 0
    for viejo, nuevo in cambios:
        if nuevo in t:
            continue
        assert t.count(viejo) == 1, "%s: no está (o no es único): %r" % (rel, viejo[:80])
        t = t.replace(viejo, nuevo)
        hechos += 1
    open(p, "w", encoding="utf-8", newline="").write(t)
    print("%s: %d cambios%s" % (rel, hechos, "" if hechos else " (ya estaban)"))
