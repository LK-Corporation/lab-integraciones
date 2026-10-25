#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 20, VX3: escribe vx/CLASES-VX3.json, la clase de cada mecanismo de VXU por la regla de CV §4.3 (R-CV-9), con su referencia
exacta. Fuentes: los contrastes por conversor y de las muestras (a ciegas de la clasificación), la revisión adversaria, los
precedentes de cv/CLASES-CV3.json y los pares de cv/cv3_minimos_vxu.py. Las cuentas de la frase salen de la lista.
  python3 vx/hacer_clases_vx3.py <huella del juez>"""
import json
import os
import sys

EXP = "src/Microsoft.Health.Fhir.Liquid.Converter.FunctionalTests/TestData/Expected/Hl7v2/VXU_V04/"
IMT = "src/test/java/io/github/linuxforhealth/hl7/segments/Hl7ImmunizationFHIRConversionTest.java"
VMT = "src/test/java/io/github/linuxforhealth/hl7/message/Hl7VXUMessageTest.java"


def m(i, conv, clase, que, hecho, subtipo, casos, referencia=None, par=None, fuerza=None, nota=None):
    return {"id": i, "conversor": conv, "clase": clase, "que": que, "hecho": hecho, "subtipo": subtipo, "casos": casos,
            "referencia": referencia, "par_minimo": par, "fuerza": fuerza, "nota": nota}


MS, LFH = "microsoft", "linuxforhealth"
CLASES = [
    m("VX-M1", MS, "ya_declarada", "vaccineCode.coding.system propio (example.com/…/CVX) en vez del de CVX", "RXA-5", "codigo_mal_mapeado",
      "39 bases y muestras", EXP + "IZ_1_1.1_Admin_Child_Max_Message-expected.json:612; " + EXP + "VXU-expected.json:791 (afirmadas por "
      "BaseConvertDataFunctionalTests.cs:307)"),
    m("VX-M2", MS, "ya_declarada", "identifier del fabricante con system propio (…/Identifier/MVX)", "RXA-17", "codigo_mal_mapeado",
      "37 bases y muestras", EXP + "IZ_1_1.1_Admin_Child_Max_Message-expected.json:739"),
    m("VX-M3", MS, "ya_declarada", "route con system propio (…/HL70162) y sin el código de v3-RouteOfAdministration", "RXR-1",
      "codigo_mal_mapeado", "37 bases", "docs/HL7v2-ImportantPoints.md:3 (URL ficticia cuando el mensaje no trae la del sistema)",
      nota="genérica: ninguna salida esperada trae HL70162"),
    m("VX-M4", MS, "ya_declarada", "site con system propio (…/HL70163)", "RXR-2", "codigo_mal_mapeado", "35 bases y muestras",
      EXP + "IZ_1_1.1_Admin_Child_Max_Message-expected.json:652"),
    m("VX-M5", MS, "ya_declarada", "doseQuantity sin unit cuando RXA-7 no trae CE.2 (también ISO+ sin system canónico)", "RXA-7",
      "dato_perdido", "36 bases", "la misma plantilla (_CWEQuantity.liquid) y la misma omisión declarada en OBX-6 (VX-M6)"),
    m("VX-M6", MS, "ya_declarada", "valueQuantity sin unit cuando OBX-6 no trae CE.2", "OBX-6", "dato_perdido", "B32",
      EXP + "VXU-V04-01-expected.json:3765-3768 (OBX-6 beats/min^^ISO)"),
    m("VX-M7", MS, "nueva", "lotNumber concatena las repeticiones de RXA-15 con «+» (LOT-A+DIL-B): un lote que no existe", "RXA-15",
      "valor_distinto", "B16", par="VM07-lote-repetido", fuerza="fuerte"),
    m("VX-M8", MS, "nueva", "Organization.name une CE.2 y CE.5 de RXA-17 con «--» (Merck--Merck S.A.)", "RXA-17", "valor_distinto", "B18",
      par="VM08-fabricante-alterno", fuerza="débil"),
    m("VX-M9", MS, "ya_declarada", "telecom sin value cuando el XTN solo trae XTN.7", "NK1-5/NK1-6", "dato_perdido", "B36, B37, B39 y muestras",
      EXP + "IZ_1_1.1_Admin_Child_Max_Message-expected.json:290-295; microsoft/FHIR-Converter#462 (cerrado)"),
    m("VX-M10", MS, "nueva", "NK1-3 GRD da un relationship.coding sin code: la relación de tutor se pierde", "NK1-3", "codigo_mal_mapeado",
      "B37", par="VM10-relacion-grd", fuerza="fuerte"),
    m("VX-M11", MS, "ya_declarada", "Observation de un OBX de ORDER sin partOf a la Immunization", "OBX-3", "dato_perdido", "B30 y muestras",
      EXP + "IZ_1_1.1_Admin_Child_Max_Message-expected.json:317-323"),
    m("VX-M12", MS, "nueva", "de dos repeticiones de RXA-19 solo una llega a reasonCode", "RXA-19", "dato_perdido", "B40",
      par="VM12-dos-indicaciones", fuerza="débil"),
    m("VX-M13", MS, "ya_declarada", "dos grupos ORDER sin ORC-2/ORC-3 se funden en una Immunization (mismo id)", "RXA-5", "recurso_ausente",
      "B35 y muestras", "docs/HL7v2-ImportantPoints.md:46-47; …/UnitTests/OutputProcessors/PostProcessorTests.cs:110-126"),
    m("VX-M14", MS, "nueva", "RXA-6 «.5» se escribe 5: la dosis se multiplica por diez", "RXA-6", "valor_distinto",
      "muestra lfh-FHIRConverterTest__L136", par="VM14-dosis-punto-inicial", fuerza="fuerte",
      nota="misma causa que M-24 del estudio de conversores (OBX-5); aquí es la dosis administrada"),
    m("VX-M15", MS, "nueva", "status por RXA-18 y no por RXA-20: RE o NA sin RXA-18 salen completed (y PA con RXA-18, not-done)", "RXA-20",
      "codigo_mal_mapeado", "muestras L212, L256, L370, L423, L44 y L169", par="VM15-re-sin-rxa18", fuerza="fuerte"),
    m("VX-M16", MS, "ya_declarada", "route, site y programEligibility tomados del grupo ORDER siguiente cuando el suyo no los trae",
      "RXR-1/RXR-2", "dato_inventado", "muestras L219 y L378", "docs/HL7v2-ImportantPoints.md:21, 33-44",
      nota="genérica: la documentación lo describe como limitación de la agrupación"),
    m("VX-M17", MS, "ya_declarada", "OBX de ORDER absorbido en la Immunization, sin Observation", "OBX-3", "recurso_ausente",
      "muestra ms-VXU-V04-01", EXP + "VXU-V04-01-expected.json:4148, 4157"),
    m("VX-M18", MS, "convencion", "primarySource y reportOrigin deducidos de RXA-9 (los CDC)", "RXA/RXA-9", None, "muestras",
      "AMB-VX-9, DV-VX-8"),
    m("VX-M19", MS, "fuera_muestra_invalida", "rechazo de dos muestras con MSH-7 inválido (día 33; fracción sin punto)", "MSH-9",
      "rechazo_incorrecto", "muestras lfh-FHIRConverterTest__L272 y lfh-Hl7ImmunizationFHIRConversionTest__L661",
      "MSH-7 «201305330» y «20160106165800070+0000»: fuera de TS de v2.5 (CH02A); como M-14 del estudio de conversores"),
    m("VX-M20", MS, "fuera_muestra_invalida", "Observation sin status con OBX-11 vacío (OBX-11 es R en v2.5)", "OBX-11", "fhir_invalido",
      "8 muestras de LinuxForHealth", "como M-29 del estudio de conversores (OBX-3 vacío)"),
    m("VX-L1", LFH, "ya_declarada", "Immunization.identifier sin ORC-3; lleva «<CVX>-CVX»", "ORC-3", "dato_perdido", "39 bases y muestras",
      "src/test/java/io/github/linuxforhealth/hl7/segments/Hl7IdentifierFHIRConversionTest.java:716-729"),
    m("VX-L2", LFH, "ya_declarada", "Immunization.identifier sin ORC-2", "ORC-2", "dato_perdido", "B03, B24 y muestras",
      "la misma prueba: un solo identifier con ORC valorado"),
    m("VX-L3", LFH, "ya_declarada", "route en v2-0162 para IM, SC, ID y PO, sin el código de v3-RouteOfAdministration", "RXR-1",
      "codigo_mal_mapeado", "37 bases", "src/test/java/io/github/linuxforhealth/FHIRConverterTest.java:279, 307, 318; "
      "LinuxForHealth/hl7v2-fhir-converter#104 y #107"),
    m("VX-L4", LFH, "ya_declarada", "doseQuantity.unit con CE.1 aunque haya CE.2", "RXA-7", "valor_distinto", "B02, B05, B39 y muestras",
      "la misma regla declarada en OBX-6: L-26 del estudio de conversores (Hl7ObservationFHIRConversionTest)"),
    m("VX-L5", LFH, "ya_declarada", "RXA-7 ISO+ con system «urn:id:ISO+»", "RXA-7", "codigo_mal_mapeado", "B04 y muestras", IMT + ":48, 85, 88-90"),
    m("VX-L6", LFH, "nueva", "RXA-21 = D (borrado) con RXA-20 = CP sale completed, no entered-in-error: un registro anulado aparece como "
      "vacuna administrada", "RXA-21", "valor_distinto", "B11", par="VL04-rxa21-d", fuerza="fuerte"),
    m("VX-L7", LFH, "ya_declarada", "recorded = RXA-22 aunque RXA-21 no sea A", "ORC-9", "valor_distinto", "B12",
      "LinuxForHealth/hl7v2-fhir-converter#344 («RXA-22 to Immunization.recorded», sin condición)"),
    m("VX-L8", LFH, "nueva", "de dos repeticiones de RXA-10 solo la primera llega a performer", "RXA-10", "dato_perdido", "B21",
      par="VL06-dos-rxa10", fuerza="débil"),
    m("VX-L9", LFH, "nueva", "de dos repeticiones de RXA-19 solo una llega a reasonCode", "RXA-19", "dato_perdido", "B40",
      par="VL07-dos-indicaciones", fuerza="débil"),
    m("VX-L10", LFH, "convencion", "isSubpotent true con RXA-20 PA", "RXA", None, "B08", "DV-VX-8 (R4 Immunization.isSubpotent); además "
      + IMT + ":48, 64", nota="tumbado por la revisión adversaria como dato inventado (H19)"),
    m("VX-L11", LFH, "ya_declarada", "NK1 sin RelatedPerson ni Patient.contact", "NK1-2", "recurso_ausente", "B36, B37, B39 y muestras",
      "README.md:27-50 (segmentos soportados, sin NK1); como L-4 del estudio de conversores"),
    m("VX-L12", LFH, "ya_declarada", "OBX de ORDER absorbidos en la Immunization, sin Observation", "OBX-3", "recurso_ausente",
      "B30, B31 y muestras", VMT + ":157-173; LinuxForHealth/hl7v2-fhir-converter#400 y #381"),
    m("VX-L13", LFH, "ya_declarada", "OBX de ORDER sin Observation salvo la reacción (31044-1)", "OBX-3", "recurso_ausente", "B32 y muestras",
      VMT + ":170 («No Observations should be created because OBX3.1 is not 31044-1»)"),
    m("VX-L14", LFH, "ya_declarada", "manufacturer perdido en los mensajes siguientes del mismo proceso tras un RXA-17 sin código", "RXA-17",
      "dato_perdido", "B18-B40 en lote (ninguno mensaje a mensaje)", "LinuxForHealth/hl7v2-fhir-converter#348 (abierto: «Repeating "
      "messages do not completely reset internal variables»)", par="VL11-estado-fabricante",
      nota="matiz: el arreglo provisional del issue (condition: rxa17 NOT_NULL) no cubre un RXA-17 con texto y sin código, y el fallo "
           "pasa de un mensaje a los siguientes"),
    m("VX-L15", LFH, "ya_declarada", "status not-done por RXA-18 con RXA-20 vacío", "RXA-20", "valor_distinto", "muestra L169", IMT + ":167, 183"),
    m("VX-L16", LFH, "ya_declarada", "statusReason sin RXA-18 (de RXA-20 RE o de OBX 30945-0/59784-9)", "RXA-18", "dato_inventado",
      "9 muestras", IMT + ":208-228, 342-443; LinuxForHealth/hl7v2-fhir-converter#370"),
    m("VX-L17", LFH, "ya_declarada", "Observation de reacción con el código de OBX-5, no de OBX-3", "OBX", "recurso_inventado", "3 muestras",
      IMT + ":129-138, 304-313; LinuxForHealth/hl7v2-fhir-converter#400 y #365"),
    m("VX-L18", LFH, "ya_declarada", "RXA-6 999 (dosis desconocida, los CDC) sin doseQuantity", "RXA-6", "dato_perdido", "7 muestras",
      IMT + ":330-331"),
    m("VX-L19", LFH, "ya_declarada", "sin Immunization cuando RXA-3 es una fecha incorrecta", "RXA-5", "recurso_ausente",
      "muestra lfh-IssueFixTest__L51", "src/test/java/io/github/linuxforhealth/hl7/message/IssueFixTest.java:54, 64-67; "
      "LinuxForHealth/hl7v2-fhir-converter#75"),
    m("VX-L20", LFH, "convencion", "primarySource y reportOrigin deducidos de RXA-9 (los CDC)", "RXA/RXA-9", None, "muestras", "AMB-VX-9, DV-VX-8"),
    m("VX-L21", LFH, "dudosa", "sin Immunization en las dos muestras 2.8 de Microsoft (VXU-V04-01/02)", "RXA-5", "recurso_ausente",
      "muestras ms-VXU-V04-01/02", None,
      nota="causa sin separar en el tope de 30 min: no es MSH-12 (también con 2.6), ni el OBX de paciente antes del ORC, ni RXA-5 en "
           "NDC, ni los campos de RXA posteriores a 2.5"),
]


def main(juez):
    n = [x for x in CLASES if x["clase"] == "nueva"]
    d = [x for x in CLASES if x["clase"] == "ya_declarada"]
    frase = {"N_nuevas_confirmadas": len(n), "N_por_conversor": {c: sum(1 for x in n if x["conversor"] == c) for c in (MS, LFH)},
             "N_fuertes": sum(1 for x in n if x["fuerza"] == "fuerte"), "K_conversores": len({x["conversor"] for x in n}),
             "D_ya_declaradas": len(d), "D_por_conversor": {c: sum(1 for x in d if x["conversor"] == c) for c in (MS, LFH)},
             "C_convenciones": 5, "C_nota": "notas de convención del juez final por conversor, hecho y firma, en lo propio de VXU: "
             "primarySource y reportOrigin de RXA-9 en los dos, e isSubpotent de PA en LinuxForHealth",
             "dudosas": sum(1 for x in CLASES if x["clase"] == "dudosa"),
             "fuera_muestra_invalida": sum(1 for x in CLASES if x["clase"] == "fuera_muestra_invalida"), "M_mensajes": 125,
             "M_nota": "40 bases sintéticas (bases_vxu.py) y 85 muestras de los proyectos (4 de Microsoft y 81 de las pruebas de "
                       "LinuxForHealth)"}
    out = {"juez": juez, "regla": "cv/diseno-conversores-fable.md §4.3 (R-CV-9); la de la etapa: ANTES-ETAPA-VXU.md",
           "fuera_de_vxu": "Lo que cuenta en Patient y Encounter es el perfil de adt_conv: lo clasificó el estudio de conversores "
                           "(cv/CLASES-CV3.json) y no entra en estas cuentas (en las bases, PV1-2 de B38 en LinuxForHealth: L-3 y L-5)",
           "frase": frase, "clases": CLASES}
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CLASES-VX3.json")
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(frase, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1])
