#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 32 (ANTES-ETAPA-IVDECLARADA.md, «Cómo» 4): el cruce y las cifras, escrito después de la corrida (no lo cubre el sello de
antes de correr; se declara en el resultado). Lee los veredictos de las dos lecturas (../privado/ivd/VEREDICTOS-IVD251.jsonl y
VEREDICTOS-IVDST.jsonl), los de la 31 (ivm/VEREDICTOS-IVM.jsonl) y su cruce (ivm/CRUCE-IVM.json: qué muestras y qué mensajes
del laboratorio apoyan cada nueva, y su estado en la 30).
- Cada muestra frente a su veredicto de la 31.
- Cada nueva con apoyo en muestras, con el estado de sus muestras en su versión y su apoyo del laboratorio de la 30, con las
  mismas reglas que la 31 (afectada, tocada, intacta; con algún válido).
- Un contraste que no es veredicto: los obligatorios que IRIS da en las versiones sin texto, frente a la OPT del mismo campo en el
  texto de v2.5.1 (la versión más cercana con texto). Dice cuántas inválidas lo son solo por obligatorios que v2.5.1 no hace
  obligatorios.
- La previsión sellada (ivd/PREVISION-IVD.json) y la de Jev (ivd/decision-jev-prevision-ivd.md), frente a lo medido, con la
  lectura final y con la sellada.
Tras la revisión a ciegas:
- la pasada de repeticiones se mide en las FILAS, en la variante que manda, como en la 31 (la lectura de la 2.5.1 sellada no la
  anotaba), y también las otras formas de error que el conductor no reconoce;
- las cifras con cada respuesta a Q-VD-3: «aparte» (Q-VD-3b, la del ANTES, que va en el titular por Q-VD-3d), «dentro» y «sin
  decidir» (Q-VD-3c), como sensibilidad; y que los veredictos finales son los de la lectura sellada (guardados aparte,
  ../privado/ivd/VEREDICTOS-*-sellada.jsonl), porque lo que cambió en las lecturas solo anota la clase X;
- cuántas sin decidir lo son solo por tablas que el índice de v2.5.1 da como de usuario (Q-VD-1 decía «las de usuario, aviso»;
  el aparato lee «la que el esquema de IRIS trae vacía»).
Escribe ivd/CRUCE-IVD.json y ivd/CIFRAS-IVD.json (publicables: lugares, recuentos y nombres de muestra).
  python3 ivd/cruce_ivd.py"""
import collections
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(AQUI)
PRIV = os.path.normpath(os.path.join(FASE, "..", "privado", "ivd"))
sys.path.insert(0, AQUI)
import texto_ivd as TX  # noqa: E402

VISTA = os.path.normpath(os.path.join(FASE, "..", "estandares", "hl7v2", "HL7_Messaging_v251", "vista_v25"))


def veredictos(nombres):
    d = {}
    for f in nombres:
        for l in open(os.path.join(PRIV, f), encoding="utf-8"):
            x = json.loads(l)
            assert x["id"] not in d
            d[x["id"]] = x
    return d


V32 = veredictos(("VEREDICTOS-IVD251.jsonl", "VEREDICTOS-IVDST.jsonl"))
SELLADA = veredictos(("VEREDICTOS-IVD251-sellada.jsonl", "VEREDICTOS-IVDST-sellada.jsonl"))
FILAS = {}
for f in ("FILAS-IVD251.jsonl", "FILAS-IVDST.jsonl"):
    for l in open(os.path.join(PRIV, f), encoding="utf-8"):
        x = json.loads(l)
        FILAS[x["id"]] = x
V31 = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(FASE, "ivm", "VEREDICTOS-IVM.jsonl"), encoding="utf-8")}
LISTA = json.load(open(os.path.join(AQUI, "CORPUS-IVD-lista.json"), encoding="utf-8"))
assert len(V32) == 223 and set(V32) == set(SELLADA) == set(FILAS), "las lecturas no casan"
assert set(V32) | set(LISTA["fuera"]) == set(V31), "las muestras no casan con las de la 31"
TIPO251 = json.load(open(os.path.join(AQUI, "TABLAS-TIPO-IVD251.json"), encoding="utf-8"))["tablas"]


def principal(f):
    """La variante que manda, como en las dos lecturas."""
    vs = f["variantes"]
    m = vs.get("msh93")
    if m and vs.get("esquema") and any("no DocType set" in (p.get("crudo") or "") for p in m["errores"]):
        return vs["esquema"]
    return m or vs.get("esquema") or vs.get("ninguna")


def partes(lugar):
    p = lugar.split("|")
    return p[1:] if p[0][:1].isdigit() else p              # sin la versión delante (las de la lectura sin texto la llevan)


def lugar(e):
    clase, seg, campo = partes(e["lugar"])[:3]
    return "%s-%s" % (seg, campo) if campo else seg


def etiqueta(e):
    if e["lugar"] == "aparato":
        return "aparato (pasadas sin leer enteras)"
    p = partes(e["lugar"])
    if p[0] == "C":
        return "%s (campos de más)" % p[1]
    return "%s%s" % (lugar(e), " (tabla %s)" % p[3] if len(p) > 3 and p[3] else "")


def estado(v, campos):
    """El de la 31 (ivm/cruce_ivm.py)."""
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


# la pasada de repeticiones y las otras formas que el conductor no reconoce, en las FILAS (tras la revisión a ciegas)
repes, x_otras = {}, []
for i, f in FILAS.items():
    for p in principal(f)["errores"]:
        if p["clase"] != "X":
            continue
        m = re.search(r"segment (\d+):(\w+)\.\s+Segment has more fields", p.get("crudo") or "")
        if p.get("pasada") == "dn" and m:
            repes[i] = m.group(2)
        else:
            x_otras.append({"muestra": i, "version": f["version"], "pasada": p.get("pasada"),
                            "veredicto": V32[i]["veredicto_sostenido"],
                            "forma": re.sub(r"\d+", "N", (p.get("crudo") or "").replace("ERROR <Ens>ErrGeneral: ", ""))[:120]})

# las nuevas
C31 = json.load(open(os.path.join(FASE, "ivm", "CRUCE-IVM.json"), encoding="utf-8"))["nuevas"]
nuevas = []
for n in C31:
    mus = []
    for m in n["apoyo_muestras"]:
        v = V32.get(m["mensaje"]) or V31.get(m["mensaje"])     # las de la 2.5, con su veredicto de la 31
        s, reglas = estado(v, n["campos"])
        mus.append({"mensaje": m["mensaje"], "version": (V32.get(m["mensaje"]) or {}).get("version", "2.5 (la 31)"),
                    "estado": s, "reglas": reglas, "estado_en_la_31": m["estado"],
                    "aparte": sorted({e["lugar"] for e in (v or {}).get("aparte", [])})})
    lab = n["apoyo_laboratorio"]
    todos = [x["estado"] for x in lab + mus if x["estado"] != "no_encontrado"]
    nuevas.append({"id": n["id"], "campos": n["campos"], "apoyo_laboratorio": lab, "apoyo_muestras": mus,
                   "con_algun_valido": "valido" in todos,
                   "afectada": bool(todos) and all(s == "invalido_en_su_campo" for s in todos),
                   "todo_invalido": bool(todos) and all(s.startswith("invalido") for s in todos),
                   "estado": ("afectada" if todos and all(s == "invalido_en_su_campo" for s in todos) else
                              "tocada" if any(s == "invalido_en_su_campo" for s in todos) else "intacta"),
                   "estado_en_la_31": n["estado"], "con_algun_valido_en_la_31": n["con_algun_valido"],
                   "muestras_por_estado": dict(collections.Counter(x["estado"] for x in mus))})
json.dump({"nuevas": nuevas}, open(os.path.join(AQUI, "CRUCE-IVD.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
sin_valido = sorted(x["id"] for x in nuevas if not x["con_algun_valido"])

# las cifras
n = len(V32)
pct = lambda a, b: round(100.0 * a / b, 1) if b else None     # noqa: E731
tot = collections.Counter(v["veredicto_sostenido"] for v in V32.values())
por_version = collections.defaultdict(collections.Counter)
por_grupo = collections.defaultdict(collections.Counter)
for v in V32.values():
    por_version[v["version"]][v["veredicto_sostenido"]] += 1
    por_grupo[v["corpus"]][v["veredicto_sostenido"]] += 1
trans = collections.Counter("%s -> %s" % (V31[i]["veredicto_sostenido"], v["veredicto_sostenido"]) for i, v in V32.items())
solo_uno = collections.defaultdict(collections.Counter)
clases = collections.Counter()
for v in V32.values():
    lg = sorted({lugar(e) + " (" + partes(e["lugar"])[0] + ")" for e in v["sostenidos"]})
    for e in v["sostenidos"]:
        clases[partes(e["lugar"])[0]] += 1
    if len(lg) == 1:
        solo_uno[v["version"]][lg[0]] += 1
nd_por = collections.Counter()
nd_solo_por = collections.Counter()
for v in V32.values():
    if v["veredicto_sostenido"] == "no_decidible":
        ks = sorted({etiqueta(e) for e in v["no_decidibles"]})
        for k in ks:
            nd_por[k] += 1
        if len(ks) == 1:
            nd_solo_por[ks[0]] += 1
aparte = collections.Counter()
for v in V32.values():
    for e in v["aparte"]:
        aparte[e["por"].split(" (")[0]] += 1
con_aparte = sum(bool(v["aparte"]) for v in V32.values())
# las tres respuestas a Q-VD-3
alternativas = {
    "Q-VD-3b_aparte_(la_del_ANTES,_en_el_titular)": dict(tot),
    "dentro": dict(collections.Counter(("invalido" if i in repes else x["veredicto_sostenido"]) for i, x in V32.items())),
    "Q-VD-3c_sin_decidir": dict(collections.Counter(
        ("no_decidible" if i in repes and x["veredicto_sostenido"] == "valido" else x["veredicto_sostenido"]) for i, x in V32.items()))}
validas_que_cambian = sorted(i for i, x in V32.items() if i in repes and x["veredicto_sostenido"] == "valido")
iguales = all(V32[i]["veredicto_sostenido"] == SELLADA[i]["veredicto_sostenido"] for i in V32)
assert iguales, "los veredictos finales no son los de la lectura sellada"
# Q-VD-1, las tablas de usuario: las sin decidir solo por tablas que el índice de v2.5.1 da como de usuario
solo_usuario = []
for i, v in V32.items():
    if v["veredicto_sostenido"] != "no_decidible":
        continue
    tablas = [partes(e["lugar"]) for e in v["no_decidibles"]]
    if all(p[0] == "T_HL7" and len(p) > 3 and (TIPO251.get(p[3]) or {}).get("tipo") == "User-defined" for p in tablas):
        solo_usuario.append(i)
# el contraste con v2.5.1: los obligatorios que da IRIS sin texto, con su OPT en v2.5.1
ATR = TX.atributos(VISTA)
r_st = collections.defaultdict(lambda: {"muestras": set()})
solo_no_r = set()
for i, v in V32.items():
    if v["version"] == "2.5.1" or v["veredicto_sostenido"] != "invalido":
        continue
    no_r = []
    for e in v["sostenidos"]:
        c, seg, campo = partes(e["lugar"])[:3]
        if c != "R":
            continue
        opt = (ATR.get(seg, {}).get(int(campo)) or {}).get("opt")
        k = "%s-%s" % (seg, campo)
        r_st[k]["opt_v251"] = opt
        r_st[k]["muestras"].add(i)
        if opt != "R":
            no_r.append(e)
    if no_r and len(no_r) == len(v["sostenidos"]):
        solo_no_r.add(i)
contraste = {k: {"opt_v251": x.get("opt_v251"), "muestras": len(x["muestras"])} for k, x in sorted(r_st.items())}
no_r_opt = {k: x for k, x in contraste.items() if x["opt_v251"] != "R"}


def medir(V):
    t = collections.Counter(v["veredicto_sostenido"] for v in V.values())
    pv = collections.defaultdict(collections.Counter)
    for v in V.values():
        pv[v["version"]][v["veredicto_sostenido"]] += 1
    tr = collections.Counter("%s -> %s" % (V31[i]["veredicto_sostenido"], v["veredicto_sostenido"]) for i, v in V.items())
    return {"PVD1_validas_pct_por_version": {k: pct(pv[k]["valido"], sum(pv[k].values())) for k in ("2.5.1", "2.6", "2.8")},
            "PVD2_validas_pct_total": pct(t["valido"], n), "PVD3_invalidas_pct_total": pct(t["invalido"], n),
            "PVD4_sin_decidir_pct_total": pct(t["no_decidible"], n),
            "PVD5_invalidas_en_la_31_que_salen_validas": tr["invalido -> valido"],
            "PVD6_muestras_con_algo_aparte_pct": pct(sum(bool(v["aparte"]) for v in V.values()), n),
            "PVD7_nuevas_con_muestras_sin_ningun_mensaje_valido": len(sin_valido)}, t


P = json.load(open(os.path.join(AQUI, "PREVISION-IVD.json"), encoding="utf-8"))["prevision"]


def frente(med, t):
    prev = {}
    for k, m in med.items():
        if isinstance(m, dict):
            for kk, mm in m.items():
                iv = P[k][kk]
                prev["%s %s" % (k, kk)] = {"previsto": iv, "medido": mm, "acierta": iv[1] <= mm <= iv[2]}
        else:
            prev[k] = {"previsto": P[k], "medido": m, "acierta": P[k][1] <= m <= P[k][2]}
    pv = pct(t["valido"], n)
    jev_bin = "menos_20" if pv < 20 else "20_50" if pv < 50 else "50_80" if pv < 80 else "mas_80"
    prev["Jev pv_validas (menos_20)"] = {"medido": jev_bin, "acierta": jev_bin == "menos_20"}
    prev["Jev pv_nuevas (las_dos)"] = {"medido": len(sin_valido), "acierta": len(sin_valido) == 2}
    return prev


prev = frente(*medir(V32))
cif = {
    "n": n, "total": dict(tot), "por_version": {k: dict(c) for k, c in sorted(por_version.items())},
    "por_grupo": {k: dict(c) for k, c in sorted(por_grupo.items())},
    "frase": ("De las %d muestras que declaran otra versión que la 2.5, con el esquema de IRIS de la suya, %d son válidas, %d "
              "inválidas y %d sin decidir; de las %d nuevas que se apoyan en muestras, %d siguen sin ningún mensaje válido"
              % (n, tot["valido"], tot["invalido"], tot["no_decidible"], len(nuevas), len(sin_valido))),
    "q_vd_3_las_tres_respuestas": alternativas,
    "validas_que_dependen_de_q_vd_3": validas_que_cambian,
    "veredictos_iguales_que_la_lectura_sellada": iguales,
    "pasada_de_repeticiones": {
        "nota": "medida en las FILAS, en la variante que manda, como en la 31: «el segmento tiene más campos de los que permite la estructura»",
        "muestras": len(repes), "por_version": dict(collections.Counter(FILAS[i]["version"] for i in repes)),
        "por_version_y_segmento": dict(sorted(collections.Counter("%s %s" % (FILAS[i]["version"], s) for i, s in repes.items()).items())),
        "por_veredicto_final": dict(collections.Counter(V32[i]["veredicto_sostenido"] for i in repes))},
    "otras_formas_que_el_conductor_no_reconoce": x_otras,
    "frente_a_la_31": dict(sorted(trans.items())),
    "errores_sostenidos_por_clase": dict(clases),
    "invalidas_por_un_solo_lugar": {k: dict(c.most_common()) for k, c in sorted(solo_uno.items())},
    "sin_decidir_por": dict(nd_por.most_common()), "sin_decidir_solo_por": dict(nd_solo_por.most_common()),
    "muestras_con_algo_aparte": con_aparte, "aparte_por_motivo": dict(aparte),
    "muestras_con_campos_sin_evaluar": sorted(i for i, v in V32.items() if v.get("campos_sin_evaluar")),
    "sin_decidir_solo_por_tablas_de_usuario_en_v251": sorted(solo_usuario),
    "contraste_obligatorios_sin_texto_frente_a_v251": {
        "nota": "no es veredicto: la OPT del mismo campo en el texto de v2.5.1, la versión más cercana con texto",
        "obligatorios_que_v251_no_hace_obligatorios": no_r_opt,
        "invalidas_solo_por_esos": sorted(solo_no_r), "n_invalidas_solo_por_esos": len(solo_no_r),
        "todos": contraste},
    "nuevas": {"n": len(nuevas), "sin_ningun_valido": sin_valido,
               "con_algun_valido": sorted(x["id"] for x in nuevas if x["con_algun_valido"]),
               "afectadas": sorted(x["id"] for x in nuevas if x["afectada"]),
               "por_estado": dict(collections.Counter(x["estado"] for x in nuevas))},
    "prevision": prev, "prevision_aciertos": "%d de %d" % (sum(x["acierta"] for x in prev.values()), len(prev)),
}
json.dump(cif, open(os.path.join(AQUI, "CIFRAS-IVD.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(cif["frase"])
print("por versión:", cif["por_version"])
print("las tres respuestas:", alternativas, "| válidas que dependen de Q-VD-3:", len(validas_que_cambian), "| iguales:", iguales)
print("frente a la 31:", cif["frente_a_la_31"])
print("repeticiones:", cif["pasada_de_repeticiones"]["muestras"], cif["pasada_de_repeticiones"]["por_veredicto_final"])
print("otras formas:", [(x["muestra"], x["pasada"], x["veredicto"]) for x in x_otras])
print("aparte:", con_aparte, dict(aparte), "| sin decidir solo por tablas de usuario:", solo_usuario)
for x in nuevas:
    print("  %-7s %s | muestras %s | algún válido %s (en la 31: %s)" % (
        x["id"], x["estado"], x["muestras_por_estado"], x["con_algun_valido"], x["con_algun_valido_en_la_31"]))
print("contraste v2.5.1:", no_r_opt, "| inválidas solo por esos:", len(solo_no_r))
print("previsión:", cif["prevision_aciertos"])
for k, x in prev.items():
    if not x["acierta"]:
        print("  falla:", k, x)
print("sin decidir por:", list(nd_por.most_common(8)))
print("sin decidir solo por:", list(nd_solo_por.most_common(6)))
