#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 14l (cv/diseno-conversores-fable.md, de Fable; decisiones de Jev en cv/decisiones-qcv.md): el juez ante la salida de un
conversor HL7 v2 → FHIR de terceros. Puntos `adt_conv` y `oru_conv` (S-CV-1, `solo_transformacion`): sin acuse, ni log, ni
canónico. Lo esperado es la proyección «guía», los ConceptMap de v2-to-FHIR 1.0.0, no el canónico del laboratorio (S-CV-3); las
S-n del laboratorio no cuentan contra un tercero. verificador.verificar despacha aquí con una línea; el resto del juez no cambia.

Piezas: leer_bundle (§2.1) -> emparejar (§2.2, por papel) -> juzgar cada recurso con el perfil (§3) -> clases (§4.1) ->
categoría (§1.4). Un hallazgo por campo (fusión por hecho); un recurso ausente absorbe sus datos perdidos.
Etapa 20: `vxu_conv` (VXU^V04) vive en conversion_vxu.py; aquí solo hay cinco ganchos por familia (vx/diseno-vx-fable.md §2.6).
Etapa 26: `mdm_conv` (MDM^T02) vive en conversion_mdm.py; seis ganchos más, una rama «mdm» al lado de cada uno (md/diseno-md.md §3).
  python3 conversion.py --autoprueba      -> los mapas contra el paquete de la guía (si está) y un caso nominal"""
import datetime
import json
import os
import re
import sys

import almacen_oru as AO
import mapeador_referencia as MR
import puntos_entrada as PE

GUIA = "v2-to-FHIR 1.0.0 (ConceptMap) y hojas CSV 873b331"
PAQUETE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "estandares", "v2mappings", "package")
TIPOS_PROY = ("Patient", "Encounter", "Observation", "DiagnosticReport")

# Q-CV-D (Jev, cv/decision-jev-qcv.md). ALTERNATIVA: la otra respuesta de las de confianza baja, para la sensibilidad
# preinscrita (cv/decisiones-qcv.md); con_alternativas() la aplica sin tocar el juez.
DECISIONES = {"Q-CV-D-3": "dato_inventado", "Q-CV-D-5": "nota", "Q-CV-D-6": "recurso_ausente", "Q-CV-D-7": "aceptable",
              "Q-CV-D-8": "codigo_mal_mapeado", "Q-CV-D-9": "solo_fn1", "Q-CV-D-10": "cuenta", "Q-CV-D-11": "las_dos",
              "Q-CV-D-12": "juzgar_con_marca",
              "Q-CV-D-13": "incorrecto", "Q-CV-D-14": "cuenta"}       # CV3 (cv/decision-jev-qcv-cv3.md)
ALTERNATIVA = {"Q-CV-D-3": "convencion", "Q-CV-D-5": "dato_inventado_si_no_esta", "Q-CV-D-9": "las_dos"}

MAPAS = {
    'table-hl70001-to-administrative-gender': {'F': ('http://hl7.org/fhir/administrative-gender', 'female'), 'M': ('http://hl7.org/fhir/administrative-gender', 'male'), 'O': ('http://hl7.org/fhir/administrative-gender', 'other'), 'U': ('http://hl7.org/fhir/administrative-gender', 'unknown'), 'A': ('http://hl7.org/fhir/administrative-gender', 'other'), 'N': ('http://hl7.org/fhir/administrative-gender', 'other')},
    'table-hl70002-to-v3-maritalstatus': {'A': ('http://terminology.hl7.org/CodeSystem/v3-MaritalStatus', 'L'), 'D': ('http://terminology.hl7.org/CodeSystem/v3-MaritalStatus', 'D'), 'M': ('http://terminology.hl7.org/CodeSystem/v3-MaritalStatus', 'M'), 'S': ('http://terminology.hl7.org/CodeSystem/v3-MaritalStatus', 'S'), 'W': ('http://terminology.hl7.org/CodeSystem/v3-MaritalStatus', 'W'), 'C': ('http://terminology.hl7.org/CodeSystem/v3-MaritalStatus', 'C'), 'G': ('http://terminology.hl7.org/CodeSystem/v3-MaritalStatus', 'T'), 'P': ('http://terminology.hl7.org/CodeSystem/v3-MaritalStatus', 'T'), 'R': ('http://terminology.hl7.org/CodeSystem/v3-MaritalStatus', 'T'), 'E': ('http://terminology.hl7.org/CodeSystem/v3-MaritalStatus', 'L'), 'N': ('http://terminology.hl7.org/CodeSystem/v3-MaritalStatus', 'A'), 'I': ('http://terminology.hl7.org/CodeSystem/v3-MaritalStatus', 'I'), 'B': ('http://terminology.hl7.org/CodeSystem/v3-MaritalStatus', 'U'), 'U': ('http://terminology.hl7.org/CodeSystem/v3-NullFlavor', 'UNK'), 'O': ('http://terminology.hl7.org/CodeSystem/v3-NullFlavor', 'OTH'), 'T': ('http://terminology.hl7.org/CodeSystem/v3-NullFlavor', 'NAVU')},
    'table-hl70003-to-encounter-status': {'A01': ('http://hl7.org/fhir/encounter-status', 'in-progress'), 'A02': ('http://hl7.org/fhir/encounter-status', 'in-progress'), 'A03': ('http://hl7.org/fhir/encounter-status', 'finished'), 'A04': ('http://hl7.org/fhir/encounter-status', 'planned'), 'A05': ('http://hl7.org/fhir/encounter-status', 'planned'), 'A08': ('http://hl7.org/fhir/encounter-status', 'unknown'), 'A11': ('http://hl7.org/fhir/encounter-status', 'cancelled'), 'A13': ('http://hl7.org/fhir/encounter-status', 'in-progress')},
    'table-hl70004-to-encounter-status': {'E': ('http://hl7.org/fhir/encounter-status', 'in-progress'), 'I': ('http://hl7.org/fhir/encounter-status', 'in-progress'), 'O': ('http://hl7.org/fhir/encounter-status', 'in-progress'), 'P': ('http://hl7.org/fhir/encounter-status', 'planned'), 'R': ('http://hl7.org/fhir/encounter-status', 'in-progress'), 'B': ('http://hl7.org/fhir/encounter-status', 'in-progress'), 'C': ('http://hl7.org/fhir/encounter-status', 'in-progress'), 'N': ('http://hl7.org/fhir/encounter-status', 'in-progress'), 'U': ('http://hl7.org/fhir/encounter-status', 'unknown')},
    'table-hl70004-to-v3-actcode': {'E': ('http://terminology.hl7.org/CodeSystem/v3-ActCode', 'EMER'), 'I': ('http://terminology.hl7.org/CodeSystem/v3-ActCode', 'IMP'), 'O': ('http://terminology.hl7.org/CodeSystem/v3-ActCode', 'AMB'), 'P': ('http://terminology.hl7.org/CodeSystem/v3-ActCode', 'PRENC'), 'R': ('http://terminology.hl7.org/CodeSystem/v2-0004', 'R'), 'B': ('http://terminology.hl7.org/CodeSystem/v2-0004', 'B'), 'C': ('http://terminology.hl7.org/CodeSystem/v2-0004', 'C'), 'N': ('http://terminology.hl7.org/CodeSystem/v2-0004', 'N'), 'U': ('http://terminology.hl7.org/CodeSystem/v2-0004', 'U')},
    'table-hl70007-to-v2-0007': {'A': ('http://terminology.hl7.org/CodeSystem/v2-0007', 'A'), 'E': ('http://terminology.hl7.org/CodeSystem/v2-0007', 'E'), 'L': ('http://terminology.hl7.org/CodeSystem/v2-0007', 'L'), 'R': ('http://terminology.hl7.org/CodeSystem/v2-0007', 'R'), 'N': ('http://terminology.hl7.org/CodeSystem/v2-0007', 'N'), 'U': ('http://terminology.hl7.org/CodeSystem/v2-0007', 'U'), 'C': ('http://terminology.hl7.org/CodeSystem/v2-0007', 'C')},
    'table-hl70069-to-service-type': {'MED': ('http://terminology.hl7.org/CodeSystem/service-type', '382'), 'URO': ('http://terminology.hl7.org/CodeSystem/service-type', '222'), 'SUR': ('http://terminology.hl7.org/CodeSystem/v2-0069', 'SUR'), 'PUL': ('http://terminology.hl7.org/CodeSystem/v2-0069', 'PUL'), 'CAR': ('http://terminology.hl7.org/CodeSystem/v2-0069', 'CAR')},
    'table-hl70136-to-special-values': {'Y': ('http://terminology.hl7.org/CodeSystem/special-values', 'true'), 'N': ('http://terminology.hl7.org/CodeSystem/special-values', 'false')},
    'table-hl70190-to-address-use': {'BA': ('http://hl7.org/fhir/address-use', 'old'), 'BI': ('http://hl7.org/fhir/address-use', 'billing'), 'C': ('http://hl7.org/fhir/address-use', 'temp'), 'B': ('http://hl7.org/fhir/address-use', 'work'), 'H': ('http://hl7.org/fhir/address-use', 'home'), 'O': ('http://hl7.org/fhir/address-use', 'work'), 'N': None, 'BDL': None, 'F': None, 'L': None, 'M': None, 'P': None, 'RH': None, 'BR': None, 'S': None, 'SH': None, 'TM': None, 'V': None},
    'table-hl70190-to-address-type': {'M': ('http://hl7.org/fhir/address-type', 'postal'), 'SH': ('http://hl7.org/fhir/address-type', 'postal'), 'BA': None, 'BI': None, 'N': None, 'BDL': None, 'F': None, 'C': None, 'B': None, 'H': None, 'L': None, 'O': None, 'P': None, 'RH': None, 'BR': None, 'S': None, 'TM': None, 'V': None},
    'table-hl70200-to-name-use': {'BAD': ('http://hl7.org/fhir/name-use', 'old'), 'D': ('http://hl7.org/fhir/name-use', 'usual'), 'L': ('http://hl7.org/fhir/name-use', 'official'), 'M': ('http://hl7.org/fhir/name-use', 'maiden'), 'MSK': ('http://hl7.org/fhir/name-use', 'anonymous'), 'N': ('http://hl7.org/fhir/name-use', 'nickname'), 'NAV': ('http://hl7.org/fhir/name-use', 'temp'), 'R': ('http://hl7.org/fhir/name-use', 'official'), 'TEMP': ('http://hl7.org/fhir/name-use', 'temp'), 'A': None, 'B': None, 'C': None, 'F': None, 'I': None, 'K': None, 'NB': None, 'NOUSE': None, 'P': None, 'REL': None, 'S': None, 'T': None, 'U': None},
    'table-hl70201-to-contact-point-use': {'PRN': ('http://hl7.org/fhir/contact-point-use', 'home'), 'WPN': ('http://hl7.org/fhir/contact-point-use', 'work'), 'PRS': ('http://hl7.org/fhir/contact-point-use', 'mobile'), 'ORN': None, 'VHN': None, 'ASN': None, 'EMR': None, 'NET': None, 'BPN': None},
    'table-hl70202-to-contact-point-system': {'PH': ('http://hl7.org/fhir/contact-point-system', 'phone'), 'FX': ('http://hl7.org/fhir/contact-point-system', 'fax'), 'MD': ('http://hl7.org/fhir/contact-point-system', 'other'), 'SAT': ('http://hl7.org/fhir/contact-point-system', 'other'), 'BP': ('http://hl7.org/fhir/contact-point-system', 'pager'), 'Internet': ('http://hl7.org/fhir/contact-point-system', 'email'), 'X.400': ('http://hl7.org/fhir/contact-point-system', 'email'), 'TDD': ('http://hl7.org/fhir/contact-point-system', 'other'), 'TTY': ('http://hl7.org/fhir/contact-point-system', 'other'), 'CP': ('http://hl7.org/fhir/contact-point-use', 'mobile')},
    'table-hl70078-to-v3-observationinterpretation': {'<': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', '<'), '>': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', '>'), 'A': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'A'), 'AA': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'AA'), 'B': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'B'), 'CAR': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'CAR'), 'D': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'D'), 'DET': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'DET'), 'E': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'E'), 'EX': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'EX'), 'EXP': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'EXP'), 'H': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'H'), 'HH': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'HH'), 'HU': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'HU'), 'I': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'I'), 'IE': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'IE'), 'IND': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'IND'), 'L': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'L'), 'LL': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'LL'), 'LU': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'LU'), 'MS': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'MS'), 'N': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'N'), 'NCL': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'NCL'), 'ND': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'ND'), 'NEG': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'NEG'), 'NR': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'NR'), 'NS': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'NS'), 'POS': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'POS'), 'R': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'R'), 'RR': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'RR'), 'S': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'S'), 'SDD': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'SDD'), 'SYN-R': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'SYN-R'), 'SYN-S': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'SYN-S'), 'U': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'U'), 'VS': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'VS'), 'UNE': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'UNE'), 'W': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'W'), 'WR': ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'WR'), 'AC': None, 'HM': None, 'OBX': None, 'QCF': None, 'TOX': None},
    'table-hl70085-to-observation-status': {'A': ('http://hl7.org/fhir/observation-status', 'amended'), 'C': ('http://hl7.org/fhir/observation-status', 'corrected'), 'D': ('http://hl7.org/fhir/observation-status', 'entered-in-error'), 'F': ('http://hl7.org/fhir/observation-status', 'final'), 'P': ('http://hl7.org/fhir/observation-status', 'preliminary'), 'X': ('http://hl7.org/fhir/observation-status', 'cancelled'), 'W': ('http://hl7.org/fhir/observation-status', 'entered-in-error'), 'B': None, 'I': None, 'N': None, 'O': None, 'R': None, 'S': None, 'V': None, 'U': None},
    'table-hl70123-queries-to-diagnostic-report-status': {'O': ('http://hl7.org/fhir/diagnostic-report-status', 'registered'), 'I': ('http://hl7.org/fhir/diagnostic-report-status', 'registered'), 'S': ('http://hl7.org/fhir/diagnostic-report-status', 'registered'), 'P': ('http://hl7.org/fhir/diagnostic-report-status', 'preliminary'), 'C': ('http://hl7.org/fhir/diagnostic-report-status', 'corrected'), 'R': ('http://hl7.org/fhir/diagnostic-report-status', 'partial'), 'F': ('http://hl7.org/fhir/diagnostic-report-status', 'final'), 'X': ('http://hl7.org/fhir/diagnostic-report-status', 'cancelled'), 'A': None, 'Y': None, 'Z': None, 'M': None, 'N': None},
}

CM = {"0001": "table-hl70001-to-administrative-gender", "0002": "table-hl70002-to-v3-maritalstatus",
      "0003": "table-hl70003-to-encounter-status", "0004s": "table-hl70004-to-encounter-status",
      "0004c": "table-hl70004-to-v3-actcode", "0007": "table-hl70007-to-v2-0007", "0069": "table-hl70069-to-service-type",
      "0136": "table-hl70136-to-special-values", "0190u": "table-hl70190-to-address-use", "0190t": "table-hl70190-to-address-type",
      "0200": "table-hl70200-to-name-use", "0201": "table-hl70201-to-contact-point-use",
      "0202": "table-hl70202-to-contact-point-system", "0078": "table-hl70078-to-v3-observationinterpretation",
      "0085": "table-hl70085-to-observation-status", "0123": "table-hl70123-queries-to-diagnostic-report-status"}
FUERA = "fuera"                                                     # el código no está en el source del ConceptMap
GENERO_FHIR = {"male", "female", "other", "unknown"}
URI_SISTEMA = {"LN": "http://loinc.org", "SCT": "http://snomed.info/sct", "SNM": "http://snomed.info/sct",
               "SNM3": "http://snomed.info/sct", "UCUM": "http://unitsofmeasure.org", "ISO+": "http://unitsofmeasure.org"}  # L-CV-3
PARTICIPANTE = {7: "ATND", 8: "REF", 9: "CON", 17: "ADM", 52: "PART"}                        # PV1_Encounter.csv:14-25,37-40,80-83
UBICACION = {3: None, 6: "completed", 11: "active", 42: "reserved"}                         # PV1_Encounter.csv:7-9,12-13,27-31,68-69
V2_0203 = "http://terminology.hl7.org/CodeSystem/v2-0203"


def mapa(tabla, codigo):
    """(system, code) destino | None (unmatched: sin destino) | FUERA (no está en el source)."""
    m = MAPAS[CM[tabla]]
    return m[codigo] if codigo in m else FUERA


# ---------------------------------------------------------------------------- citas (§3.7)
C = {"PID-3": ["[CM datatype-cx-to-identifier CX.1 → value, CX.4 → system/assigner, CX.5 → type]", "[G PID_Patient.csv:6]"],
     "PID-5": ["[CM datatype-xpn-to-humanname]", "[CM table-hl70200-to-name-use]", "[G PID_Patient.csv:8]"],
     "PID-7": ["[CM segment-pid-to-patient PID-7 → birthDate]", "[G PID_Patient.csv:11-13]", "[E2A §2.A.22 DTM]"],
     "PID-8": ["[CM table-hl70001-to-administrative-gender]", "[G PID_Patient.csv:14]", "[F Patient.gender required]"],
     "PID-11": ["[CM datatype-xad-to-address]", "[CM table-hl70190-to-address-use/-type]", "[G PID_Patient.csv:17]"],
     "PID-13": ["[CM datatype-xtn-to-contactpoint]", "[CM table-hl70201/0202]", "[G PID_Patient.csv:22-25]"],
     "PID-16": ["[CM table-hl70002-to-v3-maritalstatus]", "[G PID_Patient.csv:27]"],
     "PID-29": ["[CM segment-pid-to-patient PID-29 → deceasedDateTime]", "[G PID_Patient.csv:50]"],
     "PID-30": ["[CM table-hl70136-to-special-values]", "[G PID_Patient.csv:51]"],
     "PV1": ["[G MSG_ADT_A01.csv:36] PV1 → Encounter[1]"], "PID": ["[G MSG_ADT_A01.csv:15] PID → Patient[1]"],
     "PV1-2": ["[CM table-hl70004-to-v3-actcode]", "[CM table-hl70004-to-encounter-status]", "[G PV1_Encounter.csv:5-6]"],
     "MSH-9": ["[CM table-hl70003-to-encounter-status]", "[CM message-adt-a11-to-bundle]"],
     "PV1-4": ["[CM table-hl70007-to-v2-0007]", "[G PV1_Encounter.csv:10]"],
     "PV1-10": ["[CM table-hl70069-to-service-type]", "[G PV1_Encounter.csv:26]"],
     "PV1-19": ["[CM segment-pv1-to-encounter PV1-19]", "[G PV1_Encounter.csv:42-45]"],
     "PV1-44": ["[G PV1_Encounter.csv:71]"], "PV1-45": ["[G PV1_Encounter.csv:72-73]"],
     "PV1-14": ["[G PV1_Encounter.csv:34]"], "PV1-36": ["[G PV1_Encounter.csv:62]"],
     "PV1-loc": ["[CM datatype-pl-to-location]", "[G PV1_Encounter.csv:7-9,12-13,27-31,68-69]"],
     "PV1-par": ["[CM datatype-xcn-to-practitioner]", "[G PV1_Encounter.csv:14-25,37-40,80-83]"],
     "OBX-11": ["[CM table-hl70085-to-observation-status]", "[G OBX_Observation.csv:43-48]"],
     "OBX-3": ["[CM datatype-ce-to-codeableconcept]", "[G OBX_Observation.csv:6]"],
     "OBX-5": ["[CM segment-obx-to-observation OBX-5]", "[G OBX_Observation.csv:8-26]"],
     "OBX-6": ["[CM datatype-cwe-to-quantity]", "[G OBX_Observation.csv:32-37]"],
     "OBX-7": ["[CM segment-obx-to-observation OBX-7]", "[G OBX_Observation.csv:38]"],
     "OBX-8": ["[CM table-hl70078-to-v3-observationinterpretation]", "[G OBX_Observation.csv:39]"],
     "OBX-14": ["[CM segment-obx-to-observation OBX-14]", "[G OBX_Observation.csv:51]"],
     "OBR": ["[G MSG_ORU_R01.csv:44,53]"], "OBX": ["[G MSG_ORU_R01.csv:67-69]"],
     "OBR-2": ["[CM segment-obr-to-diagnosticreport OBR-2/OBR-3]", "[G OBR_DiagnosticReport.csv:5-10]"],
     "OBR-4": ["[G OBR_DiagnosticReport.csv:11]"], "OBR-7": ["[G OBR_DiagnosticReport.csv:14-16]"],
     "OBR-22": ["[G OBR_DiagnosticReport.csv:30]"], "OBR-25": ["[CM table-hl70123-queries-to-diagnostic-report-status]"],
     "ref": ["[F Bundle «Resolving references in Bundles»]"]}


def _cit(clave):
    base = re.sub(r"\(\d+\)", "", clave)
    return C.get(clave) or C.get(base) or C.get(base.split("-")[0], [])


# ---------------------------------------------------------------------------- hallazgos
def _h(clase, subtipo, hecho, que, cuenta=True, certeza="literal", citas=None, evidencia=None):
    return {"mensaje": 0, "clase": clase, "subtipo": subtipo, "hecho": hecho, "que": [que], "origen": ["conversion"],
            "cuenta": cuenta, "certeza": certeza, "causa": None, "alternativa": None, "nivel": None, "estado": "firme",
            "opinion_circuito": None, "evidencia": evidencia or {}, "citas": list(citas or _cit(hecho)),
            "clase_cv": None if cuenta else ("convencion" if subtipo == "convencion" else None)}


class Juicio:
    """Lo que se va juzgando de un mensaje: los hallazgos, la versión y las entries referidas desde la proyección."""

    def __init__(self, m, v25, dec):
        self.m, self.v25, self.dec, self.hs, self.referidas = m, v25, dec, [], set()

    def cuenta(self, subtipo, hecho, que, clase="fidelidad", tabla=False, citas=None):
        """tabla=True: el hallazgo depende de que un código esté en una tabla de v2.5. Con MSH-12 ≠ 2.5 no cuenta (L18, S-CV-6)."""
        if tabla and not self.v25:
            self.hs.append(_h("nota", "version", hecho, que + " [L18: no se comprueba fuera de 2.5]", cuenta=False,
                              certeza="ambiguedad L18", citas=citas))
        else:
            self.hs.append(_h(clase, subtipo, hecho, que, citas=citas))

    def nota(self, subtipo, hecho, que, certeza="literal"):
        self.hs.append(_h("nota", subtipo, hecho, que, cuenta=False, certeza=certeza))


def _fusionar(hs):
    """§4.1: un hallazgo que cuenta por campo (hecho); las notas, una por (hecho, subtipo)."""
    out, idx = [], {}
    for h in hs:
        k = (h["hecho"], "c") if h["cuenta"] else (h["hecho"], h["subtipo"], "n")
        if k in idx:
            g = idx[k]
            g["que"] += [q for q in h["que"] if q not in g["que"]]
            g["citas"] += [c for c in h["citas"] if c not in g["citas"]]
            subs = g["subtipo"].split("+")
            if h["subtipo"] not in subs:
                g["subtipo"] = "+".join(subs + [h["subtipo"]])
        else:
            idx[k] = h
            out.append(h)
    return out


# ---------------------------------------------------------------------------- el mensaje
def _seg(m, nombre):
    s = m.segmentos(nombre)
    return s[0] if s else None


def _f(m, seg, n):
    return m.campo(seg, n) if seg else ""


def _reps(m, v):
    return [r for r in (v or "").split(m.r) if r]


def _comp(m, rep, i):
    ps = (rep or "").split(m.c)
    return ps[i - 1] if i <= len(ps) else ""


def _sub(m, comp, i):
    ps = (comp or "").split(m.s)
    return ps[i - 1] if i <= len(ps) else ""


def _d(m, x):
    return m.desescapa(x) if x and x != '""' else ""


def _t(m, rep, i, k=1):
    """Componente i (subcomponente k) desescapado."""
    return _d(m, _sub(m, _comp(m, rep, i), k))


# ---------------------------------------------------------------------------- lectura del Bundle (§2.1)
def leer_bundle(texto, tipos=TIPOS_PROY):
    """-> (entries, notas) o (None, [motivo]). Entry: {i, fullUrl, tipo, id, r, padre}; contained -> fullUrl «#id», padre = i."""
    d, motivo = AO.parsear(texto)
    if d is None:
        return None, [motivo]
    notas = []
    if d.get("resourceType") != "Bundle":
        if d.get("resourceType") in tipos:
            d, notas = {"resourceType": "Bundle", "entry": [{"resource": d}]}, ["recurso_suelto"]
        else:
            return None, ["ni Bundle ni recurso proyectado (resourceType %r)" % d.get("resourceType")]
    entries = []
    for i, en in enumerate(d.get("entry") or []):
        if not isinstance(en, dict) or not isinstance(en.get("resource"), dict):
            notas.append("entry %d sin resource" % i)
            continue
        r = en["resource"]
        entries.append({"i": i, "fullUrl": en.get("fullUrl"), "tipo": r.get("resourceType"), "id": r.get("id"), "r": r, "padre": None})
        for c in r.get("contained") or []:
            if isinstance(c, dict):
                entries.append({"i": i, "fullUrl": "#%s" % c.get("id"), "tipo": c.get("resourceType"), "id": c.get("id"), "r": c, "padre": i})
    return entries, notas


def resolver(entries, ref, desde=None, tipo=None):
    """R4 «Resolving references in Bundles»: fullUrl, Tipo/id, sufijo, #contained; Reference.identifier es referencia lógica
    (convención). -> (entry | None, forma)."""
    if not isinstance(ref, dict):
        return None, "ausente"
    s = ref.get("reference")
    if isinstance(s, str) and s:
        if s.startswith("#"):
            for e in entries:
                if desde is not None and e["padre"] == desde["i"] and e["fullUrl"] == s:
                    return e, "contained"
            return None, "rota"
        for e in entries:
            if e["padre"] is None and e["fullUrl"] == s:
                return e, "fullUrl"
        for e in entries:
            if e["padre"] is None and e["tipo"] and e["id"] and "%s/%s" % (e["tipo"], e["id"]) == s:
                return e, "relativa"
        for e in entries:
            if e["padre"] is None and isinstance(e["fullUrl"], str) and e["fullUrl"].endswith("/" + s):
                return e, "sufijo"
        return None, "rota"
    ide = ref.get("identifier")
    if isinstance(ide, dict) and ide.get("value"):
        cs = [e for e in entries if e["padre"] is None and (tipo is None or e["tipo"] == tipo) and ide.get("value") in _valores(e["r"])]
        return (cs[0] if len(cs) == 1 else None), "logica"
    return None, "display" if ref.get("display") else "ausente"


def _valores(r):
    return {x.get("value") for x in r.get("identifier") or [] if isinstance(x, dict) and x.get("value")}


def _codigos(cc):
    return [(c.get("system"), c.get("code")) for c in (cc or {}).get("coding") or [] if isinstance(c, dict)] if isinstance(cc, dict) else []


# ---------------------------------------------------------------------------- emparejamiento (§2.2)
def _grupos_oru(m):
    """[(OBR, [OBX…])] por ORDER_OBSERVATION; los OBX fuera de un OBR (PATIENT_OBSERVATION, bajo SPM) solo se cuentan (L-CV-7)."""
    grupos, fuera, ctx = [], 0, None
    for s in m.segs:
        n = s.split(m.f)[0]
        if n == "OBR":
            grupos.append((s, []))
            ctx = "obr"
        elif n == "SPM":
            ctx = "spm"
        elif n == "OBX":
            if ctx == "obr":
                grupos[-1][1].append(s)
            else:
                fuera += 1
    return grupos, fuera


def leer_y_emparejar(m, texto, familia):
    entries, notas = leer_bundle(texto, CVX.TIPOS if familia == "vxu" else CVM.TIPOS if familia == "mdm" else TIPOS_PROY)  # gancho 3 (20) y 1 (26)
    if entries is None:
        return {"recursos": [], "sobrantes": [], "otros_tipos": {}, "referencias_rotas": [], "fallos": notas, "ambiguo": [],
                "entries": None}
    return emparejar(m, entries, familia, notas)


def emparejar(m, entries, familia, notas=()):
    out = {"recursos": [], "sobrantes": [], "otros_tipos": {}, "referencias_rotas": [], "fallos": list(notas), "ambiguo": [],
           "entries": entries}
    top = [e for e in entries if e["padre"] is None]
    usados = set()

    def rol(nombre, origen, e, por, n):
        out["recursos"].append({"rol": nombre, "origen": origen, "observado": e["r"] if e else None, "entry": e,
                                "fullUrl": e["fullUrl"] if e else None, "emparejado_por": por, "candidatos": n})
        if e:
            usados.add(e["i"])

    pid = _seg(m, "PID")
    pats = [e for e in top if e["tipo"] == "Patient"]
    pat = None
    if pid is not None:
        ids3 = {_t(m, r, 1) for r in _reps(m, _f(m, pid, 3))} - {""}
        if len(pats) == 1:
            pat, por = pats[0], "unico"
        else:
            cs = [e for e in pats if _valores(e["r"]) & ids3]
            if len(cs) == 1:
                pat, por = cs[0], "identifier"
            elif len(cs) > 1:
                out["ambiguo"].append("Patient#1")
                pat, por = None, "ambiguo"
            else:
                refs = [resolver(entries, e["r"].get("subject"), e, "Patient")[0] for e in top if e["tipo"] in TIPOS_PROY[1:]]
                refs = {x["i"]: x for x in refs if x and x["tipo"] == "Patient"}
                pat, por = (list(refs.values())[0], "referencia") if len(refs) == 1 else (None, None)
        rol("Patient#1", "PID", pat, por, len(pats))
    for e in pats:
        if e is not pat and pid is not None and pat is not None:
            out["sobrantes"].append({"resourceType": "Patient", "fullUrl": e["fullUrl"], "motivo": "duplicado", "hecho": "PID"})
            usados.add(e["i"])

    def sujeto_es_pat(e):
        x, _ = resolver(entries, e["r"].get("subject"), e, "Patient")
        return pat is not None and x is pat

    if familia == "vxu":                                            # gancho 4 (etapa 20): Immunization, Observation, NK1, PV1
        CVX.emparejar(m, entries, top, out, pat, rol, usados)
    elif familia == "mdm":                                          # gancho 2 (etapa 26): DocumentReference, ServiceRequest, PV1
        CVM.emparejar(m, entries, top, out, pat, rol, usados)
    elif familia == "adt":
        pv1 = _seg(m, "PV1")
        encs = [e for e in top if e["tipo"] == "Encounter"]
        en = None
        if pv1 is not None:
            v19 = _t(m, _f(m, pv1, 19), 1)
            if len(encs) == 1:
                en, por = encs[0], "unico"
            elif encs:
                s = [e for e in encs if sujeto_es_pat(e)]
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
                    en, por = None, "ambiguo"
            else:
                por = None
            rol("Encounter#1", "PV1", en, por, len(encs))
        for e in encs:
            if e is not en and en is not None:
                out["sobrantes"].append({"resourceType": "Encounter", "fullUrl": e["fullUrl"], "motivo": "duplicado", "hecho": "PV1"})
                usados.add(e["i"])
        n_obx = len(m.segmentos("OBX"))
        obs = [e for e in top if e["tipo"] in ("Observation", "DiagnosticReport")]
        for k, e in enumerate(obs):
            motivo = "origen_guia" if e["tipo"] == "Observation" and k < n_obx else "inventado"
            out["sobrantes"].append({"resourceType": e["tipo"], "fullUrl": e["fullUrl"], "motivo": motivo,
                                     "hecho": "OBX" if e["tipo"] == "Observation" else "OBR"})
            usados.add(e["i"])
    else:
        grupos, fuera = _grupos_oru(m)
        drs = [e for e in top if e["tipo"] == "DiagnosticReport"]
        ob = [e for e in top if e["tipo"] == "Observation"]
        libres = list(drs)
        asignados = {}
        for i, (obr, _) in enumerate(grupos, 1):
            fill, plac, cod = _t(m, _f(m, obr, 3), 1), _t(m, _f(m, obr, 2), 1), _t(m, _f(m, obr, 4), 1)
            c = [e for e in libres if (fill and fill in _valores(e["r"])) or (plac and plac in _valores(e["r"]))]
            por = "identifier"
            if not c:
                c, por = [e for e in libres if cod and cod in {x[1] for x in _codigos(e["r"].get("code"))}][:1], "codigo"
            if not c and len(drs) == len(grupos) and libres:
                c, por = libres[:1], "orden"
            d = c[0] if c else None
            if d:
                libres.remove(d)
            asignados[i] = d
            rol("DiagnosticReport#%d" % i, "OBR %d" % i, d, por if d else None, len(drs))
        referidas = {}
        for i, d in asignados.items():
            for rr in (d["r"].get("result") or []) if d else []:
                x, _ = resolver(entries, rr, d, "Observation")
                if x:
                    referidas.setdefault(x["i"], i)
        libres_o = list(ob)
        for i, (obr, obxs) in enumerate(grupos, 1):
            d = asignados[i]
            propias = []
            for rr in (d["r"].get("result") or []) if d else []:
                x, _ = resolver(entries, rr, d, "Observation")
                if x:
                    propias.append(x)
            for j, obx in enumerate(obxs, 1):
                cod, sub = _t(m, _f(m, obx, 3), 1), _f(m, obx, 4)
                cands = [x for x in propias if x in libres_o and cod in {c[1] for c in _codigos(x["r"].get("code"))}]
                por = "referencia"
                if not cands:
                    glob = [x for x in libres_o if cod and cod in {c[1] for c in _codigos(x["r"].get("code"))}]
                    cands = sorted(glob, key=lambda x: x["i"] in referidas)
                    por = "codigo"
                if len(cands) > 1 and sub:
                    porsub = [x for x in cands if sub in _valores(x["r"])]
                    cands = porsub or cands
                o = cands[0] if cands else None
                if o:
                    libres_o.remove(o)
                rol("Observation#%d.%d" % (i, j), "OBX %d.%d" % (i, j), o, por if o else None, len(ob))
        for d in libres:
            out["sobrantes"].append({"resourceType": "DiagnosticReport", "fullUrl": d["fullUrl"], "motivo": "inventado", "hecho": "OBR"})
            usados.add(d["i"])
        for k, o in enumerate(libres_o):
            out["sobrantes"].append({"resourceType": "Observation", "fullUrl": o["fullUrl"],
                                     "motivo": "origen_guia" if k < fuera else "inventado", "hecho": "OBX"})
            usados.add(o["i"])
    out["_usados"] = usados
    alcanzadas = _alcanzadas(entries, [x["entry"] for x in out["recursos"] if x["entry"]])
    for e in top:                                    # L-CV-5: fuera de la proyección y sin referencia desde ella -> solo recuento
        if e["i"] not in usados and e["i"] not in alcanzadas and e["tipo"] not in (CVX.TIPOS if familia == "vxu" else CVM.TIPOS if familia == "mdm"
                                                                                   else TIPOS_PROY):        # gancho 3 (etapa 26)
            out["otros_tipos"][e["tipo"]] = out["otros_tipos"].get(e["tipo"], 0) + 1
    return out


def _referencias(obj):
    if isinstance(obj, dict):
        if isinstance(obj.get("reference"), str):
            yield obj
        for v in obj.values():
            yield from _referencias(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _referencias(v)


def _alcanzadas(entries, desde):
    """Las entries a las que se llega por referencia (transitiva) desde los recursos emparejados: Practitioner, Location y su
    cadena partOf, Organization de un assigner… Se leen como destino de una referencia y no se cuentan como otros_tipos."""
    vistas, pila = set(), list(desde)
    while pila:
        e = pila.pop()
        for ref in _referencias(e["r"]):
            x, _ = resolver(entries, ref, e)
            if x is not None and x["i"] not in vistas:
                vistas.add(x["i"])
                pila.append(x)
    return vistas


# ---------------------------------------------------------------------------- fechas (§3.6, R-CV-7)
FHIR_DT = re.compile(r"^(\d{4})(?:-(\d{2})(?:-(\d{2})(?:T(\d{2}):(\d{2})(?::(\d{2})(\.\d+)?)?(Z|[+-]\d{2}:\d{2})?)?)?)?$")


def _instante(y, mo, d, hh, mi, ss, z):
    """Minutos desde una época común (z: «±HHMM», «±HH:MM» o «Z»)."""
    t = datetime.datetime(int(y), int(mo), int(d), int(hh), int(mi), int(ss or 0))
    if z in (None, "Z"):
        off = 0
    else:
        zz = z.replace(":", "")
        off = (1 if zz[0] == "+" else -1) * (int(zz[1:3]) * 60 + int(zz[3:5]))
    return (t - datetime.datetime(1970, 1, 1)).total_seconds() / 60 - off


def _fecha(J, hecho, origen, obs, tipo, ruta):
    """tipo: date (birthDate, solo fecha y sin desplazar, AMB-CV-4), dateTime o instant."""
    if not origen:
        if obs is not None:
            J.cuenta("dato_inventado", hecho, "%s: %r presente sin %s" % (ruta, obs, hecho))
        return
    partes, _ = MR.partes_dtm(origen)
    if partes is None:
        if obs is not None:
            J.cuenta("valor_imposible_convertido", hecho, "%s: %r convertido desde un DTM imposible %r" % (ruta, obs, origen),
                     clase="valor_imposible_aceptado")
        return
    if obs is None:
        J.cuenta("dato_perdido", hecho, "%s: falta (%s = %r)" % (ruta, hecho, origen))
        return
    mo = FHIR_DT.match(obs) if isinstance(obs, str) else None
    if not mo:
        J.cuenta("fhir_invalido", hecho, "%s: %r no es un %s de FHIR R4" % (ruta, obs, tipo))
        return
    oy, omo, od, oh, omi, os_, ofr, oz = mo.groups()
    y, m_, d, hh, mi, ss, fr, z = partes
    if tipo == "date":
        if oh is not None:
            J.cuenta("fhir_invalido", hecho, "%s: %r lleva hora (date)" % (ruta, obs))
            return
        esp, ob = [x for x in (y, m_, d) if x], [x for x in (oy, omo, od) if x]
        _precision(J, hecho, ruta, esp, ob, origen, obs)
        return
    if oh is not None and oz is None:
        J.cuenta("fhir_invalido", hecho, "%s: %r con hora y sin zona" % (ruta, obs))
        return
    if hh is None:
        if oh is not None:
            if tipo == "instant":
                if [oy, omo, od] != [y, m_ or "01", d or "01"]:
                    J.cuenta("valor_distinto", hecho, "%s: esperado %r, observado %r" % (ruta, origen, obs))
                else:
                    J.nota("convencion", hecho, "%s: %r completado desde %r (AMB-CV-9)" % (ruta, obs, origen), "ambiguedad AMB-CV-9")
            else:
                J.cuenta("dato_inventado", hecho, "%s: %r añade hora a %r" % (ruta, obs, origen))
            return
        _precision(J, hecho, ruta, [x for x in (y, m_, d) if x], [x for x in (oy, omo, od) if x], origen, obs)
        return
    if oh is None:
        J.cuenta("dato_perdido", hecho, "%s: %r pierde la hora de %r" % (ruta, obs, origen))
        return
    if (mi is None and omi != "00") or (ss is None and os_ not in (None, "00")):
        J.cuenta("dato_inventado", hecho, "%s: %r añade precisión a %r" % (ruta, obs, origen))
        return
    if ss is not None and os_ is None:
        J.cuenta("dato_perdido", hecho, "%s: %r pierde los segundos de %r" % (ruta, obs, origen))
        return
    if fr and (ofr or "").rstrip("0") != fr.rstrip("0"):
        J.cuenta("dato_perdido" if not ofr else "valor_distinto", hecho, "%s: fracción %r frente a %r" % (ruta, ofr, fr))
        return
    if z:
        igual = _instante(y, m_, d, hh, mi or 0, ss, z) == _instante(oy, omo, od, oh, omi, os_, oz)
    else:                                                   # sin zona: «local time zone of the sender»; se conserva la hora escrita
        igual = [y, m_, d, hh, mi or "00", ss or "00"] == [oy, omo, od, oh, omi, os_ or "00"]
    if not igual:
        J.cuenta("valor_distinto", hecho, "%s: esperado %r, observado %r" % (ruta, origen, obs))


def _precision(J, hecho, ruta, esp, ob, origen, obs):
    if len(ob) > len(esp):
        J.cuenta("dato_inventado", hecho, "%s: %r añade precisión a %r" % (ruta, obs, origen))
    elif len(ob) < len(esp):
        J.cuenta("dato_perdido", hecho, "%s: %r pierde precisión de %r" % (ruta, obs, origen))
    elif ob != esp:
        J.cuenta("valor_distinto", hecho, "%s: esperado %r, observado %r" % (ruta, origen, obs))


# ---------------------------------------------------------------------------- Patient (§3.1)
def _patient(J, m, pid, r, entries):
    _identifier(J, m, _f(m, pid, 3), r, "PID-3", "Patient")
    _nombres(J, m, _f(m, pid, 5), r)
    _fecha(J, "PID-7", _t(m, _f(m, pid, 7), 1), r.get("birthDate"), "date", "Patient.birthDate")
    _genero(J, m, _d(m, _f(m, pid, 8)), r.get("gender"))
    _fallecido(J, m, pid, r)
    _direcciones(J, m, _f(m, pid, 11), r, _d(m, _f(m, pid, 12)))
    _telecom(J, m, pid, r)
    _codigo_tabla(J, "PID-16", _t(m, _f(m, pid, 16), 1), r.get("maritalStatus"), "0002", "Patient.maritalStatus")


def _identifier(J, m, campo, r, hecho, recurso, tipo_fijo=None):
    """CV3 (DV-CV-15): `tipo_fijo` es el tipo que la hoja del segmento pone a mano (PV1-19 → «VN», PV1_Encounter.csv:43);
    la guía admite ese o el de CX.5 (CM datatype-cx-to-identifier)."""
    obs = [x for x in r.get("identifier") or [] if isinstance(x, dict)]
    usados = set()
    for rep in _reps(m, campo):
        v, tipo, hd = _t(m, rep, 1), _t(m, rep, 5), _comp(m, rep, 4)
        if not v:
            continue
        cs = [k for k, x in enumerate(obs) if x.get("value") == v and k not in usados]
        if not cs:
            J.cuenta("dato_perdido", hecho, "%s.identifier: falta %r" % (recurso, v))
            continue
        admitidos = {tipo, tipo_fijo} - {None, ""}
        k = next((k for k in cs if not tipo or admitidos & {c[1] for c in _codigos(obs[k].get("type"))}), cs[0])
        usados.add(k)
        x = obs[k]
        if tipo and not admitidos & {c[1] for c in _codigos(x.get("type"))}:
            J.cuenta("valor_distinto", hecho, "%s.identifier %r type: esperado %r, observado %r" %
                     (recurso, v, tipo, [c[1] for c in _codigos(x.get("type"))]))
        ns, uid = _d(m, _sub(m, hd, 1)), _d(m, _sub(m, hd, 2))
        if ns or uid:
            a = x.get("assigner") if isinstance(x.get("assigner"), dict) else {}
            textos = [x.get("system") or "", a.get("display") or "", a.get("reference") or "",
                      ((a.get("identifier") or {}).get("value") or "") if isinstance(a.get("identifier"), dict) else ""]
            ae, _ = resolver(J.entries, a, None, "Organization") if a.get("reference") else (None, None)
            if ae:
                textos += [ae["r"].get("name") or ""] + list(_valores(ae["r"]))
                J.referidas.add(ae["i"])
            # CV4 (CV3, M-36 y L-24): el conversor lleva CX.4 a system transformado («urn:id:NIST_MPI»); sin espacios ni signos
            nsn, uidn = _plano(ns), _plano(uid)
            if not any((nsn and nsn in _plano(t)) or (uidn and uidn in _plano(t)) for t in textos):
                J.cuenta("dato_perdido", hecho, "%s.identifier %r: CX.4 %r sin system ni assigner" % (recurso, v, hd))
    extra = [x.get("value") for k, x in enumerate(obs) if k not in usados]
    if extra:
        _extra(J, m, hecho, "%s.identifier de más: %r" % (recurso, extra), extra)


def _plano(s):
    """Minúsculas, solo letras y dígitos: para buscar un texto de HL7 dentro de un system o un nombre que lo transforma."""
    return re.sub(r"[^0-9a-z]", "", (s or "").lower())


def _extra(J, m, hecho, que, valores):
    """Q-CV-D-5: una entrada de más en un elemento repetible es nota; con la alternativa, dato inventado si el valor no está
    en ningún campo del mensaje."""
    if J.dec["Q-CV-D-5"] == "dato_inventado_si_no_esta" and any(v and v not in "\r".join(m.segs) for v in valores):
        J.cuenta("dato_inventado", hecho, que)
    else:
        J.nota("extra", hecho, que)


def _nombres(J, m, campo, r):
    obs = [x for x in r.get("name") or [] if isinstance(x, dict)]
    usados = set()
    for rep in _reps(m, campo):
        fn = _comp(m, rep, 1)
        fam = _d(m, _sub(m, fn, 1))
        fam_entero = " ".join(x for x in (_d(m, _sub(m, fn, k)) for k in range(1, 6)) if x)
        g1, g2, suf4, pre5, suf6, uso, suf14 = (_t(m, rep, k) for k in (2, 3, 4, 5, 6, 7, 14))
        if not (fam or g1 or g2):
            continue
        familias = {fam} | ({fam_entero} if J.dec["Q-CV-D-9"] == "las_dos" else set())
        opciones = []
        for parte2 in ([g2], g2.split()) if g2 else ([],):
            opciones.append(([g1] if g1 else []) + [x for x in parte2 if x])
        libres = [k for k in range(len(obs)) if k not in usados]
        k = next((k for k in libres if obs[k].get("family") in familias and (obs[k].get("given") or [None])[0] == (g1 or g2.split()[0] if (g1 or g2) else None)), None)
        if k is None:
            k = next((k for k in libres if obs[k].get("family") in familias), None)
        if k is None:
            k = next((k for k in libres if g1 and (obs[k].get("given") or [None])[0] == g1), None)
        if k is None:
            J.cuenta("dato_perdido", "PID-5", "Patient.name: falta %r" % rep)
            continue
        usados.add(k)
        x = obs[k]
        if fam and x.get("family") not in familias:
            J.cuenta("valor_distinto", "PID-5", "Patient.name.family: esperado %r, observado %r" % (sorted(familias), x.get("family")))
        if (g1 or g2) and list(x.get("given") or []) not in opciones:
            J.cuenta("valor_distinto", "PID-5", "Patient.name.given: esperado %r, observado %r" % (opciones, x.get("given")))
        if pre5 and pre5 not in (x.get("prefix") or []):
            J.cuenta("dato_perdido", "PID-5", "Patient.name.prefix: falta %r" % pre5)
        for s in (suf4, suf6, suf14):
            if s and s not in (x.get("suffix") or []):
                J.cuenta("dato_perdido", "PID-5", "Patient.name.suffix: falta %r" % s)
        _uso(J, "PID-5", uso, x.get("use"), "0200", "Patient.name.use")
    if len(obs) > len(usados):
        J.nota("extra", "PID-5", "Patient.name de más: %d" % (len(obs) - len(usados)))


def _uso(J, hecho, codigo, obs, tabla, ruta):
    """Un `use` o `status` de valor único mapeado por un ConceptMap (§3.1): mapeado -> debe ser el destino; unmatched -> ausente
    (Q-CV-D-8: presente es código mal mapeado); vacío -> ausente (presente: dato inventado); fuera de la tabla -> convención."""
    if not codigo:
        if obs is not None:
            J.cuenta("dato_inventado", hecho, "%s: %r sin código en el mensaje" % (ruta, obs))
        return
    t = mapa(tabla, codigo)
    if t == FUERA:
        if obs is not None:
            J.nota("convencion" if J.v25 else "version", hecho, "%s: %r para %r, fuera del ConceptMap" % (ruta, obs, codigo))
        return
    if t is None:
        if obs is not None:
            J.cuenta("codigo_mal_mapeado", hecho, "%s: %r para %r, que el ConceptMap deja sin destino" % (ruta, obs, codigo))
        return
    if obs is None:
        J.cuenta("dato_perdido", hecho, "%s: falta %r (de %r)" % (ruta, t[1], codigo))
    elif obs != t[1]:
        J.cuenta("codigo_mal_mapeado", hecho, "%s: esperado %r (de %r), observado %r" % (ruta, t[1], codigo, obs))


ESTADO_FHIR = {"0085": {"registered", "preliminary", "final", "amended", "corrected", "cancelled", "entered-in-error", "unknown"},
               "0123": {"registered", "partial", "preliminary", "final", "amended", "corrected", "appended", "cancelled",
                        "entered-in-error", "unknown"}}


def _estado(J, hecho, codigo, obs, tabla, ruta):
    """CV2 rep. 1 (J3): status 1..1 con binding required (observation-status, diagnostic-report-status). Mapeado -> el destino;
    unmatched, fuera de la tabla o vacío -> cualquier código del ValueSet es convención (diseño §3.3-§3.4); ausente o fuera
    del ValueSet -> FHIR inválido."""
    if obs is None or obs not in ESTADO_FHIR[tabla]:
        J.cuenta("fhir_invalido", hecho, "%s: %r (1..1, required)" % (ruta, obs))
        return
    t = mapa(tabla, codigo) if codigo else None
    if isinstance(t, tuple):
        if obs != t[1]:
            J.cuenta("codigo_mal_mapeado", hecho, "%s: esperado %r (de %r), observado %r" % (ruta, t[1], codigo, obs))
    else:
        J.nota("convencion", hecho, "%s: %r para %r (sin destino en el ConceptMap)" % (ruta, obs, codigo))


def _genero(J, m, v, obs):
    if not v:
        if obs is not None:
            if J.dec["Q-CV-D-3"] == "dato_inventado":
                J.cuenta("dato_inventado", "PID-8", "Patient.gender: %r con PID-8 vacío" % obs)
            else:
                J.nota("convencion", "PID-8", "Patient.gender: %r con PID-8 vacío (Q-CV-D-3, alternativa)" % obs)
        return
    t = mapa("0001", v)
    if t == FUERA and mapa("0001", v.upper()) not in (FUERA, None):
        t2 = mapa("0001", v.upper())
        if obs not in (None, t2[1]):                                 # CV2 rep. 1 (J2): el literal no es un código FHIR
            J.cuenta("codigo_mal_mapeado" if obs in GENERO_FHIR else "fhir_invalido", "PID-8", "Patient.gender: %r para %r" % (obs, v))
        elif obs is not None:
            J.nota("convencion", "PID-8", "Patient.gender: %r mapeado desde %r en minúscula (AMB-CV-1)" % (obs, v), "ambiguedad AMB-CV-1")
        return
    if t == FUERA:
        if obs is not None:
            J.cuenta("valor_imposible_convertido", "PID-8", "Patient.gender: %r convertido desde %r, fuera de la 0001" % (obs, v),
                     clase="valor_imposible_aceptado", tabla=True)
            if obs not in GENERO_FHIR:
                J.cuenta("fhir_invalido", "PID-8", "Patient.gender: %r fuera de administrative-gender (required)" % obs)
        return
    if obs is None:
        J.cuenta("dato_perdido", "PID-8", "Patient.gender: falta %r (de %r)" % (t[1], v))
    elif obs not in GENERO_FHIR:
        J.cuenta("fhir_invalido", "PID-8", "Patient.gender: %r fuera de administrative-gender (required)" % obs)
    elif obs != t[1]:
        J.cuenta("valor_distinto", "PID-8", "Patient.gender: esperado %r, observado %r" % (t[1], obs))


def _fallecido(J, m, pid, r):
    p29, p30 = _t(m, _f(m, pid, 29), 1), _d(m, _f(m, pid, 30))
    dt, db = r.get("deceasedDateTime"), r.get("deceasedBoolean")
    if dt is not None and db is not None:
        J.cuenta("fhir_invalido", "PID-29", "Patient.deceased[x]: deceasedDateTime y deceasedBoolean a la vez")
        return
    if p29:
        if db is not None and dt is None:
            J.cuenta("dato_perdido", "PID-29", "Patient.deceasedDateTime: falta (%r); hay deceasedBoolean %r" % (p29, db))
        else:
            _fecha(J, "PID-29", p29, dt, "dateTime", "Patient.deceasedDateTime")
        return
    if dt is not None:
        J.cuenta("dato_inventado", "PID-29", "Patient.deceasedDateTime: %r sin PID-29" % dt)
    if not p30:
        if db is not None:
            J.cuenta("dato_inventado", "PID-30", "Patient.deceasedBoolean: %r sin PID-30" % db)
        return
    t = mapa("0136", p30)
    texto = None if db is None else ("true" if db is True else "false" if db is False else str(db))
    if t in (FUERA, None):
        if db is not None:
            J.cuenta("valor_imposible_convertido", "PID-30", "Patient.deceasedBoolean: %r desde %r, fuera de la 0136" % (db, p30),
                     clase="valor_imposible_aceptado", tabla=True)
    elif texto is None:
        J.cuenta("dato_perdido", "PID-30", "Patient.deceasedBoolean: falta %s (de %r)" % (t[1], p30))
    elif texto != t[1]:
        J.cuenta("valor_distinto", "PID-30", "Patient.deceasedBoolean: esperado %s, observado %r" % (t[1], db))


def _direcciones(J, m, campo, r, pid12=""):
    """XAD (CM datatype-xad-to-address, SAD.1-3 -> line[1-3]). CV2 rep. 1 (J1): PID-12 County Code -> address[1].district si
    PID-11 no repite y XAD.9 vacío; con XAD.9 distinto, o con PID-11 repetido, la guía lo lleva a address[2]: convención
    (PID_Patient.csv:18-21)."""
    obs = [x for x in r.get("address") or [] if isinstance(x, dict)]
    usados = set()
    reps = _reps(m, campo)
    if pid12 and not reps:
        if not any(x.get("district") == pid12 for x in obs):
            J.cuenta("dato_perdido", "PID-12", "Patient.address.district: falta %r (PID-12, sin PID-11)" % pid12,
                     citas=["[G PID_Patient.csv:21]"])
        return
    for rep in reps:
        x1 = _comp(m, rep, 1)
        linea = [_d(m, _sub(m, x1, k)) for k in (1, 2, 3)] + [_t(m, rep, 2)]
        linea = [x for x in linea if x]
        esp = {"city": _t(m, rep, 3), "state": _t(m, rep, 4), "postalCode": _t(m, rep, 5), "country": _t(m, rep, 6),
               "district": _t(m, rep, 9)}
        tipo7 = _t(m, rep, 7)
        if not (linea or any(esp.values())):
            continue
        de_pid12 = bool(pid12 and len(reps) == 1 and not esp["district"])
        if de_pid12:
            esp["district"] = pid12
        libres = [k for k in range(len(obs)) if k not in usados]

        def puntos(k):
            x = obs[k]
            return sum([bool(linea) and (x.get("line") or [None])[0] in linea] + [bool(v) and x.get(c) == v for c, v in esp.items()])
        k = max(libres, key=puntos, default=None)
        if k is None or puntos(k) == 0:
            J.cuenta("dato_perdido", "PID-11", "Patient.address: falta %r" % rep)
            continue
        usados.add(k)
        x = obs[k]
        if linea and list(x.get("line") or []) != linea:
            J.cuenta("valor_distinto", "PID-11", "Patient.address.line: esperado %r, observado %r" % (linea, x.get("line")))
        for c, v in esp.items():
            hecho = "PID-12" if c == "district" and de_pid12 else "PID-11"
            if v and x.get(c) is None:
                J.cuenta("dato_perdido", hecho, "Patient.address.%s: falta %r" % (c, v))
            elif v and x.get(c) != v:
                J.cuenta("valor_distinto", hecho, "Patient.address.%s: esperado %r, observado %r" % (c, v, x.get(c)))
            elif not v and x.get(c) is not None:
                if c == "district" and pid12 and x.get(c) == pid12:
                    J.nota("convencion", "PID-12", "Patient.address.district %r desde PID-12 (PID-11 repetido o con XAD.9: address[2] en la guía)" % pid12)
                else:
                    J.cuenta("dato_inventado", "PID-11", "Patient.address.%s: %r sin componente en XAD" % (c, x.get(c)))
        tu, tt = (mapa("0190u", tipo7), mapa("0190t", tipo7)) if tipo7 else (None, None)
        if not tipo7:
            for c in ("use", "type"):
                if x.get(c) is not None:
                    J.cuenta("dato_inventado", "PID-11", "Patient.address.%s: %r sin XAD.7" % (c, x.get(c)))
        elif tu == FUERA and tt == FUERA:
            if x.get("use") is not None or x.get("type") is not None:
                J.nota("convencion" if J.v25 else "version", "PID-11", "Patient.address: XAD.7 %r fuera del ConceptMap" % tipo7)
        else:
            for c, t in (("use", tu), ("type", tt)):
                if isinstance(t, tuple):
                    if x.get(c) != t[1]:
                        J.cuenta("codigo_mal_mapeado" if x.get(c) else "dato_perdido", "PID-11",
                                 "Patient.address.%s: esperado %r (de %r), observado %r" % (c, t[1], tipo7, x.get(c)))
                elif x.get(c) is not None:
                    J.cuenta("codigo_mal_mapeado", "PID-11", "Patient.address.%s: %r para %r, sin destino" % (c, x.get(c), tipo7))
    if len(obs) > len(usados):
        J.nota("extra", "PID-11", "Patient.address de más: %d" % (len(obs) - len(usados)))


def _telecom(J, m, pid, r):
    obs = [x for x in r.get("telecom") or [] if isinstance(x, dict)]
    usados = set()
    for n, por_omision in ((13, "home"), (14, "work")):
        hecho = "PID-%d" % n
        for rep in _reps(m, _f(m, pid, n)):
            c1, uso, eq, correo, pais, area, local, sin = (_t(m, rep, k) for k in (1, 2, 3, 4, 5, 6, 7, 12))
            if eq in ("Internet", "X.400") or (not eq and correo and not (sin or c1 or local)):
                valor, contiene = correo, []
            elif sin:
                valor, contiene = sin, []
            elif c1 and not local:
                valor, contiene = c1, []
            elif local:
                valor, contiene = None, [x for x in (pais, area, local) if x]                  # L-CV-2: la fórmula no está
            else:
                continue
            if not valor and not contiene:
                continue
            libres = [k for k in range(len(obs)) if k not in usados]
            k = next((k for k in libres if (valor and obs[k].get("value") == valor) or
                      (contiene and all(c in (obs[k].get("value") or "") for c in contiene))), None)
            if k is None:
                J.cuenta("dato_perdido", hecho, "Patient.telecom: falta %r" % (valor or contiene))
                continue
            usados.add(k)
            x = obs[k]
            ts = mapa("0202", eq) if eq else None
            if eq and isinstance(ts, tuple) and ts[0].endswith("contact-point-use"):               # CP: solo da el use
                uso_esp, sis_esp = ts[1], None
            else:
                sis_esp = ts[1] if isinstance(ts, tuple) else ("email" if not eq and correo and valor == correo else None)
                uso_esp = None
            if sis_esp and x.get("system") != sis_esp:
                J.cuenta("codigo_mal_mapeado" if x.get("system") else "dato_perdido", hecho,
                         "Patient.telecom %r system: esperado %r (de %r), observado %r" % (x.get("value"), sis_esp, eq, x.get("system")))
            if uso_esp is None:
                if uso:
                    tu = mapa("0201", uso)
                    uso_esp = tu[1] if isinstance(tu, tuple) else (None if tu is None else "*")
                else:
                    uso_esp = por_omision
            if uso_esp == "*":
                continue
            if uso_esp is None and x.get("use") is not None:
                J.cuenta("codigo_mal_mapeado", hecho, "Patient.telecom %r use: %r para %r, sin destino" % (x.get("value"), x.get("use"), uso))
            elif uso_esp and x.get("use") != uso_esp:
                J.cuenta("codigo_mal_mapeado" if x.get("use") else "dato_perdido", hecho,
                         "Patient.telecom %r use: esperado %r, observado %r" % (x.get("value"), uso_esp, x.get("use")))
    if len(obs) > len(usados):
        J.nota("extra", "PID-13", "Patient.telecom de más: %d" % (len(obs) - len(usados)))


def _codigo_tabla(J, hecho, v, cc, tabla, ruta, varios=False):
    """Un CodeableConcept desde una tabla con ConceptMap: con destino, debe haber un coding {system, code} del destino; fuera de
    la tabla (user-defined), convención; vacío, ausente (presente: dato inventado, o nota si es repetible)."""
    obs = [y for x in (cc if varios else [cc]) for y in _codigos(x)] if cc else []
    if not v:
        if obs:
            (J.nota("extra", hecho, "%s: %r sin código" % (ruta, obs)) if varios else
             J.cuenta("dato_inventado", hecho, "%s: %r sin código en el mensaje" % (ruta, obs)))
        return
    t = mapa(tabla, v)
    if t in (FUERA, None):
        if obs and v not in {c[1] for c in obs}:
            J.nota("convencion" if J.v25 else "version", hecho, "%s: %r para %r, fuera del ConceptMap" % (ruta, obs, v))
        return
    if tuple(t) in obs:
        return
    if not obs:
        J.cuenta("dato_perdido", hecho, "%s: falta %r" % (ruta, t))
    else:
        J.cuenta("codigo_mal_mapeado", hecho, "%s: esperado %r (de %r), observado %r" % (ruta, t, v, obs))


# ---------------------------------------------------------------------------- Encounter (§3.2)
def _encounter(J, m, pv1, r, entries, pat_entry, en_entry):
    msh = m.segs[0]
    ev = (_comp(m, _f(m, msh, 9), 2) or "").upper()
    _identifier(J, m, _f(m, pv1, 19), r, "PV1-19", "Encounter", tipo_fijo="VN")
    c2, p45 = _t(m, _f(m, pv1, 2), 1), _t(m, _f(m, pv1, 45), 1)
    _status_encounter(J, ev, c2, p45, r.get("status"))
    cl = r.get("class") if isinstance(r.get("class"), dict) else None
    _codigo_tabla(J, "PV1-2", c2, {"coding": [cl]} if cl else None, "0004c", "Encounter.class")
    _codigo_tabla(J, "PV1-4", _t(m, _f(m, pv1, 4), 1), r.get("type") or [], "0007", "Encounter.type", varios=True)
    _codigo_tabla(J, "PV1-10", _t(m, _f(m, pv1, 10), 1), r.get("serviceType"), "0069", "Encounter.serviceType")
    _sujeto(J, m, r, en_entry, pat_entry, "Encounter.subject", "PID-3")
    _participantes(J, m, pv1, r, en_entry)
    per = r.get("period") if isinstance(r.get("period"), dict) else {}
    _fecha(J, "PV1-44", _t(m, _f(m, pv1, 44), 1), per.get("start"), "dateTime", "Encounter.period.start")
    _fecha(J, "PV1-45", p45, per.get("end"), "dateTime", "Encounter.period.end")
    _ubicaciones(J, m, pv1, r, en_entry, c2)
    hosp = r.get("hospitalization") if isinstance(r.get("hospitalization"), dict) else {}
    for n, c in ((14, "admitSource"), (36, "dischargeDisposition")):
        v, obs = _t(m, _f(m, pv1, n), 1), {x[1] for x in _codigos(hosp.get(c))}
        if v and v not in obs:
            J.cuenta("dato_perdido" if not obs else "valor_distinto", "PV1-%d" % n,
                     "Encounter.hospitalization.%s: esperado %r, observado %r" % (c, v, sorted(obs)))
        elif not v and obs:
            J.cuenta("dato_inventado", "PV1-%d" % n, "Encounter.hospitalization.%s: %r sin PV1-%d" % (c, sorted(obs), n))


def _status_encounter(J, ev, c2, p45, obs):
    """§3.2: conjunto admitido. A11: cancelled (mapa del mensaje) y, con PV1-45, también finished (Q-CV-D-11). Resto:
    {PV1-45 -> finished, o PV1-2 por la 0004} ∪ {la 0003 por el evento}; PV1-2 vacío o fuera de la 0004 sin PV1-45: cualquiera."""
    if ev == "A11":
        adm = {"cancelled"} | ({"finished"} if p45 and J.dec["Q-CV-D-11"] == "las_dos" else set())
        hecho = "MSH-9"
    else:
        hecho = "PV1-2"
        t4 = mapa("0004s", c2) if c2 else FUERA
        if not p45 and not isinstance(t4, tuple):
            if obs is not None and c2 and not J.v25:
                J.nota("version", "PV1-2", "Encounter.status %r con PV1-2 %r fuera de la 0004 [L18]" % (obs, c2), "ambiguedad L18")
            return
        adm = {"finished"} if p45 else {t4[1]}
        t3 = mapa("0003", ev)
        if isinstance(t3, tuple):
            adm.add(t3[1])
    if obs is None:
        J.cuenta("fhir_invalido", hecho, "Encounter.status: falta (1..1); admitidos %r" % sorted(adm))
    elif obs not in adm:
        if obs == "finished" and not p45:
            J.cuenta("dato_inventado", "PV1-45", "Encounter.status: finished sin PV1-45; admitidos %r" % sorted(adm))
        else:
            J.cuenta("valor_distinto", hecho, "Encounter.status: esperado uno de %r, observado %r" % (sorted(adm), obs))


def _sujeto(J, m, r, desde, pat_entry, ruta, hecho):
    ref = r.get("subject")
    if ref is None:
        if pat_entry is not None:
            J.cuenta("dato_perdido", hecho, "%s: falta" % ruta)
        return
    x, forma = resolver(J.entries, ref, desde, "Patient")
    if x is not None and x is pat_entry:
        if forma == "logica":
            J.nota("convencion", hecho, "%s: referencia lógica por identifier" % ruta)
        return
    if forma == "logica" and x is None:
        pid = _seg(m, "PID")
        ids3 = {_t(m, rr, 1) for rr in _reps(m, _f(m, pid, 3))} if pid else set()
        if (ref.get("identifier") or {}).get("value") in ids3:
            J.nota("convencion", hecho, "%s: referencia lógica a %r" % (ruta, ref["identifier"]["value"]))
            return
    if _seg(m, "PID") is None:                               # CV4 (CV3, M-23): el hecho es el PID que falta, no PID-3
        J.cuenta("referencia_rota", "PID", "%s: %r apunta a un Patient %s, y el mensaje no trae PID" %
                 (ruta, ref, "que no está en el Bundle" if x is None else "sin origen en el mensaje"), citas=_cit("ref"))
        return
    J.cuenta("referencia_rota", hecho, "%s: %r no resuelve al Patient del PID" % (ruta, ref), citas=_cit("ref"))


def _participantes(J, m, pv1, r, en_entry):
    obs = [x for x in r.get("participant") or [] if isinstance(x, dict)]
    usados = set()
    for n, tipo in PARTICIPANTE.items():
        hecho = "PV1-%d" % n
        for rep in _reps(m, _f(m, pv1, n)):
            x1, fam, g = _t(m, rep, 1), _d(m, _sub(m, _comp(m, rep, 2), 1)), _t(m, rep, 3)
            if not (x1 or fam):
                continue
            mejor, rota, solo_display = None, False, None
            for k, p in enumerate(obs):
                if k in usados:
                    continue
                ind = p.get("individual") if isinstance(p.get("individual"), dict) else {}
                pr, forma = resolver(J.entries, ind, en_entry, "Practitioner")
                tipos = {c[1] for t in p.get("type") or [] for c in _codigos(t)}
                if pr is not None:
                    ids, nom = _valores(pr["r"]), (pr["r"].get("name") or [{}])[0] if pr["r"].get("name") else {}
                    if (x1 and x1 in ids) or (fam and nom.get("family") == fam):
                        if mejor is None or tipo in tipos:
                            mejor = (k, pr, tipos, nom)
                elif forma == "logica" and x1 and (ind.get("identifier") or {}).get("value") == x1:
                    if mejor is None or tipo in tipos:
                        mejor = (k, None, tipos, {})
                elif forma == "rota" and tipo in tipos:
                    rota = True
                elif forma == "display" and tipo in tipos and fam and fam in (ind.get("display") or ""):
                    solo_display = k
            if mejor is None:
                if rota:
                    J.cuenta("referencia_rota", hecho, "Encounter.participant %s: individual no resuelve" % tipo, citas=_cit("ref"))
                elif solo_display is not None:
                    usados.add(solo_display)
                    if x1:
                        J.cuenta("dato_perdido", hecho, "Encounter.participant %s: solo display, falta el identificador %r" % (tipo, x1))
                    else:
                        J.nota("convencion", hecho, "Encounter.participant %s: solo display" % tipo)
                else:
                    J.cuenta("dato_perdido", hecho, "Encounter.participant %s: falta %r" % (tipo, rep))
                continue
            k, pr, tipos, nom = mejor
            usados.add(k)
            if pr is not None:
                J.referidas.add(pr["i"])
            if tipo not in tipos:
                J.cuenta("codigo_mal_mapeado", hecho, "Encounter.participant %r: type esperado %r, observado %r" % (x1 or fam, tipo, sorted(tipos)))
            if pr is not None:
                if fam and nom.get("family") != fam:
                    J.cuenta("valor_distinto", hecho, "Practitioner.name.family: esperado %r, observado %r" % (fam, nom.get("family")))
                if g and (nom.get("given") or [None])[0] != g:
                    J.cuenta("valor_distinto", hecho, "Practitioner.name.given: esperado %r, observado %r" % (g, nom.get("given")))
    if len(obs) > len(usados):
        J.nota("extra", "PV1-7", "Encounter.participant de más: %d" % (len(obs) - len(usados)))


def _cadena(J, ref, desde):
    """Valores (identifier, name) y descripciones de la Location referida y su cadena partOf (hasta 6 niveles)."""
    vals, descs, x, vistos = set(), set(), resolver(J.entries, ref, desde, "Location")[0], set()
    if isinstance(ref, dict) and ref.get("display"):
        descs.add(ref["display"])
    for _ in range(6):
        if x is None or x["i"] in vistos and x["padre"] is None:
            break
        vistos.add(x["i"])
        J.referidas.add(x["i"])
        vals |= _valores(x["r"]) | ({x["r"]["name"]} if x["r"].get("name") else set())
        if x["r"].get("description"):
            descs.add(x["r"]["description"])
        x = resolver(J.entries, x["r"].get("partOf"), x, "Location")[0]
    return vals, descs


def _ubicaciones(J, m, pv1, r, en_entry, c2):
    obs = [x for x in r.get("location") or [] if isinstance(x, dict)]
    cadenas = [_cadena(J, x.get("location"), en_entry) for x in obs]
    usados = set()
    for n, st in UBICACION.items():
        v = _f(m, pv1, n)
        if not v:
            continue
        hecho = "PV1-%d" % n
        rep = _reps(m, v)[0]
        comps = [_d(m, _sub(m, _comp(m, rep, 1), 1)), _d(m, _sub(m, _comp(m, rep, 2), 1)), _d(m, _sub(m, _comp(m, rep, 3), 1)),
                 _d(m, _sub(m, _comp(m, rep, 4), 1)), _d(m, _sub(m, _comp(m, rep, 7), 1)), _d(m, _sub(m, _comp(m, rep, 8), 1))]
        comps = [x for x in comps if x]
        pl9 = _t(m, rep, 9)
        if not comps and not pl9:                            # CV3 (DV-CV-16): «^^» no está valorado
            continue
        esperado = st or ("planned" if c2 == "P" else "active")
        libres = [k for k in range(len(obs)) if k not in usados]
        k = max(libres, key=lambda k: sum(c in cadenas[k][0] for c in comps), default=None)
        if k is None or not comps or sum(c in cadenas[k][0] for c in comps) == 0:
            J.cuenta("dato_perdido", hecho, "Encounter.location: falta %r" % rep, citas=_cit("PV1-loc"))
            continue
        usados.add(k)
        faltan = [c for c in comps if c not in cadenas[k][0]]
        if faltan:
            J.cuenta("dato_perdido", hecho, "Encounter.location %r: la cadena de Location no conserva %r" % (rep, faltan), citas=_cit("PV1-loc"))
        if pl9 and pl9 not in cadenas[k][1]:
            con_pl9 = sorted(d for d in cadenas[k][1] if pl9 in d)
            if con_pl9:                                      # CV4 (Q-CV-D-14, Jev: cuenta): la contiene, pero no es PL.9
                J.cuenta("valor_distinto", hecho, "Encounter.location %r: la descripción %r contiene PL.9 %r sin ser PL.9" %
                         (rep, con_pl9[0], pl9), citas=_cit("PV1-loc"))
            else:
                J.cuenta("dato_perdido", hecho, "Encounter.location %r: falta la descripción %r (PL.9)" % (rep, pl9), citas=_cit("PV1-loc"))
        if obs[k].get("status") != esperado:
            J.cuenta("valor_distinto", hecho, "Encounter.location %r status: esperado %r, observado %r" % (rep, esperado, obs[k].get("status")),
                     citas=_cit("PV1-loc"))
    if len(obs) > len(usados):
        J.nota("extra", "PV1-3", "Encounter.location de más: %d" % (len(obs) - len(usados)))


# ---------------------------------------------------------------------------- Observation y DiagnosticReport (§3.3-§3.4)
NM_RE = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)$")


def _nm_canonico(v):
    """AMB-ORU-3: sin «+» ni ceros iniciales superfluos; la precisión (ceros finales) se conserva. CV3 (DV-CV-13): un punto
    final sin decimales («5.») no da precisión y se quita."""
    s = v[1:] if v.startswith("+") else v
    neg = s.startswith("-")
    s = s.lstrip("-")
    if s.startswith("."):
        s = "0" + s
    ent, _, dec = s.partition(".")
    ent = ent.lstrip("0") or "0"
    return ("-" if neg else "") + ent + ("." + dec if dec else "")


def _codigo(J, m, campo, cc, hecho, ruta):
    """CE/CWE -> CodeableConcept: CE.1 y CE.4 en algún coding; CE.3/CE.6 -> system para LN, SCT y UCUM (L-CV-3); otros nombres,
    convención; display, forma; CWE.9 -> text."""
    rep = _reps(m, campo)[0] if _reps(m, campo) else ""
    obs = _codigos(cc)
    for ci, si in ((1, 3), (4, 6)):
        code, sis = _t(m, rep, ci), _t(m, rep, si)
        if not code:
            continue
        con = [c for c in obs if c[1] == code]
        if not con:
            J.cuenta("dato_perdido" if not obs else "valor_distinto", hecho, "%s: falta el código %r (observado %r)" % (ruta, code, [c[1] for c in obs]))
            continue
        uri = URI_SISTEMA.get(sis.upper()) if sis else None
        if uri and not any(c[0] == uri for c in con):
            J.cuenta("codigo_mal_mapeado" if any(c[0] for c in con) else "dato_perdido", hecho,
                     "%s %r: system esperado %r (de %r), observado %r" % (ruta, code, uri, sis, [c[0] for c in con]))
    t9 = _t(m, rep, 9)
    if t9 and (cc or {}).get("text") != t9:
        J.cuenta("dato_perdido" if not (cc or {}).get("text") else "valor_distinto", hecho, "%s.text: esperado %r" % (ruta, t9))


def _hecho(seg, i, n):
    """OBX-5 para la primera ocurrencia; OBX(2)-5 para la segunda (como DV-ORU-1)."""
    return "%s-%d" % (seg, n) if i == 1 else "%s(%d)-%d" % (seg, i, n)


def _observacion(J, m, obx, r, desde, pat_entry, k, obr):
    h = lambda n: _hecho("OBX", k, n)  # noqa: E731
    _estado(J, h(11), _d(m, _f(m, obx, 11)), r.get("status"), "0085", "Observation.status")
    _codigo(J, m, _f(m, obx, 3), r.get("code"), h(3), "Observation.code")
    _sujeto(J, m, r, desde, pat_entry, "Observation.subject", "PID-3")
    v14 = _t(m, _f(m, obx, 14), 1)
    if v14:
        _fecha(J, h(14), v14, r.get("effectiveDateTime"), "dateTime", "Observation.effectiveDateTime")
    elif r.get("effectiveDateTime") is not None:
        o7 = _t(m, _f(m, obr, 7), 1) if obr else ""
        sub = Juicio(m, J.v25, J.dec)
        sub.entries = J.entries
        _fecha(sub, h(14), o7, r.get("effectiveDateTime"), "dateTime", "Observation.effectiveDateTime")
        if o7 and not any(x["cuenta"] for x in sub.hs):
            J.nota("convencion", h(14), "Observation.effectiveDateTime = OBR-7 con OBX-14 vacío (AMB-CV-7)", "ambiguedad AMB-CV-7")
        else:
            J.cuenta("dato_inventado", h(14), "Observation.effectiveDateTime %r sin OBX-14" % r.get("effectiveDateTime"))
    _valor(J, m, obx, r, h)
    for rep in _reps(m, _f(m, obx, 8)):
        cod = _t(m, rep, 1)
        t = mapa("0078", cod)
        obs = [c for x in r.get("interpretation") or [] for c in _codigos(x)]
        if isinstance(t, tuple):
            if tuple(t) not in obs:
                J.cuenta("codigo_mal_mapeado" if any(c[1] == cod for c in obs) else "dato_perdido", h(8),
                         "Observation.interpretation: esperado %r (de %r), observado %r" % (t, cod, obs))
        elif obs and t == FUERA:
            J.nota("convencion" if J.v25 else "version", h(8), "Observation.interpretation %r para %r, fuera del ConceptMap" % (obs, cod))
    v7 = _d(m, _f(m, obx, 7))
    rr = [x for x in r.get("referenceRange") or [] if isinstance(x, dict)]
    if len(_reps(m, _f(m, obx, 5))) > 1:                    # J5: con OBX-5 repetido, el rango puede ir en los componentes
        rr += [x for c in r.get("component") or [] if isinstance(c, dict) for x in c.get("referenceRange") or [] if isinstance(x, dict)]
    if v7:
        if not rr:
            J.cuenta("dato_perdido", h(7), "Observation.referenceRange: falta %r" % v7)
        elif not any(x.get("text") == v7 or x.get("low") or x.get("high") for x in rr):
            J.cuenta("valor_distinto", h(7), "Observation.referenceRange: esperado %r, observado %r" % (v7, rr))
    elif rr:
        J.nota("extra", h(7), "Observation.referenceRange sin OBX-7")


VALOR_X = {"NM": "valueQuantity", "ST": "valueString", "FT": "valueString", "TX": "valueString", "CE": "valueCodeableConcept",
           "CWE": "valueCodeableConcept", "CNE": "valueCodeableConcept", "IS": "valueCodeableConcept", "CF": "valueCodeableConcept",
           "DTM": "valueDateTime", "DT": "valueDateTime", "TM": "valueTime", "NR": "valueRange", "DR": "valuePeriod"}


def _valor(J, m, obx, r, h):
    tipo, v5 = _d(m, _f(m, obx, 2)).upper(), _f(m, obx, 5)
    claves = [k for k in r if k.startswith("value")]
    reps = _reps(m, v5)
    if not reps:
        if claves:
            J.cuenta("dato_inventado", h(5), "Observation.%s sin OBX-5" % claves[0])
        return
    rep = reps[0]
    if len(reps) > 1 and tipo != "NA":
        _valor_repetido(J, m, reps, tipo, r, h)
        return
    if tipo == "SN":
        _valor_sn(J, m, rep, r, h, claves)
        return
    clave = VALOR_X.get(tipo)
    if clave is None:
        if claves:
            J.nota("convencion", h(5), "Observation.%s para OBX-2 %r (la guía no da una clave única)" % (claves[0], tipo))
        return
    if not claves:
        J.cuenta("dato_perdido", h(5), "Observation.%s: falta (OBX-5 %r)" % (clave, rep))
        return
    if clave not in claves:
        J.cuenta("valor_distinto", h(5), "Observation.value[x]: esperado %s por OBX-2 %r, observado %s" % (clave, tipo, claves))
        return
    o = r[clave]
    if clave == "valueQuantity":
        val = _d(m, rep)
        if not NM_RE.match(val):
            J.cuenta("valor_imposible_convertido", h(5), "Observation.valueQuantity desde un NM imposible %r" % val, clase="valor_imposible_aceptado")
            return
        ov = o.get("value") if isinstance(o, dict) else None
        if ov is None:
            J.cuenta("dato_perdido", h(5), "Observation.valueQuantity.value: falta %r" % val)
        elif ov not in (val, _nm_canonico(val)):
            J.cuenta("valor_distinto", h(5), "Observation.valueQuantity.value: esperado %r, observado %r (la precisión cuenta: Q-CV-D-10)" % (val, ov))
        _unidades(J, m, obx, o, h)
    elif clave == "valueString":
        partes = [_d(m, x) for x in (reps if tipo in ("TX", "FT") else [rep])]
        lecturas = [partes]
        if tipo == "FT":                                     # CV3 (DV-CV-14): «\.br\» es «Begin new output line» (CH02.txt:1063)
            lecturas.append([p.replace(m.e + ".br" + m.e, "\n") for p in partes])
        if not isinstance(o, str):
            J.cuenta("fhir_invalido", h(5), "Observation.valueString no es texto")
        elif not any((len(ps) == 1 and o == ps[0]) or (len(ps) > 1 and _en_orden(ps, o)) for ps in lecturas):
            J.cuenta("valor_distinto", h(5), "Observation.valueString: esperado %r, observado %r" % (partes, o))
    elif clave == "valueCodeableConcept":
        if tipo == "IS":
            if _d(m, rep) not in {c[1] for c in _codigos(o)}:
                J.cuenta("valor_distinto", h(5), "Observation.valueCodeableConcept: falta %r" % _d(m, rep))
        else:
            _codigo(J, m, rep, o, h(5), "Observation.valueCodeableConcept")
    elif clave == "valueDateTime":
        _fecha(J, h(5), _t(m, rep, 1), o, "dateTime", "Observation.valueDateTime")
    elif clave == "valueTime":
        esp = _d(m, rep)
        if not isinstance(o, str) or o.replace(":", "")[:len(esp)] != esp[:6]:
            J.cuenta("valor_distinto", h(5), "Observation.valueTime: esperado %r, observado %r" % (esp, o))
    elif clave == "valueRange":
        lo, hi = _t(m, rep, 1), _t(m, rep, 2)
        if (lo and (o.get("low") or {}).get("value") != lo) or (hi and (o.get("high") or {}).get("value") != hi):
            J.cuenta("valor_distinto", h(5), "Observation.valueRange: esperado %r-%r, observado %r" % (lo, hi, o))


def _textos_valor(obj):
    """Todos los textos de los value[x] de un recurso y de sus componentes (números como su texto JSON)."""
    out = []
    for fuente in [obj] + [c for c in obj.get("component") or [] if isinstance(c, dict)]:
        for k, v in fuente.items():
            if k.startswith("value"):
                if isinstance(v, str):
                    out.append(v)
                elif isinstance(v, dict):
                    out += [x for x in AO._hojas(v).values() if isinstance(x, str)]
    return out


def _valor_repetido(J, m, reps, tipo, r, h):
    """CV2 rep. 1 (J5): OBX-5 repetido -> varias Observation, componentes, concatenación u otra solución (MSG_ORU_R01.csv:69-73,
    OBX[Observation-Component]): la forma es convención; se exige que la primera repetición esté en algún value[x] del recurso o
    de sus componentes."""
    primero = _d(m, _sub(m, _comp(m, reps[0], 1), 1)) if tipo not in ("ST", "TX", "FT") else _d(m, reps[0])
    if tipo in ("NM", "SN") and NM_RE.match(primero or ""):
        buscar = {primero, _nm_canonico(primero)}
        ok = any(t in buscar for t in _textos_valor(r))
    else:
        ok = any(primero and primero in t for t in _textos_valor(r))
    if ok:
        J.nota("convencion", h(5), "OBX-5 repetido (%d): forma admitida por la guía (MSG_ORU_R01.csv:69-73)" % len(reps))
    else:
        J.cuenta("dato_perdido", h(5), "Observation.value[x]: falta la primera repetición de OBX-5 %r" % primero,
                 citas=["[G MSG_ORU_R01.csv:69-73]"] + _cit("OBX-5"))


def _en_orden(partes, texto):
    p = 0
    for x in partes:
        q = texto.find(x, p)
        if q < 0:
            return False
        p = q + len(x)
    return True


def _valor_sn(J, m, rep, r, h, claves):
    """SN (CM datatype-sn-to-quantity/-range/-ratio): <> o + -> valueString; separador : o / -> valueRatio; - -> valueRange;
    sin separador -> valueQuantity con comparator (SN.1 ∈ <, <=, >=, >)."""
    cmp_, n1, sep, n2 = (_t(m, rep, k) for k in (1, 2, 3, 4))
    if cmp_ == "<>" or sep == "+":
        clave = "valueString"
    elif sep in (":", "/"):
        clave = "valueRatio"
    elif sep == "-":
        clave = "valueRange"
    else:
        clave = "valueQuantity"
    if clave not in claves:
        J.cuenta("valor_distinto" if claves else "dato_perdido", h(5), "Observation.value[x] SN %r: esperado %s, observado %s" % (rep, clave, claves))
        return
    o = r[clave]
    if clave == "valueQuantity":
        if o.get("value") not in (n1, _nm_canonico(n1) if n1 and NM_RE.match(n1) else n1):
            J.cuenta("valor_distinto", h(5), "Observation.valueQuantity.value: esperado %r, observado %r" % (n1, o.get("value")))
        esp_c = cmp_ if cmp_ in ("<", "<=", ">=", ">") else None
        if o.get("comparator") != esp_c:
            J.cuenta("valor_distinto" if o.get("comparator") else "dato_perdido", h(5),
                     "Observation.valueQuantity.comparator: esperado %r, observado %r" % (esp_c, o.get("comparator")))
    elif clave == "valueRatio":
        if (o.get("numerator") or {}).get("value") != n1 or (o.get("denominator") or {}).get("value") != n2:
            J.cuenta("valor_distinto", h(5), "Observation.valueRatio: esperado %s%s%s, observado %r" % (n1, sep, n2, o))
    elif clave == "valueRange":
        if (o.get("low") or {}).get("value") != n1 or (o.get("high") or {}).get("value") != n2:
            J.cuenta("valor_distinto", h(5), "Observation.valueRange: esperado %s-%s, observado %r" % (n1, n2, o))
    elif not all(x in (o or "") for x in (n1, n2) if x):
        J.cuenta("valor_distinto", h(5), "Observation.valueString SN: esperado que conserve %r, observado %r" % (rep, o))


def _unidades(J, m, obx, q, h):
    """OBX-6 (CM datatype-cwe-to-quantity): unit = CWE.2 o, si vacío, CWE.1; code = CWE.1 y system = CWE.3 solo si ambos; UCUM e
    ISO+ -> http://unitsofmeasure.org; otros nombres, convención."""
    rep = (_reps(m, _f(m, obx, 6)) or [""])[0]
    u1, u2, u3 = _t(m, rep, 1), _t(m, rep, 2), _t(m, rep, 3)
    if not (u1 or u2):
        if q.get("unit") or q.get("code"):
            J.cuenta("dato_inventado", h(6), "Observation.valueQuantity.unit %r sin OBX-6" % q.get("unit"))
        return
    unit = u2 or u1
    if q.get("unit") != unit:
        J.cuenta("dato_perdido" if q.get("unit") is None else "valor_distinto", h(6),
                 "Observation.valueQuantity.unit: esperado %r, observado %r" % (unit, q.get("unit")))
    if u1 and u3:
        if q.get("code") != u1:
            J.cuenta("dato_perdido" if q.get("code") is None else "valor_distinto", h(6),
                     "Observation.valueQuantity.code: esperado %r, observado %r" % (u1, q.get("code")))
        uri = URI_SISTEMA.get(u3.upper())
        if uri and q.get("system") != uri:
            J.cuenta("dato_perdido" if q.get("system") is None else "codigo_mal_mapeado", h(6),
                     "Observation.valueQuantity.system: esperado %r (de %r), observado %r" % (uri, u3, q.get("system")))


def _informe(J, m, obr, r, desde, pat_entry, i, obxs_entries, entries):
    h = lambda n: _hecho("OBR", i, n)  # noqa: E731
    ids = [x for x in r.get("identifier") or [] if isinstance(x, dict)]
    for n, tipo, otro in ((2, "PLAC", "FILL"), (3, "FILL", "PLAC")):
        v = _t(m, _f(m, obr, n), 1)
        if not v:
            continue
        con = [x for x in ids if x.get("value") == v]
        if not con:
            J.cuenta("dato_perdido", h(n), "DiagnosticReport.identifier: falta %r (%s)" % (v, tipo), citas=_cit("OBR-2"))
        elif not any(tipo in {c[1] for c in _codigos(x.get("type"))} for x in con):
            J.cuenta("codigo_mal_mapeado", h(n), "DiagnosticReport.identifier %r: type esperado %s, observado %r" %
                     (v, tipo, [c[1] for x in con for c in _codigos(x.get("type"))]), citas=_cit("OBR-2"))
    _estado(J, h(25), _d(m, _f(m, obr, 25)), r.get("status"), "0123", "DiagnosticReport.status")
    _codigo(J, m, _f(m, obr, 4), r.get("code"), h(4), "DiagnosticReport.code")
    _sujeto(J, m, r, desde, pat_entry, "DiagnosticReport.subject", "PID-3")
    o7, o8 = _t(m, _f(m, obr, 7), 1), _t(m, _f(m, obr, 8), 1)
    edt, ep = r.get("effectiveDateTime"), r.get("effectivePeriod") if isinstance(r.get("effectivePeriod"), dict) else None
    if edt is not None and ep is not None:
        J.cuenta("fhir_invalido", h(7), "DiagnosticReport.effective[x]: dateTime y Period a la vez")
    elif o8:
        if ep is None:
            J.cuenta("dato_perdido", h(8), "DiagnosticReport.effectivePeriod: falta (OBR-8 %r)" % o8, citas=_cit("OBR-7"))
        else:
            _fecha(J, h(7), o7, ep.get("start"), "dateTime", "DiagnosticReport.effectivePeriod.start")
            _fecha(J, h(8), o8, ep.get("end"), "dateTime", "DiagnosticReport.effectivePeriod.end")
    elif ep is not None:
        _fecha(J, h(7), o7, ep.get("start"), "dateTime", "DiagnosticReport.effectivePeriod.start")
        if ep.get("end") is not None:
            J.cuenta("dato_inventado", h(8), "DiagnosticReport.effectivePeriod.end sin OBR-8")
    else:
        _fecha(J, h(7), o7, edt, "dateTime", "DiagnosticReport.effectiveDateTime")
    _fecha(J, h(22), _t(m, _f(m, obr, 22), 1), r.get("issued"), "instant", "DiagnosticReport.issued")
    esperadas = {e["i"] for e in obxs_entries if e}
    vistas = set()
    for rr in r.get("result") or []:
        x, _ = resolver(entries, rr, desde, "Observation")
        if x is None or x["i"] not in esperadas:
            J.cuenta("referencia_rota", _hecho("OBR", i, 0).replace("-0", ""), "DiagnosticReport.result %r: no es una Observation de su OBR" % rr,
                     citas=_cit("OBX"))
        else:
            vistas.add(x["i"])
    if esperadas - vistas:
        J.cuenta("referencia_rota", _hecho("OBR", i, 0).replace("-0", ""), "DiagnosticReport.result: le faltan %d Observation de su OBR" %
                 len(esperadas - vistas), citas=_cit("OBX"))


# ---------------------------------------------------------------------------- el veredicto (§1.3-§1.4)
def _imposibles(m, familia):
    """Valores imposibles del mensaje (fijan el rechazo aceptable, §1.3; Q-CV-D-7)."""
    out = []
    pid = _seg(m, "PID")
    if pid is not None:
        v7 = _t(m, _f(m, pid, 7), 1)
        if v7 and MR.partes_dtm(v7)[0] is None:
            out.append("PID-7")
        v8 = _d(m, _f(m, pid, 8))
        if v8 and mapa("0001", v8) == FUERA:
            out.append("PID-8")
    for s in m.segmentos("OBX"):
        if _d(m, _f(m, s, 2)).upper() == "NM" and _f(m, s, 5) and not NM_RE.match(_d(m, _f(m, s, 5))):
            out.append("OBX-5")
    return out


def _veredicto(cat, sub=None, cert="literal"):
    return {"categoria": cat, "subtipo": sub, "certeza": cert, "alternativa": None, "provisional": False}


def verificar(e, pe, dec=None):
    dec = dict(DECISIONES, **(dec or {}))
    familia = pe.get("familia") or ("oru" if pe["nombre"] == "oru_conv" else "adt")          # gancho 1 (etapa 20)
    conv = e.get("conversion") or {}
    salida = conv.get("salida") or {}
    estado = salida.get("estado")
    out = {"mensajes": [], "conversion": {"conversor": conv.get("conversor"), "estado": estado, "emparejamiento": None,
                                          "recuentos": {}, "otros_tipos": {}}, "hallazgos": [], "veredicto": None,
           "hechos_de_tabla": [], "punto_entrada": pe["nombre"], "decisiones": dec}
    ms = MR.mensajes(e.get("mensaje"))
    if not ms:
        out["veredicto"] = _veredicto("indeterminado", "lectura")
        out["hallazgos"] = [_h("lectura", "sin_mensaje", "MSH", "el cable no trae ningún MSH", cuenta=False)]
        return out
    m = ms[0]
    msh = m.segs[0]
    out["mensajes"] = [{"msh9": _f(m, msh, 9), "msh10": _f(m, msh, 10), "msh12": _f(m, msh, 12)}]
    ver = _comp(m, _f(m, msh, 12), 1)
    J = Juicio(m, ver in ("2.5", ""), dec)
    J.entries = []
    if len(ms) > 1:
        J.nota("mensaje_extra", "MSH", "el cable trae %d mensajes: solo se juzga el primero (L-CV-13)" % len(ms))
    if not ver:
        J.nota("version_ausente", "MSH-12", "MSH-12 vacío: se juzga como 2.5")
    elif ver != "2.5":
        J.nota("version", "MSH-12", "MSH-12 = %s: lo que dependa de las tablas o estructuras de 2.5 no cuenta (L18)" % ver, "ambiguedad L18")
    est = PE.estructura_de(m, pe)
    if est is None:
        J.nota("fuera_de_alcance", "MSH-9", "%s fuera de los tipos de %s" % (_f(m, msh, 9), pe["nombre"]))
        out["hallazgos"], out["veredicto"] = _fusionar(J.hs), _veredicto("fuera_de_alcance")
        return out
    m93 = (_comp(m, _f(m, msh, 9), 3) or "").upper()
    if m93 and m93 != est:
        J.nota("estructura_declarada", "MSH-9", "MSH-9.3 %r; la 0354 de v2.5 da %r para el evento (Q-CV-A-1)" % (m93, est),
               "literal" if J.v25 else "ambiguedad L18")
    if estado == "error":
        err = salida.get("error") or {}
        txt = str(err.get("texto") or "")
        imp = CVX.imposibles(m) if familia == "vxu" else CVM.imposibles(m) if familia == "mdm" else _imposibles(m, familia)  # gancho 2 (20) y 4 (26)
        faltan = [s for s in (CVX.FALTAN if familia == "vxu" else CVM.FALTAN if familia == "mdm" else ("PID", "PV1") if familia == "adt"
                              else ("PID", "OBR")) if not m.segmentos(s)]
        if imp or faltan or (ver not in ("2.5", "") and re.search(r"versi", txt, re.I)):
            J.nota("aceptable", (imp + faltan + ["MSH-12"])[0], "el conversor rechazó un mensaje con %r: rechazo aceptable (Q-CV-D-7)" % (imp + faltan))
            for h in J.hs:
                if h["subtipo"] == "aceptable":
                    h["clase"] = "rechazo"
            out["hallazgos"], out["veredicto"] = _fusionar(J.hs), _veredicto("correcto")
        else:
            campo = re.search(r"\b([A-Z]{2}[A-Z0-9])-(\d+)\b", txt)
            J.hs.append(_h("rechazo", "incorrecto", campo.group(0) if campo else "MSH-9",
                           "el conversor devolvió error %r con un mensaje que la guía convierte" % txt[:200], citas=["[E2 §2.6.2]"]))
            out["hallazgos"], out["veredicto"] = _fusionar(J.hs), _veredicto("rechazo_incorrecto", "error")
        return out
    if estado != "bundle":
        out["hallazgos"], out["veredicto"] = _fusionar(J.hs), _veredicto("indeterminado", "sin_salida")
        return out
    lec = leer_y_emparejar(m, salida.get("bundle"), familia)
    if lec["entries"] is None:
        J.hs.append(_h("lectura", "lectura", "MSH", "Bundle ilegible: %s" % "; ".join(lec["fallos"]), cuenta=False))
        out["hallazgos"], out["veredicto"] = _fusionar(J.hs), _veredicto("indeterminado", "lectura")
        return out
    J.entries = lec["entries"]
    out["conversion"]["emparejamiento"] = [{k: x[k] for k in ("rol", "origen", "fullUrl", "emparejado_por", "candidatos")}
                                           for x in lec["recursos"]]
    out["conversion"]["recuentos"] = {t: n for t in (CVX.TIPOS if familia == "vxu" else CVM.TIPOS if familia == "mdm" else TIPOS_PROY)
                                       for n in [sum(1 for x in lec["entries"] if x["padre"] is None and x["tipo"] == t)] if n}
    if familia == "vxu":                                            # §2.4: los recuentos propios de VXU
        out["conversion"]["recuentos"].update(CVX.recuentos(m))
    elif familia == "mdm":                                          # gancho 5 (etapa 26): los recuentos propios de MDM
        out["conversion"]["recuentos"].update(CVM.recuentos(m, lec))
    if lec["ambiguo"]:
        J.nota("emparejamiento", "MSH", "emparejamiento ambiguo: %r" % lec["ambiguo"])
        out["hallazgos"], out["veredicto"] = _fusionar(J.hs), _veredicto("indeterminado", "emparejamiento")
        return out
    _juzgar(J, m, lec, familia)
    out["conversion"]["otros_tipos"] = lec["otros_tipos"]
    hs = _fusionar(J.hs)
    out["hallazgos"] = hs
    cuentan = [h for h in hs if h["cuenta"]]
    if cuentan:
        subs = []
        if any(h["clase"] in ("fidelidad", "rechazo") for h in cuentan):
            subs.append("convertido")
        if any(h["clase"] == "valor_imposible_aceptado" for h in cuentan):
            subs.append("aceptado_imposible")
        out["veredicto"] = _veredicto("fallo_silencioso", "+".join(subs))
    else:
        out["veredicto"] = _veredicto("correcto")
    return out


def _juzgar(J, m, lec, familia):
    roles = {x["rol"]: x for x in lec["recursos"]}
    pat = roles.get("Patient#1")
    pat_entry = pat["entry"] if pat else None
    pid = _seg(m, "PID")
    if pid is not None:
        if pat_entry is None:
            J.cuenta("recurso_ausente", "PID", "falta el Patient del PID")
        else:
            _patient(J, m, pid, pat_entry["r"], lec["entries"])
    if familia == "adt":
        pv1 = _seg(m, "PV1")
        en = roles.get("Encounter#1")
        if pv1 is not None:
            if en is None or en["entry"] is None:
                c2 = _t(m, _f(m, pv1, 2), 1)
                if c2 == "N" and J.dec["Q-CV-D-6"] != "recurso_ausente":
                    J.nota("convencion", "PV1", "sin Encounter con PV1-2 = N (AMB-CV-5, alternativa de Q-CV-D-6)")
                else:
                    J.cuenta("recurso_ausente", "PV1", "falta el Encounter del PV1" + (" (PV1-2 = N: Q-CV-D-6)" if c2 == "N" else ""))
            else:
                _encounter(J, m, pv1, en["entry"]["r"], lec["entries"], pat_entry, en["entry"])
    elif familia == "vxu":                                          # gancho 5 (etapa 20)
        CVX.juzgar(J, m, lec, pat_entry)
    elif familia == "mdm":                                          # gancho 6 (etapa 26)
        CVM.juzgar(J, m, lec, pat_entry)
    else:
        grupos, _ = _grupos_oru(m)
        for i, (obr, obxs) in enumerate(grupos, 1):
            d = roles.get("DiagnosticReport#%d" % i)
            obs_e = [(roles.get("Observation#%d.%d" % (i, j)) or {}).get("entry") for j in range(1, len(obxs) + 1)]
            for j, obx in enumerate(obxs, 1):
                o = obs_e[j - 1]
                k = sum(len(g[1]) for g in grupos[:i - 1]) + j
                if o is None:
                    J.cuenta("recurso_ausente", _hecho("OBX", k, 3), "falta la Observation del OBX %d.%d" % (i, j), citas=_cit("OBX"))
                else:
                    _observacion(J, m, obx, o["r"], o, pat_entry, k, obr)
            if d is None or d["entry"] is None:
                J.cuenta("recurso_ausente", _hecho("OBR", i, 4), "falta el DiagnosticReport del OBR %d" % i, citas=_cit("OBR"))
            else:
                _informe(J, m, obr, d["entry"]["r"], d["entry"], pat_entry, i, obs_e, lec["entries"])
    for s in lec["sobrantes"]:
        if s["motivo"] == "origen_guia":
            J.nota("fuera_proyeccion", s["hecho"], "%s sin OBR que la guía crea desde un OBX fuera de ORDER_OBSERVATION (L-CV-7)" % s["resourceType"])
        else:
            J.cuenta("recurso_%s" % s["motivo"], s["hecho"], "%s %s sin origen propio en el mensaje" % (s["resourceType"], s["fullUrl"]),
                     citas=_cit(s["hecho"]))


# ---------------------------------------------------------------------------- el perfil como datos (consultar_tabla, §3)
PERFIL_GUIA_ADT = [
    {"elemento": "Patient.identifier[]", "campo": "PID-3", "regla": "por cada CX con CX.1: value = CX.1; type = CX.5; CX.4 en system o assigner", "nivel": "cuenta", "citas": C["PID-3"]},
    {"elemento": "Patient.name[]", "campo": "PID-5", "regla": "family = FN.1 (Q-CV-D-9); given = XPN.2 + XPN.3 (entero o partido, AMB-CV-3); prefix XPN.5; suffix ⊇ XPN.4/6/14; use por la 0200 (unmatched: ausente)", "nivel": "cuenta", "citas": C["PID-5"]},
    {"elemento": "Patient.birthDate", "campo": "PID-7", "regla": "fecha con la precisión del origen, sin desplazar (AMB-CV-4)", "nivel": "cuenta", "citas": C["PID-7"]},
    {"elemento": "Patient.gender", "campo": "PID-8", "regla": "por la 0001; vacío: ausente (Q-CV-D-3); fuera de la 0001: ausente", "nivel": "cuenta", "citas": C["PID-8"]},
    {"elemento": "Patient.deceased[x]", "campo": "PID-29/PID-30", "regla": "PID-29 -> deceasedDateTime; si no, PID-30 por la 0136 -> deceasedBoolean; uno solo", "nivel": "cuenta", "citas": C["PID-29"] + C["PID-30"]},
    {"elemento": "Patient.address[]", "campo": "PID-11", "regla": "line = [SAD.1-3, XAD.2] en orden; city, state, postalCode, country, district; XAD.7 por la 0190 a use o type", "nivel": "cuenta", "citas": C["PID-11"]},
    {"elemento": "Patient.telecom[]", "campo": "PID-13/PID-14", "regla": "value por XTN.3/4/12/1 (XTN.5-8: contiene, L-CV-2); use por la 0201 (por omisión home/work); system por la 0202", "nivel": "cuenta", "citas": C["PID-13"]},
    {"elemento": "Patient.maritalStatus", "campo": "PID-16", "regla": "coding por la 0002 (v3-MaritalStatus o v3-NullFlavor); user-defined: convención", "nivel": "cuenta", "citas": C["PID-16"]},
    {"elemento": "Encounter (existencia)", "campo": "PV1", "regla": "un Encounter por PV1, también con PV1-2 = N (Q-CV-D-6)", "nivel": "cuenta", "citas": C["PV1"]},
    {"elemento": "Encounter.identifier[]", "campo": "PV1-19", "regla": "value = PV1-19.1; type VN: convención", "nivel": "cuenta", "citas": C["PV1-19"]},
    {"elemento": "Encounter.status", "campo": "PV1-2/PV1-45/MSH-9", "regla": "conjunto admitido: PV1-45 -> finished, o PV1-2 por la 0004, más la 0003 por el evento; A11: cancelled (y finished con PV1-45, Q-CV-D-11)", "nivel": "cuenta", "citas": C["PV1-2"] + C["MSH-9"]},
    {"elemento": "Encounter.class", "campo": "PV1-2", "regla": "por la 0004 -> v3-ActCode (E/I/O/P) o v2-0004 (R/B/C/N/U)", "nivel": "cuenta", "citas": C["PV1-2"]},
    {"elemento": "Encounter.type[]", "campo": "PV1-4", "regla": "por la 0007 (identidad, v2-0007); user-defined: convención", "nivel": "cuenta", "citas": C["PV1-4"]},
    {"elemento": "Encounter.serviceType", "campo": "PV1-10", "regla": "por la 0069 (MED -> 382, URO -> 222; SUR, PUL, CAR identidad)", "nivel": "cuenta", "citas": C["PV1-10"]},
    {"elemento": "Encounter.subject", "campo": "PID-3", "regla": "resuelve al Patient del PID (forma: convención)", "nivel": "cuenta", "citas": C["ref"]},
    {"elemento": "Encounter.participant[]", "campo": "PV1-7/8/9/17/52", "regla": "type ATND/REF/CON/ADM/PART; individual -> Practitioner con XCN.1 y family = XCN.2", "nivel": "cuenta", "citas": C["PV1-par"]},
    {"elemento": "Encounter.period", "campo": "PV1-44/PV1-45", "regla": "start/end con la precisión del origen (§3.6)", "nivel": "cuenta", "citas": C["PV1-44"] + C["PV1-45"]},
    {"elemento": "Encounter.location[]", "campo": "PV1-3/6/11/42", "regla": "status por campo; la cadena partOf conserva PL.1-4/7/8; PL.9 -> description", "nivel": "cuenta", "citas": C["PV1-loc"]},
    {"elemento": "Encounter.hospitalization.admitSource", "campo": "PV1-14", "regla": "coding.code literal; system: convención", "nivel": "cuenta", "citas": C["PV1-14"]},
    {"elemento": "Encounter.hospitalization.dischargeDisposition", "campo": "PV1-36", "regla": "coding.code literal (la 0112 no tiene ConceptMap)", "nivel": "cuenta", "citas": C["PV1-36"]},
    {"elemento": "id, meta, text, extensiones, display, Bundle.type, orden de listas", "campo": "—", "regla": "forma (§4.2, L-CV-4, L-CV-9)", "nivel": "forma", "citas": ["[L-CV-4]", "[L-CV-9]"]},
]
PERFIL_GUIA_ORU = [
    {"elemento": "DiagnosticReport (existencia)", "campo": "OBR", "regla": "uno por ORDER_OBSERVATION", "nivel": "cuenta", "citas": C["OBR"]},
    {"elemento": "DiagnosticReport.identifier[]", "campo": "OBR-2/OBR-3", "regla": "OBR-2.1 con type PLAC, OBR-3.1 con type FILL (AMB-CV-8)", "nivel": "cuenta", "citas": C["OBR-2"]},
    {"elemento": "DiagnosticReport.status", "campo": "OBR-25", "regla": "por la 0123; unmatched: convención", "nivel": "cuenta", "citas": C["OBR-25"]},
    {"elemento": "DiagnosticReport.code", "campo": "OBR-4", "regla": "como Observation.code", "nivel": "cuenta", "citas": C["OBR-4"]},
    {"elemento": "DiagnosticReport.effective[x]", "campo": "OBR-7/OBR-8", "regla": "OBR-8 vacío -> effectiveDateTime = OBR-7; valorado -> effectivePeriod", "nivel": "cuenta", "citas": C["OBR-7"]},
    {"elemento": "DiagnosticReport.issued", "campo": "OBR-22", "regla": "instant; con menos de segundos, ausente o completado (AMB-CV-9)", "nivel": "cuenta", "citas": C["OBR-22"]},
    {"elemento": "DiagnosticReport.result[]", "campo": "OBX", "regla": "exactamente las Observation de los OBX de su OBR (orden: forma)", "nivel": "cuenta", "citas": C["OBX"]},
    {"elemento": "Observation.status", "campo": "OBX-11", "regla": "por la 0085; unmatched: convención", "nivel": "cuenta", "citas": C["OBX-11"]},
    {"elemento": "Observation.code", "campo": "OBX-3", "regla": "CE.1 y CE.4 en algún coding; system canónico para LN, SCT y UCUM (L-CV-3); otros: convención", "nivel": "cuenta", "citas": C["OBX-3"]},
    {"elemento": "Observation.subject", "campo": "PID-3", "regla": "resuelve al Patient del PID", "nivel": "cuenta", "citas": C["ref"]},
    {"elemento": "Observation.effective[x]", "campo": "OBX-14", "regla": "OBX-14 -> effectiveDateTime; vacío: ausente o la de OBR-7 (AMB-CV-7)", "nivel": "cuenta", "citas": C["OBX-14"]},
    {"elemento": "Observation.value[x]", "campo": "OBX-2/OBX-5", "regla": "clave por OBX-2; NM: texto decimal exacto (Q-CV-D-10); SN por sus ramas", "nivel": "cuenta", "citas": C["OBX-5"]},
    {"elemento": "Observation.valueQuantity.unit/code/system", "campo": "OBX-6", "regla": "unit CWE.2 o CWE.1; code CWE.1 y system CWE.3 si ambos; UCUM canónico", "nivel": "cuenta", "citas": C["OBX-6"]},
    {"elemento": "Observation.interpretation[]", "campo": "OBX-8", "regla": "por la 0078 a v3-ObservationInterpretation", "nivel": "cuenta", "citas": C["OBX-8"]},
    {"elemento": "Observation.referenceRange[]", "campo": "OBX-7", "regla": "text igual o low/high", "nivel": "convencion", "citas": C["OBX-7"]},
    {"elemento": "Observation.identifier propio, subject lógico, otros elementos", "campo": "—", "regla": "las 6 filas de convención del laboratorio se apartan (§3.3)", "nivel": "convencion", "citas": ["[D-ORU-1]", "[S58]", "[S69]"]},
]


S_CV = {"S-CV-1": "Dos puntos de entrada de solo transformación, adt_conv y oru_conv, con el contrato de su familia; el juez despacha antes de leer acuse, log o canónico (Q-CV-D-1).",
        "S-CV-2": "La evidencia es {mensaje, punto_entrada, conversion}: quién convirtió y qué devolvió (Bundle como texto, o error).",
        "S-CV-3": "Lo esperado es la proyección «guía» (ConceptMap de v2-to-FHIR 1.0.0), no el canónico del laboratorio; las S-n del laboratorio no cuentan contra un tercero.",
        "S-CV-4": "El lector empareja por papel (Patient del PID, Encounter del PV1, DiagnosticReport por OBR, Observation por OBX) resolviendo las referencias del Bundle.",
        "S-CV-5": "Cuenta lo que cambia el significado del dato: valor distinto, dato perdido, dato inventado, código mal mapeado, valor imposible convertido, recurso ausente/duplicado/inventado, referencia rota y FHIR inválido; lo demás es forma.",
        "S-CV-6": "Manda la versión escrita en MSH-12; con MSH-12 ≠ 2.5, lo que dependa de las tablas o estructuras de 2.5 no cuenta (L18); MSH-9.3 nunca cuenta."}
L_CV = {"L-CV-1": "Con MSH-12 ≠ 2.5 la legalidad de un código o de la estructura no se juzga (nota version, L18); MSH-9.3 nunca cuenta en adt_conv/oru_conv.",
        "L-CV-2": "Las fórmulas de XTN.5-8 → value no están en el paquete: se comprueba que el valor contenga XTN.7 y, si valorados, XTN.6 y XTN.5.",
        "L-CV-3": "La tabla 0396 → uri no está en el paquete: se fijan LN, SCT/SNM/SNM3 y UCUM/ISO+ por sus uris canónicas de R4; los demás nombres son convención.",
        "L-CV-4": "Las extensiones nunca cuentan, aunque lleven dato.",
        "L-CV-5": "Solo se juzgan Patient, Encounter, Observation y DiagnosticReport (y Practitioner y Location como destino de sus referencias); el resto es recuento.",
        "L-CV-6": "OBX-5 repetido (salvo TX/FT) y OBX-11 N no se juzgan: nota.",
        "L-CV-7": "Los OBX fuera de ORDER_OBSERVATION (bajo SPM, PATIENT_OBSERVATION) solo se cuentan.",
        "L-CV-8": "El juez no ejecuta conversores; con salida vacía o sin respuesta no distingue la caja del conversor: indeterminado.",
        "L-CV-9": "display, text, meta, id, fullUrl, Bundle.type/timestamp/identifier y entry.request nunca se juzgan.",
        "L-CV-10": "La clase nueva / ya declarada / convención no la calcula el juez: la pone CV3, por mecanismo.",
        "L-CV-11": "No hay validador FHIR completo: solo cardinalidad 1..1, bindings required y formato de los primitivos del perfil.",
        "L-CV-12": "El perfil del laboratorio (canónico y S-n) no se aplica a terceros; perfil_valor admite solo «guia».",
        "L-CV-13": "Un cable con varios MSH: solo se juzga el primero.",
        "L-CV-14": "La legalidad solo se mira en lo que el juez proyecta: un rechazo por un valor imposible en un segmento que no "
                   "proyecta (GT1, ACC…) cuenta como rechazo_incorrecto (CV2: los 30 de GT1 desplazado en E2 se apartaron a mano).",
        "L-CV-15": "ORU: la Observation se empareja con su OBX por el código; con el código distinto sale como recurso_ausente, "
                   "recurso_inventado y referencia_rota, no como valor_distinto en code.",
        "L-CV-16": "Los tipos de datos son los de v2.5: en mensajes 2.6+ no se proyectan los componentes posteriores (XAD.19, "
                   "XPN.15, XAD.9 como CWE…); lo que depende de ellos se aparta al adjudicar (CV3)."}
AMB_CV = {"AMB-CV-1": "Código origen en minúscula: mapearlo o no, ambos aceptables.",
          "AMB-CV-2": "FN con subcomponentes: Jev (Q-CV-D-9) admite solo FN.1 en family; la alternativa admite FN.1-5 unidos.",
          "AMB-CV-3": "XPN.3 / XCN.4 con varios nombres: entero o partido en given.",
          "AMB-CV-4": "PID-7 con hora: birthDate es la fecha escrita, sin desplazar por zona.",
          "AMB-CV-5": "PV1-2 = N sin Encounter: Jev (Q-CV-D-6) lo cuenta como recurso ausente; la alternativa es convención.",
          "AMB-CV-6": "A11 con PV1-45: cancelled y finished (Q-CV-D-11).",
          "AMB-CV-7": "OBX-14 vacío: effective ausente o la fecha de OBR-7.",
          "AMB-CV-8": "OBR-2/3: el valor con su type PLAC/FILL, venga de OBR o de ORC.",
          "AMB-CV-9": "OBR-22 con menos de segundos: issued ausente o completado con :00 y una zona.",
          "AMB-CV-10": "OBX-3 con sufijo de identificador (v2.5 §7.2.4, «71020&IMP»): el código es OBX-3.1, o el componente entero "
                       "con su sufijo; según la lectura acierta un conversor u otro."}
ABIERTAS = {"Q-CV-D-15": "El formato de ContactPoint.value frente a los componentes de XTN: comparar dígitos o literal (Jev: "
                         "empate, 0,49 frente a 0,48). Hoy, literal.",
            "Q-CV-D-16": "Un comparador SN que FHIR no admite («<>»): quitarlo invierte el sentido; ¿cuenta aunque el conversor "
                         "declare que filtra los comparadores?"}
INFO = {"guia": GUIA, "decisiones": S_CV, "decisiones_jev": DECISIONES, "alternativas_sensibilidad": ALTERNATIVA, "limites": L_CV,
        "ambiguedades": AMB_CV, "preguntas_abiertas": ABIERTAS, "puntos_entrada": ["adt_conv", "oru_conv"],
        "diseno": "cv/diseno-conversores-fable.md", "resultado": "RESULTADO-CONVERSORES.md"}


def con_alternativas(*qs):
    """Las decisiones con la alternativa de las Q indicadas (sensibilidad preinscrita de cv/decisiones-qcv.md)."""
    return {q: ALTERNATIVA[q] for q in qs}


import conversion_vxu as CVX  # noqa: E402  (al final: conversion_vxu importa este módulo y registra sus citas e INFO, DV-VX-2)
import conversion_mdm as CVM  # noqa: E402  (al final, como CVX: registra su INFO; sus citas no, DV-MD-3)


# ---------------------------------------------------------------------------- autoprueba
def autoprueba():
    ok = True
    if os.path.isdir(PAQUETE):
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "cv"))
        import extraer_mapas as X
        for n in MAPAS:
            if X.mapa(PAQUETE, n) != MAPAS[n]:
                print("  MAL el mapa %s no es el del paquete" % n)
                ok = False
        print("mapas contra el paquete: %s (%d)" % ("IGUALES" if ok else "DISTINTOS", len(MAPAS)))
    else:
        print("mapas: el paquete de la guía no está aquí; no se comparan")
    print("AUTOPRUEBA DE conversion: %s" % ("TODO BIEN" if ok else "MAL"))
    return 0 if ok else 1


if __name__ == "__main__":
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
