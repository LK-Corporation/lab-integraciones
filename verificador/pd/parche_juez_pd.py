#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 40: el arreglo del juez (pd/diseno-pd-fable.md §1, con pd/decision-jev-pd.md: Q-PD-1 a, Q-PD-2 a, Q-PD-3 a).

  python3 pd/parche_juez_pd.py [<carpeta del juez>]     (por omisión, la de este laboratorio)

La Observation que la guía crea desde PD1-7 en un ADT (PD1[Observation-LivingWill], MSG_ADT_A01.csv:19) se reconoce, con PD1-7
valorado, por un coding de su valueCodeableConcept con el sistema de la 0315 o con el código de PD1-7 (la primera con el sistema;
si no, la primera del Bundle), antes que ACC y PDA; y se juzga: su valor por la 0315 (identidad), su status (FHIR R4) y su sujeto.
Sin ella, recurso_ausente. La 0315 entra en MAPAS, CM y cv/extraer_mapas.py; C["PD1-7"], S-CV-4, L-CV-17, L-CV-18, el perfil de
ADT y el texto de versión del servidor. Cada sustitución tiene que darse una sola vez; si no, no se escribe nada. Conserva los finales
de línea."""
import os
import sys

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S0315 = "http://terminology.hl7.org/CodeSystem/v2-0315"
MAPA_0315 = ("    'table-hl70315-to-v2-0315': {%s},\n" %
             ", ".join("'%s': ('%s', '%s')" % (c, S0315, c) for c in ("Y", "F", "N", "I", "U")))

CV = []          # (nombre, antes, después) de conversion.py
CV.append(("la 0315 en MAPAS", "\n}\n\nCM = {", "\n" + MAPA_0315.rstrip("\n") + "\n}\n\nCM = {"))
CV.append(("la 0315 en CM",
           '"0123": "table-hl70123-queries-to-diagnostic-report-status"}',
           '"0123": "table-hl70123-queries-to-diagnostic-report-status",\n      "0315": "table-hl70315-to-v2-0315"}   # etapa 40'))
CV.append(("C[\"PD1-7\"]", "\n\ndef _cit(clave):",
           "\nC[\"PD1-7\"] = [\"[CM segment-pd1-livingwill-to-observation PD1-7 → valueCodeableConcept]\", \"[CM table-hl70315-to-v2-0315]\",\n"
           "              \"[G MSG_ADT_A01.csv:19]\", \"[E3 Ch03.txt:8504]\", \"[E3 Ch03.txt:8630-8643]\"]   # etapa 40\n"
           "S0315 = \"%s\"\n\n\ndef _cit(clave):" % S0315))
CV.append(("la Observation de PD1-7, antes de emparejar",
           "def emparejar(m, entries, familia, notas=()):",
           '''# ---------------------------------------------------------------------------- etapa 40: la Observation de PD1-7 (L-CV-18)
def _valor_pd17(m):
    """PD1-7, su primer componente (en v2.5, un IS sin componentes: el campo entero); "" si no hay PD1 o viene vacío."""
    pd1 = _seg(m, "PD1")
    return _t(m, _f(m, pd1, 7), 1) if pd1 is not None else ""


def _origen_pd17(m, obs):
    """Con PD1-7 valorado: (entry o None, por, candidatas) de la Observation que la guía crea desde PD1-7 (Q-PD-1 a: solo por el
    dato). Candidata: una Observation sin el código de un OBX del mensaje cuyo valueCodeableConcept lleva un coding con el sistema
    de la 0315 o con el código de PD1-7; la primera con el sistema, y si ninguna lo lleva, la primera del Bundle. None sin PD1-7."""
    v = _valor_pd17(m)
    if not v:
        return None
    obx = {c for s in m.segmentos("OBX") for c in (_t(m, _f(m, s, 3), 1), _t(m, _f(m, s, 3), 4)) if c}
    cands = []
    for e in obs:
        if e["tipo"] != "Observation" or obx & {c for _, c in _codigos(e["r"].get("code"))}:
            continue
        cods = _codigos(e["r"].get("valueCodeableConcept"))
        sistema = any(s == S0315 for s, _ in cods)
        if sistema or any(c == v for _, c in cods):
            cands.append((e, sistema))
    if not cands:
        return None, None, 0
    con = [e for e, s in cands if s]
    return (con[0], "sistema", len(cands)) if con else (cands[0][0], "codigo", len(cands))


def emparejar(m, entries, familia, notas=()):'''))
CV.append(("emparejar: la de PD1-7 primero (Q-PD-2 a)",
           '''        obs = [e for e in top if e["tipo"] in ("Observation", "DiagnosticReport")]
        k = 0
        for e in obs:
            sm = _origen_sin_mapa(m, e["r"]) if e["tipo"] == "Observation" else None      # etapa 37 (L-CV-17)''',
           '''        obs = [e for e in top if e["tipo"] in ("Observation", "DiagnosticReport")]
        pd17 = _origen_pd17(m, obs)                                        # etapa 40 (L-CV-18): antes que ACC y PDA (Q-PD-2 a)
        if pd17 is not None:
            rol("Observation#PD1", "PD1-7", pd17[0], pd17[1], pd17[2])
            obs = [e for e in obs if pd17[0] is None or e is not pd17[0]]
        k = 0
        for e in obs:
            sm = _origen_sin_mapa(m, e["r"]) if e["tipo"] == "Observation" else None      # etapa 37 (L-CV-17)'''))
CV.append(("_juzgar: la Observation de PD1-7 (Q-PD-3 a)",
           '''                _encounter(J, m, pv1, en["entry"]["r"], lec["entries"], pat_entry, en["entry"])
    elif familia == "vxu":''',
           '''                _encounter(J, m, pv1, en["entry"]["r"], lec["entries"], pat_entry, en["entry"])
        v7 = _valor_pd17(m)                                            # etapa 40 (Q-PD-3 a): la Observation de PD1-7
        if v7:
            o = roles.get("Observation#PD1")
            if o is None or o["entry"] is None:
                J.cuenta("recurso_ausente", "PD1-7", "falta la Observation de PD1-7 = %r (PD1[Observation-LivingWill])" % v7,
                         citas=C["PD1-7"])
            else:
                _livingwill(J, m, v7, o["entry"]["r"], o["entry"], pat_entry)
    elif familia == "vxu":'''))
CV.append(("_livingwill",
           "\n\ndef _juzgar(J, m, lec, familia):",
           '''

def _livingwill(J, m, v, r, entry, pat_entry):
    """Etapa 40 (L-CV-18): la Observation de PD1-7. El paquete solo fija PD1-7 → valueCodeableConcept por la 0315 (identidad); además,
    su status (FHIR R4, 1..1, required) y su sujeto. Code, effective[x] y lo demás no se juzgan."""
    st = r.get("status")
    if st not in ESTADO_FHIR["0085"]:
        J.cuenta("fhir_invalido", "PD1-7", "Observation.status: %r fuera de observation-status (required)" % (st,), citas=C["PD1-7"])
    obs = _codigos(r.get("valueCodeableConcept"))
    t = mapa("0315", v)
    if t in (FUERA, None):                      # la 0315 es de usuario: fuera de ella, el mismo código vale; otro, convención
        if obs and v not in {c for _, c in obs}:
            J.nota("convencion" if J.v25 else "version", "PD1-7", "Observation.valueCodeableConcept: %r para %r, fuera del ConceptMap "
                   "(la 0315 es user-defined)" % (obs, v), citas=C["PD1-7"])
    elif tuple(t) not in obs:
        if any(s == S0315 for s, _ in obs):
            J.cuenta("valor_distinto", "PD1-7", "Observation.valueCodeableConcept: esperado %r, observado %r" % (
                t[1], [c for s, c in obs if s == S0315]), citas=C["PD1-7"])
        else:
            J.cuenta("codigo_mal_mapeado", "PD1-7", "Observation.valueCodeableConcept: esperado %r (de %r), observado %r" % (t, v, obs),
                     citas=C["PD1-7"])
    _sujeto(J, m, r, entry, pat_entry, "Observation.subject", "PD1-7")


def _juzgar(J, m, lec, familia):'''))
CV.append(("el perfil de ADT: la fila de PD1-7",
           '''"citas": SIN_DESTINO_ADT["ACC"]["citas"] + SIN_DESTINO_ADT["PDA"]["citas"]},\n''',
           '''"citas": SIN_DESTINO_ADT["ACC"]["citas"] + SIN_DESTINO_ADT["PDA"]["citas"]},\n'''
           '''    {"elemento": "Observation (de PD1-7)", "campo": "PD1-7", "regla": "IF PD1-7 VALUED: valueCodeableConcept por la 0315 (identidad), '''
           '''status y subject; se reconoce por el sistema de la 0315 o el código de PD1-7; sin ella, recurso ausente (L-CV-18, etapa 40)", '''
           '''"nivel": "cuenta", "citas": C["PD1-7"]},\n'''))
CV.append(("S-CV-4",
           "Observation por OBX) resolviendo las referencias del Bundle.",
           "Observation por OBX y, desde la etapa 40, la de PD1-7 por su valor o el sistema de la 0315) resolviendo las referencias del "
           "Bundle."))
CV.append(("L-CV-17 sin PD1-7 en su primer riesgo",
           '''de solo Y/N que no sale de ACC ni de PDA (la de PD1-7, que la guía sí mapea, o una "
                   "inventada) se da por de ellos''',
           '''de solo Y/N que no sale de ACC ni de PDA (una inventada, o la de PD1-7 cuando el "
                   "conversor no la saca como valueCodeableConcept) se da por de ellos'''))
CV.append(("L-CV-18",
           '''"por la del OBX, que en ADT no se proyecta)."}''',
           '''"por la del OBX, que en ADT no se proyecta).",
        "L-CV-18": "Etapa 40: la Observation de PD1-7 (PD1[Observation-LivingWill]) se reconoce solo con PD1-7 valorado, por un coding "
                   "de su valueCodeableConcept con el sistema de la 0315 o con el código de PD1-7; una por mensaje, la primera con el "
                   "sistema. El paquete solo fija PD1-7 → valueCodeableConcept, así que code, effective[x] y lo demás no se juzgan. Con "
                   "otro value[x] no se reconoce: sale recurso_ausente de PD1-7 y la Observation sigue por los pasos de siempre "
                   "(recurso_inventado, o ACC/PDA por la 0136). Con PD1-7 en Y o N y ACC o PDA con ese valor, dos Observation de solo "
                   "Y/N sin sistema no se distinguen: la primera es la de PD1-7. Solo en ADT: la hoja de ORU también la crea "
                   "(MSG_ORU_R01.csv:17) y en oru_conv sigue como recurso_inventado."}'''))

MCP = [("la entrada de la etapa 40 en el texto de versión",
        'REVISION = ("etapa 37: ',
        'REVISION = ("etapa 40: la Observation de PD1-7 en adt_conv (S-CV-4) y L-CV-18; "\n            "antes, etapa 37: ')]
EXT = [("la 0315 en la lista del paquete",
        '"table-hl70085-to-observation-status", "table-hl70123-queries-to-diagnostic-report-status"]',
        '"table-hl70085-to-observation-status", "table-hl70123-queries-to-diagnostic-report-status",\n'
        '         "table-hl70315-to-v2-0315"]   # etapa 40')]


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
    open(p, "w", encoding="utf-8", newline="").write(t)
    print("%s: %s" % (os.path.basename(p), ", ".join(hechos) if hechos else "ya estaba"))


def main(carpeta=AQUI):
    aplica(os.path.join(carpeta, "conversion.py"), CV)
    aplica(os.path.join(carpeta, "mcp_verificador.py"), MCP)
    aplica(os.path.join(carpeta, "cv", "extraer_mapas.py"), EXT)
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
