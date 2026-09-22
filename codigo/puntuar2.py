#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El puntuador de la Fase 12, version 2 — reescrito tras la revision adversaria.

POR QUE HAY UNA VERSION 2. La version 1 no medía triaje. Categoria, locus y
accion valian 3 de los 5 puntos y SE CONCEDIAN AUNQUE EL VEREDICTO ESTUVIERA
MAL; los tres se sacan con un diff contra la plantilla, sin razonar. Medido:
un lookup sin cerebro sacaba 0,938 y pasaba tres de los seis criterios
firmados. Reproducido antes de tocar nada con `adversarios.py`.

LOS SEIS ARREGLOS (apartado 8.1 del informe del revisor):

  1. El titular ya no regala los tres campos faciles. Dos modos, y los dos se
     imprimen siempre para que no se pueda elegir despues de ver el resultado:
       veredicto     el titular es el veredicto y nada mas
       condicionado  categoria/locus/accion solo cuentan CON el veredicto bien

     FIRMADO 🧑 (20-sep): EL TITULAR ES 'veredicto'. 'condicionado' se sigue
     calculando y publicando, pero es secundario. El motivo es medido, no de
     gusto: el mismo atacante sin cerebro, con categoria, locus y accion
     PERFECTOS en vez de deducidos, pasa de 0,689 a 0,835 en 'condicionado' y
     de 0,835 a 0,835 en 'veredicto'. Con el titular en el veredicto, afinar
     el diff contra la plantilla no vale absolutamente nada; con el titular
     condicionado vale quince puntos. Se elige el que no deja palanca.
  2. Autoprueba (iii) a confianza 0,69 y con UMBRAL ABSOLUTO (< 0,25). La de
     antes exigia "caer al 60 % de la clave perfecta", y eso lo pasaba un
     puntuador con un termino de penalizacion y el resto constante.
  3. Bootstrap POR OPERADOR. La unidad de variacion son los 60 operadores, no
     los 312 casos: los 5 casos de un operador son la misma pregunta con otro
     apellido, asi que remuestrear casos estrecha el intervalo a mentira.
  4. Tasa de falsa alarma aparte, fuera del titular.
  5. (NINGUNA, "") puntua pleno cuando el veredicto verdadero es SIN_PROBLEMA.
     Exigir la categoria de un defecto que se ha juzgado inocuo —y bien— era
     castigar la respuesta correcta.
  6. LA CONFIANZA SALE DEL TITULAR y se mide con una regla propia (Brier). La
     formula vieja solo restaba, nunca sumaba, asi que bajar la confianza a
     0,69 era gratis: el mismo triador sacaba 0,585 con 0,9 y con 0,69, y el
     criterio 3 firmado se cumplia sin hacer nada. Brier es una regla propia:
     se minimiza diciendo la verdad sobre lo que uno sabe, asi que ni inflar
     ni rebajar la confianza sale a cuenta.

LO QUE NO CAMBIA, porque estaba firmado y sigue siendo correcto:
  - Macro-media por clase de veredicto verdadero, nunca micro.
  - Abstenerse (NO_SE) nunca resta.
  - Enmienda 1: en (a) y (c) el ideal es un CONJUNTO, asi que acertar el
    veredicto verdadero en un caso no diagnosticable puntua igual que callarse.
  - Las filas canario no se puntuan.

Uso:
  python3 puntuar2.py tabla_casos.tsv respuestas.tsv [brazo]   # brazo: a|b|c
  python3 puntuar2.py --autopruebas tabla_casos.tsv
  python3 puntuar2.py --tabla tabla_casos.tsv dir_respuestas/  # comparativa
"""
import collections
import io
import os
import random
import sys

MODOS = ("veredicto", "condicionado")
VEREDICTOS_REALES = ("FALLO_MENSAJE", "ENTORNO", "RECHAZO_POLITICA", "SIN_PROBLEMA",
                     "RESULTADO_INCORRECTO_SILENCIOSO")


# ---------------------------------------------------------------------------
# Lectura
# ---------------------------------------------------------------------------
def cargar(ruta):
    with io.open(ruta, encoding="utf-8") as fh:
        cols = fh.readline().rstrip("\n").split("\t")
        return [dict(zip(cols, l.rstrip("\n").split("\t"))) for l in fh if l.strip()]


def ideal(fila, brazo):
    """Conjunto de veredictos que puntuan como acierto en ese brazo."""
    return set(fila[{"a": "ideal_a", "b": "ideal_b", "c": "ideal_c"}[brazo]].split("|"))


def confianza(r):
    try:
        return float(r.get("confianza", 0) or 0)
    except ValueError:
        return 0.0


# ---------------------------------------------------------------------------
# Los tres campos de detalle
# ---------------------------------------------------------------------------
def normalizar_locus(x):
    """ENTORNO:FhirPatient.RutaFhir -> ENTORNO:FhirPatient.

    El nombre del ajuste no es adivinable desde la evidencia que ve el agente,
    asi que exigirlo apuntaba a un punto inalcanzable.
    """
    x = (x or "").strip()
    if x.startswith("ENTORNO:"):
        return "ENTORNO:" + x[8:].split(".")[0]
    return x


def punto_locus(dado, esperado):
    dado, esperado = normalizar_locus(dado), normalizar_locus(esperado)
    if not esperado:
        return 1.0 if not dado else 0.0
    if dado == esperado:
        return 1.0
    if dado and esperado.split(":")[0] == dado.split(":")[0]:
        return 0.5
    return 0.0


def detalle(fila, r):
    """(categoria, locus, accion) en [0,1] cada uno, sin condicionar a nada.

    ARREGLO 5: si el veredicto verdadero es SIN_PROBLEMA, contestar
    (NINGUNA, "") vale lo mismo que nombrar el campo mutado. Las dos son
    respuestas correctas a "aqui no pasa nada": una nombra donde estaba el
    susto y la otra dice que no habia susto. El catalogo guarda la primera
    porque le hace falta para generar; el agente no tiene por que adivinarla.
    """
    inocuo = fila["esperado_veredicto"] == "SIN_PROBLEMA"
    cat_dada = r.get("categoria", "")
    loc_dado = r.get("locus", "")
    if inocuo and cat_dada == "NINGUNA" and not normalizar_locus(loc_dado):
        c, l = 1.0, 1.0
    else:
        c = 1.0 if cat_dada == fila["clase"] else 0.0
        l = punto_locus(loc_dado, fila["locus"])
    a = 1.0 if r.get("accion", "") == fila["esperado_accion"] else 0.0
    return c, l, a


# ---------------------------------------------------------------------------
# EL TITULAR. Sin confianza dentro: ARREGLO 6.
# ---------------------------------------------------------------------------
def puntuar_caso(fila, r, brazo, modo):
    ok = r.get("veredicto", "") in ideal(fila, brazo)
    if modo == "veredicto":
        return 1.0 if ok else 0.0
    # condicionado: los tres faciles solo se cobran con el veredicto bien
    if not ok:
        return 0.0
    if r.get("veredicto", "") == "NO_SE":
        # ARREGLO 7, no pedido por el revisor y encontrado al reescribir esto:
        # la enmienda 1 firmada dice que en (a) y (c), para un caso no
        # diagnosticable desde ese brazo, "puntuan IGUAL NO_SE y el veredicto
        # verdadero". La v1 daba 2 de 5 al que se callaba y 5 de 5 al que
        # acertaba con los tres campos, asi que la enmienda estaba implementada
        # a medias: quito la penalizacion y concedio el termino del veredicto,
        # pero los otros tres puntos seguian separandolos. Aqui una abstencion
        # que cae dentro del ideal vale lo mismo que la respuesta completa,
        # que es lo que se firmo.
        return 1.0
    c, l, a = detalle(fila, r)
    return (2.0 + c + l + a) / 5.0


# ---------------------------------------------------------------------------
# Agregacion y ARREGLO 3: el bootstrap por operador
# ---------------------------------------------------------------------------
def agrupar(filas, resp, brazo, modo):
    """{clase: {operador: [puntuaciones]}} — la unidad es el operador."""
    por = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in filas:
        r = resp.get(f["caso_id"])
        if r is None:
            continue
        por[f["esperado_veredicto"]][f["operador"]].append(
            puntuar_caso(f, r, brazo, modo))
    return por


def macro(por):
    clases = {}
    for k, ops in por.items():
        if not ops:
            continue
        # media de casos dentro del operador, y media de operadores en la clase
        medias = [sum(v) / len(v) for v in ops.values() if v]
        if medias:
            clases[k] = sum(medias) / len(medias)
    return (sum(clases.values()) / len(clases) if clases else 0.0), clases


def bootstrap(por, n=2000, semilla=7):
    """IC 95 % remuestreando OPERADORES dentro de cada clase, no casos.

    Los 5 casos de un operador son el mismo literal con otro apellido: tratarlos
    como 5 observaciones independientes estrecha el intervalo por debajo de lo
    que el juego de datos puede sostener. El revisor lo midio: el IC del regex
    pasa de [0,554 - 0,617] a [0,492 - 0,655] al cambiar la unidad.
    """
    rnd = random.Random(semilla)
    llaves = [k for k, v in por.items() if v]
    if not llaves:
        return 0.0, 0.0
    porclase = {k: [sum(v) / len(v) for v in por[k].values() if v] for k in llaves}
    muestras = []
    for _ in range(n):
        medias = []
        for k in llaves:
            v = porclase[k]
            medias.append(sum(rnd.choice(v) for _ in v) / len(v))
        muestras.append(sum(medias) / len(medias))
    muestras.sort()
    return muestras[int(0.025 * n)], muestras[int(0.975 * n)]


def n_casos(por):
    return sum(len(v) for ops in por.values() for v in ops.values())


def n_ops(por):
    return len(set(o for ops in por.values() for o in ops))


def informe(filas, resp, brazo, modo, titulo, con_ic=True):
    por = agrupar(filas, resp, brazo, modo)
    m, clases = macro(por)
    if con_ic:
        lo, hi = bootstrap(por)
        print("%-32s %.3f  IC95 [%.3f, %.3f]  %d casos / %d operadores"
              % (titulo, m, lo, hi, n_casos(por), n_ops(por)))
    else:
        print("%-32s %.3f  (%d casos / %d operadores)"
              % (titulo, m, n_casos(por), n_ops(por)))
    for k in sorted(clases, key=lambda x: -clases[x]):
        print("      %-32s %.3f  (%d casos / %d op.)"
              % (k, clases[k], sum(len(v) for v in por[k].values()), len(por[k])))
    return m


# ---------------------------------------------------------------------------
# ARREGLO 6: la confianza, medida aparte y con una regla propia
# ---------------------------------------------------------------------------
def calibracion(filas, resp, brazo):
    """Brier sobre el veredicto, y los descriptivos que ya se reportaban.

    Brier = media de (confianza - acierto)^2 sobre los casos en los que el
    agente SE MOJA (NO_SE queda fuera: no ha afirmado nada que calibrar).
    Es una regla PROPIA: su minimo esta en decir la confianza verdadera, asi
    que ni inflarla ni rebajarla a 0,69 sale a cuenta. Cero es perfecto.
    """
    b, n = 0.0, 0
    confiados_mal = abst = 0
    for f in filas:
        r = resp.get(f["caso_id"])
        if r is None:
            continue
        v = r.get("veredicto", "")
        ok = 1.0 if v in ideal(f, brazo) else 0.0
        c = confianza(r)
        if v == "NO_SE":
            abst += 1
        else:
            b += (c - ok) ** 2
            n += 1
        if c >= 0.7 and not ok and v != "NO_SE":
            confiados_mal += 1
    total = sum(1 for f in filas if f["caso_id"] in resp)
    return {"brier": (b / n if n else float("nan")), "n_brier": n,
            "error_confiado": 100.0 * confiados_mal / total if total else 0.0,
            "abstencion": 100.0 * abst / total if total else 0.0}


def falsa_alarma(filas, resp, brazo):
    """ARREGLO 4: cuantas veces se acusa a un mensaje que no tiene nada.

    Fuera del titular por la enmienda 2 firmada. Aqui se reporta entera y
    tambien partida por si el agente acusa de silencioso o de otra cosa.
    """
    limpios = [f for f in filas if f["esperado_veredicto"] == "SIN_PROBLEMA"]
    acusa = collections.Counter()
    for f in limpios:
        r = resp.get(f["caso_id"])
        if r is None:
            continue
        v = r.get("veredicto", "")
        if v not in ("SIN_PROBLEMA", "NO_SE"):
            acusa[v] += 1
    n = sum(1 for f in limpios if f["caso_id"] in resp)
    return (100.0 * sum(acusa.values()) / n if n else 0.0), n, acusa


# ---------------------------------------------------------------------------
# EL SUBCONJUNTO DEL CRITERIO 1 (paso 2 del plan de arreglo)
#
# El criterio 1 firmado dice "+15 puntos sobre el subconjunto DONDE EL REGEX
# FALLA". Ese subconjunto no se escribe a mano: se DERIVA de las respuestas de
# la barra, que estan congeladas por hash. Asi no hay forma de moverlo despues
# de ver como le fue al agente.
#
# Encima se descuentan dos cosas, declaradas de antemano en `subconjuntos.tsv`:
#   INGANABLE        nada de lo que ve el brazo (b) permite acertarlo. Dejarlos
#                    dentro seria exigirle al agente que adivine.
#   PENDIENTE_PASO3  lo medido no es lo que vera el agente. Se reportan aparte
#                    hasta que el paso 3 los rehaga o los excluya.
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# EL CRITERIO 1, versión firmada 🧑 el 20-sep tras la revisión externa.
#
# QUE CAMBIA Y POR QUE. Antes el subconjunto era "donde falla la barra" y el
# suelo era "la mejor respuesta constante". Tres revisiones externas seguidas
# encontraron que eso es pasable sin razonar; la ultima con una regla de UNA
# LINEA —"ACK positivo -> SILENCIOSO, ACK negativo -> FALLO_MENSAJE"— que saca
# +0,333 y cumple. El error de concepto:
#
#     «donde falla la barra» NO ES «donde hace falta razonar»
#
# Un atacante no tiene que repetir los fallos de esa barra; le basta con tener
# otros. Y cada vez que se corregia la clave, el subconjunto se movia y
# aparecia una grieta nueva.
#
# (1) EL SUBCONJUNTO SE PRE-REGISTRA POR CONSTRUCCION, en
#     `subconjunto_criterio1.tsv`, que genera `subconjunto_constructivo.py`:
#     los operadores cuya FIRMA OBSERVABLE coincide con la de otro operador de
#     veredicto distinto. Si dos casos producen el mismo ACK, el mismo ERR-3,
#     los mismos tipos de log y la misma forma del canonico, y la verdad es
#     distinta, NINGUNA regla sobre esas senales puede separarlos. No se
#     menciona ninguna linea base: se calcula de la tabla y de lo medido.
#
# (2) EL SUELO ES EL MAXIMO DE TODO EL BANCO DE ADVERSARIOS, recalculado en
#     cada tanda, mas las respuestas constantes. Asi la estrategia N+1 SUBE EL
#     LISTON en vez de colarse por el: el dia que alguien encuentre otra, se
#     mete en el banco y el criterio se endurece solo.
#
# Del suelo se excluyen los que contestan MIRANDO LA CLAVE (la clave barajada,
# las filas barajadas, el techo del arbol de locus): son autopruebas, no
# atacantes, y un atacante no tiene la clave. Se reportan aparte.
# ---------------------------------------------------------------------------
USAN_CLAVE = ("clave_barajada", "filas_barajadas", "e13_techo")


def cargar_subconjunto(filas, ruta):
    """Los casos de los operadores pre-registrados. Aborta si falta el fichero:
    sin subconjunto declarado no hay criterio 1 que calcular."""
    if not os.path.exists(ruta):
        print("ABORTA: no existe %s. El subconjunto del criterio 1 se declara"
              " ANTES de correr, no se deduce despues." % ruta)
        raise SystemExit(4)
    ops = set(r["operador"] for r in cargar(ruta))
    return [f for f in filas if f["operador"] in ops], ops


def suelo_adversarial(sub, brazo, dir_banco):
    """(mejor, nombre, {nombre: macro}) sobre el subconjunto.

    Entran todos los ficheros del banco que no usen la clave, y las cinco
    respuestas constantes, que son el atacante mas tonto posible.
    """
    marcas = {}
    for v in VEREDICTOS_REALES:
        cte = {f["caso_id"]: {"veredicto": v} for f in sub}
        marcas["constante:" + v] = cte
    if os.path.isdir(dir_banco):
        for nombre in sorted(os.listdir(dir_banco)):
            if not nombre.endswith(".tsv"):
                continue
            corto = nombre[len("respuestas_"):-len(".tsv")]
            if any(x in corto for x in USAN_CLAVE) or corto.startswith("techo_"):
                continue
            resp = {r["caso_id"]: r for r in cargar(os.path.join(dir_banco, nombre))}
            if all(f["caso_id"] in resp for f in sub):
                marcas[corto] = resp
    notas = {}
    for nombre, resp in marcas.items():
        m, _ = macro(agrupar(sub, resp, brazo, "veredicto"))
        notas[nombre] = m
    mejor = max(notas, key=lambda k: notas[k])
    return notas[mejor], mejor, notas, marcas[mejor]


def informe_criterio1(filas, resp, brazo, ruta_sub, dir_banco):
    sub, ops = cargar_subconjunto(filas, ruta_sub)
    print()
    print("### CRITERIO 1 — SUBCONJUNTO PRE-REGISTRADO Y SUELO ADVERSARIAL")
    print("  %s: %d casos en %d operadores" % (ruta_sub, len(sub), len(ops)))
    print("  (firmas observables que NO separan el veredicto: ninguna regla")
    print("   sobre el ACK, el ERR-3, el log o la forma del canonico las parte)")

    suelo, quien, notas, resp_suelo = suelo_adversarial(sub, brazo, dir_banco)
    print()
    print("  EL SUELO = el mejor del banco de adversarios (%d estrategias):" % len(notas))
    for k in sorted(notas, key=lambda x: -notas[x])[:6]:
        print("      %-34s %.3f%s" % (k, notas[k], "   <- SUELO" if k == quien else ""))
    print()
    ma = informe(sub, resp, brazo, "veredicto", "  EL AGENTE aqui")
    pora = agrupar(sub, resp, brazo, "veredicto")
    _, clases = macro(pora)
    lo, hi = bootstrap_diferencia(pora, agrupar(sub, resp_suelo, brazo, "veredicto"))
    con = sum(1 for x in clases.values() if x > 0)
    cumple = (ma - suelo) > 0.15 and lo > 0 and con >= 2
    print()
    print("  VENTAJA SOBRE EL SUELO  %+.3f   IC95 [%+.3f, %+.3f]" % (ma - suelo, lo, hi))
    print("  acierta en %d de las %d clases del subconjunto" % (con, len(clases)))
    print("  -> CRITERIO 1: %s" % ("CUMPLE" if cumple else "NO CUMPLE"))
    return ma - suelo


def bootstrap_diferencia(por_a, por_b, n=2000, semilla=7):
    """IC de la DIFERENCIA, remuestreando los mismos operadores en los dos.

    Emparejado: si se remuestrean por separado, el intervalo sale mas ancho de
    lo que es, porque las dos medidas comparten los mismos casos.
    """
    rnd = random.Random(semilla)
    llaves = [k for k in por_a if por_a[k]]
    if not llaves:
        return 0.0, 0.0
    muestras = []
    for _ in range(n):
        da = []
        for k in llaves:
            ops = list(por_a[k])
            elegidos = [rnd.choice(ops) for _ in ops]
            ma = sum(sum(por_a[k][o]) / len(por_a[k][o]) for o in elegidos) / len(elegidos)
            mb = sum(sum(por_b[k][o]) / len(por_b[k][o]) for o in elegidos) / len(elegidos)
            da.append(ma - mb)
        muestras.append(sum(da) / len(da))
    muestras.sort()
    return muestras[int(0.025 * n)], muestras[int(0.975 * n)]


def faciles(filas, resp):
    """Los tres campos que ya NO entran en el titular, medidos igualmente.

    Se siguen imprimiendo porque son informativos y porque su distancia con el
    titular es la senal de alarma: un agente que clava locus y categoria y
    falla el veredicto esta reconociendo la plantilla, no triando.
    """
    c = l = a = n = 0.0
    for f in filas:
        r = resp.get(f["caso_id"])
        if r is None:
            continue
        dc, dl, da = detalle(f, r)
        c, l, a, n = c + dc, l + dl, a + da, n + 1
    return (c / n, l / n, a / n, int(n)) if n else (0.0, 0.0, 0.0, 0)


# ---------------------------------------------------------------------------
# LAS AUTOPRUEBAS. Sin ellas el puntuador es el "All PASSED" con cero pruebas.
# La v1 pasaba las suyas y no medía triaje: las de aqui son las que habria
# hecho falta pasar, y dos de ellas son adversarios reales, no barajados.
# ---------------------------------------------------------------------------
UMBRAL_AZAR = 0.25


def autopruebas(filas):
    print("=" * 78)
    print("AUTOPRUEBAS DEL PUNTUADOR v2")
    print("=" * 78)
    puntua = [f for f in filas if f["puntua"] == "1"]
    fallos = []

    def resultado(etiqueta, ok, extra=""):
        print("  %-58s %s %s" % (etiqueta, "OK   " if ok else "FALLA", extra))
        if not ok:
            fallos.append(etiqueta)

    # (i) respuestas incompletas -> aborta
    parciales = {f["caso_id"]: {"veredicto": f["esperado_veredicto"]}
                 for f in puntua[:len(puntua) // 2]}
    try:
        comprobar_completo(puntua, parciales)
        resultado("(i)   respuestas incompletas -> aborta", False)
    except SystemExit:
        resultado("(i)   respuestas incompletas -> aborta", True)

    def clave(f, veredicto=None, conf="0.9"):
        return {"veredicto": veredicto or f["esperado_veredicto"],
                "categoria": f["clase"], "locus": f["locus"],
                "accion": f["esperado_accion"], "confianza": conf}

    for modo in MODOS:
        print("  --- modo %s ---" % modo)

        # (ii) clave perfecta -> 100 %
        perfecta = {f["caso_id"]: clave(f) for f in puntua}
        m2, _ = macro(agrupar(puntua, perfecta, "b", modo))
        resultado("(ii)  clave perfecta -> 1,000", m2 > 0.999, "(%.3f)" % m2)

        # (iii) clave barajada A CONFIANZA 0,69 -> por debajo de un umbral
        #       ABSOLUTO. La v1 pedia "cae al 60 % de la perfecta", que lo
        #       pasa cualquier puntuador con un termino de penalizacion.
        rnd = random.Random(11)
        orden = [f["esperado_veredicto"] for f in puntua]
        rnd.shuffle(orden)
        barajada = {f["caso_id"]: clave(f, v, "0.69") for f, v in zip(puntua, orden)}
        m3, _ = macro(agrupar(puntua, barajada, "b", modo))
        resultado("(iii) clave barajada a conf 0,69 -> < %.2f" % UMBRAL_AZAR,
                  m3 < UMBRAL_AZAR, "(%.3f)" % m3)

        # (iv) EL PEREZOSO CON LOS TRES FACILES REGALADOS. Este es el control
        #      que la v1 no tenia y que le costo la vida: contesta siempre
        #      SIN_PROBLEMA y acierta categoria, locus y accion SIEMPRE. En la
        #      v1 sacaba 0,680 y ganaba al regex.
        perezoso = {f["caso_id"]: clave(f, "SIN_PROBLEMA", "0.69") for f in puntua}
        m4, _ = macro(agrupar(puntua, perezoso, "b", modo))
        resultado("(iv)  perezoso con cat/locus/accion regalados -> < %.2f" % UMBRAL_AZAR,
                  m4 < UMBRAL_AZAR, "(%.3f)" % m4)

        # (v) LA CONFIANZA NO PUEDE MOVER EL TITULAR. Si mover 0,9 -> 0,69
        #     cambia la nota, la confianza vuelve a ser una palanca gratis.
        alta = {f["caso_id"]: clave(f, "SIN_PROBLEMA", "0.9") for f in puntua}
        m5, _ = macro(agrupar(puntua, alta, "b", modo))
        resultado("(v)   bajar la confianza no mueve el titular",
                  abs(m5 - m4) < 1e-9, "(%.3f vs %.3f)" % (m5, m4))

    # (vi) Y SI LA MUEVE EN LA CALIBRACION: Brier tiene que castigar al que
    #      rebaja la confianza cuando acierta. Es la otra mitad del arreglo 6.
    print("  --- calibracion ---")
    acierta_09 = {f["caso_id"]: clave(f, conf="0.9") for f in puntua}
    acierta_069 = {f["caso_id"]: clave(f, conf="0.69") for f in puntua}
    b9 = calibracion(puntua, acierta_09, "b")["brier"]
    b69 = calibracion(puntua, acierta_069, "b")["brier"]
    resultado("(vi)  rebajar la confianza acertando empeora el Brier",
              b69 > b9, "(0,69 -> %.3f  frente a  0,9 -> %.3f)" % (b69, b9))

    # (vii) y tiene que castigar tambien al que la infla equivocandose
    rnd = random.Random(5)
    orden = [f["esperado_veredicto"] for f in puntua]
    rnd.shuffle(orden)
    mal_09 = {f["caso_id"]: clave(f, v, "0.9") for f, v in zip(puntua, orden)}
    mal_05 = {f["caso_id"]: clave(f, v, "0.5") for f, v in zip(puntua, orden)}
    b_m9 = calibracion(puntua, mal_09, "b")["brier"]
    b_m5 = calibracion(puntua, mal_05, "b")["brier"]
    resultado("(vii) inflar la confianza fallando empeora el Brier",
              b_m9 > b_m5, "(0,9 -> %.3f  frente a  0,5 -> %.3f)" % (b_m9, b_m5))

    # (viii) ENMIENDA 1, que la v1 cumplia a medias: en el brazo (a), callarse
    #        en un caso no diagnosticable tiene que valer LO MISMO que acertar
    #        el veredicto verdadero con los tres campos bien.
    print("  --- enmienda 1 ---")
    nodiag = [f for f in puntua if "NO_SE" in ideal(f, "a")]
    callado = {f["caso_id"]: {"veredicto": "NO_SE", "categoria": "", "locus": "",
                              "accion": "", "confianza": "0.3"} for f in nodiag}
    completo = {f["caso_id"]: clave(f) for f in nodiag}
    for modo in MODOS:
        mc, _ = macro(agrupar(nodiag, callado, "a", modo))
        mp, _ = macro(agrupar(nodiag, completo, "a", modo))
        resultado("(viii) [%s] callarse == acertar donde no se puede saber" % modo[:4],
                  abs(mc - mp) < 1e-9, "(%.3f vs %.3f, %d casos)"
                  % (mc, mp, len(nodiag)))

    # (ix) el canario no se puntua
    can = [f for f in filas if f["puntua"] == "0"]
    resultado("(ix)  filas canario fuera de la puntuacion", bool(can),
              "(%d)" % len(can))

    print()
    if fallos:
        print("EL PUNTUADOR ESTA ROTO:")
        for f in fallos:
            print("   -", f)
        return 1
    print("Las %d autopruebas pasan en los dos modos." % (len(MODOS) * 5 + 4))
    return 0


# ---------------------------------------------------------------------------
# EL CANARIO, sobre la salida CRUDA (arreglo 4 del informe, paso 4 del plan)
#
# El canario de la v1 buscaba el literal en el campo `veredicto` de la
# respuesta YA VALIDADA. No podia saltar nunca: el esquema es cerrado y
# CANARIO_TABLA no esta en el enum, asi que el reintento de validacion lo
# borraba antes de llegar aqui. Un control negativo que no puede dispararse
# no es un control: es un adorno que da tranquilidad.
#
# Ahora se busca el literal en TODO lo que el modelo escribio, y en especial
# en la columna `crudo`, que es la salida tal cual sale del modelo ANTES de
# validar el esquema. Quien escriba el ejecutor de la tanda tiene que
# rellenarla.
#
# Y si esa columna NO ESTA, no se dice que el canario paso: se dice que NO SE
# HA PODIDO COMPROBAR. Un verde que no se ha medido es peor que un rojo.
# ---------------------------------------------------------------------------
LITERAL_CANARIO = "CANARIO_TABLA"


def revisar_canario(resp):
    if not resp:
        return False
    hay_crudo = any("crudo" in r for r in resp.values())
    tocados = [cid for cid, r in resp.items()
               if any(LITERAL_CANARIO in str(v) for v in r.values())]
    if tocados:
        print("!! CANARIO EMITIDO en %d respuestas (p.ej. %s): ha leido la tabla."
              % (len(tocados), tocados[0]))
        print("   TANDA INVALIDADA.")
        return True
    if not hay_crudo:
        print("!! EL CANARIO NO SE HA PODIDO COMPROBAR: las respuestas no traen")
        print("   columna 'crudo' con la salida sin validar. El esquema cerrado")
        print("   borra CANARIO_TABLA antes de que llegue aqui, asi que sin esa")
        print("   columna el control no existe. NO se puede publicar que paso.")
    return False


def comprobar_completo(filas, resp):
    faltan = [f["caso_id"] for f in filas if f["caso_id"] not in resp]
    if faltan:
        print("ABORTA: faltan %d respuestas de %d casos (p.ej. %s)"
              % (len(faltan), len(filas), faltan[0]))
        raise SystemExit(2)


# ---------------------------------------------------------------------------
# Comparativa: todas las respuestas de un directorio, en una tabla
# ---------------------------------------------------------------------------
def comparativa(tabla, dirs, brazo="b"):
    filas = [f for f in cargar(tabla) if f["puntua"] == "1"]
    rutas = []
    for d in dirs:
        if os.path.isdir(d):
            rutas += [os.path.join(d, x) for x in sorted(os.listdir(d))
                      if x.endswith(".tsv")]
        else:
            rutas.append(d)
    sil = [f for f in filas if f["esperado_deteccion"] == "SILENCIO"]
    print("%-26s %-15s %-15s %8s %7s %7s %7s %7s"
          % ("estrategia", "veredicto", "condicionado", "silenc.", "Brier",
             "falsa", "conf.mal", "abst."))
    print("-" * 104)
    for ruta in rutas:
        resp = {r["caso_id"]: r for r in cargar(ruta)}
        if any(f["caso_id"] not in resp for f in filas):
            continue
        celdas = []
        for modo in MODOS:
            por = agrupar(filas, resp, brazo, modo)
            m, _ = macro(por)
            lo, hi = bootstrap(por)
            celdas.append("%.3f[%.2f-%.2f]" % (m, lo, hi))
        ms, _ = macro(agrupar(sil, resp, brazo, "veredicto"))
        cal = calibracion(filas, resp, brazo)
        fa, _, _ = falsa_alarma(filas, resp, brazo)
        print("%-26s %-15s %-15s %8.3f %7.3f %6.1f%% %7.1f%% %6.1f%%"
              % (os.path.basename(ruta)[len("respuestas_"):-len(".tsv")],
                 celdas[0], celdas[1], ms, cal["brier"], fa,
                 cal["error_confiado"], cal["abstencion"]))
    return 0


def main():
    if sys.argv[1] == "--autopruebas":
        return autopruebas(cargar(sys.argv[2]))
    if sys.argv[1] == "--tabla":
        return comparativa(sys.argv[2], sys.argv[3:])

    argv = list(sys.argv)
    if "--barra" in argv:
        i = argv.index("--barra")
        del argv[i:i + 2]
        print("(--barra se ignora desde el 20-sep: el subconjunto del criterio 1"
              " ya no se deriva de una linea base, se pre-registra)")
    filas = [f for f in cargar(argv[1]) if f["puntua"] == "1"]
    resp = {r["caso_id"]: r for r in cargar(argv[2])}
    brazo = argv[3] if len(argv) > 3 else "b"

    if revisar_canario(resp):
        return 3
    comprobar_completo(filas, resp)

    print("=" * 78)
    print("PUNTUACION  brazo (%s)   %d casos / %d operadores"
          % (brazo, len(filas), len(set(f["operador"] for f in filas))))
    print("=" * 78)
    duros = [f for f in filas if f["severidad"] in ("2", "3")]
    cm = [f for f in filas if f["contra_memoria"] == "1"]
    sil = [f for f in filas if f["esperado_deteccion"] == "SILENCIO"]

    for modo in MODOS:
        print()
        print("### %s — MODO '%s'"
              % ("TITULAR FIRMADO" if modo == "veredicto" else "SECUNDARIO",
                 modo.upper()))
        informe(filas, resp, brazo, modo, "TOTAL")
        print()
        informe(duros, resp, brazo, modo, "severidad >= 2", con_ic=False)
        if cm:
            informe(cm, resp, brazo, modo, "contra-memoria", con_ic=False)
        if sil:
            informe(sil, resp, brazo, modo, "fallos silenciosos", con_ic=False)

    base = os.path.dirname(os.path.abspath(argv[1]))
    informe_criterio1(filas, resp, brazo,
                      os.path.join(base, "subconjunto_criterio1.tsv"),
                      os.path.join(base, "adversarios"))

    print()
    print("### FUERA DEL TITULAR (arreglos 4 y 6)")
    cal = calibracion(filas, resp, brazo)
    print("  Brier del veredicto   %.3f   (0 perfecto; regla propia, sobre %d "
          "casos en los que se moja)" % (cal["brier"], cal["n_brier"]))
    print("  error confiado        %.1f %%   (descriptivo: conf >= 0,7 y mal)"
          % cal["error_confiado"])
    print("  abstencion            %.1f %%" % cal["abstencion"])
    fa, nfa, acusa = falsa_alarma(filas, resp, brazo)
    print("  falsa alarma          %.1f %%   (%d casos limpios)" % (fa, nfa))
    for k, v in acusa.most_common():
        print("        acusa de %-32s %d" % (k, v))

    c, l, a, n = faciles(filas, resp)
    print()
    print("### LOS TRES CAMPOS FACILES, medidos pero YA NO en el titular")
    print("  categoria %.3f   locus %.3f   accion %.3f   (%d casos)" % (c, l, a, n))
    print("  Si estos tres son altos y el titular en modo 'veredicto' es bajo,")
    print("  lo que hay delante es un reconocedor de plantillas, no un triador.")

    print()
    print("### ABSTENCION POR CLASE DE VEREDICTO VERDADERO")
    print("   (si se concentra en una clase, esa clase no es observable con")
    print("    estas herramientas: es un dato del arnes, no del agente)")
    porclase = collections.defaultdict(lambda: [0, 0])
    for f in filas:
        d = porclase[f["esperado_veredicto"]]
        d[1] += 1
        if resp[f["caso_id"]].get("veredicto") == "NO_SE":
            d[0] += 1
    for k in sorted(porclase, key=lambda x: -porclase[x][0] / porclase[x][1]):
        nn, t = porclase[k]
        print("      %-34s %5.1f %%  (%d de %d)" % (k, 100.0 * nn / t, nn, t))

    print()
    print("### CAUSAS DE LAS ABSTENCIONES (no puntuan, pero explican el fallo)")
    vistas = 0
    for f in filas:
        r = resp[f["caso_id"]]
        if r.get("veredicto") == "NO_SE" and r.get("causa", "").strip():
            print("      [%s] %s" % (f["esperado_veredicto"][:18], r["causa"][:92]))
            vistas += 1
            if vistas >= 12:
                break
    return 0


if __name__ == "__main__":
    sys.exit(main())
