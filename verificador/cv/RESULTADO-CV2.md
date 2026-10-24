# CV2: los dos conversores juzgados contra la previsión sellada (23-oct-2026)

**CV2 hecho.**
- Los dos conversores pasaron por el corpus entero en su caja: ADT 263, ORU 40 y 65 muestras.
- El juez los juzgó todos.
- Todo lo que quedó fuera de previsto está adjudicado (juez, perfil, corpus, conversor o ambigüedad), cada cosa con su
  cita.
- Salen **20 candidatas a discrepancia** que no estaban en la lista de mecanismos de Fable, más los mecanismos previstos que
  sí aparecieron. Todas pasan a CV3.

La previsión falló por mucho, y así queda escrito:
- **Muchos menos `correcto` de lo previsto en ADT, en los dos conversores:** el 2,3 % y el 4,2 % frente a rangos de 30-65 %.
  Viene de un solo mecanismo sistemático en cada uno.
- **Muchos más rechazos de lo previsto:** el 27 % y el 35 % frente a topes del 5 y el 10 %.

Se usó una repetición del juez de las dos permitidas.

| | |
|---|---|
| Previsión | `cv/PREVISION-CV2.json`, sellada en `ed1c341` con el juez `63d40cd0…` (`cv/SELLO-CV2.txt`) |
| Juez de este resultado | `be73697f3d79…`: el sellado más la repetición 1 (J1, J2, J3, J5), en `3408647` |
| Conversores | Microsoft `v7.0 (253307f)`, huella `766f8938…`; LinuxForHealth `v1.1.0`, huella `ac41f71b…`; los dos en la caja de E-CV-3 |
| Corpus | `aa83359a…` (DV-CV-10: CR y sin BOM antes de convertir) |
| Agregados | `cv/RESULTADO-CV2.json` (lo escribe `cv/juzgar_cv2.py`) |
| Detalle por caso | `privado/cv/cv2/juicio.jsonl`, fuera de git |
| Adjudicación y candidatas | `cv/ADJUDICACION-CV2.json` |
| Pasada 0 | `cv/RESULTADO-CV2-pasada0.json`, guardada como registro |

## Cómo se llegó aquí

1. **Pasada 0, con el juez sellado.** Su adjudicación encontró cuatro defectos del juez:
   - **J1:** PID-12 a `address.district` (`PID_Patient.csv:18-21`).
   - **J2:** el género en minúscula, que es un literal y no un código FHIR.
   - **J3:** `status` es 1..1 con binding required: lo no mapeado o vacío va a convención.
   - **J5:** OBX-5 repetido admite componentes, varias Observation o concatenación (`MSG_ORU_R01.csv:69-73`).
2. **Repetición 1 (`3408647`).** P-CV-19..21 y la comprobación de J2 en p12 se escribieron en rojo y pasan en verde.
   - Todas las suites siguen en verde y la regresión de 2.721 casos sigue en CASA.
   - La previsión no se tocó.
3. **El arnés se corrigió antes de juzgar** (no son cambios del juez):
   - **DV-CV-11:** Microsoft corre fichero a fichero. En modo carpeta para en el primer fallo y deja la salida sin
     postprocesar.
   - **DV-CV-12:** MSH-9 se lee con los separadores del propio mensaje.
4. **Rejuicio con `be73697f`.** Es lo que se cuenta abajo.

La sensibilidad prerregistrada no cambia nada: con la alternativa de Q-CV-D-3, Q-CV-D-5 o Q-CV-D-9 sale el mismo número de
`fallo_silencioso` en las seis combinaciones de conversor y corpus, muestras incluidas.

## Lo que salió, frente a lo previsto

| Conversor · familia | n | Salida | `correcto` | `fallo_silencioso` | `rechazo_incorrecto` | `indeterminado` | Mecanismos distintos |
|---|---|---|---|---|---|---|---|
| Microsoft · ADT | 263 | 191 Bundle, 72 error | 6 (2,3 %) [35-65] | 185 (70,3 %) [30-60] | 72 (27,4 %) [0-5] | 0 | 12 [3-6] |
| Microsoft · ORU | 40 | 39 Bundle, 1 error | 33 (82,5 %) [20-50] | 6 (15,0 %) [45-80] | 1 (2,5 %) [0-5] | 0 | 8 [2-5] |
| LinuxForHealth · ADT | 263 | 162 Bundle, 101 error | 11 (4,2 %) [30-60] | 160 (60,8 %) [35-65] | 92 (35,0 %) [0-10] | 0 | 10 [3-6] |
| LinuxForHealth · ORU | 40 | 40 Bundle | 4 (10,0 %) [20-50] | 36 (90,0 %) [45-80] | 0 | 0 | 9 [2-5] |

Entre corchetes, el rango sellado. El lector no dio ni un `indeterminado` en 606 juicios.

### Mecanismos, en número de casos

| Microsoft · ADT | | LinuxForHealth · ADT | |
|---|---|---|---|
| MC-ADT-3 (PL a una sola Location o solo PL.1) | 184 | MC-ADT-3 | 160 |
| MC-ADT-11 (rechazo) | 72 | `Encounter.period.start` dato_inventado | 120 |
| MC-ADT-9 (Encounter.status) | 16 | MC-ADT-9 | 108 |
| MC-ADT-5 (PV1-10 literal v2-0069) | 14 | MC-ADT-11 | 92 |
| `Patient.gender` fhir_invalido | 9 | MC-ADT-1 (class) | 30 |
| MC-ADT-10 (participantes) | 8 | MC-ADT-5 | 15 |
| `Patient.address.district` dato_perdido | 6 | MC-ADT-8 (telecom) | 5 |
| MC-ADT-12 (DTM sin zona) | 5 | `Patient.address.line` valor_distinto | 5 |
| `Patient.deceasedBoolean` dato_inventado | 5 | MC-ADT-4 (estado civil) | 2 |
| MC-ADT-1 | 2 | `Patient.gender` valor_distinto | 1 |
| `Patient.gender` fhir_invalido + valor_imposible_convertido | 2 | | |
| MC-ADT-4 | 1 | | |

| Microsoft · ORU | | LinuxForHealth · ORU | |
|---|---|---|---|
| falta la Observation (`recurso_ausente`) | 3 | MC-ORU-4 (OBX-8 a v2-0078) | 30 |
| MC-ADT-11 (rechazo) | 1 | falta la Observation (`recurso_ausente`) | 3 |
| MC-ORU-1 (NM reserializado) | 1 | MC-ORU-2 (SN) | 2 |
| MC-ORU-2 | 1 | `DiagnosticReport.status` codigo_mal_mapeado | 2 |
| MC-ORU-6 (TX/FT) | 1 | MC-ORU-1 | 1 |
| MC-ORU-7 (result cruzado) | 1 | `Observation.status` codigo_mal_mapeado | 1 |
| `DiagnosticReport.subject` referencia_rota | 1 | `valueCodeableConcept.text` valor_distinto | 1 |
| `Observation.subject` referencia_rota | 1 | `valueString` dato_perdido | 1 |
| | | `valueTime` dato_perdido | 1 |

**Mecanismos previstos que no aparecen en el corpus:**
- de ADT: MC-ADT-2, -6, -7, -13 y -14;
- de ORU: MC-ORU-3 y -5;
- MC-ADT-8, -10 y -12 y MC-ORU-4, -6 y -7 solo aparecen en uno de los dos conversores.

La ruta «falta» de la lista es un artefacto de la regla de asignación: la ruta es la primera palabra del «que», y el «que» de
`recurso_ausente` empieza por «falta». Esos casos habrían quedado fuera de previsto de todos modos.

## Adjudicación de lo que quedó fuera de previsto

Cada punto de la lista `fuera_de_previsto` de `cv/RESULTADO-CV2.json`, con su decisión:
- **juez:** el código se equivoca;
- **límite:** el diseño no lo ve;
- **corpus:** el mensaje está mal hecho;
- **conversor:** discrepancia real;
- **ambigüedad:** el estándar admite las dos lecturas.

### Microsoft · ADT

| Fuera de previsto | Decisión | Qué es | Cita |
|---|---|---|---|
| El juez no es el sellado | declarado | La repetición 1 (J1, J2, J3, J5), con P-CV-19..21 y las suites en verde. Queda una repetición sin usar. | `3408647` |
| `correcto` 2,3 %, `fallo_silencioso` 70,3 %, 12 mecanismos | conversor | MC-ADT-3 aparece en 184 de 191 Bundles. `Encounter.location` apunta al punto de cuidado (PL.1, `lvl`). La cama (PL.3) está en la cadena `partOf`, pero el centro no queda enlazado. | CM `datatype-pl-to-location`; `PV1_Encounter.csv:7-9` |
| 30 rechazos «Date or DateTime is invalid: L.» | **corpus** | Los 30 mensajes son de las familias «comp» (18) y «opci» (12) de E2. Traen GT1 desplazado un campo: GT1-2 (Guarantor Number, CX) lleva un nombre `…^^^^^L`, y CX.7 es un DT (Effective Date). **La causa es casi segura:** NK1-2.7 también es `L` en esos 30, pero ahí es el tipo de nombre (XPN.7), el mismo de PID-5.7 = `L` en 152 mensajes que Microsoft convierte sin problema. Hay un valor imposible en un campo que Microsoft sí consume, así que el rechazo es aceptable (Q-CV-D-7). El juez no lo ve porque GT1 queda fuera de su proyección: es el **L-CV-14** nuevo. CV3 lo confirma con un mensaje mínimo. | E2 «comp»/«opci»; CX.7 DT (`CH02A.txt`) |
| 18 rechazos «Date or DateTime is invalid: ""» | conversor | Es la familia «nulos» de A01. El valor nulo `""` es legal. Microsoft intenta leerlo como fecha. En esos mensajes el único DTM con `""` es ACC-1: es la causa probable, y se confirma en CV3. | `CH02.txt:392` |
| 24 rechazos «Escape character should be backslash» | conversor | Son mensajes con caracteres de codificación distintos de los recomendados. `^~\&` son los recomendados, no los únicos. | `CH02.txt:624`, `:3703` |
| Rechaza el 27,4 % (> 10 %) | conversor y corpus | 42 de los 72 son de conversor. Sin los 30 del corpus, el porcentaje es del 16,0 %. | — |
| `Patient.address.district` dato_perdido (6) | conversor, con un matiz | Microsoft escribe PID-12 en una Address aparte que solo tiene `{district}`. La guía lo pone en la misma dirección de PID-11 (`address[1]`) cuando PID-11 no repite y XAD.9 está vacío, y reserva una segunda dirección para cuando repite o XAD.9 difiere. LinuxForHealth no da hallazgo en ninguno de sus 30 casos con PID-12. **Matiz:** el comentario de la fila 18 («not appropriate to include PID-12 in an iteration of .address populated from PID-11») se puede leer a favor de Microsoft. Se mira en CV3. | `PID_Patient.csv:18-21` |
| `Patient.deceasedBoolean` dato_inventado (5) | conversor | Escribe `deceasedBoolean: true` en cinco A02 de la familia «nulos» que no traen PID-29 ni PID-30. La causa se busca en CV3. | `PID_Patient.csv` (PID-30) |
| `Patient.gender` fhir_invalido (9) y fhir_invalido + valor_imposible_convertido (2) | conversor | Copia a `Patient.gender` un PID-8 en minúscula (`f`) o fuera de 0001 (`Z`). El binding es required. | `patient.profile.json:595`; CM `table-0001` |

### Microsoft · ORU

| Fuera de previsto | Decisión | Qué es | Cita |
|---|---|---|---|
| `correcto` 82,5 % (por encima), `fallo_silencioso` 15 % (por debajo), 8 mecanismos | conversor | Lo hace mejor de lo previsto. | — |
| Falta la Observation, ORU-B09 | conversor | Dos OBX con el mismo código (1988-5) dan una sola Observation: se pierde la primera (`<5`). La que queda lleva `comparator: "<>"`, que no está en `quantity-comparator` (required). | `MSG_ORU_R01.csv:67-69`; R4 Quantity |
| Falta la Observation, ORU-B23 | conversor | Se pierde el segundo OBX (2160-0) cuando el primero lleva dos NTE. La causa se busca en CV3. | `MSG_ORU_R01.csv:67-69` |
| Falta la Observation, ORU-B14 | **ambigüedad** + límite | OBX-3 trae `71020&IMP`: es la convención de sufijos del capítulo 7 (código, separador de subcomponente, sufijo). El juez empareja por OBX-3.1 = `71020`. Microsoft guarda `71020&IMP` y LinuxForHealth `71020`. Con la otra lectura (el código con su sufijo), Microsoft acierta y LinuxForHealth pierde el sufijo: el caso cambia de lado. Es la **AMB-CV-10** nueva. Además, que salga como «ausente + inventada + `referencia_rota`» es un artefacto del emparejamiento por código (§2.2): es el **L-CV-15** nuevo. No es candidata. | `CH07.txt:368-372` (v2.5 §7.2.4) |
| `subject` referencia_rota en DiagnosticReport y Observation, ORU-B30 | conversor | El mensaje no trae PID. Microsoft escribe `subject: Patient/364bf61f…`, un Patient que no está en el Bundle. Sin PID no hay `Patient[1]` al que apuntar. El hecho «PID-3» de un mensaje sin PID es una errata de redacción del juez, sin efecto en la categoría; se arregla en CV4. | `MSG_ORU_R01.csv` (subject = Patient[1]) |

### LinuxForHealth · ADT

| Fuera de previsto | Decisión | Qué es | Cita |
|---|---|---|---|
| 92 rechazos (35 %) | **pregunta de diseño** | Los 92 son «Message type not yet supported»: ADT_A02 (31), A11 (30) y A13 (31). El diseño sellado (§1.3, fila 95) los cuenta como `rechazo_incorrecto`. Pero v2.5 da al receptor un AR con 200/201 (tipo o evento no soportado), y el mismo diseño ya trata como aceptable el rechazo por versión. Va como **Q-CV-D-13**, para Jev antes de CV4. Sea cual sea la respuesta, es alcance de la versión y no una discrepancia de conversión. No es candidata. | tabla 0357 (`CH02.txt:3989-3990`); diseño §1.3 |
| `correcto` 4,2 %, 10 mecanismos | conversor | MC-ADT-3 aparece en 160 de 162 Bundles: no hay `Encounter.location`. | `PV1_Encounter.csv:7-9` |
| `Encounter.period.start` dato_inventado (120) | conversor | Con PV1-44 vacío, pone en `period.start` la hora del mensaje (MSH-7/EVN). | `PV1_Encounter.csv:71` |
| `Patient.address.line` valor_distinto (5) | conversor | Pierde SAD.2 y SAD.3. | CM `datatype-xad-to-address` (SAD.1-3 → line[1-3]) |
| `Patient.gender` valor_distinto (1) | conversor | Traduce PID-8 `N` a `unknown`; el ConceptMap dice `other`. | CM `table-0001` |

### LinuxForHealth · ORU

| Fuera de previsto | Decisión | Qué es | Cita |
|---|---|---|---|
| `correcto` 10 %, `fallo_silencioso` 90 %, 9 mecanismos | conversor | MC-ORU-4 (OBX-8 a `v2-0078`, previsto) aparece en 30 de 40. | previsión §7 |
| Falta la Observation, ORU-B10 | conversor (declarado por él) | Un OBX TX no da Observation: el texto va a `DiagnosticReport.presentedForm`. Su plantilla lo dice. Además, con OBX mezclados no hay `presentedForm` y los TX se pierden: pasa con los OBX 26-28 de la muestra `ms-LRI_2.0-NG_CBC`. | `DiagnosticReport.yml:139-141` del jar; `MSG_ORU_R01.csv:67-69` |
| Falta la Observation, ORU-B18 y B22 | conversor | Un OBX sin OBX-2 y sin valor (resultado pendiente `I`, o que no se puede obtener `X`) no da Observation. Va contra la guía y contra el comentario de su propia plantilla («OBX.2 is null/empty … CREATE the Observation»). La condición `$obx2 NOT_EQUALS_STRING TX` lo excluye. | `Observation.yml` del jar; `OBX_Observation.csv` |
| `valueString` dato_perdido (ORU-B11) y `valueTime` dato_perdido (ORU-B13) | conversor | Los valores FT y TM no se escriben: `valueString` solo existe para ST. | `Observation.yml` (`$obx2 EQUALS ST`); `OBX_Observation.csv` (OBX-5) |
| `valueCodeableConcept.text` valor_distinto (ORU-B15) | conversor | Toma `text` de CWE.2; la guía lo toma de CWE.9. | CM `datatype-cwe-to-codeableconcept` |
| `Observation.status` codigo_mal_mapeado (ORU-B20) | conversor | Traduce OBX-11 `D` a `cancelled`; el ConceptMap dice `entered-in-error`. | CM `table-0085` |
| `DiagnosticReport.status` codigo_mal_mapeado (ORU-B22, B31) | conversor | Traduce OBR-25 `I` a `unknown`; el ConceptMap dice `registered`. | CM `table-0123` |

### Señales selladas

**`no_previsto_y_seria_senal`:**
- **`recurso_inventado`:** aparece una vez en el corpus (ORU-B14, el artefacto de L-CV-15).
- **`referencia_rota` en `subject`:** aparece una vez (ORU-B30). Es real.
- **`fhir_invalido` masivo:** no aparece (11 de 263 en Microsoft · ADT).

### Las cuentas, leídas con la adjudicación (informativo; lo juzgado es lo de arriba)

- **Microsoft · ADT:**
  - Los 30 rechazos del corpus son aceptables. Quedan `correcto` 36 (13,7 %) y `rechazo_incorrecto` 42 (16,0 %).
  - Sigue fuera de rango, por MC-ADT-3 y por los dos rechazos reales.
- **LinuxForHealth · ADT:**
  - Si Q-CV-D-13 resulta aceptable, quedan `correcto` 103 (39,2 %) y `rechazo_incorrecto` 0.
  - Si no, se queda como está.
- **Microsoft · ORU-B14:** depende de AMB-CV-10.

## Las muestras (65 por conversor; fuera de los rangos de la previsión)

| | `correcto` | `fallo_silencioso` | `rechazo_incorrecto` | `fuera_de_alcance` |
|---|---|---|---|---|
| Microsoft | 2 | 26 | 1 | 36 |
| LinuxForHealth | 3 | 23 | 3 | 36 |

**Qué son:**
- Los 36 `fuera_de_alcance` son 18 eventos ADT que los PE no cubren (A05, A06, A07…), dos de cada uno.
- Las muestras en alcance son 29 por conversor. Son el material de prueba de los propios proyectos: **no se adjudican en
  CV2**.
- Pasan a CV3, que las compara con las salidas esperadas de cada proyecto. Ahí se comprueba la previsión sellada de que al
  menos el 70 % de lo que cuente será ya_declarada.

**La otra previsión de las muestras se cumple ya:** en las 52 de 2.8 no cuenta ningún hallazgo de tabla ni de estructura
(L18). Los cuatro `valor_imposible_convertido` de las muestras son de las dos muestras ORU 2.5 de Microsoft (`ms-LAB-ORU-1/2`,
PID-30 `NO`, fuera de 0136), que los dos conversores convierten a `deceasedBoolean: false`.

## Candidatas para CV3

Salen del corpus, de mecanismos que no estaban en la lista. CV3 decide, para cada una, si es nueva, ya_declarada o
convención, mirando las salidas esperadas, las pruebas y las incidencias de cada proyecto (solo lectura).

| Id | Conversor | Candidata | Casos |
|---|---|---|---|
| CA-M-1 | Microsoft | `Encounter.location` al punto de cuidado (PL.1), sin el centro enlazado | 184 de 191 Bundles |
| CA-M-2 | Microsoft | Rechaza el nulo `""` en un DTM (probablemente ACC-1) | 18 |
| CA-M-3 | Microsoft | Rechaza caracteres de codificación distintos de los recomendados | 24 |
| CA-M-4 | Microsoft | NM con cero a la izquierda (`01.20`): escribe `"value":01.20`, que es JSON inválido, y la conversión falla. Los ceros no son significativos (`CH02A.txt:2979`). | ORU-B27 |
| CA-M-5 | Microsoft | PID-8 en minúscula o fuera de 0001 copiado a `Patient.gender` (FHIR inválido) | 11 |
| CA-M-6 | Microsoft | `deceasedBoolean: true` sin PID-29 ni PID-30 | 5 |
| CA-M-7 | Microsoft | PID-12 en una Address aparte (con el matiz del comentario de la guía) | 6 |
| CA-M-8 | Microsoft | Dos OBX con el mismo código dan una Observation, y `comparator: "<>"` | ORU-B09 |
| CA-M-9 | Microsoft | Se pierde el OBX que sigue a otro con dos NTE | ORU-B23 |
| CA-M-10 | Microsoft | `subject` a un Patient que no está en el Bundle cuando no hay PID | ORU-B30 |
| CA-L-1 | LinuxForHealth | Sin `Encounter.location` | 160 de 162 Bundles |
| CA-L-2 | LinuxForHealth | `period.start` con la hora del mensaje cuando PV1-44 está vacío | 120 |
| CA-L-3 | LinuxForHealth | `address.line` sin SAD.2 ni SAD.3 | 5 |
| CA-L-4 | LinuxForHealth | PID-8 `N` a `unknown` (la guía dice `other`) | 1 |
| CA-L-5 | LinuxForHealth | TX a `presentedForm`; con OBX mezclados los TX se pierden | ORU-B10, `ms-LRI_2.0-NG_CBC` |
| CA-L-6 | LinuxForHealth | Un OBX sin OBX-2 no da Observation | ORU-B18, B22 |
| CA-L-7 | LinuxForHealth | FT y TM sin valor | ORU-B11, B13 |
| CA-L-8 | LinuxForHealth | `CodeableConcept.text` de CWE.2 y no de CWE.9 | ORU-B15 |
| CA-L-9 | LinuxForHealth | OBX-11 `D` a `cancelled` (la guía dice `entered-in-error`) | ORU-B20 |
| CA-L-10 | LinuxForHealth | OBR-25 `I` a `unknown` (la guía dice `registered`) | ORU-B22, B31 |

**También pasan a CV3 los mecanismos previstos que aparecieron:**
- **Microsoft:** MC-ADT-9, -5, -10, -12, -1 y -4; MC-ORU-1, -2, -6 y -7.
- **LinuxForHealth:** MC-ADT-9, -1, -5, -8 y -4; MC-ORU-4, -2 y -1.
- MC-ADT-3 y MC-ADT-11 ya están desglosados arriba.

**No pasan a CV3 como candidatas:**
- los 30 rechazos de GT1 (corpus);
- los 92 rechazos de LinuxForHealth por evento no soportado (Q-CV-D-13);
- ORU-B14 (AMB-CV-10).

## Lo que queda declarado para CV4 (con la subida de versión del servidor, sin tocar el juez ahora)

- **L-CV-14:** la legalidad solo se mira en la proyección. Un rechazo por un valor imposible en un segmento que el juez no
  proyecta (GT1, ACC…) cuenta como `rechazo_incorrecto`.
- **L-CV-15:** el emparejamiento ORU es por código. Una Observation con el código distinto sale como
  `recurso_ausente` + `recurso_inventado` + `referencia_rota`, en vez de como `valor_distinto` en `code`.
- **AMB-CV-10:** el sufijo de OBX-3 (`71020&IMP`), `CH07.txt:368-372`. Las dos lecturas y lo que cambia: ORU-B14.
- **Q-CV-D-13:** un rechazo por tipo o evento no soportado (200/201), ¿`rechazo_aceptable` como el de versión, o
  `rechazo_incorrecto`? Va a Jev.
- **Redacción:** el hecho «PID-3» en una `referencia_rota` de un mensaje sin PID debe ser «subject».
- **Regla de asignación:** la ruta «falta» de `recurso_ausente` se queda fuera de previsto por construcción. Se dice en la
  previsión de CV4 si la hay, no se cambia ahora.

**Suelto, fuera de la etapa:** el generador de E2 desplaza GT1 un campo en las familias «comp» y «opci» (GT1-2 lleva el
nombre). No
afecta a lo juzgado en etapas anteriores, porque ningún juez anterior proyectaba GT1. No se corrige ahora, porque cambiaría la
huella del corpus sellado.

## Desviaciones de esta fase

| Id | Qué | Por qué |
|---|---|---|
| DV-CV-10 | El corpus se normaliza a CR y sin BOM antes de convertir | El conversor y el juez leen el mismo mensaje, y la trama no es lo que se mide |
| DV-CV-11 | Microsoft corre fichero a fichero (`-n`/`-f`), un contenedor por plantilla | En modo carpeta para en el primer fallo y deja la salida sin postprocesar |
| DV-CV-12 | MSH-9, para elegir la plantilla, se lee con los separadores del mensaje | E2 trae mensajes con `#$%*!` |
| Repetición 1 | J1, J2, J3, J5 en el juez (`3408647`) | Defectos del juez hallados al adjudicar la pasada 0 |

## Siguiente: CV3

Para cada candidata y cada mecanismo previsto que apareció, CV3 decide si es nueva, ya_declarada o convención. Mira, solo con
`gh api` de lectura:
- las salidas esperadas y las pruebas de cada proyecto;
- sus incidencias;
- la documentación de la versión fijada.

**Primero las de más casos:** CA-M-1, CA-L-1, CA-L-2, CA-M-2/3. Una candidata se confirma como nueva solo si, además, se
reproduce con un mensaje mínimo en la caja. Las muestras en alcance se adjudican allí.
