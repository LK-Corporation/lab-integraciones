#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 25 (cv/ci/diseno-mant-fable.md §4, S-MANT-7): lee por la API las anotaciones de cada job de unas corridas de GitHub
Actions y dice cuáles llevan el aviso de que una acción corre en Node.js 20. Su control negativo es una corrida que tiene que
llevarlo: si el control no lo lleva, el patrón ya no casa con el texto de GitHub y la orden falla. Los jobs admitidos (los que
llaman a un flujo viejo a propósito) se dan como <run_id>:<job>, valen solo para esa corrida y tienen que llevar el aviso: son
un segundo control, del mismo momento. Sin medida no hay «sin aviso»: ninguna corrida, una sin acabar o un job que no acabó en
success ni en failure (saltado, cancelado…) hacen fallar la orden (DV-MANT-6). Escribe AVISOS-MANT.json.
  python3 cv/ci/anotaciones_ci.py <run_id>[,<run_id>…] -o <json> [--admitir "<run_id>:<job>"]… [--control <run_id>]"""
import argparse
import json
import re
import subprocess
import sys

REPO = "LK-Corporation/lab-integraciones"
PATRON = re.compile(r"Node\.js 20|node20", re.I)
MEDIDOS = ("success", "failure")   # un job que corrió sus pasos; «failure» vale porque el rojo falla a propósito


def avisos_de(anotaciones):
    """-> los mensajes de las anotaciones que avisan de Node.js 20 (sin red; P-CI-30)."""
    return [("%s %s" % (a.get("title") or "", a.get("message") or "")).strip() for a in anotaciones
            if PATRON.search(a.get("message") or "") or PATRON.search(a.get("title") or "")]


def motivos(corridas, admitidos, control):
    """-> por qué la medida no vale o el aviso sigue donde no debe; vacía si todo cuadra (sin red; P-CI-30)."""
    m = []
    if not (control or {}).get("jobs_con_aviso"):
        m.append("el control no lleva el aviso")
    if not corridas:
        m.append("ninguna corrida")
    vistos = set()
    for rid, c in corridas.items():
        if c.get("estado") != "completed":
            m.append("%s: la corrida no ha acabado (%s)" % (rid, c.get("estado")))
        if not c["jobs"]:
            m.append("%s: sin jobs" % rid)
        for nombre in c.get("repetidos") or []:
            m.append("%s:%s: nombre de job repetido" % (rid, nombre))
        for nombre, j in c["jobs"].items():
            clave = "%s:%s" % (rid, nombre)
            vistos.add(clave)
            if j.get("conclusion") not in MEDIDOS:
                m.append("%s: %s, sin medida" % (clave, j.get("conclusion")))
            elif j["aviso_node20"] and clave not in admitidos:
                m.append("%s: lleva el aviso" % clave)
            elif not j["aviso_node20"] and clave in admitidos:
                m.append("%s: admitido y sin el aviso" % clave)
    m += ["%s: admitido y no está en las corridas" % a for a in admitidos if a not in vistos]
    return m


def veredicto(corridas, admitidos, control):
    """1 si hay algún motivo; 0 si no (sin red; P-CI-30)."""
    return 1 if motivos(corridas, admitidos, control) else 0


def gh(*a):
    return subprocess.run(["gh"] + list(a), capture_output=True, text=True, check=True, timeout=300).stdout


def anotaciones_de(job_id, llamar=None):
    """-> todas las anotaciones de un job, página a página (gh api devuelve 30 por omisión)."""
    salida = (llamar or gh)("api", "--paginate", "repos/%s/check-runs/%s/annotations?per_page=100" % (REPO, job_id), "--jq", ".[] | @json")
    return [json.loads(linea) for linea in salida.splitlines() if linea.strip()]


def leer_corrida(run_id):
    r = json.loads(gh("run", "view", str(run_id), "--repo", REPO, "--json", "databaseId,headSha,workflowName,status,conclusion,jobs"))
    jobs, repetidos = {}, []
    for j in r["jobs"]:
        if j["name"] in jobs:
            repetidos.append(j["name"])
        anot = anotaciones_de(j["databaseId"])
        av = avisos_de(anot)
        jobs[j["name"]] = {"conclusion": j.get("conclusion"), "anotaciones": len(anot), "node20": [m[:300] for m in av], "aviso_node20": bool(av)}
    return {"commit": r["headSha"], "flujo": r["workflowName"], "estado": r.get("status"), "conclusion": r.get("conclusion"),
            "repetidos": repetidos, "jobs": jobs}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="anotaciones_ci", description="El aviso de Node.js 20 en las anotaciones de unas corridas (etapa 25).")
    ap.add_argument("corridas")
    ap.add_argument("-o", dest="salida", required=True)
    ap.add_argument("--admitir", action="append", default=[], help="<run_id>:<job>")
    ap.add_argument("--control")
    a = ap.parse_args(argv)
    corridas = {rid: leer_corrida(rid) for rid in a.corridas.split(",") if rid}
    control = None
    if a.control:
        c = leer_corrida(a.control)
        control = {"run_id": int(a.control), "jobs": sorted(c["jobs"]), "jobs_con_aviso": sorted(n for n, j in c["jobs"].items() if j["aviso_node20"]),
                   "mensaje": next((j["node20"][0] for j in c["jobs"].values() if j["node20"]), "")[:300]}
    m = motivos(corridas, a.admitir, control)
    json.dump({"formato": "avisos-ci/2", "patron": PATRON.pattern, "admitidos": a.admitir, "control": control, "corridas": corridas,
               "motivos": m, "veredicto": "mal" if m else "bien"}, open(a.salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for rid, c in corridas.items():
        for n, j in c["jobs"].items():
            adm = " (admitido)" if "%s:%s" % (rid, n) in a.admitir else ""
            print("  %s %-12s %-28s %s" % (rid, c["flujo"], n, "%s, sin medida" % j.get("conclusion") if j.get("conclusion") not in MEDIDOS else
                                          ("AVISO" if j["aviso_node20"] else "sin aviso") + adm))
    for x in m:
        print("  motivo: %s" % x)
    print("anotaciones_ci: %s; control %s" % ("MAL" if m else "BIEN", control and ("con aviso en %d jobs" % len(control["jobs_con_aviso"]))))
    return 1 if m else 0


if __name__ == "__main__":
    sys.exit(main())
