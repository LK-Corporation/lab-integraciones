#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 35, tras la revisión a ciegas (DV-CR-3; menores 2 y 3): en cv/ci/comprobar_publicado.py, una lista de flujos vacía, un
ENSAYO.json con tipos raros y unos argumentos mal puestos salen con 2 («no se pudo comprobar»), y no con un verde sin comparar nada
o con una traza y 1. Afirma cada texto. Idempotente.  cd fase12 && python3 cr/parche_comprobar_cr.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(FASE, "cv", "ci", "comprobar_publicado.py")
CAMBIOS = [
    ("- Sale con 2 si no pudo comprobar: el remoto o la rama no se leen, un ENSAYO.json no es JSON, dos ensayos del mismo flujo.\n",
     "- Sale con 2 si no pudo comprobar: el remoto o la rama no se leen, un ENSAYO.json no es JSON o no es válido, dos ensayos del\n"
     "  mismo flujo, ningún flujo que comprobar, o los argumentos están mal.\n"),
    ("    if not isinstance(d, dict) or not d.get(\"flujo\"):\n"
     "        raise NoSePuede(\"%s no es un ENSAYO.json: no dice su flujo\" % ruta)\n",
     "    def raro(que):\n"
     "        raise NoSePuede(\"%s no es un ENSAYO.json válido: %s\" % (ruta, que))\n"
     "    if not isinstance(d, dict) or not isinstance(d.get(\"flujo\"), str) or not d[\"flujo\"]:\n"
     "        raro(\"no dice su flujo\")\n"
     "    for k in (\"jobs\", \"como_se_esperaba\", \"informes_iguales\", \"clon\"):\n"
     "        if d.get(k) is not None and not isinstance(d[k], dict):\n"
     "            raro(\"%s no es un objeto\" % k)\n"),
    ("    clon = d.get(\"clon\") or {}\n",
     "    clon = d.get(\"clon\") or {}\n"
     "    for k in (\"arbol\", \"head\", \"tipo\"):\n"
     "        if clon.get(k) is not None and not isinstance(clon[k], str):\n"
     "            raro(\"clon.%s no es un texto\" % k)\n"),
    ("def main(argv):\n",
     "def main(argv):\n"
     "    try:\n"
     "        return comprobar(argv)\n"
     "    except (IndexError, ValueError) as ex:                              # los argumentos, mal puestos\n"
     "        print(\"no se pudo comprobar: los argumentos están mal (%s)\" % ex)\n"
     "        return 2\n"
     "\n"
     "\n"
     "def comprobar(argv):\n"),
    ("    try:\n"
     "        commit, arbol = publicado(repo, remoto, rama)\n",
     "    try:\n"
     "        if not flujos:\n"
     "            raise NoSePuede(\"no hay flujos que comprobar (--flujos vacío)\")\n"
     "        commit, arbol = publicado(repo, remoto, rama)\n"),
]
t = open(P, encoding="utf-8").read()
if "def comprobar(argv):" not in t:
    for viejo, nuevo in CAMBIOS:
        assert t.count(viejo) == 1, "no está (o no es único): %r" % viejo[:80]
        t = t.replace(viejo, nuevo)
    open(P, "w", encoding="utf-8").write(t)
print("cv/ci/comprobar_publicado.py: entradas raras y flujos vacíos, con 2")
