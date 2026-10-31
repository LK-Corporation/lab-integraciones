#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 26, MD1-b (md/diseno-md.md §8): P-MD-1..27, el juez ante un MDM^T02 convertido por un tercero, con evidencia
sintética. Los Bundles se escriben a mano (no salen del perfil: un fallo de la proyección no se confirmaría a sí mismo); cada
prueba cambia una sola cosa y lleva su control negativo. Mandan las decisiones de Jev (md/decisiones-qmd.md), y en cuatro van
contra la recomendación del diseñador: Q-MD-D-1 (solo T02), Q-MD-D-4 (el literal de TXA-17 cuenta además como fhir_invalido),
Q-MD-D-9 (CA/OB además con status coherente) y, sin ir contra él, las alternativas de confianza baja se prueban aparte.

Dos líneas base pasan hoy y deben seguir pasando (§8): P-MD-1 base (el punto `mdm` de acuse intacto) y P-MD-25 base (las
suites de hoy, el rejuicio y los INFORME de las corridas, y lo que conversion.py y puntos_entrada.py exportan, iguales).
Antes del código (sin el punto mdm_conv ni conversion_mdm) fallan las 27: PE.resolver no conoce el punto, o falta el módulo.
P-MD-24 (su parte del corpus) y P-MD-26 dependen de bases_mdm.py, que es de MD2-a: hasta entonces siguen en rojo, declaradas.
  python3 prueba_conversion_mdm.py          -> TODO BIEN si no hay ningún MAL
  python3 prueba_conversion_mdm.py rojo     -> sale 0 solo si fallan las 27 y pasan las dos líneas base"""
import base64
import copy
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import traceback
from contextlib import redirect_stdout

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(AQUI, "cv")]
_argv, sys.argv = sys.argv, ["x", "--silencio"]
import estructuras_hl7 as EH  # noqa: E402
import mapeador_referencia as MR  # noqa: E402
import puntos_entrada as PE  # noqa: E402
import verificador as V  # noqa: E402
from prueba_conversion import seg, cc, S, ev, texto, con, sin_clave  # noqa: E402
sys.argv = _argv

mal, n_ok, grupo = [], [0], [None]
FALLAN, RAZON = set(), {}
MD2A = {"P-MD-24": "la parte del corpus (generar_corpus con la carpeta mdm)", "P-MD-26": "bases_mdm.py"}


def mira(nombre, obtenido, esperado):
    if obtenido == esperado:
        n_ok[0] += 1
    else:
        print("  MAL %s %s: %r != %r" % (grupo[0], nombre, obtenido, esperado))
        mal.append(nombre)
        FALLAN.add(grupo[0])
        RAZON.setdefault(grupo[0], "MAL %s" % nombre)


def huella(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


# Medidos el 31-oct con el juez bde94016ca58 (HEAD 8502678), antes de MDM (P-MD-1 base y P-MD-25 d).
ANTES = {"mdm": "75ab855348d66163", "C": "5dabbc37ec4a7909", "INFO": "d8b3a2eb651b1ac4", "TIPOS_PROY": "415c77f208321377",
         "CVX.TIPOS": "9cf86194ce1b29a6", "PUNTOS": "08fc6c6fea93f4af", "MAPAS": "6fb1b433ac5d4d8f"}
V2 = "http://terminology.hl7.org/CodeSystem/v2-%s"
V3_CONF = "http://terminology.hl7.org/CodeSystem/v3-Confidentiality"
ALT = "http://hl7.org/fhir/StructureDefinition/alternate-codes"


def b64(x):
    return base64.b64encode(x if isinstance(x, bytes) else x.encode("utf-8")).decode("ascii")


# ---------------------------------------------------------------------------- el mensaje
MSH = {3: "DOCSYS", 4: "CSSYN", 5: "HIS", 6: "SALUD", 7: "20230109101500+0100", 9: "MDM^T02^MDM_T02", 10: "MDM-N1", 11: "P",
       12: "2.5"}
EVN = {1: "T02", 2: "20230109101500+0100"}
PID = {1: "1", 3: "PAC0001^^^CSSYN^MR", 5: "Prueba^Mateo^^^^^L", 7: "20230512", 8: "M"}
PV1 = {1: "1", 2: "O", 19: "V0001"}
ORC = {1: "SC", 2: "PL0001^CSSYN", 3: "FL0001^CSSYN"}
OBR = {1: "1", 2: "PL0001^CSSYN", 3: "FL0001^CSSYN", 4: "DOC-DS^Informe de alta^L"}
TXA = {1: "1", 2: "DS", 3: "TEXT", 6: "20230109101500+0100", 9: "PR01^Ensayo^Ana^^^Dra", 10: "PR02^Muestra^Jorge",
       12: "DOC0001^CSSYN", 16: "/docs/2023/alta0001.txt", 17: "AU", 18: "R", 19: "AV"}
TEXTO = "Paciente estable al alta Zeta010101"
OBX = {1: "1", 2: "TX", 3: "2000.40^MOTIVO^L", 5: TEXTO, 11: "F"}


def junta(base, cambios):
    d = dict(base)
    for k, v in (cambios or {}).items():
        if v is None:
            d.pop(k, None)
        else:
            d[k] = v
    return d


def orden(orc=None, obr=None, nte=(), tq1=False, sin_orc=False):
    s = [] if sin_orc else [seg("ORC", junta(ORC, orc))]
    if tq1:
        s.append(seg("TQ1", {1: "1", 7: "20230109100000+0100"}))
    s.append(seg("OBR", junta(OBR, obr)))
    return s + [seg("NTE", {1: str(k), 3: t}) for k, t in enumerate(nte, 1)]


def obx(k=1, tipo="TX", valor=TEXTO, cod="2000.40^MOTIVO^L", **campos):
    return seg("OBX", junta({1: str(k), 2: tipo, 3: cod, 5: valor, 11: "F"}, campos))


def nte(j, texto_):
    return seg("NTE", {1: str(j), 3: texto_})


def msg(msh=None, evn=None, pid=None, pv1=None, txa=None, ordenes=None, obxs=None, sin_pv1=False, antes_txa=(), despues=(),
        segundo_txa=None, sin_pid=False, extra_cabecera=()):
    """Un MDM^T02: MSH, EVN, PID, PV1, los grupos de orden (por omisión, uno), TXA y sus OBX (por omisión, uno TX)."""
    segs = [seg("MSH", junta(MSH, msh))] + list(extra_cabecera) + [seg("EVN", junta(EVN, evn))]
    if not sin_pid:
        segs.append(seg("PID", junta(PID, pid)))
    if not sin_pv1:
        segs.append(seg("PV1", junta(PV1, pv1)))
    for g in (ordenes if ordenes is not None else [orden()]):
        segs += g
    segs += list(antes_txa)
    segs.append(seg("TXA", junta(TXA, txa)))
    segs += list(obxs if obxs is not None else [obx()])
    if segundo_txa:
        segs += segundo_txa
    segs += list(despues)
    return "\r".join(segs)


# ---------------------------------------------------------------------------- el Bundle (a mano)
def pac(i="p1", ident="PAC0001"):
    return {"resourceType": "Patient", "id": i,
            "identifier": [{"value": ident, "type": cc("0203", "MR"), "assigner": {"display": "CSSYN"}}],
            "name": [{"family": "Prueba", "given": ["Mateo"], "use": "official"}], "birthDate": "2023-05-12", "gender": "male"}


def enc():
    return {"resourceType": "Encounter", "id": "e1", "identifier": [{"value": "V0001"}], "status": "in-progress",
            "class": {"system": S["act"], "code": "AMB"}, "subject": {"reference": "urn:uuid:p1"}}


def adj(texto_=TEXTO, tipo="application/text", **k):
    a = {"contentType": tipo, "data": b64(texto_)} if texto_ is not None else {"contentType": tipo}
    if tipo is None:
        a.pop("contentType")
    a.update(k)
    return {"attachment": a}


def doc(i="d1", **k):
    d = {"resourceType": "DocumentReference", "id": i,
         "masterIdentifier": {"value": "DOC0001", "assigner": {"display": "CSSYN"}},
         "identifier": [{"value": "/docs/2023/alta0001.txt"}],
         "status": "current", "docStatus": "final",
         "type": {"coding": [{"code": "DS"}]},
         "subject": {"reference": "urn:uuid:p1"},
         "date": "2023-01-09T10:15:00+01:00",
         "author": [{"reference": "urn:uuid:pr1"}],
         "authenticator": {"reference": "urn:uuid:pr2"},
         "securityLabel": [{"coding": [{"system": V2 % "0272", "code": "R"}]}],
         "content": [adj()],
         "context": {"encounter": [{"reference": "urn:uuid:e1"}], "related": [{"reference": "urn:uuid:s1"}]}}
    for c, v in k.items():
        if v is None:
            d.pop(c, None)
        else:
            d[c] = v
    return d


def sr(i="s1", plac="PL0001", fill="FL0001", cod="DOC-DS", **k):
    r = {"resourceType": "ServiceRequest", "id": i, "status": "active", "intent": "order", "subject": {"reference": "urn:uuid:p1"},
         "identifier": [{"value": plac, "type": cc("0203", "PLAC")}, {"value": fill, "type": cc("0203", "FILL")}],
         "code": {"coding": [{"system": "urn:local", "code": cod, "display": "Informe de alta"}]}}
    for c, v in k.items():
        if v is None:
            r.pop(c, None)
        else:
            r[c] = v
    return r


def prac(i, ident, family, given):
    return {"resourceType": "Practitioner", "id": i, "identifier": [{"value": ident}], "name": [{"family": family, "given": [given]}]}


PRACS = [prac("pr1", "PR01", "Ensayo", "Ana"), prac("pr2", "PR02", "Muestra", "Jorge")]
PR3 = prac("pr3", "PR03", "Patron", "Irene")


def bundle(d=None, docs=None, srs=None, p=None, e=None, extra=(), sin=()):
    rs = [p or pac(), e or enc()] + (docs if docs is not None else [d or doc()]) + (srs if srs is not None else [sr()]) + PRACS + list(extra)
    return {"resourceType": "Bundle", "type": "collection",
            "entry": [{"fullUrl": "urn:uuid:" + r["id"], "resource": r} for r in rs if r["resourceType"] not in sin]}


def con_doc(**k):
    return bundle(d=doc(**k))


def ev_mdm(m, b=None, **k):
    return ev(m, b, pe="mdm_conv", **k)


def j(e):
    return V.verificar(e)


def cat(r):
    return (r["veredicto"]["categoria"], r["veredicto"].get("subtipo"))


def sh(r):
    """Los que cuentan, como (subtipo, hecho)."""
    return sorted((h["subtipo"], h["hecho"]) for h in r["hallazgos"] if h["cuenta"])


def subs(r, hecho=None):
    return sorted({s for h in r["hallazgos"] if h["cuenta"] and (hecho is None or h["hecho"] == hecho) for s in h["subtipo"].split("+")})


def cuentan(r):
    return sorted((h["clase"], h["subtipo"], h["hecho"]) for h in r["hallazgos"] if h["cuenta"])


def notas(r):
    return sorted({s for h in r["hallazgos"] if not h["cuenta"] for s in (h["subtipo"] or "").split("+")})


def notas_de(r, hecho):
    return sorted({s for h in r["hallazgos"] if not h["cuenta"] and h["hecho"] == hecho for s in (h["subtipo"] or "").split("+")})


def juzga(m=None, b=None, **k):
    return j(ev_mdm(m or msg(), b if b is not None else bundle(), **k))


def juzga_alt(q, m=None, b=None):
    """La sensibilidad preinscrita: el juez con la alternativa de Q (conversion_mdm.ALTERNATIVA_MD)."""
    import conversion as CV
    import conversion_mdm as CVM
    return CV.verificar(ev_mdm(m or msg(), b if b is not None else bundle()), PE.PUNTOS["mdm_conv"], CVM.con_alternativas_md(q))


def emp(r, rol):
    return next((x["emparejado_por"] for x in r["conversion"]["emparejamiento"] or [] if x["rol"] == rol), None)


# ---------------------------------------------------------------------------- las dos líneas base (pasan hoy)
def base_p01():
    mira("MDM_T02 en la gramática", "MDM_T02" in EH.GRAMATICAS, True)
    mira("contrato del punto mdm (acuse)", huella(PE.contrato(PE.PUNTOS["mdm"])), ANTES["mdm"])


SUITES = (("prueba_conversion.py", "PRUEBAS CONVERSIÓN: TODO BIEN"), ("prueba_conversion_vxu.py", "PRUEBAS VXU: TODO BIEN"),
          (os.path.join("cv", "prueba_vc.py"), "PRUEBAS VC: TODO BIEN"))
PRIVADO = os.path.normpath(os.path.join(AQUI, "..", "privado"))
CARPETAS = ["cv/cv2/ev", "cv/cv3/ev-minimos", "cv/cv3/ev-minimos-main", "cv/cv1d", "cv/vc", "vx/vx2c", "vx/vxpre", "vx/vx3", "vx/rv",
            "ar", "ci", "ci2", "mant", "mdm/mdpre"]
CORRIDAS = ["mant", "ci", "ci2", "mdm/mdpre", "ar", "vx", "cv"]


def base_p25():
    """P-MD-25 a, b, c, d: lo de ADT, ORU y VXU no cambia."""
    import conversion as CV
    import conversion_vxu as CVX
    for s, fin in SUITES:                                                        # (a) sin editar
        r = subprocess.run([sys.executable, os.path.join(AQUI, s)], capture_output=True, text=True, cwd=AQUI)
        mira("(a) %s en verde" % s, (r.returncode, fin in r.stdout), (0, True))
    info = {k: v for k, v in CV.INFO.items() if k != "mdm"}                     # (d)
    puntos = {n: PE.contrato(p) for n, p in PE.PUNTOS.items() if n != "mdm_conv"}
    mira("(d) lo que exportan conversion y puntos_entrada", (huella(CV.C), huella(info), huella(CV.TIPOS_PROY), huella(CVX.TIPOS),
                                                             huella(puntos), huella(CV.MAPAS)),
         (ANTES["C"], ANTES["INFO"], ANTES["TIPOS_PROY"], ANTES["CVX.TIPOS"], ANTES["PUNTOS"], ANTES["MAPAS"]))
    base = os.path.join(PRIVADO, "mdm", "rejuicio", "linea_base.jsonl")
    if not os.path.exists(base):
        mira("(b, c) rejuicio: sin evidencias privadas (copia pública)", True, True)
        return
    rj = os.path.join(AQUI, "md", "rejuicio_md.py")
    r = subprocess.run([sys.executable, rj, "comparar", base] + [os.path.join(PRIVADO, c) for c in CARPETAS], capture_output=True, text=True)
    mira("(b) rejuicio sin diferencias, y el punto solo cambia en MDM", (r.returncode, bool(re.search(r"evidencias, 0 diferencias, 0 de la línea base", r.stdout)),
                                                                          bool(re.search(r"\(\d+ MDM, 0 no MDM\)", r.stdout))), (0, True, True))
    r = subprocess.run([sys.executable, rj, "control", base] + [os.path.join(PRIVADO, c) for c in CARPETAS[:1] + ["vx/vx2c"]],
                       capture_output=True, text=True)
    mira("(b) control: el rejuicio ve un defecto en ADT y en VXU", (r.returncode, bool(re.search(r"'adt_conv': \d+", r.stdout)),
                                                                    bool(re.search(r"'vxu_conv': \d+", r.stdout))), (0, True, True))
    inf = os.path.join(PRIVADO, "mdm", "rejuicio", "informes_base.json")
    r = subprocess.run([sys.executable, rj, "informes_comparar", inf] + [os.path.join(PRIVADO, c) for c in CORRIDAS], capture_output=True, text=True)
    mira("(c) INFORME y juicio de cada corrida, iguales", (r.returncode, bool(re.search(r"corridas, 0 con el INFORME", r.stdout))), (0, True))


# ---------------------------------------------------------------------------- P-MD-1..27
def p01():
    m = MR.mensajes(msg())[0]
    mira("estructura del PE", PE.estructura_de(m, PE.PUNTOS["mdm_conv"]), "MDM_T02")
    r = juzga()
    mira("nominal", (cat(r), cuentan(r)), (("correcto", None), []))
    rc = r["conversion"]["recuentos"]
    mira("recuentos", {k: rc.get(k) for k in ("Patient", "Encounter", "DocumentReference", "ServiceRequest", "txa", "obx", "grupos_orden")},
         {"Patient": 1, "Encounter": 1, "DocumentReference": 1, "ServiceRequest": 1, "txa": 1, "obx": 1, "grupos_orden": 1})
    mira("emparejamiento", [emp(r, x) for x in ("Patient#1", "Encounter#1", "DocumentReference#1", "ServiceRequest#1")],
         ["unico", "unico", "master", "identifier"])
    r = juzga(b=con_doc(docStatus="entered-in-error"))
    mira("control docStatus", (cat(r), cuentan(r)), (("fallo_silencioso", "convertido"), [("fidelidad", "valor_distinto", "TXA-17")]))


def p02():
    for c17, ds in (("LA", "final"), ("AU", "final"), ("AU", "preliminary"), ("PA", "preliminary"), ("IN", "preliminary"),
                    ("IP", "preliminary"), ("DI", "preliminary"), ("DO", "preliminary")):
        r = juzga(msg(txa={17: c17}), con_doc(docStatus=ds))
        mira("%s -> %s" % (c17, ds), (sh(r), "convencion" in notas_de(r, "TXA-17")), ([], True))
    mira("control PA -> final", sh(juzga(msg(txa={17: "PA"}), con_doc(docStatus="final"))), [("valor_distinto", "TXA-17")])
    mira("control DI -> entered-in-error", sh(juzga(msg(txa={17: "DI"}), con_doc(docStatus="entered-in-error"))), [("valor_distinto", "TXA-17")])
    mira("control docStatus ausente", sh(juzga(b=con_doc(docStatus=None))), [("dato_perdido", "TXA-17")])
    r = juzga(msg(txa={17: None}))                                   # MD3-r1 (H10): OBX-11 F y docStatus final
    mira("sin TXA-17, docStatus = el ConceptMap de OBX-11 (H10): nota", (sh(r), "convencion" in notas_de(r, "TXA-17")), ([], True))
    r = juzga(msg(txa={17: None}, ordenes=[orden(obr={25: "P"})]), con_doc(docStatus="preliminary"))
    mira("sin TXA-17, docStatus = el ConceptMap de OBR-25 (H10): nota", (sh(r), "convencion" in notas_de(r, "TXA-17")), ([], True))
    mira("control sin TXA-17 y docStatus sin origen", sh(juzga(msg(txa={17: None}), con_doc(docStatus="preliminary"))),
         [("dato_inventado", "TXA-17")])
    mira("el literal AU (Q-MD-D-4: cuenta como fhir_invalido)", sh(juzga(b=con_doc(docStatus="AU"))), [("fhir_invalido", "TXA-17")])
    r = juzga_alt("Q-MD-D-4", b=con_doc(docStatus="AU"))
    mira("el literal AU con la alternativa (sin penalizar)", (sh(r), "literal_de_la_guia" in notas(r)), ([], True))
    mira("control XX: fhir_invalido y valor_distinto en TXA-17", sh(juzga(b=con_doc(docStatus="XX"))), [("fhir_invalido+valor_distinto", "TXA-17")])


def _ext(c, url=ALT, forma="cc"):
    v = {"cc": {"valueCodeableConcept": {"coding": [{"system": V2 % "0273", "code": c}]}}, "coding": {"valueCoding": {"code": c}},
         "code": {"valueCode": c}}[forma]
    return {"extension": [dict({"url": url}, **v)]}


def p03():
    mira("TXA-19 vacío -> current", sh(juzga(msg(txa={19: None}))), [])
    mira("AV -> current", sh(juzga()), [])
    for url in (ALT, ALT.replace("http:", "https:")):
        mira("CA con extensión %s y entered-in-error" % url[:5], sh(juzga(msg(txa={19: "CA"}), con_doc(status="entered-in-error", _status=_ext("CA", url)))), [])
    mira("CA con entered-in-error sin extensión", sh(juzga(msg(txa={19: "CA"}), con_doc(status="entered-in-error"))), [])
    mira("OB con superseded", sh(juzga(msg(txa={19: "OB"}), con_doc(status="superseded"))), [])
    for forma in ("cc", "coding", "code"):
        mira("UN con extensión (%s)" % forma, sh(juzga(msg(txa={19: "UN"}), con_doc(_status=_ext("UN", forma=forma)))), [])
    mira("control AV con superseded", sh(juzga(b=con_doc(status="superseded"))), [("valor_distinto", "TXA-19")])
    r = juzga(msg(txa={19: "CA"}), con_doc(status="current"))
    mira("control CA con current sin extensión (Q-MD-D-9): una sola cuenta (H20)", sh(r), [("valor_distinto", "TXA-19")])
    mira("control CA con current sin extensión, alternativa", sh(juzga_alt("Q-MD-D-9", msg(txa={19: "CA"}), con_doc(status="current"))),
         [("dato_perdido", "TXA-19")])
    mira("control CA con current y extensión (Q-MD-D-9)", sh(juzga(msg(txa={19: "CA"}), con_doc(status="current", _status=_ext("CA")))),
         [("valor_distinto", "TXA-19")])
    mira("CA con current y extensión, alternativa", sh(juzga_alt("Q-MD-D-9", msg(txa={19: "CA"}), con_doc(status="current", _status=_ext("CA")))), [])
    mira("control UN sin extensión", sh(juzga(msg(txa={19: "UN"}))), [("dato_perdido", "TXA-19")])
    mira("control UN con la extensión en el recurso (L-MD-11: solo status.extension)",
         sh(juzga(msg(txa={19: "UN"}), con_doc(extension=_ext("UN")["extension"]))), [("dato_perdido", "TXA-19")])
    mira("control status active", sh(juzga(b=con_doc(status="active"))), [("fhir_invalido", "TXA-19")])
    mira("control status ausente", sh(juzga(b=con_doc(status=None))), [("fhir_invalido", "TXA-19")])


def p04():
    mira("TXA-12 con system", sh(juzga(b=con_doc(masterIdentifier={"system": "urn:local:cssyn", "value": "DOC0001"}))), [])
    m = msg(txa={12: "DOC0036^CSSYN^1.2.840.113619.2.1^ISO"})
    mira("EI.3 en system", sh(juzga(m, con_doc(masterIdentifier={"system": "urn:oid:1.2.840.113619.2.1", "value": "DOC0036"}))), [])
    org = {"resourceType": "Organization", "id": "o1", "identifier": [{"value": "1.2.840.113619.2.1"}], "name": "CSSYN"}
    mira("EI.3 en assigner", sh(juzga(m, bundle(d=doc(masterIdentifier={"value": "DOC0036", "assigner": {"reference": "urn:uuid:o1"}}), extra=[org]))), [])
    m16 = msg(txa={16: "C:\\E\\docs\\E\\x.rtf"})
    mira("TXA-16 desescapado y entero", sh(juzga(m16, con_doc(identifier=[{"value": "C:\\docs\\x.rtf"}]))), [])
    mira("control masterIdentifier ausente", sh(juzga(b=con_doc(masterIdentifier=None))), [("dato_perdido", "TXA-12")])
    mira("control value con el namespace", sh(juzga(b=con_doc(masterIdentifier={"value": "DOC0001^CSSYN"}))), [("valor_distinto", "TXA-12")])
    mira("control EI.3 sin system ni assigner", sh(juzga(m, con_doc(masterIdentifier={"value": "DOC0036"}))), [("dato_perdido", "TXA-12")])
    mira("control TXA-16 truncado", sh(juzga(m16, con_doc(identifier=[{"value": "x.rtf"}]))), [("valor_distinto", "TXA-16")])
    mira("control TXA-16 sin desescapar", sh(juzga(m16, con_doc(identifier=[{"value": "C:\\E\\docs\\E\\x.rtf"}]))), [("valor_distinto", "TXA-16")])
    mira("control TXA-16 ausente", sh(juzga(b=con_doc(identifier=None))), [("dato_perdido", "TXA-16")])
    sin1 = msg(txa={12: "^SYSTEM^1.2.840.99^ISO"})                         # MD1-e: TXA-12 sin EI.1 (lfh-…L488, las dos salidas)
    mira("TXA-12 sin EI.1 y masterIdentifier solo con system (MD1-e)",
         sh(juzga(sin1, con_doc(masterIdentifier={"system": "urn:local:system"}))), [])
    mira("TXA-12 sin EI.1 y sin masterIdentifier (MD1-e)", sh(juzga(sin1, con_doc(masterIdentifier=None))), [])
    mira("control TXA-12 sin EI.1 y masterIdentifier.value (MD1-e)", sh(juzga(sin1, con_doc(masterIdentifier={"value": "1.2.840.99"}))),
         [("dato_inventado", "TXA-12")])
    r = juzga(b=con_doc(identifier=[{"value": "/docs/2023/alta0001.txt"}, {"system": "urn:id:propio", "value": "X-99"}]))
    mira("control identifier propio: nota", (sh(r), "extra" in notas(r)), ([], True))


def p05():
    mira("TXA-2 con system", sh(juzga(b=con_doc(type={"coding": [{"system": V2 % "0270", "code": "DS", "display": "Discharge summary"}]}))), [])
    mira("TXA-2 local", sh(juzga(msg(txa={2: "ZX"}), con_doc(type={"coding": [{"code": "ZX"}]}))), [])
    mira("TXA-3 TEXT con text/plain", sh(juzga(b=con_doc(content=[adj(tipo="text/plain")]))), [])
    mira("control type solo text", sh(juzga(b=con_doc(type={"text": "Discharge summary"}))), [("dato_perdido", "TXA-2")])
    mira("control coding LOINC sin DS", sh(juzga(b=con_doc(type={"coding": [{"system": "http://loinc.org", "code": "18842-5"}]}))),
         [("valor_distinto", "TXA-2")])
    mira("control type sin TXA-2", sh(juzga(msg(txa={2: None}))), [("dato_inventado", "TXA-2")])
    mira("control TXA-3 sin ningún contentType", sh(juzga(b=con_doc(content=[adj(tipo=None)]))), [("dato_perdido", "OBX-2"), ("dato_perdido", "TXA-3")])
    mira("TXA-3 y un attachment sin data ni url: R-MD-14 no cuenta (H13)",
         sh(juzga(b=con_doc(content=[{"attachment": {"creation": "2023-01-09T10:15:00+01:00"}}]))), [("dato_perdido", "OBX-5")])


def p06():
    for c in ("V", "R", "U"):
        mira("TXA-18 %s" % c, sh(juzga(msg(txa={18: c}), con_doc(securityLabel=[{"coding": [{"system": V2 % "0272", "code": c}]}]))), [])
    mira("v3-Confidentiality", sh(juzga(b=con_doc(securityLabel=[{"coding": [{"system": V3_CONF, "code": "R"}]}]))), [])
    mira("control R con TXA-18 V", sh(juzga(msg(txa={18: "V"}))), [("codigo_mal_mapeado", "TXA-18")])
    mira("control ausente", sh(juzga(b=con_doc(securityLabel=None))), [("dato_perdido", "TXA-18")])
    r = juzga(msg(txa={18: None}))
    mira("control label sin TXA-18: nota", (sh(r), "extra" in notas(r)), ([], True))


def p07():
    mira("instante en Z", sh(juzga(b=con_doc(date="2023-01-09T09:15:00Z"))), [])
    m = msg(txa={6: "20230109"})
    mira("solo fecha sin date", sh(juzga(m, con_doc(date=None))), [])
    r = juzga(m, con_doc(date="2023-01-09T00:00:00+01:00"))
    mira("solo fecha completada (AMB-CV-9)", (sh(r), "convencion" in notas_de(r, "TXA-6")), ([], True))
    r = juzga(msg(txa={6: None}), con_doc(date="2023-01-09T10:15:00+01:00"))
    mira("sin TXA-6 y date = MSH-7: nota", (sh(r), "convencion" in notas_de(r, "TXA-6")), ([], True))
    mira("control solo fecha, otro día", sh(juzga(m, con_doc(date="2023-01-10T00:00:00+01:00"))), [("valor_distinto", "TXA-6")])
    mira("control hora sin zona", sh(juzga(b=con_doc(date="2023-01-09T10:15:00"))), [("fhir_invalido", "TXA-6")])
    mira("control hora cambiada", sh(juzga(b=con_doc(date="2023-01-09T11:15:00+01:00"))), [("valor_distinto", "TXA-6")])
    mira("control hora perdida", sh(juzga(b=con_doc(date="2023-01-09"))), [("dato_perdido", "TXA-6")])
    mira("control sin TXA-6 y date ajeno", sh(juzga(msg(txa={6: None}), con_doc(date="2020-05-05T10:00:00+01:00"))), [("dato_inventado", "TXA-6")])
    mira("control date sin TXA-6 ni nada", sh(juzga(msg(txa={6: None}), con_doc(date=None))), [])


def p08():
    gold = prac("pr9", "1234", "Goldstein", "Harold")
    m = msg(txa={9: "1234^Goldstein^Harold^A^^DR"})
    mira("author Practitioner", sh(juzga(m, bundle(d=doc(author=[{"reference": "urn:uuid:pr9"}]), extra=[gold]))), [])
    rol = {"resourceType": "PractitionerRole", "id": "rl9", "practitioner": {"reference": "urn:uuid:pr9"}}
    mira("author vía PractitionerRole", sh(juzga(m, bundle(d=doc(author=[{"reference": "urn:uuid:rl9"}]), extra=[gold, rol]))), [])
    m2 = msg(txa={10: "PR02^Muestra^Jorge~PR03^Patron^Irene"})
    b3 = bundle(d=doc(authenticator={"reference": "urn:uuid:pr3"}), extra=[PR3])
    mira("authenticator con la segunda repetición (Q-MD-D-11)", sh(juzga(m2, b3)), [])
    mira("control authenticator con la segunda, alternativa (la primera)", sh(juzga_alt("Q-MD-D-11", m2, b3)), [("valor_distinto", "TXA-10")])
    mira("control author solo display", sh(juzga(b=con_doc(author=[{"display": "Ana Ensayo"}]))), [("dato_perdido", "TXA-9")])
    mira("control authenticator con la persona de TXA-9", sh(juzga(b=con_doc(authenticator={"reference": "urn:uuid:pr1"}))),
         [("valor_distinto", "TXA-10")])
    org = {"resourceType": "Organization", "id": "o9", "identifier": [{"value": "PR01"}], "name": "Ensayo"}
    mira("control actor Organization", sh(juzga(b=bundle(d=doc(author=[{"reference": "urn:uuid:o9"}]), extra=[org]))), [("dato_perdido", "TXA-9")])
    mira("control author a un id inexistente", sh(juzga(b=con_doc(author=[{"reference": "urn:uuid:nadie"}]))), [("referencia_rota", "TXA-9")])
    mira("control authenticator sin TXA-10", sh(juzga(msg(txa={10: None}))), [("dato_inventado", "TXA-10")])
    mira("control family distinta", sh(juzga(msg(txa={9: "PR01^Otra^Ana"}))), [("valor_distinto", "TXA-9")])
    ppn = lambda xcn: "^".join(xcn.split("^") + [""] * (14 - len(xcn.split("^"))) + ["20230109110000+0100"])  # noqa: E731
    m22 = msg(txa={10: None, 22: ppn("PR02^Muestra^Jorge")})          # MD3-r1 (H8): TXA-10 vacío, TXA-22 valorado
    r = juzga(m22)
    mira("TXA-10 vacío y authenticator = TXA-22 (H8): nota", (sh(r), "convencion" in notas_de(r, "TXA-10")), ([], True))
    r = juzga(m22, con_doc(authenticator={"display": "Jorge Muestra"}))
    mira("TXA-10 vacío y authenticator solo display de TXA-22 (H8): nota", (sh(r), "convencion" in notas_de(r, "TXA-10")), ([], True))
    mira("control TXA-10 vacío y authenticator distinto de TXA-22", sh(juzga(m22, con_doc(authenticator={"reference": "urn:uuid:pr1"}))),
         [("dato_inventado", "TXA-10")])
    b37 = bundle(d=doc(authenticator={"reference": "urn:uuid:pr3"}), extra=[PR3])
    mira("control con TXA-10, el authenticator de TXA-22 sigue contando (H5)", sh(juzga(msg(txa={22: ppn("PR03^Patron^Irene")}), b37)),
         [("valor_distinto", "TXA-10")])


LINEAS = ["Primera linea Zeta020101", "Segunda linea Zeta020102", "Tercera linea Zeta020103", "Cuarta linea Zeta020104"]


def p09():
    m = msg(obxs=[obx(valor="~".join(LINEAS))])
    mira("cuatro repeticiones con LF", sh(juzga(m, con_doc(content=[adj("\n".join(LINEAS))]))), [])
    mira("cuatro repeticiones con CR LF", sh(juzga(m, con_doc(content=[adj("\r\n".join(LINEAS))]))), [])
    m2 = msg(obxs=[obx(1, valor=LINEAS[0]), obx(2, valor=LINEAS[1])])
    mira("dos OBX en dos content", sh(juzga(m2, con_doc(content=[adj(LINEAS[0]), adj(LINEAS[1])]))), [])
    mira("dos OBX en uno", sh(juzga(m2, con_doc(content=[adj(LINEAS[0] + "\n" + LINEAS[1])]))), [])
    m3 = msg(obxs=[obx(valor="Sal \\T\\ pimienta Zeta020201")])
    mira("\\T\\ desescapado", sh(juzga(m3, con_doc(content=[adj("Sal & pimienta Zeta020201")]))), [])
    mira("control repeticiones sin salto", sh(juzga(m, con_doc(content=[adj(" ".join(LINEAS))]))), [("valor_distinto", "OBX-5")])
    mira("control sin la última línea", sh(juzga(m, con_doc(content=[adj("\n".join(LINEAS[:3]))]))), [("dato_perdido", "OBX-5")])
    mira("control otro orden", sh(juzga(m, con_doc(content=[adj("\n".join(LINEAS[::-1]))]))), [("valor_distinto", "OBX-5")])
    mira("control \\T\\ literal", sh(juzga(m3, con_doc(content=[adj("Sal \\T\\ pimienta Zeta020201")]))), [("valor_distinto", "OBX-5")])
    mira("control texto crudo (no Base64)", sh(juzga(b=con_doc(content=[{"attachment": {"contentType": "application/text", "data": TEXTO}}]))),
         [("fhir_invalido", "OBX-5")])


def p10():
    mira("TX application/text", sh(juzga()), [])
    mira("TX text/plain (Q-MD-D-3)", sh(juzga(b=con_doc(content=[adj(tipo="text/plain")]))), [])
    mira("TX text/plain con charset", sh(juzga(b=con_doc(content=[adj(tipo="text/plain; charset=UTF-8")]))), [])
    m = msg(obxs=[obx(tipo="FT", valor="Texto formateado Zeta030101")])
    mira("FT text/hl7v2", sh(juzga(m, con_doc(content=[adj("Texto formateado Zeta030101", "text/hl7v2")]))), [])
    mira("FT text/plain (Q-MD-D-3)", sh(juzga(m, con_doc(content=[adj("Texto formateado Zeta030101", "text/plain")]))), [])
    mira("control TX application/pdf", sh(juzga(b=con_doc(content=[adj(tipo="application/pdf")]))), [("valor_distinto", "OBX-2")])
    mira("control TX sin contentType", sh(juzga(msg(txa={3: None}), con_doc(content=[adj(tipo=None)]))), [("dato_perdido", "OBX-2")])
    mira("control TX text/plain con la alternativa (literales)", sh(juzga_alt("Q-MD-D-3", b=con_doc(content=[adj(tipo="text/plain")]))),
         [("valor_distinto", "OBX-2")])
    mira("control FT application/text", sh(juzga(m, con_doc(content=[adj("Texto formateado Zeta030101", "application/text")]))),
         [("valor_distinto", "OBX-2")])


FT = "Primera Zeta040101\\.br\\Segunda \\H\\importante\\N\\ final Zeta040102"


def p11():
    m = msg(obxs=[obx(tipo="FT", valor=FT)])
    mira("FT con las órdenes crudas y text/hl7v2", sh(juzga(m, con_doc(content=[adj(FT, "text/hl7v2")]))), [])
    limpio = "Primera Zeta040101\nSegunda importante final Zeta040102"
    mira("FT sin órdenes y text/plain", sh(juzga(m, con_doc(content=[adj(limpio, "text/plain")]))), [])
    mn = msg(obxs=[obx(), nte(1, "Comentario del informe Zeta040201")])
    mira("NTE en su content", sh(juzga(mn, con_doc(content=[adj(), adj("Comentario del informe Zeta040201", "text/hl7v2")]))), [])
    mira("NTE con el texto, text/plain", sh(juzga(mn, con_doc(content=[adj(TEXTO + "\nComentario del informe Zeta040201", "text/plain")]))), [])
    mira("control \\.br\\ crudo con text/plain", sh(juzga(m, con_doc(content=[adj(FT, "text/plain")]))), [("valor_distinto", "OBX-5")])
    mira("control NTE perdido", sh(juzga(mn)), [("dato_perdido", "NTE-3")])
    mira("control FT sin el último párrafo", sh(juzga(m, con_doc(content=[adj("Primera Zeta040101", "text/plain")]))), [("dato_perdido", "OBX-5")])


CARGA = b"SINTETICO-12-AP\x00\x01\x02 binario"
HEX = "53494E544554494330"                                                 # 9 octetos: 18 dígitos (no múltiplo de 4)
HEX4 = "53494E5445544943"                                                   # 8 octetos: 16 dígitos


def ed(k, ed2, ed3, ed4, ed5, reps=None):
    v = "~".join("^%s^%s^%s^%s" % r for r in (reps or [(ed2, ed3, ed4, ed5)]))
    return obx(k, "ED", v, cod="PDF^Documento^L")


def p12():
    bb = b64(CARGA)
    m = msg(txa={3: "AP"}, obxs=[ed(1, "AP", "RTF", "Base64", bb)])
    nominal_ed = lambda data, tipo="application/rtf": con_doc(content=[{"attachment": {"contentType": tipo, "data": data}}])  # noqa: E731
    mira("Base64", sh(juzga(m, nominal_ed(bb))), [])
    ma = msg(txa={3: "TEXT"}, obxs=[ed(1, "TEXT", "XML", "A", "<a>1 \\T\\ 2 \\S\\ 3</a>")])
    for tipo in ("text/xml", "application/xml"):
        mira("A con escapes, %s" % tipo, sh(juzga(ma, nominal_ed(b64("<a>1 & 2 ^ 3</a>"), tipo))), [])
    mh = msg(txa={3: "AP"}, obxs=[ed(1, "AP", "PostScript", "Hex", HEX)])
    mira("Hex", sh(juzga(mh, nominal_ed(b64(bytes.fromhex(HEX)), "application/postscript"))), [])
    mj = msg(txa={3: "IM"}, obxs=[ed(1, "IM", "JPEG", "Base64", bb)])
    mira("image/jpeg", sh(juzga(mj, nominal_ed(bb, "image/jpeg"))), [])
    mc = msg(txa={3: "multipart"}, obxs=[ed(1, "multipart", "x-hl7-cda-level-one", "Base64", bb)])
    mira("CDA", sh(juzga(mc, nominal_ed(bb, "application/x-hl7-cda-level-one+xml"))), [])
    m0 = msg(txa={3: "IM"}, obxs=[ed(1, "IM", "", "Base64", bb)])
    mira("sin ED.3", sh(juzga(m0, nominal_ed(bb, "image/gif"))), [])
    bb2 = b64(b"SINTETICO-18-GIF")
    m2 = msg(txa={3: "IM"}, obxs=[ed(1, None, None, None, None, reps=[("IM", "JPEG", "Base64", bb), ("IM", "GIF", "Base64", bb2)])])
    dos = con_doc(content=[{"attachment": {"contentType": "image/jpeg", "data": bb}}, {"attachment": {"contentType": "image/gif", "data": bb2}}])
    mira("dos repeticiones, dos attachments", sh(juzga(m2, dos)), [])
    binario = {"resourceType": "Binary", "id": "bin1", "contentType": "application/rtf", "data": bb}
    r = juzga(m, bundle(d=doc(content=[{"attachment": {"contentType": "application/rtf", "url": "urn:uuid:bin1"}}]), extra=[binario]))
    mira("Binary referenciado", (sh(r), "convencion" in notas(r), r["conversion"]["otros_tipos"].get("Binary")), ([], True, None))
    r = juzga(m, nominal_ed(b64(bb)))
    mira("control codificado dos veces", (sh(r), any("doble" in q for h in r["hallazgos"] if h["cuenta"] for q in h["que"])),
         ([("valor_distinto", "OBX-5")], True))
    mh4 = msg(txa={3: "AP"}, obxs=[ed(1, "AP", "PostScript", "Hex", HEX4)])
    mira("control Hex sin convertir", sh(juzga(mh4, nominal_ed(HEX4, "application/postscript"))), [("valor_distinto", "OBX-5")])
    mira("control image/png con JPEG", sh(juzga(mj, nominal_ed(bb, "image/png"))), [("valor_distinto", "OBX-2")])
    mira("control sin su attachment", sh(juzga(m, con_doc(content=[adj("otra cosa", "text/plain")]))), [("dato_perdido", "OBX-5")])
    mira("control solo una de dos", sh(juzga(m2, con_doc(content=dos["entry"][2]["resource"]["content"][:1]))), [("dato_perdido", "OBX-5")])
    mi = msg(txa={3: "AP"}, obxs=[ed(1, "AP", "RTF", "Base64", "***")])
    r = juzga(mi, nominal_ed("***"))
    mira("control ED.5 imposible escrito", ("valor_imposible_convertido" in subs(r, "OBX-5"), r["veredicto"]["subtipo"] is not None
                                            and "aceptado_imposible" in r["veredicto"]["subtipo"]), (True, True))


def p13():
    rp = lambda k, *reps: obx(k, "RP", "~".join("%s^^%s^%s" % r for r in reps), cod="IMG^Imagen^L")  # noqa: E731
    m = msg(txa={3: "IM"}, obxs=[rp(1, ("ptr-0006", "IM", "JPEG"))])
    u = lambda url, tipo="image/jpeg": {"attachment": {"contentType": tipo, "url": url}}  # noqa: E731
    mira("url y image/jpeg", sh(juzga(m, con_doc(content=[u("ptr-0006")]))), [])
    mira("url e IM/JPEG", sh(juzga(m, con_doc(content=[u("ptr-0006", "IM/JPEG")]))), [])
    m2 = msg(txa={3: "IM"}, obxs=[rp(1, ("ptr-0006", "IM", "JPEG"), ("ptr-0007", "IM", "GIF"))])
    mira("dos repeticiones", sh(juzga(m2, con_doc(content=[u("ptr-0006"), u("ptr-0007", "image/gif")]))), [])
    r = juzga(m, con_doc(content=[u("https://repo.ejemplo/ptr-0006")]))
    mira("url con prefijo: nota", (sh(r), "convencion" in notas(r)), ([], True))
    mira("control url ausente", sh(juzga(m, con_doc(content=[{"attachment": {"contentType": "image/jpeg"}}]))), [("dato_perdido", "OBX-5")])
    mira("control url distinta", sh(juzga(m, con_doc(content=[u("ptr-9999")]))), [("valor_distinto", "OBX-5")])
    mira("control application/pdf", sh(juzga(m, con_doc(content=[u("ptr-0006", "application/pdf")]))), [("valor_distinto", "OBX-2")])
    mira("control solo una de dos", sh(juzga(m2, con_doc(content=[u("ptr-0006")]))), [("dato_perdido", "OBX-5")])


def p14():
    r = juzga(b=con_doc(content=None))
    mira("sin content con OBX TX: un solo hallazgo", sh(r), [("fhir_invalido", "OBX-5")])
    mira("content sin attachment", sh(juzga(b=con_doc(content=[adj(), {"format": {"code": "x"}}]))), [("fhir_invalido", "OBX-5")])
    mira("data con caracteres no Base64", sh(juzga(b=con_doc(content=[adj(), {"attachment": {"contentType": "text/plain", "data": "@@@"}}]))),
         [("fhir_invalido", "OBX-5")])
    mira("control content completo", sh(juzga()), [])
    m = msg(txa={3: None}, obxs=[obx(1, "CE", "C001^Codigo^L"), obx(2, "ST", "Valor")])
    r = juzga(m, con_doc(content=None))
    mira("control solo OBX sin destino y sin content", (sh(r), "sin_content_posible" in notas(r)), ([], True))


def p15():
    r = juzga()
    mira("uno y uno: master", emp(r, "DocumentReference#1"), "master")
    m = msg(obxs=[obx(1, valor=LINEAS[0]), obx(2, valor=LINEAS[1])])
    d1, d2 = doc("d1", content=[adj(LINEAS[0])]), doc("d2", content=[adj(LINEAS[1])])
    r = juzga(m, bundle(docs=[d1, d2]))
    mira("dos DocumentReference con el mismo masterIdentifier", (sh(r), "varias_candidatas" in notas(r)), ([("recurso_duplicado", "TXA-12")], True))
    mira("ninguna", sh(juzga(b=bundle(docs=[]))), [("recurso_ausente", "TXA-12")])
    d3 = doc("d3", masterIdentifier=None, identifier=None, type=None)
    mira("control una sin claves comunes con un TXA", sh(juzga(b=bundle(docs=[doc(), d3]))), [("recurso_duplicado", "TXA-12")])
    m2 = msg(segundo_txa=[seg("TXA", junta(TXA, {12: "DOC0002^CSSYN", 16: None})), obx(2, valor=LINEAS[1])])
    r = juzga(m2)
    mira("control dos TXA y una sola", ("recurso_ausente", "TXA(2)-12") in sh(r), True)


def p16():
    r = juzga(b=con_doc(subject=None))
    mira("subject ausente: nota (Q-MD-D-6)", (sh(r), "sin_subject" in notas(r)), ([], True))
    mo = msg(ordenes=[orden(), orden({2: "PL0002^CSSYN", 3: "FL0002^CSSYN"}, {2: "PL0002^CSSYN", 3: "FL0002^CSSYN"})])
    rel = {"encounter": [{"reference": "urn:uuid:e1"}], "related": [{"reference": "urn:uuid:s1"}, {"reference": "urn:uuid:s2"}]}
    mira("related a los dos (Q-MD-D-7)", sh(juzga(mo, bundle(d=doc(context=rel), srs=[sr(), sr("s2", "PL0002", "FL0002")]))), [])
    mira("control solo al primero (Q-MD-D-7: uno por orden)",
         sh(juzga(mo, bundle(srs=[sr(), sr("s2", "PL0002", "FL0002")]))), [("dato_perdido", "ORC(2)-1")])
    r = juzga(b=bundle(d=doc(subject={"reference": "urn:uuid:p2"}), extra=[pac("p2", "OTRO1")]))
    mira("control subject a otro Patient", ("referencia_rota", "PID-3") in sh(r), True)
    mira("control subject a un id inexistente", sh(juzga(b=con_doc(subject={"reference": "urn:uuid:nadie"}))), [("referencia_rota", "PID-3")])
    mira("control related ausente", sh(juzga(b=con_doc(context={"encounter": [{"reference": "urn:uuid:e1"}]}))), [("dato_perdido", "ORC-1")])
    r = juzga(b=con_doc(context={"encounter": [{"reference": "urn:uuid:e1"}], "related": [{"reference": "urn:uuid:nada"}]}))
    mira("control related a un id inexistente", "referencia_rota" in subs(r, "ORC-1"), True)
    mira("control encounter a un id inexistente", sh(juzga(b=con_doc(context={"encounter": [{"reference": "urn:uuid:nada"}],
                                                                                "related": [{"reference": "urn:uuid:s1"}]}))), [("referencia_rota", "PV1-19")])
    mira("control context.encounter sin PV1", ("dato_inventado", "PV1-19") in sh(juzga(msg(sin_pv1=True), bundle(sin=("Encounter",)))), True)
    mira("control subject ausente, alternativa (dato_perdido)", sh(juzga_alt("Q-MD-D-6", b=con_doc(subject=None))), [("dato_perdido", "PID-3")])


def p17():
    m = msg(ordenes=[orden({2: None, 3: None})])
    mira("ORC-2/3 vacíos: los números del OBR", sh(juzga(m)), [])
    mira("status e intent válidos cualesquiera", sh(juzga(b=bundle(srs=[sr(status="completed", intent="original-order")]))), [])
    mira("control PLAC y FILL intercambiados", sh(juzga(b=bundle(srs=[sr(plac="FL0001", fill="PL0001")]))),
         [("codigo_mal_mapeado", "ORC-2"), ("codigo_mal_mapeado", "ORC-3")])
    mira("control identifier ausente", sh(juzga(b=bundle(srs=[sr(identifier=None)]))), [("dato_perdido", "ORC-2"), ("dato_perdido", "ORC-3")])
    mira("control code ausente", sh(juzga(b=bundle(srs=[sr(code=None)]))), [("dato_perdido", "OBR-4")])
    mira("control status foo", sh(juzga(b=bundle(srs=[sr(status="foo")]))), [("fhir_invalido", "ORC-5")])
    mira("control intent ausente", sh(juzga(b=bundle(srs=[sr(intent=None)]))), [("fhir_invalido", "ORC-1")])
    mira("control subject ausente", sh(juzga(b=bundle(srs=[sr(subject=None)]))), [("dato_perdido", "PID-3")])
    mira("control uno de más", sh(juzga(b=bundle(srs=[sr(), sr("s9", "PL0009", "FL0009", "OTRO")]))), [("recurso_inventado", "ORC")])
    mira("control ausente", sh(juzga(b=bundle(d=doc(context={"encounter": [{"reference": "urn:uuid:e1"}]}), srs=[]))), [("recurso_ausente", "ORC-1")])
    tres = msg(ordenes=[orden({2: "PL000%d^CSSYN" % k, 3: "FL000%d^CSSYN" % k}, {2: "PL000%d^CSSYN" % k, 3: "FL000%d^CSSYN" % k}) for k in (1, 2, 3)])
    iguales = [sr("s1", identifier=None), sr("s2", identifier=None)]
    r = juzga(tres, bundle(d=doc(context={"encounter": [{"reference": "urn:uuid:e1"}]}), srs=iguales))
    mira("control tres grupos con el mismo OBR-4 y dos iguales", cat(r), ("indeterminado", "emparejamiento"))
    iguales3 = msg(ordenes=[orden(), orden(), orden()])                # MD3-r1 (H22): el mismo número de orden, una sola orden
    r = juzga(iguales3)
    mira("tres grupos idénticos y un ServiceRequest (H22)", (cat(r), sh(r), "orden_repetida" in notas(r)), (("correcto", None), [], True))
    r = juzga(iguales3, bundle(srs=[sr("s1"), sr("s2"), sr("s3")]))
    mira("tres grupos idénticos y tres ServiceRequest iguales (H22)", (cat(r), sh(r)), (("correcto", None), []))
    mira("control: cuatro ServiceRequest para tres grupos idénticos", sh(juzga(iguales3, bundle(srs=[sr("s%d" % k) for k in range(1, 5)]))),
         [("recurso_duplicado", "ORC-1")])
    m29 = msg(ordenes=[orden(obr={29: "PAI-29"})])                    # MD3-r1 (H21): el pedido padre de OBR-29
    padre = sr("s9", cod="OTRO", identifier=[{"value": "PAI-29", "type": cc("0203", "PLAC")}])
    hijo = sr(basedOn=[{"reference": "urn:uuid:s9"}])
    r = juzga(m29, bundle(srs=[hijo, padre]))
    mira("ServiceRequest padre de OBR-29 por basedOn (H21): nota", (sh(r), "pedido_padre" in notas(r), r["conversion"]["otros_tipos"].get("ServiceRequest")),
         ([], True, None))
    mira("control: el padre sin basedOn", sh(juzga(m29, bundle(srs=[sr(), padre]))), [("recurso_inventado", "ORC")])
    mira("control: basedOn a uno que no es OBR-29", sh(juzga(msg(), bundle(srs=[hijo, padre]))), [("recurso_inventado", "ORC")])
    cod9 = "DOC-DS^Informe de alta^L^^^^^^Texto original"            # MD3-r1 (H7): OBR-4 es CE hasta 2.5
    for ver in ("2.3", "2.5"):
        mira("OBR-4 CE en %s: el componente 9 no se espera (H7)" % ver, subs(juzga(msg(msh={12: ver}, ordenes=[orden(obr={4: cod9})])), "OBR-4"), [])
    mira("control: en 2.6, OBR-4 es CWE y CWE.9 va a text", sh(juzga(msg(msh={12: "2.6"}, ordenes=[orden(obr={4: cod9})]))),
         [("dato_perdido", "OBR-4")])


def p18():
    m = msg(obxs=[obx(1, "CE", "C001^Codigo^L", cod="2000.10^CODIGO^L"), obx(2, "ST", "Valor libre", cod="2000.20^TEXTO^L"), obx(3)])
    obs = [{"resourceType": "Observation", "id": "ob%d" % k, "status": "final", "code": {"text": "x"}} for k in (1, 2)]
    r = juzga(m, bundle(extra=obs))
    mira("OBX CE y ST sin rastro y un Observation por OBX", (sh(r), r["conversion"]["recuentos"].get("obx_sin_destino"),
                                                              r["conversion"]["otros_tipos"]), ([], 2, {"Observation": 2}))
    mira("control CE y ST sin rastro, alternativa de Q-MD-D-12", sh(juzga_alt("Q-MD-D-12", m, bundle())),
         [("dato_perdido", "OBX(2)-5"), ("dato_perdido", "OBX-5")])
    mira("control Observation, alternativa de Q-MD-D-8", sh(juzga_alt("Q-MD-D-8", m, bundle(extra=obs[:1]))), [("recurso_inventado", "OBX")])


def p19():
    mira("Patient y Encounter nominales", sh(juzga()), [])
    m = msg(pv1={2: "I"})
    mira("control PV1-2 I con {v2-0004, I}", sh(juzga(m, bundle(e=con(enc, **{"class": {"system": V2 % "0004", "code": "I"}})))),
         [("codigo_mal_mapeado", "PV1-2")])
    r = juzga(b=bundle(d=doc(context={"related": [{"reference": "urn:uuid:s1"}]}), sin=("Encounter",)))
    mira("control sin Encounter", (sh(r), any("MSG_MDM_T02" in c for h in r["hallazgos"] if h["hecho"] == "PV1" for c in h["citas"])),
         ([("recurso_ausente", "PV1")], True))
    mira("control PV1-2 N sin Encounter (Q-CV-D-6)", sh(juzga(msg(pv1={2: "N"}), bundle(d=doc(context={"related": [{"reference": "urn:uuid:s1"}]}),
                                                                                     sin=("Encounter",)))), [("recurso_ausente", "PV1")])
    mira("control dos Patient", ("recurso_duplicado", "PID") in sh(juzga(b=bundle(extra=[pac("p2", "OTRO1")]))), True)
    mira("control PID-8 distinto", sh(juzga(b=bundle(p=con(pac, gender="female")))), [("valor_distinto", "PID-8")])


def p20():
    for ev_, est in (("T01", "MDM_T01"), ("T03", "MDM_T01"), ("T05", "MDM_T01"), ("T07", "MDM_T01"), ("T09", "MDM_T01"), ("T11", "MDM_T01"),
                     ("T04", "MDM_T02"), ("T06", "MDM_T02"), ("T08", "MDM_T02"), ("T10", "MDM_T02")):
        mira("MDM^%s fuera de alcance (Q-MD-D-1: solo T02)" % ev_, cat(juzga(msg(msh={9: "MDM^%s^%s" % (ev_, est)}, evn={1: ev_}))),
             ("fuera_de_alcance", None))
    for t in ("QRY^T12^QRY_T12", "ACK^T02^ACK"):
        mira("%s fuera de alcance" % t, cat(juzga(msg(msh={9: t}))), ("fuera_de_alcance", None))
    import conversion as CV
    import conversion_mdm as CVM
    r = CV.verificar(ev_mdm(msg(msh={9: "MDM^T06^MDM_T02"}, evn={1: "T06"}), bundle()), CVM.PE_ALTERNATIVA_EVENTOS, CVM.con_alternativas_md("Q-MD-D-1"))
    mira("T06 con la alternativa de Q-MD-D-1: se juzga, nota evento", (cat(r), "evento" in notas(r)), (("correcto", None), True))
    r = juzga(msg(msh={9: "MDM^T02^MDM_T01"}))
    mira("control MSH-9.3 MDM_T01", (cat(r), "estructura_declarada" in notas(r)), (("correcto", None), True))


def p21():
    r = juzga(msg(msh={9: "MDM^T02"}))
    mira("MSH-9.3 vacío: nota", (sh(r), "estructura_declarada" in notas(r)), ([], True))
    r = juzga(msg(msh={12: "2.5.1"}, txa={17: "XX"}), con_doc(docStatus="preliminary"))
    mira("2.5.1 con TXA-17 XX: L18", (sh(r), "version" in notas(r)), ([], True))
    r = juzga(msg(antes_txa=[obx(9, valor="Suelto Zeta050101")]))
    mira("OBX antes del TXA", (sh(r), r["conversion"]["recuentos"].get("obx_fuera_txa")), ([], 1))
    m2 = msg(segundo_txa=[seg("TXA", junta(TXA, {12: "DOC0002^CSSYN", 16: None})), obx(2, valor=LINEAS[1])])
    d2 = doc("d2", masterIdentifier={"value": "DOC0002", "assigner": {"display": "CSSYN"}}, identifier=None, content=[adj(LINEAS[1])])
    r = juzga(m2, bundle(docs=[doc(), d2]))
    mira("segundo TXA: nota y su DocumentReference", (sh(r), "estructura" in notas(r), emp(r, "DocumentReference#2")), ([], True, "master"))
    r = juzga(msg(txa={3: None}, obxs=[]), con_doc(content=None))
    mira("TXA sin OBX: nota", (sh(r), "estructura" in notas(r)), ([], True))
    r = juzga(msg(txa={17: "XX"}), con_doc(docStatus="XX"))
    mira("control 2.5 con TXA-17 XX y docStatus XX", subs(r, "TXA-17"), ["fhir_invalido", "valor_imposible_convertido"])


def p22():
    err = lambda m, t="no se pudo convertir": j(ev_mdm(m, estado="error", error={"codigo": "1", "texto": t}))  # noqa: E731
    casos = {"TXA-6 imposible": msg(txa={6: "20261301"}), "TXA-17 XX": msg(txa={17: "XX"}), "TXA-19 ZZ": msg(txa={19: "ZZ"}),
             "ED.5 no Base64": msg(obxs=[ed(1, "AP", "RTF", "Base64", "***")]), "ED.5 Hex impar": msg(obxs=[ed(1, "AP", "RTF", "Hex", "ABC")]),
             "OBX-2 ZZ": msg(obxs=[obx(tipo="ZZ")]), "sin PV1": msg(sin_pv1=True), "TXA-12 vacío": msg(txa={12: None})}
    for n, m in casos.items():
        r = err(m)
        mira("error con %s: aceptable" % n, (cat(r), "aceptable" in notas(r)), (("correcto", None), True))
    mira("error con el nominal", cat(err(msg())), ("rechazo_incorrecto", "error"))
    m = msg(extra_cabecera=[seg("SFT", {1: "Proveedor", 2: "1.0", 3: "Prog", 4: "1"})], ordenes=[orden(tq1=True)])
    mira("control error con SFT y TQ1", cat(err(m)), ("rechazo_incorrecto", "error"))
    r = err(msg(sin_pid=True))
    mira("control error sin PID", (cat(r), "aceptable" in notas(r)), (("correcto", None), True))


def mutaciones_clase():
    """P-MD-23: una mutación por subtipo sobre el nominal -> (mensaje, Bundle, (subtipo, hecho))."""
    otra = copy.deepcopy(doc("d2"))
    return [(msg(), con_doc(docStatus="entered-in-error"), ("valor_distinto", "TXA-17")),
            (msg(), con_doc(masterIdentifier=None), ("dato_perdido", "TXA-12")),
            (msg(txa={10: None}), bundle(), ("dato_inventado", "TXA-10")),
            (msg(), con_doc(securityLabel=[{"coding": [{"system": V2 % "0272", "code": "V"}]}]), ("codigo_mal_mapeado", "TXA-18")),
            (msg(txa={17: "XX"}), con_doc(docStatus="preliminary"), ("valor_imposible_convertido", "TXA-17")),
            (msg(), bundle(d=doc(context={"encounter": [{"reference": "urn:uuid:e1"}]}), srs=[]), ("recurso_ausente", "ORC-1")),
            (msg(), bundle(docs=[doc(), otra]), ("recurso_duplicado", "TXA-12")),
            (msg(), bundle(srs=[sr(), sr("s9", "PL0009", "FL0009", "OTRO")]), ("recurso_inventado", "ORC")),
            (msg(), con_doc(author=[{"reference": "urn:uuid:nadie"}]), ("referencia_rota", "TXA-9")),
            (msg(), con_doc(status="active"), ("fhir_invalido", "TXA-19"))]


def p23():
    for m, b, esp in mutaciones_clase():
        mira("mutación %s" % esp[0], sh(juzga(m, b)), [esp])
    b = bundle()
    formas = []
    x = copy.deepcopy(b)
    x["entry"].reverse()
    formas.append(("orden de entries", x))
    d = doc(content=[adj(), {"attachment": {"title": "copia"}}])
    formas.append(("orden de content", con_doc(content=d["content"][::-1])))
    formas.append(("orden de author", bundle(d=doc(author=[{"reference": "urn:uuid:pr3"}, {"reference": "urn:uuid:pr1"}]), extra=[PR3])))
    x = copy.deepcopy(b)
    for e in x["entry"]:
        e["resource"]["id"] = e["resource"]["id"] + "x"
    formas.append(("id", x))
    formas.append(("meta", con_doc(meta={"versionId": "7", "lastUpdated": "2023-01-09T10:20:00+01:00"})))
    formas.append(("text", con_doc(text={"status": "generated", "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">x</div>"})))
    formas.append(("extensión ajena", con_doc(extension=[{"url": "urn:ext:propia", "valueString": "x"}])))
    formas.append(("display", con_doc(author=[{"reference": "urn:uuid:pr1", "display": "Dra. Ana Ensayo"}])))
    x = copy.deepcopy(b)
    x["type"] = "batch"
    formas.append(("Bundle.type", x))
    formas.append(("subject lógico", con_doc(subject={"identifier": {"value": "PAC0001"}})))
    for n, x in formas:
        mira("forma: %s" % n, sh(juzga(b=x)), [])


def p24():
    import mcp_verificador as M
    import verificar_conversor as VC
    import conversor_juguete as JG
    mira("punto en el esquema", "mdm_conv" in M.E_PROPS["punto_entrada"]["enum"], True)
    a = dict(ev_mdm(msg(), texto(bundle())), caso="p-md-24")
    esq = next(h for h in M.HERRAMIENTAS if h["name"] == "verificar_caso")["inputSchema"]
    M.validar(a, esq)
    out = M.t_verificar(a)[0]
    mira("MCP verificar_caso", (out["veredicto"]["categoria"], out["entrada"]["punto_entrada"]), ("correcto", "mdm_conv"))
    sin = dict(ev_mdm(msg()), caso="p-md-24b")
    sin.pop("conversion")
    mira("control sin conversion (DV-MD-2: como adt_conv)", M.t_verificar(sin)[0]["veredicto"]["categoria"], "indeterminado")
    t = M.t_tabla({"tabla": "perfil_guia_mdm"})[0]
    mira("perfil_guia_mdm: 46 filas con nivel y citas", (len(t["entradas"]), all("nivel" in f and f.get("citas") for f in t["entradas"])), (46, True))
    mira("niveles del perfil (39, 2, 4, 1)", {n: sum(1 for f in t["entradas"] if f["nivel"] == n) for n in ("cuenta", "convencion", "nota", "forma")},
         {"cuenta": 39, "convencion": 2, "nota": 4, "forma": 1})
    mira("control: perfiles de ADT, ORU y VXU sin cambios", (len(M.t_tabla({"tabla": "perfil_guia_adt"})[0]["entradas"]),
                                                              len(M.t_tabla({"tabla": "perfil_guia_oru"})[0]["entradas"]),
                                                              len(M.t_tabla({"tabla": "perfil_guia_vxu"})[0]["entradas"])), (21, 16, 27))
    info = M.t_info({})[0]
    mira("info declara mdm_conv", ("mdm_conv" in info["puntos_entrada"], "mdm" in info["conversores"]), (True, True))
    mira("punto de MDM", VC.punto(msg()), "mdm_conv")
    from prueba_conversion import msg as msg_adt, oru_msg
    import prueba_conversion_vxu as PV
    mira("control ADT, ORU, VXU y SIU", (VC.punto(msg_adt()), VC.punto(oru_msg()), VC.punto(PV.msg()), VC.punto(msg_adt(msh9="SIU^S12^SIU_S12"))),
         ("adt_conv", "oru_conv", "vxu_conv", "adt_conv"))
    m = msg(msh={8: "JUGUETE-NOMINAL"})
    acc, b = JG.convertir(m)
    r = j(ev_mdm(m, b))
    mira("juguete nominal MDM", (acc, cat(r), sh(r)), ("bundle", ("correcto", None), []))
    m = msg(msh={8: "JUGUETE-DOCSTATUS"})
    mira("control JUGUETE-DOCSTATUS (Q-MD-D-4)", sh(j(ev_mdm(m, JG.convertir(m)[1]))), [("fhir_invalido", "TXA-17")])
    m = msg(msh={8: "JUGUETE-TEXTO"})
    mira("control JUGUETE-TEXTO", sh(j(ev_mdm(m, JG.convertir(m)[1]))), [("dato_perdido", "OBX-5")])
    d = os.path.join(os.environ.get("TMPDIR", "/tmp"), "prueba_mdm_corpus")          # MD2-a: el corpus de MDM (bases_mdm.py)
    with redirect_stdout(io.StringIO()):
        co = VC.generar_corpus(d, lab=True, minimos=False)
    mira("corpus mdm (MD2-a)", co["n"].get("mdm"), 40)
    mira("control: adt, oru y vxu como hoy", (co["n"]["adt"], co["n"]["oru"], co["n"]["vxu"], co["por_corpus"]["adt"][:12],
                                               co["por_corpus"]["oru"][:12], co["por_corpus"]["vxu"][:12], co["huella_adt_oru_muestras"][:12]),
         (263, 40, 40, "7b4e7cfba041", "b5be5675b204", "3bcb0eefe4dd", "f2321d41fe7e"))      # medidos el 31-oct con el juez bde94016ca58
    mira("CORPUS: mdm al final", VC.CORPUS, ("adt", "oru", "vxu", "muestras", "minimos", "propio", "mdm"))
    mira("puntos del corpus mdm", {x["punto"] for x in co["casos"] if x["corpus"] == "mdm"}, {"mdm_conv"})
    mira("L-VC-2 nombra mdm_conv", "mdm_conv" in VC.L_VC["L-VC-2"], True)


def p25():
    """P-MD-25 e: el punto que da la herramienta solo cambia en MDM (a, b, c y d están en la línea base)."""
    import verificar_conversor as VC
    from prueba_conversion import msg as msg_adt, oru_msg
    import prueba_conversion_vxu as PV
    mira("MDM -> mdm_conv", [VC.punto(msg(msh={9: x})) for x in ("MDM^T02^MDM_T02", "MDM^T01^MDM_T01", "mdm^t06")], ["mdm_conv"] * 3)
    mira("lo demás como hoy", (VC.punto(msg_adt()), VC.punto(oru_msg()), VC.punto(PV.msg()), VC.punto(msg_adt(msh9="SIU^S12^SIU_S12")),
                               VC.punto(msg_adt(msh9="ORM^O01^ORM_O01"))), ("adt_conv", "oru_conv", "vxu_conv", "adt_conv", "adt_conv"))


def p26():
    import bases_mdm as BM
    mira("40 bases", [b["id"] for b in BM.BASES], ["B%02d" % k for k in range(1, 41)])
    with redirect_stdout(io.StringIO()):
        ok = BM.autoprueba()
    mira("autoprueba del corpus", ok, True)
    sin22 = [b["id"] for b in BM.BASES if BM.campos(b).get("TXA-17") in ("AU", "LA") and not BM.campos(b).get("TXA-22")]
    mira("TXA-22 en las bases AU y LA (DV-MD-7, [E9 CH09.txt:1798-1800])", sin22, [])
    bases = copy.deepcopy(BM.BASES)
    otra = copy.deepcopy(bases[0])
    otra["id"] = "B99"
    otra["segmentos"] = [s.replace("DOC0001", "DOC0099") for s in otra["segmentos"]]
    mira("control: una copia con un campo distinto rompe la firma", bool(BM.firma(bases + [otra])), True)


def p27():
    import conversion as CV
    import conversion_mdm as CVM
    with redirect_stdout(io.StringIO()):
        rc = CVM.autoprueba()
    mira("autoprueba de conversion_mdm", rc, 0)
    mira("ninguna clave de C_MDM choca con conversion.C salvo las de C_SEG",
         [k for k in CVM.C_MDM if k in CV.C and CV.C[k] != CVM.C_MDM[k] and k not in CVM.C_SEG], [])
    CVM.C_MDM["OBX-5"] = ["[G OBX_DocumentReference.csv:8-13]", "[E7 §7.4.2.5]"]
    try:
        with redirect_stdout(io.StringIO()):
            rc = CVM.autoprueba()
        mira("control: una clave OBX-5 en C_MDM hace fallar la autoprueba", rc, 1)
    finally:
        del CVM.C_MDM["OBX-5"]
    malas = []
    for m, b, _ in mutaciones_clase():
        for h in juzga(m, b)["hallazgos"]:
            if h["cuenta"] and re.match(r"^(TXA|OBX|NTE|ORC|OBR)", h["hecho"]):
                cs = h["citas"]
                if not (any(c.startswith(("[G ", "[CM ")) for c in cs) and any(c.startswith(("[E", "[F ", "[AMB")) for c in cs)):
                    malas.append((h["subtipo"], h["hecho"], cs))
    mira("todo hallazgo de MDM que cuenta: guía y estándar", malas, [])


PRUEBAS = [p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24,
           p25, p26, p27]
BASES = [("P-MD-1 base", base_p01), ("P-MD-25 base", base_p25)]


def main():
    rojo = sys.argv[1:] == ["rojo"]
    for nombre, b in BASES:
        grupo[0] = nombre
        try:
            b()
        except Exception as ex:
            FALLAN.add(nombre)
            print("  EXCEPCIÓN %s: %s" % (nombre, "".join(traceback.format_exception_only(type(ex), ex)).strip()[:300]))
            mal.append(nombre)
    bases_bien = not any(n in FALLAN for n, _ in BASES)
    for p in PRUEBAS:
        grupo[0] = "P-MD-%d" % int(p.__name__[1:])
        try:
            p()
        except Exception as ex:                                             # en rojo, lo esperado es que el PE o el módulo no existan
            FALLAN.add(grupo[0])
            RAZON.setdefault(grupo[0], "".join(traceback.format_exception_only(type(ex), ex)).strip()[:160])
            if not rojo:
                print("  EXCEPCIÓN %s: %s" % (grupo[0], RAZON[grupo[0]]))
                mal.append(grupo[0])
    nombres = ["P-MD-%d" % k for k in range(1, len(PRUEBAS) + 1)]
    if rojo:
        for n in nombres:
            print("  %-8s %s" % (n, ("ROJO: " + RAZON.get(n, "")) if n in FALLAN else "VERDE (no debía)"))
        print("PRUEBAS MDM (rojo): fallan %d de %d%s; líneas base %s" % (sum(n in FALLAN for n in nombres), len(PRUEBAS),
              " (TODAS)" if all(n in FALLAN for n in nombres) else "", "en verde" if bases_bien else "MAL"))
        return 0 if all(n in FALLAN for n in nombres) and bases_bien else 1
    pend = [n for n in nombres if n in FALLAN and n in MD2A]
    otras = [n for n in sorted(FALLAN) if n not in pend]
    if not otras and pend:
        print("PRUEBAS MDM: TODO BIEN salvo lo de MD2-a, en rojo y declarado: %s (%d comprobaciones, %d pruebas)" % (
            ", ".join("%s (%s)" % (n, MD2A[n]) for n in pend), n_ok[0], len(PRUEBAS)))
        return 1
    print("PRUEBAS MDM: %s (%d comprobaciones, %d pruebas)" % ("TODO BIEN" if not mal else "%d MAL" % len(mal), n_ok[0], len(PRUEBAS)))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
