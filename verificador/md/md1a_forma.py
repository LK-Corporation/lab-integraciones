#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 26, MD1-a (md/diseno-md.md §11): el punto `mdm_conv` y el emparejador sobre la salida real, SIN perfil.

Antes de las pruebas en rojo y del código. Aquí no se toca el juez: el PE se construye en memoria con PE._pe (el contrato del
§2.1), se registra solo dentro de este proceso para pasar `_afirmar` y comprobar que `contrato(PUNTOS["mdm"])` no cambia, y el
emparejador es un prototipo del §2.2 (grupos, DocumentReference por TXA, ServiceRequest por grupo de orden, Patient y Encounter)
que MD1-d pasa a conversion_mdm.py. Sobre las salidas guardadas de E-MD-3 (los MDM^T02 de las muestras públicas, 38 por
conversor) anota la forma de lo que devuelve cada conversor: tipos de recurso, referencias, la DocumentReference y su `content`.
Esa forma es para el informe (MD1.md); no toca el perfil. Solo biblioteca estándar.

  python3 md/md1a_forma.py <carpeta mdpre> <salida.json>"""
import base64
import binascii
import collections
import glob
import json
import os
import re
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [FASE]
_argv, sys.argv = sys.argv, ["x", "--silencio"]
import conversion as CV  # noqa: E402
import estructuras_hl7 as EH  # noqa: E402
import mapeador_referencia as MR  # noqa: E402
import puntos_entrada as PE  # noqa: E402
sys.argv = _argv

_t, _f, _d, _reps, _comp, _sub, _seg = CV._t, CV._f, CV._d, CV._reps, CV._comp, CV._sub, CV._seg
_codigos, _valores = CV._codigos, CV._valores
TIPOS = ("Patient", "Encounter", "DocumentReference", "ServiceRequest")


# ---------------------------------------------------------------------------- (1) el PE del §2.1, en memoria
def pe_mdm_conv():
    return PE._pe(
        "mdm_conv", 0, {"MDM": {"T02": "MDM_T02"}},
        PE.MSH_CONSUMIDOS | {("PID", 3), ("PID", 5), ("PID", 7), ("PID", 8), ("PID", 11), ("PID", 13), ("PID", 14), ("PID", 16),
                             ("PID", 29), ("PID", 30),
                             ("PV1", 2), ("PV1", 3), ("PV1", 4), ("PV1", 6), ("PV1", 7), ("PV1", 8), ("PV1", 10), ("PV1", 11), ("PV1", 14),
                             ("PV1", 17), ("PV1", 19), ("PV1", 36), ("PV1", 44), ("PV1", 45),
                             ("ORC", 2), ("ORC", 3), ("OBR", 2), ("OBR", 3), ("OBR", 4),
                             ("TXA", 2), ("TXA", 3), ("TXA", 6), ("TXA", 9), ("TXA", 10), ("TXA", 12), ("TXA", 16), ("TXA", 17),
                             ("TXA", 18), ("TXA", 19), ("OBX", 2), ("OBX", 5), ("NTE", 3)},
        [("MSH", 10, "consumido"), ("PID", 3, "consumido"), ("PID", 5, "consumido"), ("TXA", 2, "consumido"), ("TXA", 12, "consumido"),
         ("TXA", 17, "consumido"), ("PV1", 2, "consumido"), ("MSH", 7, "estricto"), ("EVN", 2, "estricto"), ("OBX", 3, "estricto")],
        [("MSH", 7, "ts", "estricto"), ("MSH", 18, "0211", "estricto"), ("EVN", 1, "0003", "estricto"), ("EVN", 2, "ts", "estricto"),
         ("PID", 7, "ts", "consumido"), ("PID", 8, "0001", "consumido"), ("PID", 29, "ts", "consumido"), ("PID", 30, "0136", "consumido"),
         ("PV1", 2, "0004", "consumido"), ("PV1", 44, "ts", "consumido"), ("PV1", 45, "ts", "consumido"), ("TXA", 1, "nm", "estricto"),
         ("TXA", 3, "0191", "consumido"), ("TXA", 6, "ts", "consumido"), ("TXA", 17, "0271", "consumido"), ("TXA", 18, "0272", "consumido"),
         ("TXA", 19, "0273", "consumido"), ("OBX", 2, "0125", "consumido"), ("OBX", 11, "0085", "estricto")],
        "MDM^T02 convertido por un tercero (HL7 v2 -> FHIR): solo transformación, sin acuse; perfil «guía» de DocumentReference (S-MD-1..17).",
        solo_transformacion=True, familia="mdm")


def comprobar_pe():
    antes = json.dumps(PE.contrato(PE.PUNTOS["mdm"]), sort_keys=True, ensure_ascii=False)
    pe = pe_mdm_conv()
    PE.PUNTOS["mdm_conv"] = pe
    try:
        PE._afirmar()
        despues = json.dumps(PE.contrato(PE.PUNTOS["mdm"]), sort_keys=True, ensure_ascii=False)
        ok = {"afirmar": True, "MDM_T02 en la gramática": "MDM_T02" in EH.GRAMATICAS, "contrato mdm igual": antes == despues,
              "tipos": pe["tipos"], "longitudes TXA": sorted("%s-%d" % c for c in pe["longitudes"] if c[0] == "TXA")}
    finally:
        del PE.PUNTOS["mdm_conv"]
    return pe, ok


# ---------------------------------------------------------------------------- (2) el prototipo del emparejador (§2.2)
def grupos(m):
    """Grupos de orden (ORC abre; OBR sin ORC abre con nota) y documentos (TXA abre; sus OBX y, a cada OBX, sus NTE)."""
    ordenes, docs, fuera, ctx, nte_suelta = [], [], 0, None, 0
    for s in m.segs:
        n = s.split(m.f)[0]
        if n == "ORC":
            ordenes.append({"orc": s, "obr": None, "nte": [], "sin_orc": False})
            ctx = "orden"
        elif n == "OBR":
            if ordenes and ctx == "orden" and ordenes[-1]["obr"] is None:
                ordenes[-1]["obr"] = s
            else:
                ordenes.append({"orc": None, "obr": s, "nte": [], "sin_orc": True})
            ctx = "orden"
        elif n == "TXA":
            docs.append({"txa": s, "obx": []})
            ctx = "txa"
        elif n == "OBX":
            if docs:
                docs[-1]["obx"].append({"seg": s, "nte": []})
                ctx = "obx"
            else:
                fuera += 1
                ctx = "fuera"
        elif n == "NTE":
            if ctx == "orden":
                ordenes[-1]["nte"].append(s)
            elif ctx == "obx":
                docs[-1]["obx"][-1]["nte"].append(s)
            else:
                nte_suelta += 1
        elif n in ("MSH", "SFT", "EVN", "PID", "PD1", "PV1", "PV2"):
            ctx = None
    return {"ordenes": ordenes, "docs": docs, "obx_fuera_txa": fuera, "nte_suelta": nte_suelta}


def _mi(e):
    x = e["r"].get("masterIdentifier")
    return (x.get("value") or "") if isinstance(x, dict) else ""


def emparejar(m, entries):
    out = {"recursos": [], "sobrantes": [], "ambiguo": [], "duplicadas": {}, "fallos": []}
    top = [e for e in entries if e["padre"] is None]
    usados = set()

    def rol(nombre, origen, e, por, n):
        out["recursos"].append({"rol": nombre, "origen": origen, "entry": e, "fullUrl": e["fullUrl"] if e else None,
                                "emparejado_por": por, "candidatos": n})
        if e:
            usados.add(e["i"])

    # Patient: la parte común de conversion.emparejar (el prototipo la llama tal cual con la familia adt y se queda con el Patient)
    com = CV.emparejar(m, entries, "adt")
    pat_rol = next((x for x in com["recursos"] if x["rol"] == "Patient#1"), None)
    pat = pat_rol["entry"] if pat_rol else None
    if pat_rol:
        rol("Patient#1", "PID", pat, pat_rol["emparejado_por"], pat_rol["candidatos"])
    enc = next((x for x in com["recursos"] if x["rol"] == "Encounter#1"), None)
    if enc:
        rol("Encounter#1", "PV1", enc["entry"], enc["emparejado_por"], enc["candidatos"])
    out["ambiguo"] += [a for a in com["ambiguo"]]
    g = grupos(m)
    docs, ordenes = g["docs"], g["ordenes"]
    drs = [e for e in top if e["tipo"] == "DocumentReference"]
    claves = {i: (_t(m, _f(m, d["txa"], 12), 1), _d(m, _f(m, d["txa"], 16)), _t(m, _f(m, d["txa"], 2), 1)) for i, d in enumerate(docs, 1)}
    asignadas, por_i, libres = {}, {}, list(drs)
    if len(docs) == 1:
        t12 = claves[1][0]
        c = [e for e in drs if t12 and (t12 in _mi(e) or t12 in _valores(e["r"]))]
        if len(c) == 1:
            asignadas[1], por_i[1] = c[0], "master"
        elif drs:
            asignadas[1], por_i[1] = (c or drs)[0], ("unico" if len(drs) == 1 else "orden")
        if asignadas.get(1):
            libres.remove(asignadas[1])
    else:
        for paso in ("master", "archivo", "tipo", "orden"):
            for i, (t12, t16, t2) in claves.items():
                if i in asignadas:
                    continue
                if paso == "master":
                    c = [e for e in libres if t12 and (t12 in _mi(e) or t12 in _valores(e["r"]))]
                elif paso == "archivo":
                    c = [e for e in libres if t16 and t16 in _valores(e["r"])]
                elif paso == "tipo":
                    c = [e for e in libres if t2 and t2 in {x[1] for x in _codigos(e["r"].get("type"))}]
                else:
                    c = libres[:1] if (len(drs) == len(docs) or len(drs) == 1) and libres else []
                if len(c) > 1:
                    out["ambiguo"].append("DocumentReference#%d" % i)
                    asignadas[i] = None
                elif c:
                    libres.remove(c[0])
                    asignadas[i], por_i[i] = c[0], paso
    for i in claves:
        rol("DocumentReference#%d" % i, "TXA %d" % i, asignadas.get(i), por_i.get(i), len(drs))
    for e in libres:
        dueno = 1 if len(docs) == 1 else next((i for i, (t12, t16, _) in claves.items() if asignadas.get(i) and
                                               ((t12 and (t12 in _mi(e) or t12 in _valores(e["r"]))) or (t16 and t16 in _valores(e["r"])))), None)
        if dueno:
            out["duplicadas"].setdefault(dueno, []).append(e)
            out["sobrantes"].append({"resourceType": "DocumentReference", "fullUrl": e["fullUrl"], "motivo": "duplicado", "hecho": "TXA-12"})
        else:
            out["sobrantes"].append({"resourceType": "DocumentReference", "fullUrl": e["fullUrl"], "motivo": "inventado", "hecho": "TXA"})
        usados.add(e["i"])
    # ServiceRequest por grupo de orden
    srs = [e for e in top if e["tipo"] == "ServiceRequest"]
    referidos = set()
    for i in claves:
        d = asignadas.get(i)
        for ref in (((d["r"].get("context") or {}).get("related") or []) if d else []):
            x, _ = CV.resolver(entries, ref, d, "ServiceRequest")
            if x is not None:
                referidos.add(x["i"])
    sclaves = {}
    for i, o in enumerate(ordenes, 1):
        ids = {_t(m, _f(m, o["obr"], 2), 1), _t(m, _f(m, o["obr"], 3), 1), _t(m, _f(m, o["orc"], 2), 1), _t(m, _f(m, o["orc"], 3), 1)} - {""}
        sclaves[i] = (ids, _t(m, _f(m, o["obr"], 4), 1))
    sasig, spor, slibres = {}, {}, list(srs)
    for paso in ("identifier", "referencia", "codigo", "orden"):
        for i, (ids, cod) in sclaves.items():
            if i in sasig:
                continue
            con_cod = [e for e in slibres if cod and cod in {x[1] for x in _codigos(e["r"].get("code"))}]
            if paso == "identifier":                                 # DV-MD-1: gana quien comparte más números; empate, OBR-4
                puntos = {e["i"]: len(ids & _valores(e["r"])) for e in slibres}
                mx = max(puntos.values(), default=0)
                c = [e for e in slibres if mx and puntos[e["i"]] == mx]
                if len(c) > 1 and cod:
                    c = [e for e in c if cod in {x[1] for x in _codigos(e["r"].get("code"))}] or c
            elif paso == "referencia":
                c = [e for e in con_cod if e["i"] in referidos]
            elif paso == "codigo":
                c = con_cod
            else:
                c = slibres[:1] if len(srs) == len(ordenes) and slibres else []
            if len(c) > 1:
                out["ambiguo"].append("ServiceRequest#%d" % i)
                sasig[i] = None
            elif c:
                slibres.remove(c[0])
                sasig[i], spor[i] = c[0], paso
    for i in sclaves:
        rol("ServiceRequest#%d" % i, "ORC %d" % i, sasig.get(i), spor.get(i), len(srs))
    for e in slibres:
        out["sobrantes"].append({"resourceType": "ServiceRequest", "fullUrl": e["fullUrl"], "motivo": "inventado", "hecho": "ORC"})
        usados.add(e["i"])
    alc = CV._alcanzadas(entries, [x["entry"] for x in out["recursos"] if x["entry"]])
    otros = collections.Counter(e["tipo"] for e in top if e["i"] not in usados and e["i"] not in alc and e["tipo"] not in TIPOS)
    out["otros_tipos"] = dict(otros)
    out["alcanzados"] = dict(collections.Counter(e["tipo"] for e in entries if e["i"] in alc and e["tipo"] not in TIPOS))
    out["grupos"] = g
    return out


# ---------------------------------------------------------------------------- (3) la forma del contenido
PALABRA = re.compile(r"[^\W_]+")


def _palabras(s):
    return [w.casefold() for w in PALABRA.findall(s or "")]


def _subsecuencia(a, b):
    it = iter(b)
    return all(any(x == y for y in it) for x in a)


def _texto_obx(m, s):
    """Texto de un OBX TX/FT o un NTE-3 sin órdenes de formato y desescapado (forma; el perfil lo define en MD1-d)."""
    e = re.escape(m.e)
    sin = re.sub(e + r"(\.[^" + e + r"]*|H|N|Z[^" + e + r"]*|C[^" + e + r"]*|M[^" + e + r"]*)" + e, " ", s)
    return m.desescapa(sin)


def _forma_attachment(a, entries, desde):
    f = {"claves": sorted(k for k in a if k not in ("extension",)), "contentType": a.get("contentType")}
    if "data" in a:
        d = a["data"]
        try:
            b = base64.b64decode(re.sub(r"\s", "", d or ""), validate=True)
            f["data"] = "base64"
            f["octetos"] = len(b)
            try:
                b.decode("utf-8")
                f["utf8"] = True
            except UnicodeDecodeError:
                f["utf8"] = False
        except (binascii.Error, ValueError):
            f["data"] = "no_base64"
    if "url" in a:
        x, forma = CV.resolver(entries, {"reference": a["url"]}, desde)
        f["url"] = {"forma": forma, "a": x["tipo"] if x else None, "absoluta": bool(re.match(r"^[a-z][a-z0-9+.-]*:", a["url"] or ""))}
    return f


def forma(m, b, entries, lec):
    """Lo que el informe anota de un Bundle de MDM^T02 (sin datos personales: tipos, claves y recuentos)."""
    g = lec["grupos"]
    roles = {x["rol"]: x for x in lec["recursos"]}
    out = {"tipos": dict(collections.Counter(e["tipo"] for e in entries if e["padre"] is None)),
           "contained": dict(collections.Counter(e["tipo"] for e in entries if e["padre"] is not None)),
           "fullUrl": sorted({("urn:uuid" if (e["fullUrl"] or "").startswith("urn:uuid:") else "Tipo/id" if re.match(r"^[A-Z][A-Za-z]+/", e["fullUrl"] or "")
                               else "otra" if e["fullUrl"] else "ninguna") for e in entries if e["padre"] is None}),
           "txa": len(g["docs"]), "ordenes": len(g["ordenes"]), "obx_por_tipo": dict(collections.Counter(_d(m, _f(m, o["seg"], 2)).upper()
                                                                                                           for d in g["docs"] for o in d["obx"])),
           "nte_obx": sum(len(o["nte"]) for d in g["docs"] for o in d["obx"]), "obx_fuera_txa": g["obx_fuera_txa"],
           "emparejamiento": {k: v["emparejado_por"] for k, v in roles.items()}, "ambiguo": lec["ambiguo"],
           "sobrantes": [(s["resourceType"], s["motivo"]) for s in lec["sobrantes"]], "otros_tipos": lec["otros_tipos"],
           "alcanzados": lec["alcanzados"], "documentos": []}
    for i, d in enumerate(g["docs"], 1):
        x = roles.get("DocumentReference#%d" % i)
        e = x["entry"] if x else None
        doc = {"emparejada": bool(e), "duplicadas": len(lec["duplicadas"].get(i, []))}
        if e:
            r = e["r"]
            ctx = r.get("context") or {}
            doc["elementos"] = sorted(k for k in r if k not in ("resourceType", "id", "meta", "text"))
            doc["context"] = sorted(ctx)
            doc["status"], doc["docStatus"] = r.get("status"), r.get("docStatus")
            doc["type.system"] = sorted({c[0] or "" for c in _codigos(r.get("type"))})
            doc["securityLabel.system"] = sorted({c[0] or "" for x in r.get("securityLabel") or [] for c in _codigos(x)})
            doc["status.extension"] = sorted(x.get("url") for x in (r.get("_status") or {}).get("extension") or [] if isinstance(x, dict))
            doc["author"] = [CV.resolver(entries, a, e)[1:] + ((CV.resolver(entries, a, e)[0] or {}).get("tipo"),) for a in r.get("author") or []]
            doc["authenticator"] = (CV.resolver(entries, r.get("authenticator"), e)[1], (CV.resolver(entries, r.get("authenticator"), e)[0] or {}).get("tipo")) if r.get("authenticator") else None
            doc["subject"] = CV.resolver(entries, r.get("subject"), e, "Patient")[1] if r.get("subject") else None
            doc["subject_es_patient1"] = bool(r.get("subject")) and CV.resolver(entries, r.get("subject"), e, "Patient")[0] is (roles.get("Patient#1") or {}).get("entry")
            doc["related"] = [((CV.resolver(entries, x, e)[0] or {}).get("tipo"), CV.resolver(entries, x, e)[1]) for x in ctx.get("related") or [] if isinstance(x, dict)]
            todas = [e] + lec["duplicadas"].get(i, [])
            atts = [(y, c.get("attachment")) for y in todas for c in y["r"].get("content") or [] if isinstance(c, dict)]
            doc["content"] = len(atts)
            doc["attachments"] = [_forma_attachment(a, entries, y) if isinstance(a, dict) else {"sin_attachment": True} for y, a in atts]
            textos = []
            for _, a in atts:
                if isinstance(a, dict) and a.get("data"):
                    try:
                        textos.append(base64.b64decode(re.sub(r"\s", "", a["data"]), validate=True).decode("utf-8", errors="replace"))
                    except (binascii.Error, ValueError):
                        textos.append(a["data"])
            llegada = []
            for o in d["obx"]:
                tipo = _d(m, _f(m, o["seg"], 2)).upper()
                v5 = _f(m, o["seg"], 5)
                if tipo in ("TX", "FT") and v5:
                    esp = _palabras(_texto_obx(m, " ".join(_reps(m, v5))))
                    entero = any(_subsecuencia(esp, _palabras(t)) for t in textos)
                    llegada.append((tipo, "entero" if entero else "partido" if _subsecuencia(esp, _palabras(" ".join(textos))) else "falta"))
                elif tipo == "ED" and v5:
                    rep = _reps(m, v5)[0]
                    ed4, ed5 = _t(m, rep, 4).upper(), _sub(m, _comp(m, rep, 5), 1)
                    datos = {a.get("data") for _, a in atts if isinstance(a, dict)}
                    llegada.append(("ED", ed4, "mismo_data" if ed5 and ed5 in datos else "vacio" if not ed5 else "otro"))
                elif tipo == "RP" and v5:
                    rp1 = _t(m, _reps(m, v5)[0], 1)
                    urls = {a.get("url") for _, a in atts if isinstance(a, dict)}
                    llegada.append(("RP", "url_igual" if rp1 in urls else "url_contiene" if any(rp1 and u and rp1 in u for u in urls) else "sin_url"))
                else:
                    llegada.append((tipo, "sin_destino" if tipo not in ("TX", "FT", "ED", "RP") else "vacio"))
                for n in o["nte"]:
                    t3 = _palabras(_texto_obx(m, " ".join(_reps(m, _f(m, n, 3)))))
                    if t3:
                        llegada.append(("NTE", "entero" if any(_subsecuencia(t3, _palabras(t)) for t in textos) else "falta"))
            doc["llegada"] = llegada
        out["documentos"].append(doc)
    out["srs"] = [{"emparejado_por": (roles.get("ServiceRequest#%d" % i) or {}).get("emparejado_por")} for i in range(1, len(g["ordenes"]) + 1)]
    return out


def main(carpeta, salida):
    pe, ok = comprobar_pe()
    res = {"pe": ok, "casos": {}, "resumen": {}}
    for conv in ("microsoft", "linuxforhealth"):
        res["casos"][conv] = {}
        resumen = collections.Counter()
        mayor = 0
        for f in sorted(glob.glob(os.path.join(carpeta, conv, "evidencias", conv, "muestras", "*.json"))):
            e = json.load(open(f, encoding="utf-8"))
            ms = MR.mensajes(e["mensaje"])
            m = ms[0]
            if PE.estructura_de(m, pe) is None:
                continue
            caso = os.path.splitext(os.path.basename(f))[0]
            s = e["conversion"]["salida"]
            if s["estado"] != "bundle":
                res["casos"][conv][caso] = {"estado": s["estado"]}
                resumen["estado " + s["estado"]] += 1
                continue
            mayor = max(mayor, len(s["bundle"]))
            entries, notas = CV.leer_bundle(s["bundle"], TIPOS)
            if entries is None:
                res["casos"][conv][caso] = {"lectura": notas}
                resumen["ilegible"] += 1
                continue
            lec = emparejar(m, entries)
            fo = forma(m, s["bundle"], entries, lec)
            res["casos"][conv][caso] = fo
            resumen["bundle"] += 1
            resumen["ambiguo"] += bool(fo["ambiguo"])
            resumen["DocumentReference=%d" % fo["tipos"].get("DocumentReference", 0)] += 1
            for d in fo["documentos"]:
                resumen["doc emparejada" if d["emparejada"] else "doc ausente"] += 1
                for a in d.get("attachments", []):
                    resumen["attachment data=%s" % a.get("data")] += 1
                    resumen["attachment contentType=%s" % a.get("contentType")] += 1
                    if "url" in a:
                        resumen["attachment url->%s" % (a["url"]["a"] or a["url"]["forma"])] += 1
                for l in d.get("llegada", []):
                    resumen["llegada %s" % "/".join(l)] += 1
                for k in ("status", "docStatus"):
                    resumen["%s=%s" % (k, d.get(k))] += 1
                resumen["subject=%s" % d.get("subject")] += 1
                resumen["context=%s" % (",".join(d.get("context") or []) or "-")] += 1
                el = d.get("elementos") or []
                resumen["type=%s" % ("-" if "type" not in el else ",".join(x or "sin system" for x in d.get("type.system") or []) or "sin coding")] += 1
                for k in ("masterIdentifier", "identifier", "date", "author", "authenticator", "securityLabel", "description", "content"):
                    resumen["elemento %s=%s" % (k, "sí" if k in el else "no")] += 1
                resumen["content: %d attachments" % d.get("content", 0)] += 1
                for a in d.get("attachments", []):
                    resumen["attachment claves=%s" % ",".join(a.get("claves") or ["-"])] += 1
                resumen["related=%s" % (",".join(sorted({x[0] or "rota" for x in d.get("related") or []})) or "-")] += 1
            for sr in fo["srs"]:
                resumen["SR %s" % sr["emparejado_por"]] += 1
            for t, n in fo["otros_tipos"].items():
                resumen["otros_tipos %s" % t] += n
            for t, n in fo["alcanzados"].items():
                resumen["alcanzado %s" % t] += n
            for x in fo["fullUrl"]:
                resumen["fullUrl %s" % x] += 1
            for x in fo["sobrantes"]:
                resumen["sobrante %s %s" % x] += 1
        resumen["bundle mayor (caracteres)"] = mayor
        res["resumen"][conv] = dict(sorted(resumen.items()))
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps(res["pe"], ensure_ascii=False))
    for conv, r in res["resumen"].items():
        print("== %s" % conv)
        for k, v in r.items():
            print("  %-60s %s" % (k, v))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
