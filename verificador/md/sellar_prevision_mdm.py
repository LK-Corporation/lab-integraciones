#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 26, MD2-b (md/diseno-md.md §6): escribe md/prevision-mdm.json con el cuerpo del programador (fijado antes de leer a
Jev; su sha256 va dentro), la previsión de Jev, la huella del juez y la del corpus. Se niega a pisar una previsión sellada.
Se corre desde fase12, antes de que ningún conversor vea las 40 bases.
  python3 md/sellar_prevision_mdm.py <cuerpo.json> <decision-jev-prevision-mdm.md>"""
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.getcwd())
sys.argv, args = [sys.argv[0], "--silencio"], sys.argv[1:]
import mcp_verificador as M  # noqa: E402
import bases_mdm as BM  # noqa: E402

SALIDA = "md/prevision-mdm.json"


def jev(ruta):
    """-> {pregunta: {respuesta, confianza, reparto}} leído del .md de decidir.py."""
    out, actual = {}, None
    for linea in open(ruta, encoding="utf-8"):
        m = re.match(r"- \*\*(\w+)\*\* \(choice\): \*\*(\w+)\*\*\s+\[confianza ([\d.]+)\]", linea)
        if m:
            actual = m.group(1)
            out[actual] = {"respuesta": m.group(2), "confianza": float(m.group(3))}
        elif actual and "·" in linea:
            out[actual]["reparto"] = {k: float(v) for k, v in re.findall(r"(\w+) ([\d.]+)", linea)}
            actual = None
    return out


def main(cuerpo, decision):
    if os.path.exists(SALIDA):
        raise SystemExit("ya hay una %s: no se pisa una previsión sellada" % SALIDA)
    crudo = open(cuerpo, "rb").read()
    p = json.loads(crudo)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    p["fecha"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    p["juez"] = {"huella": M.VERSION["huella"], "commit": commit, "servidor": M.SERVIDOR}
    p["corpus"] = {"bases_mdm_huella": BM.HUELLA, "n_mdm": len(BM.BASES),
                   "bases_mdm_jsonl_sha256": hashlib.sha256(open("bases_mdm.jsonl", "rb").read()).hexdigest()}
    p["programador_cuerpo_sha256"] = hashlib.sha256(crudo).hexdigest()
    p["jev"] = {"_que": "previsión de Jev con un estado neutro (md/estado_prevision_mdm.md); el cuerpo del programador se fijó antes de leerla",
                "respuestas": jev(decision)}
    assert len(BM.BASES) == 40 and p["jev"]["respuestas"], "faltan las bases o la respuesta de Jev"
    json.dump(p, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("%s sellada: juez %s, corpus %s, sha256 %s" % (SALIDA, p["juez"]["huella"][:12], BM.HUELLA[:12],
                                                          hashlib.sha256(open(SALIDA, "rb").read()).hexdigest()))


if __name__ == "__main__":
    main(*args)
