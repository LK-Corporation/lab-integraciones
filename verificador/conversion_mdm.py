#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 26 (md/diseno-md.md, a ciegas, DV-MD-0; decisiones de Jev en md/decisiones-qmd.md): el juez ante un MDM^T02 convertido
por un tercero. Punto `mdm_conv` (S-MD-1, familia «mdm», `solo_transformacion`), hermano de adt_conv, oru_conv y vxu_conv, con
su misma evidencia, clases y veredicto (S-MD-2, S-MD-4). conversion.py llama aquí desde seis ganchos que con las familias adt,
oru y vxu no cambian nada (P-MD-25); lo de MDM vive en este módulo: los grupos de orden y los documentos (TXA con sus OBX y NTE),
el emparejamiento de DocumentReference, ServiceRequest y Encounter (§2.2) y el perfil «guía» de DocumentReference (§4).

A diferencia de VXU (DV-VX-2), no registra sus citas en conversion.C (P-MD-25 d exige que no cambie): pasa las suyas en cada
hallazgo y corrige las que ponen por omisión las funciones de conversion.py que reutiliza (_reusa). Solo registra su INFO en
conversion.INFO["mdm"]. Solo biblioteca estándar; el contenido de un documento no se interpreta (L-MD-1).
  python3 conversion_mdm.py --autoprueba   -> la tabla 0272 contra el paquete de la guía (si está), las citas y el perfil"""
import base64
import binascii
import collections
import os
import re
import sys

import conversion as CV
import mapeador_referencia as MR
import puntos_entrada as PE

_t, _f, _d, _reps, _comp, _sub, _seg = CV._t, CV._f, CV._d, CV._reps, CV._comp, CV._sub, CV._seg
_codigos, _valores, _hecho, FUERA = CV._codigos, CV._valores, CV._hecho, CV.FUERA

TIPOS = ("Patient", "Encounter", "DocumentReference", "ServiceRequest")          # §3: a propósito sin Observation ni DiagnosticReport
FALTAN = ("PID", "PV1", "TXA", "OBX")                                             # §2.3: sin ellos, un error es rechazo aceptable

# Q-MD-D (Jev, md/decision-jev-qmd.md; tabla en md/decisiones-qmd.md). ALTERNATIVA_MD: la segunda opción de Jev en las que
# salieron con confianza ≤ 0,52 (regla del §9.1); con_alternativas_md() la aplica sin tocar el juez.
DECISIONES_MD = {"Q-MD-D-1": "solo_t02", "Q-MD-D-2": "nota", "Q-MD-D-3": "literal_o_registrado",
                 "Q-MD-D-4": "literal_o_mapa_y_literal_invalido", "Q-MD-D-5": "cualquier_reparto", "Q-MD-D-6": "nota",
                 "Q-MD-D-7": "una_por_orden", "Q-MD-D-8": "nota", "Q-MD-D-9": "extension_y_coherente", "Q-MD-D-10": "basico",
                 "Q-MD-D-11": "cualquiera", "Q-MD-D-12": "nota"}
ALTERNATIVA_MD = {"Q-MD-D-1": "t02_y_cuatro", "Q-MD-D-3": "literales", "Q-MD-D-4": "literal_o_mapa_sin_penalizar",
                  "Q-MD-D-6": "dato_perdido", "Q-MD-D-8": "inventado", "Q-MD-D-9": "extension", "Q-MD-D-11": "primero",
                  "Q-MD-D-12": "dato_perdido"}

V2 = "http://terminology.hl7.org/CodeSystem/v2-%s"
V3_CONF = "http://terminology.hl7.org/CodeSystem/v3-Confidentiality"
ALTERNATE = ("http://hl7.org/fhir/StructureDefinition/alternate-codes", "https://hl7.org/fhir/StructureDefinition/alternate-codes")  # AMB-MD-5

# Las tablas de §4.5. La 0272 es el ConceptMap del paquete (autoprueba la coteja); MAPA_0271 y FAMILIA_0191 no son de la guía (L-MD-6).
MAPAS_MDM = {"table-hl70272-to-v2-0272": {"V": (V2 % "0272", "V"), "R": (V2 % "0272", "R"), "U": (V2 % "0272", "U")}}
MAPA_0271 = {"LA": {"final"}, "AU": {"final", "preliminary"}, "PA": {"preliminary"}, "IN": {"preliminary"}, "IP": {"preliminary"},
             "DI": {"preliminary"}, "DO": {"preliminary"}}                       # [E9 CH09.txt:87-132]; composition-status (R4)
FAMILIA_0191 = {"TEXT": "text", "TX": "text", "FT": "text", "AP": "application", "AU": "audio", "IM": "image", "MULTIPART": "multipart",
                "NS": None, "SD": None, "SI": None}                               # [E9 CH09.txt:892-903]; tipos principales de MIME
T0191 = set(FAMILIA_0191)
T0271 = set(MAPA_0271)
T0272 = {"V", "R", "U"}
T0273 = {"AV", "CA", "OB", "UN"}
T0299 = {"A", "HEX", "BASE64"}
T0125 = {"AD", "CE", "CF", "CK", "CN", "CP", "CX", "DT", "ED", "FT", "MO", "NM", "PN", "RP", "SN", "ST", "TM", "TN", "TS", "TX", "XAD",
         "XCN", "XON", "XPN", "XTN"}                                              # [E7 CH07.txt:2603-2637]
CON_DESTINO = ("TX", "FT", "ED", "RP")                                            # [G OBX_DocumentReference.csv:8-13]
COMPOSITION_STATUS = {"preliminary", "final", "amended", "entered-in-error"}      # [F codesystem-composition-status.json:49-68]
DOCREF_STATUS = {"current", "superseded", "entered-in-error"}                    # [F codesystem-document-reference-status.json:38-52]
REQUEST_STATUS = {"draft", "active", "on-hold", "revoked", "completed", "entered-in-error", "unknown"}           # R4 request-status
REQUEST_INTENT = {"proposal", "plan", "directive", "order", "original-order", "reflex-order", "filler-order", "instance-order",
                  "option"}                                                       # R4 request-intent (L-MD-6)
COHERENTE_0273 = {"CA": "entered-in-error", "OB": "superseded"}                  # Q-MD-D-9 (b)
MIME_TEXTO = {"TX": {"literales": {"application/text"}, "literal_o_registrado": {"application/text", "text/plain"}},
              "FT": {"literales": {"text/hl7v2"}, "literal_o_registrado": {"text/hl7v2", "text/plain"}}}           # Q-MD-D-3


def _dec(J, q):
    return J.dec.get(q, DECISIONES_MD[q])


def con_alternativas_md(*qs):
    """Las decisiones con la alternativa de las Q indicadas (sensibilidad preinscrita de md/decisiones-qmd.md). La de Q-MD-D-1
    cambia los tipos del punto: se juzga con PE_ALTERNATIVA_EVENTOS."""
    return {q: ALTERNATIVA_MD[q] for q in qs}


# ---------------------------------------------------------------------------- citas (§4.6)
C_MDM = {"TXA": ["[G MSG_MDM_T02.csv:29] TXA → DocumentReference[1]", "[E9 CH09.txt:345-354]"],
         "TXA-2": ["[CM segment-txa-to-documentreference TXA-2 → type]", "[CM datatype-is-to-codeableconcept]", "[G TXA_DocumentReference.csv:6]",
                   "[E9 §9.6.1.2 tabla 0270]", "[F DocumentReference.type]", "[AMB-MD-1]"],
         "TXA-3": ["[CM segment-txa-to-documentreference TXA-3 → content.attachment.contentType]", "[G TXA_DocumentReference.csv:7]",
                   "[E9 §9.6.1.3 tabla 0191]", "[F Attachment.contentType required]", "[AMB-MD-2]"],
         "TXA-6": ["[CM segment-txa-to-documentreference TXA-6 → date]", "[G TXA_DocumentReference.csv:10-12]", "[F DocumentReference.date instant]",
                   "[AMB-MD-17]"],
         "TXA-9": ["[CM segment-txa-to-documentreference TXA-9 → author]", "[CM datatype-xcn-to-practitioner]", "[G TXA_DocumentReference.csv:15]",
                   "[F DocumentReference.author]"],
         "TXA-10": ["[G TXA_DocumentReference.csv:16]", "[CM datatype-xcn-to-practitioner]", "[F DocumentReference.authenticator 0..1]", "[AMB-MD-14]"],
         "TXA-12": ["[CM segment-txa-to-documentreference TXA-12 → masterIdentifier]", "[CM datatype-ei-organization-to-identifier]",
                    "[G TXA_DocumentReference.csv:18]", "[F DocumentReference.masterIdentifier]", "[E9 §9.6.1.12]", "[AMB-MD-19]"],
         "TXA-16": ["[CM segment-txa-to-documentreference TXA-16 → identifier[1]]", "[CM datatype-st-to-identifier]", "[G TXA_DocumentReference.csv:22]",
                    "[F DocumentReference.identifier]"],
         "TXA-17": ["[CM segment-txa-to-documentreference TXA-17 → docStatus]", "[CM datatype-id-to-code $value]", "[G TXA_DocumentReference.csv:23]",
                    "[F DocumentReference.docStatus required]", "[E9 §9.6.1.17 tabla 0271]", "[AMB-MD-3]"],
         "TXA-18": ["[CM segment-txa-to-documentreference TXA-18 → securityLabel]", "[CM table-hl70272-to-v2-0272]", "[G TXA_DocumentReference.csv:24]",
                    "[F DocumentReference.securityLabel extensible]", "[E9 §9.6.1.18 tabla 0272]", "[AMB-MD-20]"],
         "TXA-19": ["[CM segment-txa-to-documentreference TXA-19 → status / status.extension]", "[G TXA_DocumentReference.csv:4,25-27]",
                    "[F DocumentReference.status required]", "[E9 §9.6.1.19 tabla 0273]", "[AMB-MD-4]", "[AMB-MD-5]"],
         "OBX-TX": ["[CM segment-obx-to-documentreference OBX-5 IF OBX-2=TX]", "[G OBX_DocumentReference.csv:12-13]", "[E2A §2.A.78 TX]",
                    "[F DocumentReference.content.attachment]"],
         "OBX-FT": ["[CM segment-obx-to-documentreference OBX-5 IF OBX-2=FT]", "[G OBX_DocumentReference.csv:9-10]", "[E2A §2.A.31 FT]", "[E2 §2.7.6]"],
         "OBX-ED": ["[CM segment-obx-to-documentreference OBX-5 IF OBX-2=ED]", "[CM datatype-ed-to-attachment]", "[G OBX_DocumentReference.csv:8]",
                    "[G ED_Attachment.csv:5-9]", "[E2A §2.A.24 ED]"],
         "OBX-RP": ["[CM segment-obx-to-documentreference OBX-5 IF OBX-2=RP]", "[CM datatype-rp-to-attachment]", "[G OBX_DocumentReference.csv:11]",
                    "[G RP_Attachment.csv:4,6]", "[E2A §2.A.65 RP]"],
         "OBX-sin": ["[G OBX_DocumentReference.csv:8-13] (sin fila)", "[E9 CH09.txt:191-195]", "[L-MD-2]"],
         "OBX-content": ["[G MSG_MDM_T02.csv:34] OBX → DocumentReference[1]", "[F DocumentReference.content 1..*]",
                         "[F DocumentReference.content.attachment 1..1]"],
         "OBX-data": ["[G ED_Attachment.csv:9] base64", "[F Attachment.data base64Binary]", "[L-MD-7]"],
         "OBX-obs": ["[G MSG_MDM_T02.csv:34] OBX → DocumentReference[1], no Observation", "[E9 CH09.txt:345-354]", "[Q-MD-D-8]"],
         "NTE-3": ["[CM segment-nte-to-documentreference NTE-3 → content.attachment.data]", "[G NTE_DocumentReference.csv:6-7]",
                   "[G MSG_MDM_T02.csv:35]", "[E2 §2.15.10.3]", "[AMB-MD-13]"],
         "ORC-ref": ["[G MSG_MDM_T02.csv:20,29] context.related → ServiceRequest", "[E9 CH09.txt:235-240]", "[F DocumentReference.context.related]",
                     "[AMB-MD-16]"],
         "ORC-5": ["[G ORC_ServiceRequest.csv:4] «localized interpretation»", "[F ServiceRequest.status required]", "[AMB-MD-25]"],
         "ORC-int": ["[G ORC_ServiceRequest.csv:4] «localized interpretation»", "[F ServiceRequest.intent required]", "[AMB-MD-25]"],
         "SR": ["[G MSG_MDM_T02.csv:20,26] ORC/OBR → ServiceRequest[1]", "[E9 CH09.txt:322-343]"],
         "SR-subject": ["[G MSG_MDM_T02.csv:20] ServiceRequest.subject=Patient[PID]", "[F ServiceRequest.subject 1..1]"],
         "DR-subject": ["[G MSG_MDM_T02.csv:29] (sin fila para subject)", "[F DocumentReference.subject PID-3]", "[AMB-MD-15]", "[L-MD-5]"],
         "DR-encounter": ["[G MSG_MDM_T02.csv:15] PV1 → Encounter[1]", "[F DocumentReference.context.encounter]",
                          "[F Bundle «Resolving references in Bundles»]"]}
C_SEG = {"PID": ["[G MSG_MDM_T02.csv:13] PID → Patient[1]", "[E9 CH09.txt:319-321]"],          # las claves que en conversion.C son
         "PV1": ["[G MSG_MDM_T02.csv:15] PV1 → Encounter[1]", "[E9 CH09.txt:319-321]"],        # de ADT, ORU o VXU
         "OBR-4": ["[G OBR_ServiceRequest.csv:13]", "[CM datatype-cwe-to-codeableconcept]", "[E4 §4.5.3.4]", "[F ServiceRequest.code]"],
         "ORC-1": ["[G MSG_MDM_T02.csv:20,26] ORC/OBR → ServiceRequest[1]", "[E9 CH09.txt:322-343]"],
         "ORC-2": ["[G ORC_ServiceRequest.csv:10-12]", "[G OBR_ServiceRequest.csv:6-8]", "[CM datatype-ei-extension-to-identifier]",
                   "[E9 CH09.txt:242-246]", "[AMB-CV-8]"],
         "ORC-3": ["[G ORC_ServiceRequest.csv:13-15]", "[G OBR_ServiceRequest.csv:9-12]", "[CM datatype-ei-extension-to-identifier]",
                   "[E9 CH09.txt:242-246]", "[AMB-CV-8]"]}


def _cit(clave):
    base = re.sub(r"\(\d+\)", "", clave)
    return C_SEG.get(base) or C_MDM.get(base) or C_MDM.get(base.split("-")[0]) or []


def _cuenta(J, subtipo, hecho, que, clase="fidelidad", tabla=False, citas=None):
    J.cuenta(subtipo, hecho, que, clase=clase, tabla=tabla, citas=list(citas or _cit(hecho)))


def _nota(J, subtipo, hecho, que, certeza="literal"):
    J.hs.append(CV._h("nota", subtipo, hecho, que, cuenta=False, certeza=certeza, citas=_cit(hecho)))


def _reusa(J, citas, fn, *a, **k):
    """Llama a una función de conversion.py y pone las citas de MDM en lo que haya citado por omisión desde conversion.C (que
    es de ADT, ORU o VXU, o está vacío para TXA)."""
    n = len(J.hs)
    fn(*a, **k)
    for h in J.hs[n:]:
        if h["citas"] == CV._cit(h["hecho"]):
            h["citas"] = list(citas)


# ---------------------------------------------------------------------------- el mensaje (§2.2)
def grupos(m):
    """Grupos de orden (un ORC abre; un OBR sin ORC delante, también, con nota) y documentos (un TXA abre; le pertenecen los OBX
    que le siguen y, a cada OBX, los NTE que le siguen). TQ1/TQ2 se ignoran; un OBX antes del primer TXA solo se cuenta (L-MD-9).
    Cada OBX lleva su número `k` en todo el mensaje y cada NTE su `j` (los hechos OBX(k)-5 y NTE(j)-3)."""
    ordenes, docs, fuera, ctx, k, j, suelta = [], [], 0, None, 0, 0, 0
    for s in m.segs:
        n = s.split(m.f)[0]
        if n == "ORC":
            ordenes.append({"orc": s, "obr": None, "nte": [], "sin_orc": False})
            ctx = "orden"
        elif n == "OBR":
            if ordenes and ctx == "orden" and ordenes[-1]["obr"] is None and ordenes[-1]["orc"] is not None:
                ordenes[-1]["obr"] = s
            else:
                ordenes.append({"orc": None, "obr": s, "nte": [], "sin_orc": True})
            ctx = "orden"
        elif n == "TXA":
            docs.append({"txa": s, "obx": []})
            ctx = "txa"
        elif n == "OBX":
            k += 1
            if docs:
                docs[-1]["obx"].append({"seg": s, "k": k, "nte": []})
                ctx = "obx"
            else:
                fuera += 1
                ctx = "fuera"
        elif n == "NTE":
            j += 1
            if ctx == "orden":
                ordenes[-1]["nte"].append({"seg": s, "j": j})
            elif ctx == "obx":
                docs[-1]["obx"][-1]["nte"].append({"seg": s, "j": j})
            else:
                suelta += 1
        elif n in ("MSH", "SFT", "EVN", "PID", "PD1", "PV1", "PV2"):
            ctx = None
    return {"ordenes": ordenes, "docs": docs, "obx_fuera_txa": fuera, "nte_suelta": suelta}


def _tipo_obx(m, o):
    return _d(m, _f(m, o["seg"], 2)).upper()


def _octetos(ed4, ed5):
    """§4.2: los octetos de ED.5 según ED.4 (ED.5 ya desescapado, [E2A CH02A.txt:1861-1876]) -> (bytes | None, motivo)."""
    e4 = (ed4 or "").upper()
    if e4 == "BASE64":
        try:
            return base64.b64decode(re.sub(r"\s", "", ed5), validate=True), None
        except (binascii.Error, ValueError):
            return None, "invalido"
    if e4 == "HEX":
        try:
            return bytes.fromhex(ed5), None
        except ValueError:
            return None, "invalido"
    if e4 == "A":
        try:
            return ed5.encode("ascii"), None
        except UnicodeEncodeError:
            return None, "no_ascii"
    return None, "invalido"


def imposibles(m):
    """§2.3: los valores imposibles de un MDM (fijan el rechazo aceptable, Q-CV-D-7). Los de tabla, solo en 2.5 (L18)."""
    out = CV._imposibles(m, "mdm")                                    # PID-7, PID-8 y OBX-5 NM, como en ADT y ORU
    v25 = _comp(m, _f(m, m.segs[0], 12), 1) in ("2.5", "")
    for i, txa in enumerate(m.segmentos("TXA"), 1):
        v = lambda n: _t(m, (_reps(m, _f(m, txa, n)) or [""])[0], 1)  # noqa: E731
        for n in (2, 12, 17):                                         # R en 2.5 ([E9 CH09.txt:823-839])
            if not v(n):
                out.append(_hecho("TXA", i, n))
        if v(6) and MR.partes_dtm(v(6))[0] is None:
            out.append(_hecho("TXA", i, 6))
        if v25:
            for n, tabla in ((3, T0191), (17, T0271), (18, T0272), (19, T0273)):
                if v(n) and v(n).upper() not in tabla:
                    out.append(_hecho("TXA", i, n))
    for k, s in enumerate(m.segmentos("OBX"), 1):
        t2 = _d(m, _f(m, s, 2)).upper()
        if v25 and t2 and t2 not in T0125:
            out.append(_hecho("OBX", k, 2))
        if t2 == "ED":
            for rep in _reps(m, _f(m, s, 5)):
                ed5 = _d(m, _comp(m, rep, 5))
                if ed5 and _octetos(_t(m, rep, 4), ed5)[1] == "invalido":
                    out.append(_hecho("OBX", k, 5))
                    break
    return out


def recuentos(m, lec):
    """§2.4: lo propio de la familia, sin datos personales (ni el texto ni el Base64 entran)."""
    g = grupos(m)
    por_tipo = collections.Counter()
    sin, reps = 0, 0
    for d in g["docs"]:
        for o in d["obx"]:
            t = _tipo_obx(m, o)
            por_tipo[t if t in CON_DESTINO else "otros"] += 1
            sin += t not in CON_DESTINO
            if t in ("ED", "RP"):
                reps += len(_reps(m, _f(m, o["seg"], 5)))
    txas = m.segmentos("TXA")
    v = lambda s, n: _t(m, (_reps(m, _f(m, s, n)) or [""])[0], 1) or "vacío"  # noqa: E731
    info = lec.get("mdm") or {}
    docs = [x["entry"] for x in lec["recursos"] if x["rol"].startswith("DocumentReference#") and x["entry"]]
    docs += [y for ys in (info.get("duplicadas") or {}).values() for y in ys]
    atts = [c.get("attachment") for y in docs for c in y["r"].get("content") or [] if isinstance(c, dict)]
    atts = [a for a in atts if isinstance(a, dict)]
    texto = [a for a in atts if a.get("data") is not None and (_mime(a.get("contentType")).startswith("text/") or _mime(a.get("contentType")) == "application/text")]
    return {"txa": len(txas), "obx": len(m.segmentos("OBX")), "obx_por_tipo": dict(sorted(por_tipo.items())), "obx_sin_destino": sin,
            "obx_fuera_txa": g["obx_fuera_txa"], "repeticiones_obx5": reps, "nte_obx": sum(len(o["nte"]) for d in g["docs"] for o in d["obx"]),
            "nte_obr": sum(len(o["nte"]) for o in g["ordenes"]), "grupos_orden": len(g["ordenes"]),
            "ordenes_distintas": len(set(orden_de(m, g["ordenes"])[0].values())),
            "txa_por_completitud": dict(sorted(collections.Counter(v(s, 17) for s in txas).items())),
            "txa_por_disponibilidad": dict(sorted(collections.Counter(v(s, 19) for s in txas).items())),
            "content_observado": sum(len([c for c in y["r"].get("content") or [] if isinstance(c, dict)]) for y in docs),
            "attachments_texto": len(texto), "attachments_binarios": sum(1 for a in atts if a.get("data") is not None) - len(texto),
            "attachments_con_url": sum(1 for a in atts if a.get("url"))}


# ---------------------------------------------------------------------------- emparejamiento (§2.2)
def _mi(e):
    x = e["r"].get("masterIdentifier")
    return (x.get("value") or "") if isinstance(x, dict) and isinstance(x.get("value"), str) else ""


def _tiene_master(e, t12):
    return bool(t12) and (t12 in _mi(e) or t12 in _valores(e["r"]))


def emparejar(m, entries, top, out, pat, rol, usados):
    """Gancho 2 de conversion.emparejar, tras el Patient. DocumentReference por TXA: (1) TXA-12.1 en masterIdentifier o en un
    identifier, (2) TXA-16 en un identifier, (3) TXA-2.1 en type, (4) la única o tantas como TXA; cada clave para todos los TXA
    antes de la siguiente, y dos candidatas igual de buenas son ambiguas. Con un solo TXA: la que lleva TXA-12, o la primera, y las
    demás son duplicadas (su content se suma, AMB-MD-18). ServiceRequest por grupo de orden: (1) números de PLAC/FILL (gana quien
    comparte más; empate, OBR-4: DV-MD-1), (2) referido desde context.related y con OBR-4, (3) OBR-4, (4) tantos como grupos.
    Encounter por PV1, como en adt_conv. Un Binary al que lleva attachment.url no es otros_tipos."""
    g = grupos(m)
    docs, ordenes = g["docs"], g["ordenes"]
    info = {"grupos": g, "duplicadas": {}, "varias": False}
    out["mdm"] = info
    drs = [e for e in top if e["tipo"] == "DocumentReference"]
    claves = {i: (_t(m, _f(m, d["txa"], 12), 1), _d(m, _f(m, d["txa"], 16)), _t(m, (_reps(m, _f(m, d["txa"], 2)) or [""])[0], 1))
              for i, d in enumerate(docs, 1)}
    asignadas, por_i, libres = {}, {}, list(drs)
    if len(docs) == 1:
        c = [e for e in drs if _tiene_master(e, claves[1][0])]
        if len(c) == 1:
            asignadas[1], por_i[1] = c[0], "master"
        elif drs:
            asignadas[1], por_i[1] = (c or drs)[0], "unico" if len(drs) == 1 else "orden"
            info["varias"] = len(drs) > 1
        if asignadas.get(1):
            libres.remove(asignadas[1])
    else:
        for paso in ("master", "archivo", "tipo", "orden"):
            for i, (t12, t16, t2) in claves.items():
                if i in asignadas:
                    continue
                if paso == "master":
                    c = [e for e in libres if _tiene_master(e, t12)]
                elif paso == "archivo":
                    c = [e for e in libres if t16 and t16 in _valores(e["r"])]
                elif paso == "tipo":
                    c = [e for e in libres if t2 and t2 in {x[1] for x in _codigos(e["r"].get("type"))}]
                else:
                    c = libres[:1] if (len(drs) == len(docs) or len(drs) == 1) and libres else []
                if len(c) > 1:
                    out["ambiguo"].append("DocumentReference#%d" % i)
                    asignadas[i] = None
                elif c:
                    libres.remove(c[0])
                    asignadas[i], por_i[i] = c[0], paso
    for i in claves:
        rol("DocumentReference#%d" % i, "TXA %d" % i, asignadas.get(i), por_i.get(i), len(drs))
    for e in libres:
        dueno = (1 if asignadas.get(1) else None) if len(docs) == 1 else next(
            (i for i, (t12, t16, _) in claves.items() if asignadas.get(i) and (_tiene_master(e, t12) or (t16 and t16 in _valores(e["r"])))), None)
        if dueno:
            info["duplicadas"].setdefault(dueno, []).append(e)
            out["sobrantes"].append({"resourceType": "DocumentReference", "fullUrl": e["fullUrl"], "motivo": "duplicado",
                                     "hecho": _hecho("TXA", dueno, 12)})
        else:
            out["sobrantes"].append({"resourceType": "DocumentReference", "fullUrl": e["fullUrl"], "motivo": "inventado", "hecho": "TXA"})
        usados.add(e["i"])
    srs = [e for e in top if e["tipo"] == "ServiceRequest"]
    referidos = set()
    for d in [x for x in asignadas.values() if x] + [y for ys in info["duplicadas"].values() for y in ys]:
        ctx = d["r"].get("context") if isinstance(d["r"].get("context"), dict) else {}
        for ref in ctx.get("related") or []:
            x, _ = CV.resolver(entries, ref, d, "ServiceRequest")
            if x is not None:
                referidos.add(x["i"])
    canon, mult = orden_de(m, ordenes)                               # DV-MD-13 (H22): un grupo repetido es la misma orden
    info["orden_de"], info["repetidos"], info["padres"] = canon, {}, []
    sclaves = {i: ({_t(m, _f(m, o["obr"], 2), 1), _t(m, _f(m, o["obr"], 3), 1), _t(m, _f(m, o["orc"], 2), 1), _t(m, _f(m, o["orc"], 3), 1)} - {""},
                   _t(m, _f(m, o["obr"], 4), 1)) for i, o in enumerate(ordenes, 1) if canon[i] == i}
    sasig, spor, slibres = {}, {}, list(srs)
    for paso in ("identifier", "referencia", "codigo", "orden"):
        for i, (ids, cod) in sclaves.items():
            if i in sasig:
                continue
            con_cod = [e for e in slibres if cod and cod in {x[1] for x in _codigos(e["r"].get("code"))}]
            if paso == "identifier":                                 # DV-MD-1: gana quien comparte más números; empate, OBR-4
                puntos = {e["i"]: len(ids & _valores(e["r"])) for e in slibres}
                mx = max(puntos.values(), default=0)
                c = [e for e in slibres if mx and puntos[e["i"]] == mx]
                if len(c) > 1 and cod:
                    c = [e for e in c if e in con_cod] or c
            elif paso == "referencia":
                c = [e for e in con_cod if e["i"] in referidos]
            elif paso == "codigo":
                c = con_cod
            else:
                c = slibres[:1] if len(srs) == len(sclaves) and slibres else []
            if len(c) > 1 and mult[i] > 1:                           # DV-MD-13: los iguales de una orden repetida no son ambiguos
                for e in c:
                    slibres.remove(e)
                info["repetidos"][i] = c[1:mult[i]]
                for e in c[mult[i]:]:
                    out["sobrantes"].append({"resourceType": "ServiceRequest", "fullUrl": e["fullUrl"], "motivo": "duplicado",
                                             "hecho": _hecho("ORC", i, 1)})
                for e in c[1:]:
                    usados.add(e["i"])
                sasig[i], spor[i] = c[0], paso
            elif len(c) > 1:
                out["ambiguo"].append("ServiceRequest#%d" % i)
                sasig[i] = None
            elif c:
                slibres.remove(c[0])
                sasig[i], spor[i] = c[0], paso
    for i in sclaves:
        rol("ServiceRequest#%d" % i, "ORC %d" % i, sasig.get(i), spor.get(i), len(srs))
    padres = {v for o in ordenes for s, n in ((o["obr"], 29), (o["orc"], 8)) for v in (_t(m, _f(m, s, n), 1), _t(m, _f(m, s, n), 2)) if v}
    hijos = [x for x in sasig.values() if x]
    for e in slibres:                                                # DV-MD-12 (H21): el padre, por basedOn y con el número de OBR-29/ORC-8
        if padres & _valores(e["r"]) and any(CV.resolver(entries, ref, x, "ServiceRequest")[0] is e for x in hijos
                                             for ref in x["r"].get("basedOn") or [] if isinstance(ref, dict)):
            info["padres"].append(e)
        else:
            out["sobrantes"].append({"resourceType": "ServiceRequest", "fullUrl": e["fullUrl"], "motivo": "inventado", "hecho": "ORC"})
        usados.add(e["i"])
    _emparejar_encounter(m, entries, top, out, pat, rol, usados)
    for d in [x for x in asignadas.values() if x] + [y for ys in info["duplicadas"].values() for y in ys]:   # R-MD-29
        for c in d["r"].get("content") or []:
            a = c.get("attachment") if isinstance(c, dict) else None
            if isinstance(a, dict) and isinstance(a.get("url"), str) and a["url"]:
                x, _ = CV.resolver(entries, {"reference": a["url"]}, d, "Binary")
                if x is not None and x["tipo"] == "Binary":
                    usados.add(x["i"])


def orden_de(m, ordenes):
    """DV-MD-13 (H22): dos grupos de orden con el mismo número de orden (ORC-2.1 u OBR-2.1, valorado) e iguales en ORC-3, OBR-2, OBR-3 y
    OBR-4 son la misma orden: el número de placer «identifies an order uniquely» ([E4 CH04.txt:2353-2365]). -> ({i: el primero de los
    suyos}, {i: cuántos grupos la repiten})"""
    canon, mult, vistos = {}, {}, {}
    for i, o in enumerate(ordenes, 1):
        clave = (_t(m, _f(m, o["orc"], 2), 1) or _t(m, _f(m, o["obr"], 2), 1), _t(m, _f(m, o["orc"], 3), 1), _t(m, _f(m, o["obr"], 2), 1),
                 _t(m, _f(m, o["obr"], 3), 1), _t(m, _f(m, o["obr"], 4), 1))
        if clave[0] and clave in vistos:
            canon[i] = vistos[clave]
            mult[vistos[clave]] += 1
        else:
            vistos[clave] = canon[i] = i
            mult[i] = 1
    return canon, mult


def _emparejar_encounter(m, entries, top, out, pat, rol, usados):
    """Copia de conversion_vxu._emparejar_encounter (un cambio de VXU no debe mover MDM, §3): como la rama adt; sin PV1, un
    Encounter no tiene origen."""
    pv1 = _seg(m, "PV1")
    encs = [e for e in top if e["tipo"] == "Encounter"]
    en = None
    if pv1 is not None:
        v19 = _t(m, _f(m, pv1, 19), 1)
        por = None
        if len(encs) == 1:
            en, por = encs[0], "unico"
        elif encs:
            s = [e for e in encs if pat is not None and CV.resolver(entries, e["r"].get("subject"), e, "Patient")[0] is pat]
            si = [e for e in s if v19 and v19 in _valores(e["r"])]
            solo_id = [e for e in encs if v19 and v19 in _valores(e["r"])]
            if len(si) == 1:
                en, por = si[0], "identifier"
            elif len(s) == 1:
                en, por = s[0], "referencia"
            elif len(solo_id) == 1:
                en, por = solo_id[0], "identifier"
            else:
                out["ambiguo"].append("Encounter#1")
        rol("Encounter#1", "PV1", en, por, len(encs))
    for e in encs:
        if e is en or (pv1 is not None and en is None):
            continue
        out["sobrantes"].append({"resourceType": "Encounter", "fullUrl": e["fullUrl"], "motivo": "duplicado" if pv1 is not None else "inventado",
                                 "hecho": "PV1"})
        usados.add(e["i"])


# ---------------------------------------------------------------------------- el juicio (§4)
def juzgar(J, m, lec, pat_entry):
    """Gancho 6 de conversion._juzgar (el Patient ya está juzgado). Juzga también los sobrantes, con sus citas, y deja la lista vacía."""
    roles = {x["rol"]: x for x in lec["recursos"]}
    info = lec.get("mdm") or {"grupos": grupos(m), "duplicadas": {}, "varias": False}
    g = info["grupos"]
    msh = m.segs[0]
    ev = (_comp(m, _f(m, msh, 9), 2) or "").upper()
    if ev != "T02":
        _nota(J, "evento", "MSH-9", "MDM^%s con el perfil de T02 (alternativa de Q-MD-D-1): la semántica de cambio de estado no se juzga (L-MD-8)" % ev)
    if not _comp(m, _f(m, msh, 9), 3):
        _nota(J, "estructura_declarada", "MSH-9", "MSH-9.3 vacío: se lee con la estructura del evento (§2.3; nunca cuenta, L-MD-13)")
    if g["obx_fuera_txa"]:
        _nota(J, "fuera_proyeccion", "OBX", "%d OBX antes del TXA: fuera de la estructura, solo se cuentan (L-MD-9)" % g["obx_fuera_txa"])
    for i, o in enumerate(g["ordenes"], 1):
        if o["sin_orc"]:
            _nota(J, "estructura", _hecho("ORC", i, 1), "OBR sin ORC delante: se espera su ServiceRequest (ORC es R, [E4 CH04.txt:1823])")
        elif o["obr"] is None:
            _nota(J, "estructura", _hecho("ORC", i, 1), "ORC sin OBR: se espera su ServiceRequest ([E9 CH09.txt:322-343])")
    pv1 = _seg(m, "PV1")
    en = roles.get("Encounter#1")
    en_entry = en["entry"] if en else None
    if pv1 is not None and "Encounter#1" not in lec["ambiguo"]:          # R-MD-44: las reglas de adt_conv
        if en_entry is None:
            if _t(m, _f(m, pv1, 2), 1) == "N" and J.dec["Q-CV-D-6"] != "recurso_ausente":
                _nota(J, "convencion", "PV1", "sin Encounter con PV1-2 = N (AMB-CV-5, alternativa de Q-CV-D-6)")
            else:
                _cuenta(J, "recurso_ausente", "PV1", "falta el Encounter del PV1", citas=C_SEG["PV1"])
        else:
            CV._encounter(J, m, pv1, en_entry["r"], lec["entries"], pat_entry, en_entry)
    for i, d in enumerate(g["docs"], 1):
        if i > 1:
            _nota(J, "estructura", _hecho("TXA", i, 1), "segundo TXA: fuera de la estructura (TXA 1..1); se espera su DocumentReference (L-MD-9)")
        if not d["obx"]:
            _nota(J, "estructura", _hecho("TXA", i, 1), "TXA sin OBX (el grupo OBX es obligatorio): no se espera content ([E9 CH09.txt:345-354])")
        x = roles.get("DocumentReference#%d" % i)
        e = x["entry"] if x else None
        if e is None:
            if "DocumentReference#%d" % i not in lec["ambiguo"]:
                _cuenta(J, "recurso_ausente", _hecho("TXA", i, 12), "falta la DocumentReference del TXA %d" % i, citas=C_MDM["TXA"])
            continue
        if i == 1 and info.get("varias"):
            _nota(J, "varias_candidatas", _hecho("TXA", i, 12), "un TXA y varias DocumentReference sin TXA-12 que las distinga: la primera (AMB-MD-18)")
        _documento(J, m, d, i, e, info["duplicadas"].get(i, []), pat_entry, en_entry, pv1, roles, g)
    canon = info.get("orden_de") or {i: i for i in range(1, len(g["ordenes"]) + 1)}
    for i, o in enumerate(g["ordenes"], 1):
        if canon[i] != i:                                            # DV-MD-13 (H22)
            _nota(J, "orden_repetida", _hecho("ORC", i, 2), "grupo de orden %d igual al %d, con el mismo número de orden: una sola orden "
                  "([E4 CH04.txt:2353-2365]); basta un ServiceRequest" % (i, canon[i]))
            continue
        for y in (info.get("repetidos") or {}).get(i, []):
            _nota(J, "orden_repetida", _hecho("ORC", i, 1), "ServiceRequest %s: otro para la orden repetida %d (la guía crea uno por ORC)" % (y["fullUrl"], i))
        x = roles.get("ServiceRequest#%d" % i)
        e = x["entry"] if x else None
        if e is None:
            if "ServiceRequest#%d" % i not in lec["ambiguo"]:
                _cuenta(J, "recurso_ausente", _hecho("ORC", i, 1), "falta el ServiceRequest del grupo de orden %d" % i, citas=C_MDM["SR"])
            continue
        _servicio(J, m, o, i, e, pat_entry)
    for y in info.get("padres") or []:                                # DV-MD-12 (H21)
        _nota(J, "pedido_padre", "OBR-29", "ServiceRequest %s: el pedido padre (OBR-29 u ORC-8), referenciado desde basedOn "
              "([G OBR_ServiceRequest.csv:43-46])" % y["fullUrl"])
    for s in lec["sobrantes"]:
        cit = {"DocumentReference": C_MDM["TXA"], "ServiceRequest": C_MDM["SR"], "Encounter": C_SEG["PV1"], "Patient": C_SEG["PID"]}
        _cuenta(J, "recurso_%s" % s["motivo"], s["hecho"], "%s %s sin origen propio en el mensaje" % (s["resourceType"], s["fullUrl"]),
                citas=cit.get(s["resourceType"]) or _cit(s["hecho"]))
    lec["sobrantes"] = []
    obs = {t: n for t, n in lec["otros_tipos"].items() if t in ("Observation", "DiagnosticReport")}   # R-MD-36 (Q-MD-D-8)
    if obs:
        if _dec(J, "Q-MD-D-8") == "inventado":
            for t, n in sorted(obs.items()):
                for _ in range(n):
                    _cuenta(J, "recurso_inventado", "OBX", "%s en el Bundle: la guía lleva el OBX a la DocumentReference (alternativa de Q-MD-D-8)" % t,
                            citas=C_MDM["OBX-obs"])
        else:
            _nota(J, "fuera_proyeccion", "OBX", "%r en el Bundle: la guía lleva el OBX a la DocumentReference; otros_tipos (Q-MD-D-8, L-MD-3)" % obs)
    for h in J.hs:                                                   # el Patient ausente lo juzgó la parte común, con la cita de ADT
        if h["hecho"] == "PID" and h["citas"] == CV.C["PID"]:
            h["citas"] = list(C_SEG["PID"])


def _documento(J, m, d, i, e, dups, pat_entry, en_entry, pv1, roles, g):
    txa, r = d["txa"], e["r"]
    h = lambda n: _hecho("TXA", i, n)  # noqa: E731
    _maestro(J, m, txa, r, e, h)
    _archivo(J, m, txa, r, h)
    _tipo(J, m, txa, r, h)
    _estado(J, m, txa, r, h)
    _doc_status(J, m, txa, r, h, d, g)
    _etiqueta(J, m, txa, r, h)
    _fecha_doc(J, m, txa, r, h)
    _profesionales(J, m, txa, r, e, h)
    _referencias(J, m, i, r, e, pat_entry, en_entry, pv1, roles, g)
    _contenido(J, m, d, i, e, dups, h)


def _rep1(m, seg, n):
    return (_reps(m, _f(m, seg, n)) or [""])[0]


def _maestro(J, m, txa, r, e, h):
    """R-MD-3 y R-MD-4: TXA-12.1 → masterIdentifier.value; EI.2/EI.3 en system o assigner (forma: convención, como CX.4)."""
    rep = _rep1(m, txa, 12)
    v = _t(m, rep, 1)
    mi = r.get("masterIdentifier") if isinstance(r.get("masterIdentifier"), dict) else None
    hecho, c = h(12), C_MDM["TXA-12"]
    if not v:                                                        # MD1-e: la regla es de .value; sin EI.1, system o assigner solos no
        if mi and mi.get("value"):                                   # inventan nada (CV._identifier tampoco mira CX.4 sin CX.1)
            de = [n for n, x in (("EI.2", _t(m, rep, 2)), ("EI.3", _t(m, rep, 3))) if x and x == mi["value"]]
            _cuenta(J, "dato_inventado", hecho, "DocumentReference.masterIdentifier.value %r sin TXA-12.1%s" % (
                mi["value"], " (EI.1 vacío; el valor es %s)" % de[0] if de else ""), citas=c)
        return
    if mi is None or not mi.get("value"):
        _cuenta(J, "dato_perdido", hecho, "DocumentReference.masterIdentifier: falta %r (TXA-12.1)" % v, citas=c)
        return
    if mi["value"] != v:
        _cuenta(J, "valor_distinto", hecho, "DocumentReference.masterIdentifier.value: esperado %r, observado %r" % (v, mi["value"]), citas=c)
        return
    ns, uid = _t(m, rep, 2), _t(m, rep, 3)
    if not (ns or uid):
        return
    a = mi.get("assigner") if isinstance(mi.get("assigner"), dict) else {}
    textos = [mi.get("system") or "", a.get("display") or "", a.get("reference") or "",
              ((a.get("identifier") or {}).get("value") or "") if isinstance(a.get("identifier"), dict) else ""]
    if a.get("reference"):
        ae, _ = CV.resolver(J.entries, a, e, "Organization")
        if ae:
            textos += [ae["r"].get("name") or ""] + list(_valores(ae["r"]))
            J.referidas.add(ae["i"])
    nsn, uidn = CV._plano(ns), CV._plano(uid)
    if not any((nsn and nsn in CV._plano(t)) or (uidn and uidn in CV._plano(t)) for t in textos):
        _cuenta(J, "dato_perdido", hecho, "DocumentReference.masterIdentifier %r: EI.2/EI.3 %r sin system ni assigner" % (v, [x for x in (ns, uid) if x]),
                citas=c)


def _archivo(J, m, txa, r, h):
    """R-MD-5: TXA-16 desescapado y entero (la ruta completa) en un identifier; truncado o sin desescapar, valor distinto."""
    raw = _f(m, txa, 16)
    v = _d(m, raw)
    vals = [x.get("value") for x in r.get("identifier") or [] if isinstance(x, dict)]
    hecho, c = h(16), C_MDM["TXA-16"]
    usados = set()
    if v:
        k = next((k for k, x in enumerate(vals) if x == v), None)
        if k is None:
            k = next((k for k, x in enumerate(vals) if isinstance(x, str) and x and (x == raw or (len(x) < len(v) and v.endswith(x) and v[-len(x) - 1] in "/\\:"))), None)
            if k is not None:
                _cuenta(J, "valor_distinto", hecho, "DocumentReference.identifier: esperado %r (TXA-16 entero y desescapado), observado %r" % (v, vals[k]), citas=c)
            else:
                _cuenta(J, "dato_perdido", hecho, "DocumentReference.identifier: falta %r (TXA-16)" % v, citas=c)
        if k is not None:
            usados.add(k)
    extra = [x for k, x in enumerate(vals) if k not in usados]
    if extra:
        _reusa(J, c, CV._extra, J, m, hecho, "DocumentReference.identifier de más: %r" % extra, extra)


def _tipo(J, m, txa, r, h):
    """R-MD-6: TXA-2.1 (IS de la 0270, definida por el usuario) en type.coding.code; system, display y text: convención o forma."""
    v = _t(m, _rep1(m, txa, 2), 1)
    cc = r.get("type")
    codes = [x[1] for x in _codigos(cc)]
    hecho, c = h(2), C_MDM["TXA-2"]
    if not v:
        if cc is not None:
            _cuenta(J, "dato_inventado", hecho, "DocumentReference.type %r sin TXA-2" % (codes or cc), citas=c)
        return
    if not codes:
        _cuenta(J, "dato_perdido", hecho, "DocumentReference.type: falta el código %r (observado %r)" % (v, cc), citas=c)
    elif v not in codes:
        if v.upper() in {(x or "").upper() for x in codes}:
            _nota(J, "convencion", hecho, "DocumentReference.type: %r en otra caja (AMB-CV-1)" % codes, "ambiguedad AMB-CV-1")
        else:
            _cuenta(J, "valor_distinto", hecho, "DocumentReference.type: falta el código %r (observado %r)" % (v, codes), citas=c)
    elif len(codes) > 1:
        _nota(J, "extra", hecho, "DocumentReference.type: codings de más %r" % [x for x in codes if x != v])


def _alternos(prim):
    """Los códigos de status.extension[alternate-codes] (`_status` en JSON): valueCodeableConcept, valueCoding o valueCode."""
    out = set()
    for x in (prim or {}).get("extension") or [] if isinstance(prim, dict) else []:
        if not isinstance(x, dict) or x.get("url") not in ALTERNATE:
            continue
        out |= {c for _, c in _codigos(x.get("valueCodeableConcept")) if c}
        vc = x.get("valueCoding")
        if isinstance(vc, dict) and vc.get("code"):
            out.add(vc["code"])
        if isinstance(x.get("valueCode"), str):
            out.add(x["valueCode"])
    return {c.upper() for c in out if isinstance(c, str)}


def _estado(J, m, txa, r, h):
    """R-MD-7 y R-MD-8: TXA-19 vacío o AV → current; CA, OB, UN → el código en status.extension[alternate-codes] o, para CA y OB,
    en un status coherente; con Q-MD-D-9 (b) el status de CA y OB debe ser además el coherente."""
    c19 = _t(m, _rep1(m, txa, 19), 1).upper()
    st = r.get("status")
    hecho, c = h(19), C_MDM["TXA-19"]
    valido = st in DOCREF_STATUS
    if not valido:
        _cuenta(J, "fhir_invalido", hecho, "DocumentReference.status: %r (1..1, required)" % st, citas=c)
    if c19 in ("", "AV"):
        if valido and st != "current":
            _cuenta(J, "valor_distinto", hecho, "DocumentReference.status: esperado 'current' (TXA-19 %s), observado %r" % (c19 or "vacío", st), citas=c)
    elif c19 in ("CA", "OB", "UN"):
        coh = COHERENTE_0273.get(c19)
        perdido = c19 not in _alternos(r.get("_status")) and not (coh and st == coh)
        if coh and valido and st != coh and _dec(J, "Q-MD-D-9") == "extension_y_coherente":     # DV-MD-11 (H20): una cuenta
            _cuenta(J, "valor_distinto", hecho, "DocumentReference.status: con TXA-19 %r se espera %r (Q-MD-D-9), observado %r%s" % (
                c19, coh, st, "; y el código no se conserva en status.extension[alternate-codes]" if perdido else ""), citas=c)
        elif perdido:
            _cuenta(J, "dato_perdido", hecho, "DocumentReference.status %r: TXA-19 %r no se conserva (ni status coherente ni "
                    "status.extension[alternate-codes])" % (st, c19), citas=c)
    elif valido:
        _nota(J, "fuera_de_tabla" if J.v25 else "version", hecho, "DocumentReference.status %r con TXA-19 %r fuera de la 0273" % (st, c19))


def _conservado(r, c):
    """¿Está el código de TXA-17 en alguna extensión de la DocumentReference (de docStatus o del recurso)?"""
    exts = [x for x in ((r.get("_docStatus") or {}).get("extension") or []) + (r.get("extension") or []) if isinstance(x, dict)]
    for x in exts:
        vals = [x.get("valueCode"), x.get("valueString"), (x.get("valueCoding") or {}).get("code") if isinstance(x.get("valueCoding"), dict) else None]
        vals += [cd for _, cd in _codigos(x.get("valueCodeableConcept"))]
        if any(isinstance(v, str) and v.upper() == c for v in vals):
            return True
    return False


def _doc_status(J, m, txa, r, h, d=None, g=None):
    """R-MD-9: conjunto E(c) = {c literal} ∪ MAPA_0271(c). El literal, según Q-MD-D-4 (b: además fhir_invalido; c: nota)."""
    c = _t(m, _rep1(m, txa, 17), 1)
    cu = c.upper()
    obs = r.get("docStatus")
    hecho, cit = h(17), C_MDM["TXA-17"]
    if not c:
        if obs is not None:                                          # DV-MD-9 (H10): el de OBX-11 u OBR-25 por su ConceptMap es nota
            de = [("OBX-11", x) for x in (_d(m, _f(m, o["seg"], 11)) for o in (d or {}).get("obx", [])) if x and CV.mapa("0085", x) not in (None, FUERA)
                  and CV.mapa("0085", x)[1] == obs]
            de += [("OBR-25", x) for x in (_d(m, _f(m, o["obr"], 25)) for o in (g or {}).get("ordenes", [])) if x and CV.mapa("0123", x) not in (None, FUERA)
                   and CV.mapa("0123", x)[1] == obs]
            if de:
                _nota(J, "convencion", hecho, "DocumentReference.docStatus %r sin TXA-17: es el de %s %r por su ConceptMap (DV-MD-9)" % (obs, de[0][0], de[0][1]))
            else:
                _cuenta(J, "dato_inventado", hecho, "DocumentReference.docStatus %r sin TXA-17" % obs, citas=cit)
        return
    if cu not in MAPA_0271:                                          # fuera de la 0271: imposible en 2.5
        if obs is not None:
            _cuenta(J, "valor_imposible_convertido", hecho, "DocumentReference.docStatus %r convertido desde TXA-17 %r, fuera de la 0271" % (obs, c),
                    clase="valor_imposible_aceptado", tabla=True, citas=cit)
            if obs not in COMPOSITION_STATUS:
                _cuenta(J, "fhir_invalido", hecho, "DocumentReference.docStatus %r fuera de composition-status (required)" % obs, citas=cit)
        return
    if obs is None:
        if _conservado(r, cu):
            _nota(J, "convencion", hecho, "DocumentReference.docStatus ausente; TXA-17 %r conservado en una extensión" % c)
        else:
            _cuenta(J, "dato_perdido", hecho, "DocumentReference.docStatus: falta (TXA-17 %r; admitidos %r)" % (c, sorted(MAPA_0271[cu] | {c})), citas=cit)
        return
    if obs in MAPA_0271[cu]:
        _nota(J, "convencion", hecho, "DocumentReference.docStatus %r para TXA-17 %r: mapa semántico 0271 → composition-status (AMB-MD-3, L-MD-6)" % (obs, c),
              "ambiguedad AMB-MD-3")
    elif isinstance(obs, str) and obs.upper() == cu:
        if _dec(J, "Q-MD-D-4") == "literal_o_mapa_y_literal_invalido":
            _cuenta(J, "fhir_invalido", hecho, "DocumentReference.docStatus %r: el literal de la guía no está en composition-status (required; Q-MD-D-4)" % obs,
                    citas=cit)
        else:
            _nota(J, "literal_de_la_guia", hecho, "DocumentReference.docStatus %r: el literal de la guía ($value; alternativa de Q-MD-D-4)" % obs)
    elif obs in COMPOSITION_STATUS:
        _cuenta(J, "valor_distinto", hecho, "DocumentReference.docStatus: esperado uno de %r (TXA-17 %r), observado %r" % (sorted(MAPA_0271[cu] | {c}), c, obs),
                citas=cit)
    else:
        _cuenta(J, "fhir_invalido", hecho, "DocumentReference.docStatus %r fuera de composition-status (required)" % obs, citas=cit)
        _cuenta(J, "valor_distinto", hecho, "DocumentReference.docStatus: esperado uno de %r (TXA-17 %r), observado %r" % (sorted(MAPA_0271[cu] | {c}), c, obs),
                citas=cit)


def _etiqueta(J, m, txa, r, h):
    """R-MD-10: TXA-18 → securityLabel {v2-0272, código} (guía) o {v3-Confidentiality, código} (binding extensible, AMB-MD-20)."""
    v = _t(m, _rep1(m, txa, 18), 1)
    obs = [x for s in r.get("securityLabel") or [] for x in _codigos(s)]
    hecho, c = h(18), C_MDM["TXA-18"]
    if not v:
        if obs:
            _nota(J, "extra", hecho, "DocumentReference.securityLabel %r sin TXA-18" % obs)
        return
    t = MAPAS_MDM["table-hl70272-to-v2-0272"].get(v.upper())
    if t is None:
        if obs:
            _nota(J, "fuera_de_tabla" if J.v25 else "version", hecho, "DocumentReference.securityLabel %r para TXA-18 %r, fuera de la 0272" % (obs, v))
        return
    admitidos = {tuple(t), (V3_CONF, t[1])}
    if any(x in admitidos for x in obs):
        if len(obs) > 1:
            _nota(J, "extra", hecho, "DocumentReference.securityLabel de más: %r" % [x for x in obs if x not in admitidos])
    elif any((s, (cd or "").upper()) in admitidos for s, cd in obs):
        _nota(J, "convencion", hecho, "DocumentReference.securityLabel %r en otra caja (AMB-CV-1)" % obs, "ambiguedad AMB-CV-1")
    elif not obs:
        _cuenta(J, "dato_perdido", hecho, "DocumentReference.securityLabel: falta %r (TXA-18 %r)" % (t, v), citas=c)
    else:
        _cuenta(J, "codigo_mal_mapeado", hecho, "DocumentReference.securityLabel: esperado %r o %r, observado %r" % (tuple(t), (V3_CONF, t[1]), obs), citas=c)


def _misma_fecha(m, origen, obs):
    """Un TS del mensaje frente a date con la regla de fechas del juez: igual si no dejaría hallazgo que cuente."""
    if not origen or not isinstance(obs, str):
        return False
    sub = CV.Juicio(m, True, CV.DECISIONES)
    sub.entries = []
    CV._fecha(sub, "TXA-6", origen, obs, "instant", "DocumentReference.date")
    return not any(x["cuenta"] for x in sub.hs)


def _fecha_doc(J, m, txa, r, h):
    """R-MD-11: con hora, instant (R-CV-7); solo fecha, ausente o completada (AMB-CV-9; la guía usa una extensión de R6); sin
    TXA-6, date presente es nota si coincide con MSH-7, EVN-2, TXA-4, TXA-7 o TXA-8 (AMB-MD-17), si no dato inventado."""
    v6 = _t(m, _rep1(m, txa, 6), 1)
    obs = r.get("date")
    hecho, c = h(6), C_MDM["TXA-6"]
    if not v6:
        if obs is None:
            return
        evn = _seg(m, "EVN")
        fuentes = [_t(m, _f(m, m.segs[0], 7), 1), _t(m, _f(m, evn, 2), 1), _t(m, _rep1(m, txa, 4), 1), _t(m, _rep1(m, txa, 7), 1)]
        fuentes += [_t(m, x, 1) for x in _reps(m, _f(m, txa, 8))]
        if any(_misma_fecha(m, f, obs) for f in fuentes if f):
            _nota(J, "convencion", hecho, "DocumentReference.date %r sin TXA-6: coincide con un TS del mensaje (AMB-MD-17)" % obs, "ambiguedad AMB-MD-17")
        else:
            _cuenta(J, "dato_inventado", hecho, "DocumentReference.date %r sin TXA-6" % obs, citas=c)
        return
    partes, _ = MR.partes_dtm(v6)
    if partes is None:
        if obs is not None:
            _cuenta(J, "valor_imposible_convertido", hecho, "DocumentReference.date %r convertido desde un DTM imposible %r" % (obs, v6),
                    clase="valor_imposible_aceptado", citas=c)
        return
    if partes[3] is None and obs is None:                            # solo fecha: la guía solo tiene la extensión de R6
        return
    _reusa(J, c, CV._fecha, J, hecho, v6, obs, "instant", "DocumentReference.date")


def _persona(J, ref, desde):
    """Copia de conversion_vxu._persona (§3): el Practitioner de un actor, directo, contained o tras PractitionerRole.practitioner."""
    x, forma = CV.resolver(J.entries, ref, desde, None)
    if x is not None and x["tipo"] == "PractitionerRole":
        J.referidas.add(x["i"])
        y, _ = CV.resolver(J.entries, x["r"].get("practitioner"), x, "Practitioner")
        return y, forma, "PractitionerRole"
    return x, forma, (x["tipo"] if x is not None else None)


def _nombre(r):
    n = r.get("name")
    return n[0] if isinstance(n, list) and n and isinstance(n[0], dict) else {}


def _xcn(m, rep):
    return _t(m, rep, 1), _d(m, _sub(m, _comp(m, rep, 2), 1)), _t(m, rep, 3)


def _profesionales(J, m, txa, r, e, h):
    """R-MD-12 (TXA-9 → author[]) y R-MD-13 (TXA-10 → authenticator, una repetición cualquiera: Q-MD-D-11)."""
    cit9, cit10 = C_MDM["TXA-9"], C_MDM["TXA-10"]
    obs = [a for a in r.get("author") or [] if isinstance(a, dict)]
    reps = [rep for rep in _reps(m, _f(m, txa, 9)) if _xcn(m, rep)[0] or _xcn(m, rep)[1]]
    usados = set()
    for rep in reps:
        x1, fam, g = _xcn(m, rep)
        mejor, rota, solo_display, otra = None, False, None, None
        for k, a in enumerate(obs):
            if k in usados:
                continue
            pr, forma, tipo = _persona(J, a, e)
            if pr is not None and pr["tipo"] == "Practitioner":
                ids, nom = _valores(pr["r"]), _nombre(pr["r"])
                if ((x1 and x1 in ids) or (fam and nom.get("family") == fam)) and mejor is None:
                    mejor = (k, pr, nom)
            elif pr is not None:
                otra = k if otra is None else otra
            elif forma == "logica" and x1 and (a.get("identifier") or {}).get("value") == x1:
                mejor = mejor or (k, None, {})
            elif forma == "rota":
                rota = True
            elif forma == "display" and ((fam and fam in (a.get("display") or "")) or (x1 and x1 in (a.get("display") or ""))):
                solo_display = k
        if mejor is None:
            if solo_display is not None:
                usados.add(solo_display)
                if x1:
                    _cuenta(J, "dato_perdido", h(9), "DocumentReference.author: solo display, falta el identificador %r" % x1, citas=cit9)
                else:
                    _nota(J, "convencion", h(9), "DocumentReference.author: solo display (sin XCN.1)")
            elif rota:
                _cuenta(J, "referencia_rota", h(9), "DocumentReference.author: la referencia no resuelve", citas=cit9 + CV.C["ref"])
            elif otra is not None:
                usados.add(otra)
                _cuenta(J, "dato_perdido", h(9), "DocumentReference.author: el autor no es una persona (XCN es un profesional)", citas=cit9)
            else:
                _cuenta(J, "dato_perdido", h(9), "DocumentReference.author: falta %r" % rep, citas=cit9)
            continue
        k, pr, nom = mejor
        usados.add(k)
        if pr is not None:
            J.referidas.add(pr["i"])
            _nombre_igual(J, h(9), "author", fam, g, nom, cit9)
    if len(obs) > len(usados):
        _nota(J, "extra", h(9), "DocumentReference.author de más: %d" % (len(obs) - len(usados)))
    a = r.get("authenticator") if isinstance(r.get("authenticator"), dict) else None
    reps = [rep for rep in _reps(m, _f(m, txa, 10)) if _xcn(m, rep)[0] or _xcn(m, rep)[1]]
    if not reps:
        if a is not None:
            if _de_txa22(J, m, txa, a, e):                           # DV-MD-8 (H8): la persona de TXA-22, con TXA-10 vacío
                _nota(J, "convencion", h(10), "DocumentReference.authenticator: la persona de TXA-22 (Authentication Person), con TXA-10 vacío (DV-MD-8)")
            else:
                _cuenta(J, "dato_inventado", h(10), "DocumentReference.authenticator %r sin TXA-10" % a, citas=cit10)
        return
    if a is None:
        _cuenta(J, "dato_perdido", h(10), "DocumentReference.authenticator: falta %r" % reps[0], citas=cit10)
        return
    esperadas = reps if _dec(J, "Q-MD-D-11") == "cualquiera" else reps[:1]
    pr, forma, _ = _persona(J, a, e)
    if pr is not None and pr["tipo"] == "Practitioner":
        J.referidas.add(pr["i"])
        ids, nom = _valores(pr["r"]), _nombre(pr["r"])
        cand = [rep for rep in esperadas if (_xcn(m, rep)[0] and _xcn(m, rep)[0] in ids) or (_xcn(m, rep)[1] and nom.get("family") == _xcn(m, rep)[1])]
        if not cand:
            _cuenta(J, "valor_distinto", h(10), "DocumentReference.authenticator: %r no es %s de TXA-10 %r (Q-MD-D-11)" % (
                sorted(ids) or nom.get("family"), "ninguna" if len(esperadas) > 1 else "la primera", esperadas), citas=cit10)
            return
        _, fam, g = _xcn(m, cand[0])
        _nombre_igual(J, h(10), "authenticator", fam, g, nom, cit10)
    elif pr is not None:
        _cuenta(J, "dato_perdido", h(10), "DocumentReference.authenticator: no es una persona (%s)" % pr["tipo"], citas=cit10)
    elif forma == "logica" and any(_xcn(m, rep)[0] == (a.get("identifier") or {}).get("value") for rep in esperadas):
        _nota(J, "convencion", h(10), "DocumentReference.authenticator: referencia lógica por identifier")
    elif forma == "rota":
        _cuenta(J, "referencia_rota", h(10), "DocumentReference.authenticator: la referencia no resuelve", citas=cit10 + CV.C["ref"])
    elif forma == "display" and not any(_xcn(m, rep)[0] for rep in esperadas):
        _nota(J, "convencion", h(10), "DocumentReference.authenticator: solo display (sin XCN.1)")
    else:
        _cuenta(J, "dato_perdido", h(10), "DocumentReference.authenticator: %s, falta el identificador de %r" % (forma, esperadas[0]), citas=cit10)


def _de_txa22(J, m, txa, a, e):
    """DV-MD-8 (H8): ¿es el authenticator la persona de TXA-22 (PPN.1 en identifier o PPN.2 en family; o solo display con ese apellido)?"""
    personas = [(_t(m, rep, 1), _d(m, _sub(m, _comp(m, rep, 2), 1))) for rep in _reps(m, _f(m, txa, 22))]
    personas = [(x1, fam) for x1, fam in personas if x1 or fam]
    if not personas:
        return False
    pr, forma, _ = _persona(J, a, e)
    if pr is not None and pr["tipo"] == "Practitioner":
        ids, nom = _valores(pr["r"]), _nombre(pr["r"])
        if any((x1 and x1 in ids) or (fam and nom.get("family") == fam) for x1, fam in personas):
            J.referidas.add(pr["i"])
            return True
        return False
    if forma == "logica":
        return any(x1 and x1 == (a.get("identifier") or {}).get("value") for x1, _ in personas)
    if forma == "display":
        return any((fam and fam in (a.get("display") or "")) or (x1 and x1 in (a.get("display") or "")) for x1, fam in personas)
    return False


def _nombre_igual(J, hecho, ruta, fam, g, nom, cit):
    if fam and nom.get("family") != fam:
        _cuenta(J, "valor_distinto", hecho, "DocumentReference.%s → Practitioner.name.family: esperado %r, observado %r" % (ruta, fam, nom.get("family")), citas=cit)
    if g and (nom.get("given") or [None])[0] != g:
        _cuenta(J, "valor_distinto", hecho, "DocumentReference.%s → Practitioner.name.given: esperado %r, observado %r" % (ruta, g, nom.get("given")), citas=cit)


def _referencias(J, m, i, r, e, pat_entry, en_entry, pv1, roles, g):
    """R-MD-15 (subject y context.encounter: presentes deben resolver; ausentes, nota: Q-MD-D-6) y R-MD-16 (context.related: una
    referencia por ServiceRequest emparejado, Q-MD-D-7)."""
    if r.get("subject") is None:
        if pat_entry is not None:
            if _dec(J, "Q-MD-D-6") == "dato_perdido":
                _cuenta(J, "dato_perdido", "PID-3", "DocumentReference.subject: falta (alternativa de Q-MD-D-6)", citas=C_MDM["DR-subject"])
            else:
                _nota(J, "sin_subject", "PID-3", "DocumentReference.subject ausente: la guía no tiene fila (Q-MD-D-6, L-MD-5)")
    else:
        _reusa(J, C_MDM["DR-subject"], CV._sujeto, J, m, r, e, pat_entry, "DocumentReference.subject", "PID-3")
    ctx = r.get("context") if isinstance(r.get("context"), dict) else {}
    ce = C_MDM["DR-encounter"]
    for ref in [x for x in ctx.get("encounter") or [] if isinstance(x, dict)]:
        x, forma = CV.resolver(J.entries, ref, e, "Encounter")
        if pv1 is None:
            if x is not None and x["tipo"] == "Encounter":
                _nota(J, "convencion", "PV1-19", "DocumentReference.context.encounter a un Encounter sin PV1 (cuenta el Encounter)")
            else:
                _cuenta(J, "dato_inventado", "PV1-19", "DocumentReference.context.encounter %r sin PV1" % ref, citas=ce)
            continue
        if en_entry is not None and x is en_entry:
            if forma == "logica":
                _nota(J, "convencion", "PV1-19", "DocumentReference.context.encounter: referencia lógica por identifier")
            continue
        if x is None and forma == "logica" and (ref.get("identifier") or {}).get("value") == _t(m, _f(m, pv1, 19), 1):
            _nota(J, "convencion", "PV1-19", "DocumentReference.context.encounter: referencia lógica a %r" % ref["identifier"]["value"])
            continue
        _cuenta(J, "referencia_rota", "PV1-19", "DocumentReference.context.encounter %r no resuelve al Encounter del PV1" % ref, citas=ce)
    if not ctx.get("encounter") and pv1 is not None and en_entry is not None:
        _nota(J, "sin_encounter", "PV1-19", "DocumentReference.context.encounter ausente: la guía no tiene fila (L-MD-5)")
    rels = [x for x in ctx.get("related") or [] if isinstance(x, dict)]
    srs = {k: (roles.get("ServiceRequest#%d" % k) or {}).get("entry") for k in range(1, len(g["ordenes"]) + 1)}
    hr = _hecho("ORC", 1, 1) if g["ordenes"] else _hecho("TXA", i, 12)
    resueltos = []
    for ref in rels:
        x, forma = CV.resolver(J.entries, ref, e)
        if x is not None:
            resueltos.append(x)
            if not any(x is s for s in srs.values()):
                _nota(J, "extra", hr, "DocumentReference.context.related a %s (no es un ServiceRequest de un grupo de orden)" % x["tipo"])
        elif forma == "rota":
            _cuenta(J, "referencia_rota", hr, "DocumentReference.context.related %r no resuelve" % ref, citas=C_MDM["ORC-ref"] + CV.C["ref"])
        else:
            _nota(J, "convencion", hr, "DocumentReference.context.related %s %r" % (forma, ref))
    vivos = {k: s for k, s in srs.items() if s is not None}
    if not vivos:
        return
    if _dec(J, "Q-MD-D-7") == "una_por_orden":
        for k, s in sorted(vivos.items()):
            if not any(x is s for x in resueltos):
                _cuenta(J, "dato_perdido", _hecho("ORC", k, 1), "DocumentReference.context.related: falta la referencia al ServiceRequest del grupo %d" % k,
                        citas=C_MDM["ORC-ref"])
    elif not any(x is s for x in resueltos for s in vivos.values()):
        k = min(vivos)
        _cuenta(J, "dato_perdido", _hecho("ORC", k, 1), "DocumentReference.context.related: falta la referencia a un ServiceRequest (alternativa de Q-MD-D-7)",
                citas=C_MDM["ORC-ref"])


# ---------------------------------------------------------------------------- el contenido (§4.2)
PALABRA = re.compile(r"[^\W_]+")


def _palabras(s):
    return [w.casefold() for w in PALABRA.findall(s or "")]


def _con_spans(s):
    return [(w.group(0).casefold(), w.start(), w.end()) for w in PALABRA.finditer(s or "")]


def _sin_formato(m, s):
    """Quita las órdenes de formato y locales de un FT/TX ([E2 CH02.txt:947-1111]): \\.xx…\\ deja un hueco (son saltos y
    sangrías), \\H\\ \\N\\ \\Z…\\ \\C…\\ \\M…\\ no dejan nada."""
    e = re.escape(m.e)
    s = re.sub(e + r"\.[^" + e + r"]*" + e, " ", s)
    return re.sub(e + r"(H|N|Z[^" + e + r"]*|C[0-9A-Fa-f]*|M[0-9A-Fa-f]*)" + e, "", s)


def _esperado(m, rep):
    return m.desescapa(_sin_formato(m, rep))


def _escapes(m, rep):
    e = re.escape(m.e)
    return set(re.findall(e + r"[^" + e + r"]*" + e, rep or ""))


def _mime(ct):
    return ct.split(";")[0].strip().lower() if isinstance(ct, str) else ""


def _subtipo(ct):
    return _mime(ct).rsplit("/", 1)[-1].split("+")[0] if "/" in _mime(ct) else ""


def _subsecuencia(esp, obs):
    """Posiciones (índices en obs) de una subsecuencia ordenada de esp, o None."""
    out, p = [], 0
    for w in esp:
        while p < len(obs) and obs[p][0] != w:
            p += 1
        if p == len(obs):
            return None
        out.append(p)
        p += 1
    return out


def _buscar(esp, pool):
    """§4.2 «llega entero»: en un attachment; si no, en todos (en el orden del Bundle, nota partido); si no, desordenado o falta."""
    for x in pool:
        sp = _con_spans(x["texto"])
        pos = _subsecuencia(esp, sp)
        if pos is not None:
            return "entero", [x], x["texto"], sp, pos
    todo = "\n".join(x["texto"] for x in pool)
    sp = _con_spans(todo)
    pos = _subsecuencia(esp, sp)
    if pos is not None:
        return "partido", [x for x in pool if set(_palabras(x["texto"])) & set(esp)], todo, sp, pos
    hay = collections.Counter(w for w, _, _ in sp)
    if not collections.Counter(esp) - hay:
        return "desordenado", [], todo, sp, None
    p, faltan, primera = 0, 0, None
    for w in esp:
        q = next((k for k in range(p, len(sp)) if sp[k][0] == w), None)
        if q is None:
            faltan += 1
            primera = primera or w
        else:
            p = q + 1
    return "falta", [], todo, sp, (primera, faltan)


def _texto(J, m, reps, hecho5, hecho2, pool, tipo, cit, es_nte=False):
    """R-MD-18..24 y R-MD-33: un OBX TX/FT o un NTE-3 (FT) frente al pool de texto."""
    partes = [_palabras(_esperado(m, rep)) for rep in reps]
    esp = [w for p in partes for w in p]
    if not esp:
        return
    modo, atts, texto, sp, pos = _buscar(esp, pool)
    ruta = "NTE-3" if es_nte else "OBX-5 %s" % tipo
    if modo == "falta":
        _cuenta(J, "dato_perdido", hecho5, "DocumentReference.content: del %s faltan %d de %d palabras, la primera %r" % (ruta, pos[1], len(esp), pos[0]),
                citas=cit)
        return
    if modo == "desordenado":
        _cuenta(J, "valor_distinto", hecho5, "DocumentReference.content: las %d palabras del %s están, en otro orden" % (len(esp), ruta), citas=cit)
        return
    if modo == "partido":
        _nota(J, "partido", hecho5, "DocumentReference.content: el %s llega repartido en %d attachments (Q-MD-D-5)" % (ruta, len(atts)))
    for x in atts:
        x.setdefault("hechos", []).append(hecho5)
    if len([p for p in partes if p]) >= 2 and not es_nte:            # R-MD-19: entre repeticiones, un salto de línea
        k, cortes = 0, []
        for p in partes:
            if not p:
                continue
            cortes.append((pos[k], pos[k + len(p) - 1]))
            k += len(p)
        for (_, fin), (ini, _) in zip(cortes, cortes[1:]):
            if not re.search(r"[\r\n]", texto[sp[fin][2]:sp[ini][1]]):
                _cuenta(J, "valor_distinto", hecho5, "DocumentReference.content: las repeticiones de OBX-5 no van separadas por un salto de línea "
                        "(«each repeat yields a line feed»)", citas=cit)
                break
    crudos = {s for rep in reps for s in _escapes(m, rep)}
    tipos = [_mime(x["a"].get("contentType")) for x in atts]
    if tipo == "TX" and not es_nte:                                   # R-MD-20
        delim = {m.e + c + m.e for c in "FSTRE"}
        malos = sorted(s for s in crudos & delim if any(s in x["texto"] for x in atts))
        if malos:
            _cuenta(J, "valor_distinto", hecho5, "DocumentReference.content: escapes de delimitador sin resolver %r" % malos, citas=cit)
    elif tipo == "FT" and not es_nte:                                 # R-MD-23
        malos = sorted(s for s in crudos if any(s in x["texto"] and t != "text/hl7v2" for x, t in zip(atts, tipos)))
        if malos:
            _cuenta(J, "valor_distinto", hecho5, "DocumentReference.content: %r crudos con un contentType que no es text/hl7v2" % malos, citas=cit)
    admitidos = MIME_TEXTO[tipo][_dec(J, "Q-MD-D-3") if _dec(J, "Q-MD-D-3") in ("literales", "literal_o_registrado") else "literal_o_registrado"]
    for x, t in zip(atts, tipos):                                     # R-MD-21 y R-MD-24
        if not t:
            _cuenta(J, "dato_perdido", hecho2, "Attachment.contentType: falta (%s; admitidos %r, Q-MD-D-3)" % (ruta, sorted(admitidos)), citas=cit)
            break
        if t not in admitidos:
            _cuenta(J, "valor_distinto", hecho2, "Attachment.contentType %r para el %s: admitidos %r (Q-MD-D-3)" % (t, ruta, sorted(admitidos)), citas=cit)
            break


def _ed(J, m, o, info):
    """R-MD-25..29: cada repetición de ED, sus octetos en un attachment (o en un Binary referenciado), con su contentType."""
    k = o["k"]
    h5, h2, cit = _hecho("OBX", k, 5), _hecho("OBX", k, 2), C_MDM["OBX-ED"]
    for n, rep in enumerate(_reps(m, _f(m, o["seg"], 5)), 1):
        ed2, ed3, ed4 = _t(m, rep, 2), _t(m, rep, 3), _t(m, rep, 4)
        ed5 = _d(m, _comp(m, rep, 5))
        if not ed5:
            continue
        esp, motivo = _octetos(ed4, ed5)
        libres = [x for x in info if not x["usado"]]
        if esp is None:
            if motivo == "no_ascii":
                _nota(J, "sin_esperado", h5, "ED.4 = A con caracteres no ASCII: no se juzga (L-MD-14)")
                continue
            x = next((x for x in libres if x["a"].get("data") == ed5 or x["octetos"] == ed5.encode("utf-8", "replace")), None)
            if x is not None:
                x["usado"] = True
                x.setdefault("hechos", []).append(h5)
                _cuenta(J, "valor_imposible_convertido", h5, "Attachment.data: ED.5 no es válido para ED.4 %r y el conversor lo escribe" % ed4,
                        clase="valor_imposible_aceptado", citas=cit)
            continue
        x = next((x for x in libres if x["octetos"] == esp), None)
        if x is None:
            for y in libres:
                url = y["a"].get("url")
                if y["a"].get("data") is None and isinstance(url, str) and url:
                    b, _ = CV.resolver(J.entries, {"reference": url}, y["y"], "Binary")
                    if b is not None and b["tipo"] == "Binary" and isinstance(b["r"].get("data"), str):
                        try:
                            igual = base64.b64decode(re.sub(r"\s", "", b["r"]["data"]), validate=True) == esp
                        except (binascii.Error, ValueError):
                            igual = False
                        if igual:
                            x = y
                            J.referidas.add(b["i"])
                            _nota(J, "convencion", h5, "Attachment.url a un Binary con los mismos octetos (R-MD-29)")
                            break
        if x is not None:
            x["usado"] = True
            x.setdefault("hechos", []).append(h5)
            if ed3:                                                  # R-MD-27: sin ED.3, nada se espera
                _tipo_mime(J, x, ed3, ("%s/%s" % (ed2, ed3)) if ed2 else ed3, h2, cit, "ED.3")
            continue
        causa, y = None, None
        for z in libres:
            dat = z["a"].get("data")
            if z["octetos"] is not None and z["octetos"] in (base64.b64encode(esp), re.sub(r"\s", "", ed5).encode("ascii", "replace")) and ed4.upper() == "BASE64":
                causa, y = "codificación doble (el Base64 de ED.5 codificado otra vez)", z
            elif z["octetos"] and len(z["octetos"]) < len(esp) and esp.startswith(z["octetos"]):
                causa, y = "truncado (%d de %d octetos)" % (len(z["octetos"]), len(esp)), z
            elif isinstance(dat, str) and ed4.upper() != "BASE64" and re.sub(r"\s", "", dat) == re.sub(r"\s", "", ed5):
                causa, y = "sin convertir de %s a Base64" % ed4, z
            if causa:
                break
        if causa is None:
            y = next((z for z in libres if z["octetos"] is not None and ed3 and _subtipo(z["a"].get("contentType")) == ed3.lower()), None)
            causa = "ninguna de las dos (otros octetos con el mismo subtipo)" if y else None
        if y is not None:
            y["usado"] = True
            y.setdefault("hechos", []).append(h5)
            _cuenta(J, "valor_distinto", h5, "Attachment.data de la repetición %d de OBX-5 (ED): %s" % (n, causa), citas=cit)
        else:
            _cuenta(J, "dato_perdido", h5, "DocumentReference.content: falta el attachment de la repetición %d de OBX-5 (ED, %d octetos)" % (n, len(esp)),
                    citas=cit)


def _tipo_mime(J, x, sub, literal, h2, cit, campo):
    """R-MD-27 y R-MD-31: el literal (ED.3, ED.2/ED.3; RP.3/RP.4) o, con Q-MD-D-3 (b), cualquier tipo con el mismo subtipo."""
    t = _mime(x["a"].get("contentType"))
    if not t:
        _cuenta(J, "dato_perdido", h2, "Attachment.contentType: falta (%s %r)" % (campo, sub), citas=cit)
        return
    admitidos = {sub.lower(), (literal or "").lower()} - {""}
    if t in admitidos or (_dec(J, "Q-MD-D-3") != "literales" and _subtipo(t) == sub.lower()):
        return
    _cuenta(J, "valor_distinto", h2, "Attachment.contentType %r para %s %r (Q-MD-D-3)" % (t, campo, literal), citas=cit)


def _rp(J, m, o, info):
    """R-MD-30..32: cada repetición de RP, un attachment con url = RP.1 (con un prefijo, nota) y, con RP.3 y RP.4, su contentType."""
    k = o["k"]
    h5, h2, cit = _hecho("OBX", k, 5), _hecho("OBX", k, 2), C_MDM["OBX-RP"]
    for n, rep in enumerate(_reps(m, _f(m, o["seg"], 5)), 1):
        rp1, rp3, rp4 = _t(m, rep, 1), _t(m, rep, 3), _t(m, rep, 4)
        if not rp1:
            continue
        libres = [x for x in info if not x["usado"]]
        x = next((x for x in libres if x["a"].get("url") == rp1), None)
        if x is None:
            x = next((x for x in libres if isinstance(x["a"].get("url"), str) and x["a"]["url"].endswith("/" + rp1)), None)
            if x is not None:
                _nota(J, "convencion", h5, "Attachment.url %r: RP.1 con un prefijo (AMB-MD-11)" % x["a"]["url"], "ambiguedad AMB-MD-11")
        if x is None:
            y = next((y for y in libres if y["a"].get("url")), None)
            if y is not None:
                y["usado"] = True
                _cuenta(J, "valor_distinto", h5, "Attachment.url de la repetición %d de OBX-5 (RP): esperado %r, observado %r" % (n, rp1, y["a"]["url"]), citas=cit)
            else:
                _cuenta(J, "dato_perdido", h5, "DocumentReference.content: falta el attachment con url %r (repetición %d de OBX-5, RP)" % (rp1, n), citas=cit)
            continue
        x["usado"] = True
        x.setdefault("hechos", []).append(h5)
        if rp3 and rp4:
            _tipo_mime(J, x, rp4, "%s/%s" % (rp3, rp4), h2, cit, "RP.3/RP.4")


def _sin_destino(J, m, o, todas, info):
    """R-MD-35 (Q-MD-D-12): un OBX de tipo sin fila es nota; con la alternativa, dato perdido si su valor no está en ningún
    elemento de la DocumentReference ni de lo que referencia."""
    h5 = _hecho("OBX", o["k"], 5)
    v5 = _f(m, o["seg"], 5)
    if not v5:
        return
    if _dec(J, "Q-MD-D-12") != "dato_perdido":
        _nota(J, "sin_destino", h5, "OBX-2 %r sin fila en la guía (L-MD-2, Q-MD-D-12)" % _tipo_obx(m, o))
        return
    rep = _reps(m, v5)[0]
    vals = {v for v in (_t(m, rep, 1), _d(m, rep)) if v}
    cadenas = [x["texto"] for x in info if x["texto"]]
    for y in todas:
        cadenas += list(_cadenas(y["r"]))
        for ref in CV._referencias(y["r"]):
            z, _ = CV.resolver(J.entries, ref, y)
            if z is not None:
                cadenas += list(_cadenas(z["r"]))
    if not any(v in c for v in vals for c in cadenas if isinstance(c, str)):
        _cuenta(J, "dato_perdido", h5, "OBX-2 %r: su valor no está en la DocumentReference ni en lo que referencia (alternativa de Q-MD-D-12)" % _tipo_obx(m, o),
                citas=C_MDM["OBX-sin"])


def _cadenas(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from _cadenas(v)
    elif isinstance(x, list):
        for v in x:
            yield from _cadenas(v)


def _contenido(J, m, d, i, e, dups, h):
    """R-MD-14, R-MD-17..35: el contenido de la DocumentReference emparejada y de sus duplicadas, juzgado en conjunto (AMB-MD-18)."""
    todas = [e] + dups
    contents = [(y, c) for y in todas for c in (y["r"].get("content") or []) if isinstance(c, dict)]
    obxs = d["obx"]
    destino = [o for o in obxs if _tipo_obx(m, o) in CON_DESTINO and _f(m, o["seg"], 5)]
    ntes = [n for o in obxs for n in o["nte"] if _palabras(_esperado(m, " ".join(_reps(m, _f(m, n["seg"], 3)))))]
    h0 = _hecho("OBX", (destino or obxs)[0]["k"], 5) if (destino or obxs) else h(12)
    if not contents:                                                  # R-MD-17: absorbe lo del contenido (y la ausencia de TXA-3)
        if destino or ntes:
            _cuenta(J, "fhir_invalido", h0, "DocumentReference.content: falta (1..*), con %d OBX con destino en la guía" % len(destino),
                    citas=C_MDM["OBX-content"])
        else:
            _nota(J, "sin_content_posible", h0, "DocumentReference sin content y sin OBX con destino en la guía (R4 pide content 1..*; L-MD-2)")
            for o in obxs:
                _sin_destino(J, m, o, todas, [])
        return
    if any(not isinstance(c.get("attachment"), dict) for _, c in contents):
        _cuenta(J, "fhir_invalido", h0, "DocumentReference.content: %d sin attachment (1..1)" % sum(1 for _, c in contents if not isinstance(c.get("attachment"), dict)),
                citas=C_MDM["OBX-content"])
    info = []
    for y, c in contents:
        a = c.get("attachment")
        if not isinstance(a, dict):
            continue
        x = {"y": y, "a": a, "octetos": None, "texto": None, "valido": None, "usado": False}
        if isinstance(a.get("data"), str):
            try:
                x["octetos"] = base64.b64decode(re.sub(r"\s", "", a["data"]), validate=True)
                x["valido"] = True
                try:
                    x["texto"] = x["octetos"].decode("utf-8")
                except UnicodeDecodeError:
                    pass
            except (binascii.Error, ValueError):
                x["valido"], x["texto"] = False, a["data"]
        elif a.get("data") is not None:
            x["valido"] = False
        info.append(x)
    t3 = _t(m, _rep1(m, d["txa"], 3), 1)                              # R-MD-14; DV-MD-10 (H13): solo con un attachment con data o url
    con_dato = [x for x in info if x["a"].get("data") is not None or x["a"].get("url")]
    if t3 and con_dato and not any(x["a"].get("contentType") for x in con_dato):
        _cuenta(J, "dato_perdido", h(3), "Attachment.contentType: ninguno, con TXA-3 %r (Q-MD-D-3)" % t3, citas=C_MDM["TXA-3"])
    for o in obxs:                                                    # primero lo que ocupa un attachment propio
        t = _tipo_obx(m, o)
        if t == "ED":
            _ed(J, m, o, info)
        elif t == "RP":
            _rp(J, m, o, info)
    pool = [x for x in info if not x["usado"] and x["texto"] is not None]
    for o in obxs:
        t = _tipo_obx(m, o)
        if t in ("TX", "FT"):
            _texto(J, m, _reps(m, _f(m, o["seg"], 5)), _hecho("OBX", o["k"], 5), _hecho("OBX", o["k"], 2), pool, t, C_MDM["OBX-%s" % t])
        elif t not in ("ED", "RP"):
            _sin_destino(J, m, o, todas, info)
        for n in o["nte"]:
            hn = _hecho("NTE", n["j"], 3)
            _texto(J, m, _reps(m, _f(m, n["seg"], 3)), hn, hn, pool, "FT", C_MDM["NTE-3"], es_nte=True)
    for x in info:                                                    # R-MD-34
        if x["valido"] is False:
            _cuenta(J, "fhir_invalido", (x.get("hechos") or [h0])[0], "Attachment.data no es base64Binary (L-MD-7)", citas=C_MDM["OBX-data"])


# ---------------------------------------------------------------------------- ServiceRequest (§4.3)
def _ce_en(m):
    """DV-MD-14 (H7): OBR-4 es CE ([E4 CH04.txt:3448-3451], seis componentes, [E2A CH02A.txt:309-319]) en las versiones hasta 2.5 (MSH-12
    vacío se juzga como 2.5); un componente de más «shall be ignored» ([E2 CH02.txt:932-935]). Desde 2.6 es CWE y CWE.9 va a text."""
    v = [int(x) for x in re.findall(r"\d+", _comp(m, _f(m, m.segs[0], 12), 1))[:2]] or [2, 5]
    return tuple(v + [0])[:2] < (2, 6)


def _servicio(J, m, o, i, e, pat_entry):
    """R-MD-38..41 (Q-MD-D-10 a): subject, identifier PLAC/FILL (de OBR si está valorado, si no de ORC: AMB-CV-8), code ← OBR-4 y
    validez de status e intent («localized interpretation»)."""
    r, orc, obr = e["r"], o["orc"], o["obr"]
    _reusa(J, C_MDM["SR-subject"], CV._sujeto, J, m, r, e, pat_entry, "ServiceRequest.subject", "PID-3")
    ids = [x for x in r.get("identifier") or [] if isinstance(x, dict)]
    usados = set()
    for n, tipo in ((2, "PLAC"), (3, "FILL")):
        vals = {_t(m, _f(m, obr, n), 1), _t(m, _f(m, orc, n), 1)} - {""}
        if not vals:
            continue
        hecho, cit = _hecho("ORC", i, n), C_SEG["ORC-%d" % n]
        con = [k for k, x in enumerate(ids) if x.get("value") in vals]
        if not con:
            _cuenta(J, "dato_perdido", hecho, "ServiceRequest.identifier: falta %r (%s)" % (sorted(vals), tipo), citas=cit)
            continue
        usados |= set(con)
        if not any(tipo in {c[1] for c in _codigos(ids[k].get("type"))} for k in con):
            _cuenta(J, "codigo_mal_mapeado", hecho, "ServiceRequest.identifier %r: type esperado %s, observado %r" %
                    (sorted(vals), tipo, [c[1] for k in con for c in _codigos(ids[k].get("type"))]), citas=cit)
    extra = [x.get("value") for k, x in enumerate(ids) if k not in usados]
    if extra:
        _nota(J, "extra", _hecho("ORC", i, 3), "ServiceRequest.identifier de más: %r (TXA-14/15 y ORC-4 no se esperan)" % extra)
    if obr is not None:
        campo4 = _f(m, obr, 4)
        if _ce_en(m):                                                # DV-MD-14 (H7): CE (seis componentes) hasta 2.5; el resto se ignora
            campo4 = m.c.join((_reps(m, campo4) or [""])[0].split(m.c)[:6])
        _reusa(J, C_SEG["OBR-4"], CV._codigo, J, m, campo4, r.get("code"), _hecho("OBR", i, 4), "ServiceRequest.code")
    if r.get("status") not in REQUEST_STATUS:
        _cuenta(J, "fhir_invalido", _hecho("ORC", i, 5), "ServiceRequest.status: %r (1..1, required)" % r.get("status"), citas=C_MDM["ORC-5"])
    if r.get("intent") not in REQUEST_INTENT:
        _cuenta(J, "fhir_invalido", _hecho("ORC", i, 1), "ServiceRequest.intent: %r (1..1, required)" % r.get("intent"), citas=C_MDM["ORC-int"])


# ---------------------------------------------------------------------------- el perfil como datos (consultar_tabla, §4)
def _fila(elemento, campo, regla, nivel, clave):
    return {"elemento": elemento, "campo": campo, "regla": regla, "nivel": nivel, "citas": list(C_MDM.get(clave) or C_SEG.get(clave) or [])}


PERFIL_GUIA_MDM = [
    _fila("DocumentReference (existencia)", "TXA", "R-MD-1: una por TXA; emparejada por TXA-12, TXA-16, TXA-2, única u orden", "cuenta", "TXA"),
    _fila("DocumentReference (duplicadas)", "TXA-12", "R-MD-2: de más para un TXA, recurso duplicado; su content se suma (AMB-MD-18)", "cuenta", "TXA"),
    _fila("DocumentReference.masterIdentifier.value", "TXA-12", "R-MD-3: EI.1 desescapado", "cuenta", "TXA-12"),
    _fila("DocumentReference.masterIdentifier.system/assigner", "TXA-12", "R-MD-4: con EI.2 o EI.3, en system o assigner (forma: convención)", "cuenta", "TXA-12"),
    _fila("DocumentReference.identifier[]", "TXA-16", "R-MD-5: TXA-16 desescapado y entero (la ruta completa); los demás, nota", "cuenta", "TXA-16"),
    _fila("DocumentReference.type", "TXA-2", "R-MD-6: coding.code = TXA-2.1 (IS, 0270 definida por el usuario); system: convención", "cuenta", "TXA-2"),
    _fila("DocumentReference.status (TXA-19 vacío o AV)", "TXA-19", "R-MD-7: current", "cuenta", "TXA-19"),
    _fila("DocumentReference.status (TXA-19 CA, OB, UN)", "TXA-19", "R-MD-8: el código en status.extension[alternate-codes] o, CA y OB, en un status "
          "coherente; con Q-MD-D-9 (b) CA → entered-in-error y OB → superseded", "cuenta", "TXA-19"),
    _fila("DocumentReference.docStatus", "TXA-17", "R-MD-9: el literal ∪ MAPA_0271; el literal cuenta además como fhir_invalido (Q-MD-D-4 b)", "cuenta", "TXA-17"),
    _fila("DocumentReference.securityLabel[]", "TXA-18", "R-MD-10: {v2-0272, código} o {v3-Confidentiality, código}", "cuenta", "TXA-18"),
    _fila("DocumentReference.date", "TXA-6", "R-MD-11: instant con hora; solo fecha, ausente o completada; sin TXA-6, nota si es otro TS del mensaje", "cuenta", "TXA-6"),
    _fila("DocumentReference.author[]", "TXA-9", "R-MD-12: un Practitioner por repetición (identifier ∋ XCN.1, family = XCN.2, given[1] = XCN.3)", "cuenta", "TXA-9"),
    _fila("DocumentReference.authenticator", "TXA-10", "R-MD-13: una repetición cualquiera (Q-MD-D-11 b)", "cuenta", "TXA-10"),
    _fila("Attachment.contentType (TXA-3)", "TXA-3", "R-MD-14: con TXA-3, algún contentType; su valor es convención (Q-MD-D-3)", "convencion", "TXA-3"),
    _fila("DocumentReference.subject, context.encounter", "PID-3/PV1-19", "R-MD-15: presentes, resuelven al Patient y al Encounter; ausentes, nota (Q-MD-D-6)",
          "cuenta", "DR-subject"),
    _fila("DocumentReference.context.related[]", "ORC", "R-MD-16: una referencia por ServiceRequest emparejado (Q-MD-D-7 b)", "cuenta", "ORC-ref"),
    _fila("DocumentReference.content 1..*, attachment 1..1", "OBX", "R-MD-17: con OBX con destino, content; absorbe los datos perdidos", "cuenta", "OBX-content"),
    _fila("content: TX", "OBX-5 (TX)", "R-MD-18: las palabras de todas las repeticiones, en orden, en un attachment o en el conjunto", "cuenta", "OBX-TX"),
    _fila("content: salto entre repeticiones", "OBX-5 (TX)", "R-MD-19: LF, CR LF o CR entre repeticiones (AMB-MD-24)", "cuenta", "OBX-TX"),
    _fila("content: TX, escapes", "OBX-5 (TX)", "R-MD-20: sin \\F\\ \\S\\ \\T\\ \\R\\ \\E\\ crudos", "cuenta", "OBX-TX"),
    _fila("Attachment.contentType (TX)", "OBX-2 (TX)", "R-MD-21: application/text o text/plain (Q-MD-D-3 b)", "cuenta", "OBX-TX"),
    _fila("content: FT", "OBX-5 (FT)", "R-MD-22: como TX, sin las órdenes de formato", "cuenta", "OBX-FT"),
    _fila("content: FT, escapes", "OBX-5 (FT)", "R-MD-23: crudos solo con text/hl7v2 (AMB-MD-9)", "cuenta", "OBX-FT"),
    _fila("Attachment.contentType (FT, NTE)", "OBX-2 (FT)", "R-MD-24: text/hl7v2 o text/plain (Q-MD-D-3 b)", "cuenta", "OBX-FT"),
    _fila("Attachment.data (ED Base64)", "OBX-5 (ED)", "R-MD-25: los mismos octetos que ED.5", "cuenta", "OBX-ED"),
    _fila("Attachment.data (ED A, Hex)", "OBX-5 (ED)", "R-MD-26: los octetos de ED.5 según ED.4; ED.5 imposible escrito: valor imposible convertido", "cuenta", "OBX-ED"),
    _fila("Attachment.contentType (ED)", "OBX-2 (ED)", "R-MD-27: ED.3, ED.2/ED.3 o el mismo subtipo (Q-MD-D-3 b); sin ED.3, nada", "cuenta", "OBX-ED"),
    _fila("content por repetición (ED)", "OBX-5 (ED)", "R-MD-28: una repetición, un attachment", "cuenta", "OBX-ED"),
    _fila("Attachment.url → Binary (ED)", "OBX-5 (ED)", "R-MD-29: un Binary referenciado con los mismos octetos", "convencion", "OBX-ED"),
    _fila("Attachment.url (RP)", "OBX-5 (RP)", "R-MD-30: url = RP.1 (con prefijo, nota)", "cuenta", "OBX-RP"),
    _fila("Attachment.contentType (RP)", "OBX-2 (RP)", "R-MD-31: RP.3/RP.4 o el mismo subtipo (Q-MD-D-3 b)", "cuenta", "OBX-RP"),
    _fila("content por repetición (RP)", "OBX-5 (RP)", "R-MD-32: una repetición, un attachment", "cuenta", "OBX-RP"),
    _fila("content: NTE bajo OBX", "NTE-3", "R-MD-33: las palabras de NTE-3 en el pool", "cuenta", "NTE-3"),
    _fila("Attachment.data", "OBX-5", "R-MD-34: base64Binary válido (L-MD-7)", "cuenta", "OBX-data"),
    _fila("OBX sin destino", "OBX-2", "R-MD-35: CE, ST, NM… sin fila: nota (Q-MD-D-12)", "nota", "OBX-sin"),
    _fila("Observation, DiagnosticReport", "OBX", "R-MD-36: otros_tipos (Q-MD-D-8)", "nota", "OBX-obs"),
    _fila("ServiceRequest (existencia)", "ORC/OBR", "R-MD-37: uno por grupo de orden; de más, recurso inventado", "cuenta", "SR"),
    _fila("ServiceRequest.subject", "PID-3", "R-MD-38: resuelve al Patient (1..1)", "cuenta", "SR-subject"),
    _fila("ServiceRequest.identifier[]", "ORC-2/ORC-3", "R-MD-39: PLAC y FILL de OBR o de ORC (AMB-CV-8); TXA-14/15 no", "cuenta", "ORC-2"),
    _fila("ServiceRequest.code", "OBR-4", "R-MD-40: como CV._codigo", "cuenta", "OBR-4"),
    _fila("ServiceRequest.status, intent", "ORC-5/ORC-1", "R-MD-41: presentes y en request-status / request-intent; sin valor esperado", "cuenta", "ORC-5"),
    _fila("ServiceRequest (resto)", "—", "R-MD-42: NTE de OBR, TQ1, requester, occurrence…: nota", "nota", "SR"),
    _fila("Patient", "PID", "R-MD-43: las reglas de adt_conv", "cuenta", "PID"),
    _fila("Encounter", "PV1", "R-MD-44: las reglas de adt_conv; ausente, recurso ausente (PV1-2 = N: Q-CV-D-6)", "cuenta", "PV1"),
    _fila("MessageHeader, Provenance, Device, Organization, Practitioner y Binary no alcanzados…", "—", "R-MD-45: otros_tipos (Q-MD-D-2, L-MD-3)", "nota", "TXA"),
    {"elemento": "id, meta, text, extensiones (salvo la de R-MD-8), display, orden de listas y de content[], Bundle.*", "campo": "—",
     "regla": "R-MD-46: forma (L-CV-4, L-CV-9, L-MD-11)", "nivel": "forma", "citas": ["[L-CV-4]", "[L-CV-9]", "[L-MD-11]"]},
]

S_MD = {"S-MD-1": "Un punto de entrada nuevo, mdm_conv (familia mdm, solo transformación), hermano de adt_conv, oru_conv y vxu_conv; el punto mdm de acuse no cambia.",
        "S-MD-2": "La misma evidencia {mensaje, punto_entrada, conversion} de S-CV-2.",
        "S-MD-3": "Una DocumentReference por TXA con el contenido de todos sus OBX y NTE; de más para un TXA, recurso duplicado, y su contenido se juzga en conjunto.",
        "S-MD-4": "Las mismas ocho clases, categorías y leyenda de adt_conv, oru_conv y vxu_conv.",
        "S-MD-5": "El contenido se juzga como vehículo, no como texto: tipo (OBX-2), codificación (ED.4), tipo MIME y que llegue entero (palabras en orden; octetos).",
        "S-MD-6": "Los caminos de la hoja de OBX se leen como content[].attachment.*; los índices 1-4 son etiquetas por tipo.",
        "S-MD-7": "Un ServiceRequest por grupo de orden con perfil reducido, referenciado desde context.related.",
        "S-MD-8": "Patient y Encounter con las reglas de adt_conv; el PV1 es 1..1.",
        "S-MD-9": "TXA-17 → docStatus con un conjunto: el literal de la guía ∪ MAPA_0271 (Q-MD-D-4).",
        "S-MD-10": "TXA-19 → status: vacío y AV → current; CA, OB, UN → el código en status.extension[alternate-codes] (Q-MD-D-9).",
        "S-MD-11": "TXA-9 → author, TXA-10 → authenticator; Provenance y MessageHeader fuera (Q-MD-D-2).",
        "S-MD-12": "Los OBX de tipo sin fila y los NTE de OBR son nota; un Observation en el Bundle es nota (Q-MD-D-8, Q-MD-D-12).",
        "S-MD-13": "mdm_conv juzga MDM^T02 (Q-MD-D-1); el resto de eventos MDM es fuera de alcance.",
        "S-MD-14": "El corpus son 40 bases sintéticas válidas en v2.5 (bases_mdm.py, MD2-a).",
        "S-MD-15": "La herramienta lleva MSH-9.1 = MDM a mdm_conv; ADT, ORU y VXU quedan igual.",
        "S-MD-16": "La versión manda como en S-CV-6: con MSH-12 ≠ 2.5 los ConceptMap cuentan y la legalidad de tabla o estructura de 2.5 no (L18).",
        "S-MD-17": "Los campos que la guía mapea y 2.5 no tiene nunca cuentan: TXA-24..28, NTE-5..9, OBX-20..33, UAC y CON."}
L_MD = {"L-MD-1": "El contenido no se interpreta: ni RTF, ni PDF, ni CDA. Un texto llega entero si sus palabras son una subsecuencia ordenada de las del data "
                  "decodificado; un binario, si sus octetos son los mismos tras deshacer ED.4.",
        "L-MD-2": "Los OBX de tipo distinto de TX, FT, ED y RP no tienen fila en la guía: nota sin_destino (Q-MD-D-12).",
        "L-MD-3": "Provenance, MessageHeader, Device, Coverage, Basic, Organization, Observation y lo demás fuera del perfil son otros_tipos; Practitioner y "
                  "Binary solo se leen como destino de author, authenticator y attachment.url.",
        "L-MD-4": "TXA-4, 5, 7, 8, 11, 13, 14, 15, 20, 21, 22 y 23 no tienen destino en DocumentReference; TXA-24..28, NTE-5..9 y OBX-20..33 no existen en 2.5.",
        "L-MD-5": "subject y context.encounter no tienen fila en la guía: presentes y equivocados cuentan; ausentes, nota (Q-MD-D-6).",
        "L-MD-6": "MAPA_0271, FAMILIA_0191 y los códigos de request-status y request-intent no son de la guía ni están en el paquete.",
        "L-MD-7": "De base64Binary solo se comprueba el alfabeto y el relleno; ni url, ni la sintaxis MIME, ni los demás primitivos.",
        "L-MD-8": "Solo MDM^T02; la semántica de cambio de estado, TXA-13 y las transiciones de TXA-17 y TXA-19 no se juzgan.",
        "L-MD-9": "Un OBX antes del TXA solo se cuenta; un segundo TXA da nota estructura; UAC y CON se ignoran.",
        "L-MD-10": "Dos grupos de orden que solo se distinguen por los ServiceRequest (sin números que los separen, con el mismo OBR-4), o dos "
                   "DocumentReference sin claves comunes, no se distinguen: indeterminado/emparejamiento. Desde MD3-r1 (DV-MD-13), los grupos "
                   "idénticos con el mismo número de orden son una sola orden y no caen aquí.",
        "L-MD-11": "Las extensiones nunca cuentan, salvo status.extension[alternate-codes] con TXA-19 = CA, OB o UN.",
        "L-MD-12": "ED.5 llega a 65536 caracteres en 2.5; un Bundle de más de 4.000.000 de caracteres no se juzga (L-VC-12).",
        "L-MD-13": "MSH-9.3 nunca cuenta; con MSH-12 ≠ 2.5 la legalidad de una tabla o de la estructura no se juzga (L18).",
        "L-MD-14": "ED.4 = A se codifica como ASCII; con caracteres no ASCII no se juzga (nota).",
        "L-MD-15": "«Llega entero» mira palabras (alfanuméricas, sin mayúsculas): no ve puntuación ni espacios, ni distingue dos OBX con el mismo texto.",
        "L-MD-16": "Con varias DocumentReference para un TXA, el contenido se juzga en conjunto.",
        "L-MD-17": "La clase nueva / ya declarada / convención no la calcula el juez: la pone MD3 por mecanismo."}
AMB_MD = {"AMB-MD-1": "TXA-2: IS de una tabla definida por el usuario (2.5) o CWE (hoja): coding.code ∋ TXA-2.1, sin system.",
          "AMB-MD-2": "TXA-3 (0191) no es un tipo MIME: el valor es convención; solo cuenta la ausencia total.",
          "AMB-MD-3": "TXA-17: el literal ∪ MAPA_0271 (Q-MD-D-4); AU admite final y preliminary.",
          "AMB-MD-4": "TXA-19 vacío → current (fila de la hoja); CA, OB, UN: la extensión y, con Q-MD-D-9 (b), status coherente.",
          "AMB-MD-5": "alternate-codes con http (hoja de TXA) o https (hoja de ED): las dos.",
          "AMB-MD-6": "La hoja de OBX escribe content[n].data sin .attachment: se lee content[].attachment.*; los números son etiquetas.",
          "AMB-MD-7": "Varios OBX del mismo tipo: cualquier reparto (Q-MD-D-5).",
          "AMB-MD-8": "application/text y text/hl7v2 no son tipos registrados: también text/plain (Q-MD-D-3).",
          "AMB-MD-9": "FT con text/hl7v2 conserva las órdenes de formato; con otro tipo, ninguna cruda.",
          "AMB-MD-10": "ED.3 → contentType lleva solo el subtipo: ED.3, ED.2/ED.3 o el mismo subtipo.",
          "AMB-MD-11": "RP.1 es un «pointer»: url = RP.1; con un prefijo, nota.",
          "AMB-MD-12": "La hoja de ED solo nombra A y Hex: Base64 pasa tal cual.",
          "AMB-MD-13": "NTE-3 → content[1].attachment.data y content[2].contentType: un content con las palabras del comentario.",
          "AMB-MD-14": "TXA-10 repite y authenticator es 0..1: una repetición cualquiera (Q-MD-D-11).",
          "AMB-MD-15": "subject sin fila en la guía: ausente, nota (Q-MD-D-6).",
          "AMB-MD-16": "ServiceRequest[1] con varios grupos: una referencia por ServiceRequest (Q-MD-D-7).",
          "AMB-MD-17": "date con hora: instant; sin hora: ausente o completada; sin TXA-6, nota si coincide con un TS del mensaje.",
          "AMB-MD-18": "Varias DocumentReference para un TXA: la primera se empareja, las demás son duplicadas; contenido en conjunto.",
          "AMB-MD-19": "EI[Identifier-Organization] sin system: EI.2/EI.3 en system o assigner.",
          "AMB-MD-20": "TXA-18: v2-0272 (guía) o v3-Confidentiality (binding extensible).",
          "AMB-MD-21": "UAC y CON de la hoja no están en el MDM_T02 de 2.5: se ignoran.",
          "AMB-MD-22": "Provenance[3] se usa dos veces en la hoja: irrelevante mientras Provenance sea nota.",
          "AMB-MD-23": "EVN es «B, v2.5» y sigue obligatorio; EVN-1 = MSH-9.2; EVN no se juzga.",
          "AMB-MD-24": "Entre repeticiones de TX: LF, CR LF o CR.",
          "AMB-MD-25": "ServiceRequest.status e intent: «localized interpretation»; solo validez."}
DV_MD = {"DV-MD-0": "El diseño lo hizo Sonnet a ciegas, no Fable (sin cupo); Jev eligió un modelo más pequeño y distinto (0,61).",
         "DV-MD-1": "ServiceRequest, clave identifier: gana el candidato que comparte más números del grupo (PLAC y FILL) y un empate se desempata por "
                    "OBR-4. Con la regla literal, ms-MDM-T02-02 (dos grupos con el mismo filler 1-1) salía indeterminado en los dos conversores (MD1-a).",
         "DV-MD-2": "P-MD-24: mdm_conv sin `conversion` no es un error de esquema sino indeterminado/sin_salida, como adt_conv, oru_conv y vxu_conv hoy; "
                    "hacerlo error solo para mdm_conv sería incoherente, y para todos cambiaría ADT, ORU y VXU.",
         "DV-MD-3": "Las citas de MDM no se registran en conversion.C (P-MD-25 d la exige igual): cada hallazgo lleva las suyas y las de las funciones "
                    "reutilizadas de conversion.py se corrigen al vuelo (_reusa). ORC-1/2/3, OBR-4, PID y PV1 van en C_SEG porque ya son claves de "
                    "ADT, ORU o VXU.",
         "DV-MD-4": "CORPUS, generar_corpus y bases_mdm no entraron en MD1: sin bases_mdm.py, la carpeta mdm rompía la herramienta. "
                    "MD2-a los añade, con mdm al final de CORPUS.",
         "DV-MD-5": "prueba_multitipo.py fija la lista de puntos de entrada de info_verificador, que gana mdm_conv (como DV-VX-4); el "
                    "diseño la daba entre los controles que no cambian.",
         "DV-MD-6": "Las bases con TXA-17 distinto de DI llevan TXA-7 y TXA-11, que el estándar exige ([E9 CH09.txt:1030-1035]: TXA-7 con "
                    "TXA-17 distinto de «dictated»; TXA-11, en todo documento transcrito). B40, «solo TXA-1, 2, 3, 12 y 17», lleva TXA-17 DI. "
                    "Sin ellos, un rechazo del conversor sería legítimo y el juez lo contaría como rechazo incorrecto.",
         "DV-MD-7": "Las bases con TXA-17 AU o LA llevan TXA-22 con la persona de la primera repetición de TXA-10 y la fecha de la autenticación "
                    "(PPN.15): el estándar lo exige ([E9 CH09.txt:1798-1800]). B37 conserva el suyo.",
         "DV-MD-8": "H8: con TXA-10 vacío, un authenticator que es la persona de TXA-22 es nota, no dato inventado (v2.5 y R4 definen lo mismo).",
         "DV-MD-9": "H10: con TXA-17 vacío, un docStatus igual al que da el ConceptMap de OBX-11 (0085) u OBR-25 (0123) es nota.",
         "DV-MD-10": "H13: R-MD-14 cuenta solo si algún attachment lleva data o url; sin ellos R4 no exige contentType y la pérdida ya cuenta.",
         "DV-MD-11": "H20: un status equivocado con TXA-19 CA u OB es una sola cuenta (valor_distinto), no dato_perdido+valor_distinto.",
         "DV-MD-12": "H21: un ServiceRequest con el número de OBR-29 u ORC-8, referenciado desde basedOn de otro emparejado, es el pedido padre: nota.",
         "DV-MD-13": "H22: grupos de orden idénticos con el mismo número de orden son una sola orden: un ServiceRequest basta; otros iguales, hasta "
                    "tantos como grupos, son nota; los de más, recurso duplicado.",
         "DV-MD-14": "H7: OBR-4 es CE hasta 2.5; los componentes de más se ignoran ([E2 §2.6.2]) y CWE.9 → text no se espera. Se hace en el camino "
                    "de MDM, sin tocar CV._codigo."}
INFO = {"guia": CV.GUIA, "decisiones": S_MD, "decisiones_jev": DECISIONES_MD, "alternativas_sensibilidad": ALTERNATIVA_MD, "limites": L_MD,
        "ambiguedades": AMB_MD, "desviaciones": DV_MD, "puntos_entrada": ["mdm_conv"], "diseno": "md/diseno-md.md",
        "decisiones_doc": "md/decisiones-qmd.md", "resultado": "RESULTADO-MDM.md"}

CV.INFO["mdm"] = INFO
# Q-MD-D-1, alternativa (t02_y_cuatro): el mismo punto con T04, T06, T08 y T10 (estructura MDM_T02), para la sensibilidad de MD2.
PE_ALTERNATIVA_EVENTOS = dict(PE.PUNTOS["mdm_conv"], tipos={"MDM": {ev: "MDM_T02" for ev in ("T02", "T04", "T06", "T08", "T10")}})


# ---------------------------------------------------------------------------- autoprueba
def autoprueba():
    ok = True
    if os.path.isdir(CV.PAQUETE):
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "cv"))
        import extraer_mapas as X
        for n in MAPAS_MDM:
            if X.mapa(CV.PAQUETE, n) != MAPAS_MDM[n]:
                print("  MAL el mapa %s no es el del paquete" % n)
                ok = False
        print("mapas de MDM contra el paquete: %s (%d)" % ("IGUALES" if ok else "DISTINTOS", len(MAPAS_MDM)))
    else:
        print("mapas de MDM: el paquete de la guía no está aquí; no se comparan")
    choques = [k for k in C_MDM if k in CV.C and CV.C[k] != C_MDM[k] and k not in C_SEG]
    if choques:
        print("  MAL claves de cita de MDM que ya eran de ADT, ORU o VXU: %r" % choques)
        ok = False
    malas = [k for k, v in list(C_MDM.items()) + list(C_SEG.items())
             if not (any(c.startswith(("[G ", "[CM ")) for c in v) and any(c.startswith(("[E", "[F ", "[AMB")) for c in v))]
    if malas:
        print("  MAL citas sin guía y estándar: %r" % malas)
        ok = False
    niveles = collections.Counter(f["nivel"] for f in PERFIL_GUIA_MDM)
    if len(PERFIL_GUIA_MDM) != 46 or dict(niveles) != {"cuenta": 39, "convencion": 2, "nota": 4, "forma": 1} or not all(f["citas"] for f in PERFIL_GUIA_MDM):
        print("  MAL el perfil: %d filas, niveles %r" % (len(PERFIL_GUIA_MDM), dict(niveles)))
        ok = False
    if set(DECISIONES_MD) != {"Q-MD-D-%d" % n for n in range(1, 13)} or not set(ALTERNATIVA_MD) <= set(DECISIONES_MD):
        print("  MAL las decisiones de Jev")
        ok = False
    print("AUTOPRUEBA DE conversion_mdm: %s" % ("TODO BIEN" if ok else "MAL"))
    return 0 if ok else 1


if __name__ == "__main__":
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
