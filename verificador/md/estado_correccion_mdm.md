# Estado: dos discrepancias publicadas que se apoyan en mensajes fuera de la tabla de estados del estándar (31-oct-2026)

Redactado el 31-oct-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

Un verificador publicó esta madrugada que encuentra 5 discrepancias nuevas y confirmadas en dos conversores HL7 v2 → FHIR al
convertir documentos clínicos (MDM^T02). Cada una se reprodujo con un par mínimo. Una revisión a ciegas de la etapa siguiente ha
señalado que dos de ellas se apoyan en mensajes T02 con un estado que el estándar no da para T02.

## Hechos (comprobados en HL7 v2.5, capítulo 9)

1. **La figura 9-2, la tabla de transiciones de la disponibilidad del documento (TXA-19),** da para T02 un único estado nuevo:
   «Available». «Obsolete» solo aparece en T04 (cambio de estado). «Unavailable» aparece en T01, T03, T05, T07 y T09.
2. **La tabla 0273** define UN como «Unavailable for patient care», no como «desconocido». La etapa lo había descrito como
   «disponibilidad desconocida».
3. **La definición de TXA-19** dice que, si las reglas de una organización permiten usar un documento antes de autenticarlo, el
   campo debe valer AV. Leída sola, deja sitio a otros valores antes de autenticar. La tabla de transiciones, no.
4. **Las dos discrepancias afectadas:**
   - **Microsoft convierte TXA-19 OB (obsoleto) en `entered-in-error`.** Se midió con un T02 con OB, que la figura 9-2 no da. El
     único evento donde OB cabe es T04, y Microsoft no trae plantilla de T04, así que no se puede reproducir en un mensaje que el
     estándar dé por válido.
   - **LinuxForHealth convierte TXA-19 UN en `current`, sin conservar el código.** Se midió con un T02 con UN, que la figura 9-2
     tampoco da para T02. LinuxForHealth solo convierte T02 y T06, y los dos dan «Available».
5. **Las otras tres discrepancias** no dependen de esos estados: un rechazo por TXA-8 repetido, el texto perdido tras un OBX
   codificado y el formato crudo de un FT. Sus pares usan estados que la tabla sí da para T02.
6. **Seis de las 40 bases sintéticas llevan estados fuera de la tabla de T02:** DI, DO o vacío en TXA-17; UN, CA u OB en TXA-19.
   La estructura es válida en v2.5.

## La pregunta

¿Cómo quedan esas dos discrepancias?
- (a) **Se retiran:** no cuentan como nuevas, porque se apoyan en mensajes que el estándar no da por válidos. El resultado pasa de
  5 a 3 y se publica la corrección.
- (b) **Pasan a dudosas:** no cuentan, pero se dejan descritas con el argumento en contra y el matiz a favor de la definición. El
  resultado pasa igualmente de 5 a 3.
- (c) **Se mantienen como nuevas,** con la tabla de transiciones como ambigüedad declarada.
