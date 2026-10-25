# La previsión de la etapa 21, sellada antes de correr

Se escribió y se selló antes de cualquier corrida con Docker de esta etapa, ni en lote ni mensaje a mensaje. Es más estricto que el
diseño (`diseno-ar-fable.md` §10), que la ponía tras el humo: el humo ya convierte un mensaje de cada corpus. Las cifras exactas
están en `PREVISION-AR.json`; su huella y la del aparato, en `SELLO-AR.txt`.

## Lo que se espera

- **Lo más probable es que no cambie ningún veredicto** (K = 0). La probabilidad de al menos una diferencia de veredicto por
  arrastre es 0,3, y por cualquier causa, 0,35.
- **Si hay arrastre, lo más probable es que salga en las muestras de los proyectos** (0,6), que traen más campos con solo texto
  donde LinuxForHealth construye un recurso anidado. Siguen ADT (0,25), ORU (0,1) y los mínimos (0,05).
- **La dirección:** el lote añadiría `dato_perdido` tras el disparador, así que mensaje a mensaje saldrían menos hallazgos. La
  probabilidad de una fuga de datos de un mensaje a otro (un dato que solo aparece en lote) es 0,07.
- **Lo que podría cambiar:** L-22 (PV1-52), L-14 (OBX TX), L-9, L-7, L-11 y L-17; los pares L13, L14 y L03. No deberían cambiar
  los mecanismos de plantilla (L-1, L-4, L-10, L-12, L-15, L-16, L-18 a L-21).
- **Alguna cifra publicada cambia:** 0,22. Algún mecanismo aparece, desaparece o cambia de clase: 0,08. Algún par mínimo cambia:
  0,05.
- **Los controles:** el negativo pasa con 0,9 (veredictos 0 y errores 0; el ruido del Bundle, en la fecha de la conversión); el
  positivo VL11 sale con 0,95; el corpus VXU da los 23 de F7 con 0,9. La etapa para por una de sus reglas con 0,12.

## La previsión de Jev, al lado

Se le pasó a Jev un estado neutro (`estado_prevision_ar.md`) con tres preguntas, y su respuesta está en
`decision-jev-prevision-ar.md`. Es bastante más pesimista que la de arriba, que no se cambió al verla:
- **Casos que cambian por arrastre:** ninguno 0,21; de 1 a 5, 0,36; de 6 a 40, 0,35; más de 40, 0,08. Es decir, 0,79 a que cambie
  al menos uno, frente a 0,3.
- **Dónde, si cambia alguno:** las muestras, 0,89; los mínimos, 0,11.
- **Alguna cifra publicada cambia:** 0,85, frente a 0,22.

## La base

Antes de sellar no se corrió nada en esta etapa. Se sabe que el arrastre de F7 (`vx/VX2.md`) va por la referencia a Organization
de un RXA-17 con solo texto. Se leyó, sin ejecutarlo, el código de LinuxForHealth en su rama principal: comparte las plantillas
entre conversiones, pero no se aisló el mecanismo. Y en el control de la etapa 18, la herramienta en lote dio los mismos
veredictos que la corrida del estudio, también en lote, en los 368 casos.
