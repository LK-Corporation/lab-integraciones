#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 22 (vx/rv/diseno-rv-fable.md §9; decisiones de Jev en vx/rv/decision-jev-qrv.md): P-RV-1..12, el aparato que corre los
pares de VXU y la secuencia VL11 con las versiones fijadas y con las ramas principales, decide qué sigue y escribe los
borradores. Corren sin Docker: el conversor de juguete, un ejecutor espía copiado de cv/ar/prueba_ar.py y JSON fabricados.

Antes del código fallan todas: los tres adaptadores de rama y vx/rv/ramas_vxu.py no existen.
  python3 vx/rv/prueba_rv.py          -> TODO BIEN si no hay ningún MAL
  python3 vx/rv/prueba_rv.py rojo     -> sale 0 solo si fallan todas"""
import copy
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import traceback
from contextlib import redirect_stdout

RV_D = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(os.path.dirname(RV_D))
CVD = os.path.join(FASE, "cv")
AR_D = os.path.join(CVD, "ar")
sys.path[:0] = [RV_D, AR_D, CVD, FASE]
sys.argv_guardado, sys.argv = sys.argv, ["x", "--silencio"]
import verificar_conversor as VC  # noqa: E402
import cv3_minimos_vxu as MV  # noqa: E402
from prueba_conversion import msg  # noqa: E402
try:
    import ramas_vxu as RV  # noqa: E402
except ImportError as ex:                                                   # en rojo: el módulo no existe todavía
    RV, ERROR_RV = None, ex
sys.argv = sys.argv_guardado

mal, n_ok, grupo = [], [0], [None]
FALLAN = set()
RAIZ = tempfile.mkdtemp(prefix="prueba_rv_")
DIGEST_LFH = "sha256:7bb84a451705605a47d24eb844d4d9ab03e33e131a507db76aafe25db3907f64"
IN = "/in"                                                                  # compuesto, para la guarda de higiene
PUBLICADO = os.path.join(FASE, "vx", "RESULTADO-VX3-minimos.json")


def mira(nombre, obtenido, esperado):
    if obtenido == esperado:
        n_ok[0] += 1
    else:
        print("  MAL %s %s: %r != %r" % (grupo[0], nombre, obtenido, esperado))
        mal.append(nombre)
        FALLAN.add(grupo[0])


def tmp(nombre="t"):
    return tempfile.mkdtemp(prefix=nombre + "_", dir=RAIZ)


def leer_json(ruta):
    return json.load(open(ruta, encoding="utf-8"))


def adaptador(nombre):
    return leer_json(os.path.join(CVD, "adaptadores", nombre + ".json"))


def ruta_ad(nombre):
    return os.path.join(CVD, "adaptadores", nombre + ".json")


def cambia(d, **cambios):
    d = copy.deepcopy(d)
    for ruta, v in cambios.items():
        partes = ruta.split("__")
        x = d
        for p in partes[:-1]:
            x = x.setdefault(p, {})
        if v == "BORRA":
            x.pop(partes[-1], None)
        else:
            x[partes[-1]] = v
    return d


def escribir_ad(d, carpeta=None):
    ruta = os.path.join(carpeta or tmp("ad"), "adaptador.json")
    with open(ruta, "w", encoding="utf-8") as g:
        g.write(json.dumps(d, ensure_ascii=False))
    return ruta


def con_msh8(t, directiva):
    segs = t.split("\r")
    p = segs[0].split("|")
    p += [""] * max(0, 8 - len(p))
    p[7] = directiva
    segs[0] = "|".join(p)
    return "\r".join(segs)


def artefactos():
    """Las carpetas que piden los adaptadores fijados y los de rama, vacías salvo un fichero."""
    a = tmp("art")
    for d in ("ms/out", "ms/src/data/Templates/Hl7v2", "ms-main/out", "ms-main/src/data/Templates/Hl7v2", "lfh/lib", "lfh/clases",
              "lfh-main/lib", "lfh-main/clases"):
        os.makedirs(os.path.join(a, d))
        open(os.path.join(a, d, "x.txt"), "w").write(d)
    for d in ("ms", "ms-main"):
        open(os.path.join(a, d, "src/data/Templates/Hl7v2/VXU_V04.liquid"), "w").write("{}")
    for d in ("lfh", "lfh-main"):
        open(os.path.join(a, d, "Arnes.java"), "w").write("class Arnes {}")
    return a


class Espia(VC.Ejecutor):
    """Registra las órdenes sin correrlas (como en cv/ar/prueba_ar.py) y guarda lo que hay en la carpeta montada en /in."""
    def __init__(self, digest="img@" + DIGEST_LFH):
        self.corridas, self.consultas, self.digest, self.en_in = [], [], digest, []
        self.matar = True

    def consultar(self, orden):
        self.consultas.append(orden)
        if orden[:2] == ["docker", "version"]:
            return 0, "27.0.0\n"
        if orden[:3] == ["docker", "image", "inspect"]:
            return 0, self.digest + "\n"
        return 0, ""

    def _run(self, orden, timeout):
        self.corridas.append(orden)
        for i, x in enumerate(orden):
            if x == "-v" and orden[i + 1].endswith(":" + IN + ":ro"):
                self.en_in.append(sorted(os.listdir(orden[i + 1][:-len(":" + IN + ":ro")])))
        return 0, ""


def correr_vc(argv, ejecutor=None):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = VC.main(argv, ejecutor=ejecutor)
    return rc, buf.getvalue()


def pares_dir():
    d = os.path.join(tmp("pares"), "p")
    with redirect_stdout(io.StringIO()):
        MV.escribir(d)
    return d


def vl11_dir():
    d = os.path.join(tmp("vl11"), "v")
    with redirect_stdout(io.StringIO()):
        MV.secuencias(d)
    return d


def juguete_id(cid, mensaje=False):
    ad = cambia(adaptador("juguete"), id=cid)
    if mensaje:
        ad = cambia(ad, invocacion__modo="mensaje", invocacion__contenedor="por_mensaje",
                    invocacion__orden=["python3", "conversor_juguete.py", "--fichero", "{entrada_fichero}", "--salida", "{salida_fichero}"])
    return escribir_ad(ad)


def correr_juguete(corpus, cid, mensaje=False):
    salida = os.path.join(tmp("salida"), "s")
    rc, out = correr_vc([juguete_id(cid, mensaje), salida, "--artefactos", CVD, "--sin-corpus-lab", "--sin-minimos", "--sin-sensibilidad",
                         "--json-solo", "--corpus", corpus])
    assert rc == 0, out[-500:]
    return salida


def filas(salida):
    return [json.loads(x) for x in open(os.path.join(salida, "juicio.jsonl"), encoding="utf-8") if x.strip()]


def fila(corpus, caso, cuentan=(), estado="bundle", que=None, conversor="linuxforhealth"):
    cu = [{"hecho": h, "clase": c, "subtipo": s, "que": [que or "%s: %s" % (h, s)]} for h, c, s in cuentan]
    cat, sub = ("fallo_silencioso", "convertido") if cu else ("correcto", None)
    return {"conversor": conversor, "corpus": corpus, "caso": caso, "estado": estado, "categoria": cat, "subtipo": sub, "cuentan": cu}


def publicado():
    return leer_json(PUBLICADO)


def par(res, pid):
    return next(p for p in res["pares"] if p["id"] == pid)


# ---------------------------------------------------------------------------- P-RV-1..12
def p01():
    art = artefactos()
    ms, msm = VC.leer_adaptador(ruta_ad("microsoft"), art), VC.leer_adaptador(ruta_ad("microsoft-main"), art)
    lm, lmm = VC.leer_adaptador(ruta_ad("linuxforhealth-main"), art), VC.leer_adaptador(ruta_ad("linuxforhealth-main-mensaje"), art)
    mira("ids", (msm["id"], lm["id"], lmm["id"]), ("microsoft-main", "linuxforhealth-main", "linuxforhealth-main"))
    v = re.compile(r"^(main|master) \([0-9a-f]{7}, \d{4}-\d\d-\d\d\)")
    mira("versiones con commit y fecha", [bool(v.match(a["conversor"]["version"])) for a in (msm, lm, lmm)], [True] * 3)
    mira("Microsoft: imagen y montajes", (msm["caja"]["imagen"], [m["origen"] for m in msm["caja"]["montajes"].values()]),
         ("mcr.microsoft.com/dotnet/runtime:8.0", ["ms-main/out", "ms-main/src/data/Templates/Hl7v2"]))
    resto = lambda a: (a["invocacion"], a["salida"], a["caja"]["entorno"], a["caja"]["limites"], a["conversor"]["huella"])  # noqa: E731
    mira("Microsoft: lo demás igual a v7.0", resto(msm), resto(ms))
    mira("LinuxForHealth: misma huella en lote y mensaje", VC.huella(lm, art), VC.huella(lmm, art))
    mira("LinuxForHealth: bloques iguales", (lm["caja"], lm["salida"], lm["conversor"]), (lmm["caja"], lmm["salida"], lmm["conversor"]))
    mira("LinuxForHealth: modos", ((lm["invocacion"]["modo"]), (lmm["invocacion"]["modo"], lmm["invocacion"]["contenedor"])),
         ("lote", ("mensaje", "por_mensaje")))
    o = VC.orden_caja(lmm, 1, None, "/T/in", "/T/out", art, ["a.hl7"])
    mira("la orden del mensaje", o[-4:], ["Arnes", IN, "/salida", IN + "/a.hl7"])
    mira("LinuxForHealth: monta lfh-main", [m["origen"] for m in lm["caja"]["montajes"].values()], ["lfh-main/lib", "lfh-main/clases"])
    s = os.path.join(tmp("s"), "s")
    correr_vc([ruta_ad("linuxforhealth-main-mensaje"), s, "--artefactos", art, "--sin-corpus-lab", "--json-solo"], Espia())
    mira("con el id de rama no entran los 68 mínimos", leer_json(os.path.join(s, "CORRIDA.json"))["corpus"]["n"]["minimos"], 0)
    mira("control: v7.0 corre en .NET 6 con ms/out", (ms["caja"]["imagen"], ms["caja"]["montajes"]["codigo"]["origen"]),
         ("mcr.microsoft.com/dotnet/runtime:6.0", "ms/out"))
    s2 = os.path.join(tmp("s"), "s")
    correr_vc([escribir_ad(cambia(leer_json(ruta_ad("linuxforhealth-main-mensaje")), id="linuxforhealth")), s2, "--artefactos", art,
               "--sin-corpus-lab", "--json-solo"], Espia())
    mira("control: con el id del estudio entran", leer_json(os.path.join(s2, "CORRIDA.json"))["corpus"]["n"]["minimos"], 68)


def corridas_juguete():
    p, v = pares_dir(), vl11_dir()
    ms = correr_juguete(p, "jm")
    lfh = correr_juguete(p, "jl", mensaje=True)
    caso = correr_juguete(os.path.join(v, "VL11-estado-fabricante-caso"), "jl")
    control = correr_juguete(os.path.join(v, "VL11-estado-fabricante-control"), "jl")
    return ms, lfh, caso, control


def p02():
    ms, lfh, caso, control = corridas_juguete()
    open(os.path.join(ms, "evidencias", "jm", "propio", "intruso.json"), "w").write("{}")
    evid = tmp("evid")
    RV.armar(ms, lfh, caso, control, evid, ids=("jm", "jl"))
    mira("Microsoft, 50", len([f for f in os.listdir(os.path.join(evid, "microsoft")) if f.endswith(".json")]), 50)
    mira("LinuxForHealth, 50", len([f for f in os.listdir(os.path.join(evid, "linuxforhealth")) if f.endswith(".json")]), 50)
    mira("la secuencia", [os.path.exists(os.path.join(evid, "linuxforhealth", "VL11-estado-fabricante-%s" % s, "L11b.json"))
                          for s in ("caso", "control")], [True, True])
    mira("el intruso no entra", os.path.exists(os.path.join(evid, "microsoft", "intruso.json")), False)
    res = RV.juzgar(evid, os.path.join(tmp("j"), "r.json"))
    mira("26 juzgados", res["de"], 26)
    evid2 = tmp("evid")
    RV.armar(ms, lfh, caso, None, evid2, ids=("jm", "jl"))
    r2 = RV.juzgar(evid2, os.path.join(tmp("j"), "r.json"))
    vl = par(r2, "VL11-estado-fabricante")
    mira("control: sin la secuencia de control, None y no confirmada", (vl["linuxforhealth"]["control"], vl["confirmada"]), (None, False))


def p03():
    pub = publicado()
    nuevo = copy.deepcopy(pub)
    nuevo["juez"] = "b" * 64
    c = RV.comparar_control(nuevo, pub)
    mira("idéntico salvo el juez", (c["reproduce"], c["diferencias"], c["jueces"]), (True, [], sorted([pub["juez"], "b" * 64])))
    n2 = copy.deepcopy(nuevo)
    p = par(n2, "VM07-lote-repetido")
    p["microsoft"]["caso"]["sale"] = not p["microsoft"]["caso"]["sale"]
    c2 = RV.comparar_control(n2, pub)
    mira("un sale invertido", ([d["clase"] for d in c2["diferencias"]], c2["reproduce"]), (["veredicto"], False))
    n3 = copy.deepcopy(nuevo)
    par(n3, "VL04-rxa21-d")["confirmada"] = False
    mira("confirmada cambiada", [d["clase"] for d in RV.comparar_control(n3, pub)["diferencias"]], ["veredicto"])
    n4 = copy.deepcopy(nuevo)
    par(n4, "VM14-dosis-punto-inicial")["microsoft"]["caso"]["que"] = ["otro texto"]
    c4 = RV.comparar_control(n4, pub)
    mira("solo el texto: se lista y no bloquea (Jev)", ([d["clase"] for d in c4["diferencias"]], c4["reproduce"]), (["texto"], True))
    n5 = copy.deepcopy(nuevo)
    par(n5, "VL11-estado-fabricante")["linuxforhealth"]["caso"]["sale"] = False
    mira("la secuencia también", [d["par"] for d in RV.comparar_control(n5, pub)["diferencias"]], ["VL11-estado-fabricante"])
    mira("control: copias idénticas", RV.comparar_control(copy.deepcopy(pub), pub)["diferencias"], [])


def p04():
    fij, main = publicado(), copy.deepcopy(publicado())
    for pid in ("VM08-fabricante-alterno", "VM10-relacion-grd", "VM12-dos-indicaciones", "VM14-dosis-punto-inicial"):
        par(main, pid)["confirmada"] = False
    par(main, "VM08-fabricante-alterno")["microsoft"]["caso"]["sale"] = False
    par(main, "VM10-relacion-grd")["microsoft"]["caso"]["sale"] = False
    par(main, "VM12-dos-indicaciones")["microsoft"]["control"]["sale"] = True
    par(main, "VM14-dosis-punto-inicial")["microsoft"]["caso"]["estado"] = "error"
    par(main, "VM01-cvx-system")["confirmada"] = False                         # de las otras 17: no entra en K
    filas_main = {("microsoft", "VM08-fabricante-alterno-caso"): fila("propio", "x", conversor="microsoft"),
                  ("microsoft", "VM10-relacion-grd-caso"): fila("propio", "x", [("NK1(2)-3", "fidelidad", "dato_perdido")], conversor="microsoft")}
    e = RV.estado_nueve(fij, main, filas_main)
    est = {x["id_vx"]: x["estado"] for x in e["nueve"]}
    mira("estados", est, {"VX-M7": "sigue", "VX-M8": "corregida", "VX-M10": "cambiada", "VX-M12": "par_roto", "VX-M14": "par_roto",
                          "VX-M15": "sigue", "VX-L6": "sigue", "VX-L8": "sigue", "VX-L9": "sigue"})
    mira("K", (e["K"], e["k_por_conversor"]), (5, {"microsoft": 2, "linuxforhealth": 3}))
    mira("cambiadas aparte (Jev)", [x["id_vx"] for x in e["cambiadas"]], ["VX-M10"])
    mira("las otras 17", (len(e["otros_17"]), next(x for x in e["otros_17"] if x["id"] == "VM01-cvx-system")["main"]), (17, False))
    f2 = copy.deepcopy(fij)
    par(f2, "VM07-lote-repetido")["confirmada"] = False
    try:
        RV.estado_nueve(f2, main, filas_main)
        mira("control: la fijada sin las nueve", "sigue", "ControlNoPasa")
    except RV.ControlNoPasa:
        mira("control: la fijada sin las nueve", "ControlNoPasa", "ControlNoPasa")


def compare(ahead, ficheros, n=None):
    return {"ahead_by": ahead, "commits": [{"sha": "a" * 40, "commit": {"committer": {"date": "2026-10-01T00:00:00Z"}, "message": "m\nx"}}] * min(ahead, 3),
            "files": [{"filename": f} for f in (ficheros if n is None else ["src/test/x%d" % i for i in range(n)])]}


def p05():
    mira("no avanzó", {k: v for k, v in RV.decidir_ramas(compare(0, []), "microsoft").items() if k in ("avanzo", "reconstruir")},
         {"avanzo": False, "reconstruir": False})
    r = RV.decidir_ramas(compare(2, ["README.md", "src/Microsoft.Health.Fhir.Liquid.Converter.UnitTests/x.cs", "docs/a.md"]), "microsoft")
    mira("avanzó sin tocar VXU", (r["avanzo"], r["reconstruir"], r["ficheros_vxu"]), (True, False, []))
    mira("una plantilla de VXU", RV.decidir_ramas(compare(1, ["data/Templates/Hl7v2/VXU_V04.liquid"]), "microsoft")["reconstruir"], True)
    mira("Immunization.yml", RV.decidir_ramas(compare(1, ["src/main/resources/hl7/resource/Immunization.yml"]), "linuxforhealth")["reconstruir"], True)
    mira("300 ficheros: incompleto", RV.decidir_ramas(compare(5, [], n=300), "linuxforhealth")["incompleto"], True)
    mira("control: una plantilla de CCDA", RV.decidir_ramas(compare(1, ["data/Templates/Ccda/x.liquid"]), "microsoft")["reconstruir"], False)


RXA17 = ("RXA-17", "fidelidad", "dato_perdido")


def v(*hallazgos):
    return RV.valor(fila("propio", "x", hallazgos, que="Immunization.manufacturer: falta"))


def p06():
    nom, perd = v(), v(RXA17)
    rep = lambda sale, lote, mensaje: {"sale": sale, "motivos": [], "lote_2_L11b": lote, "mensaje_2_L11b": mensaje}  # noqa: E731
    mira("sigue", RV.veredicto_vl11([rep(True, perd, nom)] * 2, nom, True)[0], "sigue")
    mira("no sigue", RV.veredicto_vl11([rep(False, nom, nom)] * 2, nom, False)[0], "no_sigue")
    vd, mot = RV.veredicto_vl11([rep(False, perd, perd)] * 2, perd, False)
    mira("mensaje a mensaje también pierde", (vd, "mensaje a mensaje, 2-L11b también pierde RXA-17" in mot), ("otra_cosa", True))
    mira("repeticiones distintas", RV.veredicto_vl11([rep(True, perd, nom), rep(False, nom, nom)], nom, True)[0], "otra_cosa")
    mira("control: sin el manufacturer en el Bundle", RV.veredicto_vl11([rep(True, perd, nom)] * 2, nom, False)[0], "otra_cosa")


def issue(n, titulo, cuerpo="", estado="open", pr=False):
    d = {"number": n, "title": titulo, "body": cuerpo, "state": estado, "html_url": "https://github.com/o/r/issues/%d" % n,
         "closed_at": None if estado == "open" else "2026-01-01T00:00:00Z"}
    if pr:
        d["pull_request"] = {"url": "x"}
    return d


def p07():
    iss = [issue(1, "lotNumber concatenates repeated RXA-15"), issue(2, "RXA-15 is mapped"), issue(3, "repeated values everywhere"),
           issue(4, "Question about lots"), issue(5, "LOTNUMBER: REPETITION", estado="closed", pr=True),
           issue(6, "ORU reasonCode repeated")]
    com = [{"issue_url": "https://api.github.com/repos/o/r/issues/4", "body": "the rxa-15 repetition is joined with +"}]
    c = RV.candidatos("VX-M7", iss, com)
    mira("campo y efecto", sorted(x["numero"] for x in c), [1, 4, 5])
    mira("cerrados y PR con su estado", next((x["estado"], x["tipo"]) for x in c if x["numero"] == 5), ("closed", "pr"))
    mira("el comentario cuenta", next(x["terminos"] for x in c if x["numero"] == 4) != [], True)
    mira("control: un ORU con reasonCode no es de VX-M7", 6 in [x["numero"] for x in c], False)


def estado_fab():
    nueve = [{"id_vx": i, "par": p, "conversor": cv, "fuerza": "fuerte", "estado": e, "que_main": "observado %s" % i}
             for i, p, cv, e in (("VX-M7", "VM07-lote-repetido", "microsoft", "sigue"), ("VX-L6", "VL04-rxa21-d", "linuxforhealth", "sigue"),
                                 ("VX-M15", "VM15-re-sin-rxa18", "microsoft", "sigue"), ("VX-M8", "VM08-fabricante-alterno", "microsoft", "corregida"),
                                 ("VX-M10", "VM10-relacion-grd", "microsoft", "cambiada"))]
    return {"nueve": nueve, "K": 3, "k_por_conversor": {"microsoft": 2, "linuxforhealth": 1}, "cambiadas": [nueve[4]], "otros_17": []}


def contraste_fab(nula=False):
    d = {"VX-M7": {"decision": "no_reportada"}, "VX-L6": {"decision": "no_reportada"},
         "VX-M15": {"decision": "reportada_abierta", "numero": 77, "cita": "status from RXA-18"},
         "VX-M8": {"decision": "no_reportada"}, "VX-M10": {"decision": None if nula else "no_reportada"}}
    return {"fecha": "2026-10-25", "discrepancias": d, "arrastre": {"decision": "reportada_abierta", "numero": 348}}


VERSIONES = {"microsoft": {"fijada": "v7.0 (253307f)", "rama": "main (abcdef1, 2026-10-01)"},
             "linuxforhealth": {"fijada": "v1.1.0 (Maven Central)", "rama": "master (1234567, 2026-02-11)"}}


def p08():
    sec = {"veredicto": "sigue"}
    md = RV.borradores(estado_fab(), contraste_fab(), sec, VERSIONES)
    secciones = re.findall(r"^### (.+)$", md, re.M)
    mira("dos issues, un comentario y el del #348", (sum(1 for s in secciones if s.startswith("VXU-")),
                                                     sum(1 for s in secciones if "Comment on #77" in s),
                                                     sum(1 for s in secciones if "#348" in s)), (2, 1, 1))
    mira("nada para la corregida ni la cambiada", ("VX-M8" in "".join(secciones), "VX-M10" in "".join(secciones)), (False, False))
    for etiqueta in ("**Title:**", "To reproduce", "Expected", "References", "Versions checked"):
        mira("lleva %s" % etiqueta, md.lower().count(etiqueta.lower()) >= 2, True)
    mira("el caso en líneas", ("\r" in md, "RXA|0|1|" in md), (False, True))
    mira("los dos commits", ("abcdef1" in md, "253307f" in md, "1234567" in md), (True, True, True))
    mira("sin rutas de máquina", VC.RUTA_MAQUINA.search(md), None)
    md2 = RV.borradores(estado_fab(), contraste_fab(), {"veredicto": "no_sigue"}, VERSIONES)
    mira("control: arrastre que no sigue", ("Comment on #348" in md2, "no sigue" in md2), (False, True))
    try:
        RV.borradores(estado_fab(), contraste_fab(nula=True), sec, VERSIONES)
        mira("control: una decisión vacía", "escrito", "excepción")
    except ValueError:
        mira("control: una decisión vacía", "excepción", "excepción")


def prevision(d, quitar=None, p_sigue=None):
    p = {k: 1 for k in RV.CLAVES_PREVISION_RV}
    p["p_sigue"] = p_sigue if p_sigue is not None else {i: {"si_no_toca_vxu": 0.9, "si_toca_vxu": 0.8} for i, _, _, _ in RV.NUEVE}
    if quitar:
        p.pop(quitar)
    open(os.path.join(d, "PREVISION-RV.json"), "w", encoding="utf-8").write(json.dumps(p))
    sha = hashlib.sha256(open(os.path.join(d, "PREVISION-RV.json"), "rb").read()).hexdigest()
    open(os.path.join(d, "SELLO-RV.txt"), "w", encoding="utf-8").write("# sello\n%s  PREVISION-RV.json\n" % sha)
    return os.path.join(d, "PREVISION-RV.json"), os.path.join(d, "SELLO-RV.txt")


def p09():
    d = tmp("sello")
    pj, st = prevision(d)
    mira("cuadra", RV.comprobar_sello_rv(pj, st), True)
    open(pj, "a").write(" ")
    mira("control: un byte", RV.comprobar_sello_rv(pj, st), False)
    mira("control: sin p_sigue", RV.comprobar_sello_rv(*prevision(tmp("sello"), quitar="p_sigue")), False)
    mira("control: p_sigue sin las nueve", RV.comprobar_sello_rv(*prevision(tmp("sello"), p_sigue={"VX-M7": {}})), False)


def p10():
    art, buf = artefactos(), io.StringIO()
    sello_ok = tmp("sello")
    prevision(sello_ok)
    es = Espia()
    with redirect_stdout(buf):
        rc = RV.correr([art, os.path.join(tmp("c"), "s"), "--desde", "5", "--hasta", "5", "--sello", tmp("vacia")], ejecutor=es,
                       git=lambda c: (True, "x"))
    mira("sin sello, 7 y nada corre", (rc, len(es.corridas)), (7, 0))
    sal = os.path.join(tmp("c"), "s")
    os.makedirs(sal)
    open(os.path.join(sal, "CONTROL-RV.json"), "w").write(json.dumps({"reproduce": False}))
    es2 = Espia()
    with redirect_stdout(buf):
        rc = RV.correr([art, sal, "--desde", "7", "--hasta", "7", "--sello", sello_ok], ejecutor=es2, git=lambda c: (True, "x"))
    rama = [o for o in es2.corridas if any("ms-main" in x or "lfh-main" in x for x in o)]
    mira("sin el control, 3 y ninguna rama", (rc, rama), (3, []))
    open(os.path.join(sal, "CONTROL-RV.json"), "w").write(json.dumps({"reproduce": True}))
    es3 = Espia()
    with redirect_stdout(buf):
        rc = RV.correr([art, sal, "--desde", "7", "--hasta", "7", "--sello", sello_ok], ejecutor=es3, git=lambda c: (True, "x"))
    ms = [o for o in es3.corridas if any("ms-main/out" in x for x in o)]
    lfh = [i for o, i in zip(es3.corridas, es3.en_in) if any("lfh-main/lib" in x for x in o)]
    mira("con todo, corre la rama", rc, 0)
    mira("Microsoft en .NET 8", bool(ms) and all("mcr.microsoft.com/dotnet/runtime:8.0" in o for o in ms), True)
    mira("LinuxForHealth mensaje a mensaje: 50 contenedores de uno", sum(1 for i in lfh if len(i) == 1 and i[0][:2] in ("VM", "VL")), 50)
    mira("sin lote de pares en la rama (Jev)", any(len(i) > 2 for i in lfh), False)
    mira("la secuencia en lote", ["1-L11a.hl7", "2-L11b.hl7"] in lfh, True)
    es4 = Espia()
    sal4 = os.path.join(tmp("c"), "s")
    with redirect_stdout(buf):
        RV.correr([art, sal4, "--desde", "5", "--hasta", "5", "--sello", sello_ok], ejecutor=es4, git=lambda c: (True, "x"))
    fij = [o for o in es4.corridas if any("ms/out" in x for x in o)]
    mira("control: las fijadas en .NET 6 con ms/out", bool(fij) and all("mcr.microsoft.com/dotnet/runtime:6.0" in o for o in fij), True)


def p11():
    e = estado_fab()
    sec = {"veredicto": "sigue"}
    ramas = {"microsoft": {"commit_hoy": "abcdef1" + "0" * 33, "reconstruida": False, "huella": "38c6d32b" + "0" * 56},
             "linuxforhealth": {"commit_hoy": "1234567" + "0" * 33, "reconstruida": True, "huella": "28c16067" + "0" * 56}}
    md = RV.resultado_md(e, sec, contraste_fab(), ramas, {"reproduce": True, "diferencias": []})
    mira("la frase", "De las 9 nuevas de VXU, siguen 3 en la rama principal de su conversor (Microsoft 2 de 6, LinuxForHealth 1 de 3); "
                     "el arrastre de estado sigue en `master`" in md, True)
    mira("la tabla de las nueve", all(i in md for i in ("VX-M7", "VX-L6", "VX-M15", "VX-M8", "VX-M10")), True)
    mira("los commits", ("abcdef1" in md, "1234567" in md), (True, True))
    mira("sin rutas de máquina", VC.RUTA_MAQUINA.search(md), None)
    md2 = RV.resultado_md(e, {"veredicto": "no_sigue"}, contraste_fab(), ramas, {"reproduce": True, "diferencias": []})
    mira("no sigue", "el arrastre de estado no sigue en `master`" in md2, True)
    malo = copy.deepcopy(e)
    malo["K"] = 4
    try:
        RV.resultado_md(malo, sec, contraste_fab(), ramas, {"reproduce": True})
        mira("control: K que no cuadra", "escrito", "excepción")
    except ValueError:
        mira("control: K que no cuadra", "excepción", "excepción")


def p12():
    """Control negativo de contaminación con el juguete: lote_vs_mensaje ve un arrastre sembrado y nada sin él."""
    def corpus(con):
        return {"%02d-n" % i: con_msh8(msg("A01"), "JUGUETE-ARRASTRE" if con and i == 3 else "JUGUETE-NOMINAL") for i in range(1, 51)}
    def carpeta(d):
        c = tmp("corpus")
        for n, t in d.items():
            open(os.path.join(c, n + ".hl7"), "w", encoding="utf-8", newline="").write(t)
        return c
    con = carpeta(corpus(True))
    lote, mensaje = filas(correr_juguete(con, "jl")), filas(correr_juguete(con, "jl", mensaje=True))
    mira("lote frente a mensaje ve los 47 siguientes", RV.lote_vs_mensaje(lote, mensaje), ["%02d-n" % i for i in range(4, 51)])
    sin = carpeta(corpus(False))
    mira("control: sin la directiva", RV.lote_vs_mensaje(filas(correr_juguete(sin, "jl")), filas(correr_juguete(sin, "jl", mensaje=True))), [])


PRUEBAS = [p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12]


def main():
    rojo = sys.argv[1:] == ["rojo"]
    if RV is None and not rojo:
        print("  no se importa: %s" % ERROR_RV)
    for p in PRUEBAS:
        grupo[0] = "P-RV-%d" % int(p.__name__[1:])
        try:
            p()
        except Exception as ex:                                             # en rojo, lo esperado es que el código no exista
            FALLAN.add(grupo[0])
            if not rojo:
                print("  EXCEPCIÓN %s: %s" % (grupo[0], "".join(traceback.format_exception(type(ex), ex, ex.__traceback__)[-3:]).strip()[:600]))
                mal.append(grupo[0])
    shutil.rmtree(RAIZ, ignore_errors=True)
    if rojo:
        print("PRUEBAS RV (rojo): fallan %d de %d %s" % (len(FALLAN), len(PRUEBAS), "(TODAS)" if len(FALLAN) == len(PRUEBAS) else ""))
        return 0 if len(FALLAN) == len(PRUEBAS) else 1
    print("PRUEBAS RV: %s (%d comprobaciones, %d pruebas)" % ("TODO BIEN" if not mal else "%d MAL" % len(mal), n_ok[0], len(PRUEBAS)))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
