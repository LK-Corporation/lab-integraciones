# ANTES: etapa 27, subir el pin del proyecto de ejemplo como lo haría un tercero (FIJADO el 31-oct-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). Jev la eligió con 0,54
(`decision-jev-ruta10.md`, no publicada); un
quinto tipo de mensaje quedó en 0,25.

## La pregunta (fija)

> Un proyecto que llama al flujo fijado a un commit anterior, ¿puede subir el pin al commit que trae un tipo de mensaje nuevo
> siguiendo solo la guía publicada (`CI.md`): cambiar el pin, rehacer su línea base con la receta y nada más? ¿Siguen sus dos
> llamadas en verde y el run en rojo cayendo solo por su defecto? ¿Y qué ve quien sube el pin sin rehacer la base?

## Punto de partida (medido el 31-oct)

- **El proyecto de ejemplo** (`ejemplo-ci/`) llama al flujo fijado a `e704b97` (etapa 25), con `laboratorio_ref` igual:
  - su base tiene 349 casos: 343 del laboratorio y 6 propios;
  - el defecto sembrado da 164 casos con `PID-8`.
- **El laboratorio publicado está en `c9d49d9`** (etapa 26). Su juez cambia de huella (`cb1338ca…`) y su corpus gana 40 mensajes
  MDM. Con ese pin, el corpus del laboratorio pasa a 383.
- **La guía** dice: «Cuando subas de commit y cambie el juez o el corpus, regenera la base». La receta es `ejemplo-ci/ci/hacer_base.sh`,
  con Docker y red.
- **La prueba P-CI-27** vigila que los dos YAML del ejemplo sean sus plantillas con un mismo commit, el esperado.

## Condiciones que no se negocian

1. **Lo de siempre:**
   - el juez no cambia;
   - el código de terceros va en la caja;
   - sin secretos y con permisos de solo lectura;
   - cada push por la opción B.
2. **Como un tercero:** solo lo que dice la guía publicada. Si hace falta algo más, es un hallazgo de la etapa, se arregla en la
   guía y se declara.
3. **El pin, a un commit publicado y entero** (40 hex), en `uses:` y en `laboratorio_ref`.
4. **La base del proyecto se rehace con la receta,** sin tocarla a mano.

## Qué se mide

- **Sin rehacer la base** (en el ensayo local, antes del push): qué da `ejemplo` con el pin nuevo y la base vieja. Si falla o
  pasa, por qué motivo, y qué avisos.
- **Con la base rehecha:**
  - las dos llamadas, en verde en GitHub;
  - el run en rojo a mano, que falla solo en la comparación y por el defecto sembrado, comprobado desde fuera;
  - cuántos casos.
- **Lo que cuesta:** pushes y minutos.

## Previsión (se sella antes del primer push)

Qué da el ensayo sin rehacer la base, cuántos casos tendrá el rojo y la probabilidad de que todo salga a la primera.

## Hecho cuando

- **Publicado y en el runner:** el pin subido, las dos llamadas en verde y el rojo como se espera.
- **Un documento de resultado,** `RESULTADO-PIN.md`, con la frase: «Siguiendo solo la guía, un proyecto sube el pin al commit que
  trae un tipo de mensaje nuevo cambiando el pin y rehaciendo su base; sin rehacerla, el flujo <lo que pasó>».

## Tope

**Una sesión de trabajo.**

## Fuera de la etapa

- Un repositorio aparte para el ejemplo (es del autor).
- Cambiar el flujo o el juez.
