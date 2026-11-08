#!/usr/bin/env python3
"""Etapa 37: el arreglo del juez (jz/diseno-jz-fable.md §3, con las decisiones de jz/decision-jev-jz.md).

  python3 jz/parche_juez_jz.py [<carpeta del juez>]     (por omisión, la de este laboratorio)

Conducta 1 (Q-JZ-1 b, Q-JZ-5 a): PID-8 y NK1-15 fuera de la 0001 (user-defined): un código de administrative-gender es nota de
convención (version fuera de 2.5); otro, FHIR inválido; sin gender, nada; PID-8 sale de los valores imposibles del rechazo.
Conducta 2 (Q-JZ-2 a, Q-JZ-3 d, Q-JZ-4 a): una Observation de un ADT que sale de ACC o PDA cuenta como recurso_sin_mapa, con hecho el
segmento y las citas de la hoja de ADT_A01 y de v2.5.
Cada sustitución tiene que darse una sola vez; si no, no se escribe nada. Conserva los finales de línea."""
import os
import sys

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CV = []          # (nombre, antes, después) de conversion.py

CV.append(("Juicio.nota con citas",
'''    def nota(self, subtipo, hecho, que, certeza="literal"):
        self.hs.append(_h("nota", subtipo, hecho, que, cuenta=False, certeza=certeza))''',
'''    def nota(self, subtipo, hecho, que, certeza="literal", citas=None):
        self.hs.append(_h("nota", subtipo, hecho, que, cuenta=False, certeza=certeza, citas=citas))'''))

CV.append(("los segmentos sin destino, antes de emparejar",
'''def emparejar(m, entries, familia, notas=()):''',
'''# ---------------------------------------------------------------------------- etapa 37: los segmentos de ADT sin destino
# Q-JZ-2 a, Q-JZ-3 d y Q-JZ-4 a (jz/decision-jev-jz.md): ACC y PDA, que la hoja de ADT_A01 lista sin destino. De cada campo, su
# tipo de v2.5 (CH06.txt:5586-5612, Ch03.txt:8914-8935): fechas (TS; DR, sus dos TS), códigos (CE.1 y CE.4), textos (ST entero;
# XCN.1-3, PL.1-4 y XAD.1-3, con su primer subcomponente) y los ID de la 0136.
SIN_DESTINO_ADT = {
    "ACC": {"citas": ["[G MSG_ADT_A01.csv:78]", "[E3 Ch03.txt:269]", "[E6 CH06.txt:5586-5612]"],
            "ts": (1,), "dr": (), "ce": (2, 4), "st": (3, 8, 9), "comp": {7: (1, 2, 3), 11: (1, 2, 3)}, "si_no": (5, 6, 10)},
    "PDA": {"citas": ["[G MSG_ADT_A01.csv:81]", "[E3 Ch03.txt:275]", "[E3 Ch03.txt:8914-8935]"],
            "ts": (4,), "dr": (7,), "ce": (1,), "st": (), "comp": {2: (1, 2, 3, 4), 5: (1, 2, 3), 8: (1, 2, 3)}, "si_no": (3, 6, 9)},
}
SI_NO = {"Y", "N"}
NO_DATO = {"id", "meta", "fullUrl", "reference", "system", "url", "display", "text", "div", "resourceType", "status"}


def _primitivos(x, clave=None):
    """(clave, valor) de cada primitivo de un recurso, sin lo que nunca se juzga (L-CV-9) ni el status."""
    if isinstance(x, dict):
        return [p for k, v in x.items() if k not in NO_DATO for p in _primitivos(v, k)]
    if isinstance(x, list):
        return [p for v in x for p in _primitivos(v, clave)]
    if isinstance(x, (str, int, float)) and not isinstance(x, bool):
        return [(clave, str(x))]
    return []


def _datos_sin_destino(m, s, d):
    """Las fechas, los códigos, los textos y los valores de la 0136 de un segmento sin destino, cada uno con su campo."""
    nombre = s.split(m.f)[0]
    fechas, codigos, textos, si_no = [], [], [], []
    for n in d["ts"] + d["dr"]:
        for rep in _reps(m, _f(m, s, n)):
            fechas += [("%s-%d" % (nombre, n), _t(m, rep, i)) for i in ((1, 2) if n in d["dr"] else (1,)) if _t(m, rep, i)]
    for n in d["ce"]:
        for rep in _reps(m, _f(m, s, n)):
            codigos += [("%s-%d" % (nombre, n), v) for v in (_t(m, rep, 1), _t(m, rep, 4)) if v]
    for n in d["st"]:
        textos += [("%s-%d" % (nombre, n), _d(m, rep)) for rep in _reps(m, _f(m, s, n)) if len(_d(m, rep)) >= 3]
    for n, cs in d["comp"].items():
        for rep in _reps(m, _f(m, s, n)):
            textos += [("%s-%d" % (nombre, n), _t(m, rep, i)) for i in cs if len(_t(m, rep, i)) >= 3]
    for n in d["si_no"]:
        v = _d(m, _f(m, s, n)).upper()
        if v in SI_NO:
            si_no.append(("%s-%d" % (nombre, n), v))
    return fechas, codigos, textos, si_no


def _misma_fecha(ts, valor):
    """Un TS y un date/dateTime de FHIR: las partes que trae el de FHIR (al menos el día) son las del TS, sin desplazar."""
    f, t = FHIR_DT.match(valor), re.match(r"\\d+", ts)
    if not f or not t:
        return False
    partes = "".join(x for x in f.groups()[:6] if x)
    return len(partes) >= 8 and t.group(0).startswith(partes)


def _origen_sin_mapa(m, r):
    """Etapa 37 (L-CV-17): (segmento, dato) del segmento sin destino del que sale una Observation de un ADT, o None.
    Por un dato igual (una fecha de un TS, un código de un CE en un coding.code, un texto de tres caracteres o más) o, si solo
    lleva valores de la 0136, por un campo de la 0136 de ese valor; si así casan varios segmentos, el hecho los nombra todos.
    Con el código de un OBX del mensaje, es la de ese OBX: None."""
    presentes = [(s.split(m.f)[0], s) for s in m.segs if s.split(m.f)[0] in SIN_DESTINO_ADT]
    if not presentes:
        return None
    prims = _primitivos(r)
    obx = {c for s in m.segmentos("OBX") for c in (_t(m, _f(m, s, 3), 1), _t(m, _f(m, s, 3), 4)) if c}
    if obx & {v for k, v in prims if k == "code"}:
        return None
    sn = []
    for nombre, s in presentes:
        fechas, codigos, textos, si_no = _datos_sin_destino(m, s, SIN_DESTINO_ADT[nombre])
        for campo, ts in fechas:
            if any(_misma_fecha(ts, v) for _, v in prims):
                return nombre, "%s = %r" % (campo, ts)
        for campo, c in codigos:
            if any(k == "code" and v == c for k, v in prims):
                return nombre, "%s = %r" % (campo, c)
        for campo, t in textos:
            if any(v == t for _, v in prims):
                return nombre, "%s = %r" % (campo, t)
        sn.append((nombre, si_no))
    resto = {v for _, v in _primitivos({k: v for k, v in r.items() if k != "code"})}
    if resto and resto <= SI_NO:
        casan = [(nombre, [c for c, v in si_no if v in resto]) for nombre, si_no in sn if resto <= {v for _, v in si_no}]
        if casan:
            return ("/".join(n for n, _ in casan),
                    "%s = %s, de la 0136" % ("/".join(c for _, cs in casan for c in cs), "/".join(repr(v) for v in sorted(resto))))
    return None


def emparejar(m, entries, familia, notas=()):'''))

CV.append(("emparejar: los sobrantes de ADT",
'''        n_obx = len(m.segmentos("OBX"))
        obs = [e for e in top if e["tipo"] in ("Observation", "DiagnosticReport")]
        for k, e in enumerate(obs):
            motivo = "origen_guia" if e["tipo"] == "Observation" and k < n_obx else "inventado"
            out["sobrantes"].append({"resourceType": e["tipo"], "fullUrl": e["fullUrl"], "motivo": motivo,
                                     "hecho": "OBX" if e["tipo"] == "Observation" else "OBR"})
            usados.add(e["i"])''',
'''        n_obx = len(m.segmentos("OBX"))
        obs = [e for e in top if e["tipo"] in ("Observation", "DiagnosticReport")]
        k = 0
        for e in obs:
            sm = _origen_sin_mapa(m, e["r"]) if e["tipo"] == "Observation" else None      # etapa 37 (L-CV-17)
            if sm:
                out["sobrantes"].append({"resourceType": e["tipo"], "fullUrl": e["fullUrl"], "motivo": "sin_mapa", "hecho": sm[0],
                                         "dato": sm[1]})
            else:
                motivo = "origen_guia" if e["tipo"] == "Observation" and k < n_obx else "inventado"
                k += 1
                out["sobrantes"].append({"resourceType": e["tipo"], "fullUrl": e["fullUrl"], "motivo": motivo,
                                         "hecho": "OBX" if e["tipo"] == "Observation" else "OBR"})
            usados.add(e["i"])'''))

CV.append(("PID-8 fuera de la 0001",
'''def _genero(J, m, v, obs):''',
'''CIT_0001 = C["PID-8"][:2] + ["[E3 Ch03.txt:5032-5044]"]          # etapa 37: la 0001 de v2.5 es user-defined, valores sugeridos


def _genero(J, m, v, obs):'''))

CV.append(("_genero, la rama de fuera",
'''    if t == FUERA:
        if obs is not None:
            J.cuenta("valor_imposible_convertido", "PID-8", "Patient.gender: %r convertido desde %r, fuera de la 0001" % (obs, v),
                     clase="valor_imposible_aceptado", tabla=True)
            if obs not in GENERO_FHIR:
                J.cuenta("fhir_invalido", "PID-8", "Patient.gender: %r fuera de administrative-gender (required)" % obs)
        return''',
'''    if t == FUERA:                   # etapa 37: la 0001 es user-defined; fuera del mapa, convención (Q-JZ-5 a: sin gender, nada)
        if obs in GENERO_FHIR:
            J.nota("convencion" if J.v25 else "version", "PID-8",
                   "Patient.gender: %r para %r, fuera del ConceptMap (la 0001 es user-defined)" % (obs, v), citas=CIT_0001)
        elif obs is not None:
            J.cuenta("fhir_invalido", "PID-8", "Patient.gender: %r fuera de administrative-gender (required)" % obs)
        return'''))

CV.append(("_imposibles sin PID-8",
'''        v8 = _d(m, _f(m, pid, 8))
        if v8 and mapa("0001", v8) == FUERA:
            out.append("PID-8")''',
'''        # etapa 37 (Q-JZ-1 b): PID-8 fuera de la 0001 ya no es imposible (la 0001 es user-defined, Ch03.txt:5032-5044)'''))

CV.append(("_juzgar: recurso sin mapa",
'''        if s["motivo"] == "origen_guia":
            J.nota("fuera_proyeccion", s["hecho"], "%s sin OBR que la guía crea desde un OBX fuera de ORDER_OBSERVATION (L-CV-7)" % s["resourceType"])
        else:''',
'''        if s["motivo"] == "origen_guia":
            J.nota("fuera_proyeccion", s["hecho"], "%s sin OBR que la guía crea desde un OBX fuera de ORDER_OBSERVATION (L-CV-7)" % s["resourceType"])
        elif s["motivo"] == "sin_mapa":                                  # etapa 37 (Q-JZ-2 a)
            J.cuenta("recurso_sin_mapa", s["hecho"], "%s %s de %s (%s), que la hoja de ADT_A01 de la guía lista sin destino" % (
                s["resourceType"], s["fullUrl"], " o ".join(s["hecho"].split("/")), s["dato"]),
                citas=[c for x in s["hecho"].split("/") for c in SIN_DESTINO_ADT[x]["citas"]])
        else:'''))

CV.append(("perfil de PID-8",
'''    {"elemento": "Patient.gender", "campo": "PID-8", "regla": "por la 0001; vacío: ausente (Q-CV-D-3); fuera de la 0001: ausente", "nivel": "cuenta", "citas": C["PID-8"]},''',
'''    {"elemento": "Patient.gender", "campo": "PID-8", "regla": "por la 0001; vacío: ausente (Q-CV-D-3); fuera de la 0001 (user-defined): un código de administrative-gender es convención, otro es FHIR inválido; sin gender, nada (etapa 37)", "nivel": "cuenta", "citas": CIT_0001 + C["PID-8"][2:]},'''))

CV.append(("perfil: la Observation de un segmento sin destino",
'''    {"elemento": "id, meta, text, extensiones, display, Bundle.type, orden de listas", "campo": "—", "regla": "forma (§4.2, L-CV-4, L-CV-9)", "nivel": "forma", "citas": ["[L-CV-4]", "[L-CV-9]"]},
]
PERFIL_GUIA_ORU = [''',
'''    {"elemento": "Observation (de un segmento sin destino)", "campo": "ACC/PDA", "regla": "la hoja de ADT_A01 los lista sin destino: recurso sin mapa, reconocido por un dato igual o, con solo valores de la 0136, por un campo de la 0136 de ese valor (L-CV-17, etapa 37)", "nivel": "cuenta", "citas": SIN_DESTINO_ADT["ACC"]["citas"] + SIN_DESTINO_ADT["PDA"]["citas"]},
    {"elemento": "id, meta, text, extensiones, display, Bundle.type, orden de listas", "campo": "—", "regla": "forma (§4.2, L-CV-4, L-CV-9)", "nivel": "forma", "citas": ["[L-CV-4]", "[L-CV-9]"]},
]
PERFIL_GUIA_ORU = ['''))

CV.append(("S-CV-5",
'''recurso ausente/duplicado/inventado, referencia rota''',
'''recurso ausente/duplicado/inventado/sin mapa (etapa 37), referencia rota'''))

CV.append(("L-CV-17 y L-CV-18",
'''"XPN.15, XAD.9 como CWE…); lo que depende de ellos se aparta al adjudicar (CV3)."}''',
'''"XPN.15, XAD.9 como CWE…); lo que depende de ellos se aparta al adjudicar (CV3).",
        "L-CV-17": "Etapa 37: una Observation de un ADT sale de ACC o PDA (sin destino en la hoja de ADT_A01) si comparte con el "
                   "segmento un dato (una fecha de un TS sin desplazar, un código de un CE, un texto de tres caracteres o más) o, si "
                   "solo lleva valores de la 0136, si un campo de la 0136 del segmento tiene ese valor; con varios segmentos así, el "
                   "hecho los nombra todos; con el código de un OBX del mensaje, es la de ese OBX. Sin nada de eso sigue como "
                   "recurso_inventado. Los otros 16 segmentos que la hoja lista sin destino no se reconocen.",
        "L-CV-18": "La Observation que la guía crea desde PD1-7 (MSG_ADT_A01.csv:19, «IF PD1-7 VALUED») no se empareja con su campo: "
                   "pasa por una de las de los OBX, por orden, y sin OBX cuenta como recurso_inventado (fallo conocido, fuera de la "
                   "etapa 37)."}'''))

VX = [("_genero de VXU, la rama de fuera",
'''    t = CV.mapa("0001", v)
    if t == FUERA:
        if obs is not None:
            _cuenta(J, "valor_imposible_convertido", hecho, "%s.gender %r desde %r, fuera de la 0001" % (ruta, obs, v),
                     clase="valor_imposible_aceptado", tabla=True)
        return''',
'''    t = CV.mapa("0001", v)
    if t == FUERA:                   # etapa 37: la 0001 es user-defined; fuera del mapa, convención (Q-JZ-5 a: sin gender, nada)
        if obs in CV.GENERO_FHIR:
            J.hs.append(CV._h("nota", "convencion" if J.v25 else "version", hecho,
                              "%s.gender %r para %r, fuera del ConceptMap (la 0001 es user-defined)" % (ruta, obs, v), cuenta=False,
                              citas=list(_cit(hecho)) + ["[E3 Ch03.txt:5032-5044]"]))
        elif obs is not None:
            _cuenta(J, "fhir_invalido", hecho, "%s.gender %r fuera de administrative-gender (required)" % (ruta, obs))
        return'''),
      ("comentario de imposibles en VXU",
'''    out = CV._imposibles(m, "vxu")                                   # PID-7, PID-8 y OBX-5 NM, como en ADT y ORU''',
'''    out = CV._imposibles(m, "vxu")                                   # PID-7 y OBX-5 NM, como en ADT y ORU (PID-8 no: etapa 37)''')]

MD = [("comentario de imposibles en MDM",
'''    out = CV._imposibles(m, "mdm")                                    # PID-7, PID-8 y OBX-5 NM, como en ADT y ORU''',
'''    out = CV._imposibles(m, "mdm")                                    # PID-7 y OBX-5 NM, como en ADT y ORU (PID-8 no: etapa 37)''')]


def aplica(ruta, cambios):
    t = open(ruta, encoding="utf-8", newline="").read()
    for nombre, antes, despues in cambios:
        n = t.count(antes)
        if n != 1:
            raise SystemExit("%s, «%s»: aparece %d veces; no se escribe nada" % (os.path.basename(ruta), nombre, n))
        t = t.replace(antes, despues)
    return t


def main(carpeta=AQUI):
    rutas = [os.path.join(carpeta, f) for f in ("conversion.py", "conversion_vxu.py", "conversion_mdm.py")]
    if "SIN_DESTINO_ADT" in open(rutas[0], encoding="utf-8").read():
        print("ya aplicado")
        return 0
    nuevos = [aplica(r, c) for r, c in zip(rutas, (CV, VX, MD))]
    for r, t in zip(rutas, nuevos):
        open(r, "w", encoding="utf-8", newline="").write(t)
    print("juez de la etapa 37 escrito en %s" % ", ".join(os.path.basename(r) for r in rutas))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
