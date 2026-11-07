#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33: las 27 nuevas publicadas, en la versión 2. Dos preguntas distintas:
- apoyo_valido: si algún mensaje de su apoyo de la etapa 30 (iv/CRUCE-IV.json, que asigna el apoyo por el campo del hallazgo) es
  válido en la versión 2. Es lo que medía la 30.
- se_reproduce_en_valido: si la nueva SALE en algún mensaje válido de la versión 2. Por mecanismo, no por campo:
  - las del estudio de conversores (14l): los casos de su clase con la regla de cv/cv3_clases.py sobre el juicio de la versión 2
    (el árbol de ga/comparar_ga.py), y su par mínimo si se confirma en la versión 2 y su caso es válido;
  - las de MDM (26): su base y su par (md/CLASES-MD3.json), que el estudio confirmó, si alguno es válido; y, para MD-M5, el gemelo de
    su par MP1 con contenido ED (Q-GA-8, ga/GEMELO-MDM.json);
  - las 12 con gemelo: ga/GEMELOS-GA.json (el par confirmado con los gemelos y las bases gemelas con el hallazgo).
  python3 ga/cruce_ga.py <carpeta de la comparación>      -> ga/CRUCE-GA.json"""
import collections
import json
import os
import re
import sys

GA = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(GA)
sys.path[:0] = [os.path.join(FASE, "cv"), os.path.join(FASE, "md"), FASE]
a, sys.argv = sys.argv, ["x", "--silencio"]
import cv3_clases as CL  # noqa: E402
import juzgar_cv2 as J  # noqa: E402
import pares_mdm as PM  # noqa: E402
sys.argv = a
COMP = sys.argv[1]
C30 = json.load(open(os.path.join(FASE, "iv", "CRUCE-IV.json"), encoding="utf-8"))["nuevas"]
L = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(FASE, "..", "privado", "ga", "LISTA-CORPUS-V2-con-veredictos.jsonl"),
                                                     encoding="utf-8")}               # la de ga/ va sin veredictos (Q-IV-D-10)
CO1 = {f["id"]: f["sha256"] for f in json.load(open(os.path.join(FASE, "..", "privado", "iv", "corpus", "CORPUS-IV.json"),
                                                   encoding="utf-8"))["filas"]}
V30 = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(FASE, "iv", "VEREDICTOS-IV.jsonl"), encoding="utf-8")}
GE = json.load(open(os.path.join(GA, "GEMELOS-GA.json"), encoding="utf-8"))["nuevas"]
CL2 = {x["id"]: x for x in json.load(open(os.path.join(GA, "CLASES-GA-v2.json"), encoding="utf-8"))["clases"]}
MIN2 = {p["id"]: p for p in json.load(open(os.path.join(GA, "minimos-GA-v2.json"), encoding="utf-8"))["pares"]}
MD = {x["id"]: x for x in json.load(open(os.path.join(FASE, "md", "CLASES-MD3.json"), encoding="utf-8"))["clases"]}
MDPARES = [p[0] for p in PM.PARES]
GM = json.load(open(os.path.join(GA, "GEMELO-MDM.json"), encoding="utf-8"))


def valido(i):
    return (L.get(i) or {}).get("veredicto") == "valido"


uso = collections.defaultdict(set)
for x in map(json.loads, open(os.path.join(COMP, "arbol-v2", "juicio.jsonl"), encoding="utf-8")):
    for h in x["cuentan"]:
        for q in h["que"]:
            r = CL.regla(x["conversor"], J.asignar(h, q), q, x["caso"])
            if r:
                uso[r[0]].add("lab/%s/%s.hl7" % (x["corpus"], x["caso"]) if x["corpus"] != "muestras" else "muestras/" + x["caso"])
out = []
for n in C30:
    i = n["id"]
    apoyos = [{"apoyo": ap, "v1": V30[ap]["veredicto_sostenido"], "v2": L[ap]["veredicto"],
               "bytes": "iguales" if CO1[ap] == L[ap]["huella"] else "cambian"} for ap in n["apoyo"]]
    fila = {"id": i, "apoyos": apoyos, "apoyo_valido": any(x["v2"] == "valido" for x in apoyos)}
    if i in GE:
        g = GE[i]
        fila["donde"] = {"gemelos": g["se_reproduce_en_gemelos"]}
        fila["se_reproduce_en_valido"] = g["se_reproduce_en_gemelos"]
        fila["por"] = "su gemelo con ISO+"
    elif i in CL2:
        casos = sorted(uso[i])
        val = [c for c in casos if valido(c)]
        pares = [p.strip() for p in (CL2[i].get("par_minimo") or "").split("/") if p.strip()]
        pv = [p for p in pares if (MIN2.get(p) or {}).get("confirmada") and valido("lab/minimos/%s-caso.hl7" % p)]
        fila["donde"] = {"casos_de_la_clase": len(casos), "casos_validos": val[:6], "n_casos_validos": len(val), "pares": pares,
                         "pares_confirmados_y_validos": pv}
        fila["se_reproduce_en_valido"] = bool(val or pv)
        fila["por"] = "casos de su clase" if val else "su par mínimo" if pv else "ninguno"
    elif i in MD:
        m = re.search(r"base (B\d+)", MD[i].get("hallazgo") or "")
        del_apoyo = [x for x in n["apoyo"] if x.startswith("lab/mdm/")]
        base = "lab/mdm/MDM-%s.hl7" % m.group(1) if m else (del_apoyo[0] if len(del_apoyo) == 1 else None)   # MD-L5: B24; MD-M5: B33
        par = MD[i].get("par")
        pid = next((p for p in MDPARES if p == par or p.startswith(par + "-")), None) if par else None
        par_f = "mdm-pares/%s-con.hl7" % pid if pid else None
        fila["donde"] = {"base": base, "base_v2": (L.get(base) or {}).get("veredicto"), "par": par_f,
                         "par_v2": (L.get(par_f) or {}).get("veredicto"),
                         "sin_decidir": sorted({l for f in (base, par_f) if f for l in (L[f]["marcas"].get("sin_decidir") or [])})}
        gm = GM if par == "MP1" else None                          # Q-GA-8: el gemelo de MP1 con contenido ED (ga/GEMELO-MDM.json)
        if gm:
            fila["donde"]["gemelo_ed"] = gm["gemelo"]
        if valido(base) or valido(par_f):
            fila["se_reproduce_en_valido"], fila["por"] = True, "su base o su par"
        elif gm and gm["se_reproduce_en_valido"]:
            fila["se_reproduce_en_valido"], fila["por"] = True, "un gemelo de su par con contenido ED"
        else:
            fila["se_reproduce_en_valido"], fila["por"] = False, "ninguno"
    else:
        raise SystemExit("PARADA: no sé dónde buscar %s" % i)
    out.append(fila)
r = {"nuevas": out, "n": len(out),
     "apoyo_valido": sum(1 for x in out if x["apoyo_valido"]),
     "se_reproducen_en_un_mensaje_valido": sum(1 for x in out if x["se_reproduce_en_valido"]),
     "por": dict(collections.Counter(x["por"] for x in out if x["se_reproduce_en_valido"])),
     "no": [x["id"] for x in out if not x["se_reproduce_en_valido"]],
     "con_apoyo_valido_y_sin_reproducirse": [x["id"] for x in out if x["apoyo_valido"] and not x["se_reproduce_en_valido"]],
     "apoyos_que_pasan_a_validos": [f["apoyo"] for x in out for f in x["apoyos"] if f["v1"] != "valido" and f["v2"] == "valido"]}
json.dump(r, open(os.path.join(GA, "CRUCE-GA.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("de %d nuevas: con algún apoyo válido %d; se reproducen en un mensaje válido %d %s; no: %s; con apoyo válido y sin "
      "reproducirse: %s" % (r["n"], r["apoyo_valido"], r["se_reproducen_en_un_mensaje_valido"], r["por"], r["no"],
                            r["con_apoyo_valido_y_sin_reproducirse"]))
for x in out:
    if x["id"].startswith("MD") or not x["se_reproduce_en_valido"] or x["por"] == "su par mínimo":
        print("  %-6s %s %s" % (x["id"], x["por"], json.dumps(x["donde"], ensure_ascii=False)[:260]))
