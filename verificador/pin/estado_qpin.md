# Estado: cómo arreglar la receta de la base del proyecto de ejemplo (31-oct-2026)

Redactado el 31-oct-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

Un proyecto de ejemplo llama a un flujo de integración continua fijado a un commit del laboratorio, con su propia línea base de
resultados. Para subir el pin a un commit con un juez y un corpus nuevos, la guía publicada dice que hay que rehacer la base con
una receta (un guion). La etapa sigue esa guía como lo haría un tercero, y lo que haga falta de más es un hallazgo que se arregla
en la guía y se declara.

## Hechos (medidos)

1. **Sin rehacer la base,** el flujo sigue en verde. Los 40 casos nuevos solo se anotan, y el juez y el corpus distintos salen como
   avisos. Una comprobación aparte, de fuera, sí falla.
2. **La receta, corrida tal cual con el pin nuevo, se para en el primer paso:** «ejemplo: 389 casos y se esperaban 349». El
   número esperado está escrito a mano en la receta: es el tamaño del corpus del laboratorio de antes más los 6 mensajes propios.
3. **Esa parada protege** de una base hecha con un corpus que cambió sin querer. Pero la guía no dice que haya que tocar el número
   al subir el pin, y un tercero que copia la receta tendría el mismo problema.

## La pregunta

¿Cómo se arregla?
- (a) **La receta calcula el número esperado** a partir del corpus del commit fijado y de los mensajes propios. La parada se
  queda para cuando no cuadren.
- (b) **El número sigue escrito a mano,** y la guía y el mensaje de la parada dicen que hay que cambiarlo cuando el pin trae
  corpus nuevo.
- (c) **Las dos cosas:** la receta lo calcula, y además la guía explica que el número cambia con el corpus.
