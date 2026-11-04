#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 30 (iv/diseno-iv-fable.md §1.4): de qué tipo es cada tabla en el texto de v2.5, y qué valores da el Apéndice A.
- TABLAS-TIPO-IV.json (publicable: solo números y tipo): por tabla, cuántas veces la llama el texto «HL7 Table» y cuántas
  «User-defined Table» (en todos los capítulos y el Apéndice A); el tipo es el del Apéndice A si lo nombra y, si no, el de la
  mayoría; «conflicto» si el texto usa los dos.
- TABLAS-VALORES-IV.json (privado: el texto de HL7 no se redistribuye): los valores de cada tabla en el Apéndice A, sin
  descripciones, para comprobar si un valor que IRIS rechaza está o no en la tabla del estándar.
  python3 tablas_iv.py <carpeta txt de v2.5> <TABLAS-TIPO-IV.json> <TABLAS-VALORES-IV.json>"""
import collections
import glob
import json
import os
import re
import sys

TXT, TIPO, VALORES = sys.argv[1:4]
RX = re.compile(r"(User-defined|HL7)[ -]+[Tt]able +(\d{4})")
cuenta = collections.defaultdict(collections.Counter)
apendice = collections.defaultdict(collections.Counter)
for f in sorted(glob.glob(os.path.join(TXT, "*.txt"))):
    t = open(f, encoding="utf-8", errors="replace").read()
    for m in RX.finditer(t):
        tipo = "HL7" if m.group(1) == "HL7" else "User-defined"
        cuenta[m.group(2)][tipo] += 1
        if os.path.basename(f) == "AppendixA.txt":
            apendice[m.group(2)][tipo] += 1
tipos = {}
for n in sorted(cuenta):
    c, a = cuenta[n], apendice.get(n)
    fuente = a if a else c
    tipo = fuente.most_common(1)[0][0]
    tipos[n] = {"tipo": tipo, "HL7": c["HL7"], "User-defined": c["User-defined"], "conflicto": len(c) > 1,
                "decide": "apendice_a" if a else "mayoria"}
json.dump({"origen": "texto de HL7 v2.5 (todos los capítulos y el Apéndice A): solo el número de tabla y su tipo",
           "tablas": tipos}, open(TIPO, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
# valores: las filas «    NNNN      VALOR      descripción» del Apéndice A, partidas por dos o más espacios. Un valor puede traer
# alternativas («99zzz or L») y comodines en minúscula: nnnn (cuatro dígitos) y zzz (alfanuméricos), que se guardan como patrón.
valores = collections.defaultdict(set)
patrones = collections.defaultdict(set)
RXV = re.compile(r"^\s+(\d{4})\s{2,}(\S.*)$")
for l in open(os.path.join(TXT, "AppendixA.txt"), encoding="utf-8", errors="replace"):
    m = RXV.match(l.rstrip("\n"))
    if not m:
        continue
    partes = re.split(r"\s{2,}", m.group(2).strip())
    for v in partes[0].split(" or "):
        v = v.strip()
        if not v or " " in v:
            continue
        if re.search(r"n{2,}|z{2,}", v) and re.fullmatch(r"[A-Z0-9+]*(n+|z+)[A-Z0-9+]*", v):
            patrones[m.group(1)].add("^" + re.sub(r"z+", lambda x: "[A-Za-z0-9]{%d}" % len(x.group(0)),
                                                  re.sub(r"n+", lambda x: r"\d{%d}" % len(x.group(0)), re.escape(v))) + "$")
        else:
            valores[m.group(1)].add(v)
json.dump({"valores": {n: sorted(v) for n, v in sorted(valores.items())},
           "patrones": {n: sorted(v) for n, v in sorted(patrones.items())}},
          open(VALORES, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("tipos: %d tablas (%d HL7, %d de usuario, %d con conflicto); valores: %d tablas, %d valores, %d patrones"
      % (len(tipos), sum(1 for x in tipos.values() if x["tipo"] == "HL7"), sum(1 for x in tipos.values() if x["tipo"] != "HL7"),
         sum(1 for x in tipos.values() if x["conflicto"]), len(valores), sum(len(v) for v in valores.values()),
         sum(len(v) for v in patrones.values())))
for n in ("0001", "0003", "0076", "0085", "0103", "0361", "0396", "0200", "0203", "0191"):
    print("  %s: %s, valores %d %s, patrones %s" % (n, tipos.get(n, {}).get("tipo"), len(valores.get(n, ())),
                                                    sorted(valores.get(n, ()))[:6], sorted(patrones.get(n, ()))))
print("  0396 tiene L: %s, LN: %s, UCUM: %s" % ("L" in valores["0396"], "LN" in valores["0396"], "UCUM" in valores["0396"]))
