#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Las 40 bases ORU sintéticas de diseno-oru-fable.md §6 O4 (brazo 0, estrato E1): mensajes VÁLIDOS (todas AA en oru_fhir);
la batería de errores se deriva de ellas en O4 (y prueba_oru.py las muta para O0b). Pacientes ficticios. Deterministas.

Qué ejercitan (§6 O4): química NM+UCUM+rango+flags; micro CE/ST; SN `>^100`, `1^-^5`, `1^:^10`; TX en párrafos; TS; CE «^texto»;
CWE en 2.6; OBX-11 F/P/C/X/W/D/R/I; 2-3 OBR; NTE; SPM+OBX; escapes \\S\\ y UTF-8 en OBX-3.2/OBX-5; «01.20», «-0.5», «.5»; sin PID;
sin OBX; OBX-14 vacío con OBR-7.

Escribe bases_oru/BNN.hl7 (segmentos separados por CR, sin MLLP) y bases_oru.jsonl (id, descripcion, ejercita, fichero).
Aquí NO se escribe ningún canónico esperado (lo calcula un oráculo a ciegas en O1).

Uso: python3 bases_oru.py            escribe los ficheros
     python3 bases_oru.py --lista    imprime id y descripción"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CARPETA = os.path.join(AQUI, "bases_oru")
INDICE = os.path.join(AQUI, "bases_oru.jsonl")


def msh(n, ver="2.5", msh18="", ev="R01", est="ORU_R01", m15="", m16=""):
    return "MSH|^~\\&|LABSYS|HOSPSYN|LABORU|LAB|20230104%02d1500||ORU^%s^%s|ORU-B%02d|P|%s|||%s|%s||%s" % (
        8 + n % 12, ev, est, n, ver, m15, m16, msh18)


PIDS = {
    "ana": "PID|1||SYN0001^^^HOSPSYN^PI~MRN00001^^^HOSPSYN^MR||Prueba^Ana^^^^^L||19800315|F",
    "luis": "PID|1||MRN00002^^^HOSPSYN^MR||Sintetico^Luis^Maria^^^^L||19751120|M",
    "sinmr": "PID|1||SYN0003^^^HOSPSYN^PI~SYN0003B^^^OTRO^PI||Ficticia^Carmen^^^^^L||19900101|F",
    "eva": "PID|1||MRN00004^^^HOSPSYN^MR||Ejemplo^Eva^^^^^L||20000229|F",
}
OBR_QUIM = "OBR|1|PL-%02d|FL-%02d|24323-8^Panel metabolico basico^LN|||20230104073000|||||||||||||||20230104091500|||F"
OBR_HEMO = "OBR|2|PL-%02dB|FL-%02dB|58410-2^Hemograma^LN|||20230104073000|||||||||||||||20230104100000|||F"
OBR_MICRO = "OBR|1|PL-%02d|FL-%02d|600-7^Cultivo de sangre^LN|||20230103120000|||||||||||||||20230104160000|||F"
OBR_COAG = "OBR|3|PL-%02dC|FL-%02dC|34714-6^INR^LN|||20230104073000|||||||||||||||20230104101500|||F"


def obx(j, tipo, cod, val, uni="", rango="", flag="", st="F", t14="20230104080000", sub=""):
    return "OBX|%d|%s|%s|%s|%s|%s|%s|%s|||%s|||%s" % (j, tipo, cod, sub, val, uni, rango, flag, st, t14)


GLU = "2345-7^Glucosa^LN"
CREA = "2160-0^Creatinina^LN"
NA = "2951-2^Sodio^LN"
HB = "718-7^Hemoglobina^LN"
LEU = "6690-2^Leucocitos^LN"
PLQ = "777-3^Plaquetas^LN"
INR = "34714-6^INR^LN"
MGDL = "mg/dL^mg/dL^UCUM"
MMOLL = "mmol/L^mmol/L^UCUM"
GDL = "g/dL^g/dL^UCUM"
KUL = "10*3/uL^10*3/uL^UCUM"


def quimica(n, extra=None):
    return [obx(1, "NM", GLU, "95", MGDL, "70-110", "N"), obx(2, "NM", CREA, "1.1", MGDL, "0.7-1.3", "N"),
            obx(3, "NM", NA, "142", MMOLL, "136-145", "N")] + (extra or [])


def base(n, descripcion, ejercita, segs):
    return {"id": "B%02d" % n, "descripcion": descripcion, "ejercita": ejercita, "segmentos": segs}


def construir():
    b = []
    b.append(base(1, "Química básica: 1 OBR, 3 OBX NM con UCUM, rango y flag N, finales", ["NM", "UCUM", "rango", "flags", "F", "OBX-14"],
                  [msh(1), PIDS["ana"], OBR_QUIM % (1, 1)] + quimica(1)))
    b.append(base(2, "Química con valores altos: flags H y HH, rangos con < y >", ["NM", "flags H/HH", "rango textual"],
                  [msh(2), PIDS["luis"], OBR_QUIM % (2, 2), obx(1, "NM", GLU, "260", MGDL, "70-110", "HH"), obx(2, "NM", CREA, "2.4", MGDL, "<1.3", "H"),
                   obx(3, "NM", NA, "131", MMOLL, ">135", "L")]))
    b.append(base(3, "Dos OBR (química + hemograma), 3 + 3 OBX", ["2 OBR", "pertenencia OBX->OBR", "NM"],
                  [msh(3), PIDS["ana"], OBR_QUIM % (3, 3)] + quimica(3) + [OBR_HEMO % (3, 3), obx(1, "NM", HB, "13.5", GDL, "12-16", "N"),
                   obx(2, "NM", LEU, "7.2", KUL, "4-10", "N"), obx(3, "NM", PLQ, "250", KUL, "150-400", "N")]))
    b.append(base(4, "Tres OBR (química, hemograma, coagulación) con OBX-1 reiniciado por OBR", ["3 OBR", "OBX-1 por grupo", "identificadores i.j"],
                  [msh(4), PIDS["luis"], OBR_QUIM % (4, 4), obx(1, "NM", GLU, "88", MGDL, "70-110", "N"), OBR_HEMO % (4, 4),
                   obx(1, "NM", HB, "14.1", GDL, "12-16", "N"), obx(2, "NM", LEU, "5.5", KUL, "4-10", "N"), OBR_COAG % (4, 4),
                   obx(1, "NM", INR, "1.1", "", "0.8-1.2", "N")]))
    b.append(base(5, "Microbiología: organismo CE (SCT) + antibiograma ST con flags S/R/I", ["CE", "ST", "flags S/R/I", "SCT"],
                  [msh(5), PIDS["eva"], OBR_MICRO % (5, 5), obx(1, "CE", "630-4^Microorganismo identificado^LN", "3092008^Staphylococcus aureus^SCT", st="F"),
                   obx(2, "ST", "18906-8^Ciprofloxacino^LN", "Sensible", "", "", "S", sub="1"), obx(3, "ST", "18928-2^Penicilina^LN", "Resistente", "", "", "R", sub="1"),
                   obx(4, "ST", "18878-9^Cefazolina^LN", "Intermedio", "", "", "I", sub="1")]))
    b.append(base(6, "SN con comparador: >^100 (valueQuantity con comparator)", ["SN", "comparador >", "quantity"],
                  [msh(6), PIDS["ana"], OBR_QUIM % (6, 6), obx(1, "SN", GLU, ">^100", MGDL, "70-110", "H")]))
    b.append(base(7, "SN rango: ^1^-^5 (valueRange)", ["SN", "separador -", "range"],
                  [msh(7), PIDS["ana"], OBR_QUIM % (7, 7), obx(1, "SN", "5778-6^Color de orina^LN", "^1^-^5", "", "", "N")]))
    b.append(base(8, "SN cociente: ^1^:^10 (valueRatio) y titulación ^1^/^64", ["SN", "separador : y /", "ratio"],
                  [msh(8), PIDS["luis"], OBR_MICRO % (8, 8), obx(1, "SN", "5193-8^Anticuerpos VHB^LN", "^1^:^10", "", "", "N"),
                   obx(2, "SN", "22314-9^Titulo^LN", "^1^/^64", "", "", "A")]))
    b.append(base(9, "SN <^5 (quantity con <) y <>^5 (valueString crudo)", ["SN", "comparador <", "comparador <> -> string"],
                  [msh(9), PIDS["eva"], OBR_QUIM % (9, 9), obx(1, "SN", "1988-5^PCR^LN", "<^5", "mg/L^mg/L^UCUM", "<5", "N"), obx(2, "SN", "1988-5^PCR^LN", "<>^5", "mg/L^mg/L^UCUM", "", "", sub="2")]))
    b.append(base(10, "TX con dos repeticiones (párrafos, D-ORU-3)", ["TX", "repeticiones = párrafos"],
                  [msh(10), PIDS["ana"], OBR_MICRO % (10, 10), obx(1, "TX", "6463-4^Comentario de cultivo^LN", "Crecimiento escaso a las 24 h.~Se recomienda repetir la toma.", st="F")]))
    b.append(base(11, "FT con formato \\.br\\ conservado literal", ["FT", "formato literal"],
                  [msh(11), PIDS["luis"], OBR_MICRO % (11, 11), obx(1, "FT", "6463-4^Comentario de cultivo^LN", "Primera linea\\.br\\Segunda linea", st="F")]))
    b.append(base(12, "TS como valor (fecha y hora de la toma) -> valueDateTime (AMB-ORU-1)", ["TS", "datetime"],
                  [msh(12), PIDS["ana"], OBR_QUIM % (12, 12), obx(1, "TS", "33882-2^Fecha de toma^LN", "20230104071500", st="F")]))
    b.append(base(13, "DT (fecha) y TM (hora) como valores", ["DT", "TM", "date/time"],
                  [msh(13), PIDS["eva"], OBR_QUIM % (13, 13), obx(1, "DT", "11778-8^Fecha probable^LN", "20230601", st="F"), obx(2, "TM", "8601-7^Hora de la toma^LN", "0715", st="F")]))
    b.append(base(14, "CE solo texto «^texto» (AMB-ORU-4)", ["CE ^texto", "display sin code"],
                  [msh(14), PIDS["ana"], OBR_MICRO % (14, 14), obx(1, "CE", "71020&IMP^Impresion^L", "^Insuficiencia cardiaca congestiva", st="F")]))
    b.append(base(15, "CWE en un mensaje 2.6 (S22: tratado como CE; CWE.9 texto original)", ["2.6", "CWE", "S22"],
                  [msh(15, ver="2.6"), PIDS["luis"], OBR_MICRO % (15, 15), obx(1, "CWE", "630-4^Microorganismo identificado^LN", "112283007^Escherichia coli^SCT^^^^^^E. coli", st="F")]))
    b.append(base(16, "OBX-11 P (preliminar)", ["OBX-11 P"],
                  [msh(16), PIDS["ana"], OBR_QUIM.replace("|||F", "|||P") % (16, 16), obx(1, "NM", GLU, "101", MGDL, "70-110", "N", "P")]))
    b.append(base(17, "OBX-11 C (corrección) con OBR-25 C", ["OBX-11 C", "OBR-25 C"],
                  [msh(17), PIDS["ana"], OBR_QUIM.replace("|||F", "|||C") % (17, 17), obx(1, "NM", GLU, "97", MGDL, "70-110", "N", "C")]))
    b.append(base(18, "OBX-11 X con OBX-2 y OBX-5 vacíos (no se pudo obtener)", ["OBX-11 X", "sin valor", "OBX-2 vacío legal"],
                  [msh(18), PIDS["eva"], OBR_QUIM % (18, 18), obx(1, "", GLU, "", "", "", "", "X"), obx(2, "NM", CREA, "1.0", MGDL, "0.7-1.3", "N")]))
    b.append(base(19, "OBX-11 W (resultado erróneo)", ["OBX-11 W"],
                  [msh(19), PIDS["luis"], OBR_QUIM % (19, 19), obx(1, "NM", GLU, "95", MGDL, "70-110", "N", "W")]))
    b.append(base(20, "OBX-11 D (orden de borrado, AMB-ORU-6)", ["OBX-11 D"],
                  [msh(20), PIDS["luis"], OBR_QUIM % (20, 20), obx(1, "NM", GLU, "95", MGDL, "70-110", "N", "D")]))
    b.append(base(21, "OBX-11 R (entrado, no verificado; S62) con OBR-25 R", ["OBX-11 R", "S62", "OBR-25 R"],
                  [msh(21), PIDS["ana"], OBR_QUIM.replace("|||F", "|||R") % (21, 21), obx(1, "NM", GLU, "95", MGDL, "70-110", "N", "R")]))
    b.append(base(22, "OBX-11 I (muestra en laboratorio, pendiente; S62) con OBR-25 I", ["OBX-11 I", "S62", "OBR-25 I"],
                  [msh(22), PIDS["eva"], OBR_QUIM.replace("|||F", "|||I") % (22, 22), obx(1, "", GLU, "", "", "", "", "I")]))
    b.append(base(23, "NTE tras el OBR y tras los OBX (L-ORU-4: se cuentan)", ["NTE", "NumNte"],
                  [msh(23), PIDS["ana"], OBR_QUIM % (23, 23), "NTE|1|L|Muestra hemolizada", obx(1, "NM", GLU, "95", MGDL, "70-110", "N"),
                   "NTE|1|L|Valor confirmado por repeticion", "NTE|2|L|Segunda nota", obx(2, "NM", CREA, "1.1", MGDL, "0.7-1.3", "N")]))
    b.append(base(24, "SPM con OBX de muestra (L-ORU-5: no se consumen)", ["SPM", "OBX bajo SPM", "NumObxEspecimen"],
                  [msh(24), PIDS["luis"], OBR_QUIM % (24, 24), obx(1, "NM", GLU, "95", MGDL, "70-110", "N"), "SPM|1|SPM-24^LABSYS||119297000^Sangre venosa^SCT",
                   obx(1, "ST", "93048-0^Aspecto de la muestra^LN", "Hemolizada", st="F")]))
    b.append(base(25, "Escapes \\S\\, \\T\\ y \\F\\ en OBX-5 (ST) y \\S\\ en OBX-3.2", ["escapes §2.7", "OBX-3.2", "OBX-5"],
                  [msh(25), PIDS["ana"], OBR_MICRO % (25, 25), obx(1, "ST", "6463-4^Comentario \\S\\ cultivo^LN", "Escaso \\T\\ lento \\F\\ ver nota \\S\\ 2", st="F")]))
    b.append(base(26, "UTF-8 (ñ, á, –) en OBX-3.2 y OBX-5 con MSH-18 UNICODE UTF-8", ["UTF-8", "S38", "MSH-18"],
                  [msh(26, msh18="UNICODE UTF-8"), PIDS["eva"], OBR_QUIM % (26, 26), obx(1, "NM", "2345-7^Glucosa en ayunas – mañana^LN", "95", MGDL, "70-110", "N"),
                   obx(2, "ST", "6463-4^Comentario^LN", "Muestra tomada tras 8 h de ayuno; señal débil.", st="F")]))
    b.append(base(27, "NM «01.20» (cero inicial superfluo, D-ORU-2)", ["NM 01.20", "D-ORU-2"],
                  [msh(27), PIDS["ana"], OBR_QUIM % (27, 27), obx(1, "NM", CREA, "01.20", MGDL, "0.7-1.3", "N")]))
    b.append(base(28, "NM «-0.5» (negativo)", ["NM -0.5", "signo"],
                  [msh(28), PIDS["luis"], OBR_QUIM % (28, 28), obx(1, "NM", "1925-7^Exceso de base^LN", "-0.5", MMOLL, "-2-2", "N")]))
    b.append(base(29, "NM «.5» (sin cero, AMB-ORU-3) y «5.»", ["NM .5", "NM 5.", "AMB-ORU-3"],
                  [msh(29), PIDS["eva"], OBR_QUIM % (29, 29), obx(1, "NM", "1988-5^PCR^LN", ".5", "mg/L^mg/L^UCUM", "<5", "N"), obx(2, "NM", NA, "5.", MMOLL, "", "")]))
    b.append(base(30, "ORU sin PID (PATIENT opcional; S60: AA sin subject)", ["sin PID", "S60"],
                  [msh(30), OBR_QUIM % (30, 30), obx(1, "NM", GLU, "95", MGDL, "70-110", "N")]))
    b.append(base(31, "ORU sin OBX (solo OBR; S55: AA, informe sin observaciones)", ["sin OBX", "S55"],
                  [msh(31), PIDS["ana"], OBR_QUIM.replace("|||F", "|||I") % (31, 31)]))
    b.append(base(32, "OBX-14 vacío con OBR-7 (S63: effective = OBR-7)", ["OBX-14 vacío", "S63", "OBR-7"],
                  [msh(32), PIDS["luis"], OBR_QUIM % (32, 32), obx(1, "NM", GLU, "95", MGDL, "70-110", "N", t14=""), obx(2, "NM", CREA, "1.1", MGDL, "0.7-1.3", "N", t14="")]))
    b.append(base(33, "OBX-14 y OBR-7 vacíos (sin effective; OBR-7 C solo nota L-MT6)", ["OBX-14 vacío", "OBR-7 vacío", "FechaOrigen ninguna"],
                  [msh(33), PIDS["ana"], OBR_QUIM.replace("|||20230104073000|", "||||") % (33, 33), obx(1, "NM", GLU, "95", MGDL, "70-110", "N", t14="")]))
    b.append(base(34, "OBR-25 vacío (S64: DiagnosticReport.status unknown)", ["OBR-25 vacío", "S64"],
                  [msh(34), PIDS["eva"], OBR_QUIM.replace("|||F", "|||") % (34, 34), obx(1, "NM", GLU, "95", MGDL, "70-110", "N")]))
    b.append(base(35, "OBR-22 sin segundos (D-ORU-5: issued omitido) y OBR-8 (effectivePeriod)", ["OBR-22 minutos", "D-ORU-5", "OBR-8"],
                  [msh(35), PIDS["ana"], "OBR|1|PL-35|FL-35|24323-8^Panel metabolico basico^LN|||20230104073000|20230104074500||||||||||||||202301040915|||F",
                   obx(1, "NM", GLU, "95", MGDL, "70-110", "N")]))
    b.append(base(36, "OBX-5 NM repetido 95~96 (L-ORU-3: primera + RepeticionesPerdidas)", ["OBX-5 repetido", "L-ORU-3"],
                  [msh(36), PIDS["luis"], OBR_QUIM % (36, 36), obx(1, "NM", GLU, "95~96", MGDL, "70-110", "N")]))
    b.append(base(37, "ORC + OBR y OBX-4 sub-id (L-ORU-6)", ["ORC", "OBX-4", "SubId"],
                  [msh(37), PIDS["ana"], "ORC|RE|PL-37|FL-37", OBR_QUIM % (37, 37), obx(1, "NM", GLU, "95", MGDL, "70-110", "N", sub="1.1"), obx(2, "NM", CREA, "1.1", MGDL, "0.7-1.3", "N", sub="1.2")]))
    b.append(base(38, "PD1, NK1 y PV1 (VISIT) presentes; PID-3 sin MR (se elige la primera no vacía)", ["PD1/NK1/PV1", "PID-3 sin MR"],
                  [msh(38), PIDS["sinmr"], "PD1|||Centro Sintetico", "NK1|1|Ficticio^Pedro^^^^^L|SPO", "PV1|1|O|CONS-3", OBR_QUIM % (38, 38),
                   obx(1, "NM", GLU, "95", MGDL, "70-110", "N")]))
    b.append(base(39, "DTM con zona explícita +0200 y fracción; OBX-11 f en minúscula (S4); OBX-8 h minúscula", ["zona explícita", "fracción", "S4"],
                  [msh(39), PIDS["eva"], "OBR|1|PL-39|FL-39|24323-8^Panel metabolico basico^LN|||20230104073000+0200|||||||||||||||20230104091500.25+0200|||F",
                   obx(1, "NM", GLU, "120", MGDL, "70-110", "h", "f", "20230104080000.5+0200")]))
    b.append(base(40, "Tipo XPN no soportado (L-ORU-2) y OBR-4 con código alternativo (CE.4-6) y sistema local L", ["no_soportado", "CE.4-6", "sistema L"],
                  [msh(40), PIDS["luis"], "OBR|1|PL-40|FL-40|24323-8^Panel metabolico basico^LN^PMB^Panel basico^L|||20230104073000|||||||||||||||20230104091500|||F",
                   obx(1, "XPN", "18767-4^Observador^L", "Observador^Sintetico", st="F"), obx(2, "NM", GLU, "95", MGDL, "70-110", "N")]))
    assert [x["id"] for x in b] == ["B%02d" % i for i in range(1, 41)]
    return b


BASES = construir()


def cable(b):
    """El mensaje como va por el cable: segmentos separados por CR (sin MLLP)."""
    return "\r".join(b["segmentos"]) + "\r"


def escribir():
    os.makedirs(CARPETA, exist_ok=True)
    with open(INDICE, "w", encoding="utf-8") as idx:
        for b in BASES:
            ruta = os.path.join(CARPETA, b["id"] + ".hl7")
            with open(ruta, "w", encoding="utf-8", newline="") as f:
                f.write(cable(b))
            idx.write(json.dumps({"id": b["id"], "descripcion": b["descripcion"], "ejercita": b["ejercita"],
                                  "fichero": "bases_oru/%s.hl7" % b["id"], "msh10": "ORU-" + b["id"], "segmentos": len(b["segmentos"])},
                                 ensure_ascii=False) + "\n")
    return len(BASES)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--lista"]:
        for b in BASES:
            print(b["id"], b["descripcion"])
    else:
        print("escritas %d bases en %s y %s" % (escribir(), CARPETA, INDICE))
