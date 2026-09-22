#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EL APRENDIZ: el adivinador que pide el apartado 8.4 del informe.

QUE ES. Un arbol de decision, no un modelo de lenguaje, entrenado SOLO con lo
que el arnes devuelve. Sirve para una cosa que un modelo no puede hacer bien:
**demostrar que por un tubo se cuela informacion que no deberia estar ahi**.
Un modelo que acierta puede estar razonando; un arbol de tres hojas sobre una
marca de tiempo no razona nada, asi que si acierta, hay fuga.

QUE SE SOSPECHA. El arnes ya usa identificadores de traza OPACOS justamente
para no filtrar el orden de envio. Pero el orden se cuela igual por otros dos
sitios que nadie miro:

  1. Las marcas de tiempo del Event Log son ABSOLUTAS y crecen con el envio.
  2. El texto del log lleva el id del recurso FHIR ("id=2704"), que es un
     contador y tambien crece.

Los operadores no se enviaron barajados del todo —los de ENTORNO van juntos al
final, porque habia que romper el entorno para provocarlos—, asi que "envio
tarde => ENTORNO" puede ser una regla ganadora sin mirar el mensaje.

COMO SE MIDE. Se entrena SOLO con las dos variables sospechosas, en la
particion de CALIBRACION, y se mide en la de EVALUACION. Si un arbol con esas
dos columnas predice el veredicto mejor que la clase mayoritaria, la fuga
existe y hay cuanta es.

Uso:
  python3 aprendiz.py tabla.tsv          # mide la fuga
"""
import collections
import io
import sys

sys.path.insert(0, ".")
import lab
import puntuar2 as P


def a_segundos(t):
    """'2026-09-20 17:26:35.443' -> segundos desde el arranque del dia."""
    try:
        hms = str(t).split(" ")[1]
        h, m, s = hms.split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)
    except (IndexError, ValueError):
        return -1.0


def rasgos():
    """Por sesion: (primera marca de tiempo, mayor id de recurso del log)."""
    t0 = {}
    for f in lab.consulta("SELECT SessionId AS ses, MIN(TimeLogged) AS t "
                          "FROM Ens_Util.Log GROUP BY SessionId"):
        t0[str(f["ses"])] = a_segundos(f["t"])
    rec = collections.defaultdict(lambda: -1)
    for f in lab.consulta("SELECT SessionId AS ses, Text AS txt FROM Ens_Util.Log"):
        for trozo in str(f["txt"] or "").split("id="):
            n = ""
            for c in trozo:
                if c.isdigit():
                    n += c
                else:
                    break
            if n:
                rec[str(f["ses"])] = max(rec[str(f["ses"])], int(n))
    return t0, rec


# ---------------------------------------------------------------------------
# Un arbol de decision minimo. Sin dependencias: solo cortes por umbral.
# ---------------------------------------------------------------------------
def gini(etiquetas):
    n = len(etiquetas)
    if not n:
        return 0.0
    c = collections.Counter(etiquetas)
    return 1.0 - sum((v / n) ** 2 for v in c.values())


def mejor_corte(filas, columnas):
    base, n = gini([y for _, y in filas]), len(filas)
    mejor = None
    for col in columnas:
        valores = sorted(set(x[col] for x, _ in filas))
        for i in range(len(valores) - 1):
            umbral = (valores[i] + valores[i + 1]) / 2.0
            izq = [(x, y) for x, y in filas if x[col] <= umbral]
            der = [(x, y) for x, y in filas if x[col] > umbral]
            if not izq or not der:
                continue
            g = (len(izq) * gini([y for _, y in izq])
                 + len(der) * gini([y for _, y in der])) / n
            if mejor is None or g < mejor[0]:
                mejor = (g, col, umbral, izq, der)
    if mejor is None or mejor[0] >= base - 1e-9:
        return None
    return mejor


def entrenar(filas, columnas, profundidad=3, minimo=8):
    mayoria = collections.Counter(y for _, y in filas).most_common(1)[0][0]
    if profundidad == 0 or len(filas) < minimo or gini([y for _, y in filas]) == 0:
        return ("hoja", mayoria)
    corte = mejor_corte(filas, columnas)
    if corte is None:
        return ("hoja", mayoria)
    _, col, umbral, izq, der = corte
    return ("nodo", col, umbral,
            entrenar(izq, columnas, profundidad - 1, minimo),
            entrenar(der, columnas, profundidad - 1, minimo))


def predecir(arbol, x):
    while arbol[0] == "nodo":
        arbol = arbol[3] if x[arbol[1]] <= arbol[2] else arbol[4]
    return arbol[1]


def dibujar(arbol, sangria="      "):
    if arbol[0] == "hoja":
        print("%s-> %s" % (sangria, arbol[1]))
        return
    print("%ssi %s <= %.1f:" % (sangria, arbol[1], arbol[2]))
    dibujar(arbol[3], sangria + "   ")
    print("%ssi no:" % sangria)
    dibujar(arbol[4], sangria + "   ")


def macro(pares):
    por = collections.defaultdict(list)
    for verdad, dado in pares:
        por[verdad].append(1.0 if dado == verdad else 0.0)
    return sum(sum(v) / len(v) for v in por.values()) / len(por)


def main():
    tabla = sys.argv[1] if len(sys.argv) > 1 else "tabla_casos_v2.tsv"
    filas = [f for f in P.cargar(tabla) if f["puntua"] == "1"]
    bloque = {b["caso_id"]: b for b in P.cargar("bloqueC_total.tsv")}
    t0, rec = rasgos()

    datos = {"CALIBRACION": [], "EVALUACION": []}
    for f in filas:
        ses = bloque.get(f["caso_id"], {}).get("session_id", "")
        if not ses:
            continue
        datos[f["particion"]].append(
            ({"reloj": t0.get(ses, -1.0), "id_recurso": float(rec.get(ses, -1))},
             f["esperado_veredicto"]))

    cols = ["reloj", "id_recurso"]
    print("=" * 84)
    print("EL APRENDIZ — cuanta informacion se cuela por el reloj y el contador")
    print("=" * 84)
    print("entrena en CALIBRACION (%d casos), mide en EVALUACION (%d casos)"
          % (len(datos["CALIBRACION"]), len(datos["EVALUACION"])))
    print("y SOLO ve dos numeros: la primera marca de tiempo del log y el mayor")
    print("id de recurso FHIR que aparece en su texto. Nada del mensaje.")
    print()

    may = collections.Counter(y for _, y in datos["CALIBRACION"]).most_common(1)[0][0]
    base = macro([(y, may) for _, y in datos["EVALUACION"]])
    print("  clase mayoritaria (%s)            macro %.3f" % (may[:22], base))

    for combinacion in (["reloj"], ["id_recurso"], cols):
        arbol = entrenar(datos["CALIBRACION"], combinacion)
        m = macro([(y, predecir(arbol, x)) for x, y in datos["EVALUACION"]])
        print("  arbol sobre %-24s macro %.3f%s"
              % ("+".join(combinacion), m,
                 "   <<< FUGA" if m > base + 0.05 else ""))
    print()
    print("  el arbol de los dos rasgos, entero:")
    dibujar(entrenar(datos["CALIBRACION"], cols))
    return 0


if __name__ == "__main__":
    sys.exit(main())
