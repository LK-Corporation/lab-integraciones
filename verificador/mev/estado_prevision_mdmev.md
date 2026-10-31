# Estado: la previsión de la etapa de los otros eventos de MDM, antes de correr los conversores (31-oct-2026)

Redactado el 31-oct-2026. **A propósito NO incluye la previsión ni la recomendación de nadie.**

## Contexto

Un verificador juzga lo que devuelven dos conversores HL7 v2 → FHIR (Microsoft y LinuxForHealth) contra la guía v2-to-FHIR. En
documentos clínicos MDM^T02 encontró 5 discrepancias nuevas. Ahora se mira si los conversores tratan el documento igual en
otros cuatro eventos con la misma estructura (T04, T06, T08 y T10).

El corpus repite cada uno de los 40 mensajes de T02 en los cuatro eventos, cambiando solo el evento y, en T06 y T10, el número
del documento padre que el estándar exige. Cada diferencia de veredicto frente a su T02 es lo propio del evento.

## Hechos

- **Microsoft** trae plantillas de T06 y T10, pero no de T04 ni de T08. Un conversor sin plantilla para un evento no corre ese
  evento, y eso no cuenta como discrepancia.
- **LinuxForHealth** trae las cuatro. Sus muestras públicas de T06 dieron Bundle.
- **La guía** no da destino a lo que distingue esos eventos (el documento padre, el motivo del cambio).

## Las preguntas

1. ¿Correrá Microsoft T04 y T08?
2. En los eventos que cada conversor sí corre, ¿tratará el documento igual que en T02 en todas las bases?
3. ¿Habrá al menos una discrepancia nueva y confirmada?
