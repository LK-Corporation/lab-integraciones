#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 20, P-VX-22 (vx/diseno-vx-fable.md §7): ADT y ORU no cambian. Juzga todas las evidencias del estudio de conversores
(privado: las de CV2 y las de los pares mínimos) con el juez de esta carpeta y escribe, por evidencia, el veredicto y todos sus
hallazgos (clase, subtipo, hecho, cuenta, que, citas, certeza). Con «comparar», exige que el juez de ahora dé exactamente lo
mismo que la línea base, byte a byte, y lista lo que difiera.

  python3 vx/rejuicio_vx.py linea_base <salida.jsonl> <carpeta de evidencias> [...]
  python3 vx/rejuicio_vx.py comparar   <linea_base.jsonl> <carpeta de evidencias> [...]
  python3 vx/rejuicio_vx.py control    <linea_base.jsonl> <carpeta de evidencias> [...]   # con un defecto inyectado: debe ver diferencias"""
import glob
import json
import os
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, FASE)
_argv, sys.argv = sys.argv, ["x", "--silencio"]
import conversion as CV  # noqa: E402
import mcp_verificador as M  # noqa: E402
import verificador as V  # noqa: E402
sys.argv = _argv

CAMPOS = ("clase", "subtipo", "hecho", "cuenta", "que", "citas", "certeza", "nivel", "estado", "causa", "alternativa")


def fila(ruta, e):
    r = V.verificar(e)
    return json.dumps({"evidencia": ruta, "veredicto": r["veredicto"],
                       "hallazgos": [{k: h.get(k) for k in CAMPOS} for h in r["hallazgos"]],
                       "recuentos": (r.get("conversion") or {}).get("recuentos")}, ensure_ascii=False, sort_keys=True)


def evidencias(carpetas):
    for c in carpetas:
        for f in sorted(glob.glob(os.path.join(c, "**", "*.json"), recursive=True)):
            e = json.load(open(f, encoding="utf-8"))
            if isinstance(e, dict) and "conversion" in e and "punto_entrada" in e:
                yield os.path.relpath(f, os.path.dirname(c.rstrip("/"))), e


def main(modo, base, *carpetas):
    if modo == "linea_base":
        n = 0
        with open(base, "w", encoding="utf-8") as g:
            for ruta, e in evidencias(carpetas):
                g.write(fila(ruta, e) + "\n")
                n += 1
        print("línea base: %d evidencias, juez %s" % (n, M._version()["huella"][:12]))
        return 0
    if modo == "control":                                        # P-VX-22, control negativo: un defecto en _patient se ve
        original = CV._patient

        def roto(J, m, r, *a, **k):
            J.cuenta("valor_distinto", "PID-5", "defecto inyectado por el control del rejuicio")
            return original(J, m, r, *a, **k)
        CV._patient = roto
    antes = {json.loads(l)["evidencia"]: l.rstrip("\n") for l in open(base, encoding="utf-8")}
    dif, n = [], 0
    for ruta, e in evidencias(carpetas):
        n += 1
        ahora = fila(ruta, e)
        if antes.get(ruta) != ahora:
            dif.append(ruta)
    falta = sorted(set(antes) - {r for r, _ in evidencias(carpetas)})
    print("rejuicio (%s): %d evidencias, %d diferencias, %d de la línea base sin evidencia; juez %s" % (
        modo, n, len(dif), len(falta), M._version()["huella"][:12]))
    for d in dif[:10]:
        print("  distinta: %s" % d)
    if modo == "control":
        return 0 if dif else 1
    return 0 if not dif and not falta else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
