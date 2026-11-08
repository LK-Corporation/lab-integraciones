# Estado: Q-PD-4 otra vez, con un hecho corregido (8-nov-2026)

Redactado el 8-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Por qué se repregunta

El estado de Q-PD-4 (`pd/estado_pd2.md`) tenía un hecho falso: decía que la opción (a), «se declara en L-CV-18», no cambia el juez
publicable, ni su huella, ni las bases. L-CV-18 es texto de `conversion.py`, que entra en la huella del juez. Declararlo allí
cambia la huella, y con ella las tres bases de la integración continua (otros 50 minutos) y la huella de la información del juez que
fija P-MD-25 (d). La pregunta se repite con las opciones separadas.

## Contexto y hechos (los mismos de `pd/estado_pd2.md`)

- **El juez nuevo** reconoce la Observation de PD1-7 si su `valueCodeableConcept` lleva un coding con el sistema de la 0315 o con
  el código de PD1-7, con cualquier sistema; entre varias, la primera con el sistema de la 0315. Ese paso va antes que la regla de
  ACC y PDA de la etapa 37 (la 0136).
- **El caso:** PD1-7 = Y, ACC-5 = Y, y una sola Observation de solo Y con el sistema de la 0136. El juez la da a PD1-7 por el
  código y cuenta un código mal mapeado de PD1-7. Con el juez de antes era una sin mapa de ACC. Igual con N, con PDA y con otro
  sistema que no sea la 0315.
- **El estado de Q-PD-2** decía que el sistema separa la de PD1-7 de la de ACC o PDA «si el conversor lo pone». Vale cuando están
  las dos; con una sola de la 0136, el código la lleva a PD1-7.
- **Precedente:** con PD1-7 = F, (v2-0136, F) es la de PD1-7 con código mal mapeado, y las pruebas lo fijan.
- **L-CV-18 hoy dice** que la Observation de PD1-7 se reconoce «por un coding de su valueCodeableConcept con el sistema de la 0315
  o con el código de PD1-7». De esa letra se sigue el caso, pero no lo nombra: solo nombra dos Observation sin sistema.
- **El servidor MCP del juez** publica sus límites (L-CV) a quien lo use; el resultado de la etapa no lo ve quien solo consulta el
  servidor.
- **Ninguna evidencia guardada lleva PD1-7.** Ninguna opción cambia el rejuicio, las cifras ni ningún caso de las bases; con (a1) y
  (b) cambia la huella del juez y las bases se rehacen solo por ella.
- **La revisión a ciegas** propuso declararlo en L-CV-18 y en el resultado, con una prueba, o preguntarlo a Jev.
- **La primera respuesta de Jev** a Q-PD-4, con el hecho falso, fue (a), 0,95.

## Q-PD-4. PD1-7 en Y o N, ACC o PDA con ese valor, y una sola Observation de solo Y/N con el sistema de la 0136

- **(a1) Es la de PD1-7, y se declara en L-CV-18 y en el resultado,** con su prueba.
  - A favor: el juez dice de sí mismo lo que hace, también a quien solo usa el servidor; un hallazgo por una Observation; la misma
    regla que (v2-0136, F).
  - En contra: otra huella del juez; las tres bases otra vez (unos 50 minutos) y la prueba de la información en rojo antes.
- **(a2) Es la de PD1-7, y se declara solo en el resultado,** con su prueba.
  - A favor: el juez no cambia, ni su huella, ni las bases; L-CV-18 ya lo cubre por su letra.
  - En contra: la información del juez no nombra el caso; quien solo consulte el servidor tiene que deducirlo.
- **(b) Con el sistema de la 0136 no es de PD1-7:** sin mapa de ACC o PDA, y PD1-7 ausente.
  - A favor: el juez no da por de PD1-7 algo que lleva el sistema de otra tabla cuando el mensaje tiene un campo de esa tabla con ese
    valor.
  - En contra: cambia lo que hace el juez después de medir: otra huella, las bases otra vez, pruebas nuevas en rojo antes; y la regla
    queda asimétrica, porque con PD1-7 = F, (v2-0136, F) sigue siendo la de PD1-7.
