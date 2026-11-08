#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 40 (pd/diseno-pd-fable.md §5): la previsión del rejuicio, contada sobre la línea base del juez de antes y los mensajes de
las evidencias, sin correr el juez nuevo.

  python3 pd/prever_pd.py <linea_base.jsonl> <clases de antes.json> <salida.json>

Cuenta, por punto, carpeta y conversor, las evidencias con PD1 y con PD1-7 valorado (su primer componente), y de la línea base lo
que marcarán las pasadas del control: los ADT con un recurso_sin_mapa (ACC-inventada) y con la nota fuera_proyeccion (la Observation
de un OBX en su sitio: OBX-fuera-de-sitio), sin PD1-7. Lo previsto: con PD1-7 valorado en ningún ADT, el paso nuevo del
emparejamiento y el juicio nuevo no se dan, y el rejuicio da 0 diferencias."""
import collections
import hashlib
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PRIVADO = os.path.normpath(os.path.join(AQUI, "..", "..", "privado"))
CONVERSORES = ("microsoft", "linuxforhealth", "juguete", "ejemplo", "propio")


def _segs(m):
    return [s for s in re.split(r"\r\n|\r|\n", m or "") if s]


def pd17(m):
    """(hay PD1, primer componente de PD1-7) del mensaje crudo."""
    s = _segs(m)
    if not s or not s[0].startswith("MSH") or len(s[0]) < 8:
        return False, ""
    f = s[0][3]
    enc = s[0].split(f)[1]
    cs, rs = enc[0], (enc[1] if len(enc) > 1 else "~")
    pd1 = [x.split(f) for x in s if x.split(f)[0] == "PD1"]
    if not pd1:
        return False, ""
    p = pd1[0]
    v = p[7] if len(p) > 7 else ""
    return True, v.split(rs)[0].split(cs)[0]


def main(base, clases, salida):
    h = hashlib.sha256()
    por = collections.Counter()
    tot = collections.Counter()
    for linea in open(base, "rb"):
        h.update(linea)
        x = json.loads(linea)
        ruta = x["evidencia"] if x["evidencia"].startswith("/") else os.path.join(PRIVADO, x["evidencia"])
        m = json.load(open(ruta, encoding="utf-8")).get("mensaje") or ""
        hay, v = pd17(m)
        g = json.loads(x["guardado"])
        ev = x["evidencia"].replace(os.sep, "/")
        conv = next((p for p in CONVERSORES if p in ev.split("/")), "?")
        carpeta = "/".join(ev.split("/")[:2])
        tot[("evidencias", x["punto"])] += 1
        if hay:
            tot[("con_PD1", x["punto"])] += 1
            por[("con_PD1", x["punto"], carpeta, conv)] += 1
        if v:
            tot[("PD1_7_valorado", x["punto"])] += 1
            por[("PD1_7_valorado", x["punto"], carpeta, conv)] += 1
        if x["punto"] == "adt_conv" and not v:
            if any(hh["subtipo"] == "recurso_sin_mapa" for hh in g["hallazgos"]):
                tot[("control_ACC-inventada", "adt_conv")] += 1
            if any(hh["subtipo"] == "fuera_proyeccion" for hh in g["hallazgos"]):
                tot[("control_OBX-fuera-de-sitio", "adt_conv")] += 1
    cuenta = collections.defaultdict(dict)
    for (k, p), n in sorted(tot.items()):
        cuenta[k][p] = n
    cl = json.load(open(clases, encoding="utf-8"))
    n_ev = sum(cuenta["evidencias"].values())
    n_v = sum(cuenta.get("PD1_7_valorado", {}).values())
    n_v_adt = cuenta.get("PD1_7_valorado", {}).get("adt_conv", 0)
    res = {
        "etapa": 40,
        "linea_base": {"fichero": os.path.basename(base), "sha256": h.hexdigest(), "evidencias": n_ev},
        "conteo": dict(cuenta),
        "detalle": [{"que": k[0], "punto": k[1], "carpeta": k[2], "conversor": k[3], "evidencias": n} for k, n in sorted(por.items())],
        "prevision": {
            "rejuicio": {"diferencias": 0 if n_v_adt == 0 else None, "pd17": 0 if n_v_adt == 0 else None, "fuera": 0, "faltan": 0,
                         "punto_cambia": 0,
                         "por_que": "Ninguna evidencia de adt_conv lleva PD1-7 valorado (%d en adt_conv, %d en total): el paso nuevo del "
                                    "emparejamiento y el juicio nuevo solo se dan con él, y nada más cambia en el camino de una Observation "
                                    "sin él. ORU, VXU y MDM no se tocan." % (n_v_adt, n_v)},
            "control": {"todas_fuera": True,
                        "con_defecto": {"PD1-7-ausente": "más de 0 y como mucho %d (los ADT que llegan al juicio)" % cuenta["evidencias"].get("adt_conv", 0),
                                        "ACC-inventada": cuenta.get("control_ACC-inventada", {}).get("adt_conv", 0),
                                        "OBX-fuera-de-sitio": cuenta.get("control_OBX-fuera-de-sitio", {}).get("adt_conv", 0),
                                        "PD1-7-valor-ajeno": "como mucho %d (los ADT con PD1); con 0, se declara" % cuenta.get("con_PD1", {}).get("adt_conv", 0),
                                        "PID-5": "más de 0", "PID-8": "más de 0"}},
            "clases": {"iguales_caso_a_caso_salvo_la_huella_del_juez": True, "frase_antes": cl.get("frase"), "n_sin_clase_antes": cl.get("n_sin_clase"),
                       "juez_antes": cl.get("juez")},
            "bases": {"demostracion": "en las tres cambia solo creada_de.juez.huella; ningún caso; las dos corridas de cada una, iguales byte a byte",
                      "juguete_positivo_casos": 344,
                      "ejemplo": "en las dos cambia solo la huella del juez; ningún caso"},
        },
    }
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({"evidencias": n_ev, "conteo": res["conteo"], "rejuicio": res["prevision"]["rejuicio"]["diferencias"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
