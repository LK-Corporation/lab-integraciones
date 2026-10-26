#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 24 (cv/ci/diseno-ci2-fable.md §4.3): comprueba desde fuera las dos llamadas del proyecto de ejemplo por la forma
remota. Lee los dos artefactos (descargados, sin el prefijo trabajo/) y decide si cada uno pasó contra su base sin nada nuevo,
con las identidades de la base, y si las entradas hicieron lo que deben y nada más: en «ejemplo», el corpus del laboratorio más
el propio, con INFORME.md y sin evidencias; en «ejemplo-propio», solo el propio (sin_corpus_lab), sin INFORME.md (--json-solo)
y con evidencias y corpus (artefacto_completo). Aquí las salidas de los jobs (--salidas) sí deciden: los jobs salieron bien.
Escribe COMPROBACION-EJEMPLO.json y sale con 0 solo si todo es cierto.
  python3 cv/ci/comprobar_ejemplo.py <artefacto ejemplo> <artefacto propio> <LINEA-BASE.json> <LINEA-BASE-propio.json>
                                     <adaptador.json> [--salidas <resultado> <huella> <digest> <resultado propio>] -o <carpeta>"""
import argparse
import json
import os
import sys

FIJOS = {"corrida/INFORME.json", "corrida/juicio.jsonl", "corrida/CORRIDA.json", "corrida/ADAPTADOR.json", "corrida/VEREDICTO-CI.json",
         "corrida/VEREDICTO-CI.md", "corrida/LINEA-BASE-propuesta.json", "solo-orden.txt"}
SEIS = {"EJ-ADT-A01", "EJ-ADT-A03", "EJ-ADT-A08", "EJ-ORU-R01", "EJ-ORU-R01-dos", "EJ-VXU-V04"}


def leer(ruta):
    try:
        return json.load(open(ruta, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def ficheros(raiz):
    out = set()
    for d, _, fs in os.walk(raiz):
        for f in fs:
            out.add(os.path.relpath(os.path.join(d, f), raiz).replace(os.sep, "/"))
    return out


def no_cero(n):
    return {k: v for k, v in (n or {}).items() if v}


def un_artefacto(a, b, ad, propio):
    v = leer(os.path.join(a, "corrida", "VEREDICTO-CI.json")) or {}
    inf = leer(os.path.join(a, "corrida", "INFORME.json")) or {}
    b = b or {}
    n = b.get("n_casos")
    fs = ficheros(a)
    resto = {f for f in fs if not f.startswith("corrida/cajas/") and not f.startswith("corrida/evidencias/") and not f.startswith("corrida/corpus/")}
    md = os.path.join(a, "corrida", "VEREDICTO-CI.md")
    primera = open(md, encoding="utf-8").readline().rstrip("\n") if os.path.exists(md) else ""
    nb = no_cero((b.get("corpus") or {}).get("n"))
    r = {
        "pasa": v.get("esperado") == "pasa" and v.get("resultado") == "pasa" and v.get("pasa") is True and v.get("veredicto_esperado") is True
        and v.get("motivos") == [],
        "nada_nuevo": all(v.get(k) == [] for k in ("nuevos", "arreglos", "casos_nuevos", "casos_ausentes", "notas", "cambios_de_categoria")),
        "sin_avisos": v.get("avisos") == {},
        "todos_los_casos": n is not None and n == len(b.get("casos") or {}) and v.get("n") == {"base": n, "corrida": n, "comparados": n},
        "identidades": (v.get("identidades") or {}).get("huella") == (b.get("conversor") or {}).get("huella")
        and (v.get("identidades") or {}).get("imagen_digest") == ad["caja"]["imagen_digest"]
        and (v.get("identidades") or {}).get("juez") == ((b.get("creada_de") or {}).get("juez") or {}).get("huella"),
        "corpus_del_informe": no_cero((inf.get("corpus") or {}).get("n")) == nb,
        "resumen": primera == "## Verificador: ejemplo · pasa · **PASA**",
    }
    if propio:
        hl7 = {os.path.basename(f)[:-4] for f in fs if f.startswith("corrida/corpus/") and f.endswith(".hl7")}
        r["solo_el_corpus_propio"] = nb == {"propio": 6} and all(k.startswith("propio/") for k in (b.get("casos") or {}))
        r["sin_INFORME_md"] = "corrida/INFORME.md" not in fs
        r["con_evidencias_y_corpus"] = any(f.startswith("corrida/evidencias/") for f in fs) and hl7 == SEIS
        r["nada_mas"] = resto == FIJOS
    else:
        r["corpus_del_laboratorio_y_el_propio"] = nb.get("propio") == 6 and len(nb) > 1
        r["con_INFORME_md"] = "corrida/INFORME.md" in fs
        r["sin_evidencias_ni_corpus"] = not any(f.startswith("corrida/evidencias/") or f.startswith("corrida/corpus/") for f in fs)
        r["nada_mas"] = resto == FIJOS | {"corrida/INFORME.md"}
    return r


def comprobar(art_ej, art_pr, base, base_pr, adaptador, salidas):
    ad = leer(adaptador)
    b, p = leer(base), leer(base_pr)
    res = {"ejemplo": un_artefacto(art_ej, b, ad, False), "ejemplo-propio": un_artefacto(art_pr, p, ad, True)}
    if salidas:
        r, h, d, rp = salidas
        res["salidas"] = {"resultado": r == "pasa", "huella": h == (b or {}).get("conversor", {}).get("huella"),
                          "digest": d == ad["caja"]["imagen_digest"], "resultado_propio": rp == "pasa"}
    todo = all(ok for g in res.values() for ok in g.values())
    return {"formato": "comprobacion-ejemplo/1", "comprobaciones": res, "todo_bien": todo}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="comprobar_ejemplo", description="Las dos llamadas del proyecto de ejemplo, comprobadas desde fuera (etapa 24).")
    for x in ("artefacto_ejemplo", "artefacto_propio", "base", "base_propio", "adaptador"):
        ap.add_argument(x)
    ap.add_argument("--salidas", nargs=4, default=None)
    ap.add_argument("-o", dest="salida", required=True)
    a = ap.parse_args(argv)
    res = comprobar(a.artefacto_ejemplo, a.artefacto_propio, a.base, a.base_propio, a.adaptador, a.salidas)
    os.makedirs(a.salida, exist_ok=True)
    json.dump(res, open(os.path.join(a.salida, "COMPROBACION-EJEMPLO.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for g, cs in res["comprobaciones"].items():
        for k, ok in cs.items():
            print("  %s %s / %s" % ("✓" if ok else "✗", g, k))
    print("comprobar_ejemplo: %s" % ("TODO BIEN" if res["todo_bien"] else "MAL"))
    return 0 if res["todo_bien"] else 1


if __name__ == "__main__":
    sys.exit(main())
