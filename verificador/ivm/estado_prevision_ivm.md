# Estado: la previsión de la etapa 31, antes de correr (4-nov-2026, noche)

Redactado el 4-nov-2026. **A propósito NO incluye la previsión de nadie.**

## Contexto

Se van a pasar por el validador de IRIS, contra v2.5, las 225 muestras públicas de los dos conversores de HL7 v2 a FHIR (sus
mensajes de prueba). Cuenta solo lo que el texto de v2.5 sostiene. Lo que no se puede leer con el texto de v2.5 (campos o
segmentos que no define, tablas que no trae, la versión declarada) va aparte. En la etapa anterior, con los mensajes sintéticos del
laboratorio, salieron un 38 % válidos, un 13 % inválidos y un 49 % sin decidir.

## Hechos

1. **Las versiones:** la mayoría de las muestras no son de v2.5. De las de conversores, 52 de 65 son de la 2.8; de las de VXU, la
   mitad de la 2.5.1 y la otra mitad de la 2.6; de las de MDM, casi todas de la 2.6.
2. **Lo que dejó sin decidir la etapa anterior:** UCUM en las unidades, que el texto permite como extensión de la tabla, y TXA-3
   en MDM.
3. **Los inválidos de la etapa anterior** eran obligatorios vacíos en mensajes sintéticos con segmentos opcionales mínimos.
4. **Las muestras son los mensajes de prueba** que cada proyecto escribió para su conversor.
5. **Cinco discrepancias nuevas publicadas** se apoyan en parte en muestras.

## Las preguntas

- ¿Qué proporción de las 225 muestras sale válida?
- ¿Cuántas de esas cinco nuevas quedan sin ningún mensaje válido, contando las muestras?
