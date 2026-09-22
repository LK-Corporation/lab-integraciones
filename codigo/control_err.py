# -*- coding: utf-8 -*-
"""EL CONTROL QUE DECIDE: un ERR correcto contra uno incorrecto.

La primera comparacion estaba confundida y hay que decirlo: los acuses limpios
NO LLEVAN SEGMENTO ERR, asi que cualquier hallazgo sobre el ERR crea una
diferencia con los limpios que no es deteccion. Un detector que dispare con "hay
ERR" acierta el 100% sin entender nada — que es el modo de fallo F8 del diseno,
aqui dentro del propio oraculo.

La pregunta buena: ¿distingue el comprobador un codigo CORRECTO de uno
INCORRECTO en la misma situacion? Se construyen las variantes corregidas:

    SEG_ORDEN_PV1_ANTES_PID   101 "Required field missing" -> 100 "Segment
                              sequence error", que es el correcto segun el
                              estandar cuando el PID va fuera de sitio
    ENV_FHIR_*                102 "Data type error" -> 207 "Application
                              internal error", que es lo que corresponde a un
                              fallo de ENTORNO nuestro y no del emisor

Si la salida es identica, el comprobador no ve la diferencia y P1 queda
confirmada.
"""
import io, json, os, sys
sys.path.insert(0, ".")
from via_d_v2_validar import problemas, HORA_FALSA

CORRECCION = {"101": ("100", "Segment sequence error"),
              "102": ("207", "Application internal error")}

idx = json.load(io.open("via_d_v2/indice.json", encoding="utf-8"))
print("%-26s %-14s %-22s %-22s %s"
      % ("operador", "caso", "como esta", "corregido", "¿distingue?"))
print("-" * 100)
iguales = 0
for x in idx["con_acuse"]:
    t = io.open(x["fichero"], encoding="utf-8", newline="").read()
    t = t.replace("<hora oculta>", HORA_FALSA)
    cod = next((c for c in CORRECCION if "|%s^" % c in t), None)
    if not cod:
        continue
    bueno, texto = CORRECCION[cod]
    t2 = t.replace("|%s^" % cod, "|%s^" % bueno)
    import re
    t2 = re.sub(r"\|%s\^[^^|]*\^" % bueno, "|%s^%s^" % (bueno, texto), t2)
    e1, a1 = problemas(t)
    e2, a2 = problemas(t2)
    mismo = (sorted(e1 + a1) == sorted(e2 + a2))
    iguales += 1 if mismo else 0
    print("%-26s %-14s %-22s %-22s %s"
          % (x["operador"][:26], x["caso"][:14],
             "ERR-3=%s  %de %da" % (cod, len(e1), len(a1)),
             "ERR-3=%s  %de %da" % (bueno, len(e2), len(a2)),
             "NO, identico" if mismo else "SI, difiere"))

print()
print("=" * 100)
print("acuses en los que el comprobador NO distingue el codigo correcto del"
      " incorrecto: %d de 6" % iguales)
print()
if iguales == 6:
    print("P1 CONFIRMADA, 0 de 2 fallos vistos. La diferencia con los limpios")
    print("que salio antes era un CONFUNDENTE: solo los acuses de fallo llevan")
    print("ERR, y el aviso lo dispara el ERR y no el codigo. El comprobador")
    print("avisa de lo mismo con el codigo bueno y con el malo.")
    print()
    print("P3 DISPARA: las DOS mitades de la via (d) son ciegas al fallo")
    print("silencioso, y la razon transfiere: un oraculo de estanteria")
    print("comprueba que el mensaje este bien formado y que sus codigos")
    print("EXISTAN; el fallo silencioso es un valor VALIDO en la situacion")
    print("equivocada.")
else:
    print("Hay al menos un caso donde SI distingue. Mirarlo: puede ser la")
    print("refutacion de P1.")
