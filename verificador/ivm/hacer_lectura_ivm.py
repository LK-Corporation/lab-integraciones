#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 31: ivm/lectura_ivm.py sale de iv/lectura_iv.py (la lectura de la 30, publicada) con las reglas de Q-MV-2 (Jev,
ivm/decision-jev-qmv.md: lo que no se puede leer con el texto de v2.5 va aparte y no entra en el veredicto). La primera versión
se selló ANTES de correr las muestras; lo cambiado después está declarado en ivm/SELLO-IVM.txt: la ruta de los veredictos; la
variante que manda cuando MSH-9.3 no tiene estructura en v2.5, junto con que una pasada sin leer entera no deje salir válida una
muestra; tras la segunda revisión a ciegas, la 0399 con los valores de las muestras y MSH-12 (Q-MV-3); y, tras la tercera,
que cada error de los veredictos lleve el índice de su segmento y su repetición (no cambia ninguna regla). Van aparte:
- un segmento que no tiene tabla de atributos en v2.5, o un campo que su tabla no trae;
- una tabla que no está en el índice del Apéndice A de v2.5.
MSH-12 con una versión que no está en la 0104 de v2.5 ya no va aparte: queda sin decidir, como en la 30 (Q-IV-D-11b), por Q-MV-3
(ivm/decision-jev-qmv3.md). La versión sellada la ponía aparte por la decisión S19 del juez.
Afirma cada sustitución. Desde fase12:  python3 ivm/hacer_lectura_ivm.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = open(os.path.join(FASE, "iv", "lectura_iv.py"), encoding="utf-8").read()
CAMBIOS = [
    ('"""Etapa 30 (iv/diseno-iv-fable.md §3.4; Q-IV-D-5: lee el conductor, con cita): cada lugar que cuenta, leído en el texto de v2.5.',
     '"""Etapa 31 (ANTES-ETAPA-IVMUESTRAS.md): la lectura de la etapa 30 (iv/lectura_iv.py), para las muestras públicas, con Q-MV-2\n'
     '(ivm/decision-jev-qmv.md): lo que no se puede leer con el texto de v2.5 va APARTE y no entra en el veredicto (un segmento o un\n'
     'campo que v2.5 no define, una tabla que su índice no trae). MSH-12 con otra versión queda sin decidir, como en la 30\n'
     '(Q-MV-3, ivm/decision-jev-qmv3.md). Hecho con ivm/hacer_lectura_ivm.py.\n'
     'Lo que sigue es la cabecera de la 30.\n'
     'Etapa 30 (iv/diseno-iv-fable.md §3.4; Q-IV-D-5: lee el conductor, con cita): cada lugar que cuenta, leído en el texto de v2.5.'),
    ('TV = json.load(open(os.path.join(PRIV, "iv", "TABLAS-VALORES-IV.json"), encoding="utf-8"))',
     'TV = json.load(open(os.path.join(PRIV, "iv", "TABLAS-VALORES-IV.json"), encoding="utf-8"))   # los mismos de la 30'),
    ('        clase = considerar(p)\n        if clase is None:\n            continue\n        clave = "%s|%s|%s|%s" % (clase, p.get("seg"), p.get("campo") or "", p.get("tabla") or "")\n        ok = LECT[clave]["sostenida"] if clave in LECT else True',
     '        clase = considerar(p)\n        if clase is None:\n            continue\n        clave = "%s|%s|%s|%s" % (clase, p.get("seg"), p.get("campo") or "", p.get("tabla") or "")\n'
     '        motivo_aparte = aparte_ivm(clase, p)                       # Q-MV-2: no se lee con v2.5, va aparte\n'
     '        if motivo_aparte:\n'
     '            aparte.append({"lugar": clave, "valor": p.get("valor"), "por": motivo_aparte})\n'
     '            ajustes[(clave, "aparte: " + motivo_aparte)] += 1\n'
     '            continue\n'
     '        ok = LECT[clave]["sostenida"] if clave in LECT else True'),
    ('    sost, nd = [], []\n    for p in v["errores"]:\n        clase = considerar(p)',
     '    sost, nd, aparte = [], [], []\n    for p in v["errores"]:\n        clase = considerar(p)'),
    ('                       "sostenidos": sost, "no_decidibles": nd})',
     '                       "sostenidos": sost, "no_decidibles": nd, "aparte": aparte})'),
    ('sys.path.insert(0, AQUI)\nimport validar_iv as V  # noqa: E402',
     'sys.path.insert(0, os.path.join(os.path.dirname(AQUI), "iv"))       # el conductor de la 30\nimport validar_iv as V  # noqa: E402'),
    # tras la corrida (declarado en el sello y en el resultado): la variante que manda y lo que no se pudo leer entero
    ('for f in F:\n    v = f["variantes"].get("msh93") or f["variantes"].get("esquema") or f["variantes"].get("ninguna")\n'
     '    orig = V.segmentos(',
     'for f in F:\n    v, sin_estructura = principal_ivm(f)\n'
     '    orig = V.segmentos('),
    ('for f in F:\n    v = f["variantes"].get("msh93") or f["variantes"].get("esquema") or f["variantes"].get("ninguna")\n'
     '    for p in v["errores"]:\n        clase = considerar(p)',
     'for f in F:\n  for v in f["variantes"].values():                # todas las variantes: la que mande tiene que estar leída\n'
     '    for p in v["errores"]:\n        clase = considerar(p)'),
    ('    veredictos.append({"id": f["id"], "corpus": f["corpus"], "veredicto_iris_que_cuenta": v["veredicto_que_cuenta"],',
     '    if sin_estructura:                               # MSH-9.3 sin estructura en v2.5: fuera de la 0354 impresa (Q-IV-D-11)\n'
     '        nd.append({"lugar": "T_HL7|MSH|9|0354", "valor": f["doctype_msh93"], "sistema_0396": False,\n'
     '                   "por": "MSH-9.3 sin estructura en el esquema 2.5; se valida con la de la 0354 (Q-IV-D-2 y Q-IV-D-11)"})\n'
     '    sin_leer = sorted(s for s, fin in v["fines"].items() if s != "dn" and fin in ("no_reconocido", "tope_alcanzado", "no_enmudecible"))\n'
     '    if sin_leer and not sost:                        # una pasada sin leer entera: la muestra no puede salir válida\n'
     '        nd.append({"lugar": "aparato", "valor": None, "sistema_0396": False, "por": "pasadas sin leer enteras: %s" % ", ".join(sin_leer)})\n'
     '    veredictos.append({"id": f["id"], "corpus": f["corpus"], "veredicto_iris_que_cuenta": v["veredicto_que_cuenta"],'),
    ('        e = {"lugar": clave, "valor": p.get("valor"), "sistema_0396": clase == "T_HL7" and p.get("tabla") == "0396"}',
     '        e = {"lugar": clave, "valor": p.get("valor"), "sistema_0396": clase == "T_HL7" and p.get("tabla") == "0396",\n'
     '             "idx": p.get("idx"), "rep": p.get("rep"),                # dónde está, en el clon (tercera revisión)\n'
     '             "leido": V.leer(segs, p["idx"], p["campo"], p.get("rep") or 1) if clase == "L" and segs else None}'),
    ('SAL.replace("LECTURAS-IV.json", "VEREDICTOS-IV.jsonl")',
     'SAL.replace("LECTURAS-IVM.json", "VEREDICTOS-IVM.jsonl")'),       # la ruta de los veredictos (arreglo tras la corrida)
    ('EXTERNAS = {"0399": ("ISO 3166, forma de tres letras (CH02.txt:4580-4585)", {"ESP"})}',
     'EXTERNAS = {"0399": ("ISO 3166, forma de tres letras (CH02.txt:4580-4585)", {"ESP", "USA", "GBR"})}   # los de las muestras\n'
     '# (USA y GBR, leídos tras la revisión a ciegas; US, JP, 764, 44 y 999990000 no tienen la forma de tres letras)'),
    ('veredictos = []\najustes = collections.Counter()',
     'def principal_ivm(f):\n'
     '    """La variante que manda: la de MSH-9.3, salvo que su estructura no exista en el esquema 2.5 (IRIS: «no DocType set»);\n'
     '    entonces, la de la 0354. -> (variante, si MSH-9.3 no tenía estructura)."""\n'
     '    vs = f["variantes"]\n'
     '    m = vs.get("msh93")\n'
     '    if m and vs.get("esquema") and any("no DocType set" in (p.get("crudo") or "") for p in m["errores"]):\n'
     '        return vs["esquema"], True\n'
     '    return (m or vs.get("esquema") or vs.get("ninguna")), False\n\n\n'
     'def aparte_ivm(clase, p):\n'
     '    """Q-MV-2: el motivo por el que un error no se lee con el texto de v2.5, o None."""\n'
     '    seg, campo, tabla = p.get("seg"), p.get("campo"), p.get("tabla")\n'
     '    if seg and seg not in ATR and not seg.startswith("Z"):\n'
     '        return "segmento sin tabla de atributos en v2.5"\n'
     '    if clase in ("R", "L") and campo and campo not in ATR.get(seg, {}):\n'
     '        return "campo que la tabla de atributos de v2.5 no trae"\n'
     '    if clase.startswith("T") and tabla and tabla not in INDICE:\n'
     '        return "tabla que el índice del Apéndice A de v2.5 no trae"\n'
     '    return None\n\n\n'
     'veredictos = []\najustes = collections.Counter()'),
]
for viejo, nuevo in CAMBIOS:
    assert t.count(viejo) == 1, "no está (o no es único): %r" % viejo[:70]
    t = t.replace(viejo, nuevo)
open(os.path.join(FASE, "ivm", "lectura_ivm.py"), "w", encoding="utf-8").write(t)
print("ivm/lectura_ivm.py: escrita desde iv/lectura_iv.py con %d cambios" % len(CAMBIOS))
