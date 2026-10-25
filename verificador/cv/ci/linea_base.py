#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 23 (cv/ci/diseno-ci-fable.md §2; decisiones de Jev en cv/ci/decision-jev-qci.md): la línea base de un conversor para la
integración continua. Crea la base desde una corrida de cv/verificar_conversor.py y compara una corrida con ella con una regla
asimétrica: falla un hallazgo que no estaba en la base de ese caso; lo que desaparece es un arreglo. No toca la herramienta ni el
juez (S-CI-2). Solo biblioteca estándar.

  python3 cv/ci/linea_base.py crear <corrida> -o <LINEA-BASE.json> [--permitir-sin-evidencia]
  python3 cv/ci/linea_base.py comparar <corrida> <LINEA-BASE.json> [--esperar pasa|igual|falla] [--hallazgo-esperado <JSON>]
                                       [--rc-herramienta N] [--github-output <fichero>] [-o <carpeta>] [--actualizar]
  python3 cv/ci/linea_base.py fijar-imagen <adaptador> <repo[:etiqueta]@sha256:…|""> -o <copia> [--etiquetar]

Códigos: 0 el veredicto es el esperado; 2 entrada inválida; 10 el veredicto no es el esperado; 1 error interno."""
import argparse
import json
import os
import re
import sys

CI_D = os.path.dirname(os.path.abspath(__file__))
CVD = os.path.dirname(CI_D)
FORMATO = "linea-base-ci/1"
DIGEST_RE = re.compile(r"^(?P<repo>[a-z0-9][a-z0-9._/-]*?)(?::(?P<etiqueta>[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}))?@(?P<digest>sha256:[0-9a-f]{64})$")
FALLAN_EN_PASA = ("hallazgo_nuevo", "salida_perdida", "indeterminado_nuevo", "caja")


class EntradaInvalida(Exception):
    pass


def _leer(ruta):
    return json.load(open(ruta, encoding="utf-8"))


def _escribir(ruta, d):
    os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as g:
        g.write(json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True) + "\n")


def _valor(f):
    """Q-VC-D-7, como verificar_conversor._valor: estado, categoría, subtipo y {(hecho, clase, subtipo)} de lo que cuenta."""
    return {"estado": f["estado"], "categoria": f["categoria"], "subtipo": f.get("subtipo"),
            "hallazgos": sorted({(h["hecho"], h["clase"], h["subtipo"]) for h in f["cuentan"]})}


def _json(x):
    return json.loads(json.dumps(x))


# ---------------------------------------------------------------------------- crear (§2.1-2.2)
def crear(corrida, permitir_sin_evidencia=False):
    for f in ("CORRIDA.json", "INFORME.json", "juicio.jsonl", "ADAPTADOR.json"):
        if not os.path.exists(os.path.join(corrida, f)):
            raise EntradaInvalida("la carpeta no es de una corrida de la herramienta: falta %s" % f)
    inf, ad = _leer(os.path.join(corrida, "INFORME.json")), _leer(os.path.join(corrida, "ADAPTADOR.json"))
    sin = (inf.get("no_juzgado") or {}).get("sin_evidencia") or []
    if sin and not permitir_sin_evidencia:
        raise EntradaInvalida("la corrida tiene %d casos sin evidencia (la caja falló): no se crea una base de ahí" % len(sin))
    filas = [json.loads(x) for x in open(os.path.join(corrida, "juicio.jsonl"), encoding="utf-8") if x.strip()]
    casos = {"%s/%s" % (f["corpus"], f["caso"]): _json(_valor(f)) for f in filas}
    conv = inf["conversor"]
    co = inf.get("corpus") or {}
    base = {"formato": FORMATO,
            "creada_de": {"herramienta": {k: inf["herramienta"].get(k) for k in ("version", "huella")},
                          "juez": {k: inf["juez"].get(k) for k in ("huella", "servidor")}},
            "conversor": {"id": conv.get("id"), "nombre": conv.get("nombre"), "version": conv.get("version"), "huella": conv.get("huella"),
                          "huella_con_nombres": conv.get("huella_con_nombres"), "imagen": conv.get("imagen"),
                          "imagen_digest": conv.get("imagen_digest"), "modo": ad["invocacion"]["modo"],
                          "contenedor": ad["invocacion"].get("contenedor")},
            "corpus": {"huella": co.get("huella"), "n": co.get("n"), "por_corpus": co.get("por_corpus")},
            "casos": casos, "n_casos": len(casos)}
    if sin:
        base["creada_de"]["sin_evidencia"] = sorted(sin) if all(isinstance(x, str) for x in sin) else len(sin)
    return base


# ---------------------------------------------------------------------------- comparar (§2.3)
def _clasificar(B, C):
    """-> (lo del caso, sus triples nuevos, sus arreglos)."""
    nuevos = [t for t in C["hallazgos"] if t not in B["hallazgos"]]
    fuera = [t for t in B["hallazgos"] if t not in C["hallazgos"]]
    eventos = []
    if nuevos:
        eventos.append("hallazgo_nuevo")
    if B["estado"] == "bundle" and C["estado"] != "bundle":
        eventos.append("salida_perdida")
    if C["categoria"] == "indeterminado" and B["categoria"] != "indeterminado":
        eventos.append("indeterminado_nuevo")
    arreglo = bool(fuera) or (B["estado"] != "bundle" and C["estado"] == "bundle") or (B["categoria"] != "correcto" and C["categoria"] == "correcto")
    if arreglo and not nuevos and "salida_perdida" not in eventos and "indeterminado_nuevo" not in eventos:
        eventos.append("arreglo")
    if not eventos:
        if B["subtipo"] != C["subtipo"] and B["categoria"] == C["categoria"] and B["estado"] == C["estado"]:
            eventos.append("nota")
        elif B["estado"] != C["estado"] or B["categoria"] != C["categoria"]:
            eventos.append("cambio_de_categoria")
    return eventos, nuevos, fuera


def comparar(corrida, base, esperar="pasa", hallazgo_esperado=None, rc_herramienta=0):
    if base.get("formato") != FORMATO:
        raise EntradaInvalida("la línea base no es %s" % FORMATO)
    actual = crear(corrida, permitir_sin_evidencia=True)
    if actual["conversor"]["id"] != base["conversor"]["id"]:
        raise EntradaInvalida("conversor_distinto: la base es de %s y la corrida de %s" % (base["conversor"]["id"], actual["conversor"]["id"]))
    B, C = base["casos"], actual["casos"]
    v = {"formato": "veredicto-ci/1", "esperado": esperar, "nuevos": [], "nuevos_distintos": [], "arreglos": [], "casos_nuevos": [],
         "casos_ausentes": [], "salida_perdida": [], "indeterminado_nuevo": [], "notas": [], "cambios_de_categoria": [], "avisos": {}}
    distintos = set()
    for k in sorted(set(B) | set(C)):
        if k not in B:
            v["casos_nuevos"].append({"caso": k, "hallazgos": C[k]["hallazgos"]})        # Q-RV… Q-CI-D-1 (Jev: lista)
            continue
        if k not in C:
            v["casos_ausentes"].append(k)                                               # Q-CI-D-2 (Jev: aviso)
            continue
        eventos, nuevos, fuera = _clasificar(B[k], C[k])
        for t in nuevos:
            v["nuevos"].append({"caso": k, "hecho": t[0], "clase": t[1], "subtipo": t[2]})
            distintos.add(tuple(t))
        if "arreglo" in eventos:
            v["arreglos"].append({"caso": k, "fuera": fuera})
        for e, lista in (("salida_perdida", "salida_perdida"), ("indeterminado_nuevo", "indeterminado_nuevo"), ("nota", "notas"),
                         ("cambio_de_categoria", "cambios_de_categoria")):
            if e in eventos:
                v[lista].append(k)
    v["nuevos_distintos"] = [list(t) for t in sorted(distintos)]
    caja = rc_herramienta == 4 or bool((actual["creada_de"].get("sin_evidencia")))
    motivos = [m for m, hay in (("hallazgo_nuevo", v["nuevos"]), ("salida_perdida", v["salida_perdida"]),
                                ("indeterminado_nuevo", v["indeterminado_nuevo"]), ("caja", caja)) if hay]
    if v["casos_ausentes"]:
        v["avisos"]["caso_ausente"] = len(v["casos_ausentes"])
    for clave, b, a in (("juez_distinto", base["creada_de"]["juez"]["huella"], actual["creada_de"]["juez"]["huella"]),
                        ("corpus_distinto", base["corpus"].get("huella"), actual["corpus"].get("huella")),
                        ("huella_distinta", base["conversor"].get("huella"), actual["conversor"].get("huella")),
                        ("imagen_distinta", base["conversor"].get("imagen_digest"), actual["conversor"].get("imagen_digest"))):
        if b != a:
            v["avisos"][clave] = {"base": b, "corrida": a}
    regresion = bool(motivos)
    if esperar == "pasa":
        ok = not regresion
    elif esperar == "igual":
        diferencias = (v["nuevos"] or v["arreglos"] or v["casos_nuevos"] or v["casos_ausentes"] or v["salida_perdida"] or v["indeterminado_nuevo"]
                       or v["notas"] or v["cambios_de_categoria"] or caja or any(k for k in v["avisos"] if k not in ("huella_distinta",)))
        ok = not diferencias
    elif esperar == "falla":
        esperado = sorted(tuple(t) for t in (hallazgo_esperado or []))
        ok = (bool(v["nuevos"]) and sorted(distintos) == esperado and not v["casos_ausentes"] and not v["salida_perdida"]
              and not v["indeterminado_nuevo"] and not caja)
    else:
        raise EntradaInvalida("esperar: pasa, igual o falla")
    v.update({"motivos": motivos, "resultado": "falla" if regresion else "pasa", "pasa": not regresion, "veredicto_esperado": ok,
              "identidades": {"juez": actual["creada_de"]["juez"]["huella"], "herramienta": actual["creada_de"]["herramienta"]["huella"],
                              "huella": actual["conversor"]["huella"], "huella_con_nombres": actual["conversor"]["huella_con_nombres"],
                              "imagen_digest": actual["conversor"]["imagen_digest"], "corpus": actual["corpus"]["huella"]},
              "n": {"base": len(B), "corrida": len(C), "comparados": len(set(B) & set(C))}})
    propuesta = dict(actual)
    if "juez_distinto" in v["avisos"]:
        propuesta["juez_cambiado"] = True                                               # Q-CI-D-4 (Jev: aviso_marcado)
    return v, propuesta


def resumen_md(v, base):
    c = base["conversor"]
    ids = v["identidades"]
    L = ["## Verificador: %s · %s · **%s**" % (c["id"], v["esperado"], "PASA" if v["pasa"] else "FALLA"), "", "| | |", "|---|---|",
         "| Veredicto esperado | %s |" % ("sí" if v["veredicto_esperado"] else "no"),
         "| Hallazgos nuevos | %d (%d triples distintos) |" % (len(v["nuevos"]), len(v["nuevos_distintos"])),
         "| Arreglos | %d |" % len(v["arreglos"]),
         "| Casos nuevos / ausentes | %d / %d |" % (len(v["casos_nuevos"]), len(v["casos_ausentes"])),
         "| Salida perdida / indeterminado nuevo | %d / %d |" % (len(v["salida_perdida"]), len(v["indeterminado_nuevo"])),
         "| Caja | %s |" % ("falló" if "caja" in v["motivos"] else "bien"),
         "| Casos comparados | %d de %d (base %d) |" % (v["n"]["comparados"], v["n"]["corrida"], v["n"]["base"]),
         "| Conversor | huella `%s` (base `%s`) |" % ((ids["huella"] or "")[:16], (c.get("huella") or "")[:16]),
         "| Imagen | `%s` |" % (ids["imagen_digest"] or "—"),
         "| Juez | `%s` (base `%s`) |" % ((ids["juez"] or "")[:16], (base["creada_de"]["juez"]["huella"] or "")[:16]), ""]
    if v["nuevos"]:
        L += ["### Hallazgos nuevos (hasta 50)", "", "| caso | hecho | clase | subtipo |", "|---|---|---|---|"]
        L += ["| %s | %s | %s | %s |" % (x["caso"], x["hecho"], x["clase"], x["subtipo"]) for x in v["nuevos"][:50]] + [""]
    if v["arreglos"]:
        L += ["### Arreglos (hasta 50)", ""] + ["- %s: %s" % (x["caso"], ", ".join(" ".join(t) for t in x["fuera"]) or "sale mejor") for x in v["arreglos"][:50]] + [""]
    if v["casos_nuevos"] or v["casos_ausentes"]:
        L += ["### Casos nuevos y ausentes", ""] + ["- nuevo: %s" % x["caso"] for x in v["casos_nuevos"][:50]] + \
             ["- ausente: %s" % x for x in v["casos_ausentes"][:50]] + [""]
    if v["avisos"]:
        L += ["### Avisos", ""] + ["- %s" % k for k in sorted(v["avisos"])] + [""]
    return "\n".join(L)


# ---------------------------------------------------------------------------- fijar-imagen (§3.2)
def _repo(imagen):
    """El repositorio de una referencia de imagen, sin etiqueta ni digest (la etiqueta va tras el último «/»)."""
    sin = imagen.split("@")[0]
    ultimo = sin.rsplit("/", 1)[-1]
    return sin[:len(sin) - len(ultimo)] + ultimo.split(":")[0]


def fijar_imagen(adaptador, imagen, salida, etiquetar=False):
    ad = _leer(adaptador)
    caja = ad.get("caja") or {}
    if caja.get("tipo") != "docker":
        if imagen:
            raise EntradaInvalida("el adaptador no es de Docker y se dio una imagen")
        _escribir_tal_cual(salida, ad)
        return None
    m = DIGEST_RE.match(imagen or "")
    if not m:
        raise EntradaInvalida("la imagen tiene que llevar digest: repo[:etiqueta]@sha256:<64 hex>")
    repo_ad = _repo(caja["imagen"])
    if m.group("repo") != repo_ad:
        raise EntradaInvalida("la imagen es de %s y el adaptador pide %s" % (m.group("repo"), repo_ad))
    ad["caja"]["imagen_digest"] = m.group("digest")
    _escribir_tal_cual(salida, ad)
    if not etiquetar:
        return None
    if "@sha256:" in caja["imagen"]:
        return "true"
    return "docker tag %s@%s %s" % (m.group("repo"), m.group("digest"), caja["imagen"])


def _escribir_tal_cual(ruta, d):
    os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as g:
        g.write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")


# ---------------------------------------------------------------------------- las órdenes
def main(argv=None):
    p = argparse.ArgumentParser(prog="linea_base")
    sub = p.add_subparsers(dest="orden")
    c = sub.add_parser("crear")
    c.add_argument("corrida")
    c.add_argument("-o", required=True)
    c.add_argument("--permitir-sin-evidencia", action="store_true")
    k = sub.add_parser("comparar")
    k.add_argument("corrida")
    k.add_argument("base")
    k.add_argument("--esperar", default="pasa")
    k.add_argument("--hallazgo-esperado", default="[]")
    k.add_argument("--rc-herramienta", type=int, default=0)
    k.add_argument("--github-output")
    k.add_argument("-o")
    k.add_argument("--actualizar", action="store_true")
    f = sub.add_parser("fijar-imagen")
    f.add_argument("adaptador")
    f.add_argument("imagen")
    f.add_argument("-o", required=True)
    f.add_argument("--etiquetar", action="store_true")
    a = p.parse_args(argv)
    try:
        if a.orden == "crear":
            _escribir(a.o, crear(a.corrida, a.permitir_sin_evidencia))
            return 0
        if a.orden == "fijar-imagen":
            t = fijar_imagen(a.adaptador, a.imagen, a.o, a.etiquetar)
            if t:
                print(t)
            return 0
        if a.orden == "comparar":
            base = _leer(a.base)
            v, propuesta = comparar(a.corrida, base, a.esperar, json.loads(a.hallazgo_esperado or "[]"), a.rc_herramienta)
            out = a.o or a.corrida
            os.makedirs(out, exist_ok=True)
            _escribir(os.path.join(out, "VEREDICTO-CI.json"), v)
            open(os.path.join(out, "VEREDICTO-CI.md"), "w", encoding="utf-8").write(resumen_md(v, base))
            _escribir(os.path.join(out, "LINEA-BASE-propuesta.json"), propuesta)
            if a.github_output:
                with open(a.github_output, "a", encoding="utf-8") as g:
                    for k_, val in (("resultado", v["resultado"]), ("nuevos", len(v["nuevos"])),
                                    ("nuevos_distintos", json.dumps(v["nuevos_distintos"])), ("arreglos", len(v["arreglos"])),
                                    ("huella", v["identidades"]["huella"]), ("imagen_digest", v["identidades"]["imagen_digest"] or ""),
                                    ("juez", v["identidades"]["juez"])):
                        g.write("%s=%s\n" % (k_, val))
            print("linea_base: %s (%s); nuevos %d, arreglos %d, casos nuevos %d, ausentes %d" % (
                v["resultado"], "lo esperado" if v["veredicto_esperado"] else "NO es lo esperado", len(v["nuevos"]), len(v["arreglos"]),
                len(v["casos_nuevos"]), len(v["casos_ausentes"])))
            if a.actualizar:
                _escribir(a.base, propuesta)
                return 0
            return 0 if v["veredicto_esperado"] else 10
        p.print_help()
        return 2
    except EntradaInvalida as ex:
        print("linea_base: %s" % ex)
        return 2
    except (OSError, ValueError, KeyError) as ex:
        print("linea_base: error: %s" % ex)
        return 1


if __name__ == "__main__":
    sys.exit(main())
