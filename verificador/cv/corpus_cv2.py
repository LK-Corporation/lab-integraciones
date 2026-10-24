#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CV2: el corpus de la etapa de conversores, en ficheros .hl7 (uno por mensaje), con su manifiesto y su huella.
  - adt/: las 263 entradas de A1 (E2 216 + ejemplos del cap. 3, 7 + A1 propias, 40), como las junta a1/concordancia_adt.py;
  - oru/: las 40 bases ORU (bases_oru/, que regenera bases_oru.py);
  - muestras/: las 65 muestras públicas de los conversores (privado/cv/muestras), corpus secundario.
DV-CV-10: todo se normaliza a CR como separador de segmento y sin BOM ANTES de convertir: el conversor y el juez leen el mismo
mensaje, y la trama no es lo que se mide. Uso: python3 cv/corpus_cv2.py <carpeta de salida>"""
import hashlib
import json
import os
import re
import shutil
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUESTRAS = os.path.join(FASE, "..", "privado", "cv", "muestras")


def normal(t):
    return re.sub(r"\r\n|\n|\r", "\r", t.lstrip("﻿").strip()) + "\r"


def main(salida):
    if os.path.exists(salida):
        shutil.rmtree(salida)
    for d in ("adt", "oru", "muestras"):
        os.makedirs(os.path.join(salida, d))
    adt = json.load(open(os.path.join(FASE, "bases_adt", "bases_e2.json"), encoding="utf-8")) + \
        json.load(open(os.path.join(FASE, "a1", "ejemplos_cap3.json"), encoding="utf-8")) + \
        json.load(open(os.path.join(FASE, "a1", "bases_a1.json"), encoding="utf-8"))
    for x in adt:
        open(os.path.join(salida, "adt", x["id"] + ".hl7"), "w", encoding="utf-8").write(normal(x["mensaje"]))
    for f in sorted(os.listdir(os.path.join(FASE, "bases_oru"))):
        if f.endswith(".hl7"):
            t = open(os.path.join(FASE, "bases_oru", f), "rb").read().decode("utf-8")
            open(os.path.join(salida, "oru", "ORU-" + f), "w", encoding="utf-8").write(normal(t))
    for c in ("ms", "lfh"):
        for f in sorted(os.listdir(os.path.join(MUESTRAS, c))):
            t = open(os.path.join(MUESTRAS, c, f), encoding="utf-8-sig", errors="replace").read()
            nombre = "%s-%s" % (c, os.path.splitext(f)[0])
            open(os.path.join(salida, "muestras", nombre + ".hl7"), "w", encoding="utf-8").write(normal(t))
    man, h = [], hashlib.sha256()
    for d in ("adt", "oru", "muestras"):
        for f in sorted(os.listdir(os.path.join(salida, d))):
            s = hashlib.sha256(open(os.path.join(salida, d, f), "rb").read()).hexdigest()
            man.append("%s  %s/%s" % (s, d, f))
            h.update(s.encode())
    open(os.path.join(salida, "MANIFIESTO.txt"), "w").write("\n".join(man) + "\n")
    print("corpus CV2: adt %d, oru %d, muestras %d; huella %s" % tuple(
        [len(os.listdir(os.path.join(salida, d))) for d in ("adt", "oru", "muestras")] + [h.hexdigest()]))


if __name__ == "__main__":
    main(sys.argv[1])
