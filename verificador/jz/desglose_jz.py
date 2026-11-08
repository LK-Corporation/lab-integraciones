#!/usr/bin/env python3
"""Etapa 37: el desglose del rejuicio. De cada evidencia que cambia, qué cambia, con el juez de esta carpeta frente a la línea base.

  python3 jz/desglose_jz.py <linea_base.jsonl> <salida.json> <carpeta de evidencias> [...]

Segunda versión (8-nov, tras la revisión a ciegas): la primera daba por «pasa a nota» o «pasa a solo FHIR inválido» lo que ya era
así con el juez de antes. Ahora no hay clases puestas a mano: de cada evidencia, la conducta que le da jz/rejuicio_jz.py y, en la
conducta 1 y la lectura, lo que había en PID-8 o NK1-15 antes y lo que hay después (los subtipos, «nota:» delante de las notas, «+»
si cuentan juntos), y el rechazo; en la conducta 2, los hechos de las Observation sin mapa. Cuenta además los veredictos."""
import collections
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(os.path.dirname(AQUI), "md"), os.path.dirname(AQUI), AQUI]


def _pid8(g):
    import rejuicio_jz as R
    out = []
    for h in g["hallazgos"]:                      # solo PID-8 y NK1(n)-15, no los demás campos de NK1 (segunda pasada de la revisión)
        if h["clase"] != "rechazo" and R.HECHO_1.match(h["hecho"] or ""):
            out.append(("nota:" if h["clase"] == "nota" else "") + h["subtipo"])
    return " y ".join(sorted(out)) or "nada"


def _rechazo(g):
    r = [h for h in g["hallazgos"] if h["clase"] == "rechazo"]
    return r[0]["subtipo"] if r else None


def main(base, salida, *carpetas):
    _argv, sys.argv = sys.argv, ["x", "--silencio"]
    import rejuicio_md as RM
    import rejuicio_jz as R
    sys.argv = _argv
    antes = {}
    for linea in open(base, encoding="utf-8"):
        x = json.loads(linea)
        antes[x["evidencia"]] = x
    tipos, transiciones, ejemplos, hechos_2 = collections.Counter(), collections.Counter(), {}, collections.Counter()
    for ruta, e in RM.evidencias(carpetas):
        a = antes.get(ruta)
        f = RM.fila(ruta, e)
        if a is None or a["guardado"] == f["guardado"]:
            continue
        ga, gb = json.loads(a["guardado"]), json.loads(f["guardado"])
        c = R.clasificar(ga, gb, e.get("mensaje") or "", a["punto"])
        va, vb = ga["veredicto"], gb["veredicto"]
        transiciones["%s/%s -> %s/%s" % (va["categoria"], va["subtipo"], vb["categoria"], vb["subtipo"])] += 1
        partes = []
        if c & {"1", "lectura"}:
            ra, rb = _rechazo(ga), _rechazo(gb)
            if ra or rb:
                partes.append("%s: rechazo %s -> %s" % ("1" if "1" in c else "lectura", ra, rb))
            else:
                partes.append("%s: %s -> %s" % ("1" if "1" in c else "lectura", _pid8(ga), _pid8(gb)))
        if "2" in c:
            hs = sorted({h["hecho"] for h in gb["hallazgos"] if h["subtipo"] == "recurso_sin_mapa"})
            partes.append("2: " + " y ".join(hs))
            for h in gb["hallazgos"]:
                if h["subtipo"] == "recurso_sin_mapa":
                    hechos_2[h["hecho"]] += len(h["que"])
        if "fuera" in c:
            partes.append("fuera")
        k = " | ".join(partes)
        tipos[k] += 1
        ejemplos.setdefault(k, ruta)
    res = {"tipos": dict(sorted(tipos.items())), "veredictos": dict(sorted(transiciones.items())),
           "observation_sin_mapa_por_hecho": dict(sorted(hechos_2.items())), "un_ejemplo_por_tipo": ejemplos}
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in res.items() if k != "un_ejemplo_por_tipo"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
