#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33: las cifras de la validación de la versión 2 (iv/lectura_iv.py sobre las filas de iv/validar_iv.py) frente a la previsión A
sellada (ga/PREVISION-GA-A.json) y frente a la etapa 30 (iv/VEREDICTOS-IV.jsonl). Ninguna cifra va a mano.
  cd fase12 && python3 ga/cifras_ga_a.py <VEREDICTOS v2> <CORPUS-IV.json v2> <salida CIFRAS-GA-A.json>"""
import collections
import json
import os
import sys

GA = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(GA)
VER2, CORP2, SAL = sys.argv[1:4]
V2 = {json.loads(l)["id"]: json.loads(l) for l in open(VER2, encoding="utf-8")}
V1 = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(FASE, "iv", "VEREDICTOS-IV.jsonl"), encoding="utf-8")}
C2 = {f["id"]: f for f in json.load(open(CORP2, encoding="utf-8"))["filas"]}
C1 = {f["id"]: f for f in json.load(open(os.path.join(FASE, "..", "privado", "iv", "corpus", "CORPUS-IV.json"),
                                         encoding="utf-8"))["filas"]}
P = {p["id"]: p for p in json.load(open(os.path.join(GA, "PREVISION-GA-A.json"), encoding="utf-8"))["prevision"]}
GEN = {x["id"]: x["familia"] for x in json.load(open(os.path.join(FASE, "ga", "bases_adt_v2.json"), encoding="utf-8"))}
MAPA = {g["origen"]: g["gemelo"] for g in json.load(open(os.path.join(GA, "GEMELOS.json"), encoding="utf-8"))}
VD = "veredicto_sostenido"


def cuenta(ids):
    c = collections.Counter(V2[i][VD] for i in ids)
    return {"validas": c.get("valido", 0), "invalidas": c.get("invalido", 0), "sin_decidir": c.get("no_decidible", 0)}


estado = {i: ("nuevo" if i not in C1 else "igual" if C1[i]["sha256"] == C2[i]["sha256"] else "cambia") for i in C2}
iguales = [i for i in C2 if estado[i] == "igual"]
mismo = [i for i in iguales if V1[i][VD] == V2[i][VD]]
distinto_igual = [{"id": i, "v1": V1[i][VD], "v2": V2[i][VD]} for i in iguales if V1[i][VD] != V2[i][VD]]
base = lambda i: os.path.basename(i)[:-4]
g_genadt = [i for i in C2 if estado[i] == "cambia" and i.startswith("lab/adt/") and base(i) in GEN]
g_a1 = [i for i in C2 if estado[i] == "cambia" and base(i).startswith("A1-")]
g_cap3 = [i for i in C2 if estado[i] == "nuevo" and i.startswith("lab/adt/")]
g_b36 = [i for i in C2 if estado[i] == "cambia" and ("mdm" in i)]
g_gem = [i for i in C2 if i.startswith("gemelos/")]
r = {"n": len(C2), "por_estado": dict(collections.Counter(estado.values())),
     "PA1_identicos_mismo_veredicto": {"n": len(iguales), "mismo": len(mismo), "distintos": distinto_igual},
     "PA2_genadt": dict(cuenta(g_genadt), n=len(g_genadt), familias=dict(collections.Counter(GEN[base(i)] for i in g_genadt))),
     "PA3_a1": dict(cuenta(g_a1), n=len(g_a1)),
     "PA4_cap3_completadas": dict(cuenta(g_cap3), n=len(g_cap3), detalle={base(i): {"veredicto": V2[i][VD], "no_decidibles": [
         x.get("lugar") for x in V2[i]["no_decidibles"]], "sostenidos": [x.get("lugar") for x in V2[i]["sostenidos"]]} for i in g_cap3}),
     "PA5_b36": dict(cuenta(g_b36), n=len(g_b36), detalle={i: [x.get("lugar") for x in V2[i]["no_decidibles"] + V2[i]["sostenidos"]]
                                                           for i in g_b36}),
     "PA6_gemelos": dict(cuenta(g_gem), n=len(g_gem), no_validos={i: [x.get("lugar") for x in V2[i]["no_decidibles"] + V2[i]["sostenidos"]]
                                                                  for i in g_gem if V2[i][VD] != "valido"}),
     "PA7_total": cuenta(list(C2)),
     "por_corpus": {c: cuenta([i for i in C2 if C2[i]["corpus"] == c]) for c in sorted({f["corpus"] for f in C2.values()})}}
inval = [i for i in C2 if V2[i][VD] == "invalido"]
r["PA8_invalidas"] = {"n": len(inval), "ids": sorted(inval)}
# PA9: las 12 nuevas sin apoyo válido por la 0396 (CRUCE-IV.json de la 30), con el apoyo en sus gemelos
cruce = json.load(open(os.path.join(FASE, "iv", "CRUCE-IV.json"), encoding="utf-8"))["nuevas"]
doce = {}
for n in cruce:
    if n["con_algun_apoyo_valido"]:
        continue
    gem = []
    for a in n["apoyo"]:
        orig = [o for o in MAPA if o == a]
        if orig:
            g = "gemelos/" + MAPA[orig[0]]
            ctl = [o for o in MAPA if a.endswith("-caso.hl7") and o.startswith(a[:-len("caso.hl7")] + "control")]
            gem.append({"apoyo": a, "gemelo": g, "veredicto": V2[g][VD],
                        "controles": {MAPA[o]: V2["gemelos/" + MAPA[o]][VD] for o in ctl}})
    doce[n["id"]] = {"gemelos": gem, "con_apoyo_valido_en_gemelo": any(x["veredicto"] == "valido" for x in gem)}
r["PA9_apoyo_en_gemelos"] = {"nuevas": doce, "con_apoyo_valido": sum(1 for v in doce.values() if v["con_apoyo_valido_en_gemelo"]),
                             "sin": sorted(k for k, v in doce.items() if not v["con_apoyo_valido_en_gemelo"])}
acierto = {
    "PA1": len(mismo) == P["PA1"]["cifra"] and not distinto_igual,
    "PA2": {k: r["PA2_genadt"][k] for k in ("validas", "invalidas", "sin_decidir")} == {k: P["PA2"][k] for k in ("validas", "invalidas", "sin_decidir")},
    "PA3": r["PA3_a1"]["validas"] == P["PA3"]["validas"] == r["PA3_a1"]["n"],
    "PA4": {k: r["PA4_cap3_completadas"][k] for k in ("validas", "invalidas", "sin_decidir")} == {k: P["PA4"][k] for k in ("validas", "invalidas", "sin_decidir")}
    and r["PA4_cap3_completadas"]["detalle"].get("cap3-36-A04-completada", {}).get("veredicto") == "no_decidible",
    "PA5": r["PA5_b36"]["invalidas"] == 0 and r["PA5_b36"]["sin_decidir"] == P["PA5"]["sin_decidir"],
    "PA6": r["PA6_gemelos"]["validas"] == P["PA6"]["validas"],
    "PA7": r["PA7_total"] == {k: P["PA7"][k] for k in ("validas", "invalidas", "sin_decidir")},
    "PA8": len(inval) == P["PA8"]["cifra"],
    "PA9": r["PA9_apoyo_en_gemelos"]["con_apoyo_valido"] == P["PA9"]["cifra"],
}
r["prevision"] = {k: {"acierta": v, "prevision": P[k]} for k, v in acierto.items()}
r["aciertos"] = "%d de %d" % (sum(acierto.values()), len(acierto))
json.dump(r, open(SAL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in r.items() if k not in ("prevision", "PA9_apoyo_en_gemelos", "PA8_invalidas", "PA4_cap3_completadas")},
                 ensure_ascii=False)[:2500])
print("PA4:", json.dumps(r["PA4_cap3_completadas"], ensure_ascii=False)[:900])
print("PA9:", r["PA9_apoyo_en_gemelos"]["con_apoyo_valido"], r["PA9_apoyo_en_gemelos"]["sin"])
print("PA8:", r["PA8_invalidas"])
print("previsión:", {k: v["acierta"] for k, v in r["prevision"].items()}, r["aciertos"])
