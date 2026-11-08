#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 38: ¿se reproduce cv/CLASES-CV3.json con su receta? Y, si con otro juicio salen otros casos, ¿adónde va cada caso?

  cd fase12 && python3 cl/reproducir_clases_cl.py <salida.json> <juicio de la receta> <evidencias> <otro juicio> [...]

- Con el juicio de la receta (el del estudio, CV3), cv/cv3_clases.py tal como está hoy escribe sus clases en una carpeta temporal,
  y se comparan con el JSON publicado clase a clase: clase, casos, ejemplos y conversor, y la frase. El campo «juez» del JSON lo
  pone el guion con el juez de la carpeta, y las convenciones las recalcula sobre las evidencias con ese juez (cv3_clases.py), así
  que no entran en la comparación más que por la frase.
- Con cada otro juicio, lo mismo, y además, caso a caso, las clases de cada caso con el juicio de la receta y con el otro, por la
  misma regla (cv3_clases.regla sobre juzgar_cv2.asignar): los casos que cambian de clase, y de cuál a cuál.
Los juicios son JSONL de cv/juzgar_cv2.py (conversor, corpus, caso, cuentan…). Solo lee; escribe la salida y su carpeta temporal."""
import collections
import json
import os
import sys
import tempfile

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(FASE, "cv"))
CAMPOS = ("clase", "casos", "ejemplos", "conversor")


def clases_por_caso(juicio):
    import cv3_clases as C
    import juzgar_cv2 as J
    out = collections.defaultdict(set)
    for linea in open(juicio, encoding="utf-8"):
        x = json.loads(linea)
        for h in x["cuentan"]:
            for q in h["que"]:
                r = C.regla(x["conversor"], J.asignar(h, q), q, x["caso"])
                out[(x["conversor"], x["corpus"], x["caso"])].add(r[0] if r else "sin_clase")
    return out


def calcular(juicio, evidencias):
    import cv3_clases as C
    d = tempfile.mkdtemp(prefix="cl38-")
    s = os.path.join(d, "clases.json")
    argv = sys.argv
    try:
        C.main(juicio, os.path.join(FASE, "cv", "RESULTADO-CV3-minimos.json"), evidencias, s)
    finally:
        sys.argv = argv
    return json.load(open(s, encoding="utf-8"))


def comparar(pub, hoy):
    cp = {c["id"]: c for c in pub["clases"]}
    ch = {c["id"]: c for c in hoy["clases"]}
    dif = {}
    for k in sorted(set(cp) | set(ch)):
        a, b = cp.get(k, {}), ch.get(k, {})
        d = {f: [a.get(f), b.get(f)] for f in CAMPOS if a.get(f) != b.get(f)}
        if d:
            dif[k] = d
    fa, fb = pub["frase"], hoy["frase"]
    frase = {k: [fa.get(k), fb.get(k)] for k in sorted(set(fa) | set(fb)) if fa.get(k) != fb.get(k) and k != "C_nota"}
    return dif, frase


def main(salida, receta, evidencias, *otros):
    pub = json.load(open(os.path.join(FASE, "cv", "CLASES-CV3.json"), encoding="utf-8"))
    res = {"publicado": {"juez": pub.get("juez")}, "receta": {"juicio": os.path.basename(receta)}, "otros": {}}
    hoy = calcular(receta, evidencias)
    dif, frase = comparar(pub, hoy)
    res["receta"].update({"clases_que_difieren": dif, "frase_que_difiere": frase, "sin_clase": hoy.get("sin_clase"),
                          "se_reproduce": not dif and not frase and not hoy.get("sin_clase")})
    base = clases_por_caso(receta)
    for o in otros:
        hoy = calcular(o, evidencias)
        dif, frase = comparar(pub, hoy)
        otro = clases_por_caso(o)
        mueven = {"%s|%s|%s" % k: [sorted(base.get(k, set())), sorted(otro.get(k, set()))]
                  for k in sorted(set(base) | set(otro)) if base.get(k, set()) != otro.get(k, set())}
        res["otros"][os.path.basename(o)] = {"clases_que_difieren": dif, "frase_que_difiere": frase, "sin_clase": hoy.get("sin_clase"),
                                             "casos_que_cambian_de_clase": mueven}
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps(res, ensure_ascii=False, indent=1, sort_keys=True)[:6000])
    return 0 if res["receta"]["se_reproduce"] else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
