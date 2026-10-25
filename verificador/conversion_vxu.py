#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 20 (vx/diseno-vx-fable.md, de Fable; decisiones de Jev en vx/decisiones-qvx.md): el juez ante un VXU^V04 convertido por
un tercero. Punto `vxu_conv` (S-VX-1, familia «vxu», `solo_transformacion`), hermano de `adt_conv` y `oru_conv`, con su misma
evidencia, clases y veredicto (S-VX-2, S-VX-4). conversion.py llama aquí desde cinco ganchos que con las familias adt y oru no
cambian nada (P-VX-22); lo de VXU vive en este módulo: los grupos ORDER, el emparejamiento de Immunization, Observation,
RelatedPerson y Encounter (§2.2) y el perfil «guía» de Immunization (§3). Al importarse registra sus citas (claves nuevas) y su
INFO en conversion.py (DV-VX-2).
  python3 conversion_vxu.py --autoprueba   -> las tablas de VXU contra el paquete de la guía (si está)"""
import os
import re
import sys

import conversion as CV
import mapeador_referencia as MR

_t, _f, _d, _reps, _comp, _sub, _seg = CV._t, CV._f, CV._d, CV._reps, CV._comp, CV._sub, CV._seg
_codigos, _valores, _hecho, FUERA = CV._codigos, CV._valores, CV._hecho, CV.FUERA

TIPOS = CV.TIPOS_PROY + ("Immunization", "RelatedPerson")
FALTAN = ("PID", "RXA")                                             # §2.3: sin ellos, un error es rechazo aceptable

# Q-VX-D (Jev, vx/decision-jev-qvx.md). ALTERNATIVA_VX: la segunda opción de las siete con confianza ≤ 0,52 (regla de §8.1);
# con_alternativas_vx() la aplica sin tocar el juez. La Q-VX-D-3 es la rareza declarada en vx/decisiones-qvx.md.
DECISIONES_VX = {"Q-VX-D-1": "fijar", "Q-VX-D-2": "las_dos", "Q-VX-D-3": "rxa22", "Q-VX-D-4": "recurso_ausente", "Q-VX-D-5": "nk1",
                 "Q-VX-D-6": "si_dos", "Q-VX-D-7": "inventado", "Q-VX-D-8": "convencion", "Q-VX-D-9": "convencion",
                 "Q-VX-D-10": "todas"}
ALTERNATIVA_VX = {"Q-VX-D-2": "solo_0550", "Q-VX-D-3": "cualquiera", "Q-VX-D-4": "convencion", "Q-VX-D-5": "ninguno",
                  "Q-VX-D-6": "siempre", "Q-VX-D-8": "primera", "Q-VX-D-9": "perdido"}

URI_CVX, URI_MVX = "http://hl7.org/fhir/sid/cvx", "http://terminology.hl7.org/CodeSystem/MVX"      # Q-VX-D-1, L-VX-4
URI_VX = dict(CV.URI_SISTEMA, CVX=URI_CVX, MVX=URI_MVX)
URI_V2_TABLA = {"CVX": "http://terminology.hl7.org/CodeSystem/v2-0292", "MVX": "http://terminology.hl7.org/CodeSystem/v2-0227"}  # DV-VX-7
V2 = "http://terminology.hl7.org/CodeSystem/v2-%s"
V3_RUTA = "http://terminology.hl7.org/CodeSystem/v3-RouteOfAdministration"
V3_ROL = "http://terminology.hl7.org/CodeSystem/v3-RoleCode"
ESTADO_FHIR = {"completed", "entered-in-error", "not-done"}                       # [F Immunization.status required]
ACCION_0323 = {"A", "D", "U"}                                                       # [E4 CH04.txt:11445-11449]
SIN_FILA_REP = ("note", "protocolApplied", "education", "programEligibility", "reaction", "subpotentReason", "reasonReference")
ABSORBEN = ("programEligibility", "fundingSource", "education", "reportOrigin", "reasonCode", "note")     # AMB-VX-4


def _identidad(sistema, codigos):
    return {c: (sistema, c) for c in codigos.split(" ")}


# Las tablas de §3.4, leídas de los ConceptMap del paquete v2-to-FHIR 1.0.0 (cv/extraer_mapas.mapa) y comprobadas por
# autoprueba() contra el paquete. Las identidades se escriben como lista; tres códigos de la 0550 traen «\xc2» en el paquete.
MAPAS_VXU = {
    "table-hl70322-to-event-status": {"CP": ("http://hl7.org/fhir/event-status", "completed"), "RE": ("http://hl7.org/fhir/event-status", "not-done"),
                                      "NA": ("http://hl7.org/fhir/event-status", "not-done"), "PA": ("http://hl7.org/fhir/event-status", "completed")},
    "table-hl70162-to-v2-0162": dict(_identidad(V2 % "0162", "AP B DT EP ET GTT GU IMR IA IB IC ICV IH IHA IN IO IP IS IT IU MTH MM NS NG NP NT "
                                                             "OP OT OTH PF PR RM SD SL TP TRA TL UR VG VM WND"),
                                     IM=(V3_RUTA, "IM"), PO=(V3_RUTA, "PO"), ID=(V3_RUTA, "IDINJ"), IV=(V3_RUTA, "IVINJ"), SC=(V3_RUTA, "SQ"),
                                     TD=(V3_RUTA, "TRNSDERM")),
    "table-hl70163-to-v2-0163": _identidad(V2 % "0163", "BE OU BN BU CT LA LAC LACF LD LE LEJ OS LF LG LH LIJ LLAQ LLFA LMFA LN LPC LSC LT "
                                                        "LUA LUAQ LUFA LVG LVL NB PA PERIN RA RAC RACF RD RE REJ OD RF RG RH RIJ RLAQ RLFA "
                                                        "RMFA RN RPC RSC RT RUA RUAQ RUFA RVL RVG"),
    "table-hl70550-to-v2-0550": _identidad(V2 % "0550", (
        "JUGE ADB ACET ACHIL ADE ADR AMN AMS ANAL ANKL ANTEC ANTECF ANTR ANUS AORTA AR AV APDX AREO ARM ARTE ASCIT ASCT ATR AURI AXI BACK "
        "BARTD BARTG BRTGF BPH BID BIFL BLAD BLOOD BLDA BLDC BLDV CBLD BLD BDY BON BMAR BOWEL BOWLA BOWSM BRA BRAIN BCYS BRST BRSTFL BRO "
        "BROCH BRONC BRV BUCCA BURSA BURSF BUTT CALF CANAL CANLI CNL CANTH CDM CARO CARP CAVIT CHE CECUM CSF CVX CERVUT CHEEK CHES CHEST\xc2 "
        "CHIN CIRCU CLAVI CLITO CLIT COCCG COCCY COLON COLOS COS CDUCT CONJ CORAL COR CORD CORN CRANE CRANF CRANO CRANP CRANS CRANT CUBIT "
        "CUFF CULD CULDO DELT DENTA DEN DIAF DPH DIGIT DISC DORS DUFL DUODE DUR EAR EARBI EARBM EARBS EARLO ELBOW ELBOWJ ENDC EC EOLPH ENDM "
        "ET EUR EOS EPICA EPICM EPD EPIDU EPIGL ESOPG ESO ETHMO \xc2 EYE BROW EYELI FACE FBINC FBLAC FBMAX FBNAS FBPAL FBVOM FBZYG FALLT FEMOR "
        "FMH FEMUR FET FIBU FING FINGN FOL FOOT FOREA FOREH FORES FOURC GB GEN GVU GENC GL GENL GLAND GLANS GLUTE GLUT GLUTM GROIN GUM HAR "
        "HAL HAND HEAD HART HV HVB HVT HEEL HEM HIP HIPJ HUMER HYMEN ILC ILE ILEOS ILEUM ILIAC ILCR ILCON INGUI JUGI INT ICX INASA INTRU "
        "INTRO ISCHI JAW KIDN\xc2 KNEE KNEEF KNEEJ LABIA LABMA LABMI LACRI LAM INSTL LARYN LEG LENS WBC LING LINGU LIP STOOLL LIVER LOBE "
        "LOCH ISH LUMBA LMN LUNG LN LNG LYM MAC MALLE MANDI MAR MAST MAXIL MAXS MEATU MEC MEDST MEDU MOU MPB METAC METAT MILK MITRL MOLAR "
        "MP MONSU MONSV MOUTH MRSA2 MYO NAIL NAILB NAILF NAILT NARES NASL NSS NLACR NP NTRAC NAVEL NECK NERVE NIPPL NOS NOSE NOSTR OCCIP "
        "OLECR OMEN ORBIT ORO OSCOX OVARY PALAT PLATH PLATS PALM PANCR PAFL PAS PARAT PARIE PARON PAROT PATEL PELV PENSH PENIS PANAL PERI "
        "PCARD PCLIT PERIH PNEAL PERIN PNEPH PNM PORBI PERRA PERIS PER PERT PERIT PTONS PERIU PERIV PHALA PILO PINNA PLC PLACF PLACM PLANT "
        "PLEUR PLEU PLR POPLI PREAU PRERE PRST PROS PUBIC PUL RADI RADIUS RECTL RECTU RBC RENL RNP RPERI RIB SACRA SACRO SACIL SACRU SALGL "
        "SCALP SCAPU SCLER SCROT SEMN SEM SEPTU SEROM SHIN SHOLJ SHOL SIGMO SINUS SKM SKENE SKULL INSTS SOLE SPRM SPHEN SPCOR SPLN STER STOM "
        "USTOM STOMA STUMP SCLV SDP SUB SUBD SGF SUBM SUBX SUBME SUBPH SPX SCLAV SUPRA SUPB SWT SWTG SYNOL SYN SYNOV TARS TDUCT TEAR TEMPL "
        "TEMPO TML TESTI THIGH THORA THRB THUMB TNL THM THYRD TIBIA TOE TOEN TONG TONS TOOTH TSK TRCHE TBRON TCN ULNA UMB UMBL URET URTH "
        "UTERI SAC UTER VAGIN VCUFF VGV VAL VAS VASTL VAULT VEIN VENTG VCSF VERMI VERTC VERTL VERTT VESI VESCL VESFLD VESTI VITR VOC VULVA "
        "WRIST")),
    "table-hl70063-to-v3-rolecode": dict(_identidad(V3_ROL, "MTH FTH SIB BRO SIS"),
                                         **_identidad(V2 % "0063", "DEP WRD CGV GRD OAD EME ASC OWN TRA MGR NON"),
                                         SEL=(V3_ROL, "ONESELF"), SPO=(V3_ROL, "SPS"), DOM=(V3_ROL, "SIGOTHR"), CHD=(V3_ROL, "CHILD"),
                                         GCH=(V3_ROL, "GRNDCHILD"), NCH=(V3_ROL, "NCHILD"), SCH=(V3_ROL, "STPCHLD"), FCH=(V3_ROL, "CHLDFOST"),
                                         PAR=(V3_ROL, "PRN"), GRP=(V3_ROL, "GRPRN"), EXF=(V3_ROL, "EXT"), FND=(V3_ROL, "FRND"),
                                         EMR=(V2 % "0131", "E"), EMC=(V2 % "0131", "C"), UNK=(V2 % "0131", "U"), OTH=(V2 % "0131", "O")),
    "table-hl70131-to-v2-0131": _identidad(V2 % "0131", "E C F I N S O U"),
}
CM_VXU = {"0322": "table-hl70322-to-event-status", "0162": "table-hl70162-to-v2-0162", "0163": "table-hl70163-to-v2-0163",
          "0550": "table-hl70550-to-v2-0550", "0063": "table-hl70063-to-v3-rolecode", "0131": "table-hl70131-to-v2-0131"}


def mapa(tabla, codigo):
    """Como CV.mapa, con las tablas de VXU."""
    m = MAPAS_VXU[CM_VXU[tabla]]
    return m[codigo] if codigo in m else FUERA


# ---------------------------------------------------------------------------- citas (§3.6)
C_VXU = {"RXA-3": ["[CM segment-rxa-to-immunization RXA-3 → occurrenceDateTime]", "[G RXA_Immunization.csv:6]", "[E2A §2.A.22 DTM]", "[F Immunization.occurrence[x] 1..1]"],
         "RXA-5": ["[CM segment-rxa-to-immunization RXA-5 → vaccineCode]", "[CM datatype-cwe-to-codeableconcept]", "[G RXA_Immunization.csv:8]", "[E4 §4.18.1.1]"],
         "RXA-6": ["[CM segment-rxa-to-immunization RXA-6 → doseQuantity.value]", "[G RXA_Immunization.csv:9]"],
         "RXA-7": ["[CM datatype-cwe-to-quantity]", "[G RXA_Immunization.csv:10]"],
         "RXA-9": ["[G RXA_Immunization.csv:12] (comentario)", "[AMB-VX-9]"],
         "RXA-10": ["[CM segment-rxa-to-immunization RXA-10 → performer.actor(Practitioner), function AP]", "[CM datatype-xcn-to-practitioner]", "[G RXA_Immunization.csv:13-15]"],
         "RXA-11": ["[G RXA_Immunization.csv:16,33-34]", "[L-VX-1]"],
         "RXA-15": ["[CM segment-rxa-to-immunization RXA-15 → lotNumber]", "[G RXA_Immunization.csv:20]"],
         "RXA-16": ["[CM segment-rxa-to-immunization RXA-16 → expirationDate]", "[G RXA_Immunization.csv:21]", "[E4 §4.14.7.16 YYYYMM]"],
         "RXA-17": ["[CM segment-rxa-to-immunization RXA-17 → manufacturer(Organization)]", "[CM datatype-cwe-to-organization]", "[G RXA_Immunization.csv:22]", "[E4 §4.18.1.2]"],
         "RXA-18": ["[CM segment-rxa-to-immunization RXA-18 → statusReason]", "[G RXA_Immunization.csv:23]"],
         "RXA-19": ["[CM segment-rxa-to-immunization RXA-19 → reasonCode]", "[G RXA_Immunization.csv:24]"],
         "RXA-20": ["[CM segment-rxa-to-immunization RXA-20 → status IF RXA-21 NOT EQUALS D]", "[CM table-hl70322-to-event-status]", "[G RXA_Immunization.csv:25-26]", "[E4 §4.14.7.20 tabla 0322]", "[F Immunization.status required]"],
         "RXA-21": ["[CM segment-rxa-to-immunization RXA-21 → status entered-in-error IF D]", "[G RXA_Immunization.csv:27]", "[E4 §4.14.7.21 tabla 0323]"],
         "RXA-22": ["[CM segment-rxa-to-immunization RXA-22 → recorded IF RXA-21 EQUALS A]", "[G RXA_Immunization.csv:28]", "[AMB-VX-3]", "[Q-VX-D-3]"],
         "RXR-1": ["[CM segment-rxr-to-immunization RXR-1 → route]", "[CM table-hl70162-to-v2-0162]", "[G RXR_Immunization.csv:4]", "[E4 §4.14.2.1 tabla 0162]"],
         "RXR-2": ["[CM segment-rxr-to-immunization RXR-2 → site]", "[CM table-hl70163-to-v2-0163]", "[CM table-hl70550-to-v2-0550]", "[G RXR_Immunization.csv:5]", "[E4 §4.14.2.2]", "[AMB-VX-2]"],
         "ORC-1": ["[E4 CH04.txt:12397-12421] ORDER: ORC [TIMING] RXA [RXR] [OBSERVATION]"],
         "ORC-2": ["[CM segment-orc-to-immunization ORC-2 → identifier[1] PLAC]", "[CM datatype-ei-extension-to-identifier]", "[G ORC_Immunization.csv:5-7]"],
         "ORC-3": ["[CM segment-orc-to-immunization ORC-3 → identifier[2] FILL]", "[G ORC_Immunization.csv:8-10]"],
         "ORC-9": ["[CM segment-orc-to-immunization ORC-9 → recorded]", "[G ORC_Immunization.csv:17]", "[AMB-VX-3]", "[Q-VX-D-3]"],
         "ORC-12": ["[CM segment-orc-to-immunization ORC-12 → performer.actor(PractitionerRole), function OP]", "[CM datatype-xcn-to-practitionerrole]", "[G ORC_Immunization.csv:20-22]"],
         "RXA": ["[G MSG_VXU_V04.csv:42,58-59] ORC/RXA/RXR → Immunization[1]"], "OBX": ["[G MSG_VXU_V04.csv:61-62] OBX → Observation[2], partOf Immunization[1]"],
         "NK1-2": ["[CM segment-nk1-to-relatedperson NK1-2 → name[1]]", "[CM segment-nk1-to-patient NK1-2 → contact.name]", "[G NK1_RelatedPerson.csv:5]", "[G NK1_Patient.csv:5]"],
         "NK1-3": ["[CM table-hl70063-to-v3-rolecode]", "[G NK1_RelatedPerson.csv:6-7]", "[G NK1_Patient.csv:6]"],
         "NK1-5": ["[CM datatype-xtn-to-contactpoint]", "[G NK1_RelatedPerson.csv:9]"], "NK1-6": ["[G NK1_RelatedPerson.csv:10-11] use work"],
         "NK1-7": ["[CM table-hl70131-to-v2-0131]", "[G NK1_RelatedPerson.csv:12-14]"], "NK1-15": ["[CM table-hl70001-to-administrative-gender]", "[G NK1_RelatedPerson.csv:22]"],
         "NK1-16": ["[G NK1_RelatedPerson.csv:23]"], "NK1": ["[G MSG_VXU_V04.csv:16-17] NK1 → RelatedPerson[1] o Patient[1].contact"],
         "PD1": ["[G PD1_Patient.csv:6-19]", "[L-VX-3]"]}
C_SEG = {"PV1": ["[G MSG_VXU_V04.csv:20] PV1 → Encounter[1] «only if the system wants»"],             # las claves que en CV.C
         "PID": ["[G MSG_VXU_V04.csv:12,42] PID → Patient[1]"], "OBX": C_VXU["OBX"]}                  # son de ADT u ORU


def _cit(clave):
    base = re.sub(r"\(\d+\)", "", clave)
    return C_SEG.get(base) or C_VXU.get(base) or CV._cit(clave)


def _cuenta(J, subtipo, hecho, que, clase="fidelidad", tabla=False, citas=None):
    """J.cuenta con las citas de VXU (las claves PID, PV1 y OBX de conversion.C son de ADT u ORU)."""
    J.cuenta(subtipo, hecho, que, clase=clase, tabla=tabla, citas=citas or _cit(hecho))


def _nota(J, subtipo, hecho, que, certeza="literal"):
    J.hs.append(CV._h("nota", subtipo, hecho, que, cuenta=False, certeza=certeza, citas=_cit(hecho)))


def _dec(J, q):
    return J.dec.get(q, DECISIONES_VX[q])


def con_alternativas_vx(*qs):
    """Las decisiones con la alternativa de las Q indicadas (sensibilidad preinscrita de vx/decisiones-qvx.md)."""
    return {q: ALTERNATIVA_VX[q] for q in qs}


def _seg_hecho(seg, i):
    """«RXA» para el primer grupo, «RXA(2)» para el segundo: el hecho de lo que no tiene campo."""
    return seg if i == 1 else "%s(%d)" % (seg, i)


# ---------------------------------------------------------------------------- el mensaje (§2.2)
def grupos(m):
    """[{orc, rxa, rxr, obx, sin_orc, rxr_antes}] por grupo ORDER, y cuántos OBX quedan fuera de él. Un ORC abre grupo; un RXA sin
    ORC delante, también (AMB-VX-12); RXR y OBX van al grupo abierto; TQ1/TQ2 y NTE se ignoran; un OBX antes del primer grupo está
    fuera de la estructura de 2.5 y solo se cuenta (L-VX-10)."""
    gs, fuera = [], 0
    for s in m.segs:
        n = s.split(m.f)[0]
        if n == "ORC":
            gs.append({"orc": s, "rxa": None, "rxr": None, "obx": [], "sin_orc": False, "rxr_antes": False})
        elif n == "RXA":
            if not gs or gs[-1]["rxa"] is not None:
                gs.append({"orc": None, "rxa": s, "rxr": None, "obx": [], "sin_orc": True, "rxr_antes": False})
            else:
                gs[-1]["rxa"] = s
        elif n == "RXR" and gs:
            if gs[-1]["rxa"] is None:
                gs[-1]["rxr_antes"] = True
            elif gs[-1]["rxr"] is None:
                gs[-1]["rxr"] = s
        elif n == "OBX":
            if gs:
                gs[-1]["obx"].append(s)
            else:
                fuera += 1
    return gs, fuera


def imposibles(m):
    """§2.3: los valores imposibles de un VXU (fijan el rechazo aceptable, Q-CV-D-7). Los de tabla, solo en 2.5 (L18)."""
    out = CV._imposibles(m, "vxu")                                   # PID-7, PID-8 y OBX-5 NM, como en ADT y ORU
    v25 = _comp(m, _f(m, m.segs[0], 12), 1) in ("2.5", "")
    for g in grupos(m)[0]:
        rxa = g["rxa"]
        if rxa is not None:
            for n in (3, 16):
                v = _t(m, (_reps(m, _f(m, rxa, n)) or [""])[0], 1)
                if v and MR.partes_dtm(v)[0] is None:
                    out.append("RXA-%d" % n)
            v6 = _d(m, _f(m, rxa, 6))
            if v6 and not CV.NM_RE.match(v6):
                out.append("RXA-6")
            c20, c21 = _t(m, _f(m, rxa, 20), 1).upper(), _t(m, _f(m, rxa, 21), 1).upper()
            if v25 and c20 and mapa("0322", c20) == FUERA:
                out.append("RXA-20")
            if v25 and c21 and c21 not in ACCION_0323:
                out.append("RXA-21")
        if g["rxr"] is not None and v25:                             # un código local declarado (CE.3 ≠ HL70162) no es imposible
            c1, c3 = _t(m, _f(m, g["rxr"], 1), 1).upper(), _t(m, _f(m, g["rxr"], 1), 3).upper()
            if c1 and c3 in ("", "HL70162") and mapa("0162", c1) == FUERA:
                out.append("RXR-1")
    return out


def recuentos(m):
    """§2.4: lo propio de la familia, sin datos personales."""
    gs, fuera = grupos(m)
    est, acc = {}, {}
    for g in gs:
        if g["rxa"] is not None:
            c, a = _t(m, _f(m, g["rxa"], 20), 1), _t(m, _f(m, g["rxa"], 21), 1)
            est[c] = est.get(c, 0) + 1
            acc[a] = acc.get(a, 0) + 1
    return {"grupos_orden": len(gs), "obx_en_orden": sum(len(g["obx"]) for g in gs), "obx_fuera_orden": fuera,
            "nk1": len(m.segmentos("NK1")), "rxa_por_estado": est, "rxa_por_accion": acc}


# ---------------------------------------------------------------------------- emparejamiento (§2.2)
def _misma_fecha(m, origen, obs):
    """RXA-3 frente a occurrenceDateTime con la regla de fechas del juez (R-CV-7): igual si no dejaría hallazgo que cuente."""
    if not origen or not isinstance(obs, str):
        return False
    sub = CV.Juicio(m, True, CV.DECISIONES)
    sub.entries = []
    CV._fecha(sub, "RXA-3", origen, obs, "dateTime", "Immunization.occurrenceDateTime")
    return not any(h["cuenta"] for h in sub.hs)


def _parte_de(entries, x, d):
    return any(CV.resolver(entries, p, x, "Immunization")[0] is d for p in x["r"].get("partOf") or [] if isinstance(p, dict))


def _familia_nk1(m, nk1):
    return _d(m, _sub(m, _comp(m, (_reps(m, _f(m, nk1, 2)) or [""])[0], 1), 1))


def emparejar(m, entries, top, out, pat, rol, usados):
    """Gancho 4 de conversion.emparejar, tras el Patient. Immunization por grupo ORDER: (1) ORC-3.1/ORC-2.1 en identifier,
    (2) RXA-5 (CE.1 o CE.4) y RXA-3, (3) RXA-5 si es la única libre con ese código, (4) por orden si hay tantas como grupos;
    dos candidatas igual de buenas → ambiguo. Observation por OBX: partOf a la Immunization del grupo y código, si no código.
    RelatedPerson o Patient.contact por NK1 (identifier, apellido, orden). Encounter por PV1, como en adt_conv."""
    gs, fuera = grupos(m)
    inms = [e for e in top if e["tipo"] == "Immunization"]
    n_rxa = sum(1 for g in gs if g["rxa"] is not None)
    libres, asignadas, por_i, claves = list(inms), {}, {}, {}
    for i, g in enumerate(gs, 1):
        if g["rxa"] is not None:
            r5 = (_reps(m, _f(m, g["rxa"], 5)) or [""])[0]
            claves[i] = (_t(m, _f(m, g["orc"], 3), 1), _t(m, _f(m, g["orc"], 2), 1), {_t(m, r5, 1), _t(m, r5, 4)} - {""},
                         _t(m, (_reps(m, _f(m, g["rxa"], 3)) or [""])[0], 1))
    for paso in ("identifier", "codigo+fecha", "codigo", "orden"):      # VX2-c: cada clave para todos los grupos antes de la siguiente
        for i, (fill, plac, cods, o3) in claves.items():
            if i in asignadas:
                continue
            cod = [e for e in libres if cods & {x[1] for x in _codigos(e["r"].get("vaccineCode"))}]
            if paso == "identifier":
                c = [e for e in libres if (fill and fill in _valores(e["r"])) or (plac and plac in _valores(e["r"]))]
            elif paso == "codigo+fecha":
                c = [e for e in cod if _misma_fecha(m, o3, e["r"].get("occurrenceDateTime"))]
            elif paso == "codigo":
                c = cod if len(cod) == 1 else []
            else:
                c = libres[:1] if len(inms) == n_rxa and libres else []
            if len(c) > 1:
                out["ambiguo"].append("Immunization#%d" % i)
                asignadas[i] = None
            elif c:
                libres.remove(c[0])
                asignadas[i], por_i[i] = c[0], paso
    for i in claves:
        d = asignadas.get(i)
        rol("Immunization#%d" % i, "RXA %d" % i, d, por_i.get(i), len(inms))
    obs = [e for e in top if e["tipo"] == "Observation"]
    libres_o, por_obx = list(obs), {}
    otras = {x["i"] for x in asignadas.values() if x}
    for paso in ("partOf", "codigo"):                                # VX1-e: primero todas por partOf, después por código
        for i, g in enumerate(gs, 1):
            d = asignadas.get(i)
            for j, obx in enumerate(g["obx"], 1):
                if (i, j) in por_obx:
                    continue
                cod, sub = _t(m, _f(m, obx, 3), 1), _f(m, obx, 4)
                cands = [x for x in libres_o if cod and cod in {c[1] for c in _codigos(x["r"].get("code"))}]
                if paso == "partOf":
                    cands = [x for x in cands if d is not None and _parte_de(entries, x, d)]
                else:                                                # las que son parte de otra Immunization, al final
                    cands = sorted(cands, key=lambda x: any(_parte_de(entries, x, y) for y in asignadas.values()
                                                            if y and y is not d and y["i"] in otras))
                if len(cands) > 1 and sub:
                    cands = [x for x in cands if sub in _valores(x["r"])] or cands
                if cands:
                    libres_o.remove(cands[0])
                    por_obx[(i, j)] = (cands[0], paso)
    for i, g in enumerate(gs, 1):
        for j in range(1, len(g["obx"]) + 1):
            o, por = por_obx.get((i, j), (None, None))
            rol("Observation#%d.%d" % (i, j), "OBX %d.%d" % (i, j), o, por, len(obs))
    for d in libres:
        out["sobrantes"].append({"resourceType": "Immunization", "fullUrl": d["fullUrl"], "motivo": "inventado", "hecho": "RXA"})
        usados.add(d["i"])
    for k, o in enumerate(libres_o):
        out["sobrantes"].append({"resourceType": "Observation", "fullUrl": o["fullUrl"],
                                 "motivo": "origen_guia" if k < fuera else "inventado", "hecho": "OBX"})
        usados.add(o["i"])
    _emparejar_nk1(m, top, out, pat, rol, usados)
    _emparejar_encounter(m, entries, top, out, pat, rol, usados)


def _emparejar_nk1(m, top, out, pat, rol, usados):
    nk1s = m.segmentos("NK1")
    rps = [e for e in top if e["tipo"] == "RelatedPerson"]
    cs = [c for c in (pat["r"].get("contact") or []) if isinstance(c, dict)] if pat else []
    libres_r, libres_c = list(rps), list(range(len(cs)))
    otros = len(m.segmentos("GT1")) + len(m.segmentos("IN1"))       # la guía crea RelatedPerson también desde GT1 e IN1 (L-VX-10)
    out["contactos_vx"] = {}
    for k, nk1 in enumerate(nk1s, 1):
        if not (_f(m, nk1, 2) or _f(m, nk1, 3)):
            continue
        fam = _familia_nk1(m, nk1)
        ids = {_t(m, x, 1) for n in (33, 12) for x in _reps(m, _f(m, nk1, n))} - {""}
        c, por = [e for e in libres_r if ids & _valores(e["r"])], "identifier"
        if not c:
            c, por = [e for e in libres_r if fam and fam in {x.get("family") for x in e["r"].get("name") or [] if isinstance(x, dict)}], "nombre"
        cc = [j for j in libres_c if fam and isinstance(cs[j].get("name"), dict) and cs[j]["name"].get("family") == fam]
        r3 = _t(m, _f(m, nk1, 3), 1)                                 # VX2-c: dos con el mismo apellido, desempata la relación
        rel = {r3, (mapa("0063", r3) if mapa("0063", r3) not in (FUERA, None) else ("", ""))[1]} - {""}
        con_rel = lambda xs, f: [x for x in xs if rel & {y[1] for z in f(x) for y in _codigos(z)}]  # noqa: E731
        if len(c) > 1 and len(con_rel(c, lambda e: e["r"].get("relationship") or [])) == 1:
            c = con_rel(c, lambda e: e["r"].get("relationship") or [])
        if len(cc) > 1 and len(con_rel(cc, lambda j: cs[j].get("relationship") or [])) == 1:
            cc = con_rel(cc, lambda j: cs[j].get("relationship") or [])
        if len(c) > 1 or len(cc) > 1:                                # L-VX-11
            out["ambiguo"].append("RelatedPerson#%d" % k)
            continue
        if not c and not cc and not otros:                          # VX1-e: con GT1/IN1 hay RelatedPerson de otro origen
            if len(rps) == len(nk1s) and libres_r:
                c, por = libres_r[:1], "orden"
            elif len(cs) == len(nk1s) and libres_c:
                cc = libres_c[:1]
        e = c[0] if c else None
        if e:
            libres_r.remove(e)
        if cc:
            libres_c.remove(cc[0])
            out["contactos_vx"][k] = cc[0]
        rol("RelatedPerson#%d" % k, "NK1 %d" % k, e, por if e else ("contact" if cc else None), len(rps))
    for k, e in enumerate(libres_r):
        out["sobrantes"].append({"resourceType": "RelatedPerson", "fullUrl": e["fullUrl"], "motivo": "origen_guia" if k < otros else "inventado",
                                 "hecho": "NK1"})
        usados.add(e["i"])
    out["contactos_vx_libres"] = libres_c


def _emparejar_encounter(m, entries, top, out, pat, rol, usados):
    """Como la rama adt de conversion.emparejar; sin PV1, un Encounter no tiene origen (S-VX-10)."""
    pv1 = _seg(m, "PV1")
    encs = [e for e in top if e["tipo"] == "Encounter"]
    en = None
    if pv1 is not None:
        v19 = _t(m, _f(m, pv1, 19), 1)
        por = None
        if len(encs) == 1:
            en, por = encs[0], "unico"
        elif encs:
            s = [e for e in encs if pat is not None and CV.resolver(entries, e["r"].get("subject"), e, "Patient")[0] is pat]
            si = [e for e in s if v19 and v19 in _valores(e["r"])]
            solo_id = [e for e in encs if v19 and v19 in _valores(e["r"])]
            if len(si) == 1:
                en, por = si[0], "identifier"
            elif len(s) == 1:
                en, por = s[0], "referencia"
            elif len(solo_id) == 1:
                en, por = solo_id[0], "identifier"
            else:
                out["ambiguo"].append("Encounter#1")
        rol("Encounter#1", "PV1", en, por, len(encs))
    for e in encs:
        if e is en or (pv1 is not None and en is None):
            continue
        out["sobrantes"].append({"resourceType": "Encounter", "fullUrl": e["fullUrl"], "motivo": "duplicado" if pv1 is not None else "inventado",
                                 "hecho": "PV1"})
        usados.add(e["i"])


# ---------------------------------------------------------------------------- el juicio (§3)
def juzgar(J, m, lec, pat_entry):
    """Gancho 5 de conversion._juzgar (el Patient ya está juzgado). Juzga también los sobrantes, con sus citas, y deja la lista vacía."""
    roles = {x["rol"]: x for x in lec["recursos"]}
    gs, fuera = grupos(m)
    pv1 = _seg(m, "PV1")
    en = roles.get("Encounter#1")
    en_entry = en["entry"] if en else None
    k = 0
    for i, g in enumerate(gs, 1):
        e = None
        if g["sin_orc"]:
            _nota(J, "estructura", _hecho("ORC", i, 1), "RXA sin ORC delante: se espera su Immunization (AMB-VX-12)")
        if g["rxr_antes"]:
            _nota(J, "estructura", _hecho("RXR", i, 1), "RXR delante del RXA: fuera de la estructura de 2.5, se ignora")
        if g["rxa"] is None:
            _nota(J, "estructura", _hecho("ORC", i, 1), "ORC sin RXA: no se espera Immunization de este grupo")
        else:
            x = roles.get("Immunization#%d" % i)
            e = x["entry"] if x else None
            if e is None:
                _cuenta(J, "recurso_ausente", _hecho("RXA", i, 5), "falta la Immunization del grupo ORDER %d" % i, citas=C_VXU["RXA"])
            else:
                _inmunizacion(J, m, g, e["r"], e, pat_entry, i, pv1, en_entry)
        for j, obx in enumerate(g["obx"], 1):
            k += 1
            h3 = _hecho("OBX", k, 3)
            o = (roles.get("Observation#%d.%d" % (i, j)) or {}).get("entry")
            if o is None:
                abs_ = e is not None and _absorbido(m, obx, e["r"])
                if abs_ and _dec(J, "Q-VX-D-4") == "convencion":
                    _nota(J, "absorbido", h3, "OBX %d.%d sin Observation: su valor está en la Immunization (AMB-VX-4, alternativa de Q-VX-D-4)" % (i, j),
                           "ambiguedad AMB-VX-4")
                else:
                    _cuenta(J, "recurso_ausente", h3, "falta la Observation del OBX %d.%d%s" % (i, j, " (su valor está en la Immunization: Q-VX-D-4)" if abs_ else ""),
                             citas=C_VXU["OBX"])
                continue
            CV._observacion(J, m, obx, o["r"], o, pat_entry, k, None)         # Q-VX-D-10: todas las reglas de oru_conv
            _parte(J, o, e, h3)
    _parientes(J, m, lec, pat_entry, roles)
    if pv1 is not None and en_entry is None and "Encounter#1" not in lec["ambiguo"]:
        _nota(J, "convencion", "PV1", "sin Encounter del PV1: la guía lo crea «only if the system wants» (S-VX-10, L-VX-8)")
    elif pv1 is not None and en_entry is not None:
        CV._encounter(J, m, pv1, en_entry["r"], lec["entries"], pat_entry, en_entry)
    if _seg(m, "PD1") is not None:
        _nota(J, "fuera_proyeccion", "PD1", "PD1 fuera del perfil (L-VX-3, Q-VX-D-5)")
    if fuera:
        _nota(J, "fuera_proyeccion", "OBX", "%d OBX fuera del grupo ORDER: solo se cuentan (L-VX-10)" % fuera)
    for s in lec["sobrantes"]:
        if s["motivo"] == "origen_guia":
            _nota(J, "fuera_proyeccion", s["hecho"], "%s de un segmento que el perfil no juzga (OBX fuera de ORDER, GT1, IN1: L-VX-10)" % s["resourceType"])
        else:
            _cuenta(J, "recurso_%s" % s["motivo"], s["hecho"], "%s %s sin origen propio en el mensaje" % (s["resourceType"], s["fullUrl"]),
                     citas=_cit(s["hecho"]))
    lec["sobrantes"] = []
    for h in J.hs:                                                   # el Patient ausente lo juzgó la parte común, con la cita de ADT
        if h["hecho"] == "PID" and h["citas"] == CV.C["PID"]:
            h["citas"] = list(C_SEG["PID"])


def _cadenas(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from _cadenas(v)
    elif isinstance(x, list):
        for v in x:
            yield from _cadenas(v)


def _absorbido(m, obx, r):
    """AMB-VX-4: el valor del OBX (CE.1, o el texto o la fecha) está en algún elemento de la Immunization que puede absorberlo."""
    rep = (_reps(m, _f(m, obx, 5)) or [""])[0]
    vals = {v for v in (_t(m, rep, 1), _d(m, rep)) if v}
    dentro = {s for c in ABSORBEN for s in _cadenas(r.get(c))}
    digitos = {re.sub(r"\D", "", s) for s in dentro}
    return bool(vals & dentro) or any(v.isdigit() and v in digitos for v in vals)


def _parte(J, o, e, h):
    """§3.2: Observation.partOf debe resolver a la Immunization de su grupo (sin ella, lo absorbe su recurso ausente)."""
    if e is None:
        return
    refs = [p for p in o["r"].get("partOf") or [] if isinstance(p, dict)]
    if not refs:
        _cuenta(J, "dato_perdido", h, "Observation.partOf: falta la referencia a la Immunization de su grupo", citas=C_VXU["OBX"])
        return
    if any(CV.resolver(J.entries, p, o, "Immunization")[0] is e for p in refs):
        return
    _cuenta(J, "referencia_rota", h, "Observation.partOf %r no resuelve a la Immunization de su grupo" % refs, citas=C_VXU["OBX"] + CV.C["ref"])


def _inmunizacion(J, m, g, r, e, pat_entry, i, pv1, en_entry):
    orc, rxa, rxr = g["orc"], g["rxa"], g["rxr"]
    h = lambda seg, n: _hecho(seg, i, n)  # noqa: E731
    hr = _seg_hecho("RXA", i)
    _status(J, m, rxa, r, h)
    r18 = (_reps(m, _f(m, rxa, 18)) or [""])[0]
    if _t(m, r18, 1) or _t(m, r18, 4):
        _codigo(J, m, r18, r.get("statusReason"), h("RXA", 18), "Immunization.statusReason")
    elif r.get("statusReason") is not None:
        _cuenta(J, "dato_inventado", h("RXA", 18), "Immunization.statusReason %r sin RXA-18" % r.get("statusReason"))
    r5 = (_reps(m, _f(m, rxa, 5)) or [""])[0]
    if not (_t(m, r5, 1) or _t(m, r5, 4) or _t(m, r5, 9)):
        _nota(J, "sin_esperado", h("RXA", 5), "RXA-5 vacío (R): la hoja no tiene esperado para vaccineCode (1..1)")
    else:
        if r.get("vaccineCode") is None:
            _cuenta(J, "fhir_invalido", h("RXA", 5), "Immunization.vaccineCode: falta (1..1)")
        _codigo(J, m, r5, r.get("vaccineCode"), h("RXA", 5), "Immunization.vaccineCode")
    CV._sujeto(J, m, {"subject": r.get("patient")}, e, pat_entry, "Immunization.patient", "PID-3")
    _encuentro(J, r, e, pv1, en_entry)
    _ocurrencia(J, m, rxa, r, h)
    _registro(J, m, orc, rxa, r, h)
    deducido = {"primarySource": ("RXA-9", bool(_t(m, _f(m, rxa, 9), 1)), "AMB-VX-9"),           # DV-VX-8: deducidos de un campo,
                "isSubpotent": ("RXA-20 PA", _t(m, _f(m, rxa, 20), 1).upper() == "PA",           # no «por omisión»
                                "R4 Immunization.isSubpotent: «partial administration»")}
    for c in ("primarySource", "isSubpotent"):                       # Q-VX-D-7
        if r.get(c) is not None:
            campo, si, apoyo = deducido[c]
            if si:
                _nota(J, "convencion", hr, "Immunization.%s %r deducido de %s, sin fila en la guía (%s; DV-VX-8)" % (c, r.get(c), campo, apoyo))
            elif _dec(J, "Q-VX-D-7") == "inventado":
                _cuenta(J, "dato_inventado", hr, "Immunization.%s %r sin campo en el mensaje (Q-VX-D-7)" % (c, r.get(c)), citas=C_VXU["RXA"])
            else:
                _nota(J, "convencion", hr, "Immunization.%s %r por omisión (alternativa de Q-VX-D-7)" % (c, r.get(c)))
    if r.get("reportOrigin") is not None:                            # AMB-VX-9
        if _t(m, _f(m, rxa, 9), 1):
            _nota(J, "convencion", h("RXA", 9), "Immunization.reportOrigin desde RXA-9 (AMB-VX-9: la guía lo deja a las IG)", "ambiguedad AMB-VX-9")
        else:
            _cuenta(J, "dato_inventado", h("RXA", 9), "Immunization.reportOrigin %r sin RXA-9" % r.get("reportOrigin"))
    if r.get("location") is not None:                                # L-VX-1
        if _f(m, rxa, 11):
            _nota(J, "fuera_proyeccion", h("RXA", 11), "Immunization.location: RXA-11 no tiene fila en la guía (L-VX-1)")
        else:
            _nota(J, "extra", h("RXA", 11), "Immunization.location sin RXA-11 (L-VX-1)")
    elif _f(m, rxa, 11):
        _nota(J, "fuera_proyeccion", h("RXA", 11), "RXA-11 no tiene fila en la guía (L-VX-1)")
    _fabricante(J, m, rxa, r, e, h)
    _lote(J, m, rxa, r, h)
    CV._fecha(J, h("RXA", 16), _t(m, (_reps(m, _f(m, rxa, 16)) or [""])[0], 1), r.get("expirationDate"), "date", "Immunization.expirationDate")
    _ruta_sitio(J, m, rxr, r, h)
    _dosis(J, m, rxa, r, h)
    _performers(J, m, orc, rxa, r, e, h)
    _motivos(J, m, rxa, r, h)
    _identificadores(J, m, orc, r, h)
    absorbe = any(_absorbido(m, obx, {"fundingSource": r.get("fundingSource")}) for obx in g["obx"])
    if r.get("fundingSource") is not None:
        if absorbe:
            _nota(J, "absorbido", hr, "Immunization.fundingSource con el valor de un OBX del grupo (AMB-VX-4)", "ambiguedad AMB-VX-4")
        else:
            _cuenta(J, "dato_inventado", hr, "Immunization.fundingSource %r sin campo ni OBX que lo sostenga" % r.get("fundingSource"), citas=C_VXU["RXA"])
    extra = [c for c in SIN_FILA_REP if r.get(c)]
    if extra:
        _nota(J, "extra", hr, "Immunization sin fila en la guía: %s" % ", ".join(extra))


def _status(J, m, rxa, r, h):
    """R-VX-1 (S-VX-5, AMB-VX-11): RXA-21 D → entered-in-error; si no, RXA-20 por la 0322; RXA-20 vacío → completed."""
    d, c = _t(m, _f(m, rxa, 21), 1).upper(), _t(m, _f(m, rxa, 20), 1)
    obs = r.get("status")
    if d != "D" and c and mapa("0322", c) == FUERA and mapa("0322", c.upper()) == FUERA:
        if obs is None:
            _cuenta(J, "fhir_invalido", h("RXA", 20), "Immunization.status: falta (1..1)")
        elif obs == c:
            _cuenta(J, "valor_imposible_convertido", h("RXA", 20), "Immunization.status %r copiado de RXA-20 fuera de la 0322" % obs,
                     clase="valor_imposible_aceptado", tabla=True)
            if obs not in ESTADO_FHIR:
                _cuenta(J, "fhir_invalido", h("RXA", 20), "Immunization.status %r fuera de immunization-status (required)" % obs)
        elif obs in ESTADO_FHIR:
            _nota(J, "sin_esperado" if J.v25 else "version", h("RXA", 20), "Immunization.status %r con RXA-20 %r fuera de la 0322" % (obs, c),
                   "literal" if J.v25 else "ambiguedad L18")
        else:
            _cuenta(J, "fhir_invalido", h("RXA", 20), "Immunization.status %r fuera de immunization-status (required)" % obs)
        return
    if d == "D":
        adm, hecho = "entered-in-error", h("RXA", 21)
    elif not c:
        adm, hecho = "completed", h("RXA", 20)
    else:
        t = mapa("0322", c)
        if t == FUERA:                                               # AMB-CV-1: el código en minúscula
            t = mapa("0322", c.upper())
            if obs == t[1]:
                _nota(J, "convencion", h("RXA", 20), "Immunization.status %r desde %r en minúscula (AMB-CV-1)" % (obs, c), "ambiguedad AMB-CV-1")
                return
        adm, hecho = t[1], h("RXA", 20)
    if obs is None or obs not in ESTADO_FHIR:
        _cuenta(J, "fhir_invalido", h("RXA", 20), "Immunization.status %r (1..1, required)" % obs)
    elif obs != adm:
        clase = "codigo_mal_mapeado" if c and d != "D" else "valor_distinto"
        _cuenta(J, clase, hecho, "Immunization.status: esperado %r (RXA-20 %r, RXA-21 %r), observado %r" % (adm, c, d, obs))


def _codigo(J, m, rep, cc, hecho, ruta):
    """Como CV._codigo (CE.1 y CE.4 en algún coding; CE.3/CE.6 → system; CE.9 → text) con CVX y MVX fijados (Q-VX-D-1)."""
    obs = _codigos(cc)
    for ci, si in ((1, 3), (4, 6)):
        code, sis = _t(m, rep, ci), _t(m, rep, si)
        if not code:
            continue
        con = [c for c in obs if c[1] == code]
        if not con:
            _cuenta(J, "dato_perdido" if not obs else "valor_distinto", hecho, "%s: falta el código %r (observado %r)" % (ruta, code, [c[1] for c in obs]))
            continue
        uri = (URI_VX if _dec(J, "Q-VX-D-1") == "fijar" else CV.URI_SISTEMA).get(sis.upper()) if sis else None
        admitidas = {uri, URI_V2_TABLA.get(sis.upper())} if sis else set()     # DV-VX-7: la uri de la tabla v2 de R4 también
        if uri and not any(c[0] in admitidas for c in con):
            _cuenta(J, "codigo_mal_mapeado" if any(c[0] for c in con) else "dato_perdido", hecho,
                     "%s %r: system esperado %r (de %r), observado %r" % (ruta, code, uri, sis, [c[0] for c in con]))
    t9 = _t(m, rep, 9)
    if t9 and (cc or {}).get("text") != t9:
        _cuenta(J, "dato_perdido" if not (cc or {}).get("text") else "valor_distinto", hecho, "%s.text: esperado %r" % (ruta, t9))


def _encuentro(J, r, e, pv1, en_entry):
    """AMB-VX-5 (Q-VX-D-9): con PV1 y Encounter, encounter ausente es convención; presente debe resolver. Sin PV1, presente es
    dato inventado (si apunta a un Encounter, ese ya cuenta como recurso inventado)."""
    ref = r.get("encounter")
    x = CV.resolver(J.entries, ref, e, "Encounter")[0] if ref is not None else None
    if pv1 is None:
        if ref is None:
            return
        if x is not None and x["tipo"] == "Encounter":
            _nota(J, "convencion", "PV1-19", "Immunization.encounter a un Encounter sin PV1 (cuenta el Encounter)")
        else:
            _cuenta(J, "dato_inventado", "PV1-19", "Immunization.encounter %r sin PV1" % ref, citas=C_SEG["PV1"])
        return
    if ref is None:
        if en_entry is not None:
            if _dec(J, "Q-VX-D-9") == "perdido":
                _cuenta(J, "dato_perdido", "PV1-19", "Immunization.encounter: falta la referencia al Encounter del PV1 (alternativa de Q-VX-D-9)", citas=C_SEG["PV1"])
            else:
                _nota(J, "convencion", "PV1-19", "Immunization.encounter ausente (AMB-VX-5, Q-VX-D-9)", "ambiguedad AMB-VX-5")
        return
    if en_entry is None or x is not en_entry:
        _cuenta(J, "referencia_rota", "PV1-19", "Immunization.encounter %r no resuelve al Encounter del PV1" % ref, citas=C_SEG["PV1"] + CV.C["ref"])


def _ocurrencia(J, m, rxa, r, h):
    o3 = _t(m, (_reps(m, _f(m, rxa, 3)) or [""])[0], 1)
    odt, ost = r.get("occurrenceDateTime"), r.get("occurrenceString")
    if not o3:
        if odt is not None or ost is not None:
            _nota(J, "sin_esperado", h("RXA", 3), "RXA-3 vacío (R): la hoja no tiene esperado para occurrence[x]")
        return
    if ost is not None and odt is None:
        _cuenta(J, "valor_distinto", h("RXA", 3), "Immunization.occurrenceString %r: la guía da occurrenceDateTime" % ost)
        return
    if odt is None:
        _cuenta(J, "fhir_invalido", h("RXA", 3), "Immunization.occurrence[x]: falta (1..1)")
    CV._fecha(J, h("RXA", 3), o3, odt, "dateTime", "Immunization.occurrenceDateTime")


def _registro(J, m, orc, rxa, r, h):
    """Q-VX-D-3 (rxa22): manda RXA-22 cuando RXA-21 es A; si no, ORC-9. La alternativa (cualquiera) admite los dos (AMB-VX-3).
    Sin ninguno: recorded igual a RXA-22 (con RXA-21 distinto de A) es convención; otro valor, dato inventado."""
    o9 = _t(m, _f(m, orc, 9), 1)
    a21, r22 = _t(m, _f(m, rxa, 21), 1).upper(), _t(m, _f(m, rxa, 22), 1)
    de22 = [("RXA", 22, r22)] if r22 and a21 == "A" else []
    de9 = [("ORC", 9, o9)] if o9 else []
    adm = (de22 or de9) if _dec(J, "Q-VX-D-3") == "rxa22" else de9 + de22
    obs = r.get("recorded")

    def igual(v):
        sub = CV.Juicio(m, J.v25, J.dec)
        sub.entries = J.entries
        CV._fecha(sub, "RXA-22", v, obs, "dateTime", "Immunization.recorded")
        return not any(x["cuenta"] for x in sub.hs)
    if adm:
        if obs is None:
            s, n, _ = adm[0]
            _cuenta(J, "dato_perdido", h(s, n), "Immunization.recorded: falta (%s-%d)" % (s, n))
        elif not any(igual(v) for _, _, v in adm):
            s, n, v = adm[0]
            CV._fecha(J, h(s, n), v, obs, "dateTime", "Immunization.recorded")
        return
    if obs is None:
        return
    if r22 and igual(r22):
        _nota(J, "convencion", h("RXA", 22), "Immunization.recorded = RXA-22 con RXA-21 %r (AMB-VX-3)" % a21, "ambiguedad AMB-VX-3")
    else:
        _cuenta(J, "dato_inventado", h("ORC", 9), "Immunization.recorded %r sin ORC-9 ni RXA-22 con A" % obs)


def _fabricante(J, m, rxa, r, e, h):
    """RXA-17 (primera repetición) → Organization: identifier ∋ CE.1 (system MVX por Q-VX-D-1), name = CE.2 (o CE.9) desescapado."""
    hecho = h("RXA", 17)
    rep = (_reps(m, _f(m, rxa, 17)) or [""])[0]
    c1, c2, c3, c9 = _t(m, rep, 1), _t(m, rep, 2), _t(m, rep, 3), _t(m, rep, 9)
    ref = r.get("manufacturer")
    if not (c1 or c2 or c9):
        if ref is not None:
            _cuenta(J, "dato_inventado", hecho, "Immunization.manufacturer %r sin RXA-17" % ref)
        return
    if not isinstance(ref, dict):
        _cuenta(J, "dato_perdido", hecho, "Immunization.manufacturer: falta (RXA-17 %r)" % rep)
        return
    x, forma = CV.resolver(J.entries, ref, e, "Organization")
    if x is not None:
        J.referidas.add(x["i"])
        ids = [y for y in x["r"].get("identifier") or [] if isinstance(y, dict)]
        nombre = x["r"].get("name")
    elif forma == "logica":
        ids, nombre = [ref["identifier"]], ref.get("display")
    elif forma == "rota":
        _cuenta(J, "referencia_rota", hecho, "Immunization.manufacturer %r no resuelve" % ref, citas=C_VXU["RXA-17"] + CV.C["ref"])
        return
    else:
        if c1:
            _cuenta(J, "dato_perdido", hecho, "Immunization.manufacturer: solo display %r, falta el código %r" % (ref.get("display"), c1))
        elif ref.get("display") == (c2 or c9):
            _nota(J, "convencion", hecho, "Immunization.manufacturer: solo display, sin código en RXA-17")
        else:
            _cuenta(J, "valor_distinto", hecho, "Immunization.manufacturer.display: esperado %r, observado %r" % (c2 or c9, ref.get("display")))
        return
    if c1:
        con = [y for y in ids if y.get("value") == c1]
        if not con:
            _cuenta(J, "dato_perdido" if not ids else "valor_distinto", hecho, "Organization.identifier: falta %r" % c1)
        else:
            uri = URI_VX.get(c3.upper()) if c3 and _dec(J, "Q-VX-D-1") == "fijar" else None
            if uri and not any(y.get("system") in (uri, URI_V2_TABLA.get(c3.upper())) for y in con):
                _cuenta(J, "codigo_mal_mapeado" if any(y.get("system") for y in con) else "dato_perdido", hecho,
                         "Organization.identifier %r: system esperado %r (de %r), observado %r" % (c1, uri, c3, [y.get("system") for y in con]))
    esperado = c2 or c9
    if esperado and nombre != esperado:
        _cuenta(J, "dato_perdido" if nombre is None else "valor_distinto", hecho, "Organization.name: esperado %r, observado %r" % (esperado, nombre))


def _lote(J, m, rxa, r, h):
    """RXA-15: la primera repetición (Q-VX-D-8, L-VX-12); otra repetición es convención (alternativa: valor distinto)."""
    hecho = h("RXA", 15)
    reps = [_d(m, x) for x in _reps(m, _f(m, rxa, 15))]
    reps = [x for x in reps if x]
    obs = r.get("lotNumber")
    if not reps:
        if obs is not None:
            _cuenta(J, "dato_inventado", hecho, "Immunization.lotNumber %r sin RXA-15" % obs)
        return
    if obs is None:
        _cuenta(J, "dato_perdido", hecho, "Immunization.lotNumber: falta %r" % reps[0])
    elif obs == reps[0]:
        if len(reps) > 1:
            _nota(J, "extra", hecho, "RXA-15 repetido: %d lotes y lotNumber 0..1 (L-VX-12)" % len(reps))
    elif obs in reps[1:] and _dec(J, "Q-VX-D-8") != "primera":
        _nota(J, "convencion", hecho, "Immunization.lotNumber %r es la repetición %d de RXA-15 (Q-VX-D-8)" % (obs, reps.index(obs) + 1),
               "ambiguedad AMB-VX-7")
    else:
        _cuenta(J, "valor_distinto", hecho, "Immunization.lotNumber: esperado %r, observado %r" % (reps[0], obs))


def _tabla(J, hecho, v, cc, tabla, ruta, varios=False):
    """Como CV._codigo_tabla, con las tablas de VXU."""
    obs = [y for x in (cc if varios else [cc]) for y in _codigos(x)] if cc else []
    if not v:
        if obs:
            (_nota(J, "extra", hecho, "%s: %r sin código" % (ruta, obs)) if varios else
             _cuenta(J, "dato_inventado", hecho, "%s: %r sin código en el mensaje" % (ruta, obs)))
        return
    t = mapa(tabla, v)
    if t in (FUERA, None):
        if obs and v not in {c[1] for c in obs}:
            _nota(J, "convencion" if J.v25 else "version", hecho, "%s: %r para %r, fuera del ConceptMap" % (ruta, obs, v))
        return
    if tuple(t) in obs:
        return
    if not obs:
        _cuenta(J, "dato_perdido", hecho, "%s: falta %r" % (ruta, t))
    else:
        _cuenta(J, "codigo_mal_mapeado", hecho, "%s: esperado %r (de %r), observado %r" % (ruta, t, v, obs))


def _ruta_sitio(J, m, rxr, r, h):
    """RXR-1 por la 0162 (dos grupos, S-VX-6); RXR-2 por la 0163 o la 0550 (Q-VX-D-2, AMB-VX-2)."""
    _tabla(J, h("RXR", 1), _t(m, _f(m, rxr, 1), 1), r.get("route"), "0162", "Immunization.route")
    hecho, c = h("RXR", 2), _t(m, _f(m, rxr, 2), 1)
    obs = _codigos(r.get("site"))
    if not c:
        if obs:
            _cuenta(J, "dato_inventado", hecho, "Immunization.site %r sin RXR-2" % obs)
        return
    tablas = ("0550",) if _dec(J, "Q-VX-D-2") == "solo_0550" else ("0163", "0550")
    adm = [tuple(mapa(t, c)) for t in tablas if mapa(t, c) not in (FUERA, None)]
    if not adm:                                                      # fuera de las dos: convención, como CV._codigo_tabla
        if obs and c not in {x[1] for x in obs}:
            _nota(J, "convencion" if J.v25 else "version", hecho, "Immunization.site %r para %r, fuera de la 0163 y la 0550" % (obs, c))
        return
    if any(a in obs for a in adm):
        return
    if not obs:
        _cuenta(J, "dato_perdido", hecho, "Immunization.site: falta %r" % adm)
    else:
        _cuenta(J, "codigo_mal_mapeado", hecho, "Immunization.site: esperado uno de %r (de %r), observado %r" % (adm, c, obs))


def _dosis(J, m, rxa, r, h):
    """RXA-6 → doseQuantity.value como texto decimal (Q-CV-D-10, `.5` ≡ `0.5`); RXA-7 con las reglas de OBX-6 (CV._unidades, que
    lee OBX-6: aquí, la misma regla sobre RXA-7)."""
    q = r.get("doseQuantity") if isinstance(r.get("doseQuantity"), dict) else None
    v6 = _d(m, _f(m, rxa, 6))
    ov = q.get("value") if q else None
    if not v6:
        if ov is not None:
            _cuenta(J, "dato_inventado", h("RXA", 6), "Immunization.doseQuantity.value %r sin RXA-6" % ov)
    elif not CV.NM_RE.match(v6):
        if ov is not None:
            _cuenta(J, "valor_imposible_convertido", h("RXA", 6), "Immunization.doseQuantity desde un NM imposible %r" % v6, clase="valor_imposible_aceptado")
    elif ov is None:
        _cuenta(J, "dato_perdido", h("RXA", 6), "Immunization.doseQuantity.value: falta %r" % v6)
    elif ov not in (v6, CV._nm_canonico(v6)):
        _cuenta(J, "valor_distinto", h("RXA", 6), "Immunization.doseQuantity.value: esperado %r, observado %r (la precisión cuenta: Q-CV-D-10)" % (v6, ov))
    q = q or {}
    rep = (_reps(m, _f(m, rxa, 7)) or [""])[0]
    u1, u2, u3 = _t(m, rep, 1), _t(m, rep, 2), _t(m, rep, 3)
    hecho = h("RXA", 7)
    if not (u1 or u2):
        if q.get("unit") or q.get("code"):
            _cuenta(J, "dato_inventado", hecho, "Immunization.doseQuantity.unit %r sin RXA-7" % q.get("unit"))
        return
    unit = u2 or u1
    if q.get("unit") != unit:
        _cuenta(J, "dato_perdido" if q.get("unit") is None else "valor_distinto", hecho,
                 "Immunization.doseQuantity.unit: esperado %r, observado %r" % (unit, q.get("unit")))
    if u1 and u3:
        if q.get("code") != u1:
            _cuenta(J, "dato_perdido" if q.get("code") is None else "valor_distinto", hecho,
                     "Immunization.doseQuantity.code: esperado %r, observado %r" % (u1, q.get("code")))
        uri = CV.URI_SISTEMA.get(u3.upper())
        if uri and q.get("system") != uri:
            _cuenta(J, "dato_perdido" if q.get("system") is None else "codigo_mal_mapeado", hecho,
                     "Immunization.doseQuantity.system: esperado %r (de %r), observado %r" % (uri, u3, q.get("system")))


def _persona(J, entries, ref, desde):
    """El Practitioner de un actor: directo, contained, o tras PractitionerRole.practitioner (AMB-VX-8). -> (entry, forma, tipo)."""
    x, forma = CV.resolver(entries, ref, desde, None)
    if x is not None and x["tipo"] == "PractitionerRole":
        J.referidas.add(x["i"])
        y, _ = CV.resolver(entries, x["r"].get("practitioner"), x, "Practitioner")
        return y, forma, "PractitionerRole"
    return x, forma, (x["tipo"] if x is not None else None)


def _performers(J, m, orc, rxa, r, e, h):
    """R-VX-3 (S-VX-7): RXA-10 → función AP, ORC-12 → función OP, con actor (Practitioner o PractitionerRole → Practitioner) que
    lleve XCN.1 en identifier o XCN.2 en family. Función ausente: Q-VX-D-6 (si_dos: convención con uno, dato perdido con dos)."""
    obs = [p for p in r.get("performer") or [] if isinstance(p, dict)]
    esperados = [(rep, "AP", h("RXA", 10)) for rep in _reps(m, _f(m, rxa, 10))] + [(rep, "OP", h("ORC", 12)) for rep in _reps(m, _f(m, orc, 12))]
    esperados = [x for x in esperados if _t(m, x[0], 1) or _d(m, _sub(m, _comp(m, x[0], 2), 1))]
    usados = set()
    for rep, fn, hecho in esperados:
        x1, fam, g = _t(m, rep, 1), _d(m, _sub(m, _comp(m, rep, 2), 1)), _t(m, rep, 3)
        mejor, rota, solo_display, otra = None, False, None, None
        for k, p in enumerate(obs):
            if k in usados:
                continue
            act = p.get("actor") if isinstance(p.get("actor"), dict) else {}
            pr, forma, tipo = _persona(J, J.entries, act, e)
            funcs = {c[1] for c in _codigos(p.get("function"))}
            if pr is not None and tipo in ("Practitioner", "PractitionerRole") and pr["tipo"] == "Practitioner":
                ids, nom = _valores(pr["r"]), ((pr["r"].get("name") or [{}])[0] if pr["r"].get("name") else {})
                if (x1 and x1 in ids) or (fam and nom.get("family") == fam):
                    if mejor is None or fn in funcs:
                        mejor = (k, pr, funcs, nom)
            elif pr is not None:
                if fn in funcs or otra is None:
                    otra = k
            elif forma == "logica" and x1 and (act.get("identifier") or {}).get("value") == x1:
                if mejor is None or fn in funcs:
                    mejor = (k, None, funcs, {})
            elif forma == "rota" and fn in funcs:
                rota = True
            elif forma == "display" and ((fam and fam in (act.get("display") or "")) or (x1 and x1 in (act.get("display") or ""))):
                solo_display = k
        if mejor is None:
            if solo_display is not None:
                usados.add(solo_display)
                if x1:
                    _cuenta(J, "dato_perdido", hecho, "Immunization.performer %s: solo display, falta el identificador %r" % (fn, x1))
                else:
                    _nota(J, "convencion", hecho, "Immunization.performer %s: solo display" % fn)
            elif rota:
                _cuenta(J, "referencia_rota", hecho, "Immunization.performer %s: actor no resuelve" % fn, citas=_cit(hecho) + CV.C["ref"])
            elif otra is not None:
                usados.add(otra)
                _cuenta(J, "dato_perdido", hecho, "Immunization.performer %s: el actor no es una persona (XCN es un profesional)" % fn)
            else:
                _cuenta(J, "dato_perdido", hecho, "Immunization.performer %s: falta %r" % (fn, rep))
            continue
        k, pr, funcs, nom = mejor
        usados.add(k)
        if pr is not None:
            J.referidas.add(pr["i"])
        if not funcs:
            if _dec(J, "Q-VX-D-6") == "si_dos" and len(esperados) == 1:
                _nota(J, "convencion", hecho, "Immunization.performer sin function con un solo profesional (Q-VX-D-6)")
            elif _dec(J, "Q-VX-D-6") == "convencion":
                _nota(J, "convencion", hecho, "Immunization.performer sin function (Q-VX-D-6)")
            else:
                _cuenta(J, "dato_perdido", hecho, "Immunization.performer %r: falta function %s (Q-VX-D-6)" % (x1 or fam, fn))
        elif fn not in funcs:
            _cuenta(J, "codigo_mal_mapeado", hecho, "Immunization.performer %r: function esperada %s, observada %r" % (x1 or fam, fn, sorted(funcs)))
        if pr is not None:
            if fam and nom.get("family") != fam:
                _cuenta(J, "valor_distinto", hecho, "Practitioner.name.family: esperado %r, observado %r" % (fam, nom.get("family")))
            if g and (nom.get("given") or [None])[0] != g:
                _cuenta(J, "valor_distinto", hecho, "Practitioner.name.given: esperado %r, observado %r" % (g, nom.get("given")))
    if len(obs) > len(usados):
        _nota(J, "extra", h("RXA", 10), "Immunization.performer de más: %d" % (len(obs) - len(usados)))


def _motivos(J, m, rxa, r, h):
    """RXA-19 → reasonCode[], un CodeableConcept por repetición con CE.1; multiconjunto por code; system: convención."""
    hecho = h("RXA", 19)
    esperados = [c for c in (_t(m, x, 1) for x in _reps(m, _f(m, rxa, 19))) if c]
    obs = [x for x in r.get("reasonCode") or [] if isinstance(x, dict)]
    libres = list(range(len(obs)))
    for c in esperados:
        k = next((k for k in libres if c in {x[1] for x in _codigos(obs[k])}), None)
        if k is None:
            if libres:
                _cuenta(J, "valor_distinto", hecho, "Immunization.reasonCode: falta %r (observado %r)" % (c, [_codigos(obs[k]) for k in libres]))
                libres.pop(0)
            else:
                _cuenta(J, "dato_perdido", hecho, "Immunization.reasonCode: falta %r" % c)
            continue
        libres.remove(k)
    if libres:
        _nota(J, "extra", hecho, "Immunization.reasonCode de más: %d" % len(libres))


def _identificadores(J, m, orc, r, h):
    """ORC-2.1 → identifier con type PLAC, ORC-3.1 → FILL (como _informe de oru_conv); los demás identifiers, nota."""
    ids = [x for x in r.get("identifier") or [] if isinstance(x, dict)]
    usados = set()
    for n, tipo in ((2, "PLAC"), (3, "FILL")):
        v = _t(m, _f(m, orc, n), 1)
        if not v:
            continue
        con = [k for k, x in enumerate(ids) if x.get("value") == v]
        if not con:
            _cuenta(J, "dato_perdido", h("ORC", n), "Immunization.identifier: falta %r (%s)" % (v, tipo))
            continue
        usados |= set(con)
        if not any(tipo in {c[1] for c in _codigos(ids[k].get("type"))} for k in con):
            _cuenta(J, "codigo_mal_mapeado", h("ORC", n), "Immunization.identifier %r: type esperado %s, observado %r" %
                     (v, tipo, [c[1] for k in con for c in _codigos(ids[k].get("type"))]))
    extra = [x.get("value") for k, x in enumerate(ids) if k not in usados]
    if extra:
        _nota(J, "extra", h("ORC", 3), "Immunization.identifier de más: %r (ORC-4 es nota, AMB-VX-1)" % extra)


# ---------------------------------------------------------------------------- NK1 → RelatedPerson / Patient.contact (§3.3)
def _parientes(J, m, lec, pat_entry, roles):
    """S-VX-11 (Q-VX-D-5): perfil reducido; una de las dos formas, las dos a la vez es nota (AMB-VX-6)."""
    nk1s = m.segmentos("NK1")
    if not nk1s:
        return
    if _dec(J, "Q-VX-D-5") == "ninguno":
        _nota(J, "fuera_proyeccion", "NK1", "NK1 fuera del perfil (alternativa de Q-VX-D-5)")
        return
    cs = [c for c in (pat_entry["r"].get("contact") or []) if isinstance(c, dict)] if pat_entry else []
    for k, nk1 in enumerate(nk1s, 1):
        if not (_f(m, nk1, 2) or _f(m, nk1, 3)) or "RelatedPerson#%d" % k in lec["ambiguo"]:
            continue
        h = lambda n: _hecho("NK1", k, n)  # noqa: E731
        x = roles.get("RelatedPerson#%d" % k)
        e = x["entry"] if x else None
        ci = lec.get("contactos_vx", {}).get(k)
        if e is None and ci is None:
            _cuenta(J, "recurso_ausente", h(2), "falta el RelatedPerson (o el Patient.contact) del NK1 %d" % k, citas=C_VXU["NK1"])
            continue
        if e is not None and ci is not None:
            _nota(J, "ambos", h(2), "NK1 %d como RelatedPerson y como Patient.contact (AMB-VX-6)" % k)
        if e is not None:
            CV._sujeto(J, m, {"subject": e["r"].get("patient")}, e, pat_entry, "RelatedPerson.patient", "PID-3")
            _pariente(J, m, nk1, e["r"], h, "RelatedPerson", [y for y in e["r"].get("name") or [] if isinstance(y, dict)])
        else:
            c = cs[ci]
            _pariente(J, m, nk1, c, h, "Patient.contact", [c["name"]] if isinstance(c.get("name"), dict) else [])
    if lec.get("contactos_vx_libres"):
        _nota(J, "extra", "NK1", "Patient.contact sin NK1: %d" % len(lec["contactos_vx_libres"]))


def _pariente(J, m, nk1, r, h, ruta, nombres):
    rep = (_reps(m, _f(m, nk1, 2)) or [""])[0]
    fam, g1, g2, uso = _familia_nk1(m, nk1), _t(m, rep, 2), _t(m, rep, 3), _t(m, rep, 7)
    if fam or g1:
        x = next((y for y in nombres if y.get("family") == fam), nombres[0] if nombres else None)
        if x is None:
            _cuenta(J, "dato_perdido", h(2), "%s.name: falta %r" % (ruta, rep))
        else:
            if fam and x.get("family") != fam:
                _cuenta(J, "valor_distinto", h(2), "%s.name.family: esperado %r, observado %r" % (ruta, fam, x.get("family")))
            dados = [y for y in [g1] if y] + [y for y in g2.split() if y]
            if (g1 or g2) and list(x.get("given") or []) not in ([y for y in [g1, g2] if y], dados):
                _cuenta(J, "valor_distinto", h(2), "%s.name.given: esperado %r, observado %r" % (ruta, dados, x.get("given")))
            CV._uso(J, h(2), uso, x.get("use"), "0200", "%s.name.use" % ruta)
    rel = [y for y in r.get("relationship") or [] if isinstance(y, dict)]
    _tabla(J, h(3), _t(m, _f(m, nk1, 3), 1), rel, "0063", "%s.relationship" % ruta, varios=True)
    if _t(m, _f(m, nk1, 7), 1):
        _tabla(J, h(7), _t(m, _f(m, nk1, 7), 1), rel, "0131", "%s.relationship" % ruta, varios=True)
    _telefonos(J, m, nk1, r, h, ruta)
    _genero(J, m, _d(m, _f(m, nk1, 15)), r.get("gender"), h(15), ruta)
    v16 = _t(m, _f(m, nk1, 16), 1)
    if ruta == "RelatedPerson":
        CV._fecha(J, h(16), v16, r.get("birthDate"), "date", "RelatedPerson.birthDate")
    elif v16:
        _nota(J, "convencion", h(16), "Patient.contact no tiene birthDate: NK1-16 solo va a RelatedPerson (S-VX-11)")


def _genero(J, m, v, obs, hecho, ruta):
    if not v:
        if obs is not None:
            _cuenta(J, "dato_inventado", hecho, "%s.gender %r sin NK1-15" % (ruta, obs))
        return
    t = CV.mapa("0001", v)
    if t == FUERA:
        if obs is not None:
            _cuenta(J, "valor_imposible_convertido", hecho, "%s.gender %r desde %r, fuera de la 0001" % (ruta, obs, v),
                     clase="valor_imposible_aceptado", tabla=True)
        return
    if obs is None:
        _cuenta(J, "dato_perdido", hecho, "%s.gender: falta %r (de %r)" % (ruta, t[1], v))
    elif obs not in CV.GENERO_FHIR:
        _cuenta(J, "fhir_invalido", hecho, "%s.gender %r fuera de administrative-gender (required)" % (ruta, obs))
    elif obs != t[1]:
        _cuenta(J, "valor_distinto", hecho, "%s.gender: esperado %r, observado %r" % (ruta, t[1], obs))


def _textos_tel(x):
    """DV-VX-9: el value y, con solo XTN.7, la extensión contactpoint-local ([CM datatype-xtn-to-contactpoint] extension[3])."""
    return [x.get("value") or ""] + [e.get("valueString") or "" for e in x.get("extension") or []
                                     if isinstance(e, dict) and str(e.get("url", "")).endswith("contactpoint-local")]


def _telefonos(J, m, nk1, r, h, ruta):
    """NK1-5 (use home por omisión) y NK1-6 (use work): las reglas de PID-13/14 de CV._telecom."""
    obs = [x for x in r.get("telecom") or [] if isinstance(x, dict)]
    usados = set()
    for n, por_omision in ((5, "home"), (6, "work")):
        for rep in _reps(m, _f(m, nk1, n)):
            c1, uso, eq, correo, pais, area, local, sin = (_t(m, rep, k) for k in (1, 2, 3, 4, 5, 6, 7, 12))
            if eq in ("Internet", "X.400") or (not eq and correo and not (sin or c1 or local)):
                valor, contiene = correo, []
            elif sin:
                valor, contiene = sin, []
            elif c1 and not local:
                valor, contiene = c1, []
            elif local:
                valor, contiene = None, [x for x in (pais, area, local) if x]
            else:
                continue
            libres = [k for k in range(len(obs)) if k not in usados]
            k = next((k for k in libres if (valor and valor in _textos_tel(obs[k])) or
                      (contiene and any(all(c in s for c in contiene) for s in _textos_tel(obs[k])))), None)
            if k is None:
                _cuenta(J, "dato_perdido", h(n), "%s.telecom: falta %r" % (ruta, valor or contiene))
                continue
            usados.add(k)
            x = obs[k]
            ts = CV.mapa("0202", eq) if eq else None
            sis = ts[1] if isinstance(ts, tuple) and not ts[0].endswith("contact-point-use") else None
            if sis and x.get("system") != sis:
                _cuenta(J, "codigo_mal_mapeado" if x.get("system") else "dato_perdido", h(n),
                         "%s.telecom %r system: esperado %r, observado %r" % (ruta, x.get("value"), sis, x.get("system")))
            tu = CV.mapa("0201", uso) if uso else None
            uso_esp = (tu[1] if isinstance(tu, tuple) else None) if uso else por_omision
            if uso_esp and x.get("use") != uso_esp:
                _cuenta(J, "codigo_mal_mapeado" if x.get("use") else "dato_perdido", h(n),
                         "%s.telecom %r use: esperado %r, observado %r" % (ruta, x.get("value"), uso_esp, x.get("use")))
    if len(obs) > len(usados):
        _nota(J, "extra", h(5), "%s.telecom de más: %d" % (ruta, len(obs) - len(usados)))


# ---------------------------------------------------------------------------- el perfil como datos (consultar_tabla, §3)
def _fila(elemento, campo, regla, nivel, clave):
    return {"elemento": elemento, "campo": campo, "regla": regla, "nivel": nivel, "citas": list(C_VXU.get(clave) or C_SEG.get(clave) or [])}


PERFIL_GUIA_VXU = [
    _fila("Immunization (existencia)", "ORC/RXA", "una por grupo ORDER; emparejada por ORC-3.1/ORC-2.1, RXA-5 y RXA-3, código único u orden", "cuenta", "RXA"),
    _fila("Immunization.status", "RXA-20/RXA-21", "RXA-21 D → entered-in-error; si no, RXA-20 por la 0322 (CP/PA → completed, RE/NA → not-done); vacío → completed (R-VX-1)", "cuenta", "RXA-20"),
    _fila("Immunization.statusReason", "RXA-18", "primera repetición: CE.1 en coding.code; system: convención", "cuenta", "RXA-18"),
    _fila("Immunization.vaccineCode", "RXA-5", "CE.1 y CE.4 en algún coding; CVX → http://hl7.org/fhir/sid/cvx (Q-VX-D-1); CE.9 → text", "cuenta", "RXA-5"),
    _fila("Immunization.patient", "PID-3", "resuelve al Patient del PID (lógica por identifier: convención)", "cuenta", "PID"),
    _fila("Immunization.encounter", "PV1-19", "con PV1 y Encounter: ausente es convención (Q-VX-D-9), presente debe resolver; sin PV1, presente es dato inventado", "convencion", "PV1"),
    _fila("Immunization.occurrence[x]", "RXA-3", "occurrenceDateTime con la precisión del origen (R-CV-7); occurrenceString o RXA-4 → valor distinto", "cuenta", "RXA-3"),
    _fila("Immunization.recorded", "ORC-9/RXA-22", "manda RXA-22 si RXA-21 = A; si no, ORC-9 (Q-VX-D-3; alternativa: cualquiera de los dos)", "cuenta", "RXA-22"),
    _fila("Immunization.primarySource, isSubpotent", "—", "sin fila: deducidos de RXA-9 (primarySource) o de RXA-20 PA (isSubpotent), "
         "convención (DV-VX-8); escritos sin campo que los sostenga, dato inventado (Q-VX-D-7)", "cuenta", "RXA"),
    _fila("Immunization.reportOrigin", "RXA-9", "con RXA-9: convención (AMB-VX-9); sin RXA-9: dato inventado", "convencion", "RXA-9"),
    _fila("Immunization.location", "RXA-11", "nunca cuenta (L-VX-1)", "nota", "RXA-11"),
    _fila("Immunization.manufacturer", "RXA-17", "Organization con identifier ∋ CE.1 (system MVX, Q-VX-D-1) y name = CE.2 desescapado; solo display con CE.1 → dato perdido", "cuenta", "RXA-17"),
    _fila("Immunization.lotNumber", "RXA-15", "primera repetición, texto exacto; otra repetición: convención (Q-VX-D-8)", "cuenta", "RXA-15"),
    _fila("Immunization.expirationDate", "RXA-16", "date con la precisión del origen; un día añadido a YYYYMM es dato inventado", "cuenta", "RXA-16"),
    _fila("Immunization.site", "RXR-2", "{v2-0163, código} o {v2-0550, código} según la tabla donde esté (Q-VX-D-2); fuera de ambas: convención", "cuenta", "RXR-2"),
    _fila("Immunization.route", "RXR-1", "por la 0162: ID/IM/IV/PO/SC/TD → v3-RouteOfAdministration, el resto identidad v2-0162", "cuenta", "RXR-1"),
    _fila("Immunization.doseQuantity", "RXA-6/RXA-7", "value texto decimal (.5 ≡ 0.5, 0.50 ≠ 0.5); unit CE.2 o CE.1; code CE.1 y system UCUM si ambos", "cuenta", "RXA-6"),
    _fila("Immunization.performer[]", "RXA-10/ORC-12", "RXA-10 → AP, ORC-12 → OP (v2-0443); actor Practitioner o PractitionerRole → Practitioner; función ausente: Q-VX-D-6", "cuenta", "RXA-10"),
    _fila("Immunization.reasonCode[]", "RXA-19", "un CodeableConcept por repetición con CE.1; multiconjunto por code", "cuenta", "RXA-19"),
    _fila("Immunization.identifier[]", "ORC-2/ORC-3", "ORC-2.1 con type PLAC, ORC-3.1 con type FILL; los demás: nota", "cuenta", "ORC-3"),
    _fila("Immunization.fundingSource, note, protocolApplied, education, programEligibility, reaction…", "—", "sin fila: repetibles nota; fundingSource sin OBX que lo sostenga, dato inventado", "nota", "RXA"),
    _fila("Observation (existencia)", "OBX", "una por OBX del grupo ORDER; absorbido en la Immunization: recurso ausente (Q-VX-D-4; alternativa: convención)", "cuenta", "OBX"),
    _fila("Observation.partOf[]", "OBX-3", "resuelve a la Immunization de su grupo; las demás reglas, las de oru_conv (Q-VX-D-10)", "cuenta", "OBX"),
    _fila("RelatedPerson / Patient.contact", "NK1", "uno por NK1 en una de las dos formas (AMB-VX-6); nombre, relación (0063, 0131), teléfonos, sexo; birthDate solo en RelatedPerson", "cuenta", "NK1"),
    _fila("Encounter", "PV1", "opcional (S-VX-10): ausente es convención; presente, las reglas de adt_conv", "convencion", "PV1"),
    _fila("PD1", "PD1", "fuera del perfil (L-VX-3)", "nota", "PD1"),
    {"elemento": "id, meta, text, extensiones, display, Bundle.type, orden de listas", "campo": "—", "regla": "forma (L-CV-4, L-CV-9)", "nivel": "forma",
     "citas": ["[L-CV-4]", "[L-CV-9]"]},
]

S_VX = {"S-VX-1": "Un punto de entrada nuevo, vxu_conv (familia vxu, solo transformación), hermano de adt_conv y oru_conv; nada de lo que leen esos dos cambia.",
        "S-VX-2": "La misma evidencia {mensaje, punto_entrada, conversion} de S-CV-2.",
        "S-VX-3": "Una Immunization por grupo ORDER (ORC + RXA [+RXR] [+OBX]), emparejada por ORC-3.1/ORC-2.1, luego por RXA-5 y RXA-3, luego por orden.",
        "S-VX-4": "Las mismas ocho clases, categorías y leyenda de adt_conv/oru_conv.",
        "S-VX-5": "Immunization.status por RXA-21 y RXA-20: D → entered-in-error; si no, RXA-20 por la 0322; vacío → completed.",
        "S-VX-6": "Ruta por la 0162 en sus dos grupos; sitio por la 0163 o la 0550.",
        "S-VX-7": "RXA-10 → performer con función AP; ORC-12 → performer con función OP.",
        "S-VX-8": "recorded: manda RXA-22 cuando RXA-21 es A; si no, ORC-9 (Q-VX-D-3).",
        "S-VX-9": "Los OBX del grupo ORDER se juzgan como Observation con las reglas de oru_conv, más subject → Patient y partOf → la Immunization de su grupo.",
        "S-VX-10": "El PV1 es opcional en el Bundle; si hay Encounter, se juzga con las reglas de adt_conv.",
        "S-VX-11": "NK1 entra con un perfil reducido (RelatedPerson o Patient.contact); PD1 queda fuera.",
        "S-VX-12": "El corpus son 40 bases sintéticas válidas en v2.5 (bases_vxu.py).",
        "S-VX-13": "La herramienta decide vxu_conv por MSH-9.1 = VXU; ADT y ORU quedan igual.",
        "S-VX-14": "La versión manda como en S-CV-6: con MSH-12 ≠ 2.5 los ConceptMap cuentan y la legalidad de tabla/estructura de 2.5 no (L18)."}
L_VX = {"L-VX-1": "En v2.5 el lugar de administración es RXA-11 y la guía no lo mapea: Immunization.location nunca cuenta (con RXA-11, nota fuera_proyeccion; sin él, nota extra).",
        "L-VX-2": "ORC-28 → meta.security no se juzga: meta es forma (L-CV-9).",
        "L-VX-3": "PD1 queda fuera del perfil (nota).",
        "L-VX-4": "La pertenencia de RXA-5 al CVX y de RXA-17 al MVX no se juzga; sus uris se fijan por Q-VX-D-1, con cita externa a R4.",
        "L-VX-5": "TQ1/TQ2 no tienen fila y PRT no existe en 2.5: el juez no deduce performers de otros segmentos.",
        "L-VX-6": "Un OBX absorbido en la Immunization solo se comprueba por la presencia de su valor.",
        "L-VX-7": "NTE bajo OBX: solo presencia (nota).",
        "L-VX-8": "El Encounter de un VXU es opcional; su status se decide solo por PV1-2/PV1-45 (V04 no está en la 0003).",
        "L-VX-9": "Las reglas de la guía de los CDC no entran: los VXU 2.5.1 se juzgan contra la guía base con banderas L18.",
        "L-VX-10": "GT1, IN1-3, SFT, PV2 y los OBX fuera de ORDER solo se cuentan.",
        "L-VX-11": "NK1 se empareja por identificador o apellido: dos NK1 con el mismo apellido y sin identificador dan indeterminado/emparejamiento.",
        "L-VX-12": "RXA-15/16/17/18 repiten en 2.5 y van a elementos 0..1: se juzga la primera repetición (Q-VX-D-8).",
        "L-VX-13": "Un error del conversor por falta de plantilla de VXU es sin_plantilla en la herramienta (L-VC-13), no rechazo_incorrecto.",
        "L-VX-14": "Dos grupos ORDER iguales en ORC-3, RXA-3 y RXA-5 no se distinguen: indeterminado/emparejamiento (VX2-c: dos muestras de "
                   "pruebas de LinuxForHealth que comprueban justo eso)."}
AMB_VX = {"AMB-VX-1": "ORC-4 (EI en 2.5, EIP en la guía): nota; un identifier con ORC-4.1 es convención.",
          "AMB-VX-2": "RXR-2: la 0550 (mapa) o la 0163 (tabla de atributos): el system de la tabla donde esté el código (Q-VX-D-2; alternativa: solo la 0550).",
          "AMB-VX-3": "ORC-9 y RXA-22 (IF A) → recorded: manda RXA-22 con A (Q-VX-D-3; alternativa: cualquiera de los dos).",
          "AMB-VX-4": "OBX de ORDER absorbido en la Immunization: recurso ausente (Q-VX-D-4; alternativa: convención).",
          "AMB-VX-5": "Immunization.encounter ausente con PV1 y Encounter: convención (Q-VX-D-9; alternativa: dato perdido).",
          "AMB-VX-6": "NK1 → RelatedPerson o Patient.contact: una de las dos formas; las dos, nota.",
          "AMB-VX-7": "RXA-15 repetido: la primera repetición, y otra es convención (Q-VX-D-8; alternativa: la primera, literal).",
          "AMB-VX-8": "El tipo del actor (PractitionerRole o Practitioner) es forma; se recorre PractitionerRole.practitioner.",
          "AMB-VX-9": "reportOrigin y primarySource con RXA-9: convención; sin RXA-9: dato inventado (Q-VX-D-7). isSubpotent con RXA-20 PA: "
                      "convención (R4 Immunization.isSubpotent; DV-VX-8).",
          "AMB-VX-10": "El apellido de ORC-12 se juzga por el mapa XCN → Practitioner.",
          "AMB-VX-11": "RXA-20 y RXA-21 vacíos: completed.",
          "AMB-VX-12": "RXA sin ORC delante: el grupo existe y se espera su Immunization; nota estructura.",
          "AMB-VX-13": "La condición de ORDER.OBSERVATION.OBX → Observation[2] (message-vxu-v04-to-bundle) dice «LST.count LESS THAN OR "
                       "EQUALS 1 AND OBX-2 IS NA»; se lee como el «OR» de PERSON_OBSERVATION (MSG_VXU_V04.csv:34): todo OBX del grupo da "
                       "su Observation. Alternativa literal: un OBX de un solo valor no la da, y su ausencia no cuenta."}
INFO = {"guia": CV.GUIA, "decisiones": S_VX, "decisiones_jev": DECISIONES_VX, "alternativas_sensibilidad": ALTERNATIVA_VX, "limites": L_VX,
        "ambiguedades": AMB_VX, "puntos_entrada": ["vxu_conv"], "diseno": "vx/diseno-vx-fable.md", "decisiones_doc": "vx/decisiones-qvx.md",
        "resultado": "RESULTADO-VXU.md"}

CV.C.update({k: v for k, v in C_VXU.items() if k not in CV.C})       # DV-VX-2: solo claves nuevas; las de ADT y ORU no cambian
CV.INFO["vxu"] = INFO


# ---------------------------------------------------------------------------- autoprueba
def autoprueba():
    ok = True
    if os.path.isdir(CV.PAQUETE):
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "cv"))
        import extraer_mapas as X
        for n in MAPAS_VXU:
            if X.mapa(CV.PAQUETE, n) != MAPAS_VXU[n]:
                print("  MAL el mapa %s no es el del paquete" % n)
                ok = False
        print("mapas de VXU contra el paquete: %s (%d)" % ("IGUALES" if ok else "DISTINTOS", len(MAPAS_VXU)))
    else:
        print("mapas de VXU: el paquete de la guía no está aquí; no se comparan")
    choques = [k for k in C_VXU if k in CV.C and CV.C[k] != C_VXU[k] and k not in C_SEG]
    if choques:
        print("  MAL claves de cita de VXU que ya eran de ADT u ORU: %r" % choques)
        ok = False
    print("AUTOPRUEBA DE conversion_vxu: %s" % ("TODO BIEN" if ok else "MAL"))
    return 0 if ok else 1


if __name__ == "__main__":
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
