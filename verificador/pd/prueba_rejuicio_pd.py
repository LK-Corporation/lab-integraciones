#!/usr/bin/env python3
"""Etapa 40 (pd/diseno-pd-fable.md §4): el clasificador del rejuicio, sobre juicios sintéticos. Cada caso cambia una cosa; los
mensajes llevan los valores de verdad, y entran los casos con la forma de la conducta que no lo son (y qué regla los saca).

  python3 pd/prueba_rejuicio_pd.py        -> TODO BIEN si no hay ningún MAL"""
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
            "hallazgos": hs, "recuentos": rec or {"Patient": 1, "Encounter": 1}}


def seg(nombre, campos):
    n = max(campos) if campos else 0
    return "|".join([nombre] + [campos.get(i, "") for i in range(1, n + 1)])


def adt(pd17="F", *mas, ver="2.5"):
    msh = "MSH|^~\\&|A|B|C|D|20260101||ADT^A01^ADT_A01|1|P|%s" % ver
    segs = [msh, seg("PID", {1: "1", 3: "X1", 8: "F"})] + ([seg("PD1", {7: pd17})] if pd17 is not None else []) + ["PV1|1|I"]
    return "\r".join(segs + list(mas))


INV = "Observation urn:uuid:%s sin origen propio en el mensaje"
SM = "Observation urn:uuid:%s de %s (%s = '%s'%s), que la hoja de ADT_A01 de la guía lista sin destino"
FP = h("nota", "fuera_proyeccion", "OBX", "Observation sin OBR que la guía crea desde un OBX fuera de ORDER_OBSERVATION (L-CV-7)", cuenta=False)
OBX = seg("OBX", {1: "1", 2: "NM", 3: "8867-4^Frecuencia^LN", 5: "60", 11: "F"})
ACC_Y = seg("ACC", {1: "20260102", 5: "Y"})
S0315 = "http://terminology.hl7.org/CodeSystem/v2-0315"


def aus(v="F"):
    return h("fidelidad", "recurso_ausente", "PD1-7", "falta la Observation de PD1-7 = %r (PD1[Observation-LivingWill])" % v)


def cmm(v="F"):
    return h("fidelidad", "codigo_mal_mapeado", "PD1-7", "Observation.valueCodeableConcept: esperado (%r, %r) (de %r), observado [(None, %r)]" %
             (S0315, v, v, v))


def vd(v="F", obs="Y"):
    return h("fidelidad", "valor_distinto", "PD1-7", "Observation.valueCodeableConcept: esperado %r, observado [%r]" % (v, obs))


def nota(sub, v="X", obs="W"):
    return h("nota", sub, "PD1-7", "Observation.valueCodeableConcept: [(%r, %r)] para %r, fuera del ConceptMap (la 0315 es user-defined)" %
             (S0315, obs, v), cuenta=False)


def main():
    import rejuicio_pd as R
    F, CORR = adt(), juicio("correcto", None, [])
    inv = lambda *us: h("fidelidad", "recurso_inventado", "OBX", [INV % u for u in us])
    fs = lambda *hs: juicio("fallo_silencioso", "convertido", list(hs))
    # ---- la conducta
    mira("sin OBX: la inventada pasa a ser de PD1-7", R.clasificar(fs(inv("op")), CORR, F, "adt_conv"), {"pd17"})
    mira("sin Observation: entra recurso_ausente", R.clasificar(CORR, fs(aus()), F, "adt_conv"), {"pd17"})
    mira("codigo_mal_mapeado con el valor del mensaje", R.clasificar(fs(inv("op")), fs(cmm()), F, "adt_conv"), {"pd17"})
    mira("valor_distinto con el valor del mensaje", R.clasificar(fs(inv("op")), fs(vd()), F, "adt_conv"), {"pd17"})
    mira("fhir_invalido y referencia_rota de PD1-7", R.clasificar(fs(inv("op")), fs(h("fidelidad", "fhir_invalido", "PD1-7", "status"),
                                                                                     h("fidelidad", "referencia_rota", "PD1-7", "subject")), F, "adt_conv"), {"pd17"})
    X = adt("X")
    mira("PD1-7 = X: la nota convencion en 2.5", R.clasificar(fs(inv("op")), juicio("correcto", None, [nota("convencion")]), X, "adt_conv"), {"pd17"})
    X8 = adt("X", ver="2.8")
    mira("PD1-7 = X: la nota version en 2.8", R.clasificar(fs(inv("op")), juicio("correcto", None, [nota("version")]), X8, "adt_conv"), {"pd17"})
    FO = adt("F", OBX)
    mira("con OBX: sale la inventada, la nota se queda", R.clasificar(fs(inv("ox"), FP), juicio("correcto", None, [FP]), FO, "adt_conv"), {"pd17"})
    mira("con OBX y solo la de PD1-7: sale la nota", R.clasificar(juicio("correcto", None, [FP]), CORR, FO, "adt_conv"), {"pd17"})
    YA = adt("Y", ACC_Y)
    sm = h("fidelidad", "recurso_sin_mapa", "ACC", SM % ("op", "ACC", "ACC-5", "Y", ", de la 0136"))
    mira("PD1-7 = Y y ACC-5 = Y: la de ACC pasa a ser de PD1-7", R.clasificar(fs(sm), CORR, YA, "adt_conv"), {"pd17"})
    sm2 = h("fidelidad", "recurso_sin_mapa", "ACC", [SM % ("o1", "ACC", "ACC-5", "Y", ", de la 0136"), SM % ("op", "ACC", "ACC-5", "Y", ", de la 0136")])
    sm1 = h("fidelidad", "recurso_sin_mapa", "ACC", SM % ("o1", "ACC", "ACC-5", "Y", ", de la 0136"))
    mira("dos de ACC fundidas, una pasa a PD1-7", R.clasificar(fs(sm2), fs(sm1), YA, "adt_conv"), {"pd17"})
    mira("dos inventadas fundidas, una pasa a PD1-7", R.clasificar(fs(inv("o1", "op")), fs(inv("o1")), F, "adt_conv"), {"pd17"})
    mira("dos salen con OBX y la nota", R.clasificar(fs(inv("o1", "op"), FP), juicio("correcto", None, [FP]), FO, "adt_conv"), {"pd17"})
    # ---- con la forma de la conducta, sin serlo (y la regla que lo saca)
    V = adt("")
    mira("control PD1-7 vacío con lo demás bien formado: R1", R.reglas(fs(inv("op")), CORR, V, "adt_conv"), ["R1"])
    mira("control sin PD1: R1", R.reglas(CORR, fs(aus()), adt(None), "adt_conv"), ["R1", "R3"])
    mira("control oru_conv: R1", R.reglas(fs(inv("op")), CORR, F, "oru_conv"), ["R1"])
    mira("control dos salen sin OBX: R4", R.reglas(fs(inv("o1", "op")), CORR, F, "adt_conv"), ["R4"])
    mira("control dos salen con OBX y sin la nota: R4", R.reglas(fs(inv("o1", "op")), CORR, FO, "adt_conv"), ["R4"])
    mira("control la de ACC pasa a inventada: R4", R.reglas(fs(sm), fs(inv("op")), YA, "adt_conv"), ["R4"])
    sm_z = h("fidelidad", "recurso_sin_mapa", "ACC", SM % ("op", "ACC", "ACC-1", "20250505", ""))
    mira("control entra un sin_mapa cuyo dato no está en el mensaje: R4", R.reglas(fs(sm), fs(sm_z), YA, "adt_conv"), ["R4"])
    mira("control recurso_ausente con otro valor: R3", R.reglas(CORR, fs(aus("Z")), F, "adt_conv"), ["R3"])
    mira("control codigo_mal_mapeado con otro valor: R3", R.reglas(fs(inv("op")), fs(cmm("Z")), F, "adt_conv"), ["R3"])
    mira("control valor_distinto con otro valor: R3", R.reglas(fs(inv("op")), fs(vd("Z")), F, "adt_conv"), ["R3"])
    mira("control la nota convencion en 2.8: R3", R.reglas(fs(inv("op")), juicio("correcto", None, [nota("convencion")]), X8, "adt_conv"), ["R3"])
    mira("control la nota version en 2.5: R3", R.reglas(fs(inv("op")), juicio("correcto", None, [nota("version")]), X, "adt_conv"), ["R3"])
    mira("control recurso_ausente con otro hallazgo de PD1-7: R3", R.reglas(CORR, fs(aus(), vd()), F, "adt_conv"), ["R3"])
    mira("control un valor_distinto en PID-5: R2", R.reglas(fs(inv("op")), fs(h("fidelidad", "valor_distinto", "PID-5", "x")), F, "adt_conv"), ["R2"])
    mira("control un subtipo de PD1-7 que el juez no da: R2", R.reglas(CORR, fs(h("fidelidad", "dato_inventado", "PD1-7", "x")), F, "adt_conv"),
         ["R2"])
    rz = juicio("rechazo_incorrecto", "error", [h("rechazo", "incorrecto", "MSH", "rechazó un mensaje con ['PID-8']")])
    mira("control un rechazo que cambia: R2 y R5", R.reglas(rz, CORR, F, "adt_conv"), ["R2", "R5"])
    ai = juicio("fallo_silencioso", "convertido+aceptado_imposible", [aus()])
    mira("control el veredicto a aceptado_imposible: R5", R.reglas(CORR, ai, F, "adt_conv"), ["R5"])
    b = fs(aus())
    b["recuentos"] = {"Patient": 1, "Encounter": 1, "Observation": 1}
    mira("control los recuentos cambian: R5", R.reglas(CORR, b, F, "adt_conv"), ["R5"])
    a = fs(inv("op"))
    mira("sin diferencia", R.clasificar(a, copy.deepcopy(a), F, "adt_conv"), set())
    mira("valor_pd17 y msh12 del mensaje crudo", (R.valor_pd17(F), R.valor_pd17(V), R.valor_pd17(adt(None)), R.msh12(X8), R.msh12(F)),
         ("F", "", "", "2.8", "2.5"))
    print("PRUEBAS REJUICIO PD: %s (%d comprobaciones)" % ("TODO BIEN" if not mal else "%d MAL" % len(mal), n_ok[0]))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
