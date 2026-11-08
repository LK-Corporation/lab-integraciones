# Estado: qué se hace con la regla de M-4 (etapa 38, 8-nov-2026)

Redactado el 8-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 38 busca por qué tres clases del estudio de conversores publicado (M-4, M-36 y L-24) no dan hoy los casos de su JSON,
`cv/CLASES-CV3.json`. Su ANTES dice que, si hay que cambiar código, el diseño va a ciegas antes y cada cambio lleva su prueba en
rojo antes. Y que los resultados sellados no se tocan: una corrección va con un bloque nuevo en su sello.

## Hechos (medidos)

1. **El JSON publicado se reproduce con su receta.** Con el juicio del estudio (CV3, juez `54a90cd9`) y el `cv/cv3_clases.py` de
   hoy, las clases, sus casos, sus ejemplos y la frase salen iguales. Nada queda sin clase.
2. **El juez cambió en CV4,** el mismo 24-oct, después de escribirse las clases. `RESULTADO-CONVERSORES.md` lo declara:
   - **CX.4 en system** se compara sin espacios ni signos: desaparecen tres falsos positivos, y por eso M-36 y L-24 (falsos
     positivos del juez, ya apartados) se quedan sin casos;
   - **PL.9 dentro de la descripción** pasa a «valor distinto» (Q-CV-D-14, Jev: cuenta, y Microsoft lo declara, M-4). Su texto
     pasa de «falta la descripción…» a «la descripción … contiene PL.9 … sin ser PL.9»;
   - el documento dice que «M-4 es ya declarada en los dos jueces» y que la frase no cambia.

   El juicio de hoy es idéntico al de CV4 en los 736 casos.
3. **La regla de M-4 no sigue el texto nuevo.** En `cv/cv3_clases.py`, M-4 pide el texto «falta la descripción».
   - Con el juez de CV4 (y el de hoy), los 8 hallazgos de PL.9 de Microsoft quedan **sin clase**, y M-4 baja de 16 casos a 8.
   - El guion dice que «comprueba que nada que cuente quede sin clase», pero lo lista sin fallar.
   - Ya pasaba en las clases que calculó la etapa 37, que no lo dijo.
   - La frase no cambia: M-4 sigue con casos, y las 8 siguen siendo de Microsoft y ya declaradas por la decisión Q-CV-D-14.
4. **Así se hizo con M-28 en la etapa 37:** su regla reconoció también el hallazgo nuevo del juez, con un bloque 8 en el sello de la
   etapa 33. El JSON publicado no se tocó.
5. **Arreglar la regla de M-4:**
   - es aceptar los dos textos;
   - lleva un diseño a ciegas, por la condición del ANTES (pequeño, de un modelo), una prueba en rojo antes y un bloque 9 en el
     sello de la 33;
   - con ella, el juicio de hoy da M-4 con 16 casos y nada sin clase;
   - se publica con la opción B, con un lector a ciegas.
6. **Declararlo solo:** el resultado de la etapa lo dice, y la regla se queda como está. Con el juez publicado, 8 hallazgos siguen
   sin clase en cualquier recálculo.

## La pregunta

**Q-CL-1.** ¿Qué se hace con la regla de M-4?
- (a) Arreglarla, para que reconozca también el texto del juez de CV4: diseño a ciegas, prueba en rojo, bloque 9 del sello.
- (b) Declararlo en el resultado, sin tocar la regla.
