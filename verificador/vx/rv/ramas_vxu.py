#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 22 (vx/rv/diseno-rv-fable.md; decisiones de Jev en vx/rv/decision-jev-qrv.md): las nueve nuevas de VXU y el arrastre de
estado en la rama principal de cada conversor. Corre los pares de cv/cv3_minimos_vxu.py y la secuencia VL11 con las versiones
fijadas (el control) y con las ramas principales, con la herramienta del estudio y el mismo juez; LinuxForHealth decide mensaje a
mensaje (S-RV-4). No toca la herramienta, el arnés, cv3_minimos_vxu.py, cv/ar/ ni el juez (S-RV-15). Solo biblioteca estándar.

  python3 vx/rv/ramas_vxu.py correr <artefactos> <salida> [--desde N] [--hasta N] [--sello <carpeta>]   # pasos 3, 5, 7 y 8
  python3 vx/rv/ramas_vxu.py ramas <compare-ms.json> <compare-lfh.json> <RAMAS-RV.json>
  python3 vx/rv/ramas_vxu.py contraste <proyectos> <ESTADO-RV.json> <CONTRASTE-RV.json> [--comprobar]
  python3 vx/rv/ramas_vxu.py borradores <salida> <BORRADORES-ISSUES-VXU.md>
  python3 vx/rv/ramas_vxu.py resultado <salida> <RESULTADO-RAMAS-VXU.md>

Pasos de correr: 3 identidades (sin Docker); 5 el control con las versiones fijadas -> CONTROL-RV.json; 7 las corridas con las
ramas -> RESULTADO-RV-minimos-main.json y SECUENCIA-RV.json; 8 el estado de las nueve -> ESTADO-RV.json. Los pasos 6 (las ramas
al día, con red), 9 (el contraste, con red) y 10-11 se lanzan aparte.
Códigos: 0 bien; 1 identidades; 2 error del aparato; 3 el control no reproduce; 4 la caja falló; 6 contraste con decisiones
vacías; 7 sello."""
import argparse
import collections
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout

RV_D = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(os.path.dirname(RV_D))
CVD = os.path.join(FASE, "cv")
AR_D = os.path.join(CVD, "ar")
sys.path[:0] = [RV_D, AR_D, CVD, FASE]
_argv, sys.argv = sys.argv, ["x", "--silencio"]
import verificar_conversor as VC  # noqa: E402
import cv3_minimos_vxu as MV  # noqa: E402
import arrastre as AR  # noqa: E402
sys.argv = _argv

AD = lambda n: os.path.join(CVD, "adaptadores", n + ".json")  # noqa: E731
FIJADA = {"microsoft": AD("microsoft"), "lfh_lote": AD("linuxforhealth"), "lfh_mensaje": AD("linuxforhealth-mensaje")}
RAMA = {"microsoft": AD("microsoft-main"), "lfh_lote": AD("linuxforhealth-main"), "lfh_mensaje": AD("linuxforhealth-main-mensaje")}
PUBLICADO = os.path.join(FASE, "vx", "RESULTADO-VX3-minimos.json")
ESPERADO = {"microsoft": "766f8938d0c12c382bec2edceeca4d3be4fd19900d0bd131ba880ac615fadf3e",
            "linuxforhealth": "ac41f71b98ee75bac637ecd4b68f58b463f0798bf66cfa941f4194cb2a50acf2"}
# las nueve (vx/CLASES-VX3.json, clase «nueva» y confirmada con su par): id, par, conversor, fuerza
NUEVE = [("VX-M7", "VM07-lote-repetido", "microsoft", "fuerte"), ("VX-M8", "VM08-fabricante-alterno", "microsoft", "débil"),
         ("VX-M10", "VM10-relacion-grd", "microsoft", "fuerte"), ("VX-M12", "VM12-dos-indicaciones", "microsoft", "débil"),
         ("VX-M14", "VM14-dosis-punto-inicial", "microsoft", "fuerte"), ("VX-M15", "VM15-re-sin-rxa18", "microsoft", "fuerte"),
         ("VX-L6", "VL04-rxa21-d", "linuxforhealth", "fuerte"), ("VX-L8", "VL06-dos-rxa10", "linuxforhealth", "débil"),
         ("VX-L9", "VL07-dos-indicaciones", "linuxforhealth", "débil")]
VL11 = "VL11-estado-fabricante"
CLAVES_PREVISION_RV = ("etapa", "fecha", "juez", "herramienta", "ramas_15A", "p_control_reproduce", "p_lote_igual_mensaje_fijada",
                       "p_rama_avanzo", "p_toca_vxu_si_avanzo", "p_construccion_dentro_del_tope", "p_sigue", "K_previsto",
                       "k_mas_probable", "p_arrastre_sigue_master", "p_ya_reportada", "p_alguna_cambiada_o_par_roto",
                       "tolerancia_control", "jev")
TOCA = {"microsoft": ([r"^data/Templates/Hl7v2/", r"^src/Microsoft\.Health\.Fhir\.Liquid\.Converter/",
                       r"^src/Microsoft\.Health\.Fhir\.Liquid\.Converter\.Tool/"],
                      [r"^docs/", r"Tests?/", r"^\.github/", r"README", r"\.md$"]),
        "linuxforhealth": ([r"^src/main/resources/hl7/", r"^src/main/java/", r"^build\.gradle", r"^gradle/", r"^settings\.gradle"],
                           [r"^src/test/", r"^docs?/", r"\.md$", r"^\.github/"])}
TERMINOS = {   # §6.2: candidato = al menos un término de campo y uno de efecto
    "VX-M7": (["rxa-15", "rxa.15", "rxa15", "lotnumber", "lot number"], ["repeat", "repetition", "~", "concaten", "+", "multiple lot", "diluent"]),
    "VX-M8": (["rxa-17", "rxa.17", "rxa17", "manufacturer", "organization.name"], ["--", "alternate", "cwe.5", "ce.5", "concaten", "display"]),
    "VX-M10": (["nk1-3", "nk1.3", "nk13", "relationship", "relatedperson"], ["grd", "guardian", "hl70063", "v2-0063", "v3-rolecode", "no code", "empty code"]),
    "VX-M12": (["rxa-19", "rxa.19", "rxa19", "reasoncode", "indication"], ["repeat", "repetition", "only the first", "second", "multiple"]),
    "VX-L9": (["rxa-19", "rxa.19", "rxa19", "reasoncode", "indication"], ["repeat", "repetition", "only the first", "second", "multiple"]),
    "VX-M14": (["rxa-6", "rxa.6", "rxa6", "dosequantity", "administered amount"], ["leading", "decimal", ".5", "nm", "invalid json", "number"]),
    "VX-M15": (["rxa-20", "rxa.20", "rxa20", "rxa-18", "rxa.18", "completion status", "immunization.status"],
               ["not-done", "completed", "re ", "na ", "refus", "statusreason", "hl70322"]),
    "VX-L6": (["rxa-21", "rxa.21", "rxa21", "action code", "immunization.status"], ["entered-in-error", "delete", "d ", "completed"]),
    "VX-L8": (["rxa-10", "rxa.10", "rxa10", "performer", "administering provider"], ["repeat", "repetition", "only the first", "second", "multiple"]),
    "arrastre": (["rxa-17", "manufacturer", "organization"], ["reset", "internal variable", "state", "repeating messages", "previous message", "leak", "#348"]),
}
# §7.2: lo fijo de cada borrador (título, cita de la guía, esperado y observado en la versión fijada)
TABLA = {
    "VX-M15": ("RXA-20 = RE/NA without RXA-18 becomes Immunization.status completed",
               "RXA_Immunization.csv:25-26; ConceptMap table-hl70322-to-event-status (RE, NA -> not-done)",
               "status: not-done", "status: completed (the status is taken from RXA-18, the refusal reason, instead of RXA-20)"),
    "VX-M14": ("RXA-6 \".5\" becomes doseQuantity.value 5",
               "RXA_Immunization.csv:9; HL7 v2.5 chapter 2A, NM (a leading period is valid)",
               "doseQuantity.value: 0.5", "doseQuantity.value: 5 (the dose is multiplied by ten)"),
    "VX-M7": ("repeated RXA-15 is concatenated with \"+\" into one lotNumber",
              "RXA_Immunization.csv:20 (RXA-15 -> lotNumber, 0..1)",
              "lotNumber: the first repetition (LOT-M07c)", "lotNumber: LOT-M07c+DIL-M07c (a lot that does not exist)"),
    "VX-M10": ("NK1-3 GRD gives a RelatedPerson.relationship coding with no code",
               "ConceptMap table-hl70063-to-v3-rolecode (GRD, identity v2-0063)",
               "relationship.coding: {system: v2-0063, code: GRD}", "relationship.coding with a local system and no code: the guardian relation is lost"),
    "VX-M8": ("RXA-17 CWE.2 and CWE.5 are joined with \"--\" into Organization.name",
              "ConceptMap datatype-cwe-to-organization (CWE.2 -> name)",
              "Organization.name: Merck", "Organization.name: Merck--Merck S.A."),
    "VX-M12": ("only one of two RXA-19 repetitions reaches Immunization.reasonCode",
               "RXA_Immunization.csv:24 (RXA-19 -> reasonCode, 0..*)", "two reasonCode", "one reasonCode (ASM is dropped)"),
    "VX-L6": ("RXA-21 = D (deleted) with RXA-20 = CP gives status completed, not entered-in-error",
              "RXA_Immunization.csv:27 (RXA-21 D -> entered-in-error)", "status: entered-in-error",
              "status: completed (a deleted record looks like an administered vaccine)"),
    "VX-L8": ("only the first of two RXA-10 repetitions reaches Immunization.performer",
              "RXA_Immunization.csv:13-15 (RXA-10 -> performer, 0..*)", "two performer entries (AP)", "only the first (PR02 is dropped)"),
    "VX-L9": ("only one of two RXA-19 repetitions reaches Immunization.reasonCode",
              "RXA_Immunization.csv:24 (RXA-19 -> reasonCode, 0..*)", "two reasonCode", "one reasonCode (ASM is dropped)"),
}
INVOCACION = {"microsoft": "Microsoft.Health.Fhir.Liquid.Converter.Tool convert -d data/Templates/Hl7v2 -r VXU_V04 -n input.hl7 -f output.json",
              "linuxforhealth": "HL7ToFHIRConverter.convert(String), one message per JVM"}


class ErrorAparato(Exception):
    pass


class ControlNoPasa(Exception):
    pass


valor = AR.valor


def _leer(ruta):
    return json.load(open(ruta, encoding="utf-8"))


def _escribir(ruta, d):
    with open(ruta, "w", encoding="utf-8") as g:
        g.write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")


def _par(res, pid):
    return next((p for p in res["pares"] if p["id"] == pid), None)


# ---------------------------------------------------------------------------- correr y juzgar (§2)
def _cid(corrida):
    return _leer(os.path.join(corrida, "ADAPTADOR.json"))["id"]


def correr_carpeta(ad, corpus, salida, artefactos, ejecutor=None):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = VC.main([ad, salida, "--artefactos", artefactos, "--sin-corpus-lab", "--sin-minimos", "--sin-sensibilidad", "--json-solo",
                      "--corpus", corpus], ejecutor=ejecutor)
    if rc == 4:
        raise ErrorAparato("la caja falló en %s" % os.path.basename(salida))
    if rc != 0:
        raise ErrorAparato("la herramienta salió con %s en %s:\n%s" % (rc, os.path.basename(salida), buf.getvalue()[-1500:]))
    return salida


def armar(corrida_ms, corrida_lfh, vl11_caso, vl11_control, evid, ids=None):
    """S-RV-6: el árbol que espera cv3_minimos_vxu.juzgar, desde las carpetas de la herramienta (solo los ficheros de PARES)."""
    shutil.rmtree(evid, ignore_errors=True)
    nombres = {"%s-%s" % (pid, s) for pid, _, _, _ in MV.PARES for s in ("caso", "control")}
    ids = ids or (_cid(corrida_ms), _cid(corrida_lfh))
    for conv, corrida, cid in (("microsoft", corrida_ms, ids[0]), ("linuxforhealth", corrida_lfh, ids[1])):
        d = os.path.join(evid, conv)
        os.makedirs(d)
        origen = os.path.join(corrida, "evidencias", cid, "propio")
        for f in sorted(os.listdir(origen)) if os.path.isdir(origen) else []:
            if os.path.splitext(f)[0] in nombres:
                shutil.copyfile(os.path.join(origen, f), os.path.join(d, f))
    for lado, corrida, fichero in (("caso", vl11_caso, "2-L11b.json"), ("control", vl11_control, "1-L11b.json")):
        if corrida is None:
            continue
        src = os.path.join(corrida, "evidencias", ids[1], "propio", fichero)
        if os.path.exists(src):
            d = os.path.join(evid, "linuxforhealth", "%s-%s" % (VL11, lado))
            os.makedirs(d, exist_ok=True)
            shutil.copyfile(src, os.path.join(d, "L11b.json"))
    return evid


def juzgar(evid, salida):
    """cv3_minimos_vxu.juzgar tal cual (S-RV-6)."""
    guardado = sys.argv
    sys.argv = ["x", "--silencio"]
    try:
        with redirect_stdout(io.StringIO()):
            MV.juzgar(evid, salida)
    finally:
        sys.argv = guardado
    return _leer(salida)


# ---------------------------------------------------------------------------- el control (§3)
def comparar_control(nuevo, publicado):
    """S-RV-8 con Q-RV-D-4 (Jev: no_cuenta): par a par; «veredicto» (confirmada, sale, estado, categoría) bloquea; «texto» (que) se
    lista y no bloquea."""
    dif = []
    for p in publicado["pares"]:
        q = _par(nuevo, p["id"])
        if q is None:
            dif.append({"par": p["id"], "conversor": None, "lado": None, "campo": "par", "publicado": "presente", "hoy": "ausente", "clase": "veredicto"})
            continue
        if q.get("confirmada") != p.get("confirmada"):
            dif.append({"par": p["id"], "conversor": None, "lado": None, "campo": "confirmada", "publicado": p.get("confirmada"),
                        "hoy": q.get("confirmada"), "clase": "veredicto"})
        for conv in ("microsoft", "linuxforhealth"):
            for lado in ("caso", "control"):
                a, b = (p.get(conv) or {}).get(lado), (q.get(conv) or {}).get(lado)
                if a is None and b is None:
                    continue
                if a is None or b is None:
                    dif.append({"par": p["id"], "conversor": conv, "lado": lado, "campo": "lado", "publicado": a is not None,
                                "hoy": b is not None, "clase": "veredicto"})
                    continue
                for campo in ("sale", "estado", "categoria", "que"):
                    if a.get(campo) != b.get(campo):
                        dif.append({"par": p["id"], "conversor": conv, "lado": lado, "campo": campo, "publicado": a.get(campo),
                                    "hoy": b.get(campo), "clase": "texto" if campo == "que" else "veredicto"})
    return {"reproduce": not any(d["clase"] == "veredicto" for d in dif), "diferencias": dif,
            "jueces": sorted({nuevo.get("juez"), publicado.get("juez")}), "tolerancia": "solo el juez; el texto se lista (Q-RV-D-4, Jev)"}


def lote_vs_mensaje(filas_lote, filas_mensaje):
    """Los casos cuyo veredicto cambia entre lote y mensaje a mensaje (S-RV-9; P-RV-12)."""
    a = {f["caso"]: valor(f) for f in filas_lote}
    b = {f["caso"]: valor(f) for f in filas_mensaje}
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


# ---------------------------------------------------------------------------- las ramas al día (§4)
def decidir_ramas(compare, conversor):
    toca, no = TOCA[conversor]
    ficheros = [f["filename"] for f in compare.get("files") or []]
    vxu = [f for f in ficheros if not any(re.search(r, f) for r in no) and any(re.search(r, f) for r in toca)]
    ahead = compare.get("ahead_by", 0)
    return {"avanzo": ahead > 0, "ahead_by": ahead, "reconstruir": ahead > 0 and bool(vxu), "ficheros_vxu": vxu,
            "incompleto": len(ficheros) >= 300 or ahead > 250,
            "commits": [{"sha": c["sha"][:7], "fecha": c["commit"]["committer"]["date"], "mensaje": c["commit"]["message"].split("\n")[0]}
                        for c in compare.get("commits") or []]}


# ---------------------------------------------------------------------------- la secuencia (§5)
def veredicto_vl11(reps, control_1_L11b, b_ve):
    """-> (sigue | no_sigue | otra_cosa, motivos)."""
    mot = []
    for r in reps:
        if any(x[0] == "RXA-17" and x[2] == "dato_perdido" for x in r["mensaje_2_L11b"]["hallazgos"]):
            mot.append("mensaje a mensaje, 2-L11b también pierde RXA-17")
    if len({json.dumps(r["lote_2_L11b"], sort_keys=True) for r in reps}) > 1 or len({json.dumps(r["mensaje_2_L11b"], sort_keys=True) for r in reps}) > 1:
        mot.append("las repeticiones difieren")
    if all(r["sale"] for r in reps) and b_ve and not mot:
        return "sigue", []
    if not mot and all(not any(x[0] == "RXA-17" and x[2] == "dato_perdido" for x in r["lote_2_L11b"]["hallazgos"])
                       and r["lote_2_L11b"] == r["mensaje_2_L11b"] == control_1_L11b for r in reps):
        return "no_sigue", []
    if not mot:
        mot.append("el lote pierde el fabricante pero el nivel del Bundle no lo ve, o las condiciones de la etapa 21 no se cumplen")
    return "otra_cosa", mot


def secuencia_vl11(artefactos, trabajo, ad_lote, ad_mensaje, ejecutor=None):
    """S-RV-10: como AR.positivo_vl11, con los adaptadores dados."""
    d = os.path.join(trabajo, "vl11")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    with redirect_stdout(io.StringIO()):
        MV.secuencias(os.path.join(d, "mensajes"))
    caso = os.path.join(d, "mensajes", VL11 + "-caso")
    control = os.path.join(d, "mensajes", VL11 + "-control")
    por_caso = lambda c: {f["caso"]: f for f in AR.filas(c)}  # noqa: E731
    reps = []
    for r in (1, 2):
        lc = correr_carpeta(ad_lote, caso, os.path.join(d, "lote-caso-%d" % r), artefactos, ejecutor)
        mc = correr_carpeta(ad_mensaje, caso, os.path.join(d, "mensaje-caso-%d" % r), artefactos, ejecutor)
        reps.append((lc, mc))
    lk = correr_carpeta(ad_lote, control, os.path.join(d, "lote-control-1"), artefactos, ejecutor)
    out = {"repeticiones": []}
    for lc, mc in reps:
        sale, mot = AR.positivo_sale(por_caso(lc), por_caso(mc), por_caso(lk))
        out["repeticiones"].append({"sale": sale, "motivos": mot, "lote_2_L11b": valor(por_caso(lc)["2-L11b"]),
                                    "mensaje_2_L11b": valor(por_caso(mc)["2-L11b"])})
    out["lote_control_1_L11b"] = valor(por_caso(lk)["1-L11b"])
    lc, mc = reps[0]
    el, em = AR.evidencia(lc, ("propio", "2-L11b")), AR.evidencia(mc, ("propio", "2-L11b"))
    b = []
    if el["conversion"]["salida"]["estado"] == em["conversion"]["salida"]["estado"] == "bundle":
        b = AR.diff_bundles(el["conversion"]["salida"]["bundle"], em["conversion"]["salida"]["bundle"])
    out["bundle_2_L11b"] = [list(x) for x in b]
    out["b_ve_manufacturer"] = any(x[0] == "Immunization" and x[1].startswith("manufacturer") for x in b)
    out["veredicto"], out["motivos"] = veredicto_vl11(out["repeticiones"], out["lote_control_1_L11b"], out["b_ve_manufacturer"])
    out["carpetas"] = {"lote_caso": os.path.basename(reps[0][0]), "lote_control": os.path.basename(lk)}
    out["_rutas"] = {"lote_caso": reps[0][0], "lote_control": lk}
    return out


# ---------------------------------------------------------------------------- el estado de las nueve (S-RV-7)
def _base(h):
    return re.sub(r"\(\d+\)", "", h)


def estado_nueve(fijada, main, filas_main):
    """S-RV-7 con Q-RV-D-1 (Jev: fila_aparte). filas_main: {(conversor, «<pid>-caso»): fila del juicio de la rama}."""
    objetivo = {pid: (hecho if isinstance(hecho, tuple) else (hecho,)) for pid, _, _, (hecho, _, _) in MV.PARES}
    no = [i for i, pid, _, _ in NUEVE if not (_par(fijada, pid) or {}).get("confirmada")]
    if no:
        raise ControlNoPasa("en la versión fijada no se confirman %s" % no)
    out = []
    for i, pid, conv, fuerza in NUEVE:
        m = _par(main, pid) or {}
        c = (m.get(conv) or {})
        caso, control = c.get("caso") or {}, c.get("control") or {}
        if m.get("confirmada"):
            est = "sigue"
        elif control.get("sale") or caso.get("estado") != "bundle" or control.get("estado") != "bundle":
            est = "par_roto"
        else:
            f = filas_main.get((conv, pid + "-caso")) or {"cuentan": []}
            bases = {_base(h) for h in objetivo[pid]}
            est = "cambiada" if any(_base(h["hecho"]) in bases for h in f["cuentan"]) else "corregida"
        f = filas_main.get((conv, pid + "-caso")) or {"cuentan": []}
        out.append({"id_vx": i, "par": pid, "conversor": conv, "fuerza": fuerza, "estado": est,
                    "fijada": (_par(fijada, pid) or {}).get(conv), "main": c,
                    "que_main": [q for h in f["cuentan"] if _base(h["hecho"]) in {_base(x) for x in objetivo[pid]} for q in h["que"]][:3]})
    nueve_pids = {pid for _, pid, _, _ in NUEVE}
    otros = [{"id": p["id"], "conversor": p.get("conversor"), "fijada": p.get("confirmada"), "main": (_par(main, p["id"]) or {}).get("confirmada")}
             for p in fijada["pares"] if p["id"] not in nueve_pids]
    k = collections.Counter(x["conversor"] for x in out if x["estado"] == "sigue")
    return {"juez": main.get("juez"), "nueve": out, "K": sum(k.values()),
            "k_por_conversor": {"microsoft": k["microsoft"], "linuxforhealth": k["linuxforhealth"]},
            "cambiadas": [x for x in out if x["estado"] == "cambiada"], "otros_17": otros}


# ---------------------------------------------------------------------------- el contraste (§6)
def candidatos(disc, issues, comments):
    campo, efecto = TERMINOS[disc]
    por_issue = collections.defaultdict(list)
    for c in comments:
        m = re.search(r"/issues/(\d+)$", c.get("issue_url") or "")
        if m:
            por_issue[int(m.group(1))].append(c.get("body") or "")
    out = []
    for i in issues:
        texto = " ".join([i.get("title") or "", i.get("body") or ""] + por_issue.get(i["number"], [])).lower()
        tc, te = [t for t in campo if t in texto], [t for t in efecto if t in texto]
        if tc and te:
            out.append({"numero": i["number"], "tipo": "pr" if "pull_request" in i else "issue", "estado": i.get("state"),
                        "titulo": i.get("title"), "url": i.get("html_url"), "terminos": sorted(tc + te), "cerrado": i.get("closed_at")})
    return sorted(out, key=lambda x: x["numero"])


def leer_varios(ruta):
    """Los JSON que escribe `gh api --paginate` (varias listas seguidas), aplanados."""
    t = open(ruta, encoding="utf-8").read()
    dec, i, out = json.JSONDecoder(), 0, []
    while i < len(t):
        while i < len(t) and t[i].isspace():
            i += 1
        if i >= len(t):
            break
        v, i = dec.raw_decode(t, i)
        out += v if isinstance(v, list) else [v]
    return out


REPO = {"microsoft": "ms", "linuxforhealth": "lfh"}


def contraste(proyectos, estado, salida, comprobar=False):
    if comprobar:
        c = _leer(salida)
        vacias = [k for k, v in list(c["discrepancias"].items()) + [("arrastre", c["arrastre"])] if v.get("decision") is None]
        if vacias:
            print("contraste: decisiones vacías en %s" % vacias)
            return 6
        print("contraste: todas decididas")
        return 0
    datos = {r: (leer_varios(os.path.join(proyectos, "issues-%s.json" % r)), leer_varios(os.path.join(proyectos, "comments-%s.json" % r)))
             for r in REPO.values()}
    res = {"fecha_lectura": None, "totales": {r: {"issues_y_pr": len(v[0]), "comentarios": len(v[1])} for r, v in datos.items()},
           "discrepancias": {}, "arrastre": None}
    for x in estado["nueve"]:
        iss, com = datos[REPO[x["conversor"]]]
        res["discrepancias"][x["id_vx"]] = {"estado": x["estado"], "candidatos": candidatos(x["id_vx"], iss, com),
                                           "decision": None, "numero": None, "cita": None, "nota": None}
    iss, com = datos["lfh"]
    res["arrastre"] = {"candidatos": candidatos("arrastre", iss, com), "decision": None, "numero": 348, "cita": None, "nota": None}
    _escribir(salida, res)
    return 0


# ---------------------------------------------------------------------------- los borradores (§7)
def _mensaje(pid, lado=0):
    caso = next(p for p in MV.PARES if p[0] == pid)[2][lado]
    return "\n".join(s for s in caso.replace("\r\n", "\r").split("\r") if s)


def _vl11():
    caso, _ = MV.SECUENCIAS[0][2]
    return ["\n".join(s for s in t.split("\r") if s) for _, t in caso]


def _frase(t):
    return t[0].upper() + t[1:]


def borradores(estado, contraste_, secuencia, versiones):
    """§7 con Q-RV-D-1 (cambiada: sin borrador), Q-RV-D-2 (VX-M14: propio, remite a MS-1) y Q-RV-D-3 (cerrada que sigue: pedir
    reabrir). Lanza ValueError si queda alguna decisión del contraste vacía."""
    vacias = [k for k, v in contraste_["discrepancias"].items() if v.get("decision") is None]
    if (contraste_.get("arrastre") or {}).get("decision") is None:
        vacias.append("arrastre")
    if vacias:
        raise ValueError("decisiones del contraste vacías: %s" % vacias)
    L = ["# Borradores de issues de VXU (etapa 22; %s)" % contraste_.get("fecha", ""), "",
         "**Son del autor: no se abren sin él.** Saldrían desde su cuenta de GitHub y hablan en su nombre. Están listos para copiar y",
         "pegar.", "",
         "**Qué cumple cada uno:**",
         "- es una discrepancia nueva y confirmada de la etapa de VXU (`RESULTADO-VXU.md`);",
         "- sigue en la rama principal (`RESULTADO-RAMAS-VXU.md`);",
         "- se buscó en los issues y PR del proyecto, abiertos y cerrados, con sus comentarios (`vx/rv/CONTRASTE-RV.json`).", "",
         "**Van en inglés.** Microsoft no tiene plantilla de issue; LinuxForHealth sí, y los suyos la siguen.", "",
         "**Antes de abrir alguno, conviene:**",
         "1. Mirar otra vez los issues abiertos: puede haber aparecido uno igual.",
         "2. Empezar por los fuertes (VX-M15, VX-M14, VX-M7, VX-M10 y VX-L6).",
         "3. Si se quiere, enlazar el resultado público (`verificador/RESULTADO-VXU.md`).", "",
         "Los mensajes son sintéticos: no hay ningún dato de paciente.", ""]
    cola, n = [], {"microsoft": 0, "linuxforhealth": 0}
    for conv, nombre in (("microsoft", "Microsoft FHIR-Converter (`microsoft/FHIR-Converter`)"),
                         ("linuxforhealth", "LinuxForHealth hl7v2-fhir-converter (`LinuxForHealth/hl7v2-fhir-converter`)")):
        L += ["---", "", "## %s" % nombre, "", "Versiones comprobadas: %s y %s. Orden usada: `%s`." % (
            versiones[conv]["fijada"], versiones[conv]["rama"], INVOCACION[conv]), ""]
        for x in estado["nueve"]:
            if x["conversor"] != conv:
                continue
            dec = contraste_["discrepancias"].get(x["id_vx"], {})
            if x["estado"] != "sigue":
                cola.append("- %s (%s): %s; sin borrador." % (x["id_vx"], x["par"],
                            "cambiada, pendiente de contraste (Q-RV-D-1)" if x["estado"] == "cambiada" else x["estado"]))
                continue
            titulo, cita, esperado, observado = TABLA[x["id_vx"]]
            obs = "%s (the same on %s and on %s)" % (observado, versiones[conv]["fijada"], versiones[conv]["rama"])    # DV-RV-2
            cuerpo = ["**To reproduce** (VXU_V04):", "", "```", _mensaje(x["par"]), "```", "",
                      "**Actual:** %s" % obs, "", "**Expected:** %s" % esperado, "",
                      "**Control:** the same message without the trigger converts correctly:", "", "```", _mensaje(x["par"], 1), "```", "",
                      "**References:** HL7 v2-to-FHIR guide, %s." % cita, "",
                      "**Versions checked:** %s and %s; order used: `%s`." % (versiones[conv]["fijada"], versiones[conv]["rama"], INVOCACION[conv])]
            if dec["decision"] in ("reportada_abierta", "reportada_cerrada"):
                cab = "### Comment on #%s (%s)%s" % (dec.get("numero"), x["id_vx"], ": please reopen" if dec["decision"] == "reportada_cerrada" else "")
                L += [cab, "", "Reproduced on the main branch with a minimal pair (%s)." % x["par"], ""] + cuerpo + [""]
                cola.append("- %s: comentario a #%s%s." % (x["id_vx"], dec.get("numero"), ", pidiendo reabrir" if dec["decision"] == "reportada_cerrada" else ""))
                continue
            n[conv] += 1
            bid = "VXU-%s-%d" % ("MS" if conv == "microsoft" else "LFH", n[conv])
            t = ("[HL7v2 VXU_V04] %s" % titulo) if conv == "microsoft" else ("%s, VXU_V04" % _frase(titulo))
            L += ["### %s. %s (%s)" % (bid, _frase(titulo), x["id_vx"]), ""]
            if x["id_vx"] == "VX-M14":
                L += ["> Nota para el autor: la misma causa que MS-1 de `cv/BORRADORES-ISSUES.md` (los NM se escriben tal cual). Si MS-1 "
                      "se abre antes, pegar esto como comentario allí (Q-RV-D-2).", ""]
            L += ["**Title:** `%s`" % t, ""]
            if dec["decision"] == "relacionada" and dec.get("numero"):
                L += ["Possibly related to #%s%s." % (dec["numero"], (" (%s)" % dec["nota_ingles"]) if dec.get("nota_ingles") else ""), ""]
            L += (["**Describe the bug**", "", "%s, and the meaning of the data changes." % _frase(titulo), ""] if conv == "linuxforhealth"
                  else ["%s, and the meaning of the data changes." % _frase(titulo), ""]) + cuerpo + [""]
            cola.append("- %s ← %s: issue nuevo." % (bid, x["id_vx"]))
    L += ["---", "", "## El arrastre de estado: comentario al #348 de LinuxForHealth", ""]
    if secuencia.get("veredicto") == "sigue":
        m1, m2 = _vl11()
        L += ["### Comment on #348 (arrastre de estado)", "",
              "Another trigger for this, reproducible on %s and %s, converting two messages with the same HL7ToFHIRConverter instance." % (
                  versiones["linuxforhealth"]["rama"], versiones["linuxforhealth"]["fijada"]), "",
              "This issue describes repeated ORC/RXA groups inside one message. Here the state carries over from one message to the "
              "next, and the trigger is an RXA-17 with text only.", "",
              "Message 1 has RXA-17 with text only and no code (`^Laboratorio Sintetico^`). Message 2 is a plain VXU_V04 with "
              "`RXA-17 = MSD^Merck^MVX`. Synthetic data.", "",
              "- Message 2 converted alone: Immunization.manufacturer references an Organization with identifier MSD (MVX).",
              "- Message 2 converted after message 1, same instance: Immunization.manufacturer is missing, and the Organization is not created.",
              "- Nothing else in message 2 changes.", "",
              "The interim fix mentioned here (`condition: rxa17 NOT_NULL`) does not cover this case: RXA-17 is not null, it has text and "
              "no code. In a batch of 40 VXU messages, every message after the first one with a text-only RXA-17 lost its manufacturer "
              "(23 of 40); converting one message per process, none did.", "",
              "Message 1:", "", "```", m1, "```", "", "Message 2:", "", "```", m2, "```", "",
              "HL7 v2-to-FHIR guide: RXA-17 -> Immunization.manufacturer (RXA_Immunization.csv:22).", ""]
        cola.append("- El arrastre: comentario al #348.")
    else:
        L += ["El arrastre no sigue en `master` (%s): no hay comentario." % secuencia.get("veredicto"), ""]
        cola.append("- El arrastre: no sigue en `master`, sin comentario.")
    L += ["---", "", "## Para la cola del autor", ""] + cola + [""]
    return "\n".join(L)


# ---------------------------------------------------------------------------- la previsión (§8)
def comprobar_sello_rv(prevision, sello, base=None):
    base = base or os.path.dirname(os.path.abspath(sello))
    vistos = set()
    try:
        for linea in open(sello, encoding="utf-8"):
            m = re.match(r"^([0-9a-f]{64})  (\S+)\s*$", linea)
            if not m:
                continue
            ruta = os.path.realpath(os.path.join(base, m.group(2)))
            if hashlib.sha256(open(ruta, "rb").read()).hexdigest() != m.group(1):
                return False
            vistos.add(ruta)
        p = _leer(prevision)
    except (OSError, ValueError):
        return False
    return (os.path.realpath(prevision) in vistos and all(k in p for k in CLAVES_PREVISION_RV)
            and isinstance(p.get("p_sigue"), dict) and all(i in p["p_sigue"] for i, _, _, _ in NUEVE))


# ---------------------------------------------------------------------------- el resultado
def resultado_md(estado, secuencia, contraste_, ramas, control):
    k = collections.Counter(x["conversor"] for x in estado["nueve"] if x["estado"] == "sigue")
    if estado["K"] != sum(k.values()) or estado["k_por_conversor"] != {"microsoft": k["microsoft"], "linuxforhealth": k["linuxforhealth"]}:
        raise ValueError("K no cuadra con la tabla de las nueve")
    vd = secuencia.get("veredicto")
    arr = {"sigue": "sigue", "no_sigue": "no sigue"}.get(vd)
    cola = ("el arrastre de estado %s en `master`" % arr) if arr else ("el arrastre de estado en `master` da otra cosa: %s" %
                                                                       "; ".join(secuencia.get("motivos") or []))
    frase = ("De las 9 nuevas de VXU, siguen %d en la rama principal de su conversor (Microsoft %d de 6, LinuxForHealth %d de 3); %s"
             % (estado["K"], k["microsoft"], k["linuxforhealth"], cola))
    L = ["# Resultado de la etapa 22: las nueve de VXU en las ramas principales", "", "**%s.**" % frase, "",
         "La pregunta, fijada antes de medir en [`ANTES-ETAPA-RAMAS-VXU.md`](ANTES-ETAPA-RAMAS-VXU.md): ¿siguen en la rama principal "
         "de cada conversor las nueve discrepancias nuevas de VXU y el arrastre de estado de LinuxForHealth? Y, para las que sigan, "
         "¿quedan listos los borradores de issues, contrastados con lo que cada proyecto tiene abierto hoy?", "",
         "## Las ramas", ""]
    L += ["| Conversor | Commit | Reconstruida hoy | Huella |", "|---|---|---|---|"]
    for conv, r in ramas.items():
        L.append("| %s | `%s` | %s | `%s` |" % (conv, (r.get("commit_hoy") or "")[:7], "sí" if r.get("reconstruida") else "no",
                                               (r.get("huella") or "")[:12]))
    L += ["", "## Las nueve", "", "| Id | Conversor | Par | Fuerza | En la rama | Contraste |", "|---|---|---|---|---|---|"]
    for x in estado["nueve"]:
        d = (contraste_.get("discrepancias") or {}).get(x["id_vx"], {})
        c = d.get("decision") or "—"
        if d.get("numero") and c != "no_reportada":
            c += " (#%s)" % d["numero"]
        L.append("| %s | %s | %s | %s | %s | %s |" % (x["id_vx"], x["conversor"], x["par"], x["fuerza"], x["estado"], c))
    L += ["", "## El control", "",
          "Los pares corridos hoy con las versiones fijadas dan %s que en la etapa 20 (`vx/RESULTADO-VX3-minimos.json`): %d "
          "diferencias de veredicto y %d de texto, que se listan y no bloquean (Q-RV-D-4)." % (
              "lo mismo" if control.get("reproduce") else "OTRA COSA",
              sum(1 for d in control.get("diferencias") or [] if d["clase"] == "veredicto"),
              sum(1 for d in control.get("diferencias") or [] if d["clase"] == "texto")), ""]
    if control.get("contaminacion_etapa_20") is not None:
        L += ["Con LinuxForHealth v1.1.0, los pares en lote y mensaje a mensaje dan %s." % (
            "los mismos veredictos" if not control["contaminacion_etapa_20"] else "veredictos distintos en %s" % ", ".join(control["contaminacion_etapa_20"])), ""]
    L += ["## La secuencia del arrastre en `master`", "", "Veredicto: **%s**%s." % (vd, ("; " + "; ".join(secuencia.get("motivos") or [])) if secuencia.get("motivos") else ""), ""]
    return "\n".join(L)


# ---------------------------------------------------------------------------- el orquestador
def git_por_omision(carpeta):
    try:
        h = subprocess.run(["git", "-C", carpeta, "log", "-1", "--format=%h %cI", "--", "PREVISION-RV.json", "SELLO-RV.txt"],
                           capture_output=True, text=True, timeout=60).stdout.strip()
        st = subprocess.run(["git", "-C", carpeta, "status", "--porcelain", "--", "PREVISION-RV.json", "SELLO-RV.txt", "ramas_vxu.py"],
                            capture_output=True, text=True, timeout=60).stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as ex:
        return False, str(ex)
    return bool(h) and not st, h or "sin commit"


def identidades(art):
    r = {"juez": VC.M._version()["huella"]}
    for clave, ad in list(FIJADA.items()) + [("rama_" + k, v) for k, v in RAMA.items()]:
        a = VC.leer_adaptador(ad, art)
        r[clave] = {"huella": VC.huella(a, art), "huella_con_nombres": VC.huella_con_nombres(a, art), "version": a["conversor"]["version"]}
    d = os.path.join(tempfile.mkdtemp(prefix="rv_ident_"), "pares")
    try:
        with redirect_stdout(io.StringIO()):
            MV.escribir(d)
        fs = sorted(os.listdir(d))
        r["pares"] = {"n": len(fs), "vxu_conv": all(VC.punto(open(os.path.join(d, f), encoding="utf-8").read()) == "vxu_conv" for f in fs)}
    finally:
        shutil.rmtree(os.path.dirname(d), ignore_errors=True)
    r["cuadra"] = (r["microsoft"]["huella"] == ESPERADO["microsoft"] and r["lfh_lote"]["huella"] == r["lfh_mensaje"]["huella"] == ESPERADO["linuxforhealth"]
                   and r["rama_lfh_lote"]["huella"] == r["rama_lfh_mensaje"]["huella"] and r["pares"] == {"n": 50, "vxu_conv": True})
    return r


def _pares_y_secuencia(sal):
    p = os.path.join(sal, "pares")
    if not os.path.isdir(p):
        with redirect_stdout(io.StringIO()):
            MV.escribir(p)
    return p


def _filas_por_par(corrida, conv):
    return {(conv, f["caso"]): f for f in AR.filas(corrida)}


def correr(argv=None, ejecutor=None, git=None):
    p = argparse.ArgumentParser(prog="ramas_vxu correr")
    p.add_argument("artefactos")
    p.add_argument("salida")
    p.add_argument("--desde", type=int, default=3)
    p.add_argument("--hasta", type=int, default=8)
    p.add_argument("--sello", default=RV_D)
    a = p.parse_args(argv)
    git = git or git_por_omision
    art, sal = a.artefactos, a.salida
    os.makedirs(sal, exist_ok=True)
    paso = lambda n: a.desde <= n <= a.hasta  # noqa: E731
    try:
        if paso(3):
            r = identidades(art)
            _escribir(os.path.join(sal, "IDENTIDADES-RV.json"), r)
            if not r["cuadra"]:
                print("ramas_vxu: las identidades no cuadran")
                return 1
        if paso(5) or paso(7):
            ok_s = comprobar_sello_rv(os.path.join(a.sello, "PREVISION-RV.json"), os.path.join(a.sello, "SELLO-RV.txt"))
            ok_g, commit = git(a.sello)
            if not (ok_s and ok_g):
                print("ramas_vxu: la previsión no está sellada en un commit")
                return 7
        if paso(5):
            pares = _pares_y_secuencia(sal)
            f = os.path.join(sal, "fijada")
            shutil.rmtree(f, ignore_errors=True)
            os.makedirs(f)
            ms = correr_carpeta(FIJADA["microsoft"], pares, os.path.join(f, "ms"), art, ejecutor)
            ll = correr_carpeta(FIJADA["lfh_lote"], pares, os.path.join(f, "lfh-lote"), art, ejecutor)
            lm = correr_carpeta(FIJADA["lfh_mensaje"], pares, os.path.join(f, "lfh-mensaje"), art, ejecutor)
            sec = secuencia_vl11(art, f, FIJADA["lfh_lote"], FIJADA["lfh_mensaje"], ejecutor)
            rutas = sec.pop("_rutas")
            res = {}
            for modo, lfh in (("lote", ll), ("mensaje", lm)):
                evid = armar(ms, lfh, rutas["lote_caso"], rutas["lote_control"], os.path.join(f, "evid-" + modo))
                res[modo] = juzgar(evid, os.path.join(sal, "RESULTADO-RV-minimos-fijada-%s.json" % modo))
            c = comparar_control(res["lote"], _leer(PUBLICADO))
            c["contaminacion_etapa_20"] = lote_vs_mensaje(AR.filas(ll), AR.filas(lm))
            c["vl11_fijada"] = sec
            c["reproduce"] = c["reproduce"] and not c["contaminacion_etapa_20"] and sec["veredicto"] == "sigue"
            _escribir(os.path.join(sal, "CONTROL-RV.json"), c)
            if not c["reproduce"]:
                print("ramas_vxu: el control no reproduce la etapa 20")
                return 3
        if paso(7):
            ctl = os.path.join(sal, "CONTROL-RV.json")
            if not (os.path.exists(ctl) and _leer(ctl).get("reproduce")):
                print("ramas_vxu: sin el control en «reproduce», no se corre ninguna rama")
                return 3
            pares = _pares_y_secuencia(sal)
            r = os.path.join(sal, "rama")
            shutil.rmtree(r, ignore_errors=True)
            os.makedirs(r)
            ms = correr_carpeta(RAMA["microsoft"], pares, os.path.join(r, "ms"), art, ejecutor)
            lm = correr_carpeta(RAMA["lfh_mensaje"], pares, os.path.join(r, "lfh-mensaje"), art, ejecutor)
            sec = secuencia_vl11(art, r, RAMA["lfh_lote"], RAMA["lfh_mensaje"], ejecutor)
            rutas = sec.pop("_rutas")
            evid = armar(ms, lm, rutas["lote_caso"], rutas["lote_control"], os.path.join(r, "evid"))
            juzgar(evid, os.path.join(sal, "RESULTADO-RV-minimos-main.json"))
            _escribir(os.path.join(sal, "SECUENCIA-RV.json"), sec)
        if paso(8):
            r = os.path.join(sal, "rama")
            filas = dict(_filas_por_par(os.path.join(r, "ms"), "microsoft"))
            filas.update(_filas_por_par(os.path.join(r, "lfh-mensaje"), "linuxforhealth"))
            e = estado_nueve(_leer(os.path.join(sal, "RESULTADO-RV-minimos-fijada-mensaje.json")),
                             _leer(os.path.join(sal, "RESULTADO-RV-minimos-main.json")), filas)
            _escribir(os.path.join(sal, "ESTADO-RV.json"), e)
            print("ramas_vxu: K = %d (%s)" % (e["K"], e["k_por_conversor"]))
    except ErrorAparato as ex:
        print("ramas_vxu: %s" % ex)
        return 4 if "caja" in str(ex) else 2
    except ControlNoPasa as ex:
        print("ramas_vxu: %s" % ex)
        return 3
    print("ramas_vxu: hecho hasta el paso %d" % a.hasta)
    return 0


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a:
        print(__doc__)
        return 1
    if a[0] == "correr":
        return correr(a[1:])
    if a[0] == "ramas":
        res = {}
        for conv, f in (("microsoft", a[1]), ("linuxforhealth", a[2])):
            res[conv] = decidir_ramas(_leer(f), conv)
        _escribir(a[3], res)
        print(json.dumps({k: {x: v[x] for x in ("avanzo", "ahead_by", "reconstruir", "incompleto")} for k, v in res.items()}))
        return 0
    if a[0] == "contraste":
        return contraste(a[1], _leer(a[2]), a[3], comprobar="--comprobar" in a)
    if a[0] == "borradores":
        s = a[1]
        ramas = _leer(os.path.join(s, "RAMAS-RV.json"))
        versiones = {"microsoft": {"fijada": "v7.0 (253307f)", "rama": ramas["microsoft"]["version"]},
                     "linuxforhealth": {"fijada": "v1.1.0 (Maven Central)", "rama": ramas["linuxforhealth"]["version"]}}
        md = borradores(_leer(os.path.join(s, "ESTADO-RV.json")), _leer(os.path.join(s, "CONTRASTE-RV.json")),
                        _leer(os.path.join(s, "SECUENCIA-RV.json")), versiones)
        open(a[2], "w", encoding="utf-8").write(md)
        print("escrito %s" % os.path.basename(a[2]))
        return 0
    if a[0] == "resultado":
        s = a[1]
        md = resultado_md(_leer(os.path.join(s, "ESTADO-RV.json")), _leer(os.path.join(s, "SECUENCIA-RV.json")),
                          _leer(os.path.join(s, "CONTRASTE-RV.json")), _leer(os.path.join(s, "RAMAS-RV.json")),
                          _leer(os.path.join(s, "CONTROL-RV.json")))
        open(a[2], "w", encoding="utf-8").write(md)
        print("escrito %s" % os.path.basename(a[2]))
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
