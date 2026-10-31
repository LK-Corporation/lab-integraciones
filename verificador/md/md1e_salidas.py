#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 26, MD1-e (md/diseno-md.md §11): las salidas de MD1-a (E-MD-3: los dos conversores con las muestras públicas de MDM)
juzgadas con el perfil puesto. Cada evidencia se juzga con el punto que hoy le da la herramienta (cv/verificar_conversor.punto:
MDM -> mdm_conv), no con el adt_conv con que se guardó. Escribe el juicio por caso (privado) y resume por conversor: categorías,
emparejamiento y los hallazgos que cuentan por (subtipo, hecho). Es para el informe de MD1 y para la previsión de MD2; no toca el
perfil. Solo biblioteca estándar.
  python3 md/md1e_salidas.py <carpeta mdpre> <salida.json>"""
import collections
import glob
import json
import os
import re
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [FASE, os.path.join(FASE, "cv")]
_argv, sys.argv = sys.argv, ["x", "--silencio"]
import mcp_verificador as M  # noqa: E402
import verificador as V  # noqa: E402
import verificar_conversor as VC  # noqa: E402
sys.argv = _argv


def base(hecho):
    return re.sub(r"\(\d+\)", "", hecho)


def main(carpeta, salida):
    res = {"juez": M._version()["huella"][:12], "casos": {}, "resumen": {}}
    for conv in ("microsoft", "linuxforhealth"):
        cats, emp, mec, notas, n = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), 0
        casos_mec = collections.defaultdict(set)
        for f in sorted(glob.glob(os.path.join(carpeta, conv, "evidencias", conv, "muestras", "*.json"))):
            e = json.load(open(f, encoding="utf-8"))
            pe = VC.punto(e["mensaje"])
            e = dict(e, punto_entrada=pe)
            r = V.verificar(e)
            v = r["veredicto"]
            caso = os.path.splitext(os.path.basename(f))[0]
            ev = "^".join((VC._msh9_partes(e["mensaje"]) or [""])[:2])
            if v["categoria"] == "fuera_de_alcance":
                cats["fuera_de_alcance (%s)" % ev] += 1
                continue
            n += 1
            cats["%s%s" % (v["categoria"], "/" + v["subtipo"] if v.get("subtipo") else "")] += 1
            for x in (r["conversion"] or {}).get("emparejamiento") or []:
                emp["%s %s" % (x["rol"].split("#")[0], x["emparejado_por"])] += 1
            cuentan = [h for h in r["hallazgos"] if h["cuenta"]]
            for h in cuentan:
                for s in h["subtipo"].split("+"):
                    mec[(s, base(h["hecho"]))] += 1
                    casos_mec[(s, base(h["hecho"]))].add(caso)
            for h in r["hallazgos"]:
                if not h["cuenta"]:
                    notas[h["subtipo"]] += 1
            res["casos"].setdefault(conv, {})[caso] = {"evento": ev, "veredicto": v, "cuentan": [(h["subtipo"], h["hecho"], h["que"]) for h in cuentan],
                                                       "notas": sorted({h["subtipo"] for h in r["hallazgos"] if not h["cuenta"]}),
                                                       "emparejamiento": (r["conversion"] or {}).get("emparejamiento")}
        res["resumen"][conv] = {"juzgados": n, "categorias": dict(sorted(cats.items())), "emparejamiento": dict(sorted(emp.items())),
                                "mecanismos": [{"subtipo": s, "hecho": h, "hallazgos": c, "casos": len(casos_mec[(s, h)])}
                                               for (s, h), c in sorted(mec.items(), key=lambda t: (-len(casos_mec[t[0]]), t[0]))],
                                "notas": dict(sorted(notas.items(), key=lambda t: -t[1]))}
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    for conv, r in res["resumen"].items():
        print("== %s: %d juzgados (MDM^T02)" % (conv, r["juzgados"]))
        print("  categorías: %s" % r["categorias"])
        print("  emparejamiento: %s" % r["emparejamiento"])
        for x in r["mecanismos"]:
            print("  %-28s %-8s %3d casos (%d hallazgos)" % (x["subtipo"], x["hecho"], x["casos"], x["hallazgos"]))
        print("  notas: %s" % r["notas"])
    print("juez %s" % res["juez"])
    robustez(carpeta)
    return 0


def robustez(carpeta):
    """Los MDM de las muestras con tres salidas que no son las suyas: un Bundle vacío, el genérico del juguete y un error. Ninguna
    excepción; cuenta las categorías."""
    import conversor_juguete as JG
    vacio = json.dumps({"resourceType": "Bundle", "type": "collection", "entry": []})
    cats, exc, n = collections.Counter(), [], 0
    for f in sorted(glob.glob(os.path.join(carpeta, "microsoft", "evidencias", "microsoft", "muestras", "*.json"))):
        m = json.load(open(f, encoding="utf-8"))["mensaje"]
        for nombre, salida in (("vacio", {"estado": "bundle", "bundle": vacio}), ("generico", {"estado": "bundle", "bundle": JG.texto(JG.generico(JG.Msg(m)))}),
                               ("error", {"estado": "error", "error": {"codigo": "1", "texto": "fallo"}})):
            n += 1
            e = {"punto_entrada": VC.punto(m), "mensaje": m, "conversion": {"conversor": {"nombre": "robustez"}, "salida": salida}}
            try:
                v = V.verificar(e)["veredicto"]
                cats["%s %s%s" % (nombre, v["categoria"], "/" + v["subtipo"] if v.get("subtipo") else "")] += 1
            except Exception as ex:                                  # noqa: BLE001
                exc.append("%s %s: %s" % (os.path.basename(f), nombre, type(ex).__name__))
    print("robustez: %d juicios, %d excepciones; %s" % (n, len(exc), dict(sorted(cats.items()))))
    for x in exc[:10]:
        print("  EXCEPCIÓN %s" % x)


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
