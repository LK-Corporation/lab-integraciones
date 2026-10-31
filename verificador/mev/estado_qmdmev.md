# Estado: dos decisiones de método de la etapa de los otros eventos de MDM (31-oct-2026)

Redactado el 31-oct-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

Un verificador determinista juzga lo que devuelven dos conversores HL7 v2 → FHIR contra la guía v2-to-FHIR. Desde hoy juzga los
documentos clínicos MDM^T02. Esta etapa lo amplía a cuatro eventos con la misma estructura (T04, T06, T08 y T10). La guía solo
trae el mapa de MDM_T02 y no da destino a lo que distingue esos eventos (el documento padre, el motivo del cambio). La pregunta es
si los conversores tratan el documento igual que en T02 y, si no, si las diferencias son discrepancias nuevas.

## Hechos

1. **El juez ya trae preparada la ampliación a esos cuatro eventos.** La diseñó a ciegas otro modelo en la etapa anterior, como
   alternativa de una de sus preguntas, y está programada y probada. Hay cuatro mensajes de prueba escritos para ella.
2. **El método de las etapas de tipo nuevo** pide un diseño a ciegas por otro modelo. El cupo del diseñador habitual se agotó esta
   madrugada; en la etapa anterior diseñó otro modelo, más pequeño.
3. **Un corpus derivado:** cada uno de los 40 mensajes de T02, válidos en v2.5 y escritos a ciegas, se puede repetir como T04,
   T06, T08 y T10, cambiando solo el evento y, en T06 y T10, el documento padre que v2.5 exige. Serían 160 mensajes: cada uno es
   un par mínimo de su T02, y cualquier diferencia de veredicto es del evento.
4. **Un riesgo medido en el laboratorio:** un corpus hecho de mutaciones deja una firma mecánica en cada caso. Aquí la diferencia
   mecánica (el evento) es justo lo que se quiere medir.
5. **La otra opción de corpus:** solo las cuatro bases secundarias y las 33 muestras públicas de T06 y T10 (en v2.6 y v2.8, no en
   v2.5).

## Las preguntas

1. **¿Quién diseña?**
   - (a) **El programador,** sobre lo que ya diseñó y programó la etapa anterior, sin nuevo diseño a ciegas. Se declara.
   - (b) **Un diseño a ciegas nuevo** por otro modelo, como en la etapa anterior.
2. **¿Qué corpus?**
   - (a) **El derivado:** los 40 mensajes de T02 repetidos en los cuatro eventos (160), más las bases secundarias y las muestras
     públicas.
   - (b) **Solo las cuatro bases secundarias y las muestras públicas.**
