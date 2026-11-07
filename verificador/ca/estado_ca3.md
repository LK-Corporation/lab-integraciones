# Estado: Q-CA-2 otra vez, con los hechos corregidos (7-nov-2026)

Redactado el 7-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Por qué se pregunta otra vez

Jev decidió `Q-CA-2` («también se corrige en el estudio», 0,97) con un estado (`ca/estado_ca2.md`) en el que el hecho 11 decía que
corregir la descripción de M-28 obligaba a regenerar la página web del estudio. **No es así:** la página no muestra M-28. Y faltaba un
hecho: uno de los ficheros que se corregirían está sellado.

## Contexto

La candidata de Microsoft de la etapa 33 es M-28, una clase ya declarada del estudio de conversores: la misma conducta, ya contada
en las muestras de Microsoft. Su descripción publicada, «Observation de PDA (certificado de defunción, autopsia…) que la guía no
mapea», se queda corta: en la muestra `ADT-A31-01`, que lleva ACC y no PDA, la Observation que cuenta es la `injury-incident` de ACC.

## Hechos

1. **Dónde está esa descripción:**
   - en la tabla de las ya declaradas de `cv/RESULTADO-CV3.md` (línea 167), que no está sellada;
   - en `cv/cv3_clases.py` (línea 87), que está sellado en el bloque 2 del sello de la etapa 33 (`ga/SELLO-GA.txt:45`). Cambiarlo
     hace que esa línea del sello deje de cuadrar, y habría que declararlo en un bloque nuevo del sello de la 33;
   - en cinco JSON de clases de corridas pasadas (`cv/CLASES-CV3.json`, `cv/ar/CLASES-AR-*.json`, `ga/CLASES-GA-v1.json` y `v2`).
     Son registros de su etapa: los escribió `cv3_clases.py` al correr, y no se reescriben.
2. **La página web del estudio** no muestra M-28 ni esa descripción, así que no hay que regenerarla.
3. **Lo que no cambia en ningún caso:** la clase (ya declarada), su declaración, sus casos y las cifras del estudio. Solo cambia el
   texto que la describe.
4. **El resultado de la etapa 36 y la marca en el de la 33** dicen la descripción corregida en cualquier caso.

## La pregunta

**Q-CA-2. La descripción de M-28.**
- (a) Se dice en el resultado de la 36 y en la marca del de la 33; el estudio no se toca.
- (b) Se corrige también en la tabla de `cv/RESULTADO-CV3.md`, con una marca de la etapa 36. `cv3_clases.py` y los JSON no se tocan.
- (c) Como (b), y también en `cv3_clases.py`, con un bloque nuevo en el sello de la 33. Los JSON de las corridas pasadas no se tocan.
