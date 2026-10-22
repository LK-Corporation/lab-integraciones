#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa ADT, A1 (diseno-adt-fable.md §1.2-§3, con S75-S95 de RESULTADO-A0.md): un mensaje ADT de HL7 v2.5 -> los recursos
FHIR R4 Patient y Encounter que deben quedar en el almacén, en la forma de a1/contrato_forma_salida.md (la que se compara con
el oráculo ciego congelado en oraculo_adt/).

  fhir(texto) -> {"evento", "estructura", "Patient", "Encounter", "accion", "notas"}
  analizar(texto) -> (lo mismo sin "notas", notas)

Es la PROYECCIÓN: lo que se escribe si el circuito acepta el mensaje. El acuse (AE/AR) lo juzga acuse_referencia; aquí, un
valor inválido se omite del recurso y deja una nota («NO-n: …»), nunca se inventa. Fuentes, por fila, en los comentarios:
[CM <nombre>] = ConceptMap del paquete HL7 v2-to-FHIR; [E3 n] = Ch03.txt:n; [E2A n] = CH02A.txt:n; S-n = decisión del sitio.
Solo biblioteca estándar y los lectores del verificador (mapeador_referencia: cable, §2.7, DTM; mapeador_oru: dateTime).

  python3 mapeador_adt.py --autoprueba
  python3 mapeador_adt.py <fichero.hl7>          (imprime fhir() en JSON)
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adjudicacion as A          # noqa: E402
import mapeador_referencia as MR  # noqa: E402
import mapeador_oru as MO         # noqa: E402

V2 = "http://terminology.hl7.org/CodeSystem/v2-%s"
SIS_MRN = "urn:lab:integraciones:mrn"          # D-ADT-1 (= FhirPatient.cls:64 y S58)
SIS_VISIT = "urn:lab:integraciones:visit"      # D-ADT-1
SIS_LOC = "urn:lab:integraciones:loc"          # D-ADT-1, S82
SIS_PROF = "urn:lab:integraciones:prof"        # D-ADT-1, S83
ACTCODE = "http://terminology.hl7.org/CodeSystem/v3-ActCode"
NULLFLAVOR = "http://terminology.hl7.org/CodeSystem/v3-NullFlavor"
PARTTYPE = "http://terminology.hl7.org/CodeSystem/v3-ParticipationType"
ZONA = MO.ZONA_POR_OMISION                     # S66: zona fija del emisor (+01:00) para un DTM con hora y sin zona

# [tabla 0354] evento -> estructura (estructuras_25.json)
ESTRUCTURA = {"A01": "ADT_A01", "A04": "ADT_A01", "A08": "ADT_A01", "A13": "ADT_A01", "A02": "ADT_A02", "A03": "ADT_A03",
              "A11": "ADT_A09", "A31": "ADT_A05"}
# [CM table-hl70001-to-administrative-gender]
M0001 = {"F": "female", "M": "male", "O": "other", "U": "unknown", "A": "other", "N": "other"}
# [CM table-hl70004-to-v3-actcode]: grupo 1 a v3-ActCode, grupo 2 a v2-0004
M0004_CLASE = {"E": (ACTCODE, "EMER"), "I": (ACTCODE, "IMP"), "O": (ACTCODE, "AMB"), "P": (ACTCODE, "PRENC"),
               "R": (V2 % "0004", "R"), "B": (V2 % "0004", "B"), "C": (V2 % "0004", "C"), "N": (V2 % "0004", "N"),
               "U": (V2 % "0004", "U")}
# [CM table-hl70004-to-encounter-status]
M0004_ESTADO = {"E": "in-progress", "I": "in-progress", "O": "in-progress", "P": "planned", "R": "in-progress",
                "B": "in-progress", "C": "in-progress", "N": "in-progress", "U": "unknown"}
# [CM table-hl70003-to-encounter-status]; solo la invoca message-adt-a11-to-bundle (MSH -> Encounter), y S95 con PV1-2 vacío
M0003_ESTADO = {"A01": "in-progress", "A02": "in-progress", "A03": "finished", "A04": "planned", "A05": "planned",
                "A08": "unknown", "A11": "cancelled", "A13": "in-progress"}
# [CM table-hl70200-to-name-use]; los demás códigos de la 0200 no tienen destino (sin use)
M0200 = {"BAD": "old", "D": "usual", "L": "official", "M": "maiden", "MSK": "anonymous", "N": "nickname", "NAV": "temp",
         "R": "official", "TEMP": "temp"}
T0200 = set(M0200) | {"A", "B", "C", "F", "I", "K", "NB", "NOUSE", "P", "REL", "S", "T", "U"}
# [CM table-hl70190-to-address-use] y [CM table-hl70190-to-address-type]
M0190_USO = {"BA": "old", "BI": "billing", "C": "temp", "B": "work", "H": "home", "O": "work"}
M0190_TIPO = {"M": "postal", "SH": "postal"}
# [CM table-hl70201-to-contact-point-use] y [CM table-hl70202-to-contact-point-system]
M0201 = {"PRN": "home", "WPN": "work", "PRS": "mobile"}
M0202 = {"PH": "phone", "FX": "fax", "MD": "other", "SAT": "other", "BP": "pager", "Internet": "email", "X.400": "email",
         "TDD": "other", "TTY": "other"}
# [CM table-hl70002-to-v3-maritalstatus]
MARITAL = "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus"
M0002 = {"A": (MARITAL, "L"), "D": (MARITAL, "D"), "M": (MARITAL, "M"), "S": (MARITAL, "S"), "W": (MARITAL, "W"),
         "C": (MARITAL, "C"), "G": (MARITAL, "T"), "P": (MARITAL, "T"), "R": (MARITAL, "T"), "E": (MARITAL, "L"),
         "N": (MARITAL, "A"), "I": (MARITAL, "I"), "B": (MARITAL, "U"), "U": (NULLFLAVOR, "UNK"), "O": (NULLFLAVOR, "OTH"),
         "T": (NULLFLAVOR, "NAVU")}
# [CM table-hl70136-to-special-values]
M0136 = {"Y": True, "N": False}
# [CM segment-pv1-to-encounter] PV1-7/8/17: constantes asignadas por el mapa (AMB-ADT-3 / S94: tal cual)
PARTICIPANTES = ((7, "ATND", "display", "attender"), (8, "REF", "text", "referrer"), (17, "ADM", "text", "admitter"))
NULO = '""'                                     # [E2 §2.5.3] valor nulo explícito


class Lector:
    """Acceso a campos, componentes y subcomponentes de un Msg de mapeador_referencia, con §2.7 resuelto y las notas."""

    def __init__(self, m):
        self.m = m
        self.notas = []

    def campo(self, seg, n):
        return self.m.campo(seg, n) if seg else ""

    def reps(self, seg, n):
        v = self.campo(seg, n)
        return [r for r in v.split(self.m.r)] if v else []

    def comps(self, rep):
        return rep.split(self.m.c)

    def texto(self, crudo, donde):
        """Componente o subcomponente -> texto FHIR. «""» (nulo de v2) y vacío -> None (D-ADT-8: con el PUT completo de S79
        omitir el elemento ya lo borra en el almacén). Escapes §2.7 resueltos; blancos de los bordes fuera (D-ADT-9)."""
        if crudo is None or crudo == "":
            return None
        if crudo == NULO:
            self.nota("D-ADT-8: %s = \"\" (nulo de v2): el elemento se omite" % donde)
            return None
        t = self.m.desescapa(crudo).strip()
        return t or None

    def comp(self, rep, i, donde):
        c = self.comps(rep)
        return self.texto(c[i - 1] if len(c) >= i else "", donde)

    def sub1(self, rep, i, donde):
        """Primer subcomponente del componente i (HD.1, CWE.1 de un componente compuesto…)."""
        c = self.comps(rep)
        v = c[i - 1] if len(c) >= i else ""
        return self.texto(v.split(self.m.s)[0], donde)

    def nota(self, t):
        if t not in self.notas:
            self.notas.append(t)


def _limpio(x):
    """FHIR no admite valores vacíos (contrato): fuera None, "", {} y [] a cualquier profundidad."""
    if isinstance(x, dict):
        d = {k: _limpio(v) for k, v in x.items()}
        return {k: v for k, v in d.items() if v not in (None, "", {}, [])}
    if isinstance(x, list):
        l = [_limpio(v) for v in x]
        return [v for v in l if v not in (None, "", {}, [])]
    return x


def _fecha_hora(L, crudo, donde):
    """[E2A 1713-1733] DTM -> dateTime FHIR con la precisión del origen (mapeador_oru.fecha_hora); sin zona -> S66; blancos en
    los bordes -> inválido (L23). Inválido -> None y nota (el acuse lo rechaza: AE 102)."""
    v = (crudo or "").split(L.m.c)[0]
    if v == "" or v == NULO:
        return None
    if v != v.strip():
        L.nota("NO-1: %s %r con blancos en los bordes: inválido (L23), se omite" % (donde, v))
        return None
    r, prob = MO.fecha_hora(v, ZONA, L.m.c)
    if prob:
        L.nota("NO-1: %s %s: se omite" % (donde, prob))
        return None
    return r or None


def _codigo(L, crudo, tabla, mapa, donde, hl7=False):
    """Código de una tabla: con mapa -> el destino; sin él -> {system v2-NNNN, code literal} y nota (contrato). Minúscula: S4."""
    c = L.texto(crudo, donde)
    if c is None:
        return None
    k = c if c in mapa else (c.upper() if c.upper() in mapa else None)
    if k is not None and k != c:
        L.nota("S4: %s %r en minúscula se lee como %r" % (donde, c, k))
    if k is None:
        L.nota("NO-2: %s %r sin destino en el mapa de la tabla %s: código literal en v2-%s%s"
               % (donde, c, tabla, tabla, " (AE 103 en el acuse si ≤ 2.5)" if hl7 else ""))
        return {"system": V2 % tabla, "code": c}
    s, code = mapa[k] if isinstance(mapa[k], tuple) else (V2 % tabla, mapa[k])
    return {"system": s, "code": code}


# ---------------------------------------------------------------------------- Patient [CM segment-pid-to-patient]
def _identificador_paciente(L, pid):
    """PID-3 -> identifier: UNA entrada, la repetición elegida por la regla del contrato ADT ([C]: CX.5 = MR; si ninguna, la
    primera con CX.1), todas las repeticiones miradas [V]; system del laboratorio (D-ADT-1); S89: las demás no viajan.
    [CM datatype-cx-to-identifier] CX.1 -> value, CX.5 -> type.coding.code (0203)."""
    reps = [L.comps(r) for r in L.reps(pid, 3)]
    eleg = next((c for c in reps if len(c) > 4 and c[4] == "MR"), None) or next((c for c in reps if c[0]), None)
    if eleg is None:
        return None
    if len([c for c in reps if c[0]]) > 1:
        L.nota("S89: PID-3 trae %d identificadores; solo viaja el del laboratorio" % len([c for c in reps if c[0]]))
    valor = L.texto(eleg[0], "PID-3.1")
    if valor is None:
        return None
    tipo = L.texto(eleg[4] if len(eleg) > 4 else "", "PID-3.5")
    ident = {"system": SIS_MRN, "value": valor}
    if tipo:
        ident["type"] = {"coding": [{"system": V2 % "0203", "code": tipo}]}
    return ident


def _given(L, c, i, donde):
    """S96 (AMB-ADT-4, Jev 0,91 y Víctor, 10-oct): el componente i (XPN.2 / XCN.3) entero es given[1] (literal de [CM
    datatype-xpn-to-humanname] XPN.2 -> given[1]); el siguiente (XPN.3 / XCN.4, «second and further given names») se parte
    por espacios ([E3 4975-4976]). «Luis Miguel^» -> ["Luis Miguel"]; «Ana^María José» -> ["Ana", "María", "José"]."""
    primero = L.texto(c[i] if len(c) > i else "", "%s.%d" % (donde, i + 1))
    resto = L.texto(c[i + 1] if len(c) > i + 1 else "", "%s.%d" % (donde, i + 2))
    return ([primero] if primero else []) + ([w for w in resto.split(" ") if w] if resto else [])


def _nombres(L, pid):
    """PID-5 -> name[]: TODAS las repeticiones con apellido o nombre, en orden (S84). [CM datatype-xpn-to-humanname]: XPN.1
    (FN.1, subcomponentes unidos por espacio [D]) -> family; XPN.2/XPN.3 -> given según S96; XPN.4 -> suffix[1]; XPN.6 ->
    suffix[2] (DV-ADT-1: el diseño no lo listaba); XPN.5 -> prefix; XPN.7 -> use por la 0200. XPN.14 y el resto: L-ADT-14."""
    out = []
    for i, rep in enumerate(L.reps(pid, 5), 1):
        c = L.comps(rep)
        fam_subs = [L.texto(s, "PID-5.1") for s in (c[0].split(L.m.s) if c else [])]
        fam = " ".join(s for s in fam_subs if s) or None
        given = _given(L, c, 1, "PID-5")
        if not fam and not given:
            continue
        uso_c = L.texto(c[6] if len(c) > 6 else "", "PID-5.7")
        uso = None
        if uso_c:
            k = uso_c if uso_c in T0200 else (uso_c.upper() if uso_c.upper() in T0200 else None)
            if k is None:
                L.nota("NO-2: PID-5.7 %r fuera de la 0200: sin use" % uso_c)
            else:
                uso = M0200.get(k)
        out.append({"use": uso, "family": fam, "given": given,
                    "prefix": [L.texto(c[4] if len(c) > 4 else "", "PID-5.5")],
                    "suffix": [L.texto(c[3] if len(c) > 3 else "", "PID-5.4"), L.texto(c[5] if len(c) > 5 else "", "PID-5.6")]})
    return out


def _direcciones(L, pid):
    """PID-11 -> address[] (S-ADT-19). [CM datatype-xad-to-address]: XAD.1 (SAD.1-3) -> line[1-3], XAD.2 -> line[4], XAD.3 city,
    XAD.4 state, XAD.5 postalCode, XAD.6 country, XAD.7 -> use (0190) o type (M, SH). XAD.9/10/12-14: L-ADT-14."""
    out = []
    for rep in L.reps(pid, 11):
        c = L.comps(rep)
        sad = c[0].split(L.m.s) if c else []
        linea = [L.texto(s, "PID-11.1") for s in sad[:3]] + [L.comp(rep, 2, "PID-11.2")]
        d = {"line": [x for x in linea if x], "city": L.comp(rep, 3, "PID-11.3"), "state": L.comp(rep, 4, "PID-11.4"),
             "postalCode": L.comp(rep, 5, "PID-11.5"), "country": L.comp(rep, 6, "PID-11.6")}
        t = L.comp(rep, 7, "PID-11.7")
        if t in M0190_USO:
            d["use"] = M0190_USO[t]
        elif t in M0190_TIPO:
            d["type"] = M0190_TIPO[t]
        elif t:
            L.nota("NO-2: PID-11.7 %r sin destino en address-use ni address-type" % t)
        d = _limpio(d)
        if d:
            out.append(d)
    return out


def _telecom(L, rep, campo):
    """[CM datatype-xtn-to-contactpoint] con S88: XTN.3 -> system (0202); XTN.3 vacío y XTN.4 -> email; XTN.3 vacío sin XTN.4 ->
    phone (S88, en vez de data-absent-reason). Valor: Internet/X.400 -> XTN.4; si no, XTN.12 si valorado; si no, XTN.1
    (DV-ADT-2: el orden XTN.12 > XTN.1 es el del ConceptMap; S88 solo simplifica las fórmulas de XTN.5-8, que son L-ADT-6).
    use: XTN.2 por la 0201; vacío -> home (PID-13) / work (PID-14) [CM segment-pid-to-patient]; CP -> use mobile."""
    eq = L.comp(rep, 3, "PID-%d.3" % campo)
    x4 = L.comp(rep, 4, "PID-%d.4" % campo)
    if eq in ("Internet", "X.400"):
        valor = x4
    else:
        valor = L.comp(rep, 12, "PID-%d.12" % campo) or L.comp(rep, 1, "PID-%d.1" % campo)
        if valor is None and x4 and not eq:
            valor = x4
    if valor is None:
        L.nota("NO-3: PID-%d con una repetición sin valor de contacto: no se escribe" % campo)
        return None
    uso_c = L.comp(rep, 2, "PID-%d.2" % campo)
    uso = M0201.get(uso_c) if uso_c else ("home" if campo == 13 else "work")
    if uso_c and uso is None:
        L.nota("NO-2: PID-%d.2 %r sin destino en contact-point-use" % (campo, uso_c))
    if eq == "CP":
        sistema, uso = "phone", "mobile"
    elif eq:
        sistema = M0202.get(eq)
        if sistema is None:
            L.nota("NO-2: PID-%d.3 %r sin destino en contact-point-system" % (campo, eq))
    else:
        sistema = "email" if (x4 and valor == x4) else "phone"
    return {"system": sistema, "value": valor, "use": uso}


def patient(L, pid, msh):
    p = {"identifier": [_identificador_paciente(L, pid)], "name": _nombres(L, pid)}
    # PID-7 -> birthDate, solo la fecha (S85; D-ADT-6: la del DTM tal cual), precisión conservada [E2A 1713-1725]
    v7 = L.campo(pid, 7).split(L.m.c)[0]
    if v7 and v7 != NULO:
        b, prob = MR.fecha(v7, None, L.m.c)
        if prob:
            L.nota("NO-1: %s: se omite (AE 102 en el acuse)" % prob)
        elif v7 != v7.strip():
            L.nota("NO-1: PID-7 %r con blancos en los bordes: inválido (L23), se omite" % v7)
        else:
            p["birthDate"] = b
            if MR.posterior_a(v7, L.campo(msh, 7).split(L.m.c)[0]):                     # [S18] (N8): lo decide el acuse
                L.nota("S18: PID-7 posterior a MSH-7: AE 102 en el acuse; la proyección (si se aceptara) lo conserva")
            if len(MR.digitos_dtm(v7)) > 8:
                L.nota("S85: PID-7 trae hora; solo se escribe birthDate (sin patient-birthTime)")
    # PID-8 -> gender (0001); vacío -> omitido (S86); fuera de la 0001 -> sin destino: omitido + nota (AE 103 / S22)
    g = L.texto(L.campo(pid, 8), "PID-8")
    if g:
        k = g if g in M0001 else (g.upper() if g.upper() in M0001 else None)
        if k is None:
            L.nota("NO-2: PID-8 %r fuera de la 0001: gender omitido (AE 103 si ≤ 2.5; S22 si posterior)" % g)
        else:
            if k != g:
                L.nota("S4: PID-8 %r en minúscula se lee como %r" % (g, k))
            p["gender"] = M0001[k]
    # PID-29 -> deceasedDateTime; PID-30 -> deceasedBoolean IF PID-29 NOT VALUED (0136)
    d29 = _fecha_hora(L, L.campo(pid, 29), "PID-29")
    if d29:
        p["deceasedDateTime"] = d29
    elif not L.campo(pid, 29) or L.campo(pid, 29) == NULO:
        d30 = L.texto(L.campo(pid, 30), "PID-30")
        if d30:
            k = d30.upper() if d30.upper() in M0136 else None
            if k is None:
                L.nota("NO-2: PID-30 %r fuera de la 0136: se omite (AE 103)" % d30)
            else:
                p["deceasedBoolean"] = M0136[k]
    p["address"] = _direcciones(L, pid)
    p["telecom"] = [_telecom(L, r, 13) for r in L.reps(pid, 13)] + [_telecom(L, r, 14) for r in L.reps(pid, 14)]
    # PID-16 -> maritalStatus (0002, user-defined: fuera de tabla, literal + nota)
    ms = _codigo(L, L.campo(pid, 16).split(L.m.c)[0] if L.campo(pid, 16) else "", "0002", M0002, "PID-16")
    if ms:
        p["maritalStatus"] = {"coding": [ms]}
    return _limpio(p)


# ---------------------------------------------------------------------------- Encounter [CM segment-pv1-to-encounter]
def _ubicacion(L, crudo, donde, estado):
    """PL -> location[] con referencia LÓGICA (S82): identifier {SIS_LOC, PL.1^PL.2^PL.3^PL.4.1 sin componentes finales
    vacías} (D-ADT-3); PL.9 -> description [CM datatype-pl-to-location] (para PV1-3, 6 y 11: DV-ADT-3). Todo vacío -> None."""
    if not crudo or crudo == NULO:
        return None
    c = L.comps(crudo)
    partes = [L.texto(c[i] if len(c) > i else "", donde) or "" for i in range(3)]
    partes.append(L.texto((c[3] if len(c) > 3 else "").split(L.m.s)[0], donde) or "")
    while partes and partes[-1] == "":
        partes.pop()
    if not partes:
        return None
    loc = {"_recurso": "Location", "identifier": [{"system": SIS_LOC, "value": "^".join(partes)}],
           "description": L.texto(c[8] if len(c) > 8 else "", donde + ".9")}
    return {"location": loc, "status": estado}


def _participantes(L, pv1):
    """PV1-7/8/17 -> participant[] (S83): solo la primera repetición (L-ADT-15); individual lógico {SIS_PROF, XCN.1};
    [CM datatype-xcn-to-practitioner] XCN.2 (FN.1) family, XCN.3/XCN.4 given, XCN.5 suffix, XCN.6 prefix. XCN.1 vacío ->
    se omite el participante con nota. type: constantes del mapa, tal cual (S94)."""
    out = []
    for n, code, campo_txt, txt in PARTICIPANTES:
        reps = L.reps(pv1, n)
        if not reps:
            continue
        if len([r for r in reps if r]) > 1:
            L.nota("L-ADT-15: PV1-%d trae %d repeticiones; solo viaja la primera" % (n, len([r for r in reps if r])))
        rep = reps[0]
        ident = L.comp(rep, 1, "PV1-%d.1" % n)
        c = L.comps(rep)
        fam = L.texto((c[1] if len(c) > 1 else "").split(L.m.s)[0], "PV1-%d.2" % n)
        nombre = _limpio({"family": fam, "given": _given(L, c, 2, "PV1-%d" % n),
                          "suffix": [L.comp(rep, 5, "PV1-%d.5" % n)], "prefix": [L.comp(rep, 6, "PV1-%d.6" % n)]})
        if not ident and not nombre:
            continue
        if not ident:
            # DV-ADT-4: el diseño omitía el participante sin XCN.1; el mapa lo mapea igual (XCN.2-6 -> name): se escribe
            # con el nombre y sin identifier (en el circuito, Reference.display)
            L.nota("DV-ADT-4: PV1-%d sin XCN.1: Practitioner solo con el nombre" % n)
        coding = {"system": PARTTYPE, "code": code}
        tipo = {"coding": [coding]}
        if campo_txt == "display":
            coding["display"] = txt
        else:
            tipo["text"] = txt
        out.append((n, {"type": [tipo], "individual": {"_recurso": "Practitioner",
                                                       "identifier": [{"system": SIS_PROF, "value": ident}] if ident else None,
                                                       "name": [nombre]}}))
    return out                                                      # [(campo PV1-n, participante)]


def encounter(L, pv1, evento, version):
    """-> (Encounter o None, acción). §1.2 con S77 (PV1-2 = N: sin Encounter), S91 (A31 con PV1-2 ≠ N: sí), S80 (subject
    lógico del mismo mensaje), S78 (sin PV1-19: Encounter sin identifier)."""
    if not pv1:
        return None, "ninguna"
    clase_c = L.texto(L.campo(pv1, 2).split(L.m.c)[0], "PV1-2")
    clase_k = None if clase_c is None else (clase_c if clase_c in M0004_CLASE else
                                             (clase_c.upper() if clase_c.upper() in M0004_CLASE else None))
    if clase_k == "N":
        L.nota("S77: PV1-2 = N (PV1 pseudo-opcional, [E3 2511-2513, 5753-5756]): sin Encounter")
        return None, "ninguna"
    e = {}
    # status (S-ADT-2 rehecha con S75/S76): A11 -> cancelled; PV1-45 valorado -> finished; si no, PV1-2 por la 0004
    fin = _fecha_hora(L, (L.reps(pv1, 45) or [""])[0], "PV1-45")
    if len([r for r in L.reps(pv1, 45) if r]) > 1:
        L.nota("L-ADT-15: PV1-45 trae varias repeticiones; solo viaja la primera")
    if clase_c is None:
        # S95: PV1-2 vacío. Perfil «lab»: AE 101 (la proyección es la del perfil del sitio); class nulo declarado
        L.nota("S95: PV1-2 vacío: AE 101 en el perfil lab; el perfil del sitio lo tolera con class nulo (v3-NullFlavor UNK)")
        e["class"] = {"system": NULLFLAVOR, "code": "UNK"}
        estado = "cancelled" if evento == "A11" else ("finished" if fin else M0003_ESTADO.get(evento, "unknown"))
    else:
        if clase_k is None:
            L.nota("NO-2: PV1-2 %r fuera de la 0004: class literal en v2-0004 y status unknown (%s)"
                   % (clase_c, "S90" if MR.posterior_a_25(version) else "AE 103 en el acuse"))
            e["class"] = {"system": V2 % "0004", "code": clase_c}
        else:
            if clase_k != clase_c:
                L.nota("S4: PV1-2 %r en minúscula se lee como %r" % (clase_c, clase_k))
            s, code = M0004_CLASE[clase_k]
            e["class"] = {"system": s, "code": code}
        estado = ("cancelled" if evento == "A11" else "finished" if fin else
                  M0004_ESTADO.get(clase_k, "unknown"))
    e["status"] = estado
    # identifier <- PV1-19 (VN asignado por el mapa); vacío -> sin identifier (S78)
    vis = L.comp((L.campo(pv1, 19) or ""), 1, "PV1-19.1")
    if vis:
        e["identifier"] = [{"system": SIS_VISIT, "value": vis,
                            "type": {"coding": [{"system": V2 % "0203", "code": "VN"}], "text": "visit number"}}]
    else:
        L.nota("S78: PV1-19 vacío: Encounter sin identifier (sin idempotencia)")
    e["subject"] = {"_recurso": "Patient", "_mismo_mensaje": True}
    # Literales por diseño (sin nota): 0007 [CM table-hl70007-to-v2-0007, identidad]; 0069 S92; 0023 sin vocabulario y 0112
    # unspecified_mapping [CM segment-pv1-to-encounter PV1-14, PV1-36]
    e["type"] = [_cc(_literal(L, pv1, 4, "0007"))]
    e["serviceType"] = _cc(_literal(L, pv1, 10, "0069"))
    e["hospitalization"] = {"admitSource": _cc(_literal(L, pv1, 14, "0023")),
                            "dischargeDisposition": _cc(_literal(L, pv1, 36, "0112"))}
    e["period"] = {"start": _fecha_hora(L, (L.reps(pv1, 44) or [""])[0], "PV1-44"), "end": fin}
    estado3 = "planned" if clase_k == "P" else "active"                     # PV1-3 status por PV1-2.1
    e["location"] = [_ubicacion(L, L.campo(pv1, 3), "PV1-3", estado3), _ubicacion(L, L.campo(pv1, 6), "PV1-6", "completed"),
                     _ubicacion(L, L.campo(pv1, 11), "PV1-11", "active")]
    e["participant"] = [p for _, p in _participantes(L, pv1)]
    return _limpio(e), ("cancelar" if evento == "A11" else "crear_o_actualizar")


def _cc(coding):
    return {"coding": [coding]} if coding else None


def _literal(L, seg, n, tabla):
    c = L.texto(L.campo(seg, n).split(L.m.c)[0], "PV1-%d" % n)
    return {"system": V2 % tabla, "code": c} if c else None


# ---------------------------------------------------------------------------- entrada
def _msg(texto):
    if "\r" not in texto:
        texto = texto.replace("\n", "\r")
    texto = texto.replace("\r\n", "\r")
    ms = MR.mensajes(A.cable(b"\x0b" + texto.rstrip("\r").encode("utf-8") + b"\r\x1c\r"))
    if not ms:
        raise ValueError("no hay MSH")
    return ms[0]


def analizar(texto):
    return _analizar(_msg(texto))


def _analizar(m):
    L = Lector(m)
    msh = m.segs[0]
    t9 = m.campo(msh, 9).split(m.c)
    evento = t9[1] if len(t9) > 1 else ""
    version = m.campo(msh, 12).split(m.c)[0]
    pid = (m.segmentos("PID") or [""])[0]
    pv1 = (m.segmentos("PV1") or [""])[0]
    out = {"evento": evento, "estructura": ESTRUCTURA.get(evento, t9[2] if len(t9) > 2 else ""),
           "Patient": None, "Encounter": None, "accion": {"Patient": "ninguna", "Encounter": "ninguna"}}
    if evento not in ESTRUCTURA:
        L.nota("L-ADT-2: evento %r fuera de los 8: AR 201 en adt_fhir" % evento)
        return out, L.notas
    if pid:
        out["Patient"] = patient(L, pid, msh) or None
        out["accion"]["Patient"] = "crear_o_actualizar" if out["Patient"] else "ninguna"
    else:
        L.nota("sin PID: AE 100 en el acuse")
    out["Encounter"], out["accion"]["Encounter"] = encounter(L, pv1, evento, version)
    for s in sorted({s.split(m.f)[0] for s in m.segs} - {"MSH", "EVN", "PID", "PV1"}):
        L.nota("L-ADT-1: segmento %s fuera del alcance v1: no se mapea" % s)
    return out, L.notas


def fhir(texto):
    out, notas = analizar(texto)
    out["notas"] = notas
    return out


# ---------------------------------------------------------------------------- canónico ADT y verificador (A1b; diseño §2, §5.5, §7.1)
# El canónico es lo que LABADT registra (Lab.HL7.Msg.AdtRequest + hijas) y el verificador lee por SQL: sesiones[].canonico_adt =
# {cabecera, nombres, direcciones, telecoms, participantes}. Se construye desde la MISMA lectura que fhir() y proyectar() lo
# devuelve al almacén; la autoprueba exige proyectar(canónico esperado) == a_circuito(fhir()) en todas las entradas de A1.
CAMPOS_CABECERA = ("MsgControlId", "SendingApp", "SendingFacility", "MsgEvent", "ProcessingId", "VersionId", "Estructura",
                   "Identifier", "IdentifierTipo", "NumIdentificadores", "FamilyName", "GivenName", "Gender", "BirthDate",
                   "DeceasedDateTime", "DeceasedBoolean", "MaritalCode", "MaritalSystem", "NumNombres", "NumDirecciones",
                   "NumTelecoms", "NumParticipantes", "TieneVisita", "VisitaId", "ClaseCode", "ClaseSystem", "Estado",
                   "TipoAdmision", "Servicio", "OrigenIngreso", "DisposicionAlta", "Inicio", "Fin", "Ubicacion",
                   "UbicacionDescripcion", "UbicacionPrevia", "UbicacionPreviaDescripcion", "UbicacionTemporal",
                   "UbicacionTemporalDescripcion", "Truncado")
AUX_CABECERA = ("Pid7Crudo", "Pid8Crudo", "ClaseCruda", "VisitaIdTipo")             # para la causa y la ficha; no se comparan
CAMPOS_NOMBRE = ("Orden", "Family", "Given", "Otros", "Prefix", "Suffix", "Grado", "Uso", "Elegido")
CAMPOS_DIRECCION = ("Orden", "Linea1", "Linea2", "Linea3", "Linea4", "Ciudad", "Provincia", "Codigo", "Pais", "Uso", "Tipo")
CAMPOS_TELECOM = ("Orden", "Campo", "Valor", "Uso", "Sistema")
CAMPOS_PARTICIPANTE = ("Orden", "Campo", "Id", "Family", "Given", "Otros", "Prefix", "Suffix")
HIJAS = (("nombres", "Nombre", CAMPOS_NOMBRE), ("direcciones", "Direccion", CAMPOS_DIRECCION),
         ("telecoms", "Telecom", CAMPOS_TELECOM), ("participantes", "Participante", CAMPOS_PARTICIPANTE))
ENTEROS = {"Orden", "Campo", "NumIdentificadores", "NumNombres", "NumDirecciones", "NumTelecoms", "NumParticipantes",
           "TieneVisita", "Truncado", "Elegido"}
HECHO_CABECERA = {"MsgControlId": "MSH-10", "SendingApp": "MSH-3", "SendingFacility": "MSH-4", "MsgEvent": "MSH-9",
                  "ProcessingId": "MSH-11", "VersionId": "MSH-12", "Estructura": "MSH-9", "Identifier": "PID-3",
                  "IdentifierTipo": "PID-3", "NumIdentificadores": "PID-3", "FamilyName": "PID-5", "GivenName": "PID-5",
                  "Gender": "PID-8", "BirthDate": "PID-7", "DeceasedDateTime": "PID-29", "DeceasedBoolean": "PID-30",
                  "MaritalCode": "PID-16", "MaritalSystem": "PID-16", "NumNombres": "PID-5", "NumDirecciones": "PID-11",
                  "NumTelecoms": "PID-13", "NumParticipantes": "PV1-7", "TieneVisita": "PV1-2", "VisitaId": "PV1-19",
                  "ClaseCode": "PV1-2", "ClaseSystem": "PV1-2", "Estado": "PV1-2", "TipoAdmision": "PV1-4", "Servicio": "PV1-10",
                  "OrigenIngreso": "PV1-14", "DisposicionAlta": "PV1-36", "Inicio": "PV1-44", "Fin": "PV1-45",
                  "Ubicacion": "PV1-3", "UbicacionDescripcion": "PV1-3", "UbicacionPrevia": "PV1-6",
                  "UbicacionPreviaDescripcion": "PV1-6", "UbicacionTemporal": "PV1-11", "UbicacionTemporalDescripcion": "PV1-11",
                  "Truncado": "longitud"}
HECHO_HIJA = {"Nombre": "PID-5", "Direccion": "PID-11", "Telecom": "PID-13", "Participante": "PV1-7"}
# Q-MI-V-9 / S-VE-4: la representación del canónico ADT, campo a campo, tal como la construye esperado_mensaje y la compara el juez.
# Fuente única del contrato público (consultar_tabla «canonico_adt» y contratos/contrato_canonico_adt.md, generado). Reglas comunes:
# vacío es "" (nunca null) en el esperado; None en el esperado = imposible, no se juzga (S10); sin visita (PV1-2 = N, TieneVisita =
# 0) TODOS los campos de visita van "" (DV-MI-4); los códigos van ya mapeados a FHIR (DV-MI-2); el mensaje se lee truncado al LEN
# del punto de entrada (S3). (bloque, campo, origen HL7, tipo, valor, cita)
CONTRATO_CANONICO = (
    ("cabecera", "MsgControlId", "MSH-10", "texto", "MSH-10 entero, truncado al LEN del punto", "S3"),
    ("cabecera", "SendingApp", "MSH-3", "texto", "MSH-3.1", ""),
    ("cabecera", "SendingFacility", "MSH-4", "texto", "MSH-4.1", ""),
    ("cabecera", "MsgEvent", "MSH-9", "texto", "MSH-9.2 (el evento)", ""),
    ("cabecera", "ProcessingId", "MSH-11", "texto", "MSH-11.1 escrito", "DV-MI-7"),
    ("cabecera", "VersionId", "MSH-12", "texto", "MSH-12.1 ESCRITO; vacío si no viene (la versión asumida del perfil no entra)", "DV-MI-6, S103"),
    ("cabecera", "Estructura", "MSH-9", "texto", "la estructura con que se lee el mensaje: MSH-9.3 o, si falta, la de la tabla 0354", "AMB-MT-1"),
    ("cabecera", "Identifier", "PID-3", "texto", "Patient.identifier.value: CX.1 de la repetición con CX.5 = MR (si no hay, la primera con CX.1), desescapado", "S80"),
    ("cabecera", "IdentifierTipo", "PID-3", "texto", "CX.5 de esa repetición (Patient.identifier.type)", ""),
    ("cabecera", "NumIdentificadores", "PID-3", "entero", "repeticiones de PID-3 con CX.1", ""),
    ("cabecera", "FamilyName", "PID-5", "texto", "XPN.1 de la repetición elegida (S74), desescapado", "S74"),
    ("cabecera", "GivenName", "PID-5", "texto", "XPN.2 y XPN.3 de la repetición elegida (S74), unidos por un espacio", "S74, DV-MI-3"),
    ("cabecera", "Gender", "PID-8", "texto", "código AdministrativeGender por la 0001 (ConceptMap oficial); None si es imposible", "S22, S103"),
    ("cabecera", "BirthDate", "PID-7", "texto", "date FHIR con la precisión del TS de PID-7; None si es imposible", "S8"),
    ("cabecera", "DeceasedDateTime", "PID-29", "texto", "dateTime FHIR con la zona del emisor; None si es imposible", "S66"),
    ("cabecera", "DeceasedBoolean", "PID-30", "texto", "\"true\" o \"false\" por la 0136; vacío si no viene; None si es imposible", ""),
    ("cabecera", "MaritalCode", "PID-16", "texto", "Patient.maritalStatus.coding.code por la 0002", ""),
    ("cabecera", "MaritalSystem", "PID-16", "texto", "Patient.maritalStatus.coding.system", ""),
    ("cabecera", "NumNombres", "PID-5", "entero", "filas de «nombres»", ""),
    ("cabecera", "NumDirecciones", "PID-11", "entero", "filas de «direcciones»", ""),
    ("cabecera", "NumTelecoms", "PID-13", "entero", "filas de «telecoms» (PID-13 y PID-14)", ""),
    ("cabecera", "NumParticipantes", "PV1-7", "entero", "filas de «participantes»; 0 sin visita", ""),
    ("cabecera", "TieneVisita", "PV1-2", "entero", "1 si hay Encounter; 0 con PV1-2 = N", "S77"),
    ("cabecera", "VisitaId", "PV1-19", "texto", "Encounter.identifier.value (PV1-19.1); vacío sin visita o sin PV1-19", "S78"),
    ("cabecera", "ClaseCode", "PV1-2", "texto", "Encounter.class.code por la 0004 (v3-ActCode o v2-0004); vacío sin visita, no el mapeo de N; None si es imposible", "DV-MI-4"),
    ("cabecera", "ClaseSystem", "PV1-2", "texto", "Encounter.class.system", ""),
    ("cabecera", "Estado", "PV1-2", "texto", "Encounter.status (encounter-status), por el evento y PV1-45", ""),
    ("cabecera", "TipoAdmision", "PV1-4", "texto", "Encounter.type.coding.code", ""),
    ("cabecera", "Servicio", "PV1-10", "texto", "Encounter.serviceType.coding.code", ""),
    ("cabecera", "OrigenIngreso", "PV1-14", "texto", "Encounter.hospitalization.admitSource.coding.code", ""),
    ("cabecera", "DisposicionAlta", "PV1-36", "texto", "Encounter.hospitalization.dischargeDisposition.coding.code", ""),
    ("cabecera", "Inicio", "PV1-44", "texto", "Encounter.period.start, dateTime FHIR con la zona del emisor; None si es imposible", "S66"),
    ("cabecera", "Fin", "PV1-45", "texto", "Encounter.period.end, dateTime FHIR con la zona del emisor; None si es imposible", "S66"),
    ("cabecera", "Ubicacion", "PV1-3", "texto", "identifier de la Location: PL.1^PL.2^PL.3^PL.4.1", ""),
    ("cabecera", "UbicacionDescripcion", "PV1-3", "texto", "Location.description", ""),
    ("cabecera", "UbicacionPrevia", "PV1-6", "texto", "identifier de la Location previa (completed)", ""),
    ("cabecera", "UbicacionPreviaDescripcion", "PV1-6", "texto", "su description", ""),
    ("cabecera", "UbicacionTemporal", "PV1-11", "texto", "identifier de la Location temporal", ""),
    ("cabecera", "UbicacionTemporalDescripcion", "PV1-11", "texto", "su description", ""),
    ("cabecera", "Truncado", "longitud", "entero", "1 si algún campo se truncó al LEN de v2.5; 0 si no", "S3"),
    ("auxiliar", "Pid7Crudo", "PID-7", "texto", "PID-7 crudo (para la causa y la ficha; no se compara)", ""),
    ("auxiliar", "Pid8Crudo", "PID-8", "texto", "PID-8 crudo (no se compara)", ""),
    ("auxiliar", "ClaseCruda", "PV1-2", "texto", "PV1-2 crudo (no se compara)", ""),
    ("auxiliar", "VisitaIdTipo", "PV1-19", "texto", "CX.5 de PV1-19 crudo (no se compara)", ""),
    ("nombres", "Orden", "PID-5", "entero", "1..n en el orden de las repeticiones con XPN.1, XPN.2 o XPN.3", "D-ADT-5"),
    ("nombres", "Family", "PID-5.1", "texto", "FN.1..n unidos por un espacio, desescapados", ""),
    ("nombres", "Given", "PID-5.2", "texto", "XPN.2 entero", "S96"),
    ("nombres", "Otros", "PID-5.3", "texto", "XPN.3 entero", "S96"),
    ("nombres", "Prefix", "PID-5.5", "texto", "XPN.5", ""),
    ("nombres", "Suffix", "PID-5.4", "texto", "XPN.4", ""),
    ("nombres", "Grado", "PID-5.6", "texto", "XPN.6", ""),
    ("nombres", "Uso", "PID-5.7", "texto", "XPN.7 mapeado por la 0200 a name-use de FHIR; vacío si no está en la tabla", "DV-MI-2"),
    ("nombres", "Elegido", "PID-5", "entero", "1 en la repetición elegida por S74; 0 en las demás", "S74"),
    ("direcciones", "Orden", "PID-11", "entero", "1..n en el orden de Patient.address", "D-ADT-5"),
    ("direcciones", "Linea1", "PID-11", "texto", "address.line[0]", ""),
    ("direcciones", "Linea2", "PID-11", "texto", "address.line[1]", ""),
    ("direcciones", "Linea3", "PID-11", "texto", "address.line[2]", ""),
    ("direcciones", "Linea4", "PID-11", "texto", "address.line[3]", ""),
    ("direcciones", "Ciudad", "PID-11.3", "texto", "address.city", ""),
    ("direcciones", "Provincia", "PID-11.4", "texto", "address.state", ""),
    ("direcciones", "Codigo", "PID-11.5", "texto", "address.postalCode", ""),
    ("direcciones", "Pais", "PID-11.6", "texto", "address.country", ""),
    ("direcciones", "Uso", "PID-11.7", "texto", "address.use de FHIR, ya mapeado", "DV-MI-2"),
    ("direcciones", "Tipo", "PID-11.7", "texto", "address.type de FHIR, ya mapeado", "DV-MI-2"),
    ("telecoms", "Orden", "PID-13", "entero", "1..n: primero PID-13, luego PID-14", "D-ADT-5"),
    ("telecoms", "Campo", "PID-13", "entero", "13 o 14", ""),
    ("telecoms", "Valor", "PID-13", "texto", "ContactPoint.value", ""),
    ("telecoms", "Uso", "PID-13", "texto", "ContactPoint.use de FHIR, ya mapeado", "DV-MI-2"),
    ("telecoms", "Sistema", "PID-13", "texto", "ContactPoint.system de FHIR, ya mapeado", "DV-MI-2"),
    ("participantes", "Orden", "PV1-7", "entero", "1..n en el orden de Encounter.participant; ninguno sin visita", "D-ADT-5"),
    ("participantes", "Campo", "PV1-7", "entero", "el campo de PV1 del que sale (7, 8, 17...)", ""),
    ("participantes", "Id", "PV1-7", "texto", "Practitioner.identifier.value (XCN.1)", ""),
    ("participantes", "Family", "PV1-7", "texto", "Practitioner.name.family (XCN.2)", ""),
    ("participantes", "Given", "PV1-7.3", "texto", "XCN.3 entero", ""),
    ("participantes", "Otros", "PV1-7.4", "texto", "XCN.4 entero", ""),
    ("participantes", "Prefix", "PV1-7", "texto", "Practitioner.name.prefix", ""),
    ("participantes", "Suffix", "PV1-7", "texto", "Practitioner.name.suffix", ""),
)
PE_POR_OMISION = "adt_fhir"


def _pe(pe):
    import puntos_entrada as PE
    return PE.resolver(pe or PE_POR_OMISION)


def _eleccion_s74(L, pid):
    """S74: la repetición de PID-5 con XPN.7 = L traiga lo que traiga; si no, la primera con XPN.1 o XPN.2 (0-based, o None)."""
    reps = [L.comps(r) for r in L.reps(pid, 5)]
    i = next((i for i, c in enumerate(reps) if len(c) > 6 and c[6] == "L"), None)
    return i if i is not None else next((i for i, c in enumerate(reps) if c[0] or (len(c) > 1 and c[1])), None)


def _imposibles(L, m, pid, pv1, version):
    """Lo que el acuse debía rechazar (AE 102/103) y, si se aceptó, es valor_imposible_aceptado. -> ([textos], {campos a no comparar})."""
    out, nulos = [], set()
    msh = m.segs[0]
    posterior25 = MR.posterior_a_25(version)
    v7 = L.campo(pid, 7).split(m.c)[0]
    if v7 and v7 != NULO:
        _, prob = MR.fecha(v7, L.campo(msh, 7).split(m.c)[0] or None, m.c)
        if prob or v7 != v7.strip():
            out.append("%s y se aceptó" % (prob or "PID-7 %r con blancos en los bordes" % v7))
            nulos.add("BirthDate")
    for seg, n, campo in ((pid, 29, "DeceasedDateTime"), (pv1, 44, "Inicio"), (pv1, 45, "Fin")):
        v = (L.campo(seg, n).split(m.r)[0]).split(m.c)[0]
        if v and v != NULO and (v != v.strip() or MO.fecha_hora(v, ZONA, m.c)[1]):
            out.append("%s-%d %r no es un TS de v2.5 y se aceptó" % ("PID" if seg is pid else "PV1", n, v))
            nulos.add(campo)
    if not posterior25:                                                   # S22: en > 2.5 es tolerancia, no imposible
        for seg, n, tabla, campo in ((pid, 8, M0001, "Gender"), (pv1, 2, M0004_CLASE, "ClaseCode"), (pid, 30, M0136, "DeceasedBoolean")):
            v = L.campo(seg, n).split(m.c)[0]
            if v and v != NULO and v not in tabla and v.upper() not in tabla:
                out.append("%s-%d %r no está en la tabla %s y se aceptó" % ("PID" if seg is pid else "PV1", n, v,
                                                                           {8: "0001", 2: "0004", 30: "0136"}[n]))
                nulos.add(campo)
    for seg, nombre, campos in ((pid, "PID", (3, 5, 7, 8, 11, 13, 14, 16, 29, 30)),
                                (pv1, "PV1", (2, 3, 4, 6, 7, 8, 10, 11, 14, 17, 19, 36, 44, 45))):   # [S10]
        for n in campos:
            c = MR.control_en(m.desescapa(L.campo(seg, n))) if seg else None
            if c is not None:
                out.append("%s-%d contiene un carácter de control U+%04X y se aceptó" % (nombre, n, c))
    return out, nulos


def esperado_mensaje(m, pe=None):
    """-> (canónico esperado {cabecera, nombres, direcciones, telecoms, participantes}, imposibles aceptados, avisos de estructura,
    tolerancias y notas etiquetadas «[S4] …»). El mensaje se trunca como en el acuse (P1b, S3/S46, longitudes del PE)."""
    import acuse_referencia as AR
    pe = _pe(pe)
    t, truncs = AR._truncar(m, pe)
    r, notas = _analizar(t)
    L = Lector(t)
    msh = t.segs[0]
    pid = (t.segmentos("PID") or [""])[0]
    pv1 = (t.segmentos("PV1") or [""])[0]
    t9 = t.campo(msh, 9).split(t.c)
    version = t.campo(msh, 12).split(t.c)[0]
    est = []
    if len(t.segmentos("PID")) > 1 or len(t.segmentos("PV1")) > 1:
        est.append("ADT lleva exactamente un PID y un PV1 y hay %d y %d" % (len(t.segmentos("PID")), len(t.segmentos("PV1"))))
    imp, nulos = _imposibles(L, t, pid, pv1, version)
    P, E = r["Patient"] or {}, r["Encounter"] or {}
    ident = (P.get("identifier") or [{}])[0]
    fam, giv = MR.nombre(t, pid)
    cab = {"MsgControlId": t.campo(msh, 10), "SendingApp": t.campo(msh, 3).split(t.c)[0],
           "SendingFacility": t.campo(msh, 4).split(t.c)[0], "MsgEvent": t9[1] if len(t9) > 1 else "",
           "ProcessingId": t.campo(msh, 11).split(t.c)[0], "VersionId": version, "Estructura": r["estructura"],
           "Identifier": ident.get("value", ""),
           "IdentifierTipo": ((ident.get("type") or {}).get("coding") or [{}])[0].get("code", ""),
           "NumIdentificadores": len([x for x in L.reps(pid, 3) if L.comps(x)[0]]),
           "FamilyName": fam, "GivenName": giv, "Gender": P.get("gender", ""), "BirthDate": P.get("birthDate", ""),
           "DeceasedDateTime": P.get("deceasedDateTime", ""),
           "DeceasedBoolean": {True: "true", False: "false"}.get(P.get("deceasedBoolean"), ""),
           "MaritalCode": ((P.get("maritalStatus") or {}).get("coding") or [{}])[0].get("code", ""),
           "MaritalSystem": ((P.get("maritalStatus") or {}).get("coding") or [{}])[0].get("system", ""),
           "Pid7Crudo": L.campo(pid, 7), "Pid8Crudo": L.campo(pid, 8), "ClaseCruda": L.campo(pv1, 2),
           "VisitaIdTipo": (L.comps(L.campo(pv1, 19)) + [""] * 5)[4] if pv1 else "",
           "TieneVisita": 1 if r["Encounter"] else 0, "Truncado": 1 if truncs else 0}
    # hijas del paciente
    eleg = _eleccion_s74(L, pid)
    nombres = []
    for i, rep in enumerate(L.reps(pid, 5)):
        c = L.comps(rep)
        famh = " ".join(s for s in (L.texto(x, "PID-5.1") for x in (c[0].split(t.s) if c else [])) if s)
        g2, g3 = L.comp(rep, 2, "PID-5.2"), L.comp(rep, 3, "PID-5.3")
        if not famh and not g2 and not g3:
            continue
        uso_c = L.comp(rep, 7, "PID-5.7")
        k = None if not uso_c else (uso_c if uso_c in T0200 else (uso_c.upper() if uso_c.upper() in T0200 else None))
        nombres.append({"Orden": len(nombres) + 1, "Family": famh, "Given": g2 or "", "Otros": g3 or "",
                        "Prefix": L.comp(rep, 5, "PID-5.5") or "", "Suffix": L.comp(rep, 4, "PID-5.4") or "",
                        "Grado": L.comp(rep, 6, "PID-5.6") or "", "Uso": M0200.get(k, "") if k else "",
                        "Elegido": 1 if i == eleg else 0})
    direcciones = []
    for d in P.get("address") or []:
        ln = list(d.get("line") or []) + [""] * 4
        direcciones.append({"Orden": len(direcciones) + 1, "Linea1": ln[0], "Linea2": ln[1], "Linea3": ln[2], "Linea4": ln[3],
                            "Ciudad": d.get("city", ""), "Provincia": d.get("state", ""), "Codigo": d.get("postalCode", ""),
                            "Pais": d.get("country", ""), "Uso": d.get("use", ""), "Tipo": d.get("type", "")})
    telecoms = []
    Lt = Lector(t)
    for campo in (13, 14):
        for rep in Lt.reps(pid, campo):
            x = _telecom(Lt, rep, campo)
            if x:
                telecoms.append({"Orden": len(telecoms) + 1, "Campo": campo, "Valor": x.get("value", ""), "Uso": x.get("use") or "",
                                 "Sistema": x.get("system") or ""})
    participantes = []
    if r["Encounter"]:
        for n, p in _participantes(Lector(t), pv1):
            ind = p["individual"]
            nm_ = (ind.get("name") or [{}])[0]
            rep = L.reps(pv1, n)[0]
            participantes.append({"Orden": len(participantes) + 1, "Campo": n,
                                  "Id": ((ind.get("identifier") or [{}])[0]).get("value", ""), "Family": nm_.get("family", ""),
                                  "Given": L.comp(rep, 3, "PV1-%d.3" % n) or "", "Otros": L.comp(rep, 4, "PV1-%d.4" % n) or "",
                                  "Prefix": (nm_.get("prefix") or [""])[0], "Suffix": (nm_.get("suffix") or [""])[0]})
        Lu = Lector(t)
        locs = {}
        for n, clave, estado in ((3, "Ubicacion", "active"), (6, "UbicacionPrevia", "completed"), (11, "UbicacionTemporal", "active")):
            u = _ubicacion(Lu, L.campo(pv1, n), "PV1-%d" % n, estado)
            locs[clave] = u["location"]["identifier"][0]["value"] if u else ""
            locs[clave + "Descripcion"] = (u["location"].get("description") or "") if u else ""
        cab.update(locs)
        cab.update({"VisitaId": ((E.get("identifier") or [{}])[0]).get("value", ""),
                    "ClaseCode": E["class"]["code"], "ClaseSystem": E["class"]["system"], "Estado": E["status"],
                    "TipoAdmision": ((E.get("type") or [{}])[0].get("coding") or [{}])[0].get("code", ""),
                    "Servicio": ((E.get("serviceType") or {}).get("coding") or [{}])[0].get("code", ""),
                    "OrigenIngreso": (((E.get("hospitalization") or {}).get("admitSource") or {}).get("coding") or [{}])[0].get("code", ""),
                    "DisposicionAlta": (((E.get("hospitalization") or {}).get("dischargeDisposition") or {}).get("coding") or [{}])[0].get("code", ""),
                    "Inicio": (E.get("period") or {}).get("start", ""), "Fin": (E.get("period") or {}).get("end", "")})
    for k in CAMPOS_CABECERA:
        cab.setdefault(k, "")
    cab.update({"NumNombres": len(nombres), "NumDirecciones": len(direcciones), "NumTelecoms": len(telecoms),
                "NumParticipantes": len(participantes)})
    for k in nulos:
        cab[k] = None                                                    # imposible: no se compara (MR.esperado, [S10])
    tol = []
    for n_ in notas:
        etq, _, txt = n_.partition(": ")
        hl7 = etq == "NO-2" and any(s in txt for s in ("PID-8", "PV1-2", "PID-30"))
        if etq == "NO-1" or (hl7 and not MR.posterior_a_25(version)):
            continue                                                     # ya está en imposibles
        tol.append("[%s] %s" % ("S22" if hl7 else etq, txt))
    if truncs:
        tol.append("[S3] truncado al LEN de v2.5 (Truncado = 1): " + "; ".join(truncs))
    return {"cabecera": cab, "nombres": nombres, "direcciones": direcciones, "telecoms": telecoms,
            "participantes": participantes}, imp, est, tol


def esperado(texto, pe=None):
    return [esperado_mensaje(m, pe) for m in MR.mensajes(texto)]


def canonico_texto(canon):
    """Un canónico OBSERVADO (leído por SQL: "" llega como None) con la forma del esperado: None -> "" en los textos y 0 en los
    enteros. En proyectar(), None significa «imposible, no juzgar»; en lo observado solo significa vacío (A3, 10-oct)."""
    def fila(d, campos):
        d = d if isinstance(d, dict) else {}
        return {c: (int(d.get(c) or 0) if c in ENTEROS else ("" if d.get(c) is None else d.get(c))) for c in campos}
    out = {"cabecera": fila(canon.get("cabecera"), CAMPOS_CABECERA + AUX_CABECERA)}
    for clave, _, campos in HIJAS:
        out[clave] = [fila(h, campos) for h in (canon.get(clave) or []) if isinstance(h, dict)]
    return out


def proyectar(canon):
    """Canónico -> {"Patient", "Encounter"} como deben quedar en el almacén (forma del circuito, §5.2 con S80: subject lógico por el
    identifier mrn; Location y Practitioner como Reference con identifier y display). Mismas reglas que fhir() (equivalencia en
    la autoprueba). Valores None (imposibles) -> la hoja se marca None («no juzgar»)."""
    c = canon["cabecera"]

    def cc(system, code):
        return {"coding": [{"system": system, "code": code}]} if code else None
    pat = {"resourceType": "Patient",
           "identifier": [{"system": SIS_MRN, "value": c["Identifier"],
                           "type": cc(V2 % "0203", c["IdentifierTipo"])}] if c["Identifier"] else None,
           "name": [{"use": n["Uso"], "family": n["Family"], "given": ([n["Given"]] if n["Given"] else []) + n["Otros"].split(),
                     "prefix": [n["Prefix"]], "suffix": [n["Suffix"], n["Grado"]]} for n in canon["nombres"]],
           "gender": c["Gender"], "birthDate": c["BirthDate"], "deceasedDateTime": c["DeceasedDateTime"],
           "deceasedBoolean": {"true": True, "false": False}.get(c["DeceasedBoolean"]) if c["DeceasedBoolean"] is not None else None,
           "address": [{"line": [d["Linea1"], d["Linea2"], d["Linea3"], d["Linea4"]], "city": d["Ciudad"], "state": d["Provincia"],
                        "postalCode": d["Codigo"], "country": d["Pais"], "use": d["Uso"], "type": d["Tipo"]}
                       for d in canon["direcciones"]],
           "telecom": [{"system": x["Sistema"], "value": x["Valor"], "use": x["Uso"]} for x in canon["telecoms"]],
           "maritalStatus": cc(c["MaritalSystem"], c["MaritalCode"])}
    nulos = {k for k, v in c.items() if v is None}
    pat = _limpio(pat)
    if list(pat) == ["resourceType"]:
        pat = None                                                       # sin PID (AE 100): no hay Patient que escribir
    for k, ruta in (("BirthDate", "birthDate"), ("Gender", "gender"), ("DeceasedDateTime", "deceasedDateTime"),
                    ("DeceasedBoolean", "deceasedBoolean")):
        if k in nulos and pat is not None:
            pat[ruta] = None
    enc = None
    if c["TieneVisita"]:
        tipos = {n: (code, campo_txt, txt) for n, code, campo_txt, txt in PARTICIPANTES}

        def part(p):
            code, campo_txt, txt = tipos[p["Campo"]]
            coding = {"system": PARTTYPE, "code": code, "display": txt if campo_txt == "display" else None}
            disp = " ".join(x for x in [p["Family"], p["Given"]] + p["Otros"].split() if x)
            return {"type": [{"coding": [coding], "text": txt if campo_txt == "text" else None}],
                    "individual": {"identifier": {"system": SIS_PROF, "value": p["Id"]} if p["Id"] else None, "display": disp}}

        def loc(valor, desc, estado):
            return {"location": {"identifier": {"system": SIS_LOC, "value": valor}, "display": desc}, "status": estado} if valor else None
        enc = {"resourceType": "Encounter",
               "identifier": [{"system": SIS_VISIT, "value": c["VisitaId"],
                               "type": {"coding": [{"system": V2 % "0203", "code": "VN"}], "text": "visit number"}}] if c["VisitaId"] else None,
               "status": c["Estado"], "class": {"system": c["ClaseSystem"], "code": c["ClaseCode"]} if c["ClaseCode"] else None,
               "type": [cc(V2 % "0007", c["TipoAdmision"])], "serviceType": cc(V2 % "0069", c["Servicio"]),
               "subject": {"identifier": {"system": SIS_MRN, "value": c["Identifier"]}} if c["Identifier"] else None,
               "participant": [part(p) for p in canon["participantes"]],
               "period": {"start": c["Inicio"], "end": c["Fin"]},
               "location": [loc(c["Ubicacion"], c["UbicacionDescripcion"], "planned" if c["ClaseCode"] == "PRENC" else "active"),
                            loc(c["UbicacionPrevia"], c["UbicacionPreviaDescripcion"], "completed"),
                            loc(c["UbicacionTemporal"], c["UbicacionTemporalDescripcion"], "active")],
               "hospitalization": {"admitSource": cc(V2 % "0023", c["OrigenIngreso"]),
                                   "dischargeDisposition": cc(V2 % "0112", c["DisposicionAlta"])}}
        enc = _limpio(enc)
        for k, ruta in (("Inicio", "start"), ("Fin", "end")):
            if k in nulos:
                enc.setdefault("period", {})[ruta] = None
        if "ClaseCode" in nulos:
            enc["class"] = None
    return {"Patient": pat, "Encounter": enc}


def a_circuito(r):
    """Salida de fhir() (forma de A1) -> la forma en que el circuito la escribe (S80, S82, S83; D-ADT-10: display del Practitioner
    = family, given y otros nombres separados por espacio)."""
    import copy
    p = copy.deepcopy(r.get("Patient"))
    if p is not None:
        p = dict({"resourceType": "Patient"}, **p)
    e = copy.deepcopy(r.get("Encounter"))
    if e is not None:
        e = dict({"resourceType": "Encounter"}, **e)
        mrn = ((p or {}).get("identifier") or [{}])[0].get("value")
        e["subject"] = {"identifier": {"system": SIS_MRN, "value": mrn}} if mrn else None
        for l_ in e.get("location") or []:
            loc = l_["location"]
            l_["location"] = {"identifier": loc["identifier"][0], "display": loc.get("description")}
        for pa in e.get("participant") or []:
            ind = pa["individual"]
            nm_ = (ind.get("name") or [{}])[0]
            pa["individual"] = {"identifier": (ind.get("identifier") or [None])[0],
                                "display": " ".join(x for x in [nm_.get("family")] + (nm_.get("given") or []) if x)}
        e = _limpio(e)
    return {"Patient": p, "Encounter": e}


def _igual(e, o, campo):
    if campo in ENTEROS:
        oi = int(o) if str(o).strip().lstrip("-").isdigit() else (0 if o in ("", None) else o)
        return e == oi
    return str(e) == ("" if o is None else str(o))


def comparar(observado, esperado_):
    """-> (discrepancias, recuentos). «Campo: esperado X, observado Y» (cabecera), «Nombre i Campo: …», «Direccion i …»,
    «Telecom i …», «Participante i …»; las hijas por posición (D-ADT-5: el orden es dato)."""
    out = []
    can = observado if isinstance(observado, dict) else {}
    cab_o = can.get("cabecera") if isinstance(can.get("cabecera"), dict) else {}
    for c in CAMPOS_CABECERA:
        e, o = esperado_["cabecera"].get(c), cab_o.get(c)
        if e is None or (c not in cab_o and e in ("", 0)):
            continue
        if not _igual(e, o, c):
            out.append("%s: esperado %r, observado %r" % (c, e, o))
    rec = {}
    for clave, nombre, campos in HIJAS:
        lo = can.get(clave) if isinstance(can.get(clave), list) else []
        le = esperado_[clave]
        rec[clave] = (len(le), len(lo))
        for i, x in enumerate(le):
            o = lo[i] if i < len(lo) and isinstance(lo[i], dict) else None
            if o is None:
                continue                                                 # el recuento (cabecera Num*) ya lo dice
            for c in campos:
                e = x.get(c)
                if e is None or (c not in o and e in ("", 0)):
                    continue
                if not _igual(e, o.get(c), c):
                    out.append("%s %d %s: esperado %r, observado %r" % (nombre, i + 1, c, e, o.get(c)))
    return out, rec


def revisar(texto_mensaje, canonicos, ack, pe=None):
    """Misma forma que mapeador_oru.revisar: -> (discrepancias, tolerancias y notas etiquetadas), o None fuera de alcance
    (MSA-1 ≠ AA o sin canónico)."""
    ms = MR.mensajes(texto_mensaje)
    am = MR.mensajes(ack or "")
    msa = am[0].segmentos("MSA") if am else []
    if not ms or not canonicos or not msa or am[0].campo(msa[0], 1) != "AA":
        return None
    out, tol = [], []
    for k, m in enumerate(ms):
        pre = "mensaje %d: " % (k + 1) if len(ms) > 1 else ""
        a_k = next((a for a in am if a.segmentos("MSA") and a.campo(a.segmentos("MSA")[0], 2) == m.campo(m.segs[0], 10)),
                   am[k] if k < len(am) else None)
        if len(ms) > 1 and (a_k is None or not a_k.segmentos("MSA") or a_k.campo(a_k.segmentos("MSA")[0], 1) != "AA"):
            tol.append("[L24] " + pre + "su acuse no es AA: su canónico no se compara (fuera de alcance)")
            continue
        esp, imp, est, tl = esperado_mensaje(m, pe)
        out += [pre + z for z in imp] + [pre + z for z in est]
        tol += [pre + z if not z.startswith("[") else z.replace("] ", "] " + pre, 1) for z in tl]
        can = canonicos[k] if k < len(canonicos) else None
        if not isinstance(can, dict):
            out.append(pre + "no hay canónico para este mensaje")
            continue
        out += [pre + z for z in comparar(can, esp)[0]]
    ecos = [a.campo(z, 2) for a in am for z in a.segmentos("MSA")]
    for k, m in enumerate(ms):
        ctl = m.campo(m.segs[0], 10)
        if ctl not in ecos:
            a = am[k] if k < len(am) else None
            msa2 = a.campo(a.segmentos("MSA")[0], 2) if a is not None and a.segmentos("MSA") else None
            out.append(("mensaje %d: " % (k + 1) if len(ms) > 1 else "") + "MSA-2 %r no devuelve el MSH-10 %r" % (msa2, ctl))
    return out, tol


def _sin_nulos(x):
    if isinstance(x, dict):
        return {k: _sin_nulos(v) for k, v in x.items() if v is not None}
    if isinstance(x, list):
        return [_sin_nulos(v) for v in x]
    return x


def equivalencia(texto, pe=None):
    """proyectar(canónico esperado) frente a a_circuito(fhir()): las dos vías desde la misma lectura deben dar lo mismo (las
    hojas None de proyectar son «no juzgar» por imposible y fhir() las omite). -> [diferencias] (vacía si equivalen)."""
    m = _msg(texto)
    p = proyectar(esperado_mensaje(m, pe)[0])
    f = a_circuito(_analizar(m)[0])
    out = []

    def quitar_comodines(pp, ff):                                       # hoja None en la proyección = «no juzgar»: fuera de ff
        if isinstance(pp, dict) and isinstance(ff, dict):
            for k_, v_ in pp.items():
                if v_ is None:
                    ff.pop(k_, None)
                else:
                    quitar_comodines(v_, ff.get(k_))
    for k in ("Patient", "Encounter"):
        quitar_comodines(p[k], f[k])
        a, b = _limpio(_sin_nulos(p[k])) if p[k] else None, _limpio(f[k]) if f[k] else f[k]
        if a != b:
            out.append("%s: proyectar %s / fhir %s" % (k, json.dumps(a, ensure_ascii=False)[:300], json.dumps(b, ensure_ascii=False)[:300]))
    return out


def hecho_de(texto):
    """Campo del hecho (SEG-n) de una línea del mapeador ADT, o None si no es de este mapeador."""
    cabeza = texto.split(":")[0]
    mh = re.match(r"^(Nombre|Direccion|Telecom|Participante) \d+ (\w+)$", cabeza)
    if mh:
        return HECHO_HIJA[mh.group(1)]
    return HECHO_CABECERA.get(cabeza)


# ---------------------------------------------------------------------------- autoprueba
def autoprueba():
    mal = []
    n = [0]

    def mira(nombre, obtenido, esperado_):
        n[0] += 1
        if obtenido != esperado_:
            mal.append("MAL %s: obtenido %r, esperado %r" % (nombre, obtenido, esperado_))

    def seg(nombre, campos):
        """Segmento con los campos por índice (1-based): seg("PV1", {2: "I", 19: "V1"})."""
        hasta = max(campos) if campos else 0
        return "|".join([nombre] + [campos.get(i, "") for i in range(1, hasta + 1)])

    PV1_BASE = {1: "1", 2: "I", 3: "URG^101^1", 10: "MED", 19: "V77"}

    def pv1(**k):
        d = dict(PV1_BASE)
        d.update({int(n[1:]): v for n, v in k.items()})
        return seg("PV1", {i: v for i, v in d.items() if v is not None})

    def msg(ev="A01", pid3="X1^^^H^MR", pid5="Pérez^Ana^Luz^^^^L", pid7="19800101", pid8="F", pv1_=None, pid=None, ver="2.5"):
        e = ESTRUCTURA.get(ev, "ADT_A01")
        p = {1: "1", 3: pid3, 5: pid5, 7: pid7, 8: pid8}
        p.update(pid or {})
        return ("MSH|^~\\&|HIS|H|LAB|L|20260101120000||ADT^%s^%s|M1|P|%s\rEVN|%s|20260101120000\r%s\r%s"
                % (ev, e, ver, ev, seg("PID", p), pv1() if pv1_ is None else pv1_))

    def ruta(r, *k):
        for x in k:
            if r is None:
                return None
            r = r[x] if (isinstance(r, list) and isinstance(x, int) and x < len(r)) or (isinstance(r, dict) and x in r) else None
        return r

    # Patient: identifier por MR en 2.ª repetición [C]; S89 una sola entrada
    r = fhir(msg(pid3="P9^^^H^PI~X1^^^H^MR"))
    mira("PID-3 MR en 2.ª", ruta(r, "Patient", "identifier"), [{"system": SIS_MRN, "value": "X1",
                                                             "type": {"coding": [{"system": V2 % "0203", "code": "MR"}]}}])
    mira("PID-3 sin MR: la primera", ruta(fhir(msg(pid3="P9^^^H^PI~X1")), "Patient", "identifier", 0, "value"), "P9")
    # name: todas (S84), given por palabras [E3 4975], use 0200, FN por espacio [D]
    r = fhir(msg(pid5="Pérez&Gil^Ana María^Luz^Jr^Dr^^L~Alias^Pepe^^^^^A"))
    mira("name[0]", ruta(r, "Patient", "name", 0), {"use": "official", "family": "Pérez Gil", "given": ["Ana María", "Luz"],
                                                    "prefix": ["Dr"], "suffix": ["Jr"]})
    mira("S96 XPN.3 partido", ruta(fhir(msg(pid5="Ruiz^Eva^María José")), "Patient", "name", 0, "given"), ["Eva", "María", "José"])
    mira("name[1] A sin use", ruta(r, "Patient", "name", 1), {"family": "Alias", "given": ["Pepe"]})
    mira("escape \\S\\", ruta(fhir(msg(pid5="O\\S\\Neil^Ann")), "Patient", "name", 0, "family"), "O^Neil")
    # birthDate: precisión conservada; con hora, solo fecha; inválido -> omitido; futuro -> omitido
    mira("PID-7 AAAAMM", ruta(fhir(msg(pid7="198002")), "Patient", "birthDate"), "1980-02")
    mira("PID-7 con hora", ruta(fhir(msg(pid7="198002291230")), "Patient", "birthDate"), "1980-02-29")
    mira("PID-7 inválido", ruta(fhir(msg(pid7="19801340")), "Patient", "birthDate"), None)
    r = fhir(msg(pid7="20300101"))
    mira("PID-7 futuro: proyección + nota S18", (ruta(r, "Patient", "birthDate"), any(n.startswith("S18") for n in r["notas"])),
         ("2030-01-01", True))
    mira("PID-7 con blanco", ruta(fhir(msg(pid7=" 19800101")), "Patient", "birthDate"), None)
    # gender: 0001, vacío omitido (S86), minúscula S4, fuera omitido
    mira("PID-8 A", ruta(fhir(msg(pid8="A")), "Patient", "gender"), "other")
    mira("PID-8 vacío", ruta(fhir(msg(pid8="")), "Patient", "gender"), None)
    mira("PID-8 f", ruta(fhir(msg(pid8="f")), "Patient", "gender"), "female")
    mira("PID-8 X", ruta(fhir(msg(pid8="X")), "Patient", "gender"), None)
    # deceased: PID-29 manda; PID-30 solo si PID-29 vacío
    mira("PID-29", ruta(fhir(msg(pid={29: "202601011000", 30: "Y"})), "Patient", "deceasedDateTime"), "2026-01-01T10:00:00+01:00")
    mira("PID-29 con PID-30", ruta(fhir(msg(pid={29: "202601011000", 30: "Y"})), "Patient", "deceasedBoolean"), None)
    mira("PID-30 solo", ruta(fhir(msg(pid={30: "N"})), "Patient", "deceasedBoolean"), False)
    # address, telecom, marital
    r = fhir(msg(pid={11: "C/ Mayor 1&2ºB^Esc A^Madrid^M^28001^ESP^H~Apdo 5^^Sevilla^^^^M",
                      13: "600111222^PRN^PH~^^Internet^a@b.es", 16: "M"}))
    mira("address[0]", ruta(r, "Patient", "address", 0), {"line": ["C/ Mayor 1", "2ºB", "Esc A"], "city": "Madrid", "state": "M",
                                                         "postalCode": "28001", "country": "ESP", "use": "home"})
    mira("address[1] M postal", ruta(r, "Patient", "address", 1, "type"), "postal")
    mira("telecom[0]", ruta(r, "Patient", "telecom", 0), {"system": "phone", "value": "600111222", "use": "home"})
    mira("telecom[1] email", ruta(r, "Patient", "telecom", 1), {"system": "email", "value": "a@b.es", "use": "home"})
    mira("PID-14 use work", ruta(fhir(msg(pid={14: "911"})), "Patient", "telecom", 0, "use"), "work")
    mira("PID-16 M", ruta(r, "Patient", "maritalStatus", "coding", 0), {"system": MARITAL, "code": "M"})
    mira("XTN.12 antes que XTN.1", ruta(fhir(msg(pid={13: "111^PRN^PH^^^^^^^^^222"})), "Patient", "telecom", 0, "value"), "222")
    # Encounter: clase, estado, identificador, acción
    r = fhir(msg())
    mira("class I", ruta(r, "Encounter", "class"), {"system": ACTCODE, "code": "IMP"})
    mira("status I", ruta(r, "Encounter", "status"), "in-progress")
    mira("PV1-19", ruta(r, "Encounter", "identifier", 0, "value"), "V77")
    mira("accion A01", r["accion"], {"Patient": "crear_o_actualizar", "Encounter": "crear_o_actualizar"})
    mira("subject", ruta(r, "Encounter", "subject"), {"_recurso": "Patient", "_mismo_mensaje": True})
    mira("location PV1-3", ruta(r, "Encounter", "location", 0), {"location": {"_recurso": "Location", "identifier": [
        {"system": SIS_LOC, "value": "URG^101^1"}]}, "status": "active"})
    mira("serviceType S92", ruta(r, "Encounter", "serviceType"), {"coding": [{"system": V2 % "0069", "code": "MED"}]})
    alta = {"p44": "202601011000", "p45": "202601051200"}
    mira("A03 con PV1-45: finished", ruta(fhir(msg(ev="A03", pv1_=pv1(**alta))), "Encounter", "status"), "finished")
    mira("A03 sin PV1-45: in-progress (S75)", ruta(fhir(msg(ev="A03")), "Encounter", "status"), "in-progress")
    mira("A13 con PV1-45: finished (S76)", ruta(fhir(msg(ev="A13", pv1_=pv1(**alta))), "Encounter", "status"), "finished")
    mira("period", ruta(fhir(msg(ev="A03", pv1_=pv1(**alta))), "Encounter", "period"),
         {"start": "2026-01-01T10:00:00+01:00", "end": "2026-01-05T12:00:00+01:00"})
    r = fhir(msg(ev="A11"))
    mira("A11 cancelled", (ruta(r, "Encounter", "status"), r["accion"]["Encounter"]), ("cancelled", "cancelar"))
    r = fhir(msg(ev="A31", pv1_=pv1(p2="N", p3=None, p10=None, p19=None)))
    mira("A31 N: sin Encounter (S77)", (r["Encounter"], r["accion"]["Encounter"]), (None, "ninguna"))
    mira("A31 I: Encounter (S91)", ruta(fhir(msg(ev="A31")), "accion", "Encounter"), "crear_o_actualizar")
    r = fhir(msg(pv1_=pv1(p2=None)))
    mira("PV1-2 vacío S95", (ruta(r, "Encounter", "class"), ruta(r, "Encounter", "status")),
         ({"system": NULLFLAVOR, "code": "UNK"}, "in-progress"))
    mira("PV1-2 vacío A08 S95", ruta(fhir(msg(ev="A08", pv1_=pv1(p2=None))), "Encounter", "status"), "unknown")
    mira("PV1-2 vacío A08 con PV1-45", ruta(fhir(msg(ev="A08", pv1_=pv1(p2=None, **alta))), "Encounter", "status"), "finished")
    mira("PV1-19 vacío S78", ruta(fhir(msg(pv1_=pv1(p19=None))), "Encounter", "identifier"), None)
    rp = fhir(msg(pv1_=pv1(p2="P")))
    mira("PV1-2 P planned", (ruta(rp, "Encounter", "status"), ruta(rp, "Encounter", "location", 0, "status")), ("planned", "planned"))
    mira("PV1-2 X fuera", ruta(fhir(msg(pv1_=pv1(p2="X"))), "Encounter", "class"), {"system": V2 % "0004", "code": "X"})
    mira("PV1-2 i minúscula", ruta(fhir(msg(pv1_=pv1(p2="i"))), "Encounter", "class", "code"), "IMP")
    mira("PV1-6 completed", ruta(fhir(msg(ev="A02", pv1_=pv1(p6="URG^100^2"))), "Encounter", "location", 1),
         {"location": {"_recurso": "Location", "identifier": [{"system": SIS_LOC, "value": "URG^100^2"}]}, "status": "completed"})
    mira("PV1-4 0007", ruta(fhir(msg(pv1_=pv1(p4="R"))), "Encounter", "type"), [{"coding": [{"system": V2 % "0007", "code": "R"}]}])
    r = fhir(msg(pv1_=pv1(p7="1234^Gómez^Luis^^^Dr~999^Otro", p8="55^Ruiz", p17="77^Sanz")))
    mira("participant ATND", ruta(r, "Encounter", "participant", 0), {
        "type": [{"coding": [{"system": PARTTYPE, "code": "ATND", "display": "attender"}]}],
        "individual": {"_recurso": "Practitioner", "identifier": [{"system": SIS_PROF, "value": "1234"}],
                       "name": [{"family": "Gómez", "given": ["Luis"], "prefix": ["Dr"]}]}})
    mira("participant REF text", ruta(r, "Encounter", "participant", 1, "type", 0, "text"), "referrer")
    mira("participant ADM", ruta(r, "Encounter", "participant", 2, "type", 0, "coding", 0, "code"), "ADM")
    mira("participant sin XCN.1 (DV-ADT-4)", ruta(fhir(msg(pv1_=pv1(p7="^DOCTOR^ANA"))), "Encounter", "participant", 0, "individual"),
         {"_recurso": "Practitioner", "name": [{"family": "DOCTOR", "given": ["ANA"]}]})
    mira("participant vacío", ruta(fhir(msg(pv1_=pv1(p7="^^^"))), "Encounter", "participant"), None)
    mira("nulo \"\"", ruta(fhir(msg(pid8='""')), "Patient", "gender"), None)
    mira("sin vacíos", "{}" in json.dumps(fhir(msg(pv1_=pv1(p3="^^^", p10=None))), ensure_ascii=False), False)
    mira("estructura A11", fhir(msg(ev="A11"))["estructura"], "ADT_A09")
    mira("separadores propios", ruta(fhir(msg().replace("^", "#").replace("MSH|#~\\&", "MSH|#~\\&")), "Patient", "name", 0, "family"),
         "Pérez")
    # --- canónico, comparación, revisar y equivalencia (A1b)
    rico = msg(pid5="Gil&Ruiz^Ana María^Luz^^Dra^^L~Anita^^^^^^N", pid3="P9^^^H^PI~X1^^^H^MR",
               pid={11: "C/ Real 5&Piso 3^Esc 2^Toledo^TO^45001^ESP^H", 13: "^NET^Internet^a@b.es~925^PRN^PH", 14: "911^WPN^FX",
                    16: "M", 29: "202603150930"},
               pv1_=pv1(p4="R", p6="URG^1^A", p7="D1^Vega^Luz", p8="^DOCTOR^ANA", p11="QX^1", p14="7", p36="01",
                        p44="202603100800", p45="202603151000"))
    m_ = _msg(rico)
    esp, imp, est, tl = esperado_mensaje(m_)
    cab = esp["cabecera"]
    mira("canónico cabecera", (cab["Identifier"], cab["IdentifierTipo"], cab["NumIdentificadores"], cab["FamilyName"], cab["GivenName"],
                               cab["Estado"], cab["ClaseCode"], cab["VisitaId"], cab["UbicacionPrevia"], cab["TieneVisita"]),
         ("X1", "MR", 2, "Gil Ruiz", "Ana María Luz", "finished", "IMP", "V77", "URG^1^A", 1))
    mira("canónico hijas", (len(esp["nombres"]), esp["nombres"][0]["Elegido"], esp["nombres"][1]["Uso"], len(esp["telecoms"]),
                            esp["telecoms"][2]["Campo"], [p["Campo"] for p in esp["participantes"]]),
         (2, 1, "nickname", 3, 14, [7, 8]))
    mira("canónico sin imposibles", (imp, est), ([], []))
    mira("equivalencia rico", equivalencia(rico), [])
    for t_ in (msg(), msg(ev="A11"), msg(ev="A31", pv1_=pv1(p2="N")), msg(pv1_=pv1(p2=None)), msg(pid7="20300101"),
               msg(pid8="X"), msg(pv1_=pv1(p2="Z"), ver="2.5.1"), msg(pid5="O\\S\\Neil^Ann")):
        mira("equivalencia %r" % t_[-40:], equivalencia(t_), [])
    imp7 = esperado_mensaje(_msg(msg(pid7="19801340")))
    mira("imposible PID-7 y BirthDate no comparado", (len(imp7[1]), imp7[0]["cabecera"]["BirthDate"]), (1, None))
    mira("imposible PID-8 X (2.5)", [z[:12] for z in esperado_mensaje(_msg(msg(pid8="X")))[1]], ["PID-8 'X' no"])
    mira("S22 PID-8 Z (2.5.1)", (esperado_mensaje(_msg(msg(pid8="Z", ver="2.5.1")))[1],
                                any(z.startswith("[S22]") for z in esperado_mensaje(_msg(msg(pid8="Z", ver="2.5.1")))[3])), ([], True))
    obs = json.loads(json.dumps(esp))
    mira("comparar idéntico", comparar(obs, esp)[0], [])
    obs["cabecera"]["Estado"] = "in-progress"
    obs["nombres"][1]["Family"] = "Otra"
    mira("comparar delata", comparar(obs, esp)[0], ["Estado: esperado 'finished', observado 'in-progress'",
                                                    "Nombre 2 Family: esperado 'Anita', observado 'Otra'"])
    mira("hecho_de", (hecho_de("Nombre 2 Family: esperado"), hecho_de("Estado: esperado"), hecho_de("OBX 1 (x) Valor: e")),
         ("PID-5", "PV1-2", None))
    ack = "MSH|^~\\&|LAB|L|HIS|H|20260101||ACK^A01^ACK|A1|P|2.5\rMSA|%s|M1"
    mira("revisar con AE: fuera de alcance", revisar(rico, [esp], ack % "AE"), None)
    mira("revisar con AA idéntico", revisar(rico, [json.loads(json.dumps(esp))], ack % "AA")[0], [])
    mira("revisar sin canónico", revisar(rico, [None], ack % "AA")[0][-1:], ["no hay canónico para este mensaje"])
    # controles negativos: expectativas deliberadamente erróneas que mira() TIENE que detectar
    antes = len(mal)
    for nombre, obt, esp in (("CN1", ruta(fhir(msg()), "Encounter", "status"), "finished"),
                             ("CN2", ruta(fhir(msg(pid8="M")), "Patient", "gender"), "female"),
                             ("CN3", ruta(fhir(msg(ev="A11")), "accion", "Encounter"), "crear_o_actualizar"),
                             ("CN4", ruta(fhir(msg(pid7="1980")), "Patient", "birthDate"), "1980-01-01"),
                             ("CN5", ruta(fhir(msg(ev="A31", pv1_=pv1(p2="N"))), "Encounter"), {})):
        mira(nombre, obt, esp)
    detectados = len(mal) - antes
    del mal[antes:]
    if detectados != 5:
        mal.append("MAL controles negativos: detectados %d de 5" % detectados)
    # S-VE-4: el contrato cubre EXACTAMENTE los campos que el juez lee, y cada fila trae origen, tipo y valor
    cubre = {(b, c) for b, c, *_ in CONTRATO_CANONICO}
    lee = {("cabecera", c) for c in CAMPOS_CABECERA} | {("auxiliar", c) for c in AUX_CABECERA} | \
          {(clave, c) for clave, _n, campos in HIJAS for c in campos}
    mira("CONTRATO_CANONICO cubre exactamente los campos del canónico, sin filas repetidas ni vacías",
         (sorted(lee - cubre), sorted(cubre - lee), len(CONTRATO_CANONICO) == len(cubre),
          [c for b, c, o, t_, v, _ci in CONTRATO_CANONICO if not (o and v and t_ == ("entero" if c in ENTEROS else "texto"))]),
         ([], [], True, []))
    for x in mal:
        print(x)
    print("AUTOPRUEBA %s %d" % ("OK" if not mal else "FALLA %d/" % len(mal), n[0]))
    return not mal


if __name__ == "__main__":
    if sys.argv[1:] == ["--autoprueba"]:
        sys.exit(0 if autoprueba() else 1)
    print(json.dumps(fhir(open(sys.argv[1], encoding="utf-8").read()), ensure_ascii=False, indent=1))
