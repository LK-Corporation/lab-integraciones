#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 23: ensayo local de la demostración antes del primer push. Corre en la máquina del laboratorio los pasos `run:` de un
job de .github/workflows/demo-ci.yml, y los del flujo reutilizable cuando el job lo llama, con las expresiones `${{ … }}`
evaluadas como las evalúa GitHub en lo que estos dos YAML usan (inputs, steps, needs, jobs, github, &&, ||, !, ==, !=,
always(), success()). Los `actions/checkout` se emulan copiando el árbol del repositorio; `setup-python` y `pip install` no se
emulan (se usa el python3 de la máquina); `upload-artifact` solo lista lo que subiría y comprueba que el nombre no se repite.
No es el runner: el Docker, el usuario, la imagen de Ubuntu y la red son los de la máquina. Lo que prueba es la mecánica de los
YAML (entradas, expresiones, salidas entre jobs, rutas del workspace) y que cada control da lo esperado.
  python3 cv/ci/ensayo_flujo.py <repositorio> <trabajo vacío> <job>[,<job>…] [--modo-real lote|mensaje]
  (job: pruebas, negativo, positivo, real; tras positivo y real corre su «-comprobado»)"""
import json
import os
import re
import shutil
import subprocess
import sys

import yaml

TOKEN = re.compile(r"\s*(?:(?P<cad>'(?:[^']|'')*')|(?P<op>&&|\|\||==|!=|!|\(|\))|(?P<num>\d+)|(?P<id>[A-Za-z_][A-Za-z0-9_.\-]*(?:\(\))?))")


class Contexto(dict):
    def valor(self, nombre):
        if nombre in ("always()", "success()"):
            return nombre == "always()" or self.get("_ok", True)
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
    return bool(evaluar(c, ctx))


def copiar_repo(repo, destino):
    shutil.copytree(repo, destino, ignore=shutil.ignore_patterns(".git", "__pycache__"), dirs_exist_ok=True)


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


def correr_pasos(nombre, job, ctx, ws, artefactos_subidos):
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
        if usa.startswith("actions/checkout@"):
            destino = os.path.normpath(os.path.join(ws, (paso.get("with") or {}).get("path", "")))
            if not os.path.exists(os.path.join(destino, "verificador")):
                copiar_repo(ctx["_repo"], destino)
            print("  [%s] ✓ %s (copia del árbol)" % (nombre, etiqueta))
            continue
        if usa.startswith("actions/setup-python@"):
            print("  [%s] ✓ %s (no se emula: python3 de la máquina)" % (nombre, etiqueta))
            continue
        if usa.startswith("actions/upload-artifact@"):
            w = {k: interpolar(v, ctx) for k, v in (paso.get("with") or {}).items()}
            if w["name"] in artefactos_subidos or re.search(r'[":<>|*?\\/\r\n]', w["name"]):
                print("  [%s] ✗ %s: el nombre de artefacto %r se repite o no vale" % (nombre, etiqueta, w["name"]))
                ctx["_ok"] = False
                continue
            artefactos_subidos.add(w["name"])
            rutas = [r.strip() for r in w["path"].splitlines() if r.strip()]
            hay = [r for r in rutas if os.path.exists(os.path.join(ws, r))]
            print("  [%s] ✓ %s: %s, %d de %d rutas" % (nombre, etiqueta, w["name"], len(hay), len(rutas)))
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


def correr_job(nombre, demo, repo, trabajo, modo_real, needs, artefactos_subidos):
    job = demo["jobs"][nombre]
    ws = os.path.join(trabajo, nombre)
    os.makedirs(ws)
    base = {"github": {"sha": "ensayo", "ref": "refs/heads/main", "run_attempt": "1", "job": nombre, "workspace": ws,
                       "event_name": "push"},
            "inputs": {"modo_real": modo_real} if modo_real else {}, "needs": needs, "_repo": repo,
            "_env": {k: str(v) for k, v in (demo.get("env") or {}).items()}}
    ctx = Contexto(base)
    if "uses" not in job:
        ok, _ = correr_pasos(nombre, job, ctx, ws, artefactos_subidos)
        return ok, {}
    assert job["uses"].startswith("./"), job["uses"]
    flujo = yaml.safe_load(open(os.path.join(repo, job["uses"][2:]), encoding="utf-8"))
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
        okj, cj = correr_pasos(nombre + "/" + nj, j, interno, ws, artefactos_subidos)
        ok &= okj
        salidas_jobs[nj] = {"outputs": {k: texto(interpolar(v, cj)) for k, v in (j.get("outputs") or {}).items()}}
    fuera = Contexto(dict(base, jobs=salidas_jobs))
    return ok, {k: texto(interpolar(v["value"], fuera)) for k, v in (llamada.get("outputs") or {}).items()}


def main(argv):
    repo, trabajo, jobs = os.path.abspath(argv[0]), os.path.abspath(argv[1]), argv[2].split(",")
    modo_real = argv[argv.index("--modo-real") + 1] if "--modo-real" in argv else None
    if os.path.exists(trabajo) and os.listdir(trabajo):
        raise SystemExit("ENSAYO: %s no está vacía" % trabajo)
    os.makedirs(trabajo, exist_ok=True)
    demo = yaml.safe_load(open(os.path.join(repo, ".github", "workflows", "demo-ci.yml"), encoding="utf-8"))
    pendientes = list(jobs) + [j + "-comprobado" for j in jobs if j + "-comprobado" in demo["jobs"]]
    needs, artefactos, resultado = {}, set(), {}
    for nombre in pendientes:
        print("== %s" % nombre)
        ok, salidas = correr_job(nombre, demo, repo, trabajo, modo_real, needs, artefactos)
        needs[nombre] = {"outputs": salidas, "result": "success" if ok else "failure"}
        resultado[nombre] = ok
        if salidas:
            print("  salidas: %s" % json.dumps(salidas, ensure_ascii=False))
    json.dump({"jobs": resultado, "needs": needs}, open(os.path.join(trabajo, "ENSAYO.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("ensayo: %s" % ", ".join("%s %s" % (k, "verde" if v else "ROJO") for k, v in resultado.items()))
    return 0 if all(resultado.values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
