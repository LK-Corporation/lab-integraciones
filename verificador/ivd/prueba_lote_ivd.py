#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 32: prueba mínima de Lab.IVD.Validar.Lote. Resolver en 2.5 (sin versión, como la 30), 2.5.1, 2.6 y 2.8; los segmentos de
2.5.1, 2.6 y 2.8 (ARV en 2.6 y 2.8, no en 2.5.1; PRT solo en 2.8); y la misma base del laboratorio con MSH-12 cambiado,
validada con el esquema de cada versión. Desde fase12: python3 ivd/prueba_lote_ivd.py"""
import json
import os
import subprocess

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = open(os.path.join(FASE, "..", "privado", "iv", "corpus", "lab", "adt", "A01-001.hl7"), encoding="utf-8").read()
segs = [s for s in base.replace("\n", "\r").split("\r") if s]
p = segs[0].split("|")


def con_version(v):
    q = list(p)
    q[11] = v
    return "\r".join(["|".join(q)] + segs[1:]) + "\r"


pedidos = [{"k": "r-def", "op": "resolver", "tipo": "ADT_A04"}]
for v in ("2.5.1", "2.6", "2.8"):
    pedidos.append({"k": "r-" + v, "op": "resolver", "tipo": "ADT_A04", "version": v})
    pedidos.append({"k": "s-" + v, "op": "segmentos", "version": v})
    pedidos.append({"k": "v-" + v, "op": "validar", "texto": con_version(v), "doctype": v + ":ADT_A01", "spec": "dm"})
datos = "".join(json.dumps(x) + "\n" for x in pedidos).encode("utf-8")
subprocess.run(["docker", "exec", "-i", "iris-ai", "sh", "-c", "mkdir -p /tmp/ivd && cat > /tmp/ivd/prueba-entrada.jsonl"],
               input=datos, check=True)
guion = open(os.path.join(FASE, "ivd", "prueba_ivd.txt"), "rb").read()
r = subprocess.run(["docker", "exec", "-i", "iris-ai", "iris", "session", "IRIS", "-U", "USER"], input=guion, capture_output=True)
assert b"lote: OK" in r.stdout, r.stdout[-400:]
out = subprocess.run(["docker", "exec", "iris-ai", "cat", "/tmp/ivd/prueba-salida.jsonl"], capture_output=True, check=True).stdout
res = {json.loads(l)["k"]: json.loads(l) for l in out.decode("utf-8").splitlines() if l.strip()}
for k in sorted(res):
    x = res[k]
    if k.startswith("s-"):
        s = x["segmentos"]
        print(k, len(s), "ARV" in s, "PRT" in s, "PID" in s)
    else:
        print(k, {a: b for a, b in x.items() if a != "k"})
assert res["r-def"]["doctype"].startswith("2.5:")
for v in ("2.5.1", "2.6", "2.8"):
    assert res["r-" + v]["doctype"].startswith(v + ":"), res["r-" + v]
assert "ARV" not in res["s-2.5.1"]["segmentos"] and "ARV" in res["s-2.6"]["segmentos"] and "PRT" in res["s-2.8"]["segmentos"]
print("PRUEBA: BIEN")
