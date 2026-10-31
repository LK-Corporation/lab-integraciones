#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 26, MD2-c (md/diseno-md.md §6.3, sensibilidad preinscrita): rejuzga las evidencias de las 40 bases de una corrida de
verificar_conversor.py con la decisión de Jev y, aparte, con la alternativa de cada Q de ALTERNATIVA_MD, sin volver a correr
los conversores. Dice, por conversor y por alternativa, qué mecanismos (hecho sin índice, subtipo) aparecen o desaparecen y en
cuántas bases, y las categorías. Q-MD-D-1 no cambia nada en las 40 (todas son T02): su alternativa se mide con S01..S04 aparte.
  python3 md/sensibilidad_md.py <carpeta de la corrida (con microsoft/ y linuxforhealth/)> -o <json>"""
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
import conversion as CV  # noqa: E402
import conversion_mdm as CVM  # noqa: E402
import puntos_entrada as PE  # noqa: E402


def mecanismos(out):
    ver = out.get("veredicto") or {}
    hall = [h for h in out.get("hallazgos") or [] if h.get("cuenta")]
    return ver.get("categoria"), {(re.sub(r"\(\d+\)", "", h.get("hecho") or h.get("campo") or ""), h.get("subtipo")) for h in hall}


def main(corrida, salida):
    res = {}
    for c in ("microsoft", "linuxforhealth"):
        evs = sorted(glob.glob(os.path.join(corrida, c, "evidencias", "**", "mdm", "*.json"), recursive=True))
        assert len(evs) == 40, (c, len(evs))
        base = {}
        for p in evs:
            e = json.load(open(p, encoding="utf-8"))
            base[os.path.basename(p)] = (e, mecanismos(CV.verificar(e, PE.resolver(None, e), None)))
        r = {"decision": {"categorias": dict(collections.Counter(v[1][0] for v in base.values())),
                          "mecanismos": {"%s %s" % k: n for k, n in collections.Counter(m for v in base.values() for m in v[1][1]).items()}}}
        for q, alt in sorted(CVM.ALTERNATIVA_MD.items()):
            mas, menos, cats = collections.Counter(), collections.Counter(), collections.Counter()
            for nombre, (e, (cat0, m0)) in base.items():
                cat, m = mecanismos(CV.verificar(e, PE.resolver(None, e), {q: alt}))
                cats[cat] += 1
                for k in m - m0:
                    mas["%s %s" % k] += 1
                for k in m0 - m:
                    menos["%s %s" % k] += 1
            r[q] = {"alternativa": alt, "categorias": dict(cats), "aparecen": dict(mas), "desaparecen": dict(menos)}
        res[c] = r
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for c, r in res.items():
        print("==", c, r["decision"]["categorias"])
        for q in sorted(k for k in r if k.startswith("Q-")):
            x = r[q]
            print("  %-10s %-36s aparecen %s | desaparecen %s" % (q, x["alternativa"], x["aparecen"] or "-", x["desaparecen"] or "-"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[sys.argv.index("-o") + 1])
