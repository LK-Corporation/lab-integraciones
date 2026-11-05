#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 31: el conductor de la etapa 30 con la regla de Q-MV-4 (ivm/decision-jev-qmv4.md), hecho con ivm/hacer_validar_ivm.py:
si IRIS echa en falta un segmento justo donde hay uno que v2.5 no define, el que sobra es ese, y se quita. Lo que sigue es la
cabecera de la 30.
Etapa 30: el conductor (iv/diseno-iv-fable.md §1-2; decisiones de Jev en iv/decision-jev-qiv.md).

Pasa cada mensaje por `Validate` de IRIS (clase Lab.IV.Validar en iris-ai, USER) bandera a bandera, y enumera todos los errores de
cada clase con un clon al que se le enmudece el error anterior. IRIS solo valida; el enmudecer y la clasificación van aquí.
- Estructuras (Q-IV-D-2, las dos): la de MSH-9.3 si viene, y la que el esquema resuelve por la 0354; si coinciden, una sola.
- Pasadas: `d`; `dm-z` (una vez); `dm` enumerado sobre el original, que deja el clon estructural; `dr`, `dl`, `dt` y `dn`
  enumerados, cada uno sobre su copia del clon estructural. En la estructura solo se quitan segmentos (los no reconocidos y los
  Z); un segmento requerido que falta se anota y cierra la pasada, sin insertar nada (un segmento vacío fabricaría errores en
  cascada, medido en el control). Si IRIS echa en falta un segmento justo donde hay un Z, el error es del Z, fuera de sitio.
- Cuenta (lo que el estándar sostiene): E siempre; Z solo fuera de sitio (Q-IV-D-8: si detrás hay algún segmento que no es Z);
  R si el estándar lo hace obligatorio; L si el valor pasa la longitud del estándar (Q-IV-D-9); T si la tabla es de HL7 en el
  estándar y el valor no está en su Apéndice A (Q-IV-D-3: las de usuario son aviso); N si el estándar no deja repetir.
  Lo que IRIS dice y el estándar no sostiene queda con `cuenta: false` y su motivo.
Uso, desde fase12:
  python3 iv/validar_iv.py <corpus> <salida.jsonl> [--solo patrón] [--tope 40]
  (<corpus> tiene CORPUS-IV.json, como lo escribe iv/corpus_iv.py)"""
import glob
import json
import os
import re
import subprocess
import sys
import time

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIV = os.path.normpath(os.path.join(FASE, "..", "privado"))
EST = json.load(open(os.path.join(FASE, "estructuras_25.json"), encoding="utf-8"))["campos"]
TIPOS = json.load(open(os.path.join(FASE, "iv", "TABLAS-TIPO-IV.json"), encoding="utf-8"))["tablas"]
_TV = json.load(open(os.path.join(PRIV, "iv", "TABLAS-VALORES-IV.json"), encoding="utf-8"))
VALORES = {k: set(v) for k, v in _TV["valores"].items()}
PATRONES = {k: [re.compile(x) for x in v] for k, v in _TV["patrones"].items()}


def en_tabla(tabla, valor):
    return valor in VALORES.get(tabla, ()) or any(r.match(valor) for r in PATRONES.get(tabla, ()))
CONTENEDOR = "iris-ai"
TOPE = 40
# etapa 31 (Q-MV-4): los segmentos que el texto de v2.5 define, por su tabla de atributos
TXT25 = os.path.normpath(os.path.join(FASE, "..", "estandares", "hl7v2", "HL7_Messaging_v25", "txt"))
SEG25 = set()
for _f in sorted(glob.glob(os.path.join(TXT25, "*.txt"))):
    for _l in open(_f, encoding="utf-8", errors="replace"):
        _m = re.search(r"HL7 Attribute Table\s*[-–]\s*([A-Z][A-Z0-9]{2})\b", _l)
        if _m:
            SEG25.add(_m.group(1))
assert {"MSH", "PID", "PV1", "RXA", "TXA"} <= SEG25 and "ARV" not in SEG25, "no se leyeron las tablas de atributos de v2.5"

RX = {
    "R": re.compile(r"Required field missing in segment (\d+):(\w+)\.\s+Missing field (\d+)"),
    "L": re.compile(r"Field size restriction exceeded in segment (\d+):(\w+)\.\s+Field (\d+), repetition (\d+)"),
    "T": re.compile(r"Invalid value '(.*?)' appears in segment (\d+):(\w+), field (\d+), repetition (\d+), component (\d+), "
                    r"subcomponent (\d+), but (does not appear in|no value is permitted by) code table [\w.]+:(\w+)"),
    "Zseg": re.compile(r"Unrecognized 'Z' Segment (\d+):'(\w+)'"),
    "Eseg": re.compile(r"Segment (\d+):'(\w+)'"),
    "Ereq": re.compile(r"Missing required (\w+) element at segment (\d+)"),
}


# ---------------------------------------------------------------------------------------------- el texto del mensaje
def segmentos(texto):
    return [s for s in texto.replace("\r\n", "\r").replace("\n", "\r").split("\r") if s != ""]


def unir(segs):
    return "\r".join(segs) + "\r"


def separadores(segs):
    """(campo, componente, repetición, subcomponente) de MSH-1 y MSH-2; los de siempre si el MSH no los trae."""
    m = segs[0] if segs and segs[0].startswith("MSH") and len(segs[0]) > 3 else "MSH|^~\\&"
    fs, enc = m[3], m[4:].split(m[3], 1)[0]
    enc = enc + "^~\\&"[len(enc):] if len(enc) < 4 else enc
    return fs, enc[0], enc[1], enc[3]


def editar(segs, idx, campo, rep=None, comp=None, sub=None, valor=""):
    """El campo `campo` del segmento `idx` (1 = MSH), su repetición, componente o subcomponente, con `valor`, con los
    separadores del propio mensaje."""
    fs, cs, rs, ss = separadores(segs)
    segs = list(segs)
    s = segs[idx - 1]
    partes = s.split(fs)
    i = campo - 1 if partes[0] == "MSH" else campo
    while len(partes) <= i:
        partes.append("")
    if rep is None:
        partes[i] = valor
    else:
        reps = partes[i].split(rs)
        while len(reps) < rep:
            reps.append("")
        if comp is None:
            reps[rep - 1] = valor
        else:
            comps = reps[rep - 1].split(cs)
            while len(comps) < comp:
                comps.append("")
            if sub is None:
                comps[comp - 1] = valor
            else:
                subs = comps[comp - 1].split(ss)
                while len(subs) < sub:
                    subs.append("")
                subs[sub - 1] = valor
                comps[comp - 1] = ss.join(subs)
            reps[rep - 1] = cs.join(comps)
        partes[i] = rs.join(reps)
    segs[idx - 1] = fs.join(partes)
    return segs


def leer(segs, idx, campo, rep):
    fs, _, rs, _ = separadores(segs)
    partes = segs[idx - 1].split(fs)
    i = campo - 1 if partes[0] == "MSH" else campo
    if i >= len(partes):
        return ""
    reps = partes[i].split(rs)
    return reps[rep - 1] if rep - 1 < len(reps) else ""


def msh9(segs):
    fs = separadores(segs)[0]
    p = segs[0].split(fs) if segs and segs[0].startswith("MSH") else []
    return p[8] if len(p) > 8 else ""


def msh9_partes(segs):
    return msh9(segs).split(separadores(segs)[1])


# ---------------------------------------------------------------------------------------------- IRIS
def lote(pedidos):
    """Una llamada a Lab.IV.Validar.Lote con todos los pedidos; devuelve {k: respuesta}."""
    if not pedidos:
        return {}
    datos = "".join(json.dumps(p, ensure_ascii=False) + "\n" for p in pedidos).encode("utf-8")
    subprocess.run(["docker", "exec", "-i", CONTENEDOR, "sh", "-c", "mkdir -p /tmp/iv && cat > /tmp/iv/lote-entrada.jsonl"],
                   input=datos, check=True)
    guion = (b'set sc=##class(Lab.IV.Validar).Lote("/tmp/iv/lote-entrada.jsonl","/tmp/iv/lote-salida.jsonl")\n'
             b'write "lote: ",$select($system.Status.IsOK(sc):"OK",1:$system.Status.GetErrorText(sc)),!\nhalt\n')
    r = subprocess.run(["docker", "exec", "-i", CONTENEDOR, "iris", "session", "IRIS", "-U", "USER"], input=guion,
                       capture_output=True, timeout=3600)
    if b"lote: OK" not in r.stdout:
        raise SystemExit("PARADA: el lote no salió bien: %r" % r.stdout[-500:])
    out = subprocess.run(["docker", "exec", CONTENEDOR, "cat", "/tmp/iv/lote-salida.jsonl"], capture_output=True, check=True).stdout
    res = {}
    for l in out.decode("utf-8").splitlines():
        if l.strip():
            x = json.loads(l)
            res[x["k"]] = x
    faltan = [p["k"] for p in pedidos if p["k"] not in res]
    if faltan:
        raise SystemExit("PARADA: el lote no devolvió %d pedidos (%s…)" % (len(faltan), faltan[0]))
    return res


# ---------------------------------------------------------------------------------------------- un error de IRIS
def parsear(texto_error, spec):
    """-> dict con la clase de IRIS y su lugar, o clase X si no se reconoce la forma."""
    e = texto_error.replace("ERROR <Ens>ErrGeneral: ", "").replace("ERROR <EnsEDI>", "").strip()
    if not spec.startswith("dm") and ("ErrMap" in texto_error or "Cannot validate segment schemas without a category" in texto_error):
        return {"clase_iris": "ESTRUCTURA"}       # con la estructura rota, IRIS no llega a los campos: no es un error nuevo
    m = RX["T"].search(e)
    if m:
        return {"clase_iris": "T", "valor": m.group(1), "idx": int(m.group(2)), "seg": m.group(3), "campo": int(m.group(4)),
                "rep": int(m.group(5)), "comp": int(m.group(6)), "sub": int(m.group(7)),
                "tabla_vacia_en_iris": m.group(8).startswith("no value"), "tabla": m.group(9).zfill(4)}
    m = RX["R"].search(e)
    if m:
        return {"clase_iris": "R", "idx": int(m.group(1)), "seg": m.group(2), "campo": int(m.group(3))}
    m = RX["L"].search(e)
    if m:
        return {"clase_iris": "L", "idx": int(m.group(1)), "seg": m.group(2), "campo": int(m.group(3)), "rep": int(m.group(4))}
    m = RX["Zseg"].search(e)
    if m:
        return {"clase_iris": "Z", "idx": int(m.group(1)), "seg": m.group(2)}
    m = RX["Ereq"].search(e)
    if m:
        return {"clase_iris": "E", "tipo_e": "requerido_ausente", "seg": m.group(1), "idx": int(m.group(2))}
    if spec.startswith("dm"):
        m = RX["Eseg"].search(e)
        if m:
            return {"clase_iris": "E", "tipo_e": "no_esperado", "idx": int(m.group(1)), "seg": m.group(2)}
    return {"clase_iris": "X"}


def enmudecer(segs, p):
    """-> (segs nuevos, cómo) o (None, motivo) si no se sabe enmudecer."""
    c = p["clase_iris"]
    if c in ("Z",) or (c == "E" and p.get("tipo_e") == "no_esperado"):
        if not 1 <= p["idx"] <= len(segs) or p["idx"] == 1:
            return None, "indice_fuera"
        return segs[:p["idx"] - 1] + segs[p["idx"]:], "quitado"
    if c == "E" and p.get("tipo_e") == "requerido_ausente":
        return None, "requerido_ausente"            # no se inserta: el segmento vacío fabricaría errores en cascada
    if c == "R":
        return editar(segs, p["idx"], p["campo"], valor="X"), "relleno"
    if c == "L":
        p["longitud_valor"] = len(leer(segs, p["idx"], p["campo"], p["rep"]))
        return editar(segs, p["idx"], p["campo"], rep=p["rep"], valor=""), "vaciado"
    if c == "T":
        return editar(segs, p["idx"], p["campo"], p["rep"], p["comp"], p["sub"], valor=""), "vaciado"
    return None, "no_se_sabe"


# ---------------------------------------------------------------------------------------------- lo que el estándar sostiene
def atributo(seg, campo):
    return (EST.get(seg) or {}).get("atributos", {}).get("%s-%d" % (seg, campo))


def clasificar(p, original):
    """Añade `clase`, `cuenta` y `motivo` a un error parseado (sobre el mensaje original para los Z)."""
    c = p["clase_iris"]
    p["cuenta"], p["motivo"] = True, None
    if c == "Z":                                   # `al_final` lo pone el recorrido, con el mensaje de ese momento
        p["clase"] = "Z"
        p["cuenta"] = not p.get("al_final")
        p["motivo"] = ("Z al final del mensaje: el estándar permite segmentos locales (Q-IV-D-8)" if p.get("al_final") else
                       "Z fuera de sitio: IRIS echa en falta un segmento donde está el Z (Q-IV-D-8)")
    elif c == "E":
        p["clase"] = "E"
    elif c == "R":
        p["clase"] = "R"
        a = atributo(p["seg"], p["campo"])
        p["opt_estandar"] = a.get("opt") if a else None
        if a is None:
            p["cuenta"], p["motivo"] = True, "campo sin atributos en estructuras_25.json: a lectura"
        elif a.get("opt") != "R":
            p["cuenta"], p["motivo"] = False, "el estándar no lo hace obligatorio (OPT %s)" % a.get("opt")
    elif c == "L":
        p["clase"] = "L"
        a = atributo(p["seg"], p["campo"])
        p["len_estandar"] = a.get("len") if a else None
        lv = p.get("longitud_valor")
        if p["len_estandar"] is None or lv is None:
            p["cuenta"], p["motivo"] = True, "sin longitud del estándar: a lectura"
        elif lv <= p["len_estandar"]:
            p["cuenta"], p["motivo"] = False, "cabe en la longitud del estándar (%d de %d): la del esquema de IRIS es menor" % (
                lv, p["len_estandar"])
    elif c == "T":
        t = TIPOS.get(p["tabla"])
        p["tipo_tabla"] = t["tipo"] if t else None
        p["tabla_en_conflicto"] = bool(t and t["conflicto"])
        if p["tabla_vacia_en_iris"]:
            p["clase"], p["cuenta"], p["motivo"] = "T_USR", False, "tabla sin valores en el esquema de IRIS (tabla_usuario_vacia)"
        elif t is None:
            p["clase"], p["cuenta"], p["motivo"] = "T_HL7", True, "tabla que el texto no tipa: a lectura"
        elif t["tipo"] != "HL7":
            p["clase"], p["cuenta"], p["motivo"] = "T_USR", False, "tabla de usuario en el estándar (Q-IV-D-3: aviso)"
        else:
            p["clase"] = "T_HL7"
            if not VALORES.get(p["tabla"]) and not PATRONES.get(p["tabla"]):
                p["cuenta"], p["motivo"] = True, "tabla de HL7 sin valores en el Apéndice A: a lectura"
            elif en_tabla(p["tabla"], p["valor"]):
                p["cuenta"], p["motivo"] = False, "el valor está en la tabla del estándar (por valor o por patrón): lo rechaza el esquema de IRIS"
            elif p["tabla"] == "0396":
                p["motivo"] = "sistema de codificación que la 0396 de v2.5 no trae (Q-IV-D-11: cuenta)"
    elif c == "N":
        p["clase"] = "N"
    else:
        p["clase"], p["cuenta"], p["motivo"] = "X", False, "forma de error no reconocida"
    return p


# ---------------------------------------------------------------------------------------------- el recorrido
class Tarea:
    def __init__(self, msg, variante, doctype, spec, segs, enumerar):
        self.msg, self.variante, self.doctype, self.spec = msg, variante, doctype, spec
        self.segs, self.enumerar = segs, enumerar
        self.vueltas, self.errores, self.ultimo, self.fin = 0, [], None, None

    def k(self):
        return "%s|%s|%s|%d" % (self.msg["id"], self.variante, self.spec, self.vueltas)


def correr(corpus_dir, salida, solo=None, tope=TOPE):
    filas_corpus = json.load(open(os.path.join(corpus_dir, "CORPUS-IV.json"), encoding="utf-8"))["filas"]
    msgs = []
    for f in filas_corpus:
        if solo and not re.search(solo, f["id"]):
            continue
        datos = open(os.path.join(corpus_dir, f["fichero"]), "rb").read()
        texto = datos.decode("utf-8")
        segs = segmentos(texto)
        msgs.append({"id": f["id"], "corpus": f["corpus"], "sha256": f["sha256"], "texto": texto, "segs": segs,
                     "no_ascii": any(b > 127 for b in datos), "msh9": msh9(segs)})
    # las estructuras: MSH-9.3 y la del esquema (0354)
    tipos = sorted({"_".join(msh9_partes(m["segs"])[:2]) for m in msgs})
    res = lote([{"k": "r|" + t, "op": "resolver", "tipo": t} for t in tipos])
    resuelto = {t: res["r|" + t].get("doctype") or "" for t in tipos}
    tareas = []
    for m in msgs:
        comps = msh9_partes(m["segs"])
        e3 = comps[2] if len(comps) > 2 and comps[2] else None
        esq = resuelto["_".join(comps[:2])]
        m["doctype_msh93"] = ("2.5:" + e3) if e3 else None
        m["doctype_esquema"] = esq or None
        vs = {}
        if m["doctype_msh93"]:
            vs["msh93"] = m["doctype_msh93"]
        if esq and esq != m["doctype_msh93"]:
            vs["esquema"] = esq
        m["variantes"] = vs
        m["doctype_discrepante"] = bool(m["doctype_msh93"] and esq and esq != m["doctype_msh93"])
        m["separadores"] = "".join(separadores(m["segs"]))
        m["importado"] = {"segmentos_fichero": len(m["segs"]), "segmentos_iris": None, "ok": False}
        if not vs:                                   # ni MSH-9.3 ni la 0354: un tipo sin estructura (error E, cuenta)
            m["resultado"] = {"ninguna": {"doctype": None, "pasadas": {"dm": {"fin": "tipo_no_resuelto", "vueltas": 0, "errores": [
                {"clase_iris": "E", "tipo_e": "tipo_no_resuelto", "seg": "MSH", "idx": 1, "pasada": "dm", "vuelta": 0,
                 "crudo": "sin estructura: ni MSH-9.3 ni la 0354 del esquema"}]}}}}
            continue
        m["resultado"] = {}
        for v, dt in vs.items():
            m["resultado"][v] = {"doctype": dt, "pasadas": {}}
            tareas.append(Tarea(m, v, dt, "d", m["segs"], False))
            tareas.append(Tarea(m, v, dt, "dm-z", m["segs"], False))
            tareas.append(Tarea(m, v, dt, "dm", m["segs"], True))
    por_id = {m["id"]: m for m in msgs}
    activas, rondas, t0 = tareas, 0, time.time()
    while activas:
        rondas += 1
        res = lote([{"k": t.k(), "op": "validar", "texto": unir(t.segs), "doctype": t.doctype, "spec": t.spec} for t in activas])
        siguientes = []
        for t in activas:
            r = res[t.k()]
            if t.vueltas == 0 and t.spec == "d":
                t.msg["importado"] = {"segmentos_fichero": len(t.msg["segs"]), "segmentos_iris": r.get("segs"),
                                      "ok": bool(r.get("importado")) and r.get("segs") == len(t.msg["segs"])}
            if not r.get("importado"):
                t.fin = "no_importado"
            elif r.get("ok"):
                t.fin = "ok"
            else:
                p = parsear(r.get("error") or "", t.spec)
                p.update({"pasada": t.spec, "vuelta": t.vueltas + 1, "crudo": r.get("error")})
                if p["clase_iris"] == "Z":
                    p["al_final"] = all(s.startswith("Z") for s in t.segs[p["idx"]:])
                elif (p["clase_iris"] == "E" and p.get("tipo_e") == "requerido_ausente" and 1 <= p["idx"] <= len(t.segs)
                      and t.segs[p["idx"] - 1].startswith("Z")):
                    # IRIS echa en falta un segmento justo donde hay un Z: el que sobra es el Z, fuera de sitio
                    p.update({"clase_iris": "Z", "seg_que_falta": p["seg"], "seg": t.segs[p["idx"] - 1].split("|", 1)[0],
                              "al_final": False})
                elif (p["clase_iris"] == "E" and p.get("tipo_e") == "requerido_ausente" and 1 < p["idx"] <= len(t.segs)
                      and t.segs[p["idx"] - 1][:3] not in SEG25 and not t.segs[p["idx"] - 1].startswith("Z")):
                    # etapa 31 (Q-MV-4): IRIS echa en falta un segmento justo donde hay uno que v2.5 no define; el que sobra
                    # es ese, como con los Z, y se quita como un segmento no esperado
                    p.update({"tipo_e": "no_esperado", "seg_que_falta": p["seg"], "seg": t.segs[p["idx"] - 1][:3]})
                if p["clase_iris"] == "ESTRUCTURA":
                    t.fin = "estructura_rota"                # los campos de esta pasada quedan sin evaluar
                elif not t.enumerar:
                    t.errores.append(p)
                    t.fin = "un_error"
                elif r.get("error") == t.ultimo:
                    t.fin = "no_enmudecible"
                elif p["clase_iris"] == "X":
                    t.errores.append(p)
                    t.fin = "no_reconocido"
                else:
                    nuevos, como = enmudecer(t.segs, p)
                    p["enmudecido"] = como
                    t.errores.append(p)
                    if nuevos is None and como == "requerido_ausente":
                        t.fin = "requerido_ausente"          # la estructura se cierra aquí; el clon es lo que hay
                    elif nuevos is None:
                        t.fin = "no_enmudecible"
                    elif t.vueltas + 1 >= tope:
                        t.fin = "tope_alcanzado"
                    else:
                        t.segs, t.ultimo, t.vueltas = nuevos, r.get("error"), t.vueltas + 1
            if t.fin:
                t.msg["resultado"][t.variante]["pasadas"][t.spec] = {"fin": t.fin, "errores": t.errores, "vueltas": t.vueltas + 1}
                if t.spec == "dm":                        # el clon estructural: lo que queda tras enmudecer la estructura
                    for spec in ("dr", "dl", "dt", "dn"):
                        siguientes.append(Tarea(t.msg, t.variante, t.doctype, spec, t.segs, True))
            else:
                siguientes.append(t)
        activas = siguientes
        sys.stderr.write("ronda %d: %d tareas siguen (%.0f s)\n" % (rondas, len(activas), time.time() - t0))
    with open(salida, "w", encoding="utf-8") as fh:
        for m in msgs:
            fila = {k: m[k] for k in ("id", "corpus", "sha256", "msh9", "no_ascii", "doctype_msh93", "doctype_esquema",
                                      "doctype_discrepante", "importado", "separadores")}
            fila["variantes"] = {}
            for v, rv in m["resultado"].items():
                errores = []
                for spec in ("dm", "dr", "dl", "dt", "dn"):
                    for p in rv["pasadas"].get(spec, {}).get("errores", []):
                        errores.append(clasificar(dict(p), m["segs"]))
                fines = {s: rv["pasadas"][s]["fin"] for s in rv["pasadas"]}
                aparte = {s: rv["pasadas"][s]["errores"] for s in ("d", "dm-z") if rv["pasadas"].get(s, {}).get("errores")}
                n = {}
                for p in errores:
                    n[p["clase"]] = n.get(p["clase"], 0) + 1
                que_cuenta = [p for p in errores if p["cuenta"]]
                fila["variantes"][v] = {
                    "doctype": rv["doctype"], "fines": fines, "primer_error_d_y_dm-z": aparte, "errores": errores,
                    "n_por_clase": n, "n_que_cuentan": len(que_cuenta),
                    "veredicto_iris": "invalido" if errores else "valido",
                    "veredicto_que_cuenta": "invalido" if que_cuenta else "valido",
                    "incompleto": any(f in ("no_enmudecible", "tope_alcanzado", "no_reconocido", "no_importado") for f in fines.values()),
                    "campos_sin_evaluar": sorted(s for s, f in fines.items() if f == "estructura_rota")}
            fh.write(json.dumps(fila, ensure_ascii=False, sort_keys=True) + "\n")
    print("%d mensajes, %d rondas, %.0f s -> %s" % (len(msgs), rondas, time.time() - t0, salida))


if __name__ == "__main__":
    a = sys.argv[1:]
    solo = a[a.index("--solo") + 1] if "--solo" in a else None
    tope = int(a[a.index("--tope") + 1]) if "--tope" in a else TOPE
    correr(os.path.abspath(a[0]), os.path.abspath(a[1]), solo, tope)
