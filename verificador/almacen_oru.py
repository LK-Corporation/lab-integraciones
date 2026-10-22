#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Almacén FHIR en el veredicto ORU (diseno-oru-v11-fable.md §2-§3; S65, S67-S72). Compara lo que el emisor releyó del servidor
FHIR tras el ACK (`sesiones[].almacen_oru`, §1.1) con la PROYECCIÓN FHIR del canónico ESPERADO (`mapeador_oru.esperado_mensaje`).
La proyección es una regla del verificador, derivada de los ConceptMaps y de S57-S66 (tabla cerrada TABLA, §2.2/§2.3); no copia
FhirResultados.cls: la coincidencia con el circuito se mide (P1/P2), no se asume.

Hechos medidos el 4-oct contra el FHIR real de iris-ai (citados como [M-4oct-n]):
  [M-4oct-1] releer por id devuelve lo enviado igual salvo `id`/`meta` (codings y su orden, acentos, «\\n», zonas, fracciones);
             `DiagnosticReport.result` vuelve resuelto a «Observation/<id>» (se envió urn:uuid).
  [M-4oct-2] el servidor conserva el texto decimal exacto («1.20» -> 1.20; «100.0» -> 100.0; «95» -> 95).
  [M-4oct-3] el circuito escribe 1.2 donde el canónico dice «1.20» (FhirResultados.Quantity, %Set(…, "number")): CIR-ORU-4, se
             arregla aparte [S67]; aquí es fidelidad/almacen (FHIR R4 decimal: la precisión es significativa).

Declarados (D-ORU11-n) y desviaciones (DV-ORU11-n), también en CAMBIOS-P0.md y en info_verificador:
  D-ORU11-1  `id` y `meta` son metadatos del servidor: se descartan antes de comparar.
  D-ORU11-2  lectura textual: json.loads(crudo, parse_float=str, parse_int=str); todo escalar queda como texto y la comparación es
             textual («1.20» ≠ «1.2»; «95» = «95»); un número y la misma cadena entre comillas no se distinguen (L-ORU-10).
  D-ORU11-3  presencia: un elemento se espera AUSENTE cuando su campo canónico esperado está vacío (R4 JSON: las propiedades sin
             valor se omiten); «esperado <ausente>» / «observado <ausente>» son discrepancias.
  DV-ORU11-1 con n > 1 el contenido se compara sobre el PRIMER recurso; los demás solo se comparan con el primero (iguales/distintos).
  DV-ORU11-2 un identifier esperado que no está en las listas de almacen_oru (el arnés lee por el canónico OBSERVADO: un OBX que el
             circuito descartó no tiene entrada) no es `ausente` (su n no se observó): nota `almacen_no_leido` que no cuenta; el
             recuento del mapeador ya cuenta ese OBX (fidelidad/recuento).
  DV-ORU11-3 un identifier leído con n ≥ 1 que no corresponde a ninguna observación/informe esperado es fidelidad/almacen (hecho
             OBX/OBR, causa escritura): se escribió lo que no se esperaba.
  DV-ORU11-4 la causa a tres (E esperado, C canónico observado proyectado, A almacén): A = C -> transformacion; C = E -> escritura;
             los tres distintos -> transformacion+escritura; sin canónico observado comparable -> escritura.
  DV-ORU11-5 identificadores por PAPEL, no por índice: propio (system urn:lab:integraciones:obs|dr), PLAC y FILL (type.coding.code,
             system v2-0203), otros; `result` por pertenencia resuelta (L-ORU-12). Un value[x] con otra clave que la que manda
             ValorTipo es UNA discrepancia «value[x]» (hecho OBX-5), no una por hoja.
Límites: L-ORU-10 (solo el contrato v1; lo demás es nota almacen_extra), L-ORU-11 (una lectura, tras el ACK), L-ORU-12 (result por
pertenencia dentro de lo leído; no se llama a nada), L-ORU-13 (n > 1: el primero). Tolerancia AMB-ORU-7 [S72]: orden de coding[] o
interpretation[] distinto con el mismo contenido.

Uso: python3 almacen_oru.py --autoprueba
"""
import json
import re
import sys

SISTEMA_OBS = "urn:lab:integraciones:obs"                      # D-ORU-1
SISTEMA_DR = "urn:lab:integraciones:dr"                        # D-ORU-1
SISTEMA_MRN = "urn:lab:integraciones:mrn"                      # [S58] referencia lógica por PID-3 (regla MR)
SISTEMA_0203 = "http://terminology.hl7.org/CodeSystem/v2-0203"  # [M] table-hl70203-to-v2-0203
SISTEMA_INTERP = "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation"  # [M] table-hl70078-to-v3-observationinterpretation
METADATOS = ("id", "meta")                                      # D-ORU11-1
VALORES = {"quantity": "valueQuantity", "string": "valueString", "codeableconcept": "valueCodeableConcept",
           "datetime": "valueDateTime", "time": "valueTime", "range": "valueRange", "ratio": "valueRatio"}   # [M OBX-5]
AUSENTE = "<ausente>"
CONTRATO = {"Observation": {"resourceType", "identifier", "status", "code", "subject", "effectiveDateTime", "interpretation", "referenceRange"},
            "DiagnosticReport": {"resourceType", "identifier", "status", "code", "subject", "effectiveDateTime", "effectivePeriod", "issued", "result"}}
ORDENABLES = ("code.coding", "valueCodeableConcept.coding", "interpretation")   # AMB-ORU-7 [S72]

# ---------------------------------------------------------------------------- tabla cerrada §2.2/§2.3 (consultar_tabla proyeccion_fhir_oru)
TABLA = [
    {"recurso": "Observation", "elemento": "resourceType", "campo": "—", "hecho": "OBX", "regla": "= Observation", "citas": ["[M ORU]"]},
    {"recurso": "Observation", "elemento": "identifier[]", "campo": "Identificador", "hecho": "OBX", "regla": "exactamente UN identifier propio {system urn:lab:integraciones:obs, value <MSH-10>#i.j}", "citas": ["[D-ORU-1]"]},
    {"recurso": "Observation", "elemento": "status", "campo": "Estado", "hecho": "OBX-11", "regla": "igual; esperado tupla [S22] -> pertenencia", "citas": ["[M OBX-11]", "[M 0085]", "[S62]"]},
    {"recurso": "Observation", "elemento": "code.coding[1].code/.display/.system", "campo": "CodigoCode/Display/Sistema", "hecho": "OBX-3", "regla": "cada subelemento presente <=> campo no vacío; igual", "citas": ["[M OBX-3]", "[M CE]", "[S61]"]},
    {"recurso": "Observation", "elemento": "code.coding[2]", "campo": "CodigoAlt*", "hecho": "OBX-3", "regla": "idem; ausente <=> los tres vacíos", "citas": ["[M CE]"]},
    {"recurso": "Observation", "elemento": "subject.identifier.system/.value", "campo": "PacienteId", "hecho": "PID-3", "regla": "presente <=> PacienteId ≠ ''; system urn:lab:integraciones:mrn, value PacienteId", "citas": ["[S58]", "[S60]"]},
    {"recurso": "Observation", "elemento": "effectiveDateTime", "campo": "Fecha", "hecho": "OBX-14", "regla": "presente <=> Fecha ≠ ''; texto exacto, zona incluida", "citas": ["[M OBX-14]", "[S63]", "[S66]", "[M-4oct-1]"]},
    {"recurso": "Observation", "elemento": "value[x]", "campo": "ValorTipo", "hecho": "OBX-5", "regla": "exactamente la clave que manda ValorTipo (quantity->valueQuantity, string->valueString, codeableconcept->valueCodeableConcept, datetime->valueDateTime, time->valueTime, range->valueRange, ratio->valueRatio); sin_valor/no_soportado -> ninguna", "citas": ["[M OBX-5]", "[L-ORU-2]"]},
    {"recurso": "Observation", "elemento": "valueQuantity.value", "campo": "ValorNumero", "hecho": "OBX-5", "regla": "texto decimal EXACTO («1.20» ≠ «1.2»)", "citas": ["[M NM]", "[M SN]", "[F decimal]", "[D-ORU-2]", "[M-4oct-2]", "[M-4oct-3]"]},
    {"recurso": "Observation", "elemento": "valueQuantity.comparator", "campo": "ValorComparador", "hecho": "OBX-5", "regla": "presente <=> ≠ ''; igual", "citas": ["[M SN]"]},
    {"recurso": "Observation", "elemento": "valueQuantity.unit/.code/.system", "campo": "UnidadTexto/UnidadCode/UnidadSistema", "hecho": "OBX-6", "regla": "unit presente <=> UnidadTexto ≠ ''; code+system presentes <=> ambos ≠ ''", "citas": ["[M OBX-6]", "[M CWE unidades]", "[DV-ORU-7]"]},
    {"recurso": "Observation", "elemento": "valueString", "campo": "ValorTexto", "hecho": "OBX-5", "regla": "igual (con «\\n» de D-ORU-3 y escapes resueltos)", "citas": ["[M OBX-5]", "[D-ORU-3]", "[M-4oct-1]"]},
    {"recurso": "Observation", "elemento": "valueCodeableConcept.coding[1..2], .text", "campo": "ValorCodigo/Display/Sistema, ValorAlt*, ValorTextoOriginal", "hecho": "OBX-5", "regla": "como code; text presente <=> ValorTextoOriginal ≠ ''", "citas": ["[M OBX-5]", "[M CE]", "[M CWE texto]", "[M IS]"]},
    {"recurso": "Observation", "elemento": "valueDateTime / valueTime", "campo": "ValorFecha", "hecho": "OBX-5", "regla": "igual", "citas": ["[M OBX-5]", "[M DTM]", "[AMB-ORU-1]"]},
    {"recurso": "Observation", "elemento": "valueRange.low/high.value/.unit/.code/.system", "campo": "ValorNumero/ValorNum2 + Unidad*", "hecho": "OBX-5 / OBX-6", "regla": "low.value = ValorNumero, high.value = ValorNum2 (texto decimal); unidad en ambos", "citas": ["[M SN]", "[M OBX-6]", "[F decimal]"]},
    {"recurso": "Observation", "elemento": "valueRatio.numerator/denominator", "campo": "ValorNumero/ValorNum2 + ValorComparador + Unidad*", "hecho": "OBX-5 / OBX-6", "regla": "numerator.value = ValorNumero, numerator.comparator si ≠ '', denominator.value = ValorNum2; unidad en ambos", "citas": ["[M SN]", "[M OBX-6]", "[F decimal]"]},
    {"recurso": "Observation", "elemento": "interpretation[]", "campo": "Interpretacion (códigos por «;»)", "hecho": "OBX-8", "regla": "lista ordenada de {coding: [{system v3-ObservationInterpretation, code}]}; ausente <=> ''", "citas": ["[M OBX-8]", "[M 0078]"]},
    {"recurso": "Observation", "elemento": "referenceRange[]", "campo": "RangoRef", "hecho": "OBX-7", "regla": "exactamente una entrada {text} <=> ≠ ''; igual", "citas": ["[M OBX-7]"]},
    {"recurso": "Observation", "elemento": "id, meta", "campo": "—", "hecho": "—", "regla": "se descartan (D-ORU11-1)", "citas": ["[D-ORU11-1]", "[M-4oct-1]"]},
    {"recurso": "Observation", "elemento": "cualquier otro elemento", "campo": "—", "hecho": "—", "regla": "nota almacen_extra que no cuenta (L-ORU-10) [S69]", "citas": ["[L-ORU-10]", "[S69]"]},
    {"recurso": "DiagnosticReport", "elemento": "identifier[] propio", "campo": "MsgControlId + Orden", "hecho": "OBR", "regla": "exactamente uno {system urn:lab:integraciones:dr, value <MSH-10>#i}", "citas": ["[D-ORU-1]"]},
    {"recurso": "DiagnosticReport", "elemento": "identifier[] PLAC", "campo": "Placer", "hecho": "OBR-2", "regla": "presente <=> ≠ ''; value igual; type.coding.system v2-0203", "citas": ["[M OBR-2]", "[M 0203]"]},
    {"recurso": "DiagnosticReport", "elemento": "identifier[] FILL", "campo": "Filler", "hecho": "OBR-3", "regla": "idem", "citas": ["[M OBR-3]", "[M 0203]"]},
    {"recurso": "DiagnosticReport", "elemento": "status", "campo": "Estado", "hecho": "OBR-25", "regla": "igual; tupla [S22] -> pertenencia; vacío -> unknown [S64]", "citas": ["[M OBR-25]", "[M 0123]", "[S64]"]},
    {"recurso": "DiagnosticReport", "elemento": "code", "campo": "Codigo*", "hecho": "OBR-4", "regla": "como Observation.code", "citas": ["[M OBR-4]", "[M CE]", "[S61]"]},
    {"recurso": "DiagnosticReport", "elemento": "subject.identifier", "campo": "PacienteId", "hecho": "PID-3", "regla": "como Observation", "citas": ["[S58]"]},
    {"recurso": "DiagnosticReport", "elemento": "effectiveDateTime ⊕ effectivePeriod{start,end}", "campo": "Efectivo, EfectivoFin", "hecho": "OBR-7 / OBR-8", "regla": "EfectivoFin ≠ '' -> effectivePeriod.end = EfectivoFin y .start = Efectivo si ≠ ''; si no, effectiveDateTime = Efectivo si ≠ ''; nunca ambos", "citas": ["[M OBR-7]", "[M OBR-8]"]},
    {"recurso": "DiagnosticReport", "elemento": "issued", "campo": "Emitido", "hecho": "OBR-22", "regla": "presente <=> ≠ ''; igual", "citas": ["[M OBR-22]", "[D-ORU-5]"]},
    {"recurso": "DiagnosticReport", "elemento": "result[]", "campo": "observaciones con Informe = i, en orden OrdenEnInforme", "hecho": "OBX", "regla": "cada reference «Observation/<id>» se resuelve al identifier de la Observation leída con ese id; la lista debe ser exactamente [<MSH-10>#i.1 … #i.k]; una referencia fuera de lo leído se anota sin seguirla (L-ORU-12)", "citas": ["[M ORU]", "[M-4oct-1]", "[L-ORU-12]"]},
    {"recurso": "DiagnosticReport", "elemento": "otros", "campo": "—", "hecho": "—", "regla": "nota almacen_extra (L-ORU-10)", "citas": ["[L-ORU-10]"]},
]


# ---------------------------------------------------------------------------- hecho por ruta (sin índice: DV-ORU-4, fusiona con el mapeador)
def hecho_almacen(recurso, ruta):
    """Hecho (SEG-n) del elemento `ruta` (notación a.b[1].c de la proyección normalizada) de un recurso del contrato."""
    r = re.sub(r"\[\d+\]", "", ruta)
    cab = r.split(".")[0]
    if recurso == "Observation":
        if cab in ("resourceType", "identifier"):
            return "OBX"
        if cab == "status":
            return "OBX-11"
        if cab == "code":
            return "OBX-3"
        if cab == "subject":
            return "PID-3"
        if cab == "effectiveDateTime":
            return "OBX-14"
        if cab == "interpretation":
            return "OBX-8"
        if cab == "referenceRange":
            return "OBX-7"
        if cab.startswith("value"):
            return "OBX-6" if r.split(".")[-1] in ("unit", "code", "system") and cab in ("valueQuantity", "valueRange", "valueRatio") else "OBX-5"
        return "OBX"
    if cab == "identifier":
        papel = r.split(".")[1] if "." in r else ""
        return {"PLAC": "OBR-2", "FILL": "OBR-3"}.get(papel, "OBR")
    return {"status": "OBR-25", "code": "OBR-4", "subject": "PID-3", "effectiveDateTime": "OBR-7", "issued": "OBR-22",
            "result": "OBX", "effectivePeriod": "OBR-8" if r.endswith(".end") else "OBR-7"}.get(cab, "OBR")


# ---------------------------------------------------------------------------- proyección del canónico esperado (tabla §2.2/§2.3)
def _pon(d, k, v):
    """'' (campo vacío) -> ausente (D-ORU11-3); None (imposible ya contado, S10) -> marca «no juzgar»; lo demás, presente."""
    if v == "" or v == [] or v == {}:
        return
    d[k] = v


def _coding(code, display, system):
    c = {}
    _pon(c, "system", system)                                     # [M CE] CE.3 -> system (uri por S61)
    _pon(c, "code", code)                                         # CE.1 -> code
    _pon(c, "display", display)                                   # CE.2 -> display
    return c


def _codeable(x, prefijo, alt_prefijo, text=""):
    """[M] datatype-ce-to-codeableconcept: CE.1-3 -> coding[1], CE.4-6 -> coding[2]; CWE.9 -> text. None si algún campo es imposible.
    Nombres del canónico: Codigo{Code,Display,Sistema}/CodigoAlt{…} para OBX-3/OBR-4; Valor{Codigo,Display,Sistema}/ValorAlt{…} para OBX-5."""
    cod = "Codigo" if prefijo.startswith("Valor") else "Code"
    vals = [x.get(prefijo + cod), x.get(prefijo + "Display"), x.get(prefijo + "Sistema"),
            x.get(alt_prefijo + cod), x.get(alt_prefijo + "Display"), x.get(alt_prefijo + "Sistema"), text]
    if any(v is None for v in vals):
        return None
    cc = {}
    codings = [c for c in (_coding(vals[0], vals[1], vals[2]), _coding(vals[3], vals[4], vals[5])) if c]
    _pon(cc, "coding", codings)
    _pon(cc, "text", text)
    return cc


def _cantidad(valor, comparador, x):
    """[M] nm-to-quantity NM.1 -> value; sn-to-quantity SN.1 -> comparator; cwe-to-quantity CWE.2 -> unit, CWE.1/.3 -> code/system."""
    q = {}
    q["value"] = valor                                            # None = no juzgar; '' (SN sin Num1, AMB-ORU-8) -> sin value
    if valor == "":
        del q["value"]
    _pon(q, "comparator", comparador)
    _pon(q, "unit", x.get("UnidadTexto"))
    uc, us = x.get("UnidadCode"), x.get("UnidadSistema")
    if uc is None or us is None:                                  # imposible ya contado (S10): «no juzgar»
        _pon(q, "code", uc)
        _pon(q, "system", us)
    elif uc != "" and us != "":                                   # N5: code y system, los dos o ninguno (tabla, fila 67)
        q["code"], q["system"] = uc, us
    return q


def _sujeto(cab):
    pid = cab.get("PacienteId")
    if pid is None:
        return None
    return {"identifier": {"system": SISTEMA_MRN, "value": pid}} if pid != "" else ""    # [S58] [S60]


def proyectar_observation(o, cab):
    """Proyección FHIR (normalizada: identifier por papeles) de una observación del canónico esperado."""
    r = {"resourceType": "Observation"}                           # [M ORU] OBX -> Observation[2]
    ident = o.get("Identificador")
    r["identifier"] = None if ident is None else {"propio": [{"value": ident}]}   # D-ORU-1
    r["status"] = o.get("Estado")                                 # [M OBX-11] -> status; tupla [S22]
    _pon(r, "code", _codeable(o, "Codigo", "CodigoAlt"))          # [M OBX-3] -> code
    _pon(r, "subject", _sujeto(cab))
    _pon(r, "effectiveDateTime", o.get("Fecha"))                  # [M OBX-14]; [S63] OBR-7; [S66] zona
    vt = o.get("ValorTipo")
    if vt is None:
        r["value[x]"] = None                                      # OBX-2 imposible: no se juzga value[x]
    elif vt == "quantity":                                        # [M OBX-5] NM / SN sin separador -> valueQuantity
        _pon(r, "valueQuantity", _cantidad(o.get("ValorNumero"), o.get("ValorComparador"), o))   # A7: {} -> ausente (FHIR JSON)
    elif vt == "string":                                          # [M OBX-5] ST/FT/TX, SN «<>»/«+» -> valueString
        r["valueString"] = o.get("ValorTexto")
    elif vt == "codeableconcept":                                 # [M OBX-5] CE/CWE/CNE/IS -> valueCodeableConcept
        r["valueCodeableConcept"] = _codeable(o, "Valor", "ValorAlt", o.get("ValorTextoOriginal"))
    elif vt == "datetime":                                        # [M OBX-5] DTM/DT (TS por AMB-ORU-1) -> valueDateTime
        r["valueDateTime"] = o.get("ValorFecha")
    elif vt == "time":                                            # [M OBX-5] TM -> valueTime
        r["valueTime"] = o.get("ValorFecha")
    elif vt == "range":                                           # [M] sn-to-range SN.2 -> low.value, SN.4 -> high.value; OBX-6 en ambos
        rg = {}
        if o.get("ValorNumero") != "":
            rg["low"] = _cantidad(o.get("ValorNumero"), "", o)
        if o.get("ValorNum2") != "":
            rg["high"] = _cantidad(o.get("ValorNum2"), "", o)
        _pon(r, "valueRange", rg)                                 # A7
    elif vt == "ratio":                                           # [M] sn-to-ratio SN.1 -> numerator.comparator, SN.2/SN.4 -> values
        rt = {}
        if o.get("ValorNumero") != "":
            rt["numerator"] = _cantidad(o.get("ValorNumero"), o.get("ValorComparador"), o)
        if o.get("ValorNum2") != "":
            rt["denominator"] = _cantidad(o.get("ValorNum2"), "", o)
        _pon(r, "valueRatio", rt)                                 # A7
    # sin_valor / no_soportado: ninguna value* (L-ORU-2)
    inter = o.get("Interpretacion")                               # [M OBX-8] -> interpretation; [M 0078] equivalent
    r["interpretation"] = None if inter is None else [{"coding": [{"system": SISTEMA_INTERP, "code": c}]} for c in inter.split(";") if c != ""]
    if r["interpretation"] == []:
        del r["interpretation"]
    rr = o.get("RangoRef")                                        # [M OBX-7] -> referenceRange.text
    r["referenceRange"] = None if rr is None else [{"text": rr}]
    if r["referenceRange"] == [{"text": ""}]:
        del r["referenceRange"]
    return r


def proyectar_diagnostic_report(inf, cab, identifiers_obx):
    """Proyección FHIR normalizada de un informe del canónico esperado; `identifiers_obx`: identifiers de sus observaciones en orden."""
    r = {"resourceType": "DiagnosticReport"}                      # [M ORU] OBR -> DiagnosticReport[1]
    msh10 = cab.get("MsgControlId")
    ident = {"propio": [{"value": "%s#%s" % (msh10, inf["Orden"])}]} if msh10 is not None else None   # D-ORU-1
    for campo, papel in (("Placer", "PLAC"), ("Filler", "FILL")):  # [M OBR-2]/[M OBR-3] identifier + type.coding PLAC/FILL [M 0203]
        v = inf.get(campo)
        if v is None:
            ident = ident if ident is None else dict(ident, **{papel: None})
        elif v != "" and ident is not None:
            ident[papel] = [{"value": v, "type_system": SISTEMA_0203}]
    r["identifier"] = ident
    r["status"] = inf.get("Estado")                               # [M OBR-25] IF VALUED; [S64] unknown
    _pon(r, "code", _codeable(inf, "Codigo", "CodigoAlt"))        # [M OBR-4]
    _pon(r, "subject", _sujeto(cab))
    ef, fin = inf.get("Efectivo"), inf.get("EfectivoFin")
    if ef is None or fin is None:
        r["effectiveDateTime"], r["effectivePeriod"] = None, None
    elif fin != "":                                               # [M OBR-8] -> effectivePeriod.end; OBR-7 -> .start IF OBR-8 VALUED
        per = {"end": fin}
        _pon(per, "start", ef)
        r["effectivePeriod"] = per
    else:                                                         # [M OBR-7] -> effectiveDateTime IF OBR-8 NOT VALUED
        _pon(r, "effectiveDateTime", ef)
    r["issued"] = inf.get("Emitido")                              # [M OBR-22] -> issued; D-ORU-5
    if r["issued"] == "":
        del r["issued"]
    _pon(r, "result", list(identifiers_obx))                      # R7: pertenencia resuelta (§2.3)
    return r


def proyectar_mensaje(esp):
    """-> (observaciones [(obs_esp, proyección)], informes [(inf_esp, proyección)]) del canónico esperado de un mensaje."""
    cab = esp.get("cabecera") or {}
    obs = [(o, proyectar_observation(o, cab)) for o in esp.get("observaciones") or []]
    infs = []
    for inf in esp.get("informes") or []:
        ids = [o.get("Identificador") for o in sorted((o for o in esp.get("observaciones") or [] if o.get("Informe") == inf.get("Orden")),
                                                      key=lambda o: o.get("OrdenEnInforme") or 0)]
        infs.append((inf, proyectar_diagnostic_report(inf, cab, ids)))
    return obs, infs


# ---------------------------------------------------------------------------- de la proyección normalizada al recurso FHIR (y a texto crudo)
class Num(str):
    """Texto decimal que se serializa como número JSON tal cual («1.20» -> 1.20): para sintetizar recursos sin perder precisión."""


_DECIMALES = ("valueQuantity.value", "valueRange.low.value", "valueRange.high.value", "valueRatio.numerator.value", "valueRatio.denominator.value")


def recurso_fhir(proy, ids_por_identifier=None):
    """Proyección normalizada -> recurso FHIR R4 (identifier[] de verdad; result[].reference = Observation/<id> por `ids_por_identifier`,
    o urn:uuid:<identifier> si no hay id). Los decimales quedan como Num (números en `crudo_de`). Las marcas None se omiten."""
    ids_por_identifier = ids_por_identifier or {}
    r = {}
    for k, v in proy.items():
        if v is None or k == "value[x]":
            continue
        if k == "identifier":
            lista = []
            for e in v.get("propio") or []:
                lista.append({"system": SISTEMA_OBS if proy.get("resourceType") == "Observation" else SISTEMA_DR, "value": e["value"]})
            for papel in ("PLAC", "FILL"):
                for e in v.get(papel) or []:
                    lista.append({"type": {"coding": [{"system": e["type_system"], "code": papel}]}, "value": e["value"]})
            for e in v.get("otros") or []:
                lista.append(e)
            r["identifier"] = lista
        elif k == "result":
            r["result"] = [{"reference": "Observation/%s" % ids_por_identifier[i] if i in ids_por_identifier else "urn:uuid:%s" % i} for i in v]
        else:
            r[k] = json.loads(json.dumps(v))
    for ruta in _DECIMALES:
        partes = ruta.split(".")
        d = r
        for p in partes[:-1]:
            d = d.get(p) if isinstance(d, dict) else None
            if d is None:
                break
        if isinstance(d, dict) and isinstance(d.get(partes[-1]), str):
            d[partes[-1]] = Num(d[partes[-1]])
    return r


def crudo_de(recurso):
    """Serializa un recurso con los Num como números JSON sin comillas (lo que un servidor que conserva la precisión devuelve)."""
    def f(x):
        if isinstance(x, Num):
            return str(x)
        if isinstance(x, dict):
            return "{" + ",".join(json.dumps(k, ensure_ascii=False) + ":" + f(v) for k, v in x.items()) + "}"
        if isinstance(x, list):
            return "[" + ",".join(f(v) for v in x) + "]"
        return json.dumps(x, ensure_ascii=False)
    return f(recurso)


# ---------------------------------------------------------------------------- lectura textual del almacén (D-ORU11-2) y normalización
def parsear(crudo):
    """json.loads con parse_float=str y parse_int=str: «1.20» sigue siendo «1.20». -> (dict, None) o (None, motivo)."""
    if not isinstance(crudo, str):
        return None, "crudo no es texto (%s)" % type(crudo).__name__
    try:
        d = json.loads(crudo, parse_float=str, parse_int=str, parse_constant=str)
    except ValueError as ex:
        return None, "JSON ilegible (%s)" % str(ex)[:80]
    if not isinstance(d, dict):
        return None, "el JSON no es un objeto"
    return d, None


def leer(almacen):
    """-> {"indice": {id: identificador (Observation)}, "entradas": {(tipo, identificador): entrada}, "fallos": [textos]}.
    Entrada: {"identificador", "n", "recursos": [{"id", "crudo", "obj" (parseado o None), "error"}]}."""
    out = {"indice": {}, "entradas": {}, "fallos": [], "orden": []}
    if not isinstance(almacen, dict):
        return out
    for tipo, clave in (("Observation", "observaciones"), ("DiagnosticReport", "informes")):
        for ent in almacen.get(clave) or []:
            if not isinstance(ent, dict) or not isinstance(ent.get("identificador"), str):
                out["fallos"].append("entrada de %s sin identificador en almacen_oru" % clave)
                continue
            recs = []
            for rc in ent.get("recursos") or []:
                rc = rc if isinstance(rc, dict) else {}
                obj, err = parsear(rc.get("crudo"))
                rid = rc.get("id") if isinstance(rc.get("id"), str) else (obj or {}).get("id") if isinstance((obj or {}).get("id"), str) else None
                recs.append({"id": rid, "crudo": rc.get("crudo"), "obj": obj, "error": err})
                if tipo == "Observation" and rid is not None:
                    out["indice"][rid] = ent["identificador"]
            n = ent.get("n")
            if not isinstance(n, int) or isinstance(n, bool):
                n = len(recs)
            k = (tipo, ent["identificador"])
            out["entradas"][k] = {"identificador": ent["identificador"], "n": n, "recursos": recs, "tipo": tipo}
            out["orden"].append(k)
    for f in almacen.get("fallos") or []:
        if isinstance(f, dict):
            out["fallos"].append("lectura del almacén fallida para %s: %s HTTP %s (%s)" % (
                f.get("identificador"), f.get("paso") or "?", f.get("http") if f.get("http") is not None else "—", (f.get("detalle") or "")[:120]))
        else:
            out["fallos"].append("lectura del almacén fallida: %r" % (f,))
    return out


def _clasificar_identifiers(lista, propio_system):
    """identifier[] -> {propio: [...], PLAC: [...], FILL: [...], otros: [...]} (DV-ORU11-5). Cada entrada conserva lo que no se consume."""
    out = {"propio": [], "PLAC": [], "FILL": [], "otros": []}
    for e in lista if isinstance(lista, list) else [lista]:
        if not isinstance(e, dict):
            out["otros"].append(e)
            continue
        e = dict(e)
        if e.get("system") == propio_system:
            e.pop("system")
            out["propio"].append(e)
            continue
        tipo = e.get("type") if isinstance(e.get("type"), dict) else {}
        codings = tipo.get("coding") if isinstance(tipo.get("coding"), list) else []
        papel = next((c.get("code") for c in codings if isinstance(c, dict) and c.get("code") in ("PLAC", "FILL")), None)
        if papel:
            c0 = next(c for c in codings if isinstance(c, dict) and c.get("code") == papel)
            e.pop("type")
            e["type_system"] = c0.get("system", AUSENTE)
            if len(codings) > 1 or len(tipo) > 1:
                e["type_extra"] = "true"
            out[papel].append(e)
            continue
        out["otros"].append(e)
    return {k: v for k, v in out.items() if v}


def normalizar(obj, tipo, indice):
    """Recurso leído -> forma comparable: sin id/meta (D-ORU11-1), identifier por papeles, result resuelto a identifiers (L-ORU-12)."""
    a = {k: v for k, v in obj.items() if k not in METADATOS}
    if "identifier" in a:
        a["identifier"] = _clasificar_identifiers(a["identifier"], SISTEMA_OBS if tipo == "Observation" else SISTEMA_DR)
    if tipo == "DiagnosticReport" and "result" in a:
        res = []
        for ref in a["result"] if isinstance(a["result"], list) else [a["result"]]:
            texto = ref.get("reference") if isinstance(ref, dict) else ref
            texto = texto if isinstance(texto, str) else json.dumps(texto, ensure_ascii=False)
            rid = texto.split("/")[-1] if texto.startswith("Observation/") else texto[len("urn:uuid:"):] if texto.startswith("urn:uuid:") else texto
            res.append(indice.get(rid, "%s (fuera del almacén leído)" % texto))
        a["result"] = res
    return a


# ---------------------------------------------------------------------------- comparación hoja a hoja
def _hojas(obj, pref="", out=None, nulos_como_texto=True):
    """Aplana a {ruta: hoja}. Hojas: str, tupla (pertenencia), None (marca «no juzgar», solo en el esperado); en el observado
    null -> «null», true/false -> «true»/«false» (D-ORU11-2: todo texto)."""
    out = {} if out is None else out
    if isinstance(obj, dict):
        if not obj:
            out[pref] = "{}" if pref else "{}"
        for k, v in obj.items():
            _hojas(v, pref + "." + k if pref else k, out, nulos_como_texto)
    elif isinstance(obj, list):
        if not obj:
            out[pref] = "[]"
        for i, v in enumerate(obj, 1):
            _hojas(v, "%s[%d]" % (pref, i), out, nulos_como_texto)
    elif isinstance(obj, bool):
        out[pref] = "true" if obj else "false"
    elif obj is None:
        out[pref] = "null" if nulos_como_texto else None
    else:
        out[pref] = obj
    return out


def _ruta(obj, ruta):
    d = obj
    for p in ruta.split("."):
        d = d.get(p) if isinstance(d, dict) else None
    return d


def _ordenar_como(a, e):
    """AMB-ORU-7 [S72]: si una lista de codings/interpretaciones observada es una permutación de la esperada, se reordena como la esperada."""
    tol = []
    for ruta in ORDENABLES:
        le, la = _ruta(e, ruta), _ruta(a, ruta)
        if not (isinstance(le, list) and isinstance(la, list)) or le == la or len(le) != len(la):
            continue
        ke = sorted(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in le)
        ka = sorted(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in la)
        if ke == ka:
            padre, hoja = ruta.rsplit(".", 1) if "." in ruta else (None, ruta)
            dest = _ruta(a, padre) if padre else a
            dest[hoja] = [json.loads(k) for k in sorted((json.dumps(x, sort_keys=True, ensure_ascii=False) for x in la), key=lambda s: [json.dumps(x, sort_keys=True, ensure_ascii=False) for x in le].index(s))]
            tol.append("[AMB-ORU-7] %s: el almacén trae los mismos elementos en otro orden (FHIR no da semántica al orden) [S72]" % ruta)
    return tol


def _repr(v):
    return AUSENTE if v is AUSENTE else repr(v)


def comparar_recurso(E, A, tipo):
    """Proyección esperada E (normalizada) frente a recurso observado A (normalizado). -> (lineas [(ruta, hecho, esperado, observado)],
    extras [elementos fuera del contrato], tolerancias [textos AMB-ORU-7]). `esperado`/`observado` son AUSENTE o el valor."""
    A = json.loads(json.dumps(A))
    tol = _ordenar_como(A, E)
    lineas, extras = [], []
    he = _hojas(E, nulos_como_texto=False)
    saltar = tuple(k for k, v in he.items() if v is None)
    he = {k: v for k, v in he.items() if v is not None}
    E_ = dict(E)
    A_ = dict(A)
    if tipo == "Observation" and "value[x]" not in saltar:        # DV-ORU11-5: la clave value[x] es UNA discrepancia
        ve = sorted(k for k in E_ if k.startswith("value"))
        va = sorted(k for k in A_ if k.startswith("value"))
        if ve != va:
            lineas.append(("value[x]", "OBX-5", ve[0] if ve else AUSENTE, ("+".join(va) if len(va) > 1 else va[0]) if va else AUSENTE))
            for k in ve + va:
                E_.pop(k, None)
                A_.pop(k, None)
    if tipo == "DiagnosticReport" and "result" not in saltar:    # R7 pertenencia resuelta (L-ORU-12)
        re_, ra = E_.pop("result", AUSENTE), A_.pop("result", AUSENTE)
        if (re_ if re_ is not AUSENTE else []) != (ra if ra is not AUSENTE else []):
            lineas.append(("result", "OBX", re_, ra))
    he = _hojas(E_, nulos_como_texto=False)
    he = {k: v for k, v in he.items() if v is not None}
    ha = _hojas(A_)
    vistos = set()
    for ruta in list(he) + [r for r in ha if r not in he]:
        if any(ruta == s or ruta.startswith(s + ".") or ruta.startswith(s + "[") for s in saltar) or ruta in vistos or \
                ("value[x]" in saltar and ruta.startswith("value")):     # N3: «no se juzga value[x]» vale para toda clave value*
            continue
        vistos.add(ruta)
        cab = re.sub(r"\[\d+\]", "", ruta).split(".")[0]
        if ruta not in he:
            if cab in CONTRATO[tipo] or (tipo == "Observation" and cab.startswith("value")):
                lineas.append((ruta, hecho_almacen(tipo, ruta), AUSENTE, ha[ruta]))
            elif cab not in extras:
                extras.append(cab)
        elif ruta not in ha:
            lineas.append((ruta, hecho_almacen(tipo, ruta), he[ruta], AUSENTE))
        else:
            e, a = he[ruta], ha[ruta]
            if isinstance(e, tuple):
                if a not in e:
                    lineas.append((ruta, hecho_almacen(tipo, ruta), e, a))
            elif str(e) != str(a):
                lineas.append((ruta, hecho_almacen(tipo, ruta), e, a))
    return lineas, extras, tol


# ---------------------------------------------------------------------------- evaluación de un mensaje (§3)
def _linea(clase, subtipo, hecho, que, cuenta=True, causa=None):
    return {"clase": clase, "subtipo": subtipo, "hecho": hecho, "que": que, "cuenta": cuenta, "causa": causa}


def _buscar_observado(canon, o):
    """La observación del canónico observado que corresponde a la esperada (por Identificador; si no, por (Informe, OrdenEnInforme))."""
    lista = (canon or {}).get("observaciones") if isinstance(canon, dict) else None
    if not isinstance(lista, list):
        return None
    por_id = [c for c in lista if isinstance(c, dict) and c.get("Identificador") == o.get("Identificador")]
    if por_id:
        return por_id[0]
    return next((c for c in lista if isinstance(c, dict) and str(c.get("Informe")) == str(o.get("Informe"))
                 and str(c.get("OrdenEnInforme")) == str(o.get("OrdenEnInforme"))), None)


def _buscar_informe_observado(canon, inf):
    lista = (canon or {}).get("informes") if isinstance(canon, dict) else None
    if not isinstance(lista, list):
        return None
    return next((c for c in lista if isinstance(c, dict) and str(c.get("Orden")) == str(inf.get("Orden"))), None)


def _texto_canon(c):
    """Canónico observado -> con las columnas enteras como texto, para proyectarlo con la misma regla."""
    return {k: (str(v) if isinstance(v, int) and not isinstance(v, bool) else v) for k, v in c.items()}


def _causa(ruta, E_h, C_h, a_valor):
    """DV-ORU11-4: comparación a tres sobre una hoja. C_h None = sin canónico comparable."""
    if C_h is None:
        return "escritura"
    c = C_h.get(ruta, AUSENTE)
    e = E_h.get(ruta, AUSENTE)
    if str(c) == str(a_valor) if a_valor is not AUSENTE else c is AUSENTE:
        return "transformacion"
    if (c in e or str(c) in map(str, e)) if isinstance(e, tuple) else (str(c) == str(e) if e is not AUSENTE else c is AUSENTE):
        return "escritura"                                        # N9: una tupla de valores tolerados (S22) se mira por pertenencia
    return "transformacion+escritura"


def _hojas_proy(p):
    h = _hojas(p, nulos_como_texto=False) if p is not None else {}
    return {k: v for k, v in h.items() if v is not None}


def _comparar_entrada(tipo, donde, ident, E, C, entrada, msa1, res, extras_notas):
    """Un identifier esperado frente a su entrada del almacén. Añade líneas a res; devuelve True si hubo escritura (n > 0)."""
    n = entrada["n"]
    res["resumen"][tipo].append(n)
    hecho_rec = "OBX" if tipo == "Observation" else "OBR"
    if n == 0:
        if msa1 == "AA":
            res["lineas"].append(_linea("fidelidad", "ausente", hecho_rec, "ALM %s: ningún recurso con el identifier %s (el circuito acusó AA: esperado 1)" % (donde, ident), causa="escritura"))
        return False
    if msa1 in ("AE", "AR"):
        res["lineas"].append(_linea("acuse", "rechazo_con_escritura", "destino", "ALM %s: %d recurso(s) con el identifier %s aunque MSA-1 = %s (esperado 0: nada debió escribirse, S59/S68)" % (donde, n, ident, msa1)))
    if n > 1:
        iguales = None
        objs = [r["obj"] for r in entrada["recursos"] if r["obj"] is not None]
        if len(objs) > 1:
            base = normalizar(objs[0], tipo, res["indice"])
            iguales = all(normalizar(x, tipo, res["indice"]) == base for x in objs[1:])
        res["lineas"].append(_linea("fidelidad", "duplicado", hecho_rec, "ALM %s: %d recursos con el identifier %s (esperado 1)%s" % (
            donde, n, ident, "" if iguales is None else "; los demás son %s al primero (DV-ORU11-1)" % ("iguales" if iguales else "distintos")), causa="escritura"))
    primero = entrada["recursos"][0] if entrada["recursos"] else None
    if primero is None:
        res["lineas"].append(_linea("nota", "almacen_sin_contenido", hecho_rec, "ALM %s: n=%d pero sin recurso leído para %s (contenido no comparado)" % (donde, n, ident), cuenta=False))
        return True
    if primero["obj"] is None:
        res["fallos"].append("lectura del almacén fallida para %s: %s" % (ident, primero["error"]))
        res["resumen"]["fallos"] = len(res["fallos"])                # N10
        return True
    for i, r in enumerate(entrada["recursos"][1:], 2):             # N6: un recurso ilegible que no es el primero también falla
        if r["obj"] is None:
            res["fallos"].append("lectura del almacén fallida para %s (recurso %d de %d): %s" % (ident, i, len(entrada["recursos"]), r["error"]))
            res["resumen"]["fallos"] = len(res["fallos"])            # N10
    A = normalizar(primero["obj"], tipo, res["indice"])
    lineas, extras, tol = comparar_recurso(E, A, tipo)
    E_h = _hojas_proy(E)
    C_h = _hojas_proy(C) if C is not None else None
    A_h = _hojas(normalizar(primero["obj"], tipo, res["indice"]))
    for ruta, hecho, e, a in lineas:
        causa = _causa(ruta, E_h, C_h, a if ruta not in ("value[x]", "result") else a)
        if ruta in ("value[x]", "result") and C_h is not None:
            cv = sorted(k for k in (C or {}) if k.startswith("value")) if ruta == "value[x]" else (C or {}).get("result", AUSENTE)
            ev = sorted(k for k in E if k.startswith("value")) if ruta == "value[x]" else E.get("result", AUSENTE)
            if ruta == "value[x]":
                cv, ev = (cv[0] if cv else AUSENTE), (ev[0] if ev else AUSENTE)
            causa = "transformacion" if cv == a else ("escritura" if cv == ev else "transformacion+escritura")
        sufijo = " (el almacén reproduce el canónico)" if causa == "transformacion" else ""
        res["lineas"].append(_linea("fidelidad", "almacen", hecho, "ALM %s %s: esperado %s, observado %s%s" % (donde, ruta, _repr(e), _repr(a), sufijo), causa=causa))
    if C_h is not None:                                           # fila 5 de §3.2: el canónico difiere pero el almacén coincide con lo esperado
        for ruta, cv in C_h.items():
            ev = E_h.get(ruta, AUSENTE)
            if ruta.startswith("value") and "value[x]" in [l[0] for l in lineas]:
                continue
            if (str(cv) != str(ev) if not isinstance(ev, tuple) else cv not in ev) and ruta in A_h and (str(A_h[ruta]) == str(ev) if not isinstance(ev, tuple) else A_h[ruta] in ev):
                res["lineas"].append(_linea("nota", "almacen_canonico", hecho_almacen(tipo, ruta), "ALM %s %s: el almacén coincide con lo esperado (%s) aunque el canónico guardó %s (causa canonico: anomalía anotada)" % (donde, ruta, _repr(ev), _repr(cv)), cuenta=False, causa="canonico"))
        for ruta, ev in E_h.items():
            if ruta not in C_h and ruta in A_h and not ruta.startswith("value") and not isinstance(ev, tuple) and str(A_h[ruta]) == str(ev) and not any(ruta.startswith(s) for s in ("identifier", "resourceType")):
                res["lineas"].append(_linea("nota", "almacen_canonico", hecho_almacen(tipo, ruta), "ALM %s %s: el almacén coincide con lo esperado (%s) aunque el canónico no lo guardó (causa canonico: anomalía anotada)" % (donde, ruta, _repr(ev)), cuenta=False, causa="canonico"))
    if extras:
        res["lineas"].append(_linea("nota", "almacen_extra", hecho_rec, "ALM %s %s: elementos fuera del contrato v1: %s (no se juzgan, L-ORU-10) [S69]" % (tipo, ident, ", ".join(sorted(extras))), cuenta=False))
    for t in tol:
        res["lineas"].append(_linea("nota", "AMB-ORU-7", hecho_rec, "ALM %s %s" % (donde, t), cuenta=False))
    return True


def comparar(almacen, esperado, canonico_observado=None, msa1=None, rechazo_http=None):
    """Un mensaje. -> {"lineas": [{clase, subtipo, hecho, que, cuenta, causa}], "escrito": bool, "fallos": [textos de lectura],
    "resumen": {"Observation": [n…], "DiagnosticReport": [n…], "fallos": k}, "indice": {id: identificador}}.
    msa1: el MSA-1 observado equivalente (AA/AE/AR) o None si no hubo ACK; rechazo_http: 400/422 si FHIR rechazó (S43)."""
    lect = leer(almacen)
    res = {"lineas": [], "escrito": False, "fallos": list(lect["fallos"]), "resumen": {"Observation": [], "DiagnosticReport": [], "fallos": 0},
           "indice": lect["indice"]}
    res["resumen"]["fallos"] = len(lect["fallos"])
    if not isinstance(almacen, dict):
        return res
    obs_p, inf_p = proyectar_mensaje(esperado)
    vistos = set()
    n_ident = 0
    for o, E in obs_p:
        ident = o.get("Identificador")
        if ident is None:
            continue
        n_ident += 1
        donde = "OBX %s (%s)" % (o.get("Orden"), o.get("CodigoCode") or "")
        ent = lect["entradas"].get(("Observation", ident))
        if ent is None:                                           # DV-ORU11-2
            res["lineas"].append(_linea("nota", "almacen_no_leido", "OBX", "ALM %s: el identifier %s no está en almacen_oru (el arnés lee por el canónico observado; su n no se observó)" % (donde, ident), cuenta=False))
            continue
        vistos.add(("Observation", ident))
        c = _buscar_observado(canonico_observado, o)
        C = proyectar_observation(_texto_canon(dict(c, Identificador=ident)), (canonico_observado or {}).get("cabecera") or {}) if isinstance(c, dict) else None
        if _comparar_entrada("Observation", donde, ident, E, C, ent, msa1, res, None):
            res["escrito"] = True
    for inf, E in inf_p:
        ident = (E.get("identifier") or {}).get("propio", [{}])[0].get("value") if isinstance(E.get("identifier"), dict) else None
        if ident is None:
            continue
        n_ident += 1
        donde = "OBR %s (%s)" % (inf.get("Orden"), inf.get("CodigoCode") or "")
        ent = lect["entradas"].get(("DiagnosticReport", ident))
        if ent is None:
            res["lineas"].append(_linea("nota", "almacen_no_leido", "OBR", "ALM %s: el identifier %s no está en almacen_oru (el arnés lee por el canónico observado; su n no se observó)" % (donde, ident), cuenta=False))
            continue
        vistos.add(("DiagnosticReport", ident))
        c = _buscar_informe_observado(canonico_observado, inf)
        C = None
        if isinstance(c, dict):
            co = (canonico_observado or {}).get("observaciones") or []
            ids_c = [x.get("Identificador") for x in sorted((x for x in co if isinstance(x, dict) and str(x.get("Informe")) == str(inf.get("Orden"))),
                                                           key=lambda x: int(x.get("OrdenEnInforme") or 0)) if isinstance(x.get("Identificador"), str)]
            C = proyectar_diagnostic_report(_texto_canon(dict(c, Orden=inf.get("Orden"))), (canonico_observado or {}).get("cabecera") or {}, ids_c)
        if _comparar_entrada("DiagnosticReport", donde, ident, E, C, ent, msa1, res, None):
            res["escrito"] = True
    for k in lect["orden"]:                                       # DV-ORU11-3: leído con n ≥ 1 sin esperado
        if k in vistos:
            continue
        ent = lect["entradas"][k]
        res["resumen"][k[0]].append(ent["n"])
        if ent["n"] >= 1:
            res["escrito"] = True
            res["lineas"].append(_linea("fidelidad", "almacen", "OBX" if k[0] == "Observation" else "OBR",
                                        "ALM %s: %d recurso(s) con el identifier %s sin %s esperada (escrito lo que no se esperaba)" % (
                                            k[0], ent["n"], k[1], "observación" if k[0] == "Observation" else "informe"), causa="escritura"))
            if msa1 in ("AE", "AR"):                              # N4: tras AE/AR no debió escribirse nada, esperado o no (S59/S68)
                res["lineas"].append(_linea("acuse", "rechazo_con_escritura", "destino", "ALM %s: %d recurso(s) con el identifier %s aunque MSA-1 = %s (esperado 0: nada debió escribirse, S59/S68)" % (k[0], ent["n"], k[1], msa1)))
    if msa1 in ("AE", "AR") and not res["escrito"] and n_ident:
        s43 = " [S43][L22] la atomicidad de la transacción (S59) está observada, no supuesta" if rechazo_http in (400, 422) else " (atomicidad S59 observada)"
        res["lineas"].append(_linea("nota", "almacen_vacio_tras_rechazo", "destino", "ALM: almacén leído tras MSA-1 %s: 0 recursos para los %d identifiers del mensaje%s [S68]" % (msa1, n_ident, s43), cuenta=False))
    return res


def evaluar(e, ms, m1s, pe, lec_por_mensaje=None):
    """Para cada mensaje k cuya sesión k trae `almacen_oru` (dict): comparar(...) con el esperado del mapeador. -> {k: resultado}.
    ms: mensajes (mapeador_referencia.Msg); m1s: MSA-1 observado equivalente por k (o None); pe: punto de entrada (dict o nombre)."""
    import mapeador_oru as MO
    ses = e.get("sesiones") or []
    out = {}
    for k, m in enumerate(ms):
        s = ses[k] if k < len(ses) and isinstance(ses[k], dict) else None
        if s is None or not isinstance(s.get("almacen_oru"), dict):
            continue
        esp = MO.esperado_mensaje(m, pe)[0]
        http = ((lec_por_mensaje or {}).get(k) or {}).get("http")
        out[k] = comparar(s["almacen_oru"], esp, s.get("canonico_oru") if isinstance(s.get("canonico_oru"), dict) else None,
                          m1s[k] if k < len(m1s) else None, http if http in (400, 422) else None)
    return out


# ---------------------------------------------------------------------------- evidencia sintética (prueba_oru, P1, P2)
def almacen_sintetico(esperado, n=1, leido="tras_ack", ack_msa1="AA", ids_desde=100):
    """`almacen_oru` como lo produciría el arnés si el almacén tuviera exactamente la proyección del esperado, n recursos por
    identifier (0 = vacío), con decimales exactos en el JSON crudo. Formato §1.1 (ver ejemplo_almacen_oru.json)."""
    obs_p, inf_p = proyectar_mensaje(esperado)
    ids = {}
    sig = [ids_desde]

    def nuevo_id():
        sig[0] += 1
        return str(sig[0])
    observaciones = []
    for o, E in obs_p:
        ident = o.get("Identificador")
        recs = []
        for _ in range(n):
            rid = nuevo_id()
            ids.setdefault(ident, rid)
            r = dict(recurso_fhir(E), id=rid)
            r["meta"] = {"versionId": "1", "lastUpdated": "2026-10-04T12:00:00Z"}
            recs.append({"id": rid, "crudo": crudo_de(r)})
        observaciones.append({"identificador": ident, "n": n, "recursos": recs})
    informes = []
    for inf, E in inf_p:
        ident = E["identifier"]["propio"][0]["value"]
        recs = []
        for _ in range(n):
            rid = nuevo_id()
            r = dict(recurso_fhir(E, ids), id=rid)
            r["meta"] = {"versionId": "1", "lastUpdated": "2026-10-04T12:00:00Z"}
            recs.append({"id": rid, "crudo": crudo_de(r)})
        informes.append({"identificador": ident, "n": n, "recursos": recs})
    return {"leido": leido, "ack_msa1": ack_msa1, "informes": informes, "observaciones": observaciones, "fallos": []}


# ---------------------------------------------------------------------------- autoprueba: por regla, un caso que delata y uno que no
def autoprueba():
    mal = []
    n_ok = [0]

    def mira(nombre, obtenido, esperado_):
        ok = obtenido == esperado_
        n_ok[0] += ok
        print(("  ok  " if ok else "  MAL ") + nombre + ("" if ok else ": %r != %r" % (obtenido, esperado_)))
        if not ok:
            mal.append(nombre)

    def obs_base(**kw):
        o = {"Orden": 1, "OrdenEnInforme": 1, "Informe": 1, "CodigoCode": "2160-0", "CodigoDisplay": "Creatinina", "CodigoSistema": "http://loinc.org",
             "CodigoAltCode": "", "CodigoAltDisplay": "", "CodigoAltSistema": "", "SubId": "", "ValorTipo": "quantity", "ValorNumero": "1.20",
             "ValorComparador": "", "ValorNum2": "", "ValorSeparador": "", "ValorTexto": "", "ValorCodigo": "", "ValorDisplay": "", "ValorSistema": "",
             "ValorAltCodigo": "", "ValorAltDisplay": "", "ValorAltSistema": "", "ValorTextoOriginal": "", "ValorFecha": "", "ValorCrudo": "",
             "RepeticionesPerdidas": 0, "UnidadCode": "mg/dL", "UnidadTexto": "mg/dL", "UnidadSistema": "http://unitsofmeasure.org", "RangoRef": "0.7-1.3",
             "Interpretacion": "H;LL", "Estado": "final", "Fecha": "2023-01-04T08:00:00.5+01:00", "FechaOrigen": "OBX-14", "Identificador": "ORU-X#1.1"}
        o.update(kw)
        return o
    cab = {"MsgControlId": "ORU-X", "PacienteId": "MRN1", "NumInformes": 1, "NumObservaciones": 1}
    inf = {"Orden": 1, "Placer": "PL-1", "Filler": "FL-1", "CodigoCode": "24323-8", "CodigoDisplay": "Panel", "CodigoSistema": "http://loinc.org",
           "CodigoAltCode": "PMB", "CodigoAltDisplay": "Panel básico", "CodigoAltSistema": "urn:lab:integraciones:cs:L", "Estado": "final",
           "Efectivo": "2023-01-04T07:30:00+01:00", "EfectivoFin": "2023-01-04T07:45:00+01:00", "Emitido": "2023-01-04T09:15:00+01:00", "NumObx": 1}
    variantes = {
        "quantity": obs_base(),
        "quantity comparador": obs_base(ValorComparador=">", ValorNumero="100.0"),
        "string": obs_base(ValorTipo="string", ValorNumero="", ValorTexto="Crecimiento escaso\nSe recomienda repetir ^ 2 & más", UnidadCode="", UnidadTexto="", UnidadSistema=""),
        "codeableconcept": obs_base(ValorTipo="codeableconcept", ValorNumero="", ValorCodigo="E", ValorDisplay="E. coli", ValorSistema="http://snomed.info/sct",
                                    ValorAltCodigo="EC", ValorAltDisplay="Escherichia", ValorAltSistema="urn:lab:integraciones:cs:L", ValorTextoOriginal="E. coli",
                                    UnidadCode="", UnidadTexto="", UnidadSistema=""),
        "datetime": obs_base(ValorTipo="datetime", ValorNumero="", ValorFecha="2023-01-04T08:00:00+01:00", UnidadCode="", UnidadTexto="", UnidadSistema=""),
        "time": obs_base(ValorTipo="time", ValorNumero="", ValorFecha="08:00:00", UnidadCode="", UnidadTexto="", UnidadSistema=""),
        "range": obs_base(ValorTipo="range", ValorNumero="1", ValorNum2="5", ValorSeparador="-"),
        "ratio": obs_base(ValorTipo="ratio", ValorNumero="1", ValorNum2="10", ValorSeparador=":", ValorComparador="<"),
        "sin_valor": obs_base(ValorTipo="sin_valor", ValorNumero="", UnidadCode="", UnidadTexto="", UnidadSistema="", Estado="cancelled"),
        "no_soportado": obs_base(ValorTipo="no_soportado", ValorNumero="", ValorCrudo="Observador^Sintetico", UnidadCode="", UnidadTexto="", UnidadSistema=""),
        "sin interpretacion ni rango ni fecha": obs_base(Interpretacion="", RangoRef="", Fecha="", FechaOrigen="ninguna"),
    }
    for nombre, o in variantes.items():
        esp = {"cabecera": dict(cab), "informes": [dict(inf)], "observaciones": [o]}
        alm = almacen_sintetico(esp)
        r = comparar(alm, esp, esp, "AA")
        mira("%s: proyección contra sí misma (AA, n=1) -> nada" % nombre, [l for l in r["lineas"] if l["cuenta"]] + r["fallos"], [])
        mira("%s: resumen n" % nombre, (r["resumen"], r["escrito"]), ({"Observation": [1], "DiagnosticReport": [1], "fallos": 0}, True))
        # por regla: cada hoja del recurso FHIR mutada -> exactamente una línea fidelidad/almacen con el hecho de la tabla
        rec = json.loads(alm["observaciones"][0]["recursos"][0]["crudo"], parse_float=str, parse_int=str)
        hojas = _hojas(rec)
        for ruta in hojas:
            if ruta.split(".")[0].split("[")[0] in METADATOS:
                continue
            mut = json.loads(json.dumps(rec))
            partes = re.findall(r"([^.\[\]]+)|\[(\d+)\]", ruta)
            d = mut
            for p, i in partes[:-1]:
                d = d[p] if p else d[int(i) - 1]
            p, i = partes[-1]
            k_ = p if p else int(i) - 1
            if ruta == "resourceType":
                d[k_] = "Specimen"
            elif ruta.startswith("identifier") and ruta.endswith(".system"):
                d[k_] = "urn:otro"
            else:
                d[k_] = (d[k_] + "X") if isinstance(d[k_], str) else "X"
            alm2 = json.loads(json.dumps(alm))
            alm2["observaciones"][0]["recursos"][0]["crudo"] = json.dumps(mut, ensure_ascii=False)
            r2 = comparar(alm2, esp, esp, "AA")
            cuentan = [l for l in r2["lineas"] if l["cuenta"]]
            esperado_hecho = ("OBX" if ruta.startswith(("identifier", "resourceType")) else hecho_almacen("Observation", ruta.replace("identifier[1]", "identifier.propio[1]")))
            firmas = sorted({(l["clase"], l["subtipo"], l["hecho"], l["causa"]) for l in cuentan})
            # el identifier propio con otro system deja de ser «propio» (DV-ORU11-5): varias hojas OBX, todas del almacén
            mira("%s: mutar %s -> %sfidelidad/almacen hecho %s causa escritura" % (nombre, ruta, "" if ruta.endswith("identifier[1].system") else "1 ", esperado_hecho),
                 (firmas, len(cuentan) if not ruta.endswith("identifier[1].system") else 1), ([("fidelidad", "almacen", esperado_hecho, "escritura")], 1))
        # borrar cada elemento de primer nivel -> una línea (o una por hoja) con observado <ausente>
        for k in list(rec):
            if k in METADATOS or k == "resourceType":
                continue
            mut = {kk: v for kk, v in rec.items() if kk != k}
            alm2 = json.loads(json.dumps(alm))
            alm2["observaciones"][0]["recursos"][0]["crudo"] = json.dumps(mut, ensure_ascii=False)
            cuentan = [l for l in comparar(alm2, esp, esp, "AA")["lineas"] if l["cuenta"]]
            mira("%s: sin %s -> fidelidad/almacen con <ausente>" % (nombre, k), bool(cuentan) and all(l["subtipo"] == "almacen" and AUSENTE in l["que"] for l in cuentan), True)
    # control negativo clave: 1.2 frente a «1.20» = exactamente 1 hallazgo OBX-5 causa escritura (CIR-ORU-4) [M-4oct-2/3]
    esp = {"cabecera": dict(cab), "informes": [dict(inf)], "observaciones": [obs_base()]}
    alm = almacen_sintetico(esp)
    mira("el crudo sintético lleva 1.20 como número", '"value":1.20' in alm["observaciones"][0]["recursos"][0]["crudo"], True)
    alm2 = json.loads(json.dumps(alm))
    alm2["observaciones"][0]["recursos"][0]["crudo"] = alm2["observaciones"][0]["recursos"][0]["crudo"].replace('"value":1.20', '"value":1.2')
    r = comparar(alm2, esp, esp, "AA")
    mira("1.2 frente a «1.20»: exactamente 1 hallazgo fidelidad/almacen OBX-5 causa escritura",
         [(l["subtipo"], l["hecho"], l["causa"], l["que"]) for l in r["lineas"] if l["cuenta"]],
         [("almacen", "OBX-5", "escritura", "ALM OBX 1 (2160-0) valueQuantity.value: esperado '1.20', observado '1.2'")])
    mira("control: 1.20 como número y «1.20» como texto no se distinguen (D-ORU11-2, L-ORU-10)",
         [l for l in comparar(json.loads(json.dumps(alm, ensure_ascii=False).replace('\\"value\\":1.20', '\\"value\\":\\"1.20\\"')), esp, esp, "AA")["lineas"] if l["cuenta"]], [])
    # causa a tres (DV-ORU11-4)
    c_mal = json.loads(json.dumps(esp))
    c_mal["observaciones"][0]["ValorNumero"] = "1.2"
    r = comparar(alm2, esp, c_mal, "AA")
    mira("A = C ≠ E -> causa transformacion (el almacén reproduce el canónico)", [(l["causa"], "reproduce el canónico" in l["que"]) for l in r["lineas"] if l["cuenta"]], [("transformacion", True)])
    r = comparar(alm2, esp, esp, "AA")
    mira("C = E ≠ A -> causa escritura", [l["causa"] for l in r["lineas"] if l["cuenta"]], ["escritura"])
    c_mal["observaciones"][0]["ValorNumero"] = "1.3"
    r = comparar(alm2, esp, c_mal, "AA")
    mira("los tres distintos -> transformacion+escritura", [l["causa"] for l in r["lineas"] if l["cuenta"]], ["transformacion+escritura"])
    r = comparar(alm, esp, c_mal, "AA")
    mira("A = E ≠ C -> nada cuenta; nota almacen_canonico", ([l for l in r["lineas"] if l["cuenta"]], [l["subtipo"] for l in r["lineas"]]), ([], ["almacen_canonico"]))
    r = comparar(alm2, esp, None, "AA")
    mira("sin canónico observado -> causa escritura (declarada)", [l["causa"] for l in r["lineas"] if l["cuenta"]], ["escritura"])
    # unidad: solo en el almacén -> OBX-6 escritura; también en el canónico -> transformacion
    rec = json.loads(alm["observaciones"][0]["recursos"][0]["crudo"], parse_float=str)
    for k in ("unit", "code", "system"):
        rec["valueQuantity"].pop(k)
    alm3 = json.loads(json.dumps(alm))
    alm3["observaciones"][0]["recursos"][0]["crudo"] = json.dumps(rec)
    r = comparar(alm3, esp, esp, "AA")
    mira("unidad quitada solo del recurso -> 3 hojas OBX-6 causa escritura", sorted({(l["hecho"], l["causa"]) for l in r["lineas"] if l["cuenta"]}), [("OBX-6", "escritura")])
    c_u = json.loads(json.dumps(esp))
    c_u["observaciones"][0].update(UnidadCode="", UnidadTexto="", UnidadSistema="")
    r = comparar(alm3, esp, c_u, "AA")
    mira("unidad quitada del canónico Y del recurso -> OBX-6 causa transformacion", sorted({(l["hecho"], l["causa"]) for l in r["lineas"] if l["cuenta"]}), [("OBX-6", "transformacion")])
    # status: tupla [S22] pertenencia
    esp_t = json.loads(json.dumps(esp))
    esp_t["observaciones"][0]["Estado"] = ["final", "amended"]
    esp_t["observaciones"][0]["Estado"] = tuple(esp_t["observaciones"][0]["Estado"])
    mira("status en la tupla [S22] -> nada", [l for l in comparar(alm, esp_t, esp, "AA")["lineas"] if l["cuenta"]], [])
    rec_s = json.loads(json.dumps(json.loads(alm["observaciones"][0]["recursos"][0]["crudo"], parse_float=str)))
    rec_s["status"] = "registered"
    alm_s = json.loads(json.dumps(alm))
    alm_s["observaciones"][0]["recursos"][0]["crudo"] = json.dumps(rec_s)
    mira("status fuera de la tupla -> OBX-11", [(l["hecho"], l["subtipo"]) for l in comparar(alm_s, esp_t, esp, "AA")["lineas"] if l["cuenta"]], [("OBX-11", "almacen")])
    # campo esperado None (imposible, S10) no se juzga
    esp_n = json.loads(json.dumps(esp))
    esp_n["observaciones"][0]["Estado"] = None
    mira("Estado None (imposible ya contado) -> status no se juzga", [l for l in comparar(alm_s, esp_n, esp, "AA")["lineas"] if l["cuenta"]], [])
    # duplicado, ausente, extra, orden de coding, value[x], rechazo, fallos, no leído, sobrante
    r = comparar(almacen_sintetico(esp, n=2), esp, esp, "AA")
    mira("n=2 -> fidelidad/duplicado OBX y OBR, iguales al primero; cuenta", sorted((l["subtipo"], l["hecho"], "iguales" in l["que"], l["cuenta"]) for l in r["lineas"]), [("duplicado", "OBR", True, True), ("duplicado", "OBX", True, True)])
    r = comparar(almacen_sintetico(esp, n=0), esp, esp, "AA")
    mira("n=0 con AA -> fidelidad/ausente OBX y OBR", sorted((l["subtipo"], l["hecho"], l["causa"]) for l in r["lineas"] if l["cuenta"]), [("ausente", "OBR", "escritura"), ("ausente", "OBX", "escritura")])
    r = comparar(almacen_sintetico(esp, n=0), esp, esp, "AE")
    mira("n=0 con AE -> nada cuenta; nota almacen_vacio_tras_rechazo", ([l for l in r["lineas"] if l["cuenta"]], [l["subtipo"] for l in r["lineas"]], r["escrito"]), ([], ["almacen_vacio_tras_rechazo"], False))
    r = comparar(almacen_sintetico(esp, n=0), esp, esp, "AR", 422)
    mira("n=0 con AR 422 -> la nota cita [S43][L22]", any("[S43][L22]" in l["que"] for l in r["lineas"]), True)
    r = comparar(alm, esp, esp, "AE")
    mira("n=1 con AE -> acuse/rechazo_con_escritura hecho destino (x2) y escrito", (sorted((l["clase"], l["subtipo"], l["hecho"]) for l in r["lineas"] if l["cuenta"]), r["escrito"]),
         ([("acuse", "rechazo_con_escritura", "destino")] * 2, True))
    r = comparar(alm, esp, esp, None)
    mira("n=1 sin ACK -> nada cuenta pero escrito (evidencia de «escrito sin acusar»)", ([l for l in r["lineas"] if l["cuenta"]], r["escrito"]), ([], True))
    rec_x = json.loads(alm["observaciones"][0]["recursos"][0]["crudo"], parse_float=str)
    rec_x["performer"] = [{"display": "Lab"}]
    rec_x["text"] = {"status": "generated", "div": "<div/>"}
    alm_x = json.loads(json.dumps(alm))
    alm_x["observaciones"][0]["recursos"][0]["crudo"] = json.dumps(rec_x)
    r = comparar(alm_x, esp, esp, "AA")
    mira("performer y text -> nota almacen_extra que no cuenta", ([l for l in r["lineas"] if l["cuenta"]], [(l["subtipo"], l["cuenta"], "performer, text" in l["que"]) for l in r["lineas"]]), ([], [("almacen_extra", False, True)]))
    esp_cc = {"cabecera": dict(cab), "informes": [dict(inf)], "observaciones": [variantes["codeableconcept"]]}
    alm_cc = almacen_sintetico(esp_cc)
    rec_cc = json.loads(alm_cc["observaciones"][0]["recursos"][0]["crudo"], parse_float=str)
    rec_cc["valueCodeableConcept"]["coding"].reverse()
    rec_cc["interpretation"].reverse()
    alm_cc2 = json.loads(json.dumps(alm_cc))
    alm_cc2["observaciones"][0]["recursos"][0]["crudo"] = json.dumps(rec_cc, ensure_ascii=False)
    r = comparar(alm_cc2, esp_cc, esp_cc, "AA")
    mira("coding e interpretation en otro orden -> nada cuenta; 2 notas AMB-ORU-7", ([l for l in r["lineas"] if l["cuenta"]], [l["subtipo"] for l in r["lineas"]]), ([], ["AMB-ORU-7", "AMB-ORU-7"]))
    rec_cc = json.loads(alm_cc["observaciones"][0]["recursos"][0]["crudo"], parse_float=str)
    rec_cc["valueCodeableConcept"]["coding"][1]["code"] = "ECX"
    alm_cc2["observaciones"][0]["recursos"][0]["crudo"] = json.dumps(rec_cc, ensure_ascii=False)
    r = comparar(alm_cc2, esp_cc, esp_cc, "AA")
    mira("control: coding con otro contenido -> cuenta (OBX-5), sin AMB-ORU-7", [(l["hecho"], l["cuenta"], l["subtipo"]) for l in r["lineas"]], [("OBX-5", True, "almacen")])
    rec_v = json.loads(alm["observaciones"][0]["recursos"][0]["crudo"], parse_float=str)
    rec_v["valueString"] = rec_v.pop("valueQuantity")["value"]
    alm_v = json.loads(json.dumps(alm))
    alm_v["observaciones"][0]["recursos"][0]["crudo"] = json.dumps(rec_v)
    r = comparar(alm_v, esp, esp, "AA")
    mira("value[x] con otra clave -> UNA discrepancia value[x] OBX-5", [(l["hecho"], l["que"]) for l in r["lineas"] if l["cuenta"]],
         [("OBX-5", "ALM OBX 1 (2160-0) value[x]: esperado 'valueQuantity', observado 'valueString'")])
    alm_f = json.loads(json.dumps(alm))
    alm_f["fallos"] = [{"identificador": "ORU-X#1.1", "paso": "get", "http": 500, "detalle": "Internal error"}]
    r = comparar(alm_f, esp, esp, "AA")
    mira("fallos -> lectura (indeterminado), no hallazgo", (r["fallos"], [l for l in r["lineas"] if l["cuenta"]]), (["lectura del almacén fallida para ORU-X#1.1: get HTTP 500 (Internal error)"], []))
    alm_i = json.loads(json.dumps(alm))
    alm_i["observaciones"][0]["recursos"][0]["crudo"] = "{no es json"
    r = comparar(alm_i, esp, esp, "AA")
    mira("crudo ilegible -> lectura", (len(r["fallos"]), r["fallos"][0].startswith("lectura del almacén fallida para ORU-X#1.1: JSON ilegible")), (1, True))
    alm_nl = json.loads(json.dumps(alm))
    alm_nl["observaciones"], alm_nl["informes"] = [], []
    r = comparar(alm_nl, esp, esp, "AA")
    mira("identifiers esperados sin entrada -> notas almacen_no_leido (DV-ORU11-2), no ausente", ([(l["subtipo"], l["cuenta"], l["hecho"]) for l in r["lineas"]], r["escrito"]), ([("almacen_no_leido", False, "OBX"), ("almacen_no_leido", False, "OBR")], False))
    alm_nl["informes"] = alm["informes"]
    r = comparar(alm_nl, esp, esp, "AA")
    mira("control: el DR apunta a una Observation que no se leyó -> result fuera del almacén leído (L-ORU-12)", [(l["hecho"], "fuera del almacén leído" in l["que"]) for l in r["lineas"] if l["cuenta"]], [("OBX", True)])
    alm_sb = json.loads(json.dumps(alm))
    alm_sb["observaciones"].append({"identificador": "ORU-X#1.9", "n": 1, "recursos": [dict(alm["observaciones"][0]["recursos"][0], id="999")]})
    r = comparar(alm_sb, esp, esp, "AA")
    mira("identifier leído con n=1 sin esperado -> fidelidad/almacen OBX (DV-ORU11-3)", [(l["subtipo"], l["hecho"], l["causa"]) for l in r["lineas"] if l["cuenta"]], [("almacen", "OBX", "escritura")])
    # DiagnosticReport: result por pertenencia resuelta (L-ORU-12), PLAC/FILL por papel, period
    alm_r = json.loads(json.dumps(alm))
    rec_dr = json.loads(alm_r["informes"][0]["recursos"][0]["crudo"], parse_float=str)
    mira("el DR sintético referencia Observation/<id> del almacén", rec_dr["result"], [{"reference": "Observation/101"}])
    rec_dr["result"] = []
    alm_r["informes"][0]["recursos"][0]["crudo"] = json.dumps(rec_dr)
    r = comparar(alm_r, esp, esp, "AA")
    mira("result vacío -> exactamente una línea fidelidad/almacen hecho OBX (R7)", [(l["hecho"], l["que"]) for l in r["lineas"] if l["cuenta"]],
         [("OBX", "ALM OBR 1 (24323-8) result: esperado ['ORU-X#1.1'], observado []")])
    rec_dr["result"] = [{"reference": "Observation/777"}]
    alm_r["informes"][0]["recursos"][0]["crudo"] = json.dumps(rec_dr)
    r = comparar(alm_r, esp, esp, "AA")
    mira("result a un id fuera de lo leído -> se anota sin seguirlo (L-ORU-12)", any("fuera del almacén leído" in l["que"] for l in r["lineas"] if l["cuenta"]), True)
    rec_dr = json.loads(alm["informes"][0]["recursos"][0]["crudo"], parse_float=str)
    rec_dr["identifier"] = [rec_dr["identifier"][2], rec_dr["identifier"][0], rec_dr["identifier"][1]]
    alm_r["informes"][0]["recursos"][0]["crudo"] = json.dumps(rec_dr)
    mira("identifiers del DR en otro orden -> nada (por papel, DV-ORU11-5)", [l for l in comparar(alm_r, esp, esp, "AA")["lineas"] if l["cuenta"]], [])
    plac = next(x for x in rec_dr["identifier"] if "type" in x and x["type"]["coding"][0]["code"] == "PLAC")
    plac["value"] = "PL-9"
    alm_r["informes"][0]["recursos"][0]["crudo"] = json.dumps(rec_dr)
    mira("control: PLAC con otro value -> OBR-2", [l["hecho"] for l in comparar(alm_r, esp, esp, "AA")["lineas"] if l["cuenta"]], ["OBR-2"])
    plac["value"] = "PL-1"
    rec_dr["identifier"] = [x for x in rec_dr["identifier"] if "type" not in x or x["type"]["coding"][0]["code"] != "FILL"]
    alm_r["informes"][0]["recursos"][0]["crudo"] = json.dumps(rec_dr)
    mira("sin FILL -> OBR-3 <ausente>", [(l["hecho"], AUSENTE in l["que"]) for l in comparar(alm_r, esp, esp, "AA")["lineas"] if l["cuenta"]], [("OBR-3", True), ("OBR-3", True)])
    rec_dr = json.loads(alm["informes"][0]["recursos"][0]["crudo"], parse_float=str)
    rec_dr["effectiveDateTime"] = rec_dr["effectivePeriod"]["start"]
    alm_r["informes"][0]["recursos"][0]["crudo"] = json.dumps(rec_dr)
    r = comparar(alm_r, esp, esp, "AA")
    mira("effectiveDateTime además de effectivePeriod -> OBR-7 «esperado <ausente>»", [(l["hecho"], l["que"].split(": ")[1][:18]) for l in r["lineas"] if l["cuenta"]], [("OBR-7", "esperado <ausente>")])
    esp_sf = json.loads(json.dumps(esp))
    esp_sf["informes"][0]["EfectivoFin"] = ""
    alm_sf = almacen_sintetico(esp_sf)
    rec_sf = json.loads(alm_sf["informes"][0]["recursos"][0]["crudo"], parse_float=str)
    mira("sin EfectivoFin -> effectiveDateTime y sin effectivePeriod", ("effectiveDateTime" in rec_sf, "effectivePeriod" in rec_sf), (True, False))
    mira("DR sin EfectivoFin contra sí mismo -> nada", [l for l in comparar(alm_sf, esp_sf, esp_sf, "AA")["lineas"] if l["cuenta"]], [])
    # sin PID [S60]: sin subject; con subject -> PID-3
    esp_sp = json.loads(json.dumps(esp))
    esp_sp["cabecera"]["PacienteId"] = ""
    alm_sp = almacen_sintetico(esp_sp)
    mira("PacienteId vacío -> recurso sin subject [S60]", "subject" in json.loads(alm_sp["observaciones"][0]["recursos"][0]["crudo"]), False)
    mira("control: subject presente donde no se esperaba -> PID-3", [l["hecho"] for l in comparar(alm, esp_sp, esp_sp, "AA")["lineas"] if l["cuenta"]], ["PID-3", "PID-3", "PID-3", "PID-3"])
    # tabla y hecho
    mira("hecho_almacen cubre las rutas de la tabla", [hecho_almacen("Observation", r_) for r_ in ("status", "code.coding[1].code", "valueQuantity.value", "valueQuantity.unit", "valueRange.low.value", "valueRange.low.unit", "valueRatio.numerator.comparator", "interpretation[1].coding[1].code", "referenceRange[1].text", "effectiveDateTime", "subject.identifier.value", "identifier.propio[1].value")]
         + [hecho_almacen("DiagnosticReport", r_) for r_ in ("identifier.PLAC[1].value", "identifier.FILL[1].type_system", "identifier.propio[1].value", "status", "code.coding[2].display", "effectivePeriod.end", "effectivePeriod.start", "effectiveDateTime", "issued", "result")],
         ["OBX-11", "OBX-3", "OBX-5", "OBX-6", "OBX-5", "OBX-6", "OBX-5", "OBX-8", "OBX-7", "OBX-14", "PID-3", "OBX", "OBR-2", "OBR-3", "OBR", "OBR-25", "OBR-4", "OBR-8", "OBR-7", "OBR-7", "OBR-22", "OBX"])
    mira("TABLA: toda fila cita algo y su hecho es un SEG-n, OBX/OBR o —", all(f["citas"] and re.match(r"^(OB[XR](-\d+)?( / OB[XR]-\d+)?|PID-3|—)$", f["hecho"]) for f in TABLA), True)
    print("AUTOPRUEBA DE almacen_oru: " + ("TODO BIEN (%d comprobaciones)" % n_ok[0] if not mal else "FALLAN %d" % len(mal)))
    return 1 if mal else 0


if __name__ == "__main__":
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
    print(__doc__)
