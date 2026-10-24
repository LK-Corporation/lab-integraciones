# Estado: doce decisiones de diseño para juzgar conversores HL7 v2 → FHIR de terceros (etapa 14l)

Redactado el 23-oct-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

Un verificador determinista (el juez) juzga circuitos de integración HL7 v2 → FHIR R4. Hasta hoy, siempre circuitos del
propio laboratorio, con acuse (ACK), log y un «canónico» intermedio.

Ahora va a juzgar **conversores de código abierto de terceros**: programas que reciben un mensaje HL7 v2 y devuelven un
Bundle FHIR, o un error.
- No hay ACK, ni log, ni canónico.
- Lo esperado sale de la guía oficial HL7 v2-to-FHIR (sus ConceptMap), no de las decisiones propias del laboratorio.
- El resultado de la etapa cuenta las discrepancias que «cambian el significado del dato», tienen cita y el proyecto no tiene
  ya declaradas. Si no aparece ninguna, el verificador se declara pieza de portfolio.

Una diferencia que la guía o el estándar admiten es **convención**, y no cuenta. Las preguntas de abajo son puntos donde
ni el estándar ni la guía deciden solos.

## Hechos

1. **Un «punto de entrada»** es el contrato del receptor escrito como datos: los tipos y eventos que admite, los segmentos que
   consume y sus reglas. Ya existen `adt_fhir` (8 eventos ADT → Patient y Encounter) y `oru_fhir` (ORU^R01 → Observation y
   DiagnosticReport), con contratos distintos. La lista de puntos se expone en la información pública del juez y en un enum
   de la evidencia.
2. **Las categorías de hoy** nacen del acuse. `fallo_silencioso` es «el receptor aceptó y escribió algo mal». La leyenda y las
   instrucciones del explicador del juez conocen ese nombre. Un conversor no acepta ni rechaza: convierte.
3. **PID-8 (sexo administrativo) vacío:**
   - ningún ConceptMap de la guía tiene fila para un valor vacío;
   - FHIR R4 distingue un elemento ausente del código `unknown`;
   - la tabla 0001 de v2 tiene su propio código U, «Unknown», que el mensaje no trae.
4. **Orden de las listas.** En las StructureDefinition de R4 de Patient, Encounter, Observation y DiagnosticReport, ningún
   elemento declara `orderMeaning`. En R4, un elemento repetible sin `orderMeaning` no da significado al orden. La guía
   numera `coding[1]` y `coding[2]` para repartir CE.1-3 y CE.4-6. El laboratorio, en sus propios circuitos, trató el orden
   de `name[]` como dato.
5. **Entradas de más.** La guía mapea más campos de los que el juez proyecta: PID-2, PID-4, PID-19, PID-20, PID-40, PV1-50….
   Si un Bundle trae un `identifier` o un `telecom` de más, el juez no puede distinguir si el conversor lo inventó o lo
   mapeó desde un campo que el juez no mira.
6. **PV1-2 = N:**
   - el cap. 3 de v2.5 dice que un PV1 «pseudo-opcional» se consigue valorando PV1-2 con N, «not applicable»;
   - la hoja de mensaje de la guía dice que procesar el PV1 crea un Encounter;
   - el ConceptMap de la tabla 0004 a `Encounter.status` mapea N a `in-progress`.
7. **Valores imposibles:**
   - un mensaje puede traer un valor que no está en la tabla (PID-8 fuera de la 0001) o una fecha inválida (PID-7);
   - el cap. 2 de v2.5 (§2.9.2.2 b) admite que un receptor rechace por contenido;
   - la guía no da destino a un valor sin fila en el ConceptMap;
   - `Patient.gender` tiene binding `required` en R4.
8. **Códigos `unmatched`.** Algunos ConceptMap marcan códigos v2 como sin destino, por ejemplo XPN.7 B, XAD.7 N o XTN.2 ORN.
   Un conversor podría mapearlos a algún `use` de FHIR.
9. **Apellidos.** El apellido en XPN es de tipo FN, con subcomponentes (FN.1 el apellido, y prefijos y apellidos propios
   aparte). La guía mapea el apellido a `family`.
10. **Decimales.** FHIR R4 declara significativa la precisión de un decimal: 0.010 no es lo mismo que 0.01. Un conversor
    puede reescribir «1.20» como «1.2». El laboratorio midió ya esa diferencia como real en sus propios circuitos.
11. **A11** (cancelación de admisión) **con PV1-45 (fecha de alta) valorado:**
    - la hoja del segmento PV1 de la guía da `Encounter.status = finished` cuando PV1-45 viene;
    - la hoja de mensaje de A11 da `cancelled`.
12. **Muestras en otras versiones.** Las muestras públicas de los conversores vienen sobre todo en v2.8, más algunas en 2.3,
    2.4, 2.5.1 y 2.6. El juez solo tiene el texto de v2.5. Lo que dependa de las tablas o estructuras de v2.5 en un mensaje de
    otra versión se puede marcar como «no comprobable», con la etiqueta L18, en lugar de contar.
