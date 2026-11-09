#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 41: el arreglo del juez (po/diseno-po-fable.md §1, con po/decision-jev-po.md: Q-PO-1 a, Q-PO-2 b).

  python3 po/parche_juez_po.py [<carpeta del juez>]     (por omisión, la de este laboratorio)

La Observation que la guía crea desde PD1-7 en un ORU (MSG_ORU_R01.csv:17) se aparta, con PD1-7 valorado, antes de casar las de los
OBX, por el mismo paso que en ADT (sacado a `apartar_pd17` en `emparejar`), y se juzga con lo de la 40 (sacado a `_juzgar_pd17`).
Cada hallazgo de PD1-7 cita la hoja de su mensaje (CITAS_PD17; `C["PD1-7"]` no cambia). Una referencia a ella desde
DiagnosticReport.result sigue siendo referencia_rota del OBR (Q-PO-1 a: nada que cambiar en el juicio del informe). La fila de PD1-7
en el perfil de ORU, S-CV-4, L-CV-18 y el texto de versión del servidor. En ADT, la misma salida byte a byte.
Cada sustitución tiene que darse una sola vez; si no, no se escribe nada. Conserva los finales de línea."""
import os
import sys

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CV = []
CV.append(("CITAS_PD17 (Q-PO-2 b)",
           'S0315 = "http://terminology.hl7.org/CodeSystem/v2-0315"\n',
           'S0315 = "http://terminology.hl7.org/CodeSystem/v2-0315"\n'
           'CITAS_PD17 = {"adt": C["PD1-7"], "oru": [c if c != "[G MSG_ADT_A01.csv:19]" else "[G MSG_ORU_R01.csv:17]"   # etapa 41\n'
           '                                        for c in C["PD1-7"]]}                                       # (Q-PO-2 b)\n'))
CV.append(("_sujeto con citas",
           '''def _sujeto(J, m, r, desde, pat_entry, ruta, hecho):
    ref = r.get("subject")
    if ref is None:
        if pat_entry is not None:
            J.cuenta("dato_perdido", hecho, "%s: falta" % ruta)''',
           '''def _sujeto(J, m, r, desde, pat_entry, ruta, hecho, citas=None):      # citas: etapa 41 (por omisión, las del hecho)
    ref = r.get("subject")
    if ref is None:
        if pat_entry is not None:
            J.cuenta("dato_perdido", hecho, "%s: falta" % ruta, citas=citas)'''))
CV.append(("_sujeto: la nota de la referencia lógica por identifier",
           '''            J.nota("convencion", hecho, "%s: referencia lógica por identifier" % ruta)''',
           '''            J.nota("convencion", hecho, "%s: referencia lógica por identifier" % ruta, citas=citas)'''))
CV.append(("_sujeto: la nota de la referencia lógica a un valor",
           '''            J.nota("convencion", hecho, "%s: referencia lógica a %r" % (ruta, ref["identifier"]["value"]))''',
           '''            J.nota("convencion", hecho, "%s: referencia lógica a %r" % (ruta, ref["identifier"]["value"]), citas=citas)'''))
CV.append(("_livingwill con citas",
           '''def _livingwill(J, m, v, r, entry, pat_entry):''',
           '''def _livingwill(J, m, v, r, entry, pat_entry, citas=None):'''))
CV.append(("_livingwill: las citas por omisión",
           '''    su status (FHIR R4, 1..1, required) y su sujeto. Code, effective[x] y lo demás no se juzgan."""
    st = r.get("status")''',
           '''    su status (FHIR R4, 1..1, required) y su sujeto. Code, effective[x] y lo demás no se juzgan. Etapa 41: cita la hoja de su
    mensaje (CITAS_PD17, Q-PO-2 b)."""
    citas = citas or C["PD1-7"]
    st = r.get("status")'''))
CV.append(("_livingwill: status", '(required)" % (st,), citas=C["PD1-7"])', '(required)" % (st,), citas=citas)'))
CV.append(("_livingwill: convención", '"(la 0315 es user-defined)" % (obs, v), citas=C["PD1-7"])',
           '"(la 0315 es user-defined)" % (obs, v), citas=citas)'))
CV.append(("_livingwill: valor distinto", 't[1], [c for s, c in obs if s == S0315]), citas=C["PD1-7"])',
           't[1], [c for s, c in obs if s == S0315]), citas=citas)'))
CV.append(("_livingwill: código mal mapeado",
           '''"Observation.valueCodeableConcept: esperado %r (de %r), observado %r" % (t, v, obs),
                     citas=C["PD1-7"])''',
           '''"Observation.valueCodeableConcept: esperado %r (de %r), observado %r" % (t, v, obs),
                     citas=citas)'''))
CV.append(("_livingwill: el sujeto con sus citas",
           '''    _sujeto(J, m, r, entry, pat_entry, "Observation.subject", "PD1-7")''',
           '''    _sujeto(J, m, r, entry, pat_entry, "Observation.subject", "PD1-7", citas=citas)'''))
CV.append(("_juzgar_pd17",
           "\n\ndef _juzgar(J, m, lec, familia):",
           '''

def _juzgar_pd17(J, m, roles, pat_entry, familia):
    """Etapas 40 y 41 (Q-PD-3 a, Q-PO-2 b): con PD1-7 valorado, la Observation de PD1-7 (PD1[Observation-LivingWill]) en ADT y en ORU;
    sin ella, recurso ausente. Cada hallazgo cita la hoja de su mensaje."""
    v7 = _valor_pd17(m)
    if not v7:
        return
    citas = CITAS_PD17[familia]
    o = roles.get("Observation#PD1")
    if o is None or o["entry"] is None:
        J.cuenta("recurso_ausente", "PD1-7", "falta la Observation de PD1-7 = %r (PD1[Observation-LivingWill])" % v7, citas=citas)
    else:
        _livingwill(J, m, v7, o["entry"]["r"], o["entry"], pat_entry, citas)


def _juzgar(J, m, lec, familia):'''))
CV.append(("_juzgar: ADT por el ayudante",
           '''        v7 = _valor_pd17(m)                                            # etapa 40 (Q-PD-3 a): la Observation de PD1-7
        if v7:
            o = roles.get("Observation#PD1")
            if o is None or o["entry"] is None:
                J.cuenta("recurso_ausente", "PD1-7", "falta la Observation de PD1-7 = %r (PD1[Observation-LivingWill])" % v7,
                         citas=C["PD1-7"])
            else:
                _livingwill(J, m, v7, o["entry"]["r"], o["entry"], pat_entry)
    elif familia == "vxu":''',
           '''        _juzgar_pd17(J, m, roles, pat_entry, "adt")                    # etapa 40 (Q-PD-3 a): la Observation de PD1-7
    elif familia == "vxu":'''))
CV.append(("_juzgar: ORU por el ayudante",
           '''                _informe(J, m, obr, d["entry"]["r"], d["entry"], pat_entry, i, obs_e, lec["entries"])
    for s in lec["sobrantes"]:''',
           '''                _informe(J, m, obr, d["entry"]["r"], d["entry"], pat_entry, i, obs_e, lec["entries"])
        _juzgar_pd17(J, m, roles, pat_entry, "oru")                    # etapa 41 (MSG_ORU_R01.csv:17)
    for s in lec["sobrantes"]:'''))
CV.append(("emparejar: apartar_pd17",
           '''    if familia == "vxu":                                            # gancho 4 (etapa 20): Immunization, Observation, NK1, PV1''',
           '''    def apartar_pd17(lista):                                       # etapas 40 y 41 (L-CV-18): la Observation de PD1-7, aparte
        pd17 = _origen_pd17(m, lista)
        if pd17 is None:
            return lista
        rol("Observation#PD1", "PD1-7", pd17[0], pd17[1], pd17[2])
        return [e for e in lista if pd17[0] is None or e is not pd17[0]]

    if familia == "vxu":                                            # gancho 4 (etapa 20): Immunization, Observation, NK1, PV1'''))
CV.append(("emparejar: ADT por apartar_pd17",
           '''        pd17 = _origen_pd17(m, obs)                                        # etapa 40 (L-CV-18): antes que ACC y PDA (Q-PD-2 a)
        if pd17 is not None:
            rol("Observation#PD1", "PD1-7", pd17[0], pd17[1], pd17[2])
            obs = [e for e in obs if pd17[0] is None or e is not pd17[0]]''',
           '''        obs = apartar_pd17(obs)                                            # etapa 40 (L-CV-18): antes que ACC y PDA (Q-PD-2 a)'''))
CV.append(("emparejar: ORU, antes de casar las de los OBX",
           '''        ob = [e for e in top if e["tipo"] == "Observation"]
        libres = list(drs)''',
           '''        ob = [e for e in top if e["tipo"] == "Observation"]
        ob = apartar_pd17(ob)                                              # etapa 41: antes de los OBX y de los huecos de L-CV-7
        libres = list(drs)'''))
CV.append(("el perfil de ORU: la fila de PD1-7",
           '''    {"elemento": "Observation.identifier propio, subject lógico, otros elementos", "campo": "—", "regla": "las 6 filas de convención''',
           '''    {"elemento": "Observation (de PD1-7)", "campo": "PD1-7", "regla": "IF PD1-7 VALUED: valueCodeableConcept por la 0315 (identidad), '''
           '''status y subject; se reconoce por el sistema de la 0315 o el código de PD1-7, aparte antes de casar las de los OBX; sin ella, '''
           '''recurso ausente (L-CV-18, etapa 41)", "nivel": "cuenta", "citas": CITAS_PD17["oru"]},
    {"elemento": "Observation.identifier propio, subject lógico, otros elementos", "campo": "—", "regla": "las 6 filas de convención'''))
CV.append(("S-CV-4", "el sistema de la 0315) resolviendo las referencias del Bundle.",
           "el sistema de la 0315, en ADT y, desde la etapa 41, en ORU) resolviendo las referencias del Bundle."))
CV.append(("L-CV-18: ORU",
           '''la otra sigue la regla de la 0136. Solo en ADT: la hoja "
                   "de ORU también la crea "
                   "(MSG_ORU_R01.csv:17) y en oru_conv sigue como recurso_inventado."}''',
           '''la otra sigue la regla de la 0136. En ADT y, desde la "
                   "etapa 41, en ORU (MSG_ORU_R01.csv:17): en oru_conv se aparta antes de casar las de los OBX y nunca ocupa un "
                   "hueco de L-CV-7; una referencia a ella desde DiagnosticReport.result sigue siendo referencia_rota del OBR, "
                   "porque la hoja no la pone en result (Q-PO-1); se lee el primer PD1, como el primer PID, aunque el ORU traiga "
                   "varios PATIENT_RESULT; con el código de un OBX, también de uno fuera de ORDER_OBSERVATION, es la de ese OBX, y "
                   "la Observation de un OBX que pierde su código y lleva el valor de PD1-7 pasa por la de PD1-7."}'''))

MCP = [("la entrada de la etapa 41 en el texto de versión",
        'REVISION = ("etapa 40: ',
        'REVISION = ("etapa 41: la Observation de PD1-7 también en oru_conv (S-CV-4) y L-CV-18; "\n            "antes, etapa 40: ')]


def aplica(p, cambios):
    t = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in t else "\n"
    hechos = []
    for nombre, antes, despues in cambios:
        antes, despues = antes.replace("\n", nl), despues.replace("\n", nl)
        if despues in t:
            continue
        if t.count(antes) != 1:
            raise SystemExit("%s: %s no está como se espera (%d veces); no se escribe nada" % (os.path.basename(p), nombre, t.count(antes)))
        t = t.replace(antes, despues)
        hechos.append(nombre)
    return t, hechos


def main(carpeta=AQUI):
    salidas = []
    for f, cambios in (("conversion.py", CV), ("mcp_verificador.py", MCP)):
        p = os.path.join(carpeta, f)
        t, hechos = aplica(p, cambios)
        salidas.append((p, t, hechos))
    for p, t, hechos in salidas:
        open(p, "w", encoding="utf-8", newline="").write(t)
        print("%s: %s" % (os.path.basename(p), ", ".join(hechos) if hechos else "ya estaba"))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
