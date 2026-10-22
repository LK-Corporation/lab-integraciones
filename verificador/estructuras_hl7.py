#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Estructuras de mensaje HL7 v2.5 como datos y el emparejador recursivo (diseno-multitipo-fable.md §3.2 y §3.4).

La tabla (`estructuras_25.json`) la escribe `extraer_estructuras.py` a partir del texto del estándar; aquí solo se
carga (determinista, sin leer markdown en ejecución). Gramática [E2 §2.13.1]: ítems
  ["SEG", nombre, opcional, repite] | ["GRUPO", nombre, opcional, repite, hijos] | ["ELIGE", [nombres]].

`emparejar(nombres, gramatica)` devuelve el mismo dict que `acuse_referencia.estructura()` (hallazgos, vistos, faltan,
fuera_de_orden, repetidos, ignorados) para que resumen_segmentos, notas_s45 y comparar no cambien. Reglas, en el orden
de hoy, con S2/S14/S45 y [E2 §2.6.2]:
  1. Ausentes (P3.3, AE 100): todo obligatorio efectivo (segmento R cuyos grupos antecesores son todos R) que no
     aparezca; un grupo opcional en el que se entra exige sus R (AMB-MT-2: ORU sin OBR -> 100 OBR).
  2. Orden (P3.4, AE 100): solo un obligatorio efectivo no multiposición que llega detrás de una posición posterior ya
     aceptada en su marco (S45 literal); dentro de un grupo repetible la copia siguiente reinicia la posición. Tras el
     primer P3.4 no se juzga el resto (como hoy).
  3. Repetidos (P3.5, AE 100): un [1..1] de nivel raíz que aparece dos veces [S14][S48]; dentro de un grupo repetible,
     el segmento que abre el grupo abre otra copia; otro [1..1] repetido en la misma copia se ignora con nota (L-MT3).
  4. Opcional fuera de posición (detrás de lo aceptado, o delante de un obligatorio pendiente anterior) -> «~»,
     ignorado [S45]; desconocido -> «?», ignorado [E2 §2.6.2 a]; ROL ya no es caso especial: es multiposición.
  5. Multiposición: primera posición compatible con lo último aceptado; nunca 100 por orden (AMB-MT-3).
  6. Elección <OBR|RQD|…>: cualquiera cuenta; una segunda alternativa en la misma copia se ignora con nota (L-MT4).
Límite L-MT3: dentro de los grupos no se aplica la regla del obligatorio pendiente (tope) de S45; y el «presente en el
mensaje» del tope se mira en todo el cable, como hoy."""
import json
import os
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
RUTA = os.path.join(AQUI, "estructuras_25.json")
TABLA = json.load(open(RUTA, encoding="utf-8"))
GRAMATICAS = {n: v["gramatica"] for n, v in TABLA["estructuras"].items()}
FUENTES = {n: v["fuente"] for n, v in TABLA["estructuras"].items()}
T0354 = TABLA["t0354"]["eventos"]                                   # estructura -> [eventos] [E2 §2.17.3]
ERRATAS_0354 = TABLA["t0354"]["erratas"]
TABLAS = {t: dict(v["codigos"]) for t, v in TABLA["tablas"].items()}  # 0003, 0085, 0119, 0125, 0271: código -> descripción
CAMPOS = {k: v for seg in TABLA["campos"].values() for k, v in seg["atributos"].items()}   # "OBX-11" -> {len, dt, opt, rep, tabla}


def gramatica(nombre):
    return GRAMATICAS.get(nombre)


def segmentos(items):
    """Todos los nombres de segmento, en orden y con repetición (una entrada por posición en la gramática)."""
    out = []
    for it in items:
        if it[0] == "SEG":
            out.append(it[1])
        elif it[0] == "GRUPO":
            out += segmentos(it[4])
        elif it[0] == "ELIGE":
            out += list(it[1])
    return out


def obligatorios_efectivos(items):
    """Segmentos R cuyos grupos antecesores son todos R, en orden y con repetición (ADT_A17: PID y PV1 dos veces)."""
    out = []
    for it in items:
        if it[0] == "SEG" and not it[2]:
            out.append(it[1])
        elif it[0] == "GRUPO" and not it[2]:
            out += obligatorios_efectivos(it[4])
    return out


def multiposicion(items):
    return {s for s, n in Counter(segmentos(items)).items() if n > 1}


def orden_segmentos(items):
    """{segmento: rango} por primera aparición en la gramática aplanada (para ordenar P5 y el bucle S10)."""
    out = {}
    for s in segmentos(items):
        out.setdefault(s, len(out))
    return out


def aplanar(items):
    """Posición raíz de cada segmento (como POS) y obligatorios raíz (como OBLIGATORIOS): para las afirmaciones §3.1."""
    pos, obl = {}, []
    for p, it in enumerate(items):
        if it[0] == "SEG":
            pos.setdefault(it[1], []).append(p)
            if not it[2]:
                obl.append(it[1])
        elif it[0] == "GRUPO":
            for s in segmentos(it[4]):
                pos.setdefault(s, []).append(p)
        elif it[0] == "ELIGE":
            for s in it[1]:
                pos.setdefault(s, []).append(p)
    return pos, obl


def en_grupos(items):
    return {s for it in items if it[0] == "GRUPO" for s in segmentos(it[4])}


# ---------------------------------------------------------------------------- emparejador §3.4
class _Marco:
    __slots__ = ("items", "nombre", "p", "p_ob", "vistos", "ult")

    def __init__(self, items, nombre):
        self.items, self.nombre = items, nombre
        self.p = -1                 # índice del último ítem aceptado en esta copia (los opcionales se miden contra él)
        self.p_ob = -1              # índice del último obligatorio efectivo aceptado (los obligatorios, contra él: como hoy)
        self.vistos = set()         # segmentos aceptados en esta copia; ("G", nombre) para los grupos abiertos
        self.ult = None             # último segmento aceptado en o bajo esta copia (para «tras X»)


def _contiene(item, nmb):
    if item[0] == "SEG":
        return item[1] == nmb
    if item[0] == "ELIGE":
        return nmb in item[1]
    return nmb in segmentos(item[4])


def _buscar(F, nmb, nombres, obligatorio, copia=False):
    """Decisión para colocar `nmb` en el marco F: ("acepta", ruta) con ruta = [(i, ítem), …] (los GRUPO abren copia
    nueva; el último es SEG o ELIGE); ("antes", pendiente); ("repetido", i, ítem); ("tras", último); None si no está.
    `copia`: F es una copia nueva de un grupo repetible; no puede abrirse saltándose un R anterior (quedaría sin cumplir)."""
    cands = [(i, it) for i, it in enumerate(F.items) if _contiene(it, nmb)]
    if not cands:
        return None
    ref = F.p_ob if obligatorio else F.p
    detras, repetido = False, None
    for i, it in cands:
        if i < ref:
            detras = True
            continue
        if i == ref:
            if it[0] == "SEG" and it[3]:
                return ("acepta", [(i, it)])
            if it[0] in ("SEG", "ELIGE"):                             # [1..1] ya aceptado aquí: repetido, salvo que haya otra
                repetido = repetido or ("repetido", i, it)           # posición posterior (multiposición: PID PID en A24/A37)
                continue
            if it[3]:                                                # grupo repetible: otra copia
                sub = _buscar(_Marco(it[4], it[1]), nmb, nombres, obligatorio, copia=True)
                if sub and sub[0] == "acepta":
                    return ("acepta", [(i, it)] + sub[1])
            detras = True
            continue
        if copia and any(x[0] == "SEG" and not x[2] for x in F.items[:i]):
            return None
        if not obligatorio and not copia:                            # [S45] tope: un R anterior pendiente y presente en el cable
            pend = [x[1] for j, x in enumerate(F.items) if j < i and x[0] == "SEG" and not x[2] and x[1] not in F.vistos
                    and x[1] in nombres]
            if pend:
                return ("antes", pend[0])
        if it[0] in ("SEG", "ELIGE"):
            return ("acepta", [(i, it)])
        sub = _buscar(_Marco(it[4], it[1]), nmb, nombres, obligatorio, copia=copia)
        if sub and sub[0] in ("acepta", "antes"):
            return ("acepta", [(i, it)] + sub[1]) if sub[0] == "acepta" else sub
    if repetido:
        return repetido
    return ("tras", F.ult) if detras else None


def emparejar(nombres, items, estructura=None):
    """-> {hallazgos [(código, segmento, nivel, regla)], vistos [(nombre, marca)], faltan, fuera_de_orden, repetidos,
    ignorados [(nombre, motivo)]}; mismo contrato que acuse_referencia.estructura().
    [DV-MT-E1] La gramática define el lenguaje válido (§2.12, §2.13.1): si la lectura interna (la de siempre) deja algún
    P3.3 y la lectura que prefiere otra copia del grupo exterior a abrir un grupo anidado deja estrictamente menos 100, se
    toma esa (OMG_O19: el segundo ORC es un ORDER nuevo, no un ORDER_PRIOR sin OBX). Sin P3.3, idéntico a la de siempre."""
    r = _emparejar(nombres, items, estructura, externa=False)
    if any(h[3] == "P3.3" for h in r["hallazgos"]):
        cien = lambda x: sum(h[0] == "100" for h in x["hallazgos"])    # noqa: E731
        mejor = r
        r2 = _emparejar(nombres, items, estructura, externa=True)
        if cien(r2) < cien(mejor):
            r2["lectura_externa"] = True
            mejor = r2
        # [N13] S45 (§2.6.2 a): un segmento OPCIONAL que abrió un grupo (o una copia nueva) y dejó un P3.3 puede leerse como
        # fuera de posición, ignorado. Vale si alguna lectura lo cubre (como DV-MT-E1): se adopta la de estrictamente menos 100.
        for k in r.get("abre_opcional", []):
            r3 = _emparejar(nombres, items, estructura, externa=False, ignorar={k})
            if cien(r3) < cien(mejor):
                r3["lectura_s45"] = k
                mejor = r3
        mejor.pop("abre_opcional", None)
        return mejor
    r.pop("abre_opcional", None)
    return r


def _emparejar(nombres, items, estructura, externa, ignorar=frozenset()):
    todos = set(segmentos(items))
    oblig = obligatorios_efectivos(items)
    oblig_set, multi = set(oblig), multiposicion(items)
    hall, faltan, marcas, repetidos, ignorados = [], [], [], [], []
    emitidos = set()
    req, hay = Counter(oblig), Counter(nombres)
    for nmb in dict.fromkeys(oblig):                                 # 1. ausentes (P3.3)
        if hay[nmb] < req[nmb]:
            faltan.append(nmb)
            hall.append(("100", nmb, "consumido", "P3.3"))
            emitidos.add(nmb)

    def falta(nmb):
        if nmb not in emitidos:
            emitidos.add(nmb)
            faltan.append(nmb)
            hall.append(("100", nmb, "consumido", "P3.3"))

    def exigidos(items_g, vistos):
        """R directos de una copia abierta que no aparecieron -> P3.3 (AMB-MT-2); grupos R no abiertos, recursivo."""
        for it in items_g:
            if it[0] == "SEG" and not it[2] and it[1] not in vistos:
                falta(it[1])
            elif it[0] == "GRUPO" and not it[2] and ("G", it[1]) not in vistos:
                for s in dict.fromkeys(obligatorios_efectivos(it[4])):
                    falta(s)
            elif it[0] == "ELIGE" and not any(a in vistos for a in it[1]):
                falta(it[1][0])                                      # L-MT4: se nombra la primera alternativa

    def cerrar(pila, nivel):
        while len(pila) - 1 > nivel:
            G = pila.pop()
            exigidos(G.items, G.vistos)
    pila = [_Marco(items, estructura or "raíz")]
    fuera = None
    abre_opcional = []                                               # [N13] opcionales que abrieron un grupo o una copia
    for k, nmb in enumerate(nombres):
        marca = ""
        if k in ignorar:                                             # [N13] lectura S45: este opcional, fuera de posición
            marca = "~"
            ignorados.append((nmb, "fuera de posición [S45] (lectura N13)"))
        elif nmb not in todos:
            marca = "?"                                              # se ignora [E2 §2.6.2 a]
        elif fuera is None:
            obligatorio = nmb in oblig_set
            dec, nivel, tras_dentro = None, None, False
            for d in range(len(pila) - 1, -1, -1):                   # del marco más interno al raíz
                r = _buscar(pila[d], nmb, nombres, obligatorio)
                if r is None:
                    continue
                if r[0] == "acepta":                                 # un padre que acepta (otra copia) gana al repetido/antes interno
                    tras_dentro = dec is not None and dec[0] == "tras"   # [N13] el marco interno lo dejó DETRÁS de su posición
                    dec, nivel = r, d
                    if externa and d > 0 and r[1][0][1][0] == "GRUPO":  # [DV-MT-E1] abrir un anidado: ¿otra copia fuera?
                        for d2 in range(d - 1, -1, -1):
                            r2 = _buscar(pila[d2], nmb, nombres, obligatorio)
                            if r2 and r2[0] == "acepta":
                                dec, nivel = r2, d2
                                break
                    break
                if dec is None:
                    dec, nivel = r, d
            if dec is None or dec[0] == "tras":
                if nmb in oblig_set and nmb not in multi:            # 2. orden (P3.4) [S2]
                    marca, fuera = "!", nmb
                    hall.append(("100", nmb, "consumido", "P3.4"))
                else:                                                # 4./5. opcional o multiposición fuera de posición
                    marca = "~"
                    ignorados.append((nmb, "tras %s" % ((dec[1] if dec else None) or pila[-1].ult)))
            elif dec[0] == "antes":
                marca = "~"
                ignorados.append((nmb, "antes de %s" % dec[1]))
            elif dec[0] == "repetido":
                _, i, it = dec
                F = pila[nivel]
                if nivel == 0 and it[0] == "SEG" and not it[2]:      # 3. raíz [1..1] repetido [S14][S48]
                    cerrar(pila, 0)
                    marca = "+"
                    repetidos.append(nmb)
                    hall.append(("100", nmb, "consumido", "P3.5"))
                    F.p, F.p_ob, F.ult = i, i, nmb
                elif it[0] == "ELIGE":
                    marca = "~"
                    ignorados.append((nmb, "segunda alternativa de <%s> en %s (L-MT4)" % ("|".join(it[1]), F.nombre)))
                else:
                    marca = "~"
                    ignorados.append((nmb, "repetido en %s (L-MT3)" % F.nombre if nivel else "repetido [0..1]"))
            else:
                if not obligatorio and dec[1][0][1][0] == "GRUPO" and tras_dentro:   # [N13] solo «fuera de posición» (S45),
                    abre_opcional.append(k)                          # no un segmento que se repite (PID PID: otro paciente)
                cerrar(pila, nivel)
                F = pila[nivel]
                for i, it in dec[1]:
                    F.p, F.ult = i, nmb
                    if obligatorio:
                        F.p_ob = i
                    if it[0] == "GRUPO":
                        F.vistos.add(("G", it[1]))
                        F = _Marco(it[4], it[1])
                        pila.append(F)
                    else:
                        F.vistos.add(nmb)
        marcas.append((nmb, marca))
    cerrar(pila, 0)
    return {"hallazgos": hall, "vistos": marcas, "faltan": faltan, "fuera_de_orden": fuera, "repetidos": repetidos,
            "ignorados": ignorados, "abre_opcional": abre_opcional}
