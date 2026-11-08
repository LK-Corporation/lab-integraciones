# Estado: la previsión de la etapa 38, las clases publicadas del estudio (8-nov-2026)

Redactado el 8-nov-2026. **A propósito NO incluye la recomendación de nadie.** Se sella antes de medir la causa.

## Contexto

El estudio de conversores (etapa 14l, 24-oct) publicó sus clases en `cv/CLASES-CV3.json`. Al recalcularlas en la etapa 37, tres
clases dan otros casos que los publicados, aunque la frase del estudio sale igual. La etapa 38 busca por qué.

## Hechos

1. **Lo que difiere:**
   - M-4 tenía 16 casos en ADT y hoy da 8; falta `A1-A01-03`, entre otros;
   - M-36 tenía 1 en las muestras y hoy ninguno;
   - L-24 tenía 2 en las muestras y hoy ninguno. Falta `ms-LRI_2.0-NG_CBC_Typ_Message`, que también era de M-36.

   La frase sale igual: 15, 31 y 16, con 2 rechazos nuevos, 3 dudosas y 368 mensajes.
2. **Las cifras publicadas no han cambiado desde el 24-oct.**
   - Salen del cálculo del estudio, con el juez de entonces (`54a90cd9`).
   - Las etapas 29 y 30 tocaron el JSON (notas y textos) sin recontar los casos.
3. **El cálculo de hoy:**
   - `cv/juzgar_cv2.py` sobre `privado/cv/cv2/ev`, y `cv/cv3_clases.py` sobre su detalle, `cv/RESULTADO-CV3-minimos.json` y la misma
     carpeta;
   - con el juez de antes de la 37 (`117c787d`) y con el de la 37;
   - la receta exacta del 24-oct (qué detalle, qué carpetas, qué mínimos) no está medida.
4. **Lo que cambió desde el 24-oct:**
   - **el juez,** en las etapas 20 (VXU), 26 (MDM), el 4-nov (textos) y la 37. Los rejuicios de la 21, la 26 y el 4-nov dieron 0
     diferencias en lo que rejuzgaron;
   - **`cv/cv3_clases.py`,** solo en la descripción y el mecanismo de M-28 (etapas 36 y 37).

## Las preguntas

**Q-PREV-CL-1.** ¿De dónde viene la diferencia?
- (a) La entrada: las clases de hoy se calculan con otras evidencias, otro detalle u otros mínimos que las del 24-oct.
- (b) El aparato: `cv/cv3_clases.py` o lo que lee cambió desde el 24-oct.
- (c) El juez: algún cambio entre el 24-oct y el 7-nov cambió los hallazgos de esos casos.
- (d) Más de una de las tres.

**Q-PREV-CL-2.** Con la receta del 24-oct, ¿cambia alguna cifra de la frase del estudio?
- (a) No.
- (b) Sí.
