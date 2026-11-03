#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 29 (ANTES-ETAPA-AUDITORIA.md): pares mínimos válidos en v2.5 para las tres nuevas publicadas cuyo par la auditoría dejó en
duda o invalidó, o cuyo defecto transversal caía en el campo del hallazgo. Cada par se construye con los mismos constructores de
los pares publicados (cv/cv3_minimos_vxu.vxu y cv/cv3_minimos.oru), quitando lo que la auditoría señaló:
- AU1, VX-M15 (Microsoft; el par VM15 quedó en duda): RXA-20 RE sin nada administrado (RXA-6 0; sin lote, caducidad, fabricante
  ni RXR). Caso sin RXA-18; control con RXA-18.
- AU2, VX-L8 (LinuxForHealth): dos repeticiones de RXA-10, ahora con XCN-9 (CH02A §2.A.86.1). Control con una.
- AU3, L-19 (LinuxForHealth; L10-caso era inválido, OBR-25 I con una OBX final): el informe de ORU-B31, OBR-25 I sin OBX; controles
  con OBR-25 O y S, que tampoco llevan resultados.
En todos, RXA-10 lleva XCN-9. Corre los dos conversores en su caja con cv/verificar_conversor.py (--corpus) y dice, por par y
conversor, si el hallazgo sale en el caso y no en el control. Desde fase12.
  python3 au/pares_auditoria.py <carpeta de trabajo vacía> -o <json>"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "cv"))
sys.path.insert(0, os.getcwd())
import cv3_minimos_vxu as MV  # noqa: E402
import cv3_minimos as MC  # noqa: E402

PR = "PR01^Ensayo^Ana^^^^^^HOSPSYN"
NADA = {6: "0", 10: PR, 15: None, 16: None, 17: None}
PARES = [
    ("AU1", "VX-M15", "microsoft", ("RXA-20", "codigo_mal_mapeado"),
     MV.vxu("AU1c", rxa={**NADA, 20: "RE"}, rxr=False),
     [("k", MV.vxu("AU1k", rxa={**NADA, 20: "RE", 18: "REL^Motivo religioso^L"}, rxr=False))]),
    ("AU2", "VX-L8", "linuxforhealth", ("RXA-10", ""),
     MV.vxu("AU2c", rxa={10: PR + "~PR02^Muestra^Jorge^^^^^^HOSPSYN"}),
     [("k", MV.vxu("AU2k", rxa={10: PR}))]),
    ("AU3", "L-19", "linuxforhealth", ("OBR-25", "codigo_mal_mapeado"),
     MC.oru("AU3c", [], obr25="I"),
     [("o", MC.oru("AU3o", [], obr25="O")), ("s", MC.oru("AU3s", [], obr25="S")), ("x", MC.oru("AU3x", [], obr25="X"))]),
]


def correr(adaptador, corpus, salida):
    r = subprocess.run(["python3", "cv/verificar_conversor.py", "cv/adaptadores/%s.json" % adaptador, salida, "--artefactos",
                        "../privado/cv/conversores", "--corpus", corpus, "--sin-corpus-lab", "--sin-minimos", "--sin-sensibilidad",
                        "--json-solo"], capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stderr[-500:]
    return {f["caso"]: f for f in map(json.loads, open(os.path.join(salida, "juicio.jsonl"), encoding="utf-8"))}


def tiene(fila, esperado):
    return any(re.sub(r"\(\d+\)", "", h.get("hecho") or "") == esperado[0] and esperado[1] in (h.get("subtipo") or "")
               for h in fila.get("cuentan") or [])


def main(trabajo, salida):
    assert not os.path.exists(trabajo) or not os.listdir(trabajo), "la carpeta de trabajo tiene que estar vacía"
    corpus = os.path.join(trabajo, "pares")
    os.makedirs(corpus)
    for pid, _, _, _, caso, controles in PARES:
        for lado, texto in [("caso", caso)] + [("control-" + k, t) for k, t in controles]:
            open(os.path.join(corpus, "%s-%s.hl7" % (pid, lado)), "w", encoding="utf-8", newline="").write(texto + "\r")
    filas = {c: correr(c, corpus, os.path.join(trabajo, c)) for c in ("microsoft", "linuxforhealth")}
    res = []
    for pid, nueva, conv, esp, _, controles in PARES:
        fila = {"id": pid, "nueva": nueva, "conversor_de_la_nueva": conv, "esperado": list(esp)}   # confirma: en el caso y en ningún control
        for c, fs in filas.items():
            caso = next(v for k, v in fs.items() if k.endswith("%s-caso" % pid))
            ctr = {k.split("control-")[1]: v for k, v in fs.items() if "%s-control-" % pid in k}
            fila[c] = {"caso": tiene(caso, esp), "controles": {k: tiene(v, esp) for k, v in ctr.items()},
                       "categoria_caso": caso.get("categoria"), "confirma": tiene(caso, esp) and not any(tiene(v, esp) for v in ctr.values())}
        res.append(fila)
        print("%-4s %-7s %-15s %-30s %s" % (pid, nueva, conv, "%s %s" % esp, "  ".join(
            "%s: caso=%s controles=%s %s" % (c, fila[c]["caso"], fila[c]["controles"], "CONFIRMA" if fila[c]["confirma"] else "-") for c in filas)))
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[sys.argv.index("-o") + 1])
