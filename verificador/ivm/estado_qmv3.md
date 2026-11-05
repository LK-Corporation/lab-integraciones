# Estado: MSH-12 con otra versión en las muestras (Q-MV-3) (4-nov-2026, noche)

Redactado el 4-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 31 validó las 225 muestras públicas de los dos conversores contra v2.5, como las lee el juez de los estudios (Q-MV-1).
Una revisión a ciegas, de un segundo lector, señala como bloqueante que una regla de la lectura no se hereda de la etapa 30, que
es lo que dice el ANTES de la 31. Es la regla de MSH-12, la versión que declara el mensaje.

## Hechos

1. **Q-MV-2 preguntó** «qué se hace con un error que no se puede leer con el texto de v2.5 o v2.5.1». La decisión fue «se da
   aparte y no entra en el veredicto» (0,82).
2. **La lectura de la 31 pone aparte cuatro cosas:**
   - un segmento que v2.5 no define;
   - un campo que su tabla de atributos no trae;
   - una tabla que el índice del Apéndice A no trae;
   - MSH-12 con una versión que no está en la tabla 0104 de v2.5.
   Las cuatro estaban en la lectura sellada antes de pasar ninguna muestra por IRIS.
3. **La 0104 está impresa en el texto de v2.5** (CH02.txt:4525-4534): trae de la 2.0 a la 2.5, y no la 2.5.1, la 2.6 ni la 2.8.
   Es una tabla de HL7. El texto dice que una tabla de HL7 puede ampliarse con valores definidos localmente (CH02.txt:563-565).
4. **La regla de la 30 para un valor fuera de la lista impresa de una tabla de HL7** es Q-IV-D-11b: queda sin decidir, siempre.
   La 30 la aplicó también a MSH-12: `2.5.1` en 8 mensajes y `2.6` en 1 quedaron sin decidir.
5. **El ANTES de la 31 dice:** «Las de la 30 se heredan.» Las decisiones nuevas de la 31 son Q-MV-1 y Q-MV-2.
6. **El juez de los estudios** acepta MSH-12 2.x desde la 2.4 (decisión S19), y aplica a esos mensajes las reglas, las tablas y las
   longitudes de v2.5 (limitación L17). Un mensaje de la 2.3 lo rechaza con AR 203.
7. **IRIS no marca MSH-12** en las 6 muestras de la 2.3 ni en la de la 2.4, porque están en la 0104 de v2.5.
8. **Lo que da cada regla,** con todo lo demás igual:
   - MSH-12 aparte: 22 válidas, 171 inválidas y 32 sin decidir;
   - MSH-12 sin decidir (Q-IV-D-11b): 0 válidas, 171 inválidas y 54 sin decidir.

   Las 22 son 14 de la 2.5.1 y 8 de la 2.6. No tienen ningún otro error sostenido ni sin decidir. Las inválidas no cambian. Lo de
   las nuevas tampoco: con las dos reglas, VX-M14 y VX-M15 quedan sin ningún mensaje válido y ninguna queda afectada.
9. **La frase que pide el «Hecho cuando»** dice cuántas muestras son válidas. Con la regla de la 30, dice 0.

## La pregunta

Q-MV-3, qué se hace con MSH-12 cuando la muestra declara una versión que no está en la 0104 de v2.5:
- (a) queda sin decidir, como en la 30 (Q-IV-D-11b);
- (b) va aparte, declarado como una diferencia con la 30 por la decisión S19 del juez.
