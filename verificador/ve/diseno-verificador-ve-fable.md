> *Copia pública: la procedencia y el desglose por origen de la muestra privada del sitio están redactados (punto 4 de la revisión de la publicación). Los totales y el mecanismo son los del original.*

<!-- modelo: Claude Fable 5.1 (claude-fable-5-1); fecha: 22-oct-2026; «VE0: cambios del verificador (14k); a ciegas de los corpus de rejuicio; leído solo scratchpad/ve0» -->

# Diseño VE0: cerrar los huecos medidos del juez (MMI-12, MMI-19, Q-MS-9, Q-MI-V-9) sin rejuzgar lo sellado

Documento público. Sin credenciales, sin nombres de máquinas ni de personas, sin datos de pacientes (los ejemplos usan `X1`/`V1`).

Convenciones: **S-VE-n** decisión propuesta (pasa a S-n cuando Jev decida); **R-VE-n** regla implementable; **P-VE-n** prueba (falla
con el juez de hoy, pasa con el nuevo, o control que no cambia); **E-VE1-n** sonda de solo lectura o de FHIR a mano, antes de tocar
código; **L-VE-n** límite declarado; **Q-VE-D-n** pregunta de diseño (Jev); **Q-VE-A-n** pregunta de alcance (quien decide el alcance);
**M12 / M19 / MS9 / CT** los cuatro mecanismos de cambio, para atribuir cada diferencia del rejuicio. **DV-VE-n** queda reservada a quien
implemente. Las citas son `fichero:línea` dentro de esta carpeta; las S-n, L-n y A-n son las de `verificador/info_verificador.json`.

Punto de partida fijado (`resultados/ANTES-ETAPA-VERIFICADOR.md:7-17`): entran A y B (MMI-12, MMI-19, Q-MS-9, Q-MI-V-9); C y D salen
como límite; lo sellado no se rejuzga; el juez no ha cambiado desde el cierre del modo sitio (huella
`info_verificador.json:5`); la línea base existe (`resultados/RESULTADO-VE-PRE.md:7-24`).

---

## 0. Resumen de las decisiones que lo condicionan todo

| | Decisión | Por qué (cita) |
|---|---|---|
| S-VE-1 | **Canónico obligatorio** en los tres puntos con mapeador (`adt_a01`, `adt_fhir`, `oru_fhir`) cuando el acuse observado es AA **y** la sesión trae una fila terminal de éxito (L01/L02/L15/L16). Su ausencia es `fidelidad/sin_canonico` (hecho `existencia`), cuenta, y da `fallo_silencioso`. Sin fila de éxito no se exige (L5). | AA significa «process the message successfully» (`estandar/hl7v25_CH02.txt:1457-1460`); el canónico es el registro de ese procesamiento que el contrato de la evidencia exige (`verificador/esquema_evidencia.json:51-65`, `:297-303`). VE-pre midió 0 falsas alarmas con esa condición exacta (`RESULTADO-VE-PRE.md:52-62`). |
| S-VE-2 | **Una sola versión para S22: la escrita en MSH-12.1.** La versión asumida del perfil (H4) solo decide la aceptación (P2b). Es S103 literal, aplicada al acuse. | MSH-12 «is matched by the receiving system to its own version to be sure the message will be interpreted correctly» (`hl7v25_CH02.txt:4512-4513`); S22 tolera porque «puede ser legal en su versión» (`info_verificador.json:61`, L18 `:378`): sin versión escrita no hay versión en la que serlo, y mandan las tablas de v2.5 (L17 `:377`). S103 ya lo dice (`:142`); solo el acuse no lo aplica (`verificador/acuse_referencia.py:645`). |
| S-VE-3 | **El lector relee el almacén por los identificadores del mensaje (regla del propio juez) y por el paciente** (`Encounter?subject:identifier=…`), no solo por el canónico observado; la evidencia gana `almacen_adt.visitas_por_paciente` con el censo previo (`previos`). El juez juzga lo nuevo por paciente: con PV1-2 = N es `fidelidad/almacen` hecho `PV1-2`; sin PV1-19 compara el contenido (cierra L-ADT-19). | `Encounter.subject` es referencia lógica por identifier (S80 `info_verificador.json:119`); el parámetro `patient` exige `resolve()` (`estandar/fhir_r4_encounter_search.json:15-17`) y no casa con una referencia sin `reference`; `subject` sí es el elemento (`:135-138`) y R4 permite el modificador `:identifier` sobre un parámetro de referencia (L-VE-5). 10 de 13 casos de MMI-19 van sin PV1-19 (`RESULTADO-VE-PRE.md:48-49`). |
| S-VE-4 | **La representación del canónico ADT se documenta desde una fuente única en el código** (`mapeador_adt.CONTRATO_CANONICO`), expuesta por `consultar_tabla("canonico_adt")` y renderizada en `contratos/contrato_canonico_adt.md`; la representación queda **como está** (códigos ya mapeados a FHIR, `GivenName` unido, visita vacía con PV1-2 = N). | Es lo que el juez lee hoy (`verificador/mapeador_adt.py:605-624`, `:626-650`) y lo que la comparación a tres necesita (C en términos FHIR: `almacen_adt.py:142-147`). Un circuito hecho solo con el contrato público difirió en 128 de 128 (`RESULTADO-MIRTH.md:133-134`). |
| — | **Lo que no cambia:** acuse salvo la línea de S22; `mapeador_adt`, `mapeador_oru`, `mapeador_referencia` (salvo la tabla documental); los circuitos; los RESULTADO sellados; el perfil del sitio y sus mandos. | Condiciones 2 y 5 (`ANTES-ETAPA-VERIFICADOR.md:87-92`). |

---

## 1. MMI-12 (Q-MI-V-5): el canónico obligatorio

### 1.1 El mecanismo de hoy, con cita

- `verificador._mapeador` alinea los canónicos por sesión (`verificador/verificador.py:159`) y, si **ninguna** sesión trae un diccionario,
  pasa la lista vacía (`:160-161`). Con lista vacía, `revisar` devuelve `None` sin comparar nada (`verificador/mapeador_referencia.py:540`,
  `verificador/mapeador_adt.py:814`; `mapeador_oru` igual). Resultado: `correcto` con AA, L16 y `canonico_adt = null`
  (`RESULTADO-VE-PRE.md:31-39`; MI3: 128 mordidos, 0 cazados, `RESULTADO-MIRTH.md:66,71-73`).
- Con un hueco en una lista que sí tiene algún diccionario (`[None]`), `revisar` emite «no hay canónico para este mensaje»
  (`mapeador_referencia.py:554-556`, `mapeador_adt.py:828-830`) y el verificador lo convierte en `fidelidad/sin_canonico`
  (`verificador.py:291-299`, DV-V1 `:9-11`). Ese camino ya existe y es el que se generaliza.
- El hueco es más ancho que `adt_fhir`: el mismo `_mapeador` sirve a `adt_a01` y a `oru_fhir` (`verificador.py:265-270`); en `oru_fhir`
  esconde un fallo real (`RESULTADO-VE-PRE.md:41-44`).

### 1.2 La regla (R-VE-1)

Para un punto de entrada **con mapeador** (`pe["nombre"] == "adt_a01"` o `pe.get("mapeador")` en `{"adt", "oru"}`: `verificador/puntos_entrada.py:70-73`,
`:112-123`, `:127-141`), y para cada mensaje k del cable:

| Condición | Hallazgo | Cuenta | Categoría resultante |
|---|---|---|---|
| MSA-1 observado = AA (`_obs_ack`, `verificador.py:133-148`) **y** `lec["por_mensaje"][k]["destino"] == "exito"` (fila terminal L01/L02/L15/L16: `verificador/lectura_evidencia.py:34-35`, `:49-51`, `:250-263`) **y** la sesión k no trae un diccionario en la clave del PE (`canonico` / `canonico_oru` / `canonico_adt`) | `fidelidad` / `sin_canonico`, hecho `existencia`, origen `mapeador`, certeza `literal`, causa `escritura` | sí | `fallo_silencioso` (leyenda `info_verificador.json:325`; `_subs` lo cuenta como «guardado», `verificador.py:518-522`) |
| AA sin fila de éxito (sin log, L13, F3…) y sin canónico | `nota` / `sin_canonico` (solo cuando existe la línea del mapeador, es decir, en lotes con algún canónico) | no | la de hoy |
| MSA-1 ≠ AA | nada (su canónico no se compara: L24 `info_verificador.json:383`) | — | la de hoy |
| PE sin mapeador (`adt`, `oru`, `siu`, `ord`, `mdm`) | nada: rama `else` (`verificador.py:271-272`, L-MT1 `info_verificador.json:385`) | — | la de hoy |

Texto del hallazgo: `no hay canónico para este mensaje: el circuito acusó AA y declaró haber escrito (<L16|L01|L02|L15>) sin registrar lo
que escribió; el contrato del punto <pe> lo exige (S-VE-1)`. Además, con la lista alineada, `revisar` sigue calculando el esperado del
mensaje, así que los **imposibles** (valor_imposible_aceptado) y los avisos de estructura salen aunque falte el canónico: es lo que
devuelve al caso de `oru_fhir` su `fallo_silencioso`.

**«Ninguna sesión trae canónico», que hoy es fuera de alcance, sobrevive solo cuando ningún mensaje lo exige:** evidencia sin sesiones,
AA sin log (L5, `info_verificador.json:365`), rechazos, evidencia de solo acuse. Para distinguir **solo acuse** (L-MT1) no hace falta
mirar el log: los PE sin mapeador nunca entran; y L13 («aceptado sin destino») no está en el conjunto de éxito, así que ni siquiera un
PE con mapeador que lo emitiera exigiría canónico.

**Circuito frente a lector.** Si el lector no pudo leer el canónico (SQL o API caídos), lo declara en `almacen_adt.fallos` con
`paso = "canonico"` (`esquema_evidencia.json:271-277`: `paso` es texto libre) → `lectura_hallazgos` → `indeterminado/lectura`, que manda
sobre todo (`verificador.py:329`, `:532-534`). Sin esa declaración, la ausencia es del circuito. En `adt_a01` el lector del congelado no
tiene ese canal: L-VE-4.

### 1.3 Dónde se cambia (todo bajo `verificador.py`; los mapeadores no se tocan)

1. `_mapeador(e, ms, lec, revisar, clave)` recibe además `obs` (ya calculado antes, `:262`). Calcula
   `exigidos = {k : obs[k] AA y por_mensaje[k].destino == "exito" y canon[k] is None}`. Si no hay ningún diccionario **y** `exigidos` está
   vacío → `canon = []` como hoy (`:160-161`). Si no, pasa la lista alineada tal cual (con `None`). La ruta DV-V3/DV-V4 (`:167-184`) no
   cambia: con `canon` no vacío sigue funcionando igual.
2. En el manejador de «no hay canónico» (`:291-299`): si `obs[k]` no es AA → se descarta la línea; si `destino == "exito"` →
   `fidelidad/sin_canonico` (como hoy); si no → `nota/sin_canonico` que no cuenta, texto «AA sin fila de éxito: el canónico no se exige (L5)».
   Las ramas `trama` y `acuse/recuento` (`:292-297`) se conservan delante.
3. MCP `_no_evaluado` (`verificador/mcp_verificador.py:1171-1172`): «fidelidad: sin canónico no se evalúa lo guardado; con AA y fila de
   éxito su ausencia cuenta (S-VE-1)».

### 1.4 Pruebas

| P | Dónde | Evidencia | Hoy | Después |
|---|---|---|---|---|
| P-VE-1 (el hueco) | `verificador/prueba_adt.py`, tras `:126-127` | `msg()`, ACK AA, L16, `almacen_sintetico`, **sin** `canonico_adt` | `correcto` (E-VE-3) | `fallo_silencioso`, `cuenta` = `[("fidelidad","sin_canonico","existencia")]` |
| P-VE-2 (adt_a01) | `prueba_verificador.py` (forma de `ev(...)`, `:33`) | `ev(log=[L01], canon=None)` (ACK AA por omisión) | `correcto` | `fallo_silencioso` con `sin_canonico` |
| P-VE-3 (oru_fhir) | `prueba_oru` (fuera de la carpeta; misma forma) | AA + L15 + sin `canonico_oru` + OBX-5 `1,5` con OBX-2 NM | `correcto` | `fallo_silencioso`: `valor_imposible_aceptado` OBX-5 **y** `sin_canonico` |
| P-VE-4 (lector) | `prueba_adt.py` | como P-VE-1 más `almacen_adt.fallos = [{"paso": "canonico", …}]` | `correcto` | `indeterminado/lectura` |
| Controles que no cambian | `prueba_adt.py` | AA + L16 + canónico → `correcto`; AR 201 + L04 sin canónico → `correcto`; lote [AA+L01+canónico, AR+L03 sin canónico] → `correcto` (L24); AA sin log sin canónico → la categoría de hoy (`prueba_verificador.py:628`, `:896-913` siguen igual) | | igual |

### 1.5 Previsión de M12 por corpus

| Corpus | Cambios previstos | Por qué |
|---|---|---|
| Regresión 2.721 (`adt_a01`) | **0** en veredicto y en hallazgos que cuentan | E-VE-1: 0 AA con fila de éxito sin canónico (`RESULTADO-VE-PRE.md:56-58`); las 1.847 `correcto` siguen |
| A1 263 × 2 perfiles (`adt_fhir`) | 0 | evidencia exacta con canónico |
| Casos de los agentes (9 `oru_fhir` + 14) | 0 | traen canónico; el que cambiaba al quitárselo conserva su categoría |
| `mirth/mi2_*.json` | 0 | 263 + 263 `correcto` con canónico |
| `mirth/mi3.json` | MMI-12: 128 mordidos → **128 cazados** (`fallo_silencioso`, reproducido con el constructor de `prueba_adt`, como E-VE-3) | es el cambio buscado |
| Clase no censada: lotes con un mensaje AA **sin fila de éxito** y sin canónico junto a otro con canónico (hoy `fidelidad/sin_canonico`, después `nota`) | **n = lo que cuente E-VE1-1**, esperado 0 | VE-pre censó solo «AA y fila de éxito» |

---

## 2. MMI-19 (Q-MI-V-10, L-MI-14): releer el almacén también por el paciente

### 2.1 El mecanismo, con cita

- Los dos lectores releen **solo** por el `Identifier` y el `VisitaId` del canónico observado (`lectores/labadt_adt.py:480-488`,
  `lectores/mirth_lector.py:118-138`); sin canónico, el de IRIS no lee (`labadt_adt.py:552`, `almacen_adt = None`) y el de Mirth devuelve
  listas vacías (`mirth_lector.py:121-122`). Es un **acoplamiento con MMI-12**: un circuito sin canónico también se queda sin almacén.
- El juez ya sabe juzgar un Encounter de más: toda entrada leída con n ≥ 1 que el mensaje no pedía es `fidelidad/almacen` hecho `PV1-2`
  (`verificador/almacen_adt.py:182-192`, S77 `info_verificador.json:116`); `prueba_adt.py:148-152` lo prueba. Lo que no llega es la lectura.
- Un Encounter escrito sin PV1-19 va por POST sin identifier (S78 `info_verificador.json:117`, L-ADT-19 `:424`, L-MI-2
  `resultados/diseno-mirth-fable.md:723`): **no se puede encontrar por identifier** aunque se quiera. Por eso «releer por los identificadores
  del mensaje» (Q-MI-V-10) resuelve 3 de 13 y hace falta el paciente para los otros 10 (`RESULTADO-VE-PRE.md:45-50`).

### 2.2 Qué dice el estándar de la búsqueda

| Parámetro de Encounter (R4) | Expresión | Sirve |
|---|---|---|
| `identifier` (token) | `Encounter.identifier` (`estandar/fhir_r4_encounter_search.json:9-11`) | para el VisitaId; no para un Encounter sin identifier |
| `patient` (reference) | `Encounter.subject.where(resolve() is Patient)` (`:15-17`) | **no**: con S80 el `subject` es `{"identifier": …}` sin `reference` (`mapeador_adt.py:730`), y `resolve()` no tiene qué resolver |
| `subject` (reference) | `Encounter.subject` (`:135-138`) | **sí, con el modificador `:identifier`**, que R4 define para un parámetro de referencia como coincidencia sobre `Reference.identifier` (search.html, tipo reference; el texto no está en la carpeta: L-VE-5, se mide en E-VE1-2) |

Consulta: `GET [base]/Encounter?subject:identifier=urn:lab:integraciones:mrn|<Identifier>`, con el valor escapado como ya hacen los lectores
(`mirth_lector.py:57`, `labadt_adt.py:450`), **filtro exacto en cliente** sobre `subject.identifier.system|value` (trampa de la barra
invertida: el servidor puede devolver de más; el filtro no) y paginación por `link next` (`labadt_adt.py:453-462`).

Escalera de vuelta atrás, medida en E-VE1-2 antes de escribir el lector:
1. `subject:identifier` (preferida).
2. `Encounter?_lastUpdated=ge<t0>` (parámetro común de R4; `t0` = instante anterior al envío, en el reloj del servidor, leído de un recurso
   recién escrito) + filtro exacto en cliente por `subject.identifier`.
3. Barrido `Encounter?_count=…` con filtro en cliente (el almacén del laboratorio es pequeño; coste conocido).
4. Si ninguna sirve → la parte del lector de MMI-19 pasa a **L-VE-3** y se queda la parte del juez (inocua sin la clave).

### 2.3 Contrato del lector (R-VE-2), para los dos lectores

Entradas: el cable, el canónico observado (puede faltar), MSA-1, y el **censo previo** tomado antes de enviar. El lector **no depende del
canónico para leer**.

| Entrada de `almacen_adt` | Por qué identificador | Consulta | Nota |
|---|---|---|---|
| `pacientes[]` | {`Identifier` esperado} ∪ {`Identifier` del canónico observado, si no vacío} | `Patient?identifier=mrn\|v` exacto | el esperado sale de la regla MR del propio juez (`mapeador_adt.esperado_mensaje`, `mapeador_adt.py:585`, recortado al LEN del PE `:567`), como ya hace `labadt_adt._ids_esperados` (`:885-895`) |
| `visitas[]` | {`VisitaId` esperado si `TieneVisita`} ∪ {PV1-19.1 del mensaje, desescapado y recortado, **aunque `TieneVisita` = 0**} ∪ {`VisitaId` observado} | `Encounter?identifier=visit\|v` exacto | cubre los 3 de 13 con PV1-19 y PV1-2 = N: el juez ya lo juzga (`almacen_adt.py:182-192`) |
| `visitas_por_paciente[]` (**nuevo**) | cada `v` de `pacientes` | `Encounter?subject:identifier=mrn\|v` (§2.2) | `{identificador: v, n, recursos: [{id, crudo}], previos: [ids]}`; `previos` = ids de los Encounter del mismo paciente que el **censo previo** (misma consulta, tras la limpieza y antes de enviar) ya encontró |
| `fallos[]` | | | `paso` ∈ {`busqueda`, `get`, `paciente`, `censo`, `canonico`} |

- **Limpieza previa** (`mirth_lector.limpiar` `:110-115`; `labadt_adt._borrar_por_id` `:491-501`): además de por identifier, borra los
  Encounter del paciente por `subject:identifier` (primero los Encounter, luego los Patient; cada uno releído por id y confirmado antes de
  borrar, nunca por búsqueda). Lo que quede después (secuencias, otro lote) es `previos`.
- **Una sola lectura tras el ACK** (L-ADT-9 `info_verificador.json:416`); el censo y la limpieza son contabilidad del lector, como hoy la
  limpieza, y no entran en la evidencia salvo por la lista `previos`.
- **Tras un rechazo** también se lee, por los identificadores del mensaje (S68 `info_verificador.json:107`): `almacen_adt` deja de ser `null`
  cuando el lector corrió, también en AR 200/201 (hoy `labadt_adt.py:552` devuelve `None` sin canónico).
- `almacen_adt.leido = "tras_ack"` y `ack_msa1` como hoy. El lector de Mirth cambia de firma (`almacen(texto, canon, msa1, censo)`); el de
  IRIS, `almacen_adt_de(texto, canon, msa1, censo)` y `_leer_sesion` (`labadt_adt.py:546-556`), que ya tiene el cable.
- Esquema (`esquema_evidencia.json:305-311` y el `ALMACEN_ADT` del MCP, `mcp_verificador.py:1056`): `visitas_por_paciente` (array ≤ 20;
  items `{identificador ≤ 128, n entero, recursos ≤ 20 de {id ≤ 64, crudo ≤ 64000}, previos: array ≤ 50 de cadenas ≤ 64}`); `maxProperties 8`
  sigue bastando (6 claves). Descripción: «por los identificadores del mensaje y del canónico observado, y los Encounter del paciente».

### 2.4 Cómo se juzga un Encounter encontrado por el paciente (R-VE-3, en `almacen_adt.comparar`, `:153-199`)

`nuevos` = recursos de `visitas_por_paciente` cuyo id **no** está en `previos` ni entre los ids ya juzgados por `visitas` (el Encounter
esperado aparece por las dos vías: se cuenta una vez).

| Caso | Hallazgo por cada `nuevo` | Cita |
|---|---|---|
| AA, `TieneVisita` = 0 (PV1-2 = N) | `fidelidad/almacen`, hecho `PV1-2`, causa `escritura`: «ALM Encounter id=<id> del paciente <v> que el mensaje no pedía (PV1-2 = N: sin visita, S77)» | S77; mismo hecho que `almacen_adt.py:189-192` y que la previsión de MMI-19/MA10 (`diseno-mirth-fable.md:676`) |
| AA, `TieneVisita` = 1, `VisitaId` ≠ "" | `fidelidad/almacen`, hecho `PV1-19`, causa `escritura`: «ALM Encounter id=<id> del paciente <v> sin el identifier visit\|<VisitaId> esperado» (el `ausente` por VisitaId, hecho `PV1`, sigue saliendo si n = 0) | `almacen_adt.HECHO` identifier → PV1-19 (`:36`) |
| AA, `TieneVisita` = 1, `VisitaId` = "" (S78) | 0 nuevos → `fidelidad/ausente` hecho `PV1` («esperado 1 Encounter del paciente, sin identifier»); 1 nuevo → **se compara su contenido** con `proyectar(esperado)["Encounter"]` por `_entrada` (`:118-150`; el identifier esperado ya es `None` sin VisitaId, `mapeador_adt.py:726-727`); > 1 → `fidelidad/duplicado` hecho `PV1` y se compara el primero (DV-ORU11-1) | cierra L-ADT-19 para la evidencia nueva; Q-VE-D-4 |
| AE/AR | `acuse/rechazo_con_escritura`, hecho `destino` | S68, como `:193-194` |
| `previos` no vacío | `nota/almacen_previos` (no cuenta): «k Encounter(s) del paciente anteriores al envío: no se juzgan (L-ADT-12)» | L-ADT-12 `info_verificador.json:418`; Q-VE-D-6 |
| Sin `visitas_por_paciente` (evidencia anterior) y (`TieneVisita` = 0 o `VisitaId` = "") | `nota/almacen_no_leido` hecho `PV1`: «sin relectura por paciente: un Encounter sin identifier no se vería (L-VE-3)» | solo donde importa, para no ensuciar el rejuicio |

`escrito` es verdadero si hay algún `nuevo` (alimenta `escritura` en el veredicto, `verificador.py:543`). `resumen` gana `EncounterPaciente`
(nuevos por entrada) y `previos`; la línea de la ficha (`verificador.py:627`) pasa a `ALMACÉN leído tras ACK: Patient n=[1] Encounter n=[1]
por paciente nuevos=[0] previos=[0]; fallos 0`. `almacen_sintetico` (`:217-233`) añade `visitas_por_paciente` con el mismo Encounter (mismo
id) y `previos = []`, así la evidencia exacta sigue `correcto`. La nota L-ADT-19 de `:169-171` desaparece cuando hay `visitas_por_paciente`.

### 2.5 Pruebas

| P | Dónde | Evidencia | Hoy | Después |
|---|---|---|---|---|
| P-VE-5 (MMI-19) | `almacen_adt.autoprueba` y `prueba_adt.py` | A31 con PV1-2 = N y PV1-19 vacío (`eN`), almacén exacto + `visitas_por_paciente: [{X1, n 1, recursos [{id "9", crudo Encounter{status in-progress, subject{identifier mrn\|X1}}}], previos []}]` | `correcto` (clave ignorada) | `fallo_silencioso`, `[("fidelidad","almacen","PV1-2")]` |
| P-VE-6 (previos) | ídem | lo mismo con `previos: ["9"]` | `correcto` | `correcto` + nota `almacen_previos` |
| P-VE-7 (dedupe) | ídem | A01 con V1: el mismo id en `visitas` y en `visitas_por_paciente` | `correcto` | `correcto`, sin hallazgo nuevo |
| P-VE-8 (S78) | ídem | A01 con PV1-19 vacío (`e78`): 1 nuevo = proyección → `correcto` sin nota L-ADT-19; con `status` cambiado → `fidelidad/almacen PV1-2`; 0 nuevos → `fidelidad/ausente PV1`; 2 → `duplicado` | nota L-ADT-19 (`:286`) | lo indicado |
| P-VE-9 (S68) | ídem | AE + 1 nuevo | sin hallazgo | `acuse/rechazo_con_escritura` |
| P-VE-10 (lector, en vivo, sin circuito) | VE1, FHIR a mano con la credencial del laboratorio | POST de un Encounter sin identifier con `subject.identifier = mrn\|X`; `almacen_adt_de` / `almacen` para un canónico sintético con `TieneVisita` = 0 | — | `visitas_por_paciente[0].n == 1`, `previos == []`; con censo previo, `previos == [id]`; borrado por id al final. Es el control negativo del aparato antes de usarlo |
| P-VE-11 (lector de Mirth, unidad) | `mirth_lector` | `almacen(texto, None, "AR", censo)` | listas vacías | lee por los identificadores del mensaje (n = 0 esperado) |

### 2.6 Previsión de M19 por corpus

Los corpus guardados **no traen** `visitas_por_paciente`: por construcción M19 da **0** cambios en veredicto y en hallazgos que cuentan en
todos ellos. Cambios menores (notas): `almacen_no_leido (L-VE-3)` en la evidencia `adt_fhir` con PV1-2 = N o PV1-19 vacío; **n = lo que cuente
E-VE1-3** (A1 263 × 2, agentes). En vivo: el piloto A3 repetido con el lector nuevo (`labadt_adt.sondas_a3`, `:613-626`) → 10/10 `correcto`
(S7, A31 N tras S1-S6 sobre el mismo paciente: el Encounter V1 es `previo`); P-VE-10 → cazado. `mirth/mi3.json` MMI-19: 14 → cazados por
reproducción sintética (la salida del mutante = Encounter por paciente), salvo que Q-VE-A-1 decida medirlo en vivo.

---

## 3. Q-MS-9 (VER-MS-1): una sola versión para el acuse y el mapeador

### 3.1 La incoherencia, con cita

- El acuse, con MSH-12 vacío y perfil del sitio, asume la versión por omisión (`acuse_referencia.py:502-505`) y **la usa también para S22**
  (`:645-652`: `ver = version_msh12.texto`, `posterior = MR.posterior_a_25(ver)`, tolerancia S22 y alternativa AE 103 por S26).
- Los mapeadores usan la **escrita**: `mapeador_referencia.py:480`, `mapeador_adt.py:458`, `:534`, `:546`, `:574`, `:659`. Con MSH-12 vacío,
  `posterior_a_25("")` es falso (`mapeador_referencia.py:75-78`) y PID-8 fuera de la 0001 es «valor imposible aceptado».
- Con AA el circuito no puede acertar (`RESULTADO-MS2.md:50-56`, `:82-84`); hoy se salva porque los circuitos contestan AE 103 (S103 aplicada
  en los circuitos) y S26 lo acepta como alternativa (`acuse_referencia.py:649-652`).

### 3.2 La decisión (S-VE-2): la versión escrita manda en S22

- **Estándar.** MSH-12 es R (`hl7v25_CH02.txt:4360`) y «is matched by the receiving system to its own version to be sure the message will
  be interpreted correctly» (`:4512-4513`); §2.9.2.1 b lo lee el respondedor para aceptar (`:1442`). Asumir una versión cuando falta es una
  decisión del sitio (H4) para no rechazar tráfico real: decide la aceptación. S22 tolera un código fuera de la tabla de v2.5 porque «puede
  ser legal en su versión» (`info_verificador.json:61`; L18 `:378`): sin versión escrita no hay versión en la que serlo, y se aplican las
  tablas de v2.5 (L17 `:377`) → 103 (`hl7v25_CH02.txt:3992` es el 203 de versión; el 103 es «Table value not found»). S26 (`:65`) es una
  alternativa **de S22**: si S22 no aplica, S26 tampoco.
- **S-n.** S103 ya lo dice con 0,98 (`info_verificador.json:142`): «la versión asumida por omisión SOLO decide la aceptación; S22 sigue a la
  versión escrita». Solo faltaba aplicarla al acuse. Jev confirma S-VE-2 como la S-n que cierra Q-MS-9 (Q-VE-D-3).
- **Cambio:** `acuse_referencia.py:645`: `ver` = la versión **escrita** (`""` si `version_msh12.por_omision`). Nada más: los mapeadores ya
  leen la escrita; el motivo de S26 (`:906-909`) solo se construye cuando S26 aplica. El perfil del sitio y H4 no cambian.
- **Efecto**, perfil del sitio, MSH-12 vacío, PID-8 ∉ 0001: esperado **AE 103** (P5 consumido, `puntos_entrada.py:137`), sin alternativa.
  AA → `contenido/aceptado_imposible` del acuse (`verificador.py:370-371`) + `valor_imposible_aceptado` del mapeador (`:280`, `:287-288`),
  fusionados por (mensaje, PID-8) → `fallo_silencioso/aceptado_imposible`. AE 103 → `correcto` sin tolerancia. Lo mismo mueve PV1-2 ∉ 0004
  (salvo el vacío tolerado, S95), PID-30 ∉ 0136 (consumidos) y EVN-1/MSH-18 (estrictos, no cuentan). Perfil lab: sin cambio (MSH-12 vacío es
  AR 101, `acuse_referencia.py:506-507`). Versión escrita > 2.5: sin cambio (S22 y S26 como hoy).

### 3.3 Pruebas

| P | Dónde | Evidencia | Hoy | Después |
|---|---|---|---|---|
| P-VE-12 (acuse) | `acuse_referencia` autoprueba, con un perfil mínimo en memoria `PERFILES["_ve"] = {"msh12_por_omision": "2.6", "regla_msh12": "H4"}` (los demás mandos `None`, `:63-65`) si el perfil del sitio no está cargado (patrón de `prueba_adt.py:91-99`) | MSH-12 vacío, PID-8 = V | `("AA", None)`, tolerancia `[S22]`, alternativa S26 | `("AE", "103", "PID-8")`, `alternativas_aceptadas == []` |
| P-VE-12b (controles) | ídem | MSH-12 = 2.6 escrito + PID-8 = V → como hoy (AA + S22 + S26); perfil lab + MSH-12 vacío → AR 101 | | igual |
| P-VE-13 (verificar) | `prueba_adt.py` | perfil `_ve`, MSH-12 vacío, PID-8 = V, ACK AA, L16, canónico esperado (Gender `None`) | `fallo_silencioso` con el mapeador solo | `fallo_silencioso/aceptado_imposible` con **un** hallazgo fusionado origen `acuse+mapeador`; con ACK AE 103 → `correcto` y **sin** tolerancia S26 |

### 3.4 Previsión de MS9 por corpus

| Corpus | Cambios previstos | Por qué |
|---|---|---|
| Perfil lab (todos) | **0** | no hay versión asumida |
| Perfil del sitio, MSH-12 vacío, PID-8 ∉ 0001 | **≤ 39** mensajes (`RESULTADO-VE-PRE.md:70-85`): `esperado.msa1_aplicacion` AA → AE 103 sobre PID-8 | el mecanismo exacto |
| · con evidencia **exacta** generada por el juez (previsiones sintéticas, A4/MS1) | la evidencia exacta cambia con el juez (AE 103 y nada escrito): `fallo_silencioso` → `correcto` | |
| · con evidencia **viva** sellada (MS2 LABADT sitio 597/597, Mirth sitio 263/263: el circuito contestó AE 103) | veredicto **igual** (`correcto`); desaparece la tolerancia `alternativa_S26` (cambio menor) | |
| PV1-2 ∉ 0004 / PID-30 ∉ 0136 con MSH-12 vacío en el sitio | **n = lo que cuente E-VE1-4**, esperado 0 (Q-MS-10: ningún mensaje real trae la clase propia, `info_verificador.json:435`) | VE-pre censó solo PID-8 |
| Seco de los tres circuitos (`comun/seco_ms.py`) | SIN EXPLICAR 0 se mantiene: los AE 103 de los circuitos pasan de «explicados por alternativa» a esperado principal; `clasificar_seco` pierde la clase VER-MS-1 (declarado) | |

---

## 4. Q-MI-V-9: la representación del canónico ADT en el contrato público

### 4.1 Qué falta

`contratos/contrato_canonico_adt.md:1-4` solo da nombres y tipos. Lo que un circuito ajeno no puede saber y el juez compara literalmente
(`mapeador_adt.comparar`, `:778-805`; `_igual`, `:771-775`):

| Punto (DV-MI) | Representación que lee el juez | Cita |
|---|---|---|
| DV-MI-2 `Uso`/`Sistema`/`Tipo` de las hijas | **códigos FHIR ya mapeados**: `nombres[].Uso` por la 0200 → name-use (`mapeador_adt.py:605-609`); `direcciones[].Uso/Tipo` = `address.use/type` (`:612-616`); `telecoms[].Uso/Sistema` = `ContactPoint.use/system` (`:617-624`) | `RESULTADO-MIRTH.md:109` |
| DV-MI-3 `GivenName` | XPN.2 y XPN.3 de la repetición elegida (S74) unidos por un espacio (`MR.nombre`, `:581`; `resultados/diseno-adt-fable.md:119`); en las hijas, `Given` = XPN.2 entero y `Otros` = XPN.3 (S96 `info_verificador.json:135`) | `RESULTADO-MIRTH.md:110` |
| DV-MI-4 sin visita (PV1-2 = N) | `TieneVisita` = 0 y **todos** los campos de visita `""` (`:626`, `:642-650`), incluidos `ClaseCode/ClaseSystem/Estado` (no el mapeo de la 0004 para N) | `RESULTADO-MIRTH.md:111` |
| Vacíos y enteros | vacío = `""` (nunca `null`) en el esperado; el observado puede traer `None` y se normaliza (`canonico_texto`, `:672-678`); enteros `ENTEROS` (`:501-502`) | |
| Los demás | `Gender` código AdministrativeGender; `BirthDate` ISO con la precisión del TS; `Inicio/Fin/DeceasedDateTime` dateTime FHIR con zona (S66); `ClaseCode/ClaseSystem` por la 0004 → v3-ActCode o v2-0004; `Estado` encounter-status; `MaritalCode/System` por la 0002; `Ubicacion` = `PL.1^PL.2^PL.3^PL.4.1`; `IdentifierTipo`/`VisitaIdTipo` CX.5 crudos; `MsgEvent`, `ProcessingId`, `VersionId` MSH-12.1 **escritos** (DV-MI-6/7, `RESULTADO-MIRTH.md:113-114`); `Truncado` por repetición (S3) | `diseno-adt-fable.md:111-139` |

### 4.2 Dónde (S-VE-4)

1. **Fuente única en el código:** `mapeador_adt.CONTRATO_CANONICO`, una tupla por campo `(nombre, origen HL7, tipo, regla de valor, cita)`,
   junto a `CAMPOS_CABECERA`/`HIJAS` (`mapeador_adt.py:487-502`); la autoprueba afirma que cubre exactamente `CAMPOS_CABECERA + AUX_CABECERA`
   y las cuatro hijas (un campo sin fila, o una fila sin campo, es MAL).
2. **MCP:** `consultar_tabla("canonico_adt")` devuelve esas filas (patrón de `proyeccion_fhir_adt`, `mcp_verificador.py:1704-1706`); la
   descripción de `canonico_adt` en el esquema (`esquema_evidencia.json:303`) remite a la tabla.
3. **Documento público:** `contratos/contrato_canonico_adt.md` se **genera** desde (1) (`contratos/generar_contrato.py`) con una columna
   «Valor» y otra «Cita»; la guarda de publicación comprueba que el fichero es igual a la generación (el contrato no puede divergir del juez).
   Alternativa (Q-VE-A-4): editar el `.md` a mano.
4. La tabla hace explícitas las tres DV-MI donde el diseño ciego de Mirth difirió (`diseno-mirth-fable.md:287-330` frente a 4.1).

No cambia ningún veredicto (previsión CT: 0). Q-VE-D-5 pregunta si la representación debe quedarse mapeada (recomendado) o pasar a cruda.

---

## 5. Lo que queda fuera: límites L-VE (Q-VE-1 y Q-VE-2)

| L | Redacción para `info_verificador.limites` |
|---|---|
| **L-VE-1** (C, neutralidad de motor) | «El vocabulario del log (L01-L16) y los textos de L03/L04 son los del motor de referencia; con otro motor el lector los **sintetiza** desde datos estructurados (Mirth: S-MI-5), y el juez no distingue traducción de observación (Q-MI-V-1, Q-MI-V-4). L08 y L10 no existen fuera del motor de referencia y «hubo conexión y expiró» se expresa como L07 (Q-MI-V-2); L09 no es observable (Q-MI-V-3, L-MT11); L21 vale por ventana de una petición aunque el motor no reintente (Q-MI-V-8). No se acepta una fila estructurada como terminal ni se adjunta el log nativo en la evidencia. Hasta el siguiente motor.» |
| **L-VE-2** (D, interpretación) | «Quedan sin decidir, con la lectura de hoy y sin caso real ni mutante que lo pida: el `OperationOutcome` de un 400/422 no se interpreta frente a ERR-3 aunque viaje en la evidencia (Q-MI-V-6; L3, L22); MSA-2 íntegro o recortado a 199 son ambos aceptables (Q-MI-V-7; AMB-7, L-MS-3); un HTTP fuera de la tabla de P7 es 2xx éxito y el resto AR 207 (Q-DV1); un juego de MSH-18 que no es latin-1, UTF-8 ni ASCII se lee como latin-1 (Q-AMB-10; S9, L11); la tabla 0004 ampliada del sitio no se juzga (Q-MS-10; L-MS-12).» Estas cinco van en `preguntas_pendientes` (Q-VE-A-2); Q-MS-9 sale de ahí. |
| **L-VE-3** | «La relectura por paciente solo existe en la evidencia que trae `almacen_adt.visitas_por_paciente`; en la anterior, un Encounter escrito sin identifier no se ve (L-ADT-19, L-MI-14 siguen para ella). Si el servidor FHIR no admite `subject:identifier` ni `_lastUpdated`, el límite es total y MMI-19 queda declarado.» |
| **L-VE-4** | «En `adt_a01` el lector no distingue «el circuito no registró el canónico» de «el lector no pudo leerlo»: sin canal de fallos, la ausencia con AA y fila de éxito se atribuye al circuito (S-VE-1).» |
| **L-VE-5** | «El texto de FHIR R4 sobre el modificador `:identifier` de los parámetros de referencia no está en la evidencia de diseño; se cita por sección y se mide (E-VE1-2).» |
| **L-VE-6** | «Un AA sin fila terminal de éxito y sin canónico no es fallo: no hay prueba de que el destino se alcanzara (L5); el canónico se exige solo cuando el circuito declara haber escrito.» |
| **L-VE-7** | «MMI-12, MMI-19 y los 15 mutantes cazados de MI3 no se vuelven a medir en vivo sobre el otro motor (salvo Q-VE-A-1): la caza se reproduce con evidencia sintética y la ausencia de colateral se argumenta por construcción (las reglas nuevas solo disparan sin canónico o con un Encounter de más por paciente).» |

---

## 6. El rejuicio (Q-VE-3): medir «qué cambiaría» sin reescribir lo sellado

### 6.1 Niveles de diferencia y mecanismos

| Nivel | Qué compara | Se adjudica |
|---|---|---|
| **N3** | `veredicto.categoria` + `subtipo` | siempre |
| **N2** | el conjunto de hallazgos que cuentan: (`clase`, `subtipo`, `hecho`) por mensaje | siempre |
| **N1** | notas, tolerancias, `esperado.msa1_aplicacion`/`alternativas_aceptadas`, `resumen` del almacén, textos | por firma de mecanismo, en bloque |

Cada diferencia N1-N3 se atribuye por **firma** a un mecanismo: **M12** (aparece `fidelidad/sin_canonico` o `nota/sin_canonico`); **M19**
(hallazgo o nota nacidos de `visitas_por_paciente` / `almacen_no_leido (L-VE-3)`); **MS9** (`esperado.msa1_aplicacion` AA → AE 103 sobre
PID-8/PV1-2/PID-30 con MSH-12 vacío y perfil del sitio, o tolerancia `alternativa_S26` desaparecida); **CT** (ninguna: documentación).

**Fuera de previsto** = cualquier N3 o N2 cuyo (corpus, mecanismo, sentido) no esté en la previsión o supere su cota; cualquier N1 sin firma
de mecanismo; cualquier diferencia en un corpus con 0 previsto; cualquier suite en rojo no declarada. Un «dentro de previsto» con un
recuento **menor** que la cota es correcto; **mayor**, fuera.

### 6.2 Línea base y herramienta

- **Línea base:** `privado/ve/linea_base` (`RESULTADO-VE-PRE.md:9-24`): la foto de la regresión (2.721 instancias, sha `99ac11be…`), las
  suites con sus huellas (`suites.sha256`), la concordancia de A1 (8.039 hojas / 6.255 iguales; JSON idéntico al de git) y el seco de los
  tres circuitos con SIN EXPLICAR 0. Juez viejo = huella `73d36c38…` (`info_verificador.json:5`), commit `info_verificador.json:4`.
- **Herramienta `ve/rejuicio.py`:** para cada corpus, juzga cada caso con el juez viejo (un `git worktree` del commit de la línea base, solo
  lectura, importado bajo otro nombre) y con el nuevo (árbol de trabajo), en el perfil con que se midió; diff N1/N2/N3; firma; tabla por
  corpus: n, N3 por (viejo → nuevo, mecanismo), N2, N1, fuera de previsto. Para la regresión, `regresion_perfil.py comparar` contra la foto
  (sus motivos son N3/N2) y la tabla se rellena con sus motivos. La concordancia de A1 no debe moverse (el mapeador no se toca; solo
  importa `mapeador_adt.CONTRATO_CANONICO`, que no entra en `fhir()`). El seco: SIN EXPLICAR 0 con el clasificador sin VER-MS-1.
- **Corpus y perfil:** regresión 2.721 (su perfil); A1 263 en lab y en el perfil del sitio (evidencia exacta regenerada con cada juez:
  la previsión declara que «exacta» cambia con MS9); `mirth/mi2_lab.json`, `mirth/mi2_prevision.json` (sus perfiles); `mirth/mi3.json` y
  `mirth/mi3_vivo.json` (resumen: se reproducen MMI-12 y MMI-19 con evidencia sintética, los 15 cazados por construcción, L-VE-7); la muestra
  real (`privado/`, los dos perfiles; nunca se publica); los 23 casos de los agentes.
- **La previsión se escribe y se sella (huella) antes de ejecutar nada**, con los recuentos de E-VE1-1/3/4 ya dentro.

### 6.3 Previsión consolidada (lo que VE2 debe encontrar)

| Corpus | N3 | N2 | N1 (por mecanismo) |
|---|---|---|---|
| Regresión 2.721 | 0 | 0 (+ E-VE1-1 si > 0, M12) | 0 |
| A1 263 lab | 0 | 0 | M19: notas L-VE-3 en los casos con PV1-2 = N o PV1-19 vacío (E-VE1-3) |
| A1 263 sitio (evidencia exacta) | MS9 ≤ los de A1 con MSH-12 vacío (VE-pre: los 8 de A1 con S22 tienen versión escrita > 2.5 → **0**) | 0 | como lab |
| `mi2_lab` / `mi2_prevision` | 0 | 0 | MS9: `alternativa_S26` desaparece en los casos del sitio con MSH-12 vacío y PID-8 ∉ 0001; M19 notas |
| `mi3` / `mi3_vivo` | MMI-12 128 → cazados; MMI-19 14 → cazados (sintético) | ídem | — |
| Muestra real, sitio | MS9 ≤ 3 solo si la evidencia es exacta; con la viva sellada (AE 103) 0 | 0 | MS9: 3 tolerancias S26 fuera |
| Muestra real, lab | 0 | 0 | 0 |
| Agentes (23) | 0 | 0 | M19 notas |

### 6.4 Cómo se llama la versión nueva y cómo la declara el MCP

- La identidad sigue siendo la **huella** (`mcp_verificador.py:74-94`; `FICHEROS` `:62-65` no cambia de lista; `serverInfo.version =
  huella[:12]`, `:1868`, `:1899`). Se añade a `VERSION`: `"servidor": "1.1"` (`:57`, hoy `"1.0"`) y `"revision": "etapa del verificador:
  S-VE-1..3, L-VE-1..7"`; `info_verificador.json` se regenera con la huella nueva (Q-VE-A-3).
- `info_verificador` declara: las S-n nuevas (las que Jev fije para S-VE-1..3), DV-VE-n, L-VE-1..7, `preguntas_pendientes` = las cinco de
  L-VE-2, y en `limites` la reescritura de L-ADT-19/L-MI-14 («cerrados para la evidencia con `visitas_por_paciente`»). Las pruebas del MCP
  que fijan la lista de pendientes o un texto de `_no_evaluado` se actualizan y se declaran (como P29 en MS4, `RESULTADO-MODO-SITIO.md:40-41`).
- Cada RESULTADO sellado **no se edita**; `RESULTADO-ETAPA-VERIFICADOR.md` lleva, por corpus, la línea «juzgado con `73d36c38…`; con
  `<huella nueva>` cambiarían N3 a, N2 b, N1 c (mecanismos)», y las dos huellas.

---

## 7. Plan VE1-VE3, con «hecho cuando», parada y tope

Tope total de la etapa: dos sesiones; VE-pre ya gastó parte. Reparto propuesto del resto: **VE1 ≈ 0,75 sesión, VE2 ≈ 0,5, VE3 ≈ 0,25**.
Dentro de VE1 va primero lo que puede tumbarlo (memoria «probar primero el eslabón débil»).

| Fase | Qué, en orden | Hecho cuando | Parada |
|---|---|---|---|
| **VE1-a** sondas (solo lectura y FHIR a mano; ≤ 45 min) | **E-VE1-2:** `Encounter?subject:identifier=mrn\|X` sobre un Encounter sembrado con subject lógico; si falla, `_lastUpdated`; si falla, barrido. **E-VE1-1:** censo en la regresión, A1 y agentes de lotes con un mensaje AA sin fila de éxito y sin canónico junto a otro con canónico. **E-VE1-3:** recuento de evidencia `adt_fhir` con PV1-2 = N o PV1-19 vacío. **E-VE1-4:** en los corpus del sitio con MSH-12 vacío, PV1-2 ∉ 0004 y PID-30 ∉ 0136 | las cuatro contestadas y copiadas a la previsión (§6.3) | E-VE1-2 sin ninguna vía → la parte del lector de MMI-19 pasa a L-VE-3 antes de escribir código |
| **VE1-b** pruebas antes del código | P-VE-1..9, P-VE-12/13 escritas y **en rojo** con el juez de hoy; los controles en verde | cada prueba nueva falla por la razón prevista (no por un error de la prueba) | una prueba que no se puede poner en rojo = el hueco no está reproducido: no se hace ese cambio |
| **VE1-c** código, de menor a mayor | MS9 (`acuse_referencia.py:645`) → M12 (`verificador._mapeador` y el manejador) → M19 juez (`almacen_adt`, esquema, MCP, ficha, `almacen_sintetico`) → M19 lectores (IRIS y Mirth: identificadores del mensaje, `subject:identifier`, limpieza y censo por paciente) → CT (`CONTRATO_CANONICO`, `consultar_tabla`, generador del `.md`) | todas las pruebas nuevas en verde; `prueba_verificador`, `prueba_adt`, `prueba_oru`, `prueba_multitipo`, `prueba_mutantes`, `prueba_arnes`, autopruebas y `prueba_mcp_verificador` en verde salvo las cambiadas a propósito, cada una declarada | cualquier rojo no declarado |
| **VE1-d** en vivo, sin tocar circuitos | P-VE-10 (lector contra FHIR a mano); piloto A3 repetido con LABADT y el lector nuevo (`labadt_adt.piloto`, 10 sondas; Q-VE-A-5); vuelta a USER con la sonda AA en `finally` | P-VE-10 cazado; piloto 10/10 `correcto` con S7 mostrando `previos` | un fuera de previsto en el piloto se adjudica antes de VE2 |
| **VE2** rejuicio | previsión §6.3 completada con E-VE1-1/3/4, sellada con huella; `ve/rejuicio.py` sobre todos los corpus; regresión, concordancia A1 y seco frente a la línea base; tabla por corpus | **0 fuera de previsto**; regresión con motivos = previstos; concordancia A1 idéntica; seco SIN EXPLICAR 0; LABADT y el canal Mirth con la misma categoría entre sí en `mi2`/muestra real | un fuera de previsto → se adjudica (juez nuevo / previsión / corpus); si es defecto del juez, se arregla con su prueba y VE2 se repite entero; **dos repeticiones como máximo**, luego el cambio culpable pasa a L-VE y se declara |
| **VE3** cierre | MCP: versión, S-n, DV-VE, L-VE, pendientes; `info_verificador.json` regenerado; servicio reiniciado; suites; guarda LIMPIO; `RESULTADO-ETAPA-VERIFICADOR.md`; preparación de la publicación (Q-VE-5): lista de ficheros, diff, sin nombres ni valores del sitio | todo lo anterior y el visto bueno al diff | guarda no LIMPIO → no se publica |

---

## 8. Preguntas: lo que no decide ni el estándar ni una S-n

### 8.1 Q-VE-D-n (diseño, para Jev)

| Q | Pregunta | Recomendación | Alternativa | Qué cambia según la respuesta |
|---|---|---|---|---|
| Q-VE-D-1 | ¿Cuándo es obligatorio el canónico: con AA **y fila de éxito**, o con AA **y sesión presente** (AA = procesado, §2.9.2.2 a)? | **AA y fila de éxito** (S-VE-1): es lo medido con 0 falsas alarmas; la ampliación espera a un caso que la pida | AA con sesión presente | con la ampliación cambian pruebas con AA, `log=[]` y sin canónico (`prueba_verificador.py:628`, `:896-913`) y la previsión de la regresión deja de ser 0 por construcción |
| Q-VE-D-2 | ¿Qué categoría da la ausencia del canónico con AA y fila de éxito? | **`fallo_silencioso`** (`fidelidad/sin_canonico`): el circuito dice haber escrito y no registró qué; el fallo del lector tiene su canal (`fallos.paso = canonico` → indeterminado) | `indeterminado/lectura` siempre | con la alternativa MMI-12 se «caza» como indeterminado y deja de contar en la tasa de caza de MI3; la leyenda no cambia en ningún caso |
| Q-VE-D-3 | ¿Una sola versión para S22: la **escrita** (S103 literal) o la **asumida** también en los mapeadores (S102)? | **Escrita** (S-VE-2) | Asumida en todo | con la alternativa el esperado con MSH-12 vacío es AA + gender omitido y AE 103 por S26: AA y AE 103 valen los dos (menos discriminante) y cambia `mapeador_referencia.py:480`, `mapeador_adt.py:534/574` |
| Q-VE-D-4 | Encounter encontrado por el paciente con `TieneVisita` = 1 y PV1-19 vacío: ¿se compara su contenido (cierra L-ADT-19) o solo se cuenta? | **Comparar** (R-VE-3): el juez ya tiene la proyección sin identifier | solo contar (n) y mantener L-ADT-19 | P-VE-8 y el texto de L-ADT-19; ningún corpus guardado lo nota |
| Q-VE-D-5 | ¿La representación del canónico ADT queda **mapeada a FHIR** (como hoy) o pasa a **cruda** con el mapeo en el juez? | **Mapeada** (S-VE-4): 0 cambios de código y la causa a tres (E, C, A) necesita C en términos FHIR | cruda | con la alternativa cambian la DTL del circuito (los circuitos no se tocan: condición 5), `mapeador_adt.comparar` y `canonico_texto` |
| Q-VE-D-6 | Los Encounter del paciente **anteriores al envío** (`previos`): ¿se ignoran con nota (L-ADT-12) o se juzgan también? | **Ignorar con nota**: el estado previo no está en la evidencia y en secuencias serían falsas alarmas | juzgar todo lo encontrado por paciente | con la alternativa el piloto A3 (S7 tras S1-S6) y las secuencias E6 de A4 darían `fidelidad/almacen` falsos |

### 8.2 Q-VE-A-n (alcance)

| Q | Pregunta | Recomendación | Alternativa | Qué cambia |
|---|---|---|---|---|
| Q-VE-A-1 | ¿Se levanta el otro motor para volver a medir MMI-12, MMI-19 y los 15 mutantes en vivo? | **No**: reproducción sintética + P-VE-10 + piloto A3 en IRIS, y L-VE-7 declarado | Sí (≈ 1 sesión; no cabe en el tope sin ampliarlo) | el «hecho cuando» de MI3 se cumple por construcción (rec.) o por medida (alt.) |
| Q-VE-A-2 | Las cinco preguntas de D (Q-MI-V-6/7, Q-DV1, Q-AMB-10, Q-MS-10): ¿siguen en `preguntas_pendientes` o se cierran como solo límite? | **Siguen pendientes**, bajo L-VE-2 | cerrarlas como límite y vaciar la lista | el MCP declara 5 pendientes (rec.) o 0 (alt.) |
| Q-VE-A-3 | Nombre de la versión: ¿`servidor 1.1` + `revision` además de la huella, o solo la huella? | **1.1 + revision** | solo huella | cómo se cita en los RESULTADO y en el repo público |
| Q-VE-A-4 | ¿El contrato público del canónico se **genera** desde el código con guarda, o se edita a mano? | **Generar** con guarda | a mano | con la alternativa vuelve a poder divergir (lo que midió MI1: 128 de 128) |
| Q-VE-A-5 | ¿Se repite el piloto A3 (10 sondas) con LABADT y el lector nuevo como prueba de colateral 0 en IRIS? | **Sí** (≈ 10 min, el circuito no se modifica; vuelta a USER en `finally`) | solo P-VE-10 contra FHIR a mano | sin el piloto, la limpieza y el censo por paciente del lector de IRIS no se prueban contra un circuito real |

---

## 9. Los riesgos que más me preocupan

1. **El servidor FHIR del laboratorio y `subject:identifier`.** Si no lo admite, `_lastUpdated` con filtro en cliente es la vuelta atrás; si
   tampoco, MMI-19 se queda en L-VE-3. Se mide en 15 minutos antes de escribir el lector (E-VE1-2). Añade el riesgo de la limpieza por
   paciente: un Encounter sin identifier dejado por lotes anteriores (S78) que el censo no vea daría un `nuevo` falso; por eso el censo y la
   limpieza usan la **misma** consulta y P-VE-10 prueba las dos.
2. **Las clases que VE-pre no censó**: lotes con AA sin fila de éxito y sin canónico (M12 los pasa de hallazgo a nota) y PV1-2/PID-30 fuera
   de tabla con MSH-12 vacío en el sitio (MS9). Son el único sitio donde el rejuicio puede salir «fuera de previsto»; E-VE1-1 y E-VE1-4 los
   cuentan antes y la previsión los lleva con su cota.
3. **El cambio de firma de los lectores** toca código que no está en esta carpeta (el arnés de Mirth que llama a `almacen`, `observar.py`
   del congelado) y las pruebas del MCP que fijan textos y la lista de pendientes: cada desviación se declara como DV-VE, y el piloto A3 es
   la red para el lector de IRIS; para el de Mirth solo hay unidad (P-VE-11) salvo Q-VE-A-1.

---

## Resumen (≤ 15 líneas)

1. Secciones: 0 decisiones; 1 MMI-12; 2 MMI-19; 3 Q-MS-9; 4 Q-MI-V-9; 5 límites L-VE; 6 rejuicio; 7 plan VE1-VE3; 8 preguntas; 9 riesgos.
2. MMI-12 (S-VE-1): con AA y fila de éxito en `adt_a01`/`adt_fhir`/`oru_fhir`, la sesión sin canónico es `fidelidad/sin_canonico` → `fallo_silencioso`; sin fila de éxito, nota (L5); solo acuse intacto; un cambio en `verificador._mapeador` y su manejador.
3. MMI-19 (S-VE-3): los dos lectores releen por los identificadores del mensaje y por `Encounter?subject:identifier=mrn|X` (el `patient` de R4 exige `resolve()` y S80 es lógico), con limpieza y censo previos (`previos`); el juez añade `visitas_por_paciente`: PV1-2 = N → `fidelidad/almacen` PV1-2; sin PV1-19 → compara contenido (cierra L-ADT-19).
4. Q-MS-9 (S-VE-2): S22 sigue a la versión escrita también en el acuse (una línea, `acuse_referencia.py:645`); la asumida solo acepta; con MSH-12 vacío PID-8 ∉ 0001 es AE 103 y AA es `fallo_silencioso/aceptado_imposible`, igual que el mapeador.
5. Q-MI-V-9 (S-VE-4): fuente única `mapeador_adt.CONTRATO_CANONICO` → `consultar_tabla("canonico_adt")` → `contrato_canonico_adt.md` generado con guarda; la representación (mapeada, `GivenName` unido, visita vacía con N) se documenta, no se cambia.
6. Límites L-VE-1..7 (C y D redactados; relectura solo en evidencia nueva; lector de `adt_a01`; cita R4 no en carpeta; AA sin éxito; sin remedir en el otro motor).
7. Rejuicio: niveles N1/N2/N3, firma por mecanismo M12/M19/MS9/CT, «fuera de previsto» definido, `ve/rejuicio.py` contra la línea base de VE-pre; versión `servidor 1.1` + huella nueva; lo sellado no se edita.
8. Previsión por corpus: regresión 2.721 → 0; A1 lab/sitio → 0 (notas L-VE-3); mi2 → 0 (sin `alternativa_S26` en el sitio); mi3 → MMI-12 128 y MMI-19 14 cazados (sintético); muestra real sitio → ≤ 3 solo con evidencia exacta, 0 con la viva; lab → 0; agentes → 0; cotas abiertas E-VE1-1/3/4 (esperado 0).
9. Preguntas: 6 Q-VE-D (alcance de la obligación, categoría, versión escrita, contenido sin PV1-19, representación, `previos`) y 5 Q-VE-A (remedir en el otro motor, pendientes de D, nombre de versión, contrato generado, piloto A3).
10. Plan: VE1 sondas (E-VE1-1..4) → pruebas en rojo → código MS9 → M12 → M19 → CT → en vivo sin tocar circuitos; VE2 previsión sellada y 0 fuera de previsto (≤ 2 repeticiones); VE3 MCP, guarda, RESULTADO, publicación.
11. Riesgos: `subject:identifier` no admitido (escalera `_lastUpdated` → barrido → L-VE-3); las clases no censadas por VE-pre; el cambio de firma de los lectores y las pruebas del MCP fuera de la carpeta.
