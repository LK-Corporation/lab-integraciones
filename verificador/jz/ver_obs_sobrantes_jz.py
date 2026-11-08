#!/usr/bin/env python3
"""Etapa 37, para los estados de Jev: en evidencias ADT, los segmentos ACC/PDA del mensaje y las Observation del Bundle.

  python3 jz/ver_obs_sobrantes_jz.py <evidencia.json> [...]

Imprime, por evidencia, los segmentos sin destino que trae (ACC, PDA y los demás de la hoja) con sus campos, el número de OBX y,
de cada Observation del Bundle, su code, sus valores y sus fechas. No juzga nada."""
import json
import sys

SIN_DESTINO = ("ARV", "UAC", "OH1", "OH2", "OH3", "OH4", "PRT", "DB1", "IAM", "DRG", "GT1", "IN2", "AUT", "RF1", "UB1", "UB2",
               "ACC", "PDA")


def segmentos(m):
    m = m.replace("\r\n", "\r").replace("\n", "\r")
    return [s for s in m.split("\r") if s.strip()]


def corto(x, n=230):
    t = json.dumps(x, ensure_ascii=False)
    return t if len(t) <= n else t[:n] + "…"


def main(*fs):
    for f in fs:
        e = json.load(open(f, encoding="utf-8"))
        segs = segmentos(e.get("mensaje") or "")
        print("==", f.split("privado/")[-1], "| MSH-9:", segs[0].split("|")[8] if segs else "?")
        print("   segmentos:", " ".join(s[:3] for s in segs))
        for s in segs:
            if s[:3] in SIN_DESTINO:
                print("   ", s[:200])
        print("   OBX:", sum(1 for s in segs if s[:3] == "OBX"))
        sal = ((e.get("conversion") or {}).get("salida") or {})
        b = sal.get("bundle") or sal.get("recurso") or sal.get("cuerpo")
        if isinstance(b, str):
            try:
                b = json.loads(b)
            except ValueError:
                b = None
        if not isinstance(b, dict):
            print("   (sin Bundle legible; claves de salida: %s)" % sorted(sal))
            continue
        for en in b.get("entry") or []:
            r = en.get("resource") or {}
            if r.get("resourceType") == "Observation":
                v = {k: r[k] for k in r if k.startswith("value") or k.startswith("effective") or k in ("code", "issued")}
                print("    Observation", corto(v))


if __name__ == "__main__":
    main(*sys.argv[1:])
