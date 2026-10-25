#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 22, paso 9 (diseno-rv-fable.md §6.2): las decisiones a mano sobre los candidatos de CONTRASTE-RV.json, leídos el
25-oct. Afirma que cada número citado está entre los candidatos de su discrepancia.
  python3 vx/rv/decidir_contraste.py <CONTRASTE-RV.json> <FECHA.txt>"""
import json
import sys

ruta, fecha = sys.argv[1], open(sys.argv[2]).read().strip()
c = json.load(open(ruta, encoding="utf-8"))
DECISIONES = {
    "VX-M7": ("no_reportada", None, None, "ningún candidato"),
    "VX-M8": ("no_reportada", None, None, "ningún candidato"),
    "VX-M10": ("no_reportada", None, None, "#516 trata del agente de Provenance en ADT_A01; la relación solo sale en un JSON de ejemplo"),
    "VX-M12": ("no_reportada", None, None, "ningún candidato"),
    "VX-M14": ("no_reportada", None, None, "ningún candidato; la misma causa que MS-1 de la cola del estudio (Q-RV-D-2)"),
    "VX-M15": ("no_reportada", None, None, "ningún candidato"),
    "VX-L6": ("relacionada", 343, "Add ORC-5 as a backup to RXA-20 ... ER=entered-in-error",
              "PR fusionado el 18-nov-2021 (leído a mano en GitHub el 25-oct), antes de v1.1.0 (23-oct-2023): Immunization.status "
              "desde ORC-5, no desde RXA-21 = D; #75, #341, #359 y #400 hablan de otra cosa"),
    "VX-L8": ("no_reportada", None, None, "ningún candidato"),
    "VX-L9": ("relacionada", 380, "reasonCode is an array, but we want to pick just one",
              "PR fusionado el 5-ene-2022 (leído a mano en GitHub el 25-oct), antes de v1.1.0: la elección de un solo reasonCode es "
              "para MedicationRequest, entre segmentos. En master (2cb72c2, src/main/resources/hl7/resource/Immunization.yml, entrada "
              "reasonCode), la plantilla de Immunization lee reasonCode de RXA.19 sin generateList, que da lo mismo, pero el "
              "proyecto no lo declara para Immunization. Es la más débil de las nueve como «no reportada»; #244, #280, #363 y #400 "
              "hablan de otra cosa"),
}
INGLES = {   # DV-RV-8: lo que dice el borrador junto a «Possibly related to #N»
    "VX-L6": "merged in 2021: it adds ORC-5 as a backup for Immunization.status; it does not map RXA-21 = D",
    "VX-L9": "merged in 2022: it picks a single reasonCode for MedicationRequest; the Immunization template does the same "
             "with RXA-19, which this report shows loses data",
}
for k, (dec, num, cita, nota) in DECISIONES.items():
    d = c["discrepancias"][k]
    if num is not None:
        assert num in [x["numero"] for x in d["candidatos"]], (k, num)
    d.update({"decision": dec, "numero": num, "cita": cita, "nota": nota})
    if k in INGLES:
        d["nota_ingles"] = INGLES[k]
assert 348 in [x["numero"] for x in c["arrastre"]["candidatos"]]
c["arrastre"].update({"decision": "reportada_abierta", "numero": 348, "cita": "Repeating messages do not completely reset internal variables.",
                      "nota": "abierto; su cuerpo trata de grupos ORC/RXA repetidos dentro de un mensaje y del arreglo provisional "
                              "condition: rxa17 NOT_NULL; lo de aquí es entre mensajes y con un RXA-17 de solo texto; #100 habla de otra cosa"})
c["fecha_lectura"] = fecha
c["fecha"] = fecha[:10]
json.dump(c, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("decididas %d discrepancias y el arrastre" % len(DECISIONES))
