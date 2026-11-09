#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 41 (po/diseno-po-fable.md §4, con po/decision-jev-po.md): el rejuicio de todas las evidencias guardadas con el juez de esta
carpeta, frente a la línea base hecha con el juez de antes (md/rejuicio_md.py linea_base), y la clasificación de cada diferencia como
de la conducta de PD1-7 en ORU («pd17oru») o «fuera». Usa md/rejuicio_md.py, pd/rejuicio_pd.py (sus reglas R3 y R5, las del valor y
del veredicto, que no dependen del punto) y las lecturas del mensaje de jz/rejuicio_jz.py, sin tocarlos.

  python3 po/rejuicio_po.py comparar <linea_base.jsonl> <salida.json> <carpeta de evidencias> [...]
  python3 po/rejuicio_po.py control  <linea_base.jsonl> <salida.json> <firmas.json> <carpeta de evidencias> [...]

Una diferencia es de la conducta si no falla ninguna de estas reglas; si falla alguna, es «fuera», que es la regla de parada del ANTES
(«comparar» sale con 1). Cada regla se mira por separado, para que el control diga cuáles cazan cada defecto.
- R1, el caso: el punto es oru_conv y el mensaje trae PD1 con PD1-7 valorado (su primer componente). Un ADT que cambie sale por R1.
- R2, la forma: lo que sale es recurso_inventado de OBX o la nota fuera_proyeccion de OBX; lo que entra, recurso_inventado de OBX o
  un hallazgo de PD1-7 de los que da el juez (la lista de la 40); ningún rechazo (Q-PO-1 a: ninguna nota de OBR).
- R3, el valor, y R5, el veredicto: las de pd/rejuicio_pd.py, tal cual.
- R4, el libro de las Observation, por su fullUrl: ninguna pareja (recurso_inventado, url) entra que no saliera; sale, sin volver, una
  como mucho; la nota fuera_proyeccion no entra, y solo sale si el mensaje trae OBX fuera de ORDER_OBSERVATION (antes del primer OBR o
  tras un SPM, como los cuenta el juez).
El punto de verificar_conversor (punto_vc) que cambia se cuenta aparte.

«control» siembra en el juez, pasada a pasada, un defecto con la forma de la conducta que no lo es, y dos sin ella, y pasa (sale con 0)
solo si toda evidencia con el defecto sale «fuera»; guarda, por pasada, las reglas que la sacan y la firma de lo que cambia. Una pasada
que no marca ninguna evidencia se declara; solo puede ser la de L-CV-7 si la línea base no trae la nota."""
import collections
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(AQUI)
sys.path[:0] = [os.path.join(FASE, "md"), os.path.join(FASE, "jz"), os.path.join(FASE, "pd"), FASE]
import rejuicio_jz as RJ                                  # noqa: E402  (solo sus lecturas del mensaje; no se toca)
import rejuicio_pd as RP                                  # noqa: E402  (sus R3 y R5; no se toca)

REGLAS = ("R1", "R2", "R3", "R4", "R5")


def obx_fuera(mensaje):
    """Cuántos OBX trae el mensaje fuera de ORDER_OBSERVATION: antes del primer OBR o tras un SPM (como _grupos_oru del juez)."""
    f, _, _, _, segs = RJ._partes(mensaje)
    n, ctx = 0, None
    for s in segs:
        nombre = s.split(f)[0]
        if nombre == "OBR":
            ctx = "obr"
        elif nombre == "SPM":
            ctx = "spm"
        elif nombre == "OBX" and ctx != "obr":
            n += 1
    return n


def _inventada(h):
    return h["subtipo"] == "recurso_inventado" and h["hecho"] == "OBX"


def _nota_l_cv_7(h):
    return h["clase"] == "nota" and h["subtipo"] == "fuera_proyeccion" and h["hecho"] == "OBX"


def reglas(antes, ahora, mensaje, punto):
    """Las reglas que fallan para la diferencia entre dos juicios (lista vacía: es de la conducta de PD1-7 en ORU)."""
    salen, entran = RP._diferencia(antes, ahora)
    falla = []
    if punto != "oru_conv" or not RP.valor_pd17(mensaje):                                       # R1
        falla.append("R1")
    r2 = any(h["clase"] == "rechazo" for h in salen + entran)                                   # R2
    r2 = r2 or not all(_inventada(h) or _nota_l_cv_7(h) for h in salen)
    r2 = r2 or not all(_inventada(h) or (h["hecho"] == "PD1-7" and set((h["subtipo"] or "").split("+")) <= RP.SUB_PD17)
                       for h in entran)
    if r2:
        falla.append("R2")
    de_pd = [x for x in RP.reglas(antes, ahora, mensaje, "adt_conv") if x in ("R3", "R5")]      # R3 y R5, las de la 40
    if "R3" in de_pd:
        falla.append("R3")
    par = lambda hs: collections.Counter(RP._url(q) for h in hs if _inventada(h) for q in h.get("que") or [])
    p_sal, p_ent = par(salen), par(entran)                                                      # R4
    r4 = bool(p_ent - p_sal) or sum((p_sal - p_ent).values()) > 1
    r4 = r4 or any(_nota_l_cv_7(h) for h in entran)
    r4 = r4 or (any(_nota_l_cv_7(h) for h in salen) and not obx_fuera(mensaje))
    if r4:
        falla.append("R4")
    if "R5" in de_pd:
        falla.append("R5")
    return falla


def clasificar(antes, ahora, mensaje, punto):
    """{"pd17oru"}, {"fuera"}, o set() si los dos juicios son iguales."""
    if antes == ahora:
        return set()
    return {"fuera"} if reglas(antes, ahora, mensaje, punto) else {"pd17oru"}


DEFECTOS = ("ORU-PD1-7-ausente", "ORU-PD1-7-valor-ajeno", "ORU-OBX-fuera-de-sitio", "ORU-L-CV-7-inventada", "OBX-5", "PID-5",
            "ADT-PD1-7-ausente")


def _inyectar(defecto, marca):
    """Un defecto en el juez de esta carpeta; devuelve cómo deshacerlo."""
    import conversion as CV
    if defecto == "PID-5":
        return RJ._inyectar(defecto, marca)
    if defecto in ("ORU-PD1-7-ausente", "ORU-PD1-7-valor-ajeno", "ADT-PD1-7-ausente"):
        orig, nombre = CV._juzgar, "_juzgar"
        familia = "adt" if defecto.startswith("ADT") else "oru"

        def roto(J, m, lec, fam):
            orig(J, m, lec, fam)
            if fam != familia or CV._valor_pd17(m):
                return
            if defecto == "ORU-PD1-7-valor-ajeno" and CV._seg(m, "PD1") is None:
                return
            marca[0] = True
            J.cuenta("recurso_ausente", "PD1-7", "falta la Observation de PD1-7 = %r (PD1[Observation-LivingWill])" %
                     ("Z" if defecto == "ORU-PD1-7-valor-ajeno" else "F"), citas=CV.CITAS_PD17[familia])
    elif defecto == "OBX-5":
        orig, nombre = CV._observacion, "_observacion"

        def roto(J, m, obx, r, o, pat_entry, k, obr):
            marca[0] = True
            J.cuenta("valor_distinto", CV._hecho("OBX", k, 5), "defecto inyectado por el control del rejuicio")
            return orig(J, m, obx, r, o, pat_entry, k, obr)
    else:
        orig, nombre = CV.emparejar, "emparejar"

        def roto(m, entries, familia, notas=()):
            out = orig(m, entries, familia, notas)
            if familia != "oru" or CV._valor_pd17(m):
                return out
            if defecto == "ORU-L-CV-7-inventada":                       # una sobrante de L-CV-7, dada por inventada
                for s in out.get("sobrantes") or []:
                    if s.get("motivo") == "origen_guia":
                        s["motivo"] = "inventado"
                        marca[0] = True
            else:                                                       # la Observation de un OBX, sacada de su sitio
                x = next((x for x in out["recursos"] if x["rol"].startswith("Observation#") and x["rol"] != "Observation#PD1"
                          and x["entry"] is not None), None)
                if x is not None:
                    e = x["entry"]
                    x.update({"entry": None, "observado": None, "fullUrl": None, "emparejado_por": None})
                    out["sobrantes"].append({"resourceType": "Observation", "fullUrl": e["fullUrl"], "motivo": "inventado", "hecho": "OBX"})
                    marca[0] = True
            return out
    setattr(CV, nombre, roto)
    return lambda: setattr(CV, nombre, orig)


def main(modo, base, salida, *resto):
    if modo == "control":
        firmas_salida, carpetas = resto[0], resto[1:]
        res, firmas = {}, {}
        for defecto in DEFECTOS:
            r = pasada("control", base, None, carpetas, defecto)
            firmas[defecto] = r.pop("firmas")
            res[defecto] = r
        json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
        json.dump(firmas, open(firmas_salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
        cero = [d for d, r in res.items() if r["control"]["con_defecto"] == 0]
        ok = (all(r["control"]["con_defecto"] == r["control"]["con_defecto_y_fuera"] for r in res.values())
              and set(cero) <= {"ORU-L-CV-7-inventada"})
        print("control: %s%s" % ("PASA (las %d pasadas)" % len(DEFECTOS) if ok else "NO PASA",
                                 "; marcan 0: %s" % ", ".join(cero) if cero else ""))
        return 0 if ok else 1
    if modo != "comparar":
        raise SystemExit(__doc__)
    res = pasada(modo, base, salida, resto)
    return 0 if not res["n_fuera"] and not res["n_faltan"] and not res["n_punto_cambia"] else 1


def pasada(modo, base, salida, carpetas, defecto=None):
    _argv, sys.argv = sys.argv, ["x", "--silencio"]
    import rejuicio_md as RM
    import mcp_verificador as M
    sys.argv = _argv
    marca = [False]
    deshacer = _inyectar(defecto, marca) if defecto else None
    antes = {}
    for linea in open(base, encoding="utf-8"):
        x = json.loads(linea)
        antes[x["evidencia"]] = x
    por, ev_clase = collections.Counter(), collections.Counter()
    fuera, punto_cambia, vistas, n, n_dif = [], [], set(), 0, 0
    marcadas, marcadas_fuera = 0, 0
    f_reglas, f_forma = collections.Counter(), collections.Counter()
    try:
        for ruta, e in RM.evidencias(carpetas):
            n += 1
            vistas.add(ruta)
            marca[0] = False
            ahora = RM.fila(ruta, e)
            a = antes.get(ruta)
            if a is None:
                fuera.append({"evidencia": ruta, "motivo": "no está en la línea base"})
                continue
            if a["punto_vc"] != ahora["punto_vc"]:
                punto_cambia.append(ruta)
            ga, gb = json.loads(a["guardado"]), json.loads(ahora["guardado"])
            mensaje = e.get("mensaje") or ""
            c = clasificar(ga, gb, mensaje, a["punto"])
            if marca[0]:
                marcadas += 1
                marcadas_fuera += c == {"fuera"}
                f_reglas["+".join(reglas(ga, gb, mensaje, a["punto"])) or "(ninguna)"] += 1
                salen, entran = RP._diferencia(ga, gb)
                partes = sorted({"%s %s/%s %s" % (lado, h["clase"], h["subtipo"], h["hecho"])
                                 for lado, hs in (("sale", salen), ("entra", entran)) for h in hs})
                if ga["veredicto"] != gb["veredicto"]:
                    partes.append("veredicto %s -> %s" % (ga["veredicto"]["categoria"], gb["veredicto"]["categoria"]))
                f_forma[" | ".join(partes) or "(sin cambio)"] += 1
            if not c:
                continue
            n_dif += 1
            clave = "+".join(sorted(c))
            por[(clave, RJ._conversor(ruta), RJ._carpeta(ruta), a["punto"])] += 1
            ev_clase[clave] += 1
            if c == {"fuera"} and modo == "comparar":
                salen, entran = RP._diferencia(ga, gb)
                fuera.append({"evidencia": ruta, "punto": a["punto"], "conversor": RJ._conversor(ruta), "reglas": reglas(ga, gb, mensaje, a["punto"]),
                              "veredicto": [ga["veredicto"], gb["veredicto"]], "salen": salen, "entran": entran})
    finally:
        if deshacer:
            deshacer()
    faltan = sorted(set(antes) - vistas)
    res = {"modo": modo, "juez_ahora": M._version()["huella"], "evidencias": n, "diferencias": n_dif,
           "por_clase": dict(sorted(ev_clase.items())),
           "detalle": [{"clase": k[0], "conversor": k[1], "carpeta": k[2], "punto": k[3], "evidencias": v} for k, v in sorted(por.items())],
           "fuera": fuera[:200], "n_fuera": len(fuera), "faltan": faltan[:50], "n_faltan": len(faltan),
           "punto_cambia": punto_cambia[:50], "n_punto_cambia": len(punto_cambia)}
    if modo == "control":
        res["control"] = {"defecto": defecto, "con_defecto": marcadas, "con_defecto_y_fuera": marcadas_fuera}
        res["firmas"] = {"reglas": dict(f_reglas.most_common()), "forma": dict(f_forma.most_common())}
        res.pop("fuera")
    if salida:
        json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print("rejuicio po (%s%s): %d evidencias, %d diferencias %s; faltan %d, punto cambia %d; juez %s" % (
        modo, " " + defecto if defecto else "", n, n_dif, dict(sorted(ev_clase.items())), len(faltan), len(punto_cambia),
        res["juez_ahora"][:12]))
    if modo == "control":
        print("  %d evidencias con el defecto, %d de ellas «fuera»; reglas: %s" % (marcadas, marcadas_fuera, dict(f_reglas.most_common())))
    for f in fuera[:10] if modo == "comparar" else []:
        print("  FUERA %s" % json.dumps(f, ensure_ascii=False)[:400])
    return res


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
