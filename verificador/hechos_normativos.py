#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hechos de tabla, comprobados por código, para los adjudicadores (REGLA-hechos-normativos.md).

QUÉ HACE. A partir de la `estructura` de un bundle congelado (el bundle no se toca) escribe un
bloque de hechos MECÁNICOS: qué valor trae cada campo codificado, si está en su tabla de HL7 v2.5 (la
versión del contrato), qué destino le da el mapeo oficial HL7 v2-to-FHIR y qué salió en el canónico.

QUÉ NO HACE. No da veredictos: no dice si algo es un fallo. Eso lo juzga el adjudicador con la
rúbrica. Si un campo no se puede leer con seguridad, no se afirma nada de él.

FUENTES.
- Tablas 0001, 0008, 0357 y 0516: HL7 v2.5, literal (medida/encargo_medida.md §8; extracto en
  medida/norma_tablas_v25.md).
- Mapeo 0001 -> AdministrativeGender: ConceptMap oficial «table-hl70001-to-administrative-gender» de
  la guía HL7 Version 2 to FHIR v1.0.0 (build.fhir.org/ig/HL7/v2-to-fhir), leído el 26-sep-2026.

Uso: python3 hechos_normativos.py --autoprueba
     python3 hechos_normativos.py <bundles.jsonl> [instancia]   (imprime los hechos)
     python3 hechos_normativos.py --censo <bundles.jsonl> ...     (valores vistos, sin excepciones)
"""
import collections
import json
import re
import sys

import mapeador_referencia as MR

VERSION = "2.5"
T0001 = {"F": "Female", "M": "Male", "O": "Other", "U": "Unknown", "A": "Ambiguous", "N": "Not applicable"}
MAPEO_0001 = {"F": "female", "M": "male", "O": "other", "U": "unknown", "A": "other", "N": "other"}
T0008 = {"AA": "Application Accept", "AE": "Application Error", "AR": "Application Reject",
         "CA": "Commit Accept", "CE": "Commit Error", "CR": "Commit Reject"}
T0357 = {"0": "Message accepted", "100": "Segment sequence error", "101": "Required field missing",
         "102": "Data type error", "103": "Table value not found", "200": "Unsupported message type",
         "201": "Unsupported event code", "202": "Unsupported processing id", "203": "Unsupported version id",
         "204": "Unknown key identifier", "205": "Duplicate key identifier", "206": "Application record locked",
         "207": "Application internal error"}
T0516 = {"W": "Warning", "I": "Information", "E": "Error"}

CABECERA = ("HECHOS DE TABLA, COMPROBADOS POR CÓDIGO (tablas de HL7 v2.5, la versión de referencia; el sitio acepta "
            "MSH-12 2.x desde 2.4 [S19]; "
            "mapeo oficial HL7 v2-to-FHIR para el sexo)\n"
            "Son comprobaciones mecánicas y exactas: dicen qué valor hay, si está en su tabla y qué salió. "
            "No dicen si hay un fallo: eso lo juzgas tú con la rúbrica.")


def _mensajes(texto, registros=None):
    """Mensajes del cable: lista de listas de segmentos (cadenas). DV-H1: una sola implementación, la de
    mapeador_referencia.mensajes (por marcos MLLP [S31]; bytes <0xNN> decodificados [S9]; MSH de al menos 8 caracteres).
    Los registros de decodificación van a `registros`."""
    ms = MR.mensajes(texto)
    if registros is not None:
        for m in ms:
            registros.extend(m.descodificados)
    return [m.segs for m in ms]


def _separadores(msh):
    if len(msh) < 8 or not msh.startswith("MSH"):
        return None
    return msh[3], msh[4]          # campo, componente


def _campo(seg, n, sep):
    """Campo n (1-based, numeración HL7) de un segmento; en MSH, MSH-1 es el propio separador."""
    partes = seg.split(sep)
    i = n - 1 if seg.startswith("MSH") else n
    return partes[i] if 0 <= i < len(partes) else None


def _uno(x, comp):
    return x.split(comp)[0] if x is not None else None


def _hecho_version(v):
    """[S19] el hecho de MSH-12: dentro o fuera de lo que el sitio acepta; las tablas del bloque son de v2.5."""
    if not v:
        return "MSH-12 vacío o ausente."
    if MR.version_id(v) is None:
        return "MSH-12 declara la versión %r: no tiene la forma N.N[.N] de la tabla 0104; el sitio acepta 2.x desde 2.4 [S19]." % v
    if not MR.version_aceptada(v):
        return "MSH-12 declara la versión %r: anterior a 2.4 o no es 2.x; el sitio no la acepta [S19]." % v
    return ("MSH-12 declara la versión %r: está dentro de lo que el sitio acepta (2.x desde 2.4 [S19]); las tablas de este "
            "bloque son de v2.5.%s" % (v, " Es la versión de referencia." if v == VERSION else ""))


def _hecho_sexo(valor, canonicos, version=None):
    can = ", ".join(repr(c) for c in canonicos) if canonicos else "no hubo mensaje canónico"
    if valor is None or valor == "":
        return ("PID-8 vacío o ausente: no hay valor que buscar en la tabla 0001. Gender en el canónico: %s." % can)
    if valor in T0001:
        dest = MAPEO_0001[valor]
        coinc = ""
        if canonicos:
            coinc = " (coincide con el mapeo oficial)" if all(c == dest for c in canonicos) else " (NO coincide con el mapeo oficial)"
        return ("PID-8 = %r: SÍ está en la tabla 0001 de v2.5 (%s). Destino según el mapeo oficial: %s. "
                "Gender en el canónico: %s%s." % (valor, T0001[valor], dest, can, coinc))
    extra = ""
    if valor.upper() in T0001:
        extra = (" En mayúscula, %r sí está (%s; destino oficial %s): los códigos de la tabla van en mayúscula."
                 % (valor.upper(), T0001[valor.upper()], MAPEO_0001[valor.upper()]))
    s22 = ""
    if not extra and MR.posterior_a_25(version or ""):
        s22 = " En un mensaje %s (posterior a 2.5) puede ser legal en su versión: el sitio lo tolera [S22]." % version
    return ("PID-8 = %r: NO está en la tabla 0001 de v2.5 (valores: %s). El mapeo oficial no le da destino.%s "
            "Gender en el canónico: %s.%s" % (valor, ", ".join(T0001), extra, can, s22))


def _hecho_tabla(nombre, tabla_n, tabla, valor):
    if valor is None or valor == "":
        return "%s vacío o ausente." % nombre
    if valor in tabla:
        return "%s = %r: SÍ está en la tabla %s de v2.5 (%s)." % (nombre, valor, tabla_n, tabla[valor])
    return "%s = %r: NO está en la tabla %s de v2.5 (valores: %s)." % (nombre, valor, tabla_n, ", ".join(tabla))


def hechos(e):
    """-> lista de hechos (cadenas) para la estructura `e` de un bundle."""
    out = []
    canonicos = [s["canonico"].get("Gender") for s in e.get("sesiones") or [] if isinstance(s.get("canonico"), dict)]
    regs = []
    msgs = _mensajes(e.get("mensaje"), regs)
    dec = [r for r in regs if r["via"] in ("utf-8", "latin-1")]                     # [S9]; control/lf son S10
    if dec:
        out.append("El cable trae bytes no decodificables marcados <0xNN> (%s): se leen como latin-1 [S9]." % ", ".join(
            "%s en %s-%s" % (r["bytes"], r["seg"], r["n"]) for r in dec))
    if not msgs:
        out.append("No se pudo leer por código ningún mensaje del cable: no se afirma nada de sus campos.")
    else:                                                                              # [S31] marcos sin MSH
        tr = MR.trama(e.get("mensaje"))
        for n in tr["sin_msh"]:
            segs = tr["marcos"][n - 1]["segmentos"]
            out.append("El cable trae %d marcos MLLP; el marco %d no tiene MSH (segmentos: %s): no es un mensaje HL7 y no se "
                       "afirma nada de sus campos [S31]." % (len(tr["marcos"]), n,
                                                            " ".join(s if re.fullmatch(r"[A-Z][A-Z0-9]{2}", s) else "?" for s in segs)))
        for m in MR.mensajes(e.get("mensaje")):                                        # [E2 §2.5.4] segmentos tras LF
            oc = MR.segmentos_ocultos(m.segs, m.f)
            if oc:
                out.append("El marco %s trae los segmentos %s tras un byte de control que no es CR (%s) en vez del terminador CR "
                           "[E2 §2.5.4]: por código no se leen como segmentos y no se afirma nada de sus campos."
                           % (m.marco, " ".join(n for n, _ in oc), "/".join(sorted({c for _, c in oc}))))
    for k, segs in enumerate(msgs, 1):
        pre = "Mensaje %d de %d del cable. " % (k, len(msgs)) if len(msgs) > 1 else ""
        sp = _separadores(segs[0])
        if not sp:
            out.append(pre + "Su MSH no se puede leer por código: no se afirma nada de sus campos.")
            continue
        f, c = sp
        v = _campo(segs[0], 12, f)
        ver = _uno(v, c) or ""
        out.append(pre + _hecho_version(ver))
        pids = [s for s in segs if s.startswith("PID" + f)]
        if not pids:
            out.append(pre + "No hay segmento PID.")
        for j, pid in enumerate(pids, 1):
            p2 = "Segmento PID %d de %d. " % (j, len(pids)) if len(pids) > 1 else ""
            canonicos_msg = [canonicos[k - 1]] if k <= len(canonicos) else []
            out.append(pre + p2 + _hecho_sexo(_campo(pid, 8, f), canonicos_msg, ver))
    ack = e.get("ack")
    if not ack:
        out.append("El emisor no recibió ACK: no hay MSA ni ERR que comprobar.")
    else:
        am = _mensajes(ack)
        sp = _separadores(am[0][0]) if am else None
        if not sp:
            out.append("El ACK no se puede leer por código: no se afirma nada de él.")
        else:
            f, c = sp
            segs = am[0]
            msa = [s for s in segs if s.startswith("MSA" + f)]
            for s in msa:
                out.append(_hecho_tabla("MSA-1 del ACK", "0008", T0008, _campo(s, 1, f)))
            errs = [s for s in segs if s.startswith("ERR" + f)]
            if not errs:
                out.append("El ACK no lleva segmento ERR.")
            for s in errs:
                out.append(_hecho_tabla("ERR-3 del ACK", "0357", T0357, _uno(_campo(s, 3, f), c)))
                out.append(_hecho_tabla("ERR-4 del ACK", "0516", T0516, _uno(_campo(s, 4, f), c)))
    return out


def msa1(e):
    """MSA-1 del primer MSA del acuse, leído por código; None si no hay acuse legible o no hay MSA."""
    am = _mensajes(e.get("ack") or "")
    sp = _separadores(am[0][0]) if am else None
    if not sp:
        return None
    for s in am[0]:
        if s.startswith("MSA" + sp[0]):
            return _campo(s, 1, sp[0]) or None
    return None


def texto(e):
    return CABECERA + "\n" + "\n".join("  - " + h for h in hechos(e)) + "\n"


# --------------------------------------------------------------------------
def autoprueba():
    mal = []

    def mira(nombre, obtenido, esperado):
        ok = obtenido == esperado
        print(("  ok  " if ok else "  MAL ") + nombre + ("" if ok else ": %r != %r" % (obtenido, esperado)))
        if not ok:
            mal.append(nombre)

    def est(pid8, genero, ack="MSH|^~\\&|LABFHIR|LAB|X|Y|t||ACK^A01^ACK|M1|P|2.5\nMSA|AA|M1", version="2.5"):
        m = ("<VT>MSH|^~\\&|A|B|C|D|20230101||ADT^A01^ADT_A01|M1|P|%s\nEVN|A01|20230101\n"
             "PID|1||X1^^^H^MR||Ap^No||20000101|%s\n<FS>" % (version, pid8))
        return {"mensaje": m, "sesiones": [{"canonico": {"Gender": genero}}] if genero is not None else [], "ack": ack}

    def uno(h, prefijo):
        return [x for x in h if x.startswith(prefijo)]

    h = hechos(est("X", "unknown"))
    mira("X: NO está en la 0001 y sin destino", ("NO está en la tabla 0001" in uno(h, "PID-8")[0],
                                                "no le da destino" in uno(h, "PID-8")[0]), (True, True))
    h = hechos(est("U", "unknown"))
    mira("U: está, destino unknown, coincide", ("SÍ está" in uno(h, "PID-8")[0], "oficial: unknown" in uno(h, "PID-8")[0],
                                               "(coincide" in uno(h, "PID-8")[0]), (True, True, True))
    h = hechos(est("N", "other"))
    mira("N: está, destino other, coincide", ("SÍ está" in uno(h, "PID-8")[0], "oficial: other" in uno(h, "PID-8")[0],
                                             "(coincide" in uno(h, "PID-8")[0]), (True, True, True))
    h = hechos(est("M", "unknown"))
    mira("M -> unknown: NO coincide con el mapeo", "NO coincide" in uno(h, "PID-8")[0], True)
    h = hechos(est("", "unknown"))
    mira("PID-8 vacío: no hay valor que buscar", "vacío o ausente" in uno(h, "PID-8")[0], True)
    h = hechos(est("f", "female"))
    mira("f minúscula: no está literal, sí en mayúscula", ("NO está" in uno(h, "PID-8")[0],
                                                          "En mayúscula, 'F' sí está" in uno(h, "PID-8")[0]), (True, True))
    h = hechos(est("2", "unknown"))
    mira("2: NO está y sin nota de mayúsculas", ("NO está" in uno(h, "PID-8")[0], "mayúscula" in uno(h, "PID-8")[0]), (True, False))
    h = hechos(est("U", "unknown"))
    mira("MSA-1 = AA: está en la 0008", "SÍ está en la tabla 0008" in uno(h, "MSA-1")[0], True)
    mira("sin ERR: ningún hecho de ERR-3", (uno(h, "ERR-3"), "El ACK no lleva segmento ERR." in h), ([], True))
    ack104 = ("MSH|^~\\&|LABFHIR|LAB|X|Y|t||ACK^A01^ACK|M1|P|2.5\nMSA|AR|M1\n"
              "ERR|||104^Value too long^HL70357|E||||demasiado largo")
    h = hechos(est("F", None, ack=ack104))
    mira("ERR-3 = 104: NO está en la 0357 de v2.5", "NO está en la tabla 0357" in uno(h, "ERR-3")[0], True)
    mira("ERR-4 = E: está en la 0516", "SÍ está en la tabla 0516" in uno(h, "ERR-4")[0], True)
    mira("sin canónico: se dice", "no hubo mensaje canónico" in uno(h, "PID-8")[0], True)
    ack101 = ack104.replace("104^Value too long", "101^Required field missing")
    mira("ERR-3 = 101: está", "SÍ está en la tabla 0357" in uno(hechos(est("F", None, ack=ack101)), "ERR-3")[0], True)
    h = hechos(est("U", "unknown", version="2.3"))
    mira("MSH-12 = 2.3 [S19]: no la acepta", "anterior a 2.4 o no es 2.x; el sitio no la acepta [S19]" in uno(h, "MSH-12")[0], True)
    h26 = uno(hechos(est("U", "unknown", version="2.6")), "MSH-12")[0]
    mira("H-S19 2.6: dentro de lo aceptado; '2': sin forma", ("dentro de lo que el sitio acepta" in h26 and "[S19]" in h26,
         "no tiene la forma" in uno(hechos(est("U", "unknown", version="2")), "MSH-12")[0]), (True, True))
    hx = uno(hechos(est("X", "unknown", version="2.6")), "PID-8")[0]
    mira("H-S22 2.6 + X: fuera de 0001, puede ser legal [S22]; con 2.5 no",
         ("NO está en la tabla 0001 de v2.5" in hx and "puede ser legal en su versión" in hx and "[S22]" in hx,
          "puede ser legal" in uno(hechos(est("X", "unknown")), "PID-8")[0]), (True, False))
    h = hechos(est("U", "unknown", ack=None))
    mira("sin ACK: se dice y no se inventa MSA", ("El emisor no recibió ACK: no hay MSA ni ERR que comprobar." in h,
                                                 uno(h, "MSA-1")), (True, []))
    alt = {"mensaje": "MSH#$%\\&#A#B#C#D#t##ADT$A01#M1#P#2.5\nPID#1##X1##Ap$No##20000101#X", "sesiones": [], "ack": None}
    mira("separadores alternativos: X se lee igual", "PID-8 = 'X': NO está" in uno(hechos(alt), "PID-8")[0], True)
    bom = {"mensaje": est("U", None)["mensaje"].replace("<VT>MSH", "<VT>﻿MSH"), "sesiones": [], "ack": None}
    mira("BOM delante de MSH: se lee igual", "PID-8 = 'U': SÍ está" in uno(hechos(bom), "PID-8")[0], True)
    dos = {"mensaje": est("U", None)["mensaje"] + est("X", None)["mensaje"], "sesiones": [], "ack": None}
    h = hechos(dos)
    mira("dos mensajes en un marco: hechos de cada uno", (sum("Mensaje 1 de 2" in x for x in h) >= 1,
                                                          any("Mensaje 2 de 2" in x and "'X': NO" in x for x in h)), (True, True))
    dup = {"mensaje": est("U", None)["mensaje"].replace("<FS>", "PID|1||X2^^^H^MR||Ap^No||20000101|X\n<FS>"), "sesiones": [], "ack": None}
    mira("PID duplicado: los dos segmentos", sum("Segmento PID" in x for x in hechos(dup)), 2)
    B0 = ["MSH|^~\\&|A|B|C|D|20230101||ADT^A01^ADT_A01|M1|P|2.5", "EVN|A01|20230101", "PID|1||X1^^^H^MR||Ap^No||20000101|U", "PV1|1|I"]
    h = hechos({"mensaje": "<VT><VT>" + B0[0] + "\n<FS>\n<VT>" + "\n".join(B0[1:]) + "\n<FS>\n<FS>", "sesiones": [], "ack": None})
    mira("H-S31 trama partida: sin PID y hecho de marcos", ("No hay segmento PID." in h,
         any(x.startswith("El cable trae 2 marcos MLLP; el marco 2 no tiene MSH (segmentos: EVN PID PV1)") for x in h),
         any(("fallo" in x.lower() or "veredicto" in x.lower()) for x in h)), (True, True, False))
    h = hechos({"mensaje": "<VT>" + "\n".join(B0[:2]) + "\n<FS><VT>" + "\n".join(B0[2:]) + "\n<FS>", "sesiones": [], "ack": None})
    mira("H-S36 MSH+EVN | PID+PV1", ("No hay segmento PID." in h, any("segmentos: PID PV1" in x for x in h)), (True, True))
    BL0 = [B0[0] + "||||||UNICODE UTF-8"] + B0[1:]
    h = hechos({"mensaje": "<VT>" + "<0x0A>".join(BL0) + "<0x0A><FS>\n", "sesiones": [], "ack": None})
    mira("H-LF segmentos tras LF: hecho, sin PID, sin fallo ni veredicto",
         ("No hay segmento PID." in h,
          any(x.startswith("El marco 1 trae los segmentos EVN PID PV1 tras un byte de control que no es CR (<0x0A>)") for x in h),
          any(("fallo" in x.lower() or "veredicto" in x.lower()) for x in h)), (True, True, False))
    mira("H-LF-c controles: cable normal y trama partida, sin ese hecho",
         [any(x.startswith("El marco 1 trae los segmentos") for x in hechos({"mensaje": c, "sesiones": [], "ack": None}))
          for c in ("<VT>" + "\n".join(B0) + "\n<FS>", "<VT><VT>" + B0[0] + "\n<FS>\n<VT>" + "\n".join(B0[1:]) + "\n<FS>\n<FS>")],
         [False, False])
    mira("basura: no se afirma nada", hechos({"mensaje": "hola", "sesiones": [], "ack": "x"}),
         ["No se pudo leer por código ningún mensaje del cable: no se afirma nada de sus campos.",
          "El ACK no se puede leer por código: no se afirma nada de él."])
    mira("msa1: AA, AR con ERR, sin ACK, basura",
         (msa1(est("U", "unknown")), msa1(est("F", None, ack=ack104)), msa1(est("U", "unknown", ack=None)),
          msa1({"ack": "x"})), ("AA", "AR", None, None))
    mira("ningún hecho usa la palabra veredicto ni fallo", any(("fallo" in x.lower() or "veredicto" in x.lower())
                                                               for x in hechos(est("X", "unknown", ack=ack104))), False)
    s9 = {"mensaje": est("U", None)["mensaje"].replace("Ap^No", "Mu<0xF1>oz^No"), "sesiones": [], "ack": None}
    h = hechos(s9)
    mira("H-S9 byte <0xF1> en PID-5: hecho de descodificación", uno(h, "El cable trae bytes no decodificables"),
         ["El cable trae bytes no decodificables marcados <0xNN> (F1 en PID-5): se leen como latin-1 [S9]."])
    mira("H-S9c sin marcadores: sin ese hecho", uno(hechos(est("U", None)), "El cable trae"), [])
    print("AUTOPRUEBA DE hechos_normativos: " + ("TODO BIEN" if not mal else "FALLAN %d" % len(mal)))
    return 1 if mal else 0


def censo(rutas):
    vistos, n = collections.Counter(), 0
    for r in rutas:
        for linea in open(r, encoding="utf-8"):
            f = json.loads(linea)
            for h in hechos(f["estructura"]):
                n += 1
                clave = h.split(":")[0] + (": " + h.split(":")[1].split(".")[0] if ":" in h else "")
                vistos[clave[:110]] += 1
    for k, v in vistos.most_common():
        print("%5d  %s" % (v, k))
    print("%d hechos, ninguna excepción" % n)


def main():
    a = sys.argv[1:]
    if a[:1] == ["--autoprueba"]:
        return autoprueba()
    if a[:1] == ["--censo"]:
        censo(a[1:])
        return 0
    for linea in open(a[0], encoding="utf-8"):
        f = json.loads(linea)
        if len(a) < 2 or f["instancia"].endswith(a[1]):
            print("==", f["instancia"])
            print(texto(f["estructura"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
