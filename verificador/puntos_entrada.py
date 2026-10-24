#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Puntos de entrada (PE): el contrato del receptor como DATOS (diseno-multitipo-fable.md §1 y §4; S47-S56).

Un PE dice qué ofrece el receptor en un puerto: tipos/eventos aceptados con su estructura (tabla 0354), qué campos
consume (S6/S17: dónde cuenta el 102 de S10), qué obligatorios vacíos juzga (P4), qué tipos de dato y tablas juzga
(P5) y con qué nivel («consumido» cuenta; «estricto» se anota y cuenta solo a petición; «nota» nunca cuenta: campos
condicionales C, L-MT6). Se declara, no se infiere de MSH-9 (§1.1).

`adt_a01` reproduce EXACTAMENTE el verificador de hoy: sus literales (POS, OBLIGATORIOS, consumidos, p4, p5) están
aquí MOVIDOS desde acuse_referencia.py, en el mismo orden (el orden decide el primer err y las tolerancias), y conserva
la `estructura()` plana (`estructura_plana`). Los demás PE usan la gramática de estructuras_25.json con el emparejador
recursivo (estructuras_hl7.emparejar). Al importar, se afirma que ambas fuentes coinciden sobre ADT_A01 (§3.1).

Formato: p4 = [(segmento, campo | (campo, campo) «al menos uno», nivel)]; p5 = [(segmento, campo, juicio, nivel)] con
juicio «ts» | «nm» | número de tabla; PID-7 «ts» lleva además P5f [S18]. Las longitudes de los campos juzgados por
los PE nuevos salen de los atributos extraídos del texto (P1b [S3])."""
import estructuras_hl7 as EH

# --- literales de hoy, MOVIDOS desde acuse_referencia.py (:100-102, :223, :499-514, :541-566, :569, :577)
POS = {"MSH": 0, "SFT": 1, "EVN": 2, "PID": 3, "PD1": 4, "NK1": 6, "PV1": 7, "PV2": 8, "DB1": 10, "OBX": 11,
       "AL1": 12, "DG1": 13, "DRG": 14, "PR1": 15, "GT1": 17, "IN1": 18, "IN2": 18, "IN3": 18, "ACC": 22,
       "UB1": 23, "UB2": 24, "PDA": 25}                                  # [E3 §3.3.1]; ROL exento
OBLIGATORIOS = ("EVN", "PID", "PV1")                                      # [E3 §3.3.1] cardinalidad [1..1]
CONSUMIDOS_ADT = {("MSH", 3), ("MSH", 4), ("MSH", 9), ("MSH", 10), ("MSH", 11), ("PID", 3), ("PID", 5), ("PID", 7), ("PID", 8)}
P4_ADT = [("MSH", 10, "consumido"), ("PID", 3, "consumido"), ("PID", 5, "consumido"),
          ("MSH", 7, "estricto"), ("EVN", 2, "estricto"), ("PV1", 2, "estricto")]
P5_ADT = [("MSH", 7, "ts", "estricto"), ("MSH", 18, "0211", "estricto"), ("EVN", 1, "0003", "estricto"), ("EVN", 2, "ts", "estricto"),
          ("PID", 1, "nm", "estricto"), ("PID", 7, "ts", "consumido"), ("PID", 8, "0001", "consumido"),
          ("PV1", 1, "nm", "estricto"), ("PV1", 2, "0004", "estricto")]
ORDEN_SEG_ADT = {"MSH": 0, "EVN": 1, "PID": 2, "PV1": 3}
MSH_CONSUMIDOS = {("MSH", 3), ("MSH", 4), ("MSH", 9), ("MSH", 10), ("MSH", 11)}


def _tipos(*prefijos):
    """{MSH-9.1: {MSH-9.2: estructura}} con todas las estructuras de la 0354 cuyo nombre empieza por el prefijo [S47]."""
    out = {}
    for est, evs in sorted(EH.T0354.items()):
        if est.split("_")[0] in prefijos and est in EH.GRAMATICAS:
            for ev in evs:
                out.setdefault(est.split("_")[0], {})[ev] = est
    return out


def _longitudes(p4, p5, consumidos):
    """P1b [S3]: longitud máxima de cada campo juzgado, leída de los atributos del texto; solo los que LEN no trae."""
    out = {}
    campos = {(s, n) for s, n, _ in p4 if isinstance(n, int)} | {(s, n) for s, n, _, _ in p5} | set(consumidos)
    for s, n, _ in p4:
        if isinstance(n, tuple):
            campos |= {(s, k) for k in n}
    for s, n in sorted(campos):
        at = EH.CAMPOS.get("%s-%d" % (s, n))
        if at and at.get("len"):
            out[(s, n)] = at["len"]
    return out


def _pe(nombre, puerto, tipos, consumidos, p4, p5, descripcion, estructura_plana=None, orden_seg=None, **extra):
    """`extra` (diseno-oru-fable.md §5.1): mapeador, todas_las_ocurrencias (DV-ORU-1), zona_emisor [S66]. Solo se añaden al PE
    que las declara: en los demás las claves FALTAN y ninguna rama nueva se ejecuta."""
    pe = {"nombre": nombre, "puerto": puerto, "tipos": tipos, "estructura_plana": estructura_plana,
          "consumidos": set(consumidos), "p4": list(p4), "p5": list(p5), "orden_seg": orden_seg, "descripcion": descripcion}
    pe["longitudes"] = {} if estructura_plana else _longitudes(p4, p5, consumidos)
    pe.update({k: v for k, v in extra.items() if v is not None})
    return pe


PUNTOS = {}
PUNTOS["adt_a01"] = _pe(
    "adt_a01", 2575, {"ADT": {"A01": "ADT_A01"}}, CONSUMIDOS_ADT, P4_ADT, P5_ADT,
    "El punto de entrada de hoy (USER, AdtTcpIn): solo ADT^A01^ADT_A01; estructura plana [E3 §3.3.1]; contrato del laboratorio.",
    estructura_plana=(POS, OBLIGATORIOS), orden_seg=ORDEN_SEG_ADT)
PUNTOS["adt"] = _pe(                                                        # §4: todos los ADT de la tabla [S47]
    "adt", 2580, _tipos("ADT"), CONSUMIDOS_ADT | {("MRG", 1)},
    [("MSH", 10, "consumido"), ("PID", 3, "consumido"), ("PID", 5, "consumido"), ("MRG", 1, "consumido"),
     ("MSH", 7, "estricto"), ("EVN", 2, "estricto"), ("PV1", 2, "estricto")],
    P5_ADT,
    "Todos los eventos ADT con estructura en la tabla 0354 [S47]; MSH-10, PID-3, PID-5 y MRG-1 (A39/A45) consumidos [S49].")
PUNTOS["oru"] = _pe(
    "oru", 2581, _tipos("ORU"), MSH_CONSUMIDOS | {("PID", 3), ("PID", 7), ("PID", 8), ("OBR", 4), ("OBX", 11)},
    [("MSH", 10, "consumido"), ("PID", 3, "consumido"), ("OBR", 4, "consumido"),
     ("MSH", 7, "estricto"), ("OBX", 3, "estricto"), ("PV1", 2, "estricto")],
    [("MSH", 7, "ts", "estricto"), ("MSH", 18, "0211", "estricto"), ("PID", 7, "ts", "consumido"), ("PID", 8, "0001", "consumido"),
     ("PV1", 2, "0004", "estricto"), ("OBR", 7, "ts", "estricto"), ("OBX", 2, "0125", "estricto"), ("OBX", 11, "0085", "consumido")],
    "ORU^R01: MSH-10, PID-3 (si hay PID) y OBR-4 consumidos; OBX-11 (0085) consumido; sin OBX es AA [S55]; PID-5 no se consume (L-MT8).")
PUNTOS["siu"] = _pe(
    "siu", 2582, _tipos("SIU", "SRM"), MSH_CONSUMIDOS | {("PID", 3), ("PID", 7), ("PID", 8), ("SCH", 1), ("SCH", 2), ("ARQ", 1)},
    [("MSH", 10, "consumido"), ("SCH", (1, 2), "consumido"), ("ARQ", 1, "consumido"), ("PID", 3, "consumido"),
     ("MSH", 7, "estricto"), ("SCH", 6, "estricto"), ("SCH", 16, "estricto"), ("SCH", 20, "estricto"),
     ("ARQ", 15, "estricto"), ("ARQ", 19, "estricto"), ("RGS", 1, "estricto"), ("AIS", 3, "estricto")],
    [("MSH", 7, "ts", "estricto"), ("MSH", 18, "0211", "estricto"), ("PID", 7, "ts", "consumido"), ("PID", 8, "0001", "consumido")],
    "SIU^S12-S26 y SRM^S01-S11: MSH-10, SCH-1 o SCH-2 (AMB-MT-5), ARQ-1 y PID-3 (si hay PID) consumidos; TQ compuestos no se juzgan (L-MT5).")
PUNTOS["ord"] = _pe(
    "ord", 2583, _tipos("ORM", "OMG", "OMP", "RAS"),
    MSH_CONSUMIDOS | {("PID", 3), ("PID", 7), ("PID", 8), ("ORC", 1), ("OBR", 4), ("RXO", 1), ("RXA", 3), ("RXA", 5)},
    [("MSH", 10, "consumido"), ("PID", 3, "consumido"), ("ORC", 1, "consumido"), ("OBR", 4, "consumido"), ("RXO", 1, "nota"),
     ("RXA", 5, "consumido"), ("MSH", 7, "estricto"), ("ORC", 2, "nota"), ("ORC", 3, "nota"), ("RXR", 1, "estricto")],
    [("MSH", 7, "ts", "estricto"), ("MSH", 18, "0211", "estricto"), ("PID", 7, "ts", "consumido"), ("PID", 8, "0001", "consumido"),
     ("ORC", 1, "0119", "consumido"), ("OBR", 7, "ts", "estricto"), ("RXA", 1, "nm", "estricto"), ("RXA", 2, "nm", "estricto"),
     ("RXA", 3, "ts", "consumido"), ("RXA", 4, "ts", "estricto"), ("RXA", 6, "nm", "estricto")],
    "ORM^O01, OMG^O19, OMP^O09, RAS^O17: MSH-10, PID-3, ORC-1 (0119), OBR-4, RXA-5 y RXA-3 consumidos; RXO-1 y ORC-2/3 son C: solo nota (L-MT6); contesta ACK [S56].")
PUNTOS["mdm"] = _pe(
    "mdm", 2584, _tipos("MDM"), MSH_CONSUMIDOS | {("PID", 3), ("PID", 7), ("PID", 8), ("TXA", 2), ("TXA", 12), ("TXA", 17)},
    [("MSH", 10, "consumido"), ("PID", 3, "consumido"), ("TXA", 2, "consumido"), ("TXA", 12, "consumido"),
     ("MSH", 7, "estricto"), ("EVN", 2, "estricto"), ("PV1", 2, "estricto"), ("OBX", 3, "estricto")],
    [("MSH", 7, "ts", "estricto"), ("MSH", 18, "0211", "estricto"), ("EVN", 1, "0003", "estricto"), ("EVN", 2, "ts", "estricto"),
     ("PID", 7, "ts", "consumido"), ("PID", 8, "0001", "consumido"), ("PV1", 2, "0004", "estricto"), ("TXA", 1, "nm", "estricto"),
     ("TXA", 17, "0271", "consumido"), ("OBX", 11, "0085", "estricto")],
    "MDM^T01-T11: MSH-10, PID-3, TXA-2 y TXA-12 consumidos; TXA-17 (0271) consumido.")
# diseno-oru-fable.md §5.1 [S57]: ORU^R01 con destino FHIR (namespace LABORU, 2585). `oru` (2581, sin destino) queda intacto.
PUNTOS["oru_fhir"] = _pe(
    "oru_fhir", 2585, _tipos("ORU"),
    MSH_CONSUMIDOS | {("PID", 3), ("PID", 7), ("PID", 8), ("OBR", 2), ("OBR", 3), ("OBR", 4), ("OBR", 7), ("OBR", 8), ("OBR", 22), ("OBR", 25),
                      ("OBX", 2), ("OBX", 3), ("OBX", 4), ("OBX", 5), ("OBX", 6), ("OBX", 7), ("OBX", 8), ("OBX", 11), ("OBX", 14)},
    [("MSH", 10, "consumido"), ("PID", 3, "consumido"), ("OBR", 4, "consumido"), ("OBX", 3, "consumido"), ("OBX", 11, "consumido"),
     ("MSH", 7, "estricto"), ("OBR", 7, "nota"), ("OBR", 25, "nota"), ("OBX", 2, "nota"), ("PV1", 2, "estricto")],
    [("MSH", 7, "ts", "estricto"), ("MSH", 18, "0211", "estricto"), ("PID", 7, "ts", "consumido"), ("PID", 8, "0001", "consumido"),
     ("PV1", 2, "0004", "estricto"), ("OBR", 7, "ts", "consumido"), ("OBR", 8, "ts", "consumido"), ("OBR", 22, "ts", "consumido"),
     ("OBR", 25, "0123", "consumido"), ("OBX", 2, "0125", "consumido"), ("OBX", 5, "valor_por_tipo", "consumido"),
     ("OBX", 8, "0078", "estricto"), ("OBX", 11, "0085", "consumido"), ("OBX", 14, "ts", "consumido")],
    "ORU^R01 con destino FHIR (Observation por OBX, DiagnosticReport por OBR); mapeador oru; todas las ocurrencias de OBR/OBX juzgadas.",
    mapeador="oru", todas_las_ocurrencias={"OBR", "OBX"}, zona_emisor="+01:00")
PUNTOS["oru_fhir"]["longitudes"].pop(("OBX", 2), None)       # DV-ORU-6: OBX-2 no se trunca a 2 (v2.6 lo amplía a 3; «CWE» por S22)
# diseno-adt-fable.md §4.1 [S-ADT-1]: ADT de los 8 eventos con destino FHIR (namespace LABADT, 2586). `adt` y `adt_a01` intactos.
# S78: PV1-19 no es clave (no va a P4). S95: PV1-2 consumido (vacío -> AE 101; el perfil del sitio lo tolera con un mando).
PUNTOS["adt_fhir"] = _pe(
    "adt_fhir", 2586,
    {"ADT": {"A01": "ADT_A01", "A02": "ADT_A02", "A03": "ADT_A03", "A04": "ADT_A01", "A08": "ADT_A01", "A11": "ADT_A09",
             "A13": "ADT_A01", "A31": "ADT_A05"}},
    MSH_CONSUMIDOS | {("PID", 3), ("PID", 5), ("PID", 7), ("PID", 8), ("PID", 11), ("PID", 13), ("PID", 14), ("PID", 16),
                      ("PID", 29), ("PID", 30), ("PV1", 2), ("PV1", 3), ("PV1", 4), ("PV1", 6), ("PV1", 7), ("PV1", 8),
                      ("PV1", 10), ("PV1", 11), ("PV1", 14), ("PV1", 17), ("PV1", 19), ("PV1", 36), ("PV1", 44), ("PV1", 45)},
    [("MSH", 10, "consumido"), ("PID", 3, "consumido"), ("PID", 5, "consumido"), ("PV1", 2, "consumido"),
     ("MSH", 7, "estricto"), ("EVN", 2, "estricto")],
    [("MSH", 7, "ts", "estricto"), ("MSH", 18, "0211", "estricto"), ("EVN", 1, "0003", "estricto"), ("EVN", 2, "ts", "estricto"),
     ("PID", 1, "nm", "estricto"), ("PID", 7, "ts", "consumido"), ("PID", 8, "0001", "consumido"), ("PID", 29, "ts", "consumido"),
     ("PID", 30, "0136", "consumido"), ("PV1", 1, "nm", "estricto"), ("PV1", 2, "0004", "consumido"),
     ("PV1", 44, "ts", "consumido"), ("PV1", 45, "ts", "consumido")],
    "ADT A01/A02/A03/A04/A08/A11/A13/A31 con destino FHIR (Patient por PID, Encounter por PV1; namespace LABADT); mapeador adt.",
    mapeador="adt", zona_emisor="+01:00")
# cv/diseno-conversores-fable.md §1.5 [S-CV-1]: solo transformación (conversores de terceros, etapa 14l). Sin puerto ni
# acuse: el juez despacha a conversion.py antes de leer acuse, log o canónico. Mismo contrato de familia que adt_fhir/oru_fhir.
PUNTOS["adt_conv"] = _pe(
    "adt_conv", 0, PUNTOS["adt_fhir"]["tipos"], PUNTOS["adt_fhir"]["consumidos"], PUNTOS["adt_fhir"]["p4"], PUNTOS["adt_fhir"]["p5"],
    "ADT de los 8 eventos convertido por un tercero (HL7 v2 -> FHIR): solo transformación, sin acuse; perfil «guía» (S-CV-1..6).",
    solo_transformacion=True, familia="adt")
PUNTOS["oru_conv"] = _pe(
    "oru_conv", 0, PUNTOS["oru_fhir"]["tipos"], PUNTOS["oru_fhir"]["consumidos"], PUNTOS["oru_fhir"]["p4"], PUNTOS["oru_fhir"]["p5"],
    "ORU^R01 convertido por un tercero (HL7 v2 -> FHIR): solo transformación, sin acuse; perfil «guía» (S-CV-1..6).",
    solo_transformacion=True, familia="oru")
POR_OMISION = "adt_a01"
NOMBRES = list(PUNTOS)


def resolver(pe=None, e=None):
    """Precedencia §1.3: parámetro explícito > e["punto_entrada"] del bundle > adt_a01. Admite nombre o PE."""
    if isinstance(pe, dict):
        return pe
    nombre = pe or (e or {}).get("punto_entrada") or POR_OMISION
    if nombre not in PUNTOS:
        raise ValueError("punto de entrada desconocido: %r (válidos: %s)" % (nombre, ", ".join(NOMBRES)))
    return PUNTOS[nombre]


def estructura_de(m, pe):
    """Estructura de la tabla 0354 que el PE asigna a MSH-9.1/9.2 del mensaje (mayúsculas, S4), o None si P2 la rechaza."""
    comp9 = m.campo(m.segs[0], 9).split(m.c)
    tipo = comp9[0].upper()
    ev = comp9[1].upper() if len(comp9) > 1 else ""
    return pe["tipos"].get(tipo, {}).get(ev)


def contrato(pe):
    """El PE como datos serializables (para info_verificador)."""
    return {"nombre": pe["nombre"], "puerto": pe["puerto"], "descripcion": pe["descripcion"],
            "tipos": {t: dict(sorted(evs.items())) for t, evs in sorted(pe["tipos"].items())},
            "estructura_plana": pe["estructura_plana"] is not None,
            "consumidos": sorted("%s-%d" % c for c in pe["consumidos"]),
            "p4": ["%s-%s %s" % (s, "/".join("%s-%d" % (s, k) for k in n) if isinstance(n, tuple) else n, nv) for s, n, nv in pe["p4"]],
            "p5": ["%s-%d %s %s" % (s, n, j, nv) for s, n, j, nv in pe["p5"]],
            "longitudes": {"%s-%d" % c: v for c, v in sorted(pe["longitudes"].items())},
            **{k: (sorted(pe[k]) if isinstance(pe[k], set) else pe[k]) for k in ("mapeador", "todas_las_ocurrencias", "zona_emisor", "solo_transformacion", "familia") if k in pe}}


# ---------------------------------------------------------------------------- afirmaciones §3.1 sobre ADT_A01
def _afirmar():
    g = EH.gramatica("ADT_A01")
    assert g is not None, "estructuras_25.json no trae ADT_A01"
    pos, obl = EH.aplanar(g)
    assert obl == ["MSH"] + list(OBLIGATORIOS), "(a) obligatorios raíz de la gramática ADT_A01 %r != MSH + OBLIGATORIOS" % obl
    multi = {s for s, ps in pos.items() if len(ps) > 1}
    grupos = EH.en_grupos(g)
    assert multi == {"ROL"}, "(c) multiposición en ADT_A01 debería ser solo ROL: %r" % sorted(multi)
    assert {s for s in POS if s in grupos} == {"PR1", "IN1", "IN2", "IN3"}, "(c) segmentos de POS dentro de grupos"
    libres = [s for s in POS if s not in multi and s not in grupos]
    assert len(libres) == 18, "(b) %d segmentos raíz fuera de grupos, se esperaban 18" % len(libres)
    plano = {s: ps[0] for s, ps in pos.items()}
    malos = [(a, b) for a in libres for b in libres if (POS[a] < POS[b]) != (plano[a] < plano[b])]
    assert not malos, "(b) la relación de orden de POS no es la de la gramática: %r" % malos[:5]
    assert set(POS) | {"ROL"} == set(pos), "los segmentos de POS (+ROL) son los de la gramática: %r" % sorted(set(POS) ^ set(pos))
    for pe in PUNTOS.values():                                       # cada estructura aceptada tiene gramática
        for t, evs in pe["tipos"].items():
            for ev, est in evs.items():
                assert est in EH.GRAMATICAS, "%s: %s^%s -> %s sin gramática" % (pe["nombre"], t, ev, est)


_afirmar()
