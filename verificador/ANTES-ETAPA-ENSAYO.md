> *Copia pública: el párrafo «Fijado en autónomo» marca como no publicadas la hoja de ruta y la decisión de ruta del laboratorio; el resto va literal.*

# ANTES: etapa 34, el ensayo local que ensaya lo que se publica (FIJADO el 7-nov-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). Jev eligió esta etapa
con 0,67 (`decision-jev-ruta18.md`, no publicada); la segunda opción, confirmar las 2 candidatas de la 33, quedó en 0,27.

## La pregunta (fija)

> ¿Puede el ensayo local de los flujos (`cv/ci/ensayo_flujo.py`) dejar de dar verde sobre algo distinto de lo que se va a
> publicar, sin cambiar lo que da cuando lo ensayado y lo publicado coinciden?

## Punto de partida (leído en el código y medido el 7-nov)

- **Cómo emula hoy los checkouts:**
  - con un `ref` de 40 hex que está en el repositorio, hace `git archive` de ese commit;
  - si no, copia el árbol de trabajo, sin `.git` ni `__pycache__`;
  - `github.sha` es el HEAD cuando hay `.git`, y un valor que no está cuando no lo hay.
- **Lo medido en la etapa 33, el 7-nov:**
  - el clon del repositorio público tenía la etapa preparada en el índice, sin commit. El ensayo de la demo sacó el laboratorio
    con `git archive` del HEAD (`371937c`, el commit ya publicado), así que probó la herramienta y las bases de antes;
  - los cuatro trabajos salieron en verde. Lo único que lo delataba era el texto «git archive 371937c9fb43» en una línea;
  - sobre una exportación del índice sin `.git` (`git checkout-index -a`), el ensayo copió el árbol y probó lo nuevo.
- **La otra cara, por el código:**
  - el repositorio que llama (el checkout sin `ref`) se copia del árbol de trabajo, con los ficheros sin seguimiento y los
    ignorados, que no se publican;
  - y los cambios sin `git add`, que tampoco.
- **Ninguna prueba cubre el ensayo:** `cv/ci/prueba_ci.py` no lo llama.
- **No medido:** si algún ensayo de las etapas 23 a 32 se hizo con el índice distinto del HEAD. Sus pushes salieron en verde en el
  runner.

## Condiciones que no se negocian

1. **Lo de siempre:**
   - el juez, la herramienta y los flujos de GitHub no cambian;
   - el código de terceros va en su caja;
   - cada push, por la opción B.
2. **El diseño, a ciegas,** antes de escribir código (Fable), y las decisiones abiertas a Jev.
3. **Cada cambio, con su prueba en rojo antes.** Las pruebas nuevas van en el juego de pruebas de la CI y corren en el trabajo
   `pruebas` de la demo.
4. **Cuando lo ensayado y lo publicado coinciden** (un clon limpio, o una exportación sin `.git`), el ensayo da lo mismo que hoy:
   los mismos trabajos, los mismos veredictos y los mismos informes byte a byte.

## Qué se mide

- **El control positivo:** el caso de la 33, reconstruido en una copia del clon. El HEAD queda en `371937c`, y el índice y el
  árbol de trabajo son los de la etapa 33 (`git read-tree -u --reset 54e8b9f`). Hoy da verde con lo viejo; con el arreglo no
  puede dar verde sobre lo viejo.
- **El control negativo:** un clon limpio en `74a6a99` y una exportación sin `.git`. Los trabajos `pruebas`, `negativo`,
  `positivo` y los del ejemplo y el rojo dan lo mismo que hoy, informe a informe.
- **La otra cara:** un fichero sin seguimiento y un cambio sin `git add` en el repositorio que llama. Se dice qué hace el
  ensayo con cada uno.
- **Lo que cuesta:** tiempo de más por ensayo.

## Previsión (se sella antes de correr los controles con el arreglo)

La probabilidad de que el control negativo dé lo mismo byte a byte a la primera, y de que el positivo deje de dar verde sobre lo
viejo.

## Hecho cuando

- **Publicado, con la CI en verde:** el ensayo arreglado y sus pruebas, que corren en `pruebas`.
- **Un documento de resultado,** `RESULTADO-ENSAYO.md`, con la frase: «Con el índice distinto del commit que emula, el ensayo
  ya no da verde sobre lo viejo; cuando coinciden, da lo mismo que antes, informe a informe».

## Tope

**Una sesión, y un lector a ciegas** (hasta dos pasadas). Cada push, por la opción B.

## Regla de parada

- **El control negativo no da lo mismo y no se explica:** se declara, no se publica el arreglo, y se publica la guía con el modo
  de ensayar que sí funciona (la exportación del índice).

## Fuera de la etapa

- Cambiar los flujos de GitHub, el juez, la herramienta o las bases.
- Emular el runner de verdad (Docker, red, permisos del token).
- Rehacer los ensayos de las etapas anteriores.
