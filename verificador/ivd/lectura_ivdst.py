#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 32 (ANTES-ETAPA-IVDECLARADA.md, Q-VD-1): la lectura de las muestras de las versiones sin texto en el laboratorio (2.3, 2.4,
2.6 y 2.8), sobre las filas de ivd/validar_ivdst.py. Sin texto no se lee nada en el estándar; la regla es la que eligió Jev:
- estructura (E), un Z fuera de sitio (Z), obligatorios (R) y longitudes (L): cuentan como los da IRIS («según IRIS»);
- una tabla que el esquema de IRIS trae con valores: sin decidir (sin texto no se sabe si el valor es de la tabla del estándar, ni
  si la tabla es de HL7 o de usuario); una que trae vacía: aviso, no cuenta (lo marca el conductor);
- un segmento con más campos de los que define su versión (la pasada de repeticiones): aparte (Q-VD-3b, la del ANTES; Jev la dejó
  en el titular después de correr, Q-VD-3d). Q-VD-3c («sin decidir») y «dentro» se dan como sensibilidad en el cruce. Otra forma
  de error que el conductor no reconoce: aparte también, con su forma;
- un error de estructura en un segmento que la versión no define (no lo trae el esquema de IRIS de esa versión) y que no es Z:
  aparte, como en la 31 (Q-MV-2 y Q-MV-4). La lectura de la 2.5.1 hace lo mismo con su texto. El control lo cazó: la primera
  versión de esta lectura lo contaba;
- como en la 31: la variante que manda es la de MSH-9.3, salvo que su estructura no exista en el esquema de su versión; y una
  muestra con una pasada sin leer entera (salvo la de repeticiones) no puede salir válida.
Escribe VEREDICTOS-IVDST.jsonl (privado, como en la 31) y LECTURAS-IVDST.json (publicable: lugares y recuentos, sin texto).
  python3 ivd/lectura_ivdst.py <FILAS-IVDST.jsonl> <LECTURAS-IVDST.json>"""
import collections
import json
import re
import sys

FILAS, SAL = sys.argv[1:3]
assert SAL.endswith("LECTURAS-IVDST.json"), "la salida tiene que llamarse LECTURAS-IVDST.json"
F = [json.loads(l) for l in open(FILAS, encoding="utf-8")]
assert F and all(f.get("version") in ("2.3", "2.4", "2.6", "2.8") for f in F), "la lectura sin texto recibe filas de otra versión"


def principal(f):
    vs = f["variantes"]
    m = vs.get("msh93")
    if m and vs.get("esquema") and any("no DocType set" in (p.get("crudo") or "") for p in m["errores"]):
        return vs["esquema"], True
    return (m or vs.get("esquema") or vs.get("ninguna")), False


veredictos = []
lugares = collections.defaultdict(lambda: collections.Counter())
for f in F:
    v, sin_estructura = principal(f)
    sost, nd, aparte = [], [], []
    for p in v["errores"]:
        clave = "%s|%s|%s|%s|%s" % (f["version"], p["clase"], p.get("seg"), p.get("campo") or "", p.get("tabla") or "")
        e = {"lugar": clave, "valor": p.get("valor"), "idx": p.get("idx"), "rep": p.get("rep"), "pasada": p.get("pasada")}
        mas = re.search(r"segment (\d+):(\w+)\.\s+Segment has more fields", p.get("crudo") or "") if p["clase"] == "X" else None
        if mas and p.get("pasada") == "dn":           # Q-VD-3b, la del ANTES (Q-VD-3d): campos de más, aparte
            aparte.append(dict(e, lugar="%s|C|%s||" % (f["version"], mas.group(2)),
                               por="segmento con más campos de los que define su versión (Q-VD-3b)"))
            lugares["%s|C|%s||" % (f["version"], mas.group(2))]["aparte"] += 1
        elif p["clase"] == "X":
            aparte.append(dict(e, por="forma de error que el conductor no reconoce", crudo=(p.get("crudo") or "")[:200]))
            lugares[clave]["aparte"] += 1
        elif not p["cuenta"]:
            lugares[clave]["aviso"] += 1                 # un Z al final; una tabla que el esquema de IRIS trae vacía
        elif p["clase"] == "E" and not p["seg_definido_en_la_version"] and not (p.get("seg") or "").startswith("Z"):
            aparte.append(dict(e, por="segmento que la versión no define (Q-MV-2 y Q-MV-4, como en la 31)"))
            lugares[clave]["aparte"] += 1
        elif p["clase"] in ("E", "Z", "R", "L"):
            sost.append(dict(e, por="según IRIS (Q-VD-1)"))
            lugares[clave]["sostenido"] += 1
        elif p["clase"] == "T_HL7":
            nd.append(dict(e, por="tabla con valores en el esquema de IRIS, sin texto de la versión (Q-VD-1)"))
            lugares[clave]["sin_decidir"] += 1
        else:
            raise SystemExit("PARADA: %s trae un error de clase %s que esta lectura no sabe leer" % (f["id"], p["clase"]))
    if sin_estructura:
        nd.append({"lugar": "%s|T_HL7|MSH|9|0354" % f["version"], "valor": f["doctype_msh93"],
                   "por": "MSH-9.3 sin estructura en el esquema de su versión; se valida con la de la 0354 (Q-IV-D-2 y Q-IV-D-11)"})
    sin_leer = sorted(s for s, fin in v["fines"].items() if s != "dn" and fin in ("no_reconocido", "tope_alcanzado", "no_enmudecible"))
    if sin_leer and not sost:
        nd.append({"lugar": "aparato", "valor": None, "por": "pasadas sin leer enteras: %s" % ", ".join(sin_leer)})
    veredictos.append({"id": f["id"], "corpus": f["corpus"], "version": f["version"],
                       "veredicto_iris_que_cuenta": v["veredicto_que_cuenta"],
                       "veredicto_sostenido": "invalido" if sost else ("no_decidible" if nd else "valido"),
                       "sostenidos": sost, "no_decidibles": nd, "aparte": aparte, "doctype": v.get("doctype"),
                       "campos_sin_evaluar": v.get("campos_sin_evaluar", [])})
with open(SAL.replace("LECTURAS-IVDST.json", "VEREDICTOS-IVDST.jsonl"), "w", encoding="utf-8") as fh:
    for x in veredictos:
        fh.write(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n")
json.dump({"regla": "Q-VD-1 (ivd/decision-jev-qvd.md) y Q-VD-3b (ivd/decision-jev-qvd3b.md)",
           "lugares": {k: dict(c) for k, c in sorted(lugares.items())}},
          open(SAL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
cuenta = collections.defaultdict(collections.Counter)
for x in veredictos:
    cuenta[(x["version"], x["corpus"])][x["veredicto_sostenido"]] += 1
for k in sorted(cuenta):
    print("  %-4s %-14s %s" % (k[0], k[1], dict(cuenta[k])))
print("  TOTAL %s" % dict(collections.Counter(x["veredicto_sostenido"] for x in veredictos)))
