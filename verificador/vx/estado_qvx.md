# Estado: diez decisiones de diseño del juez de conversiones VXU_V04 (25-oct-2026)

Redactado el 25-oct-2026. **A propósito NO incluye la recomendación de nadie**, tampoco la del diseñador.

## Contexto

Un verificador determinista juzga lo que devuelve un conversor HL7 v2 → FHIR R4 de terceros contra la guía HL7 v2-to-FHIR.
Se amplía a los mensajes de vacunación VXU_V04, que van a un recurso Immunization por cada vacuna.

**Las reglas fijas:**
- manda el estándar: HL7 v2.5, FHIR R4 y la guía en el commit leído;
- lo que la guía admite es convención y no cuenta;
- toda regla que cuente lleva su cita;
- los veredictos de los tipos de mensaje que ya juzgaba no cambian.

El diseño lo hizo otro modelo, a ciegas de lo que devuelven los conversores, y deja abiertas estas diez preguntas. Una
discrepancia que cuenta tiene que cambiar el significado del dato.

## Las preguntas, con lo que cambia según la respuesta

1. **Los identificadores de sistema de las vacunas y de los fabricantes.** El paquete de la guía no trae los de CVX (vacuna) y
   MVX (fabricante). Para otros catálogos (LOINC, SNOMED, UCUM) el juez ya fija los identificadores canónicos con cita
   externa.
   - (a) Se fijan los de CVX y MVX igual. Un sistema distinto en el código de la vacuna o del fabricante cuenta.
   - (b) El sistema es convención, y solo cuenta el código.
2. **El sistema del sitio de administración (RXR-2).** El mapa del segmento apunta a una tabla (la 0550), la tabla de
   atributos de v2.5 a otra (la 0163), y el texto del estándar admite las dos.
   - (a) Vale el de la tabla donde esté el código: cuentan las dos identidades.
   - (b) Solo la 0550, literal del mapa: un código que solo está en la 0163 se queda sin esperado y no se juzga.
   - (c) Solo la 0163, literal de la tabla de atributos.
3. **La fecha de registro.** Dos campos (ORC-9, sin condición, y RXA-22, solo si RXA-21 es «A») van al mismo elemento.
   - (a) Vale cualquiera de los dos.
   - (b) Manda ORC-9.
   - (c) Manda RXA-22 cuando RXA-21 es «A».

   Con (b) o (c), un mensaje con los dos valorados y distintos puede dar un valor distinto.
4. **Un OBX de la vacuna sin Observation pero con su valor en un elemento de la Immunization** (elegibilidad, financiación,
   información al paciente). La guía deja esta regla a las guías de implementación.
   - (a) Convención.
   - (b) Recurso ausente, literal de la fila que manda una Observation: cada OBX así cuenta.
5. **Qué segmentos de paciente entran.**
   - (a) NK1, con un perfil reducido, y PD1 fuera.
   - (b) Ninguno, solo Patient e Immunization.
   - (c) Los dos; con PD1, el médico de cabecera cuenta.
6. **La función del profesional ausente** (quién administró y quién ordenó) con los campos valorados. La guía la fija, pero en
   FHIR el vínculo es extensible.
   - (a) Dato perdido siempre.
   - (b) Convención con un solo profesional; dato perdido con dos que no se distinguen.
   - (c) Convención.
7. **«Fuente primaria» y «subpotente» escritos por omisión, sin campo que los sostenga.** Para un caso parecido, el sexo
   «desconocido» escrito sin dato, ya se decidió que era dato inventado.
   - (a) Dato inventado.
   - (b) Convención.

   Afecta a todas las bases.
8. **RXA-15 repetido** (el lote de la vacuna y el del diluyente) va a un elemento de cardinalidad 0..1.
   - (a) Se espera la primera repetición.
   - (b) Vale cualquiera.
   - (c) Convención.
9. **Con visita y Encounter presentes, la Immunization sin referencia al Encounter.** La hoja no tiene fila para esa
   referencia.
   - (a) Convención.
   - (b) Dato perdido.
10. **Los OBX de la vacuna.**
    - (a) Se juzgan con todas las reglas que ya se aplican a los resultados de laboratorio: estado, código, valor, unidades,
      interpretación.
    - (b) Solo su existencia y sus referencias.
