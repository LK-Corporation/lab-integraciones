<!-- modelo: Claude Sonnet 5.5 (claude-sonnet-5-5); fecha: 31-oct-2026; «MD0: el juez de conversiones ante MDM_T02 (etapa 26); diseño a ciegas de lo que devuelven los conversores; leído solo la carpeta md0» -->

# Diseño MD0: el punto `mdm_conv`, el perfil «guía» de DocumentReference y el corpus sintético de MDM_T02

Documento público. Sin credenciales, sin nombres de máquinas ni de personas, sin datos de pacientes (los ejemplos usan `DOC0001`,
`Prueba^Mateo`). Nombra los dos conversores del estudio (Microsoft FHIR-Converter y LinuxForHealth hl7v2-fhir-converter) y la guía HL7
v2-to-FHIR (ConceptMap del paquete 1.0.0; hojas CSV del commit `873b331`). **No sé qué devuelven los conversores con MDM_T02**: todo lo
que sigue sale del estándar v2.5 (caps. 2, 2A, 4, 7 y 9), de FHIR R4, de la guía y del juez tal como está en esta carpeta.

Convenciones (las de `resultados/diseno-vx-fable.md:10-16`): **S-MD-n** decisión propuesta (pasa a S-n cuando Jev decida); **R-MD-n**
regla del perfil; **P-MD-n** prueba en rojo antes del código, con su control negativo; **L-MD-n** límite declarado; **AMB-MD-n** lectura
adoptada donde la guía o el estándar admiten dos; **Q-MD-D-n** pregunta de diseño (Jev); **MC-MD-n** mecanismo previsto; **DV-MD-n**
queda reservada a quien implemente. Citas: `fichero:línea` dentro de esta carpeta; `[E2|E2A|E4|E7|E9 CHnn.txt:líneas]` para el texto de v2.5
(`E9` es el capítulo 9); `[G <hoja>.csv:línea]` para una hoja de la guía (**línea física del fichero**: en las hojas de segmento y de tipo de
dato las líneas 1-3 son cabecera, en la del mensaje las 1-2; una fila con celdas de varias líneas ocupa varias); `[CM <nombre> <origen> →
<destino>]` para un ConceptMap y su elemento; `[F <recurso>.<elemento> <fichero>:líneas]` para la StructureDefinition R4. Las S-n del
laboratorio no se citan en ningún hallazgo que cuente (`resultados/ANTES-ETAPA-CONVERSORES.md:45-48`).

Punto de partida fijado: la pregunta (`ANTES-ETAPA-MDM.md:6-10`), las condiciones (`:31-54`, y las siete del encargo,
`ENCARGO-MD0.md:24-36`), el eslabón débil y su regla de parada (`:56-70`), las fases (`:72-81`), el «hecho cuando» (`:83-93`), el tope
(`:95-98`) y la regla de resultado (`:100-105`).

**Lo que compruebo yo en la carpeta y condiciona el diseño:**

1. **La gramática ya está.** `estructuras_25.json` trae `MDM_T02` (`:4943-5051`: MSH, SFT, EVN, PID, PV1, COMMON_ORDER = ORC + TIMING + OBR + NTE,
   TXA, grupo `(OBX)` = OBX + NTE, obligatorio y repetible) y la 0354 lista `MDM_T02 → T02, T04, T06, T08, T10` (`:7022-7028`). A diferencia de
   VXU (`diseno-vx-fable.md:20-24`) no hay que extraerla. **Ya existe un punto `mdm` de acuse** (`verificador/puntos_entrada.py:103-110`, puerto
   2584, `_tipos("MDM")`, TXA-2, TXA-12 y TXA-17 consumidos): el nuevo se llama `mdm_conv` y el de hoy no se toca.
2. **El tipo de TXA-2 no es el de la guía.** En v2.5 TXA-2 es **IS** de la tabla **0270 definida por el usuario** y la lista es «suggested
   values» (`[E9 CH09.txt:824,863-884]`); la hoja de la guía lo llama CWE (`[G TXA_DocumentReference.csv:6]`). TXA llega a **TXA-23** en 2.5
   (`[E9 CH09.txt:820-846]`); la hoja trae hasta TXA-28 (`[G TXA_DocumentReference.csv:32-36]`).
3. **TXA-17 no tiene vocabulario y FHIR lo exige.** `docStatus` es `required` sobre `composition-status` = {preliminary, final, amended,
   entered-in-error} (`[F DocumentReference.docStatus documentreference.profile.json:631-639]`, `fhir_r4/codesystem-composition-status.json:49-68`);
   la 0271 son siete códigos distintos (DI, DO, IP, IN, PA, AU, LA: `[E9 CH09.txt:1492-1500]`) y la guía copia el valor (`[CM datatype-id-to-code
   $value]`: «the vocabulary mapping is done at the segment's field level») sin que el segmento lo haga (`[G TXA_DocumentReference.csv:23]`).
4. **En el mensaje MDM_T02 de la guía los OBX y los NTE de OBX no crean Observation: van dentro del `DocumentReference[1]` del TXA**
   (`[G MSG_MDM_T02.csv:29,34-35]`). Es lo contrario de ORU y de VXU.
5. **La hoja de OBX se contradice con R4.** Escribe `content[2].data`, `content[2].contentType`, `content[3].url`, `content[4].data`
   (`[G OBX_DocumentReference.csv:9-13]`): en R4 esos elementos no existen sin `.attachment` (`[F DocumentReference.content.attachment
   documentreference.profile.json:1525-1530]`, 1..1), y los números 1-4 son etiquetas por tipo (ED, FT, RP, TX), no posiciones.
6. **Los OBX que la guía no mapea son la mayoría de los tipos.** Solo ED, FT, RP y TX tienen fila (`[G OBX_DocumentReference.csv:8-13]`); el
   propio ejemplo del capítulo 9 usa CE y ST (`[E9 CH09.txt:1976-1980]`).
7. **El `DocumentReference` no se enlaza al Patient en ninguna fila de la guía**; R4 sí lo cruza con PID-3 (`[F DocumentReference.subject
   documentreference.profile.json:820-821]`).

---

## 0. Resumen de las decisiones que lo condicionan todo (S-MD-n)

| | Decisión | Por qué, en una línea (cita) |
|---|---|---|
| S-MD-1 | **Un punto de entrada nuevo, `mdm_conv`** (`familia = "mdm"`, `solo_transformacion = True`, puerto 0, `tipos = {"MDM": {"T02": "MDM_T02"}}`; T04/T06/T08/T10 según Q-MD-D-1), hermano de `adt_conv`/`oru_conv`/`vxu_conv`; el PE `mdm` de acuse y nada de lo que leen los otros cambia. | Misma técnica de S-CV-1/S-VX-1: el PE es el contrato como datos (`puntos_entrada.py:3-8,142-171`); condición 1 del encargo. |
| S-MD-2 | **La misma evidencia** `{mensaje, punto_entrada, conversion}`: solo se añade `mdm_conv` al enum. | Condición 4: mismas formas de evidencia y de veredicto (`esquema_evidencia.json:438-456`). |
| S-MD-3 | **Un `DocumentReference` por TXA con el contenido de todos sus OBX y NTE**, emparejado por TXA-12, luego TXA-16, TXA-2, único, orden; varios `DocumentReference` para un TXA son `recurso_duplicado` y su contenido se juzga en conjunto. | «Processing of the TXA… DocumentReference[1]»; OBX y NTE → `DocumentReference[1]` (`[G MSG_MDM_T02.csv:29,34-35]`); la estructura admite un TXA y un grupo OBX obligatorio (`[E9 CH09.txt:345-354]`). |
| S-MD-4 | **Las mismas ocho clases**, categorías y leyenda de CV: `correcto`, `fallo_silencioso` (`convertido`/`aceptado_imposible`), `rechazo_incorrecto`, `indeterminado`, `fuera_de_alcance`. | Condición 4; `conversion.py:1467-1475`. |
| S-MD-5 | **El contenido se juzga como vehículo, no como texto**: tipo de dato (OBX-2), codificación (ED.4), tipo MIME y que llegue entero. Texto (TX, FT, NTE): subsecuencia ordenada de «palabras» del original en el texto del `data` decodificado de Base64; binario (ED): igualdad de bytes tras decodificar la codificación, **sin interpretar** RTF, PDF ni CDA. | Condición 7 del encargo; `[E2A CH02A.txt:1846-1876]` (ED.4/ED.5), `[G ED_Attachment.csv:9]` («convert from A or HEX to binary64»). |
| S-MD-6 | **Los caminos de la hoja de OBX se leen como `content[].attachment.*`** y los índices 1-4 como etiquetas por tipo; el número de `content` y su orden son convención (AMB-MD-6, Q-MD-D-5). | `[G OBX_DocumentReference.csv:8-13]` contra `[F :1525-1530]`. |
| S-MD-7 | **Un `ServiceRequest` por grupo COMMON_ORDER**, con perfil reducido (existencia, `subject`, `identifier` PLAC/FILL, `code`, validez de `status` e `intent`), y la `DocumentReference` lo referencia en `context.related`. | «Processing of each ORC segment results in the creation of a new ServiceRequest» y `context.related.reference=ServiceRequest[1].id` (`[G MSG_MDM_T02.csv:20,29]`). |
| S-MD-8 | **Patient y Encounter con las reglas de ADT íntegras** (`CV._patient`, `CV._encounter`); el PV1 es 1..1 también en la guía de MDM_T02. | `[G MSG_MDM_T02.csv:13,15]` (cardinalidad 1,1 sin condición); `[E9 CH09.txt:319-321]`. |
| S-MD-9 | **TXA-17 → `docStatus` con un conjunto admitido**: el literal de la guía ∪ un mapa semántico 0271 → `composition-status` tomado de las definiciones de v2.5 y R4 (no de la guía). El tratamiento del literal es Q-MD-D-4. | `[G TXA_DocumentReference.csv:23]`, `[F :631-639]`, `[E9 CH09.txt:87-132,1492-1500]`. |
| S-MD-10 | **TXA-19 → `status`**: vacío y AV → `current`; CA, OB y UN → cualquier valor del ValueSet con el código conservado en `status.extension[alternate-codes]` (la **única** extensión que cuenta, L-MD-11). | `[G TXA_DocumentReference.csv:4,25-27]`, `[F :571-583]`; Q-MD-D-9. |
| S-MD-11 | **Profesionales**: TXA-9 → `author[]`, TXA-10 → `authenticator`; TXA-5 y TXA-11 no tienen destino. **Provenance, MessageHeader y el resto de recursos de la guía** quedan fuera del perfil (nota), como en L-CV-5. | `[G TXA_DocumentReference.csv:9,15-17]`; `[G TXA_Provenance.csv:8,15-16]` en blanco; Q-MD-D-2. |
| S-MD-12 | **Los OBX de tipo sin fila (CE, ST, NM, DT, TS…) y los NTE de OBR son nota**; un `Observation` en el Bundle es nota. | Sin destino en la hoja; condición 3 (toda regla que cuente lleva cita); Q-MD-D-8 y Q-MD-D-12. |
| S-MD-13 | **Eventos**: `mdm_conv` juzga MDM^T02; T01, T03, T05, T07, T09, T11 (estructura `MDM_T01`, sin OBX) son `fuera_de_alcance`; T04, T06, T08 y T10 comparten estructura y se deciden en Q-MD-D-1. | `ANTES-ETAPA-MDM.md:107-111`; `estructuras_25.json:7014-7028`. |
| S-MD-14 | **El corpus son 40 bases sintéticas válidas en v2.5**, escritas desde §9.5.2, §9.6.1 y los tipos ED/RP/TX/FT, una por rama de la guía, con una regla medible contra la firma mecánica (§5.1). | Condición 6 del encargo; `verificador/bases_vxu.py:3-9` como forma. |
| S-MD-15 | **La herramienta lleva MSH-9.1 = MDM a `mdm_conv`** y deja ORU → `oru_conv`, VXU → `vxu_conv` y lo demás → `adt_conv` igual; el corpus gana la carpeta `mdm`; `huella_adt_oru_muestras` no cambia. | `cv/verificar_conversor.py:395-400,416-469`; condición 1. |
| S-MD-16 | **La versión manda como en S-CV-6**: MSH-12 escrita; con MSH-12 ≠ 2.5 los ConceptMap cuentan y la legalidad de tabla o estructura de 2.5 no (L18). | `conversion.py:1407-1424`. |
| S-MD-17 | **Los campos que la guía mapea y 2.5 no tiene nunca cuentan**: TXA-24..28, NTE-5..9, OBX-20..33 y los segmentos UAC y CON. | Como L-VX-1: `[E9 CH09.txt:820-846]`, `[E2 CH02.txt:4860-4867]`, `[E9 CH09.txt:1920-1941]`. |
| — | **Lo que no cambia:** `conversion.py` en las ramas `adt`/`oru`/`vxu` (sus líneas no se editan: el gancho es una rama nueva al lado), `puntos_entrada.py` en sus PE, `verificador.verificar` (la línea `:264` ya despacha por `solo_transformacion`), los mapeadores, `conversion_vxu.py`, `prueba_conversion.py`, los RESULTADO sellados y la huella con que se juzgaron. | Condición 1 del encargo; `ANTES-ETAPA-MDM.md:41-44`. |

---

## 1. E-MD-1 completo: cada campo que llega a FHIR, con su cita

Leyenda de «Cuenta»: **cuenta** (una diferencia es hallazgo de una de las ocho clases; entre paréntesis la regla R-MD del §4), **convención**
(la guía o el estándar admiten más de una representación: el esperado es un conjunto), **nota** (no es dato proyectado:
`fuera_proyeccion`/`extra`), **—** (sin destino en la guía; nunca se juzga). «Esperado» resume la regla; la regla completa está en el §4.

### 1.1 TXA (23 campos en v2.5: `[E9 CH09.txt:820-846]`; la hoja trae 28)

| Campo (DT y opc. en 2.5; DT de la hoja) | Destino | Cita | Qué espera el juez | Cuenta |
|---|---|---|---|---|
| TXA-1 Set ID (SI R; SI) | — | `[G TXA_DocumentReference.csv:5]` sin atributo; `[E9 CH09.txt:850-853]` | nada | — |
| TXA-2 Document Type (**IS R**, 0270 user-defined; CWE) | `type` (0..1) | `[G TXA_DocumentReference.csv:6]`; `[CM segment-txa-to-documentreference TXA-2 → type]` (sin `mappedVia`); `[CM datatype-is-to-codeableconcept IS.1 → coding.code]` (el tipo de 2.5 es IS, no CWE: AMB-MD-1); `[E9 CH09.txt:863-884]`; `[F DocumentReference.type documentreference.profile.json:658-720]` (binding `preferred`, `:683-691`; mapa v2 «TXA-2», `:705-707`) | `type.coding[].code` ∋ TXA-2.1; el `system` es convención (la 0270 no tiene URI ni ConceptMap); `display`/`text` forma; un coding de más (p. ej. LOINC) es nota `extra`; sin TXA-2 y con `type` → `dato_inventado` | **cuenta** (R-MD-6) |
| TXA-3 Document Content Presentation (ID C, 0191; ID) | `content.attachment.contentType` | `[G TXA_DocumentReference.csv:7]`; `[CM … TXA-3 → content.attachment.contentType]`; `[E9 CH09.txt:886-903]` (0191: AP, AU, FT, IM, multipart, NS, SD, SI, TEXT, TX: **no son tipos MIME**); `[F DocumentReference.content.attachment :1554-1555]` («TXA-3 for mime type»); `[F Attachment.contentType attachment.profile.json:175-215]` (required, BCP-13) | convención (Q-MD-D-3): el literal o la familia MIME de la 0191 (`TEXT/TX/FT` → `text/*`, `AP` → `application/*`, `IM` → `image/*`, `AU` → `audio/*`, `multipart` → `multipart/*`); solo cuenta que, con TXA-3 valorado, **ningún** attachment lleve `contentType` | convención / **cuenta** la ausencia total (R-MD-14) |
| TXA-4 Activity Date/Time (TS O; DTM) | — | `[G TXA_DocumentReference.csv:8]`; `[G TXA_Provenance.csv:7]` en blanco | nada | — |
| TXA-5 Primary Activity Provider (XCN C Y) | — | `[G TXA_DocumentReference.csv:9]`; `[G TXA_Provenance.csv:8]` en blanco; `[E9 CH09.txt:1021-1023]` | nada; un Practitioner que solo viene de TXA-5 es `otros_tipos` | — |
| TXA-6 Origination Date/Time (TS O; DTM) | `date` (instant 0..1) **si lleva hora** | `[G TXA_DocumentReference.csv:10-12]`; `[CM … TXA-6 → date; «If time is included»]`; sin hora la guía usa una extensión de **R6** (`:11-12`), no disponible en R4; `[CM datatype-ts-to-datetime TS.1 → $value]`; `[F DocumentReference.date :841-884]` (`instant`, `:854-856`); `[E9 CH09.txt:1025-1028]` | con hora: `instant` (instante si hay zona); sin hora: `date` ausente (o completado, AMB-CV-9); sin TXA-6: `date` presente es nota si coincide con un TS del mensaje, si no `dato_inventado` (AMB-MD-17) | **cuenta** (R-MD-11) |
| TXA-7 Transcription Date/Time (TS C) | — | `[G TXA_DocumentReference.csv:13]`; `[E9 CH09.txt:1030-1035]` | nada | — |
| TXA-8 Edit Date/Time (TS O Y) | — en DocumentReference; `Provenance.recorded` | `[G TXA_DocumentReference.csv:14]`; `[G TXA_Provenance.csv:11]`; `[G MSG_MDM_T02.csv:30-31]` («a separate Provenance… for each edit date time») | Provenance fuera (Q-MD-D-2): nota | nota |
| TXA-9 Originator Code/Name (XCN O Y) | `author[]` (Practitioner, 0..*) | `[G TXA_DocumentReference.csv:15]`; `[CM … TXA-9 → author(Practitioner)]`; `[CM datatype-xcn-to-practitioner XCN.1 → identifier[1].value, XCN.2 → name.family, XCN.3 → name.given[1]]`; `[F DocumentReference.author :885-941]` (destinos `:899-904`); Provenance `agent[2]`, `[G TXA_Provenance.csv:12-14]` | un `author` por repetición con XCN.1 o XCN.2, que resuelva (recurso, `contained`, lógico, o vía `PractitionerRole.practitioner`) a un Practitioner con `identifier` ∋ XCN.1 y `family` = XCN.2 (FN.1), `given[1]` = XCN.3; solo `display` con XCN.1 valorado → `dato_perdido` | **cuenta** (R-MD-12) |
| TXA-10 Assigned Document Authenticator (XCN O Y) | `authenticator` (Practitioner, **0..1**) | `[G TXA_DocumentReference.csv:16]`; `[F DocumentReference.authenticator :942-999]` (destinos `:956-958`, mapa v2 «TXA-10», `:983-984`) | como TXA-9 para **una** repetición, cualquiera (AMB-MD-14, Q-MD-D-11); las demás nota | **cuenta** (R-MD-13) |
| TXA-11 Transcriptionist (XCN C Y) | — | `[G TXA_DocumentReference.csv:17]`; `[G TXA_Provenance.csv:16]` en blanco | nada | — |
| TXA-12 Unique Document Number (**EI R**) | `masterIdentifier` (0..1) | `[G TXA_DocumentReference.csv:18]` (`EI[Identifier-Organization]`); `[CM … TXA-12 → masterIdentifier]`; `[CM datatype-ei-organization-to-identifier EI.1 → value, EI.2 → assigner(Organization[1].identifier[1].value), EI.3 → …identifier[2].value, EI.4 → …identifier[2].type]`; `[F DocumentReference.masterIdentifier :443-498]` (mapa v2 «TXA-12», `:482-483`); `[E9 CH09.txt:1383-1402]` | `value` = EI.1 desescapado; si EI.2 o EI.3 valorados, `system` o `assigner` los contienen (la forma es convención, como CX.4 en CV §3.1) | **cuenta** (R-MD-3, R-MD-4) |
| TXA-13 Parent Document Number (EI C) | — (`relatesTo` existe en R4, `:1040-1277`, pero la guía no lo mapea) | `[G TXA_DocumentReference.csv:19]`; `[E9 CH09.txt:1404-1421]` (obligatorio en T05, T06, T09 y T10) | nada; un `relatesTo` es nota `fuera_proyeccion` (L-MD-4) | — |
| TXA-14 Placer Order Number (EI O Y), TXA-15 Filler Order Number (EI O) | — | `[G TXA_DocumentReference.csv:20-21]`; `[E9 CH09.txt:242-246,1423-1480]` («if valued in the ORC or OBR… the TXA… should be ignored») | nada; los números del pedido salen de ORC/OBR | — |
| TXA-16 Unique Document File Name (ST O) | `identifier[1]` | `[G TXA_DocumentReference.csv:22]` («Need to ensure that the full path is represented»); `[CM … TXA-16 → identifier[1]]`; `[CM datatype-st-to-identifier ST.1 → $value]`; `[F DocumentReference.identifier :499-544]` (mapa v2 «TXA-16?», `:532-533`) | un `identifier` con `value` = TXA-16 desescapado **entero** (la ruta completa; `\E\` → `\`); sin TXA-16 y con un identifier propio del conversor → nota `extra` | **cuenta** (R-MD-5) |
| TXA-17 Document Completion Status (**ID R**, 0271) | `docStatus` (0..1, `code`) | `[G TXA_DocumentReference.csv:23]`; `[CM … TXA-17 → docStatus]` (sin `mappedVia`); `[CM datatype-id-to-code $value]` («the vocabulary mapping is done at the segment's field level»); `[E9 CH09.txt:1487-1500]`; `[F DocumentReference.docStatus :606-656]` (binding **required** `composition-status`, `:631-639`; mapa v2 «TXA-17», `:649-651`); `[F codesystem-composition-status.json:49-68]` | **no hay valor unívoco** (AMB-MD-3, Q-MD-D-4): el literal de la guía, o un valor de `composition-status` coherente con la 0271 (mapa semántico del §4.5); ausente → `dato_perdido`; un valor válido incoherente (p. ej. `entered-in-error` para AU) → `valor_distinto` | **cuenta** con conjunto (R-MD-9) |
| TXA-18 Document Confidentiality Status (ID O, 0272) | `securityLabel[]` | `[G TXA_DocumentReference.csv:24]` (vocabulario «DocumentConfidentialityStatus»); `[CM … TXA-18 → securityLabel mappedVia table-hl70272-to-v2-0272]`; `[CM table-hl70272-to-v2-0272 V, R, U → v2-0272 (identidad)]`; `[E9 CH09.txt:1591-1602]`; `[F DocumentReference.securityLabel :1318-1377]` (binding **extensible** `security-labels`, `:1344-1356`, que incluye v3-Confidentiality, `valueset-security-labels.json:49`; mapa v2 «TXA-18», `:1362-1363`) | un `coding` con `code` = TXA-18 y `system` v2-0272 (guía) o v3-Confidentiality (R4, AMB-MD-20); otro código → `codigo_mal_mapeado`; ausente → `dato_perdido` | **cuenta** (R-MD-10) |
| TXA-19 Document Availability Status (ID O, 0273) | `status` (1..1, `code`) y `status.extension[alternate-codes]` | `[G TXA_DocumentReference.csv:4,25-27]`; `[CM … TXA-19 → status IF TXA-19 = "AV"; → status.extension[1] IF TXA-19 IN ("CA","OB","UN")]`; `[E9 CH09.txt:1604-1621]`; `[F DocumentReference.status :545-604]` (required, `:571-583`; mapa v2 «TXA-19», `:592-595`); `[F codesystem-document-reference-status.json:38-52]` | vacío o AV → `current`; CA, OB, UN → `status` válido cualquiera y el código en la extensión (AMB-MD-4, AMB-MD-5, Q-MD-D-9) | **cuenta** (R-MD-7, R-MD-8) |
| TXA-20 Document Storage Status (ID O, 0275) | — | `[G TXA_DocumentReference.csv:28]`; `[E9 CH09.txt:1658-1668]` | nada | — |
| TXA-21 Document Change Reason (ST C) | — (Provenance `reason.text`) | `[G TXA_DocumentReference.csv:29]`; `[G TXA_Provenance.csv:26]` | nota | nota |
| TXA-22 Authentication Person, Time Stamp (PPN C Y) | — | `[G TXA_DocumentReference.csv:30]`; `[G TXA_Provenance.csv:27]` | nada (la guía no lo lleva a `authenticator`; lo hace TXA-10) | — |
| TXA-23 Distributed Copies (XCN O Y) | — (Provenance `agent[1]`) | `[G TXA_DocumentReference.csv:31]`; `[G TXA_Provenance.csv:28-30]` | nota | nota |
| TXA-24..28 (**no existen en 2.5**) | `description` (TXA-25) y otros | `[G TXA_DocumentReference.csv:32-36]`; `[F DocumentReference.description :1278-1317]` (mapa v2 «TXA-25», `:1305-1306`) | nunca cuentan (S-MD-17, L-MD-4); `description` presente es nota `extra` | — |

### 1.2 OBX (19 campos en 2.5: `[E9 CH09.txt:1920-1941]`; la hoja trae 33)

Solo **OBX-2** (selector) y **OBX-5** llegan a `DocumentReference`. El resto de campos no tiene destino (`[G OBX_DocumentReference.csv:4-7,14-42]` sin
atributo FHIR): OBX-1, OBX-3 (CE en 2.5; CWE en la hoja), OBX-4, OBX-6..OBX-19 y los posteriores a 2.5 (OBX-20..33: S-MD-17). OBX-11 (R) tampoco
condiciona nada en la hoja.

| OBX-2 (tabla 0125, `[E7 CH07.txt:2603-2637]`) | Qué lleva OBX-5 | Destino (hoja y ConceptMap) | Cita | Qué espera el juez | Cuenta |
|---|---|---|---|---|---|
| **TX** | texto; la repetición separa párrafos (`[E2A CH02A.txt:5446-5453]`) | `content[].attachment.data` (base64) + `contentType = "application/text"`; cada repetición = un salto de línea dentro del `data` | `[G OBX_DocumentReference.csv:12-13]`; `[CM segment-obx-to-documentreference OBX-5 → content[4].data, content[4].contentType IF OBX-2="TX"]`; `[E7 CH07.txt:2643-2648]` | todas las «palabras» del texto desescapado, en orden, en el `data` decodificado (R-MD-18); entre repeticiones, LF o CR LF (R-MD-19); sin escapes de delimitador sin resolver (R-MD-20); `contentType` (R-MD-21, Q-MD-D-3) | **cuenta** |
| **FT** | texto con órdenes de formato `\.br\`, `\H\`… (`[E2 CH02.txt:1056-1095]`) | `content[].attachment.data` + `contentType = "text/hl7v2"` | `[G OBX_DocumentReference.csv:9-10]`; `[CM … OBX-5 → content[2].data, content[2].contentType IF OBX-2="FT"]`; `[E2A CH02A.txt:2154-2181]` | llegada sin las órdenes de formato (R-MD-22); escapes según el `contentType` (R-MD-23); `contentType` (R-MD-24) | **cuenta** |
| **ED** | `ED.1^ED.2^ED.3^ED.4^ED.5` (`[E2A CH02A.txt:1804-1876]`) | `content[].attachment`: ED.3 → `contentType`; ED.2 → `extension[alternate-codes]` **si ED.3 vacío**; ED.5 → `data` ("convert from A or HEX to binary64"); ED.1 y ED.4 sin destino propio | `[G OBX_DocumentReference.csv:8]`; `[G ED_Attachment.csv:5-9]`; `[CM datatype-ed-to-attachment ED.2/ED.3/ED.5]` | `data` = ED.5 (Base64) o su conversión a Base64 (A: ASCII; Hex: octetos) (R-MD-25, R-MD-26); `contentType` (R-MD-27); una `content` por repetición de OBX-5 (R-MD-28); un `Binary` referenciado es convención (R-MD-29) | **cuenta** |
| **RP** | `RP.1^RP.2^RP.3^RP.4` (`[E2A CH02A.txt:4384-4448]`) | `content[].attachment.url` (RP.1) y `contentType` = RP.3 «/» RP.4 | `[G OBX_DocumentReference.csv:11]`; `[G RP_Attachment.csv:4,6]`; `[CM datatype-rp-to-attachment RP.1 → url, RP.3 → contentType]` | `url` (R-MD-30), `contentType` (R-MD-31), una `content` por repetición (R-MD-32) | **cuenta** |
| AD, CE, CF, CK, CN, CP, CX, DT, MO, NM, PN, SN, ST, TM, TN, TS, XAD, XCN, XON, XPN, XTN | su valor | **sin fila** en la hoja ni en el ConceptMap | `[G OBX_DocumentReference.csv:8-13]`; el ejemplo del estándar usa CE y ST (`[E9 CH09.txt:1976-1980]`) | nada; nota (R-MD-35); Q-MD-D-12 si se quisiera contar su pérdida | nota |
| OBX-2 vacío o fuera de la 0125 | — | — | `[E7 CH07.txt:2573-2577]` | imposible en 2.5: el `error` del conversor es `rechazo_aceptable` | — |

### 1.3 NTE (4 campos en 2.5: `[E2 CH02.txt:4860-4867]`)

| Campo | Destino | Cita | Qué espera el juez | Cuenta |
|---|---|---|---|---|
| NTE-1, NTE-2 | — | `[G NTE_DocumentReference.csv:4-5]` | nada | — |
| NTE-3 Comment (FT O Y) **bajo un OBX** | `content[].attachment.data` (base64) con `contentType = "text/hl7v2"` | `[G NTE_DocumentReference.csv:6-7]`; `[CM segment-nte-to-documentreference NTE-3 → content[1].attachment.data; content[2].contentType]` (índices incoherentes: AMB-MD-13); `[G MSG_MDM_T02.csv:35]` | llegada del comentario (R-MD-33); su `contentType` sigue a R-MD-24 | **cuenta** |
| NTE-4 Comment Type (CE) | — | `[G NTE_DocumentReference.csv:8]` | nada | — |
| NTE-5..NTE-9 (**no existen en 2.5**) | NTE-9 → `content[2].attachment.data` | `[G NTE_DocumentReference.csv:9-14]` | nunca cuentan (S-MD-17) | — |
| NTE **bajo OBR** | `ServiceRequest.note.text` | `[G MSG_MDM_T02.csv:27]`; `[CM segment-nte-to-servicerequest NTE-3 → note.text]` | nota (R-MD-42) | nota |

### 1.4 PID, PV1, EVN, ORC, OBR y los demás segmentos

| Segmento | Entra | Cita | Qué espera el juez |
|---|---|---|---|
| **PID** → Patient | **sí**, íntegro | `[G MSG_MDM_T02.csv:13]`; `[G PID_Patient.csv:6-51]` | `CV._patient` sin cambios (`conversion.py:533-541`): PID-3, 5, 7, 8, 11, 13/14, 16, 29/30 con las decisiones de Jev (`resultados/decisiones-qcv.md:14-27`) — **cuenta** (R-MD-43) |
| **PV1** → Encounter | **sí**, íntegro | `[G MSG_MDM_T02.csv:15]` (1,1); `[G PV1_Encounter.csv]`; `[E9 CH09.txt:321]` | `CV._encounter` sin cambios (`conversion.py:882-905`), con la ausencia como en ADT (Q-CV-D-6) — **cuenta** (R-MD-44); `evento` T02 no está en la 0003, así que `status` sale de PV1-2/PV1-45 (L-VX-8) |
| EVN → Provenance[3] | no | `[G MSG_MDM_T02.csv:12]`; `[G EVN_Provenance.csv:4-13]`; EVN es «B, v2.5» y EVN-1 debe valer MSH-9.2 (`[E9 CH09.txt:214-216,319]`) | Provenance fuera (Q-MD-D-2): nota. EVN-1 = MSH-9.2 lo asegura el corpus |
| **ORC** → ServiceRequest | **sí, reducido** | `[G MSG_MDM_T02.csv:20]`; `[G ORC_ServiceRequest.csv:10-15]`; `[E4 CH04.txt:1820-1860]` | ORC-2 → `identifier` PLAC y ORC-3 → FILL **si OBR-2/OBR-3 no están valorados**; ORC-1 y ORC-5 → `status`/`intent` sin esperado propio («localized interpretation», `[G ORC_ServiceRequest.csv:4]`): solo validez (R-MD-41); ORC-4, 9, 12.. nota |
| **OBR** → ServiceRequest | **sí, reducido** | `[G MSG_MDM_T02.csv:26]`; `[G OBR_ServiceRequest.csv:4,6-13]`; `[E4 CH04.txt:3285-3343]` | OBR-2/OBR-3 → `identifier` PLAC/FILL (AMB-CV-8); OBR-4 (CE R) → `code`; el resto nota |
| TQ1/TQ2 | no | `[G MSG_MDM_T02.csv:23-24]` | nota |
| MSH, SFT | no (MessageHeader, Provenance, Device) | `[G MSG_MDM_T02.csv:3-10]` | `otros_tipos` (nota) |
| UAC, CON | **no existen en el MDM_T02 de 2.5** | `[G MSG_MDM_T02.csv:11,32]` contra `estructuras_25.json:4946-5049` | nunca cuentan (S-MD-17) |
| PV1-43/PV1-20 (Basic, Coverage), PV1 → Patient | no | `[G MSG_MDM_T02.csv:16-18]` | `otros_tipos` |

### 1.5 Campos sin cita o con cita ambigua

**Sin destino en la guía (nunca cuentan):** TXA-1, 4, 5, 7, 11, 13, 14, 15, 20, 22; OBX-1, 3, 4, 6..19; NTE-1, 2, 4; todos los segmentos de §1.4 salvo los que entran.
**Dato clínico sin sitio:** los **OBX de tipo CE, ST, NM, DT…** (el contenido estructurado de un documento, tal como el propio ejemplo del estándar), TXA-13
(documento padre), TXA-22 (autenticación), TXA-4/7/8 (fechas de actividad, transcripción y edición, salvo Provenance) y `DocumentReference.subject`/`context.encounter`
(no hay fila). Se declaran L-MD-2, L-MD-4 y L-MD-5: un conversor que los lleve a algún sitio recibe nota, nunca hallazgo.

**Con cita ambigua** (lectura adoptada en AMB-MD-n, §10.2):

| Campo | Ambigüedad |
|---|---|
| TXA-2 | IS en 2.5, CWE en la hoja; tabla user-defined sin URI; binding R4 `preferred` a LOINC (AMB-MD-1) |
| TXA-3 | valores de la 0191 que no son MIME, frente a `contentType` con binding `required` BCP-13 (AMB-MD-2, Q-MD-D-3) |
| TXA-17 | sin vocabulario en la guía; R4 `required` con otros cuatro códigos (AMB-MD-3, Q-MD-D-4) |
| TXA-19 | la fila «NOT VALUED → current» está en la hoja (`:4`) y no en el ConceptMap; CA, OB, UN no fijan `status` (AMB-MD-4); URL de `alternate-codes` con `http` en la hoja de TXA (`:26`) y con `https` en la de ED (`ED_Attachment.csv:5`) (AMB-MD-5) |
| OBX-5 | rutas sin `.attachment`, índices 1-4 por tipo, varios OBX del mismo tipo sin regla (AMB-MD-6, AMB-MD-7, Q-MD-D-5) |
| OBX-5 TX/FT | `application/text` y `text/hl7v2` no son tipos registrados; FT con órdenes de formato (AMB-MD-8, AMB-MD-9) |
| ED.3 | la hoja lleva solo el subtipo a `contentType` (AMB-MD-10) |
| RP.1 | «pointer» no es necesariamente una URL (AMB-MD-11) |
| ED.4 | la hoja solo nombra A y Hex; Base64 pasa tal cual (AMB-MD-12) |
| NTE-3 | índices `content[1]`/`content[2]` incoherentes (AMB-MD-13) |
| TXA-9/10 | XCN repetible frente a `author` 0..* y `authenticator` 0..1 (AMB-MD-14) |
| `subject` | sin fila en la guía; R4 lo cruza con PID-3 (AMB-MD-15, Q-MD-D-6) |
| `context.related` | `ServiceRequest[1]` con varios grupos (AMB-MD-16, Q-MD-D-7) |
| TXA-6 | `date` de R4 es la fecha de la referencia; sin hora la guía usa R6 (AMB-MD-17) |
| TXA-12 | `EI[Identifier-Organization]` sin `system` (AMB-MD-19) |
| TXA-18 | v2-0272 (guía) frente a v3-Confidentiality (binding extensible) (AMB-MD-20) |

**Respuesta a E-MD-1:** **sí, con cita, pero el valor esperado no es unívoco en tres de los cuatro campos de la regla de parada.**

- **TXA-12** (`masterIdentifier`): fila `[G TXA_DocumentReference.csv:18]`, ConceptMap y R4 (`:482-483`); valor unívoco (EI.1 → `value`).
- **TXA-2** (`type`): fila `[G …:6]` y ConceptMap; el juez espera `type.coding[].code` ∋ TXA-2.1 y **no** exige `system`, porque 0270 es user-defined, no hay ConceptMap de tabla ni URI y el tipo de 2.5 es IS. Cita del esperado: la fila, `datatype-is-to-codeableconcept`, `[F …:705-707]` y `[E9 CH09.txt:863-884]`.
- **TXA-17** (`docStatus`): fila `[G …:23]` y ConceptMap; **sin mapa de vocabulario**. El juez espera un conjunto: el literal de la guía o un valor de `composition-status` coherente con la 0271, con la cita doble `[CM datatype-id-to-code]`/`[F :631-639]` y las definiciones `[E9 CH09.txt:87-132]`/`[F codesystem-composition-status.json:49-68]`. Es la primera Q.
- **OBX-5** (`content`): fila `[G OBX_DocumentReference.csv:8-13]` y ConceptMap, pero solo para 4 tipos y con rutas y números que hay que leer (S-MD-6).

La regla de parada del ANTES (`:65-70`) **no se activa**: los cuatro campos tienen cita. Lo que no da la guía es el valor de TXA-17, el modelo de varios OBX, el tipo MIME de TX y FT y el destino de los OBX estructurados: se declaran, no se inventan.

---

## 2. El punto de entrada `mdm_conv`

### 2.1 Contrato y evidencia

```
PUNTOS["mdm_conv"] = _pe(
    "mdm_conv", 0, {"MDM": {"T02": "MDM_T02"}},                 # Q-MD-D-1 (b) añade "T04", "T06", "T08", "T10" -> "MDM_T02"
    MSH_CONSUMIDOS | {("PID", 3), ("PID", 5), ("PID", 7), ("PID", 8), ("PID", 11), ("PID", 13), ("PID", 14), ("PID", 16),
                      ("PID", 29), ("PID", 30),
                      ("PV1", 2), ("PV1", 3), ("PV1", 4), ("PV1", 6), ("PV1", 7), ("PV1", 8), ("PV1", 10), ("PV1", 11), ("PV1", 14),
                      ("PV1", 17), ("PV1", 19), ("PV1", 36), ("PV1", 44), ("PV1", 45),
                      ("ORC", 2), ("ORC", 3), ("OBR", 2), ("OBR", 3), ("OBR", 4),
                      ("TXA", 2), ("TXA", 3), ("TXA", 6), ("TXA", 9), ("TXA", 10), ("TXA", 12), ("TXA", 16), ("TXA", 17),
                      ("TXA", 18), ("TXA", 19), ("OBX", 2), ("OBX", 5), ("NTE", 3)},
    [("MSH", 10, "consumido"), ("PID", 3, "consumido"), ("PID", 5, "consumido"), ("TXA", 2, "consumido"), ("TXA", 12, "consumido"),
     ("TXA", 17, "consumido"), ("PV1", 2, "consumido"), ("MSH", 7, "estricto"), ("EVN", 2, "estricto"), ("OBX", 3, "estricto")],
    [("MSH", 7, "ts", "estricto"), ("MSH", 18, "0211", "estricto"), ("EVN", 1, "0003", "estricto"), ("EVN", 2, "ts", "estricto"),
     ("PID", 7, "ts", "consumido"), ("PID", 8, "0001", "consumido"), ("PID", 29, "ts", "consumido"), ("PID", 30, "0136", "consumido"),
     ("PV1", 2, "0004", "consumido"), ("PV1", 44, "ts", "consumido"), ("PV1", 45, "ts", "consumido"), ("TXA", 1, "nm", "estricto"),
     ("TXA", 3, "0191", "consumido"), ("TXA", 6, "ts", "consumido"), ("TXA", 17, "0271", "consumido"), ("TXA", 18, "0272", "consumido"),
     ("TXA", 19, "0273", "consumido"), ("OBX", 2, "0125", "consumido"), ("OBX", 11, "0085", "estricto")],
    "MDM^T02 convertido por un tercero (HL7 v2 -> FHIR): solo transformación, sin acuse; perfil «guía» de DocumentReference (S-MD-1..17).",
    solo_transformacion=True, familia="mdm")
```

- Va debajo de `vxu_conv` (`puntos_entrada.py:154-171`) y antes de `POR_OMISION` (`:172`). `p4` y `p5` se declaran por coherencia con `contrato()`
  (`:194-203`) y con `_longitudes` (`:45-56`, que toma lo que haya en `EH.CAMPOS`: `TXA-*` está porque el punto `mdm` de acuse ya los consume); en un
  PE de solo transformación no hay acuse (R-CV-2).
- **No hay gramática que extraer.** `_afirmar` (`:207-225`) exige que cada estructura aceptada esté en `EH.GRAMATICAS`: `MDM_T02` ya está
  (`estructuras_25.json:4943-5051`). Añadir el PE no toca `_tipos("MDM")` ni el punto `mdm` (P-MD-1 compara `contrato(PUNTOS["mdm"])` antes y después).
- Evidencia: la de S-CV-2 con `punto_entrada = "mdm_conv"`. `esquema_evidencia.json:442-454` y `E_PROPS["punto_entrada"]` (`mcp_verificador.py:1102-1111`,
  que lee `PE.NOMBRES`) ganan el valor; la descripción de `conversion` (`esquema_evidencia.json:438`) pasa a «adt_conv, oru_conv, vxu_conv o mdm_conv».

### 2.2 Qué recursos espera y cómo se emparejan

Lectura del mensaje (`grupos(m)`, hermana de `_grupos_oru` `conversion.py:254-269` y de `CVX.grupos` `conversion_vxu.py:160-184`): un ORC abre un
**grupo de orden** (le pertenecen el OBR, los NTE que lo siguen y, ignorados, TQ1/TQ2); un OBR sin ORC abre grupo con nota `estructura` (ORC es R
en 2.5, `[E4 CH04.txt:1823]`, y el estándar manda procesar lo que se entiende, `[E2 CH02.txt:932-938]`); un **TXA abre un documento** (le pertenecen
los OBX que le siguen y, a cada OBX, los NTE que le siguen); un segundo TXA es nota `estructura` (TXA es 1..1) pero abre otro documento, como pide el
encargo («un `DocumentReference` por TXA»); un OBX antes del primer TXA está fuera de la estructura y solo se cuenta (`obx_fuera_txa`).

| Papel esperado | Fuente v2 | Clave de emparejamiento (en este orden; cada clave para todos los papeles antes de la siguiente, como `conversion_vxu.py:259`; dos candidatos igual de buenos → `indeterminado/emparejamiento`) | Cita |
|---|---|---|---|
| `Patient#1` | PID | como CV §2.2 (`conversion.py:292-314`, común a todas las familias): único; `identifier.value` ∋ PID-3.1; referido por el Encounter | `[G MSG_MDM_T02.csv:13]` |
| `Encounter#1` | PV1 | como `CVX._emparejar_encounter` (`conversion_vxu.py:362-390`) pero **ausente cuenta** (S-MD-8): único; `subject` → Patient#1 e `identifier` = PV1-19.1; solo `subject`; solo `identifier`; si hay más → `recurso_duplicado` | `[G MSG_MDM_T02.csv:15]` |
| `DocumentReference#i` | TXA i | (1) `masterIdentifier.value` ∋ TXA-12.1 (o algún `identifier.value`) → `master`; (2) `identifier[].value` ∋ TXA-16 → `archivo`; (3) `type.coding.code` ∋ TXA-2.1 y única libre con ese tipo → `tipo`; (4) la única, o tantas como TXA → `unico`/`orden`; (5) ninguna → `recurso_ausente` (hecho `TXA(i)-12`). **Con un TXA y varias DocumentReference** se empareja la que lleva TXA-12; si ninguna o varias, la primera del Bundle (`orden`, nota `varias_candidatas`) y las demás son `recurso_duplicado` (hecho `TXA-12`), con su `content` sumado al de la emparejada para no contar dos veces (AMB-MD-18) | `[G MSG_MDM_T02.csv:29,34-35]`; `[E9 CH09.txt:345-354]` |
| `ServiceRequest#i` | grupo COMMON_ORDER i | (1) `identifier.value` = OBR-3.1/ORC-3.1 (FILL) u OBR-2.1/ORC-2.1 (PLAC) → `identifier`; (2) referido por `context.related` de la DocumentReference emparejada y con `code.coding.code` ∋ OBR-4.1 → `referencia`; (3) `code` ∋ OBR-4.1 y único entre los libres → `codigo`; (4) tantos como grupos → `orden`; (5) ninguno → `recurso_ausente` (hecho `ORC(i)-1`) | `[G MSG_MDM_T02.csv:20,26]` |
| Practitioner / PractitionerRole / Binary / Organization | TXA-9, TXA-10, `attachment.url`, `assigner` | solo por resolución desde la DocumentReference emparejada (`CV._alcanzadas`, `conversion.py:431-442`): recurso, `contained`, referencia lógica por `identifier` (convención) | `[F Bundle «Resolving references in Bundles» bundle.profile.json:803-806]` |

**Sobrantes:** una DocumentReference de más → `recurso_duplicado` (misma TXA) o `recurso_inventado` (sin TXA); un ServiceRequest de más →
`recurso_inventado`; un segundo Patient o Encounter → `recurso_duplicado`; **Observation, DiagnosticReport, MessageHeader, Provenance, Coverage, Basic,
Device, Organization, Practitioner y Binary no alcanzados → `otros_tipos` (nota)**, nunca `recurso_inventado` (S-MD-12, Q-MD-D-8).

### 2.3 Qué hace con lo que no cubre

| Caso | Qué hace el punto | Cuenta | Cita |
|---|---|---|---|
| MSH-9 ≠ MDM^T02 (MDM T01, T03, T05, T07, T09, T11; ACK; QRY^T12; ADT…) | `fuera_de_alcance`, como hoy (`conversion.py:1416-1420`) | no | `ANTES-ETAPA-MDM.md:107-111` |
| MDM^T04/T06/T08/T10 | `fuera_de_alcance` con Q-MD-D-1 (a); con (b), se juzgan con este perfil y nota `evento` (la semántica de cambio de estado no se juzga) | según Q | `estructuras_25.json:7022-7028`; `ANTES:107-111` |
| MSH-9.3 vacío o distinto de `MDM_T02` | se lee con la estructura del evento; nota `estructura_declarada` si difiere (nunca cuenta, L-CV-1) | no | AMB-MT-1; `conversion.py:1421-1424` |
| MSH-12 ≠ 2.5 | se juzga; lo que depende de una tabla o estructura de 2.5 (TXA-17 ∉ 0271, un segmento fuera de sitio) lleva certeza `ambiguedad L18` y no cuenta; los ConceptMap cuentan | parcial | S-CV-6; `conversion.py:127-133` |
| `salida.estado = error` con PID, PV1, TXA u OBX ausentes; o con un valor imposible (PID-7/8, TXA-6 DTM, TXA-3 ∉ 0191, TXA-17 ∉ 0271, TXA-18 ∉ 0272, TXA-19 ∉ 0273 —las cuatro tablas son HL7, solo en 2.5—, OBX-2 ∉ 0125, ED.4 ∉ 0299, ED.5 que no es Base64 o Hex válido para su ED.4, OBX-5 NM no numérico); o con TXA-2, TXA-12 o TXA-17 vacíos (son R) | `rechazo_aceptable` (nota; Q-CV-D-7) | no | `conversion.py:1425-1442`; `[E2 CH02.txt:932-938]`; `[E9 CH09.txt:823-839]` |
| `error` con un MDM_T02 que la guía convierte | `rechazo_incorrecto` (hecho: el campo que nombre el texto, si no `MSH-9`) | sí | CV §1.3 |
| Segmentos sin mapa (SFT, EVN, TQ1/TQ2, UAC, CON, Z…) o fuera de sitio | se ignoran al calcular el esperado; recuento; un `error` por ellos → `rechazo_incorrecto` | según | `[E2 CH02.txt:934-935]` |
| OBX antes del primer TXA | recuento `obx_fuera_txa`; una DocumentReference o contenido que le corresponda es nota | no | L-MD-9 |
| TXA sin OBX (el grupo OBX es obligatorio) | nota `estructura`; la DocumentReference se espera igualmente y su `content` no (R-MD-17 solo exige `content` si hay OBX con destino) | no | `[E9 CH09.txt:345-354]` |
| ORC sin OBR, OBR sin ORC | grupo con nota `estructura`; se espera su ServiceRequest | no | `[E9 CH09.txt:322-343]` |
| OBX-2 de un tipo sin fila (CE, ST, NM…) | nota `sin_destino`; recuento `obx_sin_destino` | no | R-MD-35, L-MD-2 |
| `salida.estado` = `vacio`/`sin_respuesta`, Bundle ilegible | `indeterminado/sin_salida`, `indeterminado/lectura` | no | L-CV-8; `conversion.py:1443-1450` |
| Elementos de DocumentReference sin fila en la guía (`category`, `custodian`, `relatesTo`, `context.*` salvo `related`/`encounter`, `content.format`) | valor único presente sin campo → `dato_inventado` (§3.0 de CV); repetible → nota `extra`; `description` presente → nota `extra` (TXA-25 no existe en 2.5, L-MD-4) | según | CV §3.0; `[F :1000-1317]` |

### 2.4 Qué recuentos lleva

`conversion.recuentos` (como `conversion.py:1454-1455`, con los tipos de la familia: `Patient`, `Encounter`, `DocumentReference`, `ServiceRequest`) y, nuevos
para esta familia (`CVM.recuentos(m, entries)`, que recibe también las entries para contar lo observado):
`txa`, `obx`, `obx_por_tipo` (`{"TX": n, "FT": n, "ED": n, "RP": n, "otros": n}`), `obx_sin_destino`, `obx_fuera_txa`, `repeticiones_obx5` (suma de repeticiones
de OBX-5 de tipo ED y RP), `nte_obx`, `nte_obr`, `grupos_orden`, `txa_por_completitud` (por TXA-17) y `txa_por_disponibilidad` (por TXA-19) y, del lado observado,
`content_observado` (nº de `content[]` de las DocumentReference emparejadas y duplicadas), `attachments_texto`, `attachments_binarios`, `attachments_con_url`.
`conversion.otros_tipos` como hoy. `emparejamiento` lista `rol`, `origen`, `fullUrl`, `emparejado_por`, `candidatos` por papel (`Patient#1`, `Encounter#1`,
`DocumentReference#i`, `ServiceRequest#i`). Todo determinista y sin datos personales: ni el texto del documento ni el Base64 entran en un recuento.

### 2.5 Categorías, hallazgos y veredicto

Sin cambio respecto a CV §1.4 (`conversion.py:1467-1475`): `fallo_silencioso/convertido` si cuenta algo de las clases de datos, `+aceptado_imposible` si cuenta un
`valor_imposible_aceptado`; `correcto` si nada cuenta. Hallazgos con la forma de `_h` (`conversion.py:115-119`), `origen = "conversion"`, `hecho` = el campo origen con su
ocurrencia (`TXA-17`, `OBX(2)-5` para el segundo OBX del mensaje, `ORC(2)-1` para el segundo grupo: `_hecho`, `conversion.py:1109-1111`), `citas` de §4.6 y `clase_cv = null`.
El `hecho` de un contenido es **el OBX** (`OBX(k)-5`, o `OBX(k)-2` para su tipo MIME), con `k` contado en todo el mensaje, como en ORU y VXU.

---

## 3. Dónde vive

- `verificador/puntos_entrada.py`: el bloque `PUNTOS["mdm_conv"]` de §2.1.
- `verificador/estructuras_25.json`: **nada** (`MDM_T02` y su 0354 ya están).
- `verificador/conversion_mdm.py` (nuevo, solo biblioteca estándar, más `base64`, `binascii`, `re`): `TIPOS = ("Patient", "Encounter", "DocumentReference", "ServiceRequest")`
  (a propósito **sin** Observation ni DiagnosticReport), `FALTAN = ("PID", "PV1", "TXA", "OBX")`, `DECISIONES_MD` y `ALTERNATIVA_MD`, `MAPAS_MDM` (0272 → v2-0272, el mapa 0271 →
  `composition-status`, el 0273), `C_MDM` y `C_SEG` (citas), `grupos(m)`, `imposibles(m)`, `recuentos(m, entries)`, `emparejar(m, entries, top, out, pat, rol, usados)`,
  `juzgar(J, m, lec, pat_entry)`, `_documento`, `_tipo`, `_estado`, `_doc_status`, `_etiqueta`, `_fecha_doc`, `_profesionales`, `_contenido` (con `_texto_esperado`,
  `_palabras`, `_decodifica`, `_ed`, `_rp`, `_nte`), `_servicio`, `PERFIL_GUIA_MDM`, `S_MD`, `L_MD`, `AMB_MD`, `INFO`, `autoprueba`. Reutiliza sin editar: `CV._fecha`, `CV._codigo`,
  `CV._sujeto`, `CV._patient`, `CV._encounter`, `CV.resolver`, `CV._alcanzadas`, `CV._reps/_comp/_sub/_t/_f/_d/_seg`, `CV._hecho`, `CV.Juicio`, `CV.mapa`. **Copia** (11 líneas) `CVX._persona`
  en vez de importarla: un cambio futuro de VXU no debe poder mover MDM (condición 1).
- `verificador/conversion.py`: **seis ganchos nuevos**, paralelos a los de VXU, cuyo efecto con `familia ∈ {adt, oru, vxu}` es idéntico al de hoy (P-MD-25 lo demuestra):
  1. `leer_y_emparejar` (`:273`): `CVX.TIPOS if familia == "vxu" else CVM.TIPOS if familia == "mdm" else TIPOS_PROY`. **Es una edición de una línea de VXU** (la expresión gana una rama); es la única,
     y el rejuicio de VXU la vigila. Lo mismo en los puntos 3, 4 y 5.
  2. `emparejar` (`:320-322`): tras `if familia == "vxu": … ` se añade `elif familia == "mdm": CVM.emparejar(m, entries, top, out, pat, rol, usados)` **antes** del `elif familia == "adt"`;
     el cuerpo de `vxu` y el de `adt` no cambian.
  3. `emparejar` (`:415`): el filtro de `otros_tipos` usa los tipos de la familia (misma ampliación).
  4. `verificar` (`:1428-1431`): `imposibles` y `faltan` por familia (`CVM.imposibles(m)`, `CVM.FALTAN`).
  5. `verificar` (`:1454-1457`): `recuentos` por familia, más `out["conversion"]["recuentos"].update(CVM.recuentos(m, lec["entries"]))`.
  6. `_juzgar` (`:1501-1503`): `elif familia == "mdm": CVM.juzgar(J, m, lec, pat_entry)` entre `vxu` y el `else` de ORU.
  `verificar` ya lee `familia` del PE (`:1392`: gancho 1 de VXU); al final, `import conversion_mdm as CVM  # noqa: E402` tras la línea `:1621`. `MAPAS` no gana entradas (las de MDM viven en `MAPAS_MDM`
  y su autoprueba las coteja con el paquete, como `conversion_vxu.py:1160-1177`). `INFO["mdm"]` se registra desde `conversion_mdm` (`conversion_vxu.py:1156` como modelo). **Con tres familias, un registro de
  familias sería más limpio que cuatro expresiones con `if`; no se hace aquí porque obliga a reescribir líneas de VXU (condición 1) y se deja anotado como DV-MD si MD1 lo pide.**
- `verificador/verificador.py`: **nada** (`:264` ya despacha por `solo_transformacion`).
- `verificador/mcp_verificador.py`: `TABLAS["perfil_guia_mdm"]` (patrón `:1853-1854`); `SERVIDOR` a `"1.4"` (`:58`) y `REVISION` (`:59-60`) nombran la etapa 26; la lista de ficheros de la huella (`:69`) gana
  `conversion_mdm.py`; la descripción de `punto_entrada` (`:1102-1111`) nombra `mdm_conv`; `info_verificador` declara S-MD, L-MD, AMB-MD, DECISIONES_MD y el contrato del PE (`info_verificador.json:1345` es el de `vxu_conv`).
- `verificador/esquema_evidencia.json`: `mdm_conv` en el enum (`:453`) y en las descripciones (`:438,456`).
- Pruebas: `verificador/prueba_conversion_mdm.py` (nuevo, forma de `prueba_conversion.py:21-194`); `prueba_conversion.py` **no se edita**.
- Corpus: `verificador/bases_mdm.py` (§5). Herramienta: `cv/verificar_conversor.py` y `cv/conversor_juguete.py` (§7).

---

## 4. El perfil «guía» de MDM

### 4.0 Principio y niveles

Los de CV §3.0 sin cambio: **cuenta** (una sola representación en la guía o en R4), **convención** (la guía o el estándar admiten más de una: el esperado es un conjunto y solo cuenta lo
que queda fuera), **forma** (no es dato). Un campo vacío → elemento ausente; un elemento de valor único presente sin campo → `dato_inventado`; repetible → nota `extra` (Q-CV-D-5); nulo
explícito `""` → ausente; minúsculas en un código → convención (AMB-CV-1). Cada regla lleva su clase de las ocho (`resultados/diseno-conversores-fable.md` §4.1), su nivel y su cita.
**El perfil tiene 46 reglas: 39 cuentan, 2 son convención, 4 son nota y 1 es forma.** Las que dependen de una Q de Jev llevan su número; con confianza ≤ 0,52 entran en `ALTERNATIVA_MD`
(sensibilidad preinscrita, como `decisiones-qvx.md:21-23`).

### 4.1 DocumentReference: existencia y metadatos (TXA → `DocumentReference[i]`)

| R-MD | Elemento | Esperado (perfil guía) | Clase si difiere | Nivel | Cita |
|---|---|---|---|---|---|
| 1 | existencia | una DocumentReference por TXA (§2.2) | `recurso_ausente` / `recurso_inventado` | **cuenta** | `[G MSG_MDM_T02.csv:29]`; `[E9 CH09.txt:345-354]` |
| 2 | duplicados | más de una DocumentReference para un TXA: la primera se empareja, las demás son duplicadas; su `content` se suma al de la primera (AMB-MD-18) | `recurso_duplicado` (hecho `TXA-12`) | **cuenta** | `[G MSG_MDM_T02.csv:34-35]` (OBX y NTE entran en `DocumentReference[1]`) |
| 3 | `masterIdentifier.value` | TXA-12.1 desescapado; ausente → `dato_perdido`; otro → `valor_distinto`; presente sin TXA-12 → `dato_inventado`; un identifier propio del conversor → nota `extra` | `dato_perdido` / `valor_distinto` / `dato_inventado` | **cuenta** | `[G TXA_DocumentReference.csv:18]`; `[CM datatype-ei-organization-to-identifier EI.1 → value]`; `[F DocumentReference.masterIdentifier documentreference.profile.json:443-498]`; `[E9 CH09.txt:1383-1402]` |
| 4 | `masterIdentifier.system`/`assigner` | con EI.2 o EI.3 valorados, `system` o `assigner` (recurso, `contained` o lógico) contienen el namespace o el universal ID; la forma de la URI es convención | `dato_perdido` | **cuenta** (presencia); forma: convención | `[CM datatype-ei-organization-to-identifier EI.2 → assigner(Organization[1].identifier[1].value), EI.3 → …identifier[2].value]`; CX.4 en CV §3.1 (AMB-MD-19) |
| 5 | `identifier[]` ← TXA-16 | un Identifier con `value` = TXA-16 desescapado, **ruta completa** (`C:\E\docs\E\x` → `C:\docs\x`); truncado → `valor_distinto`; ausente → `dato_perdido`; otros identifiers → nota `extra` | `dato_perdido` / `valor_distinto` / `dato_inventado` | **cuenta** | `[G TXA_DocumentReference.csv:22]`; `[CM datatype-st-to-identifier ST.1 → $value]`; `[F DocumentReference.identifier :499-544]` (mapa v2 «TXA-16?», `:532-533`) |
| 6 | `type` ← TXA-2 | `coding[].code` ∋ TXA-2.1 (IS); `system`, `display`, `text`: convención/forma; codings de más: nota `extra`; sin TXA-2 y con `type`: `dato_inventado` | `dato_perdido` (sin `type`) / `valor_distinto` (otros códigos) / `dato_inventado` | **cuenta** (código); system: convención | `[G TXA_DocumentReference.csv:6]`; `[CM datatype-is-to-codeableconcept IS.1 → coding.code]`; `[E9 CH09.txt:863-884]`; `[F DocumentReference.type :658-720]` (mapa v2 `:705-707`); AMB-MD-1 |
| 7 | `status` con TXA-19 vacío o AV | `current`; ausente → `fhir_invalido` (1..1); otro valor del ValueSet → `valor_distinto`; fuera del ValueSet → `fhir_invalido` | `valor_distinto` / `fhir_invalido` | **cuenta** | `[G TXA_DocumentReference.csv:4,25]`; `[CM … TXA-19 → status IF TXA-19 = "AV"]`; `[E9 CH09.txt:1604-1621]`; `[F DocumentReference.status :545-604]` (required, `:571-583`); `codesystem-document-reference-status.json:38-52`; AMB-MD-4 |
| 8 | `status` con TXA-19 = CA, OB o UN | `status` ∈ {current, superseded, entered-in-error} (cualquiera: la guía no fija valor) **y** el código TXA-19 conservado: en `status.extension[alternate-codes]` (URL con `http` o `https`; `valueCodeableConcept.coding.code`, `valueCoding.code` o `valueCode` = TXA-19) o, solo para CA → `entered-in-error` y OB → `superseded`, en el propio `status` (Q-MD-D-9); ni lo uno ni lo otro → `dato_perdido`; `status` ausente o fuera del ValueSet → `fhir_invalido` | `dato_perdido` / `fhir_invalido` | **cuenta** (retención); valor: convención | `[G TXA_DocumentReference.csv:26-27]`; `[CM … TXA-19 → status.extension[1].url / .valueCodeableConcept IF TXA-19 IN ("CA","OB","UN")]`; `[E9 CH09.txt:77-82,144-148,1604-1621]`; AMB-MD-4, AMB-MD-5, L-MD-11 |
| 9 | `docStatus` ← TXA-17 | **conjunto E(c)** para c = TXA-17: {c literal (guía: `$value`)} ∪ MAPA_0271(c) (§4.5). Observado ∈ MAPA_0271(c): nota `convencion`. Observado = c literal (fuera de `composition-status`): según Q-MD-D-4. Observado válido y fuera de E(c): `valor_distinto`. Observado ni literal ni válido: `fhir_invalido` + `valor_distinto`. Ausente (y c no conservado en ninguna extensión): `dato_perdido`. Presente con TXA-17 vacío: `dato_inventado` | `valor_distinto` / `dato_perdido` / `fhir_invalido` / `dato_inventado` | **cuenta** (Q-MD-D-4) | `[G TXA_DocumentReference.csv:23]`; `[CM datatype-id-to-code $value]`; `[F DocumentReference.docStatus :606-656]` (required `:631-639`); `codesystem-composition-status.json:49-68`; `[E9 CH09.txt:87-132,1487-1500]`; AMB-MD-3 |
| 10 | `securityLabel[]` ← TXA-18 | un coding con `code` = TXA-18 (V, R, U) y `system` v2-0272 (guía) o v3-Confidentiality (R4, convención); otro `code` → `codigo_mal_mapeado`; ausente → `dato_perdido`; labels de más: nota `extra` | `codigo_mal_mapeado` / `dato_perdido` | **cuenta** | `[G TXA_DocumentReference.csv:24]`; `[CM table-hl70272-to-v2-0272 V, R, U]`; `[F DocumentReference.securityLabel :1318-1377]` (extensible `:1344-1356`); `valueset-security-labels.json:49`; `[E9 CH09.txt:1591-1602]`; AMB-MD-20 |
| 11 | `date` ← TXA-6 | con hora: `instant` (R-CV-7, `CV._fecha(…, "instant", …)`: instante si hay zona, hora local si no; con menos de segundos, ausente o completado con `:00` y zona, AMB-CV-9); sin hora (solo fecha): `date` ausente **o** completado con `00:00:00` y una zona el mismo día (nota AMB-CV-9) — `_fecha_doc` solo llama a `CV._fecha` si TXA-6 trae hora o si hay `date` observado, porque `_fecha` cuenta `dato_perdido` ante un observado ausente (`conversion.py:472-474`); sin TXA-6: presente → nota si coincide con MSH-7, EVN-2, TXA-4, -7 u -8, si no `dato_inventado` (AMB-MD-17) | según `_fecha`: `valor_distinto` / `dato_perdido` / `dato_inventado` / `fhir_invalido` | **cuenta** | `[G TXA_DocumentReference.csv:10-12]`; `[CM … TXA-6 → date; «If time is included»]`; `[CM datatype-ts-to-datetime]`; `[F DocumentReference.date :841-884]`; `[E2A CH02A.txt:5380]`; AMB-MD-17 |
| 12 | `author[]` ← TXA-9 | por cada repetición con XCN.1 o XCN.2: un `author` que resuelve (recurso, `contained`, lógico o `PractitionerRole.practitioner →`) a un Practitioner con `identifier` ∋ XCN.1, `name.family` = XCN.2 (FN.1) y `given[1]` = XCN.3; solo `display` con XCN.1 valorado → `dato_perdido`, sin XCN.1 → convención; referencia que no resuelve → `referencia_rota`; actor Organization/Device → `dato_perdido` (XCN es una persona); autores de más: nota `extra` | `dato_perdido` / `valor_distinto` / `referencia_rota` | **cuenta** | `[G TXA_DocumentReference.csv:15]`; `[CM datatype-xcn-to-practitioner XCN.1 → identifier[1].value, XCN.2 → name.family, XCN.3 → name.given[1]]`; `[F DocumentReference.author :885-941]` (destinos `:899-904`); `[E9 CH09.txt:1042]`; `CV._participantes` (`conversion.py:958-1010`) y `CVX._performers` (`conversion_vxu.py:837-902`) como modelo |
| 13 | `authenticator` ← TXA-10 | como R-MD-12 para **una** repetición cualquiera de TXA-10 (AMB-MD-14, Q-MD-D-11); las demás nota `extra`; sin TXA-10 y con `authenticator`: `dato_inventado` | `dato_perdido` / `valor_distinto` / `referencia_rota` / `dato_inventado` | **cuenta** | `[G TXA_DocumentReference.csv:16]`; `[F DocumentReference.authenticator :942-999]` (destinos `:956-958`); `[E9 CH09.txt:1156]` |
| 14 | `content.attachment.contentType` ← TXA-3 | con TXA-3 valorado, **algún** attachment lleva `contentType`; su valor es convención (Q-MD-D-3): el literal TXA-3 o la familia MIME de la 0191 (§4.5); sin TXA-3, nada | `dato_perdido` (ningún attachment con `contentType`) | convención; **cuenta** la ausencia total | `[G TXA_DocumentReference.csv:7]`; `[F DocumentReference.content.attachment :1554-1555]`; `[F Attachment.contentType attachment.profile.json:175-215]`; AMB-MD-2 |
| 15 | `subject` y `context.encounter` | si `subject` está: resuelve a Patient#1 (referencia lógica por identifier: convención); a otro Patient o sin resolver → `referencia_rota`; si falta: nota `sin_subject` (Q-MD-D-6, L-MD-5). `context.encounter` presente: debe resolver al Encounter#1 (`referencia_rota` si no); ausente: nota; presente sin PV1: `dato_inventado` | `referencia_rota` / `dato_perdido` (solo con Q-MD-D-6 b) / `dato_inventado` | **cuenta** (presente y mal); ausente: nota | `[F DocumentReference.subject :779-840]` (destinos `:792-795`, mapa v2 «PID-3», `:820-821`); `[F DocumentReference.context.encounter :1766-1809]`; `[F Bundle «Resolving references in Bundles» bundle.profile.json:803-806]`; `CV._sujeto` (`conversion.py:934-955`) |
| 16 | `context.related[]` → ServiceRequest | por cada ServiceRequest emparejado (todos o solo el primero: Q-MD-D-7), alguna referencia de `related` resuelve a él; ninguna → `dato_perdido` (hecho `ORC(i)-1`); referencia que no resuelve → `referencia_rota`; con el mensaje sin grupos, un `related` a un ServiceRequest: nota `extra` | `dato_perdido` / `referencia_rota` | **cuenta** | `[G MSG_MDM_T02.csv:29,34-35]` (columna References); `[E9 CH09.txt:235-240]`; `[F DocumentReference.context.related :2047-2089]` (`Resource`, `:2059-2062`); AMB-MD-16 |

### 4.2 DocumentReference: el contenido (OBX y NTE → `content[]`)

**Definiciones que usan las reglas** (todas deterministas y de biblioteca estándar; ninguna lee el significado del documento):

- **Texto esperado** de una repetición de TX, FT o NTE-3: se quitan las órdenes de formato y locales (`\.xx…\`, `\H\`, `\N\`, `\Zdddd\`, `\Cxxyy\`, `\Mxxyyzz\`, con la barra de MSH-2.4) y se aplica
  `Msg.desescapa` (`mapeador_referencia.py:163-178`: `\F\ \S\ \T\ \R\ \E\ \X…\`) — `[E2 CH02.txt:947-1111]`. Una repetición vacía no aporta palabras.
- **Palabras**: las secuencias maximales alfanuméricas Unicode (`[^\W_]+`, `casefold`) del texto. Puntuación, símbolos y espacios no son palabras (L-MD-15).
- **Pool de texto observado**: el `data` de cada attachment de la DocumentReference emparejada (y de las duplicadas) que no esté emparejado con un ED o un RP y cuyo Base64 se decodifique en UTF-8; si el `data` no es Base64
  válido, se lee su cadena cruda como texto (y se cuenta R-MD-34, no además la pérdida). Sus palabras se calculan igual.
- **«Llega entero»** (texto): las palabras del OBX son una subsecuencia ordenada de las de **un** attachment del pool; si no, de la concatenación de todos en el orden del Bundle (nota `partido`); si no, falta alguna →
  `dato_perdido` (el `que` da la primera palabra que falta y cuántas); están todas pero en otro orden → `valor_distinto`. El orden entre OBX distintos y el de los `content[]` son forma.
- **Binario esperado** de una repetición de ED: los octetos de ED.5 según ED.4: `Base64` → `base64.b64decode(ED.5)`; `A` → `ED.5` desescapado codificado en ASCII (cualquier carácter no ASCII lo hace imposible); `Hex` → `bytes.fromhex(ED.5)`
  — `[E2A CH02A.txt:1846-1876]`. Se compara con los octetos del `data` observado; **no se interpretan** (condición 7).

| R-MD | Elemento | Esperado (perfil guía) | Clase si difiere | Nivel | Cita |
|---|---|---|---|---|---|
| 17 | `content` 1..* y `attachment` 1..1 | con al menos un OBX con destino (TX, FT, ED, RP) o un NTE de OBX con texto, la DocumentReference (y duplicadas) trae algún `content`, y cada `content` un `attachment`; si no, un hallazgo que **absorbe** los `dato_perdido` de los OBX de esa DocumentReference. Si el único contenido son OBX sin destino (CE, ST…): nota `sin_content_posible` | `fhir_invalido` | **cuenta** | `[F DocumentReference.content documentreference.profile.json:1379-1411]` (1..*, `:1383-1384`); `[F …content.attachment :1525-1530]` (1..1); `[G MSG_MDM_T02.csv:34]` |
| 18 | TX: llegada | las palabras del texto esperado de **todas** las repeticiones de OBX-5 llegan enteras (definición de arriba) | `dato_perdido` / `valor_distinto` (hecho `OBX(k)-5`) | **cuenta** | `[G OBX_DocumentReference.csv:12]`; `[CM segment-obx-to-documentreference OBX-5 → content[4].data IF OBX-2="TX"]`; `[E7 CH07.txt:2643-2648]`; `[E2A CH02A.txt:5437-5453]` |
| 19 | TX y FT: salto entre repeticiones | si OBX-5 trae n ≥ 2 repeticiones, entre la última palabra de una y la primera de la siguiente, en el texto observado, hay al menos un LF o un CR (LF, CR LF o CR: el estándar admite CR LF o LF) | `valor_distinto` | **cuenta** | `[G OBX_DocumentReference.csv:9,12]` («each repeat yields a line feed»); `[E2A CH02A.txt:5446-5453]` |
| 20 | TX: delimitadores desescapados | el texto observado no contiene `\F\`, `\S\`, `\T\`, `\R\`, `\E\` (con la barra del mensaje) cuando el original los llevaba escapados | `valor_distinto` | **cuenta** | `[E2 CH02.txt:1037-1046]`; `[E2A CH02A.txt:5437-5441]` |
| 21 | TX: `contentType` | cada attachment que lleva texto de un OBX TX trae `contentType`; conjunto según Q-MD-D-3: (a) `application/text`; (b) `application/text` o `text/plain`; (c) cualquier `type/subtype` de texto; ausente → `dato_perdido` (hecho `OBX(k)-2`); otro → `valor_distinto` | `dato_perdido` / `valor_distinto` | **cuenta** (Q-MD-D-3) | `[G OBX_DocumentReference.csv:13]`; `[CM … OBX-5 → content[4].contentType]`; `[F Attachment.contentType attachment.profile.json:175-215]`; AMB-MD-8 |
| 22 | FT: llegada | como R-MD-18 sobre el texto esperado sin órdenes de formato | `dato_perdido` / `valor_distinto` (hecho `OBX(k)-5`) | **cuenta** | `[G OBX_DocumentReference.csv:9]`; `[CM … OBX-5 → content[2].data IF OBX-2="FT"]`; `[E2A CH02A.txt:2154-2181]`; `[E2 CH02.txt:1056-1095]` |
| 23 | FT: escapes según `contentType` | con `text/hl7v2`, los escapes (de delimitador o de formato) pueden estar crudos o resueltos (convención); con cualquier otro `contentType`, ningún escape de delimitador ni orden de formato (`\.br\`, `\H\`…) puede quedar crudo | `valor_distinto` | **cuenta** | `[G OBX_DocumentReference.csv:10]` («text/hl7v2»); `[E2 CH02.txt:1056-1095]`; AMB-MD-9 |
| 24 | FT y NTE: `contentType` | como R-MD-21 con `text/hl7v2` (a) o `text/hl7v2` o `text/plain` (b y c) | `dato_perdido` / `valor_distinto` | **cuenta** (Q-MD-D-3) | `[G OBX_DocumentReference.csv:10]`; `[G NTE_DocumentReference.csv:7]` |
| 25 | ED: `data` si ED.4 = Base64 | existe un attachment cuyo `data` decodifica a los mismos octetos que ED.5; si hay uno con `data` distinto: `valor_distinto` (el `que` dice si es la codificación doble, un truncamiento o ninguna de las dos); si no hay ninguno: `dato_perdido` | `valor_distinto` / `dato_perdido` | **cuenta** | `[G OBX_DocumentReference.csv:8]`; `[G ED_Attachment.csv:9]`; `[CM datatype-ed-to-attachment ED.5 → data]`; `[E2A CH02A.txt:1861-1876]` |
| 26 | ED: `data` si ED.4 = A o Hex | igual con el binario esperado de A (ASCII) o Hex («convert from A or HEX to binary64»); si ED.5 no es válido para su ED.4 (imposible), no hay esperado y un `data` igual al texto crudo es `valor_imposible_convertido` | `valor_distinto` / `dato_perdido` / `valor_imposible_convertido` | **cuenta** | `[G ED_Attachment.csv:9]`; `[E2A CH02A.txt:1846-1859]` (0299) |
| 27 | ED: `contentType` | con ED.3 valorado: el observado, en minúsculas, es ED.3 o `ED.2/ED.3`, o su subtipo (tras la última `/` y antes de un `+`) es ED.3 sin distinguir mayúsculas (`image/jpeg`, `application/postscript`, `text/xml`, `application/xml`, `application/x-hl7-cda-level-one+xml`); ausente → `dato_perdido`; otro → `valor_distinto`. Con ED.3 vacío: nada se espera (el ED.2 va a la extensión, que no cuenta) | `dato_perdido` / `valor_distinto` | **cuenta** (Q-MD-D-3) | `[G ED_Attachment.csv:7]`; `[CM datatype-ed-to-attachment ED.3 → contentType]`; `[E2A CH02A.txt:1840-1844,4431-4448]` (0291); AMB-MD-10 |
| 28 | ED: una `content` por repetición | una repetición de OBX-5 = un attachment (y no un `content` que mezcle dos); n repeticiones y menos attachments con sus octetos → `dato_perdido` por la que falta | `dato_perdido` | **cuenta** | `[G OBX_DocumentReference.csv:8]` («each repeat yields a new .content instance») |
| 29 | ED: `Binary` referenciado | un attachment sin `data` cuyo `url` resuelve a un `Binary` del Bundle con los mismos octetos: se acepta (nota `convencion`) | — | convención | `[F Attachment.url attachment.profile.json:315-329]`; `CV.resolver` |
| 30 | RP: `url` | un attachment con `url` = RP.1 desescapado; con un prefijo delante (`…/RP.1`): nota `convencion`; ausente → `dato_perdido`; otro → `valor_distinto` | `dato_perdido` / `valor_distinto` | **cuenta** | `[G OBX_DocumentReference.csv:11]`; `[G RP_Attachment.csv:4]`; `[CM datatype-rp-to-attachment RP.1 → url]`; AMB-MD-11 |
| 31 | RP: `contentType` | con RP.3 y RP.4 valorados: el literal `RP.3/RP.4` (sin distinguir mayúsculas) o su subtipo (RP.4) como en R-MD-27; con uno solo valorado, nada se espera | `dato_perdido` / `valor_distinto` | **cuenta** (Q-MD-D-3) | `[G RP_Attachment.csv:6]` (`RP.3"/"RP.4`); `[CM datatype-rp-to-attachment RP.3 → contentType]`; `[E2A CH02A.txt:4405-4448]` |
| 32 | RP: una `content` por repetición | como R-MD-28 | `dato_perdido` | **cuenta** | `[G OBX_DocumentReference.csv:11]` |
| 33 | NTE bajo OBX: llegada | las palabras de cada repetición de NTE-3 llegan en el pool (hecho `NTE(j)-3`) | `dato_perdido` / `valor_distinto` | **cuenta** | `[G NTE_DocumentReference.csv:6]`; `[CM segment-nte-to-documentreference NTE-3 → content[1].attachment.data]`; `[G MSG_MDM_T02.csv:35]`; `[E2 CH02.txt:4894-4900]` |
| 34 | `data` es Base64 | todo `data` de un attachment de la DocumentReference es Base64 válido (alfabeto estándar y `=`, espacios ignorados; `base64.b64decode(…, validate=True)`) | `fhir_invalido` | **cuenta** | `[F Attachment.data attachment.profile.json:279-293]` (`base64Binary`); L-MD-7 |
| 35 | OBX de tipo sin destino | OBX-2 ∉ {TX, FT, ED, RP}: nada se espera; el valor puede estar o no en la DocumentReference | nota `sin_destino` (Q-MD-D-12) | nota | `[G OBX_DocumentReference.csv:8-13]`; L-MD-2 |
| 36 | Observation y otros recursos desde OBX | un `Observation` o `DiagnosticReport` en el Bundle es `otros_tipos` | nota `fuera_proyeccion` (Q-MD-D-8) | nota | `[G MSG_MDM_T02.csv:34]` (OBX → `DocumentReference[1]`) |

### 4.3 ServiceRequest (COMMON_ORDER → `ServiceRequest[i]`, perfil reducido)

| R-MD | Elemento | Esperado (perfil guía) | Clase si difiere | Nivel | Cita |
|---|---|---|---|---|---|
| 37 | existencia | un ServiceRequest por grupo COMMON_ORDER (por ORC, o por OBR si no hay ORC); sobrantes → `recurso_inventado` | `recurso_ausente` / `recurso_inventado` | **cuenta** | `[G MSG_MDM_T02.csv:20,26]`; `[E9 CH09.txt:322-343]` |
| 38 | `subject` | resuelve a Patient#1 (`CV._sujeto`); ausente → `dato_perdido` (1..1) | `referencia_rota` / `dato_perdido` | **cuenta** | `[G MSG_MDM_T02.csv:20]`; `[F ServiceRequest.subject servicerequest.profile.json:1089-1097]` |
| 39 | `identifier[]` | PLAC con `value` ∈ {OBR-2.1, ORC-2.1} y FILL con `value` ∈ {OBR-3.1, ORC-3.1} (el de OBR si está valorado, el de ORC si no; si los dos y distintos, basta uno: AMB-CV-8); `type.coding.code` PLAC/FILL (`system` v2-0203: convención); intercambiados → `codigo_mal_mapeado`; ausente → `dato_perdido`; otros identifiers (ORC-4, ORC-33…) nota `extra`. Los números de TXA-14/TXA-15 no se esperan | `dato_perdido` / `codigo_mal_mapeado` | **cuenta** | `[G ORC_ServiceRequest.csv:10-15]`; `[G OBR_ServiceRequest.csv:6-12]`; `[CM datatype-ei-extension-to-identifier EI.1 → value]`; `[F ServiceRequest.identifier :439]`; `[E9 CH09.txt:242-246]`; `CVX._identificadores` (`conversion_vxu.py:925-943`) |
| 40 | `code` ← OBR-4 | `CV._codigo`: CE.1 y CE.4 en algún coding, system canónico para LN/SCT (L-CV-3), CE.9 → `text`; ausente → `dato_perdido` | `dato_perdido` / `valor_distinto` / `codigo_mal_mapeado` | **cuenta** | `[G OBR_ServiceRequest.csv:13]`; `[CM datatype-cwe-to-codeableconcept]`; `[F ServiceRequest.code :941]`; `[E4 CH04.txt:3448-3456]` |
| 41 | `status` e `intent` | presentes (1..1) y dentro de `request-status` y `request-intent` (required); **sin valor esperado**: la propia hoja lo declara «localized interpretation» | `fhir_invalido` | **cuenta** (validez) | `[G ORC_ServiceRequest.csv:4]`; `[G OBR_ServiceRequest.csv:4]`; `[F ServiceRequest.status :692-725; .intent :749-782]`; AMB-MD-25, L-MD-6 |
| 42 | resto del ServiceRequest | NTE de OBR → `note`, TQ1, ORC-4/-5/-9/-12, OBR-5/-6/-16/-31, `requester`, `occurrence[x]`… : nota | — | nota | `[G MSG_MDM_T02.csv:23-27]`; `[CM segment-nte-to-servicerequest]` |

### 4.4 Patient, Encounter, el resto y la forma

| R-MD | Elemento | Esperado | Clase | Nivel | Cita |
|---|---|---|---|---|---|
| 43 | Patient (PID) | CV §3.1 íntegro (`CV._patient`, `conversion.py:533-541`) | las de CV | **cuenta** | `[G MSG_MDM_T02.csv:13]`; `[G PID_Patient.csv]` |
| 44 | Encounter (PV1) | CV §3.2 íntegro (`CV._encounter`, `conversion.py:882-905`); ausente: `recurso_ausente` (con PV1-2 = N según Q-CV-D-6) | las de CV | **cuenta** | `[G MSG_MDM_T02.csv:15]`; `[G PV1_Encounter.csv]` |
| 45 | resto de recursos | MessageHeader, Provenance, Device, Coverage, Basic, Organization, Practitioner (salvo como destino de `author`/`authenticator`), Binary no alcanzado, Observation: `otros_tipos` | — | nota | `[G MSG_MDM_T02.csv:3-18,30]`; L-CV-5; Q-MD-D-2 |
| 46 | `id`, `meta`, `text`, extensiones (salvo la de R-MD-8), `display`, orden de listas y de `content[]`, `Bundle.*`, `attachment.title/size/hash/creation/language` | forma | — | forma | L-CV-4, L-CV-9, L-MD-11 |

### 4.5 Las tablas de códigos que necesita el perfil y su paso a FHIR

| Tabla | Clase y valores en 2.5 | Destino FHIR | Mapa | Dónde se usa | Texto de 2.5 |
|---|---|---|---|---|---|
| 0270 Document Type | **user-defined**; 14 sugeridos: AR, CD, CN, DI, DS, ED, HP, OP, PC, PH, PN, PR, SP, TS | `type.coding.code` literal, sin `system` | ninguno (la guía no trae `table-hl70270`) | R-MD-6 | `[E9 CH09.txt:863-884]` |
| 0271 Document Completion Status | HL7; DI, DO, IP, IN, PA, AU, LA | `docStatus` | **la guía no trae mapa**; `MAPA_0271` (abajo) es de R4 y de las definiciones de 2.5, no de la guía (L-MD-6) | R-MD-9 | `[E9 CH09.txt:1487-1500]`, definiciones `:87-132` |
| 0272 Document Confidentiality Status | HL7; V, R, U | `securityLabel[].coding` | `table-hl70272-to-v2-0272` (identidad, system `http://terminology.hl7.org/CodeSystem/v2-0272`); v3-Confidentiality admitido por el binding extensible | R-MD-10 | `[E9 CH09.txt:1591-1602]` |
| 0273 Document Availability Status | HL7; AV, CA, OB, UN | `status` y `status.extension[alternate-codes]` | sin ConceptMap de tabla; las condiciones viven en el mapa de segmento; AV/vacío → `current` | R-MD-7, R-MD-8 | `[E9 CH09.txt:1604-1621]`, definiciones `:77-82,144-148` |
| 0275 Document Storage Status | HL7; AC, AA, AR, PU | — | — | (TXA-20: sin destino) | `[E9 CH09.txt:1658-1668]` |
| 0191 Type of Referenced Data | HL7; AP, AU, FT, IM, multipart, NS, SD, SI, TEXT, TX | familia MIME del `contentType` (TXA-3) y de ED.2/RP.3 | `FAMILIA_0191` = TEXT/TX/FT → `text`; AP → `application`; AU → `audio`; IM → `image`; multipart → `multipart`; NS/SD/SI → sin familia (cualquiera) — **del RFC/IANA, no de la guía** (AMB-MD-2) | R-MD-14, R-MD-27, R-MD-31 | `[E9 CH09.txt:892-903]`; `[E2A CH02A.txt:4409-4420]` |
| 0291 Subtype of Referenced Data | HL7; BASIC, DICOM, FAX, GIF, HTML, JOT, JPEG, Octet-stream, PICT, PostScript, RTF, SGML, TIFF, x-hl7-cda-level-one, XML (no hay PDF) | subtipo del `contentType` (ED.3, RP.4) | igualdad sin distinguir mayúsculas | R-MD-27, R-MD-31 | `[E2A CH02A.txt:4431-4448]` |
| 0299 Encoding | HL7; A, Hex, Base64 | cómo se obtiene `data` | A y Hex se convierten, Base64 pasa (`[G ED_Attachment.csv:9]`) | R-MD-25, R-MD-26 | `[E2A CH02A.txt:1850-1859]` |
| 0125 Value Type | HL7; AD, CE, CF, CK, CN, CP, CX, DT, ED, FT, MO, NM, PN, RP, SN, ST, TM, TN, TS, TX, XAD, XCN, XON, XPN, XTN | selector del destino de OBX-5 | solo ED, FT, RP, TX tienen fila | R-MD-18..35 | `[E7 CH07.txt:2603-2637]` |
| 0203 Identifier Type | PLAC, FILL | `ServiceRequest.identifier.type` | identidad (`table-hl70203-to-v2-0203`) | R-MD-39 | CV §3.5 |
| `document-reference-status` | R4 | `status` ∈ {current, superseded, entered-in-error} | — | R-MD-7, R-MD-8 | `fhir_r4/codesystem-document-reference-status.json:38-52` |
| `composition-status` | R4 | `docStatus` ∈ {preliminary, final, amended, entered-in-error} | — | R-MD-9 | `fhir_r4/codesystem-composition-status.json:49-68` |

**`MAPA_0271` (R-MD-9, S-MD-9): conjunto de `composition-status` coherente con cada código.** No es de la guía; cada línea lleva su cita y su alternativa.

| TXA-17 | Admitidos | Por qué (cita) |
|---|---|---|
| LA | `final` | «the most mature state» (`[E9 CH09.txt:124-128]`); `final` = «complete and verified by an appropriate person» (`codesystem-composition-status.json:55-57`) |
| AU | `final`, `preliminary` | firmado y atestiguado (`[E9 CH09.txt:91-96]`) pero la figura 9-1 todavía lo hace pasar a LA (`:1533-1535`): «no further work is planned» no está claro (AMB-MD-3) |
| PA | `preliminary` | transcrito y sin autenticar (`[E9 CH09.txt:130-132]`); `preliminary` = «may be incomplete or unverified» (`codesystem-composition-status.json:50-52`) |
| IN, IP, DI, DO | `preliminary` | información que falta, en curso, hablado sin transcribir, o recibido sin traducir (`[E9 CH09.txt:105-122]`) |
| cualquiera | nunca `entered-in-error` ni `amended` | T02 es el documento original (`[E9 CH09.txt:139-142,306-307]`); `amended` presupone un `final` previo (`codesystem-composition-status.json:60-62`) |

### 4.6 Cómo se cita cada hallazgo (`C_MDM`, patrón `conversion.py:76-106` y `conversion_vxu.py:98-134`)

Cada hallazgo que cuenta lleva `citas` con, como mínimo, una de la guía y una del estándar o de FHIR (CV §3.7). **Cuidado con la colisión de claves**: `CV.C` ya tiene `OBX`, `OBX-3`, `OBX-5`,
`OBX-6`, `PID`, `PV1`, `OBR-4`, etc. con citas de ORU y ADT; `_cit` busca `C.get(clave) or C.get(base) or C.get(base.split("-")[0])` (`conversion.py:109-111`). Por eso:

```
C_MDM = {"TXA": ["[G MSG_MDM_T02.csv:29] TXA → DocumentReference[1]"],
         "TXA-2": ["[CM segment-txa-to-documentreference TXA-2 → type]", "[CM datatype-is-to-codeableconcept]", "[G TXA_DocumentReference.csv:6]", "[E9 §9.6.1.2 tabla 0270]", "[F DocumentReference.type]"],
         "TXA-3": [... "[G TXA_DocumentReference.csv:7]", "[E9 §9.6.1.3 tabla 0191]", "[F Attachment.contentType required]", "[AMB-MD-2]"],
         "TXA-6": [... "[G TXA_DocumentReference.csv:10-12]", "[F DocumentReference.date instant]"],   "TXA-9": [... "[G TXA_DocumentReference.csv:15]", "[CM datatype-xcn-to-practitioner]"],
         "TXA-10": [... ":16"], "TXA-12": [... ":18", "[CM datatype-ei-organization-to-identifier]"], "TXA-16": [... ":22"],
         "TXA-17": [... ":23", "[CM datatype-id-to-code $value]", "[F DocumentReference.docStatus required]", "[E9 §9.6.1.17 tabla 0271]", "[AMB-MD-3]"],
         "TXA-18": [... ":24", "[CM table-hl70272-to-v2-0272]", "[AMB-MD-20]"],  "TXA-19": [... ":4,25-27", "[F DocumentReference.status required]", "[AMB-MD-4]"],
         "OBX-TX": ["[CM segment-obx-to-documentreference OBX-5 IF OBX-2=TX]", "[G OBX_DocumentReference.csv:12-13]", "[E2A §2.A.78 TX]"],
         "OBX-FT": [... ":9-10", "[E2A §2.A.31 FT]", "[E2 §2.7.6]"], "OBX-ED": [... ":8", "[G ED_Attachment.csv:5-9]", "[E2A §2.A.24 ED]"],
         "OBX-RP": [... ":11", "[G RP_Attachment.csv:4,6]", "[E2A §2.A.65 RP]"], "NTE-3": ["[G NTE_DocumentReference.csv:6-7]", "[E2 §2.15.10.3]"],
         "ORC-ref": ["[G MSG_MDM_T02.csv:20,29]", "[E9 §9.5 «wholly and exclusively satisfied»]"], "ORC-2": [... "[G ORC_ServiceRequest.csv:10-12]", "[G OBR_ServiceRequest.csv:6-8]"],
         "ORC-3": [... ":13-15", ":9-12"], "OBR-4": ["[G OBR_ServiceRequest.csv:13]", "[E4 §4.5.3.4]"], "SR": ["[G MSG_MDM_T02.csv:20,26] ORC/OBR → ServiceRequest[1]"]}
C_SEG = {"PID": ["[G MSG_MDM_T02.csv:13] PID → Patient[1]"], "PV1": ["[G MSG_MDM_T02.csv:15] PV1 → Encounter[1]"]}   # las claves que en CV.C son de ADT y ORU
```

Los hechos de contenido llevan las citas **por parámetro** (`citas=C_MDM["OBX-ED"]`), como `conversion_vxu.py:414,428`; las claves `OBX-TX`, `OBX-FT`, `OBX-ED` y `OBX-RP` son nuevas y no chocan. `CV.C.update` solo añade
claves que no existen (DV-VX-2) y la autoprueba de `conversion_mdm` falla si una clave de `C_MDM` ya está en `CV.C` con otra cita y no está en `C_SEG` (como `conversion_vxu.py:1172-1175`).
`consultar_tabla("perfil_guia_mdm")` devuelve `PERFIL_GUIA_MDM` (una fila por R-MD con `elemento`, `campo`, `regla`, `nivel`, `citas`), como `perfil_guia_vxu` (`mcp_verificador.py:1853-1854`).

---

## 5. El corpus sintético (`bases_mdm.py`)

### 5.1 Principios, y la regla contra la firma mecánica

1. **Cada base es un mensaje de documento clínico completo y plausible en v2.5**, escrito desde `[E9 CH09.txt:306-354]` (estructura), §9.6.1 (TXA), §9.6.2 y `[E7 CH07.txt:2556-2652,2787]` (OBX), `[E2A CH02A.txt:1804-1876,
   4384-4448]` (ED, RP), `[E2 CH02.txt:947-1111]` (escapes, formatos), `[E4 CH04.txt:1820-1860,3285-3343]` (ORC, OBR) y el ejemplo `[E9 CH09.txt:1963-1983]`: MSH, EVN, PID, PV1, [COMMON_ORDER], TXA y uno o más OBX [con NTE].
   Pacientes ficticios (seis, apellidos de una lista cerrada), cuatro profesionales ficticios, textos de una lista cerrada de frases con una **palabra ancla única por OBX** (`Zeta0403`) para que «llegue entero»
   sea comprobable, y cargas binarias generadas con `base64` desde cadenas sintéticas (`SINTETICO-07-IM`): el juez no las decodifica, solo las compara.
2. **Cada base ejercita una rama de la guía o del estándar** (una fila con condición, un valor de una tabla, una forma de dato), no un fallo supuesto de nadie. La tabla de §5.2 dice cuál.
3. **Regla medible contra la firma de mutación:** `bases_mdm.py --firma` calcula, para cada par de bases, el número de campos (segmento-campo) con valor distinto, sin MSH-7, MSH-10 ni EVN-2, y exige **≥ 3 en todo par**,
   y además que ningún par difiera solo en los campos que ejercita una de las dos (forma de `bases_vxu.py:261-271`). Lo que no cumpla se reescribe antes de sellar. Las ocho primeras bases son el **subconjunto
   de control**: documentos planos donde todo lo mapeado está presente y es simple, para distinguir un mecanismo que muerde en todo el corpus de uno que solo muerde en la rama. El corpus **no se construye
   mutando el control**: los textos, las cargas, los profesionales, las fechas y los números cambian en cada base.
4. **Todas válidas** (ninguna lleva un valor imposible ni un segmento fuera de sitio): la autoprueba afirma, para cada base, que `MR.mensajes` la lee, que `PE.estructura_de(m, PUNTOS["mdm_conv"])` da `MDM_T02`,
   que `EH.emparejar` con `EH.gramatica("MDM_T02")` no da ausentes ni fuera de orden, que todo TS pasa `MR.partes_dtm`, que TXA-3, TXA-17, TXA-18 y TXA-19, ED.2/RP.3, ED.3/RP.4, ED.4 y OBX-2 están en sus tablas
   (0191, 0271, 0272, 0273, 0291, 0299, 0125), que todo ED.5 es válido para su ED.4 (Base64 con `b64decode(validate=True)`, Hex con `bytes.fromhex`, A solo ASCII) y no pasa de 65536 caracteres, que EVN-1 = MSH-9.2
   (`[E9 CH09.txt:214-216]`) y que ningún texto tiene un carácter fuera de ASCII salvo con MSH-18 = `UNICODE UTF-8`. Los imposibles van a las pruebas P-MD, no al corpus (como `bases_oru.py:3-4`).
5. **Sin esperado escrito**: el fichero no guarda ningún Bundle ni canónico; la previsión se sella aparte (§6).
6. **Deterministas**: `bases_mdm/BNN.hl7` (segmentos separados por CR, sin MLLP) y `bases_mdm.jsonl` (`id`, `descripcion`, `ejercita`, `campos`, `fichero`, `msh10 = "MDM-BNN"`, `segmentos`), con la huella del conjunto fijada
   al terminar MD2-a (`bases_vxu.py:27`).

### 5.2 Las 40 bases y qué ejercita cada una

Piezas comunes: `MSH|^~\&|DOCSYS|CSSYN|HIS|SALUD|<fecha>||MDM^T02^MDM_T02|MDM-BNN|P|2.5`; `EVN|T02|<fecha>`; `PID|1||DOC0001^^^CSSYN^MR||Prueba^Mateo^^^^^L||<nac>|M`; `PV1|1|<I/O/E>|<ubicación>|…|V0001^^^CSSYN^VN`;
`TXA|1|<0270>|<0191>|<TXA-4>|<TXA-5>|<TXA-6>|<TXA-7>|<TXA-8>|<TXA-9>|<TXA-10>|<TXA-11>|<TXA-12>|<TXA-13>|<TXA-14>|<TXA-15>|<TXA-16>|<0271>|<0272>|<0273>`;
`OBX|k|<0125>|<código>^<texto>^L|<sub-id>|<valor>||||||F`; ORC y OBR con números de placer y de filler (`PL0001^CSSYN`, `FL0001^CSSYN`) y OBR-4 (`DOC-DS^Informe de alta^L`).

| Id | Qué es | Ejercita (rama de la guía o del estándar) | R-MD |
|---|---|---|---|
| B01 | **Control.** DS (informe de alta); TXA-3 TEXT, TXA-17 AU, TXA-18 R, TXA-19 AV; TXA-6 con hora y zona; TXA-9 ×1 y TXA-10 ×1; TXA-12 `DOC0001^CSSYN`; TXA-16 `/docs/2023/alta0001.txt`; un grupo ORC+OBR (ORC-2/3 = OBR-2/3); un OBX TX de una línea | AU, AV, R; TX básico; PLAC+FILL; zona por instante | 1, 3, 5-7, 9-13, 16, 18, 21, 37-40 |
| B02 | **Control.** HP (historia y exploración); TXA-17 LA, TXA-18 V; cuatro OBX TX con OBX-3 (`2000.40^MOTIVO`, `2000.02^ENFERMEDAD ACTUAL`… como `[E9 CH09.txt:1976-1980]`) y OBX-4 | LA → final; V; varios OBX de TX | 9, 10, 18 |
| B03 | **Control.** CN (consulta); TXA-17 PA, TXA-18 U; un OBX FT con `\.in+4\\.ti-4\ … \.br\` (como `[E2 CH02.txt:1091-1095]`) | PA → preliminary; U; FT | 9, 10, 22-24 |
| B04 | **Control.** OP (informe operatorio); TXA-17 IP; **TXA-19 vacío**; un OBX TX con cuatro repeticiones `~` | IP; vacío → `current`; salto entre repeticiones | 7, 9, 18, 19 |
| B05 | **Control.** PN (nota de procedimiento); TXA-3 AP; un OBX ED `^AP^RTF^Base64^<b64>` | ED en Base64, subtipo RTF | 25, 27 |
| B06 | **Control.** PR (nota de evolución); TXA-3 IM; un OBX RP `<ptr>^^IM^JPEG` | RP: url y contentType | 30, 31 |
| B07 | **Control.** DI (diagnóstico por imagen); TXA-3 IM; un OBX ED `^IM^JPEG^Base64^<b64>` | ED imagen | 25, 27 |
| B08 | **Control.** TS (traslado); **sin COMMON_ORDER**; TXA-17 DI; un OBX TX | DI → preliminary; sin ServiceRequest | 1, 9, 37 |
| B09 | PN con TXA-17 DO y TXA-19 AV | DO | 9 |
| B10 | CN con TXA-17 IN y **TXA-19 UN** | IN; UN → solo extensión | 8, 9 |
| B11 | CN con TXA-17 AU y **TXA-19 CA** (borrado) | CA → `entered-in-error` o extensión | 8 |
| B12 | PR con TXA-17 LA y **TXA-19 OB** (obsoleto) | OB → `superseded` o extensión | 8 |
| B13 | ED `^AP^Octet-stream^Base64^` con TXA-3 AP | contentType desde ED.3 (`octet-stream`) | 25, 27 |
| B14 | ED `^TEXT^XML^A^<texto XML con \T\ y \S\>` con TXA-3 TEXT | ED.4 = A: ASCII con escapes de delimitador | 26 |
| B15 | ED `^AP^PostScript^Hex^<dígitos hex>` | ED.4 = Hex → Base64 | 26 |
| B16 | ED `^IM^^Base64^<b64>` (**sin ED.3**) | ED.2 → extensión; sin contentType esperado | 25, 27 |
| B17 | ED CDA `^multipart^x-hl7-cda-level-one^Base64^<b64>` (como `[E7 CH07.txt:2650-2652]`), TXA-3 multipart | CDA como ED, sin interpretarlo | 25, 27 |
| B18 | **Dos repeticiones** de ED en un OBX-5 (`ED~ED`, JPEG y GIF) | una `content` por repetición | 28 |
| B19 | **Dos repeticiones** de RP en un OBX-5 | una `content` por repetición | 32 |
| B20 | Documento largo: 12 OBX TX con repeticiones (≈ 60 líneas) y anclas | «llega entero»; varios OBX; orden | 18, 19 |
| B21 | FT con `\H\…\N\`, `\.sp\`, `\.ce\`, `\.nf\` | FT: órdenes de formato | 22, 23 |
| B22 | TX con `\F\ \S\ \T\ \R\ \E\` y `ñ`/`í` con MSH-18 `UNICODE UTF-8` | desescape de delimitadores; UTF-8 | 20 |
| B23 | **Mixto TX + ED**: dos OBX TX y un OBX ED Base64 (informe con imagen) | `content` múltiples de tipos distintos | 18, 25, 28 |
| B24 | **Mixto TX + FT + RP** | TX, FT y RP juntos | 18, 22, 30 |
| B25 | OBX **CE y ST** estructurados (como `[E9 CH09.txt:1976-1980]`) más dos TX | OBX sin destino (nota); recuento `obx_sin_destino` | 35 |
| B26 | OBX TX con un **NTE** (NTE-3 de una línea) | NTE bajo OBX → `content` | 33 |
| B27 | OBX FT con **dos NTE** (NTE-3 con repeticiones) y NTE-4 | NTE múltiples | 33 |
| B28 | **Dos** grupos ORC/OBR (con TQ1), números distintos | ServiceRequest ×2; `context.related` | 16, 37-40 |
| B29 | **Tres** grupos (escenario B de `[E9 CH09.txt:312-314]`), mismo OBR-4 y números de placer y de filler distintos | emparejamiento por identifier; «todos o el primero» | 16, 37-39 |
| B30 | Un grupo con **ORC-2/3 vacíos** y OBR-2/3 valorados, y **NTE bajo OBR** | los números salen del OBR (AMB-CV-8); NTE de OBR → nota | 39, 42 |
| B31 | TXA-14 y TXA-15 valorados además de los de ORC/OBR | ignorar los de TXA (`[E9 CH09.txt:242-246]`) | 39 |
| B32 | ORC-5, ORC-12 y OBR-16 (solicitante) valorados | status/intent sin esperado; solicitante: nota | 41, 42 |
| B33 | TXA-4, TXA-6 con hora y zona, TXA-7 y **TXA-8 ×2**, TXA-5 (condicionado a TXA-4) | `date` por instante; los demás sin destino | 11 |
| B34 | **TXA-6 solo fecha** | `date` ausente (R6 no disponible) | 11 |
| B35 | TXA-9 ×2, TXA-10 ×2, TXA-5 y TXA-11 | `author[]`; `authenticator` 0..1 | 12, 13 |
| B36 | TXA-12 con EI.2-EI.4 (`DOC0036^CSSYN^1.2.840.113619.2.1^ISO`) y TXA-16 con ruta de Windows `C:\E\docs\E\b36.rtf` | assigner/system; ruta completa desescapada | 3-5 |
| B37 | TXA-13, TXA-21, TXA-22 y TXA-23 valorados en un T02 | campos sin destino: nota | 45 |
| B38 | TXA-2 **local** (`ZX`, user-defined) y TXA-18 vacío | `type` literal sin `system`; sin `securityLabel` | 6, 10 |
| B39 | PID con dos identificadores, SFT, EVN-4, MSH-18 UTF-8 y `ñ` en PID-5 y TXA-9 | segmentos sin mapa; UTF-8 en nombres | 12, 43, 45 |
| B40 | **Documento mínimo**: solo TXA-1, 2, 3, 12 y 17, `PV1|1|O`, un OBX TX, **sin COMMON_ORDER**, TXA-19 vacío | todos los opcionales vacíos | 1, 7, 9, 44 |

**Cobertura** (afirmada por `bases_mdm.py --cobertura` contra `PERFIL_GUIA_MDM`): toda fila de nivel **cuenta** tiene al menos una base con el campo valorado y, si es opcional en 2.5, una con el campo vacío; la
0271 entera (AU B01 y otras, LA B02, PA B03, IP B04, DI B08, DO B09, IN B10), la 0272 (R, V, U y vacío), la 0273 (AV, vacío, UN, CA, OB), la 0299 (A B14, Hex B15, Base64), los cuatro tipos con destino (TX, FT, ED, RP) y
dos sin él (CE, ST), 0, 1, 2 y 3 grupos de orden, 0, 1 y 2 NTE bajo OBX, y 0, 1 y 2 TXA-9 y TXA-10.

**Corpus secundario (solo con Q-MD-D-1 b):** `bases_mdm.py --secundario` escribe `S01..S04` (T04, T06, T08, T10) derivadas de B01, B02, B05 y B08 con MSH-9.2, EVN-1 y, en T06 y T10, TXA-13 (obligatorio,
`[E9 CH09.txt:1417-1421]`). No entran en las 40, ni en la huella, ni en `n["mdm"]`.

### 5.3 Cómo se genera (`verificador/bases_mdm.py`, forma de `bases_vxu.py`)

```
def msh(n, ver="2.5", ev="T02", est="MDM_T02", msh18=""): ...     # MSH-7 distinto por base; MSH-10 "MDM-B%02d"
PIDS = {"mateo": "PID|1||DOC0001^^^CSSYN^MR||Prueba^Mateo^^^^^L||20230512|M", ...}       # seis ficticios, dos con segunda repetición PI
PROF = {1: "PR01^Ensayo^Ana^^^Dra", 2: "PR02^Muestra^Jorge", 3: "PR03^Patron^Irene", 4: "PR04^Plantilla^Raul"}
def txa(n, tipo, pres="TEXT", **campos): ...     # TXA-1..23 desde {número: valor}; valores por omisión vacíos salvo 1, 2, 3, 12, 17
def orc(n, g, placer="", filler="", **campos): ...; def obr(n, g, placer="", filler="", cod="DOC-DS^Informe de alta^L"): ...; def tq1(...): ...
def obx_tx(k, cod, lineas): ...   # lineas -> OBX-5 con "~" entre líneas; escapes en el texto ya puestos por quien llama
def obx_ft(k, cod, texto): ...    def obx_ed(k, cod, ed2, ed3, ed4, carga): ...    def obx_rp(k, cod, ptr, rp3, rp4): ...    def obx_ce(...): ...    def obx_st(...): ...
def nte(j, texto): ...
def carga(n, sufijo): return ("SINTETICO-%02d-%s" % (n, sufijo)).encode()          # el binario de un ED; b64/hex/ascii se calculan aquí
def ancla(n, k, j=0): return "Zeta%02d%02d%02d" % (n, k, j)                         # palabra única que acompaña a cada OBX
def base(n, descripcion, ejercita, campos, segs): ...
def construir(): ... 40 bases; assert ids B01..B40
BASES = construir()
def cable(b): return "\r".join(b["segmentos"]) + "\r"
def firma(): ...        # pares con < 3 campos distintos, o que solo difieren en los campos ejercitados
def cobertura(): ...    # filas «cuenta» de PERFIL_GUIA_MDM con base valorada y vacía; tablas; grupos; NTE
def autoprueba(): ...   # §5.1.4 + firma + cobertura + determinismo + huella fijada
def escribir(): ...     # bases_mdm/BNN.hl7 + bases_mdm.jsonl
```

Uso: `python3 bases_mdm.py` escribe; `--lista`, `--firma`, `--cobertura`, `--secundario`, `--autoprueba`. Solo biblioteca estándar. `bases_mdm.py` no importa `conversion_mdm` salvo para `--cobertura` (lee
`PERFIL_GUIA_MDM`, datos, no juicio), de modo que un error del perfil no se confirme a sí mismo. Las cargas se generan aquí con `base64.b64encode`/`binascii.hexlify`, **no** se escriben a mano.

### 5.4 Las variantes, de un vistazo

| Dimensión | Variantes en el corpus (bases) |
|---|---|
| OBX-2 con destino | TX (la mayoría), FT (B03, B21, B24, B27), ED (B05, B07, B13-B18, B23), RP (B06, B19, B24) |
| OBX-2 sin destino | CE y ST (B25) |
| Contenido de texto | una línea (B01); varios OBX (B02, B20, B23); repeticiones con `~` (B04, B20); FT con formato (B03, B21); escapes de delimitador y UTF-8 (B22, B14); NTE bajo OBX (B26, B27) |
| ED | Base64 (B05, B07, B13, B16-B18, B23), A (B14), Hex (B15); subtipos RTF, JPEG, Octet-stream, PostScript, XML, CDA; sin ED.3 (B16); dos repeticiones (B18) |
| RP | una (B06, B24), dos (B19) |
| TXA-17 / TXA-19 / TXA-18 | AU, LA, PA, IP, DI, DO, IN / AV, vacío, UN, CA, OB / R, V, U, vacío |
| TXA-3 | TEXT, AP, IM, multipart |
| TXA-2 | DS, HP, CN, OP, PN, PR, DI, TS, local `ZX` |
| TXA-6 / TXA-12 / TXA-16 | hora y zona (B01, B33), solo fecha (B34); `CSSYN`, con EI.2-4 (B36); ruta Unix, ruta con `\E\` (B36) |
| TXA-9 / TXA-10 | 0, 1 y 2 repeticiones (B35) |
| Grupos de orden | 0 (B08, B40), 1 (la mayoría), 2 (B28), 3 (B29); números en ORC (la mayoría) o solo en OBR (B30) |

---

## 6. La previsión sellada

### 6.1 Forma

Antes de correr nada, MD2 escribe y sella `prevision-mdm.json` con: la huella del juez, la huella de `bases_mdm` (`por_corpus["mdm"]` del manifiesto), y por conversor: `corre_en_caja` (**dato ya medido en MD-pre, E-MD-3:
no es una probabilidad**), los rangos de `correcto` / `fallo_silencioso` / `rechazo_incorrecto` / `indeterminado` sobre las 40 bases, la lista de mecanismos MC-MD-n con `{hecho, subtipo, ruta FHIR, probabilidad,
bases_que_lo_disparan, depende_de}` (donde `depende_de` es la Q o las Q de las que depende que cuente), la probabilidad de **≥ 1 nueva confirmada**, el efecto previsto de cada alternativa preinscrita (`ALTERNATIVA_MD`) y las reglas
de «fuera de previsto». La tabla de §6.2 es la versión de hoy, a ciegas; MD2 solo le añade las cuentas de E-MD-3 y del corpus (n por mecanismo) antes de sellar. Los mecanismos se escribieron **sin haber visto** ninguna salida: salen de
lo que el estándar y la guía dicen distinto o callan.

### 6.2 Mecanismos previstos (A alta, M media, B baja; la cita es la del perfil que lo juzga)

| Id | Mecanismo (hecho, subtipo) | Microsoft | LinuxForHealth | Depende de | Bases que lo disparan |
|---|---|---|---|---|---|
| MC-MD-1 | TXA-17 → `docStatus` con el código de la 0271 tal cual (`AU`, `LA`…) fuera de `composition-status`, o ausente (`fhir_invalido`/`dato_perdido` `TXA-17`) | M-A | M-A | Q-MD-D-4 | las 40 |
| MC-MD-2 | TXA-19 vacío sin `current`, o CA/OB/UN con `status` `current` y sin el código en la extensión (`valor_distinto`/`fhir_invalido`/`dato_perdido` `TXA-19`) | M | M | Q-MD-D-9 | B04, B10-B12, B40 |
| MC-MD-3 | TXA-2 → `type` con solo `text`/`display`, o con un código LOINC sin el original (`dato_perdido`/`valor_distinto` `TXA-2`) | M | M | — | las 40 |
| MC-MD-4 | TXA-12 → `masterIdentifier` ausente (queda en `identifier`) o con el namespace concatenado al `value` (`dato_perdido`/`valor_distinto` `TXA-12`) | M-A | M | — | las 40, B36 |
| MC-MD-5 | TXA-16 perdido o con la ruta truncada o sin desescapar (`dato_perdido`/`valor_distinto` `TXA-16`) | M | M | — | B01, B36 |
| MC-MD-6 | TXA-6 → `date` con `T00:00:00` inventado, sin zona o ausente con hora (`dato_inventado`/`fhir_invalido`/`dato_perdido` `TXA-6`) | M | M | — | B33, B34, las de TXA-6 con hora |
| MC-MD-7 | TXA-9/TXA-10 → `author`/`authenticator` ausentes, solo `display`, intercambiados o desde TXA-22 (`dato_perdido`/`valor_distinto` `TXA-9`/`TXA-10`) | M-A | M | Q-MD-D-11 | B01, B35, B39 |
| MC-MD-8 | TXA-18 → `securityLabel` ausente o con código perdido (`dato_perdido`/`codigo_mal_mapeado` `TXA-18`); el sistema v3 es convención | M | M | AMB-MD-20 | B01-B03 |
| MC-MD-9 | OBX TX/FT: texto sin Base64 (`fhir_invalido`) o solo el primer OBX o la primera línea (`dato_perdido` `OBX-5`) | M | M | — | B02, B04, B20, B23, B24 |
| MC-MD-10 | Repeticiones de OBX-5 unidas sin salto de línea (`valor_distinto` `OBX-5`) | M | M | — | B04, B20 |
| MC-MD-11 | `contentType` de TX/FT: `text/plain` frente a `application/text`/`text/hl7v2` (`valor_distinto` `OBX-2`); con ausencia (`dato_perdido`) | M-A | M-A | **Q-MD-D-3** | todas las de TX y FT (≈ 30) |
| MC-MD-12 | Escapes sin resolver en TX (`\T\`, `\F\`) o órdenes de formato crudas en `text/plain` (`valor_distinto` `OBX-5`) | B-M | M | — | B03, B21, B22 |
| MC-MD-13 | ED: `contentType` derivado de ED.2 (`image`, `application` sin subtipo) o ausente (`valor_distinto`/`dato_perdido` `OBX-2`) | M | M | Q-MD-D-3 | B05, B07, B13-B18, B23 |
| MC-MD-14 | ED: A o Hex sin convertir a Base64, o Base64 codificado dos veces (`valor_distinto` `OBX-5`) | M | M | — | B14, B15 (A, Hex); B05, B07, B13 (doble) |
| MC-MD-15 | RP: `url` con prefijo o perdido; `contentType` sin subtipo (`valor_distinto`/`dato_perdido` `OBX-5`/`OBX-2`) | M | M | — | B06, B19, B24 |
| MC-MD-16 | Varios OBX → varias DocumentReference (`recurso_duplicado` `TXA-12`) o un `content` que mezcla dos (`dato_perdido`) | M | B-M | Q-MD-D-5 | B02, B20, B23, B24 |
| MC-MD-17 | OBX → Observation en lugar de `content` (`dato_perdido` `OBX-5` y `fhir_invalido` por `content` ausente) | B-M | B-M | Q-MD-D-8 | B02, B25 |
| MC-MD-18 | NTE bajo OBX perdidos (`dato_perdido` `NTE-3`) | M-A | M-A | — | B26, B27 |
| MC-MD-19 | ORC/OBR: ServiceRequest ausente, o DocumentReference sin `context.related` (`recurso_ausente`/`dato_perdido` `ORC-1`) | M-A | M | Q-MD-D-7, Q-MD-D-10 | B01, B28, B29, B30 |
| MC-MD-20 | `ServiceRequest.identifier` sin PLAC/FILL o con tipos intercambiados (`dato_perdido`/`codigo_mal_mapeado` `ORC-2`/`ORC-3`) | M | M | — | B01, B28-B31 |
| MC-MD-21 | PV1 sin Encounter (`recurso_ausente` `PV1`), o sin la referencia al Patient | B-M | B-M | — | las 40 |
| MC-MD-22 | Rechazo (`error`) de un MDM_T02 válido (EVN, TQ1, SFT, un ED grande) (`rechazo_incorrecto`) | B | B-M | — | B05, B14-B17, B39 |

### 6.3 Previsión agregada (lo que MD2 debe encontrar, con cota)

| Conversor | Corre MDM_T02 en la caja (E-MD-3, de MD-pre) | `correcto` | `fallo_silencioso` | `rechazo_incorrecto` | `indeterminado` | Mecanismos que cuentan (distintos) | ≥ 1 **nueva confirmada** tras MD3 |
|---|---|---|---|---|---|---|---|
| Microsoft (40 bases) | dato | 0-15 % | 80-100 % | 0-15 % | ≤ 3 % | 6-12 | 0,75 |
| LinuxForHealth (40 bases) | dato | 0-15 % | 80-100 % | 0-15 % | ≤ 3 % | 6-12 | 0,75 |
| Muestras públicas de los proyectos (E-MD-2; v2.8 y v2.3 en su mayoría) | — | se juzgan con banderas L18; ≥ 70 % de lo que cuente será `ya_declarada` o `convencion` | | | | | — |

- Al menos una nueva confirmada en **alguno** de los dos: **0,85**. Frase fija prevista: N ≥ 3, K ∈ {1, 2}, D ≥ 2, C ≥ 10 (las convenciones serán: `text/plain`, v3-Confidentiality, número y orden de `content[]`, `Binary`,
  `system` de `type`, forma de `author`, `display`, Provenance/MessageHeader).
- La más probable de las nuevas: **MC-MD-1** (TXA-17 → `docStatus`), porque la guía no trae mapa y R4 lo exige; si Q-MD-D-4 sale en (a) o (c), baja a nota y la más probable pasa a **MC-MD-2** (TXA-19 CA/OB/UN) o a **MC-MD-18**
  (NTE bajo OBX, que la guía mapea a un `content` que ningún conversor por plantilla suele crear).
- **Fuera de previsto** = un mecanismo que cuente y no esté en §6.2; un porcentaje fuera de su rango; `indeterminado` > 3 % (lector/emparejador); un conversor que rechace > 15 % del corpus 2.5. Cada uno se adjudica
  (juez / perfil / corpus / caja) con cita antes de MD3.
- **Lo que no preveo** (y si aparece, es la señal): un `recurso_inventado` de DocumentReference, una `referencia_rota` en `subject`, un `fhir_invalido` masivo por Base64 (R-MD-34) o un `indeterminado/emparejamiento` en B29
  (tres grupos con el mismo OBR-4).
- **Sensibilidad preinscrita:** las Q que Jev deje con confianza ≤ 0,52 entran en `ALTERNATIVA_MD` y MD2 da también la N con la alternativa de cada una (`con_alternativas`, `conversion.py:1616-1618`, extendido a
  `CVM.ALTERNATIVA_MD`). Si una discrepancia «nueva» depende solo de una de ellas, se dice en la frase.

---

## 7. Lo que cambia en la herramienta (`cv/verificar_conversor.py`, `cv/conversor_juguete.py`)

Hoy: `punto(t)` decide solo por MSH-9.1: `ORU → oru_conv`, `VXU → vxu_conv`, lo demás → `adt_conv` (`verificar_conversor.py:395-400`, S-VC-22 y S-VX-13); el corpus es
`CORPUS = ("adt", "oru", "vxu", "muestras", "minimos", "propio")` (`:50`) y `generar_corpus` escribe por carpeta, con una huella por corpus y una huella conjunta
`huella_adt_oru_muestras` que no incluye `vxu` (`:416-469`, `:455-456`); `L-VC-2` dice que solo juzga ADT, ORU y VXU (`:67`).

| Pieza | Cambio | Lo que no cambia (y cómo se afirma) |
|---|---|---|
| `punto(t)` | `"oru_conv" if ORU else "vxu_conv" if VXU else "mdm_conv" if c[0].upper().startswith("MDM") else "adt_conv"` | ADT, ORU, VXU, SIU, ORM… dan lo mismo que hoy; P-MD-24 repite `prueba_vc.p07` (`prueba_vc.py:356-370`, `{"a": "adt_conv", "b": "oru_conv", "s": "adt_conv"}`) y añade `"v": "vxu_conv"` y `"m": "mdm_conv"` |
| `CORPUS` | `("adt", "oru", "vxu", "muestras", "minimos", "propio", "mdm")`: **`mdm` al final**, para que `CORPUS.index(...)` de los seis existentes (clave de orden de la corrida, `:610`) no cambie | las carpetas `adt`, `oru` y `vxu` se escriben con los mismos ficheros: `por_corpus["adt"]`, `["oru"]`, `["vxu"]` y `huella_adt_oru_muestras` idénticas a las de hoy (`:455-456` solo cuenta `adt`, `oru`, `muestras`); la huella conjunta `huella` cambia (incluye `mdm`): cambio declarado, como con VXU |
| `generar_corpus(lab=True)` | `import bases_mdm as BM` junto a `:35` y `textos["mdm"] = [("MDM-%s.hl7" % b["id"], normal(BM.cable(b))) for b in BM.BASES]` tras `:424` | `n["adt"] = 263`, `n["oru"] = 40`, `n["vxu"] = 40` iguales; el recuento total sube en 40: `prueba_vc.p06` pasa de `"vxu": 40` a añadir `"mdm": 40` (`:333`) y «sin mínimos» de 343 a 383 (`:353`): cambio declarado |
| `plantilla(t, regla)` | nada: `msh9_tipo_evento` ya da `MDM_T02` (`:403-412`) | `prueba_vc.p08` igual |
| `L_VC["L-VC-2"]` | «Solo juzga lo que juzgan adt_conv, oru_conv, vxu_conv y mdm_conv: ADT de los ocho eventos, ORU^R01, VXU^V04 y MDM^T02…» | — |
| `agregar` / `informe_md` / `comprobar_informe` | nada en el código: iteran `CORPUS` y `CLASES8` (`:53-54,897`); aparece la fila `mdm` | la fila `adt`/`oru`/`vxu` del informe no cambia para el mismo corpus |
| `pares_minimos` | los pares mínimos de MDM (MD3) van en `cv3_minimos_mdm.PARES`, lista aparte, y entran solo si el corpus lleva `mdm` | `MIN.PARES` (los 68) no cambia de tamaño ni de contenido |
| `juzgar` | nada: `V.verificar(e)` despacha por el PE de la evidencia | — |
| `conversor_juguete.py` | `nominal(m)` (`:201-203`) gana `mdm_nominal()` para MSH-9.1 = MDM (Patient + Encounter + DocumentReference + ServiceRequest, a mano, copiado de `prueba_conversion_mdm.py`); directivas nuevas `JUGUETE-DOCSTATUS` (el nominal con `docStatus` = el código literal de TXA-17: control positivo de MC-MD-1) y `JUGUETE-TEXTO` (el nominal con el `data` de TX truncado a la mitad: control positivo de R-MD-18), añadidas en `_convertir` (`:221-256`) | las directivas de hoy (`:13-25`) y sus Bundles ADT/ORU/VXU no se tocan; `JUGUETE-RUTA` sigue siendo de VXU (`:228-229`) |
| `adaptador.json` de los dos conversores | nada obligatorio; `declara.no_soporta` puede listar `MDM^T02` si un conversor no trae plantilla (`:190-192`, `:925-932`) | — |

**Qué pasa con los MDM que ya estaban en `muestras`** (los 3 de Microsoft, los de LinuxForHealth): hoy van a `adt_conv` y salen `fuera_de_alcance`; con el cambio van a `mdm_conv` y se juzgan (T02) o siguen
`fuera_de_alcance` (T01, T03… y T04, T06, T08, T10 según Q-MD-D-1). **No es un cambio de veredicto de ADT, ORU o VXU**: P-MD-25 cuenta cuántos MDM hay en `muestras` y exige que sean los únicos que cambian de `punto`.
Un `error` del conversor por «sin plantilla» (`:803`, L-VC-13 en `:86`) para `MDM_T02` es `sin_plantilla` sin entrar en la caja y se contabiliza como «no corre MDM_T02» en E-MD-3.

---

## 8. Pruebas en rojo antes del código (P-MD-n)

Todas en `verificador/prueba_conversion_mdm.py` (forma de `prueba_conversion.py:21-194`: `mira`, `seg`, `msg_mdm(...)`, Bundles escritos **a mano**, `ev(m, b, pe="mdm_conv")`, `cuentan`, `notas`). «Hoy» = sin el PE y sin
`conversion_mdm`: `PE.resolver` lanza `ValueError` (`puntos_entrada.py:181-182`) y todas fallan por construcción (`prueba_conversion_mdm.py rojo` sale 0 solo si fallan todas, **salvo las dos líneas base**: P-MD-1 (`mdm` de acuse
intacto) y P-MD-25 (a), que pasan hoy y deben seguir pasando). El control negativo es lo que debe seguir dando `correcto` o `0 hallazgos que cuentan`, o el subtipo exacto previsto.

| P | Pieza | Caso | Esperado | Control negativo |
|---|---|---|---|---|
| P-MD-1 | PE, gramática, evidencia | `PE.estructura_de(m, PUNTOS["mdm_conv"])` = `MDM_T02` para MDM^T02; `contrato(PUNTOS["mdm"])` (JSON) igual que antes de añadir el PE; B01 con su Bundle exacto (Patient, Encounter, DocumentReference con `content`, ServiceRequest, todos con las referencias) | `correcto`, `cuenta = []`, `recuentos = {Patient: 1, Encounter: 1, DocumentReference: 1, ServiceRequest: 1, txa: 1, obx: 1, grupos_orden: 1, …}` | `docStatus "entered-in-error"` con TXA-17 AU → `fallo_silencioso/convertido`, `[("fidelidad", "valor_distinto", "TXA-17")]` |
| P-MD-2 | R-MD-9 `docStatus` | cada código de la 0271 con su valor del `MAPA_0271` (LA→final; AU→final y →preliminary; PA, IN, IP, DI, DO→preliminary) | 0 cuentan en los siete | PA→`final` → `valor_distinto` TXA-17; DI→`entered-in-error` → `valor_distinto`; `docStatus` ausente → `dato_perdido`; presente con TXA-17 vacío → `dato_inventado`; el literal `AU` → según `DECISIONES_MD["Q-MD-D-4"]`; `docStatus "XX"` → `fhir_invalido+valor_distinto` fusionados en TXA-17 |
| P-MD-3 | R-MD-7/8 `status` | TXA-19 vacío y AV → `current`; CA con extensión `http://hl7.org/fhir/StructureDefinition/alternate-codes` (y con `https://`) y `valueCodeableConcept` `CA`; CA con `status entered-in-error` y sin extensión; OB con `superseded`; UN con extensión | 0 cuentan | AV con `superseded` → `valor_distinto` TXA-19; CA con `current` y sin extensión → `dato_perdido` TXA-19; `status "active"` → `fhir_invalido`; `status` ausente → `fhir_invalido` |
| P-MD-4 | R-MD-3/4/5 identificadores | TXA-12 `DOC0001^CSSYN` → `masterIdentifier.value DOC0001` con `system`; con EI.2-4 → `assigner` o `system` con el OID; TXA-16 `C:\E\docs\E\x.rtf` → `identifier.value "C:\docs\x.rtf"` | 0 cuentan | `masterIdentifier` ausente → `dato_perdido` TXA-12; `value "DOC0001^CSSYN"` → `valor_distinto`; EI.3 valorado y ni `system` ni `assigner` → `dato_perdido`; TXA-16 `x.rtf` (truncado) → `valor_distinto` TXA-16; `identifier` propio → nota `extra` |
| P-MD-5 | R-MD-6 `type` y R-MD-14 TXA-3 | TXA-2 `DS` → `type.coding.code DS` (con y sin `system`); TXA-2 local `ZX`; TXA-3 TEXT con un attachment `contentType text/plain` | 0 cuentan | `type` solo con `text` → `dato_perdido` TXA-2; `coding` LOINC sin `DS` → `valor_distinto`; `type` sin TXA-2 → `dato_inventado`; TXA-3 valorado y ningún `contentType` → `dato_perdido` TXA-3 |
| P-MD-6 | R-MD-10 `securityLabel` | V, R, U → `{v2-0272, V}`; también `{v3-Confidentiality, R}` | 0 cuentan | `{v2-0272, R}` con TXA-18 V → `codigo_mal_mapeado` TXA-18; ausente → `dato_perdido`; label sin TXA-18 → nota `extra` |
| P-MD-7 | R-MD-11 `date` | TXA-6 `20230109101500+0100` → `2023-01-09T09:15:00Z` y `…T10:15:00+01:00`; solo fecha (TXA-6 `20230109`) → `date` ausente, o `2023-01-09T00:00:00+01:00` (nota AMB-CV-9); sin TXA-6 y `date` = MSH-7 → nota | 0 cuentan | solo fecha con `date` `2023-01-10T00:00:00+01:00` (otro día) → `valor_distinto`; hora sin zona → `fhir_invalido`; hora cambiada → `valor_distinto`; hora perdida (`2023-01-09` con TXA-6 que trae hora) → `dato_perdido` (`conversion.py:503-505`); sin TXA-6 y `date` ajeno → `dato_inventado` |
| P-MD-8 | R-MD-12/13 profesionales | TXA-9 `1234^Goldstein^Harold^A^^DR` → `author` con Practitioner (`identifier 1234`, `family Goldstein`); también vía `PractitionerRole`; TXA-10 con dos repeticiones y `authenticator` con la segunda | 0 cuentan | `author` solo `display` con XCN.1 → `dato_perdido`; `authenticator` con la persona de TXA-9 → `valor_distinto`; actor Organization → `dato_perdido`; `author` a un id inexistente → `referencia_rota`; `authenticator` sin TXA-10 → `dato_inventado` |
| P-MD-9 | R-MD-18/19/20 TX | un OBX TX con cuatro repeticiones → un `data` Base64 con las palabras en orden y LF (y con CR LF); dos OBX TX en dos `content` y en uno solo; texto con `\T\` → `&` | 0 cuentan | `data` con las cuatro líneas separadas por espacio → `valor_distinto` OBX-5 (R-MD-19); `data` sin la última línea → `dato_perdido` OBX-5; las líneas en otro orden → `valor_distinto`; el literal `\T\` en el texto → `valor_distinto` (R-MD-20); `data` en texto crudo → `fhir_invalido` y no además `dato_perdido` |
| P-MD-10 | R-MD-21/24 `contentType` de TX y FT | TX con `application/text` (a, b, c) y con `text/plain` (b, c); FT con `text/hl7v2` | 0 cuentan según `DECISIONES_MD["Q-MD-D-3"]` | `application/pdf` en un TX → `valor_distinto` OBX-2; sin `contentType` → `dato_perdido` OBX-2; `text/plain` con Q (a) → `valor_distinto` |
| P-MD-11 | R-MD-22/23 FT y R-MD-33 NTE | FT con `\.br\` y `\H\…\N\` → `data` con las palabras (con las órdenes crudas y `text/hl7v2`; sin ellas y `text/plain`); NTE-3 de un OBX en su `content` | 0 cuentan | `\.br\` crudo con `text/plain` → `valor_distinto` OBX-5; NTE perdido → `dato_perdido` NTE-3; FT sin el último párrafo → `dato_perdido` |
| P-MD-12 | R-MD-25/26/27/28/29 ED | ED Base64 → mismo `data`; ED A (con `\T\` desescapado) y ED Hex → `data` Base64 de sus octetos; `contentType image/jpeg` con ED.3 JPEG, `application/postscript`, `text/xml` y `application/xml` con XML, `application/x-hl7-cda-level-one+xml`; ED.3 vacío → sin esperado; dos repeticiones → dos attachments; `Binary` referenciado con los mismos octetos | 0 cuentan | `data` codificado dos veces → `valor_distinto` con su causa; Hex sin convertir → `valor_distinto`; `image/png` con ED.3 JPEG → `valor_distinto` OBX-2; sin attachment → `dato_perdido`; solo uno de dos → `dato_perdido`; ED.5 inválido y el conversor lo escribe → `valor_imposible_convertido` |
| P-MD-13 | R-MD-30/31/32 RP | `ptr-0006^^IM^JPEG` → `url "ptr-0006"` y `contentType image/jpeg` o `IM/JPEG`; dos repeticiones; `https://repo.ejemplo/ptr-0006` → nota | 0 cuentan | `url` ausente → `dato_perdido` OBX-5; `url` distinta → `valor_distinto`; `contentType application/pdf` → `valor_distinto` OBX-2 |
| P-MD-14 | R-MD-17/34 | DocumentReference sin `content` con OBX TX → `fhir_invalido` y **un solo** hallazgo (absorbe los `dato_perdido`); `content` sin `attachment`; un `data` con caracteres no Base64 | `fhir_invalido` | un `content` completo → 0 hallazgos; solo OBX CE/ST y sin `content` → nota `sin_content_posible`, 0 cuentan |
| P-MD-15 | R-MD-1/2 emparejamiento de DocumentReference | un TXA y una DocumentReference → `emparejado_por master`; dos DocumentReference (una por OBX) con el mismo `masterIdentifier` → la primera emparejada y la otra `recurso_duplicado` TXA-12, con el `content` sumado; un TXA y ninguna → `recurso_ausente` | `correcto` solo en el primero | `DocumentReference` sin TXA (mensaje con un TXA y dos) y sin claves comunes → `recurso_duplicado`; dos TXA y una sola → `recurso_ausente` `TXA(2)-12` |
| P-MD-16 | R-MD-15/16 referencias | `subject` y `context.encounter` resuelven; `subject` ausente → nota `sin_subject`; `related` a los ServiceRequest (todos o el primero según Q-MD-D-7) | 0 cuentan | `subject` a otro Patient → `referencia_rota`; `subject` a un id inexistente → `referencia_rota`; `related` ausente con un grupo → `dato_perdido` ORC-1; `related` a un id inexistente → `referencia_rota`; `context.encounter` sin PV1 → `dato_inventado`; Q-MD-D-6 (b): `subject` ausente → `dato_perdido` |
| P-MD-17 | R-MD-37..41 ServiceRequest | un grupo con ORC-2/3 → `identifier` PLAC/FILL; grupo con ORC-2/3 vacíos y OBR-2/3 → los del OBR; OBR-4 `DOC-DS^Informe de alta^L` → `code`; `status`/`intent` cualquiera válido | 0 cuentan | PLAC y FILL intercambiados → `codigo_mal_mapeado` ORC-2 y ORC-3; `identifier` ausente → `dato_perdido`; `code` ausente → `dato_perdido` OBR-4; `status "foo"` → `fhir_invalido`; ServiceRequest de más → `recurso_inventado`; ausente → `recurso_ausente` `ORC-1`; tres grupos con el mismo OBR-4 y dos ServiceRequest iguales → `indeterminado/emparejamiento` |
| P-MD-18 | R-MD-35/36 y OBX sin destino | OBX CE y ST sin rastro en el Bundle; un `Observation` por OBX | 0 cuentan; `obx_sin_destino = 2`; `otros_tipos = {"Observation": n}` | con Q-MD-D-12 (b), el CE sin rastro → `dato_perdido`; con Q-MD-D-8 (b), un `Observation` → `recurso_inventado` |
| P-MD-19 | R-MD-43/44 Patient y Encounter | los de ADT (PID-3, 5, 7, 8, 11, 13, 16, 29/30; PV1-2, 4, 10, 19, 44/45); PV1 ausente en el Bundle | 0 cuentan en el nominal | PV1-2 `I` → `{v2-0004, I}` → `codigo_mal_mapeado`; sin Encounter → `recurso_ausente` `PV1`; con PV1-2 = N, según Q-CV-D-6; dos Patient → `recurso_duplicado` |
| P-MD-20 | eventos | MDM^T01, T03, T05, T07, T09, T11 → `fuera_de_alcance`; MDM^T04/T06/T08/T10 según Q-MD-D-1; QRY^T12 y ACK^T02 → `fuera_de_alcance` | las categorías previstas | MDM^T02 con MSH-9.3 `MDM_T01` → `correcto` + nota `estructura_declarada` (no cuenta) |
| P-MD-21 | estructura y versión | MSH-9.3 vacío → nota; MSH-12 2.5.1 con TXA-17 `XX` → nota `version` L18, 0 cuentan; OBX antes del TXA → `obx_fuera_txa = 1`; segundo TXA → nota `estructura` y segunda DocumentReference esperada; TXA sin OBX → nota | según | MSH-12 2.5 con TXA-17 `XX` y `docStatus "XX"` → cuenta (`valor_imposible_convertido` + `fhir_invalido`) |
| P-MD-22 | `error` y rechazos | `error` con TXA-6 `20261301` (DTM imposible), TXA-17 `XX`, TXA-19 `ZZ`, ED.4 `Base64` con ED.5 `***`, ED.4 `Hex` con `ABC`, OBX-2 `ZZ`, PID sin PV1, TXA-12 vacío → `correcto` + nota `aceptable`; `error` con B01 → `rechazo_incorrecto` | según | `error` con un MDM válido que lleva SFT y TQ1 → `rechazo_incorrecto`; `error` sin PID → `correcto` + `aceptable` |
| P-MD-23 | las ocho clases | nueve mutaciones, una por subtipo, sobre el Bundle exacto de B01 | exactamente el subtipo previsto, uno por mutación | ocho mutaciones de forma (orden de entries, de `content[]` y de `author[]`, `id`, `meta`, `text`, extensión ajena, `display`, `Bundle.type`, `subject` lógico) → 0 cuentan y 8 notas |
| P-MD-24 | MCP, esquema y herramienta (§7) | `verificar_caso` con `punto_entrada = mdm_conv` pasa el esquema; `consultar_tabla("perfil_guia_mdm")` devuelve **46 filas** con `nivel` y `citas`; `info_verificador.puntos_entrada` ∋ `mdm_conv`; `punto()` de MDM → `mdm_conv`; `generar_corpus(lab=True)`: `por_corpus["adt"]`, `["oru"]`, `["vxu"]`, `huella_adt_oru_muestras` iguales a las de hoy (valores fijados en la prueba), `n["mdm"] = 40`, `CORPUS.index` de los seis existentes sin cambio; juguete `JUGUETE-NOMINAL` MDM → `correcto` | sin error | `mdm_conv` con `conversion` ausente → error de esquema; `consultar_tabla("perfil_guia_vxu")` y `("perfil_guia_adt")` devuelven las filas de hoy; `JUGUETE-DOCSTATUS` → `fallo_silencioso`, `[("fidelidad", "fhir_invalido+valor_distinto", "TXA-17")]` según Q; `JUGUETE-TEXTO` → `dato_perdido` OBX-5; `punto()` de ADT/ORU/VXU/SIU como en `prueba_vc.p07` |
| P-MD-25 | **ADT, ORU y VXU no cambian** | (a) `prueba_conversion.py` (28), `prueba_vc.py` y todas las suites de hoy, incluidas las de VXU, en verde **sin editar** (con el único cambio declarado de `p06`); (b) `cv/rejuicio.py`: cada evidencia del corpus del estudio (A1 263, E2 216, ORU 40, VXU 40, muestras) juzgada con el juez nuevo da `veredicto` y `hallazgos` (`clase, subtipo, hecho, cuenta, que, citas`) **byte a byte iguales** a los sellados; (c) `INFORME.json` de cada conversor idéntico salvo `juez.huella/revision`; (d) `json.dumps` ordenado de `CV.C`, `CV.INFO` (sin la clave `mdm`), `CV.TIPOS_PROY`, `CVX.TIPOS`, `PUNTOS` (sin `mdm_conv`) y `CV.MAPAS`, igual antes y después; (e) los MDM de `muestras` son los únicos casos cuyo `punto` cambia | 0 diferencias | una línea cambiada a propósito en `_patient` y otra en `conversion_vxu._status` hacen fallar (b): la prueba de que el rejuicio ve |
| P-MD-26 | corpus (§5) | `bases_mdm.autoprueba`: 40 bases, ids B01..B40, todas leídas y con estructura `MDM_T02`, TS y tablas válidos, ED.5 válido, `firma` ≥ 3 en todo par, `cobertura` completa, sha256 del conjunto fijo, sin nombres reales (lista cerrada) | TODO BIEN | una base duplicada con un solo campo distinto rompe `firma`; una fila «cuenta» sin base rompe `cobertura`; un ED.5 con un carácter fuera del alfabeto rompe la tabla |
| P-MD-27 | citas | `conversion_mdm.autoprueba`: `MAPAS_MDM` iguales a los del paquete; ninguna clave de `C_MDM` choca con `CV.C` ni con `C_VXU` salvo las de `C_SEG`; todo hallazgo que cuenta lleva una cita `[G …]` o `[CM …]` y otra `[E…]`, `[F …]` o `[AMB…]` | TODO BIEN | una clave `OBX-5` en `C_MDM` hace fallar la autoprueba (colisión con la de ORU) |

Controles que no cambian: `prueba_verificador`, `prueba_adt`, `prueba_oru`, `prueba_multitipo`, `prueba_mutantes`, `prueba_conversion`, `prueba_conversion_vxu`, `prueba_vc` (salvo el recuento declarado de `p06`),
autopruebas, `prueba_mcp_verificador`; la regresión 2.721 y la concordancia A1: idénticas.

---

## 9. Las preguntas de diseño para Jev (Q-MD-D-n)

Solo las que no deciden ni la pregunta ni las condiciones. Estado neutro: cada fila da las opciones y qué cambia; **la recomendación va aparte**, en §9.1. Ninguna toca ADT, ORU ni VXU.

| Q | Pregunta | Opciones | Qué cambia según la respuesta |
|---|---|---|---|
| Q-MD-D-1 | ¿Qué eventos MDM juzga `mdm_conv`? T04, T06, T08 y T10 comparten la estructura de T02 (`estructuras_25.json:7022-7028`) pero la guía solo tiene el mapa de T02 (`[G MSG_MDM_T02.csv]`) y el ANTES deja «su semántica de cambio de estado» fuera (`ANTES:107-111`) | (a) solo MDM^T02; (b) T02 y los otros cuatro con este perfil y nota `evento` (no se juzgan TXA-13 ni las transiciones de TXA-17/TXA-19); los T01, T03, T05, T07, T09 y T11 siguen `fuera_de_alcance` | `tipos` del PE (§2.1); con (b), las bases secundarias S01..S04 (§5.2) y los T04/T06/T08/T10 de las muestras públicas se juzgan; con (a), son `fuera_de_alcance` |
| Q-MD-D-2 | ¿Entran Provenance y MessageHeader? La guía crea un Provenance por cada TXA-8 «if the implementer wants» (`[G MSG_MDM_T02.csv:30-31]`) y otros desde EVN, PID y MSH | (a) fuera: `otros_tipos` (nota), como L-CV-5; (b) solo existencia (un Provenance por TXA-8 y un MessageHeader); (c) Provenance con campos (`recorded` ← TXA-8, `agent[2]` ← TXA-9, `reason.text` ← TXA-21, `agent[1]` ← TXA-23) | (b) añade 2 reglas y (c) hasta 6; (c) obliga a emparejar Provenance con DocumentReference por `target`; la numeración `Provenance[3]` de la hoja se usa dos veces (AMB-MD-22) |
| Q-MD-D-3 | Tipo MIME de los attachments: `application/text` (TX) y `text/hl7v2` (FT) son los literales de la guía y no están registrados; `text/plain` es el registrado. ED.3 y RP.3/RP.4 dan un subtipo, no un MIME completo. ¿Qué espera el juez? | (a) los literales de la guía (TX `application/text`, FT y NTE `text/hl7v2`; ED: ED.3 o `ED.2/ED.3`; RP: `RP.3/RP.4`); (b) los literales **o** el MIME registrado equivalente (TX y FT: `text/plain`; ED y RP: cualquier tipo principal con el subtipo igual); (c) solo que haya un `type/subtype` que no contradiga el tipo (texto para TX/FT, el subtipo para ED/RP) | MC-MD-11, MC-MD-13 y MC-MD-15 (≈ 30 bases cada uno): con (a) todo conversor que escriba `text/plain` suma `valor_distinto` en cada base de texto; con (b) no; con (c) solo cuenta lo que contradice |
| Q-MD-D-4 | `docStatus` ← TXA-17: la guía copia el código (`$value`, sin vocabulario) y R4 lo ata a `composition-status` (cuatro valores que no son los de la 0271). ¿Qué espera el juez? | (a) solo el literal de la guía (un valor de `composition-status` sale `valor_distinto`); (b) el literal **o** el `MAPA_0271` (§4.5), y el literal cuenta además como `fhir_invalido`; (c) el literal **o** el `MAPA_0271`, sin penalizar el literal (nota `literal_de_la_guia`); cuentan la ausencia, la incoherencia y lo que no es ni literal ni válido; (d) solo valores válidos y coherentes (el literal y la ausencia cuentan) | MC-MD-1, que dispara las 40 bases: con (b) y (d) todo conversor fiel a la guía suma un hallazgo en todas; con (a) y (c), no. Es la Q que más mueve N |
| Q-MD-D-5 | Varios OBX del mismo tipo (las secciones de un informe): la guía no dice si son un `content` o varios; sus índices `content[2]` y `content[4]` sugieren uno por tipo, y «each repeat yields a line feed» habla de repeticiones de OBX-5, no de OBX distintos | (a) cualquier reparto (un `content` por OBX, uno por tipo, uno solo) mientras todo llegue entero; (b) un único `content` por tipo (literal de los índices); (c) un `content` por OBX | B02, B20, B23, B24; MC-MD-16: con (b) o (c), el reparto distinto de OBX suma `valor_distinto` o `dato_dividido` (se añadiría el subtipo) |
| Q-MD-D-6 | `DocumentReference.subject` y `context.encounter` ausentes: la guía no tiene fila y R4 solo cruza `subject` con PID-3 (`[F documentreference.profile.json:820-821]`) | (a) nota `sin_subject` (presente y mal sí cuenta); (b) `dato_perdido` (cita: el cruce de R4 y la condición 2) | las 40 bases; MC nuevo «sin subject» (frecuente en un conversor por plantilla); con (b) cambia R-MD-15 y sube el nº de hallazgos por base |
| Q-MD-D-7 | `context.related` y varios grupos de orden: la guía escribe `ServiceRequest[1]`; el estándar dice que el documento satisface **todas** las órdenes (`[E9 CH09.txt:235-240]`) | (a) basta una referencia a alguno (literal de `[1]`); (b) una por cada ServiceRequest emparejado | B28 (2 grupos) y B29 (3 grupos); MC-MD-19 |
| Q-MD-D-8 | Un `Observation` (o `DiagnosticReport`) en el Bundle de un MDM: la guía lleva el OBX a `DocumentReference`, no a Observation (`[G MSG_MDM_T02.csv:34]`) | (a) nota (`otros_tipos`); (b) `recurso_inventado` | MC-MD-17: con (b) cada Observation es un hallazgo |
| Q-MD-D-9 | TXA-19 = CA, OB o UN: la guía solo pone la extensión `alternate-codes` y deja `status` (1..1) sin valor | (a) `status` cualquiera del ValueSet y el código en la extensión (S-MD-10); (b) lo anterior y además `status` coherente: CA → `entered-in-error`, OB → `superseded` (UN: cualquiera); (c) la extensión no cuenta (L-CV-4): solo `status` válido | B10-B12; MC-MD-2: con (b) un CA con `current` es `valor_distinto` aunque la extensión esté; con (c) un conversor que escribe la extensión no gana nada |
| Q-MD-D-10 | Profundidad del ServiceRequest | (a) existencia, `subject`, `identifier` PLAC/FILL, `code` y validez de `status`/`intent` (R-MD-37..41); (b) solo existencia y enlace desde la DocumentReference; (c) además `requester` (ORC-12/OBR-16), `authoredOn` (ORC-9) y `note` (NTE de OBR) | nº de reglas (46 → 43 con (b), 49 con (c)), MC-MD-20 y el tiempo de MD1 |
| Q-MD-D-11 | TXA-9 y TXA-10 repiten (XCN) y `authenticator` es 0..1 (`author`, 0..*) | (a) la primera repetición de TXA-10 es la esperada; (b) cualquiera de las repeticiones; las demás nota `extra` | B35; MC-MD-7: con (a), un conversor que escoge la segunda suma `valor_distinto` |
| Q-MD-D-12 | OBX de tipo sin fila (CE, ST, NM, DT…): la guía no los lleva a ningún sitio, pero el capítulo 9 dice que el contenido de un documento «can be represented with one or more» OBX (`[E9 CH09.txt:191-195]`) y R4 pide `content` 1..* | (a) nota: sin destino no hay esperado; (b) `dato_perdido` si el valor del OBX (texto, código o fecha) no está en ningún elemento de la DocumentReference ni de sus referidos | B25 y los MDM públicos con OBX estructurados (como el del capítulo 9); con (b) se cuenta algo que la guía no manda |

### 9.1 Mi recomendación (aparte, para que el estado de Jev sea neutro)

| Q | Recomiendo | Por qué |
|---|---|---|
| Q-MD-D-1 | **(b)** | el ANTES permite T04, T06, T08 y T10 como corpus secundario; la estructura y el mapa son los mismos y cuesta cuatro bases; la semántica de cambio de estado queda fuera con nota |
| Q-MD-D-2 | **(a)** | la propia guía deja el Provenance «up to the implementer» (`[G MSG_MDM_T02.csv:30-31]`) y L-CV-5 ya lo trata como nota en ADT, ORU y VXU; contarlo añade reglas con condiciones sin dato clínico propio |
| Q-MD-D-3 | **(b)** | los literales de la guía no son tipos registrados y `text/plain` dice lo mismo; contar `text/plain` como fallo en ≈ 30 bases sería contar la elección de un literal, no un cambio del significado |
| Q-MD-D-4 | **(c)** | contar el literal como `fhir_invalido` es contar el defecto de la guía contra el conversor que la sigue; pero un `entered-in-error` para un documento autenticado o la ausencia del estado sí cambian el significado. La alternativa preinscrita es (b) |
| Q-MD-D-5 | **(a)** | la guía no define el reparto y R4 admite varios `content`; lo que importa es que el texto llegue entero y en orden |
| Q-MD-D-6 | **(a)** | sin fila de la guía no hay esperado (condición 3); un `subject` equivocado sí cuenta. La alternativa preinscrita es (b) |
| Q-MD-D-7 | **(b)** | el capítulo 9 dice que el documento satisface todas las órdenes; `[1]` es un índice de instancia en la notación de la guía, no «solo el primero». Confianza media: entra en `ALTERNATIVA_MD` |
| Q-MD-D-8 | **(a)** | un Observation de más duplica el dato, no lo cambia; y la hoja de MDM no lo prohíbe |
| Q-MD-D-9 | **(a)** | la guía solo fija la extensión; exigir un `status` concreto es inventar un mapa que no tiene. Pero el dato (el código) sí debe conservarse |
| Q-MD-D-10 | **(a)** | es lo que `ServiceRequest` exige (1..1: `status`, `intent`, `subject`) más lo que la guía llena con valor propio (identifier, code); el resto de la hoja tiene comentarios de «localized interpretation» |
| Q-MD-D-11 | **(b)** | la guía no dice cuál; con 0..1 y XCN repetible, cualquier elección es una lectura válida |
| Q-MD-D-12 | **(a)** | sin fila no hay cita de destino (condición 3); queda declarado como L-MD-2 para que el RESULTADO diga cuántos OBX estructurados traen los MDM públicos |

Sensibilidad preinscrita (como `resultados/decisiones-qvx.md:21-23`): las Q que Jev deje con confianza ≤ 0,52 entran en `ALTERNATIVA_MD` y MD2 da también la N con la alternativa de cada una.

---

## 10. Límites (L-MD-n) y lecturas adoptadas (AMB-MD-n)

### 10.1 L-MD-n (para `info_verificador.limites`)

| L | Redacción |
|---|---|
| L-MD-1 | «El contenido del documento no se interpreta: no se decodifica RTF, PDF ni CDA y no se lee el texto. Un texto (TX, FT, NTE) llega entero si las palabras del original son una subsecuencia ordenada de las del `data` decodificado; un binario (ED), si sus octetos son los mismos tras deshacer su codificación (ED.4).» |
| L-MD-2 | «Los OBX de tipo distinto de TX, FT, ED y RP (CE, ST, NM, DT, TS…) no tienen fila en la guía: nota `sin_destino`, aunque el propio capítulo 9 los use en su ejemplo. Su pérdida no cuenta (Q-MD-D-12).» |
| L-MD-3 | «Provenance, MessageHeader, Device, Coverage, Basic, Organization, Observation y todo recurso fuera del perfil son `otros_tipos` (nota); Practitioner y Binary solo se leen como destino de `author`, `authenticator` y `attachment.url` (Q-MD-D-2, Q-MD-D-8).» |
| L-MD-4 | «TXA-4, 5, 7, 8, 11, 13, 14, 15, 20, 21, 22 y 23 no tienen destino en `DocumentReference` (TXA-8, 9, 21 y 23 van a Provenance en la guía). TXA-24..28, NTE-5..9 y OBX-20..33 no existen en 2.5: aunque la guía los mapee (TXA-25 → `description`), nunca cuentan.» |
| L-MD-5 | «`DocumentReference.subject` y `context.encounter` no tienen fila en la guía; R4 solo cruza `subject` con PID-3. Presentes y equivocados cuentan; ausentes son nota (Q-MD-D-6).» |
| L-MD-6 | «Los conjuntos que el perfil usa y no son de la guía ni están en la carpeta: `MAPA_0271` (de las definiciones de v2.5 y de R4), `FAMILIA_0191` (tipos principales de MIME), y los códigos de `request-status` y `request-intent` (R4, fuera de la carpeta, como L-CV-3).» |
| L-MD-7 | «No hay validador FHIR completo: de `base64Binary` solo se comprueba el alfabeto estándar y el relleno; el tipo `url`, la sintaxis MIME y los demás primitivos no (L-CV-11).» |
| L-MD-8 | «Solo MDM^T02 (y, si Q-MD-D-1 lo decide, T04, T06, T08 y T10 con nota `evento`). La semántica de cambio de estado, el documento padre (TXA-13) y las transiciones de TXA-17 y TXA-19 entre mensajes no se juzgan; T01, T03, T05, T07, T09 y T11 son `fuera_de_alcance`.» |
| L-MD-9 | «Un OBX antes del TXA solo se cuenta; un segundo TXA da nota `estructura`; UAC y CON (que la hoja del mensaje trae y el MDM_T02 de 2.5 no) se ignoran.» |
| L-MD-10 | «Dos grupos de orden iguales en números y OBR-4, o dos DocumentReference sin ninguna clave común, no se distinguen: `indeterminado/emparejamiento`.» |
| L-MD-11 | «Las extensiones nunca cuentan (L-CV-4), salvo en `mdm_conv` la de `status.extension[alternate-codes]` de TXA-19 = CA, OB o UN, que es el único portador del dato en la guía.» |
| L-MD-12 | «ED.5 llega a 65536 caracteres en 2.5 (`[E2A CH02A.txt:1820]`); un Bundle de más de 4.000.000 de caracteres no se juzga (L-VC-12).» |
| L-MD-13 | «MSH-9.3 nunca cuenta; con MSH-12 ≠ 2.5 la legalidad de una tabla o de la estructura no se juzga (L18).» |
| L-MD-14 | «ED.4 = A se codifica como ASCII; un ED.5 con caracteres no ASCII y A no se juzga (nota).» |
| L-MD-15 | «"Llega entero" mira palabras (alfanuméricas Unicode, sin mayúsculas): no ve puntuación, símbolos ni espacios, y no distingue dos OBX con el mismo texto. Un texto reordenado palabra a palabra sí se ve; uno al que se le quita un guion, no.» |
| L-MD-16 | «Con varias DocumentReference para un TXA, el contenido se juzga en conjunto para no contar la pérdida dos veces.» |
| L-MD-17 | «La clase nueva / ya declarada / convención no la calcula el juez: la pone MD3 con las salidas esperadas, pruebas e issues del proyecto, por mecanismo (L-CV-10).» |

### 10.2 Índice de lecturas adoptadas AMB-MD-n (para `info_verificador.ambiguedades`; cada una con su alternativa)

| AMB | Enunciado | Lectura adoptada | Alternativa |
|---|---|---|---|
| AMB-MD-1 | TXA-2 es IS de una tabla user-defined en 2.5 y CWE en la hoja | `type.coding.code` ∋ TXA-2.1; sin `system` | exigir un `system` fijo (no hay URI) |
| AMB-MD-2 | TXA-3 (0191) no es un MIME y `contentType` tiene binding `required` BCP-13 | convención: el literal o la familia; solo cuenta la ausencia total (Q-MD-D-3) | literal estricto |
| AMB-MD-3 | TXA-17: sin vocabulario en la guía; `composition-status` en R4; AU no es el estado final (figura 9-1) | conjunto: literal ∪ `MAPA_0271` (Q-MD-D-4) | solo el literal, o solo lo válido |
| AMB-MD-4 | la fila «TXA-19 NOT VALUED → current» (`[G TXA_DocumentReference.csv:4]`) no está en el ConceptMap; CA, OB y UN no fijan `status` | `current` con TXA-19 vacío; CA/OB/UN: `status` libre y código en la extensión (Q-MD-D-9) | sin esperado con TXA-19 vacío |
| AMB-MD-5 | la URL de `alternate-codes` es `http` en la hoja de TXA (`:26`) y `https` en la de ED (`ED_Attachment.csv:5`) | se aceptan las dos | solo la de la hoja de TXA |
| AMB-MD-6 | la hoja de OBX escribe `content[2].data`, `content[3].url`… sin `.attachment`, y numera por tipo | `content[].attachment.*`; los números son etiquetas | tomar los índices como posiciones |
| AMB-MD-7 | varios OBX del mismo tipo: la guía no dice si son uno o varios `content` | cualquier reparto (Q-MD-D-5) | uno por tipo |
| AMB-MD-8 | `application/text` y `text/hl7v2` no son tipos registrados | convención con `text/plain` (Q-MD-D-3) | los literales |
| AMB-MD-9 | FT con `text/hl7v2` conserva las órdenes de formato; con otro tipo debe renderlas | R-MD-23 | contar siempre el escape crudo |
| AMB-MD-10 | ED.3 → `contentType` lleva solo el subtipo | subtipo igual, o `ED.2/ED.3` | solo el literal ED.3 |
| AMB-MD-11 | RP.1 es un «pointer», no necesariamente una URL | `url` = RP.1; con prefijo, nota | exigir URL absoluta |
| AMB-MD-12 | la hoja de ED solo nombra A y Hex como conversión | Base64 pasa tal cual; A y Hex se convierten | no juzgar A y Hex |
| AMB-MD-13 | NTE-3 → `content[1].attachment.data` y `content[2].contentType`: índices distintos | un `content` con las palabras del comentario; el tipo sigue a R-MD-24 | exigir dos `content` |
| AMB-MD-14 | XCN repite; `author` es 0..* y `authenticator` 0..1 | una repetición cualquiera para `authenticator` (Q-MD-D-11) | la primera |
| AMB-MD-15 | `subject` sin fila en la guía; R4 lo cruza con PID-3 | ausente: nota (Q-MD-D-6) | `dato_perdido` |
| AMB-MD-16 | `ServiceRequest[1]` con varios grupos | una referencia por ServiceRequest (Q-MD-D-7) | basta una |
| AMB-MD-17 | `date` de R4 es la fecha de la referencia; TXA-6 es la del documento; sin hora la guía usa R6; sin TXA-6 el valor puede venir de otro TS | `instant` con hora; sin hora ausente o completado (AMB-CV-9); sin TXA-6, nota si coincide con un TS del mensaje | contar siempre `dato_inventado` |
| AMB-MD-18 | varias DocumentReference para un TXA | la primera se empareja y las demás son `recurso_duplicado`; contenido en conjunto | contar la pérdida en cada una |
| AMB-MD-19 | `EI[Identifier-Organization]` no tiene `system` | `system` o `assigner` con EI.2/EI.3 (como CX.4) | solo `assigner` |
| AMB-MD-20 | TXA-18 → v2-0272 (guía) o v3-Confidentiality (binding extensible) | las dos | solo v2-0272 |
| AMB-MD-21 | la hoja del mensaje trae UAC y CON y el MDM_T02 de 2.5 no | se ignoran | — |
| AMB-MD-22 | `Provenance[3]` se usa para EVN y para ORC en la hoja del mensaje | irrelevante mientras Provenance sea nota (Q-MD-D-2) | — |
| AMB-MD-23 | EVN es «B, v2.5» y sigue siendo obligatorio en la estructura; EVN-1 debe valer MSH-9.2 | el corpus lo cumple; EVN no se juzga | — |
| AMB-MD-24 | el estándar admite CR LF o LF entre repeticiones de TX; la guía dice «line feed» | LF, CR LF o CR | solo LF |
| AMB-MD-25 | `ServiceRequest.status` e `intent`: «localized interpretation»; hay ConceptMap de la 0119 pero la hoja lo condiciona a ORC-5 sin valor | solo validez | exigir el mapa 0119 |

---

## 11. El plan: MD1 y MD2 (y lo que sigue), con «hecho cuando» y regla de parada

Tope de la etapa: cuatro sesiones y antes del 20-nov (`ANTES-ETAPA-MDM.md:95-98`); MD-pre y MD0 gastan parte de la primera. Reparto propuesto: **MD1 ≈ 1,5 sesiones, MD2 ≈ 1, MD3 ≈ 1, MD4 ≈ 0,5**.
Primero lo que puede tumbarlo: el emparejamiento y el contenido sobre la salida real.

| Fase | Qué, en orden | Hecho cuando | Parada |
|---|---|---|---|
| **MD1-a** emparejador y salida real (≤ 1 h) | (1) construir `PUNTOS["mdm_conv"]`, afirmar `_afirmar` y que `contrato(PUNTOS["mdm"])` no cambia; (2) pasar por `leer_bundle`/`emparejar` **sin perfil** las salidas guardadas de E-MD-3 (B01, B05 y B24, tal cual): ¿una DocumentReference por TXA?, ¿`content` con `attachment`?, ¿`Binary`?, ¿Observation?, ¿ServiceRequest?, ¿referencias por `urn:uuid`?; (3) comprobar que un ED grande no pasa de 4.000.000 caracteres (L-VC-12) | PE y emparejador leen las salidas sin `indeterminado`; la forma del contenido de cada conversor queda anotada para el informe de E-MD-3 (nunca para tocar el perfil) | un `indeterminado/emparejamiento` o `lectura` → se corrige el emparejador con la salida como cita (DV-MD), nunca el perfil; **ningún conversor devolvió Bundle con MDM_T02 en E-MD-3 → la etapa ya estaba parada** (`ANTES:68-70`); uno solo → sigue con uno y K ≤ 1 |
| **MD1-b** pruebas en rojo | P-MD-1..27 escritas y en rojo por la razón prevista; `prueba_conversion_mdm.py rojo` sale 0; las dos líneas base (P-MD-1 `mdm` intacto, P-MD-25 a) en verde con el juez de hoy | cada prueba falla donde debe | una prueba que no se puede poner en rojo = pieza no definida: vuelve a este diseño como Q-MD-D |
| **MD1-c** las decisiones de Jev | Q-MD-D-1..12 con estado neutro (§9), sin §9.1; `DECISIONES_MD` y `ALTERNATIVA_MD` en `conversion_mdm.py` | las doce contestadas con confianza | — |
| **MD1-d** código | PE `mdm_conv` → `conversion_mdm` (grupos, imposibles, emparejar, perfil, juzgar, contenido) → seis ganchos en `conversion.py` → esquema, MCP (`perfil_guia_mdm`, descripción), `info_verificador` → `punto()`, `CORPUS`, juguete | P-MD-1..24, 26, 27 en verde; todas las suites de hoy en verde sin ningún cambio salvo los declarados (enum del esquema, textos de `info_verificador`/`REVISION`, recuento de `prueba_vc.p06`) | cualquier rojo no declarado |
| **MD1-e** el rejuicio y la primera salida real con perfil | P-MD-25: corpus del estudio (A1, E2, ORU, VXU, muestras) con el juez nuevo = sellados, **0 diferencias**; las salidas de MD1-a con el perfil puesto | 0 diferencias; emparejamiento `master`/`identifier` sin ambiguos | una diferencia en ADT/ORU/VXU → se deshace el gancho que la causó antes de seguir (las cuatro expresiones de §3 son los sospechosos); un `indeterminado/emparejamiento` → se corrige el emparejador (DV-MD) |
| **MD2-a** el corpus | `bases_mdm.py` con las 40 de §5.2; `--firma`, `--cobertura`, `--autoprueba` en verde; `generar_corpus` escribe `mdm/` con su huella y deja `adt`/`oru`/`vxu` intactas (P-MD-24) | 40 bases válidas, firma ≥ 3, cobertura completa, huella sellada | una fila «cuenta» sin base → se escribe la base, no se baja la fila |
| **MD2-b** la previsión sellada | §6 completada con las cuentas (n de bases por mecanismo, lo visto en E-MD-3) y sellada con la huella del juez y del corpus **antes** de juzgar | `prevision-mdm.json` sellado | — |
| **MD2-c** las corridas y el juicio | los dos conversores sobre las 40 bases (y las muestras públicas de E-MD-2 con banderas L18) con `verificar_conversor.py`; tabla por conversor × categoría × mecanismo; «fuera de previsto» adjudicado con cita; la N también con cada alternativa de `ALTERNATIVA_MD` | 0 fuera de previsto sin adjudicar | un defecto del juez se arregla con su prueba y MD2-c se repite entero; **dos repeticiones como máximo**; luego el mecanismo pasa a L-MD y se declara |
| **MD3** contraste y clase | por mecanismo: salidas esperadas y pruebas publicadas del proyecto; sus issues (con red, fuera de la caja, Q-CV-A-5); relectura del ConceptMap y la hoja → `clase_cv` por la regla de CV §4.3; pares mínimos de MDM en `cv3_minimos_mdm`; revisión adversaria | cada mecanismo con clase y referencia; cada `nueva` con par mínimo y cita completa | un mecanismo sin clasificar en 30 min → Q-MD-D, no cuenta como nueva; ≤ 2 rejuicios por correcciones del perfil (DV-MD) |
| **MD4** cierre | `RESULTADO-MDM.md` con la frase fija (`ANTES:88-91`), o el resultado negativo con su frase (`ANTES:100-105`); MCP con S-MD/L-MD/AMB-MD/DV-MD; suites; guarda en LIMPIO; opción B | todo lo anterior | guarda no LIMPIO → no se publica |

---

## 12. Los cuatro riesgos que más me preocupan

1. **El contenido es la pieza más nueva y la que más mecanismos concentra.** Ni ORU ni VXU obligan al juez a decodificar Base64, comparar octetos ni seguir palabras a través de uno o varios `content`. Si un conversor devuelve el texto en `text.div`,
   en un `Binary` aparte o en un `content` por línea, el lector del §2.2 y el pool del §4.2 hacen lo que pueden y lo demás sale como `dato_perdido`. Por eso MD1-a pasa la salida real por el emparejador **antes** del perfil y cualquier ajuste es DV-MD con la
   salida como cita. Nivel: alto.
2. **El perfil cuenta de más donde la guía calla.** `docStatus` (sin vocabulario), `contentType` (literales no registrados), TXA-19 CA/OB/UN (sin `status`), `subject` (sin fila) y los OBX sin destino son silencios de la guía y cada uno está escrito como AMB-MD y Q-MD-D con
   su alternativa; si en MD3 hay que bajar más de dos mecanismos a convención, la N queda inflada o el tope no llega. Nivel: medio-alto.
3. **Un solo mecanismo puede teñir todo el corpus.** MC-MD-1 se dispara en las 40 bases y MC-MD-11 en ≈ 30: `fallo_silencioso` en el 100 % no informa. La lectura de resultados va por mecanismo y con las 8 bases de control, y la previsión da los rangos
   con y sin las dos Q que los mueven. Nivel: medio-alto.
4. **El emparejamiento sin identificadores.** B29 (tres grupos con el mismo OBR-4), B30 (sin ORC-2/3) y las DocumentReference duplicadas dependen de números que un conversor puede cambiar o perder; VXU ya tuvo su L-VX-14. Las claves van en pasadas por papel (como
   `conversion_vxu.py:259`) y el último recurso es `indeterminado/emparejamiento`, no una elección al azar. Nivel: medio.

---

## Resumen (≤ 15 líneas)

1. Secciones: 0 decisiones S-MD-1..17; 1 E-MD-1 (TXA, OBX por OBX-2, NTE, PID/PV1/EVN/ORC/OBR, sin cita y ambiguas); 2 `mdm_conv`; 3 dónde vive; 4 perfil «guía» (46 reglas) y tablas de códigos; 5 corpus; 6 previsión; 7 herramienta; 8 P-MD-1..27; 9 Q-MD-D-1..12; 10 L-MD-1..17 y AMB-MD-1..25; 11 plan; 12 riesgos.
2. E-MD-1: TXA-2, TXA-12, TXA-17 y OBX-5 **tienen cita** (la regla de parada no se activa) pero TXA-17 no tiene vocabulario y R4 lo ata a otros cuatro códigos, TXA-2 es IS user-defined en 2.5, y OBX-5 solo tiene fila para ED, FT, RP y TX con caminos que R4 no tiene.
3. Punto `mdm_conv`: hermano de `adt_conv`/`oru_conv`/`vxu_conv` con `familia = "mdm"`; gramática y 0354 ya existen (nada que extraer); una DocumentReference por TXA con todos sus OBX y NTE (no hay Observation); un ServiceRequest por grupo de orden; Patient y Encounter como en ADT; seis ganchos nuevos en `conversion.py`.
4. Perfil: 46 reglas (39 cuentan, 2 convención, 4 nota, 1 forma): metadatos (TXA-2, 3, 6, 9, 10, 12, 16, 17, 18, 19) y contenido por OBX-2 (TX/FT por palabras en orden, ED por octetos, RP por url) sin interpretar el documento.
5. Corpus: 40 bases válidas en v2.5 (8 de control), una por rama, con regla medible contra la firma (≥ 3 campos distintos por par) y cobertura afirmada; cargas generadas con `base64`; 4 bases secundarias (T04/T06/T08/T10) solo si Jev las quiere.
6. Previsión: 22 mecanismos; `fallo_silencioso` 80-100 % en ambos; la más probable de las nuevas, `docStatus`; ≥ 1 nueva en alguno 0,85.
7. Herramienta: `punto()` añade MDM → `mdm_conv` sin tocar ADT/ORU/VXU; `mdm` al final de `CORPUS`; T01, T03, T05, T07, T09 y T11 `fuera_de_alcance`; T04/T06/T08/T10 según Q-MD-D-1.
8. P-MD-1..27 con control negativo; P-MD-25 es el rejuicio byte a byte de ADT, ORU y VXU (0 diferencias) y las suites de hoy sin editar.
9. 12 Q-MD-D (eventos, Provenance, tipo MIME, `docStatus`, varios OBX, `subject`, `related`, Observation, TXA-19, ServiceRequest, TXA-10, OBX sin destino) con la recomendación aparte.
10. Plan: MD1 emparejador sobre la salida real (parada si ningún conversor devolvió Bundle) → rojo → Jev → código → rejuicio 0; MD2 corpus → previsión sellada → corridas (≤ 2 repeticiones).

