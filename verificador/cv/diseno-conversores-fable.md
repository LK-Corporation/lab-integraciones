> *Copia pública: se quitaron las alusiones al trabajo del autor y la cola de lo que solo él decide. El resto es el original del laboratorio.*

<!-- modelo: Claude Fable 5.1 (claude-fable-5-1); fecha: 23-oct-2026; «CV0: el verificador ante conversores HL7 v2 → FHIR de terceros (14l); a ciegas de lo que devuelven los conversores; leído solo caja-cv0» -->

# Diseño CV0: punto de entrada de solo transformación, lector de la salida de un conversor y perfil «guía»

Documento público. Sin credenciales, sin nombres de máquinas ni de personas, sin datos de pacientes (los ejemplos usan `X1`/`V1`/`M1`).
Nombra los dos conversores (Microsoft FHIR-Converter y LinuxForHealth hl7v2-fhir-converter) y la guía HL7 v2-to-FHIR (ConceptMap del
paquete 1.0.0; hojas CSV del commit `873b331`). **No sé qué devuelven los conversores**: todo lo que sigue sale del estándar, de la guía y
del juez tal como está en esta carpeta.

Convenciones: **S-CV-n** decisión propuesta (pasa a S-n cuando Jev decida); **R-CV-n** regla implementable; **P-CV-n** prueba en rojo
antes del código, con su control negativo; **L-CV-n** límite declarado; **AMB-CV-n** lectura adoptada donde la guía o el estándar admiten
dos; **Q-CV-D-n** pregunta de diseño (Jev); **Q-CV-A-n** pregunta de alcance; **DV-CV-n** queda reservada a quien implemente. Citas:
`fichero:línea` dentro de esta carpeta; un ConceptMap se cita por su nombre y el elemento (`CM datatype-cx-to-identifier CX.1 → value`);
una hoja de la guía por `guia_csv/<hoja>.csv:fila`; FHIR R4 por el `id` del elemento en su StructureDefinition y la línea del snapshot.
Las S-n del laboratorio se citan **solo** en notas de convención (para explicar por qué algo no cuenta), nunca en un hallazgo que cuente
(`resultados/ANTES-ETAPA-CONVERSORES.md:45-48`).

Punto de partida fijado: la pregunta (`ANTES-ETAPA-CONVERSORES.md:14-18`), las condiciones 1-6 (`:40-53`), Q-CV-1..5 (`:72-80`), la regla
de pieza de portfolio (`:108-122`) y el tope (`:103-106`). CV-pre midió: los elementos proyectados coinciden con la guía (20/20 y 21/21,
`RESULTADO-CV-PRE.md:18-21`); el hueco está en el **valor esperado** de ADT (70 filas sin cita de la guía, `:28-31`) y en las 6 filas de
convención de ORU (`:31`); las muestras de los conversores dan 10 mensajes aceptados y plantean la pregunta de MSH-9.3 (`:55-63`).

---

## 0. Resumen de las decisiones que lo condicionan todo

| | Decisión | Por qué (cita) |
|---|---|---|
| S-CV-1 | **Dos puntos de entrada nuevos de solo transformación**, `adt_conv` y `oru_conv`, con el contrato de la familia (los `tipos`, `consumidos` y `p5` de `adt_fhir` y `oru_fhir`) y una clave nueva `solo_transformacion = True`. El juez despacha por esa clave **antes** de leer acuse, log, entorno o canónico: con cualquier otro PE el verificador es idéntico byte a byte. | El PE es «el contrato del receptor como datos» (`verificador/puntos_entrada.py:3-8`); el conversor es un receptor sin acuse. Misma técnica de aislamiento que `verificador.py:268-277` para `oru`/`adt`. Condición 5: el juez no cambia para los PE de los resultados sellados (`ANTES:51-52`). |
| S-CV-2 | **La evidencia de un caso es `{mensaje, punto_entrada, conversion}`**: sin `ack`, sin `sesiones`, sin `entorno` ni `conexion`. `conversion` trae quién convirtió (nombre, versión, huella) y qué devolvió (`bundle` como TEXTO, o `error`). | Un conversor «recibe un mensaje y devuelve un Bundle, o un error» (`ENCARGO-CV0.md:52-53`). El Bundle se lee como texto para no perder la precisión decimal (D-ORU11-2, `verificador/almacen_oru.py:322-332`), que FHIR R4 declara significativa (§4.2). |
| S-CV-3 | **Lo esperado es la proyección «guía»**: una tabla de datos (`PERFIL_GUIA_ADT`, `PERFIL_GUIA_ORU`) que dice, por elemento proyectado, el valor que mandan los ConceptMap, con tres niveles: `cuenta`, `convencion` (la guía admite más de una representación) y `forma` (no es dato). Se calcula desde el mensaje reutilizando los lectores de los mapeadores (`mapeador_adt.Lector`, `mapeador_oru.agrupar`/`_observacion`), **no** desde el canónico del laboratorio. | Q-CV-3 (`ANTES:78`): el valor esperado sale «de los mapas de tipos de datos y vocabularios de la guía»; las S-n no cuentan. Las 70 filas de ADT sin cita (`RESULTADO-CV-PRE.md:30`) y las 6 de convención de ORU (`:31`) son exactamente lo que separa el canónico del laboratorio de la guía. |
| S-CV-4 | **El lector empareja por papel, no por los identificadores del laboratorio**: el Patient del mensaje, el Encounter de su PV1, el DiagnosticReport de cada OBR y la Observation de cada OBX, resolviendo las referencias dentro del Bundle (`fullUrl`, `urn:uuid`, `Tipo/id`). | Los recursos de un tercero no llevan `urn:lab:integraciones:*` (`ENCARGO:59-61`); la guía fija las referencias internas (`guia_csv/MSG_ADT_A01.csv:36` «Encounter[1].subject.reference = Patient[1].id»; `MSG_ORU_R01.csv:67-69` «DiagnosticReport.result.reference = Observation[2].id»); FHIR R4 fija cómo se resuelven (`estandar/fhir_r4/bundle.profile.json:803-806`). |
| S-CV-5 | **«Cambia el significado del dato»** = una de ocho clases operativas (valor distinto, dato perdido, dato inventado, código mal mapeado, valor imposible convertido, recurso ausente/duplicado/inventado, referencia rota, FHIR inválido), cada una definida sobre la proyección «guía» (§4.1). Todo lo demás es forma (§4.2) y no cuenta. La clase `nueva` / `ya_declarada` / `convencion` la pone CV3, no el juez (§4.3). | Regla de portfolio (`ANTES:110-112`): «confirmada quiere decir que tiene cita, cambia el significado del dato, el proyecto no la tiene declarada y se reproduce con un mensaje público». |
| S-CV-6 | **La versión que manda es la escrita en MSH-12**. Los mapas de la guía no dependen de la versión v2 (sus `group.source` son los sistemas de códigos v2 sin versión): un código que está en la tabla de v2.5 se juzga con certeza literal en cualquier versión; la legalidad de un código o estructura **fuera** de las tablas de v2.5 no se juzga en mensajes ≠ 2.5 (certeza `ambiguedad L18`, no cuenta). MSH-9.3 nunca cuenta en este punto de entrada (§5). | MSH-12 «is matched by the receiving system to its own version» (`estandar/hl7v25_CH02.txt:4512-4513`); el texto de HL7 posterior a 2.5 no está en la evidencia (L18, `verificador/info_verificador.json:384`); el conversor no acusa, así que 200/203 no existen aquí. |
| — | **Lo que no cambia:** `acuse_referencia`, `lectura_evidencia`, `mapeador_referencia`, `mapeador_adt`, `mapeador_oru`, `almacen_adt`, `almacen_oru` (se importan, no se editan); los PE existentes; los RESULTADO sellados y la huella con que se juzgaron. | Condición 5 (`ANTES:51-52`); `diseno-verificador-ve-fable.md:27` (misma política en 14k). |

---

## 1. El punto de entrada de solo transformación

### 1.1 La forma de la evidencia (R-CV-1)

Un caso = un mensaje = una invocación del conversor. Esquema nuevo en `verificador/esquema_evidencia.json` (hermano de `:3-8` y `:340-354`)
y en `E_PROPS` del MCP (`verificador/mcp_verificador.py:1068`):

```
{"punto_entrada": "adt_conv" | "oru_conv",
 "mensaje": "<cable HL7 tal cual, CR como salto de línea, BOM tolerado (esquema :7)>",
 "conversion": {
   "conversor": {"nombre": "microsoft-fhir-converter" | "linuxforhealth-hl7v2-fhir-converter" | "<otro>",
                 "version": "<etiqueta publicada>", "huella": "<sha256 del artefacto fijado>",
                 "plantilla": "<la que eligió el arnés, si la hay>", "invocacion": "<línea de mando, sin rutas de máquina>"},
   "salida": {"estado": "bundle" | "error" | "vacio" | "sin_respuesta",
              "bundle": "<JSON del Bundle TAL CUAL, texto>",            # solo con estado = bundle
              "error": {"codigo": "<salida/HTTP>", "texto": "<≤ 4000 car.>"},  # solo con estado = error
              "duracion_ms": 123},
   "perfil_valor": "guia"}                                               # único valor en CV; «lab» es L-CV-12
```

- `ack`, `sesiones`, `entorno`, `conexion` **pueden venir** (el esquema los admite) pero el punto los **ignora con una nota**
  `evidencia_ignorada` que no cuenta: aquí no hay acuse que juzgar (`ENCARGO:52-53`).
- `salida.bundle` se guarda como texto y se lee con `parse_float=str, parse_int=str` (reutilizando `almacen_oru.parsear`, `:322-332`).
- Un cable con **más de un MSH**: solo se juzga el primero y se anota `mensaje_extra` (un conversor transforma un mensaje; Q-CV-D-1).
- El arnés que corre el conversor en la caja (CV1) escribe `estado = sin_respuesta` ante timeout o caída del proceso, `vacio` si el
  conversor terminó sin error y sin cuerpo; nunca inventa un `error`.

### 1.2 Qué reglas del juez aplican y cuáles no (R-CV-2)

| Pieza del juez de hoy | En `adt_conv` / `oru_conv` | Por qué |
|---|---|---|
| Lectura del cable: marcos MLLP, bytes `<0xNN>`, separadores, escapes §2.7 (`mapeador_referencia.mensajes`, `descodificar`, `Msg.desescapa`) | **Aplica tal cual** | Es la lectura del estándar (`CH02.txt` §2.5-§2.7), no una decisión del sitio. |
| P2 del acuse (tipo/evento/estructura/versión, `acuse_referencia.py:480-524`) | **No aplica como acuse.** Se reutiliza solo `PE.estructura_de(m, pe)` (`puntos_entrada.py:156-161`) para saber si el evento está en alcance y con qué estructura de la 0354 se lee. | Sin acuse no hay 200/201/203. Lo que el juez no aceptaría se trata en §1.3. |
| P4/P5 del acuse (campo obligatorio vacío, tipo de dato, tabla) | **No aplica como acuse.** Los «imposibles» del mapeador (`esperado_mensaje` → `imp`: valor fuera de tabla HL7, DTM/NM inválido, control C0) **sí** se usan: fijan la clase `valor_imposible_convertido` (§4.1) y marcan como «no juzgar» (`None`) la hoja afectada. | El mapeador ya calcula ambos (`mapeador_adt.py:614`, `mapeador_oru.py:351-461`); son hechos del estándar (tabla 0001, DTM), no del sitio. |
| Log L01-L16, entorno, conexión, trama D0 (`lectura_evidencia.py:33-53`) | **No aplica** | No hay circuito ni destino. |
| Canónico y `fidelidad/guardado`, `sin_canonico` (S104) | **No aplica** | No hay canónico (`ENCARGO:53`). |
| Proyección del esperado a FHIR (`mapeador_adt.proyectar`, `almacen_oru.proyectar_*`) | **Aplica como base**, pero sustituida por la proyección «guía» (§3) en todo lo que el laboratorio decidió por su cuenta. | S-CV-3. |
| Comparación hoja a hoja (`almacen_oru._hojas` `:413-433`, `comparar_recurso` `:464-511`; `almacen_adt.comparar_recurso` `:103-124`) | **Aplica**, con tres cambios: (a) el esperado puede ser un **conjunto admitido** (tupla), como ya hace S22; (b) hojas de nivel `convencion`/`forma` no generan hallazgo que cuente; (c) comparación de fechas por instante cuando el DTM traía zona (§3.6). | Es el motor de v1.1/A1b; lo nuevo es la tabla de niveles. |
| `fusionar` y precedencia (`verificador.py:499-526`, `:70`) | **Aplica** (clave `(mensaje, hecho)`) | Un hallazgo por campo del mensaje, como siempre. |
| `veredicto` (`verificador.py:536-583`) | **No aplica**: tiene su propio cálculo (§1.4), sin MSA-1. | Las categorías de hoy nacen del acuse. |
| Certezas (`CERTEZA`, `verificador.py:73`) | **Aplica** la misma escala: `literal`, `ambiguedad AMB-CV-n`, `ambiguedad L18`, `decision_pendiente Q-CV-D-n`, `lectura`. | Leyenda `info_verificador.json:336-343`. |
| Datos personales (`ocultar_datos_personales`) | **Aplica** al mensaje y al Bundle. | Regla R6 de ORU; nunca se publica un recurso con datos reales. |

### 1.3 Qué pasa con un mensaje que el juez no aceptaría (R-CV-3)

| Caso | Qué hace el punto | Cuenta | Cita |
|---|---|---|---|
| Tipo o evento fuera de los `tipos` del PE (A05, A14, ORM, SIU…) | Categoría **`fuera_de_alcance`**; el Bundle no se juzga; nota con el evento. | no | Q-CV-2 (`ANTES:77`); L-ADT-2 (`info_verificador.json:417`). El tercero puede convertirlo bien, pero el juez no tiene esperado. |
| MSH-9.3 valorado y distinto de la estructura que la 0354 de v2.5 asigna al evento (`ADT^A04^ADT_A04`) | Se lee con la estructura **del evento** (la 0354 de v2.5: `CH02.txt:6060-6061`, «ADT_A01 describes the single abstract message structure used by A01, A04, A08 and A13»; `:6067`); nota `estructura_declarada` con las dos. | no (§5.2) | El dato está en el mensaje de muestra, no en la conversión (`RESULTADO-CV-PRE.md:58-62`). |
| MSH-9.3 vacío | Igual: estructura del evento (AMB-MT-1, `info_verificador.json:226-230`); sin nota. | no | — |
| MSH-12 distinto de 2.5 (2.3, 2.4, 2.5.1, 2.6, 2.8) | Se juzga. Todo hallazgo que dependa de que un valor esté o no en una tabla de v2.5, o de la estructura de v2.5, lleva certeza `ambiguedad L18` y **no cuenta**; los mapeos de la guía sí cuentan (§5.1). | parcial | S-CV-6. |
| MSH-12 vacío o sin forma N.N | Se juzga como 2.5 (la única versión con texto en la evidencia) y nota `version_ausente`. | no la nota | L17 (`info_verificador.json:383`). |
| Falta EVN/PID/PV1 (ADT) o OBR (ORU); PID repetido | Si el conversor devuelve `error`: **`rechazo_aceptable`** (nota); si devuelve Bundle: se juzga lo que haya; la ausencia de Patient/Encounter sin su segmento **no** es `recurso_ausente`. | no | §2.6.2 b-c (`CH02.txt:936-938`): lo ausente se trata como no presente; un conversor puede rechazarlo o no. |
| Segmento conocido fuera de sitio (OBX tras AL1), segmentos Z, repeticiones de más | Se **ignoran** al calcular el esperado; un `error` del conversor por ello es **`rechazo_incorrecto`** (cuenta). | sí | §2.6.2 a) (`CH02.txt:934-935`): «ignore segments… that are present but were not expected». |
| Valor imposible en un campo consumido (PID-8 ∉ 0001, PID-7 inválido, OBX-5 NM no numérico) | Si el conversor devuelve `error`: **`rechazo_aceptable`** (Q-CV-D-7). Si devuelve Bundle: la hoja afectada se espera **ausente**; si trae el valor imposible o un mapeo inventado → `valor_imposible_convertido` (cuenta). | según | Un ConceptMap sin fila para el valor no da destino; `Patient.gender` tiene binding `required` (`patient.profile.json:595`): un valor fuera del ValueSet es FHIR inválido. |
| `salida.estado` = `error` con un mensaje que el juez acepta y sin ninguno de los casos anteriores | **`rechazo_incorrecto`** (cuenta), hecho = el campo que nombre el texto del error si nombra alguno (misma heurística que `lectura_evidencia._submotivo_pe`, `:72-80`), si no `MSH-9`. | sí | El estándar manda procesar lo que se entiende (§2.6.2); el conversor no procesó. |
| `salida.estado` = `vacio` / `sin_respuesta` | **`indeterminado/sin_salida`**: no se sabe si es del conversor o de la caja (L-CV-8). | no | Como un ACK ausente sin conexión observada. |
| `salida.bundle` ilegible (no JSON, no objeto, sin `resourceType = Bundle` ni recurso suelto) | **`indeterminado/lectura`**, hallazgo clase `lectura`. | no | Como `almacen_oru.parsear` (`:322-332`) y §3.5 de v1.1. |

### 1.4 Categorías, hallazgos y veredicto (R-CV-4)

Leyenda nueva `conversion` en `info_verificador.leyenda` (la de hoy, `info_verificador.json:326-365`, queda intacta para los PE con acuse):

| Categoría | Cuándo | Subtipo |
|---|---|---|
| `correcto` | Bundle devuelto y ningún hallazgo firme que cuente | — |
| `fallo_silencioso` | Bundle devuelto **sin error** y al menos un hallazgo que cuenta de las clases de datos | `convertido` (fidelidad), `aceptado_imposible` (valor imposible convertido), o ambos unidos por `+`, como hoy `_subs` (`verificador.py:529-533`) |
| `rechazo_incorrecto` | `salida.estado = error` donde el juez tenía esperado y ninguna causa de `rechazo_aceptable` (§1.3) | `error` |
| `indeterminado` | Bundle ilegible, sin salida, o emparejamiento imposible (§2.3) | `lectura`, `sin_salida`, `emparejamiento` |
| `fuera_de_alcance` | tipo/evento fuera del PE | — |

Gravedad para el `min` de un lote (un caso = un mensaje, así que solo ordena la ficha): `fallo_silencioso > rechazo_incorrecto >
indeterminado > correcto > fuera_de_alcance`. Q-CV-D-2 pregunta si `fallo_silencioso` conserva el nombre (recomendado) o se llama
`conversion_incorrecta`.

Hallazgos (forma de `verificador._h`, `:91-95`, `origen = "conversion"`): clase `fidelidad` con los subtipos de §4.1; clase
`valor_imposible_aceptado` subtipo `convertido`; clase `rechazo` subtipo `incorrecto` (cuenta) o `aceptable` (no cuenta); clase
`lectura`; clases `nota`/`tolerancia` con subtipos `convencion`, `forma`, `extension`, `fuera_proyeccion`, `version`,
`estructura_declarada`, `evidencia_ignorada`, `mensaje_extra`. Cada hallazgo lleva `hecho` (SEG-n del campo origen), `que` con
`<Recurso>[rol] <ruta>: esperado X, observado Y`, `certeza`, `evidencia = {recurso, ruta, fullUrl, emparejado_por}` y `citas` (§3.7).
`clase_cv` (`nueva` | `ya_declarada` | `convencion`) nace `null`: la pone CV3 (§4.3).

Salida de `verificar` (misma envoltura que hoy, `verificador.py:481-496`, con `conversion` en vez de `lectura`/`esperado`/`observado`):
`{"mensajes", "conversion": {"conversor", "estado", "emparejamiento": <§2.5>, "recuentos": {...}}, "hallazgos", "veredicto",
"hechos_de_tabla", "punto_entrada"}`.

### 1.5 Dónde vive

- `verificador/puntos_entrada.py`: `PUNTOS["adt_conv"] = _pe("adt_conv", 0, PUNTOS["adt_fhir"]["tipos"], …consumidos/p4/p5 de adt_fhir…,
  "ADT de los 8 eventos convertido por un tercero: solo transformación, sin acuse; perfil guía.", mapeador="adt", solo_transformacion=True,
  familia="adt")`; `oru_conv` igual sobre `oru_fhir` (`:112-141`). `puerto 0` (no escucha). `_afirmar` (`:177-195`) ya los cubre.
- `verificador/conversion.py` (nuevo): `leer_bundle`, `emparejar`, `esperado_guia`, `comparar`, `verificar(e, pe)`, las tablas
  `PERFIL_GUIA_ADT` / `PERFIL_GUIA_ORU`, y `autoprueba`. Importa de los mapeadores y de `almacen_oru` sin tocarlos.
- `verificador/verificador.py`: **una línea** al principio de `verificar` (`:260-261`): `if pe.get("solo_transformacion"): return CV.verificar(e, pe)`.
- MCP (`mcp_verificador.py`): `punto_entrada` enum + `adt_conv`/`oru_conv` (`esquema_evidencia.json:342-351`); `E_PROPS["conversion"]`;
  `_no_evaluado` (`:1237-1254`) con la línea «conversión: sin acuse ni canónico, solo se juzga el Bundle devuelto»; `consultar_tabla`
  gana `perfil_guia_adt` y `perfil_guia_oru` (patrón `proyeccion_fhir_adt`, `:1777-1779`) con elemento, campo, regla, nivel y citas;
  `comparar_canonico` responde `sin_mapeador_para_pe` como hoy para estos PE (no hay canónico). `info_verificador` declara S-CV, L-CV, AMB-CV.
- Pruebas: `verificador/prueba_conversion.py` (forma de `prueba_adt.py:25-72`: `mira`, constructores `msg`, un `bundle_de(proy)` que
  sintetiza el Bundle exacto desde la proyección guía, `ev_conv(texto, salida)`).

---

## 2. El lector de la salida (R-CV-5)

### 2.1 Lectura del Bundle

1. `parsear(texto)` textual (`almacen_oru.py:322-332`). Se admite: un `Bundle` de cualquier `type` (`bundle.profile.json:332`: document,
   message, transaction, batch, collection…); un recurso suelto de un tipo proyectado (se envuelve como Bundle de una entry, nota
   `forma/recurso_suelto`); un `Bundle` con `entry[].resource` ausente pero `entry[].request`/`response` → entry ignorada con nota.
2. Por cada entry: `fullUrl` (puede faltar), `resource.resourceType`, `resource.id`, el recurso **normalizado**: sin `id`, `meta`, `text`
   (D-ORU11-1 ampliado con `text`: narrativa generada); `contained[]` se desdobla en recursos virtuales con `fullUrl = "#<id>"`.
3. **Índice de resolución** (R4 «Resolving references in Bundles», `bundle.profile.json:803-806`: el `fullUrl` es la referencia absoluta;
   `urn:uuid:` es válido como fullUrl): una referencia `r` resuelve a la entry cuyo `fullUrl == r`; si no, a la entry cuyo
   `resourceType/id == r` (referencia relativa); si no, a la entry cuyo `fullUrl` termina en `/r`; `#id` resuelve a un `contained` del
   mismo recurso; `Reference.identifier` sin `reference` resuelve a la entry del tipo pedido con ese `identifier.system|value` (referencia
   lógica, como S58/S80 del laboratorio: es **convención** admitida, no cuenta). Lo que no resuelve → `referencia_rota` (§4.1).
4. `otros_tipos`: recuento de recursos fuera de la proyección (MessageHeader, Provenance, Organization, Practitioner, PractitionerRole,
   Location, Specimen, ServiceRequest, Account, Coverage, RelatedPerson…): nota `fuera_proyeccion`, nunca cuenta (L-CV-5). Practitioner
   y Location **sí** se leen cuando una referencia de Encounter los apunta (§2.3).

### 2.2 Qué se empareja con qué

| Papel esperado | Fuente v2 | Clave de emparejamiento (en este orden) | Cita |
|---|---|---|---|
| `Patient[1]` | PID (uno por mensaje en ADT; el primero de PATIENT_RESULT en ORU) | (1) si hay **un solo** Patient en el Bundle, es él; (2) el Patient con algún `identifier.value` igual a alguna PID-3.1 (desescapada), preferida la repetición con CX.5 = MR; (3) el Patient referenciado por el Encounter/Observation emparejados por otra vía; (4) ninguno → `recurso_ausente` PID | `MSG_ADT_A01.csv:15`; `MSG_ORU_R01.csv:14`; `PID_Patient.csv:6` (PID-3 → identifier[2], CX[Identifier]); `CH03.txt:4911-4914` |
| `Encounter[1]` | PV1 | (1) un solo Encounter → él; (2) el Encounter cuyo `subject` resuelve al Patient emparejado **y** con `identifier.value` = PV1-19.1; (3) solo por `subject`; (4) solo por `identifier` = PV1-19.1; (5) ninguno → `recurso_ausente` PV1 (salvo PV1-2 = N: §3.2 fila status) | `MSG_ADT_A01.csv:36` (subject.reference = Patient[1].id); `PV1_Encounter.csv:42` |
| `DiagnosticReport[i]` | OBR i-ésimo (cada ORDER_OBSERVATION) | (1) el DR con `identifier` FILL = OBR-3.1 (o PLAC = OBR-2.1); (2) el DR cuyo `code.coding.code` = OBR-4.1 y que ocupa la i-ésima posición entre los DR no emparejados (orden del Bundle); (3) si hay tantos DR como OBR, por orden; (4) ninguno → `recurso_ausente` OBR | `MSG_ORU_R01.csv:44,53`; `OBR_DiagnosticReport.csv:5-10` |
| `Observation[i.j]` | OBX j del OBR i | (1) las Observation referenciadas por `DR[i].result[]`, en el orden de `result`, casadas con los OBX por `code.coding.code` = OBX-3.1 y, si se repite el código, por OBX-4 (`identifier`/`extension` sub-id) y luego por orden; (2) las Observation no referenciadas por ningún DR, por `code` + orden de aparición; (3) ninguna → `recurso_ausente` OBX | `MSG_ORU_R01.csv:67-69`; `OBX_Observation.csv:6-7` |
| Observation de OBX bajo SPM o PATIENT_OBSERVATION, y de OBX en ADT | OBX fuera de OBR | solo **recuento** (esperado n = número de esos OBX): `recuento` si faltan; contenido no se compara (L-CV-7) | `MSG_ORU_R01.csv:26-27,88-91`; `MSG_ADT_A01.csv:46-47` |
| Practitioner de `participant[k].individual` | PV1-7/8/9/17/52 | por resolución de la referencia; si es lógica (`identifier`) o solo `display`, se lee lo que traiga | `PV1_Encounter.csv:14-25,37-40`; CM datatype-xcn-to-practitioner |
| Location de `location[k].location` y su cadena `partOf` | PV1-3/6/11/42 | por resolución; se recorre `partOf` hasta 6 niveles | `PV1_Encounter.csv:7-9,12-13,27-31`; CM datatype-pl-to-location PL.1-PL.9 |

**Ambigüedad** (dos candidatos igual de buenos en el mismo paso): `indeterminado/emparejamiento` con nota de los candidatos; nunca se
elige al azar. **Sobrantes**: un Patient/Encounter de más → `recurso_duplicado` (ADT: el mensaje trae un PID y un PV1); una
Observation/DR de más sin OBX/OBR de origen → `recurso_inventado`, salvo que corresponda a un origen que la guía sí mapea
(PD1-7 → Observation living will, `MSG_ADT_A01.csv:19`; OBX de ADT, `:46-47`): entonces nota.

### 2.3 Salida del lector (contrato)

```
{"recursos": [{"rol": "Patient#1" | "Encounter#1" | "DiagnosticReport#i" | "Observation#i.j",
               "origen": "PID" | "PV1" | "OBR i" | "OBX i.j",
               "observado": <recurso normalizado> | null, "fullUrl": "...", "emparejado_por": "unico" | "identifier" | "referencia" | "codigo" | "orden",
               "candidatos": n, "referidos": {"subject": "<fullUrl|null>", "individual": [...], "location": [...], "result": [...]}}],
 "sobrantes": [{"resourceType", "fullUrl", "motivo": "duplicado" | "inventado" | "origen_guia"}],
 "otros_tipos": {"MessageHeader": 1, "Provenance": 2, ...},
 "referencias_rotas": [{"desde": "Encounter#1.subject", "texto": "Patient/abc"}],
 "fallos": ["<texto>"]}                                                # ilegible, sin Bundle, contained sin id...
```

### 2.4 Normalización antes de comparar (R-CV-6)

- Hojas por `almacen_oru._hojas` (`:413-433`), observado todo texto (booleanos `true`/`false`, números como su texto JSON).
- `identifier[]`, `name[]`, `address[]`, `telecom[]`, `coding[]`, `interpretation[]`, `result[]`, `participant[]`, `location[]` se comparan
  como **multiconjuntos** por clave (§3) cuando la guía no da semántica al orden; `line[]` y `given[]` **en orden** (la guía numera
  `line[1-3]/line[4]` y `given[1]/given[2]`: CM datatype-xad-to-address XAD.1/XAD.2; CM datatype-xpn-to-humanname XPN.2/XPN.3).
- Referencias: antes de comparar, cada `Reference` se sustituye por `{resuelve_a: <rol o null>, identifier: ..., display: ...}`.
- Fechas: §3.6. Decimales: texto exacto (§3.3, fila `valueQuantity.value`).
- Códigos: `system` + `code` exactos; `display` y `version` son forma (§4.2).

---

## 3. El perfil «guía»

### 3.0 Principio y niveles

Por cada elemento proyectado (`CV-PRE-E1.json`: 21 filas ADT, 30 ORU), la tabla dice el valor que **mandan** los ConceptMap, con un nivel:

- **cuenta**: la guía da una sola representación; una diferencia es hallazgo de §4.1.
- **convencion**: la guía admite más de una (dos filas con condición que se solapan, «Narrative-Condition», un «indirect mapping», o un
  elemento FHIR obligatorio sin fila para el caso); el esperado es un **conjunto** y solo cuenta lo que queda fuera de él.
- **forma**: no es dato (§4.2); nunca cuenta.

Los **vacíos**: un campo v2 vacío no tiene fila en ningún ConceptMap → el elemento se espera **ausente** (R4 JSON omite lo vacío;
D-ORU11-3 `diseno-oru-v11-fable.md:153-156`). Un elemento presente sin campo que lo sostenga es `dato_inventado` si es de valor único,
y nota `extra` si es repetible (Q-CV-D-5). El **nulo explícito `""`** de v2 (`CH02.txt` §2.5.3; `mapeador_adt.py:74,95-103`) se espera
ausente también (en un conversor no hay «borrado»: lo que no hay no se escribe).

**Mayúsculas y minúsculas** de un código (`f` por `F`): las tablas v2 son sensibles a mayúsculas y los ConceptMap solo listan el código
tal cual; un conversor puede mapear `f` o no: **convención** (AMB-CV-1; S4 es del laboratorio).

### 3.1 Patient (PID → `CM segment-pid-to-patient`; `guia_csv/PID_Patient.csv`)

| Elemento | Esperado (perfil guía) | Nivel | Cita |
|---|---|---|---|
| `identifier[]` | Por **cada** repetición de PID-3 con CX.1: un Identifier con `value` = CX.1 desescapado. `type.coding.code` = CX.5 si valorado (`system` del type: `http://terminology.hl7.org/CodeSystem/v2-0203`, identidad de la 0203). CX.4 (HD) → `system` (uri) **o** `assigner` (Organization); se exige que, si CX.4 está valorado, alguno de los dos exista y contenga el namespace o el universal ID; la forma de la uri es convención. CX.7/CX.8 → `period.start/end` (fecha). Identifiers de más (PID-2, PID-4, PID-19, PID-20, o uno que la herramienta añada) → nota `extra`. | value: **cuenta**; type.coding.code: cuenta; type.system: convención; CX.4 presente de alguna forma: cuenta (dato perdido si falta); uri exacta: convención | `PID_Patient.csv:6`; CM datatype-cx-to-identifier CX.1 → value, CX.4 → system «IF CX.4 IN identifier-registry» / → assigner, CX.5 → type.coding.code, CX.7/8 → period; CM table-hl70203-to-v2-0203 (identidad); `CH02A.txt:988-1000,1089-1091,1111-1113`; `patient.profile.json:430` |
| `name[]` | Por cada repetición de PID-5 con FN.1, XPN.2 o XPN.3: un HumanName. `family` = FN.1 (desescapado); si FN trae subcomponentes 2-5, se admite también FN.1-5 unidos por espacio (AMB-CV-2: la guía los manda a extensiones, que son forma; perder las partículas del apellido cambia el nombre). `given[1]` = XPN.2 entero; XPN.3 → `given[2]` entero **o** partido por espacios en `given[2..]` (AMB-CV-3, el propio ConceptMap lo deja abierto); `prefix` = XPN.5; `suffix` ⊇ {XPN.4, XPN.6, XPN.14} en ese orden; `use` por la 0200 (BAD old, D usual, L official, M maiden, MSK anonymous, N nickname, NAV temp, R official, TEMP temp); XPN.7 `unmatched` (A, B, C, F, I, K, NB, NOUSE, P, REL, S, T, U) → `use` **ausente**. `period` por XPN.10/12/13. Se compara como multiconjunto por (`family`, `given[1]`); el orden de `name[]` es forma. | family, given[1], prefix, suffix, use mapeado: **cuenta**; XPN.3 entero o partido: convención; use para unmatched: cuenta (Q-CV-D-8); orden: forma | `PID_Patient.csv:8` (name[1], XPN[HumanName], cardinalidad −1); CM datatype-xpn-to-humanname XPN.1-7, XPN.10-14; CM datatype-fn-to-humanname FN.1 → family, FN.2-5 → extensiones; CM table-hl70200-to-name-use (9 equivalent, 13 unmatched); `CH02A.txt:6150-6175`; `patient.profile.json:515` |
| `birthDate` | PID-7 → `date` con la **precisión del origen**: `YYYY`, `YYYY-MM` o `YYYY-MM-DD` (reformateo ISO 8601 del DTM). Con hora (longitud > 8): `birthDate` = la fecha escrita, sin desplazar por zona (AMB-CV-4: la guía dice re-formatear, no convertir); la extensión `patient-birthTime` es forma. Vacío → ausente. Inválido (`DTM_RE`, `mapeador_referencia.py:291`) → ausente esperado (imposible). | precisión y dígitos: **cuenta**; extensión: forma | `PID_Patient.csv:11-13`; CM segment-pid-to-patient PID-7 → birthDate; CM datatype-dtm-to-datetime DTM.1 → $value; `CH02A.txt:1700-1733`; `patient.profile.json:648` |
| `gender` | PID-8 por la 0001: F female, M male, O other, U unknown, A other, N other. Vacío → **ausente** (ningún ConceptMap tiene fila para vacío; FHIR distingue ausente de `unknown`): un `unknown` inventado cuenta (Q-CV-D-3). Fuera de la 0001 → ausente esperado; `gender` con el literal → `fhir_invalido` (binding required); con un código inventado → `codigo_mal_mapeado`. | **cuenta** | `PID_Patient.csv:14` (CWE[code], AdministrativeSex); CM table-hl70001-to-administrative-gender (6 filas equivalent); `CH03.txt:5032`; `patient.profile.json:595` (binding required administrative-gender) |
| `deceased[x]` | PID-29 valorado → `deceasedDateTime` (§3.6) y **ningún** `deceasedBoolean` (es un choice: uno solo). PID-29 vacío y PID-30 valorado → `deceasedBoolean` por la 0136: Y → `true`, N → `false`. Ambos vacíos → ausente. PID-30 fuera de 0136 → ausente. | **cuenta** | `PID_Patient.csv:50-51` (IF PID-29 NOT VALUED); CM segment-pid-to-patient PID-29/PID-30; CM table-hl70136-to-special-values (Y true, N false); `CH03.txt:5468-5475`; `patient.profile.json:692` (deceased[x] 0..1 boolean|dateTime) |
| `address[]` | Por cada repetición de PID-11: `line` = [SAD.1, SAD.2, SAD.3 de XAD.1 (no vacíos), XAD.2] **en ese orden**; `city` XAD.3; `state` XAD.4; `postalCode` XAD.5; `country` XAD.6; `district` XAD.9; XAD.7 → `use` (BA old, BI billing, C temp, B work, H home, O work) **o** `type` (M postal, SH postal); XAD.7 unmatched para ambos (N, BDL, F, L, P, RH, BR, S, TM, V) → ni use ni type; `period` por XAD.12-14. Multiconjunto por (`line[1]`, `city`, `postalCode`). | line (contenido y orden), city, state, postalCode, country, district, use/type mapeados: **cuenta**; `period`: convención; orden de `address[]`: forma | `PID_Patient.csv:17`; CM datatype-xad-to-address XAD.1 → line[1-3], XAD.2 → line[4], XAD.3-6, XAD.7 (dos condiciones), XAD.9 → district, XAD.12-14 → period; CM table-hl70190-to-address-use / -type; `CH02A.txt:5661`; `patient.profile.json:736` |
| `telecom[]` | Por cada repetición de PID-13 (y de PID-14) con algún valor: ContactPoint. `value`: si XTN.3 ∈ {Internet, X.400} → XTN.4; si no, XTN.12 si valorado; si no, XTN.1 si valorado y XTN.7 no; si XTN.7 valorado → el valor debe **contener** XTN.7 y, si valorados, XTN.6 y XTN.5 (la fórmula exacta de la guía no está en el paquete: L-CV-2). `use`: XTN.2 por la 0201 (PRN home, WPN work, PRS mobile; ORN/VHN/ASN/EMR/NET/BPN unmatched → ausente); XTN.2 vacío → `home` en PID-13 y `work` en PID-14. `system`: XTN.3 por la 0202 (PH phone, FX fax, MD/SAT/TDD/TTY other, BP pager, Internet/X.400 email); CP → `use = mobile` y `system` libre (la 0202 solo le da use: convención); XTN.3 vacío y XTN.4 valorado → `email`; XTN.3 y XTN.4 vacíos → la guía manda `system` con extensión data-absent-reason; un `system` inferido (`phone`) es convención (cpt-2 obliga a algún system). Multiconjunto por `value`. | value, use mapeado/por omisión, system mapeado: **cuenta**; CP system, sin XTN.3 ni XTN.4, formato con XTN.5-8: convención | `PID_Patient.csv:22-25` (telecom[1]/[2] y use por omisión); CM datatype-xtn-to-contactpoint XTN.1/4/7/12 → value con sus condiciones, XTN.2 → use, XTN.3 → system (tres filas); CM table-hl70201-to-contact-point-use; CM table-hl70202-to-contact-point-system (CP → use mobile); `CH02A.txt:6529`; `patient.profile.json:555` |
| `maritalStatus` | PID-16.1 por la 0002: A→L, D→D, M→M, S→S, W→W, C→C, G→T, P→T, R→T, E→L, N→A, I→I, B→U con `system` `http://terminology.hl7.org/CodeSystem/v3-MaritalStatus`; U→UNK, O→OTH, T→NAVU con `system` `…/v3-NullFlavor`. Fuera de la 0002 (user-defined) → convención: cualquier `coding` con ese code literal, o ausente. `display`/`text`: forma. | code y system para los 16 mapeados: **cuenta**; resto: convención | `PID_Patient.csv:27` (CWE[CodeableConcept], MaritalStatus); CM table-hl70002-to-v3-maritalstatus (dos grupos, 16 filas); `CH03.txt:5169-5177`; `patient.profile.json:776` (binding extensible) |

### 3.2 Encounter (PV1 → `CM segment-pv1-to-encounter`; `guia_csv/PV1_Encounter.csv`; MSH → `CM segment-msh-to-encounter` solo en A11)

| Elemento | Esperado (perfil guía) | Nivel | Cita |
|---|---|---|---|
| existencia | PV1 → Encounter[1] en **todos** los eventos del PE, también con PV1-2 = N (la guía no tiene condición; el estándar dice que con N «the PV1 segment itself is not applicable»): Encounter ausente con N es **convención** (AMB-CV-5, Q-CV-D-6); ausente con PV1-2 ≠ N → `recurso_ausente`. | ausente con N: convención; resto: cuenta | `MSG_ADT_A01.csv:36`; `CH03.txt:5753-5756`, `:2512-2513` |
| `identifier[]` | PV1-19.1 → `identifier[].value` (cuenta); `type.coding.code = "VN"`, `type.coding.system = …/v2-0203`, `type.text = "visit number"`: constantes de la guía → convención (un type distinto no cambia el número de visita); CX.4 → system/assigner como en Patient. PV1-50 → identifier[2]: nota si aparece. | value: **cuenta**; type: convención | `PV1_Encounter.csv:42-45`; CM segment-pv1-to-encounter PV1-19 (4 filas); CM datatype-cx-to-identifier; `CH03.txt:6175-6205`; `encounter.profile.json:420` |
| `status` | **Conjunto admitido** por evento: (a) PV1-45 valorado → `finished`; (b) si no, PV1-2 por la 0004→encounter-status (E/I/O/R/B/C/N in-progress, P planned, U unknown); (c) la 0003 por el evento (A01/A02/A13 in-progress, A03 finished, A04/A05 planned, A08 unknown, A11 cancelled), que la guía solo invoca desde el mapa de A11 pero publica para todos. Admitidos = {(a) o (b)} ∪ {(c)} para el evento; **A11**: `cancelled` es lo literal del mapa de mensaje; `finished` (PV1-45) se admite (AMB-CV-6). PV1-2 vacío o fuera de 0004 y sin PV1-45: cualquier status (FHIR lo exige 1..1 y la guía no da fila): convención. | fuera del conjunto: **cuenta**; dentro: nada | `PV1_Encounter.csv:6` (IF PV1-45 NOT VALUED), `:73` (status = finished IF PV1-45 VALUED); CM table-hl70004-to-encounter-status; CM table-hl70003-to-encounter-status; CM message-adt-a11-to-bundle ADT_A11.MSH → Encounter[1]; CM segment-msh-to-encounter MSH-9 → status; `encounter.profile.json:462` (required encounter-status) |
| `class` | PV1-2 por la 0004→v3-ActCode: E → EMER, I → IMP, O → AMB, P → PRENC con `system` `…/v3-ActCode`; R, B, C, N, U → el mismo código con `system` `…/v2-0004`. `{v2-0004, "I"}` donde el mapa dice IMP → `codigo_mal_mapeado`. Fuera de la 0004 o vacío: cualquier Coding o ausente (FHIR 1..1, sin fila): convención. `display`: forma. | code y system de los 9: **cuenta** | `PV1_Encounter.csv:5` (CWE[Coding], PatientClass[EncounterClass]); CM table-hl70004-to-v3-actcode (dos grupos); `CH03.txt:5730-5746`; `encounter.profile.json:731` (Coding 1..1, extensible v3-ActEncounterCode) |
| `type[]` | PV1-4 → un CodeableConcept con `coding {system …/v2-0007, code}` para A, E, L, R, N, U, C (identidad). Otro código (user-defined) → convención. | code+system de los 7: **cuenta** | `PV1_Encounter.csv:10`; CM table-hl70007-to-v2-0007; `CH03.txt:5781-5795`; `encounter.profile.json:993` |
| `serviceType` | PV1-10: MED → `{…/service-type, 382}`, URO → `{…/service-type, 222}`; SUR, PUL, CAR → `{…/v2-0069, <mismo>}`; otros → convención. | code+system de los 5: **cuenta** | `PV1_Encounter.csv:26`; CM table-hl70069-to-service-type (dos grupos); `CH03.txt:5997-6003`; `encounter.profile.json:1045` |
| `subject` | Resuelve al `Patient#1` emparejado (referencia por fullUrl, relativa o lógica por identifier: convención la forma). Ausente o a otro Patient → `referencia_rota` / `valor_distinto`. | **cuenta** | `MSG_ADT_A01.csv:36`; `encounter.profile.json:1139` |
| `participant[]` | Por cada repetición con XCN.1 o XCN.2 de PV1-7 (`type.coding.code` ATND), PV1-8 (REF), PV1-9 (CON), PV1-17 (ADM), PV1-52 (PART), `type.coding.system` `…/v3-ParticipationType`; `individual` resuelve a un Practitioner (recurso, contained o lógico) con `identifier[].value` ∋ XCN.1 (si valorado) y `name.family` = XCN.2 (FN.1), `name.given[1]` = XCN.3, `given[2..]` = XCN.4 (entero o partido: AMB-CV-3), `suffix` ⊇ {XCN.5, XCN.21}, `prefix` = XCN.6; `type.coding.display`/`type.text` («attender», «referrer»…): forma. Un `individual` que es solo `display` con el nombre y sin XCN.1 valorado: convención si XCN.1 vacío; `dato_perdido` si XCN.1 valorado. Multiconjunto por (`type.code`, XCN.1 o family). | type.code, XCN.1, family, given[1]: **cuenta**; display/text: forma | `PV1_Encounter.csv:14-25,37-40,80-83`; CM segment-pv1-to-encounter PV1-7/8/9/17/52; CM datatype-xcn-to-practitioner XCN.1-7, XCN.21; `CH02A.txt:5808`; `encounter.profile.json:1418,1500` |
| `period` | PV1-44 → `start`, PV1-45 → `end` (§3.6). | **cuenta** | `PV1_Encounter.csv:71-72`; `CH03.txt:6473-6480`; `encounter.profile.json:1584` |
| `location[]` | PV1-3 → `location[k].location` con `status` `active` (PV1-2.1 ≠ P) / `planned` (= P); PV1-6 → `status completed`; PV1-11 → `status active` (su extensión «temporary» es forma); PV1-42 → `reserved`. Cada `location.location` resuelve a una Location (recurso, contained o lógica); recorriendo `partOf` desde ella, el conjunto de `identifier[].value` ∪ `name` de la cadena debe **contener** cada componente valorado de PL.1, PL.2, PL.3, PL.4.1, PL.7, PL.8 (la guía los reparte en hasta 6 Location encadenadas; un solo Location con todos los valores en identifier/name es convención); PL.9 → `description` de la más granular (o `display` de la referencia: convención). Un Location que no conserva algún componente → `dato_perdido` con hecho PV1-3/6/11. | status por campo, componentes PL presentes, PL.9 presente: **cuenta**; reparto en recursos, uri/system de los identifier: convención | `PV1_Encounter.csv:7-9,12-13,27-31,68-69`; CM segment-pv1-to-encounter PV1-3/6/11/42; CM datatype-pl-to-location PL.1 → [4].identifier, PL.2 → [2], PL.3 → [1], PL.4 → [6], PL.7 → [5], PL.8 → [3], PL.9 → [1].location(Location.description), partOf; `CH02A.txt:3377-3515`; `encounter.profile.json:2716,2759` (location.status required) |
| `hospitalization.admitSource` | PV1-14.1 → `coding.code` literal (la 0023 no tiene valores sugeridos, sin vocabulario); `system`: convención. | code: **cuenta**; system: convención | `PV1_Encounter.csv:34`; CM segment-pv1-to-encounter PV1-14; `CH03.txt:6052-6062`; `encounter.profile.json:2277` |
| `hospitalization.dischargeDisposition` | PV1-36.1 → `coding.code` literal (la guía nombra el vocabulario DischargeDisposition pero el paquete no trae ConceptMap para la 0112); `system`: convención. | code: **cuenta**; system: convención | `PV1_Encounter.csv:62`; `CH03.txt:6340-6347`; `encounter.profile.json:2530` |

### 3.3 Observation (OBX → `CM segment-obx-to-observation`; `guia_csv/OBX_Observation.csv`)

Las 24 filas que ya citan `[M]` (`CV-PRE-E1.json`) se mantienen con el valor del ConceptMap; las **6 filas de convención** del laboratorio
se apartan así: `Observation.identifier[]` (D-ORU-1, `diseno-oru-fable.md:65`) → no se espera ningún identifier propio; `OBX-21` → `identifier`
FILL si valorado; lo demás nota. `Observation.subject.identifier` (S58/S60) → la forma lógica es convención; **lo que cuenta es que
`subject` resuelva al Patient#1** (`MSG_ORU_R01.csv:67-69`); sin PID → ausente. `cualquier otro elemento` (L-ORU-10/S69) → nota
`fuera_proyeccion`. Lo mismo para `DiagnosticReport.identifier[] propio`, `.subject.identifier` y `otros`.

| Elemento | Esperado (perfil guía) | Nivel | Cita |
|---|---|---|---|
| `status` | OBX-11 por la 0085: A amended, C corrected, D entered-in-error, F final, P preliminary, W entered-in-error, X cancelled. Unmatched (B, I, N, O, R, S, U, V) → cualquier código de observation-status (FHIR 1..1): convención. X → además `status.extension` alternate-codes: forma. N → `dataAbsentReason` not-asked: nota (L-CV-6). | los 7 mapeados: **cuenta**; resto: convención | `OBX_Observation.csv:43-48`; CM table-hl70085-to-observation-status (7 equivalent, 8 unmatched); `CH07.txt:3229-3284`; `observation.profile.json:596` (required) |
| `code` | OBX-3: CE/CWE.1 → `coding[1].code`; CE.3 → `coding[1].system` **indirecto** («the vocabulary table will give the actual uri»): para LN, SCT/SNM/SNM3 y UCUM/ISO+ se exige la uri canónica de FHIR R4 (`http://loinc.org`, `http://snomed.info/sct`, `http://unitsofmeasure.org`; L-CV-3); para cualquier otro nombre, convención (cualquier uri o el nombre; ausente → `dato_perdido`); CE.4-6 → `coding[2]`; CWE.9 → `text`; CE.2/CE.5 → `display`: forma. Orden de `coding[]`: forma (multiconjunto por `code`). `^texto` sin código → `coding.display` o `text`: convención (AMB-ORU-4 es lectura, no decisión del sitio). | code de coding[1] y [2], system de los nombres conocidos, text: **cuenta**; system de otros nombres: convención; display: forma | `OBX_Observation.csv:6`; CM datatype-ce-to-codeableconcept CE.1-6; CM datatype-cwe-to-codeableconcept CWE.1-13; `CH07.txt:2654`; `observation.profile.json:703` |
| `subject` | resuelve a Patient#1; sin PID → ausente. | **cuenta** | `MSG_ORU_R01.csv:67-69`; `observation.profile.json:765` |
| `effective[x]` | OBX-14 → `effectiveDateTime` (§3.6). OBX-14 vacío → ausente **o** la fecha de OBR-7 (AMB-CV-7: ch07 solo exige OBX-14 cuando difiere del OBR, `CH07.txt:3312`; S63 es la misma lectura). | OBX-14 valorado: **cuenta**; vacío: convención | `OBX_Observation.csv:51`; CM segment-obx-to-observation OBX-14; `observation.profile.json:911` |
| `value[x]` (cuál) | Por OBX-2: NM → `valueQuantity`; ST/FT/TX → `valueString`; CE/CWE/CNE/IS/CF → `valueCodeableConcept`; DTM/DT → `valueDateTime`; TM → `valueTime`; NR → `valueRange`; DR → `valuePeriod`; NA → `valueSampledData`; SN: `<>` → valueString, sep `:`/`/` → `valueRatio`, `-` → `valueRange`, `+` → valueString, sin separador → `valueQuantity`; ED/RP → extensión (forma); TS → `valueDateTime` o ausente (la guía no lista TS: AMB-ORU-1 → convención); otro tipo de la 0125 (AD, CX, XPN…) → convención; OBX-2 vacío → convención. **Elegir otra clave** (NM como valueString) cuenta. OBX-5 repetido (no TX/FT) → convención entre componentes, varias Observation o concatenación (lo dice la propia hoja del mensaje); se exige que la primera repetición esté. | clave por tipo: **cuenta**; repeticiones: convención | `OBX_Observation.csv:8-26` (todas las ramas); CM segment-obx-to-observation OBX-5 (21 filas); `MSG_ORU_R01.csv:69-73` (comentario sobre OBX-5 repetido); `CH07.txt:2573-2603,2787`; `observation.profile.json:1053` |
| `valueQuantity.value` | NM.1 / SN.2 → `value` como **texto decimal exacto** (`1.20` ≠ `1.2`: la precisión del decimal FHIR es significativa, R4 datatypes §decimal, fuera de la carpeta: L-CV-3); forma canónica del NM admitida: sin `+`, sin ceros iniciales superfluos (AMB-ORU-3 es lectura del estándar). | **cuenta** (Q-CV-D-10) | CM datatype-nm-to-quantity NM.1 → $value; CM datatype-sn-to-quantity SN.2 → value; `CH02A.txt:4842` (SN) |
| `valueQuantity.comparator` | SN.1 → `comparator` cuando SN.1 ∈ {<, <=, >=, >}; `=` → ausente (no está en el ValueSet quantity-comparator); `<>` ya fue valueString. | **cuenta** | CM datatype-sn-to-quantity SN.1 → comparator; CM datatype-sn-to-ratio SN.1 (IF NOT «=») |
| `valueQuantity.unit/.code/.system` | OBX-6: CWE.2 → `unit` (si vacío, CWE.1 → `unit`); CWE.1 → `code` y CWE.3 → `system` **solo si ambos valorados**; UCUM/ISO+ → `http://unitsofmeasure.org`; otro nombre → convención. OBX-6 vacío → sin unit/code/system. Aplica a Quantity, a `valueRange.low/high` y a `valueRatio.numerator/denominator`. | unit, code, system UCUM: **cuenta** | `OBX_Observation.csv:32-37`; CM datatype-cwe-to-quantity CWE.1/.2/.3 con sus condiciones; `CH07.txt:2909` |
| `valueString` | ST/TX/FT: texto desescapado (§2.7); TX/FT con repeticiones = párrafos: unidos por salto de línea o por otro separador de párrafo: convención (D-ORU-3 es una elección); un escape sin resolver (`\T\` literal) o un párrafo perdido → cuenta. SN `<>`/`+`: el texto SN completo (fórmula de la hoja) o cualquier concatenación que conserve los cuatro componentes: convención. | contenido: **cuenta**; separador de párrafos: convención | `OBX_Observation.csv:9,20,23,25`; `CH02.txt` §2.7 |
| `valueCodeableConcept` | como `code` (CE/CWE); IS → `coding.code` sin system. | **cuenta** | `OBX_Observation.csv:10-14`; CM datatype-is-to-codeableconcept IS.1 → coding.code |
| `valueDateTime` / `valueTime` | §3.6; TM → `time` FHIR (HH:MM:SS). | **cuenta** | `OBX_Observation.csv:16,19`; CM datatype-dtm-to-datetime; CM datatype-ts-to-datetime TS.1 |
| `valueRange` / `valueRatio` | SN.2 → `low.value` / `numerator.value`; SN.4 → `high.value` / `denominator.value`; NR → `low`/`high`; unidades como arriba. | **cuenta** | CM datatype-sn-to-range; CM datatype-sn-to-ratio; CM datatype-nr-to-range |
| `interpretation[]` | Por cada repetición de OBX-8: `coding {system …/v3-ObservationInterpretation, code}` (identidad para los 39 códigos del mapa); `system` v2-0078 → `codigo_mal_mapeado`; código fuera del mapa (AC, HM, OBX, QCF, TOX, o local) → convención. Multiconjunto. | code y system: **cuenta** | `OBX_Observation.csv:39`; CM table-hl70078-to-v3-observationinterpretation (grupo source y target v3-ObservationInterpretation); `CH07.txt:3161-3170`; `observation.profile.json:1174` (extensible) |
| `referenceRange[]` | OBX-7 → `referenceRange[1].text` igual **o** parseado a `low`/`high` (la guía lo admite «if sufficiently parseable»): convención entre las dos; ninguna → `dato_perdido`. | presencia: **cuenta**; forma: convención | `OBX_Observation.csv:38`; CM segment-obx-to-observation OBX-7; `CH07.txt:3142`; `observation.profile.json:1806` |
| `id`, `meta`, `text`, extensiones, `category`, `performer`, `method`, `device`, `specimen`, `note`, `component` sin OBX-5 repetido | forma / fuera de proyección | nunca | L-CV-4, L-CV-5 |

### 3.4 DiagnosticReport (OBR → `CM segment-obr-to-diagnosticreport`; `guia_csv/OBR_DiagnosticReport.csv`)

| Elemento | Esperado (perfil guía) | Nivel | Cita |
|---|---|---|---|
| existencia | Uno por ORDER_OBSERVATION (ORC lo crea, OBR lo completa; sin ORC lo crea el OBR). | **cuenta** | `MSG_ORU_R01.csv:44,53` |
| `identifier[]` | OBR-2.1 → Identifier con `type.coding.code = PLAC` (system …/v2-0203); OBR-3.1 → FILL; la condición «If ORC-2 … is not valued OR there is ORC segment» es ambigua (AMB-CV-8): se exige que el valor esté **con el type correcto**, venga de OBR o de ORC; PLAC/FILL intercambiados → `codigo_mal_mapeado`. Identifiers propios del conversor → nota. | value con su type: **cuenta** | `OBR_DiagnosticReport.csv:5-10`; CM segment-obr-to-diagnosticreport OBR-2/OBR-3 (6 filas); CM datatype-ei-extension-to-identifier EI.1 → value; `CH07.txt:1721,1754`; `diagnosticreport.profile.json:431` |
| `status` | OBR-25 por la 0123: O/I/S registered, P preliminary, C corrected, R partial, F final, X cancelled. Unmatched (A, Y, Z, M, N) → convención. Vacío: la hoja lo llama «error on the v2 side»; FHIR exige 1..1 → cualquier status o `error` del conversor: convención. | los 8: **cuenta** | `OBR_DiagnosticReport.csv:33-34`; CM table-hl70123-queries-to-diagnostic-report-status; `CH07.txt:2117-2129`; `diagnosticreport.profile.json:524` |
| `code` | OBR-4 como Observation.code. | **cuenta** | `OBR_DiagnosticReport.csv:11`; `CH07.txt:1804` |
| `subject` | resuelve a Patient#1. | **cuenta** | `diagnosticreport.profile.json:681` |
| `effective[x]` | OBR-8 vacío → `effectiveDateTime` = OBR-7; OBR-8 valorado → `effectivePeriod{start = OBR-7, end = OBR-8}`; nunca ambos. | **cuenta** | `OBR_DiagnosticReport.csv:14-16`; CM segment-obr-to-diagnosticreport OBR-7 (dos condiciones), OBR-8; `CH07.txt:1825,1842` |
| `issued` | OBR-22 → `instant` (segundos y zona obligatorios): con DTM de precisión ≥ segundos, el instante (§3.6); con menos precisión, ausente **o** completado con `:00` y una zona (convención, AMB-CV-9); dígitos del origen cambiados → cuenta. | **cuenta** / convención | `OBR_DiagnosticReport.csv:30`; `CH07.txt:2090`; `diagnosticreport.profile.json:829` |
| `result[]` | El conjunto de referencias resueltas = exactamente las Observation de los OBX de **su** OBR (multiconjunto; el orden es forma: Q-CV-D-4); una referencia a la Observation de otro OBR o a nada → cuenta; un OBX sin Observation → `recurso_ausente`. | pertenencia: **cuenta** | `MSG_ORU_R01.csv:67-73`; `diagnosticreport.profile.json:1014` |
| `category` (OBR-24), `performer`, `resultsInterpreter`, `specimen`, `basedOn` | fuera de proyección | nunca | L-CV-5 |

### 3.5 Vocabularios: resumen de los mapas que el perfil usa (todos del paquete 1.0.0)

| Tabla | ConceptMap | Filas con destino | Sin destino (convención) | Dónde se usa |
|---|---|---|---|---|
| 0001 | table-hl70001-to-administrative-gender | F, M, O, U, A, N (6) | — (fuera de tabla: imposible) | Patient.gender |
| 0002 | table-hl70002-to-v3-maritalstatus | 13 → v3-MaritalStatus; U, O, T → v3-NullFlavor | user-defined | Patient.maritalStatus |
| 0003 | table-hl70003-to-encounter-status | A01, A02, A03, A04, A05, A08, A11, A13 | resto | Encounter.status (conjunto) |
| 0004 | table-hl70004-to-encounter-status; table-hl70004-to-v3-actcode | 9 / 4 + 5 | user-defined | Encounter.status, Encounter.class |
| 0007 | table-hl70007-to-v2-0007 | A, E, L, R, N, U, C (identidad) | user-defined | Encounter.type |
| 0069 | table-hl70069-to-service-type | MED → 382, URO → 222; SUR, PUL, CAR identidad | user-defined | Encounter.serviceType |
| 0112 | (sin ConceptMap en el paquete) | — | todo: código literal | Encounter.hospitalization.dischargeDisposition |
| 0136 | table-hl70136-to-special-values | Y → true, N → false | — | Patient.deceasedBoolean |
| 0190 | table-hl70190-to-address-use / -type | 6 / 2 | 12 / 16 unmatched | Patient.address.use/type |
| 0200 | table-hl70200-to-name-use | 9 | 13 unmatched | Patient.name.use |
| 0201, 0202 | table-hl70201-to-contact-point-use; table-hl70202-to-contact-point-system | 3 / 9 (+ CP → use) | 6 unmatched / — | Patient.telecom |
| 0203 | table-hl70203-to-v2-0203 | identidad | — | Identifier.type |
| 0078 | table-hl70078-to-v3-observationinterpretation | 39 identidad | 5 unmatched | Observation.interpretation |
| 0085 | table-hl70085-to-observation-status | A, C, D, F, P, X, W | B, I, N, O, R, S, U, V | Observation.status |
| 0123 | table-hl70123-queries-to-diagnostic-report-status | O, I, S, P, C, R, F, X | A, Y, Z, M, N | DiagnosticReport.status |

### 3.6 Fechas y horas (R-CV-7)

- DTM (`CH02A.txt:1700-1733`) → FHIR `date`/`dateTime`/`instant` con la **precisión del origen**: `YYYY`, `YYYY-MM`, `YYYY-MM-DD`,
  y con hora `YYYY-MM-DDThh:mm:ss[.ffff]±hh:mm` (FHIR exige minutos, segundos y zona cuando hay hora). Añadir dígitos que el origen no
  traía (día a un `YYYYMM`, segundos a un `HHMM`) es `dato_inventado`; quitar precisión que traía (segundos, fracción) es `dato_perdido`.
  Excepciones admitidas (convención): completar `HH` o `HHMM` con `:00` cuando FHIR obliga a segundos (`dateTime` con hora), e `issued`
  (§3.4).
- **Zona**: si el DTM traía `±ZZZZ`, el observado se compara como **instante** (misma hora en otra zona = igual; distinta = `valor_distinto`).
  Si no traía zona, «defaults to that of the local time zone of the sender» (`CH02A.txt:1733`): cualquier zona es convención siempre que la
  **hora local escrita** se conserve; un `dateTime` con hora y sin zona es `fhir_invalido`; reducir a fecha para evitar la zona es
  `dato_perdido` (la hora estaba).
- `birthDate`: solo fecha, sin desplazar (AMB-CV-4). TS.2 (grado de precisión) se ignora: componente B desde la 2.3 y el ConceptMap
  ts-to-datetime solo usa TS.1 (es lo que dice el paquete, no una S-n).

### 3.7 Cómo se cita cada hallazgo (R-CV-8)

Cada hallazgo que cuenta lleva `citas` con, como mínimo, **una de la guía y una del estándar o de FHIR**, en este orden:

1. `[CM <nombre> <origen> → <destino>]` el ConceptMap y el elemento (p. ej. `[CM table-hl70004-to-v3-actcode I → IMP]`), o `[CM segment-… <campo> → <atributo> IF …]` con su condición;
2. `[G <hoja>.csv:fila]` la fila de la hoja CSV del commit `873b331`;
3. `[E… fichero:línea]` el texto de v2.5 (capítulos 2, 2A, 3 y 7) (definición del campo, tabla o tipo de dato);
4. `[F <recurso>.<elemento> fichero:línea]` la StructureDefinition R4 (cardinalidad, binding, tipo) cuando la diferencia es de validez FHIR;
5. `[AMB-CV-n]` / `[L18]` / `[Q-CV-D-n]` cuando la certeza no es literal.

Las S-n aparecen solo en notas `convencion` («el laboratorio escribe X [S58]; la guía admite X e Y»). La tabla `consultar_tabla("perfil_guia_adt")`
devuelve las mismas citas por fila, para que CV3 las copie sin reescribirlas. `citas_conversion(h)` en el MCP reutiliza `_citas` y `CITAS`
(`mcp_verificador.py:601,802`) añadiendo las claves `[CM …]` y `[G …]` nuevas.

---

## 4. Cuándo una diferencia «cambia el significado del dato» (S-CV-5)

### 4.1 Definición operativa: las ocho clases que cuentan

Todas sobre la proyección «guía» de §3 (nivel `cuenta`) y el recurso emparejado por §2. `hecho` = el campo v2 de origen.

| Subtipo (clase `fidelidad` salvo el 5) | Definición | Ejemplo |
|---|---|---|
| 1 `valor_distinto` | La hoja existe en esperado y observado y los textos difieren tras las normalizaciones de §2.4 y §3.6 | `birthDate` 1980-02 esperado, 1980-02-01 observado (también 3); `period.start` con la hora local cambiada |
| 2 `dato_perdido` | El campo v2 está valorado, la guía lo lleva a un elemento proyectado (no a una extensión) y ninguna hoja del recurso emparejado ni de sus referidos lo contiene | PID-3 con dos repeticiones y un solo identifier; PL.3 (cama) sin rastro en la cadena de Location; OBR-8 valorado sin `effectivePeriod.end` |
| 3 `dato_inventado` | Un elemento proyectado de valor único está presente sin campo v2 que lo sostenga, o con más precisión que el origen | `gender: unknown` con PID-8 vacío; `deceasedBoolean: false` sin PID-30; `period.end` sin PV1-45 |
| 4 `codigo_mal_mapeado` | El código origen está en el `source` de un ConceptMap con destino y el `code`/`system` observados no son su `target` (incluidas las identidades con `system` fijado) | PV1-2 I → `{v2-0004, I}` en vez de `{v3-ActCode, IMP}`; PV1-10 MED → `{v2-0069, MED}`; OBX-8 H con system v2-0078; XPN.7 B → `use official` (unmatched: Q-CV-D-8) |
| 5 `valor_imposible_convertido` (clase `valor_imposible_aceptado`) | El valor origen es imposible según v2.5 (fuera de una tabla HL7 con binding `required` en el destino, DTM/NM inválidos, carácter de control) y el conversor lo escribió, tal cual o con un mapeo inventado, en vez de omitirlo o devolver error | PID-8 X → `gender: "X"` o `gender: other`; PID-7 20261301 → `birthDate` cualquiera |
| 6 `recurso_ausente` / `recurso_duplicado` / `recurso_inventado` | Falta el recurso de un papel esperado; hay más de uno para el mismo papel; hay un Patient/Encounter/Observation/DiagnosticReport sin origen en el mensaje (§2.2) | 0 Patient; 2 Encounter para un PV1; una Observation que no sale de ningún OBX |
| 7 `referencia_rota` | `subject`, `individual`, `location`, `result` no resuelve dentro del Bundle (§2.1 paso 3) o resuelve a un recurso de otro papel | `Encounter.subject = Patient/123` sin entry con ese id; `result` apuntando a la Observation de otro OBR |
| 8 `fhir_invalido` | El observado viola el tipo o el binding `required` del elemento proyectado | `gender` fuera de administrative-gender; `birthDate` con hora; `dateTime` con hora sin zona; `comparator = "="`; `status` fuera de su ValueSet; `deceasedBoolean` y `deceasedDateTime` a la vez |

Regla de **un hallazgo por campo**: `fusionar` por `(mensaje, hecho)` (`verificador.py:499-526`); un campo con varias hojas discrepantes da un
hallazgo con todas en `que`. Regla de **no doble conteo**: un `recurso_ausente` absorbe todos los `dato_perdido` de ese recurso; una
`referencia_rota` absorbe el `dato_perdido` del elemento referido.

### 4.2 Lo que es forma y no cuenta (nota `forma`, `convencion`, `extension` o `fuera_proyeccion`)

Orden de entries y de listas sin semántica (`identifier[]`, `name[]`, `address[]`, `telecom[]`, `coding[]`, `interpretation[]`, `result[]`,
`participant[]`, `location[]`); `id`, `fullUrl`, `urn:uuid`, `meta`, `text` (narrativa), `Bundle.type`, `Bundle.timestamp`, `identifier` del
Bundle, `entry.request`; extensiones (aunque lleven dato: L-CV-4); `display` de cualquier Coding y `text` de un `type`; forma de una
referencia (recurso, `contained`, lógica por identifier, `display` acompañante) mientras el dato referido se conserve; la uri de un
`system` para tablas user-defined o nombres de sistema no canónicos; recursos fuera de la proyección (MessageHeader, Provenance, Organization,
PractitionerRole, Specimen, ServiceRequest, Account, Coverage, RelatedPerson, Device); elementos del recurso fuera de la proyección
(`category`, `performer`, `note`, `method`, `language`…); mayúsculas de un código origen (AMB-CV-1); el separador de párrafos de TX/FT;
la zona elegida para un DTM sin zona; la representación textual de un decimal **equivalente en precisión** (`1.20` = `1.20`, nunca `1.2`).

### 4.3 Cómo se clasifica cada discrepancia: nueva, ya declarada o convención (R-CV-9)

El juez pone `clase_cv = null` en todo hallazgo que cuenta y `convencion` en las notas que nacen de un nivel `convencion`. **CV3** rellena
`clase_cv` por **mecanismo** (mismo `hecho`, mismo subtipo, misma firma de valores), no caso a caso, con esta regla escrita antes:

1. `ya_declarada` si el proyecto la muestra como comportamiento querido: la misma diferencia aparece en una **salida esperada** publicada de
   sus pruebas, en una prueba que la afirma, en su documentación o en un issue abierto o cerrado que la describe (E-CV-4,
   `RESULTADO-CV-PRE.md:75-84`). Se guarda la referencia exacta (fichero y línea del proyecto, o número de issue).
2. `convencion` si, releídos el ConceptMap y la hoja CSV que cita el hallazgo, la guía **sí** admite la representación observada (una
   condición mal leída, una segunda fila, un «Narrative-Condition»). Entonces el perfil estaba mal: se corrige como **DV-CV-n** con la cita,
   se vuelve a juzgar el corpus entero con el juez corregido (huella nueva) y el cambio se cuenta en el RESULTADO. Nunca se baja a
   convención por lo que diga el conversor ni por frecuencia.
3. `nueva` en cualquier otro caso. Confirmada (regla de portfolio) cuando además se reproduce con un mensaje público del corpus (todos lo
   son) y la cita de §3.7 está completa.

Tope de iteraciones de la regla 2: **dos** rejuicios en CV3; lo que siga dudoso pasa a `Q-CV-D` y no se cuenta como nueva.

---

## 5. La versión

### 5.1 Regla (S-CV-6, R-CV-10)

- La versión del mensaje es **MSH-12.1 escrita** (`CH02.txt:4500-4513`); sin ella, 2.5 con nota. El PE no la acepta ni la rechaza: no acusa.
- El juez solo tiene texto de v2.5 (caps. 2, 2A, 3, 7). Con MSH-12 = 2.5 todo cuenta como en §3-§4.
- Con MSH-12 ≠ 2.5 (las muestras: 2.3 ×4, 2.4 ×1, 2.5.1 ×3, 2.6 ×3, 2.8 ×52; `RESULTADO-CV-PRE.md:53`):
  - **cuentan** los hallazgos que dependen solo de un ConceptMap (los `group.source` son los sistemas v2 sin versión: `CM table-hl70004-to-v3-actcode`
    source `http://terminology.hl7.org/CodeSystem/v2-0004`), de la estructura de un tipo de dato en su parte estable (CX.1, XPN.1-7, XAD.1-7,
    XTN.1-4/12, PL.1-4/9, CE/CWE.1-6, SN.1-4, DTM) o de FHIR R4;
  - **no cuentan** (certeza `ambiguedad L18`, nota `version`): que un código esté o no en una tabla de v2.5 (`valor_imposible_convertido` de tabla),
    que la estructura de la 0354 sea la de v2.5 (§5.2), las longitudes, y cualquier componente de tipo de dato añadido después de 2.5 que el
    juez no conozca.
- Un conversor que devuelve `error` por la versión (equivalente a un 203) → `rechazo_aceptable` (nota): el receptor decide qué versiones
  acepta (`CH02.txt:1442`). Si lo hace con todo el corpus 2.5, la etapa **para** para ese conversor (regla de parada de CV1, §8).

### 5.2 MSH-9.3 y la tabla 0354 (`ADT^A04^ADT_A04` en las muestras 2.8)

- En v2.5, A04 usa ADT_A01 (`CH02.txt:6060-6061,6067`); el juez con acuse lo marca AR 200 (`acuse_referencia.py:498-499`, A-6). En este
  punto de entrada **no hay acuse**: el mensaje se lee con la estructura del evento y la diferencia es nota `estructura_declarada`.
- Si en v2.8 la 0354 asigna ADT_A04 a A04, la muestra es correcta en su versión; si no, es un defecto de la muestra, **no de la conversión**
  (`RESULTADO-CV-PRE.md:61-62`). Ninguna de las dos lecturas cambia lo que se juzga del Bundle. **No se decide** con lo que hay en la carpeta:
  Q-CV-A-1 pide leer la 0354 de v2.8 antes de escribir una palabra sobre MSH-9.3 en el RESULTADO; hasta entonces, nota con certeza `L18`.
- Para el corpus del laboratorio (2.5, MSH-9.3 coherente con la 0354) no hay caso.

### 5.3 Plantillas «basadas en v2.8» frente a corpus 2.5

Los conversores declaran plantillas para 2.8 (`ANTES:24-25`). Un mensaje 2.5 es un subconjunto por campos de uno 2.8 (los campos se añaden al
final, nunca se renumeran): las plantillas pueden leer PID-3, PV1-2, OBX-5… igual. Lo que puede diferir y el perfil ya contempla: tipos de
dato ampliados (CWE donde 2.5 tiene CE/IS: el perfil acepta CE.1-6 y CWE.1-13), OBX-2 con valores posteriores (convención), tablas con códigos
nuevos (solo cuentan los que la 2.5 ya tenía). **No se espera ninguna diferencia atribuible a la versión de las plantillas** sobre el corpus
2.5; si aparece, se adjudica en CV2 como «fuera de previsto» y se documenta (§8).

---

## 6. Pruebas en rojo antes del código (P-CV-n)

Todas en `verificador/prueba_conversion.py`, con evidencia sintética: `bundle_de(proy_guia, forma)` construye un Bundle exacto desde la
proyección guía (con `fullUrl` `urn:uuid:` deterministas y `subject`/`result` por fullUrl), y cada prueba muta **una** cosa. «Hoy» = sin el
módulo: el PE no existe (`PE.resolver` lanza `ValueError`, `puntos_entrada.py:151-153`), así que todas fallan por construcción; el control
negativo es lo que debe seguir dando `correcto` o `0 hallazgos que cuentan`.

| P | Pieza | Caso | Esperado | Control negativo |
|---|---|---|---|---|
| P-CV-1 | PE y evidencia | `adt_conv`, A01 nominal, `salida.estado = bundle` exacto | `correcto`, `cuenta = []`, `conversion.recuentos = {Patient: 1, Encounter: 1}` | mismo Bundle con `gender` cambiado → `fallo_silencioso/convertido`, `[("fidelidad","valor_distinto","PID-8")]` |
| P-CV-2 | PE, §1.3 | `salida.estado = error` con A01 válido | `rechazo_incorrecto`, hallazgo `rechazo/incorrecto` hecho `MSH-9` | `error` con A05 → `fuera_de_alcance`, 0 cuentan; `error` con PID-7 inválido → `correcto` + nota `rechazo/aceptable` |
| P-CV-3 | PE, §1.3 | `salida.bundle = "no json"`; `salida.estado = vacio` | `indeterminado/lectura`; `indeterminado/sin_salida` | Bundle válido → no `lectura` |
| P-CV-4 | lector §2.1-2.2 | Bundle con Patient, Encounter, MessageHeader, Provenance, Practitioner; `subject` por `urn:uuid` | emparejado `Patient#1` (unico), `Encounter#1` (referencia); `otros_tipos = {MessageHeader: 1, Provenance: 1}`; 0 cuentan | `subject` a un fullUrl inexistente → `referencia_rota` PID-3; `subject` como `{identifier}` lógico → 0 cuentan (nota convención) |
| P-CV-5 | lector §2.2 | dos Patient (uno con el identifier del mensaje, otro sin) | emparejado por `identifier`; `recurso_duplicado` PID | un Patient → `unico` |
| P-CV-6 | lector ORU | 2 OBR × 2 OBX; `result[]` por fullUrl; una Observation sin referencia | `Observation#1.1..#2.2` por `referencia`; la sobrante → `recurso_inventado` | intercambiar una Observation entre los dos DR → `result` de ambos cuenta (`referencia_rota`); orden invertido de `result[]` → 0 cuentan |
| P-CV-7 | perfil CX | PID-3 `X1^^^H&1.2&ISO^MR~X2^^^H^PI`; Bundle con los dos identifier y `assigner` | 0 cuentan | solo `X1` → `dato_perdido` PID-3; `X1` con `type.coding.code = PI` → `valor_distinto` |
| P-CV-8 | perfil XPN | PID-5 `de la&Cruz^Luis Miguel^José^Jr^Dr^^L~Pérez^Ana^^^^^B` | `family` «de la» **o** «de la Cruz» OK; `given[1]` «Luis Miguel»; `given[2]` «José»; `use official`; segundo nombre sin `use` | segundo nombre con `use official` → `codigo_mal_mapeado` (Q-CV-D-8); `given` = ["Luis","Miguel","José"] → `valor_distinto` PID-5 |
| P-CV-9 | perfil XAD/XTN | PID-11 `C/ A 1&2º&B^Esc 3^Madrid^M^28001^ES^H`; PID-13 `^PRN^PH^^^^^^^^^+34 600` y `^^Internet^a@b.c` | `line` [«C/ A 1», «2º», «B», «Esc 3»], `use home`; telecom `+34 600` (XTN.12) `phone/home`; `a@b.c` `email` | `line` con `Esc 3` primero → `valor_distinto`; telecom con XTN.1 vacío y sin XTN.12 → `dato_perdido`; email con `system phone` → `codigo_mal_mapeado` |
| P-CV-10 | perfil PL | PV1-3 `URG^101^A^HOSP^^^^^Box 1`; Bundle con cadena bed → room → point of care → facility por `partOf` | 0 cuentan; `location.status active` | un solo Location con identifier `URG` → `dato_perdido` PV1-3 (101, A, HOSP); PV1-6 con `status active` → `valor_distinto` PV1-6 |
| P-CV-11 | perfil XCN | PV1-7 `123^García^Luis^^^Dr`, PV1-8 `456^Ruiz^Ana` | participant ATND con Practitioner `identifier 123`, `family García`; REF con 456 | PV1-7 como REF → `codigo_mal_mapeado` PV1-7; `individual` solo `display` → `dato_perdido` PV1-7 |
| P-CV-12 | vocabularios | PID-8 A; PID-16 G y U; PV1-2 O y R; PV1-4 E; PV1-10 MED y SUR; PV1-36 01 | `other`; `{v3-MaritalStatus,T}` y `{v3-NullFlavor,UNK}`; `{v3-ActCode,AMB}` y `{v2-0004,R}`; `{v2-0007,E}`; `{service-type,382}` y `{v2-0069,SUR}`; `code 01` con cualquier system | `{v2-0004,O}` → mal mapeado; `{v2-0069,MED}` → mal mapeado; PID-8 vacío con `gender unknown` → `dato_inventado` (Q-CV-D-3); PID-8 X con `gender X` → `valor_imposible_convertido` y `fhir_invalido` fusionados en PID-8 |
| P-CV-13 | status | A03 sin PV1-45 con `in-progress` y con `finished`; A11 con `cancelled`; A08 con `unknown` | 0 cuentan en los cuatro | A11 con `in-progress` → `valor_distinto` MSH-9; A01 con `finished` sin PV1-45 → `dato_inventado` PV1-45 |
| P-CV-14 | perfil ORU | ORU con OBX NM `1.20` `mg/dL^^UCUM`, OBX-8 H, OBX-11 F, OBX-7 `0.5-1.5`, OBR-25 F, OBR-7/8 | `valueQuantity.value "1.20"`, `code mg/dL system unitsofmeasure`, `interpretation {v3-ObservationInterpretation,H}`, `status final`, `referenceRange.text`, `effectivePeriod` | `value 1.2` → `valor_distinto` OBX-5; interpretation system v2-0078 → mal mapeado; `effectiveDateTime` con OBR-8 valorado → `dato_perdido` OBR-8; las 6 filas de convención: Bundle sin identifier propio ni subject lógico → 0 cuentan |
| P-CV-15 | clasificación §4 | nueve mutaciones, una por subtipo de §4.1, sobre el Bundle exacto | exactamente el subtipo previsto, uno por mutación | ocho mutaciones de forma (orden de entries, `id`, `meta`, `text`, extensión, `display`, `Bundle.type`, `subject` lógico) → 0 cuentan y 8 notas |
| P-CV-16 | versión §5 | MSH-12 2.8 con PV1-2 Z (fuera de 0004) y `class {v2-0004,Z}`; MSH-9.3 ADT_A04 con evento A04 | nota `version` L18 sin contar; nota `estructura_declarada`; el mapeo de PID-8 F sigue contando si se cambia | MSH-12 2.5 con PV1-2 Z y class literal → nota (imposible en origen: hoja no juzgada); MSH-12 2.5 con MSH-9.3 ADT_A04 → nota, no hallazgo |
| P-CV-17 | fechas §3.6 | PV1-44 `20260101103000+0100` observado `2026-01-01T09:30:00Z`; `202601011030` observado `…T10:30:00+05:00`; PID-7 `198002` observado `1980-02` | 0 cuentan | `…T10:30:00+0100` como `…T11:30:00+01:00` → `valor_distinto`; `1980-02-01` → `dato_inventado`; `2026-01-01T10:30:00` sin zona → `fhir_invalido` |
| P-CV-18 | MCP | `verificar_caso` con `punto_entrada = adt_conv` y `conversion` pasa el esquema; `consultar_tabla("perfil_guia_adt")` devuelve filas con `nivel` y `citas` | sin error; `entrada.no_evaluado` lleva la línea de conversión | `conversion.salida.bundle` de 70 000 caracteres → error de esquema (`maxLength`) |
| Controles que no cambian | — | `prueba_verificador`, `prueba_adt`, `prueba_oru`, `prueba_multitipo`, `prueba_mutantes`, autopruebas, `prueba_mcp_verificador`; la regresión 2.721 y la concordancia A1 | idénticas | — |

---

## 7. La previsión, a ciegas, por conversor y familia

Escrita sin ver una plantilla ni una salida. Razono desde lo que la guía hace difícil (modelos encadenados, condiciones por tipo, dos
representaciones admitidas) y desde lo que un conversor por plantillas tiende a hacer. La previsión sellada de CV2 toma estas tablas y les
añade las cuentas reales de E-CV-3 y del corpus (n por evento, n con PID-3 múltiple, n con PL completo, n con SN…).

### 7.1 Mecanismos previstos (por familia; probabilidad por conversor: A alta, M media, B baja)

| Id | Mecanismo (hecho, subtipo) | Microsoft | LinuxForHealth | Dónde morderá en el corpus |
|---|---|---|---|---|
| MC-ADT-1 | PV1-2 → `class` literal v2-0004 o sin system v3-ActCode (`codigo_mal_mapeado` PV1-2) | M | M | todas las bases con PV1-2 ∈ {E, I, O, P} |
| MC-ADT-2 | PID-8 vacío → `gender unknown` (`dato_inventado` PID-8; Q-CV-D-3) | M | M | las bases con PID-8 vacío |
| MC-ADT-3 | PL → una sola Location o solo PL.1 (`dato_perdido` PV1-3/6/11) | M-A | M | bases con PL.2/PL.3 valorados |
| MC-ADT-4 | PID-16 → v2-0002 literal en vez de v3-MaritalStatus/NullFlavor (`codigo_mal_mapeado` PID-16) | M | M | bases con PID-16 |
| MC-ADT-5 | PV1-10 MED/URO → v2-0069 literal (`codigo_mal_mapeado` PV1-10) | M | M | bases con MED/URO |
| MC-ADT-6 | PID-7 con precisión reducida → fecha completada (`dato_inventado` PID-7) | B-M | B-M | bases `YYYY`/`YYYYMM` |
| MC-ADT-7 | XPN.7 unmatched (B, A…) → `use` inventado (`codigo_mal_mapeado` PID-5) | M | B | bases con segunda repetición de PID-5 |
| MC-ADT-8 | Telecom: XTN.1 preferido a XTN.12; XTN.4 sin `system email` (`valor_distinto`/`codigo_mal_mapeado` PID-13) | M | M | bases con XTN.12 o XTN.4 |
| MC-ADT-9 | Encounter.status fuera del conjunto (A11 no cancelado; status fijo) (`valor_distinto` MSH-9/PV1-2) | B | B-M | A11, A03 |
| MC-ADT-10 | Participantes: solo PV1-7, o `individual` solo con `display` (`dato_perdido` PV1-8/17) | M | M | bases con PV1-8/17 |
| MC-ADT-11 | Rechazo de mensajes con segmentos fuera de sitio o Z (`rechazo_incorrecto`) | B | B-M | E2 con OBX tras AL1, Z |
| MC-ADT-12 | DTM sin zona → `dateTime` sin zona (`fhir_invalido`) o reducido a fecha (`dato_perdido`) | B | B-M | PV1-44/45, PID-29 sin zona |
| MC-ORU-1 | NM/SN → número reserializado: `1.20` → `1.2` (`valor_distinto` OBX-5) | A | A | toda base con ceros finales |
| MC-ORU-2 | SN: `valueString` en vez de ratio/range/quantity, o comparador perdido (`valor_distinto`/`dato_perdido` OBX-5) | M-A | M | bases con SN |
| MC-ORU-3 | OBX-6: `unit` de CWE.1 en vez de CWE.2; `code` sin `system`; UCUM no canónico (`valor_distinto`/`dato_perdido` OBX-6) | M | M | todas las NM con unidad |
| MC-ORU-4 | OBX-8 → `system` v2-0078 (`codigo_mal_mapeado` OBX-8) | M | M | bases con OBX-8 |
| MC-ORU-5 | OBR-8 valorado → `effectiveDateTime` solo (`dato_perdido` OBR-8) | M | M | bases con OBR-8 |
| MC-ORU-6 | TX/FT: escapes sin resolver o repeticiones perdidas (`valor_distinto` OBX-5) | M | M | bases con `\T\`, repeticiones |
| MC-ORU-7 | `result[]` cruzados entre dos OBR o Observation sin referencia (`referencia_rota`/`recurso_inventado`) | B | B-M | bases con 2 OBR |
| MC-ORU-8 | OBX-11 F/P/C bien; D → `entered-in-error` bien (0 hallazgos) | — | — | — |
| MC-ORU-9 | CE.3 LN → `http://loinc.org` bien; nombre local → uri propia (convención) | — | — | — |
| MC-ORU-10 | OBR-25 vacío → status inventado (convención) / rechazo (aceptable) | — | — | bases sin OBR-25 |

### 7.2 Previsión agregada (lo que CV2 debe encontrar, con cota)

| Conversor × familia | Corre aislado (E-CV-3) | `correcto` | `fallo_silencioso` | `rechazo_incorrecto` | `indeterminado` | Mecanismos que cuentan (distintos) | ≥ 1 **nueva confirmada** tras CV3 |
|---|---|---|---|---|---|---|---|
| Microsoft · ADT (479: A1 263 + E2 216) | sí (0,8) | 35-65 % | 30-60 % | 0-5 % | ≤ 2 % | 3-6 | 0,6 |
| Microsoft · ORU (40) | sí | 20-50 % | 45-80 % | 0-5 % | ≤ 2 % | 2-5 | 0,65 |
| LinuxForHealth · ADT (479) | sí (0,8) | 30-60 % | 35-65 % | 0-10 % | ≤ 2 % | 3-6 | 0,6 |
| LinuxForHealth · ORU (40) | sí | 20-50 % | 45-80 % | 0-10 % | ≤ 2 % | 2-5 | 0,65 |
| Muestras aceptadas (7 ADT + 3 ORU) | — | — | — | — | — | ≥ 70 % de lo que cuente será `ya_declarada` (son sus propias pruebas) | — |
| Muestras 2.8 (52) | — | se juzgan; ≥ 1 nota `version`/`estructura_declarada` por mensaje; **0** hallazgos de tabla o estructura que cuenten | | | | | |

- Al menos una nueva confirmada en **alguno** de los dos: **0,8**. Frase fija prevista: N ≥ 2, K ∈ {1, 2}, D ≥ 3, C ≥ 10 (las convenciones
  serán la clase más numerosa de diferencias brutas: ids, fullUrl, meta, MessageHeader/Provenance, display, orden de coding).
- **Fuera de previsto** = un mecanismo que cuente y no esté en 7.1, un porcentaje fuera de su rango, un `indeterminado` > 2 % (lector),
  o un conversor que rechace > 10 % del corpus 2.5. Cada uno se adjudica (juez / perfil / corpus / caja) con cita antes de CV3.
- Lo que **no** preveo (y si aparece, es la señal buena): un `recurso_inventado`, un `referencia_rota` en `subject`, o un `fhir_invalido`
  masivo: si un conversor público hiciera eso en 2.5 nominal, ya estaría declarado en sus issues.

---

## 8. Plan CV1-CV4, con «hecho cuando», parada y tope

Tope de la etapa: cuatro sesiones hasta el 20-nov (`ANTES:105`); CV-pre y CV0 gastan parte de la primera. Reparto propuesto del resto:
**CV1 ≈ 1,5 sesiones, CV2 ≈ 0,5, CV3 ≈ 1, CV4 ≈ 0,5**. Primero lo que puede tumbarlo (E-CV-3).

| Fase | Qué, en orden | Hecho cuando | Parada |
|---|---|---|---|
| **CV1-a** E-CV-3 (≤ 1,5 h) | Caja sin red, sin privilegios, versión fijada con huella (condición 2, `ANTES:43-44`): un artefacto por conversor; un mensaje A01 y un ORU nominales del corpus; se guarda `conversion.salida` tal cual. Se mide: corre / no corre; tiempo; forma de la salida (¿Bundle?, `type`, ¿fullUrl `urn:uuid` o relativos?, ¿contained?, ¿ids?) solo para el **informe de E-CV-3**, nunca para tocar el perfil | los dos conversores contestados; las dos salidas de muestra guardadas con su huella | **ninguno corre aislado → la etapa para** (`ANTES:70`); uno solo → sigue con uno y K ≤ 1 |
| **CV1-b** pruebas en rojo | P-CV-1..18 escritas y en rojo por la razón prevista; controles en verde | cada prueba falla donde debe | una prueba que no se puede poner en rojo = la pieza no está definida: vuelve a este diseño como Q-CV-D |
| **CV1-c** código | PE `adt_conv`/`oru_conv` → `conversion.leer_bundle`/`emparejar` → `PERFIL_GUIA_*` como datos → `esperado_guia` → `comparar` → `verificar` → la línea en `verificador.verificar` → esquema y MCP (`consultar_tabla`, `_no_evaluado`, leyenda `conversion`) | P-CV en verde; todas las suites de hoy en verde sin ningún cambio salvo los declarados (enum del esquema, texto de `info_verificador`); regresión 2.721 y concordancia A1 idénticas | cualquier rojo no declarado |
| **CV1-d** primer Bundle real por el lector | Las dos salidas de muestra de CV1-a pasan por `leer_bundle`/`emparejar` (sin perfil todavía): `fallos = []`, emparejamiento `unico`/`referencia`, 0 `referencias_rotas` salvo las que se vean a ojo | el lector lee ambas sin `indeterminado` | un `indeterminado/emparejamiento` → se corrige el lector (es la pieza que no se puede diseñar a ciegas) y se declara DV-CV |
| **CV2** previsión sellada y corpus | §7 completada con las cuentas del corpus (n por mecanismo) y sellada con huella **antes** de juzgar; se juzgan A1 263, E2 216, ORU 40 con cada conversor, más las 10 muestras aceptadas y las 52 de 2.8 (flags L18); tabla por conversor × familia × categoría × mecanismo; `fuera de previsto` adjudicado | 0 fuera de previsto sin adjudicar; cada adjudicación con cita | un defecto del juez se arregla con su prueba y CV2 se repite entero; **dos repeticiones como máximo**; luego el mecanismo pasa a L-CV y se declara |
| **CV3** contraste y clase | Por mecanismo (no por caso): (1) salidas esperadas y pruebas publicadas del proyecto; (2) sus issues (abiertos y cerrados); (3) relectura del ConceptMap y la hoja citados → `clase_cv` por §4.3; DV-CV por cada corrección del perfil, rejuicio ≤ 2 | cada mecanismo con clase y referencia; cada `nueva` reproducida con un mensaje público y cita completa (§3.7) | un mecanismo que no se puede clasificar en 30 min pasa a Q-CV-D y no cuenta como nueva |
| **CV4** cierre | `RESULTADO-CONVERSORES.md` con la frase fija (`ANTES:100-101`) y, si procede, la declaración de pieza de portfolio; MCP con S-CV/L-CV/DV-CV/AMB-CV y `preguntas_pendientes`; suites; guarda en LIMPIO; nada se publica ni se reporta sin el visto bueno (condición 6) | todo lo anterior | guarda no LIMPIO → no se publica |

---

## 9. Límites declarados L-CV-n (para `info_verificador.limites`)

| L | Redacción |
|---|---|
| L-CV-1 | «La tabla 0354 y las tablas de valores de versiones distintas de 2.5 no están en la evidencia: con MSH-12 ≠ 2.5 la legalidad de un código o de la estructura no se juzga (nota `version`, certeza L18); MSH-9.3 nunca cuenta en `adt_conv`/`oru_conv`.» |
| L-CV-2 | «Las fórmulas de XTN.5-8 → value del ConceptMap xtn-to-contactpoint no están en el paquete (solo sus condiciones): se comprueba que el valor contenga XTN.7 y, si valorados, XTN.6 y XTN.5; el formato es convención.» |
| L-CV-3 | «La tabla nombre de sistema → uri (0396 → uri) no está en el paquete; se fijan solo LN, SCT/SNM/SNM3 y UCUM/ISO+ por las uris canónicas de FHIR R4, citadas por sección fuera de la carpeta, y la precisión significativa del decimal (R4 datatypes §decimal) igual; los demás nombres son convención.» |
| L-CV-4 | «Las extensiones nunca cuentan, aunque lleven dato (patient-birthTime, FN.2-5, subject-locationClassification, alternate-codes de OBX-11 X): la regla de la etapa las declara forma.» |
| L-CV-5 | «Solo se juzgan Patient, Encounter, Observation y DiagnosticReport en los elementos de `perfil_guia_*`; MessageHeader, Provenance, Organization, PractitionerRole, Location (salvo como destino de Encounter.location), Practitioner (salvo como destino de participant), Specimen, ServiceRequest, Account, Coverage, RelatedPerson, Device y los elementos fuera del perfil son nota.» |
| L-CV-6 | «OBX-5 repetido (component / varias Observation / concatenación) y OBX-11 N (dataAbsentReason) no se juzgan: nota.» |
| L-CV-7 | «Los OBX bajo SPM, los de PATIENT_OBSERVATION, los OBX de un ADT y los PATIENT_RESULT adicionales solo se cuentan (recurso presente o ausente); su contenido no se compara.» |
| L-CV-8 | «El juez no ejecuta conversores; con `salida.estado` vacío o sin respuesta no distingue la caja del conversor: indeterminado.» |
| L-CV-9 | «`display`, `text` (narrativa), `meta`, `id`, `fullUrl`, `Bundle.type`/`timestamp`/`identifier` y `entry.request` nunca se juzgan.» |
| L-CV-10 | «La clase nueva / ya declarada / convención no la calcula el juez: la pone CV3 con las salidas esperadas, pruebas e issues del proyecto, por mecanismo.» |
| L-CV-11 | «No hay validador FHIR completo: solo cardinalidad 1..1, bindings `required` y formato de los primitivos de los elementos del perfil.» |
| L-CV-12 | «El perfil del laboratorio (canónico y S-n) no se aplica a terceros; `perfil_valor` admite solo `guia`.» |
| L-CV-13 | «Un cable con varios MSH: solo se juzga el primero.» |

### 9.1 Índice de lecturas adoptadas AMB-CV-n (para `info_verificador.ambiguedades`; cada una con su alternativa)

| AMB | Enunciado | Lectura adoptada | Alternativa |
|---|---|---|---|
| AMB-CV-1 | Código origen en minúscula (`f`): las tablas v2 y los ConceptMap solo listan mayúsculas | Convención: mapearlo o no son ambos aceptables | Imposible (hoja no juzgada) |
| AMB-CV-2 | FN con subcomponentes (`de la&Cruz`): la guía manda FN.2-5 a extensiones (forma) | `family` = FN.1 **o** FN.1-5 unidos por espacio | Solo FN.1 |
| AMB-CV-3 | XPN.3 / XCN.4 con varios nombres separados por espacio: el ConceptMap deja abierto si es un `given` o varios | Entero o partido, ambos | Solo entero (literal `given[2]`) |
| AMB-CV-4 | PID-7 con hora y zona: la guía dice «re-formatting» ISO 8601, no conversión | `birthDate` = la fecha escrita, sin desplazar | Fecha del instante en UTC |
| AMB-CV-5 | PV1-2 = N: la guía mapea PV1 → Encounter sin condición; el cap. 3 dice que el PV1 «is not applicable» | Encounter presente (class v2-0004 N) o ausente: convención | Encounter obligatorio (`recurso_ausente`) |
| AMB-CV-6 | A11 con PV1-45 valorado: el mapa de mensaje da `cancelled`, el de segmento `finished` | Las dos admitidas | Solo `cancelled` |
| AMB-CV-7 | OBX-14 vacío: la guía no da `effective`; el cap. 7 solo exige OBX-14 cuando difiere del OBR | Ausente o la fecha de OBR-7 | Solo ausente |
| AMB-CV-8 | OBR-2/3 → identifier «If ORC-2 … is not valued OR there is ORC segment»: condición ambigua | El valor con su type PLAC/FILL, venga de OBR o de ORC | Solo cuando no hay ORC |
| AMB-CV-9 | OBR-22 con menos precisión que segundos: `instant` exige segundos y zona | Ausente, o completado con `:00` y una zona | Solo ausente |

---

## 10. Preguntas: lo que no decide ni el estándar ni la guía

### 10.1 Q-CV-D-n (diseño, para Jev)

| Q | Pregunta | Recomendación | Alternativa | Qué cambia según la respuesta |
|---|---|---|---|---|
| Q-CV-D-1 | ¿Dos PE (`adt_conv`, `oru_conv`) con el contrato de cada familia, o un PE `conv` parametrizado? | **Dos PE**: el contrato (tipos, consumidos, p5) es de la familia y `info_verificador` lo expone como siempre | un PE con `familia` en la evidencia | el enum de `punto_entrada` (2 valores o 1), `PE.estructura_de` sin cambios (rec.) o con rama |
| Q-CV-D-2 | ¿La categoría de «Bundle sin error y con hallazgos» conserva el nombre `fallo_silencioso` (subtipos `convertido`/`aceptado_imposible`) o se llama `conversion_incorrecta`? | **Conservar** `fallo_silencioso`: la leyenda y el explicador MCP ya lo conocen; el subtipo lo distingue | `conversion_incorrecta` | leyenda nueva con 5 categorías (rec.) o 6; las instrucciones del explicador (`mcp_verificador.py:101`) cambian solo en la alternativa |
| Q-CV-D-3 | PID-8 vacío y `gender: unknown`: ¿`dato_inventado` (cuenta) o convención? | **Cuenta**: ningún ConceptMap tiene fila para vacío, R4 distingue ausente de `unknown`, y el mensaje no dijo «desconocido» | convención (nota) | MC-ADT-2 entra o sale de lo que cuenta; P-CV-12 control |
| Q-CV-D-4 | Orden de `DiagnosticReport.result[]`, `name[]`, `identifier[]`, `coding[]`: ¿forma (multiconjunto) o dato? | **Forma**: FHIR no da semántica al orden de esas listas; la guía numera `coding[1]/[2]` solo para distribuir CE.1-3/CE.4-6 | orden = dato (como D-ADT-5 en el laboratorio) | §2.4; P-CV-6 y P-CV-15 controles |
| Q-CV-D-5 | Entradas de más en un elemento repetible (un identifier que la herramienta añade, un telecom de PID-40) con valor que no está en el mensaje: ¿nota `extra` o `dato_inventado`? | **Nota**: la guía mapea más campos de los proyectados (PID-2/4/19/20/40, PV1-50) y el lector no puede distinguir «añadido» de «mapeado desde un campo no proyectado» | `dato_inventado` cuando el valor no aparece en ningún campo del mensaje | §3.0; cuántos hallazgos de identifier cuentan |
| Q-CV-D-6 | PV1-2 = N sin Encounter: ¿convención (AMB-CV-5) o `recurso_ausente`? | **Convención**: la guía no condiciona PV1 → Encounter, pero el cap. 3 dice que el PV1 «is not applicable» con N; las dos lecturas son defendibles | `recurso_ausente` (literal de la guía) | A31 N y A08 N: 0 hallazgos (rec.) o uno por mensaje |
| Q-CV-D-7 | Conversor que devuelve `error` ante un valor imposible (PID-7 inválido, PID-8 ∉ 0001): ¿`rechazo_aceptable` (nota) o `rechazo_incorrecto`? | **Aceptable**: §2.9.2.2 b admite AE por contenido en un receptor; un conversor que no sabe mapear puede parar | `rechazo_incorrecto` (la guía manda omitir el elemento y seguir) | E2 trae bases con imposibles: cuántos `rechazo_incorrecto` salen |
| Q-CV-D-8 | Código `unmatched` en un ConceptMap de un elemento opcional (XPN.7 B, XAD.7 N, XTN.2 ORN) mapeado por el conversor a algún `use`: ¿`codigo_mal_mapeado` o convención? | **Cuenta**: el ConceptMap dice `unmatched` (sin destino), un `use` añade un significado que la guía niega | convención | MC-ADT-7; P-CV-8 control |
| Q-CV-D-9 | `family` con FN subcomponentes: ¿FN.1 solo (literal) o también los subcomponentes unidos (AMB-CV-2)? | **Las dos** (convención) | solo FN.1 | P-CV-8 |
| Q-CV-D-10 | Decimal reserializado (`1.20` → `1.2`): ¿cuenta (`valor_distinto`, precisión significativa en R4) o convención? | **Cuenta**: R4 lo declara; el laboratorio lo midió como diferencia real (S67) | convención | MC-ORU-1 es, probablemente, el mecanismo más frecuente: decide buena parte de N |
| Q-CV-D-11 | `Encounter.status` en A11 con PV1-45 valorado: ¿solo `cancelled` o también `finished` (AMB-CV-6)? | **Las dos** | solo `cancelled` (el mapa de mensaje es más específico) | P-CV-13 |
| Q-CV-D-12 | Las muestras 2.3/2.4/2.6/2.8: ¿se juzgan con las banderas L18 (§5.1) o se dejan fuera? | **Se juzgan** con banderas: cuestan 0 y dan los `ya_declarada` del control positivo | fuera | corpus secundario presente o no en la tabla de CV2 |

### 10.2 Q-CV-A-n (alcance)

| Q | Pregunta | Recomendación | Alternativa | Qué cambia |
|---|---|---|---|---|
| Q-CV-A-1 | ¿Se lee la tabla 0354 de v2.8 (el texto de HL7 es gratuito y no se redistribuye) para contestar lo de `ADT_A04` antes del RESULTADO? | **Sí, en CV1-a** si se obtiene sin gasto; se cita por sección sin copiar el texto | queda como nota L18 para siempre | la frase sobre MSH-9.3 en el RESULTADO: «es correcto en 2.8» / «es un defecto de la muestra» / «no se sabe» |
| Q-CV-A-2 | OBX bajo SPM, PATIENT_OBSERVATION y PATIENT_RESULT adicionales: ¿solo recuento (L-CV-7) o se extiende `esperado_guia` para compararlos? | **Solo recuento** (cabe en el tope) | extender (≈ ½ sesión; toca `agrupar`, que no se edita: habría que duplicarla) | cobertura de ORU; P-CV-6 |
| Q-CV-A-3 | ¿Google (Whistle) entra si los dos corren y sobra tope? | como Q-CV-1: **solo si sobra** tras CV3 | no | K ∈ {1,2} o {1,2,3} |
| Q-CV-A-4 | Las fórmulas de XTN.5-8 y la tabla 0396 → uri están en hojas de la guía que no están en la carpeta: ¿se traen (commit `873b331`) para cerrar L-CV-2 y L-CV-3? | **Sí si cuesta < 15 min** en CV1; si no, L-CV-2/3 se quedan | se quedan | «contiene» frente a igualdad exacta en telecom; convención frente a cuenta en los `system` de otros nombres |
| Q-CV-A-5 | ¿CV3 lee los issues con red (fuera de la caja, por Claude) y los guarda como referencias en el RESULTADO privado? | **Sí**: es la condición 4 (`ANTES:49-50`); la caja del conversor sigue sin red | solo salidas esperadas y pruebas publicadas (ya descargadas) | D (ya declaradas) más o menos completo |
| Q-CV-A-6 | ¿Se publica el perfil «guía» (`perfil_guia_*`, solo tablas y citas, sin texto de HL7) en el repo público con el MCP? | **Sí**, tras la guarda (memoria «el texto de HL7 no se redistribuye») | privado hasta el visto bueno | qué va en el commit de CV4 |

---

## 11. Los tres riesgos que más me preocupan

1. **El emparejamiento está diseñado a ciegas y es lo que no se puede diseñar a ciegas.** Si un conversor devuelve referencias en una forma
   que §2.1 no contempla (ids sin fullUrl y referencias por `urn:uuid` distintas; `contained` sin `#`; Practitioner solo como `display`), el
   lector dará `indeterminado/emparejamiento` o `referencia_rota` en masa y todo lo demás no se verá. Por eso CV1-d pasa el primer Bundle
   real por el lector **antes** del perfil, y cualquier ajuste es DV-CV con la salida como cita, no un parche silencioso. Nivel: alto.
2. **El perfil cuenta de más donde la guía admite más de lo que leí.** Cada `nueva` que CV3 baje a convención por una segunda lectura del
   ConceptMap es un rejuicio (tope: dos). Si hay más de dos mecanismos así, la etapa termina con una N inflada o sin tiempo para el
   contraste. Mitigación: los puntos donde dudé están escritos como AMB-CV-1..9 y Q-CV-D con la alternativa; Jev decide antes de CV2.
   Nivel: medio-alto.
3. **E-CV-3 y la versión.** Un conversor que no corre sin red en versión fijada, o que rechaza el corpus 2.5 por no ser 2.8, deja K = 1 o
   para la etapa. Se mide en la primera hora y media de CV1 con la regla de parada escrita; y si solo queda uno, la previsión de §7.2 ya
   está dividida por conversor para que el resultado siga siendo legible. Nivel: medio.

---

## Resumen (≤ 15 líneas)

1. Secciones: 0 decisiones; 1 punto de entrada; 2 lector; 3 perfil «guía»; 4 significado del dato y clasificación; 5 versión; 6 P-CV; 7 previsión; 8 plan; 9 L-CV; 10 preguntas; 11 riesgos.
2. Punto de entrada: dos PE nuevos `adt_conv`/`oru_conv` con `solo_transformacion`; evidencia `{mensaje, conversion: {conversor, salida}}` sin acuse ni sesiones; una línea de despacho en `verificador.verificar`; categorías `correcto`, `fallo_silencioso` (convertido/aceptado_imposible), `rechazo_incorrecto`, `indeterminado`, `fuera_de_alcance`.
3. Lector: Bundle leído como texto, referencias resueltas por fullUrl/`urn:uuid`/relativa/lógica, emparejamiento por papel (Patient del PID, Encounter del PV1, DR por OBR, Observation por `result[]` y código), sobrantes como duplicado/inventado, cadenas de Location y Practitioner recorridas.
4. Perfil «guía»: tabla de datos por elemento con nivel `cuenta`/`convencion`/`forma`, valor por ConceptMap (CX, XPN, XAD, XTN, PL, XCN; 0001, 0002, 0003, 0004×2, 0007, 0069, 0112 literal, 0136, 0190, 0200-0203; 0078, 0085, 0123), conjuntos admitidos para `Encounter.status`; las 6 filas de convención de ORU apartadas y sustituidas por «subject resuelve al Patient».
5. Significado: ocho clases (valor distinto, dato perdido, dato inventado, código mal mapeado, valor imposible convertido, recurso ausente/duplicado/inventado, referencia rota, FHIR inválido); forma = orden, ids, meta, extensiones, display, forma de la referencia, recursos fuera del perfil; nueva/ya declarada/convención la pone CV3 por mecanismo con regla y tope de dos rejuicios.
6. Versión: manda MSH-12 escrita; los ConceptMap cuentan en cualquier versión; legalidad de tabla/estructura fuera de 2.5 no cuenta (L18); MSH-9.3 nunca cuenta aquí y la 0354 de v2.8 se lee antes de opinar (Q-CV-A-1).
7. P-CV-1..18 con control negativo: PE y salidas de error, lector (referencias, duplicados, ORU 2×2), cada tipo de dato y vocabulario, conjuntos de status, las ocho clases y ocho formas, versión y fechas por instante, MCP.
8. Previsión: ambos corren (0,8); ADT `correcto` 30-65 % y `fallo_silencioso` 30-65 %; ORU `fallo_silencioso` 45-80 %; 3-6 mecanismos ADT y 2-5 ORU por conversor (clase v2-0004, gender inventado, Location aplanada, marital/serviceType literales, decimal `1.20`, SN, unidades, interpretation v2-0078, OBR-8 perdido); ≥ 1 nueva confirmada por conversor 0,6, en alguno 0,8; muestras 2.8 solo notas.
9. Plan: CV1 E-CV-3 (≤ 1,5 h, parada si ninguno corre) → P-CV en rojo → código → primer Bundle real por el lector; CV2 previsión sellada y corpus con 0 fuera de previsto (≤ 2 repeticiones); CV3 contraste por mecanismo y clase; CV4 RESULTADO con la frase fija, MCP, guarda LIMPIO.
10. Preguntas: **12 Q-CV-D** y **6 Q-CV-A**; 13 L-CV; 9 AMB-CV.
11. Riesgos: el emparejamiento a ciegas (se prueba con el primer Bundle real antes del perfil); el perfil que cuenta de más (AMB-CV y Q-CV-D escritas, tope de dos rejuicios); E-CV-3 y la versión (regla de parada en la primera hora y media).
