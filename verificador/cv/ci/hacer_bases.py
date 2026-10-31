#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 23 (cv/ci/diseno-ci-fable.md §6, pasos 1-7): las líneas base de la demostración, desde la copia pública (el juez que
correrá el runner). Dos corridas de cada una, iguales byte a byte en INFORME.json; la base de la primera; la segunda contra ella
con «igual»; y, con el juguete, la siembra y «falla». Para en el primer paso que no cuadra.
  python3 cv/ci/hacer_bases.py <copia pública>/verificador <artefactos del estudio> <trabajo> [juguete|lote|mensaje ...]
Escribe cv/ci/LINEA-BASE-juguete.json, LINEA-BASE-linuxforhealth.json y LINEA-BASE-linuxforhealth-mensaje.json (las pedidas) y
<trabajo>/BASES-CI.json con lo comprobado."""
import io
import json
import os
import shutil
import subprocess
import sys
from contextlib import redirect_stdout

CI_D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CI_D)
import linea_base as LB  # noqa: E402

PUB, ART, TRAB = sys.argv[1:4]
QUE = sys.argv[4:] or ["juguete", "lote"]
PYTHON = sys.executable
res = json.load(open(os.path.join(TRAB, "BASES-CI.json"))) if os.path.exists(os.path.join(TRAB, "BASES-CI.json")) else {}


def parar(m):
    res["parada"] = m
    json.dump(res, open(os.path.join(TRAB, "BASES-CI.json"), "w"), ensure_ascii=False, indent=1)
    raise SystemExit("PARADA: " + m)


def correr(ad, salida, art, extra=()):
    shutil.rmtree(salida, ignore_errors=True)
    r = subprocess.run([PYTHON, "cv/verificar_conversor.py", ad, salida, "--artefactos", art, "--sin-sensibilidad"] + list(extra),
                       cwd=PUB, capture_output=True, text=True, timeout=7200)
    cr = json.load(open(os.path.join(salida, "CORRIDA.json")))
    return {"rc": r.returncode, "juez": cr["juez"]["huella"], "huella": cr["huella"], "huella_con_nombres": cr["huella_con_nombres"],
            "imagen_digest": cr["imagen_digest"], "n": cr["corpus"]["n"], "sin_evidencia": cr["sin_evidencia"], "reintentos": cr["reintentos"],
            "segundos": cr["duraciones"]["total_s"]}


def lb(*a):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = LB.main(list(a))
    return rc, buf.getvalue().strip()


def base(nombre, ad, art, n_esperado, extra=(), dos=True):
    s1, s2 = os.path.join(TRAB, nombre + "-1"), os.path.join(TRAB, nombre + "-2")
    c1 = correr(ad, s1, art, extra)
    r = {"corrida_1": c1}
    if c1["rc"] != 0 or c1["sin_evidencia"]:
        parar("%s: la corrida 1 salió con %s o con casos sin evidencia" % (nombre, c1["rc"]))
    if dos:
        c2 = correr(ad, s2, art, extra)
        r["corrida_2"] = c2
        if open(os.path.join(s1, "INFORME.json"), "rb").read() != open(os.path.join(s2, "INFORME.json"), "rb").read():
            parar("%s: INFORME.json distinto entre dos corridas" % nombre)
    destino = os.path.join(CI_D, "LINEA-BASE-%s.json" % nombre)
    rc, out = lb("crear", s1, "-o", destino)
    if rc:
        parar("%s: crear salió con %d (%s)" % (nombre, rc, out))
    d = json.load(open(destino))
    if d["n_casos"] != n_esperado:
        parar("%s: %d casos y se esperaban %d" % (nombre, d["n_casos"], n_esperado))
    if dos:
        rc, out = lb("comparar", s2, destino, "--esperar", "igual", "-o", os.path.join(TRAB, nombre + "-veredicto"))
        r["igual"] = {"rc": rc, "salida": out}
        if rc:
            parar("%s: la segunda corrida no da lo mismo que la base (%s)" % (nombre, out))
    cats = {}
    for x in d["casos"].values():
        pass
    for k, x in d["casos"].items():
        c = k.split("/")[0]
        cats.setdefault(c, {}).setdefault(x["categoria"], 0)
        cats[c][x["categoria"]] += 1
    r["categorias"] = cats
    r["n_casos"] = d["n_casos"]
    res[nombre] = r
    return s1, d


if "juguete" in QUE:
    s1, d = base("juguete", "cv/adaptadores/juguete.json", "cv", 383)          # etapa 26: 343 + las 40 de MDM
    jug = os.path.join(PUB, "cv", "conversor_juguete.py")
    original = open(jug, "rb").read()
    try:
        rc = subprocess.run([PYTHON, os.path.join(CI_D, "sembrar_juguete.py"), jug], capture_output=True, text=True).returncode
        if rc:
            parar("juguete: la siembra no aplica en la copia pública")
        s3 = os.path.join(TRAB, "juguete-sembrado")
        correr("cv/adaptadores/juguete.json", s3, "cv")
    finally:
        open(jug, "wb").write(original)
    esperado = json.dumps(json.load(open(os.path.join(CI_D, "POSITIVO-CI.json")))["hallazgo_esperado"])
    rc, out = lb("comparar", s3, os.path.join(CI_D, "LINEA-BASE-juguete.json"), "--esperar", "falla", "--hallazgo-esperado", esperado,
                 "-o", os.path.join(TRAB, "juguete-sembrado-veredicto"))
    v = json.load(open(os.path.join(TRAB, "juguete-sembrado-veredicto", "VEREDICTO-CI.json")))
    res["juguete"]["positivo"] = {"rc": rc, "nuevos": len(v["nuevos"]), "nuevos_distintos": v["nuevos_distintos"],
                                  "casos_con_el_hallazgo": len({x["caso"] for x in v["nuevos"]})}
    if rc:
        parar("juguete: el positivo sembrado no falla como se espera (%s)" % out)
    if open(jug, "rb").read() != original:
        parar("juguete: la copia pública quedó sembrada")
if "lote" in QUE:
    base("linuxforhealth", "cv/adaptadores/linuxforhealth.json", ART, 451)                         # etapa 26: 411 + 40
if "mensaje" in QUE:
    base("linuxforhealth-mensaje", "cv/adaptadores/linuxforhealth-mensaje.json", ART, 451, dos=False)   # etapa 26: 411 + 40
json.dump(res, open(os.path.join(TRAB, "BASES-CI.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: {x: v.get(x) for x in ("n_casos", "categorias", "positivo") if x in v} for k, v in res.items() if isinstance(v, dict)},
                 ensure_ascii=False, indent=1))
