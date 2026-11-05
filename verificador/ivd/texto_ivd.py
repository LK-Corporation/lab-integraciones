#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 32 (ANTES-ETAPA-IVDECLARADA.md, Q-VD-2): leer el texto de una versión con los analizadores de la 30 y la 31.
- atributos(txt): las tablas de atributos («HL7 Attribute Table - SEG»), con el mismo patrón de fila que iv/lectura_iv.py.
- segmentos_definidos(txt): los segmentos con tabla de atributos (Q-MV-4), con el mismo patrón que ivm/validar_ivm.py.
- est(txt, base): la tabla de campos del conductor (el formato de estructuras_25.json) para los mismos segmentos que trae `base`,
  con la LEN y la OPT del texto.
Un cambio frente al patrón de la 30: el tipo de dato admite «varies» (y «varie», como sale cortado en el texto). Sin él, la fila de
OBX-5 no casa y OBX-5 se queda con la de una tabla de ejemplo de más abajo (CH07.txt:7624 en v2.5: TS, 26, R). En la 30 y la 31
no hubo ningún error en OBX-5.
- segmentos_definidos sigue contando también las cabeceras de las tablas de ejemplo, como la 31: solo nombran segmentos que el
  texto ya define.
El texto de v2.5.1 se lee por la carpeta de enlaces que hace ivd/hacer_vista_251.sh (los nombres de fichero de v2.5)."""
import glob
import os
import re

FILA = re.compile(r"^\s+(\d+)\s+(\d+)\s+([A-Z][A-Z0-9]{1,2}|varies|varie)\s+((?:\(B\)\s*)?(?:R|O|C|B|X|W|RE))\b(.*)$")
CABECERA = re.compile(r"HL7 Attribute Table\s*[-–]\s*([A-Z][A-Z0-9]{2})\b")


def atributos(txt):
    atr = {}
    for f in sorted(glob.glob(os.path.join(txt, "*.txt"))):
        seg = None
        for n, l in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
            m = CABECERA.search(l)
            if m:
                seg = m.group(1)
                atr.setdefault(seg, {})
                continue
            if seg:
                m = FILA.match(l)
                if m:
                    tbl = re.search(r"\b(\d{4})\b", m.group(5))
                    atr[seg].setdefault(int(m.group(1)), {"len": int(m.group(2)), "dt": m.group(3),
                                                          "opt": re.sub(r"\s+", " ", m.group(4)),
                                                          "tbl": tbl.group(1) if tbl else None,
                                                          "cita": "%s:%d" % (os.path.basename(f), n)})
                elif re.match(r"^\s*\d+\.\d+", l) and atr[seg]:
                    seg = None
    return atr


def segmentos_definidos(txt):
    s = set()
    for f in sorted(glob.glob(os.path.join(txt, "*.txt"))):
        for l in open(f, encoding="utf-8", errors="replace"):
            m = CABECERA.search(l)
            if m:
                s.add(m.group(1))
    return s


def est(txt, base):
    atr = atributos(txt)
    out = {}
    for seg in base:
        a = atr.get(seg) or {}
        out[seg] = {"atributos": {"%s-%d" % (seg, q): {"dt": x["dt"], "len": x["len"], "opt": x["opt"], "tabla": x["tbl"]}
                                  for q, x in sorted(a.items())},
                    "fuente": "texto de la versión (%s)" % (min((x["cita"] for x in a.values()), default="sin tabla"))}
    return out
