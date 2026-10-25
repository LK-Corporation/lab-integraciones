#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 23 (cv/ci/diseno-ci-fable.md §8): escribe PREVISION-CI.json con el juez publicado, el conversor, la imagen y la
herramienta añadidos al cuerpo de la previsión, y SELLO-CI.txt con la huella de lo sellado (rutas relativas a su carpeta). Se
niega a pisar un sello. Después, el commit, antes del primer push (la primera corrida en GitHub Actions es posterior por
construcción). Copia adaptada de cv/ar/sellar_prevision.py.
  python3 cv/ci/sellar_prevision_ci.py <cuerpo.json> <juez publicado> [<carpeta>]"""
import datetime
import hashlib
import json
import os
import re
import sys

CI_D = os.path.dirname(os.path.abspath(__file__))
CVD = os.path.dirname(CI_D)
CLAVES_PREVISION_CI = ("etapa", "fecha", "juez", "conversor", "imagen_digest", "herramienta", "base_de_la_prevision",
                       "probabilidad_pruebas_verdes_a_la_primera", "probabilidad_negativo_a_la_primera", "probabilidad_positivo_a_la_primera",
                       "probabilidad_real_a_la_primera", "probabilidad_real_mismos_veredictos", "probabilidad_real_huella_cuadra",
                       "probabilidad_los_tres_verdes_en_una_sesion", "pushes_previstos", "minutos_por_corrida_previstos",
                       "positivo_n_casos_previsto", "causas_de_fallo_previstas", "diferencias_que_se_explicarian", "regla_de_parada", "jev")
APARATO = ["linea_base.py", "sembrar_juguete.py", "preparar_lfh.sh", "prueba_ci.py", "POSITIVO-CI.json", "github/verificador-conversor.yml",
           "github/demo-ci.yml", "LINEA-BASE-juguete.json", "LINEA-BASE-linuxforhealth.json", "LINEA-BASE-linuxforhealth-mensaje.json",
           "ensayo_flujo.py", "decision-jev-prevision-ci.md", "decision-jev-prevision-ci-2.md"]


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
    return os.path.realpath(prevision) in vistos and all(k in p for k in CLAVES_PREVISION_CI)


def sellar(cuerpo, juez, carpeta=CI_D):
    if os.path.exists(os.path.join(carpeta, "SELLO-CI.txt")):
        raise SystemExit("ya hay un SELLO-CI.txt en %s: no se pisa un sello" % carpeta)
    p = dict(json.load(open(cuerpo, encoding="utf-8")))
    aparato = [os.path.join(CI_D, f) for f in APARATO if os.path.exists(os.path.join(CI_D, f))]
    p.update({"fecha": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "juez": juez,
              "conversor": "ac41f71b98ee75bac637ecd4b68f58b463f0798bf66cfa941f4194cb2a50acf2",
              "imagen_digest": "sha256:7bb84a451705605a47d24eb844d4d9ab03e33e131a507db76aafe25db3907f64",
              "herramienta": dict([(os.path.relpath(f, CI_D), sha(f)) for f in aparato] +
                                  [("verificar_conversor.py", sha(os.path.join(CVD, "verificar_conversor.py")))])})
    faltan = [k for k in CLAVES_PREVISION_CI if k not in p]
    assert not faltan, faltan
    ruta = os.path.join(carpeta, "PREVISION-CI.json")
    open(ruta, "w", encoding="utf-8").write(json.dumps(p, ensure_ascii=False, indent=1) + "\n")
    sellados = [ruta] + [f for f in [os.path.join(carpeta, "PREVISION-CI.md")] if os.path.exists(f)] + aparato
    lineas = ["# Sello de la previsión de la etapa 23 (la integración continua), %s, antes del primer push" % p["fecha"]]
    lineas += ["%s  %s" % (sha(f), os.path.relpath(f, carpeta)) for f in sellados]
    lineas.append("juez %s" % juez)
    open(os.path.join(carpeta, "SELLO-CI.txt"), "w", encoding="utf-8").write("\n".join(lineas) + "\n")
    assert comprobar_sello(ruta, os.path.join(carpeta, "SELLO-CI.txt"))
    print("sellado: juez %s, %d ficheros" % (juez[:12], len(sellados)))


if __name__ == "__main__":
    sellar(sys.argv[1], sys.argv[2], *(sys.argv[3:4]))
