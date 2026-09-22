#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida los acuses con hl7apy, que es un tercero, y los cruza con la tabla.

LA PREGUNTA, sellada en PRE-VIA-D-V2.md con huella f7c897ac: un comprobador de
conformidad v2 de estanteria, ¿ve los dos fallos vivos que SI dejan acuse
recuperable?

    ENV_FHIR_CREDENCIAL_401 / ENV_FHIR_RUTA_404
        un fallo de ENTORNO contestado AR con ERR-3=102 "Data type error":
        le dice al emisor que el error es SUYO y que no reintente
    SEG_ORDEN_PV1_ANTES_PID
        ERR-3=101 "Required field missing" con el identificador PRESENTE en el
        mensaje; el codigo correcto seria el 100, Segment sequence error

P1 predice 0 de 2: los dos codigos son VALIDOS en la tabla 0357 y los segmentos
estan bien formados. Lo que esta mal es cual de los codigos validos se eligio.

DOS COSAS QUE HAY QUE DECIR DE LA MEDIDA, y van en la salida:

(1) EL MSH-7 DE LOS PAYLOADS ESTA ENMASCARADO. El arnes sustituye la hora por
    "<hora oculta>" a proposito, porque es un reloj absoluto y filtraba el orden
    de envio. Eso NO es del circuito: es del instrumento. Se sustituye por una
    marca valida antes de validar, o el unico error de todos los mensajes seria
    un artefacto mio y taparia lo que se busca. La sustitucion se declara.

(2) CONTROL NEGATIVO. Ademas de los limpios, se le pasa un acuse MUTILADO a
    proposito -sin MSA, que es obligatorio en un ACK-. Si tampoco protesta con
    ese, la herramienta no esta midiendo y la medida se descarta entera.

Uso: python3 via_d_v2_validar.py <directorio_de_acuses>
"""
import collections
import io
import json
import os
import re
import sys

HORA_FALSA = "20260920120000"     # sustituye al enmascarado del arnes
LIMPIOS = ("NINGUNA_",)

try:
    from hl7apy.parser import parse_message
    from hl7apy.validation import Validator
    from hl7apy.consts import VALIDATION_LEVEL
except ImportError:
    raise SystemExit("Falta hl7apy. Usar el python del venv del validador.")


def problemas(texto):
    """Errores y avisos de un mensaje, o el fallo de parseo si no se puede."""
    errores, avisos = [], []
    try:
        msg = parse_message(texto, validation_level=VALIDATION_LEVEL.TOLERANT)
    except Exception as e:                                       # noqa: BLE001
        return ["PARSEO: %s: %s" % (type(e).__name__, e)], []
    rep = "/tmp/hl7apy_reporte.txt"
    if os.path.exists(rep):
        os.remove(rep)
    try:
        Validator.validate(msg, report_file=rep)
    except Exception as e:                                       # noqa: BLE001
        errores.append("%s: %s" % (type(e).__name__, str(e)[:160]))
    if os.path.exists(rep):
        for ln in io.open(rep, encoding="utf-8", errors="replace"):
            ln = ln.strip()
            if not ln:
                continue
            (errores if "ERROR" in ln.upper() else avisos).append(ln[:160])
    return errores, avisos


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    base = sys.argv[1]
    idx = json.load(io.open(os.path.join(base, "indice.json"),
                            encoding="utf-8"))
    con = idx["con_acuse"]

    print("acuses a validar: %d   (casos sin acuse almacenado: %d)"
          % (len(con), len(idx["sin_acuse"])))
    for x in idx["sin_acuse"]:
        print("   SIN ACUSE: %-26s %s" % (x["operador"], x["caso"]))

    # --- control negativo, ANTES de mirar nada mas --------------------------
    crudo = io.open(con[0]["fichero"], encoding="utf-8", newline="").read()
    crudo = crudo.replace("<hora oculta>", HORA_FALSA)
    mutilado = "\r".join(l for l in crudo.split("\r")
                         if not l.startswith("MSA"))
    e_mut, a_mut = problemas(mutilado)
    print()
    print("CONTROL NEGATIVO — el mismo acuse sin su segmento MSA:")
    print("   errores: %d   avisos: %d" % (len(e_mut), len(a_mut)))
    for t in (e_mut + a_mut)[:3]:
        print("     %s" % t)
    if not e_mut and not a_mut:
        print()
        print("   LA HERRAMIENTA NO PROTESTA ANTE UN ACUSE ROTO A PROPOSITO.")
        print("   No esta midiendo. La medida se descarta: no se concluye nada.")
        return 1
    print("   -> protesta, luego discrimina algo. Se sigue.")

    # --- los acuses de verdad ----------------------------------------------
    print()
    print("=" * 96)
    print("POR CASO")
    print("=" * 96)
    print("%-14s %-26s %7s %7s  %s" % ("caso", "operador", "errores",
                                       "avisos", "ERR-3"))
    res = collections.defaultdict(lambda: collections.Counter())
    textos = collections.defaultdict(collections.Counter)
    for x in con:
        t = io.open(x["fichero"], encoding="utf-8", newline="").read()
        n_oculta = t.count("<hora oculta>")
        t = t.replace("<hora oculta>", HORA_FALSA)
        err, avi = problemas(t)
        op = x["operador"]
        res[op]["casos"] += 1
        res[op]["errores"] += len(err)
        res[op]["avisos"] += len(avi)
        res[op]["msh7_enmascarado"] += n_oculta
        for s in err + avi:
            textos[op][s] += 1
        cod = ""
        m = re.search(r"\|(\d{3})\^", x.get("err") or "")
        if m:
            cod = m.group(1)
        print("%-14s %-26s %7d %7d  %s"
              % (x["caso"][:14], op[:26], len(err), len(avi), cod or "-"))

    print()
    print("=" * 96)
    print("POR OPERADOR")
    print("=" * 96)
    print("%-28s %6s %8s %7s" % ("operador", "casos", "errores", "avisos"))
    for op in sorted(res, key=lambda o: (o.startswith(LIMPIOS), o)):
        r = res[op]
        print("%-28s %6d %8d %7d%s"
              % (op, r["casos"], r["errores"], r["avisos"],
                 "   <- LIMPIO" if op.startswith(LIMPIOS) else ""))
    print()
    print("(MSH-7 enmascarado por el arnes y sustituido por %s en %d mensajes:"
          % (HORA_FALSA, sum(res[o]["msh7_enmascarado"] for o in res)))
    print(" es del instrumento, no del circuito, y se declara.)")

    for op in sorted(textos):
        if textos[op]:
            print()
            print("  %s:" % op)
            for t, n in textos[op].most_common(4):
                print("     x%-3d %s" % (n, t))

    fallos = [o for o in res if not o.startswith(LIMPIOS)]
    limpios = [o for o in res if o.startswith(LIMPIOS)]

    def porcaso(ops):
        n = sum(res[o]["casos"] for o in ops) or 1
        return sum(res[o]["errores"] + res[o]["avisos"] for o in ops) / float(n)

    print()
    print("=" * 96)
    print("CONTRA LA PREDICCION SELLADA (PRE-VIA-D-V2.md, f7c897ac)")
    print("=" * 96)
    print("problemas POR CASO, acuses de fallo:  %.2f" % porcaso(fallos))
    print("problemas POR CASO, acuses limpios:   %.2f" % porcaso(limpios))
    print()
    if abs(porcaso(fallos) - porcaso(limpios)) < 0.5:
        print("P1 y P2 CONFIRMADAS: lo que encuentra es indistinguible entre")
        print("acuses de fallo y acuses limpios. El comprobador valida gramatica")
        print("y vocabulario; los dos fallos usan CODIGOS VALIDOS en la situacion")
        print("equivocada, y eso no lo ve.")
        print()
        print("P3 DISPARA: las DOS mitades de la via (d) son ciegas, y no por")
        print("mala suerte. Hay que escribirlo en el diseno.")
    else:
        print("P1 REFUTADA o matizada: hay diferencia. Mirar los textos de")
        print("arriba: tiene que ser una razon SUSTANTIVA sobre el codigo")
        print("elegido, no un aviso generico que varie por azar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
