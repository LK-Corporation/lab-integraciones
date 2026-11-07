# Estado: MD-M5 y un gemelo con contenido que no es texto (etapa 33, 5-nov-2026)

Redactado el 5-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

- **La etapa 33 arregló los generadores del corpus** en una versión 2, y mira cuántas de las 27 nuevas publicadas se reproducen en
  algún mensaje válido de v2.5.
  - Salen 24: 12 en mensajes de su clase o en su par mínimo, y 12 en un gemelo de su mensaje con las unidades en ISO+ (Q-GA-2).
- **Las tres de MDM no se reproducen en ningún mensaje válido:** MD-L3, MD-L5 y MD-M5. Su base y su par mínimo quedan sin decidir,
  y solo por TXA-3 = `TEXT` (Q-IV-D-12).

## Hechos

- **Lo que dice v2.5 de TXA-3:**
  - es obligatorio cuando el mensaje trae contenido en OBX, y su LEN es 2 (CH09.txt:825, 888-890);
  - la 0191 da `AP` (datos de aplicación), `AU` (audio) e `IM` (imagen), «HL7 V2.3 and later», y caben en 2;
  - para el texto da `TEXT`, «V2.3.1 and later», que no cabe; y `TX` y `FT`, «HL7 V2.2 only» (CH09.txt:892-903).
- **Una corrección al estado de Q-GA-1 a 7** (`ga/estado_ga.md` y `ga2`). Decía que ningún MDM_T02 con contenido en OBX puede ser
  válido en v2.5. Solo es cierto del contenido de texto: la versión 2 trae 8 MDM_T02 válidos, con OBX ED o RP y TXA-3 = `AP` o `IM`.
  Ninguna de las siete preguntas era sobre MDM.
- **MD-L3 y MD-L5 son de texto:** el texto de los OBX TX que no llega con un CE delante, y un FT con sus órdenes de formato crudas.
  Sin contenido de texto no hay hallazgo, así que con la lectura de Q-IV-D-12 no pueden salir en un mensaje válido.
- **MD-M5 no es de texto:** Microsoft rechaza entero un MDM_T02 con TXA-8 (fecha de edición, repetible) repetido (`RESULTADO-MDM.md`).
  - Su par mínimo es MP1, y su base, B33. Los dos llevan contenido de texto y TXA-3 = `TEXT`.
  - Nadie ha probado si el rechazo sale también con contenido ED y TXA-3 = `AP`.
- **Un gemelo de MP1 con contenido ED cambiaría más que los gemelos de las unidades.** Aquellos solo cambiaban un componente.
  Este cambiaría el OBX (de TX a ED, con su contenido) y TXA-3. Probar el par costaría unos minutos (los dos mensajes, por IRIS y
  por Microsoft).
- **El ANTES pide, para las 12 con UCUM, que se miren en su gemelo, y para las 27, si se reproducen en algún mensaje válido.** No
  pide gemelos para las de MDM.
- **El cupo de agentes es compartido con el trabajo del autor.** Esto no gasta agentes; lo que gasta es la revisión.

## La pregunta

- **Q-GA-8, MD-M5:**
  - (a) se declara que no se ha probado en un mensaje válido;
  - (b) se hace un gemelo del par MP1 con contenido ED y TXA-3 = `AP`, y se mira si Microsoft lo rechaza igual (caso) y no el
    control.
