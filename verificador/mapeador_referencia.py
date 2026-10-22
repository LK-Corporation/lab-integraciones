#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mapeador de referencia (REGLA-mapeador.md): calcula el canónico que DEBERÍA salir de un ADT^A01 y
lo compara con el que salió. Determinista; solo usa el contrato, HL7 v2.5 y el mapeo oficial HL7
v2-to-FHIR de la tabla 0001. Ninguna regla menciona un operador ni un caso: cada una cita su fuente.

La firma es MÍA (lo escribe quien conoce el catálogo), declarado como `v3-invariante`.

Alcance: mensajes ACEPTADOS con canónico (MSA-1 = AA y canónico presente). Lo demás, fuera.

Fuentes de cada regla:
  [C] contrato del circuito (medida/encargo_medida.md §5)
  [E] HL7 v2.5 capítulo 2 (separadores §2.5, escapes §2.7, tipos de dato) y capítulo 3 (PID, ADT_A01)
  [M] mapeo oficial HL7 v2-to-FHIR, ConceptMap table-hl70001-to-administrative-gender
  [D] declarado: lo que el contrato no fija y se toma de un caso base (unir subcomponentes con espacio)
  [V] decisión del experto (Víctor, 27-sep, tras el piloto): minúscula = tolerancia; el límite de 10
      repeticiones del contrato es un defecto
  [S19] versiones aceptadas: 2.x desde 2.4; [S22] en un mensaje posterior a 2.5, un PID-8 fuera de la 0001
      de v2.5 no es imposible: Gender solo tiene que ser un código de AdministrativeGender
  [S30][S32][S33][S34][S37] blancos (U+0020, Zs, Zl, Zp) quitados al guardar en los bordes de cada parte de
      FamilyName/GivenName: tolerancia; nunca se tolera quitar un no-blanco
  [S31][S36] el cable se lee por marcos MLLP: cada MSH abre un mensaje dentro de su marco; un marco sin MSH no es mensaje
  [E2 §2.5.4] el terminador es CR; un segmento tras otro byte de control no se lee como segmento (segmentos_ocultos)

Uso: python3 mapeador_referencia.py --autoprueba
"""
import calendar
import itertools
import re
import sys

MAPEO_0001 = {"F": "female", "M": "male", "O": "other", "U": "unknown", "A": "other", "N": "other"}   # [M]
MAXREP = None       # [V] el «como mucho diez repeticiones» del contrato es un defecto: se miran todas [E]
LONG_MAX = {("MSH", 10): 20, ("MSH", 3): 227, ("MSH", 4): 227, ("MSH", 11): 3,                     # [E] v2.5
            ("PID", 3): 250, ("PID", 5): 250, ("PID", 7): 26, ("PID", 8): 1}
# Gancho del perfil del sitio: lo instala acuse_referencia al importarse (este módulo no lo importa: evita el ciclo).
# Es un callable sin argumentos que devuelve {(seg, n): máximo} con lo que el perfil ACTIVO fija distinto de v2.5
# (hoy solo MSH-10, regla H10), o {} / None con el perfil «lab». Sin gancho (mapeador solo), v2.5.
LONG_PERFIL = None


def long_max():
    """LONG_MAX con las longitudes que el perfil del sitio activo fija. Con «lab» o sin gancho, LONG_MAX tal cual."""
    extra = LONG_PERFIL() if LONG_PERFIL else None
    if not extra:
        return LONG_MAX
    d = dict(LONG_MAX)
    d.update(extra)
    return d
ADMINISTRATIVE_GENDER = ("male", "female", "other", "unknown")                                     # [F AdministrativeGender]
VERSION_MINIMA = (2, 4)     # [S19] se acepta MSH-12 2.x desde la 2.4
VERSION_REGLAS = (2, 5)     # reglas, tablas y longitudes de v2.5 para todas (L17)
CAMPOS = ("Identifier", "FamilyName", "GivenName", "Gender", "BirthDate", "MsgControlId",
          "SendingApp", "SendingFacility", "MsgEvent", "ProcessingId", "Truncado")


# ---------------------------------------------------------------------------- versión [S19] [S22]
VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)(?:\.(0|[1-9]\d*))?$")


def version_id(v):
    """MSH-12.1 -> (mayor, menor, parche|None) en enteros, o None si no tiene la forma N.N[.N] (sin blancos)."""
    mt = VERSION_RE.match(v or "")
    if not mt:
        return None
    return int(mt.group(1)), int(mt.group(2)), int(mt.group(3)) if mt.group(3) is not None else None


def version_aceptada(v):
    """[S19] 2.x desde 2.4 (el parche no cuenta)."""
    vi = version_id(v)
    return vi is not None and vi[0] == 2 and vi[:2] >= VERSION_MINIMA


def posterior_a_25(v):
    """[S22] [S27] posterior a la 2.5 de la evidencia: (mayor, menor, parche o 0) > (2, 5, 0); 2.5.1 cuenta."""
    vi = version_id(v)
    return vi is not None and (vi[0], vi[1], vi[2] or 0) > (2, 5, 0)


# ---------------------------------------------------------------------------- lectura del cable [E]
MARCADOR = re.compile(r"(?:<0x[0-9A-Fa-f]{2}>)+")    # [S9] la evidencia marca así los bytes no decodificables
CONTROL = re.compile("[\x00-\x1f\x7f-\x9f]")            # [S10] C0, DEL y C1; los Cf (anchura cero) no [S7]


def _subruns(bs):
    """Parte un run de bytes marcados: cada byte < 0x80 va solo; los bytes >= 0x80 contiguos van juntos."""
    out = []
    for b in bs:
        if b < 0x80 or not out or out[-1][-1] < 0x80:
            out.append(bytes([b]))
        else:
            out[-1] += bytes([b])
    return out


LF_MARCADO = "<0x0A>"


# [S10] (diseno-control-c0-fable.md) DV-C0-1: el LF se queda marcado <0x0A> (vía lf) por L1/S31-S36; el resto de C0/DEL se
# decodifica (vía control). DV-C0-3: el marcador <0x0A> puede partirse al truncar [S3] (previo, declarado).
def control_en(v):
    """[S10] Primer carácter de control de v: crudo (C0, DEL, C1) o el LF que la evidencia deja marcado <0x0A> [L1].
    -> code point o None."""
    c = CONTROL.search(v)
    i = v.find(LF_MARCADO)
    if c and (i < 0 or c.start() < i):
        return ord(c.group(0))
    return 0x0A if i >= 0 else None


def descodificar(linea, fsep=None):
    """[S9] Cada secuencia contigua de marcadores <0xNN> se decodifica entera: primero UTF-8 estricto; si falla,
    latin-1. Un byte < 0x80 marcado se deja literal. -> (texto, registros {seg, n, bytes, texto, via})."""
    regs = []
    if "<0x" not in linea:
        return linea, regs
    es_msh = linea.startswith("MSH")
    f = linea[3] if es_msh and len(linea) > 3 else fsep
    out, fin = [], 0
    for mt in MARCADOR.finditer(linea):
        crudo = linea[:mt.start()]
        n = (crudo.count(f) + (1 if es_msh else 0)) if f else None
        out.append(linea[fin:mt.start()])
        for bs in _subruns(bytes.fromhex("".join(re.findall(r"<0x([0-9A-Fa-f]{2})>", mt.group(0))))):
            if bs[0] == 0x0A:                                           # [L1] el LF queda marcado: lo lee segmentos_ocultos
                txt, via = "<0x0A>", "lf"
            elif bs[0] < 0x20 or bs[0] == 0x7F:                         # [S10] un byte de control C0/DEL es ese carácter
                txt, via = chr(bs[0]), "control"
            elif bs[0] < 0x80:                                          # ASCII imprimible marcado: cable() no lo produce
                txt, via = "<0x%02X>" % bs[0], "literal"
            else:
                try:
                    txt, via = bs.decode("utf-8"), "utf-8"
                except UnicodeDecodeError:
                    txt, via = bs.decode("latin-1"), "latin-1"
            regs.append({"seg": linea[:3], "n": n, "bytes": bs.hex().upper(), "texto": txt, "via": via})
            out.append(txt)
        fin = mt.end()
    out.append(linea[fin:])
    return "".join(out), regs


class Msg:
    def __init__(self, segs, descodificados=None, marco=None, no_ascii=None):
        self.segs = segs
        self.descodificados = descodificados or []
        self.marco = marco                                       # [S31] número de marco MLLP
        self.no_ascii = no_ascii or []                           # [S38][S39] (seg, n) con caracteres > U+007F en el cable
        msh = segs[0]
        self.f = msh[3]                                          # §2.5: el carácter tras «MSH»
        enc = msh.split(self.f)[1] if len(msh.split(self.f)) > 1 else "^~\\&"
        self.c, self.r, self.e, self.s = (list(enc) + list("^~\\&"))[:4]

    def segmentos(self, nombre):
        return [s for s in self.segs if s.split(self.f)[0] == nombre]

    def campo(self, seg, n):
        p = seg.split(self.f)
        i = n - 1 if seg.startswith("MSH") else n
        return p[i] if 0 <= i < len(p) else ""

    def desescapa(self, x):
        """§2.7: \\F\\ \\S\\ \\T\\ \\R\\ \\E\\ y \\Xhh..\\; el resto se deja literal."""
        e = re.escape(self.e)

        def uno(m):
            k = m.group(1)
            tabla = {"F": self.f, "S": self.c, "T": self.s, "R": self.r, "E": self.e}
            if k in tabla:
                return tabla[k]
            if k.startswith("X") and re.fullmatch(r"X([0-9A-Fa-f]{2})+", k):
                try:
                    return bytes.fromhex(k[1:]).decode("utf-8")
                except ValueError:
                    return bytes.fromhex(k[1:]).decode("latin-1")          # [E2 §2.7.5] + [S9]
            return m.group(0)
        return re.sub(e + r"([^" + e + r"]*)" + e, uno, x)


MARCA = re.compile(r"<VT>|\x0b|<FS>|\x1c")


def _lineas(txt):
    return [s for s in (l.strip("\x0b\x1c").lstrip("\ufeff") for l in txt.split("\n")) if s.strip()]


def trama(texto):
    """[S31] Parte el cable en marcos MLLP (<VT>/0x0B abre, <FS>/0x1C cierra) -> {marcos, sin_msh, anomalias}.
    Cada marco: {n, lineas, msh, segmentos}. Sin <VT>, sin <FS>, marcadores repetidos y marcos vacíos se anotan [A-2]."""
    t = (texto or "").replace("<CR>", "\n").replace("\r", "\n")
    marcos, anom = [], []
    hay_marcas = bool(MARCA.search(t))
    cur = {"txt": "", "vt": False, "abierto": False}

    def cerrar(con_fs):
        if cur["txt"].strip():
            n = len(marcos) + 1
            marcos.append({"n": n, "lineas": _lineas(cur["txt"])})
            if not cur["vt"]:
                anom.append("marco %d sin <VT>" % n)
            if not con_fs:
                anom.append("marco %d sin <FS>" % n)
        elif con_fs:
            anom.append("marcador <FS> repetido (tras el marco %d)" % len(marcos))
    pos = 0
    for mt in MARCA.finditer(t):
        cur["txt"] += t[pos:mt.start()]
        pos = mt.end()
        if mt.group(0) in ("<VT>", "\x0b"):
            if cur["txt"].strip():
                cerrar(False)
            elif cur["abierto"] and cur["vt"]:
                anom.append("marcador <VT> repetido (marco %d)" % (len(marcos) + 1))
                continue
            cur = {"txt": "", "vt": True, "abierto": True}
        else:
            cerrar(True)
            cur = {"txt": "", "vt": False, "abierto": False}
    cur["txt"] += t[pos:]
    if cur["txt"].strip():
        cerrar(False)
    if not hay_marcas:
        anom = ["sin marcadores MLLP"]
    for mc in marcos:
        msh = next((l for l in mc["lineas"] if l.startswith("MSH") and len(l) > 8), None)
        sep = msh[3] if msh else "|"
        mc["msh"] = msh is not None
        mc["segmentos"] = [l.split(sep)[0] for l in mc["lineas"]]
        if msh is not None:
            antes = mc["lineas"].index(msh)
            if antes:
                anom.append("marco %d: %d líneas antes del MSH ignoradas" % (mc["n"], antes))
    return {"marcos": marcos, "sin_msh": [mc["n"] for mc in marcos if not mc["msh"]], "anomalias": anom}


def no_ascii(linea, fsep=None):
    """[S38][S39] Campos de la línea CRUDA (antes de descodificar: los <0xNN> son texto ASCII) con algún carácter
    > U+007F, es decir, UTF-8 válido en el cable -> [(seg, n)]; n como en descodificar (MSH: índice + 1)."""
    if not any(ord(ch) > 0x7f for ch in linea):
        return []
    es_msh = linea.startswith("MSH")
    f = linea[3] if es_msh and len(linea) > 3 else fsep
    if not f:
        return [(linea[:3], None)]
    return [(linea[:3], i + (1 if es_msh else 0)) for i, p in enumerate(linea.split(f)) if any(ord(ch) > 0x7f for ch in p)]


def mensajes(texto):
    """[S31] Mensajes del cable por marcos: cada MSH abre un mensaje dentro de su marco; las líneas siguientes del
    mismo marco se le añaden; un marco sin MSH no produce mensaje. [S9] bytes <0xNN> decodificados."""
    out = []
    for mc in trama(texto)["marcos"]:
        cur = None
        for s in mc["lineas"]:
            fsep = cur[0][0][3] if cur and len(cur[0][0]) > 3 else None
            na = no_ascii(s, fsep)
            s, rg = descodificar(s, fsep)
            if s.startswith("MSH") and len(s) > 8:
                cur = ([s], list(rg), mc["n"], list(na))
                out.append(cur)
            elif cur is not None:
                cur[0].append(s)
                cur[1].extend(rg)
                cur[3].extend(na)
    return [Msg(segs, regs, n, na) for segs, regs, n, na in out]


# [E2 §2.5.4] el terminador de segmento es CR: otro byte de control (el marcador <0xNN> de la evidencia con NN en
# 00-1F/7F, o el carácter crudo) no termina segmento
CONTROL_NO_CR = r"(?:<0x(?:0[0-9A-Fa-f]|1[0-9A-Fa-f]|7[Ff])>|[\x00-\x09\x0b\x0c\x0e-\x1f\x7f])"


def segmentos_ocultos(segs, f):
    """[E2 §2.5.4] Segmentos que una línea arrastra tras un byte de control que no es CR, seguido de un nombre de
    segmento [A-Z][A-Z0-9]{2} y del separador de campo o del fin de línea -> [(nombre, control visible)], en orden.
    El receptor parte por CR: no los lee como segmentos. Los marcadores se devuelven tal cual; los crudos, como \\xNN.
    Falso positivo declarado: un control dentro de un campo seguido de tres mayúsculas o dígitos y el separador."""
    pat = re.compile("(" + CONTROL_NO_CR + "+)([A-Z][A-Z0-9]{2})(?=" + re.escape(f) + "|$)")
    out = []
    for s in segs:
        for mt in pat.finditer(s):
            vis = re.sub(r"[\x00-\x1f\x7f]", lambda c: "\\x%02X" % ord(c.group(0)), mt.group(1))
            out.append((mt.group(2), vis))
    return out


# ---------------------------------------------------------------------------- fechas [E] TS / DTM
# ---------------------------------------------------------------------------- DTM: UNA sola gramática (N1, 5-oct)
# La usan mapeador_oru (fecha_hora, instante, valor_valido), acuse_referencia._ts (P5 de todos los PE) y fecha() (PID-7).
DTM_RE = re.compile(r"^(\d{4})(\d{2})?(\d{2})?(\d{2})?(\d{2})?(\d{2})?(\.\d{1,4})?([+-]\d{4})?$")   # [E2A §2.A.22] ch02a.md:1751-1790


def partes_dtm(v):
    m = DTM_RE.match(v or "")
    if not m:
        return None, "%r no es un DTM de v2.5" % v
    y, mo, d, hh, mi, ss, fr, z = m.groups()
    if mo and not 1 <= int(mo) <= 12:
        return None, "%r: mes imposible" % v
    if d and not 1 <= int(d) <= calendar.monthrange(int(y), int(mo))[1]:
        return None, "%r: día imposible" % v
    if hh and int(hh) > 23 or mi and int(mi) > 59 or ss and int(ss) > 59:
        return None, "%r: hora imposible" % v
    if fr and not ss:                                                 # A2: [E2A §2.A.22] «SS[.S[S[S[S]]]]», fracción solo tras segundos
        return None, "%r: fracción sin segundos" % v
    if z and not zona_valida(z):
        return None, "%r: zona imposible" % v
    return (y, mo, d, hh, mi, ss, fr, z), None


def zona_valida(z):
    """A3: ±HHMM representable como zona de un dateTime FHIR R4 (datatypes.html: «(Z|(\\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))»):
    horas 00-13 con minutos 00-59, o 14:00 exacto."""
    hh, mm = int(z[1:3]), int(z[3:5])
    return (hh <= 13 and mm <= 59) or (hh == 14 and mm == 0)


def digitos_dtm(v):
    """N2b: los dígitos de fecha y hora de un DTM, sin fracción ni zona («202601011200+0100» -> «202601011200»)."""
    return re.match(r"\d*", v or "").group(0)


def posterior_a(v, ref):
    """[S18] (N2/N8): ¿el DTM v es posterior al DTM ref? Hasta la precisión común, con la hora si ambos la traen; si las zonas
    no coinciden (o solo uno la trae), solo la fecha. La usan acuse_referencia (P5f) y fecha() (PID-7)."""
    d, r = digitos_dtm(v), digitos_dtm(ref)
    zona = lambda x: (re.search(r"[+-]\d{4}$", x or "") or [""])[0]
    if zona(v) != zona(ref):
        d, r = d[:8], r[:8]
    k = min(len(d), len(r))
    return k > 0 and d[:k] > r[:k]


def fecha(ts, ref=None, c="^"):
    """-> (valor normalizado o None, problema o None). DTM con la gramática única (N1: hora, minutos, segundos, fracción y
    zona validados; componente 1 según MSH-2). La precisión reducida es válida y se conserva (ISO 8601, como pide el mapeo
    oficial para birthDate). ref = dígitos de MSH-7 sin fracción ni zona (N2b); se compara con la precisión común (N2)."""
    v = ts.split(c)[0]
    if not v.strip():                                             # solo blancos: vacío
        return "", None                                           # [L23] blancos en los bordes: inválido, como P5 (Jev, 6-oct)
    p, prob = partes_dtm(v)
    if prob:
        return None, ("PID-7 %r no es un TS de v2.5" % v) if "no es un DTM" in prob else "PID-7 " + prob
    y, mo, d = p[0], p[1], p[2]
    iso = y + ("-" + mo if mo else "") + ("-" + d if d else "")
    if ref and posterior_a(v, ref):                               # N8: ref = MSH-7 (componente 1) tal cual
        return None, "PID-7 %r: posterior a la fecha del mensaje (MSH-7)" % v
    return iso, None


# ---------------------------------------------------------------------------- el nombre [C] [D] [S30]-[S37]
# [S33][S37] blanco = U+0020, categoría Zs y U+2028/U+2029 (Zl/Zp). Cc (tabulador…) es S10; Cf (anchura cero) es S7.
BLANCO = frozenset(chr(c) for c in [0x20, 0xA0, 0x1680] + list(range(0x2000, 0x200B)) + [0x202F, 0x205F, 0x3000, 0x2028, 0x2029])
MAX_PARTES = 8


def partes_nombre(m, pid):
    """[C] PID-5: la repetición con PID-5.7 = L; si no, la primera con apellido o nombre; todas [V].
    -> (partes de FamilyName = subcomponentes de PID-5.1, partes de GivenName = PID-5.2 y PID-5.3), desescapadas y no vacías."""
    reps = [r.split(m.c) for r in m.campo(pid, 5).split(m.r)][:MAXREP] if pid else []
    nom = next((c for c in reps if len(c) > 6 and c[6] == "L"), None) or \
        next((c for c in reps if (c[0] or (len(c) > 1 and c[1]))), None) or [""]
    fam = [p for p in (m.desescapa(s) for s in nom[0].split(m.s) if s) if p]
    giv = [p for p in (m.desescapa(s) for s in nom[1:3] if s) if p]
    return fam, giv


def nombre(m, pid, f=lambda s: s):
    """FamilyName = partes unidas por espacio [D]; GivenName = PID-5.2 y PID-5.3 unidas [C]. f se aplica a cada parte."""
    fam, giv = partes_nombre(m, pid)
    return (" ".join(p for p in (f(x) for x in fam) if p), " ".join(p for p in (f(x) for x in giv) if p))


def _tiras(p, B):
    """-> (longitud de la tira inicial, de la final) de blancos B de una parte; una parte de solo blancos es toda inicial."""
    i = len(p) - len(p.lstrip("".join(B)))
    if i == len(p):
        return i, 0
    return i, len(p) - len(p.rstrip("".join(B)))


def recortes(partes, B=BLANCO):
    """[S30][S32][S34] Valores guardados tolerados: en cada parte se puede quitar entera su tira inicial y/o final de blancos
    (una parte que queda vacía se omite con su espacio de unión). -> {valor: info}. Invariante: solo se quitan blancos."""
    raw = " ".join(partes)
    if len(partes) > MAX_PARTES:                           # límite declarado: solo las variantes del valor entero
        partes = [raw]
    inicios, pos = [], 0
    for p in partes:
        inicios.append(pos)
        pos += len(p) + 1
    lead = len(raw) - len(raw.lstrip("".join(B)))
    trail_ini = len(raw.rstrip("".join(B)))
    opciones = []
    for p in partes:
        li, lf = _tiras(p, B)
        ops = [(0, 0)]
        if lf:
            ops.append((0, lf))
        if li:
            ops.append((li, 0))
        if li and lf:
            ops.append((li, lf))
        opciones.append(ops)
    out = {}
    for combo in itertools.product(*opciones):
        kept, piezas, ult = set(), [], None
        for k, (p, (qi, qf)) in enumerate(zip(partes, combo)):
            s0 = inicios[k]
            dentro = range(s0 + qi, s0 + len(p) - qf)
            if not len(dentro):
                continue
            if ult is not None:
                kept.add(inicios[ult] + len(partes[ult]))             # el espacio de unión tras la parte anterior conservada
            kept.update(dentro)
            piezas.append(p[qi:len(p) - qf])
            ult = k
        v = " ".join(piezas)
        if v in out:
            continue
        quit = [q for q in range(len(raw)) if q not in kept]
        ini = sum(1 for q in quit if q < lead)
        fin = sum(1 for q in quit if q >= lead and q >= trail_ini)
        out[v] = {"ini": ini, "fin": fin, "int": len(quit) - ini - fin,
                  "unicode": sorted({raw[q] for q in quit if raw[q] != " "})}
    return out


def blancos(esp, obs, partes):
    """-> None | {decisiones, ini, fin, int, unicode}: qué normalización de blancos explica obs frente a esp."""
    if not isinstance(esp, str) or not isinstance(obs, str) or esp == obs:
        return None
    info = recortes(partes).get(obs)
    if info is None:
        return None
    dec = ([("S30")] if info["ini"] else []) + (["S32"] if info["fin"] else []) + (["S33"] if info["unicode"] else []) + \
        (["S34"] if info["int"] else [])
    return dict(info, decisiones=dec)


def _texto_blancos(b, campo, e, o):
    piezas = []
    for n, uno, varios in ((b["ini"], "el blanco inicial", "los %d blancos iniciales"),
                           (b["fin"], "el blanco final", "los %d blancos finales"),
                           (b["int"], "el blanco interior en el borde de una parte", "los %d blancos interiores en los bordes de sus partes")):
        if n:
            piezas.append(uno if n == 1 else varios % n)
    desc = piezas[0] if len(piezas) == 1 else ", ".join(piezas[:-1]) + " y " + piezas[-1]
    if b["unicode"]:
        desc += " (blancos Unicode: %s)" % ", ".join("U+%04X" % ord(c) for c in b["unicode"])
    return "%s %s: guardado sin %s (%r -> %r) (L19)" % ("".join("[%s]" % d for d in b["decisiones"]), campo, desc, e, o)


# ---------------------------------------------------------------------------- el canónico esperado [C]
def esperado(m):
    """-> (canónico esperado, lista de valores imposibles aceptados, avisos de estructura)."""
    msh = m.segs[0]
    pids = m.segmentos("PID")
    imposibles, estructura, tolerancias = [], [], []
    if len(pids) != 1:                                           # [E] ADT_A01: PID [1..1]; es el que se consume
        estructura.append("ADT_A01 lleva exactamente un PID y hay %d" % len(pids))
    pid = pids[0] if pids else ""
    x = {}
    # [C] Identifier <- PID-3: la repetición con PID-3.5 = MR; si ninguna, la primera no vacía; todas [V]
    reps = [r for r in m.campo(pid, 3).split(m.r)][:MAXREP] if pid else []
    comp = [r.split(m.c) for r in reps]
    elegida = next((c for c in comp if len(c) > 4 and c[4] == "MR"), None) or next((c for c in comp if c[0]), None)
    x["Identifier"] = m.desescapa(elegida[0]) if elegida else ""
    x["FamilyName"], x["GivenName"] = nombre(m, pid)
    # [C]+[M] Gender <- PID-8 por la tabla 0001
    g = m.desescapa(m.campo(pid, 8)) if pid else ""
    if g == "":
        x["Gender"] = ("", "unknown")        # [C] ausente -> el valor que en destino significa ausente
    elif g in MAPEO_0001:
        x["Gender"] = MAPEO_0001[g]
    elif g.upper() in MAPEO_0001:                                 # [V] minúscula: tolerancia, no fallo
        x["Gender"] = MAPEO_0001[g.upper()]
        tolerancias.append("PID-8 %r en minúscula: se tolera como %r" % (g, g.upper()))
    elif posterior_a_25(m.campo(msh, 12).split(m.c)[0]):         # [S22] puede ser legal en su versión: sin destino en [M]
        x["Gender"] = ADMINISTRATIVE_GENDER + ("",)
        tolerancias.append("[S22] PID-8 %r fuera de la 0001 de v2.5 en un mensaje %s: sin destino en el mapeo oficial; "
                           "solo se comprueba que Gender sea un código de AdministrativeGender" % (g, m.campo(msh, 12).split(m.c)[0]))
    else:
        x["Gender"] = None
        imposibles.append("PID-8 %r no está en la tabla 0001 y se aceptó" % g)            # [C] valor que no puede ser cierto
    # [C] BirthDate <- PID-7 normalizado; [E] TS
    b, prob = fecha(m.campo(pid, 7) if pid else "", m.campo(msh, 7).split(m.c)[0] or None, m.c)   # N1/N2b/N8
    x["BirthDate"] = b
    if prob:
        imposibles.append(prob + " y se aceptó")
    # [C] cabecera
    x["MsgControlId"] = m.campo(msh, 10)
    x["SendingApp"] = m.campo(msh, 3).split(m.c)[0]
    x["SendingFacility"] = m.campo(msh, 4).split(m.c)[0]
    t9 = m.campo(msh, 9).split(m.c)
    x["MsgEvent"] = t9[1] if len(t9) > 1 else ""
    x["ProcessingId"] = m.campo(msh, 11).split(m.c)[0]
    if t9[:2] != ["ADT", "A01"]:                                  # [C] solo ADT^A01; lo demás va a Rechazo
        estructura.append("MSH-9 %r no es ADT^A01 y se aceptó" % m.campo(msh, 9))
    # [C] Truncado: algún campo consumido excede su longitud máxima [E]; el perfil del sitio puede fijar otra (H10).
    # [E2 §2.5.3.2] la longitud es de cada repetición, no del campo entero (como acuse_referencia._truncar; A-pre, 6-oct)
    largos = [(s, n) for (s, n), mx in long_max().items()
              if any(len(r) > mx for r in (m.campo(msh if s == "MSH" else pid, n) if (s == "MSH" or pid) else "").split(m.r))]
    x["Truncado"] = 1 if largos else 0
    # [S10] un carácter de control en un campo consumido: valor que no puede ser cierto; el campo no se compara
    crudos = {"PID-3": [x.get("Identifier") or ""], "PID-5": [x.get("FamilyName") or "", x.get("GivenName") or ""],
              "PID-7": [m.campo(pid, 7) if pid else ""], "PID-8": [g], "MSH-10": [x["MsgControlId"]],
              "MSH-3": [x["SendingApp"]], "MSH-4": [x["SendingFacility"]], "MSH-9": [m.campo(msh, 9)],
              "MSH-11": [x["ProcessingId"]]}
    campos_de = {"PID-3": ["Identifier"], "PID-5": ["FamilyName", "GivenName"], "PID-7": ["BirthDate"],
                 "PID-8": ["Gender"], "MSH-10": ["MsgControlId"], "MSH-3": ["SendingApp"], "MSH-4": ["SendingFacility"],
                 "MSH-9": ["MsgEvent"], "MSH-11": ["ProcessingId"]}
    for donde, vals in crudos.items():
        c = next((control_en(v) for v in vals if isinstance(v, str) and control_en(v) is not None), None)
        if c is not None:
            imposibles.append("%s contiene un carácter de control U+%04X y se aceptó" % (donde, c))
            for campo in campos_de[donde]:
                x[campo] = None
    return x, imposibles, estructura, tolerancias


def _igual(esp, obs):
    if isinstance(esp, tuple):
        return obs in esp
    return esp == obs


def comparar(texto_mensaje, canonicos, ack):
    """-> lista de discrepancias (cadenas), o None si está fuera de alcance (no aceptado o sin canónico)."""
    r = revisar(texto_mensaje, canonicos, ack)
    return None if r is None else r[0]


def revisar(texto_mensaje, canonicos, ack):
    """-> (discrepancias, tolerancias), o None si está fuera de alcance. Las tolerancias no son fallos."""
    ms = mensajes(texto_mensaje)
    am = mensajes(ack or "")
    msa = [s for s in (am[0].segmentos("MSA") if am else [])]
    if not ms or not canonicos or not msa or am[0].campo(msa[0], 1) != "AA":
        return None
    out, tol = [], []
    for k, m in enumerate(ms):
        pre = "mensaje %d: " % (k + 1) if len(ms) > 1 else ""
        a_k = next((a for a in am if a.segmentos("MSA") and a.campo(a.segmentos("MSA")[0], 2) == m.campo(m.segs[0], 10)),
                   am[k] if k < len(am) else None)                    # D10: el ACK de ESTE mensaje (por MSA-2, o el posicional)
        if len(ms) > 1 and (a_k is None or not a_k.segmentos("MSA") or a_k.campo(a_k.segmentos("MSA")[0], 1) != "AA"):
            tol.append("[L24] " + pre + "su acuse no es AA: su canónico no se compara (fuera de alcance)")
            continue
        esp, imp, est, tl = esperado(m)
        out += [pre + i for i in imp] + [pre + e for e in est]
        tol += [pre + t for t in tl]
        can = canonicos[k] if k < len(canonicos) else None
        if can is None:
            out.append(pre + "no hay canónico para este mensaje")
            continue
        for c in CAMPOS:
            e, o = esp.get(c), can.get(c)
            if c == "Truncado":
                o = int(o) if str(o).strip().lstrip("-").isdigit() else o
            if e is None:
                continue                                          # ya contado como imposible
            if c in ("FamilyName", "GivenName"):                              # [S30][S32][S33][S34][S37]
                pids = m.segmentos("PID")
                b = blancos(e, o, partes_nombre(m, pids[0] if pids else "")[0 if c == "FamilyName" else 1])
                if b:
                    tol.append(pre + _texto_blancos(b, c, e, o))
                    continue
            if not _igual(e, "" if o is None else o):
                out.append(pre + "%s: esperado %r, observado %r" % (c, e, o))
    # [E2 §2.9.2.2] MSA-2 devuelve el MSH-10 acusado: CADA mensaje del cable debe tener su eco (D9)
    ecos = [a.campo(z, 2) for a in am for z in a.segmentos("MSA")]
    for k, m in enumerate(ms):
        ctl = m.campo(m.segs[0], 10)
        if ctl not in ecos:
            a = am[k] if k < len(am) else None
            msa2 = a.campo(a.segmentos("MSA")[0], 2) if a is not None and a.segmentos("MSA") else None
            out.append(("mensaje %d: " % (k + 1) if len(ms) > 1 else "") + "MSA-2 %r no devuelve el MSH-10 %r" % (msa2, ctl))
    return out, tol


# ---------------------------------------------------------------------------- autoprueba
def autoprueba():
    mal = []

    def mira(nombre, obtenido, esperado_):
        ok = obtenido == esperado_
        print(("  ok  " if ok else "  MAL ") + nombre + ("" if ok else ": %r != %r" % (obtenido, esperado_)))
        if not ok:
            mal.append(nombre)

    def msg(pid3="X1^^^H^MR", pid5="Pérez^Ana^Luz^^^^L", pid7="19800101", pid8="F", msh9="ADT^A01^ADT_A01", msh10="M1", extra="",
            ver="2.5"):
        return ("<VT>MSH|^~\\&|APP|FAC|R|RF|20230101120000||%s|%s|P|%s\nEVN|A01|20230101\n"
                "PID|1||%s||%s||%s|%s\n%sPV1|1|I\n<FS>" % (msh9, msh10, ver, pid3, pid5, pid7, pid8, extra))

    bueno_can = {"Identifier": "X1", "FamilyName": "Pérez", "GivenName": "Ana Luz", "Gender": "female",
                 "BirthDate": "1980-01-01", "MsgControlId": "M1", "SendingApp": "APP", "SendingFacility": "FAC",
                 "MsgEvent": "A01", "ProcessingId": "P", "Truncado": 0}
    ack = "MSH|^~\\&|L|L|APP|FAC|t||ACK^A01^ACK|M1|P|2.5\nMSA|AA|M1"

    def c(m, **k):
        return comparar(m, [dict(bueno_can, **k)], ack)

    mira("caso base: sin discrepancias", c(msg()), [])
    mira("fuera de alcance: AR", comparar(msg(), [bueno_can], ack.replace("MSA|AA", "MSA|AR")), None)
    mira("fuera de alcance: sin canónico", comparar(msg(), [], ack), None)
    mira("escape \\S\\ sin resolver en el canónico: se delata",
         bool(c(msg(pid5="Ferr\\S\\Soler^Ana^Luz^^^^L"), FamilyName="Ferr\\S\\Soler")), True)
    mira("escape \\S\\ resuelto: nada", c(msg(pid5="Ferr\\S\\Soler^Ana^Luz^^^^L"), FamilyName="Ferr^Soler"), [])
    mira("subcomponentes unidos por espacio: nada", c(msg(pid5="Ferrer&Soler^Ana^Luz^^^^L"), FamilyName="Ferrer Soler"), [])
    mira("acento perdido: se delata", bool(c(msg(pid5="Muñoz^Ana^Luz^^^^L"), FamilyName="Mu?oz")), True)
    mira("MR en la repetición 2: se elige", c(msg(pid3="P1^^^H^PI~X1^^^H^MR")), [])
    once = "~".join("P%d^^^H^PI" % i for i in range(10)) + "~X1^^^H^MR"
    mira("MR en la 11 [V]: se mira; si el canónico toma la primera, se delata",
         (bool(c(msg(pid3=once), Identifier="P0")), c(msg(pid3=once), Identifier="X1")), (True, []))
    lonce = "~".join("Alias%d^Otro^^^^^A" % i for i in range(10)) + "~Pérez^Ana^Luz^^^^L"
    mira("nombre L en la 11 [V]: se mira", bool(c(msg(pid5=lonce), FamilyName="Alias0", GivenName="Otro")), True)
    mira("minúscula [V]: sin discrepancia y anotada como tolerancia",
         revisar(msg(pid8="m"), [dict(bueno_can, Gender="male")], ack),
         ([], ["PID-8 'm' en minúscula: se tolera como 'M'"]))
    mira("minúscula mal traducida: sí se delata", bool(c(msg(pid8="f"), Gender="unknown")), True)
    mira("identificador equivocado: se delata", bool(c(msg(pid3="P1^^^H^PI~X1^^^H^MR"), Identifier="P1")), True)
    mira("nombre legal en la segunda repetición: se elige",
         c(msg(pid5="Alias^Otro^^^^^A~Pérez^Ana^Luz^^^^L")), [])
    mira("sexo X: imposible aceptado", any("tabla 0001" in d for d in c(msg(pid8="X"), Gender="unknown")), True)
    mira("sexo U -> unknown: nada", c(msg(pid8="U"), Gender="unknown"), [])
    mira("sexo N -> other: nada", c(msg(pid8="N"), Gender="other"), [])
    mira("sexo vacío -> unknown o vacío: nada", (c(msg(pid8=""), Gender="unknown"), c(msg(pid8=""), Gender="")), ([], []))
    mira("sexo M -> unknown: se delata", bool(c(msg(pid8="M"), Gender="unknown")), True)
    mira("fecha corta 1992 conservada: nada; perdida: se delata",
         (c(msg(pid7="1992"), BirthDate="1992"), bool(c(msg(pid7="1992"), BirthDate=""))), ([], True))
    mira("fecha ISO con guiones: imposible", any("no es un TS" in d for d in c(msg(pid7="1980-01-01"))), True)
    mira("29 de febrero no bisiesto: imposible", any("día imposible" in d for d in c(msg(pid7="20230229"), BirthDate="")), True)
    mira("29 de febrero bisiesto: nada", c(msg(pid7="20200229"), BirthDate="2020-02-29"), [])
    mira("fecha futura: imposible", any("posterior" in d for d in c(msg(pid7="20300101"), BirthDate="2030-01-01")), True)
    mira("A04 aceptado: se delata", any("no es ADT^A01" in d for d in c(msg(msh9="ADT^A04^ADT_A01"), MsgEvent="A04")), True)
    mira("PID duplicado: se delata", any("exactamente un PID" in d for d in c(msg(extra="PID|1||X2^^^H^MR||Otro^Uno||19900101|M\n"))), True)
    mira("MSA-2 que no hace eco: se delata",
         any("MSA-2" in d for d in comparar(msg(), [bueno_can], ack.replace("MSA|AA|M1", "MSA|AA|SINID1"))), True)
    mira("MSH-10 largo (21) -> Truncado esperado 1", bool(c(msg(msh10="M" * 21), MsgControlId="M" * 21)), True)
    # --- gancho del perfil del sitio (LONG_PERFIL): sin gancho o con {} es v2.5; instalado, manda su longitud

    def c10(n, truncado):                                       # MSH-10 de n caracteres con MSA-2 íntegro
        return comparar(msg(msh10="M" * n), [dict(bueno_can, MsgControlId="M" * n, Truncado=truncado)],
                        ack.replace("MSA|AA|M1", "MSA|AA|" + "M" * n))

    global LONG_PERFIL
    antes = LONG_PERFIL
    try:
        LONG_PERFIL = lambda: {}
        mira("M-PERFIL-0 gancho vacío (perfil lab): LONG_MAX tal cual; 20 no trunca, 21 sí",
             (long_max() is LONG_MAX, c10(20, 0), c10(21, 1), c10(21, 0)), (True, [], [], ["Truncado: esperado 1, observado 0"]))
        LONG_PERFIL = lambda: {("MSH", 10): 199}
        mira("M-PERFIL-1 gancho con MSH-10 199: 21 y 199 no truncan, 200 sí; el resto de LONG_MAX no cambia",
             (c10(21, 0), c10(199, 0), c10(200, 1), c10(21, 1), {k: v for k, v in long_max().items() if k != ("MSH", 10)}),
             ([], [], [], ["Truncado: esperado 0, observado 1"], {k: v for k, v in LONG_MAX.items() if k != ("MSH", 10)}))
    finally:
        LONG_PERFIL = antes
    mira("M-PERFIL-2 gancho restaurado: 21 trunca", c10(21, 0), ["Truncado: esperado 1, observado 0"])
    mira("BOM delante de MSH: se lee", c(msg().replace("<VT>MSH", "<VT>﻿MSH")), [])
    mira("separadores alternativos: se leen",
         comparar(msg().replace("|", "#").replace("^", "$").replace("MSH#$~\\&", "MSH#$~\\&"), [bueno_can],
                  ack) is not None, True)
    # --- S7, S9, S10 (diseno-s6-s16-fable.md)
    zw = "Pérez​"
    mira("M-S7 invisible conservado: nada", c(msg(pid5=zw + "^Ana^Luz^^^^L"), FamilyName=zw), [])
    mira("M-S7c invisible perdido: se delata", bool(c(msg(pid5=zw + "^Ana^Luz^^^^L"), FamilyName="Pérez")), True)
    mf = msg(pid5="Mu<0xF1>oz^Ana^Luz^^^^L")
    mira("M-S9-1 byte latin-1 decodificado: Muñoz esperado", c(mf, FamilyName="Muñoz"), [])
    mira("M-S9-2 guardado con ?: se delata", c(mf, FamilyName="Mu?oz"), ["FamilyName: esperado 'Muñoz', observado 'Mu?oz'"])
    mira("M-S9-3 el canónico no se decodifica", bool(c(mf, FamilyName="Mu<0xF1>oz")), True)
    mira("M-S9-4 \\XF1\\ con latin-1 de reserva", c(msg(pid5="Mu\\XF1\\oz^Ana^Luz^^^^L"), FamilyName="Muñoz"), [])
    m5 = mensajes(msg(pid5="Mu<0xC3><0xB1>oz^Ana^Luz^^^^L"))[0]
    mira("M-S9-5 secuencia UTF-8 válida marcada: vía utf-8", (c(msg(pid5="Mu<0xC3><0xB1>oz^Ana^Luz^^^^L"), FamilyName="Muñoz"),
         m5.descodificados[0]["via"], m5.descodificados[0]["seg"], m5.descodificados[0]["n"]), ([], "utf-8", "PID", 5))
    m6 = mensajes(msg(pid5="Mu<0x41>oz^Ana^Luz^^^^L"))[0]
    mira("M-S9-6 byte ASCII marcado: literal", (esperado(m6)[0]["FamilyName"], m6.descodificados[0]["via"]), ("Mu<0x41>oz", "literal"))
    r = revisar(msg(pid5="Pe\x01rez^Ana^Luz^^^^L"), [dict(bueno_can, FamilyName="Perez")], ack)[0]
    mira("M-S10 carácter de control en PID-5: imposible y sin comparar el campo",
         (any("PID-5 contiene un carácter de control U+0001" in d for d in r), any(d.startswith("FamilyName") for d in r)), (True, False))
    r = revisar(msg(pid5="<0xC0><0x80>Señor^Ana^Luz^^^^L"), [dict(bueno_can, FamilyName="Señor")], ack)[0]
    mira("M-S10b NUL overlong (C0 80 -> latin-1 -> U+0080): imposible", any("U+0080" in d for d in r), True)
    mc = mensajes(msg(pid5="Pe<0x01>rez^Ana^Luz^^^^L"))[0]
    r = revisar(msg(pid5="Pe<0x01>rez^Ana^Luz^^^^L"), [dict(bueno_can, FamilyName="Perez")], ack)[0]
    mira("M-S10c <0x01> marcado: imposible U+0001, sin comparar el campo, vía control",
         (any("U+0001" in d for d in r), any(d.startswith("FamilyName") for d in r), mc.descodificados[0]["via"],
          mc.descodificados[0]["texto"]), (True, False, "control", "\x01"))
    md = mensajes(msg(pid5="Pe<0x0A>rez^Ana^Luz^^^^L"))[0]
    r = revisar(msg(pid5="Pe<0x0A>rez^Ana^Luz^^^^L"), [dict(bueno_can, FamilyName="Perez")], ack)[0]
    mira("M-S10d <0x0A> marcado: imposible U+000A, vía lf", (any("U+000A" in d for d in r), md.descodificados[0]["via"]),
         (True, "lf"))
    m7 = mensajes(msg(pid5="Mu<0x01><0xF1>oz^Ana^Luz^^^^L"))[0]
    mira("M-S9-7 run mixto control + latin-1: dos registros y FamilyName imposible",
         ([z["via"] for z in m7.descodificados], esperado(m7)[0]["FamilyName"]), (["control", "latin-1"], None))
    # --- S19, S22 (diseno-s19-s21-fable.md)
    mira("M-S19-1 version_id", [version_id(v) for v in ("2.5", "2.5.1", "2.10", "2", "v2.6", "2.6 ", "02.6", "", "2.0D")],
         [(2, 5, None), (2, 5, 1), (2, 10, None), None, None, None, None, None, None])
    mira("M-S22-0 posterior_a_25", [posterior_a_25(v) for v in ("2.5", "2.5.1", "2.6", "2.4", "2.10", "")],
         [False, True, True, False, True, False])
    r = revisar(msg(pid8="X", ver="2.6"), [dict(bueno_can, Gender="unknown")], ack)
    mira("M-S22-1 2.6 + PID-8 X + unknown: sin discrepancia, tolerancia S22",
         (r[0], len(r[1]), r[1][0].startswith("[S22] PID-8 'X'")), ([], 1, True))
    mira("M-S22-2 2.6 + PID-8 X + other: nada", c(msg(pid8="X", ver="2.6"), Gender="other"), [])
    mira("M-S22-3 2.6 + PID-8 X + Gender X: fuera del value set", c(msg(pid8="X", ver="2.6"), Gender="X"),
         ["Gender: esperado ('male', 'female', 'other', 'unknown', ''), observado 'X'"])
    mira("M-S22-4 2.5 + PID-8 X: imposible (como hoy)", any("tabla 0001" in d for d in c(msg(pid8="X"), Gender="unknown")), True)
    mira("M-S22-5 2.4 + PID-8 X: imposible", any("tabla 0001" in d for d in c(msg(pid8="X", ver="2.4"), Gender="unknown")), True)
    # --- S30 (diseno-s30-fable.md)
    mira("M-S30-1 5 blancos delante quitados: tolerancia S30", revisar(msg(pid5="     Pérez^Ana^Luz^^^^L"), [bueno_can], ack),
         ([], ["[S30] FamilyName: guardado sin los 5 blancos iniciales ('     Pérez' -> 'Pérez') (L19)"]))
    mira("M-S30-1c blancos conservados: nada", revisar(msg(pid5="     Pérez^Ana^Luz^^^^L"), [dict(bueno_can, FamilyName="     Pérez")], ack),
         ([], []))
    mira("M-S30-2 letra recortada: discrepancia", c(msg(pid5="     Pérez^Ana^Luz^^^^L"), FamilyName="érez"),
         ["FamilyName: esperado '     Pérez', observado 'érez'"])
    mira("M-S30-2b guardado vacío: discrepancia", c(msg(pid5="     Pérez^Ana^Luz^^^^L"), FamilyName=""),
         ["FamilyName: esperado '     Pérez', observado ''"])
    mira("M-S30-3 blanco del medio quitado: discrepancia", c(msg(), GivenName="AnaLuz"), ["GivenName: esperado 'Ana Luz', observado 'AnaLuz'"])
    mira("M-S30-4 GivenName con 2 blancos delante", revisar(msg(pid5="Pérez^  Ana^Luz^^^^L"), [bueno_can], ack),
         ([], ["[S30] GivenName: guardado sin los 2 blancos iniciales ('  Ana Luz' -> 'Ana Luz') (L19)"]))
    mira("M-S30-5/M-S32-1 finales [S32]", revisar(msg(pid5="Pérez   ^Ana^Luz^^^^L"), [bueno_can], ack),
         ([], ["[S32] FamilyName: guardado sin los 3 blancos finales ('Pérez   ' -> 'Pérez') (L19)"]))
    mira("M-S30-6/M-S33-1 U+00A0 inicial [S30][S33]", revisar(msg(pid5="\u00a0Pérez^Ana^Luz^^^^L"), [bueno_can], ack),
         ([], ["[S30][S33] FamilyName: guardado sin el blanco inicial (blancos Unicode: U+00A0) ('\\xa0Pérez' -> 'Pérez') (L19)"]))
    mira("M-S30-7/M-S34-1 borde de PID-5.3 [S34]", revisar(msg(pid5="Pérez^Ana^ Luz^^^^L"), [bueno_can], ack),
         ([], ["[S34] GivenName: guardado sin el blanco interior en el borde de una parte ('Ana  Luz' -> 'Ana Luz') (L19)"]))
    mira("M-S30-7c PID-5.3 con blanco guardado tal cual: nada", c(msg(pid5="Pérez^Ana^ Luz^^^^L"), GivenName="Ana  Luz"), [])
    mira("M-S30-8 subcomponentes FN con blancos delante", revisar(msg(pid5="  Ferrer&Soler^Ana^Luz^^^^L"),
         [dict(bueno_can, FamilyName="Ferrer Soler")], ack),
         ([], ["[S30] FamilyName: guardado sin los 2 blancos iniciales ('  Ferrer Soler' -> 'Ferrer Soler') (L19)"]))
    mx = msg(pid5="\\X20\\Pérez^Ana^Luz^^^^L")
    mira("M-S30-9 S8: \\X20\\ resuelto y quitado -> S30; tal cual -> nada; sin resolver -> discrepancia",
         (revisar(mx, [bueno_can], ack)[0], len(revisar(mx, [bueno_can], ack)[1]), c(mx, FamilyName=" Pérez"), len(c(mx, FamilyName="\\X20\\Pérez"))),
         ([], 1, [], 1))
    mv = msg(pid5="     ^^^^^^L")
    mira("M-S30-10 solo blancos y XPN.7: S30 al guardar vacío; tal cual nada",
         (revisar(mv, [dict(bueno_can, FamilyName="", GivenName="")], ack), revisar(mv, [dict(bueno_can, FamilyName="     ", GivenName="")], ack)),
         (([], ["[S30] FamilyName: guardado sin los 5 blancos iniciales ('     ' -> '') (L19)"]), ([], [])))
    r = revisar(msg(pid5="\tPérez^Ana^Luz^^^^L"), [bueno_can], ack)
    mira("M-S30-11 S10 manda sobre S30", (any("U+0009" in d for d in r[0]), any(d.startswith("FamilyName") for d in r[0]), r[1]), (True, False, []))
    mira("M-S34-11 recortes", (set(recortes(["  Ferrer", "Soler "])), set(recortes(["Ana", " Luz"])), set(recortes(["   "]))),
         ({"  Ferrer Soler ", "Ferrer Soler ", "  Ferrer Soler", "Ferrer Soler"}, {"Ana  Luz", "Ana Luz"}, {"   ", ""}))
    mira("M-S32-2 iniciales y finales", revisar(msg(pid5="  Pérez   ^Ana^Luz^^^^L"), [bueno_can], ack),
         ([], ["[S30][S32] FamilyName: guardado sin los 2 blancos iniciales y los 3 blancos finales ('  Pérez   ' -> 'Pérez') (L19)"]))
    mira("M-S32-2b solo iniciales quitados", revisar(msg(pid5="  Pérez   ^Ana^Luz^^^^L"), [dict(bueno_can, FamilyName="Pérez   ")], ack),
         ([], ["[S30] FamilyName: guardado sin los 2 blancos iniciales ('  Pérez   ' -> 'Pérez   ') (L19)"]))
    mira("M-S32-3 letra perdida", c(msg(pid5="Pérez   ^Ana^Luz^^^^L"), FamilyName="Pére"), ["FamilyName: esperado 'Pérez   ', observado 'Pére'"])
    mira("M-S32-3b vacío", c(msg(pid5="Pérez   ^Ana^Luz^^^^L"), FamilyName=""), ["FamilyName: esperado 'Pérez   ', observado ''"])
    mira("M-S33-2 U+3000 finales", revisar(msg(pid5="Pérez\u3000\u3000^Ana^Luz^^^^L"), [bueno_can], ack),
         ([], ["[S32][S33] FamilyName: guardado sin los 2 blancos finales (blancos Unicode: U+3000) ('Pérez\\u3000\\u3000' -> 'Pérez') (L19)"]))
    r = revisar(msg(pid5="\u2028Pérez^Ana^Luz^^^^L"), [bueno_can], ack)
    mira("M-S33-3 U+2028 inicial [S37]", (r, blancos("\u2028Pérez", "Pérez", ["\u2028Pérez"])["decisiones"]),
         (([], ["[S30][S33] FamilyName: guardado sin el blanco inicial (blancos Unicode: U+2028) ('\\u2028Pérez' -> 'Pérez') (L19)"]), ["S30", "S33"]))
    mira("M-S33-4 Cf delante quitado: discrepancia", (len(c(msg(pid5="\u200bPérez^Ana^Luz^^^^L"), FamilyName="Pérez")),
         blancos("\u200bPérez", "Pérez", ["\u200bPérez"])), (1, None))
    mira("M-S33-4b blanco tras Cf: discrepancia", (len(c(msg(pid5="\u200b Pérez^Ana^Luz^^^^L"), FamilyName="\u200bPérez")),
         blancos("\u200b Pérez", "\u200bPérez", ["\u200b Pérez"])), (1, None))
    r = revisar(msg(pid5="\x85Pérez^Ana^Luz^^^^L"), [bueno_can], ack)
    mira("M-S33-5 C1 U+0085: S10", (any("U+0085" in d for d in r[0]), any(d.startswith("FamilyName") for d in r[0]), r[1]), (True, False, []))
    mira("M-S34-2 subcomponente con blanco final", revisar(msg(pid5="Ferrer &Soler^Ana^Luz^^^^L"), [dict(bueno_can, FamilyName="Ferrer Soler")], ack),
         ([], ["[S34] FamilyName: guardado sin el blanco interior en el borde de una parte ('Ferrer  Soler' -> 'Ferrer Soler') (L19)"]))
    mira("M-S34-3 blanco interior de una parte: fallo", c(msg(pid5="Pérez^María  Elena^Luz^^^^L"), GivenName="María Elena Luz"),
         ["GivenName: esperado 'María  Elena Luz', observado 'María Elena Luz'"])
    mira("M-S34-4 MaríaElena: fallo", c(msg(pid5="Pérez^María Elena^Luz^^^^L"), GivenName="MaríaElena Luz"),
         ["GivenName: esperado 'María Elena Luz', observado 'MaríaElena Luz'"])
    mira("M-S34-5 unión sin espacio: fallo", c(msg(pid5="Ferrer&Soler^Ana^Luz^^^^L"), FamilyName="FerrerSoler"),
         ["FamilyName: esperado 'Ferrer Soler', observado 'FerrerSoler'"])
    mira("M-S34-6 orden: fallo", len(c(msg(pid5="Ferrer&Soler^Ana^Luz^^^^L"), FamilyName="Soler Ferrer")), 1)
    mira("M-S34-7 parte perdida: fallo", c(msg(pid5="Pérez^Ana^ Luz^^^^L"), GivenName="Ana"), ["GivenName: esperado 'Ana  Luz', observado 'Ana'"])
    mira("M-S34-8 parte de solo blancos", (revisar(msg(pid5="Ferrer&   &Soler^Ana^Luz^^^^L"), [dict(bueno_can, FamilyName="Ferrer Soler")], ack),
         len(c(msg(pid5="Ferrer&   &Soler^Ana^Luz^^^^L"), FamilyName="Ferrer"))),
         (([], ["[S34] FamilyName: guardado sin los 4 blancos interiores en los bordes de sus partes ('Ferrer     Soler' -> 'Ferrer Soler') (L19)"]), 1))
    mira("M-S34-9 letra junto al blanco: fallo", len(c(msg(pid5="Pérez^Ana^ Luz^^^^L"), GivenName="Ana uz")), 1)
    mira("M-S34-10 todo a la vez", revisar(msg(pid5="  Ferrer &Soler  ^ Ana^ Luz\u00a0^^^^L"),
         [dict(bueno_can, FamilyName="Ferrer Soler", GivenName="Ana Luz")], ack),
         ([], ["[S30][S32][S34] FamilyName: guardado sin los 2 blancos iniciales, los 2 blancos finales y el blanco interior en el borde de una parte ('  Ferrer  Soler  ' -> 'Ferrer Soler') (L19)",
               "[S30][S32][S33][S34] GivenName: guardado sin el blanco inicial, el blanco final y el blanco interior en el borde de una parte (blancos Unicode: U+00A0) (' Ana  Luz\\xa0' -> 'Ana Luz') (L19)"]))

    def subsec(v, raw):
        it = iter(raw)
        return all(ch in it for ch in v)
    inv = True
    for partes in (["  Ferrer", "  ", "Soler "], [" Ana", " Luz "], ["\u200b Pérez"], ["María  Elena", "Luz"], ["  Pérez", "Soler "], [" "],
                   ["\u2028Ana\u2029", "\u3000Luz"]):
        raw = " ".join(partes)
        for v in recortes(partes):
            inv = inv and subsec(v, raw) and "".join(ch for ch in v if ch not in BLANCO) == "".join(ch for ch in raw if ch not in BLANCO)
    mira("M-S34-12 invariante: solo se quitan blancos; BLANCO de 19", (inv, "María Elena Luz" in recortes(["María  Elena", "Luz"]),
         len(BLANCO), " " in BLANCO, "\t" in BLANCO, "\x85" in BLANCO, "\u200b" in BLANCO), (True, False, 19, True, False, False, False))
    mira("M-S37-1 U+2029 final", revisar(msg(pid5="Pérez\u2029^Ana^Luz^^^^L"), [bueno_can], ack),
         ([], ["[S32][S33] FamilyName: guardado sin el blanco final (blancos Unicode: U+2029) ('Pérez\\u2029' -> 'Pérez') (L19)"]))
    mira("M-S37-2 blanco interior de una parte: fallo", c(msg(pid5="Pé\u2028rez^Ana^Luz^^^^L"), FamilyName="Pérez"),
         ["FamilyName: esperado 'Pé\\u2028rez', observado 'Pérez'"])
    r = revisar(msg(pid5="\x1fPérez^Ana^Luz^^^^L"), [bueno_can], ack)
    mira("M-S37-3 Cc U+001F: S10", (any("U+001F" in d for d in r[0]), any(d.startswith("FamilyName") for d in r[0]), r[1]), (True, False, []))
    # --- S31 / S36 (lector por marcos)
    B0 = ["MSH|^~\\&|APP|FAC|R|RF|20230101120000||ADT^A01^ADT_A01|M1|P|2.5", "EVN|A01|20230101", "PID|1||X1^^^H^MR||Pérez^Ana^Luz^^^^L||19800101|F", "PV1|1|I"]
    B2 = [s.replace("|M1|", "|M2|") for s in B0]
    ORIGEN = "<VT><VT>" + B0[0] + "\n<FS>\n<VT>" + "\n".join(B0[1:]) + "\n<FS>\n<FS>"
    SIN_VT, SIN_FS = "\n".join(B0) + "\n<FS>", "<VT>" + "\n".join(B0) + "\n"
    DOS_UN = "<VT>" + "\n".join(B0) + "\n" + "\n".join(B2) + "\n<FS>"
    DOS_MARCOS = "<VT>" + "\n".join(B0) + "\n<FS><VT>" + "\n".join(B2) + "\n<FS>"
    PARTIDA_EVN = "<VT>" + "\n".join(B0[:2]) + "\n<FS><VT>" + "\n".join(B0[2:]) + "\n<FS>"
    HUERFANO = "<VT>EVN|A01|x\n<FS><VT>" + "\n".join(B0) + "\n<FS>"
    tr = trama(ORIGEN)
    mira("M-S31-1 trama del caso origen", (len(tr["marcos"]), tr["sin_msh"], tr["anomalias"], tr["marcos"][1]["segmentos"]),
         (2, [2], ["marcador <VT> repetido (marco 1)", "marcador <FS> repetido (tras el marco 2)"], ["EVN", "PID", "PV1"]))
    mira("M-S31-1b mensajes por cable", [len(mensajes(x)) for x in (SIN_VT, SIN_FS, "\n".join(B0), DOS_UN, DOS_MARCOS, ORIGEN, PARTIDA_EVN,
         HUERFANO, "\x0b" + "\r".join(B0) + "\x1c")], [1, 1, 1, 2, 2, 1, 1, 1, 1])
    mira("M-S31-1c anomalías", [trama(x)["anomalias"] for x in (SIN_VT, SIN_FS, "\n".join(B0), DOS_UN, DOS_MARCOS)],
         [["marco 1 sin <VT>"], ["marco 1 sin <FS>"], ["sin marcadores MLLP"], [], []])
    m0 = mensajes(ORIGEN)[0]
    mira("M-S31-2 el marco 1 trae solo el MSH", ([s.split("|")[0] for s in m0.segs], m0.marco), (["MSH"], 1))
    mira("M-S31-3 marco de cada mensaje", ([m.marco for m in mensajes(DOS_UN)], [m.marco for m in mensajes(DOS_MARCOS)], mensajes(HUERFANO)[0].marco),
         ([1, 1], [1, 2], 2))
    x4 = "<VT>EVN|A01|x\n" + "\n".join(B0) + "\n<FS>"
    mira("M-S31-4 líneas antes del MSH ignoradas", (len(mensajes(x4)[0].segs), trama(x4)["anomalias"]),
         (4, ["marco 1: 1 líneas antes del MSH ignoradas"]))
    mira("M-LF-1 segmentos tras un control que no es CR",
         [segmentos_ocultos(["MSH|^~\\&|a|b<0x0A>EVN|A01<0x09>PID|1|x<0x0A>"], "|"),
          segmentos_ocultos([B0[0] + "<0x0A>"], "|"),
          segmentos_ocultos(["MSH|^~\\&|x\tEVN|A01"], "|"),
          segmentos_ocultos(["MSH|^~\\&|x<0x0A>evn|A01"], "|"),
          segmentos_ocultos(["MSH|^~\\&|<0x0A>UTF|x"], "|"),
          segmentos_ocultos(["MSH|^~\\&|Mu<0xF1>oz|EVN"], "|")],
         [[("EVN", "<0x0A>"), ("PID", "<0x09>")], [], [("EVN", "\\x09")], [], [("UTF", "<0x0A>")], []])
    GARCIA = "García^Lucía^Óscar^^^^L"
    mira("M-S38-1 no_ascii: PID-5 en UTF-8", mensajes(msg(pid5=GARCIA))[0].no_ascii, [("PID", 5)])
    mira("M-S38-2 no_ascii: bytes marcados <0xNN> no cuentan", mensajes(msg(pid5="Mu<0xF1>oz^Ana^Luz^^^^L"))[0].no_ascii, [])
    mira("M-S38-3 no_ascii: la base (Pérez)", mensajes(msg())[0].no_ascii, [("PID", 5)])
    mira("M-S38-4 [S38] el esperado de GARCIA no depende de MSH-18",
         [(esperado(mensajes(msg(pid5=GARCIA).replace("|P|2.5", "|P|2.5" + x))[0])[0]["FamilyName"],
           esperado(mensajes(msg(pid5=GARCIA).replace("|P|2.5", "|P|2.5" + x))[0])[0]["GivenName"]) for x in ("", "||||||ASCII", "||||||8859/1")],
         [("García", "Lucía Óscar")] * 3)
    print("AUTOPRUEBA DE mapeador_referencia: " + ("TODO BIEN" if not mal else "FALLAN %d" % len(mal)))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(autoprueba() if sys.argv[1:2] == ["--autoprueba"] else 0)
