#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O0b (diseno-oru-fable.md §6): el verificador en seco sobre las bases ORU sintéticas (bases_oru.py), punto de entrada oru_fhir.
  (a) las 20 primeras bases por acuse_esperado: válidas -> AA; sin OBR -> AE 100 OBR; OBX-11 vacío en el 3.º OBX -> AE 101 OBX(3)-11
      (DV-ORU-1); OBX-5 «1,5» con NM -> AE 102 OBX-5 (DV-ORU-2); OBX-11 «Q» -> AE 103 OBX-11; 2.6 -> AA + S22.
  (b) el mapeador sobre las 40 bases sin excepción: esperado sin imposibles ni avisos de estructura; control negativo (el esperado contra
      sí mismo, también por el MCP y por verificar_caso con L15 -> correcto); el PE `oru` sigue AA sobre las mismas bases.
  Ningún canónico esperado se escribe a fichero (O1 lo calcula un oráculo a ciegas).
Regla: ningún MAL. Uso: python prueba_oru.py"""
import contextlib
import copy
import io
import json
import re
import sys

import acuse_referencia as AR
import bases_oru as BO
import lectura_evidencia as LE
import mapeador_oru as MO
import mapeador_referencia as MR
import puntos_entrada as PE
import verificador as V

mal = []
n_ok = [0]


def mira(nombre, obtenido, esperado):
    ok = obtenido == esperado
    if ok:
        n_ok[0] += 1
    else:
        print("  MAL " + nombre + ": %r != %r" % (obtenido, esperado))
        mal.append(nombre)


def ack(b, msa1="AA", err=None):
    a = "MSH|^~\\&|LABORU|LAB|LABSYS|HOSPSYN|20230104090000||ACK^R01^ACK|A-%s|P|2.5\rMSA|%s|ORU-%s" % (b["id"], msa1, b["id"])
    return a + ("\rERR|||%s|E" % err if err else "")


def ev(texto, pe="oru_fhir", ack_=None, log=None, canon=None):
    e = {"mensaje": texto, "ack": ack_, "conexion": ["conexión establecida"] + (["ACK recibido a los 0.02 s del envío"] if ack_ else []),
         "sesiones": [dict({"log": log or []}, **({"canonico_oru": canon} if canon is not None else {}))], "entorno": [], "punto_entrada": pe}
    return e


def res(texto, pe="oru_fhir"):
    x = AR.calcular(ev(texto), pe=pe)[0]
    return (x.get("msa1"), x["err"][0]["err3"] if x["err"] else None, x["err"][0]["donde"] if x["err"] else None)


def quitar(b, nombre):
    return [s for s in b["segmentos"] if s.split("|")[0] != nombre]


def campo(seg, n, v):
    return AR._campo_set(seg, n, v)


def cable(segs):
    return "\r".join(segs) + "\r"


# ---------------------------------------------------------------------------- (a) acuse sobre las 20 primeras
mira("PE oru_fhir: puerto 2585, mapeador oru, todas_las_ocurrencias OBR/OBX, zona +01:00 [S57][S66]",
     (PE.PUNTOS["oru_fhir"]["puerto"], PE.PUNTOS["oru_fhir"]["mapeador"], sorted(PE.PUNTOS["oru_fhir"]["todas_las_ocurrencias"]), PE.PUNTOS["oru_fhir"]["zona_emisor"]),
     (2585, "oru", ["OBR", "OBX"], "+01:00"))
mira("los demás PE no llevan las claves nuevas", [k for p in PE.PUNTOS.values() if p["nombre"] not in ("oru_fhir", "adt_fhir") for k in ("mapeador", "todas_las_ocurrencias", "zona_emisor") if k in p], [])
B = {b["id"]: b for b in BO.BASES}
mira("40 bases, ids B01-B40", [b["id"] for b in BO.BASES], ["B%02d" % i for i in range(1, 41)])
for b in BO.BASES[:20]:
    x = AR.calcular(ev(BO.cable(b)))[0]
    mira("%s válida -> AA en oru_fhir" % b["id"], (x["msa1"], [z for z in x["notas"] if "[S6]" in z and "102" in z]), ("AA", []))
b1 = B["B01"]
mira("B01 sin OBR -> AE 100 OBR (P3.3)", res(cable(quitar(b1, "OBR"))), ("AE", "100", "OBR"))
segs = list(b1["segmentos"])
segs[-1] = campo(segs[-1], 11, "")
mira("B01 OBX-11 vacío en el 3.º OBX -> AE 101 OBX(3)-11 (DV-ORU-1)", res(cable(segs)), ("AE", "101", "OBX(3)-11"))
mira("B01 OBX-11 vacío en el 3.º OBX -> en el PE oru (DV-MT5) sigue AA", res(cable(segs), "oru")[0], "AA")
segs = list(b1["segmentos"])
segs[3] = campo(segs[3], 5, "1,5")
mira("B01 OBX-5 «1,5» con NM -> AE 102 OBX(1)-5 (DV-ORU-2; con varios OBX la etiqueta lleva el índice)", res(cable(segs)), ("AE", "102", "OBX(1)-5"))
mira("B01 OBX-5 «1,5» con NM -> en el PE oru sigue AA (L-MT7)", res(cable(segs), "oru")[0], "AA")
segs = list(b1["segmentos"])
segs[4] = campo(segs[4], 5, "1,5")
mira("B01 OBX-5 «1,5» en el 2.º OBX -> AE 102 OBX(2)-5", res(cable(segs)), ("AE", "102", "OBX(2)-5"))
segs = list(b1["segmentos"])
segs[3] = campo(segs[3], 11, "Q")
mira("B01 OBX-11 «Q» -> AE 103 OBX(1)-11", res(cable(segs)), ("AE", "103", "OBX(1)-11"))
segs = list(B["B06"]["segmentos"])
segs[3] = campo(segs[3], 11, "Q")
mira("B06 (un solo OBX) OBX-11 «Q» -> AE 103 OBX-11 (sin índice)", res(cable(segs)), ("AE", "103", "OBX-11"))
x = AR.calcular(ev(BO.cable(B["B15"])))[0]
mira("B15 2.6 CWE -> AA + tolerancia S22", (x["msa1"], [t[:22] for t in x["tolerancias"]]), ("AA", ["[S22] OBX-2 'CWE' no e"]))
segs = list(B["B06"]["segmentos"])
segs[3] = campo(segs[3], 5, ">^1,5")
mira("B06 SN con num1 no NM -> AE 102 OBX-5", res(cable(segs)), ("AE", "102", "OBX-5"))
segs = list(B["B12"]["segmentos"])
segs[3] = campo(segs[3], 5, "20230230")
mira("B12 TS 30-feb -> AE 102 OBX-5", res(cable(segs)), ("AE", "102", "OBX-5"))
segs = list(b1["segmentos"])
segs[3] = campo(segs[3], 14, "20231301080000")
mira("B01 OBX-14 mes 13 -> AE 102 OBX(1)-14", res(cable(segs)), ("AE", "102", "OBX(1)-14"))
segs = list(b1["segmentos"])
segs[2] = campo(segs[2], 25, "Q")
mira("B01 OBR-25 «Q» -> AE 103 OBR-25 (tabla 0123, DV-ORU-5)", res(cable(segs)), ("AE", "103", "OBR-25"))
segs = list(b1["segmentos"])
segs[4] = campo(segs[4], 3, "")
mira("B01 OBX-3 vacío en el 2.º OBX -> AE 101 OBX(2)-3", res(cable(segs)), ("AE", "101", "OBX(2)-3"))
segs = list(b1["segmentos"])
segs[5] = campo(segs[5], 5, "9\x015")
mira("B01 control C0 en OBX-5 del 3.º OBX [S10] -> AE 102 OBX(3)-5", res(cable(segs)), ("AE", "102", "OBX(3)-5"))
x = AR.calcular(ev(cable(list(b1["segmentos"][:3]) + [campo(b1["segmentos"][3], 8, "ZZ")])))[0]
mira("OBX-8 fuera de la 0078 (user-defined, estricto) -> AA + nota S6", (x["msa1"], any("103 OBX-8" in n for n in x["notas"])), ("AA", True))
ADT = ["MSH|^~\\&|APP|FAC|LABORU|LAB|20230101171416||ADT^A01^ADT_A01|MSG1|P|2.5", "EVN|A01|20230101171416", "PID|1||ID1^^^HOSP^MR||Apellido^Nombre||19600910|M", "PV1|1|I|CLINIC_1"]
mira("ADT al 2585 -> AR 200 (E2)", res(cable(ADT))[:2], ("AR", "200"))
mira("ORU^R30 al 2585 -> AR 201 (lista cerrada)", res(cable([BO.msh(1, ev="R30", est="ORU_R30")] + b1["segmentos"][1:]))[:2], ("AR", "201"))
mira("MSH-12 2.3.1 -> AR 203 [S19]", res(cable([BO.msh(1, ver="2.3.1")] + b1["segmentos"][1:]))[:2], ("AR", "203"))

# ---------------------------------------------------------------------------- (b) mapeador sobre las 40 bases
with contextlib.redirect_stdout(io.StringIO()):
    import mcp_verificador as M
L15 = {"tipo": "Info", "texto": "Resultados escritos en FHIR (MSH-10=%s): creados=%d existentes=0 (HTTP 200)"}
for b in BO.BASES:
    texto = BO.cable(b)
    m = MR.mensajes(texto)
    mira("%s se lee como un mensaje con %d segmentos" % (b["id"], len(b["segmentos"])), (len(m), len(m[0].segs)), (1, len(b["segmentos"])))
    try:
        esp, imp, est, tol = MO.esperado_mensaje(m[0], "oru_fhir")
    except Exception as ex:                                             # sin excepción, sea cual sea la base
        mira("%s mapeador sin excepción" % b["id"], repr(ex), None)
        continue
    mira("%s esperado sin imposibles ni avisos de estructura" % b["id"], (imp, est), ([], []))
    mira("%s recuentos coherentes (NumInformes/NumObservaciones = listas)" % b["id"],
         (esp["cabecera"]["NumInformes"], esp["cabecera"]["NumObservaciones"]), (len(esp["informes"]), len(esp["observaciones"])))
    mira("%s identificadores D-ORU-1 por posición" % b["id"], [o["Identificador"] for o in esp["observaciones"]],
         ["ORU-%s#%d.%d" % (b["id"], o["Informe"], o["OrdenEnInforme"]) for o in esp["observaciones"]])
    mira("%s ValorTipo decidido en toda observación" % b["id"], all(o["ValorTipo"] in ("quantity", "string", "codeableconcept", "datetime", "time", "range", "ratio", "sin_valor", "no_soportado") for o in esp["observaciones"]), True)
    mira("%s control negativo: el esperado contra sí mismo no delata nada" % b["id"], MO.comparar(copy.deepcopy(esp), esp)[0], [])
    r = MO.revisar(texto, [esp], ack(b), "oru_fhir")
    mira("%s revisar (AA + canónico igual): sin discrepancias" % b["id"], r[0], [])
    n = len(esp["informes"]) + len(esp["observaciones"])
    e = ev(texto, ack_=ack(b), log=[dict(L15, texto=L15["texto"] % ("ORU-" + b["id"], n))], canon=copy.deepcopy(esp))
    v = V.verificar(e)
    mira("%s verificar con AA + L15 + canónico igual -> correcto" % b["id"], (v["veredicto"]["categoria"], [h["id"] for h in v["hallazgos"] if h["cuenta"]]), ("correcto", []))
    out, _ = M.t_verificar({"mensaje": texto, "ack": ack(b), "sesiones": e["sesiones"], "punto_entrada": "oru_fhir", "incluir_ficha": True})
    mira("%s MCP verificar_caso -> correcto, base completa salvo conexión, ficha con PUNTO y CANÓNICO" % b["id"],
         (out["veredicto"]["categoria"], out["entrada"]["canonicos"], "PUNTO    oru_fhir (puerto 2585)" in out["ficha"], "CANÓNICO MsgControlId=ORU-%s" % b["id"] in out["ficha"]),
         ("correcto", 1, True, True))
    out, _ = M.t_canonico({"mensaje": texto, "canonico": copy.deepcopy(esp), "ack": ack(b), "punto_entrada": "oru_fhir"})
    mira("%s MCP comparar_canonico: aceptado, sin discrepancias, recuentos iguales" % b["id"],
         (out["alcance"], out["mensajes"][0]["discrepancias"], out["mensajes"][0]["recuentos"]["observaciones"]["esperado"] == len(esp["observaciones"])), ("aceptado", [], True))
    mira("%s el PE oru (2581) sigue aceptando la base" % b["id"], res(texto, "oru")[0], "AA")
    # mutante MO4-like sobre el canónico: un OBX descartado -> fidelidad/recuento
    if esp["observaciones"]:
        c2 = copy.deepcopy(esp)
        c2["observaciones"].pop()
        v2 = V.verificar(ev(texto, ack_=ack(b), log=[dict(L15, texto=L15["texto"] % ("ORU-" + b["id"], n - 1))], canon=c2))
        mira("%s canónico con un OBX menos -> fallo_silencioso/guardado por fidelidad/recuento hecho OBX" % b["id"],
             (v2["veredicto"]["categoria"], v2["veredicto"]["subtipo"], sorted({(h["clase"], h["subtipo"], h["hecho"]) for h in v2["hallazgos"] if h["cuenta"]})),
             ("fallo_silencioso", "guardado", [("fidelidad", "recuento", "OBX")]))

# rasgos concretos que las bases deben ejercitar (sin escribir el canónico a fichero)
def esp_de(i):
    return MO.esperado_mensaje(MR.mensajes(BO.cable(B[i]))[0], "oru_fhir")

e3 = esp_de("B03")[0]
mira("B03: 2 informes, 6 observaciones, pertenencia 3+3", (len(e3["informes"]), [o["Informe"] for o in e3["observaciones"]], [i["NumObx"] for i in e3["informes"]]), (2, [1, 1, 1, 2, 2, 2], [3, 3]))
e4 = esp_de("B04")[0]
mira("B04: 3 informes; OBX-1 reiniciado no confunde la posición", ([o["Orden"] for o in e4["observaciones"]], [o["OrdenEnInforme"] for o in e4["observaciones"]]), ([1, 2, 3, 4], [1, 1, 2, 1]))
mira("B06/B07/B08/B09 SN -> quantity/range/ratio/ratio/quantity/string", [o["ValorTipo"] for i in ("B06", "B07", "B08", "B09") for o in esp_de(i)[0]["observaciones"]],
     ["quantity", "range", "ratio", "ratio", "quantity", "string"])
mira("B10 TX párrafos", esp_de("B10")[0]["observaciones"][0]["ValorTexto"], "Crecimiento escaso a las 24 h.\nSe recomienda repetir la toma.")
mira("B14 CE ^texto: display sin code + nota AMB-ORU-4", (esp_de("B14")[0]["observaciones"][0]["ValorCodigo"], esp_de("B14")[0]["observaciones"][0]["ValorDisplay"], any("AMB-ORU-4" in t for t in esp_de("B14")[3])),
     ("", "Insuficiencia cardiaca congestiva", True))
mira("B15 CWE 2.6: codeableconcept con texto original", (esp_de("B15")[0]["observaciones"][0]["ValorTipo"], esp_de("B15")[0]["observaciones"][0]["ValorTextoOriginal"]), ("codeableconcept", "E. coli"))
mira("B16-B22 OBX-11 P/C/X/W/D/R/I -> status", [esp_de("B%02d" % i)[0]["observaciones"][0]["Estado"] for i in range(16, 23)],
     ["preliminary", "corrected", "cancelled", "entered-in-error", "entered-in-error", "preliminary", "registered"])
mira("B18 OBX-11 X con OBX-2 vacío: sin_valor y sin nota AMB-ORU-2", (esp_de("B18")[0]["observaciones"][0]["ValorTipo"], [t for t in esp_de("B18")[3] if "AMB-ORU-2" in t]), ("sin_valor", []))
mira("B23 NumNte = 3 (todos los NTE, adjudicación O1), nota L-ORU-4", (esp_de("B23")[0]["cabecera"]["NumNte"], any("[L-ORU-4]" in t for t in esp_de("B23")[3])), (3, True))
mira("B24 NumObxEspecimen = 1, NumObservaciones = 1", (esp_de("B24")[0]["cabecera"]["NumObxEspecimen"], esp_de("B24")[0]["cabecera"]["NumObservaciones"]), (1, 1))
mira("B25 escapes resueltos en OBX-3.2 y OBX-5", (esp_de("B25")[0]["observaciones"][0]["CodigoDisplay"], esp_de("B25")[0]["observaciones"][0]["ValorTexto"]),
     ("Comentario ^ cultivo", "Escaso & lento | ver nota ^ 2"))
mira("B26 UTF-8 conservado", esp_de("B26")[0]["observaciones"][0]["CodigoDisplay"], "Glucosa en ayunas – mañana")
mira("B27/B28/B29 forma canónica del número (D-ORU-2)", [o["ValorNumero"] for i in ("B27", "B28", "B29") for o in esp_de(i)[0]["observaciones"]], ["1.20", "-0.5", "0.5", "5"])
mira("B30 sin PID: PacienteId vacío + nota S60", (esp_de("B30")[0]["cabecera"]["PacienteId"], any("[S60]" in t for t in esp_de("B30")[3])), ("", True))
mira("B31 sin OBX: 1 informe, 0 observaciones", (esp_de("B31")[0]["cabecera"]["NumInformes"], esp_de("B31")[0]["cabecera"]["NumObservaciones"]), (1, 0))
mira("B32 OBX-14 vacío -> OBR-7 (S63)", [(o["Fecha"], o["FechaOrigen"]) for o in esp_de("B32")[0]["observaciones"]], [("2023-01-04T07:30:00+01:00", "OBR-7")] * 2)
mira("B33 sin fecha: ninguna + nota L-MT6", (esp_de("B33")[0]["observaciones"][0]["FechaOrigen"], any("[L-MT6]" in t for t in esp_de("B33")[3])), ("ninguna", True))
mira("B34 OBR-25 vacío -> unknown (S64)", esp_de("B34")[0]["informes"][0]["Estado"], "unknown")
mira("B35 OBR-22 sin segundos -> Emitido vacío (D-ORU-5); OBR-8 -> EfectivoFin", (esp_de("B35")[0]["informes"][0]["Emitido"], esp_de("B35")[0]["informes"][0]["EfectivoFin"]), ("", "2023-01-04T07:45:00+01:00"))
mira("B36 repetición perdida", esp_de("B36")[0]["observaciones"][0]["RepeticionesPerdidas"], 1)
mira("B38 PID-3 sin MR: la primera no vacía", esp_de("B38")[0]["cabecera"]["PacienteId"], "SYN0003")
mira("B39 zona explícita y fracción; S4 en OBX-11 f y OBX-8 h", (esp_de("B39")[0]["observaciones"][0]["Fecha"], esp_de("B39")[0]["informes"][0]["Emitido"], esp_de("B39")[0]["observaciones"][0]["Estado"],
     esp_de("B39")[0]["observaciones"][0]["Interpretacion"], sorted(t[:4] for t in esp_de("B39")[3])), ("2023-01-04T08:00:00.5+02:00", "2023-01-04T09:15:00.25+02:00", "final", "H", ["[S4]", "[S4]"]))
mira("B40 XPN no_soportado con crudo; OBR-4 alt y sistema L", (esp_de("B40")[0]["observaciones"][0]["ValorTipo"], esp_de("B40")[0]["observaciones"][0]["ValorCrudo"],
     esp_de("B40")[0]["informes"][0]["CodigoAltCode"], esp_de("B40")[0]["informes"][0]["CodigoAltSistema"]), ("no_soportado", "Observador^Sintetico", "PMB", "urn:lab:integraciones:cs:L"))
# L15 y L03 en la lectura
lec = LE.leer({"sesiones": [{"log": [dict(L15, texto=L15["texto"] % ("ORU-B01", 0))]}]}, ["ORU-B01"], "oru_fhir")
mira("L15 con creados=0 -> exito + nota L5'", (lec["filas"][0]["id"], lec["por_mensaje"][0]["destino"], [n_[:3] for n_ in lec["por_mensaje"][0]["notas"]]), ("L15", "exito", ["L5'"]))
L03 = {"tipo": "Warning", "texto": "Mensaje rechazado antes de FHIR (MSH-10=ORU-B01): OBX 3: OBX-11 (Observation Result Status) vacio"}
mira("L03 del circuito ORU -> hecho OBX-11 solo en oru_fhir (DV-ORU-3)", (LE.clasificar_fila(L03, "oru_fhir")["datos"]["hecho"], LE.clasificar_fila(L03)["datos"]["hecho"], LE.clasificar_fila(L03, "adt_a01")["datos"]["hecho"]),
     ("OBX-11", "otro", "otro"))
mira("L15 no casa con los textos de hoy", [LE.clasificar_fila({"tipo": "Info", "texto": t})["id"] for t in (
     "Patient creado en FHIR: id=1 desde MSH-10=MSG1 (HTTP 201)", "Mensaje aceptado sin destino (MSH-10=MSG1): punto oru")], ["L01", "L13"])
# O4 ronda 1: un L03 con el motivo en varias líneas (IRIS une los errores de Validate con CRLF) es L03, no vocabulario nuevo
import lectura_evidencia as _LE
_fila = {"tipo": "Warning", "texto": "Mensaje rechazado antes de FHIR (MSH-10=X-1): Estructura no conforme con el esquema (DocType 2.5:ORU_R01, validacion dm): ERROR <EnsEDI>ErrMapRequired: falta OBR\r\nERROR <EnsEDI>ErrMapSegUnrecog: OBX"}
mira("L03 con motivo de varias líneas -> L03", (_LE.clasificar_fila(_fila, "oru_fhir")["id"], _LE.clasificar_fila(_fila, "oru_fhir")["msh10"]), ("L03", "X-1"))
mira("control negativo: una fila desconocida sigue siendo desconocida (F3)", _LE.clasificar_fila({"tipo": "Info", "texto": "Algo nuevo\r\notra línea"}, "oru_fhir")["id"], "F3")
# O4 ronda 2 (B24): un control C0 en un OBX bajo SPM (no consumido, L-ORU-5) no es 102; en un OBX consumido, sí [S10]
import acuse_referencia as _AR
def _acuse(texto):
    x = _AR.calcular({"mensaje": texto, "sesiones": [], "ack": None, "conexion": ["conexión establecida"], "entorno": []}, pe="oru_fhir")[0]
    return (x.get("msa1_aplicacion"), [z["err3"] for z in x.get("err") or []][:1])
_b24 = open("bases_oru/B24.hl7", "rb").read().decode("latin-1").split("\r")
_spm = [k for k, z in enumerate(_b24) if z.startswith("OBX|") and any(y.startswith("SPM|") for y in _b24[:k])][0]
_obs = [k for k, z in enumerate(_b24) if z.startswith("OBX|")][0]
def _con_c0(lineas, k):
    t = list(lineas)
    f = t[k].split("|")
    f[5] = f[5][:1] + "\x01" + f[5][1:]
    t[k] = "|".join(f)
    import adjudicacion as _A
    return _A.cable(b"\x0b" + "\r".join(z for z in t if z).encode("latin-1") + b"\r\x1c\r")
mira("C0 en OBX bajo SPM (no consumido): AA [L-ORU-5][S17]", _acuse(_con_c0(_b24, _spm)), ("AA", []))
mira("control negativo: C0 en el OBX consumido -> AE 102 [S10]", _acuse(_con_c0(_b24, _obs)), ("AE", ["102"]))
# O6: info_verificador publica las deudas CIR-ORU y la DV-ORU-1 acotada
import mcp_verificador as _MCP
_info, _ = _MCP.t_info({})
mira("info: CIR-ORU-1..4 (CIR-ORU-4 = decimal, v1.1) y DV-ORU-1 acotada a los OBX consumidos [O6]",
     (sorted(k for k in _info["deudas_circuito_mt"] if k.startswith("CIR-ORU")), "CONSUMIDO" in _info["desviaciones_oru"]["DV-ORU-1"]),
     (["CIR-ORU-1", "CIR-ORU-2", "CIR-ORU-3", "CIR-ORU-4", "CIR-ORU-5", "CIR-ORU-6"], True))
# ---------------------------------------------------------------------------- P0 v1.1 (diseno-oru-v11-fable.md §5 P0 b): el almacén en el veredicto
import almacen_oru as AO


def ev_alm(b, alm, canon=None, msa1="AA", err=None, log=None, esp=None):
    texto = BO.cable(b)
    esp = esp or MO.esperado_mensaje(MR.mensajes(texto)[0], "oru_fhir")[0]
    n = len(esp["informes"]) + len(esp["observaciones"])
    s = {"log": log if log is not None else [dict(L15, texto=L15["texto"] % ("ORU-" + b["id"], n))], "canonico_oru": canon if canon is not None else copy.deepcopy(esp)}
    if alm is not None:
        s["almacen_oru"] = alm
    return {"mensaje": texto, "ack": ack(b, msa1, err), "conexion": ["conexión establecida", "ACK recibido a los 0.02 s del envío"],
            "sesiones": [s], "entorno": [], "punto_entrada": "oru_fhir"}


def firmas(v):
    return sorted({(h["clase"], h["subtipo"], h["hecho"], h["causa"], "+".join(h["origen"])) for h in v["hallazgos"] if h["cuenta"]})


def cat(v):
    return (v["veredicto"]["categoria"], v["veredicto"]["subtipo"])


_dec = {}
for b in BO.BASES:                                                    # (b) las 40 bases: proyección exacta -> correcto; v1 idéntico
    esp = MO.esperado_mensaje(MR.mensajes(BO.cable(b))[0], "oru_fhir")[0]
    alm = AO.almacen_sintetico(esp)
    v_alm = V.verificar(ev_alm(b, alm, esp=esp))
    mira("%s almacén = proyección del esperado (decimales exactos) -> correcto, resumen n=1" % b["id"],
         (cat(v_alm), firmas(v_alm), v_alm["almacen"][0]["Observation"], v_alm["almacen"][0]["DiagnosticReport"], v_alm["almacen"][0]["fallos"]),
         (("correcto", None), [], [1] * len(esp["observaciones"]), [1] * len(esp["informes"]), 0))
    v_v1 = V.verificar(ev_alm(b, None, esp=esp))
    mira("%s sin almacen_oru: JSON de verificar sin clave almacen y correcto (S70)" % b["id"], ("almacen" in v_v1, cat(v_v1)), (False, ("correcto", None)))
    for o, ent in zip(esp["observaciones"], alm["observaciones"]):    # 1.2 frente a «1.20»: todo ValorNumero con ceros finales
        for vn in (o.get("ValorNumero"), o.get("ValorNum2")):
            if isinstance(vn, str) and re.search(r"\.\d*0$", vn):
                _dec.setdefault(b["id"], []).append((o["Orden"], vn))
mira("bases con decimales con cero final (los que CIR-ORU-4 pierde, previsión P2): B18 «1.0» y B27 «1.20»; B28/B29 no", sorted(_dec), ["B18", "B27"])
b27 = B["B27"]
esp27 = MO.esperado_mensaje(MR.mensajes(BO.cable(b27))[0], "oru_fhir")[0]
alm27 = AO.almacen_sintetico(esp27)
mira("B27: el crudo sintético lleva \"value\":1.20 como número (no «1.2»)", '"value":1.20' in alm27["observaciones"][0]["recursos"][0]["crudo"], True)
alm_dec = copy.deepcopy(alm27)
alm_dec["observaciones"][0]["recursos"][0]["crudo"] = alm_dec["observaciones"][0]["recursos"][0]["crudo"].replace('"value":1.20', '"value":1.2')
v = V.verificar(ev_alm(b27, alm_dec, esp=esp27))
mira("B27 decimal 1.2 por «1.20» -> fallo_silencioso/guardado, UN hallazgo fidelidad/almacen OBX-5 causa escritura [S67] (CIR-ORU-4)",
     (cat(v), firmas(v), [h["que"] for h in v["hallazgos"] if h["cuenta"]]),
     (("fallo_silencioso", "guardado"), [("fidelidad", "almacen", "OBX-5", "escritura", "almacen")], [["ALM OBX 1 (2160-0) valueQuantity.value: esperado '1.20', observado '1.2'"]]))
mira("B27 control negativo: 1.20 como número -> correcto", cat(V.verificar(ev_alm(b27, alm27, esp=esp27))), ("correcto", None))
# status solo en el almacén (MA2) y también en el canónico (MO2: fusión)
b16 = B["B16"]                                                        # OBX-11 P -> preliminary
esp16 = MO.esperado_mensaje(MR.mensajes(BO.cable(b16))[0], "oru_fhir")[0]
mira("B16 esperado preliminary", esp16["observaciones"][0]["Estado"], "preliminary")
alm16 = AO.almacen_sintetico(esp16)
alm_st = copy.deepcopy(alm16)
alm_st["observaciones"][0]["recursos"][0]["crudo"] = alm_st["observaciones"][0]["recursos"][0]["crudo"].replace('"status":"preliminary"', '"status":"final"')
v = V.verificar(ev_alm(b16, alm_st, esp=esp16))
mira("B16 status final solo en el almacén -> fidelidad/almacen OBX-11 causa escritura", (cat(v), firmas(v)), (("fallo_silencioso", "guardado"), [("fidelidad", "almacen", "OBX-11", "escritura", "almacen")]))
c16 = copy.deepcopy(esp16)
c16["observaciones"][0]["Estado"] = "final"
v = V.verificar(ev_alm(b16, alm_st, canon=c16, esp=esp16))
mira("B16 status final en el canónico Y en el almacén -> UN hallazgo fusionado OBX-11 causa transformacion, dos orígenes",
     (cat(v), firmas(v), len([h for h in v["hallazgos"] if h["cuenta"]])), (("fallo_silencioso", "guardado"), [("fidelidad", "guardado", "OBX-11", "transformacion", "almacen+mapeador")], 1))
mira("B16 control: status preliminary en ambos -> correcto", cat(V.verificar(ev_alm(b16, alm16, esp=esp16))), ("correcto", None))
# unidad (MA1 / MO1)
b1 = B["B01"]
esp1 = MO.esperado_mensaje(MR.mensajes(BO.cable(b1))[0], "oru_fhir")[0]
alm1 = AO.almacen_sintetico(esp1)
rec = json.loads(alm1["observaciones"][0]["recursos"][0]["crudo"], parse_float=str)
for k_ in ("unit", "code", "system"):
    rec["valueQuantity"].pop(k_)
alm_u = copy.deepcopy(alm1)
alm_u["observaciones"][0]["recursos"][0]["crudo"] = json.dumps(rec)
v = V.verificar(ev_alm(b1, alm_u, esp=esp1))
mira("B01 unidad quitada solo del recurso (MA1) -> fidelidad/almacen OBX-6 causa escritura; 3 hojas", (cat(v), firmas(v), len([h for h in v["hallazgos"] if h["cuenta"]][0]["que"])),
     (("fallo_silencioso", "guardado"), [("fidelidad", "almacen", "OBX-6", "escritura", "almacen")], 3))
c1 = copy.deepcopy(esp1)
c1["observaciones"][0].update(UnidadCode="", UnidadTexto="", UnidadSistema="")
v = V.verificar(ev_alm(b1, alm_u, canon=c1, esp=esp1))
mira("B01 unidad quitada del canónico Y del recurso (MO1) -> UN hallazgo fidelidad/guardado OBX-6 causa transformacion (fusión)",
     (cat(v), firmas(v), len([h for h in v["hallazgos"] if h["cuenta"]])), (("fallo_silencioso", "guardado"), [("fidelidad", "guardado", "OBX-6", "transformacion", "almacen+mapeador")], 1))
mira("B01 control: proyección exacta -> correcto", cat(V.verificar(ev_alm(b1, alm1, esp=esp1))), ("correcto", None))
# ausente (MA3), duplicado (MO8), extra (S69), orden de coding (S72)
alm_a = copy.deepcopy(alm1)
alm_a["observaciones"][2] = {"identificador": alm_a["observaciones"][2]["identificador"], "n": 0, "recursos": []}
v = V.verificar(ev_alm(b1, alm_a, esp=esp1))
mira("B01 tercera Observation no escrita (MA3) -> fidelidad/ausente OBX + result del DR sin ella, fusionados por hecho OBX",
     (cat(v), firmas(v), sorted(q[:12] for h in v["hallazgos"] if h["cuenta"] for q in h["que"])),
     (("fallo_silencioso", "guardado"), [("fidelidad", "ausente", "OBX", "escritura", "almacen")], ["ALM OBR 1 (2", "ALM OBX 3 (2"]))
v = V.verificar(ev_alm(b1, AO.almacen_sintetico(esp1, n=2), esp=esp1))
mira("B01 dos recursos por identifier (MO8, sin ifNoneExist) -> fallo_silencioso/guardado por fidelidad/duplicado OBX y OBR (cierra CIR-ORU-3)",
     (cat(v), firmas(v)), (("fallo_silencioso", "guardado"), [("fidelidad", "duplicado", "OBR", "escritura", "almacen"), ("fidelidad", "duplicado", "OBX", "escritura", "almacen")]))
rec = json.loads(alm1["observaciones"][0]["recursos"][0]["crudo"], parse_float=str)
rec["performer"] = [{"display": "Laboratorio"}]
alm_x = copy.deepcopy(alm1)
alm_x["observaciones"][0]["recursos"][0]["crudo"] = json.dumps(rec)
v = V.verificar(ev_alm(b1, alm_x, esp=esp1))
mira("B01 performer en el recurso -> correcto con nota almacen_extra que no cuenta [S69] (L-ORU-10)",
     (cat(v), [(h["subtipo"], h["cuenta"]) for h in v["hallazgos"] if "almacen" in h["origen"]]), (("correcto", None), [("almacen_extra", False)]))
b40 = B["B40"]                                                        # OBR-4 con código alternativo: dos codings
esp40 = MO.esperado_mensaje(MR.mensajes(BO.cable(b40))[0], "oru_fhir")[0]
alm40 = AO.almacen_sintetico(esp40)
rec = json.loads(alm40["informes"][0]["recursos"][0]["crudo"], parse_float=str)
mira("B40 el DR proyectado lleva dos codings", len(rec["code"]["coding"]), 2)
rec["code"]["coding"].reverse()
alm_o = copy.deepcopy(alm40)
alm_o["informes"][0]["recursos"][0]["crudo"] = json.dumps(rec, ensure_ascii=False)
v = V.verificar(ev_alm(b40, alm_o, esp=esp40))
mira("B40 codings del DR en otro orden -> correcto con nota AMB-ORU-7 [S72]", (cat(v), [(h["subtipo"], h["cuenta"]) for h in v["hallazgos"] if "almacen" in h["origen"]]), (("correcto", None), [("AMB-ORU-7", False)]))
rec["code"]["coding"][0]["code"] = "XX"
alm_o["informes"][0]["recursos"][0]["crudo"] = json.dumps(rec, ensure_ascii=False)
v = V.verificar(ev_alm(b40, alm_o, esp=esp40))
mira("B40 control: coding con otro código -> fidelidad/almacen OBR-4", (cat(v), firmas(v)), (("fallo_silencioso", "guardado"), [("fidelidad", "almacen", "OBR-4", "escritura", "almacen")]))
# rechazo AE legítimo (OBX-11 vacío -> AE 101): n = 0 -> correcto con nota; con escritura -> acuse/rechazo_con_escritura
segs = list(b1["segmentos"])
segs[-1] = campo(segs[-1], 11, "")
b_ae = dict(b1, segmentos=segs)
texto_ae = cable(segs)
esp_ae = MO.esperado_mensaje(MR.mensajes(texto_ae)[0], "oru_fhir")[0]
L03ae = [{"tipo": "Warning", "texto": "Mensaje rechazado antes de FHIR (MSH-10=ORU-B01): OBX 3: OBX-11 (Observation Result Status) vacio"}]
e_ae = ev_alm(b_ae, AO.almacen_sintetico(esp_ae, n=0, ack_msa1="AE"), msa1="AE", err="101", log=L03ae, esp=esp_ae)
e_ae["mensaje"] = texto_ae
v = V.verificar(e_ae)
mira("B01 OBX-11 vacío: AE 101 + almacén n=0 -> correcto, nota almacen_vacio_tras_rechazo [S68]",
     (cat(v), [(h["subtipo"], h["cuenta"]) for h in v["hallazgos"] if "almacen" in h["origen"]], "almacen" in v), (("correcto", None), [("almacen_vacio_tras_rechazo", False)], True))
e_ae1 = ev_alm(b_ae, AO.almacen_sintetico(esp_ae, n=1, ack_msa1="AE"), msa1="AE", err="101", log=L03ae, esp=esp_ae)
e_ae1["mensaje"] = texto_ae
v = V.verificar(e_ae1)
mira("B01 OBX-11 vacío: AE 101 pero n=1 escrito -> acuse_incorrecto/rechazo_con_escritura (hecho destino); nada de datos (DV-ORU11-4)",
     (cat(v), firmas(v)), (("acuse_incorrecto", "rechazo_con_escritura"), [("acuse", "rechazo_con_escritura", "destino", None, "almacen")]))
alm_ae2 = AO.almacen_sintetico(esp_ae, n=1, ack_msa1="AE")
alm_ae2["observaciones"][0]["recursos"][0]["crudo"] = alm_ae2["observaciones"][0]["recursos"][0]["crudo"].replace('"value":95', '"value":95.0')
e_ae2 = ev_alm(b_ae, alm_ae2, msa1="AE", err="101", log=L03ae, esp=esp_ae)
e_ae2["mensaje"] = texto_ae
v = V.verificar(e_ae2)
mira("B01 AE 101 con n=1 y además 95.0 por «95» -> ambos (datos + acuse)", (cat(v), sorted({h["clase"] for h in v["hallazgos"] if h["cuenta"]})), (("ambos", "guardado+rechazo_con_escritura"), ["acuse", "fidelidad"]))
# lectura fallida -> indeterminado/lectura; identifier sin entrada -> nota (DV-ORU11-2); AR 207 con 422 y n=0 -> nota S43/L22
alm_f = copy.deepcopy(alm1)
alm_f["fallos"] = [{"identificador": "ORU-B01#1.2", "paso": "get", "http": 500, "detalle": "Internal Server Error"}]
v = V.verificar(ev_alm(b1, alm_f, esp=esp1))
mira("B01 fallos en la lectura del almacén -> indeterminado/lectura, hallazgo lectura con el identifier",
     (cat(v), [h["que"][0] for h in v["hallazgos"] if h["clase"] == "lectura"]), (("indeterminado", "lectura"), ["lectura del almacén fallida para ORU-B01#1.2: get HTTP 500 (Internal Server Error)"]))
mira("B01 control: sin fallos -> correcto", cat(V.verificar(ev_alm(b1, alm1, esp=esp1))), ("correcto", None))
c_menos = copy.deepcopy(esp1)
c_menos["observaciones"].pop()
alm_menos = AO.almacen_sintetico(c_menos)                            # el arnés lee por el canónico observado: sin entrada para #1.3
e_m = ev_alm(b1, alm_menos, canon=c_menos, esp=esp1)
e_m["sesiones"][0]["log"][0]["texto"] = L15["texto"] % ("ORU-B01", 3)
v = V.verificar(e_m)
mira("B01 OBX descartado (MO4) con almacén coherente -> fidelidad/recuento (mapeador) + result del DR sin él (almacén) fusionados por OBX; nota almacen_no_leido",
     (cat(v), firmas(v), [(h["subtipo"], h["cuenta"]) for h in v["hallazgos"] if h["subtipo"] == "almacen_no_leido"]),
     (("fallo_silencioso", "guardado"), [("fidelidad", "recuento", "OBX", "transformacion", "almacen+mapeador")], [("almacen_no_leido", False)]))
L05 = [{"tipo": "Error", "texto": "FHIR respondió HTTP 422 (MSH-10=ORU-B01): code=invalid"}]
e_ar = ev_alm(b1, AO.almacen_sintetico(esp1, n=0, ack_msa1="AR"), msa1="AR", err="207", log=L05, esp=esp1)
v = V.verificar(e_ar)
_lec = LE.leer(e_ar, ["ORU-B01"], "oru_fhir")["por_mensaje"][0]
mira("B01 AR 207 con 422 y almacén n=0 -> nota almacen_vacio_tras_rechazo con [S43][L22] (atomicidad observada); veredicto como v1",
     ((_lec["destino"], _lec["http"]), [("[S43][L22]" in h["que"][0]) for h in v["hallazgos"] if h["subtipo"] == "almacen_vacio_tras_rechazo"], cat(v)),
     (("http", 422), [True], ("correcto", None)))
e_v1_ar = ev_alm(b1, None, msa1="AR", err="207", log=L05, esp=esp1)
mira("B01 AR 207 con 422 sin almacén (v1): mismo veredicto", cat(V.verificar(e_v1_ar)), cat(v))
# ficha y MCP
v = V.verificar(ev_alm(b27, alm_dec, esp=esp27))
f = V.ficha("B27", v, ev_alm(b27, alm_dec, esp=esp27))
mira("ficha con almacén: línea ALMACÉN leído y el hallazgo ALM", ("ALMACÉN  leído tras ACK: Observation n=[1] DiagnosticReport n=[1]; fallos 0" in f, "ALM OBX 1 (2160-0) valueQuantity.value" in f), (True, True))
f1 = V.ficha("B27", V.verificar(ev_alm(b27, None, esp=esp27)), ev_alm(b27, None, esp=esp27))
mira("ficha sin almacén (v1): línea «ALMACÉN  no leído (L-ORU-1)» [S70]", "ALMACÉN  no leído (L-ORU-1)" in f1, True)
out, _ = M.t_verificar(dict(ev_alm(b27, alm_dec, esp=esp27), incluir_ficha=True))
h0 = out["hallazgos"][0]
mira("MCP verificar_caso con almacén: hallazgo con esperado/observado y citas [F decimal] [M-4oct-2] [M-4oct-3] [CIR-ORU-4] [S67]; entrada.almacenes = 1; sin línea L-ORU-1 en no_evaluado",
     (out["veredicto"]["categoria"], h0["esperado"], h0["observado"], {"[F decimal]", "[M-4oct-2]", "[M-4oct-3]", "[CIR-ORU-4]", "[S67]"} <= {c["etiqueta"] for c in h0["citas"]},
      out["entrada"]["almacenes"], any("L-ORU-1" in n_ for n_ in out["entrada"]["no_evaluado"])),
     ("fallo_silencioso", {"almacen": {"campo": "ALM OBX 1 (2160-0) valueQuantity.value", "esperado": "1.20"}}, {"almacen": {"campo": "ALM OBX 1 (2160-0) valueQuantity.value", "observado": "1.2"}}, True, 1, False))
out, _ = M.t_verificar(ev_alm(b27, None, esp=esp27))
mira("MCP verificar_caso sin almacén (v1): base completa, almacenes 0, no_evaluado con la línea L-ORU-1 [S70]",
     (out["veredicto"]["categoria"], out["entrada"]["base_de_evidencia"], out["entrada"]["almacenes"], any("sin almacen_oru no se evalúa" in n_ for n_ in out["entrada"]["no_evaluado"])), ("correcto", "completa", 0, True))
out, _ = M.t_verificar({"mensaje": BO.cable(B["B02"]), "ack": ack(B["B02"]), "sesiones": [{"log": [dict(L15, texto=L15["texto"] % ("ORU-B02", 4))], "canonico": {"Identifier": "x"}}], "punto_entrada": "adt"})
mira("MCP con PE adt: la entrada no lleva la clave almacenes", "almacenes" in out["entrada"], False)
out, _ = M.t_canonico({"mensaje": BO.cable(b27), "canonico": copy.deepcopy(esp27), "ack": ack(b27), "punto_entrada": "oru_fhir", "almacen_oru": alm_dec})
mira("MCP comparar_canonico con almacen_oru: bloque almacen con la discrepancia OBX-5 y recuentos",
     (out["mensajes"][0]["almacen"]["recuentos"], [(d["hecho"], d["esperado"], d["observado"], d["causa"]) for d in out["mensajes"][0]["almacen"]["discrepancias"]]),
     ({"Observation": [1], "DiagnosticReport": [1], "fallos": 0}, [("OBX-5", "1.20", "1.2", "escritura")]))
out, _ = M.t_canonico({"mensaje": BO.cable(b27), "canonico": copy.deepcopy(esp27), "ack": ack(b27), "punto_entrada": "oru_fhir"})
mira("MCP comparar_canonico sin almacen_oru: sin bloque almacen", "almacen" in out["mensajes"][0], False)
out, _ = M.t_tabla({"tabla": "proyeccion_fhir_oru", "valor": "valueQuantity.value"})
mira("MCP consultar_tabla proyeccion_fhir_oru: 30 filas; valueQuantity.value -> OBX-5 con [F decimal]",
     (len(out["entradas"]), out["consulta"]["presente_literal"], [x for x in out["entradas"] if x["codigo"] == "valueQuantity.value"][0]["hecho"],
      "[F decimal]" in [c["etiqueta"] for c in [x for x in out["entradas"] if x["codigo"] == "valueQuantity.value"][0]["citas"]]), (30, True, "OBX-5", True))
_info, _ = M.t_info({})
mira("info: S67-S72, D-ORU11-1..3, DV-ORU11-1..5, L-ORU-10..13, AMB-ORU-7 cerrada por S72, CIR-ORU-3 cerrada y CIR-ORU-4",
     (all("S%d" % n in _info["decisiones_sitio"] for n in range(67, 73)), sorted(_info["declarados_oru11"]), sorted(k for k in _info["desviaciones_oru"] if "11" in k),
      all("L-ORU-%d" % n in _info["limites"] for n in range(10, 14)), _info["ambiguedades_cerradas"].get("AMB-ORU-7"),
      _info["deudas_circuito_mt"]["CIR-ORU-3"].startswith("Cerrada en v1.1"), "CIR-ORU-4" in _info["deudas_circuito_mt"], "almacen_oru" in _info["limites"]["L-ORU-1"]),
     (True, ["D-ORU11-1", "D-ORU11-2", "D-ORU11-3"], ["DV-ORU11-%d" % n for n in range(1, 6)], True, "S72", True, True, True))
mira("el esquema de sesiones[] admite almacen_oru", M.validar({"mensaje": "MSH|^~\\&|a|b|c|d|e||ORU^R01|1|P|2.5", "sesiones": [{"log": [], "almacen_oru": alm27}]}, M.HERRAMIENTAS[0]["inputSchema"]), None)
try:
    M.validar({"mensaje": "x", "sesiones": [{"almacen_oru": {"observaciones": [{"identificador": "a", "n": 1, "recursos": [{"crudo": {"a": 1}}]}]}}]}, M.HERRAMIENTAS[0]["inputSchema"])
    mira("crudo objeto -> tipo_invalido", "sin error", "tipo_invalido")
except M.ErrorEntrada as ex:
    mira("crudo objeto -> tipo_invalido", (ex.codigo, ex.campo), ("tipo_invalido", "sesiones[0].almacen_oru.observaciones[0].recursos[0].crudo"))
# v1.1 P4: info publica L-ORU-14 (punto ciego MA3) y CIR-ORU-4 como arreglada
_info2, _ = _MCP.t_info({})
mira("info: L-ORU-14 y CIR-ORU-4 arreglada [v1.1 P4]", ("L-ORU-14" in _info2["limites"], _info2["deudas_circuito_mt"]["CIR-ORU-4"].startswith("ARREGLADA")), (True, True))
# Arreglos A1-A5 (ANTES-ARREGLOS-ORU.md; revisión por pares, propuestas/revision-codigo/sondas_a.py). Cada uno delata en b21fca0.
def _oru_a(seps="^~\\&", obr7="20260101100000", extra=""):
    c = seps[0]
    return "\r".join(["MSH|" + seps + "|LAB|HOSP|HIS|HOSP|20260101120000||ORU" + c + "R01" + c + "ORU_R01|M1|P|2.5",
                      "PID|1||12345" + c * 3 + "HOSP" + c + "MR||Doe" + c + "John",
                      "OBR|1|P1|F1|GLU" + c + "Glucosa" + c + "LN|||" + obr7 + "|||||||||||||||20260101110000|||F",
                      "OBX|1|NM|GLU" + c + "Glucosa" + c + "LN||1.20|mg/dL|||||F"] + ([extra] if extra else []))
_ca = MO.esperado(_oru_a(), "oru_fhir")[0][0]
_oa = copy.deepcopy(_ca)
for _o in _oa["observaciones"]:
    _o["Orden"], _o["Informe"], _o["OrdenEnInforme"], _o["ValorNumero"] = 0, 0, 0, "9.99"
for _i in _oa["informes"]:
    _i["Orden"] = 0
_da = MO.comparar(_oa, _ca)[0]
mira("A1 claves que no casan con el recuento igual: discrepancia por OBR y por OBX", sorted(z.split(" Orden:")[0] for z in _da), ["OBR 1 (GLU)", "OBX 1 (GLU)"])
_ob = copy.deepcopy(_ca)
_ob["observaciones"].pop()
mira("A1 control: con recuento distinto solo el recuento (identidad v1 «-menos1»)", MO.comparar(_ob, _ca)[0], ["Observaciones: esperado 1, observado 0"])
mira("A2 DTM y TM con fracción sin segundos: rechazados", [MO.fecha_hora("202601011230.5")[1] is not None, MO.hora("1230.5")[1] is not None,
     _AR._ts("202601011230.5"), MO.fecha_hora("20260101123000.5")[1]], [True, True, False, None])
mira("A3 zona: minutos 60 y 14:01 rechazados; 13:59 y 14:00 aceptados (FHIR R4 dateTime)",
     [MO.fecha_hora("20260101120000" + z)[1] is None for z in ("+0160", "-1401", "+1359", "-1400")] + [_AR._ts("20260101120000+0160")],
     [False, False, True, True, False])
mira("A4 separador de componentes de MSH-2 ($): OBR-7 con precisión sin imposible y AA",
     ([z for z in MO.esperado(_oru_a("$~\\&", "20260101100000$S"), "oru_fhir")[0][1] if "OBR-7" in z],
      _AR.calcular({"mensaje": _oru_a("$~\\&", "20260101100000$S"), "punto_entrada": "oru_fhir"}, pe="oru_fhir")[0]["msa1"]), ([], "AA"))
mira("A4 control: el mismo OBR-7 inválido con «$» sigue siendo 102",
     [e["err3"] for e in _AR.calcular({"mensaje": _oru_a("$~\\&", "202601011000.5$S"), "punto_entrada": "oru_fhir"}, pe="oru_fhir")[0]["err"]], ["102"])
_seg2 = "\r".join(["PID|2||999^^^HOSP^MR", "OBR|1|||||||20260101100000||||||||||||||||||F", "OBX|1|NM|X^X^LN||1||||||F"])
mira("A5 un segundo PATIENT_RESULT con OBR-4 vacío no cambia el acuse (AMB-ORU-5)",
     _AR.calcular({"mensaje": _oru_a(extra=_seg2), "punto_entrada": "oru_fhir"}, pe="oru_fhir")[0]["msa1"], "AA")
mira("A5 control: el mismo OBR-4 vacío en el primer PATIENT_RESULT sí es 101",
     [(e["err3"], e["donde"]) for e in _AR.calcular({"mensaje": _oru_a().replace("OBR|1|P1|F1|GLU^Glucosa^LN|", "OBR|1|P1|F1||"),
                                                     "punto_entrada": "oru_fhir"}, pe="oru_fhir")[0]["err"]], [("101", "OBR-4")])
# AMB-ORU-8 (SN «.» y rango de un número): la letra del ConceptMap, publicada con su alternativa y la deuda CIR-ORU-5
_info8, _ = _MCP.t_info({})
_e8 = [MO.esperado(_oru_a().replace("|NM|", "|SN|").replace("||1.20|", "||" + v + "|"), "oru_fhir")[0][0]["observaciones"][0] for v in ("^1^.^5", "<^^-^5")]
mira("AMB-ORU-8: «.» -> quantity value Num1; «<^^-^5» -> range high 5; publicada con CIR-ORU-5/6",
     ([(o["ValorTipo"], o["ValorNumero"], o.get("ValorNum2")) for o in _e8], "AMB-ORU-8" in json.dumps(_info8, ensure_ascii=False),
      "valueString" in json.dumps(_info8, ensure_ascii=False).split("AMB-ORU-8")[1][:1500]),
     ([("quantity", "1", "5"), ("range", "", "5")], True, True))
# A6 (cierre de ORU): OBX-5 solo con separadores = vacío en el mapeador, como en el acuse (§2.1.5); delata en 426ff1f
_t6 = _oru_a().replace("|NM|", "|SN|").replace("||1.20|", "||^|")
_e6 = MO.esperado(_t6, "oru_fhir")[0]
mira("A6 OBX-5 «^» con SN: sin_valor y sin imposible; acuse AA (coherentes)",
     (_e6[0]["observaciones"][0]["ValorTipo"], _e6[1], _AR.calcular({"mensaje": _t6, "punto_entrada": "oru_fhir"}, pe="oru_fhir")[0]["msa1"]),
     ("sin_valor", [], "AA"))
# A7 (cierre de ORU): proyección de SN de un solo número; un value[x] vacío no se proyecta (FHIR JSON no admite objetos vacíos)
_ob7 = {"ValorTipo": "range", "ValorNumero": "", "ValorNum2": "5", "UnidadTexto": "mg/dL", "UnidadCode": "", "UnidadSistema": ""}
_p7 = AO.proyectar_observation(_ob7, {})
_p7b = AO.proyectar_observation(dict(_ob7, ValorTipo="quantity", ValorNumero="", ValorNum2="", UnidadTexto="", ValorComparador=""), {})
mira("A7 range de un número: solo high; quantity sin nada: sin valueQuantity",
     (_p7.get("valueRange"), "valueQuantity" in _p7b), ({"high": {"value": "5", "unit": "mg/dL"}}, False))
# Cierre de ORU: CIR-ORU-5/6 arregladas y L23 (bordes de TS en los PE ADT, sin medir) publicados
_info9, _ = _MCP.t_info({})
mira("cierre de ORU: CIR-ORU-5/6 ARREGLADAS y L23 publicado", (_info9["deudas_circuito_mt"]["CIR-ORU-5"].startswith("ARREGLADA"),
     _info9["deudas_circuito_mt"]["CIR-ORU-6"].startswith("ARREGLADA"), "L23" in _info9["limites"]), (True, True, True))
# N1-N7 (triaje de la revisión nocturna, ANTES-ARREGLOS-NOCTURNA.md); las de N1-N3, N5 y N7 delatan en 2f4a64b
def _adt_n(msh7="20230101120000", pid7="19800101", seps="^~\\&"):
    c = seps[0]
    return "\r".join(["MSH|%s|APP|FAC|R|RF|%s||ADT%sA01%sADT_A01|M1|P|2.5" % (seps, msh7, c, c), "EVN|A01|" + msh7,
                      "PID|1||X1%s%s%sH%sMR||Perez%sAna||%s|F" % (c, c, c, c, c, pid7), "PV1|1|I"])
mira("N1 MR.fecha con la gramática única: hora 99, zona +0160 y fracción sin segundos imposibles; los textos de antes no cambian",
     [MR.fecha("1980010199")[1] is not None, MR.fecha("19800101120000+0160")[1] is not None, MR.fecha("198001011230.5")[1] is not None,
      MR.fecha("19801301")[1], MR.fecha("1980x")[1], MR.fecha("19800101+0500")[0]],
     [True, True, True, "PID-7 '19801301': mes imposible", "PID-7 '1980x' no es un TS de v2.5", "1980-01-01"])
_e_n1 = MR.esperado(MR.mensajes(_adt_n(pid7="19800101$L", seps="$~\\&"))[0])
mira("N1 PID-7 con MSH-2 «$» y segunda componente: BirthDate sin imposible (camino real)",
     (_e_n1[0]["BirthDate"], [z for z in _e_n1[1] if "PID-7" in z]), ("1980-01-01", []))
_err = lambda t: [(e["err3"], e["donde"]) for e in _AR.calcular({"mensaje": t, "punto_entrada": "adt_a01"}, pe="adt_a01")[0]["err"]]
mira("N2 S18 con la precisión común: MSH-7 al mes y PID-7 del mismo mes no es posterior; del mes siguiente sí",
     (_err(_adt_n(msh7="202301", pid7="20230102")), ("102", "PID-7") in _err(_adt_n(msh7="202301", pid7="20230201"))), ([], True))
mira("N2b S18 con MSH-7 con zona: se contrasta (antes, «no contrastable»)",
     (("102", "PID-7") in _err(_adt_n(msh7="20230101120000+0100", pid7="20230102")), _err(_adt_n(msh7="20230101120000+0100", pid7="20221231"))),
     (True, []))
_rc = AO.comparar_recurso({"resourceType": "Observation", "status": "final", "value[x]": None},
                          {"resourceType": "Observation", "status": "final", "valueQuantity": {"value": "5"}}, "Observation")
mira("N3 value[x] «no se juzga»: ninguna línea value*", [l for l in _rc[0] if str(l[0]).startswith("value")], [])
mira("N5 code y system, los dos o ninguno", (AO._cantidad("5", "", {"UnidadTexto": "mg", "UnidadCode": "mg", "UnidadSistema": ""}),
     AO._cantidad("5", "", {"UnidadTexto": "mg", "UnidadCode": "mg", "UnidadSistema": "http://unitsofmeasure.org"})),
     ({"value": "5", "unit": "mg"}, {"value": "5", "unit": "mg", "code": "mg", "system": "http://unitsofmeasure.org"}))
_ack7 = "MSH|^~\\&|L|L|APP|FAC|t||ACK^A01^ACK|A1|P|2.5\rMSA|AA|M1\rERR|||207"
_c7 = _AR.comparar({"mensaje": _adt_n(), "ack": _ack7, "punto_entrada": "adt_a01"}, pe="adt_a01")
mira("N7 AA con ERR 207 sin ERR-4: nota D3 «ERR-4 ausente», que no cuenta",
     [(z["id"], z["cuenta"]) for z in _c7 if "ERR-4 ausente" in z["que"]], [("D3", False)])
# N8-N11 (triaje de la cola 2, D2; delatan en 41b9341)
mira("N8 S18 con la hora: nacido a las 13:00 del día del mensaje de las 12:00 es posterior; con zonas distintas, solo la fecha",
     [MR.posterior_a("20260101130000", "20260101120000"), MR.posterior_a("20260101130000+0100", "20260101120000"),
      ("102", "PID-7") in _err(_adt_n(msh7="20260101120000", pid7="20260101130000"))], [True, False, True])
mira("N9 _causa con una tupla de valores tolerados: pertenencia", AO._causa("status", {"status": ("final", "amended")}, {"status": "final"}, "registered"), "escritura")
_rc11 = AO.comparar_recurso({"resourceType": "Observation", "status": "final", "valueQuantity": {"value": "1"}},
                            {"resourceType": "Observation", "status": "final", "valueQuantity": {"value": "1"}, "valueString": "x"}, "Observation")[0]
mira("N11 dos claves value* observadas: el hallazgo las nombra todas", [l[3] for l in _rc11 if l[0] == "value[x]"], ["valueQuantity+valueString"])
_r10 = {"resumen": {"Observation": [], "DiagnosticReport": [], "fallos": 0}, "lineas": [], "fallos": [], "escrito": False, "indice": {}}
AO._comparar_entrada("Observation", "OBX 1", "X#1.1", {}, None, {"n": 1, "recursos": [{"id": "1", "crudo": "{x", "obj": None, "error": "JSON ilegible"}]}, "AA", _r10, None)
mira("N10 resumen.fallos sigue a los fallos de lectura", (len(_r10["fallos"]), _r10["resumen"]["fallos"]), (1, 1))
# Lote B (ANTES-LOTE-A-B.md; delatan en 2b4a843)
_oru_err = lambda t: [(e["err3"], e["donde"]) for e in _AR.calcular({"mensaje": t, "punto_entrada": "oru_fhir"}, pe="oru_fhir")[0]["err"]]
mira("B1 AMB-ORU-9: una repetición vacía no se juzga en ningún tipo",
     ([MO.valor_valido(t, "") for t in ("NM", "SN", "TS", "DT", "TM")], _oru_err(_oru_a().replace("||1.20|", "||1.20~|")),
      _oru_err(_oru_a().replace("||1.20|", "||1.20~abc|"))),
     ([None] * 5, [], [("102", "OBX-5")]))
_t_b3 = _oru_a("$~\\&").replace("OBR|1|P1|F1|GLU$Glucosa$LN|", "OBR|1|P1|F1|$$|")
mira("B3 vacío con los delimitadores del mensaje: con MSH-2 «$~\\&» un OBR-4 «$$» está vacío (101); «#» con los estándar no lo está",
     (("101", "OBR-4") in _oru_err(_t_b3), _AR._vacio_en("#", _AR.SEPS_ESTANDAR), _AR._vacio_en("$$", "|$~\\&"), _AR._vacio_en('""', _AR.SEPS_ESTANDAR)),
     (True, False, True, False))
_AR.NIVEL = "estricto"                                                # PID-1 es «estricto» [S6]
try:
    _b4 = (("102", "PID-1") in _err(_adt_n().replace("PID|1|", "PID|1.|")), ("102", "PID-1") in _err(_adt_n().replace("PID|1|", "PID|1x|")))
finally:
    _AR.NIVEL = "consumido"
mira("B4 nm() con la regla NM única (nivel estricto): PID-1 «1.» (AMB-ORU-3) no es 102; «1x» sí", _b4, (False, True))
# Lote C, N13 (ANTES-LOTE-C.md; delata en 95c5704)
_c_base = _oru_a().split("\r")
_c_orc_tras = "\r".join(_c_base[:3] + ["ORC|RE|P1|F1"] + _c_base[3:])
_c_sin_obr = "\r".join(_c_base[:2] + ["ORC|RE|P1|F1"] + _c_base[3:])
_c_dos = "\r".join(_c_base + ["ORC|RE|P2|F2", "OBR|2|P2|F2|GLU^Glucosa^LN|||20260101100000|||||||||||||||20260101110000|||F", _c_base[3].replace("OBX|1|", "OBX|2|")])
mira("N13 ORC detrás del OBR: fuera de posición, ignorado [S45] (AA); sin ningún OBR sigue 100 OBR; un segundo pedido completo, AA",
     (_oru_err(_c_orc_tras), ("100", "OBR") in _oru_err(_c_sin_obr), _oru_err(_c_dos)), ([], True, []))
print("AUTOPRUEBA ORU (O0b): " + ("TODO BIEN (%d comprobaciones)" % n_ok[0] if not mal else "FALLAN %d" % len(mal)))
sys.exit(1 if mal else 0)
