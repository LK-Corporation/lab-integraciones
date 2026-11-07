#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33 (ga/diseno-ga-fable.md §8.4): la versión 2 del corpus solo difiere de la 1 en lo que el diseño y las decisiones de Jev
permiten. Falla (sale 1) si no.
1. GENADT: mismos ids, eventos, familias y segmentos en el mismo orden; los campos distintos, dentro de PERMITIDOS; y el azar se
   llama las mismas veces (un random.Random que cuenta).
2. A1: solo cambia PID-5 de la familia «contactos», y solo «í» -> «i».
3. Capítulo 3: los 7 fragmentos, idénticos; cada copia completada contiene el fragmento: sus segmentos, iguales o prolongados con
   campos añadidos; MSH-9 puede prolongarse con MSG.3.
4. MDM: solo B36, en TXA-12; y mev/bases_mdmev.derivar da en T06 y T10 un TXA-13 de 30 caracteres o menos.
5. Gemelos: cada uno solo difiere de su origen en MSH-10 (sufijo «-ISO») y en el componente 3 de OBX-6 o RXA-7 (UCUM -> ISO+).
6. Los ficheros de la versión 1 no cambian: sus bytes son los del commit de partida (git HEAD de este fichero no basta: se comparan
   con el commit e53ff64, anterior a la etapa).
  cd fase12 && python3 ga/solo_cambia_esto.py"""
import json
import os
import random
import subprocess
import sys

GA = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(GA)
os.chdir(FASE)
sys.path[:0] = [GA, FASE, os.path.join(FASE, "bases_adt"), os.path.join(FASE, "mev")]
PARTIDA = "e53ff64"

# (familia, segmento, campo) que pueden cambiar en GENADT (§1.6, con P1 y DV-GA-1: los valores de tablas de usuario no cambian)
_OPC = {("ROL", 2), ("OBX", 11), ("DG1", 2), ("DG1", 6), ("PR1", 2), ("PR1", 5), ("GT1", 2), ("GT1", 3), ("ACC", 1), ("UB1", 2)}
PERMITIDOS = {(f, s, c) for f in ("completo", "opcionales") for s, c in _OPC} | {("completo", "PV1", 37)} | \
    {("nulos", s, c) for s, c in {("ROL", 2), ("ROL", 3), ("ROL", 4), ("ROL", 5), ("NK1", 1), ("DB1", 1), ("DB1", 2), ("OBX", 1),
                                  ("OBX", 2), ("OBX", 3), ("OBX", 5), ("OBX", 6), ("OBX", 11), ("AL1", 1), ("AL1", 2), ("AL1", 3),
                                  ("DG1", 1), ("DG1", 2), ("DG1", 6), ("PR1", 2), ("PR1", 5), ("GT1", 1), ("GT1", 3)}}
V1_FICHEROS = ["bases_adt/gen_adt.py", "bases_adt/bases_e2.json", "bases_adt/e2_comprobacion.json", "a1/gen_bases_a1.py",
               "a1/bases_a1.json", "a1/ejemplos_cap3.json", "bases_mdm.py", "bases_mdm.jsonl", "mev/bases_mdmev.py",
               "estructuras_hl7.py", "estructuras_25.json", "iv/tablas_iv.py", "iv/TABLAS-TIPO-IV.json", "bases_oru.py",
               "bases_vxu.py", "cv/cv3_minimos.py", "cv/cv3_minimos_vxu.py", "au/pares_auditoria.py"]
mal = []


def mira(nombre, cond, detalle=""):
    if not cond:
        mal.append("%s %s" % (nombre, detalle))


def campos(seg):
    f = seg.split("|")
    return f if not seg.startswith("MSH") else ["MSH", "|"] + f[1:]


def distintos(a, b):
    fa, fb = campos(a), campos(b)
    n = max(len(fa), len(fb))
    fa, fb = fa + [""] * (n - len(fa)), fb + [""] * (n - len(fb))
    return [i for i in range(1, n) if fa[i] != fb[i]]


class Contador(random.Random):
    llamadas = 0

    def random(self):
        Contador.llamadas += 1
        return super().random()

    def getrandbits(self, k):
        Contador.llamadas += 1
        return super().getrandbits(k)


def genadt():
    v1 = json.load(open("bases_adt/bases_e2.json", encoding="utf-8"))
    v2 = json.load(open("ga/bases_adt_v2.json", encoding="utf-8"))
    mira("GENADT: 216 y 216", len(v1) == len(v2) == 216)
    cambios = set()
    for a, b in zip(v1, v2):
        mira("GENADT %s: id, evento y familia" % a["id"], (a["id"], a["evento"], a["familia"]) == (b["id"], b["evento"], b["familia"]))
        sa, sb = a["mensaje"].split("\r"), b["mensaje"].split("\r")
        mira("GENADT %s: segmentos" % a["id"], [s[:3] for s in sa] == [s[:3] for s in sb])
        for x, y in zip(sa, sb):
            for c in distintos(x, y):
                cambios.add((a["familia"], x[:3], c))
                mira("GENADT %s %s-%d permitido" % (a["id"], x[:3], c), (a["familia"], x[:3], c) in PERMITIDOS)
    import gen_adt
    import gen_adt_v2
    cuentas = []
    for mod in (gen_adt, gen_adt_v2):
        Contador.llamadas = 0
        orig, mod.random.Random = mod.random.Random, Contador
        try:
            b = mod.bases(1)
        finally:
            mod.random.Random = orig
        cuentas.append(Contador.llamadas)
    mira("GENADT: el azar, las mismas llamadas", cuentas[0] == cuentas[1] and cuentas[0] > 0, cuentas)
    mira("GENADT: bases(1) de v2 = ga/bases_adt_v2.json", b == v2)
    return {"lugares_que_cambian": sorted("%s %s-%d" % x for x in cambios), "permitidos_sin_usar": sorted(
        "%s %s-%d" % x for x in PERMITIDOS - cambios), "llamadas_al_azar": cuentas}


def a1():
    v1 = json.load(open("a1/bases_a1.json", encoding="utf-8"))
    v2 = json.load(open("ga/bases_a1_v2.json", encoding="utf-8"))
    n = 0
    for a, b in zip(v1, v2):
        if a == b:
            continue
        n += 1
        mira("A1 %s: solo contactos" % a["id"], a["familia"] == "contactos")
        sa, sb = a["mensaje"].split("\r"), b["mensaje"].split("\r")
        for x, y in zip(sa, sb):
            d = distintos(x, y)
            mira("A1 %s: solo PID-5" % a["id"], d in ([], [5]) and (not d or x[:3] == "PID"))
            if d:
                mira("A1 %s: solo í -> i" % a["id"], campos(x)[5].replace("í", "i") == campos(y)[5])
    mira("A1: 40 y 40", len(v1) == len(v2) == 40)
    return {"distintas": n}


def cap3():
    v1 = json.load(open("a1/ejemplos_cap3.json", encoding="utf-8"))
    v2 = json.load(open("ga/ejemplos_cap3_v2.json", encoding="utf-8"))
    mira("cap3: los 7 fragmentos idénticos", v2[:7] == v1)
    orig = {x["id"]: x for x in v1}
    for c in v2[7:]:
        o = orig[c["copia_completada_de"]]
        mira("cap3 %s: nombre" % c["id"], c["id"] == o["id"] + "-completada")
        so, sc = o["mensaje"].split("\r"), c["mensaje"].split("\r")
        for s in so:
            par = [t for t in sc if t[:3] == s[:3]]
            mira("cap3 %s: %s presente" % (c["id"], s[:3]), len(par) == 1)
            if par:
                fo, fc = campos(s), campos(par[0])
                for i in range(1, len(fo)):
                    ok = fo[i] == fc[i] or (s[:3] == "MSH" and i == 9 and fc[i].startswith(fo[i] + "^"))
                    mira("cap3 %s %s-%d: igual o prolongado" % (c["id"], s[:3], i), ok, (fo[i], fc[i]))
    return {"copias": len(v2) - 7}


def mdm():
    import bases_mdm as BM
    import bases_mdm_v2 as B2
    import bases_mdmev as EV
    d = [(a["id"], [i for x, y in zip(a["segmentos"], b["segmentos"]) for i in distintos(x, y)], a["segmentos"] == b["segmentos"])
         for a, b in zip(BM.BASES, B2.BASES)]
    dist = [x for x in d if not x[2]]
    mira("MDM: solo B36, en TXA-12", [(x[0], x[1]) for x in dist] == [("B36", [12])], dist)
    b36 = [b for b in B2.BASES if b["id"] == "B36"][0]
    txa13 = []
    for ev in ("T06", "T10"):
        t = [s for s in EV.derivar(b36, ev) if s.startswith("TXA|")][0].split("|")
        txa13.append(t[13])
        mira("MDM B36 %s: TXA-13 <= 30" % ev, len(t[13]) <= 30, t[13])
    t12 = [s for s in b36["segmentos"] if s.startswith("TXA|")][0].split("|")[12]
    mira("MDM B36: TXA-12 <= 30", len(t12) <= 30, t12)
    return {"txa12": t12, "txa13": txa13}


def gemelos():
    import hacer_resto_v2 as R
    textos = R.origenes()
    filas = json.load(open("ga/GEMELOS.json", encoding="utf-8"))
    mira("gemelos: 37", len(filas) == len(R.ORIGENES) == 37)
    for g in filas:
        o = textos[g["origen"]].decode("utf-8").split("\r")
        t = open(os.path.join("ga", "gemelos", g["gemelo"]), encoding="utf-8", newline="").read().split("\r")
        mira("gemelo %s: segmentos" % g["gemelo"], [s[:3] for s in o] == [s[:3] for s in t])
        for x, y in zip(o, t):
            for c in distintos(x, y):
                if x[:3] == "MSH":
                    mira("gemelo %s MSH" % g["gemelo"], c == 10 and campos(y)[10] == campos(x)[10] + "-ISO")
                    continue
                mira("gemelo %s %s-%d" % (g["gemelo"], x[:3], c), (x[:3], c) in (("OBX", 6), ("RXA", 7)))
                for rx, ry in zip(campos(x)[c].split("~"), campos(y)[c].split("~")):
                    cx, cy = rx.split("^"), ry.split("^")
                    mira("gemelo %s %s-%d: solo CE.3 UCUM -> ISO+" % (g["gemelo"], x[:3], c),
                         len(cx) == len(cy) and all(p == q or (k == 2 and p == "UCUM" and q == "ISO+")
                                                    for k, (p, q) in enumerate(zip(cx, cy))))
    return {"n": len(filas)}


def v1_intacta():
    out = subprocess.run(["git", "diff", "--name-only", PARTIDA, "--"] + V1_FICHEROS, capture_output=True, text=True)
    mira("versión 1: los ficheros no cambian desde %s" % PARTIDA, out.returncode == 0 and not out.stdout.strip(), out.stdout)
    return {"ficheros": len(V1_FICHEROS), "cambiados": out.stdout.split()}


if __name__ == "__main__":
    r = {"genadt": genadt(), "a1": a1(), "cap3": cap3(), "mdm": mdm(), "gemelos": gemelos(), "version1": v1_intacta(), "mal": mal}
    r["veredicto"] = "TODO BIEN" if not mal else "%d MAL" % len(mal)
    json.dump(r, open(os.path.join(GA, "SOLO-CAMBIA-ESTO.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for x in mal[:20]:
        print("  MAL", x)
    print(json.dumps({k: v for k, v in r.items() if k not in ("mal",)}, ensure_ascii=False)[:1500])
    print("SOLO CAMBIA ESTO:", r["veredicto"])
    sys.exit(0 if not mal else 1)
