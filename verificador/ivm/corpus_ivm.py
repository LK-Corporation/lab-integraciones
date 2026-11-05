#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 31 (ANTES-ETAPA-IVMUESTRAS.md): las muestras públicas de los dos conversores, en una carpeta, como las junta la herramienta
(cv/verificar_conversor.generar_corpus con `muestras`, que lee <carpeta>/ms y <carpeta>/lfh y normaliza el texto):
- cv: las del estudio de conversores (ADT y ORU);
- vxu: las de VXU;
- mdm: las de MDM.
Escribe <salida>/<grupo>/… y <salida>/CORPUS-IV.json (id, corpus, fichero, msh9, sha256), con la misma forma que iv/corpus_iv.py.
  python3 ivm/corpus_ivm.py <publicación>/verificador <privado> <salida vacía>"""
import hashlib
import json
import os
import shutil
import sys
import tempfile

VER, PRIV, SAL = (os.path.abspath(x) for x in sys.argv[1:4])
assert not os.path.exists(SAL) or not os.listdir(SAL), "la salida tiene que estar vacía"
os.chdir(VER)
sys.path[:0] = [VER, os.path.join(VER, "cv")]
_argv, sys.argv = sys.argv, ["x", "--silencio"]
import verificar_conversor as VC  # noqa: E402
sys.argv = _argv
GRUPOS = {"cv": os.path.join(PRIV, "cv", "muestras"), "vxu": os.path.join(PRIV, "vxu", "muestras"),
          "mdm": os.path.join(PRIV, "mdm", "muestras")}
filas = []
for g, d in GRUPOS.items():
    tmp = tempfile.mkdtemp()
    co = VC.generar_corpus(os.path.join(tmp, "c"), lab=False, minimos=False, propios=[], muestras=d)
    for c in co["casos"]:
        destino = os.path.join(SAL, g, os.path.basename(c["fichero"]))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        shutil.copyfile(os.path.join(tmp, "c", c["fichero"]), destino)
        datos = open(destino, "rb").read()
        rel = os.path.relpath(destino, SAL)
        filas.append({"id": rel, "corpus": "muestras/" + g, "fichero": rel, "msh9": c.get("msh9"),
                      "sha256": hashlib.sha256(datos).hexdigest()})
json.dump({"filas": filas}, open(os.path.join(SAL, "CORPUS-IV.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
cuenta = {}
for f in filas:
    cuenta[f["corpus"]] = cuenta.get(f["corpus"], 0) + 1
print(json.dumps({"n": len(filas), "por_grupo": cuenta, "distintas": len({f["sha256"] for f in filas})}, ensure_ascii=False))
