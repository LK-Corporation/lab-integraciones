#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 39 (ANTES-ETAPA-SINCLASE.md, «Qué se mide»): lo que queda sin clase con el juez y el aparato de hoy, en cada corpus que
clasifica cv/cv3_clases.py. No toca el juez ni el aparato: los usa sobre copias en una carpeta temporal.
- Cada árbol de la etapa 33 (la versión 1 y la 2 del corpus, como los ensambla cv/ar/arrastre.py): con el juicio que guarda el
  árbol (el juez de su día) y con uno nuevo, de cv/juzgar_cv2.py con el juez de hoy; las clases, con cv/ar/arrastre.juzgar_arbol.
- El estudio (las evidencias de cv2): con un juicio nuevo, y cv/cv3_clases.py con cv/RESULTADO-CV3-minimos.json.
De cada uno: lo sin clase (conversor | mecanismo | firma: n) y la frase.
  cd fase12 && python3 sc/medir_sinclase_sc.py <salida.json> <árbol v1> <árbol v2> <evidencias del estudio>"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CVD = os.path.join(FASE, "cv")
sys.path[:0] = [FASE, CVD, os.path.join(CVD, "ar")]


def juzgar(evidencias, juicio):
    subprocess.run([sys.executable, os.path.join(CVD, "juzgar_cv2.py"), evidencias, juicio, juicio + ".agregados.json"],
                   check=True, capture_output=True)


def resumen(cl):
    f = cl.get("frase") or {}
    return {"sin_clase": cl.get("sin_clase") or {}, "n_sin_clase": sum((cl.get("sin_clase") or {}).values()),
            "frase": {k: f.get(k) for k in ("N_nuevas_confirmadas", "D_ya_declaradas", "C_convenciones", "M_mensajes")},
            "juez": cl.get("juez")}


def main(salida, arbol1, arbol2, ev_estudio):
    import arrastre as AR
    tmp = tempfile.mkdtemp(prefix="sc39-")
    res = {}
    try:
        for nombre, arbol in (("ga-v1", arbol1), ("ga-v2", arbol2)):
            d = os.path.join(tmp, nombre)
            shutil.copytree(arbol, d)
            cl, _ = AR.juzgar_arbol(d)
            antes = resumen(cl)
            juzgar(os.path.join(d, "evidencias"), os.path.join(d, "juicio.jsonl"))
            cl, _ = AR.juzgar_arbol(d)
            res[nombre] = {"con_el_juicio_guardado": antes, "con_el_juez_de_hoy": resumen(cl)}
        j = os.path.join(tmp, "estudio.jsonl")
        juzgar(ev_estudio, j)
        argv = sys.argv
        try:
            import cv3_clases as C
            C.main(j, os.path.join(CVD, "RESULTADO-CV3-minimos.json"), ev_estudio, os.path.join(tmp, "estudio.json"))
        finally:
            sys.argv = argv
        res["estudio"] = {"con_el_juez_de_hoy": resumen(json.load(open(os.path.join(tmp, "estudio.json"), encoding="utf-8")))}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    res["total_hoy"] = sum(v["con_el_juez_de_hoy"]["n_sin_clase"] for v in res.values() if isinstance(v, dict))
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps(res, ensure_ascii=False, indent=1, sort_keys=True))


if __name__ == "__main__":
    main(*sys.argv[1:])
