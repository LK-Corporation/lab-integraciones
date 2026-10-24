#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 18, VC3 (cv/vc/diseno-vc-fable.md §6): el control de cv/verificar_conversor.py con los dos conversores del estudio.
El eslabón débil primero: 0) el juguete dentro de Docker da lo mismo que fuera; 1) identidades (huellas de los conversores, del
juez y del corpus) antes de correr nada; 2) las dos corridas con --comparar contra el juicio de CV4, caso por caso; 3) las
comprobaciones que valen desde lo público (agregados de RESULTADO-CV2.json y pares mínimos de RESULTADO-CV3-minimos.json y, si
está, de RESULTADO-15A-minimos-fijada.json, que es privado); 4) los informes sin las muestras. El juicio de CV4 solo lo lee el
paso 2: si no se corre, el argumento puede ser cualquier fichero.

  python3 cv/vc/control_vc.py <artefactos> <muestras> <juicio CV4.jsonl> <salida> [microsoft|linuxforhealth|juguete ...]

Escribe <salida>/CONTROL-VC.json; las corridas quedan en <salida>/<id>/."""
import io
import json
import os
import sys
from contextlib import redirect_stdout

AQUI = os.path.dirname(os.path.abspath(__file__))
CVD = os.path.dirname(AQUI)
FASE = os.path.dirname(CVD)
sys.path[:0] = [CVD, FASE]
import verificar_conversor as VC  # noqa: E402
sys.argv_guardado, sys.argv = sys.argv, ["x"]
from prueba_conversion import msg, oru_msg  # noqa: E402
sys.argv = sys.argv_guardado

ESPERADO = {"juez": "40bbc3ef", "microsoft": "766f8938d0c12c382bec2edceeca4d3be4fd19900d0bd131ba880ac615fadf3e",
            "linuxforhealth": "ac41f71b98ee75bac637ecd4b68f58b463f0798bf66cfa941f4194cb2a50acf2", "corpus_cv2": "aa83359a"}


def con_msh8(t, d):
    segs = t.split("\r")
    p = segs[0].split("|")
    p += [""] * max(0, 8 - len(p))
    p[7] = d
    segs[0] = "|".join(p)
    return "\r".join(segs)


SEIS = {"n": con_msh8(msg(), "JUGUETE-NOMINAL"), "g": con_msh8(msg(), "JUGUETE-GENERO"), "e": con_msh8(msg(), "JUGUETE-ERROR"),
        "v": con_msh8(msg(), "JUGUETE-NADA"), "a05": con_msh8(msg("A05"), "JUGUETE-NOMINAL"), "o": con_msh8(oru_msg(), "JUGUETE-NOMINAL")}


def main_vc(args):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = VC.main(args)
    return rc, buf.getvalue()


def filas(salida):
    return [json.loads(x) for x in open(os.path.join(salida, "juicio.jsonl"), encoding="utf-8")]


def paso0(salida):
    c = os.path.join(salida, "seis")
    os.makedirs(c, exist_ok=True)
    for k, t in SEIS.items():
        open(os.path.join(c, k + ".hl7"), "w", encoding="utf-8", newline="").write(t)
    res = {}
    for nombre, ad in (("local", os.path.join(CVD, "adaptadores", "juguete.json")), ("docker", os.path.join(AQUI, "juguete-docker.json"))):
        s = os.path.join(salida, "juguete-" + nombre)
        rc, out = main_vc([ad, s, "--artefactos", CVD, "--sin-corpus-lab", "--corpus", c])
        res[nombre] = {"rc": rc, "veredictos": {f["caso"]: [f["estado"], f["categoria"], f["subtipo"], sorted({(h["hecho"], h["clase"], h["subtipo"]) for h in f["cuentan"]})]
                                                for f in filas(s)}}
    res["iguales"] = json.loads(json.dumps(res["local"]["veredictos"])) == json.loads(json.dumps(res["docker"]["veredictos"]))
    return res


def paso1(artefactos, muestras, salida):
    r = {"juez": VC.M._version()["huella"]}
    for cv in ("microsoft", "linuxforhealth"):
        ad = VC.leer_adaptador(os.path.join(CVD, "adaptadores", cv + ".json"), artefactos)
        r[cv] = VC.huella(ad, artefactos)
    co = VC.generar_corpus(os.path.join(salida, "corpus-identidad"), lab=True, minimos=True, muestras=muestras)
    man = dict(reversed(x.split("  ", 1)) for x in open(os.path.join(CVD, "CORPUS-CV2-MANIFIESTO.txt")).read().split("\n") if x)
    gen = dict(reversed(x.split("  ", 1)) for x in open(os.path.join(salida, "corpus-identidad", "MANIFIESTO.txt")).read().split("\n") if x)
    r["manifiesto"] = {"lineas_estudio": len(man), "iguales": sum(1 for k, v in man.items() if gen.get(k) == v),
                       "distintas": sorted(k for k, v in man.items() if gen.get(k) != v)}
    r["corpus_cv2"] = co["huella_adt_oru_muestras"]
    r["n"] = co["n"]
    r["cuadra"] = (r["juez"].startswith(ESPERADO["juez"]) and r["microsoft"] == ESPERADO["microsoft"] and
                   r["linuxforhealth"] == ESPERADO["linuxforhealth"] and r["corpus_cv2"].startswith(ESPERADO["corpus_cv2"]) and
                   not r["manifiesto"]["distintas"])
    return r


def paso2(cv, artefactos, muestras, juicio_cv4, salida):
    ref = os.path.join(salida, "referencia-%s.jsonl" % cv)
    with open(ref, "w", encoding="utf-8") as g:
        for x in open(juicio_cv4, encoding="utf-8"):
            if json.loads(x)["conversor"] == cv:
                g.write(x)
    s = os.path.join(salida, cv)
    rc, out = main_vc([os.path.join(CVD, "adaptadores", cv + ".json"), s, "--artefactos", artefactos, "--muestras", muestras,
                       "--comparar", ref])
    c = json.load(open(os.path.join(s, "CONTROL.json"), encoding="utf-8"))
    inf = json.load(open(os.path.join(s, "INFORME.json"), encoding="utf-8"))
    return {"rc": rc, "ultima_linea": out.strip().split("\n")[-1], "diferencias": c["diferencias"],
            "solo_en_corrida": c["solo_en_corrida"], "solo_en_referencia": c["solo_en_referencia"],
            "por_corpus": {k: v["categorias"] for k, v in inf["por_corpus"].items()},
            "pares": {d["id"]: d["reproduce"] for d in inf["pares_minimos"]["detalle"]} if inf["pares_minimos"]["aplica"] else None,
            "sin_evidencia": inf["no_juzgado"]["sin_evidencia"], "conversor": inf["conversor"]}


def paso3(r):
    """Lo público: categorías por corpus frente a RESULTADO-CV2.json; pares frente a RESULTADO-CV3-minimos.json (público, juez
    de CV3) y, si está, frente a RESULTADO-15A-minimos-fijada.json (privado, juez de CV4)."""
    cv2 = json.load(open(os.path.join(CVD, "RESULTADO-CV2.json"), encoding="utf-8"))["por_conversor"]
    fij = os.path.join(CVD, "RESULTADO-15A-minimos-fijada.json")
    pares = {p["id"]: p for p in json.load(open(fij, encoding="utf-8"))["pares"]} if os.path.exists(fij) else {}
    if not pares:
        print("aviso: no está %s (privado); los pares se comparan solo con RESULTADO-CV3-minimos.json" % os.path.basename(fij), flush=True)
    cv3 = {p["id"]: p for p in json.load(open(os.path.join(CVD, "RESULTADO-CV3-minimos.json"), encoding="utf-8"))["pares"]}
    out = {}
    for cv in ("microsoft", "linuxforhealth"):
        if cv not in r:
            continue
        o = {"categorias": {}}
        for fam in ("adt", "oru", "muestras"):
            a, b = r[cv]["por_corpus"].get(fam, {}), cv2[cv].get(fam, {}).get("categorias", {})
            o["categorias"][fam] = {"iguales": a == b, "herramienta": a, "cv2": b}
        if r[cv]["pares"] is not None and pares:
            o["pares"] = {pid: {"herramienta": r[cv]["pares"].get(pid), "cv4_fijada": p["confirmada"]}
                          for pid, p in pares.items() if p["conversor"] == cv and r[cv]["pares"].get(pid) != p["confirmada"]}
        if r[cv]["pares"] is not None:
            o["pares_cv3_publico"] = {"de": sum(1 for p in cv3.values() if p["conversor"] == cv),
                                      "distintos": {pid: {"herramienta": r[cv]["pares"].get(pid), "cv3": p["confirmada"]}
                                                    for pid, p in cv3.items() if p["conversor"] == cv and r[cv]["pares"].get(pid) != p["confirmada"]}}
        out[cv] = o
    return out


def paso4(cv, artefactos, salida):
    """Lo que obtiene un tercero desde el repo público: sin las muestras de los proyectos, que no se redistribuyen (L-VC-7)."""
    s = os.path.join(salida, "publico-" + cv)
    rc, out = main_vc([os.path.join(CVD, "adaptadores", cv + ".json"), s, "--artefactos", artefactos])
    inf = json.load(open(os.path.join(s, "INFORME.json"), encoding="utf-8"))
    md = open(os.path.join(s, "INFORME.md"), encoding="utf-8").read()
    return {"rc": rc, "comprobar_informe": VC.comprobar_informe(md, inf), "totales": inf["totales"],
            "por_corpus": {k: v["categorias"] for k, v in inf["por_corpus"].items()},
            "pares": inf["pares_minimos"].get("reproducidos"), "carpeta": os.path.basename(s)}


def main(artefactos, muestras, juicio_cv4, salida, *quien):
    os.makedirs(salida, exist_ok=True)
    quien = quien or ("juguete", "microsoft", "linuxforhealth")
    r = {}
    ruta = os.path.join(salida, "CONTROL-VC.json")
    guarda = lambda: json.dump(r, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=list)  # noqa: E731
    if "juguete" in quien:
        r["paso0"] = paso0(salida)
        guarda()
        print("paso 0, juguete dentro y fuera de Docker: %s" % ("IGUALES" if r["paso0"]["iguales"] else "DISTINTOS"), flush=True)
        if not r["paso0"]["iguales"]:
            return 1
    r["paso1"] = paso1(artefactos, muestras, salida)
    guarda()
    print("paso 1, identidades: %s %s" % ("CUADRAN" if r["paso1"]["cuadra"] else "NO CUADRAN",
                                          {k: v for k, v in r["paso1"].items() if k != "manifiesto"}), flush=True)
    if not r["paso1"]["cuadra"]:
        return 1
    for cv in ("microsoft", "linuxforhealth"):
        if cv in quien:
            r[cv] = paso2(cv, artefactos, muestras, juicio_cv4, salida)
            guarda()
            print("paso 2, %s: rc %d, %d diferencias, %d solo en la corrida, %d solo en la referencia" % (
                cv, r[cv]["rc"], len(r[cv]["diferencias"]), len(r[cv]["solo_en_corrida"]), len(r[cv]["solo_en_referencia"])), flush=True)
    r["paso3"] = paso3(r)
    guarda()
    print("paso 3: %s" % json.dumps({cv: {f: v["iguales"] for f, v in o["categorias"].items()} for cv, o in r["paso3"].items()}), flush=True)
    r["paso4"] = {cv: paso4(cv, artefactos, salida) for cv in ("microsoft", "linuxforhealth") if cv in quien}
    guarda()
    print("paso 4, informes sin muestras: %s" % json.dumps({cv: [v["rc"], v["comprobar_informe"]] for cv, v in r["paso4"].items()}), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
