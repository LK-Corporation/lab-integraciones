#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 35 (cr/diseno-cr-fable.md; decisiones de Jev en cr/decision-jev-cr.md y cr2): después del push, comprueba que el árbol
publicado es el que se ensayó. Lee el commit que el remoto tiene (git ls-remote, solo lectura), saca su árbol y lo compara con el
árbol que cada ENSAYO.json dice haber ensayado (clon.arbol, desde la etapa 34). Compara árboles, no commits.
- Pasa (0) si cada flujo de --flujos tiene un ensayo de sus jobs mínimos sobre el árbol publicado.
- Cae (1) si falta un ensayo, si no ensayó nada o no dice su árbol, si le falta un job de la lista mínima, o si ensayó otro árbol;
  entonces lista las rutas que difieren y la orden para re-ensayar ese flujo.
- Sale con 2 si no pudo comprobar: el remoto o la rama no se leen, un ENSAYO.json no es JSON o no es válido, dos ensayos del
  mismo flujo, ningún flujo que comprobar, los argumentos están mal, o un fichero no se lee o no se escribe.
- Avisa, sin cambiar el código: un ensayo en rojo sobre el árbol publicado (Q-CR-4), commits intermedios que GitHub no corre,
  otra historia (un amend), y, con --base, un commit de fusión con otro árbol.
Escribe PUBLICADO.json en -o. No escribe en el remoto; trae el commit con fetch solo si falta en el clon.
  python3 cv/ci/comprobar_publicado.py <clon> <ENSAYO.json>… [--remoto origin] [--rama main]
          [--flujos demo-ci,ejemplo-ci,rojo-ci] [--jobs-minimos <flujo>=<job>,<job> …] [--base <rama>] [-o <carpeta>]"""
import json
import os
import re
import subprocess
import sys

SHA40 = re.compile(r"^[0-9a-f]{40}$")
JOBS_MINIMOS = {"demo-ci": ["pruebas", "negativo", "positivo", "positivo-comprobado"],      # Q-CR-7: los que ya se ensayan
                "ejemplo-ci": ["ejemplo", "ejemplo-propio", "ejemplo-comprobado"],
                "rojo-ci": ["rojo", "rojo-comprobado"]}
ORDEN = {"demo-ci": "pruebas,negativo,positivo --flujo demo-ci", "ejemplo-ci": "ejemplo,ejemplo-propio --flujo ejemplo-ci",
         "rojo-ci": "rojo --flujo rojo-ci --rojo rojo"}


class NoSePuede(Exception):
    pass


def git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args), capture_output=True)


def salida(r):
    return r.stdout.decode("utf-8", "replace").strip()


def error(r):
    return r.stderr.decode("utf-8", "replace").strip().splitlines()[-1:] or [""]


def leer_ensayo(ruta):
    """(ensayo, motivo de que no valga). None si el fichero no existe."""
    if not os.path.isfile(ruta):
        return None, "no existe %s" % ruta
    try:
        d = json.load(open(ruta, encoding="utf-8"))
    except ValueError as ex:
        raise NoSePuede("%s no es JSON: %s" % (ruta, ex))
    def raro(que):
        raise NoSePuede("%s no es un ENSAYO.json válido: %s" % (ruta, que))
    if not isinstance(d, dict) or not isinstance(d.get("flujo"), str) or not d["flujo"]:
        raro("no dice su flujo")
    for k in ("jobs", "como_se_esperaba", "informes_iguales", "clon"):
        if d.get(k) is not None and not isinstance(d[k], dict):
            raro("%s no es un objeto" % k)
    e = {"ruta": ruta, "flujo": d["flujo"], "jobs": sorted(d.get("jobs") or {})}
    if d.get("no_ensayado"):
        return e, "el ensayo no ensayó nada (%s)" % d["no_ensayado"]
    clon = d.get("clon") or {}
    for k in ("arbol", "head", "tipo"):
        if clon.get(k) is not None and not isinstance(clon[k], str):
            raro("clon.%s no es un texto" % k)
    if not clon.get("git") or not SHA40.match(clon.get("arbol") or ""):
        return e, "no dice qué árbol ensayó: ensayo anterior a la etapa 34 o sobre una carpeta sin .git"
    rojo = ([k for k, v in sorted((d.get("como_se_esperaba") or {}).items()) if not v]
            + ["el informe de %s" % k for k, v in sorted((d.get("informes_iguales") or {}).items()) if not v])
    e.update(arbol=clon["arbol"], head=clon.get("head") or "", tipo=clon.get("tipo") or "", rojo=rojo)
    return e, None


def publicado(repo, remoto, rama):
    """(commit, árbol) que el remoto tiene en la rama."""
    r = git(repo, "ls-remote", remoto, "refs/heads/" + rama)
    lineas = salida(r).splitlines()
    if r.returncode != 0 or len(lineas) != 1:
        raise NoSePuede("no se pudo leer %s %s: %s" % (remoto, rama, error(r)[0] if r.returncode else "la rama no está"))
    commit = lineas[0].split()[0]
    if git(repo, "cat-file", "-e", commit + "^{commit}").returncode != 0:
        git(repo, "fetch", "-q", remoto, rama)
        if git(repo, "cat-file", "-e", commit + "^{commit}").returncode != 0:
            raise NoSePuede("no se pudo traer el commit %s de %s" % (commit[:12], remoto))
    return commit, salida(git(repo, "rev-parse", commit + "^{tree}"))


def diferencia(repo, ensayado, publicado_):
    """Las rutas que difieren («estado<TAB>ruta»), o None si el árbol ensayado no está en este clon."""
    if git(repo, "cat-file", "-e", ensayado + "^{tree}").returncode != 0:
        return None
    return [l for l in salida(git(repo, "diff", "--name-status", "--no-renames", ensayado, publicado_)).splitlines() if l]


def comparar(repo, e, commit, arbol):
    c = {"ensayo": e["ruta"], "arbol_ensayado": e["arbol"], "head_ensayado": e["head"], "tipo": e["tipo"], "jobs": e["jobs"],
         "rojo": e["rojo"], "igual": e["arbol"] == arbol, "mismo_commit": e["tipo"] == "commit" and e["head"] == commit,
         "diferencia": None, "commits_nuevos": None, "otra_historia": None, "amend": False}
    desciende = bool(SHA40.match(e["head"])) and git(repo, "merge-base", "--is-ancestor", e["head"], commit).returncode == 0
    c["otra_historia"] = not desciende
    if desciende:
        c["commits_nuevos"] = int(salida(git(repo, "rev-list", "--count", "%s..%s" % (e["head"], commit))) or 0)
    if not c["igual"]:
        c["diferencia"] = diferencia(repo, e["arbol"], arbol)
        c["amend"] = e["tipo"] == "commit" and not desciende
    return c


def fusion(repo, remoto, base, commit):
    """El árbol que tendría la fusión de commit con la base del remoto, o None si hay conflicto."""
    if git(repo, "fetch", "-q", remoto, base).returncode != 0:
        raise NoSePuede("no se pudo leer %s %s" % (remoto, base))
    r = git(repo, "merge-tree", "--write-tree", "FETCH_HEAD", commit)
    arbol = salida(r).splitlines()[0] if salida(r) else ""
    return arbol if r.returncode == 0 and SHA40.match(arbol) else None


def plural(n, uno, varios):
    return uno if n == 1 else varios


def main(argv):
    try:
        return comprobar(argv)
    except (IndexError, ValueError) as ex:                              # los argumentos, mal puestos
        print("no se pudo comprobar: los argumentos están mal (%s)" % ex)
        return 2
    except OSError as ex:                                               # un fichero que no se lee o no se escribe
        print("no se pudo comprobar: %s" % ex)
        return 2


def comprobar(argv):
    opts = {"--remoto": "origin", "--rama": "main", "--flujos": "demo-ci,ejemplo-ci,rojo-ci", "--base": None, "-o": None}
    minimos, pos, i = dict(JOBS_MINIMOS), [], 0
    while i < len(argv):
        a = argv[i]
        if a == "--jobs-minimos":
            f, js = argv[i + 1].split("=", 1)
            minimos[f] = [j for j in js.split(",") if j]
            i += 2
        elif a in opts:
            opts[a] = argv[i + 1]
            i += 2
        else:
            pos.append(a)
            i += 1
    if not pos:
        print(__doc__)
        return 2
    repo, rutas = os.path.abspath(pos[0]), pos[1:]
    remoto, rama = opts["--remoto"], opts["--rama"]
    flujos = [f for f in opts["--flujos"].split(",") if f]
    res = {"remoto": remoto, "rama": rama, "commit": None, "arbol": None, "flujos": {}, "avisos": [], "fusion": None,
           "cerrado": False, "codigo": 2}

    def avisa(texto):
        res["avisos"].append(texto)
        print("   aviso: " + texto)
    try:
        if not flujos:
            raise NoSePuede("no hay flujos que comprobar (--flujos vacío)")
        commit, arbol = publicado(repo, remoto, rama)
        res.update(commit=commit, arbol=arbol)
        cabeza = salida(git(repo, "rev-parse", "HEAD"))
        print("== lo publicado: %s refs/heads/%s → commit %s, árbol %s (%s)"
              % (remoto, rama, commit[:12], arbol[:12],
                 "el clon está en el mismo commit" if cabeza == commit else "el clon está en otro commit, %s" % cabeza[:12]))
        ensayos = {}
        for ruta in rutas:
            e, motivo = leer_ensayo(ruta)
            if e is None:
                avisa(motivo)
                continue
            if e["flujo"] in ensayos:
                raise NoSePuede("dos ensayos de %s" % e["flujo"])
            ensayos[e["flujo"]] = (e, motivo)
        abiertos = []
        for f in flujos:
            if f not in ensayos:
                res["flujos"][f] = {"motivo": "no hay ensayo"}
                print("   %s: no hay ensayo de %s" % (f, f))
                abiertos.append("%s sin ensayo" % f)
                continue
            e, motivo = ensayos[f]
            if motivo:
                res["flujos"][f] = {"ensayo": e["ruta"], "jobs": e["jobs"], "motivo": motivo}
                print("   %s: %s" % (f, motivo))
                abiertos.append("%s: %s" % (f, motivo.split(" (")[0].split(":")[0]))
                continue
            c = comparar(repo, e, commit, arbol)
            faltan = [j for j in minimos.get(f, []) if j not in e["jobs"]] or ([] if e["jobs"] else ["ningún job"])
            c["faltan"] = faltan
            res["flujos"][f] = c
            desc = ("ensayo sobre el árbol del índice %s (HEAD %s)" % (e["arbol"][:12], e["head"][:12]) if e["tipo"] == "arbol"
                    else "ensayo sobre el commit %s (árbol %s)" % (e["head"][:12], e["arbol"][:12]))
            jobs = "%d %s" % (len(e["jobs"]), plural(len(e["jobs"]), "job", "jobs"))
            if c["igual"]:
                texto = "el mismo árbol; " + ("es el mismo commit" if c["mismo_commit"] else "el commit es nuevo sobre él")
            else:
                d = c["diferencia"]
                if d is None:
                    texto = ("OTRO ÁRBOL: el árbol ensayado %s no es el publicado %s y no está en este clon: se ensayó en otra "
                             "copia o ya se purgó; no se puede listar la diferencia" % (e["arbol"][:12], arbol[:12]))
                else:
                    texto = "OTRO ÁRBOL: %d %s (%s%s)" % (len(d), plural(len(d), "ruta difiere", "rutas difieren"),
                                                         ", ".join(x.replace("\t", " ") for x in d[:20]),
                                                         ", … y %d más" % (len(d) - 20) if len(d) > 20 else "")
                if c["amend"]:
                    texto += "; el commit ensayado %s ya no está en %s" % (e["head"][:12], rama)
                texto += ("; re-ensaya: python3 cv/ci/ensayo_flujo.py <clon> <carpeta vacía> %s"
                          % ORDEN.get(f, "%s --flujo %s" % (",".join(e["jobs"]), f)))
            print("   %s: %s, %s: %s" % (f, desc, jobs, texto))
            if faltan:
                print("   %s: el ensayo no corrió %s" % (f, ", ".join(faltan)))
                abiertos.append("%s no corrió %s" % (f, ", ".join(faltan)))
            if not c["igual"]:
                abiertos.append("%s se ensayó sobre otro árbol" % f)
            elif e["rojo"]:
                avisa("%s: el ensayo salió en rojo (%s)" % (f, ", ".join(e["rojo"])))
            if c["igual"] and c["commits_nuevos"] is not None and c["commits_nuevos"] > (1 if e["tipo"] == "arbol" else 0):
                avisa("%s: %d commits nuevos desde el HEAD del ensayo; solo la cabeza está ensayada, que es lo que GitHub corre"
                      % (f, c["commits_nuevos"]))
            if c["igual"] and c["otra_historia"]:
                avisa("%s: el commit publicado no desciende del HEAD del ensayo (%s): otra historia sobre el mismo árbol"
                      % (f, e["head"][:12]))
        if opts["--base"]:
            fa = fusion(repo, remoto, opts["--base"], commit)
            ensayados = {c.get("arbol_ensayado") for c in res["flujos"].values() if c.get("arbol_ensayado")}
            res["fusion"] = {"base": opts["--base"], "arbol": fa, "igual": fa is not None and fa in ensayados}
            if fa is None:
                avisa("la fusión con %s tiene conflictos: no se puede prever su árbol" % opts["--base"])
            elif res["fusion"]["igual"]:
                print("   la fusión con %s tendría el árbol %s: el mismo árbol que el ensayado" % (opts["--base"], fa[:12]))
            else:
                avisa("el commit de fusión con %s tendría el árbol %s, que no está ensayado: las corridas de pull_request corren "
                      "sobre él" % (opts["--base"], fa[:12]))
        if abiertos:
            res["codigo"] = 1
            print("CÍRCULO ABIERTO: " + "; ".join(abiertos))
        else:
            res.update(cerrado=True, codigo=0)
            print("círculo cerrado: %s %s sobre el árbol %s, el del commit %s en %s %s"
                  % (len(flujos), plural(len(flujos), "flujo se ensayó", "flujos se ensayaron"), arbol[:12], commit[:12], remoto,
                     rama))
    except NoSePuede as ex:
        res["codigo"] = 2
        print("no se pudo comprobar: %s" % ex)
    if opts["-o"]:
        os.makedirs(opts["-o"], exist_ok=True)
        json.dump(res, open(os.path.join(opts["-o"], "PUBLICADO.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return res["codigo"]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
