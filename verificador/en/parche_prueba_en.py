#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 34 (en/diseno-en-fable.md §4; en/decision-jev-en.md): añade a cv/ci/prueba_ci.py las pruebas P-EN-1..8 del ensayo local,
que levantan repositorios de git mínimos en tempfile (sin Docker ni red) y llaman a cv/ci/ensayo_flujo.py. Se aplica antes del
arreglo, para verlas en rojo. Afirma cada texto. Idempotente.
  cd fase12 && python3 en/parche_prueba_en.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(FASE, "cv", "ci", "prueba_ci.py")

DOC_VIEJO = ("(cv/ci/diseno-mant-fable.md §5): P-CI-28..31, las acciones en Node.js 24, y las de la 24 leen las plantillas de "
             "github-mant/. Corren sin Docker y sin red")
DOC_NUEVO = ("(cv/ci/diseno-mant-fable.md §5): P-CI-28..31, las acciones en Node.js 24, y las de la 24 leen las plantillas de "
             "github-mant/. Etapa 34\n(en/diseno-en-fable.md §4; en/decision-jev-en.md): P-EN-1..8, el ensayo local con lo que se "
             "publica, sobre repositorios de git\nmínimos. Corren sin Docker y sin red")

PRUEBAS_EN = r'''
# Etapa 34: el ensayo local con lo que se publica (en/diseno-en-fable.md §4). Repositorios de git mínimos, sin Docker ni red.
GIT_C = ["-c", "user.name=ensayo", "-c", "user.email=ensayo@localhost", "-c", "commit.gpgsign=false",
         "-c", "core.hooksPath=" + os.devnull, "-c", "init.defaultBranch=main"]
CHECKOUT = "actions/checkout@" + "0" * 40
MINI = """name: mini
on: push
jobs:
  uno:
    runs-on: ubuntu-latest
    steps:
      - uses: %(co)s
      - uses: %(co)s
        with:
          ref: ${{ github.sha }}
          path: lab
      - name: mirar
        env:
          SHA: ${{ github.sha }}
        run: |
          cat MARCA lab/MARCA
          echo "sha=$SHA"
          ls
  dos:
    runs-on: ubuntu-latest
    steps:
      - uses: %(co)s
        with:
          ref: %(ref)s
          path: lab
      - uses: %(co)s
      - name: mirar
        run: cat lab/MARCA ./MARCA
"""


def g(repo, *args):
    return subprocess.run(["git", "-C", repo] + GIT_C + list(args), check=True, capture_output=True, text=True).stdout.strip()


def escribir(repo, rel, t):
    p = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8", newline="").write(t)


def repo_minimo(ref="ab" * 20):
    """MARCA = v1, .gitignore con *.log y el flujo mini, en un commit."""
    r = tmp("en_repo")
    subprocess.run(["git"] + GIT_C + ["init", "-q", r], check=True, capture_output=True)
    escribir(r, "MARCA", "v1\n")
    escribir(r, ".gitignore", "*.log\n")
    escribir(r, ".github/workflows/mini.yml", MINI % {"co": CHECKOUT, "ref": ref})
    g(r, "add", "-A")
    g(r, "commit", "-q", "-m", "uno")
    return r


def cargar_ensayo():
    spec = importlib.util.spec_from_file_location("ensayo_flujo_en", os.path.join(CI_D, "ensayo_flujo.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def ensayar(repo, jobs="uno"):
    """Corre el ensayo sobre repo; devuelve (código, salida, ENSAYO.json o None, carpeta de trabajo, registro del paso 3)."""
    w = os.path.join(tmp("en_w"), "w")
    buf = io.StringIO()
    with redirect_stdout(buf):
        try:
            rc = cargar_ensayo().main([repo, w, jobs, "--flujo", "mini"])
        except SystemExit as ex:
            rc = "SystemExit: %s" % ex
    e = os.path.join(w, "ENSAYO.json")
    ens = leer_json(e) if os.path.exists(e) else None
    def reg(job):
        f = os.path.join(w, job, ".runner", "registro-3.txt")
        return open(f, encoding="utf-8").read().split("\n") if os.path.exists(f) else []
    return rc, buf.getvalue(), ens, w, reg


def clon_de(ens):
    return (ens or {}).get("clon") or {}


def en1():
    """El índice distinto del HEAD: se ensaya el árbol del índice, y github.sha es ese árbol."""
    r = repo_minimo()
    head = g(r, "rev-parse", "HEAD")
    escribir(r, "MARCA", "v2\n")
    g(r, "add", "MARCA")
    arbol = g(r, "write-tree")
    rc, out, ens, w, reg = ensayar(r)
    l = reg("uno")
    mira("devuelve 0", rc, 0)
    mira("el checkout sin ref y el de github.sha sacan el índice (MARCA v2), no el HEAD", l[:2], ["v2", "v2"])
    mira("github.sha es el árbol del índice", "sha=" + arbol in l, True)
    mira("clon: árbol y lo publicado", (clon_de(ens).get("tipo"), clon_de(ens).get("publicado")), ("arbol", arbol))
    mira("la línea del checkout dice «árbol del índice»", "árbol del índice %s" % arbol[:12] in out, True)
    mira("ninguna línea dice «git archive» del HEAD", "git archive %s" % head[:12] in out, False)


def en2():
    """Un cambio sin git add: no se ensaya nada, código 2, con la lista (también con parte en el índice y parte fuera)."""
    r = repo_minimo()
    escribir(r, "MARCA", "v2\n")
    rc, out, ens, w, reg = ensayar(r)
    mira("devuelve 2", rc, 2)
    mira("no corre ningún job", os.path.exists(os.path.join(w, "uno")), False)
    mira("lo dice, con la ruta", ("NO SE ENSAYA" in out, "MARCA" in out), (True, True))
    mira("ENSAYO.json: no_ensayado y sin jobs", (bool((ens or {}).get("no_ensayado")), (ens or {}).get("jobs")), (True, {}))
    r2 = repo_minimo()
    escribir(r2, "MARCA", "v2\n")
    g(r2, "add", "MARCA")
    escribir(r2, "MARCA", "v3\n")
    mira("control MM: también para", ensayar(r2)[0], 2)


def en3():
    """Un fichero sin seguimiento: no se ensaya nada, código 2, con la lista."""
    r = repo_minimo()
    escribir(r, "nuevo.txt", "x\n")
    rc, out, ens, w, reg = ensayar(r)
    mira("devuelve 2", rc, 2)
    mira("lo lista", "nuevo.txt" in out, True)
    mira("no corre ningún job", os.path.exists(os.path.join(w, "uno")), False)


def en4():
    """Un fichero ignorado: no para, no avisa y no entra en el checkout."""
    r = repo_minimo()
    escribir(r, "x.log", "x\n")
    rc, out, ens, w, reg = ensayar(r)
    mira("devuelve 0", rc, 0)
    mira("x.log no entra en el checkout", "x.log" in reg("uno"), False)
    mira("ni para ni lo nombra", ("NO SE ENSAYA" in out, "x.log" in out), (False, False))


def en5():
    """El clon limpio: lo de hoy (control), y el checkout sin ref sale del commit."""
    r = repo_minimo()
    head = g(r, "rev-parse", "HEAD")
    rc, out, ens, w, reg = ensayar(r)
    l = reg("uno")
    mira("control: devuelve 0, MARCA v1 en los dos, github.sha el HEAD", (rc, l[:2], "sha=" + head in l), (0, ["v1", "v1"], True))
    mira("control: el checkout de github.sha dice «git archive» del HEAD", "(git archive %s)" % head[:12] in out, True)
    mira("los dos checkouts salen del HEAD (hoy, el sin ref copia el árbol)", out.count("(git archive %s)" % head[:12]), 2)
    mira("clon: commit, y lo publicado es el HEAD", (clon_de(ens).get("tipo"), clon_de(ens).get("publicado")), ("commit", head))


def en6():
    """Sin .git: la carpeta tal cual (control); un ref de 40 hex que no se puede resolver, con aviso."""
    r = repo_minimo()
    e = tmp("en_export")
    a = subprocess.run(["git", "-C", r, "archive", "HEAD"], capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", e], input=a, check=True)
    rc, out, ens, w, reg = ensayar(e)
    l = reg("uno")
    mira("control: devuelve 0, MARCA v1, github.sha el marcador, copia del árbol",
         (rc, l[:2], "sha=" + "e0" * 20 in l, "(copia del árbol)" in out), (0, ["v1", "v1"], True, True))
    mira("clon: sin git", clon_de(ens).get("git"), False)
    rc, out, ens, w, reg = ensayar(e, "dos")
    mira("un ref de 40 hex sin .git: copia, con aviso", (rc, "no se puede resolver sin .git" in out), (0, True))


def en7():
    """Un commit fijado con el índice distinto: sale el commit fijado (control); un ref que no está, el índice con aviso."""
    r = repo_minimo()
    c1 = g(r, "rev-parse", "HEAD")
    escribir(r, ".github/workflows/mini.yml", MINI % {"co": CHECKOUT, "ref": c1})
    g(r, "add", "-A")
    g(r, "commit", "-q", "-m", "dos")
    escribir(r, "MARCA", "v2\n")
    g(r, "add", "MARCA")
    rc, out, ens, w, reg = ensayar(r, "dos")
    mira("control: lab del commit fijado (v1) y ./ del índice (v2)", (rc, reg("dos")[:2]), (0, ["v1", "v2"]))
    r2 = repo_minimo()
    escribir(r2, "MARCA", "v2\n")
    g(r2, "add", "MARCA")
    rc, out, ens, w, reg = ensayar(r2, "dos")
    mira("un ref que no está: el índice (v2 en los dos)", (rc, reg("dos")[:2]), (0, ["v2", "v2"]))
    mira("con aviso de que no está", "no está en esta copia" in out, True)


def en8():
    """ENSAYO.json conserva sus seis claves, en orden, y añade clon; con el código 2, sin jobs y con no_ensayado."""
    r = repo_minimo()
    ens = ensayar(r)[2] or {}
    mira("control: las seis claves de hoy, en orden", list(ens)[:6],
         ["flujo", "jobs", "esperado_rojo", "como_se_esperaba", "informes_iguales", "needs"])
    mira("y clon", "clon" in ens, True)
    escribir(r, "nuevo.txt", "x\n")
    ens = ensayar(r)[2] or {}
    mira("con el código 2: las mismas claves, sin jobs y con no_ensayado",
         (list(ens)[:6], ens.get("jobs"), bool(ens.get("no_ensayado"))),
         (["flujo", "jobs", "esperado_rojo", "como_se_esperaba", "informes_iguales", "needs"], {}, True))


'''
ANCLA = "\nPRUEBAS = [p01, "
PRUEBAS_VIEJA = "           p25, p26, p27, p28, p29, p30, p31]\n"
PRUEBAS_NUEVA = "           p25, p26, p27, p28, p29, p30, p31, en1, en2, en3, en4, en5, en6, en7, en8]\n"
GRUPO_VIEJO = '        grupo[0] = "P-CI-%d" % int(p.__name__[1:])\n'
GRUPO_NUEVO = ('        grupo[0] = ("P-EN-%d" % int(p.__name__[2:])) if p.__name__.startswith("en") else ("P-CI-%d" % int(p.__name__[1:]))\n')

t = open(P, encoding="utf-8").read()
if "def en1():" not in t:
    for viejo, nuevo in ((DOC_VIEJO, DOC_NUEVO), (PRUEBAS_VIEJA, PRUEBAS_NUEVA), (GRUPO_VIEJO, GRUPO_NUEVO)):
        assert t.count(viejo) == 1, viejo[:60]
        t = t.replace(viejo, nuevo)
    assert t.count(ANCLA) == 1
    t = t.replace(ANCLA, PRUEBAS_EN + ANCLA, 1)
    open(P, "w", encoding="utf-8").write(t)
print("cv/ci/prueba_ci.py: P-EN-1..8")
