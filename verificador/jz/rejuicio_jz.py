#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 37 (jz/diseno-jz-fable.md §6, con jz/decision-jev-jz.md): el rejuicio de todas las evidencias guardadas con el juez de
esta carpeta, frente a una línea base hecha con el juez de antes (md/rejuicio_md.py linea_base), y la clasificación de cada
diferencia en una de las dos conductas de la etapa 36 o «fuera». Usa md/rejuicio_md.py sin tocarlo.

  python3 jz/rejuicio_jz.py comparar <linea_base.jsonl> <salida.json> <carpeta de evidencias> [...]
  python3 jz/rejuicio_jz.py control  <linea_base.jsonl> <salida.json> <carpeta de evidencias> [...]

Una diferencia es de una conducta si todo lo que cambia en ella (hallazgos que salen y que entran, y el veredicto) cabe en esa
conducta, y además el caso es de esa conducta (segunda versión, 8-nov, tras la revisión a ciegas: antes bastaba la forma del
hallazgo). Si algo no cabe, es «fuera», que es la regla de parada del ANTES: «comparar» sale con 1.
- Conducta 1: un valor de PID-8 o NK1-15 fuera de la 0001. El valor del mensaje (su componente 1) está fuera del mapa de la guía;
  los hallazgos que salen son valor_imposible_convertido, fhir_invalido o la nota de versión de antes; los que entran, fhir_invalido
  o la nota de convención o versión nueva (con la cita de la 0001). Y la cara del rechazo: PID-8 en la lista de un rechazo aceptable.
- «lectura» (jz/decision-jev-jz2.md, Q-JZ-7 b): lo mismo, pero el componente 1 está en la 0001 y el campo entero no (un CWE de v2.8
  que el juez lee entero, como un IS de v2.5); solo pueden cambiar notas. Va aparte: ni conducta 1 ni «fuera».
- Conducta 2: una Observation de un ADT que sale de ACC o PDA. El mensaje trae ACC o PDA; las Observation que salen como
  recurso_inventado (hecho OBX) son las que entran como recurso_sin_mapa, más las que se quedan inventadas (las mismas, por su
  fullUrl); cada recurso_sin_mapa nombra segmentos del mensaje, con su hecho, y el dato que cita está en ese campo del mensaje.
«control» inyecta en el juez defectos ajenos a las dos conductas y pasa (sale con 0) solo si toda evidencia con un defecto
inyectado sale «fuera»: tres sin forma de conducta (valor_distinto en PID-5 y en PID-8, y en RXA-20 de VXU) y cuatro con ella (un
fhir_invalido y una nota de convención en un PID-8 dentro de la 0001; una Observation de un OBX que el juez da por de ACC; y una de
ACC o PDA atribuida al otro segmento)."""
import ast
import collections
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(AQUI)
sys.path[:0] = [os.path.join(FASE, "md"), FASE]
CAMPOS = ("clase", "subtipo", "hecho", "cuenta", "que", "citas", "certeza", "nivel", "estado", "causa", "alternativa")
SUB_1_SALEN = {"valor_imposible_convertido", "fhir_invalido", "version"}
SUB_1_ENTRAN = {"fhir_invalido", "convencion", "version"}
CITA_0001 = "Ch03.txt:5032-5044"
HECHO_1 = re.compile(r"^(PID-8|NK1(\((\d+)\))?-15)$")
HECHO_2 = {"ACC": ("ACC",), "PDA": ("PDA",), "ACC/PDA": ("ACC", "PDA")}
TEXTO_2 = {"ACC": "ACC", "PDA": "PDA", "ACC o PDA": "ACC/PDA"}
URL = re.compile(r"^Observation (\S+) ")
SIN_MAPA = re.compile(r"^Observation (\S+) de (ACC|PDA|ACC o PDA) \(([A-Z]{3}-\d+(?:/[A-Z]{3}-\d+)*) = '([^']*)'(, de la 0136)?\)")
LISTA = re.compile(r"rechazó un mensaje con (\[[^\]]*\])")


def _partes(mensaje):
    """Los separadores y los segmentos del mensaje crudo (sin las funciones del juez)."""
    segs = [s for s in re.split(r"\r\n|\r|\n", mensaje or "") if s]
    if not segs or not segs[0].startswith("MSH") or len(segs[0]) < 8:
        return "|", "^", "~", "&", segs
    f = segs[0][3]
    enc = segs[0].split(f)[1]
    return f, enc[0], (enc[1] if len(enc) > 1 else "~"), (enc[3] if len(enc) > 3 else "&"), segs


def _campo(mensaje, nombre, n, cual=1):
    """El campo n del segmento nombre número cual del mensaje crudo; None si no hay ese segmento."""
    f, _, _, _, segs = _partes(mensaje)
    de = [s.split(f) for s in segs if s.split(f)[0] == nombre]
    if len(de) < cual:
        return None
    p = de[cual - 1]
    return p[n] if len(p) > n else ""


def _fuera_0001(v):
    import conversion as CV                      # solo la tabla: el mapa de la 0001 de la guía
    return bool(v) and CV.mapa("0001", v) == CV.FUERA and CV.mapa("0001", v.upper()) == CV.FUERA


def caso_1(mensaje, hecho):
    """«1» si el valor del campo (su componente 1) está fuera de la 0001; «lectura» si el componente 1 está dentro y el campo entero,
    con componentes, no; None si no es ninguno de los dos."""
    m = HECHO_1.match(hecho or "")
    if not m:
        return None
    _, cs, rs, _, _ = _partes(mensaje)
    v = _campo(mensaje, "PID", 8) if hecho == "PID-8" else _campo(mensaje, "NK1", 15, int(m.group(3) or 1))
    if not v:
        return None
    c1 = v.split(rs)[0].split(cs)[0]
    if _fuera_0001(c1):
        return "1"
    if cs in v and _fuera_0001(v):
        return "lectura"
    return None


def _tiene(mensaje, campo, valor, si_no):
    """El dato que cita un recurso_sin_mapa está en ese campo del mensaje (una repetición, un componente o su primer subcomponente;
    en la 0136, el campo entero en mayúsculas)."""
    f, cs, rs, ss, segs = _partes(mensaje)
    nombre, n = campo.split("-")
    n = int(n)
    for s in segs:
        p = s.split(f)
        if p[0] != nombre or len(p) <= n:
            continue
        if si_no:
            if p[n].upper() == valor:
                return True
            continue
        for rep in p[n].split(rs):
            if rep == valor or any(c == valor or c.split(ss)[0] == valor for c in rep.split(cs)):
                return True
    return False
CONVERSORES = ("microsoft", "linuxforhealth", "juguete", "ejemplo", "propio")


def _clave(h):
    return json.dumps({k: h.get(k) for k in CAMPOS}, ensure_ascii=False, sort_keys=True)


def _lista(h):
    m = LISTA.search(" ".join(h.get("que") or []))
    return ast.literal_eval(m.group(1)) if m else None


def _segmentos(mensaje):
    return {s[:3] for s in re.split(r"\r\n|\r|\n", mensaje or "") if s}


def clasificar(antes, ahora, mensaje, punto):
    """El conjunto de conductas de la diferencia entre dos juicios ({"1"}, {"2"}, {"1", "2"}), {"fuera"}, o set() si son iguales."""
    if antes == ahora:
        return set()
    if antes.get("recuentos") != ahora.get("recuentos"):
        return {"fuera"}
    a = collections.Counter(_clave(h) for h in antes["hallazgos"])
    b = collections.Counter(_clave(h) for h in ahora["hallazgos"])
    salen = [json.loads(k) for k in (a - b).elements()]
    entran = [json.loads(k) for k in (b - a).elements()]
    conductas, rechazo_1 = set(), False
    r_salen = [h for h in salen if h["clase"] == "rechazo"]
    r_entran = [h for h in entran if h["clase"] == "rechazo"]
    if r_salen or r_entran:                                          # la cara de rechazo de la conducta 1 (Q-JZ-1 b)
        if len(r_salen) != 1 or len(r_entran) != 1 or r_salen[0]["subtipo"] != "aceptable":
            return {"fuera"}
        la, lb = _lista(r_salen[0]), _lista(r_entran[0])
        if not la or "PID-8" not in la or caso_1(mensaje, "PID-8") != "1":
            return {"fuera"}
        if r_entran[0]["subtipo"] == "incorrecto" and la == ["PID-8"]:
            rechazo_1 = True
        elif r_entran[0]["subtipo"] == "aceptable" and lb == [x for x in la if x != "PID-8"]:
            rechazo_1 = True
        else:
            return {"fuera"}
        conductas.add("1")
    segs = _segmentos(mensaje)
    adt_sin_destino = punto == "adt_conv" and bool(segs & {"ACC", "PDA"})
    inv_salen, inv_entran, sin_mapa = [], [], []
    for lado, hs in (("salen", salen), ("entran", entran)):
        for h in hs:
            if h["clase"] == "rechazo":
                continue
            subs = set((h["subtipo"] or "").split("+"))
            if HECHO_1.match(h["hecho"] or ""):                     # conducta 1 (o la lectura de NK1-15)
                if not subs <= (SUB_1_SALEN if lado == "salen" else SUB_1_ENTRAN):
                    return {"fuera"}
                if lado == "entran" and h["clase"] == "nota" and not any(CITA_0001 in c for c in h.get("citas") or []):
                    return {"fuera"}
                c = caso_1(mensaje, h["hecho"])
                if c is None or (c == "lectura" and h["clase"] != "nota"):
                    return {"fuera"}
                conductas.add(c)
            elif adt_sin_destino and h["subtipo"] == "recurso_inventado" and h["hecho"] == "OBX":
                (inv_salen if lado == "salen" else inv_entran).append(h)
            elif adt_sin_destino and lado == "entran" and h["subtipo"] == "recurso_sin_mapa" and h["hecho"] in HECHO_2:
                sin_mapa.append(h)
            else:
                return {"fuera"}
    if inv_salen or inv_entran or sin_mapa:                           # conducta 2: las mismas Observation, con su dato
        if not inv_salen or not sin_mapa:
            return {"fuera"}
        urls = lambda hs: collections.Counter(URL.match(q).group(1) if URL.match(q) else q for x in hs for q in x["que"])
        for h in sin_mapa:
            for q in h["que"]:
                m = SIN_MAPA.match(q)
                if not m or TEXTO_2[m.group(2)] != h["hecho"]:
                    return {"fuera"}
                nombres = HECHO_2[h["hecho"]]
                if not set(nombres) <= segs:
                    return {"fuera"}
                for campo in m.group(3).split("/"):
                    if campo[:3] not in nombres or not _tiene(mensaje, campo, m.group(4), bool(m.group(5))):
                        return {"fuera"}
        if urls(inv_salen) != urls(sin_mapa) + urls(inv_entran):
            return {"fuera"}
        conductas.add("2")
    va, vb = antes["veredicto"], ahora["veredicto"]
    if va != vb:
        ca, cb = va["categoria"], vb["categoria"]
        if rechazo_1:
            if not ((ca, cb) == ("correcto", "rechazo_incorrecto") or ca == cb):
                return {"fuera"}
        elif "1" not in conductas:                                   # la conducta 2 no cambia el veredicto (fidelidad sigue)
            return {"fuera"}
        elif not (ca == cb == "fallo_silencioso" or (ca, cb) == ("fallo_silencioso", "correcto")):
            return {"fuera"}
        elif "aceptado_imposible" in (vb.get("subtipo") or ""):
            return {"fuera"}
    return conductas or {"fuera"}


def _conversor(ruta):
    partes = ruta.replace(os.sep, "/").split("/")
    return next((c for c in CONVERSORES if c in partes), next((c for c in CONVERSORES if c in ruta), "?"))


def _carpeta(ruta):
    p = ruta.replace(os.sep, "/").split("/")
    return "/".join(p[:2])


DEFECTOS = ("PID-5", "PID-8", "RXA-20",                                        # sin forma de conducta
            "PID-8-dentro-cuenta", "PID-8-dentro-nota", "OBX-por-ACC", "ACC-PDA-cambiado")   # con forma de conducta (8-nov)


def _inyectar(defecto, marca):
    """Un defecto ajeno a las dos conductas, en el juez de esta carpeta; devuelve cómo deshacerlo."""
    import conversion as CV
    import conversion_vxu as CVX
    if defecto in ("PID-5", "PID-8", "RXA-20"):
        mod, nombre = {"PID-5": (CV, "_patient"), "PID-8": (CV, "_genero"), "RXA-20": (CVX, "_status")}[defecto]
        orig = getattr(mod, nombre)

        def roto(J, *a, **k):
            marca[0] = True
            J.cuenta("valor_distinto", a[-1]("RXA", 20) if defecto == "RXA-20" else defecto, "defecto inyectado por el control del rejuicio")
            return orig(J, *a, **k)
    elif defecto.startswith("PID-8-dentro"):     # un hallazgo con forma de conducta 1, en un PID-8 dentro de la 0001
        mod, nombre = CV, "_genero"
        orig = CV._genero

        def roto(J, m, v, obs):
            if v and obs is not None and CV.mapa("0001", v) != CV.FUERA:
                marca[0] = True
                if defecto.endswith("cuenta"):
                    J.cuenta("fhir_invalido", "PID-8", "Patient.gender: %r fuera de administrative-gender (required)" % obs)
                else:
                    J.nota("convencion", "PID-8", "Patient.gender: %r para %r, fuera del ConceptMap (la 0001 es user-defined)" % (obs, v),
                           citas=CV.CIT_0001)
            return orig(J, m, v, obs)
    else:                                        # una Observation con forma de conducta 2 que no lo es
        mod, nombre = CV, "_origen_sin_mapa"
        orig = CV._origen_sin_mapa

        def roto(m, r):
            sm = orig(m, r)
            if defecto == "OBX-por-ACC" and sm is None:          # la de un OBX, dada por de ACC con el ACC-1 del mensaje
                acc = [s for s in m.segs if s.split(m.f)[0] == "ACC"]
                v = CV._t(m, CV._f(m, acc[0], 1), 1) if acc else ""
                if v:
                    marca[0] = True
                    return "ACC", "ACC-1 = %r" % v
            if defecto == "ACC-PDA-cambiado" and sm and "/" not in sm[0]:   # la de ACC dada por de PDA, y al revés
                marca[0] = True
                return ("PDA" if sm[0] == "ACC" else "ACC"), sm[1]
            return sm
    setattr(mod, nombre, roto)
    return lambda: setattr(mod, nombre, orig)


def main(modo, base, salida, *carpetas):
    if modo == "control":
        res = {}
        for defecto in DEFECTOS:
            res[defecto] = pasada("control", base, None, carpetas, defecto)
        json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
        ok = all(r["control"]["con_defecto"] > 0 and r["control"]["con_defecto"] == r["control"]["con_defecto_y_fuera"] for r in res.values())
        print("control: %s" % ("PASA (las %d pasadas)" % len(DEFECTOS) if ok else "NO PASA"))
        return 0 if ok else 1
    if modo != "comparar":
        raise SystemExit(__doc__)
    res = pasada(modo, base, salida, carpetas)
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
    por = collections.Counter()
    ev_conducta = collections.Counter()
    fuera, punto_cambia, vistas, n, n_dif = [], [], set(), 0, 0
    marcadas, marcadas_fuera = 0, 0
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
        c = clasificar(json.loads(a["guardado"]), json.loads(ahora["guardado"]), e.get("mensaje") or "", a["punto"])
        if marca[0]:
            marcadas += 1
            marcadas_fuera += c == {"fuera"}
        if not c:
            continue
        n_dif += 1
        clave = "+".join(sorted(c))
        por[(clave, _conversor(ruta), _carpeta(ruta), a["punto"])] += 1
        ev_conducta[clave] += 1
        if c == {"fuera"} and modo == "comparar":
            ga, gb = json.loads(a["guardado"]), json.loads(ahora["guardado"])
            ka = {_clave(h) for h in ga["hallazgos"]}
            kb = {_clave(h) for h in gb["hallazgos"]}
            fuera.append({"evidencia": ruta, "punto": a["punto"], "conversor": _conversor(ruta),
                          "veredicto": [ga["veredicto"], gb["veredicto"]],
                          "salen": [json.loads(k) for k in ka - kb], "entran": [json.loads(k) for k in kb - ka]})
    faltan = sorted(set(antes) - vistas)
    res = {"modo": modo, "juez_ahora": M._version()["huella"], "evidencias": n, "diferencias": n_dif,
           "por_conducta": dict(sorted(ev_conducta.items())),
           "detalle": [{"conducta": k[0], "conversor": k[1], "carpeta": k[2], "punto": k[3], "evidencias": v} for k, v in sorted(por.items())],
           "fuera": fuera[:200], "n_fuera": len(fuera), "faltan": faltan[:50], "n_faltan": len(faltan),
           "punto_cambia": punto_cambia[:50], "n_punto_cambia": len(punto_cambia)}
    if deshacer:
        deshacer()
    if modo == "control":
        res["control"] = {"defecto": defecto, "con_defecto": marcadas, "con_defecto_y_fuera": marcadas_fuera}
        res.pop("fuera")
    if salida:
        json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print("rejuicio jz (%s%s): %d evidencias, %d diferencias %s; faltan %d, punto cambia %d; juez %s" % (
        modo, " " + defecto if defecto else "", n, n_dif, dict(sorted(ev_conducta.items())), len(faltan), len(punto_cambia),
        res["juez_ahora"][:12]))
    if modo == "control":
        print("  %d evidencias con el defecto, %d de ellas «fuera»" % (marcadas, marcadas_fuera))
    for f in fuera[:10] if modo == "comparar" else []:
        print("  FUERA %s" % json.dumps(f, ensure_ascii=False)[:400])
    return res


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
