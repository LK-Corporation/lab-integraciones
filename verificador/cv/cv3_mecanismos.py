#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CV3: por conversor y mecanismo del corpus (ADT y ORU), los casos y la «firma» de sus «que» (los valores quitados de
comillas sustituidos por <v>), y si el mismo mecanismo con la misma firma aparece en las salidas esperadas publicadas de
Microsoft. Solo lee. Uso: python3 cv/cv3_mecanismos.py <juicio CV2.jsonl> <esperadas_ms.jsonl> [corpus,…]"""
import collections
import json
import re
import sys


def firma(q):
    q = re.sub(r"'[^']*'", "<v>", q)
    q = re.sub(r"\[[^\]]*\]", "<v>", q)
    q = re.sub(r"\{[^}]*\}", "<ref>", q)
    q = re.sub(r"urn:uuid:[0-9a-f-]+|[0-9a-f]{8}-[0-9a-f-]{27,}", "<id>", q)
    q = re.sub(r"\b\d+(\.\d+)?\b", "<n>", q)
    return q[:140]


def main(juicio, esperadas, corpus="adt,oru"):
    corpus = corpus.split(",")
    cuerpo = collections.defaultdict(lambda: collections.defaultdict(list))
    muestras = collections.defaultdict(set)
    for x in map(json.loads, open(juicio, encoding="utf-8")):
        if x["corpus"] not in corpus:
            continue
        for h in x["cuentan"]:
            for m in h["mc"]:
                for q in h["que"]:
                    cuerpo[(x["conversor"], m)][firma(q)].append((x["caso"], h["hecho"], q))
                    if x["corpus"] == "muestras":
                        muestras[(x["conversor"], m)].add(x["caso"])
    esp = collections.defaultdict(lambda: collections.defaultdict(list))
    for x in map(json.loads, open(esperadas, encoding="utf-8")):
        for h in x.get("cuentan", []):
            for m in h["mc"]:
                for q in h["que"]:
                    esp[m][firma(q)].append((x["caso"], x["esperada"], h["hecho"], q))
    for (cv, m), fs in sorted(cuerpo.items()):
        casos = {c for v in fs.values() for c, _, _ in v}
        print("=" * 110)
        print("%s  %s  (%d casos, %d firmas)%s" % (cv, m, len(casos), len(fs), ("  muestras: " + " ".join(sorted(muestras[(cv, m)]))[:200]) if muestras[(cv, m)] else ""))
        for f, v in sorted(fs.items(), key=lambda t: -len(t[1]))[:4]:
            c, hc, q = v[0]
            print("   %3d× [%s] %s" % (len({a for a, _, _ in v}), hc, q[:230]))
            print("        firma: %s" % f)
            if cv == "microsoft":
                e = esp.get(m, {}).get(f)
                print("        en las esperadas: %s" % ("%d (%s → %s)" % (len(e), e[0][0], e[0][1]) if e else "no"))
        if cv == "microsoft" and m in esp:
            otras = [f for f in esp[m] if f not in fs]
            if otras:
                print("   (en las esperadas, otras firmas del mismo mecanismo: %s)" % "; ".join(otras[:3]))


if __name__ == "__main__":
    main(*sys.argv[1:4])
