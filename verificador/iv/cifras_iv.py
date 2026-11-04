#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 30: todas las cifras del resultado, de VEREDICTOS-IV.jsonl, FILAS-IV.jsonl y CRUCE-IV.json, y su contraste con la
previsión sellada (PREVISION-IV.json y decision-jev-prevision-iv.md). Ninguna cifra de RESULTADO-IRISVAL.md va a mano.
  python3 iv/cifras_iv.py <FILAS-IV.jsonl> <VEREDICTOS-IV.jsonl> <CRUCE-IV.json> <CIFRAS-IV.json>"""
import collections
import json
import os
import re
import sys

FILAS, VERED, CRUCE, SAL = sys.argv[1:5]
AQUI = os.path.dirname(os.path.abspath(__file__))
F = {json.loads(l)["id"]: json.loads(l) for l in open(FILAS, encoding="utf-8")}
V = [json.loads(l) for l in open(VERED, encoding="utf-8")]
C = json.load(open(CRUCE, encoding="utf-8"))
P = json.load(open(os.path.join(AQUI, "PREVISION-IV.json"), encoding="utf-8"))["prevision"]


def grupo(i):
    """El origen de cada mensaje de ADT, por su nombre: los del generador (comp, nulo…), los de A1 y los del capítulo 3."""
    b = os.path.basename(i)
    if b.startswith("cap3-"):
        return "adt: ejemplos del capítulo 3"
    if b.startswith("A1-"):
        return "adt: bases A1"
    m = re.match(r"A\d\d-(\d+)", b)
    f = F[i]
    ctl = [s for s in [f.get("msh9")]]
    return "adt: generador GENADT"


por = collections.defaultdict(collections.Counter)
clases = collections.Counter()
mens_clase = collections.defaultdict(set)
lugares = collections.Counter()
for v in V:
    c = v["corpus"]
    por[c][v["veredicto_sostenido"]] += 1
    if v["solo_0396"]:
        por[c]["solo_0396"] += 1
    if c == "lab/adt":
        por[grupo(v["id"])][v["veredicto_sostenido"]] += 1
    for e in v["sostenidos"]:
        k = e["lugar"].split("|")[0]
        clases[k] += 1
        mens_clase[k].add(v["id"])
        lugares[e["lugar"]] += 1
tot = collections.Counter()
for c in [c for c in por if not c.startswith("adt:")]:
    tot.update(por[c])
cifras = {
    "n": len(V), "total": dict(tot),
    "por_corpus": {c: dict(x) for c, x in sorted(por.items())},
    "errores_sostenidos_por_clase": dict(clases), "mensajes_por_clase": {k: len(s) for k, s in mens_clase.items()},
    "lugares_sostenidos": dict(lugares.most_common()),
    "importados_mal": sum(1 for f in F.values() if not f["importado"]["ok"]),
    "incompletos": sum(1 for f in F.values() for x in f["variantes"].values() if x["incompleto"]),
    "z_al_final": sum(1 for f in F.values() for x in f["variantes"].values() for p in x["errores"] if p["clase"] == "Z" and not p["cuenta"]),
    "z_que_cuentan": sum(1 for f in F.values() for x in f["variantes"].values() for p in x["errores"] if p["clase"] == "Z" and p["cuenta"]),
    "msh9_sin_estructura": sum(1 for f in F.values() if not f["doctype_msh93"]),
    "msh9_sin_estructura_no_resueltos": sum(1 for f in F.values() if not f["doctype_msh93"] and not f["doctype_esquema"]),
    "estructura_discrepante": sum(1 for f in F.values() if f["doctype_discrepante"]),
    "otros_separadores": sum(1 for f in F.values() if f["separadores"] != "|^~&"),
    "no_ascii": sum(1 for f in F.values() if f["no_ascii"]),
}
# lo que IRIS dice y no cuenta, por motivo (agregados de las filas, que no se publican)
avisos = collections.Counter()
inval_cualquiera = 0
for f in F.values():
    x = f["variantes"].get("msh93") or f["variantes"].get("esquema") or f["variantes"].get("ninguna")
    inval_cualquiera += x["veredicto_iris"] == "invalido"
    for p in x["errores"]:
        if not p["cuenta"]:
            avisos[p.get("motivo") or "sin motivo"] += 1
L = json.load(open(os.path.join(AQUI, "LECTURAS-IV.json"), encoding="utf-8"))
TIPOS_IDX = {}
for r in L["lecturas"]:
    if r.get("tipo_en_indice"):
        TIPOS_IDX[r["tabla"]] = r["tipo_en_indice"]
por_tabla = collections.Counter()
campos_sin_evaluar = 0
for f in F.values():
    x = f["variantes"].get("msh93") or f["variantes"].get("esquema") or f["variantes"].get("ninguna")
    campos_sin_evaluar += bool(x.get("campos_sin_evaluar"))
    for p in x["errores"]:
        if p["clase"] == "T_USR":
            por_tabla[(p.get("tabla"), "vacia_en_iris" if p.get("tabla_vacia_en_iris") else "de_usuario")] += 1
cifras["avisos_de_tabla_por_tabla"] = {"%s|%s" % k: n for k, n in sorted(por_tabla.items())}
cifras["mensajes_con_campos_sin_evaluar"] = campos_sin_evaluar
CO = json.load(open(os.path.join(AQUI, "..", "..", "privado", "iv", "corpus", "CORPUS-IV.json"), encoding="utf-8"))
cifras["mensajes_distintos"] = len({x["sha256"] for x in CO["filas"]})
cifras["copias_en_el_corpus"] = len(CO["filas"]) - cifras["mensajes_distintos"]
cifras["pares_comprobados_byte_a_byte"] = CO.get("comprobado")
cifras["avisos_de_iris_que_no_cuentan"] = dict(avisos.most_common())
cifras["ajustes_de_la_lectura"] = L["ajustes_por_valor"]
cifras["invalidos_por_cualquier_error_de_iris"] = inval_cualquiera
A = C["auditores"]
cifras["auditores"] = {k: {"acuerdo_mensaje": A[k]["acuerdo_mensaje"], "kappa": A[k]["kappa"], "lugares": A[k]["lugares"],
                           "campos_distintos": A[k]["campos_distintos"], "n_mensajes_2x2": A[k]["n_mensajes_2x2"],
                           "fuera_del_2x2": A[k]["fuera_del_2x2"], "positivos_iris": A[k]["positivos_iris"],
                           "positivos_auditores": A[k]["positivos_auditores"],
                           "matriz": A[k]["matriz"], "discrepancias": A[k]["discrepancias"] if k == "sin_0396" else len(A[k]["discrepancias"])}
                       for k in ("con_0396",)}
cifras["auditores"]["nota"] = ("con Q-IV-D-11 (decision-jev-qiv11b.md), lo de la 0396 queda sin decidir y la vista «sin la 0396» "
                               "es igual a esta: no se da aparte")
nv = C["nuevas"]
cifras["nuevas"] = {"n": len(nv), "por_estado": dict(collections.Counter(n["estado"] for n in nv)),
                    "criterio_del_antes": dict(collections.Counter(n["criterio_del_antes"] for n in nv)),
                    "todo_invalido_por_cualquier_regla": sorted(n["id"] for n in nv if n["criterio_del_antes"] == "todo_invalido"),
                    "sin_ningun_apoyo_valido": sorted(n["id"] for n in nv if not n["con_algun_apoyo_valido"]),
                    "con_algun_apoyo_valido": sum(1 for n in nv if n["con_algun_apoyo_valido"]),
                    "apoyo_incompleto": sum(1 for n in nv if not n["completo"]),
                    "por_juez": {j: dict(collections.Counter(n["estado"] for n in nv if n["juez"] == j)) for j in ("CV3", "VX3", "MD3")},
                    "apoyo_todo_invalido_por_otra_regla": sorted(n["id"] for n in nv if n["apoyo_por_estado"].get("invalido_por_otra_regla", 0)
                                                                 == sum(n["apoyo_por_estado"].values())),
                    "indeterminadas_cv3": sum(1 for n in nv if n["juez"] == "CV3" and n["estado"] == "indeterminada")}
# la previsión sellada, frente a lo medido
pct = lambda c: 100.0 * por[c]["valido"] / sum(por[c][k] for k in ("valido", "invalido", "no_decidible"))   # noqa: E731
contraste = {}
for c, x in P["PV1_validos_que_cuentan_pct"].items():
    if c.startswith("_"):
        continue
    pt, lo, hi = x
    contraste["PV1 " + c] = {"previsto": [pt, lo, hi], "medido": round(pct(c), 1), "acierta": lo <= pct(c) <= hi}
pv2 = 100.0 * inval_cualquiera / len(V)
contraste["PV2 inválidos por cualquier error"] = {"previsto": P["PV2_invalidos_por_cualquier_error_pct"], "medido": round(pv2, 1),
                                                  "acierta": P["PV2_invalidos_por_cualquier_error_pct"][1] <= pv2 <= P["PV2_invalidos_por_cualquier_error_pct"][2]}
cl3 = {k: clases.get(k, 0) for k in ("E", "R", "L", "T_HL7", "N")}
dos = sorted(cl3, key=lambda k: -cl3[k])[:2]
contraste["PV3 las dos clases mayores"] = {"previsto": ["R", "T_HL7"], "medido": dos, "por_clase": cl3, "acierta": set(dos) == {"R", "T_HL7"}}
contraste["PV4 importados mal"] = {"previsto": 0, "medido": cifras["importados_mal"], "acierta": cifras["importados_mal"] == 0}
contraste["PV5 incompletos"] = {"previsto": [0, 0, 3], "medido": cifras["incompletos"], "acierta": cifras["incompletos"] <= 3}
for k, clave in (("con_0396", "PV6 acuerdo por mensaje"),):
    m = 100 * A[k]["acuerdo_mensaje"] if A[k]["acuerdo_mensaje"] is not None else None
    contraste[clave] = {"previsto": P["PV6_acuerdo_mensaje_con_auditores_pct"], "medido": m and round(m, 1),
                        "n": A[k]["n_mensajes_2x2"],
                        "acierta": m is not None and P["PV6_acuerdo_mensaje_con_auditores_pct"][1] <= m <= P["PV6_acuerdo_mensaje_con_auditores_pct"][2]}
    kp = A[k]["kappa"]
    contraste[clave.replace("acuerdo por mensaje", "kappa")] = {
        "previsto": P["PV6b_kappa"], "medido": round(kp, 3) if kp is not None else "no se puede calcular",
        "acierta": kp is not None and P["PV6b_kappa"][1] <= kp <= P["PV6b_kappa"][2]}
    lg = 100 * (A[k]["lugares"]["los_dos_entre_alguno"] or 0)
    contraste[clave.replace("acuerdo por mensaje", "lugares de los dos")] = {
        "previsto": P["PV6c_lugares_vistos_por_los_dos_entre_los_vistos_por_alguno_pct"], "medido": round(lg, 1),
        "acierta": P["PV6c_lugares_vistos_por_los_dos_entre_los_vistos_por_alguno_pct"][1] <= lg <= P["PV6c_lugares_vistos_por_los_dos_entre_los_vistos_por_alguno_pct"][2]}
    for lado, pv in (("solo_iris", "PV7_solo_iris"), ("solo_auditores", "PV7_solo_auditores")):
        n = A[k]["lugares"][lado]
        contraste["PV7 %s (%s)" % (lado, k)] = {"previsto": P[pv], "medido": n, "acierta": P[pv][1] <= n <= P[pv][2]}
si = [d for d in A["con_0396"]["discrepancias"] if d["lo_ve"] == "IRIS"]
sost = sum(1 for d in si if d.get("tiene_razon") != "auditores")      # lo de IRIS que entra en el cruce ya es lo sostenido
pv8 = 100.0 * sost / len(si) if si else None
contraste["PV8 solo IRIS sostenidas"] = {"previsto": P["PV8_solo_iris_sostenidas_pct"], "medido": pv8 and round(pv8, 1),
                                         "acierta": pv8 is not None and P["PV8_solo_iris_sostenidas_pct"][1] <= pv8 <= P["PV8_solo_iris_sostenidas_pct"][2],
                                         "nota": ("no se puede medir: no hay pares que vea solo IRIS" if pv8 is None else
                                                  "al cruce solo entra lo de IRIS que la lectura sostiene")}
for j in ("CV3", "VX3", "MD3"):
    n = cifras["nuevas"]["por_juez"][j].get("afectada", 0)
    contraste["PV9 afectadas " + j] = {"previsto": P["PV9_nuevas_afectadas_por_juez"][j], "medido": n,
                                       "acierta": P["PV9_nuevas_afectadas_por_juez"][j][1] <= n <= P["PV9_nuevas_afectadas_por_juez"][j][2]}
contraste["PV9b indeterminadas CV3"] = {"previsto": ">0", "medido": cifras["nuevas"]["indeterminadas_cv3"],
                                        "acierta": cifras["nuevas"]["indeterminadas_cv3"] > 0}
contraste["PV10 Z que cuentan"] = {"previsto": 0, "medido": cifras["z_que_cuentan"], "acierta": cifras["z_que_cuentan"] == 0,
                                   "nota": "casi por construcción: antes del sello ya se sabía que los 24 Z van al final"}
contraste["PV11 sin estructura no resueltos"] = {"previsto": 0, "medido": cifras["msh9_sin_estructura_no_resueltos"],
                                                 "acierta": cifras["msh9_sin_estructura_no_resueltos"] == 0}
pv = 100.0 * tot["valido"] / len(V)
lg = 100 * A["con_0396"]["lugares"]["los_dos_entre_alguno"]
contraste["Jev: proporción válida"] = {"previsto": "más del 95 %", "medido": round(pv, 1), "acierta": pv > 95}
contraste["Jev: lugares de los dos"] = {"previsto": "menos del 20 %", "medido": round(lg, 1), "acierta": lg < 20}
contraste["Jev: nuevas afectadas"] = {"previsto": "ninguna", "medido": cifras["nuevas"]["por_estado"].get("afectada", 0),
                                      "acierta": cifras["nuevas"]["por_estado"].get("afectada", 0) == 0}
for k, x in contraste.items():
    x["vista_aparte"] = "sin_0396" in k or "sin la 0396" in k     # no estaba sellada así: se da como vista, no se cuenta
    x["repite"] = {"Jev: lugares de los dos": "PV6c, con otro intervalo", "Jev: nuevas afectadas": "PV9, en total",
                   "Jev: proporción válida": "PV1, en total"}.get(k)
cifras["prevision"] = contraste
selladas = [x for x in contraste.values() if not x["vista_aparte"]]
cifras["prevision_aciertos"] = "%d de %d" % (sum(1 for x in selladas if x["acierta"]), len(selladas))
json.dump(cifras, open(SAL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: cifras[k] for k in ("n", "total", "errores_sostenidos_por_clase", "mensajes_por_clase",
                                         "prevision_aciertos")}, ensure_ascii=False))
for c, x in cifras["por_corpus"].items():
    print("  %-30s %s" % (c, x))
print("nuevas:", cifras["nuevas"]["por_estado"], "| criterio del ANTES:", cifras["nuevas"]["criterio_del_antes"],
      "| todo inválido por cualquier regla:", cifras["nuevas"]["todo_invalido_por_cualquier_regla"],
      "| sin ningún apoyo válido:", cifras["nuevas"]["sin_ningun_apoyo_valido"], "| con algún apoyo válido:",
      cifras["nuevas"]["con_algun_apoyo_valido"])
print("avisos:", cifras["avisos_de_iris_que_no_cuentan"])
for k in ("con_0396", "sin_0396"):
    print("auditores %s: campos distintos %s; 2x2 n=%s, fuera %s, positivos IRIS %s, auditores %s" % (
        k, A[k]["campos_distintos"], A[k]["n_mensajes_2x2"], A[k]["fuera_del_2x2"], A[k]["positivos_iris"], A[k]["positivos_auditores"]))
for k, x in contraste.items():
    print("  %-48s %-5s previsto %s, medido %s" % (k, x["acierta"], x["previsto"], x["medido"]))
