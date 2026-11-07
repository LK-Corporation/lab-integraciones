#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33 (ga/diseno-ga-fable.md §7; ANTES, «Qué cambia», 6): la lista de la versión 2 del corpus, una fila por mensaje de los 767
que validó el aparato de la 30, con su origen, su huella, su veredicto y sus marcas:
- a_proposito: lo que la base hace inválido o raro a propósito (A1: S95, S90 y S22, MSH-12 2.5.1; L17: el par de L-25 y M-35);
- fragmento_estandar: los 7 ejemplos del capítulo 3, con su línea en Ch03.txt; copia_completada_de: sus 7 copias;
- gemelo_de: los 37 gemelos con ISO+;
- avisos_conocidos y errores_conocidos: lo que el comprobador de tipos dice de un mensaje de ADT y se acepta (P1, P5, P8);
- sin_decidir: los lugares que dejan el mensaje sin decidir (TXA-3, la 0396, …).
La guarda: un mensaje inválido para IRIS lleva a_proposito o fragmento_estandar; un mensaje de ADT con un error del comprobador lleva
a_proposito, fragmento_estandar o errores_conocidos; toda marca a_proposito corresponde a un hallazgo real. Sale 1 si no.
  cd fase12 && python3 ga/lista_corpus_v2.py <CORPUS-IV.json v2> <corpus v2>"""
import json
import os
import re
import sys

GA = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(GA)
sys.path[:0] = [GA, FASE]
import comprobar_tipos as CT  # noqa: E402

CORP, DIR = sys.argv[1:3]
filas_c = json.load(open(CORP, encoding="utf-8"))["filas"]
V = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(GA, "VEREDICTOS-GA.jsonl"), encoding="utf-8")}
A1 = {x["id"]: x["familia"] for x in json.load(open(os.path.join(GA, "bases_a1_v2.json"), encoding="utf-8"))}
GEN = {x["id"]: x for x in json.load(open(os.path.join(GA, "bases_adt_v2.json"), encoding="utf-8"))}
CAP3 = {x["id"]: x for x in json.load(open(os.path.join(GA, "ejemplos_cap3_v2.json"), encoding="utf-8"))}
GEM = {g["gemelo"]: g for g in json.load(open(os.path.join(GA, "GEMELOS.json"), encoding="utf-8"))}
LINEAS_CAP3 = {"cap3-08-A01": "Ch03.txt:9094-9095", "cap3-10-A04": "Ch03.txt:9155-9156", "cap3-12-A02": "Ch03.txt:9239-9241",
               "cap3-14-A02": "Ch03.txt:9270-9272", "cap3-15-A03": "Ch03.txt:9290-9292", "cap3-36-A04": "Ch03.txt:10866-10868",
               "cap3-37-A04": "Ch03.txt:10890-10891"}
A_PROPOSITO_A1 = {   # (familia, regla, lugar) -> por qué (a1/gen_bases_a1.py:3-6)
    ("pv1_2_vacio", "R_ausente", "PV1-2"): ("PV1-2 vacío, para la tolerancia del perfil del sitio (S95)", "Ch03.txt:5657"),
    ("clases", "tabla_usuario", "PID-8"): ("PID-8 en minúscula o fuera de la 0001 (S22)", "Ch03.txt:5037"),
    ("clases", "tabla_usuario", "PV1-2"): ("PV1-2 en minúscula o fuera de la 0004 (S90)", "Ch03.txt:5736-5745"),
    ("escapes_251", "tabla_usuario", "PID-8"): ("PID-8 fuera de la 0001 (S22)", "Ch03.txt:5037"),
    ("escapes_251", "tabla_usuario", "PV1-2"): ("PV1-2 fuera de la 0004 (S90)", "Ch03.txt:5736-5745"),
    ("escapes_251", "tabla_hl7", "MSH-12.1"): ("MSH-12 = 2.5.1, otra versión", "CH02.txt:4525-4533"),
}
ERRORES_CONOCIDOS = {("cap3-36-A04-completada", "tabla_hl7", "PID-5.8"): "XPN.8 = D del ejemplo, que la copia deja (P5)"}
mal = []
out = []
for f in filas_c:
    i, c = f["id"], f["corpus"]
    b = os.path.basename(i)[:-4]
    texto = open(os.path.join(DIR, f["fichero"]), encoding="utf-8", newline="").read()
    v = V[i]
    fila = {"id": i, "corpus": c, "huella": f["sha256"], "msh9": f["msh9"], "version": 2, "veredicto": v["veredicto_sostenido"],
            "marcas": {}}
    m = fila["marcas"]
    if v["veredicto_sostenido"] == "no_decidible":
        m["sin_decidir"] = sorted({x.get("lugar") for x in v["no_decidibles"]})
    if v["veredicto_sostenido"] == "invalido":
        m["invalido_por"] = sorted({x.get("lugar") for x in v["sostenidos"]})
    if b in GEN:
        fila.update(origen="genadt", evento=GEN[b]["evento"], familia=GEN[b]["familia"])
    elif b in A1:
        fila.update(origen="a1", familia=A1[b])
    elif b in CAP3:
        fila["origen"] = "cap3-completada" if "copia_completada_de" in CAP3[b] else "cap3"
        if "copia_completada_de" in CAP3[b]:
            m["copia_completada_de"] = CAP3[b]["copia_completada_de"]
        else:
            m["fragmento_estandar"] = LINEAS_CAP3[b]
    elif c == "gemelos":
        g = GEM[os.path.basename(i)]
        fila["origen"] = "gemelo"
        m["gemelo_de"] = {"id": g["origen"], "campo": "OBX-6 o RXA-7, componente 3", "de": "UCUM", "a": "ISO+"}
    else:
        fila["origen"] = c
    if b == "L17-pid-30-no-caso":
        m["a_proposito"] = [{"campo": "PID-30", "que": "NO, fuera de la 0136 y del LEN 1", "por_que": "el par de L-25 y M-35",
                             "cita": "Ch03.txt:4829"}]
    if c == "lab/adt":
        hs = CT.comprobar(texto)
        ap, av, ec = [], {}, []
        for h in hs:
            lug = re.sub(r"\(\d+\)|\[\d+\]", "", h["lugar"])
            k = (fila.get("familia"), h["regla"], lug)
            if fila["origen"] == "a1" and k in A_PROPOSITO_A1:
                por, cita = A_PROPOSITO_A1[k]
                if not any(x["campo"] == lug and x["por_que"] == por for x in ap):
                    ap.append({"campo": lug, "regla": h["regla"], "por_que": por, "cita": cita})
            elif (b, h["regla"], lug) in ERRORES_CONOCIDOS:
                ec.append({"campo": lug, "regla": h["regla"], "por_que": ERRORES_CONOCIDOS[(b, h["regla"], lug)]})
            elif h["gravedad"] == "aviso":
                av["%s %s" % (h["regla"], lug)] = av.get("%s %s" % (h["regla"], lug), 0) + 1
            elif "fragmento_estandar" not in m:
                mal.append("%s: error del comprobador sin marca %s %s" % (i, h["regla"], lug))
        if ap:
            m["a_proposito"] = ap
        if av:
            m["avisos_conocidos"] = av
        if ec:
            m["errores_conocidos"] = ec
        if fila["origen"] == "a1" and A1[b] in ("pv1_2_vacio", "escapes_251") and not ap:
            mal.append("%s: familia a propósito sin hallazgo" % i)
    if fila["veredicto"] == "invalido" and not (m.get("a_proposito") or m.get("fragmento_estandar")):
        mal.append("%s: inválido sin marca" % i)
    out.append(fila)
PRIV = os.path.join(FASE, "..", "privado", "ga")
os.makedirs(PRIV, exist_ok=True)
with open(os.path.join(PRIV, "LISTA-CORPUS-V2-con-veredictos.jsonl"), "w", encoding="utf-8") as g:
    for fila in out:
        g.write(json.dumps(fila, ensure_ascii=False, sort_keys=True) + "\n")
VEREDICTO = ("veredicto", "sin_decidir", "invalido_por")          # Q-IV-D-10 de la 30: no se publican las filas por mensaje
with open(os.path.join(GA, "LISTA-CORPUS-V2.jsonl"), "w", encoding="utf-8") as g:
    for fila in out:
        pub = {k: v for k, v in fila.items() if k not in VEREDICTO}
        pub["marcas"] = {k: v for k, v in fila["marcas"].items() if k not in VEREDICTO}
        g.write(json.dumps(pub, ensure_ascii=False, sort_keys=True) + "\n")
cuenta = {}
for fila in out:
    for k in fila["marcas"]:
        cuenta[k] = cuenta.get(k, 0) + 1
print("filas %d; marcas %s" % (len(out), json.dumps(cuenta, ensure_ascii=False)))
for x in mal[:20]:
    print("  MAL", x)
print("LISTA DEL CORPUS V2:", "TODO BIEN" if not mal else "%d MAL" % len(mal))
sys.exit(0 if not mal else 1)
