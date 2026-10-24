# CV3: cada discrepancia con su cita, frente a lo que declara cada proyecto (24-oct-2026)

**CV3 hecho.** El verificador encuentra **15 discrepancias nuevas y confirmadas**:
- 5 en Microsoft y 10 en LinuxForHealth;
- 7 de ellas, fuertes (un valor multiplicado por diez, un resultado que desaparece, un rango que pasa a ser un número…).

Además:
- **ve 31 ya declaradas** por los proyectos, que son el control positivo;
- **16 diferencias son convención**;
- quedan **2 rechazos nuevos**, que no entran en la frase porque fallan a la vista;
- y **3 dudosas**, que no cuentan.

Cada nueva:
- tiene su cita en la guía;
- cambia el significado del dato (una de las ocho clases de S-CV-5);
- no está declarada en ninguna salida esperada, prueba, documentación, comentario de plantilla, issue ni comentario de issue;
- se reproduce con un par mínimo (caso y control) en la caja.

**Una revisión adversaria independiente intentó romper las 25 candidatas y tumbó 10.** Todo lo que cuenta lo juzga el juez final
`54a90cd9…`, tras los dos rejuicios que permite el diseño.

**Para la regla de portfolio:** hay al menos una discrepancia nueva y confirmada, así que el verificador **no** se declara pieza
de portfolio. CV4 lo cierra con la frase. Lo siguiente (publicarlo, abrir issues, otra etapa) lo decide Víctor, y nada sale sin
su visto bueno (condición 6).

| | |
|---|---|
| Juez final | `54a90cd9e08d…` (rejuicio 2 de CV3). Corpus `aa83359a…`; conversores con las huellas de CV1 |
| Clasificación, caso a caso | `cv/CLASES-CV3.json` (lo escribe `cv/cv3_clases.py` con las reglas, cada una con su referencia) |
| Pares mínimos | `cv/cv3/minimos/` (34 pares, v2.5 sintéticos); resultado en `cv/RESULTADO-CV3-minimos.json` (`cv/cv3_minimos.py`) |
| Salidas esperadas de Microsoft, juzgadas | `cv/cv3_esperadas_ms.py`; detalle en `privado/cv/cv3/esperadas_ms.jsonl` |
| Rejuicios del corpus | `cv/RESULTADO-CV3-rejuicio1.json` y `-rejuicio2.json`; detalle en `privado/cv/cv3/` |
| Material de los proyectos (solo lectura) | **Microsoft:** el código fijado de CV1 (`253307f`), con sus pruebas, salidas esperadas y `docs/`. **LinuxForHealth:** 54 ficheros de la etiqueta `v1.1.0` leídos con `gh api` y las plantillas del jar. **Issues y PR:** 1.120 (587 + 533) y 879 comentarios (565 + 314), leídos el 24-oct; en `privado/cv/cv3/proyectos/` |
| Decisiones de Jev | `cv/decision-jev-qcv-cv3.md` (estado neutro en `cv/estado_qcv_cv3.md`) |

## Cómo se clasificó

La regla es la de §4.3 del diseño, escrita antes de medir.

**1. `ya_declarada`.** El proyecto muestra la misma diferencia como comportamiento querido. Se buscó así:
- **Las salidas esperadas de Microsoft se juzgaron con el mismo juez.**
  - Son 62 muestras, y dan los mismos hallazgos que la conversión real de CV2.
  - Un mecanismo que aparece en ellas está publicado como querido.
- **Además:** las pruebas, la documentación y los comentarios de plantilla de los dos proyectos, y todos los issues y PR con sus
  comentarios.
- **Una lectura fijada al empezar CV3:**
  - una tabla de mapeo en el código, sin comentario ni prueba, **no** es una declaración, porque es el código mismo;
  - un comentario de plantilla que describe el comportamiento **sí** lo es.

**2. `convencion`.** Releídos la hoja CSV y el ConceptMap, la guía admite lo observado. Se corrigió el juez con la prueba en rojo
primero y se volvió a juzgar el corpus entero. Se hicieron los dos rejuicios, el máximo:

| Rejuicio | Juez | Qué | Prueba | Efecto |
|---|---|---|---|---|
| 1 | `198cebdd` | **DV-CV-13:** NM «5.» vale 5 con la misma precisión; JSON no admite «5.» | P-CV-22 | En el corpus solo cambia LinuxForHealth ORU-B29, que pierde MC-ORU-1 |
| 1 | | **DV-CV-14:** en FT, «\.br\» es «Begin new output line» (`CH02.txt:1063`); se admite un salto de línea | P-CV-23 | Ninguno: Microsoft no escribe un salto de línea, sino los dos caracteres «\n» |
| 2 | `54a90cd9` | **DV-CV-15:** la hoja del segmento fija el tipo «VN» en PV1-19 (`PV1_Encounter.csv:43`), y el mapa de CX da CX.5: la guía admite los dos | P-CV-24 | El corpus, igual; 26 muestras pierden el hallazgo de Encounter.identifier |
| 2 | | **DV-CV-16:** un PL hecho solo de separadores («^^») no está valorado | P-CV-25 | Una muestra |

En los dos rejuicios:
- todas las suites siguen en verde;
- la regresión de 2.721 sigue en CASA;
- la concordancia de A1 no cambia.

**3. `nueva`.** En cualquier otro caso. **Se confirma con un par mínimo:**
- **El par:** el caso trae solo el disparador; el control es el mismo mensaje sin él.
- **Cómo se corre:** los dos conversores, en su caja.
- **Cómo se juzga:** con el juez final.
- **Cuándo se confirma:** si el hallazgo sale en el caso y no en el control.
- **El resultado:** se confirman 31 de los 34 pares.
  - Dos de los que no confirman son diagnósticos a propósito: el PDA en A01 y la NTE al final.
  - El tercero quitó una candidata: LinuxForHealth sí prefiere XTN.12.

**4. La revisión adversaria (DV-CV-17).**
- **Quién:** dos agentes, uno por conversor, sin la conclusión de quien clasificó. Trabajaron en solo lectura e intentaron
  romper cada nueva por cuatro vías: el mínimo, la guía, el proyecto y el significado.
- **Por qué Opus:** se encargó primero a Fable, que devolvió error 500 del servidor cuatro veces seguidas; se repitió con Opus,
  con el mismo encargo.
- **El resultado:**
  - cayeron 10;
  - una quedó dudosa;
  - la revisión encontró un falso positivo del juez (CX.4).

**5. Los issues, completos (DV-CV-18).**
- **El fallo:** la primera lectura cortaba los cuerpos a 4.000 caracteres y no traía los comentarios. Así se escapó M-21, que
  estaba declarada en los comentarios del #325.
- **El arreglo:** se releyeron los cuerpos completos y los 879 comentarios contra cada nueva que quedaba. No salió ninguna más.

**6. Las preguntas de diseño, a Jev, con el estado neutro:**

| Q | Qué | Decisión | Efecto |
|---|---|---|---|
| Q-CV-D-13 | Rechazo de un evento no soportado | **incorrecto** (0,78) | Ninguno: LinuxForHealth lo declara (L-4) |
| Q-CV-D-14 | PL.9 dentro de una descripción concatenada | **cuenta** (0,97) | Ninguno: Microsoft lo declara (M-4) |
| Q-CV-D-15 | El formato del número de teléfono | empate: **dígitos** 0,49, **literal** 0,48 | Queda dudosa y no cuenta |
| Q-CV-D-16 | El filtro de comparadores de LinuxForHealth con «<>» | nueva, no preguntada | Queda dudosa (L-21) |

## Las 15 nuevas y confirmadas

Están ordenadas por fuerza. Las citas de la guía son de las hojas CSV del commit `873b331` y de los ConceptMap del paquete 1.0.0.

| Id | Conversor | Discrepancia | Casos | Guía | Par mínimo | Fuerza |
|---|---|---|---|---|---|---|
| M-24 | Microsoft | NM «.5» se escribe **5**: el valor se multiplica por diez. La plantilla emite `"value":.5`, y el postproceso del JSON lo recupera como 5 | ORU-B29 | `CH02A.txt:2958` (NM admite «.5»); `OBX_Observation.csv` (NM → valueQuantity) | M01 | fuerte |
| M-23 | Microsoft | ORU sin PID: `subject` apunta a «Patient/364bf61f…», que no está en el Bundle. Es el mismo id en ORU-B30 y en el mínimo: todos los mensajes sin PID quedan colgados del mismo paciente inexistente | ORU-B30 | `MSG_ORU_R01.csv:14,67-69` (Patient[1] solo desde PID) | M07 | fuerte |
| M-18 | Microsoft | En ADT^A02, un PDA sin datos (`PDA\|""`) da `deceasedBoolean: true`, sin PID-29 ni PID-30. En A01 no pasa | 5 (A02 «nulos») | `PID_Patient.csv:50-51`; PDA sin destino (`MSG_ADT_A01.csv:81`) | M03 (y M03b, el control en A01) | fuerte |
| L-10 | LinuxForHealth | PID-16 «A» (separado) se escribe en v3-MaritalStatus como «A», que allí es **anulado**; la guía da «L» | 2 | CM `table-hl70002-to-v3-maritalstatus` | L02 | fuerte |
| L-15 | LinuxForHealth | Un OBX sin OBX-2 y sin valor (resultado no obtenible «X», o pendiente «I») no da Observation. Va contra la guía y contra el comentario de su propia plantilla («OBX.2 is null/empty … CREATE») | ORU-B18, B22 | `MSG_ORU_R01.csv:67`; `CH07.txt:2574` (OBX-2 es condicional) | L06 | fuerte |
| L-16 | LinuxForHealth | Los valores FT y TM se pierden: valueString solo existe para ST, y no hay valueTime | ORU-B11, B13 | `OBX_Observation.csv:9,19` | L07, L08 | fuerte |
| L-20 | LinuxForHealth | SN «^1^-^5» (rango) se escribe como valueQuantity **1** | ORU-B07 | `OBX_Observation.csv:22` (SN con «-» → valueRange); CM `datatype-sn-to-range` | L11 | fuerte |
| M-7 | Microsoft | De PV1-8 repetido, solo la primera repetición llega a participant | 8 | `PV1_Encounter.csv:18-21` (PV1-8, 0..*) | M04 | media |
| L-1 | LinuxForHealth | No hay Encounter.location: `Encounter.yml` no la mapea, y de PV1-3 solo queda PL.4 como Organization | 160 + 15 muestras | `PV1_Encounter.csv:7-9` | L01 | media |
| L-11 | LinuxForHealth | SAD.2 y SAD.3 de XAD.1 no llegan a address.line | 5 + 12 muestras | CM `datatype-sad-to-address` (SAD.1-3 → line[1-3]) | L04 | media |
| L-12 | LinuxForHealth | PID-8 «N» se escribe «unknown»; la guía da «other» | 1 | CM `table-hl70001-to-administrative-gender` | L05 | media |
| L-18 | LinuxForHealth | OBX-11 «D» se escribe «cancelled»; la guía da «entered-in-error» | ORU-B20 | CM `table-hl70085-to-observation-status` | L09 | media |
| L-19 | LinuxForHealth | OBR-25 «I» se escribe «unknown»; la guía da «registered» | ORU-B22, B31 | `OBR_DiagnosticReport.csv:33`; CM `table-hl70123` | L10 | media |
| L-22 | LinuxForHealth | PV1-52 no llega a participant (PART) | 10 muestras | `PV1_Encounter.csv:80-83` | L13 | media |
| M-10 | Microsoft | PID-16 «T» (no declarado) no da maritalStatus; la guía da NullFlavor NAVU | 1 | CM `table-hl70002-to-v3-maritalstatus` | M08 | débil |

**Matices que deja la revisión:**
- **M-18:** vale para un PDA sin datos de muerte. Con un PDA relleno, inferir la muerte es razonable.
- **L-11:** el mínimo pone texto artificial en SAD.2 y SAD.3. La pérdida es la de la guía, pero su peso depende de lo que traigan.
- **L-22:** PV1-52 está marcado «B» en v2.5, pero sigue siendo válido.
- **L-1:** el ejemplo de salida de `TEMPLATING.md` trae un Encounter sin location, pero no publica la entrada: no declara nada.
- **L-12 y L-19:** se apoyan en elecciones de la propia guía. Para «no aplicable», tanto «other» como «unknown» pierden algo.
  L-19 usa el mapa de la 0123 de consultas.

## Las 10 que cayeron en la revisión, y las que cayeron antes

| Id | Por qué cae | Cita |
|---|---|---|
| M-9 | **No cambia el significado:** v3-ActCode «OBS» es «Obstetrics», el mismo concepto que v2-0004 «B» | CodeSystem v3-ActCode (`_ActMedicalServiceCode`) |
| M-16 | **Ya declarada:** que un código sin mapeo pase tal cual es comportamiento querido; de ahí sale PID-8 «Z» en gender | microsoft/FHIR-Converter#187 (cerrado) |
| M-21 | **Ya declarada:** una NTE tras un OBX hace perder el OBX siguiente; `get_related_segment_list` solo da segmentos consecutivos | microsoft/FHIR-Converter#325, en sus comentarios |
| M-25 | **Ya declarada:** la prueba afirma que «\.br\» pasa a los dos caracteres «\n» | `…UnitTests/InputProcessors/Hl7v2EscapeSequenceProcessorTests.cs:32` |
| L-6 | **Ya declarada:** el ejemplo de salida publica serviceType v2-0069 «MED» | `TEMPLATING.md:519-525` |
| L-21 | **Dudosa (Q-CV-D-16):** la plantilla declara que quita los comparadores que FHIR no admite, y lo prueba con «=». Con «<>» invierte el sentido («distinto de 5» pasa a ser «5»), pero eso no lo dice | `hl7/datatype/Quantity.yml:13`; `Hl7ObservationFHIRConversionTest.java:144` |
| L-23 | **Ya declarada:** la prueba afirma que no pone el título en suffix, y usa la misma plantilla HumanName | `Hl7ObservationFHIRConversionTest.java:622` |
| L-24 | **Falso positivo del juez:** el Bundle sí trae system, «urn:id:NIST_MPI». El juez busca «NIST MPI» literal | Bundle del par L16 |
| L-25 | **No cambia el significado:** «NO» y false dicen lo mismo | CM `table-hl70136-to-special-values` |
| L-26 | **Ya declarada:** la prueba afirma unit = OBX.6.1 | `Hl7ObservationFHIRConversionTest.java:141` |

**Antes de la revisión, por el mismo camino:**
- **M-4 pasa a ya declarada:** la descripción concatenada está en 114 salidas esperadas (`_PLLocation.liquid:62-63`).
- **M-36 pasa a falso positivo del juez:** es el mismo de L-24, ahora con «…/Identifier/NIST-MPI».
- **La candidata de XTN.12 de LinuxForHealth se retira:** la cumple.

## Las 31 ya declaradas: el verificador ve lo que los proyectos ya saben

**Microsoft (19):**

| Id | Qué | Dónde lo declara |
|---|---|---|
| M-1 | Encounter.location al componente menos granular | salidas esperadas (52) e **issue #624** (abierto) |
| M-2, M-3 | location.status distinto, o ausente | salidas esperadas |
| M-4 | PL.9 dentro de la descripción concatenada | salidas esperadas (114) |
| M-5 | PV1-10 sin system | salidas esperadas |
| M-6 | Encounter.status «in-progress» | salidas esperadas |
| M-8 | PV1-45 sin period.end | salidas esperadas |
| M-13 | Rechaza el escape distinto de «\» | prueba `Hl7v2DataValidatorTests.cs:51` |
| M-16 | gender «Z» | #187 |
| M-17 | PID-12 en una dirección aparte | salidas esperadas |
| M-19, M-20 | Choque de id entre dos OBX con el mismo código, y comparator «<>» | `docs/HL7v2-ImportantPoints.md` punto 5, e **issue #504** |
| M-21 | El OBX perdido tras una NTE | #325 |
| M-25 | FT «\n» literal | prueba unitaria |
| M-26 | ContactPoint.use | salidas esperadas |
| M-28 | Observation de PDA | salidas esperadas |
| M-30 | DiagnosticReport de un OBX RP/ED | salidas esperadas |
| M-31 | period.end sin PV1-45 | salidas esperadas |
| M-35 | PID-30 «NO» | salidas esperadas |

**LinuxForHealth (12):**

| Id | Qué | Dónde lo declara |
|---|---|---|
| L-2 | period.start desde EVN | prueba `testEncounterPeriod` |
| L-3 | Encounter.status por fechas | `Hl7RelatedGeneralUtilsTest.java:76-100` |
| L-4 | Rechazo de A02, A11 y A13 | `README.md:7-26` |
| L-5 | class sin system | `test_encounter_class` |
| L-6 | serviceType v2-0069 | `TEMPLATING.md` |
| L-7, L-8 | ContactPoint.system y use | **issue #524** (abierto) |
| L-13 | OBX-8 v2-0078 | `Hl7ObservationFHIRConversionTest.java:161-163` |
| L-14 | TX a presentedForm, que se pierde con OBX mezclados | `DiagnosticReport.yml:139-141` y #306 |
| L-17 | text desde CWE.2 | #139 |
| L-23 | El título, fuera de suffix | prueba |
| L-26 | unit desde CWE.1 | prueba |

## Las 16 convenciones

**Son 14 mecanismos de nota de nivel convención del juez final.** Por cada conversor:
- status sin destino en el ConceptMap (OBX-11, OBR-25);
- OBX-5 repetido en una forma que la guía admite;
- interpretation y maritalStatus fuera del ConceptMap;
- gender en minúscula (AMB-CV).

**Las otras 2 son PV1-19 «VN»**, una en cada conversor (DV-CV-15).

## Lo que no cuenta, y por qué

**Rechazos nuevos (2).** No entran en la frase: un rechazo no es de las ocho clases y falla a la vista.
- **M-12:** Microsoft rechaza el nulo «""» en un DTM (ACC-1; `CH02.txt:392`). Son 18 casos, par R01.
- **M-15:** con NM «01.20», Microsoft escribe JSON inválido y falla (`CH02A.txt:2979`). Par R02.

**Dudosas (3), que pasan a Q-CV-D:**
- **M-27 y L-9:** el formato del teléfono (Q-CV-D-15, empate de Jev);
- **L-21:** el comparador «<>» (Q-CV-D-16).

**Fuera, con motivo:**

| Motivo | Ids | Qué |
|---|---|---|
| Corpus | M-11 | 30 rechazos por GT1 desplazado en E2 |
| Ambigüedad | M-22 | AMB-CV-10, el sufijo «&IMP» |
| Versión (L-CV-16) | M-32, M-33, M-34 | XAD.9 CWE, XAD.19 y XPN.15 en muestras 2.8 |
| Muestra inválida | M-14, M-29 | MSH-2 con dos barras; OBX-3 vacío |
| Falso positivo del juez | M-36, L-24 | CX.4 |
| No cambia el significado | M-9, L-25 | |

## La previsión sellada, frente a lo que salió

**Las muestras aceptadas**, las 10 en que el juez espera AA, son todas de Microsoft. La previsión decía «≥ 70 % de lo que cuente
será ya_declarada (son sus propias pruebas)»:
- **Microsoft, sobre sus propias pruebas:** 75 de 93 (80,6 %). Las otras 18 dependen de componentes posteriores a 2.5. Se cumple.
- **LinuxForHealth, sobre esas mismas muestras:** 36 de 65 (55,4 %).
- **Los dos juntos:** 111 de 158 (70,3 %).

**La frase prevista:**

| Pieza | Previsto | Salió |
|---|---|---|
| N | ≥ 2 | 15 |
| K | 1 o 2 | 2 |
| D | ≥ 3 | 31 |
| C | ≥ 10 | 16 |

**La frase, en borrador para CV4:** «El verificador encuentra 15 discrepancias nuevas y confirmadas en 2 de 2 conversores, sobre 368
mensajes públicos; además ve 31 de las ya declaradas, y 16 diferencias son convención».

## Desviaciones de CV3

| Id | Qué |
|---|---|
| DV-CV-13..16 | Los dos rejuicios del juez por la regla 2 (arriba), con P-CV-22..25 |
| DV-CV-17 | La revisión adversaria se hizo con Opus: Fable devolvió error 500 cuatro veces |
| DV-CV-18 | Los issues se releyeron completos y con sus comentarios, tras ver que la primera lectura los cortaba |
| Lectura de la regla 1 | Una tabla de mapeo sin comentario ni prueba no es declaración; un comentario de plantilla sí. Se fijó al empezar a clasificar |

## Para CV4 (sin tocar ahora el juez de los resultados sellados)

**Cambios del juez, con la subida de versión del servidor:**
- **CX.4:** comparar el espacio de nombres con system normalizando espacios y signos. Quita los falsos positivos M-36 y L-24.
- **Q-CV-D-14:** la descripción con PL.9 dentro debe salir como `valor_distinto`, no como «falta».
- **Declarar:** L-CV-14 (la legalidad, solo en la proyección), L-CV-15 (el emparejamiento por código), L-CV-16 (los
  componentes posteriores a 2.5 en muestras de otras versiones) y AMB-CV-10.
- **Redacción:** el hecho «subject» en un mensaje sin PID.

**Q-CV-D-15 y Q-CV-D-16 siguen abiertas.**

**El cierre:**
- `RESULTADO-CONVERSORES.md` con la frase;
- el MCP con lo nuevo declarado;
- reiniciar `verificador-mcp`;
- la guarda en LIMPIO.

**Publicar o abrir issues:** solo con el visto bueno de Víctor.

**Sueltos:**
- el generador de E2 desplaza GT1 en las familias «comp» y «opci»;
- hay dos muestras de LinuxForHealth mal formadas, que no se tocan porque son de terceros.
