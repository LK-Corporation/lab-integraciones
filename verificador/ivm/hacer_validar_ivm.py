#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 31, Q-MV-4 (ivm/decision-jev-qmv4.md): el conductor y el control de la etapa 30 con una regla más, escritos aparte para
que los de la 30 (publicados) no cambien:
- ivm/validar_ivm.py sale de iv/validar_iv.py. Si IRIS echa en falta un segmento justo donde hay uno que v2.5 no define (sin tabla
  de atributos en el texto de v2.5, y que no es Z), el que sobra es ese, y se quita como un segmento no esperado. Es la regla de
  los Z de la 30, para los segmentos de versiones posteriores (CH02.txt:934-935).
- ivm/control_ivm.py sale de iv/control_iv.py. Lleva un mutante más (N-V1: un ARV justo antes del PV1 de la base de ADT), que
  tiene que dar solo el error del ARV, sin campos sin evaluar. Su control negativo: con el conductor de la 30, el mismo mutante
  tiene que dar el error de PV1 y campos sin evaluar.
Es un cambio del aparato DESPUÉS de sellar, declarado en ivm/SELLO-IVM.txt y en el resultado. Afirma cada sustitución.
  python3 ivm/hacer_validar_ivm.py"""
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
IV = os.path.join(os.path.dirname(AQUI), "iv")

V_CAMBIOS = [
    ('"""Etapa 30: el conductor (iv/diseno-iv-fable.md §1-2; decisiones de Jev en iv/decision-jev-qiv.md).',
     '"""Etapa 31: el conductor de la etapa 30 con la regla de Q-MV-4 (ivm/decision-jev-qmv4.md), hecho con ivm/hacer_validar_ivm.py:\n'
     'si IRIS echa en falta un segmento justo donde hay uno que v2.5 no define, el que sobra es ese, y se quita. Lo que sigue es la\n'
     'cabecera de la 30.\n'
     'Etapa 30: el conductor (iv/diseno-iv-fable.md §1-2; decisiones de Jev en iv/decision-jev-qiv.md).'),
    ('import json\nimport os\nimport re\n', 'import glob\nimport json\nimport os\nimport re\n'),
    ('TOPE = 40\n',
     'TOPE = 40\n'
     '# etapa 31 (Q-MV-4): los segmentos que el texto de v2.5 define, por su tabla de atributos\n'
     'TXT25 = os.path.normpath(os.path.join(FASE, "..", "estandares", "hl7v2", "HL7_Messaging_v25", "txt"))\n'
     'SEG25 = set()\n'
     'for _f in sorted(glob.glob(os.path.join(TXT25, "*.txt"))):\n'
     '    for _l in open(_f, encoding="utf-8", errors="replace"):\n'
     '        _m = re.search(r"HL7 Attribute Table\\s*[-–]\\s*([A-Z][A-Z0-9]{2})\\b", _l)\n'
     '        if _m:\n'
     '            SEG25.add(_m.group(1))\n'
     'assert {"MSH", "PID", "PV1", "RXA", "TXA"} <= SEG25 and "ARV" not in SEG25, "no se leyeron las tablas de atributos de v2.5"\n'),
    ('                    p.update({"clase_iris": "Z", "seg_que_falta": p["seg"], "seg": t.segs[p["idx"] - 1].split("|", 1)[0],\n'
     '                              "al_final": False})\n',
     '                    p.update({"clase_iris": "Z", "seg_que_falta": p["seg"], "seg": t.segs[p["idx"] - 1].split("|", 1)[0],\n'
     '                              "al_final": False})\n'
     '                elif (p["clase_iris"] == "E" and p.get("tipo_e") == "requerido_ausente" and 1 < p["idx"] <= len(t.segs)\n'
     '                      and t.segs[p["idx"] - 1][:3] not in SEG25 and not t.segs[p["idx"] - 1].startswith("Z")):\n'
     '                    # etapa 31 (Q-MV-4): IRIS echa en falta un segmento justo donde hay uno que v2.5 no define; el que sobra\n'
     '                    # es ese, como con los Z, y se quita como un segmento no esperado\n'
     '                    p.update({"tipo_e": "no_esperado", "seg_que_falta": p["seg"], "seg": t.segs[p["idx"] - 1][:3]})\n'),
]

C_CAMBIOS = [
    ('"""Etapa 30 (iv/diseno-iv-fable.md §5): los controles del conductor antes de usarlo.',
     '"""Etapa 31: el control de la etapa 30 sobre ivm/validar_ivm.py, con el mutante N-V1 de la regla de Q-MV-4 y su control\n'
     'negativo con el conductor de la 30. Hecho con ivm/hacer_validar_ivm.py. Lo que sigue es la cabecera de la 30.\n'
     'Etapa 30 (iv/diseno-iv-fable.md §5): los controles del conductor antes de usarlo.'),
    ('import validar_iv as V  # noqa: E402', 'import validar_ivm as V  # noqa: E402'),
    ('                             [s.replace("^", "$") for s in A[1:]], i_pid, 3, valor=""), {("R", "PID", 3): True}),\n}\n',
     '                             [s.replace("^", "$") for s in A[1:]], i_pid, 3, valor=""), {("R", "PID", 3): True}),\n'
     '    # etapa 31 (Q-MV-4): un segmento que v2.5 no define, justo donde la estructura espera PV1\n'
     '    "N-V1": ("adt", A[:i_pv1 - 1] + ["ARV|1|A"] + A[i_pv1 - 1:], {("E", "ARV", None): True}),\n}\n'),
    ('    if mid == "N-U1":\n',
     '    if mid == "N-V1":\n'
     '        ok = nuevos == esperado and not v["campos_sin_evaluar"]\n'
     '    if mid == "N-U1":\n'),
    ('print("determinista: %s" % determinista)\n',
     '# el control negativo de la regla de Q-MV-4: con el conductor de la 30, N-V1 tiene que dar el fallo que la regla arregla\n'
     'import importlib.util  # noqa: E402\n'
     '_s = importlib.util.spec_from_file_location("validar_iv_30", os.path.join(os.path.dirname(AQUI), "iv", "validar_iv.py"))\n'
     'V30 = importlib.util.module_from_spec(_s)\n'
     '_s.loader.exec_module(V30)\n'
     'd30 = os.path.join(TRAB, "conductor-30")\n'
     'escribir_corpus(d30, {"base-adt": piezas["base-adt"], "N-V1": piezas["N-V1"]})\n'
     'V30.correr(d30, os.path.join(d30, "filas.jsonl"))\n'
     'R30 = filas_de(os.path.join(d30, "filas.jsonl"))\n'
     'l30, v30 = lugares(R30["N-V1"])\n'
     'lb30, _ = lugares(R30["base-adt"])\n'
     'n30 = {x: c for x, c in l30.items() if x not in lb30 or lb30[x] != c}\n'
     'ok30 = ("E", "PV1", None) in n30 and bool(v30["campos_sin_evaluar"])\n'
     'print("  N-V1 con el conductor de la 30 (control negativo): %s, sin evaluar %s -> %s" % (\n'
     '    sorted(n30.items()), v30["campos_sin_evaluar"], "bien" if ok30 else "MAL"))\n'
     'if not ok30:\n'
     '    fallos.append("N-V1 con el conductor de la 30 no da el fallo que arregla la regla: %s" % n30)\n'
     'print("determinista: %s" % determinista)\n'),
    ('json.dump({"fallos": fallos, "determinista": determinista, ',
     'json.dump({"control_negativo_N-V1_con_el_conductor_de_la_30": {"nuevos": sorted(map(list, n30.items()), key=str),\n'
     '                                                              "campos_sin_evaluar": v30["campos_sin_evaluar"], "bien": ok30},\n'
     '           "fallos": fallos, "determinista": determinista, '),
]


def hacer(origen, destino, cambios):
    t = open(origen, encoding="utf-8").read()
    for viejo, nuevo in cambios:
        assert t.count(viejo) == 1, "%s: no está (o no es único): %r" % (os.path.basename(origen), viejo[:70])
        t = t.replace(viejo, nuevo)
    open(destino, "w", encoding="utf-8").write(t)
    print("%s: escrito desde %s con %d cambios" % (os.path.relpath(destino, os.path.dirname(AQUI)),
                                                   os.path.relpath(origen, os.path.dirname(AQUI)), len(cambios)))


hacer(os.path.join(IV, "validar_iv.py"), os.path.join(AQUI, "validar_ivm.py"), V_CAMBIOS)
hacer(os.path.join(IV, "control_iv.py"), os.path.join(AQUI, "control_ivm.py"), C_CAMBIOS)
