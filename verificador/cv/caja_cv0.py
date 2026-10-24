#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CV0: la carpeta cerrada para el diseño de Fable (ANTES-ETAPA-CONVERSORES.md, Q-CV-4), como ve/caja_ve0.py.
A ciegas de lo que devuelven los conversores: ni sus plantillas, ni sus salidas, ni sus salidas esperadas, ni sus muestras,
ni nada de privado/. Solo el juez, lo que declara, CV-pre, los diseños anteriores y el estándar (HL7 v2.5, FHIR R4 y la guía
v2-to-FHIR). Se ejecuta desde fase12/:
  python3 cv/caja_cv0.py      -> /tmp/cv0/ (y su lista de ficheros con sha256 en /tmp/cv0/MANIFIESTO.txt)"""
import glob
import hashlib
import json
import os
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(AQUI)
EST = os.path.join(FASE, "..", "estandares")
CAJA = "/tmp/cv0"
os.chdir(FASE)
sys.path.insert(0, FASE)
sys.argv = ["x", "--silencio"]
import mcp_verificador as M  # noqa: E402

JUEZ = [f for f in M.FICHEROS if f.endswith(".py") or f.endswith(".json")] + ["prueba_verificador.py", "prueba_adt.py",
                                                                             "prueba_oru.py"]
RESULTADOS = ["ANTES-ETAPA-CONVERSORES.md", "RESULTADO-CV-PRE.md", "cv/CV-PRE-E1.json", "diseno-adt-fable.md",
              "diseno-oru-fable.md", "diseno-oru-v11-fable.md", "ve/diseno-verificador-ve-fable.md"]
V25 = os.path.join(EST, "hl7v2", "HL7_Messaging_v25", "txt")
ESTANDAR = [(os.path.join(V25, "CH02.txt"), "estandar/hl7v25_CH02.txt"), (os.path.join(V25, "CH02A.txt"), "estandar/hl7v25_CH02A.txt"),
            (os.path.join(V25, "Ch03.txt"), "estandar/hl7v25_CH03.txt"), (os.path.join(V25, "CH07.txt"), "estandar/hl7v25_CH07.txt")]
FHIR = ["bundle", "patient", "encounter", "observation", "diagnosticreport"]


def copiar(origen, destino):
    d = os.path.join(CAJA, destino)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    shutil.copyfile(origen, d)


def sanear():
    """Como en VE0: los nombres de máquina de la lista de la guarda pasan a «el servidor» en resultados/. No imprime qué
    cambia, solo cuántos."""
    import re
    import antes_de_publicar as G
    ctx = G.cargar(os.path.join(FASE, "..", "publicacion"))
    rx = re.compile("|".join(r"(?<![\w.])%s(?![\w])" % re.escape(m) for m in ctx["maquinas"]), re.I)
    n = 0
    for f in os.listdir(os.path.join(CAJA, "resultados")):
        p = os.path.join(CAJA, "resultados", f)
        t = open(p, encoding="utf-8").read()
        t2, k = rx.subn("el servidor", t)
        if k:
            open(p, "w", encoding="utf-8").write(t2)
            n += k
    print("saneado: %d nombres de máquina en resultados/" % n)


def main():
    if os.path.exists(CAJA):
        shutil.rmtree(CAJA)
    os.makedirs(CAJA)
    for f in JUEZ:
        copiar(f, os.path.join("verificador", f))
    for f in RESULTADOS:
        copiar(f, os.path.join("resultados", os.path.basename(f)))
    for o, d in ESTANDAR:
        copiar(o, d)
    pkg = os.path.join(EST, "v2mappings", "package")
    for p in sorted(glob.glob(os.path.join(pkg, "ConceptMap-*.json"))) + [os.path.join(pkg, "package.json")]:
        copiar(p, os.path.join("estandar", "v2mappings", os.path.basename(p)))
    for p in sorted(glob.glob(os.path.join(AQUI, "guia", "*.csv"))):
        copiar(p, os.path.join("estandar", "guia_csv", os.path.basename(p)))
    for r in FHIR:                           # los ficheros del sitio FHIR se extrajeron con «\» en el nombre
        copiar(os.path.join(EST, "fhir-r4", "site\\%s.profile.json" % r), os.path.join("estandar", "fhir_r4", "%s.profile.json" % r))
    info = M.t_info({})[0]
    json.dump(info, open(os.path.join(CAJA, "verificador", "info_verificador.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"verificar_caso.properties": M.E_PROPS}, open(os.path.join(CAJA, "verificador", "esquema_evidencia.json"), "w",
              encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    copiar(os.path.join(FASE, "contratos", "contrato_canonico_adt.md"), os.path.join("contratos", "contrato_canonico_adt.md"))
    shutil.copyfile(os.path.join(AQUI, "ENCARGO-CV0.md"), os.path.join(CAJA, "ENCARGO-CV0.md"))
    sanear()
    man = []
    for d, _, fs in sorted(os.walk(CAJA)):
        for f in sorted(fs):
            p = os.path.join(d, f)
            man.append("%s  %s" % (hashlib.sha256(open(p, "rb").read()).hexdigest(), os.path.relpath(p, CAJA)))
    open(os.path.join(CAJA, "MANIFIESTO.txt"), "w").write("\n".join(man) + "\n")
    print("caja CV0: %d ficheros, %d bytes" % (len(man), sum(os.path.getsize(os.path.join(CAJA, l.split("  ", 1)[1])) for l in man)))


if __name__ == "__main__":
    main()
