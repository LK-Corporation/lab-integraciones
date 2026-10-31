#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 26 (MD-pre, E-MD-4): el inventario de contraste de MDM, como privado/vxu/contraste/ en la etapa 20. Guarda, de los dos
proyectos, los issues y PR que hablan de MDM o de DocumentReference, con su cuerpo y sus comentarios (gh api, solo lectura), y
lista lo que publican como salida esperada o prueba de MDM en las copias fijadas. No se le pasa al diseñador.
  python3 md/inventario_contraste_mdm.py <carpeta de salida vacía> <copia de Microsoft> <copia de LinuxForHealth>"""
import json
import os
import subprocess
import sys

REPOS = {"microsoft": "microsoft/FHIR-Converter", "linuxforhealth": "LinuxForHealth/hl7v2-fhir-converter"}
TERMINOS = ["MDM", "DocumentReference", "TXA"]


def gh(*a):
    r = subprocess.run(["gh"] + list(a), capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise SystemExit("gh %s: %s" % (" ".join(a[:3]), r.stderr[:300]))
    return r.stdout


def buscar(repo):
    vistos = {}
    for t in TERMINOS:
        q = "repo:%s %s" % (repo, t)
        for linea in gh("api", "--paginate", "-X", "GET", "search/issues", "-f", "q=" + q, "-f", "per_page=100",
                        "--jq", ".items[] | @json").splitlines():
            if linea.strip():
                i = json.loads(linea)
                vistos.setdefault(i["number"], i)
    return vistos


def main(salida, ms, lfh):
    assert not os.path.exists(salida) or not os.listdir(salida), "la carpeta de salida tiene que estar vacía"
    os.makedirs(salida, exist_ok=True)
    resumen = ["# Inventario de contraste de MDM (E-MD-4)", "",
               "No se le pasa al diseñador. Issues y PR por búsqueda de «%s» en cada repositorio (gh api, solo lectura)." % "», «".join(TERMINOS), ""]
    for nombre, repo in REPOS.items():
        items = buscar(repo)
        d = os.path.join(salida, nombre)
        os.makedirs(d, exist_ok=True)
        for n, i in sorted(items.items()):
            coms = []
            if i.get("comments"):
                coms = [json.loads(l) for l in gh("api", "--paginate", "repos/%s/issues/%d/comments" % (repo, n), "--jq", ".[] | @json").splitlines() if l.strip()]
            json.dump({"numero": n, "titulo": i["title"], "estado": i["state"], "pr": "pull_request" in i, "url": i["html_url"],
                       "creado": i["created_at"], "cerrado": i.get("closed_at"), "cuerpo": i.get("body") or "",
                       "comentarios": [{"fecha": c["created_at"], "cuerpo": c.get("body") or ""} for c in coms]},
                      open(os.path.join(d, "%d.json" % n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        prs = sum(1 for i in items.values() if "pull_request" in i)
        resumen.append("## %s (`%s`)" % (nombre, repo))
        resumen.append("- %d issues y PR (%d PR, %d issues), en `%s/`." % (len(items), prs, len(items) - prs, nombre))
        for n, i in sorted(items.items()):
            resumen.append("  - #%d %s [%s%s] %s" % (n, i["title"][:90], "PR, " if "pull_request" in i else "", i["state"], ""))
        resumen.append("")
    esperadas = os.path.join(ms, "src", "Microsoft.Health.Fhir.Liquid.Converter.FunctionalTests", "TestData", "Expected", "Hl7v2")
    resumen.append("## Salidas esperadas y pruebas en las copias fijadas")
    for carpeta in sorted(os.listdir(esperadas)) if os.path.isdir(esperadas) else []:
        if carpeta.startswith("MDM"):
            resumen.append("- Microsoft, `%s`: %s" % (carpeta, ", ".join(sorted(os.listdir(os.path.join(esperadas, carpeta))))))
    for raiz, _, fs in sorted(os.walk(os.path.join(lfh, "src", "test"))):
        for f in sorted(fs):
            if f.endswith(".java"):
                t = open(os.path.join(raiz, f), encoding="utf-8").read()
                if "MDM^" in t:
                    resumen.append("- LinuxForHealth, `%s`: %d pruebas (@Test o @ParameterizedTest) en el fichero" % (
                        f, t.count("@Test") + t.count("@ParameterizedTest")))
    open(os.path.join(salida, "INVENTARIO.md"), "w", encoding="utf-8").write("\n".join(resumen) + "\n")
    print("\n".join(resumen))


if __name__ == "__main__":
    main(*sys.argv[1:4])
