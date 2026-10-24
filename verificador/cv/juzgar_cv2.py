#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CV2: juzga las evidencias de los dos conversores con el juez (huella de la previsión sellada), asigna cada hallazgo que cuenta
a su mecanismo con la regla sellada (cv/PREVISION-CV2.json) y compara con la previsión. Escribe el detalle por caso fuera de git
y los agregados en cv/RESULTADO-CV2.json (o en el fichero que se le dé: los rejuicios de CV3 no pisan el de CV2).
Uso: python3 cv/juzgar_cv2.py <carpeta de evidencias> <detalle.jsonl> [agregados.json]"""
import collections
import glob
import json
import os
import re
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, FASE)
sys.argv_guardado, sys.argv = sys.argv, ["x", "--silencio"]
import conversion as CV  # noqa: E402
import mcp_verificador as M  # noqa: E402
import puntos_entrada as PE  # noqa: E402
import verificador as V  # noqa: E402
sys.argv = sys.argv_guardado

PREV = json.load(open(os.path.join(FASE, "cv", "PREVISION-CV2.json"), encoding="utf-8"))
CONV = {"microsoft-fhir-converter": "microsoft", "linuxforhealth-hl7v2-fhir-converter": "linuxforhealth"}


def ruta(que):
    return re.split(r"[\s:]", que.strip(), 1)[0]


def asignar(h, q):
    """La regla sellada: primer MC, en orden, que case por ruta y por subtipo."""
    subs = set(h["subtipo"].split("+"))
    r = ruta(q)
    for mc, d in PREV["mecanismos"].items():
        if not subs & set(d["subtipos"]):
            continue
        for x in d["rutas"]:
            if x == "*rechazo" and h["clase"] == "rechazo":
                return mc
            if x == "*recurso PV1" and "recurso_ausente" in subs and h["hecho"] == "PV1":
                return mc
            if x == "*recurso OBX" and "recurso_inventado" in subs and h["hecho"].startswith("OBX"):
                return mc
            if x.startswith("*"):
                continue
            base, _, cond = x.partition("|")
            if r.startswith(base) and (not cond or cond in q):
                return mc
    return "fuera:%s|%s" % (r if h["clase"] != "rechazo" else "rechazo", "+".join(sorted(subs)))


def juzgar(e, dec=None):
    pe = PE.resolver(None, e)
    return CV.verificar(e, pe, dec) if dec else V.verificar(e)


def main(carpeta, detalle, salida=os.path.join(FASE, "cv", "RESULTADO-CV2.json")):
    huella = M._version()["huella"]
    filas = []
    for f in sorted(glob.glob(os.path.join(carpeta, "*", "*", "*.json"))):
        conv_dir, fam_dir = f.split(os.sep)[-3], f.split(os.sep)[-2]
        e = json.load(open(f, encoding="utf-8"))
        r = juzgar(e)
        alt = {q: juzgar(e, CV.con_alternativas(q)) for q in CV.ALTERNATIVA}
        cuentan = [h for h in r["hallazgos"] if h["cuenta"]]
        mcs = sorted({asignar(h, q) for h in cuentan for q in h["que"]})
        filas.append({"conversor": conv_dir, "corpus": fam_dir, "caso": os.path.splitext(os.path.basename(f))[0],
                      "punto": e["punto_entrada"], "estado": e["conversion"]["salida"]["estado"],
                      "categoria": r["veredicto"]["categoria"], "subtipo": r["veredicto"].get("subtipo"),
                      "cuentan": [{"hecho": h["hecho"], "clase": h["clase"], "subtipo": h["subtipo"], "que": h["que"],
                                   "mc": sorted({asignar(h, q) for q in h["que"]})} for h in cuentan],
                      "notas": sorted({h["subtipo"] for h in r["hallazgos"] if not h["cuenta"]}), "mcs": mcs,
                      "alternativas": {q: {"categoria": a["veredicto"]["categoria"], "cuentan": sum(1 for h in a["hallazgos"] if h["cuenta"])}
                                       for q, a in alt.items()}})
    with open(detalle, "w", encoding="utf-8") as g:
        for x in filas:
            g.write(json.dumps(x, ensure_ascii=False) + "\n")
    res = {"juez": huella, "prevision_sellada": PREV["identidad"]["juez"], "por_conversor": {}, "fuera_de_previsto": []}
    if huella != PREV["identidad"]["juez"]:
        res["fuera_de_previsto"].append("el juez no es el de la previsión sellada: %s" % huella)
    for cv in ("microsoft", "linuxforhealth"):
        res["por_conversor"][cv] = {}
        for fam, corpus in (("adt", "adt"), ("oru", "oru"), ("muestras", "muestras")):
            fs = [x for x in filas if x["conversor"] == cv and x["corpus"] == corpus]
            if not fs:
                continue
            n = len(fs)
            cats = collections.Counter(x["categoria"] for x in fs)
            mc = collections.Counter(m for x in fs for m in x["mcs"])
            rech = sum(1 for x in fs if x["categoria"] == "rechazo_incorrecto")
            d = {"n": n, "estado": dict(collections.Counter(x["estado"] for x in fs)), "categorias": dict(cats),
                 "mecanismos": dict(sorted(mc.items())), "mecanismos_distintos": len(mc),
                 "sensibilidad": {q: {"fallo_silencioso": sum(1 for x in fs if x["alternativas"][q]["categoria"] == "fallo_silencioso"),
                                      "con_decision_de_jev": cats.get("fallo_silencioso", 0)} for q in CV.ALTERNATIVA}}
            res["por_conversor"][cv][fam] = d
            if fam == "muestras":
                continue
            rangos = PREV["categorias_por_conversor_y_familia"][cv][fam]
            for c, (lo, hi) in rangos.items():
                p = cats.get(c, 0) / n
                if not lo <= p <= hi:
                    res["fuera_de_previsto"].append("%s %s: %s %.1f %% fuera de [%.0f, %.0f] %%" % (cv, fam, c, 100 * p, 100 * lo, 100 * hi))
            if rech / n > 0.10:
                res["fuera_de_previsto"].append("%s %s: rechaza %d de %d (%.1f %%) del corpus 2.5" % (cv, fam, rech, n, 100 * rech / n))
            lo, hi = PREV["mecanismos_distintos_que_cuentan"][fam]
            if not lo <= len(mc) <= hi:
                res["fuera_de_previsto"].append("%s %s: %d mecanismos distintos que cuentan, fuera de [%d, %d]" % (cv, fam, len(mc), lo, hi))
            for m in mc:
                if m.startswith("fuera:"):
                    res["fuera_de_previsto"].append("%s %s: mecanismo no previsto %s (%d casos)" % (cv, fam, m[6:], mc[m]))
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
