#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 41 (po/diseno-po-fable.md §5): la previsión del rejuicio, contada sobre la línea base del juez de antes y los mensajes de
las evidencias, sin correr el juez nuevo.

  python3 po/prever_po.py <linea_base.jsonl> <clases de antes.json> <salida.json>

Cuenta, por punto, las evidencias con PD1 y con PD1-7 valorado (pd/prever_pd.py, sin tocarlo), y lo que marcarán las pasadas del
control: los ORU con OBX dentro de ORDER_OBSERVATION (cota de «la Observation de un OBX, fuera de su sitio»), los ORU sin PD1-7 con la
nota fuera_proyeccion en la línea base («una sobrante de L-CV-7, dada por inventada») y los ORU con PD1 (cota de «otro valor»). Lo
previsto: con PD1-7 valorado en ningún ORU, el paso nuevo del emparejamiento y el juicio nuevo no se dan, en ADT el código es el mismo,
y el rejuicio da 0 diferencias."""
import collections
import hashlib
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), "pd"))
import prever_pd as PP                                    # noqa: E402  (pd17 y PRIVADO; no se toca)


def obx_en_obr(m):
    """Si el mensaje trae algún OBX dentro de un ORDER_OBSERVATION (tras un OBR y antes de un SPM)."""
    segs = [s for s in re.split(r"\r\n|\r|\n", m or "") if s]
    if not segs or not segs[0].startswith("MSH") or len(segs[0]) < 8:
        return False
    f, ctx = segs[0][3], None
    for s in segs:
        n = s.split(f)[0]
        if n == "OBR":
            ctx = "obr"
        elif n == "SPM":
            ctx = "spm"
        elif n == "OBX" and ctx == "obr":
            return True
    return False


def main(base, clases, salida):
    h = hashlib.sha256()
    tot = collections.Counter()
    for linea in open(base, "rb"):
        h.update(linea)
        x = json.loads(linea)
        ruta = x["evidencia"] if x["evidencia"].startswith("/") else os.path.join(PP.PRIVADO, x["evidencia"])
        m = json.load(open(ruta, encoding="utf-8")).get("mensaje") or ""
        hay, v = PP.pd17(m)
        g = json.loads(x["guardado"])
        p = x["punto"]
        tot[("evidencias", p)] += 1
        if hay:
            tot[("con_PD1", p)] += 1
        if v:
            tot[("PD1_7_valorado", p)] += 1
        if p == "oru_conv" and not v:
            if obx_en_obr(m):
                tot[("control_ORU-OBX-fuera-de-sitio_cota", p)] += 1
            if any(hh["subtipo"] == "fuera_proyeccion" for hh in g["hallazgos"]):
                tot[("control_ORU-L-CV-7-inventada", p)] += 1
    cuenta = collections.defaultdict(dict)
    for (k, p), n in sorted(tot.items()):
        cuenta[k][p] = n
    cl = json.load(open(clases, encoding="utf-8"))
    n_v_oru = cuenta.get("PD1_7_valorado", {}).get("oru_conv", 0)
    n_v = sum(cuenta.get("PD1_7_valorado", {}).values())
    oru = cuenta["evidencias"].get("oru_conv", 0)
    res = {
        "etapa": 41,
        "linea_base": {"fichero": os.path.basename(base), "sha256": h.hexdigest(), "evidencias": sum(cuenta["evidencias"].values())},
        "conteo": dict(cuenta),
        "prevision": {
            "rejuicio": {"diferencias": 0 if n_v == 0 else None, "pd17oru": 0 if n_v_oru == 0 else None, "fuera": 0, "faltan": 0,
                         "punto_cambia": 0,
                         "por_que": "Ninguna evidencia lleva PD1-7 valorado (%d en oru_conv, %d en total): el paso nuevo del emparejamiento "
                                    "de ORU y el juicio nuevo solo se dan con él; en ADT el código es el mismo, movido a dos ayudantes "
                                    "y llamado en el mismo punto, con las mismas citas." % (n_v_oru, n_v)},
            "control": {"todas_fuera": True,
                        "con_defecto": {"ORU-PD1-7-ausente": "más de 0 y como mucho %d (los ORU que llegan al juicio)" % oru,
                                        "ORU-PD1-7-valor-ajeno": "como mucho %d (los ORU con PD1)" % cuenta.get("con_PD1", {}).get("oru_conv", 0),
                                        "ORU-OBX-fuera-de-sitio": "más de 0 y como mucho %d (los ORU con un OBX en ORDER_OBSERVATION)" %
                                                                  cuenta.get("control_ORU-OBX-fuera-de-sitio_cota", {}).get("oru_conv", 0),
                                        "ORU-L-CV-7-inventada": cuenta.get("control_ORU-L-CV-7-inventada", {}).get("oru_conv", 0),
                                        "OBX-5": "más de 0", "PID-5": 23765, "ADT-PD1-7-ausente": 15979}},
            "clases": {"iguales_caso_a_caso_salvo_la_huella_del_juez": True, "frase_antes": cl.get("frase"), "n_sin_clase_antes": cl.get("n_sin_clase"),
                       "juez_antes": cl.get("juez")},
            "bases": {"demostracion": "en las tres cambia solo creada_de.juez.huella; ningún caso; las dos corridas de cada una, iguales byte a byte",
                      "juguete_positivo_casos": 344,
                      "ejemplo": "en las dos cambia solo la huella del juez; ningún caso"},
        },
    }
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({"conteo": res["conteo"], "rejuicio": res["prevision"]["rejuicio"]["diferencias"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
