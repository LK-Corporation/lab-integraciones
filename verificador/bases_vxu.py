#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Las 40 bases VXU^V04 sintéticas de vx/diseno-vx-fable.md §4 (etapa 20): registros de vacunación VÁLIDOS en v2.5, escritos desde
[E4 CH04.txt:12366-12421] (estructura), §4.14.7 y §4.18 (RXA en vacunas), §4.14.2 (RXR) y §4.5.1 (ORC). Cada base ejercita una rama
de la guía (§4.2), no un fallo supuesto de nadie; los imposibles van a las pruebas P-VX, no aquí. Pacientes ficticios, apellidos de una
lista cerrada. Deterministas.

Escribe bases_vxu/BNN.hl7 (segmentos separados por CR, sin MLLP) y bases_vxu.jsonl (id, descripcion, ejercita, campos, fichero, msh10,
segmentos). Aquí NO se escribe ningún Bundle ni canónico esperado: la previsión se sella aparte (§5).

Uso: python3 bases_vxu.py               escribe los ficheros
     python3 bases_vxu.py --lista       id y descripción
     python3 bases_vxu.py --firma       pares de bases con menos de 3 campos distintos (R-VX-7)
     python3 bases_vxu.py --cobertura   filas «cuenta» del perfil sin base valorada o vacía
     python3 bases_vxu.py --autoprueba  lectura, estructura, tipos y tablas, firma, cobertura y huella del conjunto"""
import datetime
import hashlib
import itertools
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CARPETA = os.path.join(AQUI, "bases_vxu")
INDICE = os.path.join(AQUI, "bases_vxu.jsonl")
HUELLA = "5734cc3b9d6df918bb94b19393d199cdb5af09f80ecd8e949f29f50f068d0605"   # sha256 de los 40 cables en orden (VX2a, 25-oct)
APELLIDOS = {"Prueba", "Sintetico", "Ficticia", "Ejemplo", "Modelo", "Simulado", "Ensayo", "Muestra", "Patron", "Plantilla"}
NO_FIRMA = {"MSH-7", "MSH-10"}                                        # metadatos del envío: no cuentan para la firma


def fecha(n, hora=True):
    """Fechas repartidas por 2023-2024, una por base: 9-ene-2023 + 17·n días; 10:mm con mm = n."""
    d = datetime.date(2023, 1, 9) + datetime.timedelta(days=17 * n)
    return d.strftime("%Y%m%d") + ("10%02d00" % n if hora else "")


def caducidad(n, dia=False):
    d = datetime.date(2025, 1, 1) + datetime.timedelta(days=23 * n)
    return d.strftime("%Y%m%d") if dia else d.strftime("%Y%m")


def msh(n, ver="2.5", est="VXU_V04", msh18=""):
    return "MSH|^~\\&|REGVAC|CSSYN|REGISTRO|SALUD|%s||VXU^V04%s|VXU-B%02d|P|%s%s" % (
        fecha(n)[:8] + "1100", "^" + est if est else "", n, ver, "||||||" + msh18 if msh18 else "")


PIDS = {
    "mateo": "PID|1||VAC0001^^^CSSYN^MR||Prueba^Mateo^^^^^L||20230512|M",
    "lucia": "PID|1||VAC0002^^^CSSYN^MR~SYNV0002^^^CSSYN^PI||Sintetico^Lucia^^^^^L||20210304|F",
    "carmen": "PID|1||VAC0003^^^CSSYN^MR||Ficticia^Carmen^Rosa^^^^L||19580917|F",
    "pablo": "PID|1||VAC0004^^^CSSYN^MR~SYNV0004^^^CSSYN^PI||Ejemplo^Pablo^^^^^L||20190811|M",
    "elena": "PID|1||VAC0005^^^CSSYN^MR||Modelo^Elena^^^^^L||19900122|F",
    "begona": "PID|1||VAC0006^^^CSSYN^MR||Simulado^Begona^^^^^L||20220707|F",          # en B39, «Begoña» con MSH-18 UTF-8
}
PROF = {1: "PR01^Ensayo^Ana", 2: "PR02^Muestra^Jorge", 3: "PR03^Patron^Irene", 4: "PR04^Plantilla^Raul"}
CVX = {"03": "03^MMR^CVX", "08": "08^Hep B pediatrica^CVX", "10": "10^IPV^CVX", "20": "20^DTaP^CVX", "21": "21^Varicela^CVX",
       "33": "33^Neumococica polisacarida^CVX", "48": "48^Hib PRP-T^CVX", "02": "02^OPV^CVX", "19": "19^BCG^CVX", "09": "09^Td adulto^CVX",
       "52": "52^Hep A adulto^CVX", "88": "88^Gripe sin especificar^CVX"}
MVX = {"MSD": "MSD^Merck \\T\\ Co., Inc.^MVX", "SKB": "SKB^GlaxoSmithKline^MVX", "PMC": "PMC^sanofi pasteur^MVX",
       "WAL": "WAL^Wyeth^MVX", "NOV": "NOV^Novartis^MVX", "OTH": "OTH^Otro fabricante^MVX"}
RUTA = {"IM": "IM^Intramuscular^HL70162", "SC": "SC^Subcutanea^HL70162", "PO": "PO^Oral^HL70162", "ID": "ID^Intradermica^HL70162"}
SITIO = {"LD": "LD^Deltoides izquierdo^HL70163", "RA": "RA^Brazo derecho^HL70163", "LT": "LT^Muslo izquierdo^HL70163",
         "RVL": "RVL^Vasto lateral derecho^HL70163", "LUA": "LUA^Brazo superior izquierdo^HL70163", "RD": "RD^Deltoides derecho^HL70163"}


def seg(nombre, campos):
    """Un segmento desde {número de campo: valor} (como prueba_conversion.seg, sin MSH)."""
    p = [nombre] + [""] * (max(campos) if campos else 0)
    for k, v in campos.items():
        p[k] = v
    return "|".join(p).rstrip("|") if campos else nombre


def orc(n, placer="", filler=None, orc9="", orc12="", orc4="", orc28=""):
    return seg("ORC", {1: "RE", 2: placer, 3: "VX-%02d^REGVAC" % n if filler is None else filler, 4: orc4, 9: orc9, 12: orc12, 28: orc28})


def rxa(n, cvx, dosis="0.5", unidad="mL^^UCUM", prov=1, lote=None, cad=None, mvx="MSD", rech="", ind="", c20="CP", c21="A", c22="",
        f3=None, f4=None):
    f3 = fecha(n) if f3 is None else f3
    return seg("RXA", {1: "0", 2: "1", 3: f3, 4: f3 if f4 is None else f4, 5: CVX.get(cvx, cvx), 6: dosis, 7: unidad,
                       10: PROF.get(prov, prov) if prov else "", 15: "LOT-B%02d" % n if lote is None else lote,
                       16: caducidad(n) if cad is None else cad, 17: MVX.get(mvx, mvx) if mvx else "", 18: rech, 19: ind,
                       20: c20, 21: c21, 22: c22})


def rxr(ruta, sitio=None):
    return seg("RXR", {1: RUTA.get(ruta, ruta), 2: SITIO.get(sitio, sitio) if sitio else ""})


def obx(j, tipo, cod, val, uni="", st="F", t14=""):
    return seg("OBX", {1: str(j), 2: tipo, 3: cod, 5: val, 6: uni, 11: st, 14: t14})


def nk1(k, nombre, rel, tel="", dir_="", tel_trabajo="", rol="", sexo="", nac=""):
    return seg("NK1", {1: str(k), 2: nombre, 3: rel, 4: dir_, 5: tel, 6: tel_trabajo, 7: rol, 15: sexo, 16: nac})


def base(n, descripcion, ejercita, campos, segs):
    return {"id": "B%02d" % n, "descripcion": descripcion, "ejercita": ejercita, "campos": campos, "segmentos": segs}


def construir():
    b = []
    P = PIDS
    b.append(base(1, "Control. MMR, 0.5 mL UCUM, RXA-10 completo, lote, caducidad YYYYMM, MSD con \\T\\, CP, A, RXA-22; IM/LD",
                  ["CP", "IM v3", "LD v2-0163", "\\T\\", "YYYYMM", "AP"], [],
                  [msh(1), P["mateo"], orc(1), rxa(1, "03", prov="PR01^Ensayo^Ana^M^^DRA^^^CSSYN^L", c22=fecha(1)[:10] + "1500"),
                   rxr("IM", "LD")]))
    b.append(base(2, "Control. Varicela SC/RA, mL^mililitro^UCUM, SKB, CP, sin RXA-21 ni RXA-22",
                  ["SC -> SQ", "RA", "unit = CWE.2", "sin recorded"], ["RXA-7"],
                  [msh(2), P["lucia"], orc(2), rxa(2, "21", unidad="mL^mililitro^UCUM", prov=2, mvx="SKB", c21=""), rxr("SC", "RA")]))
    b.append(base(3, "Control. DTaP IM/LT a un lactante; RXA-3 solo fecha; caducidad YYYYMMDD; ORC-2 y ORC-3",
                  ["fecha sin hora", "PLAC+FILL", "LT"], ["RXA-3", "ORC-2"],
                  [msh(3), P["mateo"], orc(3, placer="PL-03^REGVAC"), rxa(3, "20", prov=3, mvx="PMC", f3=fecha(3, hora=False),
                                                                      cad=caducidad(3, dia=True)), rxr("IM", "LT")]))
    b.append(base(4, "Control. IPV IM/RVL; 1 mL^^ISO+; ORC-12 distinto de RXA-10",
                  ["ISO+", "OP y AP"], ["ORC-12", "RXA-7"],
                  [msh(4), P["pablo"], orc(4, orc12=PROF[3]), rxa(4, "10", dosis="1", unidad="mL^^ISO+", prov=4, mvx="SKB"), rxr("IM", "RVL")]))
    b.append(base(5, "Control. OPV oral sin RXR-2; 2 [drp]^gota^UCUM",
                  ["PO v3", "sin site", "UCUM con corchetes"], ["RXR-2", "RXA-7"],
                  [msh(5), P["begona"], orc(5), rxa(5, "02", dosis="2", unidad="[drp]^gota^UCUM", prov=1, mvx="OTH"), rxr("PO")]))
    b.append(base(6, "Control. BCG ID/LUA; PMC", ["ID -> IDINJ", "LUA"], ["RXR-1"],
                  [msh(6), P["mateo"], orc(6), rxa(6, "19", dosis="0.1", prov=2, mvx="PMC"), rxr("ID", "LUA")]))
    b.append(base(7, "Control. Hib IM/RD; RXA-20 y RXA-21 vacíos", ["vacío -> completed"], ["RXA-20", "RXA-21"],
                  [msh(7), P["pablo"], orc(7), rxa(7, "48", prov=3, mvx="SKB", c20="", c21=""), rxr("IM", "RD")]))
    b.append(base(8, "Control. Neumocócica IM/LD adulto; 0.25 mL; RXA-20 PA", ["PA -> completed", "decimal 0.25"], ["RXA-20", "RXA-6"],
                  [msh(8), P["carmen"], orc(8), rxa(8, "33", dosis="0.25", prov=4, mvx="MSD", c20="PA"), rxr("IM", "LD")]))
    b.append(base(9, "Hep A rechazada: RE, RXA-18 REL, dosis 0, sin RXR, sin lote", ["RE -> not-done", "statusReason", "dosis 0"],
                  ["RXA-20", "RXA-18"],
                  [msh(9), P["elena"], orc(9), rxa(9, "52", dosis="0", unidad="", prov=0, lote="", cad="", mvx="", rech="REL^Motivo religioso^L",
                                                  c20="RE")]))
    b.append(base(10, "Td no administrada: NA, RXA-18 CTR, sin RXR", ["NA -> not-done"], ["RXA-20", "RXA-18"],
                  [msh(10), P["carmen"], orc(10), rxa(10, "09", dosis="0", unidad="", prov=0, lote="", cad="", mvx="",
                                                      rech="CTR^Contraindicacion^L", c20="NA")]))
    b.append(base(11, "MMR con RXA-21 D y RXA-20 CP (corrección de registro)", ["D -> entered-in-error"], ["RXA-21"],
                  [msh(11), P["lucia"], orc(11), rxa(11, "03", prov=1, mvx="MSD", c21="D"), rxr("SC", "RA")]))
    b.append(base(12, "DTaP con RXA-21 U, RXA-22 y ORC-9 valorados", ["U no manda RXA-22", "recorded = ORC-9"], ["RXA-21", "ORC-9", "RXA-22"],
                  [msh(12), P["pablo"], orc(12, orc9=fecha(12)[:10] + "2000"), rxa(12, "20", prov=2, mvx="PMC", c21="U",
                                                                                  c22=fecha(12)[:10] + "4500"), rxr("IM", "LT")]))
    b.append(base(13, "Varicela con RXA-21 A, RXA-22 y ORC-9 distintos", ["recorded con ORC-9 y RXA-22"], ["ORC-9", "RXA-22"],
                  [msh(13), P["begona"], orc(13, orc9=fecha(13)[:10] + "2000"), rxa(13, "21", prov=3, mvx="MSD",
                                                                                   c22=fecha(13)[:10] + "4500"), rxr("SC", "LUA")]))
    b.append(base(14, "Hep B con RXA-3 con zona y RXA-4 posterior", ["zona por instante", "RXA-4 no es occurrence"], ["RXA-3", "RXA-4"],
                  [msh(14), P["mateo"], orc(14), rxa(14, "08", prov=4, mvx="SKB", f3=fecha(14) + "+0200", f4=fecha(14)[:8] + "1130+0200"),
                   rxr("IM", "LT")]))
    b.append(base(15, "IPV con RXA-3 de minutos sin zona", ["precisión de minutos"], ["RXA-3"],
                  [msh(15), P["begona"], orc(15), rxa(15, "10", prov=1, mvx="PMC", f3=fecha(15)[:12]), rxr("IM", "RVL")]))
    b.append(base(16, "Gripe con RXA-15 repetido y caducidad YYYYMMDD", ["primera repetición del lote", "date completo"], ["RXA-15", "RXA-16"],
                  [msh(16), P["elena"], orc(16), rxa(16, "88", prov=2, mvx="WAL", lote="LOT-B16~DIL-B16", cad=caducidad(16, dia=True)),
                   rxr("IM", "LD")]))
    b.append(base(17, "Neumocócica con RXA-17 solo texto", ["manufacturer sin identifier"], ["RXA-17"],
                  [msh(17), P["carmen"], orc(17), rxa(17, "33", prov=3, mvx="^Laboratorio Sintetico^"), rxr("IM", "RD")]))
    b.append(base(18, "MMR con RXA-17 con código alterno", ["CWE.4-6 de RXA-17"], ["RXA-17"],
                  [msh(18), P["lucia"], orc(18), rxa(18, "03", prov=4, mvx="MSD^Merck^MVX^MERCK^Merck S.A.^L"), rxr("SC", "RA")]))
    b.append(base(19, "MMR con RXA-5 con código alterno local", ["CE.4-6 -> coding[2]"], ["RXA-5"],
                  [msh(19), P["pablo"], orc(19), rxa(19, "03^MMR^CVX^TV^Triple virica^L", prov=1, mvx="MSD"), rxr("SC", "LUA")]))
    b.append(base(20, "DTaP con RXA-5.3 = HL70292", ["system convención"], ["RXA-5"],
                  [msh(20), P["mateo"], orc(20), rxa(20, "20^DTaP^HL70292", prov=2, mvx="PMC"), rxr("IM", "LT")]))
    b.append(base(21, "Hib con dos RXA-10", ["performer AP x2"], ["RXA-10"],
                  [msh(21), P["begona"], orc(21), rxa(21, "48", prov=PROF[1] + "~" + PROF[2], mvx="SKB"), rxr("IM", "RVL")]))
    b.append(base(22, "Td con RXA-10 sin XCN.1", ["actor solo display"], ["RXA-10"],
                  [msh(22), P["carmen"], orc(22), rxa(22, "09", prov="^Patron^Irene", mvx="SKB"), rxr("IM", "LD")]))
    b.append(base(23, "Gripe con solo ORC-12", ["un performer OP"], ["ORC-12", "RXA-10"],
                  [msh(23), P["elena"], orc(23, orc12=PROF[4]), rxa(23, "88", prov=0, mvx="NOV"), rxr("IM", "RD")]))
    b.append(base(24, "Hep B con ORC-2/ORC-3 con EI.2-4", ["EI.2-4 convención"], ["ORC-2", "ORC-3"],
                  [msh(24), P["mateo"], orc(24, placer="PL-24^RV^1.2.3^ISO", filler="VX-24^RV^1.2.3^ISO"), rxa(24, "08", prov=3, mvx="MSD"),
                   rxr("IM", "LT")]))
    b.append(base(25, "MMR con ORC-4", ["ORC-4 nota"], ["ORC-4"],
                  [msh(25), P["lucia"], orc(25, orc4="GRP-25^REGVAC"), rxa(25, "03", prov=4, mvx="MSD"), rxr("SC", "RA")]))
    b.append(base(26, "Varicela con ORC-28 V", ["meta.security no se juzga"], ["ORC-28"],
                  [msh(26), P["pablo"], orc(26, orc28="V^Muy restringido^HL70177"), rxa(26, "21", prov=1, mvx="MSD"), rxr("SC", "LUA")]))
    b.append(base(27, "DTaP con RXR-2 de la 0550", ["0550 -> v2-0550"], ["RXR-2"],
                  [msh(27), P["begona"], orc(27), rxa(27, "20", prov=2, mvx="PMC"), rxr("IM", "DELT^Deltoides^HL70550")]))
    b.append(base(28, "IPV con RXR-2 de SNOMED CT", ["sitio fuera de 0163/0550"], ["RXR-2"],
                  [msh(28), P["mateo"], orc(28), rxa(28, "10", prov=3, mvx="SKB"), rxr("IM", "368208006^Brazo superior izquierdo^SCT")]))
    b.append(base(29, "Gripe con RXR-1 local", ["ruta fuera de la 0162"], ["RXR-1"],
                  [msh(29), P["elena"], orc(29), rxa(29, "88", prov=4, mvx="WAL"), rxr("JET^Inyector a presion^L", "LD")]))
    b.append(base(30, "MMR con dos OBX CE (elegibilidad y financiación)", ["OBX -> Observation partOf", "absorción"], ["OBX-3", "OBX-5"],
                  [msh(30), P["lucia"], orc(30), rxa(30, "03", prov=1, mvx="MSD"), rxr("SC", "RA"),
                   obx(1, "CE", "64994-7^Elegibilidad^LN", "ELE^Elegible programa^L", t14=fecha(30)),
                   obx(2, "CE", "30963-3^Fuente de financiacion^LN", "PUB^Publica^L", t14=fecha(30))]))
    b.append(base(31, "DTaP con dos OBX DT (hoja informativa)", ["OBX DT", "partOf"], ["OBX-3", "OBX-5"],
                  [msh(31), P["pablo"], orc(31), rxa(31, "20", prov=2, mvx="PMC"), rxr("IM", "LT"),
                   obx(1, "DT", "29768-9^Fecha de publicacion de la hoja^LN", "20210806"),
                   obx(2, "DT", "29769-7^Fecha de entrega de la hoja^LN", fecha(31, hora=False))]))
    b.append(base(32, "Varicela con OBX NM UCUM y NTE", ["OBX NM + UCUM", "NTE nota"], ["OBX-3", "OBX-6"],
                  [msh(32), P["begona"], orc(32), rxa(32, "21", prov=3, mvx="MSD"), rxr("SC", "LUA"),
                   obx(1, "NM", "8310-5^Temperatura corporal^LN", "38.5", "Cel^^UCUM", t14=fecha(32)[:8] + "1800"),
                   "NTE|1||Fiebre leve tras la vacuna"]))
    b.append(base(33, "Dos grupos ORDER (DTaP + IPV, misma visita)", ["emparejamiento por identifier", "recuentos"], ["ORC-3"],
                  [msh(33), P["mateo"], orc(33), rxa(33, "20", prov=4, mvx="PMC"), rxr("IM", "LT"),
                   orc(33, filler="VX-33B^REGVAC"), rxa(33, "10", prov=4, mvx="SKB", lote="LOT-B33B", cad=caducidad(34)), rxr("IM", "RVL")]))
    b.append(base(34, "Tres grupos ORDER del mismo CVX en tres fechas", ["tres Immunization del mismo código"], ["ORC-3", "RXA-3"],
                  [msh(34), P["pablo"]] + [s for k, f in enumerate((fecha(34, hora=False), fecha(36, hora=False), fecha(38, hora=False)))
                                           for s in (orc(34, filler="VX-34%s^REGVAC" % "ABC"[k]),
                                                     rxa(34, "20", prov=1 + k, mvx="PMC", lote="LOT-B34%s" % "ABC"[k], f3=f),
                                                     rxr("IM", "LT"))]))
    b.append(base(35, "Dos grupos, RE y CP, sin ORC-2 ni ORC-3", ["código+fecha", "nota ORC-3"], ["ORC-3", "RXA-20"],
                  [msh(35), P["elena"], orc(35, filler=""), rxa(35, "88", dosis="0", unidad="", prov=0, lote="", cad="", mvx="",
                                                               rech="PTE^Decision del paciente^L", c20="RE"),
                   orc(35, filler=""), rxa(35, "09", prov=2, mvx="SKB", f3=fecha(35)[:8] + "1130"), rxr("IM", "LD")]))
    b.append(base(36, "Lactante con NK1 MTH completo", ["NK1 -> RelatedPerson/contact", "MTH -> v3-RoleCode"], ["NK1-2", "NK1-3"],
                  [msh(36), P["mateo"],
                   nk1(1, "Prueba^Lucia^^^^^L", "MTH^Madre^HL70063", tel="^PRN^PH^^^^5551001",
                       dir_="Calle Sintetica 1^^Ciudad Modelo^^28000^ESP^H", sexo="F", nac="19900301"),
                   orc(36), rxa(36, "08", prov=3, mvx="MSD"), rxr("IM", "LT")]))
    b.append(base(37, "Niño con dos NK1: FTH (trabajo, rol C) y GRD", ["NK1 x2", "0131", "use work"], ["NK1-6", "NK1-7"],
                  [msh(37), P["pablo"],
                   nk1(1, "Ejemplo^Andres^^^^^L", "FTH^Padre^HL70063", tel="^PRN^PH^^^^5552001", tel_trabajo="^WPN^PH^^^^5552002",
                       rol="C^Contacto de urgencia^HL70131", sexo="M"),
                   nk1(2, "Modelo^Teresa^^^^^L", "GRD^Tutora^HL70063", tel="^PRN^PH^^^^5552003", sexo="F"),
                   orc(37), rxa(37, "21", prov=4, mvx="MSD"), rxr("SC", "LUA")]))
    b.append(base(38, "Adulto con PD1, PV1 con número de visita y PV2", ["PD1 nota", "PV1 opcional"], ["PD1-3", "PV1-19"],
                  [msh(38), P["carmen"], "PD1|||Centro de Salud Sintetico^^CS01|PR02^Muestra^Jorge||||||||||||A",
                   "PV1|1|R|||||||||||||||||V38", "PV2|||VAC^Vacunacion^L",
                   orc(38), rxa(38, "09", prov=1, mvx="SKB"), rxr("IM", "RD")]))
    b.append(base(39, "Niña con SFT, GT1, IN1/IN2, MSH-9.3 vacío, UTF-8 con ñ", ["segmentos sin mapa", "MSH-9.3 vacío", "UTF-8"], ["MSH-9", "MSH-18"],
                  [msh(39, est="", msh18="UNICODE UTF-8"), "SFT|Sintetico SL^L^^^^CSSYN|1.0|RegVac|B39", P["begona"].replace("Begona", "Begoña"),
                   nk1(1, "Simulado^Iñaki^^^^^L", "FTH^Padre^HL70063", tel="^PRN^PH^^^^5553001", sexo="M"),
                   "GT1|1||Simulado^Iñaki^^^^^L", "IN1|1|PLAN01^Plan sintetico^L|ASEG01^^^CSSYN|Aseguradora Sintetica", "IN2|1",
                   orc(39), rxa(39, "02", dosis="2", unidad="[drp]^gota^UCUM", prov=2, mvx="OTH"), rxr("PO")]))
    b.append(base(40, "Gripe adulto con dos RXA-19, IM/RD y \\S\\ en RXA-17.2", ["reasonCode x2", "escapes"], ["RXA-19", "RXA-17"],
                  [msh(40), P["elena"], orc(40), rxa(40, "88", prov=3, mvx="NOV^Novartis \\S\\ Vacunas^MVX", ind="DM^Diabetes^L~ASM^Asma^L"),
                   rxr("IM", "RD")]))
    assert [x["id"] for x in b] == ["B%02d" % k for k in range(1, 41)]
    return b


BASES = construir()


def cable(b):
    """El mensaje como va por el cable: segmentos separados por CR (sin MLLP)."""
    return "\r".join(b["segmentos"]) + "\r"


def huella(bases=None):
    h = hashlib.sha256()
    for b in bases or BASES:
        h.update(cable(b).encode("utf-8"))
    return h.hexdigest()


# ---------------------------------------------------------------------------- R-VX-7: la firma contra la mutación
def campos(b):
    """{«SEG(k)-n»: valor} de todos los campos valorados (k = ocurrencia del segmento, 1 sin paréntesis)."""
    out, vistos = {}, {}
    for s in b["segmentos"]:
        p = s.split("|")
        vistos[p[0]] = vistos.get(p[0], 0) + 1
        k = vistos[p[0]]
        for n, v in enumerate(p[1:], 1):
            n = n + 1 if p[0] == "MSH" else n                       # en MSH el primer campo tras el nombre es MSH-2
            if v:
                out["%s%s-%d" % (p[0], "" if k == 1 else "(%d)" % k, n)] = v
    return out


def firma(bases=None):
    """Pares con menos de 3 campos distintos (sin MSH-7/MSH-10), o que solo difieren en los campos que ejercita una de las dos."""
    bases = bases or BASES
    cs = [(b, campos(b)) for b in bases]
    malos = []
    for (a, ca), (b, cb) in itertools.combinations(cs, 2):
        dif = {k for k in set(ca) | set(cb) if ca.get(k) != cb.get(k) and re.sub(r"\(\d+\)", "", k) not in NO_FIRMA}
        base_dif = {re.sub(r"\(\d+\)", "", k) for k in dif}
        if len(dif) < 3 or base_dif <= set(a["campos"]) or base_dif <= set(b["campos"]):
            malos.append((a["id"], b["id"], sorted(dif)))
    return malos


# ---------------------------------------------------------------------------- cobertura (§4.2)
def cobertura():
    """Las filas «cuenta» de PERFIL_GUIA_VXU (datos, no juicio): cada campo valorado en alguna base y, si es opcional en 2.5, vacío
    en alguna; cada segmento presente en alguna. Y las ramas de tabla de §4.2. -> [faltas]."""
    sys.path.insert(0, AQUI)
    _argv, sys.argv = sys.argv, ["x", "--silencio"]
    import conversion_vxu as CVX
    import estructuras_hl7 as EH
    sys.argv = _argv
    cs = [campos(b) for b in BASES]
    segs = [{s.split("|")[0] for s in b["segmentos"]} for b in BASES]
    faltas = []
    for fila in CVX.PERFIL_GUIA_VXU:
        if fila["nivel"] != "cuenta" or fila["campo"] in ("—", "PID-3"):
            continue
        for parte in fila["campo"].split("/"):
            if "-" not in parte:
                if not any(parte in s for s in segs):
                    faltas.append("%s: ninguna base con %s" % (fila["elemento"], parte))
                continue
            if not any(any(re.sub(r"\(\d+\)", "", k) == parte for k in c) for c in cs):
                faltas.append("%s: ninguna base con %s valorado" % (fila["elemento"], parte))
            opt = (EH.CAMPOS.get(parte) or {}).get("opt")
            if opt != "R" and not any(not any(re.sub(r"\(\d+\)", "", k) == parte for k in c) for c in cs):
                faltas.append("%s: ninguna base con %s vacío" % (fila["elemento"], parte))
    val = lambda campo: {c.get(campo, "").split("^")[0] for c in cs}  # noqa: E731
    for nombre, campo, esperados in (("0322", "RXA-20", {"CP", "RE", "NA", "PA", ""}), ("0323", "RXA-21", {"A", "D", "U", ""}),
                                     ("0162 grupo 2", "RXR-1", {"ID", "IM", "PO", "SC"}), ("0163", "RXR-2", {"LD", "RA", "LT"}),
                                     ("0550 y SCT", "RXR-2", {"DELT", "368208006"})):
        if not esperados <= val(campo):
            faltas.append("%s: faltan %s en %s" % (nombre, sorted(esperados - val(campo)), campo))
    grupos = {sum(1 for s in b["segmentos"] if s.startswith("ORC|")) for b in BASES}
    nk1s = {sum(1 for s in b["segmentos"] if s.startswith("NK1|")) for b in BASES}
    if not {1, 2, 3} <= grupos or not {0, 1, 2} <= nk1s:
        faltas.append("grupos ORDER %r o NK1 %r sin uno, dos y tres / cero, uno y dos" % (sorted(grupos), sorted(nk1s)))
    return faltas


# ---------------------------------------------------------------------------- autoprueba (§4.1.4)
def autoprueba():
    sys.path.insert(0, AQUI)
    _argv, sys.argv = sys.argv, ["x", "--silencio"]
    import estructuras_hl7 as EH
    import mapeador_referencia as MR
    import puntos_entrada as PE
    import conversion_vxu as CVX
    sys.argv = _argv
    ok, n = [], [0]

    def mira(nombre, cond):
        n[0] += 1
        if not cond:
            ok.append(nombre)
            print("  MAL", nombre)
    g = EH.gramatica("VXU_V04")
    for b in BASES:
        ms = MR.mensajes(cable(b))
        mira("%s: un mensaje" % b["id"], len(ms) == 1)
        if len(ms) != 1:
            continue
        m = ms[0]
        mira("%s: estructura VXU_V04" % b["id"], PE.estructura_de(m, PE.PUNTOS["vxu_conv"]) == "VXU_V04")
        r = EH.emparejar([s.split(m.f)[0] for s in m.segs], g, "VXU_V04")
        mira("%s: sin ausentes ni fuera de orden %r" % (b["id"], (r["faltan"], r["fuera_de_orden"])), not r["faltan"] and not r["fuera_de_orden"])
        c = campos(b)
        mira("%s: texto no ASCII solo con MSH-18 UNICODE UTF-8" % b["id"], cable(b).isascii() or c.get("MSH-18") == "UNICODE UTF-8")
        for k, v in c.items():
            campo = re.sub(r"\(\d+\)", "", k)
            at = EH.CAMPOS.get(campo) or {}
            for rep in v.split("~"):
                if at.get("dt") == "TS":
                    mira("%s %s TS %r" % (b["id"], k, rep), MR.partes_dtm(rep.split("^")[0])[0] is not None)
                if at.get("dt") == "NM":
                    mira("%s %s NM %r" % (b["id"], k, rep), bool(CVX.CV.NM_RE.match(rep)))
            cod = v.split("^")[0]
            local = len(v.split("^")) > 2 and v.split("^")[2] in ("L", "SCT")
            if campo == "RXA-20":
                mira("%s RXA-20 en la 0322" % b["id"], CVX.mapa("0322", cod) != CVX.FUERA)
            if campo == "RXA-21":
                mira("%s RXA-21 en la 0323" % b["id"], cod in CVX.ACCION_0323)
            if campo == "RXR-1":
                mira("%s RXR-1 en la 0162 o local" % b["id"], local or CVX.mapa("0162", cod) != CVX.FUERA)
            if campo == "RXR-2":
                mira("%s RXR-2 en la 0163/0550 o externo" % b["id"], local or CVX.mapa("0163", cod) != CVX.FUERA or CVX.mapa("0550", cod) != CVX.FUERA)
            if campo in ("PID-5", "NK1-2", "RXA-10", "ORC-12", "GT1-3", "PD1-4"):
                for rep in v.split("~"):
                    fam = rep.split("^")[1] if campo in ("RXA-10", "ORC-12", "PD1-4") else rep.split("^")[0]
                    mira("%s %s apellido sintético %r" % (b["id"], k, fam), fam in APELLIDOS)
    malos = firma()
    mira("firma: todo par con ≥ 3 campos distintos %r" % malos[:3], not malos)
    faltas = cobertura()
    mira("cobertura %r" % faltas[:3], not faltas)
    mira("determinismo: dos construcciones iguales", huella(construir()) == huella())
    if HUELLA:
        mira("huella del conjunto fijada", huella() == HUELLA)
    else:
        print("  (huella del conjunto sin fijar: %s)" % huella())
    print("AUTOPRUEBA DE bases_vxu: %s (%d comprobaciones, %d bases)" % ("TODO BIEN" if not ok else "%d MAL" % len(ok), n[0], len(BASES)))
    return not ok


def escribir():
    os.makedirs(CARPETA, exist_ok=True)
    with open(INDICE, "w", encoding="utf-8") as idx:
        for b in BASES:
            with open(os.path.join(CARPETA, b["id"] + ".hl7"), "w", encoding="utf-8", newline="") as f:
                f.write(cable(b))
            idx.write(json.dumps({"id": b["id"], "descripcion": b["descripcion"], "ejercita": b["ejercita"], "campos": b["campos"],
                                  "fichero": "bases_vxu/%s.hl7" % b["id"], "msh10": "VXU-" + b["id"], "segmentos": len(b["segmentos"])},
                                 ensure_ascii=False) + "\n")
    return len(BASES)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--lista"]:
        for b in BASES:
            print(b["id"], b["descripcion"])
    elif sys.argv[1:2] == ["--firma"]:
        malos = firma()
        print("\n".join("%s %s: %r" % m for m in malos) or "firma: todo par con 3 o más campos distintos")
        sys.exit(1 if malos else 0)
    elif sys.argv[1:2] == ["--cobertura"]:
        f = cobertura()
        print("\n".join(f) or "cobertura completa")
        sys.exit(1 if f else 0)
    elif sys.argv[1:2] == ["--autoprueba"]:
        sys.exit(0 if autoprueba() else 1)
    else:
        print("escritas %d bases en %s y %s; huella %s" % (escribir(), CARPETA, INDICE, huella()[:12]))
