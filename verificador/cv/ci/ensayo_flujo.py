#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapas 23 y 24: ensayo local de los flujos antes de cada push. Corre en la máquina del laboratorio los pasos `run:` de los jobs
de un YAML de .github/workflows/ (demo-ci, ejemplo-ci o rojo-ci), y los del flujo reutilizable cuando un job lo llama, con las
expresiones `${{ … }}` evaluadas como las evalúa GitHub en lo que estos YAML usan (inputs, steps, needs, jobs, github, &&, ||, !,
==, !=, always(), success()).
- Los `actions/checkout` se emulan: con un `ref` de 40 hex que esté en el repositorio, con `git archive` de ese commit; si no,
  copiando el árbol.
- El `uses:` remoto (`owner/repo/<ruta>@<ref>`) se resuelve en la copia local: con `git show <ref>:<ruta>` si el commit está, o
  con el YAML del árbol si no (una plantilla con COMMIT_C1, por ejemplo); `owner/repo` no se resuelve.
- `upload-artifact` registra lo que subiría (sin el prefijo común, como la acción) y `download-artifact` lo copia; un nombre
  repetido o que no se subió es un fallo.
- El `if:` de un job se evalúa con `needs`; un job llamado que falla pasa sus salidas igual.
- `setup-python` y `pip install` no se emulan: se usa el python3 de la máquina.
No es el runner. Lo que el ensayo no ve: la evaluación de GitHub de verdad, la resolución remota del `uses:` y del `repository:`
de checkout (sin red), si GitHub propaga las salidas de un job llamado que falla, los permisos del token para
`download-artifact`, el commit de fusión de un PR, y el Docker, el usuario y la red del runner.
  python3 cv/ci/ensayo_flujo.py <repositorio> <trabajo vacío> <job>[,<job>…] [--flujo demo-ci|ejemplo-ci|rojo-ci]
          [--modo-real lote|mensaje] [--entrada k=v …] [--rojo <job>[,…]] [--evento push|pull_request]
          [--informes-como <CORRIDA-CI-1.json>]
  (tras los jobs pedidos corren los de comprobación que solo dependen de ellos: positivo-comprobado, ejemplo-comprobado,
  rojo-comprobado…; un job que llama al flujo, como real, solo corre si se pide)"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

import yaml

TOKEN = re.compile(r"\s*(?:(?P<cad>'(?:[^']|'')*')|(?P<op>&&|\|\||==|!=|!|\(|\))|(?P<num>\d+)|(?P<id>[A-Za-z_][A-Za-z0-9_.\-]*(?:\(\))?))")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
REMOTO = re.compile(r"^([\w.-]+/[\w.-]+)/(.+)@(\S+)$")


class Contexto(dict):
    def valor(self, nombre):
        if nombre in ("always()", "success()", "failure()"):
            ok = self.get("_ok", True)
            return {"always()": True, "success()": ok, "failure()": not ok}[nombre]
        if nombre in ("true", "false", "null"):
            return {"true": True, "false": False, "null": None}[nombre]
        v = self
        for parte in nombre.split("."):
            v = v.get(parte) if isinstance(v, dict) else None
        return v


def evaluar(expr, ctx):
    py, pos, nombres = [], 0, {}
    while pos < len(expr.rstrip()):
        m = TOKEN.match(expr, pos)
        if not m:
            raise SystemExit("ENSAYO: no sé evaluar %r (en %r)" % (expr[pos:], expr))
        pos = m.end()
        if m.group("cad"):
            py.append(repr(m.group("cad")[1:-1].replace("''", "'")))
        elif m.group("op"):
            py.append({"&&": " and ", "||": " or ", "!": " not "}.get(m.group("op"), m.group("op")))
        elif m.group("num"):
            py.append(m.group("num"))
        else:
            clave = "_v%d" % len(nombres)
            nombres[clave] = ctx.valor(m.group("id"))
            py.append(clave)
    return eval("".join(py), {"__builtins__": {}}, nombres)


def texto(v):
    return "" if v is None else ("true" if v is True else "false" if v is False else str(v))


def interpolar(s, ctx):
    return re.sub(r"\$\{\{(.*?)\}\}", lambda m: texto(evaluar(m.group(1), ctx)), s) if isinstance(s, str) else s


def condicion(c, ctx):
    if c is None:
        return ctx.get("_ok", True)
    c = c.strip()
    c = c[3:-2] if c.startswith("${{") and c.endswith("}}") else c
    if not re.search(r"\b(always|success|failure|cancelled)\(\)", c):     # como GitHub: sin función de estado, va «success() &&»
        return ctx.get("_ok", True) and bool(evaluar(c, ctx))
    return bool(evaluar(c, ctx))


def git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args), capture_output=True)


def hay_commit(repo, ref):
    return bool(SHA40.match(ref or "")) and os.path.exists(os.path.join(repo, ".git")) and git(repo, "cat-file", "-e", ref + "^{commit}").returncode == 0


def copiar_repo(repo, destino, ref=None):
    os.makedirs(destino, exist_ok=True)
    if hay_commit(repo, ref):
        a = subprocess.run(["git", "-C", repo, "archive", ref], capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", destino], input=a, check=True)
        return "git archive %s" % ref[:12]
    shutil.copytree(repo, destino, ignore=shutil.ignore_patterns(".git", "__pycache__"), dirs_exist_ok=True)
    return "copia del árbol"


def leer_salidas(ruta):
    salidas, lineas = {}, open(ruta, encoding="utf-8").read().splitlines()
    i = 0
    while i < len(lineas):
        l = lineas[i]
        if "<<" in l and "=" not in l.split("<<")[0]:
            k, delim = l.split("<<", 1)
            j = lineas.index(delim, i + 1)
            salidas[k] = "\n".join(lineas[i + 1:j])
            i = j
        elif "=" in l:
            k, v = l.split("=", 1)
            salidas[k] = v
        i += 1
    return salidas


def ficheros_de(ws, rutas):
    out = []
    for r in rutas:
        p = os.path.join(ws, r)
        if os.path.isdir(p):
            out += [os.path.join(d, f) for d, _, fs in os.walk(p) for f in fs]
        elif os.path.exists(p):
            out.append(p)
    return sorted(out)


def subir(ws, rutas):
    """Lo que guardaría upload-artifact: los ficheros relativos a su antecesor común (la acción quita ese prefijo)."""
    fs = ficheros_de(ws, rutas)
    if not fs:
        return None, []
    comun = os.path.commonpath(fs) if len(fs) > 1 else os.path.dirname(fs[0])
    if os.path.isfile(comun):
        comun = os.path.dirname(comun)
    return comun, [os.path.relpath(f, comun) for f in fs]


def correr_pasos(nombre, job, ctx, ws, artefactos):
    """Los pasos de un job con runs-on. Devuelve (ok, ctx con steps)."""
    os.makedirs(os.path.join(ws, ".runner"), exist_ok=True)
    resumen = os.path.join(ws, ".runner", "resumen.md")
    open(resumen, "a").close()
    ctx["steps"], ctx["_ok"] = {}, True
    entorno_job = {k: texto(interpolar(v, ctx)) for k, v in (job.get("env") or {}).items()}
    for n, paso in enumerate(job["steps"], 1):
        etiqueta = paso.get("name") or paso.get("uses") or (paso.get("run") or "").splitlines()[0][:60]
        if not condicion(paso.get("if"), ctx):
            print("  [%s] - %s (saltado)" % (nombre, etiqueta))
            continue
        usa = paso.get("uses", "")
        w = {k: interpolar(v, ctx) for k, v in (paso.get("with") or {}).items()}
        if usa.startswith("actions/checkout@"):
            destino = os.path.normpath(os.path.join(ws, w.get("path", "")))
            como = "ya estaba"
            if not os.path.exists(os.path.join(destino, "verificador")):
                como = copiar_repo(ctx["_repo"], destino, w.get("ref"))
            print("  [%s] ✓ %s (%s%s)" % (nombre, etiqueta, como, "; repository %s sin resolver" % w["repository"] if w.get("repository") else ""))
            continue
        if usa.startswith("actions/setup-python@"):
            print("  [%s] ✓ %s (no se emula: python3 de la máquina)" % (nombre, etiqueta))
            continue
        if usa.startswith("actions/upload-artifact@"):
            if w["name"] in artefactos or re.search(r'[":<>|*?\\/\r\n]', w["name"]):
                print("  [%s] ✗ %s: el nombre de artefacto %r se repite o no vale" % (nombre, etiqueta, w["name"]))
                ctx["_ok"] = False
                continue
            rutas = [r.strip() for r in w["path"].splitlines() if r.strip()]
            comun, fs = subir(ws, rutas)
            artefactos[w["name"]] = (comun, fs)
            print("  [%s] ✓ %s: %s, %d ficheros de %d rutas" % (nombre, etiqueta, w["name"], len(fs), len(rutas)))
            continue
        if usa.startswith("actions/download-artifact@"):
            if w.get("name") not in artefactos or not artefactos[w["name"]][1]:
                print("  [%s] ✗ %s: el artefacto %r no se subió" % (nombre, etiqueta, w.get("name")))
                ctx["_ok"] = False
                continue
            comun, fs = artefactos[w["name"]]
            destino = os.path.join(ws, w.get("path", "."))
            for f in fs:
                os.makedirs(os.path.dirname(os.path.join(destino, f)), exist_ok=True)
                shutil.copyfile(os.path.join(comun, f), os.path.join(destino, f))
            print("  [%s] ✓ %s: %s, %d ficheros" % (nombre, etiqueta, w["name"], len(fs)))
            continue
        if usa:
            raise SystemExit("ENSAYO: no sé emular %s" % usa)
        cuerpo = interpolar(paso["run"], ctx)
        if cuerpo.lstrip().startswith("python3 -m pip install"):
            print("  [%s] ✓ %s (no se emula)" % (nombre, etiqueta))
            continue
        guion = os.path.join(ws, ".runner", "paso-%d.sh" % n)
        open(guion, "w", encoding="utf-8").write(cuerpo)
        salida = os.path.join(ws, ".runner", "salida-%d" % n)
        open(salida, "w").close()
        entorno = dict(os.environ, **ctx["_env"], **entorno_job,
                       **{k: texto(interpolar(v, ctx)) for k, v in (paso.get("env") or {}).items()},
                       GITHUB_WORKSPACE=ws, GITHUB_OUTPUT=salida, GITHUB_STEP_SUMMARY=resumen, RUNNER_TEMP=os.path.join(ws, ".runner"))
        shell = ["bash", "--noprofile", "--norc", "-eo", "pipefail"] if paso.get("shell") == "bash" else ["bash", "-e"]
        cwd = os.path.join(ws, paso.get("working-directory", ""))
        r = subprocess.run(shell + [guion], cwd=cwd, env=entorno, capture_output=True, text=True)
        open(os.path.join(ws, ".runner", "registro-%d.txt" % n), "w", encoding="utf-8").write(r.stdout + r.stderr)
        cola = (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]
        print("  [%s] %s %s (código %d) %s" % (nombre, "✓" if r.returncode == 0 else "✗", etiqueta, r.returncode, cola[0][:100]))
        if paso.get("id"):
            ctx["steps"][paso["id"]] = {"outputs": leer_salidas(salida), "outcome": "success" if r.returncode == 0 else "failure"}
        if r.returncode != 0:
            ctx["_ok"] = False
    return ctx["_ok"], ctx


def flujo_llamado(uses, repo, trabajo):
    if uses.startswith("./"):
        return yaml.safe_load(open(os.path.join(repo, uses[2:]), encoding="utf-8"))
    m = REMOTO.match(uses)
    if not m:
        raise SystemExit("ENSAYO: no sé resolver %s" % uses)
    duenyo, ruta, ref = m.groups()
    if hay_commit(repo, ref):
        t = git(repo, "show", "%s:%s" % (ref, ruta)).stdout.decode("utf-8")
        destino = os.path.join(trabajo, ".runner", ref[:12], ruta)
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        open(destino, "w", encoding="utf-8").write(t)
        print("  forma remota: %s (sin resolver) -> %s en el commit %s" % (duenyo, ruta, ref[:12]))
        return yaml.safe_load(t)
    print("  forma remota: el commit %s no está en esta copia; se ensaya el YAML del árbol (%s sin resolver)" % (ref, duenyo))
    return yaml.safe_load(open(os.path.join(repo, ruta), encoding="utf-8"))


def correr_job(nombre, demo, repo, trabajo, base_ctx, needs, artefactos):
    job = demo["jobs"][nombre]
    ws = os.path.join(trabajo, nombre)
    os.makedirs(ws)
    base = dict(base_ctx, github=dict(base_ctx["github"], job=nombre, workspace=ws), needs=needs)
    ctx = Contexto(base)
    if "uses" not in job:
        ok, _ = correr_pasos(nombre, job, ctx, ws, artefactos)
        return ok, {}
    flujo = flujo_llamado(job["uses"], repo, trabajo)
    llamada = flujo[True]["workflow_call"] if True in flujo else flujo["on"]["workflow_call"]
    entradas = {}
    for k, d in llamada["inputs"].items():
        v = (job.get("with") or {}).get(k, d.get("default"))
        if d.get("required") and k not in (job.get("with") or {}):
            raise SystemExit("ENSAYO: %s no da la entrada obligatoria %s" % (nombre, k))
        v = interpolar(v, ctx) if isinstance(v, str) else v
        if d["type"] == "boolean" and isinstance(v, str):
            v = v == "true"
        entradas[k] = v
    sobra = set(job.get("with") or {}) - set(llamada["inputs"])
    if sobra:
        raise SystemExit("ENSAYO: %s da entradas que el flujo no declara: %s" % (nombre, sorted(sobra)))
    interno = Contexto(dict(base, inputs=entradas, needs={}, _env={k: str(v) for k, v in (flujo.get("env") or {}).items()}))
    salidas_jobs, ok = {}, True
    for nj, j in flujo["jobs"].items():
        okj, cj = correr_pasos(nombre + "/" + nj, j, interno, ws, artefactos)
        ok &= okj
        salidas_jobs[nj] = {"outputs": {k: texto(interpolar(v, cj)) for k, v in (j.get("outputs") or {}).items()}}
    if not ok:
        print("  salidas de un job fallido: el ensayo las pasa; GitHub puede no hacerlo")
    fuera = Contexto(dict(base, jobs=salidas_jobs))
    return ok, {k: texto(interpolar(v["value"], fuera)) for k, v in (llamada.get("outputs") or {}).items()}


def informes_como(trabajo, corrida_1, resultado):
    """Para negativo, positivo y real: el INFORME.json del ensayo, igual al de la corrida de la etapa 23."""
    c1 = json.load(open(corrida_1, encoding="utf-8"))
    out = {}
    for j in ("negativo", "positivo", "real"):
        if j not in resultado:
            continue
        inf = os.path.join(trabajo, j, "trabajo", "corrida", "INFORME.json")
        h = hashlib.sha256(open(inf, "rb").read()).hexdigest() if os.path.exists(inf) else None
        esperado = (c1["artefactos"].get("verificador-%s-1" % j) or {}).get("informe_sha256")
        out[j] = h is not None and h == esperado
        print("  informe de %s frente a la corrida 1: %s" % (j, "igual" if out[j] else "DISTINTO"))
    return out


def main(argv):
    repo, trabajo, jobs = os.path.abspath(argv[0]), os.path.abspath(argv[1]), argv[2].split(",")

    def opcion(n, por_omision=None):
        return argv[argv.index(n) + 1] if n in argv else por_omision
    flujo = opcion("--flujo", "demo-ci")
    rojo = set((opcion("--rojo", "") or "").split(",")) - {""}
    entradas_a_mano = dict(argv[i + 1].split("=", 1) for i, a in enumerate(argv) if a == "--entrada")
    if opcion("--modo-real"):
        entradas_a_mano["modo_real"] = opcion("--modo-real")
    if os.path.exists(trabajo) and os.listdir(trabajo):
        raise SystemExit("ENSAYO: %s no está vacía" % trabajo)
    os.makedirs(trabajo, exist_ok=True)
    ruta = os.path.join(repo, ".github", "workflows", flujo + ".yml")
    if not os.path.exists(ruta):
        ruta = os.path.join(repo, "verificador", "cv", "ci", "github-ci2", flujo + ".yml")
        print("== %s: no está en .github/workflows/; se ensaya su plantilla" % flujo)
    demo = yaml.safe_load(open(ruta, encoding="utf-8"))
    cabeza = git(repo, "rev-parse", "HEAD").stdout.decode().strip() if os.path.exists(os.path.join(repo, ".git")) else ""
    sha = cabeza if SHA40.match(cabeza) else "e0" * 20                  # 40 hex, como el de GitHub; sin .git, uno que no está
    base_ctx = {"github": {"sha": sha, "ref": "refs/heads/main", "run_attempt": "1", "repository": "LK-Corporation/lab-integraciones",
                           "event_name": opcion("--evento", "push")},
                "inputs": entradas_a_mano, "_repo": repo, "_env": {k: str(v) for k, v in (demo.get("env") or {}).items()}}
    needs, artefactos, resultado = {}, {}, {}
    pendientes = list(jobs)
    while pendientes:
        nombre = pendientes.pop(0)
        j = demo["jobs"][nombre]
        nd = j.get("needs") or []
        nd = [nd] if isinstance(nd, str) else nd
        print("== %s" % nombre)
        cj = Contexto(dict(base_ctx, needs=needs, _ok=all(needs.get(x, {}).get("result") == "success" for x in nd)))
        if not condicion(j.get("if"), cj):
            print("  (saltado por su if:)")
            needs[nombre], resultado[nombre] = {"outputs": {}, "result": "skipped"}, None
        else:
            ok, salidas = correr_job(nombre, demo, repo, trabajo, base_ctx, needs, artefactos)
            needs[nombre] = {"outputs": salidas, "result": "success" if ok else "failure"}
            resultado[nombre] = ok
            if salidas:
                print("  salidas: %s" % json.dumps(salidas, ensure_ascii=False))
        for otro, jo in demo["jobs"].items():
            dep = jo.get("needs") or []
            dep = [dep] if isinstance(dep, str) else dep
            # solo los jobs de comprobación (sin uses:) que dependen de lo corrido; un job que llama al flujo hay que pedirlo
            if otro not in needs and otro not in pendientes and "uses" not in jo and dep and all(x in needs for x in dep):
                pendientes.append(otro)
    bien = {k: (v is False) if k in rojo else (v is True) for k, v in resultado.items()}
    iguales = informes_como(trabajo, opcion("--informes-como"), resultado) if opcion("--informes-como") else {}
    json.dump({"flujo": flujo, "jobs": resultado, "esperado_rojo": sorted(rojo), "como_se_esperaba": bien, "informes_iguales": iguales,
               "needs": needs}, open(os.path.join(trabajo, "ENSAYO.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ensayo: %s" % ", ".join("%s %s%s" % (k, "saltado" if v is None else "verde" if v else "ROJO", " (se esperaba rojo)" if k in rojo else "")
                                   for k, v in resultado.items()))
    return 0 if all(bien.values()) and all(iguales.values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
