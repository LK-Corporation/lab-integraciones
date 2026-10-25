#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VX0: la carpeta cerrada para el diseño de Fable (ANTES-ETAPA-VXU.md), como cv/caja_cv0.py.
A ciegas de lo que devuelven los conversores: ni sus plantillas, ni sus salidas, ni sus muestras, ni el contraste del estudio
(RESULTADO-CV3, CLASES-CV3, los pares mínimos), ni nada de privado/ salvo las hojas de la guía que se trajeron para VXU. Solo
el juez, lo que declara, el diseño y las decisiones del estudio, y el estándar. Se ejecuta desde fase12/:
  python3 vx/caja_vx0.py      -> /tmp/vx0/ (y su lista de ficheros con sha256 en /tmp/vx0/MANIFIESTO.txt)"""
import glob
import hashlib
import json
import os
import re
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(AQUI)
EST = os.path.join(FASE, "..", "estandares")
GUIA_VXU = os.path.join(FASE, "..", "privado", "vxu", "guia_csv")
CAJA = "/tmp/vx0"
os.chdir(FASE)
sys.path.insert(0, FASE)
sys.argv = ["x", "--silencio"]
import mcp_verificador as M  # noqa: E402

JUEZ = [f for f in M.FICHEROS if f.endswith(".py") or f.endswith(".json")] + [
    "prueba_conversion.py", "bases_oru.py", "cv/verificar_conversor.py", "cv/prueba_vc.py", "cv/conversor_juguete.py"]
RESULTADOS = ["ANTES-ETAPA-VXU.md", "ANTES-ETAPA-CONVERSORES.md", "cv/diseno-conversores-fable.md", "cv/decisiones-qcv.md"]
V25 = os.path.join(EST, "hl7v2", "HL7_Messaging_v25", "txt")
ESTANDAR = [(os.path.join(V25, c + ".txt"), "estandar/hl7v25_%s.txt" % c.upper()) for c in ("CH02", "CH02A", "Ch03", "CH04", "CH07")]
FHIR = ["bundle", "patient", "immunization", "practitioner", "organization", "location", "relatedperson", "observation",
        "messageheader", "provenance"]
FHIR_TERM = ["codesystem-event-status", "valueset-immunization-status", "valueset-immunization-status-reason"]


def copiar(origen, destino):
    d = os.path.join(CAJA, destino)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    shutil.copyfile(origen, d)


def sanear():
    """Como en CV0: los nombres de máquina de la lista de la guarda pasan a «el servidor» en resultados/."""
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
    for p in sorted(glob.glob(os.path.join(FASE, "cv", "guia", "*.csv"))) + sorted(glob.glob(os.path.join(GUIA_VXU, "*.csv"))):
        copiar(p, os.path.join("estandar", "guia_csv", os.path.basename(p)))
    copiar(os.path.join(GUIA_VXU, "FUENTES.txt"), os.path.join("estandar", "guia_csv", "FUENTES-VXU.txt"))
    for r in FHIR:                           # los ficheros del sitio FHIR se extrajeron con «\» en el nombre
        copiar(os.path.join(EST, "fhir-r4", "site\\%s.profile.json" % r), os.path.join("estandar", "fhir_r4", "%s.profile.json" % r))
    for r in FHIR_TERM:
        p = os.path.join(EST, "fhir-r4", "site\\%s.json" % r)
        if os.path.exists(p):
            copiar(p, os.path.join("estandar", "fhir_r4", "%s.json" % r))
    info = M.t_info({})[0]
    json.dump(info, open(os.path.join(CAJA, "verificador", "info_verificador.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"verificar_caso.properties": M.E_PROPS}, open(os.path.join(CAJA, "verificador", "esquema_evidencia.json"), "w",
              encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    shutil.copyfile(os.path.join(AQUI, "ENCARGO-VX0.md"), os.path.join(CAJA, "ENCARGO-VX0.md"))
    sanear()
    prohibido = [p for p in glob.glob(os.path.join(CAJA, "**", "*"), recursive=True)
                 if re.search(r"liquid|\.yml$|SampleData|RESULTADO-CV3|CLASES-CV3|cv3_minimos|muestras", p)]
    if prohibido:
        raise SystemExit("PARADA: la caja lleva algo de los conversores: %s" % prohibido[:5])
    man = []
    for d, _, fs in sorted(os.walk(CAJA)):
        for f in sorted(fs):
            p = os.path.join(d, f)
            man.append("%s  %s" % (hashlib.sha256(open(p, "rb").read()).hexdigest(), os.path.relpath(p, CAJA)))
    open(os.path.join(CAJA, "MANIFIESTO.txt"), "w").write("\n".join(man) + "\n")
    print("caja VX0: %d ficheros, %d bytes" % (len(man), sum(os.path.getsize(os.path.join(CAJA, l.split("  ", 1)[1])) for l in man)))


if __name__ == "__main__":
    main()
