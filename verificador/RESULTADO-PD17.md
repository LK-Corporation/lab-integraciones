# RESULTADO de la etapa 40: la Observation de PD1-7 en el juez (8-nov-2026)

> **El juez empareja con su campo la Observation de PD1-7; en el rejuicio de lo publicado cambian 0 evidencias.**
>
> - **En un ADT con PD1-7,** la guía crea una Observation desde ese campo (`MSG_ADT_A01.csv:19`). El juez de antes la tomaba por la
>   de un OBX, por orden, y sin OBX la contaba como inventada. Ahora la reconoce por su valor y la juzga como la de PD1-7: su valor
>   por la tabla 0315, su status y su sujeto. Si falta, cuenta como recurso ausente.
> - **Ninguna de las 30.118 evidencias guardadas lleva PD1-7.** 5.655 de ADT traen PD1, y en todas PD1-7 viene vacío. Por eso no
>   cambia ninguna, y lo nuevo se ve en las pruebas sintéticas.
> - **Las cifras del estudio de conversores no cambian:** 15 nuevas, 31 ya declaradas y 16 convenciones, caso a caso.
> - **La huella del juez publicado** pasa de `4a75a245…` a `6b98df04…`. En las tres bases de la demostración solo cambia eso; el
>   proyecto de ejemplo y el run en rojo suben su pin en un segundo push.

La pregunta, fijada antes de medir, está en [`ANTES-ETAPA-PD17.md`](ANTES-ETAPA-PD17.md).

## Cómo se hizo

| | |
|---|---|
| El diseño | A ciegas, por Fable, antes de escribir código: [`pd/diseno-pd-fable.md`](pd/diseno-pd-fable.md), con su encargo en [`pd/encargo-diseno-pd.md`](pd/encargo-diseno-pd.md) |
| Las decisiones abiertas | Cuatro, a Jev, con estados que llevan los hechos de los dos lados: tres del arreglo ([`pd/estado_pd.md`](pd/estado_pd.md), [`pd/decision-jev-pd.md`](pd/decision-jev-pd.md)) y una de después de la primera pasada de la revisión a ciegas, que se repreguntó porque su primer estado tenía un hecho falso ([`pd/estado_pd2.md`](pd/estado_pd2.md), [`pd/decision-jev-pd2.md`](pd/decision-jev-pd2.md); [`pd/estado_pd2b.md`](pd/estado_pd2b.md), [`pd/decision-jev-pd2b.md`](pd/decision-jev-pd2b.md)) |
| Las pruebas, en rojo antes | [`pd/ROJO-PD.txt`](pd/ROJO-PD.txt): con el juez de antes caen 29 comprobaciones de conversión, 1 de VXU y 4 de MDM. [`pd/ROJO-PD-2.txt`](pd/ROJO-PD-2.txt): la prueba del clasificador del rejuicio, antes de que existiera. [`pd/ROJO-PD-3.txt`](pd/ROJO-PD-3.txt): las de conversión con el segundo parche, contra el juez de antes (caen 30). [`pd/ROJO-PD-4.txt`](pd/ROJO-PD-4.txt): las del caso de Q-PD-4, contra el juez de antes de su texto (caen 1 de conversión y 2 de MDM) |
| El arreglo | Dos parches del juez: [`pd/parche_juez_pd.py`](pd/parche_juez_pd.py), sobre `conversion.py`, `mcp_verificador.py` y `cv/extraer_mapas.py`, y [`pd/parche_juez_pd_2.py`](pd/parche_juez_pd_2.py), que solo cambia el texto de L-CV-18 (Q-PD-4). Y tres de las pruebas: [`pd/parche_prueba_pd.py`](pd/parche_prueba_pd.py), [`pd/parche_prueba_pd_2.py`](pd/parche_prueba_pd_2.py) y [`pd/parche_prueba_pd_3.py`](pd/parche_prueba_pd_3.py) |
| Las pruebas, probadas | [`pd/mutantes_pd.py`](pd/mutantes_pd.py) siembra 18 fallos en el arreglo, uno por copia del juez, y `prueba_conversion.py` tiene que caer con cada uno. Con el primer parche de las pruebas vivían 2 ([`pd/MUTANTES-PD.txt`](pd/MUTANTES-PD.txt)); el segundo los mata ([`pd/MUTANTES-PD-2.txt`](pd/MUTANTES-PD-2.txt)) |
| La previsión | Sellada antes de correr el juez nuevo sobre las evidencias: [`pd/PREVISION-PD.json`](pd/PREVISION-PD.json), con su huella en [`pd/SELLO-PD.txt`](pd/SELLO-PD.txt). La contó [`pd/prever_pd.py`](pd/prever_pd.py) sobre la línea base del juez de antes y los mensajes |
| El rejuicio | Las 30.118 evidencias guardadas, con el juez de antes y con el nuevo. [`pd/rejuicio_pd.py`](pd/rejuicio_pd.py) pone cada diferencia en la conducta de PD1-7 o «fuera» (con su prueba, [`pd/prueba_rejuicio_pd.py`](pd/prueba_rejuicio_pd.py)): [`pd/REJUICIO-PD.json`](pd/REJUICIO-PD.json) y el registro de la corrida, [`pd/REJUICIO-PD-registro.txt`](pd/REJUICIO-PD-registro.txt); con el juez final, tras el segundo parche, [`pd/REJUICIO-PD-2.json`](pd/REJUICIO-PD-2.json) y [`pd/REJUICIO-PD-2-registro.txt`](pd/REJUICIO-PD-2-registro.txt). Las evidencias no van al repositorio |
| El control del rejuicio | Seis pasadas, cada una con un defecto sembrado en el juez: [`pd/CONTROL-PD.json`](pd/CONTROL-PD.json), y las reglas que sacan cada evidencia y lo que cambia en ella, [`pd/FIRMAS-CONTROL-PD.json`](pd/FIRMAS-CONTROL-PD.json) |
| Las clases del estudio | Con el juez de antes y con el final: [`pd/CLASES-PD-antes.json`](pd/CLASES-PD-antes.json) y [`pd/CLASES-PD-despues.json`](pd/CLASES-PD-despues.json) |
| La revisión a ciegas | Un lector, en dos pasadas. La primera aprobó con cuatro menores y ningún bloqueante: un caso sin declarar, que fue a Jev (Q-PD-4); una comprobación de P-CV-33 que no cazaba una nota de más, la misma que había dejado vivo un mutante; y dos frases de este resultado. La segunda aprobó con un menor, este hueco sin rellenar, y dos nimiedades: con qué juez corrieron el control y los informes, que ahora se dice, y dos cifras viejas de la tabla «Correrlo» del README de `verificador/`, que se pusieron al día. Lo de la segunda está aplicado aquí, y el lector no lo ha visto |
| Las bases de la integración continua | Rehechas con `base_nc.sh`, un guion del laboratorio que llama a [`cv/ci/hacer_bases.py`](cv/ci/hacer_bases.py), y comprobadas contra la previsión con [`pd/comprobar_bases_pd.py`](pd/comprobar_bases_pd.py): [`pd/BASES-PD.json`](pd/BASES-PD.json) |

## Lo que hace el juez ahora

**La base:**
- **La guía,** en la hoja de ADT_A01, crea `Observation[1]` desde PD1 «IF PD1-7 VALUED» (`MSG_ADT_A01.csv:19`). Su mapa de
  segmento tiene un solo elemento: PD1-7 a `valueCodeableConcept`, por la tabla 0315. Ese mapa es la identidad sobre Y, F, N, I y U,
  con el sistema `http://terminology.hl7.org/CodeSystem/v2-0315`. No fija `Observation.code` ni nada más.
- **En v2.5,** PD1-7 (Living Will Code) es un IS con la tabla de usuario 0315 (Ch03.txt:8504, 8630-8643).
- **FHIR R4** pide `Observation.status` (1..1, required).

**Cómo la reconoce** (`conversion.py`, `_origen_pd17` y `emparejar`; solo en ADT y con PD1-7 valorado):
1. una Observation con el código de un OBX del mensaje es la de ese OBX, como antes;
2. si no, es candidata si su `valueCodeableConcept` lleva un coding con el sistema de la 0315 o con el código de PD1-7. Es una
   sola: la primera con el sistema, y si ninguna lo lleva, la primera del Bundle. Entra en el emparejamiento con el rol
   `Observation#PD1`;
3. si no, la regla de ACC y PDA de la etapa 37 (L-CV-17), como antes;
4. si no, la de un OBX o inventada, por orden, como antes.

Con PD1-7 vacío, el paso 2 no existe.

**Qué juzga de ella** (`_livingwill`; el hecho es siempre PD1-7):

| Lo que hay | El juez | Cuenta |
|---|---|---|
| PD1-7 valorado y ninguna Observation reconocida | Recurso ausente, con la cita de la hoja | Sí, en toda versión |
| Un coding con el sistema de la 0315 y el valor de PD1-7 | Nada | |
| El código de PD1-7 con otro sistema, o sin sistema | Código mal mapeado | Sí |
| El sistema de la 0315 con otro código, y PD1-7 dentro de la 0315 | Valor distinto | Sí |
| PD1-7 fuera de la 0315 (es una tabla de usuario) y el mismo código | Nada | |
| PD1-7 fuera de la 0315 y otro código | Nota de convención; con MSH-12 distinto de 2.5, de versión | No |
| `status` ausente o fuera de `observation-status` | FHIR inválido | Sí |
| `subject` | Como el de las demás: si falta, dato perdido; si no resuelve al Patient del PID, referencia rota; una referencia lógica por su identifier, nota de convención | Sí, salvo la nota |
| `code`, `effective[x]` y lo demás | No se juzga: el mapa no lo fija | |

**Jev:**
- **Q-PD-1:** reconocerla solo por el dato, no por eliminación, 0,95, con confianza 0,9.
- **Q-PD-2:** con PD1-7 en Y o N y ACC o PDA con ese valor, una Observation de solo Y/N sin sistema es la de PD1-7, 0,69 frente a
  0,31 de dejarla como antes, con confianza 0,38.
- **Q-PD-3:** sin ella, recurso ausente que cuenta, 0,94 frente a 0,06 de una nota, con confianza 0,88.
- **Q-PD-4,** después de la primera pasada de la revisión a ciegas: con PD1-7 en Y o N y ACC o PDA con ese valor, una sola
  Observation de solo Y/N con el sistema de la 0136 es la de PD1-7, con código mal mapeado, como ya hacía el juez, y se declara en
  L-CV-18 y aquí. La primera vez el estado decía que declararlo en L-CV-18 no cambiaba la huella del juez, y la cambia; con eso
  corregido, 0,64 frente a 0,35 de declararlo solo aquí y 0,01 de darla a ACC o PDA, con confianza 0,46.

**Lo que no hace,** declarado en el límite nuevo L-CV-18:
- **ORU.** La hoja de ORU_R01 también la crea (`MSG_ORU_R01.csv:17`); en `oru_conv` sigue como inventada. VXU no se toca.
- **Otro `value[x]`.** Una Observation con el dato de PD1-7 en `valueString` o `valueBoolean` no se reconoce: sale recurso ausente
  de PD1-7, y la Observation sigue los pasos de siempre.
- **Con PD1-7 en Y o N y ACC o PDA con ese valor,** una Observation de solo Y/N sin el sistema de la 0315 (sin sistema, o con el
  de la 0136) es la de PD1-7, con código mal mapeado, y no de ACC o PDA (Q-PD-2 y Q-PD-4). Si hay dos así, la primera; la otra
  sigue la regla de la 0136. El juez no tiene con qué separarlas mejor.
- **La lectura de los tipos de 2.6 y posteriores:** toma el primer componente de PD1-7, que en v2.5 es el campo entero.

**Lo que dice de sí mismo:** S-CV-4 nombra la Observation de PD1-7; L-CV-17 acota a PD1-7 en su primer riesgo (queda «una
inventada, o la de PD1-7 cuando el conversor no la saca como `valueCodeableConcept`»); L-CV-18 es nuevo; el perfil de la guía para
ADT pasa de 22 a 23 filas; la 0315 entra en los mapas del juez, igual que en el paquete de la guía; y el texto de versión del servidor
tiene una entrada de la etapa 40.

## Las pruebas

Del repositorio publicado: `prueba_conversion.py`, 34 pruebas y 180 comprobaciones; `prueba_conversion_vxu.py`, 24 y 158;
`prueba_conversion_mdm.py`, 27 y 276; y `pd/prueba_rejuicio_pd.py`, 33 comprobaciones.

- **P-CV-33, la conducta.** Con el juez de antes caen las 23 comprobaciones que no son control:

  | Caso (PD1-7 = F si no se dice otra cosa) | Antes | Ahora |
  |---|---|---|
  | La Observation, sin OBX | Inventada | Correcto, y de PD1-7 |
  | Con OBX y las dos Observation, en los dos órdenes | Una inventada | Correcto, con la nota del OBX |
  | Con OBX y solo la de PD1-7 | La tomaba por la del OBX | Correcto, y de PD1-7 |
  | Sin Observation, en 2.5 y en 2.8 | Correcto | Recurso ausente |
  | El código F con el sistema de la 0136, o sin sistema | Inventada | Código mal mapeado |
  | (v2-0315, Y) | Inventada | Valor distinto |
  | PD1-7 = X, con el código X | Inventada | Correcto, sin ninguna nota de PD1-7 |
  | PD1-7 = X, con (v2-0315, W) | Inventada | Nota de convención en 2.5, de versión en 2.8 |
  | PD1-7 = Y y ACC-5 = Y, con (v2-0315, Y), sola o con otra de la 0136 en los dos órdenes | Sin mapa, de ACC | La de la 0315, de PD1-7; la otra, de ACC |
  | PD1-7 = Y y ACC-5 = Y, dos de solo Y sin sistema | Sin mapa, de ACC | La primera, de PD1-7, con código mal mapeado; la segunda, de ACC |
  | PD1-7 = Y y ACC-5 = Y, una sola (v2-0136, Y) | Sin mapa, de ACC | De PD1-7, con código mal mapeado (Q-PD-4) |
  | Con el código del OBX y el valor F | La del OBX | La del OBX, y PD1-7 ausente |
  | `valueString` F | Inventada | Recurso ausente e inventada |
  | Sin `status` | Inventada | FHIR inválido |
  | `subject` a otro Patient | Inventada | Referencia rota |
  | 2.8, con (v2-0315, F) | Inventada | Correcto, y de PD1-7 |
  | 2.8, con PD1-7 = `F^Living will on file^HL70315` (un CWE) y (v2-0315, F) | Inventada | Correcto, y de PD1-7: se lee el primer componente |

  Y cuatro controles, iguales antes y ahora: con OBX y solo la de PD1-7 no cuenta nada; PD1-7 vacío, ACC-5 = Y y una de solo Y es
  de ACC; un PD1 sin PD1-7 deja la Observation como inventada; y en un ORU con PD1 sigue inventada.
- **P-CV-34, lo que el juez dice de sí mismo:** el perfil, `C["PD1-7"]`, L-CV-18 (con el caso de Q-PD-4), S-CV-4, el mapa de la
  0315 y el texto de versión del servidor. Donde está el paquete de la guía, que no se publica, compara además el mapa de la 0315 con él.
- **Las que cambian:** P-CV-32 (L-CV-17 acota a PD1-7 en su primer riesgo, y la entrada de la 37 deja de ser la primera del texto de
  versión), P-VX-20 y P-MD-24 (el perfil de ADT, de 22 a 23 filas) y P-MD-25 (d), con las huellas nuevas de `C`, `INFO` y `MAPAS`.
- **Las cifras del rojo son del laboratorio:** caen 29 de conversión porque allí está el paquete de la guía; en el repositorio
  publicado serían 28. Con el segundo parche, 30 y 29. Con el tercero, contra el juez de antes de su texto, caen la comprobación
  de L-CV-18 y la huella de la información (P-MD-25 d); la de P-CV-33 del caso de Q-PD-4 ya pasaba, porque fija lo que el juez ya
  hacía.
- **Los mutantes.** Con el primer parche de las pruebas sobrevivían dos fallos del juez: una nota de convención de PD1-7 cuando el
  código es el mismo, que no cuenta, y leer PD1-7 entero en vez de su primer componente, que con los valores de las pruebas daba
  lo mismo. El segundo parche añade una comprobación para cada uno, y mueren los 18.

## El rejuicio

- **0 diferencias en 30.118 evidencias.** Ninguna «fuera», ninguna que falte y ningún punto de entrada que cambie. Con el juez
  final, tras el texto de Q-PD-4, lo mismo.
- **Cómo se pone una diferencia en la conducta de PD1-7** (`pd/rejuicio_pd.py`). No falla ninguna de cinco reglas, que se miran por
  separado:
  - **R1, el caso:** un ADT cuyo mensaje trae PD1-7 valorado;
  - **R2, la forma:** sale una Observation inventada, una sin mapa de ACC o PDA, o la nota del OBX; entra eso mismo o un hallazgo de
    PD1-7 de los que da el juez nuevo; ningún rechazo;
  - **R3, el valor:** los hallazgos de PD1-7 que entran citan el valor de PD1-7 del mensaje, y la nota es de convención en 2.5 y de
    versión en otra;
  - **R4, el libro de las Observation,** por su `fullUrl`: las que entran estaban entre las que salen, con el mismo subtipo; salen,
    sin volver, una como mucho, o dos si hay OBX y la nota del OBX está; y cada sin mapa que entra cita un dato del mensaje;
  - **R5, el veredicto:** los recuentos no cambian, y el veredicto solo pasa entre correcto y fallo silencioso convertido.
- **Lo que no mira:** si la Observation que ahora es de PD1-7 lleva de verdad el sistema de la 0315 o el código de PD1-7. No ve el
  Bundle; eso lo prueba P-CV-33.

**El control** siembra un defecto en el juez, uno por pasada, y toda evidencia con el defecto tiene que salir «fuera». Son los cinco
del diseño, el último en dos campos:

| Defecto sembrado | Evidencias con el defecto | Salen «fuera» | Reglas que fallan |
|---|---:|---:|---|
| Recurso ausente de PD1-7 en un ADT sin PD1-7 | 15.979 | 15.979 | R1 y R3 |
| La Observation de ACC o PDA, dada por inventada | 161 | 161 | R1 y R4 |
| La de un OBX, sacada de su sitio en un ADT sin PD1-7 | 1.513 | 1.513 | R1 y R4 |
| Recurso ausente de PD1-7 con otro valor, en un ADT con PD1 | 3.658 | 3.658 | R1 y R3 |
| Un valor distinto en PID-5 | 23.765 | 23.765 | R1 y R2 |
| Un valor distinto en PID-8 | 23.765 | 23.765 | R1 y R2 |

- **Cada defecto lo caza, además de la regla del caso, la que le toca:** el valor (R3), el libro (R4) o la forma (R2).
- **En el corpus no hay PD1-7,** así que R1 falla siempre. R3 y R4 solas, con PD1-7 valorado, las prueba
  `pd/prueba_rejuicio_pd.py`.
- **El control corrió con el juez de antes del texto de Q-PD-4** (`d153f791…`). Entre ese y el final solo cambia el texto de
  L-CV-18, que ni el juez ni el clasificador leen al juzgar; el rejuicio con el final dio lo mismo.

## Las cifras del estudio de conversores

**La frase no cambia:** 15 nuevas, 31 ya declaradas y 16 convenciones, con 0 hallazgos sin clase. `cv/cv3_clases.py`, con el juez de
antes y con el final, da el mismo JSON salvo la huella del juez. Ningún hallazgo de PD1-7 tiene clase, y no hay ninguno.

## Las bases de la integración continua

- **Rehechas con `base_nc.sh`, dos veces:** con el juez de antes de la revisión a ciegas (huella `ce09708f…`) y con el final
  (`6b98df04…`). Entre una y otra solo cambia la huella del juez. Lo de abajo es de la segunda.
- **Las corridas** ([`pd/BASES-CI-40.json`](pd/BASES-CI-40.json) y [`pd/BASES-PD-HECHO.txt`](pd/BASES-PD-HECHO.txt)):
  - en el juguete y en LinuxForHealth en lote, dos corridas iguales byte a byte, y la comparación «igual» contra la base;
  - mensaje a mensaje, la primera corrida está en `BASES-CI-40.json`, y la segunda, su `cmp` y su «igual», en `BASES-PD-HECHO.txt`;
  - en el juguete, el defecto sembrado sale en los mismos 344 casos que antes.
- **Lo que cambia, frente a lo sellado** ([`pd/BASES-PD.json`](pd/BASES-PD.json), contra las bases de antes de la etapa): en las
  tres, la huella del juez, de `4a75a245…` a `6b98df04…`, y ningún caso. El juguete tiene 390 casos, y LinuxForHealth 458 en lote y
  458 mensaje a mensaje.
- **La comprobación tiene su control.** Siembra cuatro defectos en cada base: un caso que cambia, la huella del corpus que cambia, la
  del juez que no cambia y la del juez que no es la publicada. Cae con cada uno.
- **El proyecto de ejemplo** rehace sus dos bases en el segundo push, con el pin. Lo previsto es que no cambie ningún caso.

## La previsión

| | Previsto | Medido |
|---|---|---|
| Diferencias | 0: ningún ADT lleva PD1-7 | 0 |
| Fuera, faltan, punto que cambia | 0 | 0 |
| El control | Toda evidencia con el defecto, «fuera» | Así, en las seis pasadas |
| ACC o PDA dada por inventada | 161 | 161 |
| La de un OBX, fuera de su sitio | 1.513 | 1.513 |
| Recurso ausente en un ADT sin PD1-7 | Más de 0, y como mucho 21.553 | 15.979 |
| Con otro valor, en un ADT con PD1 | Como mucho 5.655 | 3.658 |
| Las clases | Iguales caso a caso, salvo la huella | Lo mismo |
| Las bases | Solo la huella del juez; en el juguete, 344 casos con el defecto | Lo mismo |

**Declarado en el sello:** antes de sellar, al poner en verde las pruebas, P-MD-25 (b) ya había rejuzgado con el juez nuevo las
evidencias de su línea base, 14 carpetas, y había pasado. La previsión de 0 diferencias no fue ciega para esas carpetas; se apoyaba en
el recuento de PD1-7, que no depende del juez.

## Lo que cambia en lo publicado

- **El juez y sus pruebas,** con la huella nueva.
- **Las tres bases de la demostración,** aquí. En un segundo push, las dos del proyecto de ejemplo y su pin.
- **`cv/ci/CI.md`** nombra la etapa 40 como ejemplo de juez que cambia sin cambiar ningún caso.
- **Lo que no cambia:** los resultados sellados de etapas pasadas y sus JSON, `cv/cv3_clases.py` y `cv/CLASES-CV3.json`.
- **En el laboratorio,** la base de los informes de P-MD-25 (c) se rehizo con el juez nuevo
  ([`pd/INFORMES-PD.txt`](pd/INFORMES-PD.txt)). En sus 137 corridas solo cambia la lista de límites, que gana L-CV-18; el juicio,
  igual. Se rehízo con el juez de antes del texto de Q-PD-4; con el final, P-MD-25 (c) sigue pasando, porque los informes llevan
  qué límites hay y no su texto. Las demás líneas base privadas no cambian.

## Lo que se vio de paso

- **El diseño se contradecía en un caso.** Para dos Observation de solo Y sin sistema, con PD1-7 = Y y ACC-5 = Y, su lista de
  pruebas decía que solo contaría la de ACC. Su tabla de lo que juzga dice que un código sin sistema es código mal mapeado. La
  prueba sigue a la tabla: cuentan las dos.
- **Un caso que no se decidió al principio.** La revisión a ciegas vio que una sola Observation de solo Y/N con el sistema de la
  0136 se da por la de PD1-7 cuando ACC o PDA traen ese valor. El estado de Q-PD-2 decía que el sistema las separa si el conversor
  lo pone, y eso solo es cierto cuando están las dos. Fue a Jev como Q-PD-4.
- **Un PD1-7 que repite** (`F~Y`, que un IS de v2.5 no admite): el juez lo lee entero y da una nota de convención, y el
  clasificador del rejuicio lee `F`. El mensaje no es válido, y ninguna evidencia lo trae.
- **El clasificador es más estricto que el diseño en dos cosas.** Admite una lista cerrada de hallazgos de PD1-7, los que da el
  juez nuevo, y no cualquiera; y un recurso ausente de PD1-7 no puede entrar con otro hallazgo de PD1-7.
