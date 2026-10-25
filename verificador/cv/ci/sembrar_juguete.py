#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 23 (cv/ci/diseno-ci-fable.md §4.3, S-CI-12): siembra en el conversor de juguete el defecto del control positivo de la
integración continua (POSITIVO-CI.json): un reemplazo exacto y único. Sale con 2, sin tocar nada, si el texto no aparece
exactamente una vez. Con --deshacer hace lo contrario.
  python3 cv/ci/sembrar_juguete.py <conversor_juguete.py> [--deshacer]"""
import json
import os
import sys

CI_D = os.path.dirname(os.path.abspath(__file__))


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a:
        print(__doc__)
        return 2
    ruta, deshacer = a[0], "--deshacer" in a[1:]
    s = json.load(open(os.path.join(CI_D, "POSITIVO-CI.json"), encoding="utf-8"))
    de, en = (s["a"], s["de"]) if deshacer else (s["de"], s["a"])
    t = open(ruta, encoding="utf-8", newline="").read()
    n = t.count(de)
    if n != 1:
        print("sembrar_juguete: el texto aparece %d veces en %s; no se toca" % (n, os.path.basename(ruta)))
        return 2
    open(ruta, "w", encoding="utf-8", newline="").write(t.replace(de, en))
    print("sembrar_juguete: %s %s" % ("deshecho en" if deshacer else "sembrado en", os.path.basename(ruta)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
