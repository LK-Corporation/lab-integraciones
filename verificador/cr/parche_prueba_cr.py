#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 35 (cr/diseno-cr-fable.md §5; cr/decision-jev-cr.md y cr2): añade a cv/ci/prueba_ci.py P-CR-1..12, la comprobación de
después del push (cv/ci/comprobar_publicado.py), sobre los repositorios mínimos de las P-EN y un remoto vacío al lado, sin Docker
ni red. Se aplica antes de escribir la comprobación, para verlas en rojo. Afirma cada texto. Idempotente.
  cd fase12 && python3 cr/parche_prueba_cr.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(FASE, "cv", "ci", "prueba_ci.py")

DOC_VIEJO = "P-EN-1..10, el ensayo local con lo que se publica, sobre repositorios de git\nmínimos."
DOC_NUEVO = ("P-EN-1..10, el ensayo local con lo que se publica, sobre repositorios de git\nmínimos. Etapa 35 (cr/diseno-cr-fable.md §5; "
             "cr/decision-jev-cr.md): P-CR-1..12, la comprobación de después del push, con un\nremoto vacío al lado.")
PRUEBAS_VIEJA = "           en9, en10]\n"
PRUEBAS_NUEVA = "           en9, en10, cr1, cr2, cr3, cr4, cr5, cr6, cr7, cr8, cr9, cr10, cr11, cr12]\n"
GRUPO_VIEJO = '        grupo[0] = ("P-EN-%d" % int(p.__name__[2:])) if p.__name__.startswith("en") else ("P-CI-%d" % int(p.__name__[1:]))\n'
GRUPO_NUEVO = ('        pre = p.__name__[:2]\n'
               '        grupo[0] = ("P-%s-%d" % (pre.upper(), int(p.__name__[2:]))) if pre in ("en", "cr") else ("P-CI-%d" % int(p.__name__[1:]))\n')
ANCLA = "\n\nPRUEBAS = [p01, "
NUEVAS = r'''

# Etapa 35: la comprobación de después del push (cr/diseno-cr-fable.md §5), con un remoto vacío al lado.
def remoto_para(r):
    b = os.path.join(tmp("cr_remoto"), "remoto.git")
    subprocess.run(["git"] + GIT_C + ["init", "--bare", "-q", b], check=True, capture_output=True)
    g(r, "remote", "add", "origin", b)
    return b


def empujar(r, destino="main"):
    g(r, "push", "-q", "origin", "HEAD:refs/heads/" + destino)


def cargar_comprobacion():
    spec = importlib.util.spec_from_file_location("comprobar_publicado_cr", os.path.join(CI_D, "comprobar_publicado.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def ens_de(repo, jobs="uno"):
    """El ENSAYO.json de un ensayo del flujo mini sobre repo."""
    return os.path.join(ensayar(repo, jobs)[3], "ENSAYO.json")


def comprobar(repo, ensayos, *extra, flujos="mini", minimos=("mini=uno",)):
    o = tmp("cr_o")
    args = [repo] + list(ensayos) + ["--flujos", flujos, "-o", o] + list(extra)
    for m in minimos:
        args += ["--jobs-minimos", m]
    buf = io.StringIO()
    with redirect_stdout(buf):
        try:
            rc = cargar_comprobacion().main(args)
        except SystemExit as ex:
            rc = "SystemExit: %s" % ex
    p = os.path.join(o, "PUBLICADO.json")
    return rc, buf.getvalue(), (leer_json(p) if os.path.exists(p) else None)


def ultima(out):
    return (out.strip().splitlines() or [""])[-1]


def flujo_de(pub, f="mini"):
    return ((pub or {}).get("flujos") or {}).get(f) or {}


def cr1():
    """Negativo, con el ensayo del HEAD: pasa, el mismo commit."""
    r = repo_minimo()
    remoto_para(r)
    e = ens_de(r)
    empujar(r)
    rc, out, pub = comprobar(r, [e])
    mira("devuelve 0", rc, 0)
    mira("el mismo commit", "es el mismo commit" in out, True)
    mira("cerrado e igual", ((pub or {}).get("cerrado"), flujo_de(pub).get("igual")), (True, True))
    mira("la última línea", ultima(out).startswith("círculo cerrado"), True)


def cr2():
    """Negativo, con el ensayo del índice: pasa, el commit es nuevo sobre el árbol ensayado."""
    r = repo_minimo()
    remoto_para(r)
    escribir(r, "MARCA", "v2\n")
    g(r, "add", "MARCA")
    e = ens_de(r)
    g(r, "commit", "-q", "-m", "dos")
    empujar(r)
    rc, out, pub = comprobar(r, [e])
    mira("devuelve 0", rc, 0)
    mira("el commit es nuevo sobre el árbol", "el commit es nuevo sobre él" in out, True)
    mira("igual, y otro commit", (flujo_de(pub).get("igual"), flujo_de(pub).get("mismo_commit")), (True, False))


def cr3():
    """Un git add de más después del ensayo: cae, con la ruta."""
    r = repo_minimo()
    remoto_para(r)
    escribir(r, "MARCA", "v2\n")
    g(r, "add", "MARCA")
    e = ens_de(r)
    escribir(r, "OTRO", "de más\n")
    g(r, "add", "OTRO")
    g(r, "commit", "-q", "-m", "dos")
    empujar(r)
    rc, out, pub = comprobar(r, [e])
    mira("devuelve 1", rc, 1)
    mira("lo dice, con la ruta", ("OTRO ÁRBOL" in out, "1 ruta" in out, flujo_de(pub).get("diferencia")), (True, True, ["A\tOTRO"]))
    mira("la última línea", ultima(out).startswith("CÍRCULO ABIERTO"), True)


def cr4():
    """Un commit --amend con cambio después del ensayo del HEAD: cae, con la ruta, y dice que el commit ensayado ya no está."""
    r = repo_minimo()
    remoto_para(r)
    e = ens_de(r)
    escribir(r, "MARCA", "v3\n")
    g(r, "add", "MARCA")
    g(r, "commit", "-q", "--amend", "--no-edit")
    empujar(r)
    rc, out, pub = comprobar(r, [e])
    mira("devuelve 1", rc, 1)
    mira("la ruta", flujo_de(pub).get("diferencia"), ["M\tMARCA"])
    mira("el commit ensayado ya no está", "ya no está en main" in out, True)


def cr5():
    """Un amend que solo cambia el mensaje: pasa, el mismo árbol."""
    r = repo_minimo()
    remoto_para(r)
    e = ens_de(r)
    g(r, "commit", "-q", "--amend", "-m", "otro mensaje")
    empujar(r)
    rc, out, pub = comprobar(r, [e])
    mira("devuelve 0", rc, 0)
    mira("el commit es nuevo sobre el mismo árbol", "el commit es nuevo sobre él" in out, True)


def cr6():
    """Sin ensayo, y ensayos que no valen: cae; un fichero que no es JSON: 2."""
    r = repo_minimo()
    remoto_para(r)
    empujar(r)
    rc, out, pub = comprobar(r, [])
    mira("ningún ensayo", (rc, "no hay ensayo" in out), (1, True))
    rc, out, pub = comprobar(r, [os.path.join(tmp("cr_nada"), "ENSAYO.json")])
    mira("una ruta que no existe", (rc, "no hay ensayo" in out), (1, True))
    e = ens_de(r)
    d = leer_json(e)
    d.pop("clon")
    sin_clon = escribir_json(os.path.join(tmp("cr_sin_clon"), "ENSAYO.json"), d)
    mira("sin clon", comprobar(r, [sin_clon])[:2][0], 1)
    mira("sin clon: lo dice", "no dice qué árbol ensayó" in comprobar(r, [sin_clon])[1], True)
    x = tmp("cr_export")
    a = subprocess.run(["git", "-C", r, "archive", "HEAD"], capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", x], input=a, check=True)
    rc, out, pub = comprobar(r, [ens_de(x)])
    mira("sin .git", (rc, "no dice qué árbol ensayó" in out), (1, True))
    escribir(r, "nuevo.txt", "x\n")
    rc, out, pub = comprobar(r, [ens_de(r)])
    mira("un ensayo que no ensayó", (rc, "no ensayó nada" in out), (1, True))
    malo = os.path.join(tmp("cr_malo"), "ENSAYO.json")
    open(malo, "w").write("{no es json")
    mira("no es JSON: 2", comprobar(r, [malo])[0], 2)


def cr7():
    """Otra copia: con otro contenido, cae sin poder listar; con el mismo contenido, pasa."""
    r = repo_minimo()
    b = remoto_para(r)
    empujar(r)
    d = leer_json(ens_de(r))
    d["clon"]["arbol"] = "ab" * 20
    otro = escribir_json(os.path.join(tmp("cr_otro"), "ENSAYO.json"), d)
    rc, out, pub = comprobar(r, [otro])
    mira("otro contenido: cae", (rc, "no está en este clon" in out, flujo_de(pub).get("diferencia", "x")), (1, True, None))
    r2 = os.path.join(tmp("cr_clon2"), "c")
    subprocess.run(["git"] + GIT_C + ["clone", "-q", b, r2], check=True, capture_output=True)
    mira("el mismo contenido, en otra copia: pasa", comprobar(r, [ens_de(r2)])[0], 0)


def cr8():
    """Dos flujos sobre árboles distintos: cae el del árbol viejo, con su ruta, y solo él."""
    r = repo_minimo()
    remoto_para(r)
    d = leer_json(ens_de(r))
    d["flujo"] = "otro"
    viejo = escribir_json(os.path.join(tmp("cr_viejo"), "ENSAYO.json"), d)
    escribir(r, "MARCA", "v2\n")
    g(r, "add", "MARCA")
    e = ens_de(r)
    g(r, "commit", "-q", "-m", "dos")
    empujar(r)
    rc, out, pub = comprobar(r, [e, viejo], flujos="mini,otro", minimos=("mini=uno", "otro=uno"))
    mira("devuelve 1", rc, 1)
    mira("mini igual; otro, con la ruta", (flujo_de(pub).get("igual"), flujo_de(pub, "otro").get("diferencia")), (True, ["M\tMARCA"]))
    mira("la última línea nombra solo otro", ("otro" in ultima(out), "mini" in ultima(out)), (True, False))


def cr9():
    """Varios commits: pasa con aviso si la cabeza es el árbol ensayado; cae si no."""
    r = repo_minimo()
    remoto_para(r)
    escribir(r, "MARCA", "v2\n")
    escribir(r, "OTRO", "x\n")
    g(r, "add", "MARCA", "OTRO")
    e = ens_de(r)
    g(r, "commit", "-q", "-m", "a", "--", "MARCA")
    g(r, "commit", "-q", "-m", "b")
    empujar(r)
    rc, out, pub = comprobar(r, [e])
    mira("pasa, con aviso de 2 commits", (rc, "2 commits nuevos" in out, flujo_de(pub).get("commits_nuevos")), (0, True, 2))
    r2 = repo_minimo()
    remoto_para(r2)
    e2 = ens_de(r2)
    for v in ("v2", "v3"):
        escribir(r2, "MARCA", v + "\n")
        g(r2, "commit", "-q", "-am", v)
    empujar(r2)
    rc, out, pub = comprobar(r2, [e2])
    mira("la cabeza no es lo ensayado: cae", (rc, flujo_de(pub).get("diferencia")), (1, ["M\tMARCA"]))


def cr10():
    """Un PR: se comprueba la rama; con --base, la fusión prevista, y un aviso si main avanzó."""
    r = repo_minimo()
    remoto_para(r)
    empujar(r)
    g(r, "checkout", "-q", "-b", "rama")
    escribir(r, "MARCA", "v2\n")
    g(r, "commit", "-q", "-am", "rama")
    e = ens_de(r)
    empujar(r, "rama")
    rc, out, pub = comprobar(r, [e], "--rama", "rama", "--base", "main")
    mira("la rama: pasa, y la fusión tiene el mismo árbol", (rc, ((pub or {}).get("fusion") or {}).get("igual")), (0, True))
    g(r, "checkout", "-q", "main")
    escribir(r, "OTRO", "main avanza\n")
    g(r, "add", "OTRO")
    g(r, "commit", "-q", "-m", "main")
    empujar(r)
    g(r, "checkout", "-q", "rama")
    rc, out, pub = comprobar(r, [e], "--rama", "rama", "--base", "main")
    mira("main avanzó: pasa, con aviso de la fusión", (rc, "aviso" in out and "fusión" in out, ((pub or {}).get("fusion") or {}).get("igual")),
         (0, True, False))


def cr11():
    """No se puede comprobar: el remoto no se lee, o la rama no está: 2."""
    r = repo_minimo()
    remoto_para(r)
    empujar(r)
    e = ens_de(r)
    rc, out, pub = comprobar(r, [e], "--remoto", os.path.join(tmp("cr_no"), "no-existe.git"))
    mira("el remoto no se lee", (rc, "no se pudo" in out), (2, True))
    mira("la rama no está", comprobar(r, [e], "--rama", "no-esta")[0], 2)


def cr12():
    """Un ensayo en rojo sobre el árbol publicado avisa (Q-CR-4); un job que falta de la lista mínima cae (Q-CR-7)."""
    r = repo_minimo()
    remoto_para(r)
    empujar(r)
    e = ens_de(r)
    for clave, valor in (("como_se_esperaba", {"uno": False}), ("informes_iguales", {"negativo": False})):
        d = leer_json(e)
        d[clave] = valor
        rojo = escribir_json(os.path.join(tmp("cr_rojo"), "ENSAYO.json"), d)
        rc, out, pub = comprobar(r, [rojo])
        mira("en rojo (%s): pasa con aviso" % clave, (rc, "aviso" in out and "salió en rojo" in out), (0, True))
    rc, out, pub = comprobar(r, [e], minimos=("mini=uno,dos",))
    mira("falta un job de la lista: cae", (rc, "no corrió dos" in out), (1, True))
'''

t = open(P, encoding="utf-8").read()
if "def cr1():" not in t:
    for viejo, nuevo in ((DOC_VIEJO, DOC_NUEVO), (PRUEBAS_VIEJA, PRUEBAS_NUEVA), (GRUPO_VIEJO, GRUPO_NUEVO)):
        assert t.count(viejo) == 1, viejo[:60]
        t = t.replace(viejo, nuevo)
    assert t.count(ANCLA) == 1
    t = t.replace(ANCLA, NUEVAS + ANCLA, 1)
    open(P, "w", encoding="utf-8").write(t)
print("cv/ci/prueba_ci.py: P-CR-1..12")
