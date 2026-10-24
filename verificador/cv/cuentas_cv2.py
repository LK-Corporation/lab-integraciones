#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CV2: las cuentas del corpus que completan la previsión de Fable (cv/diseno-conversores-fable.md §7): por cada mecanismo
previsto, en cuántos mensajes PUEDE morder (su oportunidad). Solo lee los mensajes; no corre ningún conversor ni mira ninguna
salida. Uso: python3 cv/cuentas_cv2.py <corpus> -> cv/CUENTAS-CV2.json"""
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import conversion as CV  # noqa: E402
import mapeador_referencia as MR  # noqa: E402
import puntos_entrada as PE  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))


def campo(m, seg, n):
    s = CV._seg(m, seg)
    return CV._f(m, s, n) if s is not None else ""


def adt(m):
    o = set()
    pid, pv1 = CV._seg(m, "PID"), CV._seg(m, "PV1")
    c2 = CV._t(m, campo(m, "PV1", 2), 1)
    if c2 in ("E", "I", "O", "P"):
        o.add("MC-ADT-1")
    if pid is not None and not CV._d(m, campo(m, "PID", 8)):
        o.add("MC-ADT-2")
    for n in (3, 6, 11, 42):
        v = campo(m, "PV1", n)
        if v and (CV._t(m, v, 2) or CV._t(m, v, 3)):
            o.add("MC-ADT-3")
    if CV._t(m, campo(m, "PID", 16), 1):
        o.add("MC-ADT-4")
    if CV._t(m, campo(m, "PV1", 10), 1) in ("MED", "URO"):
        o.add("MC-ADT-5")
    v7 = CV._t(m, campo(m, "PID", 7), 1)
    if v7 and len(re.match(r"\d*", v7).group(0)) in (4, 6):
        o.add("MC-ADT-6")
    reps5 = CV._reps(m, campo(m, "PID", 5))
    if len(reps5) > 1 or any(CV.mapa("0200", CV._t(m, r, 7)) is None for r in reps5 if CV._t(m, r, 7)):
        o.add("MC-ADT-7")
    for n in (13, 14):
        for r in CV._reps(m, campo(m, "PID", n)):
            if CV._t(m, r, 12) or CV._t(m, r, 4):
                o.add("MC-ADT-8")
    ev = (CV._comp(m, CV._f(m, m.segs[0], 9), 2) or "").upper()
    if ev in ("A11", "A03"):
        o.add("MC-ADT-9")
    if campo(m, "PV1", 8) or campo(m, "PV1", 17):
        o.add("MC-ADT-10")
    nombres = [s.split(m.f)[0] for s in m.segs]
    if any(n.startswith("Z") for n in nombres) or ("AL1" in nombres and "OBX" in nombres[nombres.index("AL1"):]):
        o.add("MC-ADT-11")
    for seg, n in (("PV1", 44), ("PV1", 45), ("PID", 29)):
        v = CV._t(m, campo(m, seg, n), 1)
        if v and len(re.match(r"\d*", v).group(0)) > 8 and not re.search(r"[+-]\d{4}$", v):
            o.add("MC-ADT-12")
    if c2 == "N":
        o.add("MC-ADT-13 (Q-CV-D-6)")
    if any(m.s in CV._comp(m, r, 1) for r in reps5):
        o.add("MC-ADT-14 (Q-CV-D-9)")
    return o


def oru(m):
    o = set()
    grupos, fuera = CV._grupos_oru(m)
    for _, obxs in grupos:
        for x in obxs:
            t = CV._d(m, CV._f(m, x, 2)).upper()
            v5 = CV._f(m, x, 5)
            if t in ("NM", "SN") and re.search(r"\.\d*0(\D|$)", v5):
                o.add("MC-ORU-1")
            if t == "SN":
                o.add("MC-ORU-2")
            if t == "NM" and CV._f(m, x, 6):
                o.add("MC-ORU-3")
            if CV._f(m, x, 8):
                o.add("MC-ORU-4")
            if t in ("TX", "FT") and (m.e in v5 or m.r in v5):
                o.add("MC-ORU-6")
    for obr, _ in grupos:
        if CV._f(m, obr, 8):
            o.add("MC-ORU-5")
        if not CV._f(m, obr, 25):
            o.add("MC-ORU-10")
    if len(grupos) > 1:
        o.add("MC-ORU-7")
    if fuera:
        o.add("OBX fuera de OBR (L-CV-7)")
    return o


def main(corpus):
    out = {}
    for fam, d, f_op in (("adt", "adt", adt), ("oru", "oru", oru)):
        c, ev, otros = collections.Counter(), collections.Counter(), collections.Counter()
        fs = sorted(os.listdir(os.path.join(corpus, d)))
        for f in fs:
            ms = MR.mensajes(open(os.path.join(corpus, d, f), encoding="utf-8").read())
            if not ms:
                otros["sin mensaje"] += 1
                continue
            m = ms[0]
            msh9 = CV._f(m, m.segs[0], 9)
            ev[msh9.split(m.c)[1] if m.c in msh9 else msh9] += 1
            for k in f_op(m):
                c[k] += 1
            imp = CV._imposibles(m, fam)
            if imp:
                otros["con valor imposible (%s)" % "+".join(sorted(set(imp)))] += 1
            falta = [s for s in (("PID", "PV1") if fam == "adt" else ("PID", "OBR")) if not m.segmentos(s)]
            if falta:
                otros["sin %s" % "+".join(falta)] += 1
            pe = PE.PUNTOS["adt_conv" if fam == "adt" else "oru_conv"]
            if PE.estructura_de(m, pe) is None:
                otros["fuera de alcance"] += 1
        out[fam] = {"mensajes": len(fs), "por_evento": dict(sorted(ev.items())), "oportunidad_por_mecanismo": dict(sorted(c.items())),
                    "otros": dict(sorted(otros.items()))}
    json.dump(out, open(os.path.join(AQUI, "CUENTAS-CV2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
