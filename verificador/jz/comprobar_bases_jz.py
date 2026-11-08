#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 37: las bases de la integración continua, rehechas con el juez nuevo, frente a lo sellado (jz/PREVISION-JZ.json, bases_ci).

Cada base, la de antes (la del commit) frente a la de después (la del árbol de trabajo):
- fuera de los casos, solo puede cambiar la huella del juez (creada_de.juez.huella), y tiene que cambiar;
- los casos son los mismos, y cambian exactamente los previstos, cada uno como dice la previsión:
  - «correcto -> rechazo_incorrecto»: de categoría correcto a rechazo_incorrecto;
  - «sin el hallazgo de PID-8; subtipo X -> Y»: la misma categoría, los mismos hallazgos sin los de PID-8, y el subtipo de X a Y.
Control negativo (sin ficheros): sobre una copia en memoria de cada base de después se siembran cuatro defectos (un caso no
previsto que cambia, un caso previsto que no cambia, la huella del corpus que cambia y la del juez que no cambia), y cada uno
tiene que hacer caer la comprobación de esa base. Si no cae alguno, el control no vale y la salida lo dice.

  cd fase12 && python3 jz/comprobar_bases_jz.py <salida.json> [--ejemplo <clon público>] [--antes <commit>]
Sin --ejemplo, las tres de la demostración (cv/ci/LINEA-BASE-*.json de fase12). Con él, las dos del proyecto de ejemplo del clon
(ejemplo-ci/ci/LINEA-BASE*.json). La base de antes es la de --antes (por omisión, HEAD; una vez hecho el commit de las bases
nuevas, el commit anterior: en fase12, 387bed8). Sale con 0 si todo cuadra y el control vale."""
import copy
import json
import os
import subprocess
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO = {"LINEA-BASE-juguete.json": "cv/ci/LINEA-BASE-juguete.json",
        "LINEA-BASE-linuxforhealth.json": "cv/ci/LINEA-BASE-linuxforhealth.json",
        "LINEA-BASE-linuxforhealth-mensaje.json": "cv/ci/LINEA-BASE-linuxforhealth-mensaje.json"}
EJEMPLO = {"ejemplo-ci/ci/LINEA-BASE.json": "ejemplo-ci/ci/LINEA-BASE.json",
           "ejemplo-ci/ci/LINEA-BASE-propio.json": "ejemplo-ci/ci/LINEA-BASE-propio.json"}


def previstos(prev, nombre):
    """{caso: texto de la previsión} de esa base; la de mensaje a mensaje dice «los mismos 6» que la de lote."""
    p = prev["bases_ci"][nombre]
    casos = p.get("casos", {})
    if isinstance(casos, str):
        assert casos == "los mismos 6", casos
        casos = prev["bases_ci"]["LINEA-BASE-linuxforhealth.json"]["casos"]
    assert len(casos) == p["cambian"], (nombre, len(casos), p["cambian"])
    return casos


def diferencias(x, y, ruta=""):
    if isinstance(x, dict) and isinstance(y, dict):
        out = []
        for k in sorted(set(x) | set(y)):
            out += diferencias(x.get(k), y.get(k), ruta + "." + k)
        return out
    return [ruta] if x != y else []


def comprobar(antes, despues, casos_prev):
    """Lista de fallos (vacía si cuadra)."""
    fallos = []
    resto_a = {k: v for k, v in antes.items() if k != "casos"}
    resto_d = {k: v for k, v in despues.items() if k != "casos"}
    fuera = [r for r in diferencias(resto_a, resto_d) if r != ".creada_de.juez.huella"]
    if fuera:
        fallos.append("cambia fuera de los casos: %s" % ", ".join(fuera))
    if antes["creada_de"]["juez"]["huella"] == despues["creada_de"]["juez"]["huella"]:
        fallos.append("la huella del juez no cambia")
    ca, cd = antes["casos"], despues["casos"]
    if set(ca) != set(cd):
        fallos.append("casos distintos: faltan %s, sobran %s" % (sorted(set(ca) - set(cd))[:5], sorted(set(cd) - set(ca))[:5]))
    cambian = {k for k in set(ca) & set(cd) if ca[k] != cd[k]}
    for k in sorted(cambian - set(casos_prev)):
        fallos.append("%s cambia y no estaba previsto: %s -> %s" % (k, json.dumps(ca[k])[:160], json.dumps(cd[k])[:160]))
    for k, texto in sorted(casos_prev.items()):
        a, d = ca.get(k), cd.get(k)
        if a is None or d is None:
            fallos.append("%s: previsto y no está" % k)
            continue
        if k not in cambian:
            fallos.append("%s: previsto (%s) y no cambia" % (k, texto))
            continue
        if texto == "correcto -> rechazo_incorrecto":
            if not (a["categoria"] == "correcto" and d["categoria"] == "rechazo_incorrecto"):
                fallos.append("%s: %s -> %s, y lo previsto es %s" % (k, a["categoria"], d["categoria"], texto))
        elif texto.startswith("sin el hallazgo de PID-8; subtipo "):
            de, a_ = texto.split("subtipo ", 1)[1].split(" -> ")
            sin = [h for h in a["hallazgos"] if h[0] != "PID-8"]
            if not (len(sin) < len(a["hallazgos"]) and d["hallazgos"] == sin and d["categoria"] == a["categoria"]
                    and d.get("estado") == a.get("estado") and a["subtipo"] == de and d["subtipo"] == a_):
                fallos.append("%s: no es «%s»: %s -> %s" % (k, texto, json.dumps(a)[:200], json.dumps(d)[:200]))
        else:
            fallos.append("%s: la previsión dice «%s», que este comprobador no sabe leer" % (k, texto))
    return fallos


def sembrar(antes, despues, casos_prev):
    """Los cuatro defectos del control, cada uno sobre su propia copia de la base de después."""
    out = []
    no_previsto = next(k for k in sorted(despues["casos"]) if k not in casos_prev)
    d = copy.deepcopy(despues)
    d["casos"][no_previsto]["categoria"] = "indeterminado" if d["casos"][no_previsto]["categoria"] != "indeterminado" else "correcto"
    out.append(("un caso no previsto cambia (%s)" % no_previsto, d))
    if casos_prev:
        k = sorted(casos_prev)[0]
        d = copy.deepcopy(despues)
        d["casos"][k] = copy.deepcopy(antes["casos"][k])
        out.append(("un caso previsto no cambia (%s)" % k, d))
    d = copy.deepcopy(despues)
    d["corpus"]["huella"] = "0" * 64
    out.append(("la huella del corpus cambia", d))
    d = copy.deepcopy(despues)
    d["creada_de"]["juez"]["huella"] = antes["creada_de"]["juez"]["huella"]
    out.append(("la huella del juez no cambia", d))
    return out


def main(salida, *resto):
    prev = json.load(open(os.path.join(FASE, "jz", "PREVISION-JZ.json"), encoding="utf-8"))
    resto = list(resto)
    ref = "HEAD"
    if "--antes" in resto:
        i = resto.index("--antes")
        ref = resto[i + 1]
        del resto[i:i + 2]
    if resto[:1] == ["--ejemplo"]:
        raiz, bases = resto[1], EJEMPLO
    else:
        raiz, bases = FASE, DEMO
    res, bien = {"bases": {}, "control": {}, "antes": ref}, True
    for nombre, rel in bases.items():
        antes = json.loads(subprocess.run(["git", "show", ref + ":" + rel], cwd=raiz, capture_output=True, check=True).stdout)
        despues = json.load(open(os.path.join(raiz, rel), encoding="utf-8"))
        casos_prev = previstos(prev, nombre)
        fallos = comprobar(antes, despues, casos_prev)
        cambian = sorted(k for k in antes["casos"] if k in despues["casos"] and antes["casos"][k] != despues["casos"][k])
        res["bases"][nombre] = {"cuadra": not fallos, "fallos": fallos, "casos": len(despues["casos"]), "cambian": cambian,
                                "juez": [antes["creada_de"]["juez"]["huella"][:16], despues["creada_de"]["juez"]["huella"][:16]]}
        bien &= not fallos
        ctl = {}
        for que, d in sembrar(antes, despues, casos_prev):
            ctl[que] = "cae" if comprobar(antes, d, casos_prev) else "NO CAE"
        res["control"][nombre] = ctl
        bien &= all(v == "cae" for v in ctl.values())
    res["resultado"] = "CUADRA" if bien else "NO CUADRA"
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps(res, ensure_ascii=False, indent=1, sort_keys=True))
    return 0 if bien else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
