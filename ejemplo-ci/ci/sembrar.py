#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El proyecto de ejemplo (etapa 24, ejemplo-ci/README.md): siembra en una copia del conversor el defecto del run en rojo
(DEFECTO.json): un reemplazo exacto y único. Sale con 2, sin tocar nada, si el texto no aparece exactamente una vez. Con
--deshacer hace lo contrario. Es verificador/cv/ci/sembrar_juguete.py con el JSON por argumento.
  python3 ejemplo-ci/ci/sembrar.py <fichero> <DEFECTO.json> [--deshacer]"""
import json
import os
import sys


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if len(a) < 2:
        print(__doc__)
        return 2
    ruta, defecto, deshacer = a[0], a[1], "--deshacer" in a[2:]
    s = json.load(open(defecto, encoding="utf-8"))
    de, en = (s["a"], s["de"]) if deshacer else (s["de"], s["a"])
    t = open(ruta, encoding="utf-8", newline="").read()
    n = t.count(de)
    if n != 1:
        print("sembrar: el texto aparece %d veces en %s; no se toca" % (n, os.path.basename(ruta)))
        return 2
    open(ruta, "w", encoding="utf-8", newline="").write(t.replace(de, en))
    print("sembrar: %s %s" % ("deshecho en" if deshacer else "sembrado en", os.path.basename(ruta)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
