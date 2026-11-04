#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueba mínima de Lab.IV.Validar.Lote: un ADT limpio, uno no ASCII, uno sin PID y tres resoluciones de tipo."""
import json
import subprocess

B = "MSH|^~\\&|LAB|L|HIS|H|20260101120000||ADT^A01^ADT_A01|M1|P|2.5\rEVN|A01|20260101120000\rPID|1||12345^^^HOSP^MR||PEREZ^ANA||19800101|F\rPV1|1|I|W1^101^1\r"
U = B.replace("PEREZ^ANA", "MUÑOZ^IÑAKI").replace("|M1|", "|M2|")
S = B.replace("PID|1||12345^^^HOSP^MR||PEREZ^ANA||19800101|F\r", "")
pedidos = [{"k": "b-dm", "op": "validar", "texto": B, "doctype": "2.5:ADT_A01", "spec": "dm"},
           {"k": "u-dr", "op": "validar", "texto": U, "doctype": "2.5:ADT_A01", "spec": "dr"},
           {"k": "s-dm", "op": "validar", "texto": S, "doctype": "2.5:ADT_A01", "spec": "dm"},
           {"k": "r1", "op": "resolver", "tipo": "ADT_A04"}, {"k": "r2", "op": "resolver", "tipo": "VXU_V04"},
           {"k": "r3", "op": "resolver", "tipo": "MDM_T06"}, {"k": "r4", "op": "resolver", "tipo": "ADT_A11"}]
datos = "".join(json.dumps(p, ensure_ascii=False) + "\n" for p in pedidos).encode("utf-8")
subprocess.run(["docker", "exec", "-i", "iris-ai", "sh", "-c", "cat > /tmp/iv/prueba-entrada.jsonl"], input=datos, check=True)
guion = b'set sc=##class(Lab.IV.Validar).Lote("/tmp/iv/prueba-entrada.jsonl","/tmp/iv/prueba-salida.jsonl")\nwrite "lote: ",$select($system.Status.IsOK(sc):"OK",1:$system.Status.GetErrorText(sc)),!\nhalt\n'
r = subprocess.run(["docker", "exec", "-i", "iris-ai", "iris", "session", "IRIS", "-U", "USER"], input=guion, capture_output=True)
print([l for l in r.stdout.decode("utf-8", "replace").splitlines() if "lote:" in l])
out = subprocess.run(["docker", "exec", "iris-ai", "cat", "/tmp/iv/prueba-salida.jsonl"], capture_output=True, check=True).stdout
for l in out.decode("utf-8").splitlines():
    print(l[:300])
