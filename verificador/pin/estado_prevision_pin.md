# Estado: la previsión de la etapa 27 (subir el pin del proyecto de ejemplo), antes de medir (31-oct-2026)

Redactado el 31-oct-2026. **A propósito NO incluye la previsión ni la recomendación de nadie.**

## Contexto

Un laboratorio publica un flujo reutilizable de integración continua que pasa un conversor HL7 v2 → FHIR por un juez. Un
proyecto de ejemplo lo llama fijado a un commit, con su propia línea base de resultados. El laboratorio acaba de publicar un tipo
de mensaje nuevo: el juez cambia y su corpus de pruebas gana 40 mensajes. El proyecto de ejemplo va a subir el pin al commit nuevo,
como lo haría un tercero, siguiendo la guía publicada: cambiar el pin y rehacer su línea base con la receta.

## Hechos

- **La comparación con la base** funciona en modo «pasa»:
  - falla ante un hallazgo nuevo en un caso que ya estaba en la base;
  - un caso que no estaba en la base se anota, pero no hace fallar;
  - un juez o un corpus distintos son avisos.
- **Un job aparte comprueba desde fuera** que no hay nada nuevo: ni casos nuevos ni hallazgos nuevos.
- **El conversor del ejemplo** solo convierte tres tipos de mensaje y rechaza los demás, entre ellos el tipo nuevo.
- **El run en rojo a propósito** siembra un defecto que hoy se ve en 164 casos.
- **Las etapas anteriores de integración continua** salieron en GitHub a la primera, salvo una sorpresa con un evento nuevo.

## Las preguntas

1. Si el proyecto sube el pin **sin rehacer su base**, ¿qué hará su llamada principal?
2. Y la comprobación de fuera, en ese caso, ¿qué hará?
3. Con la base rehecha, ¿saldrá todo en verde a la primera en GitHub?
4. ¿Cuántos casos tendrá el run en rojo con la base rehecha?
