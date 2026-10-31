#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 25 (cv/ci/diseno-mant-fable.md §6): escribe PREVISION-MANT.json con el juez publicado, las acciones fijadas y la
herramienta añadidos al cuerpo de la previsión, y SELLO-MANT.txt con la huella de lo sellado (rutas relativas a su carpeta). Se
niega a pisar SELLO-MANT.txt y no toca los sellos de la 23 ni la 24. Copia adaptada de cv/ci/sellar_prevision_ci2.py, sin los
ficheros del proyecto de ejemplo, que no cambian (sus huellas están en SELLO-CI2.txt).
  python3 cv/ci/sellar_prevision_mant.py <cuerpo.json> <juez publicado> [<carpeta>]"""
import datetime
import hashlib
import json
import os
import re
import sys

CI_D = os.path.dirname(os.path.abspath(__file__))
CVD = os.path.dirname(CI_D)
CLAVES_PREVISION_MANT = ("etapa", "fecha", "juez", "herramienta", "acciones", "base_de_la_prevision",
                         "probabilidad_demo_verde_en_m1_a_la_primera", "probabilidad_demo_informes_iguales",
                         "probabilidad_ejemplo_verde_en_m2_a_la_primera", "probabilidad_rojo_a_la_primera", "probabilidad_sin_aviso_node20",
                         "probabilidad_pull_request_verde_a_la_primera", "probabilidad_todo_en_una_sesion", "pushes_previstos",
                         "pushes_mas_probable", "minutos_por_corrida_previstos", "rojo_n_casos_previsto", "causas_de_fallo_previstas",
                         "diferencias_que_se_explicarian", "regla_de_parada", "jev")
APARATO = ["github-mant/verificador-conversor.yml", "github-mant/demo-ci.yml", "github-mant/higiene.yml", "github-mant/ejemplo-ci.yml",
           "github-mant/rojo-ci.yml", "ACCIONES-CI.json", "prueba_ci.py", "ensayo_flujo.py", "traer_resultados_ci.py", "anotaciones_ci.py",
           "sellar_prevision_mant.py", "decision-jev-prevision-mant.md"]


def sha(ruta):
    return hashlib.sha256(open(ruta, "rb").read()).hexdigest()


def comprobar_sello(prevision, sello):
    base, vistos = os.path.dirname(os.path.abspath(sello)), set()
    try:
        for linea in open(sello, encoding="utf-8"):
            m = re.match(r"^([0-9a-f]{64})  (\S+)\s*$", linea)
            if m:
                ruta = os.path.realpath(os.path.join(base, m.group(2)))
                if sha(ruta) != m.group(1):
                    return False
                vistos.add(ruta)
        p = json.load(open(prevision, encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return os.path.realpath(prevision) in vistos and all(k in p for k in CLAVES_PREVISION_MANT)


def sellar(cuerpo, juez, carpeta=CI_D):
    if os.path.exists(os.path.join(carpeta, "SELLO-MANT.txt")):
        raise SystemExit("ya hay un SELLO-MANT.txt en %s: no se pisa un sello" % carpeta)
    faltan = [f for f in APARATO if not os.path.exists(os.path.join(CI_D, f))]
    if faltan:
        raise SystemExit("faltan ficheros del aparato: %s" % ", ".join(faltan))
    p = dict(json.load(open(cuerpo, encoding="utf-8")))
    acc = json.load(open(os.path.join(CI_D, "ACCIONES-CI.json"), encoding="utf-8"))["acciones"]
    p.update({"fecha": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "juez": juez,
              "acciones": {a: {"etiqueta": x["etiqueta"], "sha": x["sha"], "node": x["node"]} for a, x in acc.items()},
              "herramienta": dict([(f, sha(os.path.join(CI_D, f))) for f in APARATO] +
                                  [("verificar_conversor.py", sha(os.path.join(CVD, "verificar_conversor.py")))])})
    faltan = [k for k in CLAVES_PREVISION_MANT if k not in p]
    assert not faltan, faltan
    ruta = os.path.join(carpeta, "PREVISION-MANT.json")
    open(ruta, "w", encoding="utf-8").write(json.dumps(p, ensure_ascii=False, indent=1) + "\n")
    sellados = [ruta] + [f for f in [os.path.join(carpeta, "PREVISION-MANT.md")] if os.path.exists(f)] + [os.path.join(CI_D, f) for f in APARATO]
    lineas = ["# Sello de la previsión de la etapa 25 (el mantenimiento de la integración continua), %s, antes del primer push" % p["fecha"]]
    lineas += ["%s  %s" % (sha(f), os.path.relpath(f, carpeta)) for f in sellados]
    lineas.append("juez %s" % juez)
    open(os.path.join(carpeta, "SELLO-MANT.txt"), "w", encoding="utf-8").write("\n".join(lineas) + "\n")
    assert comprobar_sello(ruta, os.path.join(carpeta, "SELLO-MANT.txt"))
    print("sellado: juez %s, %d ficheros" % (juez[:12], len(sellados)))


if __name__ == "__main__":
    sellar(sys.argv[1], sys.argv[2], *(sys.argv[3:4]))
