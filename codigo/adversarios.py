#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Banco de CONTROL NEGATIVO del puntuador de la Fase 12.

Reconstruye las estrategias SIN CEREBRO con las que la revision adversaria del
20-sep demostro que el puntuador no mide triaje, y las deja escritas como
ficheros de respuestas normales para poder puntuarlas con CUALQUIER version
del puntuador.

POR QUE EXISTE ESTE FICHERO: el arreglo del puntuador no se puede validar
diciendo "ahora esta mejor". Se valida ensenandole las mismas respuestas que
antes sacaban 0,922 y comprobando que ahora se hunden. Si no se reproduce
primero el fallo, no se ha arreglado nada: se ha cambiado de sitio.

NINGUNA de estas estrategias mira la tabla de casos para CONTESTAR. Lo unico
que leen es lo que ve el brazo (b): el mensaje, el ACK, el log y el canonico.
Las dos primeras son la excepcion declarada: la clave barajada necesita la
clave por construccion, porque es la autoprueba (iii), no un atacante.

Estrategias:
  clave_barajada_09    veredicto barajado, cat/locus/accion CORRECTOS, conf 0,90
  clave_barajada_069   lo mismo a conf 0,69  -> el umbral de confianza es gratis
  filas_barajadas_05   filas enteras barajadas, conf 0,50  -> azar de verdad
  sinproblema_diff     siempre SIN_PROBLEMA + cat/locus/accion por diff, 0,69
  lookup_completo      ACK + ERR-8 + forma del canonico + diff, 0,69

Uso:
  python3 adversarios.py tabla_casos.tsv informe_total.tsv casos/ salida_dir/
"""
import collections
import io
import os
import random
import re
import sys


# ---------------------------------------------------------------------------
# Lectura
# ---------------------------------------------------------------------------
def cargar(ruta):
    with io.open(ruta, encoding="utf-8") as fh:
        cols = fh.readline().rstrip("\n").split("\t")
        return [dict(zip(cols, l.rstrip("\n").split("\t"))) for l in fh if l.strip()]


def leer_mensaje(dir_casos, caso_id):
    ruta = os.path.join(dir_casos, caso_id + ".hl7")
    if not os.path.exists(ruta):
        return None
    with io.open(ruta, "rb") as fh:
        crudo = fh.read()
    txt = crudo.decode("utf-8", "replace")
    return [s for s in re.split(r"[\r\n]+", txt) if s.strip()]


# ---------------------------------------------------------------------------
# EL DIFF CONTRA LA PLANTILLA
#
# El revisor lo dijo asi: "las cinco bases comparten esqueleto, direccion,
# MSH-7 y orden de segmentos, asi que un diff contra la plantilla da el locus".
# Aqui ni siquiera hace falta tener la plantilla: se RECONSTRUYE por mayoria
# entre los casos que comparten base. Esto no usa la clave para nada.
#
# El estorbo real: MSH-10 y el identificador de PID-3 son DISTINTOS EN CADA
# CASO, asi que una mayoria a pelo no reconstruye nada. La salida de un
# atacante perezoso es obvia y no exige entender HL7: mirar primero el literal
# y, si el literal cambia en todos los mensajes, mirar su PATRON (las cifras
# sustituidas por #). El identificador `LAB-302207^^^LAB^MR` tiene un patron
# estable; `F127C6F78CFFAAC8` no lo tiene ni asi, y ese campo se descarta.
# Un campo descartado es un campo donde este atacante no puede acusar nada.
# ---------------------------------------------------------------------------
RE_CIFRAS = re.compile(r"\d+")


def patron(x):
    return RE_CIFRAS.sub("#", x)


def nombre_seg(linea):
    return linea[:3]


def campos(linea):
    """Campos con su numero HL7. En MSH, MSH-1 es el propio separador."""
    trozos = linea.split("|")
    desfase = 1 if nombre_seg(linea) == "MSH" else 0
    return [(i + desfase, t) for i, t in enumerate(trozos) if i + desfase > 0]


def indexar(segs):
    """[(SEG, ocurrencia), linea] — soporta segmentos repetidos."""
    visto = collections.Counter()
    fuera = []
    for l in segs:
        n = nombre_seg(l)
        fuera.append(((n, visto[n]), l))
        visto[n] += 1
    return fuera


def modelo_por_base(filas, dir_casos):
    """Para cada base: el orden de segmentos normal y, por campo, con que se
    compara (literal, patron, o nada porque cambia siempre)."""
    porbase = collections.defaultdict(list)
    for f in filas:
        segs = leer_mensaje(dir_casos, f["caso_id"])
        if segs:
            porbase[f["base_id"]].append(segs)

    modelos = {}
    for base, lista in porbase.items():
        n = len(lista)
        orden = collections.Counter(
            tuple(nombre_seg(l) for l in s) for s in lista).most_common(1)[0][0]
        lit = collections.defaultdict(collections.Counter)
        pat = collections.defaultdict(collections.Counter)
        for s in lista:
            for clave, linea in indexar(s):
                for num, val in campos(linea):
                    lit[(clave, num)][val] += 1
                    pat[(clave, num)][patron(val)] += 1
        reglas = {}
        for k in lit:
            if len(lit[k]) <= max(2, 0.5 * n):
                reglas[k] = ("literal", lit[k].most_common(1)[0][0])
            elif len(pat[k]) <= max(2, 0.5 * n):
                reglas[k] = ("patron", pat[k].most_common(1)[0][0])
            # si tampoco el patron es estable, el campo no es acusable
        modelos[base] = (list(orden), reglas)
    return modelos


def locus_por_diff(segs, modelo):
    """El locus deducido comparando el mensaje con el modelo de su base."""
    if not segs or not modelo:
        return ""
    orden, reglas = modelo
    aqui = [nombre_seg(l) for l in segs]

    # 1. El esqueleto cambio: sobra, falta o esta desordenado un segmento.
    if aqui != orden:
        sobra = [x for x in aqui if aqui.count(x) > orden.count(x)]
        if sobra:
            return sobra[0]
        falta = [x for x in orden if orden.count(x) > aqui.count(x)]
        if falta:
            return falta[0]
        for a, b in zip(aqui, orden):           # mismo conjunto, otro orden
            if a != b:
                return a
        return aqui[0]

    # 2. Mismo esqueleto: el primer campo acusable que difiere.
    for clave, linea in indexar(segs):
        for num, val in campos(linea):
            regla = reglas.get((clave, num))
            if regla is None:
                continue                        # campo volatil: no acusable
            modo, esperado = regla
            visto = val if modo == "literal" else patron(val)
            if visto != esperado:
                return "%s:%d" % (clave[0], num)

    # 3. No se ve nada. Es uno de los casos inganables.
    return ""


# ---------------------------------------------------------------------------
# LA FORMA DEL CANONICO: las seis reglas de grep del revisor
# ---------------------------------------------------------------------------
RE_IDENT = re.compile(r"^LAB-\d{6}$")
RE_SUCIO = re.compile("\\\\[SFRTE]\\\\|[�?]|Ã|Â")


def canonico_sospechoso(m):
    """Seis senales visibles en el Patient que salio, sin mirar la clave."""
    s = []
    if not (m.get("can_birthdate") or "").strip():
        s.append("birthdate_vacio")
    g = (m.get("can_gender") or "").strip()
    if g in ("", "unknown", "other"):
        s.append("gender_" + (g or "vacio"))
    ident = (m.get("can_identifier") or "").strip()
    if ident and not RE_IDENT.match(ident):
        s.append("ident_fuera_de_patron")
    fam = m.get("can_family") or ""
    if RE_SUCIO.search(fam):
        s.append("apellido_sucio")
    if not fam.strip():
        s.append("apellido_vacio")
    if not (m.get("can_given") or "").strip():
        s.append("nombre_vacio")
    n = (m.get("n_recurso_canonico") or "").strip()
    if n not in ("1", ""):
        s.append("n_recursos_" + n)
    return s


# ---------------------------------------------------------------------------
# LOS MAPAS FACILES: categoria casi funcion del locus, accion casi funcion del
# veredicto. Se aprenden SOLO de la particion CALIBRACION, que es lo que el
# protocolo permite mirar.
# ---------------------------------------------------------------------------
def aprender_mapas(filas):
    cal = [f for f in filas if f["particion"] == "CALIBRACION" and f["puntua"] == "1"]
    cat = collections.defaultdict(collections.Counter)
    acc = collections.defaultdict(collections.Counter)
    for f in cal:
        cat[f["locus"]][f["clase"]] += 1
        acc[f["esperado_veredicto"]][f["esperado_accion"]] += 1
    return ({k: v.most_common(1)[0][0] for k, v in cat.items()},
            {k: v.most_common(1)[0][0] for k, v in acc.items()})


ACC_POR_DEFECTO = {
    "SIN_PROBLEMA": "NADA",
    "RECHAZO_POLITICA": "NADA",
    "FALLO_MENSAJE": "CORREGIR_EMISOR",
    "ENTORNO": "ESCALAR_ENTORNO",
    "RESULTADO_INCORRECTO_SILENCIOSO": "CORREGIR_MAPEO",
}


# ---------------------------------------------------------------------------
# EL LOOKUP SIN CEREBRO: el que saca 0,922. Es una tabla escrita a mano sobre
# lo que el circuito DICE de si mismo. No razona sobre HL7 en ningun momento.
# ---------------------------------------------------------------------------
def lookup_veredicto(m, sospechas):
    ack = (m.get("medido_ack") or "").strip()
    texto = " ".join([m.get("medido_err8") or "", m.get("medido_err3") or ""])
    if ack in ("AR", "AE", "CE", "CR", "SIN_ACK", ""):
        if re.search(r"Tipo de mensaje no soportado", texto, re.I):
            return "RECHAZO_POLITICA"
        if re.search(r"FHIR devolvio \d\d\d|401|404|connection|Connect|"
                     r"timeout|no devolvio respuesta", texto, re.I):
            return "ENTORNO"
        if ack == "":
            return "ENTORNO"
        return "FALLO_MENSAJE"
    # ACK positivo: la unica pista que queda es como quedo el paciente.
    if sospechas:
        return "RESULTADO_INCORRECTO_SILENCIOSO"
    return "SIN_PROBLEMA"


# ---------------------------------------------------------------------------
# Escritura
# ---------------------------------------------------------------------------
COLS = ["caso_id", "veredicto", "categoria", "locus", "accion", "confianza", "causa"]


def escribir(ruta, filas_resp):
    with io.open(ruta, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(COLS) + "\n")
        for r in filas_resp:
            fh.write("\t".join(str(r.get(c, "")) for c in COLS) + "\n")
    return len(filas_resp)


def main():
    tabla, informe, dir_casos, salida = sys.argv[1:5]
    filas = cargar(tabla)
    med = {m["caso_id"]: m for m in cargar(informe)}
    puntua = [f for f in filas if f["puntua"] == "1"]
    if not os.path.isdir(salida):
        os.makedirs(salida)

    plantillas = modelo_por_base(filas, dir_casos)
    mapa_cat, mapa_acc = aprender_mapas(filas)
    for k, v in ACC_POR_DEFECTO.items():
        mapa_acc.setdefault(k, v)

    # --- diff: locus deducido caso a caso, sin clave -----------------------
    locus_diff = {}
    for f in filas:
        segs = leer_mensaje(dir_casos, f["caso_id"])
        locus_diff[f["caso_id"]] = locus_por_diff(segs, plantillas.get(f["base_id"]))

    ok = sum(1 for f in puntua if locus_diff[f["caso_id"]] == f["locus"])
    print("diff contra la plantilla: locus exacto en %d de %d casos (%.1f %%)"
          % (ok, len(puntua), 100.0 * ok / len(puntua)))
    ok_cat = sum(1 for f in puntua
                 if mapa_cat.get(locus_diff[f["caso_id"]], "NINGUNA") == f["clase"])
    print("categoria por locus aprendido en CALIBRACION: %d de %d (%.1f %%)"
          % (ok_cat, len(puntua), 100.0 * ok_cat / len(puntua)))

    hechos = []

    # --- (1) y (2): la clave barajada, que es la autoprueba (iii) ----------
    for conf, nombre in ((0.90, "clave_barajada_09"), (0.69, "clave_barajada_069")):
        rnd = random.Random(11)
        orden = [f["esperado_veredicto"] for f in puntua]
        rnd.shuffle(orden)
        resp = [{"caso_id": f["caso_id"], "veredicto": v, "categoria": f["clase"],
                 "locus": f["locus"], "accion": f["esperado_accion"],
                 "confianza": conf, "causa": "clave barajada"}
                for f, v in zip(puntua, orden)]
        hechos.append((nombre, escribir(
            os.path.join(salida, "respuestas_%s.tsv" % nombre), resp)))

    # --- (3) filas enteras barajadas: el azar de verdad ---------------------
    rnd = random.Random(23)
    fuente = list(puntua)
    rnd.shuffle(fuente)
    resp = [{"caso_id": f["caso_id"], "veredicto": g["esperado_veredicto"],
             "categoria": g["clase"], "locus": g["locus"],
             "accion": g["esperado_accion"], "confianza": 0.5,
             "causa": "fila barajada"}
            for f, g in zip(puntua, fuente)]
    hechos.append(("filas_barajadas_05", escribir(
        os.path.join(salida, "respuestas_filas_barajadas_05.tsv"), resp)))

    # --- (4) siempre SIN_PROBLEMA + los tres faciles por diff --------------
    resp = []
    for f in puntua:
        l = locus_diff[f["caso_id"]]
        resp.append({"caso_id": f["caso_id"], "veredicto": "SIN_PROBLEMA",
                     "categoria": mapa_cat.get(l, "NINGUNA"), "locus": l,
                     "accion": "NADA", "confianza": 0.69,
                     "causa": "perezoso con diff"})
    hechos.append(("sinproblema_diff", escribir(
        os.path.join(salida, "respuestas_sinproblema_diff.tsv"), resp)))

    # --- (5) EL LOOKUP COMPLETO: el que saca 0,922 -------------------------
    veredicto_lookup = {f["caso_id"]: lookup_veredicto(
        med.get(f["caso_id"], {}), canonico_sospechoso(med.get(f["caso_id"], {})))
        for f in puntua}
    resp = []
    for f in puntua:
        l = locus_diff[f["caso_id"]]
        v = veredicto_lookup[f["caso_id"]]
        resp.append({"caso_id": f["caso_id"], "veredicto": v,
                     "categoria": mapa_cat.get(l, "NINGUNA"), "locus": l,
                     "accion": mapa_acc.get(v, "NADA"), "confianza": 0.69,
                     "causa": "lookup sin cerebro"})
    hechos.append(("lookup_completo", escribir(
        os.path.join(salida, "respuestas_lookup_completo.tsv"), resp)))

    # --- (6) y (7) LOS TECHOS ---------------------------------------------
    # El revisor publico 0,680 y 0,922 para las dos de arriba. Esos numeros
    # SALEN si se supone que categoria, locus y accion se aciertan SIEMPRE.
    # Un diff honesto no llega a tanto (aqui saca 69 % de locus y 48 % de
    # categoria), asi que se miden las dos cosas: lo que un atacante consigue
    # HOY, y el TECHO de la estrategia si afinara el diff hasta clavarlos.
    # El puntuador hay que disenarlo contra el techo, no contra el atacante
    # que ya existe.
    for nombre, quien in (("sinproblema_techo", lambda f: "SIN_PROBLEMA"),
                          ("lookup_techo", lambda f: veredicto_lookup[f["caso_id"]])):
        resp = [{"caso_id": f["caso_id"], "veredicto": quien(f),
                 "categoria": f["clase"], "locus": f["locus"],
                 "accion": f["esperado_accion"], "confianza": 0.69,
                 "causa": "techo: los tres faciles regalados"}
                for f in puntua]
        hechos.append((nombre, escribir(
            os.path.join(salida, "respuestas_%s.tsv" % nombre), resp)))

    for nombre, n in hechos:
        print("  %-22s %d respuestas" % (nombre, n))

    # Cuanto acierta de VEREDICTO cada estrategia, que es lo unico que deberia
    # contar en el titular.
    print()
    print("aciertos de veredicto (macro por clase verdadera):")
    for nombre, quien in (("sinproblema", lambda f: "SIN_PROBLEMA"),
                          ("lookup", lambda f: veredicto_lookup[f["caso_id"]])):
        por = collections.defaultdict(list)
        for f in puntua:
            por[f["esperado_veredicto"]].append(
                1.0 if quien(f) in set(f["ideal_b"].split("|")) else 0.0)
        cl = {k: sum(v) / len(v) for k, v in por.items()}
        print("  %-14s %.3f   %s" % (nombre, sum(cl.values()) / len(cl),
                                     "  ".join("%s %.2f" % (k[:12], v)
                                               for k, v in sorted(cl.items()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
