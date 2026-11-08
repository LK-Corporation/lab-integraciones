#!/usr/bin/env python3
"""Etapa 37 (jz/diseno-jz-fable.md §4 y §6): el clasificador del rejuicio, sobre juicios sintéticos. Cada caso cambia una cosa.
Segunda versión (8-nov, tras la revisión a ciegas): el clasificador mira el caso, no solo la forma del hallazgo. Los mensajes
llevan los valores de verdad, y entran los casos con forma de conducta que no lo son (jz/decision-jev-jz2.md, Q-JZ-7: la lectura
de NK1-15, aparte).

  python3 jz/prueba_rejuicio_jz.py        -> TODO BIEN si no hay ningún MAL"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
mal, n_ok = [], [0]


def mira(nombre, obtenido, esperado):
    if obtenido == esperado:
        n_ok[0] += 1
    else:
        print("  MAL %s: %r != %r" % (nombre, obtenido, esperado))
        mal.append(nombre)


def h(clase, subtipo, hecho, que, cuenta=True, citas=()):
    return {"clase": clase, "subtipo": subtipo, "hecho": hecho, "cuenta": cuenta, "que": que if isinstance(que, list) else [que],
            "citas": list(citas), "certeza": "literal", "nivel": None, "estado": "firme", "causa": None, "alternativa": None}


def juicio(cat, sub, hs, rec=None):
    return {"veredicto": {"categoria": cat, "subtipo": sub, "certeza": "literal", "alternativa": None, "provisional": False},
            "hallazgos": hs, "recuentos": rec or {"Patient": 1, "Encounter": 1}}


def seg(nombre, campos):
    n = max(campos) if campos else 0
    return "|".join([nombre] + [campos.get(i, "") for i in range(1, n + 1)])


MSH = "MSH|^~\\&|A|B|C|D|20260101||ADT^A01^ADT_A01|1|P|2.5"
PV1 = "PV1|1|I"


def adt(pid8, *mas):
    return "\r".join([MSH, seg("PID", {1: "1", 3: "X1", 8: pid8}), PV1] + list(mas))


VXU = "MSH|^~\\&|A|B|C|D|20260101||VXU^V04^VXU_V04|1|P|2.8"
CIT = ["[E3 Ch03.txt:5032-5044]"]
PV1_44 = h("fidelidad", "dato_inventado", "PV1-44", "Encounter.period.start presente sin PV1-44")
ACC1 = seg("ACC", {1: "20260102", 5: "Y"})
PDA3 = seg("PDA", {3: "Y", 9: "N"})
INV = "Observation urn:uuid:%s sin origen propio en el mensaje"
SM = "Observation urn:uuid:%s de %s (%s = '%s'%s), que la hoja de ADT_A01 de la guía lista sin destino"


def main():
    import rejuicio_jz as R
    S, M = adt("S"), adt("M")
    # ---- conducta 1, con un valor fuera de la 0001 de verdad
    a = juicio("fallo_silencioso", "convertido+aceptado_imposible",
               [h("valor_imposible_aceptado", "valor_imposible_convertido+fhir_invalido", "PID-8", "Patient.gender: 'S' convertido desde 'S'")])
    b = juicio("fallo_silencioso", "convertido", [h("fidelidad", "fhir_invalido", "PID-8", "Patient.gender: 'S' fuera de administrative-gender")])
    mira("conducta 1, Microsoft", R.clasificar(a, b, S, "adt_conv"), {"1"})
    a = juicio("fallo_silencioso", "convertido+aceptado_imposible",
               [h("valor_imposible_aceptado", "valor_imposible_convertido", "PID-8", "Patient.gender: 'unknown' convertido desde 'S'"), PV1_44])
    b = juicio("fallo_silencioso", "convertido",
               [h("nota", "convencion", "PID-8", "Patient.gender: 'unknown' para 'S', fuera del ConceptMap", cuenta=False, citas=CIT), PV1_44])
    mira("conducta 1, LinuxForHealth", R.clasificar(a, b, S, "adt_conv"), {"1"})
    a2 = juicio("fallo_silencioso", "aceptado_imposible", [h("valor_imposible_aceptado", "valor_imposible_convertido", "PID-8", "x")])
    b2 = juicio("correcto", None, [h("nota", "convencion", "PID-8", "Patient.gender: 'unknown' para 'S'", cuenta=False, citas=CIT)])
    mira("conducta 1, a correcto si no queda nada", R.clasificar(a2, b2, S, "adt_conv"), {"1"})
    a3 = juicio("fallo_silencioso", "convertido", [h("nota", "version", "PID-8", "valor imposible en 2.5.1", cuenta=False)])
    b3 = juicio("fallo_silencioso", "convertido", [h("nota", "version", "PID-8", "Patient.gender: 'unknown' para 'Z'", cuenta=False, citas=CIT)])
    mira("conducta 1, la nota de versión cambia de texto", R.clasificar(a3, b3, adt("Z"), "adt_conv"), {"1"})
    vxu_s = "\r".join([VXU, seg("PID", {8: "F"}), seg("NK1", {1: "1", 15: "M"}), seg("NK1", {1: "2", 15: "S"})])
    a = juicio("fallo_silencioso", "aceptado_imposible", [h("valor_imposible_aceptado", "valor_imposible_convertido", "NK1(2)-15", "x")])
    b = juicio("correcto", None, [h("nota", "convencion", "NK1(2)-15", "y", cuenta=False, citas=CIT)])
    mira("conducta 1, NK1(2)-15", R.clasificar(a, b, vxu_s, "vxu_conv"), {"1"})
    a1, b1 = (json.loads(json.dumps(x).replace("NK1(2)-15", "NK1-15")) for x in (a, b))
    mira("control: el mismo cambio en NK1-15 (el primero, = M, dentro de la 0001) es de fuera",
         R.clasificar(a1, b1, vxu_s, "vxu_conv"), {"fuera"})
    # ---- conducta 1, rechazo (Q-JZ-1 b)
    ra = juicio("correcto", None, [h("rechazo", "aceptable", "PID-8", "el conversor rechazó un mensaje con ['PID-8']: rechazo aceptable (Q-CV-D-7)", cuenta=False)])
    rb = juicio("rechazo_incorrecto", "error", [h("rechazo", "incorrecto", "MSH-9", "el conversor devolvió error 'x'")])
    mira("conducta 1, rechazo", R.clasificar(ra, rb, adt("X"), "adt_conv"), {"1"})
    mira("control: rechazo con PID-8 = M, dentro de la 0001, es de fuera", R.clasificar(ra, rb, M, "adt_conv"), {"fuera"})
    a3 = juicio("correcto", None, [h("rechazo", "aceptable", "PID-8", "el conversor rechazó un mensaje con ['PID-8', 'RXA-3']: rechazo aceptable (Q-CV-D-7)", cuenta=False)])
    b3 = juicio("correcto", None, [h("rechazo", "aceptable", "RXA-3", "el conversor rechazó un mensaje con ['RXA-3']: rechazo aceptable (Q-CV-D-7)", cuenta=False)])
    mira("conducta 1, rechazo que sigue aceptable por otro", R.clasificar(a3, b3, S.replace("ADT^A01^ADT_A01", "VXU^V04^VXU_V04"), "vxu_conv"), {"1"})
    a4 = juicio("correcto", None, [h("rechazo", "aceptable", "PID-7", "el conversor rechazó un mensaje con ['PID-7']: rechazo aceptable (Q-CV-D-7)", cuenta=False)])
    mira("control: un rechazo por PID-7 que cambia es de fuera", R.clasificar(a4, rb, S, "adt_conv"), {"fuera"})
    # ---- con forma de conducta 1, y no lo son (la revisión a ciegas)
    a7 = juicio("fallo_silencioso", "convertido", [PV1_44])
    b7 = juicio("fallo_silencioso", "convertido", [PV1_44, h("fidelidad", "fhir_invalido", "PID-8", "Patient.gender: 'm' fuera de administrative-gender")])
    mira("control: un fhir_invalido de más en PID-8 = M es de fuera", R.clasificar(a7, b7, M, "adt_conv"), {"fuera"})
    b8 = juicio("fallo_silencioso", "convertido", [PV1_44, h("nota", "convencion", "PID-8", "Patient.gender: 'male' para 'M'", cuenta=False, citas=CIT)])
    mira("control: una nota de convención de más en PID-8 = M es de fuera", R.clasificar(a7, b8, M, "adt_conv"), {"fuera"})
    b9 = juicio("fallo_silencioso", "convertido", [PV1_44, h("valor_imposible_aceptado", "valor_imposible_convertido", "PID-8", "x")])
    mira("control: un valor_imposible_convertido que entra (el juez nuevo no lo da) es de fuera", R.clasificar(a7, b9, S, "adt_conv"), {"fuera"})
    mira("control: PID-8 vacío y un hallazgo de PID-8, de fuera", R.clasificar(a7, b7, adt(""), "adt_conv"), {"fuera"})
    # ---- la lectura de NK1-15 (Q-JZ-7 b): un CWE de v2.8 que el juez lee entero, con el código dentro de la 0001
    vxu_cwe = "\r".join([VXU, seg("PID", {8: "M"}), seg("NK1", {1: "1", 15: "F^^^M"})])
    la = juicio("fallo_silencioso", "convertido", [h("nota", "version", "NK1-15", "valor imposible", cuenta=False)])
    lb = juicio("fallo_silencioso", "convertido", [h("nota", "version", "NK1-15", "RelatedPerson.gender: 'female' para 'F^^^M', fuera del ConceptMap",
                                                     cuenta=False, citas=CIT)])
    mira("la lectura de NK1-15 = F^^^M, aparte", R.clasificar(la, lb, vxu_cwe, "vxu_conv"), {"lectura"})
    lc = juicio("fallo_silencioso", "convertido", [h("fidelidad", "fhir_invalido", "NK1-15", "x")])
    mira("control: con F^^^M, un hallazgo que cuenta es de fuera", R.clasificar(la, lc, vxu_cwe, "vxu_conv"), {"fuera"})
    # ---- conducta 2: las mismas Observation salen inventadas y entran sin mapa, con su dato en el mensaje
    ADT_ACC = adt("F", ACC1)
    a = juicio("fallo_silencioso", "convertido", [h("fidelidad", "recurso_inventado", "OBX", INV % "o")])
    b = juicio("fallo_silencioso", "convertido", [h("fidelidad", "recurso_sin_mapa", "ACC", SM % ("o", "ACC", "ACC-1", "20260102", ""))])
    mira("conducta 2", R.clasificar(a, b, ADT_ACC, "adt_conv"), {"2"})
    mira("control: conducta 2 sin ACC ni PDA en el mensaje es de fuera", R.clasificar(a, b, adt("F"), "adt_conv"), {"fuera"})
    mira("control: conducta 2 fuera de ADT es de fuera", R.clasificar(a, b, ADT_ACC, "oru_conv"), {"fuera"})
    b5 = copy.deepcopy(b)
    b5["veredicto"]["categoria"] = "correcto"
    mira("control: conducta 2 con el veredicto cambiado es de fuera", R.clasificar(a, b5, ADT_ACC, "adt_conv"), {"fuera"})
    b10 = copy.deepcopy(b)
    b10["hallazgos"].append(h("fidelidad", "recurso_inventado", "OBX", INV % "p"))
    mira("control: un recurso_inventado nuevo en un ADT con ACC es de fuera", R.clasificar(a, b10, ADT_ACC, "adt_conv"), {"fuera"})
    b11 = juicio("fallo_silencioso", "convertido", [h("fidelidad", "recurso_sin_mapa", "ACC", SM % ("q", "ACC", "ACC-1", "20260102", ""))])
    mira("control: sale inventada una Observation y entra sin mapa otra, de fuera", R.clasificar(a, b11, ADT_ACC, "adt_conv"), {"fuera"})
    b12 = juicio("fallo_silencioso", "convertido", [h("fidelidad", "recurso_sin_mapa", "ACC", SM % ("o", "ACC", "ACC-1", "20991231", ""))])
    mira("control: el dato citado no es el del mensaje, de fuera", R.clasificar(a, b12, ADT_ACC, "adt_conv"), {"fuera"})
    b13 = juicio("fallo_silencioso", "convertido", [h("fidelidad", "recurso_sin_mapa", "PDA", SM % ("o", "ACC", "ACC-1", "20260102", ""))])
    mira("control: el hecho no es el segmento del texto, de fuera", R.clasificar(a, b13, ADT_ACC, "adt_conv"), {"fuera"})
    ap = juicio("fallo_silencioso", "convertido", [h("fidelidad", "recurso_inventado", "OBX", [INV % "o", INV % "p"])])
    bp = juicio("fallo_silencioso", "convertido", [h("fidelidad", "recurso_sin_mapa", "PDA", SM % ("o", "PDA", "PDA-3", "Y", ", de la 0136")),
                                                   h("fidelidad", "recurso_inventado", "OBX", INV % "p")])
    ADT_PDA = adt("F", PDA3)
    mira("conducta 2, por la 0136, y una que se queda inventada", R.clasificar(ap, bp, ADT_PDA, "adt_conv"), {"2"})
    mira("control: el campo de la 0136 no tiene ese valor, de fuera",
         R.clasificar(ap, bp, adt("F", seg("PDA", {3: "N", 9: "N"})), "adt_conv"), {"fuera"})
    bq = juicio("fallo_silencioso", "convertido", [h("fidelidad", "recurso_sin_mapa", "ACC/PDA",
                                                     SM % ("o", "ACC o PDA", "ACC-5/PDA-3", "Y", ", de la 0136"))])
    mira("conducta 2, ACC/PDA", R.clasificar(a, bq, adt("F", ACC1, PDA3), "adt_conv"), {"2"})
    mira("control: ACC/PDA con un solo segmento en el mensaje, de fuera", R.clasificar(a, bq, ADT_ACC, "adt_conv"), {"fuera"})
    # ---- las dos, y lo de fuera
    a = juicio("fallo_silencioso", "convertido+aceptado_imposible",
               [h("valor_imposible_aceptado", "valor_imposible_convertido+fhir_invalido", "PID-8", "x"),
                h("fidelidad", "recurso_inventado", "OBX", INV % "o")])
    b = juicio("fallo_silencioso", "convertido", [h("fidelidad", "fhir_invalido", "PID-8", "y"),
                                                  h("fidelidad", "recurso_sin_mapa", "PDA", SM % ("o", "PDA", "PDA-3", "Y", ", de la 0136"))])
    LAS_DOS = adt("S", PDA3)
    mira("las dos", R.clasificar(a, b, LAS_DOS, "adt_conv"), {"1", "2"})
    b6 = copy.deepcopy(b)
    b6["hallazgos"].append(h("fidelidad", "valor_distinto", "PID-5", "defecto"))
    mira("control: un hallazgo de PID-5 de más es de fuera", R.clasificar(a, b6, LAS_DOS, "adt_conv"), {"fuera"})
    a7 = juicio("fallo_silencioso", "convertido", [h("fidelidad", "valor_distinto", "PID-8", "Patient.gender: esperado 'female'")])
    b7 = juicio("fallo_silencioso", "convertido", [h("fidelidad", "valor_distinto", "PID-8", "Patient.gender: esperado 'female'"),
                                                   h("fidelidad", "valor_distinto", "PID-8", "defecto")])
    mira("control: un valor_distinto en PID-8 es de fuera", R.clasificar(a7, b7, S, "adt_conv"), {"fuera"})
    b8 = copy.deepcopy(a7)
    b8["recuentos"] = {"Patient": 2, "Encounter": 1}
    mira("control: los recuentos cambian, de fuera", R.clasificar(a7, b8, S, "adt_conv"), {"fuera"})
    mira("sin diferencia", R.clasificar(a7, copy.deepcopy(a7), S, "adt_conv"), set())
    print("PRUEBAS REJUICIO JZ: %s (%d comprobaciones)" % ("TODO BIEN" if not mal else "%d MAL" % len(mal), n_ok[0]))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
