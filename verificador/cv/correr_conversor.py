#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CV1-d / CV2: corre un conversor de terceros sobre una carpeta de mensajes, en su caja (condición 2 del ANTES: docker sin red,
sistema de ficheros de solo lectura, usuario nobody, sin capacidades), y escribe una evidencia por mensaje con la forma que lee
el juez (S-CV-2): {mensaje, punto_entrada, conversion: {conversor: {nombre, version, huella}, salida: {estado, bundle|error,
duracion_ms}}}. No toca el mensaje ni el Bundle: el juicio es del verificador.

  python3 cv/correr_conversor.py microsoft|linuxforhealth <carpeta con .hl7> <carpeta de evidencias>

Los artefactos de cada conversor viven fuera de git, en privado/cv/conversores/ (E-CV-3); aquí solo se calcula su huella.
Con CV_VARIANTE=main corre la rama principal construida en la etapa 15a (ms-main, lfh-main), en la misma caja."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "privado", "cv", "conversores")
CAJA = ["--rm", "--network", "none", "--read-only", "--tmpfs", "/tmp", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
        "--user", "65534:65534", "-e", "HOME=/tmp"]
PRINCIPAL = os.environ.get("CV_VARIANTE") == "main"          # etapa 15a
DIR_MS, DIR_LFH = ("ms-main", "lfh-main") if PRINCIPAL else ("ms", "lfh")
RUNTIME_MS = "mcr.microsoft.com/dotnet/runtime:%s" % ("8.0" if PRINCIPAL else "6.0")


def huella_carpeta(d):
    h = hashlib.sha256()
    for raiz, _, fs in sorted(os.walk(d)):
        for f in sorted(fs):
            p = os.path.join(raiz, f)
            h.update(hashlib.sha256(open(p, "rb").read()).hexdigest().encode())
    return h.hexdigest()


def conversor(nombre):
    if nombre == "microsoft":
        b = os.path.join(BASE, DIR_MS)
        return {"nombre": "microsoft-fhir-converter", "version": "main (70fd328)" if PRINCIPAL else "v7.0 (253307f)",
                "huella": hashlib.sha256((huella_carpeta(os.path.join(b, "out")) +
                                          huella_carpeta(os.path.join(b, "src", "data", "Templates", "Hl7v2"))).encode()).hexdigest()}
    b = os.path.join(BASE, DIR_LFH)
    return {"nombre": "linuxforhealth-hl7v2-fhir-converter",
            "version": "master (2cb72c2), construido con Gradle" if PRINCIPAL else "v1.1.0 (Maven Central; DV-CV-3)",
            "huella": hashlib.sha256((huella_carpeta(os.path.join(b, "lib")) +
                                      hashlib.sha256(open(os.path.join(b, "Arnes.java"), "rb").read()).hexdigest()).encode()).hexdigest()}


def plantilla(texto):
    """Microsoft elige la plantilla raíz por MSH-9 (tipo_evento: ADT_A01, ORU_R01). DV-CV-12: MSH-9 se lee con los separadores
    del propio mensaje (MSH-1 y el primer carácter de MSH-2); E2 trae mensajes con «#$%*!»."""
    msh = texto.lstrip("﻿").replace("\r\n", "\r").replace("\n", "\r").split("\r")[0]
    if len(msh) < 5:
        return ""
    f = msh[3]
    p = msh.split(f)
    comp = p[1][0] if len(p) > 1 and p[1] else "^"
    c = (p[8] if len(p) > 8 else "").split(comp)
    return ("%s_%s" % (c[0], c[1]) if len(c) > 1 else c[0]).upper()


def correr_microsoft(entrada, salida, ficheros):
    b = os.path.join(BASE, DIR_MS)
    por_plantilla = {}
    for f in ficheros:
        por_plantilla.setdefault(plantilla(open(os.path.join(entrada, f), encoding="utf-8").read()), []).append(f)
    out = {}
    for pl, fs in sorted(por_plantilla.items()):
        tin, tout = tempfile.mkdtemp(prefix="cv_in_"), tempfile.mkdtemp(prefix="cv_out_")
        os.chmod(tout, 0o777)
        os.chmod(tin, 0o755)                                 # el contenedor corre como nobody: la entrada, solo de lectura
        for f in fs:
            shutil.copyfile(os.path.join(entrada, f), os.path.join(tin, f))
        t0 = time.time()
        if not os.path.exists(os.path.join(b, "src", "data", "Templates", "Hl7v2", pl + ".liquid")):
            for f in fs:
                out[f] = {"estado": "error", "error": {"codigo": "sin_plantilla", "texto": "no hay plantilla %s" % pl}, "duracion_ms": 0}
            continue
        # DV-CV-11: fichero a fichero (-n/-f). En modo carpeta (-i/-o) la herramienta para en el primer fichero que falla y deja
        # la salida sin postprocesar; aquí, un contenedor por plantilla con un bucle dentro y el registro de cada fichero aparte.
        bucle = ('for f in /in/*.hl7; do b=$(basename "$f" .hl7); dotnet /app/Microsoft.Health.Fhir.Liquid.Converter.Tool.dll convert '
                 '-d /tpl -r %s -n "$f" -f "/salida/$b.json" > "/salida/$b.log" 2>&1; echo $? > "/salida/$b.rc"; done' % pl)
        r = subprocess.run(["docker", "run"] + CAJA + ["-e", "DOTNET_CLI_TELEMETRY_OPTOUT=1", "-v", "%s:/app:ro" % os.path.join(b, "out"),
                           "-v", "%s:/tpl:ro" % os.path.join(b, "src", "data", "Templates", "Hl7v2"), "-v", "%s:/in:ro" % tin,
                           "-v", "%s:/salida" % tout, RUNTIME_MS, "sh", "-c", bucle],
                           capture_output=True, text=True, timeout=3600)
        ms = int((time.time() - t0) * 1000 / max(len(fs), 1))
        for f in fs:
            base = os.path.splitext(f)[0]
            j, log, rc = (os.path.join(tout, base + x) for x in (".json", ".log", ".rc"))
            texto_log = open(log, encoding="utf-8", errors="replace").read() if os.path.exists(log) else (r.stdout + r.stderr)
            if not os.path.exists(j):
                cod = open(rc).read().strip() if os.path.exists(rc) else str(r.returncode)
                out[f] = {"estado": "error" if os.path.exists(rc) else "sin_respuesta",
                          "error": {"codigo": cod, "texto": texto_log[-4000:]}, "duracion_ms": ms}
                continue
            d = json.loads(open(j, encoding="utf-8").read())
            if d.get("Status") == "OK" and isinstance(d.get("FhirResource"), dict):
                out[f] = {"estado": "bundle", "bundle": json.dumps(d["FhirResource"], ensure_ascii=False), "duracion_ms": ms}
            else:
                out[f] = {"estado": "error", "error": {"codigo": str(d.get("Status")), "texto": json.dumps(d, ensure_ascii=False)[:4000]},
                          "duracion_ms": ms}
        shutil.rmtree(tin, ignore_errors=True)
        shutil.rmtree(tout, ignore_errors=True)
    return out


def correr_lfh(entrada, salida, ficheros):
    b = os.path.join(BASE, DIR_LFH)
    tin, tout = tempfile.mkdtemp(prefix="cv_in_"), tempfile.mkdtemp(prefix="cv_out_")
    os.chmod(tout, 0o777)
    os.chmod(tin, 0o755)
    for f in ficheros:
        shutil.copyfile(os.path.join(entrada, f), os.path.join(tin, f))
    t0 = time.time()
    r = subprocess.run(["docker", "run"] + CAJA + ["-v", "%s:/lib2:ro" % os.path.join(b, "lib"), "-v", "%s:/clases:ro" % os.path.join(b, "clases"),
                       "-v", "%s:/in:ro" % tin, "-v", "%s:/salida" % tout, "maven:3.9-eclipse-temurin-11", "java", "-cp", "/clases:/lib2/*",
                       "Arnes", "/in", "/salida"], capture_output=True, text=True, timeout=3600)
    tiempos = dict(re.findall(r"^(\S+) (\d+) ms$", r.stdout, re.M))
    out = {}
    for f in ficheros:
        ms = int(tiempos.get(f, 0))
        j, e = os.path.join(tout, f + ".json"), os.path.join(tout, f + ".error")
        if os.path.exists(j):
            out[f] = {"estado": "bundle", "bundle": open(j, encoding="utf-8").read(), "duracion_ms": ms}
        elif os.path.exists(e):
            out[f] = {"estado": "error", "error": {"codigo": "excepcion", "texto": open(e, encoding="utf-8").read()[:4000]}, "duracion_ms": ms}
        else:
            out[f] = {"estado": "sin_respuesta", "error": {"codigo": str(r.returncode), "texto": (r.stdout + r.stderr)[-4000:]}, "duracion_ms": ms}
    shutil.rmtree(tin, ignore_errors=True)
    shutil.rmtree(tout, ignore_errors=True)
    return out


def main(nombre, entrada, salida):
    os.makedirs(salida, exist_ok=True)
    fs = sorted(f for f in os.listdir(entrada) if f.endswith(".hl7"))
    res = (correr_microsoft if nombre == "microsoft" else correr_lfh)(entrada, salida, fs)
    cv = conversor(nombre)
    for f in fs:
        texto = open(os.path.join(entrada, f), encoding="utf-8").read()
        pe = "oru_conv" if plantilla(texto).startswith("ORU") else "adt_conv"
        s = res[f]
        if s.get("estado") == "bundle" and len(s["bundle"]) > 4000000:
            s = {"estado": "error", "error": {"codigo": "demasiado_grande", "texto": "%d caracteres" % len(s["bundle"])}, "duracion_ms": s["duracion_ms"]}
        e = {"punto_entrada": pe, "mensaje": texto, "conversion": {"conversor": cv, "salida": s, "perfil_valor": "guia"}}
        json.dump(e, open(os.path.join(salida, os.path.splitext(f)[0] + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("%s: %d mensajes; %s" % (nombre, len(fs), {k: sum(1 for x in res.values() if x["estado"] == k) for k in ("bundle", "error", "sin_respuesta")}))


if __name__ == "__main__":
    main(*sys.argv[1:4])
