#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 41: ¿cazan las pruebas un juez mal hecho? Cada mutante cambia una cosa del arreglo de PD1-7 (los 18 de la etapa 40, con sus
anclas donde quedó el código tras sacarlo a dos ayudantes, y los de ORU de po/diseno-po-fable.md §3.3) en una copia de la carpeta del
juez, y prueba_conversion.py tiene que caer (salir con 1). Un mutante que sobrevive es un hueco de las pruebas.
  python3 po/mutantes_po.py <carpeta del juez>      (trabaja en <carpeta>-mutantes/, que rehace en cada corrida y no borra al final)"""
import os
import shutil
import subprocess
import sys

CV, MCP = "conversion.py", "mcp_verificador.py"
SIN_MAPA = '[e for e in obs if e["tipo"] == "Observation" and _origen_sin_mapa(m, e["r"])]'
MUTANTES = [
    # ---- los de la etapa 40
    (CV, "sin el criterio del sistema", "        sistema = any(s == S0315 for s, _ in cods)\n", "        sistema = False\n"),
    (CV, "sin el criterio del código", "        if sistema or any(c == v for _, c in cods):\n", "        if sistema:\n"),
    (CV, "la última candidata", "    return (con[0], \"sistema\", len(cands)) if con else (cands[0][0], \"codigo\", len(cands))",
     "    return (con[-1], \"sistema\", len(cands)) if con else (cands[-1][0], \"codigo\", len(cands))"),
    (CV, "sin preferir el sistema", "    return (con[0], \"sistema\", len(cands)) if con else (cands[0][0], \"codigo\", len(cands))",
     "    return (cands[0][0], \"sistema\" if cands[0][1] else \"codigo\", len(cands))"),
    (CV, "sin apartar las del OBX", "        if e[\"tipo\"] != \"Observation\" or obx & {c for _, c in _codigos(e[\"r\"].get(\"code\"))}:\n",
     "        if e[\"tipo\"] != \"Observation\":\n"),
    (CV, "la de PD1-7 sigue en la lista", "        return [e for e in lista if pd17[0] is None or e is not pd17[0]]\n", "        return lista\n"),
    (CV, "ausente como nota", "        J.cuenta(\"recurso_ausente\", \"PD1-7\", \"falta la Observation",
     "        J.nota(\"recurso_ausente\", \"PD1-7\", \"falta la Observation"),
    (CV, "sin ausente", "    if o is None or o[\"entry\"] is None:\n", "    if False:\n"),
    (CV, "solo en 2.5", "    v7 = _valor_pd17(m)\n    if not v7:\n", "    v7 = _valor_pd17(m) if J.v25 else \"\"\n    if not v7:\n"),
    (CV, "sin status", "    if st not in ESTADO_FHIR[\"0085\"]:\n", "    if False:\n"),
    (CV, "sin sujeto", "    _sujeto(J, m, r, entry, pat_entry, \"Observation.subject\", \"PD1-7\", citas=citas)\n", "    pass\n"),
    (CV, "valor y código cambiados", "        if any(s == S0315 for s, _ in obs):\n            J.cuenta(\"valor_distinto\"",
     "        if not any(s == S0315 for s, _ in obs):\n            J.cuenta(\"valor_distinto\""),
    (CV, "convención en toda versión", "            J.nota(\"convencion\" if J.v25 else \"version\", \"PD1-7\"",
     "            J.nota(\"convencion\", \"PD1-7\""),
    (CV, "nota aunque el código sea el mismo", "        if obs and v not in {c for _, c in obs}:\n", "        if obs:\n"),
    (CV, "el campo entero", "    return _t(m, _f(m, pd1, 7), 1) if pd1 is not None else \"\"",
     "    return _f(m, pd1, 7) or \"\" if pd1 is not None else \"\""),
    (CV, "PD1-6 en vez de PD1-7", "    return _t(m, _f(m, pd1, 7), 1) if pd1 is not None else \"\"",
     "    return _t(m, _f(m, pd1, 6), 1) if pd1 is not None else \"\""),
    (CV, "la 0315 con F a N", "'F': ('http://terminology.hl7.org/CodeSystem/v2-0315', 'F')", "'F': ('http://terminology.hl7.org/CodeSystem/v2-0315', 'N')"),
    (CV, "el paso de PD1-7 tras ACC y PDA", "        obs = apartar_pd17(obs)                                            # etapa 40",
     "        obs = apartar_pd17([e for e in obs if e not in %s]) + %s  # etapa 40" % (SIN_MAPA, SIN_MAPA)),
    # ---- los de la etapa 41 (ORU)
    (CV, "ORU sin apartar_pd17", "        ob = apartar_pd17(ob)                                              # etapa 41",
     "        ob = ob                                                            # etapa 41"),
    (CV, "ORU sin _juzgar_pd17", "        _juzgar_pd17(J, m, roles, pat_entry, \"oru\")", "        pass  # _juzgar_pd17(J, m, roles, pat_entry, \"oru\")"),
    (CV, "ORU: apartar_pd17 tras las sobrantes", "        ob = apartar_pd17(ob)                                              # etapa 41",
     "        ob = ob                                                            # etapa 41"),
    (CV, "_origen_pd17 solo con los OBX de ORDER_OBSERVATION",
     "        return None\n    obx = {c for s in m.segmentos(\"OBX\") for c in (_t(m, _f(m, s, 3), 1), _t(m, _f(m, s, 3), 4)) if c}",
     "        return None\n    obx = {c for g in _grupos_oru(m)[0] for s in g[1] for c in (_t(m, _f(m, s, 3), 1), _t(m, _f(m, s, 3), 4)) if c}"),
    (CV, "_juzgar_pd17 solo en ADT", "    citas = CITAS_PD17[familia]\n", "    if familia != \"adt\":\n        return\n    citas = CITAS_PD17[familia]\n"),
    (CV, "ORU con las citas de ADT", "    citas = CITAS_PD17[familia]\n", "    citas = C[\"PD1-7\"]\n"),
    (CV, "sin la fila de PD1-7 en el perfil de ORU", "    {\"elemento\": \"Observation (de PD1-7)\", \"campo\": \"PD1-7\", \"regla\": \"IF PD1-7 VALUED: valueCodeableConcept por la 0315 (identidad), status y subject; se reconoce por el sistema de la 0315 o el código de PD1-7, aparte",
     "    {\"elemento\": \"Observation (de PD1-7)\", \"campo\": \"—\", \"regla\": \"IF PD1-7 VALUED: valueCodeableConcept por la 0315 (identidad), status y subject; se reconoce por el sistema de la 0315 o el código de PD1-7, aparte"),
    (CV, "L-CV-18 sin ORU", "en oru_conv se aparta antes de casar las de los OBX", "en un ORU se aparta antes de casar las de los OBX"),
    (CV, "S-CV-4 sin ORU", "en ADT y, desde la etapa 41, en ORU) resolviendo", "en ADT) resolviendo"),
    (MCP, "el texto de versión sin la 41", 'REVISION = ("etapa 41: la Observation de PD1-7 también en oru_conv (S-CV-4) y L-CV-18; "\n            "antes, etapa 40: ',
     'REVISION = ("etapa 40: '),
]
EXTRA = {"ORU: apartar_pd17 tras las sobrantes": ("    out[\"_usados\"] = usados\n",
                                                 "    if familia not in (\"adt\", \"vxu\", \"mdm\"):\n"
                                                 "        apartar_pd17([e for e in top if e[\"tipo\"] == \"Observation\"])\n"
                                                 "    out[\"_usados\"] = usados\n")}


def main(carpeta):
    base = os.path.abspath(carpeta).rstrip(os.sep) + "-mutantes"
    if os.path.isdir(base):
        shutil.rmtree(base)
    os.makedirs(base)
    origs = {f: open(os.path.join(carpeta, f), encoding="utf-8", newline="").read() for f in (CV, MCP)}
    vivos = []
    for i, (f, nombre, antes, despues) in enumerate(MUTANTES, 1):
        t = origs[f]
        assert t.count(antes) == 1, "%s: %d veces" % (nombre, t.count(antes))
        t = t.replace(antes, despues)
        if nombre in EXTRA:
            a2, d2 = EXTRA[nombre]
            assert t.count(a2) == 1, "%s (extra): %d veces" % (nombre, t.count(a2))
            t = t.replace(a2, d2)
        d = os.path.join(base, "m%02d" % i)
        shutil.copytree(carpeta, d, ignore=shutil.ignore_patterns("__pycache__", "bases_oru*", "*-mutantes"))
        open(os.path.join(d, f), "w", encoding="utf-8", newline="").write(t)
        r = subprocess.run([sys.executable, "prueba_conversion.py"], cwd=d, capture_output=True, text=True, timeout=600)
        caen = sorted({l.split()[1].rstrip(":") + (" (excepción)" if l.startswith("  EXCEPCIÓN ") else "")
                       for l in r.stdout.splitlines() if l.startswith("  MAL ") or l.startswith("  EXCEPCIÓN ")})
        print("%-50s %s %s" % (nombre, "MUERE" if r.returncode else "VIVE ", ", ".join(caen)), flush=True)
        if not r.returncode:
            vivos.append(nombre)
    print("mutantes: %d, vivos: %d %s" % (len(MUTANTES), len(vivos), vivos))
    return 1 if vivos else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
