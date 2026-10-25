#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 23 (cv/ci/diseno-ci-fable.md §9; decisiones de Jev en cv/ci/decision-jev-qci.md): P-CI-1..15, la línea base, la siembra
del positivo y los dos flujos de GitHub Actions. Corren sin Docker y sin red, con el conversor de juguete. Los YAML se validan
con PyYAML (la única dependencia, solo de pruebas).

Antes del código fallan todas: linea_base.py, sembrar_juguete.py, POSITIVO-CI.json y los YAML no existen.
  python3 cv/ci/prueba_ci.py          -> TODO BIEN si no hay ningún MAL
  python3 cv/ci/prueba_ci.py rojo     -> sale 0 solo si fallan todas"""
import copy
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
    return pub if os.path.exists(os.path.join(pub, "verificador-conversor.yml")) else os.path.join(CI_D, "github")


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
        return paso_de_github(cambio(cuerpo) if cambio else cuerpo, w, env), open(salida).read(), open(resumen).read()

    rc, _, res = correr("veredicto", 10)
    mira("veredicto: con 10, el resumen se escribe y el paso sale con 10", (rc, res), (10, "## Verificador: FALLA\n"))
    rc, sal, _ = correr("verificar", 4)
    mira("verificar: con 4 (caja), deja rc=4 y el paso sigue", (rc, "rc=4" in sal), (0, True))
    rc, sal, _ = correr("verificar", 2)
    mira("verificar: con 2, deja rc=2 y el paso falla con 2", (rc, "rc=2" in sal), (2, True))
    rc, _, res = correr("veredicto", 10, lambda c: c.replace("set +e", ":"))
    mira("control: sin «set +e», el -e de GitHub corta el paso antes del resumen", (rc, res), (10, ""))


PRUEBAS = [p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15]


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
