#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Acuse de referencia: implementación del diseño de Fable (`diseno-acuse-referencia-fable.md`, commit
fde861d), escrito a ciegas desde HL7 v2.5 y FHIR R4 y las decisiones del sitio S1-S4. Calcula qué acuse
DEBERÍA haber recibido el emisor y lo compara con el observado. Determinista.

Las etiquetas [E2 §x], [E3 §x], [T0357], [F §x], [S1-S4], [A-n], AMB-n remiten al diseño. Desviaciones de
la implementación respecto al diseño, declaradas:
  - DV1: P7 no dice qué hacer con un código HTTP que no está en su tabla. Los 2xx se tratan como éxito
    (AA) y el resto como sistema (AR 207, «ambigua»).
  - DV2: las tablas 0003, 0004 y 0211 se leen del texto del estándar (encargo_medida.md §8), no se copian.
  - DV3: en P2, MSH-9 es un campo MSG: se lee por componentes; «vacío» sigue la definición de §2.1.5.
  - DV4: la tabla 0104 se copia de [E2 §2.15.9.12]: `_tabla` no puede leerla (sus filas parecen cabeceras).
Decisiones S19-S29 (diseno-s19-s21-fable.md §1, §5, §6): versiones 2.x desde 2.4 [S19]; tolerancia de tabla en
mensajes posteriores a 2.5 [S22] con AE 103 como alternativa aceptada [S26]; AR <código> tolerado si FHIR devolvió
400/422 [S21][S24]; AR 207 si el destino falló por sistema [S25][S29], con AE <código> como alternativa [S28].
Decisiones S31, S35, S36 (diseno-s31-s34-fable.md): el receptor juzga cada marco MLLP; al mensaje al que la partición
dejó sin EVN/PID/PV1 se le espera AE 100 y se aceptan AE/AR 100/101; un marco sin MSH no es mensaje; ACK sobrante, nota.
Multi-tipo (diseno-multitipo-fable.md §1-§4, S47-S56): el contrato es un PUNTO DE ENTRADA (puntos_entrada.py) que llega
por `pe` (parámetro > e["punto_entrada"] > adt_a01). P2 generaliza tipo/evento/estructura con la tabla 0354; P3 usa la
estructura plana de hoy para adt_a01 y el emparejador recursivo (estructuras_hl7) para los demás; P4/P5/S10 recorren las
listas del PE. Con adt_a01 y perfil «lab» la salida es byte a byte la de siempre.

Uso: python3 acuse_referencia.py --autoprueba
"""
import collections
import io
import os
import re
import sys
import unicodedata

import estructuras_hl7 as EH
import lectura_evidencia as LE
import mapeador_oru as MO
import mapeador_referencia as MR
import puntos_entrada as PE

NIVEL = "consumido"                      # [S6] los campos R que el contrato no consume no cuentan; «estricto», a petición
# Perfiles del sitio. «lab» es el de siempre (cap. 2 + S-n) y no tiene mandos. Los demás son módulos PRIVADOS perfil_*.py
# (dict REGLAS de mandos) en LAB_PERFILES o en ../privado/perfiles; no van al repositorio. Con «lab», _p() devuelve None
# y ninguna rama nueva se ejecuta.
PERFIL = "lab"
PERFILES = {"lab": {}}


def _cargar_perfiles():
    import importlib.util
    d = os.environ.get("LAB_PERFILES") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "privado", "perfiles")
    if not os.path.isdir(d):
        return
    for f in sorted(os.listdir(d)):
        if f.startswith("perfil_") and f.endswith(".py"):
            spec = importlib.util.spec_from_file_location(f[:-3], os.path.join(d, f))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            PERFILES[mod.REGLAS["nombre"]] = mod.REGLAS


_cargar_perfiles()


def _p(mando):
    """Valor del mando en el perfil activo; None con «lab» (o si el perfil no lo define)."""
    return None if PERFIL == "lab" else PERFILES[PERFIL].get(mando)


def equiv_msa1(m1):
    """MSA-1 observado tal como lo lee el perfil activo (p. ej. la grafía C- equivalente a la A-)."""
    eq = _p("msa1_equivalencias")
    return eq.get(m1, m1) if eq else m1
EM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "medida", "encargo_medida.md")


# ---------------------------------------------------------------------------- tablas del estándar
def _tabla(cabecera, max_indent=20):
    """Lee los valores de una tabla del texto del estándar (DV2): primera columna de las filas cuya
    sangría es ≤ max_indent, desde la cabecera hasta la siguiente cabecera de tabla o sección."""
    ls = io.open(EM, encoding="utf-8").read().split("\n")
    # la cabecera de la TABLA, no una mención «Refer to …»: la línea es solo el título y le sigue «Value»
    i = next(k for k, l in enumerate(ls) if l.strip() == cabecera and any("Value" in z for z in ls[k + 1:k + 4]))
    out = []
    for l in ls[i + 1:]:
        if re.search(r"(HL7|User-defined) Table \d{4}", l) or re.match(r"^\d+\.\d+(\.\d+)*\s", l.strip()) \
                or re.match(r"^\s*([a-z]\)|\u2022)", l):
            break
        if re.search(r"Health Level Seven|Page \d+-\d+|Final Standard|July 2003|Chapter \d+:", l):
            continue                                                  # pie o cabecera de página del estándar
        m = re.match(r"^(\s*)(\S(?:.*?\S)?)\s{2,}\S", l)
        if not m or len(m.group(1)) > max_indent or m.group(2) in ("Value",):
            continue
        out.append(m.group(2))
    return out


T0003 = set(v for v in _tabla("HL7 Table 0003 - Event type") if re.fullmatch(r"[A-Z0-9]{3}", v))
T0004 = set(v for v in _tabla("User-defined Table 0004 - Patient Class", 45) if re.fullmatch(r"[A-Z]", v))
T0211 = set(_tabla("HL7 Table 0211 - Alternate character sets", 14))
T0001 = {"F", "M", "O", "U", "A", "N"}                                   # [E3 §3.4.2.8]
T0008 = {"AA", "AE", "AR", "CA", "CE", "CR"}
T0103 = {"D", "P", "T"}
T0155 = {"AL", "NE", "ER", "SU"}
T0104 = ("2.0", "2.0D", "2.1", "2.2", "2.3", "2.3.1", "2.4", "2.5")    # DV4 [E2 §2.15.9.12]
TABLA_DE = {"PID-8": "0001", "EVN-1": "0003", "PV1-2": "0004", "MSH-18": "0211",
            "OBX-11": "0085", "OBX-2": "0125", "ORC-1": "0119", "TXA-17": "0271",        # las cuatro últimas: PE nuevos (§4)
            "OBR-25": "0123", "OBX-8": "0078",                                           # oru_fhir (diseno-oru-fable.md §5.1)
            "PID-30": "0136"}                                                           # adt_fhir (diseno-adt-fable.md §4.1)
LEN = {("MSH", 3): 227, ("MSH", 4): 227, ("MSH", 7): 26, ("MSH", 9): 15, ("MSH", 10): 20, ("MSH", 11): 3,
       ("MSH", 12): 60, ("MSH", 15): 2, ("MSH", 16): 2, ("MSH", 18): 16, ("EVN", 1): 3, ("EVN", 2): 26,
       ("PID", 1): 4, ("PID", 3): 250, ("PID", 5): 250, ("PID", 7): 26, ("PID", 8): 1, ("PV1", 1): 4, ("PV1", 2): 1}
POS, OBLIGATORIOS = PE.POS, PE.OBLIGATORIOS          # [E3 §3.3.1]; literales MOVIDOS a puntos_entrada.py (adt_a01), ROL exento


def _tabla_pe(codigo):
    """Tabla de códigos por número: las de hoy (0001, 0003, 0004, 0211) y las leídas del texto para los PE nuevos (DV2)."""
    propias = {"0001": T0001, "0003": T0003, "0004": T0004, "0211": T0211,
               "0123": set(MO.T0123), "0078": set(MO.T0078),                          # oru_fhir (DV-ORU-5: 0123 del ConceptMap)
               "0136": {"Y", "N"}}                                                    # adt_fhir: PID-30 [E2A 0136]
    if codigo in propias:
        return propias[codigo]
    return set(EH.TABLAS[codigo])


def _etq_base(etq):
    """«OBX(3)-11» -> «OBX-11» (DV-ORU-1: la etiqueta lleva el índice de la ocurrencia; las tablas se buscan sin él)."""
    return re.sub(r"\(\d+\)", "", etq)


def _etq_partes(etq):
    """«OBX(3)-11» -> (OBX, 3, 11); «MSH-9.3» -> (MSH, 0, 9)."""
    mo = re.match(r"^([A-Z][A-Z0-9]{2})(?:\((\d+)\))?-(\d+)", etq)
    return (mo.group(1), int(mo.group(2) or 0), int(mo.group(3))) if mo else (etq.split("-")[0], 0, 0)


# ---------------------------------------------------------------------------- lectura de la evidencia §2
def _plano(s):
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn")


CAIDA = r"inalcanz|caid|parad|deten|apagad|unreach|down|refus|timeout|sin respuesta"


def clasificar_entorno(entorno):
    out = set()
    for e in entorno or []:
        t = _plano(e if isinstance(e, str) else str(e))
        if "fhir" in t and re.search(CAIDA, t):
            out.add("fhir_inalcanzable")
        elif re.search(r"adttcpin|mllp|2575|produccion|servicio tcp|receptor|escucha", t) and re.search(CAIDA, t):
            out.add("receptor_parado")
        else:
            out.add("otro")
    return out


def clasificar_conexion(conexion):
    ts = [_plano(c) for c in conexion or []]
    fallida = any(re.search(r"rechaz|refused|no establec|no se pudo|timeout", t) for t in ts) and \
        not any("establecida" in t for t in ts)
    return {"conexion_fallida": fallida, "ack_recibido": any("ack recibido" in t for t in ts)}


def resultado_log(sesiones, msh10=None):
    """§2.3: último código HTTP del log (emparejado por MSH-10 si aparece) y si hay filas Error."""
    filas = [f for s in sesiones or [] for f in s.get("log") or []]
    if msh10:
        propias = [f for f in filas if ("MSH-10=%s" % msh10) in (f.get("texto") or "")]
        filas = propias or filas
    http = None
    for f in filas:
        m = re.search(r"\bHTTP\s*/?\s*(\d{3})\b", f.get("texto") or "")
        if m:
            http = int(m.group(1))
    error = any((f.get("tipo") or "").lower() == "error" for f in filas)
    return http, error


SEPS_ESTANDAR = "|^~\\&"


def _seps(m):
    """Los delimitadores que declara el mensaje (MSH-1 y MSH-2)."""
    return "".join([m.f, m.c, m.r, m.e, m.s]) if m is not None else SEPS_ESTANDAR


def _vacio_en(x, seps):
    """§2.1.5 (B3): ausente, o solo blancos y los delimitadores DEL MENSAJE. '""' cuenta como presente [A-9]."""
    return x is None or (all(ch.isspace() or ch in seps for ch in x) and x.strip() != '""')


def _vacio(x):
    """Fuera de un mensaje concreto: con los delimitadores estándar. Dentro de esperado() se liga a los del mensaje (B3)."""
    return _vacio_en(x, SEPS_ESTANDAR)


def _len_perfil():
    """Longitudes que el perfil activo fija distintas de v2.5: {(seg, n): máximo}; {} con «lab». Hoy solo MSH-10 (H10).
    La usan _len() (el acuse) y, por el gancho MR.LONG_PERFIL, el mapeador (Truncado): una sola fuente."""
    return {("MSH", 10): _p("len_msh10")} if _p("len_msh10") else {}


def _len(pe=None):
    x = _len_perfil()
    lp = (pe or {}).get("longitudes") or {}                          # PE nuevos: longitudes de los campos que juzgan (§1.2)
    if x or lp:
        d = dict(LEN)
        d.update(lp)
        d.update(x)
        return d
    return LEN


MR.LONG_PERFIL = _len_perfil      # gancho: el mapeador no importa este módulo (ciclo); se evalúa en cada llamada (PERFIL puede cambiar)


def _truncar(m, pe=None):
    """P1b [S3]: recorta cada ocurrencia que excede LEN. Devuelve (segmentos truncados, anotaciones)."""
    segs, notas = [], []
    for s in m.segs:
        nombre = s.split(m.f)[0]
        partes = s.split(m.f)
        for (sg, n), mx in _len(pe).items():
            if sg != nombre:
                continue
            i = n - 1 if sg == "MSH" else n
            if i < len(partes) and (sg != "MSH" or n > 2):
                reps = partes[i].split(m.r)
                nuevas = [r[:mx] for r in reps]
                if nuevas != reps:
                    notas.append("%s-%d: %r -> %r" % (sg, n, partes[i][:40], m.r.join(nuevas)[:40]))
                    partes[i] = m.r.join(nuevas)
        segs.append(m.f.join(partes))
    t = MR.Msg(segs, m.descodificados, m.marco, m.no_ascii)
    return t, notas


# ---------------------------------------------------------------------------- el procedimiento §3
def _codigo(v, tabla, tolerancias, donde):
    """Comparación de códigos ID/IS en mayúsculas [S4]; anota la tolerancia."""
    if v in tabla:
        return True
    if v.upper() in tabla:
        tolerancias.append("%s %r leído como %r [S4]" % (donde, v, v.upper()))
        return True
    return False


def _ts(v, c="^"):
    """[E2A §2.A.77, §2.A.22] DTM; la 2.ª componente (precisión) se ignora. Misma gramática que mapeador_oru._partes_dtm
    (A2 fracción solo con segundos, A3 zona representable en FHIR) y componente según MSH-2 (A4)."""
    return MO._partes_dtm(v.split(c)[0])[1] is None


LEYENDA_SEG = "? no reconocido, ! fuera de orden, + repetido; orden [E3 §3.3.1]: MSH EVN PID PV1"
LEYENDA_S45 = "~ opcional fuera de posición, ignorado [S45]"


def leyenda_seg(pe=None, nombre=None):
    """Leyenda de la línea SEGMENTOS: la literal de hoy para adt_a01; para los demás PE, la estructura de la 0354 y sus
    obligatorios efectivos."""
    pe = PE.resolver(pe)
    if pe["estructura_plana"] is not None:
        return LEYENDA_SEG
    g = EH.gramatica(nombre) if nombre else None
    if g is None:
        return "? no reconocido, ! fuera de orden, + repetido; estructura no resuelta por el punto %s (P2)" % pe["nombre"]
    return "? no reconocido, ! fuera de orden, + repetido; orden [0354 %s]: %s" % (nombre, " ".join(dict.fromkeys(EH.obligatorios_efectivos(g))))


def estructura(m, pe=None, nombre=None):
    """P3 [S2] [S14] [S45] -> {hallazgos, vistos [(nombre crudo, marca)], faltan, fuera_de_orden, repetidos,
    ignorados [(nombre, motivo)]}. Con el PE adt_a01, la estructura plana de hoy [E3 §3.3.1]; con los demás, el
    emparejador recursivo sobre la gramática de la 0354 que el PE asigna a MSH-9 (`nombre`, o se resuelve aquí)."""
    pe = PE.resolver(pe)
    if pe["estructura_plana"] is not None:
        return _estructura_plana(m)
    nombre = nombre or PE.estructura_de(m, pe)
    g = EH.gramatica(nombre) if nombre else None
    nombres = [s.split(m.f)[0] for s in m.segs]
    if g is None:                                                     # P2 rechaza el tipo/evento: P3 no se juzga (nada que marcar)
        return {"hallazgos": [], "vistos": [(n, "") for n in nombres], "faltan": [], "fuera_de_orden": None, "repetidos": [],
                "ignorados": [], "estructura": None}
    r = EH.emparejar(nombres, g, nombre)
    r["estructura"] = nombre
    return r


def _estructura_plana(m):
    """P3 [E3 §3.3.1] [S2] [S14] [S45] de hoy (adt_a01): -> {hallazgos, vistos [(nombre crudo, marca)], faltan, fuera_de_orden,
    repetidos, ignorados [(nombre, motivo)]}.
    Orden [S45]: el 100 por orden (P3.4) es solo para un obligatorio (MSH, EVN, PID, PV1) que llega detrás de otro
    obligatorio posterior en la estructura. Un opcional conocido que llega fuera de su posición (detrás de un segmento
    aceptado posterior, o delante de un obligatorio pendiente anterior a él) no era esperado ahí: el receptor lo ignora
    [E2 §2.6.2 a] y no avanza la posición; se anota y se marca ~. Tras el primer P3.4 no se juzga el resto (como antes)."""
    nombres = [s.split(m.f)[0] for s in m.segs]
    hall, faltan = [], []
    for req in OBLIGATORIOS:
        if req not in nombres:
            faltan.append(req)
            hall.append(("100", req, "consumido", "P3.3"))
    pendientes = [r for r in OBLIGATORIOS if r in nombres]               # obligatorios aún no vistos, en orden
    ult_ob, ult, ult_nmb = -1, -1, None                                   # último obligatorio aceptado; último aceptado
    vistos, fuera, repetidos, marcas, ignorados = set(), None, [], [], []
    for nmb in nombres:
        marca = ""
        if nmb not in POS:
            marca = "" if nmb == "ROL" else "?"                          # se ignora [E2 §2.6.2 a]; ROL exento
        elif fuera is None:
            p = POS[nmb]
            if nmb == "MSH" or nmb in OBLIGATORIOS:
                if p < ult_ob:                                            # [S2] obligatorio fuera de orden
                    marca, fuera = "!", nmb
                    hall.append(("100", nmb, "consumido", "P3.4"))
                else:
                    if nmb in vistos and nmb in OBLIGATORIOS:
                        marca = "+"
                        repetidos.append(nmb)
                        hall.append(("100", nmb, "consumido", "P3.5"))      # [S14] cardinalidad [1..1] [E3 §3.3.1]
                    vistos.add(nmb)
                    if nmb in pendientes:
                        pendientes.remove(nmb)
                    ult_ob = ult = p
                    ult_nmb = nmb
            else:                                                         # opcional conocido [S45]
                tope = POS[pendientes[0]] if pendientes else None
                if p < ult:
                    marca = "~"
                    ignorados.append((nmb, "tras %s" % ult_nmb))
                elif tope is not None and p > tope:
                    marca = "~"
                    ignorados.append((nmb, "antes de %s" % pendientes[0]))
                else:
                    ult, ult_nmb = p, nmb
        marcas.append((nmb, marca))
    return {"hallazgos": hall, "vistos": marcas, "faltan": faltan, "fuera_de_orden": fuera, "repetidos": repetidos,
            "ignorados": ignorados}


def notas_s45(est, estructura_nombre=None):
    """[S45] una nota por opcional ignorado; sin datos personales (solo nombres de segmento). Para adt_a01, el texto de
    hoy; para las demás estructuras, se nombra la estructura de la 0354 (y L-MT3/L-MT4 si el motivo los cita)."""
    if estructura_nombre is None:
        return ["[S45] %s %s: segmento opcional fuera de su posición en ADT_A01 [E3 §3.3.1]; el receptor lo ignora "
                "[E2 §2.6.2 a], no es AE 100 (nota, no cuenta)" % (n, motivo) for n, motivo in est["ignorados"]]
    return ["[S45] %s %s: segmento fuera de su posición en %s [E2 §2.13.1, tabla 0354]; el receptor lo ignora "
            "[E2 §2.6.2 a], no es AE 100 (nota, no cuenta)" % (n, motivo, estructura_nombre) for n, motivo in est["ignorados"]]


def _nombre_visible(nmb):
    """Nombre de segmento para la ficha, sin datos: canónico tal cual; si no, entre «» con los blancos como ·,
    tabulador y controles como \\xNN, recortado a 4 caracteres (+ …)."""
    if re.fullmatch(r"[A-Z][A-Z0-9]{2}", nmb):
        return nmb
    corto = nmb[:4]
    vis = "".join("·" if c == " " else ("\\x%02X" % ord(c) if (c == "\t" or MR.CONTROL.match(c)) else c) for c in corto)
    return "«%s%s»" % (vis, "…" if len(nmb) > 4 else "")


def resumen_segmentos(m, pe=None):
    """Línea SEGMENTOS de la ficha (sin el prefijo): determinista y sin datos personales."""
    pe = PE.resolver(pe)
    es = estructura(m, pe)
    items = [_nombre_visible(n) + mc for n, mc in es["vistos"]]
    s = " ".join(items)
    if es["faltan"]:
        s += " | faltan: " + " ".join(es["faltan"])
    oc = MR.segmentos_ocultos(m.segs, m.f)                                # [E2 §2.5.4]
    if oc:
        s += " | tras control no CR: " + " ".join(n for n, _ in oc)
    if any(mc for _, mc in es["vistos"]):
        s += "  (%s)" % (leyenda_seg(pe, es.get("estructura")) + ("; " + LEYENDA_S45 if es["ignorados"] else ""))   # [S45] solo si hay ~
    return s


UN_BYTE = ("ASCII", "8859/1", "8859/2", "8859/3", "8859/4", "8859/5", "8859/6", "8859/7", "8859/8", "8859/9", "ISO IR14")
UTF8 = ("UNICODE UTF-8", "UNICODE")


def clase_msh18(m):
    """[S9][S38][S39] -> (clase, valor): ascii (vacío o ASCII: ASCII por defecto [T0211]), utf-8, latin-1 (8859/1),
    otro (de la 0211) o fuera_de_tabla. Primera repetición, primer componente, en mayúsculas."""
    v = m.campo(m.segs[0], 18).split(m.r)[0].split(m.c)[0].upper()
    if v == "" and _p("msh18_por_omision") == "8859/1":                 # perfil: MSH-18 vacío = 8859/1 por omisión
        return "latin-1", v
    return ("ascii" if v in ("", "ASCII") else "utf-8" if v in UTF8 else "latin-1" if v == "8859/1" else
            "otro" if v in T0211 else "fuera_de_tabla"), v


def contradiccion_msh18(m):
    """[S39] ¿MSH-18 contradice los bytes del cable? -> dict {msh18, clase, motivo, donde, bytes, texto} o None.
    Bytes del cable según la evidencia: carácter > U+007F sin marcar = UTF-8 válido (m.no_ascii); <0xNN> con vía
    latin-1 = byte que no es UTF-8; vía utf-8 = UTF-8 válido marcado. Los juegos multibyte no Unicode y los valores
    fuera de la 0211 no se juzgan (L11)."""
    clase, v = clase_msh18(m)
    utf8 = ["%s-%s" % d for d in m.no_ascii] + ["%s-%s" % (r["seg"], r["n"]) for r in m.descodificados if r["via"] == "utf-8"]
    lat = [r for r in m.descodificados if r["via"] == "latin-1"]
    un_byte = clase == "latin-1" or (clase == "otro" and v in UN_BYTE)
    partes, donde, bs, motivo = [], [], [], None
    if clase == "ascii":
        if utf8:
            partes.append("caracteres fuera de 7-bit ASCII, UTF-8 válido")
            motivo = "utf8_multibyte"
        if lat:
            partes.append("bytes %s fuera de 7-bit ASCII, leídos como latin-1 [S9]" % " ".join(r["bytes"] for r in lat))
            motivo = motivo or "bytes_no_ascii"
        donde = utf8 + ["%s-%s" % (r["seg"], r["n"]) for r in lat]
    elif clase == "utf-8" and lat:
        partes.append("bytes %s que no son UTF-8, leídos como latin-1 [S9]" % " ".join(r["bytes"] for r in lat))
        motivo, donde = "bytes_no_utf8", ["%s-%s" % (r["seg"], r["n"]) for r in lat]
    elif un_byte and utf8:
        partes.append("UTF-8 multibyte válido en un juego de un byte")
        motivo, donde = "utf8_multibyte", utf8
    if not motivo:
        return None
    donde = list(dict.fromkeys(donde))
    bs = [r["bytes"] for r in lat]
    sujeto = ("MSH-18 ausente (%s por omisión del perfil [%s])" % (_p("msh18_por_omision"), _p("regla_msh18"))
              if v == "" and _p("msh18_por_omision") else "MSH-18 ausente (ASCII por defecto)" if v == "" else "MSH-18 = %s" % v)
    return {"msh18": v, "clase": clase, "motivo": motivo, "donde": donde, "bytes": bs,
            "texto": "[S39] %s contradice los bytes del cable: %s, en %s (nota menor, no cuenta)" % (sujeto, " y ".join(partes), ", ".join(donde))}


def esperado(m, ctx):
    """Acuse esperado para un mensaje (P1-P9). ctx: {destino, marco, ocultos, pe}; pe = punto de entrada (§1.3)."""
    _vacio = lambda x, _s=_seps(m): _vacio_en(x, _s)                 # noqa: E731 - B3: «vacío» con los delimitadores del mensaje
    pe = PE.resolver(ctx.get("pe"))
    plana = pe["estructura_plana"] is not None                            # adt_a01: las ramas literales de hoy
    x = {"err": [], "truncados": [], "tolerancias": [], "ambiguedades": [], "notas": [], "version_msh12": None,
         "alternativas_aceptadas": [], "marco": ctx.get("marco"), "punto_entrada": pe["nombre"], "estructura": None}
    if PERFIL != "lab":
        x["perfil"], x["perfil_reglas"] = PERFIL, []
    msh0 = m.segs[0]
    x["msa2"] = m.campo(msh0, 10)
    m, x["truncados"] = _truncar(m, pe)                                   # P1b [S3]
    msh = m.segs[0]
    tol = x["tolerancias"]
    # [S9] bytes no decodificables <0xNN>: se leen como latin-1; MSH-18 decide la certeza
    clase18, v18c = clase_msh18(m)
    regs = [r for r in m.descodificados if r["via"] in ("utf-8", "latin-1")]
    x["descodificacion"] = {"clase_msh18": clase18, "entradas": list(m.descodificados),
                            "certeza": "ambiguedad AMB-10" if (clase18 == "otro" and regs) else "literal",
                            "contradiccion": contradiccion_msh18(m)}                                  # [S39]
    for r in regs:
        donde = "%s-%s" % (r["seg"], r["n"])
        if clase18 == "latin-1" and v18c == "" and _p("msh18_por_omision"):
            x["notas"].append("%s: bytes %s leídos como 8859/1: MSH-18 vacío = 8859/1 por omisión del perfil [%s]"
                              % (donde, r["bytes"], _p("regla_msh18")))
        elif clase18 == "latin-1":
            x["notas"].append("%s: bytes %s leídos como 8859/1 declarado en MSH-18 [E2 §2.15.9.18]" % (donde, r["bytes"]))
        else:
            tol.append("[S9] %s: bytes %s decodificados como %s (MSH-18 %s)" % (
                donde, r["bytes"], r["via"], "ausente: ASCII por defecto" if clase18 == "ascii" else "= " + (v18c or "?")))
    for r in m.descodificados:
        donde = "%s-%s" % (r["seg"], r["n"])
        if r["via"] == "literal":
            x["notas"].append("%s: marcador <0x%s> con byte ASCII imprimible: se deja literal (fuera de S9 y S10)" % (donde, r["bytes"]))
        elif r["via"] == "control":
            x["notas"].append("[S10] %s: byte %s del cable es el carácter de control U+%04X" % (donde, r["bytes"], ord(r["texto"])))
        elif r["via"] == "lf":
            x["notas"].append("[S10] %s: byte 0A del cable (LF) dentro del campo es un carácter de control; no termina segmento "
                              "[E2 §2.5.4] (L1)" % donde)
    c39 = x["descodificacion"]["contradiccion"]                          # [S39] callada si S9 ya lo dice (Víctor, 30-sep)
    if c39 and c39["motivo"] != "utf8_multibyte" and any(t.startswith("[S9]") for t in tol):
        x["descodificacion"]["contradiccion"] = None
        x["descodificacion"]["contradiccion_callada"] = "S9"
    # P1 modo
    m15, m16 = m.campo(msh, 15).split(m.c)[0], m.campo(msh, 16).split(m.c)[0]
    x["modo"] = "original" if _vacio(m15) and _vacio(m16) else "mejorado"
    def cond(v):
        if _vacio(v):
            return None
        if v.upper() not in T0155:
            x["ambiguedades"].append("MSH-15/16 %r fuera de 0155: tratado como AL [A-5]" % v)
            return "AL"
        return v.upper()
    c15, c16 = cond(m15), cond(m16)
    if x["modo"] == "mejorado":
        c15 = c15 or "NE"
        c16 = c16 or "NE"
    # P2 comprobaciones del respondedor [E2 §2.9.2.1], generalizado por PE con la tabla 0354 (§2): 200 tipo, 201 evento,
    # 200 estructura declarada distinta de la que la 0354 asigna al evento [A-6], AMB-6 si MSH-9.3 vacío
    p2 = []
    t9 = m.campo(msh, 9)
    comp9 = t9.split(m.c)
    tipos = pe["tipos"]
    if _vacio(t9):
        p2.append(("101", "MSH-9", "consumido", "P2a")); x["ambiguedades"].append("AMB-2: MSH-9 vacío -> 101")
    elif comp9[0].upper() not in tipos:
        p2.append(("200", "MSH-9", "consumido", "P2a"))
    elif len(comp9) < 2 or comp9[1].upper() not in tipos[comp9[0].upper()]:
        p2.append(("201", "MSH-9", "consumido", "P2a"))
    else:
        x["estructura"] = tipos[comp9[0].upper()][comp9[1].upper()]
        if len(comp9) < 3 or _vacio(comp9[2]):
            if NIVEL == "estricto":
                p2.append(("101", "MSH-9.3", "estricto", "P2a"))
            x["notas"].append("AMB-6: MSH-9.3 vacío")
        elif comp9[2].upper() != x["estructura"]:
            p2.append(("200", "MSH-9.3", "consumido", "P2a"))
    if not p2:
        v12 = m.campo(msh, 12)
        if _vacio(v12) and _p("msh12_por_omision"):                    # perfil: MSH-12 vacío = versión por omisión
            vo = _p("msh12_por_omision")
            x["version_msh12"] = {"texto": vo, "leida": list(MR.version_id(vo)), "aceptada": True, "por_omision": True}
            x["notas"].append("MSH-12 vacío: %s por omisión del perfil [%s]" % (vo, _p("regla_msh12")))
        elif _vacio(v12):
            p2.append(("101", "MSH-12", "consumido", "P2b"))
        else:                                                         # [S19] 2.x desde 2.4 [E2 §2.9.2.1 b] [E2 §2.8]
            v = v12.split(m.c)[0]
            vi = MR.version_id(v)
            x["version_msh12"] = {"texto": v, "leida": list(vi) if vi else None, "aceptada": MR.version_aceptada(v)}
            if vi is None:
                p2.append(("203", "MSH-12", "consumido", "P2b"))
                x["notas"].append("MSH-12 %r no tiene la forma N.N[.N] de la tabla 0104 -> 203 [S19]" % v)
            elif not x["version_msh12"]["aceptada"] and _p("version_cualquier_2x") and vi[0] == 2:
                x["version_msh12"]["aceptada"] = True
                x["notas"].append("MSH-12 %s aceptada por el perfil (cualquier 2.x) [%s]; se aplican reglas, tablas y "
                                  "longitudes de v2.5 (límite L17)" % (v, _p("regla_msh12")))
            elif not x["version_msh12"]["aceptada"]:
                p2.append(("203", "MSH-12", "consumido", "P2b"))
                x["notas"].append("MSH-12 %s anterior a 2.4 o no es 2.x -> 203 [S19]" % v)
            elif vi != (2, 5, None):
                x["notas"].append("MSH-12 %s aceptada [S19]: fuera de la tabla 0104 de v2.5 o distinta de la de referencia; "
                                  "se aplican reglas, tablas y longitudes de v2.5 (límite L17)" % v)
    if not p2:
        v11 = m.campo(msh, 11)
        if _vacio(v11) and _p("msh11_por_omision"):
            x["notas"].append("MSH-11 vacío: %s por omisión del perfil [%s]" % (_p("msh11_por_omision"), _p("regla_msh12")))
        elif _vacio(v11):
            p2.append(("101", "MSH-11", "consumido", "P2c"))
        elif not _codigo(v11.split(m.c)[0], set(_p("msh11_validos") or T0103), tol, "MSH-11"):
            p2.append(("202", "MSH-11", "consumido", "P2c"))
    x["msa1_commit"] = None
    if p2:
        x["msa1_aplicacion"] = "AR"
        x["err"] = [{"err3": c, "err4": "E", "donde": d, "nivel": nv, "regla": r} for c, d, nv, r in p2]
        commit = "CR"
        if _p("no_soportado_ae"):                                    # perfil: AE «mensaje invalidado»; AR tolerado
            x["msa1_aplicacion"] = "AE"
            x["alternativas_aceptadas"] += [{"msa1": "AR", "err3": c, "donde": d, "por": _p("regla_no_soportado")}
                                            for c, d, _, _ in p2]
            x["perfil_reglas"].append(_p("regla_no_soportado"))
    else:
        commit = "CA"
        est = estructura(m, pe, x["estructura"])
        hall = list(est["hallazgos"])                                    # P3 estructura
        x["notas"] += notas_s45(est, None if plana else x["estructura"])  # [S45] opcionales fuera de posición, ignorados
        mc = x.get("marco") or {}
        if mc.get("solo_msh"):                                           # [S31][S35] el marco trae solo el MSH
            x["alternativas_aceptadas"] += [{"msa1": "AR", "err3": "101", "donde": "trama", "por": "S31"},
                                            {"msa1": "AE", "err3": "101", "donde": "trama", "por": "S35"},
                                            {"msa1": "AR", "err3": "100", "donde": "trama", "por": "S35"}]
            x["notas"].append("[S31][S35] el marco %d trae solo el MSH: se juzga lo que llegó; esperado AE 100 (EVN, PID y PV1 "
                              "ausentes); AE 101, AR 100 y AR 101 aceptados" % mc["n"])
        oc = ctx.get("ocultos") or []                                    # [E2 §2.5.4] segmentos tras un control que no es CR
        falt = [s for s in est["faltan"] if s not in [n for n, _ in oc]]
        if not mc.get("solo_msh") and falt and mc.get("trama_partida"):  # [S36] otra partición: lo que el marco no trae
            x["alternativas_aceptadas"] += [{"msa1": "AR", "err3": "101", "donde": "trama", "por": "S36"},
                                            {"msa1": "AE", "err3": "101", "donde": "trama", "por": "S36"},
                                            {"msa1": "AR", "err3": "100", "donde": "trama", "por": "S36"}]
            x["notas"].append("[S36] el marco %d no trae %s: se juzga lo que llegó; esperado AE 100; AE/AR 100/101 aceptados"
                              % (mc["n"], ", ".join(falt)))
            x["faltan_particion"] = falt
        if oc:
            x["notas"].append("[E2 §2.5.4] el marco %s trae %s tras %s en vez del terminador CR: el receptor no los reconoce como "
                              "segmentos (ausentes, [E2 §2.6.2 b]); el marco no trae solo el MSH: S31/S35 no aplican (L1)"
                              % (mc.get("n"), " ".join(n for n, _ in oc), "/".join(sorted({c for _, c in oc}))))
        # P4 obligatorios vacíos: la lista p4 del PE, en su orden (adt_a01: MSH-10, PID-3, PID-5, MSH-7, EVN-2, PV1-2, como hoy).
        # Un segmento ausente no se juzga; con los PE nuevos tampoco uno que la estructura resuelta no conoce [E2 §2.6.2 a].
        def primero(nmb):
            s = [z for z in m.segs if z.split(m.f)[0] == nmb]
            return s[0] if s else None
        conocidos = None if plana else set(EH.segmentos(EH.gramatica(x["estructura"]) or []))
        todas = pe.get("todas_las_ocurrencias") or set()                  # DV-ORU-1 (solo oru_fhir): cada OBR y cada OBX

        def ocurrencias(nmb):
            """[(segmento, etiqueta del segmento)]: la primera ocurrencia (como hoy, DV-MT5) o, en los segmentos que el PE
            declara en todas_las_ocurrencias, todas con su índice si hay más de una («OBX(3)»)."""
            if nmb == "MSH":
                return [(msh, "MSH")]
            segs = [z for z in m.segs if z.split(m.f)[0] == nmb]
            if nmb in todas and nmb in ("OBX", "OBR") and pe.get("mapeador") == "oru":
                # DV-ORU-1 acotada (O4 ronda 2, B24): solo los OBX que el contrato consume, los del grupo OBSERVATION
                # según mapeador_oru.agrupar; los de SPM (L-ORU-5), los anteriores al primer OBR (S45) y los de otro
                # PATIENT_RESULT (AMB-ORU-5) no se juzgan campo a campo (S6/S17: se anotan). Etiqueta por posición global.
                # A5: igual con los OBR, que solo cuentan los del primer PATIENT_RESULT (AMB-ORU-5: el acuse no cambia)
                inf_ = MO.agrupar(m)["informes"]
                quedan = collections.Counter(o for inf in inf_ for o in inf["obx"]) if nmb == "OBX" else \
                    collections.Counter(inf["obr"] for inf in inf_)
                elegidos = []
                for i, z in enumerate(segs):
                    if quedan[z] > 0:
                        quedan[z] -= 1
                        elegidos.append((i, z))
                if len(segs) > 1:
                    return [(z, "%s(%d)" % (nmb, i + 1)) for i, z in elegidos]
                return [(z, nmb) for i, z in elegidos]
            if nmb in todas and len(segs) > 1:
                return [(s, "%s(%d)" % (nmb, i + 1)) for i, s in enumerate(segs)]
            return [(segs[0], nmb)] if segs else []

        def juzgable(nmb):
            return nmb == "MSH" or (primero(nmb) is not None and (conocidos is None or nmb in conocidos))
        for sg, n, nv in pe["p4"]:
            if not juzgable(sg):
                continue
            for seg, etq in ocurrencias(sg):
                if isinstance(n, tuple):                                      # «al menos uno» (SCH-1 o SCH-2, AMB-MT-5)
                    if all(_vacio(m.campo(seg, k)) for k in n):
                        hall.append(("101", "%s-%d" % (etq, n[0]), nv, "P4"))
                        x["ambiguedades"].append("AMB-MT-5: %s vacíos (ambos C): 101 sobre %s-%d" % (
                            " y ".join("%s-%d" % (sg, k) for k in n), sg, n[0]))
                    continue
                v = m.campo(seg, n)
                if (sg, n) == ("PID", 3):                                     # regla propia de PID-3 [A-9]: todas las repeticiones
                    if v.strip() != '""' and all(_vacio(r.split(m.c)[0]) for r in v.split(m.r)):
                        hall.append(("101", "PID-3", nv, "P4"))
                    elif v.strip() == '""':
                        x["notas"].append("PID-3 = \"\" (nulo explícito) cuenta como presente [A-9]")
                elif _vacio(v) and (sg, n) == ("PV1", 2) and pe["nombre"] == "adt_fhir" and _p("pv1_2_vacio"):
                    tol.append("[S95] PV1-2 vacío: el perfil del sitio lo tolera (class nulo declarado) [%s]" % _p("pv1_2_vacio"))
                    x["perfil_reglas"].append(_p("pv1_2_vacio"))
                elif _vacio(v):
                    hall.append(("101", "%s-%d" % (etq, n), nv, "P4"))
        # P5 tipo de dato y valor de tabla, por posición en el mensaje y número de campo: la lista p5 del PE, en su orden
        p5 = []
        def ts(seg, n, nv, etiqueta):
            v = m.campo(seg, n)
            if not _vacio(v) and not _ts(v, m.c):
                p5.append(("102", etiqueta, nv, "P5"))
        def nm(seg, n, nv, etiqueta):
            v = m.campo(seg, n)
            if not _vacio(v) and MO.valor_valido("NM", v, m.c) is False:     # B4: la regla NM única (AMB-ORU-3)
                p5.append(("102", etiqueta, nv, "P5"))

        def valor_por_tipo(seg, n, nv, etiqueta):
            """DV-ORU-2 (solo oru_fhir): OBX-5 según OBX-2 (NM ampliado AMB-ORU-3, SN, TS/DT/TM; el resto no se juzga), cada
            repetición; resuelve L-MT7 para este PE."""
            v = m.campo(seg, n)
            if _vacio(v):
                return
            tipo = m.campo(seg, 2).split(m.c)[0].upper()                   # [S4]
            if any(MO.valor_valido(tipo, rep, m.c) is False for rep in v.split(m.r)):
                p5.append(("102", etiqueta, nv, "P5"))
        vm = x.get("version_msh12") or {}
        ver = "" if vm.get("por_omision") else (vm.get("texto") or "")     # [S-VE-2] S22 sigue a la versión ESCRITA (S103): la asumida
        posterior = MR.posterior_a_25(ver)                             # [S22] [S27]    solo decide la aceptación; MSH-12 vacío = v2.5

        def s22(v, etiqueta):
            """[S22] fuera de la tabla de v2.5 en un mensaje posterior a 2.5: tolerancia, no 103; AE 103 aceptable [S26]."""
            tol.append("[S22] %s %r no está en la %s de v2.5; mensaje %s: puede ser legal en su versión (no verificado, L18)"
                       % (etiqueta, v, TABLA_DE[_etq_base(etiqueta)], ver))
            x["alternativas_aceptadas"].append({"msa1": "AE", "err3": "103", "donde": etiqueta, "por": "S26"})

        def tab(seg, n, tabla, nv, etiqueta):
            v = m.campo(seg, n).split(m.c)[0]
            if not _vacio(v) and not _codigo(v, tabla, tol, etiqueta):
                if posterior:
                    s22(v, etiqueta)
                else:
                    p5.append(("103", etiqueta, nv, "P5"))

        def msh18(nv):
            v18 = m.campo(msh, 18)
            if not _vacio(v18) and v18.split(m.r)[0] not in T0211 and v18.split(m.r)[0].upper() not in T0211:
                if posterior:
                    s22(v18.split(m.r)[0], "MSH-18")
                else:
                    p5.append(("103", "MSH-18", nv, "P5"))

        def p5f(pid, nv):
            """[S18] fecha de nacimiento posterior a MSH-7: rechazarla es lo correcto; sin MSH-7 válido no se contrasta (L16)."""
            v7 = m.campo(pid, 7).split(m.c)[0]
            m7 = m.campo(msh, 7).split(m.c)[0]
            if v7 and _ts(v7, m.c):
                if m7 and _ts(m7, m.c):                           # N2b: MSH-7 se valida entero (con zona)
                    if MR.posterior_a(v7, m7):                    # N2/N8: precisión común, con la hora si la hay
                        p5.append(("102", "PID-7", nv, "P5f"))
                else:
                    x["notas"].append("PID-7 no contrastable: MSH-7 ausente o inválido (límite L16)")
        for sg, n, juicio, nv in pe["p5"]:
            if not juzgable(sg):
                continue
            for seg, etq in ocurrencias(sg):
                etiqueta = "%s-%d" % (etq, n)
                if (sg, n) == ("MSH", 18):
                    msh18(nv)
                elif juicio == "ts":
                    ts(seg, n, nv, etiqueta)
                    if (sg, n) == ("PID", 7):
                        p5f(seg, nv)
                elif juicio == "nm":
                    nm(seg, n, nv, etiqueta)
                elif juicio == "valor_por_tipo":                              # DV-ORU-2
                    valor_por_tipo(seg, n, nv, etiqueta)
                else:
                    tab(seg, n, _tabla_pe(juicio), nv, etiqueta)
        if not plana and juzgable("EVN"):                                 # L-MT9: EVN-1 ≠ MSH-9.2 es redundancia, no error [E2 §2.9.1]
            v1 = m.campo(primero("EVN"), 1).split(m.c)[0]
            if not _vacio(v1) and v1.upper() != (comp9[1].upper() if len(comp9) > 1 else ""):
                x["notas"].append("[L-MT9] EVN-1 %r distinto de MSH-9.2 %r: campo redundante, retenido por compatibilidad "
                                  "[E2 §2.9.1]; se anota, no es error" % (v1, comp9[1] if len(comp9) > 1 else ""))
        # [S10] carácter de control C0, DEL o C1, en crudo, por \Xhh\ o por <0xNN> decodificado [S9] -> 102 (E2A §2.A.74);
        # en un campo no consumido solo se anota [S17]/[S6]. Segmentos: los que el PE nombra (primera ocurrencia de cada uno)
        consumidos = pe["consumidos"]
        if pe["orden_seg"] is not None:
            orden_seg = pe["orden_seg"]
        else:
            orden_seg = EH.orden_segmentos(EH.gramatica(x["estructura"]) or [])
        nombres_s10 = {s for s, _, _ in pe["p4"]} | {s for s, _, _, _ in pe["p5"]} | {s for s, _ in consumidos}
        segs_s10 = [oc for s in sorted(nombres_s10, key=lambda s: (orden_seg.get(s, 9), s)) if juzgable(s) for oc in ocurrencias(s)]
        for seg, etq in [z for z in segs_s10 if z[0] is not None]:
            nombre = seg.split(m.f)[0]
            ncampos = len(seg.split(m.f)) - (0 if nombre == "MSH" else 1)       # DV-C0-4
            for n in range(3 if nombre == "MSH" else 1, ncampos + 1):
                v = m.campo(seg, n)
                if MR.control_en(v if _p("escape_control_legal") else m.desescapa(v)) is not None:
                    p5.append(("102", "%s-%d" % (etq, n), "consumido" if (nombre, n) in consumidos else "estricto", "P5'"))
        vistos5, p5o = set(), []
        for h in sorted(p5, key=lambda h: (orden_seg.get(_etq_partes(h[1])[0], 9), _etq_partes(h[1])[1], int(h[1].split("-")[1].split(".")[0]), h[0])):
            if (h[0], h[1]) not in vistos5:
                vistos5.add((h[0], h[1]))
                p5o.append(h)
        hall += p5o
        activos = [h for h in hall if h[2] == "consumido" or (NIVEL == "estricto" and h[2] == "estricto")]
        for h in hall:
            if h not in activos:
                if h[2] == "nota":                                         # L-MT6: campo condicional (C), la condición es prosa
                    x["notas"].append("hallazgo condicional (C) no juzgado [L-MT6]: %s %s" % (h[0], h[1]))
                else:
                    x["notas"].append("hallazgo estricto no activo [S6]: %s %s" % (h[0], h[1]))
        dst = ctx.get("destino") or {"destino": "sin_evidencia", "ambigua": [], "notas": []}
        hd = dst.get("http") or 0
        sistema_s25 = dst.get("destino") == "sistema" or (dst.get("destino") == "http" and not 200 <= hd < 300
                                                              and hd not in (400, 422))          # [S25] [S29]
        if activos and not sistema_s25:                               # P6 [E2 §2.9.2.2 b]
            x["msa1_aplicacion"] = "AE"
            x["err"] = [{"err3": c, "err4": "E", "donde": d, "nivel": nv, "regla": r} for c, d, nv, r in activos]
            if dst.get("destino") == "http" and hd in (400, 422):
                x["notas"].append("[S21] error de contenido y HTTP %d del destino: se espera AE %s; AR %s se tolera"
                                  % (hd, activos[0][0], activos[0][0]))
        else:                                                         # P7 (tabla 1.3b)
            x["ambiguedades"] += dst.get("ambigua", [])
            x["notas"] += dst.get("notas", [])
            d0 = dst["destino"]
            if d0 == "exito":
                clase = ("AA", None)
            elif d0 == "no_intentado":
                clase = ("AA", None)
                x["notas"].append("el circuito no llamó al destino (su opinión: %s); el estándar no halla nada" %
                                  (dst["opinion"]["datos"].get("hecho") or dst["opinion"]["datos"].get("tipo")))
            elif d0 == "sistema":
                clase = ("AR", "207")
            elif d0 == "http":
                h, code = dst["http"], dst.get("code")
                if 200 <= h < 300:
                    clase = ("AA", None)
                    if h not in (200, 201):
                        x["ambiguedades"].append("DV1: HTTP %d tratado como éxito" % h)
                elif h in (400, 422):
                    clase = ("AR", "207"); x["notas"].append("HTTP %d: AR 207 por decisión del sitio [S16]" % h)
                elif h == 409:
                    clase = ("AR", "206")
                elif h == 412:
                    clase = ("AR", "205")
                elif h in (401, 403, 404, 405, 406, 415) or 300 <= h < 400 or h == 429 or h >= 500:
                    clase = ("AR", "207")
                else:
                    clase = ("AR", "207"); x["ambiguedades"].append("DV1: HTTP %d fuera de la tabla 1.3b" % h)
            else:
                clase = ("AA", None)
            x["msa1_aplicacion"] = clase[0]
            if clase[1]:
                x["err"] = [{"err3": clase[1], "err4": "E", "donde": "destino", "nivel": "consumido", "regla": "P7"}]
            if activos:                                               # [S25] el fallo del sistema prevalece; AE <código> [S28]
                x["contenido_no_acusado"] = [{"err3": c, "donde": d, "nivel": nv, "regla": r} for c, d, nv, r in activos]
                x["notas"].append("[S25] hallazgos de contenido no acusados por fallo del sistema en el destino: " +
                                  ", ".join("%s %s" % (c, d) for c, d, _, _ in activos))
                x["alternativas_aceptadas"] += [{"msa1": "AE", "err3": c, "donde": d, "por": "S28"} for c, d, _, _ in activos]
    if _p("reenvio_nota") and "entorno:tiempo" in ((ctx.get("destino") or {}).get("causas_d0") or []):
        x["notas"].append("sin ACK en el plazo, el perfil prescribe reenviar el original; el reenvío y su duplicado no "
                          "están en la evidencia (L15) [%s]" % _p("reenvio_nota"))
    # P8 existencia y clase
    x["aplicacion_requerida"] = True
    if _p("ack_siempre"):                                            # perfil: un ACK siempre, de aplicación, síncrono
        x.update(debe_haber_ack="si", clase_ack="aplicacion", msa1=x["msa1_aplicacion"])
        if c15 != "AL":
            x["notas"].append("MSH-15 %s: el perfil espera AL; el receptor acusa igual [%s]" % (m15 or "vacío", _p("ack_siempre")))
    elif x["modo"] == "original":
        x.update(debe_haber_ack="si", clase_ack="aplicacion", msa1=x["msa1_aplicacion"])
    else:
        x["msa1_commit"] = commit
        pide_c = c15 == "AL" or (c15 == "ER" and commit == "CR") or (c15 == "SU" and commit == "CA")
        pide_a = c16 == "AL" or (c16 == "ER" and x["msa1_aplicacion"] in ("AE", "AR")) or \
            (c16 == "SU" and x["msa1_aplicacion"] == "AA")
        x["aplicacion_requerida"] = pide_a
        if pide_a:                                    # [S13] acuse de aplicación síncrono: perfil del sitio (AckMode App)
            x.update(debe_haber_ack="si", clase_ack="aplicacion", msa1=x["msa1_aplicacion"])
            if pide_c:
                x["notas"].append("modo mejorado (MSH-15/16 = %s/%s): acuse de aplicación síncrono, perfil del sitio [S13]; "
                                  "por el estándar la respuesta síncrona sería %s" % (c15, c16, commit))
        elif pide_c:
            x.update(debe_haber_ack="si", clase_ack="commit", msa1=commit)
        else:
            x.update(debe_haber_ack="no", clase_ack="ninguno", msa1=None)
    # P9 cabecera
    x["cabecera_ack"] = {"msh9": "ACK^%s^ACK" % (comp9[1] if len(comp9) > 1 else ""), "msh5": m.campo(msh0, 3),
                         "msh6": m.campo(msh0, 4), "msh11": m.campo(msh0, 11)}
    return x


def calcular(e, lectura=None, pe=None):
    """-> lista de acuses esperados (uno por mensaje), o [{'debe_haber_ack': ...}] en P0. Lleva la lectura.
    pe: punto de entrada (nombre o PE); precedencia §1.3: parámetro > e["punto_entrada"] > adt_a01."""
    pe = PE.resolver(pe, e)
    ms = MR.mensajes(e.get("mensaje"))
    m10 = [m.campo(m.segs[0], 10) for m in ms]
    lec = lectura or LE.leer(e, m10, pe["nombre"])
    tr = MR.trama(e.get("mensaje"))                                                   # [S31]
    resumen_tr = {"marcos": len(tr["marcos"]), "sin_msh": tr["sin_msh"], "anomalias": tr["anomalias"]}
    nota_a2 = ["[A-2] trama: " + "; ".join(tr["anomalias"])] if tr["anomalias"] else []
    if lec["p0"]:                                                                      # P0.a
        return [{"debe_haber_ack": "no", "clase_ack": "ninguno", "msa1": None, "err": [], "notas": ["P0.a"],
                 "sin_intercambio": True, "lectura": lec, "destino": None, "trama": resumen_tr}]
    if not ms:                                                                         # P0.b
        return [{"debe_haber_ack": "indeterminado", "clase_ack": "ninguno", "msa1": None, "err": [], "notas": ["P0.b"] + nota_a2,
                 "lectura": lec, "destino": None, "trama": resumen_tr}]
    out = []
    for k, m in enumerate(ms):
        oc = MR.segmentos_ocultos(m.segs, m.f)                           # [E2 §2.5.4] lo que el marco arrastra tras LF
        marco = {"n": m.marco, "solo_msh": len(m.segs) == 1 and not oc, "trama_partida": bool(tr["sin_msh"])}
        x = esperado(m, {"destino": lec["por_mensaje"][k], "marco": marco, "ocultos": oc, "pe": pe})
        x["lectura"], x["destino"], x["trama"] = lec, lec["por_mensaje"][k], resumen_tr
        out.append(x)
    for mc in tr["marcos"]:                                                            # [S31] marcos sin MSH, anotados
        if mc["msh"]:
            continue
        previos = [x for x, m in zip(out, ms) if m.marco < mc["n"]]
        dest = previos[-1] if previos else out[0]
        dest["notas"].append("[S31] marco %d sin MSH (%s): no es un mensaje; sin acuse esperado (L9)"
                             % (mc["n"], " ".join(_nombre_visible(s) for s in mc["segmentos"])))
    if nota_a2:
        out[0]["notas"] += nota_a2
    return out


# ---------------------------------------------------------------------------- comparación §4
def _acks(ack):
    return MR.mensajes(ack) if ack else []


def comparar(e, esperados=None, pe=None):
    """-> lista de discrepancias [{'id': 'D1', 'que': ..., 'cuenta': bool, 'ambigua': bool}]. pe como en calcular()."""
    pe = PE.resolver(pe, e)
    esp = esperados or calcular(e, pe=pe)
    obs = _acks(e.get("ack"))
    out = []
    kk = [None]
    def d(i, que, cuenta=True, amb=False, causa=None, k=None):
        out.append({"id": i, "que": que, "cuenta": cuenta, "ambigua": amb, "causa": causa, "k": kk[0] if k is None else k})
    if esp[0]["debe_haber_ack"] == "indeterminado":
        return [{"id": "nota", "que": "indeterminado (P0.b)", "cuenta": False, "ambigua": False}]
    ms = MR.mensajes(e.get("mensaje"))
    msh10 = [m.campo(m.segs[0], 10) for m in ms] or [None]
    pares, libres = [], list(obs)
    for k, x in enumerate(esp):
        a = next((o for o in libres if o.segmentos("MSA") and o.campo(o.segmentos("MSA")[0], 2) == msh10[k]), None)
        if a is None and libres:
            a = libres[0]
        if a is not None:
            libres.remove(a)
        pares.append((x, a, msh10[k] if k < len(msh10) else None))
    if len(ms) > len(obs) and obs:
        cs = [c for x in esp for c in (x.get("destino") or {}).get("causas_d0", []) if c == "trama"]
        d("D0", "recuento: %d mensajes y %d ACK" % (len(ms), len(obs)), causa=cs[0] if cs else None)
    for k, (x, a, m10) in enumerate(pares):
        kk[0] = k
        amb = bool(x.get("ambiguedades"))
        dst = x.get("destino") or {}
        if x["debe_haber_ack"] == "si" and a is None:
            if not (len(ms) > len(obs) and obs):
                cs = dst.get("causas_d0") or []
                d("D0", "ACK ausente", amb=amb, causa=cs[0] if cs else None, k=k)
            continue
        if x["debe_haber_ack"] == "no":
            if a is not None:
                d("D0", "ACK no solicitado")
            continue
        msa = a.segmentos("MSA")
        m1 = a.campo(msa[0], 1) if msa else ""
        if m1.upper() not in T0008:
            d("D1", "MSA-1 inválido: %r" % m1)
            continue
        m1 = equiv_msa1(m1.upper())
        if m1 in ("AA", "AE", "AR"):
            exp1 = x.get("msa1_aplicacion")
        else:
            exp1 = x.get("msa1_commit")
        errs = a.segmentos("ERR")
        codigos = [(a.campo(s, 3).split(a.c)[0], a.campo(s, 4).split(a.c)[0]) for s in errs]
        obs3 = [c for c, _ in codigos]
        alts = [z for z in x.get("alternativas_aceptadas") or [] if z["msa1"] == m1] if m1 != exp1 else []
        alt = next((z for z in alts if z["err3"] in obs3), None)
        term = (dst.get("terminal") or {}).get("id")
        cod_esp = [z["err3"] for z in x.get("err") or []]

        def motivo(z):
            if z["por"] == "S26":
                return " fuera de la %s de v2.5 en un mensaje %s" % (TABLA_DE.get(_etq_base(z["donde"]), "tabla"),
                                                                    (x.get("version_msh12") or {}).get("texto"))
            if z["por"] in ("S31", "S35"):
                return " del marco %s, que trae solo el MSH (esperado AE 100: EVN, PID y PV1 ausentes)" % (x.get("marco") or {}).get("n")
            if z["por"] == "S36":
                falt = x.get("faltan_particion") or (estructura(ms[k], pe, x.get("estructura"))["faltan"] if k < len(ms) else [])
                return " del marco %s, que no trae %s (esperado AE 100)" % ((x.get("marco") or {}).get("n"), ", ".join(falt))
            if z["por"] == _p("regla_no_soportado"):
                return ": el perfil espera AE para lo no soportado y tolera AR"
            return " con el destino caído (AR %s esperado por S25)" % (cod_esp[0] if cod_esp else "207")
        if alt is not None:                                           # R-alt [S26] [S28] [S31] [S35] [S36]
            d("D1", "MSA-1 %s, esperado %s: aceptado [%s] (%s %s sobre %s%s)" % (m1, exp1, alt["por"], m1, alt["err3"],
              alt["donde"], motivo(alt)), cuenta=False, causa="alternativa_" + alt["por"], k=k)
        elif (m1 == "AR" and exp1 == "AE" and dst.get("destino") == "http" and dst.get("http") in (400, 422) and term == "L05"
              and cod_esp and all(c in ("100", "101", "102", "103") for c in cod_esp) and any(c in cod_esp for c in obs3)):
            d("D1", "MSA-1 AR, esperado AE: tolerado [S21] (el destino devolvió HTTP %d y ERR-3 %s es un código de contenido "
              "esperado)" % (dst["http"], next(c for c in obs3 if c in cod_esp)), cuenta=False, causa="rechazo_del_destino", k=k)
        elif m1 != exp1:
            causa = None
            if dst.get("fabricado") and m1 in ("CA", "CE", "CR"):
                causa = "acuse_fabricado_por_servicio"
            elif exp1 == "AA" and m1 in ("AE", "AR") and dst.get("opinion"):
                causa = "opinion_del_circuito(%s)" % (dst["opinion"]["datos"].get("hecho") or dst["opinion"]["datos"].get("tipo"))
            elif m1 == "AA" and exp1 == "AR" and x.get("err") and x["err"][0]["donde"] == "destino":
                causa = "aceptacion_falsa"
            d("D1", "MSA-1 %s, esperado %s" % (m1, exp1), amb=amb, causa=causa, k=k)
        # [S13] D5 no existe: el acuse de aplicación síncrono es el perfil del sitio
        esp_err = x["err"] if (m1 in ("AA", "AE", "AR") and exp1 in ("AE", "AR")) or (m1 in ("CA", "CE", "CR") and exp1 == "CR") else []
        if alt is not None:                                           # D2/D3 contra las alternativas [S26] [S28]
            esp_err = [{"err3": z["err3"], "donde": z["donde"]} for z in alts]
        err_menor = _p("err_menor")
        if exp1 in ("AE", "AR", "CR") or alt is not None:
            if not errs:
                d("D2", "ERR ausente" + (" [%s]" % err_menor if err_menor else ""), amb=amb, cuenta=not err_menor)
            else:
                prim = esp_err[0]["err3"] if esp_err else None
                secs = [z["err3"] for z in esp_err[1:]]
                alt2 = next((z for z in x.get("alternativas_aceptadas") or [] if z["msa1"] == m1 and z["err3"] in obs3), None)
                vale = {"AE": ("100", "101", "102", "103"), "AR": ("205", "206", "207")}.get(m1, ()) if err_menor else ()
                if prim not in obs3 and m1 == exp1 and any(c in vale for c in obs3):
                    pass                                                                  # perfil: código de la misma clase
                elif prim not in obs3:
                    if any(c in secs for c in obs3):
                        if not (alt is not None and alt["por"] in ("S31", "S35", "S36")):   # alternativas equivalentes
                            d("D2", "ERR-3 secundario %s (primaria %s)" % (obs3, prim), cuenta=False)
                    elif alt is None and alt2 is not None:                                # R-alt2: mismo MSA-1, código alternativo
                        d("D2", "ERR-3 %s, esperado %s: aceptado [%s] (%s %s sobre %s%s)" % (obs3, prim, alt2["por"], m1,
                          alt2["err3"], alt2["donde"], motivo(alt2)), cuenta=False, causa="alternativa_" + alt2["por"])
                    else:
                        d("D2", "ERR-3 %s, esperado %s" % (obs3, prim) + (" [%s]" % err_menor if err_menor else ""), amb=amb,
                          cuenta=not err_menor)
                bueno = [(c, e4) for c, e4 in codigos if c == prim] or codigos[:1]
                e4 = bueno[0][1]
                if not e4:
                    d("D3", "ERR-4 ausente", cuenta=False)
                elif e4.upper() in ("W", "I"):
                    d("D3", "ERR-4 %s en un error" % e4, cuenta=False)
        else:
            for c, e4 in codigos:
                if c == "0" and e4.upper() != "I":
                    d("D3", "ERR-3 0 con ERR-4 %r" % e4, cuenta=False)
                elif c != "0" and e4.upper() == "E":
                    d("D2", "ERR %s/E contradice %s" % (c, m1))
                elif c != "0" and not e4:                         # N7: como en AE/AR, ERR-4 ausente se anota y no cuenta
                    d("D3", "ERR-4 ausente", cuenta=False)
        if _p("notas_err"):
            for z in errs:
                c3, e6, e8 = a.campo(z, 3).split(a.c)[0], a.campo(z, 6), a.campo(z, 8)
                if c3 == "0" and m1 == "AA":
                    d("N", "ERR 0/I con AA: forma de éxito del perfil [%s]" % _p("notas_err"), cuenta=False)
                if not _vacio_en(e6, _seps(a)) or not _vacio_en(e8, _seps(a)):   # B3
                    d("N", "ERR-6/ERR-8 presentes (identificadores asignados o texto): se anotan, no se juzgan [%s]"
                      % _p("notas_err"), cuenta=False)
        m2 = a.campo(msa[0], 2) if msa else ""
        if m10 is not None and m2 != m10 and not (len(m10) > 20 and m2 == m10[:20] and not _p("msa2_integro")):
            d("D4", "MSA-2 %r no devuelve MSH-10 %r" % (m2[:30], m10[:30]), k=k)     # cuenta: acuse inservible [C]
        cab = x.get("cabecera_ack") or {}
        h = a.segs[0]
        if cab:
            if a.campo(h, 9).upper() != cab["msh9"].upper():
                d("D6", "MSH-9 del ACK %r, esperado %r" % (a.campo(h, 9), cab["msh9"]), cuenta=False)
            if a.campo(h, 5) != cab["msh5"] or a.campo(h, 6) != cab["msh6"]:
                d("D6", "MSH-5/6 del ACK no copian MSH-3/4", cuenta=False)
            if a.campo(h, 11) != cab["msh11"]:
                d("D6", "MSH-11 del ACK no copia el entrante", cuenta=False)
            if _vacio_en(a.campo(h, 10), _seps(a)):
                d("D6", "MSH-10 del ACK vacío", cuenta=False)
            if not _vacio_en(a.campo(h, 16), _seps(a)) and not _p("ack_msh16_ignorado"):
                d("D6", "MSH-16 del ACK no nulo", cuenta=False)
            if _p("ack_msh18") and not _vacio_en(a.campo(h, 18), _seps(a)) and a.campo(h, 18).split(a.r)[0].upper() != _p("ack_msh18"):
                d("D6", "MSH-18 del ACK %r, el perfil espera %s [%s]" % (a.campo(h, 18), _p("ack_msh18"), _p("regla_msh18")),
                  cuenta=False)
    sin_msh = (esp[0].get("trama") or {}).get("sin_msh") or []
    if libres and sin_msh:                                            # [S31] el marco sin MSH no espera acuse
        d("D0", "ACK sobrante: %d ACK para %d mensajes; el marco %d sin MSH no es un mensaje [S31]" % (len(obs), len(ms), sin_msh[0]),
          cuenta=False, causa="trama", k=len(esp) - 1)
    elif libres and _p("ack_sobrante_nota"):
        d("N", "ACK sobrante: %d ACK para %d mensajes; el emisor lo ignora [%s]" % (len(obs), len(ms), _p("ack_sobrante_nota")),
          cuenta=False, k=len(esp) - 1)
    return out


# ---------------------------------------------------------------------------- autoprueba §5
B = ["MSH|^~\\&|LAB_SYS|CLINICA_B|ADT_IN|CIRCUITO|20230101171416||ADT^A01^ADT_A01|MSG1|P|2.5",
     "EVN|A01|20230101171416", "PID|1||ID1^^^HOSP^MR||Apellido^Nombre||19600910|M", "PV1|1|I|CLINIC_1"]
ACK_AA = "MSH|^~\\&|LABFHIR|LAB|LAB_SYS|CLINICA_B|<hora oculta>||ACK^A01^ACK|X1|P|2.5\nMSA|AA|MSG1"


def _campo_set(seg, n, v):
    p = seg.split("|")
    i = n - 1 if seg.startswith("MSH") else n
    while len(p) <= i:
        p.append("")
    p[i] = v
    return "|".join(p)


def _ev(segs=None, log=None, entorno=None, conexion=None, ack=ACK_AA, mensaje=None):
    segs = list(B) if segs is None else segs
    return {"mensaje": mensaje if mensaje is not None else "<VT>" + "\n".join(segs) + "\n<FS>",
            "conexion": conexion if conexion is not None else ["conexión establecida", "ACK recibido a los 0.01 s"],
            "sesiones": [{"log": log if log is not None else [{"tipo": "Info", "texto": "Patient creado (HTTP 201)"}]}],
            "ack": ack, "entorno": entorno or []}


def _con(campos):
    segs = list(B)
    for (sg, n), v in campos.items():
        k = [s.split("|")[0] for s in segs].index(sg)
        segs[k] = _campo_set(segs[k], n, v)
    return segs


def _res(x):
    e = x[0]
    return (e["debe_haber_ack"], e.get("msa1"), e["err"][0]["err3"] if e["err"] else None)


def autoprueba():
    global NIVEL
    mal = []

    def mira(nombre, obtenido, esperado_):
        ok = obtenido == esperado_
        print(("  ok  " if ok else "  MAL ") + nombre + ("" if ok else ": %r != %r" % (obtenido, esperado_)))
        if not ok:
            mal.append(nombre)

    def r(segs=None, **k):
        return _res(calcular(_ev(segs, **k)))

    mira("tablas leídas del estándar: 0003 (A01, A08), 0004 y 0211 (UNICODE UTF-8, ASCII)",
         ({"A01", "A08"} <= T0003, set("EIOPRBCNU") <= T0004, {"UNICODE UTF-8", "ASCII", "8859/1"} <= T0211), (True, True, True))
    mira("T01 base", r(), ("si", "AA", None))
    x = calcular(_ev(_con({("MSH", 15): "AL", ("MSH", 16): "AL"})))[0]
    mira("T02 AL/AL [S13]: mejorado, aplicación AA síncrona, aplicación requerida", (x["modo"], x["clase_ack"], x["msa1"], x["aplicacion_requerida"]),
         ("mejorado", "aplicacion", "AA", True))
    mira("T02: AA observado -> sin discrepancia (sin D5) [S13]", sorted(z["id"] for z in comparar(_ev(_con({("MSH", 15): "AL", ("MSH", 16): "AL"})))), [])
    x = calcular(_ev(_con({("MSH", 15): "NE", ("MSH", 16): "AL"})))[0]
    mira("T03 NE/AL: aplicación AA, sin D5", (x["clase_ack"], x["msa1"], [z["id"] for z in comparar(_ev(_con({("MSH", 15): "NE", ("MSH", 16): "AL"})))]),
         ("aplicacion", "AA", []))
    mira("T04 NE/NE: no; AA observado -> D0 no solicitado",
         (r(_con({("MSH", 15): "NE", ("MSH", 16): "NE"}))[0], [z["que"] for z in comparar(_ev(_con({("MSH", 15): "NE", ("MSH", 16): "NE"})))]),
         ("no", ["ACK no solicitado"]))
    mira("T05 ER/NE: no", r(_con({("MSH", 15): "ER", ("MSH", 16): "NE"}))[0], "no")
    mira("T06 ER/NE y ORU: CR 200", r(_con({("MSH", 15): "ER", ("MSH", 16): "NE", ("MSH", 9): "ORU^R01^ORU_R01"})), ("si", "CR", "200"))
    mira("T07 ORU: AR 200", r(_con({("MSH", 9): "ORU^R01^ORU_R01"})), ("si", "AR", "200"))
    mira("T08 A08: AR 201", r(_con({("MSH", 9): "ADT^A08^ADT_A01"})), ("si", "AR", "201"))
    NIVEL = "estricto"
    mira("T09 ADT^A01 estricto (a petición): AR 101", r(_con({("MSH", 9): "ADT^A01"})), ("si", "AR", "101"))
    NIVEL = "consumido"
    mira("T09 consumido (defecto, S6): AA", r(_con({("MSH", 9): "ADT^A01"})), ("si", "AA", None))
    mira("T10 estructura ADT_A04: AR 200", r(_con({("MSH", 9): "ADT^A01^ADT_A04"})), ("si", "AR", "200"))
    mira("T11 MSH-9 vacío: AR 101", r(_con({("MSH", 9): ""})), ("si", "AR", "101"))
    mira("T12 MSH-12 2.3: AR 203", r(_con({("MSH", 12): "2.3"})), ("si", "AR", "203"))
    mira("T13 MSH-12 2.5^ES: AA", r(_con({("MSH", 12): "2.5^ES"})), ("si", "AA", None))
    mira("T14 MSH-11 X: AR 202", r(_con({("MSH", 11): "X"})), ("si", "AR", "202"))
    mira("T15 MSH-11 T: AA", r(_con({("MSH", 11): "T"})), ("si", "AA", None))
    x = calcular(_ev(_con({("MSH", 9): "ORU^R01", ("PID", 3): ""})))[0]
    mira("T16 ORU y PID-3 vacío: AR 200, sin 101", (x["msa1"], [z["err3"] for z in x["err"]]), ("AR", ["200"]))
    mira("T17 sin PV1: AE 100", r(B[:3]), ("si", "AE", "100"))
    mira("T18 PV1 antes de PID: AE 100", r([B[0], B[1], B[3], B[2]]), ("si", "AE", "100"))
    mira("T19 ZPD tras PID: AA", r(B[:3] + ["ZPD|1|X"] + B[3:]), ("si", "AA", None))
    mira("T20 NK1 entre PID y PV1: AA", r(B[:3] + ["NK1|1|Madre^Una"] + B[3:]), ("si", "AA", None))
    x = calcular(_ev(B[:3] + ["PID|1||ID2^^^HOSP^MR||Otro^Uno||19600910|M"] + B[3:]))[0]
    mira("T21 segundo PID tras el PID [S14]: AE 100, sin tolerancia", (x["msa1"], x["err"][0]["err3"], x["err"][0]["regla"], x["tolerancias"]),
         ("AE", "100", "P3.5", []))
    x = calcular(_ev(B[:2] + ["EVN|A01|20230101171416"] + B[2:]))[0]
    mira("T73 segundo EVN [S14]: AE 100 en EVN", (x["msa1"], x["err"][0]["err3"], x["err"][0]["donde"]), ("AE", "100", "EVN"))
    mira("T73c dos NK1 entre PID y PV1: AA (repetible)", r(B[:3] + ["NK1|1|Madre^Una", "NK1|2|Padre^Uno"] + B[3:]), ("si", "AA", None))
    mira("T22 segundo PID tras PV1: AE 100", r(B + ["PID|1||ID2^^^HOSP^MR||Otro^Uno||19600910|M"]), ("si", "AE", "100"))
    # ---- [S45] opcional conocido fuera de posición: se ignora [E2 §2.6.2 a]; el 100 por orden es de los obligatorios
    AL1, OBX = "AL1|1|DA|^Penicilina", "OBX|1|ST|^Nota||x"
    LEY45 = "  (%s; %s)" % (LEYENDA_SEG, LEYENDA_S45)

    def seg(segs):
        return resumen_segmentos(MR.mensajes("\n".join(segs))[0])

    def n45(segs):
        return [n for n in calcular(_ev(segs))[0]["notas"] if n.startswith("[S45]")]
    S45 = B + [AL1, OBX]
    mira("T90 [S45] OBX tras AL1 (orden de ADT_A03) en un ADT^A01: AA, nota, OBX~",
         (r(S45), n45(S45), seg(S45)),
         (("si", "AA", None), ["[S45] OBX tras AL1: segmento opcional fuera de su posición en ADT_A01 [E3 §3.3.1]; el receptor lo "
                               "ignora [E2 §2.6.2 a], no es AE 100 (nota, no cuenta)"], "MSH EVN PID PV1 AL1 OBX~" + LEY45))
    S45b = B[:3] + [AL1, OBX] + B[3:]
    mira("T90b [S45] AL1 y OBX antes de PV1: PV1 no está fuera de orden respecto a un opcional; AA, dos notas",
         (r(S45b), [n.split(":")[0] for n in n45(S45b)], seg(S45b)),
         (("si", "AA", None), ["[S45] AL1 antes de PV1", "[S45] OBX antes de PV1"], "MSH EVN PID AL1~ OBX~ PV1" + LEY45))
    S45c = [B[0], "NK1|1|Madre^Una"] + B[1:]
    mira("T90c [S45] NK1 antes de EVN: EVN en orden respecto a MSH/PID/PV1; AA, NK1~",
         (r(S45c), [n.split(":")[0] for n in n45(S45c)], seg(S45c)), (("si", "AA", None), ["[S45] NK1 antes de EVN"], "MSH NK1~ EVN PID PV1" + LEY45))
    S45d = [B[0], B[1], "SFT|x", B[2], B[3]]
    mira("T90d [S45] SFT tras EVN: SFT~, AA", (r(S45d), seg(S45d)), (("si", "AA", None), "MSH EVN SFT~ PID PV1" + LEY45))
    x = calcular(_ev([B[0], B[1], B[3], B[2]]))[0]
    mira("T90e [S2] PV1 antes de PID sigue siendo AE 100 P3.4 en PID, sin ~ ni nota S45",
         (_res([x]), x["err"][0]["regla"], x["err"][0]["donde"], n45([B[0], B[1], B[3], B[2]]), seg([B[0], B[1], B[3], B[2]])),
         (("si", "AE", "100"), "P3.4", "PID", [], "MSH EVN PV1 PID!  (%s)" % LEYENDA_SEG))
    x = calcular(_ev([B[0], B[2], B[1], B[3]]))[0]
    mira("T90f [S2] EVN tras PID: AE 100 P3.4 en EVN", (_res([x]), x["err"][0]["regla"], x["err"][0]["donde"]), (("si", "AE", "100"), "P3.4", "EVN"))
    S45g = [B[0], B[1], B[3], B[2], AL1, OBX]
    mira("T90g tras el primer P3.4 no se juzga el resto (como antes): sin ~ tras PID!",
         (r(S45g), seg(S45g), n45(S45g)), (("si", "AE", "100"), "MSH EVN PV1 PID! AL1 OBX  (%s)" % LEYENDA_SEG, []))
    S45h = B[:3] + ["NK1|1|Madre^Una", "PID|1||ID2^^^HOSP^MR||Otro^Uno||19600910|M"] + B[3:]
    x = calcular(_ev(S45h))[0]
    mira("T90h [S14] segundo PID tras NK1: repetido (P3.5, PID+), no fuera de orden respecto a NK1",
         (_res([x]), x["err"][0]["regla"], seg(S45h)), (("si", "AE", "100"), "P3.5", "MSH EVN PID NK1 PID+ PV1  (%s)" % LEYENDA_SEG))
    S45i = _con({("MSH", 9): "ORU^R01^ORU_R01"}) + [AL1, OBX]
    mira("T90i P2 (ORU) con OBX tras AL1: AR 200 y el resumen marca OBX~ (sin nota: P3 no corre)",
         (r(S45i), seg(S45i), n45(S45i)), (("si", "AR", "200"), "MSH EVN PID PV1 AL1 OBX~" + LEY45, []))
    S45j = B[:3] + [AL1]
    mira("T90j sin PV1 y AL1 tras PID: AE 100 por P3.3, AL1 sin ~ (el tope es el obligatorio que llega, no el ausente)",
         (r(S45j), seg(S45j), n45(S45j)), (("si", "AE", "100"), "MSH EVN PID AL1 | faltan: PV1", []))
    S45k = B + [OBX, AL1, OBX]
    mira("T90k OBX AL1 OBX: solo el segundo OBX se ignora", (r(S45k), seg(S45k), len(n45(S45k))),
         (("si", "AA", None), "MSH EVN PID PV1 OBX AL1 OBX~" + LEY45, 1))
    mira("T90l estructura(): claves nuevas", sorted(estructura(MR.mensajes("\n".join(S45))[0])["ignorados"]), [("OBX", "tras AL1")])
    mira("T23 PID-3 vacío: AE 101", r(_con({("PID", 3): ""})), ("si", "AE", "101"))
    mira("T24 PID-3 sin CX.1: AE 101", r(_con({("PID", 3): "^^^HOSP^MR"})), ("si", "AE", "101"))
    mira("T25 PID-5 vacío: AE 101", r(_con({("PID", 5): ""})), ("si", "AE", "101"))
    mira("T26 PID-5 solo separadores: AE 101", r(_con({("PID", 5): "^^^^"})), ("si", "AE", "101"))
    x = calcular(_ev(_con({("MSH", 10): ""})))[0]
    mira("T27 MSH-10 vacío: AE 101 y msa2 ''", (x["msa1"], x["err"][0]["err3"], x["msa2"]), ("AE", "101", ""))
    NIVEL = "estricto"
    mira("T28 EVN-2 vacío estricto (a petición): AE 101", r(_con({("EVN", 2): ""})), ("si", "AE", "101"))
    NIVEL = "consumido"
    x = calcular(_ev(_con({("EVN", 2): ""})))[0]
    mira("T28 consumido (S6): AA + nota [S6]", (x["msa1"], any("[S6]: 101 EVN-2" in n for n in x["notas"])), ("AA", True))
    x = calcular(_ev(_con({("MSH", 7): ""})))[0]
    mira("T67 MSH-7 vacío (S6): AA + nota", (x["msa1"], any("[S6]: 101 MSH-7" in n for n in x["notas"])), ("AA", True))
    mira("T67c PID-3 vacío (consumido): AE 101", r(_con({("PID", 3): ""})), ("si", "AE", "101"))
    mira("T29 PID-7 vacío: AA", r(_con({("PID", 7): ""})), ("si", "AA", None))
    x = calcular(_ev(_con({("PID", 3): '""'})))[0]
    mira("T30 PID-3 = \"\": AA + nota", (x["msa1"], bool(x["notas"])), ("AA", True))
    mira("T31 PID-7 mes 13: AE 102", r(_con({("PID", 7): "19601310"})), ("si", "AE", "102"))
    mira("T32 PID-7 196009: AA", r(_con({("PID", 7): "196009"})), ("si", "AA", None))
    mira("T33 PID-7 con zona: AA", r(_con({("PID", 7): "19600910120000+0100"})), ("si", "AA", None))
    mira("T34 PID-7 futura [S18]: AE 102", r(_con({("PID", 7): "20991231"})), ("si", "AE", "102"))
    x = calcular(_ev(_con({("PID", 7): "20991231", ("MSH", 7): ""})))[0]
    mira("T34c PID-7 futura con MSH-7 vacío: AA + nota L16", (x["msa1"], any("L16" in n for n in x["notas"])), ("AA", True))
    mira("T35 PID-8 X: AE 103", r(_con({("PID", 8): "X"})), ("si", "AE", "103"))
    x = calcular(_ev(_con({("PID", 8): "m"})))[0]
    mira("T36 PID-8 m: AA + tolerancia", (x["msa1"], bool(x["tolerancias"])), ("AA", True))
    mira("T37 PID-8 vacío: AA", r(_con({("PID", 8): ""})), ("si", "AA", None))
    x = calcular(_ev(_con({("PID", 8): "FEMALE"})))[0]
    mira("T38 PID-8 FEMALE: AA, truncado a F", (x["msa1"], bool(x["truncados"])), ("AA", True))
    x = calcular(_ev(_con({("PID", 8): "XY"})))[0]
    mira("T39 PID-8 XY: AE 103, truncado", (x["msa1"], x["err"][0]["err3"], bool(x["truncados"])), ("AE", "103", True))
    lar = "M" * 25
    x = calcular(_ev(_con({("MSH", 10): lar})))[0]
    ack = ACK_AA.replace("MSA|AA|MSG1", "MSA|AA|" + lar[:20])
    mira("T40 MSH-10 de 25: AA truncado; D4 admite los 20 primeros",
         (x["msa1"], bool(x["truncados"]), [z["id"] for z in comparar(_ev(_con({("MSH", 10): lar}), ack=ack))]), ("AA", True, []))
    mira("T41 PID-5 de 260: AA (nunca 104)", r(_con({("PID", 5): "A" * 260 + "^N"})), ("si", "AA", None))
    NIVEL = "estricto"
    mira("T42 PV1-2 Z estricto (a petición): AE 103", r(_con({("PV1", 2): "Z"})), ("si", "AE", "103"))
    NIVEL = "consumido"
    mira("T42 consumido (S6): AA", r(_con({("PV1", 2): "Z"})), ("si", "AA", None))
    x = calcular(_ev(_con({("PID", 3): "", ("PID", 8): "X"})))[0]
    mira("T43 PID-3 vacío y PID-8 X: 101 primaria, 103 secundaria", [z["err3"] for z in x["err"]], ["101", "103"])
    x = calcular(_ev([B[0], B[1], _campo_set(B[2], 8, "X")]))[0]
    mira("T44 sin PV1 y PID-8 X: 100 primaria, 103 secundaria", [z["err3"] for z in x["err"]], ["100", "103"])
    for tid, h, esp in (("T45", 500, ("AR", "207")), ("T46", 503, ("AR", "207")), ("T49", 400, ("AR", "207")),
                        ("T50", 422, ("AR", "207")), ("T51", 412, ("AR", "205")), ("T52", 409, ("AR", "206")),
                        ("T53", 200, ("AA", None)), ("T54", 404, ("AR", "207")), ("T55", 401, ("AR", "207"))):
        mira("%s HTTP %d" % (tid, h), r(log=[{"tipo": "Warning", "texto": "FHIR devolvio (HTTP %d)" % h}])[1:], esp)
    x = calcular(_ev(log=[{"tipo": "Warning", "texto": "FHIR rechazo el recurso (MSH-10=MSG1): FHIR devolvio 422"}]))[0]
    mira("T50 [S16]: sin ambigüedad, nota S16", (x["ambiguedades"], any("[S16]" in n for n in x["notas"])), ([], True))
    # S9 y S10
    x = calcular(_ev(_con({("PID", 5): "Mu<0xF1>oz^Ana"})))[0]
    mira("T69 byte latin-1, MSH-18 vacío [S9]: AA + tolerancia; clase ascii",
         (x["msa1"], any(t.startswith("[S9] PID-5") for t in x["tolerancias"]), x["descodificacion"]["clase_msh18"]), ("AA", True, "ascii"))
    x = calcular(_ev(_con({("PID", 5): "Mu<0xF1>oz^Ana", ("MSH", 18): "8859/1"})))[0]
    mira("T69b MSH-18 8859/1: AA, sin tolerancia, nota", (x["msa1"], x["tolerancias"], any("8859/1" in n for n in x["notas"])), ("AA", [], True))
    x = calcular(_ev(_con({("PID", 5): "Mu<0xF1>oz^Ana", ("MSH", 18): "ISO IR87"}),
                     log=[{"tipo": "Info", "texto": "Patient creado en FHIR: id=1 desde MSH-10=MSG1 (HTTP 201)"}]))[0]
    mira("T69c MSH-18 ISO IR87: AA, certeza AMB-10, sin ambigüedades de acuse",
         (x["msa1"], x["descodificacion"]["certeza"], x["ambiguedades"]), ("AA", "ambiguedad AMB-10", []))
    x = calcular(_ev(_con({("PID", 5): "Mu<0xF1>oz^Ana", ("MSH", 18): "UNICODE UTF-8"})))[0]
    mira("T69d MSH-18 UNICODE UTF-8: AA + tolerancia S9", (x["msa1"], any(t.startswith("[S9]") for t in x["tolerancias"])), ("AA", True))
    # DV-A1: el diseño pone «^N» detrás, pero LEN de PID-5 cuenta la repetición entera (252 > 250); sin «^N»
    # quedan 250 caracteres reales y 255 con el marcador, que es lo que la prueba de control debe separar.
    x = calcular(_ev(_con({("PID", 5): "A" * 249 + "<0xF1>"})))[0]
    mira("T70 249 A + <0xF1>: 250 caracteres reales, sin truncado", x["truncados"], [])
    x = calcular(_ev(_con({("PID", 5): "A" * 250 + "<0xF1>"})))[0]
    mira("T70c 250 A + <0xF1>: 251 caracteres reales, truncado", bool(x["truncados"]), True)
    mira("T71 C1 crudo en PID-5 [S10]: AE 102", r(_con({("PID", 5): "Pe\x80rez^Ana"})), ("si", "AE", "102"))
    mira("T71b NUL overlong <0xC0><0x80> [S9+S10]: AE 102", r(_con({("PID", 5): "<0xC0><0x80>Señor^Ana"})), ("si", "AE", "102"))
    mira("T71c \\XC080\\ [S10]: AE 102", r(_con({("PID", 5): "Pe\\XC080\\rez^Ana"})), ("si", "AE", "102"))
    mira("T71d ñ latin-1 imprimible: AA", r(_con({("PID", 5): "Mu<0xF1>oz^Ana"})), ("si", "AA", None))
    mira("T71e Señor: AA", r(_con({("PID", 5): "Señor^Ana"})), ("si", "AA", None))
    x = calcular(_ev(_con({("PV1", 3): "A\x01B"})))[0]
    mira("T71f control en PV1-3 (no consumido) [S17]: AA + nota", (x["msa1"], any("[S6]: 102 PV1-3" in n for n in x["notas"])), ("AA", True))
    # --- controles C0/DEL marcados por el arnés (diseno-control-c0-fable.md §3)
    mira("T71g <0x01> en PID-5 [S10]: AE 102", r(_con({("PID", 5): "Pe<0x01>rez^Ana"})), ("si", "AE", "102"))
    x = calcular(_ev(_con({("PV1", 3): "A<0x01>B"})))[0]
    mira("T71h <0x01> en PV1-3 (no consumido) [S17]: AA + nota S6 y S10",
         (x["msa1"], any("[S6]: 102 PV1-3" in n for n in x["notas"]), any(n.startswith("[S10] PV1-3: byte 01") for n in x["notas"])),
         ("AA", True, True))
    mira("T71i <0x0A> dentro de PID-5 [S10]: AE 102", r(_con({("PID", 5): "Pe<0x0A>rez^Ana"})), ("si", "AE", "102"))
    mira("T71j <0x09> (TAB) en PID-5 [S10][S33]: AE 102", r(_con({("PID", 5): "Pe<0x09>rez^Ana"})), ("si", "AE", "102"))
    x = calcular(_ev(_con({("PID", 5): "A" * 249 + "<0x01>"})))[0]
    mira("T70d 249 A + <0x01>: 250 caracteres reales, sin truncado", x["truncados"], [])
    x = calcular(_ev(_con({("MSH", 15): "AL", ("MSH", 16): "AL"})))[0]
    mira("T72 AL/AL: nota S13", any("[S13]" in n for n in x["notas"]), True)
    ack_ca = ACK_AA.replace("MSA|AA|", "MSA|CA|")
    mira("T72c AL/AL con CA: sin discrepancia", [z["id"] for z in comparar(_ev(_con({("MSH", 15): "AL", ("MSH", 16): "AL"}), ack=ack_ca))], [])
    mira("T68 PID-5 solo U+200B [S7]: AA", r(_con({("PID", 5): "\u200b"})), ("si", "AA", None))
    mira("T68c PID-5 ^^^^: AE 101", r(_con({("PID", 5): "^^^^"})), ("si", "AE", "101"))
    ack_m = ACK_AA.replace("MSA|AA|MSG1", "MSA|AA|M<0xF1>1")
    mira("T70b MSH-10 M<0xF1>1 y MSA-2 igual: sin D4", "D4" in [z["id"] for z in comparar(_ev(_con({("MSH", 10): "M<0xF1>1"}), ack=ack_m))], False)
    ack_ae = ACK_AA.replace("MSA|AA|MSG1", "MSA|AE|MSG1\nERR||PID^1^7|102^Data type error^HL70357|E")
    mira("T74 PID-7 futura con AE 102 observado [S18]: sin discrepancia",
         [z["id"] for z in comparar(_ev(_con({("PID", 7): "20991231"}), ack=ack_ae))], [])
    mira("T47 entorno FHIR inalcanzable, sin HTTP: AR 207",
         r(log=[], entorno=["el puerto de FHIR al que llama el circuito estaba cerrado: FHIR era inalcanzable"])[1:], ("AR", "207"))
    mira("T48 Error sin HTTP: AR 207", r(log=[{"tipo": "Error", "texto": "connection refused"}])[1:], ("AR", "207"))
    x = calcular(_ev(log=[]))[0]
    mira("T56 sin log ni entorno: AA + nota sin evidencia", (x["msa1"], any("L5" in n for n in x["notas"])), ("AA", True))
    ev = _ev(_con({("PID", 8): "X"}))
    mira("T57 PID-8 X con HTTP 201 y AA observado: AE 103 y D1", (r(_con({("PID", 8): "X"})), "D1" in [z["id"] for z in comparar(ev)]),
         (("si", "AE", "103"), True))
    x = calcular(_ev(_con({("PID", 8): "X"}), log=[{"tipo": "Error", "texto": "HTTP 500"}]))[0]
    mira("T58 PID-8 X y HTTP 500 [S25]: AR 207, sin AMB-5, nota S25 con 103 PID-8",
         (x["msa1"], x["err"][0]["err3"], any("AMB-5" in a for a in x["ambiguedades"]),
          any("[S25]" in n and "103 PID-8" in n for n in x["notas"])), ("AR", "207", False, True))
    ev = _ev(entorno=["el servicio se paró y se volvió a arrancar durante el lote (stop, 2 s, start)"],
             conexion=["la conexión no se estableció: ConnectionRefusedError: [Errno 111] Connection refused"], ack=None)
    mira("T59 receptor parado: no, y sin ACK no hay discrepancia", (_res(calcular(ev))[0], comparar(ev)), ("no", []))
    mira("T60 sin ACK: D0 ACK ausente", [z["que"] for z in comparar(_ev(ack=None))], ["ACK ausente"])
    ev = _ev(mensaje="\n".join(B))
    mira("T61 sin VT/FS: AA", _res(calcular(ev)), ("si", "AA", None))
    mira("T62 cable 'hola': indeterminado", _res(calcular(_ev(mensaje="hola")))[0], "indeterminado")
    b2 = [s.replace("MSG1", "MSG2") for s in B]
    ev = _ev(mensaje="<VT>" + "\n".join(B) + "\n<FS><VT>" + "\n".join(b2) + "\n<FS>")
    mira("T63 dos mensajes, un ACK: dos esperados y D0 recuento", (len(calcular(ev)), [z["id"] for z in comparar(ev)]), (2, ["D0"]))
    mira("T64 BOM: AA", _res(calcular(_ev(mensaje="<VT>﻿" + "\n".join(B) + "\n<FS>"))), ("si", "AA", None))
    alt = ["MSH#$~\\&#LAB_SYS#CLINICA_B#ADT_IN#CIRCUITO#20230101171416##ADT$A01$ADT_A01#MSG1#P#2.5",
           "EVN#A01#20230101171416", "PID#1##ID1$$$HOSP$MR##Apellido$Nombre##19600910#M", "PV1#1#I#CLINIC_1"]
    mira("T65 separadores alternativos: AA", _res(calcular(_ev(mensaje="<VT>" + "\n".join(alt) + "\n<FS>"))), ("si", "AA", None))
    x = calcular(_ev(_con({("MSH", 15): "QQ"})))[0]
    mira("T66 MSH-15 QQ: mejorado como AL, CA + ambigüedad", (x["modo"], x["msa1"], any("A-5" in a for a in x["ambiguedades"])), ("mejorado", "CA", True))
    # comparación (esperado de T35: AE/103/E)
    e35 = _con({("PID", 8): "X"})
    H = "MSH|^~\\&|LABFHIR|LAB|LAB_SYS|CLINICA_B|<hora oculta>||ACK^A01^ACK|X1|P|2.5\n"
    def c(segs, ack_cuerpo):
        return sorted(z["que"].split(" ")[0] + ":" + z["id"] for z in comparar(_ev(segs, ack=H + ack_cuerpo)))
    mira("C1 AE + 103/E: sin discrepancia", c(e35, "MSA|AE|MSG1\nERR|||103^Table value not found^HL70357|E"), [])
    mira("C2 AE sin ERR: ERR ausente", c(e35, "MSA|AE|MSG1"), ["ERR:D2"])
    mira("C3 AE + 101: ERR-3 distinto", c(e35, "MSA|AE|MSG1\nERR|||101^^HL70357|E"), ["ERR-3:D2"])
    e43 = _con({("PID", 3): "", ("PID", 8): "X"})
    r4 = comparar(_ev(e43, ack=H + "MSA|AE|MSG1\nERR|||103|E"))
    mira("C4 esperado 101+103, observado 103: secundario (menor)", [(z["id"], z["cuenta"]) for z in r4], [("D2", False)])
    mira("C5 AE + 103/W: D3", c(e35, "MSA|AE|MSG1\nERR|||103|W"), ["ERR-4:D3"])
    mira("C6 MSA-2 MSG9: D4", c(e35, "MSA|AE|MSG9\nERR|||103|E"), ["MSA-2:D4"])
    mira("C7 AR en vez de AE: D1", c(e35, "MSA|AR|MSG1\nERR|||103|E"), ["MSA-1:D1"])
    mira("C8 AA + ERR 0/I: sin discrepancia", c(B, "MSA|AA|MSG1\nERR|||0^^HL70357|I"), [])
    mira("C9 AA + ERR 207/E: contradice", c(B, "MSA|AA|MSG1\nERR|||207|E"), ["ERR:D2"])
    mira("C10 MSH-9 del ACK ACK^A08^ACK: D6", c(B, "MSA|AA|MSG1").__len__() == 0 and
         [z["id"] for z in comparar(_ev(ack=ACK_AA.replace("ACK^A01^ACK", "ACK^A08^ACK")))], ["D6"])
    e02 = _con({("MSH", 15): "AL", ("MSH", 16): "AL"})
    mira("C11 AL/AL con AA [S13]: sin discrepancia", [z["id"] for z in comparar(_ev(e02))], [])
    mira("C12 AL/AL con CA: sin discrepancia", [z["id"] for z in comparar(_ev(e02, ack=H + "MSA|CA|MSG1"))], [])
    mira("C13 MSA XX: MSA-1 inválido", c(B, "MSA|XX|MSG1"), ["MSA-1:D1"])
    # ======================== S19-S29 (diseno-s19-s21-fable.md)
    def l05(h):
        return {"tipo": "Warning", "texto": "FHIR rechazo el recurso (MSH-10=MSG1): FHIR devolvio %d:" % h}
    L06_503 = {"tipo": "Error", "texto": "FHIR fallo del lado servidor (MSH-10=MSG1): FHIR devolvio 503:"}
    L07 = {"tipo": "Error", "texto": "No se pudo hablar con FHIR (MSH-10=MSG1): ERROR #6059: Unable to open TCP/IP socket to server localhost:59999"}
    TO = "ERROR <Ens>ErrFailureTimeout: FailureTimeout of 15 seconds exceeded in Lab.HL7.Operation.FhirPatient; status from last attempt was OK"
    L08 = [{"tipo": "Error", "texto": TO}, {"tipo": "Alert", "texto": TO}]
    L01 = {"tipo": "Info", "texto": "Patient creado en FHIR: id=x desde MSH-10=MSG1 (HTTP 201)"}
    L03_5 = {"tipo": "Warning", "texto": "Mensaje rechazado antes de FHIR (MSH-10=MSG1): Falta el nombre del paciente (PID-5): no se puede crear un Patient sin nombre"}
    E07 = "el puerto de FHIR al que llama el circuito estaba cerrado: FHIR era inalcanzable"
    E08 = "la ruta de FHIR a la que llama el circuito no existía"

    def ak(m1, e3=None, e4="E"):
        return H + "MSA|%s|MSG1" % m1 + ("\nERR|||%s|%s" % (e3, e4) if e3 else "")

    def cmp(segs, log, ack):
        return [(z["id"], z["cuenta"], z.get("causa")) for z in comparar(_ev(segs, log=log, ack=ack))]

    def v12(v, extra=None):
        return calcular(_ev(_con({**{("MSH", 12): v}, **(extra or {})})))[0]
    # --- S19
    x = v12("2.6")
    mira("T75 MSH-12 2.6 [S19]: AA, nota S19 y L17, version_msh12",
         (_res([x]), any("MSH-12 2.6 aceptada [S19]" in n for n in x["notas"]), any("L17" in n for n in x["notas"]), x["version_msh12"]),
         (("si", "AA", None), True, True, {"texto": "2.6", "leida": [2, 6, None], "aceptada": True}))
    for tid, v in (("T75b", "2.5.1"), ("T75c", "2.4")):
        x = v12(v)
        mira("%s MSH-12 %s: AA + nota S19" % (tid, v), (_res([x]), any("[S19]" in n for n in x["notas"])), (("si", "AA", None), True))
    mira("T75d MSH-12 2.10: AA (numérico)", r(_con({("MSH", 12): "2.10"})), ("si", "AA", None))
    mira("T75e MSH-12 2.6^ES: AA", r(_con({("MSH", 12): "2.6^ES"})), ("si", "AA", None))
    x = v12("2.3.1")
    mira("T75f MSH-12 2.3.1: AR 203 P2b", (_res([x]), x["err"][0]["regla"]), (("si", "AR", "203"), "P2b"))
    mira("T75g MSH-12 3.0: AR 203", r(_con({("MSH", 12): "3.0"})), ("si", "AR", "203"))
    for tid, v in (("T75h", "2"), ("T75i", "v2.6"), ("T75j", "2.6 "), ("T75k", "02.6")):
        x = v12(v)
        mira("%s MSH-12 %r: AR 203, nota de forma" % (tid, v), (_res([x]), any("no tiene la forma N.N[.N]" in n for n in x["notas"])),
             (("si", "AR", "203"), True))
    x = v12("2.5")
    mira("T75l MSH-12 2.5: AA sin nota S19", (_res([x]), any("[S19]" in n for n in x["notas"]), x["version_msh12"]["aceptada"]),
         (("si", "AA", None), False, True))
    mira("T75m MSH-12 2.6 y ORU: AR 200 (P2a antes)", r(_con({("MSH", 12): "2.6", ("MSH", 9): "ORU^R01^ORU_R01"})), ("si", "AR", "200"))
    # --- S21 / S24
    x = calcular(_ev(e35, log=[l05(400)]))[0]
    mira("T76 PID-8 X + 400 [S21]: AE 103, sin ambigüedades, nota S21", (_res([x]), x["ambiguedades"], any("[S21]" in n for n in x["notas"])),
         (("si", "AE", "103"), [], True))
    x = calcular(_ev(e35, log=[{"tipo": "Error", "texto": "HTTP 500"}]))[0]
    mira("T76c' PID-8 X + HTTP 500 (F1) [S25]: AR 207, sin AMB-5, nota S25",
         (_res([x]), any("AMB-5" in a for a in x["ambiguedades"]), any("[S25]" in n and "103 PID-8" in n for n in x["notas"])),
         (("si", "AR", "207"), False, True))
    NUL = _con({("PID", 5): "<0xC0><0x80>Señor^Ana"})
    mira("T77 NUL + 400 + AR 102: D1 tolerado [S21]", cmp(NUL, [l05(400)], ak("AR", "102")), [("D1", False, "rechazo_del_destino")])
    mira("T77b NUL + 422 + AR 102: D1 tolerado", cmp(NUL, [l05(422)], ak("AR", "102")), [("D1", False, "rechazo_del_destino")])
    mira("T77c NUL sin log + AR 102: D1 cuenta", cmp(NUL, [], ak("AR", "102")), [("D1", True, None)])
    mira("T77d NUL + L03 + AR 102: D1 cuenta", cmp(NUL, [L03_5], ak("AR", "102")), [("D1", True, None)])
    mira("T77e NUL + 503 + AR 102 [S25]: D2 cuenta (esperado AR 207)", cmp(NUL, [L06_503], ak("AR", "102")), [("D2", True, None)])
    mira("T77f NUL + 400 + AR 207: D1 y D2 cuentan", cmp(NUL, [l05(400)], ak("AR", "207")), [("D1", True, None), ("D2", True, None)])
    mira("T77g NUL + F1 400 + AR 102: D1 cuenta", cmp(NUL, [{"tipo": "Warning", "texto": "algo con HTTP 400"}], ak("AR", "102")),
         [("D1", True, None)])
    mira("T77h PID-3 vacío y PID-8 X + 400 + AR 103: D1 tolerado, D2 secundario [S24]", cmp(e43, [l05(400)], ak("AR", "103")),
         [("D1", False, "rechazo_del_destino"), ("D2", False, None)])
    mira("T77i PID-3 vacío + 400 + AR 102: D1 y D2 cuentan", cmp(_con({("PID", 3): ""}), [l05(400)], ak("AR", "102")),
         [("D1", True, None), ("D2", True, None)])
    # --- S25 / S29
    x = calcular(_ev(e35, log=[L07]))[0]
    mira("T78 PID-8 X + L07 [S25]: AR 207, contenido no acusado, err solo 207",
         (_res([x]), x.get("contenido_no_acusado"), [z["err3"] for z in x["err"]]),
         (("si", "AR", "207"), [{"err3": "103", "donde": "PID-8", "nivel": "consumido", "regla": "P5"}], ["207"]))
    x = calcular(_ev(e35, log=L08))[0]
    mira("T78b PID-8 X + L08: AR 207, notas S25 y L15", (_res([x]), any("[S25]" in n for n in x["notas"]), any("L15" in n for n in x["notas"])),
         (("si", "AR", "207"), True, True))
    x = calcular(_ev(_con({("PID", 3): ""}), log=[], entorno=[E07]))[0]
    mira("T78c PID-3 vacío + E07: AR 207, contenido 101", (_res([x]), x["contenido_no_acusado"][0]["err3"]), (("si", "AR", "207"), "101"))
    for tid, log, ent, esp_ in (("T78d", [l05(401)], None, "207"), ("T78e", [l05(404)], [E08], "207"), ("T78f", [l05(409)], None, "206")):
        x = calcular(_ev(e35, log=log, entorno=ent))[0]
        mira("%s PID-8 X + %s [S29]: AR %s, nota S25" % (tid, log[0]["texto"][-4:-1], esp_),
             (_res([x]), any("[S25]" in n for n in x["notas"])), (("si", "AR", esp_), True))
    x = calcular(_ev(e35, log=[l05(400)]))[0]
    mira("T78g PID-8 X + 400: AE 103, nota S21, sin contenido no acusado",
         (_res([x]), any("[S21]" in n for n in x["notas"]), "contenido_no_acusado" in x), (("si", "AE", "103"), True, False))
    mira("T78h PID-8 X + L01: AE 103", r(e35, log=[L01]), ("si", "AE", "103"))
    x = calcular(_ev(B[:3], log=[L06_503]))[0]
    mira("T78i sin PV1 + 503: AR 207, contenido 100 PV1", (_res([x]), x["contenido_no_acusado"][0]["err3"], x["contenido_no_acusado"][0]["donde"]),
         (("si", "AR", "207"), "100", "PV1"))
    x = calcular(_ev(log=[L06_503]))[0]
    mira("T78j B + 503 [S16/P7]: AR 207, sin contenido ni nota S25", (_res([x]), "contenido_no_acusado" in x, any("[S25]" in n for n in x["notas"])),
         (("si", "AR", "207"), False, False))
    mira("T78k T78 + AR 103: D2 cuenta", [(z[0], z[1]) for z in cmp(e35, [L07], ak("AR", "103"))], [("D2", True)])
    mira("T78l T78 + AE 103 [S28]: D1 no cuenta", [(z[0], z[1]) for z in cmp(e35, [L07], ak("AE", "103"))], [("D1", False)])
    # --- S22 / S26 / S27
    x = v12("2.6", {("PID", 8): "X"})
    mira("T79 2.6 + PID-8 X [S22]: AA, tolerancia S22", (_res([x]), [z[:14] for z in x["tolerancias"]]), (("si", "AA", None), ["[S22] PID-8 'X"]))
    NIVEL = "estricto"
    x = v12("2.6", {("EVN", 1): "A99"})
    mira("T79b 2.6 + EVN-1 A99 estricto: AA, tolerancia S22 EVN-1",
         (_res([x]), any(z.startswith("[S22] EVN-1") for z in x["tolerancias"]), any("103 EVN-1" in n for n in x["notas"])),
         (("si", "AA", None), True, False))
    x = v12("2.6", {("MSH", 18): "XYZ"})
    mira("T79c 2.6 + MSH-18 XYZ estricto: AA, tolerancia S22 MSH-18", (_res([x]), any(z.startswith("[S22] MSH-18") for z in x["tolerancias"])),
         (("si", "AA", None), True))
    NIVEL = "consumido"
    x = v12("2.5.1", {("PID", 8): "X"})
    mira("T79d 2.5.1 + PID-8 X [S27]: AA + S22", (_res([x]), any(z.startswith("[S22]") for z in x["tolerancias"])), (("si", "AA", None), True))
    mira("T79e 2.4 + PID-8 X: AE 103", _res([v12("2.4", {("PID", 8): "X"})]), ("si", "AE", "103"))
    mira("T79f 2.5 + PID-8 X: AE 103", _res([v12("2.5", {("PID", 8): "X"})]), ("si", "AE", "103"))
    mira("T79g 2.6 + MSH-11 X: AR 202", _res([v12("2.6", {("MSH", 11): "X"})]), ("si", "AR", "202"))
    x = v12("2.6", {("PID", 8): "x"})
    mira("T79h 2.6 + PID-8 x: AA + S22 (no S4)", (_res([x]), [z[:5] for z in x["tolerancias"]]), (("si", "AA", None), ["[S22]"]))
    x = v12("2.6", {("PID", 8): "XY"})
    mira("T79i 2.6 + PID-8 XY: AA, truncado y S22 sobre 'X'",
         (_res([x]), any(z.startswith("PID-8") for z in x["truncados"]), [z[:14] for z in x["tolerancias"]]),
         (("si", "AA", None), True, ["[S22] PID-8 'X"]))
    x = v12("2.6", {("PID", 8): ""})
    mira("T79j 2.6 + PID-8 vacío: AA sin tolerancias", (_res([x]), x["tolerancias"]), (("si", "AA", None), []))
    x = v12("2.6", {("PID", 8): "m"})
    mira("T79k 2.6 + PID-8 m: AA, solo S4", (_res([x]), [z.endswith("[S4]") for z in x["tolerancias"]]), (("si", "AA", None), [True]))
    x = v12("2.6", {("PID", 8): "X", ("PID", 3): ""})
    mira("T79l 2.6 + PID-8 X y PID-3 vacío: AE 101, S22 anotada",
         (_res([x]), [z["err3"] for z in x["err"]], any(z.startswith("[S22]") for z in x["tolerancias"])), (("si", "AE", "101"), ["101"], True))
    e26 = _con({("MSH", 12): "2.6", ("PID", 8): "X"})
    mira("T80 2.6 + X + AE 103 [S26]: D1 aceptado", (cmp(e26, None, ak("AE", "103")), calcular(_ev(e26))[0]["alternativas_aceptadas"]),
         ([("D1", False, "alternativa_S26")], [{"msa1": "AE", "err3": "103", "donde": "PID-8", "por": "S26"}]))
    mira("T80b 2.6 + X + AE 102: D1 y D2 cuentan", cmp(e26, None, ak("AE", "102")), [("D1", True, None), ("D2", True, None)])
    mira("T80c 2.5 + X + AE 103: nada", cmp(e35, None, ak("AE", "103")), [])
    # DV-T80d: el diseño espera solo D1; con esperado AA, un ERR 103/E contradice el AR (rama de hoy, como T80b)
    mira("T80d 2.6 + X + AR 103: D1 y D2 cuentan (S26 dice AE)", cmp(e26, None, ak("AR", "103")), [("D1", True, None), ("D2", True, None)])
    mira("T80e 2.6 + X + AE 103/W: D1 aceptado y D3 menor", cmp(e26, None, ak("AE", "103", "W")),
         [("D1", False, "alternativa_S26"), ("D3", False, None)])
    mira("T80f 2.6 + X + AA: nada; una alternativa", (cmp(e26, None, ACK_AA), len(calcular(_ev(e26))[0]["alternativas_aceptadas"])), ([], 1))
    x = calcular(_ev(e35, log=[L06_503]))[0]
    mira("T81 X + 503 + AE 103 [S28]: D1 aceptado", (cmp(e35, [L06_503], ak("AE", "103")), x["alternativas_aceptadas"]),
         ([("D1", False, "alternativa_S28")], [{"msa1": "AE", "err3": "103", "donde": "PID-8", "por": "S28"}]))
    mira("T81b X + 503 + AE 102: D1 y D2", cmp(e35, [L06_503], ak("AE", "102")), [("D1", True, None), ("D2", True, None)])
    mira("T81c X + 503 + AE 207: D1", cmp(e35, [L06_503], ak("AE", "207")), [("D1", True, None)])
    mira("T81d X + 503 + AR 103: D2", cmp(e35, [L06_503], ak("AR", "103")), [("D2", True, None)])
    mira("T81e PID-3 vacío y X + 503 + AE 103: D1 aceptado, D2 secundario", cmp(e43, [L06_503], ak("AE", "103")),
         [("D1", False, "alternativa_S28"), ("D2", False, None)])
    mira("T81f X + 503 + AR 207: nada", cmp(e35, [L06_503], ak("AR", "207")), [])
    mira("T81g X + 400 + AE 103: nada", cmp(e35, [l05(400)], ak("AE", "103")), [])
    # --- S30: el acuse no cambia (diseno-s30-fable.md)
    x = calcular(_ev(_con({("PID", 5): "     Fernández^María Elena^Lucia^^^^L"})))[0]
    mira("T82 PID-5 con 5 blancos delante: AA, sin truncados ni tolerancias", (_res([x]), x["truncados"], x["tolerancias"]),
         (("si", "AA", None), [], []))
    x = calcular(_ev(_con({("PID", 5): "     "})))[0]
    mira("T82b PID-5 solo blancos: AE 101 PID-5", (_res([x]), x["err"][0]["donde"]), (("si", "AE", "101"), "PID-5"))
    mira("T82c PID-5 solo blancos con XPN.7 = L: AA", r(_con({("PID", 5): "     ^^^^^^L"})), ("si", "AA", None))
    x = calcular(_ev(_con({("PID", 5): "     " + "A" * 246 + "^N"})))[0]
    mira("T82d 5 blancos + 246 A: truncado PID-5", [z[:5] for z in x["truncados"]], ["PID-5"])
    # --- S31, S35, S36 (diseno-s31-s34-fable.md)
    ORIGEN = "<VT><VT>" + B[0] + "\n<FS>\n<VT>" + "\n".join(B[1:]) + "\n<FS>\n<FS>"
    B2 = [z.replace("MSG1", "MSG2") for z in B]
    SIN_VT, SIN_FS = "\n".join(B) + "\n<FS>", "<VT>" + "\n".join(B) + "\n"
    DOS_UN = "<VT>" + "\n".join(B) + "\n" + "\n".join(B2) + "\n<FS>"
    DOS_MARCOS = "<VT>" + "\n".join(B) + "\n<FS><VT>" + "\n".join(B2) + "\n<FS>"
    PARTIDA_EVN = "<VT>" + "\n".join(B[:2]) + "\n<FS><VT>" + "\n".join(B[2:]) + "\n<FS>"
    PARTIDA_PV1 = "<VT>" + "\n".join(B[:3]) + "\n<FS><VT>" + B[3] + "\n<FS>"
    PARTIDA_PV1_X = "<VT>" + "\n".join(B[:2] + [_campo_set(B[2], 8, "X")]) + "\n<FS><VT>" + B[3] + "\n<FS>"
    PID2 = "PID|1||ID2^^^HOSP^MR||Otro^Uno||19600910|M"
    AK101 = H + "MSA|AR|MSG1\nERR|||101|E"
    ALT3 = [{"msa1": "AR", "err3": "101", "donde": "trama", "por": "S31"}, {"msa1": "AE", "err3": "101", "donde": "trama", "por": "S35"},
            {"msa1": "AR", "err3": "100", "donde": "trama", "por": "S35"}]

    def cmpm(mensaje, ack, log=None):
        return [(z["id"], z["cuenta"], z.get("causa")) for z in comparar(_ev(mensaje=mensaje, ack=ack, log=log))]
    xs = calcular(_ev(mensaje=ORIGEN))
    x = xs[0]
    mira("T83 marco con solo el MSH [S31][S35]: AE 100 x3, marco, trama, alternativas, notas",
         (len(xs), _res(xs), [z["donde"] for z in x["err"]], x["marco"], x["trama"], x["alternativas_aceptadas"],
          any(n.startswith("[S31][S35] el marco 1 trae solo el MSH") for n in x["notas"]),
          any(n.startswith("[S31] marco 2 sin MSH (EVN PID PV1)") for n in x["notas"])),
         (1, ("si", "AE", "100"), ["EVN", "PID", "PV1"], {"n": 1, "solo_msh": True, "trama_partida": True},
          {"marcos": 2, "sin_msh": [2], "anomalias": ["marcador <VT> repetido (marco 1)", "marcador <FS> repetido (tras el marco 2)"]},
          ALT3, True, True))
    mira("T83b AR 101 [S31]: D1 aceptado", cmpm(ORIGEN, AK101, [L03_5]), [("D1", False, "alternativa_S31")])
    mira("T83c AE 100: nada", cmpm(ORIGEN, ak("AE", "100")), [])
    mira("T83d AR 207: D1 y D2", cmpm(ORIGEN, ak("AR", "207")), [("D1", True, None), ("D2", True, None)])
    mira("T83e AE 101 / AR 100 [S35]", (cmpm(ORIGEN, ak("AE", "101")), cmpm(ORIGEN, ak("AR", "100"))),
         ([("D2", False, "alternativa_S35")], [("D1", False, "alternativa_S35")]))
    mira("T83f AA: D1 y D2", cmpm(ORIGEN, ACK_AA), [("D1", True, None), ("D2", True, None)])
    x = calcular(_ev(mensaje=PARTIDA_EVN))[0]
    mira("T83g MSH+EVN | PID+PV1 [S36]: AE 100 PID, tres alternativas S36, marco, nota",
         (_res([x]), x["err"][0]["donde"], [z["por"] for z in x["alternativas_aceptadas"]], [z["msa1"] + z["err3"] for z in x["alternativas_aceptadas"]],
          x["marco"], any(n.startswith("[S36] el marco 1 no trae PID, PV1") for n in x["notas"])),
         (("si", "AE", "100"), "PID", ["S36"] * 3, ["AR101", "AE101", "AR100"], {"n": 1, "solo_msh": False, "trama_partida": True}, True))
    for tid, cab, nota in (("SIN_VT", SIN_VT, "[A-2] trama: marco 1 sin <VT>"), ("SIN_FS", SIN_FS, "[A-2] trama: marco 1 sin <FS>"),
                           ("sin marcadores", "\n".join(B), "[A-2] trama: sin marcadores MLLP")):
        x = calcular(_ev(mensaje=cab))[0]
        mira("T84 %s: AA y nota [A-2]" % tid, (_res([x]), nota in x["notas"]), (("si", "AA", None), True))
    x = calcular(_ev())[0]
    mira("T84b cable normal: sin notas [A-2]/[S31], trama limpia", (any(n.startswith(("[A-2]", "[S31]")) for n in x["notas"]), x["trama"]),
         (False, {"marcos": 1, "sin_msh": [], "anomalias": []}))
    r85 = comparar(_ev(mensaje=ORIGEN, ack=AK101 + "\n" + H + "MSA|AR|\nERR|||100|E"))
    mira("T85 ACK sobrante: D1 aceptado y D0 menor", ([(z["id"], z["cuenta"], z.get("causa")) for z in r85], r85[-1]["que"]),
         ([("D1", False, "alternativa_S31"), ("D0", False, "trama")], "ACK sobrante: 2 ACK para 1 mensajes; el marco 2 sin MSH no es un mensaje [S31]"))
    mira("T85c dos marcos, dos ACK: nada", cmpm(DOS_MARCOS, ACK_AA + "\n" + ACK_AA.replace("MSG1", "MSG2")), [])
    x = calcular(_ev(mensaje="hola"))[0]
    mira("T62b hola: P0.b y [A-2]", ("P0.b" in x["notas"], "[A-2] trama: sin marcadores MLLP" in x["notas"]), (True, True))
    r86 = comparar(_ev(mensaje=ORIGEN, ack=ak("AE", "101")))
    mira("T86 AE 101 [S35]: texto", r86[0]["que"], "ERR-3 ['101'], esperado 100: aceptado [S35] (AE 101 sobre trama del marco 1, que trae solo el "
         "MSH (esperado AE 100: EVN, PID y PV1 ausentes))")
    mira("T86c AE 102 / AR 207 / AA", (cmpm(ORIGEN, ak("AE", "102")), cmpm(ORIGEN, ak("AR", "207")), cmpm(ORIGEN, ACK_AA)),
         ([("D2", True, None)], [("D1", True, None), ("D2", True, None)], [("D1", True, None), ("D2", True, None)]))
    mira("T86d S28 intacto (= T81e)", cmp(e43, [L06_503], ak("AE", "103")), [("D1", False, "alternativa_S28"), ("D2", False, None)])
    r87 = [cmpm(PARTIDA_EVN, ak(a1, a3)) for a1, a3 in (("AR", "101"), ("AE", "101"), ("AR", "100"), ("AE", "100"))]
    mira("T87 PARTIDA_EVN [S36]", (r87, comparar(_ev(mensaje=PARTIDA_EVN, ack=ak("AR", "101")))[0]["que"]),
         ([[("D1", False, "alternativa_S36")], [("D2", False, "alternativa_S36")], [("D1", False, "alternativa_S36")], []],
          "MSA-1 AR, esperado AE: aceptado [S36] (AR 101 sobre trama del marco 1, que no trae PID, PV1 (esperado AE 100))"))
    x = calcular(_ev(mensaje=PARTIDA_PV1))[0]
    mira("T87b PARTIDA_PV1", (_res([x]), x["err"][0]["donde"], [z["por"] for z in x["alternativas_aceptadas"]],
         any(n.startswith("[S36] el marco 1 no trae PV1") for n in x["notas"])), (("si", "AE", "100"), "PV1", ["S36"] * 3, True))
    x = calcular(_ev(mensaje=PARTIDA_PV1_X))[0]
    mira("T87c otro código", ([z["err3"] for z in x["err"]], cmpm(PARTIDA_PV1_X, ak("AE", "103")), cmpm(PARTIDA_PV1_X, ak("AR", "103")),
         cmpm(PARTIDA_PV1_X, ak("AR", "101"))),
         (["100", "103"], [("D2", False, None)], [("D1", True, None), ("D2", False, None)], [("D1", False, "alternativa_S36")]))
    x = calcular(_ev(B[:3], ack=ak("AR", "101")))[0]
    mira("T87d sin partición", (x["alternativas_aceptadas"], [(z["id"], z["cuenta"], z.get("causa")) for z in comparar(_ev(B[:3], ack=ak("AR", "101")))]),
         ([], [("D1", True, None), ("D2", True, None)]))
    x = calcular(_ev(mensaje="<VT>" + "\n".join(B) + "\n<FS><VT>" + PID2 + "\n<FS>"))[0]
    mira("T87e nada falta", (_res([x]), x["alternativas_aceptadas"], x["marco"]["trama_partida"]), (("si", "AA", None), [], True))
    mira("T87f sin marco sin MSH", [(calcular(_ev(mensaje=cab))[0]["marco"]["trama_partida"], calcular(_ev(mensaje=cab))[0]["alternativas_aceptadas"],
         len(calcular(_ev(mensaje=cab)))) for cab in ("\n".join(B), SIN_VT, SIN_FS, DOS_UN, DOS_MARCOS)],
         [(False, [], 1), (False, [], 1), (False, [], 1), (False, [], 2), (False, [], 2)])
    x = calcular(_ev(mensaje=PARTIDA_EVN.replace("ADT^A01^ADT_A01", "ORU^R01^ORU_R01")))[0]
    mira("T87g P2 antes que S36", (_res([x]), x["alternativas_aceptadas"]), (("si", "AR", "200"), []))
    # [E2 §2.5.4] diseño del arreglo solo_msh (Fable, 29-sep): un LF no termina segmento; el marco que arrastra
    # segmentos tras LF no «trae solo el MSH»
    # desviación declarada de las pruebas del diseño: B[0] acaba en MSH-12 y un LF pegado a él contamina la versión
    # (CR 203); la base de estas pruebas lleva MSH-18 al final, como el cable real del corpus
    BL = [B[0] + "||||||UNICODE UTF-8"] + B[1:]
    LF1 = "<VT>" + "<0x0A>".join(BL) + "<0x0A><FS>\n"
    LF_MSH = "<VT>" + BL[0] + "<0x0A>" + "\n".join(BL[1:]) + "\n<FS>"
    LF_FIN = "<VT>" + "\n".join(BL) + "<0x0A><FS>\n"
    CRLF = "<VT>" + "\n<0x0A>".join(BL) + "\n<0x0A><FS>\n"
    MSH_CR = "<VT>" + BL[0] + "\n<FS>"
    MSH_LF = "<VT>" + BL[0] + "<0x0A><FS>\n"
    LF_PART = "<VT>" + BL[0] + "<0x0A>" + BL[1] + "\n<FS><VT>" + "\n".join(BL[2:]) + "\n<FS>"
    LF_NK1 = "<VT>" + "<0x0A>".join(BL) + "<0x0A><FS><VT>NK1|1|x\n<FS>"
    MSHLF_PART = "<VT>" + BL[0] + "<0x0A><FS><VT>" + "\n".join(BL[1:]) + "\n<FS>"
    NOTA = "[E2 §2.5.4] el marco 1 trae "
    xs = calcular(_ev(mensaje=LF1))
    x = xs[0]
    mira("T88 LF en los cuatro segmentos: AE 100 x3, sin alternativas, nota, resumen",
         (len(xs), _res(xs), [z["donde"] for z in x["err"]], x["marco"], x["alternativas_aceptadas"],
          any(n.startswith(NOTA + "EVN PID PV1 tras <0x0A> en vez del terminador CR") for n in x["notas"]),
          any(n.startswith("[S31][S35]") for n in x["notas"]), resumen_segmentos(MR.mensajes(LF1)[0])),
         (1, ("si", "AE", "100"), ["EVN", "PID", "PV1"], {"n": 1, "solo_msh": False, "trama_partida": False}, [], True, False,
          "MSH | faltan: EVN PID PV1 | tras control no CR: EVN PID PV1"))
    mira("T88b LF: AR 101 / AE 101 / AR 100 / AE 100 / AA",
         [cmpm(LF1, a) for a in (ak("AR", "101"), ak("AE", "101"), ak("AR", "100"), ak("AE", "100"), ACK_AA)],
         [[("D1", True, None), ("D2", True, None)], [("D2", True, None)], [("D1", True, None)], [],
          [("D1", True, None), ("D2", True, None)]])
    x = calcular(_ev(mensaje=MSH_CR))[0]
    mira("T88c solo el MSH con CR: S31/S35 como siempre",
         (x["marco"], x["alternativas_aceptadas"], any(n.startswith("[S31][S35]") for n in x["notas"]),
          any(n.startswith(NOTA) for n in x["notas"]), cmpm(MSH_CR, ak("AR", "101"))),
         ({"n": 1, "solo_msh": True, "trama_partida": False}, ALT3, True, False, [("D1", False, "alternativa_S31")]))
    x = calcular(_ev(mensaje=MSH_LF))[0]
    mira("T88d solo el MSH terminado en LF: S31/S35 por la letra",
         (x["marco"]["solo_msh"], x["alternativas_aceptadas"], any(n.startswith(NOTA) for n in x["notas"]),
          any(n.startswith("[S10] MSH-") and "byte 0A" in n for n in x["notas"])), (True, ALT3, False, True))
    x = calcular(_ev(mensaje=LF_MSH))[0]
    mira("T88e LF solo tras el MSH",
         (_res([x]), [z["donde"] for z in x["err"]], x["marco"]["solo_msh"], x["alternativas_aceptadas"],
          any(n.startswith(NOTA + "EVN tras <0x0A>") for n in x["notas"]), cmpm(LF_MSH, ak("AR", "101"))),
         (("si", "AE", "100"), ["EVN"], False, [], True, [("D1", True, None), ("D2", True, None)]))
    x = calcular(_ev(mensaje=LF_FIN))[0]
    mira("T88f LF al final del último segmento: sin cambio (Q-LF-1)",
         (_res([x]), x["alternativas_aceptadas"], any(n.startswith(NOTA) for n in x["notas"]), resumen_segmentos(MR.mensajes(LF_FIN)[0])),
         (("si", "AA", None), [], False, "MSH EVN PID PV1"))
    x = calcular(_ev(mensaje=CRLF))[0]
    rs = resumen_segmentos(MR.mensajes(CRLF)[0])
    mira("T88g CRLF: lectura literal (Q-LF-2), nota",
         (_res([x]), [z["donde"] for z in x["err"]], x["marco"]["solo_msh"], x["alternativas_aceptadas"],
          any(n.startswith(NOTA + "EVN PID PV1 tras <0x0A>") for n in x["notas"]), "faltan: EVN PID PV1" in rs, "?" in rs),
         (("si", "AE", "100"), ["EVN", "PID", "PV1"], False, [], True, True, True))
    x = calcular(_ev(mensaje=LF_PART))[0]
    mira("T88h partida con LF: S36 por lo que falta de verdad",
         (_res([x]), [z["donde"] for z in x["err"]], x["marco"], [z["por"] for z in x["alternativas_aceptadas"]],
          any(n.startswith("[S36] el marco 1 no trae PID, PV1:") for n in x["notas"]), cmpm(LF_PART, ak("AR", "101")),
          comparar(_ev(mensaje=LF_PART, ack=ak("AR", "101")))[0]["que"]),
         (("si", "AE", "100"), ["EVN", "PID", "PV1"], {"n": 1, "solo_msh": False, "trama_partida": True}, ["S36"] * 3, True,
          [("D1", False, "alternativa_S36")],
          "MSA-1 AR, esperado AE: aceptado [S36] (AR 101 sobre trama del marco 1, que no trae PID, PV1 (esperado AE 100))"))
    x = calcular(_ev(mensaje=LF_NK1))[0]
    mira("T88i nada falta por la partición: sin S36",
         (_res([x]), x["marco"]["trama_partida"], x["alternativas_aceptadas"], any(n.startswith("[S36]") for n in x["notas"]),
          any(n.startswith("[S31] marco 2 sin MSH (NK1)") for n in x["notas"]), cmpm(LF_NK1, ak("AR", "101"))),
         (("si", "AE", "100"), True, [], False, True, [("D1", True, None), ("D2", True, None)]))
    x = calcular(_ev(mensaje=MSHLF_PART))[0]
    mira("T88j MSH<LF> | resto: como ORIGEN",
         (x["marco"]["solo_msh"], [z["por"] for z in x["alternativas_aceptadas"]], cmpm(MSHLF_PART, ak("AR", "101"))),
         (True, ["S31", "S35", "S35"], [("D1", False, "alternativa_S31")]))
    mira("T88k controles sin cambio: sin nota, resumen de siempre",
         [(any(n.startswith(NOTA) for n in calcular(_ev(mensaje=c) if c else _ev())[0]["notas"]),
           resumen_segmentos(MR.mensajes(c or "\n".join(B))[0])) for c in (None, ORIGEN, PARTIDA_EVN, "\n".join(B[:3]))],
         [(False, "MSH EVN PID PV1"), (False, "MSH | faltan: EVN PID PV1"), (False, "MSH EVN | faltan: PID PV1"),
          (False, "MSH EVN PID | faltan: PV1")])
    mira("T82e blancos finales: el acuse no mira", (r(_con({("PID", 5): "Fernández   ^María Elena^Lucia^^^^L"})),
         calcular(_ev(_con({("PID", 5): "Fernández   ^María Elena^Lucia^^^^L"})))[0]["tolerancias"]), (("si", "AA", None), []))
    mira("T82f PID-5 solo blancos: AE 101", r(_con({("PID", 5): "   "})), ("si", "AE", "101"))
    # [S39] contradicción MSH-18 / bytes (diseno-citas-s38-s39-fable.md)
    GARCIA = "García^Lucía^Óscar^^^^L"

    def cm(msh18, pid5):
        return contradiccion_msh18(MR.mensajes("\n".join(_con({("MSH", 18): msh18, ("PID", 5): pid5})))[0])
    mira("T89 ASCII + UTF-8", cm("ASCII", GARCIA),
         {"msh18": "ASCII", "clase": "ascii", "motivo": "utf8_multibyte", "donde": ["PID-5"], "bytes": [],
          "texto": "[S39] MSH-18 = ASCII contradice los bytes del cable: caracteres fuera de 7-bit ASCII, UTF-8 válido, en PID-5 (nota menor, no cuenta)"})
    mira("T89b vacío + UTF-8", (cm("", GARCIA) or {}).get("texto"),
         "[S39] MSH-18 ausente (ASCII por defecto) contradice los bytes del cable: caracteres fuera de 7-bit ASCII, UTF-8 válido, en PID-5 (nota menor, no cuenta)")
    x89c = cm("UNICODE UTF-8", "Mu<0xF1>oz^Ana^^^^^L") or {}
    mira("T89c UTF-8 + byte latin-1", (x89c.get("motivo"), x89c.get("bytes"), x89c.get("texto")),
         ("bytes_no_utf8", ["F1"], "[S39] MSH-18 = UNICODE UTF-8 contradice los bytes del cable: bytes F1 que no son UTF-8, leídos como latin-1 [S9], en PID-5 (nota menor, no cuenta)"))
    mira("T89d 8859/1 + byte latin-1: coherente", cm("8859/1", "Mu<0xF1>oz^Ana^^^^^L"), None)
    mira("T89e 8859/1 + UTF-8", (cm("8859/1", GARCIA) or {}).get("texto"),
         "[S39] MSH-18 = 8859/1 contradice los bytes del cable: UTF-8 multibyte válido en un juego de un byte, en PID-5 (nota menor, no cuenta)")
    def dcod(msh18, pid5):
        return calcular(_ev(_con({("MSH", 18): msh18, ("PID", 5): pid5})))[0]["descodificacion"]
    mira("T89j S39 callada cuando S9 ya lo dice (UTF-8 + byte F1; ASCII + byte F1)",
         [(dcod(v, "Mu<0xF1>oz^Ana^^^^^L")["contradiccion"], dcod(v, "Mu<0xF1>oz^Ana^^^^^L").get("contradiccion_callada")) for v in ("UNICODE UTF-8", "ASCII")],
         [(None, "S9"), (None, "S9")])
    x89k = dcod("ASCII", "García<0xF1>^Lucía^^^^^L")
    mira("T89k ASCII + UTF-8 multibyte + byte F1: la nota se mantiene", ((x89k["contradiccion"] or {}).get("motivo"), x89k.get("contradiccion_callada")),
         ("utf8_multibyte", None))
    mira("T89f-i multibyte, fuera de tabla, ASCII puro, UTF-8 coherente",
         [cm("ISO IR87", GARCIA), cm("XYZ", GARCIA), cm("ASCII", "Garcia^Lucia^^^^^L"), cm("UNICODE UTF-8", GARCIA)], [None] * 4)
    print("AUTOPRUEBA DE acuse_referencia: " + ("TODO BIEN" if not mal else "FALLAN %d" % len(mal)))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(autoprueba() if sys.argv[1:2] == ["--autoprueba"] else 0)
