#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Autoprueba del verificador unificado: los casos N01-N20c (lectura, §1.9) y V01-V26 (combinación, §2.6)
de diseno-verificador-fable.md, N21-N24 y V27-V36 de diseno-s6-s16-fable.md (decisiones del sitio S6-S18), y N25,
V37-V50 y F01-F07 de diseno-s19-s21-fable.md (S19-S29 y la línea SEGMENTOS de la ficha), y V51* y F08* de
diseno-s30-fable.md (S30), y V52-V56, N26, F09-F10 de diseno-s31-s34-fable.md (S31-S37), y N16c-N16l, V62-V62j y F13 de diseno-s42-s43-fable.md (S42, S43).
Cualquier desviación bloquea el uso de la pieza.
Uso: python3 prueba_verificador.py"""
import copy
import sys

import acuse_referencia as AR
import verificador as V

B = list(AR.B)
L01 = {"tipo": "Info", "componente": "FhirPatient", "texto": "Patient creado en FHIR: id=<oculto> desde MSH-10=MSG1 (HTTP 201)"}
X01, X02 = "conexión establecida", "ACK recibido a los 0.016 s del envío"
CAN = {"Identifier": "ID1", "FamilyName": "Apellido", "GivenName": "Nombre", "Gender": "male", "BirthDate": "1960-09-10",
       "MsgControlId": "MSG1", "SendingApp": "LAB_SYS", "SendingFacility": "CLINICA_B", "MsgEvent": "A01", "ProcessingId": "P",
       "Truncado": 0}
H = "MSH|^~\\&|LABFHIR|LAB|LAB_SYS|CLINICA_B|<hora oculta>||ACK^A01^ACK|X1|P|2.5\n"
AA = H + "MSA|AA|MSG1"
mal = []


def mira(nombre, obtenido, esperado):
    ok = obtenido == esperado
    print(("  ok  " if ok else "  MAL ") + nombre + ("" if ok else ": %r != %r" % (obtenido, esperado)))
    if not ok:
        mal.append(nombre)


def ev(segs=None, log=None, entorno=None, conexion=None, ack=AA, canon=CAN, mensaje=None):
    segs = list(B) if segs is None else segs
    s = {"log": [L01] if log is None else log}
    if canon is not None:
        s["canonico"] = dict(canon)
    return {"mensaje": mensaje if mensaje is not None else "<VT>" + "\n".join(segs) + "\n<FS>",
            "conexion": [X01, X02] if conexion is None else conexion, "sesiones": [s], "ack": ack, "entorno": entorno or []}


def con(campos):
    return AR._con(campos)


def fila(tipo, texto):
    return {"tipo": tipo, "componente": "FhirPatient", "texto": texto}


def esp(e):
    x = AR.calcular(e)[0]
    return (x["debe_haber_ack"], x.get("msa1"), x["err"][0]["err3"] if x.get("err") else None)


def lect(e, k=0):
    import lectura_evidencia as LE
    import mapeador_referencia as MR
    ms = MR.mensajes(e["mensaje"])
    return LE.leer(e, [m.campo(m.segs[0], 10) for m in ms])


def ids(e):
    return sorted({z["id"] for z in AR.comparar(e) if z["cuenta"]})


def cuentan(r):
    return [h for h in r["hallazgos"] if h["cuenta"]]


def ver(e):
    r = V.verificar(e)
    return r["veredicto"]["categoria"], r


# ============================================================ N: lectura (§1.9)
e = ev()
mira("N01 L01 -> éxito, AA", (lect(e)["por_mensaje"][0]["destino"], esp(e)), ("exito", ("si", "AA", None)))
e = ev(log=[fila("Info", "Patient creado en FHIR: id=abc desde MSH-10=OTRO (HTTP 201)")])
x = AR.calcular(e)[0]
mira("N01c L01 de otro mensaje -> sin evidencia, AA + nota L5", (x["msa1"], any("L5" in n for n in x["notas"])), ("AA", True))
e = ev(log=[fila("Info", "Patient ya existia (creacion condicional) en FHIR: id=abc desde MSH-10=MSG1 (HTTP 200)")])
x = AR.calcular(e)[0]
mira("N02 L02 -> AA + nota L5'", (x["msa1"], any("L5'" in n for n in x["notas"])), ("AA", True))
e = ev(log=[fila("Info", "Patient ya existia (creacion condicional) en FHIR: id=abc desde MSH-10=MSG1 (HTTP 201)")])
f = lect(e)["filas"][0]
mira("N02c 200 con (HTTP 201): F1 con 201, AA marcado", (f["id"], f["datos"]["http"], esp(e)[1],
     any("F1" in a for a in AR.calcular(e)[0]["ambiguedades"])), ("F1", 201, "AA", True))
L03 = fila("Warning", "Mensaje rechazado antes de FHIR (MSH-10=MSG1): Falta el identificador del paciente (PID-3.1): no se puede crear un Patient sin identificador")
e = ev(con({("PID", 3): ""}), log=[L03], ack=H + "MSA|AE|MSG1\nERR|||101|E", canon=None)
mira("N03 PID-3 vacío, opinión L03, obs AE 101 -> AE 101 sin discrepancia",
     (lect(e)["filas"][0]["datos"]["hecho"], esp(e), ids(e)), ("PID-3", ("si", "AE", "101"), []))
e = ev(log=[L03], ack=H + "MSA|AE|MSG1\nERR|||101|E", canon=None)
d1 = [z for z in AR.comparar(e) if z["id"] == "D1"]
mira("N03c B intacto con opinión L03 -> AA; D1 falso rechazo con causa opinión",
     (esp(e), d1 and d1[0]["causa"]), (("si", "AA", None), "opinion_del_circuito(PID-3)"))
L03L = fila("Warning", "Mensaje rechazado antes de FHIR (MSH-10=MSG1): Algun campo excede la longitud maxima admitida: se rechaza en vez de guardar un dato mutilado")
e = ev(con({("PID", 5): "A" * 260 + "^N"}), log=[L03L], ack=H + "MSA|AR|MSG1\nERR|||104|E", canon=None)
mira("N04 longitud, obs AR 104 -> AA (truncado) y D1", (esp(e)[1], "D1" in ids(e)), ("AA", True))
e = ev(con({("PID", 5): "A" * 260 + "^N"}), log=[L03L], canon=dict(CAN, FamilyName="A" * 250, GivenName="N", Truncado=1))
mira("N04c longitud con AA y Truncado=1: sin discrepancia del acuse", ids(e), [])
L04 = fila("Warning", "Mensaje rechazado a proposito (MSH-10=MSG1): Tipo de mensaje no soportado: ADT^A04 (DocType 2.5:ADT_A01). Esta integracion solo acepta ADT^A01")
L04["componente"] = "Rechazo"
e = ev(con({("MSH", 9): "ADT^A04^ADT_A01"}), log=[L04], ack=H + "MSA|AR|MSG1\nERR|||200|E", canon=None)
mira("N05 A04 con 200 -> AR 201; D2 ERR-3 distinto", (esp(e), ids(e)), (("si", "AR", "201"), ["D2"]))
e = ev(con({("MSH", 9): "ADT^A04^ADT_A01"}), log=[L04], ack=H + "MSA|AR|MSG1\nERR|||201|E", canon=None)
mira("N05c A04 con 201 -> sin discrepancia", ids(e), [])
L05_400 = fila("Warning", 'FHIR rechazo el recurso (MSH-10=MSG1): FHIR devolvio 400: {"resourceType":"OperationOutcome","issue":[{"severity":"error","code":"invalid","diagnostics":"<HSFHIRErr>IllegalControlChar"}]}')
e = ev(log=[L05_400], ack=H + "MSA|AR|MSG1\nERR|||207|E", canon=None)
f = lect(e)["filas"][0]
x = AR.calcular(e)[0]
mira("N06 400 invalid IllegalControlChar -> AR 207 [S16], sin ambigüedad ni discrepancia",
     ((f["id"], f["datos"]["http"], f["datos"]["code"]), esp(e), x["ambiguedades"], ids(e)),
     (("L05", 400, "invalid"), ("si", "AR", "207"), [], []))
e = ev(con({("PID", 5): "Pe\x01rez^Ana"}), log=[L05_400], ack=H + "MSA|AR|MSG1\nERR|||207|E", canon=None)
mira("N06b carácter de control en PID-5 -> AE 102; D1 y D2", (esp(e), ids(e)), (("si", "AE", "102"), ["D1", "D2"]))
e = ev(log=[fila("Warning", "FHIR rechazo el recurso (MSH-10=MSG1): FHIR devolvio 400:")], ack=H + "MSA|AR|MSG1\nERR|||207|E", canon=None)
mira("N06c 400 sin cuerpo -> AR 207 [S16], sin ambigüedad", (esp(e), AR.calcular(e)[0]["ambiguedades"]),
     (("si", "AR", "207"), []))
L05_401 = fila("Warning", "FHIR rechazo el recurso (MSH-10=MSG1): FHIR devolvio 401:")
e = ev(log=[L05_401], entorno=["la credencial con la que el circuito llama a FHIR estaba vacía"], ack=H + "MSA|AR|MSG1\nERR|||207|E", canon=None)
mira("N07 401 + credencial vacía -> AR 207 literal, sin discrepancia", (esp(e), ids(e), AR.calcular(e)[0]["ambiguedades"]),
     (("si", "AR", "207"), [], []))
e = ev(entorno=["la credencial con la que el circuito llama a FHIR pasó a ser vacia tras el mensaje 1"])
mira("N07c credencial vacía tras el mensaje 1: L01 decide -> AA", (esp(e), ids(e)), (("si", "AA", None), []))
e = ev(log=[fila("Warning", "FHIR rechazo el recurso (MSH-10=MSG1): FHIR devolvio 404:")],
       entorno=["la ruta de FHIR a la que llama el circuito no existía"], ack=H + "MSA|AR|MSG1\nERR|||207|E", canon=None)
mira("N08 404 + ruta inexistente -> AR 207", esp(e), ("si", "AR", "207"))
e = ev(entorno=["la ruta de FHIR a la que llama el circuito no existía"])
mira("N08c ruta inexistente y 201 [S12] -> decide el log: correcto + nota",
     (lect(e)["contradictorio"], ver(e)[0], any("entorno contradicho por el log" in n for n in lect(e)["por_mensaje"][0]["notas"])),
     ([], "correcto", True))
L06 = fila("Error", 'FHIR fallo del lado servidor (MSH-10=MSG1): FHIR devolvio 503: {"resourceType": "OperationOutcome", "issue": [{"severity": "error", "code": "transient"}]}')
e = ev(log=[L06], ack=H + "MSA|AR|MSG1\nERR|||207|E", canon=None)
mira("N09 503 transient -> AR 207 sin ambigüedad, sin discrepancia", (esp(e), AR.calcular(e)[0]["ambiguedades"], ids(e)),
     (("si", "AR", "207"), [], []))
e = ev(log=[L06])
d1 = [z for z in AR.comparar(e) if z["id"] == "D1"]
mira("N09c 503 y AA observado -> D1 aceptacion_falsa", d1 and d1[0]["causa"], "aceptacion_falsa")
L07 = fila("Error", "No se pudo hablar con FHIR (MSH-10=MSG1): ERROR #6059: Unable to open TCP/IP socket to server localhost:59999")
E07 = "el puerto de FHIR al que llama el circuito estaba cerrado: FHIR era inalcanzable"
mira("N10 L07 + E07 -> AR 207", esp(ev(log=[L07], entorno=[E07], canon=None)), ("si", "AR", "207"))
mira("N10c solo E07, log vacío -> AR 207", esp(ev(log=[], entorno=[E07], canon=None)), ("si", "AR", "207"))
TO = "ERROR <Ens>ErrFailureTimeout: FailureTimeout of 15 seconds exceeded in Lab.HL7.Operation.FhirPatient; status from last attempt was OK"
L08 = [fila("Error", TO), fila("Alert", TO),
       {"tipo": "Error", "componente": "EnrutadorAdt", "texto": "ERROR <Ens>ErrBPTerminated: Terminating BP EnrutadorAdt # due to error: " + TO}]
e = ev(log=L08, entorno=["las peticiones del circuito a FHIR se retrasaron 20 s, cada una con probabilidad 0.5"],
       ack=H + "MSA|AR|MSG1\nERR|||207|E", canon=None)
x = AR.calcular(e)[0]
mira("N11 timeouts -> AR 207, sin discrepancia, nota L15", (esp(e), ids(e), any("L15" in n for n in x["notas"])),
     (("si", "AR", "207"), [], True))
e = ev(entorno=["las peticiones del circuito a FHIR se retrasaron 14 s, cada una con probabilidad 1.0"],
       conexion=[X01, "ACK recibido a los 14.2 s del envío"])
mira("N11c retraso con 201 -> AA, sin discrepancia", (esp(e), ids(e)), (("si", "AA", None), []))
CE = fila("Warning", "Constructing ACK with code CE because SendRequestSync() of 7@EnsLib.HL7.Message/66752 returned with no response object and status: ERROR <Ens>ErrFailureTimeout")
CE["componente"] = "AdtTcpIn"
e = ev(log=L08 + [CE], ack=H + "MSA|CE|MSG1", canon=None)
d1 = [z for z in AR.comparar(e) if z["id"] == "D1"]
mira("N12 CE fabricado en modo original -> esperado AR 207; D1 con causa fabricado",
     (esp(e), d1 and d1[0]["causa"]), (("si", "AR", "207"), "acuse_fabricado_por_servicio"))
e = ev(con({("MSH", 15): "AL", ("MSH", 16): "AL"}), log=L08 + [CE], ack=H + "MSA|CE|MSG1", canon=None)
x = AR.calcular(e)[0]
mira("N12c modo mejorado [S13]: aplicación AR 207; D1 CE != CA (contra msa1_commit)",
     (x["msa1"], x["msa1_aplicacion"], "D1" in ids(e)), ("AR", "AR", True))
LOST = {"tipo": "Error", "componente": "AdtTcpIn", "texto": "ERROR <Ens>ErrOutConnectionLost: Lost HL7 Write connection to |TCP|2575 - detected via ERROR #5002: ObjectScript error: <NOTOPEN>Flush+7^%IO.DeviceStream.1"}
e = ev(log=[LOST, L01], conexion=[X01, "no llegó ACK (el emisor dejó de esperar a los 10.0 s)"], ack=None)
d0 = [z for z in AR.comparar(e) if z["id"] == "D0"]
mira("N13 ACK ausente por tiempo -> AA esperado, D0 causa tiempo", (esp(e), d0 and d0[0]["causa"]),
     (("si", "AA", None), "entorno:tiempo"))
mira("N13c ACK recibido -> sin discrepancia", ids(ev(conexion=[X01, "ACK recibido a los 0.05 s del envío"])), [])
B2 = [z.replace("MSG1", "MSG2") for z in B]
DISC = {"tipo": "Warning", "componente": "AdtTcpIn", "texto": "Discarding leftover input '" + B2[0] + "'"}
e = ev(mensaje="<VT>" + "\n".join(B) + "\n" + "\n".join(B2) + "\n<FS>", log=[L01, DISC])
d0 = [z for z in AR.comparar(e) if z["id"] == "D0"]
mira("N14 resto descartado MSG2 -> D0 recuento, causa trama", (len(AR.calcular(e)), d0 and d0[0]["causa"]), (2, "trama"))
e = ev(log=[L01, {"tipo": "Warning", "componente": "AdtTcpIn", "texto": "Discarding leftover input 'basura'"}])
mira("N14c resto sin MSH -> AA sin discrepancia", (esp(e), ids(e)), (("si", "AA", None), []))
e = ev(log=[L01, {"tipo": "Info", "componente": "AdtTcpIn", "texto": "Disconnecting from 2575<-172.19.0.1:36568"}])
mira("N15 desconexión: irrelevante", (lect(e)["filas"][1]["id"], ids(e)), ("L12", []))
e = ev(log=[L01, {"tipo": "Error", "componente": "AdtTcpIn", "texto": "Disconnecting from 2575<-172.19.0.1:36568"}])
mira("N15c desconexión con tipo Error: L12 igual (el tipo no manda)", (lect(e)["filas"][1]["id"], ids(e)), ("L12", []))
e = ev(log=[fila("Error", "algo nunca visto")])
mira("N16 Error desconocido -> AR 207 ambigua; veredicto indeterminado",
     (esp(e)[1:], any("F2" in a for a in AR.calcular(e)[0]["ambiguedades"]), ver(e)[0]), (("AR", "207"), True, "indeterminado"))
e = ev(log=[fila("Info", "algo nunca visto")])
x = AR.calcular(e)[0]
mira("N16c Info desconocido sin terminal -> AA + nota L5; vocabulario nuevo; indeterminado [S42]", (x["msa1"],
     any("L5" in n for n in x["notas"]), bool(lect(e)["vocabulario_nuevo"]), ver(e)[0],
     any("[S42]" in t for t in lect(e)["lectura_hallazgos"])), ("AA", True, True, "indeterminado", True))
E04 = "una fila de la tabla de consulta del sexo cambió: F -> 'male'"
e = ev(con({("PID", 8): "F"}), entorno=[E04], canon=dict(CAN, Gender="male"))
c, r = ver(e)
mira("N17 tabla del sexo alterada: acuse sin discrepancia; mapeador Gender", (ids(e), [h["hecho"] for h in cuentan(r)]), ([], ["PID-8"]))
e = ev(entorno=[E04])
mira("N17c tabla alterada, PID-8 M: sin discrepancias", (ids(e), ver(e)[0]), ([], "correcto"))
E09 = "el componente que escribe en FHIR estaba deshabilitado"
e = ev(log=[], entorno=[E09], conexion=[X01, "no llegó ACK (el emisor dejó de esperar a los 30.0 s)"], ack=None, canon=None)
d0 = [z for z in AR.comparar(e) if z["id"] == "D0"]
mira("N18 deshabilitado + sin ACK -> AR 207; D0 causa tiempo", (esp(e), d0 and d0[0]["causa"]), (("si", "AR", "207"), "entorno:tiempo"))
mira("N18c deshabilitado y 201 [S12] -> correcto", ver(ev(entorno=[E09]))[0], "correcto")
e = ev(log=[], entorno=["el servicio se paró y se volvió a arrancar durante el lote (stop, 2 s, start)"],
       conexion=["la conexión no se estableció: ConnectionRefusedError: [Errno 111] Connection refused"], ack=None, canon=None)
e["sesiones"] = []
mira("N19 conexión rechazada -> sin intercambio", (esp(e)[0], ver(e)[0]), ("no", "sin_intercambio"))
e = ev(conexion=[X01, "error en el emisor: ConnectionResetError: [Errno 104] Connection reset by peer"], ack=None)
d0 = [z for z in AR.comparar(e) if z["id"] == "D0"]
mira("N19c reiniciada tras establecer, con sesión -> AA; D0 causa conexión", (esp(e), d0 and d0[0]["causa"]),
     (("si", "AA", None), "entorno:conexion"))
L06_504 = fila("Error", 'FHIR fallo del lado servidor (MSH-10=MSG1): FHIR devolvio 504: {"resourceType": "OperationOutcome", "issue": [{"severity": "error", "code": "timeout"}]}')
e = ev(log=[L06_504, L01], entorno=["FHIR contestó a las peticiones del circuito con error 504, cada una con probabilidad 0.6"])
mira("N20 504 y luego 201: gana la última -> AA; intentos previos", (esp(e), ids(e), lect(e)["por_mensaje"][0]["intentos_previos"]),
     (("si", "AA", None), [], ["L06:504"]))
# hechos del entorno exactos (diseno-entorno-exacto-fable.md §5): el 5xx lleva ventana y no decide [A-18]
E02V = lambda http, p, n: ("FHIR contestó con error %s, con probabilidad %s, solo a %s del circuito en el lote (reintentos "
                           "incluidos); a las demás las atendió con normalidad"
                           % (http, p, "la primera petición POST" if n == 1 else "las %d primeras peticiones POST" % n))
e = ev(log=[L06_504, L01], entorno=[E02V(504, 0.6, 2)])
mira("N20' texto con ventana, 504 y luego 201 -> AA; intentos previos; nota L21",
     (esp(e), ids(e), lect(e)["por_mensaje"][0]["intentos_previos"], any("[L21]" in n for n in lect(e)["por_mensaje"][0]["notas"])),
     (("si", "AA", None), [], ["L06:504"], True))
e = ev(log=[], entorno=[E02V(503, 1.0, 1)])
c, r = ver(e)
mira("N20c 503 p=1.0 con ventana, log vacío y AA -> AA con nota L5; no decide; correcto",
     (esp(e), [z["decide"] for z in lect(e)["entorno"]], c, any("L5" in n for n in lect(e)["por_mensaje"][0]["notas"])),
     (("si", "AA", None), [False], "correcto", True))
mira("N20c control: el mismo caso con E07 sí decide -> AR 207", esp(ev(log=[], entorno=[E07])), ("si", "AR", "207"))
mira("N20d «mensajes» en vez de «peticiones» no es el texto del arnés -> EF",
     [z["id"] for z in lect(ev(entorno=[E02V(503, 1.0, 2).replace("peticiones", "mensajes")]))["entorno"]], ["EF"])
e = ev(log=[], entorno=["FHIR contestó a las peticiones del circuito con error 503, cada una con probabilidad 1.0"])
mira("N20e texto antiguo (legado), log vacío y AA -> AA con nota L5 (antes AR 207); nota [A-18]",
     (esp(e), ver(e)[0], any("[A-18]" in n for n in lect(e)["arnes_inexacto"])), (("si", "AA", None), "correcto", True))

# ============================================================ V: combinación (§2.6)
def vv(nombre, e, n, cat, sub=None, extra=None):
    c, r = ver(e)
    got = (len(cuentan(r)), c) + ((r["veredicto"]["subtipo"],) if sub is not None else ())
    exp = (n, cat) + ((sub,) if sub is not None else ())
    mira(nombre, got, exp)
    return r


vv("V01 base: correcto", ev(), 0, "correcto")
r = vv("V02 PID-8 X aceptado: 1 hallazgo fusionado, fallo_silencioso", ev(con({("PID", 8): "X"}), canon=dict(CAN, Gender="unknown")),
       1, "fallo_silencioso", "aceptado_imposible")
mira("V02: fusión de mapeador y acuse", cuentan(r)[0]["origen"], ["acuse", "mapeador"])
vv("V03 PID-8 X con AE 103, sin canónico: correcto", ev(con({("PID", 8): "X"}), log=[], ack=H + "MSA|AE|MSG1\nERR|||103|E", canon=None),
   0, "correcto")
vv("V04 PID-8 X con AR 200: acuse_incorrecto/codigo", ev(con({("PID", 8): "X"}), log=[], ack=H + "MSA|AR|MSG1\nERR|||200|E", canon=None),
   1, "acuse_incorrecto", "codigo")
e5 = ev(con({("PID", 8): "F"}), entorno=[E04], canon=dict(CAN, Gender="male"))
r = vv("V05 tabla alterada [S20]: fallo_entorno/tabla", e5, 1, "fallo_entorno", "tabla")
mira("V05: hecho PID-8, clase entorno, causa entorno:tabla", (cuentan(r)[0]["hecho"], cuentan(r)[0]["clase"], cuentan(r)[0]["causa"]),
     ("PID-8", "entorno", "entorno:tabla"))
e6 = ev(con({("PID", 8): "F", ("PID", 7): "19601310"}), entorno=[E04], canon=dict(CAN, Gender="male", BirthDate=""))
vv("V06 + PID-7 mes 13 [S23]: ambos/aceptado_imposible+tabla", e6, 2, "ambos", "aceptado_imposible+tabla")
vv("V07 longitud con AR 104: falso rechazo", ev(con({("PID", 5): "A" * 260 + "^N"}), log=[L03L], ack=H + "MSA|AR|MSG1\nERR|||104|E", canon=None),
   1, "acuse_incorrecto", "falso_rechazo")
vv("V07c longitud con AA y Truncado=1: correcto", ev(con({("PID", 5): "A" * 260 + "^N"}), canon=dict(CAN, FamilyName="A" * 250, GivenName="N", Truncado=1)),
   0, "correcto")
vv("V08 503 con AR 207: correcto", ev(log=[L06], ack=H + "MSA|AR|MSG1\nERR|||207|E", canon=None), 0, "correcto")
vv("V09 503 con AA y canónico: aceptacion_falsa", ev(log=[L06]), 1, "fallo_silencioso", "aceptacion_falsa")
e10 = ev(log=[LOST, L01], entorno=["las peticiones del circuito a FHIR se retrasaron 20 s, cada una con probabilidad 0.5"],
         conexion=[X01, "no llegó ACK (el emisor dejó de esperar a los 10.0 s)"], ack=None)
r = vv("V10 sin ACK por tiempo: fallo_entorno", e10, 1, "fallo_entorno")
mira("V10 [S11]: certeza literal, sin alternativa", (r["veredicto"]["certeza"], r["veredicto"]["alternativa"]), ("literal", None))
e10b = copy.deepcopy(e10)
e10b["sesiones"][0]["canonico"]["Gender"] = "female"
vv("V10b + Gender mal: ambos/guardado+ausente", e10b, 2, "ambos", "guardado+ausente")
e11 = ev(log=[], conexion=["la conexión no se estableció: ConnectionRefusedError: [Errno 111] Connection refused"], ack=None, canon=None,
         entorno=["el servicio se paró y se volvió a arrancar durante el lote (stop, 2 s, start)"])
e11["sesiones"] = []
vv("V11 conexión rechazada: sin_intercambio", e11, 0, "sin_intercambio")
vv("V12 timeout + CE fabricado: acuse_incorrecto/fabricado", ev(log=L08 + [CE], ack=H + "MSA|CE|MSG1", canon=None), 1, "acuse_incorrecto", "fabricado")
vv("V12b + 201 tras el timeout y canónico bien: fabricado (sin ambos)", ev(log=L08 + [CE, L01], ack=H + "MSA|CE|MSG1"),
   1, "acuse_incorrecto", "fabricado")
b2 = [z.replace("MSG1", "MSG2") for z in AR._con({("MSH", 15): "AL", ("MSH", 16): "AL"})]
e13 = ev(mensaje="<VT>" + "\n".join(B) + "\n" + "\n".join(b2) + "\n<FS>", log=[L01, dict(DISC, texto="Discarding leftover input '" + b2[0] + "'")])
r = vv("V13 trama: acuse_incorrecto/trama", e13, 1, "acuse_incorrecto", "trama")
mira("V13 [S15]: certeza literal, sin alternativa", (r["veredicto"]["certeza"], r["veredicto"]["alternativa"]), ("literal", None))
r = vv("V14 carácter de control con AE 207: acuse_incorrecto/codigo, A-15",
       ev(con({("PID", 5): "Pe\x01rez^Ana"}), log=[L05_400], ack=H + "MSA|AE|MSG1\nERR|||207|E", canon=None), 1, "acuse_incorrecto", "codigo")
mira("V14 [S10]: certeza literal, sin alternativa", (r["veredicto"]["certeza"], r["veredicto"]["alternativa"]), ("literal", None))
r = vv("V14c 400 con AR 207 y B intacto: correcto [S16]", ev(log=[L05_400], ack=H + "MSA|AR|MSG1\nERR|||207|E", canon=None), 0, "correcto")
mira("V14c: certeza literal", r["veredicto"]["certeza"], "literal")
r = vv("V15 puerto cerrado + 201 + AA [S12]: correcto", ev(entorno=[E07]), 0, "correcto")
mira("V15: nota S12", any("[S12]" in n for n in r["lectura"]["arnes_inexacto"]), True)
vv("V16 Error nunca visto con AA: indeterminado", ev(log=[fila("Error", "texto nunca visto")]), 0, "indeterminado")
vv("V17 200 existía, AA, canónico bien: correcto",
   ev(log=[fila("Info", "Patient ya existia (creacion condicional) en FHIR: id=x desde MSH-10=MSG1 (HTTP 200)")]), 0, "correcto")
vv("V18 PID-3 vacío con AE 101: correcto", ev(con({("PID", 3): ""}), log=[L03], ack=H + "MSA|AE|MSG1\nERR|||101|E", canon=None),
   0, "correcto")
vv("V19 PID-3 vacío aceptado: fallo_silencioso", ev(con({("PID", 3): ""}), canon=dict(CAN, Identifier="")), 1, "fallo_silencioso",
   "aceptado_imposible")
L04b = dict(L04)
vv("V20 A04 con AR 200: acuse_incorrecto/codigo", ev(con({("MSH", 9): "ADT^A04^ADT_A01"}), log=[L04b], ack=H + "MSA|AR|MSG1\nERR|||200|E", canon=None),
   1, "acuse_incorrecto", "codigo")
vv("V20c A04 con AR 201: correcto", ev(con({("MSH", 9): "ADT^A04^ADT_A01"}), log=[L04b], ack=H + "MSA|AR|MSG1\nERR|||201|E", canon=None),
   0, "correcto")
PID2 = "PID|1||ID2^^^HOSP^MR||Otro^Uno||19600910|M"
r = vv("V21 segundo PID en orden, AA [S14]: fallo_silencioso", ev(B[:3] + [PID2] + B[3:]), 1, "fallo_silencioso", "aceptado_imposible")
mira("V21: firme, literal, sin alternativa, origen acuse+mapeador",
     ([h["estado"] for h in cuentan(r)], r["veredicto"]["certeza"], r["veredicto"]["alternativa"], cuentan(r)[0]["origen"]),
     (["firme"], "literal", None, ["acuse", "mapeador"]))
vv("V22 EVN-2 vacío aceptado [S6]: correcto", ev(con({("EVN", 2): ""})), 0, "correcto")
lar = "M" * 25
vv("V23 MSH-10 de 25, MSA-2 con 20, Truncado=1: correcto",
   ev(con({("MSH", 10): lar}), log=[dict(L01, texto=L01["texto"].replace("MSG1", lar))], ack=H + "MSA|AA|" + lar[:20],
      canon=dict(CAN, MsgControlId=lar, Truncado=1)), 0, "correcto")
vv("V24 MSA-2 que no hace eco: fallo_silencioso/inservible", ev(ack=H + "MSA|AA|MSG9"), 1, "fallo_silencioso", "inservible")
r = vv("V25 AL/AL con AA [S13]: correcto", ev(con({("MSH", 15): "AL", ("MSH", 16): "AL"})), 0, "correcto")
mira("V25: sin menores (no hay D5)", [h for h in r["hallazgos"] if not h["cuenta"] and h["clase"] == "acuse"], [])
e26 = ev(con({("PID", 8): "X"}), log=[LOST, L01], conexion=[X01, "no llegó ACK (el emisor dejó de esperar a los 10.0 s)"], ack=None,
         canon=dict(CAN, Gender="unknown"))
vv("V26 fusión: PID-8 (mapeador + acuse) y existencia -> 2, ambos/aceptado_imposible+ausente", e26, 2, "ambos",
   "aceptado_imposible+ausente")

# ============================================================ S6-S18 (diseno-s6-s16-fable.md)
TIEMPO = "no llegó ACK (el emisor dejó de esperar a los 10.0 s)"
e = ev(log=[], conexion=[X01, TIEMPO], ack=None, canon=None)
d0 = [z for z in AR.comparar(e) if z["id"] == "D0"]
c, r = ver(e)
mira("N21 [S11] sin ACK por tiempo: AA, D0 tiempo, fallo_entorno literal",
     (esp(e), d0 and d0[0]["causa"], c, r["veredicto"]["certeza"]), (("si", "AA", None), "entorno:tiempo", "fallo_entorno", "literal"))
c, r = ver(ev(log=[], conexion=[X01], ack=None, canon=None))
mira("N21c sin ACK y sin causa: acuse_incorrecto/ausente", (c, r["veredicto"]["subtipo"]), ("acuse_incorrecto", "ausente"))
E02_1 = "FHIR contestó a las peticiones del circuito con error 503, cada una con probabilidad 1.0"
e = ev(entorno=[E02_1])
c, r = ver(e)
mira("N22 [A-18] E02 antiguo p=1.0 + L01 + AA: correcto; no decide; una nota [A-18] y ninguna S12 ni contradicción",
     (esp(e), c, [z["decide"] for z in lect(e)["entorno"]], [n for n in r["lectura"]["arnes_inexacto"] if "[A-18]" in n] != [],
      any("S12" in n for n in r["lectura"]["arnes_inexacto"]), r["lectura"]["contradictorio"]),
     (("si", "AA", None), "correcto", [False], True, False, []))
E09 = "el componente que escribe en fhir estaba deshabilitado"
e = ev(entorno=[E09])
mira("N22 control: un entorno que sí decide (E09) contradicho por L01 sigue dejando la nota [S12]",
     any("S12" in n for n in ver(e)[1]["lectura"]["arnes_inexacto"]), True)
CRED_X = "la credencial con la que el circuito llama a FHIR pasó a ser la de un usuario que no existe tras el mensaje 1"
L05_404 = fila("Error", 'FHIR rechazo el recurso (MSH-10=MSG1): FHIR devolvio 404: {"resourceType": "OperationOutcome"}')
e = ev(log=[L05_404], entorno=[CRED_X], ack=H + "MSA|AR|MSG1\nERR|||207|E", canon=None)
mira("N26x credencial de un usuario que no existe + 404 + AR 207: correcto; E06 sin vocabulario nuevo",
     (ver(e)[0], lect(e)["entorno"][0]["id"], lect(e)["vocabulario_nuevo"]), ("correcto", "E06", []))
mira("N26x control: «estaba vacía» sin momento, log vacío -> sigue decidiendo AR 207",
     esp(ev(log=[], entorno=["la credencial con la que el circuito llama a FHIR estaba vacía"], canon=None)), ("si", "AR", "207"))
e = copy.deepcopy(e11)
e["entorno"] = ["el circuito entero (la producción) se paró tras el mensaje 3 y se volvió a arrancar 2 s después, durante el lote"]
mira("N27x reinicio con momento + conexión rechazada: sin_intercambio; E03' con desde y seg",
     (ver(e)[0], lect(e)["entorno"][0]["id"], lect(e)["entorno"][0]["datos"]), ("sin_intercambio", "E03'", {"desde": "3", "seg": "2"}))
BORRADA = "la fila F de la tabla de consulta del sexo se borró (sin traducción para ese valor)"
r = vv("N28x [S41] fila F borrada, PID-8 F guardado unknown: fallo_entorno/tabla",
       ev(con({("PID", 8): "F"}), entorno=[BORRADA], canon=dict(CAN, Gender="unknown")), 1, "fallo_entorno", "tabla")
vv("N28x control: la fila borrada es F; PID-8 M guardado female sigue siendo del circuito",
   ev(con({("PID", 8): "M"}), entorno=[BORRADA], canon=dict(CAN, Gender="female")), 1, "fallo_silencioso", "guardado")
e = ev(entorno=["las peticiones POST del circuito a FHIR (reintentos incluidos) se retrasaron 20 s antes de llegar a FHIR, "
                "cada una con probabilidad 0.5; FHIR las atendió con normalidad"], conexion=[X01, "ACK recibido a los 20.2 s del envío"])
mira("N11' retraso con el texto nuevo y 201 -> AA; E01' que no decide", (esp(e), [(z["id"], z["decide"]) for z in lect(e)["entorno"]]),
     (("si", "AA", None), [("E01'", False)]))
X03 = "la conexión no se estableció: ConnectionRefusedError: [Errno 111] Connection refused"
e = ev(conexion=[X03], ack=None, canon=None)
mira("N23 X03 + L01: contradictorio, indeterminado (antes sin_intercambio)", (bool(lect(e)["contradictorio"]), ver(e)[0]),
     (True, "indeterminado"))
mira("N24 L03 y L01 para el mismo MSH-10: indeterminado", ver(ev(log=[L03, L01], canon=None))[0], "indeterminado")

r = vv("V27 [S8] escape \\S\\ guardado sin resolver: fallo_silencioso/guardado",
       ev(con({("PID", 5): "Ferr\\S\\Soler^Ana"}), canon=dict(CAN, FamilyName="Ferr\\S\\Soler", GivenName="Ana")),
       1, "fallo_silencioso", "guardado")
mira("V27: evidencia escape_sin_resolver", cuentan(r)[0]["evidencia"].get("escape_sin_resolver"), True)
vv("V27c escape resuelto: correcto", ev(con({("PID", 5): "Ferr\\S\\Soler^Ana"}), canon=dict(CAN, FamilyName="Ferr^Soler", GivenName="Ana")),
   0, "correcto")
MU = con({("PID", 5): "Mu<0xF1>oz^Ana"})
r = vv("V28 [S9] <0xF1> y canónico Muñoz: correcto", ev(MU, canon=dict(CAN, FamilyName="Muñoz", GivenName="Ana")), 0, "correcto")
mira("V28: tolerancia S9", [h["subtipo"] for h in r["hallazgos"] if h["clase"] == "tolerancia"], ["S9"])
r = vv("V28b canónico Mu?oz: fallo_silencioso/guardado", ev(MU, canon=dict(CAN, FamilyName="Mu?oz", GivenName="Ana")),
       1, "fallo_silencioso", "guardado")
mira("V28b: literal, descodificado", (r["veredicto"]["certeza"], cuentan(r)[0]["evidencia"].get("descodificado")), ("literal", True))
MU87 = con({("PID", 5): "Mu<0xF1>oz^Ana", ("MSH", 18): "ISO IR87"})
r = vv("V28c MSH-18 ISO IR87 + Mu?oz: fallo_silencioso/guardado", ev(MU87, canon=dict(CAN, FamilyName="Mu?oz", GivenName="Ana")),
       1, "fallo_silencioso", "guardado")
mira("V28c: certeza AMB-10, alternativa correcto", (r["veredicto"]["certeza"], r["veredicto"]["alternativa"]),
     ("ambiguedad AMB-10", "correcto"))
NUL = con({("PID", 5): "<0xC0><0x80>Señor^Ana"})
r = vv("V29 [S10] NUL overlong aceptado: fallo_silencioso/aceptado_imposible", ev(NUL, canon=dict(CAN, FamilyName="Señor", GivenName="Ana")),
       1, "fallo_silencioso", "aceptado_imposible")
mira("V29: valor_imposible_aceptado, acuse+mapeador, literal", (cuentan(r)[0]["clase"], cuentan(r)[0]["origen"], r["veredicto"]["certeza"]),
     ("valor_imposible_aceptado", ["acuse", "mapeador"], "literal"))
vv("V29c NUL overlong con AE 102: correcto", ev(NUL, log=[], ack=H + "MSA|AE|MSG1\nERR|||102|E", canon=None), 0, "correcto")
vv("V30 [S14] segundo PID con AE 100: correcto", ev(B[:3] + [PID2] + B[3:], log=[], ack=H + "MSA|AE|MSG1\nERR|||100|E", canon=None),
   0, "correcto")
r = vv("V30b segundo PID y PID-8 X aceptados: 2 hallazgos", ev(B[:2] + [AR._campo_set(B[2], 8, "X"), PID2] + B[3:],
       canon=dict(CAN, Gender="unknown")), 2, "fallo_silencioso")
mira("V30b: hechos PID y PID-8", sorted(h["hecho"] for h in cuentan(r)), ["PID", "PID-8"])
DOS = "<VT>" + "\n".join(B) + "\n" + "\n".join(B2) + "\n<FS>"
r = vv("V31 [S15] dos mensajes, un ACK, sin L11: acuse_incorrecto/recuento", ev(mensaje=DOS), 1, "acuse_incorrecto", "recuento")
mira("V31: literal", r["veredicto"]["certeza"], "literal")
e = ev(mensaje=DOS, ack=AA + "\n" + H + "MSA|AA|MSG2")
e["sesiones"].append({"log": [dict(L01, texto=L01["texto"].replace("MSG1", "MSG2"))], "canonico": dict(CAN, MsgControlId="MSG2")})
vv("V31c dos mensajes, dos ACK, dos sesiones: correcto", e, 0, "correcto")
L05_422 = fila("Warning", "FHIR rechazo el recurso (MSH-10=MSG1): FHIR devolvio 422:")
r = vv("V32 [S16] 422 con AA: fallo_silencioso/aceptacion_falsa", ev(log=[L05_422]), 1, "fallo_silencioso", "aceptacion_falsa")
mira("V32: literal, sin alternativa", (r["veredicto"]["certeza"], r["veredicto"]["alternativa"]), ("literal", None))
vv("V32c 422 con AR 207: correcto", ev(log=[L05_422], ack=H + "MSA|AR|MSG1\nERR|||207|E", canon=None), 0, "correcto")
r = vv("V33 [S6] EVN-2 vacío y PV1-2 Z con AA: correcto", ev(con({("EVN", 2): "", ("PV1", 2): "Z"})), 0, "correcto")
mira("V33: dos notas S6", sum("[S6]" in n for n in r["esperado"][0]["notas"]), 2)
vv("V33c sin PV1 con AA: fallo_silencioso/aceptado_imposible", ev(B[:3]), 1, "fallo_silencioso", "aceptado_imposible")
INV = con({("PID", 5): "Apellido\u200b^Nombre"})
vv("V34 [S7] invisible conservado: correcto", ev(INV, canon=dict(CAN, FamilyName="Apellido\u200b")), 0, "correcto")
r = vv("V34c invisible perdido: fallo_silencioso/guardado", ev(INV, canon=dict(CAN, FamilyName="Apellido")), 1, "fallo_silencioso", "guardado")
mira("V34c: literal, evidencia invisible", (r["veredicto"]["certeza"], cuentan(r)[0]["evidencia"].get("invisible")), ("literal", True))
r = vv("V35 [S8/S18] PID-7 futura aceptada: fallo_silencioso/aceptado_imposible",
       ev(con({("PID", 7): "20991231"}), canon=dict(CAN, BirthDate="2099-12-31")), 1, "fallo_silencioso", "aceptado_imposible")
mira("V35: valor_imposible_aceptado; esperado AE [S18]", (cuentan(r)[0]["clase"], r["esperado"][0]["msa1"]), ("valor_imposible_aceptado", "AE"))
r = vv("V35c PID-7 futura con MSH-7 vacío: correcto + nota L16",
       ev(con({("PID", 7): "20991231", ("MSH", 7): ""}), canon=dict(CAN, BirthDate="2099-12-31")), 0, "correcto")
mira("V35c: notas L16 y S6", (any("L16" in n for n in r["esperado"][0]["notas"]), any("[S6]: 101 MSH-7" in n for n in r["esperado"][0]["notas"])),
     (True, True))
vv("V36 [S18] PID-7 futura rechazada con AE 102: correcto",
   ev(con({("PID", 7): "20991231"}), log=[], ack=H + "MSA|AE|MSG1\nERR|||102|E", canon=None), 0, "correcto")

# ============================================================ S19-S29 y ficha (diseno-s19-s21-fable.md)
import lectura_evidencia as LE
E05 = "en la tabla de consulta del sexo, las filas F, M daban 'unknown'"
lec = LE.leer({"entorno": [E04, E05]}, ["MSG1"])
mira("N25 tabla_sexo y explica_gender", ([(z["id"], z["de"], z["a"]) for z in lec["tabla_sexo"]],
     [(LE.explica_gender(lec, *a) or {}).get("id") for a in (("F", "male"), ("m", "unknown"), ("F", "other"), ("M", "male"))]),
     ([("E04", {"F"}, "male"), ("E05", {"F", "M"}, "unknown")], ["E04", "E05", None, None]))
F_ = con({("PID", 8): "F"})
r = vv("V37 [S20] tabla + ACK perdido por tiempo: fallo_entorno/ausente+tabla",
       ev(F_, log=[LOST, L01], entorno=[E04], conexion=[X01, TIEMPO], ack=None, canon=dict(CAN, Gender="male")), 2, "fallo_entorno", "ausente+tabla")
mira("V37: todo entorno", {h["clase"] for h in cuentan(r)}, {"entorno"})
r = vv("V38 [S23] tabla + nombre mal guardado: ambos/guardado+tabla", ev(F_, entorno=[E04], canon=dict(CAN, Gender="male", FamilyName="Apelido")),
       2, "ambos", "guardado+tabla")
mira("V38: PID-5 fidelidad sin causa, PID-8 entorno", sorted((h["hecho"], h["clase"], h["causa"]) for h in cuentan(r)),
     [("PID-5", "fidelidad", None), ("PID-8", "entorno", "entorno:tabla")])
r = vv("V38c PID-8 M con E04 F -> male y Gender female: fallo_silencioso/guardado", ev(entorno=[E04], canon=dict(CAN, Gender="female")),
       1, "fallo_silencioso", "guardado")
mira("V38c: fidelidad sin causa, entorno_no_explica E04", (cuentan(r)[0]["clase"], cuentan(r)[0]["causa"],
     cuentan(r)[0]["evidencia"].get("entorno_no_explica", "")[:3]), ("fidelidad", None, "E04"))
vv("V39 PID-8 X con E04: la tabla no absuelve un 103", ev(con({("PID", 8): "X"}), entorno=[E04], canon=dict(CAN, Gender="unknown")),
   1, "fallo_silencioso", "aceptado_imposible")
vv("V40 [S20] E05 F,M -> unknown y Gender unknown: fallo_entorno/tabla", ev(F_, entorno=[E05], canon=dict(CAN, Gender="unknown")),
   1, "fallo_entorno", "tabla")
vv("V40c E05 y Gender other: fallo_silencioso/guardado", ev(F_, entorno=[E05], canon=dict(CAN, Gender="other")), 1, "fallo_silencioso", "guardado")
r = vv("V41 E04 y PID-8 f: fallo_entorno/tabla + S4", ev(con({("PID", 8): "f"}), entorno=[E04], canon=dict(CAN, Gender="male")),
       1, "fallo_entorno", "tabla")
mira("V41: tolerancia S4", [h["subtipo"] for h in r["hallazgos"] if h["clase"] == "tolerancia"][:1], ["S4"])
vv("V42 tabla + MSA-2 sin eco: fallo_silencioso/inservible+tabla", ev(F_, entorno=[E04], ack=H + "MSA|AA|MSG9", canon=dict(CAN, Gender="male")),
   2, "fallo_silencioso", "inservible+tabla")
vv("V42c E04 y AE 103 sin canónico: acuse_incorrecto/falso_rechazo", ev(F_, log=[], entorno=[E04], ack=H + "MSA|AE|MSG1\nERR|||103|E", canon=None),
   1, "acuse_incorrecto", "falso_rechazo")
V26_ = con({("MSH", 12): "2.6"})
r = vv("V43 [S19] 2.6 rechazado con AR 203: acuse_incorrecto/falso_rechazo", ev(V26_, log=[], ack=H + "MSA|AR|MSG1\nERR|||203|E", canon=None),
       1, "acuse_incorrecto", "falso_rechazo")
mira("V43: hecho ACK, literal", (cuentan(r)[0]["hecho"], r["veredicto"]["certeza"]), ("ACK", "literal"))
vv("V43c 2.3 con AR 203: correcto", ev(con({("MSH", 12): "2.3"}), log=[], ack=H + "MSA|AR|MSG1\nERR|||203|E", canon=None), 0, "correcto")
r = vv("V44 2.6 aceptado y guardado: correcto", ev(V26_), 0, "correcto")
mira("V44: nota S19", any("[S19]" in n for n in r["esperado"][0]["notas"]), True)
L05_400b = L05_400
r = vv("V45 [S21] NUL + 400 + AR 102: correcto con tolerancia S21", ev(NUL, log=[L05_400b], ack=H + "MSA|AR|MSG1\nERR|||102|E", canon=None),
       0, "correcto")
tl = [h for h in r["hallazgos"] if h["clase"] == "tolerancia" and h["subtipo"] == "S21"]
mira("V45: tolerancia S21 PID-5, http 400, literal", ([(h["hecho"], h["causa"], h["evidencia"].get("http")) for h in tl], r["veredicto"]["certeza"]),
     ([("PID-5", "rechazo_del_destino", 400)], "literal"))
r = vv("V45b [S24] PID-8 X + 400 + AR 103: correcto", ev(con({("PID", 8): "X"}), log=[L05_400b], ack=H + "MSA|AR|MSG1\nERR|||103|E", canon=None),
       0, "correcto")
mira("V45b: literal, tolerancia S21 PID-8", (r["veredicto"]["certeza"], [h["hecho"] for h in r["hallazgos"] if h["subtipo"] == "S21"]),
     ("literal", ["PID-8"]))
vv("V45c NUL + 400 + AE 102: correcto", ev(NUL, log=[L05_400b], ack=H + "MSA|AE|MSG1\nERR|||102|E", canon=None), 0, "correcto")
for vid, log, ack in (("V46", [L05_400b], "AR|MSG1\nERR|||207|E"), ("V46c", [], "AR|MSG1\nERR|||102|E"),
                      ("V46d", [L06], "AR|MSG1\nERR|||102|E"), ("V46e", [L01], "AR|MSG1\nERR|||102|E")):
    vv("%s NUL + %s + %s: acuse_incorrecto/codigo" % (vid, (log[0]["texto"][:30] if log else "sin log"), ack[:2]),
       ev(NUL, log=log, ack=H + "MSA|" + ack, canon=None), 1, "acuse_incorrecto", "codigo")
vv("V46f NUL + 400 + AR 102 con canónico: correcto", ev(NUL, log=[L05_400b], ack=H + "MSA|AR|MSG1\nERR|||102|E",
   canon=dict(CAN, FamilyName="Señor", GivenName="Ana")), 0, "correcto")
X_ = con({("PID", 8): "X"})
r = vv("V47 [S25] X + 503 + AR 207: correcto", ev(X_, log=[L06], ack=H + "MSA|AR|MSG1\nERR|||207|E", canon=None), 0, "correcto")
mira("V47: literal, nota S25", (r["veredicto"]["certeza"], any("[S25]" in n for n in r["esperado"][0]["notas"])), ("literal", True))
r = vv("V47b [S28] X + 503 + AE 103: correcto con tolerancia S28", ev(X_, log=[L06], ack=H + "MSA|AE|MSG1\nERR|||103|E", canon=None), 0, "correcto")
mira("V47b: tolerancia S28 PID-8, literal", ([h["hecho"] for h in r["hallazgos"] if h["subtipo"] == "S28"], r["veredicto"]["certeza"]),
     (["PID-8"], "literal"))
r = vv("V47c X + 503 + AA + Gender unknown: fallo_silencioso/aceptacion_falsa+aceptado_imposible",
       ev(X_, log=[L06], canon=dict(CAN, Gender="unknown")), 2, "fallo_silencioso", "aceptacion_falsa+aceptado_imposible")
mira("V47c: PID-8 fusionado y destino", sorted((h["hecho"], h["clase"], tuple(h["origen"])) for h in cuentan(r)),
     [("PID-8", "valor_imposible_aceptado", ("acuse", "mapeador")), ("destino", "acuse", ("acuse",))])
r = vv("V47d PID-3 vacío + E07 + AA: fallo_silencioso/aceptacion_falsa+aceptado_imposible",
       ev(con({("PID", 3): ""}), log=[], entorno=[E07], canon=dict(CAN, Identifier="")), 2, "fallo_silencioso", "aceptacion_falsa+aceptado_imposible")
h3 = [h for h in cuentan(r) if h["hecho"] == "PID-3"]
mira("V47d: PID-3 contenido de origen acuse, contenido no acusado", [(h["clase"], h["origen"], h["que"][0][:26]) for h in h3],
     [("contenido", ["acuse"], "contenido no acusado [S25]")])
vv("V47e X + 400 + AR 103: correcto", ev(X_, log=[L05_400b], ack=H + "MSA|AR|MSG1\nERR|||103|E", canon=None), 0, "correcto")
vv("V47f X + 400 + AR 207: acuse_incorrecto/codigo", ev(X_, log=[L05_400b], ack=H + "MSA|AR|MSG1\nERR|||207|E", canon=None),
   1, "acuse_incorrecto", "codigo")
vv("V47g X + timeout + CE fabricado: acuse_incorrecto/fabricado", ev(X_, log=L08 + [CE], ack=H + "MSA|CE|MSG1", canon=None),
   1, "acuse_incorrecto", "fabricado")
X26 = con({("MSH", 12): "2.6", ("PID", 8): "X"})
r = vv("V48 [S22] 2.6 + X + AA + unknown: correcto", ev(X26, canon=dict(CAN, Gender="unknown")), 0, "correcto")
mira("V48: tolerancias S22 del acuse y del mapeador, sin err", ([h["subtipo"] for h in r["hallazgos"] if h["clase"] == "tolerancia"],
     r["esperado"][0]["err"]), (["S22", "S22"], []))
vv("V48b 2.4 + X + AA: fallo_silencioso/aceptado_imposible", ev(con({("MSH", 12): "2.4", ("PID", 8): "X"}), canon=dict(CAN, Gender="unknown")),
   1, "fallo_silencioso", "aceptado_imposible")
r = vv("V48c 2.6 + X + Gender X: fallo_silencioso/guardado", ev(X26, canon=dict(CAN, Gender="X")), 1, "fallo_silencioso", "guardado")
mira("V48c: PID-8, valueset", (cuentan(r)[0]["hecho"], cuentan(r)[0]["evidencia"].get("valueset")), ("PID-8", True))
r = vv("V48d [S26] 2.6 + X + AE 103: correcto", ev(X26, log=[], ack=H + "MSA|AE|MSG1\nERR|||103|E", canon=None), 0, "correcto")
mira("V48d: tolerancias S22 y S26 en PID-8", sorted((h["subtipo"], h["hecho"]) for h in r["hallazgos"] if h["clase"] == "tolerancia"),
     [("S22", "PID-8"), ("S26", "PID-8")])
r = vv("V48e 2.6 + X + E04 X -> male + Gender male: correcto", ev(X26, entorno=["una fila de la tabla de consulta del sexo cambió: X -> 'male'"],
       canon=dict(CAN, Gender="male")), 0, "correcto")
mira("V48e: tolerancia S22", "S22" in [h["subtipo"] for h in r["hallazgos"] if h["clase"] == "tolerancia"], True)
r = vv("V49 [S26] 2.6 + X + AE 103 sin log: correcto", ev(X26, log=[], ack=H + "MSA|AE|MSG1\nERR|||103|E", canon=None), 0, "correcto")
mira("V49: S22 y S26, esperado AA", (sorted(h["subtipo"] for h in r["hallazgos"] if h["clase"] == "tolerancia"), r["esperado"][0]["msa1"]),
     (["S22", "S26"], "AA"))
vv("V49c 2.6 + X + AE 102: acuse_incorrecto/falso_rechazo", ev(X26, log=[], ack=H + "MSA|AE|MSG1\nERR|||102|E", canon=None),
   1, "acuse_incorrecto", "falso_rechazo")
r = vv("V50 [S28] X + 503 + AE 103: correcto", ev(X_, log=[L06], ack=H + "MSA|AE|MSG1\nERR|||103|E", canon=None), 0, "correcto")
mira("V50: tolerancia S28 PID-8, esperado AR", ([h["hecho"] for h in r["hallazgos"] if h["subtipo"] == "S28"], r["esperado"][0]["msa1"]),
     (["PID-8"], "AR"))
r = vv("V50c X + 503 + AE 102: acuse_incorrecto/codigo", ev(X_, log=[L06], ack=H + "MSA|AE|MSG1\nERR|||102|E", canon=None),
       1, "acuse_incorrecto", "codigo")
mira("V50c: hecho destino", cuentan(r)[0]["hecho"], "destino")
vv("V50d X + 503 + AA + unknown (= V47c)", ev(X_, log=[L06], canon=dict(CAN, Gender="unknown")), 2, "fallo_silencioso",
   "aceptacion_falsa+aceptado_imposible")


def seglineas(e):
    c_, r_ = ver(e)
    return [l for l in V.ficha("F", r_, e).split("\n") if l.startswith("SEGMENTOS  ")], r_


LEY = "  (? no reconocido, ! fuera de orden, + repetido; orden [E3 §3.3.1]: MSH EVN PID PV1)"
mira("F01 B: SEGMENTOS  MSH EVN PID PV1", seglineas(ev())[0], ["SEGMENTOS  MSH EVN PID PV1"])
ls, r = seglineas(ev([B[0], " " + B[1], B[3], B[2]]))
mira("F02 EVN con blanco y PV1 antes de PID", (ls, r["veredicto"]["categoria"], r["veredicto"]["subtipo"]),
     (["SEGMENTOS  MSH «·EVN»? PV1 PID! | faltan: EVN" + LEY], "fallo_silencioso", "aceptado_imposible"))
# DV-F02b: el diseño escribe «\tEVN»; la regla del mismo diseño manda el tabulador como \xNN
mira("F02b EVN con tabulador: «\\x09EVN»?", "«\\x09EVN»?" in seglineas(ev([B[0], "\t" + B[1], B[2], B[3]]))[0][0], True)
ls, r = seglineas(ev(B[:3] + ["ZPD|1|X", "NK1|1|Madre^Una"] + B[3:]))
mira("F03 ZPD y NK1: correcto", (ls, r["veredicto"]["categoria"]), (["SEGMENTOS  MSH EVN PID ZPD? NK1 PV1" + LEY], "correcto"))
mira("F04 segundo PID: PID+", "MSH EVN PID PID+ PV1" in seglineas(ev(B[:3] + [PID2] + B[3:]))[0][0], True)
mira("F04b PID tras PV1: PV1 PID!", "PV1 PID!" in seglineas(ev(B + [PID2]))[0][0], True)
# DV-F05: el nombre crudo es «PID1» (4 caracteres): la regla no le pone «…»; el diseño esperaba «PID1…». El
# identificador es XY9 porque «ID1» es subcadena de «PID1» y la comprobación de datos no distinguiría
ls = seglineas(ev([B[0], B[1], "PID1||XY9^^^HOSP^MR||Apellido^Nombre", B[3]]))[0][0]
mira("F05 PID sin separador: «PID1»?, faltan PID, sin datos", ("«PID1»?" in ls, "faltan: PID" in ls, any(x in ls for x in ("Apellido", "Nombre", "XY9"))),
     (True, True, False))
mira("F06 pid en minúscula: «pid»?", "«pid»?" in seglineas(ev([B[0], B[1], B[2].replace("PID", "pid", 1), B[3]]))[0][0], True)
fl = V.ficha("F", V.verificar(ev(mensaje=DOS)), ev(mensaje=DOS)).split("\n")
mira("F07 dos mensajes: dos SEGMENTOS, cada una tras su MENSAJE",
     [fl[i - 1].startswith("MENSAJE") for i, l in enumerate(fl) if l.startswith("SEGMENTOS")], [True, True])

# ============================================================ S30 (diseno-s30-fable.md)
FER = con({("PID", 5): "     Fernández^María Elena^Lucia^^^^L"})
CFER = dict(CAN, FamilyName="Fernández", GivenName="María Elena Lucia")


def tols(r):
    return [(h["subtipo"], h["hecho"]) for h in r["hallazgos"] if h["clase"] == "tolerancia"]


r51 = vv("V51 [S30] caso origen: correcto con tolerancia S30", ev(FER, canon=CFER), 0, "correcto")
mira("V51: tolerancia S30 en PID-5, literal", (tols(r51), r51["veredicto"]["certeza"]), ([("S30", "PID-5")], "literal"))
r = vv("V51b blancos conservados: correcto sin tolerancias", ev(FER, canon=dict(CFER, FamilyName="     Fernández")), 0, "correcto")
mira("V51b: sin tolerancias", tols(r), [])
r = vv("V51c letra recortada: fallo_silencioso/guardado", ev(FER, canon=dict(CFER, FamilyName="ernández")), 1, "fallo_silencioso", "guardado")
mira("V51c: literal, sin alternativa", (r["veredicto"]["certeza"], r["veredicto"]["alternativa"]), ("literal", None))
r = vv("V51d blanco del medio quitado: fallo_silencioso/guardado", ev(FER, canon=dict(CFER, GivenName="MaríaElena Lucia")),
       1, "fallo_silencioso", "guardado")
mira("V51d: literal", r["veredicto"]["certeza"], "literal")
for vid, pid5, tol_, dec in (("V51e", "Fernández   ^María Elena^Lucia^^^^L", ("S32", "PID-5"), ["S32"]),
                             ("V51f", "\u00a0Fernández^María Elena^Lucia^^^^L", ("S30", "PID-5"), ["S30", "S33"]),
                             ("V51g", "Fernández^María Elena^ Lucia^^^^L", ("S34", "PID-5"), ["S34"])):
    r = vv("%s [%s]: correcto con tolerancia" % (vid, tol_[0]), ev(con({("PID", 5): pid5}), canon=CFER), 0, "correcto")
    mira("%s: tolerancia, decisiones, literal" % vid, (tols(r), [h["evidencia"].get("decisiones") for h in r["hallazgos"] if h["clase"] == "tolerancia"],
         r["veredicto"]["certeza"]), ([tol_], [dec], "literal"))
    if vid == "V51e":
        r51e, e51e = r, ev(con({("PID", 5): pid5}), canon=CFER)
r = vv("V51g-c PID-5.3 con blanco guardado tal cual: correcto", ev(con({("PID", 5): "Fernández^María Elena^ Lucia^^^^L"}),
       canon=dict(CFER, GivenName="María Elena  Lucia")), 0, "correcto")
mira("V51g-c: sin tolerancias", tols(r), [])
r = vv("V51h S10 manda: tabulador delante aceptado", ev(con({("PID", 5): "\tFernández^María Elena^Lucia^^^^L"}), canon=CFER),
       1, "fallo_silencioso", "aceptado_imposible")
mira("V51h: sin tolerancias del mapeador de PID-5", [t_ for t_ in tols(r) if t_[0] == "S30"], [])
LARGO = con({("PID", 5): "     " + "A" * 246 + "^N"})
r = vv("V51i S3+S30: truncado y sin blancos", ev(LARGO, canon=dict(CAN, FamilyName="A" * 245, GivenName="N", Truncado=1)), 0, "correcto")
t3 = [h for h in r["hallazgos"] if h["subtipo"] == "truncado_S3"]
mira("V51i: truncado_S3 en PID-5 con [S30]", [(h["hecho"], "[S30]" in h["que"][0]) for h in t3], [("PID-5", True)])
r = vv("V51i-b sin blancos y entero: correcto con S30", ev(LARGO, canon=dict(CAN, FamilyName="A" * 246, GivenName="N", Truncado=1)), 0, "correcto")
mira("V51i-b: tolerancia S30, sin truncado_S3", ([s for s, _ in tols(r)].count("S30"), [s for s, _ in tols(r)].count("truncado_S3")), (1, 0))
r = vv("V51i-c Truncado 0: fallo_silencioso/guardado en longitud", ev(LARGO, canon=dict(CAN, FamilyName="A" * 246, GivenName="N", Truncado=0)),
       1, "fallo_silencioso", "guardado")
mira("V51i-c: hecho longitud", cuentan(r)[0]["hecho"], "longitud")
XJ = con({("PID", 5): "\\X20\\Fernández^María Elena^Lucia^^^^L"})
r = vv("V51j S8+S30: \\X20\\ resuelto y quitado: correcto", ev(XJ, canon=CFER), 0, "correcto")
mira("V51j: tolerancia S30", [s for s, _ in tols(r)], ["S30"])
r = vv("V51j-b \\X20\\ sin resolver: fallo_silencioso/guardado", ev(XJ, canon=dict(CFER, FamilyName="\\X20\\Fernández")),
       1, "fallo_silencioso", "guardado")
mira("V51j-b: escape_sin_resolver", cuentan(r)[0]["evidencia"].get("escape_sin_resolver"), True)
r = vv("V51k PID-5 solo blancos aceptado: fallo_silencioso/aceptado_imposible", ev(con({("PID", 5): "     "}),
       canon=dict(CAN, FamilyName="", GivenName="")), 1, "fallo_silencioso", "aceptado_imposible")
mira("V51k: contenido de acuse en PID-5; tolerancia S30", ((cuentan(r)[0]["clase"], cuentan(r)[0]["hecho"], cuentan(r)[0]["origen"]),
     [s for s, _ in tols(r) if s == "S30"]), (("contenido", "PID-5", ["acuse"]), ["S30"]))
fl = V.ficha("F08", r51, ev(FER, canon=CFER)).split("\n")
mira("F08 ficha de V51: tolerancia S30 en menores, sin hallazgos",
     (any(l.startswith("menores, tolerancias y notas: ") and "tolerancia [S30] FamilyName: guardado sin los 5 blancos ini" in l for l in fl),
      any(l.startswith("[H") for l in fl)), (True, False))
fl = V.ficha("F08b", r51e, e51e).split("\n")
mira("F08b ficha de V51e: correcto literal y tolerancia [S32]", (any(l.startswith("VEREDICTO PROPUESTO: correcto  (certeza: literal)") for l in fl),
     any(l.startswith("menores, tolerancias y notas:") and "tolerancia [S32] FamilyName: guardado sin los 3 blancos finales" in l for l in fl)),
     (True, True))
# ============================================================ S31-S37 (diseno-s31-s34-fable.md)
ORIGEN = "<VT><VT>" + B[0] + "\n<FS>\n<VT>" + "\n".join(B[1:]) + "\n<FS>\n<FS>"
SIN_VT, SIN_FS = "\n".join(B) + "\n<FS>", "<VT>" + "\n".join(B) + "\n"
PARTIDA_EVN = "<VT>" + "\n".join(B[:2]) + "\n<FS><VT>" + "\n".join(B[2:]) + "\n<FS>"
PARTIDA_PV1 = "<VT>" + "\n".join(B[:3]) + "\n<FS><VT>" + B[3] + "\n<FS>"
PARTIDA_PV1_X = "<VT>" + "\n".join(B[:2] + [AR._campo_set(B[2], 8, "X")]) + "\n<FS><VT>" + B[3] + "\n<FS>"
HUERFANO = "<VT>EVN|A01|x\n<FS><VT>" + "\n".join(B) + "\n<FS>"
AK101 = H + "MSA|AR|MSG1\nERR|||101|E"
r = vv("V52 [S31] caso origen: correcto con tolerancia S31", ev(mensaje=ORIGEN, log=[L03], ack=AK101, canon=None), 0, "correcto")
mira("V52: tolerancia S31 en trama, literal, esperado AE 100 x3, no intentado, trama",
     (tols(r), r["veredicto"]["certeza"], [z["err3"] for z in r["esperado"][0]["err"]], r["lectura"]["resultado_destino"][0]["destino"],
      r["trama"]["sin_msh"]), ([("S31", "trama")], "literal", ["100", "100", "100"], "no_intentado", [2]))
r52 = r
r = vv("V52b AE 100: correcto sin tolerancias", ev(mensaje=ORIGEN, log=[L03], ack=H + "MSA|AE|MSG1\nERR|||100|E", canon=None), 0, "correcto")
mira("V52b: sin tolerancias de trama", [x_ for x_ in tols(r) if x_[1] == "trama"], [])
r = vv("V52c AR 207: acuse_incorrecto/codigo", ev(mensaje=ORIGEN, log=[L03], ack=H + "MSA|AR|MSG1\nERR|||207|E", canon=None),
       1, "acuse_incorrecto", "codigo")
mira("V52c: hecho EVN, literal", (cuentan(r)[0]["hecho"], r["veredicto"]["certeza"]), ("EVN", "literal"))
for ack_ in ("MSA|AE|MSG1\nERR|||101|E", "MSA|AR|MSG1\nERR|||100|E"):
    r = vv("V52d [S35] %s: correcto" % ack_[:6], ev(mensaje=ORIGEN, log=[L03], ack=H + ack_, canon=None), 0, "correcto")
    mira("V52d %s: tolerancia S35, literal" % ack_[:6], ([x_ for x_ in tols(r) if x_[1] == "trama"], r["veredicto"]["certeza"]),
         ([("S35", "trama")], "literal"))
r = vv("V52e AA al marco con solo MSH: fallo_silencioso/aceptado_imposible", ev(mensaje=ORIGEN, log=[], canon=None), 1, "fallo_silencioso",
       "aceptado_imposible")
mira("V52e: estructura EVN, literal", (cuentan(r)[0]["clase"], cuentan(r)[0]["hecho"], r["veredicto"]["certeza"]), ("estructura", "EVN", "literal"))
r = vv("V52f [S36] MSH+EVN | PID+PV1 con AR 101: correcto", ev(mensaje=PARTIDA_EVN, log=[L03], ack=AK101, canon=None), 0, "correcto")
mira("V52f: tolerancia S36, literal", ([x_ for x_ in tols(r) if x_[1] == "trama"], r["veredicto"]["certeza"]), ([("S36", "trama")], "literal"))
r = vv("V52f-b reensamblado con AA: fallo_silencioso, 5 hallazgos", ev(mensaje=PARTIDA_EVN), 5, "fallo_silencioso")
mira("V52f-b: hechos, literal", (sorted(h["hecho"] for h in cuentan(r)), r["veredicto"]["certeza"], r["veredicto"]["alternativa"]),
     (["PID", "PID-3", "PID-5", "PID-7", "PID-8"], "literal", None))
for cab in (SIN_VT, SIN_FS):
    r = vv("V52g control oro %s: correcto" % ("SIN_VT" if cab == SIN_VT else "SIN_FS"), ev(mensaje=cab), 0, "correcto")
    mira("V52g %s: nota [A-2]" % ("SIN_VT" if cab == SIN_VT else "SIN_FS"), any(n.startswith("[A-2]") for n in r["esperado"][0]["notas"]), True)
vv("V52g-b S15 intacto (= V31)", ev(mensaje=DOS), 1, "acuse_incorrecto", "recuento")
r = vv("V52h ACK sobrante: correcto", ev(mensaje=ORIGEN, log=[L03], ack=AK101 + "\n" + H + "MSA|AR|\nERR|||100|E", canon=None), 0, "correcto")
mira("V52h: menor trama", [(h["clase"], h["subtipo"], h["hecho"], h["cuenta"]) for h in r["hallazgos"] if not h["cuenta"] and h["clase"] == "trama"],
     [("trama", "trama", "existencia", False)])
r = vv("V52i marco huérfano delante: correcto", ev(mensaje=HUERFANO), 0, "correcto")
mira("V52i: trama y mensajes", (r["trama"]["sin_msh"], r["mensajes"]), ([1], [{"k": 0, "msh10": "MSG1"}]))
vv("V52j PID suelto detrás en otro marco: correcto", ev(mensaje="<VT>" + "\n".join(B) + "\n<FS><VT>" + PID2 + "\n<FS>"), 0, "correcto")
e = ev(mensaje=ORIGEN, log=[L03, {"tipo": "Warning", "componente": "AdtTcpIn", "texto": "Discarding leftover input 'EVN|A01|20230101171416'"}],
       ack=AK101, canon=None)
mira("N26 resto descartado sin MSH-10: correcto, sin causas D0", (ver(e)[0], lect(e)["por_mensaje"][0]["causas_d0"]), ("correcto", []))
r = vv("V53 [S37] U+2028 delante: correcto", ev(con({("PID", 5): "\u2028Fernández^María Elena^Lucia^^^^L"}), canon=CFER), 0, "correcto")
mira("V53: tolerancia S30 con S33", (tols(r), [h["evidencia"].get("decisiones") for h in r["hallazgos"] if h["clase"] == "tolerancia"]),
     ([("S30", "PID-5")], [["S30", "S33"]]))
vv("V53b control S7 (= V34c)", ev(INV, canon=dict(CAN, FamilyName="Apellido")), 1, "fallo_silencioso", "guardado")
r = vv("V53c combinado: correcto", ev(con({("PID", 5): "  Fernández  ^María Elena^ Lucia\u00a0^^^^L"}), canon=CFER), 0, "correcto")
mira("V53c: dos tolerancias", (tols(r), [h["evidencia"].get("decisiones") for h in r["hallazgos"] if h["clase"] == "tolerancia"]),
     ([("S30", "PID-5"), ("S32", "PID-5")], [["S30", "S32"], ["S32", "S33", "S34"]]))
r = vv("V53d MaríaElena: fallo_silencioso/guardado", ev(con({("PID", 5): "  Fernández  ^María Elena^ Lucia\u00a0^^^^L"}),
       canon=dict(CFER, GivenName="MaríaElena Lucia")), 1, "fallo_silencioso", "guardado")
mira("V53d: literal; sigue la tolerancia de FamilyName", (r["veredicto"]["certeza"], tols(r)), ("literal", [("S30", "PID-5")]))
r54 = vv("V54 [S35] AE 101: correcto", ev(mensaje=ORIGEN, log=[L03], ack=H + "MSA|AE|MSG1\nERR|||101|E", canon=None), 0, "correcto")
mira("V54: S35, literal", ([x_ for x_ in tols(r54) if x_[1] == "trama"], r54["veredicto"]["certeza"]), ([("S35", "trama")], "literal"))
r = vv("V54c AE 102: acuse_incorrecto/codigo", ev(mensaje=ORIGEN, log=[L03], ack=H + "MSA|AE|MSG1\nERR|||102|E", canon=None),
       1, "acuse_incorrecto", "codigo")
mira("V54c: EVN, literal", (cuentan(r)[0]["hecho"], r["veredicto"]["certeza"]), ("EVN", "literal"))
r = vv("V55 [S36] PARTIDA_PV1 + AR 101: correcto", ev(mensaje=PARTIDA_PV1, log=[L03], ack=AK101, canon=None), 0, "correcto")
mira("V55: S36, trama", ([x_ for x_ in tols(r) if x_[1] == "trama"], r["trama"]["sin_msh"]), ([("S36", "trama")], [2]))
r = vv("V55b PARTIDA_PV1_X + AR 103: acuse_incorrecto/codigo", ev(mensaje=PARTIDA_PV1_X, log=[], ack=H + "MSA|AR|MSG1\nERR|||103|E", canon=None),
       1, "acuse_incorrecto", "codigo")
mira("V55b: PV1, literal", (cuentan(r)[0]["hecho"], r["veredicto"]["certeza"]), ("PV1", "literal"))
r = vv("V55c sin partición + AR 101: acuse_incorrecto/codigo", ev(B[:3], log=[], ack=AK101, canon=None), 1, "acuse_incorrecto", "codigo")
mira("V55c: PV1, sin tolerancias de trama", (cuentan(r)[0]["hecho"], [x_ for x_ in tols(r) if x_[1] == "trama"]), ("PV1", []))
vv("V55d DOS en un marco (= V31)", ev(mensaje=DOS), 1, "acuse_incorrecto", "recuento")
r = vv("V56 [S37] U+2029 final: correcto", ev(con({("PID", 5): "Fernández\u2029^María Elena^Lucia^^^^L"}), canon=CFER), 0, "correcto")
mira("V56: S32 con S33", (tols(r), [h["evidencia"].get("decisiones") for h in r["hallazgos"] if h["clase"] == "tolerancia"]),
     ([("S32", "PID-5")], [["S32", "S33"]]))
vv("V56b control S7", ev(INV, canon=dict(CAN, FamilyName="Apellido")), 1, "fallo_silencioso", "guardado")
r = vv("V56c Cc U+001F: S10", ev(con({("PID", 5): "\x1fFernández^María Elena^Lucia^^^^L"}), canon=CFER), 1, "fallo_silencioso", "aceptado_imposible")
mira("V56c: sin tolerancias S3x", [s for s, _ in tols(r) if s.startswith("S3")], [])
fl = V.ficha("F09", r52, ev(mensaje=ORIGEN, log=[L03], ack=AK101, canon=None)).split("\n")
LT = "TRAMA    2 marcos: [1] MSH  [2] sin MSH: EVN PID PV1 (no es mensaje; L9/S31) | anomalías: marcador <VT> repetido (marco 1); marcador <FS> repetido (tras el marco 2)"
i_t = fl.index(LT) if LT in fl else -1
mira("F09 ficha: TRAMA antes del primer MENSAJE, SEGMENTOS, sin PID, tolerancia S31, sin datos",
     (i_t >= 0 and fl[i_t + 1].startswith("MENSAJE"), "SEGMENTOS  MSH | faltan: EVN PID PV1" in fl, any(l.startswith("         PID-3=") for l in fl),
      any(l.startswith("menores, tolerancias y notas:") and "tolerancia MSA-1 AR, esperado AE: aceptado [S31]" in l for l in fl),
      any(x_ in LT for x_ in ("Apellido", "Nombre", "ID1"))), (True, True, False, True, False))
mira("F09b ficha normal sin TRAMA", any(l.startswith("TRAMA") for l in V.ficha("F", V.verificar(ev()), ev()).split("\n")), False)
mira("F09c ficha SIN_VT", "TRAMA    1 marco: [1] MSH EVN PID PV1 | anomalías: marco 1 sin <VT>" in
     V.ficha("F", V.verificar(ev(mensaje=SIN_VT)), ev(mensaje=SIN_VT)).split("\n"), True)
fl = V.ficha("F10", r54, ev(mensaje=ORIGEN, log=[L03], ack=H + "MSA|AE|MSG1\nERR|||101|E", canon=None)).split("\n")
mira("F10 ficha de V54", (any(l.startswith("VEREDICTO PROPUESTO: correcto  (certeza: literal)") for l in fl),
     any(l.startswith("menores, tolerancias y notas:") and "tolerancia ERR-3 ['101'], esperado 100: aceptado [S35]" in l for l in fl)), (True, True))

# ============================================================ arreglo solo_msh (diseno-arreglo-solo-msh-fable.md)
# desviación declarada: base con MSH-18 al final (B[0] acaba en MSH-12 y el LF contaminaría la versión)
BL = [B[0] + "||||||UNICODE UTF-8"] + B[1:]
LF1 = "<VT>" + "<0x0A>".join(BL) + "<0x0A><FS>\n"
LF_PART = "<VT>" + BL[0] + "<0x0A>" + BL[1] + "\n<FS><VT>" + "\n".join(BL[2:]) + "\n<FS>"
LF_NK1 = "<VT>" + "<0x0A>".join(BL) + "<0x0A><FS><VT>NK1|1|x\n<FS>"
r57 = vv("V57 [E2 §2.5.4] LF en un marco con AR 101: acuse_incorrecto/codigo", ev(mensaje=LF1, log=[L03], ack=AK101, canon=None),
         1, "acuse_incorrecto", "codigo")
mira("V57: hecho EVN, sin tolerancias, literal, solo_msh falso", (cuentan(r57)[0]["hecho"], tols(r57), r57["veredicto"]["certeza"],
     AR.calcular(ev(mensaje=LF1, log=[L03], ack=AK101, canon=None))[0]["marco"]["solo_msh"]), ("EVN", [], "literal", False))
for ack_ in ("MSA|AE|MSG1\nERR|||101|E", "MSA|AR|MSG1\nERR|||100|E"):
    r = vv("V57b %s: acuse_incorrecto/codigo" % ack_[:6], ev(mensaje=LF1, log=[L03], ack=H + ack_, canon=None), 1, "acuse_incorrecto", "codigo")
    mira("V57b %s: hecho EVN, sin tolerancias" % ack_[:6], (cuentan(r)[0]["hecho"], tols(r)), ("EVN", []))
r = vv("V57c AE 100: correcto", ev(mensaje=LF1, log=[L03], ack=H + "MSA|AE|MSG1\nERR|||100|E", canon=None), 0, "correcto")
mira("V57c: sin tolerancias", tols(r), [])
r = vv("V57e partida con LF [S36]: correcto", ev(mensaje=LF_PART, log=[L03], ack=AK101, canon=None), 0, "correcto")
mira("V57e: tolerancia S36", tols(r), [("S36", "trama")])
r = vv("V57f LF entero | NK1: acuse_incorrecto/codigo", ev(mensaje=LF_NK1, log=[L03], ack=AK101, canon=None), 1, "acuse_incorrecto", "codigo")
mira("V57f: hecho EVN, sin tolerancias", (cuentan(r)[0]["hecho"], tols(r)), ("EVN", []))
fl = V.ficha("F11", r57, ev(mensaje=LF1, log=[L03], ack=AK101, canon=None)).split("\n")
mira("F11 ficha de V57: veredicto, SEGMENTOS con lo arrastrado, sin tolerancia S31, sin TRAMA",
     (any(l.startswith("VEREDICTO PROPUESTO: acuse_incorrecto/codigo  (certeza: literal)") for l in fl),
      "SEGMENTOS  MSH | faltan: EVN PID PV1 | tras control no CR: EVN PID PV1" in fl,
      any("tolerancia MSA-1 AR" in l for l in fl), any(l.startswith("TRAMA") for l in fl)), (True, True, False, False))

# ============================================================ citas, S38, S39 y MSH-18 (diseno-citas-s38-s39-fable.md)
GARCIA = "García^Lucía^Óscar^^^^L"
MOJI = dict(CAN, FamilyName="García".encode("utf-8").decode("latin-1"), GivenName="Lucía Óscar".encode("utf-8").decode("latin-1"))
BIEN = dict(CAN, FamilyName="García", GivenName="Lucía Óscar")


def notas39(r):
    return [h for h in r["hallazgos"] if h["clase"] == "nota" and h["subtipo"] == "S39"]


r58 = vv("V58 caso real: MSH-18 ASCII, PID-5 UTF-8, guardado mojibake: fallo_silencioso/guardado",
         ev(con({("MSH", 18): "ASCII", ("PID", 5): GARCIA}), canon=MOJI), 1, "fallo_silencioso", "guardado")
e58 = cuentan(r58)[0]["evidencia"]
mira("V58: banderas", (e58.get("no_ascii_distinto"), e58.get("invisible"), e58.get("invisible_observado"), e58.get("escape_en_entrada"),
     e58.get("clase_msh18"), r58["veredicto"]["certeza"]), (True, None, True, None, "ascii", "literal"))
mira("V58: nota S39", [(h["hecho"], h["cuenta"], h["que"][0]) for h in notas39(r58)],
     [("MSH-18", False, "[S39] MSH-18 = ASCII contradice los bytes del cable: caracteres fuera de 7-bit ASCII, UTF-8 válido, en PID-5 (nota menor, no cuenta)")])
r = vv("V58b UNICODE UTF-8 + mojibake: mismo veredicto", ev(con({("MSH", 18): "UNICODE UTF-8", ("PID", 5): GARCIA}), canon=MOJI),
       1, "fallo_silencioso", "guardado")
mira("V58b: sin nota S39", notas39(r), [])
r = vv("V58c 8859/1 + mojibake: mismo veredicto", ev(con({("MSH", 18): "8859/1", ("PID", 5): GARCIA}), canon=MOJI), 1, "fallo_silencioso", "guardado")
mira("V58c: nota S39 de un byte", [h["que"][0] for h in notas39(r)],
     ["[S39] MSH-18 = 8859/1 contradice los bytes del cable: UTF-8 multibyte válido en un juego de un byte, en PID-5 (nota menor, no cuenta)"])
r = vv("V58d ASCII puro, letra perdida: fallo_silencioso/guardado", ev(con({("MSH", 18): "ASCII", ("PID", 5): "Garcia^Lucia^^^^^L"}),
       canon=dict(CAN, FamilyName="Garca", GivenName="Lucia")), 1, "fallo_silencioso", "guardado")
mira("V58d: sin no_ascii_distinto, sin nota", (cuentan(r)[0]["evidencia"].get("no_ascii_distinto"), notas39(r)), (None, []))
r = vv("V58e ASCII + UTF-8 bien guardado: correcto", ev(con({("MSH", 18): "ASCII", ("PID", 5): GARCIA}), canon=BIEN), 0, "correcto")
mira("V58e: una nota S39", len(notas39(r)), 1)
r = vv("V59 (= V34c) invisible en la entrada", ev(INV, canon=dict(CAN, FamilyName="Apellido")), 1, "fallo_silencioso", "guardado")
mira("V59: invisible", cuentan(r)[0]["evidencia"].get("invisible"), True)
r = vv("V59b invisible solo en lo guardado", ev(con({("PID", 5): "Apellido^Nombre"}), canon=dict(CAN, FamilyName="Apellido\u200b")),
       1, "fallo_silencioso", "guardado")
mira("V59b: invisible_observado, no invisible", (cuentan(r)[0]["evidencia"].get("invisible"), cuentan(r)[0]["evidencia"].get("invisible_observado")),
     (None, True))
r = vv("V60 (= V27) escape sin resolver", ev(con({("PID", 5): "Ferr\\S\\Soler^Ana"}), canon=dict(CAN, FamilyName="Ferr\\S\\Soler", GivenName="Ana")),
       1, "fallo_silencioso", "guardado")
mira("V60: escape_en_entrada y sin resolver", (cuentan(r)[0]["evidencia"].get("escape_en_entrada"), cuentan(r)[0]["evidencia"].get("escape_sin_resolver")),
     (True, True))
r = vv("V60b escape resuelto y letra perdida", ev(con({("PID", 5): "Ferr\\S\\Soler^Ana"}), canon=dict(CAN, FamilyName="Ferr^Sole", GivenName="Ana")),
       1, "fallo_silencioso", "guardado")
mira("V60b: escape_en_entrada, no sin resolver", (cuentan(r)[0]["evidencia"].get("escape_en_entrada"), cuentan(r)[0]["evidencia"].get("escape_sin_resolver")),
     (True, None))
r = vv("V60c O'Brien guardado con escape añadido", ev(con({("PID", 5): "O'Brien^Ana"}), canon=dict(CAN, FamilyName="O\\'Brien", GivenName="Ana")),
       1, "fallo_silencioso", "guardado")
mira("V60c: sin escape_sin_resolver", cuentan(r)[0]["evidencia"].get("escape_sin_resolver"), None)
r = vv("V61 (= V28b) byte F1 sin MSH-18, Mu?oz", ev(MU, canon=dict(CAN, FamilyName="Mu?oz", GivenName="Ana")), 1, "fallo_silencioso", "guardado")
mira("V61: descodificado, sin no_ascii_distinto, nota S39 callada por S9", (cuentan(r)[0]["evidencia"].get("descodificado"),
     cuentan(r)[0]["evidencia"].get("no_ascii_distinto"), notas39(r)), (True, None, []))
r = vv("V61b UTF-8 declarado + byte F1, Mu?oz", ev(con({("PID", 5): "Mu<0xF1>oz^Ana", ("MSH", 18): "UNICODE UTF-8"}), canon=dict(CAN, FamilyName="Mu?oz", GivenName="Ana")),
       1, "fallo_silencioso", "guardado")
mira("V61b: nota S39 callada por S9", notas39(r), [])
r = vv("V61c 8859/1 + byte F1, Mu?oz", ev(con({("PID", 5): "Mu<0xF1>oz^Ana", ("MSH", 18): "8859/1"}), canon=dict(CAN, FamilyName="Mu?oz", GivenName="Ana")),
       1, "fallo_silencioso", "guardado")
mira("V61c: sin nota S39", notas39(r), [])
fl = V.ficha("F12", r58, ev(con({("MSH", 18): "ASCII", ("PID", 5): GARCIA}), canon=MOJI)).split("\n")
mira("F12 ficha del caso real: MSH-18 en MENSAJE y nota S39 en menores",
     (any(l.startswith("MENSAJE") and l.endswith("MSH-18=ASCII") for l in fl),
      any(l.startswith("menores, tolerancias y notas:") and "nota [S39] MSH-18 = ASCII" in l for l in fl)), (True, True))
mira("F12b ficha base: MSH-18 vacío", any(l.startswith("MENSAJE") and l.endswith("MSH-18=") for l in V.ficha("F", V.verificar(ev()), ev()).split("\n")), True)
e12 = ev(con({("MSH", 18): "ASCII", ("PID", 5): GARCIA}), canon=BIEN)
fl = V.ficha("F12d", V.verificar(e12), e12).split("\n")
mira("F12d correcto con la nota en menores", (any(l.startswith("VEREDICTO PROPUESTO: correcto") for l in fl),
     any(l.startswith("menores, tolerancias y notas:") and "nota [S39] MSH-18 = ASCII" in l for l in fl)), (True, True))

# ============================================================ S42 y S43 (diseno-s42-s43-fable.md §3)
def s42(e):
    return any("[S42]" in t for t in lect(e)["lectura_hallazgos"])


F3X = fila("Info", "algo nunca visto")
e = ev(log=[L01, F3X])
mira("N16d [S42] control con fila terminal: correcto, vocabulario nuevo, sin hallazgo de lectura",
     (ver(e)[0], bool(lect(e)["vocabulario_nuevo"]), lect(e)["lectura_hallazgos"]), ("correcto", True, []))
e = ev(log=[fila("Info", "algo nunca visto (MSH-10=OTRO)")])
mira("N16e [S42] F3 de otro mensaje: correcto con nota L5, sin hallazgo de lectura",
     (ver(e)[0], any("L5" in n for n in AR.calcular(e)[0]["notas"]), lect(e)["lectura_hallazgos"], bool(lect(e)["vocabulario_nuevo"])),
     ("correcto", True, [], True))
e = ev(log=[fila("Warning", "algo nunca visto")])
mira("N16f [S42] Warning desconocida sin terminal: indeterminado", (ver(e)[0], s42(e)), ("indeterminado", True))
e = ev(log=[fila("Info", "Paciente registrado en el servidor remoto con codigo de respuesta correcto")])
f = lect(e)["filas"][0]
mira("N16g [S42] el texto de RV-18: F3 sin MSH-10 -> indeterminado", (f["id"], f["msh10"], ver(e)[0], s42(e)),
     ("F3", None, "indeterminado", True))
b2 = [z.replace("MSG1", "MSG2") for z in AR._con({("MSH", 15): "AL", ("MSH", 16): "AL"})]
L01b = dict(L01, texto=L01["texto"].replace("MSG1", "MSG2"))
e = ev(mensaje="<VT>" + "\n".join(B) + "\n" + "\n".join(b2) + "\n<FS>", log=[L01, F3X])
mira("N16h [S42][DV-L3] dos mensajes, F3 de sesión y MSG2 sin terminal: indeterminado", (ver(e)[0], s42(e)), ("indeterminado", True))
e = ev(mensaje="<VT>" + "\n".join(B) + "\n" + "\n".join(b2) + "\n<FS>", log=[L01, L01b, F3X])
mira("N16h' control: los dos con terminal, sin hallazgo de lectura", lect(e)["lectura_hallazgos"], [])
e = ev(log=[F3X], conexion=["la conexión no se estableció: ConnectionRefusedError: [Errno 111] Connection refused"], ack=None, canon=None)
mira("N16i [S42] X03 + F3: sin_intercambio gana", ver(e)[0], "sin_intercambio")
e = ev(log=[F3X], entorno=[E07])
mira("N16j [S42] E07 + F3 sin terminal y AA: indeterminado, destino sistema",
     (ver(e)[0], lect(e)["por_mensaje"][0]["destino"]), ("indeterminado", "sistema"))
e = ev(log=L08 + [F3X], ack=H + "MSA|AR|MSG1\nERR|||207|E", canon=None)
mira("N16k [S42] L08 + F3 con AR 207: indeterminado; el esperado sigue AR 207", (ver(e)[0], esp(e)), ("indeterminado", ("si", "AR", "207")))
e = ev(log=[F3X], conexion=[X01, "no llegó ACK (el emisor dejó de esperar a los 30.0 s)"], ack=None, canon=None)
mira("N16l [S42] X06 + F3: indeterminado (antes fallo_entorno)", ver(e)[0], "indeterminado")

P7B = con({("PID", 7): "19600925"})
L05_INV = fila("Warning", 'FHIR rechazo el recurso (MSH-10=MSG1): FHIR devolvio 400: {"resourceType":"OperationOutcome","issue":[{"severity":"error","code":"invalid","diagnostics":"Invalid date"}]}')
L05_INV422 = dict(L05_INV, texto=L05_INV["texto"].replace("devolvio 400", "devolvio 422"))
AR102, AR207 = H + "MSA|AR|MSG1\nERR|||102|E", H + "MSA|AR|MSG1\nERR|||207|E"
MAL7, BIEN7 = dict(CAN, BirthDate="1960-25-09"), dict(CAN, BirthDate="1960-09-25")


def s43h(r, cuenta=None):
    return [h for h in r["hallazgos"] if (h.get("evidencia") or {}).get("alcance_s43") and (cuenta is None or h["cuenta"] == cuenta)]


def nota43(r):
    return [h for h in r["hallazgos"] if h["clase"] == "nota" and h["subtipo"] == "S43"]


e62 = ev(P7B, log=[L05_INV], ack=AR102, canon=MAL7)
r = vv("V62 [S43] M03b sintético: acuse_incorrecto/codigo+transformado", e62, 2, "acuse_incorrecto", "codigo+transformado")
h = (s43h(r) or [{}])[0]
mira("V62: fidelidad/transformado PID-7, causa transformacion, mapeador, literal, alcance_s43 y HTTP 400",
     (h.get("clase"), h.get("subtipo"), h.get("hecho"), h.get("causa"), h.get("origen"), h.get("certeza"),
      h.get("evidencia", {}).get("alcance_s43"), h.get("evidencia", {}).get("http")),
     ("fidelidad", "transformado", "PID-7", "transformacion", ["mapeador"], "literal", True, 400))
mira("V62: el veredicto va por los dos hallazgos, literal", (len(r["veredicto"]["por"]), r["veredicto"]["certeza"]), (2, "literal"))
r = vv("V62c [S43] canónico bien con 400 y AR 102: acuse_incorrecto/codigo", ev(P7B, log=[L05_INV], ack=AR102, canon=BIEN7),
       1, "acuse_incorrecto", "codigo")
mira("V62c: nota S43 que no cuenta y ningún hallazgo de fidelidad",
     ([h["cuenta"] for h in nota43(r)], [h for h in r["hallazgos"] if h["clase"] == "fidelidad"]), ([False], []))
r = vv("V62d [S43] AR 207 y canónico mal: correcto (atribuye, no detecta)", ev(P7B, log=[L05_INV], ack=AR207, canon=MAL7), 0, "correcto")
mira("V62d: fidelidad/transformado que no cuenta, con «no cuenta»",
     [(h["subtipo"], any("no cuenta" in q for q in h["que"])) for h in s43h(r, False)], [("transformado", True)])
vv("V62e [S43] 422: igual que V62", ev(P7B, log=[L05_INV422], ack=AR102, canon=MAL7), 2, "acuse_incorrecto", "codigo+transformado")
r = vv("V62f AA con 400 (ya cubierto): fallo_silencioso/aceptacion_falsa+guardado", ev(P7B, log=[L05_INV], ack=AA, canon=MAL7),
       2, "fallo_silencioso", "aceptacion_falsa+guardado")
mira("V62f: ningún hallazgo de la ruta S43", s43h(r), [])
r = vv("V62g [S43] carácter de control + fecha mal, AE 207: la transformación se anota",
       ev(con({("PID", 5): "Pe\x01rez^Ana", ("PID", 7): "19600925"}), log=[L05_400], ack=H + "MSA|AE|MSG1\nERR|||207|E",
          canon=dict(MAL7, GivenName="Ana")), 2, "acuse_incorrecto", "codigo+transformado")
mira("V62g: sin valor_imposible_aceptado (la trampa) y el hallazgo S43 en PID-7",
     ([h for h in r["hallazgos"] if h["clase"] == "valor_imposible_aceptado"], [h["hecho"] for h in s43h(r)]), ([], ["PID-7"]))
L05_401 = fila("Warning", 'FHIR rechazo el recurso (MSH-10=MSG1): FHIR devolvio 401: {"resourceType":"OperationOutcome"}')
r = vv("V62h 401 fuera de alcance: correcto, sin ruta S43", ev(P7B, log=[L05_401], ack=AR207, canon=MAL7), 0, "correcto")
mira("V62h: ni hallazgo ni nota S43", (s43h(r), nota43(r)), ([], []))
r = vv("V62i [S43] F1 con 400: la ruta corre por el código", ev(P7B, log=[fila("Warning", "algo con HTTP 400")], ack=AR102, canon=MAL7),
       2, "acuse_incorrecto")
mira("V62i: fidelidad/transformado presente", [h["subtipo"] for h in s43h(r)], ["transformado"])
r = vv("V62j [S43] ACK ausente por tiempo: fallo_entorno/ausente+transformado",
       ev(P7B, log=[L05_INV], ack=None, canon=MAL7, conexion=[X01, "no llegó ACK (el emisor dejó de esperar a los 30.0 s)"]),
       2, "fallo_entorno", "ausente+transformado")
fl = V.ficha("F13", V.verificar(e62), e62).split("\n")
mira("F13 ficha M03b: veredicto con +transformado y causa=transformacion",
     (any(l.startswith("VEREDICTO PROPUESTO: acuse_incorrecto/codigo+transformado") for l in fl),
      any("causa=transformacion" in l for l in fl)), (True, True))
e62c = ev(P7B, log=[L05_INV], ack=AR102, canon=BIEN7)
fl = V.ficha("F13c", V.verificar(e62c), e62c).split("\n")
mira("F13c ficha con la nota S43 en menores", any(l.startswith("menores, tolerancias y notas:") and "nota [S43]" in l for l in fl), True)

# ============================================================ controles C0/DEL por el cable (diseno-control-c0-fable.md §3)
import adjudicacion as AJ


def cable_de(segs):
    return AJ.cable(b"\x0b" + ("\r".join(segs) + "\r").encode("latin-1") + b"\x1c\r")


t90 = AJ.cable(bytes(range(0, 0x20)) + b"\x7f")
mira("N90 contrato con el arnés: C0 y DEL marcados <0xNN> salvo CR, VT y FS",
     all(("<0x%02X>" % b) in t90 for b in list(range(0, 0x20)) + [0x7F] if b not in (0x0B, 0x0D, 0x1C)), True)
P5C = con({("PID", 5): "Pe\x01rez^Ana"})
AR207 = H + "MSA|AR|MSG1\nERR|||207|E"
e = ev(mensaje=cable_de(P5C), log=[L05_400], ack=AR207, canon=None)
mira("N91 (= N06b por el cable) <0x01> en PID-5: AE 102; D1 y D2", (esp(e), ids(e)), (("si", "AE", "102"), ["D1", "D2"]))
vv("N91 veredicto", e, 1, "acuse_incorrecto", "codigo")
e = ev(mensaje=cable_de(P5C), canon=dict(CAN, FamilyName="Perez", GivenName="Ana"))
r91 = V.verificar(e)
mira("N91b ACK AA y canónico: fallo_silencioso, sin evidencia.descodificado",
     (r91["veredicto"]["categoria"], any((h.get("evidencia") or {}).get("descodificado") for h in r91["hallazgos"])),
     ("fallo_silencioso", False))
e = ev(mensaje=cable_de(P5C), log=[], ack=H + "MSA|AE|MSG1\nERR|||102|E", canon=None)
vv("N91c ACK AE 102: correcto", e, 0, "correcto")
for byte in ("\x7f", "\x09", "\x00"):
    e = ev(mensaje=cable_de(con({("PID", 5): "Pe" + byte + "rez^Ana"})), log=[], canon=None)
    mira("N92 byte %02X en PID-5: AE 102 y nota S10" % ord(byte),
         (esp(e), any(n.startswith("[S10] PID-5: byte %02X" % ord(byte)) for n in AR.calcular(e)[0]["notas"])),
         (("si", "AE", "102"), True))
e = ev(mensaje=cable_de(con({("PV1", 3): "A\x01B"})))
x = AR.calcular(e)[0]
mira("N93 <0x01> en PV1-3: correcto; notas S6 y S10 (S17)",
     (ver(e)[0], any("[S6]: 102 PV1-3" in n for n in x["notas"]), any(n.startswith("[S10] PV1-3: byte 01") for n in x["notas"])),
     ("correcto", True, True))
e = ev(mensaje=cable_de(con({("PID", 5): "Pe\nrez^Ana"})), canon=dict(CAN, FamilyName="Perez", GivenName="Ana"))
mira("N94 LF dentro de PID-5 (Jev: control): AE 102 esperado, fallo_silencioso con AA",
     (esp(e), ver(e)[0]), (("si", "AE", "102"), "fallo_silencioso"))
e = ev(mensaje=cable_de(con({("PID", 5): "Mu\x01\xf1oz^Ana"})), log=[], canon=None)
x = AR.calcular(e)[0]
mira("N96 run mixto 01+F1: AE 102 y tolerancia S9 del F1", (esp(e), any(t.startswith("[S9] PID-5") for t in x["tolerancias"])),
     (("si", "AE", "102"), True))
M10 = con({("MSH", 10): "M\x011"})
e = ev(mensaje=cable_de(M10), log=[], canon=None, ack=AJ.cable(("MSH|^~\\&|LABFHIR|LAB|LAB_SYS|CLINICA_B|X||ACK^A01^ACK|X1|P|2.5\r"
                                                               "MSA|AE|M\x011\rERR|||102|E\r").encode("latin-1")))
vv("N97 MSH-10 con control y ACK por el cable: correcto, sin D4", e, 0, "correcto")
B13 = [B[0] + "|||||\x01"] + list(B[1:])
x = AR.calcular(ev(mensaje=cable_de(B13), log=[], canon=None))[0]
mira("N99 control en el último campo del MSH (MSH-17): nota S6", any("[S6]: 102 MSH-17" in n for n in x["notas"]), True)
antes_pf = (dict(AR.PERFILES), AR.PERFIL)
try:
    AR.PERFILES["prueba_escape"] = {"escape_control_legal": True}
    AR.PERFIL = "prueba_escape"
    mira("N98 perfil con escape_control_legal: <0x01> y LF siguen siendo 102; \\X01\\ legal",
         (esp(ev(mensaje=cable_de(P5C), log=[], canon=None)), esp(ev(mensaje=cable_de(con({("PID", 5): "Pe\nrez^Ana"})), log=[], canon=None)),
          esp(ev(con({("PID", 5): "Pe\\X01\\rez^Ana"}), log=[], canon=None))),
         (("si", "AE", "102"), ("si", "AE", "102"), ("si", "AA", None)))
finally:
    AR.PERFILES.clear()
    AR.PERFILES.update(antes_pf[0])
    AR.PERFIL = antes_pf[1]

e = ev(mensaje="hola", log=[], canon=None)
mira("AP-1 cable sin MSH: sin_intercambio, sin excepción", ver(e)[0], "sin_intercambio")
mira("AP-1 bundle vacío: sin_intercambio", V.verificar({"mensaje": ""})["veredicto"]["categoria"], "sin_intercambio")

print("AUTOPRUEBA DEL VERIFICADOR: " + ("TODO BIEN" if not mal else "FALLAN %d" % len(mal)))
sys.exit(1 if mal else 0)
