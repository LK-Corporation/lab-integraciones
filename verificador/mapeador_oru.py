#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mapeador de referencia ORU (diseno-oru-fable.md §2, §3 y §5.2): calcula el canónico que DEBERÍA registrar el circuito
LABORU (PE `oru_fhir`) a partir de un ORU^R01 y lo compara con el que salió (`sesiones[].canonico_oru`).

Mismas reglas de construcción que mapeador_referencia.py (REGLA-mapeador.md): determinista; ninguna regla menciona un
operador ni un caso; cada regla cita contrato [C-ORU] (§2 del diseño), estándar [E2]/[E2A]/[E7] (estandar/ch02.md,
ch02a.md, ch07.md) o mapeo oficial [M] (ConceptMap de v2mappings/package + elemento); donde callan, S-ORU (S57-S66 en
decisiones_s57_s66.md), D-ORU (declarado), AMB-ORU (ambigüedad anotada). Reutiliza de mapeador_referencia la lectura del
cable (mensajes, trama, Msg.desescapa §2.7, descodificar S9, control_en S10, version_id/posterior_a_25 S19/S22) y la
regla de PID-3 (MR.esperado :422-426).

Canónico esperado por mensaje (§2): {"cabecera": {...}, "informes": [...], "observaciones": [...]}.
  cabecera: MsgControlId SendingApp SendingFacility MsgEvent ProcessingId PacienteId NumInformes NumObservaciones
            NumObxEspecimen NumNte Truncado
  informe (uno por OBR del primer PATIENT_RESULT, i = posición en el cable): Orden Placer Filler CodigoCode CodigoDisplay
            CodigoSistema CodigoAltCode CodigoAltDisplay CodigoAltSistema EstadoCrudo Estado Efectivo EfectivoFin Emitido NumObx
  observación (una por OBX del grupo OBSERVATION, j = posición global): Orden OrdenEnInforme Informe SetId Tipo CodigoCode
            CodigoDisplay CodigoSistema CodigoAltCode CodigoAltDisplay CodigoAltSistema SubId ValorTipo ValorNumero
            ValorComparador ValorNum2 ValorSeparador ValorTexto ValorCodigo ValorDisplay ValorSistema ValorAltCodigo
            ValorAltDisplay ValorAltSistema ValorTextoOriginal ValorFecha ValorCrudo RepeticionesPerdidas UnidadCode
            UnidadTexto UnidadSistema RangoRef Interpretacion EstadoCrudo Estado Fecha FechaOrigen Identificador
Se compara (§2 «Qué se compara»): cabecera campo a campo, recuentos (antes que nada) y, por posición (i, j), todos los
campos salvo los crudos auxiliares (SetId, Tipo, EstadoCrudo; ValorCrudo solo cuando ValorTipo = no_soportado). Un valor
esperado None no se compara (ya contado como imposible); una tupla esperada admite cualquiera de sus valores [S22].

Desviaciones declaradas en este módulo (también en CAMBIOS-O0.md):
  DV-ORU-5: la tabla 0123 (cap. 4, que no está en estandar/) se toma de los códigos y textos del ConceptMap oficial
            table-hl70123-queries-to-diagnostic-report-status (13 valores, los de v2.5); la 0078 se copia del texto ch07.md:2181-2205.
  DV-ORU-6: el truncado [S3][S46] se aplica ANTES de mapear (como hace el acuse): un OBX-11 «FF» se lee «F» con Truncado = 1
            (mapeador_referencia no trunca PID-8; aquí se sigue el acuse para que AA + canónico coincidan). OBX-2 (LEN 2 en
            v2.5) NO se trunca: solo decide el tipo y v2.6 lo amplía a 3 («CWE», tolerado por S22); el PE oru_fhir tampoco.
  DV-ORU-7 (corregida en O1 por el oráculo N-versión, 4-oct): NumNte cuenta TODOS los NTE del PATIENT_RESULT consumido (L-ORU-4:
            ninguno viaja en v1 y nada queda en silencio; B23 da 3; los de un PATIENT_RESULT extra no, AMB-ORU-5, como el circuito); Unidad* de OBX-6 SOLO cuando el valor es quantity, range o ratio
            (O5/O6: [M] OBX-6 -> valueQuantity IF OBX-2 IN (NA, NM) y ramas SN); con string, código o fecha, vacía (B09).

Uso: python3 mapeador_oru.py --autoprueba
"""
import calendar
import re
import sys

import estructuras_hl7 as EH
import mapeador_referencia as MR

PE_POR_OMISION = "oru_fhir"
ZONA_POR_OMISION = "+01:00"                         # [S66] zona fija del emisor, salvo que el PE declare otra
# --- tablas [E7] / [M]
T0085 = dict(EH.TABLAS["0085"])                     # [E7] ch07.md:2231 (leída del texto, estructuras_25.json)
T0125 = dict(EH.TABLAS["0125"])                     # [E7] ch07.md:1865-1895
T0078 = {"L": "Below low normal", "H": "Above high normal", "LL": "Below lower panic limits", "HH": "Above upper panic limits",
         "<": "Below absolute low-off instrument scale", ">": "Above absolute high-off instrument scale",
         "N": "Normal (applies to non-numeric results)", "A": "Abnormal (applies to non-numeric results)",
         "AA": "Very abnormal (applies to non-numeric units, analogous to panic limits for numeric units)",
         "U": "Significant change up", "D": "Significant change down", "B": "Better--use when direction not relevant",
         "W": "Worse--use when direction not relevant", "S": "Susceptible. Indicates for microbiology susceptibilities only.",
         "R": "Resistant. Indicates for microbiology susceptibilities only.", "I": "Intermediate. Indicates for microbiology susceptibilities only.",
         "MS": "Moderately susceptible. Indicates for microbiology susceptibilities only.",
         "VS": "Very susceptible. Indicates for microbiology susceptibilities only."}   # [E7] ch07.md:2181-2205 (user-defined)
T0123 = {"O": "Order received; specimen not yet received", "I": "No results available; specimen received, procedure incomplete",
         "S": "No results available; procedure scheduled, but not done", "P": "Preliminary", "C": "Corrected, final",
         "R": "Results stored; not yet verified", "F": "Final results", "X": "No results available; Order canceled",
         "A": "Some, but not all, results available", "Y": "No order on record for this test", "Z": "No record of this patient",
         "M": "Corrected, not final", "N": "Procedure completed, results pending"}     # [M] ConceptMap-table-hl70123 (DV-ORU-5)
# [M] ConceptMap-table-hl70085-to-observation-status (F, P, C, D, W, X equivalent; B, I, N, O, R, S, U, V unmatched)
MAPEO_0085 = {"F": "final", "P": "preliminary", "C": "corrected", "D": "entered-in-error", "W": "entered-in-error", "X": "cancelled"}
MAPEO_0085_SITIO = {"I": "registered", "O": "registered", "R": "preliminary", "S": "preliminary", "U": "final", "N": "final"}  # [S62]
# [M] ConceptMap-table-hl70123-queries-to-diagnostic-report-status (A, Y, Z, M, N unmatched)
MAPEO_0123 = {"O": "registered", "I": "registered", "S": "registered", "P": "preliminary", "C": "corrected", "R": "partial",
              "F": "final", "X": "cancelled"}
MAPEO_0123_SITIO = {"A": "unknown", "Y": "unknown", "Z": "unknown", "M": "unknown", "N": "unknown", "": "unknown"}    # [S64]
OBSERVATION_STATUS = ("registered", "preliminary", "final", "amended", "corrected", "cancelled", "entered-in-error", "unknown")
DIAGNOSTIC_REPORT_STATUS = ("registered", "partial", "preliminary", "final", "amended", "corrected", "appended", "cancelled",
                            "entered-in-error", "unknown")
# [S61] CE.3/CWE.3 -> Coding.system (§3.4): lista cerrada del sitio; HL7nnnn -> v2-nnnn; otro -> urn:lab:integraciones:cs:<valor>
URIS = {"LN": "http://loinc.org", "SCT": "http://snomed.info/sct", "SNM": "http://snomed.info/sct", "SNM3": "http://snomed.info/sct",
        "UCUM": "http://unitsofmeasure.org", "ISO+": "http://unitsofmeasure.org", "I9": "http://hl7.org/fhir/sid/icd-9-cm",
        "I9C": "http://hl7.org/fhir/sid/icd-9-cm", "I10": "http://hl7.org/fhir/sid/icd-10"}
URI_OTRO = "urn:lab:integraciones:cs:"
SISTEMA_OBS = "urn:lab:integraciones:obs"
TIPOS_V1 = ("NM", "SN", "ST", "TX", "FT", "CE", "DT", "TM", "TS")      # §1.2; CWE/CNE/IS por [S22] en > 2.5
TIPOS_S22 = ("CWE", "CNE", "IS")
TOPE_OBX5 = 32000                                                      # D-ORU-4
# O17 longitudes [E7] tabla OBX ch07.md:1826-1850, OBR :1384-1437; PID-3 [E3]; MSH por MR.long_max()
LONG_ORU = {("OBX", 3): 250, ("OBX", 4): 20, ("OBX", 5): TOPE_OBX5, ("OBX", 6): 250, ("OBX", 7): 60, ("OBX", 8): 5,
            ("OBX", 11): 1, ("OBX", 14): 26, ("OBR", 2): 22, ("OBR", 3): 22, ("OBR", 4): 250, ("OBR", 7): 26, ("OBR", 8): 26,
            ("OBR", 22): 26, ("OBR", 25): 1, ("PID", 3): 250}
CAMPOS_CABECERA = ("MsgControlId", "SendingApp", "SendingFacility", "MsgEvent", "ProcessingId", "PacienteId", "NumInformes",
                   "NumObservaciones", "NumObxEspecimen", "NumNte", "Truncado")
CAMPOS_INFORME = ("Orden", "Placer", "Filler", "CodigoCode", "CodigoDisplay", "CodigoSistema", "CodigoAltCode", "CodigoAltDisplay",
                  "CodigoAltSistema", "Estado", "Efectivo", "EfectivoFin", "Emitido", "NumObx")
AUX_INFORME = ("EstadoCrudo",)
CAMPOS_OBSERVACION = ("Orden", "OrdenEnInforme", "Informe", "CodigoCode", "CodigoDisplay", "CodigoSistema", "CodigoAltCode",
                      "CodigoAltDisplay", "CodigoAltSistema", "SubId", "ValorTipo", "ValorNumero", "ValorComparador", "ValorNum2",
                      "ValorSeparador", "ValorTexto", "ValorCodigo", "ValorDisplay", "ValorSistema", "ValorAltCodigo", "ValorAltDisplay",
                      "ValorAltSistema", "ValorTextoOriginal", "ValorFecha", "ValorCrudo", "RepeticionesPerdidas", "UnidadCode",
                      "UnidadTexto", "UnidadSistema", "RangoRef", "Interpretacion", "Estado", "Fecha", "FechaOrigen", "Identificador")
AUX_OBSERVACION = ("SetId", "Tipo", "EstadoCrudo")
ENTEROS = {"Orden", "OrdenEnInforme", "Informe", "NumObx", "RepeticionesPerdidas", "Truncado", "NumInformes", "NumObservaciones",
           "NumObxEspecimen", "NumNte"}
# hecho (SEG-n) de cada campo canónico, para verificador.hecho_oru (§5.2)
HECHO_CABECERA = {"MsgControlId": "MSH-10", "SendingApp": "MSH-3", "SendingFacility": "MSH-4", "MsgEvent": "MSH-9", "ProcessingId": "MSH-11",
                  "PacienteId": "PID-3", "NumInformes": "OBR", "NumObservaciones": "OBX", "NumObxEspecimen": "OBX", "NumNte": "NTE",
                  "Truncado": "longitud"}
HECHO_INFORME = {"Orden": "OBR", "Placer": "OBR-2", "Filler": "OBR-3", "CodigoCode": "OBR-4", "CodigoDisplay": "OBR-4", "CodigoSistema": "OBR-4",
                 "CodigoAltCode": "OBR-4", "CodigoAltDisplay": "OBR-4", "CodigoAltSistema": "OBR-4", "Estado": "OBR-25", "EstadoCrudo": "OBR-25",
                 "Efectivo": "OBR-7", "EfectivoFin": "OBR-8", "Emitido": "OBR-22", "NumObx": "OBX"}
HECHO_OBSERVACION = {"Orden": "OBX", "OrdenEnInforme": "OBX", "Informe": "OBX", "SetId": "OBX-1", "Tipo": "OBX-2", "SubId": "OBX-4",
                     "RepeticionesPerdidas": "OBX-5", "UnidadCode": "OBX-6", "UnidadTexto": "OBX-6", "UnidadSistema": "OBX-6", "RangoRef": "OBX-7",
                     "Interpretacion": "OBX-8", "Estado": "OBX-11", "EstadoCrudo": "OBX-11", "Fecha": "OBX-14", "FechaOrigen": "OBX-14",
                     "Identificador": "OBX"}
for _c in CAMPOS_OBSERVACION:
    if _c.startswith("Codigo"):
        HECHO_OBSERVACION[_c] = "OBX-3"
    elif _c.startswith("Valor"):
        HECHO_OBSERVACION[_c] = "OBX-5"


def zona_de(pe):
    """Zona fija del emisor declarada en el PE [S66]; por omisión +01:00. Admite nombre, dict o None."""
    if isinstance(pe, dict):
        return pe.get("zona_emisor") or ZONA_POR_OMISION
    try:
        import puntos_entrada as PE
        return PE.PUNTOS.get(pe or PE_POR_OMISION, {}).get("zona_emisor") or ZONA_POR_OMISION
    except ImportError:                                           # mapeador solo
        return ZONA_POR_OMISION


# ---------------------------------------------------------------------------- tipos de dato [E2A]
NM_RE = re.compile(r"^([+-]?)(\d+)?(?:\.(\d*))?$")                     # O4 / AMB-ORU-3: «5.» y «.5» se aceptan


def numero(nm):
    """O4 [E2A §2.A.47 NM] -> (forma canónica D-ORU-2 o None, problema o None). Sin «+», sin ceros iniciales superfluos
    («01.20» -> «1.20», «.5» -> «0.5», «5.» -> «5»); ceros finales CONSERVADOS («1.20» ≠ «1.2», precisión FHIR decimal)."""
    v = nm or ""
    m = NM_RE.match(v)
    if not m or (m.group(2) is None and not m.group(3)):
        return None, "%r no es un NM válido" % nm
    signo, ent, frac = m.group(1), m.group(2) or "0", m.group(3)
    ent = ent.lstrip("0") or "0"
    return ("-" if signo == "-" else "") + ent + ("." + frac if frac else ""), None


DTM_RE = MR.DTM_RE                                                    # N1: UNA sola gramática DTM, en mapeador_referencia
TM_RE = re.compile(r"^(\d{2})(\d{2})?(\d{2})?(\.\d{1,4})?([+-]\d{4})?$")                        # [E2A TM]
_partes_dtm = MR.partes_dtm
zona_valida = MR.zona_valida


def fecha_hora(dtm, zona=ZONA_POR_OMISION, c="^"):
    """§3.5 DTM -> dateTime FHIR con la precisión del origen; con hora, FHIR exige minutos, segundos y zona: HH -> HH:00:00
    (D-ORU-6, ch02a.md:1780 «HHMM = 0000 representa medianoche»); fracción conservada; zona ±ZZZZ -> ±HH:MM; sin zona ->
    la del emisor [S66] (ch02a.md:1780 «defaults to that of the local time zone of the sender»). -> (valor, problema)."""
    v = (dtm or "").split(c)[0].strip()                              # A4: componente 1 según MSH-2
    if not v:
        return "", None
    p, prob = _partes_dtm(v)
    if prob:
        return None, prob
    y, mo, d, hh, mi, ss, fr, z = p
    iso = y + ("-" + mo if mo else "") + ("-" + d if d else "")
    if not hh:
        return iso, None
    tz = ("%s%s:%s" % (z[0], z[1:3], z[3:5])) if z else zona
    return "%sT%s:%s:%s%s%s" % (iso, hh, mi or "00", ss or "00", fr or "", tz), None


def instante(dtm, zona=ZONA_POR_OMISION, c="^"):
    """R6 `instant` exige segundos y zona: con precisión >= segundo -> como fecha_hora; con menos -> "" (D-ORU-5: no se
    inventan segundos). -> (valor, problema, omitido_por_precision)."""
    v = (dtm or "").split(c)[0].strip()                              # A4: componente 1 según MSH-2
    if not v:
        return "", None, False
    p, prob = _partes_dtm(v)
    if prob:
        return None, prob, False
    if not p[5]:
        return "", None, True
    return fecha_hora(v, zona)[0], None, False


def hora(tm, c="^"):
    """O9 TM HH[MM[SS[.S[S[S[S]]]]]][+/-ZZZZ] -> time FHIR HH:MM:SS[.f] (sin zona: FHIR time no la lleva; se completa con
    ceros como D-ORU-6). -> (valor, problema)."""
    v = (tm or "").split(c)[0].strip()                               # A4
    if not v:
        return "", None
    m = TM_RE.match(v)
    if not m:
        return None, "%r no es un TM de v2.5" % tm
    hh, mi, ss, fr, z = m.groups()
    if int(hh) > 23 or mi and int(mi) > 59 or ss and int(ss) > 59:
        return None, "%r: hora imposible" % tm
    if fr and not ss:                                                 # A2: [E2A TM] «SS[.S[S[S[S]]]]»
        return None, "%r: fracción sin segundos" % tm
    if z and not zona_valida(z):                                      # A3
        return None, "%r: zona imposible" % tm
    return "%s:%s:%s%s" % (hh, mi or "00", ss or "00", fr or ""), None


def fecha_dt(dt, c="^"):
    """O9 DT YYYY[MM[DD]] -> date FHIR. -> (valor, problema)."""
    v = (dt or "").split(c)[0].strip()                               # A4
    if not v:
        return "", None
    if not re.fullmatch(r"\d{4}(\d{2}(\d{2})?)?", v):
        return None, "%r no es un DT de v2.5" % dt
    return fecha_hora(v)


COMPARADORES = (">", "<", ">=", "<=", "=", "<>")                       # [E2A §2.A.70.1] ch02a.md:3790
SEPARADORES = ("-", "+", "/", ".", ":")                               # [E2A §2.A.70.3] ch02a.md:3796


def valor_valido(tipo, rep, c="^"):
    """DV-ORU-2 (P5 `valor_por_tipo` del acuse): ¿la repetición `rep` de OBX-5 tiene la forma de su OBX-2?
    -> True | False | None (tipo que no se juzga). NM ampliado AMB-ORU-3; SN por componentes; TS/DT/TM por forma."""
    t = (tipo or "").upper()
    if all(ch.isspace() or ch == c for ch in rep):                    # AMB-ORU-9 (Jev): una repetición vacía no se juzga
        return None
    if t == "NM":
        return c not in rep and numero(rep)[0] is not None
    if t == "SN":
        comp = (rep.split(c) + ["", "", "", ""])[:4]
        return (comp[0] in COMPARADORES + ("",) and (comp[1] == "" or numero(comp[1])[0] is not None)
                and comp[2] in SEPARADORES + ("",) and (comp[3] == "" or numero(comp[3])[0] is not None)
                and (comp[1] != "" or comp[3] != "") and not (comp[1] and comp[3] and not comp[2]))    # ch02a.md:3783
    if t in ("TS", "DTM"):
        return fecha_hora(rep.split(c)[0])[1] is None
    if t == "DT":
        return fecha_dt(rep.split(c)[0])[1] is None
    if t == "TM":
        return hora(rep.split(c)[0])[1] is None
    return None


# ---------------------------------------------------------------------------- codificaciones [M] [S61]
def uri(cs):
    """§3.4 [S61]: nombre de sistema (tabla 0396, ch02a.md:957) -> uri; vacío -> ""; HL7nnnn -> v2-nnnn; otro -> urn del sitio."""
    cs = cs or ""
    if cs == "":
        return ""
    if cs in URIS:
        return URIS[cs]
    m = re.fullmatch(r"HL7(\d{4})", cs)
    if m:
        return "http://terminology.hl7.org/CodeSystem/v2-" + m.group(1)
    return URI_OTRO + cs


def codigo(m, campo, prefijo="Codigo"):
    """O1/R3 [M] ConceptMap-datatype-ce-to-codeableconcept: CE.1 -> coding[1].code, CE.2 -> display, CE.3 -> system (uri §3.4),
    CE.4/.5/.6 -> coding[2]. Desescapado §2.7. «^texto» (solo texto, ch07.md:2039) -> display sin code (AMB-ORU-4)."""
    c = (campo.split(m.c) + [""] * 6)[:6]
    d = {prefijo + "Code": m.desescapa(c[0]), prefijo + "Display": m.desescapa(c[1]), prefijo + "Sistema": uri(m.desescapa(c[2])),
         prefijo + "AltCode": m.desescapa(c[3]), prefijo + "AltDisplay": m.desescapa(c[4]), prefijo + "AltSistema": uri(m.desescapa(c[5]))}
    return d


def unidad(m, campo):
    """O5 [M] ConceptMap-datatype-cwe-to-quantity: CWE.2 -> unit; CWE.1 -> unit si CWE.2 vacío; CWE.1 -> code y CWE.3 -> system
    solo si .1 y .3 valorados; UCUM/ISO+ -> http://unitsofmeasure.org (§3.4). Vacío -> sin unit."""
    c = (campo.split(m.c) + ["", "", ""])[:3]
    c1, c2, c3 = m.desescapa(c[0]), m.desescapa(c[1]), m.desescapa(c[2])
    return {"UnidadTexto": c2 if c2 else c1, "UnidadCode": c1 if (c1 and c3) else "", "UnidadSistema": uri(c3) if (c1 and c3) else ""}


def estado_0085(c):
    """O12: tabla 0085 -> Observation.status: oficial [M] o del sitio [S62]; None si no está."""
    return MAPEO_0085.get(c) or MAPEO_0085_SITIO.get(c)


def estado_0123(c):
    """R4: tabla 0123 -> DiagnosticReport.status: oficial [M]; sin destino o vacío -> unknown [S64]; None si no está."""
    return MAPEO_0123.get(c) or MAPEO_0123_SITIO.get(c)


# ---------------------------------------------------------------------------- truncado [S3][S46] (DV-ORU-6)
def _long_max():
    d = dict(MR.long_max())                                            # MSH y PID de v2.5 (+ perfil del sitio, H10)
    d.update(LONG_ORU)
    return d


def _truncar(m):
    """Recorta cada repetición de los campos consumidos que excede su LEN. -> (Msg truncado, hubo_truncado)."""
    segs, hubo = [], False
    lm = _long_max()
    for s in m.segs:
        partes = s.split(m.f)
        nombre = partes[0]
        for (sg, n), mx in lm.items():
            if sg != nombre:
                continue
            i = n - 1 if sg == "MSH" else n
            if i < len(partes) and (sg != "MSH" or n > 2):
                reps = partes[i].split(m.r)
                nuevas = [r[:mx] for r in reps]
                if nuevas != reps:
                    hubo = True
                    partes[i] = m.r.join(nuevas)
        segs.append(m.f.join(partes))
    return MR.Msg(segs, m.descodificados, m.marco, m.no_ascii), hubo


# ---------------------------------------------------------------------------- agrupación §3.1
def agrupar(m):
    """Recorre el cable con la gramática ORU_R01 (ch07.md:712-745): cada OBR abre una copia de ORDER_OBSERVATION; los OBX que
    le siguen son su OBSERVATION; los OBX tras un SPM (SPECIMEN) no se consumen (L-ORU-5); un OBX antes del primer OBR se
    ignora (S45); un segundo PID abre otro PATIENT_RESULT, que v1 no consume (AMB-ORU-5)."""
    out = {"pid": None, "informes": [], "obx_especimen": 0, "nte": 0, "obx_sueltos": 0, "patient_result_extra": 0}
    estado, consumiendo, ultimo_obx = "antes", True, False
    for s in m.segs[1:]:
        nombre = s.split(m.f)[0]
        if nombre == "PID":
            if out["pid"] is None and not out["informes"]:
                out["pid"] = s
            else:
                out["patient_result_extra"] += 1
                consumiendo = False
            continue
        if not consumiendo:
            continue
        if nombre == "OBR":
            out["informes"].append({"obr": s, "obx": []})
            estado, ultimo_obx = "obs", False
        elif nombre == "SPM" and out["informes"]:
            estado, ultimo_obx = "spm", False
        elif nombre == "OBX":
            if not out["informes"]:
                out["obx_sueltos"] += 1
            elif estado == "spm":
                out["obx_especimen"] += 1
            else:
                out["informes"][-1]["obx"].append(s)
                ultimo_obx = True
        elif nombre == "NTE":
            out["nte"] += 1        # L-ORU-4 «NTE no viaja (se cuenta)», §1 «nada en silencio»: TODOS los NTE del PATIENT_RESULT consumido (adjudicación O1, B23; AMB-ORU-5)
        else:
            ultimo_obx = False
    return out


# ---------------------------------------------------------------------------- el canónico esperado
def _control(m, v):
    return MR.control_en(m.desescapa(v))


def esperado_mensaje(m, pe=None):
    """-> (canónico esperado, imposibles aceptados, avisos de estructura, tolerancias y notas [etiquetadas])."""
    zona = zona_de(pe)
    msh0 = m.segs[0]
    m, truncado = _truncar(m)                                        # O17 + [S46] (DV-ORU-6)
    msh = m.segs[0]
    imp, est, tol = [], [], []
    ver = m.campo(msh, 12).split(m.c)[0]
    posterior = MR.posterior_a_25(ver)                               # [S22]
    g = agrupar(m)
    cab = {}
    # --- cabecera [C-ORU] (los cuatro del eco, como PatientRequest)
    cab["MsgControlId"] = m.campo(msh, 10)
    cab["SendingApp"] = m.campo(msh, 3).split(m.c)[0]
    cab["SendingFacility"] = m.campo(msh, 4).split(m.c)[0]
    t9 = m.campo(msh, 9).split(m.c)
    cab["MsgEvent"] = t9[1] if len(t9) > 1 else ""
    cab["ProcessingId"] = m.campo(msh, 11).split(m.c)[0]
    if [x.upper() for x in t9[:2]] != ["ORU", "R01"]:                # [C-ORU] solo ORU^R01 (Rule.Oru, §4.3)
        est.append("MSH-9 %r no es ORU^R01 y se aceptó" % m.campo(msh, 9))
    # [S58] PacienteId <- PID-3: la repetición con PID-3.5 = MR; si ninguna, la primera no vacía; todas [V] (MR.esperado :422-426)
    pid = g["pid"]
    if pid is None:
        cab["PacienteId"] = ""
        tol.append("[S60] ORU sin PID (PATIENT opcional, ch07.md:717): se acepta y se guarda sin subject (PacienteId vacío)")
    else:
        reps = m.campo(pid, 3).split(m.r)
        comp = [r.split(m.c) for r in reps]
        elegida = next((c for c in comp if len(c) > 4 and c[4] == "MR"), None) or next((c for c in comp if c[0]), None)
        cab["PacienteId"] = m.desescapa(elegida[0]) if elegida else ""
    cab["NumInformes"] = len(g["informes"])
    cab["NumObservaciones"] = sum(len(i["obx"]) for i in g["informes"])
    cab["NumObxEspecimen"] = g["obx_especimen"]
    cab["NumNte"] = g["nte"]
    cab["Truncado"] = 1 if truncado else 0
    if g["obx_sueltos"]:
        tol.append("[S45] %d OBX antes del primer OBR: fuera de posición, ignorado; sin Observation esperada" % g["obx_sueltos"])
    if g["obx_especimen"]:
        tol.append("[L-ORU-5] %d OBX bajo SPM (SPECIMEN) no se escriben; se cuentan en NumObxEspecimen" % g["obx_especimen"])
    if g["nte"]:
        tol.append("[L-ORU-4] %d NTE no viajan a FHIR (Observation.note fuera de v1); se cuentan en NumNte" % g["nte"])
    if g["patient_result_extra"]:
        tol.append("[AMB-ORU-5] %d PATIENT_RESULT adicional(es) (ch07.md:716): v1 consume solo el primero; sus OBR/OBX no se esperan"
                   % g["patient_result_extra"])
    # [S10] control en los campos consumidos de la cabecera
    for donde, campos, vals in (("MSH-10", ["MsgControlId"], [cab["MsgControlId"]]), ("MSH-3", ["SendingApp"], [cab["SendingApp"]]),
                                ("MSH-4", ["SendingFacility"], [cab["SendingFacility"]]), ("MSH-9", ["MsgEvent"], [m.campo(msh, 9)]),
                                ("MSH-11", ["ProcessingId"], [cab["ProcessingId"]]), ("PID-3", ["PacienteId"], [cab["PacienteId"]])):
        c = next((MR.control_en(v) for v in vals if isinstance(v, str) and MR.control_en(v) is not None), None)
        if c is not None:
            imp.append("%s contiene un carácter de control U+%04X y se aceptó" % (donde, c))
            for campo in campos:
                cab[campo] = None
    informes, observaciones = [], []
    j_global = 0
    for i, inf in enumerate(g["informes"], 1):
        obr = inf["obr"]
        pre = "OBR %d: " % i
        x = {"Orden": i}
        # R1/R2 [M] OBR-2 -> identifier[1] (PLAC), OBR-3 -> identifier[2] (FILL); [E7] ch07.md:1447-1459
        x["Placer"] = m.desescapa(m.campo(obr, 2).split(m.c)[0])
        x["Filler"] = m.desescapa(m.campo(obr, 3).split(m.c)[0])
        x.update(codigo(m, m.campo(obr, 4)))                          # R3 [M] OBR-4 -> code (como O1); [E7] ch07.md:1389,1477
        # R4 [M] OBR-25 -> status IF VALUED; [E7] ch07.md:1410,1623-1629; vacío o sin destino -> unknown [S64]
        c25 = m.campo(obr, 25).split(m.c)[0]
        x["EstadoCrudo"] = c25
        if c25 == "" or c25 in T0123:
            x["Estado"] = estado_0123(c25)
            if c25 == "":
                tol.append("[S64] %sOBR-25 vacío: DiagnosticReport.status = unknown (no se infiere de los OBX)" % pre)
            elif c25 in MAPEO_0123_SITIO:
                tol.append("[S64] %sOBR-25 %r sin destino en el mapeo oficial: status = unknown" % (pre, c25))
        elif c25.upper() in T0123:                                    # [S4]
            x["Estado"] = estado_0123(c25.upper())
            tol.append("[S4] %sOBR-25 %r en minúscula: se tolera como %r" % (pre, c25, c25.upper()))
        elif posterior:                                               # [S22]
            x["Estado"] = DIAGNOSTIC_REPORT_STATUS + ("",)
            tol.append("[S22] %sOBR-25 %r fuera de la 0123 de v2.5 en un mensaje %s: sin destino en el mapeo oficial; solo se "
                       "comprueba que Estado sea un código de DiagnosticReportStatus" % (pre, c25, ver))
        else:
            x["Estado"] = None
            imp.append("%sOBR-25 %r no está en la tabla 0123 y se aceptó" % (pre, c25))
        # R5 [M] OBR-7 -> effectiveDateTime IF OBR-8 NOT VALUED / effectivePeriod.start; OBR-8 -> effectivePeriod.end; §3.5
        for n, campo in ((7, "Efectivo"), (8, "EfectivoFin")):
            v, prob = fecha_hora(m.campo(obr, n), zona, m.c)
            x[campo] = v
            if prob:
                imp.append("%sOBR-%d %s y se aceptó" % (pre, n, prob))
        if m.campo(obr, 7).split(m.c)[0] == "":
            tol.append("[L-MT6] %sOBR-7 vacío: campo C («must be filled in» en informes, ch07.md:1487); se anota, no es 101" % pre)
        # R6 [M] OBR-22 -> issued (instant: segundos y zona; D-ORU-5); [E7] ch07.md:1407,1609
        v, prob, omitido = instante(m.campo(obr, 22), zona, m.c)
        x["Emitido"] = v
        if prob:
            imp.append("%sOBR-22 %s y se aceptó" % (pre, prob))
        if omitido:
            tol.append("[D-ORU-5] %sOBR-22 %r sin segundos: issued (instant) se omite, Emitido vacío" % (pre, m.campo(obr, 22)))
        # [S10] en los campos consumidos del OBR
        for n, campos in ((2, ["Placer"]), (3, ["Filler"]), (4, ["CodigoCode", "CodigoDisplay", "CodigoSistema", "CodigoAltCode", "CodigoAltDisplay", "CodigoAltSistema"]),
                          (7, ["Efectivo"]), (8, ["EfectivoFin"]), (22, ["Emitido"]), (25, ["Estado"])):
            c = _control(m, m.campo(obr, n))
            if c is not None:
                imp.append("%sOBR-%d contiene un carácter de control U+%04X y se aceptó" % (pre, n, c))
                for campo in campos:
                    x[campo] = None
        x["NumObx"] = len(inf["obx"])
        informes.append(x)
        for jj, obx in enumerate(inf["obx"], 1):
            j_global += 1
            observaciones.append(_observacion(m, obx, i, jj, j_global, obr, cab["MsgControlId"], zona, posterior, ver, imp, tol))
    return {"cabecera": cab, "informes": informes, "observaciones": observaciones}, imp, est, tol


def _observacion(m, obx, i, jj, j, obr, msh10, zona, posterior, ver, imp, tol):
    pre = "OBX %d: " % j
    x = {"Orden": j, "OrdenEnInforme": jj, "Informe": i, "SetId": m.campo(obx, 1), "Tipo": m.campo(obx, 2).split(m.c)[0]}
    x.update(codigo(m, m.campo(obx, 3)))                              # O1 [M] OBX-3 -> code; CE.1/.2/.3/.4/.5/.6; [E7] ch07.md:1829,1905
    if x["CodigoCode"] == "" and x["CodigoDisplay"] != "":
        tol.append("[AMB-ORU-4] %sOBX-3 solo con texto («^texto», ch07.md:2039): coding[1].display sin code" % pre)
    x["SubId"] = m.desescapa(m.campo(obx, 4))                         # O2 [M] OBX-4 -> $this (Narrative-Condition); L-ORU-6
    for k in ("ValorNumero", "ValorComparador", "ValorNum2", "ValorSeparador", "ValorTexto", "ValorCodigo", "ValorDisplay",
              "ValorSistema", "ValorAltCodigo", "ValorAltDisplay", "ValorAltSistema", "ValorTextoOriginal", "ValorFecha", "ValorCrudo"):
        x[k] = ""
    x["RepeticionesPerdidas"] = 0
    # O3 OBX-2 [E7] ch07.md:1828,1857; [T0125] :1865-1895; [S22]
    tipo_crudo = x["Tipo"]
    tipo = tipo_crudo
    v5 = m.campo(obx, 5)
    reps = v5.split(m.r) if v5 != "" else []
    c11 = m.campo(obx, 11).split(m.c)[0]
    tipo_ok = True
    if tipo != "" and tipo not in T0125 and tipo.upper() in T0125:    # [S4]
        tol.append("[S4] %sOBX-2 %r en minúscula: se tolera como %r" % (pre, tipo, tipo.upper()))
        tipo = tipo.upper()
    elif tipo != "" and tipo not in T0125:
        if posterior and tipo.upper() in TIPOS_S22:
            tol.append("[S22] %sOBX-2 %r fuera de la 0125 de v2.5 en un mensaje %s: se trata como CE (valueCodeableConcept, [M])"
                       % (pre, tipo, ver))
            tipo = tipo.upper()
        elif posterior:
            tol.append("[S22] %sOBX-2 %r fuera de la 0125 de v2.5 en un mensaje %s: puede ser legal en su versión (L18); sin "
                       "value[x] en v1 (L-ORU-2)" % (pre, tipo, ver))
        else:
            imp.append("%sOBX-2 %r no está en la tabla 0125 y se aceptó" % (pre, tipo))
            tipo_ok = False
    # el valor según el tipo
    if not tipo_ok:
        x["ValorTipo"] = None
    elif not reps or all(r == "" for r in reps) or all(ch.isspace() or ch in (m.f + m.c + m.r + m.e + m.s) for ch in v5):   # B3
        # A6 (cierre de ORU, q1 antes): solo separadores y blancos = vacío, la MISMA regla que acuse_referencia._vacio
        # (§2.1.5); antes «^» con OBX-2 = SN daba imposible aquí y AA en el acuse (el circuito no podía acertar)
        x["ValorTipo"] = "sin_valor"
        if tipo == "" and c11 != "X":
            tol.append("[AMB-ORU-2] %sOBX-2 vacío con OBX-11 %r (ch07.md:1857 lo exige salvo X): sin valor, se anota" % (pre, c11))
    elif tipo == "":
        x["ValorTipo"], x["ValorCrudo"] = "no_soportado", v5          # AMB-ORU-2 / O15
        tol.append("[AMB-ORU-2] %sOBX-2 vacío con OBX-5 valorado (ch07.md:1857): no_soportado con ValorCrudo; alternativa 101" % pre)
    elif tipo == "NM":                                                # O4 [M] OBX-5 -> valueQuantity.value IF OBX-2 = NM; NM.1 -> $value
        x["ValorTipo"] = "quantity"
        val, prob = (None, "%r no es un NM válido" % reps[0]) if m.c in reps[0] else numero(reps[0])
        if prob:
            imp.append("%sOBX-5 %s y se aceptó" % (pre, prob))
            x["ValorNumero"] = None
        else:
            x["ValorNumero"] = val
        x["RepeticionesPerdidas"] = len(reps) - 1                     # O14 / L-ORU-3
    elif tipo == "SN":                                                # O6 [M] ramas SN de OBX-5; [E2A §2.A.70] ch02a.md:3773-3800
        comp = (reps[0].split(m.c) + ["", "", "", ""])[:4]
        cmpr = comp[0] if comp[0] != "" else "="
        n1, sep, n2 = comp[1], comp[2], comp[3]
        forma_mal = cmpr not in COMPARADORES or sep not in SEPARADORES + ("",) or (n1 and n2 and not sep) or not (n1 or n2)
        if cmpr == "<>" or sep == "+" or forma_mal:                   # valueString crudo
            x["ValorTipo"], x["ValorTexto"] = "string", reps[0]
            if forma_mal:
                imp.append("%sOBX-5 %r no tiene la forma SN de v2.5 y se aceptó" % (pre, reps[0]))
                x["ValorTexto"] = None
        else:
            nums = {}
            for nombre_c, nv in (("num1", n1), ("num2", n2)):
                if nv == "":
                    nums[nombre_c] = ""
                    continue
                val, prob = numero(nv)
                if prob:
                    imp.append("%sOBX-5 SN %s: %s y se aceptó" % (pre, nombre_c, prob))
                    val = None
                nums[nombre_c] = val
            if sep in (":", "/"):                                     # [M] sn-to-ratio: SN.1 -> numerator.comparator si ≠ «=»
                x["ValorTipo"] = "ratio"
                x["ValorComparador"] = cmpr if cmpr != "=" else ""
                x["ValorNumero"], x["ValorNum2"], x["ValorSeparador"] = nums["num1"], nums["num2"], sep
            elif sep == "-":                                          # [M] sn-to-range: SN.2 -> low.value, SN.4 -> high.value
                x["ValorTipo"] = "range"
                x["ValorNumero"], x["ValorNum2"], x["ValorSeparador"] = nums["num1"], nums["num2"], sep
            else:                                                     # [M] sn-to-quantity: SN.1 -> comparator (salvo «=»), SN.2 -> value
                x["ValorTipo"] = "quantity"
                x["ValorComparador"] = cmpr if cmpr != "=" else ""
                x["ValorNumero"], x["ValorSeparador"] = nums["num1"], sep
                if n2:
                    x["ValorNum2"] = nums["num2"]
        x["RepeticionesPerdidas"] = len(reps) - 1
    elif tipo in ("ST", "TX", "FT"):                                  # O7 [M] OBX-5 -> valueString IF OBX-2 IN (ST, FT, TX); [E2 §2.7]
        x["ValorTipo"] = "string"
        if tipo == "ST":
            x["ValorTexto"] = m.desescapa(reps[0])
            x["RepeticionesPerdidas"] = len(reps) - 1
        else:                                                         # D-ORU-3: repeticiones = párrafos (ch02a.md:4172) -> «\n»
            x["ValorTexto"] = "\n".join(m.desescapa(r) for r in reps)
    elif tipo in ("CE", "CWE", "CNE", "IS"):                          # O8 [M] OBX-5 -> valueCodeableConcept; ce/cwe-to-codeableconcept
        x["ValorTipo"] = "codeableconcept"
        if tipo == "IS":                                              # [M] is-to-codeableconcept: coding[1].code sin system
            x["ValorCodigo"] = m.desescapa(reps[0].split(m.c)[0])
        else:
            cc = codigo(m, reps[0], "Valor")
            x["ValorCodigo"], x["ValorDisplay"], x["ValorSistema"] = cc["ValorCode"], cc["ValorDisplay"], cc["ValorSistema"]
            x["ValorAltCodigo"], x["ValorAltDisplay"], x["ValorAltSistema"] = cc["ValorAltCode"], cc["ValorAltDisplay"], cc["ValorAltSistema"]
            if tipo == "CWE":
                c9 = (reps[0].split(m.c) + [""] * 9)[8]
                x["ValorTextoOriginal"] = m.desescapa(c9)             # [M] CWE.9 -> text
            if x["ValorCodigo"] == "" and x["ValorDisplay"] != "":
                tol.append("[AMB-ORU-4] %sOBX-5 solo con texto («^texto», ch07.md:2039): coding[1].display sin code" % pre)
        x["RepeticionesPerdidas"] = len(reps) - 1
    elif tipo in ("TS", "DT", "TM"):                                  # O9 [M] valueDateTime IF (DTM, DT); valueTime IF TM; AMB-ORU-1
        x["ValorTipo"] = "time" if tipo == "TM" else "datetime"
        f = ((lambda v: hora(v, m.c)) if tipo == "TM" else ((lambda v: fecha_dt(v, m.c)) if tipo == "DT"
                                                             else (lambda v: fecha_hora(v, zona, m.c))))
        val, prob = f(reps[0])
        if prob:
            imp.append("%sOBX-5 %s y se aceptó" % (pre, prob))
        x["ValorFecha"] = val
        x["RepeticionesPerdidas"] = len(reps) - 1
    else:                                                             # O15 L-ORU-2: tipo de la 0125 fuera de v1
        x["ValorTipo"], x["ValorCrudo"] = "no_soportado", v5
    if x.get("ValorTipo") in ("quantity", "range", "ratio"):          # O5/O6 [M] OBX-6 -> valueQuantity IF OBX-2 IN (NA, NM) y
        x.update(unidad(m, m.campo(obx, 6)))                          # ramas SN cantidad/rango/razón; con string/código/fecha no hay
    else:                                                             # unidad (adjudicación O1, B09: SN «<>» -> valueString)
        x.update({"UnidadTexto": "", "UnidadCode": "", "UnidadSistema": ""})
    x["RangoRef"] = m.desescapa(m.campo(obx, 7))                      # O10 [M] OBX-7 -> referenceRange.text (literal, sin parsear)
    inter = []                                                        # O11 [M] OBX-8 -> interpretation; ConceptMap 0078 (todos equivalent)
    for r in (m.campo(obx, 8).split(m.r) if m.campo(obx, 8) != "" else []):
        c8 = m.desescapa(r.split(m.c)[0])
        if c8 not in T0078 and c8.upper() in T0078:
            tol.append("[S4] %sOBX-8 %r en minúscula: se tolera como %r" % (pre, c8, c8.upper()))
            c8 = c8.upper()
        inter.append(c8)
    x["Interpretacion"] = ";".join(inter)
    # O12 [M] OBX-11 -> status; ConceptMap 0085; sin destino -> [S62]; [E7] ch07.md:2223-2245
    x["EstadoCrudo"] = c11
    if c11 == "":
        x["Estado"] = None                                            # 101 (R): lo juzga el acuse
    elif c11 in T0085:
        x["Estado"] = estado_0085(c11)
        if c11 in MAPEO_0085_SITIO:
            tol.append("[S62] %sOBX-11 %r sin destino en el mapeo oficial: status = %r por decisión del sitio%s"
                       % (pre, c11, x["Estado"], "; sin dataAbsentReason (L-ORU-7)" if c11 == "N" else ""))
        if c11 == "D":
            tol.append("[AMB-ORU-6] %sOBX-11 = D («Deletes the OBX record»): se escribe con status entered-in-error, no se borra nada" % pre)
    elif c11.upper() in T0085:                                        # [S4]
        x["Estado"] = estado_0085(c11.upper())
        tol.append("[S4] %sOBX-11 %r en minúscula: se tolera como %r" % (pre, c11, c11.upper()))
    elif posterior:                                                   # [S22]
        x["Estado"] = OBSERVATION_STATUS + ("",)
        tol.append("[S22] %sOBX-11 %r fuera de la 0085 de v2.5 en un mensaje %s: sin destino en el mapeo oficial; solo se "
                   "comprueba que Estado sea un código de ObservationStatus" % (pre, c11, ver))
    else:
        x["Estado"] = None
        imp.append("%sOBX-11 %r no está en la tabla 0085 y se aceptó" % (pre, c11))
    # O13 [M] OBX-14 -> effectiveDateTime; vacío -> OBR-7 del OBR padre [S63] (ch07.md:2258); ambos vacíos -> ninguna
    v14 = m.campo(obx, 14)
    if v14.split(m.c)[0] != "":
        x["Fecha"], prob = fecha_hora(v14, zona, m.c)
        x["FechaOrigen"] = "OBX-14"
        if prob:
            imp.append("%sOBX-14 %s y se aceptó" % (pre, prob))
    elif m.campo(obr, 7).split(m.c)[0] != "":
        x["Fecha"], prob = fecha_hora(m.campo(obr, 7), zona, m.c)
        x["FechaOrigen"] = "OBR-7"
        if prob:
            x["Fecha"] = None                                         # ya contado en el OBR
    else:
        x["Fecha"], x["FechaOrigen"] = "", "ninguna"
    x["Identificador"] = "%s#%d.%d" % (msh10, i, jj)                  # D-ORU-1 §1.3
    # [S10] control en los campos consumidos del OBX: imposible y el campo no se compara
    for n, campos in ((3, [c for c in x if c.startswith("Codigo")]), (4, ["SubId"]), (5, [c for c in x if c.startswith("Valor") and c != "ValorTipo"]),
                      (6, ["UnidadCode", "UnidadTexto", "UnidadSistema"]), (7, ["RangoRef"]), (8, ["Interpretacion"]), (11, ["Estado"]),
                      (14, ["Fecha"])):
        c = _control(m, m.campo(obx, n))
        if c is not None:
            imp.append("%sOBX-%d contiene un carácter de control U+%04X y se aceptó" % (pre, n, c))
            for campo in campos:
                x[campo] = None
    return x


def esperado(texto, pe=None):
    """-> por mensaje del cable: (canónico esperado, imposibles, estructura, tolerancias/notas)."""
    return [esperado_mensaje(m, pe) for m in MR.mensajes(texto)]


# ---------------------------------------------------------------------------- comparación §5.2
def _igual(e, o, campo):
    if isinstance(e, tuple):
        return o in e
    if campo in ENTEROS:
        oi = int(o) if str(o).strip().lstrip("-").isdigit() else (0 if o in ("", None) else o)
        return e == oi
    return str(e) == ("" if o is None else str(o))


def _repr(v):
    return repr(v)


def _buscar(lista, claves, pos):
    """La entrada observada que casa con `claves` ({campo: valor}); si ninguna lleva esas claves, la de la posición."""
    con_claves = [o for o in lista if isinstance(o, dict) and all(k in o for k in claves)]
    if con_claves:
        for o in con_claves:
            if all(_igual(v, o.get(k), k) for k, v in claves.items()):
                return o
        return None
    return lista[pos] if pos < len(lista) and isinstance(lista[pos], dict) else None


def comparar(observado, esperado_):
    """-> (discrepancias [texto], recuentos {informes: (esperado, observado), observaciones: (...)}). Textos: «Campo: esperado X,
    observado Y» (cabecera), «OBR i (código) Campo: …», «OBX j (código) Campo: …», «Informes: esperado 2, observado 1»."""
    out = []
    can = observado if isinstance(observado, dict) else {}
    cab_o = can.get("cabecera") if isinstance(can.get("cabecera"), dict) else {}
    inf_o = can.get("informes") if isinstance(can.get("informes"), list) else []
    obs_o = can.get("observaciones") if isinstance(can.get("observaciones"), list) else []
    cab_e = esperado_["cabecera"]
    for c in CAMPOS_CABECERA:
        e, o = cab_e.get(c), cab_o.get(c)
        if e is None:
            continue                                                  # ya contado como imposible
        if c not in cab_o and e in ("", 0):
            continue                                                  # columna ausente y nada que guardar
        if not _igual(e, o, c):
            out.append("%s: esperado %r, observado %r" % (c, e, o))
    rec = {"informes": (len(esperado_["informes"]), len(inf_o)), "observaciones": (len(esperado_["observaciones"]), len(obs_o))}
    if rec["informes"][0] != rec["informes"][1]:
        out.append("Informes: esperado %d, observado %d" % rec["informes"])
    if rec["observaciones"][0] != rec["observaciones"][1]:
        out.append("Observaciones: esperado %d, observado %d" % rec["observaciones"])
    for k, x in enumerate(esperado_["informes"]):
        o = _buscar(inf_o, {"Orden": x["Orden"]}, k)
        donde = "OBR %d (%s)" % (x["Orden"], x.get("CodigoCode") or "")
        if o is None:
            if rec["informes"][0] == rec["informes"][1]:              # A1: con el recuento igual, nadie más lo diría
                out.append("%s Orden: esperado %r, no hay ninguna entrada observada con esa clave" % (donde, x["Orden"]))
            continue                                                  # con recuento distinto, el recuento ya lo dice
        for c in CAMPOS_INFORME:
            e = x.get(c)
            if e is None or (c not in o and e in ("", 0)):
                continue
            if not _igual(e, o.get(c), c):
                out.append("%s %s: esperado %r, observado %r" % (donde, c, e, o.get(c)))
    for k, x in enumerate(esperado_["observaciones"]):
        o = _buscar(obs_o, {"Informe": x["Informe"], "OrdenEnInforme": x["OrdenEnInforme"]}, k)
        if o is None:
            o = _buscar(obs_o, {"Orden": x["Orden"]}, k)
        donde = "OBX %d (%s)" % (x["Orden"], x.get("CodigoCode") or "")
        if o is None:
            if rec["observaciones"][0] == rec["observaciones"][1]:    # A1
                out.append("%s Orden: esperado %r, no hay ninguna entrada observada con esa clave" % (donde, x["Orden"]))
            continue
        for c in CAMPOS_OBSERVACION:
            if c == "ValorCrudo" and x.get("ValorTipo") != "no_soportado":
                continue
            e = x.get(c)
            if e is None or (c not in o and e in ("", 0)):
                continue
            if not _igual(e, o.get(c), c):
                out.append("%s %s: esperado %r, observado %r" % (donde, c, e, o.get(c)))
    return out, rec


def revisar(texto_mensaje, canonicos, ack, pe=None):
    """Misma forma que mapeador_referencia.revisar: -> (discrepancias, tolerancias y notas), o None si está fuera de alcance
    (MSA-1 ≠ AA o sin canónico). Las tolerancias y notas van etiquetadas ([S4], [S22], [S60], [AMB-ORU-n], [L-ORU-n]…)."""
    ms = MR.mensajes(texto_mensaje)
    am = MR.mensajes(ack or "")
    msa = am[0].segmentos("MSA") if am else []
    if not ms or not canonicos or not msa or am[0].campo(msa[0], 1) != "AA":
        return None
    out, tol = [], []
    for k, m in enumerate(ms):
        pre = "mensaje %d: " % (k + 1) if len(ms) > 1 else ""
        a_k = next((a for a in am if a.segmentos("MSA") and a.campo(a.segmentos("MSA")[0], 2) == m.campo(m.segs[0], 10)),
                   am[k] if k < len(am) else None)                    # D10: el ACK de ESTE mensaje (por MSA-2, o el posicional)
        if len(ms) > 1 and (a_k is None or not a_k.segmentos("MSA") or a_k.campo(a_k.segmentos("MSA")[0], 1) != "AA"):
            tol.append("[L24] " + pre + "su acuse no es AA: su canónico no se compara (fuera de alcance)")
            continue
        esp, imp, est, tl = esperado_mensaje(m, pe)
        out += [pre + z for z in imp] + [pre + z for z in est]
        tol += [pre + t for t in tl]
        can = canonicos[k] if k < len(canonicos) else None
        if not isinstance(can, dict):
            out.append(pre + "no hay canónico para este mensaje")
            continue
        d, _ = comparar(can, esp)
        out += [pre + z for z in d]
    # [E2 §2.9.2.2] MSA-2 devuelve el MSH-10 acusado: CADA mensaje del cable debe tener su eco (D9)
    ecos = [a.campo(z, 2) for a in am for z in a.segmentos("MSA")]
    for k, m in enumerate(ms):
        ctl = m.campo(m.segs[0], 10)
        if ctl not in ecos:
            a = am[k] if k < len(am) else None
            msa2 = a.campo(a.segmentos("MSA")[0], 2) if a is not None and a.segmentos("MSA") else None
            out.append(("mensaje %d: " % (k + 1) if len(ms) > 1 else "") + "MSA-2 %r no devuelve el MSH-10 %r" % (msa2, ctl))
    return out, tol


def hecho_de(texto):
    """Campo del hecho (SEG-n) de una línea de discrepancia/tolerancia del mapeador ORU (§5.2), o None si no es de este mapeador."""
    mt = re.match(r"^(OBX|OBR) \d+ \([^)]*\) (\w+)$", texto.split(":")[0])
    if mt:
        return (HECHO_OBSERVACION if mt.group(1) == "OBX" else HECHO_INFORME).get(mt.group(2), mt.group(1))
    campo = texto.split(":")[0]
    if campo in HECHO_CABECERA:
        return HECHO_CABECERA[campo]
    if campo == "Informes":
        return "OBR"
    if campo == "Observaciones":
        return "OBX"
    return None


# ---------------------------------------------------------------------------- autoprueba (§6 O0a: por regla, delata y control negativo)
def autoprueba():
    mal = []

    def mira(nombre, obtenido, esperado_):
        ok = obtenido == esperado_
        print(("  ok  " if ok else "  MAL ") + nombre + ("" if ok else ": %r != %r" % (obtenido, esperado_)))
        if not ok:
            mal.append(nombre)

    MSH = "MSH|^~\\&|LAB|HOSP|DEST|FAC|20230101120000||ORU^R01^ORU_R01|M1|P|%s"
    PID = "PID|1||P1^^^H^PI~X1^^^H^MR||Pérez^Ana||19800101|F"
    OBR = "OBR|1|PL1|FL1|24323-8^Panel^LN|||20230101080000|||||||||||||||20230101090000|||F"
    OBX = "OBX|1|NM|2345-7^Glucosa^LN||95|mg/dL^mg/dL^UCUM|70-110|N|||F|||20230101083000"
    ACK = "MSH|^~\\&|D|F|LAB|HOSP|t||ACK^R01^ACK|X|P|2.5\nMSA|AA|M1"

    def msg(*segs, ver="2.5"):
        return "<VT>" + "\n".join([MSH % ver] + list(segs)) + "\n<FS>"

    def esp(*segs, ver="2.5"):
        return esperado_mensaje(MR.mensajes(msg(*segs, ver=ver))[0])

    def c(texto, can):
        return revisar(texto, [can], ACK)

    def copia(e):
        import copy
        return copy.deepcopy(e)

    base = msg(PID, OBR, OBX)
    e0, imp0, est0, tol0 = esp(PID, OBR, OBX)
    ob0, in0, cab0 = e0["observaciones"][0], e0["informes"][0], e0["cabecera"]
    mira("base: sin imposibles ni estructura; control negativo (el esperado contra sí mismo)", (imp0, est0, c(base, e0)[0]), ([], [], []))
    mira("cabecera [C-ORU]", (cab0["MsgControlId"], cab0["SendingApp"], cab0["SendingFacility"], cab0["MsgEvent"], cab0["ProcessingId"],
         cab0["PacienteId"], cab0["NumInformes"], cab0["NumObservaciones"], cab0["NumObxEspecimen"], cab0["NumNte"], cab0["Truncado"]),
         ("M1", "LAB", "HOSP", "R01", "P", "X1", 1, 1, 0, 0, 0))
    mira("fuera de alcance: AR / sin canónico", (revisar(base, [e0], ACK.replace("MSA|AA", "MSA|AR")), revisar(base, [], ACK)), (None, None))
    mira("MSA-2 que no hace eco: se delata", any(z.startswith("MSA-2") for z in revisar(base, [e0], ACK.replace("MSA|AA|M1", "MSA|AA|Z"))[0]), True)
    mira("sin canónico para el mensaje", c(base, None), (["no hay canónico para este mensaje"], tol0))
    # S58 PacienteId
    mira("S58 PID-3: MR en la 2.ª repetición; PI guardado se delata", (cab0["PacienteId"], c(base, dict(copia(e0), cabecera=dict(cab0, PacienteId="P1")))[0]),
         ("X1", ["PacienteId: esperado 'X1', observado 'P1'"]))
    # S60 sin PID
    e, _, _, t = esp(OBR, OBX)
    mira("S60 sin PID: PacienteId vacío, nota [S60], correcto", (e["cabecera"]["PacienteId"], any(z.startswith("[S60]") for z in t)), ("", True))
    # O1 código
    mira("O1 OBX-3 CE: code/display/system LN", (ob0["CodigoCode"], ob0["CodigoDisplay"], ob0["CodigoSistema"]), ("2345-7", "Glucosa", "http://loinc.org"))
    e1 = esp(PID, OBR, OBX.replace("2345-7^Glucosa^LN", "2345-7^Glucosa^LN^GLU^Gluc^L"))[0]
    mira("O1 CE.4-6 -> alt; sistema L -> urn del sitio [S61]", (e1["observaciones"][0]["CodigoAltCode"], e1["observaciones"][0]["CodigoAltSistema"]),
         ("GLU", "urn:lab:integraciones:cs:L"))
    ec = copia(e0); ec["observaciones"][0]["CodigoSistema"] = "LN"
    mira("O1 sistema sin traducir a uri: se delata; traducido: nada", (len(c(base, ec)[0]), c(base, copia(e0))[0]), (1, []))
    mira("S61 uri", [uri(x) for x in ("LN", "SCT", "SNM3", "UCUM", "ISO+", "I9", "I10", "HL70078", "L", "99zzz", "")],
         ["http://loinc.org", "http://snomed.info/sct", "http://snomed.info/sct", "http://unitsofmeasure.org", "http://unitsofmeasure.org",
          "http://hl7.org/fhir/sid/icd-9-cm", "http://hl7.org/fhir/sid/icd-10", "http://terminology.hl7.org/CodeSystem/v2-0078",
          "urn:lab:integraciones:cs:L", "urn:lab:integraciones:cs:99zzz", ""])
    # O2 SubId
    e2 = esp(PID, OBR, OBX.replace("^LN||95", "^LN|1.2|95"))[0]
    ec = copia(e2); ec["observaciones"][0]["SubId"] = ""
    mira("O2 OBX-4 SubId guardado; perdido se delata", (e2["observaciones"][0]["SubId"], len(c(msg(PID, OBR, OBX.replace("^LN||95", "^LN|1.2|95")), ec)[0])), ("1.2", 1))
    # O3 tipo
    e3, imp3, _, tol3 = esp(PID, OBR, OBX.replace("|NM|", "|QQ|"))
    mira("O3 OBX-2 fuera de 0125 en 2.5: imposible, ValorTipo None", (any("tabla 0125" in z for z in imp3), e3["observaciones"][0]["ValorTipo"]), (True, None))
    e3b, imp3b, _, tol3b = esp(PID, OBR, OBX.replace("|NM|", "|CWE|").replace("||95|", "||123^Positivo^SCT^^^^^^Texto original|"), ver="2.6")
    o3b = e3b["observaciones"][0]
    mira("O3/O8 CWE en 2.6 [S22]: codeableconcept, CWE.9 -> ValorTextoOriginal, tolerancia S22",
         (imp3b, o3b["ValorTipo"], o3b["ValorCodigo"], o3b["ValorSistema"], o3b["ValorTextoOriginal"], any(z.startswith("[S22]") for z in tol3b)),
         ([], "codeableconcept", "123", "http://snomed.info/sct", "Texto original", True))
    e3c, imp3c, _, _ = esp(PID, OBR, OBX.replace("|NM|", "|CWE|"))
    mira("O3 CWE en 2.5: imposible (P5 103)", any("'CWE' no está en la tabla 0125" in z for z in imp3c), True)
    e3d, _, _, tol3d = esp(PID, OBR, OBX.replace("|NM|", "|nm|"))
    mira("O3 OBX-2 minúscula [S4]: quantity + tolerancia", (e3d["observaciones"][0]["ValorTipo"], any(z.startswith("[S4]") and "OBX-2" in z for z in tol3d)), ("quantity", True))
    e3e, _, _, tol3e = esp(PID, OBR, "OBX|1||2345-7^Glucosa^LN||||||||X")
    mira("O3 OBX-2 vacío con OBX-11 X: sin_valor, sin nota", (e3e["observaciones"][0]["ValorTipo"], [z for z in tol3e if "AMB-ORU-2" in z]), ("sin_valor", []))
    e3f, _, _, tol3f = esp(PID, OBR, "OBX|1||2345-7^Glucosa^LN||95||||||F")
    mira("O3 OBX-2 vacío con valor (AMB-ORU-2): no_soportado + crudo", (e3f["observaciones"][0]["ValorTipo"], e3f["observaciones"][0]["ValorCrudo"],
         any("AMB-ORU-2" in z for z in tol3f)), ("no_soportado", "95", True))
    # O4 NM
    mira("O4 numero: forma canónica D-ORU-2", [numero(x)[0] for x in ("95", "01.20", "-0.5", ".5", "5.", "+7", "1.20", "007", "0", "-.5")],
         ["95", "1.20", "-0.5", "0.5", "5", "7", "1.20", "7", "0", "-0.5"])
    mira("O4 numero inválido", [numero(x)[0] for x in ("1,5", "", ".", "1e5", "95 ", "95^x")], [None, None, None, None, None, None])
    mira("O4 ValorNumero 95; «1.2» por «1.20» se delata", (ob0["ValorNumero"], len(c(msg(PID, OBR, OBX.replace("||95|", "||1.20|")),
         dict(copia(e0), observaciones=[dict(ob0, ValorNumero="1.2")]))[0])), ("95", 1))
    e4 = esp(PID, OBR, OBX.replace("||95|", "||01.20|"))[0]
    mira("O4 «01.20» -> «1.20» esperado; guardado «1.20» correcto", (e4["observaciones"][0]["ValorNumero"],
         c(msg(PID, OBR, OBX.replace("||95|", "||01.20|")), dict(copia(e4), observaciones=[dict(e4["observaciones"][0], ValorNumero="1.20")]))[0]), ("1.20", []))
    e4b, imp4b, _, _ = esp(PID, OBR, OBX.replace("||95|", "||1,5|"))
    mira("O4 NM «1,5»: imposible, ValorNumero None (no se compara)", (imp4b, e4b["observaciones"][0]["ValorNumero"]),
         (["OBX 1: OBX-5 '1,5' no es un NM válido y se aceptó"], None))
    # O5 unidades
    mira("O5 OBX-6 CWE UCUM: unit/code/system", (ob0["UnidadTexto"], ob0["UnidadCode"], ob0["UnidadSistema"]), ("mg/dL", "mg/dL", "http://unitsofmeasure.org"))
    e5 = esp(PID, OBR, OBX.replace("|mg/dL^mg/dL^UCUM|", "|mg/dL|"))[0]["observaciones"][0]
    mira("O5 OBX-6 solo CWE.1: unit = CWE.1, sin code/system", (e5["UnidadTexto"], e5["UnidadCode"], e5["UnidadSistema"]), ("mg/dL", "", ""))
    e5b = esp(PID, OBR, OBX.replace("|mg/dL^mg/dL^UCUM|", "||"))[0]["observaciones"][0]
    mira("O5 OBX-6 vacío: sin unit (correcto)", (e5b["UnidadTexto"], e5b["UnidadCode"]), ("", ""))
    mira("O5 unidad perdida se delata (MO1)", len(c(base, dict(copia(e0), observaciones=[dict(ob0, UnidadTexto="", UnidadCode="", UnidadSistema="")]))[0]), 3)
    # O6 SN
    def sn(v):
        return esp(PID, OBR, OBX.replace("|NM|", "|SN|").replace("||95|", "||%s|" % v))
    o = sn(">^100")[0]["observaciones"][0]
    mira("O6 SN >^100: quantity con comparador", (o["ValorTipo"], o["ValorComparador"], o["ValorNumero"], o["ValorSeparador"]), ("quantity", ">", "100", ""))
    o = sn("^100")[0]["observaciones"][0]
    mira("O6 SN ^100 (= por omisión): quantity sin comparador", (o["ValorTipo"], o["ValorComparador"], o["ValorNumero"]), ("quantity", "", "100"))
    o = sn("^1^-^5")[0]["observaciones"][0]
    mira("O6 SN 1^-^5: range low/high", (o["ValorTipo"], o["ValorNumero"], o["ValorNum2"], o["ValorSeparador"]), ("range", "1", "5", "-"))
    o = sn("<^1^:^10")[0]["observaciones"][0]
    mira("O6 SN <^1^:^10: ratio con comparador", (o["ValorTipo"], o["ValorComparador"], o["ValorNumero"], o["ValorNum2"], o["ValorSeparador"]), ("ratio", "<", "1", "10", ":"))
    o = sn("^1^/^10")[0]["observaciones"][0]
    mira("O6 SN 1^/^10: ratio", (o["ValorTipo"], o["ValorSeparador"]), ("ratio", "/"))
    o = sn("<>^5")[0]["observaciones"][0]
    mira("O6 SN <>^5: valueString crudo", (o["ValorTipo"], o["ValorTexto"]), ("string", "<>^5"))
    o = sn("^5^+")[0]["observaciones"][0]
    mira("O6 SN 5^+: valueString crudo", (o["ValorTipo"], o["ValorTexto"]), ("string", "^5^+"))
    r6, imp6, _, _ = sn("^1^^5")
    mira("O6 SN num1 y num2 sin separador: imposible (ch02a.md:3783)", (any("forma SN" in z for z in imp6), r6["observaciones"][0]["ValorTexto"]), (True, None))
    r6b, imp6b, _, _ = sn(">^1,5")
    mira("O6 SN num1 no NM: imposible", any("num1" in z and "y se aceptó" in z for z in imp6b), True)
    mira("O6 range guardado como quantity se delata", len(c(msg(PID, OBR, OBX.replace("|NM|", "|SN|").replace("||95|", "||^1^-^5|")),
         dict(copia(sn("^1^-^5")[0]), observaciones=[dict(sn("^1^-^5")[0]["observaciones"][0], ValorTipo="quantity", ValorNum2="", ValorSeparador="")]))[0]), 3)
    # O7 texto
    o = esp(PID, OBR, OBX.replace("|NM|", "|ST|").replace("||95|", "||Ferr\\S\\Soler \\T\\ más|"))[0]["observaciones"][0]
    mira("O7 ST desescapado §2.7", (o["ValorTipo"], o["ValorTexto"]), ("string", "Ferr^Soler & más"))
    o = esp(PID, OBR, OBX.replace("|NM|", "|TX|").replace("||95|", "||Primer párrafo~Segundo párrafo|"))[0]["observaciones"][0]
    mira("O7 TX repeticiones = párrafos (D-ORU-3)", (o["ValorTexto"], o["RepeticionesPerdidas"]), ("Primer párrafo\nSegundo párrafo", 0))
    o = esp(PID, OBR, OBX.replace("|NM|", "|ST|").replace("||95|", "||uno~dos|"))[0]["observaciones"][0]
    mira("O7/O14 ST repetido: primera + RepeticionesPerdidas (L-ORU-3)", (o["ValorTexto"], o["RepeticionesPerdidas"]), ("uno", 1))
    o = esp(PID, OBR, OBX.replace("|NM|", "|FT|").replace("||95|", "||línea\\.br\\otra|"))[0]["observaciones"][0]
    mira("O7 FT: \\.br\\ se conserva literal", o["ValorTexto"], "línea\\.br\\otra")
    mst = msg(PID, OBR, OBX.replace("|NM|", "|ST|").replace("||95|", "||Ferr\\S\\Soler|"))
    e7 = esperado_mensaje(MR.mensajes(mst)[0])[0]
    mira("O7 escape sin resolver guardado: se delata; resuelto: nada",
         (len(c(mst, dict(copia(e7), observaciones=[dict(e7["observaciones"][0], ValorTexto="Ferr\\S\\Soler")]))[0]), c(mst, e7)[0]), (1, []))
    r7, imp7, _, _ = esp(PID, OBR, OBX.replace("|NM|", "|ST|").replace("||95|", "||a\x01b|"))
    mira("O18/S10 control en OBX-5: imposible y el valor no se compara", (any("U+0001" in z for z in imp7), r7["observaciones"][0]["ValorTexto"]), (True, None))
    # O8 CE
    o = esp(PID, OBR, OBX.replace("|NM|", "|CE|").replace("||95|", "||260385009^Negativo^SCT|"))[0]["observaciones"][0]
    mira("O8 CE: valueCodeableConcept", (o["ValorTipo"], o["ValorCodigo"], o["ValorDisplay"], o["ValorSistema"]), ("codeableconcept", "260385009", "Negativo", "http://snomed.info/sct"))
    r8, _, _, tol8 = esp(PID, OBR, OBX.replace("|NM|", "|CE|").replace("||95|", "||^Insuficiencia cardiaca|"))
    mira("O8 CE «^texto» (AMB-ORU-4): display sin code", (r8["observaciones"][0]["ValorCodigo"], r8["observaciones"][0]["ValorDisplay"], any("AMB-ORU-4" in z for z in tol8)),
         ("", "Insuficiencia cardiaca", True))
    o = esp(PID, OBR, OBX.replace("|NM|", "|IS|").replace("||95|", "||ABC|"), ver="2.6")[0]["observaciones"][0]
    mira("O8 IS en 2.6: coding.code sin system", (o["ValorTipo"], o["ValorCodigo"], o["ValorSistema"]), ("codeableconcept", "ABC", ""))
    # O9 fechas
    mira("O9/§3.5 fecha_hora", [fecha_hora(x)[0] for x in ("2023", "202301", "20230101", "2023010108", "202301010830", "20230101083000", "20230101083000.5", "20230101083000+0200", "20230101083000-0500")],
         ["2023", "2023-01", "2023-01-01", "2023-01-01T08:00:00+01:00", "2023-01-01T08:30:00+01:00", "2023-01-01T08:30:00+01:00", "2023-01-01T08:30:00.5+01:00",
          "2023-01-01T08:30:00+02:00", "2023-01-01T08:30:00-05:00"])
    mira("O9 fecha_hora con zona del PE", fecha_hora("202301010830", "+02:00")[0], "2023-01-01T08:30:00+02:00")
    mira("O9 fecha imposible", [fecha_hora(x)[1] is not None for x in ("20231301", "20230230", "2023010125", "2023-01-01", "202301010860")], [True] * 5)
    o = esp(PID, OBR, OBX.replace("|NM|", "|TS|").replace("||95|", "||20230101083000|"))[0]["observaciones"][0]
    mira("O9 TS -> datetime (AMB-ORU-1)", (o["ValorTipo"], o["ValorFecha"]), ("datetime", "2023-01-01T08:30:00+01:00"))
    o = esp(PID, OBR, OBX.replace("|NM|", "|DT|").replace("||95|", "||20230101|"))[0]["observaciones"][0]
    mira("O9 DT -> date", (o["ValorTipo"], o["ValorFecha"]), ("datetime", "2023-01-01"))
    o = esp(PID, OBR, OBX.replace("|NM|", "|TM|").replace("||95|", "||0830|"))[0]["observaciones"][0]
    mira("O9 TM -> time", (o["ValorTipo"], o["ValorFecha"]), ("time", "08:30:00"))
    r9, imp9, _, _ = esp(PID, OBR, OBX.replace("|NM|", "|TS|").replace("||95|", "||20230230|"))
    mira("O9 TS 30-feb: imposible", (any("día imposible" in z for z in imp9), r9["observaciones"][0]["ValorFecha"]), (True, None))
    mira("O9 fecha perdida se delata", len(c(msg(PID, OBR, OBX.replace("|NM|", "|TS|").replace("||95|", "||20230101083000|")),
         dict(copia(esp(PID, OBR, OBX.replace("|NM|", "|TS|").replace("||95|", "||20230101083000|"))[0]), observaciones=[dict(o, ValorTipo="datetime", ValorFecha="2023-01-01")]))[0]) >= 1, True)
    # O10 rango
    mira("O10 OBX-7 literal; parseado se delata", (ob0["RangoRef"], len(c(base, dict(copia(e0), observaciones=[dict(ob0, RangoRef="70")]))[0])), ("70-110", 1))
    # O11 interpretación
    o = esp(PID, OBR, OBX.replace("|70-110|N|", "|70-110|H~A|"))[0]["observaciones"][0]
    mira("O11 OBX-8 repetido: códigos unidos por ;", o["Interpretacion"], "H;A")
    r11, _, _, tol11 = esp(PID, OBR, OBX.replace("|70-110|N|", "|70-110|h|"))
    mira("O11 minúscula [S4]: H esperado + tolerancia", (r11["observaciones"][0]["Interpretacion"], any("OBX-8 'h'" in z for z in tol11)), ("H", True))
    o = esp(PID, OBR, OBX.replace("|70-110|N|", "|70-110|ZZ|"))[0]["observaciones"][0]
    mira("O11 fuera de la 0078 (user-defined): se espera igual", o["Interpretacion"], "ZZ")
    mira("O11 flag perdido se delata", len(c(base, dict(copia(e0), observaciones=[dict(ob0, Interpretacion="")]))[0]), 1)
    # O12 estado
    mira("O12 0085 oficial + sitio [S62]", [estado_0085(x) for x in "FPCDWXIORSUN"],
         ["final", "preliminary", "corrected", "entered-in-error", "entered-in-error", "cancelled", "registered", "registered", "preliminary", "preliminary", "final", "final"])
    mira("O12 F -> final; P guardado como final se delata (MO2)", (ob0["Estado"], c(base, dict(copia(e0), observaciones=[dict(ob0, Estado="preliminary")]))[0]),
         ("final", ["OBX 1 (2345-7) Estado: esperado 'final', observado 'preliminary'"]))
    r12, _, _, tol12 = esp(PID, OBR, OBX.replace("|||F|||", "|||R|||"))
    mira("O12 R [S62] -> preliminary + nota S62", (r12["observaciones"][0]["Estado"], any(z.startswith("[S62]") for z in tol12)), ("preliminary", True))
    r12b, imp12b, _, _ = esp(PID, OBR, OBX.replace("|||F|||", "|||Q|||"))
    mira("O12 Q en 2.5: imposible, Estado None", (imp12b, r12b["observaciones"][0]["Estado"]), (["OBX 1: OBX-11 'Q' no está en la tabla 0085 y se aceptó"], None))
    r12c, imp12c, _, tol12c = esp(PID, OBR, OBX.replace("|||F|||", "|||Q|||"), ver="2.6")
    mira("O12 Q en 2.6 [S22]: tupla ObservationStatus + tolerancia; «final» pasa, «Q» no",
         (imp12c, any(z.startswith("[S22]") for z in tol12c),
          c(msg(PID, OBR, OBX.replace("|||F|||", "|||Q|||"), ver="2.6"), dict(copia(r12c), observaciones=[dict(r12c["observaciones"][0], Estado="final")]))[0],
          len(c(msg(PID, OBR, OBX.replace("|||F|||", "|||Q|||"), ver="2.6"), dict(copia(r12c), observaciones=[dict(r12c["observaciones"][0], Estado="Q")]))[0])),
         ([], True, [], 1))
    r12d, _, _, tol12d = esp(PID, OBR, OBX.replace("|||F|||", "|||f|||"))
    mira("O12 f minúscula [S4]", (r12d["observaciones"][0]["Estado"], any("OBX-11 'f'" in z for z in tol12d)), ("final", True))
    r12e, _, _, tol12e = esp(PID, OBR, OBX.replace("|||F|||", "|||D|||"))
    mira("O12 D: entered-in-error + AMB-ORU-6", (r12e["observaciones"][0]["Estado"], any("AMB-ORU-6" in z for z in tol12e)), ("entered-in-error", True))
    r12f, _, _, _ = esp(PID, OBR, OBX.replace("|||F|||", "||||||"))
    mira("O12 OBX-11 vacío: Estado None (lo juzga el acuse, 101)", r12f["observaciones"][0]["Estado"], None)
    # O13 fecha efectiva
    mira("O13 OBX-14 valorado", (ob0["Fecha"], ob0["FechaOrigen"]), ("2023-01-01T08:30:00+01:00", "OBX-14"))
    o = esp(PID, OBR, OBX.replace("|||20230101083000", "|||"))[0]["observaciones"][0]
    mira("O13 OBX-14 vacío -> OBR-7 [S63]", (o["Fecha"], o["FechaOrigen"]), ("2023-01-01T08:00:00+01:00", "OBR-7"))
    o = esp(PID, OBR.replace("|||20230101080000|", "||||"), OBX.replace("|||20230101083000", "|||"))[0]["observaciones"][0]
    mira("O13 ambos vacíos -> ninguna", (o["Fecha"], o["FechaOrigen"]), ("", "ninguna"))
    mira("O13 effective perdido se delata (MO: OBX-14 ausente)", len(c(base, dict(copia(e0), observaciones=[dict(ob0, Fecha="", FechaOrigen="ninguna")]))[0]), 2)
    r13, imp13, _, _ = esp(PID, OBR, OBX.replace("|||20230101083000", "|||20231301"))
    mira("O13 OBX-14 imposible", (any("OBX-14" in z and "mes imposible" in z for z in imp13), r13["observaciones"][0]["Fecha"]), (True, None))
    # O14 repeticiones NM
    o = esp(PID, OBR, OBX.replace("||95|", "||95~96|"))[0]["observaciones"][0]
    mira("O14 OBX-5 repetido NM: primera + contador; contador 0 se delata",
         (o["ValorNumero"], o["RepeticionesPerdidas"], len(c(msg(PID, OBR, OBX.replace("||95|", "||95~96|")), dict(copia(e0), observaciones=[dict(o, RepeticionesPerdidas=0)]))[0])),
         ("95", 1, 1))
    # O15 no soportado
    o = esp(PID, OBR, OBX.replace("|NM|", "|XPN|").replace("||95|", "||Pérez^Ana|"))[0]["observaciones"][0]
    mira("O15 XPN: no_soportado con crudo; crudo perdido se delata", (o["ValorTipo"], o["ValorCrudo"],
         len(c(msg(PID, OBR, OBX.replace("|NM|", "|XPN|").replace("||95|", "||Pérez^Ana|")), dict(copia(esp(PID, OBR, OBX.replace("|NM|", "|XPN|").replace("||95|", "||Pérez^Ana|"))[0]), observaciones=[dict(o, ValorCrudo="")]))[0])),
         ("no_soportado", "Pérez^Ana", 1))
    mira("O15 ValorCrudo no se compara cuando hay value[x]", c(base, dict(copia(e0), observaciones=[dict(ob0, ValorCrudo="lo que sea")]))[0], [])
    # O16 campos fuera del contrato: no cambian nada
    mira("O16 OBX-16 (fuera) no cambia el esperado", esp(PID, OBR, OBX + "||Obs^Ana")[0] == e0, True)
    # O17 truncado
    r17 = esp(PID, OBR, OBX.replace("|||F|||", "|||FF|||"))
    mira("O17/S46 OBX-11 FF: truncado a F, Truncado 1; Truncado 0 guardado se delata", (r17[0]["observaciones"][0]["Estado"], r17[0]["cabecera"]["Truncado"], r17[1],
         c(msg(PID, OBR, OBX.replace("|||F|||", "|||FF|||")), dict(copia(r17[0]), cabecera=dict(r17[0]["cabecera"], Truncado=0)))[0]),
         ("final", 1, [], ["Truncado: esperado 1, observado 0"]))
    r17b = esp(PID, OBR, OBX.replace("|70-110|", "|%s|" % ("x" * 61)))[0]
    mira("O17 OBX-7 de 61: Truncado 1 y RangoRef recortado a 60", (r17b["cabecera"]["Truncado"], len(r17b["observaciones"][0]["RangoRef"])), (1, 60))
    r17c = esp(PID, OBR, OBX.replace("|NM|", "|TX|").replace("||95|", "||%s|" % ("t" * 32001)))[0]
    mira("O17/D-ORU-4 OBX-5 > 32000: Truncado 1; 32000 no", (r17c["cabecera"]["Truncado"], esp(PID, OBR, OBX.replace("|NM|", "|TX|").replace("||95|", "||%s|" % ("t" * 32000)))[0]["cabecera"]["Truncado"]), (1, 0))
    # O18 S9 / S38 / S7
    r18 = esp(PID, OBR, OBX.replace("|NM|", "|ST|").replace("||95|", "||Mu<0xF1>oz|"))[0]["observaciones"][0]
    mira("O18/S9 byte latin-1 marcado: Muñoz", r18["ValorTexto"], "Muñoz")
    r18b = esp(PID, OBR, OBX.replace("2345-7^Glucosa^LN", "2345-7^Glucosa en sangre, ayunas – ñ^LN"))[0]["observaciones"][0]
    mira("O18/S38 UTF-8 en OBX-3.2", r18b["CodigoDisplay"], "Glucosa en sangre, ayunas – ñ")
    zw = "Glucosa​"
    mira("O18/S7 Cf conservado: nada; perdido: se delata", (c(msg(PID, OBR, OBX.replace("Glucosa", zw)), esp(PID, OBR, OBX.replace("Glucosa", zw))[0])[0],
         len(c(msg(PID, OBR, OBX.replace("Glucosa", zw)), dict(copia(esp(PID, OBR, OBX.replace("Glucosa", zw))[0]), observaciones=[dict(esp(PID, OBR, OBX.replace("Glucosa", zw))[0]["observaciones"][0], CodigoDisplay="Glucosa")]))[0])), ([], 1))
    # R1-R2 identificadores
    mira("R1/R2 Placer/Filler", (in0["Placer"], in0["Filler"]), ("PL1", "FL1"))
    mira("R1 placer perdido se delata", c(base, dict(copia(e0), informes=[dict(in0, Placer="")]))[0], ["OBR 1 (24323-8) Placer: esperado 'PL1', observado ''"])
    o = esp(PID, OBR.replace("|PL1|FL1|", "|||"), OBX)[0]["informes"][0]
    mira("R1/R2 OBR-2/3 vacíos: sin identifier", (o["Placer"], o["Filler"]), ("", ""))
    # R3 código
    mira("R3 OBR-4 -> code", (in0["CodigoCode"], in0["CodigoDisplay"], in0["CodigoSistema"]), ("24323-8", "Panel", "http://loinc.org"))
    # R4 estado 0123
    mira("R4 0123 oficial + sitio [S64]", [estado_0123(x) for x in ("O", "I", "S", "P", "C", "R", "F", "X", "A", "Y", "Z", "M", "N", "")],
         ["registered", "registered", "registered", "preliminary", "corrected", "partial", "final", "cancelled"] + ["unknown"] * 6)
    mira("R4 OBR-25 F -> final; unknown guardado se delata", (in0["Estado"], c(base, dict(copia(e0), informes=[dict(in0, Estado="unknown")]))[0]),
         ("final", ["OBR 1 (24323-8) Estado: esperado 'final', observado 'unknown'"]))
    r4, _, _, tol4 = esp(PID, OBR.replace("|||F", "|||"), OBX)
    mira("R4 OBR-25 vacío -> unknown [S64] + nota", (r4["informes"][0]["Estado"], any(z.startswith("[S64]") for z in tol4)), ("unknown", True))
    r4b, imp4b2, _, _ = esp(PID, OBR.replace("|||F", "|||Q"), OBX)
    mira("R4 OBR-25 Q en 2.5: imposible", (any("tabla 0123" in z for z in imp4b2), r4b["informes"][0]["Estado"]), (True, None))
    r4c, imp4c, _, tol4c = esp(PID, OBR.replace("|||F", "|||Q"), OBX, ver="2.6")
    mira("R4 OBR-25 Q en 2.6 [S22]: tupla", (imp4c, isinstance(r4c["informes"][0]["Estado"], tuple)), ([], True))
    r4d, _, _, tol4d = esp(PID, OBR.replace("|||F", "|||f"), OBX)
    mira("R4 OBR-25 f minúscula [S4]", (r4d["informes"][0]["Estado"], any("OBR-25 'f'" in z for z in tol4d)), ("final", True))
    # R5 efectivo
    mira("R5 OBR-7 -> Efectivo; OBR-8 vacío", (in0["Efectivo"], in0["EfectivoFin"]), ("2023-01-01T08:00:00+01:00", ""))
    o = esp(PID, OBR.replace("|||20230101080000|", "|||20230101080000|20230101090000|"), OBX)[0]["informes"][0]
    mira("R5 OBR-8 -> EfectivoFin", o["EfectivoFin"], "2023-01-01T09:00:00+01:00")
    r5, _, _, tol5 = esp(PID, OBR.replace("|||20230101080000|", "||||"), OBX)
    mira("R5 OBR-7 vacío: nota L-MT6, Efectivo vacío", (r5["informes"][0]["Efectivo"], any("[L-MT6]" in z for z in tol5)), ("", True))
    mira("R5 efectivo perdido se delata", len(c(base, dict(copia(e0), informes=[dict(in0, Efectivo="")]))[0]), 1)
    r5b, imp5b, _, _ = esp(PID, OBR.replace("|||20230101080000|", "|||20230145|"), OBX.replace("|||20230101083000", "|||"))
    mira("R5 OBR-7 imposible: imposible; la Fecha heredada del OBX no se compara", (any("OBR-7" in z for z in imp5b), r5b["informes"][0]["Efectivo"], r5b["observaciones"][0]["Fecha"]), (True, None, None))
    # R6 emitido
    mira("R6 OBR-22 con segundos -> instant", in0["Emitido"], "2023-01-01T09:00:00+01:00")
    r6c, _, _, tol6c = esp(PID, OBR.replace("|20230101090000|||F", "|202301010900|||F"), OBX)
    mira("R6 OBR-22 sin segundos: Emitido vacío + D-ORU-5", (r6c["informes"][0]["Emitido"], any("[D-ORU-5]" in z for z in tol6c)), ("", True))
    mira("R6 instante", [instante(x)[:2] for x in ("20230101090000", "202301010900", "20230101090000+0000", "")],
         [("2023-01-01T09:00:00+01:00", None), ("", None), ("2023-01-01T09:00:00+00:00", None), ("", None)])
    mira("R6 emitido perdido se delata", len(c(base, dict(copia(e0), informes=[dict(in0, Emitido="")]))[0]), 1)
    # R7 pertenencia y recuentos
    OBR2 = OBR.replace("OBR|1|PL1|FL1|24323-8^Panel", "OBR|2|PL2|FL2|58410-2^Hemograma")
    OBXb = OBX.replace("OBX|1|NM|2345-7^Glucosa", "OBX|2|NM|718-7^Hemoglobina").replace("||95|", "||13.5|")
    e7r = esp(PID, OBR, OBX, OBR2, OBXb, OBXb.replace("OBX|2|", "OBX|3|"))[0]
    mira("R7 2 OBR × (1+2) OBX: pertenencia e identificadores", ([(o["Informe"], o["OrdenEnInforme"], o["Orden"], o["Identificador"]) for o in e7r["observaciones"]],
         [i["NumObx"] for i in e7r["informes"]], e7r["cabecera"]["NumInformes"], e7r["cabecera"]["NumObservaciones"]),
         ([(1, 1, 1, "M1#1.1"), (2, 1, 2, "M1#2.1"), (2, 2, 3, "M1#2.2")], [1, 2], 2, 3))
    m7 = msg(PID, OBR, OBX, OBR2, OBXb, OBXb.replace("OBX|2|", "OBX|3|"))
    ec = copia(e7r); ec["observaciones"][1]["Informe"] = 1
    mira("R7 pertenencia equivocada (MO4-like) se delata", any("Informe" in z for z in c(m7, ec)[0]), True)
    ec = copia(e7r); ec["observaciones"].pop()
    mira("recuento: OBX descartado (MO4) -> Observaciones: esperado 3, observado 2", c(m7, ec)[0], ["Observaciones: esperado 3, observado 2"])
    ec = copia(e7r); ec["informes"].pop(); ec["cabecera"]["NumInformes"] = 1
    mira("recuento: informe perdido", c(m7, ec)[0], ["NumInformes: esperado 2, observado 1", "Informes: esperado 2, observado 1"])
    ec = copia(e7r); ec["observaciones"] = [ec["observaciones"][2], ec["observaciones"][0], ec["observaciones"][1]]
    mira("comparación por (Informe, OrdenEnInforme), no por orden de la lista", c(m7, ec)[0], [])
    # agrupación §3.1
    g = agrupar(MR.mensajes(msg(PID, "OBX|0|ST|x^y^L||antes||||||F", OBR, OBX, "NTE|1||nota", "NTE|2||otra", "SPM|1|S1||BLD", OBX, OBX, OBR2, "NTE|1||del OBR", OBXb, "PID|2||OTRO", OBR, OBX))[0])
    mira("§3.1 agrupar: suelto, especimen, todos los NTE (O1), 2.º PATIENT_RESULT", (len(g["informes"]), [len(i["obx"]) for i in g["informes"]], g["obx_sueltos"],
         g["obx_especimen"], g["nte"], g["patient_result_extra"]), (2, [1, 1], 1, 2, 3, 1))
    eg, _, _, tg = esp(PID, "OBX|0|ST|x^y^L||antes||||||F", OBR, OBX, "NTE|1||nota", "SPM|1|S1||BLD", OBX, OBR2, OBXb, "PID|2||OTRO", OBR, OBX)
    mira("§3.1 cabecera: NumObxEspecimen, NumNte, notas S45/L-ORU-5/L-ORU-4/AMB-ORU-5",
         (eg["cabecera"]["NumInformes"], eg["cabecera"]["NumObservaciones"], eg["cabecera"]["NumObxEspecimen"], eg["cabecera"]["NumNte"],
          sorted(z.split("]")[0] + "]" for z in tg if z.startswith("[") and z.split("]")[0] + "]" in ("[S45]", "[L-ORU-5]", "[L-ORU-4]", "[AMB-ORU-5]"))),
         (2, 2, 1, 1, ["[AMB-ORU-5]", "[L-ORU-4]", "[L-ORU-5]", "[S45]"]))
    e_sin = esp(PID, OBR)[0]
    mira("ORU sin OBX [S55]: informe sin observaciones", (e_sin["cabecera"]["NumObservaciones"], e_sin["informes"][0]["NumObx"], e_sin["observaciones"]), (0, 0, []))
    _, _, estA, _ = esp(PID, OBR, OBX)
    m_a = MR.mensajes(msg(PID, OBR, OBX).replace("ORU^R01^ORU_R01", "ORU^R30^ORU_R30"))[0]
    mira("estructura: MSH-9 no ORU^R01 aceptado se delata", any("no es ORU^R01" in z for z in esperado_mensaje(m_a)[2]), True)
    # DV-ORU-2 valor_valido (para el acuse)
    mira("DV-ORU-2 valor_valido", [valor_valido(t, v) for t, v in (("NM", "95"), ("NM", "1,5"), ("NM", ".5"), ("NM", "95^x"), ("SN", ">^100"), ("SN", "^1^-^5"),
         ("SN", "^1^^5"), ("SN", "x^1"), ("SN", ">^1,5"), ("TS", "20230101"), ("TS", "20230230"), ("DT", "202301"), ("DT", "2023010108"), ("TM", "0830"), ("TM", "2560"), ("ST", "x"), ("CE", "a^b"))],
         [True, False, True, False, True, True, False, False, False, True, False, True, False, True, False, None, None])
    # entradas observadas laxas: enteros como texto, columnas ausentes con nada que guardar
    lax = {"cabecera": {k: (str(v) if k in ENTEROS else v) for k, v in cab0.items()},
           "informes": [{k: v for k, v in in0.items() if v not in ("", 0)}], "observaciones": [{k: v for k, v in ob0.items() if v not in ("", 0)}]}
    mira("observado con enteros como texto y columnas vacías ausentes: nada", c(base, lax)[0], [])
    mira("hecho_de", [hecho_de(z) for z in ("OBX 3 (718-7) Estado: esperado 'final', observado 'preliminary'", "OBR 1 (x) Placer: esperado 'a', observado ''",
         "PacienteId: esperado 'X1', observado ''", "Observaciones: esperado 3, observado 2", "Informes: esperado 2, observado 1", "Gender: esperado 'male', observado 'x'",
         "OBX 1 (2345-7) ValorNumero: esperado '95', observado '9'", "OBX 1 (2345-7) UnidadCode: esperado 'a', observado 'b'", "Truncado: esperado 1, observado 0")],
         ["OBX-11", "OBR-2", "PID-3", "OBX", "OBR", None, "OBX-5", "OBX-6", "longitud"])
    print("AUTOPRUEBA DE mapeador_oru: " + ("TODO BIEN (%d comprobaciones)" % 0 if False else ("TODO BIEN" if not mal else "FALLAN %d" % len(mal))))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(autoprueba() if sys.argv[1:2] == ["--autoprueba"] else 0)
