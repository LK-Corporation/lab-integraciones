#!/usr/bin/env python3
"""Etapa 37, cuarto parche de las pruebas (8-nov, tras la segunda pasada de la revisión a ciegas; jz/decision-jev-jz3.md, Q-JZ-9 a),
antes del cuarto parche del juez: P-CV-32 deja de conformarse con la cadena «L-CV-1..17» en cualquier sitio del texto de versión.
Ahora pide una entrada de la etapa 37, la primera, con L-CV-17, y la de la 14l con «L-CV-1..16». Cae con el juez de antes del parche.
  python3 jz/parche_prueba_jz4.py [<carpeta del juez>]"""
import os
import sys

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANTES = '''    mira("la versión del servidor nombra L-CV-17", "L-CV-1..17" in M.REVISION, True)
'''
DESPUES = '''    entradas = M.REVISION.split("; antes, ")          # la etapa más reciente, primero (Q-JZ-9 a)
    mira("la versión del servidor: la primera entrada es la de la etapa 37, con L-CV-17",
         (entradas[0].startswith("etapa 37"), "L-CV-17" in entradas[0]), (True, True))
    mira("la versión del servidor: la entrada de la 14l, con L-CV-1..16",
         [e for e in entradas if e.startswith("14l")][:1] and "L-CV-1..16" in [e for e in entradas if e.startswith("14l")][0], True)
'''


def main(carpeta=AQUI):
    p = os.path.join(carpeta, "prueba_conversion.py")
    t = open(p, encoding="utf-8", newline="").read()
    if DESPUES in t:
        print("prueba_conversion.py: P-CV-32 con las entradas del texto de versión, ya estaba")
        return 0
    if t.count(ANTES) != 1:
        raise SystemExit("prueba_conversion.py: P-CV-32 no está como se espera; no se escribe nada")
    open(p, "w", encoding="utf-8", newline="").write(t.replace(ANTES, DESPUES))
    print("prueba_conversion.py: P-CV-32 con las entradas del texto de versión")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
