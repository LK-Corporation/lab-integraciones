#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MD0: la carpeta cerrada para el diseño de Fable (ANTES-ETAPA-MDM.md), como vx/caja_vx0.py.
A ciegas de lo que devuelven los conversores: ni sus plantillas, ni sus salidas, ni sus muestras, ni el contraste de los
estudios (RESULTADO-CV3, CLASES-CV3, RESULTADO-VXU, CLASES-VX3, los pares mínimos), ni nada de privado/ salvo las hojas de la
guía que se trajeron para MDM. Solo el juez, lo que declara, los diseños y las decisiones de los estudios, y el estándar.
Se ejecuta desde fase12/:
  python3 md/caja_md0.py      -> /tmp/md0/ (y su lista de ficheros con sha256 en /tmp/md0/MANIFIESTO.txt)"""
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
GUIA_MDM = os.path.join(FASE, "..", "privado", "mdm", "guia_csv")
CAJA = "/tmp/md0"
os.chdir(FASE)
sys.path.insert(0, FASE)
sys.argv = ["x", "--silencio"]
import mcp_verificador as M  # noqa: E402

JUEZ = [f for f in M.FICHEROS if f.endswith(".py") or f.endswith(".json")] + [
    "prueba_conversion.py", "bases_oru.py", "bases_vxu.py", "cv/verificar_conversor.py", "cv/prueba_vc.py", "cv/conversor_juguete.py"]
RESULTADOS = ["ANTES-ETAPA-MDM.md", "ANTES-ETAPA-VXU.md", "ANTES-ETAPA-CONVERSORES.md", "cv/diseno-conversores-fable.md",
              "cv/decisiones-qcv.md", "vx/diseno-vx-fable.md", "vx/decisiones-qvx.md"]
V25 = os.path.join(EST, "hl7v2", "HL7_Messaging_v25", "txt")
ESTANDAR = [(os.path.join(V25, c + ".txt"), "estandar/hl7v25_%s.txt" % c.upper()) for c in ("CH02", "CH02A", "Ch03", "CH04", "CH07", "CH09")]
FHIR = ["bundle", "patient", "documentreference", "attachment", "practitioner", "organization", "location", "encounter",
        "servicerequest", "observation", "messageheader", "provenance"]
FHIR_TERM = ["valueset-composition-status", "codesystem-composition-status", "valueset-document-reference-status",
             "codesystem-document-reference-status", "valueset-c80-doc-typecodes", "valueset-doc-typecodes",
             "valueset-security-labels", "valueset-mimetypes"]


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
    for p in sorted(glob.glob(os.path.join(FASE, "cv", "guia", "*.csv"))) + sorted(glob.glob(os.path.join(GUIA_MDM, "*.csv"))):
        copiar(p, os.path.join("estandar", "guia_csv", os.path.basename(p)))
    copiar(os.path.join(GUIA_MDM, "FUENTES.txt"), os.path.join("estandar", "guia_csv", "FUENTES-MDM.txt"))
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
    shutil.copyfile(os.path.join(AQUI, "ENCARGO-MD0.md"), os.path.join(CAJA, "ENCARGO-MD0.md"))
    sanear()
    prohibido = [p for p in glob.glob(os.path.join(CAJA, "**", "*"), recursive=True)
                 if re.search(r"liquid|\.yml$|SampleData|RESULTADO-CV3|CLASES-CV3|cv3_minimos|muestras|contraste|mdpre|RESULTADO-VX|CLASES-VX", p)]
    if prohibido:
        raise SystemExit("PARADA: la caja lleva algo de los conversores: %s" % prohibido[:5])
    man = []
    for d, _, fs in sorted(os.walk(CAJA)):
        for f in sorted(fs):
            p = os.path.join(d, f)
            man.append("%s  %s" % (hashlib.sha256(open(p, "rb").read()).hexdigest(), os.path.relpath(p, CAJA)))
    open(os.path.join(CAJA, "MANIFIESTO.txt"), "w").write("\n".join(man) + "\n")
    print("caja MD0: %d ficheros, %d bytes" % (len(man), sum(os.path.getsize(os.path.join(CAJA, l.split("  ", 1)[1])) for l in man)))


if __name__ == "__main__":
    main()
