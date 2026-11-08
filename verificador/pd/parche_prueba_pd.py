#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 40: las pruebas del arreglo del juez, antes que el arreglo (pd/diseno-pd-fable.md §3, con pd/decision-jev-pd.md).

  python3 pd/parche_prueba_pd.py [<carpeta>]     (por omisión, la de este laboratorio)

- prueba_conversion.py: P-CV-33 (la conducta: la Observation de PD1-7 en un ADT) y P-CV-34 (lo que el juez dice de sí mismo), y
  P-CV-32 al revés en lo de PD1-7 (L-CV-17 ya no la da por de ACC o PDA) y con la entrada de la etapa 37 donde esté;
- prueba_conversion_vxu.py (P-VX-20) y prueba_conversion_mdm.py (P-MD-24): el perfil de ADT con 23 filas;
- prueba_conversion_mdm.py (P-MD-25 d): las huellas de C, INFO y MAPAS medidas sobre una copia con pd/parche_juez_pd.py aplicado.
Cada sustitución tiene que darse una sola vez; si no, no se escribe nada. Conserva los finales de línea."""
import os
import sys

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

P33 = '''

# ---------------------------------------------------------------------------- etapa 40: la Observation de PD1-7
CS0315 = "http://terminology.hl7.org/CodeSystem/v2-0315"
ACC_Y = seg("ACC", {1: "20260102", 3: "Calle Mayor 5", 5: "Y", 6: "N", 8: "caida en casa"})


def con_pd1(m, valor="F"):
    """El mensaje con PD1 (PD1-7 = valor) tras el PID, donde lo pone la estructura."""
    s = m.split("\\r")
    k = next(i for i, x in enumerate(s) if x.startswith("PID|")) + 1
    return "\\r".join(s[:k] + [seg("PD1", {7: valor})] + s[k:])


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
    mira("PD1-7 = X, fuera de la 0315, con el código X: nada", cuentan(j(ev(mx, adt_bundle(extra=[obs_pd1("X")])))), [])
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
    mira("control ORU: con PD1, la Observation de más sigue inventada",
         ("fidelidad", "recurso_inventado", "OBX") in cuentan(j(ev(con_pd1(oru_msg()), oru_bundle([pac_oru(), dr(), obs1(), obs2(), obs_pd1()]),
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
    mira("la versión del servidor: la primera entrada, la de la etapa 40 con L-CV-18; la segunda, la de la 37 con L-CV-17",
         (entradas[0].startswith("etapa 40"), "L-CV-18" in entradas[0], len(entradas) > 1 and entradas[1].startswith("etapa 37"),
          len(entradas) > 1 and "L-CV-17" in entradas[1]), (True, True, True, True))
'''

CV = []
CV.append(("P-CV-33 y P-CV-34", "\n\nPRUEBAS = [p01,", P33.rstrip("\n") + "\n\n\nPRUEBAS = [p01,"))
CV.append(("la lista", "p25, p26, p27, p28, p29, p30, p31, p32]", "p25, p26, p27, p28, p29, p30, p31, p32, p33, p34]"))
CV.append(("P-CV-32: L-CV-17 ya no da la de PD1-7 por de ACC o PDA",
           '''    mira("L-CV-17: una Observation de solo Y/N que no sale de ACC ni de PDA (PD1-7, o una inventada) se da por de ellos",
         ("0136" in l17, "PD1-7" in l17, "inventada" in l17), (True, True, True))''',
           '''    mira("L-CV-17: una Observation de solo Y/N que no sale de ACC ni de PDA (una inventada, o la de PD1-7 sin valueCodeableConcept) "
         "se da por de ellos; la de PD1-7 que la guía mapea, ya no (etapa 40)",
         ("0136" in l17, "inventada" in l17, "valueCodeableConcept" in l17, "que la guía sí mapea" in l17), (True, True, True, False))'''))
CV.append(("P-CV-32: la entrada de la etapa 37, donde esté",
           '''    mira("la versión del servidor: la primera entrada es la de la etapa 37, con L-CV-17",
         (entradas[0].startswith("etapa 37"), "L-CV-17" in entradas[0]), (True, True))''',
           '''    e37 = [e for e in entradas if e.startswith("etapa 37")]       # desde la etapa 40, la segunda (P-CV-34)
    mira("la versión del servidor: la entrada de la etapa 37, con L-CV-17", (len(e37), bool(e37) and "L-CV-17" in e37[0]), (1, True))'''))
CV.append(("P-CV-32: el docstring",
           '''    y el texto de versión del servidor nombra L-CV-17."""''',
           '''    y el texto de versión del servidor nombra L-CV-17. Etapa 40: L-CV-17 ya no da la de PD1-7 por de ACC o PDA, y la entrada de la
    37 deja de ser la primera."""'''))

VX = [("P-VX-20: el perfil de ADT con la fila de PD1-7",
       '(len(CV.PERFIL_GUIA_ADT), len(CV.PERFIL_GUIA_ORU)), (22, 16))  # etapa 37: L-CV-17',
       '(len(CV.PERFIL_GUIA_ADT), len(CV.PERFIL_GUIA_ORU)), (23, 16))  # etapa 37: L-CV-17; etapa 40: PD1-7')]
MD = [("P-MD-24: el perfil de ADT con la fila de PD1-7",
       'len(M.t_tabla({"tabla": "perfil_guia_vxu"})[0]["entradas"])), (22, 16, 27))',
       'len(M.t_tabla({"tabla": "perfil_guia_vxu"})[0]["entradas"])), (23, 16, 27))   # etapa 40: la fila de PD1-7'),
      ("P-MD-25 d: C, INFO y MAPAS de la etapa 40",
       '''ANTES = {"mdm": "75ab855348d66163", "C": "5dabbc37ec4a7909", "INFO": "cbb618aa5d7c14dc", "TIPOS_PROY": "415c77f208321377",
         "CVX.TIPOS": "9cf86194ce1b29a6", "PUNTOS": "08fc6c6fea93f4af", "MAPAS": "6fb1b433ac5d4d8f"}''',
       '''# Etapa 40 (8-nov): C (C["PD1-7"]), INFO (S-CV-4, L-CV-17 y L-CV-18) y MAPAS (la 0315) cambian a propósito; antes,
# 5dabbc37ec4a7909, cbb618aa5d7c14dc y 6fb1b433ac5d4d8f. Lo demás, igual.
ANTES = {"mdm": "75ab855348d66163", "C": "cfd33a3662852137", "INFO": "4fc316780b5e8ded", "TIPOS_PROY": "415c77f208321377",
         "CVX.TIPOS": "9cf86194ce1b29a6", "PUNTOS": "08fc6c6fea93f4af", "MAPAS": "efd2c02a08bded34"}''')]


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
    for p, t, hechos in salidas:                      # se escribe solo si las tres casan
        open(p, "w", encoding="utf-8", newline="").write(t)
        print("%s: %s" % (os.path.basename(p), ", ".join(hechos) if hechos else "ya estaba"))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
