#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 23 (cv/ci/diseno-ci-fable.md §9; decisiones de Jev en cv/ci/decision-jev-qci.md): P-CI-1..15, la línea base, la siembra
del positivo y los dos flujos de GitHub Actions. Etapa 24 (cv/ci/diseno-ci2-fable.md §8; cv/ci/decision-jev-qci2.md): P-CI-16..26,
los endurecimientos, el proyecto de ejemplo, la forma remota y el run en rojo; P-CI-27, en el segundo push. Etapa 25
(cv/ci/diseno-mant-fable.md §5): P-CI-28..31, las acciones en Node.js 24, y las de la 24 leen las plantillas de github-mant/. Corren sin Docker y sin red, con el conversor de juguete. Los YAML se validan
con PyYAML (la única dependencia, solo de pruebas).

Antes del código fallan todas: linea_base.py, sembrar_juguete.py, POSITIVO-CI.json y los YAML no existen.
  python3 cv/ci/prueba_ci.py          -> TODO BIEN si no hay ningún MAL
  python3 cv/ci/prueba_ci.py rojo     -> sale 0 solo si fallan todas"""
import copy
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import sys
import subprocess
import tempfile
import traceback
from contextlib import redirect_stdout

CI_D = os.path.dirname(os.path.abspath(__file__))
CVD = os.path.dirname(CI_D)
FASE = os.path.dirname(CVD)
sys.path[:0] = [CI_D, CVD, FASE]
sys.argv_guardado, sys.argv = sys.argv, ["x", "--silencio"]
import verificar_conversor as VC  # noqa: E402
from prueba_conversion import msg, oru_msg  # noqa: E402
try:
    import linea_base as LB  # noqa: E402
except ImportError as ex:
    LB, ERROR_LB = None, ex
try:
    import sembrar_juguete as SJ  # noqa: E402
except ImportError as ex:
    SJ, ERROR_SJ = None, ex
try:
    import yaml  # noqa: E402
except ImportError:
    yaml = None
sys.argv = sys.argv_guardado

mal, n_ok, grupo = [], [0], [None]
FALLAN = set()
RAIZ = tempfile.mkdtemp(prefix="prueba_ci_")
JUGUETE = os.path.join(CVD, "conversor_juguete.py")
PID7 = ["PID-7", "fidelidad", "dato_perdido"]
DIGEST = "sha256:7bb84a451705605a47d24eb844d4d9ab03e33e131a507db76aafe25db3907f64"
RUTA = re.compile(r"(/(?:home|datos|tmp|Users|root)/|[A-Za-z]:\\\\)")


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


def escribir_json(ruta, d):
    open(ruta, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    return ruta


def con_msh8(t, directiva):
    segs = t.split("\r")
    p = segs[0].split("|")
    p += [""] * max(0, 8 - len(p))
    p[7] = directiva
    segs[0] = "|".join(p)
    return "\r".join(segs)


def adt(directiva=None, ev="A01"):
    return con_msh8(msg(ev), directiva) if directiva else msg(ev)


def corrida(mensajes, ad="juguete", rc_esperado=0):
    c = tmp("corpus")
    for n, t in mensajes.items():
        open(os.path.join(c, n + ".hl7"), "w", encoding="utf-8", newline="").write(t)
    salida = os.path.join(tmp("salida"), "s")
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = VC.main([os.path.join(CVD, "adaptadores", ad + ".json"), salida, "--artefactos", CVD, "--sin-corpus-lab", "--sin-minimos",
                      "--sin-sensibilidad", "--json-solo", "--corpus", c])
    assert rc == rc_esperado, (rc, buf.getvalue()[-400:])
    return salida


def base_de(salida):
    ruta = os.path.join(tmp("base"), "LINEA-BASE.json")
    rc = LB.main(["crear", salida, "-o", ruta])
    assert rc == 0, rc
    return ruta


def comparar(salida, base, *extra):
    out = tmp("veredicto")
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = LB.main(["comparar", salida, base, "-o", out] + list(extra))
    v = leer_json(os.path.join(out, "VEREDICTO-CI.json")) if os.path.exists(os.path.join(out, "VEREDICTO-CI.json")) else None
    return rc, v, out


def editar_base(base, f):
    d = leer_json(base)
    f(d)
    return escribir_json(os.path.join(tmp("base"), "LINEA-BASE.json"), d)


NOMINALES = {"a": adt(), "b": con_msh8(oru_msg(), "JUGUETE-NOMINAL"), "c": adt(ev="A03")}


def yaml_dir():
    pub = os.path.join(os.path.dirname(FASE), ".github", "workflows")
    if os.path.exists(os.path.join(pub, "verificador-conversor.yml")):
        return pub
    for d in ("github-mant", "github-ci2"):                                  # etapa 25, después la 24; antes, las de la 23
        if os.path.exists(os.path.join(CI_D, d, "verificador-conversor.yml")):
            return os.path.join(CI_D, d)
    return os.path.join(CI_D, "github")


def cargar_yaml(nombre):
    if yaml is None:
        raise RuntimeError("instala pyyaml")
    return yaml.safe_load(open(os.path.join(yaml_dir(), nombre), encoding="utf-8"))


def on(d):
    return d.get("on", d.get(True))                                          # PyYAML lee «on» como True


# ---------------------------------------------------------------------------- P-CI-1..15
def p01():
    s = corrida(dict(NOMINALES, g=adt("JUGUETE-GENERO")))
    b = base_de(s)
    d = leer_json(b)
    mira("formato", d["formato"], "linea-base-ci/1")
    filas = {f["corpus"] + "/" + f["caso"]: json.loads(json.dumps(VC._valor(f))) for f in map(json.loads, open(os.path.join(s, "juicio.jsonl")))}
    mira("casos como _valor", d["casos"], filas)
    mira("identidades", (d["conversor"]["id"], d["conversor"]["modo"], d["n_casos"]), ("juguete", "lote", 4))
    texto = open(b, encoding="utf-8").read()
    mira("sin fechas ni rutas", ("fecha" in texto, RUTA.search(texto)), (False, None))
    b2 = base_de(s)
    mira("determinista", open(b, "rb").read(), open(b2, "rb").read())
    vacia = tmp("vacia")
    mira("control: sin CORRIDA.json", LB.main(["crear", vacia, "-o", os.path.join(vacia, "x.json")]), 2)
    s2 = os.path.join(tmp("copia"), "s")
    shutil.copytree(s, s2)
    inf = leer_json(os.path.join(s2, "INFORME.json"))
    inf.setdefault("no_juzgado", {})["sin_evidencia"] = ["propio/a"]
    escribir_json(os.path.join(s2, "INFORME.json"), inf)
    mira("control: con sin_evidencia", LB.main(["crear", s2, "-o", os.path.join(tmp("x"), "x.json")]), 2)
    mira("control: permitido", LB.main(["crear", s2, "-o", os.path.join(tmp("x"), "x.json"), "--permitir-sin-evidencia"]), 0)


def p02():
    s = corrida(NOMINALES)
    b = base_de(s)
    rc, v, out = comparar(s, b)
    mira("pasa", (rc, v["resultado"], len(v["nuevos"]), len(v["arreglos"])), (0, "pasa", 0, 0))
    mira("igual", comparar(s, b, "--esperar", "igual")[0], 0)
    rc2, v2, out2 = comparar(s, b)
    mira("determinista", open(os.path.join(out, "VEREDICTO-CI.json"), "rb").read(), open(os.path.join(out2, "VEREDICTO-CI.json"), "rb").read())
    mira("propuesta", os.path.exists(os.path.join(out, "LINEA-BASE-propuesta.json")), True)
    b3 = editar_base(b, lambda d: d["casos"]["propio/a"]["hallazgos"].append(["PID-8", "fidelidad", "valor_distinto"]))
    rc3, v3, _ = comparar(s, b3)
    mira("control: un triple de más en la base es un arreglo", (rc3, len(v3["arreglos"])), (0, 1))
    mira("control: en igual falla", comparar(s, b3, "--esperar", "igual")[0], 10)


def p03():
    b = base_de(corrida(NOMINALES))
    s = corrida(dict(NOMINALES, a=adt("JUGUETE-GENERO")))
    rc, v, _ = comparar(s, b)
    mira("hallazgo nuevo", (rc, v["motivos"], v["nuevos_distintos"]), (10, ["hallazgo_nuevo"], [["PID-8", "fidelidad", "valor_distinto"]]))
    b2 = editar_base(b, lambda d: d["casos"]["propio/a"]["hallazgos"].append(["PID-8", "fidelidad", "valor_distinto"]))
    mira("control: el triple ya estaba", comparar(s, b2)[0], 0)


def p04():
    b = base_de(corrida(NOMINALES))
    s = corrida(dict(NOMINALES, d=adt("JUGUETE-GENERO")))
    rc, v, out = comparar(s, b)
    mira("caso nuevo con hallazgos: se lista y no falla (Jev)", (rc, [x["caso"] for x in v["casos_nuevos"]]), (0, ["propio/d"]))
    mira("entra en la propuesta", "propio/d" in leer_json(os.path.join(out, "LINEA-BASE-propuesta.json"))["casos"], True)
    mira("en igual falla", comparar(s, b, "--esperar", "igual")[0], 10)


def p05():
    s = corrida(NOMINALES)
    b = editar_base(base_de(s), lambda d: d["casos"].__setitem__("propio/z", {"estado": "bundle", "categoria": "correcto", "subtipo": None, "hallazgos": []}))
    rc, v, out = comparar(s, b)
    mira("caso ausente: aviso (Jev)", (rc, v["casos_ausentes"], "caso_ausente" in v["avisos"]), (0, ["propio/z"], True))
    mira("la propuesta lo quita", "propio/z" in leer_json(os.path.join(out, "LINEA-BASE-propuesta.json"))["casos"], False)
    mira("en igual falla", comparar(s, b, "--esperar", "igual")[0], 10)


def p06():
    b = base_de(corrida(NOMINALES))
    rc, v, _ = comparar(corrida(dict(NOMINALES, a=adt("JUGUETE-ERROR"))), b)
    mira("salida perdida", (rc, "salida_perdida" in v["motivos"]), (10, True))
    rc2, v2, _ = comparar(corrida(dict(NOMINALES, a=adt("JUGUETE-NADA"))), b)
    mira("indeterminado nuevo", (rc2, "indeterminado_nuevo" in v2["motivos"]), (10, True))
    b2 = base_de(corrida(dict(NOMINALES, a=adt("JUGUETE-ERROR"))))
    rc3, v3, _ = comparar(corrida(dict(NOMINALES, a=adt("JUGUETE-NOMINAL"))), b2)      # DV-CI-1: el nominal sale correcto
    mira("control: al revés es un arreglo", (rc3, len(v3["arreglos"]) > 0), (0, True))


def p07():
    s = corrida(NOMINALES)
    b = base_de(s)
    rc, v, _ = comparar(s, b, "--rc-herramienta", "4")
    mira("caja", (rc, "caja" in v["motivos"]), (10, True))
    mira("otro conversor", comparar(s, editar_base(b, lambda d: d["conversor"].__setitem__("id", "otro")))[0], 2)
    bj = editar_base(b, lambda d: d["creada_de"]["juez"].__setitem__("huella", "0" * 64))
    rc2, v2, out2 = comparar(s, bj)
    mira("otro juez: aviso, y la propuesta lo marca (Jev)", (rc2, "juez_distinto" in v2["avisos"],
                                                             leer_json(os.path.join(out2, "LINEA-BASE-propuesta.json")).get("juez_cambiado")), (0, True, True))
    mira("otro juez en igual falla", comparar(s, bj, "--esperar", "igual")[0], 10)
    bh = editar_base(b, lambda d: d["conversor"].__setitem__("huella", "1" * 64))
    mira("otra huella: aviso también en igual", (comparar(s, bh)[0], comparar(s, bh, "--esperar", "igual")[0]), (0, 0))


def p08():
    b = base_de(corrida(NOMINALES))
    esperado = json.dumps([["PID-8", "fidelidad", "valor_distinto"]])
    s_nuevo = corrida(dict(NOMINALES, a=adt("JUGUETE-GENERO")))
    mira("falla por el esperado", comparar(s_nuevo, b, "--esperar", "falla", "--hallazgo-esperado", esperado)[0], 0)
    mira("control: no falla", comparar(corrida(NOMINALES), b, "--esperar", "falla", "--hallazgo-esperado", esperado)[0], 10)
    mira("control: otro triple", comparar(s_nuevo, b, "--esperar", "falla", "--hallazgo-esperado", json.dumps([PID7]))[0], 10)
    s_dos = corrida(dict(NOMINALES, a=adt("JUGUETE-GENERO"), c=adt("JUGUETE-ERROR", ev="A03")))
    mira("control: el esperado y otra cosa", comparar(s_dos, b, "--esperar", "falla", "--hallazgo-esperado", esperado)[0], 10)


def cargar_copia(ruta):
    spec = importlib.util.spec_from_file_location("juguete_copia_%d" % len(os.listdir(RAIZ)), ruta)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def p09():
    d = tmp("siembra")
    copia = os.path.join(d, "conversor_juguete.py")
    shutil.copyfile(JUGUETE, copia)
    original = open(copia, "rb").read()
    mira("siembra", SJ.main([copia]), 0)
    j = cargar_copia(copia)
    _, gen = j.convertir(adt())
    _, nom = j.convertir(adt("JUGUETE-NOMINAL"))
    mira("el genérico pierde birthDate, el nominal no", ("birthDate" in gen, "birthDate" in nom), (False, True))
    mira("deshacer", (SJ.main([copia, "--deshacer"]), open(copia, "rb").read() == original), (0, True))
    otro = os.path.join(d, "otro.py")
    open(otro, "w").write("print(1)\n")
    mira("control: sin el texto", (SJ.main([otro]), open(otro).read()), (2, "print(1)\n"))


def p10():
    s_a = corrida({"a": adt(), "b": adt(ev="A03"), "c": adt(ev="A04"), "d": con_msh8(oru_msg(), "JUGUETE-NOMINAL")})
    b = base_de(s_a)
    esperado = json.dumps(leer_json(os.path.join(CI_D, "POSITIVO-CI.json"))["hallazgo_esperado"])
    original = open(JUGUETE, "rb").read()
    try:
        assert SJ.main([JUGUETE]) == 0
        s_b = corrida({"a": adt(), "b": adt(ev="A03"), "c": adt(ev="A04"), "d": con_msh8(oru_msg(), "JUGUETE-NOMINAL")})
    finally:
        open(JUGUETE, "wb").write(original)
    rc, v, _ = comparar(s_b, b, "--esperar", "falla", "--hallazgo-esperado", esperado)
    mira("el positivo, de punta a punta", (rc, v["nuevos_distintos"]), (0, [PID7]))
    mira("control: con pasa falla", comparar(s_b, b)[0], 10)
    mira("control: sin sembrar, falla no se cumple", comparar(s_a, b, "--esperar", "falla", "--hallazgo-esperado", esperado)[0], 10)
    mira("el juguete quedó como estaba", open(JUGUETE, "rb").read() == original, True)


ENTRADAS = {"adaptador", "artefactos", "preparar", "linea_base", "imagen", "corpus", "sin_corpus_lab", "opciones", "esperar",
            "hallazgo_esperado", "huella_esperada", "laboratorio", "laboratorio_ref", "sembrar", "artefacto_completo", "nombre"}
SALIDAS = {"resultado", "nuevos", "nuevos_distintos", "arreglos", "huella", "imagen_digest", "juez"}


def acciones(d):
    out = []
    for j in d["jobs"].values():
        for s in j.get("steps") or []:
            if "uses" in s:
                out.append(s["uses"])
    return out


def guarda_flujo(d):
    """-> lista de problemas del flujo reutilizable (vacía si está bien)."""
    p = []
    wc = (on(d) or {}).get("workflow_call") or {}
    if set(wc.get("inputs") or {}) != ENTRADAS:
        p.append("entradas")
    if set(wc.get("outputs") or {}) != SALIDAS:
        p.append("salidas")
    if d.get("permissions") != {"contents": "read"} or "secrets" in wc:
        p.append("permisos")
    for j in d["jobs"].values():
        if "permissions" in j and j["permissions"] != {"contents": "read"}:
            p.append("permisos del job")
        if j.get("runs-on") != "ubuntu-latest" or "timeout-minutes" not in j:
            p.append("runner o tiempo")
    for u in acciones(d):
        if not re.match(r"^actions/[\w-]+@(v\d+|[0-9a-f]{40})$", u):
            p.append("acción %s" % u)
    return p


def p11():
    d = cargar_yaml("verificador-conversor.yml")
    mira("el flujo reutilizable, bien", guarda_flujo(d), [])
    demo = cargar_yaml("demo-ci.yml")
    mira("la demo, solo lectura", (demo.get("permissions"), all(j.get("permissions", {"contents": "read"}) == {"contents": "read"}
                                                                  for j in demo["jobs"].values())), ({"contents": "read"}, True))
    malo = copy.deepcopy(d)
    malo["permissions"] = {"contents": "write"}
    mira("control: contents write", "permisos" in guarda_flujo(malo), True)
    malo2 = copy.deepcopy(d)
    on(malo2)["workflow_call"]["inputs"].pop("imagen")
    mira("control: una entrada menos", "entradas" in guarda_flujo(malo2), True)
    malo3 = copy.deepcopy(d)
    next(iter(malo3["jobs"].values()))["steps"].append({"uses": "otro/accion@main"})
    mira("control: una acción de fuera", any(x.startswith("acción") for x in guarda_flujo(malo3)), True)


def runs(d):
    return [s.get("run", "") for j in d["jobs"].values() for s in j.get("steps") or []]


def guarda_caja(d):
    p = []
    todo = "\n".join(runs(d))
    if re.search(r"docker\s+run", todo):
        p.append("docker run")
    for m in re.finditer(r"\bdocker\s+(\w+)", todo):
        if m.group(1) not in ("version", "pull", "image", "tag"):
            p.append("docker %s" % m.group(1))
    verif = [r for r in runs(d) if "cv/verificar_conversor.py" in r and "--solo-orden" not in r]
    if not verif or any("--comparar" in r or "--muestras" in r for r in verif):
        p.append("la orden de verificar")
    if not any("GITHUB_STEP_SUMMARY" in r and "--github-output" in r for r in runs(d)):
        p.append("el resumen")
    return p


def p12():
    d = cargar_yaml("verificador-conversor.yml")
    mira("la caja, solo la de la herramienta", guarda_caja(d), [])
    malo = copy.deepcopy(d)
    next(iter(malo["jobs"].values()))["steps"].append({"run": "docker run --privileged algo"})
    mira("control: un docker run", "docker run" in guarda_caja(malo), True)


def guarda_demo(d):
    p = []
    o = on(d)
    if (o.get("push") or {}).get("branches") != ["main"] or set((o.get("push") or {}).get("paths") or []) != {
            "verificador/**", ".github/workflows/**", "tests/**"}:
        p.append("push")
    if "modo_real" not in ((o.get("workflow_dispatch") or {}).get("inputs") or {}):
        p.append("workflow_dispatch")
    if not (d.get("concurrency") or {}).get("cancel-in-progress"):
        p.append("concurrency")
    j = d["jobs"]
    for n in ("negativo", "positivo", "real"):
        if j.get(n, {}).get("uses") != "./.github/workflows/verificador-conversor.yml" or j[n]["with"].get("laboratorio_ref") != "${{ github.sha }}":
            p.append(n)
    pos = (j.get("positivo") or {}).get("with") or {}
    esperado = leer_json(os.path.join(CI_D, "POSITIVO-CI.json"))["hallazgo_esperado"]
    if pos.get("sembrar") != "juguete" or pos.get("esperar") != "falla" or json.loads(pos.get("hallazgo_esperado", "[]")) != esperado:
        p.append("positivo con")
    real = (j.get("real") or {}).get("with") or {}
    if DIGEST not in real.get("imagen", "") or real.get("huella_esperada") != "ac41f71b98ee75bac637ecd4b68f58b463f0798bf66cfa941f4194cb2a50acf2" \
            or real.get("esperar") != "igual" or "LINEA-BASE-linuxforhealth" not in real.get("linea_base", ""):
        p.append("real con")
    if ((j.get("negativo") or {}).get("with") or {}).get("esperar") != "igual":
        p.append("negativo con")
    if (j.get("positivo-comprobado") or {}).get("needs") != "positivo" or (j.get("real-comprobado") or {}).get("needs") != "real":
        p.append("comprobados")
    return p


def p13():
    d = cargar_yaml("demo-ci.yml")
    mira("la demo", guarda_demo(d), [])
    malo = copy.deepcopy(d)
    malo["jobs"]["positivo"]["with"]["hallazgo_esperado"] = '[["PID-8", "fidelidad", "valor_distinto"]]'
    mira("control: otro hallazgo esperado", "positivo con" in guarda_demo(malo), True)
    malo2 = copy.deepcopy(d)
    malo2["jobs"]["positivo"]["with"]["esperar"] = "pasa"
    mira("control: el positivo con pasa", "positivo con" in guarda_demo(malo2), True)


def artefactos_lfh():
    a = tmp("art")
    for x in ("lfh/lib", "lfh/clases"):
        os.makedirs(os.path.join(a, x))
        open(os.path.join(a, x, "x.txt"), "w").write(x)
    open(os.path.join(a, "lfh/Arnes.java"), "w").write("class Arnes {}")
    return a


def p14():
    art = artefactos_lfh()
    copia = os.path.join(tmp("ad"), "adaptador.json")
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = LB.main(["fijar-imagen", os.path.join(CVD, "adaptadores", "linuxforhealth.json"), "maven:3.9-eclipse-temurin-11@" + DIGEST, "-o", copia, "--etiquetar"])
    mira("fijar la imagen", (rc, leer_json(copia)["caja"]["imagen_digest"]), (0, DIGEST))
    mira("la orden de etiquetar", buf.getvalue().strip(), "docker tag maven@%s maven:3.9-eclipse-temurin-11" % DIGEST)
    mira("la copia vale", VC.leer_adaptador(copia, art)["caja"]["imagen_digest"], DIGEST)
    copia2 = os.path.join(tmp("ad"), "adaptador.json")
    mira("proceso local, sin cambios", (LB.main(["fijar-imagen", os.path.join(CVD, "adaptadores", "juguete.json"), "", "-o", copia2]),
                                        leer_json(copia2) == leer_json(os.path.join(CVD, "adaptadores", "juguete.json"))), (0, True))
    mira("control: otro repositorio", LB.main(["fijar-imagen", os.path.join(CVD, "adaptadores", "linuxforhealth.json"), "python@" + DIGEST, "-o", copia]), 2)
    mira("control: digest mal formado", LB.main(["fijar-imagen", os.path.join(CVD, "adaptadores", "linuxforhealth.json"), "maven@sha256:123", "-o", copia]), 2)
    for n, cid in (("LINEA-BASE-juguete.json", "juguete"), ("LINEA-BASE-linuxforhealth.json", "linuxforhealth"),
                   ("LINEA-BASE-linuxforhealth-mensaje.json", "linuxforhealth")):
        ruta = os.path.join(CI_D, n)
        if os.path.exists(ruta):
            d = leer_json(ruta)
            mira("la base publicada %s" % n, (d["formato"], d["n_casos"] == len(d["casos"]), d["conversor"]["id"]), ("linea-base-ci/1", True, cid))


def cuerpo_de_paso(d, id_paso):
    for j in d["jobs"].values():
        for s in j.get("steps") or []:
            if s.get("id") == id_paso:
                return s["run"]
    raise KeyError(id_paso)


def con_fallo(t, rc):
    """El cuerpo de un paso sin expresiones y con su orden python3 (y sus líneas de continuación) cambiada por una que sale con rc."""
    lineas, out, i = re.sub(r"\$\{\{.*?\}\}", "x", t).splitlines(), [], 0
    while i < len(lineas):
        if lineas[i].lstrip().startswith("python3 "):
            while lineas[i].rstrip().endswith("\\"):
                i += 1
            out.append("(exit %d)" % rc)
        else:
            out.append(lineas[i])
        i += 1
    return "\n".join(out) + "\n"


def paso_de_github(cuerpo, ws, env):
    """Como corre GitHub un paso con «shell: bash»: bash --noprofile --norc -eo pipefail."""
    g = os.path.join(ws, "paso.sh")
    open(g, "w", encoding="utf-8").write(cuerpo)
    return subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", g], cwd=ws, env=dict(os.environ, **env),
                          capture_output=True, text=True).returncode


def p15():
    """Tras la revisión a ciegas: los pasos que recogen un código de salida siguen tras él con el -e que pone GitHub."""
    d = cargar_yaml("verificador-conversor.yml")
    w = tmp("p15")
    os.makedirs(os.path.join(w, "lab", "verificador"))
    os.makedirs(os.path.join(w, "trabajo", "corrida"))
    open(os.path.join(w, "trabajo", "corrida", "VEREDICTO-CI.md"), "w", encoding="utf-8").write("## Verificador: FALLA\n")
    salida, resumen = os.path.join(w, "salida"), os.path.join(w, "resumen.md")
    env = {"GITHUB_OUTPUT": salida, "GITHUB_STEP_SUMMARY": resumen, "GITHUB_WORKSPACE": w}

    def correr(id_paso, rc, cambio=None):
        for f in (salida, resumen):
            open(f, "w").close()
        cuerpo = con_fallo(cuerpo_de_paso(d, id_paso), rc)
        entorno = dict(entorno_de(d, id_paso, rc), **env)                    # etapa 24: las entradas llegan por env:
        return paso_de_github(cambio(cuerpo) if cambio else cuerpo, w, entorno), open(salida).read(), open(resumen).read()

    rc, _, res = correr("veredicto", 10)
    mira("veredicto: con 10, el resumen se escribe y el paso sale con 10", (rc, res), (10, "## Verificador: FALLA\n"))
    rc, sal, _ = correr("verificar", 4)
    mira("verificar: con 4 (caja), deja rc=4 y el paso sigue", (rc, "rc=4" in sal), (0, True))
    rc, sal, _ = correr("verificar", 2)
    mira("verificar: con 2, deja rc=2 y el paso falla con 2", (rc, "rc=2" in sal), (2, True))
    rc, _, res = correr("veredicto", 10, lambda c: c.replace("set +e", ":"))
    mira("control: sin «set +e», el -e de GitHub corta el paso antes del resumen", (rc, res), (10, ""))


# ---------------------------------------------------------------------------- P-CI-16..26 (etapa 24, cv/ci/diseno-ci2-fable.md §8)
ACCIONES_JSON = os.path.join(CI_D, "ACCIONES-CI.json")
LK_REMOTO = re.compile(r"^LK-Corporation/lab-integraciones/\.github/workflows/verificador-conversor\.yml@(COMMIT_C1|COMMIT_M1|[0-9a-f]{40})$")
USO_ACCION = re.compile(r"^\s*-?\s*uses: actions/([\w-]+)@([0-9a-f]{40})  # (v\d+\.\d+\.\d+)$")


def plantillas_dir():
    return os.path.join(CI_D, "github-mant")                                  # etapa 25; las de la 24, en github-ci2/


def ejemplo_dir():
    """ejemplo-ci/ está en la raíz del repositorio público; en el laboratorio, dentro de su árbol."""
    pub = os.path.join(os.path.dirname(FASE), "ejemplo-ci")
    return pub if os.path.exists(os.path.join(pub, "conversor.py")) else os.path.join(FASE, "ejemplo-ci")


def ficheros_yaml():
    """Los YAML que corren y las plantillas selladas, sin repetir ruta."""
    rutas = []
    for d in (yaml_dir(), plantillas_dir()):
        if os.path.isdir(d):
            rutas += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".yml")]
    return sorted(set(os.path.realpath(r) for r in rutas))


def cargar(ruta):
    return yaml.safe_load(open(ruta, encoding="utf-8"))


def runs_con_expresion(d):
    return ["%s/%s" % (jn, s.get("name") or s.get("id") or "?") for jn, j in (d.get("jobs") or {}).items()
            for s in j.get("steps") or [] if "${{" in (s.get("run") or "")]


def p16():
    """Ninguna ${{ }} dentro de un run: en ningún YAML (S-CI2-1)."""
    fs = ficheros_yaml()
    mira("hay YAML que mirar (los que corren y las plantillas de la 24)",
         len(fs) >= 3 and any(os.sep + "github-mant" + os.sep in f for f in fs), True)
    mira("ningún run: con ${{", {os.path.basename(f): runs_con_expresion(cargar(f)) for f in fs if runs_con_expresion(cargar(f))}, {})
    malo = {"jobs": {"j": {"steps": [{"run": "echo ${{ inputs.x }}"}]}}}
    bueno = {"jobs": {"j": {"steps": [{"run": "echo $IN_X", "env": {"IN_X": "${{ inputs.x }}"}}]}}}
    mira("control: run con ${{ inputs.x }}", runs_con_expresion(malo), ["j/?"])
    mira("control: con env, nada", runs_con_expresion(bueno), [])


def guarda_acciones(textos, acciones):
    """textos: {nombre: texto crudo del YAML}. -> lista de problemas."""
    p = []
    if acciones.get("formato") != "acciones-ci/1" or set(acciones.get("acciones") or {}) != {
            "actions/checkout", "actions/setup-python", "actions/upload-artifact", "actions/download-artifact"}:
        p.append("ACCIONES-CI.json")
    for a, x in (acciones.get("acciones") or {}).items():
        if not re.match(r"^[0-9a-f]{40}$", x.get("sha", "")) or not re.match(r"^v\d+\.\d+\.\d+$", x.get("etiqueta", "")):
            p.append("ACCIONES-CI.json %s" % a)
    for n, t in textos.items():
        for i, l in enumerate(t.splitlines(), 1):
            m = re.match(r"^\s*-?\s*uses:\s*(\S+)", l)
            if not m:
                continue
            v = m.group(1)
            if v.startswith("actions/"):
                ma = USO_ACCION.match(l)
                x = (acciones.get("acciones") or {}).get("actions/" + ma.group(1), {}) if ma else {}
                if not ma or (ma.group(2), ma.group(3)) != (x.get("sha"), x.get("etiqueta")):
                    p.append("%s:%d acción" % (n, i))
            elif v != "./.github/workflows/verificador-conversor.yml" and not LK_REMOTO.match(v):
                p.append("%s:%d flujo" % (n, i))
    return p


def p17():
    """Toda acción por commit, con su etiqueta, el mismo commit en todos los YAML (S-CI2-2)."""
    acciones = leer_json(ACCIONES_JSON)
    textos = {os.path.basename(f) + ("@plantilla" if "github-mant" in f else ""): open(f, encoding="utf-8").read() for f in ficheros_yaml()}
    mira("las acciones, por commit y con su etiqueta", guarda_acciones(textos, acciones), [])
    sha = acciones["acciones"]["actions/checkout"]["sha"]
    et = acciones["acciones"]["actions/checkout"]["etiqueta"]
    mira("control: por etiqueta", guarda_acciones({"x": "      - uses: actions/checkout@v4\n"}, acciones), ["x:1 acción"])
    mira("control: un commit que no es el del JSON", guarda_acciones({"x": "      - uses: actions/checkout@%s  # %s\n" % ("0" * 40, et)}, acciones), ["x:1 acción"])
    mira("control: otra etiqueta en el comentario", guarda_acciones({"x": "      - uses: actions/checkout@%s  # v9.9.9\n" % sha}, acciones), ["x:1 acción"])
    mira("control: un flujo de fuera en main", guarda_acciones({"x": "    uses: otro/flujo/.github/workflows/x.yml@main\n"}, acciones), ["x:1 flujo"])
    mira("control: el bueno", guarda_acciones({"x": "      - uses: actions/checkout@%s  # %s\n" % (sha, et)}, acciones), [])


def entorno_de(d, id_paso, rc="0", **cambios):
    """El env: de un paso con ${{ inputs.k }} -> el default declarado y ${{ steps.verificar.outputs.rc }} -> rc."""
    entradas = on(d)["workflow_call"]["inputs"]
    paso = next(s for j in d["jobs"].values() for s in j.get("steps") or [] if s.get("id") == id_paso or s.get("name") == id_paso)
    env = {}
    for k, v in (paso.get("env") or {}).items():
        m = re.match(r"^\$\{\{ inputs\.(\w+) \}\}$", str(v))
        if m:
            x = entradas[m.group(1)].get("default", "")
            env[k] = "true" if x is True else "false" if x is False else str(x)
        elif str(v) == "${{ steps.verificar.outputs.rc }}":
            env[k] = str(rc)
        else:
            env[k] = re.sub(r"\$\{\{.*?\}\}", "x", str(v))
    env.update(cambios)
    return env


def paso_con_salida(cuerpo, ws, env):
    g = os.path.join(ws, "paso.sh")
    open(g, "w", encoding="utf-8").write(cuerpo)
    r = subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", g], cwd=ws, env=dict(os.environ, **env), capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def guarda_ref(d):
    e = on(d)["workflow_call"]["inputs"]["laboratorio_ref"]
    return [] if e.get("required") is True and "default" not in e else ["laboratorio_ref"]


def p18():
    """laboratorio_ref obligatoria y de 40 hex (S-CI2-3)."""
    d = cargar_yaml("verificador-conversor.yml")
    mira("laboratorio_ref obligatoria, sin valor por omisión", guarda_ref(d), [])
    malo = copy.deepcopy(d)
    on(malo)["workflow_call"]["inputs"]["laboratorio_ref"] = {"type": "string", "required": False, "default": "main"}
    mira("control: con default main", guarda_ref(malo), ["laboratorio_ref"])
    w = tmp("p18")
    cuerpo = cuerpo_de_paso(d, "entradas")
    for ref in ("main", "v1.2"):
        rc, out = paso_con_salida(cuerpo, w, dict(entorno_de(d, "entradas", IN_LABORATORIO_REF=ref, IN_ADAPTADOR="no-existe.json"),
                                                 GITHUB_OUTPUT=os.path.join(w, "salida")))
        mira("«Entradas» con laboratorio_ref=%s: 2 y el motivo" % ref, (rc, "40 hex" in out), (2, True))
    rc, out = paso_con_salida(cuerpo, w, dict(entorno_de(d, "entradas", IN_LABORATORIO_REF="a" * 40, IN_ADAPTADOR="no-existe.json"),
                                             GITHUB_OUTPUT=os.path.join(w, "salida")))
    mira("con 40 hex pasa esa línea y llega al adaptador", (rc, "40 hex" in out, "no existe el adaptador" in out), (2, False, True))
    mira("las entradas no cambian", set(on(d)["workflow_call"]["inputs"]), ENTRADAS)


def guarda_env(d):
    p = []
    for j in d["jobs"].values():
        for s in j.get("steps") or []:
            if "run" not in s:
                continue
            env = s.get("env") or {}
            for v in set(re.findall(r"\$\{?(IN_[A-Z_]+|RC_HERRAMIENTA)\b", s["run"])):
                if v not in env:
                    p.append("%s sin %s" % (s.get("name"), v))
            for k, v in env.items():
                if k.startswith("IN_") and v != "${{ inputs.%s }}" % k[3:].lower():
                    p.append("%s: %s" % (s.get("name"), k))
                if k == "RC_HERRAMIENTA" and v != "${{ steps.verificar.outputs.rc }}":
                    p.append("%s: %s" % (s.get("name"), k))
    return p


def p19():
    """Cada $IN_X de un run: está en el env: de su paso, y vale ${{ inputs.x }} (S-CI2-1)."""
    d = cargar_yaml("verificador-conversor.yml")
    mira("las variables, declaradas y bien conectadas", guarda_env(d), [])
    nombres = {s.get("id"): s for j in d["jobs"].values() for s in j.get("steps") or []}
    mira("«Verificar» usa IN_CORPUS", "IN_CORPUS" in (nombres["verificar"].get("env") or {}), True)
    malo = copy.deepcopy(d)
    next(s for j in malo["jobs"].values() for s in j["steps"] if s.get("id") == "verificar")["env"].pop("IN_CORPUS")
    mira("control: sin IN_CORPUS en el env:", any("sin IN_CORPUS" in x for x in guarda_env(malo)), True)
    malo2 = copy.deepcopy(d)
    next(s for j in malo2["jobs"].values() for s in j["steps"] if s.get("id") == "verificar")["env"]["IN_CORPUS"] = "${{ inputs.opciones }}"
    mira("control: IN_CORPUS con la entrada que no es", any(x.endswith(": IN_CORPUS") for x in guarda_env(malo2)), True)


def con_laboratorio(d, jobs):
    return {n: ((d.get("jobs") or {}).get(n, {}).get("with") or {}).get("laboratorio") for n in jobs}


def p20():
    """El laboratorio de la demo, el del repositorio que corre; el de los ejemplos, escrito (S-CI2-4)."""
    demo = cargar_yaml("demo-ci.yml")
    mira("la demo, con github.repository", con_laboratorio(demo, ("negativo", "positivo", "real")),
         {n: "${{ github.repository }}" for n in ("negativo", "positivo", "real")})
    mira("el flujo conserva el valor por omisión", on(cargar_yaml("verificador-conversor.yml"))["workflow_call"]["inputs"]["laboratorio"].get("default"),
         "LK-Corporation/lab-integraciones")
    ej, ro = cargar(os.path.join(plantillas_dir(), "ejemplo-ci.yml")), cargar(os.path.join(plantillas_dir(), "rojo-ci.yml"))
    mira("los ejemplos, con el laboratorio escrito", (con_laboratorio(ej, ("ejemplo", "ejemplo-propio")), con_laboratorio(ro, ("rojo",))),
         ({"ejemplo": "LK-Corporation/lab-integraciones", "ejemplo-propio": "LK-Corporation/lab-integraciones"}, {"rojo": "LK-Corporation/lab-integraciones"}))
    malo = copy.deepcopy(demo)
    malo["jobs"]["real"]["with"]["laboratorio"] = "LK-Corporation/lab-integraciones"
    mira("control: la demo con el nombre escrito", con_laboratorio(malo, ("real",)) == {"real": "${{ github.repository }}"}, False)


def digest_del_adaptador():
    return leer_json(os.path.join(ejemplo_dir(), "ci", "adaptador.json"))["caja"]["imagen_digest"]


def guarda_ejemplo(d):
    p = []
    o = on(d) or {}
    rutas = {"ejemplo-ci/**", ".github/workflows/**", "verificador/**"}
    if (o.get("push") or {}).get("branches") != ["main"] or set((o.get("push") or {}).get("paths") or []) != rutas \
            or set((o.get("pull_request") or {}).get("paths") or []) != rutas or "workflow_dispatch" not in o:
        p.append("on")
    if not (d.get("concurrency") or {}).get("cancel-in-progress") or d.get("permissions") != {"contents": "read"}:
        p.append("concurrency o permisos")
    j = d.get("jobs") or {}
    refs = set()
    for n in ("ejemplo", "ejemplo-propio"):
        x = j.get(n) or {}
        w = x.get("with") or {}
        m = LK_REMOTO.match(x.get("uses", ""))
        if not m or x.get("permissions") != {"contents": "read"} or w.get("laboratorio_ref") != m.group(1):
            p.append(n + " forma remota")
            continue
        refs.add(m.group(1))
        if not w.get("adaptador", "").startswith("proyecto/ejemplo-ci/") or not w.get("linea_base", "").startswith("proyecto/ejemplo-ci/") \
                or w.get("corpus") != "proyecto/ejemplo-ci/corpus" or w.get("esperar", "pasa") != "pasa" \
                or not w.get("imagen", "").endswith("@" + digest_del_adaptador()) or w.get("nombre") != n:
            p.append(n + " con")
    if len(refs) > 1:
        p.append("dos refs")
    ej, pr = (j.get("ejemplo") or {}).get("with") or {}, (j.get("ejemplo-propio") or {}).get("with") or {}
    if pr.get("sin_corpus_lab") is not True or pr.get("artefacto_completo") is not True or "--json-solo" not in pr.get("opciones", ""):
        p.append("ejemplo-propio entradas")
    if ej.get("sin_corpus_lab") or ej.get("artefacto_completo") or "--json-solo" in ej.get("opciones", ""):
        p.append("ejemplo entradas")
    c = j.get("ejemplo-comprobado") or {}
    bajadas = [(s.get("with") or {}).get("name") for s in c.get("steps") or [] if str(s.get("uses", "")).startswith("actions/download-artifact@")]
    if sorted(c.get("needs") or []) != ["ejemplo", "ejemplo-propio"] or bajadas != ["ejemplo-${{ github.run_attempt }}", "ejemplo-propio-${{ github.run_attempt }}"]:
        p.append("ejemplo-comprobado")
    return p


def p21():
    """La plantilla de ejemplo-ci.yml: la forma remota, dos llamadas y su comprobación (§4.2)."""
    d = cargar(os.path.join(plantillas_dir(), "ejemplo-ci.yml"))
    mira("ejemplo-ci.yml", guarda_ejemplo(d), [])
    for n, f, motivo in (("laboratorio_ref distinto del uses:", lambda x: x["jobs"]["ejemplo"]["with"].__setitem__("laboratorio_ref", "b" * 40), "ejemplo forma remota"),
                         ("esperar: igual", lambda x: x["jobs"]["ejemplo"]["with"].__setitem__("esperar", "igual"), "ejemplo con"),
                         ("sin sin_corpus_lab", lambda x: x["jobs"]["ejemplo-propio"]["with"].pop("sin_corpus_lab"), "ejemplo-propio entradas")):
        malo = copy.deepcopy(d)
        f(malo)
        mira("control: %s" % n, motivo in guarda_ejemplo(malo), True)


def guarda_rojo(d, ref_ejemplo):
    p = []
    o = on(d) or {}
    if set(o) != {"workflow_dispatch"}:
        p.append("on")
    if d.get("permissions") != {"contents": "read"}:
        p.append("permisos")
    j = d.get("jobs") or {}
    r = j.get("rojo") or {}
    w = r.get("with") or {}
    m = LK_REMOTO.match(r.get("uses", ""))
    if not m or m.group(1) != ref_ejemplo or w.get("laboratorio_ref") != ref_ejemplo or r.get("permissions") != {"contents": "read"}:
        p.append("rojo forma remota")
    if w.get("esperar", "pasa") != "pasa" or not all(x in w.get("preparar", "") for x in ("preparar.sh", "sembrar.py", "DEFECTO.json")) \
            or not w.get("linea_base", "").endswith("ejemplo-ci/ci/LINEA-BASE.json") or w.get("nombre") != "rojo":
        p.append("rojo con")
    c = j.get("rojo-comprobado") or {}
    bajadas = [(s.get("with") or {}).get("name") for s in c.get("steps") or [] if str(s.get("uses", "")).startswith("actions/download-artifact@")]
    if c.get("needs") != "rojo" or c.get("if") != "always()" or bajadas != ["rojo-${{ github.run_attempt }}"] \
            or not any("comprobar_rojo.py" in (s.get("run") or "") for s in c.get("steps") or []):
        p.append("rojo-comprobado")
    return p


def p22():
    """La plantilla de rojo-ci.yml: solo a mano, la forma remota, la siembra y la comprobación de fuera (§5.1)."""
    d = cargar(os.path.join(plantillas_dir(), "rojo-ci.yml"))
    ref = LK_REMOTO.match(cargar(os.path.join(plantillas_dir(), "ejemplo-ci.yml"))["jobs"]["ejemplo"]["uses"]).group(1)
    mira("rojo-ci.yml", guarda_rojo(d, ref), [])
    for n, f, motivo in (("con push", lambda x: on(x).__setitem__("push", {"branches": ["main"]}), "on"),
                         ("esperar: falla", lambda x: x["jobs"]["rojo"]["with"].__setitem__("esperar", "falla"), "rojo con"),
                         ("sin if: always()", lambda x: x["jobs"]["rojo-comprobado"].pop("if"), "rojo-comprobado")):
        malo = copy.deepcopy(d)
        f(malo)
        mira("control: %s" % n, motivo in guarda_rojo(malo, ref), True)


def guarda_proyecto(e, plantillas):
    p = []
    ad = leer_json(os.path.join(e, "ci", "adaptador.json"))
    dig = ad["caja"].get("imagen_digest") or ""
    if ad.get("id") != "ejemplo" or ad["caja"]["tipo"] != "docker" or ad["caja"]["imagen"] != "python:3.12-slim" or not re.match(r"^sha256:[0-9a-f]{64}$", dig):
        p.append("adaptador")
    for n in ("ejemplo-ci.yml", "rojo-ci.yml"):
        t = open(os.path.join(plantillas, n), encoding="utf-8").read()
        if ("python:3.12-slim@" + dig) not in t:
            p.append("digest en " + n)
    if dig[7:] not in open(os.path.join(e, "ci", "hacer_base.sh"), encoding="utf-8").read():
        p.append("digest en hacer_base.sh")
    hl7 = sorted(f for f in os.listdir(os.path.join(e, "corpus")) if f.endswith(".hl7"))
    if len(hl7) != 6:
        p.append("seis mensajes")
    for f in hl7:
        t = open(os.path.join(e, "corpus", f), encoding="utf-8").read()
        msh = t.replace("\r\n", "\n").replace("\r", "\n").split("\n")[0].split("|")
        if not t.startswith("MSH|^~\\&|") or len(msh) < 10 or msh[8].split("^")[0] not in ("ADT", "ORU", "VXU") or msh[9] != f[:-4] \
                or "@" in t or re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", t):
            p.append("mensaje " + f)
    for n, solo_propio in (("LINEA-BASE.json", False), ("LINEA-BASE-propio.json", True)):
        r = os.path.join(e, "ci", n)
        if not os.path.exists(r):
            continue
        b = leer_json(r)
        n_corpus = (b.get("corpus") or {}).get("n") or {}
        bien = b.get("formato") == "linea-base-ci/1" and b["conversor"]["id"] == "ejemplo" and b["n_casos"] == len(b["casos"])
        if solo_propio:
            bien = bien and all(k.startswith("propio/") for k in b["casos"]) and {k for k, v in n_corpus.items() if v} == {"propio"}
        else:
            bien = bien and n_corpus.get("propio") == 6 and (n_corpus.get("adt") or 0) > 0
        if not bien:
            p.append(n)
    df = leer_json(os.path.join(e, "ci", "DEFECTO.json"))
    if df.get("formato") != "defecto-ci/1" or df.get("fichero") != "conversor.py" or df.get("de") == df.get("a") \
            or not df.get("hallazgo_esperado") or not all(isinstance(x, list) and len(x) == 3 for x in df["hallazgo_esperado"]):
        p.append("DEFECTO.json")
    return p


def p23():
    """El proyecto de ejemplo: adaptador, digest en todas partes, seis mensajes, las bases y el defecto (§3)."""
    e = ejemplo_dir()
    art = tmp("art_ej")
    os.makedirs(os.path.join(art, "conv"))
    shutil.copyfile(os.path.join(e, "conversor.py"), os.path.join(art, "conv", "conversor.py"))
    mira("el adaptador se lee", VC.leer_adaptador(os.path.join(e, "ci", "adaptador.json"), art)["id"], "ejemplo")
    mira("el proyecto de ejemplo", guarda_proyecto(e, plantillas_dir()), [])
    for n, cambio, motivo in (("una base de otro conversor", ("ci/LINEA-BASE.json", lambda b: b["conversor"].__setitem__("id", "juguete")), "LINEA-BASE.json"),
                              ("otro digest en una plantilla", ("ejemplo-ci.yml", None), "digest en ejemplo-ci.yml")):
        e2, pl2 = tmp("ej2"), tmp("pl2")
        shutil.rmtree(e2)
        shutil.copytree(e, e2)
        for f in os.listdir(plantillas_dir()):
            shutil.copyfile(os.path.join(plantillas_dir(), f), os.path.join(pl2, f))
        if cambio[1]:
            r = os.path.join(e2, cambio[0])
            if not os.path.exists(r):
                escribir_json(r, {"formato": "linea-base-ci/1", "conversor": {"id": "ejemplo"}, "casos": {}, "n_casos": 0, "corpus": {"n": {"propio": 6, "adt": 1}}})
            b = leer_json(r)
            cambio[1](b)
            escribir_json(r, b)
        else:
            t = open(os.path.join(pl2, cambio[0]), encoding="utf-8").read()
            open(os.path.join(pl2, cambio[0]), "w", encoding="utf-8").write(t.replace(digest_del_adaptador()[7:], "0" * 64))
        mira("control: %s" % n, motivo in guarda_proyecto(e2, pl2), True)


def convertir_ejemplo(conversor, corpus):
    s = tmp("conv_ej")
    r = subprocess.run([sys.executable, conversor, corpus, s], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr[-400:]
    return s, {f: open(os.path.join(s, f), "rb").read() for f in sorted(os.listdir(s))}


def cargar_modulo(nombre):
    spec = importlib.util.spec_from_file_location(nombre.replace("-", "_"), os.path.join(ejemplo_dir(), "ci", nombre + ".py") if nombre == "sembrar"
                                                  else os.path.join(CI_D, nombre + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def p24():
    """El conversor del ejemplo sin Docker: determinista, y el defecto solo cambia el género de F (§3.1, §3.5)."""
    e = ejemplo_dir()
    conv, corpus = os.path.join(e, "conversor.py"), os.path.join(e, "corpus")
    s1, a = convertir_ejemplo(conv, corpus)
    _, b = convertir_ejemplo(conv, corpus)
    jsons = sorted(f for f in a if f.endswith(".json"))
    mira("un .json por mensaje", len(jsons), 6)
    mira("dos corridas, iguales byte a byte", a == b, True)
    bundles = {f: json.loads(a[f].decode("utf-8")) for f in jsons}
    mira("cada uno, un Bundle con su Patient", all(x["resourceType"] == "Bundle" and any(en["resource"]["resourceType"] == "Patient" for en in x["entry"])
                                                  for x in bundles.values()), True)
    mira("el número, con su texto literal", b'"value": 5.30' in a["EJ-ORU-R01.json"], True)
    sm = cargar_modulo("sembrar")
    copia = os.path.join(tmp("sembrado"), "conversor.py")
    shutil.copyfile(conv, copia)
    defecto = os.path.join(e, "ci", "DEFECTO.json")
    mira("sembrar sale con 0", sm.main([copia, defecto]), 0)
    _, c = convertir_ejemplo(copia, corpus)

    def genero(datos, f):
        return [en["resource"].get("gender") for en in json.loads(datos[f].decode("utf-8"))["entry"] if en["resource"]["resourceType"] == "Patient"][0]
    mira("A01 (F) sale male; A03 (M), igual", (genero(c, "EJ-ADT-A01.json"), genero(c, "EJ-ADT-A03.json")), ("male", "male"))
    distintos = sorted(f for f in jsons if a[f] != c[f])
    con_f = sorted(f for f in jsons if genero(a, f) == "female")
    mira("solo cambian los de F, y solo en gender", (distintos, all(a[f].replace(b'"gender": "female"', b'"gender": "male"') == c[f] for f in distintos)),
         (con_f, True))
    mira("--deshacer lo devuelve byte a byte", (sm.main([copia, defecto, "--deshacer"]), open(copia, "rb").read() == open(conv, "rb").read()), (0, True))
    otro = tmp("otro")
    open(os.path.join(otro, "siu.hl7"), "w").write("MSH|^~\\&|EJ|EJ|LAB|LAB|20260301120000||SIU^S12^SIU_S12|siu|P|2.5\rSCH|1\r")
    s2, d = convertir_ejemplo(conv, otro)
    mira("un SIU da .error", sorted(d), ["siu.error"])
    sin = os.path.join(tmp("sin"), "x.py")
    open(sin, "w").write("nada\n")
    mira("control: sembrar donde no está el texto", (sm.main([sin, defecto]), open(sin).read()), (2, "nada\n"))
    dos = os.path.join(tmp("dos"), "x.py")
    texto = leer_json(defecto)["de"]
    open(dos, "w").write(texto + "\n" + texto + "\n")
    mira("control: el texto dos veces", sm.main([dos, defecto]), 2)


def artefacto_rojo(**cambios):
    """Un artefacto sintético del run en rojo, como lo deja el flujo (sin el prefijo trabajo/)."""
    e = ejemplo_dir()
    triple = leer_json(os.path.join(e, "ci", "DEFECTO.json"))["hallazgo_esperado"]
    a = tmp("artefacto_rojo")
    os.makedirs(os.path.join(a, "corrida"))
    base = {"formato": "linea-base-ci/1", "conversor": {"id": "ejemplo", "huella": "h" * 64}, "casos": {"propio/EJ-ADT-A01": {}, "adt/A01-001": {}},
            "n_casos": 2, "creada_de": {"juez": {"huella": "j" * 64}}}
    b = escribir_json(os.path.join(tmp("base_rojo"), "LINEA-BASE.json"), base)
    v = {"formato": "veredicto-ci/1", "esperado": "pasa", "resultado": "falla", "pasa": False, "veredicto_esperado": False, "motivos": ["hallazgo_nuevo"],
         "nuevos": [{"caso": "propio/EJ-ADT-A01", "hecho": triple[0][0], "clase": triple[0][1], "subtipo": triple[0][2]}],
         "nuevos_distintos": triple, "arreglos": [], "casos_nuevos": [], "casos_ausentes": [], "salida_perdida": [], "indeterminado_nuevo": [], "notas": [],
         "avisos": {"huella_distinta": {"base": "h" * 64, "corrida": "k" * 64}}}
    v.update(cambios.get("v", {}))
    escribir_json(os.path.join(a, "corrida", "VEREDICTO-CI.json"), v)
    if not cambios.get("sin_md"):
        open(os.path.join(a, "corrida", "VEREDICTO-CI.md"), "w", encoding="utf-8").write(
            "## Verificador: ejemplo · pasa · **FALLA**\n\n### Hallazgos nuevos (hasta 50)\n\n- x\n")
    escribir_json(os.path.join(a, "corrida", "INFORME.json"), {"formato": "informe-vc/1"})
    open(os.path.join(a, "corrida", "juicio.jsonl"), "w").write("{}\n")
    escribir_json(os.path.join(a, "corrida", "LINEA-BASE-propuesta.json"), {"casos": {"propio/EJ-ADT-A01": {"hallazgos": triple}}})
    return a, b


def comprobar_rojo(a, b, *extra):
    cr = cargar_modulo("comprobar_rojo")
    out = tmp("comprobacion_rojo")
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = cr.main([a, os.path.join(ejemplo_dir(), "ci", "DEFECTO.json"), b] + list(extra) + ["-o", out])
    ruta = os.path.join(out, "COMPROBACION-ROJO.json")
    return rc, (leer_json(ruta) if os.path.exists(ruta) else None)


def p25():
    """comprobar_rojo.py: el job falló por el hallazgo sembrado y solo por él, con su resumen y su artefacto (§5.3)."""
    triple = leer_json(os.path.join(ejemplo_dir(), "ci", "DEFECTO.json"))["hallazgo_esperado"]
    a, b = artefacto_rojo()
    rc, c = comprobar_rojo(a, b, "--resultado-job", "failure")
    mira("el bueno: 0 y todo cierto", (rc, c and c["todo_bien"], c and all(c["comprobaciones"].values())), (0, True, True))
    rc, c = comprobar_rojo(a, b, "--resultado-job", "failure", "--salidas", "", "", "")
    mira("salidas vacías: no decide y se anota", (rc, c and c["salidas_del_job"]), (0, "vacias"))
    rc, _ = comprobar_rojo(a, b, "--resultado-job", "failure", "--salidas", "falla", "1", json.dumps(triple))
    mira("salidas que cuadran", rc, 0)
    for n, args, art in (("el job en verde", ["--resultado-job", "success"], {}),
                         ("motivo caja", ["--resultado-job", "failure"], {"v": {"motivos": ["hallazgo_nuevo", "caja"]}}),
                         ("un triple de más", ["--resultado-job", "failure"], {"v": {"nuevos_distintos": triple + [["PID-7", "fidelidad", "dato_perdido"]]}}),
                         ("sin VEREDICTO-CI.md", ["--resultado-job", "failure"], {"sin_md": True}),
                         ("esperaba falla", ["--resultado-job", "failure"], {"v": {"esperado": "falla"}}),
                         ("salidas que dicen pasa", ["--resultado-job", "failure", "--salidas", "pasa", "1", json.dumps(triple)], {})):
        a2, b2 = artefacto_rojo(**art)
        mira("control: %s" % n, comprobar_rojo(a2, b2, *args)[0], 1)


def artefacto_ejemplo(propio=False, **cambios):
    a = tmp("artefacto_ej")
    os.makedirs(os.path.join(a, "corrida", "cajas"))
    corpus = ["EJ-ADT-A01", "EJ-ADT-A03", "EJ-ADT-A08", "EJ-ORU-R01", "EJ-ORU-R01-dos", "EJ-VXU-V04"]
    casos = {"propio/" + c: {} for c in corpus} if propio else dict({"propio/" + c: {} for c in corpus}, **{"adt/A01-%03d" % i: {} for i in range(3)})
    n_corpus = {"propio": 6} if propio else {"propio": 6, "adt": 3}
    base = {"formato": "linea-base-ci/1", "conversor": {"id": "ejemplo", "huella": "h" * 64}, "casos": casos, "n_casos": len(casos),
            "corpus": {"n": n_corpus}, "creada_de": {"juez": {"huella": "j" * 64}}}
    b = escribir_json(os.path.join(tmp("base_ej"), "LINEA-BASE.json"), base)
    n = cambios.get("n", len(casos))
    v = {"formato": "veredicto-ci/1", "esperado": "pasa", "resultado": "pasa", "pasa": True, "veredicto_esperado": True, "motivos": [], "nuevos": [],
         "nuevos_distintos": [], "arreglos": [], "casos_nuevos": [], "casos_ausentes": [], "salida_perdida": [], "indeterminado_nuevo": [], "notas": [],
         "cambios_de_categoria": [], "avisos": cambios.get("avisos", {}), "n": {"base": len(casos), "corrida": n, "comparados": len(casos)},
         "identidades": {"huella": "h" * 64, "imagen_digest": digest_del_adaptador(), "juez": "j" * 64}}
    escribir_json(os.path.join(a, "corrida", "VEREDICTO-CI.json"), v)
    nombre = "ejemplo-propio" if propio else "ejemplo"
    open(os.path.join(a, "corrida", "VEREDICTO-CI.md"), "w", encoding="utf-8").write("## Verificador: ejemplo · pasa · **PASA**\n")
    escribir_json(os.path.join(a, "corrida", "INFORME.json"), {"corpus": {"n": dict({"adt": 0, "oru": 0, "vxu": 0, "minimos": 0, "muestras": 0}, **n_corpus)}})
    for f in ("juicio.jsonl", "CORRIDA.json", "ADAPTADOR.json", "LINEA-BASE-propuesta.json"):
        open(os.path.join(a, "corrida", f), "w").write("{}\n")
    open(os.path.join(a, "solo-orden.txt"), "w").write("[1/9] adaptador\n")
    open(os.path.join(a, "corrida", "cajas", "g.log"), "w").write("x\n")
    if not propio or cambios.get("con_md"):
        open(os.path.join(a, "corrida", "INFORME.md"), "w").write("# Informe\n")
    if propio or cambios.get("con_evidencias"):
        os.makedirs(os.path.join(a, "corrida", "evidencias", "x"))
        open(os.path.join(a, "corrida", "evidencias", "x", "e.json"), "w").write("{}\n")
        os.makedirs(os.path.join(a, "corrida", "corpus", "propio"))
        for c in corpus:
            open(os.path.join(a, "corrida", "corpus", "propio", c + ".hl7"), "w").write("MSH|\n")
    return a, b, nombre


def comprobar_ejemplo(ej, pr):
    ce = cargar_modulo("comprobar_ejemplo")
    out = tmp("comprobacion_ej")
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = ce.main([ej[0], pr[0], ej[1], pr[1], os.path.join(ejemplo_dir(), "ci", "adaptador.json"),
                      "--salidas", "pasa", "h" * 64, digest_del_adaptador(), "pasa", "-o", out])
    return rc


def p26():
    """comprobar_ejemplo.py: las dos llamadas dicen lo que tienen que decir, y nada más; los YAML que corren son los sellados (§4.3)."""
    ej, pr = artefacto_ejemplo(), artefacto_ejemplo(propio=True)
    mira("los dos buenos: 0", comprobar_ejemplo(ej, pr), 0)
    for n, a in (("INFORME.md en el propio", (ej, artefacto_ejemplo(propio=True, con_md=True))),
                 ("evidencias/ en el de ejemplo", (artefacto_ejemplo(con_evidencias=True), pr)),
                 ("n.corrida distinto", (artefacto_ejemplo(n=1), pr)),
                 ("un aviso huella_distinta", (artefacto_ejemplo(avisos={"huella_distinta": {"base": "a", "corrida": "b"}}), pr))):
        mira("control: %s" % n, comprobar_ejemplo(*a), 1)
    vivos = os.path.join(os.path.dirname(FASE), ".github", "workflows")
    for f in ("verificador-conversor.yml", "demo-ci.yml", "higiene.yml"):
        if os.path.exists(os.path.join(vivos, f)):
            mira("%s, el sellado" % f, open(os.path.join(vivos, f), "rb").read() == open(os.path.join(plantillas_dir(), f), "rb").read(), True)


C0 = "0f8543718e0ce004fb477bbd7da06cb7c44486ee"                              # el commit publicado del que partió la etapa 24
C1 = "5183b4edeb2fff421cd441b248f141ccd52852bc"                              # el pin del ejemplo en la 24
M1 = "e704b97b560a252cfac2cdeae68ed1530cc78be7"                              # etapa 25: el commit del primer push, puesto en M2
P27 = "c9d49d9566d14121cef9fc7a21dbaf1ee906d494"                             # etapa 27: el pin subido al commit con MDM
PIN_ESPERADO = P27 or M1 or C1


def comprobar_vivos(vivos):
    """-> (problemas, commits): los dos YAML del ejemplo en `vivos`, frente a sus plantillas con COMMIT_C1 cambiado."""
    p, commits = [], set()
    for f in ("ejemplo-ci.yml", "rojo-ci.yml"):
        vivo, plantilla = os.path.join(vivos, f), open(os.path.join(plantillas_dir(), f), encoding="utf-8").read()
        if not os.path.exists(vivo):
            p.append("%s no existe" % f)
            continue
        t = open(vivo, encoding="utf-8").read()
        m = re.search(r"verificador-conversor\.yml@([0-9a-f]{40})", t)
        if not m:
            p.append("%s sin forma remota de 40 hex" % f)
            continue
        commits.add(m.group(1))
        if t != plantilla.replace("COMMIT_M1", m.group(1)):
            p.append("%s no es su plantilla" % f)
    if len(commits) != 1:
        p.append("commits distintos")
    if C0 in commits:
        p.append("C0")
    if commits and commits != {PIN_ESPERADO}:
        p.append("no es el pin esperado")
    return p, commits


def p27():
    """Los dos YAML del ejemplo que corren son sus plantillas con COMMIT_C1 cambiado por un mismo commit, que no es C0 (§4.1)."""
    vivos = os.path.join(os.path.dirname(FASE), ".github", "workflows")
    if not os.path.exists(os.path.join(vivos, "verificador-conversor.yml")):
        mira("en el laboratorio no hay .github/workflows/: P-CI-27 se comprueba en el repositorio público", True, True)
        return
    mira("los dos YAML del ejemplo, sus plantillas con un mismo commit", comprobar_vivos(vivos)[0], [])

    def copia(cambio):
        d = tmp("vivos")
        for f in ("ejemplo-ci.yml", "rojo-ci.yml"):
            if os.path.exists(os.path.join(vivos, f)):
                shutil.copyfile(os.path.join(vivos, f), os.path.join(d, f))
        cambio(d)
        return d

    def cambiar(f, viejo, nuevo):
        def h(d):
            r = os.path.join(d, f)
            texto = open(r, encoding="utf-8").read()
            open(r, "w", encoding="utf-8").write(texto.replace(viejo, nuevo, 1))
        return h
    mira("control: un espacio cambiado", "ejemplo-ci.yml no es su plantilla" in comprobar_vivos(copia(cambiar("ejemplo-ci.yml", "  ejemplo:", " ejemplo:")))[0], True)
    plantilla = open(os.path.join(plantillas_dir(), "rojo-ci.yml"), encoding="utf-8").read()

    def otro_commit(d):
        open(os.path.join(d, "rojo-ci.yml"), "w", encoding="utf-8").write(plantilla.replace("COMMIT_M1", "b" * 40))
    mira("control: dos commits distintos", "commits distintos" in comprobar_vivos(copia(otro_commit))[0], True)

    def con_c0(d):
        for f in ("ejemplo-ci.yml", "rojo-ci.yml"):
            open(os.path.join(d, f), "w", encoding="utf-8").write(open(os.path.join(plantillas_dir(), f), encoding="utf-8").read().replace("COMMIT_M1", C0))
    mira("control: los dos con C0", "C0" in comprobar_vivos(copia(con_c0))[0], True)
    mira("control: sin rojo-ci.yml", "rojo-ci.yml no existe" in comprobar_vivos(copia(lambda d: os.remove(os.path.join(d, "rojo-ci.yml"))))[0], True)


# ---------------------------------------------------------------------------- P-CI-28..31 (etapa 25, cv/ci/diseno-mant-fable.md §5)
MINIMO_NODE24 = {"actions/checkout": 5, "actions/setup-python": 6, "actions/upload-artifact": 6, "actions/download-artifact": 7}
ENTRADAS_ACCION = {"actions/checkout": {"path", "persist-credentials", "repository", "ref", "fetch-depth"},
                   "actions/setup-python": {"python-version"},
                   "actions/upload-artifact": {"name", "path", "retention-days", "if-no-files-found"},
                   "actions/download-artifact": {"name", "path"}}


def guarda_node24(acciones):
    p = []
    for a, x in (acciones.get("acciones") or {}).items():
        sha, ant = x.get("sha", ""), (x.get("anterior") or {})
        if x.get("node") != "node24":
            p.append("%s node" % a)
        if not str(x.get("mayor", "")).startswith("v") or int(str(x["mayor"])[1:]) < MINIMO_NODE24.get(a, 99):
            p.append("%s mayor" % a)
        if not str(x.get("etiqueta", "")).startswith(str(x.get("mayor")) + "."):
            p.append("%s etiqueta" % a)
        if sha == ant.get("sha") or not re.match(r"^[0-9a-f]{40}$", ant.get("sha", "")):
            p.append("%s anterior" % a)
        if sha not in str(x.get("api", "")):
            p.append("%s api" % a)
    return p


def huellas_ci2():
    """Las plantillas de la 24 (github-ci2/*.yml) frente a sus líneas de SELLO-CI2.txt."""
    sello = {}
    for l in open(os.path.join(CI_D, "SELLO-CI2.txt"), encoding="utf-8"):
        m = re.match(r"^([0-9a-f]{64})  (github-ci2/\S+\.yml)\s*$", l)
        if m:
            sello[m.group(2)] = m.group(1)
    return sello, {r: hashlib.sha256(open(os.path.join(CI_D, r), "rb").read()).hexdigest() for r in sello}


def p28():
    """ACCIONES-CI.json: las cuatro en Node.js 24, en la mayor mínima o más, distintas de las de la 24; github-ci2/ intacto."""
    acciones = leer_json(ACCIONES_JSON)
    mira("las acciones, en Node.js 24", guarda_node24(acciones), [])
    for n, f, motivo in (("node20", lambda x: x["acciones"]["actions/checkout"].__setitem__("node", "node20"), "actions/checkout node"),
                         ("download v6", lambda x: x["acciones"]["actions/download-artifact"].__setitem__("mayor", "v6"), "actions/download-artifact mayor"),
                         ("el mismo sha que la 24", lambda x: x["acciones"]["actions/setup-python"].__setitem__("sha", x["acciones"]["actions/setup-python"]["anterior"]["sha"]),
                          "actions/setup-python anterior")):
        malo = copy.deepcopy(acciones)
        f(malo)
        mira("control: %s" % n, motivo in guarda_node24(malo), True)
    sello, ahora = huellas_ci2()
    mira("las cinco plantillas de la 24, intactas", (len(sello), sello == ahora), (5, True))
    d = tmp("ci2")
    shutil.copyfile(os.path.join(CI_D, "github-ci2", "demo-ci.yml"), os.path.join(d, "demo-ci.yml"))
    open(os.path.join(d, "demo-ci.yml"), "a", encoding="utf-8").write(" ")
    mira("control: una plantilla de la 24 con un espacio más",
         hashlib.sha256(open(os.path.join(d, "demo-ci.yml"), "rb").read()).hexdigest() == sello["github-ci2/demo-ci.yml"], False)


def checkouts_sin_persistencia(d):
    return ["%s/%s" % (jn, s.get("name") or "?") for jn, j in (d.get("jobs") or {}).items() for s in j.get("steps") or []
            if str(s.get("uses", "")).startswith("actions/checkout@") and (s.get("with") or {}).get("persist-credentials") is not False]


def p29():
    """Todo checkout de todo YAML, sin persistir credenciales (Q-MANT-D-2: también la higiene)."""
    mira("ningún checkout persiste credenciales",
         {os.path.basename(f): checkouts_sin_persistencia(cargar(f)) for f in ficheros_yaml() if checkouts_sin_persistencia(cargar(f))}, {})
    mira("control: un checkout sin la clave", checkouts_sin_persistencia({"jobs": {"j": {"steps": [{"uses": "actions/checkout@" + "a" * 40}]}}}), ["j/?"])


def cargar_anotaciones():
    spec = importlib.util.spec_from_file_location("anotaciones_ci", os.path.join(CI_D, "anotaciones_ci.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def p30():
    """anotaciones_ci.py sin red: ve el aviso de Node.js 20 y decide con lo admitido y el control (S-MANT-7)."""
    an = cargar_anotaciones()
    aviso = {"message": "Node.js 20 actions are deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/checkout@x", "title": ""}
    mira("ve el aviso", (len(an.avisos_de([aviso, {"message": "otra cosa"}])), an.avisos_de([{"message": "otra cosa"}])), (1, []))
    mira("control: Node.js 24 no es el aviso", an.avisos_de([{"message": "running on Node.js 24", "title": ""}]), [])
    def corrida(estado="completed", **jobs):
        return {"estado": estado, "jobs": {n: {"conclusion": "success", "aviso_node20": v} if isinstance(v, bool) else v for n, v in jobs.items()}}
    corridas = {"1": corrida(a=False, b=True)}
    control = {"jobs_con_aviso": ["x"]}
    mira("un job con aviso, no admitido: 1", an.veredicto(corridas, [], control), 1)
    mira("admitido por <run_id>:<job>: 0", an.veredicto(corridas, ["1:b"], control), 0)
    mira("control: admitido solo por el nombre: 1", an.veredicto(corridas, ["b"], control), 1)
    mira("control: lo admitido vale solo en su corrida", an.veredicto({"1": corrida(b=True), "2": corrida(b=True)}, ["1:b"], control), 1)
    mira("control: admitido y sin el aviso: 1", an.veredicto({"1": corrida(a=False, b=False)}, ["1:b"], control), 1)
    mira("control: control sin aviso: 1", an.veredicto({"1": corrida(a=False)}, [], {"jobs_con_aviso": []}), 1)
    mira("control: ninguna corrida: 1", an.veredicto({}, [], control), 1)
    mira("control: corrida sin acabar: 1", an.veredicto({"1": corrida("in_progress", a=False)}, [], control), 1)
    mira("control: job saltado: 1", an.veredicto({"1": corrida(a={"conclusion": "skipped", "aviso_node20": False})}, [], control), 1)
    mira("control: job cancelado: 1", an.veredicto({"1": corrida(a={"conclusion": "cancelled", "aviso_node20": False})}, [], control), 1)
    mira("un job en rojo es medida: 0", an.veredicto({"1": corrida(a={"conclusion": "failure", "aviso_node20": False})}, [], control), 0)
    mira("control: sin jobs: 1", an.veredicto({"1": corrida()}, [], control), 1)
    mira("sin aviso, medido: 0", an.veredicto({"1": corrida(a=False)}, [], control), 0)
    llamadas = []
    paginas = an.anotaciones_de(7, lambda *a: (llamadas.append(a), '{"message": "x"}\n{"message": "y"}\n')[1])
    mira("lee todas las páginas", (len(paginas), "--paginate" in llamadas[0]), (2, True))


def entradas_raras(d):
    p = []
    for jn, j in (d.get("jobs") or {}).items():
        for s in j.get("steps") or []:
            u = str(s.get("uses", ""))
            a = u.split("@")[0]
            if a in ENTRADAS_ACCION:
                extra = set(s.get("with") or {}) - ENTRADAS_ACCION[a]
                if extra or (a == "actions/download-artifact" and set(s.get("with") or {}) != {"name", "path"}):
                    p.append("%s/%s %s" % (jn, a, sorted(extra)))
    return p


def p31():
    """Las entradas de cada acción, las revisadas en sus notas de versión (§2.1)."""
    mira("ninguna entrada fuera de las revisadas",
         {os.path.basename(f): entradas_raras(cargar(f)) for f in ficheros_yaml() if entradas_raras(cargar(f))}, {})
    for n, paso in (("archive: false", {"uses": "actions/upload-artifact@x", "with": {"name": "a", "path": "b", "archive": False}}),
                    ("artifact-ids", {"uses": "actions/download-artifact@x", "with": {"artifact-ids": "1", "path": "b"}}),
                    ("cache: pip", {"uses": "actions/setup-python@x", "with": {"python-version": "3.12", "cache": "pip"}})):
        mira("control: %s" % n, bool(entradas_raras({"jobs": {"j": {"steps": [paso]}}})), True)


PRUEBAS = [p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24,
           p25, p26, p27, p28, p29, p30, p31]


def main():
    rojo = sys.argv[1:] == ["rojo"]
    if not rojo:
        for m, n in ((LB, "ERROR_LB"), (SJ, "ERROR_SJ")):
            if m is None:
                print("  no se importa: %s" % globals().get(n))
    for p in PRUEBAS:
        grupo[0] = "P-CI-%d" % int(p.__name__[1:])
        try:
            p()
        except Exception as ex:                                             # en rojo, lo esperado es que el código no exista
            FALLAN.add(grupo[0])
            if not rojo:
                print("  EXCEPCIÓN %s: %s" % (grupo[0], "".join(traceback.format_exception(type(ex), ex, ex.__traceback__)[-3:]).strip()[:600]))
                mal.append(grupo[0])
    shutil.rmtree(RAIZ, ignore_errors=True)
    if rojo:
        print("PRUEBAS CI (rojo): fallan %d de %d %s" % (len(FALLAN), len(PRUEBAS), "(TODAS)" if len(FALLAN) == len(PRUEBAS) else ""))
        return 0 if len(FALLAN) == len(PRUEBAS) else 1
    print("PRUEBAS CI: %s (%d comprobaciones, %d pruebas)" % ("TODO BIEN" if not mal else "%d MAL" % len(mal), n_ok[0], len(PRUEBAS)))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
