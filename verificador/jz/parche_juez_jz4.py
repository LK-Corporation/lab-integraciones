#!/usr/bin/env python3
"""Etapa 37, cuarto parche del juez (8-nov, tras la segunda pasada de la revisión a ciegas; jz/decision-jev-jz3.md, Q-JZ-9 a): el
texto de versión del servidor lleva una entrada de la etapa 37, con recurso_sin_mapa y L-CV-17, y la de la 14l vuelve a «L-CV-1..16»
(el tercer parche había puesto L-CV-17 en la entrada de la 14l). No cambia ningún veredicto ni la información del juez; sí su huella.
  python3 jz/parche_juez_jz4.py [<carpeta del juez>]"""
import os
import sys

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMBIOS = [
    ('REVISION = ("etapa de MDM (26): ',
     'REVISION = ("etapa 37: las dos conductas de la etapa 36 en adt_conv y vxu_conv, recurso_sin_mapa (S-CV-5) y L-CV-17; "\n'
     '            "antes, etapa de MDM (26): '),
    ("(S-CV-1..6), L-CV-1..17, ", "(S-CV-1..6), L-CV-1..16, "),
]


def main(carpeta=AQUI):
    p = os.path.join(carpeta, "mcp_verificador.py")
    t = open(p, encoding="utf-8", newline="").read()
    if all(d in t for _, d in CAMBIOS):
        print("mcp_verificador.py: la entrada de la etapa 37, ya estaba")
        return 0
    for a, _ in CAMBIOS:
        if t.count(a) != 1:
            raise SystemExit("mcp_verificador.py: %r no está como se espera; no se escribe nada" % a[:40])
    for a, d in CAMBIOS:
        t = t.replace(a, d)
    open(p, "w", encoding="utf-8", newline="").write(t)
    print("mcp_verificador.py: la entrada de la etapa 37 en el texto de versión; la de la 14l, con L-CV-1..16")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
