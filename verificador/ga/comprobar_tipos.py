#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33 (ga/diseno-ga-fable.md §6; Jev: ga/decision-jev-gad.md y gad2): el comprobador de tipos y tablas de HL7 v2.5. Mira lo que
el validador de IRIS no ve: el tipo de dato de cada campo y componente, las tablas y las longitudes. No mira la estructura del mensaje.

De dónde sale cada cosa, todo del texto de v2.5 (`estandares/hl7v2/HL7_Messaging_v25/txt/`):
- los campos de cada segmento: sus tablas de atributos, con el lector de la etapa 32 (ivd/texto_ivd.atributos);
- los componentes de cada tipo: las «HL7 Component Table» de CH02A, con un lector del mismo estilo (`componentes`); el §6.1 del
  diseño sirve de contraste (DV-GA-4);
- si una tabla es de HL7 o de usuario: el índice del Apéndice A, como la lectura de la etapa 30 (iv/lectura_iv.py:46-50);
- los valores y patrones de cada tabla: privado/iv/TABLAS-VALORES-IV.json, de iv/tablas_iv.py (no se publica: es texto de HL7).

Las reglas (§6.1-6.2), con las decisiones de Jev:
- R_ausente (error): un campo R vacío. «(B) R» cuenta como B y no se exige (P4). Los C no se miran, salvo OBX-2 frente a OBX-11.
- nulo_en_R (error, P3): `""` en un campo R. Un `""` no pasa por ninguna otra regla (CH02.txt:390-392).
- componentes_de_mas (error, C1); longitud_campo (error, C2: por repetición, con los separadores de componente y subcomponente,
  CH02.txt:430-432); longitud_componente (aviso, C3 y P8).
- no_ascii y escape (error, C4): con MSH-18 vacío, solo 0x20-0x7E (CH02.txt:4599-4602); en un ST y los demás tipos solo valen los
  escapes de separadores, y en TX, FT y CF además H, N, X y Z (CH02.txt:950-973).
- tabla_hl7 (error) y tabla_usuario (aviso, solo si la tabla trae valores sugeridos), C5; un IS siempre es aviso. CE.1 se mira contra
  la tabla del campo solo si CE.3 está vacío o es HL7nnnn de esa tabla.
- componente_retirado (aviso, C6): un componente B valorado. componente_R_ausente (error): un compuesto valorado sin un componente R.
- formato (error): NM, SI, DT, DTM, TM; condicion (error): HD.2 con HD.3, EI.3 con EI.4, MSG.3 con MSG.2 (0354) y OBX-2 con OBX-11.
- Un segmento sin tabla de atributos (los Z) no se mira; un tipo sin tabla de componentes que no sea primitivo, tampoco (se cuenta).
  python3 ga/comprobar_tipos.py <fichero.hl7> ...      los hallazgos de cada fichero"""
import glob
import json
import os
import re
import sys

GA = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(GA)
TXT = os.path.join(FASE, "..", "estandares", "hl7v2", "HL7_Messaging_v25", "txt")
VALORES_F = os.path.join(FASE, "..", "privado", "iv", "TABLAS-VALORES-IV.json")
sys.path[:0] = [os.path.join(FASE, "ivd"), FASE]
import texto_ivd  # noqa: E402

_argv, sys.argv = sys.argv, ["x", "--silencio"]
import estructuras_hl7 as EH  # noqa: E402
sys.argv = _argv

FILA_C = re.compile(r"^\s+(\d+)\s+(\d+)?\s+([A-Z][A-Z0-9]{1,2}|varies)\s+(R|O|C|B|X|W|RE)?\s+(?:(\d{4})\s+)?(\S.*)$")
CABECERA_C = re.compile(r"HL7 Component Table\s*[-–]\s*([A-Z][A-Z0-9]{1,2})\s*[-–]")
PRIMITIVOS = {"ST", "TX", "FT", "NM", "SI", "ID", "IS", "DT", "DTM", "TM", "GTS"}


def componentes(txt=TXT):
    """{tipo: {seq: {len, dt, opt, tbl, cita}}} de las «HL7 Component Table» de CH02A."""
    out, tipo = {}, None
    f = os.path.join(txt, "CH02A.txt")
    for n, l in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
        m = CABECERA_C.search(l)
        if m:
            tipo = m.group(1)
            out.setdefault(tipo, {})
            continue
        if not tipo:
            continue
        if re.match(r"^\s*(Definition:|2\.A\.\d+\s)", l):
            tipo = None
            continue
        m = FILA_C.match(l)
        if m:
            out[tipo].setdefault(int(m.group(1)), {"len": int(m.group(2)) if m.group(2) else None, "dt": m.group(3),
                                                   "opt": m.group(4) or "O", "tbl": m.group(5), "cita": "CH02A.txt:%d" % n})
    return {k: v for k, v in out.items() if v}


ATR = texto_ivd.atributos(TXT)
COMP = componentes()
INDICE = {}
for _n, _l in enumerate(open(os.path.join(TXT, "AppendixA.txt"), encoding="utf-8", errors="replace"), 1):
    _m = re.match(r"^\s+(HL7|User)\s+(\d{4})\s+\S", _l)
    if _m:
        INDICE.setdefault(_m.group(2), {"tipo": _m.group(1), "cita": "AppendixA.txt:%d" % _n})
_V = json.load(open(VALORES_F, encoding="utf-8"))
VALORES = {k: set(v) for k, v in _V["valores"].items()}
PATRONES = {k: [re.compile(p) for p in v] for k, v in _V["patrones"].items()}
T0354 = EH.T0354

NM = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)$")
SI = re.compile(r"^\d{1,4}$")
DT_ = re.compile(r"^(\d{4})(\d{2})?(\d{2})?$")
DTM = re.compile(r"^(\d{4})(?:(\d{2})(?:(\d{2})(?:(\d{2})(?:(\d{2})(?:(\d{2})(?:\.(\d{1,4}))?)?)?)?)?)?([+-]\d{4})?$")
TM = re.compile(r"^(\d{2})(?:(\d{2})(?:(\d{2})(?:\.(\d{1,4}))?)?)?([+-]\d{4})?$")
NO_CONTADOS = {}


def _fecha_ok(m, desde=0):
    if not m:
        return False
    g = m.groups()
    mes, dia = (g[1], g[2]) if desde == 0 else (None, None)
    if mes and not 1 <= int(mes) <= 12:
        return False
    if dia and not 1 <= int(dia) <= 31:
        return False
    return True


def _dtm_ok(v):
    m = DTM.match(v)
    if not _fecha_ok(m):
        return False
    g = m.groups()
    if g[3] and int(g[3]) > 23 or g[4] and int(g[4]) > 59 or g[5] and int(g[5]) > 59:
        return False
    return True


def _tm_ok(v):
    m = TM.match(v)
    if not m:
        return False
    g = m.groups()
    return int(g[0]) <= 23 and (not g[1] or int(g[1]) <= 59) and (not g[2] or int(g[2]) <= 59)


def en_tabla(tbl, v):
    """None si no se puede decidir (tabla sin valores en el texto); si no, True o False."""
    if tbl in VALORES or tbl in PATRONES:
        return v in VALORES.get(tbl, ()) or any(p.match(v) for p in PATRONES.get(tbl, ()))
    return None


def tipo_tabla(tbl):
    return (INDICE.get(tbl) or {}).get("tipo")


class Comprobador:
    def __init__(self, texto):
        self.h = []
        t = texto.replace("\r\n", "\r").replace("\n", "\r")
        self.segs = [s for s in t.split("\r") if s]
        msh = self.segs[0] if self.segs and self.segs[0].startswith("MSH") else None
        self.fs = msh[3] if msh and len(msh) > 3 else "|"
        f = msh.split(self.fs) if msh else []
        enc = f[1] if len(f) > 1 else "^~\\&"
        enc = enc + "^~\\&"[len(enc):]
        self.cs, self.rs, self.es, self.ss = enc[0], enc[1], enc[2], enc[3]
        self.ascii = not (len(f) > 17 and f[17])                # MSH-18 está en f[17]

    def anotar(self, lugar, regla, gravedad, valor, cita=None):
        self.h.append({"lugar": lugar, "regla": regla, "gravedad": gravedad, "valor": valor, "cita": cita})

    def tabla(self, lugar, tbl, v, es_is=False):
        if not tbl or v == "":
            return
        r = en_tabla(tbl, v)
        tt = tipo_tabla(tbl)
        if r is None or r:
            if r is None:
                NO_CONTADOS["tabla_sin_valores:" + tbl] = NO_CONTADOS.get("tabla_sin_valores:" + tbl, 0) + 1
            return
        if tt == "HL7" and not es_is:
            self.anotar(lugar, "tabla_hl7", "error", v, (INDICE.get(tbl) or {}).get("cita"))
        elif tt in ("HL7", "User"):
            self.anotar(lugar, "tabla_usuario", "aviso", v, (INDICE.get(tbl) or {}).get("cita"))
        else:
            NO_CONTADOS["tabla_sin_indice:" + tbl] = NO_CONTADOS.get("tabla_sin_indice:" + tbl, 0) + 1

    def valor(self, lugar, dt, v, tbl, nivel, campo_tbl=None):
        """Un valor (campo, componente o subcomponente) de tipo dt; nivel 0, 1 o 2."""
        if v == "":
            return
        if dt in PRIMITIVOS:
            sep = self.cs if nivel == 0 else self.ss
            if nivel < 2 and sep in v:                                    # un primitivo no tiene componentes (C1)
                self.anotar(lugar, "componentes_de_mas", "error", v, "CH02.txt:484-487")
                return
            if dt == "NM" and not NM.match(v):
                self.anotar(lugar, "formato", "error", v, "CH02A NM")
            elif dt == "SI" and not SI.match(v):
                self.anotar(lugar, "formato", "error", v, "CH02A SI")
            elif dt == "DT" and not _fecha_ok(DT_.match(v)):
                self.anotar(lugar, "formato", "error", v, "CH02A DT")
            elif dt == "DTM" and not _dtm_ok(v):
                self.anotar(lugar, "formato", "error", v, "CH02A DTM")
            elif dt == "TM" and not _tm_ok(v):
                self.anotar(lugar, "formato", "error", v, "CH02A TM")
            elif dt in ("ID", "IS"):
                self.tabla(lugar, tbl, v, es_is=(dt == "IS"))
            return
        comps = COMP.get(dt)
        if not comps:
            NO_CONTADOS["tipo_sin_componentes:" + dt] = NO_CONTADOS.get("tipo_sin_componentes:" + dt, 0) + 1
            return
        sep = self.cs if nivel == 0 else self.ss
        if nivel >= 2:
            return
        partes = v.split(sep)
        if len(partes) > max(comps):
            self.anotar(lugar, "componentes_de_mas", "error", v, comps[max(comps)]["cita"])
        for i, p in enumerate(partes, 1):
            c = comps.get(i)
            if not c:
                continue
            sub = "%s.%d" % (lugar, i)
            if p == "":
                continue
            if c["len"] and len(p) > c["len"]:
                self.anotar(sub, "longitud_componente", "aviso", p, c["cita"])
            if c["opt"] == "B":
                self.anotar(sub, "componente_retirado", "aviso", p, c["cita"])
            if dt in ("CE", "CWE", "CNE") and i == 1 and campo_tbl:     # CE.1 es ST: la tabla del campo se mira aquí
                sistema = partes[2] if len(partes) > 2 else ""
                if sistema in ("", "HL7" + campo_tbl):
                    self.tabla(sub, campo_tbl, p)
            self.valor(sub, c["dt"], p, c["tbl"], nivel + 1)
        if any(p != "" for p in partes):
            for i, c in comps.items():
                if c["opt"] == "R" and (len(partes) < i or partes[i - 1] == ""):
                    self.anotar("%s.%d" % (lugar, i), "componente_R_ausente", "error", v, c["cita"])
        get = lambda i: partes[i - 1] if len(partes) >= i else ""
        if dt == "HD" and bool(get(2)) != bool(get(3)):
            self.anotar(lugar, "condicion", "error", v, comps[2]["cita"])
        if dt == "EI" and bool(get(3)) != bool(get(4)):
            self.anotar(lugar, "condicion", "error", v, comps[3]["cita"])
        if dt == "MSG" and get(2) and get(3) and get(2) not in T0354.get(get(3), []):
            self.anotar(lugar, "condicion", "error", v, "0354")

    def escapes(self, lugar, dt, v):
        if self.ascii and any(not (0x20 <= ord(ch) <= 0x7E) for ch in v):
            self.anotar(lugar, "no_ascii", "error", v, "CH02.txt:4599-4602")
        e = re.escape(self.es)
        validos = "[FSTRE]" if dt not in ("TX", "FT", "CF") else r"(?:[FSTREHN]|X[0-9A-Fa-f]*|Z[^%s]*|\.[a-z]{2}[+-]?\d*|C[0-9A-Fa-f]{4}|M[0-9A-Fa-f]{4,6})" % e
        resto = re.sub("%s%s%s" % (e, validos, e), "", v)
        if self.es in resto:
            self.anotar(lugar, "escape", "error", v, "CH02.txt:950-973")

    def campo(self, seg, n_seg, seq, v, atr, obx2=None):
        lugar = "%s%s-%d" % (seg, "" if n_seg == 1 else "(%d)" % n_seg, seq)
        opt = atr["opt"]
        if v == "":
            if opt == "R":
                self.anotar(lugar, "R_ausente", "error", v, atr["cita"])
            return
        if v == '""':
            if opt == "R":
                self.anotar(lugar, "nulo_en_R", "error", v, atr["cita"])
            return
        dt = atr["dt"]
        if dt in ("varies", "varie"):
            dt = obx2 if obx2 in COMP or obx2 in PRIMITIVOS else None
            if not dt:
                return
        for k, rep in enumerate(v.split(self.rs) if not (seg == "MSH" and seq == 2) else [v], 1):
            lr = lugar if k == 1 else "%s[%d]" % (lugar, k)
            if rep == '""':
                continue
            if atr["len"] and len(rep) > atr["len"] and dt not in ("varies",):
                self.anotar(lr, "longitud_campo", "error", rep, atr["cita"])
            self.escapes(lr, dt, rep)
            self.valor(lr, dt, rep, atr["tbl"] if dt in ("ID", "IS") else None, 0, campo_tbl=atr["tbl"])

    def correr(self):
        vistos = {}
        for s in self.segs:
            seg = s[:3]
            vistos[seg] = vistos.get(seg, 0) + 1
            atr = ATR.get(seg)
            if not atr:
                NO_CONTADOS["segmento_sin_tabla:" + seg] = NO_CONTADOS.get("segmento_sin_tabla:" + seg, 0) + 1
                continue
            f = s.split(self.fs)
            if seg == "MSH":
                f = ["MSH", self.fs] + f[1:]            # MSH-n en f[n]
            obx2 = f[2] if seg == "OBX" and len(f) > 2 else None
            for seq, a in sorted(atr.items()):
                if seg == "MSH" and seq in (1, 2):
                    continue
                self.campo(seg, vistos[seg], seq, f[seq] if len(f) > seq else "", a, obx2)
            if seg == "OBX":
                o11 = f[11] if len(f) > 11 else ""
                if o11 != "X" and (len(f) <= 2 or f[2] == ""):
                    self.anotar("OBX%s-2" % ("" if vistos[seg] == 1 else "(%d)" % vistos[seg]), "condicion", "error", "",
                                "CH07.txt:2574-2575")
        return self.h


def comprobar(texto):
    return Comprobador(texto).correr()


if __name__ == "__main__":
    for r in sys.argv[1:]:
        for f in sorted(glob.glob(r)):
            hs = comprobar(open(f, encoding="utf-8", errors="replace").read())
            print("%s: %d errores, %d avisos" % (f, sum(h["gravedad"] == "error" for h in hs), sum(h["gravedad"] == "aviso" for h in hs)))
            for h in hs:
                print("   %-6s %-22s %-20s %r" % (h["gravedad"], h["lugar"], h["regla"], h["valor"][:40]))
