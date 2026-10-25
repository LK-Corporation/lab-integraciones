#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 20 (VX-pre): trae del repositorio HL7/v2-to-fhir, en el commit del estudio (873b331), las hojas CSV de la guía que
cubren VXU_V04, con su nombre original y una copia con el nombre que usa el laboratorio (cv/guia/). Escribe FUENTES.txt con
la ruta de origen y el sha256 de cada una. Solo lectura de GitHub (gh api). Compara además las hojas que el juez ya tiene con
las del mismo commit.

  python3 vx/traer_guia_vxu.py <carpeta de salida>"""
import base64
import hashlib
import json
import os
import subprocess
import sys
import urllib.parse

COMMIT = "873b331b3890c8bc5d62ef9b4dabb41801aac70d"
HOJAS = [  # (carpeta en el repo, nombre original, nombre del laboratorio)
    ("messages", "HL7 Message - FHIR R4_ VXU_V04 - Sheet1.csv", "MSG_VXU_V04.csv"),
    ("segments", "HL7 Segment - FHIR R4_ RXA[Immunization] - RXA.csv", "RXA_Immunization.csv"),
    ("segments", "HL7 Segment - FHIR R4_ RXR[Immunization] - RXR.csv", "RXR_Immunization.csv"),
    ("segments", "HL7 Segment - FHIR R4_ ORC[Immunization] - ORC.csv", "ORC_Immunization.csv"),
    ("segments", "HL7 Segment - FHIR R4_ PD1[Patient] - PD1.csv", "PD1_Patient.csv"),
    ("segments", "HL7 Segment - FHIR R4_ NK1[RelatedPerson] - Sheet1.csv", "NK1_RelatedPerson.csv"),
    ("segments", "HL7 Segment - FHIR R4_ NK1[Patient] - Sheet1.csv", "NK1_Patient.csv"),
]
YA = [("segments", "HL7 Segment - FHIR R4_ PID[Patient] - PID.csv", "PID_Patient.csv"),
      ("segments", "HL7 Segment - FHIR R4_ PV1[Encounter] - PV1.csv", "PV1_Encounter.csv"),
      ("segments", "HL7 Segment - FHIR R4_ OBX[Observation] - OBX.csv", "OBX_Observation.csv")]
GUIA_LAB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cv", "guia")


def traer(carpeta, nombre):
    ruta = "mappings/%s/%s" % (carpeta, nombre)
    r = subprocess.run(["gh", "api", "repos/HL7/v2-to-fhir/contents/%s?ref=%s" % (urllib.parse.quote(ruta), COMMIT)],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise SystemExit("no se pudo traer %s: %s" % (ruta, r.stderr[:200]))
    return ruta, base64.b64decode(json.loads(r.stdout)["content"])


def main(salida):
    os.makedirs(os.path.join(salida, "original"), exist_ok=True)
    filas = ["# Hojas CSV de la guía HL7 v2-to-FHIR, repositorio HL7/v2-to-fhir, commit %s (CC0)" % COMMIT,
             "# sha256  nombre del laboratorio  <-  ruta en el repositorio"]
    for carpeta, nombre, lab in HOJAS:
        ruta, b = traer(carpeta, nombre)
        open(os.path.join(salida, "original", nombre), "wb").write(b)
        open(os.path.join(salida, lab), "wb").write(b)
        filas.append("%s  %s  <-  %s" % (hashlib.sha256(b).hexdigest(), lab, ruta))
    filas.append("# Las que el juez ya tiene (cv/guia/), frente a las del mismo commit:")
    for carpeta, nombre, lab in YA:
        ruta, b = traer(carpeta, nombre)
        local = open(os.path.join(GUIA_LAB, lab), "rb").read()
        filas.append("# %s: %s" % (lab, "IGUAL" if local == b else "DISTINTA (sha256 commit %s, laboratorio %s)" % (
            hashlib.sha256(b).hexdigest()[:12], hashlib.sha256(local).hexdigest()[:12])))
    open(os.path.join(salida, "FUENTES.txt"), "w", encoding="utf-8").write("\n".join(filas) + "\n")
    print("\n".join(filas))


if __name__ == "__main__":
    main(sys.argv[1])
