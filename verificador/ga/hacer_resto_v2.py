#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33 (ga/diseno-ga-fable.md §2-§5; Jev: ga/decision-jev-gad.md y gad2): el resto de la versión 2 del corpus.
- ga/gen_bases_a1_v2.py -> ga/bases_a1_v2.json: A1 con «María» -> «Maria» (§2.1, P9); lo demás, a propósito, se queda (§2.2).
- ga/ejemplos_cap3_v2.json: los 7 fragmentos tal cual y 7 copias «-completada» (§3). P5: cap3-36 deja XPN.8 = D (error conocido);
  P8: el HD.1 largo de cap3-37 es aviso.
- ga/bases_mdm_v2.py: deriva las 40 bases de bases_mdm.py con B36 TXA-12 = DOC0036^CSSYN^2.999^ISO (§4, P7).
- ga/gemelos/: los 39 gemelos (§5): CE.3 UCUM -> ISO+ en OBX-6 y RXA-7, y MSH-10 con «-ISO» (P6). Salen de los mismos generadores
  públicos que los escribió la etapa 30 (iv/corpus_iv.py). DV-GA-2: no entran en el corpus por omisión de la herramienta.
Ningún fichero de la versión 1 cambia.
  cd fase12 && python3 ga/hacer_resto_v2.py"""
import glob
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

GA = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(GA)
os.chdir(FASE)
sys.path[:0] = [FASE, os.path.join(FASE, "cv"), os.path.join(FASE, "au"), GA]


def una(t, viejo, nuevo, nombre):
    n = t.count(viejo)
    if n != 1:
        sys.exit("PARADA: %s aparece %d veces" % (nombre, n))
    return t.replace(viejo, nuevo)


# ---------------------------------------------------------------------------- A1 (§2)
def a1():
    t = open("a1/gen_bases_a1.py", encoding="utf-8").read()
    t = una(t, "de&la&Fuente^Ana^María^^Dra^^L", "de&la&Fuente^Ana^Maria^^Dra^^L", "María")
    uso = re.findall(r"  cd \S+/fase12 && python3 a1/gen_bases_a1\.py +-> a1/bases_a1\.json", t)   # la línea de uso del original
    assert len(uso) == 1, uso
    t = t.replace(uso[0], "  cd fase12 && python3 ga/gen_bases_a1_v2.py      -> ga/bases_a1_v2.json")
    t = una(t, 'json.dump(b, open("a1/bases_a1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)\n    print(len(b), "bases en a1/bases_a1.json")',
            'json.dump(b, open("ga/bases_a1_v2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)\n    print(len(b), "bases en ga/bases_a1_v2.json")',
            "salida de A1")
    open(os.path.join(GA, "gen_bases_a1_v2.py"), "w", encoding="utf-8").write(
        "# Generado por ga/hacer_resto_v2.py desde a1/gen_bases_a1.py (etapa 33). No editar a mano.\n" + t)
    import gen_bases_a1_v2
    b = gen_bases_a1_v2.bases()
    json.dump(b, open(os.path.join(GA, "bases_a1_v2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return len(b)


# ---------------------------------------------------------------------------- capítulo 3 (§3)
PID_ADD = "EJEMPLO^CAPITULO^^^^^L"
COMPLETAR = {
    # id: (cambios de MSH {campo: valor}, EVN que se añade o None, PID que se añade o None, campos que se añaden al PID, PV1)
    "cap3-08-A01": ({11: "P", 12: "2.5"}, "EVN|A01|198808181126", "PID|||CAP308^^^CAP3^MR||" + PID_ADD, None, "PV1||I"),
    "cap3-10-A04": ({}, None, "PID|||CAP310^^^CAP3^MR||" + PID_ADD, None, "PV1||O"),
    "cap3-12-A02": ({}, None, None, {5: PID_ADD}, "PV1||I"),
    "cap3-14-A02": ({}, None, None, {5: PID_ADD}, "PV1||I"),
    "cap3-15-A03": ({}, None, None, {5: PID_ADD}, "PV1||I"),
    "cap3-36-A04": ({9: "ADT^A04^ADT_A01", 10: "CAP336", 11: "P", 12: "2.5"}, "EVN|A04|199902171830", None, None, "PV1||O"),
    "cap3-37-A04": ({9: "ADT^A04^ADT_A01", 10: "CAP337", 11: "P", 12: "2.5"}, "EVN|A04|199902171830", None, {5: PID_ADD}, "PV1||O"),
}


def poner(seg, campos):
    f = seg.split("|")
    for i, v in campos.items():
        k = i if f[0] != "MSH" else i - 1              # MSH-1 es el separador: MSH-n está en f[n-1]
        while len(f) <= k:
            f.append("")
        assert f[k] == "" or v.startswith(f[k] + "^"), (seg[:3], i, f[k])   # solo se añade o se prolonga (MSH-9 con MSG.3)
        f[k] = v
    return "|".join(f)


def cap3():
    orig = json.load(open("a1/ejemplos_cap3.json", encoding="utf-8"))
    out = list(orig)
    for x in orig:
        msh_c, evn, pid, pid_c, pv1 = COMPLETAR[x["id"]]
        segs = x["mensaje"].split("\r")
        assert segs[0].startswith("MSH|")
        nuevos = [poner(segs[0], msh_c)]
        resto = segs[1:]
        if evn:
            assert not any(s.startswith("EVN|") for s in resto)
            nuevos.append(evn)
        for s in resto:
            nuevos.append(poner(s, pid_c) if s.startswith("PID|") and pid_c else s)
        if pid:
            assert not any(s.startswith("PID|") for s in resto)
            nuevos.append(pid)
        assert not any(s.startswith("PV1|") for s in resto)
        nuevos.append(pv1)
        out.append({"id": x["id"] + "-completada", "evento": x["evento"], "mensaje": "\r".join(nuevos),
                    "copia_completada_de": x["id"]})
    json.dump(out, open(os.path.join(GA, "ejemplos_cap3_v2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return len(out)


# ---------------------------------------------------------------------------- MDM (§4)
MDM_V2 = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33 (ga/diseno-ga-fable.md §4; Jev P7): las 40 bases MDM^T02 de la versión 2 del corpus. Se derivan de bases_mdm.py (que no
cambia): solo B36 cambia, en TXA-12, para caber en su LEN 30 (CH09.txt:834) conservando EI.2 a EI.4; así el TXA-13 que deriva
mev/bases_mdmev.py en T06 y T10 (EI.1 + «-PADRE») tiene 29 caracteres. Escrito por ga/hacer_resto_v2.py."""
import copy
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bases_mdm as BM  # noqa: E402

TXA12_V1 = "DOC0036^CSSYN^1.2.840.113619.2.1^ISO"
TXA12_V2 = "DOC0036^CSSYN^2.999^ISO"


def _v2(b):
    if b["id"] != "B36":
        return b
    b = copy.deepcopy(b)
    n = 0
    for i, s in enumerate(b["segmentos"]):
        if s.startswith("TXA|"):
            f = s.split("|")
            assert f[12] == TXA12_V1, f[12]
            f[12] = TXA12_V2
            b["segmentos"][i] = "|".join(f)
            n += 1
    assert n == 1
    return b


BASES = [_v2(b) for b in BM.BASES]
cable = BM.cable


def huella(bases=None):
    h = hashlib.sha256()
    for b in bases or BASES:
        h.update(cable(b).encode("utf-8"))
    return h.hexdigest()
'''


def mdm():
    open(os.path.join(GA, "bases_mdm_v2.py"), "w", encoding="utf-8").write(MDM_V2)
    import bases_mdm_v2 as B2
    import bases_mdm as BM
    dist = [b["id"] for a, b in zip(BM.BASES, B2.BASES) if BM.cable(a) != B2.cable(b)]
    assert dist == ["B36"], dist
    return len(B2.BASES)


# ---------------------------------------------------------------------------- gemelos (§5)
ORIGENES = [   # los 23 que sostienen a las 12 y, si son el caso de un par, sus controles; como los nombra iv/corpus_iv.py
    "au-pares/AU1-caso.hl7", "au-pares/AU1-control-k.hl7", "au-pares/AU2-caso.hl7", "au-pares/AU2-control-k.hl7",
    "lab/minimos/L09-obx-11-d-caso.hl7", "lab/minimos/L09-obx-11-d-control.hl7",
    "lab/minimos/M01-nm-punto-inicial-caso.hl7", "lab/minimos/M01-nm-punto-inicial-control.hl7",
    "lab/minimos/M07-oru-sin-pid-caso.hl7", "lab/minimos/M07-oru-sin-pid-control.hl7",
    "lab/oru/ORU-B20.hl7", "lab/oru/ORU-B29.hl7", "lab/oru/ORU-B30.hl7",
    "lab/vxu/VXU-B11.hl7", "lab/vxu/VXU-B16.hl7", "lab/vxu/VXU-B18.hl7", "lab/vxu/VXU-B21.hl7", "lab/vxu/VXU-B37.hl7",
    "lab/vxu/VXU-B40.hl7",
    "vxu-pares/VL04-rxa21-d-caso.hl7", "vxu-pares/VL04-rxa21-d-control.hl7", "vxu-pares/VL06-dos-rxa10-caso.hl7",
    "vxu-pares/VL06-dos-rxa10-control.hl7", "vxu-pares/VL07-dos-indicaciones-caso.hl7", "vxu-pares/VL07-dos-indicaciones-control.hl7",
    "vxu-pares/VM07-lote-repetido-caso.hl7", "vxu-pares/VM07-lote-repetido-control.hl7",
    "vxu-pares/VM08-fabricante-alterno-caso.hl7", "vxu-pares/VM08-fabricante-alterno-control.hl7",
    "vxu-pares/VM10-relacion-grd-caso.hl7", "vxu-pares/VM10-relacion-grd-control.hl7",
    "vxu-pares/VM12-dos-indicaciones-caso.hl7", "vxu-pares/VM12-dos-indicaciones-control.hl7",
    "vxu-pares/VM14-dosis-punto-inicial-caso.hl7", "vxu-pares/VM14-dosis-punto-inicial-control.hl7",
    "vxu-pares/VM15-re-sin-rxa18-caso.hl7", "vxu-pares/VM15-re-sin-rxa18-control.hl7",
]


def origenes():
    """Los textos de origen, escritos por los mismos generadores y del mismo modo que iv/corpus_iv.py."""
    _argv, sys.argv = sys.argv, ["x", "--silencio"]
    import verificar_conversor as VC
    import cv3_minimos_vxu as MV
    import pares_auditoria as PA
    sys.argv = _argv
    tmp = tempfile.mkdtemp(prefix="ga_gem_")
    try:
        co = VC.generar_corpus(os.path.join(tmp, "c"), lab=True, minimos=True, propios=[])     # versión 1: ORU, VXU y mínimos no cambian
        textos = {}
        for c in co["casos"]:
            textos["lab/" + c["fichero"]] = open(os.path.join(tmp, "c", c["fichero"]), "rb").read()
        d = os.path.join(tmp, "vxu-pares")
        os.makedirs(d)
        MV.escribir(d)
        for r in glob.glob(os.path.join(d, "**", "*.hl7"), recursive=True):
            textos["vxu-pares/" + os.path.relpath(r, d).replace(os.sep, "/")] = open(r, "rb").read()
        for pid, _, _, _, caso, controles in PA.PARES:
            for lado, texto in [("caso", caso)] + [("control-" + k, t) for k, t in controles]:
                textos["au-pares/%s-%s.hl7" % (pid, lado)] = (texto + "\r").encode("utf-8")
        return textos
    finally:
        shutil.rmtree(tmp)


def gemelo(texto):
    segs = texto.split("\r")
    fin = segs[-1] == ""
    out, n = [], 0
    for s in segs:
        f = s.split("|")
        if f[0] == "MSH":
            f[9] = f[9] + "-ISO"
            assert len(f[9]) <= 20, f[9]
        idx = {"OBX": 6, "RXA": 7}.get(f[0])
        if idx and len(f) > idx and f[idx]:
            reps = []
            for r in f[idx].split("~"):
                c = r.split("^")
                if len(c) > 2 and c[2] == "UCUM":
                    c[2] = "ISO+"
                    n += 1
                reps.append("^".join(c))
            f[idx] = "~".join(reps)
        out.append("|".join(f))
    assert n >= 1, "sin UCUM"
    return "\r".join(out), n, (segs[0].split("|")[9])


def gemelos():
    textos = origenes()
    mapa = os.path.join(FASE, "..", "privado", "ga", "MAPA-GEMELOS.json")
    sha = {m["origen"]: m["sha256"] for m in json.load(open(mapa))} if os.path.exists(mapa) else {}
    d = os.path.join(GA, "gemelos")
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    man, filas = [], []
    for o in ORIGENES:
        t = textos[o]
        if sha:
            assert hashlib.sha256(t).hexdigest() == sha[o], ("el origen no es el de la etapa 30", o)
        g, n, msh10 = gemelo(t.decode("utf-8"))
        nombre = msh10 + "-ISO.hl7"
        assert not os.path.exists(os.path.join(d, nombre)), nombre
        open(os.path.join(d, nombre), "w", encoding="utf-8", newline="").write(g)
        man.append("%s  %s" % (hashlib.sha256(g.encode("utf-8")).hexdigest(), nombre))
        filas.append({"gemelo": nombre, "origen": o, "msh10_origen": msh10, "cambios_ce3": n})
    open(os.path.join(d, "MANIFIESTO.txt"), "w", encoding="utf-8").write("\n".join(sorted(man, key=lambda x: x.split()[1])) + "\n")
    json.dump(filas, open(os.path.join(GA, "GEMELOS.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return len(filas), bool(sha)


if __name__ == "__main__":
    print("A1: %d bases" % a1())
    print("capítulo 3: %d (7 fragmentos y 7 copias)" % cap3())
    print("MDM: %d bases (solo B36 distinta)" % mdm())
    n, comprobado = gemelos()
    print("gemelos: %d%s" % (n, "; orígenes idénticos a los de la etapa 30" if comprobado else ""))
