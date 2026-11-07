#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33: el corpus de la versión 2 para el aparato de la etapa 30 (iv/validar_iv.py y iv/lectura_iv.py, sin cambiarlos), con los
mismos lotes y nombres que iv/corpus_iv.py y uno más, los gemelos:
- lab: generar_corpus(version=2, lab=True, minimos=True): 270 ADT, 40 ORU, 40 VXU, 40 MDM (con B36 v2) y 68 mínimos;
- vxu-pares, mdm-pares y au-pares: como en la 30 (no cambian);
- mdm-eventos: mev/bases_mdmev.derivar sobre las bases de la versión 2 (ga/bases_mdm_v2.py), con los nombres de la 28;
- gemelos: los 37 de ga/gemelos/.
Escribe <salida>/<lote>/… y <salida>/CORPUS-IV.json (filas: id, corpus, fichero, msh9, sha256), como corpus_iv.py.
  cd fase12 && python3 ga/corpus_ga.py <salida vacía>"""
import glob
import hashlib
import json
import os
import shutil
import sys
import tempfile

GA = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(GA)
SAL = os.path.abspath(sys.argv[1])
assert not os.path.exists(SAL) or not os.listdir(SAL), "la salida tiene que estar vacía"
os.chdir(FASE)
sys.path[:0] = [GA, FASE, os.path.join(FASE, "cv"), os.path.join(FASE, "md"), os.path.join(FASE, "mev"), os.path.join(FASE, "au")]
_argv, sys.argv = sys.argv, ["x", "--silencio"]
import verificar_conversor as VC  # noqa: E402
import cv3_minimos_vxu as MV  # noqa: E402
import pares_mdm as PM  # noqa: E402
import bases_mdmev as EV  # noqa: E402
import pares_auditoria as PA  # noqa: E402
import bases_mdm_v2 as B2  # noqa: E402
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


tmp = tempfile.mkdtemp()
co = VC.generar_corpus(os.path.join(tmp, "c"), lab=True, minimos=True, propios=[], version=2)
for c in co["casos"]:
    destino = os.path.join(SAL, "lab", c["fichero"])
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    shutil.copyfile(os.path.join(tmp, "c", c["fichero"]), destino)
    apuntar("lab/" + c["corpus"], destino)
shutil.rmtree(tmp)
assert len(filas) == 458, len(filas)
d = os.path.join(SAL, "vxu-pares")
os.makedirs(d)
MV.escribir(d)
for r in sorted(glob.glob(os.path.join(d, "**", "*.hl7"), recursive=True)):
    apuntar("vxu-pares", r)
d = os.path.join(SAL, "mdm-pares")
os.makedirs(d)
for pid, _, _, sin, con, _ in PM.PARES:
    for lado, segs in (("sin", sin), ("con", con)):
        segs = PM.campo(segs, "MSH", 9, "MDM-%s-%s" % (pid, lado))
        open(os.path.join(d, "%s-%s.hl7" % (pid, lado)), "w", encoding="utf-8", newline="").write("\r".join(segs) + "\r")
for r in sorted(glob.glob(os.path.join(d, "*.hl7"))):
    apuntar("mdm-pares", r)
d = os.path.join(SAL, "mdm-eventos")
os.makedirs(d)
for b in B2.BASES:
    for ev in EV.EVENTOS:
        segs = EV.derivar(b, ev)
        EV.comprobar(b, ev, segs)
        open(os.path.join(d, "MDM-%s-%s.hl7" % (b["id"], ev)), "wb").write(("\r".join(segs) + "\r").encode("utf-8"))
for r in sorted(glob.glob(os.path.join(d, "*.hl7"))):
    apuntar("mdm-eventos", r)
d = os.path.join(SAL, "au-pares")
os.makedirs(d)
for pid, _, _, _, caso, controles in PA.PARES:
    for lado, texto in [("caso", caso)] + [("control-" + k, t) for k, t in controles]:
        open(os.path.join(d, "%s-%s.hl7" % (pid, lado)), "w", encoding="utf-8", newline="").write(texto + "\r")
for r in sorted(glob.glob(os.path.join(d, "*.hl7"))):
    apuntar("au-pares", r)
d = os.path.join(SAL, "gemelos")
shutil.copytree(os.path.join(GA, "gemelos"), d)
os.remove(os.path.join(d, "MANIFIESTO.txt"))
for r in sorted(glob.glob(os.path.join(d, "*.hl7"))):
    apuntar("gemelos", r)
cuenta = {}
for f in filas:
    cuenta[f["corpus"]] = cuenta.get(f["corpus"], 0) + 1
json.dump({"filas": filas, "version": 2}, open(os.path.join(SAL, "CORPUS-IV.json"), "w", encoding="utf-8"), ensure_ascii=False,
          indent=1)
print(json.dumps({"n": len(filas), "por_corpus": cuenta}, ensure_ascii=False))
