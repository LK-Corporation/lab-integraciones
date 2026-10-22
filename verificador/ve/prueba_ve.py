#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VE1-b (ve/diseno-verificador-ve-fable.md §1.4, §2.5, §3.3): las pruebas de la etapa del verificador, escritas ANTES del código.
Cada prueba fija lo que da el juez de HOY y lo que tiene que dar DESPUÉS. Las que no cambian son controles (hoy = después).
Viven aquí, no repartidas por las suites, para no tocar los ficheros de la huella del juez antes del código (DV-VE-4).
  python3 ve/prueba_ve.py hoy       el juez de hoy: cada prueba da su «hoy»; las que no son control, en rojo por la razón prevista
  python3 ve/prueba_ve.py           el juez nuevo: cada prueba da su «después»
  python3 ve/prueba_ve.py ver       imprime lo observado (para adjudicar)
Regla: ningún MAL. Los ejemplos son sintéticos (X1, V1, MSG1)."""
import copy
import json
import os
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, FASE)
os.chdir(FASE)

import acuse_referencia as AR  # noqa: E402
import almacen_adt as AA2  # noqa: E402
import bases_oru as BO  # noqa: E402
import mapeador_adt as MA  # noqa: E402
import mapeador_oru as MO  # noqa: E402
import mapeador_referencia as MR  # noqa: E402
import verificador as V  # noqa: E402

SIS_MRN = "urn:lab:integraciones:mrn"

# ---- adt_fhir, como prueba_adt.py
BASE = ("MSH|^~\\&|HIS|H|LAB|L|20260101120000||ADT^%s^%s|M1|P|2.5\rEVN|%s|20260101120000\r"
        "PID|1||X1^^^H^MR||Pérez^Ana^^^^^L||19800101|F\rPV1|1|%s|URG^1^A|||||||MED|||||||||%s")
L16 = {"tipo": "Info", "texto": "Paciente y visita escritos en FHIR (MSH-10=M1): Patient=creado Encounter=creado (HTTP 200)"}


def msg(ev="A01", pv12="I", pv119="V1"):
    return BASE % (ev, MA.ESTRUCTURA.get(ev, "ADT_A05"), ev, pv12, pv119)


def ack(msa1="AA", err=None, ctl="M1"):
    return "MSH|^~\\&|LAB|L|HIS|H|20260101120001||ACK^A01^ACK|A1|P|2.5\rMSA|%s|%s" % (msa1, ctl) + ("\rERR|||%s|E" % err if err else "")


def ev_adt(texto, ack_, log, canon, alm):
    s = {"log": log}
    if canon is not None:
        s["canonico_adt"] = canon
    if alm is not None:
        s["almacen_adt"] = alm
    return {"mensaje": texto, "ack": ack_, "conexion": ["conexión establecida"] + (["ACK recibido a los 0.02 s del envío"] if ack_ else []),
            "sesiones": [s], "entorno": [], "punto_entrada": "adt_fhir"}


def esp(texto):
    return MA.esperado_mensaje(MA._msg(texto), "adt_fhir")[0]


def encounter(id_, status="in-progress", paciente="X1", **mas):
    return {"id": id_, "crudo": json.dumps(dict({"resourceType": "Encounter", "id": id_, "status": status,
                                                 "subject": {"identifier": {"system": SIS_MRN, "value": paciente}}}, **mas))}


def vpp(recursos, previos=(), paciente="X1"):
    return [{"identificador": paciente, "n": len(recursos), "recursos": list(recursos), "previos": list(previos)}]


# ---- adt_a01, como prueba_verificador.py
B_A01 = list(AR.B)
L01 = {"tipo": "Info", "componente": "FhirPatient", "texto": "Patient creado en FHIR: id=<oculto> desde MSH-10=MSG1 (HTTP 201)"}
CAN = {"Identifier": "ID1", "FamilyName": "Apellido", "GivenName": "Nombre", "Gender": "male", "BirthDate": "1960-09-10",
       "MsgControlId": "MSG1", "SendingApp": "LAB_SYS", "SendingFacility": "CLINICA_B", "MsgEvent": "A01", "ProcessingId": "P", "Truncado": 0}
H = "MSH|^~\\&|LABFHIR|LAB|LAB_SYS|CLINICA_B|<hora oculta>||ACK^A01^ACK|X1|P|2.5\n"


def ev_a01(log, canon):
    s = {"log": log}
    if canon is not None:
        s["canonico"] = dict(canon)
    return {"mensaje": "<VT>" + "\n".join(B_A01) + "\n<FS>", "conexion": ["conexión establecida", "ACK recibido a los 0.016 s del envío"],
            "sesiones": [s], "ack": H + "MSA|AA|MSG1", "entorno": []}


# ---- oru_fhir, como prueba_oru.py
L15 = {"tipo": "Info", "texto": "Resultados escritos en FHIR (MSH-10=%s): creados=%d existentes=0 (HTTP 200)"}
B_ORU = {b["id"]: b for b in BO.BASES}


def ev_oru(con_canonico, obx5=None):
    b = B_ORU["B01"]
    segs = list(b["segmentos"])
    if obx5 is not None:
        segs[3] = AR._campo_set(segs[3], 5, obx5)
    texto = "\r".join(segs) + "\r"
    e_ = MO.esperado_mensaje(MR.mensajes(texto)[0], "oru_fhir")[0]
    s = {"log": [dict(L15, texto=L15["texto"] % ("ORU-" + b["id"], len(e_["informes"]) + len(e_["observaciones"])))]}
    if con_canonico:
        s["canonico_oru"] = copy.deepcopy(e_)
    a = ("MSH|^~\\&|LABORU|LAB|LABSYS|HOSPSYN|20230104090000||ACK^R01^ACK|A-%s|P|2.5\rMSA|AA|ORU-%s" % (b["id"], b["id"]))
    return {"mensaje": texto, "ack": a, "conexion": ["conexión establecida", "ACK recibido a los 0.02 s del envío"],
            "sesiones": [s], "entorno": [], "punto_entrada": "oru_fhir"}


# ---- perfil mínimo en memoria para MS9 (no se nombra ni se carga el del sitio): MSH-12 vacío = 2.6 por omisión (H4)
AR.PERFILES["_ve"] = {"nombre": "_ve", "msh12_por_omision": "2.6", "regla_msh12": "H4"}


def con_perfil(p, f):
    AR.PERFIL = p
    try:
        return f()
    finally:
        AR.PERFIL = "lab"


def msg_ms9(v12="", pid8="V"):
    return msg().replace("|M1|P|2.5\r", "|M1|P|%s\r" % v12).replace("|19800101|F", "|19800101|%s" % pid8)


# ---- observaciones
def cuenta(v):
    return sorted((h["clase"], h["subtipo"], h["hecho"]) for h in v["hallazgos"] if h["cuenta"])


def subtipos_no_cuentan(v):
    return sorted({h["subtipo"] for h in v["hallazgos"] if not h["cuenta"]})


def cat(v):
    return (v["veredicto"]["categoria"], v["veredicto"].get("subtipo"))


def acuse(x):
    return (x.get("msa1"), x["err"][0]["err3"] if x["err"] else None, x["err"][0]["donde"] if x["err"] else None,
            any(t.startswith("[S22]") for t in x.get("tolerancias") or []),
            sorted((a["msa1"], a["err3"], a["por"]) for a in x.get("alternativas_aceptadas") or []))


PRUEBAS = []


def prueba(pid, que, hoy, despues):
    def dec(f):
        PRUEBAS.append((pid, que, f, hoy, despues))
        return f
    return dec


FS_SIN = ("fallo_silencioso", "guardado")
SC = ("fidelidad", "sin_canonico", "existencia")


# ================================================================================================= M12 (§1.4)
@prueba("P-VE-1", "adt_fhir: AA + L16 + almacén exacto, SIN canonico_adt (MMI-12)", (("correcto", None), []), (FS_SIN, [SC]))
def p1():
    t = msg()
    v = V.verificar(ev_adt(t, ack(), [L16], None, AA2.almacen_sintetico(esp(t))))
    return (cat(v), cuenta(v))


@prueba("P-VE-2", "adt_a01: AA + L01, SIN canónico", (("correcto", None), []), (FS_SIN, [SC]))
def p2():
    v = V.verificar(ev_a01([L01], None))
    return (cat(v), cuenta(v))


@prueba("P-VE-3", "oru_fhir: AA + L15, SIN canonico_oru, ORU válido (DV-VE-5)", (("correcto", None), []), (FS_SIN, [SC]))
def p3():
    v = V.verificar(ev_oru(False))
    return (cat(v), cuenta(v))


@prueba("P-VE-3b", "oru_fhir: AA + L15, SIN canonico_oru, OBX-5 «1,5» con NM: el acuse ya lo caza hoy; se añade sin_canonico",
        ("fallo_silencioso", False, True), ("fallo_silencioso", True, True))
def p3b():
    v = V.verificar(ev_oru(False, "1,5"))
    c = cuenta(v)
    return (cat(v)[0], SC in c, any(s == "aceptado_imposible" and h.startswith("OBX") and h.endswith("-5") for _c, s, h in c))


@prueba("P-VE-4", "control: como P-VE-1 + el lector declara que no pudo leer el canónico (hoy ya manda; DV-VE-6)",
        (("indeterminado", "lectura"), None), (("indeterminado", "lectura"), None))
def p4():
    t = msg()
    a = AA2.almacen_sintetico(esp(t))
    a["fallos"] = [{"paso": "canonico", "detalle": "sonda VE1-b"}]
    v = V.verificar(ev_adt(t, ack(), [L16], None, a))
    return (cat(v), None if cat(v)[0] == "indeterminado" else cuenta(v))


@prueba("C-1", "control: adt_fhir AA + L16 + canónico + almacén exacto", (("correcto", None), []), (("correcto", None), []))
def c1():
    t = msg()
    v = V.verificar(ev_adt(t, ack(), [L16], copy.deepcopy(esp(t)), AA2.almacen_sintetico(esp(t))))
    return (cat(v), cuenta(v))


@prueba("C-2", "control: adt_fhir AR 201 (A05) sin log y sin canónico", (("correcto", None), []), (("correcto", None), []))
def c2():
    t = msg("A05")
    v = V.verificar(ev_adt(t, ack("AR", "201"), [], None, None))
    return (cat(v), cuenta(v))


@prueba("C-4", "control: adt_a01 AA sin log y sin canónico (L5: el canónico no se exige)", (("correcto", None), []), (("correcto", None), []))
def c4():
    v = V.verificar(ev_a01([], None))
    return (cat(v), cuenta(v))


# ================================================================================================= M19 (§2.5)
FS_ALM_PV12 = (FS_SIN, [("fidelidad", "almacen", "PV1-2")])


@prueba("P-VE-5", "A31 PV1-2 = N, PV1-19 vacío: un Encounter del paciente en visitas_por_paciente (MMI-19)",
        (("correcto", None), []), FS_ALM_PV12)
def p5():
    t = msg("A31", "N", "")
    a = AA2.almacen_sintetico(esp(t))
    a["visitas_por_paciente"] = vpp([encounter("9")])
    v = V.verificar(ev_adt(t, ack(), [L16], copy.deepcopy(esp(t)), a))
    return (cat(v), cuenta(v))


@prueba("P-VE-6", "como P-VE-5 con el Encounter en previos: no se juzga, nota",
        (("correcto", None), [], False), (("correcto", None), [], True))
def p6():
    t = msg("A31", "N", "")
    a = AA2.almacen_sintetico(esp(t))
    a["visitas_por_paciente"] = vpp([encounter("9")], previos=["9"])
    v = V.verificar(ev_adt(t, ack(), [L16], copy.deepcopy(esp(t)), a))
    return (cat(v), cuenta(v), "almacen_previos" in subtipos_no_cuentan(v))


@prueba("P-VE-7", "control: A01 con V1, el mismo Encounter por visita y por paciente (se cuenta una vez)",
        (("correcto", None), []), (("correcto", None), []))
def p7():
    t = msg()
    a = AA2.almacen_sintetico(esp(t))
    a["visitas_por_paciente"] = vpp([dict(a["visitas"][0]["recursos"][0])])
    v = V.verificar(ev_adt(t, ack(), [L16], copy.deepcopy(esp(t)), a))
    return (cat(v), cuenta(v))


def _p8(recursos):
    t = msg(pv119="")
    e_ = esp(t)
    a = AA2.almacen_sintetico(e_)
    if recursos is not None:
        a["visitas_por_paciente"] = vpp(recursos)
    v = V.verificar(ev_adt(t, ack(), [L16], copy.deepcopy(e_), a))
    return (cat(v), cuenta(v), "almacen_no_leido" in subtipos_no_cuentan(v))


def _proyeccion_encounter(id_, **cambios):
    t = msg(pv119="")
    r = MA._limpio(MA._sin_nulos(MA.proyectar(esp(t))["Encounter"]))
    r = dict(r, id=id_, meta={"versionId": "1"}, **cambios)
    return {"id": id_, "crudo": json.dumps(r, ensure_ascii=False)}


@prueba("P-VE-8a", "A01 PV1-19 vacío (S78): 1 Encounter del paciente = la proyección", (("correcto", None), [], True), (("correcto", None), [], False))
def p8a():
    return _p8([_proyeccion_encounter("9")])


@prueba("P-VE-8b", "A01 PV1-19 vacío: el Encounter del paciente con status cambiado", (("correcto", None), [], True), FS_ALM_PV12 + (False,))
def p8b():
    return _p8([_proyeccion_encounter("9", status="finished")])


@prueba("P-VE-8c", "A01 PV1-19 vacío: 0 Encounter del paciente", (("correcto", None), [], True), (FS_SIN, [("fidelidad", "ausente", "PV1")], False))
def p8c():
    return _p8([])


@prueba("P-VE-8d", "A01 PV1-19 vacío: 2 Encounter del paciente", (("correcto", None), [], True), (FS_SIN, [("fidelidad", "duplicado", "PV1")], False))
def p8d():
    return _p8([_proyeccion_encounter("9"), _proyeccion_encounter("10")])


@prueba("P-VE-9", "AE 102 sin escritura por identifier, 1 Encounter del paciente: rechazo con escritura", (False,), (True,))
def p9():
    t = msg().replace("19800101", "19801340")
    vacio = {"leido": "tras_ack", "pacientes": [{"identificador": "X1", "n": 0, "recursos": []}],
             "visitas": [{"identificador": "V1", "n": 0, "recursos": []}], "fallos": [],
             "visitas_por_paciente": vpp([encounter("9")])}
    v = V.verificar(ev_adt(t, ack("AE", "102"), [], None, vacio))
    return (("acuse", "rechazo_con_escritura", "destino") in cuenta(v),)


# ================================================================================================= MS9 (§3.3)
@prueba("P-VE-12", "acuse, perfil con MSH-12 por omisión, MSH-12 vacío, PID-8 = V",
        ("AA", None, None, True, [("AE", "103", "S26")]), ("AE", "103", "PID-8", False, []))
def p12():
    return con_perfil("_ve", lambda: acuse(AR.calcular(ev_adt(msg_ms9(), None, [], None, None), pe="adt_fhir")[0]))


@prueba("P-VE-12b", "control: el mismo perfil con MSH-12 = 2.6 escrito y PID-8 = V (S22 y S26 como hoy)",
        ("AA", None, None, True, [("AE", "103", "S26")]), ("AA", None, None, True, [("AE", "103", "S26")]))
def p12b():
    return con_perfil("_ve", lambda: acuse(AR.calcular(ev_adt(msg_ms9("2.6"), None, [], None, None), pe="adt_fhir")[0]))


@prueba("P-VE-12c", "control: perfil lab con MSH-12 vacío -> AR 101", ("AR", "101", "MSH-12", False, []), ("AR", "101", "MSH-12", False, []))
def p12c():
    return acuse(AR.calcular(ev_adt(msg_ms9(), None, [], None, None), pe="adt_fhir")[0])


def _p13(msa1, err):
    def f():
        t = msg_ms9()
        e_ = esp(t)
        alm = AA2.almacen_sintetico(e_) if msa1 == "AA" else {"leido": "tras_ack", "pacientes": [{"identificador": "X1", "n": 0, "recursos": []}],
                                                             "visitas": [{"identificador": "V1", "n": 0, "recursos": []}], "fallos": []}
        v = V.verificar(ev_adt(t, ack(msa1, err), [L16] if msa1 == "AA" else [], copy.deepcopy(e_) if msa1 == "AA" else None, alm))
        pid8 = [h for h in v["hallazgos"] if h["cuenta"] and h["hecho"] == "PID-8"]
        return (cat(v), sorted(tuple(sorted(h["origen"])) for h in pid8),
                "S26" in json.dumps([h for h in v["hallazgos"] if not h["cuenta"]], ensure_ascii=False))
    return con_perfil("_ve", f)


AI = ("fallo_silencioso", "aceptado_imposible")


@prueba("P-VE-13", "verificar, perfil con MSH-12 por omisión, MSH-12 vacío, PID-8 = V, ACK AA: un hallazgo de PID-8, acuse + mapeador",
        (AI, [("mapeador",)], False), (AI, [("acuse", "mapeador")], False))
def p13():
    return _p13("AA", None)


@prueba("P-VE-13b", "ídem con ACK AE 103: correcto, sin la alternativa S26", (("correcto", None), [], True), (("correcto", None), [], False))
def p13b():
    return _p13("AE", "103")


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "despues"
    mal = []
    for pid, que, f, hoy, despues in PRUEBAS:
        try:
            obs = f()
        except Exception as ex:                                         # noqa: BLE001
            obs = ("EXCEPCIÓN", type(ex).__name__, str(ex)[:200])
        if modo == "ver":
            print("%-9s %s\n          obs=%r\n          hoy=%r\n          después=%r" % (pid, que, obs, hoy, despues))
            continue
        esperado = hoy if modo == "hoy" else despues
        control = hoy == despues
        ok = esperado is not None and obs == esperado
        etiqueta = "control" if control else ("rojo previsto" if modo == "hoy" else "verde")
        print("  %s %-9s %-14s %s%s" % ("ok " if ok else "MAL", pid, etiqueta if ok else "", que, "" if ok else "\n        obs=%r\n        esp=%r" % (obs, esperado)))
        if not ok:
            mal.append(pid)
    if modo != "ver":
        n_ctrl = sum(1 for p in PRUEBAS if p[3] == p[4])
        print("PRUEBAS VE (%s): %s (%d pruebas, %d controles)" % (modo, "TODO BIEN" if not mal else "%d MAL: %s" % (len(mal), ", ".join(mal)), len(PRUEBAS), n_ctrl))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
