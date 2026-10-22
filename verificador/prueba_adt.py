#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A1b (diseno-adt-fable.md §7, con S75-S96): el verificador de punta a punta con el punto adt_fhir, sobre evidencia sintética.
  (a) acuse: los 8 eventos -> AA; A05 -> AR 201; ORU -> AR 200; PV1-2 vacío -> AE 101 (lab) y AA + [S95] (perfil del sitio);
      PV1-19 vacío -> AA (S78); PID-30 fuera de 0136 -> AE 103; PID-7 inválido -> AE 102; los PE de siempre no cambian.
  (b) verificar: AA + L16 + canónico igual + almacén igual -> correcto en las 263 entradas de A1 que el acuse acepta; controles
      negativos: canónico con Estado cambiado -> fallo_silencioso (PV1-2); almacén con status cambiado -> fidelidad/almacen;
      A11 sin cancelar -> hecho MSH-9; Encounter escrito con PV1-2 = N -> fidelidad/almacen; AE con escritura -> rechazo_con_escritura;
      AA con PV1-2 vacío en lab -> fallo_silencioso (contenido/aceptado_imposible).
  (c) el MCP: verificar_caso con canonico_adt/almacen_adt pasa el esquema.
Regla: ningún MAL. Uso: python3 prueba_adt.py"""
import copy
import json
import os
import sys

import acuse_referencia as AR
import almacen_adt as AA2
import mapeador_adt as MA
import verificador as V

mal, n_ok = [], [0]


def mira(nombre, obtenido, esperado):
    if obtenido == esperado:
        n_ok[0] += 1
    else:
        print("  MAL %s: %r != %r" % (nombre, obtenido, esperado))
        mal.append(nombre)


BASE = ("MSH|^~\\&|HIS|H|LAB|L|20260101120000||ADT^%s^%s|M1|P|2.5\rEVN|%s|20260101120000\r"
        "PID|1||X1^^^H^MR||Pérez^Ana^^^^^L||19800101|F\rPV1|1|%s|URG^1^A|||||||MED|||||||||%s")
EST = MA.ESTRUCTURA


def msg(ev="A01", pv12="I", pv119="V1", **k):
    t = BASE % (ev, EST.get(ev, "ADT_A05"), ev, pv12, pv119)
    for a, b in k.items():
        t = t.replace(a, b)
    return t


def ack(msa1="AA", err=None, ctl="M1"):
    return "MSH|^~\\&|LAB|L|HIS|H|20260101120001||ACK^A01^ACK|A1|P|2.5\rMSA|%s|%s" % (msa1, ctl) + ("\rERR|||%s|E" % err if err else "")


L16 = {"tipo": "Info", "texto": "Paciente y visita escritos en FHIR (MSH-10=M1): Patient=creado Encounter=creado (HTTP 200)"}


def ev_(texto, ack_=None, log=None, canon=None, alm=None):
    s = {"log": log if log is not None else ([L16] if ack_ and "MSA|AA" in ack_ else [])}
    if canon is not None:
        s["canonico_adt"] = canon
    if alm is not None:
        s["almacen_adt"] = alm
    return {"mensaje": texto, "ack": ack_, "conexion": ["conexión establecida"] + (["ACK recibido a los 0.02 s del envío"] if ack_ else []),
            "sesiones": [s], "entorno": [], "punto_entrada": "adt_fhir"}


def acuse(texto, pe="adt_fhir"):
    x = AR.calcular(ev_(texto), pe=pe)[0]
    return (x.get("msa1"), x["err"][0]["err3"] if x["err"] else None, x["err"][0]["donde"] if x["err"] else None)


def verif(texto, msa1="AA", canon="esperado", alm="esperado", err=None, log=None):
    m = MA._msg(texto)
    esp = MA.esperado_mensaje(m, "adt_fhir")[0]
    c = copy.deepcopy(esp) if canon == "esperado" else canon
    a = AA2.almacen_sintetico(esp, ack_msa1=msa1) if alm == "esperado" else alm
    return V.verificar(ev_(texto, ack(msa1, err), log, c, a))


def cuenta(v):
    return sorted((h["clase"], h["subtipo"], h["hecho"]) for h in v["hallazgos"] if h["cuenta"])


# ---- (a) acuse
for ev in ("A01", "A02", "A03", "A04", "A08", "A11", "A13"):
    mira("%s -> AA" % ev, acuse(msg(ev))[:2], ("AA", None))
mira("A31 con PV1-2 N -> AA", acuse(msg("A31", "N", ""))[:2], ("AA", None))
mira("A05 -> AR 201 (L-ADT-2)", acuse(msg("A05").replace("ADT_A05", "ADT_A05"))[:2], ("AR", "201"))
mira("ORU -> AR 200", acuse(msg().replace("ADT^A01^ADT_A01", "ORU^R01^ORU_R01"))[:2], ("AR", "200"))
mira("PV1-2 vacío (lab) -> AE 101 PV1-2 (S95)", acuse(msg(pv12="")), ("AE", "101", "PV1-2"))
mira("PV1-19 vacío -> AA (S78)", acuse(msg(pv119=""))[:2], ("AA", None))
mira("PID-30 Q -> AE 103 (0136)", acuse(msg().replace("|19800101|F", "|19800101|F" + "|" * 22 + "Q"))[:3], ("AE", "103", "PID-30"))
mira("PID-7 inválido -> AE 102", acuse(msg().replace("19800101", "19801340"))[:3], ("AE", "102", "PID-7"))
mira("PV1-45 inválido -> AE 102", acuse(msg(pv119="V1" + "|" * 26 + "2026013"))[:2], ("AE", "102"))
mira("el PE adt no cambia: PV1-2 vacío -> AA", acuse(msg(pv12=""), "adt")[:2], ("AA", None))
perfiles = sorted(AR.PERFILES)
privados = [p for p in sorted(AR.PERFILES) if p != "lab"]          # el perfil del sitio no se nombra en fase12
if privados:
    AR.PERFIL = privados[0]
    try:
        x = AR.calcular(ev_(msg(pv12="")), pe="adt_fhir")[0]
        mira("PV1-2 vacío (perfil del sitio) -> AA + [S95]", (x["msa1"], any(t.startswith("[S95]") for t in x["tolerancias"])), ("AA", True))
    finally:
        AR.PERFIL = "lab"
else:
    print("  (perfil del sitio no cargado: S95 en el sitio no se prueba aquí)")

# ---- (b) verificar sobre las entradas de A1
B = []
for f in ("bases_adt/bases_e2.json", "a1/ejemplos_cap3.json", "a1/bases_a1.json"):
    if os.path.exists(f):
        B += json.load(open(f, encoding="utf-8"))
correctos, aceptados, otros = 0, 0, []
for b in B:
    x = AR.calcular(ev_(b["mensaje"]), pe="adt_fhir")[0]
    if x.get("msa1") != "AA":
        continue
    aceptados += 1
    ctl = MA._msg(b["mensaje"]).campo(MA._msg(b["mensaje"]).segs[0], 10)
    m = MA._msg(b["mensaje"])
    esp = MA.esperado_mensaje(m, "adt_fhir")[0]
    log = [dict(L16, texto=L16["texto"].replace("M1", ctl))]
    v = V.verificar(ev_(b["mensaje"], ack("AA", ctl=ctl), log, copy.deepcopy(esp), AA2.almacen_sintetico(esp)))
    if v["veredicto"]["categoria"] == "correcto":
        correctos += 1
    else:
        otros.append((b["id"], v["veredicto"]["categoria"], cuenta(v)[:3]))
mira("A1: todas las aceptadas con evidencia exacta -> correcto (%d de %d)" % (correctos, aceptados), otros[:5], [])
print("  (b) %d entradas, %d aceptadas por el acuse, %d correctas con evidencia exacta" % (len(B), aceptados, correctos))

v = verif(msg())
mira("exacto -> correcto", (v["veredicto"]["categoria"], cuenta(v)), ("correcto", []))
esp = MA.esperado_mensaje(MA._msg(msg()), "adt_fhir")[0]
c2 = copy.deepcopy(esp)
c2["cabecera"]["Estado"] = "finished"
v = verif(msg(), canon=c2)
mira("canónico con Estado cambiado -> fallo_silencioso PV1-2", (v["veredicto"]["categoria"], ("fidelidad", "guardado", "PV1-2") in cuenta(v)),
     ("fallo_silencioso", True))
a2 = AA2.almacen_sintetico(esp)
r = json.loads(a2["visitas"][0]["recursos"][0]["crudo"])
r["status"] = "finished"
a2["visitas"][0]["recursos"][0]["crudo"] = json.dumps(r)
v = verif(msg(), alm=a2)
mira("almacén con status cambiado -> fidelidad/almacen PV1-2", (v["veredicto"]["categoria"], cuenta(v)),
     ("fallo_silencioso", [("fidelidad", "almacen", "PV1-2")]))
e11 = MA.esperado_mensaje(MA._msg(msg("A11")), "adt_fhir")[0]
a11 = AA2.almacen_sintetico(e11)
r = json.loads(a11["visitas"][0]["recursos"][0]["crudo"])
r["status"] = "in-progress"
a11["visitas"][0]["recursos"][0]["crudo"] = json.dumps(r)
v = verif(msg("A11"), alm=a11)
mira("A11 sin cancelar -> fidelidad/almacen MSH-9", cuenta(v), [("fidelidad", "almacen", "MSH-9")])
eN = MA.esperado_mensaje(MA._msg(msg("A31", "N", "")), "adt_fhir")[0]
aN = AA2.almacen_sintetico(eN)
aN["visitas"] = [{"identificador": "V9", "n": 1, "recursos": [{"id": "9", "crudo": json.dumps({"resourceType": "Encounter", "status": "in-progress"})}]}]
v = verif(msg("A31", "N", ""), alm=aN)
mira("Encounter escrito con PV1-2 = N -> fidelidad/almacen PV1-2", cuenta(v), [("fidelidad", "almacen", "PV1-2")])
vacio = {"leido": "tras_ack", "pacientes": [{"identificador": "X1", "n": 0, "recursos": []}],
         "visitas": [{"identificador": "V1", "n": 0, "recursos": []}]}
v = verif(msg().replace("19800101", "19801340"), msa1="AE", err="102", log=[], alm=vacio)
mira("AE 102 sin escritura -> correcto", (v["veredicto"]["categoria"], cuenta(v)), ("correcto", []))
v = verif(msg().replace("19800101", "19801340"), msa1="AE", err="102", log=[],
          alm=AA2.almacen_sintetico(MA.esperado_mensaje(MA._msg(msg()), "adt_fhir")[0]))
mira("AE con escritura -> rechazo_con_escritura", ("acuse", "rechazo_con_escritura", "destino") in cuenta(v), True)
v = verif(msg(pv12=""))
mira("AA con PV1-2 vacío (lab) -> fallo_silencioso contenido/aceptado_imposible PV1-2 (un AA donde había que rechazar)",
     (v["veredicto"]["categoria"], cuenta(v)), ("fallo_silencioso", [("contenido", "aceptado_imposible", "PV1-2")]))

# ---- (c) MCP: el esquema admite canonico_adt y almacen_adt
try:
    import mcp_verificador as MCP
    e = ev_(msg(), ack(), None, copy.deepcopy(esp), AA2.almacen_sintetico(esp))
    out = MCP.llamar_herramienta({"name": "verificar_caso", "arguments": dict(e, caso="adt1", incluir_ficha=True)})
    texto = json.dumps(out, ensure_ascii=False)
    mira("MCP verificar_caso adt_fhir sin error de esquema", ("isError\": true" in texto, "correcto" in texto,
                                                              "ALMACÉN  leído tras ACK: Patient n=[1] Encounter n=[1]" in texto), (False, True, True))
except Exception as ex:                                              # el MCP es opcional en esta prueba
    mira("MCP importable", repr(ex)[:200], None)

print("AUTOPRUEBA ADT (A1b): %s (%d comprobaciones)" % ("TODO BIEN" if not mal else "FALLAN %d" % len(mal), n_ok[0] + len(mal)))
sys.exit(1 if mal else 0)
