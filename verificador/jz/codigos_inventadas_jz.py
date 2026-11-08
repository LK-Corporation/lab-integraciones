#!/usr/bin/env python3
"""Etapa 37, hecho para Q-JZ-3/4: en las evidencias ADT con «recurso_inventado» de la línea base, los code de las Observation
que el juez da por inventadas (las que nombra el hallazgo) y, de la injury-incident, si su effectiveDateTime es ACC-1.

  python3 jz/codigos_inventadas_jz.py <linea_base.jsonl> [...]"""
import collections
import json
import os
import re
import sys

PRIVADO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "privado"))


def main(*bases):
    cod = collections.Counter()
    fecha = collections.Counter()
    for b in bases:
        for l in open(b, encoding="utf-8"):
            x = json.loads(l)
            if x["punto"] != "adt_conv":
                continue
            g = json.loads(x["guardado"])
            inv = [h for h in g["hallazgos"] if h.get("subtipo") == "recurso_inventado"]
            if not inv:
                continue
            urls = set(re.findall(r"(urn:uuid:[0-9a-f-]+|Observation/[^ \"']+)", json.dumps([h["que"] for h in inv])))
            ruta = x["evidencia"] if x["evidencia"].startswith("/") else os.path.join(PRIVADO, x["evidencia"])
            e = json.load(open(ruta, encoding="utf-8"))
            bd = e["conversion"]["salida"]["bundle"]
            bd = json.loads(bd) if isinstance(bd, str) else bd
            m = e["mensaje"].replace("\r\n", "\r").replace("\n", "\r")
            acc = next((s.split("|") for s in m.split("\r") if s.startswith("ACC|")), None)
            for en in bd.get("entry") or []:
                r = en.get("resource") or {}
                if r.get("resourceType") != "Observation":
                    continue
                ids = {en.get("fullUrl"), "Observation/%s" % r.get("id"), "urn:uuid:%s" % r.get("id")}
                if not ids & urls:
                    continue
                c = ((r.get("code") or {}).get("coding") or [{}])[0].get("code")
                cod[c] += 1
                if c == "injury-incident":
                    ef = (r.get("effectiveDateTime") or "")[:10].replace("-", "")
                    a1 = (acc[1] if acc and len(acc) > 1 else "")[:8]
                    fecha["ACC-1 = effective" if ef and ef == a1 else "distinta: %s / %s" % (a1, ef)] += 1
    print("code de las Observation inventadas en ADT:", dict(cod.most_common()))
    print("injury-incident frente a ACC-1:", dict(fecha))


if __name__ == "__main__":
    main(*sys.argv[1:])
