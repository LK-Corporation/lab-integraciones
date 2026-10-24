#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CV3, regla 1 de §4.3 para Microsoft: juzga las SALIDAS ESPERADAS que el proyecto publica en sus pruebas funcionales
(`…FunctionalTests/TestData/Expected/Hl7v2/<tipo>/<muestra>-expected.json`) contra su mensaje de muestra, con el mismo juez y
la misma regla de asignación de CV2. Un mecanismo que aparece aquí es comportamiento querido y publicado: ya_declarada, con
la referencia al fichero. Compara además con lo que dio la conversión real de CV2 sobre la misma muestra.
Uso: python3 cv/cv3_esperadas_ms.py <src de Microsoft> <corpus/muestras> <juicio CV2.jsonl> <detalle.jsonl>"""
import collections
import glob
import hashlib
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import juzgar_cv2 as J  # noqa: E402
from correr_conversor import plantilla  # noqa: E402

RAIZ_ESPERADAS = "src/Microsoft.Health.Fhir.Liquid.Converter.FunctionalTests/TestData/Expected/Hl7v2"


def main(src, muestras, juicio_cv2, detalle):
    reales = {x["caso"]: x for x in map(json.loads, open(juicio_cv2, encoding="utf-8"))
              if x["conversor"] == "microsoft" and x["corpus"] == "muestras"}
    filas = []
    for f in sorted(glob.glob(os.path.join(muestras, "ms-*.hl7"))):
        caso = os.path.splitext(os.path.basename(f))[0]
        nombre = caso[3:]
        esp = glob.glob(os.path.join(src, RAIZ_ESPERADAS, "*", nombre + "-expected.json"))
        if len(esp) != 1:
            filas.append({"caso": caso, "esperada": None, "motivo": "%d ficheros esperados" % len(esp)})
            continue
        texto = open(f, encoding="utf-8").read()
        bruto = open(esp[0], "rb").read()
        e = {"punto_entrada": "oru_conv" if plantilla(texto).startswith("ORU") else "adt_conv", "mensaje": texto,
             "conversion": {"conversor": {"nombre": "microsoft-fhir-converter", "version": "v7.0 (253307f), salida esperada publicada",
                                          "huella": hashlib.sha256(bruto).hexdigest()},
                            "salida": {"estado": "bundle", "bundle": bruto.decode("utf-8-sig"), "duracion_ms": 0},
                            "perfil_valor": "guia"}}
        r = J.juzgar(e)
        cuentan = [h for h in r["hallazgos"] if h["cuenta"]]
        fila = {"caso": caso, "esperada": os.path.relpath(esp[0], src).replace(os.sep, "/"), "categoria": r["veredicto"]["categoria"],
                "cuentan": [{"hecho": h["hecho"], "clase": h["clase"], "subtipo": h["subtipo"], "que": h["que"],
                             "mc": sorted({J.asignar(h, q) for q in h["que"]})} for h in cuentan]}
        real = reales.get(caso)
        if real:
            a = sorted((h["hecho"], h["subtipo"]) for h in fila["cuentan"])
            b = sorted((h["hecho"], h["subtipo"]) for h in real["cuentan"])
            fila["igual_que_la_conversion_real"] = a == b and fila["categoria"] == real["categoria"]
        filas.append(fila)
    with open(detalle, "w", encoding="utf-8") as g:
        for x in filas:
            g.write(json.dumps(x, ensure_ascii=False) + "\n")
    cats = collections.Counter(x.get("categoria") for x in filas)
    mc = collections.Counter(m for x in filas for h in x.get("cuentan", []) for m in h["mc"])
    print("muestras ms: %d; con salida esperada: %d" % (len(filas), sum(1 for x in filas if x.get("esperada"))))
    print("categorias:", dict(cats))
    print("igual que la conversion real de CV2:", collections.Counter(x.get("igual_que_la_conversion_real") for x in filas))
    for m, n in sorted(mc.items(), key=lambda t: -t[1]):
        print("  %4d  %s" % (n, m))


if __name__ == "__main__":
    main(*sys.argv[1:5])
