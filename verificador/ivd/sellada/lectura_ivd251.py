#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 32, la 2.5.1 (ANTES-ETAPA-IVDECLARADA.md, Q-VD-2): la lectura de la 31 con el texto de v2.5.1, hecha con
ivd/hacer_lectura_ivd.py. Lo que sigue es la cabecera de la 31.
Etapa 31 (ANTES-ETAPA-IVMUESTRAS.md): la lectura de la etapa 30 (iv/lectura_iv.py), para las muestras públicas, con Q-MV-2
(ivm/decision-jev-qmv.md): lo que no se puede leer con el texto de v2.5 va APARTE y no entra en el veredicto (un segmento o un
campo que v2.5 no define, una tabla que su índice no trae). MSH-12 con otra versión queda sin decidir, como en la 30
(Q-MV-3, ivm/decision-jev-qmv3.md). Hecho con ivm/hacer_lectura_ivm.py.
Lo que sigue es la cabecera de la 30.
Etapa 30 (iv/diseno-iv-fable.md §3.4; Q-IV-D-5: lee el conductor, con cita): cada lugar que cuenta, leído en el texto de v2.5.
- R: la OPT del campo en su tabla de atributos («HL7 Attribute Table - SEG»), del texto de v2.5 (no de la extracción de 2.5.1).
- L: su LEN en esa tabla, frente a la longitud de cada valor.
- T_HL7: el tipo de la tabla en el índice del Apéndice A («HL7» o «User»); el nulo «""» no es un valor fuera de tabla
  (CH02.txt:392); si el valor está en el Apéndice A, no cuenta.
- E: la estructura del mensaje, con el capítulo donde se define.
Escribe LECTURAS-IV.json (publicable: número de tabla, OPT, LEN y citas de fichero y línea, sin texto del estándar) y la tabla
de lugares en pantalla.
  python3 iv/lectura_iv.py <FILAS-IV.jsonl> <txt de v2.5> <LECTURAS-IV.json> <corpus>
(escribe también VEREDICTOS-IV.jsonl junto a LECTURAS-IV.json: el veredicto sostenido de cada mensaje)"""
import collections
import glob
import json
import os
import re
import sys

FILAS, TXT, SAL = sys.argv[1:4]
assert SAL.endswith("LECTURAS-IVD251.json"), "la salida tiene que llamarse LECTURAS-IVD251.json"
AQUI = os.path.dirname(os.path.abspath(__file__))
PRIV = os.path.normpath(os.path.join(AQUI, "..", "..", "privado"))
TV = json.load(open(os.path.join(PRIV, "ivd", "TABLAS-VALORES-IVD251.json"), encoding="utf-8"))   # etapa 32: los de v2.5.1
VALORES = {k: set(v) for k, v in TV["valores"].items()}
PATRONES = {k: [re.compile(x) for x in v] for k, v in TV["patrones"].items()}

# las tablas de atributos y el índice de tablas del Apéndice A
ATR = collections.defaultdict(dict)
FILA = re.compile(r"^\s+(\d+)\s+(\d+)\s+([A-Z][A-Z0-9]{1,2}|varies|varie)\s+((?:\(B\)\s*)?(?:R|O|C|B|X|W|RE))\b(.*)$")
for f in sorted(glob.glob(os.path.join(TXT, "*.txt"))):
    seg = None
    for n, l in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
        m = re.search(r"HL7 Attribute Table\s*[-–]\s*([A-Z][A-Z0-9]{2})\b", l)
        if m:
            seg = m.group(1)
            continue
        if seg:
            m = FILA.match(l)
            if m:
                seq = int(m.group(1))
                tbl = re.search(r"\b(\d{4})\b", m.group(5))
                ATR[seg].setdefault(seq, {"len": int(m.group(2)), "dt": m.group(3), "opt": re.sub(r"\s+", " ", m.group(4)),
                                          "tbl": tbl.group(1) if tbl else None, "cita": "%s:%d" % (os.path.basename(f), n)})
            elif re.match(r"^\s*\d+\.\d+", l) and ATR[seg]:
                seg = None
INDICE = {}
for n, l in enumerate(open(os.path.join(TXT, "AppendixA.txt"), encoding="utf-8", errors="replace"), 1):
    m = re.match(r"^\s*(HL7|User)\s+(\d{4})\s+\S", l)
    if m:
        INDICE.setdefault(m.group(2), {"tipo": m.group(1), "cita": "AppendixA.txt:%d" % n})


def en_tabla(t, v):
    return v in VALORES.get(t, ()) or any(r.match(v) for r in PATRONES.get(t, ()))


F = [json.loads(l) for l in open(FILAS, encoding="utf-8")]
assert F and all(f.get("version") == "2.5.1" for f in F), "la lectura de la 2.5.1 recibe filas de otra versión"


def considerar(p):
    """La clase con la que se lee un error: lo que cuenta, y además los T_USR de una tabla que el índice del Apéndice A da como de
    HL7 (el apartado previo se hizo con la mayoría del texto; la lectura manda el índice, como dice el resultado)."""
    if p["cuenta"]:
        return p["clase"]
    if p["clase"] == "T_USR" and (INDICE.get(p.get("tabla")) or {}).get("tipo") == "HL7":
        return "T_HL7"
    return None


lugares = collections.OrderedDict()
for f in F:
  for v in f["variantes"].values():                # todas las variantes: la que mande tiene que estar leída
    for p in v["errores"]:
        clase = considerar(p)
        if clase is None:
            continue
        clave = "%s|%s|%s|%s" % (clase, p.get("seg"), p.get("campo") or "", p.get("tabla") or "")
        x = lugares.setdefault(clave, {"clase": clase, "seg": p.get("seg"), "campo": p.get("campo"), "tabla": p.get("tabla"),
                                       "mensajes": set(), "corpus": collections.Counter(), "valores": collections.Counter(),
                                       "longitudes": collections.Counter(), "doctypes": set(),
                                       "reclasificado": not p["cuenta"]})
        x["doctypes"].add(v.get("doctype") or "")
        if f["id"] not in x["mensajes"]:
            x["corpus"][f["corpus"]] += 1
        x["mensajes"].add(f["id"])
        if p["clase"].startswith("T"):
            x["valores"][p.get("valor")] += 1
        if p["clase"] == "L":
            x["longitudes"][p.get("longitud_valor")] += 1
CAPITULO_DE = {"ADT": "Ch03.txt", "ORU": "CH07.txt", "VXU": "CH04.txt", "MDM": "CH09.txt"}
out = []
for clave, x in lugares.items():
    a = ATR.get(x["seg"], {}).get(x["campo"]) if x["campo"] else None
    r = {"lugar": clave, "clase": x["clase"], "seg": x["seg"], "campo": x["campo"], "tabla": x["tabla"],
         "n_mensajes": len(x["mensajes"]), "corpus": dict(x["corpus"]), "valores": dict(x["valores"]),
         "longitudes": {str(k): n for k, n in x["longitudes"].items()}, "atributo_v251": a}
    if x["clase"] == "R":
        r["sostenida"] = bool(a and a["opt"].endswith("R"))
        r["cita"] = a["cita"] if a else None
        r["razon"] = ("%s-%d es %s en la tabla de atributos de v2.5.1" % (x["seg"], x["campo"], a["opt"]) if a else
                      "no encuentro %s-%d en las tablas de atributos de v2.5.1" % (x["seg"], x["campo"]))
    elif x["clase"] == "L":
        largos = [int(k) for k in x["longitudes"] if k is not None]
        r["sostenida"] = bool(a and largos and min(largos) > a["len"])
        r["cita"] = a["cita"] if a else None
        r["razon"] = ("LEN %d en v2.5.1; los valores miden %s" % (a["len"], sorted(set(largos))) if a else "sin LEN en v2.5.1")
    elif x["clase"] == "T_HL7":
        idx = INDICE.get(x["tabla"])
        vals = list(x["valores"])
        nulos = [v for v in vals if v == '""']
        fuera = [v for v in vals if v != '""' and not en_tabla(x["tabla"], v)]
        if idx and idx["tipo"] == "User":
            r["sostenida"], r["razon"] = False, "la tabla %s es de usuario en el índice del Apéndice A" % x["tabla"]
        elif nulos and not fuera:
            r["sostenida"], r["razon"] = False, 'el valor es el nulo de HL7 («""»), que no es un valor de tabla (v2.5.1, CH02.txt:374)'
        elif fuera:
            r["sostenida"], r["razon"] = None, ("tabla %s de HL7; %s no están en su lista impresa: sin decidir, porque el texto "
                                                "permite extender las tablas de HL7 (v2.5.1, CH02.txt:542; Q-IV-D-11)" % (x["tabla"], fuera))
        else:
            r["sostenida"], r["razon"] = False, "todos los valores están en la tabla del Apéndice A"
        r["cita"] = idx["cita"] if idx else None
        r["tipo_en_indice"] = idx["tipo"] if idx else None
    elif x["clase"] in ("E", "Z"):
        r["sostenida"] = True
        r["razon"] = "estructura del mensaje (segmento %s): IRIS lo echa en falta o no lo esperaba" % x["seg"]
        citas = []
        for dt in sorted(d for d in x["doctypes"] if d):
            est = dt.split(":")[-1]
            cap = CAPITULO_DE.get(est[:3])
            if not cap:
                continue
            for n, l in enumerate(open(os.path.join(TXT, cap), encoding="utf-8", errors="replace"), 1):
                if re.match(r"^\s+[A-Z]{3}\^[A-Z0-9]{3}\^%s\s" % re.escape(est), l):
                    citas.append("%s:%d (estructura %s)" % (cap, n, est))
                    break
        r["cita"] = "; ".join(citas) or None
    else:
        r["sostenida"], r["razon"], r["cita"] = None, "sin lectura automática", None
    r["reclasificado_por_el_indice"] = x["reclasificado"]
    out.append(r)
LECT = {r["lugar"]: r for r in out}
# por valor y por mensaje (escrito después de la corrida, cuarto bloque del sello): un error se sostiene si su lugar se sostiene,
# salvo lo que leen las reglas de abajo; en una tabla de HL7, lo que está fuera de su lista impresa queda sin decidir (Q-IV-D-11).
CORPUS = sys.argv[4] if len(sys.argv) > 4 else None
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), "iv"))       # el conductor de la 30
import validar_iv as V  # noqa: E402


def componente(segs, idx, campo, rep, comp):
    fs, cs, rs, _ = V.separadores(segs)
    if not 1 <= idx <= len(segs):
        return ""
    r = V.leer(segs, idx, campo, rep)
    c = r.split(cs)
    return c[comp - 1] if comp - 1 < len(c) else ""


EQUIVALENTES = {("0191", "TEXT"): None, ("0191", "multipart"): None, ("0125", "XPN"): None}   # None: no hay uno que quepa
RAZON_EQUIVALENTE = {
    ("0191", "TEXT"): "TX tiene la misma descripción pero es «HL7 V2.2 only» (v2.5.1, AppendixA.txt:3473): no hay equivalente en v2.5",
    ("0191", "multipart"): "la 0191 no trae otro valor con su descripción (v2.5.1, AppendixA.txt:3467)",
    ("0125", "XPN"): "PN tiene otra descripción (v2.5.1, AppendixA.txt:2881, 2894): no hay equivalente",
}
EXTERNAS = {"0399": ("ISO 3166, forma de tres letras (v2.5.1, CH02.txt:4451-4456)", {"ESP", "USA", "GBR"})}   # los de las muestras
# (USA y GBR, leídos tras la revisión a ciegas; US, JP, 764, 44 y 999990000 no tienen la forma de tres letras)   # tablas sin lista impresa
EXTENDER = "Q-IV-D-11 (decision-jev-qiv11b.md): fuera de la lista impresa; el texto permite extender las tablas de HL7 (v2.5.1, CH02.txt:542)"


def clon_estructural(segs, errores):
    """El mensaje sobre el que corrieron dr, dl, dt y dn: el original sin los segmentos que quitó la pasada dm, en su orden."""
    c = list(segs)
    for p in errores:
        if p.get("pasada") == "dm" and p.get("enmudecido") == "quitado" and 1 <= p.get("idx", 0) <= len(c):
            c = c[:p["idx"] - 1] + c[p["idx"]:]
    return c


def principal_ivm(f):
    """La variante que manda: la de MSH-9.3, salvo que su estructura no exista en el esquema de su versión (IRIS: «no DocType set»);
    entonces, la de la 0354. -> (variante, si MSH-9.3 no tenía estructura)."""
    vs = f["variantes"]
    m = vs.get("msh93")
    if m and vs.get("esquema") and any("no DocType set" in (p.get("crudo") or "") for p in m["errores"]):
        return vs["esquema"], True
    return (m or vs.get("esquema") or vs.get("ninguna")), False


def aparte_ivm(clase, p):
    """Q-MV-2 (en la 32, con el texto de v2.5.1): el motivo por el que un error no se lee con el texto, o None."""
    seg, campo, tabla = p.get("seg"), p.get("campo"), p.get("tabla")
    if seg and seg not in ATR and not seg.startswith("Z"):
        return "segmento sin tabla de atributos en v2.5.1"
    if clase in ("R", "L") and campo and campo not in ATR.get(seg, {}):
        return "campo que la tabla de atributos de v2.5.1 no trae"
    if clase.startswith("T") and tabla and tabla not in INDICE:
        return "tabla que el índice del Apéndice A de v2.5.1 no trae"
    return None


veredictos = []
ajustes = collections.Counter()
por_error = collections.defaultdict(collections.Counter)
for f in F:
    v, sin_estructura = principal_ivm(f)
    orig = V.segmentos(open(os.path.join(CORPUS, f["id"]), encoding="utf-8").read()) if CORPUS else []
    segs = clon_estructural(orig, v["errores"])
    sost, nd, aparte = [], [], []
    for p in v["errores"]:
        clase = considerar(p)
        if clase is None:
            continue
        clave = "%s|%s|%s|%s" % (clase, p.get("seg"), p.get("campo") or "", p.get("tabla") or "")
        motivo_aparte = aparte_ivm(clase, p)                       # Q-MV-2: no se lee con v2.5, va aparte
        if motivo_aparte:
            aparte.append({"lugar": clave, "valor": p.get("valor"), "por": motivo_aparte})
            ajustes[(clave, "aparte: " + motivo_aparte)] += 1
            continue
        ok = LECT[clave]["sostenida"] if clave in LECT else True
        por = None if p["cuenta"] else "reclasificado por el índice del Apéndice A"
        if clase == "T_HL7":
            a = ATR.get(p["seg"], {}).get(p["campo"]) or {}
            sistema = componente(segs, p["idx"], p["campo"], p["rep"], 3) if segs and p.get("comp") == 1 else ""
            idx = INDICE.get(p["tabla"]) or {}
            if idx.get("tipo") == "User":
                ok, por = False, "tabla de usuario en el índice del Apéndice A"
            elif p.get("valor") == '""':
                ok, por = False, "nulo"
            elif (a.get("dt") in ("CE", "CWE", "CNE") and p.get("comp") == 1 and sistema and sistema != "HL7" + p["tabla"]):
                ok, por = False, "valor de otro sistema (%s)" % sistema
            elif en_tabla(p["tabla"], p.get("valor") or ""):
                ok, por = False, "en la tabla"
            elif p["tabla"] in EXTERNAS:
                ref, validos = EXTERNAS[p["tabla"]]
                ok, por = (False, "tabla externa, %s: «%s» es suyo" % (ref, p.get("valor"))) if p.get("valor") in validos else \
                    (None, "tabla externa, %s: sin leer" % ref)
            elif clave == "T_HL7|OBX|2|0125" and p.get("valor") == "CWE":
                ok, por = None, ("OBX-2 «CWE»: la 0125 impresa no lo trae, y v2.5.1, CH07.txt:2593, dice que todos los tipos de HL7 valen "
                                 "salvo CM, CQ, SI e ID (el estándar se contradice)")
            else:
                ok, por = None, EXTENDER
        # Q-IV-D-12 (Jev, decision-jev-qiv12b.md): un valor que la tabla del campo admite pero no cabe en su LEN cuenta solo si
        # la tabla trae otro equivalente (la misma descripción) que cabe y vale en v2.5; si no, sin decidir.
        if clase == "L" and segs:
            a = ATR.get(p["seg"], {}).get(p["campo"]) or {}
            valor = V.leer(segs, p["idx"], p["campo"], p.get("rep") or 1)
            tbl = a.get("tbl")
            if tbl and valor in VALORES.get(tbl, ()):
                eq = EQUIVALENTES.get((tbl, valor), "sin_leer")
                if eq is None:
                    ok, por = None, "%s «%s»: está en la %s y no cabe en el LEN %d; %s" % (
                        "%s-%d" % (p["seg"], p["campo"]), valor, tbl, a.get("len"), RAZON_EQUIVALENTE[(tbl, valor)])
                elif eq == "sin_leer":
                    ok, por = None, "%s «%s»: está en la %s y no cabe en el LEN; equivalente sin leer" % (p["seg"], valor, tbl)
                elif len(eq) <= (a.get("len") or 0):
                    ok, por = True, "%s «%s»: la %s trae «%s», equivalente, que cabe" % (p["seg"], valor, tbl, eq)
            if clave == "L|OBX|2|" and valor == "CWE":
                ok, por = None, ("OBX-2 «CWE»: no cabe en el LEN 2 (v2.5.1, CH07.txt:2529), y el texto lo admite (CH07.txt:2593): el "
                                 "estándar se contradice")
        if por and (por != "reclasificado por el índice del Apéndice A"):
            ajustes[(clave, por if not por.startswith("Q-IV-D-11") else "Q-IV-D-11b: sin decidir")] += 1
        e = {"lugar": clave, "valor": p.get("valor"), "sistema_0396": clase == "T_HL7" and p.get("tabla") == "0396",
             "idx": p.get("idx"), "rep": p.get("rep"),                # dónde está, en el clon (tercera revisión)
             "leido": V.leer(segs, p["idx"], p["campo"], p.get("rep") or 1) if clase == "L" and segs else None}
        por_error[clave]["sostenido" if ok else ("sin_decidir" if ok is None else "no_cuenta")] += 1
        if ok:
            sost.append(e)
        elif ok is None:
            nd.append(dict(e, por=por))
    if sin_estructura:                               # MSH-9.3 sin estructura en v2.5: fuera de la 0354 impresa (Q-IV-D-11)
        nd.append({"lugar": "T_HL7|MSH|9|0354", "valor": f["doctype_msh93"], "sistema_0396": False,
                   "por": "MSH-9.3 sin estructura en el esquema 2.5.1; se valida con la de la 0354 (Q-IV-D-2 y Q-IV-D-11)"})
    sin_leer = sorted(s for s, fin in v["fines"].items() if s != "dn" and fin in ("no_reconocido", "tope_alcanzado", "no_enmudecible"))
    if sin_leer and not sost:                        # una pasada sin leer entera: la muestra no puede salir válida
        nd.append({"lugar": "aparato", "valor": None, "sistema_0396": False, "por": "pasadas sin leer enteras: %s" % ", ".join(sin_leer)})
    veredictos.append({"id": f["id"], "corpus": f["corpus"], "version": f["version"], "veredicto_iris_que_cuenta": v["veredicto_que_cuenta"],
                       "veredicto_sostenido": "invalido" if sost else ("no_decidible" if nd else "valido"),
                       "solo_0396": bool(sost) and all(e["sistema_0396"] for e in sost),
                       "sostenidos": sost, "no_decidibles": nd, "aparte": aparte})
with open(os.path.join(os.path.dirname(SAL), "..", "..", "privado", "iv", "VEREDICTOS-IV.jsonl")
          if False else SAL.replace("LECTURAS-IVD251.json", "VEREDICTOS-IVD251.jsonl"), "w", encoding="utf-8") as fh:
    for x in veredictos:
        fh.write(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n")
for r in out:                                   # lo que decide es la lectura error a error; el lugar lleva su recuento
    r["resultado_por_error"] = dict(por_error.get(r["lugar"], {}))
json.dump({"lecturas": out, "ajustes_por_valor": [{"lugar": k, "por": p, "n": n} for (k, p), n in sorted(ajustes.items())],
           "atributos_leidos": sum(len(v) for v in ATR.values()), "indice_tablas": len(INDICE)},
          open(SAL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ajustes por valor:")
for (k, p), n in sorted(ajustes.items()):
    print("  %4d %s: %s" % (n, k, p))
cuenta = collections.defaultdict(collections.Counter)
for x in veredictos:
    cuenta[x["corpus"]][x["veredicto_sostenido"]] += 1
    if x["solo_0396"]:
        cuenta[x["corpus"]]["solo_0396"] += 1
t = collections.Counter()
for c in sorted(cuenta):
    t.update(cuenta[c])
    print("  %-14s %s" % (c, dict(cuenta[c])))
print("  %-14s %s" % ("TOTAL", dict(t)))
print("tablas de atributos: %d segmentos, %d campos; índice de tablas: %d" % (len(ATR), sum(len(v) for v in ATR.values()), len(INDICE)))
for r in sorted(out, key=lambda r: -r["n_mensajes"]):
    print("%-26s %4d  %-5s %-22s %s | %s" % (r["lugar"], r["n_mensajes"], r["sostenida"], (r.get("cita") or "-"), r["razon"][:90],
                                          dict(list(r["valores"].items())[:3]) if r["valores"] else ""))
