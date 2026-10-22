#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa ADT, A1b (diseno-adt-fable.md §5.4-§5.5 con S80): lo releído del almacén FHIR tras el ACK (sesiones[].almacen_adt)
frente a la proyección del canónico ESPERADO (mapeador_adt.proyectar), hoja a hoja y texto exacto, como la v1.1 de ORU.

  almacen_adt = {"leido": "tras_ack", "ack_msa1": "AA",
                 "pacientes": [{"identificador": <Identifier>, "n": 1, "recursos": [{"id": "12", "crudo": "<GET /Patient/12 tal cual>"}]}],
                 "visitas":   [{"identificador": <VisitaId>,   "n": 1, "recursos": [{"id": "34", "crudo": "<GET /Encounter/34>"}]}],
                 "fallos":    [{"identificador", "paso": "busqueda" | "get", "http", "detalle"}]}

Hallazgos (los de almacen_oru): fidelidad/almacen (elemento distinto; hecho por elemento), fidelidad/duplicado (n > 1),
fidelidad/ausente (n = 0 con AA), acuse/rechazo_con_escritura (n > 0 con AE/AR), fidelidad/almacen con hecho PV1-2 cuando hay
un Encounter que el mensaje no pedía (PV1-2 = N, S77); notas almacen_extra, almacen_vacio_tras_rechazo, almacen_no_leido.
id y meta no se comparan (D-ORU11-1); el crudo se lee como texto (D-ORU11-2); el orden de name/address/telecom/location/
participant es dato (D-ADT-5). L-ADT-19: un Encounter sin PV1-19 (S78) no tiene identifier con que releerlo: no se juzga.

  python3 almacen_adt.py --autoprueba
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import almacen_oru as AO      # noqa: E402  (parsear, _hojas, _causa, _linea, _repr, AUSENTE: sin tocarlo)
import mapeador_adt as MA     # noqa: E402

AUSENTE = AO.AUSENTE
METADATOS = ("id", "meta")
CONTRATO = {"Patient": {"resourceType", "identifier", "name", "gender", "birthDate", "deceasedDateTime", "deceasedBoolean", "address",
                        "telecom", "maritalStatus"},
            "Encounter": {"resourceType", "identifier", "status", "class", "type", "serviceType", "subject", "participant", "period",
                          "location", "hospitalization"}}
HECHO = {"Patient": {"identifier": "PID-3", "name": "PID-5", "gender": "PID-8", "birthDate": "PID-7", "deceasedDateTime": "PID-29",
                     "deceasedBoolean": "PID-30", "address": "PID-11", "telecom": "PID-13", "maritalStatus": "PID-16"},
         "Encounter": {"identifier": "PV1-19", "status": "PV1-2", "class": "PV1-2", "type": "PV1-4", "serviceType": "PV1-10",
                       "subject": "PID-3", "participant": "PV1-7", "period.start": "PV1-44", "period.end": "PV1-45",
                       "location": "PV1-3", "hospitalization.admitSource": "PV1-14", "hospitalization.dischargeDisposition": "PV1-36"}}
CLAVE = {"Patient": "pacientes", "Encounter": "visitas"}
TABLA = [(t, ruta, h) for t, d in HECHO.items() for ruta, h in d.items()]          # consultar_tabla proyeccion_fhir_adt


def hecho_almacen(tipo, ruta, evento=None):
    """Hecho (SEG-n) de una hoja del almacén. El status de un A11 es MSH-9 (lo fija el evento, no PV1-2: diseño §5.5)."""
    r = re.sub(r"\[\d+\]", "", ruta)
    if tipo == "Encounter" and r == "status" and evento == "A11":
        return "MSH-9"
    for k in sorted(HECHO[tipo], key=len, reverse=True):
        if r == k or r.startswith(k + ".") or r.startswith(k + "["):
            return HECHO[tipo][k]
    return "PID" if tipo == "Patient" else "PV1"


def leer(almacen):
    """-> {"entradas": {(tipo, identificador): {identificador, n, recursos: [{id, crudo, obj, error}], tipo}}, "fallos", "orden"}."""
    out = {"entradas": {}, "fallos": [], "orden": []}
    if not isinstance(almacen, dict):
        return out
    for tipo, clave in CLAVE.items():
        for ent in almacen.get(clave) or []:
            if not isinstance(ent, dict) or not isinstance(ent.get("identificador"), str):
                out["fallos"].append("entrada de %s sin identificador en almacen_adt" % clave)
                continue
            recs = []
            for rc in ent.get("recursos") or []:
                rc = rc if isinstance(rc, dict) else {}
                obj, err = AO.parsear(rc.get("crudo"))
                rid = rc.get("id") if isinstance(rc.get("id"), str) else (obj or {}).get("id") if isinstance((obj or {}).get("id"), str) else None
                recs.append({"id": rid, "crudo": rc.get("crudo"), "obj": obj, "error": err})
            n = ent.get("n")
            if not isinstance(n, int) or isinstance(n, bool):
                n = len(recs)
            k = (tipo, ent["identificador"])
            out["entradas"][k] = {"identificador": ent["identificador"], "n": n, "recursos": recs, "tipo": tipo}
            out["orden"].append(k)
    if isinstance(almacen.get("visitas_por_paciente"), list):             # S-VE-3: los Encounter del paciente (relectura nueva)
        out["por_paciente"] = []
        for ent in almacen["visitas_por_paciente"]:
            if not isinstance(ent, dict) or not isinstance(ent.get("identificador"), str):
                out["fallos"].append("entrada de visitas_por_paciente sin identificador en almacen_adt")
                continue
            recs = []
            for rc in ent.get("recursos") or []:
                rc = rc if isinstance(rc, dict) else {}
                obj, err = AO.parsear(rc.get("crudo"))
                rid = rc.get("id") if isinstance(rc.get("id"), str) else (obj or {}).get("id") if isinstance((obj or {}).get("id"), str) else None
                recs.append({"id": rid, "crudo": rc.get("crudo"), "obj": obj, "error": err})
            out["por_paciente"].append({"identificador": ent["identificador"], "recursos": recs,
                                        "previos": [str(p) for p in ent.get("previos") or []]})
    for f in almacen.get("fallos") or []:
        if isinstance(f, dict):
            out["fallos"].append("lectura del almacén fallida para %s: %s HTTP %s (%s)" % (
                f.get("identificador"), f.get("paso") or "?", f.get("http") if f.get("http") is not None else "—", (f.get("detalle") or "")[:120]))
        else:
            out["fallos"].append("lectura del almacén fallida: %r" % (f,))
    return out


def normalizar(obj):
    return {k: v for k, v in obj.items() if k not in METADATOS}


def comparar_recurso(E, A, tipo, evento=None):
    """-> (lineas [(ruta, hecho, esperado, observado)], extras [elementos fuera del contrato]). Hoja None en E = «no juzgar»."""
    he = AO._hojas(E, nulos_como_texto=False)
    saltar = tuple(k for k, v in he.items() if v is None)
    he = {k: v for k, v in he.items() if v is not None}
    ha = AO._hojas(A)
    lineas, extras, vistos = [], [], set()
    for ruta in list(he) + [r for r in ha if r not in he]:
        if ruta in vistos or any(ruta == s or ruta.startswith(s + ".") or ruta.startswith(s + "[") for s in saltar):
            continue
        vistos.add(ruta)
        cab = re.sub(r"\[\d+\]", "", ruta).split(".")[0]
        if ruta not in he:
            if cab in CONTRATO[tipo]:
                lineas.append((ruta, hecho_almacen(tipo, ruta, evento), AUSENTE, ha[ruta]))
            elif cab not in extras:
                extras.append(cab)
        elif ruta not in ha:
            lineas.append((ruta, hecho_almacen(tipo, ruta, evento), he[ruta], AUSENTE))
        elif str(he[ruta]) != str(ha[ruta]):
            lineas.append((ruta, hecho_almacen(tipo, ruta, evento), he[ruta], ha[ruta]))
    return lineas, extras


def _hojas_proy(p):
    h = AO._hojas(p, nulos_como_texto=False) if p is not None else {}
    return {k: v for k, v in h.items() if v is not None}


def _entrada(tipo, ident, E, C, ent, msa1, res, evento):
    """Un identifier esperado frente a su entrada del almacén. -> True si hubo escritura (n > 0)."""
    n = ent["n"]
    res["resumen"][tipo].append(n)
    hrec = "PID" if tipo == "Patient" else "PV1"
    if n == 0:
        if msa1 == "AA":
            res["lineas"].append(AO._linea("fidelidad", "ausente", hrec, "ALM %s: ningún recurso con el identifier %s (el circuito acusó AA: esperado 1)" % (tipo, ident), causa="escritura"))
        return False
    if msa1 in ("AE", "AR"):
        res["lineas"].append(AO._linea("acuse", "rechazo_con_escritura", "destino", "ALM %s: %d recurso(s) con el identifier %s aunque MSA-1 = %s (esperado 0: nada debió escribirse, S59/S68)" % (tipo, n, ident, msa1)))
    if n > 1:
        res["lineas"].append(AO._linea("fidelidad", "duplicado", hrec, "ALM %s: %d recursos con el identifier %s (esperado 1)" % (tipo, n, ident), causa="escritura"))
    primero = ent["recursos"][0] if ent["recursos"] else None
    if primero is None:
        res["lineas"].append(AO._linea("nota", "almacen_sin_contenido", hrec, "ALM %s: n=%d pero sin recurso leído para %s (contenido no comparado)" % (tipo, n, ident), cuenta=False))
        return True
    for i, r in enumerate(ent["recursos"], 1):
        if r["obj"] is None:
            res["fallos"].append("lectura del almacén fallida para %s (recurso %d de %d): %s" % (ident, i, len(ent["recursos"]), r["error"]))
    if primero["obj"] is None:
        return True
    A = normalizar(primero["obj"])
    lineas, extras = comparar_recurso(E, A, tipo, evento)
    E_h = _hojas_proy(E)
    C_h = _hojas_proy(C) if C is not None else None
    for ruta, hecho, e, a in lineas:
        causa = AO._causa(ruta, E_h, C_h, a)
        sufijo = " (el almacén reproduce el canónico)" if causa == "transformacion" else ""
        res["lineas"].append(AO._linea("fidelidad", "almacen", hecho, "ALM %s %s: esperado %s, observado %s%s" % (tipo, ruta, AO._repr(e), AO._repr(a), sufijo), causa=causa))
    if extras:
        res["lineas"].append(AO._linea("nota", "almacen_extra", hrec, "ALM %s %s: elementos fuera del contrato v1: %s (no se juzgan, L-ADT-10)" % (tipo, ident, ", ".join(sorted(extras))), cuenta=False))
    return True


def comparar(almacen, esperado_canon, canonico_observado=None, msa1=None, rechazo_http=None):
    """Un mensaje. -> {"lineas", "escrito", "fallos", "resumen": {"Patient": [n…], "Encounter": [n…], "fallos": k}}."""
    lect = leer(almacen)
    res = {"lineas": [], "escrito": False, "fallos": list(lect["fallos"]), "resumen": {"Patient": [], "Encounter": [], "fallos": 0}}
    if not isinstance(almacen, dict):
        return res
    cab = esperado_canon["cabecera"]
    evento = cab.get("MsgEvent")
    proy = MA.proyectar(esperado_canon)
    C = MA.proyectar(MA.canonico_texto(canonico_observado)) if isinstance(canonico_observado, dict) \
        and isinstance(canonico_observado.get("cabecera"), dict) else None          # A3: el observado llega de SQL con None
    vistos, n_ident = set(), 0
    for tipo, ident in (("Patient", cab.get("Identifier")), ("Encounter", cab.get("VisitaId") if cab.get("TieneVisita") else None)):
        E = proy[tipo]
        if E is None:
            continue
        if not ident:
            if tipo == "Encounter" and "por_paciente" not in lect:       # con la relectura por paciente se juzga abajo (S-VE-3)
                res["lineas"].append(AO._linea("nota", "almacen_no_leido", "PV1-19", "ALM Encounter sin PV1-19 (S78): sin identifier con que releerlo; lo escrito no se juzga (L-ADT-19)", cuenta=False))
            continue
        n_ident += 1
        ent = lect["entradas"].get((tipo, ident))
        if ent is None:
            res["lineas"].append(AO._linea("nota", "almacen_no_leido", "PID" if tipo == "Patient" else "PV1", "ALM %s: el identifier %s no está en almacen_adt (el arnés lee por el canónico observado; su n no se observó)" % (tipo, ident), cuenta=False))
            continue
        vistos.add((tipo, ident))
        Ct = (C or {}).get(tipo) if C else None
        if _entrada(tipo, ident, E, Ct, ent, msa1, res, evento):
            res["escrito"] = True
    for k in lect["orden"]:                                            # leído con n ≥ 1 sin esperado (S77: un Encounter con PV1-2 = N)
        if k in vistos:
            continue
        ent = lect["entradas"][k]
        res["resumen"][k[0]].append(ent["n"])
        if ent["n"] >= 1:
            res["escrito"] = True
            res["lineas"].append(AO._linea("fidelidad", "almacen", "PV1-2" if k[0] == "Encounter" else "PID-3",
                                           "ALM %s: %d recurso(s) con el identifier %s que el mensaje no pedía (escrito lo que no se esperaba%s)" % (
                                               k[0], ent["n"], k[1], "; PV1-2 = N: sin visita, S77" if k[0] == "Encounter" and not cab.get("TieneVisita") else ""),
                                           causa="escritura"))
            if msa1 in ("AE", "AR"):
                res["lineas"].append(AO._linea("acuse", "rechazo_con_escritura", "destino", "ALM %s: %d recurso(s) con el identifier %s aunque MSA-1 = %s (esperado 0, S68)" % (k[0], ent["n"], k[1], msa1)))
    if "por_paciente" in lect:
        if _por_paciente(lect, cab, proy, C, msa1, res, evento):
            res["escrito"] = True
    elif not cab.get("TieneVisita") and cab.get("Identifier"):              # evidencia sin la relectura por paciente (L-VE-3)
        res["lineas"].append(AO._linea("nota", "almacen_no_leido", "PV1", "ALM Encounter: sin relectura por paciente, un Encounter sin identifier no se vería (L-VE-3)", cuenta=False))
    if msa1 in ("AE", "AR") and not res["escrito"] and n_ident:
        res["lineas"].append(AO._linea("nota", "almacen_vacio_tras_rechazo", "destino", "ALM: almacén leído tras MSA-1 %s: 0 recursos para los %d identifiers del mensaje%s [S68]" % (
            msa1, n_ident, " [S43][L22] atomicidad observada" if rechazo_http in (400, 422) else ""), cuenta=False))
    res["resumen"]["fallos"] = len(res["fallos"])
    return res


def _por_paciente(lect, cab, proy, C, msa1, res, evento):
    """S-VE-3 / R-VE-3 (diseño VE §2.4): los Encounter releídos por el paciente. Se juzgan los NUEVOS: ni en `previos` (anteriores
    al envío, no se juzgan: L-ADT-12) ni ya juzgados por su identifier en `visitas`. -> True si hubo escritura."""
    ya = {r["id"] for (t, _i), ent in lect["entradas"].items() if t == "Encounter" for r in ent["recursos"] if r["id"]}
    res["resumen"]["EncounterPaciente"], res["resumen"]["previos"] = [], []
    escrito = False
    for ent in lect["por_paciente"]:
        v, previos = ent["identificador"], set(ent["previos"])
        nuevos = [r for r in ent["recursos"] if r["id"] not in previos and r["id"] not in ya]
        res["resumen"]["EncounterPaciente"].append(len(nuevos))
        res["resumen"]["previos"].append(len(previos))
        if previos:
            res["lineas"].append(AO._linea("nota", "almacen_previos", "PV1", "ALM %d Encounter(s) del paciente %s anteriores al envío: no se juzgan (L-ADT-12)" % (len(previos), v), cuenta=False))
        if v != cab.get("Identifier"):                                # el paciente del canónico observado, no el esperado
            for r in nuevos:
                escrito = True
                res["lineas"].append(AO._linea("fidelidad", "almacen", "PID-3", "ALM Encounter id=%s de un paciente (%s) que el mensaje no pedía" % (r["id"], v), causa="escritura"))
            continue
        if cab.get("TieneVisita") and not cab.get("VisitaId"):         # S78: sin PV1-19 el Encounter se encuentra por el paciente
            E = proy["Encounter"]
            Ct = (C or {}).get("Encounter") if C else None
            if E is not None and _entrada("Encounter", "del paciente %s (sin PV1-19, S78)" % v, E, Ct,
                                          {"n": len(nuevos), "recursos": nuevos}, msa1, res, evento):
                escrito = True
            continue
        for r in nuevos:
            escrito = True
            if msa1 in ("AE", "AR"):
                res["lineas"].append(AO._linea("acuse", "rechazo_con_escritura", "destino", "ALM Encounter id=%s del paciente %s aunque MSA-1 = %s (esperado 0, S68)" % (r["id"], v, msa1)))
            elif not cab.get("TieneVisita"):
                res["lineas"].append(AO._linea("fidelidad", "almacen", "PV1-2", "ALM Encounter id=%s del paciente %s que el mensaje no pedía (PV1-2 = N: sin visita, S77)" % (r["id"], v), causa="escritura"))
            else:
                res["lineas"].append(AO._linea("fidelidad", "almacen", "PV1-19", "ALM Encounter id=%s del paciente %s sin el identifier visit|%s esperado" % (r["id"], v, cab.get("VisitaId")), causa="escritura"))
    return escrito


def evaluar(e, ms, m1s, pe, lec_por_mensaje=None):
    """Para cada mensaje k cuya sesión k trae `almacen_adt`: comparar(...) con el esperado del mapeador. -> {k: resultado}."""
    ses = e.get("sesiones") or []
    out = {}
    for k, m in enumerate(ms):
        s = ses[k] if k < len(ses) and isinstance(ses[k], dict) else None
        if s is None or not isinstance(s.get("almacen_adt"), dict):
            continue
        esp = MA.esperado_mensaje(m, pe)[0]
        http = ((lec_por_mensaje or {}).get(k) or {}).get("http")
        out[k] = comparar(s["almacen_adt"], esp, s.get("canonico_adt") if isinstance(s.get("canonico_adt"), dict) else None,
                          m1s[k] if k < len(m1s) else None, http if http in (400, 422) else None)
    return out


def almacen_sintetico(esperado_canon, n=1, leido="tras_ack", ack_msa1="AA", ids_desde=100):
    """Evidencia sintética: el almacén tal como quedaría si el circuito escribe exactamente la proyección del esperado."""
    proy = MA.proyectar(esperado_canon)
    cab = esperado_canon["cabecera"]
    out = {"leido": leido, "ack_msa1": ack_msa1, "pacientes": [], "visitas": [], "fallos": []}
    i = ids_desde
    for tipo, ident in (("Patient", cab.get("Identifier")), ("Encounter", cab.get("VisitaId") if cab.get("TieneVisita") else None)):
        if proy[tipo] is None or not ident:
            continue
        recs = []
        for _ in range(n):
            i += 1
            r = MA._limpio(MA._sin_nulos(proy[tipo]))
            r = dict(r, id=str(i), meta={"versionId": "1"})
            recs.append({"id": str(i), "crudo": json.dumps(r, ensure_ascii=False)})
        out[CLAVE[tipo]].append({"identificador": ident, "n": n, "recursos": recs})
    if cab.get("Identifier"):                                           # S-VE-3: la relectura por paciente, con los mismos Encounter
        enc = [r for ent in out["visitas"] for r in ent["recursos"]]
        if cab.get("TieneVisita") and not cab.get("VisitaId") and proy["Encounter"] is not None:     # S78: va por POST, sin identifier
            for _ in range(n):
                i += 1
                r = dict(MA._limpio(MA._sin_nulos(proy["Encounter"])), id=str(i), meta={"versionId": "1"})
                enc.append({"id": str(i), "crudo": json.dumps(r, ensure_ascii=False)})
        out["visitas_por_paciente"] = [{"identificador": cab["Identifier"], "n": len(enc), "recursos": enc, "previos": []}]
    return out


# ---------------------------------------------------------------------------- autoprueba
def autoprueba():
    mal, n = [], [0]

    def mira(nombre, obtenido, esperado_):
        n[0] += 1
        if obtenido != esperado_:
            mal.append("MAL %s: obtenido %r, esperado %r" % (nombre, obtenido, esperado_))

    def esp(texto):
        return MA.esperado_mensaje(MA._msg(texto))[0]

    base = ("MSH|^~\\&|HIS|H|LAB|L|20260101120000||ADT^%s^%s|M1|P|2.5\rEVN|%s|20260101120000\r"
            "PID|1||X1^^^H^MR||Pérez^Ana^^^^^L||19800101|F\rPV1|1|%s|URG^1^A|||||||MED|||||||||%s")
    e01 = esp(base % ("A01", "ADT_A01", "A01", "I", "V1"))
    clases = lambda r: sorted((z["clase"], z["subtipo"], z["hecho"]) for z in r["lineas"] if z["cuenta"])
    a = almacen_sintetico(e01)
    r = comparar(a, e01, None, "AA")
    mira("exacto: sin hallazgos", (clases(r), r["escrito"], r["resumen"]["Patient"], r["resumen"]["Encounter"]), ([], True, [1], [1]))
    # status cambiado en el almacén -> fidelidad/almacen PV1-2
    a2 = json.loads(json.dumps(a))
    v = json.loads(a2["visitas"][0]["recursos"][0]["crudo"])
    v["status"] = "finished"
    a2["visitas"][0]["recursos"][0]["crudo"] = json.dumps(v)
    mira("status distinto", clases(comparar(a2, e01, None, "AA")), [("fidelidad", "almacen", "PV1-2")])
    # A11 no cancelado -> hecho MSH-9
    e11 = esp(base % ("A11", "ADT_A09", "A11", "I", "V1"))
    a11 = almacen_sintetico(e11)
    v = json.loads(a11["visitas"][0]["recursos"][0]["crudo"])
    v["status"] = "in-progress"
    a11["visitas"][0]["recursos"][0]["crudo"] = json.dumps(v)
    mira("A11 sin cancelar: MSH-9", clases(comparar(a11, e11, None, "AA")), [("fidelidad", "almacen", "MSH-9")])
    # duplicado, ausente, rechazo con escritura, vacío tras rechazo
    mira("duplicado", clases(comparar(almacen_sintetico(e01, n=2), e01, None, "AA")),
         [("fidelidad", "duplicado", "PID"), ("fidelidad", "duplicado", "PV1")])
    vacio = {"leido": "tras_ack", "pacientes": [{"identificador": "X1", "n": 0, "recursos": []}],
             "visitas": [{"identificador": "V1", "n": 0, "recursos": []}]}
    mira("ausente con AA", clases(comparar(vacio, e01, None, "AA")), [("fidelidad", "ausente", "PID"), ("fidelidad", "ausente", "PV1")])
    mira("rechazo con escritura", clases(comparar(a, e01, None, "AE")),
         [("acuse", "rechazo_con_escritura", "destino"), ("acuse", "rechazo_con_escritura", "destino")])
    rv = comparar(vacio, e01, None, "AE")
    mira("vacío tras rechazo: nota", (clases(rv), [z["subtipo"] for z in rv["lineas"]]), ([], ["almacen_vacio_tras_rechazo"]))
    # PV1-2 = N: un Encounter leído que no se pedía
    eN = esp(base % ("A31", "ADT_A05", "A31", "N", ""))
    aN = almacen_sintetico(eN)
    aN["visitas"] = [{"identificador": "V9", "n": 1, "recursos": [{"id": "9", "crudo": json.dumps({"resourceType": "Encounter", "status": "in-progress"})}]}]
    mira("Encounter con PV1-2 = N", clases(comparar(aN, eN, None, "AA")), [("fidelidad", "almacen", "PV1-2")])
    # sin PV1-19 (S78): con la relectura por paciente se juzga el contenido (S-VE-3, Q-VE-D-4); sin ella, nota L-ADT-19 como antes
    e78 = esp(base % ("A01", "ADT_A01", "A01", "I", ""))
    r78 = comparar(almacen_sintetico(e78), e78, None, "AA")
    mira("sin PV1-19 con visitas_por_paciente: se juzga, sin nota L-ADT-19", (clases(r78), any("L-ADT-19" in z["que"] for z in r78["lineas"])), ([], False))
    a78 = almacen_sintetico(e78)
    a78.pop("visitas_por_paciente")
    r78 = comparar(a78, e78, None, "AA")
    mira("sin PV1-19 sin visitas_por_paciente (evidencia anterior): nota L-ADT-19", (clases(r78), any("L-ADT-19" in z["que"] for z in r78["lineas"])), ([], True))
    # causa a tres: el canónico observado ya traía el error -> transformacion
    obs = json.loads(json.dumps(e01))
    obs["cabecera"]["Gender"] = "male"
    ag = almacen_sintetico(obs)
    rg = comparar(ag, e01, obs, "AA")
    mira("causa transformacion", [(z["hecho"], z["causa"]) for z in rg["lineas"] if z["cuenta"]], [("PID-8", "transformacion")])
    rg2 = comparar(ag, e01, json.loads(json.dumps(e01)), "AA")
    mira("causa escritura", [(z["hecho"], z["causa"]) for z in rg2["lineas"] if z["cuenta"]], [("PID-8", "escritura")])
    # A3: el canónico observado llega de SQL con None en vez de "" (y sin hijas en algún caso): no revienta y la causa es la misma
    sql = json.loads(json.dumps(e01))
    sql["cabecera"] = {k: (None if v == "" else v) for k, v in sql["cabecera"].items()}
    sql["cabecera"]["Gender"] = "male"
    rg3 = comparar(ag, e01, sql, "AA")
    mira("observado de SQL (None): causa transformacion", [(z["hecho"], z["causa"]) for z in rg3["lineas"] if z["cuenta"]], [("PID-8", "transformacion")])
    # extra fuera del contrato: nota; id/meta no cuentan
    ax = json.loads(json.dumps(a))
    p = json.loads(ax["pacientes"][0]["recursos"][0]["crudo"])
    p["text"] = {"status": "generated"}
    ax["pacientes"][0]["recursos"][0]["crudo"] = json.dumps(p)
    rx = comparar(ax, e01, None, "AA")
    mira("extra: nota", (clases(rx), [z["subtipo"] for z in rx["lineas"]]), ([], ["almacen_extra"]))
    # fallo de lectura
    af = json.loads(json.dumps(a))
    af["pacientes"][0]["recursos"][0]["crudo"] = "{no es json"
    mira("crudo ilegible -> fallo", len(comparar(af, e01, None, "AA")["fallos"]), 1)
    # controles negativos
    antes = len(mal)
    mira("CN1", clases(r), [("fidelidad", "almacen", "PV1-2")])
    mira("CN2", clases(comparar(a2, e01, None, "AA")), [])
    mira("CN3", clases(comparar(vacio, e01, None, "AA")), [])
    det = len(mal) - antes
    del mal[antes:]
    if det != 3:
        mal.append("MAL controles negativos: %d de 3" % det)
    for x in mal:
        print(x)
    print("AUTOPRUEBA DE almacen_adt: %s (%d comprobaciones)" % ("TODO BIEN" if not mal else "FALLA %d" % len(mal), n[0]))
    return not mal


if __name__ == "__main__":
    sys.exit(0 if autoprueba() else 1)
