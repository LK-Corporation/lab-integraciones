#!/usr/bin/env python3
"""Etapa 37, hecho para Q-JZ-5: evidencias con Bundle cuyo PID-8 está fuera de la 0001 (ni en mayúscula ni en minúscula) y cuyo
Patient no lleva gender; y, para comparar, las que sí lo llevan. Por conversor, carpeta y valor. Lee las evidencias de la línea
base; no juzga nada.

  python3 jz/pid8_ausente_jz.py <linea_base.jsonl> [...]"""
import collections
import json
import os
import sys

T0001 = {"F", "M", "O", "U", "A", "N"}
PRIVADO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "privado"))


def main(*bases):
    c = collections.Counter()
    for b in bases:
        for l in open(b, encoding="utf-8"):
            x = json.loads(l)
            ruta = x["evidencia"] if x["evidencia"].startswith("/") else os.path.join(PRIVADO, x["evidencia"])
            e = json.load(open(ruta, encoding="utf-8"))
            m = (e.get("mensaje") or "").replace("\r\n", "\r").replace("\n", "\r")
            pid = next((s for s in m.split("\r") if s[:4] == "PID|"), None)
            if not pid:
                continue
            p = pid.split("|")
            v = (p[8] if len(p) > 8 else "").split("^")[0]
            if not v or v.upper() in T0001:
                continue
            sal = (e.get("conversion") or {}).get("salida") or {}
            bd = sal.get("bundle")
            if isinstance(bd, str):
                try:
                    bd = json.loads(bd)
                except ValueError:
                    bd = None
            if not isinstance(bd, dict):
                c[("sin Bundle", "/".join(x["evidencia"].split("/")[:2]), v)] += 1
                continue
            pats = [en.get("resource") or {} for en in bd.get("entry") or [] if (en.get("resource") or {}).get("resourceType") == "Patient"]
            g = pats[0].get("gender") if pats else "(sin Patient)"
            conv = next((q for q in ("microsoft", "linuxforhealth", "juguete", "propio", "ejemplo") if q in x["evidencia"]), "?")
            c[(conv, "/".join(x["evidencia"].split("/")[:2]), v, "gender=%s" % g if g else "SIN gender")] += 1
    for k in sorted(c, key=str):
        print("  " + " | ".join(k) + " : %d" % c[k])
    sin = sum(n for k, n in c.items() if k[-1] == "SIN gender")
    print("total con Bundle y SIN gender: %d" % sin)


if __name__ == "__main__":
    main(*sys.argv[1:])
