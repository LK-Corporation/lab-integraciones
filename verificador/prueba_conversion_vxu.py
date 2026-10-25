#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 20, VX1-b (vx/diseno-vx-fable.md §7): P-VX-1..23, el juez ante la conversión de un VXU^V04 por un tercero, con
evidencia sintética. Los Bundles se escriben a mano (no salen del perfil: un fallo de la proyección no se confirmaría a sí
mismo); cada prueba cambia una sola cosa y lleva su control negativo. Mandan las decisiones de Jev (vx/decisiones-qvx.md), y
en cinco van contra la recomendación del diseñador: Q-VX-D-3 (manda RXA-22 si RXA-21 es A), Q-VX-D-4 (un OBX absorbido es
recurso ausente), Q-VX-D-6 (con un solo profesional la función es convención), Q-VX-D-8 (el lote repetido es convención).

Antes del código (sin el punto vxu_conv ni conversion_vxu) fallan todas: PE.resolver no conoce el punto.
  python3 prueba_conversion_vxu.py          -> TODO BIEN si no hay ningún MAL
  python3 prueba_conversion_vxu.py rojo     -> sale 0 solo si fallan las 23"""
import copy
import io
import json
import os
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
from prueba_conversion import seg, cc, S, ev, texto, num, con, sin_clave  # noqa: E402
sys.argv = _argv

mal, n_ok, grupo = [], [0], [None]
FALLAN = set()


def mira(nombre, obtenido, esperado):
    if obtenido == esperado:
        n_ok[0] += 1
    else:
        print("  MAL %s %s: %r != %r" % (grupo[0], nombre, obtenido, esperado))
        mal.append(nombre)
        FALLAN.add(grupo[0])


CVX, MVX = "http://hl7.org/fhir/sid/cvx", "http://terminology.hl7.org/CodeSystem/MVX"
RUTA_V3 = "http://terminology.hl7.org/CodeSystem/v3-RouteOfAdministration"
V2 = "http://terminology.hl7.org/CodeSystem/v2-%s"
UCUM = "http://unitsofmeasure.org"


# ---------------------------------------------------------------------------- el mensaje
MSH = {3: "REGVAC", 4: "CSSYN", 5: "REGISTRO", 6: "SALUD", 7: "20240115103000+0100", 9: "VXU^V04^VXU_V04", 10: "VX-N1", 11: "P",
       12: "2.5"}
PID = {1: "1", 3: "VAC0001^^^CSSYN^MR", 5: "Prueba^Mateo^^^^^L", 7: "20230512", 8: "M"}
ORC = {1: "RE", 3: "VX-01^REGVAC"}
RXA = {1: "0", 2: "1", 3: "20240115103000+0100", 4: "20240115103000+0100", 5: "03^MMR^CVX", 6: "0.5", 7: "mL^^UCUM",
       10: "1234^Goldstein^Harold", 15: "LOT-01", 16: "202511", 17: "MSD^Merck \\T\\ Co., Inc.^MVX", 20: "CP", 21: "A",
       22: "20240115104500+0100"}
RXR = {1: "IM^Intramuscular^HL70162", 2: "LD^Left Deltoid^HL70163"}


def junta(base, cambios):
    d = dict(base)
    for k, v in (cambios or {}).items():
        if v is None:
            d.pop(k, None)
        else:
            d[k] = v
    return d


def grupo_orden(orc=None, rxa=None, rxr=None, obx=(), sin_rxr=False, sin_orc=False):
    s = [] if sin_orc else [seg("ORC", junta(ORC, orc))]
    s.append(seg("RXA", junta(RXA, rxa)))
    if not sin_rxr:
        s.append(seg("RXR", junta(RXR, rxr)))
    return s + list(obx)


def msg(msh=None, pid=None, grupos=None, antes_orden=(), **k):
    """Un VXU^V04: MSH, PID, lo que vaya antes del grupo ORDER (PD1, NK1, PV1…) y los grupos (por omisión, uno nominal)."""
    segs = [seg("MSH", junta(MSH, msh)), seg("PID", junta(PID, pid))] + list(antes_orden)
    for g in grupos if grupos is not None else [grupo_orden(**k)]:
        segs += g
    return "\r".join(segs)


# ---------------------------------------------------------------------------- el Bundle (a mano)
def pac():
    return {"resourceType": "Patient", "id": "p1",
            "identifier": [{"value": "VAC0001", "type": cc("0203", "MR"), "assigner": {"display": "CSSYN"}}],
            "name": [{"family": "Prueba", "given": ["Mateo"], "use": "official"}], "birthDate": "2023-05-12", "gender": "male"}


def inm(i="i1"):
    return {"resourceType": "Immunization", "id": i,
            "identifier": [{"value": "VX-01", "type": cc("0203", "FILL")}],
            "status": "completed",
            "vaccineCode": {"coding": [{"system": CVX, "code": "03", "display": "MMR"}]},
            "patient": {"reference": "urn:uuid:p1"},
            "occurrenceDateTime": "2024-01-15T10:30:00+01:00",
            "recorded": "2024-01-15T10:45:00+01:00",
            "lotNumber": "LOT-01", "expirationDate": "2025-11",
            "manufacturer": {"reference": "urn:uuid:o1"},
            "route": {"coding": [{"system": RUTA_V3, "code": "IM"}]},
            "site": {"coding": [{"system": V2 % "0163", "code": "LD"}]},
            "doseQuantity": {"value": num("0.5"), "unit": "mL", "system": UCUM, "code": "mL"},
            "performer": [{"function": {"coding": [{"system": V2 % "0443", "code": "AP"}]}, "actor": {"reference": "urn:uuid:pr1"}}]}


def prac(i="pr1", ident="1234", family="Goldstein", given=("Harold",)):
    return {"resourceType": "Practitioner", "id": i, "identifier": [{"value": ident}], "name": [{"family": family, "given": list(given)}]}


def org():
    return {"resourceType": "Organization", "id": "o1", "identifier": [{"system": MVX, "value": "MSD"}], "name": "Merck & Co., Inc."}


def bundle(i=None, p=None, extra=(), sin=(), inms=None):
    rs = [p or pac()] + (inms if inms is not None else [i or inm()]) + [prac(), org()] + list(extra)
    return {"resourceType": "Bundle", "type": "collection",
            "entry": [{"fullUrl": "urn:uuid:" + r["id"], "resource": r} for r in rs if r["resourceType"] not in sin]}


def bundle_con_org(o):
    b = bundle()
    b["entry"][3]["resource"] = o
    return b


def ev_vxu(m, b=None, **k):
    return ev(m, b, pe="vxu_conv", **k)


def j(e):
    return V.verificar(e)


def cat(r):
    return (r["veredicto"]["categoria"], r["veredicto"].get("subtipo"))


def sh(r):
    """Los que cuentan, como (subtipo, hecho)."""
    return sorted((h["subtipo"], h["hecho"]) for h in r["hallazgos"] if h["cuenta"])


def notas(r):
    return sorted({s for h in r["hallazgos"] if not h["cuenta"] for s in (h["subtipo"] or "").split("+")})


def juzga(m=None, b=None, **k):
    return j(ev_vxu(m or msg(), b if b is not None else bundle(), **k))


def con_inm(**k):
    return bundle(i=con(inm, **k))


# ---------------------------------------------------------------------------- P-VX-1..23
def p01():
    mira("gramática", EH.gramatica("VXU_V04")[0], ["SEG", "MSH", False, False])
    mira("estructura del PE", PE.estructura_de(MR.mensajes(msg())[0], PE.PUNTOS["vxu_conv"]), "VXU_V04")
    r = juzga()
    mira("nominal", (cat(r), sh(r)), (("correcto", None), []))
    rc = r["conversion"]["recuentos"]
    mira("recuentos", (rc.get("Patient"), rc.get("Immunization"), rc.get("grupos_orden")), (1, 1, 1))
    r = juzga(b=con_inm(status="not-done"))
    mira("control status", (cat(r), sh(r)), (("fallo_silencioso", "convertido"), [("codigo_mal_mapeado", "RXA-20")]))


def p02():
    for c20, c21, esperado in (("CP", "A", "completed"), ("PA", "A", "completed"), ("RE", "A", "not-done"), ("NA", "A", "not-done"),
                               (None, None, "completed"), ("CP", "D", "entered-in-error")):
        r = juzga(msg(rxa={20: c20, 21: c21}), con_inm(status=esperado))
        mira("status %s/%s" % (c20, c21), sh(r), [])
    r = juzga(msg(rxa={21: "D"}), con_inm(status="completed"))
    mira("control D ignorado", sh(r), [("valor_distinto", "RXA-21")])
    r = juzga(msg(rxa={20: None, 21: None}), con_inm(status="not-done"))
    mira("control vacío", sh(r), [("valor_distinto", "RXA-20")])
    r = juzga(msg(rxa={20: "XX"}), con_inm(status="XX"))
    mira("control imposible", ("valor_imposible_convertido" in {h["subtipo"].split("+")[0] for h in r["hallazgos"] if h["cuenta"]},
                                "fhir_invalido" in {s for h in r["hallazgos"] if h["cuenta"] for s in h["subtipo"].split("+")}), (True, True))
    r = j(ev_vxu(msg(rxa={20: "XX"}), estado="error", error={"codigo": "1", "texto": "tabla 0322"}))
    mira("control imposible con error", (cat(r), "aceptable" in notas(r)), (("correcto", None), True))
    r = juzga(b=bundle(i=sin_clave(inm(), "status")))
    mira("control status ausente", sh(r), [("fhir_invalido", "RXA-20")])


def p03():
    i = con(inm, vaccineCode={"coding": [{"system": CVX, "code": "03"}, {"system": "urn:local", "code": "TV"}]})
    r = juzga(msg(rxa={5: "03^MMR^CVX^TV^Triple virica^L"}), bundle(i=i))
    mira("CE.1 y CE.4", sh(r), [])
    r = juzga(b=con_inm(vaccineCode={"coding": [{"system": CVX, "code": "3"}]}))
    mira("control código", sh(r), [("valor_distinto", "RXA-5")])
    r = juzga(b=con_inm(vaccineCode={"text": "MMR"}))
    mira("control sin coding", sh(r), [("dato_perdido", "RXA-5")])
    r = juzga(b=con_inm(vaccineCode={"coding": [{"code": "03"}]}))
    mira("control sin system de CVX (DV-VX-3: como CV._codigo)", sh(r), [("dato_perdido", "RXA-5")])
    r = juzga(b=con_inm(vaccineCode={"coding": [{"system": "urn:oid:2.16.840.1.113883.12.292", "code": "03"}]}))
    mira("control otro system de CVX (Q-VX-D-1: fijar)", sh(r), [("codigo_mal_mapeado", "RXA-5")])
    r = juzga(msg(rxa={5: "03^MMR^HL70292"}), con_inm(vaccineCode={"coding": [{"system": V2 % "0292", "code": "03"}]}))
    mira("HL70292: convención", sh(r), [])
    # VX3, revisión adversaria (H2, DV-VX-7): la uri de la tabla v2 de R4 también vale para CVX y MVX
    mira("CVX con v2-0292", sh(juzga(b=con_inm(vaccineCode={"coding": [{"system": V2 % "0292", "code": "03"}]}))), [])
    o = dict(org(), identifier=[{"system": V2 % "0227", "value": "MSD"}])
    mira("MVX con v2-0227", sh(juzga(b=bundle_con_org(o))), [])


def p04():
    r = juzga(msg(rxa={3: "20240115", 4: None}), con_inm(occurrenceDateTime="2024-01-15"))
    mira("solo fecha", sh(r), [])
    r = juzga(msg(rxa={3: "20240115103000+0200", 4: None}), con_inm(occurrenceDateTime="2024-01-15T08:30:00Z"))
    mira("con zona, por instante", sh(r), [])
    r = juzga(msg(rxa={3: "202401151015", 4: None}), con_inm(occurrenceDateTime="2024-01-15T10:15:00+01:00"))
    mira("sin zona, la hora escrita", sh(r), [])
    r = juzga(msg(rxa={3: "20240115", 4: None}), con_inm(occurrenceDateTime="2024-01-15T00:00:00+01:00"))
    mira("control hora inventada", sh(r), [("dato_inventado", "RXA-3")])
    r = juzga(msg(rxa={3: "202401151015", 4: None}), con_inm(occurrenceDateTime="2024-01-15T10:15:00"))
    mira("control hora sin zona en FHIR", sh(r), [("fhir_invalido", "RXA-3")])
    i = sin_clave(inm(), "occurrenceDateTime")
    i["occurrenceString"] = "2024-01-15T10:30:00+01:00"
    mira("control occurrenceString", sh(juzga(b=bundle(i=i))), [("valor_distinto", "RXA-3")])
    r = juzga(msg(rxa={4: "20240115113000+0100"}), con_inm(occurrenceDateTime="2024-01-15T11:30:00+01:00"))
    mira("control RXA-4 usado", sh(r), [("valor_distinto", "RXA-3")])


def p05():
    r = juzga(msg(rxa={6: ".5"}), con_inm(doseQuantity={"value": num("0.5"), "unit": "mL", "system": UCUM, "code": "mL"}))
    mira(".5 como 0.5", sh(r), [])
    r = juzga(msg(rxa={7: "mL^mililitro^UCUM"}), con_inm(doseQuantity={"value": num("0.5"), "unit": "mililitro", "system": UCUM, "code": "mL"}))
    mira("unit = CE.2", sh(r), [])
    r = juzga(b=con_inm(doseQuantity={"value": num("0.50"), "unit": "mL", "system": UCUM, "code": "mL"}))
    mira("control 0.50", sh(r), [("valor_distinto", "RXA-6")])
    r = juzga(b=con_inm(doseQuantity={"value": num("0.5"), "system": UCUM, "code": "mL"}))
    mira("control sin unit", sh(r), [("dato_perdido", "RXA-7")])
    r = juzga(b=con_inm(doseQuantity={"value": num("0.5"), "unit": "mL", "system": V2 % "0396", "code": "mL"}))
    mira("control system v2", sh(r), [("codigo_mal_mapeado", "RXA-7")])
    r = juzga(msg(rxa={7: None}), con_inm(doseQuantity={"value": num("0.5"), "unit": "mL"}))
    mira("control unit inventada", sh(r), [("dato_inventado", "RXA-7")])


def p06():
    for rxr1, cod in (("IM^Intramuscular^HL70162", {"system": RUTA_V3, "code": "IM"}), ("SC^Subcutaneous^HL70162", {"system": RUTA_V3, "code": "SQ"}),
                      ("PO^Oral^HL70162", {"system": RUTA_V3, "code": "PO"}), ("ID^Intradermal^HL70162", {"system": RUTA_V3, "code": "IDINJ"}),
                      ("IN^Inhalation^HL70162", {"system": V2 % "0162", "code": "IN"})):
        r = juzga(msg(rxr={1: rxr1}), con_inm(route={"coding": [cod]}))
        mira("ruta %s" % rxr1[:2], sh(r), [])
    r = juzga(msg(rxr={2: "DELT^Deltoid^HL70550"}), con_inm(site={"coding": [{"system": V2 % "0550", "code": "DELT"}]}))
    mira("sitio de la 0550", sh(r), [])
    r = juzga(msg(rxr={2: "368208006^Left upper arm^SCT"}), con_inm(site={"coding": [{"system": "http://snomed.info/sct", "code": "368208006"}]}))
    mira("sitio SNOMED: convención", sh(r), [])
    r = juzga(b=con_inm(route={"coding": [{"system": V2 % "0162", "code": "IM"}]}))
    mira("control ruta v2-0162", sh(r), [("codigo_mal_mapeado", "RXR-1")])
    r = juzga(b=con_inm(site={"coding": [{"system": V2 % "0550", "code": "LD"}]}))
    mira("control LD en la 0550", sh(r), [("codigo_mal_mapeado", "RXR-2")])
    i = sin_clave(inm(), "route", "site")
    mira("sin RXR", sh(juzga(msg(sin_rxr=True), bundle(i=i))), [])
    mira("control ruta sin RXR", sh(juzga(msg(sin_rxr=True), bundle(i=sin_clave(inm(), "site")))), [("dato_inventado", "RXR-1")])
    mira("control ruta perdida", sh(juzga(b=bundle(i=sin_clave(inm(), "route")))), [("dato_perdido", "RXR-1")])


def dos_performers(f_ap=True, f_op=True):
    i = inm()
    i["performer"] = [{"actor": {"reference": "urn:uuid:pr1"}}, {"actor": {"reference": "urn:uuid:pr2"}}]
    if f_ap:
        i["performer"][0]["function"] = {"coding": [{"system": V2 % "0443", "code": "AP"}]}
    if f_op:
        i["performer"][1]["function"] = {"coding": [{"system": V2 % "0443", "code": "OP"}]}
    return i


def p07():
    m = msg(orc={12: "5678^Ruiz^Ana"})
    b = bundle(i=dos_performers(), extra=[prac("pr2", "5678", "Ruiz", ("Ana",))])
    mira("AP y OP con Practitioner", sh(juzga(m, b)), [])
    rol = {"resourceType": "PractitionerRole", "id": "pr2", "practitioner": {"reference": "urn:uuid:pr3"}}
    b = bundle(i=dos_performers(), extra=[rol, prac("pr3", "5678", "Ruiz", ("Ana",))])
    mira("OP con PractitionerRole", sh(juzga(m, b)), [])
    i = dos_performers()
    i["performer"][0]["function"], i["performer"][1]["function"] = i["performer"][1]["function"], i["performer"][0]["function"]
    r = juzga(m, bundle(i=i, extra=[prac("pr2", "5678", "Ruiz", ("Ana",))]))
    mira("control funciones intercambiadas", sh(r), [("codigo_mal_mapeado", "ORC-12"), ("codigo_mal_mapeado", "RXA-10")])
    i = inm()
    i["performer"] = [{"function": {"coding": [{"system": V2 % "0443", "code": "AP"}]}, "actor": {"display": "Goldstein"}}]
    mira("control solo display", sh(juzga(b=bundle(i=i))), [("dato_perdido", "RXA-10")])
    i = inm()
    i["performer"][0]["actor"] = {"reference": "urn:uuid:o1"}
    mira("control actor Organization", sh(juzga(b=bundle(i=i))), [("dato_perdido", "RXA-10")])
    i = inm()
    del i["performer"][0]["function"]
    mira("un solo profesional sin función: convención (Q-VX-D-6)", sh(juzga(b=bundle(i=i))), [])
    r = juzga(m, bundle(i=dos_performers(False, False), extra=[prac("pr2", "5678", "Ruiz", ("Ana",))]))
    mira("control dos sin función: dato perdido (Q-VX-D-6)", sh(r), [("dato_perdido", "ORC-12"), ("dato_perdido", "RXA-10")])


def p08():
    o = {"resourceType": "Organization", "id": "o9", "identifier": [{"system": MVX, "value": "MSD"}], "name": "Merck & Co., Inc."}
    mira("contained", sh(juzga(b=con_inm(manufacturer={"reference": "#o9"}, contained=[o]))), [])
    mira("lógico", sh(juzga(b=con_inm(manufacturer={"identifier": {"system": MVX, "value": "MSD"}, "display": "Merck & Co., Inc."}))), [])
    mira("control solo display", sh(juzga(b=con_inm(manufacturer={"display": "Merck"}))), [("dato_perdido", "RXA-17")])
    b = bundle()
    b["entry"][3]["resource"]["name"] = "Merck \\T\\ Co., Inc."
    mira("control escape sin deshacer", sh(juzga(b=b)), [("valor_distinto", "RXA-17")])
    r = juzga(msg(rxa={17: "^Laboratorio Sintetico^"}), con_inm(manufacturer={"display": "Laboratorio Sintetico"}))
    mira("solo texto: convención", sh(r), [])


def p09():
    mira("lote repetido, el primero", sh(juzga(msg(rxa={15: "LOT-A~DIL-B"}), con_inm(lotNumber="LOT-A"))), [])
    mira("lote repetido, el segundo: convención (Q-VX-D-8)", sh(juzga(msg(rxa={15: "LOT-A~DIL-B"}), con_inm(lotNumber="DIL-B"))), [])
    mira("caducidad completa", sh(juzga(msg(rxa={16: "20251130"}), con_inm(expirationDate="2025-11-30"))), [])
    mira("control día inventado", sh(juzga(b=con_inm(expirationDate="2025-11-01"))), [("dato_inventado", "RXA-16")])
    mira("control lote perdido", sh(juzga(b=bundle(i=sin_clave(inm(), "lotNumber")))), [("dato_perdido", "RXA-15")])
    mira("control lote distinto", sh(juzga(b=con_inm(lotNumber="LOT-02"))), [("valor_distinto", "RXA-15")])


def p10():
    m = msg(rxa={20: "RE", 18: "REL^Motivo religioso^L"})
    mira("statusReason", sh(juzga(m, con_inm(status="not-done", statusReason={"coding": [{"code": "REL"}]}))), [])
    m2 = msg(rxa={19: "DM^Diabetes^L~ASM^Asma^L"})
    mira("dos reasonCode", sh(juzga(m2, con_inm(reasonCode=[{"coding": [{"code": "DM"}]}, {"coding": [{"code": "ASM"}]}]))), [])
    mira("control un reasonCode", sh(juzga(m2, con_inm(reasonCode=[{"coding": [{"code": "DM"}]}]))), [("dato_perdido", "RXA-19")])
    mira("control statusReason perdido", sh(juzga(m, con_inm(status="not-done"))), [("dato_perdido", "RXA-18")])
    mira("control statusReason inventado", sh(juzga(b=con_inm(statusReason={"coding": [{"code": "REL"}]}))), [("dato_inventado", "RXA-18")])


def p11():
    m = msg(orc={9: "20240115104000+0100"}, rxa={21: None, 22: None})
    mira("solo ORC-9", sh(juzga(m, con_inm(recorded="2024-01-15T10:40:00+01:00"))), [])
    mira("RXA-22 con A", sh(juzga()), [])
    m = msg(orc={9: "20240115104000+0100"})
    mira("los dos con A: manda RXA-22 (Q-VX-D-3)", sh(juzga(m, bundle())), [])
    mira("control los dos con A y ORC-9 puesto", sh(juzga(m, con_inm(recorded="2024-01-15T10:40:00+01:00"))), [("valor_distinto", "RXA-22")])
    m = msg(rxa={21: "U"})
    mira("RXA-22 con U y ORC-9 vacío: convención", (sh(juzga(m, bundle())), "convencion" in notas(juzga(m, bundle()))), ([], True))
    mira("control recorded inventado", sh(juzga(msg(rxa={21: None, 22: None}), bundle())), [("dato_inventado", "ORC-9")])
    m = msg(orc={9: "20240115104000+0100"}, rxa={21: None, 22: None})
    mira("control ORC-9 perdido", sh(juzga(m, bundle(i=sin_clave(inm(), "recorded")))), [("dato_perdido", "ORC-9")])


def p12():
    m = msg(orc={2: "PL-1", 3: "VX-1^REGVAC"})
    ids = [{"value": "PL-1", "type": cc("0203", "PLAC")}, {"value": "VX-1", "type": cc("0203", "FILL")}]
    mira("PLAC y FILL", sh(juzga(m, con_inm(identifier=ids))), [])
    mal_ = [{"value": "PL-1", "type": cc("0203", "FILL")}, {"value": "VX-1", "type": cc("0203", "PLAC")}]
    mira("control intercambiados", sh(juzga(m, con_inm(identifier=mal_))), [("codigo_mal_mapeado", "ORC-2"), ("codigo_mal_mapeado", "ORC-3")])
    mira("control FILL perdido", sh(juzga(m, con_inm(identifier=ids[:1]))), [("dato_perdido", "ORC-3")])
    r = juzga(b=con_inm(identifier=[{"value": "VX-01", "type": cc("0203", "FILL")}, {"system": "urn:conv", "value": "x1"}]))
    mira("identifier propio: nota", (sh(r), "extra" in notas(r)), ([], True))


def p13():
    g1 = grupo_orden(orc={3: "VX-01^REGVAC"})
    g2 = grupo_orden(orc={3: "VX-02^REGVAC"}, rxa={5: "10^IPV^CVX", 15: "LOT-02"})
    i2 = con(inm, id="i2", identifier=[{"value": "VX-02", "type": cc("0203", "FILL")}],
             vaccineCode={"coding": [{"system": CVX, "code": "10", "display": "IPV"}]}, lotNumber="LOT-02")
    r = juzga(msg(grupos=[g1, g2]), bundle(inms=[inm(), i2]))
    por = sorted({x["emparejado_por"] for x in r["conversion"]["emparejamiento"] if x["rol"].startswith("Immunization")})
    mira("dos grupos por identifier", (sh(r), r["conversion"]["recuentos"]["Immunization"], por), ([], 2, ["identifier"]))
    tres = [grupo_orden(orc={3: None}, rxa={3: f, 4: None, 15: "L%d" % k}) for k, f in enumerate(("20230105", "20230305", "20230505"))]
    ims = [con(inm, id="i%d" % k, identifier=[], occurrenceDateTime="2023-%02d-05" % (2 * k + 1), lotNumber="L%d" % k) for k in range(3)]
    for x in ims:
        del x["identifier"]
    r = juzga(msg(grupos=tres), bundle(inms=ims[::-1]))
    por = sorted({x["emparejado_por"] for x in r["conversion"]["emparejamiento"] if x["rol"].startswith("Immunization")})
    mira("tres del mismo código por código y fecha", (sh(r), por), ([], ["codigo+fecha"]))
    r = juzga(msg(grupos=[g1, g2]), bundle(inms=[inm()]))
    mira("control una para dos", sh(r), [("recurso_ausente", "RXA(2)-5")])
    r = juzga(b=bundle(inms=[inm(), con(inm, id="i9", identifier=[{"value": "VX-99", "type": cc("0203", "FILL")}],
                                         vaccineCode={"coding": [{"system": CVX, "code": "21"}]})]))
    mira("control de más", sh(r), [("recurso_inventado", "RXA")])
    # VX2-c (Microsoft, B35): dos grupos sin ORC-3 fundidos en una Immunization con los dos códigos y la fecha del segundo:
    # el segundo se empareja por código y fecha antes de que el primero se la lleve por código
    g1 = grupo_orden(orc={3: None}, rxa={5: "88^Gripe^CVX", 4: None})
    g2 = grupo_orden(orc={3: None}, rxa={3: "20240115113000+0100", 4: None, 5: "09^Td^CVX", 15: "LOT-02"})
    fundida = sin_clave(con(inm, vaccineCode={"coding": [{"system": CVX, "code": "88"}, {"system": CVX, "code": "09"}]},
                            occurrenceDateTime="2024-01-15T11:30:00+01:00", lotNumber="LOT-02"), "identifier")
    r = juzga(msg(grupos=[g1, g2]), bundle(i=fundida))
    mira("VX2-c: código y fecha de todos los grupos antes que el código solo", sh(r), [("recurso_ausente", "RXA-5")])
    gemela = sin_clave(con(inm, id="i8"), "identifier")
    r = juzga(msg(orc={3: None}), bundle(inms=[sin_clave(inm(), "identifier"), gemela]))
    mira("control dos candidatas iguales", cat(r), ("indeterminado", "emparejamiento"))


OBX_CE = seg("OBX", {1: "1", 2: "CE", 3: "64994-7^Elegibilidad^LN", 5: "ELE^Elegible programa^L", 11: "F"})


def obs(i="ob1", parte="urn:uuid:i1", sujeto="urn:uuid:p1"):
    o = {"resourceType": "Observation", "id": i, "status": "final", "code": cc("loinc", "64994-7"),
         "valueCodeableConcept": {"coding": [{"code": "ELE"}]}}
    if sujeto:
        o["subject"] = {"reference": sujeto}
    if parte:
        o["partOf"] = [{"reference": parte}]
    return o


def p14():
    m = msg(obx=[OBX_CE])
    mira("OBX con partOf", sh(juzga(m, bundle(extra=[obs()]))), [])
    nm = seg("OBX", {1: "2", 2: "NM", 3: "30973-2^Dosis de la serie^LN", 5: "1", 11: "F"})
    o2 = {"resourceType": "Observation", "id": "ob2", "status": "final", "code": cc("loinc", "30973-2"), "valueQuantity": {"value": num("1")},
          "subject": {"reference": "urn:uuid:p1"}, "partOf": [{"reference": "urn:uuid:i1"}]}
    mira("OBX CE y NM", sh(juzga(msg(obx=[OBX_CE, nm]), bundle(extra=[obs(), o2]))), [])
    mira("control sin partOf", sh(juzga(m, bundle(extra=[obs(parte=None)]))), [("dato_perdido", "OBX-3")])
    otra = con(inm, id="i2", identifier=[{"value": "VX-02", "type": cc("0203", "FILL")}])
    g2 = grupo_orden(orc={3: "VX-02^REGVAC"})
    r = juzga(msg(grupos=[grupo_orden(obx=[OBX_CE]), g2]), bundle(inms=[inm(), otra], extra=[obs(parte="urn:uuid:i2")]))
    mira("control partOf a otra", ("referencia_rota", "OBX-3") in sh(r), True)
    # VX1-e (Microsoft, VXU-V04-02): el OBX del grupo 1 sin Observation no se lleva la del grupo 2 que trae su código en CE.4
    ox = seg("OBX", {1: "1", 2: "CE", 3: "29769-7^Fecha VIS^LN^64994-7", 5: "ELE^Elegible programa^L", 11: "F"})
    o2 = dict(obs("ob2", parte="urn:uuid:i2"), code={"coding": [{"system": S["loinc"], "code": "29769-7"}, {"system": S["loinc"], "code": "64994-7"}]})
    r = juzga(msg(grupos=[grupo_orden(obx=[OBX_CE]), grupo_orden(orc={3: "VX-02^REGVAC"}, obx=[ox])]), bundle(inms=[inm(), otra], extra=[o2]))
    mira("VX1-e: la Observation de otro grupo no se empareja por código antes que por partOf", sh(r), [("recurso_ausente", "OBX-3")])
    r = juzga(m, con_inm(programEligibility=[{"coding": [{"code": "ELE"}]}]))
    mira("absorbido: recurso ausente (Q-VX-D-4)", sh(r), [("recurso_ausente", "OBX-3")])
    mira("control sin Observation", sh(juzga(m, bundle())), [("recurso_ausente", "OBX-3")])


NK1 = seg("NK1", {1: "1", 2: "Prueba^Lucia^^^^^L", 3: "MTH^Madre^HL70063", 5: "^PRN^PH^^^^5551234", 15: "F", 16: "19900301"})


def madre(rel=None):
    return {"resourceType": "RelatedPerson", "id": "rp1", "patient": {"reference": "urn:uuid:p1"},
            "name": [{"family": "Prueba", "given": ["Lucia"], "use": "official"}],
            "relationship": [rel or {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode", "code": "MTH"}]}],
            "telecom": [{"system": "phone", "value": "5551234", "use": "home"}], "gender": "female", "birthDate": "1990-03-01"}


def p15():
    m = msg(antes_orden=[NK1])
    mira("RelatedPerson", sh(juzga(m, bundle(extra=[madre()]))), [])
    p = pac()
    c = madre()
    p["contact"] = [{"name": c["name"][0], "relationship": c["relationship"], "telecom": c["telecom"], "gender": "female"}]
    mira("Patient.contact, sin birthDate: convención", sh(juzga(m, bundle(p=p))), [])
    r = juzga(m, bundle(extra=[madre({"coding": [{"system": V2 % "0063", "code": "MTH"}]})]))
    mira("control MTH en la 0063", sh(r), [("codigo_mal_mapeado", "NK1-3")])
    # VX3, revisión adversaria (H10, DV-VX-9): con solo XTN.7, la guía lleva el número a la extensión contactpoint-local
    loc = "http://hl7.org/fhir/StructureDefinition/contactpoint-local"
    t_ext = [{"system": "phone", "use": "home", "extension": [{"url": loc, "valueString": "5551234"}]}]
    mira("teléfono XTN.7 en contactpoint-local", sh(juzga(m, bundle(extra=[dict(madre(), telecom=t_ext)]))), [])
    mira("control teléfono en ningún sitio", sh(juzga(m, bundle(extra=[dict(madre(), telecom=[{"system": "phone", "use": "home"}])]))),
         [("dato_perdido", "NK1-5")])
    mira("control ni una ni otra", sh(juzga(m, bundle())), [("recurso_ausente", "NK1-2")])
    # VX1-e (Microsoft, VXU-V04-01): la guía también crea RelatedPerson desde GT1 e IN1, que el perfil no juzga (L-VX-10)
    gt1 = seg("GT1", {1: "1", 3: "Garante^Pedro^^^^^L"})
    garante = dict(madre(), id="rp2", name=[{"family": "Garante", "given": ["Pedro"]}], relationship=[{"coding": [{"code": "BRO"}]}])
    r = juzga(msg(antes_orden=[NK1, gt1]), bundle(extra=[madre(), garante]))
    mira("VX1-e: RelatedPerson del GT1, nota", (sh(r), "fuera_proyeccion" in notas(r)), ([], True))
    r = juzga(msg(antes_orden=[NK1, gt1]), bundle(extra=[garante]))
    mira("VX1-e: control, el del GT1 no ocupa el sitio del NK1 por orden", sh(r), [("recurso_ausente", "NK1-2")])
    # VX2-c (Microsoft, B39): el garante se llama como el NK1; desempata la relación (NK1-3)
    gt1b = seg("GT1", {1: "1", 3: "Prueba^Lucia^^^^^L"})
    homonima = dict(madre(), id="rp3", relationship=[])
    r = juzga(msg(antes_orden=[NK1, gt1b]), bundle(extra=[homonima, madre()]))
    mira("VX2-c: dos RelatedPerson con el apellido del NK1, desempata la relación", (cat(r), sh(r)), (("correcto", None), []))


def p16():
    pv1 = seg("PV1", {1: "1", 2: "O", 19: "V9"})
    enc = {"resourceType": "Encounter", "id": "e1", "status": "in-progress", "class": {"system": S["act"], "code": "AMB"},
           "identifier": [{"value": "V9"}], "subject": {"reference": "urn:uuid:p1"}}
    m = msg(antes_orden=[pv1])
    mira("PV1 con Encounter, sin referencia: convención (Q-VX-D-9)", sh(juzga(m, bundle(extra=[enc]))), [])
    mira("PV1 sin Encounter: convención", sh(juzga(m, bundle())), [])
    mira("control referencia rota", sh(juzga(m, bundle(i=con(inm, encounter={"reference": "urn:uuid:nada"}), extra=[enc]))),
         [("referencia_rota", "PV1-19")])
    mira("control encounter sin PV1", sh(juzga(b=bundle(i=con(inm, encounter={"reference": "urn:uuid:e1"})))),
         [("dato_inventado", "PV1-19")])
    mira("control Encounter sin PV1", sh(juzga(b=bundle(i=con(inm, encounter={"reference": "urn:uuid:e1"}), extra=[enc]))),
         [("recurso_inventado", "PV1")])
    mira("control dos Encounter", sh(juzga(m, bundle(extra=[enc, dict(enc, id="e2", identifier=[{"value": "V8"}])]))),
         [("recurso_duplicado", "PV1")])


def p17():
    pd1 = seg("PD1", {3: "Centro^^^^^^^^^C1", 16: "A^Activo^L"})
    m = msg(antes_orden=[pd1], rxa={11: "^^^CENTRO1"})
    r = juzga(m, con_inm(location={"display": "Centro"}))
    mira("PD1 y RXA-11: notas", (sh(r), "fuera_proyeccion" in notas(r)), ([], True))
    r = juzga(msg(antes_orden=[OBX_CE]))
    mira("OBX antes del ORC: recuento", (sh(r), r["conversion"]["recuentos"].get("obx_fuera_orden")), ([], 1))
    mira("control location sin RXA-11: nota extra", ("extra" in notas(juzga(b=con_inm(location={"display": "x"}))),
                                                     sh(juzga(b=con_inm(location={"display": "x"})))), (True, []))
    mira("control primarySource por omisión (Q-VX-D-7)", sh(juzga(b=con_inm(primarySource=True))), [("dato_inventado", "RXA")])
    # VX3, revisión adversaria (H19, DV-VX-8): deducidos de un campo, no «por omisión»: nota de convención
    r = juzga(msg(rxa={9: "00^Nuevo registro^NIP001"}), con_inm(primarySource=True))
    mira("primarySource con RXA-9: convención", (sh(r), "convencion" in notas(r)), ([], True))
    r = juzga(msg(rxa={20: "PA"}), con_inm(isSubpotent=True))
    mira("isSubpotent con RXA-20 PA: convención (R4 Immunization.isSubpotent)", (sh(r), "convencion" in notas(r)), ([], True))
    mira("control isSubpotent con CP", sh(juzga(b=con_inm(isSubpotent=True))), [("dato_inventado", "RXA")])
    mira("control reportOrigin sin RXA-9", sh(juzga(b=con_inm(reportOrigin={"coding": [{"code": "01"}]}))), [("dato_inventado", "RXA-9")])


def p18():
    r = juzga(msg(msh={9: "VXU^V04"}))
    mira("MSH-9.3 vacío", sh(r), [])
    r = juzga(msg(msh={12: "2.5.1"}, rxa={20: "XX"}), con_inm(status="completed"))
    mira("2.5.1 con RXA-20 fuera: versión", (sh(r), "version" in notas(r)), ([], True))
    r = j(ev_vxu(msg(), estado="error", error={"codigo": "1", "texto": "fallo"}))
    mira("error con VXU válido", (cat(r), sh(r)), (("rechazo_incorrecto", "error"), [("incorrecto", "MSH-9")]))
    # VX2a (base B29): una ruta local declarada (CE.3 = L) no es un valor imposible; sin sistema o con HL70162, sí
    r = j(ev_vxu(msg(rxr={1: "JET^Inyector a presion^L"}), estado="error", error={"codigo": "1", "texto": "ruta"}))
    mira("error con ruta local: rechazo incorrecto", cat(r), ("rechazo_incorrecto", "error"))
    r = j(ev_vxu(msg(rxr={1: "XX^Desconocida^HL70162"}), estado="error", error={"codigo": "1", "texto": "ruta"}))
    mira("control error con ruta fuera de la 0162: aceptable", (cat(r), "aceptable" in notas(r)), (("correcto", None), True))
    r = j(ev_vxu(msg(msh={9: "QBP^Q11^QBP_Q11"}), estado="error", error={"codigo": "1", "texto": "x"}))
    mira("control QBP fuera de alcance", cat(r), ("fuera_de_alcance", None))
    r = j(ev_vxu("\r".join(msg().split("\r")[:1] + msg().split("\r")[2:]), estado="error", error={"codigo": "1", "texto": "sin PID"}))
    mira("control error sin PID: aceptable", (cat(r), "aceptable" in notas(r)), (("correcto", None), True))


def p19():
    casos = {
        "valor_distinto": con_inm(lotNumber="OTRO"),
        "dato_perdido": bundle(i=sin_clave(inm(), "expirationDate")),
        "dato_inventado": con_inm(statusReason={"coding": [{"code": "X"}]}),
        "codigo_mal_mapeado": con_inm(route={"coding": [{"system": V2 % "0162", "code": "IM"}]}),
        "recurso_ausente": bundle(inms=[]),
        "recurso_inventado": bundle(inms=[inm(), con(inm, id="i9", identifier=[{"value": "VX-99", "type": cc("0203", "FILL")}])]),
        "recurso_duplicado": bundle(extra=[con(pac, id="p2", identifier=[{"value": "OTRO"}])]),
        "referencia_rota": con_inm(patient={"reference": "urn:uuid:nadie"}),
        "fhir_invalido": con_inm(status="hecho"),
    }
    for sub, b in casos.items():
        subs = {s for h in juzga(b=b)["hallazgos"] if h["cuenta"] for s in h["subtipo"].split("+")}
        mira("clase %s" % sub, sub in subs, True)
    b = bundle()
    b["entry"] = b["entry"][::-1]
    for x in b["entry"]:
        x["resource"]["meta"] = {"versionId": "1"}
    mira("forma: orden y meta", sh(juzga(b=b)), [])


def p20():
    import mcp_verificador as M
    import conversion as CV
    mira("punto en el esquema", "vxu_conv" in M.E_PROPS["punto_entrada"]["enum"], True)
    a = dict(ev_vxu(msg(), texto(bundle())), caso="p-vx-20")
    out = M.t_verificar(a)[0]
    mira("MCP verificar_caso", (out["veredicto"]["categoria"], any("conversión" in x for x in out["entrada"]["no_evaluado"])), ("correcto", True))
    esq = next(h for h in M.HERRAMIENTAS if h["name"] == "verificar_caso")["inputSchema"]
    M.validar(a, esq)
    t = M.t_tabla({"tabla": "perfil_guia_vxu"})[0]
    mira("perfil_guia_vxu con nivel y citas", bool(t["entradas"]) and all("nivel" in f and f.get("citas") for f in t["entradas"]), True)
    info = M.t_info({})[0]
    mira("info declara vxu_conv", ("vxu_conv" in info["puntos_entrada"], "vxu" in info["conversores"]), (True, True))
    mira("control: perfil_guia_adt y _oru sin cambios", (len(CV.PERFIL_GUIA_ADT), len(CV.PERFIL_GUIA_ORU)), (21, 16))


def p21():
    import verificar_conversor as VC
    import conversor_juguete as JG
    mira("punto de VXU", VC.punto(msg()), "vxu_conv")
    from prueba_conversion import msg as msg_adt, oru_msg
    mira("control ADT y ORU", (VC.punto(msg_adt()), VC.punto(oru_msg()), VC.punto(msg_adt(msh9="SIU^S12^SIU_S12"))),
         ("adt_conv", "oru_conv", "adt_conv"))
    d = os.path.join(os.environ.get("TMPDIR", "/tmp"), "prueba_vxu_corpus")
    with redirect_stdout(io.StringIO()):
        co = VC.generar_corpus(d, lab=True, minimos=False)
    mira("corpus vxu", co["n"].get("vxu"), 40)
    mira("control: adt y oru como hoy", (co["n"]["adt"], co["n"]["oru"], co["por_corpus"]["adt"][:12], co["por_corpus"]["oru"][:12],
                                          co["huella_adt_oru_muestras"][:12]),
         (263, 40, "7b4e7cfba041", "b5be5675b204", "f2321d41fe7e"))                   # medidos el 25-oct con el juez ee7e5379, antes de VXU
    mira("puntos del corpus vxu", {x["punto"] for x in co["casos"] if x["corpus"] == "vxu"}, {"vxu_conv"})
    m = msg(msh={8: "JUGUETE-NOMINAL"})
    acc, b = JG.convertir(m)
    r = j(ev_vxu(m, b))
    mira("juguete nominal VXU", (acc, cat(r), sh(r)), ("bundle", ("correcto", None), []))
    m = msg(msh={8: "JUGUETE-RUTA"})
    r = j(ev_vxu(m, JG.convertir(m)[1]))
    mira("control JUGUETE-RUTA", (cat(r), sh(r)), (("fallo_silencioso", "convertido"), [("codigo_mal_mapeado", "RXR-1")]))


def p22():
    """ADT y ORU no cambian: el rejuicio de vx/rejuicio_vx.py, con las evidencias privadas del estudio si están."""
    import re
    import subprocess
    mira("vxu_conv presente (sin él, el rejuicio no prueba nada)", "vxu_conv" in PE.PUNTOS, True)
    base = os.path.join(AQUI, "..", "privado", "vx", "rejuicio", "linea_base.jsonl")
    ev_ = [os.path.join(AQUI, "..", "privado", "cv", x) for x in ("cv2/ev", "cv3/ev-minimos", "cv3/ev-minimos-main")]
    if not os.path.exists(base):
        mira("rejuicio: sin evidencias privadas (copia pública)", True, True)
        return
    r = subprocess.run([sys.executable, os.path.join(AQUI, "vx", "rejuicio_vx.py"), "comparar", base] + ev_, capture_output=True, text=True)
    mira("rejuicio sin diferencias", (r.returncode, bool(re.search(r"evidencias, 0 diferencias, 0 de la línea base", r.stdout))), (0, True))


def p23():
    import bases_vxu as BV
    mira("40 bases", [b["id"] for b in BV.BASES], ["B%02d" % k for k in range(1, 41)])
    with redirect_stdout(io.StringIO()):
        ok = BV.autoprueba()
    mira("autoprueba del corpus", ok, True)
    bases = copy.deepcopy(BV.BASES)
    otra = copy.deepcopy(bases[0])
    otra["id"] = "B99"
    otra["segmentos"] = [s.replace("LOT-B01", "LOT-B99") for s in otra["segmentos"]]
    mira("control: una copia con un campo distinto rompe la firma", bool(BV.firma(bases + [otra])), True)


PRUEBAS = [p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23]


def main():
    rojo = sys.argv[1:] == ["rojo"]
    for p in PRUEBAS:
        grupo[0] = "P-VX-%d" % int(p.__name__[1:])
        try:
            p()
        except Exception as ex:                                             # en rojo, lo esperado es que el PE no exista
            FALLAN.add(grupo[0])
            if not rojo:
                print("  EXCEPCIÓN %s: %s" % (grupo[0], "".join(traceback.format_exception_only(type(ex), ex)).strip()[:300]))
                mal.append(grupo[0])
    if rojo:
        print("PRUEBAS VXU (rojo): fallan %d de %d %s" % (len(FALLAN), len(PRUEBAS), "(TODAS)" if len(FALLAN) == len(PRUEBAS) else ""))
        return 0 if len(FALLAN) == len(PRUEBAS) else 1
    print("PRUEBAS VXU: %s (%d comprobaciones, %d pruebas)" % ("TODO BIEN" if not mal else "%d MAL" % len(mal), n_ok[0], len(PRUEBAS)))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
