# Estado: dos decisiones de la etapa 37 tras la revisión a ciegas (8-nov-2026)

Redactado el 8-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 37 arregla dos fallos del juez que encontró la etapa 36:
- **conducta 1:** un valor de PID-8 o NK1-15 fuera de la 0001, una tabla de usuario;
- **conducta 2:** una Observation que sale de ACC o PDA, dos segmentos que la hoja de ADT_A01 de la guía lista sin destino.

El ANTES fija la pregunta: «¿Puede el juez dejar de contar mal las dos conductas, cambiando solo los veredictos de esas dos
conductas?». También fija la regla de parada: «El rejuicio cambia algo fuera de las dos conductas y no se explica: se declara, el
juez no se publica, y se publica lo medido». Y pone fuera de la etapa «otros fallos del juez».

El juez ya está arreglado y el rejuicio hecho: 662 diferencias en 30.118 evidencias. Un lector a ciegas revisó lo preparado para
publicar y pidió cambios. Dos de ellos piden una decisión; el resto son arreglos de texto y del clasificador del rejuicio.

## Hechos comunes

- **La información del juez** (lo que sirve `info_verificador` a quien lo usa) lleva sus límites declarados, L-CV-1 a L-CV-17.
  L-CV-17 es de esta etapa: dice cómo reconoce el juez una Observation de ACC o PDA. Es lo único que lee quien usa el juez sin
  leer los resultados.
- **La huella del juez va a cambiar de todos modos.** El texto de versión del servidor dice «L-CV-1..16», y hay que ponerlo al
  día. Por eso las bases de la integración continua se rehacen otra vez (unos 50 minutos), con o sin cambios en los límites.
  Cambiar el texto de un límite no cambia ningún veredicto. Su prueba (la huella de la información) se pone en rojo antes.

## Q-JZ-6. Qué límites nuevos declara la información del juez

**Medido:**
- **La regla de la 0136 (Q-JZ-3 d) puede atribuir mal.** Una Observation que solo lleva `Y` o `N` se atribuye a ACC o PDA si
  uno de sus campos de la 0136 tiene ese valor.
  - **El caso del lector:** PD1-7 = `Y`, que la guía sí mapea (`MSG_ADT_A01.csv:19`, una Observation), y un PDA con un `Y`. El juez
    nuevo da «recurso sin mapa, de PDA», y cita que la hoja lo lista sin destino. El de antes daba «inventado».
  - Por la misma regla, una Observation de verdad inventada de solo `Y`/`N` se escondería.
  - Ni L-CV-17 ni el resultado lo dicen.
- **Con un OBX y un ACC, el veredicto puede cambiar.** Si el conversor solo saca la Observation de ACC, el juez de antes daba
  `correcto` (la emparejaba con el OBX), y el nuevo da `fallo_silencioso` (recurso sin mapa, y el OBX sin su Observation). En el
  corpus no pasa.
- **Otro fallo del juez, de antes de la etapa:** la Observation que la guía crea desde PD1-7 no se empareja con su campo; pasa por
  una de los OBX, por orden. Lo encontró el diseño.
  - El arreglo lo declaraba como límite, L-CV-18.
  - Se quitó del juez después de sellar la previsión, por ser de fuera de la etapa.
  - El resultado lo cuenta como «visto de paso» y explica por qué se quitó.
  - El lector dice que así un fallo conocido queda fuera de la información del juez, y que explicar por qué se quitó es decir
    por qué falta algo.
- **En el corpus:** ninguna de las 21.553 evidencias de ADT lleva PD1-7.

**Las opciones:**
- **(a) Las dos en el juez.**
  - L-CV-17 dice también los dos riesgos de la regla: la atribución de una Observation de solo Y/N, y el veredicto que puede
    cambiar.
  - Vuelve L-CV-18 (PD1-7), como límite declarado; el fallo no se arregla.
- **(b) Solo los riesgos de esta etapa.** L-CV-17 dice los dos riesgos. PD1-7 se queda en el resultado, como visto de paso.
- **(c) Nada en el juez.** Los dos riesgos y PD1-7, solo en el resultado.

## Q-JZ-7. Las 2 evidencias de VXU con NK1-15 = `F^^^M`

**Medido:**
- **Las dos son muestras de Microsoft,** mensajes VXU de v2.8. En v2.8, NK1-15 es un CWE, y `F^^^M` es el código `F`, de la 0001.
  Microsoft da `female`, que es lo correcto.
- **El juez lee NK1-15 entero, como en v2.5,** donde es un IS sin componentes. Ve el valor `F^^^M`, que no está en la 0001.
  - Así lo hacía ya el juez de antes. Es otro fallo, anterior a la etapa: L-CV-16 declara que los tipos son los de v2.5.
  - Con el juez de antes daba una nota de versión, «valor imposible», que no cuenta.
  - Con el nuevo da una nota de versión «fuera del ConceptMap», que tampoco cuenta.
  - El veredicto no cambia.
- **El cambio sale de la rama de la conducta 1,** sobre un valor que no está fuera de la 0001.
  - El clasificador del rejuicio las cuenta en la conducta 1 porque solo mira la forma del hallazgo, y el lector lo señala.
  - Si mira el valor de verdad (el componente 1), salen «fuera».
- **La previsión** las contaba en sus cifras (501), y su nota decía «en VXU ninguna».
- **Ninguna otra de las 662 tiene este problema.**

**Las opciones:**
- **(a) Conducta 1, nombradas.** La frase dice «todas de esas dos conductas», y el resultado nombra las 2 y su causa.
- **(b) Aparte, explicadas.** No son de ninguna de las dos conductas, pero tienen explicación: el resultado dice «660 de las dos
  conductas y 2 de una lectura de NK1-15 que el juez ya hacía mal», y la regla de parada no salta, porque se explican.
- **(c) Fuera: salta la regla de parada.** El juez no se publica, y se publica lo medido.
