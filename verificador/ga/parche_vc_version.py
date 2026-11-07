#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33 (ga/diseno-ga-fable.md §8.2; Jev P10: «la función sigue en la 1 por omisión, y la herramienta pide la 2»): parchea
cv/verificar_conversor.py con sustituciones literales, cada una afirmada una sola vez.
- generar_corpus(..., version=1): con version=1 el cuerpo es el de siempre, sin cambiar una línea; con version=2 lee ga/.
  CASOS.json lleva "version" solo si no es la 1, para que las corridas de la versión 1 escriban lo mismo byte a byte.
- correr(): la opción "version_corpus", 1 por omisión (los llamadores sellados no cambian).
- la línea de órdenes: --version-corpus {1,2}, con la 2 por omisión.
  cd fase12 && python3 ga/parche_vc_version.py [fichero]      (por omisión, cv/verificar_conversor.py)"""
import os
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = sys.argv[1] if len(sys.argv) > 1 else os.path.join(FASE, "cv", "verificar_conversor.py")

CAMBIOS = [
    ("firma",
     "def generar_corpus(carpeta, lab=True, minimos=True, propios=(), muestras=None, limite=None):\n"
     "    textos = collections.OrderedDict((c, []) for c in CORPUS)\n"
     "    if lab:\n",
     "def generar_corpus(carpeta, lab=True, minimos=True, propios=(), muestras=None, limite=None, version=1):\n"
     "    textos = collections.OrderedDict((c, []) for c in CORPUS)\n"
     "    assert version in (1, 2), version                                                # etapa 33: la versión del corpus\n"
     "    if lab and version == 1:\n"),
    ("rama_v2",
     "    if muestras:\n"
     "        for c in (\"ms\", \"lfh\"):\n",
     "    elif lab:                                                                         # etapa 33: la versión 2, en ga/\n"
     "        ga = os.path.join(FASE, \"ga\")\n"
     "        adt = json.load(open(os.path.join(ga, \"bases_adt_v2.json\"), encoding=\"utf-8\")) + \\\n"
     "            json.load(open(os.path.join(ga, \"ejemplos_cap3_v2.json\"), encoding=\"utf-8\")) + \\\n"
     "            json.load(open(os.path.join(ga, \"bases_a1_v2.json\"), encoding=\"utf-8\"))\n"
     "        textos[\"adt\"] = [(x[\"id\"] + \".hl7\", normal(x[\"mensaje\"])) for x in adt]\n"
     "        textos[\"oru\"] = [(\"ORU-%s.hl7\" % b[\"id\"], normal(BO.cable(b))) for b in BO.BASES]\n"
     "        textos[\"vxu\"] = [(\"VXU-%s.hl7\" % b[\"id\"], normal(BV.cable(b))) for b in BV.BASES]\n"
     "        if ga not in sys.path:\n"
     "            sys.path.insert(0, ga)\n"
     "        import bases_mdm_v2 as BM2\n"
     "        textos[\"mdm\"] = [(\"MDM-%s.hl7\" % b[\"id\"], normal(BM2.cable(b))) for b in BM2.BASES]\n"
     "    if muestras:\n"
     "        for c in (\"ms\", \"lfh\"):\n"),
    ("casos_version",
     "          \"huella_adt_oru_muestras\": cv2.hexdigest()}\n"
     "    json.dump(co, open(os.path.join(carpeta, \"CASOS.json\"), \"w\", encoding=\"utf-8\"), ensure_ascii=False, indent=1)\n",
     "          \"huella_adt_oru_muestras\": cv2.hexdigest()}\n"
     "    if version != 1:\n"
     "        co[\"version\"] = version\n"
     "    json.dump(co, open(os.path.join(carpeta, \"CASOS.json\"), \"w\", encoding=\"utf-8\"), ensure_ascii=False, indent=1)\n"),
    ("correr_o",
     "    o = {\"lab\": True, \"minimos\": False, \"propios\": [], \"muestras\": None, \"sensibilidad\": True, \"limite\": None, \"json_solo\": False,\n"
     "         \"comparar\": None}\n",
     "    o = {\"lab\": True, \"minimos\": False, \"propios\": [], \"muestras\": None, \"sensibilidad\": True, \"limite\": None, \"json_solo\": False,\n"
     "         \"comparar\": None, \"version_corpus\": 1}\n"),
    ("correr_llamada",
     "    co = generar_corpus(os.path.join(salida, \"corpus\"), lab=o[\"lab\"], minimos=o[\"minimos\"], propios=o[\"propios\"], muestras=o[\"muestras\"],\n"
     "                        limite=o[\"limite\"])\n",
     "    co = generar_corpus(os.path.join(salida, \"corpus\"), lab=o[\"lab\"], minimos=o[\"minimos\"], propios=o[\"propios\"], muestras=o[\"muestras\"],\n"
     "                        limite=o[\"limite\"], version=o[\"version_corpus\"])\n"),
    ("argumento",
     "    p.add_argument(\"--sin-minimos\", action=\"store_true\",",
     "    p.add_argument(\"--version-corpus\", type=int, choices=(1, 2), default=2,\n"
     "                   help=\"la versión del corpus del laboratorio: 2 (la de la etapa 33, por omisión) o 1 (la de los resultados sellados)\")\n"
     "    p.add_argument(\"--sin-minimos\", action=\"store_true\","),
    ("op",
     "          \"comparar\": a.comparar}\n",
     "          \"comparar\": a.comparar, \"version_corpus\": a.version_corpus}\n"),
    ("solo_orden",
     "                co = generar_corpus(os.path.join(d, \"corpus\"), lab=op[\"lab\"], minimos=op[\"minimos\"], propios=op[\"propios\"],\n"
     "                                    muestras=op[\"muestras\"], limite=op[\"limite\"])\n",
     "                co = generar_corpus(os.path.join(d, \"corpus\"), lab=op[\"lab\"], minimos=op[\"minimos\"], propios=op[\"propios\"],\n"
     "                                    muestras=op[\"muestras\"], limite=op[\"limite\"], version=op[\"version_corpus\"])\n"),
]


def main():
    t = open(F, encoding="utf-8").read()
    for nombre, viejo, nuevo in CAMBIOS:
        n = t.count(viejo)
        if n != 1:
            sys.exit("PARADA: %s aparece %d veces" % (nombre, n))
        t = t.replace(viejo, nuevo)
    open(F, "w", encoding="utf-8").write(t)
    print("parcheado %s: %d sustituciones" % (F, len(CAMBIOS)))


if __name__ == "__main__":
    main()
