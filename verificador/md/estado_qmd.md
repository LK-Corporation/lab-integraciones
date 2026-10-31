# Estado: doce decisiones de diseño del juez de conversiones MDM_T02 (31-oct-2026)

Redactado el 31-oct-2026. **A propósito NO incluye la recomendación de nadie**, tampoco la del diseñador.

## Contexto

Un verificador determinista juzga lo que devuelve un conversor HL7 v2 → FHIR R4 de terceros contra la guía HL7 v2-to-FHIR.
Se amplía a los mensajes de documentos clínicos MDM_T02. La guía lleva cada documento a un recurso `DocumentReference`: la
cabecera (TXA) da sus metadatos y los OBX, su contenido.

**Las reglas fijas:**
- manda el estándar: HL7 v2.5, FHIR R4 y la guía en el commit leído;
- lo que la guía admite es convención y no cuenta;
- toda regla que cuente lleva su cita;
- los veredictos de los tipos de mensaje que ya juzgaba no cambian;
- el contenido del documento no se juzga por lo que dice, solo por cómo se lleva.

El diseño lo hizo otro modelo, a ciegas de lo que devuelven los conversores, y deja abiertas estas doce preguntas. Una
discrepancia que cuenta tiene que cambiar el significado del dato.

## Las preguntas, con lo que cambia según la respuesta

1. **Qué eventos se juzgan.** T04, T06, T08 y T10 (cambios de estado, añadidos, ediciones y sustituciones del documento)
   tienen la misma estructura que T02, pero la guía solo trae el mapa de T02. El plan de la etapa deja fuera la semántica de
   los cambios de estado.
   - (a) Solo T02. Los demás quedan fuera de alcance.
   - (b) T02 y esos cuatro, con el mismo perfil y una nota del evento. No se juzgan las transiciones de estado. Entran cuatro
     bases más y las muestras públicas de esos eventos.
2. **Los recursos de procedencia y la cabecera del mensaje** (`Provenance` y `MessageHeader`). La guía crea un `Provenance`
   «si el implementador quiere», y otros desde EVN, PID y MSH. En los tipos que ya juzga, el juez los trata como nota.
   - (a) Fuera, como nota.
   - (b) Solo que existan.
   - (c) Con sus campos (fecha, autor, motivo), emparejados con su documento.
3. **El tipo MIME del contenido.** Los literales de la guía son `application/text` para TX y `text/hl7v2` para FT, y ninguno
   de los dos está registrado; `text/plain` sí lo está. ED y RP dan un subtipo, no un tipo completo. Afecta a unas 30 bases.
   - (a) Solo los literales de la guía. Un conversor que escriba `text/plain` suma una discrepancia en cada base de texto.
   - (b) Los literales o el tipo registrado equivalente.
   - (c) Solo que el tipo no contradiga el dato (texto para TX y FT; el subtipo para ED y RP).
4. **El estado del documento (`docStatus`, desde TXA-17).** La guía copia el código de v2 sin traducirlo. FHIR R4 ata ese
   campo a un conjunto de cuatro valores que no son los de la tabla v2 (0271), así que el literal de la guía no es FHIR válido.
   Afecta a las 40 bases.
   - (a) Solo el literal de la guía. Un valor válido de FHIR cuenta como distinto.
   - (b) El literal o un mapa sacado de las definiciones de v2.5 y R4, y el literal cuenta además como FHIR inválido. Todo
     conversor fiel a la guía suma una discrepancia en todas las bases.
   - (c) El literal o el mapa, sin penalizar el literal. Cuentan la ausencia, un valor incoherente y lo que no es ni lo uno ni
     lo otro.
   - (d) Solo valores válidos y coherentes. El literal y la ausencia cuentan.
5. **Varios OBX del mismo tipo** (las secciones de un informe). La guía no dice si van en un bloque de contenido o en varios.
   - (a) Cualquier reparto, mientras todo llegue entero y en orden.
   - (b) Un único bloque por tipo.
   - (c) Un bloque por OBX.
6. **El paciente y el episodio del documento** (`subject` y `context.encounter`) cuando faltan. La guía no tiene fila para
   ellos; FHIR solo dice que el paciente del documento es el del mensaje. Afecta a las 40 bases.
   - (a) Su ausencia es nota. Si están y son otros, sí cuenta.
   - (b) Su ausencia cuenta como dato perdido.
7. **El enlace con las órdenes** cuando el documento cubre varias (varios grupos ORC/OBR). La guía escribe una referencia a
   la primera orden; el estándar dice que el documento satisface todas.
   - (a) Basta una referencia a alguna.
   - (b) Una referencia por cada orden.
8. **Un recurso `Observation` (o `DiagnosticReport`) en el Bundle de un MDM.** La guía lleva el OBX al documento, no a
   `Observation`.
   - (a) Nota.
   - (b) Recurso inventado, que cuenta.
9. **La disponibilidad del documento (TXA-19) cuando es «cancelado», «obsoleto» o «desconocido».** La guía solo pone el
   código en una extensión y deja sin valor el estado obligatorio del recurso.
   - (a) El estado puede ser cualquiera válido; el código tiene que estar en la extensión.
   - (b) Lo anterior, y además el estado tiene que ser coherente: cancelado → `entered-in-error`, obsoleto → `superseded`.
   - (c) La extensión no cuenta; solo que el estado sea válido.
10. **Cuánto se juzga de la orden** (`ServiceRequest`).
   - (a) Que exista, su paciente, sus identificadores, su código, y que su estado y su intención sean válidos (43 a 46
     reglas en total).
   - (b) Solo que exista y que el documento la enlace.
   - (c) Además el solicitante, la fecha y las notas (hasta 49 reglas).
11. **Varios autenticadores (TXA-10 repetido)** cuando el recurso admite uno.
   - (a) El esperado es el primero.
   - (b) Vale cualquiera; los demás son nota.
12. **OBX con tipos que la guía no lleva a ningún sitio** (códigos, cadenas, números, fechas). El estándar dice que el
   contenido de un documento puede ir en uno o más OBX.
   - (a) Nota: sin destino en la guía no hay valor esperado.
   - (b) Dato perdido, si su valor no está en ninguna parte del documento ni de sus referidos.
