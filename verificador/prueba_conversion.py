#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CV1-b (cv/diseno-conversores-fable.md §6): P-CV-1..18, el juez ante la salida de un conversor de terceros, con evidencia
sintética. Los Bundles se escriben a mano (no salen del perfil «guía»: un fallo de la proyección no se confirmaría a sí mismo),
cada prueba muta una sola cosa y lleva su control negativo. Las decisiones de Jev (cv/decisiones-qcv.md) mandan: Q-CV-D-6
(PV1-2 = N sin Encounter cuenta) y Q-CV-D-9 (family solo FN.1) van contra la recomendación de Fable.

Antes del código (sin conversion.py ni los PE adt_conv/oru_conv) fallan todas: PE.resolver no conoce el punto.
  python3 prueba_conversion.py          -> TODO BIEN si no hay ningún MAL
  python3 prueba_conversion.py rojo     -> sale 0 solo si fallan las 18 (el rojo de CV1-b)"""
import json
import sys
import traceback

import verificador as V

mal, n_ok, grupo = [], [0], [None]
FALLAN = set()


def mira(nombre, obtenido, esperado):
    if obtenido == esperado:
        n_ok[0] += 1
    else:
        print("  MAL %s %s: %r != %r" % (grupo[0], nombre, obtenido, esperado))
        mal.append(nombre)
        FALLAN.add(grupo[0])


# ---------------------------------------------------------------------------- el mensaje
ESTRUCTURA = {"A01": "ADT_A01", "A02": "ADT_A02", "A03": "ADT_A03", "A04": "ADT_A01", "A05": "ADT_A05", "A08": "ADT_A01",
              "A11": "ADT_A09", "A13": "ADT_A01", "A31": "ADT_A05"}


def seg(nombre, campos):
    """Un segmento desde {número de campo: valor}. En MSH, MSH-1 es el separador y MSH-k va en la posición k-1."""
    n = max(campos) if campos else 1
    if nombre == "MSH":
        p = ["MSH", "^~\\&"] + [""] * max(n - 2, 0)
        for k, v in campos.items():
            p[k - 1] = v
    else:
        p = [nombre] + [""] * n
        for k, v in campos.items():
            p[k] = v
    return "|".join(p)


def xtn(**c):
    """XTN por componentes con nombre: c1 (número antiguo), uso (2), equipo (3), correo (4), pais (5), area (6), local (7), sin (12)."""
    nombres = {"c1": 1, "uso": 2, "equipo": 3, "correo": 4, "pais": 5, "area": 6, "local": 7, "sin": 12}
    p = [""] * 12
    for k, v in c.items():
        p[nombres[k] - 1] = v
    while p and not p[-1]:
        p.pop()
    return "^".join(p)


MSH = {3: "APP", 4: "FAC", 5: "LAB", 6: "LAB", 7: "20260101120000", 10: "M1", 11: "P", 12: "2.5"}
PID = {1: "1", 3: "X1^^^H^MR", 5: "Pérez^Ana^Luz^^^^L", 7: "19800215", 8: "F", 11: "C/ Mayor 1^^Madrid^M^28001^ES^H",
       13: xtn(uso="PRN", equipo="PH", sin="+34600111222"), 16: "M"}
PV1 = {1: "1", 2: "I", 3: "URG^101^A^HOSP", 4: "E", 7: "123^García^Luis^^^Dr", 10: "MED", 14: "7", 19: "V1", 36: "01",
       44: "20260101100000+0100"}


def msg(ev="A01", msh=None, pid=None, pv1=None, msh9=None, sin_pv1=False):
    """ADT del punto adt_conv. Los diccionarios sustituyen campos; un valor None borra el campo."""
    def junta(base, cambios):
        d = dict(base)
        for k, v in (cambios or {}).items():
            if v is None:
                d.pop(k, None)
            else:
                d[k] = v
        return d
    h = junta(MSH, msh)
    h[9] = msh9 or "ADT^%s^%s" % (ev, ESTRUCTURA[ev])
    segs = [seg("MSH", h), seg("EVN", {1: ev, 2: "20260101120000"}), seg("PID", junta(PID, pid))]
    if not sin_pv1:
        segs.append(seg("PV1", junta(PV1, pv1)))
    return "\r".join(segs)


# ---------------------------------------------------------------------------- el Bundle (a mano)
S = {"0203": "http://terminology.hl7.org/CodeSystem/v2-0203", "act": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
     "0004": "http://terminology.hl7.org/CodeSystem/v2-0004", "mar": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
     "nul": "http://terminology.hl7.org/CodeSystem/v3-NullFlavor", "0007": "http://terminology.hl7.org/CodeSystem/v2-0007",
     "sty": "http://terminology.hl7.org/CodeSystem/service-type", "0069": "http://terminology.hl7.org/CodeSystem/v2-0069",
     "par": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType", "loinc": "http://loinc.org",
     "ucum": "http://unitsofmeasure.org", "int": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
     "0078": "http://terminology.hl7.org/CodeSystem/v2-0078"}


def cc(sistema, codigo):
    return {"coding": [{"system": S.get(sistema, sistema), "code": codigo}]}


def pac():
    return {"resourceType": "Patient", "id": "p1",
            "identifier": [{"value": "X1", "type": cc("0203", "MR"), "assigner": {"display": "H"}}],
            "name": [{"family": "Pérez", "given": ["Ana", "Luz"], "use": "official"}],
            "birthDate": "1980-02-15", "gender": "female",
            "address": [{"line": ["C/ Mayor 1"], "city": "Madrid", "state": "M", "postalCode": "28001", "country": "ES", "use": "home"}],
            "telecom": [{"system": "phone", "value": "+34600111222", "use": "home"}],
            "maritalStatus": cc("mar", "M")}


def enc():
    return {"resourceType": "Encounter", "id": "e1", "identifier": [{"value": "V1"}], "status": "in-progress",
            "class": {"system": S["act"], "code": "IMP"}, "type": [cc("0007", "E")], "serviceType": cc("sty", "382"),
            "subject": {"reference": "urn:uuid:p1"},
            "participant": [{"type": [cc("par", "ATND")], "individual": {"reference": "urn:uuid:pr1"}}],
            "period": {"start": "2026-01-01T10:00:00+01:00"},
            "location": [{"location": {"reference": "urn:uuid:l1"}, "status": "active"}],
            "hospitalization": {"admitSource": {"coding": [{"code": "7"}]}, "dischargeDisposition": {"coding": [{"code": "01"}]}}}


def prac(i="pr1", ident="123", family="García", given=("Luis",), prefix=("Dr",)):
    r = {"resourceType": "Practitioner", "id": i, "identifier": [{"value": ident}], "name": [{"family": family, "given": list(given)}]}
    if prefix:
        r["name"][0]["prefix"] = list(prefix)
    return r


def locs(valores=("A", "101", "URG", "HOSP"), pref="l"):
    """Cadena de Location de la más granular a la menos, por partOf (la guía reparte PL en hasta 6 Location)."""
    out = []
    for k, v in enumerate(valores, 1):
        r = {"resourceType": "Location", "id": "%s%d" % (pref, k), "identifier": [{"value": v}]}
        if k < len(valores):
            r["partOf"] = {"reference": "urn:uuid:%s%d" % (pref, k + 1)}
        out.append(r)
    return out


def adt_bundle(p=None, e=None, extra=(), sin=()):
    rs = [p or pac(), e or enc(), prac()] + locs() + list(extra)
    return {"resourceType": "Bundle", "type": "batch",
            "entry": [{"fullUrl": "urn:uuid:" + r["id"], "resource": r} for r in rs if r["resourceType"] not in sin]}


def num(t):
    return "@NUM:%s@" % t


def texto(b):
    """JSON del Bundle; num("1.20") queda como el número 1.20 tal cual (el juez lee el Bundle como texto)."""
    s = json.dumps(b, ensure_ascii=False)
    import re
    return re.sub(r'"@NUM:([^@]*)@"', r"\1", s)


def ev(m, b=None, estado="bundle", error=None, pe="adt_conv"):
    salida = {"estado": estado}
    if b is not None:
        salida["bundle"] = b if isinstance(b, str) else texto(b)
    if error is not None:
        salida["error"] = error
    return {"punto_entrada": pe, "mensaje": m,
            "conversion": {"conversor": {"nombre": "prueba", "version": "0", "huella": "0" * 64}, "salida": salida, "perfil_valor": "guia"}}


def j(e):
    return V.verificar(e)


def cat(r):
    return (r["veredicto"]["categoria"], r["veredicto"].get("subtipo"))


def cuentan(r):
    return sorted((h["clase"], h["subtipo"], h["hecho"]) for h in r["hallazgos"] if h["cuenta"])


def subtipos(r, cuenta=True):
    return sorted({s for h in r["hallazgos"] if h["cuenta"] == cuenta for s in h["subtipo"].split("+")})


def notas(r):
    return sorted({s for h in r["hallazgos"] if not h["cuenta"] for s in (h["subtipo"] or "").split("+")})


def con(base, **k):
    d = base()
    d.update(k)
    return d


def sin_clave(d, *ks):
    for k in ks:
        d.pop(k, None)
    return d


# ---------------------------------------------------------------------------- P-CV-1..18
def p01():
    r = j(ev(msg(), adt_bundle()))
    mira("nominal", (cat(r), cuentan(r)), (("correcto", None), []))
    mira("recuentos", r["conversion"]["recuentos"], {"Patient": 1, "Encounter": 1})
    r = j(ev(msg(), adt_bundle(p=con(pac, gender="male"))))
    mira("control gender", (cat(r), cuentan(r)), (("fallo_silencioso", "convertido"), [("fidelidad", "valor_distinto", "PID-8")]))


def p02():
    r = j(ev(msg(), estado="error", error={"codigo": "1", "texto": "fallo"}))
    mira("error con A01 válido", (cat(r), cuentan(r)), (("rechazo_incorrecto", "error"), [("rechazo", "incorrecto", "MSH-9")]))
    r = j(ev(msg("A05"), estado="error", error={"codigo": "1", "texto": "fallo"}))
    mira("control A05", (cat(r), cuentan(r)), (("fuera_de_alcance", None), []))
    r = j(ev(msg(pid={7: "19801301"}), estado="error", error={"codigo": "1", "texto": "fecha"}))
    mira("control PID-7 imposible", (cat(r), cuentan(r), "aceptable" in notas(r)), (("correcto", None), [], True))


def p03():
    mira("no json", cat(j(ev(msg(), "no json"))), ("indeterminado", "lectura"))
    mira("vacío", cat(j(ev(msg(), estado="vacio"))), ("indeterminado", "sin_salida"))
    mira("control válido", cat(j(ev(msg(), adt_bundle())))[0] != "indeterminado", True)


def p04():
    import conversion as CV
    extra = [{"resourceType": "MessageHeader", "id": "mh"}, {"resourceType": "Provenance", "id": "pv"}]
    b = texto(adt_bundle(extra=extra))
    lec = CV.leer_y_emparejar(V.MR.mensajes(msg())[0], b, "adt")
    roles = {x["rol"]: x["emparejado_por"] for x in lec["recursos"]}
    mira("roles", (roles.get("Patient#1"), roles.get("Encounter#1")), ("unico", "unico"))
    mira("otros_tipos", lec["otros_tipos"], {"MessageHeader": 1, "Provenance": 1})
    mira("sin cuenta", cuentan(j(ev(msg(), adt_bundle(extra=extra)))), [])
    r = j(ev(msg(), adt_bundle(e=con(enc, subject={"reference": "urn:uuid:nada"}))))
    mira("control subject roto", ("fidelidad", "referencia_rota", "PID-3") in cuentan(r), True)
    r = j(ev(msg(), adt_bundle(e=con(enc, subject={"identifier": {"value": "X1"}}))))
    mira("control subject lógico", cuentan(r), [])


def p05():
    otro = con(pac, id="p2", identifier=[{"value": "X9"}])
    r = j(ev(msg(), adt_bundle(extra=[otro])))
    import conversion as CV
    lec = CV.leer_y_emparejar(V.MR.mensajes(msg())[0], texto(adt_bundle(extra=[otro])), "adt")
    mira("por identifier", {x["rol"]: x["emparejado_por"] for x in lec["recursos"]}.get("Patient#1"), "identifier")
    mira("duplicado", ("fidelidad", "recurso_duplicado", "PID") in cuentan(r), True)
    lec = CV.leer_y_emparejar(V.MR.mensajes(msg())[0], texto(adt_bundle()), "adt")
    mira("control uno", {x["rol"]: x["emparejado_por"] for x in lec["recursos"]}.get("Patient#1"), "unico")


# --- ORU
def oru_msg(obr=None, obx=None, dos=False, pid=None):
    o = {1: "1", 2: "PL1", 3: "FL1", 4: "A^Panel A^LN", 7: "20260101080000+0100", 8: "20260101090000+0100",
         22: "20260101100000+0100", 25: "F"}
    o.update(obr or {})
    x1 = {1: "1", 2: "NM", 3: "2345-7^Glucosa^LN", 5: "1.20", 6: "mg/dL^mg/dL^UCUM", 7: "0.5-1.5", 8: "H", 11: "F",
          14: "20260101080000+0100"}
    x1.update(obx or {})
    x2 = {1: "2", 2: "ST", 3: "8251-1^Comentario^LN", 5: "texto", 11: "F"}
    h = dict(MSH)
    h[9] = "ORU^R01^ORU_R01"
    p = dict(PID)
    p.update(pid or {})
    segs = [seg("MSH", h), seg("PID", {k: v for k, v in p.items() if k in (1, 3, 5, 7, 8)}), seg("OBR", o), seg("OBX", x1),
            seg("OBX", x2)]
    if dos:
        segs = segs[:2] + [seg("OBR", {1: "1", 2: "PA", 3: "FA", 4: "A^Panel A^LN", 7: "20260101080000+0100", 25: "F"}),
                           seg("OBX", {1: "1", 2: "ST", 3: "C11^c11^LN", 5: "a", 11: "F"}), seg("OBX", {1: "2", 2: "ST", 3: "C12^c12^LN", 5: "b", 11: "F"}),
                           seg("OBR", {1: "2", 2: "PB", 3: "FB", 4: "B^Panel B^LN", 7: "20260101080000+0100", 25: "F"}),
                           seg("OBX", {1: "1", 2: "ST", 3: "C21^c21^LN", 5: "c", 11: "F"}), seg("OBX", {1: "2", 2: "ST", 3: "C22^c22^LN", 5: "d", 11: "F"})]
    return "\r".join(segs)


def pac_oru():
    return {"resourceType": "Patient", "id": "p1", "identifier": [{"value": "X1", "type": cc("0203", "MR"), "assigner": {"display": "H"}}],
            "name": [{"family": "Pérez", "given": ["Ana", "Luz"], "use": "official"}], "birthDate": "1980-02-15", "gender": "female"}


def obs1():
    return {"resourceType": "Observation", "id": "o1", "status": "final", "code": cc("loinc", "2345-7"), "subject": {"reference": "urn:uuid:p1"},
            "effectiveDateTime": "2026-01-01T08:00:00+01:00",
            "valueQuantity": {"value": num("1.20"), "unit": "mg/dL", "system": S["ucum"], "code": "mg/dL"},
            "interpretation": [cc("int", "H")], "referenceRange": [{"text": "0.5-1.5"}]}


def obs2():
    return {"resourceType": "Observation", "id": "o2", "status": "final", "code": cc("loinc", "8251-1"), "subject": {"reference": "urn:uuid:p1"},
            "valueString": "texto"}


def dr():
    return {"resourceType": "DiagnosticReport", "id": "d1",
            "identifier": [{"value": "PL1", "type": cc("0203", "PLAC")}, {"value": "FL1", "type": cc("0203", "FILL")}],
            "status": "final", "code": cc("loinc", "A"), "subject": {"reference": "urn:uuid:p1"},
            "effectivePeriod": {"start": "2026-01-01T08:00:00+01:00", "end": "2026-01-01T09:00:00+01:00"},
            "issued": "2026-01-01T10:00:00+01:00", "result": [{"reference": "urn:uuid:o1"}, {"reference": "urn:uuid:o2"}]}


def oru_bundle(rs=None):
    rs = rs or [pac_oru(), dr(), obs1(), obs2()]
    return {"resourceType": "Bundle", "type": "collection", "entry": [{"fullUrl": "urn:uuid:" + r["id"], "resource": r} for r in rs]}


def oru_dos(cruzar=False, invertir=False, sobrante=True):
    def o(i, code, v):
        return {"resourceType": "Observation", "id": i, "status": "final", "code": cc("loinc", code), "subject": {"reference": "urn:uuid:p1"},
                "valueString": v}
    def d(i, code, plac, fill, res):
        return {"resourceType": "DiagnosticReport", "id": i, "identifier": [{"value": plac, "type": cc("0203", "PLAC")},
                {"value": fill, "type": cc("0203", "FILL")}], "status": "final", "code": cc("loinc", code),
                "subject": {"reference": "urn:uuid:p1"}, "effectiveDateTime": "2026-01-01T08:00:00+01:00",
                "result": [{"reference": "urn:uuid:" + x} for x in res]}
    r1, r2 = ["o11", "o12"], ["o21", "o22"]
    if cruzar:
        r1, r2 = ["o21", "o12"], ["o11", "o22"]
    if invertir:
        r1, r2 = r1[::-1], r2[::-1]
    rs = [pac_oru(), d("dA", "A", "PA", "FA", r1), d("dB", "B", "PB", "FB", r2), o("o11", "C11", "a"), o("o12", "C12", "b"),
          o("o21", "C21", "c"), o("o22", "C22", "d")]
    if sobrante:
        rs.append(o("o99", "C99", "z"))
    return oru_bundle(rs)


def p06():
    import conversion as CV
    m = V.MR.mensajes(oru_msg(dos=True))[0]
    lec = CV.leer_y_emparejar(m, texto(oru_dos()), "oru")
    roles = {x["rol"]: x["emparejado_por"] for x in lec["recursos"]}
    mira("roles ORU", [roles.get(k) for k in ("Observation#1.1", "Observation#1.2", "Observation#2.1", "Observation#2.2")],
         ["referencia"] * 4)
    r = j(ev(oru_msg(dos=True), oru_dos(), pe="oru_conv"))
    mira("sobrante", ("fidelidad", "recurso_inventado", "OBX") in cuentan(r), True)
    r = j(ev(oru_msg(dos=True), oru_dos(cruzar=True, sobrante=False), pe="oru_conv"))
    mira("control cruzado", sum(1 for h in cuentan(r) if h[1] == "referencia_rota") >= 2, True)
    r = j(ev(oru_msg(dos=True), oru_dos(invertir=True, sobrante=False), pe="oru_conv"))
    mira("control orden", cuentan(r), [])


def p07():
    m = msg(pid={3: "X1^^^H&1.2&ISO^MR~X2^^^H^PI"})
    ids = [{"value": "X1", "type": cc("0203", "MR"), "assigner": {"display": "H"}}, {"value": "X2", "type": cc("0203", "PI"), "system": "urn:oid:H"}]
    mira("dos CX", cuentan(j(ev(m, adt_bundle(p=con(pac, identifier=ids))))), [])
    mira("control falta X2", cuentan(j(ev(m, adt_bundle(p=con(pac, identifier=ids[:1]))))), [("fidelidad", "dato_perdido", "PID-3")])
    malo = [dict(ids[0], type=cc("0203", "PI")), ids[1]]
    mira("control type", cuentan(j(ev(m, adt_bundle(p=con(pac, identifier=malo))))), [("fidelidad", "valor_distinto", "PID-3")])


def p08():
    m = msg(pid={5: "de la&Cruz^Luis Miguel^José^Jr^Dr^^L~Pérez^Ana^^^^^B"})
    n1 = {"family": "de la", "given": ["Luis Miguel", "José"], "suffix": ["Jr"], "prefix": ["Dr"], "use": "official"}
    n2 = {"family": "Pérez", "given": ["Ana"]}
    mira("dos XPN", cuentan(j(ev(m, adt_bundle(p=con(pac, name=[n1, n2]))))), [])
    mira("Q-CV-D-9 FN unido", cuentan(j(ev(m, adt_bundle(p=con(pac, name=[dict(n1, family="de la Cruz"), n2]))))),
         [("fidelidad", "valor_distinto", "PID-5")])
    mira("control use", cuentan(j(ev(m, adt_bundle(p=con(pac, name=[n1, dict(n2, use="official")]))))),
         [("fidelidad", "codigo_mal_mapeado", "PID-5")])
    mira("control given", cuentan(j(ev(m, adt_bundle(p=con(pac, name=[dict(n1, given=["Luis", "Miguel", "José"]), n2]))))),
         [("fidelidad", "valor_distinto", "PID-5")])


def p09():
    m = msg(pid={11: "C/ A 1&2º&B^Esc 3^Madrid^M^28001^ES^H",
                 13: "%s~%s" % (xtn(uso="PRN", equipo="PH", sin="+34 600"), xtn(equipo="Internet", correo="a@b.c"))})
    ad = {"line": ["C/ A 1", "2º", "B", "Esc 3"], "city": "Madrid", "state": "M", "postalCode": "28001", "country": "ES", "use": "home"}
    te = [{"system": "phone", "value": "+34 600", "use": "home"}, {"system": "email", "value": "a@b.c", "use": "home"}]
    mira("XAD y XTN", cuentan(j(ev(m, adt_bundle(p=con(pac, address=[ad], telecom=te))))), [])
    mira("control line", cuentan(j(ev(m, adt_bundle(p=con(pac, address=[dict(ad, line=["Esc 3", "C/ A 1", "2º", "B"])], telecom=te))))),
         [("fidelidad", "valor_distinto", "PID-11")])
    mira("control falta teléfono", cuentan(j(ev(m, adt_bundle(p=con(pac, address=[ad], telecom=te[1:]))))),
         [("fidelidad", "dato_perdido", "PID-13")])
    mira("control email phone", cuentan(j(ev(m, adt_bundle(p=con(pac, address=[ad], telecom=[te[0], dict(te[1], system="phone")]))))),
         [("fidelidad", "codigo_mal_mapeado", "PID-13")])


def p10():
    m = msg(pv1={3: "URG^101^A^HOSP^^^^^Box 1"})
    ls = locs()
    ls[0]["description"] = "Box 1"
    b = adt_bundle()
    b["entry"] = [x for x in b["entry"] if x["resource"]["resourceType"] != "Location"] + \
        [{"fullUrl": "urn:uuid:" + r["id"], "resource": r} for r in ls]
    mira("PL nominal", cuentan(j(ev(m, b))), [])
    solo = adt_bundle(sin=("Location",), extra=[{"resourceType": "Location", "id": "l1", "identifier": [{"value": "URG"}], "description": "Box 1"}])
    mira("control un Location", cuentan(j(ev(m, solo))), [("fidelidad", "dato_perdido", "PV1-3")])
    m6 = msg(pv1={6: "URG^102^B^HOSP"})
    e6 = enc()
    e6["location"].append({"location": {"reference": "urn:uuid:m1"}, "status": "active"})
    b6 = adt_bundle(e=e6, extra=locs(("B", "102", "URG", "HOSP"), "m"))
    mira("control PV1-6 active", cuentan(j(ev(m6, b6))), [("fidelidad", "valor_distinto", "PV1-6")])


def p11():
    m = msg(pv1={8: "456^Ruiz^Ana"})
    e = enc()
    e["participant"].append({"type": [cc("par", "REF")], "individual": {"reference": "urn:uuid:pr2"}})
    extra = [prac("pr2", "456", "Ruiz", ("Ana",), ())]
    mira("XCN", cuentan(j(ev(m, adt_bundle(e=e, extra=extra)))), [])
    e2 = enc()
    e2["participant"] = [{"type": [cc("par", "REF")], "individual": {"reference": "urn:uuid:pr1"}},
                         {"type": [cc("par", "REF")], "individual": {"reference": "urn:uuid:pr2"}}]
    mira("control tipo", cuentan(j(ev(m, adt_bundle(e=e2, extra=extra)))), [("fidelidad", "codigo_mal_mapeado", "PV1-7")])
    e3 = enc()
    e3["participant"] = [{"type": [cc("par", "ATND")], "individual": {"display": "García"}}, e["participant"][1]]
    mira("control solo display", cuentan(j(ev(m, adt_bundle(e=e3, extra=extra)))), [("fidelidad", "dato_perdido", "PV1-7")])


def p12():
    m = msg(pid={8: "A", 16: "G"}, pv1={2: "O", 10: "MED"})
    e = con(enc, **{"class": {"system": S["act"], "code": "AMB"}})
    mira("vocabularios", cuentan(j(ev(m, adt_bundle(p=con(pac, gender="other", maritalStatus=cc("mar", "T")), e=e)))), [])
    m2 = msg(pid={16: "U"}, pv1={2: "R", 10: "SUR"})
    e2 = con(enc, **{"class": {"system": S["0004"], "code": "R"}, "serviceType": cc("0069", "SUR")})
    mira("vocabularios 2", cuentan(j(ev(m2, adt_bundle(p=con(pac, maritalStatus=cc("nul", "UNK")), e=e2)))), [])
    mira("control class", cuentan(j(ev(m, adt_bundle(p=con(pac, gender="other", maritalStatus=cc("mar", "T")),
                                                     e=con(enc, **{"class": {"system": S["0004"], "code": "O"}}))))),
         [("fidelidad", "codigo_mal_mapeado", "PV1-2")])
    mira("control serviceType", cuentan(j(ev(msg(), adt_bundle(e=con(enc, serviceType=cc("0069", "MED")))))),
         [("fidelidad", "codigo_mal_mapeado", "PV1-10")])
    mira("Q-CV-D-3 unknown", cuentan(j(ev(msg(pid={8: None}), adt_bundle(p=con(pac, gender="unknown"))))),
         [("fidelidad", "dato_inventado", "PID-8")])
    r = j(ev(msg(pid={8: "X"}), adt_bundle(p=con(pac, gender="X"))))
    h8 = [h for h in r["hallazgos"] if h["cuenta"] and h["hecho"] == "PID-8"]
    mira("control X fusionado", (len(h8), set(h8[0]["subtipo"].split("+")) if h8 else None),      # etapa 37: la 0001 es user-defined
         (1, {"fhir_invalido"}))
    mira("J2 minúscula literal", cuentan(j(ev(msg(pid={8: "f"}), adt_bundle(p=con(pac, gender="f"))))),       # CV2 rep. 1
         [("fidelidad", "fhir_invalido", "PID-8")])


def p13():
    for ev_, st in (("A03", "in-progress"), ("A03", "finished"), ("A11", "cancelled"), ("A08", "unknown")):
        mira("status %s %s" % (ev_, st), cuentan(j(ev(msg(ev_), adt_bundle(e=con(enc, status=st))))), [])
    mira("control A11 in-progress", cuentan(j(ev(msg("A11"), adt_bundle(e=con(enc, status="in-progress"))))),
         [("fidelidad", "valor_distinto", "MSH-9")])
    mira("control A01 finished", cuentan(j(ev(msg(), adt_bundle(e=con(enc, status="finished"))))),
         [("fidelidad", "dato_inventado", "PV1-45")])


def p14():
    r = j(ev(oru_msg(), oru_bundle(), pe="oru_conv"))
    mira("ORU nominal", (cat(r), cuentan(r)), (("correcto", None), []))
    o = obs1()
    o["valueQuantity"]["value"] = num("1.2")
    mira("control 1.2", cuentan(j(ev(oru_msg(), oru_bundle([pac_oru(), dr(), o, obs2()]), pe="oru_conv"))),
         [("fidelidad", "valor_distinto", "OBX-5")])
    o = con(obs1, interpretation=[cc("0078", "H")])
    mira("control interpretation", cuentan(j(ev(oru_msg(), oru_bundle([pac_oru(), dr(), o, obs2()]), pe="oru_conv"))),
         [("fidelidad", "codigo_mal_mapeado", "OBX-8")])
    d = sin_clave(dr(), "effectivePeriod")
    d["effectiveDateTime"] = "2026-01-01T08:00:00+01:00"
    mira("control OBR-8", cuentan(j(ev(oru_msg(), oru_bundle([pac_oru(), d, obs1(), obs2()]), pe="oru_conv"))),
         [("fidelidad", "dato_perdido", "OBR-8")])


def p15():
    import copy
    casos = {
        "valor_distinto": (msg(), adt_bundle(p=con(pac, birthDate="1980-02-16")), "PID-7"),
        "dato_perdido": (msg(), adt_bundle(p=sin_clave(pac(), "address")), "PID-11"),
        "dato_inventado": (msg(), adt_bundle(p=con(pac, deceasedBoolean=False)), "PID-30"),
        "codigo_mal_mapeado": (msg(), adt_bundle(e=con(enc, **{"class": {"system": S["0004"], "code": "I"}})), "PV1-2"),
        "valor_imposible_convertido": (msg(pid={30: "X"}), adt_bundle(p=con(pac, deceasedBoolean=False)), "PID-30"),   # etapa 37
        "recurso_ausente": (msg(), adt_bundle(sin=("Encounter",)), "PV1"),
        "recurso_duplicado": (msg(), adt_bundle(extra=[con(enc, id="e2", identifier=[])]), "PV1"),
        "recurso_inventado": (msg(), adt_bundle(extra=[{"resourceType": "Observation", "id": "ox", "status": "final", "code": cc("loinc", "1")}]), "OBX"),
        "referencia_rota": (msg(), adt_bundle(e=con(enc, participant=[{"type": [cc("par", "ATND")], "individual": {"reference": "urn:uuid:nada"}}])), "PV1-7"),
        "fhir_invalido": (msg(), adt_bundle(p=con(pac, birthDate="1980-02-15T00:00:00")), "PID-7"),
    }
    for sub, (m, b, hecho) in casos.items():
        r = j(ev(m, b))
        cl = "valor_imposible_aceptado" if sub == "valor_imposible_convertido" else "fidelidad"
        mira("subtipo %s" % sub, cuentan(r), [(cl, sub, hecho)])
    b = adt_bundle()
    formas = {}
    x = copy.deepcopy(b); x["entry"].reverse(); formas["orden de entries"] = x
    x = copy.deepcopy(b); x["entry"][0]["resource"]["id"] = "otro"; formas["id"] = x
    x = copy.deepcopy(b); x["entry"][0]["resource"]["meta"] = {"lastUpdated": "2026-01-01T00:00:00Z"}; formas["meta"] = x
    x = copy.deepcopy(b); x["entry"][0]["resource"]["text"] = {"status": "generated", "div": "<div>x</div>"}; formas["text"] = x
    x = copy.deepcopy(b); x["entry"][0]["resource"]["extension"] = [{"url": "http://x", "valueString": "y"}]; formas["extensión"] = x
    x = copy.deepcopy(b); x["entry"][0]["resource"]["maritalStatus"]["coding"][0]["display"] = "Married"; formas["display"] = x
    x = copy.deepcopy(b); x["type"] = "collection"; formas["Bundle.type"] = x
    x = copy.deepcopy(b); x["entry"][1]["resource"]["subject"] = {"identifier": {"value": "X1"}}; formas["subject lógico"] = x
    for nombre, x in formas.items():
        mira("forma %s" % nombre, cuentan(j(ev(msg(), x))), [])


def p16():
    m = msg("A04", msh={12: "2.8"}, pv1={2: "Z"}, msh9="ADT^A04^ADT_A04")
    e = con(enc, **{"class": {"system": S["0004"], "code": "Z"}})
    r = j(ev(m, adt_bundle(e=e)))
    mira("2.8: nada cuenta", cuentan(r), [])
    mira("2.8: notas", {"version", "estructura_declarada"} <= set(notas(r)), True)
    r = j(ev(m, adt_bundle(p=con(pac, gender="male"), e=e)))
    mira("2.8: el mapeo sigue contando", cuentan(r), [("fidelidad", "valor_distinto", "PID-8")])
    r = j(ev(msg(pv1={2: "Z"}), adt_bundle(e=e)))
    mira("control 2.5 PV1-2 fuera de tabla", cuentan(r), [])
    r = j(ev(msg("A04", msh9="ADT^A04^ADT_A04"), adt_bundle()))
    mira("control 2.5 MSH-9.3", (cuentan(r), "estructura_declarada" in notas(r)), ([], True))


def p17():
    def pe44(valor, obs):
        return cuentan(j(ev(msg(pv1={44: valor}), adt_bundle(e=con(enc, period={"start": obs})))))
    mira("instante con zona", pe44("20260101103000+0100", "2026-01-01T09:30:00Z"), [])
    mira("sin zona ni segundos", pe44("202601011030", "2026-01-01T10:30:00+05:00"), [])
    mira("PID-7 año y mes", cuentan(j(ev(msg(pid={7: "198002"}), adt_bundle(p=con(pac, birthDate="1980-02"))))), [])
    mira("control hora cambiada", pe44("20260101103000+0100", "2026-01-01T11:30:00+01:00"), [("fidelidad", "valor_distinto", "PV1-44")])
    mira("control día inventado", cuentan(j(ev(msg(pid={7: "198002"}), adt_bundle(p=con(pac, birthDate="1980-02-01"))))),
         [("fidelidad", "dato_inventado", "PID-7")])
    mira("control sin zona", pe44("202601011030", "2026-01-01T10:30:00"), [("fidelidad", "fhir_invalido", "PV1-44")])


def p18():
    import mcp_verificador as M
    a = dict(ev(msg(), adt_bundle()), caso="p18")
    out = M.t_verificar(a)[0]
    mira("MCP verificar_caso", (out["veredicto"]["categoria"], any("conversión" in x for x in out["entrada"]["no_evaluado"])),
         ("correcto", True))
    t = M.t_tabla({"tabla": "perfil_guia_adt"})[0]                       # t_tabla devuelve «entradas» (interfaz de siempre)
    mira("MCP perfil_guia_adt", bool(t["entradas"]) and all("nivel" in f and f.get("citas") for f in t["entradas"]), True)
    esq = next(h for h in M.HERRAMIENTAS if h["name"] == "verificar_caso")["inputSchema"]
    M.validar(a, esq)                                                    # el caso nominal pasa el esquema
    grande = dict(ev(msg(), "x" * 4000001), caso="p18b")                 # DV-CV-5: tope 4 MB (un Bundle real de una muestra: 161 KB)
    try:
        M.validar(grande, esq)
        mira("control maxLength", "sin error", "error")
    except Exception as ex:
        mira("control maxLength", type(ex).__name__, "ErrorEntrada")


# ---------------------------------------------------------------------------- CV2, repetición 1: defectos del juez adjudicados
def p19():
    """J1: PID-12 County Code -> address[1].district si PID-11 no repite y XAD.9 vacío (PID_Patient.csv:18)."""
    m = msg(pid={12: "02"})
    ad = con(pac)["address"][0]
    mira("district desde PID-12", cuentan(j(ev(m, adt_bundle(p=con(pac, address=[dict(ad, district="02")]))))), [])
    mira("control falta district", cuentan(j(ev(m, adt_bundle()))), [("fidelidad", "dato_perdido", "PID-12")])
    mira("control district sin PID-12", cuentan(j(ev(msg(), adt_bundle(p=con(pac, address=[dict(ad, district="02")]))))),
         [("fidelidad", "dato_inventado", "PID-11")])


def p20():
    """J3: Observation.status y DiagnosticReport.status son 1..1: unmatched o vacío -> cualquier código válido (convención)."""
    o = con(obs1, status="unknown")
    mira("OBX-11 R unmatched", cuentan(j(ev(oru_msg(obx={11: "R"}), oru_bundle([pac_oru(), dr(), o, obs2()]), pe="oru_conv"))), [])
    d = con(dr, status="unknown")
    mira("OBR-25 vacío", cuentan(j(ev(oru_msg(obr={25: ""}), oru_bundle([pac_oru(), d, obs1(), obs2()]), pe="oru_conv"))), [])
    o = con(obs1, status="bogus")
    mira("control status inválido", cuentan(j(ev(oru_msg(obx={11: "R"}), oru_bundle([pac_oru(), dr(), o, obs2()]), pe="oru_conv"))),
         [("fidelidad", "fhir_invalido", "OBX-11")])


def p21():
    """J5: OBX-5 repetido -> componentes, varias Observation o concatenación (MSG_ORU_R01.csv:69-73); la primera repetición debe estar."""
    o = sin_clave(obs1(), "valueQuantity")
    o["component"] = [{"code": cc("loinc", "2345-7"), "valueQuantity": {"value": num("1.20"), "unit": "mg/dL", "system": S["ucum"], "code": "mg/dL"}},
                      {"code": cc("loinc", "2345-7"), "valueQuantity": {"value": num("1.30"), "unit": "mg/dL", "system": S["ucum"], "code": "mg/dL"}}]
    mira("NM repetido en componentes", cuentan(j(ev(oru_msg(obx={5: "1.20~1.30"}), oru_bundle([pac_oru(), dr(), o, obs2()]), pe="oru_conv"))), [])
    t = sin_clave(obs2(), "valueString")
    t["component"] = [{"code": cc("loinc", "8251-1"), "valueString": "uno"}, {"code": cc("loinc", "8251-1"), "valueString": "dos"}]
    m = oru_msg().replace("ST|8251-1^Comentario^LN||texto", "TX|8251-1^Comentario^LN||uno~dos")
    mira("TX repetido en componentes", cuentan(j(ev(m, oru_bundle([pac_oru(), dr(), obs1(), t]), pe="oru_conv"))), [])
    mira("control TX sin valor", cuentan(j(ev(m, oru_bundle([pac_oru(), dr(), obs1(), sin_clave(obs2(), "valueString")]), pe="oru_conv"))),
         [("fidelidad", "dato_perdido", "OBX(2)-5")])


# ---------------------------------------------------------------------------- CV3, rejuicio 1: lo que la guía admite (regla 2 de §4.3)
def p22():
    """DV-CV-13: NM «5.» vale 5 con la misma precisión (el punto final no trae decimales; JSON no admite «5.»)."""
    def con_valor(v):
        return con(obs1, valueQuantity=dict(obs1()["valueQuantity"], value=num(v)))
    mira("NM 5. como 5", cuentan(j(ev(oru_msg(obx={5: "5."}), oru_bundle([pac_oru(), dr(), con_valor("5"), obs2()]), pe="oru_conv"))), [])
    mira("NM .5 como 0.5", cuentan(j(ev(oru_msg(obx={5: ".5"}), oru_bundle([pac_oru(), dr(), con_valor("0.5"), obs2()]), pe="oru_conv"))), [])
    mira("control NM .5 como 5", cuentan(j(ev(oru_msg(obx={5: ".5"}), oru_bundle([pac_oru(), dr(), con_valor("5"), obs2()]), pe="oru_conv"))),
         [("fidelidad", "valor_distinto", "OBX-5")])
    mira("control NM 5.0 como 5", cuentan(j(ev(oru_msg(obx={5: "5.0"}), oru_bundle([pac_oru(), dr(), con_valor("5"), obs2()]), pe="oru_conv"))),
         [("fidelidad", "valor_distinto", "OBX-5")])


def p23():
    """DV-CV-14: en FT, «\\.br\\» es «Begin new output line» (CH02.txt:1063): un salto de línea en valueString lo conserva."""
    m = oru_msg().replace("ST|8251-1^Comentario^LN||texto", "FT|8251-1^Comentario^LN||Primera linea\\.br\\Segunda linea")
    def con_texto(t):
        return oru_bundle([pac_oru(), dr(), obs1(), con(obs2, valueString=t)])
    mira("FT .br como salto de línea", cuentan(j(ev(m, con_texto("Primera linea\nSegunda linea"), pe="oru_conv"))), [])
    mira("FT .br literal", cuentan(j(ev(m, con_texto("Primera linea\\.br\\Segunda linea"), pe="oru_conv"))), [])
    mira("control FT sin el salto", cuentan(j(ev(m, con_texto("Primera lineaSegunda linea"), pe="oru_conv"))),
         [("fidelidad", "valor_distinto", "OBX(2)-5")])


# ---------------------------------------------------------------------------- CV3, rejuicio 2: las muestras de los proyectos
def p24():
    """DV-CV-15: PV1-19 lleva el tipo «VN» fijo en la hoja del segmento (PV1_Encounter.csv:43) y CX.5 en el mapa del tipo CX:
    la guía admite los dos."""
    def con_tipo(t):
        return adt_bundle(e=con(enc, identifier=[{"value": "V1", "type": cc("0203", t)}]))
    m = msg(pv1={19: "V1^^^^AM"})
    mira("PV1-19 con CX.5 AM y tipo VN", cuentan(j(ev(m, con_tipo("VN")))), [])
    mira("PV1-19 con CX.5 AM y tipo AM", cuentan(j(ev(m, con_tipo("AM")))), [])
    mira("control PV1-19 con otro tipo", cuentan(j(ev(m, con_tipo("MR")))), [("fidelidad", "valor_distinto", "PV1-19")])


def p25():
    """DV-CV-16: un PL con solo separadores (PV1-6 «^^») no está valorado: no se espera Location."""
    mira("PV1-6 solo separadores", cuentan(j(ev(msg(pv1={6: "^^"}), adt_bundle()))), [])
    mira("control PV1-6 valorado", cuentan(j(ev(msg(pv1={6: "OBS^1^1^HOSP"}), adt_bundle()))), [("fidelidad", "dato_perdido", "PV1-6")])


# ---------------------------------------------------------------------------- CV4: lo que dejó CV3 para el juez no sellado
def p26():
    """CV4 (CV3, M-36 y L-24): el espacio de nombres de CX.4 llega a system transformado («urn:id:NIST_MPI», «…/NIST-MPI»):
    se compara sin espacios ni signos."""
    m = msg(pid={3: "X1^^^NIST MPI^MR"})
    def con_system(s):
        return adt_bundle(p=con(pac, identifier=[{"value": "X1", "type": cc("0203", "MR"), "system": s}]))
    mira("CX.4 en system con guion bajo", cuentan(j(ev(m, con_system("urn:id:NIST_MPI")))), [])
    mira("CX.4 en system con guion", cuentan(j(ev(m, con_system("http://example.com/v2-to-fhir-converter/Identifier/NIST-MPI")))), [])
    mira("control otro system", cuentan(j(ev(m, con_system("urn:id:OTRO")))), [("fidelidad", "dato_perdido", "PID-3")])


def p27():
    """CV4 (Q-CV-D-14, Jev: cuenta): una descripción que contiene PL.9 sin ser PL.9 es valor distinto, no dato perdido."""
    m = msg(pv1={3: "URG^101^A^HOSP^^^^^Box 1"})
    def con_desc(d):
        ls = locs()
        if d:
            ls[0]["description"] = d
        b = adt_bundle()
        b["entry"] = [x for x in b["entry"] if x["resource"]["resourceType"] != "Location"] + \
            [{"fullUrl": "urn:uuid:" + r["id"], "resource": r} for r in ls]
        return b
    mira("descripción que contiene PL.9", cuentan(j(ev(m, con_desc("URG--101--A--HOSP--Box 1")))), [("fidelidad", "valor_distinto", "PV1-3")])
    mira("control descripción PL.9", cuentan(j(ev(m, con_desc("Box 1")))), [])
    mira("control sin descripción", cuentan(j(ev(m, con_desc(None)))), [("fidelidad", "dato_perdido", "PV1-3")])


def p28():
    """CV4 (CV3, M-23): en una ORU sin PID, el subject que apunta fuera del Bundle es referencia rota del PID ausente (hecho
    «PID»), no de PID-3."""
    m = "\r".join(s for s in oru_msg().split("\r") if not s.startswith("PID"))
    b = oru_bundle([dr(), obs1(), obs2()])
    mira("ORU sin PID con subject colgado", sorted({x[2] for x in cuentan(j(ev(m, b, pe="oru_conv")))}), ["PID"])
    mira("control con PID", cuentan(j(ev(oru_msg(), oru_bundle(), pe="oru_conv"))), [])

# ---------------------------------------------------------------------------- etapa 37: las dos conductas de la etapa 36
def p29():
    """Conducta 1 (jz/decision-jev-jz.md, Q-JZ-5 a): PID-8 fuera de la 0001, que es user-defined (Ch03.txt:5032-5044),
    convertido a un código de administrative-gender es convención; a uno que no es de FHIR, solo FHIR inválido; sin gender,
    nada."""
    def pid8(r):
        return sorted((h["clase"], h["subtipo"]) for h in r["hallazgos"] if h["hecho"] == "PID-8")
    for v, g in (("S", "unknown"), ("S", "other"), ("Z", "unknown")):
        r = j(ev(msg(pid={8: v}), adt_bundle(p=con(pac, gender=g))))
        mira("%s a %s: convención" % (v, g), (cat(r), cuentan(r), pid8(r)), (("correcto", None), [], [("nota", "convencion")]))
    r = j(ev(msg(pid={8: "S"}), adt_bundle(p=con(pac, gender="unknown"))))
    h = [x for x in r["hallazgos"] if x["hecho"] == "PID-8"]
    mira("la nota cita la 0001 de v2.5", bool(h) and "[E3 Ch03.txt:5032-5044]" in h[0]["citas"], True)
    r = j(ev(msg(pid={8: "S"}), adt_bundle(p=con(pac, gender="S"))))
    mira("S a S: solo FHIR inválido", (cat(r), cuentan(r)), (("fallo_silencioso", "convertido"), [("fidelidad", "fhir_invalido", "PID-8")]))
    r = j(ev(msg(pid={8: "S"}), adt_bundle(p=sin_clave(pac(), "gender"))))
    mira("S sin gender: nada (Q-JZ-5)", (cat(r), pid8(r)), (("correcto", None), []))
    r = j(ev(msg(pid={8: "S"}, msh={12: "2.8"}), adt_bundle(p=con(pac, gender="unknown"))))
    mira("2.8, S a unknown: nota version", pid8(r), [("nota", "version")])
    r = j(ev(msg(pid={8: "S"}), adt_bundle(p=con(pac, gender="unknown", birthDate="1980-02-16"))))
    mira("con otro hallazgo, sin aceptado_imposible", cat(r), ("fallo_silencioso", "convertido"))
    mira("control F a male", cuentan(j(ev(msg(), adt_bundle(p=con(pac, gender="male"))))), [("fidelidad", "valor_distinto", "PID-8")])
    r = j(ev(msg(pid={8: "f"}), adt_bundle(p=con(pac, gender="female"))))
    mira("control f a female (AMB-CV-1)", (cuentan(r), pid8(r)), ([], [("nota", "convencion")]))


CS = "http://example.org/observation-code"
CS0136 = "http://terminology.hl7.org/CodeSystem/v2-0136"
ACC = seg("ACC", {1: "20260102", 3: "Calle Mayor 5", 5: "N", 6: "N", 8: "caida en casa"})
PDA = seg("PDA", {1: "I21^Infarto^I10", 3: "Y", 4: "20260103120000", 6: "Y", 9: "N"})
OBX_ADT = seg("OBX", {1: "1", 2: "NM", 3: "8867-4^Frecuencia^LN", 5: "60", 11: "F", 14: "20260102"})


def obs_acc(i="oa", fecha="2026-01-02", texto_="caida en casa", codigo="injury-incident"):
    return {"resourceType": "Observation", "id": i, "status": "final", "code": cc(CS, codigo), "subject": {"reference": "urn:uuid:p1"},
            "effectiveDateTime": fecha, "valueString": texto_}


def obs_sn(i, codigo, valor):
    return {"resourceType": "Observation", "id": i, "status": "final", "code": cc(CS, codigo), "subject": {"reference": "urn:uuid:p1"},
            "valueCodeableConcept": cc(CS0136, valor)}


def obs_obx(i="ox", fecha="2026-01-02"):
    return {"resourceType": "Observation", "id": i, "status": "final", "code": cc("loinc", "8867-4"), "subject": {"reference": "urn:uuid:p1"},
            "effectiveDateTime": fecha, "valueQuantity": {"value": 60}}


def con_segs(m, *segs):
    return "\r".join([m] + list(segs))


def p30():
    """Conducta 2 (Q-JZ-2 a, Q-JZ-3 d, Q-JZ-4 a): una Observation de un ADT que sale de ACC o de PDA, que la hoja de ADT_A01
    lista sin destino (MSG_ADT_A01.csv:78, 81), cuenta como recurso_sin_mapa con hecho el segmento; se reconoce por un dato
    igual o, si solo lleva un valor de la 0136, por un campo de la 0136 con ese valor. Sin eso, sigue como recurso_inventado."""
    r = j(ev(con_segs(msg(), ACC), adt_bundle(extra=[obs_acc()])))
    mira("ACC por la fecha", cuentan(r), [("fidelidad", "recurso_sin_mapa", "ACC")])
    h = [x for x in r["hallazgos"] if x["hecho"] == "ACC"]
    mira("ACC: cita la hoja, dice el dato y no «sin origen propio»",
         bool(h) and ("[G MSG_ADT_A01.csv:78]" in h[0]["citas"], any("ACC-1" in q for q in h[0]["que"]),
                      any("sin origen propio" in q for q in h[0]["que"])), (True, True, False))
    mira("ACC por el texto", cuentan(j(ev(con_segs(msg(), ACC), adt_bundle(extra=[obs_acc(fecha="2025-05-05")])))),
         [("fidelidad", "recurso_sin_mapa", "ACC")])
    mira("control sin ACC en el mensaje", cuentan(j(ev(msg(), adt_bundle(extra=[obs_acc()])))), [("fidelidad", "recurso_inventado", "OBX")])
    mira("control ACC sin dato común", cuentan(j(ev(con_segs(msg(), ACC), adt_bundle(extra=[obs_acc(fecha="2025-05-05", texto_="otra")])))),
         [("fidelidad", "recurso_inventado", "OBX")])
    tres = [obs_sn("o1", "death-certificate", "Y"), obs_sn("o2", "autopsy", "Y"), obs_sn("o3", "coroner", "N")]
    r = j(ev(con_segs(msg("A02"), PDA), adt_bundle(extra=tres)))
    mira("PDA: tres de solo Y/N, por la 0136", (cuentan(r), cat(r)), ([("fidelidad", "recurso_sin_mapa", "PDA")], ("fallo_silencioso", "convertido")))
    pda_vacio = seg("PDA", {1: "I21^Infarto^I10"})
    mira("control PDA sin campos de la 0136", cuentan(j(ev(con_segs(msg("A02"), pda_vacio), adt_bundle(extra=tres[:1])))),
         [("fidelidad", "recurso_inventado", "OBX")])
    mira("control PDA con la 0136 de otro valor", cuentan(j(ev(con_segs(msg("A02"), seg("PDA", {3: "N", 6: "N", 9: "N"})), adt_bundle(extra=tres[:1])))),
         [("fidelidad", "recurso_inventado", "OBX")])
    for orden, extra in (("ACC primero", [obs_acc(), obs_obx()]), ("OBX primero", [obs_obx(), obs_acc()])):
        r = j(ev(con_segs(msg(), OBX_ADT, ACC), adt_bundle(extra=extra)))
        mira("OBX y ACC, %s" % orden, (cuentan(r), "fuera_proyeccion" in notas(r)), ([("fidelidad", "recurso_sin_mapa", "ACC")], True))
    r = j(ev(con_segs(msg(), OBX_ADT, ACC), adt_bundle(extra=[obs_obx()])))
    mira("la del OBX con la fecha de ACC-1 es del OBX (su código)", (cuentan(r), "fuera_proyeccion" in notas(r)), ([], True))
    mira("2.8: cuenta igual", cuentan(j(ev(con_segs(msg(msh={12: "2.8"}), ACC), adt_bundle(extra=[obs_acc()])))),
         [("fidelidad", "recurso_sin_mapa", "ACC")])
    x = {"resourceType": "Observation", "id": "o9", "status": "final", "code": cc("loinc", "9"), "subject": {"reference": "urn:uuid:p1"}}
    mira("control ORU: una Observation de más sigue inventada",
         ("fidelidad", "recurso_inventado", "OBX") in cuentan(j(ev(oru_msg(), oru_bundle([pac_oru(), dr(), obs1(), obs2(), x]), pe="oru_conv"))), True)


def p31():
    """Q-JZ-1 b: PID-8 fuera de la 0001 ya no es un valor imposible; el rechazo solo por él es rechazo incorrecto."""
    err = {"codigo": "1", "texto": "genero"}
    mira("rechazo con PID-8 X", cat(j(ev(msg(pid={8: "X"}), estado="error", error=err))), ("rechazo_incorrecto", "error"))
    mira("rechazo con PID-8 X y sin PV1: aceptable", cat(j(ev(msg(pid={8: "X"}, sin_pv1=True), estado="error", error=err))), ("correcto", None))
    mira("control PID-7 imposible: aceptable", cat(j(ev(msg(pid={7: "19801301"}), estado="error", error=err))), ("correcto", None))


def p32():
    """Etapa 37, tras la revisión a ciegas (jz/decision-jev-jz2.md, Q-JZ-6 b): L-CV-17 dice los dos riesgos de la regla de la 0136,
    y el texto de versión del servidor nombra L-CV-17. Etapa 40: L-CV-17 ya no da la de PD1-7 por de ACC o PDA, y la entrada de la
    37 deja de ser la primera."""
    import conversion as CV
    import mcp_verificador as M
    l17 = CV.L_CV["L-CV-17"]
    mira("L-CV-17: una Observation de solo Y/N que no sale de ACC ni de PDA (una inventada, o la de PD1-7 sin valueCodeableConcept) "
         "se da por de ellos; la de PD1-7 que la guía mapea, ya no (etapa 40)",
         ("0136" in l17, "inventada" in l17, "valueCodeableConcept" in l17, "que la guía sí mapea" in l17), (True, True, True, False))
    mira("L-CV-17: una de ACC o PDA ya no ocupa el sitio de la de un OBX", "ya no ocupa el sitio de la de un OBX" in l17, True)
    entradas = M.REVISION.split("; antes, ")          # la etapa más reciente, primero (Q-JZ-9 a)
    e37 = [e for e in entradas if e.startswith("etapa 37")]       # desde la etapa 40, la segunda (P-CV-34)
    mira("la versión del servidor: la entrada de la etapa 37, con L-CV-17", (len(e37), bool(e37) and "L-CV-17" in e37[0]), (1, True))
    mira("la versión del servidor: la entrada de la 14l, con L-CV-1..16",
         [e for e in entradas if e.startswith("14l")][:1] and "L-CV-1..16" in [e for e in entradas if e.startswith("14l")][0], True)


# ---------------------------------------------------------------------------- etapa 40: la Observation de PD1-7
CS0315 = "http://terminology.hl7.org/CodeSystem/v2-0315"
ACC_Y = seg("ACC", {1: "20260102", 3: "Calle Mayor 5", 5: "Y", 6: "N", 8: "caida en casa"})


def con_pd1(m, valor="F"):
    """El mensaje con PD1 (PD1-7 = valor) tras el PID, donde lo pone la estructura."""
    s = m.split("\r")
    k = next(i for i, x in enumerate(s) if x.startswith("PID|")) + 1
    return "\r".join(s[:k] + [seg("PD1", {7: valor})] + s[k:])


def obs_pd1(valor="F", sistema=CS0315, i="op", **k):
    """La Observation de PD1-7 como la crea la guía (PD1[Observation-LivingWill]): valueCodeableConcept por la 0315; sistema None,
    un coding sin sistema."""
    r = {"resourceType": "Observation", "id": i, "status": "final", "code": cc(CS, "living-will"), "subject": {"reference": "urn:uuid:p1"},
         "valueCodeableConcept": {"coding": [{"code": valor} if sistema is None else {"system": sistema, "code": valor}]}}
    r.update(k)
    return r


def de_pd1(r):
    """(origen, emparejado_por, fullUrl) del rol Observation#PD1, o None."""
    return next(((x["origen"], x["emparejado_por"], x["fullUrl"]) for x in r["conversion"]["emparejamiento"] or []
                 if x["rol"] == "Observation#PD1"), None)


def de_hecho(r, hecho):
    return sorted(h["subtipo"] for h in r["hallazgos"] if h["hecho"] == hecho)


def p33():
    """Etapa 40 (Q-PD-1 a, Q-PD-2 a, Q-PD-3 a): la Observation que la guía crea desde PD1-7 en un ADT (MSG_ADT_A01.csv:19) se
    reconoce por un coding de su valueCodeableConcept con el sistema de la 0315 o con el código de PD1-7, antes que ACC y PDA, y
    se juzga: su valor por la 0315, su status y su sujeto. Sin ella, recurso_ausente, que cuenta."""
    ACC_SM = ("fidelidad", "recurso_sin_mapa", "ACC")
    AUS = ("fidelidad", "recurso_ausente", "PD1-7")
    m = con_pd1(msg())
    r = j(ev(m, adt_bundle(extra=[obs_pd1()])))
    mira("PD1-7 = F y su Observation, sin OBX: correcta, y de PD1-7 por el sistema", (cat(r), cuentan(r), de_pd1(r)),
         (("correcto", None), [], ("PD1-7", "sistema", "urn:uuid:op")))
    mo = con_pd1(con_segs(msg(), OBX_ADT))
    for orden, extra in (("PD1 primero", [obs_pd1(), obs_obx()]), ("OBX primero", [obs_obx(), obs_pd1()])):
        r = j(ev(mo, adt_bundle(extra=extra)))
        mira("con OBX y las dos, %s: nada cuenta y la nota del OBX" % orden, (cuentan(r), "fuera_proyeccion" in notas(r), de_pd1(r)),
             ([], True, ("PD1-7", "sistema", "urn:uuid:op")))
    r = j(ev(mo, adt_bundle(extra=[obs_pd1()])))
    mira("control con OBX y solo la de PD1-7: nada cuenta", cuentan(r), [])
    mira("con OBX y solo la de PD1-7: ya no se toma por la del OBX", de_pd1(r), ("PD1-7", "sistema", "urn:uuid:op"))
    r = j(ev(m, adt_bundle()))
    h = [x for x in r["hallazgos"] if x["hecho"] == "PD1-7"]
    mira("PD1-7 = F sin Observation: recurso_ausente, que cuenta y cita la hoja",
         (cuentan(r), cat(r), bool(h) and "[G MSG_ADT_A01.csv:19]" in h[0]["citas"]), ([AUS], ("fallo_silencioso", "convertido"), True))
    for nombre, sistema in (("con el sistema de la 0136", CS0136), ("sin sistema", None)):
        mira("(F) %s: codigo_mal_mapeado" % nombre, cuentan(j(ev(m, adt_bundle(extra=[obs_pd1(sistema=sistema)])))),
             [("fidelidad", "codigo_mal_mapeado", "PD1-7")])
    mira("(v2-0315, Y) con PD1-7 = F: valor_distinto", cuentan(j(ev(m, adt_bundle(extra=[obs_pd1("Y")])))),
         [("fidelidad", "valor_distinto", "PD1-7")])
    mx = con_pd1(msg(), "X")
    r = j(ev(mx, adt_bundle(extra=[obs_pd1("X")])))
    mira("PD1-7 = X, fuera de la 0315, con el código X: nada, ni una nota", (cuentan(r), de_hecho(r, "PD1-7")), ([], []))
    r = j(ev(mx, adt_bundle(extra=[obs_pd1("W")])))
    mira("PD1-7 = X con (v2-0315, W): nota convencion en 2.5", (cuentan(r), de_hecho(r, "PD1-7")), ([], ["convencion"]))
    r = j(ev(con_pd1(msg(msh={12: "2.8"}), "X"), adt_bundle(extra=[obs_pd1("W")])))
    mira("PD1-7 = X con (v2-0315, W): nota version en 2.8", (cuentan(r), de_hecho(r, "PD1-7")), ([], ["version"]))
    my = con_segs(con_pd1(msg(), "Y"), ACC_Y)
    r = j(ev(my, adt_bundle(extra=[obs_pd1("Y")])))
    mira("PD1-7 = Y y ACC-5 = Y, una (v2-0315, Y): es la de PD1-7, no de ACC", (cuentan(r), de_pd1(r)), ([], ("PD1-7", "sistema", "urn:uuid:op")))
    for orden, extra in (("la de la 0315 primero", [obs_pd1("Y"), obs_sn("o2", "job-related", "Y")]),
                         ("la de la 0136 primero", [obs_sn("o2", "job-related", "Y"), obs_pd1("Y")])):
        r = j(ev(my, adt_bundle(extra=extra)))
        mira("... y otra (v2-0136, Y), %s: la de la 0315 es de PD1-7; la otra, de ACC" % orden, (cuentan(r), de_pd1(r)),
             ([ACC_SM], ("PD1-7", "sistema", "urn:uuid:op")))
    dos = [obs_pd1("Y", sistema=None, i="o1"), obs_pd1("Y", sistema=None, i="o2")]
    r = j(ev(my, adt_bundle(extra=dos)))
    mira("... dos de solo Y sin sistema: la primera, de PD1-7 (sin el sistema: codigo_mal_mapeado); la segunda, de ACC (Q-PD-2 a)",
         (cuentan(r), de_pd1(r)), ([("fidelidad", "codigo_mal_mapeado", "PD1-7"), ACC_SM], ("PD1-7", "codigo", "urn:uuid:o1")))
    r = j(ev(my, adt_bundle(extra=[obs_sn("o2", "job-related", "Y")])))
    mira("... una sola (v2-0136, Y): es la de PD1-7, con código mal mapeado, y no de ACC (Q-PD-4 a1)", (cuentan(r), de_pd1(r)),
         ([("fidelidad", "codigo_mal_mapeado", "PD1-7")], ("PD1-7", "codigo", "urn:uuid:o2")))
    mira("control PD1-7 vacío, ACC-5 = Y y una de solo Y: recurso_sin_mapa ACC, como hoy",
         cuentan(j(ev(con_segs(msg(), ACC_Y), adt_bundle(extra=[obs_sn("o1", "job-related", "Y")])))), [ACC_SM])
    mira("control PD1 sin PD1-7 y una (v2-0315, F): recurso_inventado, como hoy",
         cuentan(j(ev(con_pd1(msg(), ""), adt_bundle(extra=[obs_pd1()])))), [("fidelidad", "recurso_inventado", "OBX")])
    x = sin_clave(obs_obx(), "valueQuantity")
    x["valueCodeableConcept"] = {"coding": [{"system": CS0315, "code": "F"}]}
    r = j(ev(mo, adt_bundle(extra=[x])))
    mira("con el código del OBX y el valor de PD1-7: es la del OBX, y PD1-7 sale ausente", (cuentan(r), "fuera_proyeccion" in notas(r)),
         ([AUS], True))
    v = sin_clave(obs_pd1(), "valueCodeableConcept")
    v["valueString"] = "F"
    mira("valueString F: no se reconoce; recurso_ausente PD1-7 y recurso_inventado OBX (L-CV-18)", cuentan(j(ev(m, adt_bundle(extra=[v])))),
         [AUS, ("fidelidad", "recurso_inventado", "OBX")])
    mira("sin status: fhir_invalido PD1-7", cuentan(j(ev(m, adt_bundle(extra=[sin_clave(obs_pd1(), "status")])))),
         [("fidelidad", "fhir_invalido", "PD1-7")])
    mira("subject a otro Patient: referencia_rota PD1-7",
         cuentan(j(ev(m, adt_bundle(extra=[obs_pd1(subject={"reference": "urn:uuid:p9"})])))), [("fidelidad", "referencia_rota", "PD1-7")])
    m28 = con_pd1(msg(msh={12: "2.8"}))
    r = j(ev(m28, adt_bundle(extra=[obs_pd1()])))
    mira("2.8 con (v2-0315, F): nada cuenta, de PD1-7, con la nota de versión", (cuentan(r), de_pd1(r), "version" in notas(r)),
         ([], ("PD1-7", "sistema", "urn:uuid:op"), True))
    mira("2.8 sin Observation: recurso_ausente cuenta igual", cuentan(j(ev(m28, adt_bundle()))), [AUS])
    r = j(ev(con_pd1(msg(msh={12: "2.8"}), "F^Living will on file^HL70315"), adt_bundle(extra=[obs_pd1()])))
    mira("2.8, PD1-7 con componentes (CWE): se lee su primer componente", (cuentan(r), de_hecho(r, "PD1-7"), de_pd1(r)),
         ([], [], ("PD1-7", "sistema", "urn:uuid:op")))
    mira("control ORU con PD1 y PD1-7 vacío: la Observation de más sigue inventada (con PD1-7, P-CV-35)",
         ("fidelidad", "recurso_inventado", "OBX") in cuentan(j(ev(con_pd1(oru_msg(), ""), oru_bundle([pac_oru(), dr(), obs1(), obs2(), obs_pd1()]),
                                                                  pe="oru_conv"))), True)


def p34():
    """Etapa 40 (pd/diseno-pd-fable.md §1.5): lo que el juez dice de sí mismo."""
    import os as _os
    import conversion as CV
    import mcp_verificador as M
    filas = [f for f in CV.PERFIL_GUIA_ADT if f.get("campo") == "PD1-7"]
    mira("el perfil de ADT: 23 filas, una de PD1-7 que cuenta y cita la hoja",
         (len(CV.PERFIL_GUIA_ADT), len(filas), filas[0]["nivel"] if filas else None, bool(filas) and "[G MSG_ADT_A01.csv:19]" in filas[0]["citas"]),
         (23, 1, "cuenta", True))
    mira("C[PD1-7] cita el mapa de segmento y la 0315", ["[CM table-hl70315-to-v2-0315]" in CV.C.get("PD1-7", []),
                                                        any("segment-pd1-livingwill-to-observation" in c for c in CV.C.get("PD1-7", []))], [True, True])
    l18 = CV.L_CV.get("L-CV-18", "")
    mira("L-CV-18 nombra PD1-7, la 0315 y ORU", ("PD1-7" in l18, "0315" in l18, "ORU" in l18), (True, True, True))
    mira("L-CV-18 nombra el caso de Q-PD-4: una de solo Y/N sin el sistema de la 0315, también con el de la 0136, es la de PD1-7",
         ("sin el sistema de la 0315" in l18, "con el de la 0136" in l18, "Q-PD-4" in l18), (True, True, True))
    mira("S-CV-4 nombra PD1-7", "PD1-7" in CV.S_CV["S-CV-4"], True)
    mira("la 0315: la identidad sobre Y, F, N, I, U con el sistema v2-0315", CV.MAPAS.get("table-hl70315-to-v2-0315"),
         {c: (CS0315, c) for c in "YFNIU"})
    if _os.path.isdir(CV.PAQUETE):
        sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(CV.__file__)), "cv"))
        import extraer_mapas as X
        mira("la 0315 es la del paquete, y está en la lista de cv/extraer_mapas.py",
             ("table-hl70315-to-v2-0315" in X.MAPAS, X.mapa(CV.PAQUETE, "table-hl70315-to-v2-0315") == CV.MAPAS.get("table-hl70315-to-v2-0315")),
             (True, True))
    entradas = M.REVISION.split("; antes, ")
    i40 = next((i for i, e in enumerate(entradas) if e.startswith("etapa 40")), None)    # desde la 41, la segunda (P-CV-36)
    mira("la versión del servidor: la entrada de la etapa 40 con L-CV-18, y tras ella la de la 37 con L-CV-17",
         (i40 is not None, i40 is not None and "L-CV-18" in entradas[i40],
          i40 is not None and len(entradas) > i40 + 1 and entradas[i40 + 1].startswith("etapa 37") and "L-CV-17" in entradas[i40 + 1]),
         (True, True, True))


# ---------------------------------------------------------------------------- etapa 41: la Observation de PD1-7 en un ORU
def oru_fuera(m, codigo="F9"):
    """El ORU con un OBX antes del primer OBR: fuera de ORDER_OBSERVATION (L-CV-7)."""
    s = m.split("\r")
    k = next(i for i, x in enumerate(s) if x.startswith("OBR|"))
    return "\r".join(s[:k] + [seg("OBX", {1: "1", 2: "ST", 3: "%s^Fuera^LN" % codigo, 5: "x", 11: "F"})] + s[k:])


def obs_fuera(i="of", codigo="F9"):
    return {"resourceType": "Observation", "id": i, "status": "final", "code": cc("loinc", codigo), "subject": {"reference": "urn:uuid:p1"},
            "valueString": "x"}


def v28(m):
    return m.replace("|P|2.5\r", "|P|2.8\r", 1)


def p35():
    """Etapa 41 (Q-PO-1 a, Q-PO-2 b): en un ORU, la Observation que la guía crea desde PD1-7 (MSG_ORU_R01.csv:17) se aparta antes de
    casar las de los OBX y se juzga como en ADT (etapa 40); sin ella, recurso ausente con la cita de la hoja de ORU. Una referencia a
    ella desde DiagnosticReport.result sigue siendo referencia_rota del OBR."""
    AUS = ("fidelidad", "recurso_ausente", "PD1-7")
    OP = ("PD1-7", "sistema", "urn:uuid:op")
    m = con_pd1(oru_msg())

    def base(*mas):
        return oru_bundle([pac_oru(), dr(), obs1(), obs2()] + list(mas))

    def jo(mm, b):
        return j(ev(mm, b, pe="oru_conv"))

    def cita(r, hoja):
        h = [x for x in r["hallazgos"] if x["hecho"] == "PD1-7"]
        return bool(h) and hoja in h[0]["citas"]

    r = jo(m, base(obs_pd1()))
    mira("ORU, PD1-7 = F y su Observation: correcta, y de PD1-7 por el sistema", (cat(r), cuentan(r), de_pd1(r)), (("correcto", None), [], OP))
    b2 = oru_dos(sobrante=False)
    b2["entry"].append({"fullUrl": "urn:uuid:op", "resource": obs_pd1()})
    r = jo(con_pd1(oru_msg(dos=True)), b2)
    mira("con dos OBR: de PD1-7, y nada cuenta", (cuentan(r), de_pd1(r)), ([], OP))
    d = dr()
    d["result"] = d["result"] + [{"reference": "urn:uuid:op"}]
    r = jo(m, oru_bundle([pac_oru(), d, obs1(), obs2(), obs_pd1()]))
    mira("referida desde DiagnosticReport.result: de PD1-7, y el OBR sigue con referencia_rota (Q-PO-1 a)", (cuentan(r), de_pd1(r)),
         ([("fidelidad", "referencia_rota", "OBR")], OP))
    r = jo(m, base())
    mira("sin Observation: recurso_ausente, que cita la hoja de ORU y no la de ADT (Q-PO-2 b)",
         (cuentan(r), cita(r, "[G MSG_ORU_R01.csv:17]"), cita(r, "[G MSG_ADT_A01.csv:19]")), ([AUS], True, False))
    mira("2.8 sin Observation: recurso_ausente cuenta igual", cuentan(jo(v28(m), base())), [AUS])
    mira("(v2-0315, Y) con PD1-7 = F: valor_distinto", cuentan(jo(m, base(obs_pd1("Y")))), [("fidelidad", "valor_distinto", "PD1-7")])
    for nombre, sistema in (("con el sistema de la 0136", CS0136), ("sin sistema", None)):
        mira("(F) %s: codigo_mal_mapeado" % nombre, cuentan(jo(m, base(obs_pd1(sistema=sistema)))),
             [("fidelidad", "codigo_mal_mapeado", "PD1-7")])
    mx = con_pd1(oru_msg(), "X")
    r = jo(mx, base(obs_pd1("X")))
    mira("PD1-7 = X con el código X: nada, ni una nota", (cuentan(r), de_hecho(r, "PD1-7")), ([], []))
    r = jo(mx, base(obs_pd1("W")))
    mira("PD1-7 = X con (v2-0315, W): nota convencion en 2.5", (cuentan(r), de_hecho(r, "PD1-7")), ([], ["convencion"]))
    r = jo(v28(mx), base(obs_pd1("W")))
    mira("PD1-7 = X con (v2-0315, W): nota version en 2.8", (cuentan(r), de_hecho(r, "PD1-7")), ([], ["version"]))
    v = sin_clave(obs_pd1(), "valueCodeableConcept")
    v["valueString"] = "F"
    mira("valueString F: recurso_ausente PD1-7 y recurso_inventado OBX (L-CV-18)", cuentan(jo(m, base(v))),
         [AUS, ("fidelidad", "recurso_inventado", "OBX")])
    mira("sin status: fhir_invalido PD1-7", cuentan(jo(m, base(sin_clave(obs_pd1(), "status")))), [("fidelidad", "fhir_invalido", "PD1-7")])
    mira("subject a otro Patient: referencia_rota PD1-7", cuentan(jo(m, base(obs_pd1(subject={"reference": "urn:uuid:p9"})))),
         [("fidelidad", "referencia_rota", "PD1-7")])
    r = jo(m, base(sin_clave(obs_pd1(), "subject")))
    mira("sin subject: dato_perdido PD1-7, con la cita de la hoja de ORU", (cuentan(r), cita(r, "[G MSG_ORU_R01.csv:17]")),
         ([("fidelidad", "dato_perdido", "PD1-7")], True))
    o1f = obs1()
    o1f["code"] = cc("loinc", "F")
    r = jo(con_pd1(oru_msg(obx={3: "F^Codigo F^LN"})), oru_bundle([pac_oru(), dr(), o1f, obs2(), obs_pd1()]))
    mira("un OBX con el código F y las dos Observation: la de código F es del OBX; la otra, de PD1-7", (cuentan(r), de_pd1(r)), ([], OP))
    o2v = sin_clave(obs2(), "valueString")
    o2v["valueCodeableConcept"] = {"coding": [{"system": CS0315, "code": "F"}]}
    r = jo(m, oru_bundle([pac_oru(), dr(), obs1(), o2v]))
    mira("la de un OBX con su código y el valor (v2-0315, F), sin la de PD1-7: es del OBX, y PD1-7 sale ausente",
         (AUS in cuentan(r), de_pd1(r)), (True, ("PD1-7", None, None)))
    mo = oru_fuera(m)
    r = jo(mo, base(obs_pd1()))
    mira("un OBX fuera de ORDER_OBSERVATION sin su Observation, y la de PD1-7: de PD1-7, sin la nota de L-CV-7",
         (cuentan(r), "fuera_proyeccion" in notas(r), de_pd1(r)), ([], False, OP))
    for orden, extra in (("la del OBX fuera primero", [obs_fuera(), obs_pd1()]), ("la de PD1-7 primero", [obs_pd1(), obs_fuera()])):
        r = jo(mo, base(*extra))
        mira("un OBX fuera con su Observation y la de PD1-7, %s: la nota, de la del OBX; la otra, de PD1-7" % orden,
             (cuentan(r), "fuera_proyeccion" in notas(r), de_pd1(r)), ([], True, OP))
    of = sin_clave(obs_fuera(), "valueString")
    of["valueCodeableConcept"] = {"coding": [{"system": CS0315, "code": "F"}]}
    r = jo(mo, base(of))
    mira("la del OBX fuera con su código y el valor (v2-0315, F), sin la de PD1-7: nota de L-CV-7, y PD1-7 ausente",
         (cuentan(r), "fuera_proyeccion" in notas(r)), ([AUS], True))
    r = jo(v28(con_pd1(oru_msg(), "F^Living will on file^HL70315")), base(obs_pd1()))
    mira("2.8, PD1-7 con componentes (CWE): se lee su primer componente", (cuentan(r), de_hecho(r, "PD1-7"), de_pd1(r)), ([], [], OP))
    r = jo(v28(m), base(obs_pd1()))
    mira("2.8 con (v2-0315, F): nada cuenta, de PD1-7, con la nota de versión", (cuentan(r), de_pd1(r), "version" in notas(r)),
         ([], OP, True))
    r = jo(con_pd1(oru_msg(obx={3: "F^Codigo F^LN"}), ""), oru_bundle([pac_oru(), dr(), o1f, obs2()]))
    mira("control PD1-7 vacío y un OBX con el código F: la de código F es del OBX y nada cuenta, como hoy", cuentan(r), [])


def p36():
    """Etapa 41 (po/diseno-po-fable.md §1.5): lo que el juez dice de sí mismo."""
    import conversion as CV
    import mcp_verificador as M
    filas = [f for f in CV.PERFIL_GUIA_ORU if f.get("campo") == "PD1-7"]
    mira("el perfil de ORU: 17 filas, una de PD1-7 que cuenta y cita la hoja de ORU, no la de ADT",
         (len(CV.PERFIL_GUIA_ORU), len(filas), filas[0]["nivel"] if filas else None,
          bool(filas) and "[G MSG_ORU_R01.csv:17]" in filas[0]["citas"], bool(filas) and "[G MSG_ADT_A01.csv:19]" in filas[0]["citas"]),
         (17, 1, "cuenta", True, False))
    cit = getattr(CV, "CITAS_PD17", {})
    mira("las citas por familia (Q-PO-2 b): la de ORU con su hoja; la de ADT y C[PD1-7], como en la 40",
         ("[G MSG_ORU_R01.csv:17]" in cit.get("oru", []), "[G MSG_ADT_A01.csv:19]" in cit.get("oru", []), cit.get("adt") == CV.C["PD1-7"],
          "[G MSG_ORU_R01.csv:17]" in CV.C["PD1-7"]), (True, False, True, False))
    l18 = CV.L_CV.get("L-CV-18", "")
    mira("L-CV-18 nombra oru_conv, DiagnosticReport.result y L-CV-7, y ya no dice que siga como recurso_inventado",
         ("oru_conv" in l18, "DiagnosticReport.result" in l18, "L-CV-7" in l18, "sigue como recurso_inventado" in l18), (True, True, True, False))
    mira("S-CV-4 nombra ORU", "ORU" in CV.S_CV["S-CV-4"], True)
    entradas = M.REVISION.split("; antes, ")
    mira("la versión del servidor: la primera entrada, la de la etapa 41 con L-CV-18; la segunda, la de la 40",
         (entradas[0].startswith("etapa 41"), "L-CV-18" in entradas[0], len(entradas) > 1 and entradas[1].startswith("etapa 40")),
         (True, True, True))


PRUEBAS = [p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24,
           p25, p26, p27, p28, p29, p30, p31, p32, p33, p34, p35, p36]


def main():
    rojo = sys.argv[1:] == ["rojo"]
    for p in PRUEBAS:
        grupo[0] = "P-CV-%d" % int(p.__name__[1:])
        try:
            p()
        except Exception as ex:                                             # en rojo, lo esperado es que el PE no exista
            FALLAN.add(grupo[0])
            if not rojo:
                print("  EXCEPCIÓN %s: %s" % (grupo[0], "".join(traceback.format_exception_only(type(ex), ex)).strip()[:300]))
                mal.append(grupo[0])
    if rojo:
        print("PRUEBAS CONVERSIÓN (rojo): fallan %d de %d %s" % (len(FALLAN), len(PRUEBAS), "(TODAS)" if len(FALLAN) == len(PRUEBAS) else ""))
        return 0 if len(FALLAN) == len(PRUEBAS) else 1
    print("PRUEBAS CONVERSIÓN: %s (%d comprobaciones, %d pruebas)" % ("TODO BIEN" if not mal else "%d MAL" % len(mal), n_ok[0], len(PRUEBAS)))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
