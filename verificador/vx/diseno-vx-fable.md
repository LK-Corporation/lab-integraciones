<!-- modelo: Claude Fable 5.1 (claude-fable-5-1); fecha: 25-oct-2026; «VX0: el juez de conversiones ante VXU_V04 (etapa 20); diseño a ciegas de lo que devuelven los conversores; leído solo la caja VX0 (scratchpad/vx0)» -->

# Diseño VX0: el punto `vxu_conv`, el perfil «guía» de Immunization y el corpus sintético de VXU_V04

Documento público. Sin credenciales, sin nombres de máquinas ni de personas, sin datos de pacientes (los ejemplos usan `VAC0001`, `VX-01`,
`Prueba^Mateo`). Nombra los dos conversores (Microsoft FHIR-Converter y LinuxForHealth hl7v2-fhir-converter) y la guía HL7 v2-to-FHIR
(ConceptMap del paquete 1.0.0; hojas CSV del commit `873b331`). **No sé qué devuelven los conversores con VXU**: todo lo que sigue sale del
estándar v2.5 (caps. 2, 2A, 3, 4 y 7), de FHIR R4, de la guía y del juez tal como está en esta carpeta.

Convenciones: **S-VX-n** decisión propuesta (pasa a S-n cuando Jev decida); **R-VX-n** regla implementable; **P-VX-n** prueba en rojo
antes del código, con su control negativo; **L-VX-n** límite declarado; **AMB-VX-n** lectura adoptada donde la guía o el estándar admiten
dos; **Q-VX-D-n** pregunta de diseño (Jev); **MC-VX-n** mecanismo previsto; **DV-VX-n** queda reservada a quien implemente. Citas:
`fichero:línea` dentro de esta carpeta; `[E2|E2A|E3|E4|E7 CHnn.txt:líneas]` para el texto de v2.5; `[G <hoja>.csv:fila]` para una hoja de
la guía (la fila 1-3 es cabecera; RXA-n está en la fila n+3 hasta RXA-9); `[CM <nombre> <origen> → <destino> [IF …]]` para un ConceptMap
y su elemento; `[F <recurso>.<elemento> <fichero>:líneas]` para la StructureDefinition R4. Las S-n del laboratorio se citan solo en notas
de convención, nunca en un hallazgo que cuente (`resultados/ANTES-ETAPA-CONVERSORES.md:45-48`).

Punto de partida fijado: la pregunta (`resultados/ANTES-ETAPA-VXU.md:7-11`), las condiciones 1-6 (`:29-51`), las fases (`:69-78`), la regla
de resultado (`:97-102`) y el tope (`:92-95`). Lo medido en VX-pre que uso aquí: los ConceptMap del paquete cubren RXA (18 elementos), RXR,
ORC y el mensaje (`:16-18,65-66`); el juez no tiene bases de VXU (`:27`); la herramienta decide por MSH-9.1 (`:25-26`). Lo que compruebo
yo en la carpeta y condiciona el diseño: **`estructuras_25.json` no trae la gramática de `VXU_V04`** (las estructuras extraídas son ADT,
MDM, OMG, OMP, ORM, ORU, RAS, SIU, SRM: `verificador/estructuras_25.json:2775-6451`; la 0354 sí lista `VXU_V04 → V04`, `:7370-7372`), así
que `PE.estructura_de` daría `None` para cualquier VXU y el juez lo apartaría como `fuera_de_alcance` (`verificador/conversion.py:1413-1417`).
VX1 empieza por ahí (§10).

---

## 0. Resumen de las decisiones que lo condicionan todo (S-VX-n)

| | Decisión | Por qué, en una línea (cita) |
|---|---|---|
| S-VX-1 | **Un punto de entrada nuevo, `vxu_conv`** (`familia = "vxu"`, `solo_transformacion = True`, puerto 0, `tipos = {"VXU": {"V04": "VXU_V04"}}`), hermano de `adt_conv`/`oru_conv`; nada de lo que leen esos dos cambia. | Misma técnica de S-CV-1: el PE es el contrato como datos (`verificador/puntos_entrada.py:3-8,142-151`); condición 1 del encargo. |
| S-VX-2 | **La misma evidencia** `{mensaje, punto_entrada, conversion}` de S-CV-2 (`verificador/esquema_evidencia.json:438-455`): solo se añade `vxu_conv` al enum. | Condición 4: mismas formas de evidencia y veredicto. |
| S-VX-3 | **Una Immunization por grupo ORDER** (ORC + RXA [+RXR] [+OBX…]), emparejada por ORC-3.1/ORC-2.1, luego por (RXA-5.1, RXA-3), luego por orden; el Patient por PID; los Practitioner/PractitionerRole/Organization/Location solo como destino de referencias. | «Processing of each ORC segment results in the creation of a new Immunization resource» y «Incorporate RXA/RXR content into the Immunization created from the ORC segment in the same segment group» (`estandar/guia_csv/MSG_VXU_V04.csv:42,58-59`); en v2.5 ORC es obligatorio en ORDER (`[E4 hl7v25_CH04.txt:12397-12421]`). |
| S-VX-4 | **Las mismas ocho clases**, categorías y leyenda de CV (§4.1 de `resultados/diseno-conversores-fable.md`): `correcto`, `fallo_silencioso` (`convertido`/`aceptado_imposible`), `rechazo_incorrecto`, `indeterminado`, `fuera_de_alcance`. | Condición 4; `conversion.py:1459-1468`. |
| S-VX-5 | **`Immunization.status` por RXA-21 y RXA-20 como conjunto de una sola regla**: D → `entered-in-error`; si no, RXA-20 por la 0322 (CP/PA → `completed`, RE/NA → `not-done`); si no, vacío → `completed`. | Las tres filas del mapa de RXA con sus condiciones (`[G RXA_Immunization.csv:25-27]`, `[CM segment-rxa-to-immunization RXA-20/RXA-21 → status]`, `[CM table-hl70322-to-event-status]`); binding `required` (`[F Immunization.status immunization.profile.json:470-503]`). |
| S-VX-6 | **Ruta por la 0162 en sus dos grupos** (ID/IM/IV/PO/SC/TD → v3-RouteOfAdministration; el resto, identidad v2-0162); **sitio por la 0163 o la 0550** (identidad en ambas, AMB-VX-2). | `[CM table-hl70162-to-v2-0162]` (dos `group`); RXR-2 cita la 0163 en su tabla de atributos y la 0550 en su texto (`[E4 CH04.txt:9250,9350-9352]`); el mapa de RXR apunta a la 0550 y la hoja a «BodyParts» (`[G RXR_Immunization.csv:5]`). |
| S-VX-7 | **Dos funciones de performer fijadas por la guía**: RXA-10 → actor Practitioner con `function {v2-0443, AP}`; ORC-12 → actor PractitionerRole (o Practitioner: forma) con `function {v2-0443, OP}`. | `[G RXA_Immunization.csv:13-15]`, `[G ORC_Immunization.csv:20-22]`; `performer.actor` admite Practitioner, PractitionerRole y Organization (`[F Immunization.performer.actor immunization.profile.json:1355-1371]`). |
| S-VX-8 | **`recorded` como conjunto admitido** {ORC-9} ∪ {RXA-22 si RXA-21 = A} (AMB-VX-3). | Dos filas mandan al mismo elemento: `[G ORC_Immunization.csv:17]` sin condición y `[G RXA_Immunization.csv:28]` con «IF RXA-21 EQUALS "A"». |
| S-VX-9 | **Los OBX del grupo ORDER se juzgan como Observation con las reglas de `oru_conv`** más `subject → Patient` y `partOf → la Immunization de su grupo`; un OBX cuyo valor aparece en un elemento de la Immunization (sin Observation) es **convención** (AMB-VX-4). | `[G MSG_VXU_V04.csv:61-62]` («Observation[2].partOf.reference=Immunization[1].id») y su Narrative-Condition: «Some observations about the immunization may map to elements within the Immunization resource… Specific guidance… will be provided separately». |
| S-VX-10 | **El PV1 es opcional en el Bundle** (Encounter presente o ausente: convención); si está, se juzga con las reglas de `adt_conv`; `Immunization.encounter` ausente: convención (AMB-VX-5). | Narrative-Condition «Only if the system wants to know about the encounter» (`[G MSG_VXU_V04.csv:20]`); no hay fila de referencia `Immunization.encounter` en la hoja del mensaje. |
| S-VX-11 | **NK1 entra con un perfil reducido** (existencia, nombre, relación, teléfonos, sexo; fecha de nacimiento solo en RelatedPerson) y la forma RelatedPerson / Patient.contact es convención (AMB-VX-6); **PD1 queda fuera del perfil** (nota, L-VX-3). Las dos cosas van a Jev (Q-VX-D-5). | «Typically, each NK1 will be translated to either a new RelatedPerson resource or added as a new occurrence of Patient.contact, but it's possible to insert the NK1 data into both» (`[G MSG_VXU_V04.csv:16-17]`); PD1 solo mapea PD1-3/4/6/7/14 (`[G PD1_Patient.csv:6-19]`). |
| S-VX-12 | **El corpus son 40 bases sintéticas válidas en v2.5, escritas desde §4.17.6 y §4.18**, una por rama de la guía, con una regla medible contra la firma mecánica (§4.1); los defectos buscados van solo a las pruebas P-VX. | Condición 6 del encargo; `verificador/bases_oru.py:3-11` como forma. |
| S-VX-13 | **La herramienta decide `vxu_conv` por MSH-9.1 = VXU** y deja ORU → `oru_conv` y todo lo demás → `adt_conv` exactamente igual; el corpus gana la carpeta `vxu` y las huellas de `adt`/`oru`/`muestras` no cambian. | `verificador/cv/verificar_conversor.py:394-397,413-463`; condición 1 (ADT y ORU no cambian). |
| S-VX-14 | **La versión manda como en S-CV-6**: MSH-12 escrita; con MSH-12 ≠ 2.5 (los VXU públicos suelen ser 2.5.1) los ConceptMap cuentan y la legalidad de tabla/estructura de 2.5 no (L18). Las reglas de la guía CDC no entran. | `conversion.py:1404-1412`; `ANTES-ETAPA-VXU.md:104-108` (fuera de la etapa). |
| — | **Lo que no cambia:** `conversion.py` en sus ramas `adt`/`oru`, `puntos_entrada.py` en sus PE, `verificador.verificar` (la línea `:264-265` ya despacha por `solo_transformacion`), los mapeadores, `prueba_conversion.py` (28 pruebas en verde sin editar), los RESULTADO sellados y la huella con que se juzgaron. | Condición 1 del encargo; `ANTES-ETAPA-VXU.md:38-41`. |

---

## 1. E-VX-1 completo: cada campo que llega a FHIR, con su cita

Leyenda de la columna «Cuenta»: **cuenta** (una diferencia es hallazgo de una de las ocho clases), **convención** (la guía admite más de una
representación: el esperado es un conjunto), **nota** (no es dato proyectado: `fuera_proyeccion`/`extra`), **—** (sin destino en la guía;
nunca se juzga). «Esperado» resume la regla; la regla completa está en §3.

### 1.1 RXA (26 campos en v2.5: `[E4 CH04.txt:11159-11195]`; en vacunas, `[E4 CH04.txt:12440-12465]`)

| Campo (DT, OPT en 2.5) | Destino | Cita | Qué espera el juez | Cuenta |
|---|---|---|---|---|
| RXA-1 Give Sub-ID (NM R) | — | `[G RXA_Immunization.csv:4]` sin atributo FHIR; `[E4 CH04.txt:11199-11202]` | nada | — |
| RXA-2 Administration Sub-ID (NM R) | — | `[G RXA:5]`; `[E4 11204-11210]` | nada | — |
| RXA-3 Date/Time Start (TS R) | `occurrenceDateTime` | `[G RXA:6]`; `[CM segment-rxa-to-immunization RXA-3 → occurrenceDateTime]`; `[CM datatype-dtm-to-datetime DTM.1 → $value]`; `[E4 11212-11218]`; `[E2A CH02A.txt:1700-1733]`; `[F Immunization.occurrence[x] immunization.profile.json:708-725]` (1..1, dateTime \| string) | `dateTime` con la precisión del origen (R-CV-7: `conversion.py:457-527`); con zona, igualdad por instante; `occurrenceString` con los mismos dígitos es otra clave → `valor_distinto`; TS.2 se ignora | **cuenta** |
| RXA-4 Date/Time End (TS R) | — | `[G RXA:7]`; `[E4 11220-11223]` («If null, RXA-3 is assumed») | nada; si `occurrenceDateTime` = RXA-4 ≠ RXA-3 sale como `valor_distinto` de RXA-3 | — |
| RXA-5 Administered Code (CE R, 0292) | `vaccineCode` | `[G RXA:8]` (CWE[CodeableConcept]); `[CM segment-rxa-to-immunization RXA-5 → vaccineCode]`; `[CM datatype-cwe-to-codeableconcept CWE.1 → coding[1].code, CWE.2 → coding[1].display, CWE.3 → coding[1].system («indirect… the vocabulary table will give the actual uri»), CWE.4-6 → coding[2], CWE.9 → text]`; `[E4 11225-11232; 12469-12473; 14892-14898]` («CE.3 should be valued as "CVX", not as "HL70292"»); `[E2A CH02A.txt:309-335]`; `[F Immunization.vaccineCode :563-594]` (1..1, example) | CE.1 en algún `coding.code`; CE.4 en otro; `system` para CVX/MVX según Q-VX-D-1 (L-VX-4); otros nombres (HL70292, L…): convención; `display`: forma; orden de `coding[]`: forma (Q-CV-D-4) | **cuenta** (code); system: Q-VX-D-1 |
| RXA-6 Administered Amount (NM R) | `doseQuantity.value` | `[G RXA:9]`; `[CM RXA-6 → doseQuantity.value]`; `[E4 11234-11236]`; `[F Immunization.doseQuantity :1127-1139]` | texto decimal exacto (Q-CV-D-10); forma canónica del NM admitida (`.5` = `0.5`, `5.` = `5`; `_nm_canonico`, `conversion.py:1068-1082`); `0.50` ≠ `0.5` | **cuenta** |
| RXA-7 Administered Units (CE C) | `doseQuantity` (unit/code/system) | `[G RXA:10]` (CWE[Quantity]); `[CM datatype-cwe-to-quantity CWE.1 → Quantity.code IF CWE.1 AND CWE.3; CWE.1 → unit IF CWE.2 NOT VALUED; CWE.2 → unit; CWE.3 → system IF CWE.1 AND CWE.3]`; `[E4 11244-11251]` | `unit` = CE.2, o CE.1 si CE.2 vacío; `code` = CE.1 y `system` = uri(CE.3) solo si ambos valorados; UCUM/ISO+ → `http://unitsofmeasure.org` (L-CV-3); otro nombre: convención; RXA-7 vacío → sin unit/code/system (`_unidades`, `conversion.py:1295-1316`) | **cuenta** |
| RXA-8 Dosage Form (CE O) | — | `[G RXA:11]` | nada | — |
| RXA-9 Administration Notes (CE O, Y) | — (comentario: «CDC… would map this to Immunization.reportOrigin… we will leave this for implementation guides») | `[G RXA:12]`; `[E4 11263-11271]` | `reportOrigin` con RXA-9 valorado: convención (AMB-VX-9); `reportOrigin` sin RXA-9: `dato_inventado` (regla de §3.0 de CV) | nota / cuenta solo si inventado |
| RXA-10 Administering Provider (XCN O, Y) | `performer.actor(Practitioner)` + `performer.function.coding {code "AP", system v2-0443}` | `[G RXA:13-15]`; `[CM segment-rxa-to-immunization RXA-10 → performer.actor(Practitioner) / performer.function.coding.code "AP" / .system]`; `[CM datatype-xcn-to-practitioner XCN.1 → identifier[1].value, XCN.2 → name(.family), XCN.3 → name.given[1], XCN.4 → name.given[2], XCN.5 → name.suffix[1], XCN.6 → name.prefix, XCN.21 → name.suffix[2]]`; `[E4 11273-11300]`; `[E2A 5808-5843]`; `[F Immunization.performer :1162-1171; .function :1312-1343 (extensible immunization-function); .actor :1355-1371]` | por cada repetición con XCN.1 o XCN.2: un `performer` con `function` AP y `actor` que resuelve (recurso, `contained`, lógico, o vía `PractitionerRole.practitioner`) a un Practitioner con `identifier[].value` ∋ XCN.1 y `name.family` = XCN.2 (FN.1), `given[1]` = XCN.3; solo `display` con XCN.1 valorado → `dato_perdido`; `function` ausente: Q-VX-D-6 | **cuenta** |
| RXA-11 Administered-at Location (LA2 C) | — (la guía mapea RXA-27/28, que **no existen en v2.5**) | `[G RXA:16]` sin atributo; `[G RXA:33-34]` RXA-27/28 → `location[1]`; tabla de atributos de 2.5 llega a 26 (`[E4 11159-11195]`); `[E4 11329-11344]` | nada; `Immunization.location` nunca cuenta (L-VX-1): con RXA-11 valorado, nota `fuera_proyeccion`; sin RXA-11, nota `extra` | — |
| RXA-12 Administered Per (ST C) | — | `[G RXA:17]` | nada | — |
| RXA-13 Strength (NM O) / RXA-14 Strength Units (CE O) | — | `[G RXA:18-19]` | nada | — |
| RXA-15 Substance Lot Number (ST O, Y) | `lotNumber` (0..1) | `[G RXA:20]`; `[CM RXA-15 → lotNumber]`; `[E4 11375-11383]`; `[F Immunization.lotNumber :961-973]` | la **primera** repetición, desescapada (§2.7); una segunda repetición en el mensaje: nota (AMB-VX-7, Q-VX-D-8); `lotNumber` sin RXA-15 → `dato_inventado` | **cuenta** |
| RXA-16 Substance Expiration Date (TS O, Y) | `expirationDate` (date) | `[G RXA:21]`; `[CM RXA-16 → expirationDate]`; `[E4 11385-11391]` («may be transmitted as YYYYMM»); `[F Immunization.expirationDate :999-1011]` | `date` con la precisión del origen (`2025-11` para `202511`; completar el día es `dato_inventado`); con hora → `fhir_invalido`; primera repetición | **cuenta** |
| RXA-17 Substance Manufacturer Name (CE O, Y, 0227) | `manufacturer(Organization)` | `[G RXA:22]` (CWE[Organization]); `[CM RXA-17 → manufacturer(Organization)]`; `[CM datatype-cwe-to-organization CWE.1 → identifier.value, CWE.2 → name, CWE.3 → identifier.system, CWE.9 → name]`; `[E4 11393-11401; 12475-12480; 14901-14986]` («"MVX", not "HL70227"»); `[F Immunization.manufacturer :922-935]` | `manufacturer` resuelve (recurso, `contained` o lógico por identifier) a una Organization con `identifier[].value` ∋ CE.1 y `name` = CE.2 desescapado (`Merck \T\ Co.` → `Merck & Co.`); solo `display` con CE.1 valorado → `dato_perdido`; solo CE.2 valorado y `display` = CE.2 → convención; `identifier.system` para MVX: Q-VX-D-1 | **cuenta** |
| RXA-18 Refusal Reason (CE O, Y) | `statusReason` (0..1) | `[G RXA:23]`; `[CM RXA-18 → statusReason]`; `[E4 11403-11409]`; `[F Immunization.statusReason :519-551]` (example) | CodeableConcept con CE.1 (y CE.4) en `coding.code`; `system`: convención (sin vocabulario en la guía); primera repetición; `text` = CE.9 | **cuenta** |
| RXA-19 Indication (CE O, Y) | `reasonCode[]` (0..*) | `[G RXA:24]`; `[CM RXA-19 → reasonCode]`; `[E4 11411-11417]`; `[F Immunization.reasonCode :1435-1466]` | un CodeableConcept por repetición, multiconjunto por `code`; faltar una → `dato_perdido` | **cuenta** |
| RXA-20 Completion Status (ID O, 0322) | `status` | `[G RXA:25-26]` («IF RXA-21 NOT EQUALS "D"» → CompletionStatus; «IF NOT VALUED AND RXA-21 NOT EQUALS "D"» → "completed"); `[CM segment-rxa-to-immunization RXA-20 → status mappedVia table-hl70322-to-event-status; RXA-20 → status "completed"]`; `[CM table-hl70322-to-event-status CP → completed, RE → not-done, NA → not-done, PA → completed]`; `[E4 11419-11436]`; `[F Immunization.status :470-503]`; `estandar/fhir_r4/valueset-immunization-status.json:44-55` | R-VX-1 (§3.1) | **cuenta** |
| RXA-21 Action Code (ID O, 0323) | `status` = "entered-in-error" si D | `[G RXA:27]`; `[CM RXA-21 → status IF RXA-21 EQUALS "D"]`; `[E4 11438-11449]` | D prevalece sobre RXA-20; A y U no tocan `status` (A condiciona RXA-22) | **cuenta** |
| RXA-22 System Entry Date/Time (TS O) | `recorded` IF RXA-21 = A | `[G RXA:28]`; `[CM RXA-22 → recorded IF RXA-21 EQUALS "A"]`; `[E4 11451-11457]`; `[F Immunization.recorded :758-770]` | dentro del conjunto de S-VX-8 (AMB-VX-3, Q-VX-D-3) | **cuenta** (dentro del conjunto) |
| RXA-23..26 (NM, CWE, CWE, ID 0480) | — | `[G RXA:29-32]` | nada | — |
| RXA-27 Administer-at (PL), RXA-28 Address (XAD), RXA-29 (EI) | `location[1]`, `location[1].address`, — | `[G RXA:33-35]` | **no existen en v2.5**; en mensajes 2.6+ se leen con certeza L18 y no cuentan (L-VX-1) | — |

### 1.2 RXR (`[E4 CH04.txt:9246-9254]`)

| Campo | Destino | Cita | Qué espera el juez | Cuenta |
|---|---|---|---|---|
| RXR-1 Route (CE R, 0162) | `route` | `[G RXR_Immunization.csv:4]` (RouteOfAdministration); `[CM segment-rxr-to-immunization RXR-1 → route mappedVia table-hl70162-to-v2-0162]`; `[CM table-hl70162-to-v2-0162 grupo 1: 41 códigos identidad v2-0162; grupo 2: ID → IDINJ, IM → IM, IV → IVINJ, PO → PO, SC → SQ, TD → TRNSDERM con system v3-RouteOfAdministration]`; `[E4 9258-9339]`; `[F Immunization.route :1080-1111]` (example) | un `coding {system, code}` exactamente el `target` del mapa (`{v3-RouteOfAdministration, IM}` para IM; `{v2-0162, IN}` para IN); `{v2-0162, IM}` → `codigo_mal_mapeado`; código fuera de la 0162 (user-defined) → convención; `display`: forma | **cuenta** |
| RXR-2 Administration Site (CWE O, 0163) | `site` | `[G RXR:5]` (BodyParts); `[CM segment-rxr-to-immunization RXR-2 → site mappedVia table-hl70550-to-v2-0550]`; `[CM table-hl70163-to-v2-0163 identidad, 55 códigos]`; `[CM table-hl70550-to-v2-0550 identidad]`; `[E4 9341-9352]` («Refer to HL7 Table 0550… For backward compatibility, HL7 Table 0163… may also be employed»); `[E7 CH07.txt:7892-7957]`; `[F Immunization.site :1033-1064]` | código de la 0163 → `{v2-0163, código}`; de la 0550 → `{v2-0550, código}`; otro (SNOMED, local) → convención (AMB-VX-2, Q-VX-D-2) | **cuenta** |
| RXR-3 Device (CE O, 0164), RXR-4 Method (CWE O, 0165), RXR-5 Routing Instruction (CE O), RXR-6 Site Modifier (CWE O, 0495) | — | `[G RXR:6-9]` | nada | — |

### 1.3 ORC (30 campos en v2.5: `[E4 CH04.txt:1820-1860]`)

| Campo | Destino | Cita | Qué espera el juez | Cuenta |
|---|---|---|---|---|
| ORC-1 Order Control (ID R, 0119) | — | `[G ORC_Immunization.csv:4]`; `[E4 11155-11157]` («The ORC must have the filler order number and the order control code RE») | nada | — |
| ORC-2 Placer Order Number (EI C) | `identifier[1]` con `type.coding {code "PLAC", system v2-0203}` | `[G ORC:5-7]`; `[CM segment-orc-to-immunization ORC-2 → identifier[1] / identifier[1].type.coding.code "PLAC" / .system]`; `[CM datatype-ei-extension-to-identifier EI.1 → value]`; `[E4 2353-2392]`; `[E2A CH02A.txt:1886-1932]` | un Identifier con `value` = EI.1 y `type.coding.code` PLAC (system de la 0203: identidad, convención como en CV §3.1); EI.2-4 → `system`/`assigner`: convención; PLAC/FILL intercambiados → `codigo_mal_mapeado` | **cuenta** (value y type.code) |
| ORC-3 Filler Order Number (EI C) | `identifier[2]` FILL | `[G ORC:8-10]`; `[CM ORC-3 → identifier[2] / FILL]`; `[E4 2394-2442]` | igual con FILL | **cuenta** |
| ORC-4 Placer Group Number (EI O en 2.5; **EIP en la guía**) | `identifier[3]` (EIP.2, FGN) / `identifier[4]` (EIP.1, PGN) | `[G ORC:11-12]`; `[CM ORC-4 → identifier[3]/identifier[4]]`; `[CM datatype-eip-placerassignedidentifier-to-identifier EIP.1 → value, type PGN]`; `[CM datatype-eip-fillerassignedidentifier-to-identifier EIP.2 → value, type FGN]`; `[E4 1826; 2444-2457]` | cita ambigua: el tipo de dato de 2.5 (EI) no tiene EIP.1/EIP.2 → **nota** (AMB-VX-1); si aparece un identifier con ORC-4.1, nota `convencion` | nota |
| ORC-5 Order Status, ORC-6 Response Flag, ORC-7 Quantity/Timing (TQ B), ORC-8 Parent | — | `[G ORC:13-16]` | nada | — |
| ORC-9 Date/Time of Transaction (TS O) | `recorded` | `[G ORC:17]`; `[CM ORC-9 → recorded]`; `[E4 2594-2599]`; `[F Immunization.recorded :758-770]` | conjunto de S-VX-8 (AMB-VX-3) | **cuenta** |
| ORC-10 Entered By, ORC-11 Verified By (XCN) | — | `[G ORC:18-19]` | nada | — |
| ORC-12 Ordering Provider (XCN O, Y) | `performer.actor(PractitionerRole)` + `function {code "OP", system v2-0443}` | `[G ORC:20-22]`; `[CM segment-orc-to-immunization ORC-12 → performer.actor(PractitionerRole) / performer.function.coding.code "OP" / .system]`; `[CM datatype-xcn-to-practitionerrole XCN.1 → practitioner(Practitioner.identifier[1].value), XCN.3/XCN.4 → practitioner(Practitioner.name.given), XCN.5/XCN.21 → suffix, XCN.6 → prefix; **sin fila para XCN.2** (AMB-VX-10)]`; `[E4 2714-2729]` | un `performer` con `function` OP y `actor` que resuelve a un PractitionerRole cuyo `practitioner` resuelve a un Practitioner con XCN.1 y `family` = XCN.2 (por el mapa XCN → Practitioner), o directamente a un Practitioner (forma, AMB-VX-8) | **cuenta** |
| ORC-13..27 (PL, XTN, TS, CE, CE, CE, XCN, CE, XON, XAD, XTN, XAD, CWE, CWE, TS) | — | `[G ORC:23-37]` | nada | — |
| ORC-28 Confidentiality Code (CWE O, 0177) | `meta.security` | `[G ORC:38]`; `[CM segment-orc-to-immunization ORC-28 → meta.security mappedVia table-hl70177-to-v3-confidentiality]`; `[CM table-hl70177-to-v3-confidentiality V/R/PSY → v3-Confidentiality; AID, HIV → HIV; U/UWM/VIP identidad v2-0177; EMP → EMP, ETH → ETHUD (v3-ActCode)]`; `[E4 3090-3105]` | con cita, pero `meta` no se juzga (L-CV-9): **nota** (L-VX-2) | nota |
| ORC-29 Order Type (CWE 0482), ORC-30 Enterer Authorization Mode (CNE 0483) | — | `[G ORC:39-40]` | nada | — |
| ORC-31..34 | — | `[G ORC:41-44]` | no existen en v2.5 | — |

### 1.4 PID, PD1 y NK1 (entran según S-VX-11 y Q-VX-D-5)

**PID → Patient[1]** (`[G MSG_VXU_V04.csv:12]`; `Immunization.patient.reference = Patient[1].id`, `[G MSG_VXU_V04.csv:42]`;
`[F Immunization.patient immunization.profile.json:618-631]`, 1..1). Se reutiliza **tal cual** el perfil de Patient de `adt_conv`
(`resultados/diseno-conversores-fable.md` §3.1; `conversion.py:530-539` `_patient`): PID-3 → `identifier[]` (`[G PID_Patient.csv:6]`), PID-5 →
`name[]` (`:8`), PID-7 → `birthDate` (`:11-13`), PID-8 → `gender` (`:14`), PID-11 → `address[]` (`:17`), PID-13/14 → `telecom[]` (`:22-25`),
PID-16 → `maritalStatus` (`:27`), PID-29/30 → `deceased[x]` (`:50-51`). Todos **cuenta** con las decisiones de Jev ya tomadas (Q-CV-D-3, 5, 8, 9:
`resultados/decisiones-qcv.md:14-27`). Lo nuevo: `Immunization.patient` (y `Observation.subject`, `RelatedPerson.patient`) deben resolver al
Patient#1 (**cuenta**, clase `referencia_rota` si no).

**PD1 → Patient[1]** (`[G MSG_VXU_V04.csv:14]`, «Incorporate PD1 content into the Patient»):

| Campo | Destino | Cita | Qué espera el juez | Cuenta |
|---|---|---|---|---|
| PD1-3 Primary Facility (XON, Y) | `generalPractitioner[1](Organization)` | `[G PD1_Patient.csv:6]`; `[CM segment-pd1-to-patient PD1-3]`; `[CM datatype-xon-to-organization XON.1 → name; XON.3 → identifier.value IF XON-10 NOT VALUED; XON.10 → identifier.value; XON.7 → identifier.type; XON.6 → identifier[1].assigner]`; `[E3 CH03.txt:8550-8564]`; `[E2A 6026-6043]`; `[F Patient.generalPractitioner patient.profile.json:1608-1616]` | fuera del perfil en VX1 (L-VX-3): nota `fuera_proyeccion` si aparece, nada si falta | nota (Q-VX-D-5) |
| PD1-4 Primary Care Provider (XCN, Y) | `generalPractitioner[2](Practitioner)` | `[G PD1:7]`; `[CM segment-pd1-to-patient PD1-4]`; `[E3 8566-8575]` | idem | nota (Q-VX-D-5) |
| PD1-6 Handicap (CWE) | extensión `patient-disability` | `[G PD1:9-10]`; `[CM PD1-6 → extension[1].url/valueCodeableConcept]` | extensiones: forma (L-CV-4) | — |
| PD1-7 Living Will (CWE) | `Observation[3]` IF PD1-7 VALUED | `[G MSG_VXU_V04.csv:15]`; `[G PD1:11]` sin atributo en la hoja de segmento | solo recuento (como en ADT: `conversion.py:347-353`, motivo `origen_guia`) | nota |
| PD1-14 Place of Worship (XON) | extensión `patient-congregation` | `[G PD1:18-19]` | forma (L-CV-4) | — |
| PD1-16 Immunization Registry Status (CWE), PD1-17 Effective Date (DT) | — | `[G PD1:21-22]` **sin atributo FHIR** | nada; un elemento que lo lleve (p. ej. `Patient.active`, una extensión) es nota | — |
| PD1-1, 2, 5, 8-13, 15, 18-22 | — | `[G PD1:4-5,8,12-17,20,23-27]` | nada | — |

**NK1 → RelatedPerson[1] o Patient[1].contact** (`[G MSG_VXU_V04.csv:16-17]`; `RelatedPerson.patient.reference = Patient[PID].id`;
`[F RelatedPerson.patient relatedperson.profile.json:488-500]` 1..1; `[F Patient.contact patient.profile.json:911-1337]`). Una fila por NK1;
el juez empareja por nombre (§2.2):

| Campo | RelatedPerson | Patient.contact | Cita | Qué espera el juez | Cuenta |
|---|---|---|---|---|---|
| existencia | `RelatedPerson` con `patient` → Patient#1 | `contact[k]` | `[G MSG_VXU_V04.csv:16-17]` | **una de las dos formas por NK1** (las dos a la vez: nota `ambos`); ninguna → `recurso_ausente` (hecho NK1(k)) | **cuenta** |
| NK1-2 Name (XPN, Y) | `name[1]` | `contact.name` (0..1) | `[G NK1_RelatedPerson.csv:5]`; `[G NK1_Patient.csv:5]`; `[CM datatype-xpn-to-humanname]`; `[E3 CH03.txt:7295]` | `family` = FN.1, `given[1]` = XPN.2 (reglas de PID-5, Q-CV-D-9); solo la primera repetición en `contact` | **cuenta** |
| NK1-3 Relationship (CE, 0063) | `relationship[1]` | `contact.relationship[1]` | `[G NK1_RP:6-7]`; `[G NK1_P:6]`; `[CM table-hl70063-to-v3-rolecode: 16 códigos → v3-RoleCode (SEL → ONESELF, SPO → SPS, DOM → SIGOTHR, CHD → CHILD, GCH → GRNDCHILD, NCH → NCHILD, SCH → STPCHLD, FCH → CHLDFOST, PAR → PRN, MTH → MTH, FTH → FTH, GRP → GRPRN, EXF → EXT, SIB → SIB, BRO → BRO, SIS → SIS, FND → FRND); 12 identidad v2-0063 (DEP, WRD, CGV, GRD, OAD, EME, ASC, OWN, TRA, MGR, NON…); 4 → v2-0131 (EMR → E, EMC → C, UNK → U, OTH → O)]`; `[E3 7321-7342]` | un `coding {system, code}` igual al `target`; `{v2-0063, MTH}` donde el mapa da `{v3-RoleCode, MTH}` → `codigo_mal_mapeado`; código fuera (user-defined) → convención | **cuenta** |
| NK1-4 Address (XAD, Y) | `address[1]` | `contact.address` (0..1) | `[G NK1_RP:8]`; `[G NK1_P:7]` («decreased cardinality») | reglas de PID-11 sobre la primera repetición | **cuenta** |
| NK1-5 Phone (XTN, Y) | `telecom[1]` | `contact.telecom[1]` | `[G NK1_RP:9]`; `[G NK1_P:8]`; `[CM datatype-xtn-to-contactpoint]` | `value` y `system` por las reglas de PID-13; `use` por XTN.2 (sin omisión `home`: la hoja no la fija) | **cuenta** (value, system); use: convención |
| NK1-6 Business Phone (XTN, Y) | `telecom[2]` con `use = "work"` | `contact.telecom[2].use = "work"` | `[G NK1_RP:10-11]`; `[G NK1_P:9-10]` | `value` y `use work` | **cuenta** |
| NK1-7 Contact Role (CE, 0131) | `relationship[2]` | `contact.relationship[2]` | `[G NK1_RP:12-14]`; `[G NK1_P:11]`; `[CM table-hl70131-to-v2-0131 identidad: E, C, F, I, N, S, O, U]`; `[E3 7424-7433]` | `{v2-0131, código}` en algún `relationship`; fuera de tabla: convención | **cuenta** |
| NK1-8/9 Start/End Date (DT) | `period.start/.end` | `contact.period.start/.end` | `[G NK1_RP:15-16]`; `[G NK1_P:12-13]` | fecha con precisión del origen (R-CV-7) | **cuenta** |
| NK1-12 Employee Number (CX), NK1-33 Identifiers (CX, Y) | `identifier[1]`, `identifier[2]` | — | `[G NK1_RP:19,40]` | solo en RelatedPerson: nota (el contact no tiene identifier: la guía admite la forma que los pierde) | nota |
| NK1-13 Organization Name (XON, Y) | — («Do we need to enhance the Organization resource…») | `contact.organization(Organization)` | `[G NK1_RP:20]`; `[G NK1_P:17]`; `[E3 7502]` | nota | nota |
| NK1-15 Administrative Sex (IS, 0001) | `gender` | `contact.gender` | `[G NK1_RP:22]`; `[G NK1_P:19]`; `[CM segment-nk1-to-relatedperson NK1-15 → gender mappedVia table-hl70001-to-administrative-gender]`; `[E3 7533-7536]` | por la 0001 (reglas de PID-8, Q-CV-D-3) | **cuenta** |
| NK1-16 Date/Time of Birth (TS) | `birthDate` | — | `[G NK1_RP:23]`; `[G NK1_P:20]` sin atributo; `[E3 7538-7541]`; `[F RelatedPerson.birthDate :691-703]` | en RelatedPerson, `date` con precisión del origen; en `contact`, no existe → convención (la guía admite la forma) | **cuenta** / convención |
| NK1-20 Primary Language (CWE) | `communication.language` (`mappedVia unspecified_mapping`) | — | `[G NK1_RP:27]` | nota | nota |
| NK1-30/31/32 Contact Person (XPN/XTN/XAD) | `name[2]`, `telecom[3]`, `address[2]` | `contact.organization(Organization.contact.*)` | `[G NK1_RP:37-39]`; `[G NK1_P:34-36]` | nota | nota |
| NK1-37 SSN (ST) | `identifier[3]` (us-ssn) | — | `[G NK1_RP:44-47]` | nota (ámbito US) | nota |
| NK1-40/41 Telecommunication (XTN) | `telecom[4]/[5]` | `contact.telecom[3]/[4]` | `[G NK1_RP:50-51]`; `[G NK1_P:44-45]` | nota | nota |
| NK1-10, 11, 14, 17-19, 21-29, 34-36, 38, 39 | — | — | `[G NK1_RP:17-18,21,24-26,28-36,41-43,48-49]` | nada | — |

### 1.5 Campos sin cita o con cita ambigua

**Sin destino en la guía (y por tanto nunca cuentan):** RXA-1, 2, 4, 8, 9, 11, 12, 13, 14, 23-26; RXR-3-6; ORC-1, 5-8, 10, 11, 13-27, 29, 30;
PD1-16/17 y los demás PD1 salvo 3, 4, 6, 7, 14; NK1-10, 11, 14, 17-19, 21-29, 34-36, 38, 39. De estos, **tres llevan dato clínico que la
guía deja sin sitio en v2.5**: RXA-11 (dónde se administró: la guía solo mapea RXA-27/28, posteriores a 2.5), RXA-9 (notas de administración:
la guía lo delega a las IG) y PD1-16 (estado en el registro de vacunas). Se declaran L-VX-1 y L-VX-3; un conversor que los lleve a algún
sitio recibe nota, nunca hallazgo.

**Con cita ambigua (lectura adoptada en AMB-VX-n):**

| Campo | Ambigüedad | Dónde |
|---|---|---|
| RXR-2 | el mapa de segmento dice 0550, la tabla de atributos de 2.5 dice 0163, el texto de 2.5 admite las dos, la hoja dice «BodyParts» | AMB-VX-2, Q-VX-D-2 |
| ORC-4 | EI en 2.5, EIP en la guía (identifier[3]/[4] por EIP.1/EIP.2) | AMB-VX-1 |
| ORC-9 y RXA-22 | dos filas al mismo `recorded`, una sin condición y otra «IF RXA-21 EQUALS "A"» | AMB-VX-3, Q-VX-D-3 |
| RXA-5.3, RXA-17.3 | la uri de CVX y MVX («indirect mapping… the vocabulary table») no está en el paquete (la 0396 → uri tampoco: L-CV-3) | L-VX-4, Q-VX-D-1 |
| OBX de ORDER | la condición de la fila `[G MSG_VXU_V04.csv:61]` es «OBX-5 LST.count LESS THAN OR EQUALS 1 **AND** OBX-2 IS "NA"» (en PERSON_OBSERVATION, `:34`, es **OR**): leída literalmente, un OBX CE de un solo valor no entra en ninguna de las dos filas; además la Narrative-Condition deja a las IG llevar algunos OBX a elementos de la Immunization | AMB-VX-4, Q-VX-D-4 |
| ORC-12 | el mapa XCN → PractitionerRole no tiene fila para XCN.2 (apellido); el mapa XCN → Practitioner sí | AMB-VX-10 |
| PV1 | Narrative-Condition «Only if the system wants to know about the encounter»; sin fila de `Immunization.encounter` | AMB-VX-5, Q-VX-D-9 |
| NK1 | «either a new RelatedPerson… or… Patient.contact… or both» | AMB-VX-6 |
| RXA-15/16/17/18 | repetibles en 2.5 (`Y`) y mapeados a elementos 0..1 | AMB-VX-7, Q-VX-D-8 |

**Respuesta a E-VX-1:** sí. Los veinte campos que la guía lleva a Immunization tienen fila en una hoja del commit `873b331` y elemento en un
ConceptMap del paquete 1.0.0 (RXA-3, 5, 6, 7, 10, 15, 16, 17, 18, 19, 20, 21, 22; RXR-1, 2; ORC-2, 3, 4, 9, 12, 28), y los tres esenciales de
la regla de parada (RXA-3, RXA-5, RXA-20) tienen cita doble y valor esperado unívoco (RXA-20 con sus dos condiciones y la 0322). La etapa
**no para** por E-VX-1 (`ANTES-ETAPA-VXU.md:63-66`). Lo que no da la guía es la uri de CVX/MVX y el sitio de RXA-11: se declaran, no se inventan.

---

## 2. El punto de entrada `vxu_conv`

### 2.1 Contrato y evidencia (R-VX-2)

```
PUNTOS["vxu_conv"] = _pe(
    "vxu_conv", 0, {"VXU": {"V04": "VXU_V04"}},
    MSH_CONSUMIDOS | {("PID", 3), ("PID", 5), ("PID", 7), ("PID", 8), ("PID", 11), ("PID", 13), ("PID", 14), ("PID", 16), ("PID", 29), ("PID", 30),
                      ("ORC", 2), ("ORC", 3), ("ORC", 9), ("ORC", 12),
                      ("RXA", 3), ("RXA", 5), ("RXA", 6), ("RXA", 7), ("RXA", 10), ("RXA", 15), ("RXA", 16), ("RXA", 17), ("RXA", 18), ("RXA", 19),
                      ("RXA", 20), ("RXA", 21), ("RXA", 22), ("RXR", 1), ("RXR", 2),
                      ("OBX", 2), ("OBX", 3), ("OBX", 5), ("OBX", 6), ("OBX", 7), ("OBX", 8), ("OBX", 11), ("OBX", 14),
                      ("NK1", 2), ("NK1", 3), ("NK1", 4), ("NK1", 5), ("NK1", 6), ("NK1", 7), ("NK1", 8), ("NK1", 9), ("NK1", 15), ("NK1", 16)},
    [("MSH", 10, "consumido"), ("PID", 3, "consumido"), ("PID", 5, "consumido"), ("RXA", 3, "consumido"), ("RXA", 5, "consumido"),
     ("MSH", 7, "estricto"), ("ORC", 1, "estricto"), ("ORC", 3, "nota"), ("RXA", 4, "estricto"), ("RXA", 6, "estricto")],
    [("MSH", 7, "ts", "estricto"), ("MSH", 18, "0211", "estricto"), ("PID", 7, "ts", "consumido"), ("PID", 8, "0001", "consumido"),
     ("PID", 29, "ts", "consumido"), ("PID", 30, "0136", "consumido"), ("ORC", 1, "0119", "estricto"), ("ORC", 9, "ts", "consumido"),
     ("RXA", 1, "nm", "estricto"), ("RXA", 2, "nm", "estricto"), ("RXA", 3, "ts", "consumido"), ("RXA", 4, "ts", "estricto"),
     ("RXA", 6, "nm", "consumido"), ("RXA", 16, "ts", "consumido"), ("RXA", 20, "0322", "consumido"), ("RXA", 21, "0323", "consumido"),
     ("RXA", 22, "ts", "consumido"), ("RXR", 1, "0162", "consumido"), ("OBX", 2, "0125", "consumido"), ("OBX", 11, "0085", "consumido"),
     ("OBX", 14, "ts", "consumido"), ("NK1", 15, "0001", "consumido"), ("NK1", 16, "ts", "consumido")],
    "VXU^V04 convertido por un tercero (HL7 v2 -> FHIR): solo transformación, sin acuse; perfil «guía» de Immunization (S-VX-1..14).",
    solo_transformacion=True, familia="vxu")
```

- `p4`/`p5` se declaran por coherencia con `contrato()` (`puntos_entrada.py:174-183`) y para `_imposibles` (§2.3); en un PE de solo
  transformación no hay acuse (R-CV-2). `_longitudes` toma lo que haya en `EH.CAMPOS` (`RXA-*`, `RXR-*`, `ORC-*` están: `estructuras_25.json:1097-2367`).
- **La gramática `VXU_V04` hay que extraerla** a `estructuras_25.json["estructuras"]` desde `[E4 CH04.txt:12366-12421]` con el extractor del
  laboratorio (`estructuras_hl7.py:5-7`), con su `fuente`; sin ella `_afirmar` (`puntos_entrada.py:202-205`) rompe al importar. La gramática
  esperada: `MSH [{SFT}] PID [PD1] [{NK1}] [PATIENT: PV1 [PV2]] [{GT1}] [{INSURANCE: IN1 [IN2] [IN3]}] [{ORDER: ORC [{TIMING: TQ1 [{TQ2}]}] RXA [RXR] [{OBSERVATION: OBX [{NTE}]}]}]`.
  Añadir una estructura no toca `_tipos("ADT")`/`("ORU")` (filtran por prefijo, `:35-42`): P-VX-21 lo afirma.
- Evidencia: la de S-CV-2 con `punto_entrada = "vxu_conv"`; `esquema_evidencia.json:442-453` y `E_PROPS["punto_entrada"]`
  (`mcp_verificador.py:1105`, que ya lee `PE.NOMBRES`) ganan el valor; la descripción de `conversion` (`esquema_evidencia.json:438`) pasa a decir
  «adt_conv, oru_conv u vxu_conv».

### 2.2 Qué recursos espera y cómo se emparejan (R-VX-3)

Orden de lectura del mensaje (`_grupos_vxu(m)`, hermana de `_grupos_oru`, `conversion.py:253-268`): un ORC abre un grupo ORDER; el RXA, el
RXR y los OBX/NTE que siguen hasta el próximo ORC pertenecen al grupo; TQ1/TQ2 se ignoran; un RXA sin ORC delante abre grupo con nota
`estructura` (ORC es R en 2.5, pero el estándar manda procesar lo que se entiende, `[E2 CH02.txt:932-938]`); un OBX antes del primer ORC
está fuera de la estructura de 2.5 (no hay PERSON_OBSERVATION en `[E4 12366-12421]`) y solo se cuenta (L-CV-7 ampliado).

| Papel esperado | Fuente v2 | Clave de emparejamiento (en este orden; dos candidatos igual de buenos → `indeterminado/emparejamiento`) | Cita |
|---|---|---|---|
| `Patient#1` | PID | como en CV §2.2 (`conversion.py:291-313`): único; `identifier.value` ∋ PID-3.1; referido por `Immunization.patient`/`Observation.subject`/`RelatedPerson.patient` | `[G MSG_VXU_V04.csv:12,42]` |
| `Immunization#i` | grupo ORDER i (ORC+RXA) | (1) `identifier[].value` ∋ ORC-3.1 o ORC-2.1 → `identifier`; (2) `vaccineCode.coding.code` ∋ RXA-5.1 (o RXA-5.4) **y** `occurrenceDateTime` igual a RXA-3 por instante/precisión → `codigo+fecha`; (3) `vaccineCode` solo, si es único entre los libres → `codigo`; (4) tantas Immunization como grupos → `orden`; (5) ninguno → `recurso_ausente` (hecho `RXA(i)-5`) | `[G MSG_VXU_V04.csv:42,58-59]`; `[E4 11155]` (ORC-3 identifica la administración) |
| `Observation#i.j` | OBX j del grupo i | (1) las Observation cuyo `partOf` resuelve a `Immunization#i`, casadas con los OBX por `code.coding.code` = OBX-3.1 y OBX-4 si se repite → `partOf`; (2) cualquier Observation libre con ese código → `codigo`; (3) ninguna → `recurso_ausente`, **salvo** AMB-VX-4 (valor absorbido en la Immunization: convención) | `[G MSG_VXU_V04.csv:61-62]`; `[F Observation.partOf observation.profile.json:550-564]` |
| `RelatedPerson#k` / `Patient.contact[k]` | NK1 k | (1) RelatedPerson con `patient` → Patient#1 y `name.family` = NK1-2 FN.1 (o `identifier` ∋ NK1-33/NK1-12) → `nombre`/`identifier`; (2) `Patient.contact` con `name.family` igual → `contact`; (3) tantos RelatedPerson/contact como NK1 → `orden`; (4) ninguno → `recurso_ausente` (hecho `NK1(k)-2`); los dos a la vez → nota `ambos` | `[G MSG_VXU_V04.csv:16-17]` |
| `Encounter#1` | PV1 | como en CV §2.2 (`conversion.py:319-346`), pero **ausente no cuenta** (S-VX-10); si hay más de uno → `recurso_duplicado` | `[G MSG_VXU_V04.csv:20]` |
| Practitioner / PractitionerRole / Organization / Location | RXA-10, ORC-12, RXA-17, PD1-3/4, PV1-3… | solo por resolución desde la Immunization o el Encounter emparejados (`_alcanzadas`, `conversion.py:428-439`): recurso, `contained`, referencia lógica por `identifier` (convención) | `[F Bundle «Resolving references in Bundles» bundle.profile.json:803-806]` |

Sobrantes: una Immunization sin grupo → `recurso_inventado` (hecho `RXA`); una Observation sin OBX → `origen_guia` si hay OBX fuera de
ORDER o PD1-7 valorado (nota), si no `recurso_inventado`; un segundo Patient → `recurso_duplicado`; MessageHeader, Provenance, ServiceRequest
(la guía lo admite desde ORC: `[G MSG_VXU_V04.csv:43]`), Coverage, Device… → `otros_tipos` (nota).

### 2.3 Qué hace con lo que no cubre (R-VX-4)

| Caso | Qué hace el punto | Cuenta | Cita |
|---|---|---|---|
| MSH-9 ≠ VXU^V04 (QBP, RSP, VXX, ADT…) | `fuera_de_alcance`, como hoy (`conversion.py:1413-1417`) | no | `ANTES-ETAPA-VXU.md:105` |
| MSH-9.3 vacío o distinto de `VXU_V04` | se lee con la estructura del evento; nota `estructura_declarada` si difiere | no | AMB-MT-1; CV §1.3 |
| MSH-12 ≠ 2.5 (2.5.1 de los mensajes CDC, 2.3.1 antiguos) | se juzga; lo que depende de una tabla o estructura de 2.5 (RXA-20 ∉ 0322, RXR-1 ∉ 0162, un OBX fuera de ORDER) lleva certeza `ambiguedad L18` y no cuenta; los ConceptMap cuentan | parcial | S-CV-6; `conversion.py:127-133` |
| `salida.estado = error` con PID o RXA ausentes, o con un valor imposible (PID-7/8, RXA-3 DTM, RXA-6 NM, RXA-16 DTM, RXA-20 ∉ 0322, RXA-21 ∉ 0323, RXR-1 ∉ 0162 solo en 2.5) | `rechazo_aceptable` (nota; Q-CV-D-7) | no | `conversion.py:1366-1380,1422-1432`; `[E2 CH02.txt:932-938]` |
| `error` con un VXU que la guía convierte | `rechazo_incorrecto` (hecho: el campo que nombre el texto, si no `MSH-9`) | sí | CV §1.3 |
| Segmentos sin mapa (SFT, GT1, IN1-3, TQ1/TQ2, PV2, NTE) y segmentos Z o fuera de sitio | se ignoran al calcular el esperado; recuento; un `error` por ellos → `rechazo_incorrecto` | según | `[E2 CH02.txt:934-935]` |
| OBX antes del primer ORC | recuento `obx_fuera_orden`; una Observation que le corresponda es `origen_guia` | no | L-CV-7; `[E4 12366-12421]` |
| ORC sin RXA (grupo vacío) | nota `estructura`; no se espera Immunization de él; una Immunization ahí → `recurso_inventado` | sí (la inventada) | `[E4 12397-12421]` (RXA es R en ORDER) |
| RXA-5 o RXA-3 vacíos (R) con Bundle | la hoja no tiene esperado (FHIR 1..1 sin dato): nota `sin_esperado`; con `error` → `rechazo_aceptable` | no | `[E4 11159-11195]`; `[F :563-567, :708-714]` |
| `salida.estado` = `vacio`/`sin_respuesta`, Bundle ilegible | `indeterminado/sin_salida`, `indeterminado/lectura` | no | L-CV-8; `conversion.py:1439-1446` |
| Elementos de Immunization sin fila en la guía (`primarySource`, `isSubpotent`, `reportOrigin` sin RXA-9, `protocolApplied`, `programEligibility`, `fundingSource`, `education`, `reaction`) | valor único presente sin campo → `dato_inventado` (regla de §3.0 de CV, Q-CV-D-3); repetible → nota `extra`; Q-VX-D-7 para los booleanos por omisión | según | CV §3.0; `[F :792-805, :1515-1528]` |

### 2.4 Qué recuentos lleva (R-VX-5)

`conversion.recuentos` (como hoy `conversion.py:1450`, con los tipos de la familia): `Patient`, `Immunization`, `Observation`, `RelatedPerson`,
`Encounter`; y, nuevo para esta familia, `grupos_orden` (n de ORDER), `obx_en_orden`, `obx_fuera_orden`, `nk1`, `rxa_por_estado`
(`{"CP": n, "RE": n, "NA": n, "PA": n, "": n}` por RXA-20) y `rxa_por_accion` (RXA-21). `conversion.otros_tipos` como hoy. `emparejamiento`
lista `rol`, `origen`, `fullUrl`, `emparejado_por`, `candidatos` por papel. Todo determinista y sin datos personales.

### 2.5 Categorías, hallazgos y veredicto

Sin cambio respecto a CV §1.4 (`conversion.py:1459-1468`): `fallo_silencioso/convertido` si cuenta algo de las clases de datos,
`+aceptado_imposible` si cuenta un `valor_imposible_aceptado`; `correcto` si nada cuenta. Hallazgos con la forma de `_h` (`conversion.py:114-118`),
`origen = "conversion"`, `hecho` = el campo origen con su ocurrencia (`RXA-20` para el primer grupo, `RXA(2)-20` para el segundo:
`_hecho`, `conversion.py:1106-1108`), `citas` de §3.6 y `clase_cv = null`.

### 2.6 Dónde vive (R-VX-6): lo nuevo se añade, lo de ADT y ORU no se edita

- `verificador/puntos_entrada.py`: el bloque `PUNTOS["vxu_conv"]` de §2.1, debajo de `oru_conv` (`:148-151`).
- `verificador/estructuras_25.json`: la entrada `"VXU_V04"` en `estructuras` (con `fuente`), escrita por el extractor; `t0354` ya la tiene.
- `verificador/conversion_vxu.py` (nuevo, solo biblioteca estándar): `TIPOS = CV.TIPOS_PROY + ("Immunization", "RelatedPerson")`, `MAPAS_VXU`
  (0322, 0162, 0163, 0550, 0063, 0131, 0001 reutilizado), `C_VXU` (citas), `grupos(m)`, `emparejar(m, entries, top, out, pat, usados, rol)`,
  `imposibles(m)`, `faltan`, `juzgar(J, m, lec, pat_entry)`, `_inmunizacion(J, m, grupo, r, entry, pat_entry, i, entries)`, `_status`,
  `_performers`, `_fabricante`, `_dosis`, `_ruta_sitio`, `_recorded`, `_relacionado`, `PERFIL_GUIA_VXU`, `S_VX`, `L_VX`, `AMB_VX`, `autoprueba`.
  Reutiliza sin editar: `CV._fecha`, `CV._codigo`, `CV._codigo_tabla`, `CV._unidades` (recibe el segmento y el número de campo: para RXA-7 se
  le pasa `rxa` y un `h` que devuelva `RXA(i)-7`; su cuerpo lee `_f(m, obx, 6)`, así que o se duplica en `_dosis` o se generaliza con un
  parámetro por omisión `campo=6`), `CV._nm_canonico`, `CV._identifier`, `CV._nombres`, `CV._direcciones`, `CV._genero`, `CV._patient`,
  `CV._encounter`, `CV._observacion`, `CV._sujeto` (para `Observation.subject`), `CV.resolver`, `CV._alcanzadas`, `CV.mapa`/`CV.MAPAS`.
- `verificador/conversion.py`, **cinco ganchos** cuyo efecto con `familia ∈ {adt, oru}` es idéntico al de hoy (P-VX-22 lo demuestra):
  1. `verificar`: `familia = pe.get("familia") or ("oru" if pe["nombre"] == "oru_conv" else "adt")` (`:1389`; los PE de hoy ya traen `familia`).
  2. `verificar`: `faltan` y `_imposibles` por familia (`:1425-1426`): con `vxu`, `CVX.faltan` = `("PID", "RXA")` y `CVX.imposibles(m)`.
  3. `leer_bundle(texto, tipos=TIPOS_PROY)` y `verificar`/`emparejar` usan `tipos = CVX.TIPOS if familia == "vxu" else TIPOS_PROY`
     (`:197-199, :411-413, :1450`): con `adt`/`oru` la tupla es la misma de hoy.
  4. `emparejar`: tras el bloque del Patient (`:291-317`), `if familia == "vxu": CVX.emparejar(…); else: <lo de hoy>`; el `if familia == "adt": … else:`
     de hoy queda dentro del `else` sin tocar una línea.
  5. `_juzgar`: `if familia == "adt": … elif familia == "oru": … else: CVX.juzgar(J, m, lec, pat_entry)`: el `else` de hoy pasa a `elif "oru"` sin cambiar su cuerpo.
  `MAPAS` gana las entradas de VXU (la autoprueba las coteja con el paquete: `:1613-1626`); `INFO["puntos_entrada"]` y `S_CV`/`L_CV`/`AMB_CV`
  no se tocan: `INFO` incorpora `CVX.INFO` bajo `"vxu"`.
- `verificador/verificador.py`: **nada** (`:264-265` ya despacha por `solo_transformacion`).
- `verificador/mcp_verificador.py`: `TABLAS["perfil_guia_vxu"]` (patrón `:1848-1851`); `_proyectar_conversion` no cambia (`:1471-1486`);
  `REVISION` (`:59`) y la descripción de `punto_entrada` (`:1106-1111`) nombran `vxu_conv`; `info_verificador` declara S-VX, L-VX, AMB-VX y el
  contrato del PE (`info_verificador.json:1137-1341` tiene los de `adt_conv`/`oru_conv`).
- `verificador/esquema_evidencia.json`: `vxu_conv` en el enum (`:442-453`).
- Pruebas: `verificador/prueba_conversion_vxu.py` (nuevo, forma de `prueba_conversion.py:17-30,137-194`); `prueba_conversion.py` **no se edita**.
- Corpus: `verificador/bases_vxu.py` (§4). Herramienta: `cv/verificar_conversor.py` y `cv/conversor_juguete.py` (§6).

---

## 3. El perfil «guía» de VXU

### 3.0 Principio y niveles

Los de CV §3.0 sin cambio: **cuenta** (una sola representación en la guía), **convención** (la guía admite más de una: el esperado es un
conjunto y solo cuenta lo que queda fuera), **forma** (no es dato). Un campo vacío → elemento ausente; un elemento de valor único presente sin
campo → `dato_inventado`; repetible → nota `extra` (Q-CV-D-5); nulo explícito `""` → ausente; minúsculas en un código → convención (AMB-CV-1).
Cada regla lleva su clase de las ocho (`resultados/diseno-conversores-fable.md` §4.1), su nivel y su cita.

### 3.1 Immunization (ORC + RXA + RXR → `Immunization[i]`)

| Elemento | Esperado (perfil guía) | Clase si difiere | Nivel | Cita |
|---|---|---|---|---|
| existencia | una Immunization por grupo ORDER (§2.2) | `recurso_ausente` / `recurso_inventado` / `recurso_duplicado` | **cuenta** | `[G MSG_VXU_V04.csv:42,58-59]`; `[E4 CH04.txt:12397-12421]` |
| `status` | **R-VX-1:** `d` = RXA-21, `c` = RXA-20. Si `d` = D → {`entered-in-error`}. Si no y `c` vacío → {`completed`}. Si no y `c` ∈ 0322 → {mapa(c)}: CP, PA → `completed`; RE, NA → `not-done`. Si `c` ∉ 0322 (imposible en 2.5): un `status` válido cualquiera → nota `sin_esperado`; `status` = `c` literal → `valor_imposible_convertido` + `fhir_invalido`; `error` → `rechazo_aceptable`. Observado ausente → `fhir_invalido` (1..1); fuera del ValueSet → `fhir_invalido`; fuera del conjunto con `c` valorado → `codigo_mal_mapeado` (hecho RXA-20); con `c` vacío o `d` = D → `valor_distinto` (hecho RXA-21 si D, RXA-20 si no) | según | **cuenta** | `[G RXA_Immunization.csv:25-27]`; `[CM segment-rxa-to-immunization RXA-20 → status IF RXA-21 NOT EQUALS "D"; RXA-20 → status "completed" IF NOT VALUED AND RXA-21 NOT EQUALS "D"; RXA-21 → status "entered-in-error" IF RXA-21 EQUALS "D"]`; `[CM table-hl70322-to-event-status]`; `[E4 11419-11449]`; `[F Immunization.status immunization.profile.json:470-503]`; `valueset-immunization-status.json:44-55` |
| `statusReason` | RXA-18 (primera repetición): CodeableConcept con CE.1 en `coding.code` (y CE.4 en otro), `text` = CE.9; `system`: convención; vacío → ausente | `dato_perdido` / `valor_distinto` / `dato_inventado` | **cuenta** (code); system: convención | `[G RXA:23]`; `[CM RXA-18 → statusReason]`; `[CM datatype-cwe-to-codeableconcept]`; `[E4 11403-11409]`; `[F :519-551]` |
| `vaccineCode` | RXA-5: CE.1 en algún `coding.code`; CE.4 en otro; CE.9 → `text`; `system` de CVX/MVX por Q-VX-D-1 (si se fija: `coding` con CE.1 debe llevar la uri); HL70292 u otro nombre → convención; `display`: forma (`_codigo`, `conversion.py:1084-1103`, con `URI_SISTEMA` ampliado según la Q) | `dato_perdido` / `valor_distinto` / `codigo_mal_mapeado` | **cuenta** | `[G RXA:8]`; `[CM RXA-5 → vaccineCode]`; `[CM datatype-cwe-to-codeableconcept CWE.1/3/4/6/9]`; `[E4 11225-11232; 14892-14898]`; `[F :563-594]` |
| `patient` | resuelve al Patient#1 (`CV._sujeto` con clave `patient`); referencia lógica por identifier: convención | `referencia_rota` / `dato_perdido` | **cuenta** | `[G MSG_VXU_V04.csv:42]`; `[F :618-631]`; `[F Bundle bundle.profile.json:803-806]` |
| `encounter` | si hay PV1 y Encounter: ausente → convención (AMB-VX-5, Q-VX-D-9); presente → debe resolver al Encounter#1; sin PV1 → presente es `dato_inventado` | `referencia_rota` / `dato_inventado` | convención / **cuenta** | `[G MSG_VXU_V04.csv:20]` (sin fila de referencia); `[F :665-678]` |
| `occurrence[x]` | RXA-3 → `occurrenceDateTime` con R-CV-7 (precisión, instante si hay zona, hora local si no); `occurrenceString` → `valor_distinto`; ausente → `dato_perdido` (y `fhir_invalido`, 1..1); desde RXA-4 ≠ RXA-3 → `valor_distinto` | según | **cuenta** | `[G RXA:6]`; `[CM RXA-3 → occurrenceDateTime]`; `[E4 11212-11223]`; `[E2A 1700-1733]`; `[F :708-725]` |
| `recorded` | **R-VX-2 (AMB-VX-3):** admitidos = {ORC-9 si valorado} ∪ {RXA-22 si valorado y RXA-21 = A}. Si el conjunto no está vacío: ausente → `dato_perdido` (hecho ORC-9 si valorado, si no RXA-22); fuera → `valor_distinto`. Si está vacío: RXA-22 valorado con RXA-21 ≠ A y `recorded` = RXA-22 → nota `convencion`; otro valor → `dato_inventado` | según | **cuenta** | `[G ORC_Immunization.csv:17]`; `[G RXA:28]`; `[CM ORC-9 → recorded]`; `[CM RXA-22 → recorded IF RXA-21 EQUALS "A"]`; `[E4 2594-2599; 11451-11457]`; `[F :758-770]` |
| `primarySource`, `isSubpotent` | sin fila: presentes → `dato_inventado` (Q-VX-D-7) | `dato_inventado` | cuenta (Q-VX-D-7) | CV §3.0; `[F :792-805; :1515-1528]` |
| `reportOrigin` | sin fila; con RXA-9 valorado y `coding.code` = RXA-9.1 → convención (AMB-VX-9); sin RXA-9 → `dato_inventado` | `dato_inventado` | convención / cuenta | `[G RXA:12]` (comentario); `[E4 11263-11271]`; `[F :831-863]` |
| `location` | nunca cuenta (L-VX-1): RXA-11 valorado → nota `fuera_proyeccion`; sin RXA-11 → nota `extra` | — | nota | `[G RXA:16,33-34]`; `[E4 11159-11195; 11329-11344]` |
| `manufacturer` | RXA-17 (primera repetición): resuelve a una Organization con `identifier[].value` ∋ CE.1 y `name` = CE.2 desescapado; CE.9 → `name` si CE.2 vacío; `identifier.system` para MVX: Q-VX-D-1; solo `display` con CE.1 valorado → `dato_perdido`; solo CE.2 valorado y `display` = CE.2 → convención; vacío → ausente | `dato_perdido` / `valor_distinto` / `referencia_rota` / `dato_inventado` | **cuenta** | `[G RXA:22]`; `[CM RXA-17 → manufacturer(Organization)]`; `[CM datatype-cwe-to-organization CWE.1 → identifier.value, CWE.2 → name, CWE.3 → identifier.system, CWE.9 → name]`; `[E4 11393-11401; 14901-14986]`; `[F :922-935]` |
| `lotNumber` | RXA-15 (primera repetición) desescapado, texto exacto | `dato_perdido` / `valor_distinto` / `dato_inventado` | **cuenta** | `[G RXA:20]`; `[CM RXA-15 → lotNumber]`; `[E4 11375-11383]`; `[F :961-973]` |
| `expirationDate` | RXA-16 (primera repetición) → `date` con precisión del origen (`_fecha` tipo `date`); con hora → `fhir_invalido`; día añadido a `YYYYMM` → `dato_inventado` | según | **cuenta** | `[G RXA:21]`; `[CM RXA-16 → expirationDate]`; `[E4 11385-11391]`; `[F :999-1011]` |
| `site` | RXR-2: `coding {v2-0163, código}` si está en la 0163; `{v2-0550, código}` si está en la 0550; en las dos → cualquiera; fuera de ambas → convención; `{v2-0163, LD}` donde el conversor ponga `{v2-0550, LD}` → `codigo_mal_mapeado` (LD no está en la 0550) | `codigo_mal_mapeado` / `dato_perdido` / `dato_inventado` | **cuenta** (AMB-VX-2, Q-VX-D-2) | `[G RXR_Immunization.csv:5]`; `[CM RXR-2 → site mappedVia table-hl70550]`; `[CM table-hl70163-to-v2-0163]`; `[CM table-hl70550-to-v2-0550]`; `[E4 9250, 9341-9352]`; `[E7 CH07.txt:7892-7957]`; `[F :1033-1064]` |
| `route` | RXR-1 por la 0162: ID → `{v3-RouteOfAdministration, IDINJ}`, IM → `{…, IM}`, IV → `{…, IVINJ}`, PO → `{…, PO}`, SC → `{…, SQ}`, TD → `{…, TRNSDERM}`; los otros 41 → `{v2-0162, código}`; fuera de la 0162 → convención (`_codigo_tabla`, `conversion.py:856-875`) | `codigo_mal_mapeado` / `dato_perdido` / `dato_inventado` | **cuenta** | `[G RXR:4]`; `[CM RXR-1 → route mappedVia table-hl70162-to-v2-0162]`; `[CM table-hl70162-to-v2-0162]`; `[E4 9258-9339]`; `[F :1080-1111]` |
| `doseQuantity.value` | RXA-6 como texto decimal (Q-CV-D-10), forma canónica admitida (`.5` ≡ `0.5`; `0.50` ≠ `0.5`) | `valor_distinto` / `dato_perdido` / `dato_inventado` | **cuenta** | `[G RXA:9]`; `[CM RXA-6 → doseQuantity.value]`; `[E4 11234-11236]`; `[F :1127-1139]` |
| `doseQuantity.unit/.code/.system` | RXA-7 con las reglas de OBX-6 (`_unidades`): `unit` = CE.2 o CE.1; `code` = CE.1 y `system` = uri(CE.3) solo si ambos; UCUM/ISO+ → `http://unitsofmeasure.org`; RXA-7 vacío → sin unit/code/system | `dato_perdido` / `valor_distinto` / `codigo_mal_mapeado` / `dato_inventado` | **cuenta** | `[G RXA:10]`; `[CM datatype-cwe-to-quantity]`; `[E4 11244-11251]` |
| `performer[]` | **R-VX-3:** por cada repetición de RXA-10 con XCN.1 o XCN.2: un `performer` cuyo `actor` resuelve (recurso, `contained`, lógico, o `PractitionerRole.practitioner →`) a un Practitioner con `identifier[].value` ∋ XCN.1 y `name.family` = XCN.2, `given[1]` = XCN.3, y `function.coding` = `{v2-0443, AP}`; por cada repetición de ORC-12: igual con `{v2-0443, OP}` (actor PractitionerRole o Practitioner: forma, AMB-VX-8). Emparejamiento como `_participantes` (`conversion.py:955-1007`) por XCN.1 o `family`, prefiriendo el `function` esperado. `function` ausente: Q-VX-D-6 (recomendado `dato_perdido`); `function` con otro código → `codigo_mal_mapeado`; actor solo `display` con XCN.1 valorado → `dato_perdido`; sin XCN.1 → convención; actor Organization → `dato_perdido` (XCN es una persona); performers de más → nota `extra` | según | **cuenta** | `[G RXA:13-15]`; `[G ORC:20-22]`; `[CM segment-rxa-to-immunization RXA-10 ×3]`; `[CM segment-orc-to-immunization ORC-12 ×3]`; `[CM datatype-xcn-to-practitioner]`; `[CM datatype-xcn-to-practitionerrole]`; `[E4 11273-11300; 2714-2729]`; `[F :1162-1171, :1312-1343, :1355-1371]` |
| `reasonCode[]` | RXA-19: un CodeableConcept por repetición con CE.1 en `coding.code`; multiconjunto por `code`; `system`: convención | `dato_perdido` / `valor_distinto` / nota `extra` | **cuenta** | `[G RXA:24]`; `[CM RXA-19 → reasonCode]`; `[E4 11411-11417]`; `[F :1435-1466]` |
| `identifier[]` | ORC-2.1 → Identifier con `type.coding.code` PLAC; ORC-3.1 → FILL (`_informe` `conversion.py:1320-1330` como modelo); `type.coding.system` v2-0203: convención; EI.2-4 → `system`/`assigner`: convención; identifiers propios del conversor → nota `extra`; ORC-4.1 → nota (AMB-VX-1) | `dato_perdido` / `codigo_mal_mapeado` | **cuenta** | `[G ORC:5-10]`; `[CM segment-orc-to-immunization ORC-2/ORC-3]`; `[CM datatype-ei-extension-to-identifier EI.1 → value]`; `[E4 2353-2442]`; `[E2A 1886-1932]` |
| `meta.security` | ORC-28: nota (L-VX-2; `meta` es forma, L-CV-9) | — | nota | `[G ORC:38]`; `[CM table-hl70177-to-v3-confidentiality]` |
| `note[]`, `protocolApplied[]`, `education[]`, `programEligibility[]`, `fundingSource`, `reaction[]`, `subpotentReason[]`, `reasonReference[]` | sin fila; repetibles → nota `extra` (salvo AMB-VX-4, donde absorben un OBX: convención); `fundingSource` (0..1) sin OBX que lo sostenga → `dato_inventado` | según | nota / cuenta | CV §3.0; `[F :1397-1409; :1591-1614 (imm-1); :1872-1946; :2204]` |
| `id`, `meta`, `text`, extensiones, `display`, orden de listas, `Bundle.*` | forma | — | forma | L-CV-4, L-CV-9 |

### 3.2 Observation de los OBX del grupo ORDER (`Observation[2]` por OBX)

Se reutiliza `CV._observacion` (`conversion.py:1111-1149`) con `obr = None` (sin OBR-7 que heredar: con OBX-14 vacío, `effectiveDateTime`
presente es `dato_inventado`) y las filas de `OBX_Observation.csv` ya citadas en el perfil ORU (`:6, 8-26, 32-39, 43-51`). Lo propio de VXU:

| Elemento | Esperado | Clase | Nivel | Cita |
|---|---|---|---|---|
| existencia | una Observation por OBX del grupo, **o** (AMB-VX-4) el valor de OBX-5 (CE.1, o el texto/fecha) en algún elemento de la Immunization del grupo (`programEligibility`, `fundingSource`, `education.*`, `reportOrigin`, `reasonCode`, `note`) → nota `absorbido` (Q-VX-D-4); ni lo uno ni lo otro → `recurso_ausente` | `recurso_ausente` | **cuenta** / convención | `[G MSG_VXU_V04.csv:61-62]` y su Narrative-Condition |
| `subject` | resuelve al Patient#1 | `referencia_rota` / `dato_perdido` | **cuenta** | `[G MSG_VXU_V04.csv:61]` («Observation[2].subject.reference=Patient[1].id») |
| `partOf[]` | alguna referencia resuelve a la Immunization de su grupo; a otra Immunization → `referencia_rota`; ausente → `dato_perdido` (hecho `OBX(i.j)-3`) | según | **cuenta** | `[G MSG_VXU_V04.csv:61]` («Observation[2].partOf.reference=Immunization[1].id»); `[F Observation.partOf observation.profile.json:550-564]` |
| `note[]` | NTE del OBX: solo presencia (nota), como L-ORU-4 | — | nota (L-VX-7) | `[G MSG_VXU_V04.csv:66]`; `[F Observation.note :1228-1242]` |
| `status`, `code`, `value[x]`, `interpretation`, `referenceRange`, `effective[x]` | las reglas de `oru_conv` (CV §3.3) | las de CV | **cuenta** | `[G OBX_Observation.csv:6,8-26,32-39,43-51]` |

### 3.3 Patient, RelatedPerson / Patient.contact y Encounter

- **Patient:** CV §3.1 íntegro (`CV._patient`). Nada nuevo salvo las referencias que llegan a él (§3.1 `patient`, §3.2 `subject`, `RelatedPerson.patient`).
- **RelatedPerson / Patient.contact (R-VX-4, S-VX-11, Q-VX-D-5):** por cada NK1 con NK1-2 o NK1-3 valorados, una de las dos formas (§1.4):
  `name` (reglas de PID-5 sobre NK1-2; en `contact`, solo la primera repetición), `relationship` por la 0063 (tres `group`) y la 0131
  (NK1-7, identidad), `telecom` (NK1-5 por XTN; NK1-6 con `use work`), `address` (primera repetición), `gender` por la 0001, `period` por
  NK1-8/9; `birthDate` solo en RelatedPerson (en `contact`, convención). `RelatedPerson.patient` → Patient#1 (**cuenta**). Dos formas a la vez →
  nota `ambos`. Lo demás de NK1: nota.
- **Encounter (S-VX-10):** si hay PV1 y el Bundle trae Encounter, se juzga con `CV._encounter` tal cual (`conversion.py:879-902`; el evento
  `V04` no está en la 0003, así que `status` se decide solo por PV1-2/PV1-45, `:905-928`). Ausente: nota `convencion` (no `recurso_ausente`).

### 3.4 Las tablas de códigos que necesita el perfil (todas del paquete 1.0.0; `MAPAS_VXU`, cotejadas por la autoprueba como `conversion.py:1613-1626`)

| Tabla | ConceptMap | Filas con destino | Sin destino / fuera | Dónde se usa | Texto de 2.5 |
|---|---|---|---|---|---|
| 0322 Completion Status | `table-hl70322-to-event-status` (`sourceUri` v2-0322 → `event-status`) | CP → completed; RE → not-done; NA → not-done; PA → completed (4) | fuera de tabla: imposible (hoja no juzgada) | `Immunization.status` (R-VX-1) | `[E4 CH04.txt:11431-11436]` |
| 0323 Action Code | sin ConceptMap de tabla: la condición vive en el mapa de segmento | D → entered-in-error; A condiciona RXA-22; U sin efecto | fuera: imposible | `status`, `recorded` | `[E4 11445-11449]` |
| 0162 Route of Administration | `table-hl70162-to-v2-0162` (dos `group`) | 41 identidad v2-0162; ID → IDINJ, IM → IM, IV → IVINJ, PO → PO, SC → SQ, TD → TRNSDERM (v3-RouteOfAdministration) | user-defined: convención | `route` | `[E4 9276-9339]` |
| 0163 Body Site | `table-hl70163-to-v2-0163` | 55 identidad v2-0163 | — | `site` | `[E7 CH07.txt:7895-7957]` |
| 0550 Body Parts | `table-hl70550-to-v2-0550` | identidad v2-0550 (todas) | — | `site` (AMB-VX-2) | `[E4 9350-9352]` |
| 0443 Provider Role | constantes del mapa de segmento (`"AP"`, `"OP"`, `system v2-0443`); `table-hl70443-to-v3-participationtype` **no** se usa (mapea AD/AT/CP/RP/PP/PI, no AP/OP) | AP, OP | — | `performer.function` | `[G RXA:14-15]`, `[G ORC:21-22]` |
| 0292 CVX, 0227 MVX | sin ConceptMap (código literal; uri por Q-VX-D-1) | — | la pertenencia al CVX/MVX no se juzga (L-VX-4) | `vaccineCode`, `manufacturer.identifier` | `[E4 14728-14986]` |
| 0063 Relationship | `table-hl70063-to-v3-rolecode` (tres `group`) | 16 → v3-RoleCode; 12 identidad v2-0063; EMR → E, EMC → C, UNK → U, OTH → O (v2-0131) | user-defined: convención | `relationship` | `[E3 CH03.txt:7329-7342]` |
| 0131 Contact Role | `table-hl70131-to-v2-0131` | E, C, F, I, N, S, O, U identidad | user-defined: convención | `relationship[2]` | `[E3 7433]` |
| 0001 Administrative Sex | `table-hl70001-to-administrative-gender` (ya en `MAPAS`) | F, M, O, U, A, N | fuera: imposible | `RelatedPerson.gender`, `contact.gender` | `[E3 7533-7536]` |
| 0177 Confidentiality | `table-hl70177-to-v3-confidentiality` | (no se juzga: L-VX-2) | — | — | `[E4 3102-3105]` |
| 0203 Identifier Type | identidad (ya en CV) | PLAC, FILL | — | `identifier.type` | — |

### 3.5 Fechas, decimales y textos

Sin cambio: R-CV-7 para TS/DTM (`conversion.py:443-527`; `occurrenceDateTime`, `recorded`, `expirationDate` como `date`, `period`,
`birthDate`); Q-CV-D-10 y `_nm_canonico` para RXA-6 y OBX-5 NM; desescapado §2.7 para `lotNumber`, `name` de Organization/Practitioner y
`text`. `RXA-3` con `TS.2` (grado de precisión, B desde 2.3): se ignora.

### 3.6 Cómo se cita cada hallazgo (`C_VXU`, patrón `conversion.py:75-110`)

```
C_VXU = {"RXA-3": ["[CM segment-rxa-to-immunization RXA-3 → occurrenceDateTime]", "[G RXA_Immunization.csv:6]", "[E2A §2.A.22 DTM]", "[F Immunization.occurrence[x] 1..1]"],
         "RXA-5": ["[CM segment-rxa-to-immunization RXA-5 → vaccineCode]", "[CM datatype-cwe-to-codeableconcept]", "[G RXA_Immunization.csv:8]", "[E4 §4.18.1.1]"],
         "RXA-6": ["[CM segment-rxa-to-immunization RXA-6 → doseQuantity.value]", "[G RXA_Immunization.csv:9]"],
         "RXA-7": ["[CM datatype-cwe-to-quantity]", "[G RXA_Immunization.csv:10]"],
         "RXA-10": ["[CM segment-rxa-to-immunization RXA-10 → performer.actor(Practitioner), function AP]", "[CM datatype-xcn-to-practitioner]", "[G RXA_Immunization.csv:13-15]"],
         "RXA-15": ["[CM segment-rxa-to-immunization RXA-15 → lotNumber]", "[G RXA_Immunization.csv:20]"],
         "RXA-16": ["[CM segment-rxa-to-immunization RXA-16 → expirationDate]", "[G RXA_Immunization.csv:21]", "[E4 §4.14.7.16 YYYYMM]"],
         "RXA-17": ["[CM segment-rxa-to-immunization RXA-17 → manufacturer(Organization)]", "[CM datatype-cwe-to-organization]", "[G RXA_Immunization.csv:22]", "[E4 §4.18.1.2]"],
         "RXA-18": ["[CM segment-rxa-to-immunization RXA-18 → statusReason]", "[G RXA_Immunization.csv:23]"],
         "RXA-19": ["[CM segment-rxa-to-immunization RXA-19 → reasonCode]", "[G RXA_Immunization.csv:24]"],
         "RXA-20": ["[CM segment-rxa-to-immunization RXA-20 → status IF RXA-21 NOT EQUALS D]", "[CM table-hl70322-to-event-status]", "[G RXA_Immunization.csv:25-26]", "[E4 §4.14.7.20 tabla 0322]", "[F Immunization.status required]"],
         "RXA-21": ["[CM segment-rxa-to-immunization RXA-21 → status entered-in-error IF D]", "[G RXA_Immunization.csv:27]", "[E4 §4.14.7.21 tabla 0323]"],
         "RXA-22": ["[CM segment-rxa-to-immunization RXA-22 → recorded IF RXA-21 EQUALS A]", "[G RXA_Immunization.csv:28]", "[AMB-VX-3]"],
         "RXR-1": ["[CM segment-rxr-to-immunization RXR-1 → route]", "[CM table-hl70162-to-v2-0162]", "[G RXR_Immunization.csv:4]", "[E4 §4.14.2.1 tabla 0162]"],
         "RXR-2": ["[CM segment-rxr-to-immunization RXR-2 → site]", "[CM table-hl70163-to-v2-0163]", "[CM table-hl70550-to-v2-0550]", "[G RXR_Immunization.csv:5]", "[E4 §4.14.2.2]", "[AMB-VX-2]"],
         "ORC-2": ["[CM segment-orc-to-immunization ORC-2 → identifier[1] PLAC]", "[CM datatype-ei-extension-to-identifier]", "[G ORC_Immunization.csv:5-7]"],
         "ORC-3": ["[CM segment-orc-to-immunization ORC-3 → identifier[2] FILL]", "[G ORC_Immunization.csv:8-10]"],
         "ORC-9": ["[CM segment-orc-to-immunization ORC-9 → recorded]", "[G ORC_Immunization.csv:17]", "[AMB-VX-3]"],
         "ORC-12": ["[CM segment-orc-to-immunization ORC-12 → performer.actor(PractitionerRole), function OP]", "[CM datatype-xcn-to-practitionerrole]", "[G ORC_Immunization.csv:20-22]"],
         "RXA": ["[G MSG_VXU_V04.csv:42,58-59] ORC/RXA/RXR → Immunization[1]"], "OBX": ["[G MSG_VXU_V04.csv:61-62] OBX → Observation[2], partOf Immunization[1]"],
         "NK1-2": ["[CM segment-nk1-to-relatedperson NK1-2 → name[1]]", "[CM segment-nk1-to-patient NK1-2 → contact.name]", "[G NK1_RelatedPerson.csv:5]", "[G NK1_Patient.csv:5]"],
         "NK1-3": ["[CM table-hl70063-to-v3-rolecode]", "[G NK1_RelatedPerson.csv:6-7]", "[G NK1_Patient.csv:6]"],
         "NK1-5": ["[CM datatype-xtn-to-contactpoint]", "[G NK1_RelatedPerson.csv:9]"], "NK1-6": ["[G NK1_RelatedPerson.csv:10-11] use work"],
         "NK1-7": ["[CM table-hl70131-to-v2-0131]", "[G NK1_RelatedPerson.csv:12-14]"], "NK1-15": ["[CM table-hl70001-to-administrative-gender]", "[G NK1_RelatedPerson.csv:22]"],
         "NK1-16": ["[G NK1_RelatedPerson.csv:23]"], "NK1": ["[G MSG_VXU_V04.csv:16-17] NK1 → RelatedPerson[1] o Patient[1].contact"],
         "PV1": ["[G MSG_VXU_V04.csv:20] PV1 → Encounter[1] «only if the system wants»"]}
```

`consultar_tabla("perfil_guia_vxu")` devuelve `PERFIL_GUIA_VXU` (una fila por elemento de §3.1-§3.3 con `elemento`, `campo`, `regla`, `nivel`,
`citas`), como `perfil_guia_adt` (`conversion.py:1519-1541`; `mcp_verificador.py:1848-1851`).

---

## 4. El corpus sintético (`bases_vxu.py`)

### 4.1 Principios, y la regla contra la firma mecánica (R-VX-7)

1. **Cada base es un registro de vacunación completo y plausible en v2.5**, escrito desde `[E4 CH04.txt:12366-12421]` (estructura), `§4.14.7`
   y `§4.18` (RXA en vacunas), `§4.14.2` (RXR), `§4.5.1` (ORC) y el ejemplo `[E4 12601-12620]`: MSH, PID, [PD1], [NK1…], [PV1], ORC + RXA
   (+RXR) (+OBX/NTE) por grupo. Pacientes ficticios (seis), vacunas de la tabla 0292 de 2.5 (`[E4 14728-14898]`: 03 MMR, 08 Hep B pediátrica,
   10 IPV, 20 DTaP, 21 Varicela, 33 neumocócica, 48 Hib, 02 OPV, 19 BCG, 09 Td, 52 Hep A adulto, 88 gripe NOS), fabricantes de la 0227
   (`[E4 14901-14986]`: MSD, SKB, PMC, WAL, NOV, OTH), lotes y caducidades distintos, fechas repartidas por 2023-2024, cuatro profesionales.
2. **Cada base ejercita una rama de la guía** (una fila con condición, un `group` de un ConceptMap, una forma de dato), no un fallo
   supuesto de nadie. Las ramas son las de §3; la tabla de §4.2 dice cuál.
3. **Regla medible contra la firma de mutación:** `bases_vxu.py --firma` calcula, para cada par de bases, el número de campos
   (segmento-campo) con valor distinto y exige **≥ 3 en todo par**, y además que ningún par difiera solo en el campo que ejercita una de las
   dos. Lo que no cumpla se reescribe antes de sellar. Las ocho primeras bases son el **subconjunto de control**: registros planos donde todo
   lo mapeado está presente y es simple, para distinguir un mecanismo que muerde en todo el corpus de uno que solo muerde en la rama.
4. **Todas válidas** (ninguna lleva un valor imposible ni un segmento fuera de sitio): la autoprueba de `bases_vxu.py` afirma, para cada base,
   que `MR.mensajes` la lee, que `PE.estructura_de(m, PUNTOS["vxu_conv"])` da `VXU_V04`, que `estructuras_hl7.emparejar` no da ausentes ni
   fuera de orden, que todo TS pasa `MR.partes_dtm`, todo NM pasa `NM_RE` y RXA-20/21, RXR-1/2 están en 0322/0323/0162/0163-0550 (o son
   locales declarados). Los imposibles van a P-VX, no al corpus (como `bases_oru.py:3-4`).
5. **Sin esperado escrito**: el fichero no guarda ningún Bundle ni canónico (`bases_oru.py:10-11`); la previsión se sella aparte (§5).
6. **Deterministas**: `bases_vxu/BNN.hl7` (segmentos separados por CR, sin MLLP) y `bases_vxu.jsonl` (`id`, `descripcion`, `ejercita`,
   `fichero`, `msh10 = "VXU-BNN"`, `segmentos`), con la huella del conjunto en el índice.

### 4.2 Las 40 bases y qué ejercita cada una

Piezas comunes: `MSH|^~\&|REGVAC|CSSYN|REGISTRO|SALUD|<fecha>||VXU^V04^VXU_V04|VXU-BNN|P|2.5`; `PID` de seis ficticios (`VAC0001^^^CSSYN^MR`…,
dos con segunda repetición `PI`); `ORC|RE|<placer opcional>|VX-NN^REGVAC`; `RXA|0|1|<fecha>|<fecha>|<CVX>|<dosis>|<unidad>|||<XCN>|||||<lote>|<cad>|<MVX>|<rechazo>|<indicación>|<0322>|<0323>|<entrada>`;
`RXR|<0162>^<texto>^HL70162|<0163>^<texto>^HL70163`.

| Id | Qué es | Ejercita (rama de la guía) |
|---|---|---|
| B01 | **Control.** MMR (03^MMR^CVX), 0.5 `mL^^UCUM`, RXA-10 completo, lote, caducidad `YYYYMM`, `MSD^Merck \T\ Co., Inc.^MVX`, CP, A, RXA-22; RXR IM/LD | CP → completed; IM → v3 IM; LD → v2-0163; `\T\` en RXA-17.2; YYYYMM → `2025-11`; AP |
| B02 | **Control.** Varicela (21) SC/RA, `0.5^^` con `mL^mililitro^UCUM`, SKB, CP, sin RXA-21 ni RXA-22 | SC → SQ; RA; unit = CWE.2; sin recorded |
| B03 | **Control.** DTaP (20) IM/LT a un lactante; RXA-3 solo fecha; caducidad `YYYYMMDD`; ORC-2 y ORC-3 | fecha sin hora; PLAC+FILL; LT |
| B04 | **Control.** IPV (10) IM/RVL; `1` `mL^^ISO+`; ORC-12 ordenante distinto de RXA-10 | ISO+ → unitsofmeasure; dos performers OP/AP |
| B05 | **Control.** OPV (02) oral: RXR `PO^Oral^HL70162` sin RXR-2; `2` `[drp]^gota^UCUM` | PO → v3 PO; sin `site`; UCUM con corchetes |
| B06 | **Control.** BCG (19) ID/LUA; PMC | ID → IDINJ; LUA |
| B07 | **Control.** Hib (48) IM/RD; **RXA-20 vacío**, RXA-21 vacío | vacío → `completed` |
| B08 | **Control.** Neumocócica (33) IM/LD adulto; `0.25` mL; RXA-20 PA | PA → completed; decimal `0.25` |
| B09 | Hep A (52) rechazada: RXA-20 RE, RXA-18 `REL^Motivo religioso^L`, RXA-6 `0`, sin RXR | RE → not-done; statusReason; dosis 0 |
| B10 | Td (09) no administrada: RXA-20 NA, RXA-18 `CTR^Contraindicacion^L` | NA → not-done |
| B11 | MMR con RXA-21 **D** y RXA-20 CP (corrección de registro) | D prevalece → entered-in-error |
| B12 | DTaP con RXA-21 U, RXA-22 valorado y ORC-9 valorado | AMB-VX-3: U no manda RXA-22; recorded = ORC-9 |
| B13 | Varicela con RXA-21 A, RXA-22 y ORC-9 valorados y **distintos** | AMB-VX-3: conjunto {ORC-9, RXA-22} |
| B14 | Hep B (08) con RXA-3 `YYYYMMDDHHMMSS+0200` y RXA-4 posterior (fin ≠ inicio) | zona por instante; RXA-4 no es occurrence |
| B15 | IPV con RXA-3 `YYYYMMDDHHMM` sin zona | precisión de minutos, hora local |
| B16 | Gripe (88) con RXA-15 repetido (`LOT-A~DIL-B`) y caducidad `YYYYMMDD` | AMB-VX-7 (primera repetición); `date` completo |
| B17 | Neumocócica con RXA-17 `^Laboratorio Sintetico^` (solo texto) | manufacturer sin identifier: name |
| B18 | MMR con RXA-17 `MSD^Merck^MVX^MERCK^Merck S.A.^L` | CWE.4-6 de RXA-17: nota |
| B19 | MMR con RXA-5 `03^MMR^CVX^TV^Triple virica^L` | CE.4-6 → coding[2] |
| B20 | DTaP con RXA-5.3 = `HL70292` (el texto de 2.5 pide `CVX`) | `system` convención; `[E4 14898]` |
| B21 | Hib con **dos** RXA-10 (dos profesionales) | performer AP ×2 |
| B22 | Td con RXA-10 sin XCN.1 (solo nombre) | actor solo `display`: convención |
| B23 | Gripe con **solo ORC-12** (sin RXA-10) | un performer OP |
| B24 | Hep B con ORC-2/ORC-3 con EI.2-4 (`VX-24^REGVAC^1.2.3.4^ISO`) | EI.2-4 → system/assigner: convención |
| B25 | MMR con ORC-4 (grupo de órdenes, EI en 2.5) | AMB-VX-1: nota |
| B26 | Varicela con ORC-28 `V` | L-VX-2: `meta.security` no se juzga |
| B27 | DTaP con RXR-2 `DELT^Deltoid^HL70550` | 0550 → `{v2-0550, DELT}` |
| B28 | IPV con RXR-2 `368208006^Left upper arm^SCT` | sitio fuera de 0163/0550: convención |
| B29 | Gripe con RXR-1 `JET^Inyector a presion^L` (0162 es user-defined) | ruta fuera de la 0162: convención |
| B30 | MMR con OBX CE ×2 (`64994-7^Elegibilidad^LN` → `ELE^Elegible programa^L`; `30963-7^Fuente de financiacion^LN` → `PUB^Publica^L`) | OBX → Observation partOf; AMB-VX-4 (absorción) |
| B31 | DTaP con OBX DT ×2 (`29768-9` fecha publicación, `29769-7` fecha entrega de la hoja informativa) | OBX DT; partOf |
| B32 | Varicela con OBX NM `8310-5^Temperatura^LN` `38.5` `Cel^^UCUM` y NTE (reacción, como `[E4 12617-12620]`) | OBX NM + UCUM + NTE (nota) |
| B33 | **Dos** grupos ORDER (DTaP + IPV, misma visita), ORC-3 distintos, RXR por grupo | emparejamiento por identifier; recuentos |
| B34 | **Tres** grupos ORDER del mismo CVX (20) en tres fechas (serie), ORC-3 distintos | tres Immunization del mismo código |
| B35 | Dos grupos, uno RE y otro CP, **sin ORC-2 ni ORC-3** (`ORC|RE`) | emparejamiento por código+fecha; nota ORC-3 |
| B36 | Lactante con NK1 `MTH`: nombre, PRN PH, dirección, NK1-15 F, NK1-16 | NK1 → RelatedPerson/contact; MTH → v3-RoleCode |
| B37 | Niño con dos NK1: `FTH` (con NK1-6 WPN y NK1-7 `C`) y `GRD` (identidad v2-0063) | NK1 ×2; 0131; `use work` |
| B38 | Adulto con PD1-3/PD1-4, PD1-16 `A^Activo^L`, PV1 `R` con PV1-19 y PV2 | PD1 nota; PV1 opcional; L-VX-3 |
| B39 | Niña con SFT, GT1, IN1/IN2, MSH-9.3 vacío, MSH-18 `UNICODE UTF-8`, `ñ` en PID-5 y NK1-2 | segmentos sin mapa (recuento); AMB-MT-1; UTF-8 |
| B40 | Gripe adulto con RXA-19 ×2 (`DM^Diabetes^L~ASM^Asma^L`), RXR IM/RD, `\S\` en RXA-17.2 | reasonCode ×2; escapes |

Cobertura (afirmada por `bases_vxu.py --cobertura` contra `PERFIL_GUIA_VXU`): toda fila de nivel **cuenta** de §3.1-§3.3 tiene al menos una
base que la ejercita con el campo valorado y al menos una con el campo vacío; la 0322 entera (CP ×muchas, RE B09/B35, NA B10, PA B08,
vacío B07) y la 0323 (A, D B11, U B12); los seis códigos del grupo 2 de la 0162 que caben en vacunas (ID, IM, PO, SC) más dos de identidad
(IN no: no hay vacuna intranasal en la 0292 de 2002; se sustituye por un local, B29); 0163, 0550 y SCT en el sitio; un, dos y tres grupos ORDER;
cero, uno y dos NK1.

### 4.3 Cómo se genera (`verificador/bases_vxu.py`, forma de `bases_oru.py`)

```
def msh(n, ver="2.5", msh18="", est="VXU_V04"): ...        # MSH-7 distinto por base; MSH-10 "VXU-B%02d"
PIDS = {"mateo": "PID|1||VAC0001^^^CSSYN^MR||Prueba^Mateo^^^^^L||20230512|M", ...}   # seis ficticios
def orc(n, placer="", filler=None, orc9="", orc12="", orc4="", orc28=""): ...
def rxa(sub, fecha, cvx, dosis, unidad, prov="", lote="", cad="", mvx="", rech="", ind="", c20="CP", c21="A", c22="", fin=None): ...
def rxr(ruta, sitio=None): ...
def obx(j, tipo, cod, val, uni="", st="F", t14=""): ...     # igual que bases_oru.obx
def nk1(k, nombre, rel, tel="", dir_="", tel_trabajo="", rol="", sexo="", nac=""): ...
def base(n, descripcion, ejercita, segs): ...
def construir(): ... 40 bases; assert ids B01..B40
BASES = construir()
def cable(b): return "\r".join(b["segmentos"]) + "\r"
def firma(): ...        # pares de bases: nº de campos distintos; falla si alguno < 3 o si difieren solo en el campo ejercitado
def cobertura(): ...    # filas «cuenta» de PERFIL_GUIA_VXU con base valorada y vacía
def autoprueba(): ...   # lectura, estructura VXU_V04, TS/NM/tablas, firma, cobertura, determinismo (sha256 del conjunto)
def escribir(): ...     # bases_vxu/BNN.hl7 + bases_vxu.jsonl
```

Uso: `python3 bases_vxu.py` escribe; `--lista`, `--firma`, `--cobertura`, `--autoprueba`. Solo biblioteca estándar. `bases_vxu.py` no importa
`conversion_vxu` salvo para `--cobertura` (lee `PERFIL_GUIA_VXU`, datos, no juicio), de modo que un error del perfil no se confirme a sí mismo.

### 4.4 Las variantes, de un vistazo

| Dimensión | Variantes en el corpus (bases) |
|---|---|
| RXA-20 / RXA-21 | CP+A (B01, B03-B06, B08…); CP sin RXA-21 (B02); vacío (B07); PA (B08); RE (B09, B35); NA (B10); D (B11); U (B12); A con RXA-22 (B01, B13) |
| RXR | IM/LD, SC/RA, IM/LT, IM/RVL, PO sin sitio, ID/LUA, IM/RD, IM/DELT-0550 (B27), IM/SCT (B28), local/LD (B29), **sin RXR** (B09, B10) |
| ORC | FILL solo (mayoría); PLAC+FILL (B03); EI.2-4 (B24); ORC-4 (B25); ORC-9 (B12, B13); ORC-12 (B04, B23); ORC-28 (B26); **sin ORC-2/3** (B35) |
| OBX bajo ORDER | ninguno (mayoría); CE ×2 (B30); DT ×2 (B31); NM+NTE (B32) |
| Varias RXA | una (36 bases); dos (B33, B35); tres del mismo código (B34) |
| RXA-3 | fecha (B03 y otras); minutos (B15); segundos+zona (B14); segundos sin zona (B01) |
| RXA-6/7 | `0.5 mL^^UCUM`, `0.5 mL^mililitro^UCUM`, `1 mL^^ISO+`, `2 [drp]`, `0.25`, `0` |
| RXA-15/16/17 | lote simple / repetido (B16); `YYYYMM` / `YYYYMMDD`; MVX con texto, solo texto (B17), con alterno (B18), con `\T\` (B01) y `\S\` (B40) |
| RXA-10 / ORC-12 | AP ×1, AP ×2 (B21), sin XCN.1 (B22), OP solo (B23), AP+OP (B04) |
| NK1 / PD1 / PV1 | NK1 ×1 (B36), ×2 (B37); PD1+PV1+PV2 (B38); SFT/GT1/IN1 (B39) |

---

## 5. La previsión sellada

### 5.1 Forma (R-VX-8)

Antes de correr nada, VX2 escribe y sella `prevision-vxu.json` con: la huella del juez, la huella de `bases_vxu` (`por_corpus["vxu"]` del
manifiesto), y por conversor: `corre_en_caja` (probabilidad), los rangos de `correcto` / `fallo_silencioso` / `rechazo_incorrecto` /
`indeterminado` sobre las 40 bases, la lista de mecanismos MC-VX-n con `{hecho, subtipo, ruta FHIR, probabilidad, bases_que_lo_disparan}`,
la probabilidad de **≥ 1 nueva confirmada**, y las reglas de «fuera de previsto». La tabla de §5.2 es la versión de hoy, a ciegas; VX2 solo
le añade las cuentas de E-VX-3 y del corpus (n por mecanismo) antes de sellar.

### 5.2 Mecanismos previstos (A alta, M media, B baja; la cita es la del perfil que lo juzga)

| Id | Mecanismo (hecho, subtipo) | Microsoft | LinuxForHealth | Bases que lo disparan |
|---|---|---|---|---|
| MC-VX-1 | RXR-1 IM/SC/PO/ID → `{v2-0162, código}` o sin system en vez de v3-RouteOfAdministration (`codigo_mal_mapeado` RXR-1) | **A** | **A** | todas con RXR (B01-B08, B11-B28, B30-B40) |
| MC-VX-2 | RXA-6 reserializado (`0.50` → `0.5`, `.5` → `0.5` es forma) (`valor_distinto` RXA-6) | A | A | las de dos decimales (B08) y las que un conversor normalice |
| MC-VX-3 | RXA-7: `unit` de CE.1 en vez de CE.2; `code` sin `system`; ISO+ no canónico (`valor_distinto`/`dato_perdido` RXA-7) | M | M | B02, B04, B05 |
| MC-VX-4 | RXA-17 → Organization solo con `name`, o `manufacturer.display` (MVX perdido) (`dato_perdido` RXA-17) | M-A | M | todas con RXA-17 código (34) |
| MC-VX-5 | RXA-10/ORC-12 sin `performer.function`, o con el mismo código para los dos (`dato_perdido`/`codigo_mal_mapeado`) | M | M-A | B04, B21, B23 y todas con RXA-10 |
| MC-VX-6 | RXA-16 `YYYYMM` completado a día o perdido (`dato_inventado`/`dato_perdido` RXA-16) | M | M | B01 y las de `YYYYMM` |
| MC-VX-7 | RXA-3 solo fecha → `T00:00:00` (`dato_inventado` RXA-3); minutos → segundos añadidos | M | M | B03, B15 |
| MC-VX-8 | RXA-20 vacío → `status` distinto de `completed`, o PA → `not-done`, o RE/NA → `completed` (`valor_distinto`/`codigo_mal_mapeado` RXA-20) | M | M | B07, B08, B09, B10, B35 |
| MC-VX-9 | RXA-21 D ignorado (`status` `completed` donde toca `entered-in-error`) (`valor_distinto` RXA-21) | M | M-A | B11 |
| MC-VX-10 | `recorded` = RXA-22 con RXA-21 U (convención) o ausente con ORC-9 (`dato_perdido` ORC-9) | M | M | B12, B13 |
| MC-VX-11 | ORC-2/3 → identifier sin type, type intercambiado o ausente (`dato_perdido`/`codigo_mal_mapeado` ORC-2/3) | M | M | B03, B24 y todas con ORC-3 |
| MC-VX-12 | OBX de ORDER sin `partOf` (`dato_perdido`), o absorbidos en Immunization (convención AMB-VX-4), o perdidos (`recurso_ausente`) | M-A | M | B30, B31, B32 |
| MC-VX-13 | RXA-5/RXA-17 `system` no canónico para CVX/MVX (`codigo_mal_mapeado` si Q-VX-D-1 lo fija; si no, convención) | M | M | todas |
| MC-VX-14 | NK1-3 → `{v2-0063, MTH}` en vez de v3-RoleCode (`codigo_mal_mapeado` NK1-3); o NK1 perdido (`recurso_ausente`) | M-A | M | B36, B37 |
| MC-VX-15 | Varias RXA → una sola Immunization, o Observation de un grupo colgada de otro (`recurso_ausente`/`referencia_rota`) | B-M | B-M | B33, B34, B35 |
| MC-VX-16 | RXA-18 → `statusReason` ausente con RE/NA (`dato_perdido` RXA-18); RXA-19 → `reasonCode` parcial | M | M | B09, B10, B40 |
| MC-VX-17 | `primarySource` por omisión (`dato_inventado`, Q-VX-D-7) | M-A | M | todas |
| MC-VX-18 | RXR-2 `{v2-0550, LD}` o SNOMED inventado para LD (`codigo_mal_mapeado` RXR-2) | B-M | B-M | todas con sitio 0163 |
| MC-VX-19 | Rechazo (`error`) de VXU válidos por plantilla o por segmentos sin mapa (SFT, GT1, IN1, TQ1) (`rechazo_incorrecto`) | B | B-M | B38, B39 |
| MC-VX-20 | `occurrenceString` en vez de `occurrenceDateTime` (`valor_distinto` RXA-3) | B | B | todas |

### 5.3 Previsión agregada (lo que VX2 debe encontrar, con cota)

| Conversor | Corre VXU en la caja (E-VX-3) | `correcto` | `fallo_silencioso` | `rechazo_incorrecto` | `indeterminado` | Mecanismos que cuentan (distintos) | ≥ 1 **nueva confirmada** tras VX3 |
|---|---|---|---|---|---|---|---|
| Microsoft (40 bases) | 0,85 | 10-40 % | 55-90 % | 0-10 % | ≤ 2 % | 4-8 | 0,7 |
| LinuxForHealth (40 bases) | 0,85 | 10-40 % | 55-90 % | 0-10 % | ≤ 2 % | 4-8 | 0,7 |
| Muestras públicas de los proyectos (E-VX-2, 2.5.1 en su mayoría) | — | se juzgan con banderas L18; ≥ 70 % de lo que cuente será `ya_declarada` | | | | | — |

- Al menos una nueva confirmada en **alguno** de los dos: **0,85**. Frase fija prevista: N ≥ 2, K ∈ {1, 2}, D ≥ 2, C ≥ 8 (las convenciones
  serán: RelatedPerson/contact, ids, fullUrl, Provenance/MessageHeader, `display`, orden de `coding`, `system` de códigos locales).
- La más probable de las nuevas: MC-VX-1 (la ruta con system v2-0162), porque el mapa de la 0162 es el único de la guía con dos `group`
  hacia sistemas distintos para una misma tabla y el conversor por plantilla suele escribir un solo system.
- **Fuera de previsto** = un mecanismo que cuente y no esté en 5.2; un porcentaje fuera de su rango; `indeterminado` > 2 % (lector/emparejador);
  un conversor que rechace > 10 % del corpus 2.5. Cada uno se adjudica (juez / perfil / corpus / caja) con cita antes de VX3.
- **Lo que no preveo** (y si aparece, es la señal): un `recurso_inventado` (una Immunization sin RXA), una `referencia_rota` en `patient`, o
  `fhir_invalido` masivo (`status` fuera del ValueSet).

---

## 6. Lo que cambia en la herramienta (`cv/verificar_conversor.py`, `cv/conversor_juguete.py`)

Hoy: `punto(t)` decide solo por MSH-9.1: `ORU → oru_conv`, lo demás → `adt_conv` (`verificar_conversor.py:394-397`, S-VC-22); el corpus es
`CORPUS = ("adt", "oru", "muestras", "minimos", "propio")` (`:49`) y `generar_corpus` escribe por carpeta con una huella por corpus y una
huella conjunta `huella_adt_oru_muestras` (`:436-463`); `L-VC-2` dice que solo juzga ADT y ORU (`:66-67`).

| Pieza | Cambio (R-VX-9) | Lo que no cambia (y cómo se afirma) |
|---|---|---|
| `punto(t)` | `"oru_conv" if c[0].upper().startswith("ORU") else "vxu_conv" if c[0].upper().startswith("VXU") else "adt_conv"` | ADT, ORU, SIU, MDM, ORM… dan lo mismo que hoy; P-VX-21 repite `prueba_vc.p07` (`{"a": "adt_conv", "b": "oru_conv", "s": "adt_conv"}`, `cv/prueba_vc.py:364-365`) y añade `"v": "vxu_conv"` |
| `CORPUS` | `("adt", "oru", "vxu", "muestras", "minimos", "propio")` | las carpetas `adt` y `oru` se escriben con los mismos ficheros: `por_corpus["adt"]` y `["oru"]` idénticas a las de hoy; `huella_adt_oru_muestras` idéntica (es la que compara con CV2) |
| `generar_corpus(lab=True)` | añade `textos["vxu"] = [("VXU-%s.hl7" % b["id"], normal(BV.cable(b))) for b in BV.BASES]` (`import bases_vxu as BV`) | `n["adt"]`, `n["oru"]` iguales; el recuento total sube en 40 (`prueba_vc.p06` «sin mínimos» pasa de 303 a 343: cambio declarado) |
| `plantilla(t, regla)` | nada: `msh9_tipo_evento` ya da `VXU_V04` (`:400-409`) | `prueba_vc.p08` igual |
| `L_VC["L-VC-2"]` | «Solo juzga lo que juzgan adt_conv, oru_conv y vxu_conv: ADT de los ocho eventos, ORU^R01 y VXU^V04…» | — |
| `agregar` / `informe_md` / `comprobar_informe` | nada en el código: iteran `CORPUS` y `CLASES8` (`:893-899, :1002`); aparece la fila `vxu` | la fila `adt`/`oru` del informe no cambia para el mismo corpus |
| `pares_minimos` | los pares mínimos de VXU (VX3) van en `cv3_minimos_vxu.PARES`, lista aparte, y entran solo si el corpus lleva `vxu` | `MIN.PARES` (los 68) no cambia de tamaño ni de contenido |
| `juzgar` | nada: `V.verificar(e)` despacha por el PE de la evidencia; `clase8` ya agrupa `recurso_*` (`:835-842`) | — |
| `conversor_juguete.py` | `JUGUETE-NOMINAL` escribe el Bundle nominal de VXU (Patient + Immunization + Practitioner + Organization, a mano, copiado de `prueba_conversion_vxu.py`) cuando MSH-9.1 = VXU; directiva nueva `JUGUETE-RUTA` (el nominal con `route {v2-0162, IM}`) como control positivo | las directivas de hoy (`:13-22`) y sus Bundles ADT/ORU no se tocan |
| `adaptador.json` de los dos conversores | nada obligatorio; `declara.no_soporta` puede listar `VXU^V04` si un conversor no trae plantilla (`:921-929`) | — |

Un `error` del conversor por «sin plantilla» (`:385`) para `VXU_V04` es `sin_plantilla` sin entrar en la caja (L-VC-13) y se contabiliza como
«no corre VXU» en E-VX-3.

---

## 7. Pruebas en rojo antes del código (P-VX-n)

Todas en `verificador/prueba_conversion_vxu.py` (forma de `prueba_conversion.py:17-30, 137-194`: `mira`, `seg`, `msg_vxu(...)`, Bundles
escritos **a mano**, `ev(m, b, pe="vxu_conv")`, `cuentan`, `notas`). «Hoy» = sin la gramática, sin el PE y sin `conversion_vxu`: `PE.resolver`
lanza `ValueError` (`puntos_entrada.py:161-163`) y todas fallan por construcción (`prueba_conversion_vxu.py rojo` sale 0 solo si fallan todas).
El control negativo es lo que debe seguir dando `correcto` o `0 hallazgos que cuentan`.

| P | Pieza | Caso | Esperado | Control negativo |
|---|---|---|---|---|
| P-VX-1 | gramática, PE y evidencia | `EH.gramatica("VXU_V04")` existe y `PE.estructura_de(m, PUNTOS["vxu_conv"])` = `VXU_V04`; VXU nominal (B01) con Bundle exacto | `correcto`, `cuenta = []`, `recuentos = {Patient: 1, Immunization: 1, grupos_orden: 1, …}` | `status not-done` con RXA-20 CP → `fallo_silencioso/convertido`, `[("fidelidad", "codigo_mal_mapeado", "RXA-20")]` |
| P-VX-2 | R-VX-1 status | RXA-20 ∈ {CP, PA} → `completed`; {RE, NA} → `not-done`; vacío → `completed`; RXA-21 D con RXA-20 CP → `entered-in-error` | 0 cuentan en los seis | RXA-21 D con `completed` → `valor_distinto` RXA-21; vacío con `not-done` → `valor_distinto` RXA-20; RXA-20 `XX` con `status "XX"` → `valor_imposible_convertido+fhir_invalido` fusionados en RXA-20; `XX` con `error` → `correcto` + nota `aceptable`; `status` ausente → `fhir_invalido` |
| P-VX-3 | vaccineCode | `03^MMR^CVX^TV^Triple virica^L` → `coding` con `03` y con `TV`; `system` según `DECISIONES["Q-VX-D-1"]` | 0 cuentan | `code 3` → `valor_distinto` RXA-5; sin `coding` → `dato_perdido`; con Q fijada, `system http://hl7.org/fhir/sid/cvx` ausente → `codigo_mal_mapeado`; `HL70292` como CE.3 → 0 cuentan (convención) |
| P-VX-4 | occurrence | `20230104` → `2023-01-04`; `20230104101500+0200` → `2023-01-04T08:15:00Z`; `202301041015` → `…T10:15:00+01:00` | 0 cuentan | `2023-01-04T00:00:00+01:00` desde fecha sola → `dato_inventado`; `occurrenceString "2023-01-04"` → `valor_distinto`; `…T10:15:00` sin zona → `fhir_invalido`; RXA-4 posterior usado como occurrence → `valor_distinto` RXA-3 |
| P-VX-5 | dosis | `.5` + `mL^^UCUM` → `value 0.5` o `.5`, `unit mL`, `code mL`, `system unitsofmeasure`; `0.5` + `mL^mililitro^UCUM` → `unit mililitro` | 0 cuentan | `value 0.50` → `valor_distinto` RXA-6; `unit` ausente → `dato_perdido` RXA-7; `system` v2 → `codigo_mal_mapeado`; RXA-7 vacío con `unit mL` → `dato_inventado` |
| P-VX-6 | ruta y sitio | IM → `{v3-RouteOfAdministration, IM}`; SC → `SQ`; PO → `PO`; ID → `IDINJ`; `IN` → `{v2-0162, IN}`; LD → `{v2-0163, LD}`; DELT → `{v2-0550, DELT}`; SCT → 0 cuentan | 0 cuentan | `{v2-0162, IM}` → `codigo_mal_mapeado` RXR-1; `{v2-0550, LD}` → `codigo_mal_mapeado` RXR-2; `route` sin RXR → `dato_inventado`; RXR presente y `route` ausente → `dato_perdido` |
| P-VX-7 | performers | RXA-10 `1234^Goldstein^Harold^A^^DR` → performer AP con Practitioner `identifier 1234`, `family Goldstein`; ORC-12 `5678^Ruiz^Ana` → performer OP con PractitionerRole → Practitioner 5678; también OP con Practitioner directo | 0 cuentan en las dos formas | funciones intercambiadas → `codigo_mal_mapeado` RXA-10 y ORC-12; actor solo `display` con XCN.1 → `dato_perdido`; `function` ausente → según `Q-VX-D-6` (`dato_perdido` recomendado); actor Organization → `dato_perdido` |
| P-VX-8 | fabricante | `MSD^Merck \T\ Co., Inc.^MVX` → Organization `identifier MSD`, `name "Merck & Co., Inc."`; `contained` y lógico por identifier también | 0 cuentan | `manufacturer.display` solo → `dato_perdido` RXA-17; `name "Merck \T\ Co., Inc."` literal → `valor_distinto`; `^Laboratorio Sintetico^` con `display` igual → 0 cuentan |
| P-VX-9 | lote y caducidad | RXA-15 `LOT-A~DIL-B` → `lotNumber LOT-A` (+ nota); RXA-16 `202511` → `2025-11`; `20251130` → `2025-11-30` | 0 cuentan | `2025-11-01` desde `202511` → `dato_inventado` RXA-16; `lotNumber` ausente → `dato_perdido`; `lotNumber DIL-B` → `valor_distinto` (o 0 cuentan si Q-VX-D-8 = cualquiera) |
| P-VX-10 | statusReason, reasonCode | RE + RXA-18 `REL^…^L` → `statusReason.coding.code REL`; RXA-19 `DM~ASM` → dos `reasonCode` | 0 cuentan | un solo `reasonCode` → `dato_perdido` RXA-19; `statusReason` ausente → `dato_perdido` RXA-18; `statusReason` sin RXA-18 → `dato_inventado` |
| P-VX-11 | recorded (R-VX-2) | ORC-9 solo; RXA-22 con A; ambos → cualquiera de los dos | 0 cuentan en los tres | RXA-22 con U, ORC-9 vacío y `recorded` = RXA-22 → nota `convencion`, 0 cuentan; `recorded` con otra fecha → `dato_inventado`; ORC-9 valorado y `recorded` ausente → `dato_perdido` ORC-9 |
| P-VX-12 | identifiers | ORC-2 `PL-1`, ORC-3 `VX-1^REGVAC` → PLAC y FILL | 0 cuentan | intercambiados → `codigo_mal_mapeado`; FILL ausente → `dato_perdido` ORC-3; identifier propio del conversor → nota `extra` |
| P-VX-13 | varias RXA (§2.2) | dos grupos con ORC-3 → `emparejado_por identifier`; tres grupos del mismo código y distinta fecha sin ORC-3 → `codigo+fecha`; un grupo RE y uno CP | 0 cuentan; `recuentos.Immunization = 2 / 3` | una Immunization para dos RXA → `recurso_ausente` `RXA(2)-5`; Immunization de más → `recurso_inventado`; dos candidatas iguales → `indeterminado/emparejamiento` |
| P-VX-14 | OBX de ORDER (§3.2) | OBX CE con Observation `subject` Patient y `partOf` Immunization#1; OBX DT; OBX NM con UCUM | 0 cuentan | `partOf` ausente → `dato_perdido` `OBX-3`; `partOf` a otra Immunization → `referencia_rota`; OBX sin Observation y valor en `programEligibility` → nota `absorbido` (0 cuentan; `recurso_ausente` si Q-VX-D-4 = literal); sin Observation ni absorción → `recurso_ausente` |
| P-VX-15 | NK1 (§3.3) | NK1 MTH → RelatedPerson `{v3-RoleCode, MTH}`, `patient` → Patient, `name`, `telecom`, `gender female`, `birthDate`; la misma NK1 como `Patient.contact` → 0 cuentan | 0 cuentan en las dos formas | `{v2-0063, MTH}` → `codigo_mal_mapeado` NK1-3; ni RelatedPerson ni contact → `recurso_ausente` NK1; NK1-6 sin `use work` → `valor_distinto` NK1-6; `contact` sin `birthDate` → 0 cuentan (convención) |
| P-VX-16 | PV1 opcional | PV1 con Encounter → `encounter` resuelve; PV1 sin Encounter → 0 cuentan (nota) | 0 cuentan | `Immunization.encounter` a nada → `referencia_rota`; `encounter` sin PV1 → `dato_inventado`; dos Encounter → `recurso_duplicado` |
| P-VX-17 | fuera del perfil | PD1-3/4, PD1-16, RXA-11, RXA-9, GT1, IN1, SFT, TQ1, OBX antes del ORC, ORC-4, ORC-28 → solo notas | 0 cuentan; `obx_fuera_orden = 1`; `otros_tipos` con Coverage/Device si los hay | `Immunization.location` sin RXA-11 → nota `extra` (0 cuentan); `primarySource true` → `dato_inventado` (Q-VX-D-7); `reportOrigin` sin RXA-9 → `dato_inventado`; con RXA-9 → nota |
| P-VX-18 | estructura y versión | MSH-9.3 vacío → nota; MSH-12 2.5.1 con RXA-20 `XX` → nota `version` L18, 0 cuentan; RXR delante de RXA → se ignora con nota; `error` con VXU nominal → `rechazo_incorrecto` | según | MSH-12 2.5 con RXA-20 `XX` y `status "XX"` → cuenta; QBP^Q11 → `fuera_de_alcance`; `error` sin PID → `correcto` + `aceptable` |
| P-VX-19 | las ocho clases (§4.1 de CV) | nueve mutaciones, una por subtipo, sobre el Bundle exacto de B01 | exactamente el subtipo previsto, uno por mutación | ocho mutaciones de forma (orden de entries, `id`, `meta`, `text`, extensión, `display`, `Bundle.type`, `patient` lógico) → 0 cuentan y 8 notas |
| P-VX-20 | MCP y esquema | `verificar_caso` con `punto_entrada = vxu_conv` pasa el esquema; `consultar_tabla("perfil_guia_vxu")` devuelve filas con `nivel` y `citas`; `info_verificador.puntos_entrada` ∋ `vxu_conv`; `_no_evaluado` lleva la línea de conversión | sin error | `vxu_conv` con `conversion` ausente → error de esquema; `consultar_tabla("perfil_guia_adt")` devuelve exactamente las 21 filas de hoy |
| P-VX-21 | herramienta (§6) | `punto` de VXU → `vxu_conv`; `generar_corpus(lab=True)`: `por_corpus["adt"]`, `["oru"]` y `huella_adt_oru_muestras` iguales a las de hoy (valores fijados en la prueba); `n["vxu"] = 40`; juguete `JUGUETE-NOMINAL` VXU → `correcto` | según | `punto` de ADT/ORU/SIU como en `prueba_vc.p07`; `JUGUETE-RUTA` → `fallo_silencioso`, `[("fidelidad", "codigo_mal_mapeado", "RXR-1")]` |
| P-VX-22 | **ADT y ORU no cambian** | (a) `prueba_conversion.py` (28) y todas las suites de hoy en verde **sin editar**; (b) `cv/rejuicio.py`: cada evidencia del corpus del estudio (A1 263, E2 216, ORU 40, muestras) juzgada con el juez nuevo da `veredicto` y `hallazgos` (`clase, subtipo, hecho, cuenta, que, citas`) **byte a byte iguales** a los sellados; (c) `INFORME.json` de cada conversor idéntico salvo `juez.huella/revision` | 0 diferencias | una línea cambiada a propósito en `_patient` hace fallar (b): la prueba de que el rejuicio ve |
| P-VX-23 | corpus (§4) | `bases_vxu.autoprueba`: 40 bases, ids B01..B40, todas leídas y con estructura `VXU_V04`, TS/NM/tablas válidos, `firma` ≥ 3 en todo par, `cobertura` completa, sha256 del conjunto fijo, sin nombres reales (lista cerrada de apellidos sintéticos) | TODO BIEN | una base duplicada con un solo campo distinto rompe `firma`; una fila «cuenta» sin base rompe `cobertura` |

Controles que no cambian: `prueba_verificador`, `prueba_adt`, `prueba_oru`, `prueba_multitipo`, `prueba_mutantes`, `prueba_conversion`,
`prueba_vc` (salvo el recuento declarado de `p06`), autopruebas, `prueba_mcp_verificador`; la regresión 2.721 y la concordancia A1: idénticas.

---

## 8. Las preguntas de diseño para Jev (Q-VX-D-n)

Solo las que no deciden ni la pregunta ni las condiciones. Estado neutro: cada fila da las opciones y qué cambia; **la recomendación va
aparte**, en §8.1.

| Q | Pregunta | Opciones | Qué cambia según la respuesta |
|---|---|---|---|
| Q-VX-D-1 | La uri de CVX y MVX no está en el paquete (la 0396 → uri tampoco, L-CV-3). ¿Se fija `http://hl7.org/fhir/sid/cvx` y `http://terminology.hl7.org/CodeSystem/MVX` como uris canónicas citadas fuera de la carpeta, igual que LN/SCT/UCUM, o el `system` de RXA-5/RXA-17 es convención? | (a) fijar en `URI_SISTEMA` con cita externa y L-VX-4; (b) convención | si (a), un `system` distinto en `vaccineCode`/`manufacturer.identifier` es `codigo_mal_mapeado` (MC-VX-13 cuenta); si (b), solo cuenta el código |
| Q-VX-D-2 | RXR-2: el mapa de segmento apunta a la 0550, la tabla de atributos de 2.5 a la 0163 y el texto admite ambas. ¿Qué system espera el juez para un código de la 0163? | (a) `{v2-0163, código}` o `{v2-0550, código}` según la tabla donde esté el código (AMB-VX-2); (b) solo v2-0550 (literal del mapa de segmento); (c) solo v2-0163 (literal de la tabla de atributos de 2.5) | con (b), `LD` (que no está en la 0550) no tiene esperado → la hoja no se juzga; con (c), `{v2-0550, DELT}` (B27) cuenta; con (a) cuentan las dos identidades |
| Q-VX-D-3 | `recorded`: ORC-9 sin condición y RXA-22 «IF RXA-21 EQUALS "A"» mandan al mismo elemento. ¿Conjunto admitido o precedencia? | (a) conjunto {ORC-9} ∪ {RXA-22 si A} (AMB-VX-3); (b) ORC-9 manda; RXA-22 solo si ORC-9 vacío y A; (c) RXA-22 manda si A; ORC-9 solo si RXA-22 vacío | B13 (ambos valorados y distintos): con (a) 0 hallazgos; con (b)/(c) uno de los dos conversores puede sumar `valor_distinto` |
| Q-VX-D-4 | Un OBX del grupo ORDER sin Observation pero con su valor en un elemento de la Immunization (`programEligibility`, `fundingSource`, `education`…): la Narrative-Condition lo deja a las IG. ¿Convención o `recurso_ausente`? | (a) convención (nota `absorbido`, AMB-VX-4); (b) `recurso_ausente` (literal de la fila `Observation[2]`) | B30-B32 y los VXU públicos de CDC: con (b) cada OBX absorbido es un hallazgo que cuenta |
| Q-VX-D-5 | ¿Entran NK1 y PD1 en el perfil? | (a) NK1 con perfil reducido (§1.4, §3.3) y PD1 fuera (nota); (b) ninguno (solo Patient e Immunization); (c) los dos (PD1-3/4 → `generalPractitioner` cuenta) | el número de filas del perfil (y de pruebas); MC-VX-14 entra o sale; con (c) hace falta XON → Organization y XCN → Practitioner en `generalPractitioner` |
| Q-VX-D-6 | `performer.function` ausente con RXA-10/ORC-12 valorados: la guía la fija (AP/OP) pero el binding es `extensible`. ¿`dato_perdido` o convención? | (a) `dato_perdido` (siempre); (b) convención cuando hay un solo performer, `dato_perdido` cuando hay dos (RXA-10 y ORC-12) y no se distinguen; (c) convención | MC-VX-5: cuántos hallazgos cuentan en B04/B21/B23 y en todas las bases con RXA-10 |
| Q-VX-D-7 | `primarySource`/`isSubpotent` escritos por omisión (`true`/`false`) sin campo que los sostenga: ¿`dato_inventado` (regla de §3.0, como Q-CV-D-3) o convención? | (a) `dato_inventado`; (b) convención | MC-VX-17 entra o sale de lo que cuenta; afecta a todas las bases |
| Q-VX-D-8 | RXA-15 repetido (lote de la vacuna y del diluyente) mapeado a `lotNumber` 0..1: ¿cuál espera el juez? | (a) la primera repetición (literal 0..1, AMB-VX-7); (b) cualquiera de las repeticiones; (c) convención (las dos, concatenadas o una) | B16: con (a) `DIL-B` es `valor_distinto`; con (b)/(c) no |
| Q-VX-D-9 | Con PV1 y un Encounter presentes, `Immunization.encounter` ausente: la hoja no tiene fila de referencia. ¿Convención o `dato_perdido`? | (a) convención (AMB-VX-5); (b) `dato_perdido` PV1-19 | B38 |
| Q-VX-D-10 | Los OBX del grupo ORDER: ¿se juzgan con todas las reglas de `oru_conv` (status, code, value, unidades, interpretación) o solo existencia, `subject` y `partOf`? | (a) todas (reutilizando `_observacion`); (b) solo existencia y referencias | la profundidad de B30-B32; con (a) MC-ORU-1..4 pueden reaparecer en VXU |

### 8.1 Mi recomendación (aparte, para que el estado de Jev sea neutro)

| Q | Recomiendo | Por qué |
|---|---|---|
| Q-VX-D-1 | **(a) fijar**, con L-VX-4 | es la misma decisión ya tomada para LN/SCT/UCUM (L-CV-3); el texto de 2.5 exige el nombre `CVX`/`MVX` y FHIR R4 publica una uri canónica para cada uno; un `system` propio cambia el significado del código |
| Q-VX-D-2 | **(a) las dos tablas** | el texto de 2.5 admite las dos (`[E4 9350-9352]`) y el paquete trae un ConceptMap de identidad para cada una; escoger una sola sería imponer una lectura que el estándar no impone |
| Q-VX-D-3 | **(a) conjunto** | las dos fechas son «fecha de registro» en el origen (`[E4 2597-2599; 11454-11457]`); elegir una no cambia el significado del dato |
| Q-VX-D-4 | **(a) convención** | la propia guía dice que algunos OBX van a elementos de la Immunization y pospone la regla; contar un `recurso_ausente` ahí es contar lo que la guía no decide |
| Q-VX-D-5 | **(a) NK1 sí, PD1 no** | el VXU típico lleva NK1 (el padre/madre del niño) y el mapa de la 0063 es de los que un conversor por plantilla suele hacer literal; PD1 en VXU es casi siempre el estado de registro (PD1-16), que la guía no mapea |
| Q-VX-D-6 | **(b)** | con un solo performer el papel se deduce; con dos, perder AP/OP es perder quién administró y quién ordenó |
| Q-VX-D-7 | **(a) `dato_inventado`** | mismo criterio que Jev dio a `gender unknown` (Q-CV-D-3): el mensaje no lo dijo |
| Q-VX-D-8 | **(a) la primera** | es la literal (0..1) y el texto de 2.5 dice que se informe el lote de la sustancia, no el del diluyente (`[E4 11379-11383]`) |
| Q-VX-D-9 | **(a) convención** | la hoja no da la referencia; FHIR la deja 0..1 |
| Q-VX-D-10 | **(a) todas** | cuesta cero (se reutiliza) y es donde ORU ya encontró diferencias |

Sensibilidad preinscrita (como `decisiones-qcv.md:32-34`): las Q que Jev deje con confianza ≤ 0,52 entran en `ALTERNATIVA_VX` y VX2 da también
la N con la alternativa de cada una (`con_alternativas`, `conversion.py:1607-1609`, extendido a `CVX.ALTERNATIVA`).

---

## 9. Límites (L-VX-n) y lecturas adoptadas (AMB-VX-n)

### 9.1 L-VX-n (para `info_verificador.limites`)

| L | Redacción |
|---|---|
| L-VX-1 | «En v2.5 el lugar de administración es RXA-11 (LA2) y la guía no lo mapea; la guía mapea RXA-27/28, que no existen en v2.5. `Immunization.location` nunca cuenta en `vxu_conv`: con RXA-11 valorado es nota `fuera_proyeccion`, sin él nota `extra`.» |
| L-VX-2 | «ORC-28 → `meta.security` tiene ConceptMap (0177), pero `meta` es forma (L-CV-9): no se juzga.» |
| L-VX-3 | «PD1 queda fuera del perfil: PD1-3/4 → `generalPractitioner`, PD1-6/14 → extensiones y PD1-7 → Observation son nota; PD1-16/17 (estado en el registro de vacunas) no tienen fila en la guía.» (revisable por Q-VX-D-5) |
| L-VX-4 | «La pertenencia de RXA-5 al CVX (0292) y de RXA-17 al MVX (0227) no se juzga: son conjuntos externos de los que v2.5 trae una instantánea de 2002; un código fuera no es imposible. La uri de ambos no está en el paquete: se fija por Q-VX-D-1 con cita externa a R4, como L-CV-3, o es convención.» |
| L-VX-5 | «TQ1/TQ2 (grupo TIMING de 2.5) no tienen fila; PRT no existe en 2.5 y las filas de la hoja que mapean PRT → PractitionerRole no se usan. El juez no deduce performers de ningún otro segmento.» |
| L-VX-6 | «Un OBX del grupo ORDER absorbido en un elemento de la Immunization (AMB-VX-4) solo se comprueba por la presencia de su valor; qué elemento le corresponde lo deja la guía a las IG y no se juzga.» |
| L-VX-7 | «NTE bajo OBX → `Observation.note`: solo presencia (nota), como L-ORU-4; el texto no se compara.» |
| L-VX-8 | «El Encounter de un VXU es opcional en la guía; su `status` se decide solo por PV1-2/PV1-45 (V04 no está en la 0003). Ausente no cuenta; presente se juzga con las reglas de `adt_conv`.» |
| L-VX-9 | «Los VXU públicos son en su mayoría 2.5.1 con la guía de implementación de los CDC: sus reglas (RXA-9 → reportOrigin, OBX a elementos de Immunization, códigos de la 0322 ampliados, NIP/PHVS) no entran; se juzgan contra la guía base con banderas L18 y las absorciones de AMB-VX-4 son convención.» |
| L-VX-10 | «GT1, IN1/IN2/IN3, SFT, PV2 y los OBX fuera de ORDER solo se cuentan (`otros_tipos`, `obx_fuera_orden`); su contenido no se compara.» |
| L-VX-11 | «NK1 se empareja por apellido (o por NK1-33/NK1-12): dos NK1 con el mismo apellido y sin identificador dan `indeterminado/emparejamiento`.» |
| L-VX-12 | «RXA-15/16/17/18 repiten en 2.5 y la guía los lleva a elementos 0..1: solo se juzga la primera repetición (Q-VX-D-8); las demás son nota.» |
| L-VX-13 | «El juez no sabe si un conversor aplicó una plantilla de VXU o una genérica: un `error` por falta de plantilla es `sin_plantilla` (L-VC-13) y cuenta como «no corre VXU» en E-VX-3, no como `rechazo_incorrecto`.» |

### 9.2 Índice de lecturas adoptadas AMB-VX-n (para `info_verificador.ambiguedades`; cada una con su alternativa)

| AMB | Enunciado | Lectura adoptada | Alternativa |
|---|---|---|---|
| AMB-VX-1 | ORC-4 es EI en 2.5 y la guía lo mapea como EIP (identifier[3]/[4] por EIP.1/EIP.2) | nota; un identifier con ORC-4.1 es convención | identifier con `type PGN` (EIP.1 ≈ EI.1): cuenta |
| AMB-VX-2 | RXR-2: 0550 (mapa de segmento, texto de 2.5) frente a 0163 (tabla de atributos de 2.5, texto «for backward compatibility») | identidad con el system de la tabla donde esté el código | solo v2-0550 / solo v2-0163 (Q-VX-D-2) |
| AMB-VX-3 | ORC-9 y RXA-22 (IF A) → `recorded` | conjunto admitido | precedencia (Q-VX-D-3) |
| AMB-VX-4 | OBX de ORDER: Observation[2] con `partOf`, o elemento de Immunization según la IG (Narrative-Condition); la condición de la fila lleva AND donde PERSON_OBSERVATION lleva OR | una Observation por OBX; absorbido con el valor presente → convención | `recurso_ausente` literal (Q-VX-D-4) |
| AMB-VX-5 | `Immunization.encounter`: sin fila de referencia; Encounter opcional | ausente: convención; presente: debe resolver | `dato_perdido` (Q-VX-D-9) |
| AMB-VX-6 | NK1 → RelatedPerson o Patient.contact o ambos | una de las dos formas; las dos: nota | solo RelatedPerson (el mapa con `patient.reference`) |
| AMB-VX-7 | RXA-15/16/17/18 repetibles → 0..1 | la primera repetición | cualquiera (Q-VX-D-8) |
| AMB-VX-8 | ORC-12 → PractitionerRole; RXA-10 → Practitioner; `performer.actor` admite ambos | el tipo del actor es forma; se recorre `PractitionerRole.practitioner` | tipo literal (PractitionerRole para OP) cuenta |
| AMB-VX-9 | RXA-9 → (CDC) `reportOrigin`, «we leave this for implementation guides» | `reportOrigin` con RXA-9: convención; sin RXA-9: `dato_inventado` | `reportOrigin` siempre nota |
| AMB-VX-10 | el mapa XCN → PractitionerRole no tiene fila para XCN.2 | el apellido se juzga por el mapa XCN → Practitioner (es el mismo Practitioner) | no juzgar `family` en ORC-12 |
| AMB-VX-11 | RXA-20 y RXA-21 vacíos | `completed` («IF NOT VALUED AND RXA-21 NOT EQUALS "D"» se cumple con RXA-21 vacío) | sin esperado |
| AMB-VX-12 | RXA sin ORC delante (ORC es R en ORDER) | el grupo existe y se espera su Immunization; nota `estructura` | no esperar Immunization (la guía la crea desde ORC) |

---

## 10. El plan: VX1 y VX2 (y lo que sigue), con «hecho cuando» y regla de parada

Tope de la etapa: cuatro sesiones y antes del 20-nov (`ANTES-ETAPA-VXU.md:92-95`); VX-pre y VX0 gastan parte de la primera. Reparto propuesto:
**VX1 ≈ 1,5 sesiones, VX2 ≈ 1, VX3 ≈ 1, VX4 ≈ 0,5**. Primero lo que puede tumbarlo: la gramática y E-VX-3.

| Fase | Qué, en orden | Hecho cuando | Parada |
|---|---|---|---|
| **VX1-a** la gramática y E-VX-3 (≤ 1,5 h) | (1) extraer `VXU_V04` a `estructuras_25.json` desde `[E4 12366-12421]` con el extractor del laboratorio y afirmar que `_afirmar` pasa y que `_tipos("ADT")`/`("ORU")` no cambian; (2) correr un VXU nominal (B01) por cada conversor en la caja de siempre (versiones del estudio), guardar `conversion.salida` tal cual, solo para el informe de E-VX-3 (¿Bundle?, `type`, ¿`urn:uuid`?, ¿`contained`?, ¿Immunization?), nunca para tocar el perfil | la gramática está y las suites de hoy siguen en verde; los dos conversores contestados con su salida guardada | el extractor no reproduce §4.17.6 → se escribe a mano desde el texto con su cita y DV-VX; **ningún conversor corre VXU → la etapa para** (`ANTES:67`); uno solo → sigue con uno y K ≤ 1 |
| **VX1-b** pruebas en rojo | P-VX-1..23 escritas y en rojo por la razón prevista; `prueba_conversion_vxu.py rojo` sale 0; P-VX-22 (rejuicio) en verde con el juez de hoy (es la línea base) | cada prueba falla donde debe; el rejuicio da 0 con el juez actual | una prueba que no se puede poner en rojo = pieza no definida: vuelve a este diseño como Q-VX-D |
| **VX1-c** las decisiones de Jev | Q-VX-D-1..10 con estado neutro (§8), sin §8.1; `DECISIONES_VX` y `ALTERNATIVA_VX` en `conversion_vxu.py` | las diez contestadas con confianza | — |
| **VX1-d** código | PE `vxu_conv` → `conversion_vxu` (grupos, emparejar, perfil, juzgar) → cinco ganchos en `conversion.py` → `MAPAS` de VXU → esquema, MCP (`perfil_guia_vxu`, descripción), `info_verificador` → `punto()`, `CORPUS`, juguete | P-VX-1..21, 23 en verde; todas las suites de hoy en verde sin ningún cambio salvo los declarados (enum del esquema, textos de `info_verificador`/`REVISION`, recuento de `prueba_vc.p06`) | cualquier rojo no declarado |
| **VX1-e** el rejuicio y el primer Bundle real | P-VX-22: corpus del estudio (A1, E2, ORU, muestras) con el juez nuevo = sellados, **0 diferencias**; las dos salidas de VX1-a pasan por `leer_bundle`/`emparejar` sin `indeterminado` (sin perfil todavía) | 0 diferencias; emparejamiento `identifier`/`codigo+fecha` sin ambiguos | una diferencia en ADT/ORU → se deshace el gancho que la causó antes de seguir; un `indeterminado/emparejamiento` → se corrige el emparejador con la salida como cita (DV-VX), nunca el perfil |
| **VX2-a** el corpus | `bases_vxu.py` con las 40 de §4.2; `--firma`, `--cobertura`, `--autoprueba` en verde; `generar_corpus` escribe `vxu/` con su huella y deja `adt`/`oru` intactas (P-VX-21) | 40 bases válidas, firma ≥ 3, cobertura completa, huella sellada | una fila «cuenta» sin base → se escribe la base, no se baja la fila |
| **VX2-b** la previsión sellada | §5 completada con las cuentas (n de bases por mecanismo, lo visto en E-VX-3) y sellada con la huella del juez y del corpus **antes** de juzgar | `prevision-vxu.json` sellado | — |
| **VX2-c** las corridas y el juicio | los dos conversores sobre las 40 bases (y las muestras públicas de E-VX-2 con banderas L18) con `verificar_conversor.py`; tabla por conversor × categoría × mecanismo; «fuera de previsto» adjudicado con cita | 0 fuera de previsto sin adjudicar | un defecto del juez se arregla con su prueba y VX2-c se repite entero; **dos repeticiones como máximo**; luego el mecanismo pasa a L-VX y se declara |
| **VX3** contraste y clase | por mecanismo: salidas esperadas y pruebas publicadas del proyecto; sus issues (con red, fuera de la caja, Q-CV-A-5); relectura del ConceptMap y la hoja → `clase_cv` por la regla de CV §4.3; pares mínimos de VXU en `cv3_minimos_vxu`; revisión adversaria | cada mecanismo con clase y referencia; cada `nueva` con par mínimo y cita completa | un mecanismo sin clasificar en 30 min → Q-VX-D, no cuenta como nueva; ≤ 2 rejuicios por correcciones del perfil (DV-VX) |
| **VX4** cierre | `RESULTADO-VXU.md` con la frase fija (`ANTES:88-89`), o el resultado negativo con su frase (`ANTES:99-100`); MCP con S-VX/L-VX/AMB-VX/DV-VX; suites; guarda en LIMPIO; opción B | todo lo anterior | guarda no LIMPIO → no se publica |

---

## 11. Los tres riesgos que más me preocupan

1. **La gramática que no está.** Todo lo demás supone que `estructuras_25.json` tiene `VXU_V04`; hoy no la tiene. Si el extractor del
   laboratorio no lee §4.17.6 tal cual (la tabla tiene el grupo TIMING anidado y el PATIENT con PV2), hay que escribirla a mano con su cita y
   declararlo. Es la primera hora de VX1 y la primera parada posible. Nivel: medio-alto, pero barato de medir.
2. **El emparejamiento de Immunization sin identificadores.** Con ORC-3 presente es trivial; sin él (B35) y con varias RXA del mismo código
   (B34), el juez solo tiene `vaccineCode` + `occurrenceDateTime`, y si el conversor ya se equivoca en la fecha, el emparejamiento falla antes
   de poder contar la fecha. Por eso VX1-e pasa el primer Bundle real por el emparejador antes del perfil, y B33 (con identificadores) va antes
   que B35 en la lectura de resultados. Nivel: alto.
3. **El perfil que cuenta de más donde la guía calla.** VXU tiene más silencios que ADT/ORU (RXA-11, RXA-9, PD1-16, los OBX «de la IG», la
   0163/0550, el `recorded` doble). Cada uno está escrito como AMB-VX o Q-VX-D con su alternativa; si en VX3 hay que bajar más de dos
   mecanismos a convención, la N queda inflada o el tope no llega. Nivel: medio-alto.

---

## Resumen (≤ 15 líneas)

1. Secciones: 0 decisiones S-VX-1..14; 1 E-VX-1 (RXA, RXR, ORC, PID, PD1, NK1, sin cita y ambiguas); 2 `vxu_conv`; 3 perfil «guía»; 4 corpus; 5 previsión; 6 herramienta; 7 P-VX; 8 Q-VX-D; 9 L-VX y AMB-VX; 10 plan; 11 riesgos.
2. E-VX-1: los 20 campos que la guía lleva a Immunization tienen fila y ConceptMap; RXA-3/5/20 con cita doble: la etapa no para. Sin cita: RXA-11 (lugar), RXA-9 (notas), PD1-16; ambiguas: RXR-2 (0163/0550), ORC-4 (EI/EIP), ORC-9 + RXA-22, uri de CVX/MVX, condición de los OBX de ORDER.
3. Punto `vxu_conv`: hermano de `adt_conv`/`oru_conv` con `familia = "vxu"`; misma evidencia y veredicto; una Immunization por grupo ORDER emparejada por ORC-3/ORC-2, código+fecha, orden; Observation por OBX con `partOf`; RelatedPerson o Patient.contact por NK1; Encounter opcional; cinco ganchos en `conversion.py` y un módulo nuevo; **la gramática `VXU_V04` hay que extraerla primero**.
4. Perfil: `status` por RXA-21/RXA-20 y la 0322; `route` por la 0162 en dos grupos (IM → v3 IM); `site` por 0163 o 0550; performers AP/OP con actor resuelto; `manufacturer` como Organization con MVX y nombre; `doseQuantity` por RXA-6/7; fechas y decimales con las reglas de CV; `recorded` como conjunto.
5. Corpus: 40 bases válidas en v2.5 desde §4.17.6/§4.18, una por rama de la guía, ocho de control, con una regla medible contra la firma (≥ 3 campos distintos en todo par) y cobertura afirmada; los imposibles solo en P-VX.
6. Previsión: ambos corren 0,85; `fallo_silencioso` 55-90 %; 4-8 mecanismos por conversor (ruta v2-0162, decimal, unidades, fabricante sin MVX, function AP/OP, caducidad YYYYMM, status vacío/PA/D, OBX sin partOf, NK1 v2-0063, primarySource por omisión); ≥ 1 nueva en alguno 0,85.
7. Herramienta: `punto()` añade VXU → `vxu_conv` sin tocar ORU/ADT; corpus `vxu` con las huellas de `adt`/`oru` intactas; juguete con nominal VXU.
8. P-VX-1..23 con control negativo; P-VX-22 es el rejuicio byte a byte de ADT y ORU (0 diferencias) y las 28 pruebas de CV sin editar.
9. **10 Q-VX-D** (uri CVX/MVX, 0163/0550, recorded, OBX absorbidos, NK1/PD1, function, primarySource, lote repetido, encounter, profundidad de OBX) con recomendación aparte; 13 L-VX; 12 AMB-VX.
10. Plan: VX1 gramática + E-VX-3 (≤ 1,5 h, parada si ninguno corre) → rojo → Jev → código → rejuicio 0; VX2 corpus → previsión sellada → corridas (≤ 2 repeticiones); VX3 contraste; VX4 cierre con la frase, opción B.
11. Riesgos: la gramática ausente, el emparejamiento sin identificadores y el perfil que cuenta de más donde la guía calla.
