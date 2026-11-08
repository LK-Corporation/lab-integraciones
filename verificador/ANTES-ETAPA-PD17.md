> *Copia pública: el párrafo «Fijado en autónomo» marca como no publicadas la hoja de ruta y la decisión de ruta del laboratorio; el resto va literal.*

# ANTES: etapa 40, la Observation de PD1-7 en el juez (FIJADO el 8-nov-2026)

**Fijado en autónomo**, dentro de la hoja de ruta (`HOJA-DE-RUTA.md`, no publicada). Jev eligió esta etapa con 0,56 (`decision-jev-ruta23.md`, no publicada);
pausar quedó en 0,31.

## La pregunta (fija)

> ¿Puede el juez emparejar con su campo la Observation que la guía crea desde PD1-7 en un ADT, cambiando solo lo que el juez dice
> de esa Observation?

## Punto de partida (medido)

- **La guía** crea en ADT_A01 una Observation desde PD1-7 cuando viene (`MSG_ADT_A01.csv:19`, «IF PD1-7 VALUED»).
- **El juez no la empareja con su campo.**
  - Pasa por una de las Observation de los OBX, por orden, y sin OBX cuenta como inventada.
  - Lo encontró el diseño de la etapa 37. Su primer arreglo lo declaraba como límite (L-CV-18), y el segundo lo quitó.
  - Jev decidió dejarlo en el resultado de la 37 (Q-JZ-6).
- **La regla de la 0136 de la 37** (L-CV-17) puede además dar una Observation de PD1-7 de solo Y/N por de ACC o PDA, si el mensaje
  trae uno de ellos con ese valor.
- **Ninguna de las 21.553 evidencias de ADT guardadas lleva PD1-7.** Lo previsible es que ningún veredicto publicado cambie y que
  solo cambie la huella del juez. Las pruebas tienen que ser sintéticas.
- **Lo que arrastra cambiar el juez** (como en la 37):
  - su huella cambia;
  - las tres bases de la demostración se rehacen con `base_nc.sh` (unos 50 minutos);
  - las del proyecto de ejemplo, con su receta, y su pin sube en un segundo push.

## Condiciones que no se negocian

1. **Lo de siempre:**
   - el código de terceros corre en su caja;
   - los proyectos de los conversores no se tocan;
   - cada push, por la opción B, con el ensayo y la comprobación de después del push.
2. **El diseño, a ciegas,** antes de escribir código (Fable), y las decisiones abiertas a Jev, con estados que lleven los hechos de
   los dos lados.
3. **Cada cambio, con su prueba en rojo antes.** Las cifras de las pruebas se dan del repositorio publicado.
4. **El rejuicio de todas las evidencias guardadas** con el juez de antes y el nuevo. Toda diferencia tiene que ser de la conducta
   de PD1-7; una diferencia fuera de ella es la regla de parada.
5. **Los resultados sellados de etapas pasadas no se tocan.**

## Qué se mide

- **Las evidencias que cambian en el rejuicio.**
- **Las bases de la integración continua:** que solo cambie la huella del juez y lo que se prevea.
- **Las pruebas:** cómo queda la Observation de PD1-7 con y sin OBX, con y sin ACC o PDA, en v2.5 y en otras versiones.

## Previsión (se sella antes del rejuicio con el juez nuevo)

Cuántas evidencias cambian en el rejuicio, y si cambia algo de las bases además de la huella.

## Hecho cuando

- **Un documento de resultado,** `RESULTADO-PD17.md`, con la frase: «El juez empareja con su campo la Observation de PD1-7; en el
  rejuicio de lo publicado cambian N evidencias» (con lo que se mida).
- **Publicado con la opción B,** con las bases rehechas, la CI en verde, el pin del ejemplo subido en el segundo push y cada push
  comprobado.

## Tope

**Dos sesiones, y un lector a ciegas** (hasta dos pasadas).

## Regla de parada

- **El rejuicio cambia algo fuera de la conducta de PD1-7 y no se explica:** se declara, el juez no se publica, y se publica lo
  medido.

## Fuera de la etapa

- Otros fallos del juez, y la lectura de los tipos de v2.6 y posteriores.
- Los conversores, sus issues y sus proyectos.
