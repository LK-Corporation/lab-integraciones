#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33 (DV-GA-9): las líneas base de la demostración llevaban a mano el número de casos (383 y 451, los de la versión 1), y con
la versión 2 del corpus hacer_bases.py se paraba en el juguete (390). Como la receta del ejemplo desde la etapa 27, el número sale
ahora de lo que junta la herramienta de la copia pública, con su versión por omisión (la 2). Y base_nc.sh se para si las bases no
salen, en vez de seguir con la corrida mensaje a mensaje contra la base vieja. Sustituciones literales, afirmadas una a una.
  cd fase12 && python3 ga/parche_bases_ga.py"""
import os
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMBIOS = {
    "cv/ci/hacer_bases.py": [
        ("def lb(*a):\n",
         "def casos_herramienta(minimos):\n"
         "    \"\"\"Los casos que junta la herramienta de la copia pública con su corpus por omisión (etapa 33: la versión 2), sin propios.\"\"\"\n"
         "    r = subprocess.run([PYTHON, \"-c\", \"import os, sys, tempfile; sys.argv = ['x', '--silencio']; sys.path.insert(0, 'cv'); \"\n"
         "                        \"import verificar_conversor as V; co = V.generar_corpus(os.path.join(tempfile.mkdtemp(), 'c'), lab=True, \"\n"
         "                        \"minimos=%s, version=2); print(len(co['casos']))\" % bool(minimos)], cwd=PUB, capture_output=True, text=True)\n"
         "    if r.returncode:\n"
         "        parar(\"no se pudo contar el corpus de la copia pública: %s\" % r.stderr[-300:])\n"
         "    return int(r.stdout.split()[-1])\n\n\n"
         "def lb(*a):\n"),
        ('    s1, d = base("juguete", "cv/adaptadores/juguete.json", "cv", 383)          # etapa 26: 343 + las 40 de MDM\n',
         '    s1, d = base("juguete", "cv/adaptadores/juguete.json", "cv", casos_herramienta(False))  # etapa 33: lo que junta la herramienta\n'),
        ('    base("linuxforhealth", "cv/adaptadores/linuxforhealth.json", ART, 451)                         # etapa 26: 411 + 40\n',
         '    base("linuxforhealth", "cv/adaptadores/linuxforhealth.json", ART, casos_herramienta(True))     # etapa 33: con los mínimos\n'),
        ('    base("linuxforhealth-mensaje", "cv/adaptadores/linuxforhealth-mensaje.json", ART, 451, dos=False)   # etapa 26: 411 + 40\n',
         '    base("linuxforhealth-mensaje", "cv/adaptadores/linuxforhealth-mensaje.json", ART, casos_herramienta(True), dos=False)   # etapa 33\n'),
    ],
    "base_nc.sh": [
        ('echo "rc_bases=$?" >> $P/HECHO\n',
         'rc=$?\necho "rc_bases=$rc" >> $P/HECHO\n[ $rc -eq 0 ] || { echo "PARADA: las bases no salieron" >> $P/HECHO; echo "fin=$(date -Is)" >> $P/HECHO; exit 1; }\n'),
    ],
}
for f, cs in CAMBIOS.items():
    p = os.path.join(FASE, f)
    t = open(p, encoding="utf-8").read()
    for viejo, nuevo in cs:
        if nuevo in t:
            continue
        assert t.count(viejo) == 1, (f, viejo[:70])
        t = t.replace(viejo, nuevo)
    open(p, "w", encoding="utf-8").write(t)
    print("parcheado", f)
