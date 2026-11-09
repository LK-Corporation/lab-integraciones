> *Copia pública: el párrafo «Fijado en autónomo» marca como no publicadas la hoja de ruta y la decisión de ruta del laboratorio; el resto va literal. Su punto de partida dice que las únicas hojas de la guía que crean la Observation de PD1-7 son las de ADT_A01 y ORU_R01: es falso, porque se midió solo en las hojas CSV del laboratorio; el paquete de ConceptMap la crea en once mapas de mensaje (ver `RESULTADO-PD17ORU.md`).*

# ANTES: etapa 41, la Observation de PD1-7 en un ORU (FIJADO el 8-nov-2026)

**Fijado en autónomo**, dentro de la hoja de ruta (`HOJA-DE-RUTA.md`, no publicada). Jev eligió esta etapa con 0,74 (`decision-jev-ruta24.md`, no publicada);
pausar quedó en 0,19.

## La pregunta (fija)

> ¿Puede el juez emparejar con su campo la Observation que la guía crea desde PD1-7 en un ORU, cambiando solo lo que el juez dice
> de esa Observation?

## Punto de partida (medido)

- **La guía** crea en ORU_R01 una Observation desde PD1-7 cuando viene (`MSG_ORU_R01.csv:17`, «IF PD1-7 VALUED», `Observation[4]`,
  con su `subject` al Patient del PID). Las únicas hojas de mensaje de la guía con esa fila son la de ADT_A01 (`MSG_ADT_A01.csv:19`) y
  la de ORU_R01.
- **El juez ya la empareja en ADT** desde la etapa 40 (`RESULTADO-PD17.md`): la reconoce por el sistema de la 0315 o el código de
  PD1-7, y juzga su valor, su status y su sujeto. Su límite L-CV-18 dice que en `oru_conv` sigue como recurso inventado, y P-CV-33
  lo fija con un control.
- **En un ORU, hoy,** cada Observation se casa con un OBX por su código (primero entre las que refiere el DiagnosticReport de su OBR,
  después en todo el Bundle). Las que sobran son sobrantes: «origen_guia» mientras haya OBX fuera de ORDER_OBSERVATION (L-CV-7), y
  si no, inventadas, que cuentan.
- **Ninguna de las 4.424 evidencias de ORU guardadas lleva PD1-7 valorado;** 69 traen PD1 (`pd/PREVISION-PD.json`). Lo previsible es
  que ningún veredicto publicado cambie y que solo cambie la huella del juez. Las pruebas tienen que ser sintéticas.
- **Lo que arrastra cambiar el juez** (como en la 40):
  - su huella cambia;
  - las tres bases de la demostración se rehacen con `base_nc.sh` (unos 50 minutos);
  - las del proyecto de ejemplo, con su receta, y su pin sube en un segundo push.

## Condiciones que no se negocian

1. **Lo de siempre:**
   - el código de terceros corre en su caja;
   - los proyectos de los conversores no se tocan;
   - cada push, por la opción B, con el ensayo y la comprobación de después del push.
2. **El diseño, a ciegas,** antes de escribir código (Fable), y las decisiones abiertas a Jev, con estados que lleven los hechos de
   los dos lados. Lo que cuesta cada opción (huella, bases, pruebas) se comprueba antes de escribirlo en el estado.
3. **Cada cambio, con su prueba en rojo antes,** y mutantes del juez que las pruebas tengan que hacer caer, antes de la revisión.
   Las cifras de las pruebas se dan del repositorio publicado.
4. **El rejuicio de todas las evidencias guardadas** con el juez de antes y el nuevo. Toda diferencia tiene que ser de la conducta
   de PD1-7 en ORU; una diferencia fuera de ella es la regla de parada.
5. **Los resultados sellados de etapas pasadas no se tocan,** y la previsión se sella antes de correr el juez nuevo sobre las
   evidencias, también desde las pruebas que rejuzgan.

## Qué se mide

- **Las evidencias que cambian en el rejuicio.**
- **Las bases de la integración continua:** que solo cambie la huella del juez y lo que se prevea.
- **Las pruebas:** cómo queda la Observation de PD1-7 en un ORU con uno y con varios OBR, con OBX cuyo código o valor coinciden con
  los de PD1-7, con OBX fuera de ORDER_OBSERVATION, en v2.5 y en otras versiones; y que lo de ADT no cambie.

## Previsión (se sella antes del rejuicio con el juez nuevo)

Cuántas evidencias cambian en el rejuicio, y si cambia algo de las bases además de la huella.

## Hecho cuando

- **Un documento de resultado,** `RESULTADO-PD17ORU.md`, con la frase: «El juez empareja con su campo la Observation de PD1-7
  también en un ORU; en el rejuicio de lo publicado cambian N evidencias» (con lo que se mida).
- **Publicado con la opción B,** con las bases rehechas, la CI en verde, el pin del ejemplo subido en el segundo push y cada push
  comprobado.

## Tope

**Dos sesiones, y un lector a ciegas** (hasta dos pasadas).

## Regla de parada

- **El rejuicio cambia algo fuera de la conducta de PD1-7 en ORU y no se explica:** se declara, el juez no se publica, y se publica
  lo medido.

## Fuera de la etapa

- Otros fallos del juez, y la lectura de los tipos de v2.6 y posteriores.
- Los conversores, sus issues y sus proyectos.
