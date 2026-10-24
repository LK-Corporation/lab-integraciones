#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CV3: las claves de mecanismo (conversor, mecanismo asignado, firma del «que») de todo lo que cuenta en un juicio, con el
número de casos por corpus y un ejemplo. Es la lista sobre la que se pone la clase. Solo lee.
Uso: python3 cv/cv3_claves.py <juicio.jsonl>"""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cv3_mecanismos import firma  # noqa: E402


def claves(juicio):
    c = collections.defaultdict(lambda: {"casos": collections.defaultdict(set), "ejemplo": None})
    for x in map(json.loads, open(juicio, encoding="utf-8")):
        for h in x["cuentan"]:
            for q in h["que"]:
                for m in h["mc"]:
                    k = (x["conversor"], m, firma(q))
                    c[k]["casos"][x["corpus"]].add(x["caso"])
                    c[k]["ejemplo"] = c[k]["ejemplo"] or "%s [%s] %s" % (x["caso"], h["hecho"], q[:150])
    return c


if __name__ == "__main__":
    for (cv, m, f), d in sorted(claves(sys.argv[1]).items()):
        print("%s | %s | %s | %s | %s" % (cv, m, f, dict((k, len(v)) for k, v in d["casos"].items()), d["ejemplo"]))
