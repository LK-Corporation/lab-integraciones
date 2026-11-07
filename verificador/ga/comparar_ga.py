#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33 (ANTES-ETAPA-GENERADORES.md, «Qué se rehace»): el aparato que compara lo que dan los dos conversores del estudio con la
versión 1 y con la 2 del corpus, con el mismo juez a los dos lados. No toca la herramienta, ni el juez, ni cv3_clases.py ni
cv3_minimos.py: los usa, con ensamblar y juzgar_arbol de la etapa 21 (cv/ar/arrastre.py).
  python3 ga/comparar_ga.py origenes <carpeta>                       los 37 orígenes de los gemelos, con su MSH-10 por nombre
  python3 ga/comparar_ga.py ruido <A> <B> <salida.json>              dos corridas de la misma versión: lo que cambia sin cambiar nada
  python3 ga/comparar_ga.py comparar <MS1> <LFH1> <MS2> <LFH2> <ruido.json>,... <trabajo>   -> <trabajo>/COMPARACION-GA.json
  python3 ga/comparar_ga.py gemelos <MSo> <LFHo> <MSg> <LFHg> <salida.json>                  las 12, en sus gemelos
<MSn>/<LFHn>: carpetas de corridas de cv/verificar_conversor.py (con --version-corpus n). Los gemelos y sus orígenes van como
--corpus, con --sin-corpus-lab y --sin-minimos."""
import collections
import glob
import json
import os
import re
import sys

GA = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(GA)
CVD = os.path.join(FASE, "cv")
sys.path[:0] = [GA, FASE, CVD, os.path.join(CVD, "ar"), os.path.join(FASE, "au")]


def _silencio():
    a, sys.argv = sys.argv, ["x", "--silencio"]
    return a


def filas(corrida):
    return {(f["corpus"], f["caso"]): f for f in map(json.loads, open(os.path.join(corrida, "juicio.jsonl"), encoding="utf-8"))}


def huellas(corrida):
    """{(corpus, caso): sha256 del mensaje} del MANIFIESTO del corpus de la corrida."""
    out = {}
    for l in open(os.path.join(corrida, "corpus", "MANIFIESTO.txt"), encoding="utf-8"):
        if l.strip():
            s, f = l.split("  ", 1)
            c, n = f.strip().split("/", 1)
            out[(c, os.path.splitext(n)[0])] = s
    return out


def valor(f):
    """Lo que se compara de un caso: categoría, subtipo y lo que cuenta (hecho, clase, subtipo, firma)."""
    return [f.get("categoria"), f.get("subtipo"), sorted({(h.get("hecho"), h.get("clase"), h.get("subtipo"), h.get("firma"))
                                                         for h in f.get("cuentan") or []})]


def cid(corrida):
    return os.path.basename(glob.glob(os.path.join(corrida, "evidencias", "*"))[0])


# ---------------------------------------------------------------------------- orígenes
def origenes(carpeta):
    a = _silencio()
    import hacer_resto_v2 as R
    sys.argv = a
    os.makedirs(carpeta)
    textos = R.origenes()
    for o in R.ORIGENES:
        t = textos[o].decode("utf-8")
        msh10 = t.split("\r")[0].split("|")[9]
        open(os.path.join(carpeta, msh10 + ".hl7"), "w", encoding="utf-8", newline="").write(t)
    print("%d orígenes en %s" % (len(R.ORIGENES), carpeta))


# ---------------------------------------------------------------------------- ruido
def ruido(a, b, salida=None):
    fa, fb = filas(a), filas(b)
    dif = sorted("%s/%s" % k for k in set(fa) & set(fb) if valor(fa[k]) != valor(fb[k]))
    r = {"a": os.path.basename(os.path.normpath(a)), "b": os.path.basename(os.path.normpath(b)), "n": len(set(fa) & set(fb)),
         "distintos": dif, "sin_par": sorted("%s/%s" % k for k in set(fa) ^ set(fb))}      # sin rutas de la máquina
    if salida:
        json.dump(r, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ruido: %d casos, %d distintos, %d sin par" % (r["n"], len(dif), len(r["sin_par"])))
    return r


# ---------------------------------------------------------------------------- comparar
def comparar(ms1, lfh1, ms2, lfh2, ruidos, trabajo):
    os.makedirs(trabajo, exist_ok=True)
    a = _silencio()
    import arrastre as AR
    sys.argv = a
    ruido_ = set()
    for r in [x for x in ruidos.split(",") if x]:
        ruido_ |= set(json.load(open(r, encoding="utf-8"))["distintos"])
    out = {"por_conversor": {}, "ruido_declarado": sorted(ruido_)}
    for conv, c1, c2 in (("microsoft", ms1, ms2), ("linuxforhealth", lfh1, lfh2)):
        f1, f2, h1, h2 = filas(c1), filas(c2), huellas(c1), huellas(c2)
        estado = {}
        for k in set(h1) | set(h2):
            estado[k] = "solo_v1" if k not in h2 else "nuevo" if k not in h1 else "igual" if h1[k] == h2[k] else "cambia"
        res = {"n_v1": len(f1), "n_v2": len(f2), "por_estado": dict(collections.Counter(estado.values())),
               "iguales_distintos": [], "iguales_distintos_ruido": [], "cambian": [], "nuevos": []}
        for k, e in sorted(estado.items()):
            nom = "%s/%s" % k
            if e == "igual":
                if k in f1 and k in f2 and valor(f1[k]) != valor(f2[k]):
                    (res["iguales_distintos_ruido"] if nom in ruido_ else res["iguales_distintos"]).append(nom)
            elif e == "cambia":
                v1, v2 = valor(f1[k]), valor(f2[k])
                s1, s2 = {tuple(x) for x in v1[2]}, {tuple(x) for x in v2[2]}
                res["cambian"].append({"caso": nom, "categoria": [v1[0], v2[0]], "subtipo": [v1[1], v2[1]],
                                       "se_van": sorted(map(list, s1 - s2)), "llegan": sorted(map(list, s2 - s1))})
            elif e == "nuevo":
                v2 = valor(f2[k])
                res["nuevos"].append({"caso": nom, "categoria": v2[0], "subtipo": v2[1], "cuentan": v2[2]})
        res["categorias_que_cambian"] = dict(collections.Counter("%s -> %s" % tuple(x["categoria"]) for x in res["cambian"]
                                                                 if x["categoria"][0] != x["categoria"][1]))
        out["por_conversor"][conv] = res
    datos = {}
    for nombre, ms, lfh in (("v1", ms1, lfh1), ("v2", ms2, lfh2)):
        arbol = AR.ensamblar(os.path.join(trabajo, "arbol-" + nombre), {"microsoft": ms, "linuxforhealth": lfh})
        cl, mi = AR.juzgar_arbol(arbol)
        json.dump(cl, open(os.path.join(trabajo, "CLASES-GA-%s.json" % nombre), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(mi, open(os.path.join(trabajo, "minimos-GA-%s.json" % nombre), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        datos[nombre] = {"clases": cl, "minimos": mi, "por_corpus": {}}
    pub = {"clases": json.load(open(os.path.join(CVD, "CLASES-CV3.json"), encoding="utf-8")),
           "minimos": json.load(open(os.path.join(CVD, "RESULTADO-CV3-minimos.json"), encoding="utf-8")), "por_corpus": {}}
    out["cifras_que_cambian"] = AR.diferencias_cifras(datos["v1"], datos["v2"], pub)
    out["frase"] = {n: datos[n]["clases"].get("frase") for n in datos}
    out["minimos_confirmadas"] = {n: [datos[n]["minimos"].get("confirmadas"), datos[n]["minimos"].get("de")] for n in datos}
    sin1, sin2 = (datos[n]["clases"].get("sin_clase") or {} for n in ("v1", "v2"))
    out["sin_clase"] = {"v1": len(sin1), "v2": len(sin2), "candidatas": {k: v for k, v in sorted(sin2.items()) if k not in sin1},
                        "desaparecen": {k: v for k, v in sorted(sin1.items()) if k not in sin2}}
    out["deriva_del_juez_v1"] = [{"cifra": d["cifra"], "publicado": d["lote"], "con_el_juez_actual": d["mensaje"]}
                                 for d in AR.diferencias_cifras(pub, datos["v1"])]
    json.dump(out, open(os.path.join(trabajo, "COMPARACION-GA.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for conv, r in out["por_conversor"].items():
        print("%s: %s; iguales que cambian %d (ruido %d); cambian %d; nuevos %d; categorías %s" % (
            conv, r["por_estado"], len(r["iguales_distintos"]), len(r["iguales_distintos_ruido"]), len(r["cambian"]),
            len(r["nuevos"]), r["categorias_que_cambian"]))
    print("frase:", json.dumps(out["frase"], ensure_ascii=False))
    print("mínimos:", out["minimos_confirmadas"], "; cifras que cambian:", len(out["cifras_que_cambian"]),
          "; candidatas:", len(out["sin_clase"]["candidatas"]))
    return out


# ---------------------------------------------------------------------------- gemelos
def gemelos(mso, lfho, msg, lfhg, salida):
    a = _silencio()
    import cv3_minimos as MIN
    import cv3_minimos_vxu as MV
    import juzgar_cv2 as J
    import pares_auditoria as PA
    sys.argv = a
    obj = {}
    for pid, conv, _, o in MIN.PARES:
        obj[pid] = ("oru", conv, o)
    for pid, conv, _, o in MV.PARES:
        obj[pid] = ("vxu", conv, o)
    for pid, _, conv, esp, _, _ in PA.PARES:
        obj[pid] = ("au", conv, esp)
    corridas = {("microsoft", "origen"): mso, ("linuxforhealth", "origen"): lfho, ("microsoft", "gemelo"): msg,
                ("linuxforhealth", "gemelo"): lfhg}
    jf = {k: {f["caso"]: f for f in map(json.loads, open(os.path.join(c, "juicio.jsonl"), encoding="utf-8"))} for k, c in corridas.items()}

    def ev(conv, lado, nombre):
        c = corridas[(conv, lado)]
        f = os.path.join(c, "evidencias", cid(c), "propio", nombre + ".json")
        return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else None

    def sale(tipo, o, conv, lado, nombre):
        if lado == "gemelo":
            nombre = nombre + "-ISO"
        if tipo == "au":
            fila = jf[(conv, lado)].get(nombre)
            return None if fila is None else PA.tiene(fila, o)
        e = ev(conv, lado, nombre)
        if e is None:
            return None
        hecho, subtipo, texto = o
        hechos = hecho if isinstance(hecho, tuple) else (hecho,)
        sin_n = lambda x: re.sub(r"\(\d+\)", "", x or "")      # NK1(2)-3 es NK1-3 (DV-GA-5: la sellada no lo quitaba)
        if tipo == "vxu":                                           # la regla de cv3_minimos_vxu._sale, con el hecho sin aparición
            a = _silencio()
            import verificador as V
            sys.argv = a
            hs = [h for h in V.verificar(e)["hallazgos"] if h["cuenta"]]
            return any(sin_n(h["hecho"]) in hechos and subtipo in h["subtipo"].split("+") and any(texto in q for q in h["que"])
                       for h in hs)
        r = J.juzgar(e)
        hs = [h for h in r["hallazgos"] if h["cuenta"]]
        if subtipo == "error":
            return e["conversion"]["salida"]["estado"] != "bundle"
        return any(sin_n(h["hecho"]) in hechos and any(texto in q for q in h["que"]) for h in hs)

    gem ={g["origen"]: g for g in json.load(open(os.path.join(GA, "GEMELOS.json"), encoding="utf-8"))}
    cruce = json.load(open(os.path.join(FASE, "iv", "CRUCE-IV.json"), encoding="utf-8"))["nuevas"]
    res = {}
    for n in cruce:
        if n["con_algun_apoyo_valido"] or n["id"] in ("MD-L5", "MD-M5"):
            continue
        apoyos = n["apoyo"]
        pares = []
        for ap in apoyos:
            b = os.path.basename(ap)[:-4]
            m = re.match(r"^((?:[A-Z]+\d+)(?:-[a-z0-9-]+)?)-caso$", b)
            if m and m.group(1) in obj:
                pares.append((m.group(1), ap))
        par_principal = [p for p in pares if obj[p[0]][0] != "au"][0][0]
        tipo_p, conv, o = obj[par_principal]
        fila = {"conversor": conv, "par": par_principal, "objetivo": list(o), "apoyos": []}
        for ap in apoyos:
            g = gem[ap]
            nombre = g["msh10_origen"]
            b = os.path.basename(ap)[:-4]
            m = re.match(r"^((?:[A-Z]+\d+)(?:-[a-z0-9-]+)?)-caso$", b)
            if m and m.group(1) in obj:
                pid = m.group(1)
                t, cv, oo = obj[pid]
                ctl = [x for x in gem if x.startswith(ap[:-len("caso.hl7")] + "control")]
                d = {"apoyo": ap, "tipo": "par", "par": pid}
                for lado in ("origen", "gemelo"):
                    caso = sale(t, oo, cv, lado, nombre)
                    ctrs = [sale(t, oo, cv, lado, gem[c]["msh10_origen"]) for c in ctl]
                    d[lado] = {"caso": caso, "controles": ctrs, "confirmada": bool(caso) and not any(ctrs)}
            else:
                d = {"apoyo": ap, "tipo": "base"}
                for lado in ("origen", "gemelo"):
                    d[lado] = {"sale": sale(tipo_p, o, conv, lado, nombre)}
            fila["apoyos"].append(d)
        fila["se_reproduce_en_gemelos"] = all(
            (x["gemelo"]["confirmada"] if x["tipo"] == "par" else x["gemelo"]["sale"]) for x in fila["apoyos"])
        fila["igual_que_en_el_origen"] = all(x["origen"] == x["gemelo"] for x in fila["apoyos"])
        res[n["id"]] = fila
    r = {"nuevas": res, "se_reproducen": sorted(k for k, v in res.items() if v["se_reproduce_en_gemelos"]),
         "no": sorted(k for k, v in res.items() if not v["se_reproduce_en_gemelos"]),
         "distintas_del_origen": sorted(k for k, v in res.items() if not v["igual_que_en_el_origen"])}
    json.dump(r, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("se reproducen en sus gemelos: %d de %d %s; no: %s; distintas del origen: %s" % (
        len(r["se_reproducen"]), len(res), r["se_reproducen"], r["no"], r["distintas_del_origen"]))
    return r


if __name__ == "__main__":
    op, args = sys.argv[1], sys.argv[2:]
    {"origenes": origenes, "ruido": ruido, "comparar": comparar, "gemelos": gemelos}[op](*args)
