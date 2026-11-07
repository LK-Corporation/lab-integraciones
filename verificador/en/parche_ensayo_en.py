#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 34 (en/diseno-en-fable.md §3; en/decision-jev-en.md): el arreglo de cv/ci/ensayo_flujo.py. Los checkouts se emulan con lo
que se publica (el índice del clon, o el HEAD si coinciden); con cambios sin git add o ficheros sin seguimiento no se ensaya nada
y sale con 2. DV-EN-1: sin .git, el checkout cuyo ref es el marcador de github.sha no avisa. Afirma cada texto. Idempotente.
  cd fase12 && python3 en/parche_ensayo_en.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(FASE, "cv", "ci", "ensayo_flujo.py")

CAMBIOS = [
    # el docstring
    ('"""Etapas 23 y 24: ensayo local',
     '"""Etapas 23, 24 y 34: ensayo local'),
    ("- Los `actions/checkout` se emulan: con un `ref` de 40 hex que esté en el repositorio, con `git archive` de ese commit; si no,\n"
     "  copiando el árbol.\n",
     "- Los `actions/checkout` se emulan con lo que se publica (etapa 34, en/diseno-en-fable.md): con un `ref` de 40 hex que esté en\n"
     "  el repositorio, `git archive` de ese commit; sin `ref` o con `github.sha`, el índice del clon (`git archive` del árbol de\n"
     "  `write-tree`, o el HEAD si coinciden), y `github.sha` es ese árbol; sin `.git`, la carpeta tal cual. Con cambios sin\n"
     "  `git add` o ficheros sin seguimiento no se ensaya nada: sale con 2. Los ignorados no entran.\n"),
    ("  rojo-comprobado…; un job que llama al flujo, como real, solo corre si se pide)\"\"\"",
     "  rojo-comprobado…; un job que llama al flujo, como real, solo corre si se pide)\n"
     "  Códigos: 0, todo como se esperaba; 1, algún job no; 2, no se ensayó (cambios sin git add, ficheros sin seguimiento o sin commits).\"\"\""),
    # copiar_repo, exportar y estado_del_clon
    ("def copiar_repo(repo, destino, ref=None):\n"
     "    os.makedirs(destino, exist_ok=True)\n"
     "    if hay_commit(repo, ref):\n"
     "        a = subprocess.run([\"git\", \"-C\", repo, \"archive\", ref], capture_output=True, check=True).stdout\n"
     "        subprocess.run([\"tar\", \"-x\", \"-C\", destino], input=a, check=True)\n"
     "        return \"git archive %s\" % ref[:12]\n"
     "    shutil.copytree(repo, destino, ignore=shutil.ignore_patterns(\".git\", \"__pycache__\"), dirs_exist_ok=True)\n"
     "    return \"copia del árbol\"\n",
     "def estado_del_clon(repo, temporal):\n"
     "    \"\"\"Etapa 34: lo que se publica, decidido una vez al empezar. Sin .git, {\"git\": False}. Con .git: el HEAD, el árbol del índice\n"
     "    (write-tree sobre una copia del índice, que no se toca), lo publicado (el HEAD si los árboles coinciden; si no, el árbol) y\n"
     "    las rutas distintas en el índice, sin git add y sin seguimiento (los ignorados no cuentan).\"\"\"\n"
     "    if not os.path.exists(os.path.join(repo, \".git\")):\n"
     "        return {\"git\": False}\n"
     "    st = git(repo, \"status\", \"--porcelain=v1\", \"-z\", \"--untracked-files=all\")\n"
     "    if st.returncode != 0:\n"
     "        raise SystemExit(\"ENSAYO: git status falla en %s: %s\" % (repo, st.stderr.decode(\"utf-8\", \"replace\").strip()))\n"
     "    indice, sin_add, sin_seguimiento = [], [], []\n"
     "    partes, i = st.stdout.decode(\"utf-8\", \"replace\").split(\"\\0\"), 0\n"
     "    while i < len(partes):\n"
     "        e, i = partes[i], i + 1\n"
     "        if not e:\n"
     "            continue\n"
     "        x, y, ruta = e[0], e[1], e[3:]\n"
     "        if x in \"RC\":                                                     # con -z, el origen del renombrado va aparte\n"
     "            i += 1\n"
     "        if (x, y) == (\"?\", \"?\"):\n"
     "            sin_seguimiento.append(ruta)\n"
     "        elif \"U\" in (x, y) or (x, y) in ((\"A\", \"A\"), (\"D\", \"D\")):         # sin fusionar\n"
     "            sin_add.append(ruta)\n"
     "        else:\n"
     "            if x in \"MADRCT\":\n"
     "                indice.append(\"%s %s\" % (x, ruta))\n"
     "            if y not in \" ?\":\n"
     "                sin_add.append(ruta)\n"
     "    clon = {\"git\": True, \"head\": None, \"arbol\": None, \"publicado\": None, \"tipo\": None,\n"
     "            \"indice_distinto\": indice, \"sin_add\": sin_add, \"sin_seguimiento\": sin_seguimiento}\n"
     "    head = git(repo, \"rev-parse\", \"--verify\", \"-q\", \"HEAD^{commit}\").stdout.decode().strip()\n"
     "    if not SHA40.match(head):\n"
     "        return dict(clon, sin_commits=True)\n"
     "    clon[\"head\"] = head\n"
     "    if sin_add or sin_seguimiento:\n"
     "        return clon\n"
     "    os.makedirs(os.path.dirname(temporal), exist_ok=True)\n"
     "    indice_git = git(repo, \"rev-parse\", \"--git-path\", \"index\").stdout.decode().strip()\n"
     "    shutil.copyfile(os.path.join(repo, indice_git), temporal)\n"
     "    w = subprocess.run([\"git\", \"-C\", repo, \"write-tree\"], env=dict(os.environ, GIT_INDEX_FILE=temporal), capture_output=True)\n"
     "    os.remove(temporal)\n"
     "    arbol = w.stdout.decode().strip()\n"
     "    if w.returncode != 0 or not SHA40.match(arbol):\n"
     "        raise SystemExit(\"ENSAYO: git write-tree falla en %s: %s\" % (repo, w.stderr.decode(\"utf-8\", \"replace\").strip()))\n"
     "    igual = git(repo, \"rev-parse\", \"HEAD^{tree}\").stdout.decode().strip() == arbol\n"
     "    return dict(clon, arbol=arbol, publicado=head if igual else arbol, tipo=\"commit\" if igual else \"arbol\")\n"
     "\n"
     "\n"
     "def exportar(repo, destino, objeto):\n"
     "    a = subprocess.run([\"git\", \"-C\", repo, \"archive\", objeto], capture_output=True, check=True).stdout\n"
     "    subprocess.run([\"tar\", \"-x\", \"-C\", destino], input=a, check=True)\n"
     "\n"
     "\n"
     "def copiar_repo(repo, destino, ref, clon):\n"
     "    \"\"\"Un checkout, con lo que se publica (etapa 34). Devuelve el texto de su línea.\"\"\"\n"
     "    os.makedirs(destino, exist_ok=True)\n"
     "    if not clon[\"git\"]:\n"
     "        shutil.copytree(repo, destino, ignore=shutil.ignore_patterns(\".git\", \"__pycache__\"), dirs_exist_ok=True)\n"
     "        if ref and ref != clon[\"sha\"]:                                    # DV-EN-1: el marcador de github.sha no avisa\n"
     "            return \"copia del árbol; el commit %s no se puede resolver sin .git\" % ref[:12]\n"
     "        return \"copia del árbol\"\n"
     "\n"
     "    def publicado():\n"
     "        exportar(repo, destino, clon[\"publicado\"])\n"
     "        if clon[\"tipo\"] == \"commit\":\n"
     "            return \"git archive %s\" % clon[\"head\"][:12]\n"
     "        return \"árbol del índice %s, no el HEAD %s\" % (clon[\"arbol\"][:12], clon[\"head\"][:12])\n"
     "    if not ref or ref == clon[\"sha\"]:\n"
     "        return publicado()\n"
     "    if hay_commit(repo, ref):\n"
     "        exportar(repo, destino, ref)\n"
     "        return \"git archive %s\" % ref[:12]\n"
     "    return \"el commit %s no está en esta copia: %s\" % (ref[:40], publicado())\n"),
    # el checkout en correr_pasos
    ("                como = copiar_repo(ctx[\"_repo\"], destino, w.get(\"ref\"))\n",
     "                como = copiar_repo(ctx[\"_repo\"], destino, w.get(\"ref\"), ctx[\"_clon\"])\n"),
    # main: el estado del clon, la parada y la cabecera
    ("    os.makedirs(trabajo, exist_ok=True)\n",
     "    os.makedirs(trabajo, exist_ok=True)\n"
     "    clon = estado_del_clon(repo, os.path.join(trabajo, \".runner\", \"indice\"))\n"
     "    if clon.get(\"sin_commits\") or clon.get(\"sin_add\") or clon.get(\"sin_seguimiento\"):\n"
     "        def lista(rutas):\n"
     "            return \" (%s%s)\" % (\", \".join(rutas[:20]), \", … y %d más\" % (len(rutas) - 20) if len(rutas) > 20 else \"\") if rutas else \"\"\n"
     "        if clon.get(\"sin_commits\"):\n"
     "            motivo = \"el clon no tiene commits\"\n"
     "        else:\n"
     "            motivo = (\"%d cambios sin git add%s y %d ficheros sin seguimiento%s: no entrarían en lo publicado. git add lo que vaya, \"\n"
     "                      \"git stash -u lo que no, o ensaya una exportación del índice (git checkout-index -a --prefix=<carpeta>/)\"\n"
     "                      % (len(clon[\"sin_add\"]), lista(clon[\"sin_add\"]), len(clon[\"sin_seguimiento\"]), lista(clon[\"sin_seguimiento\"])))\n"
     "        print(\"== NO SE ENSAYA: %s\" % motivo)\n"
     "        json.dump({\"flujo\": flujo, \"jobs\": {}, \"esperado_rojo\": [], \"como_se_esperaba\": {}, \"informes_iguales\": {}, \"needs\": {},\n"
     "                   \"no_ensayado\": motivo, \"clon\": clon}, open(os.path.join(trabajo, \"ENSAYO.json\"), \"w\", encoding=\"utf-8\"),\n"
     "                  ensure_ascii=False, indent=1)\n"
     "        return 2\n"
     "    if not clon[\"git\"]:\n"
     "        print(\"== la carpeta no tiene .git: se ensaya tal cual; quien la exportó responde de que sea lo que se publica\")\n"
     "    elif clon[\"tipo\"] == \"commit\":\n"
     "        print(\"== lo que se publica: el commit HEAD %s (índice igual)\" % clon[\"head\"][:12])\n"
     "    else:\n"
     "        print(\"== lo que se publica: el árbol del índice %s (HEAD %s, %d rutas distintas); github.sha es ese árbol, no un commit\"\n"
     "              % (clon[\"arbol\"][:12], clon[\"head\"][:12], len(clon[\"indice_distinto\"])))\n"),
    ("    cabeza = git(repo, \"rev-parse\", \"HEAD\").stdout.decode().strip() if os.path.exists(os.path.join(repo, \".git\")) else \"\"\n"
     "    sha = cabeza if SHA40.match(cabeza) else \"e0\" * 20                  # 40 hex, como el de GitHub; sin .git, uno que no está\n",
     "    sha = clon[\"publicado\"] if clon[\"git\"] else \"e0\" * 20             # 40 hex, como el de GitHub: el commit o el árbol del índice;\n"
     "    clon[\"sha\"] = sha                                                   # sin .git, uno que no está\n"),
    ("\"inputs\": entradas_a_mano, \"_repo\": repo, ",
     "\"inputs\": entradas_a_mano, \"_repo\": repo, \"_clon\": clon, "),
    # ENSAYO.json y la última línea
    ("               \"needs\": needs}, open(os.path.join(trabajo, \"ENSAYO.json\"), \"w\", encoding=\"utf-8\"), ensure_ascii=False, indent=1)\n"
     "    print(\"ensayo: %s\" % \", \".join(",
     "               \"needs\": needs, \"clon\": clon}, open(os.path.join(trabajo, \"ENSAYO.json\"), \"w\", encoding=\"utf-8\"), ensure_ascii=False,\n"
     "              indent=1)\n"
     "    sobre = (\"ensayo sobre la carpeta sin .git\" if not clon[\"git\"] else \"ensayo sobre el commit HEAD %s\" % clon[\"head\"][:12]\n"
     "             if clon[\"tipo\"] == \"commit\" else \"ensayo sobre el árbol del índice %s (≠ HEAD %s)\" % (clon[\"arbol\"][:12], clon[\"head\"][:12]))\n"
     "    print(\"%s: %s\" % (sobre, \", \".join("),
    ("                                   for k, v in resultado.items()))\n",
     "                                         for k, v in resultado.items())))\n"),
]

t = open(P, encoding="utf-8").read()
if "def estado_del_clon(" not in t:
    for viejo, nuevo in CAMBIOS:
        assert t.count(viejo) == 1, "no está (o no es único): %r" % viejo[:80]
        t = t.replace(viejo, nuevo)
    open(P, "w", encoding="utf-8").write(t)
print("cv/ci/ensayo_flujo.py: el ensayo con lo que se publica")
