#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 26, MD3-r1: qué cambia el juez de la repetición en las evidencias ya guardadas de MD2-c (sin correr ningún conversor).
Compara dos líneas base de md/rejuicio_md.py (antes y después de los arreglos) y resume, por conversor, los hallazgos que cuentan
que desaparecen o aparecen (subtipo, hecho sin índice), las notas nuevas y los cambios de categoría. Así se ve que cada arreglo
toca lo que debe y nada más. Solo biblioteca estándar.
  python3 md/r1_diferencias.py <antes.jsonl> <después.jsonl>"""
import collections
import json
import re
import sys


def leer(f):
    out = {}
    for l in open(f, encoding="utf-8"):
        x = json.loads(l)
        out[x["evidencia"]] = json.loads(x["guardado"])
    return out


def cuentan(j):
    return collections.Counter((s, re.sub(r"\(\d+\)", "", h["hecho"])) for h in j["hallazgos"] if h["cuenta"] for s in h["subtipo"].split("+"))


def notas(j):
    return collections.Counter(h["subtipo"] for h in j["hallazgos"] if not h["cuenta"])


def cat(j):
    v = j["veredicto"]
    return v["categoria"] + ("/" + v["subtipo"] if v.get("subtipo") else "")


def main(a, b):
    A, B = leer(a), leer(b)
    menos, mas, nn, cats = (collections.defaultdict(collections.Counter) for _ in range(4))
    n = collections.Counter()
    for k in sorted(set(A) & set(B)):
        if A[k] == B[k]:
            continue
        conv = "microsoft" if "/microsoft/" in k else "linuxforhealth" if "/linuxforhealth/" in k else "?"
        n[conv] += 1
        ca, cb = cuentan(A[k]), cuentan(B[k])
        for x, v in (ca - cb).items():
            menos[conv][x] += v
        for x, v in (cb - ca).items():
            mas[conv][x] += v
        for x, v in (notas(B[k]) - notas(A[k])).items():
            nn[conv][x] += v
        if cat(A[k]) != cat(B[k]):
            cats[conv]["%s -> %s" % (cat(A[k]), cat(B[k]))] += 1
    print("evidencias comparadas %d; cambian %s" % (len(set(A) & set(B)), dict(n)))
    for conv in sorted(n):
        print("== %s" % conv)
        print("  dejan de contar: %s" % dict(sorted(menos[conv].items())))
        print("  empiezan a contar: %s" % dict(sorted(mas[conv].items())))
        print("  notas nuevas: %s" % dict(sorted(nn[conv].items())))
        print("  categorías: %s" % dict(sorted(cats[conv].items())))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
