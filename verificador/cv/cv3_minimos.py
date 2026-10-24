#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CV3: confirma cada discrepancia `nueva` con un par de mensajes mínimos, públicos y sintéticos (v2.5): el CASO, que lleva solo
el disparador del mecanismo, y su CONTROL, igual salvo el disparador. Confirmada = el hallazgo objetivo sale en el caso y no en
el control, con el conversor en su caja y el juez de CV3.

  python3 cv/cv3_minimos.py escribir <carpeta>                      # los .hl7 (CR, sin BOM)
  python3 cv/cv3_minimos.py juzgar <evidencias> <resultado.json>    # tras cv/correr_conversor.py con cada conversor
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

MSH = "MSH|^~\\&|LAB|HOSP|DEST|HIS|20260101080000+0100||%s|%s|P|2.5"


def adt(n, pid8="F", pid11="", pid16="", pv1_2="I", pv1_3="UCI^3^1^HOSP", pv1_8="", pv1_10="", extra=(), evento="A01", pid=None, pv1=None):
    p = {1: "1", 3: "P0001^^^HOSP^MR", 5: "PRUEBA^ANA", 7: "19800101", 8: pid8, 11: pid11, 16: pid16}
    p.update(pid or {})
    v = {1: "1", 2: pv1_2, 3: pv1_3, 8: pv1_8, 10: pv1_10}
    v.update(pv1 or {})
    return "\r".join([MSH % ("ADT^%s^ADT_%s" % (evento, evento), n), "EVN|%s|20260101080000+0100" % evento,
                      campos("PID", p).rstrip("|"), campos("PV1", v).rstrip("|")] + list(extra))


def campos(nombre, d):
    """Segmento con los campos {n: valor}; los que faltan, vacíos."""
    return "|".join([nombre] + [d.get(i, "") for i in range(1, max(d) + 1)])


def obx(i, tipo, codigo, valor, unidades="", estado="F", nte=0):
    s = [campos("OBX", {1: str(i), 2: tipo, 3: codigo, 5: valor, 6: unidades, 11: estado, 14: "20260101080000+0100"})]
    return s + ["NTE|%d|L|Nota %d de OBX %d" % (k, k, i) for k in range(1, nte + 1)]


def oru(n, obxs, pid=True, obr25="F", obr_nte=False):
    segs = [MSH % ("ORU^R01^ORU_R01", n)]
    if pid:
        segs.append("PID|1||P0001^^^HOSP^MR||PRUEBA^ANA||19800101|F")
    segs.append(campos("OBR", {1: "1", 2: "PL1", 3: "FL1", 4: "24323-8^Panel basico^LN", 7: "20260101070000+0100",
                               22: "20260101090000+0100", 25: obr25}))
    if obr_nte:
        segs.append("NTE|1|L|Nota de la orden")
    for o in obxs:
        segs += o
    return "\r".join(segs)


GLU = "2345-7^Glucosa^LN"
CRE = "2160-0^Creatinina^LN"
COM = "8251-1^Comentario^LN"
MG = "mg/dL^mg/dL^UCUM"

# (id, conversor que se espera que lo muestre, (caso, control), (hecho, subtipo, texto que debe estar en el «que»))
PARES = [
    ("M01-nm-punto-inicial", "microsoft", (oru("M01c", [obx(1, "NM", GLU, ".5", MG)]), oru("M01k", [obx(1, "NM", GLU, "0.5", MG)])),
     ("OBX-5", "valor_distinto", "valueQuantity.value")),
    ("M02-genero-fuera-de-tabla", "microsoft", (adt("M02c", pid8="Z"), adt("M02k", pid8="F")), ("PID-8", "fhir_invalido", "gender")),
    # el corpus lo mostró en A02; en A01 Microsoft pasa GT1 a la plantilla de Patient y no llega a esa rama (sonda de la 1.ª ronda)
    ("M03-pda-sin-muerte", "microsoft", (adt("M03c", extra=['PDA|""'], evento="A02"), adt("M03k", evento="A02")),
     ("PID-30", "dato_inventado", "deceasedBoolean")),
    ("M03b-pda-en-a01", "microsoft", (adt("M03bc", extra=['PDA|""']), adt("M03bk")), ("PID-30", "dato_inventado", "deceasedBoolean")),
    ("M04-pv1-8-repetido", "microsoft", (adt("M04c", pv1_8="D21^Uno^Ana~D22^Dos^Eva"), adt("M04k", pv1_8="D21^Uno^Ana")),
     ("PV1-8", "dato_perdido", "participant")),
    ("M05-clase-b", "microsoft", (adt("M05c", pv1_2="B"), adt("M05k", pv1_2="I")), ("PV1-2", "codigo_mal_mapeado", "class")),
    # 1.ª ronda: con dos NTE y con una se perdía igual; el disparador es la NTE tras el OBX, no su número
    ("M06-obx-tras-nte", "microsoft", (oru("M06c", [obx(1, "NM", GLU, "95", MG, nte=1), obx(2, "NM", CRE, "1.1", MG)]),
                                       oru("M06k", [obx(1, "NM", GLU, "95", MG), obx(2, "NM", CRE, "1.1", MG)])),
     ("OBX(2)-3", "recurso_ausente", "Observation")),
    ("M06b-dos-nte", "microsoft", (oru("M06bc", [obx(1, "NM", GLU, "95", MG, nte=2), obx(2, "NM", CRE, "1.1", MG)]),
                                   oru("M06bk", [obx(1, "NM", GLU, "95", MG), obx(2, "NM", CRE, "1.1", MG)])),
     ("OBX(2)-3", "recurso_ausente", "Observation")),
    ("M06c-nte-al-final", "microsoft", (oru("M06cc", [obx(1, "NM", GLU, "95", MG), obx(2, "NM", CRE, "1.1", MG, nte=1)]),
                                        oru("M06ck", [obx(1, "NM", GLU, "95", MG), obx(2, "NM", CRE, "1.1", MG)])),
     ("OBX(2)-3", "recurso_ausente", "Observation")),
    ("M06d-tres-obx", "microsoft", (oru("M06dc", [obx(1, "NM", GLU, "95", MG, nte=1), obx(2, "NM", CRE, "1.1", MG), obx(3, "ST", COM, "fin")]),
                                    oru("M06dk", [obx(1, "NM", GLU, "95", MG), obx(2, "NM", CRE, "1.1", MG), obx(3, "ST", COM, "fin")])),
     ("OBX(2)-3", "recurso_ausente", "Observation")),
    # el juez de CV4 pone el hecho «PID» (el segmento que falta); el de CV3 ponía «PID-3»
    ("M07-oru-sin-pid", "microsoft", (oru("M07c", [obx(1, "NM", GLU, "95", MG)], pid=False), oru("M07k", [obx(1, "NM", GLU, "95", MG)])),
     (("PID-3", "PID"), "referencia_rota", "subject")),
    ("M08-estado-civil-t", "microsoft", (adt("M08c", pid16="T"), adt("M08k", pid16="M")), ("PID-16", "dato_perdido", "maritalStatus")),
    ("M10-pl9-descripcion", "microsoft", (adt("M10c", pv1_3="UCI^3^1^HOSP^^^^^Box 3"), adt("M10k")),
     ("PV1-3", "dato_perdido", "PL.9")),
    ("M09-ft-br", "microsoft", (oru("M09c", [obx(1, "FT", COM, "Primera linea\\.br\\Segunda linea")]),
                                oru("M09k", [obx(1, "FT", COM, "Primera linea Segunda linea")])),
     ("OBX-5", "valor_distinto", "valueString")),
    ("L01-sin-location", "linuxforhealth", (adt("L01c"), adt("L01k", pv1_3="")), ("PV1-3", "dato_perdido", "location")),
    ("L02-estado-civil-a", "linuxforhealth", (adt("L02c", pid16="A"), adt("L02k", pid16="M")), ("PID-16", "codigo_mal_mapeado", "maritalStatus")),
    ("L03-pv1-10-med", "linuxforhealth", (adt("L03c", pv1_10="MED"), adt("L03k")), ("PV1-10", "codigo_mal_mapeado", "serviceType")),
    ("L04-sad-2-3", "linuxforhealth", (adt("L04c", pid11="C/ Real 5&Piso 3&Puerta B^Esc 2^MADRID^^28001"),
                                       adt("L04k", pid11="C/ Real 5^Esc 2^MADRID^^28001")), ("PID-11", "valor_distinto", "address.line")),
    ("L05-genero-n", "linuxforhealth", (adt("L05c", pid8="N"), adt("L05k", pid8="F")), ("PID-8", "valor_distinto", "gender")),
    ("L06-obx-sin-tipo", "linuxforhealth", (oru("L06c", [obx(1, "", GLU, "", estado="X")]), oru("L06k", [obx(1, "NM", GLU, "", estado="X")])),
     ("OBX-3", "recurso_ausente", "Observation")),
    ("L07-ft", "linuxforhealth", (oru("L07c", [obx(1, "FT", COM, "Texto con formato")]), oru("L07k", [obx(1, "ST", COM, "Texto con formato")])),
     ("OBX-5", "dato_perdido", "valueString")),
    ("L08-tm", "linuxforhealth", (oru("L08c", [obx(1, "TM", "8302-2^Hora^LN", "0715")]), oru("L08k", [obx(1, "ST", "8302-2^Hora^LN", "0715")])),
     ("OBX-5", "dato_perdido", "valueTime")),
    ("L09-obx-11-d", "linuxforhealth", (oru("L09c", [obx(1, "NM", GLU, "95", MG, estado="D")]), oru("L09k", [obx(1, "NM", GLU, "95", MG)])),
     ("OBX-11", "codigo_mal_mapeado", "status")),
    ("L10-obr-25-i", "linuxforhealth", (oru("L10c", [obx(1, "NM", GLU, "95", MG)], obr25="I"), oru("L10k", [obx(1, "NM", GLU, "95", MG)])),
     ("OBR-25", "codigo_mal_mapeado", "status")),
    ("L11-sn-rango", "linuxforhealth", (oru("L11c", [obx(1, "SN", GLU, "^1^-^5", MG)]), oru("L11k", [obx(1, "SN", GLU, "<^5", MG)])),
     ("OBX-5", "valor_distinto", "SN")),
    ("L12-sn-distinto", "linuxforhealth", (oru("L12c", [obx(1, "SN", GLU, "<>^5", MG)]), oru("L12k", [obx(1, "SN", GLU, "<^5", MG)])),
     ("OBX-5", "valor_distinto", "SN")),
    # de las muestras públicas de los proyectos (CV3, muestras en alcance)
    ("L13-pv1-52", "linuxforhealth", (adt("L13c", pv1={52: "D52^Otro^Eva"}), adt("L13k")), ("PV1-52", "dato_perdido", "participant")),
    ("L14-xpn-6-titulo", "linuxforhealth", (adt("L14c", pid={5: "PRUEBA^ANA^^^^MD"}), adt("L14k")), ("PID-5", "dato_perdido", "suffix")),
    # 1.ª ronda: con el número en XTN.7 LinuxForHealth escribe «404 2808» y el juez busca «4042808» literal: formato, Q-CV-D-15.
    # Lo que la guía sí fija es la preferencia: XTN.1 solo si XTN.7 y XTN.12 están vacíos (CM datatype-xtn-to-contactpoint).
    ("L15-xtn-12", "linuxforhealth", (adt("L15c", pid={13: "5550000^PRN^PH^^^^^^^^^5551111"}), adt("L15k", pid={13: "5551111^PRN^PH"})),
     ("PID-13", "dato_perdido", "telecom")),
    ("L16-cx-4-solo-nombre", "linuxforhealth", (adt("L16c", pid={3: "P0001^^^NIST MPI^MR"}), adt("L16k", pid={3: "P0001^^^^MR"})),
     ("PID-3", "dato_perdido", "CX.4")),
    ("L17-pid-30-no", "linuxforhealth", (adt("L17c", pid={30: "NO"}), adt("L17k", pid={30: "N"})), ("PID-30", "valor_imposible_convertido", "deceased")),
    ("L18-unidad-cwe-2", "linuxforhealth", (oru("L18c", [obx(1, "NM", GLU, "95", "mg/dL^miligramos por decilitro^UCUM")]),
                                            oru("L18k", [obx(1, "NM", GLU, "95", "mg/dL^^UCUM")])), ("OBX-6", "valor_distinto", "unit")),
    # rechazos: no son de las ocho clases (S-CV-5); se reproducen para la tabla, no para la regla de portfolio
    ("R01-nulo-en-dtm", "microsoft", (adt("R01c", extra=['ACC|""']), adt("R01k", extra=["ACC|20260101070000+0100"])), ("MSH-9", "error", "")),
    ("R02-nm-cero-inicial", "microsoft", (oru("R02c", [obx(1, "NM", CRE, "01.20", MG)]), oru("R02k", [obx(1, "NM", CRE, "1.20", MG)])),
     ("MSH-9", "error", "")),
]


def escribir(carpeta):
    os.makedirs(carpeta, exist_ok=True)
    for pid, _, (caso, control), _ in PARES:
        for sufijo, texto in (("caso", caso), ("control", control)):
            with open(os.path.join(carpeta, "%s-%s.hl7" % (pid, sufijo)), "w", encoding="utf-8", newline="") as g:
                g.write(texto + "\r")
    print("%d pares en %s" % (len(PARES), carpeta))


def juzgar(evidencias, resultado):
    import juzgar_cv2 as J
    import mcp_verificador as M
    filas = []
    for pid, conv, _, (hecho, subtipo, texto) in PARES:
        fila = {"id": pid, "conversor": conv, "objetivo": {"hecho": hecho, "subtipo": subtipo, "texto": texto}}
        for sufijo in ("caso", "control"):
            for cv in ("microsoft", "linuxforhealth"):
                f = os.path.join(evidencias, cv, "%s-%s.json" % (pid, sufijo))
                e = json.load(open(f, encoding="utf-8"))
                r = J.juzgar(e)
                hs = [h for h in r["hallazgos"] if h["cuenta"]]
                if subtipo == "error":
                    sale = e["conversion"]["salida"]["estado"] != "bundle"
                    vistos = [h for h in hs if h["clase"] == "rechazo"]
                else:
                    hechos = hecho if isinstance(hecho, tuple) else (hecho,)
                    vistos = [h for h in hs if h["hecho"] in hechos and any(texto in q for q in h["que"])]
                    sale = bool(vistos)
                fila.setdefault(cv, {})[sufijo] = {"sale": sale, "estado": e["conversion"]["salida"]["estado"],
                                                   "categoria": r["veredicto"]["categoria"],
                                                   "subtipos": sorted({h["subtipo"] for h in vistos}),
                                                   "que": [q for h in vistos for q in h["que"]][:2]}
        c = fila[conv]
        fila["confirmada"] = c["caso"]["sale"] and not c["control"]["sale"]
        filas.append(fila)
    res = {"juez": M._version()["huella"], "pares": filas,
           "confirmadas": sum(1 for x in filas if x["confirmada"]), "de": len(filas)}
    json.dump(res, open(resultado, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for x in filas:
        c = x[x["conversor"]]
        otro = "linuxforhealth" if x["conversor"] == "microsoft" else "microsoft"
        print("%-26s %-15s %-11s caso=%s control=%s %s | el otro: caso=%s | %s" % (
            x["id"], x["conversor"], "CONFIRMADA" if x["confirmada"] else "no", c["caso"]["sale"], c["control"]["sale"],
            c["caso"]["subtipos"], x[otro]["caso"]["sale"], (c["caso"]["que"] or [c["caso"]["estado"]])[0][:120]))
    print("confirmadas %d de %d; juez %s" % (res["confirmadas"], res["de"], res["juez"][:12]))


if __name__ == "__main__":
    sys.argv_guardado = sys.argv
    if sys.argv[1] == "escribir":
        escribir(sys.argv[2])
    else:
        a, b = sys.argv[2], sys.argv[3]
        sys.argv = ["x", "--silencio"]
        juzgar(a, b)
