#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 27 (Q-PIN, Jev «las dos»): la receta del ejemplo cuenta los casos que junta la herramienta en el commit fijado, en vez de
llevarlos a mano, y la guía dice qué pasa al subir el pin. Idempotente.
  python3 pin/parche_receta_pin.py <raíz con ejemplo-ci/ y la guía en cv/ci/CI.md o verificador/cv/ci/CI.md>"""
import os
import sys

raiz = sys.argv[1]
receta = os.path.join(raiz, "ejemplo-ci", "ci", "hacer_base.sh")
guia = next(p for p in (os.path.join(raiz, "cv", "ci", "CI.md"), os.path.join(raiz, "verificador", "cv", "ci", "CI.md")) if os.path.exists(p))

CAMBIOS = {
    receta: [
        ("base() {   # <nombre> <fichero de la base> <n esperado> [opciones mas]\n",
         "esperado() {   # <lab|propio>: los casos que junta la herramienta en este commit; el numero no va a mano (etapa 27)\n"
         "  python3 -c 'import os, sys, tempfile; sys.path.insert(0, \"cv\"); import verificar_conversor as V\n"
         "co = V.generar_corpus(os.path.join(tempfile.mkdtemp(), \"c\"), lab=sys.argv[1] == \"lab\", minimos=False, propios=[sys.argv[2]])\n"
         "print(len(co[\"casos\"]))' \"$1\" \"$EJ/corpus\"\n"
         "}\n"
         "base() {   # <nombre> <fichero de la base> <n esperado> [opciones mas]\n"),
        ('  [ "$(n_casos "$b")" = "$esperado" ] || para "$n: $(n_casos "$b") casos y se esperaban $esperado"\n',
         '  [ "$(n_casos "$b")" = "$esperado" ] || para "$n: $(n_casos "$b") casos y la herramienta junta $esperado en este commit"\n'),
        ('base ejemplo "$EJ/ci/LINEA-BASE.json" 349\n'
         'base propio "$EJ/ci/LINEA-BASE-propio.json" 6 --json-solo --sin-corpus-lab\n',
         'base ejemplo "$EJ/ci/LINEA-BASE.json" "$(esperado lab)"\n'
         'base propio "$EJ/ci/LINEA-BASE-propio.json" "$(esperado propio)" --json-solo --sin-corpus-lab\n'),
    ],
    guia: [
        ("   - **Cuando subas de commit y cambie el juez o el corpus, regenera la base.** Un juez distinto se avisa y la base propuesta lo marca (`juez_cambiado`).",
         "   - **Cuando subas de commit y cambie el juez o el corpus, regenera la base.** Un juez distinto se avisa y la base propuesta lo marca (`juez_cambiado`).\n"
         "     Sin rehacerla, el flujo sigue en verde en el modo `pasa`: los casos que no estaban en la base solo se anotan\n"
         "     (`casos_nuevos`) y el juez y el corpus distintos son avisos. Se midió al subir el pin del ejemplo al commit con MDM: 40\n"
         "     casos nuevos, sin juzgar frente a nada. Mira los avisos o compruébalos desde fuera, como `ejemplo-comprobado`.\n"
         "     La receta del ejemplo (`ejemplo-ci/ci/hacer_base.sh`) cuenta los casos que junta la herramienta en el commit fijado:\n"
         "     el número cambia con el corpus y no hay que tocarlo a mano."),
    ],
}

for ruta, cambios in CAMBIOS.items():
    t = open(ruta, encoding="utf-8").read()
    for viejo, nuevo in cambios:
        if nuevo in t:
            print("%s: ya estaba" % os.path.basename(ruta))
            continue
        assert t.count(viejo) == 1, "%s: no encuentro %r" % (ruta, viejo[:70])
        t = t.replace(viejo, nuevo)
        print("%s: cambiado" % os.path.basename(ruta))
    open(ruta, "w", encoding="utf-8").write(t)
