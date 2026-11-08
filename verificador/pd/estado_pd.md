# Estado: tres decisiones de la etapa 40, la Observation de PD1-7 en el juez (8-nov-2026)

Redactado el 8-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 40 quiere que el juez empareje con su campo la Observation que la guía crea desde PD1-7 en un ADT, cambiando solo lo que
dice de ella. Hoy la toma por la de un OBX, por orden, y sin OBX la cuenta como inventada. El diseño a ciegas
(`pd/diseno-pd-fable.md`) deja tres decisiones abiertas.

## Hechos comunes

- **La guía** crea en ADT_A01 una Observation desde PD1-7 «IF PD1-7 VALUED» (`MSG_ADT_A01.csv:19`). Su mapa de segmento tiene un
  solo elemento: PD1-7 → `valueCodeableConcept`, por la tabla 0315, que es la identidad (Y, F, N, I, U), con el sistema
  `…/CodeSystem/v2-0315`. No fija `Observation.code` ni nada más.
- **En v2.5,** PD1-7 es un IS con la tabla de usuario 0315.
- **Y y N coinciden con la 0136:** una Observation de PD1-7 con Y o N tiene la misma forma que las que la regla de la 0136 de la
  etapa 37 atribuye a ACC o PDA. Lo que las separa es el sistema del coding, si el conversor lo pone.
- **Ninguna de las 21.553 evidencias de ADT guardadas lleva PD1-7.** Ninguna opción cambia el rejuicio ni las bases: cambian las
  pruebas sintéticas y lo que el juez hará con conversores que sí lo traigan.
- **Precedentes del juez:**
  - en la etapa 37, la Observation de ACC o PDA se reconoce por un dato compartido, no por orden (Q-JZ-3);
  - el Encounter del PV1 que falta cuenta como `recurso_ausente`, incluso con PV1-2 = N (Q-CV-D-6), y lo mismo la Observation de
    cada OBX en ORU;
  - S-CV-5 dice que un recurso ausente cuenta.

## Q-PD-1. Reconocer la Observation solo por el dato, o también por eliminación

- **(a) Solo por el dato** (un coding con el sistema de la 0315 o con el código de PD1-7).
  - A favor: es la regla de la 37; el juez no da por de un campo lo que no lleva nada de él; una Observation inventada sigue siendo
    inventada.
  - En contra: una Observation de PD1-7 con el valor mal convertido (por ejemplo, F llevado a `true`) no se reconoce. Sale como
    ausente y además inventada: dos hallazgos por un defecto, en vez de un `valor_distinto`.
- **(b) También por eliminación:** con PD1-7 valorado, si tras los demás pasos queda exactamente una Observation, es la de PD1-7 y
  se juzga su valor.
  - A favor: un defecto, un hallazgo; es lo que hace el emparejamiento de ORU con los DiagnosticReport cuando cuentan igual.
  - En contra: una Observation inventada en un mensaje con PD1-7 pasaría a `valor_distinto` de PD1-7, y la 37 rechazó el orden como
    criterio para las Observation de ADT.

## Q-PD-2. Con PD1-7 en Y o N, y ACC o PDA con ese mismo valor: una Observation de solo Y/N, sin sistema

- **(a) Es la de PD1-7** (su paso va antes que el de ACC y PDA).
  - A favor: la guía sí mapea PD1-7 y no mapea ACC ni PDA. En las 365 Observation sin mapa del rejuicio de la 37, el valor lleva el
    sistema de la 0136 o un código propio del conversor, así que el sistema las separa cuando el conversor lo pone. Cierra el primer
    riesgo de L-CV-17.
  - En contra: con dos Observation así y sin sistemas, el juez elige por orden.
- **(b) Sin sistema no es de PD1-7:** se queda como hoy (de ACC o PDA por la 0136, o inventada), y PD1-7 sale como ausente.
  - A favor: el juez no elige por orden.
  - En contra: en el caso corriente (una sola Observation de solo Y, sin sistema, con PD1-7 = Y) contaría dos veces, ausente y sin
    mapa, lo que es una Observation bien hecha salvo el sistema; y mantiene el primer riesgo de L-CV-17.

## Q-PD-3. PD1-7 valorado y ninguna Observation

- **(a) `recurso_ausente`, que cuenta.**
  - A favor: la hoja la crea bajo condición, y la condición se cumple; es lo que hace el juez con el Encounter del PV1 y con la
    Observation de cada OBX en ORU; S-CV-5.
  - En contra: la Observation de PD1-7 es periférica, y un conversor que proyecta solo los segmentos principales pasaría de correcto
    a fallo silencioso en cuanto el mensaje traiga PD1-7.
- **(b) Una nota, que no cuenta.**
  - A favor: no cambia veredictos por un segmento opcional.
  - En contra: la guía no distingue destinos principales y periféricos.
