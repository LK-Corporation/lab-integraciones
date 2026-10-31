#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Las 40 bases MDM^T02 sintéticas de md/diseno-md.md §5 (etapa 26, MD2-a): documentos clínicos VÁLIDOS en v2.5, escritos desde
[E9 CH09.txt:306-354] (estructura), §9.6.1 (TXA), §9.6.2 y [E7 CH07.txt:2556-2652] (OBX), [E2A CH02A.txt:1804-1876, 4384-4448] (ED y
RP), [E2 CH02.txt:947-1111] (escapes y formato), [E4] (ORC, OBR, TQ1) y el ejemplo de [E9 CH09.txt:1963-1983]. Cada base ejercita
una rama de la guía o del estándar (§5.2), no un fallo supuesto de nadie; los imposibles van a las pruebas P-MD, no aquí. Pacientes
y profesionales ficticios, apellidos de una lista cerrada; cada OBX lleva una palabra ancla única (Zeta…) y las cargas binarias se
generan aquí con base64 y binascii desde cadenas sintéticas. Deterministas. Las bases son las del diseño, escrito a ciegas de lo
que devuelven los conversores; las desviaciones vienen del estándar y están en md/decisiones-qmd.md (DV-MD-6 y DV-MD-7).

Escribe bases_mdm/BNN.hl7 (segmentos separados por CR, sin MLLP) y bases_mdm.jsonl (id, descripcion, ejercita, campos, fichero,
msh10, segmentos). Aquí NO se escribe ningún Bundle ni canónico esperado: la previsión se sella aparte (§6).

Uso: python3 bases_mdm.py               escribe los ficheros
     python3 bases_mdm.py --lista       id y descripción
     python3 bases_mdm.py --firma       pares de bases con menos de 3 campos distintos (§5.1.3)
     python3 bases_mdm.py --cobertura   filas «cuenta» del perfil sin base valorada o vacía, y las ramas de §5.2
     python3 bases_mdm.py --secundario  escribe S01..S04 (T04, T06, T08, T10; para la alternativa de Q-MD-D-1, fuera de las 40)
     python3 bases_mdm.py --autoprueba  lectura, estructura, condiciones, tipos y tablas, ED.5, firma, cobertura y huella"""
import base64
import binascii
import datetime
import hashlib
import itertools
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CARPETA = os.path.join(AQUI, "bases_mdm")
INDICE = os.path.join(AQUI, "bases_mdm.jsonl")
CARPETA_SEC = os.path.join(AQUI, "bases_mdm_secundario")
INDICE_SEC = os.path.join(AQUI, "bases_mdm_secundario.jsonl")
HUELLA = "f954ee625d06cd4030b44a0abb94ff1886a91d0d38349684e1c6a60fff665396"   # sha256 de los 40 cables en orden (MD3-r1, DV-MD-7)
APELLIDOS = {"Prueba", "Sintetico", "Ficticia", "Ejemplo", "Modelo", "Simulado", "Ensayo", "Muestra", "Patron", "Plantilla"}
NO_FIRMA = {"MSH-7", "MSH-10", "EVN-2"}                               # §5.1.3: metadatos del envío, no cuentan para la firma

# Las tablas de v2.5 que la autoprueba exige (sin importar conversion_mdm: un error del perfil no se confirma a sí mismo, §5.3)
T0191 = {"AP", "AU", "FT", "IM", "MULTIPART", "NS", "SD", "SI", "TEXT", "TX"}                       # [E9 CH09.txt:892-903]
T0291 = {"BASIC", "DICOM", "FAX", "GIF", "HTML", "JOT", "JPEG", "OCTET-STREAM", "PICT", "POSTSCRIPT", "RTF", "SGML", "TIFF",
         "X-HL7-CDA-LEVEL-ONE", "XML"}                                                           # [E2A CH02A.txt:4431-4448]
T0299 = {"A", "HEX", "BASE64"}                                                                    # [E2A CH02A.txt:1850-1859]
T0271 = {"DI", "DO", "IP", "IN", "PA", "AU", "LA"}                                                # [E9 CH09.txt:1492-1500]
T0272 = {"V", "R", "U"}                                                                           # [E9 CH09.txt:1591-1602]
T0273 = {"AV", "CA", "OB", "UN"}                                                                  # [E9 CH09.txt:1604-1621]
T0125 = {"AD", "CE", "CF", "CK", "CN", "CP", "CX", "DT", "ED", "FT", "MO", "NM", "PN", "RP", "SN", "ST", "TM", "TN", "TS", "TX", "XAD",
         "XCN", "XON", "XPN", "XTN"}                                                              # [E7 CH07.txt:2603-2637]


# ---------------------------------------------------------------------------- las piezas (§5.2, §5.3)
def dia(n):
    """Un día por base, repartido por 2023-2024: 9-ene-2023 + 11·n días."""
    return datetime.date(2023, 1, 9) + datetime.timedelta(days=11 * n)


def ts(n, hora, zona=True):
    """El instante de la base n a la hora dada, con los minutos = n (cada base el suyo); con zona +0100."""
    return dia(n).strftime("%Y%m%d") + "%02d%02d00" % (hora, n) + ("+0100" if zona else "")


def msh(n, ev="T02", est="MDM_T02", msh18="", ver="2.5", pref="B"):
    return "MSH|^~\\&|DOCSYS|CSSYN|HIS|SALUD|%s||MDM^%s%s|MDM-%s%02d|P|%s%s" % (
        ts(n, 11), ev, "^" + est if est else "", pref, n, ver, "||||||" + msh18 if msh18 else "")


def evn(n, ev="T02", evn4=""):
    return seg("EVN", {1: ev, 2: ts(n, 11), 4: evn4})


PIDS = {
    "mateo": "PID|1||DOC0001^^^CSSYN^MR||Prueba^Mateo^^^^^L||20230512|M",
    "lucia": "PID|1||DOC0002^^^CSSYN^MR~SYNM0002^^^CSSYN^PI||Sintetico^Lucia^^^^^L||19840304|F",
    "carmen": "PID|1||DOC0003^^^CSSYN^MR||Ficticia^Carmen^Rosa^^^^L||19580917|F",
    "pablo": "PID|1||DOC0004^^^CSSYN^MR||Ejemplo^Pablo^^^^^L||19790811|M",
    "elena": "PID|1||DOC0005^^^CSSYN^MR||Modelo^Elena^^^^^L||19900122|F",
    "begona": "PID|1||DOC0006^^^CSSYN^MR~SYNM0006^^^CSSYN^PI||Simulado^Begona^^^^^L||19660707|F",   # en B39, «Begoña» con MSH-18 UTF-8
}
PROF = {1: "PR01^Ensayo^Ana^^^Dra", 2: "PR02^Muestra^Jorge", 3: "PR03^Patron^Irene", 4: "PR04^Plantilla^Raul"}   # 4: transcriptor
UBIC = {"I": "PLANTA3^305^B^HSYN", "O": "CEXT^C12^^HSYN", "E": "URG^B04^^HSYN"}
OBR4 = {"DS": "DOC-DS^Informe de alta^L", "HP": "DOC-HP^Historia clinica^L", "CN": "DOC-CN^Interconsulta^L", "OP": "DOC-OP^Informe quirurgico^L",
        "PN": "DOC-PN^Nota de procedimiento^L", "PR": "DOC-PR^Nota de evolucion^L", "DI": "DOC-DI^Estudio de imagen^L",
        "SP": "DOC-SP^Anatomia patologica^L", "CD": "DOC-CD^Estudio cardiologico^L", "PC": "DOC-PC^Valoracion psiquiatrica^L",
        "ED": "DOC-ED^Informe de urgencias^L", "PH": "DOC-PH^Historia psiquiatrica^L", "ZX": "DOC-ZX^Documento local^L",
        "AN": "DOC-AN^Informe de anestesia^L"}
ARCHIVO = {"DS": "alta", "HP": "hc", "CN": "cons", "OP": "qx", "PN": "proc", "PR": "evol", "DI": "img", "TS": "tras", "SP": "ap",
           "CD": "card", "PC": "psq", "ED": "urg", "PH": "psqh", "ZX": "loc"}
FRASES = ["Paciente estable al alta", "Se recomienda control en consultas externas", "Sin alergias medicamentosas conocidas",
          "Exploracion fisica sin hallazgos relevantes", "Tension arterial dentro de la normalidad", "Se pauta analgesia de rescate",
          "Evolucion favorable durante el ingreso", "Herida quirurgica limpia y sin signos de infeccion", "Dolor toracico de inicio subito",
          "Se solicita radiografia de torax", "Tolera dieta oral sin incidencias", "Afebril en las ultimas cuarenta y ocho horas",
          "Auscultacion cardiaca con ritmo regular", "Abdomen blando y depresible", "Se explica el procedimiento al paciente",
          "Pendiente de resultados de laboratorio", "Movilidad conservada en las cuatro extremidades", "Refiere cefalea leve matutina"]


def seg(nombre, campos):
    """Un segmento desde {número de campo: valor} (como bases_vxu.seg, sin MSH)."""
    p = [nombre] + [""] * (max(campos) if campos else 0)
    for k, v in campos.items():
        p[k] = v
    return "|".join(p).rstrip("|") if campos else nombre


def ancla(n, k, j=0):
    """La palabra única que acompaña a cada OBX (y a cada línea o NTE): «llega entero» es comprobable (§5.1.1)."""
    return "Zeta%02d%02d%02d" % (n, k, j)


def frase(n, k, j=0):
    return "%s %s" % (FRASES[(3 * n + 5 * k + j) % len(FRASES)], ancla(n, k, j))


def carga(n, sufijo):
    """El binario sintético de un ED (§5.3): Base64, Hex o ASCII se calculan desde aquí, nunca a mano."""
    return ("SINTETICO-%02d-%s" % (n, sufijo)).encode("ascii")


def b64(x):
    return base64.b64encode(x).decode("ascii")


def hexa(x):
    return binascii.hexlify(x).decode("ascii").upper()


def obx(k, tipo, valor, cod="TEXTO^Texto del informe^L", sub=""):
    return seg("OBX", {1: str(k), 2: tipo, 3: cod, 4: sub, 5: valor, 11: "F"})


def obx_tx(n, k, lineas=1, cod="TEXTO^Texto del informe^L", sub=""):
    """TX: una línea por repetición (la repetición separa párrafos, [E2A CH02A.txt:5446-5453])."""
    return obx(k, "TX", "~".join(frase(n, k, j) for j in range(lineas)), cod, sub)


def obx_ed(n, k, reps, cod="ADJUNTO^Documento adjunto^L"):
    """reps: [(ED.2, ED.3, ED.4, ED.5)]; ED.1 vacío."""
    return obx(k, "ED", "~".join("^%s^%s^%s^%s" % r for r in reps), cod)


def obx_rp(n, k, reps, cod="REFERENCIA^Referencia externa^L"):
    """reps: [(RP.1, RP.3, RP.4)]; RP.2 vacío."""
    return obx(k, "RP", "~".join("%s^^%s^%s" % r for r in reps), cod)


def nte(j, texto, tipo=""):
    return seg("NTE", {1: str(j), 3: texto, 4: tipo})


def pv1(n, clase="I", ubic=True, visita=True):
    return seg("PV1", {1: "1", 2: clase, 3: UBIC[clase] if ubic else "", 19: "V%04d^^^CSSYN^VN" % n if visita else ""})


def orden(n, tipo, suf="", orc_num=True, obr_num=True, orc5="", orc12="", obr16="", tq1=False, ntes=(), orc1="RE"):
    """Un grupo COMMON_ORDER: ORC [TQ1] OBR [NTE…], con los números de placer y de filler (§5.2, piezas comunes)."""
    pl, fl = "PL%04d%s^CSSYN" % (n, suf), "FL%04d%s^CSSYN" % (n, suf)
    s = [seg("ORC", {1: orc1, 2: pl if orc_num else "", 3: fl if orc_num else "", 5: orc5, 12: orc12})]
    if tq1:
        s.append(seg("TQ1", {1: "1", 7: ts(n, 8)}))
    s.append(seg("OBR", {1: "1", 2: pl if obr_num else "", 3: fl if obr_num else "", 4: OBR4[tipo], 16: obr16}))
    return s + [nte(j, t) for j, t in enumerate(ntes, 1)]


def txa(n, tipo, pres="TEXT", tipico=True, ext="txt", **c):
    """TXA-1..23 desde {número: valor} (§5.3: por omisión vacíos salvo 1, 2, 3, 12 y 17). Con tipico, lo que lleva un documento
    corriente: TXA-6 con hora y zona, un autor (TXA-9), un autenticador asignado (TXA-10), el fichero (TXA-16), TXA-18 U y TXA-19 AV;
    y, si TXA-17 no es DI, la transcripción (TXA-7 y TXA-11, condicionados por el estándar: DV-MD-6); con AU o LA, la autenticación
    (TXA-22 con la persona de TXA-10 y su fecha: DV-MD-7)."""
    f = {1: "1", 2: tipo, 3: pres, 12: "DOC%04d^CSSYN" % n, 17: c.pop("t17", "AU")}
    if tipico:
        f.update({6: ts(n, 9), 9: PROF[1 + n % 3], 10: PROF[1 + (n + 1) % 3], 16: "/docs/%d/%s%04d.%s" % (dia(n).year, ARCHIVO[tipo], n, ext),
                  18: "U", 19: "AV"})
        if f[17] != "DI":
            f.update({7: ts(n, 10), 11: PROF[4]})
    for k, v in c.items():
        num = int(k[1:])
        if v is None:
            f.pop(num, None)
        else:
            f[num] = v
    if tipico and f[17] in ("AU", "LA") and 22 not in f:             # DV-MD-7: con AU o LA, TXA-22 es obligatorio ([E9 CH09.txt:1798-1800])
        f[22] = ppn(f[10].split("~")[0], dia(n).strftime("%Y%m%d") + "10%02d30+0100" % n)
    return seg("TXA", f)


def ppn(xcn, cuando):
    """TXA-22 (PPN): la persona (los 14 primeros componentes, los de XCN) y PPN.15, la fecha y hora de la autenticación."""
    return "^".join((xcn.split("^") + [""] * 14)[:14] + [cuando])


def base(n, descripcion, ejercita, campos, segs):
    return {"id": "B%02d" % n, "descripcion": descripcion, "ejercita": ejercita, "campos": campos, "segmentos": segs}


def cab(n, paciente, clase="I", **k):
    return [msh(n, **k), evn(n), PIDS[paciente], pv1(n, clase)]


# ---------------------------------------------------------------------------- las 40 bases (§5.2)
def construir():
    b = []
    b.append(base(1, "Control. DS; TXA-3 TEXT, TXA-17 AU, TXA-18 R, TXA-19 AV; TXA-6 con hora y zona; TXA-9 y TXA-10 una vez; "
                     "TXA-12 DOC0001^CSSYN; TXA-16 /docs/2023/alta0001.txt; un grupo ORC+OBR; un OBX TX de una línea",
                  ["AU", "AV", "R", "TX básico", "PLAC+FILL", "zona por instante"], [],
                  cab(1, "mateo") + orden(1, "DS") + [txa(1, "DS", t18="R"), obx_tx(1, 1)]))
    b.append(base(2, "Control. HP; TXA-17 LA, TXA-18 V; cuatro OBX TX con OBX-3 y OBX-4 (como el ejemplo del capítulo 9)",
                  ["LA -> final", "V", "varios OBX de TX"], [],
                  cab(2, "carmen") + orden(2, "HP") + [txa(2, "HP", t17="LA", t18="V")] +
                  [obx_tx(2, k, cod=c, sub=str(k)) for k, c in enumerate(("2000.40^MOTIVO^L", "2000.02^ENFERMEDAD ACTUAL^L",
                                                                          "2000.10^EXPLORACION^L", "2000.20^PLAN^L"), 1)]))
    b.append(base(3, "Control. CN; TXA-17 PA, TXA-18 U; un OBX FT con \\.in+4\\\\.ti-4\\ … \\.br\\",
                  ["PA -> preliminary", "U", "FT"], [],
                  cab(3, "pablo", "O") + orden(3, "CN") + [txa(3, "CN", t17="PA"),
                                                           obx(1, "FT", "\\.in+4\\\\.ti-4\\%s\\.br\\%s" % (frase(3, 1, 0), frase(3, 1, 1)),
                                                               "TEXTOF^Texto con formato^L")]))
    b.append(base(4, "Control. OP; TXA-17 IP; TXA-19 vacío; un OBX TX con cuatro repeticiones",
                  ["IP", "vacío -> current", "salto entre repeticiones"], [],
                  cab(4, "elena") + orden(4, "OP") + [txa(4, "OP", t17="IP", t19=None), obx_tx(4, 1, lineas=4)]))
    b.append(base(5, "Control. PN; TXA-3 AP; un OBX ED ^AP^RTF^Base64", ["ED en Base64", "subtipo RTF"], [],
                  cab(5, "lucia") + orden(5, "PN") + [txa(5, "PN", "AP", ext="rtf"), obx_ed(5, 1, [("AP", "RTF", "Base64", b64(carga(5, "RTF")))])]))
    b.append(base(6, "Control. PR; TXA-3 IM; un OBX RP <puntero>^^IM^JPEG", ["RP: url y contentType"], [],
                  cab(6, "begona", "O") + orden(6, "PR") + [txa(6, "PR", "IM", ext="jpg"), obx_rp(6, 1, [("ptr-b06-1", "IM", "JPEG")])]))
    b.append(base(7, "Control. DI; TXA-3 IM; un OBX ED ^IM^JPEG^Base64", ["ED imagen"], [],
                  cab(7, "pablo", "O") + orden(7, "DI") + [txa(7, "DI", "IM", ext="jpg"), obx_ed(7, 1, [("IM", "JPEG", "Base64", b64(carga(7, "IM")))])]))
    b.append(base(8, "Control. TS (traslado); sin COMMON_ORDER; TXA-17 DI; un OBX TX", ["DI -> preliminary", "sin ServiceRequest"], [],
                  cab(8, "carmen") + [txa(8, "TS", t17="DI"), obx_tx(8, 1)]))
    b.append(base(9, "PN con TXA-17 DO y TXA-19 AV", ["DO"], ["TXA-17"],
                  cab(9, "mateo", "O") + orden(9, "PN") + [txa(9, "PN", t17="DO"), obx_tx(9, 1)]))
    b.append(base(10, "CN con TXA-17 IN y TXA-19 UN", ["IN", "UN -> solo extensión"], ["TXA-17", "TXA-19"],
                  cab(10, "lucia", "O") + orden(10, "CN") + [txa(10, "CN", t17="IN", t19="UN"), obx_tx(10, 1)]))
    b.append(base(11, "CN con TXA-17 AU y TXA-19 CA (borrado)", ["CA -> entered-in-error o extensión"], ["TXA-19"],
                  cab(11, "carmen", "O") + orden(11, "CN") + [txa(11, "CN", t19="CA"), obx_tx(11, 1)]))
    b.append(base(12, "PR con TXA-17 LA y TXA-19 OB (obsoleto)", ["OB -> superseded o extensión"], ["TXA-17", "TXA-19"],
                  cab(12, "pablo") + orden(12, "PR") + [txa(12, "PR", t17="LA", t19="OB"), obx_tx(12, 1)]))
    b.append(base(13, "ED ^AP^Octet-stream^Base64 con TXA-3 AP", ["contentType desde ED.3 (octet-stream)"], ["OBX-5"],
                  cab(13, "elena") + orden(13, "SP") + [txa(13, "SP", "AP", ext="bin"),
                                                        obx_ed(13, 1, [("AP", "Octet-stream", "Base64", b64(carga(13, "BIN")))])]))
    xml = "<doc id=\"b14\"><p>SINTETICO-14-XML \\T\\ datos</p><p>clave\\S\\valor</p></doc>"
    b.append(base(14, "ED ^TEXT^XML^A con \\T\\ y \\S\\, TXA-3 TEXT", ["ED.4 = A: ASCII con escapes de delimitador"], ["OBX-5"],
                  cab(14, "begona") + orden(14, "CD") + [txa(14, "CD", ext="xml"), obx_ed(14, 1, [("TEXT", "XML", "A", xml)])]))
    b.append(base(15, "ED ^AP^PostScript^Hex", ["ED.4 = Hex -> Base64"], ["OBX-5"],
                  cab(15, "mateo") + orden(15, "PC") + [txa(15, "PC", "AP", ext="ps"),
                                                        obx_ed(15, 1, [("AP", "PostScript", "Hex", hexa(carga(15, "PS")))])]))
    b.append(base(16, "ED ^IM^^Base64 (sin ED.3)", ["ED.2 -> extensión", "sin contentType esperado"], ["OBX-5"],
                  cab(16, "lucia", "O") + orden(16, "DI") + [txa(16, "DI", "IM", ext="img"), obx_ed(16, 1, [("IM", "", "Base64", b64(carga(16, "IM")))])]))
    b.append(base(17, "ED CDA ^multipart^x-hl7-cda-level-one^Base64, TXA-3 multipart", ["CDA como ED, sin interpretarlo"], ["OBX-5", "TXA-3"],
                  cab(17, "carmen") + orden(17, "DS") + [txa(17, "DS", "multipart", ext="xml"),
                                                         obx_ed(17, 1, [("multipart", "x-hl7-cda-level-one", "Base64", b64(carga(17, "CDA")))])]))
    b.append(base(18, "Dos repeticiones de ED en un OBX-5 (JPEG y GIF)", ["una content por repetición"], ["OBX-5"],
                  cab(18, "pablo", "O") + orden(18, "DI") + [txa(18, "DI", "IM", ext="img"),
                                                             obx_ed(18, 1, [("IM", "JPEG", "Base64", b64(carga(18, "JPG"))),
                                                                            ("IM", "GIF", "Base64", b64(carga(18, "GIF")))])]))
    b.append(base(19, "Dos repeticiones de RP en un OBX-5", ["una content por repetición"], ["OBX-5"],
                  cab(19, "elena", "O") + orden(19, "DI") + [txa(19, "DI", "IM", ext="img"),
                                                             obx_rp(19, 1, [("ptr-b19-1", "IM", "JPEG"), ("ptr-b19-2", "IM", "TIFF")])]))
    b.append(base(20, "Documento largo: 12 OBX TX con cinco repeticiones cada uno (60 líneas) y anclas", ["llega entero", "varios OBX", "orden"],
                  ["OBX-5"], cab(20, "begona") + orden(20, "HP") + [txa(20, "HP")] +
                  [obx_tx(20, k, lineas=5, cod="2000.%02d^SECCION %d^L" % (k, k)) for k in range(1, 13)]))
    ft21 = "\\H\\%s\\N\\\\.sp\\\\.ce\\%s\\.nf\\%s" % (frase(21, 1, 0), frase(21, 1, 1), frase(21, 1, 2))
    b.append(base(21, "FT con \\H\\…\\N\\, \\.sp\\, \\.ce\\ y \\.nf\\", ["FT: órdenes de formato"], ["OBX-5"],
                  cab(21, "mateo", "O") + orden(21, "CN") + [txa(21, "CN"), obx(1, "FT", ft21, "TEXTOF^Texto con formato^L")]))
    tx22 = ("Revisión del día: niño con tensión 110\\S\\70 \\T\\ pulso 88 \\F\\ ritmo regular \\R\\ sin cambios \\E\\ fin %s" % ancla(22, 1))
    b.append(base(22, "TX con \\F\\ \\S\\ \\T\\ \\R\\ \\E\\ y ñ/í con MSH-18 UNICODE UTF-8", ["desescape de delimitadores", "UTF-8"],
                  ["OBX-5", "MSH-18"],
                  [msh(22, msh18="UNICODE UTF-8"), evn(22), PIDS["lucia"], pv1(22, "E")] + orden(22, "ED") + [txa(22, "ED"), obx(1, "TX", tx22)]))
    b.append(base(23, "Mixto TX + ED: dos OBX TX y un OBX ED Base64 (informe con imagen)", ["content múltiples de tipos distintos"],
                  ["OBX-5", "OBX-2"],
                  cab(23, "carmen") + orden(23, "DI") + [txa(23, "DI"), obx_tx(23, 1), obx_tx(23, 2),
                                                         obx_ed(23, 3, [("IM", "JPEG", "Base64", b64(carga(23, "IM")))])]))
    ft24 = "%s\\.br\\%s" % (frase(24, 2, 0), frase(24, 2, 1))
    b.append(base(24, "Mixto TX + FT + RP", ["TX, FT y RP juntos"], ["OBX-5", "OBX-2"],
                  cab(24, "pablo") + orden(24, "OP") + [txa(24, "OP"), obx_tx(24, 1), obx(2, "FT", ft24, "TEXTOF^Texto con formato^L"),
                                                        obx_rp(24, 3, [("ptr-b24-3", "IM", "DICOM")])]))
    b.append(base(25, "OBX CE y ST estructurados (como el ejemplo del capítulo 9) y dos TX", ["OBX sin destino (nota)", "obx_sin_destino"],
                  ["OBX-2", "OBX-5"],
                  cab(25, "elena", "E") + orden(25, "HP") + [txa(25, "HP"), obx(1, "CE", "DT01^Dolor toracico^L", "2000.40^MOTIVO^L"),
                                                             obx(2, "ST", "PACIENTE", "2000.01^FUENTE^L"),
                                                             obx_tx(25, 3, cod="2000.02^ENFERMEDAD ACTUAL^L"), obx_tx(25, 4, cod="2000.20^PLAN^L")]))
    b.append(base(26, "OBX TX con un NTE (NTE-3 de una línea)", ["NTE bajo OBX -> content"], ["NTE-3"],
                  cab(26, "begona", "O") + orden(26, "PR") + [txa(26, "PR"), obx_tx(26, 1), nte(1, frase(26, 1, 9))]))
    b.append(base(27, "OBX FT con dos NTE (NTE-3 con repeticiones) y NTE-4", ["NTE múltiples"], ["NTE-3", "NTE-4"],
                  cab(27, "mateo") + orden(27, "PH") + [txa(27, "PH"), obx(1, "FT", frase(27, 1, 0), "TEXTOF^Texto con formato^L"),
                                                        nte(1, "%s~%s" % (frase(27, 1, 7), frase(27, 1, 8)), "RE^Observacion^HL70364"),
                                                        nte(2, "%s~%s" % (frase(27, 1, 5), frase(27, 1, 6)), "RE^Observacion^HL70364")]))
    b.append(base(28, "Dos grupos ORC/OBR con TQ1 y números distintos", ["ServiceRequest x2", "context.related"], ["ORC-2", "ORC-3", "OBR-4"],
                  cab(28, "lucia") + orden(28, "OP", "A", tq1=True) + orden(28, "AN", "B", tq1=True) + [txa(28, "OP"), obx_tx(28, 1)]))
    b.append(base(29, "Tres grupos (escenario B de §9.5.2), el mismo OBR-4 y distintos números de placer y de filler",
                  ["emparejamiento por identifier", "todos o el primero"], ["ORC-2", "ORC-3"],
                  cab(29, "carmen", "O") + orden(29, "DI", "A") + orden(29, "DI", "B") + orden(29, "DI", "C") + [txa(29, "DI"), obx_tx(29, 1)]))
    b.append(base(30, "Un grupo con ORC-2/3 vacíos y OBR-2/3 valorados, y NTE bajo OBR", ["los números salen del OBR", "NTE de OBR: nota"],
                  ["ORC-2", "ORC-3", "NTE-3"],
                  cab(30, "pablo") + orden(30, "SP", orc_num=False, ntes=["Muestra remitida en formol %s" % ancla(30, 0)]) +
                  [txa(30, "SP"), obx_tx(30, 1)]))
    b.append(base(31, "TXA-14 y TXA-15 valorados además de los de ORC/OBR", ["los de TXA se ignoran ([E9 CH09.txt:242-246])"],
                  ["TXA-14", "TXA-15"],
                  cab(31, "elena", "O") + orden(31, "PN") + [txa(31, "PN", t14="PL0031^CSSYN", t15="FL0031^CSSYN"), obx_tx(31, 1)]))
    b.append(base(32, "ORC-5, ORC-12 y OBR-16 (solicitante) valorados", ["status e intent sin esperado", "solicitante: nota"],
                  ["ORC-5", "ORC-12", "OBR-16"],
                  cab(32, "begona", "O") + orden(32, "CD", orc1="SC", orc5="CM", orc12=PROF[3], obr16=PROF[3]) + [txa(32, "CD"), obx_tx(32, 1)]))
    b.append(base(33, "TXA-4, TXA-6 con hora y zona, TXA-7 y TXA-8 dos veces, TXA-5 (condicionado a TXA-4)",
                  ["date por instante", "los demás sin destino"], ["TXA-4", "TXA-5", "TXA-8"],
                  cab(33, "mateo") + orden(33, "DS") + [txa(33, "DS", t4=ts(33, 8), t5=PROF[1], t8="%s~%s" % (ts(33, 12), ts(33, 13))),
                                                        obx_tx(33, 1)]))
    b.append(base(34, "TXA-6 solo fecha", ["date ausente (R6 no disponible)"], ["TXA-6"],
                  cab(34, "lucia", "O") + orden(34, "PR") + [txa(34, "PR", t6=dia(34).strftime("%Y%m%d")), obx_tx(34, 1)]))
    b.append(base(35, "TXA-9 y TXA-10 dos veces, TXA-5 y TXA-11", ["author[]", "authenticator 0..1"], ["TXA-9", "TXA-10", "TXA-5", "TXA-11"],
                  cab(35, "carmen", "O") + orden(35, "CN") + [txa(35, "CN", t5=PROF[1], t9="%s~%s" % (PROF[1], PROF[3]), t10="%s~%s" % (PROF[2], PROF[3])),
                                                              obx_tx(35, 1)]))
    b.append(base(36, "TXA-12 con EI.2-EI.4 y TXA-16 con ruta de Windows C:\\E\\docs\\E\\b36.rtf", ["assigner/system", "ruta completa desescapada"],
                  ["TXA-12", "TXA-16"],
                  cab(36, "pablo") + orden(36, "OP") + [txa(36, "OP", t12="DOC0036^CSSYN^1.2.840.113619.2.1^ISO", t16="C:\\E\\docs\\E\\b36.rtf"),
                                                        obx_tx(36, 1)]))
    ppn = "^".join(["PR02", "Muestra", "Jorge"] + [""] * 11 + [ts(37, 14)])
    b.append(base(37, "TXA-13, TXA-21, TXA-22 y TXA-23 valorados en un T02", ["campos sin destino: nota"], ["TXA-13", "TXA-21", "TXA-22", "TXA-23"],
                  cab(37, "elena") + orden(37, "DS") + [txa(37, "DS", t13="DOC0009^CSSYN", t21="Correccion de filiacion", t22=ppn, t23=PROF[3]),
                                                        obx_tx(37, 1)]))
    b.append(base(38, "TXA-2 local (ZX, definida por el usuario) y TXA-18 vacío", ["type literal sin system", "sin securityLabel"],
                  ["TXA-2", "TXA-18"],
                  cab(38, "begona", "O") + orden(38, "ZX") + [txa(38, "ZX", t18=None), obx_tx(38, 1)]))
    b.append(base(39, "PID con dos identificadores, SFT, EVN-4, MSH-18 UTF-8 y ñ en PID-5 y TXA-9", ["segmentos sin mapa", "UTF-8 en nombres"],
                  ["PID-3", "SFT", "EVN-4", "MSH-18", "PID-5", "TXA-9"],
                  [msh(39, msh18="UNICODE UTF-8"), "SFT|Sintetico SL^L^^^^CSSYN|1.0|DocSys|B39", evn(39, evn4="01"),
                   PIDS["begona"].replace("Begona", "Begoña"), pv1(39, "E")] + orden(39, "ED") +
                  [txa(39, "ED", t9="PR01^Ensayo^Ana^Begoña^^Dra"), obx_tx(39, 1)]))
    b.append(base(40, "Documento mínimo: solo TXA-1, 2, 3, 12 y 17 (DI), PV1|1|O, un OBX TX, sin COMMON_ORDER, TXA-19 vacío",
                  ["todos los opcionales vacíos"], ["TXA-6", "TXA-9", "TXA-10", "TXA-16", "TXA-18", "TXA-19", "PV1-3", "PV1-19"],
                  [msh(40), evn(40), PIDS["lucia"], "PV1|1|O", txa(40, "PR", tipico=False, t17="DI"), obx_tx(40, 1)]))
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


# ---------------------------------------------------------------------------- el corpus secundario (§5.2, Q-MD-D-1 b)
SEC = (("S01", 1, "T04", None), ("S02", 2, "T06", "DOC0902^CSSYN"), ("S03", 5, "T08", None), ("S04", 8, "T10", "DOC0908^CSSYN"))


def secundario():
    """S01..S04: B01, B02, B05 y B08 como T04, T06, T08 y T10 (estructura MDM_T02): cambian MSH-9.2, EVN-1, MSH-10 y, en T06 y T10,
    TXA-13, obligatorio ahí ([E9 CH09.txt:1417-1421]); el padre es otro documento, no el mismo. No entran en las 40 ni en la huella."""
    out = []
    for sid, n, ev, padre in SEC:
        src = BASES[n - 1]
        segs = []
        for s in src["segmentos"]:
            if s.startswith("MSH|"):
                s = s.replace("|MDM^T02^MDM_T02|MDM-B%02d|" % n, "|MDM^%s^MDM_T02|MDM-%s|" % (ev, sid))
            elif s.startswith("EVN|"):
                s = "EVN|" + ev + s[len("EVN|T02"):]
            elif s.startswith("TXA|") and padre:
                p = s.split("|") + [""] * 14
                p[13] = padre
                s = "|".join(p).rstrip("|")
            segs.append(s)
        out.append({"id": sid, "descripcion": "%s como MDM^%s%s" % (src["id"], ev, " con TXA-13" if padre else ""), "de": src["id"],
                    "evento": ev, "segmentos": segs})
    return out


SECUNDARIAS = secundario()


# ---------------------------------------------------------------------------- §5.1.3: la firma contra la mutación
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


def distintos(a, b):
    ca, cb = campos(a), campos(b)
    return {k for k in set(ca) | set(cb) if ca.get(k) != cb.get(k) and re.sub(r"\(\d+\)", "", k) not in NO_FIRMA}


def firma(bases=None):
    """Pares con menos de 3 campos distintos (sin MSH-7, MSH-10 ni EVN-2), o que solo difieren en los campos que ejercita una de las dos."""
    malos = []
    for a, b in itertools.combinations(bases or BASES, 2):
        dif = distintos(a, b)
        base_dif = {re.sub(r"\(\d+\)", "", k) for k in dif}
        if len(dif) < 3 or base_dif <= set(a["campos"]) or base_dif <= set(b["campos"]):
            malos.append((a["id"], b["id"], sorted(dif)))
    return malos


def firma_minima(bases=None):
    return min(((len(distintos(a, b)), a["id"], b["id"]) for a, b in itertools.combinations(bases or BASES, 2)))


# ---------------------------------------------------------------------------- cobertura (§5.2)
def _obx(b):
    """[(tipo, OBX-5 valorado, n de NTE que le siguen)] de los OBX de la base."""
    out = []
    for s in b["segmentos"]:
        p = s.split("|")
        if p[0] == "OBX":
            out.append([p[2] if len(p) > 2 else "", len(p) > 5 and bool(p[5]), 0])
        elif p[0] == "NTE" and out:
            out[-1][2] += 1
    return out


def cobertura(bases=None):
    """Las filas «cuenta» de PERFIL_GUIA_MDM (datos, no juicio): cada campo valorado en alguna base y, si es opcional en 2.5, vacío
    en alguna; «OBX-n (T)» se lee por tipo (valorado: una base con un OBX de tipo T; vacío: una sin él). Y las ramas de §5.2. -> [faltas]."""
    bases = bases or BASES
    sys.path.insert(0, AQUI)
    _argv, sys.argv = sys.argv, ["x", "--silencio"]
    import conversion_mdm as CVM
    import estructuras_hl7 as EH
    sys.argv = _argv
    cs = [{re.sub(r"\(\d+\)", "", k) for k in campos(b)} for b in bases]
    segs = [{s.split("|")[0] for s in b["segmentos"]} for b in bases]
    tipos = [{t for t, v, _ in _obx(b) if v} for b in bases]
    faltas = []
    for fila in CVM.PERFIL_GUIA_MDM:
        if fila["nivel"] != "cuenta" or fila["campo"] == "—":
            continue
        for parte in fila["campo"].split("/"):
            m = re.match(r"^(OBX-\d+) \((\w+)\)$", parte)
            if m:
                if not any(m.group(2) in t for t in tipos):
                    faltas.append("%s: ninguna base con OBX %s" % (fila["elemento"], m.group(2)))
                if not any(m.group(2) not in t for t in tipos):
                    faltas.append("%s: ninguna base sin OBX %s" % (fila["elemento"], m.group(2)))
                continue
            if "-" not in parte:                                     # un segmento
                if not any(parte in s for s in segs):
                    faltas.append("%s: ninguna base con %s" % (fila["elemento"], parte))
                if parte in ("ORC", "OBR") and not any(parte not in s for s in segs):
                    faltas.append("%s: ninguna base sin %s (COMMON_ORDER es opcional)" % (fila["elemento"], parte))
                continue
            if not any(parte in c for c in cs):
                faltas.append("%s: ninguna base con %s valorado" % (fila["elemento"], parte))
            opt = (EH.CAMPOS.get(parte) or {}).get("opt")
            if opt != "R" and parte != "OBX-5" and not any(parte not in c for c in cs):
                faltas.append("%s: ninguna base con %s vacío" % (fila["elemento"], parte))
    val = lambda campo: {campos(b).get(campo, "").split("^")[0] for b in bases}  # noqa: E731
    for nombre, campo, esperados in (("0271", "TXA-17", T0271), ("0272 y vacío", "TXA-18", T0272 | {""}),
                                     ("0273 y vacío", "TXA-19", T0273 | {""}), ("0191 de TXA-3", "TXA-3", {"TEXT", "AP", "IM", "multipart"})):
        if not esperados <= val(campo):
            faltas.append("%s: faltan %s en %s" % (nombre, sorted(esperados - val(campo)), campo))
    ed4 = {r.split("^")[3].upper() for b in bases for s in b["segmentos"] if s.startswith("OBX|") and s.split("|")[2] == "ED"
           for r in s.split("|")[5].split("~")}
    if not T0299 <= ed4:
        faltas.append("0299: faltan %s en ED.4" % sorted(T0299 - ed4))
    if not {"TX", "FT", "ED", "RP", "CE", "ST"} <= set().union(*tipos):
        faltas.append("OBX-2: faltan %s" % sorted({"TX", "FT", "ED", "RP", "CE", "ST"} - set().union(*tipos)))
    cuentas = {"grupos de orden": ({sum(1 for s in b["segmentos"] if s.startswith("ORC|")) for b in bases}, {0, 1, 2, 3}),
               "NTE bajo OBX": ({max([x[2] for x in _obx(b)] or [0]) for b in bases}, {0, 1, 2}),
               "TXA-9": ({len([x for x in campos(b).get("TXA-9", "").split("~") if x]) for b in bases}, {0, 1, 2}),
               "TXA-10": ({len([x for x in campos(b).get("TXA-10", "").split("~") if x]) for b in bases}, {0, 1, 2})}
    for nombre, (hay, quiero) in cuentas.items():
        if not quiero <= hay:
            faltas.append("%s: faltan %s" % (nombre, sorted(quiero - hay)))
    return faltas


# ---------------------------------------------------------------------------- autoprueba (§5.1.4)
def _ed5_valido(ed4, ed5):
    e4 = ed4.upper()
    try:
        if e4 == "BASE64":
            base64.b64decode(ed5, validate=True)
        elif e4 == "HEX":
            bytes.fromhex(ed5)
        elif e4 == "A":
            ed5.encode("ascii")
        else:
            return False
    except (binascii.Error, ValueError, UnicodeEncodeError):
        return False
    return True


def comprobar(b, MR, EH, PE, mira, pe):
    """Lo de §5.1.4 para una base (o una secundaria, con el punto que la acepta)."""
    i = b["id"]
    ms = MR.mensajes(cable(b))
    mira("%s: un mensaje" % i, len(ms) == 1)
    if len(ms) != 1:
        return
    m = ms[0]
    mira("%s: estructura MDM_T02" % i, PE.estructura_de(m, pe) == "MDM_T02")
    r = EH.emparejar([s.split(m.f)[0] for s in m.segs], EH.gramatica("MDM_T02"), "MDM_T02")
    mira("%s: sin ausentes ni fuera de orden %r" % (i, (r["faltan"], r["fuera_de_orden"])), not r["faltan"] and not r["fuera_de_orden"])
    c = campos(b)
    mira("%s: EVN-1 = MSH-9.2" % i, c.get("EVN-1") == c.get("MSH-9", "").split("^")[1])
    mira("%s: texto no ASCII solo con MSH-18 UNICODE UTF-8" % i, cable(b).isascii() or c.get("MSH-18") == "UNICODE UTF-8")
    for k, v in c.items():
        campo = re.sub(r"\(\d+\)", "", k)
        at = EH.CAMPOS.get(campo) or {}
        for rep in v.split("~"):
            if at.get("dt") == "TS":
                mira("%s %s TS %r" % (i, k, rep), MR.partes_dtm(rep.split("^")[0])[0] is not None)
        cod = v.split("^")[0]
        for campo_t, tabla in (("TXA-3", T0191), ("TXA-17", T0271), ("TXA-18", T0272), ("TXA-19", T0273), ("OBX-2", T0125)):
            if campo == campo_t:
                mira("%s %s %r en su tabla" % (i, k, cod), cod.upper() in tabla)
        if campo in ("PID-5", "TXA-5", "TXA-9", "TXA-10", "TXA-11", "TXA-22", "TXA-23", "ORC-12", "OBR-16"):
            for rep in v.split("~"):
                fam = rep.split("^")[0 if campo == "PID-5" else 1]
                mira("%s %s apellido sintético %r" % (i, k, fam), fam in APELLIDOS)
        if campo == "TXA-22":
            mira("%s TXA-22.15 TS" % i, MR.partes_dtm(v.split("^")[14])[0] is not None)
        if campo == "TQ1-7":
            mira("%s TQ1-7 TS" % i, MR.partes_dtm(v)[0] is not None)
    tx = [s for s in b["segmentos"] if s.startswith("TXA|")][0]
    t = {n: v for n, v in enumerate(tx.split("|")) if v}
    mira("%s: TXA-3 con OBX (C, [E9 CH09.txt:886-890])" % i, 3 in t)                  # DV-MD-6: las condiciones de TXA
    mira("%s: TXA-7 con TXA-17 distinto de DI (C, [E9 CH09.txt:1030-1035])" % i, t.get(17) == "DI" or 7 in t)
    mira("%s: TXA-11 en un documento transcrito (C, TXA-11)" % i, 7 not in t or 11 in t)
    mira("%s: TXA-5 con TXA-4 (C, TXA-5)" % i, 4 not in t or 5 in t)
    for rep in [x for x in t.get(22, "").split("~") if x] or ([""] if t.get(17) in ("AU", "LA") else []):   # DV-MD-7
        q = (rep.split("^") + [""] * 15)[:15]
        mira("%s: TXA-22 con persona y fecha%s (C, [E9 CH09.txt:1795-1800])" % (i, " con TXA-17 %s" % t.get(17) if t.get(17) in ("AU", "LA") else ""),
             bool(q[0] or q[1]) and MR.partes_dtm(q[14])[0] is not None)
    for s in b["segmentos"]:
        p = s.split("|")
        if p[0] == "OBX" and p[2] in ("ED", "RP"):
            for rep in p[5].split("~"):
                q = rep.split("^")
                mira("%s %s.2/RP.3 %r en la 0191" % (i, p[2], q[1] if p[2] == "ED" else q[2]), (q[1] if p[2] == "ED" else q[2]).upper() in T0191)
                sub = q[2] if p[2] == "ED" else q[3]
                mira("%s %s.3/RP.4 %r en la 0291 o vacío" % (i, p[2], sub), not sub or sub.upper() in T0291)
                if p[2] == "ED":
                    mira("%s ED.4 %r en la 0299" % (i, q[3]), q[3].upper() in T0299)
                    ed5 = m.desescapa(q[4]) if len(q) > 4 else ""
                    mira("%s ED.5 válido para ED.4 %r y de 65536 caracteres como mucho" % (i, q[3]), _ed5_valido(q[3], ed5) and len(q[4]) <= 65536)


def autoprueba():
    sys.path.insert(0, AQUI)
    _argv, sys.argv = sys.argv, ["x", "--silencio"]
    import estructuras_hl7 as EH
    import mapeador_referencia as MR
    import puntos_entrada as PE
    sys.argv = _argv
    ok, n = [], [0]

    def mira(nombre, cond):
        n[0] += 1
        if not cond:
            ok.append(nombre)
            print("  MAL", nombre)
    for b in BASES:
        comprobar(b, MR, EH, PE, mira, PE.PUNTOS["mdm_conv"])
    mira("40 bases B01..B40", [b["id"] for b in BASES] == ["B%02d" % k for k in range(1, 41)])
    for b in SECUNDARIAS:                                            # con el punto de acuse mdm, que acepta T04…T10 como MDM_T02
        comprobar(b, MR, EH, PE, mira, PE.PUNTOS["mdm"])
        if b["evento"] in ("T06", "T10"):
            mira("%s: TXA-13 en %s ([E9 CH09.txt:1417-1421])" % (b["id"], b["evento"]), bool(campos(b).get("TXA-13")))
    malos = firma()
    mira("firma: todo par con ≥ 3 campos distintos %r" % malos[:3], not malos)
    faltas = cobertura()
    mira("cobertura %r" % faltas[:3], not faltas)
    mira("determinismo: dos construcciones iguales", huella(construir()) == huella())
    if HUELLA:
        mira("huella del conjunto fijada", huella() == HUELLA)
    else:
        print("  (huella del conjunto sin fijar: %s)" % huella())
    print("AUTOPRUEBA DE bases_mdm: %s (%d comprobaciones, %d bases)" % ("TODO BIEN" if not ok else "%d MAL" % len(ok), n[0], len(BASES)))
    return not ok


def longitudes():
    """Los campos que pasan de la longitud máxima de v2.5 (informativo: la autoprueba no lo exige, §5.1.4)."""
    sys.path.insert(0, AQUI)
    _argv, sys.argv = sys.argv, ["x", "--silencio"]
    import estructuras_hl7 as EH
    sys.argv = _argv
    out = []
    for b in BASES:
        for k, v in campos(b).items():
            ln = (EH.CAMPOS.get(re.sub(r"\(\d+\)", "", k)) or {}).get("len")
            for rep in v.split("~"):
                if ln and len(rep) > ln:
                    out.append((b["id"], k, len(rep), ln))
    return out


def escribir(bases, carpeta, indice, pref):
    os.makedirs(carpeta, exist_ok=True)
    with open(indice, "w", encoding="utf-8") as idx:
        for b in bases:
            with open(os.path.join(carpeta, b["id"] + ".hl7"), "w", encoding="utf-8", newline="") as f:
                f.write(cable(b))
            idx.write(json.dumps({"id": b["id"], "descripcion": b["descripcion"], "ejercita": b.get("ejercita"), "campos": b.get("campos"),
                                  "de": b.get("de"), "fichero": "%s/%s.hl7" % (os.path.basename(carpeta), b["id"]), "msh10": "MDM-" + b["id"],
                                  "segmentos": len(b["segmentos"])}, ensure_ascii=False) + "\n")
    return len(bases)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--lista"]:
        for b in BASES:
            print(b["id"], b["descripcion"])
    elif sys.argv[1:2] == ["--firma"]:
        malos = firma()
        print("\n".join("%s %s: %r" % x for x in malos) or "firma: todo par con 3 o más campos distintos (mínimo %d, %s-%s)" % firma_minima())
        sys.exit(1 if malos else 0)
    elif sys.argv[1:2] == ["--cobertura"]:
        f = cobertura()
        print("\n".join(f) or "cobertura completa")
        sys.exit(1 if f else 0)
    elif sys.argv[1:2] == ["--secundario"]:
        print("escritas %d bases secundarias en %s y %s" % (escribir(SECUNDARIAS, CARPETA_SEC, INDICE_SEC, "S"), CARPETA_SEC, INDICE_SEC))
    elif sys.argv[1:2] == ["--longitudes"]:
        print("\n".join("%s %s: %d > %d" % x for x in longitudes()) or "ningún campo pasa de su longitud")
    elif sys.argv[1:2] == ["--autoprueba"]:
        sys.exit(0 if autoprueba() else 1)
    else:
        print("escritas %d bases en %s y %s; huella %s" % (escribir(BASES, CARPETA, INDICE, "B"), CARPETA, INDICE, huella()[:12]))
