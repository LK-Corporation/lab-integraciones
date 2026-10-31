# Estado: la previsión de la etapa 26 (MDM_T02), antes de juzgar el corpus (31-oct-2026)

Redactado el 31-oct-2026. **A propósito NO incluye la previsión ni la recomendación de nadie.**

## Contexto

Un verificador determinista juzga lo que devuelven dos conversores HL7 v2 → FHIR R4 de terceros (Microsoft FHIR-Converter y
LinuxForHealth hl7v2-fhir-converter) contra la guía HL7 v2-to-FHIR. Se ha ampliado a los mensajes de documentos clínicos
MDM_T02. Cada documento va a un recurso `DocumentReference`: la cabecera TXA da sus metadatos y los OBX, su contenido.

El juez nuevo tiene 46 reglas, y todas las que cuentan llevan cita. Ahora se va a juzgar a los dos conversores sobre un corpus
sintético de 40 mensajes en v2.5, escrito desde el estándar sin ver lo que hacen los conversores. Una discrepancia cuenta si
cambia el significado del dato. Después se contrasta con lo que cada proyecto ya sabe (sus pruebas, sus salidas esperadas y sus
issues): solo es **nueva** si el proyecto no la tiene declarada, y **confirmada** si se reproduce con un par mínimo y tiene
cita.

## Hechos (medidos sobre los 38 MDM_T02 públicos de los proyectos, no sobre el corpus)

- **Los dos conversores dan un Bundle en los 38.**
- **Microsoft:**
  - el texto de los OBX va a recursos `Observation` y no llega al documento;
  - en 26 de 37 documentos no hay contenido;
  - el documento nunca enlaza a la orden ni lleva fecha.
- **LinuxForHealth:**
  - pone todo el texto en un solo adjunto, entero;
  - enlaza a las órdenes;
  - toma el autenticador de un campo que no es el de la guía.
- **Los dos pierden las notas (NTE) que van bajo un OBX.** El único contenido binario público (ED) llega sin datos en los dos.
- **En las muestras públicas,** el juez dio 3 `correcto` y 35 `fallo_silencioso` en Microsoft, y 36 `fallo_silencioso` y
  2 `indeterminado` en LinuxForHealth.
- **En el tercer tipo de mensaje (VXU),** el mismo método encontró 9 nuevas y confirmadas en los dos conversores.

## Las preguntas

1. ¿Habrá al menos una discrepancia nueva y confirmada en alguno de los dos conversores?
2. ¿Cuántas nuevas y confirmadas en total?
3. ¿En cuántos de los dos conversores habrá alguna nueva y confirmada?
