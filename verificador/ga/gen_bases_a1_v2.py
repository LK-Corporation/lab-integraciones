# Generado por ga/hacer_resto_v2.py desde a1/gen_bases_a1.py (etapa 33). No editar a mano.
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa ADT, A1 (diseño §8 b): 40 bases propias POR CONSTRUCCIÓN (8 eventos × 5 familias) para las reglas que las 216 bases
de E2 no ejercitan (medido con a1/cobertura_a1.py): PV1-2 vacío (S95), E/P/R/B/C/U, minúscula y fuera de tabla (S90);
PID-7 AAAAMM y con hora; PID-8 A/O/U/N, minúscula y fuera (S22); PID-3 con MR en 2.ª; FN con subcomponentes; PID-11 con
XAD.7 B y M; XTN.4 (correo), XTN.12 y PID-14; PID-16; PID-29/30; PV1-6, PV1-11, PV1-17, PV1-36; PV1-7 sin XCN.1; escapes;
MSH-12 2.5.1. Deterministas, sin azar. No se mira el oráculo para escribirlas.

  cd fase12 && python3 ga/gen_bases_a1_v2.py      -> ga/bases_a1_v2.json
"""
import json

EVENTOS = ["A01", "A02", "A03", "A04", "A08", "A11", "A13", "A31"]
ESTR = {"A01": "ADT_A01", "A04": "ADT_A01", "A08": "ADT_A01", "A13": "ADT_A01", "A02": "ADT_A02", "A03": "ADT_A03",
        "A11": "ADT_A09", "A31": "ADT_A05"}


def seg(nombre, campos):
    hasta = max(campos)
    return "|".join([nombre] + [campos.get(i, "") for i in range(1, hasta + 1)])


def mensaje(ev, i, fam, pid, pv1, ver="2.5", msh7="20260315103000"):
    msh = "MSH|^~\\&|HISA1|HOSP|LAB|LAB|%s||ADT^%s^%s|A1-%s-%s|P|%s" % (msh7, ev, ESTR[ev], ev, fam, ver)
    evn = "EVN|%s|%s" % (ev, msh7)
    return "\r".join([msh, evn, seg("PID", pid), seg("PV1", pv1)])


def bases():
    out = []
    clases = ["E", "P", "R", "B", "C", "U", "o", "X"]
    sexos = ["A", "O", "U", "N", "f", "X", "M", "F"]
    civil = ["A", "D", "M", "S", "W", "U", "T", "G"]
    for k, ev in enumerate(EVENTOS):
        mrn = "MR%03d" % k
        vis = "VN%03d^^^HOSP^VN" % k
        # 1. clases y repeticiones: PV1-2 de la 0004 (y minúscula, fuera), MR en 2.ª repetición, PID-7 AAAAMM, PID-8 variado
        out.append(("clases", mensaje(ev, k, "clases",
                    {1: "1", 3: "EXT%d^^^OTRO^PI~%s^^^HOSP^MR" % (k, mrn), 5: "Ruiz^Eva^^^^^L", 7: "198002", 8: sexos[k]},
                    {1: "1", 2: clases[k], 3: "PLANTA2^201^B^HOSP", 19: vis})))
        # 2. PV1-2 vacío (S95) con y sin PV1-45; PV1-44 con zona propia; PID-7 con hora
        pv1 = {1: "1", 3: "URG^1^A", 19: vis, 44: "202603140800+0200"}
        if ev in ("A03", "A13", "A08", "A11"):
            pv1[45] = "202603151200"
        out.append(("pv1_2_vacio", mensaje(ev, k, "pv12vacio",
                    {1: "1", 3: "%s^^^HOSP^MR" % mrn, 5: "Sanz^Luis Miguel^^^^^L", 7: "197512312359", 8: "M"}, pv1)))
        # 3. contactos y nombre: FN con subcomponentes, dos nombres, XAD.7 B y M, correo (XTN.4), XTN.12, PID-14, PID-16
        out.append(("contactos", mensaje(ev, k, "contactos",
                    {1: "1", 3: "%s^^^HOSP^MR" % mrn, 5: "de&la&Fuente^Ana^Maria^^Dra^^L~Anita^^^^^^N", 7: "19900110", 8: "F",
                     11: "C/ Real 5&Piso 3&Puerta B^Esc 2^Toledo^TO^45001^ESP^B~Apdo 9^^Toledo^^45080^^M",
                     13: "^NET^Internet^ana@hosp.es~^PRN^PH^^^^^^^^^925000111", 14: "925999888^WPN^FX", 16: civil[k]},
                    {1: "1", 2: "I", 3: "PLANTA1^101^A", 19: vis})))
        # 4. visita completa: PV1-4/6/7 sin XCN.1/8 dos repeticiones/10/11/14/17/36; muerte por PID-29 o PID-30
        pid = {1: "1", 3: "%s^^^HOSP^MR" % mrn, 5: "Gil^Pedro^^^^^L", 7: "19400505", 8: "M"}
        if k % 2:
            pid[29] = "202603150930"
        else:
            pid[30] = "Y" if k % 4 == 0 else "N"
        out.append(("visita", mensaje(ev, k, "visita", pid,
                    {1: "1", 2: "I", 3: "UCI^3^1^HOSP^^^^^Box 3", 4: "R", 6: "URG^1^A", 7: "^DOCTORA^ELENA^^^Dra",
                     8: "D20^Ramos^Juan~D21^Otro^Ana", 10: "CAR", 11: "QUIROF^1", 14: "7", 17: "D30^Vega^Luz^^^Dr", 19: vis,
                     36: "01", 44: "202603100800", 45: "202603151000" if ev in ("A03", "A13") else ""})))
        # 5. escapes y versión 2.5.1: \S\ \T\ \F\ en nombre y ubicación; PID-8 fuera (S22); PV1-2 fuera (S90)
        out.append(("escapes_251", mensaje(ev, k, "escapes",
                    {1: "1", 3: "%s^^^HOSP^MR" % mrn, 5: "O\\S\\Neil\\T\\Co^Mary\\F\\Ann^^^^^L", 7: "19851224", 8: "Z"},
                    {1: "1", 2: "Z" if ev != "A31" else "I", 3: "PLANTA\\T\\4^401^A^^^^^^Sala \\S\\ norte", 19: vis},
                    ver="2.5.1")))
    return [{"id": "A1-%s-%02d" % (m.split("|")[9].split("-")[1], i), "familia": fam, "evento": m.split("|")[8].split("^")[1],
             "mensaje": m} for i, (fam, m) in enumerate(out)]


if __name__ == "__main__":
    b = bases()
    json.dump(b, open("ga/bases_a1_v2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(b), "bases en ga/bases_a1_v2.json")
