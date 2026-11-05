# Estado: qué regla de Q-VD-3 va en el titular de la etapa 32 (5-nov-2026)

Redactado el 5-nov-2026, después de correr. **A propósito NO incluye la recomendación de nadie.**

## Contexto

Q-VD-3 decide qué pasa con una muestra cuyo único problema es un segmento con más campos de los que define su versión. Mueve 13
de las muestras (de VXU de la 2.5.1, con MSH-22 y MSH-23 con valor). Esta pregunta no es sobre la regla en sí, sino sobre cómo
seguir.

## Hechos

1. **El ANTES de la etapa, sellado antes de correr,** fijó «aparte, como en la 31» (Q-VD-3b). Con esa regla: 21 válidas, 141
   inválidas y 61 sin decidir.
2. **Q-VD-3 se ha preguntado tres veces:**
   - antes de correr, «dentro» (0,75), con un estado sin las reglas del receptor;
   - antes de correr, «aparte» (0,95), con un estado sin hechos del otro lado;
   - después de correr, «sin decidir» (0,71), con un estado que el revisor a ciegas da por no neutral. Le faltaban hechos a favor
     de «aparte»: que HL7 añade campos nuevos al final de un segmento (v2.5.1, CH02.txt:1117), y que MSH-22 y MSH-23 los definen
     los esquemas de IRIS de versiones posteriores, así que no son campos locales. Le faltaba uno a favor de «dentro»: Q-VD-1
     cuenta la estructura como la da IRIS. Y traía frases que empujaban hacia «sin decidir».
3. **Las tres cifras se publican en todo caso:** «aparte», 21/141/61; «dentro», 8/174/41; «sin decidir», 8/141/74.
4. **En las etapas 30 y 31,** las decisiones que se volvieron a preguntar tras una revisión, con los hechos que faltaban, pasaron
   al titular. Se declararon como cambios posteriores al sello.
5. **El revisor ofrece dos arreglos:** preguntar otra vez con el estado completo, o dejar en el titular la regla del ANTES y dar
   las otras dos como sensibilidad de una decisión tomada después de correr.
6. **Una cuarta pregunta se haría sabiendo ya el efecto de cada respuesta.**

## La pregunta

- **Q-VD-3d.** ¿Qué regla de Q-VD-3 va en el titular?
  - (a) La del ANTES (aparte, 21/141/61); «sin decidir» y «dentro», como sensibilidad.
  - (b) Una cuarta pregunta con el estado completo, revisado antes por el lector a ciegas; va al titular lo que salga.
