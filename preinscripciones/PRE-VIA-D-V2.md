# Predicción sellada antes de la mitad v2 de la vía (d) — 22-sep-2026

**Se escribe y se sella antes de instalar el comprobador y antes de correrlo**, como la anterior
(`PRE-VIA-D.md`, `7c2e6779`), que acertó.

## Lo que ya se sabe, y no es predicción sino observación

📏 **Al extraer los acuses aparece un hecho que cambia el alcance de esta medida.** De los tres
fallos vivos que la mitad v2 iba a mirar, **uno no está al alcance de ninguna herramienta que
trabaje sobre mensajes**:

| fallo vivo | acuse recuperable |
|---|---|
| el `MSA\|CE` del FailureTimeout, no conforme al modo original | **NO.** La traza dice «no se devolvió ningún ACK de aplicación» en los dos casos mirados; el `CE` solo existe como línea del log: `Constructing ACK with code CE` |
| el 4xx de FHIR contestado `AR` con `ERR-3=102` | sí: `MSA\|AR` + `ERR\|\|\|102^Data type error^HL70357\|E\|\|\|\|FHIR devolvio 401:` |
| `PV1` antes de `PID` contestado con `ERR-3=101` | sí: `MSA\|AR` + `ERR\|\|\|101^Required field missing^HL70357\|E\|...` |

Así que **la mitad v2 solo puede probarse sobre dos de los tres**, y eso ya es un resultado: el
acuse que el motor construye al agotar el plazo **no se conserva en forma de mensaje**, y por tanto
ningún oráculo offline puede juzgarlo.

## Qué se va a montar

`hl7apy` —biblioteca v2 de terceros, ni mía ni de InterSystems—, que implementa las estructuras del
estándar y valida un mensaje contra su perfil: segmentos requeridos, cardinalidades, tipos de dato y
valores de tabla. 10 acuses extraídos: 6 de fallo y 4 de limpio, que van como control de
discriminación.

## La predicción 🔮

**P1 — verá 0 de 2.** Los dos fallos recuperables usan **códigos válidos**: `101` y `102` están los
dos en la tabla 0357, y los segmentos están bien formados —`MSH`, `MSA`, `ERR` con su severidad—.
Un comprobador de conformidad valida **gramática y vocabulario**; lo que está mal aquí es **cuál de
los códigos válidos se eligió**, que es otra cosa.

**P2 — lo que reporte será igual en fallos y en limpios**, como pasó con el `dom-6` de la mitad
FHIR.

**P3, que es la que cierra el argumento.** Si P1 y P2 se cumplen, **las dos mitades de la vía (d)
son ciegas**, y no por mala suerte sino por una razón que se puede enunciar y que transfiere:

> **Un oráculo de estantería comprueba que el mensaje esté bien formado y que sus códigos existan.
> Un fallo silencioso es un valor válido en la situación equivocada. Son cosas distintas, y ninguna
> herramienta de conformidad puede ver la segunda.**

Si P3 se cumple, la §11.5 y la §4.3 del diseño tienen que decir que **ninguna vía ve el silencio sin
firma propia**, y la promesa de (d) —«un oráculo cuya firma no es la mía»— **no es alcanzable con
herramientas de estantería en este circuito**. Entonces quedan dos salidas honestas: pagar el
mapeador de referencia declarando que la firma es mía, o aceptar que el oráculo independiente no
existe aquí y escribirlo.

## Lo que falsaría la predicción

Que `hl7apy` señale **cualquiera** de los dos acuses de fallo por una razón sustantiva que **no**
aparezca también en los cuatro limpios. Basta uno.

## El control de que la prueba puede salir mal

Si no dice nada en absoluto —ni en los limpios, ni ante un acuse roto a propósito— no está
midiendo. Se le pasará además **un acuse mutilado a mano** (sin `MSA`) para comprobar que sabe
protestar. Si tampoco protesta con ese, la medida se descarta y no se concluye nada.
