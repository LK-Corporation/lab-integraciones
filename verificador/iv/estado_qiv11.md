# Estado: los sistemas de codificación que la tabla 0396 de v2.5 no trae (4-nov-2026, noche)

Redactado el 4-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 30 pasa los mensajes sintéticos publicados por el validador de IRIS y cuenta solo lo que el estándar HL7 v2.5 sostiene.
Un valor fuera de una tabla de HL7 cuenta como invalidez si no está en la tabla del estándar. Al probar el aparato apareció una
decisión que el diseño no dejó abierta.

## Hechos

1. **La tabla 0396 (sistemas de codificación) es de HL7 en v2.5.** Su lista impresa trae valores literales (LN para LOINC, por
   ejemplo) y patrones de extensión: «99zzz o L» para códigos locales, HL7nnnn para las tablas de HL7, e ISOnnnn e IBTnnnn.
2. **No trae UCUM ni SCT**, que se añadieron en versiones posteriores. Los mensajes del laboratorio usan UCUM en las unidades (ORU,
   VXU) y pueden usar SCT.
3. **IRIS rechaza UCUM** con la tabla 0396 de su esquema.
4. **Los auditores de la etapa 29** vieron lo mismo en ORU. Lo trataron como una duda sistémica aparte, que no cambió ningún
   veredicto, y así se publicó.
5. Según cómo se trate, casi todos los mensajes de ORU y VXU salen inválidos o no por esta sola causa.

## La pregunta

¿Cómo se cuenta un sistema de codificación que no está en la 0396 de v2.5, ni por valor ni por patrón (UCUM, SCT)?
- (a) Cuenta como invalidez: es la lectura literal de la tabla impresa.
- (b) Duda sistémica aparte, sin cambiar el veredicto, como en la 29.
- (c) Cuenta, y además se marca aparte para que las cifras se puedan leer de las dos maneras.
