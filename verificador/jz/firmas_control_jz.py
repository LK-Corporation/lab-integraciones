#!/usr/bin/env python3
"""Etapa 37 (jz/decision-jev-jz3b.md, Q-JZ-8 a): qué cambia en las evidencias de cada pasada del control del rejuicio, para decir qué
las saca «fuera». No toca el clasificador: siembra cada defecto como jz/rejuicio_jz.py control y, de cada evidencia en la que el
defecto se dio, cuenta su firma: los hallazgos que salen y que entran frente a la línea base, como «sale|entra clase/subtipo hecho»,
con el hecho de los campos tal cual y el de los recursos por su segmento.

  python3 jz/firmas_control_jz.py <linea_base.jsonl> <salida.json> <carpeta de evidencias> [...]"""
import collections
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(os.path.dirname(AQUI), "md"), os.path.dirname(AQUI), AQUI]


def main(base, salida, *carpetas):
    _argv, sys.argv = sys.argv, ["x", "--silencio"]
    import rejuicio_md as RM
    import rejuicio_jz as R
    sys.argv = _argv
    antes = {}
    for linea in open(base, encoding="utf-8"):
        x = json.loads(linea)
        antes[x["evidencia"]] = x
    res = {}
    for defecto in R.DEFECTOS:
        marca = [False]
        deshacer = R._inyectar(defecto, marca)
        firmas, n, fuera = collections.Counter(), 0, 0
        try:
            for ruta, e in RM.evidencias(carpetas):
                marca[0] = False
                f = RM.fila(ruta, e)
                if not marca[0]:
                    continue
                n += 1
                a = antes[ruta]
                ga, gb = json.loads(a["guardado"]), json.loads(f["guardado"])
                fuera += R.clasificar(ga, gb, e.get("mensaje") or "", a["punto"]) == {"fuera"}
                ka = collections.Counter(R._clave(h) for h in ga["hallazgos"])
                kb = collections.Counter(R._clave(h) for h in gb["hallazgos"])
                partes = sorted({"%s %s/%s %s" % (lado, h["clase"], h["subtipo"], h["hecho"])
                                 for lado, hs in (("sale", ka - kb), ("entra", kb - ka)) for h in map(json.loads, hs.elements())})
                if ga["veredicto"] != gb["veredicto"]:
                    partes.append("veredicto %s -> %s" % (ga["veredicto"]["categoria"], gb["veredicto"]["categoria"]))
                firmas[" | ".join(partes)] += 1
        finally:
            deshacer()
        res[defecto] = {"con_defecto": n, "fuera": fuera, "firmas": dict(firmas.most_common())}
        print("%s: %d con el defecto, %d fuera; %d firmas; la más común: %s" % (
            defecto, n, fuera, len(firmas), firmas.most_common(1)[0] if firmas else None))
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)


if __name__ == "__main__":
    main(*sys.argv[1:])
