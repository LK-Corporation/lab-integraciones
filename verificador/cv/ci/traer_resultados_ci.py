#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 23 (cv/ci/diseno-ci-fable.md, pasos 8-10): trae de GitHub Actions lo que dio una corrida de demo-ci.yml y lo deja en
un JSON sin rutas ni fechas de máquina: los jobs con su conclusión y sus minutos, y de cada artefacto `verificador-*` su
VEREDICTO-CI.json (resultado, cuentas, identidades), y si su INFORME.json es igual byte a byte al de la corrida del laboratorio
de la que salió la base (con --laboratorio, la carpeta de trabajo de hacer_bases.py; solo se anota el sí o el no).
Etapa 24 (cv/ci/diseno-ci2-fable.md §7): los artefactos de los jobs de comprobación llevan su COMPROBACION-*.json. Etapa 25
(cv/ci/diseno-mant-fable.md §4): con --igual-a <referencia>, todo artefacto que esté en la referencia lleva `igual_a_la_referencia`
(su INFORME.json por huella, o sus COMPROBACION-* como objetos) y la orden sale con 1 si alguno es falso; uno que no está se anota
(`sin_referencia`) y no decide.
  python3 cv/ci/traer_resultados_ci.py <run_id> <carpeta de trabajo vacía> -o cv/ci/CORRIDA-CI-<n>.json [--laboratorio <dir>] [--mensaje]
          [--igual-a cv/ci/CORRIDA-CI-1.json]"""
import datetime
import hashlib
import json
import os
import subprocess
import sys

REPO = "LK-Corporation/lab-integraciones"
CI_D = os.path.dirname(os.path.abspath(__file__))


def gh(*a):
    return subprocess.run(["gh"] + list(a) + ["--repo", REPO], capture_output=True, text=True, check=True, timeout=600).stdout


def minutos(a, b):
    if not a or not b:
        return None
    f = lambda s: datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
    return round((f(b) - f(a)).total_seconds() / 60, 1)


LABORATORIO = {"negativo": "juguete-1", "positivo": "juguete-sembrado", "real": "linuxforhealth-1"}   # las corridas de hacer_bases.py


def main(run_id, trabajo, salida, laboratorio=None, igual_a=None):
    os.makedirs(trabajo, exist_ok=False)
    run = json.loads(gh("run", "view", run_id, "--json", "databaseId,number,headSha,event,status,conclusion,createdAt,startedAt,updatedAt,jobs,url"))
    r = {"formato": "corrida-ci/1", "run_id": run["databaseId"], "numero": run["number"], "url": run["url"],
         "commit": run["headSha"], "evento": run["event"], "estado": run["status"], "conclusion": run["conclusion"],
         "minutos_de_la_corrida": minutos(run["startedAt"], run["updatedAt"]), "jobs": {}, "artefactos": {}}
    for j in run["jobs"]:
        r["jobs"][j["name"]] = {"conclusion": j["conclusion"], "minutos": minutos(j.get("startedAt"), j.get("completedAt")),
                                "pasos_fallidos": [s["name"] for s in j.get("steps", []) if s.get("conclusion") == "failure"]}
    subprocess.run(["gh", "run", "download", run_id, "--repo", REPO, "-D", trabajo], check=False, timeout=600)
    for nombre in sorted(os.listdir(trabajo)):
        v = os.path.join(trabajo, nombre, "corrida", "VEREDICTO-CI.json")     # upload-artifact quita el prefijo común, «trabajo/»
        if not os.path.exists(v):
            r["artefactos"][nombre] = {"sin_veredicto": True, "ficheros": sorted(os.listdir(os.path.join(trabajo, nombre)))}
            for f in r["artefactos"][nombre]["ficheros"]:
                if f.startswith("COMPROBACION-") and f.endswith(".json"):
                    r["artefactos"][nombre][f[:-5]] = json.load(open(os.path.join(trabajo, nombre, f), encoding="utf-8"))
            continue
        d = json.load(open(v, encoding="utf-8"))
        r["artefactos"][nombre] = {k: d.get(k) for k in ("esperado", "resultado", "pasa", "motivos", "nuevos_distintos", "identidades", "n", "avisos")}
        r["artefactos"][nombre].update({k: len(d.get(k) or []) for k in ("nuevos", "arreglos", "casos_nuevos", "casos_ausentes",
                                                                         "salida_perdida", "indeterminado_nuevo", "notas")})
        r["artefactos"][nombre]["casos_con_nuevos"] = len({x["caso"] for x in d.get("nuevos") or []})
        inf = os.path.join(trabajo, nombre, "corrida", "INFORME.json")
        if os.path.exists(inf):
            i = json.load(open(inf, encoding="utf-8"))
            r["artefactos"][nombre]["por_corpus"] = i.get("por_corpus")
            r["artefactos"][nombre]["informe_sha256"] = hashlib.sha256(open(inf, "rb").read()).hexdigest()
            control = nombre.rsplit("-", 1)[0].replace("verificador-", "")
            if control in LABORATORIO and laboratorio:
                lab = os.path.join(laboratorio, LABORATORIO[control], "INFORME.json")
                r["artefactos"][nombre]["igual_byte_a_byte_al_laboratorio"] = open(inf, "rb").read() == open(lab, "rb").read()
    distintos = []
    if igual_a:
        ref = json.load(open(igual_a, encoding="utf-8"))["artefactos"]
        r["referencia"] = os.path.basename(igual_a)
        for nombre, x in r["artefactos"].items():
            de_ref = ref.get(nombre.rsplit("-", 1)[0] + "-1")                # el mismo artefacto, en el primer intento de la referencia
            if de_ref is None:
                x["sin_referencia"] = True                                  # se anota y no decide
                continue
            if "informe_sha256" in x:                                       # etapa 25: todo artefacto con informe, no solo los verificador-*
                x["igual_a_la_referencia"] = x["informe_sha256"] == de_ref.get("informe_sha256")
            else:                                                           # los de comprobación: sus COMPROBACION-* como objetos
                claves = [k for k in x if k.startswith("COMPROBACION-")]
                x["igual_a_la_referencia"] = bool(claves) and all(x[k] == de_ref.get(k) for k in claves)
            if not x["igual_a_la_referencia"]:
                distintos.append(nombre)
    json.dump(r, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"conclusion": r["conclusion"], "jobs": {k: (v["conclusion"], v["minutos"]) for k, v in r["jobs"].items()},
                      "artefactos": {k: (v.get("resultado"), v.get("nuevos"), v.get("arreglos"), v.get("igual_a_la_referencia"))
                                     for k, v in r["artefactos"].items()}}, ensure_ascii=False, indent=1))
    if distintos:
        print("traer_resultados_ci: distintos de la referencia: %s" % ", ".join(distintos))
        return 1
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--mensaje" in a:                                    # la corrida a mano con modo_real=mensaje
        LABORATORIO["real"] = "linuxforhealth-mensaje-1"
    sys.exit(main(a[0], a[1], a[a.index("-o") + 1], a[a.index("--laboratorio") + 1] if "--laboratorio" in a else None,
                  a[a.index("--igual-a") + 1] if "--igual-a" in a else None))
