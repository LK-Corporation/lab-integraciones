# Estado: Q-IV-D-12 otra vez, con un hecho que faltaba (4-nov-2026, noche)

Redactado el 4-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

Es la misma pregunta que `estado_qiv12.md` (Q-IV-D-12). Aquel estado decía que la tabla 0191 trae `TX`, de dos letras, para
texto, pero no decía para qué versión. La decisión de entonces fue «cuenta solo si la tabla trae otro valor equivalente que cabe;
si no, sin decidir». Se vuelve a preguntar con el hecho entero.

## Hechos

1. **En TXA-3**, el texto remite a la tabla 0191 para los valores válidos, y el LEN de TXA-3 en v2.5 es 2.
2. **En la 0191 de v2.5:**
   - `TEXT` (4 letras) es «documento de texto legible por máquina», marcado «HL7 V2.3.1 y posteriores»;
   - `TX` (2 letras) tiene la misma descripción, marcada «solo HL7 V2.2»;
   - `multipart` (9 letras) no tiene equivalente.

   Para un mensaje de v2.5, el valor vigente de texto es `TEXT`, que no cabe en el LEN. El que cabe es de la 2.2.
3. **En OBX-2**, la tabla 0125 trae tipos de tres letras, como XPN («nombre de persona extendido»). La 0125 trae también PN
   («nombre de persona»), con otra descripción. El LEN es 2.
4. **En los datos:** 200 mensajes de MDM llevan `TEXT`, 6 `multipart`, y 2 de ORU llevan tres letras en OBX-2.
5. **Lo que cambia:** si `TEXT` cuenta, son 440 inválidos y 6 sin decidir; si no, unos 240 inválidos y unos 206 sin decidir.

## La pregunta

Q-IV-D-12, un valor que la tabla del campo admite pero no cabe en su LEN:
- (a) cuenta como inválido siempre;
- (b) queda sin decidir siempre, porque el estándar se contradice;
- (c) cuenta solo si la tabla trae otro valor equivalente que cabe y vale en la misma versión del mensaje (aquí, v2.5); si no,
  sin decidir.
