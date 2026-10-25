#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 18 (cv/vc/diseno-vc-fable.md §5.1): el conversor de juguete del laboratorio. Es el accesorio de las pruebas de
cv/verificar_conversor.py (cv/prueba_vc.py), no el código bajo prueba: lo único que la herramienta acepta correr fuera de la
caja (S-VC-4). Escribe sus Bundles a mano; no importa conversion ni ningún módulo del juez (CV1-b: un error de la proyección
no se confirma a sí mismo).

  python3 conversor_juguete.py <entrada_dir> <salida_dir>                          # lote: <base>.json o <base>.error
  python3 conversor_juguete.py --fichero <in> --salida <out> [--error <err>]       # un mensaje

La directiva va en MSH-8 (Seguridad), que el juez no lee (DV-VC-2: el diseño la ponía en MSH-3, que adt_conv consume);
el segundo componente es su parámetro. Sin directiva, un Bundle genérico con unos pocos campos del mensaje.
  JUGUETE-NOMINAL        el Bundle nominal escrito a mano (ADT, ORU o VXU por MSH-9.1), copiado de prueba_conversion.py y
                         de prueba_conversion_vxu.py
  JUGUETE-RUTA           el nominal VXU con route {v2-0162, IM} (etapa 20: control positivo, RXR-1 mal mapeado)
  JUGUETE-GENERO         el nominal ADT con gender «male»
  JUGUETE-ERROR          una traza de tres líneas en <base>.error (o en --error), nada más
  JUGUETE-NADA           no escribe nada y sigue (código 0)
  JUGUETE-RC3            no escribe nada y el proceso termina con 3 (en lote, tras los demás)
  JUGUETE-LENTO^<s>      duerme <s> segundos (5 por omisión) y escribe el nominal
  JUGUETE-ENVUELTO       {"Status": "OK", "FhirResource": <nominal ORU>}, con el «"value":1.20» literal
  JUGUETE-ENVUELTO-FALLO {"Status": "Fail", "Error": "sin plantilla para X"}
  JUGUETE-GRANDE^<n>     el nominal ADT relleno hasta <n> caracteres exactos (4000001 por omisión)
  JUGUETE-ILEGIBLE       un <base>.json que no es JSON
Imprime «<nombre> <ms> ms» por mensaje."""
import json
import os
import re
import sys
import time

S = {"0203": "http://terminology.hl7.org/CodeSystem/v2-0203", "act": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
     "mar": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "0007": "http://terminology.hl7.org/CodeSystem/v2-0007",
     "sty": "http://terminology.hl7.org/CodeSystem/service-type", "par": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
     "loinc": "http://loinc.org", "ucum": "http://unitsofmeasure.org",
     "int": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation"}
GENERO = {"F": "female", "M": "male", "O": "other", "U": "unknown", "A": "other", "N": "other"}       # tabla 0001, a mano
CLASE = {"E": "EMER", "I": "IMP", "O": "AMB", "P": "PRENC"}


def cc(sistema, codigo):
    return {"coding": [{"system": S.get(sistema, sistema), "code": codigo}]}


# ---------------------------------------------------------------------------- los nominales (copia de prueba_conversion.py)
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


def prac():
    return {"resourceType": "Practitioner", "id": "pr1", "identifier": [{"value": "123"}],
            "name": [{"family": "García", "given": ["Luis"], "prefix": ["Dr"]}]}


def locs():
    out = []
    valores = ("A", "101", "URG", "HOSP")
    for k, v in enumerate(valores, 1):
        r = {"resourceType": "Location", "id": "l%d" % k, "identifier": [{"value": v}]}
        if k < len(valores):
            r["partOf"] = {"reference": "urn:uuid:l%d" % (k + 1)}
        out.append(r)
    return out


def adt_nominal(genero="female"):
    p = pac()
    p["gender"] = genero
    rs = [p, enc(), prac()] + locs()
    return {"resourceType": "Bundle", "type": "batch", "entry": [{"fullUrl": "urn:uuid:" + r["id"], "resource": r} for r in rs]}


def oru_nominal():
    p = {"resourceType": "Patient", "id": "p1", "identifier": [{"value": "X1", "type": cc("0203", "MR"), "assigner": {"display": "H"}}],
         "name": [{"family": "Pérez", "given": ["Ana", "Luz"], "use": "official"}], "birthDate": "1980-02-15", "gender": "female"}
    o1 = {"resourceType": "Observation", "id": "o1", "status": "final", "code": cc("loinc", "2345-7"), "subject": {"reference": "urn:uuid:p1"},
          "effectiveDateTime": "2026-01-01T08:00:00+01:00",
          "valueQuantity": {"value": "@NUM:1.20@", "unit": "mg/dL", "system": S["ucum"], "code": "mg/dL"},
          "interpretation": [cc("int", "H")], "referenceRange": [{"text": "0.5-1.5"}]}
    o2 = {"resourceType": "Observation", "id": "o2", "status": "final", "code": cc("loinc", "8251-1"), "subject": {"reference": "urn:uuid:p1"},
          "valueString": "texto"}
    d = {"resourceType": "DiagnosticReport", "id": "d1",
         "identifier": [{"value": "PL1", "type": cc("0203", "PLAC")}, {"value": "FL1", "type": cc("0203", "FILL")}],
         "status": "final", "code": cc("loinc", "A"), "subject": {"reference": "urn:uuid:p1"},
         "effectivePeriod": {"start": "2026-01-01T08:00:00+01:00", "end": "2026-01-01T09:00:00+01:00"},
         "issued": "2026-01-01T10:00:00+01:00", "result": [{"reference": "urn:uuid:o1"}, {"reference": "urn:uuid:o2"}]}
    return {"resourceType": "Bundle", "type": "collection", "entry": [{"fullUrl": "urn:uuid:" + r["id"], "resource": r} for r in (p, d, o1, o2)]}


def vxu_nominal(ruta_v2=False):
    """Etapa 20: el Bundle nominal de VXU, copia de prueba_conversion_vxu.py (pac, inm, prac, org); ruta_v2 es JUGUETE-RUTA."""
    v2 = "http://terminology.hl7.org/CodeSystem/v2-%s"
    p = {"resourceType": "Patient", "id": "p1",
         "identifier": [{"value": "VAC0001", "type": cc("0203", "MR"), "assigner": {"display": "CSSYN"}}],
         "name": [{"family": "Prueba", "given": ["Mateo"], "use": "official"}], "birthDate": "2023-05-12", "gender": "male"}
    i = {"resourceType": "Immunization", "id": "i1",
         "identifier": [{"value": "VX-01", "type": cc("0203", "FILL")}], "status": "completed",
         "vaccineCode": {"coding": [{"system": "http://hl7.org/fhir/sid/cvx", "code": "03", "display": "MMR"}]},
         "patient": {"reference": "urn:uuid:p1"}, "occurrenceDateTime": "2024-01-15T10:30:00+01:00", "recorded": "2024-01-15T10:45:00+01:00",
         "lotNumber": "LOT-01", "expirationDate": "2025-11", "manufacturer": {"reference": "urn:uuid:o1"},
         "route": {"coding": [{"system": v2 % "0162" if ruta_v2 else "http://terminology.hl7.org/CodeSystem/v3-RouteOfAdministration", "code": "IM"}]},
         "site": {"coding": [{"system": v2 % "0163", "code": "LD"}]},
         "doseQuantity": {"value": "@NUM:0.5@", "unit": "mL", "system": S["ucum"], "code": "mL"},
         "performer": [{"function": {"coding": [{"system": v2 % "0443", "code": "AP"}]}, "actor": {"reference": "urn:uuid:pr1"}}]}
    pr = {"resourceType": "Practitioner", "id": "pr1", "identifier": [{"value": "1234"}], "name": [{"family": "Goldstein", "given": ["Harold"]}]}
    o = {"resourceType": "Organization", "id": "o1", "identifier": [{"system": "http://terminology.hl7.org/CodeSystem/MVX", "value": "MSD"}],
         "name": "Merck & Co., Inc."}
    return {"resourceType": "Bundle", "type": "collection", "entry": [{"fullUrl": "urn:uuid:" + r["id"], "resource": r} for r in (p, i, pr, o)]}


def texto(b):
    """JSON del Bundle; «@NUM:1.20@» queda como el número 1.20 tal cual."""
    return re.sub(r'"@NUM:([^@]*)@"', r"\1", json.dumps(b, ensure_ascii=False))


# ---------------------------------------------------------------------------- el mensaje
class Msg:
    def __init__(self, t):
        self.segs = [s for s in re.split(r"\r\n|\n|\r", t.lstrip("﻿").strip()) if s]
        msh = self.segs[0] if self.segs and self.segs[0].startswith("MSH") and len(self.segs[0]) > 4 else ""
        self.f = msh[3] if msh else "|"
        self.c = msh[4] if len(msh) > 4 else "^"

    def campo(self, nombre, i, k=None):
        for s in self.segs:
            p = s.split(self.f)
            if p[0] == nombre:
                if nombre == "MSH":
                    i -= 1
                v = p[i] if len(p) > i else ""
                return v.split(self.c)[k - 1] if k and len(v.split(self.c)) >= k else ("" if k else v)
        return ""

    def todos(self, nombre):
        return [s.split(self.f) for s in self.segs if s.split(self.f)[0] == nombre]


def fecha(v):
    return "%s-%s-%s" % (v[:4], v[4:6], v[6:8]) if re.match(r"^\d{8}", v or "") else None


def generico(m):
    """Unos pocos campos, a mano: PID-3.1, PID-5, PID-7, PID-8, PID-16 (v3, con el mismo código), PV1-2, PV1-19; en ORU, OBX."""
    p = {"resourceType": "Patient", "id": "p1"}
    if m.campo("PID", 3, 1):
        p["identifier"] = [{"value": m.campo("PID", 3, 1)}]
    if m.campo("PID", 5, 1):
        p["name"] = [{"family": m.campo("PID", 5, 1), "given": [x for x in [m.campo("PID", 5, 2)] if x]}]
    if fecha(m.campo("PID", 7)):
        p["birthDate"] = fecha(m.campo("PID", 7))
    if m.campo("PID", 8) in GENERO:
        p["gender"] = GENERO[m.campo("PID", 8)]
    if m.campo("PID", 16, 1):
        p["maritalStatus"] = cc("mar", m.campo("PID", 16, 1))
    rs = [p]
    if m.campo("MSH", 9, 1).upper() == "ORU":
        obs = []
        for k, x in enumerate(m.todos("OBX"), 1):
            o = {"resourceType": "Observation", "id": "o%d" % k, "status": "final",
                 "code": cc("loinc", (x[3] if len(x) > 3 else "").split(m.c)[0]), "subject": {"reference": "urn:uuid:p1"}}
            tipo, val = (x[2] if len(x) > 2 else ""), (x[5] if len(x) > 5 else "")
            if tipo == "NM" and re.match(r"^-?\d+(\.\d+)?$", val):
                o["valueQuantity"] = {"value": "@NUM:%s@" % val}
            elif tipo == "NM" and re.match(r"^\.\d+$", val):
                o["valueQuantity"] = {"value": "@NUM:%s@" % val[1:]}          # el punto inicial se pierde, a propósito
            elif tipo in ("ST", "TX", "FT") and val:
                o["valueString"] = val
            obs.append(o)
        rs += [{"resourceType": "DiagnosticReport", "id": "d1", "status": "final", "subject": {"reference": "urn:uuid:p1"},
                "result": [{"reference": "urn:uuid:" + o["id"]} for o in obs]}] + obs
    else:
        e = {"resourceType": "Encounter", "id": "e1", "status": "in-progress", "subject": {"reference": "urn:uuid:p1"}}
        if m.campo("PV1", 2) in CLASE:
            e["class"] = {"system": S["act"], "code": CLASE[m.campo("PV1", 2)]}
        if m.campo("PV1", 19, 1):
            e["identifier"] = [{"value": m.campo("PV1", 19, 1)}]
        rs.append(e)
    return {"resourceType": "Bundle", "type": "collection", "entry": [{"fullUrl": "urn:uuid:" + r["id"], "resource": r} for r in rs]}


def nominal(m):
    t = m.campo("MSH", 9, 1).upper()
    return oru_nominal() if t == "ORU" else vxu_nominal() if t == "VXU" else adt_nominal()


def convertir(t):
    """-> (accion, contenido): accion en bundle | error | nada | rc3."""
    m = Msg(t)
    d, param = m.campo("MSH", 8, 1).upper(), m.campo("MSH", 8, 2)
    if d == "JUGUETE-NOMINAL":
        return "bundle", texto(nominal(m))
    if d == "JUGUETE-RUTA":
        return "bundle", texto(vxu_nominal(ruta_v2=True))
    if d == "JUGUETE-GENERO":
        return "bundle", texto(adt_nominal("male"))
    if d == "JUGUETE-ERROR":
        return "error", "Traceback (juguete):\n  en convertir()\nErrorJuguete: el mensaje pide fallar\n"
    if d == "JUGUETE-NADA":
        return "nada", None
    if d == "JUGUETE-RC3":
        return "rc3", None
    if d == "JUGUETE-LENTO":
        time.sleep(float(param or 5))
        return "bundle", texto(nominal(m))
    if d == "JUGUETE-ENVUELTO":
        return "bundle", '{"Status": "OK", "FhirResource": %s}' % texto(oru_nominal())
    if d == "JUGUETE-ENVUELTO-FALLO":
        return "bundle", json.dumps({"Status": "Fail", "Error": "sin plantilla para X"})
    if d == "JUGUETE-GRANDE":
        n = int(param or 4000001)
        b = adt_nominal()
        b["entry"][0]["resource"]["text"] = {"status": "generated", "div": ""}
        falta = n - len(texto(b))
        b["entry"][0]["resource"]["text"]["div"] = "x" * max(falta, 0)
        return "bundle", texto(b)
    if d == "JUGUETE-ILEGIBLE":
        return "bundle", "esto no es JSON {"
    return "bundle", texto(generico(m))


def escribir(ruta, contenido):
    with open(ruta, "w", encoding="utf-8", newline="") as g:
        g.write(contenido)


def lote(entrada, salida):
    rc = 0
    for f in sorted(os.listdir(entrada)):
        if not f.endswith(".hl7"):
            continue
        t0 = time.time()
        base = os.path.splitext(f)[0]
        accion, contenido = convertir(open(os.path.join(entrada, f), encoding="utf-8").read())
        if accion == "bundle":
            escribir(os.path.join(salida, base + ".json"), contenido)
        elif accion == "error":
            escribir(os.path.join(salida, base + ".error"), contenido)
        elif accion == "rc3":
            rc = 3
        print("%s %d ms" % (f, int((time.time() - t0) * 1000)), flush=True)
    return rc


def uno(entrada, salida, error=None):
    t0 = time.time()
    accion, contenido = convertir(open(entrada, encoding="utf-8").read())
    print("%s %d ms" % (os.path.basename(entrada), int((time.time() - t0) * 1000)), flush=True)
    if accion == "bundle":
        escribir(salida, contenido)
    elif accion == "error":
        if error:
            escribir(error, contenido)
        else:
            sys.stderr.write(contenido)
            return 1
    elif accion == "rc3":
        sys.stderr.write("juguete: termina con 3\n")
        return 3
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--fichero"]:
        op = dict(zip(a[::2], a[1::2]))
        sys.exit(uno(op["--fichero"], op["--salida"], op.get("--error")))
    sys.exit(lote(a[0], a[1]))
