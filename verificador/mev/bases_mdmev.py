#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 28 (ANTES-ETAPA-MDMEV.md; Jev: corpus derivado): repite cada una de las 40 bases de MDM_T02 (bases_mdm.py) como T04, T06,
T08 y T10. Solo cambian:
- MSH-9 (MDM^Txx^MDM_T02), EVN-1 (Txx) y MSH-10 (el control lleva el evento);
- en T06 y T10, TXA-13 (documento padre), que v2.5 exige en esos eventos (§9.6.1.13): el número de TXA-12 con «-PADRE».

Las 40 de T02 se escriben también, tal cual, para que el par de cada base se corra en las mismas condiciones. Afirma que cada
mensaje derivado solo difiere de su T02 en esos campos y que TXA-13 va donde v2.5 lo exige.
  cd fase12 && python3 mev/bases_mdmev.py <carpeta de salida vacía>"""
import hashlib
import os
import sys

sys.path.insert(0, os.getcwd())
import bases_mdm as BM  # noqa: E402

EVENTOS = ("T02", "T04", "T06", "T08", "T10")
CON_PADRE = ("T06", "T10")


def campo(seg, i, valor):
    f = seg.split("|")
    while len(f) <= i:
        f.append("")
    f[i] = valor
    return "|".join(f)


def derivar(b, ev):
    out = []
    for s in b["segmentos"]:
        if s.startswith("MSH|"):
            f = s.split("|")
            s = campo(campo(s, 8, "MDM^%s^MDM_T02" % ev), 9, "%s-%s" % (f[9], ev)) if ev != "T02" else s
        elif s.startswith("EVN|") and ev != "T02":
            s = campo(s, 1, ev)
        elif s.startswith("TXA|") and ev in CON_PADRE and not (len(s.split("|")) > 13 and s.split("|")[13]):   # si ya lo trae, se queda
            f = s.split("|")
            ei = f[12].split("^")
            assert ei[0], (b["id"], "TXA-12 sin EI.1")
            s = campo(s, 13, "^".join([ei[0] + "-PADRE"] + ei[1:]))
        out.append(s)
    return out


def comprobar(b, ev, segs):
    base = b["segmentos"]
    assert len(base) == len(segs)
    for a, d in zip(base, segs):
        if a == d:
            continue
        fa, fd = a.split("|"), d.split("|")
        cambios = {i for i in range(max(len(fa), len(fd))) if (fa + [""] * 40)[i] != (fd + [""] * 40)[i]}
        permitidos = {"MSH": {8, 9}, "EVN": {1}, "TXA": {13}}[a[:3]]
        assert cambios <= permitidos, (b["id"], ev, a[:3], cambios)
    txa = next(s for s in segs if s.startswith("TXA|")).split("|")
    if ev in CON_PADRE:
        assert len(txa) > 13 and txa[13] != "", (b["id"], ev, "TXA-13 obligatorio en T06 y T10")


def main(salida):
    assert not os.path.exists(salida) or not os.listdir(salida), "la carpeta de salida tiene que estar vacía"
    os.makedirs(salida, exist_ok=True)
    man = []
    for b in BM.BASES:
        for ev in EVENTOS:
            segs = derivar(b, ev)
            comprobar(b, ev, segs)
            nombre = "MDM-%s-%s.hl7" % (b["id"], ev)
            datos = ("\r".join(segs) + "\r").encode("utf-8")
            open(os.path.join(salida, nombre), "wb").write(datos)
            man.append("%s  %s" % (hashlib.sha256(datos).hexdigest(), nombre))
    open(os.path.join(salida, "MANIFIESTO.txt"), "w", encoding="utf-8").write("\n".join(man) + "\n")
    print("%d mensajes (%d bases × %d eventos); huella %s" % (len(man), len(BM.BASES), len(EVENTOS),
                                                            hashlib.sha256("\n".join(man).encode()).hexdigest()[:12]))


if __name__ == "__main__":
    main(sys.argv[1])
