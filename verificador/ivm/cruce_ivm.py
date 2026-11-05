#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 31: el cruce de las muestras con las nuevas publicadas que se apoyan en ellas, y todas las cifras del resultado.
- Las nuevas con muestras: L-1, L-11 y L-22 (estudio de conversores: las muestras de sus ejemplos, como en la 30, incompleto) y
  VX-M14 y VX-M15 (VXU: las muestras que nombra su clase). MD-M5 se apoya en su hallazgo H13, sin muestras.
- Su apoyo, sumado: el del laboratorio (iv/CRUCE-IV.json, etapa 30) y el de muestras (ivm/VEREDICTOS-IVM.jsonl), cada mensaje con
  el estado de la 30: válido, inválido por una regla que toca el campo del hallazgo, inválido por otra o sin decidir.
- La previsión sellada (ivm/PREVISION-IVM.json y la de Jev), frente a lo medido.
  python3 ivm/cruce_ivm.py <publicación>/verificador <corpus de muestras> <CRUCE-IVM.json> <CIFRAS-IVM.json>"""
import collections
import glob
import json
import os
import re
import sys

VER, CORPUS, SAL_C, SAL_F = sys.argv[1:5]
AQUI = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(AQUI)
VM = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(AQUI, "VEREDICTOS-IVM.jsonl"), encoding="utf-8")}
VL = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(FASE, "iv", "VEREDICTOS-IV.jsonl"), encoding="utf-8")}
C30 = {n["id"]: n for n in json.load(open(os.path.join(FASE, "iv", "CRUCE-IV.json"), encoding="utf-8"))["nuevas"]}
F = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(FASE, "..", "privado", "ivm", "FILAS-IVM.jsonl"), encoding="utf-8")}
P = json.load(open(os.path.join(AQUI, "PREVISION-IVM.json"), encoding="utf-8"))["prevision"]


def lugar(e):
    c, s, f, t = e["lugar"].split("|")
    return "%s-%s" % (s, f) if f else s


def msh12(i):
    """La versión que declara la muestra en MSH-12 (con los separadores de MSH-1 y MSH-2)."""
    segs = re.split(r"[\r\n]+", open(os.path.join(CORPUS, i), encoding="utf-8").read())
    p = segs[0].split(segs[0][3]) if segs and len(segs[0]) > 3 else []
    return (p[11].split(segs[0][4])[0] if len(p) > 11 else "?") or "?"


def estado(v, campos):
    if v is None:
        return "no_encontrado", []
    t = [e for e in v["sostenidos"] if any(lugar(e) == x or ("-" not in x and lugar(e).split("-")[0] == x) for x in campos)]
    if t:
        return "invalido_en_su_campo", sorted({lugar(e) for e in t})
    if v["sostenidos"]:
        return "invalido_por_otra_regla", sorted({lugar(e) for e in v["sostenidos"]})
    if v["no_decidibles"]:
        return "no_decidible", sorted({e["lugar"] for e in v["no_decidibles"]})
    return "valido", []


CV = {c["id"]: c for c in json.load(open(os.path.join(VER, "cv", "CLASES-CV3.json"), encoding="utf-8"))["clases"]}
VX = {c["id"]: c for c in json.load(open(os.path.join(VER, "vx", "CLASES-VX3.json"), encoding="utf-8"))["clases"]}
muestras = {}
for i in ("L-1", "L-11", "L-22"):
    muestras[i] = ["cv/%s.hl7" % m for m in CV[i]["ejemplos"]["muestras"]]
for i in ("VX-M14", "VX-M15"):
    casos = VX[i]["casos"]
    completos = re.findall(r"\blfh-(\w+__L\d+)\b", casos)              # «muestra lfh-FHIRConverterTest__L136»: exacta
    sueltos = re.findall(r"(?<![_\w])L\d+\b", re.sub(r"\blfh-\w+__L\d+\b", "", casos))   # «muestras L212, L256…»
    fich = ["vxu/lfh-%s.hl7" % n for n in completos]
    for n in sueltos:
        hay = sorted(os.path.relpath(p, CORPUS) for p in glob.glob(os.path.join(CORPUS, "vxu", "lfh-*__%s.hl7" % n)))
        assert len(hay) == 1, "%s: «%s» casa con %s" % (i, n, hay)    # un número suelto tiene que ser de una sola clase
        fich += hay
    muestras[i] = fich
nuevas = []
for i, ms in muestras.items():
    n30 = C30[i]
    lab = [{"mensaje": d["mensaje"], "estado": d["estado"]} for d in n30["detalle"]]
    mus = []
    for m in ms:
        s, reglas = estado(VM.get(m), n30["campos"])
        mus.append({"mensaje": m, "msh12": msh12(m) if VM.get(m) else None, "estado": s, "reglas": reglas, "aparte": sorted({e["lugar"] for e in (VM.get(m) or {}).get("aparte", [])})})
    todos = [x["estado"] for x in lab + mus if x["estado"] != "no_encontrado"]
    nuevas.append({"id": i, "campos": n30["campos"], "apoyo_laboratorio": lab, "apoyo_muestras": mus,
                   "muestras_no_encontradas": [x["mensaje"] for x in mus if x["estado"] == "no_encontrado"],
                   "con_algun_valido": "valido" in todos,
                   "afectada": bool(todos) and all(s == "invalido_en_su_campo" for s in todos),
                   "todo_invalido": bool(todos) and all(s.startswith("invalido") for s in todos),
                   # como en la 30 (iv/cruce_iv.py), con el apoyo del laboratorio y el de muestras juntos
                   "estado": ("afectada" if todos and all(s == "invalido_en_su_campo" for s in todos) else
                              "tocada" if any(s == "invalido_en_su_campo" for s in todos) else "intacta"),
                   "muestras_por_estado": dict(collections.Counter(x["estado"] for x in mus))})
json.dump({"nuevas": nuevas}, open(SAL_C, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# las cifras
por = collections.defaultdict(collections.Counter)
clases, aparte_m, mens_aparte = collections.Counter(), collections.Counter(), 0
for v in VM.values():
    por[v["corpus"]][v["veredicto_sostenido"]] += 1
    for e in v["sostenidos"]:
        clases[e["lugar"].split("|")[0]] += 1
    mens_aparte += bool(v.get("aparte"))
    for e in v.get("aparte", []):
        aparte_m[e["por"]] += 1
tot = collections.Counter()
for x in por.values():
    tot.update(x)
n = len(VM)
cif = {"n": n, "distintas": len({f["sha256"] for f in json.load(open(os.path.join(CORPUS, "CORPUS-IV.json"), encoding="utf-8"))["filas"]}),
       "total": dict(tot), "por_grupo": {k: dict(x) for k, x in sorted(por.items())}, "errores_sostenidos_por_clase": dict(clases),
       "muestras_con_algo_aparte": mens_aparte, "aparte_por_motivo": dict(aparte_m),
       "importadas_mal": sum(1 for f in F.values() if not f["importado"]["ok"]),
       "incompletas": sum(1 for f in F.values() for x in f["variantes"].values() if x["incompleto"]),
       "nuevas": {"n": len(nuevas), "con_algun_valido": sum(x["con_algun_valido"] for x in nuevas),
                  "sin_ningun_valido": sorted(x["id"] for x in nuevas if not x["con_algun_valido"]),
                  "todo_invalido": sorted(x["id"] for x in nuevas if x["todo_invalido"]),
                  "afectadas": sorted(x["id"] for x in nuevas if x["afectada"])}}
# lo que pidió la revisión a ciegas: qué hace inválidas a las muestras, qué pasadas quedaron sin leer en la variante que manda, qué
# llevan aparte las válidas, las versiones declaradas y los ficheros que no entran
def principal(f):
    vs = f["variantes"]
    m = vs.get("msh93")
    if m and vs.get("esquema") and any("no DocType set" in (p.get("crudo") or "") for p in m["errores"]):
        return vs["esquema"]
    return m or vs.get("esquema") or vs.get("ninguna")


causa = collections.Counter()
for v in VM.values():
    if v["veredicto_sostenido"] == "invalido":
        cl = {e["lugar"].split("|")[0] for e in v["sostenidos"]}
        causa["solo_longitudes" if cl == {"L"} else "obligatorios_o_estructura"] += 1
cif["invalidas_por_causa"] = dict(causa)
sin_leer = collections.Counter()
cortadas = []
for f in F.values():
    pv = principal(f)
    k = tuple(sorted(s for s, fin in pv["fines"].items() if fin in ("no_reconocido", "tope_alcanzado", "no_enmudecible", "no_importado")))
    sin_leer[" + ".join(k) if k else "ninguna"] += 1
    for s in k:
        if s != "dn":
            x = [p for p in pv["errores"] if p.get("pasada") == s and p["clase"] == "X"]
            cortadas.append({"muestra": f["id"], "pasada": s, "veredicto": VM[f["id"]]["veredicto_sostenido"],
                             "error": (x[-1].get("crudo") or "")[:200] if x else None})
cif["pasadas_sin_leer_en_la_variante_que_manda"] = dict(sin_leer)
cif["pasadas_cortadas_que_no_son_dn"] = cortadas
cif["variantes_con_alguna_pasada_sin_leer"] = cif.pop("incompletas")
cif["validas_con_algo_aparte"] = sum(1 for v in VM.values() if v["veredicto_sostenido"] == "valido" and v.get("aparte"))
cif["muestras_sin_estructura_en_msh93"] = sum(1 for v in VM.values() if any(e["lugar"] == "T_HL7|MSH|9|0354" for e in v["no_decidibles"]))
ver = collections.Counter(msh12(i) for i in VM)
cif["versiones_msh12"] = dict(sorted(ver.items()))
# lo que pidió la segunda revisión a ciegas
pv_ver = collections.defaultdict(collections.Counter)
for i, v in VM.items():
    pv_ver[msh12(i)][v["veredicto_sostenido"]] += 1
cif["veredicto_por_version"] = {k: dict(x) for k, x in sorted(pv_ver.items())}
m12 = lambda e: e["lugar"].startswith("T_HL7|MSH|12|")   # noqa: E731
solo12 = [i for i, v in VM.items() if v["veredicto_sostenido"] == "no_decidible" and all(m12(e) for e in v["no_decidibles"])]
cif["sin_decidir_solo_por_msh12"] = {"muestras": len(solo12), "por_version": dict(sorted(collections.Counter(msh12(i) for i in solo12).items()))}
cif["muestras_con_msh12_sin_decidir"] = sum(1 for v in VM.values() if any(m12(e) for e in v["no_decidibles"]))
cif["muestras_con_campos_sin_evaluar"] = sum(1 for f in F.values() if principal(f).get("campos_sin_evaluar"))
cif["validas_con_campos_sin_evaluar"] = sum(1 for f in F.values() if principal(f).get("campos_sin_evaluar")
                                            and VM[f["id"]]["veredicto_sostenido"] == "valido")
def valor_error(i, e):
    """-> (el valor del error, como lo leyó la lectura en el clon que validó IRIS; el separador de componentes, de MSH-2)."""
    assert e.get("leido") is not None, (i, e)
    return e["leido"], open(os.path.join(CORPUS, i), encoding="utf-8").read()[4]


sl = [(i, v) for i, v in VM.items() if v["veredicto_sostenido"] == "invalido" and {e["lugar"].split("|")[0] for e in v["sostenidos"]} == {"L"}]
err = [(i, e) for i, v in sl for e in v["sostenidos"]]
comp = sum(1 for i, e in err if (lambda vs: vs[1] in vs[0])(valor_error(i, e)))
cif["longitudes_en_las_invalidas_solo_por_longitud"] = {"muestras": len(sl), "errores": len(err), "valores_con_componentes": comp,
    "por_version": dict(sorted(collections.Counter(msh12(i) for i, v in sl).items()))}
# la pasada de repeticiones (no entra en el veredicto): el segmento que IRIS dice que trae más campos de los permitidos,
# frente a su tabla de atributos en el texto de v2.5
TXT25 = os.path.normpath(os.path.join(FASE, "..", "estandares", "hl7v2", "HL7_Messaging_v25", "txt"))
MAXC = collections.defaultdict(int)
FILA = re.compile(r"^\s+(\d+)\s+(\d+)\s+([A-Z][A-Z0-9]{1,2})\s+((?:\(B\)\s*)?(?:R|O|C|B|X|W|RE))\b(.*)$")
for _f in sorted(glob.glob(os.path.join(TXT25, "*.txt"))):
    _seg = None
    for _l in open(_f, encoding="utf-8", errors="replace"):
        _m = re.search(r"HL7 Attribute Table\s*[-–]\s*([A-Z][A-Z0-9]{2})\b", _l)
        if _m:
            _seg = _m.group(1)
            continue
        if _seg:
            _m = FILA.match(_l)
            if _m:
                MAXC[_seg] = max(MAXC[_seg], int(_m.group(1)))
            elif re.match(r"^\s*\d+\.\d+", _l) and MAXC[_seg]:
                _seg = None
assert MAXC["MSH"] == 21, MAXC["MSH"]
MAS = re.compile(r"segment (\d+):(\w+)\.\s+Segment has more fields than permitted")
rep = {"con_el_error": 0, "con_mas_campos_que_la_tabla_de_v25": 0, "con_valor_en_un_campo_de_mas": 0, "por_segmento": collections.Counter()}
for f in F.values():
    pv = principal(f)
    if pv["fines"].get("dn") != "no_reconocido":
        continue
    x = [p for p in pv["errores"] if p.get("pasada") == "dn"]
    m = MAS.search((x[-1].get("crudo") or "") if x else "")
    if not m:
        continue
    rep["con_el_error"] += 1
    segs = [s for s in re.split(r"[\r\n]+", open(os.path.join(CORPUS, f["id"]), encoding="utf-8").read()) if s]
    for e in pv["errores"]:                     # el clon estructural: lo que la pasada dm quitó, en orden
        if e.get("pasada") == "dm" and e.get("enmudecido") == "quitado":
            del segs[e["idx"] - 1]
    seg, q = m.group(2), segs[int(m.group(1)) - 1].split(segs[0][3])
    assert q[0] == seg, (f["id"], m.group(0), q[0])
    nc = len(q) if seg == "MSH" else len(q) - 1
    if nc > MAXC[seg]:
        rep["con_mas_campos_que_la_tabla_de_v25"] += 1
        rep["por_segmento"][seg] += 1
        rep["con_valor_en_un_campo_de_mas"] += any(c.strip() for c in q[MAXC[seg] + (0 if seg == "MSH" else 1):])
rep["por_segmento"] = dict(rep["por_segmento"].most_common())
cif["pasada_de_repeticiones"] = rep
cif["nuevas"]["por_estado"] = dict(collections.Counter(x["estado"] for x in nuevas))
PRIV = os.path.join(FASE, "..", "privado")
cif["ficheros_y_muestras"] = {g: {"ficheros": sum(len(os.listdir(os.path.join(PRIV, d, "muestras", s)))
                                              for s in ("ms", "lfh") if os.path.isdir(os.path.join(PRIV, d, "muestras", s))),
                                  "muestras": sum(1 for v in VM.values() if v["corpus"] == "muestras/" + g)}
                              for g, d in (("cv", "cv"), ("vxu", "vxu"), ("mdm", "mdm"))}
pct = lambda c: 100.0 * por[c]["valido"] / sum(por[c].values())   # noqa: E731
con = {}
for c, x in P["PVM1_validas_pct"].items():
    if not c.startswith("_"):
        con["PVM1 " + c] = {"previsto": x, "medido": round(pct(c), 1), "acierta": x[1] <= pct(c) <= x[2]}
for k, clave, val in (("PVM2_sin_decidir_pct_total", "PVM2 sin decidir", 100.0 * tot["no_decidible"] / n),
                      ("PVM3_invalidas_pct_total", "PVM3 inválidas", 100.0 * tot["invalido"] / n),
                      ("PVM4_muestras_con_algo_aparte_pct", "PVM4 con algo aparte", 100.0 * mens_aparte / n)):
    con[clave] = {"previsto": P[k], "medido": round(val, 1), "acierta": P[k][1] <= val <= P[k][2]}
sv = len(cif["nuevas"]["sin_ningun_valido"])
con["PVM5 nuevas sin ningún válido"] = {"previsto": P["PVM5_nuevas_con_muestras_sin_ningun_mensaje_valido_contando_las_muestras"],
                                        "medido": sv, "acierta": P["PVM5_nuevas_con_muestras_sin_ningun_mensaje_valido_contando_las_muestras"][1] <= sv <= P["PVM5_nuevas_con_muestras_sin_ningun_mensaje_valido_contando_las_muestras"][2]}
af = len(cif["nuevas"]["afectadas"])
con["PVM6 nuevas afectadas"] = {"previsto": P["PVM6_nuevas_afectadas"], "medido": af, "acierta": P["PVM6_nuevas_afectadas"][1] <= af <= P["PVM6_nuevas_afectadas"][2]}
pv = 100.0 * tot["valido"] / n
con["Jev: proporción válida"] = {"previsto": "entre el 20 % y el 50 %", "medido": round(pv, 1), "acierta": 20 <= pv <= 50}
con["Jev: nuevas sin ningún válido"] = {"previsto": "ninguna", "medido": sv, "acierta": sv == 0}
for k in ("PVM1 muestras/vxu", "PVM1 muestras/mdm", "PVM2 sin decidir", "PVM4 con algo aparte"):
    con[k]["intervalo_ancho"] = True          # un intervalo de más de 50 puntos: acertar dice poco
con["PVM5 nuevas sin ningún válido"]["intervalo_ancho"] = True   # de 0 a 5 de 5: todo lo posible; y la 30 ya dejaba sin
# ningún mensaje válido del laboratorio a VX-M14 y VX-M15, así que acertar dice poco
cif["prevision"] = con
cif["prevision_aciertos"] = "%d de %d" % (sum(x["acierta"] for x in con.values()), len(con))
json.dump(cif, open(SAL_F, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: cif[k] for k in ("n", "distintas", "total", "errores_sostenidos_por_clase", "muestras_con_algo_aparte",
                                      "nuevas", "prevision_aciertos")}, ensure_ascii=False))
for g, x in cif["por_grupo"].items():
    print("  %-14s %s" % (g, x))
for x in nuevas:
    print("  %-7s lab %s | muestras %s | no encontradas %s | algún válido %s" % (
        x["id"], dict(collections.Counter(d["estado"] for d in x["apoyo_laboratorio"])), x["muestras_por_estado"],
        x["muestras_no_encontradas"], x["con_algun_valido"]))
for k, x in con.items():
    print("  %-34s %-5s previsto %s, medido %s" % (k, x["acierta"], x["previsto"], x["medido"]))
