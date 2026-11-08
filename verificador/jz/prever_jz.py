#!/usr/bin/env python3
"""Etapa 37: la previsión del rejuicio, contada sobre la línea base del juez de antes (sin correr el juez nuevo).

  python3 jz/prever_jz.py <linea_base.jsonl> <salida.json>

Por evidencia, con las reglas decididas (jz/decision-jev-jz.md):
- conducta 1, convertido: algún hallazgo de PID-8 o NK1-15 con valor_imposible_convertido, o una nota version de PID-8 o NK1-15
  que dice «fuera de la 0001»;
- conducta 1, rechazo: un rechazo aceptable cuya lista lleva PID-8 (con solo PID-8, pasa a rechazo incorrecto);
- conducta 2: un ADT con recurso_inventado en OBX y un ACC o un PDA en el mensaje.
Escribe los recuentos por conducta, conversor y carpeta."""
import collections
import json
import os
import re
import sys

PRIVADO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "privado"))
CONVERSORES = ("microsoft", "linuxforhealth", "juguete", "ejemplo", "propio")
H1 = re.compile(r"^(PID-8|NK1(\(\d+\))?-15)$")


def main(base, salida):
    por = collections.Counter()
    tot = collections.Counter()
    rech = collections.Counter()
    for linea in open(base, encoding="utf-8"):
        x = json.loads(linea)
        g = json.loads(x["guardado"])
        c = set()
        for h in g["hallazgos"]:
            t = json.dumps(h["que"], ensure_ascii=False)
            if H1.match(h["hecho"] or "") and ("valor_imposible_convertido" in (h["subtipo"] or "")
                                               or (h["subtipo"] == "version" and "fuera de la 0001" in t)):
                c.add("1")
            if h["clase"] == "rechazo" and "'PID-8'" in t:
                c.add("1")
                rech["solo PID-8: a rechazo incorrecto" if "['PID-8']" in t else "con otro motivo: sigue aceptable"] += 1
            if x["punto"] == "adt_conv" and h["subtipo"] == "recurso_inventado" and h["hecho"] == "OBX":
                ruta = x["evidencia"] if x["evidencia"].startswith("/") else os.path.join(PRIVADO, x["evidencia"])
                m = json.load(open(ruta, encoding="utf-8")).get("mensaje") or ""
                if {s[:3] for s in re.split(r"\r\n|\r|\n", m)} & {"ACC", "PDA"}:
                    c.add("2")
        if c:
            k = "+".join(sorted(c))
            ev = x["evidencia"].replace(os.sep, "/")
            conv = next((p for p in CONVERSORES if p in ev.split("/")), "?")
            por[(k, conv, "/".join(ev.split("/")[:2]), x["punto"])] += 1
            tot[k] += 1
    res = {"por_conducta": dict(sorted(tot.items())), "rechazos_con_PID-8": dict(rech),
           "detalle": [{"conducta": k[0], "conversor": k[1], "carpeta": k[2], "punto": k[3], "evidencias": v} for k, v in sorted(por.items())]}
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({"por_conducta": res["por_conducta"], "rechazos_con_PID-8": res["rechazos_con_PID-8"]}, ensure_ascii=False))
    por_conv = collections.Counter()
    for k, v in por.items():
        por_conv[(k[0], k[1])] += v
    for k in sorted(por_conv):
        print("  %-5s %-15s %d" % (k[0], k[1], por_conv[k]))


if __name__ == "__main__":
    main(*sys.argv[1:])
