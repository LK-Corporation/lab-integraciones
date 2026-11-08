> *Copia pública: el párrafo «Fijado en autónomo» marca como no publicadas la hoja de ruta y la decisión de ruta del laboratorio; el resto va literal.*

# ANTES: etapa 38, las clases publicadas del estudio de conversores (FIJADO el 8-nov-2026)

**Fijado en autónomo**, dentro de la hoja de ruta (`HOJA-DE-RUTA.md`, no publicada). Jev eligió esta etapa con 0,95 (`decision-jev-ruta21.md`, no publicada);
pausar quedó en 0,03.

## La pregunta (fija)

> ¿Por qué tres clases del estudio de conversores publicado (M-4, M-36 y L-24) no dan hoy los casos de su JSON publicado,
> `cv/CLASES-CV3.json`? ¿Se reproduce ese JSON, entero, con su receta?

## Punto de partida (medido)

- **El cálculo de la etapa 37.** Las clases se calcularon con `cv/juzgar_cv2.py` sobre `privado/cv/cv2/ev` y `cv/cv3_clases.py`
  sobre su detalle, `cv/RESULTADO-CV3-minimos.json` y la misma carpeta. Se hizo con el juez de antes de la 37 (`117c787d`) y con el
  nuevo.
  - La frase sale igual: 15 nuevas, 31 ya declaradas, 16 convenciones, 2 rechazos nuevos, 3 dudosas y 368 mensajes.
  - Tres clases dan otros casos:
    - M-4 tenía 16 en ADT y da 8; falta `A1-A01-03`, entre otros;
    - M-36 tenía 1 en las muestras y no da ninguno;
    - L-24 tenía 2 en las muestras y no da ninguno. Falta `ms-LRI_2.0-NG_CBC_Typ_Message`, que también era de M-36.
- **El JSON publicado** lo escribió por última vez la etapa 30, con el juez `54a90cd9`. Entre la 30 y la 37, el juez cambió el
  4-nov (`117c787d`, solo en textos, con 0 diferencias en el rejuicio).
- **La receta exacta** con que se escribió (qué detalle, qué carpetas de evidencias, qué mínimos) no está medida.

## Condiciones que no se negocian

1. **Lo de siempre:**
   - el código de terceros corre en su caja;
   - los proyectos de los conversores no se tocan;
   - cada push, por la opción B, con el ensayo y la comprobación de después del push.
2. **Primero se mide, sin cambiar nada.** Se reproduce el JSON publicado con su receta y, si no sale, cada caso que difiere se
   explica.
3. **Si hay que cambiar código,** el diseño va a ciegas antes y cada cambio lleva su prueba en rojo antes.
4. **Los resultados sellados de etapas pasadas no se tocan.** Si el JSON publicado está mal, se marca, y la corrección va con un
   bloque nuevo en su sello y con lo que cambie dicho en el resultado de esta etapa.

## Qué se mide

- **Cada caso que difiere** entre el JSON publicado y el reproducido, con su causa: la entrada (qué evidencias o qué detalle), el
  aparato (`cv/cv3_clases.py` y sus sellos) o el juez.
- **Si cambia la frase** del estudio.

## Previsión (se sella antes de medir la causa)

De dónde viene la diferencia (la entrada, el aparato o el juez), y si cambia alguna cifra de la frase.

## Hecho cuando

- **Un documento de resultado,** `RESULTADO-CLASES.md`, con la frase: «Las clases publicadas del estudio de conversores [se
  reproducen / no se reproducen] con su receta; la diferencia de M-4, M-36 y L-24 viene de [la causa]».
- **Si cambia algo publicado,** publicado con la opción B y comprobado después del push.

## Tope

**Una sesión, y un lector a ciegas** (hasta dos pasadas) si se publica.

## Regla de parada

- **La causa no se encuentra dentro del tope:** se declara lo medido, y se publica eso.

## Fuera de la etapa

- Los otros cabos de la 37: el fallo del juez con PD1-7 y la lectura de los tipos de v2.6 y posteriores.
- Rehacer el estudio.
