#!/usr/bin/env python3
"""Etapa 37, segundo parche del juez (después del sello de la previsión): fuera L-CV-18.

L-CV-18 declaraba otro fallo del juez (la Observation que la guía crea desde PD1-7 no se empareja con su campo). Es de fuera de la
etapa (ANTES-ETAPA-JUEZ.md, «Fuera de la etapa»): se dice en RESULTADO-JUEZ.md y no en el juez. No cambia ningún veredicto; sí la
lista de límites que llevan los informes de cada corrida y la huella de INFO (P-MD-25 d).
  python3 jz/parche_juez_jz2.py [<carpeta del juez>]"""
import os
import sys

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANTES = '''recurso_inventado. Los otros 16 segmentos que la hoja lista sin destino no se reconocen.",
        "L-CV-18": "La Observation que la guía crea desde PD1-7 (MSG_ADT_A01.csv:19, «IF PD1-7 VALUED») no se empareja con su campo: "
                   "pasa por una de las de los OBX, por orden, y sin OBX cuenta como recurso_inventado (fallo conocido, fuera de la "
                   "etapa 37)."}'''
DESPUES = '''recurso_inventado. Los otros 16 segmentos que la hoja lista sin destino no se reconocen."}'''


PIN_ANTES = '''# Etapa 37 (7-nov): INFO cambia a propósito (S-CV-5, L-CV-17 y L-CV-18; antes, d8b3a2eb651b1ac4); C y lo demás, igual.
ANTES = {"mdm": "75ab855348d66163", "C": "5dabbc37ec4a7909", "INFO": "a06d3df87c0bd01c",'''
PIN_DESPUES = '''# Etapa 37 (7-nov): INFO cambia a propósito (S-CV-5 y L-CV-17; antes, d8b3a2eb651b1ac4); C y lo demás, igual.
ANTES = {"mdm": "75ab855348d66163", "C": "5dabbc37ec4a7909", "INFO": "3b2cbbf9084ffdc1",'''


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
    cambia(os.path.join(carpeta, "conversion.py"), ANTES, DESPUES, "fuera L-CV-18")
    cambia(os.path.join(carpeta, "prueba_conversion_mdm.py"), PIN_ANTES, PIN_DESPUES, "la huella de INFO sin L-CV-18 (P-MD-25 d)")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
