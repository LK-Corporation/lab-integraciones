#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 32 (ANTES-ETAPA-IVDECLARADA.md): el conductor de la 31 (ivm/validar_ivm.py) con la versión que declara cada mensaje,
escrito aparte en dos copias para que el de la 31 no cambie:
- ivd/validar_ivd251.py, para la 2.5.1 (Q-VD-2): la tabla de campos, los tipos y los valores de tablas salen del texto de v2.5.1
  (ivd/texto_ivd.py, ivd/TABLAS-TIPO-IVD251.json y ../privado/ivd/TABLAS-VALORES-IVD251.json), y los segmentos que define la
  versión (Q-MV-4), de sus tablas de atributos.
- ivd/validar_ivdst.py, para las versiones sin texto (Q-VD-1): estructura, obligatorios y longitudes cuentan como los da IRIS; una
  tabla que el esquema de IRIS trae vacía es aviso; una con valores queda para la lectura, sin decidir. Los segmentos que define
  la versión son los del esquema de IRIS de esa versión.
En las dos: la versión es el primer componente de MSH-12; la estructura se resuelve en esa versión (Lab.IVD.Validar), y MSH-9.3 da
«<versión>:<estructura>». Afirma cada sustitución.
  python3 ivd/hacer_validar_ivd.py"""
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIGEN = os.path.join(os.path.dirname(AQUI), "ivm", "validar_ivm.py")

COMUNES = [
    ("Lab.IV.Validar", "Lab.IVD.Validar", 3),
    ("mkdir -p /tmp/iv && cat > /tmp/iv/lote-entrada.jsonl", "mkdir -p /tmp/ivd && cat > /tmp/ivd/lote-entrada.jsonl", 1),
    ('Lote("/tmp/iv/lote-entrada.jsonl","/tmp/iv/lote-salida.jsonl")', 'Lote("/tmp/ivd/lote-entrada.jsonl","/tmp/ivd/lote-salida.jsonl")', 1),
    ('"cat", "/tmp/iv/lote-salida.jsonl"', '"cat", "/tmp/ivd/lote-salida.jsonl"', 1),
    ('def msh9_partes(segs):\n    return msh9(segs).split(separadores(segs)[1])\n',
     'def msh9_partes(segs):\n    return msh9(segs).split(separadores(segs)[1])\n\n\n'
     'def version_de(segs):\n'
     '    """etapa 32: la versión que declara el mensaje, el primer componente de MSH-12."""\n'
     '    fs, cs = separadores(segs)[:2]\n'
     '    p = segs[0].split(fs) if segs and segs[0].startswith("MSH") else []\n'
     '    return p[11].split(cs)[0] if len(p) > 11 else ""\n', 1),
    ('    # las estructuras: MSH-9.3 y la del esquema (0354)\n'
     '    tipos = sorted({"_".join(msh9_partes(m["segs"])[:2]) for m in msgs})\n'
     '    res = lote([{"k": "r|" + t, "op": "resolver", "tipo": t} for t in tipos])\n'
     '    resuelto = {t: res["r|" + t].get("doctype") or "" for t in tipos}\n',
     '    # etapa 32: la versión de cada mensaje (el primer componente de MSH-12) y sus estructuras, en esa versión: MSH-9.3 y la\n'
     '    # del esquema (0354); y los segmentos que trae el esquema de IRIS de cada versión\n'
     '    for m in msgs:\n'
     '        m["version"] = version_de(m["segs"])\n'
     '        if m["version"] not in VERSIONES:\n'
     '            raise SystemExit("PARADA: %s declara la versión %r, que este conductor no lee" % (m["id"], m["version"]))\n'
     '    tipos = sorted({(m["version"], "_".join(msh9_partes(m["segs"])[:2])) for m in msgs})\n'
     '    vers = sorted({m["version"] for m in msgs})\n'
     '    res = lote([{"k": "r|%s|%s" % vt, "op": "resolver", "tipo": vt[1], "version": vt[0]} for vt in tipos] +\n'
     '               [{"k": "s|" + v, "op": "segmentos", "version": v} for v in vers])\n'
     '    resuelto = {vt: res["r|%s|%s" % vt].get("doctype") or "" for vt in tipos}\n'
     '    for v in vers:\n'
     '        if not res["s|" + v].get("segmentos"):\n'
     '            raise SystemExit("PARADA: IRIS no trae el esquema de la versión %s" % v)\n'
     '        SEGV.setdefault(v, set(res["s|" + v]["segmentos"]))   # la 2.5.1 ya los trae de su texto\n', 1),
    ('        esq = resuelto["_".join(comps[:2])]\n        m["doctype_msh93"] = ("2.5:" + e3) if e3 else None\n',
     '        esq = resuelto[(m["version"], "_".join(comps[:2]))]\n'
     '        m["doctype_msh93"] = (m["version"] + ":" + e3) if e3 else None\n', 1),
    ('and t.segs[p["idx"] - 1][:3] not in SEG25 and not t.segs[p["idx"] - 1].startswith("Z")):',
     'and t.segs[p["idx"] - 1][:3] not in SEGV[t.msg["version"]] and not t.segs[p["idx"] - 1].startswith("Z")):', 1),
    ('                    # etapa 31 (Q-MV-4): IRIS echa en falta un segmento justo donde hay uno que v2.5 no define; el que sobra\n',
     '                    # etapa 31 (Q-MV-4; en la 32, la versión del mensaje): IRIS echa en falta un segmento justo donde hay uno\n'
     '                    # que su versión no define; el que sobra\n', 1),
    ('                        errores.append(clasificar(dict(p), m["segs"]))\n',
     '                        errores.append(clasificar(dict(p), m["segs"]))\n'
     '                        # etapa 32: si la versión del mensaje define el segmento (para la lectura: Q-MV-2 y Q-MV-4)\n'
     '                        errores[-1]["seg_definido_en_la_version"] = errores[-1].get("seg") in SEGV[m["version"]]\n', 1),
    ('fila = {k: m[k] for k in ("id", "corpus", "sha256", "msh9",', 'fila = {k: m[k] for k in ("id", "corpus", "sha256", "version", "msh9",', 1),
    ('"campo sin atributos en estructuras_25.json: a lectura"', '"campo sin atributos en la tabla de campos de la versión: a lectura"', 1),
    ('"sistema de codificación que la 0396 de v2.5 no trae (Q-IV-D-11: cuenta)"',
     '"sistema de codificación que la 0396 de la versión no trae (Q-IV-D-11: cuenta)"', 1),
    ('    c = p["clase_iris"]\n    p["cuenta"], p["motivo"] = True, None\n',
     '    c = p["clase_iris"]\n    p["cuenta"], p["motivo"] = True, None\n'
     '    if SIN_TEXTO and c in ("R", "L"):              # etapa 32 (Q-VD-1): sin texto de la versión, como lo da IRIS\n'
     '        p["clase"], p["motivo"] = c, "según IRIS, sin texto de la versión (Q-VD-1)"\n'
     '        return p\n'
     '    if SIN_TEXTO and c == "T":\n'
     '        p["tipo_tabla"], p["tabla_en_conflicto"] = None, False\n'
     '        if p["tabla_vacia_en_iris"]:\n'
     '            p["clase"], p["cuenta"], p["motivo"] = "T_USR", False, "tabla sin valores en el esquema de IRIS (tabla_usuario_vacia)"\n'
     '        else:\n'
     '            p["clase"], p["motivo"] = "T_HL7", "tabla con valores en el esquema de IRIS, sin texto de la versión: a lectura, sin decidir (Q-VD-1)"\n'
     '        return p\n', 1),
]

CARGA = ('EST = json.load(open(os.path.join(FASE, "estructuras_25.json"), encoding="utf-8"))["campos"]\n'
         'TIPOS = json.load(open(os.path.join(FASE, "iv", "TABLAS-TIPO-IV.json"), encoding="utf-8"))["tablas"]\n'
         '_TV = json.load(open(os.path.join(PRIV, "iv", "TABLAS-VALORES-IV.json"), encoding="utf-8"))\n')
SEG = ('# etapa 31 (Q-MV-4): los segmentos que el texto de v2.5 define, por su tabla de atributos\n'
       'TXT25 = os.path.normpath(os.path.join(FASE, "..", "estandares", "hl7v2", "HL7_Messaging_v25", "txt"))\n'
       'SEG25 = set()\n'
       'for _f in sorted(glob.glob(os.path.join(TXT25, "*.txt"))):\n'
       '    for _l in open(_f, encoding="utf-8", errors="replace"):\n'
       '        _m = re.search(r"HL7 Attribute Table\\s*[-–]\\s*([A-Z][A-Z0-9]{2})\\b", _l)\n'
       '        if _m:\n'
       '            SEG25.add(_m.group(1))\n'
       'assert {"MSH", "PID", "PV1", "RXA", "TXA"} <= SEG25 and "ARV" not in SEG25, "no se leyeron las tablas de atributos de v2.5"\n')
CABECERA_31 = '"""Etapa 31: el conductor de la etapa 30 con la regla de Q-MV-4'

D251 = [
    (CABECERA_31,
     '"""Etapa 32, la 2.5.1 (Q-VD-2): el conductor de la 31 con la versión de cada mensaje y el texto de v2.5.1, hecho con\n'
     'ivd/hacer_validar_ivd.py. Lo que sigue es la cabecera de la 31.\n' + CABECERA_31[3:], 1),
    (CARGA,
     '# etapa 32 (Q-VD-2): el texto de v2.5.1, por la carpeta de enlaces con los nombres de v2.5 (ivd/hacer_vista_251.sh)\n'
     'sys.path.insert(0, os.path.join(FASE, "ivd"))\n'
     'import texto_ivd as TX  # noqa: E402\n'
     'TXTV = os.path.normpath(os.path.join(FASE, "..", "estandares", "hl7v2", "HL7_Messaging_v251", "vista_v25"))\n'
     'SIN_TEXTO = False\n'
     'VERSIONES = {"2.5.1"}\n'
     'EST = TX.est(TXTV, json.load(open(os.path.join(FASE, "estructuras_25.json"), encoding="utf-8"))["campos"])\n'
     'TIPOS = json.load(open(os.path.join(FASE, "ivd", "TABLAS-TIPO-IVD251.json"), encoding="utf-8"))["tablas"]\n'
     '_TV = json.load(open(os.path.join(PRIV, "ivd", "TABLAS-VALORES-IVD251.json"), encoding="utf-8"))\n', 1),
    (SEG,
     '# etapa 32 (Q-MV-4 en la versión del mensaje): los segmentos que define la 2.5.1, por las tablas de atributos de su texto\n'
     'SEGV = {"2.5.1": TX.segmentos_definidos(TXTV)}\n'
     'assert {"MSH", "PID", "PV1", "RXA", "TXA"} <= SEGV["2.5.1"] and "ARV" not in SEGV["2.5.1"], "no se leyó el texto de v2.5.1"\n'
     'assert all(EST[s]["atributos"] for s in EST), "la tabla de campos de v2.5.1 tiene segmentos vacíos"\n', 1),
]
DST = [
    (CABECERA_31,
     '"""Etapa 32, las versiones sin texto en el laboratorio (Q-VD-1): el conductor de la 31 con la versión de cada mensaje y sin\n'
     'tablas del texto, hecho con ivd/hacer_validar_ivd.py. Lo que sigue es la cabecera de la 31.\n' + CABECERA_31[3:], 1),
    (CARGA,
     '# etapa 32 (Q-VD-1): sin texto de la versión, no hay tabla de campos ni tablas del estándar; cuenta lo que da IRIS\n'
     'SIN_TEXTO = True\n'
     'VERSIONES = {"2.3", "2.4", "2.6", "2.8"}\n'
     'EST, TIPOS, _TV = {}, {}, {"valores": {}, "patrones": {}}\n', 1),
    (SEG,
     '# etapa 32 (Q-MV-4 en la versión del mensaje): sin texto, los segmentos que trae el esquema de IRIS de cada versión (se\n'
     '# piden a IRIS al empezar la corrida)\n'
     'SEGV = {}\n', 1),
]


def hacer(destino, cambios):
    t = open(ORIGEN, encoding="utf-8").read()
    for viejo, nuevo, veces in cambios:
        assert t.count(viejo) == veces, "no está %d veces: %r (%d)" % (veces, viejo[:80], t.count(viejo))
        t = t.replace(viejo, nuevo)
    assert "SEG25" not in t and "2.5:" not in t.replace('"2.5:"', ""), "queda algo de v2.5 sin cambiar"
    open(destino, "w", encoding="utf-8").write(t)
    print("%s: escrito desde ivm/validar_ivm.py con %d cambios" % (os.path.relpath(destino, os.path.dirname(AQUI)), len(cambios)))


hacer(os.path.join(AQUI, "validar_ivd251.py"), D251 + COMUNES)
hacer(os.path.join(AQUI, "validar_ivdst.py"), DST + COMUNES)
