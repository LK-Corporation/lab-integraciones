#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 32 (Q-VD-2): las tablas del texto de v2.5.1 con el guion de la 30 (iv/tablas_iv.py), por la carpeta de enlaces:
ivd/TABLAS-TIPO-IVD251.json (publicable: número y tipo) y ../privado/ivd/TABLAS-VALORES-IVD251.json (privado: el texto de HL7 no
se redistribuye). Corrige el «origen» que el guion de la 30 escribe para v2.5. Desde fase12: python3 ivd/tablas_ivd.py"""
import json
import os
import subprocess
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VISTA = os.path.normpath(os.path.join(FASE, "..", "estandares", "hl7v2", "HL7_Messaging_v251", "vista_v25"))
TIPO = os.path.join(FASE, "ivd", "TABLAS-TIPO-IVD251.json")
VAL = os.path.normpath(os.path.join(FASE, "..", "privado", "ivd", "TABLAS-VALORES-IVD251.json"))
r = subprocess.run([sys.executable, os.path.join(FASE, "iv", "tablas_iv.py"), VISTA, TIPO, VAL], capture_output=True, text=True)
print(r.stdout, r.stderr)
assert r.returncode == 0
d = json.load(open(TIPO, encoding="utf-8"))
assert d["origen"].startswith("texto de HL7 v2.5 ")
d["origen"] = "texto de HL7 v2.5.1 (todos los capítulos y el Apéndice A; etapa 32, ivd/tablas_ivd.py): solo el número de tabla y su tipo"
json.dump(d, open(TIPO, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
v = json.load(open(VAL, encoding="utf-8"))["valores"]
assert "2.5.1" in v["0104"] and "UCUM" not in v["0396"], "las tablas de v2.5.1 no se leyeron como se esperaba"
print("origen corregido; 0104 trae 2.5.1")
