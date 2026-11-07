#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 36 (ANTES, condición 4): los pares mínimos de las 2 candidatas de la 33, en ca/pares/, a partir de la versión 2 del corpus.
- Microsoft (la Observation de ACC): un ADT_A01 con ACC (A01-004 de la versión 2) y el mismo sin el segmento ACC.
- LinuxForHealth (PID-8 = S): la copia completada del ejemplo 1 de los veterinarios (cap3-36-A04), con PID-8 = S, = F y = U.
Cada par cambia solo eso (lo afirma). Sale el corpus para la herramienta (--corpus ca/pares --sin-corpus-lab --sin-minimos).
  cd fase12 && python3 ca/pares_ca.py <la carpeta lab/adt del corpus de la versión 2>"""
import os
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADT = sys.argv[1]
SAL = os.path.join(FASE, "ca", "pares")


def segmentos(f):
    t = open(os.path.join(ADT, f), encoding="utf-8", newline="").read()
    return [s for s in t.replace("\r\n", "\r").replace("\n", "\r").split("\r") if s]


def escribir(nombre, segs, msh10):
    segs = list(segs)
    m = segs[0].split("|")
    m[9] = msh10
    segs[0] = "|".join(m)
    open(os.path.join(SAL, nombre + ".hl7"), "w", encoding="utf-8", newline="").write("\r".join(segs) + "\r")


os.makedirs(SAL, exist_ok=True)
con = segmentos("A01-004.hl7")
acc = [s for s in con if s.startswith("ACC|")]
assert len(acc) == 1, acc
sin = [s for s in con if not s.startswith("ACC|")]
assert len(sin) == len(con) - 1
escribir("MS-ACC-con", con, "CA-ACC-CON")
escribir("MS-ACC-sin", sin, "CA-ACC-SIN")

vet = segmentos("cap3-36-A04-completada.hl7")
pid = [i for i, s in enumerate(vet) if s.startswith("PID|")]
assert len(pid) == 1
campos = vet[pid[0]].split("|")
assert campos[8] == "S", campos[8]
for v in ("S", "F", "U"):
    otro = list(vet)
    c = list(campos)
    c[8] = v
    otro[pid[0]] = "|".join(c)
    escribir("LFH-PID8-" + v, otro, "CA-PID8-" + v)
print("ca/pares/: %s" % ", ".join(sorted(os.listdir(SAL))))
