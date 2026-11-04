#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 30 (iv/diseno-iv-fable.md §3-4; Q-IV-D-4, -6 y -7 en iv/decision-jev-qiv.md): los dos cruces.
1. Con los auditores de la 29 (VXU y ORU, 162 mensajes), en lo que los dos pueden ver (E, R, L, tablas de HL7): por mensaje, por
   mensaje y clase, y por lugar (segmento y campo), que es lo que manda en la frase. Lo de IRIS que cuenta es lo sostenido en
   LECTURAS-IV.json; lo de los auditores, sus defectos firmes de clase comparable (AUDITORES-CLASIFICADOS-IV.json, sellado). La
   0396 (UCUM, SCT), que la 29 dejó aparte como duda de sistema y aquí cuenta (Q-IV-D-11), se da también aparte.
2. Con las 27 nuevas publicadas (15 del estudio de conversores, 9 de VXU, 3 de MDM): afectada si todos sus mensajes de apoyo del
   laboratorio son inválidos por una regla sostenida que toca el campo del hallazgo; tocada si alguno; intacta si ninguno;
   indeterminada sin apoyo del laboratorio. Los apoyos de CV3 son sus ejemplos y su par (incompletos, Q-IV-D-7); las muestras
   públicas de los proyectos quedan fuera.
  python3 iv/cruce_iv.py <publicación>/verificador <VEREDICTOS-IV.jsonl> <CRUCE-IV.json>"""
import collections
import json
import os
import re
import sys

VER, VEREDICTOS, SAL = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3]
AQUI = os.path.dirname(os.path.abspath(__file__))
VD = {json.loads(l)["id"]: json.loads(l) for l in open(VEREDICTOS, encoding="utf-8")}
AUD = json.load(open(os.path.join(AQUI, "AUDITORES-CLASIFICADOS-IV.json"), encoding="utf-8"))
COMPARABLES = {"E", "R", "L", "T_HL7", "N"}


def lugar_iris(e):
    c, s, f, t = e["lugar"].split("|")
    return "%s-%s" % (s, f) if f else s


def a_iv(fich):
    b = os.path.basename(fich)
    for pre, nuevo in (("vxu/", "lab/vxu/VXU-"), ("pares_vxu/", "vxu-pares/"), ("oru/", "lab/oru/ORU-"), ("pares_oru/", "lab/minimos/")):
        if fich.startswith(pre):
            return nuevo + b
    return None


# ------------------------------------------------------------------------------------------------ 1. los auditores
aud_def = collections.defaultdict(set)      # fichero de iv -> lugares firmes comparables
aud_duda = collections.defaultdict(set)
for d in AUD["defectos"]:
    iv = a_iv(d["fichero"])
    if d["clase"] in COMPARABLES and d["lugar"]:
        (aud_def if d["nivel"] == "defecto" else aud_duda if d["nivel"] == "duda" else {}).setdefault(iv, set()) if False else None
        if d["nivel"] == "defecto":
            aud_def[iv].add(d["lugar"])
        elif d["nivel"] == "duda":
            aud_duda[iv].add(d["lugar"])
auditados = sorted(a_iv(f) for f in AUD["ficheros"])
no_encontrados = [f for f in auditados if f not in VD]


def cruce(sin_0396):
    m = collections.Counter()
    por_clase = {c: collections.Counter() for c in ("E", "R", "L", "T")}
    lug_ambos, lug_iris, lug_aud, discrepancias = 0, 0, 0, []
    campos = {"los_dos": set(), "solo_iris": set(), "solo_auditores": set()}
    for f in auditados:
        if f not in VD:
            continue
        v = VD[f]
        iris = {lugar_iris(e) for e in v["sostenidos"] if not (sin_0396 and e["sistema_0396"])}
        iris_nd = {lugar_iris(e) for e in v["no_decidibles"]}
        aud = aud_def.get(f, set())
        duda = aud_duda.get(f, set())
        for c in ("E", "R", "L", "T"):                 # por mensaje y clase
            ci = any(e["lugar"].split("|")[0].startswith(c) for e in v["sostenidos"] if not (sin_0396 and e["sistema_0396"]))
            ca = any(d["clase"].startswith(c) for d in AUD["defectos"] if a_iv(d["fichero"]) == f and d["nivel"] == "defecto"
                     and d["clase"] in COMPARABLES)
            por_clase[c][(ci, ca)] += 1
        lado_aud = "invalido" if aud else ("duda" if duda else "valido")
        lado_iris = "invalido" if iris else ("no_decidible" if v["no_decidibles"] else "valido")
        m[(lado_iris, lado_aud)] += 1
        lug_ambos += len(iris & aud)
        lug_iris += len(iris - aud)
        lug_aud += len(aud - iris)
        campos["los_dos"] |= iris & aud
        campos["solo_iris"] |= iris - aud
        campos["solo_auditores"] |= aud - iris
        for l in sorted(iris ^ aud):
            discrepancias.append({"mensaje": f, "lugar": l, "lo_ve": "IRIS" if l in iris else "auditores",
                                  "duda_del_auditor": l in duda, "iris_lo_deja_sin_decidir": l in iris_nd})
    a = sum(m[(x, x)] for x in ("valido", "invalido"))
    n2 = sum(m[(i, j)] for i in ("valido", "invalido") for j in ("valido", "invalido"))
    po = a / n2 if n2 else None
    pi = sum(m[("invalido", j)] for j in ("valido", "invalido")) / n2 if n2 else 0
    pa = sum(m[(i, "invalido")] for i in ("valido", "invalido")) / n2 if n2 else 0
    pe = pi * pa + (1 - pi) * (1 - pa)
    kappa = (po - pe) / (1 - pe) if n2 and pe < 1 else None
    total = lug_ambos + lug_iris + lug_aud
    return {"matriz": {"%s|%s" % k: n for k, n in sorted(m.items())}, "acuerdo_mensaje": po, "kappa": kappa, "n_mensajes_2x2": n2,
            "fuera_del_2x2": sum(n for (i, j), n in m.items() if i not in ("valido", "invalido") or j not in ("valido", "invalido")),
            "positivos_iris": sum(m[("invalido", j)] for j in ("valido", "invalido")),
            "positivos_auditores": sum(m[(i, "invalido")] for i in ("valido", "invalido")),
            "lugares": {"unidad": "pares mensaje-campo", "los_dos": lug_ambos, "solo_iris": lug_iris, "solo_auditores": lug_aud,
                        "alguno": total, "los_dos_entre_alguno": lug_ambos / total if total else None},
            "campos_distintos": {k: sorted(v) for k, v in campos.items()},
            "por_mensaje_y_clase": {c: {"los_dos": x[(True, True)], "solo_iris": x[(True, False)],
                                        "solo_auditores": x[(False, True)], "ninguno": x[(False, False)]}
                                    for c, x in por_clase.items()},
            "discrepancias": discrepancias}


AUDITORES = {"con_0396": cruce(False), "sin_0396": cruce(True), "auditados": len(auditados), "no_encontrados": no_encontrados}
# la lectura de cada discrepancia (Q-IV-D-5: el conductor, con cita; 4-nov)
LECTURA_DISCREPANCIA = {
    ("lab/oru/ORU-B15.hl7", "MSH-12"): {"tiene_razon": "IRIS", "cita": "AppendixA.txt:984 (tabla 0104)",
                                         "razon": "«2.6» no está en la 0104 de v2.5; el auditor lo anotó y lo dejó como nota"},
    ("lab/vxu/VXU-B39.hl7", "MSH-9"): {"tiene_razon": "auditores", "cita": "CH02A.txt:2809 (MSG.3, R)",
                                        "razon": "MSG.3 es obligatorio; IRIS no mira la obligatoriedad de los componentes"},
    ("lab/oru/ORU-B39.hl7", "OBX-11"): {"tiene_razon": "ninguno: sin decidir", "cita": "AppendixA.txt:742 (0085); CH02.txt:564",
                                         "razon": "«f» no está en la 0085 impresa, que trae «F»; el texto permite extender las tablas "
                                                  "de HL7 con valores locales (Q-IV-D-11)"},
}
for k in ("con_0396", "sin_0396"):
    for d in AUDITORES[k]["discrepancias"]:
        d.update(LECTURA_DISCREPANCIA.get((d["mensaje"], d["lugar"]), {}))

# ------------------------------------------------------------------------------------------------ 2. las nuevas
CV = json.load(open(os.path.join(VER, "cv", "CLASES-CV3.json"), encoding="utf-8"))["clases"]
VX = json.load(open(os.path.join(VER, "vx", "CLASES-VX3.json"), encoding="utf-8"))["clases"]
MD = json.load(open(os.path.join(VER, "md", "CLASES-MD3.json"), encoding="utf-8"))["clases"]
HM = {h["id"]: h for h in json.load(open(os.path.join(VER, "md", "HALLAZGOS-MD3-r1.json"), encoding="utf-8"))["hallazgos"]}
CAMPOS_CV = {   # el campo de cada nueva, leído de su «que»; un segmento solo vale para todo el segmento
    "M-7": ["PV1-8"], "M-10": ["PID-16"], "M-18": ["PDA", "PID-29", "PID-30"], "M-23": ["PID"], "M-24": ["OBX-5"],
    "L-1": ["PV1-3"], "L-10": ["PID-16"], "L-11": ["PID-11"], "L-12": ["PID-8"], "L-15": ["OBX-2"], "L-16": ["OBX-2", "OBX-5"],
    "L-18": ["OBX-11"], "L-19": ["OBR-25"], "L-20": ["OBX-5"], "L-22": ["PV1-52"]}
AU = {"VX-M15": ["au-pares/AU1-caso.hl7"], "VX-L8": ["au-pares/AU2-caso.hl7"], "L-19": ["au-pares/AU3-caso.hl7"]}
PAR_MD = {"MD-L3": "MP5", "MD-L5": "MP4", "MD-M5": "MP1"}
CAMPOS_MD = {"MD-L3": ["OBX-5"], "MD-L5": ["OBX-5"], "MD-M5": ["TXA-8", "MSH-9"]}
nuevas = []
for c in CV:
    if c.get("clase") != "nueva":
        continue
    apoyo = ["lab/adt/%s.hl7" % e for e in (c.get("ejemplos") or {}).get("adt", [])] + \
            ["lab/oru/%s.hl7" % e for e in (c.get("ejemplos") or {}).get("oru", [])]
    for p in re.split(r"\s*/\s*", c.get("par_minimo") or ""):
        if p:
            apoyo.append("lab/minimos/%s-caso.hl7" % p)
    nuevas.append({"id": c["id"], "juez": "CV3", "campos": CAMPOS_CV[c["id"]], "apoyo": apoyo + AU.get(c["id"], []),
                   "completo": False, "muestras_fuera": len((c.get("ejemplos") or {}).get("muestras", []))})
for c in VX:
    if c.get("clase") != "nueva":
        continue
    apoyo = ["lab/vxu/VXU-%s.hl7" % b for b in re.findall(r"\bB\d{2}\b", c.get("casos") or "")]
    if c.get("par_minimo"):
        apoyo.append("vxu-pares/%s-caso.hl7" % c["par_minimo"])
    nuevas.append({"id": c["id"], "juez": "VX3", "campos": [c["hecho"]], "apoyo": apoyo + AU.get(c["id"], []), "completo": True,
                   "muestras_fuera": len(re.findall(r"\bL\d+\b|lfh-", c.get("casos") or ""))})
for c in MD:
    if c.get("clase") != "nueva":
        continue
    h = HM[c["hallazgo"].split()[0]]
    apoyo = ["lab/mdm/%s.hl7" % b for b in h.get("bases", [])] + ["mdm-pares/%s-con.hl7" % PAR_MD[c["id"]]]
    nuevas.append({"id": c["id"], "juez": "MD3", "campos": CAMPOS_MD[c["id"]], "apoyo": apoyo, "completo": True,
                   "muestras_fuera": len(h.get("muestras", []))})


def toca(e, campos):
    l = lugar_iris(e)
    return any(l == x or (("-" not in x) and l.split("-")[0] == x) for x in campos)


for n in nuevas:
    estado = collections.Counter()
    detalle = []
    for f in n["apoyo"]:
        v = VD.get(f)
        if v is None:
            estado["no_encontrado"] += 1
            detalle.append({"mensaje": f, "estado": "no_encontrado"})
            continue
        t = [e for e in v["sostenidos"] if toca(e, n["campos"])]
        s = "invalido_en_su_campo" if t else ("invalido_por_otra_regla" if v["sostenidos"] else
                                             ("no_decidible" if v["no_decidibles"] else "valido"))
        estado[s] += 1
        detalle.append({"mensaje": f, "estado": s, "reglas": sorted({lugar_iris(e) for e in (t or v["sostenidos"])}),
                        "sin_decidir": sorted({e["lugar"] for e in v["no_decidibles"]})})
    nuestros = sum(estado[k] for k in ("invalido_en_su_campo", "invalido_por_otra_regla", "no_decidible", "valido"))
    inval = estado["invalido_en_su_campo"] + estado["invalido_por_otra_regla"]
    n["criterio_del_antes"] = ("todo_invalido" if nuestros and inval == nuestros else
                               "alguno_invalido" if inval else "ninguno_invalido")   # cualquier regla sostenida (ANTES)
    n["con_algun_apoyo_valido"] = estado["valido"] > 0
    if not nuestros:
        n["estado"] = "indeterminada"
    elif estado["invalido_en_su_campo"] == nuestros:
        n["estado"] = "afectada"
    elif estado["invalido_en_su_campo"]:
        n["estado"] = "tocada"
    else:
        n["estado"] = "intacta"
    n["apoyo_por_estado"] = dict(estado)
    n["detalle"] = detalle
json.dump({"auditores": AUDITORES, "nuevas": nuevas}, open(SAL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k in ("con_0396", "sin_0396"):
    a = AUDITORES[k]
    print("auditores, %s: matriz %s; acuerdo por mensaje %s, kappa %s; lugares %s" % (
        k, a["matriz"], a["acuerdo_mensaje"] and round(a["acuerdo_mensaje"], 3), a["kappa"] and round(a["kappa"], 3), a["lugares"]))
print("auditados %d, no encontrados %s" % (AUDITORES["auditados"], AUDITORES["no_encontrados"]))
print("discrepancias por lugar (sin la 0396):")
for d in AUDITORES["sin_0396"]["discrepancias"]:
    print("   ", d)
est = collections.Counter((n["juez"], n["estado"]) for n in nuevas)
print("nuevas: %s" % sorted(est.items()))
for n in nuevas:
    print("  %-7s %-5s %-10s campos %-22s apoyo %s" % (n["id"], n["juez"], n["estado"], ",".join(n["campos"]), n["apoyo_por_estado"]))
