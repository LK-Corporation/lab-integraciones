#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 32 (ANTES-ETAPA-IVDECLARADA.md): las muestras de la 31 (../privado/ivm/corpus), repartidas por la versión que declaran
(el primer componente de MSH-12): ../privado/ivd/corpus251 (la 2.5.1) y ../privado/ivd/corpusst (2.3, 2.4, 2.6 y 2.8), cada una
con su CORPUS-IV.json. Las que declaran la 2.5 se quedan fuera, con su veredicto de la 31. Copia los ficheros tal cual y comprueba
su sha256. Escribe ivd/CORPUS-IVD-lista.json (publicable: id, grupo, versión y sha256).  python3 ivd/corpus_ivd.py"""
import collections
import hashlib
import json
import os
import shutil
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(FASE, "ivd"))
import validar_ivdst as V  # noqa: E402  (solo para leer los segmentos y la versión, como el conductor)

ORIG = os.path.normpath(os.path.join(FASE, "..", "privado", "ivm", "corpus"))
DEST = {"251": os.path.normpath(os.path.join(FASE, "..", "privado", "ivd", "corpus251")),
        "st": os.path.normpath(os.path.join(FASE, "..", "privado", "ivd", "corpusst"))}
for d in DEST.values():
    assert not os.path.exists(d), "%s ya existe: bórralo a mano si quieres rehacerlo" % d
filas = json.load(open(os.path.join(ORIG, "CORPUS-IV.json"), encoding="utf-8"))["filas"]
reparto, lista, fuera = collections.defaultdict(list), [], []
for f in filas:
    datos = open(os.path.join(ORIG, f["fichero"]), "rb").read()
    assert hashlib.sha256(datos).hexdigest() == f["sha256"], f["id"]
    ver = V.version_de(V.segmentos(datos.decode("utf-8")))
    grupo = "251" if ver == "2.5.1" else ("st" if ver in ("2.3", "2.4", "2.6", "2.8") else None)
    lista.append({"id": f["id"], "corpus": f["corpus"], "version": ver, "sha256": f["sha256"],
                  "conductor": {"251": "validar_ivd251", "st": "validar_ivdst"}.get(grupo, "ninguno: se queda con la 31")})
    if grupo is None:
        assert ver == "2.5", (f["id"], ver)
        fuera.append(f["id"])
        continue
    destino = os.path.join(DEST[grupo], f["fichero"])
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    shutil.copyfile(os.path.join(ORIG, f["fichero"]), destino)
    reparto[grupo].append(f)
for g, fs in reparto.items():
    json.dump({"filas": fs, "origen": "../privado/ivm/corpus (etapa 31), las de la versión del grupo %s" % g},
              open(os.path.join(DEST[g], "CORPUS-IV.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump({"muestras": lista, "fuera": fuera,
           "por_version": dict(collections.Counter(x["version"] for x in lista))},
          open(os.path.join(FASE, "ivd", "CORPUS-IVD-lista.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("251: %d; sin texto: %d; fuera (2.5): %d; por versión: %s" % (
    len(reparto["251"]), len(reparto["st"]), len(fuera), dict(collections.Counter(x["version"] for x in lista))))
