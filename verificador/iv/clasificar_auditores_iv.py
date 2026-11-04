#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 30 (iv/diseno-iv-fable.md §2): los defectos de los auditores de la 29, en la rejilla de IRIS, por programa, antes de ver
ninguna fila de IRIS del corpus. Después se revisan a mano (`--revision`, un JSON {indice: clase}) y se sellan.
Clases: E, R, L, T_HL7, T_USR, N (comparables con IRIS), TRANSVERSAL (XCN-8/9), NC (no comparable: condicionales, cruces,
estados, tipos de dato, semántica). El lugar es «SEG-n» si `donde` lo da.
  python3 iv/clasificar_auditores_iv.py <publicación>/verificador <salida.json> [--revision revision.json] [--ver]"""
import json
import os
import re
import sys

VER, SAL = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
REV = json.load(open(sys.argv[sys.argv.index("--revision") + 1], encoding="utf-8")) if "--revision" in sys.argv else {}
TIPOS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "TABLAS-TIPO-IV.json"), encoding="utf-8"))["tablas"]


def clase(d):
    t = ("%s %s" % (d.get("donde") or "", d.get("que") or "")).lower()
    if re.search(r"xcn[-.]?(8|9)|componente[s]? 8|transversal", t):
        return "TRANSVERSAL"
    if re.search(r"condicion|condicional|\bc\b \(|si .* entonces|cuando ", t):
        return "NC"
    m = re.search(r"\b(?:tabla|table)\s*(\d{4})|\b(0\d{3})\b", t)
    if re.search(r"tabla|table|valor .* no (está|esta|figura)|no es un valor", t) and m:
        n = m.group(1) or m.group(2)
        return "T_HL7" if TIPOS.get(n, {}).get("tipo") == "HL7" else "T_USR"
    if re.search(r"longitud|caracteres|len\b|excede", t):
        return "L"
    if re.search(r"repetici|repite|repeat", t):
        return "N"
    if re.search(r"segmento .*(falta|ausente|no esperado|fuera de orden|orden)|grupo|estructura del mensaje", t):
        return "E"
    if re.search(r"falta|ausente|vac[ií]o|obligatori|requerid|\br\b", t):
        return "R"
    return "NC"


def lugar(d):
    m = re.match(r"\s*([A-Z][A-Z0-9]{2})[-.](\d+)", d.get("donde") or "")
    return "%s-%s" % (m.group(1), int(m.group(2))) if m else None


out, i = [], 0
for f in ("au/AUDITORIA-VXU.json", "au/AUDITORIA-ORU.json"):
    for fila in json.load(open(os.path.join(VER, f), encoding="utf-8"))["filas"]:
        for d in fila.get("defectos") or []:
            c = REV.get(str(i), clase(d))
            out.append({"i": i, "auditoria": os.path.basename(f), "fichero": fila["fichero"], "veredicto": fila.get("veredicto"),
                        "veredicto_sin_transversales": fila.get("veredicto_sin_transversales", fila.get("veredicto")),
                        "nivel": d.get("nivel") or d.get("grado"),
                        "donde": d.get("donde"), "lugar": lugar(d), "clase": c, "por": "revision" if str(i) in REV else "programa"})
            if "--ver" in sys.argv:
                print("%3d %-12s %-22s %-7s %-11s | %s" % (i, fila["fichero"][-22:], (d.get("donde") or "")[:22], d.get("nivel"), c,
                                                           (d.get("que") or "")[:110].replace("\n", " ")))
            i += 1
ficheros = {}
for f in ("au/AUDITORIA-VXU.json", "au/AUDITORIA-ORU.json"):
    for fila in json.load(open(os.path.join(VER, f), encoding="utf-8"))["filas"]:
        ficheros[fila["fichero"]] = {"veredicto": fila.get("veredicto"),
                                     "veredicto_sin_transversales": fila.get("veredicto_sin_transversales", fila.get("veredicto"))}
json.dump({"defectos": out, "ficheros": ficheros, "revision": REV}, open(SAL, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
cuenta = {}
for x in out:
    k = "%s/%s" % (x["clase"], x["nivel"])
    cuenta[k] = cuenta.get(k, 0) + 1
print("%d defectos en %d ficheros auditados; por clase/nivel: %s" % (len(out), len(ficheros), sorted(cuenta.items())))
