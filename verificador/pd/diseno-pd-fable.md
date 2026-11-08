# Diseño a ciegas de la etapa 40: la Observation de PD1-7 en el juez (8-nov-2026)

Diseño de Fable, antes de escribir código, para la pregunta fijada en `ANTES-ETAPA-PD17.md`: que el juez empareje con su campo la
Observation que la guía crea desde PD1-7 en un ADT, cambiando solo lo que dice de esa Observation. Leído: el ANTES, el resultado
de la etapa 37 (`RESULTADO-JUEZ.md`), el juez (`conversion.py` y lo que lo rodea), sus pruebas, el rejuicio de la 37, las hojas y
los ConceptMap de la guía y el texto de HL7 v2.5. Nada de `privado/`, ni salidas de conversores, ni otros resultados. Las rutas
van relativas a `fase12/` (en el repositorio publicado, `verificador/`).

Lo que hace hoy el juez, medido sobre una copia con casos sintéticos (la sonda no se guarda):

| El caso | Hoy |
|---|---|
| PD1-7 = F, una Observation con `valueCodeableConcept` (v2-0315, F), sin OBX | `recurso_inventado` (OBX): fallo silencioso |
| PD1-7 = F, sin Observation | correcto: no echa nada en falta |
| PD1-7 = F, un OBX, las dos Observation en cualquier orden | la primera pasa por la del OBX (nota `fuera_proyeccion`), la segunda `recurso_inventado` |
| PD1-7 = Y, ACC con ACC-5 = Y, una Observation (v2-0315, Y) | `recurso_sin_mapa` (ACC), «ACC-5 = 'Y', de la 0136» (el primer riesgo de L-CV-17) |
| Lo mismo en un mensaje 2.8 | igual, más la nota de versión |
| ORU con PD1-7 y la Observation de más | `recurso_inventado` (OBX) |

## 1. Qué hace el juez después

### 1.1 La base

- **La guía** crea en ADT_A01 una Observation desde PD1-7 cuando viene, con el sujeto en el Patient del PID: `[G MSG_ADT_A01.csv:19]`
  («IF PD1-7 VALUED», `Observation[1]`, `PD1[Observation-LivingWill]`, `Observation[1].subject.reference=Patient[1].id`). La hoja
  es la de A01, y el juez la aplica a los ocho eventos como ya hace con PID y PV1; en v2.5 el PD1 es opcional en todas las
  estructuras que el juez juzga (A01, A02, A03, A05 y A09: `[E3 Ch03.txt:225, 334, 423, 616]` y la de A09).
- **El mapa del segmento,** `[CM segment-pd1-livingwill-to-observation]` (`estandares/v2mappings/package/`), tiene **un solo
  elemento:** PD1-7 (Living Will Code) → `valueCodeableConcept`, equivalente, 0..1, «mappedVia» `table-hl70315-to-v2-0315`. No
  fija `Observation.code`, ni `status`, ni nada más. Lo que el paquete no fija, el juez no lo exige (como L-CV-2 con las fórmulas de
  XTN).
- **El mapa de la tabla,** `[CM table-hl70315-to-v2-0315]`: Y, F, N, I y U van a sí mismos en el sistema
  `http://terminology.hl7.org/CodeSystem/v2-0315`. Es la identidad.
- **En v2.5,** PD1-7 es un IS de 2 caracteres con la tabla de usuario 0315 (`[E3 Ch03.txt:8504]`; definición en
  `[E3 Ch03.txt:8630-8643]`, «Refer to User-defined Table 0315 - Living Will Code for suggested values»; la tabla, con Y, F, N e I,
  en `[E3 Ch03.txt:7146-7151]`, bajo PV2-43, y con U en el apéndice A). Un IS es «drawn from a site-defined (or user-defined)
  table» (`[E2A CH02A.txt:2424-2434]`): un valor fuera de la tabla es legal, como la 0001 en la etapa 37.
- **En FHIR R4,** `Observation.status` es 1..1 con binding required (`observation-status`) y `Observation.value[x]` 0..1
  (`[F Observation]`). El juez ya lo aplica a las Observation de los OBX (L-CV-11, `_estado`).
- **Y y N coinciden con la 0136.** Una Observation de PD1-7 con Y o N tiene la misma forma que las que la regla de la 0136 de la
  etapa 37 (L-CV-17) atribuye a ACC o PDA. Lo que las separa es el sistema del coding (v2-0315 frente a v2-0136 o
  `special-values`), y, si el conversor no lo pone, nada.

### 1.2 Cómo la reconoce (el emparejamiento, `emparejar`, rama `adt`)

Por cada Observation de primer nivel del Bundle, en este orden; el primer paso que casa manda:

1. **Si su `code` lleva el código de un OBX del mensaje, es la de ese OBX.** Como hoy (hoy vive dentro de `_origen_sin_mapa`;
   pasa a ser el primer paso explícito, con el mismo resultado). El código gana sobre el valor: una Observation con el código del
   OBX y el valor de PD1-7 es la del OBX.
2. **Si PD1-7 está valorado y aún no hay Observation de PD1-7, es candidata si su `valueCodeableConcept` lleva un coding con
   `system` = `http://terminology.hl7.org/CodeSystem/v2-0315`, o con `code` igual al valor de PD1-7.** Entre varias candidatas,
   la primera que lleve el sistema de la 0315; si ninguna lo lleva, la primera por orden del Bundle. **Una sola:** la hoja crea
   `Observation[1]` una vez y el mapa dice 0..1. La elegida entra en `recursos` con el rol `Observation#PD1` y origen `PD1-7`
   (como `Encounter#1` con `PV1`), y se juzga en `_juzgar`. El valor de PD1-7 es su primer componente, desescapado
   (`_t(m, _f(m, pd1, 7), 1)`): en v2.5 un IS no tiene componentes, así que es el campo entero; en 2.6+ no se proyectan los
   componentes posteriores (L-CV-16).
3. **Si no, `_origen_sin_mapa`** (ACC y PDA, L-CV-17), como hoy.
4. **Si no, `origen_guia` o `inventado` por orden,** como hoy.

Con PD1-7 vacío, el paso 2 no existe: una Observation con el sistema de la 0315 se queda como hoy (la condición de la hoja es
«IF PD1-7 VALUED», y sin PD1-7 no hay con qué compararla).

### 1.3 Qué juzga de ella (`_livingwill`, nueva; el hecho es siempre `PD1-7`)

Las citas de todos sus hallazgos: `C["PD1-7"] = ["[CM segment-pd1-livingwill-to-observation PD1-7 → valueCodeableConcept]",
"[CM table-hl70315-to-v2-0315]", "[G MSG_ADT_A01.csv:19]", "[E3 Ch03.txt:8504]", "[E3 Ch03.txt:8630-8643]"]`.

| Lo que hay | El juez | Cuenta |
|---|---|---|
| PD1-7 valorado y ninguna Observation reconocida | `recurso_ausente`, «falta la Observation de PD1-7 = 'F' (PD1[Observation-LivingWill])» | sí, en toda versión (como el Encounter del PV1, Q-CV-D-6) |
| Coding (v2-0315, valor de PD1-7) | nada | |
| Coding con el código de PD1-7 y otro sistema (v2-0136, `special-values`, ninguno) | `codigo_mal_mapeado`, «esperado ('…/v2-0315', 'F') (de 'F'), observado [...]» | sí (como PID-16 con la 0002, `_codigo_tabla`) |
| Coding con el sistema de la 0315 y otro código, con PD1-7 dentro de la 0315 | `valor_distinto`, «Observation.valueCodeableConcept: esperado 'F', observado 'Y'» | sí |
| PD1-7 fuera de la 0315 (tabla de usuario) y el código igual | nada: la identidad vale para cualquier valor | |
| PD1-7 fuera de la 0315 y otro código, con el sistema de la 0315 | nota `convencion` «fuera del ConceptMap»; con MSH-12 ≠ 2.5, nota `version` | no |
| `status` ausente o fuera de `observation-status` | `fhir_invalido` (1..1, required); ningún valor esperado, porque el paquete no lo fija | sí |
| `subject` | `_sujeto(..., "Observation.subject", "PD1-7")`: resuelve al Patient del PID, o `referencia_rota`; la lógica por identifier es convención | según `_sujeto` |
| `code`, `effective[x]`, `performer`, `category`, lo demás | no se juzga: el paquete no lo fija (L-CV-18) | |

El valor se juzga con `_codigo_tabla(J, "PD1-7", v, r["valueCodeableConcept"], "0315", ...)`, con la 0315 añadida a `MAPAS` y `CM`
(y a la lista de `cv/extraer_mapas.py`, para que `autoprueba()` la compare con el paquete), más la rama de «mismo sistema, otro
código» como `valor_distinto`, que `_codigo_tabla` hoy daría como `codigo_mal_mapeado`.

### 1.4 Los casos del ANTES

| PD1-7 | Observation del conversor | OBX | ACC/PDA | Después |
|---|---|---|---|---|
| F | (v2-0315, F) | no | no | correcto; `emparejamiento` lista `Observation#PD1` |
| F | (v2-0315, F) y la del OBX, en cualquier orden | sí | no | correcto, con la nota `fuera_proyeccion` del OBX (hoy: un `recurso_inventado`) |
| F | solo (v2-0315, F) | sí | no | correcto, sin nota (hoy: correcto con nota; la del OBX no se proyecta en ADT, L-CV-7) |
| F | (v2-0136, F) o (sin sistema, F) | — | — | `codigo_mal_mapeado` PD1-7 |
| F | (v2-0315, Y) | — | — | `valor_distinto` PD1-7 |
| F | ninguna | — | — | `recurso_ausente` PD1-7 (hoy: correcto) |
| F | `valueString` "F" | no | no | no se reconoce: `recurso_ausente` PD1-7 y `recurso_inventado` OBX, dos hallazgos por una Observation (como L-CV-15 en ORU); L-CV-18 lo declara |
| Y | (v2-0315, Y) | no | ACC-5 = Y | es la de PD1-7 (hoy: `recurso_sin_mapa` ACC) |
| Y | (v2-0315, Y) y (v2-0136, Y) | no | ACC-5 = Y | la primera, de PD1-7; la segunda, `recurso_sin_mapa` ACC por la 0136 |
| Y | dos de solo Y, sin sistema | no | ACC-5 = Y | la primera del Bundle, de PD1-7; la segunda, de ACC. El juez no tiene con qué separarlas (Q-PD-2, L-CV-18) |
| vacío | (v2-0315, F) o de solo Y | — | ACC-5 = Y | como hoy: `recurso_inventado`, o `recurso_sin_mapa` ACC por la 0136 |
| F, en 2.8 | (v2-0315, F) | — | — | correcto, más la nota de versión de MSH-12 (hoy: `recurso_inventado`) |
| F, en 2.8 | ninguna | — | — | `recurso_ausente` cuenta (como «2.8: cuenta igual» de P-CV-30: el mapa es de la guía, no de la tabla de v2.5) |
| X (fuera de la 0315), en 2.8 | (v2-0315, W) | — | — | nota `version` (en 2.5, `convencion`) |
| F | la de más en un ORU | — | — | como hoy, `recurso_inventado` (fuera de la etapa, §7) |

`recuentos` no cambia en ningún caso (cuenta entries por tipo). El veredicto solo puede moverse entre `correcto` y
`fallo_silencioso convertido`; nunca toca `aceptado_imposible` ni los rechazos.

### 1.5 Lo que cambia en la información del juez

- **S-CV-4** añade «la Observation de PD1-7 por su valor o el sistema de la 0315 (etapa 40)».
- **L-CV-17** pierde a PD1-7 de su primer riesgo: queda «una Observation de solo Y/N que no sale de ACC ni de PDA (una inventada,
  o la de PD1-7 cuando el conversor no la saca como `valueCodeableConcept`) se da por de ellos si el mensaje trae uno con ese
  valor».
- **L-CV-18, nuevo:** «Etapa 40: la Observation de PD1-7 (`PD1[Observation-LivingWill]`) se reconoce solo con PD1-7 valorado, por
  un coding de `valueCodeableConcept` con el sistema de la 0315 o con el código de PD1-7; una por mensaje, la primera con el
  sistema. El paquete solo fija PD1-7 → valueCodeableConcept, así que `code`, `effective[x]` y lo demás no se juzgan. Con otro
  `value[x]` no se reconoce: sale `recurso_ausente` de PD1-7 y la Observation sigue por los pasos de siempre (`recurso_inventado`,
  o ACC/PDA por la 0136). Con PD1-7 en Y o N y ACC o PDA con ese valor, dos Observation de solo Y/N sin sistema no se distinguen:
  la primera es la de PD1-7. Solo en ADT: la hoja de ORU también la crea (MSG_ORU_R01.csv:17) y en oru_conv sigue como
  `recurso_inventado`.»
- **El perfil `PERFIL_GUIA_ADT`** pasa de 22 a 23 filas, con una para `Observation (de PD1-7)` / `PD1-7`, nivel `cuenta`, citas
  `C["PD1-7"]`.
- **El texto de versión del servidor** (`mcp_verificador.REVISION`) gana la entrada de la etapa 40 al principio: «etapa 40: la
  Observation de PD1-7 en adt_conv (S-CV-4) y L-CV-18; antes, etapa 37: …». La entrada de la 14l sigue diciendo L-CV-1..16, como
  fijó Q-JZ-9.

## 2. Las decisiones abiertas, para Jev

**Q-PD-1. Reconocer la Observation solo por el dato, o también por eliminación.**
- (a) Solo por el dato (el sistema de la 0315 o el código de PD1-7), lo propuesto. Hechos a favor: es la regla de la etapa 37
  (Q-JZ-3: por un dato compartido), y el juez nunca da por de un campo lo que no lleva nada de él; una Observation inventada
  sigue siendo inventada. En contra: una Observation de PD1-7 con el valor mal convertido (por ejemplo, F llevado a `true`) no se
  reconoce y sale como ausente más inventada, dos hallazgos por un defecto, en vez de `valor_distinto`.
- (b) Además, por eliminación: con PD1-7 valorado, si tras los pasos 1 y 3 queda exactamente una Observation, es la de PD1-7 y se
  juzga su valor. A favor: un defecto, un hallazgo (`valor_distinto`); es lo que hace el emparejamiento de ORU con los
  DiagnosticReport cuando cuentan igual («orden»). En contra: una Observation inventada en un mensaje con PD1-7 pasaría a
  `valor_distinto` de PD1-7, y la regla de la 37 rechazó el orden como criterio para las Observation de ADT.
  Ninguna evidencia guardada lleva PD1-7: las dos opciones dan el mismo rejuicio.

**Q-PD-2. Con PD1-7 en Y o N y ACC o PDA con ese mismo valor, una Observation de solo Y/N sin sistema.**
- (a) Es la de PD1-7, lo propuesto (el paso 2 va antes que el 3). A favor: la guía sí mapea PD1-7 y no mapea ACC ni PDA; en las
  365 Observation sin mapa del rejuicio de la 37 el valor lleva el sistema de la 0136 o un código propio del conversor, así que el
  sistema las separa cuando el conversor lo pone. En contra: con dos Observation así y sin sistemas, el juez elige por orden.
- (b) Sin sistema no es de PD1-7: se queda como hoy (ACC/PDA por la 0136, o inventada) y PD1-7 sale `recurso_ausente`. A favor:
  el juez no elige por orden. En contra: en el caso corriente, una sola Observation de solo Y sin sistema con PD1-7 = Y, contaría
  dos veces (ausente y sin mapa) lo que es una Observation bien hecha salvo el sistema; y mantiene el primer riesgo de L-CV-17
  que esta etapa quiere cerrar.

**Q-PD-3. PD1-7 valorado y ninguna Observation: `recurso_ausente` que cuenta, o nota.**
- (a) Cuenta, lo propuesto. A favor: la hoja la crea bajo condición, y la condición se cumple; es lo que hace el juez con el
  Encounter del PV1 (Q-CV-D-6, incluso con PV1-2 = N) y con la Observation de cada OBX en ORU. En contra: la Observation de PD1-7
  es periférica, y un conversor que proyecta solo los segmentos principales pasaría de correcto a fallo silencioso en cuanto el
  mensaje traiga PD1-7.
- (b) Nota (`fuera_proyeccion` o una nueva), que no cuenta. A favor: no cambia veredictos por un segmento opcional. En contra: la
  guía no distingue destinos principales y periféricos, y S-CV-5 dice que un recurso ausente cuenta.
  Ninguna evidencia guardada lleva PD1-7: no cambia el rejuicio ni las bases con ninguna de las dos.

Si Jev elige (b) en Q-PD-1 o en Q-PD-2, cambian las pruebas P-CV-33 (los casos de la tabla) y el clasificador del rejuicio en la
rama que corresponda; el resto del diseño se mantiene.

## 3. Las pruebas, en rojo antes

En `prueba_conversion.py`, dos pruebas nuevas, con los mismos ayudantes de la etapa 37 (`seg`, `msg`, `adt_bundle`, `con_segs`,
`ACC`, `OBX_ADT`) y dos nuevos: `PD1 = seg("PD1", {7: "F"})` y `obs_pd1(valor, sistema=CS0315, i=...)`, una Observation con
`status`, `code` cualquiera, `subject` al Patient y `valueCodeableConcept`. Cada comprobación muta una sola cosa.

**P-CV-33, la conducta.** Con el juez de hoy caen todas las que no son control:
- PD1-7 = F y la Observation, sin OBX: `cuentan` vacío, categoría `correcto`, y `emparejamiento` con el rol `Observation#PD1`
  (hoy: `recurso_inventado`);
- con OBX, las dos Observation en los dos órdenes: `cuentan` vacío y la nota `fuera_proyeccion` (hoy: un `recurso_inventado`);
- con OBX y solo la de PD1-7: `cuentan` vacío (control: hoy también);
- sin Observation: `[("fidelidad", "recurso_ausente", "PD1-7")]` y la cita `[G MSG_ADT_A01.csv:19]` en el hallazgo (hoy: correcto);
- con el sistema de la 0136 y con ninguno: `codigo_mal_mapeado` PD1-7 (hoy: inventado);
- (v2-0315, Y) con PD1-7 = F: `valor_distinto` PD1-7 (hoy: inventado);
- PD1-7 = X: con el código X, nada; con (v2-0315, W), nota `convencion` en 2.5 y `version` en 2.8 (hoy: inventado);
- PD1-7 = Y y ACC con ACC-5 = Y, una Observation (v2-0315, Y): `cuentan` vacío (hoy: `recurso_sin_mapa` ACC); con una segunda
  (v2-0136, Y): solo `recurso_sin_mapa` ACC; dos sin sistema: lo mismo, y la primera es la de PD1-7 (Q-PD-2 a);
- control: PD1-7 vacío con ACC-5 = Y y una Observation de solo Y: `recurso_sin_mapa` ACC, como hoy;
- control: PD1-7 = F y la Observation con el código del OBX del mensaje y el valor F: es la del OBX (`fuera_proyeccion`) y PD1-7
  sale `recurso_ausente` (hoy: solo la nota);
- `valueString` "F": `recurso_ausente` PD1-7 y `recurso_inventado` OBX (hoy: solo el inventado);
- `status` ausente: `fhir_invalido` PD1-7 además (hoy: inventado);
- `subject` a otro Patient: `referencia_rota` PD1-7 (hoy: inventado);
- 2.8 con (v2-0315, F): `cuentan` vacío y la nota de versión; 2.8 sin Observation: `recurso_ausente` cuenta (hoy: inventado, y
  correcto);
- control ORU: `oru_msg()` con PD1 y la Observation de más sigue como `recurso_inventado` OBX (hoy también).

**P-CV-34, la información del juez.** Caen todas con el juez de hoy:
- `PERFIL_GUIA_ADT` tiene 23 filas y una con `campo == "PD1-7"`;
- `L_CV["L-CV-18"]` existe y nombra PD1-7, la 0315 y ORU; `L_CV["L-CV-17"]` ya no da a PD1-7 por riesgo de la regla (nombra
  `valueCodeableConcept`, no «que la guía sí mapea»);
- `S_CV["S-CV-4"]` nombra PD1-7;
- `MAPAS["table-hl70315-to-v2-0315"]` es la identidad sobre Y, F, N, I, U con el sistema v2-0315, y `autoprueba()` sigue en
  TODO BIEN contra el paquete;
- `mcp_verificador.REVISION`: la primera entrada empieza por «etapa 40» y nombra L-CV-18; la segunda, por «etapa 37» con L-CV-17;
  la de la 14l sigue con L-CV-1..16.

**Las que cambian** (caen con el juez de hoy una vez cambiadas, y van al mismo rojo):
- P-CV-32: su comprobación «L-CV-17 nombra PD1-7» pasa a lo contrario («L-CV-17 ya no da la de PD1-7 por de ACC o PDA»);
- P-VX-20 y P-MD-24: el control del perfil de ADT, de 22 a 23 filas;
- P-MD-25 (d): las huellas de `C` (nueva `C["PD1-7"]`), `MAPAS` (la 0315) e `INFO` (S-CV-4, L-CV-17 y L-CV-18), medidas sobre
  una copia con el parche aplicado, como hizo `jz/parche_prueba_jz3.py`.

El rojo se guarda en `pd/ROJO-PD.txt` (las tres suites contra el juez de hoy, con las pruebas nuevas y las cambiadas) y
`pd/ROJO-PD-2.txt` (la prueba del clasificador del rejuicio, antes de que exista). Las cifras de las pruebas se dan del
repositorio publicado: previsiblemente 34 pruebas de conversión, con las comprobaciones que resulten.

## 4. El rejuicio

Como en la 37: la línea base se hace **antes de tocar el juez** con `md/rejuicio_md.py linea_base` (el juez de hoy, `4a75a245…`), y
`pd/rejuicio_pd.py comparar` la enfrenta al juez nuevo sobre las 30.118 evidencias, reutilizando `md/rejuicio_md.py` sin tocarlo.
`pd/prueba_rejuicio_pd.py` prueba el clasificador sobre juicios sintéticos cuyos mensajes llevan los valores de verdad.

**Una diferencia es de la conducta de PD1-7** si cumple todo esto; si algo falla, es «fuera», y «fuera» es la regla de parada:
1. **El caso:** `punto == "adt_conv"` y el mensaje trae un PD1 con PD1-7 valorado (primer componente no vacío). Sin eso, cualquier
   diferencia es «fuera», aunque tenga la forma.
2. **Lo que sale** solo puede ser `recurso_inventado` con hecho OBX, `recurso_sin_mapa` con hecho ACC, PDA o ACC/PDA, o la nota
   `fuera_proyeccion` de OBX. **Lo que entra** solo puede ser un hallazgo con hecho `PD1-7` (de cualquier clase menos `rechazo`), o
   uno de esos tres.
3. **Los hallazgos de PD1-7 que entran dicen el valor del mensaje:** el `que` de `recurso_ausente` («PD1-7 = 'F'»), de
   `codigo_mal_mapeado` («de 'F'») y de `valor_distinto` («esperado 'F'») lleva el valor que está en PD1-7 del mensaje; una nota
   de convención o versión casa con MSH-12 (2.5 o vacío, frente a otra versión).
4. **El libro de las Observation,** por `fullUrl` en los `que`: las parejas (subtipo, url) de `recurso_inventado` y
   `recurso_sin_mapa` que entran son un subconjunto de las que salen (ninguna cambia de subtipo); las que salen y no entran son
   como mucho una (la que ahora es de PD1-7) más, si el mensaje trae OBX, otra (la que pasa a ocupar el sitio del OBX, y entonces la
   nota `fuera_proyeccion` entra o ya estaba). Si entra un `recurso_sin_mapa`, el dato que cita está en ese campo del mensaje, con
   la regla `_tiene` de la 37.
5. **Los recuentos no cambian; el veredicto** solo pasa entre `correcto` y `fallo_silencioso` con subtipo `convertido`; nada de
   `aceptado_imposible` ni de rechazos; `punto_vc` no cambia.

Lo que el clasificador **no mira,** dicho y no comprobado (como Q-JZ-8): si la Observation que ahora es de PD1-7 lleva de verdad el
sistema de la 0315 o el código de PD1-7, porque no ve el Bundle; eso lo prueba P-CV-33.

**El control** siembra un defecto en el juez por pasada y exige que toda evidencia con el defecto salga «fuera», con las firmas
guardadas (`pd/CONTROL-PD.json`, `pd/FIRMAS-CONTROL-PD.json`). Con la forma de la conducta y sin serlo:
- `recurso_ausente` de PD1-7 en todo ADT **sin** PD1-7 valorado (marca las 21.553 de ADT): sale por la regla 1;
- una Observation `recurso_sin_mapa` de ACC dada por `recurso_inventado` (marca las 161 con ACC o PDA): sale por el libro (la
  pareja cambia de subtipo);
- la Observation de un OBX, en un ADT con OBX y sin PD1-7, sacada del sitio del OBX (pierde la nota `fuera_proyeccion` y entra
  `recurso_inventado`): sale por la regla 1 y por el libro;
- un `recurso_ausente` de PD1-7 cuyo `que` cita un valor que no es el del mensaje, en un ADT con PD1 presente: sale por la regla
  3. Si en el corpus no hay ningún PD1, esta pasada marca 0 evidencias y se declara así, y el caso queda en las pruebas sintéticas;
- un `valor_distinto` en PID-5 y en PID-8 (los de la 37): salen por la regla 2.

En las pruebas sintéticas del clasificador, además: dos url que salen sin OBX en el mensaje; el veredicto a `aceptado_imposible`;
los recuentos cambiados; un rechazo que cambia; el punto `oru_conv`; PD1-7 vacío con todo lo demás bien formado.

## 5. La previsión (se sella antes de correr el juez nuevo)

`pd/PREVISION-PD.json`, con su huella en `pd/SELLO-PD.txt`, contada por `pd/prever_pd.py` sobre la línea base y los mensajes de las
evidencias, sin correr el juez nuevo:
- **Rejuicio: 0 diferencias.** El ANTES mide que ninguna de las 21.553 evidencias de ADT lleva PD1-7; el paso 2 del
  emparejamiento solo existe con PD1-7 valorado, y nada más cambia en el camino de una Observation sin él (los pasos 1, 3 y 4
  dan lo mismo que hoy). ORU, VXU y MDM no se tocan. `prever_pd.py` vuelve a contar, por carpeta y conversor, los mensajes con PD1
  y con PD1-7 valorado, y deja las dos cifras: lo previsto es PD1-7 valorado = 0. «Fuera», faltan, punto que cambia: 0.
- **El control:** toda evidencia con el defecto, «fuera», en las cinco pasadas; la cuarta puede marcar 0 si no hay PD1.
- **Las clases del estudio:** 15 nuevas, 31 ya declaradas, 16 convenciones, iguales caso a caso (`pd/CLASES-PD-antes.json` y
  `-despues.json` tienen que ser idénticos salvo la huella del juez). Si no lo son, el rejuicio tendría diferencias y la regla de
  parada manda.
- **Las bases de la integración continua:** en las tres de la demostración y en las dos del ejemplo cambia la huella del juez
  (`creada_de.juez.huella`, de `4a75a245…` a la nueva) y **ningún caso**; en el juguete, el defecto sembrado sale en los mismos 344
  casos; las dos corridas de cada base, iguales byte a byte. Lo comprueba `pd/comprobar_bases_pd.py`, con el control negativo de la
  37 (un caso que cambia, la huella del corpus que cambia, la huella del juez que no cambia: cada uno tiene que hacer caer la
  comprobación).

## 6. Lo que arrastra

- **La huella del juez** (los 17 ficheros de `mcp_verificador.FICHEROS`; cambia `conversion.py`, y `mcp_verificador.py` por el
  texto de versión). Con ella, `CORRIDA.json` y las bases.
- **Las tres bases de la demostración,** rehechas con `base_nc.sh` (unos 50 minutos; dos corridas iguales, «igual» y el positivo
  del juguete), y comprobadas contra la previsión con `pd/comprobar_bases_pd.py`. Van en el primer push.
- **El proyecto de ejemplo:** sus dos bases con `ejemplo-ci/ci/hacer_base.sh` y el pin de `ejemplo-ci.yml` y `rojo-ci.yml`
  (hoy `0783492…`) al commit del primer push, en el segundo push. Antes de cada push, `cv/ci/ensayo_flujo.py`; después,
  `cv/ci/comprobar_publicado.py` con los tres `ENSAYO.json`.
- **La información del juez:** S-CV-4, L-CV-17, L-CV-18, el perfil de ADT (23 filas), `C["PD1-7"]`, `MAPAS`/`CM` con la 0315 y la
  lista de `cv/extraer_mapas.py`, y `REVISION` con la entrada de la etapa 40.
- **Las pruebas que fijan huellas o tamaños:** P-MD-25 (d) (`C`, `MAPAS`, `INFO`), P-VX-20 y P-MD-24 (22 → 23 filas), P-CV-32
  (L-CV-17 sin PD1-7). Las líneas base privadas de las pruebas que rejuzgan VXU y MDM, si llevan la huella del juez, se rehacen
  cuando el rejuicio haya dado 0 diferencias.
- **`cv/ci/CI.md`:** la frase que cita a la 37 como ejemplo de juez que cambia gana una mención a la 40, que solo cambia la
  huella.
- **Lo que no se toca:** `cv/cv3_clases.py` y `cv/CLASES-CV3.json` (ningún caso cambia; un hallazgo de PD1-7 no tiene clase, pero
  no hay ninguno), los resultados sellados y sus JSON, y `jz/` entero: su clasificador y sus pruebas siguen valiendo para lo suyo.
- **La frase del estudio no cambia:** 15 nuevas, 31 ya declaradas, 16 convenciones. Si el rejuicio o las clases dijeran otra cosa,
  es «fuera», y se para.

## 7. Lo que no resuelve

- **ORU y VXU.** La hoja de ORU_R01 también crea la Observation de PD1-7 (`MSG_ORU_R01.csv:17`, `Observation[4]`), y VXU_V04 lleva
  PD1. La pregunta del ANTES es la de un ADT; en `oru_conv` sigue como `recurso_inventado` (L-CV-18 lo dice) y `vxu_conv` no se
  toca.
- **`Observation.code`.** El paquete no lo fija para PD1-7, así que el juez no lo juzga ni lo usa para reconocerla. Si otra copia
  de la guía lo fija, es otra etapa.
- **Otros `value[x]`.** Un `valueString` o un `valueBoolean` con el dato de PD1-7 no se reconocen; salen como ausente más
  inventada. Reconocerlos sería juzgar el tipo, y el mapa solo dice `valueCodeableConcept`.
- **La lectura de los tipos de 2.6+** (el PD1-7 CWE del mapa de la guía, con componentes): fuera de la etapa por el ANTES; el juez
  toma el primer componente, que en v2.5 es el campo entero.
- **Dos Observation con el sistema de la 0315 en el mismo Bundle:** la segunda sigue los pasos de siempre (inventada, o ACC/PDA
  por la 0136). El mapa dice una.
- **PV2-43,** el otro Living Will Code de v2.5: PV2 no se proyecta y la hoja no lo mapea a nada.
- **La clase del estudio** de un hallazgo de PD1-7 (L-CV-10): no hay casos, y `cv3_clases.py` no cambia.
