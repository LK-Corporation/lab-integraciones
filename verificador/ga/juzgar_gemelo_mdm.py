#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33 (Q-GA-8): el juicio del gemelo de MP1 (el par de MD-M5) con contenido ED. Confirmada = Microsoft rechaza el caso (TXA-8
repetido) y convierte el control, en el original y en el gemelo; y los dos gemelos son válidos para el aparato de la 30.
  cd fase12 && python3 ga/juzgar_gemelo_mdm.py <VEREDICTOS de los cuatro> <corrida de Microsoft>      -> ga/GEMELO-MDM.json"""
import json
import os
import sys

GA = os.path.dirname(os.path.abspath(__file__))
VER, COR = sys.argv[1:3]
v = {os.path.basename(json.loads(l)["id"])[:-4]: json.loads(l)["veredicto_sostenido"] for l in open(VER, encoding="utf-8")}
j = {x["caso"]: x for x in map(json.loads, open(os.path.join(COR, "juicio.jsonl"), encoding="utf-8"))}
r = {}
for lado in ("", "-ED"):
    caso, ctl = j["MDM-MP1-con" + lado], j["MDM-MP1-sin" + lado]
    r["gemelo" if lado else "original"] = {
        "caso": {"valido": v["MDM-MP1-con" + lado], "estado": caso["estado"], "categoria": caso["categoria"]},
        "control": {"valido": v["MDM-MP1-sin" + lado], "estado": ctl["estado"], "categoria": ctl["categoria"]},
        "confirmada": caso["estado"] != "bundle" and ctl["estado"] == "bundle"}
r["se_reproduce_en_valido"] = r["gemelo"]["confirmada"] and r["gemelo"]["caso"]["valido"] == "valido" == r["gemelo"]["control"]["valido"]
json.dump(r, open(os.path.join(GA, "GEMELO-MDM.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(r, ensure_ascii=False))
