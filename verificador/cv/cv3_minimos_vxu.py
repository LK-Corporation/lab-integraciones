#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 20, VX3 (vx/diseno-vx-fable.md §10): los pares mínimos de VXU, con la forma de cv/cv3_minimos.py. Cada par es un CASO, que
lleva el disparador del mecanismo, y su CONTROL, igual salvo el disparador; los dos, VXU^V04 v2.5 sintéticos y públicos. Confirmada =
el hallazgo objetivo sale en el caso y no en el control, con el conversor en su caja y el juez de la etapa. Lista aparte de MIN.PARES
(que no cambia). El par de estado arrastrado de LinuxForHealth (VL11) no es un mensaje sino una secuencia: va en SECUENCIAS.

  python3 cv/cv3_minimos_vxu.py escribir <carpeta>                    # los .hl7 de PARES (CR, sin BOM)
  python3 cv/cv3_minimos_vxu.py secuencias <carpeta>                  # VL11: <carpeta>/<id>-caso/ y <id>-control/
  python3 cv/cv3_minimos_vxu.py juzgar <evidencias> <resultado.json>  # <evidencias>/<conversor>/<id>-{caso,control}.json
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.dirname(AQUI)]

MSH = "MSH|^~\\&|REGVAC|CSSYN|REGISTRO|SALUD|20240301090000||VXU^V04^VXU_V04|%s|P|2.5"
PID = "PID|1||VAC0001^^^CSSYN^MR||Prueba^Mateo^^^^^L||20230512|M"


def seg(nombre, campos):
    p = [nombre] + [""] * max(campos)
    for k, v in campos.items():
        p[k] = v
    return "|".join(p).rstrip("|")


def vxu(n, orc=None, rxa=None, rxr=None, obx=(), nk1=None, grupos=None):
    """Un VXU nominal (como la base B01 de bases_vxu.py, con fabricante codificado y sin RXA-9) con cambios por campo; None borra."""
    def junta(base, c):
        d = dict(base)
        for k, v in (c or {}).items():
            if v is None:
                d.pop(k, None)
            else:
                d[k] = v
        return d
    o = {1: "RE", 3: "VX-%s^REGVAC" % n}
    a = {1: "0", 2: "1", 3: "20240301083000", 4: "20240301083000", 5: "03^MMR^CVX", 6: "0.5", 7: "mL^mL^UCUM", 10: "PR01^Ensayo^Ana",
         15: "LOT-%s" % n, 16: "202611", 17: "MSD^Merck^MVX", 20: "CP", 21: "A"}
    r = {1: "IM^Intramuscular^HL70162", 2: "LD^Deltoides izquierdo^HL70163"}
    segs = [MSH % ("VXU-" + n), PID] + ([seg("NK1", {**{1: "1", 2: "Prueba^Lucia^^^^^L", 15: "F", 16: "19900301"}, **nk1})] if nk1 else [])
    for g in grupos or [(orc, rxa, rxr, obx)]:
        go, ga, gr, gx = g
        segs += [seg("ORC", junta(o, go)), seg("RXA", junta(a, ga))]
        if gr is not False:
            segs.append(seg("RXR", junta(r, gr)))
        segs += list(gx)
    return "\r".join(segs)


T_CE = "OBX|1|CE|64994-7^Elegibilidad^LN||ELE^Elegible programa^L||||||F"
T_DT = "OBX|1|DT|29769-7^Fecha de entrega de la hoja^LN||20240301||||||F"
T_NM = "OBX|1|NM|8310-5^Temperatura corporal^LN||38.5|Cel^%s^UCUM|||||F"

# (id, conversor que se espera que lo muestre, (caso, control), (hecho o hechos, subtipo, texto que debe estar en el «que»))
PARES = [
    ("VM01-cvx-system", "microsoft", (vxu("M01c"), vxu("M01k", rxa={5: "03^MMR"})), ("RXA-5", "codigo_mal_mapeado", "system")),
    ("VM02-mvx-system", "microsoft", (vxu("M02c"), vxu("M02k", rxa={17: "MSD^Merck"})), ("RXA-17", "codigo_mal_mapeado", "system")),
    ("VM03-ruta-0162", "microsoft", (vxu("M03c"), vxu("M03k", rxr={1: "JET^Inyector a presion^L"})), ("RXR-1", "codigo_mal_mapeado", "route")),
    ("VM04-sitio-0163", "microsoft", (vxu("M04c"), vxu("M04k", rxr={2: None})), ("RXR-2", "codigo_mal_mapeado", "site")),
    ("VM05-unidad-sin-ce2", "microsoft", (vxu("M05c", rxa={7: "mL^^UCUM"}), vxu("M05k")), ("RXA-7", "dato_perdido", "unit")),
    ("VM06-obx6-sin-ce2", "microsoft", (vxu("M06c", obx=[T_NM % ""]), vxu("M06k", obx=[T_NM % "Cel"])), ("OBX-6", "dato_perdido", "unit")),
    ("VM07-lote-repetido", "microsoft", (vxu("M07c", rxa={15: "LOT-M07c~DIL-M07c"}), vxu("M07k", rxa={15: "LOT-M07k"})),
     ("RXA-15", "valor_distinto", "lotNumber")),
    ("VM08-fabricante-alterno", "microsoft", (vxu("M08c", rxa={17: "MSD^Merck^MVX^MERCK^Merck S.A.^L"}), vxu("M08k")),
     ("RXA-17", "valor_distinto", "Organization.name")),
    ("VM09-telefono-xtn7", "microsoft", (vxu("M09c", nk1={3: "MTH^Madre^HL70063", 5: "^PRN^PH^^^^5551001"}),
                                         vxu("M09k", nk1={3: "MTH^Madre^HL70063", 5: "5551001^PRN^PH"})), ("NK1-5", "dato_perdido", "telecom")),
    ("VM10-relacion-grd", "microsoft", (vxu("M10c", nk1={3: "GRD^Tutora^HL70063"}), vxu("M10k", nk1={3: "MTH^Madre^HL70063"})),
     ("NK1-3", "codigo_mal_mapeado", "relationship")),
    ("VM11-obx-sin-partof", "microsoft", (vxu("M11c", obx=[T_CE]), vxu("M11k", obx=[T_DT])), ("OBX-3", "dato_perdido", "partOf")),
    ("VM12-dos-indicaciones", "microsoft", (vxu("M12c", rxa={19: "DM^Diabetes^L~ASM^Asma^L"}), vxu("M12k", rxa={19: "DM^Diabetes^L"})),
     ("RXA-19", "dato_perdido", "reasonCode")),
    ("VM13-grupos-sin-orc3", "microsoft",
     (vxu("M13c", grupos=[({3: None}, {5: "88^Gripe^CVX", 15: "LOT-M13A"}, None, ()), ({3: None}, {5: "09^Td^CVX", 15: "LOT-M13B"}, None, ())]),
      vxu("M13k", grupos=[({3: "VX-M13A^REGVAC"}, {5: "88^Gripe^CVX", 15: "LOT-M13A"}, None, ()),
                          ({3: "VX-M13B^REGVAC"}, {5: "09^Td^CVX", 15: "LOT-M13B"}, None, ())])),
     (("RXA-5", "RXA(2)-5"), "recurso_ausente", "Immunization")),
    # de las muestras públicas (VX3): la dosis «.5» (misma causa que M-24 de CV3) y el status por RXA-18 en vez de RXA-20
    ("VM14-dosis-punto-inicial", "microsoft", (vxu("M14c", rxa={6: ".5"}), vxu("M14k", rxa={6: "0.5"})),
     ("RXA-6", "valor_distinto", "doseQuantity.value")),
    ("VM15-re-sin-rxa18", "microsoft", (vxu("M15c", rxa={20: "RE"}), vxu("M15k", rxa={20: "RE", 18: "REL^Motivo religioso^L"})),
     ("RXA-20", "codigo_mal_mapeado", "status")),
    ("VL01-orc3-perdido", "linuxforhealth", (vxu("L01c"), vxu("L01k", orc={3: None})), ("ORC-3", "dato_perdido", "identifier")),
    ("VL02-ruta-v2-0162", "linuxforhealth", (vxu("L02c"), vxu("L02k", rxr={1: "JET^Inyector a presion^L"})), ("RXR-1", "codigo_mal_mapeado", "route")),
    ("VL03-unidad-ce1", "linuxforhealth", (vxu("L03c", rxa={7: "mL^mililitro^UCUM"}), vxu("L03k", rxa={7: "mL^^UCUM"})),
     ("RXA-7", "valor_distinto", "unit")),
    ("VL04-rxa21-d", "linuxforhealth", (vxu("L04c", rxa={21: "D"}), vxu("L04k")), ("RXA-21", "valor_distinto", "status")),
    ("VL05-recorded-con-u", "linuxforhealth", (vxu("L05c", orc={9: "20240301084000"}, rxa={21: "U", 22: "20240301084500"}),
                                               vxu("L05k", orc={9: "20240301084000"}, rxa={22: "20240301084500"})),
     ("ORC-9", "valor_distinto", "recorded")),
    ("VL06-dos-rxa10", "linuxforhealth", (vxu("L06c", rxa={10: "PR01^Ensayo^Ana~PR02^Muestra^Jorge"}), vxu("L06k")),
     ("RXA-10", "dato_perdido", "performer")),
    ("VL07-dos-indicaciones", "linuxforhealth", (vxu("L07c", rxa={19: "DM^Diabetes^L~ASM^Asma^L"}), vxu("L07k", rxa={19: "DM^Diabetes^L"})),
     ("RXA-19", "dato_perdido", "reasonCode")),
    ("VL08-pa-subpotente", "linuxforhealth", (vxu("L08c", rxa={20: "PA"}), vxu("L08k")), ("RXA", "dato_inventado", "isSubpotent")),
    ("VL09-nk1-perdido", "linuxforhealth", (vxu("L09c", nk1={3: "MTH^Madre^HL70063"}), vxu("L09k")), ("NK1-2", "recurso_ausente", "RelatedPerson")),
    ("VL10-obx-nm-perdido", "linuxforhealth", (vxu("L10c", obx=[T_NM % "Cel"]), vxu("L10k")), ("OBX-3", "recurso_ausente", "Observation")),
]
# VL11 (estado arrastrado): el caso es un proceso que convierte primero un VXU con RXA-17 sin código y después el nominal; el control,
# el nominal solo. Objetivo: el nominal sale sin manufacturer en el caso y con él en el control.
SECUENCIAS = [("VL11-estado-fabricante", "linuxforhealth",
               ([("L11a", vxu("L11a", rxa={17: "^Laboratorio Sintetico^"})), ("L11b", vxu("L11b"))], [("L11b", vxu("L11b"))]),
               ("RXA-17", "dato_perdido", "manufacturer"), "L11b")]


def escribir(carpeta):
    os.makedirs(carpeta, exist_ok=True)
    for pid, _, (caso, control), _ in PARES:
        for sufijo, texto in (("caso", caso), ("control", control)):
            with open(os.path.join(carpeta, "%s-%s.hl7" % (pid, sufijo)), "w", encoding="utf-8", newline="") as g:
                g.write(texto + "\r")
    print("%d pares en %s" % (len(PARES), carpeta))


def secuencias(carpeta):
    for pid, _, (caso, control), _, _ in SECUENCIAS:
        for sufijo, msgs in (("caso", caso), ("control", control)):
            d = os.path.join(carpeta, "%s-%s" % (pid, sufijo))
            os.makedirs(d, exist_ok=True)
            for k, (nombre, texto) in enumerate(msgs, 1):
                with open(os.path.join(d, "%d-%s.hl7" % (k, nombre)), "w", encoding="utf-8", newline="") as g:
                    g.write(texto + "\r")
    print("%d secuencias en %s" % (len(SECUENCIAS), carpeta))


def _sale(e, hecho, subtipo, texto):
    import verificador as V
    r = V.verificar(e)
    hs = [h for h in r["hallazgos"] if h["cuenta"]]
    hechos = hecho if isinstance(hecho, tuple) else (hecho,)
    vistos = [h for h in hs if h["hecho"] in hechos and subtipo in h["subtipo"].split("+") and any(texto in q for q in h["que"])]
    return {"sale": bool(vistos), "estado": e["conversion"]["salida"]["estado"], "categoria": r["veredicto"]["categoria"],
            "que": [q for h in vistos for q in h["que"]][:2]}


def juzgar(evidencias, resultado):
    """La regla de cv3_minimos.juzgar: sale el hecho objetivo (con su subtipo y su texto) en el caso y no en el control."""
    import mcp_verificador as M
    filas = []
    for pid, conv, _, (hecho, subtipo, texto) in PARES:
        fila = {"id": pid, "conversor": conv, "objetivo": {"hecho": hecho, "subtipo": subtipo, "texto": texto}}
        for cv in ("microsoft", "linuxforhealth"):
            for sufijo in ("caso", "control"):
                f = os.path.join(evidencias, cv, "%s-%s.json" % (pid, sufijo))
                fila.setdefault(cv, {})[sufijo] = _sale(json.load(open(f, encoding="utf-8")), hecho, subtipo, texto) if os.path.exists(f) else None
        c = fila[conv]
        fila["confirmada"] = bool(c["caso"] and c["control"] and c["caso"]["sale"] and not c["control"]["sale"])
        filas.append(fila)
    for pid, conv, _, (hecho, subtipo, texto), objetivo in SECUENCIAS:
        fila = {"id": pid, "conversor": conv, "objetivo": {"hecho": hecho, "subtipo": subtipo, "texto": texto, "mensaje": objetivo},
                "secuencia": True}
        for sufijo in ("caso", "control"):
            f = os.path.join(evidencias, conv, "%s-%s" % (pid, sufijo), "%s.json" % objetivo)
            fila.setdefault(conv, {})[sufijo] = _sale(json.load(open(f, encoding="utf-8")), hecho, subtipo, texto) if os.path.exists(f) else None
        c = fila[conv]
        fila["confirmada"] = bool(c["caso"] and c["control"] and c["caso"]["sale"] and not c["control"]["sale"])
        filas.append(fila)
    res = {"juez": M._version()["huella"], "pares": filas, "confirmadas": sum(1 for x in filas if x["confirmada"]), "de": len(filas)}
    json.dump(res, open(resultado, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for x in filas:
        c = x[x["conversor"]]
        otro = "linuxforhealth" if x["conversor"] == "microsoft" else "microsoft"
        oc = (x.get(otro) or {}).get("caso")
        print("%-26s %-15s %-11s caso=%s control=%s | el otro: caso=%s | %s" % (
            x["id"], x["conversor"], "CONFIRMADA" if x["confirmada"] else "no", (c["caso"] or {}).get("sale"), (c["control"] or {}).get("sale"),
            oc["sale"] if oc else "-", ((c["caso"] or {}).get("que") or [(c["caso"] or {}).get("estado")])[0]))
    print("confirmadas %d de %d; juez %s" % (res["confirmadas"], res["de"], res["juez"][:12]))


if __name__ == "__main__":
    if sys.argv[1] == "escribir":
        escribir(sys.argv[2])
    elif sys.argv[1] == "secuencias":
        secuencias(sys.argv[2])
    else:
        a, b = sys.argv[2], sys.argv[3]
        sys.argv = ["x", "--silencio"]
        juzgar(a, b)
