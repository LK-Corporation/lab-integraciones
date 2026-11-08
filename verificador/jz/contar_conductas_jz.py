#!/usr/bin/env python3
"""Etapa 37: en una línea base del rejuicio (md/rejuicio_md.py linea_base), cuántas evidencias llevan cada conducta.

  python3 jz/contar_conductas_jz.py <linea_base.jsonl> [...]

Conducta T (tabla de usuario): un hallazgo cuyo «que» o «hecho» nombra PID-8.
Conducta S (segmento sin mapa): un hallazgo de sobrante «inventado» o cuyo texto dice «sin origen propio».
Escribe los recuentos por conducta, clase, subtipo y carpeta, y unos ejemplos de cada texto."""
import collections
import json
import sys


def conductas(h):
    t = json.dumps(h, ensure_ascii=False)
    r = set()
    if "PID-8" in t:
        r.add("T:PID-8")
    if "sin origen propio" in t or "inventad" in t:
        r.add("S")
    return r


def main(*bases):
    por = collections.Counter()
    ev = collections.Counter()
    textos = collections.defaultdict(collections.Counter)
    n = 0
    for b in bases:
        for l in open(b, encoding="utf-8"):
            x = json.loads(l)
            n += 1
            g = json.loads(x["guardado"])
            carpeta = "/".join(x["evidencia"].split("/")[:2])
            vistas = set()
            for h in g["hallazgos"]:
                for c in conductas(h):
                    por[(c, h.get("clase"), h.get("subtipo"), h.get("cuenta"), carpeta)] += 1
                    q = h.get("que") or h.get("hecho") or ""
                    q = q if isinstance(q, str) else json.dumps(q, ensure_ascii=False)
                    textos[c][(h.get("clase"), q[:110])] += 1
                    vistas.add(c)
            for c in vistas:
                ev[(c, carpeta, x["punto"])] += 1
    print("evidencias leídas: %d" % n)
    print("\n== evidencias con la conducta, por carpeta y punto")
    tot = collections.Counter()
    for k in sorted(ev):
        tot[k[0]] += ev[k]
        print("  %-8s %-28s %-9s %d" % (k[0], k[1], k[2], ev[k]))
    print("  total: %s" % dict(tot))
    print("\n== hallazgos, por conducta, clase, subtipo, cuenta y carpeta")
    for k in sorted(por, key=str):
        print("  %-8s %-28s %-22s %-6s %-28s %d" % (k[0], k[1], k[2], k[3], k[4], por[k]))
    print("\n== textos (los 12 más frecuentes de cada conducta)")
    for c in sorted(textos):
        for (cl, q), m in textos[c].most_common(12):
            print("  %-8s %-26s %5d  %s" % (c, cl, m, q))


if __name__ == "__main__":
    main(*sys.argv[1:])
