# Estado: una decisión más de la etapa 40, la Observation de PD1-7 en el juez (8-nov-2026)

Redactado el 8-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 40 hace que el juez empareje con su campo la Observation que la guía crea desde PD1-7 en un ADT. Está hecha y medida, y la
revisión a ciegas la aprueba con cuatro menores. Uno de ellos es un caso que no se decidió.

## Hechos

- **Cómo la reconoce hoy el juez nuevo:** con PD1-7 valorado, una Observation sin el código de un OBX es candidata si su
  `valueCodeableConcept` lleva un coding con el sistema de la 0315 o con el código de PD1-7, con cualquier sistema. Entre varias, la
  primera con el sistema de la 0315. Ese paso va antes que la regla de ACC y PDA de la etapa 37 (la 0136: una Observation de solo
  Y/N es de ACC o PDA si el segmento trae un campo de la 0136 con ese valor).
- **El caso:** PD1-7 = Y, ACC-5 = Y, y una sola Observation de solo Y con el sistema de la 0136
  (`http://terminology.hl7.org/CodeSystem/v2-0136`). Hoy el juez la da a PD1-7 por el código, y cuenta un código mal mapeado de
  PD1-7. Con el juez de antes era una Observation sin mapa de ACC. Pasa igual con N, con PDA y con otro sistema que no sea la 0315.
- **Lo que se le dijo antes a Jev era incompleto.** El estado de Q-PD-2 decía que lo que separa una Observation de PD1-7 de una de
  ACC o PDA es «el sistema del coding, si el conversor lo pone». Eso vale cuando están las dos: la de la 0315 es de PD1-7 y la de la
  0136 sigue a ACC. Con una sola de la 0136, el sistema no las separa: el código la lleva a PD1-7. Q-PD-2 (Y/N sin sistema, a
  PD1-7) se decidió solo para «sin sistema».
- **Precedente en el mismo diseño:** con PD1-7 = F, una Observation (v2-0136, F) es la de PD1-7 con código mal mapeado (F no es de la
  0136, así que no hay ACC ni PDA con los que confundirla). Las pruebas lo fijan.
- **En las 365 Observation sin mapa del rejuicio de la etapa 37,** el valor lleva el sistema de la 0136 o un código propio del
  conversor.
- **Ninguna evidencia guardada lleva PD1-7.** Ninguna opción cambia el rejuicio ni las cifras. El veredicto es fallo silencioso con
  las dos opciones: cambia qué se cuenta.

## Q-PD-4. PD1-7 en Y o N, ACC o PDA con ese valor, y una sola Observation de solo Y/N con el sistema de la 0136

- **(a) Como está: es la de PD1-7,** con código mal mapeado (un hallazgo). Se declara en L-CV-18 y se añade su prueba.
  - A favor: la guía mapea PD1-7 y no ACC ni PDA; un hallazgo por una Observation; es la misma regla que da (v2-0136, F) por la de
    PD1-7; no cambia el juez publicable, ni su huella, ni las bases.
  - En contra: una Observation que lleva bien el sistema de la 0136, que es lo que hacen los conversores con ACC y PDA, se da por la
    de PD1-7 mal hecha; el juez no dice que falte la de PD1-7 ni que haya una de ACC sin mapa.
- **(b) Con el sistema de la 0136 no es de PD1-7:** sigue la regla de ACC y PDA (sin mapa, de ACC), y PD1-7 sale como recurso
  ausente (dos hallazgos).
  - A favor: el juez no da por de PD1-7 algo que lleva el sistema de otra tabla, cuando el mensaje tiene un campo de esa tabla con ese
    valor; dice lo que hay: una de ACC y ninguna de PD1-7.
  - En contra: cambia el juez después de medir: otra huella, las tres bases otra vez (unos 50 minutos), pruebas nuevas en rojo antes;
    y la regla queda asimétrica: con PD1-7 = F, (v2-0136, F) sigue siendo la de PD1-7.
