#!/usr/bin/env python3
"""Etapa 37, tercer parche de las pruebas (8-nov, tras la revisión a ciegas; jz/decision-jev-jz2.md, Q-JZ-6 b), antes del tercer
parche del juez: P-CV-32 (L-CV-17 dice los dos riesgos de la regla de la 0136, y la versión del servidor nombra L-CV-17) y la
huella de INFO de P-MD-25 (d), medida aplicando jz/parche_juez_jz3.py a una copia. Las dos caen con el juez de antes del parche.
  python3 jz/parche_prueba_jz3.py [<carpeta del juez>]"""
import os
import sys

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P32 = '''

def p32():
    """Etapa 37, tras la revisión a ciegas (jz/decision-jev-jz2.md, Q-JZ-6 b): L-CV-17 dice los dos riesgos de la regla de la 0136,
    y el texto de versión del servidor nombra L-CV-17."""
    import conversion as CV
    import mcp_verificador as M
    l17 = CV.L_CV["L-CV-17"]
    mira("L-CV-17: una Observation de solo Y/N que no sale de ACC ni de PDA (PD1-7, o una inventada) se da por de ellos",
         ("0136" in l17, "PD1-7" in l17, "inventada" in l17), (True, True, True))
    mira("L-CV-17: una de ACC o PDA ya no ocupa el sitio de la de un OBX", "ya no ocupa el sitio de la de un OBX" in l17, True)
    mira("la versión del servidor nombra L-CV-17", "L-CV-1..17" in M.REVISION, True)


PRUEBAS = ['''
LISTA_ANTES = "           p25, p26, p27, p28, p29, p30, p31]\n"
LISTA_DESPUES = "           p25, p26, p27, p28, p29, p30, p31, p32]\n"
PIN_ANTES = '''# Etapa 37 (7-nov): INFO cambia a propósito (S-CV-5 y L-CV-17; antes, d8b3a2eb651b1ac4); C y lo demás, igual.
ANTES = {"mdm": "75ab855348d66163", "C": "5dabbc37ec4a7909", "INFO": "3b2cbbf9084ffdc1",'''
PIN_DESPUES = '''# Etapa 37 (7-nov): INFO cambia a propósito (S-CV-5 y L-CV-17; antes, d8b3a2eb651b1ac4); C y lo demás, igual.
# Y el 8-nov, tras la revisión a ciegas: L-CV-17 con los dos riesgos de la regla de la 0136 (antes, 3b2cbbf9084ffdc1).
ANTES = {"mdm": "75ab855348d66163", "C": "5dabbc37ec4a7909", "INFO": "cbb618aa5d7c14dc",'''


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
    f_cv = os.path.join(carpeta, "prueba_conversion.py")
    cambia(f_cv, "\n\nPRUEBAS = [", P32, "P-CV-32")
    cambia(f_cv, LISTA_ANTES, LISTA_DESPUES, "P-CV-32 en la lista")
    cambia(os.path.join(carpeta, "prueba_conversion_mdm.py"), PIN_ANTES, PIN_DESPUES, "la huella de INFO con L-CV-17 ampliado (P-MD-25 d)")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
