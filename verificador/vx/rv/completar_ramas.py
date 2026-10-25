#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 22, paso 6 (diseno-rv-fable.md §4.4): completa RAMAS-RV.json con el commit de hoy, su fecha, si se reconstruyó, la
versión del adaptador de rama y su huella. Aparte de ramas_vxu.py, que está sellado (DV-RV-1).
  python3 vx/rv/completar_ramas.py <compare-ms.json> <compare-lfh.json> <RAMAS-RV.json> <artefactos> [<carpeta del control>]"""
import json
import os
import sys

RV_D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RV_D)
_argv, sys.argv = sys.argv, ["x", "--silencio"]
import ramas_vxu as RV  # noqa: E402
sys.argv = _argv

cms, clfh, ruta, art = sys.argv[1:5]
control = sys.argv[5] if len(sys.argv) > 5 else None                       # DV-RV-8: la imagen con la que corrió cada rama
ramas = json.load(open(ruta, encoding="utf-8"))
for conv, comp, ad, corrida in (("microsoft", cms, RV.RAMA["microsoft"], "ms"), ("linuxforhealth", clfh, RV.RAMA["lfh_lote"], "lfh-mensaje")):
    if control and os.path.exists(os.path.join(control, "rama", corrida, "CORRIDA.json")):
        cr = json.load(open(os.path.join(control, "rama", corrida, "CORRIDA.json"), encoding="utf-8"))
        ramas[conv].update({"imagen_ejecucion": cr["imagen"], "imagen_digest": cr["imagen_digest"]})
    c = json.load(open(comp, encoding="utf-8"))
    head = c["base_commit"] if c["ahead_by"] == 0 else c["commits"][-1]
    a = RV.VC.leer_adaptador(ad, art)
    ramas[conv].update({"repositorio": c["base_commit"]["html_url"].split("/commit/")[0].replace("https://github.com/", ""),
                        "commit_15A": c["base_commit"]["sha"], "commit_hoy": head["sha"],
                        "fecha_commit_hoy": head["commit"]["committer"]["date"], "reconstruida": False,
                        "construccion": "la de 15A (24-oct): la rama no avanzó" if c["ahead_by"] == 0 else "la de 15A: avanzó sin tocar VXU",
                        "version": a["conversor"]["version"], "huella": RV.VC.huella(a, art),
                        "huella_con_nombres": RV.VC.huella_con_nombres(a, art)})
json.dump(ramas, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({k: (v["commit_hoy"][:7], v["version"], v["huella"][:12], v["reconstruida"]) for k, v in ramas.items()})
