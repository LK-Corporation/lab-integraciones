#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 26, MD3: los pares mínimos de los candidatos a nueva (md/HALLAZGOS-MD3-r1.json, tras la repetición 1). Cada par son
dos mensajes válidos en v2.5 que solo se diferencian en el disparador: «sin» (la base B26 tal cual, o con lo mínimo para ser el
contexto) y «con». Escribe los .hl7, corre los dos conversores en su caja con cv/verificar_conversor.py (--corpus) y dice, por
par y conversor, si el hallazgo esperado sale en «con» y no en «sin». Se corre desde fase12.
  python3 md/pares_mdm.py <carpeta de trabajo vacía> -o <json>"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.getcwd())
import bases_mdm as BM  # noqa: E402

BASE = [x for x in BM.BASES if x["id"] == "B26"][0]["segmentos"]   # TX con NTE, AU con TXA-22, AV, un grupo de orden


def campo(segs, nombre, i, valor):
    out = []
    for s in segs:
        if s.startswith(nombre + "|"):
            f = s.split("|")
            while len(f) <= i:
                f.append("")
            f[i] = valor
            s = "|".join(f)
        out.append(s)
    return out


def sin_nte(segs):
    return [s for s in segs if not s.startswith("NTE|")]


def obx(segs, nuevos):
    """Cambia los OBX (y sus NTE) por los de la lista, en su sitio."""
    i = next(k for k, s in enumerate(segs) if s.startswith("OBX|"))
    return segs[:i] + nuevos + [s for s in segs[i:] if not s.startswith(("OBX|", "NTE|"))]


TX = "OBX|1|TX|TEXTO^Texto del informe^L||Afebril en las ultimas cuarenta y ocho horas Zeta260100||||||F"
# (id, conversor del candidato, hallazgo esperado (hecho, subtipo) o categoría, sin, con, qué dice)
PARES = [
    ("MP1", "microsoft", ("categoria", "rechazo_incorrecto"),
     campo(BASE, "TXA", 8, "20231022103000+0100"), campo(BASE, "TXA", 8, "20231022103000+0100~20231022104000+0100"),
     "TXA-8 (Edit Date/Time, TS repetible en v2.5) con dos repeticiones: el conversor rechaza el mensaje"),
    ("MP2", "microsoft", ("TXA-19", "valor_distinto"),
     BASE, campo(BASE, "TXA", 19, "OB"),
     "TXA-19 OB (obsoleto) da status entered-in-error en vez de superseded"),
    ("MP3", "linuxforhealth", ("TXA-19", "dato_perdido"),
     BASE, campo(BASE, "TXA", 19, "UN"),
     "TXA-19 UN (desconocido) da status current y el código no se conserva"),
    ("MP4", "linuxforhealth", ("OBX-5", "valor_distinto"),
     obx(sin_nte(BASE), [TX, "OBX|2|FT|TEXTOF^Texto con formato^L||Tolera dieta oral sin incidencias Zeta260200||||||F"]),
     obx(sin_nte(BASE), [TX, "OBX|2|FT|TEXTOF^Texto con formato^L||Tolera dieta oral\\.br\\sin incidencias Zeta260200||||||F"]),
     "un FT con la orden de formato \\.br\\ junto a un TX: llega cruda en el adjunto text/plain"),
    ("MP5", "linuxforhealth", ("OBX-5", "dato_perdido"),
     obx(sin_nte(BASE), [TX]),
     obx(sin_nte(BASE), ["OBX|1|CE|2000.40^MOTIVO^L||DT01^Dolor toracico^L||||||F", TX.replace("OBX|1|", "OBX|2|")]),
     "un OBX CE antes del OBX TX: el texto del TX no llega al documento"),
    ("MP6", "linuxforhealth", ("NTE-3", "dato_perdido"),
     sin_nte(BASE), BASE,
     "una NTE bajo un OBX TX se pierde entera"),
    ("MP7", "linuxforhealth", ("TXA-10", "valor_distinto"),
     BASE, campo(BASE, "TXA", 22, "PR03^Patron^Irene^^^^^^^^^^^^20231022102630+0100"),
     "TXA-22 con otra persona que TXA-10: el authenticator sale de TXA-22"),
]


def correr(adaptador, corpus, salida):
    r = subprocess.run(["python3", "cv/verificar_conversor.py", "cv/adaptadores/%s.json" % adaptador, salida, "--artefactos",
                        "../privado/cv/conversores", "--corpus", corpus, "--sin-corpus-lab", "--sin-minimos", "--sin-sensibilidad",
                        "--json-solo"], capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stderr[-500:]
    return {f["caso"]: f for f in map(json.loads, open(os.path.join(salida, "juicio.jsonl"), encoding="utf-8"))}


def tiene(fila, esperado):
    if esperado[0] == "categoria":
        return fila.get("categoria") == esperado[1]
    return any(re.sub(r"\(\d+\)", "", h.get("hecho") or "") == esperado[0] and esperado[1] in (h.get("subtipo") or "")
               for h in fila.get("cuentan") or [])


def main(trabajo, salida, sufijo=""):
    """`sufijo` «-main» corre los adaptadores de las ramas principales (cv/adaptadores/*-main.json)."""
    assert not os.path.exists(trabajo) or not os.listdir(trabajo), "la carpeta de trabajo tiene que estar vacía"
    corpus = os.path.join(trabajo, "pares")
    os.makedirs(corpus)
    for pid, _, _, sin, con, _ in PARES:
        for lado, segs in (("sin", sin), ("con", con)):
            segs = campo(segs, "MSH", 9, "MDM-%s-%s" % (pid, lado))
            open(os.path.join(corpus, "%s-%s.hl7" % (pid, lado)), "w", encoding="utf-8", newline="").write("\r".join(segs) + "\r")
    filas = {c: correr(c + sufijo, corpus, os.path.join(trabajo, c)) for c in ("microsoft", "linuxforhealth")}
    res = []
    for pid, conv, esp, _, _, que in PARES:
        fila = {"id": pid, "conversor_del_candidato": conv, "esperado": list(esp), "que": que}
        for c, fs in filas.items():
            s = next(v for k, v in fs.items() if k.endswith("%s-sin" % pid))
            k = next(v for k, v in fs.items() if k.endswith("%s-con" % pid))
            fila[c] = {"sin": tiene(s, esp), "con": tiene(k, esp), "categoria_sin": s.get("categoria"), "categoria_con": k.get("categoria"),
                       "confirma": tiene(k, esp) and not tiene(s, esp)}
        res.append(fila)
        print("%-4s %-15s %-34s %s" % (pid, conv, "%s %s" % esp, "  ".join("%s: sin=%s con=%s %s" % (
            c, fila[c]["sin"], fila[c]["con"], "CONFIRMA" if fila[c]["confirma"] else "-") for c in filas)))
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[sys.argv.index("-o") + 1], "-main" if "--main" in sys.argv else "")
