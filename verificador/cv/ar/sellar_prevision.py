#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 21 (diseno-ar-fable.md §10.3): escribe PREVISION-AR.json con las identidades (juez, conversor, imagen, herramienta)
añadidas al cuerpo de la previsión, y SELLO-AR.txt con la huella de lo sellado. Las rutas del sello son relativas a su carpeta
(DV-AR-3). Por omisión escribe en cv/ar/; quien repite la medida sella la suya en otra carpeta y se la pasa a control_ar.py
con --sello (DV-AR-12). Después, el commit: el orquestador lo exige.
  python3 cv/ar/sellar_prevision.py <cuerpo.json> [<carpeta>]      # desde verificador/ (o fase12/); cv/ar/prevision-cuerpo.json es el de la etapa"""
import datetime
import hashlib
import json
import os
import sys

AR_D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AR_D)
_argv, sys.argv = sys.argv, ["x", "--silencio"]
import arrastre as AR  # noqa: E402
sys.argv = _argv


def sha(ruta):
    return hashlib.sha256(open(ruta, "rb").read()).hexdigest()


def sellar(cuerpo_json, carpeta=AR_D):
    if os.path.exists(os.path.join(carpeta, "SELLO-AR.txt")):                  # DV-AR-12: no se pisa un sello
        raise SystemExit("ya hay un SELLO-AR.txt en %s: no se pisa un sello; sella en otra carpeta" % carpeta)
    os.makedirs(carpeta, exist_ok=True)
    cuerpo = json.load(open(cuerpo_json, encoding="utf-8"))
    ad = json.load(open(AR.AD_MENSAJE, encoding="utf-8"))
    p = dict(cuerpo)
    p.update({"fecha": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
              "juez": AR.VC.M._version()["huella"],
              "conversor": "ac41f71b98ee75bac637ecd4b68f58b463f0798bf66cfa941f4194cb2a50acf2",   # la esperada del estudio;
              # la real la comprueba el paso 3 del control (control_ar.ESPERADO), que para si no cuadra
              "imagen_digest": ad["caja"]["imagen_digest"],
              "herramienta": {"verificar_conversor": sha(os.path.join(AR.CVD, "verificar_conversor.py")),
                              "arrastre": sha(os.path.join(AR_D, "arrastre.py")), "control_ar": sha(os.path.join(AR_D, "control_ar.py"))}})
    faltan = [k for k in AR.CLAVES_PREVISION if k not in p]
    assert not faltan, faltan
    ruta = os.path.join(carpeta, "PREVISION-AR.json")
    open(ruta, "w", encoding="utf-8").write(json.dumps(p, ensure_ascii=False, indent=1) + "\n")
    sellados = [ruta, os.path.join(carpeta, "PREVISION-AR.md")] + [os.path.join(AR_D, f) for f in ("arrastre.py", "control_ar.py", "prueba_ar.py")] + \
        [AR.AD_LOTE, AR.AD_MENSAJE, os.path.join(AR.CVD, "verificar_conversor.py")]
    sellados = [f for f in sellados if os.path.exists(f)]                      # PREVISION-AR.md, si quien sella la escribió
    lineas = ["# Sello de la previsión de la etapa 21 (arrastre), %s, antes de cualquier corrida con Docker" % p["fecha"]]
    lineas += ["%s  %s" % (sha(f), os.path.relpath(f, carpeta)) for f in sellados]
    lineas.append("juez %s" % p["juez"])
    open(os.path.join(carpeta, "SELLO-AR.txt"), "w", encoding="utf-8").write("\n".join(lineas) + "\n")
    assert AR.comprobar_sello(ruta, os.path.join(carpeta, "SELLO-AR.txt"))
    print("sellado: juez %s, %d ficheros" % (p["juez"][:12], len(sellados)))


if __name__ == "__main__":
    sellar(sys.argv[1], *(sys.argv[2:3]))
