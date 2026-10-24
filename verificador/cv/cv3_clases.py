#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CV3: la clase de cada mecanismo (§4.3 del diseño: nueva / ya_declarada / convención, más lo que se aparta con motivo) y las
cuentas de la frase fija. Las reglas de abajo son el resultado de leer las salidas esperadas, pruebas, documentación e issues
de cada proyecto (referencias en cada regla y en cv/RESULTADO-CV3.md); este script solo las aplica caso a caso, sobre el juicio
del juez final, y comprueba que nada que cuente quede sin clase.

  python3 cv/cv3_clases.py <juicio.jsonl> <minimos.json> <evidencias> <salida.json>
"""
import collections
import glob
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

MS, LFH = "microsoft", "linuxforhealth"
ESP = "src/Microsoft.Health.Fhir.Liquid.Converter.FunctionalTests/TestData/Expected/Hl7v2/"
LFH_T = "src/test/java/io/github/linuxforhealth/hl7/"

# (id, conversor, mecanismos, texto que debe estar en el «que» o None, casos o prefijos de caso o None,
#  clase, referencia, par mínimo, fuerza, qué)
# clases: nueva | nueva_rechazo (falla a la vista: no es de las ocho clases de S-CV-5) | ya_declarada | convencion |
#         dudosa (pasa a Q-CV-D, no cuenta) | no_cambia | fuera_juez | fuera_corpus | fuera_ambiguedad | fuera_version |
#         fuera_muestra_invalida
R = [
    # ---------------------------------------------------------------- Microsoft
    ("M-1", MS, {"MC-ADT-3"}, "la cadena de Location no conserva", None, "ya_declarada",
     ESP + "ADT_A01/ADT-A01-01-expected.json (y 51 más); microsoft/FHIR-Converter#624 (abierto)", None, "media",
     "Encounter.location apunta al componente menos granular de PV1-3; el resto de PL no queda en su cadena"),
    ("M-3", MS, {"MC-ADT-3"}, "observado None", None, "ya_declarada", ESP + "ADT_A11/ADT-A11-01-expected.json", None, "débil",
     "Encounter.location sin status (1..1 en la guía para PV1-3)"),
    ("M-2", MS, {"MC-ADT-3", "fuera:Encounter.location|valor_distinto"}, "status: esperado", None, "ya_declarada",
     ESP + "ADT_A01/ADT-A01-01-expected.json", None, "débil", "Encounter.location.status distinto del de la guía (PV1-11 «planned»; PV1-2 = P «active»)"),
    ("M-4", MS, {"MC-ADT-3"}, "falta la descripción", None, "ya_declarada", ESP + "ADT_A01/ADT-A01-01-expected.json (descripción concatenada en 114 salidas esperadas); data/Templates/Hl7v2/Resource/_PLLocation.liquid:62-63; Q-CV-D-14 (Jev: cuenta)", "M10-pl9-descripcion", "débil",
     "PL.9 va dentro de una descripción que concatena todo el PL («UCI--3--1--HOSP--Box 3»), no sola"),
    ("M-5", MS, {"MC-ADT-5"}, None, None, "ya_declarada", ESP + "ADT_A01/ADT-A01-01-expected.json", None, "débil",
     "PV1-10 a serviceType sin system ni el mapa de la guía"),
    ("M-6", MS, {"MC-ADT-9"}, None, None, "ya_declarada", ESP + "ADT_A04/ADT-A04-01-expected.json", None, "media",
     "Encounter.status «in-progress» donde la guía da «finished» o «planned»"),
    ("M-7", MS, {"MC-ADT-10"}, None, None, "nueva", "—", "M04-pv1-8-repetido", "media", "solo la primera repetición de PV1-8 llega a participant"),
    ("M-8", MS, {"MC-ADT-12"}, None, None, "ya_declarada", ESP + "ADT_A13/ADT-A13-02-expected.json", None, "media",
     "PV1-45 valorado sin period.end"),
    ("M-9", MS, {"MC-ADT-1"}, None, None, "no_cambia", "v3-ActCode «OBS» = «Obstetrics», el mismo concepto que v2-0004 «B»; revisión", "M05-clase-b", "media",
     "PV1-2 «B» (obstetricia) a Encounter.class v3-ActCode «OBS»; la guía no tiene equivalente v3 y deja v2-0004 «B»"),
    ("M-10", MS, {"MC-ADT-4"}, None, None, "nueva", "—", "M08-estado-civil-t", "débil",
     "PID-16 «T» (no declarado) sin maritalStatus; la guía da NullFlavor NAVU"),
    ("M-11", MS, {"MC-ADT-11"}, "invalid: L.", None, "fuera_corpus", "E2 «comp»/«opci»: GT1-2 lleva un XPN, CX.7 (DT) = «L»",
     None, None, "rechazo de un mensaje con un DT imposible en GT1-2.7"),
    # Q-CV-D-13 (Jev: incorrecto, 0,78) no mueve la clase de L-4: rechazo que cuenta, ya declarado por el proyecto
    ("M-12", MS, {"MC-ADT-11"}, "DateTime is invalid", None, "nueva_rechazo", "—", "R01-nulo-en-dtm", "media",
     "rechaza el nulo «\"\"» en un DTM (ACC-1); CH02.txt:392"),
    ("M-13", MS, {"MC-ADT-11"}, "Escape character", None, "ya_declarada",
     "src/Microsoft.Health.Fhir.Liquid.Converter.UnitTests/Validators/Hl7v2DataValidatorTests.cs:51", None, "media",
     "rechaza caracteres de codificación distintos de «\\»"),
    ("M-14", MS, {"MC-ADT-11"}, "duplicate separators", None, "fuera_muestra_invalida",
     "lfh-sample_unix: MSH-2 «^~\\\\&» (dos barras)", None, None, "rechazo de una muestra con MSH-2 mal escrito"),
    ("M-15", MS, {"MC-ADT-11"}, None, {"ORU-B27"}, "nueva_rechazo", "—", "R02-nm-cero-inicial", "media",
     "NM «01.20»: escribe «\"value\":01.20» (JSON inválido) y falla; CH02A.txt:2979"),
    ("M-16", MS, {"fuera:Patient.gender|fhir_invalido", "fuera:Patient.gender|fhir_invalido+valor_imposible_convertido"}, None, None,
     "ya_declarada", "microsoft/FHIR-Converter#187 (cerrado: «origin data … directly passed to results if there is no mapping»); revisión", "M02-genero-fuera-de-tabla", "fuerte", "copia a Patient.gender un PID-8 fuera de la 0001 o en minúscula: FHIR inválido"),
    ("M-17", MS, {"fuera:Patient.address.district|dato_perdido"}, None, None, "ya_declarada", ESP + "ADT_A01/ADT01-23-expected.json",
     None, "débil", "PID-12 en una Address aparte (matiz: comentario de PID_Patient.csv:18)"),
    ("M-18", MS, {"fuera:Patient.deceasedBoolean|dato_inventado"}, None, None, "nueva", "—", "M03-pda-sin-muerte", "fuerte",
     "en A02, un PDA sin datos de muerte (PDA|\"\") da deceasedBoolean true, sin PID-29 ni PID-30 (la guía no mapea PDA)"),
    ("M-19", MS, {"MC-ORU-2"}, None, None, "ya_declarada",
     "docs/HL7v2-ImportantPoints.md punto 5 (mismo id: se sobrescriben); microsoft/FHIR-Converter#504 (comparator «<>»)", None, "fuerte",
     "dos OBX con el mismo código dan una Observation (se pierde la primera) con comparator «<>»"),
    ("M-20", MS, {"fuera:falta|recurso_ausente"}, None, {"ORU-B09"}, "ya_declarada", "docs/HL7v2-ImportantPoints.md punto 5", None,
     "fuerte", "el mismo choque de id: falta la Observation del primer OBX"),
    ("M-21", MS, {"fuera:falta|recurso_ausente"}, None, {"ORU-B23"}, "ya_declarada", "microsoft/FHIR-Converter#325 (cerrado; comentarios: get_related_segment_list solo da segmentos consecutivos); revisión", "M06-obx-tras-nte", "fuerte",
     "una NTE tras un OBX hace perder el OBX siguiente (no con la NTE al final)"),
    ("M-22", MS, {"fuera:falta|recurso_ausente", "MC-ORU-7"}, None, {"ORU-B14"}, "fuera_ambiguedad", "AMB-CV-10 (CH07.txt:368-372)",
     None, None, "sufijo «&IMP» de OBX-3: según la lectura, acierta un conversor u otro"),
    ("M-23", MS, {"fuera:DiagnosticReport.subject|referencia_rota", "fuera:Observation.subject|referencia_rota"}, None, None, "nueva",
     "—", "M07-oru-sin-pid", "fuerte", "ORU sin PID: subject a «Patient/364bf61f…», que no está en el Bundle; el mismo id en ORU-B30 y en el mínimo M07"),
    ("M-24", MS, {"MC-ORU-1"}, None, None, "nueva", "—", "M01-nm-punto-inicial", "fuerte", "NM «.5» se escribe 5: el valor se multiplica por diez"),
    ("M-25", MS, {"MC-ORU-6"}, None, None, "ya_declarada", "src/Microsoft.Health.Fhir.Liquid.Converter.UnitTests/InputProcessors/Hl7v2EscapeSequenceProcessorTests.cs:32 (la secuencia .br pasa a los dos caracteres barra y n); revisión", "M09-ft-br", "débil",
     "FT «\\.br\\» se escribe como los dos caracteres «\\n» en el texto, no como salto de línea"),
    ("M-26", MS, {"MC-ADT-8"}, "use: esperado", None, "ya_declarada", ESP + "ADT_A01/ADT-A01-01-expected.json", None, "débil",
     "ContactPoint.use «home» donde la guía da «mobile» (XTN.3 CP)"),
    ("M-27", MS, {"MC-ADT-8"}, "Patient.telecom: falta", None, "dudosa", "Q-CV-D-15", None, None,
     "número de XTN escrito con otro formato: el juez busca los componentes literales"),
    ("M-28", MS, {"MC-ORU-7"}, None, ("ms-ADT",), "ya_declarada", ESP + "ADT_A01/ADT-A01-01-expected.json", None, "media",
     "Observation de PDA (certificado de defunción, autopsia…) que la guía no mapea"),
    ("M-29", MS, {"MC-ORU-7", "fuera:falta|recurso_ausente"}, None, ("lfh-ORU",), "fuera_muestra_invalida",
     "lfh-ORU-multiline-short(-mixed): OBX-3 vacío (obligatorio): los OBX chocan de id", None, None, "muestra con OBX-3 vacío"),
    ("M-30", MS, {"fuera:DiagnosticReport|recurso_inventado"}, None, None, "ya_declarada", ESP + "ORU_R01/ORU-R01-01-expected.json",
     None, "débil", "DiagnosticReport de un OBX RP/ED"),
    ("M-31", MS, {"fuera:Encounter.period.end|dato_inventado"}, None, None, "ya_declarada", ESP + "ADT_A04/ADT-A04-01-expected.json",
     None, "media", "period.end sin PV1-45"),
    ("M-32", MS, {"fuera:Patient.address.district|valor_distinto"}, None, None, "fuera_version", "L-CV-16: XAD.9 es CWE desde 2.7",
     None, None, "muestra 2.8: XAD.9 «&W» lleva texto; el juez lo lee como IS 2.5 vacío"),
    ("M-33", MS, {"fuera:Patient.address.line|valor_distinto"}, None, None, "fuera_version",
     "L-CV-16: XAD.19 (2.7+) va a line[5] en la guía (CM datatype-xad-to-address)", None, None, "muestra 2.8: Microsoft acierta con XAD.19"),
    ("M-34", MS, {"fuera:Patient.name.given|valor_distinto"}, None, None, "fuera_version",
     "L-CV-16: XPN.15 (2.7+) va a name[2].given en la guía", None, None, "muestra 2.8: depende de XPN.15"),
    ("M-35", MS, {"fuera:Patient.deceasedBoolean|valor_imposible_convertido"}, None, None, "ya_declarada",
     ESP + "ORU_R01/LAB-ORU-1-expected.json", None, "débil", "PID-30 «NO» (fuera de la 0136) a deceasedBoolean false"),
    ("M-36", MS, {"fuera:Patient.identifier|dato_perdido"}, None, None, "fuera_juez",
     "falso positivo: system «…/Identifier/NIST-MPI» lleva CX.4; el juez busca «NIST MPI» literal (para CV4)", None, "débil", "CX.4 con solo el nombre del espacio, sin system ni assigner"),
    # ---------------------------------------------------------------- LinuxForHealth
    ("L-1", LFH, {"MC-ADT-3"}, None, None, "nueva", "—", "L01-sin-location", "media", "no hay Encounter.location: Encounter.yml no la mapea"),
    ("L-2", LFH, {"fuera:Encounter.period.start|dato_inventado"}, None, None, "ya_declarada",
     LFH_T + "segments/Hl7EncounterFHIRConversionTest.java (testEncounterPeriod: «we fall back to either EVN.6 or EVN.2»)", None,
     "media", "period.start de EVN-6 o EVN-2 sin PV1-44"),
    ("L-3", LFH, {"MC-ADT-9", "MC-ADT-1"}, "Encounter.status", None, "ya_declarada",
     LFH_T + "data/Hl7RelatedGeneralUtilsTest.java:76-100 (UNKNOWN sin fechas, ARRIVED con PV1-44)", None, "media",
     "Encounter.status por fechas, no por evento ni PV1-2"),
    ("L-4", LFH, {"MC-ADT-11"}, None, None, "ya_declarada", "README.md:7-26 (tipos soportados: sin A02, A11 ni A13)", None, None,
     "rechaza ADT_A02, A11 y A13 (Q-CV-D-13 decide si es rechazo aceptable)"),
    ("L-5", LFH, {"MC-ADT-1", "MC-ADT-9"}, "Encounter.class", None, "ya_declarada",
     LFH_T + "segments/Hl7EncounterFHIRConversionTest.java (test_encounter_class: «Should return hl7Code if not a mapped value»)",
     None, "débil", "PV1-2 sin mapa a class: el código sin system"),
    ("L-6", LFH, {"MC-ADT-5"}, None, None, "ya_declarada", "TEMPLATING.md:519-525 (salida de ejemplo: serviceType v2-0069 MED); revisión", "L03-pv1-10-med", "débil", "PV1-10 a serviceType en v2-0069, sin el mapa de la guía"),
    ("L-7", LFH, {"MC-ADT-8"}, "system: esperado", None, "ya_declarada", "LinuxForHealth/hl7v2-fhir-converter#524 (abierto)", None,
     "media", "ContactPoint.system no sale de XTN.3 (FX, TDD → phone)"),
    ("L-8", LFH, {"MC-ADT-8"}, "use: ", None, "ya_declarada", "LinuxForHealth/hl7v2-fhir-converter#524 (abierto)", None, "débil",
     "ContactPoint.use no sale de XTN.2 (NET)"),
    ("L-9", LFH, {"MC-ADT-8"}, "Patient.telecom: falta", None, "dudosa", "Q-CV-D-15", None, None,
     "número de XTN escrito con otro formato («404 2808»): el juez busca los componentes literales"),
    ("L-10", LFH, {"MC-ADT-4"}, None, None, "nueva", "—", "L02-estado-civil-a", "fuerte",
     "PID-16 «A» (separado) a v3-MaritalStatus «A», que en v3 es anulado; la guía da «L»"),
    ("L-11", LFH, {"fuera:Patient.address.line|valor_distinto", "fuera:Patient.address|dato_perdido"}, None, None, "nueva", "—",
     "L04-sad-2-3", "media", "SAD.2 y SAD.3 de XAD.1 no llegan a address.line (CM datatype-sad-to-address)"),
    ("L-12", LFH, {"fuera:Patient.gender|valor_distinto"}, None, None, "nueva", "—", "L05-genero-n", "media",
     "PID-8 «N» a «unknown»; el mapa de la guía da «other»"),
    ("L-13", LFH, {"MC-ORU-4"}, None, None, "ya_declarada", LFH_T + "segments/Hl7ObservationFHIRConversionTest.java:161-163", None,
     "débil", "OBX-8 en v2-0078, sin el mapa a v3-ObservationInterpretation"),
    ("L-14", LFH, {"fuera:falta|recurso_ausente"}, None, {"ORU-B10", "lfh-ORU-multiline-short", "lfh-ORU-multiline-short-mixed",
                                                         "ms-LRI_2.0-NG_CBC_Typ_Message"}, "ya_declarada",
     "hl7/resource/DiagnosticReport.yml:139-141 y Observation.yml (comentarios); LinuxForHealth/hl7v2-fhir-converter#306", None,
     "fuerte", "OBX TX sin Observation: el texto va a presentedForm, y con OBX mezclados se pierde"),
    ("L-15", LFH, {"fuera:falta|recurso_ausente"}, None, {"ORU-B18", "ORU-B22"}, "nueva", "—", "L06-obx-sin-tipo", "fuerte",
     "un OBX sin OBX-2 (pendiente, no obtenible) no da Observation, contra la guía y contra el comentario de su plantilla"),
    ("L-16", LFH, {"fuera:Observation.valueString|dato_perdido", "fuera:Observation.valueTime|dato_perdido"}, None, None, "nueva", "—",
     "L07-ft / L08-tm", "fuerte", "OBX FT y TM sin valor: valueString solo para ST, y no hay valueTime"),
    ("L-17", LFH, {"fuera:Observation.valueCodeableConcept.text|valor_distinto", "fuera:Observation.code.text|valor_distinto",
                  "fuera:DiagnosticReport.code.text|valor_distinto"}, None, None, "ya_declarada",
     "LinuxForHealth/hl7v2-fhir-converter#139 (cerrado: «CWE.2 should be put in CodeableConcept.text»); hl7/datatype/CodeableConcept.yml",
     None, "débil", "CodeableConcept.text de CWE.2 antes que de CWE.9"),
    ("L-18", LFH, {"fuera:Observation.status|codigo_mal_mapeado"}, None, None, "nueva", "—", "L09-obx-11-d", "media",
     "OBX-11 «D» a «cancelled»; el mapa de la guía da «entered-in-error»"),
    ("L-19", LFH, {"fuera:DiagnosticReport.status|codigo_mal_mapeado"}, None, None, "nueva", "—", "L10-obr-25-i", "media",
     "OBR-25 «I» a «unknown»; el mapa de la guía da «registered»"),
    ("L-20", LFH, {"MC-ORU-2"}, "valueRange", None, "nueva", "—", "L11-sn-rango", "fuerte", "SN «^1^-^5» (rango) a valueQuantity 1"),
    ("L-21", LFH, {"MC-ORU-2"}, "valueString", None, "dudosa", "Q-CV-D-16: hl7/datatype/Quantity.yml:13 declara que quita los comparadores que FHIR no admite (lo prueba con «=»)", "L12-sn-distinto", "fuerte",
     "SN «<>^5» (distinto de 5) a valueQuantity 5, sin comparador"),
    ("L-22", LFH, {"MC-ADT-10"}, None, None, "nueva", "—", "L13-pv1-52", "media", "PV1-52 no llega a participant"),
    ("L-23", LFH, {"fuera:Patient.name.suffix|dato_perdido"}, None, None, "ya_declarada", LFH_T + "segments/Hl7ObservationFHIRConversionTest.java:622 («currently not putting degree ... in suffix», misma HumanName.yml)", "L14-xpn-6-titulo", "débil", "XPN.6 (título) no llega a suffix"),
    ("L-24", LFH, {"fuera:Patient.identifier|dato_perdido"}, None, None, "fuera_juez", "falso positivo: system «urn:id:NIST_MPI» lleva CX.4; el juez busca «NIST MPI» literal (para CV4)", "L16-cx-4-solo-nombre", "débil",
     "CX.4 con solo el nombre del espacio, sin system ni assigner"),
    ("L-25", LFH, {"fuera:Patient.deceasedBoolean|valor_imposible_convertido"}, None, None, "no_cambia", "«NO» y false dicen lo mismo (ConceptMap table-hl70136-to-special-values: N → false)", "L17-pid-30-no", "débil",
     "PID-30 «NO» (fuera de la 0136) a deceasedBoolean false: el sentido se conserva"),
    ("L-26", LFH, {"MC-ORU-3"}, None, None, "ya_declarada", LFH_T + "segments/Hl7ObservationFHIRConversionTest.java:141 («unit units to OBX.6.1»)", "L18-unidad-cwe-2", "débil", "Quantity.unit con el código de OBX-6 y no con su texto (CWE.2)"),
]


def regla(conv, mc, q, caso):
    for r in R:
        rid, cv, mcs, texto, casos = r[:5]
        if cv != conv or mc not in mcs or (texto and texto not in q):
            continue
        if casos is not None and not (caso in casos if isinstance(casos, set) else caso.startswith(casos)):
            continue
        return r
    return None


def main(juicio, minimos, evidencias, salida):
    import juzgar_cv2 as J
    from cv3_mecanismos import firma
    mins = {p["id"]: p for p in json.load(open(minimos, encoding="utf-8"))["pares"]}
    uso = collections.defaultdict(lambda: collections.defaultdict(set))
    sin = collections.Counter()
    filas = [json.loads(l) for l in open(juicio, encoding="utf-8")]
    for x in filas:
        for h in x["cuentan"]:
            for q in h["que"]:
                mc = J.asignar(h, q)
                r = regla(x["conversor"], mc, q, x["caso"])
                if r is None:
                    sin[(x["conversor"], mc, firma(q))] += 1
                else:
                    uso[r[0]][x["corpus"]].add(x["caso"])
    clases = []
    for r in R:
        rid, cv, mcs, texto, casos, clase, ref, par, fuerza, que = r
        pares = [p.strip() for p in par.split("/")] if par else []
        conf = all(mins.get(p, {}).get("confirmada") for p in pares) if pares else None
        clases.append({"id": rid, "conversor": cv, "clase": clase, "que": que, "referencia": ref, "par_minimo": par,
                       "confirmada_con_par": conf, "fuerza": fuerza,
                       "casos": {k: len(v) for k, v in uso[rid].items()}, "ejemplos": {k: sorted(v)[:3] for k, v in uso[rid].items()}})
    # convenciones: notas de nivel «convencion» del juez final, por conversor, hecho y firma
    conv = collections.defaultdict(set)
    sys.argv = ["x", "--silencio"]
    for f in sorted(glob.glob(os.path.join(evidencias, "*", "*", "*.json"))):
        e = json.load(open(f, encoding="utf-8"))
        cv = f.split(os.sep)[-3]
        for h in J.juzgar(e)["hallazgos"]:
            if not h["cuenta"] and h["subtipo"] == "convencion":
                for q in h["que"]:
                    conv[(cv, h["hecho"], firma(q))].add(os.path.basename(f))
    aceptadas = {"ms-ADT-A01-01", "ms-ADT-A01-02", "ms-ADT-A02-01", "ms-ADT-A02-02", "ms-ADT-A03-01", "ms-ADT-A03-02",
                 "ms-ADT01-28", "ms-LAB-ORU-1", "ms-LAB-ORU-2", "ms-ORU-R01-RMGEAD"}
    prev = collections.defaultdict(collections.Counter)
    for x in filas:
        if x["corpus"] == "muestras" and x["caso"] in aceptadas:
            for h in x["cuentan"]:
                for q in h["que"]:
                    r = regla(x["conversor"], J.asignar(h, q), q, x["caso"])
                    prev[x["conversor"]][r[5] if r else "sin_clase"] += 1
    por = lambda c: [x for x in clases if x["clase"] == c and x["casos"]]  # noqa: E731
    nuevas = [x for x in por("nueva") if x["confirmada_con_par"]]
    res = {"juez": __import__("mcp_verificador")._version()["huella"], "clases": clases,
           "sin_clase": {"%s | %s | %s" % k: n for k, n in sin.items()},
           "convenciones": {"%s | %s | %s" % k: len(v) for k, v in sorted(conv.items())},
           "frase": {"N_nuevas_confirmadas": len(nuevas),
                     "N_por_conversor": dict(collections.Counter(x["conversor"] for x in nuevas)),
                     "N_fuertes": sum(1 for x in nuevas if x["fuerza"] == "fuerte"),
                     "K_conversores": len({x["conversor"] for x in nuevas}),
                     "D_ya_declaradas": len(por("ya_declarada")),
                     "D_por_conversor": dict(collections.Counter(x["conversor"] for x in por("ya_declarada"))),
                     "C_convenciones": len(conv) + 2,
                     "C_nota": "notas de nivel convención del juez final, por conversor, hecho y firma, más PV1-19 «VN» en los dos (DV-CV-15)",
                     "rechazos_nuevos": len(por("nueva_rechazo")), "dudosas": len(por("dudosa")),
                     "M_mensajes": len({x["caso"] for x in filas if x["corpus"] in ("adt", "oru", "muestras")})},
           "muestras_aceptadas": {cv: dict(c) for cv, c in prev.items()}}
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(res["frase"], ensure_ascii=False, indent=1))
    print("sin clase:", res["sin_clase"])
    print("muestras aceptadas:", res["muestras_aceptadas"])
    for x in clases:
        print("%-5s %-15s %-22s conf=%-5s %-7s %s %s" % (x["id"], x["conversor"], x["clase"], x["confirmada_con_par"], x["fuerza"],
                                                         x["casos"], x["que"][:70]))
    print("convenciones (%d):" % len(conv))
    for k, n in sorted(res["convenciones"].items()):
        print("   %3d %s" % (n, k[:150]))


if __name__ == "__main__":
    main(*sys.argv[1:5])
