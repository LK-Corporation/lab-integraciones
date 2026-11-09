#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 41: las bases de la integración continua, rehechas con el juez nuevo, frente a lo sellado (po/PREVISION-PO.json, bases):
en cada una cambia solo la huella del juez, a la del juez publicado de esta etapa, y ningún caso.

Cada base, la de antes (la del commit) frente a la de después (la del árbol de trabajo):
- fuera de los casos, solo puede cambiar la huella del juez (creada_de.juez.huella), y tiene que cambiar a HUELLA_PUB;
- los casos son los mismos, y no cambia ninguno.
Control negativo (sin ficheros): sobre una copia en memoria de cada base de después se siembran cuatro defectos (un caso que cambia,
la huella del corpus que cambia, la huella del juez que no cambia y la huella del juez que es otra que la publicada), y cada uno
tiene que hacer caer la comprobación de esa base. Si no cae alguno, el control no vale y la salida lo dice.

  cd fase12 && python3 po/comprobar_bases_po.py <salida.json> --huella <la del juez publicado> [--ejemplo <clon público>] [--antes <commit>]
Es pd/comprobar_bases_pd.py con la huella publicada por argumento (la de la 40 está sellada con la suya).
Sin --ejemplo, las tres de la demostración (cv/ci/LINEA-BASE-*.json de fase12). Con él, las dos del proyecto de ejemplo del clon
(ejemplo-ci/ci/LINEA-BASE*.json). La base de antes es la de --antes (por omisión, HEAD). Sale con 0 si todo cuadra y el control
vale."""
import copy
import json
import os
import subprocess
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUELLA_PUB = None                                   # por argumento (--huella)
DEMO = {"LINEA-BASE-juguete.json": "cv/ci/LINEA-BASE-juguete.json",
        "LINEA-BASE-linuxforhealth.json": "cv/ci/LINEA-BASE-linuxforhealth.json",
        "LINEA-BASE-linuxforhealth-mensaje.json": "cv/ci/LINEA-BASE-linuxforhealth-mensaje.json"}
EJEMPLO = {"ejemplo-ci/ci/LINEA-BASE.json": "ejemplo-ci/ci/LINEA-BASE.json",
           "ejemplo-ci/ci/LINEA-BASE-propio.json": "ejemplo-ci/ci/LINEA-BASE-propio.json"}


def diferencias(x, y, ruta=""):
    if isinstance(x, dict) and isinstance(y, dict):
        out = []
        for k in sorted(set(x) | set(y)):
            out += diferencias(x.get(k), y.get(k), ruta + "." + k)
        return out
    return [ruta] if x != y else []


def comprobar(antes, despues):
    """Lista de fallos (vacía si cuadra)."""
    fallos = []
    resto_a = {k: v for k, v in antes.items() if k != "casos"}
    resto_d = {k: v for k, v in despues.items() if k != "casos"}
    fuera = [r for r in diferencias(resto_a, resto_d) if r != ".creada_de.juez.huella"]
    if fuera:
        fallos.append("cambia fuera de los casos: %s" % ", ".join(fuera))
    if antes["creada_de"]["juez"]["huella"] == despues["creada_de"]["juez"]["huella"]:
        fallos.append("la huella del juez no cambia")
    if despues["creada_de"]["juez"]["huella"] != HUELLA_PUB:
        fallos.append("la huella del juez no es la del juez publicado de esta etapa: %s" % despues["creada_de"]["juez"]["huella"][:16])
    ca, cd = antes["casos"], despues["casos"]
    if set(ca) != set(cd):
        fallos.append("casos distintos: faltan %s, sobran %s" % (sorted(set(ca) - set(cd))[:5], sorted(set(cd) - set(ca))[:5]))
    for k in sorted(k for k in set(ca) & set(cd) if ca[k] != cd[k]):
        fallos.append("%s cambia y no estaba previsto: %s -> %s" % (k, json.dumps(ca[k])[:160], json.dumps(cd[k])[:160]))
    return fallos


def sembrar(antes, despues):
    """Los cuatro defectos del control, cada uno sobre su propia copia de la base de después."""
    out = []
    k = sorted(despues["casos"])[0]
    d = copy.deepcopy(despues)
    d["casos"][k]["categoria"] = "indeterminado" if d["casos"][k]["categoria"] != "indeterminado" else "correcto"
    out.append(("un caso cambia (%s)" % k, d))
    d = copy.deepcopy(despues)
    d["corpus"]["huella"] = "0" * 64
    out.append(("la huella del corpus cambia", d))
    d = copy.deepcopy(despues)
    d["creada_de"]["juez"]["huella"] = antes["creada_de"]["juez"]["huella"]
    out.append(("la huella del juez no cambia", d))
    d = copy.deepcopy(despues)
    d["creada_de"]["juez"]["huella"] = "f" * 64
    out.append(("la huella del juez es otra que la publicada", d))
    return out


def main(salida, *resto):
    global HUELLA_PUB
    resto = list(resto)
    i = resto.index("--huella")
    HUELLA_PUB = resto[i + 1]
    del resto[i:i + 2]
    assert len(HUELLA_PUB) == 64, "la huella, entera"
    ref = "HEAD"
    if "--antes" in resto:
        i = resto.index("--antes")
        ref = resto[i + 1]
        del resto[i:i + 2]
    if resto[:1] == ["--ejemplo"]:
        raiz, bases = resto[1], EJEMPLO
    else:
        raiz, bases = FASE, DEMO
    res, bien = {"bases": {}, "control": {}, "antes": ref, "huella_publicada": HUELLA_PUB}, True
    for nombre, rel in bases.items():
        antes = json.loads(subprocess.run(["git", "show", ref + ":" + rel], cwd=raiz, capture_output=True, check=True).stdout)
        despues = json.load(open(os.path.join(raiz, rel), encoding="utf-8"))
        fallos = comprobar(antes, despues)
        res["bases"][nombre] = {"cuadra": not fallos, "fallos": fallos, "casos": len(despues["casos"]),
                                "juez": [antes["creada_de"]["juez"]["huella"][:16], despues["creada_de"]["juez"]["huella"][:16]]}
        bien &= not fallos
        ctl = {}
        for que, d in sembrar(antes, despues):
            ctl[que] = "cae" if comprobar(antes, d) else "NO CAE"
        res["control"][nombre] = ctl
        bien &= all(v == "cae" for v in ctl.values())
    res["resultado"] = "CUADRA" if bien else "NO CUADRA"
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps(res, ensure_ascii=False, indent=1, sort_keys=True))
    return 0 if bien else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
