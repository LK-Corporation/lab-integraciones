#!/usr/bin/env python3
"""Etapa 37, tercer parche del juez (8-nov, tras la revisión a ciegas; jz/decision-jev-jz2.md, Q-JZ-6 b): L-CV-17 dice los dos
riesgos de la regla de la 0136, y el texto de versión del servidor nombra L-CV-17. No cambia ningún veredicto; sí la información
del juez (la huella de P-MD-25 d) y la huella del juez.
  python3 jz/parche_juez_jz3.py [<carpeta del juez>]"""
import os
import sys

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L17_ANTES = '''recurso_inventado. Los otros 16 segmentos que la hoja lista sin destino no se reconocen."}'''
L17_DESPUES = '''recurso_inventado. Los otros 16 segmentos que la hoja lista sin destino no se reconocen. Dos riesgos de la regla: por la "
                   "0136, una Observation de solo Y/N que no sale de ACC ni de PDA (la de PD1-7, que la guía sí mapea, o una "
                   "inventada) se da por de ellos si el mensaje trae uno con ese valor; y una de ACC o PDA ya no ocupa el sitio de "
                   "la de un OBX, así que, si el conversor saca la de ACC y no la del OBX, cuenta como recurso_sin_mapa (antes pasaba "
                   "por la del OBX, que en ADT no se proyecta)."}'''
REV_ANTES = "(S-CV-1..6), L-CV-1..16, "
REV_DESPUES = "(S-CV-1..6), L-CV-1..17, "


def cambia(p, antes, despues, nombre):
    t = open(p, encoding="utf-8", newline="").read()
    if despues in t:
        print("%s: %s, ya estaba" % (os.path.basename(p), nombre))
        return
    if t.count(antes) != 1:
        raise SystemExit("%s: %s no está como se espera; no se escribe nada" % (os.path.basename(p), nombre))
    open(p, "w", encoding="utf-8", newline="").write(t.replace(antes, despues))
    print("%s: %s" % (os.path.basename(p), nombre))


def main(carpeta=AQUI):
    cambia(os.path.join(carpeta, "conversion.py"), L17_ANTES, L17_DESPUES, "L-CV-17 con los dos riesgos de la regla")
    cambia(os.path.join(carpeta, "mcp_verificador.py"), REV_ANTES, REV_DESPUES, "la versión del servidor nombra L-CV-17")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
