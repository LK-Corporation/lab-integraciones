# RESULTADO de la etapa 41: la Observation de PD1-7 en un ORU (8 y 9-nov-2026)

> **El juez empareja con su campo la Observation de PD1-7 también en un ORU; en el rejuicio de lo publicado cambian 0 evidencias.**
>
> - **La hoja de ORU_R01 de la guía también la crea** (`MSG_ORU_R01.csv:17`), como la de ADT_A01. El juez de antes la contaba como
>   inventada en un ORU. Ahora la aparta antes de casar las Observation de los OBX, por el mismo paso que en ADT (etapa 40), y la
>   juzga igual: su valor por la tabla 0315, su status y su sujeto. Si falta, cuenta como recurso ausente.
> - **Dónde la crea la guía:** en su paquete de ConceptMap, once mapas de mensaje la crean desde PD1-7. De los mensajes que el juez
>   juzga, ahora la empareja en los ADT (el mapa de ADT_A01 y los de otros eventos ADT, con la misma fila) y en ORU_R01. En VXU_V04
>   también la crea, y el juez de VXU no la empareja: deja PD1 fuera de su perfil, con una nota (L-VX-3). OML_O21 y ORM_O01 también
>   la crean, y el juez de conversión no tiene punto para esos mensajes.
> - **Ninguna de las 30.118 evidencias guardadas lleva PD1-7.** De las 4.424 de ORU, 69 traen PD1, y en todas PD1-7 viene vacío. Lo
>   nuevo se ve en las pruebas sintéticas.
> - **Las cifras del estudio de conversores no cambian:** 15 nuevas, 31 ya declaradas y 16 convenciones, caso a caso.
> - **La huella del juez publicado** pasa de `6b98df04…` a `20c4f52a…`. En las tres bases de la demostración solo cambia eso; el
>   proyecto de ejemplo y el run en rojo suben su pin en un segundo push.

La pregunta, fijada antes de medir, está en [`ANTES-ETAPA-PD17ORU.md`](ANTES-ETAPA-PD17ORU.md); lo que hizo la etapa 40 en ADT, en
[`RESULTADO-PD17.md`](RESULTADO-PD17.md).

## Cómo se hizo

| | |
|---|---|
| El diseño | A ciegas, por Fable, antes de escribir código: [`po/diseno-po-fable.md`](po/diseno-po-fable.md), con su encargo en [`po/encargo-diseno-po.md`](po/encargo-diseno-po.md) |
| Las decisiones abiertas | Dos, a Jev, con un estado que lleva los hechos de los dos lados y lo que toca cada opción: [`po/estado_po.md`](po/estado_po.md), [`po/decision-jev-po.md`](po/decision-jev-po.md) |
| Las pruebas, en rojo antes | [`po/ROJO-PO.txt`](po/ROJO-PO.txt): con el juez de antes caen 28 comprobaciones de conversión (las 23 de conducta de P-CV-35 y las 5 de P-CV-36), 1 de VXU y 4 de MDM. [`po/ROJO-PO-2.txt`](po/ROJO-PO-2.txt): la prueba del clasificador del rejuicio, antes de que existiera |
| El arreglo | Un parche del juez, [`po/parche_juez_po.py`](po/parche_juez_po.py), sobre `conversion.py` y `mcp_verificador.py`; y uno de las pruebas, [`po/parche_prueba_po.py`](po/parche_prueba_po.py) |
| Las pruebas, probadas | [`po/mutantes_po.py`](po/mutantes_po.py) siembra 28 fallos en el juez, uno por copia: los 18 de la etapa 40, con sus anclas donde quedó el código, y 10 de ORU. `prueba_conversion.py` cae con todos a la primera ([`po/MUTANTES-PO.txt`](po/MUTANTES-PO.txt)) |
| La previsión | Sellada antes de correr el juez nuevo sobre las evidencias: [`po/PREVISION-PO.json`](po/PREVISION-PO.json), con su huella en [`po/SELLO-PO.txt`](po/SELLO-PO.txt). La contó [`po/prever_po.py`](po/prever_po.py) sobre la línea base del juez de antes y los mensajes. Esta vez ninguna prueba rejuzgó evidencias con el juez nuevo antes del sello |
| El rejuicio | Las 30.118 evidencias guardadas, con el juez de antes (el de la etapa 40) y con el nuevo. [`po/rejuicio_po.py`](po/rejuicio_po.py) pone cada diferencia en la conducta de PD1-7 en ORU o «fuera» (con su prueba, [`po/prueba_rejuicio_po.py`](po/prueba_rejuicio_po.py)): [`po/REJUICIO-PO.json`](po/REJUICIO-PO.json) y el registro, [`po/REJUICIO-PO-registro.txt`](po/REJUICIO-PO-registro.txt). Las evidencias no van al repositorio |
| El control del rejuicio | Siete pasadas, cada una con un defecto sembrado en el juez: [`po/CONTROL-PO.json`](po/CONTROL-PO.json), y las reglas que sacan cada evidencia y lo que cambia en ella, [`po/FIRMAS-CONTROL-PO.json`](po/FIRMAS-CONTROL-PO.json) |
| Las clases del estudio | Con el juez de antes y con el nuevo: [`po/CLASES-PO-antes.json`](po/CLASES-PO-antes.json) y [`po/CLASES-PO-despues.json`](po/CLASES-PO-despues.json) |
| La revisión a ciegas | Un lector, en dos pasadas. La primera pidió cambios por una frase falsa sobre la guía (ver «Lo que se vio de paso») y dos menores; la segunda aprobó, con una precisión sobre OML y ORM que está aplicada aquí. Esa precisión y esta fila no las ha visto el lector |
| Las bases de la integración continua | Rehechas con `base_nc.sh`, un guion del laboratorio que llama a [`cv/ci/hacer_bases.py`](cv/ci/hacer_bases.py), y comprobadas contra la previsión con [`po/comprobar_bases_po.py`](po/comprobar_bases_po.py): [`po/BASES-PO.json`](po/BASES-PO.json) |

## Lo que hace el juez ahora en un ORU

**La base:**
- **La guía** crea la misma Observation en ADT_A01 (`MSG_ADT_A01.csv:19`) y en ORU_R01 (`MSG_ORU_R01.csv:17`), «IF PD1-7 VALUED», con
  una sola referencia: su `subject` al Patient del PID. En ORU la fila está dentro de PATIENT, no de ORDER_OBSERVATION, y la hoja no la
  pone en `DiagnosticReport.result`: eso lo hace solo con las Observation de los OBX de cada OBR (`MSG_ORU_R01.csv:67-73`).
- **Su mapa de segmento** tiene un solo elemento, PD1-7 a `valueCodeableConcept` por la tabla 0315, la identidad sobre Y, F, N, I y U.
- **En v2.5,** ORU_R01 lleva `[PD1]` tras el PID, y PD1-7 es un IS con la tabla de usuario 0315 (Ch03.txt:8504, 8630-8643).

**Cómo la reconoce** (`conversion.py`, `emparejar`): antes de casar los DiagnosticReport y las Observation de los OBX, el juez
aparta la de PD1-7 con el mismo paso que en ADT (`_origen_pd17`, ahora llamado desde un ayudante común). Es candidata, con PD1-7
valorado, una Observation sin el código de ningún OBX del mensaje (tampoco de uno fuera de ORDER_OBSERVATION) cuyo
`valueCodeableConcept` lleve el sistema de la 0315 o el código de PD1-7; una sola, la primera con el sistema. Al apartarla antes:
- las Observation de los OBX se casan como antes, porque se casan por el código de OBX-3, y la de PD1-7 no lleva ninguno;
- la de PD1-7 ya no ocupa el hueco que L-CV-7 da a la Observation de un OBX fuera de ORDER_OBSERVATION. Con el juez de antes, si
  el conversor sacaba las dos, una de ellas podía quedarse como inventada.

**Qué juzga de ella:** lo de la etapa 40, por un ayudante común (`_juzgar_pd17`): su valor por la 0315, su status y su sujeto; sin
ella, recurso ausente. Cada hallazgo cita la hoja de su mensaje (en ORU, `[G MSG_ORU_R01.csv:17]`), y en ADT sale lo mismo que antes,
hasta las citas.

**Jev:**
- **Q-PO-1:** si un DiagnosticReport la refiere en `result`, sigue siendo referencia rota del informe, que cuenta, como antes: 0,96
  frente a 0,04 de una nota, con confianza 0,92. La hoja no la pone en `result`, y el perfil del juez dice que `result` lleva
  exactamente las Observation de los OBX de su OBR.
- **Q-PO-2:** las citas, por familia, y no una lista con las dos hojas: 0,90, con confianza 0,8. Así un ADT sale igual byte a byte y
  la huella de `C` no cambia.

Lo ya decidido en la 40 vale tal cual, porque la fila de la hoja es la misma: reconocerla solo por el dato (Q-PD-1) y contar su
ausencia (Q-PD-3). Q-PD-2 y Q-PD-4 son de ACC y PDA, que ORU_R01 no lleva.

**Lo que no hace,** declarado en L-CV-18 y en L-VX-3:
- **VXU.** El mapa de VXU_V04 de la guía también la crea; el juez de VXU deja PD1 fuera de su perfil (L-VX-3), así que no la
  empareja. Ninguna evidencia de VXU lleva PD1-7 valorado: 63 traen PD1, con PD1-7 vacío.
- **Varios PATIENT_RESULT en un ORU:** lee el primer PD1, como el juez ya lee el primer PID.
- **La Observation de un OBX que pierde su código y lleva el valor de PD1-7** pasa por la de PD1-7. Es el mismo riesgo que en ADT.
- **Otro `value[x]`,** como en la 40: no se reconoce.

**Lo que dice de sí mismo:** S-CV-4 nombra ORU; L-CV-18 dice cómo es en `oru_conv` y deja de decir que allí sigue como inventada; el
perfil de la guía para ORU pasa de 16 a 17 filas; y el texto de versión del servidor tiene una entrada de la etapa 41.

## Las pruebas

Del repositorio publicado: `prueba_conversion.py`, 36 pruebas y 209 comprobaciones; `prueba_conversion_vxu.py`, 24 y 158;
`prueba_conversion_mdm.py`, 27 y 276; y `po/prueba_rejuicio_po.py`, 25 comprobaciones.

- **P-CV-35, la conducta en ORU.** Con el juez de antes caen las 23 comprobaciones que no son control:

  | Caso (PD1-7 = F si no se dice otra cosa) | Antes | Ahora |
  |---|---|---|
  | La Observation (v2-0315, F), con uno o con dos OBR | Inventada | Correcto, y de PD1-7 |
  | Referida desde `DiagnosticReport.result` | Inventada y referencia rota del OBR | De PD1-7; la referencia rota del OBR sigue (Q-PO-1) |
  | Sin Observation, en 2.5 y en 2.8 | Correcto | Recurso ausente, con la cita de la hoja de ORU |
  | (v2-0315, Y) | Inventada | Valor distinto |
  | El código F con el sistema de la 0136, o sin sistema | Inventada | Código mal mapeado |
  | PD1-7 = X con el código X | Inventada | Correcto, sin ninguna nota de PD1-7 |
  | PD1-7 = X con (v2-0315, W) | Inventada | Nota de convención en 2.5, de versión en 2.8 |
  | `valueString` F | Inventada | Recurso ausente e inventada |
  | Sin `status`; `subject` a otro Patient; sin `subject` | Inventada | FHIR inválido; referencia rota; dato perdido con la cita de la hoja de ORU |
  | Un OBX con el código F, y las dos Observation | La otra, inventada | La de código F, del OBX; la otra, de PD1-7 |
  | La de un OBX con su código y el valor (v2-0315, F), sin la de PD1-7 | Correcto | Del OBX, y PD1-7 ausente |
  | Un OBX fuera de ORDER_OBSERVATION sin su Observation, y la de PD1-7 | La de PD1-7 en el hueco de L-CV-7 | De PD1-7, sin la nota |
  | Un OBX fuera con su Observation, y la de PD1-7, en los dos órdenes | Una con la nota y la otra inventada | La del OBX con la nota; la otra, de PD1-7 |
  | La del OBX fuera con su código y el valor (v2-0315, F), sin la de PD1-7 | La nota | La nota, y PD1-7 ausente |
  | 2.8, con (v2-0315, F); y con PD1-7 = `F^Living will on file^HL70315` (un CWE) | Inventada | Correcto, y de PD1-7: se lee el primer componente |

  Y un control, igual antes y ahora: con PD1-7 vacío y un OBX con el código F, la de código F es del OBX y nada cuenta.
- **P-CV-36, lo que el juez dice de sí mismo:** el perfil de ORU, las citas por familia, L-CV-18, S-CV-4 y el texto de versión del
  servidor.
- **Las que cambian:** el control de ORU de P-CV-33 pasa a PD1-7 vacío (con PD1-7, es P-CV-35); P-CV-34 busca la entrada de la etapa
  40 donde esté; P-VX-20 y P-MD-24 (el perfil de ORU, de 16 a 17 filas); y P-MD-25 (d), con la huella nueva de `INFO`. La de `C` no
  cambia.
- **Las cifras del rojo son del laboratorio.** Las que caen son las mismas en el repositorio publicado (28, 1 y 4); el total de
  conversión es uno menos allí, porque una comprobación de P-CV-34 solo corre donde está el paquete de la guía.

## El rejuicio

- **0 diferencias en 30.118 evidencias.** Ninguna «fuera», ninguna que falte y ningún punto de entrada que cambie.
- **Cómo se pone una diferencia en la conducta de PD1-7 en ORU** (`po/rejuicio_po.py`). No falla ninguna de cinco reglas, que se
  miran por separado:
  - **R1, el caso:** un ORU cuyo mensaje trae PD1-7 valorado. Un ADT que cambie sale por aquí;
  - **R2, la forma:** sale una Observation inventada o la nota del OBX fuera de ORDER_OBSERVATION; entra una inventada o un hallazgo
    de PD1-7 de los que da el juez; ningún rechazo, ni ninguna nota de OBR;
  - **R3, el valor, y R5, el veredicto:** las de la etapa 40, tal cual;
  - **R4, el libro de las Observation,** por su `fullUrl`: no entra ninguna inventada que no saliera; sale una como mucho; la nota de
    L-CV-7 no entra, y solo sale si el mensaje trae un OBX fuera de ORDER_OBSERVATION.
- **Lo que no mira,** como en la 40: si la Observation que ahora es de PD1-7 lleva de verdad el sistema o el código. Eso lo prueba
  P-CV-35.

**El control** siembra un defecto en el juez, uno por pasada, y toda evidencia con el defecto tiene que salir «fuera»:

| Defecto sembrado | Evidencias con el defecto | Salen «fuera» | Reglas que fallan |
|---|---:|---:|---|
| Recurso ausente de PD1-7 en un ORU sin PD1-7 | 4.378 | 4.378 | R1 y R3 |
| Recurso ausente de PD1-7 con otro valor, en un ORU con PD1 | 69 | 69 | R1 y R3 |
| La Observation de un OBX, sacada de su sitio en un ORU sin PD1-7 | 4.150 | 4.150 | R1, R2 y R4 |
| La de un OBX fuera de ORDER_OBSERVATION, dada por inventada | 53 | 53 | R1 y R4 |
| Un valor distinto en OBX-5 | 4.218 | 4.218 | R1 y R2 |
| Un valor distinto en PID-5 | 23.765 | 23.765 | R1 y R2 |
| Recurso ausente de PD1-7 en un ADT sin PD1-7 | 15.979 | 15.979 | R1 y R3 |

- **Cada defecto lo caza, además de la regla del caso, la que le toca:** el valor (R3), el libro (R4) o la forma (R2).
- **En el corpus no hay PD1-7,** así que R1 falla siempre. R3 y R4 solas, con PD1-7 valorado, las prueba `po/prueba_rejuicio_po.py`.

## Las cifras del estudio de conversores

**La frase no cambia:** 15 nuevas, 31 ya declaradas y 16 convenciones, con 0 hallazgos sin clase. `cv/cv3_clases.py`, con el juez de
antes y con el nuevo, da el mismo JSON salvo la huella del juez.

## Las bases de la integración continua

- **Rehechas con `base_nc.sh`,** con el juez de esta etapa tal como se publica.
- **Las corridas** ([`po/BASES-CI-41.json`](po/BASES-CI-41.json) y [`po/BASES-PO-HECHO.txt`](po/BASES-PO-HECHO.txt)):
  - en el juguete y en LinuxForHealth en lote, dos corridas iguales byte a byte, y la comparación «igual» contra la base;
  - mensaje a mensaje, la primera corrida está en `BASES-CI-41.json`, y la segunda, su `cmp` y su «igual», en `BASES-PO-HECHO.txt`;
  - en el juguete, el defecto sembrado sale en los mismos 344 casos que antes.
- **Lo que cambia, frente a lo sellado** ([`po/BASES-PO.json`](po/BASES-PO.json), contra las bases de antes de la etapa): en las
  tres, la huella del juez, de `6b98df04…` a `20c4f52a…`, y ningún caso. El juguete tiene 390 casos, y LinuxForHealth 458 en lote y
  458 mensaje a mensaje.
- **La comprobación tiene su control.** Siembra cuatro defectos en cada base: un caso que cambia, la huella del corpus que cambia, la
  del juez que no cambia y la del juez que no es la publicada. Cae con cada uno.
- **El proyecto de ejemplo** rehace sus dos bases en el segundo push, con el pin. Lo previsto es que no cambie ningún caso.

## La previsión

| | Previsto | Medido |
|---|---|---|
| Diferencias | 0: ningún ORU lleva PD1-7, y en ADT el código es el mismo | 0 |
| Fuera, faltan, punto que cambia | 0 | 0 |
| El control | Toda evidencia con el defecto, «fuera» | Así, en las siete pasadas |
| Recurso ausente en un ORU sin PD1-7 | Más de 0, y como mucho 4.424 | 4.378 |
| Con otro valor, en un ORU con PD1 | Como mucho 69 | 69 |
| La de un OBX, fuera de su sitio | Más de 0, y como mucho 4.347 (los ORU con un OBX en ORDER_OBSERVATION) | 4.150 |
| La de L-CV-7, dada por inventada | 53 | 53 |
| PID-5 / recurso ausente en un ADT | 23.765 / 15.979 | 23.765 / 15.979 |
| Las clases | Iguales caso a caso, salvo la huella | Lo mismo |
| Las bases | Solo la huella del juez; en el juguete, 344 casos con el defecto | Lo mismo |

## Lo que cambia en lo publicado

- **El juez y sus pruebas,** con la huella nueva.
- **Las tres bases de la demostración,** aquí. En un segundo push, las dos del proyecto de ejemplo y su pin.
- **`cv/ci/CI.md`** nombra la etapa 41 junto a la 40 como ejemplo de juez que cambia sin cambiar ningún caso.
- **La tabla «Correrlo» del README de `verificador/`,** con la cifra nueva de `prueba_conversion.py`.
- **Lo que no cambia:** los resultados sellados de etapas pasadas y sus JSON, `cv/cv3_clases.py` y `cv/CLASES-CV3.json`. En el
  laboratorio, ninguna línea base privada: P-MD-25 (b) y (c) siguen pasando sin rehacer nada, porque ningún límite es nuevo (L-CV-18
  cambia de texto, y la base de los informes guarda qué límites hay, no su texto).

## Lo que se vio de paso

- **El ANTES dice algo falso en su punto de partida:** que las únicas hojas de la guía con esa fila son las de ADT_A01 y ORU_R01. Se
  midió en las hojas CSV del laboratorio, que solo traen esos dos mensajes; el paquete de ConceptMap de la guía la crea en once
  mapas de mensaje. Lo vio la revisión a ciegas. El ANTES va literal, y la nota de su primera línea lo dice; la pregunta y la
  etapa no cambian, porque eran de ORU.
- **El diseño vio un efecto del juez de antes** que la pregunta no nombraba: la Observation de PD1-7 ocupaba el hueco de L-CV-7 y
  podía dejar como inventada la de un OBX fuera de ORDER_OBSERVATION. Lo arregla el mismo paso.
- **El guion de los mutantes de la 40 deja de aplicar** al juez nuevo, porque sus anclas se movieron a los ayudantes. No se toca:
  es un sello de la 40. `po/mutantes_po.py` lleva sus 18 con las anclas nuevas.
- **`ve/escanear_caja.py`,** el escáner de cajas de diseñador del laboratorio, falla por un cambio de firma en la guarda. No se usa en
  esta etapa: la preparación y la guarda revisan lo que se publica.
