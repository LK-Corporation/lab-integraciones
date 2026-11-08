#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 40 (pd/diseno-pd-fable.md §4, con pd/decision-jev-pd.md): el rejuicio de todas las evidencias guardadas con el juez de esta
carpeta, frente a la línea base hecha con el juez de antes (md/rejuicio_md.py linea_base), y la clasificación de cada diferencia como
de la conducta de PD1-7 («pd17») o «fuera». Usa md/rejuicio_md.py y las lecturas del mensaje de jz/rejuicio_jz.py sin tocarlos.

  python3 pd/rejuicio_pd.py comparar <linea_base.jsonl> <salida.json> <carpeta de evidencias> [...]
  python3 pd/rejuicio_pd.py control  <linea_base.jsonl> <salida.json> <firmas.json> <carpeta de evidencias> [...]

Una diferencia es de la conducta de PD1-7 si no falla ninguna de estas reglas; si falla alguna, es «fuera», que es la regla de parada
del ANTES («comparar» sale con 1). Cada regla se mira por separado, para que el control diga cuáles cazan cada defecto.
- R1, el caso: el punto es adt_conv y el mensaje trae PD1 con PD1-7 valorado (su primer componente).
- R2, la forma: lo que sale es recurso_inventado de OBX, recurso_sin_mapa de ACC, PDA o ACC/PDA, o la nota fuera_proyeccion de OBX;
  lo que entra, eso mismo o un hallazgo de PD1-7 de los que el juez da de ella (recurso_ausente, codigo_mal_mapeado, valor_distinto,
  fhir_invalido, referencia_rota, dato_perdido, y las notas convencion y version), y nada de rechazos.
- R3, el valor: los hallazgos de PD1-7 que entran dicen el valor de PD1-7 del mensaje (recurso_ausente «= 'F'», codigo_mal_mapeado
  «de 'F'», valor_distinto «esperado 'F'», la nota «para 'F', fuera del ConceptMap»), la nota es convencion con MSH-12 2.5 o vacío y
  version con otra, y recurso_ausente no viene con otro hallazgo de PD1-7.
- R4, el libro de las Observation, por su fullUrl: las parejas (subtipo, url) de recurso_inventado y recurso_sin_mapa que entran
  están entre las que salen; las que salen y no entran son una como mucho, o dos si el mensaje trae OBX, y entonces la nota
  fuera_proyeccion entra o ya estaba; cada recurso_sin_mapa que entra cita un dato que está en ese campo del mensaje (la regla de la
  37) y nombra segmentos que el mensaje trae.
- R5, el veredicto: los recuentos no cambian; el veredicto, si cambia, solo pasa entre correcto y fallo_silencioso «convertido»;
  nada de aceptado_imposible.
El punto de verificar_conversor (punto_vc) que cambia se cuenta aparte, como en la 37.

«control» siembra en el juez, pasada a pasada, un defecto con la forma de la conducta que no lo es, y dos sin ella, y pasa (sale con 0)
solo si toda evidencia con el defecto sale «fuera»; guarda, por pasada, las reglas que la sacan y la firma de lo que cambia. Las
pasadas: PD1-7 ausente en todo ADT sin PD1-7; la Observation de ACC o PDA dada por inventada; la de un OBX sacada de su sitio en un
ADT sin PD1-7; PD1-7 ausente con un valor que no es el del mensaje, en un ADT con PD1 (si el corpus no trae ninguno, marca 0 y se
declara); valor_distinto en PID-5 y en PID-8 (los de la 37)."""
import collections
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(AQUI)
sys.path[:0] = [os.path.join(FASE, "md"), os.path.join(FASE, "jz"), FASE]
import rejuicio_jz as RJ                                  # noqa: E402  (solo sus lecturas del mensaje; no se toca)

REGLAS = ("R1", "R2", "R3", "R4", "R5")
SIN_MAPA_HECHOS = {"ACC": ("ACC",), "PDA": ("PDA",), "ACC/PDA": ("ACC", "PDA")}
SUB_PD17 = {"recurso_ausente", "codigo_mal_mapeado", "valor_distinto", "fhir_invalido", "referencia_rota", "dato_perdido",
            "convencion", "version"}
RECURSOS = ("recurso_inventado", "recurso_sin_mapa")


def valor_pd17(mensaje):
    """El primer componente de PD1-7 del mensaje crudo (el primer PD1); "" si no hay PD1 o viene vacío."""
    f, cs, rs, _, _ = RJ._partes(mensaje)
    v = RJ._campo(mensaje, "PD1", 7)
    return (v or "").split(rs)[0].split(cs)[0]


def msh12(mensaje):
    f, cs, _, _, _ = RJ._partes(mensaje)
    return (RJ._campo(mensaje, "MSH", 11) or "").split(cs)[0]      # MSH-12 es el campo 11 al partir por el separador


def _forma_permitida(h):
    """Los tres sitios de una Observation sin rol (R2)."""
    return ((h["subtipo"] == "recurso_inventado" and h["hecho"] == "OBX") or
            (h["subtipo"] == "recurso_sin_mapa" and h["hecho"] in SIN_MAPA_HECHOS) or
            (h["clase"] == "nota" and h["subtipo"] == "fuera_proyeccion" and h["hecho"] == "OBX"))


def _url(q):
    m = RJ.URL.match(q)
    return m.group(1) if m else q


def _diferencia(antes, ahora):
    a = collections.Counter(RJ._clave(h) for h in antes["hallazgos"])
    b = collections.Counter(RJ._clave(h) for h in ahora["hallazgos"])
    return [json.loads(k) for k in (a - b).elements()], [json.loads(k) for k in (b - a).elements()]


def reglas(antes, ahora, mensaje, punto):
    """Las reglas que fallan para la diferencia entre dos juicios (lista vacía: es de la conducta de PD1-7)."""
    salen, entran = _diferencia(antes, ahora)
    falla = []
    v = valor_pd17(mensaje)
    segs = RJ._segmentos(mensaje)
    if punto != "adt_conv" or not v:                                                               # R1
        falla.append("R1")
    r2 = any(h["clase"] == "rechazo" for h in salen + entran)                                       # R2
    r2 = r2 or not all(_forma_permitida(h) for h in salen)
    r2 = r2 or not all(_forma_permitida(h) or (h["hecho"] == "PD1-7" and set((h["subtipo"] or "").split("+")) <= SUB_PD17)
                       for h in entran)
    if r2:
        falla.append("R2")
    pd = [h for h in entran if h["hecho"] == "PD1-7"]                                               # R3
    r3 = False
    version = msh12(mensaje) not in ("", "2.5")
    for h in pd:
        que = " ".join(h.get("que") or [])
        subs = set((h["subtipo"] or "").split("+"))
        if "recurso_ausente" in subs and ("PD1-7 = %r" % v) not in que:
            r3 = True
        if "codigo_mal_mapeado" in subs and ("(de %r)" % v) not in que:
            r3 = True
        if "valor_distinto" in subs and ("esperado %r" % v) not in que:
            r3 = True
        if subs & {"convencion", "version"} and "fuera del ConceptMap" in que:
            if (" para %r, fuera del ConceptMap" % v) not in que or subs != ({"version"} if version else {"convencion"}):
                r3 = True
    if any("recurso_ausente" in (h["subtipo"] or "") for h in pd) and len(pd) > 1:
        r3 = True
    if r3:
        falla.append("R3")
    par = lambda hs: collections.Counter((h["subtipo"], _url(q)) for h in hs if h["subtipo"] in RECURSOS for q in h.get("que") or [])
    p_sal, p_ent = par(salen), par(entran)                                                          # R4
    r4 = bool(p_ent - p_sal) or sum((p_sal - p_ent).values()) > (2 if "OBX" in segs else 1)
    if sum((p_sal - p_ent).values()) == 2:
        nota = lambda hs: any(h["clase"] == "nota" and h["subtipo"] == "fuera_proyeccion" for h in hs)
        r4 = r4 or not nota(ahora["hallazgos"])
    for h in entran:
        if h["subtipo"] != "recurso_sin_mapa":
            continue
        for q in h.get("que") or []:
            m = RJ.SIN_MAPA.match(q)
            if not m or RJ.TEXTO_2[m.group(2)] != h["hecho"] or not set(SIN_MAPA_HECHOS[h["hecho"]]) <= segs:
                r4 = True
                continue
            for campo in m.group(3).split("/"):
                if campo[:3] not in SIN_MAPA_HECHOS[h["hecho"]] or not RJ._tiene(mensaje, campo, m.group(4), bool(m.group(5))):
                    r4 = True
    if r4:
        falla.append("R4")
    va, vb = antes["veredicto"], ahora["veredicto"]                                                  # R5
    r5 = antes.get("recuentos") != ahora.get("recuentos")
    if va != vb:
        ok = {("correcto", None), ("fallo_silencioso", "convertido")}
        r5 = r5 or (va["categoria"], va.get("subtipo")) not in ok or (vb["categoria"], vb.get("subtipo")) not in ok
    if r5:
        falla.append("R5")
    return falla


def clasificar(antes, ahora, mensaje, punto):
    """{"pd17"}, {"fuera"}, o set() si los dos juicios son iguales."""
    if antes == ahora:
        return set()
    return {"fuera"} if reglas(antes, ahora, mensaje, punto) else {"pd17"}


DEFECTOS = ("PD1-7-ausente", "ACC-inventada", "OBX-fuera-de-sitio", "PD1-7-valor-ajeno", "PID-5", "PID-8")


def _inyectar(defecto, marca):
    """Un defecto en el juez de esta carpeta; devuelve cómo deshacerlo."""
    import conversion as CV
    if defecto in ("PID-5", "PID-8"):
        return RJ._inyectar(defecto, marca)
    if defecto in ("PD1-7-ausente", "PD1-7-valor-ajeno"):
        orig, nombre = CV._juzgar, "_juzgar"

        def roto(J, m, lec, familia):
            orig(J, m, lec, familia)
            if familia != "adt" or CV._valor_pd17(m):
                return
            if defecto == "PD1-7-valor-ajeno" and CV._seg(m, "PD1") is None:
                return
            marca[0] = True
            J.cuenta("recurso_ausente", "PD1-7", "falta la Observation de PD1-7 = %r (PD1[Observation-LivingWill])" %
                     ("F" if defecto == "PD1-7-ausente" else "Z"), citas=CV.C["PD1-7"])
    elif defecto == "ACC-inventada":
        orig, nombre = CV._origen_sin_mapa, "_origen_sin_mapa"

        def roto(m, r):
            sm = orig(m, r)
            if sm:
                marca[0] = True
                return None
            return sm
    else:                                                                       # OBX-fuera-de-sitio
        orig, nombre = CV.emparejar, "emparejar"

        def roto(m, entries, familia, notas=()):
            out = orig(m, entries, familia, notas)
            if familia == "adt" and not CV._valor_pd17(m):
                for s in out.get("sobrantes") or []:
                    if s.get("motivo") == "origen_guia":
                        s["motivo"] = "inventado"
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
              and set(cero) <= {"PD1-7-valor-ajeno"})
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
                salen, entran = _diferencia(ga, gb)
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
                salen, entran = _diferencia(ga, gb)
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
    print("rejuicio pd (%s%s): %d evidencias, %d diferencias %s; faltan %d, punto cambia %d; juez %s" % (
        modo, " " + defecto if defecto else "", n, n_dif, dict(sorted(ev_clase.items())), len(faltan), len(punto_cambia),
        res["juez_ahora"][:12]))
    if modo == "control":
        print("  %d evidencias con el defecto, %d de ellas «fuera»; reglas: %s" % (marcadas, marcadas_fuera, dict(f_reglas.most_common())))
    for f in fuera[:10] if modo == "comparar" else []:
        print("  FUERA %s" % json.dumps(f, ensure_ascii=False)[:400])
    return res


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
