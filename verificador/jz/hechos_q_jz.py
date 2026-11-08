#!/usr/bin/env python3
"""Etapa 37, hechos para los estados de Jev, sobre la línea base del juez de antes (sin juzgar nada de nuevo).

  python3 jz/hechos_q_jz.py <linea_base.jsonl> [...]

1. Rechazos aceptables por PID-8 (Q-JZ-1): por carpeta, el valor de PID-8 y si PID-8 es el único imposible.
2. Recursos inventados en ADT (Q-JZ-2/3/4): por carpeta, los que están en un mensaje con un segmento que la hoja de ADT_A01 lista
   sin destino, y cuáles de esos segmentos trae.
3. Valor imposible en PID-8 con gender ausente no se ve aquí (el juez no dice nada): se cuenta aparte, leyendo las evidencias."""
import collections
import json
import os
import sys

SIN_DESTINO = ("ARV", "UAC", "OH1", "OH2", "OH3", "OH4", "PRT", "DB1", "IAM", "DRG", "GT1", "IN2", "AUT", "RF1", "UB1", "UB2",
               "ACC", "PDA")
PRIVADO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "privado"))


def segs(m):
    m = (m or "").replace("\r\n", "\r").replace("\n", "\r")
    return [s for s in m.split("\r") if s.strip()]


def campo(seg, n):
    p = seg.split("|")
    return p[n] if len(p) > n else ""


def main(*bases):
    rech = collections.Counter()
    inv = collections.Counter()
    seg_inv = collections.Counter()
    for b in bases:
        for l in open(b, encoding="utf-8"):
            x = json.loads(l)
            g = json.loads(x["guardado"])
            carpeta = "/".join(x["evidencia"].split("/")[:2])
            conv = next((p for p in ("microsoft", "linuxforhealth", "juguete", "propio", "ejemplo") if p in x["evidencia"]), "?")
            r_pid8 = [h for h in g["hallazgos"] if h["clase"] == "rechazo" and "PID-8" in json.dumps(h["que"])]
            invent = [h for h in g["hallazgos"] if h.get("subtipo") == "recurso_inventado"]
            if not (r_pid8 or invent):
                continue
            ruta = x["evidencia"] if x["evidencia"].startswith("/") else os.path.join(PRIVADO, x["evidencia"])
            e = json.load(open(ruta, encoding="utf-8"))
            ss = segs(e.get("mensaje"))
            if r_pid8:
                pid = next((s for s in ss if s[:3] == "PID"), "")
                solo = all("['PID-8']" in json.dumps(q, ensure_ascii=False) or "[\"PID-8\"]" in json.dumps(q, ensure_ascii=False)
                           for h in r_pid8 for q in (h["que"] if isinstance(h["que"], list) else [h["que"]]))
                rech[(carpeta, conv, x["punto"], campo(pid, 8), "solo PID-8" if solo else "con otros", g["veredicto"]["categoria"])] += 1
            if invent and x["punto"] == "adt_conv":
                sd = sorted({s[:3] for s in ss if s[:3] in SIN_DESTINO})
                for h in invent:
                    q = json.dumps(h["que"], ensure_ascii=False)
                    tipo = q.split()[0].strip('["') if q else "?"
                    inv[(carpeta, conv, tipo, "+".join(sd) or "-")] += 1
                for s in sd:
                    seg_inv[(conv, s)] += 1
    print("== 1. rechazos aceptables con PID-8 (carpeta, conversor, punto, PID-8, imposibles, categoría): evidencias")
    for k in sorted(rech):
        print("  %-28s %-14s %-9s %-6r %-10s %-18s %d" % (k + (rech[k],)))
    print("  total: %d" % sum(rech.values()))
    print("\n== 2. recursos inventados en ADT (carpeta, conversor, tipo, segmentos sin destino del mensaje): hallazgos")
    for k in sorted(inv):
        print("  %-28s %-14s %-14s %-40s %d" % (k + (inv[k],)))
    print("  total: %d" % sum(inv.values()))
    print("\n== segmentos sin destino presentes en evidencias ADT con algún recurso inventado (conversor, segmento): evidencias")
    for k in sorted(seg_inv):
        print("  %-14s %-5s %d" % (k + (seg_inv[k],)))


if __name__ == "__main__":
    main(*sys.argv[1:])
