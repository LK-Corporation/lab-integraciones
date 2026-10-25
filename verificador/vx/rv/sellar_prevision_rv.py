#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 22 (vx/rv/diseno-rv-fable.md §8): escribe PREVISION-RV.json con el juez y la herramienta añadidos al cuerpo de la
previsión, y SELLO-RV.txt con la huella de lo sellado (rutas relativas a su carpeta). Por omisión escribe en vx/rv/; quien repite
la medida sella la suya en otra carpeta y se la pasa a ramas_vxu.py correr con --sello. Se niega a pisar un sello. Después, el
commit: el orquestador lo exige. Copia adaptada de cv/ar/sellar_prevision.py.
  python3 vx/rv/sellar_prevision_rv.py <cuerpo.json> [<carpeta>]      # desde verificador/ (o fase12/)"""
import datetime
import hashlib
import json
import os
import sys

RV_D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RV_D)
_argv, sys.argv = sys.argv, ["x", "--silencio"]
import ramas_vxu as RV  # noqa: E402
sys.argv = _argv


def sha(ruta):
    return hashlib.sha256(open(ruta, "rb").read()).hexdigest()


def sellar(cuerpo_json, carpeta=RV_D):
    if os.path.exists(os.path.join(carpeta, "SELLO-RV.txt")):
        raise SystemExit("ya hay un SELLO-RV.txt en %s: no se pisa un sello; sella en otra carpeta" % carpeta)
    os.makedirs(carpeta, exist_ok=True)
    p = dict(json.load(open(cuerpo_json, encoding="utf-8")))
    aparato = [os.path.join(RV_D, "ramas_vxu.py"), os.path.join(RV_D, "prueba_rv.py"), RV.RAMA["microsoft"], RV.RAMA["lfh_lote"],
               RV.RAMA["lfh_mensaje"], os.path.join(RV.CVD, "cv3_minimos_vxu.py"), os.path.join(RV.CVD, "verificar_conversor.py")]
    p.update({"fecha": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "juez": RV.VC.M._version()["huella"],
              "herramienta": {os.path.basename(f): sha(f) for f in aparato}})
    faltan = [k for k in RV.CLAVES_PREVISION_RV if k not in p]
    assert not faltan, faltan
    ruta = os.path.join(carpeta, "PREVISION-RV.json")
    open(ruta, "w", encoding="utf-8").write(json.dumps(p, ensure_ascii=False, indent=1) + "\n")
    sellados = [ruta] + [f for f in [os.path.join(carpeta, "PREVISION-RV.md")] if os.path.exists(f)] + aparato
    lineas = ["# Sello de la previsión de la etapa 22 (las nueve de VXU en las ramas), %s, antes de cualquier corrida con Docker "
              "y de consultar GitHub" % p["fecha"]]
    lineas += ["%s  %s" % (sha(f), os.path.relpath(f, carpeta)) for f in sellados]
    lineas.append("juez %s" % p["juez"])
    open(os.path.join(carpeta, "SELLO-RV.txt"), "w", encoding="utf-8").write("\n".join(lineas) + "\n")
    assert RV.comprobar_sello_rv(ruta, os.path.join(carpeta, "SELLO-RV.txt"))
    print("sellado: juez %s, %d ficheros" % (p["juez"][:12], len(sellados)))


if __name__ == "__main__":
    sellar(sys.argv[1], *(sys.argv[2:3]))
