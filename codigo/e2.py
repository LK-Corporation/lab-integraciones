# -*- coding: utf-8 -*-
"""E2 medido sobre A: hay algun fallo que el agente detecte y ninguna regla?

LA PREGUNTA, y la plantea la quinta revision de la ronda B. Todo fallo cae en una
de tres clases respecto al BUNDLE que recibe un brazo (mensaje, recorrido con el
canonico y el ACK, y log):

    E1  en el bundle y expresable como predicado
    E2  en el bundle y NO expresable como predicado  <- la unica que rescata la fase
    E3  fuera del bundle: nadie lo detecta

La revision sostiene que E2 puede estar vacia, y da un prior de cero clasificando
a mano los diez fallos reales de la bitacora. Pero E2 se puede MEDIR, hoy, sobre A
y con lo que ya esta corrido:

    v3-invariante  reglas escritas SOLO con el contrato publicado
    v3-completo    reglas escritas conociendo el catalogo entero
    agente         el brazo B de la Fase 12, con sus tres herramientas
    generico       el prompt de 1.174 caracteres del paso 29

    lo detecta v3-invariante                  -> E1, y con el contrato basta
    solo v3-completo                          -> E1, pero hay que ver el catalogo
    el agente SI y NINGUNA regla              -> E2, y la fase tiene sentido
    no lo detecta nadie                       -> E3 o E0

Que la lista de E2 salga vacia no demuestra que la clase sea vacia -podria ser que
a quien escribio las reglas no se le ocurriera-, pero es el control negativo del
argumento de la revision, y es el prior con el que se decide si hay Fase 13.

Mismo criterio de acierto que brazos_analizar.py. Comprobacion de que coincide: el
paso 29 publico "16 de 18 operadores a 8/8" para v3-completo, y eso es lo que tiene
que salir en su columna.

Uso: python3 e2.py
"""
import collections
import csv
import io

CLAVE = "desarrollo/tabla_casos_v2.tsv"
RIS = "RESULTADO_INCORRECTO_SILENCIOSO"

BRAZOS = [("agente", "agente/brazo_B.tsv"),
          ("v3-invariante", "brazos/v3_invariante.tsv"),
          ("v3-completo", "brazos/v3_real.tsv"),
          ("generico", "brazos/generico.tsv")]


def lee(ruta):
    return {x["caso_id"]: x for x in
            csv.DictReader(io.open(ruta, encoding="utf-8"), delimiter="\t")}


clave = {f["caso_id"]: f for f in
         csv.DictReader(io.open(CLAVE, encoding="utf-8"), delimiter="\t")
         if f["puntua"] == "1"}
arm = {n: lee(r) for n, r in BRAZOS}

print("casos puntuables: %d" % len(clave))
for n, _ in BRAZOS:
    print("  %-14s %d filas, %d casan con la clave"
          % (n, len(arm[n]), len(set(arm[n]) & set(clave))))


def ok(n, cid, f):
    acept = (f.get("ideal_b") or f["esperado_veredicto"])
    return arm[n].get(cid, {}).get("veredicto", "") in acept.split("|")


d = collections.defaultdict(lambda: collections.defaultdict(int))
tot = collections.Counter()
for cid, f in clave.items():
    if f["esperado_veredicto"] != RIS:
        continue
    op = f["operador"]
    tot[op] += 1
    for n, _ in BRAZOS:
        if ok(n, cid, f):
            d[op][n] += 1

print()
print("=" * 94)
print("FALLO SILENCIOSO, POR OPERADOR - aciertos de cada brazo")
print("=" * 94)
print("%-34s %5s %7s %7s %8s %8s  %s"
      % ("operador", "n", "agente", "v3-inv", "v3-comp", "generico", "clase"))

cls = collections.defaultdict(list)
for op in sorted(tot, key=lambda o: (-d[o]["v3-invariante"], -d[o]["v3-completo"],
                                     -d[o]["agente"], o)):
    n, ag = tot[op], d[op]["agente"]
    inv, comp = d[op]["v3-invariante"], d[op]["v3-completo"]
    if inv > 0:
        c = "C1 contrato"
    elif comp > 0:
        c = "C2 catalogo"
    elif ag > 0:
        c = "C3 <<<"
    else:
        c = "O0"
    cls[c].append((op, ag, n))
    print("%-34s %5d %7d %7d %8d %8d  %s"
          % (op, n, ag, inv, comp, d[op]["generico"], c))

print()
print("=" * 94)
print("LA CLASIFICACION")
print("=" * 94)
print("C1 contrato  lo detecta v3-invariante, escrito SOLO con el contrato")
print("             publicado: expresable por cualquiera con el contrato    %2d"
      % len(cls["C1 contrato"]))
print("C2 catalogo  v3-invariante NO, v3-completo SI: expresable como")
print("             predicado, pero solo se te ocurre viendo el catalogo    %2d"
      % len(cls["C2 catalogo"]))
print("C3           el agente lo detecta y NINGUNA regla lo hace. Es la")
print("             unica clase que justificaria una Fase 13               %2d"
      % len(cls["C3 <<<"]))
print("O0           no lo detecta nadie: la evidencia no esta en el bundle  %2d"
      % len(cls["O0"]))

for c in ("C2 catalogo", "C3 <<<", "O0"):
    if cls[c]:
        print()
        print("  %s:" % c)
        for op, ag, n in cls[c]:
            print("     %-34s agente %d/%d" % (op, ag, n))

print()
print("=" * 94)
print("RESULTADO: operadores donde el agente detecta y NINGUN juego de reglas lo")
print("           hace: %d de %d." % (len(cls["C3 <<<"]), len(tot)))
print()
print("Cero OBSERVADO no es probabilidad cero: la cota superior unilateral al 95%")
print("es 1-0,05^(1/18) = 15,3%, y eso suponiendo los 18 operadores independientes")
print("y representativos, que es falso. Con dependencia por familia, peor.")
print()
print("Medido sobre A, que es un banco de mutaciones declarativas y por tanto el")
print("terreno mas favorable posible a las reglas. NO decide si E2 existe en un")
print("corpus emergente. Si da el PRIOR con el que decidir si hay Fase 13, y lo da")
print("con un numero en vez de con una lectura a mano de diez flecos.")
