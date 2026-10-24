#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CV-pre, sonda E-CV-1 (ANTES-ETAPA-CONVERSORES.md): ¿cuánto de lo que proyecta el verificador coincide con la guía
v2-to-FHIR? Solo lectura: lee las hojas de la guía (cv/guia/, HL7/v2-to-fhir) y las tablas del juez, sin tocarlas.

Por cada fila de la proyección del juez (almacen_adt.HECHO: Patient y Encounter; almacen_oru.TABLA: Observation y
DiagnosticReport), una clase:
  alineado        la guía saca ese elemento de ese mismo campo;
  otro_campo      la guía saca ese elemento, pero de otro campo;
  sin_mapeo       la guía no saca ese elemento de ningún campo de esa hoja;
  sin_campo       la fila del juez no viene de un campo (resourceType, una constante).
Y, aparte, de dónde sale el VALOR esperado: en ADT, las citas del contrato del canónico (mapeador_adt.CONTRATO_CANONICO) para
ese campo; en ORU, si la fila cita el mapeo oficial [M].
  cd fase12 && python3 cv/cv_pre.py        -> cv/CV-PRE-E1.json y el resumen en pantalla"""
import csv
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(AQUI)
sys.path.insert(0, FASE)
import almacen_adt as AA  # noqa: E402
import almacen_oru as AO  # noqa: E402
import mapeador_adt as MA  # noqa: E402

GUIA = os.path.join(AQUI, "guia")
HOJAS = {"Patient": ["PID_Patient.csv"], "Encounter": ["PV1_Encounter.csv", "PID_Patient.csv"],
         "Observation": ["OBX_Observation.csv"], "DiagnosticReport": ["OBR_DiagnosticReport.csv"]}


def hoja(nombre):
    """[(campo v2, elemento FHIR normalizado, atributo tal cual, tipo de datos, vocabulario, condición)] de una hoja."""
    filas, campo = [], None
    with open(os.path.join(GUIA, nombre), encoding="utf-8") as f:
        for r in list(csv.reader(f))[2:]:
            r = r + [""] * 19
            if re.match(r"^[A-Z0-9]{3}-\d+", r[1].strip()):
                campo = r[1].strip()
            atr = r[9].strip()
            if not campo or not atr:
                continue
            filas.append((campo, norm(atr), atr, r[14].strip(), r[15].strip(), r[6].strip() or r[8].strip()))
    return filas


POLIMORFOS = ("value", "effective", "onset", "multipleBirth")


def norm(ruta):
    """El elemento de primer nivel: identifier[1] -> identifier; location[1].location(Location) -> location;
    code.coding[1].code -> code; «identifier[] PLAC» -> identifier; los polimórficos (valueQuantity, value[x], effective…)
    se agrupan en su raíz. deceased no, porque la guía y el juez separan deceasedDateTime (PID-29) y deceasedBoolean (PID-30)."""
    m = re.match(r"\s*([A-Za-z]+)", re.sub(r"\(.*?\)", "", ruta))
    e = m.group(1) if m else ruta.strip()
    return next((p for p in POLIMORFOS if e.startswith(p)), e)


def base(campo):
    m = re.match(r"([A-Z0-9]{3}-\d+)", campo or "")
    return m.group(1) if m else None


def clase(tipo, elemento, campo):
    if not base(campo):
        return "sin_campo", []
    if elemento == "subject":                      # la guía resuelve la referencia en la hoja del mensaje, no en la del segmento
        return "referencia", []
    filas = [x for h in HOJAS[tipo] for x in hoja(h)]
    mismo = [x for x in filas if x[1] == elemento]
    if any(x[0] == base(campo) for x in mismo):
        return "alineado", [x for x in mismo if x[0] == base(campo)]
    if mismo:
        return "otro_campo", mismo
    return "sin_mapeo", []


def origen_valor_adt(campo):
    """Citas del contrato del canónico para las filas que salen de ese campo."""
    citas = [c for _, _, o, _, _, c in MA.CONTRATO_CANONICO if base(o) == base(campo)]
    k = {"guia_o_norma": 0, "decision_lab": 0, "sin_cita": 0}
    for c in citas:
        if not c:
            k["sin_cita"] += 1
        elif re.search(r"\bS\d+|D-ADT|DV-|AMB-", c):
            k["decision_lab"] += 1
        else:
            k["guia_o_norma"] += 1
    return k


def main():
    out = []
    for tipo, d in AA.HECHO.items():
        for ruta, campo in d.items():
            c, ig = clase(tipo, norm(ruta), campo)
            out.append({"recurso": tipo, "elemento": ruta, "campo": campo, "clase": c, "valor": origen_valor_adt(campo),
                        "guia": [{"campo": x[0], "atributo": x[2], "tipo": x[3], "vocabulario": x[4], "condicion": x[5]} for x in ig]})
    for t in AO.TABLA:
        tipo, ruta, campo = t["recurso"], t["elemento"], t["hecho"]
        if tipo not in HOJAS:
            continue
        c, ig = clase(tipo, norm(ruta), campo)
        out.append({"recurso": tipo, "elemento": ruta, "campo": campo, "clase": c,
                    "valor": {"cita_M": any(x.startswith("[M") for x in t["citas"]), "citas": t["citas"]},
                    "guia": [{"campo": x[0], "atributo": x[2], "tipo": x[3], "vocabulario": x[4], "condicion": x[5]} for x in ig]})
    json.dump(out, open(os.path.join(AQUI, "CV-PRE-E1.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for fam, tipos in (("ADT", ("Patient", "Encounter")), ("ORU", ("Observation", "DiagnosticReport"))):
        fs = [x for x in out if x["recurso"] in tipos]
        cuenta = {k: sum(1 for x in fs if x["clase"] == k) for k in ("alineado", "otro_campo", "sin_mapeo", "sin_campo",
                                                                     "referencia")}
        con_campo = len(fs) - cuenta["sin_campo"] - cuenta["referencia"]
        print("%s: %d filas; %s; alineado %d de %d con campo (%.0f %%)" % (fam, len(fs), cuenta, cuenta["alineado"], con_campo,
                                                                          100.0 * cuenta["alineado"] / max(con_campo, 1)))
        for x in fs:
            if x["clase"] in ("otro_campo", "sin_mapeo"):
                print("   %-9s %-16s %-36s %-10s guía: %s" % (x["clase"], x["recurso"], x["elemento"][:36], x["campo"],
                                                            ", ".join(sorted({g["campo"] for g in x["guia"]})) or "—"))
    adt = [x for x in out if x["recurso"] in ("Patient", "Encounter") and x["clase"] not in ("sin_campo", "referencia")]
    tot = {k: sum(x["valor"][k] for x in adt) for k in ("guia_o_norma", "decision_lab", "sin_cita")}
    print("ADT, valor esperado (filas del contrato de esos campos): %s" % tot)
    oru = [x for x in out if x["recurso"] in ("Observation", "DiagnosticReport")]
    print("ORU, filas que citan el mapeo oficial [M]: %d de %d" % (sum(1 for x in oru if x["valor"]["cita_M"]), len(oru)))


if __name__ == "__main__":
    main()
