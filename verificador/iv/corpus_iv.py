#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 30 (ANTES-ETAPA-IRISVAL.md): todos los mensajes sintéticos publicados, en una carpeta, para pasarlos por IRIS.
- lab: los 451 de la herramienta (cv/verificar_conversor.generar_corpus, con los mínimos): adt, oru, vxu, mdm y minimos;
- vxu-pares: cv/cv3_minimos_vxu.escribir;
- mdm-pares: los de md/pares_mdm.py, con su mismo bucle de escritura (su main corre además los conversores);
- mdm-eventos: mev/bases_mdmev.main (las 40 bases como T02, T04, T06, T08 y T10);
- au-pares: los de au/pares_auditoria.py, con su mismo bucle de escritura.
Escribe <salida>/<corpus>/… y <salida>/CORPUS-IV.json (id, corpus, fichero, msh9, sha256). Si se le da la carpeta privado, comprueba
byte a byte los pares de MDM y de la auditoría contra los que se corrieron de verdad.
  python3 corpus_iv.py <publicación>/verificador <salida vacía> [<privado>]"""
import glob
import hashlib
import json
import os
import shutil
import sys
import tempfile

VER, SAL = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
PRIV = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 else None
assert not os.path.exists(SAL) or not os.listdir(SAL), "la salida tiene que estar vacía"
os.chdir(VER)
sys.path[:0] = [VER, os.path.join(VER, "cv"), os.path.join(VER, "md"), os.path.join(VER, "mev"), os.path.join(VER, "au")]
_argv, sys.argv = sys.argv, ["x", "--silencio"]
import verificar_conversor as VC  # noqa: E402
import cv3_minimos_vxu as MV  # noqa: E402
import pares_mdm as PM  # noqa: E402
import bases_mdmev as EV  # noqa: E402
import pares_auditoria as PA  # noqa: E402
sys.argv = _argv


def msh9(texto):
    for l in texto.replace("\n", "\r").split("\r"):
        if l.startswith("MSH"):
            f = l.split(l[3]) if len(l) > 3 else []
            return f[8] if len(f) > 8 else None
    return None


filas = []


def apuntar(corpus, ruta):
    datos = open(ruta, "rb").read()
    rel = os.path.relpath(ruta, SAL)
    filas.append({"id": rel, "corpus": corpus, "fichero": rel, "msh9": msh9(datos.decode("utf-8", "replace")),
                  "sha256": hashlib.sha256(datos).hexdigest()})


# lab
tmp = tempfile.mkdtemp()
co = VC.generar_corpus(os.path.join(tmp, "c"), lab=True, minimos=True, propios=[])
for c in co["casos"]:
    origen = os.path.join(tmp, "c", c["fichero"])
    destino = os.path.join(SAL, "lab", c["fichero"])
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    shutil.copyfile(origen, destino)
    apuntar("lab/" + c["corpus"], destino)
assert len([f for f in filas if f["corpus"].startswith("lab/")]) == 451
# vxu-pares
d = os.path.join(SAL, "vxu-pares")
os.makedirs(d)
MV.escribir(d)
for r in sorted(glob.glob(os.path.join(d, "**", "*.hl7"), recursive=True)):
    apuntar("vxu-pares", r)
# mdm-pares (md/pares_mdm.py, main, el bucle de escritura tal cual)
d = os.path.join(SAL, "mdm-pares")
os.makedirs(d)
for pid, _, _, sin, con, _ in PM.PARES:
    for lado, segs in (("sin", sin), ("con", con)):
        segs = PM.campo(segs, "MSH", 9, "MDM-%s-%s" % (pid, lado))
        open(os.path.join(d, "%s-%s.hl7" % (pid, lado)), "w", encoding="utf-8", newline="").write("\r".join(segs) + "\r")
for r in sorted(glob.glob(os.path.join(d, "*.hl7"))):
    apuntar("mdm-pares", r)
# mdm-eventos
d = os.path.join(SAL, "mdm-eventos")
EV.main(d)
for r in sorted(glob.glob(os.path.join(d, "**", "*.hl7"), recursive=True)):
    apuntar("mdm-eventos", r)
# au-pares (au/pares_auditoria.py, main, el bucle de escritura tal cual)
d = os.path.join(SAL, "au-pares")
os.makedirs(d)
for pid, _, _, _, caso, controles in PA.PARES:
    for lado, texto in [("caso", caso)] + [("control-" + k, t) for k, t in controles]:
        open(os.path.join(d, "%s-%s.hl7" % (pid, lado)), "w", encoding="utf-8", newline="").write(texto + "\r")
for r in sorted(glob.glob(os.path.join(d, "*.hl7"))):
    apuntar("au-pares", r)

comprobado = {}
if PRIV:
    for corpus, patron in (("mdm-pares", "mdm/**/pares/*.hl7"), ("au-pares", "au/**/pares/*.hl7")):
        reales = {}
        for r in glob.glob(os.path.join(PRIV, patron), recursive=True):
            reales.setdefault(os.path.basename(r), set()).add(hashlib.sha256(open(r, "rb").read()).hexdigest())
        mios = [f for f in filas if f["corpus"] == corpus]
        iguales = sum(1 for f in mios if f["sha256"] in reales.get(os.path.basename(f["fichero"]), set()))
        comprobado[corpus] = {"n": len(mios), "iguales_a_lo_corrido": iguales, "con_copia_en_privado": sum(
            1 for f in mios if os.path.basename(f["fichero"]) in reales)}
json.dump({"filas": filas, "comprobado": comprobado}, open(os.path.join(SAL, "CORPUS-IV.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
cuenta = {}
for f in filas:
    cuenta[f["corpus"]] = cuenta.get(f["corpus"], 0) + 1
print(json.dumps({"n": len(filas), "por_corpus": cuenta, "comprobado": comprobado}, ensure_ascii=False))
