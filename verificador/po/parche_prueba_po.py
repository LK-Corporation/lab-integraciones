#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 41: las pruebas del arreglo del juez, antes que el arreglo (po/diseno-po-fable.md §3, con po/decision-jev-po.md).

  python3 po/parche_prueba_po.py [<carpeta>]     (por omisión, la de este laboratorio)

- prueba_conversion.py: P-CV-35 (la conducta: la Observation de PD1-7 en un ORU) y P-CV-36 (lo que el juez dice de sí mismo); el
  control de ORU de P-CV-33 pasa a PD1-7 vacío; P-CV-34 busca la entrada de la etapa 40 donde esté;
- prueba_conversion_vxu.py (P-VX-20) y prueba_conversion_mdm.py (P-MD-24): el perfil de ORU con 17 filas;
- prueba_conversion_mdm.py (P-MD-25 d): la huella de INFO, medida sobre una copia con po/parche_juez_po.py aplicado.
Cada sustitución tiene que darse una sola vez; si no, no se escribe nada. Conserva los finales de línea."""
import os
import sys

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

P35 = '''

# ---------------------------------------------------------------------------- etapa 41: la Observation de PD1-7 en un ORU
def oru_fuera(m, codigo="F9"):
    """El ORU con un OBX antes del primer OBR: fuera de ORDER_OBSERVATION (L-CV-7)."""
    s = m.split("\\r")
    k = next(i for i, x in enumerate(s) if x.startswith("OBR|"))
    return "\\r".join(s[:k] + [seg("OBX", {1: "1", 2: "ST", 3: "%s^Fuera^LN" % codigo, 5: "x", 11: "F"})] + s[k:])


def obs_fuera(i="of", codigo="F9"):
    return {"resourceType": "Observation", "id": i, "status": "final", "code": cc("loinc", codigo), "subject": {"reference": "urn:uuid:p1"},
            "valueString": "x"}


def v28(m):
    return m.replace("|P|2.5\\r", "|P|2.8\\r", 1)


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
'''

CV = [
    ("P-CV-35 y P-CV-36", "\n\nPRUEBAS = [p01,", P35.rstrip("\n") + "\n\n\nPRUEBAS = [p01,"),
    ("la lista", "p30, p31, p32, p33, p34]", "p30, p31, p32, p33, p34, p35, p36]"),
    ("P-CV-33: el control de ORU con PD1-7 vacío",
     '''    mira("control ORU: con PD1, la Observation de más sigue inventada",
         ("fidelidad", "recurso_inventado", "OBX") in cuentan(j(ev(con_pd1(oru_msg()), oru_bundle([pac_oru(), dr(), obs1(), obs2(), obs_pd1()]),''',
     '''    mira("control ORU con PD1 y PD1-7 vacío: la Observation de más sigue inventada (con PD1-7, P-CV-35)",
         ("fidelidad", "recurso_inventado", "OBX") in cuentan(j(ev(con_pd1(oru_msg(), ""), oru_bundle([pac_oru(), dr(), obs1(), obs2(), obs_pd1()]),'''),
    ("P-CV-34: la entrada de la etapa 40, donde esté",
     '''    mira("la versión del servidor: la primera entrada, la de la etapa 40 con L-CV-18; la segunda, la de la 37 con L-CV-17",
         (entradas[0].startswith("etapa 40"), "L-CV-18" in entradas[0], len(entradas) > 1 and entradas[1].startswith("etapa 37"),
          len(entradas) > 1 and "L-CV-17" in entradas[1]), (True, True, True, True))''',
     '''    i40 = next((i for i, e in enumerate(entradas) if e.startswith("etapa 40")), None)    # desde la 41, la segunda (P-CV-36)
    mira("la versión del servidor: la entrada de la etapa 40 con L-CV-18, y tras ella la de la 37 con L-CV-17",
         (i40 is not None, i40 is not None and "L-CV-18" in entradas[i40],
          i40 is not None and len(entradas) > i40 + 1 and entradas[i40 + 1].startswith("etapa 37") and "L-CV-17" in entradas[i40 + 1]),
         (True, True, True))'''),
]
VX = [("P-VX-20: el perfil de ORU con la fila de PD1-7",
       '(len(CV.PERFIL_GUIA_ADT), len(CV.PERFIL_GUIA_ORU)), (23, 16))  # etapa 37: L-CV-17; etapa 40: PD1-7',
       '(len(CV.PERFIL_GUIA_ADT), len(CV.PERFIL_GUIA_ORU)), (23, 17))  # etapa 37: L-CV-17; etapas 40 y 41: PD1-7')]
MD = [("P-MD-24: el perfil de ORU con la fila de PD1-7",
       'len(M.t_tabla({"tabla": "perfil_guia_vxu"})[0]["entradas"])), (23, 16, 27))   # etapa 40: la fila de PD1-7',
       'len(M.t_tabla({"tabla": "perfil_guia_vxu"})[0]["entradas"])), (23, 17, 27))   # etapas 40 y 41: las filas de PD1-7'),
      ("P-MD-25 d: INFO de la etapa 41",
       '''# vez, por el texto de L-CV-18 (antes, 4fc316780b5e8ded).
ANTES = {"mdm": "75ab855348d66163", "C": "cfd33a3662852137", "INFO": "ad4d46c08f6702a3",''',
       '''# vez, por el texto de L-CV-18 (antes, 4fc316780b5e8ded). Etapa 41: INFO, por S-CV-4 y L-CV-18 (antes, ad4d46c08f6702a3).
ANTES = {"mdm": "75ab855348d66163", "C": "cfd33a3662852137", "INFO": "503c6bd6735c9736",''')]


def aplica(p, cambios):
    t = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in t else "\n"
    hechos = []
    for nombre, antes, despues in cambios:
        antes, despues = antes.replace("\n", nl), despues.replace("\n", nl)
        if despues in t:
            continue
        if t.count(antes) != 1:
            raise SystemExit("%s: %s no está como se espera (%d veces); no se escribe nada" % (os.path.basename(p), nombre, t.count(antes)))
        t = t.replace(antes, despues)
        hechos.append(nombre)
    return t, hechos


def main(carpeta=AQUI):
    salidas = []
    for f, cambios in (("prueba_conversion.py", CV), ("prueba_conversion_vxu.py", VX), ("prueba_conversion_mdm.py", MD)):
        p = os.path.join(carpeta, f)
        t, hechos = aplica(p, cambios)
        salidas.append((p, t, hechos))
    for p, t, hechos in salidas:
        open(p, "w", encoding="utf-8", newline="").write(t)
        print("%s: %s" % (os.path.basename(p), ", ".join(hechos) if hechos else "ya estaba"))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
