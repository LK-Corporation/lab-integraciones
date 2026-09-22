#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MATRIZ DE OBSERVABILIDAD: que puede el agente establecer con lo que ve.

Lo pidio la revision de arquitectura (gpt, 21-sep) y es la unica de las cuatro
que apunto a algo que no estaba mirado: el agente ve el mensaje, el canonico,
el ACK y el log; NO ve el recurso FHIR que quedo guardado ni la respuesta HTTP.

Si algun operador de fallo silencioso mete su defecto DESPUES del canonico,
pedirle al agente que lo detecte es pedirle que adivine, y ninguna arquitectura
lo arregla. Eso no es un problema del modelo: es evidencia insuficiente.

QUE HACE, Y QUE NO. No opina. Para cada caso reconstruye el canonico que las
reglas PUBLICADAS producen a partir del mensaje —las mismas que usa fmsg.py—
y lo coteja contra el canonico observado. Luego mira el ACK y el log. La
clasificacion final es:

  CANON    el canonico observado discrepa del que las reglas producen
  ACK      el acuse es negativo, o su MSA-2 no casa con el MSH-10 del mensaje
  LOG      hay una fila de log que no es INFO
  PISTA    solo hay una fila INFO cuyo texto menciona algo, sin afirmarlo
  NINGUNA  las tres fuentes se ven normales: NO ES DECIDIBLE con estas tres

Un operador en NINGUNA o en PISTA es un operador cuyo veredicto el agente no
puede establecer, solo inferir. Que la clave lo puntue como fallo es una
decision que hay que tomar a proposito, no por descuido.

Uso: python3 observabilidad.py
"""
import collections
import csv
import io
import json
import re
import sys

sys.path.insert(0, ".")
import fmsg as F

PAYLOADS = "payloads_despues.json"
CLAVE = "tabla_casos_v2.tsv"


# --------------------------------------------------------------- el mensaje
def delimitadores(crudo):
    """MSH-1 y MSH-2, leidos del mensaje. Nunca supuestos.

    Lo cazo el control negativo: con `MSH2_SEPARADORES_ALTERNATIVOS` el
    separador de componente es `!`, y una rutina que parte por `^` canta
    discrepancia en cinco casos limpios.
    """
    linea = ""
    for l in crudo.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if l.startswith("MSH"):
            linea = l
            break
    campo_s = linea[3:4] if len(linea) > 3 else "|"
    cod = linea[4:8] if len(linea) > 7 else "^~" + chr(92) + "&"
    comp = cod[0:1] or "^"
    rep = cod[1:2] or "~"
    esc = cod[2:3] or chr(92)
    sub = cod[3:4] or "&"
    return campo_s, comp, rep, esc, sub


def desescapar(s, d):
    """Las secuencias de la §2.7, con el caracter de escape declarado."""
    campo_s, comp, rep, esc, sub = d
    for sec, val in (("F", campo_s), ("S", comp), ("T", sub), ("R", rep),
                     ("E", esc)):
        s = s.replace(esc + sec + esc, val)
    return s


def segmentos(crudo, d=None):
    d = d or delimitadores(crudo)
    campo_s = d[0]
    r = collections.defaultdict(list)
    for linea in crudo.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if linea.strip():
            r[linea.split(campo_s, 1)[0]].append(linea.split(campo_s))
    return r


def campo(seg, n):
    return seg[n] if n < len(seg) else ""


def componente(rep, i, d):
    """El componente i de una repeticion, con los subcomponentes unidos."""
    campo_s, comp, repc, esc, sub = d
    partes = rep.split(comp)
    if i >= len(partes):
        return ""
    # El circuito los une CON UN ESPACIO. El prompt dice «unidos» y no
    # precisa con que; esto es lo observado, y lo cazo el control negativo.
    return desescapar(partes[i].replace(sub, " "), d)


# ------------------------------------------ el canonico que las reglas piden
def canonico_esperado(crudo):
    """Las reglas PUBLICADAS en el prompt, no la implementacion de la DTL.

    Solo las cinco propiedades que un lector puede cotejar mirando el mensaje.
    MsgControlId sale de MSH-10 tal cual; Identifier y el nombre usan la
    misma eleccion de repeticion que `fmsg.py` publica.
    """
    d = delimitadores(crudo)
    campo_s, comp, repc, esc, sub = d
    segs = segmentos(crudo, d)
    msh = segs["MSH"][0] if segs["MSH"] else []
    pid = segs["PID"][0] if segs["PID"] else []
    e = {}
    # MSH-10: en MSH el campo 1 son los separadores, asi que MSH-n = seg[n-1]
    e["MsgControlId"] = campo(msh, 9)

    def elegir(bruto, icomp, marca):
        """La regla publicada, pero con los delimitadores de ESTE mensaje."""
        reps = bruto.split(repc) if bruto else []
        dentro = reps[:F.LIMITE_REP]
        for i, r in enumerate(dentro):
            partes = r.split(comp)
            if len(partes) > icomp and partes[icomp].strip() == marca:
                return r
        for r in dentro:
            if r.replace(comp, "").strip():
                return r
        return ""

    r3 = elegir(campo(pid, 3), 4, "MR")
    e["Identifier"] = componente(r3, 0, d)
    r5 = elegir(campo(pid, 5), 6, "L")
    e["FamilyName"] = componente(r5, 0, d)
    e["GivenName"] = " ".join(x for x in (componente(r5, 1, d),
                                          componente(r5, 2, d)) if x)
    e["BirthDate"] = componente(campo(pid, 7), 0, d)
    e["Gender"] = componente(campo(pid, 8), 0, d)
    return e


def canonico_observado(recorrido):
    d = {}
    dentro = False
    for linea in recorrido.split("\n"):
        if "MENSAJE CANONICO" in linea:
            dentro = True
            continue
        if dentro:
            if linea.strip() == "" or not linea.startswith("  "):
                if ":" not in linea:
                    dentro = False
                    continue
            if ":" in linea:
                k, v = linea.split(":", 1)
                d[k.strip()] = v.strip()
    return d


# El prompt lo dice con todas las letras: un campo ausente cuyo resultado
# lleva el valor que significa «ausente» en el destino es FIDELIDAD, no
# perdida. PID-8 vacio -> `unknown`. Lo cazo el control negativo.
NORM_SEXO = {"F": "female", "M": "male", "O": "other", "U": "unknown",
             "": "unknown"}


def discrepa(esp, obs):
    """Las que un lector puede cotejar, con la normalizacion publicada."""
    fuera = []
    for k in ("MsgControlId", "Identifier", "FamilyName"):
        if k in obs and esp.get(k, "") != obs[k]:
            fuera.append("%s: mensaje=%r canonico=%r" % (k, esp.get(k, ""), obs[k]))
    # nombre: los subcomponentes se unen, asi que se compara sin separadores
    if "GivenName" in obs:
        a = esp.get("GivenName", "").split()
        b = obs["GivenName"].split()
        if a != b:
            fuera.append("GivenName: mensaje=%r canonico=%r"
                         % (esp.get("GivenName", ""), obs["GivenName"]))
    # fecha: YYYYMMDD -> YYYY-MM-DD
    if "BirthDate" in obs:
        c = esp.get("BirthDate", "")[:8]
        n = "%s-%s-%s" % (c[:4], c[4:6], c[6:8]) if len(c) == 8 else c
        if n != obs["BirthDate"]:
            fuera.append("BirthDate: mensaje=%r canonico=%r"
                         % (esp.get("BirthDate", ""), obs["BirthDate"]))
    if "Gender" in obs:
        n = NORM_SEXO.get(esp.get("Gender", ""), "?")
        if n != "?" and n != obs["Gender"]:
            fuera.append("Gender: mensaje=%r canonico=%r"
                         % (esp.get("Gender", ""), obs["Gender"]))
    return fuera


# ---------------------------------------------- conformidad y estructura
TABLA_SEXO_0001 = {"F", "M", "O", "U", "A", "N", ""}


def _fecha_imposible(v):
    """PID-7 es un TS: YYYY[MM[DD]]. Lo que no lo sea, o no pueda existir."""
    s = (v or "").strip()
    if not s:
        return ""
    if not s.isdigit():
        return "PID-7 no es numerica: %r" % s[:20]
    if len(s) not in (4, 6, 8):
        return "PID-7 de longitud %d, que no es 4, 6 ni 8" % len(s)
    a = int(s[:4])
    if len(s) >= 6:
        m = int(s[4:6])
        if not 1 <= m <= 12:
            return "PID-7 con mes %02d" % m
    if len(s) == 8:
        import datetime
        try:
            datetime.date(a, int(s[4:6]), int(s[6:8]))
        except ValueError:
            return "PID-7 con fecha que no existe: %r" % s
    if a >= 2027:
        return "PID-7 en el futuro: %r" % s
    return ""


def predicados(crudo, obs):
    """Los hallazgos que NO son discrepancia de campo. Mecanicos, no a ojo."""
    d = delimitadores(crudo)
    campo_s, comp, repc, esc, sub = d
    segs = segmentos(crudo, d)
    pid = segs["PID"][0] if segs["PID"] else []
    lineas = [l for l in crudo.replace("\r\n", "\n").replace("\r", "\n").split("\n")
              if l.strip()]
    conf, estr = [], []

    # --- desplazamiento de campos: va PRIMERO, es el diagnostico ---------
    # Un separador de campo sin escapar dentro de un campo corre todos los
    # de despues. Se reconoce porque PID-7 deja de parecer una fecha y la
    # fecha aparece un campo mas alla.
    p7 = componente(campo(pid, 7), 0, d).strip()
    p8 = componente(campo(pid, 8), 0, d).strip()
    if p7 and p8 and not (len(p7) in (4, 6, 8) and p7.isdigit()) \
            and len(p8) == 8 and p8.isdigit():
        estr.append("los campos del PID estan desplazados: PID-7=%r y la"
                    " fecha aparece en PID-8. Un separador sin escapar."
                    % p7[:16])
        return conf, estr

    # --- conformidad -----------------------------------------------------
    m = _fecha_imposible(componente(campo(pid, 7), 0, d))
    if m:
        conf.append(m)
    g = componente(campo(pid, 8), 0, d).strip().upper()
    if g not in TABLA_SEXO_0001:
        conf.append("PID-8 fuera de la tabla 0001: %r" % g[:12])
    # una barra invertida que no abre una de las secuencias de la 2.7
    pid5 = campo(pid, 5)
    i = pid5.find(esc)
    while i >= 0:
        if pid5[i + 1:i + 2] not in ("F", "S", "T", "R", "E", "H", "N"):
            conf.append("PID-5 con %r que no abre secuencia valida" % esc)
            break
        i = pid5.find(esc, i + 1)
    # un interrogante dentro de un nombre: firma de conversion de juego
    if "?" in componente(campo(pid, 5), 0, d) \
            or "?" in componente(campo(pid, 5), 1, d):
        conf.append("hay un '?' dentro del nombre (PID-5): firma de una"
                    " conversion de juego de caracteres con perdida")
    # MSH-18 declara un juego y los bytes dicen otra cosa
    msh = segs["MSH"][0] if segs["MSH"] else []
    j = campo(msh, 17).upper()
    if j and ("ASCII" in j or "8859/1" in j or j == "7BIT"):
        if any(ord(ch) > 127 for ch in crudo):
            conf.append("MSH-18 declara %r y el mensaje trae bytes altos" % j[:16])

    # --- estructura ------------------------------------------------------
    if len(segs["PID"]) > 1:
        estr.append("hay %d segmentos PID donde va uno" % len(segs["PID"]))
    if len(segs["MSH"]) > 1:
        estr.append("hay %d segmentos MSH: dos mensajes en un marco"
                    % len(segs["MSH"]))
    # la marcada MAS ALLA del limite que el circuito mira: elige otra
    for bruto, icomp, marca, eti in ((campo(pid, 3), 4, "MR", "PID-3.5"),
                                     (campo(pid, 5), 6, "L", "PID-5.7")):
        reps = bruto.split(repc) if bruto else []
        for r in reps[F.LIMITE_REP:]:
            partes = r.split(comp)
            if len(partes) > icomp and partes[icomp].strip() == marca:
                estr.append("la repeticion con %s=%s cae mas alla de las %d"
                            " que el circuito mira" % (eti, marca, F.LIMITE_REP))
                break
    return conf, estr


# ------------------------------------------------------------ el ACK y el log
def mira_ack(crudo, recorrido):
    m = re.search(r"^MSA\|([A-Z]{2})\|(\S*)", recorrido, re.M)
    if not m:
        return ["no hay MSA en el acuse"]
    cod, ctrl = m.group(1), m.group(2)
    d = delimitadores(crudo)
    segs = segmentos(crudo, d)
    msh10 = campo(segs["MSH"][0], 9) if segs["MSH"] else ""
    fuera = []
    if cod != "AA":
        fuera.append("MSA-1=%s" % cod)
    if msh10 and ctrl != msh10:
        fuera.append("MSA-2=%r pero MSH-10=%r" % (ctrl, msh10))
    if not msh10 and ctrl:
        fuera.append("MSA-2=%r con MSH-10 vacio: identificador inventado" % ctrl)
    return fuera


def mira_log(texto):
    graves, pistas = [], []
    for linea in texto.split("\n"):
        if not linea.strip():
            continue
        if re.search(r"\b(ERROR|WARNING)\b", linea):
            graves.append(linea.strip()[:150])
        elif re.search(r"\b(ya existia|condicional|trunc|omit|ignor)", linea, re.I):
            pistas.append(linea.strip()[:150])
    return graves, pistas


# --------------------------------------------------------------------- salida
def main():
    pay = {x["caso"]: x for x in json.load(io.open(PAYLOADS, encoding="utf-8"))}
    filas = list(csv.DictReader(io.open(CLAVE, encoding="utf-8"), delimiter="\t"))

    por_op = collections.defaultdict(list)
    for f in filas:
        if f["esperado_veredicto"] != "RESULTADO_INCORRECTO_SILENCIOSO":
            continue
        x = pay.get(f["caso_id"])
        if not x:
            continue
        esp = canonico_esperado(x["mensaje"])
        obs = canonico_observado(x["recorrido"])
        d = discrepa(esp, obs)
        a = mira_ack(x["mensaje"], x["recorrido"])
        g, p = mira_log(x["log"])
        conf, estr = predicados(x["mensaje"], obs)
        if d:
            clase, detalle = "CANON", d[0]
        elif a:
            clase, detalle = "ACK", a[0]
        elif conf:
            clase, detalle = "CONFORM", conf[0]
        elif estr:
            clase, detalle = "ESTRUCT", estr[0]
        elif g:
            clase, detalle = "LOG", g[0]
        elif p:
            clase, detalle = "PISTA", p[0]
        else:
            clase, detalle = "NINGUNA", ""
        por_op[f["operador"]].append((clase, detalle, f["caso_id"]))

    print("=" * 100)
    print("MATRIZ DE OBSERVABILIDAD — fallo silencioso: ¿lo ve con mensaje, traza y log?")
    print("=" * 100)
    print("%-32s %-9s %5s  %s" % ("operador", "clase", "casos", "por que"))
    print("-" * 100)
    cuenta = collections.Counter()
    problemas = []
    for op in sorted(por_op):
        cs = por_op[op]
        clases = collections.Counter(c for c, _, _ in cs)
        clase = clases.most_common(1)[0][0]
        detalle = next((d for c, d, _ in cs if c == clase), "")
        mezcla = "" if len(clases) == 1 else "  [MEZCLA: %s]" % dict(clases)
        cuenta[clase] += 1
        print("%-32s %-9s %5d  %s%s" % (op, clase, len(cs), detalle[:52], mezcla))
        if clase in ("PISTA", "NINGUNA"):
            problemas.append((op, clase, len(cs), cs[0][2]))

    print("-" * 100)
    print("operadores por clase: %s"
          % ", ".join("%s %d" % kv for kv in sorted(cuenta.items())))

    # el control negativo: los limpios no deben salir con discrepancia
    falsos = 0
    limpios = 0
    for f in filas:
        if f["esperado_veredicto"] != "SIN_PROBLEMA":
            continue
        x = pay.get(f["caso_id"])
        if not x:
            continue
        limpios += 1
        esp = canonico_esperado(x["mensaje"])
        obs = canonico_observado(x["recorrido"])
        conf, estr = predicados(x["mensaje"], obs)
        if (discrepa(esp, obs) or mira_ack(x["mensaje"], x["recorrido"])
                or conf or estr):
            falsos += 1
    print()
    print("CONTROL NEGATIVO: de %d casos SIN_PROBLEMA, esta rutina marca %d."
          % (limpios, falsos))
    print("  (si no es 0, la rutina de cotejo esta mal y la matriz no vale)")

    if problemas:
        print()
        print("=" * 100)
        print("LO QUE EL AGENTE NO PUEDE ESTABLECER, SOLO INFERIR")
        print("=" * 100)
        for op, clase, n, caso in problemas:
            print("  %-32s %-8s %2d casos   ej. %s" % (op, clase, n, caso))
        print()
        print("  NINGUNA = la evidencia no se distingue de la de un caso")
        print("  limpio. Esta rutina marca 0 de 120 limpios, asi que un")
        print("  operador aqui no es «no lo he sabido ver»: es que no hay")
        print("  nada que ver. Dos mundos distintos, la misma observacion.")
        print()
        print("  PISTA = la evidencia SI difiere de la de un limpio, pero no")
        print("  prueba el fallo. Se puede inferir, no establecer.")
        print()
        print("  En los dos casos hay que decidir a proposito si el veredicto")
        print("  correcto es el de la clave o es NO_SE. No es arquitectura.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
