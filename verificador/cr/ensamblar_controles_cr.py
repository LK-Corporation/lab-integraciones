#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 35 (DV-CR-4): junta en un JSON lo que dejó cr/controles_cr.sh en <carpeta>/res/: por control, el código, el esperado, las
rutas que difieren en cada flujo, si salió como se esperaba, los segundos, la última línea y PUBLICADO.json entero, con las rutas
hechas relativas a la carpeta. Para si alguna ruta de la máquina queda dentro. Con la primera tanda reproduce cr/CONTROLES-CR.json
byte a byte.
  python3 cr/ensamblar_controles_cr.py <carpeta de los controles> <salida.json> [segunda]"""
import json
import re
import sys

LECTURA = {
    None: ("Etapa 35, cr/controles_cr.sh: un remoto de prueba local hecho del clon del público en 464bbb2, una copia con una línea "
           "añadida a verificador/cv/ci/CI.md en el índice, los tres flujos ensayados una vez sobre él y tres pushes al remoto de "
           "prueba, cada uno comprobado. Las rutas, relativas a la carpeta de los controles."),
    "segunda": ("Etapa 35, la segunda tanda de cr/controles_cr.sh, con la comprobación de después de la revisión a ciegas (DV-CR-3): "
                "lo mismo que la primera, sobre un remoto de prueba local hecho del clon del público en 464bbb2. Las rutas, relativas "
                "a la carpeta de los controles."),
}
ESPERADO = {"negativo": (0, None), "positivo-add": (1, ["A\tverificador/DE-MAS-35.txt"]),
            "positivo-amend": (1, ["M\tverificador/cv/ci/CI.md"])}


def main(carpeta, salida, tanda=None):
    carpeta = carpeta.rstrip("/")
    R = carpeta + "/res"
    out = {"_lectura": LECTURA[tanda], "controles": {}}
    codigos = {l.split()[0]: l.split()[1:] for l in open(R + "/CODIGOS.txt")}
    for n, (rc, dif) in ESPERADO.items():
        p = json.loads(open("%s/%s/PUBLICADO.json" % (R, n), encoding="utf-8").read().replace(carpeta + "/", ""))
        difs = {f: v.get("diferencia") for f, v in p["flujos"].items()}
        bien = p["codigo"] == rc and all(d == dif for d in difs.values())
        out["controles"][n] = {"codigo": p["codigo"], "esperado": rc, "diferencias": difs, "como_se_esperaba": bien,
                               "segundos": codigos[n][1].split("=")[1],
                               "ultima_linea": open("%s/%s.salida.txt" % (R, n)).read().strip().splitlines()[-1], "publicado": p}
        print(n, p["codigo"], bien)
    try:                                                                    # desde la segunda tanda, el guion guarda lo que corre
        out["huellas"] = dict(l.split()[::-1] for l in open(R + "/HUELLAS.txt") if l.strip())
    except FileNotFoundError:
        pass
    t = json.dumps(out, ensure_ascii=False, indent=1)
    assert not re.search(r"/(tmp|home|datos)/", t), "queda una ruta de la máquina"
    open(salida, "w", encoding="utf-8").write(t)
    return 0 if all(c["como_se_esperaba"] for c in out["controles"].values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
