# BU-pre: la latencia de `probar_parche` (13-oct-2026)

**El bucle cabe.** Una prueba con 3 disparadores y 5 mensajes de regresión, con la caja arrancada durante la tirada, cuesta
**como mucho 36 s** (LABADTMUT y LABMULTIMUT) y 8-11 s en LABORUMUT. La regla de parada del ANTES era 90 s.

Medido con `agente/bu_latencia.py`, sobre un caso de cada caja de la ampliación (R-MS-4, R-ADT-7 y R-MT1), con su árbol base:

| Caja | (a) Completa, como el evaluador de hoy | (b) Caja arrancada, por prueba (2 pruebas) |
|---|---|---|
| LABORUMUT | 22,1 s: cargar 0,7, a_caja 7,2, medir 6,1, a_user 8,0 | 7,8 y 10,9 s |
| LABADTMUT | 49,7 s: cargar 0,8, a_caja 8,9, medir 32,7, a_user 7,4 | 34,7 y 35,9 s |
| LABMULTIMUT | 49,7 s: cargar 0,5, a_caja 9,2, medir 32,9, a_user 7,2 | 34,4 y 35,9 s |

**Lo que dice para el diseño:**
- **Lo caro es medir, no compilar.** Cargar y compilar cuesta menos de 1 s. En ADT y MULTI, cada mensaje cuesta unos 4 s, porque
  se espera la sesión y el acuse. Los 3-4 minutos de la evaluación de hoy vienen de los 60 mensajes de regresión y de las
  recargas de restauración, no de la prueba.
- **Con la caja arrancada caben 3-4 pruebas** en una tirada de 10 minutos. Con la medida completa por prueba (devolviendo USER
  cada vez), 2-3.
- **El precio de la caja arrancada:** el circuito congelado (USER) queda parado mientras dura la tirada, hasta 10 min. Se
  devuelve al cerrarla, con su huella y la sonda AA.
