#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 24 (cv/ci/diseno-ci2-fable.md §10): escribe PREVISION-CI2.json con el juez publicado, el conversor del ejemplo, la
imagen de Python y la herramienta añadidos al cuerpo de la previsión, y SELLO-CI2.txt con la huella de lo sellado. Se niega a
pisar SELLO-CI2.txt y no toca SELLO-CI.txt (la 23). Copia adaptada de cv/ci/sellar_prevision_ci.py.
Las rutas del sello son relativas a su carpeta, salvo las del proyecto de ejemplo, que van como «@ejemplo-ci/…»: esa carpeta está
en la raíz del repositorio público y dentro del árbol del laboratorio, y raiz_ejemplo() la encuentra en los dos (DV-CI2-2).
  python3 cv/ci/sellar_prevision_ci2.py <cuerpo.json> <juez publicado> [<carpeta>]"""
import datetime
import hashlib
import json
import os
import re
import sys

CI_D = os.path.dirname(os.path.abspath(__file__))
CVD = os.path.dirname(CI_D)
ARBOL = os.path.dirname(CVD)                    # fase12/ en el laboratorio, verificador/ en el público
CLAVES_PREVISION_CI2 = ("etapa", "fecha", "juez", "conversor", "imagen_digest", "herramienta", "base_de_la_prevision",
                        "probabilidad_demo_verde_en_c1_a_la_primera", "probabilidad_demo_informes_iguales",
                        "probabilidad_ejemplo_verde_a_la_primera", "probabilidad_rojo_a_la_primera",
                        "probabilidad_salidas_de_job_fallido_llegan", "probabilidad_pull_request_verde_a_la_primera",
                        "probabilidad_todo_en_una_sesion", "pushes_previstos", "pushes_mas_probable", "minutos_por_corrida_previstos",
                        "rojo_n_casos_previsto", "causas_de_fallo_previstas", "diferencias_que_se_explicarian", "regla_de_parada", "jev")
APARATO = ["github-ci2/verificador-conversor.yml", "github-ci2/demo-ci.yml", "github-ci2/higiene.yml", "github-ci2/ejemplo-ci.yml",
           "github-ci2/rojo-ci.yml", "ACCIONES-CI.json", "prueba_ci.py", "ensayo_flujo.py", "comprobar_ejemplo.py", "comprobar_rojo.py",
           "traer_resultados_ci.py", "sellar_prevision_ci2.py", "decision-jev-prevision-ci2.md"]
EJEMPLO = ["conversor.py", "preparar.sh", "README.md", "ci/adaptador.json", "ci/DEFECTO.json", "ci/sembrar.py", "ci/hacer_base.sh",
           "ci/LINEA-BASE.json", "ci/LINEA-BASE-propio.json", "corpus/EJ-ADT-A01.hl7", "corpus/EJ-ADT-A03.hl7", "corpus/EJ-ADT-A08.hl7",
           "corpus/EJ-ORU-R01.hl7", "corpus/EJ-ORU-R01-dos.hl7", "corpus/EJ-VXU-V04.hl7"]


def raiz_ejemplo():
    pub = os.path.join(os.path.dirname(ARBOL), "ejemplo-ci")
    return pub if os.path.exists(os.path.join(pub, "conversor.py")) else os.path.join(ARBOL, "ejemplo-ci")


def sha(ruta):
    return hashlib.sha256(open(ruta, "rb").read()).hexdigest()


def resolver(base, ruta):
    return os.path.join(raiz_ejemplo(), ruta[len("@ejemplo-ci/"):]) if ruta.startswith("@ejemplo-ci/") else os.path.join(base, ruta)


def comprobar_sello(prevision, sello):
    base, vistos = os.path.dirname(os.path.abspath(sello)), set()
    try:
        for linea in open(sello, encoding="utf-8"):
            m = re.match(r"^([0-9a-f]{64})  (\S+)\s*$", linea)
            if m:
                ruta = os.path.realpath(resolver(base, m.group(2)))
                if sha(ruta) != m.group(1):
                    return False
                vistos.add(ruta)
        p = json.load(open(prevision, encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return os.path.realpath(prevision) in vistos and all(k in p for k in CLAVES_PREVISION_CI2)


def sellar(cuerpo, juez, carpeta=CI_D):
    if os.path.exists(os.path.join(carpeta, "SELLO-CI2.txt")):
        raise SystemExit("ya hay un SELLO-CI2.txt en %s: no se pisa un sello" % carpeta)
    p = dict(json.load(open(cuerpo, encoding="utf-8")))
    aparato = [f for f in APARATO if os.path.exists(os.path.join(CI_D, f))]
    ejemplo = [f for f in EJEMPLO if os.path.exists(os.path.join(raiz_ejemplo(), f))]
    faltan = sorted(set(APARATO) - set(aparato)) + ["ejemplo-ci/" + f for f in sorted(set(EJEMPLO) - set(ejemplo))]
    if faltan:
        raise SystemExit("faltan ficheros del aparato: %s" % ", ".join(faltan))
    base = json.load(open(os.path.join(raiz_ejemplo(), "ci", "LINEA-BASE.json"), encoding="utf-8"))
    ad = json.load(open(os.path.join(raiz_ejemplo(), "ci", "adaptador.json"), encoding="utf-8"))
    p.update({"fecha": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "juez": juez,
              "conversor": base["conversor"]["huella"], "imagen_digest": ad["caja"]["imagen_digest"],
              "herramienta": dict([(f, sha(os.path.join(CI_D, f))) for f in aparato] +
                                  [("@ejemplo-ci/" + f, sha(os.path.join(raiz_ejemplo(), f))) for f in ejemplo] +
                                  [("verificar_conversor.py", sha(os.path.join(CVD, "verificar_conversor.py")))])})
    faltan = [k for k in CLAVES_PREVISION_CI2 if k not in p]
    assert not faltan, faltan
    ruta = os.path.join(carpeta, "PREVISION-CI2.json")
    open(ruta, "w", encoding="utf-8").write(json.dumps(p, ensure_ascii=False, indent=1) + "\n")
    md = os.path.join(carpeta, "PREVISION-CI2.md")
    sellados = [(ruta, os.path.relpath(ruta, carpeta))] + ([(md, os.path.relpath(md, carpeta))] if os.path.exists(md) else []) \
        + [(os.path.join(CI_D, f), os.path.relpath(os.path.join(CI_D, f), carpeta)) for f in aparato] \
        + [(os.path.join(raiz_ejemplo(), f), "@ejemplo-ci/" + f) for f in ejemplo]
    lineas = ["# Sello de la previsión de la etapa 24 (lo abierto de la integración continua), %s, antes del primer push" % p["fecha"]]
    lineas += ["%s  %s" % (sha(f), r) for f, r in sellados]
    lineas.append("juez %s" % juez)
    open(os.path.join(carpeta, "SELLO-CI2.txt"), "w", encoding="utf-8").write("\n".join(lineas) + "\n")
    assert comprobar_sello(ruta, os.path.join(carpeta, "SELLO-CI2.txt"))
    print("sellado: juez %s, %d ficheros" % (juez[:12], len(sellados)))


if __name__ == "__main__":
    sellar(sys.argv[1], sys.argv[2], *(sys.argv[3:4]))
