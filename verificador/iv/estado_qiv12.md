# Estado: dos decisiones que abrió la revisión a ciegas de la etapa 30 (4-nov-2026, noche)

Redactado el 4-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 30 pasó los 723 mensajes sintéticos publicados por el validador de IRIS, y cuenta solo lo que el texto de HL7 v2.5
sostiene. Una longitud cuenta si el valor pasa el LEN del estándar (Q-IV-D-9). Una discrepancia nueva publicada está afectada
solo si sus mensajes de apoyo son inválidos por una regla que toca su campo (Q-IV-D-6). La revisión a ciegas, antes de publicar,
encontró dos cosas que el diseño no decidía.

## Hechos

1. **Valores que la tabla del campo admite pero no caben en su LEN.**
   - En TXA-3, el texto remite a la tabla 0191 «para los valores válidos», y la 0191 trae `TEXT` (4 letras) y `multipart`
     (9). El LEN de TXA-3 en v2.5 es 2. La tabla trae también `TX`, de 2 letras, para texto.
   - En OBX-2 pasa lo mismo: la tabla 0125 trae tipos de tres letras, como XPN, y el LEN es 2.
   - El estándar se contradice consigo mismo en los dos campos.
   - **En los datos:** 200 mensajes de MDM llevan `TEXT` y 6 `multipart`; 2 de ORU llevan tres letras en OBX-2.
   - **Lo que se hizo:** `TEXT` contó como inválido, porque para texto la tabla da `TX`; `multipart` y OBX-2 quedaron sin
     decidir. La revisión lo señala como un trato distinto de la misma contradicción.
   - **Lo que cambia:** si `TEXT` queda sin decidir, los inválidos bajan de 440 a unos 240 y los sin decidir suben de 6 a unos
     206. Si `multipart` y OBX-2 cuentan, los inválidos suben en unos 8.
2. **La salvedad de las nuevas cuyo apoyo es inválido por otra regla.**
   - De las 27 nuevas publicadas, ninguna tiene inválido su propio campo. Pero 14 se apoyan solo en mensajes inválidos por otras
     reglas: UCUM en las unidades, TXA-3 o los obligatorios de ADT. Con la pregunta tal como la fijó el ANTES («por una regla que
     el estándar sostiene», sin el campo), serían 14.
   - La etapa 29 marcó en los ficheros de clases publicados la salvedad de cada clase que tocó.

## Las preguntas

- **Q-IV-D-12, un valor que la tabla del campo admite pero no cabe en su LEN:**
  - (a) cuenta como inválido siempre (Q-IV-D-9 tal cual);
  - (b) queda sin decidir siempre, porque el estándar se contradice;
  - (c) cuenta solo si la tabla trae otro valor equivalente que cabe (`TEXT` frente a `TX`), y si no, sin decidir.
- **Q-IV-D-13, la salvedad de las 14:**
  - (a) solo en el resultado de la etapa, junto a la frase;
  - (b) además, una marca en cada clase de los ficheros de clases publicados, como en la 29.
