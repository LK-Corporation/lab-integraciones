# Estado: la previsión de la etapa 32, antes de correr (5-nov-2026)

Redactado el 5-nov-2026. **A propósito NO incluye la previsión de nadie.**

## Contexto

Se van a validar con IRIS las 223 muestras públicas de los dos conversores que declaran otra versión que la 2.5, cada una con el
esquema de su versión. Las de la 2.5.1 se leen con el texto de v2.5.1. Para las demás no hay texto: cuentan la estructura, los
obligatorios y las longitudes como los da IRIS, y un valor que IRIS rechaza en una tabla que su esquema trae con valores queda sin
decidir.

## Hechos

1. **Las versiones:** 108 de la 2.6, 64 de la 2.8, 44 de la 2.5.1, 6 de la 2.3 y 1 de la 2.4.
2. **Contra v2.5 (etapa 31) no salió ninguna válida:**
   - 2.5.1: 11 inválidas y 33 sin decidir (14 solo por la versión de MSH-12);
   - 2.6: 95 inválidas y 13 sin decidir (8 solo por MSH-12);
   - 2.8: 58 inválidas y 6 sin decidir.
3. **Parte de lo que hacía inválidas las muestras contra v2.5 venía de la versión:** segmentos y campos que v2.5 no define,
   longitudes de v2.5 y obligatorios de v2.5. Lo que viene de la propia muestra (un obligatorio vacío, un valor demasiado largo para
   su versión) sigue contando.
4. **Las muestras son los mensajes de prueba** que cada proyecto escribió para su conversor, no mensajes completos.
5. **En la etapa 30,** con los mensajes sintéticos del laboratorio y contra v2.5, salieron un 38 % válidos.
6. **Dos discrepancias nuevas publicadas** (VX-M14 y VX-M15) no tienen ningún mensaje válido. Los del laboratorio quedan sin
   decidir. VX-M14 se apoya en 1 muestra de la 2.6; VX-M15, en 6: cinco de la 2.6 y una de la 2.5.1.

## Las preguntas

- ¿Qué proporción de las 223 muestras sale válida en su versión?
- ¿Cuántas de VX-M14 y VX-M15 siguen sin ningún mensaje válido?
