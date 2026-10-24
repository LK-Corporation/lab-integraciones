#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CV-pre, sonda E-CV-2 (ANTES-ETAPA-CONVERSORES.md): ¿cuántos mensajes de muestra públicos de los conversores lee el
verificador, y qué acuse espera para cada uno? Solo lectura: el juez se llama como lo llama el MCP (acuse_esperado), con el
mensaje solo, sin ACK observado.

Los saltos de línea se normalizan a CR antes de juzgar (la trama no es lo que se mide aquí; los ficheros de muestra vienen
con LF o CRLF). Cada mensaje va al punto de su tipo: ADT -> adt_fhir, ORU -> oru_fhir.
  cd fase12 && python3 cv/cv_pre_e2.py <carpeta> [<carpeta>…]     -> cv/CV-PRE-E2.json y el resumen en pantalla"""
import collections
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
import mcp_verificador as M  # noqa: E402


def mensajes_del_fichero(texto):
    """Un fichero de muestra puede traer varios mensajes: se parte en cada MSH al principio de línea."""
    t = re.sub(r"\r\n|\n|\r", "\r", texto.strip())
    partes = re.split(r"\r(?=MSH\|)", t)
    return [p.strip("\r") + "\r" for p in partes if p.startswith("MSH|")]


def main(carpetas):
    out = []
    for c in carpetas:
        for f in sorted(os.listdir(c)):
            # utf-8-sig: 8 muestras de Microsoft empiezan con BOM; la primera pasada se las saltó sin avisar (DV-CV-1)
            texto = open(os.path.join(c, f), encoding="utf-8-sig", errors="replace").read()
            for i, m in enumerate(mensajes_del_fichero(texto)):
                campos = m.split("\r")[0].split("|")
                tipo = (campos[8] if len(campos) > 8 else "").split("^")[0]
                pe = {"ADT": "adt_fhir", "ORU": "oru_fhir"}.get(tipo)
                fila = {"fichero": "%s/%s" % (os.path.basename(c), f), "k": i, "msh9": campos[8] if len(campos) > 8 else None,
                        "msh12": campos[11] if len(campos) > 11 else None, "punto": pe}
                if not pe:
                    fila["resultado"] = "fuera_de_alcance"
                else:
                    try:
                        r = M.t_acuse({"mensaje": m, "punto_entrada": pe})
                        sc = r[0] if isinstance(r, tuple) else r
                        x = sc["mensajes"][0]["esperado"]
                        fila.update(resultado="leido", msa1=x.get("msa1"),
                                    err3=sorted({str(z.get("err3") or z.get("codigo") or "") for z in x.get("err") or []}),
                                    version=x.get("version_msh12"), notas=len(x.get("notas") or []))
                    except Exception as ex:                                    # se cuenta, no se oculta
                        fila.update(resultado="error", error="%s: %s" % (type(ex).__name__, str(ex)[:160]))
                out.append(fila)
    json.dump(out, open(os.path.join(AQUI, "CV-PRE-E2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ficheros = sum(len(os.listdir(c)) for c in carpetas)
    sin = sorted({"%s/%s" % (os.path.basename(c), f) for c in carpetas for f in os.listdir(c)} - {x["fichero"] for x in out})
    print("ficheros: %d; sin ningún mensaje leído: %d %s" % (ficheros, len(sin), sin))
    print("mensajes: %d; por resultado: %s" % (len(out), dict(collections.Counter(x["resultado"] for x in out))))
    print("versión MSH-12: %s" % dict(collections.Counter(x["msh12"] for x in out)))
    leidos = [x for x in out if x["resultado"] == "leido"]
    print("acuse esperado: %s" % dict(collections.Counter((x["punto"], x["msa1"]) for x in leidos)))
    print("ERR-3 esperados: %s" % dict(collections.Counter(e for x in leidos for e in x["err3"])))
    for x in out:
        if x["resultado"] == "error":
            print("  ERROR %s#%d: %s" % (x["fichero"], x["k"], x["error"]))


if __name__ == "__main__":
    main(sys.argv[1:])
