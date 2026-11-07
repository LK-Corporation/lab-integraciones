#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33: las cifras de los conversores (versión 2 frente a 1) y su contraste con la previsión B sellada (ga/PREVISION-GA-B.json).
Lee lo que escriben ga/comparar_ga.py (comparar, gemelos y ruido de B36) y los juicios de las corridas. Ninguna cifra va a mano.
  cd fase12 && python3 ga/cifras_ga_b.py <carpeta de corridas> <salida CIFRAS-GA-B.json>"""
import collections
import json
import os
import sys

GA = os.path.dirname(os.path.abspath(__file__))
C, SAL = sys.argv[1:3]
P = {p["id"]: p for p in json.load(open(os.path.join(GA, "PREVISION-GA-B.json"), encoding="utf-8"))["prevision"]}
CO = json.load(open(os.path.join(C, "comparacion", "COMPARACION-GA.json"), encoding="utf-8"))
GE = json.load(open(os.path.join(C, "GEMELOS-GA.json"), encoding="utf-8"))
GS = json.load(open(os.path.join(C, "GEMELOS-GA-sellada.json"), encoding="utf-8"))
CL = {n: json.load(open(os.path.join(C, "comparacion", "CLASES-GA-%s.json" % n), encoding="utf-8")) for n in ("v1", "v2")}


def juicio(corrida):
    return {(f["corpus"], f["caso"]): f for f in map(json.loads, open(os.path.join(C, corrida, "juicio.jsonl"), encoding="utf-8"))}


casos = {n: {x["id"]: sum((x.get("casos") or {}).values()) for x in CL[n]["clases"]} for n in CL}
ms1, ms2 = juicio("microsoft-v1a"), juicio("microsoft-v2")
FASE = os.path.dirname(GA)
sys.path[:0] = [os.path.join(FASE, "cv"), FASE]
_a, sys.argv = sys.argv, ["x", "--silencio"]
import cv3_clases as CL3  # noqa: E402
import juzgar_cv2 as J  # noqa: E402
sys.argv = _a
m11 = set()                                       # DV-GA-11: los casos de M-11 por su clase en la VERSIÓN 1, no por cómo salen en la 2
for x in map(json.loads, open(os.path.join(C, "comparacion", "arbol-v1", "juicio.jsonl"), encoding="utf-8")):
    for h in x["cuentan"]:
        for q in h["que"]:
            rr = CL3.regla(x["conversor"], J.asignar(h, q), q, x["caso"])
            if rr and rr[0] == "M-11":
                m11.add((x["corpus"], x["caso"]))
m11 = sorted(m11)
m11_v2 = collections.Counter(ms2[k].get("estado") for k in m11 if k in ms2)
b36 = {c: json.load(open(os.path.join(C, "B36-%s.json" % c), encoding="utf-8")) for c in ("microsoft", "linuxforhealth")}
pc = CO["por_conversor"]
r = {
    "por_conversor": {c: {"por_estado": v["por_estado"], "iguales_distintos": len(v["iguales_distintos"]),
                          "categorias_que_cambian": v["categorias_que_cambian"], "nuevos": len(v["nuevos"])} for c, v in pc.items()},
    "frase": CO["frase"], "minimos": CO["minimos_confirmadas"],
    "clases_que_cambian": {k: [casos["v1"].get(k), casos["v2"].get(k)] for k in sorted(set(casos["v1"]) | set(casos["v2"]))
                           if casos["v1"].get(k) != casos["v2"].get(k)},
    "cifras_que_cambian": [{"cifra": d["cifra"], "v1": d["lote"], "v2": d["mensaje"], "publicado": d["publicado"],
                            "donde_se_publica": d.get("donde_se_publica")} for d in CO["cifras_que_cambian"]],   # lote/mensaje = v1/v2
    "candidatas": CO["sin_clase"]["candidatas"],
    "deriva_del_juez_desde_lo_publicado": CO["deriva_del_juez_v1"],
    "m11": {"casos_v1": len(m11), "estado_v2": dict(m11_v2)},
    "gemelos": {"se_reproducen": GE["se_reproducen"], "no": GE["no"], "distintas_del_origen": GE["distintas_del_origen"],
                "con_la_comparacion_sellada": {"se_reproducen": len(GS["se_reproducen"]), "no": GS["no"]}},
    "b36": {c: {"n": v["n"], "distintos": len(v["distintos"])} for c, v in b36.items()},
}
f2 = CO["frase"]["v2"]
acierto = {
    "PB1": all(v["iguales_distintos"] == 0 and v["por_estado"].get("igual") == 435 for v in r["por_conversor"].values()),
    "PB2": r["minimos"]["v1"] == r["minimos"]["v2"] == P["PB2"]["minimos_confirmadas"],
    "PB3": all(f2[k] == P["PB3"][k] for k in ("N_nuevas_confirmadas", "D_ya_declaradas", "rechazos_nuevos", "dudosas", "M_mensajes"))
    and f2["C_convenciones"] >= P["PB3"]["C_convenciones_al_menos"],
    "PB4": casos["v1"].get("M-11") == P["PB4"]["casos_v1"] and not casos["v2"].get("M-11"),
    "PB5": all(casos["v2"].get(k) == n == casos["v1"].get(k) for k, n in P["PB5"]["clases"].items()),
    "PB6": len(m11) == P["PB6"]["cifra"] and m11_v2.get("bundle") == P["PB6"]["cifra"],
    "PB7": len(r["candidatas"]) >= P["PB7"]["al_menos"],
    "PB8": len(GE["se_reproducen"]) == P["PB8"]["cifra"] and not GE["distintas_del_origen"],
    "PB8_con_la_sellada": len(GS["se_reproducen"]) == P["PB8"]["cifra"],
    "PB9": all(v["distintos"] == 0 for v in r["b36"].values()),
}
r["prevision"] = {k: {"acierta": v, "prevision": P.get(k[:3])} for k, v in acierto.items()}
r["aciertos"] = "%d de %d (PB8 con la comparación sellada: %s)" % (
    sum(v for k, v in acierto.items() if k != "PB8_con_la_sellada"), len(acierto) - 1, acierto["PB8_con_la_sellada"])
json.dump(r, open(SAL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: r[k] for k in ("por_conversor", "minimos", "clases_que_cambian", "m11", "gemelos", "b36")}, ensure_ascii=False))
print("previsión:", {k: v["acierta"] for k, v in r["prevision"].items()}, r["aciertos"])
