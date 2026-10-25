#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 21 (cv/ar/diseno-ar-fable.md; decisiones de Jev en cv/ar/decision-jev-qar.md): el aparato que compara LinuxForHealth en
lote (un proceso por carpeta, como en el estudio) con LinuxForHealth mensaje a mensaje (un proceso por mensaje), con el mismo
juez a los dos lados. No toca la herramienta (cv/verificar_conversor.py), ni el arnés, ni el juez, ni cv3_clases.py ni
cv3_minimos.py (S-AR-15): los usa. Solo biblioteca estándar.

  python3 cv/ar/arrastre.py positivo <artefactos> <trabajo>                 # VL11 en los dos modos -> POSITIVO-AR.json
  python3 cv/ar/arrastre.py ruido <A> <B> <salida.json>                      # dos corridas del mismo modo
  python3 cv/ar/arrastre.py comparar <L1> <L2> <M1> <M2> <trabajo>           # -> COMPARACION-AR.json (exige los controles)
  python3 cv/ar/arrastre.py adjudicar <artefactos> <trabajo>                 # -> ADJUDICACION-AR.json
  python3 cv/ar/arrastre.py recalcular <artefactos> <ms> <trabajo>           # -> CIFRAS-AR.json, CLASES-AR-*.json, minimos-AR-*.json
  python3 cv/ar/arrastre.py resultado <trabajo> <RESULTADO-ARRASTRE.md>

<trabajo> es la carpeta del control (la de cv/ar/control_ar.py): sus corridas se llaman L1, L2, M1, M2 dentro de ella.
Códigos: 0 bien; 3 el positivo VL11 no sale; 6 comparar sin los dos controles en «pasa»; 1 error."""
import collections
import hashlib
import io
import json
import os
import re
import shutil
import sys
import time
from contextlib import redirect_stdout

AR_D = os.path.dirname(os.path.abspath(__file__))
CVD = os.path.dirname(AR_D)
FASE = os.path.dirname(CVD)
sys.path[:0] = [AR_D, CVD, FASE]
_argv, sys.argv = sys.argv, ["x", "--silencio"]
import verificar_conversor as VC  # noqa: E402
import cv3_minimos_vxu as MINV  # noqa: E402
sys.argv = _argv

AD_LOTE = os.path.join(CVD, "adaptadores", "linuxforhealth.json")
AD_MENSAJE = os.path.join(CVD, "adaptadores", "linuxforhealth-mensaje.json")
AD_MS = os.path.join(CVD, "adaptadores", "microsoft.json")
CONTROL = ("vxu",)                                                    # S-AR-17: VXU viaja en las corridas, no entra en N
RESULTADO_CORPUS = ("adt", "oru", "muestras")                         # los que lee cv3_clases (sin vxu ni minimos)
UMBRAL = 0.0                                                          # Q-AR-D-1 (Jev: cero)
RXA17 = ["RXA-17", "fidelidad", "dato_perdido"]
VXU_ESPERADO = ["VXU-B%02d" % i for i in range(18, 41)]               # vx/VX2.md F7
VL11 = ("1-L11a", "2-L11b", "1-L11b")
PRESUPUESTO_CASO = 40                                                 # §5.2, paso 7
RELOJ_ADJUDICACION_S = 90 * 60
CLAVES_PREVISION = ("etapa", "fecha", "juez", "conversor", "imagen_digest", "herramienta",
                    "probabilidad_al_menos_una_diferencia_por_arrastre", "K_previsto", "direccion", "mecanismos_que_podrian_cambiar",
                    "pares_que_podrian_cambiar", "cifras_que_podrian_cambiar", "ruido_previsto", "umbral_q_ar_d_1")
CIFRAS_PUBLICADAS = [                                                 # §6.1, columna 1
    ("frase.", ["verificador/RESULTADO-CONVERSORES.md", "ARTICULO.md", "README.md", "verificador/README.md", "docs/conversores/index.html"]),
    ("clases.", ["verificador/cv/CLASES-CV3.json", "verificador/cv/RESULTADO-CV3.md", "docs/conversores/index.html"]),
    ("convenciones.", ["verificador/cv/CLASES-CV3.json", "verificador/cv/RESULTADO-CV3.md"]),
    ("sin_clase.", ["verificador/cv/CLASES-CV3.json"]),
    ("minimos.", ["verificador/cv/RESULTADO-CV3-minimos.json", "docs/conversores/index.html"]),
    ("por_corpus.", ["verificador/cv/RESULTADO-CV2.json", "verificador/cv/RESULTADO-CV2.md", "docs/conversores/index.html"]),
]
UUID = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")


class ErrorAparato(Exception):
    pass


def _escribir(ruta, d):
    with open(ruta, "w", encoding="utf-8") as g:
        g.write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")


def _leer(ruta):
    return json.load(open(ruta, encoding="utf-8"))


# ---------------------------------------------------------------------------- filas y veredictos (§3)
def filas(ruta):
    """Las filas de juicio.jsonl de una corrida (carpeta) o de un fichero."""
    if os.path.isdir(ruta):
        ruta = os.path.join(ruta, "juicio.jsonl")
    return [json.loads(x) for x in open(ruta, encoding="utf-8") if x.strip()]


def valor(f):
    """S-AR-6: exactamente VC._valor (estado, categoría, subtipo y {(hecho, clase, subtipo)}), en forma JSON."""
    return json.loads(json.dumps(VC._valor(f)))


def _clave(f):
    return (f["corpus"], f["caso"])


def _resta(a, b):
    return sorted(x for x in a["hallazgos"] if x not in b["hallazgos"])


def _ques(f):
    return [q for h in f["cuentan"] for q in h["que"]][:6]


def comparar_juicios(L1, L2, M1, M2):
    """S-AR-10 caso a caso con las cuatro corridas. vxu va a control_vxu y no entra en n."""
    ix = [{_clave(f): f for f in x} for x in (L1, L2, M1, M2)]
    claves = sorted(set().union(*ix))
    pos = {}
    for c in sorted({k[0] for k in claves}):
        for i, k in enumerate(sorted((k for k in claves if k[0] == c), key=lambda k: k[1] + ".hl7"), 1):
            pos[k] = i
    out = {"n": collections.Counter(), "por_corpus": collections.defaultdict(collections.Counter), "diferencias": [],
           "no_deterministas": [], "sin_par": [], "caja": []}
    vxu = {"diferentes": [], "no_deterministas": [], "sin_par": [], "detalle": []}
    for k in claves:
        fs = [d.get(k) for d in ix]
        base = {"corpus": k[0], "caso": k[1], "posicion_en_lote": pos[k]}
        if any(f is None for f in fs):
            clase, d = "sin_par", dict(base, falta=[n for n, f in zip(("L1", "L2", "M1", "M2"), fs) if f is None])
        elif any(f["estado"] == "sin_respuesta" for f in fs):
            clase, d = "caja", dict(base, estados=[f["estado"] for f in fs])
        else:
            v = [valor(f) for f in fs]
            if v[0] != v[1] or v[2] != v[3]:
                clase, d = "no_determinista", dict(base, lote=v[:2], mensaje=v[2:])
            elif v[0] != v[2]:
                clase, d = "diferente", dict(base, lote=v[0], mensaje=v[2], solo_en_lote=_resta(v[0], v[2]),
                                             solo_en_mensaje=_resta(v[2], v[0]), que={"lote": _ques(fs[0]), "mensaje": _ques(fs[2])})
            else:
                clase, d = "igual", None
        if k[0] in CONTROL:
            if clase == "diferente":
                vxu["diferentes"].append(k[1])
                vxu["detalle"].append(d)
            elif clase == "no_determinista":
                vxu["no_deterministas"].append(k[1])
            elif clase in ("sin_par", "caja"):
                vxu["sin_par"].append(k[1])
            continue
        nombre = {"igual": "iguales", "diferente": "diferentes", "no_determinista": "no_deterministas"}.get(clase, clase)
        for cont in (out["n"], out["por_corpus"][k[0]]):
            cont["comparados"] += 1
            cont[nombre] += 1
        if d is not None:
            out["diferencias" if clase == "diferente" else "no_deterministas" if clase == "no_determinista" else clase].append(d)
    claves_n = ("comparados", "iguales", "diferentes", "no_deterministas", "sin_par", "caja")
    out["n"] = {x: out["n"][x] for x in claves_n}
    out["por_corpus"] = {c: dict({x: v[x] for x in claves_n}, n=v["comparados"]) for c, v in sorted(out["por_corpus"].items())}
    out["control_vxu"] = vxu
    return out


# ---------------------------------------------------------------------------- el Bundle (§3.1, nivel B; Q-AR-D-4: solo el ruido)
def _norm(x):
    if isinstance(x, dict):
        return {k: _norm(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_norm(v) for v in x]
    if isinstance(x, str):
        return UUID.sub("<uuid>", x)
    return x


def recursos(b):
    """Los recursos del Bundle normalizados (UUID -> <uuid>, sin resource.id ni entry.fullUrl), y el Bundle mismo como pseudorrecurso
    con type, identifier y timestamp."""
    if isinstance(b, str):
        b = json.loads(b)
    rs = [dict({k: b[k] for k in ("type", "identifier", "timestamp") if k in b}, resourceType="Bundle")]
    for e in b.get("entry") or []:
        r = dict(e.get("resource") or {})
        r.pop("id", None)
        rs.append(r)
    return [_norm(r) for r in rs]


def firma_recurso(r):
    return json.dumps(r, sort_keys=True, ensure_ascii=False)


def multiset_bundle(b):
    return collections.Counter(firma_recurso(r) for r in recursos(b))


def _hojas(x, ruta=""):
    if isinstance(x, dict):
        for k, v in x.items():
            if not (ruta == "" and k == "resourceType"):
                yield from _hojas(v, "%s.%s" % (ruta, k) if ruta else k)
    elif isinstance(x, list):
        for v in x:
            yield from _hojas(v, ruta + "[]")
    else:
        yield ruta, x


def _uno(vs):
    return None if not vs else vs[0] if len(vs) == 1 else vs


def _diff_recurso(rt, a, b):
    ha, hb = collections.defaultdict(list), collections.defaultdict(list)
    for r, v in _hojas(a):
        ha[r].append(v)
    for r, v in _hojas(b):
        hb[r].append(v)
    out = []
    for r in sorted(set(ha) | set(hb)):
        va, vb = sorted(ha.get(r, []), key=json.dumps), sorted(hb.get(r, []), key=json.dumps)
        if va != vb:
            out.append((rt, r, _uno(va), _uno(vb)))
    return out


def diff_bundles(a, b, mascara=()):
    """-> [(resourceType, ruta, valor_a, valor_b)]: se quitan los recursos iguales y el resto se empareja por tipo y orden de firma;
    un recurso sin pareja da (resourceType, "<recurso>", presente/ausente)."""
    ca, cb = multiset_bundle(a), multiset_bundle(b)
    comun = ca & cb
    resto = {"a": collections.defaultdict(list), "b": collections.defaultdict(list)}
    for lado, c in (("a", ca - comun), ("b", cb - comun)):
        for f in c.elements():
            resto[lado][json.loads(f)["resourceType"]].append(f)
    out = []
    for rt in sorted(set(resto["a"]) | set(resto["b"])):
        xa, xb = sorted(resto["a"][rt]), sorted(resto["b"][rt])
        for fa, fb in zip(xa, xb):
            out += _diff_recurso(rt, json.loads(fa), json.loads(fb))
        out += [(rt, "<recurso>", "presente", "ausente")] * max(0, len(xa) - len(xb))
        out += [(rt, "<recurso>", "ausente", "presente")] * max(0, len(xb) - len(xa))
    return [d for d in out if (d[0], d[1]) not in set(mascara)]


def firma_error(e):
    s = e["conversion"]["salida"]
    if s["estado"] != "error":
        return None
    err = s.get("error") or {}
    return [err.get("codigo"), VC.MEC.firma(((err.get("texto") or "").strip().split("\n") or [""])[0])]


# ---------------------------------------------------------------------------- el ruido (§4.2)
def _cid(corrida):
    return _leer(os.path.join(corrida, "ADAPTADOR.json"))["id"]


def evidencia(corrida, k, cid=None):
    return _leer(os.path.join(corrida, "evidencias", cid or _cid(corrida), k[0], k[1] + ".json"))


def ruido(a, b):
    """Dos corridas del mismo modo: veredictos distintos (V), la máscara del Bundle (B) y los errores con otra firma (E)."""
    ia, ib = {_clave(f): f for f in filas(a)}, {_clave(f): f for f in filas(b)}
    comunes = sorted(set(ia) & set(ib))
    ver = [list(k) for k in comunes if valor(ia[k]) != valor(ib[k])]
    ca, cb = _cid(a), _cid(b)
    mascara, casos_b, errores = collections.Counter(), 0, []
    for k in comunes:
        ea, eb = evidencia(a, k, ca), evidencia(b, k, cb)
        sa, sb = ea["conversion"]["salida"], eb["conversion"]["salida"]
        if sa["estado"] == sb["estado"] == "bundle":
            try:
                d = diff_bundles(sa["bundle"], sb["bundle"])
            except (ValueError, TypeError):
                d = [("?", "<ilegible>", None, None)] if sa["bundle"] != sb["bundle"] else []
            if d:
                casos_b += 1
                for x in {(x[0], x[1]) for x in d}:
                    mascara[x] += 1
        elif sa["estado"] == sb["estado"] == "error" and firma_error(ea) != firma_error(eb):
            errores.append(list(k))
    return {"comparados": len(comunes), "veredicto": ver, "faltan": [list(k) for k in sorted(set(ia) ^ set(ib))],
            "bundle": {"casos": casos_b, "mascara": [[rt, r, n] for (rt, r), n in sorted(mascara.items())]}, "errores": errores}


def regla_parada(ruido_lote, ruido_mensaje, n, umbral=UMBRAL):
    """Regla de parada 2 (§4.2, Q-AR-D-1): para si los casos con veredicto distinto entre dos corridas del mismo modo, en los dos
    modos y contados una vez, pasan del umbral."""
    casos = {tuple(x) for x in ruido_lote["veredicto"]} | {tuple(x) for x in ruido_mensaje["veredicto"]}
    return len(casos) > umbral * n


# ---------------------------------------------------------------------------- los positivos (§4.1)
def positivo_sale(lote_caso, mensaje_caso, lote_control):
    """P+1 en una repetición: filas por caso de lote-caso, mensaje-caso y lote-control. -> (sale, motivos)."""
    a, b, k = VL11
    mot = []
    vl, vm = valor(lote_caso[b]), valor(mensaje_caso[b])
    if RXA17 not in vl["hallazgos"]:
        mot.append("en lote, 2-L11b no pierde RXA-17")
    elif not any("manufacturer" in q for h in lote_caso[b]["cuentan"] if [h["hecho"], h["clase"], h["subtipo"]] == RXA17 for q in h["que"]):
        mot.append("el hallazgo de RXA-17 no habla de manufacturer")
    if any(x[0] == "RXA-17" and x[2] == "dato_perdido" for x in vm["hallazgos"]):
        mot.append("mensaje a mensaje, 2-L11b también pierde RXA-17")
    difs = [d["caso"] for d in VC.comparar(list(mensaje_caso.values()), list(lote_caso.values()))["diferencias"]]
    if difs != [b]:
        mot.append("las diferencias son %s, no solo 2-L11b" % difs)
    elif _resta(vl, vm) != [RXA17] or _resta(vm, vl):
        mot.append("la diferencia de 2-L11b no es exactamente RXA-17")
    if valor(lote_caso[a]) != valor(mensaje_caso[a]):
        mot.append("1-L11a cambia entre modos")
    if valor(lote_control[k]) != vm:
        mot.append("el control (1-L11b solo) no da lo de mensaje a mensaje")
    return not mot, mot


RXA17_GRUPO = re.compile(r"^RXA(\(\d+\))?-17$")                       # DV-AR-11: el grupo n de un VXU con varias RXA es «RXA(n)-17»


def positivo_vxu(comp):
    """P+2: los casos vxu diferentes son exactamente VXU-B18..B40, y en cada uno solo cambia, en lote, el RXA-17 de algún grupo
    (dato_perdido); mensaje a mensaje, nada."""
    c = comp["control_vxu"]
    det = {d["caso"]: d for d in c["detalle"]}
    solo_rxa17 = lambda xs: bool(xs) and all(RXA17_GRUPO.match(x[0]) and x[1:] == RXA17[1:] for x in xs)  # noqa: E731
    return (c["diferentes"] == VXU_ESPERADO and not c["no_deterministas"] and not c["sin_par"]
            and all(solo_rxa17(det[x]["solo_en_lote"]) and det[x]["solo_en_mensaje"] == [] for x in VXU_ESPERADO))


def _correr_carpeta(ad, corpus, salida, artefactos, ejecutor=None):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = VC.main([ad, salida, "--artefactos", artefactos, "--sin-corpus-lab", "--sin-minimos", "--sin-sensibilidad", "--json-solo",
                      "--corpus", corpus], ejecutor=ejecutor)
    if rc != 0:
        raise ErrorAparato("la herramienta salió con %s en %s:\n%s" % (rc, os.path.basename(salida), buf.getvalue()[-2000:]))
    return salida


def _por_caso(corrida):
    return {f["caso"]: f for f in filas(corrida)}


def positivo_vl11(artefactos, trabajo, ejecutor=None):
    """§4.1 P+1: dos repeticiones de lote-caso y mensaje-caso, y lote-control; y el nivel B ve el manufacturer."""
    d = os.path.join(trabajo, "positivo")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    with redirect_stdout(io.StringIO()):
        MINV.secuencias(os.path.join(d, "vl11"))
    caso = os.path.join(d, "vl11", "VL11-estado-fabricante-caso")
    control = os.path.join(d, "vl11", "VL11-estado-fabricante-control")
    reps = []
    for r in (1, 2):
        lc = _correr_carpeta(AD_LOTE, caso, os.path.join(d, "lote-caso-%d" % r), artefactos, ejecutor)
        mc = _correr_carpeta(AD_MENSAJE, caso, os.path.join(d, "mensaje-caso-%d" % r), artefactos, ejecutor)
        reps.append((lc, mc))
    lk = _correr_carpeta(AD_LOTE, control, os.path.join(d, "lote-control-1"), artefactos, ejecutor)
    res = {"repeticiones": []}
    for lc, mc in reps:
        sale, mot = positivo_sale(_por_caso(lc), _por_caso(mc), _por_caso(lk))
        res["repeticiones"].append({"sale": sale, "motivos": mot,
                                    "lote_2_L11b": valor(_por_caso(lc)["2-L11b"]), "mensaje_2_L11b": valor(_por_caso(mc)["2-L11b"])})
    lc, mc = reps[0]
    el, em = evidencia(lc, ("propio", "2-L11b")), evidencia(mc, ("propio", "2-L11b"))
    b = []
    if el["conversion"]["salida"]["estado"] == em["conversion"]["salida"]["estado"] == "bundle":
        b = diff_bundles(el["conversion"]["salida"]["bundle"], em["conversion"]["salida"]["bundle"])
    res["bundle_2_L11b"] = [list(x) for x in b]
    res["b_ve_manufacturer"] = any(x[0] == "Immunization" and x[1].startswith("manufacturer") for x in b)
    res["pasa_vl11"] = all(r["sale"] for r in res["repeticiones"]) and res["b_ve_manufacturer"]
    res["pasa"] = res["pasa_vl11"]
    return res


# ---------------------------------------------------------------------------- la adjudicación (§5)
def adjudicar_caso(vL1, vL2, vM1, vM2, aislamiento=None):
    if vL1 != vL2 or vM1 != vM2:
        return "no_determinismo"
    if vL1 == vM1:
        return "igual"
    return aislamiento["tipo"] if aislamiento else "diferente"


def hacer_corredores(ad_lote, ad_mensaje, artefactos, textos, trabajo, ejecutor=None):
    """-> (correr_secuencia, correr_solo). correr_secuencia(seq): un proceso de lote con los mensajes de seq en ese orden (ficheros
    %03d-<caso>.hl7), -> {caso: valor}. correr_solo(c): el adaptador mensaje con c solo, -> valor."""
    n = [0]
    os.makedirs(trabajo, exist_ok=True)

    def _correr(ad, nombres):
        n[0] += 1
        d = os.path.join(trabajo, "c%04d" % n[0])
        corpus = d + "-corpus"
        os.makedirs(corpus)
        for i, c in enumerate(nombres, 1):
            with open(os.path.join(corpus, "%03d-%s.hl7" % (i, c)), "w", encoding="utf-8", newline="") as g:
                g.write(textos[c])
        try:
            _correr_carpeta(ad, corpus, d, artefactos, ejecutor)
            return {f["caso"].split("-", 1)[1]: valor(f) for f in filas(d)}
        finally:
            shutil.rmtree(d, ignore_errors=True)
            shutil.rmtree(corpus, ignore_errors=True)

    return (lambda seq: _correr(ad_lote, list(seq))), (lambda c: _correr(ad_mensaje, [c])[c])


class _Agotado(Exception):
    pass


def aislar(c, previos, v_lote, v_mensaje, correr_secuencia, correr_solo, presupuesto=PRESUPUESTO_CASO, culpable=None):
    """§5.2: la secuencia mínima de una diferencia por bisección sobre el prefijo del lote, el culpable solo y, si no basta, poda
    uno a uno; reproducida con 3 de 3 de la secuencia y 3 de 3 del caso solo."""
    res = {"caso": c, "tipo": None, "culpable": None, "secuencia_minima": None, "registro": [], "repeticiones": {"secuencia": [], "solo": []}}
    if v_lote == v_mensaje:
        res["tipo"] = "igual"
        return res
    reg = res["registro"]

    def repro(pref):
        if len(reg) >= presupuesto:
            raise _Agotado()
        t0 = time.time()
        v = correr_secuencia(list(pref) + [c])[c]
        reg.append({"modo": "lote", "secuencia": list(pref) + [c], "como_en_lote": v == v_lote, "s": round(time.time() - t0, 1)})
        return v == v_lote

    def solo():
        if len(reg) >= presupuesto:
            raise _Agotado()
        t0 = time.time()
        v = correr_solo(c)
        reg.append({"modo": "mensaje", "secuencia": [c], "como_en_lote": v == v_lote, "como_mensaje": v == v_mensaje,
                    "s": round(time.time() - t0, 1)})
        return v

    try:
        seq = None
        if culpable is not None and culpable in previos and repro([culpable]):
            seq, res["culpable"] = [culpable], culpable
        if seq is None:
            P = list(previos)
            if not repro(P):
                res["tipo"] = "no_determinismo" if (repro(P) or repro(P)) else "otra_causa"
                return res
            if repro([]):
                vs = [solo() for _ in range(3)]
                res["tipo"] = "adaptador" if all(v == v_mensaje for v in vs) else "no_determinismo"
                return res
            lo, hi = 0, len(P)
            while hi - lo > 1:
                mid = (lo + hi) // 2
                if repro(P[:mid]):
                    hi = mid
                else:
                    lo = mid
            res["culpable"] = P[hi - 1]
            if repro([P[hi - 1]]):
                seq = [P[hi - 1]]
            else:
                S = P[:hi]
                for i in range(len(S) - 2, -1, -1):
                    T = S[:i] + S[i + 1:]
                    if repro(T):
                        S = T
                seq = S
        res["secuencia_minima"] = seq + [c]
        rs = [repro(seq) for _ in range(3)]
        ss = [solo() == v_mensaje for _ in range(3)]
        res["repeticiones"] = {"secuencia": rs, "solo": ss}
        res["tipo"] = "arrastre" if all(rs) and all(ss) else "no_determinismo"
    except _Agotado:
        res["tipo"] = "no_aislada"
    return res


def adjudicar(trabajo, artefactos, ejecutor=None, reloj_s=RELOJ_ADJUDICACION_S):
    """Cada diferencia de COMPARACION-AR.json, en el orden del lote de su corpus; antes de bisecar se prueba el culpable ya
    conocido del corpus (§5.3)."""
    comp = _leer(os.path.join(trabajo, "COMPARACION-AR.json"))
    L1 = os.path.join(trabajo, "L1")
    co = _leer(os.path.join(L1, "corpus", "CASOS.json"))
    orden = collections.defaultdict(list)
    for x in co["casos"]:
        orden[x["corpus"]].append(x["caso"])
    textos = {}
    for x in co["casos"]:
        textos[x["caso"]] = open(os.path.join(L1, "corpus", x["fichero"]), encoding="utf-8").read()
    ix = {n: {_clave(f): f for f in filas(os.path.join(trabajo, n))} for n in ("L1", "L2", "M1", "M2")}
    sec, solo = hacer_corredores(AD_LOTE, AD_MENSAJE, artefactos, textos, os.path.join(trabajo, "adjudicacion"), ejecutor)
    t0, conocido, out, agotado = time.time(), {}, [], False
    for d in sorted(comp["diferencias"], key=lambda d: (d["corpus"], d["posicion_en_lote"])):
        k = (d["corpus"], d["caso"])
        v = [valor(ix[n][k]) for n in ("L1", "L2", "M1", "M2")]
        if time.time() - t0 > reloj_s:
            agotado = True
            a = {"caso": d["caso"], "tipo": "no_aislada", "registro": [], "motivo": "reloj de la adjudicación agotado"}
        else:
            previos = orden[d["corpus"]][:orden[d["corpus"]].index(d["caso"])]
            a = aislar(d["caso"], previos, v[0], v[2], sec, solo, culpable=conocido.get(d["corpus"]))
            if a["tipo"] == "arrastre" and len(a["secuencia_minima"]) == 2:
                conocido.setdefault(d["corpus"], a["secuencia_minima"][0])
        a.update({"corpus": d["corpus"], "adjudicacion": adjudicar_caso(v[0], v[1], v[2], v[3], a)})
        out.append(a)
    res = {"diferencias": len(comp["diferencias"]), "casos": out, "reloj_agotado": agotado,
           "por_tipo": dict(collections.Counter(a["adjudicacion"] for a in out)),
           "inseparables": [a["caso"] for a in out if a["adjudicacion"] == "no_determinismo"]}
    _escribir(os.path.join(trabajo, "ADJUDICACION-AR.json"), res)
    return res


# ---------------------------------------------------------------------------- de las diferencias a las cifras (§6)
def ensamblar(destino, corridas):
    """Un árbol como el que leen cv3_minimos.juzgar y cv3_clases.main: evidencias/<conv>/{adt,oru,muestras}, minimos/<conv>/ y
    juicio.jsonl de esos corpus. corridas: {conversor del estudio: carpeta de la corrida} (el id de la corrida puede ser otro)."""
    shutil.rmtree(destino, ignore_errors=True)
    os.makedirs(destino)
    todas = []
    for conv, carpeta in corridas.items():
        ev = os.path.join(carpeta, "evidencias", _cid(carpeta))
        for corpus in RESULTADO_CORPUS:
            if os.path.isdir(os.path.join(ev, corpus)):
                shutil.copytree(os.path.join(ev, corpus), os.path.join(destino, "evidencias", conv, corpus))
        if os.path.isdir(os.path.join(ev, "minimos")):
            shutil.copytree(os.path.join(ev, "minimos"), os.path.join(destino, "minimos", conv))
        todas += [dict(f, conversor=conv) for f in filas(carpeta) if f["corpus"] in RESULTADO_CORPUS]
    with open(os.path.join(destino, "juicio.jsonl"), "w", encoding="utf-8") as g:
        for f in todas:
            g.write(json.dumps(f, ensure_ascii=False) + "\n")
    return destino


def juzgar_arbol(arbol):
    """cv3_minimos.juzgar y cv3_clases.main sobre el árbol, sin tocarlos. -> (CLASES, mínimos)."""
    guardado = sys.argv
    sys.argv = ["x", "--silencio"]
    try:
        import cv3_minimos
        import cv3_clases
        with redirect_stdout(io.StringIO()):
            cv3_minimos.juzgar(os.path.join(arbol, "minimos"), os.path.join(arbol, "minimos-AR.json"))
            cv3_clases.main(os.path.join(arbol, "juicio.jsonl"), os.path.join(arbol, "minimos-AR.json"), os.path.join(arbol, "evidencias"),
                            os.path.join(arbol, "CLASES-AR.json"))
    finally:
        sys.argv = guardado
    return _leer(os.path.join(arbol, "CLASES-AR.json")), _leer(os.path.join(arbol, "minimos-AR.json"))


def _planas(d):
    out = {}
    cl = (d or {}).get("clases")
    if cl:
        for k, v in (cl.get("frase") or {}).items():
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    out["frase.%s.%s" % (k, k2)] = v2
            elif k != "C_nota":
                out["frase." + k] = v
        for x in cl.get("clases") or []:
            for corpus, n in (x.get("casos") or {}).items():
                out["clases.%s.casos.%s" % (x["id"], corpus)] = n
            out["clases.%s.confirmada_con_par" % x["id"]] = x.get("confirmada_con_par")
        for k, n in (cl.get("sin_clase") or {}).items():
            out["sin_clase.%s" % k] = n
        for k, n in (cl.get("convenciones") or {}).items():
            out["convenciones.%s" % k] = n
    mi = (d or {}).get("minimos")
    if mi:
        for p in mi.get("pares") or []:
            out["minimos.%s.confirmada" % p["id"]] = p.get("confirmada")
            lfh = p.get("linuxforhealth") or {}
            for s in ("caso", "control"):
                out["minimos.%s.linuxforhealth.%s.sale" % (p["id"], s)] = (lfh.get(s) or {}).get("sale")
        out["minimos.confirmadas"] = mi.get("confirmadas")
    for corpus, cats in ((d or {}).get("por_corpus") or {}).items():
        for cat, n in cats.items():
            out["por_corpus.%s.%s" % (corpus, cat)] = n
    return out


def donde(cifra):
    for pre, docs in CIFRAS_PUBLICADAS:
        if cifra.startswith(pre):
            return docs
    return []


def diferencias_cifras(lote, mensaje, publicado=None):
    """Una fila por cifra que difiere entre lote y mensaje (cada uno {clases, minimos, por_corpus}), con lo publicado y dónde."""
    a, b, p = _planas(lote), _planas(mensaje), _planas(publicado)
    out = []
    for k in sorted(set(a) | set(b)):
        if a.get(k) != b.get(k):
            fila = {"cifra": k, "lote": a.get(k), "mensaje": b.get(k), "publicado": p.get(k), "donde_se_publica": donde(k)}
            nums = [fila[x] if fila[x] is not None else 0 for x in ("publicado", "lote", "mensaje")]
            if all(isinstance(x, int) and not isinstance(x, bool) for x in nums):
                fila["corregida"] = nums[0] + (nums[2] - nums[1])
            out.append(fila)
    return out


def _por_corpus_informe(corrida):
    inf = _leer(os.path.join(corrida, "INFORME.json"))
    return {c: v["categorias"] for c, v in inf["por_corpus"].items() if c in RESULTADO_CORPUS}


def recalcular(trabajo, ms):
    """§6.2: Microsoft (ya rejuzgado con el juez actual) con LinuxForHealth en lote y con LinuxForHealth mensaje a mensaje; las
    cifras que cambian entre los dos, y aparte la deriva del juez desde lo publicado."""
    datos = {}
    for nombre, corrida in (("lote", "L1"), ("mensaje", "M1")):
        arbol = ensamblar(os.path.join(trabajo, "recalculo", nombre), {"microsoft": ms, "linuxforhealth": os.path.join(trabajo, corrida)})
        cl, mi = juzgar_arbol(arbol)
        shutil.copyfile(os.path.join(arbol, "CLASES-AR.json"), os.path.join(trabajo, "CLASES-AR-%s.json" % nombre))
        shutil.copyfile(os.path.join(arbol, "minimos-AR.json"), os.path.join(trabajo, "minimos-AR-%s.json" % nombre))
        datos[nombre] = {"clases": cl, "minimos": mi, "por_corpus": _por_corpus_informe(os.path.join(trabajo, corrida))}
    r2 = _leer(os.path.join(CVD, "RESULTADO-CV2.json"))["por_conversor"]["linuxforhealth"]
    pub = {"clases": _leer(os.path.join(CVD, "CLASES-CV3.json")), "minimos": _leer(os.path.join(CVD, "RESULTADO-CV3-minimos.json")),
           "por_corpus": {c: v["categorias"] for c, v in r2.items() if c in RESULTADO_CORPUS}}
    jueces = {datos[n]["clases"]["juez"] for n in datos} | {datos[n]["minimos"]["juez"] for n in datos}
    deriva = [{"cifra": d["cifra"], "publicado": d["lote"], "con_el_juez_actual": d["mensaje"], "donde_se_publica": d["donde_se_publica"]}
              for d in diferencias_cifras(pub, datos["lote"])]                  # DV-AR-12: columnas con su nombre
    res = {"juez": sorted(jueces), "cifras": diferencias_cifras(datos["lote"], datos["mensaje"], pub),
           "deriva_del_juez": deriva,
           "_deriva_del_juez": "lo publicado (juez de CV3) frente a LinuxForHealth en lote con el juez actual; no se corrige aquí",
           "juez_publicado": {"clases": pub["clases"]["juez"], "minimos": pub["minimos"]["juez"]}}
    _escribir(os.path.join(trabajo, "CIFRAS-AR.json"), res)
    return res


# ---------------------------------------------------------------------------- el resultado (§10, paso 13)
def _tabla(cab, filas_):
    out = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    out += ["| " + " | ".join(str(x) for x in f) + " |" for f in filas_]
    return "\n".join(out)


def _h(x):
    return "%s %s %s" % tuple(x)


def resultado_md(control):
    """RESULTADO-ARRASTRE.md desde el control (comparación, adjudicación, cifras, ruido, positivos). Sin rutas de máquina."""
    comp = control["comparacion"]
    n = comp["n"]["comparados"]
    adj = control.get("adjudicacion") or []
    arr = [a for a in adj if a.get("tipo") == "arrastre"]
    k = len(arr)
    if k and control.get("cifras") is None:
        raise ValueError("hay %d casos por arrastre y no hay CIFRAS-AR.json" % k)
    nd = comp["n"]["no_deterministas"]
    otras = comp["n"]["diferentes"] - k
    if k:
        frase = "cambian %d casos de %d, por arrastre de estado; las cifras publicadas que cambian son estas" % (k, n)
    else:
        frase = "Convertidos mensaje a mensaje, los %d casos del estudio dan los mismos veredictos que en lote" % n
    extra = []
    if nd:
        extra.append("%d no deterministas (cambian también entre dos corridas del mismo modo)" % nd)
    if otras:
        extra.append("%d diferencias que no son arrastre o no se aislaron" % otras)
    if comp["n"]["sin_par"] or comp["n"]["caja"]:
        extra.append("%d sin par y %d de caja" % (comp["n"]["sin_par"], comp["n"]["caja"]))
    L = ["# Resultado de la etapa 21: el arrastre de estado de LinuxForHealth en el estudio publicado", "",
         "**%s%s.**" % ("Convertidos mensaje a mensaje, " + frase if k else frase, (", salvo " + "; ".join(extra)) if extra else ""), "",
         "La pregunta, fijada antes de medir en `ANTES-ETAPA-ARRASTRE.md`: ¿cambia algún veredicto del estudio de conversores publicado "
         "cuando LinuxForHealth convierte cada mensaje en su propio proceso, en vez de todos en un solo proceso, como se hizo en el "
         "estudio?", "",
         "## Qué se comparó", "",
         "Los %d casos del estudio, con el mismo juez (`%s`) y el mismo conversor (huella `%s`) a los dos lados: en lote (un proceso "
         "Java por corpus, el adaptador `cv/adaptadores/linuxforhealth.json`, como en el estudio) y mensaje a mensaje (un proceso por "
         "mensaje, `cv/adaptadores/linuxforhealth-mensaje.json`). Dos corridas de cada modo. Un caso es «diferente» solo si las dos de "
         "lote coinciden, las dos de mensaje coinciden y lote y mensaje no (S-AR-10). Las 40 bases VXU viajan en las corridas como "
         "control y no entran en N." % (n, str(control.get("juez", ""))[:12], str(control.get("conversor", ""))[:12]), ""]
    filas_ = [(c, v["n"], v.get("iguales", "—"), v.get("diferentes", 0), v.get("no_deterministas", 0), v.get("sin_par", 0) + v.get("caja", 0))
              for c, v in sorted(comp["por_corpus"].items())]
    L += [_tabla(("Corpus", "Casos", "Iguales", "Diferentes", "No deterministas", "Sin par o caja"), filas_), ""]
    pos = control.get("positivo") or {}
    ru = control.get("ruido") or {}
    L += ["## Los controles", "",
          "- **Positivo, la secuencia VL11** (un VXU con RXA-17 sin código y después el nominal, en un proceso): %s." % (
              "sale en las dos repeticiones: en lote el segundo pierde `manufacturer`, mensaje a mensaje no" if pos.get("pasa_vl11") else "NO sale"),
          "- **Positivo, el corpus VXU:** %s." % (
              "los casos VXU que cambian son exactamente VXU-B18 a VXU-B40, los 23 de F7 en `vx/VX2.md`, y solo por RXA-17" if pos.get("pasa_vxu")
              else "NO da los 23 de F7"),
          "- **Negativo, dos corridas del mismo modo:** veredictos distintos %d en lote y %d mensaje a mensaje; errores con otra firma %d "
          "y %d. Umbral de parada: cero (Q-AR-D-1, Jev)." % (
              len((ru.get("lote") or {}).get("veredicto", [])), len((ru.get("mensaje") or {}).get("veredicto", [])),
              len((ru.get("lote") or {}).get("errores", [])), len((ru.get("mensaje") or {}).get("errores", [])))]
    for modo in ("lote", "mensaje"):
        m = ((ru.get(modo) or {}).get("bundle") or {}).get("mascara") or []
        if m:
            L.append("- **Ruido del Bundle, %s** (solo se mide; no entra en N, Q-AR-D-4): %s." % (
                modo, "; ".join("`%s.%s` en %d casos" % (rt, r, c) for rt, r, c in m[:12]) + ("…" if len(m) > 12 else "")))
    L.append("")
    if comp["diferencias"]:
        L += ["## Las diferencias", ""]
        ad = {(a.get("corpus"), a.get("caso")): a for a in adj}
        filas_ = []
        for d in comp["diferencias"]:
            a = ad.get((d["corpus"], d["caso"]), {})
            filas_.append((d["corpus"], d["caso"], ", ".join(_h(x) for x in d["solo_en_lote"]) or "—",
                           ", ".join(_h(x) for x in d["solo_en_mensaje"]) or "—", a.get("tipo", "sin adjudicar"),
                           " → ".join(a.get("secuencia_minima") or []) or "—"))
        L += [_tabla(("Corpus", "Caso", "Solo en lote", "Solo mensaje a mensaje", "Adjudicación", "Secuencia mínima"), filas_), ""]
    if comp.get("no_deterministas"):
        L += ["## No deterministas", "", ", ".join("%s/%s" % (d["corpus"], d["caso"]) for d in comp["no_deterministas"]), ""]
    L += ["## Las cifras publicadas", ""]
    cif = control.get("cifras")
    if cif:
        L += [_tabla(("Cifra", "Publicada", "Lote", "Mensaje a mensaje", "Corregida", "Dónde se publica"),
                     [(c["cifra"], c.get("publicado"), c["lote"], c["mensaje"], c.get("corregida", "—"), ", ".join(c["donde_se_publica"]))
                      for c in cif]), ""]
    else:
        L += ["Ninguna cambia entre lote y mensaje a mensaje.", ""]
    der = control.get("deriva_del_juez")
    if der is not None:
        L += ["La deriva del juez desde los resultados sellados (lo publicado frente al lote con el juez actual) se declara aparte y no "
              "se corrige aquí: %s." % ("ninguna fila" if not der else "%d filas, en `cv/ar/CIFRAS-AR.json`" % len(der)), ""]
    if control.get("prevision"):
        L += ["## La previsión sellada", "", control["prevision"], ""]
    L += ["## Límites", "",
          "- «Lote» es un proceso por corpus en el orden alfabético de los nombres, el de la herramienta y el del arnés. Otro orden, todo "
          "en un solo proceso o un servicio de larga vida puede arrastrar distinto, y no se mide (L-AR-1).",
          "- Solo se ve lo que ve el juez; el Bundle crudo se compara solo para medir el ruido (L-AR-2, Q-AR-D-4).",
          "- Un arrastre necesita que su disparador esté en el corpus y antes del caso (L-AR-4).",
          "- Microsoft queda fuera: convierte un mensaje por proceso por construcción (L-AR-7).",
          "- Las muestras de los proyectos no viajan con el repositorio: un tercero repite adt, oru y mínimos (L-AR-14).", "",
          "## Cómo repetir", "",
          "Desde `verificador/`, con los artefactos del estudio (`lfh/lib`, `lfh/clases`, `lfh/Arnes.java`):", "",
          "```bash", "python3 cv/ar/prueba_ar.py",
          "python3 cv/ar/control_ar.py <artefactos> <muestras> <salida> --ms <corrida de Microsoft>", "```", ""]
    return "\n".join(L)


def comprobar_sello(prevision, sello, base=None):
    """El sello lista «sha256  ruta» (rutas relativas a su carpeta, o a base); cuadra si cada fichero listado tiene esa huella, la
    previsión está en la lista y lleva todas las claves de CLAVES_PREVISION."""
    base = base or os.path.dirname(os.path.abspath(sello))
    vistos = set()
    try:
        for linea in open(sello, encoding="utf-8"):
            m = re.match(r"^([0-9a-f]{64})  (\S+)\s*$", linea)
            if not m:
                continue
            ruta = os.path.realpath(os.path.join(base, m.group(2)))
            if hashlib.sha256(open(ruta, "rb").read()).hexdigest() != m.group(1):
                return False
            vistos.add(ruta)
        p = _leer(prevision)
    except (OSError, ValueError):
        return False
    return os.path.realpath(prevision) in vistos and all(k in p for k in CLAVES_PREVISION)


# ---------------------------------------------------------------------------- las órdenes
def _pasa(trabajo, nombre):
    try:
        return bool(_leer(os.path.join(trabajo, nombre)).get("pasa"))
    except (OSError, ValueError):
        return False


def comparar(L1, L2, M1, M2, trabajo):
    """-> 6 sin los dos controles; si no, escribe COMPARACION-AR.json (con controles.positivo_vxu) y devuelve 0."""
    if not (_pasa(trabajo, "POSITIVO-AR.json") and _pasa(trabajo, "RUIDO-AR.json")):
        print("comparar: faltan POSITIVO-AR.json o RUIDO-AR.json con «pasa»: el aparato no se ha probado (S-AR-13)")
        return 6
    c = comparar_juicios(filas(L1), filas(L2), filas(M1), filas(M2))
    c["controles"] = {"positivo_vl11": True, "negativo": True, "positivo_vxu": positivo_vxu(c)}
    c["corridas"] = {"lote": [os.path.basename(L1), os.path.basename(L2)], "mensaje": [os.path.basename(M1), os.path.basename(M2)]}
    _escribir(os.path.join(trabajo, "COMPARACION-AR.json"), c)
    print("comparación: %s; vxu %s" % (c["n"], "como F7" if c["controles"]["positivo_vxu"] else "NO como F7"))
    return 0


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a:
        print(__doc__)
        return 1
    o = a[0]
    if o == "positivo":
        r = positivo_vl11(a[1], a[2])
        _escribir(os.path.join(a[2], "POSITIVO-AR.json"), r)
        print("positivo VL11: %s" % ("sale" if r["pasa"] else "NO sale: %s" % [x["motivos"] for x in r["repeticiones"]]))
        return 0 if r["pasa"] else 3
    if o == "ruido":
        r = ruido(a[1], a[2])
        _escribir(a[3], r)
        print("ruido: %d veredictos, %d errores, Bundle en %d casos" % (len(r["veredicto"]), len(r["errores"]), r["bundle"]["casos"]))
        return 0
    if o == "comparar":
        return comparar(a[1], a[2], a[3], a[4], a[5])
    if o == "adjudicar":
        r = adjudicar(a[2], a[1])
        print("adjudicación: %s" % r["por_tipo"])
        return 0
    if o == "recalcular":
        r = recalcular(a[3], a[2])
        print("cifras que cambian: %d; deriva del juez: %d filas" % (len(r["cifras"]), len(r["deriva_del_juez"])))
        return 0
    if o == "resultado":
        t = a[1]
        ctl = {"comparacion": _leer(os.path.join(t, "COMPARACION-AR.json"))}
        for clave, f in (("adjudicacion", "ADJUDICACION-AR.json"), ("cifras", "CIFRAS-AR.json"), ("positivo", "POSITIVO-AR.json"),
                         ("ruido", "RUIDO-AR.json"), ("control", "CONTROL-AR.json")):
            if os.path.exists(os.path.join(t, f)):
                ctl[clave] = _leer(os.path.join(t, f))
        ctl["adjudicacion"] = (ctl.get("adjudicacion") or {}).get("casos", [])
        if "cifras" in ctl:
            ctl["deriva_del_juez"] = ctl["cifras"].get("deriva_del_juez")
            ctl["cifras"] = ctl["cifras"].get("cifras")
        ident = (ctl.get("control") or {}).get("identidades") or {}
        ctl["juez"], ctl["conversor"] = ident.get("juez", ""), ident.get("huella", "")
        md = resultado_md(ctl)
        open(a[2], "w", encoding="utf-8").write(md)
        print("escrito %s" % os.path.basename(a[2]))
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
