#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Las reglas de cv/cv3_clases.py que han cambiado desde el estudio, sobre hallazgos sintéticos con los textos literales del juez; no
lee juicios ni evidencias.
- Etapa 38 (cl/diseno-cl-fable.md §2, con cl/decision-jev-cl.md, Q-CL-1 a): la regla de M-4 reconoce los dos textos con que el juez
  escribe el hallazgo de PL.9 de Microsoft, el de CV3 («falta la descripción») y el de CV4 («… contiene PL.9 … sin ser PL.9»), y las
  reglas vecinas siguen dando lo mismo. Que el cambio no mueve nada más en el estudio lo mide cl/reproducir_clases_cl.py.
- Etapa 39 (sc/diseno-sc-fable.md §3, con sc/decision-jev-sc.md): la Observation «recurso sin mapa» de ACC o PDA es M-28 también en
  el corpus del laboratorio, y MC-ORU-7 sigue limitado a los casos ms-ADT (Q-SC-1 a); y lo sin clase no para el aparato, pero lo
  cuenta en su salida (entradas) y avisa al final por la salida de error, con entradas y firmas (Q-SC-2 b), con tres pasadas de
  main() sobre juicios sintéticos y una del aparato como proceso aparte.

  python3 cv/prueba_cv3_clases.py        -> TODO BIEN si no hay ningún MAL"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
mal, n_ok = [], [0]
MS, LFH = "microsoft", "linuxforhealth"
TEXTO_CV3 = "Encounter.location 'UCI^3^1^HOSP^^^^^Box 3': falta la descripción 'Box 3' (PL.9)"
TEXTO_CV4 = "Encounter.location 'UCI^3^1^HOSP^^^^^Box 3': la descripción 'UCI--3--1--HOSP--Box 3' contiene PL.9 'Box 3' sin ser PL.9"
TEXTO_ACC = ("Observation urn:uuid:5d59332f-c5da-1745-9ec9-50b105e6bc30 de ACC (ACC-1 = '20140317'), que la hoja de ADT_A01 de la guía "
             "lista sin destino")
TEXTO_PDA = ("Observation urn:uuid:6b890de2-7da4-c603-b6eb-671dbf53ae5a de PDA (PDA-3/PDA-6 = 'Y', de la 0136), que la hoja de ADT_A01 "
             "de la guía lista sin destino")
TEXTO_ORU7 = "Observation urn:uuid:2d85a414-12ea-6ac0-dbbb-1474f657311e sin origen propio en el mensaje"


def mira(nombre, obtenido, esperado):
    if obtenido == esperado:
        n_ok[0] += 1
    else:
        print("  MAL %s: %r != %r" % (nombre, obtenido, esperado))
        mal.append(nombre)


def h(hecho, subtipo, q):
    return {"hecho": hecho, "clase": "fidelidad", "subtipo": subtipo, "que": [q]}


def correr_main(C, filas):
    """main() sobre un juicio sintético, en una carpeta temporal que se borra: (salida JSON, stdout, stderr)."""
    d = tempfile.mkdtemp(prefix="prueba-cv3-")
    try:
        j = os.path.join(d, "juicio.jsonl")
        with open(j, "w", encoding="utf-8") as g:
            for x in filas:
                g.write(json.dumps(x, ensure_ascii=False) + "\n")
        m = os.path.join(d, "minimos.json")
        json.dump({"pares": []}, open(m, "w", encoding="utf-8"))
        os.makedirs(os.path.join(d, "ev"))
        s = os.path.join(d, "clases.json")
        out, err, argv = io.StringIO(), io.StringIO(), sys.argv
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                C.main(j, m, os.path.join(d, "ev"), s)
        finally:
            sys.argv = argv
        return json.load(open(s, encoding="utf-8")), out.getvalue(), err.getvalue()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    import cv3_clases as C
    import juzgar_cv2 as J

    def clase(conv, hecho, subtipo, q, caso="A1-A01-03"):
        r = C.regla(conv, J.asignar(h(hecho, subtipo, q), q), q, caso)
        return r[0] if r else None
    # ---- etapa 38: la regla de M-4
    mira("P-CL-1 el texto de CV3 es M-4", clase(MS, "PV1-3", "dato_perdido", TEXTO_CV3), "M-4")
    mira("P-CL-2 el texto de CV4 es M-4", clase(MS, "PV1-3", "dato_perdido+valor_distinto", TEXTO_CV4), "M-4")
    mira("P-CL-3 los dos textos, al mismo mecanismo",
         (J.asignar(h("PV1-3", "dato_perdido", TEXTO_CV3), TEXTO_CV3),
          J.asignar(h("PV1-3", "dato_perdido+valor_distinto", TEXTO_CV4), TEXTO_CV4)), ("MC-ADT-3", "MC-ADT-3"))
    mira("P-CL-4 control: la cadena de Location es M-1",
         clase(MS, "PV1-11", "dato_perdido+valor_distinto", "Encounter.location 'QUIROF^1': la cadena de Location no conserva ['1']"), "M-1")
    mira("P-CL-4 control: status observado None es M-3",
         clase(MS, "PV1-3", "dato_perdido+valor_distinto", "Encounter.location 'PLANTA2^201^B^HOSP' status: esperado 'active', observado None",
               "A1-A11-25"), "M-3")
    mira("P-CL-4 control: status esperado es M-2",
         clase(MS, "PV1-11", "dato_perdido+valor_distinto", "Encounter.location 'QUIROF^1' status: esperado 'active', observado 'planned'"), "M-2")
    mira("P-CL-5 control: otro texto de Location no tiene clase",
         clase(MS, "PV1-3", "dato_perdido", "Encounter.location 'X': otra cosa"), None)
    mira("P-CL-6 control: el texto de CV4 en LinuxForHealth no es M-4",
         clase(LFH, "PV1-3", "dato_perdido+valor_distinto", TEXTO_CV4), "L-1")
    formas = {r[0]: type(r[3]).__name__ for r in C.R}
    mira("P-CL-7 cada texto de R es None, una cadena o una tupla de cadenas",
         all(r[3] is None or isinstance(r[3], str) or (isinstance(r[3], tuple) and all(isinstance(t, str) for t in r[3])) for r in C.R),
         True)
    mira("P-CL-7 solo M-4 lleva una tupla", sorted(k for k, v in formas.items() if v == "tuple"), ["M-4"])
    # ---- etapa 39 (Q-SC-1 a): la Observation sin mapa es M-28 también en el corpus del laboratorio
    mira("P-SC-1 la Observation de ACC sin mapa, en un ADT del laboratorio, es M-28",
         clase(MS, "ACC", "recurso_sin_mapa", TEXTO_ACC, "A01-004"), "M-28")
    mira("P-SC-1 la de PDA también", clase(MS, "PDA", "recurso_sin_mapa", TEXTO_PDA, "A02-007"), "M-28")
    mira("P-SC-2 control: en la muestra ms-ADT-A01-01 sigue siendo M-28", clase(MS, "ACC", "recurso_sin_mapa", TEXTO_ACC, "ms-ADT-A01-01"),
         "M-28")
    mira("P-SC-2 control: el mecanismo del texto es recurso_sin_mapa", J.asignar(h("ACC", "recurso_sin_mapa", TEXTO_ACC), TEXTO_ACC),
         "fuera:Observation|recurso_sin_mapa")
    mira("P-SC-3 MC-ORU-7 en la muestra ms-ADT (juez de antes) es M-28", clase(MS, "OBX", "recurso_inventado", TEXTO_ORU7, "ms-ADT-A01-01"),
         "M-28")
    mira("P-SC-3 MC-ORU-7 en ORU-B14 es M-22", clase(MS, "OBX", "recurso_inventado", TEXTO_ORU7, "ORU-B14"), "M-22")
    mira("P-SC-3 MC-ORU-7 en lfh-ORU es M-29", clase(MS, "OBX", "recurso_inventado", TEXTO_ORU7, "lfh-ORU-multiline-short"), "M-29")
    mira("P-SC-3 MC-ORU-7 en un ADT del laboratorio no tiene clase", clase(MS, "OBX", "recurso_inventado", TEXTO_ORU7, "A01-004"), None)
    mira("P-SC-3 MC-ORU-7 en un ORU del laboratorio que no es B14 no tiene clase",
         clase(MS, "OBX", "recurso_inventado", TEXTO_ORU7, "ORU-B09"), None)
    mira("P-SC-3 control: el texto de ACC en LinuxForHealth no tiene clase", clase(LFH, "ACC", "recurso_sin_mapa", TEXTO_ACC, "A01-004"), None)

    def forma_ok(c):
        return c is None or isinstance(c, (set, tuple))
    mira("P-SC-4 cada «casos» de R es None, conjunto, tupla o diccionario por mecanismo con las claves de sus mecanismos",
         all(forma_ok(r[4]) or (isinstance(r[4], dict) and set(r[4]) == set(r[2]) and all(forma_ok(v) for v in r[4].values())) for r in C.R),
         True)
    mira("P-SC-4 solo M-28 lleva el diccionario", sorted(r[0] for r in C.R if isinstance(r[4], dict)), ["M-28"])
    # ---- etapa 39 (Q-SC-2 b): el aviso
    fila = lambda caso, cuentan: {"conversor": MS, "corpus": "adt", "caso": caso, "cuentan": cuentan}  # noqa: E731
    con = [fila("A01-004", [h("ZZZ", "dato_perdido", "Patient.zzz 'x': nada que la regla conozca")]), fila("A01-005", [])]
    sin = [fila("A01-004", [h("ACC", "recurso_sin_mapa", TEXTO_ACC)])]
    res, out, err = correr_main(C, con)
    mira("P-SC-5 con algo sin clase, la salida JSON lo cuenta (n_sin_clase)", res.get("n_sin_clase"), 1)
    mira("P-SC-5 y sin_clase sigue como estaba (una firma)", len(res["sin_clase"]), 1)
    mira("P-SC-5 y avisa al final, por la salida de error, con lo que cuenta: entradas («que») y firmas",
         "AVISO cv3_clases: 1 entradas sin clase (1 firmas)" in err, True)
    mira("P-SC-5 y la frase no lleva la cuenta (los JSON publicados se comparan por su frase)", "n_sin_clase" in res["frase"], False)
    res, out, err = correr_main(C, sin)
    mira("P-SC-6 sin nada sin clase, n_sin_clase es 0 y no hay aviso", (res.get("n_sin_clase"), "AVISO" in err), (0, False))
    # ---- etapa 39, tras la revisión a ciegas: lo que cuenta el aviso, y el aparato como proceso
    dos = [fila("A01-004", [h("ZZZ", "dato_perdido", "Patient.zzz 'x': nada que la regla conozca")]),
           fila("A01-005", [h("ZZZ", "dato_perdido", "Patient.zzz 'y': nada que la regla conozca")])]
    res, out, err = correr_main(C, dos)
    mira("P-SC-7 dos entradas de la misma firma: n_sin_clase 2, una firma, y el aviso lo dice",
         (res.get("n_sin_clase"), len(res["sin_clase"]), "AVISO cv3_clases: 2 entradas sin clase (1 firmas)" in err), (2, 1, True))
    d = tempfile.mkdtemp(prefix="prueba-cv3-")
    try:
        j = os.path.join(d, "juicio.jsonl")
        with open(j, "w", encoding="utf-8") as g:
            for x in dos:
                g.write(json.dumps(x, ensure_ascii=False) + "\n")
        json.dump({"pares": []}, open(os.path.join(d, "minimos.json"), "w", encoding="utf-8"))
        os.makedirs(os.path.join(d, "ev"))
        import subprocess
        p = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "cv3_clases.py"), j,
                            os.path.join(d, "minimos.json"), os.path.join(d, "ev"), os.path.join(d, "clases.json")],
                           capture_output=True, text=True)
        ultima = [l for l in p.stderr.splitlines() if l.strip()][-1:] or [""]
        mira("P-SC-8 como proceso, con algo sin clase: sale con 0 y el aviso es la última línea de la salida de error",
             (p.returncode, ultima[0].startswith("AVISO cv3_clases: 2 entradas sin clase (1 firmas)")), (0, True))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print("PRUEBAS CV3 CLASES: %s (%d comprobaciones)" % ("TODO BIEN" if not mal else "%d MAL" % len(mal), n_ok[0]))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
