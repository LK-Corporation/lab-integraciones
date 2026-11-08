#!/usr/bin/env python3
"""Etapa 37 (jz/diseno-jz-fable.md §4, con las decisiones de jz/decision-jev-jz.md): las pruebas del juez, en rojo antes.

  python3 jz/parche_prueba_jz.py [<carpeta del juez>]     (por omisión, la de este laboratorio)

- prueba_conversion.py: P-CV-12 («control X fusionado») y P-CV-15 (el ejemplo de valor_imposible_convertido pasa a PID-30)
  cambian; P-CV-29 (PID-8 fuera de la 0001), P-CV-30 (Observation de un segmento sin destino) y P-CV-31 (el rechazo por PID-8)
  son nuevas.
- prueba_conversion_vxu.py: P-VX-24 (NK1-15 fuera de la 0001 y el rechazo de un VXU por PID-8) es nueva.
Cada sustitución tiene que darse una sola vez; si no, no se escribe nada. Conserva los finales de línea."""
import os
import sys

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CV_12_ANTES = '''    mira("control X fusionado", (len(h8), set(h8[0]["subtipo"].split("+")) if h8 else None),
         (1, {"valor_imposible_convertido", "fhir_invalido"}))'''
CV_12_DESPUES = '''    mira("control X fusionado", (len(h8), set(h8[0]["subtipo"].split("+")) if h8 else None),      # etapa 37: la 0001 es user-defined
         (1, {"fhir_invalido"}))'''

CV_15_ANTES = '''        "valor_imposible_convertido": (msg(pid={8: "X"}), adt_bundle(p=con(pac, gender="other")), "PID-8"),'''
CV_15_DESPUES = '''        "valor_imposible_convertido": (msg(pid={30: "X"}), adt_bundle(p=con(pac, deceasedBoolean=False)), "PID-30"),   # etapa 37'''

CV_NUEVAS = '''

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
    return "\\r".join([m] + list(segs))


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
    mira("control PID-7 imposible: aceptable", cat(j(ev(msg(pid={7: "19801301"}), estado="error", error=err))), ("correcto", None))'''

CV_LISTA_ANTES = "           p25, p26, p27, p28]"
CV_LISTA_DESPUES = "           p25, p26, p27, p28, p29, p30, p31]"

VX_NUEVA = '''

# ---------------------------------------------------------------------------- etapa 37: NK1-15 y el rechazo por PID-8
def p24():
    """Conducta 1 en VXU (jz/decision-jev-jz.md): NK1-15 fuera de la 0001 es convención si el código es de administrative-gender
    y FHIR inválido si no; PID-8 fuera de la 0001 ya no hace aceptable el rechazo (Q-JZ-1 b)."""
    nk1 = lambda v: seg("NK1", {1: "1", 2: "Prueba^Lucia^^^^^L", 3: "MTH^Madre^HL70063", 5: "^PRN^PH^^^^5551234", 15: v, 16: "19900301"})  # noqa: E731
    r = juzga(msg(antes_orden=[nk1("S")]), bundle(extra=[dict(madre(), gender="unknown")]))
    mira("NK1-15 S a unknown: convención", (sh(r), "convencion" in notas(r)), ([], True))
    r = juzga(msg(antes_orden=[nk1("S")]), bundle(extra=[dict(madre(), gender="S")]))
    mira("NK1-15 S a S: FHIR inválido", sh(r), [("fhir_invalido", "NK1-15")])
    r = juzga(msg(antes_orden=[nk1("S")]), bundle(extra=[{k: v for k, v in madre().items() if k != "gender"}]))
    mira("NK1-15 S sin gender: nada", [h for h in r["hallazgos"] if h["hecho"] == "NK1-15"], [])
    mira("control NK1-15 F a male", sh(juzga(msg(antes_orden=[nk1("F")]), bundle(extra=[dict(madre(), gender="male")]))),
         [("valor_distinto", "NK1-15")])
    r = j(ev_vxu(msg(pid={8: "X"}), estado="error", error={"codigo": "1", "texto": "genero"}))
    mira("rechazo de un VXU con PID-8 X", cat(r), ("rechazo_incorrecto", "error"))'''

VX_LISTA_ANTES = "PRUEBAS = [p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23]"
VX_LISTA_DESPUES = "PRUEBAS = [p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24]"


def cambia(texto, antes, despues, nombre):
    n = texto.count(antes)
    if n != 1:
        raise SystemExit("%s: aparece %d veces; no se escribe nada" % (nombre, n))
    return texto.replace(antes, despues)


def main(carpeta=AQUI):
    f_cv = os.path.join(carpeta, "prueba_conversion.py")
    f_vx = os.path.join(carpeta, "prueba_conversion_vxu.py")
    cv = open(f_cv, encoding="utf-8", newline="").read()
    vx = open(f_vx, encoding="utf-8", newline="").read()
    if "def p29():" in cv or "def p24():" in vx:
        print("ya aplicado")
        return 0
    cv = cambia(cv, CV_12_ANTES, CV_12_DESPUES, "P-CV-12")
    cv = cambia(cv, CV_15_ANTES, CV_15_DESPUES, "P-CV-15")
    cv = cambia(cv, "\n\n\nPRUEBAS = [", CV_NUEVAS + "\n\n\nPRUEBAS = [", "P-CV-29..31")
    cv = cambia(cv, CV_LISTA_ANTES, CV_LISTA_DESPUES, "lista de P-CV")
    vx = cambia(vx, "\n\n\n" + VX_LISTA_ANTES, VX_NUEVA + "\n\n\n" + VX_LISTA_DESPUES, "P-VX-24")
    open(f_cv, "w", encoding="utf-8", newline="").write(cv)
    open(f_vx, "w", encoding="utf-8", newline="").write(vx)
    print("pruebas de la etapa 37 escritas en %s y %s" % (f_cv, f_vx))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
