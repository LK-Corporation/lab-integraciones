# Estado: la previsión de la etapa 39, lo sin clase del estudio (8-nov-2026)

Redactado el 8-nov-2026. **A propósito NO incluye la recomendación de nadie.** Se sella antes de medir.

## Contexto

`cv/cv3_clases.py` aplica las reglas de clase del estudio de conversores caso a caso, y lista en su salida (`sin_clase`) los
hallazgos que cuentan y no casan con ninguna regla. No falla por ello. La etapa 39 mide lo sin clase de hoy y decide si el aparato
debe fallar.

## Hechos

1. **En el estudio,** con el juicio de hoy y el aparato después de la etapa 38, no queda nada sin clase (medido en la 38).
2. **En la versión 2 del corpus de la etapa 33,** su JSON (`ga/CLASES-GA-v2.json`, juez del 4-nov) tenía 39 sin clase:
   - 8 de M-4 (la regla que arregló la 38);
   - 30 de la Observation de ACC de Microsoft;
   - 1 de PID-8 de LinuxForHealth.

   Desde entonces:
   - la 37 cambió el juez: la Observation de ACC sale como «recurso sin mapa», y PID-8 fuera de la 0001 como nota de convención;
   - el bloque 8 del sello hizo que M-28 reconozca ese hallazgo nuevo.

   No se ha medido qué da hoy.
3. **Lo sin clase es también un canal.** `ga/comparar_ga.py` (etapa 33) toma como candidatas nuevas lo que queda sin clase en la
   versión 2 y no en la 1; así salieron las 2 candidatas de la 33. Los 8 de M-4 estaban en las dos versiones y por eso no salieron
   como candidatas.
4. **Lo usan más guiones** (`ga/cifras_ga_b.py`, `ga/cruce_ga.py`, `ga/riesgo_ga.py`, `cl/reproducir_clases_cl.py`), y el aparato
   está sellado (bloques 1 a 9 del sello de la 33).

## Las preguntas

**Q-PREV-SC-1.** Con el juez y el aparato de hoy, ¿cuántos hallazgos sin clase quedan en la versión 2 del corpus de la 33?
- (a) Ninguno.
- (b) Entre 1 y 10.
- (c) Más de 10.

**Q-PREV-SC-2.** ¿Qué debe hacer el aparato con lo sin clase?
- (a) Fallar (salir con un código distinto de 0) cuando quede alguno.
- (b) No fallar, pero decirlo de forma que no pase sin verse (un aviso al final y una cuenta en la salida), y que los guiones que lo
  usan lo lean.
- (c) Nada: dejarlo como está.
