#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 30 (iv/diseno-iv-fable.md §5): los controles del conductor antes de usarlo.
- Negativo: sobre una base de cada tipo (ADT_A01, ORU_R01, VXU_V04 y MDM_T02, del corpus), un mutante por clase y dos combinados.
  Cada mutante tiene que dar, frente a su base, exactamente los lugares inyectados, en su clase y con su «cuenta».
- Positivo: las bases dan lo mismo que su copia enmudecida (el enmudecer no fabrica errores) y dos corridas dan filas iguales.
Para el aparato si algo no cuadra: no se corre el corpus.
  python3 iv/control_iv.py <corpus> <trabajo vacío>"""
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import validar_iv as V  # noqa: E402

CORPUS, TRAB = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
assert not os.path.exists(TRAB) or not os.listdir(TRAB), "el trabajo tiene que estar vacío"
os.makedirs(TRAB, exist_ok=True)
BASES = {"adt": "lab/adt/A01-001.hl7", "oru": "lab/oru/ORU-B01.hl7", "vxu": "lab/vxu/VXU-B01.hl7", "mdm": "lab/mdm/MDM-B01.hl7"}


def leer(rel):
    return V.segmentos(open(os.path.join(CORPUS, rel), encoding="utf-8").read())


def idx(segs, nombre, n=1):
    vistos = 0
    for i, s in enumerate(segs, 1):
        if s.split("|", 1)[0] == nombre:
            vistos += 1
            if vistos == n:
                return i
    raise KeyError(nombre)


def escribir_corpus(d, piezas):
    """piezas: {id: segmentos} -> d/CORPUS-IV.json y d/c/<id>.hl7"""
    os.makedirs(os.path.join(d, "c"), exist_ok=True)
    filas = []
    for i, segs in piezas.items():
        open(os.path.join(d, "c", "%s.hl7" % i), "w", encoding="utf-8", newline="").write(V.unir(segs))
        filas.append({"id": i, "corpus": "control", "fichero": "c/%s.hl7" % i, "sha256": "-"})
    json.dump({"filas": filas}, open(os.path.join(d, "CORPUS-IV.json"), "w", encoding="utf-8"), ensure_ascii=False)


def filas_de(ruta):
    return {json.loads(l)["id"]: json.loads(l) for l in open(ruta, encoding="utf-8")}


# las bases, limpias: se enmudecen sus errores que cuentan hasta que no quede ninguno (diseño §5.1); lo limpiado se anota
b = {k: leer(v) for k, v in BASES.items()}
limpieza = {k: [] for k in b}
for vuelta in range(1, 6):
    d = os.path.join(TRAB, "limpieza-%d" % vuelta)
    escribir_corpus(d, {"base-" + k: s for k, s in b.items()})
    V.correr(d, os.path.join(d, "filas.jsonl"))
    R0 = filas_de(os.path.join(d, "filas.jsonl"))
    quedan = 0
    for k in b:
        v = next(iter(R0["base-" + k]["variantes"].values()))
        for p in [p for p in v["errores"] if p["cuenta"]]:
            quedan += 1
            if p["clase"] == "L":
                nuevo = V.leer(b[k], p["idx"], p["campo"], p["rep"])[:p.get("len_estandar") or 1]
                b[k] = V.editar(b[k], p["idx"], p["campo"], rep=p["rep"], valor=nuevo)
            elif p["clase"] == "T_HL7":
                b[k] = V.editar(b[k], p["idx"], p["campo"], p["rep"], p["comp"], p["sub"], valor="")
            elif p["clase"] == "R":
                b[k] = V.editar(b[k], p["idx"], p["campo"], valor="X")
            else:
                raise SystemExit("PARADA: la base %s tiene un error de clase %s que no se sabe limpiar" % (k, p["clase"]))
            limpieza[k].append({"vuelta": vuelta, "clase": p["clase"], "seg": p["seg"], "campo": p["campo"],
                                "tabla": p.get("tabla"), "valor": p.get("valor"), "motivo": p.get("motivo")})
    if not quedan:
        break
else:
    raise SystemExit("PARADA: las bases no quedan limpias en cinco vueltas")
A = b["adt"]
i_pid, i_pv1, i_evn = idx(A, "PID"), idx(A, "PV1"), idx(A, "EVN")
O = b["oru"]
i_obx = idx(O, "OBX")
quitar = lambda s, i: s[:i - 1] + s[i:]                                  # noqa: E731
poner = lambda s, i, nuevo: s[:i - 1] + [nuevo] + s[i - 1:]                # noqa: E731
largo = "M" * 25
MUTANTES = {      # id: (base, segmentos, esperado {(clase, seg, campo): cuenta}, notas)
    "N-E1": ("adt", quitar(A, i_pid), {("E", "PID", None): True}),
    "N-E2": ("adt", [s for s in A if not s.startswith("EVN")][:i_pid - 1] + [A[i_evn - 1]] + [s for s in A if not s.startswith("EVN")][i_pid - 1:],
             {("E", "*", None): True}),     # EVN detrás de PID: un error de estructura que cuenta (el lugar lo da IRIS)
    "N-E3": ("adt", A + ["QQQ|1"], {("E", "QQQ", None): True}),
    "N-Z1": ("adt", A + ["ZPI|1"], {("Z", "ZPI", None): False}),
    "N-Z2": ("adt", poner(A, i_pv1, "ZPI|1"), {("Z", "ZPI", None): True}),
    "N-R1": ("adt", V.editar(A, 1, 10, valor=""), {("R", "MSH", 10): True}),
    "N-R2": ("adt", V.editar(A, i_pid, 3, valor=""), {("R", "PID", 3): True}),
    "N-L1": ("adt", V.editar(A, 1, 10, valor=largo), {("L", "MSH", 10): True}),
    "N-T1": ("adt", V.editar(A, 1, 11, valor="Q"), {("T_HL7", "MSH", 11): True}),
    "N-T2": ("oru", V.editar(O, i_obx, 11, valor="Q"), {("T_HL7", "OBX", 11): True}),
    "N-T3": ("adt", V.editar(A, 1, 3, valor="LAB"), {("T_USR", "MSH", 3): False}),
    "N-T4": ("adt", V.editar(A, i_pid, 8, valor="Q"), {("T_USR", "PID", 8): False}),
    "N-N1": ("adt", V.editar(A, i_pid, 7, valor="19800101~19800102"), {("N|X", "PID", 7): None}),
    "N-U1": ("adt", V.editar(V.editar(A, i_pid, 5, valor="MUÑOZ^IÑAKI"), 1, 10, valor=""), {("R", "MSH", 10): True}),
    "N-M1": ("adt", V.editar(V.editar(V.editar(V.editar(A, 1, 10, valor=largo), i_pid, 3, valor=""), 1, 11, valor="Q"), 1, 3,
                             valor="LAB") + ["QQQ|1"],
             {("L", "MSH", 10): True, ("R", "PID", 3): True, ("T_HL7", "MSH", 11): True, ("T_USR", "MSH", 3): False,
              ("E", "QQQ", None): True}),
    "N-M2": ("adt", V.editar(V.editar(V.editar(A, 1, 10, valor=""), i_pid, 3, valor=""), i_pv1, 2, valor=""),
             {("R", "MSH", 10): True, ("R", "PID", 3): True, ("R", "PV1", 2): True}),
    "N-D1": ("adt", V.editar(V.editar(A, 1, 9, valor="ADT^A11^ADT_A01"), i_evn, 1, valor="A11"), {}),
    # otros separadores (MSH-2 «$~\&»): la base tal cual tiene que dar lo mismo que la base, y un defecto, su lugar
    "N-S1": ("adt", [A[0].replace("|^~\\&|", "|$~\\&|", 1).replace("ADT^A01^ADT_A01", "ADT$A01$ADT_A01")] +
             [s.replace("^", "$") for s in A[1:]], {}),
    "N-S2": ("adt", V.editar([A[0].replace("|^~\\&|", "|$~\\&|", 1).replace("ADT^A01^ADT_A01", "ADT$A01$ADT_A01")] +
                             [s.replace("^", "$") for s in A[1:]], i_pid, 3, valor=""), {("R", "PID", 3): True}),
}
piezas = {"base-" + k: s for k, s in b.items()}
piezas.update({mid: segs for mid, (_, segs, _) in MUTANTES.items()})
escribir_corpus(TRAB, piezas)
V.correr(TRAB, os.path.join(TRAB, "filas-1.jsonl"))
V.correr(TRAB, os.path.join(TRAB, "filas-2.jsonl"))
determinista = open(os.path.join(TRAB, "filas-1.jsonl"), "rb").read() == open(os.path.join(TRAB, "filas-2.jsonl"), "rb").read()
R = filas_de(os.path.join(TRAB, "filas-1.jsonl"))
print("limpieza de las bases (primer resultado sobre el corpus):")
for k, l in limpieza.items():
    print("  %s: %s" % (k, ["%s %s-%s %s=%r" % (x["clase"], x["seg"], x["campo"], x["tabla"] or "", x["valor"]) for x in l] or "nada"))


def lugares(fila, variante=None):
    v = fila["variantes"].get(variante) if variante else next(iter(fila["variantes"].values()))
    return {(p["clase"], p.get("seg"), p.get("campo") if p["clase"] not in ("E", "Z") else None): p["cuenta"] for p in v["errores"]}, v


fallos = []
print("bases:")
for k in BASES:
    lg, v = lugares(R["base-" + k])
    print("  %s: %s; cuentan %d; fines %s" % (k, sorted(lg), v["n_que_cuentan"], v["fines"]))
    if v["n_que_cuentan"]:
        fallos.append("base-%s tiene errores que cuentan: %s" % (k, [x for x, c in lg.items() if c]))
for mid, (base, _, esperado) in MUTANTES.items():
    fila = R[mid]
    lb, _ = lugares(R["base-" + base])
    if mid == "N-D1":
        ok = fila["doctype_discrepante"] and set(fila["variantes"]) == {"msh93", "esquema"}
        print("  %s: discrepante %s, variantes %s, estructuras %s / %s -> %s" % (
            mid, fila["doctype_discrepante"], sorted(fila["variantes"]), fila["doctype_msh93"], fila["doctype_esquema"], ok))
        if not ok:
            fallos.append(mid)
        continue
    lm, v = lugares(fila)
    nuevos = {x: c for x, c in lm.items() if x not in lb or (lb[x] != c)}
    if mid == "N-N1":
        print("  %s: %s (la clase N: %s)" % (mid, nuevos, "medida" if nuevos else "IRIS no dice nada: N no medible"))
        continue
    if mid == "N-S1":
        ok = lm == lb and fila["separadores"] == "|$~&" and set(fila["variantes"]) == {"msh93"}
    elif mid == "N-E2":
        ok = any(x[0] == "E" and c for x, c in nuevos.items()) and all(x[0] == "E" for x in nuevos)
    elif mid in ("N-T3",):
        ok = lm.get(("T_USR", "MSH", 3)) is False and not {x for x, c in nuevos.items() if c}
    else:
        ok = nuevos == esperado or (set(esperado) <= set(lm) and all(lm[x] == c for x, c in esperado.items())
                                    and not {x for x in nuevos if x not in esperado})
    if mid == "N-U1":
        ok = ok and fila["importado"]["ok"] and fila["no_ascii"]
    print("  %s: %s -> %s%s" % (mid, sorted(nuevos.items()), "bien" if ok else "MAL",
                                "" if not v["incompleto"] else " (incompleto: %s)" % v["fines"]))
    if not ok:
        fallos.append("%s: se esperaba %s y salió %s" % (mid, esperado, nuevos))
print("determinista: %s" % determinista)
if not determinista:
    fallos.append("dos corridas distintas")
json.dump({"fallos": fallos, "determinista": determinista, "limpieza_de_las_bases": limpieza,
           "mutantes": {mid: sorted(map(list, lugares(R[mid])[0].items()), key=str) for mid in MUTANTES}},
          open(os.path.join(TRAB, "CONTROL-IV.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("CONTROL: %s" % ("TODO BIEN" if not fallos else "MAL (%d): %s" % (len(fallos), "; ".join(fallos))))
sys.exit(1 if fallos else 0)
