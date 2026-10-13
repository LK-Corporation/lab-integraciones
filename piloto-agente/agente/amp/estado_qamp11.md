# Estado: una respuesta del agente que no es JSON estricto (Q-AMP-11)

Redactado el 13-oct-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

- **El estudio.** Compara un agente con modelo con una referencia sin modelo, en dos etapas (un piloto ya cerrado y una
  ampliación sellada). En cada tirada, el agente escribe un fichero `respuesta.json` con su localización y su parche.
- **Lo que dice la consigna:** «escribe `respuesta.json`» con un esquema JSON dado. No dice nada de JSON estricto.
- **Lo que hace el arnés** (escrito antes del piloto y sin cambios): lee el fichero con un lector JSON estricto. Si no lo puede
  leer, la tirada cuenta como «sin respuesta» (no localizado, no arreglado).
- **Lo que pasó.** En la ampliación, una tirada del agente escribió `respuesta.json` con un tabulador literal dentro de una
  cadena. Es el texto de una línea de código, que en ese lenguaje empieza por tabulador. El estándar JSON no admite caracteres
  de control sin escapar dentro de una cadena; un lector tolerante lo lee sin problema y el contenido es inequívoco.
- **Lo que no pasó:**
  - en las 52 tiradas del piloto no ocurrió nunca;
  - nadie ha mirado qué localiza esa respuesta: la decisión se toma sin saber si cambia el resultado.
- **La otra rama** (DeepSeek, a través de un adaptador) escribe el mismo fichero con la misma consigna. Sus respuestas se leerían
  con la misma regla.

## La decisión

- **Mantener el lector estricto.** La tirada cuenta como «sin respuesta», como dice el arnés sellado. Una entrega que no es JSON
  válido no es una entrega.
- **Lector tolerante para todas las tiradas de la ampliación,** de los dos brazos (solo caracteres de control dentro de
  cadenas). La regla se fija ahora, antes de puntuar; la estricta se reporta como sensibilidad.
