#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 28: rejuzga las evidencias de una corrida de verificar_conversor.py sobre el corpus derivado (mev/bases_mdmev.py) con el
punto de los cinco eventos (conversion_mdm.PE_ALTERNATIVA_EVENTOS, Q-MD-D-1 b), sin volver a correr los conversores. Compara cada
base en T04, T06, T08 y T10 con la misma base en T02: categoría y mecanismos que cuentan (hecho sin índice, subtipo). Lo que
difiere es lo propio del evento. Con --muestras, juzga además las evidencias de las muestras públicas de esos eventos.
  python3 mev/juzgar_mdmev.py <corrida (con microsoft/ y linuxforhealth/)> -o <json> [--muestras <corrida de las muestras>]"""
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
import conversion as CV  # noqa: E402
import conversion_mdm as CVM  # noqa: E402

PE = CVM.PE_ALTERNATIVA_EVENTOS
DEC = CVM.con_alternativas_md("Q-MD-D-1")


def juicio(e):
    out = CV.verificar(e, PE, DEC)
    ver = out.get("veredicto") or {}
    mec = sorted({"%s %s" % (re.sub(r"\(\d+\)", "", h.get("hecho") or ""), h.get("subtipo")) for h in out.get("hallazgos") or [] if h.get("cuenta")})
    return {"estado": (e.get("terceros") or {}).get("salida", {}).get("estado") if isinstance(e.get("terceros"), dict) else None,
            "categoria": ver.get("categoria"), "subtipo": ver.get("subtipo"), "mecanismos": mec}


def main(corrida, salida, muestras=None):
    res = {}
    for c in ("microsoft", "linuxforhealth"):
        por = {}
        for p in glob.glob(os.path.join(corrida, c, "evidencias", "**", "*.json"), recursive=True):
            m = re.search(r"MDM-(B\d+)-(T\d+)\.json$", p)
            if m:
                por[(m.group(1), m.group(2))] = juicio(json.load(open(p, encoding="utf-8")))
        assert len(por) == 200, (c, len(por))
        dif = collections.defaultdict(list)
        cats = collections.defaultdict(collections.Counter)
        for (b, ev), j in sorted(por.items()):
            cats[ev][j["categoria"]] += 1
            if ev == "T02":
                continue
            t02 = por[(b, "T02")]
            mas, menos = sorted(set(j["mecanismos"]) - set(t02["mecanismos"])), sorted(set(t02["mecanismos"]) - set(j["mecanismos"]))
            if mas or menos or j["categoria"] != t02["categoria"]:
                dif[ev].append({"base": b, "categoria_t02": t02["categoria"], "categoria": j["categoria"], "subtipo": j["subtipo"],
                                "aparecen": mas, "desaparecen": menos})
        res[c] = {"categorias": {ev: dict(n) for ev, n in sorted(cats.items())}, "diferencias": dict(dif)}
        if muestras:
            ms = collections.Counter()
            filas = []
            for p in glob.glob(os.path.join(muestras, c, "evidencias", "**", "muestras", "*.json"), recursive=True):
                e = json.load(open(p, encoding="utf-8"))
                txt = json.dumps(e.get("mensaje") or e.get("entrada") or "", ensure_ascii=False)
                ev = re.search(r"MDM\^(T\d+)", txt)
                if ev and ev.group(1) in ("T04", "T06", "T08", "T10"):
                    j = juicio(e)
                    ms[(ev.group(1), j["categoria"])] += 1
                    filas.append(dict(j, caso=os.path.basename(p)[:-5], evento=ev.group(1)))
            res[c]["muestras"] = {"categorias": {"%s %s" % k: n for k, n in sorted(ms.items())}, "casos": filas}
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for c, r in res.items():
        print("==", c, r["categorias"])
        for ev, ds in r["diferencias"].items():
            agg = collections.Counter()
            for d in ds:
                agg[("cat %s->%s" % (d["categoria_t02"], d["categoria"])) if d["categoria"] != d["categoria_t02"] else "misma cat"] += 1
                for x in d["aparecen"]:
                    agg["+ " + x] += 1
                for x in d["desaparecen"]:
                    agg["- " + x] += 1
            print("  %s: %d bases distintas; %s" % (ev, len(ds), dict(agg.most_common(8))))
        if "muestras" in r:
            print("  muestras:", r["muestras"]["categorias"])


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[a.index("-o") + 1], a[a.index("--muestras") + 1] if "--muestras" in a else None)
