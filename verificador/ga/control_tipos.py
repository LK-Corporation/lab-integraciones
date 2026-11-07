#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33 (ga/diseno-ga-fable.md §6.3): el control del comprobador de tipos ANTES de usarlo sobre el corpus.
1. Mutantes: cada uno cambia un campo de la base A01-001 de la versión 2 (o añade un segmento). Dentro de ese campo, los hallazgos
   tienen que ser exactamente los esperados (ninguno, en los «no_debe»); fuera, los mismos que en la base.
2. Control positivo sobre la versión 1: tiene que encontrar cada hallazgo conocido (§6.3), con su lugar.
3. Control negativo: en la versión 1, cero errores en las seis familias de GENADT que la 30 da por válidas; en la versión 2, cero
   errores fuera de lo marcado (A1 a propósito y la copia del ejemplo veterinario, P5).
4. Unidades: UCUM en los 37 orígenes de los gemelos da tabla_hl7 en OBX-6.3 o RXA-7.3; en los gemelos, no.
Escribe ga/CONTROL-TIPOS.json. Sale 1 si algo falla.
  cd fase12 && python3 ga/control_tipos.py"""
import collections
import json
import os
import re
import sys

GA = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(GA)
os.chdir(FASE)
sys.path[:0] = [GA, FASE]
import comprobar_tipos as CT  # noqa: E402

BASE = {x["id"]: x for x in json.load(open("ga/bases_adt_v2.json", encoding="utf-8"))}["A01-001"]["mensaje"]
OBX = "OBX|1|ST|Height||170||||||F"


def poner(texto, seg, campo, valor):
    out, hecho = [], False
    for s in texto.split("\r"):
        if s.startswith(seg + "|") and not hecho:
            f = s.split("|")
            k = campo - 1 if seg == "MSH" else campo
            while len(f) <= k:
                f.append("")
            f[k] = valor
            s = "|".join(f).rstrip("|") if valor == "" else "|".join(f)
            hecho = True
        out.append(s)
    assert hecho, (seg, campo)
    return "\r".join(out)


def mas(texto, segmento):
    return texto + "\r" + segmento


# (id, base o segmento añadido, segmento, campo, valor, esperado dentro del campo: {(regla, lugar)})
M = []


def m(i, seg, campo, valor, esperado, anadir=None):
    M.append((i, anadir, seg, campo, valor, set(esperado)))


m("NM-debe", "PV1", 46, "B", {("formato", "PV1-46")})
for k, v in enumerate(("-1.5", "0", ".5")):
    m("NM-no%d" % k, "PV1", 46, v, ())
m("SI-debe-letra", "PID", 1, "A", {("formato", "PID-1")})
m("SI-debe-largo", "PID", 1, "12345", {("formato", "PID-1"), ("longitud_campo", "PID-1")})
m("SI-debe-negativo", "PID", 1, "-1", {("formato", "PID-1")})
for k, v in enumerate(("1", "9999", "0")):
    m("SI-no%d" % k, "PID", 1, v, ())
GT1 = "GT1|1||GUARANTOR^LAST^^^^^L"
m("DT-debe-guiones", "GT1", 13, "2024-01-01", {("formato", "GT1-13"), ("longitud_campo", "GT1-13")}, GT1)
m("DT-debe-mes13", "GT1", 13, "202413", {("formato", "GT1-13")}, GT1)
for k, v in enumerate(("2024", "202401", "20240131")):
    m("DT-no%d" % k, "GT1", 13, v, (), GT1)
m("DTM-debe-corto", "PID", 7, "1", {("formato", "PID-7.1")})
m("DTM-debe-minuto60", "PID", 7, "202401011260", {("formato", "PID-7.1")})
m("DTM-debe-zona", "PID", 7, "20240101+01", {("formato", "PID-7.1")})
for k, v in enumerate(("2024", "20240101120000.1234-0500", "202401011200")):
    m("DTM-no%d" % k, "PID", 7, v, ())
m("ID-debe-MSH11", "MSH", 11, "Q", {("tabla_hl7", "MSH-11.1")})
m("ID-debe-PID30", "PID", 30, "S", {("tabla_hl7", "PID-30")})
m("ID-debe-OBX11", "OBX", 11, "Z", {("tabla_hl7", "OBX-11")}, OBX)
m("ID-no-MSH11", "MSH", 11, "T", ())
m("ID-no-PID30", "PID", 30, "Y", ())
m("ID-no-OBX11", "OBX", 11, "X", (), OBX)
m("IS-debe", "PV1", 2, "Z", {("tabla_usuario", "PV1-2")})
m("IS-no-sugerido", "PV1", 2, "E", ())
m("IS-no-sin-valores", "PV1", 18, "ZZ", ())
m("C1-debe-DLD", "PV1", 37, "A^20240101^C", {("componentes_de_mas", "PV1-37")})
m("C1-debe-primitivo", "PID", 8, "M^F", {("componentes_de_mas", "PID-8"), ("longitud_campo", "PID-8")})   # LEN 1: también C2
m("C1-no", "PV1", 37, "HOME^20240101", ())
m("C2-debe-MSH10", "MSH", 10, "X" * 21, {("longitud_campo", "MSH-10")})
m("C2-debe-PID19", "PID", 19, "1" * 17, {("longitud_campo", "PID-19")})
m("C2-no-MSH10", "MSH", 10, "X" * 20, ())
m("C2-no-PID19", "PID", 19, "1" * 16, ())
m("C3-debe", "MSH", 3, "A" * 21, {("longitud_componente", "MSH-3.1")})
m("C3-no", "MSH", 3, "A" * 20, ())
m("C4-debe-tilde", "PID", 5, "GARCÍA^JUAN", {("no_ascii", "PID-5")})
m("C4-debe-escape", "PID", 5, "GAR\\Q\\CIA^JUAN", {("escape", "PID-5")})
m("C4-no-separadores", "PID", 5, "GAR\\F\\CIA\\S\\^JUAN\\T\\", ())
m("C4-no-E", "PID", 5, "GAR\\E\\CIA^JUAN", ())
m("C4-no-R", "PID", 5, "GAR\\R\\CIA^JUAN", ())
OBX_U = "OBX|1|NM|Height||170|cm^cm^ISO+|||||F"
m("C5-debe-UCUM", "OBX", 6, "mL^mL^UCUM", {("tabla_hl7", "OBX-6.3")}, OBX_U)
for k, v in enumerate(("mL^mL^ISO+", "mL^mL^99LAB", "x^y^HL70063", "mL^mL^ANS+")):
    m("C5-no%d" % k, "OBX", 6, v, (), OBX_U)
NK1 = "NK1|1|X^Y^^^^^L|SPO"
m("CE1-debe", "NK1", 3, "SPOUSE", {("tabla_usuario", "NK1-3.1")}, NK1)
m("CE1-no", "NK1", 3, "SPO", (), NK1)
m("CE1-no-sistema", "NK1", 3, "SPO^Spouse^HL70063", (), NK1)
m("MSG-debe-estructura", "MSH", 9, "ADT^A01^ADT_A02", {("condicion", "MSH-9")})
m("MSG-debe-sin-MSG3", "MSH", 9, "ADT^A01", {("componente_R_ausente", "MSH-9.3")})
m("MSG-debe-evento", "MSH", 9, "ADT^Z99^ADT_A01", {("tabla_hl7", "MSH-9.2"), ("condicion", "MSH-9")})
m("MSG-no", "MSH", 9, "ADT^A04^ADT_A01", ())
m("CX-debe-CX2", "PID", 3, "P1^LAST^^GENADT^MR", {("longitud_componente", "PID-3.2")})
m("CX-debe-CX5", "PID", 3, "P1^^^GENADT^ZZ", {("tabla_hl7", "PID-3.5")})
m("CX-debe-CX7", "PID", 3, "P1^^^GENADT^MR^^L", {("formato", "PID-3.7")})
m("CX-no", "PID", 3, "P1^4^M11^GENADT^MR^^20240101", ())
m("XPN-debe-7", "PID", 5, "A^B^^^^^Q", {("tabla_hl7", "PID-5.7")})
m("XPN-debe-8", "PID", 5, "A^B^^^^^^D", {("tabla_hl7", "PID-5.8")})
m("XPN-no", "PID", 5, "A^B^^^^^L^A", ())
m("XPN-no-FN", "PID", 5, "de&la&Fuente^Ana", ())
m("XTN-debe-2", "PID", 13, "1^XXX^PH", {("componente_retirado", "PID-13.1"), ("tabla_hl7", "PID-13.2")})
m("XTN-debe-3", "PID", 13, "1^PRN^XX", {("componente_retirado", "PID-13.1"), ("tabla_hl7", "PID-13.3")})
m("XTN-debe-NM", "PID", 13, "^PRN^PH^^34^91^abc", {("formato", "PID-13.7")})
m("XTN-no", "PID", 13, "^PRN^PH^^34^91^5551234", ())
m("XTN-no-correo", "PID", 13, "^NET^Internet^a@b.c", ())
m("XAD-debe-0190", "PID", 11, "S^^C^ST^Z^ESP^Q", {("tabla_hl7", "PID-11.7")})
m("XAD-debe-tilde", "PID", 11, "S^^C^ST^Z^ESPAÑA", {("no_ascii", "PID-11"), ("longitud_componente", "PID-11.6")})
m("XAD-no", "PID", 11, "S^^C^ST^Z^ESP^H", ())
m("HD-debe-0301", "MSH", 4, "LAB^1.2^ZZZ", {("tabla_hl7", "MSH-4.3")})
m("HD-debe-condicion", "MSH", 4, "LAB^1.2", {("condicion", "MSH-4")})
m("HD-no", "MSH", 4, "LAB^1.2.3^ISO", ())
ROL = "ROL|R1^NS^1.2^ISO|UC|CP|^DOC^X"
m("EI-debe-0301", "ROL", 1, "R1^NS^1.2^ZZ", {("tabla_hl7", "ROL-1.4")}, ROL)
m("EI-debe-condicion", "ROL", 1, "R1^NS^1.2", {("condicion", "ROL-1")}, ROL)
m("EI-no", "ROL", 1, "R1^NS^1.2^ISO", (), ROL)
m("PL-debe", "PV1", 3, "ICU^001^A^HOSP^^A", {("tabla_usuario", "PV1-3.6")})
m("PL-no", "PV1", 3, "ICU^001^A^HOSP^^N", ())
m("PT-debe", "MSH", 11, "P^Z", {("tabla_hl7", "MSH-11.2")})
m("PT-no", "MSH", 11, "P^T", ())
m("VID-debe", "MSH", 12, "2.5.1", {("tabla_hl7", "MSH-12.1")})
m("VID-no", "MSH", 12, "2.5", ())
m("C6-debe", "PID", 13, "611111111^PRN^PH", {("componente_retirado", "PID-13.1")})
m("C6-no", "PID", 13, "^PRN^PH^^^^611111111", ())
AL1 = "AL1|1||PEN"
m("C0-debe-nulo-R", "AL1", 3, '""', {("nulo_en_R", "AL1-3")}, AL1)
m("C0-no-nulo-O", "PID", 11, '""', ())
m("R-debe-PV1-2", "PV1", 2, "", {("R_ausente", "PV1-2")})
m("R-debe-OBX-11", "OBX", 11, "", {("R_ausente", "OBX-11")}, OBX)
m("R-no-OBX-11", "OBX", 11, "F", (), OBX)
m("OBX2-debe", "OBX", 2, "", {("condicion", "OBX-2")}, OBX)
m("OBX2-no-X", "OBX", 2, "", (), "OBX|1||Height||||||||X")


def dentro(lugar, pref):
    return lugar == pref or lugar.startswith(pref + ".") or lugar.startswith(pref + "[")


def claves(hs):
    return collections.Counter((h["regla"], h["lugar"]) for h in hs)


def mutantes():
    mal = []
    for i, anadir, seg, campo, valor, esp in M:
        base = mas(BASE, anadir) if anadir else BASE
        pref = "%s-%d" % (seg, campo)
        hb, hm = claves(CT.comprobar(base)), claves(CT.comprobar(poner(base, seg, campo, valor)))
        fuera_b = collections.Counter({k: v for k, v in hb.items() if not dentro(k[1], pref)})
        fuera_m = collections.Counter({k: v for k, v in hm.items() if not dentro(k[1], pref)})
        dent = {k for k in hm if dentro(k[1], pref)}
        ok = dent == esp and fuera_b == fuera_m
        if anadir:                                            # el segmento añadido, sin mutar, no puede traer hallazgos propios
            ok = ok and claves(CT.comprobar(base)) == claves(CT.comprobar(BASE))
        if not ok:
            mal.append({"id": i, "esperado": sorted(esp), "dentro": sorted(dent),
                        "fuera_distinto": sorted(set(fuera_m.items()) ^ set(fuera_b.items()))})
    return {"n": len(M), "debe": sum(1 for x in M if x[5]), "no_debe": sum(1 for x in M if not x[5]), "mal": mal}


def norm(lugar):
    return re.sub(r"\(\d+\)|\[\d+\]", "", lugar)


def hallazgos_por_grupo(ficheros):
    g = collections.defaultdict(collections.Counter)
    for f in ficheros:
        for x in json.load(open(f, encoding="utf-8")):
            i = x["id"]
            grupo = ("cap3-completada" if i.endswith("completada") else "cap3") if i.startswith("cap3") else \
                ("A1:" + x["familia"] if i.startswith("A1-") else x["familia"])
            for h in CT.comprobar(x["mensaje"]):
                g[grupo][(h["gravedad"], h["regla"], norm(h["lugar"]))] += 1
    return g


POSITIVO_V1 = [   # (grupo, gravedad, regla, lugar) que el comprobador tiene que encontrar en la versión 1 (§6.3)
    ("completo", "error", "formato", "GT1-2.7"), ("completo", "aviso", "longitud_componente", "GT1-2.2"),
    ("completo", "error", "formato", "UB1-2"), ("completo", "error", "formato", "ACC-1.1"),
    ("completo", "error", "componentes_de_mas", "PV1-37"),
    ("opcionales", "error", "formato", "GT1-2.7"), ("opcionales", "error", "formato", "UB1-2"),
    ("opcionales", "error", "formato", "ACC-1.1"),
] + [(f, "error", "R_ausente", l) for f in ("completo", "opcionales") for l in ("ROL-2", "OBX-11", "DG1-6", "PR1-5")] + \
    [("nulos", "error", "R_ausente", l) for l in ("NK1-1", "AL1-1", "DG1-1", "GT1-1", "GT1-3", "OBX-3", "ROL-4")] + \
    [("nulos", "error", "nulo_en_R", l) for l in ("ROL-3", "AL1-3", "DB1-1")] + \
    [("minimo", "aviso", "tabla_usuario", "EVN-4"), ("minimo", "aviso", "tabla_usuario", "PV1-3.6"),
     ("completo", "aviso", "tabla_usuario", "PV1-14"), ("completo", "aviso", "tabla_usuario", "NK1-3.1"),
     ("completo", "aviso", "tabla_usuario", "AL1-4.1"), ("completo", "aviso", "tabla_usuario", "ROL-3.1"),
     ("completo", "aviso", "componente_retirado", "PID-13.1"), ("completo", "aviso", "componente_retirado", "NK1-5.1"),
     ("A1:escapes_251", "error", "tabla_hl7", "MSH-12.1"), ("A1:escapes_251", "aviso", "tabla_usuario", "PID-8"),
     ("A1:escapes_251", "aviso", "tabla_usuario", "PV1-2"), ("A1:clases", "aviso", "tabla_usuario", "PID-8"),
     ("A1:clases", "aviso", "tabla_usuario", "PV1-2"), ("A1:pv1_2_vacio", "error", "R_ausente", "PV1-2"),
     ("A1:contactos", "error", "no_ascii", "PID-5"), ("cap3", "error", "tabla_hl7", "PID-5.8"),
     ("cap3", "aviso", "longitud_componente", "MSH-4.1")]
VALIDAS_30 = ("minimo", "repeticiones", "escapes", "delimitadores", "fechas", "z")
ERRORES_MARCADOS_V2 = {("A1:escapes_251", "tabla_hl7", "MSH-12.1"), ("A1:pv1_2_vacio", "R_ausente", "PV1-2"),
                       ("cap3-completada", "tabla_hl7", "PID-5.8")}


def corpus():
    v1 = hallazgos_por_grupo(["bases_adt/bases_e2.json", "a1/ejemplos_cap3.json", "a1/bases_a1.json"])
    v2 = hallazgos_por_grupo(["ga/bases_adt_v2.json", "ga/ejemplos_cap3_v2.json", "ga/bases_a1_v2.json"])
    falta = [x for x in POSITIVO_V1 if not v1[x[0]][x[1:]]]
    neg_v1 = {f: sum(v for k, v in v1[f].items() if k[0] == "error") for f in VALIDAS_30}
    err_v2 = sorted({(g, k[1], k[2]) for g, c in v2.items() for k in c if k[0] == "error" and g != "cap3"}    # los 7 fragmentos,
                    - ERRORES_MARCADOS_V2)                                                                 # marcados enteros
    avisos_v2 = {g: {"%s %s" % (k[1], k[2]): v for k, v in sorted(c.items()) if k[0] == "aviso"} for g, c in sorted(v2.items())}
    return {"positivo_v1_falta": falta, "negativo_v1_errores": neg_v1, "errores_v2_fuera_de_lo_marcado": err_v2,
            "avisos_v2": avisos_v2}


def unidades():
    import hacer_resto_v2 as R
    textos = R.origenes()
    mal = []
    for o in R.ORIGENES:
        t = textos[o].decode("utf-8")
        lug = {norm(h["lugar"]) for h in CT.comprobar(t) if h["regla"] == "tabla_hl7" and h["valor"] == "UCUM"}
        g = R.gemelo(t)[0]
        lug_g = {norm(h["lugar"]) for h in CT.comprobar(g) if h["lugar"].split(".")[0].split("(")[0] in ("OBX-6", "RXA-7")
                 and h["regla"] == "tabla_hl7"}
        if not lug or not lug <= {"OBX-6.3", "RXA-7.3"} or lug_g:
            mal.append({"origen": o, "ucum": sorted(lug), "gemelo": sorted(lug_g)})
    return {"n": len(R.ORIGENES), "mal": mal}


if __name__ == "__main__":
    r = {"mutantes": mutantes(), "corpus": corpus(), "unidades": unidades(), "no_contados": dict(sorted(CT.NO_CONTADOS.items()))}
    ok = (not r["mutantes"]["mal"] and not r["corpus"]["positivo_v1_falta"] and not any(r["corpus"]["negativo_v1_errores"].values())
          and not r["corpus"]["errores_v2_fuera_de_lo_marcado"] and not r["unidades"]["mal"])
    r["veredicto"] = "TODO BIEN" if ok else "MAL"
    json.dump(r, open(os.path.join(GA, "CONTROL-TIPOS.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("mutantes: %d (%d debe, %d no_debe), mal %d" % (r["mutantes"]["n"], r["mutantes"]["debe"], r["mutantes"]["no_debe"],
                                                         len(r["mutantes"]["mal"])))
    for x in r["mutantes"]["mal"]:
        print("   MAL", x)
    print("positivo v1, falta:", r["corpus"]["positivo_v1_falta"])
    print("negativo v1, errores:", r["corpus"]["negativo_v1_errores"])
    print("errores v2 fuera de lo marcado:", r["corpus"]["errores_v2_fuera_de_lo_marcado"])
    print("unidades: %d orígenes, mal %s" % (r["unidades"]["n"], r["unidades"]["mal"]))
    print("CONTROL DEL COMPROBADOR:", r["veredicto"])
    sys.exit(0 if ok else 1)
