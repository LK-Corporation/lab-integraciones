#!/usr/bin/env python3
"""Etapa 41 (po/diseno-po-fable.md §4): el clasificador del rejuicio de ORU, sobre juicios sintéticos. Cada caso cambia una cosa;
los mensajes llevan los valores de verdad, y entran los casos con la forma de la conducta que no lo son (y qué regla los saca).

  python3 po/prueba_rejuicio_po.py        -> TODO BIEN si no hay ningún MAL"""
import copy
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


def h(clase, subtipo, hecho, que, cuenta=True):
    return {"clase": clase, "subtipo": subtipo, "hecho": hecho, "cuenta": cuenta, "que": que if isinstance(que, list) else [que],
            "citas": [], "certeza": "literal", "nivel": None, "estado": "firme", "causa": None, "alternativa": None}


def juicio(cat, sub, hs, rec=None):
    return {"veredicto": {"categoria": cat, "subtipo": sub, "certeza": "literal", "alternativa": None, "provisional": False},
            "hallazgos": hs, "recuentos": rec or {"Patient": 1, "DiagnosticReport": 1, "Observation": 3}}


def seg(nombre, campos):
    n = max(campos) if campos else 0
    return "|".join([nombre] + [campos.get(i, "") for i in range(1, n + 1)])


OBR = seg("OBR", {1: "1", 2: "PL1", 3: "FL1", 4: "A^Panel A^LN"})
OBX1 = seg("OBX", {1: "1", 2: "NM", 3: "2345-7^Glucosa^LN", 5: "1.20", 11: "F"})
OBXF = seg("OBX", {1: "1", 2: "ST", 3: "F9^Fuera^LN", 5: "x", 11: "F"})


def oru(pd17="F", fuera=False, ver="2.5"):
    msh = "MSH|^~\\&|A|B|C|D|20260101||ORU^R01^ORU_R01|1|P|%s" % ver
    segs = [msh, seg("PID", {1: "1", 3: "X1", 8: "F"})] + ([seg("PD1", {7: pd17})] if pd17 is not None else [])
    return "\r".join(segs + ([OBXF] if fuera else []) + [OBR, OBX1])


ADT = "\r".join(["MSH|^~\\&|A|B|C|D|20260101||ADT^A01^ADT_A01|1|P|2.5", seg("PID", {1: "1", 3: "X1", 8: "F"}), seg("PD1", {7: "F"}), "PV1|1|I"])
INV = "Observation urn:uuid:%s sin origen propio en el mensaje"
FP = h("nota", "fuera_proyeccion", "OBX", "Observation sin OBR que la guía crea desde un OBX fuera de ORDER_OBSERVATION (L-CV-7)", cuenta=False)
S0315 = "http://terminology.hl7.org/CodeSystem/v2-0315"


def aus(v="F"):
    return h("fidelidad", "recurso_ausente", "PD1-7", "falta la Observation de PD1-7 = %r (PD1[Observation-LivingWill])" % v)


def vd(v="F", obs="Y"):
    return h("fidelidad", "valor_distinto", "PD1-7", "Observation.valueCodeableConcept: esperado %r, observado [%r]" % (v, obs))


def nota(sub, v="X", obs="W"):
    return h("nota", sub, "PD1-7", "Observation.valueCodeableConcept: [(%r, %r)] para %r, fuera del ConceptMap (la 0315 es user-defined)" %
             (S0315, obs, v), cuenta=False)


def main():
    import rejuicio_po as R
    F, FO, CORR = oru(), oru(fuera=True), juicio("correcto", None, [])
    inv = lambda *us: h("fidelidad", "recurso_inventado", "OBX", [INV % u for u in us])
    fs = lambda *hs: juicio("fallo_silencioso", "convertido", list(hs))
    rr = h("fidelidad", "referencia_rota", "OBR", "DiagnosticReport.result {'reference': 'urn:uuid:op'}: no es una Observation de su OBR")
    # ---- la conducta
    mira("la inventada pasa a ser de PD1-7", R.clasificar(fs(inv("op")), CORR, F, "oru_conv"), {"pd17oru"})
    mira("sin Observation: entra recurso_ausente", R.clasificar(CORR, fs(aus()), F, "oru_conv"), {"pd17oru"})
    mira("valor_distinto con el valor del mensaje", R.clasificar(fs(inv("op")), fs(vd()), F, "oru_conv"), {"pd17oru"})
    mira("referida desde el informe: sale la inventada, la referencia rota del OBR se queda (Q-PO-1 a)",
         R.clasificar(fs(inv("op"), rr), fs(rr), F, "oru_conv"), {"pd17oru"})
    mira("con un OBX fuera: sale la nota de L-CV-7 que ocupaba la de PD1-7", R.clasificar(juicio("correcto", None, [FP]), CORR, FO, "oru_conv"),
         {"pd17oru"})
    mira("con un OBX fuera: una inventada ajena baja al hueco de L-CV-7", R.clasificar(fs(inv("ox"), FP), juicio("correcto", None, [FP]), FO,
                                                                                        "oru_conv"), {"pd17oru"})
    X8 = oru("X", ver="2.8")
    mira("PD1-7 = X: la nota version en 2.8", R.clasificar(fs(inv("op")), juicio("correcto", None, [nota("version")]), X8, "oru_conv"),
         {"pd17oru"})
    mira("dos inventadas fundidas, una pasa a PD1-7", R.clasificar(fs(inv("o1", "op")), fs(inv("o1")), F, "oru_conv"), {"pd17oru"})
    # ---- con la forma de la conducta, sin serlo (y la regla que lo saca)
    mira("control un ADT: R1", R.reglas(fs(inv("op")), CORR, ADT, "adt_conv"), ["R1"])
    mira("control PD1-7 vacío: R1", R.reglas(fs(inv("op")), CORR, oru(""), "oru_conv"), ["R1"])
    mira("control sin PD1: R1 (y R3, por el valor)", R.reglas(CORR, fs(aus()), oru(None), "oru_conv"), ["R1", "R3"])
    mira("control dos parejas que salen: R4", R.reglas(fs(inv("o1", "op")), CORR, F, "oru_conv"), ["R4"])
    mira("control una inventada que entra: R4", R.reglas(fs(inv("op")), fs(inv("ox")), F, "oru_conv"), ["R4"])
    mira("control la nota que sale sin OBX fuera: R4", R.reglas(juicio("correcto", None, [FP]), CORR, F, "oru_conv"), ["R4"])
    mira("control la nota que entra: R2 y R4", R.reglas(fs(inv("op")), juicio("correcto", None, [FP]), FO, "oru_conv"), ["R2", "R4"])
    mira("control recurso_ausente con otro valor: R3", R.reglas(CORR, fs(aus("Z")), F, "oru_conv"), ["R3"])
    mira("control la nota convencion en 2.8: R3", R.reglas(fs(inv("op")), juicio("correcto", None, [nota("convencion")]), X8, "oru_conv"), ["R3"])
    mira("control un subtipo de PD1-7 que el juez no da: R2", R.reglas(CORR, fs(h("fidelidad", "dato_inventado", "PD1-7", "x")), F, "oru_conv"),
         ["R2"])
    mira("control un valor_distinto en OBX-5: R2", R.reglas(fs(inv("op")), fs(h("fidelidad", "valor_distinto", "OBX-5", "x")), F, "oru_conv"),
         ["R2"])
    mira("control una referencia_rota del OBR que entra: R2", R.reglas(fs(inv("op")), fs(rr), F, "oru_conv"), ["R2"])
    mira("control un recurso_sin_mapa que entra: R2",
         R.reglas(fs(inv("op")), fs(h("fidelidad", "recurso_sin_mapa", "ACC", "Observation urn:uuid:op de ACC (ACC-1 = 'x')")), F, "oru_conv"),
         ["R2"])
    rz = juicio("rechazo_incorrecto", "error", [h("rechazo", "incorrecto", "MSH", "rechazó un mensaje con ['PID-8']")])
    mira("control un rechazo que cambia: R2 y R5", R.reglas(rz, CORR, F, "oru_conv"), ["R2", "R5"])
    b = fs(aus())
    b["recuentos"] = {"Patient": 1, "DiagnosticReport": 1, "Observation": 4}
    mira("control los recuentos cambian: R5", R.reglas(CORR, b, F, "oru_conv"), ["R5"])
    a = fs(inv("op"))
    mira("sin diferencia", R.clasificar(a, copy.deepcopy(a), F, "oru_conv"), set())
    mira("los OBX fuera de ORDER_OBSERVATION, del mensaje crudo", (R.obx_fuera(F), R.obx_fuera(FO), R.obx_fuera(F + "\rSPM|1\r" + OBX1)), (0, 1, 1))
    print("PRUEBAS REJUICIO PO: %s (%d comprobaciones)" % ("TODO BIEN" if not mal else "%d MAL" % len(mal), n_ok[0]))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
