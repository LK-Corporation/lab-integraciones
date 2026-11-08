#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 38 (cl/diseno-cl-fable.md §2, con cl/decision-jev-cl.md, Q-CL-1 a): la regla de M-4 de cv/cv3_clases.py reconoce los dos
textos con que el juez escribe el hallazgo de PL.9 de Microsoft: el de CV3 («falta la descripción») y el de CV4 («… contiene PL.9 …
sin ser PL.9»), y las reglas vecinas siguen dando lo mismo. Sobre hallazgos sintéticos con los textos literales del juez para
A1-A01-03; no lee juicios ni evidencias. Que el cambio no mueve nada más en el estudio lo mide cl/reproducir_clases_cl.py.

  python3 cv/prueba_cv3_clases.py        -> TODO BIEN si no hay ningún MAL"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
mal, n_ok = [], [0]
MS, LFH = "microsoft", "linuxforhealth"
TEXTO_CV3 = "Encounter.location 'UCI^3^1^HOSP^^^^^Box 3': falta la descripción 'Box 3' (PL.9)"
TEXTO_CV4 = "Encounter.location 'UCI^3^1^HOSP^^^^^Box 3': la descripción 'UCI--3--1--HOSP--Box 3' contiene PL.9 'Box 3' sin ser PL.9"


def mira(nombre, obtenido, esperado):
    if obtenido == esperado:
        n_ok[0] += 1
    else:
        print("  MAL %s: %r != %r" % (nombre, obtenido, esperado))
        mal.append(nombre)


def h(hecho, subtipo, q):
    return {"hecho": hecho, "clase": "fidelidad", "subtipo": subtipo, "que": [q]}


def main():
    import cv3_clases as C
    import juzgar_cv2 as J

    def clase(conv, hecho, subtipo, q, caso="A1-A01-03"):
        r = C.regla(conv, J.asignar(h(hecho, subtipo, q), q), q, caso)
        return r[0] if r else None
    mira("P-CL-1 el texto de CV3 es M-4", clase(MS, "PV1-3", "dato_perdido", TEXTO_CV3), "M-4")
    mira("P-CL-2 el texto de CV4 es M-4", clase(MS, "PV1-3", "dato_perdido+valor_distinto", TEXTO_CV4), "M-4")
    mira("P-CL-3 los dos textos, al mismo mecanismo",
         (J.asignar(h("PV1-3", "dato_perdido", TEXTO_CV3), TEXTO_CV3),
          J.asignar(h("PV1-3", "dato_perdido+valor_distinto", TEXTO_CV4), TEXTO_CV4)), ("MC-ADT-3", "MC-ADT-3"))
    mira("P-CL-4 control: la cadena de Location es M-1",
         clase(MS, "PV1-11", "dato_perdido+valor_distinto", "Encounter.location 'QUIROF^1': la cadena de Location no conserva ['1']"), "M-1")
    mira("P-CL-4 control: status observado None es M-3",
         clase(MS, "PV1-3", "dato_perdido+valor_distinto", "Encounter.location 'PLANTA2^201^B^HOSP' status: esperado 'active', observado None",
               "A1-A11-25"), "M-3")
    mira("P-CL-4 control: status esperado es M-2",
         clase(MS, "PV1-11", "dato_perdido+valor_distinto", "Encounter.location 'QUIROF^1' status: esperado 'active', observado 'planned'"), "M-2")
    mira("P-CL-5 control: otro texto de Location no tiene clase",
         clase(MS, "PV1-3", "dato_perdido", "Encounter.location 'X': otra cosa"), None)
    mira("P-CL-6 control: el texto de CV4 en LinuxForHealth no es M-4",
         clase(LFH, "PV1-3", "dato_perdido+valor_distinto", TEXTO_CV4), "L-1")
    formas = {r[0]: type(r[3]).__name__ for r in C.R}
    mira("P-CL-7 cada texto de R es None, una cadena o una tupla de cadenas",
         all(r[3] is None or isinstance(r[3], str) or (isinstance(r[3], tuple) and all(isinstance(t, str) for t in r[3])) for r in C.R),
         True)
    mira("P-CL-7 solo M-4 lleva una tupla", sorted(k for k, v in formas.items() if v == "tuple"), ["M-4"])
    print("PRUEBAS CV3 CLASES: %s (%d comprobaciones)" % ("TODO BIEN" if not mal else "%d MAL" % len(mal), n_ok[0]))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
