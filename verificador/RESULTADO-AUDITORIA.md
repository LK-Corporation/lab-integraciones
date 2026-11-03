# Resultado de la etapa 29: la validez de los corpus publicados de VXU y ORU

**De los 162 mensajes sintéticos publicados de VXU y ORU, 65 son válidos en HL7 v2.5 con todas sus reglas, y 142 si se deja aparte
una regla transversal del tipo de dato XCN, que solo toca a VX-L8 (reconfirmada con XCN-9). Fuera de esa regla, ninguna de las 9
nuevas de VXU ni de las 7 nuevas de ORU del estudio de conversores se apoya solo en mensajes inválidos.** Una se acota, otras tres
cambian de par mínimo y una de ellas se confirma más amplia.

La pregunta, fijada antes de mirar en [`ANTES-ETAPA-AUDITORIA.md`](ANTES-ETAPA-AUDITORIA.md), nace de la etapa de documentos
clínicos. Allí, dos defectos del corpus se le escaparon al diseño a ciegas y al programador: un campo condicional sin valor y unos
estados que la tabla de transiciones no da para el evento. El segundo obligó a retirar dos discrepancias publicadas
([`RESULTADO-MDM.md`](RESULTADO-MDM.md)).

## Cómo se hizo

1. **Dos auditores a ciegas de los resultados,** uno por tipo de mensaje. Solo leyeron los mensajes y el texto de v2.5:
   - capítulos 2, 2A, 3, 4 y 7;
   - estructura, campos obligatorios, campos condicionales con su condición, valores de tabla, restricciones según otros campos o
     el estado, y formato de los tipos de datos.

   Dan un veredicto y una cita por mensaje: [`au/AUDITORIA-VXU.json`](au/AUDITORIA-VXU.json) y
   [`au/AUDITORIA-ORU.json`](au/AUDITORIA-ORU.json).
2. **El cruce, después,** con las nuevas publicadas: sus bases (`vx/CLASES-VX3.json`, `cv/RESULTADO-CV3.md`) y sus pares mínimos.
3. **Tres pares nuevos, válidos en v2.5,** donde el par publicado quedó en duda o cayó: [`au/pares_auditoria.py`](au/pares_auditoria.py),
   con su resultado en [`au/RESULTADO-AU-pares.json`](au/RESULTADO-AU-pares.json). Se corrieron con los dos conversores en su caja.

## Lo que dieron las auditorías

| Corpus | Mensajes | Válidos | Inválidos | En duda |
|---|---|---|---|---|
| VXU, con todas las reglas | 90 (40 bases y 50 de pares) | 2 | 86 | 2 |
| VXU, sin la regla transversal | 90 | 79 | 6 | 5 |
| ORU | 72 (40 bases y 32 de pares) | 63 | 7 | 2 |

**La regla transversal.** v2.5 dice que, si un XCN lleva identificador (XCN-1), también tiene que llevar la tabla de origen
(XCN-8) o la autoridad asignadora (XCN-9) (§2.A.86.1). Los profesionales de las bases de VXU no la cumplen: falta en 86 de los 90
mensajes. El propio ejemplo de VXU del capítulo 4 tampoco la cumple. Solo toca un hallazgo, VX-L8, que trata justo de RXA-10, y se
volvió a confirmar con XCN-9.

**Lo que sí es propio de cada mensaje:**
- **VXU:**
  - ORC-3 ausente (B35, VL01-control y VM13-caso);
  - un sistema de codificación sin su versión (B28);
  - un XON con la parte numérica no numérica (B38);
  - MSH-9 sin la estructura del mensaje (B39).
- **ORU:**
  - OBX-2 vacío con OBX-11 «I» (B22);
  - OBR-7 u OBR-25 vacíos en un informe (B33 y B34);
  - OBX-11 en minúscula (B39);
  - un sistema de codificación sin su versión (B15 y B24);
  - OBR-25 «I» («sin resultados») con una OBX final (L10-caso).

## Lo que cambia en lo publicado

| Hallazgo | Qué pasaba | Qué queda |
|---|---|---|
| VX-M15 (Microsoft) | Su par, VM15, quedó en duda: una vacuna rechazada («RE») con 0,5 mL administrados, lote y sitio | **Se confirma** con un par válido (AU1): rechazada sin nada administrado |
| VX-L8 (LinuxForHealth) | Su par llevaba RXA-10 sin XCN-8 ni XCN-9, en el campo del hallazgo | **Se confirma** con XCN-9 (AU2) |
| L-19 (LinuxForHealth) | Su par, L10-caso, era inválido | **Se confirma frente al control «X»** (AU3, válido): «I» sin OBX sale «unknown», y «X», «cancelled». «O» y «S» se pensaron como controles y resultaron casos: también salen «unknown», y la guía los lleva a «registered». Por eso el JSON da `confirma: false`, que cuenta todos los controles. **El hallazgo es más amplio** |
| L-15 (LinuxForHealth) | Decía «resultado no obtenible “X”, o pendiente “I”». Sin OBX-2, v2.5 solo admite «X», y el caso «I» solo salía en ORU-B22, que es inválida | **Se acota a «X»,** con ORU-B18 y el par L06, que son válidos |

Los cambios llevan su marca en [`cv/RESULTADO-CV3.md`](cv/RESULTADO-CV3.md), [`cv/CLASES-CV3.json`](cv/CLASES-CV3.json) y
[`vx/CLASES-VX3.json`](vx/CLASES-VX3.json) (`nota_auditoria`, `par_valido`). **Las frases de los dos estudios no cambian:**
siguen las 9 nuevas de VXU y las 15 del estudio de conversores.

## Lo que no dice

- **Los auditores son lecturas del texto de v2.5,** independientes y con cita, pero no un validador oficial. Lo dudoso quedó como
  duda, no como defecto.
- **No se auditaron las bases de ADT** (los ejemplos del capítulo 3 y las bases de otras etapas) **ni las muestras públicas de los
  proyectos,** que no son del laboratorio y ya se juzgan con banderas de validez.
- **El corpus de MDM lleva la misma regla transversal en sus XCN,** y no se rehízo: ninguna de sus 3 nuevas trata de un XCN.
- **«Con todas sus reglas»** deja fuera, en ORU, una duda que afecta a todo el corpus: UCUM y SCT no están en la tabla 0396 impresa
  de v2.5, que el texto deja abierta. El auditor la anotó aparte y no cambia ningún veredicto.
- **Las bases y los pares inválidos que no sostienen ninguna nueva** siguen en el corpus. Pueden pesar en las cuentas de categorías
  y en las ya declaradas, pero no en las frases.
