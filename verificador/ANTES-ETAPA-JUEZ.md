> *Copia pública: el párrafo «Fijado en autónomo» marca como no publicadas la hoja de ruta y la decisión de ruta del laboratorio; el resto va literal.*

# ANTES: etapa 37, los dos fallos del juez de la etapa 36 (FIJADO el 7-nov-2026)

**Fijado en autónomo**, dentro de la hoja de ruta (`HOJA-DE-RUTA.md`, no publicada). Jev eligió esta etapa con 0,82 (`decision-jev-ruta20.md`, no publicada);
pausar quedó en 0,13.

## La pregunta (fija)

> ¿Puede el juez dejar de contar mal las dos conductas que encontró la etapa 36, cambiando solo los veredictos de esas dos
> conductas? Las conductas son:
> - un valor de una tabla de usuario fuera del mapa de la guía;
> - un recurso que sale de un segmento que la guía no mapea.

## Punto de partida (medido)

- **Un valor de PID-8 fuera de la 0001.**
  - El juez lo cuenta como «valor imposible convertido», y además como «FHIR inválido» si el código no es de FHIR
    (`conversion.py:697-702`).
  - Su perfil dice «fuera de la 0001: ausente» (`conversion.py:1540`).
  - Para las demás tablas de usuario, su función dice «fuera de la tabla (user-defined), convención» (`conversion.py:863-865`).
  - Una minúscula de la 0001 ya es convención (AMB-CV-1).
  - La 0001 de v2.5 es de usuario y sus valores son sugeridos (Ch03.txt:5034-5044).
  - Por la regla del estudio de conversores, el `unknown` de LinuxForHealth para PID-8 = `S` es una convención que el juez cuenta
    por error (etapa 36).
- **Un recurso de un segmento que la guía no mapea.**
  - En ADT, una Observation de más (de ACC o de PDA en Microsoft) sale como sobrante «inventado», y el juez la cuenta como «sin
    origen propio en el mensaje», citando una hoja de ORU (`conversion.py:356` y `1527-1532`).
  - Tiene origen en el mensaje. El estudio la cuenta como ya declarada (M-28).
- **Cómo se rejuzga lo publicado:** `md/rejuicio_md.py` juzga todas las evidencias guardadas con el juez de la carpeta y compara,
  evidencia a evidencia, con una línea base. En la etapa 26 dio 0 diferencias en 21.892 evidencias.
- **Lo que arrastra cambiar el juez:**
  - su huella cambia;
  - las tres bases de la demostración se rehacen (`base_nc.sh`, unos 50 minutos);
  - las del proyecto de ejemplo, con su receta, y su pin sube en un segundo push.

  Desde las etapas 34 y 35, cada push se ensaya sobre el índice y se comprueba después.

## Condiciones que no se negocian

1. **Lo de siempre:**
   - el código de terceros corre en su caja;
   - los proyectos de los conversores no se tocan;
   - cada push, por la opción B, con el ensayo y la comprobación de después del push.
2. **El diseño, a ciegas,** antes de escribir código (Fable), y las decisiones abiertas a Jev, con estados que lleven los hechos de
   los dos lados.
3. **Cada cambio, con su prueba en rojo antes.** Las cifras de las pruebas se dan del repositorio publicado.
4. **El rejuicio de todas las evidencias guardadas** (las del estudio de conversores, VXU, MDM, el arrastre y las demás que
   rejuzga `md/rejuicio_md.py`) con el juez de antes y el nuevo.
   - Cada diferencia tiene que ser de una de las dos conductas.
   - Una diferencia fuera de ellas es la regla de parada.
5. **Los resultados sellados de etapas pasadas no se tocan:** sus juicios conservan la huella de su juez. Lo que cambie en las cifras
   del estudio se dice en el resultado de esta etapa y, con una marca, en el del estudio.

## Qué se mide

- **Las evidencias que cambian,** por conducta, por conversor y por corpus.
- **Las cifras del estudio de conversores** (15 nuevas, 31 ya declaradas, 16 convenciones) antes y después.
- **Las bases de la integración continua:** que solo cambien la huella del juez y los veredictos de las dos conductas.

## Previsión (se sella antes del rejuicio con el juez nuevo)

Cuántas evidencias cambian en cada conducta, y si cambia alguna de las tres cifras del estudio.

## Hecho cuando

- **Un documento de resultado,** `RESULTADO-JUEZ.md`, con la frase: «El juez deja de contar mal las dos conductas de la etapa 36;
  en el rejuicio de lo publicado cambian N evidencias, todas de esas dos conductas» (con lo que se mida).
- **Publicado con la opción B,** con las bases rehechas, la CI en verde, el pin del ejemplo subido en el segundo push y cada push
  comprobado.

## Tope

**Dos sesiones, y un lector a ciegas** (hasta dos pasadas).

## Regla de parada

- **El rejuicio cambia algo fuera de las dos conductas y no se explica:** se declara, el juez no se publica, y se publica lo medido.

## Fuera de la etapa

- Otros fallos del juez.
- Rejuzgar los resultados sellados de etapas pasadas como si fueran de este juez.
- Los conversores, sus issues y sus proyectos.
