#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El conversor del proyecto de ejemplo de la integración continua (etapa 24, ejemplo-ci/README.md): HL7 v2 -> FHIR R4, pequeño,
sin dependencias y determinista. Lee ADT, ORU^R01 y VXU^V04 y escribe un Bundle por mensaje. Hace a propósito lo justo: lo que
haga mal a ojos del verificador lo registra la línea base del proyecto.
  python3 conversor.py <entrada_dir> <salida_dir>
Por cada <base>.hl7 escribe <base>.json (el Bundle) o <base>.error (una línea con el motivo), e imprime «<nombre> <ms> ms»."""
import json
import os
import re
import sys
import time

GENERO = {"F": "female", "M": "male", "O": "other", "U": "unknown", "A": "other", "N": "other"}   # tabla 0001
CLASE = {"E": "EMER", "I": "IMP", "O": "AMB", "P": "PRENC"}
ESTADO_OBR = {"F": "final", "P": "preliminary", "C": "corrected", "X": "cancelled"}
NUMERO = re.compile(r"^-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?$")
SIS = "http://terminology.hl7.org/CodeSystem/"


class Mensaje:
    def __init__(self, texto):
        self.segs = [s for s in re.split(r"\r\n|\r|\n", texto) if s.strip()]

    def campos(self, seg):
        return seg.split("|")

    def campo_de(self, seg, n):
        p = self.campos(seg)
        i = n - 1 if seg.startswith("MSH") else n
        return p[i].split("~")[0] if 0 <= i < len(p) else ""

    def comp_de(self, seg, n, c):
        x = self.campo_de(seg, n).split("^")
        return x[c - 1] if c - 1 < len(x) else ""

    def primero(self, nombre):
        return next((s for s in self.segs if s.startswith(nombre + "|")), None)


def fecha(v):
    m = re.match(r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(?:\.\d+)?([+-]\d{4})?$", v)
    if m:
        t = "%s-%s-%sT%s:%s:%s" % m.groups()[:6]
        return t + ("%s:%s" % (m.group(7)[:3], m.group(7)[3:]) if m.group(7) else "")
    m = re.match(r"^(\d{4})(\d{2})(\d{2})$", v)
    if m:
        return "%s-%s-%s" % m.groups()
    m = re.match(r"^(\d{4})(\d{2})$", v)
    return "%s-%s" % m.groups() if m else None


class Numeros:
    """Un número va al JSON con el texto literal del mensaje: un marcador en el objeto y un reemplazo en el texto serializado."""
    def __init__(self):
        self.literales = []

    def valor(self, texto):
        self.literales.append(texto)
        return "@@NUMERO%d@@" % (len(self.literales) - 1)

    def poner(self, js):
        for i, t in enumerate(self.literales):
            js = js.replace('"@@NUMERO%d@@"' % i, t)
        return js


def codigo(sistema, valor):
    return {"coding": [{"system": sistema, "code": valor}]}


def concepto(m, seg, n, sistemas):
    c = {"code": m.comp_de(seg, n, 1)}
    if m.comp_de(seg, n, 2):
        c["display"] = m.comp_de(seg, n, 2)
    if m.comp_de(seg, n, 3) in sistemas:
        c["system"] = sistemas[m.comp_de(seg, n, 3)]
    return {"coding": [c]}


def paciente(m, pid):
    p = {"resourceType": "Patient", "id": "p1"}
    ident = {"value": m.comp_de(pid, 3, 1)}
    if m.comp_de(pid, 3, 5):
        ident["type"] = codigo(SIS + "v2-0203", m.comp_de(pid, 3, 5))
    p["identifier"] = [ident]
    nombre = {"family": m.comp_de(pid, 5, 1), "given": [x for x in (m.comp_de(pid, 5, 2), m.comp_de(pid, 5, 3)) if x], "use": "official"}
    p["name"] = [nombre]
    if fecha(m.campo_de(pid, 7)):
        p["birthDate"] = fecha(m.campo_de(pid, 7))
    if m.campo_de(pid, 8) in GENERO:
        p["gender"] = GENERO[m.campo_de(pid, 8)]
    if m.comp_de(pid, 11, 1):
        d = {"line": [m.comp_de(pid, 11, 1)]}
        for clave, c in (("city", 3), ("state", 4), ("postalCode", 5), ("country", 6)):
            if m.comp_de(pid, 11, c):
                d[clave] = m.comp_de(pid, 11, c)
        p["address"] = [d]
    tel = m.comp_de(pid, 13, 12) or m.comp_de(pid, 13, 1)
    if tel:
        p["telecom"] = [{"system": "phone", "value": tel, "use": "home"}]
    if m.campo_de(pid, 16):
        p["maritalStatus"] = codigo(SIS + "v3-MaritalStatus", m.campo_de(pid, 16))
    return p


def encuentro(m, pv1, evento):
    e = {"resourceType": "Encounter", "id": "e1", "status": "finished" if evento == "A03" else "in-progress"}
    if m.campo_de(pv1, 2) in CLASE:
        e["class"] = {"system": SIS + "v3-ActCode", "code": CLASE[m.campo_de(pv1, 2)]}
    if m.comp_de(pv1, 19, 1):
        e["identifier"] = [{"value": m.comp_de(pv1, 19, 1)}]
    e["subject"] = {"reference": "urn:uuid:p1"}
    periodo = {}
    if fecha(m.campo_de(pv1, 44)):
        periodo["start"] = fecha(m.campo_de(pv1, 44))
    if fecha(m.campo_de(pv1, 45)):
        periodo["end"] = fecha(m.campo_de(pv1, 45))
    if periodo:
        e["period"] = periodo
    if m.campo_de(pv1, 10):
        e["serviceType"] = codigo(SIS + "service-type", m.campo_de(pv1, 10))
    return e


def cantidad(numeros, texto, unidad, sistema_unidad):
    if not NUMERO.match(texto):
        return None
    q = {"value": numeros.valor(texto), "unit": unidad}
    if sistema_unidad == "UCUM":
        q["system"] = "http://unitsofmeasure.org"
    q["code"] = unidad
    return q


def informes(m, numeros):
    salida, actual, n_obr, n_obx = [], None, 0, 0
    for s in m.segs:
        if s.startswith("OBR|"):
            n_obr += 1
            d = {"resourceType": "DiagnosticReport", "id": "d%d" % n_obr}
            ids = [{"type": codigo(SIS + "v2-0203", t), "value": m.comp_de(s, n, 1)} for t, n in (("PLAC", 2), ("FILL", 3)) if m.comp_de(s, n, 1)]
            if ids:
                d["identifier"] = ids
            d["status"] = ESTADO_OBR.get(m.campo_de(s, 25), "unknown")
            d["code"] = concepto(m, s, 4, {"LN": "http://loinc.org"})
            d["subject"] = {"reference": "urn:uuid:p1"}
            if fecha(m.campo_de(s, 7)):
                d["effectiveDateTime"] = fecha(m.campo_de(s, 7))
            if fecha(m.campo_de(s, 22)):
                d["issued"] = fecha(m.campo_de(s, 22))
            d["result"] = []
            actual = d
            salida.append(d)
        elif s.startswith("OBX|"):
            n_obx += 1
            o = {"resourceType": "Observation", "id": "o%d" % n_obx, "status": ESTADO_OBR.get(m.campo_de(s, 11), "unknown"),
                 "code": concepto(m, s, 3, {"LN": "http://loinc.org"}), "subject": {"reference": "urn:uuid:p1"}}
            if fecha(m.campo_de(s, 14)):
                o["effectiveDateTime"] = fecha(m.campo_de(s, 14))
            q = cantidad(numeros, m.campo_de(s, 5), m.comp_de(s, 6, 1), m.comp_de(s, 6, 3)) if m.campo_de(s, 2) == "NM" else None
            if q:
                o["valueQuantity"] = q
            else:
                o["valueString"] = m.campo_de(s, 5)
            if m.campo_de(s, 8):
                o["interpretation"] = [codigo(SIS + "v3-ObservationInterpretation", m.campo_de(s, 8))]
            if m.campo_de(s, 7):
                o["referenceRange"] = [{"text": m.campo_de(s, 7)}]
            if actual is not None:
                actual["result"].append({"reference": "urn:uuid:" + o["id"]})
            salida.append(o)
    return [x for x in salida if x["resourceType"] == "DiagnosticReport"] + [x for x in salida if x["resourceType"] == "Observation"]


def vacunas(m, numeros):
    salida = []
    for i, s in enumerate(m.segs):
        if not s.startswith("RXA|"):
            continue
        v = {"resourceType": "Immunization", "id": "i%d" % (len(salida) + 1),
             "status": "not-done" if m.campo_de(s, 20) == "RE" or m.campo_de(s, 18) else "completed",
             "vaccineCode": concepto(m, s, 5, {"CVX": "http://hl7.org/fhir/sid/cvx"}), "patient": {"reference": "urn:uuid:p1"}}
        if fecha(m.campo_de(s, 3)):
            v["occurrenceDateTime"] = fecha(m.campo_de(s, 3))
        if m.campo_de(s, 15):
            v["lotNumber"] = m.campo_de(s, 15)
        if fecha(m.campo_de(s, 16)):
            v["expirationDate"] = fecha(m.campo_de(s, 16))
        if m.campo_de(s, 6):
            q = cantidad(numeros, m.campo_de(s, 6), m.comp_de(s, 7, 1), m.comp_de(s, 7, 3))
            if q:
                v["doseQuantity"] = q
        rxr = m.segs[i + 1] if i + 1 < len(m.segs) and m.segs[i + 1].startswith("RXR|") else None
        if rxr:
            if m.comp_de(rxr, 1, 1):
                v["route"] = codigo(SIS + "v2-0162", m.comp_de(rxr, 1, 1))
            if m.comp_de(rxr, 2, 1):
                v["site"] = codigo(SIS + "v2-0163", m.comp_de(rxr, 2, 1))
        salida.append(v)
    return salida


def convertir(texto):
    """-> (bundle en texto JSON, None) o (None, motivo)."""
    m = Mensaje(texto)
    msh = m.primero("MSH")
    if msh is None:
        return None, "sin MSH"
    tipo, evento = m.comp_de(msh, 9, 1), m.comp_de(msh, 9, 2)
    if tipo not in ("ADT", "ORU", "VXU"):
        return None, "tipo no soportado: %s" % m.campo_de(msh, 9)
    numeros, recursos = Numeros(), []
    pid = m.primero("PID")
    if pid is not None:
        recursos.append(paciente(m, pid))
    if tipo == "ADT" and m.primero("PV1") is not None:
        recursos.append(encuentro(m, m.primero("PV1"), evento))
    if tipo == "ORU":
        recursos += informes(m, numeros)
    if tipo == "VXU":
        recursos += vacunas(m, numeros)
    bundle = {"resourceType": "Bundle", "type": "collection", "entry": [{"fullUrl": "urn:uuid:" + r["id"], "resource": r} for r in recursos]}
    return numeros.poner(json.dumps(bundle, ensure_ascii=False, indent=1)), None


def main(entrada, salida):
    for f in sorted(x for x in os.listdir(entrada) if x.endswith(".hl7")):
        t0 = time.time()
        base = f[:-4]
        try:
            js, error = convertir(open(os.path.join(entrada, f), encoding="utf-8", errors="replace").read())
        except Exception as ex:                                            # un mensaje que rompe el conversor no para la carpeta
            js, error = None, "%s: %s" % (type(ex).__name__, ex)
        if js is not None:
            open(os.path.join(salida, base + ".json"), "w", encoding="utf-8").write(js + "\n")
        else:
            open(os.path.join(salida, base + ".error"), "w", encoding="utf-8").write(error + "\n")
        print("%s %d ms" % (f, int((time.time() - t0) * 1000)), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
