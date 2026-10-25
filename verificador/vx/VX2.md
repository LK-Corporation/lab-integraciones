# VX2: el corpus VXU, la previsión sellada y las corridas (etapa 20)

**Qué se hizo.**

- **VX2a.** `bases_vxu.py` trae las 40 bases; la huella del conjunto es `5734cc3b9d6d`, y el corpus `vxu` del manifiesto, `3bcb0eefe4dd`.
- **VX2b.** La previsión `vx/prevision-vxu.json` quedó sellada en `073870e` (sha256 `963baedd06c7…`) antes de juzgar las 40 bases.
- **VX2c.** Los dos conversores del estudio corrieron con `cv/verificar_conversor.py` sobre el corpus del laboratorio más los mínimos, las mismas opciones que el informe publicado, ahora con las 40 bases de VXU dentro: 343 mensajes más los 68 mínimos en la caja.

**Las corridas.**

- Microsoft tardó 3 min 27 s y LinuxForHealth, 17 s.
- Las evidencias están en `privado/vx/vx2c/`.
- Juez final: `99257d5b7084`, tras una repetición (de dos posibles; ver «Defectos del juez»).

**ADT, ORU y mínimos no cambian (P-VX-22 c).** En los dos conversores, las filas `adt`, `oru` y `minimos` de `INFORME.json`
son idénticas a las de `cv/vc/ejemplos/INFORME-*.json`, que es lo publicado.

## Resultado frente a la previsión sellada

**Categorías.**

| | Previsto | Microsoft | LinuxForHealth |
|---|---|---|---|
| corre VXU en la caja | 0,97 / 0,95 | sí, las 40 | sí, las 40 |
| `correcto` | 0-5 % | 0 % | 0 % |
| `fallo_silencioso` | 90-100 % / 85-100 % | 100 % | 100 % |
| `rechazo_incorrecto` | 0-5 % / 0-10 % | 0 % | 0 % |
| `indeterminado` | ≤ 2 % | 0 % (2,5 % antes de la repetición 1) | 0 % |

**Mecanismos previstos que se vieron.**

- **Microsoft, 9 de 21.** MC-VX-1, 3, 12, 13, 14, 15, 16, 18 y 21; con los «fuera de previsto», 12. El rango previsto era 6-11.
- **LinuxForHealth, 8 de 21.** MC-VX-1, 3, 9, 10, 11, 12, 14 y 16; con los «fuera de previsto», 12. El rango previsto era 6-11.

| Mecanismo | Microsoft | LinuxForHealth |
|---|---|---|
| MC-VX-1, ruta (RXR-1, `codigo_mal_mapeado`) | 37 bases: system propio `example.com/…/HL70162` para todos los códigos | 37: `v2-0162` para IM/SC/ID/PO, donde la 0162 manda v3-RouteOfAdministration (la «más probable» del diseño) |
| MC-VX-3, unidad (RXA-7) | 34 + 1: sin `unit` cuando CE.2 está vacío, aunque el CM dice `CWE.1 → Quantity.unit IF CWE.2 IS NOT VALUED`; ISO+ no canónico (B04) | 3 + 1: `unit` = CE.1 donde hay CE.2 (B02, B05, B39); ISO+ (B04) |
| MC-VX-9, RXA-21 D (B11) | — | `completed` donde toca `entered-in-error` |
| MC-VX-10, `recorded` (B12) | — | RXA-22 con RXA-21 U, donde manda ORC-9 (Q-VX-D-3) |
| MC-VX-11, ORC-2/ORC-3 | — | 39 + 2: ORC-3 y ORC-2 perdidos; el identifier es `<CVX>-CVX` |
| MC-VX-12, OBX de ORDER | B30 sin `partOf` | B30 y B31 absorbidos; B32 perdido: `recurso_ausente` (Q-VX-D-4) |
| MC-VX-13, system de CVX/MVX | 39 + 36: `example.com/…/CVX` y `…/Identifier/MVX` | — |
| MC-VX-14, NK1 | B37: GRD con system propio y sin código | B36, B37 y B39: NK1 sin RelatedPerson ni contact |
| MC-VX-15, varias RXA | B35: los dos grupos sin ORC-2/3 fundidos en una Immunization con los dos códigos | — |
| MC-VX-16, RXA-19 (B40) | `reasonCode` parcial | `reasonCode` parcial |
| MC-VX-18, system del sitio | 35: `example.com/…/HL70163` | — |
| MC-VX-21, teléfono del NK1 | B36, B37 y B39: `telecom` sin `value` (XTN.7 solo) | — |

**Lo que no se vio.** MC-VX-17 (`primarySource` por omisión, previsto con 0,95 en los dos) no apareció. Las muestras de E-VX-3 llevaban
`RXA-9 = 00^New Record^NIP001`, y de ahí los conversores deducen `primarySource` (la regla de los CDC). Las 40 bases no llevan RXA-9.
La previsión confundió «por omisión» con «deducido de RXA-9». Tampoco se vieron MC-VX-2, 4, 5, 6, 7, 8, 19 y 20, ni MC-VX-13 y 18 en
LinuxForHealth (previstos bajos).

## Fuera de previsto, adjudicados

| # | Qué | Dónde | Adjudicación |
|---|---|---|---|
| F0 | `indeterminado/emparejamiento` en B39 (Microsoft) | dos RelatedPerson «Simulado», uno del NK1 (FTH) y otro del GT1 | **juez**: el emparejador del NK1 solo miraba el apellido. Arreglado: desempata la relación NK1-3 (prueba en P-VX-15, roja antes) |
| F0b | B35 (Microsoft) mal atribuido | una sola Immunization con los dos códigos y la fecha del grupo 2 | **juez**: el emparejamiento iba grupo a grupo y el código solo del grupo 1 se llevaba la Immunization antes de que el grupo 2 la encontrara por código y fecha. Arreglado: cada clave para todos los grupos antes de la siguiente (P-VX-13, roja antes). El mecanismo del conversor es MC-VX-15 |
| F1 | Microsoft, `Observation.valueQuantity` sin `unit` (B32, OBX-6 `Cel^^UCUM`) | OBX-6 | **conversor**: la misma regla que en RXA-7 (MC-VX-3). `[CM datatype-cwe-to-quantity] CWE.1 → Quantity.unit IF CWE.2 IS NOT VALUED` |
| F2 | Microsoft, `lotNumber` = `LOT-B16+DIL-B16` (B16) | RXA-15 repetido | **conversor**: concatena las repeticiones con «+». La guía lleva RXA-15 a `lotNumber` (0..1); vale la primera, u otra por convención (Q-VX-D-8), pero no la suma |
| F3 | Microsoft, `Organization.name` = `Merck--Merck S.A.` (B18) | RXA-17 con código alterno | **conversor**: une CE.2 y CE.5 con «--». `[CM datatype-cwe-to-organization] CWE.2 → name` |
| F4 | LinuxForHealth, `isSubpotent: true` con RXA-20 PA (B08) | RXA-20 | **conversor**: la guía solo lleva RXA-20 a `status` (`[G RXA_Immunization.csv:25-26]`); `isSubpotent` no tiene fila. Es `dato_inventado` por la regla de CV §3.0. El texto del hallazgo cita Q-VX-D-7, que habla de «por omisión»: se corrige en VX3 |
| F5 | LinuxForHealth, segunda repetición de RXA-10 perdida (B21) | `performer` | **conversor**: solo escribe el primer XCN. `[CM segment-rxa-to-immunization RXA-10 → performer]` por repetición |
| F6 | LinuxForHealth, `Encounter.status` `unknown` y `class` sin system con PV1-2 R (B38) | PV1 | **conversor**, con las reglas de `adt_conv`. En VX3 se mira si ya está en el estudio de conversores |
| F7 | LinuxForHealth, `manufacturer` perdido de B18 a B40 | RXA-17 | **conversor, estado arrastrado**: tras un mensaje con RXA-17 sin código (B17, `^Laboratorio Sintetico^`), el proceso deja de escribir `manufacturer` en todos los mensajes siguientes. Reproducción mínima: B19 solo sale con fabricante; B17 y luego B19 en el mismo lote, sin él (B18 solo, también con él). El control mensaje a mensaje de las 40 bases (`privado/vx/vx2c/lfh-por-mensaje/`) da el mismo juicio que el lote salvo esos 23 `RXA-17 dato_perdido` |

**Defectos del juez.** Fueron tres. Todos tienen prueba, roja antes del arreglo, y todos se corrigieron en `1ec2b64`:

- los dos emparejamientos, F0 y F0b;
- la huella del juez: `mcp_verificador.FICHEROS` no cubría `conversion_vxu.py` (DV-VX-6).

La previsión sellada lleva la huella de entonces, `ba53dcccbaf5`. El commit `ec37fa7` fija su código. El rejuicio de ADT y ORU sigue
en 0 diferencias.

## Sensibilidad a las decisiones de Jev (las siete de `ALTERNATIVA_VX`)

Se rejuzgaron las 40 evidencias de cada conversor con la alternativa de cada decisión, una a una.

| Q | Alternativa | Microsoft (16 pares hecho-clase) | LinuxForHealth (15) |
|---|---|---|---|
| Q-VX-D-2 | solo la 0550 | igual | igual |
| Q-VX-D-3 | cualquiera | igual | igual |
| Q-VX-D-4 | convención | igual (B30 sigue por el partOf) | igual en mecanismos (B32 sigue); B30 y B31 pasan a nota |
| Q-VX-D-5 | ninguno | 13: salen NK1-3, NK1-5 y NK1-6 | 14: sale NK1-2 |
| Q-VX-D-6 | siempre | igual | igual |
| Q-VX-D-8 | la primera | igual | igual |
| Q-VX-D-9 | dato perdido | igual | igual |

Todas las categorías siguen en 40 `fallo_silencioso`. Solo Q-VX-D-5 mueve la N.

## Las muestras públicas (E-VX-2, con banderas L18)

**Qué se corrió primero.** 83 muestras: 4 de Microsoft y 79 de las pruebas de LinuxForHealth, casi todas 2.5.1 y 2.6. Antes se
corrigieron dos mensajes que la extracción había pegado con el texto de un comentario `//`; está anotado en el manifiesto.

**La re-extracción.** Después, los mensajes de LinuxForHealth se volvieron a extraer de los literales de sus pruebas, con un
lexer que ignora los comentarios. Los dos corregidos a mano coincidieron byte a byte. Uno cambió: `CodeableConceptTest__L101`, un
esqueleto, porque la prueba mete un trozo del mensaje por variable. Y aparecieron dos que faltaban. **LinuxForHealth pasó de 79 a
81 muestras.**

**Lo que vale: las 85** (4 + 81), corridas otra vez con los dos conversores y juzgadas con el juez final (`11a3754fb8b6`):

| | `correcto` | `fallo_silencioso` | `rechazo_incorrecto` | `indeterminado` |
|---|---|---|---|---|
| Microsoft | 33 | 50 | 2 (dos pruebas de LinuxForHealth) | 0 |
| LinuxForHealth | 25 | 58 | 0 | 2 (2,4 %) |

Las tres muestras nuevas o cambiadas salen `correcto` en los dos conversores. La diferencia con la primera corrida (29 / 52 y
23 / 58) se explica por eso y por el `primarySource` deducido de RXA-9, que tras la revisión adversaria pasó a convención (DV-VX-8,
`vx/VX3.md`). Es una inferencia: la suma cuadra, pero los juicios de la primera corrida no se guardaron.

**Los dos indeterminados de LinuxForHealth.** Son de `Hl7ImmunizationFHIRConversionTest__L661` y `Hl7VXUMessageTest__L219`.
Esas muestras traen grupos ORDER idénticos en ORC-3, RXA-3 y RXA-5, porque la prueba comprueba que no se mezclen; nada los
distingue salvo sus OBX. La adjudicación es **corpus**, no juez. Se declara L-VX-14: «dos grupos ORDER iguales en ORC-3, RXA-3 y
RXA-5 no se distinguen: indeterminado/emparejamiento».

**Para VX3.** El contraste de lo que cuenta en las muestras con lo que declaran los proyectos queda para VX3 (la previsión dice
≥ 70 % `ya_declarada`). Dos lecturas quedan pendientes para las muestras:

- `primarySource` con RXA-9 valorado (los CDC), que hoy es `dato_inventado`;
- `statusReason` sin RXA-18 en LinuxForHealth.

## Hecho cuando (§10)

- 0 «fuera de previsto» sin adjudicar.
- Una repetición de VX2-c, de dos posibles.
- Las suites siguen en verde: P-VX-1..23, `prueba_conversion`, `prueba_vc`, `ve/comprobar.sh` (CASA) y el rejuicio a 0.
