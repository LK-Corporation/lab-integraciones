#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 24 (cv/ci/diseno-ci2-fable.md §5.3): comprueba desde fuera el run en rojo a propósito. Lee el artefacto del job «rojo»
(descargado, sin el prefijo trabajo/) y decide si el job falló por el hallazgo sembrado de DEFECTO.json y solo por él, si dejó su
resumen y si el artefacto está entero. Las salidas del job (--salidas) no deciden: si llegan vacías se anota; si llegan, tienen
que cuadrar con el artefacto. Escribe COMPROBACION-ROJO.json y sale con 0 solo si todo es cierto.
  python3 cv/ci/comprobar_rojo.py <artefacto> <DEFECTO.json> <LINEA-BASE.json> --resultado-job <success|failure|...>
                                  [--salidas <resultado> <nuevos> <nuevos_distintos>] -o <carpeta>"""
import argparse
import json
import os
import sys


def leer(ruta):
    try:
        return json.load(open(ruta, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def triples(x):
    return sorted(tuple(t) for t in x or [])


def comprobar(artefacto, defecto, base, resultado_job, salidas):
    c = os.path.join(artefacto, "corrida")
    d, b, v = leer(defecto), leer(base), leer(os.path.join(c, "VEREDICTO-CI.json"))
    vv = v or {}
    nuevos = vv.get("nuevos") or []
    md = os.path.join(c, "VEREDICTO-CI.md")
    lineas = open(md, encoding="utf-8").read().splitlines() if os.path.exists(md) else []
    prop = leer(os.path.join(c, "LINEA-BASE-propuesta.json")) or {}
    primero = nuevos[0] if nuevos else {}
    en_prop = [primero.get("hecho"), primero.get("clase"), primero.get("subtipo")] in \
        ((prop.get("casos") or {}).get(primero.get("caso"), {}).get("hallazgos") or []) if primero else False
    r = {
        "job_fallido": resultado_job == "failure",
        "veredicto_en_el_artefacto": v is not None,
        "esperaba_pasa": vv.get("esperado") == "pasa",
        "fallo": vv.get("resultado") == "falla" and vv.get("pasa") is False and vv.get("veredicto_esperado") is False,
        "solo_hallazgo_nuevo": vv.get("motivos") == ["hallazgo_nuevo"] and vv.get("salida_perdida") == [] and vv.get("indeterminado_nuevo") == []
        and vv.get("casos_ausentes") == [],
        "el_hallazgo_esperado": bool(d) and triples(vv.get("nuevos_distintos")) == triples(d.get("hallazgo_esperado")),
        "en_casos_de_la_base": bool(nuevos) and bool(b) and all(x.get("caso") in (b.get("casos") or {}) for x in nuevos) and vv.get("casos_nuevos") == [],
        "conversor_cambiado": "huella_distinta" in (vv.get("avisos") or {}) and not ({"juez_distinto", "corpus_distinto", "imagen_distinta"} & set(vv.get("avisos") or {})),
        "resumen": bool(lineas) and lineas[0] == "## Verificador: ejemplo · pasa · **FALLA**" and any(l.startswith("### Hallazgos nuevos") for l in lineas),
        "informe_y_propuesta": all(os.path.exists(os.path.join(c, f)) for f in ("INFORME.json", "juicio.jsonl", "LINEA-BASE-propuesta.json")) and en_prop,
    }
    salidas_del_job = "vacias"
    if salidas and salidas[0]:
        resultado, n, distintos = salidas
        try:
            distintos = json.loads(distintos)
        except ValueError:
            distintos = None
        salidas_del_job = {"resultado": resultado, "nuevos": n, "nuevos_distintos": distintos}
        r["salidas_cuadran"] = resultado == "falla" and n == str(len(nuevos)) and triples(distintos) == triples(vv.get("nuevos_distintos"))
    return {"formato": "comprobacion-rojo/1", "resultado_job": resultado_job, "comprobaciones": r, "salidas_del_job": salidas_del_job,
            "n_casos_con_el_hallazgo": len({x.get("caso") for x in nuevos}), "todo_bien": all(r.values())}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="comprobar_rojo", description="El run en rojo, comprobado desde fuera (etapa 24).")
    ap.add_argument("artefacto")
    ap.add_argument("defecto")
    ap.add_argument("base")
    ap.add_argument("--resultado-job", required=True)
    ap.add_argument("--salidas", nargs=3, default=None)
    ap.add_argument("-o", dest="salida", required=True)
    a = ap.parse_args(argv)
    res = comprobar(a.artefacto, a.defecto, a.base, a.resultado_job, a.salidas)
    os.makedirs(a.salida, exist_ok=True)
    json.dump(res, open(os.path.join(a.salida, "COMPROBACION-ROJO.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, ok in res["comprobaciones"].items():
        print("  %s %s" % ("✓" if ok else "✗", k))
    print("comprobar_rojo: %s; %d casos con el hallazgo; salidas del job: %s" % (
        "TODO BIEN" if res["todo_bien"] else "MAL", res["n_casos_con_el_hallazgo"],
        res["salidas_del_job"] if isinstance(res["salidas_del_job"], str) else "llegaron"))
    return 0 if res["todo_bien"] else 1


if __name__ == "__main__":
    sys.exit(main())
