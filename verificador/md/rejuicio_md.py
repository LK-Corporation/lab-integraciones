#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 26, MD1-e y P-MD-25 (md/diseno-md.md §8 y §11): ADT, ORU y VXU no cambian. Adaptado de vx/rejuicio_vx.py.

Juzga todas las evidencias de las carpetas dadas (privado: las del estudio de conversores, de VXU, del arrastre, de MD-pre…) con
el juez de esta carpeta y escribe, por evidencia, dos cosas:
  - «guardado»: el veredicto y todos los hallazgos (clase, subtipo, hecho, cuenta, que, citas, certeza…) y los recuentos, con el
    punto de entrada que trae la evidencia. Tiene que dar lo mismo, byte a byte, antes y después de MDM (P-MD-25 b).
  - «punto_vc»: el punto que la herramienta (cv/verificar_conversor.punto) da hoy al mensaje. Solo puede cambiar en los MDM
    (S-MD-15, P-MD-25 e); con el juez nuevo, esos se juzgan además con su punto nuevo y se resumen aparte.
Con «comparar», exige que «guardado» sea igual en todas y que «punto_vc» cambie solo en mensajes MDM, y lista lo que difiera.

  python3 md/rejuicio_md.py linea_base <salida.jsonl> <carpeta de evidencias> [...]
  python3 md/rejuicio_md.py comparar   <linea_base.jsonl> <carpeta de evidencias> [...]
  python3 md/rejuicio_md.py control    <linea_base.jsonl> <carpeta de evidencias> [...]   # defectos inyectados: debe ver diferencias
  python3 md/rejuicio_md.py informes_base     <salida.json> <carpeta> [...]   # P-MD-25 c: el INFORME de cada corrida, rehecho
  python3 md/rejuicio_md.py informes_comparar <base.json>   <carpeta> [...]"""
import collections
import glob
import json
import os
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIVADO = os.path.normpath(os.path.join(FASE, "..", "privado"))
sys.path[:0] = [FASE, os.path.join(FASE, "cv")]
_argv, sys.argv = sys.argv, ["x", "--silencio"]
import conversion as CV  # noqa: E402
import mcp_verificador as M  # noqa: E402
import puntos_entrada as PE  # noqa: E402
import verificador as V  # noqa: E402
import verificar_conversor as VC  # noqa: E402
sys.argv = _argv

CAMPOS = ("clase", "subtipo", "hecho", "cuenta", "que", "citas", "certeza", "nivel", "estado", "causa", "alternativa")


def juicio(e):
    r = V.verificar(e)
    return {"veredicto": r["veredicto"], "hallazgos": [{k: h.get(k) for k in CAMPOS} for h in r["hallazgos"]],
            "recuentos": (r.get("conversion") or {}).get("recuentos")}


def _texto(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


def es_mdm(e):
    c = VC._msh9_partes(e.get("mensaje") or "")
    return bool(c) and c[0].upper().startswith("MDM")


def evidencias(carpetas):
    for c in carpetas:
        for f in sorted(glob.glob(os.path.join(c, "**", "*.json"), recursive=True)):
            try:
                e = json.load(open(f, encoding="utf-8"))
            except ValueError:
                continue
            if isinstance(e, dict) and "conversion" in e and "punto_entrada" in e:
                a = os.path.abspath(f)
                yield (os.path.relpath(a, PRIVADO) if a.startswith(PRIVADO + os.sep) else a), e


def fila(ruta, e):
    return {"evidencia": ruta, "guardado": _texto(juicio(e)), "punto": e["punto_entrada"], "punto_vc": VC.punto(e.get("mensaje") or ""),
            "mdm": es_mdm(e)}


VARIABLES = (("juez",), ("herramienta", "huella"), ("limites", "L-VC", "L-VC-2"))    # P-MD-25 c: lo que puede cambiar, declarado


def corridas(carpetas):
    """Las corridas de la herramienta (ADAPTADOR.json, CORRIDA.json, corpus/CASOS.json y evidencias) bajo las carpetas."""
    for c in carpetas:
        for a in sorted(glob.glob(os.path.join(c, "**", "ADAPTADOR.json"), recursive=True)):
            d = os.path.dirname(a)
            if os.path.exists(os.path.join(d, "CORRIDA.json")) and os.path.exists(os.path.join(d, "corpus", "CASOS.json")):
                yield os.path.relpath(os.path.abspath(d), PRIVADO), d


def informe(d):
    """P-MD-25 c: el INFORME.json y el juicio de una corrida, rehechos en memoria con el juez de ahora (como --desde-evidencias),
    sin lo que puede cambiar (VARIABLES)."""
    ad = json.load(open(os.path.join(d, "ADAPTADOR.json"), encoding="utf-8"))
    cr = json.load(open(os.path.join(d, "CORRIDA.json"), encoding="utf-8"))
    co = json.load(open(os.path.join(d, "corpus", "CASOS.json"), encoding="utf-8"))
    info = {"juez": M._version(), "huella": cr["huella"], "huella_con_nombres": cr["huella_con_nombres"], "imagen_digest": cr.get("imagen_digest")}
    sens = cr.get("opciones", {}).get("sensibilidad", True)
    filas = []
    for x in co["casos"]:
        f = os.path.join(d, "evidencias", ad["id"], x["corpus"], x["caso"] + ".json")
        if os.path.exists(f):
            filas.append(VC.juzgar(ad["id"], x, json.load(open(f, encoding="utf-8")), sens))
    inf = json.loads(json.dumps(VC.agregar(ad, info, filas, co, cr.get("sin_evidencia", [])), ensure_ascii=False))
    for ruta in VARIABLES:
        x = inf
        for k in ruta[:-1]:
            x = x.get(k) or {}
        if ruta[-1] in x:
            x[ruta[-1]] = "(variable)"
    return {"informe": _texto(inf), "juicio": _texto(filas), "n": len(filas)}


def main(modo, base, *carpetas):
    if modo in ("informes_base", "informes_comparar"):
        ahora = {r: informe(d) for r, d in corridas(carpetas)}
        if modo == "informes_base":
            json.dump(ahora, open(base, "w", encoding="utf-8"), ensure_ascii=False, sort_keys=True)
            print("informes: %d corridas (%d evidencias), juez %s" % (len(ahora), sum(x["n"] for x in ahora.values()), M._version()["huella"][:12]))
            return 0
        antes = json.load(open(base, encoding="utf-8"))
        dif = sorted(r for r in set(antes) | set(ahora) if antes.get(r) != ahora.get(r))
        print("informes (%s): %d corridas, %d con el INFORME o el juicio distinto; juez %s" % (
            modo, len(ahora), len(dif), M._version()["huella"][:12]))
        for r in dif[:10]:
            a, b = antes.get(r) or {}, ahora.get(r) or {}
            print("  distinta: %s (informe %s, juicio %s)" % (r, "igual" if a.get("informe") == b.get("informe") else "DISTINTO",
                                                           "igual" if a.get("juicio") == b.get("juicio") else "DISTINTO"))
        return 0 if not dif else 1
    if modo == "linea_base":
        n, por = 0, collections.Counter()
        with open(base, "w", encoding="utf-8") as g:
            for ruta, e in evidencias(carpetas):
                f = fila(ruta, e)
                g.write(json.dumps(f, ensure_ascii=False, sort_keys=True) + "\n")
                n += 1
                por["/".join(ruta.split(os.sep)[:2]) + ":" + f["punto"]] += 1
        print("línea base: %d evidencias, juez %s" % (n, M._version()["huella"][:12]))
        for k in sorted(por):
            print("  %-32s %d" % (k, por[k]))
        return 0
    if modo == "control":                                        # P-MD-25, control negativo: un defecto en ADT y otro en VXU se ven
        import conversion_vxu as CVX
        pat, est = CV._patient, CVX._status

        def roto_pat(J, m, pid, r, *a, **k):
            J.cuenta("valor_distinto", "PID-5", "defecto inyectado por el control del rejuicio")
            return pat(J, m, pid, r, *a, **k)

        def roto_est(J, m, rxa, r, h):
            J.cuenta("valor_distinto", h("RXA", 20), "defecto inyectado por el control del rejuicio")
            return est(J, m, rxa, r, h)
        CV._patient, CVX._status = roto_pat, roto_est
    antes = {}
    for l in open(base, encoding="utf-8"):
        x = json.loads(l)
        antes[x["evidencia"]] = x
    dif, dif_punto, nuevos, n, vistas = [], [], collections.Counter(), 0, set()
    por_pe = collections.Counter()
    for ruta, e in evidencias(carpetas):
        n += 1
        vistas.add(ruta)
        ahora = fila(ruta, e)
        a = antes.get(ruta)
        if a is None or a["guardado"] != ahora["guardado"]:
            dif.append((ruta, ahora["punto"]))
            por_pe[ahora["punto"]] += 1
        if a is not None and a["punto_vc"] != ahora["punto_vc"]:
            dif_punto.append((ruta, a["punto_vc"], ahora["punto_vc"], ahora["mdm"]))
            if ahora["punto_vc"] in PE.PUNTOS:
                e2 = dict(e, punto_entrada=ahora["punto_vc"])
                v = juicio(e2)["veredicto"]
                ev = VC._msh9_partes(e["mensaje"])
                nuevos[(ahora["punto_vc"], "^".join(ev[:2]), v["categoria"], v["subtipo"])] += 1
    falta = sorted(set(antes) - vistas)
    no_mdm = [x for x in dif_punto if not x[3]]
    print("rejuicio (%s): %d evidencias, %d diferencias, %d de la línea base sin evidencia; juez %s" % (
        modo, n, len(dif), len(falta), M._version()["huella"][:12]))
    if por_pe:
        print("  diferencias por punto: %s" % dict(sorted(por_pe.items())))
    for d in dif[:10]:
        print("  distinta: %s (%s)" % d)
    print("punto de la herramienta: %d cambian (%d MDM, %d no MDM)" % (len(dif_punto), len(dif_punto) - len(no_mdm), len(no_mdm)))
    for d in no_mdm[:10]:
        print("  MAL cambia el punto de un no MDM: %s %s -> %s" % d[:3])
    for k in sorted(nuevos, key=str):
        print("  con su punto nuevo: %-9s %-10s %-18s %-12s %d" % (k[0], k[1], k[2], k[3] or "", nuevos[k]))
    if modo == "control":
        return 0 if dif else 1
    return 0 if not dif and not falta and not no_mdm else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
