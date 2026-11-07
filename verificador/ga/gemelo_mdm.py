#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33 (Jev, ga/decision-jev-ga8.md: gemelo_ed, 0,80): un gemelo del par mínimo MP1 de MD-M5 (Microsoft rechaza entero un
MDM_T02 con TXA-8 repetido) con contenido que no es texto, para mirarlo en un mensaje que puede ser válido en v2.5. De cada lado del
par (sin y con, como los escribe iv/corpus_iv.py) cambian solo:
- TXA-3: TEXT -> AP (la 0191: «Other application data», HL7 V2.3 and later; cabe en el LEN 2, CH09.txt:825, 894);
- el OBX de texto -> el OBX ED de la base válida B05 (bases_mdm.py), tal cual;
- MSH-10: con «-ED».
El TXA-8 repetido del caso y todo lo demás quedan igual; se afirma campo a campo. Escribe ga/gemelos-mdm/ (los dos gemelos y los dos
originales, para correrlos juntos) y su MANIFIESTO.txt.
  cd fase12 && python3 ga/gemelo_mdm.py"""
import hashlib
import os
import shutil
import sys

GA = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(GA)
sys.path[:0] = [os.path.join(FASE, "md"), FASE]
a, sys.argv = sys.argv, ["x", "--silencio"]
import pares_mdm as PM  # noqa: E402
import bases_mdm as BM  # noqa: E402
sys.argv = a

par = [p for p in PM.PARES if p[0] == "MP1"][0]
obx_ed = [s for s in [b for b in BM.BASES if b["id"] == "B05"][0]["segmentos"] if s.startswith("OBX|")]
assert len(obx_ed) == 1 and obx_ed[0].split("|")[2] == "ED"
d = os.path.join(GA, "gemelos-mdm")
shutil.rmtree(d, ignore_errors=True)
os.makedirs(d)
man = []
for lado, segs in (("sin", par[3]), ("con", par[4])):
    segs = PM.campo(segs, "MSH", 9, "MDM-MP1-%s" % lado)                   # como iv/corpus_iv.py
    gem = []
    for s in segs:
        f = s.split("|")
        if f[0] == "MSH":
            f[9] = f[9] + "-ED"
        elif f[0] == "TXA":
            assert f[3] == "TEXT", f[3]
            f[3] = "AP"
        elif f[0] == "OBX":
            assert f[2] == "TX", f[2]
            f = obx_ed[0].split("|")
        gem.append("|".join(f))
    assert [s[:3] for s in segs] == [s[:3] for s in gem]
    for x, y in zip(segs, gem):                                              # solo cambia lo dicho
        if x != y:
            fx, fy = x.split("|"), y.split("|")
            if x[:3] == "MSH":
                assert [i for i in range(max(len(fx), len(fy))) if (fx + [""] * 30)[i] != (fy + [""] * 30)[i]] == [9]
            elif x[:3] == "TXA":
                assert [i for i in range(max(len(fx), len(fy))) if (fx + [""] * 40)[i] != (fy + [""] * 40)[i]] == [3]
            else:
                assert x[:3] == "OBX"
    for nombre, t in (("MDM-MP1-%s.hl7" % lado, segs), ("MDM-MP1-%s-ED.hl7" % lado, gem)):
        datos = ("\r".join(t) + "\r").encode("utf-8")
        open(os.path.join(d, nombre), "wb").write(datos)
        man.append("%s  %s" % (hashlib.sha256(datos).hexdigest(), nombre))
open(os.path.join(d, "MANIFIESTO.txt"), "w", encoding="utf-8").write("\n".join(man) + "\n")
print("escritos %d en %s" % (len(man), os.path.relpath(d, FASE)))
