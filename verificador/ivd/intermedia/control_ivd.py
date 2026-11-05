#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 32 (ANTES-ETAPA-IVDECLARADA.md, «Cómo» 2): los controles del aparato de la 32 antes de usarlo, con la forma del de la 31
(ivm/control_ivm.py).
- Bases: la de ADT y la de ORU del laboratorio (las de la 30) con MSH-12 cambiado a 2.5.1, 2.6 y 2.8; limpias como en la 30 (sus
  errores que cuentan se enmudecen, con lo limpiado anotado).
- Mutantes de la 31 en cada versión: cada uno tiene que dar, frente a su base, sus lugares, en su clase y con su «cuenta». Sin
  texto (2.6 y 2.8), N-T1 y N-T2 dan T_HL7 que cuenta para la lectura con el motivo de Q-VD-1, y N-T4 se mide (depende de si el
  esquema de IRIS trae la tabla 0001 con valores).
- N-V1, en cada versión, con un segmento que esa versión no define justo donde la estructura espera PV1 (ARV en la 2.5.1, PRT en
  la 2.6, QQQ en la 2.8): solo el error de ese segmento, sin campos sin evaluar. N-V2, en la 2.6: ARV, que la 2.6 sí define, no
  da ningún error de estructura.
- N-C1, en la 2.8: MSH-22 y MSH-24 con valor (campos que define la 2.8 y no la 2.5) no da nada que cuente ni de repeticiones.
  Su control negativo: con el conductor de la 31 (contra v2.5), el mismo mutante da el error de más campos.
- Tras la revisión a ciegas (Q-VD-3c): N-C2, en cada versión, con MSH-30 (que ninguna versión define), da solo el error de más
  campos, y la lectura lo deja sin decidir. N-C3, en la 2.5.1, con OBX-23 (que define la 2.5.1 y no la 2.5), no da nada; con el
  conductor de la 31, da el error de más campos.
- Las dos lecturas, sobre las filas del control: las bases, válidas; los mutantes, con el veredicto que les toca. Un segmento que
  la versión no define (N-E3 y N-V1) va aparte y la muestra sale válida, como en la 31 (Q-MV-2 y Q-MV-4).
- Dos corridas de cada conductor, iguales.
Para el aparato si algo no cuadra: no se corre el corpus.
  python3 ivd/control_ivd.py <corpus de la 30> <trabajo vacío>"""
import importlib.util
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import validar_ivd251 as V251  # noqa: E402
import validar_ivdst as VST  # noqa: E402

CORPUS, TRAB = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
assert not os.path.exists(TRAB) or not os.listdir(TRAB), "el trabajo tiene que estar vacío"
os.makedirs(TRAB, exist_ok=True)
VISTA = os.path.normpath(os.path.join(FASE, "..", "estandares", "hl7v2", "HL7_Messaging_v251", "vista_v25"))
BASES = {"adt": "lab/adt/A01-001.hl7", "oru": "lab/oru/ORU-B01.hl7"}
GRUPOS = {"251": (V251, ["2.5.1"]), "st": (VST, ["2.6", "2.8"])}
quitar = lambda s, i: s[:i - 1] + s[i:]                                  # noqa: E731
poner = lambda s, i, nuevo: s[:i - 1] + [nuevo] + s[i - 1:]                # noqa: E731


def idx(segs, nombre):
    for i, s in enumerate(segs, 1):
        if s.split("|", 1)[0] == nombre:
            return i
    raise KeyError(nombre)


def escribir_corpus(d, piezas):
    """piezas: {id: segmentos} -> d/CORPUS-IV.json y d/<id>; el id es el fichero (la lectura abre <corpus>/<id>)."""
    os.makedirs(d, exist_ok=True)
    filas = []
    for i, segs in piezas.items():
        open(os.path.join(d, i), "w", encoding="utf-8", newline="").write(V251.unir(segs))
        filas.append({"id": i, "corpus": "control", "fichero": i, "sha256": "-"})
    json.dump({"filas": filas}, open(os.path.join(d, "CORPUS-IV.json"), "w", encoding="utf-8"), ensure_ascii=False)


def filas_de(ruta):
    return {json.loads(l)["id"]: json.loads(l) for l in open(ruta, encoding="utf-8")}


def lugares(fila):
    v = next(iter(fila["variantes"].values()))
    return {(p["clase"], p.get("seg"), p.get("campo") if p["clase"] not in ("E", "Z", "X") else None): p["cuenta"]
            for p in v["errores"]}, v


crudas = {k: V251.segmentos(open(os.path.join(CORPUS, r), encoding="utf-8").read()) for k, r in BASES.items()}
fallos, informe = [], {"limpieza": {}, "mutantes": {}, "lecturas": {}, "deterministas": {}}
filas_finales = {}
for g, (V, vers) in GRUPOS.items():
    # las bases de cada versión, limpias
    b = {"%s-base-%s" % (ver, k): V.editar(s, 1, 12, valor=ver) for ver in vers for k, s in crudas.items()}
    limpieza = {k: [] for k in b}
    for vuelta in range(1, 6):
        d = os.path.join(TRAB, "limpieza-%s-%d" % (g, vuelta))
        escribir_corpus(d, b)
        V.correr(d, os.path.join(d, "filas.jsonl"))
        R0, quedan = filas_de(os.path.join(d, "filas.jsonl")), 0
        for k in b:
            v = next(iter(R0[k]["variantes"].values()))
            for p in [p for p in v["errores"] if p["cuenta"]]:
                quedan += 1
                if p["clase"] == "L":
                    b[k] = V.editar(b[k], p["idx"], p["campo"], rep=p["rep"],
                                    valor=V.leer(b[k], p["idx"], p["campo"], p["rep"])[:p.get("len_estandar") or 1])
                elif p["clase"] == "T_HL7":
                    b[k] = V.editar(b[k], p["idx"], p["campo"], p["rep"], p["comp"], p["sub"], valor="")
                elif p["clase"] == "R":
                    b[k] = V.editar(b[k], p["idx"], p["campo"], valor="X")
                else:
                    raise SystemExit("PARADA: la base %s tiene un error de clase %s que no se sabe limpiar: %s" % (
                        k, p["clase"], p.get("crudo")))
                limpieza[k].append({"vuelta": vuelta, "clase": p["clase"], "seg": p["seg"], "campo": p.get("campo"),
                                    "tabla": p.get("tabla"), "valor": p.get("valor"), "motivo": p.get("motivo")})
        if not quedan:
            break
    else:
        raise SystemExit("PARADA: las bases del grupo %s no quedan limpias en cinco vueltas" % g)
    informe["limpieza"].update(limpieza)
    # los mutantes de cada versión
    mut = {}
    for ver in vers:
        A, O = b["%s-base-adt" % ver], b["%s-base-oru" % ver]
        i_pid, i_pv1, i_obx = idx(A, "PID"), idx(A, "PV1"), idx(O, "OBX")
        otro = {"2.5.1": "ARV|1|A", "2.6": "PRT|1", "2.8": "QQQ|1"}[ver]
        m = {
            "N-E1": ("adt", quitar(A, i_pid), {("E", "PID", None): True}),
            "N-E3": ("adt", A + ["QQQ|1"], {("E", "QQQ", None): True}),
            "N-Z1": ("adt", A + ["ZPI|1"], {("Z", "ZPI", None): False}),
            "N-Z2": ("adt", poner(A, i_pv1, "ZPI|1"), {("Z", "ZPI", None): True}),
            "N-R1": ("adt", V.editar(A, 1, 10, valor=""), {("R", "MSH", 10): True}),
            "N-R2": ("adt", V.editar(A, i_pid, 3, valor=""), {("R", "PID", 3): True}),
            "N-L1": ("adt", V.editar(A, 1, 10, valor="M" * 250), {("L", "MSH", 10): True}),
            "N-T1": ("adt", V.editar(A, 1, 11, valor="Q"), {("T_HL7", "MSH", 11): True}),
            "N-T2": ("oru", V.editar(O, i_obx, 11, valor="Q"), {("T_HL7", "OBX", 11): True}),
            "N-T4": ("adt", V.editar(A, i_pid, 8, valor="Q"), "medido"),
            "N-U1": ("adt", V.editar(V.editar(A, i_pid, 5, valor="MUÑOZ^IÑAKI"), 1, 10, valor=""), {("R", "MSH", 10): True}),
            "N-M2": ("adt", V.editar(V.editar(V.editar(A, 1, 10, valor=""), i_pid, 3, valor=""), i_pv1, 2, valor=""),
                     {("R", "MSH", 10): True, ("R", "PID", 3): True, ("R", "PV1", 2): True}),
            "N-V1": ("adt", poner(A, i_pv1, otro), {("E", otro[:3], None): True}),
            # tras la revisión a ciegas (Q-VD-3c): MSH-30, que ninguna versión define: solo el error de más campos, y la lectura,
            # sin decidir
            "N-C2": ("adt", V.editar(A, 1, 30, valor="X"), "campos_de_mas"),
        }
        if ver == "2.5.1":
            # tras la revisión a ciegas: OBX-23, que define la 2.5.1 y no la 2.5: nada; con el conductor de la 31, más campos
            m["N-C3"] = ("oru", V.editar(O, i_obx, 23, valor="ORG"), "nada_que_cuente_ni_repeticiones")
        if ver == "2.6":
            m["N-V2"] = ("adt", poner(A, i_pv1, "ARV|1|A"), "sin_error_de_estructura")
        if ver == "2.8":
            m["N-C1"] = ("adt", V.editar(V.editar(A, 1, 22, valor="ORG"), 1, 24, valor="RED"), "nada_que_cuente_ni_repeticiones")
        for mid, x in m.items():
            mut["%s-%s" % (ver, mid)] = (ver,) + x
    piezas = dict(b)
    piezas.update({mid: x[2] for mid, x in mut.items()})
    d = os.path.join(TRAB, "c" + g)
    escribir_corpus(d, piezas)
    V.correr(d, os.path.join(TRAB, "filas-%s-1.jsonl" % g))
    V.correr(d, os.path.join(TRAB, "filas-%s-2.jsonl" % g))
    det = open(os.path.join(TRAB, "filas-%s-1.jsonl" % g), "rb").read() == open(os.path.join(TRAB, "filas-%s-2.jsonl" % g), "rb").read()
    informe["deterministas"][g] = det
    if not det:
        fallos.append("%s: dos corridas distintas" % g)
    R = filas_de(os.path.join(TRAB, "filas-%s-1.jsonl" % g))
    filas_finales[g] = R
    print("grupo %s:" % g)
    for k in b:
        lg, v = lugares(R[k])
        print("  %s: %s; cuentan %d; fines %s" % (k, sorted(lg.items()), v["n_que_cuentan"], v["fines"]))
        if v["n_que_cuentan"]:
            fallos.append("%s tiene errores que cuentan" % k)
        if R[k]["version"] != k.split("-")[0] or not (R[k]["doctype_msh93"] or "").startswith(k.split("-")[0] + ":"):
            fallos.append("%s: versión %s, estructura %s" % (k, R[k]["version"], R[k]["doctype_msh93"]))
    for mid, (ver, base, _, esperado) in mut.items():
        fila = R[mid]
        lb, _ = lugares(R["%s-base-%s" % (ver, base)])
        lm, v = lugares(fila)
        nuevos = {x: c for x, c in lm.items() if x not in lb or lb[x] != c}
        corto = mid.split("-", 1)[1]
        if esperado == "medido":
            ok = nuevos in ({("T_USR", "PID", 8): False}, {("T_HL7", "PID", 8): True})
            if ver == "2.5.1":
                ok = nuevos == {("T_USR", "PID", 8): False}
        elif esperado == "sin_error_de_estructura":
            ok = not any(x[0] in ("E", "Z") for x in nuevos)
        elif esperado == "nada_que_cuente_ni_repeticiones":
            ok = not any(x[0] == "X" for x in nuevos) and not any(nuevos.values())
        elif esperado == "campos_de_mas":
            ok = set(nuevos) == {("X", None, None)} and not any(nuevos.values())
        else:
            ok = nuevos == esperado or (set(esperado) <= set(lm) and all(lm[x] == c for x, c in esperado.items())
                                        and not {x for x in nuevos if x not in esperado})
            if corto == "N-V1":
                ok = nuevos == esperado and not v["campos_sin_evaluar"]
            if corto == "N-U1":
                ok = ok and fila["importado"]["ok"] and fila["no_ascii"]
            if g == "st" and corto in ("N-T1", "N-T2"):
                ok = ok and all("Q-VD-1" in (p.get("motivo") or "") for p in v["errores"] if p["clase"] == "T_HL7")
        informe["mutantes"][mid] = {"nuevos": sorted(map(list, nuevos.items()), key=str), "bien": ok}
        print("  %s: %s -> %s%s" % (mid, sorted(nuevos.items()), "bien" if ok else "MAL",
                                    "" if not v["incompleto"] else " (incompleto: %s)" % v["fines"]))
        if not ok:
            fallos.append("%s: se esperaba %s y salió %s" % (mid, esperado, nuevos))
    # la lectura del grupo sobre las filas del control
    dl = os.path.join(TRAB, "l" + g)
    os.makedirs(dl)
    if g == "251":
        cmd = [sys.executable, os.path.join(AQUI, "lectura_ivd251.py"), os.path.join(TRAB, "filas-251-1.jsonl"), VISTA,
               os.path.join(dl, "LECTURAS-IVD251.json"), d]
        ver_f = os.path.join(dl, "VEREDICTOS-IVD251.jsonl")
    else:
        cmd = [sys.executable, os.path.join(AQUI, "lectura_ivdst.py"), os.path.join(TRAB, "filas-st-1.jsonl"),
               os.path.join(dl, "LECTURAS-IVDST.json")]
        ver_f = os.path.join(dl, "VEREDICTOS-IVDST.jsonl")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        fallos.append("la lectura del grupo %s no corre: %s" % (g, r.stderr[-400:]))
        continue
    REG = {json.loads(l)["id"]: json.loads(l) for l in open(ver_f, encoding="utf-8")}
    VER = {k: x["veredicto_sostenido"] for k, x in REG.items()}
    for k, s in sorted(VER.items()):
        corto = k.split("-", 1)[1]
        if corto in ("N-E3", "N-V1"):                  # un segmento que la versión no define: aparte (Q-MV-2 y Q-MV-4)
            seg = "QQQ" if corto == "N-E3" else {"2.5.1": "ARV", "2.6": "PRT", "2.8": "QQQ"}[k.split("-", 1)[0]]
            bien = s == "valido" and any(("|E|%s|" % seg) in ("|" + a["lugar"]) for a in REG[k]["aparte"])
            informe["lecturas"][k] = {"veredicto": s, "aparte": [a["lugar"] for a in REG[k]["aparte"]], "bien": bien}
            if not bien:
                fallos.append("lectura %s: %s, aparte %s; se esperaba válido con %s aparte" % (
                    k, s, [a["lugar"] for a in REG[k]["aparte"]], seg))
            continue
        if corto == "N-C2":                            # Q-VD-3c: sin decidir, por los campos de más de MSH
            bien = s == "no_decidible" and any(("|C|MSH|" in ("|" + e["lugar"])) for e in REG[k]["no_decidibles"])
            informe["lecturas"][k] = {"veredicto": s, "bien": bien}
            if not bien:
                fallos.append("lectura %s: %s, se esperaba sin decidir por los campos de más de MSH" % (k, s))
            continue
        if corto.startswith("base-") or corto in ("N-Z1", "N-C1", "N-C3"):
            esp = {"valido"}
        elif corto in ("N-T1", "N-T2"):
            esp = {"no_decidible"}
        elif corto == "N-T4":
            esp = {"valido"} if g == "251" else {"valido", "no_decidible"}
        elif corto == "N-V2":
            esp = {"valido", "invalido", "no_decidible"}          # solo se mira la estructura, arriba
        else:
            esp = {"invalido"}
        informe["lecturas"][k] = {"veredicto": s, "bien": s in esp}
        if s not in esp:
            fallos.append("lectura %s: %s, se esperaba %s" % (k, s, sorted(esp)))
    print("  lectura %s: %s" % (g, sorted(VER.items())))
# el control negativo de la versión: N-C1 de la 2.8 con el conductor de la 31, contra v2.5
_s = importlib.util.spec_from_file_location("validar_ivm_31", os.path.join(FASE, "ivm", "validar_ivm.py"))
V31 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(V31)
d31 = os.path.join(TRAB, "conductor-31")
leer_c = lambda g, i: V251.segmentos(open(os.path.join(TRAB, g, i), encoding="utf-8").read())   # noqa: E731
escribir_corpus(d31, {"base-28": leer_c("cst", "2.8-base-adt"), "N-C1": leer_c("cst", "2.8-N-C1"),
                      "base-251": leer_c("c251", "2.5.1-base-oru"), "N-C3": leer_c("c251", "2.5.1-N-C3")})
V31.correr(d31, os.path.join(d31, "filas.jsonl"))
R31 = filas_de(os.path.join(d31, "filas.jsonl"))
for mid, base, nombre in (("N-C1", "base-28", "negativo_N-C1_con_el_conductor_de_la_31"),
                          ("N-C3", "base-251", "negativo_N-C3_con_el_conductor_de_la_31")):
    l31, _ = lugares(R31[mid])
    lb31, _ = lugares(R31[base])
    n31 = {x: c for x, c in l31.items() if x not in lb31 or lb31[x] != c}
    crudo31 = [p.get("crudo") for p in next(iter(R31[mid]["variantes"].values()))["errores"] if p["clase"] == "X"]
    ok31 = any(x[0] == "X" for x in n31) and any("more fields" in (c or "") for c in crudo31)
    informe[nombre] = {"nuevos": sorted(map(list, n31.items()), key=str), "crudo": crudo31, "bien": ok31}
    print("  %s con el conductor de la 31 (control negativo): %s %s -> %s" % (
        mid, sorted(n31.items()), [c[:90] for c in crudo31], "bien" if ok31 else "MAL"))
    if not ok31:
        fallos.append("%s con el conductor de la 31 no da el error de más campos: %s" % (mid, n31))
informe["fallos"] = fallos
json.dump(informe, open(os.path.join(TRAB, "CONTROL-IVD.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1,
          sort_keys=True)
print("CONTROL: %s" % ("TODO BIEN" if not fallos else "FALLOS:\n  " + "\n  ".join(fallos)))
