#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 40: ¿cazan las pruebas un juez mal hecho? Cada mutante cambia una cosa del arreglo de PD1-7 en una copia de la carpeta del
juez, y prueba_conversion.py tiene que caer (salir con 1). Un mutante que sobrevive es un hueco de las pruebas.
  python3 mutantes_pd.py <carpeta del juez>      (trabaja en <carpeta>-mutantes/, que rehace en cada corrida y no borra al final)"""
import os
import shutil
import subprocess
import sys

MUTANTES = [
    ("sin el criterio del sistema", "        sistema = any(s == S0315 for s, _ in cods)\n", "        sistema = False\n"),
    ("sin el criterio del código", "        if sistema or any(c == v for _, c in cods):\n", "        if sistema:\n"),
    ("la última candidata", "    return (con[0], \"sistema\", len(cands)) if con else (cands[0][0], \"codigo\", len(cands))",
     "    return (con[-1], \"sistema\", len(cands)) if con else (cands[-1][0], \"codigo\", len(cands))"),
    ("sin preferir el sistema", "    return (con[0], \"sistema\", len(cands)) if con else (cands[0][0], \"codigo\", len(cands))",
     "    return (cands[0][0], \"sistema\" if cands[0][1] else \"codigo\", len(cands))"),
    ("sin apartar las del OBX", "        if e[\"tipo\"] != \"Observation\" or obx & {c for _, c in _codigos(e[\"r\"].get(\"code\"))}:\n",
     "        if e[\"tipo\"] != \"Observation\":\n"),
    ("la de PD1-7 sigue en la lista", "            obs = [e for e in obs if pd17[0] is None or e is not pd17[0]]\n", "            pass\n"),
    ("ausente como nota", "                J.cuenta(\"recurso_ausente\", \"PD1-7\", \"falta la Observation",
     "                J.nota(\"recurso_ausente\", \"PD1-7\", \"falta la Observation"),
    ("sin ausente", "            if o is None or o[\"entry\"] is None:\n", "            if False:\n"),
    ("solo en 2.5", "        v7 = _valor_pd17(m)                                            # etapa 40",
     "        v7 = _valor_pd17(m) if J.v25 else \"\"                         # etapa 40"),
    ("sin status", "    if st not in ESTADO_FHIR[\"0085\"]:\n", "    if False:\n"),
    ("sin sujeto", "    _sujeto(J, m, r, entry, pat_entry, \"Observation.subject\", \"PD1-7\")\n", "    pass\n"),
    ("valor y código cambiados", "        if any(s == S0315 for s, _ in obs):\n            J.cuenta(\"valor_distinto\"",
     "        if not any(s == S0315 for s, _ in obs):\n            J.cuenta(\"valor_distinto\""),
    ("convención en toda versión", "            J.nota(\"convencion\" if J.v25 else \"version\", \"PD1-7\"",
     "            J.nota(\"convencion\", \"PD1-7\""),
    ("nota aunque el código sea el mismo", "        if obs and v not in {c for _, c in obs}:\n", "        if obs:\n"),
    ("el campo entero", "    return _t(m, _f(m, pd1, 7), 1) if pd1 is not None else \"\"",
     "    return _f(m, pd1, 7) or \"\" if pd1 is not None else \"\""),
    ("PD1-6 en vez de PD1-7", "    return _t(m, _f(m, pd1, 7), 1) if pd1 is not None else \"\"",
     "    return _t(m, _f(m, pd1, 6), 1) if pd1 is not None else \"\""),
    ("la 0315 con F a N", "'F': ('http://terminology.hl7.org/CodeSystem/v2-0315', 'F')", "'F': ('http://terminology.hl7.org/CodeSystem/v2-0315', 'N')"),
    ("el paso de PD1-7 tras ACC y PDA", "        pd17 = _origen_pd17(m, obs)                                        # etapa 40",
     "        pd17 = _origen_pd17(m, [e for e in obs if not (e[\"tipo\"] == \"Observation\" and _origen_sin_mapa(m, e[\"r\"]))])  # etapa 40"),
]


def main(carpeta):
    base = os.path.abspath(carpeta).rstrip(os.sep) + "-mutantes"
    if os.path.isdir(base):
        shutil.rmtree(base)
    os.makedirs(base)
    orig = open(os.path.join(carpeta, "conversion.py"), encoding="utf-8", newline="").read()
    vivos = []
    for i, (nombre, antes, despues) in enumerate(MUTANTES, 1):
        assert orig.count(antes) == 1, "%s: %d veces" % (nombre, orig.count(antes))
        d = os.path.join(base, "m%02d" % i)
        shutil.copytree(carpeta, d, ignore=shutil.ignore_patterns("__pycache__", "bases_oru*", "*-mutantes"))
        open(os.path.join(d, "conversion.py"), "w", encoding="utf-8", newline="").write(orig.replace(antes, despues))
        r = subprocess.run([sys.executable, "prueba_conversion.py"], cwd=d, capture_output=True, text=True, timeout=600)
        caen = sorted({l.split()[1].rstrip(":") + (" (excepción)" if l.startswith("  EXCEPCIÓN ") else "")
                       for l in r.stdout.splitlines() if l.startswith("  MAL ") or l.startswith("  EXCEPCIÓN ")})
        print("%-40s %s %s" % (nombre, "MUERE" if r.returncode else "VIVE ", ", ".join(caen)), flush=True)
        if not r.returncode:
            vivos.append(nombre)
    print("mutantes: %d, vivos: %d %s" % (len(MUTANTES), len(vivos), vivos))
    return 1 if vivos else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
