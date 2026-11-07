# RESULTADO de la etapa 33: los generadores del corpus, arreglados (5-nov-2026)

**Completado el 7-nov (etapa 36):** de las 2 candidatas que este resultado deja sin confirmar, ninguna es nueva. La de
Microsoft es M-28, una de las 31 ya declaradas, que el estudio ya contaba en las muestras de Microsoft; la de LinuxForHealth es
una convención ([`RESULTADO-CANDIDATAS.md`](RESULTADO-CANDIDATAS.md)). Las cifras de abajo no cambian.

> **De los 767 mensajes de la versión 2 del corpus, 392 son válidos en v2.5, 16 inválidos (todos a propósito o fragmentos del
> estándar) y 359 sin decidir.** Los sin decidir son estos:
> - 206 por TXA-3: 200 con `TEXT` y 6 con `multipart` (B17, en T02 y en sus cinco eventos);
> - 141 solo por la tabla 0396 (UCUM y SCT);
> - 8 por MSH-12 = 2.5.1, a propósito;
> - 4 por otras causas.
>
> **De las 27 nuevas publicadas, 25 salen en algún mensaje válido:**
> - 11 en casos de su clase y 1 en su par mínimo;
> - 12 en su gemelo con ISO+;
> - 1, MD-M5, en un gemelo de su par con contenido que no es texto, hecho para esto y fuera de los 767.
>
> Las otras 2, MD-L3 y MD-L5, tratan del contenido de texto de MDM. Para el texto, ningún valor de TXA-3 de v2.5 cabe en su
> longitud.
>
> **En la línea de los conversores, las nuevas, las ya declaradas y las convenciones no cambian** (15, 31 y 16), y los mensajes del
> estudio pasan de 368 a 375.
> - Desaparece M-11, un rechazo de Microsoft que el estudio había apartado como defecto del corpus. Lo causaba un error de tipo
>   del generador, y Microsoft convierte ahora esos 30 mensajes.
> - 10 clases ya declaradas ganan casos.
> - Aparecen 2 candidatas, sin confirmar (la etapa 36: M-28, ya declarada, y una convención).

| | |
|---|---|
| La pregunta | `ANTES-ETAPA-GENERADORES.md`, fijada antes de diseñar |
| Las decisiones | Jev: siete de alcance (`ga/decision-jev-ga.md` y `ga2`) y once del diseño (`ga/decision-jev-gad.md` y `gad2`) |
| El diseño | Fable, a ciegas de conversores, juez y resultados (`ga/diseno-ga-fable.md`, encargo en `ga/encargo-diseno-ga.md`) |
| El sello | `ga/SELLO-GA.txt`: el bloque 1, antes de pasar la versión 2 por IRIS; el 2, antes de correr los conversores sobre ella; el 3, después; el 4, el 5 y el 6, lo que cambió después del 3, tras la segunda pasada de la revisión y tras el segundo lector, cada fichero con su razón; el 7, desde la etapa 36, la descripción de M-28 corregida en `cv/cv3_clases.py` |
| El juez | El de hoy, el mismo en las dos versiones |
| Los conversores | Los dos del estudio, con sus adaptadores fijados (`cv/adaptadores/microsoft.json` y `linuxforhealth.json`), en su caja |

## Lo que cambia en el corpus: la versión 2

La versión 1 no cambia ni un byte: sus 18 ficheros son los del commit anterior a la etapa (`ga/SOLO-CAMBIA-ESTO.json`). La versión 2
va al lado, en `ga/`. La herramienta la usa por omisión (`--version-corpus 2`), y lo sellado sigue leyendo la 1 (Q-GA-4). La función
que junta el corpus sigue en la 1 por omisión (P10).

| Qué | Mensajes | Qué cambia |
|---|---|---|
| **El generador de ADT** (GENADT), familias `completo`, `nulos` y `opcionales` | 72 de 216 | Los segmentos opcionales llevan sus obligatorios (ROL-2 = `UC`, OBX-11, DG1-1 y DG1-6, PR1-5, NK1-1, AL1-1, GT1-1 y GT1-3), y cada valor es de su tipo: GT1-2 un CX (llevaba un nombre), GT1-3 el nombre, UB1-2 un número, ACC-1 y PR1-5 una fecha, y PV1-37 un DLD de dos componentes. Los dos campos «(B) R» se valoran: DG1-2 = `I9` y PR1-2 = `L` (llevaba `PR1`). En `nulos`, ningún `""` cae en un campo obligatorio: el nulo pasa a un campo opcional del mismo segmento, y los obligatorios de ROL, OBX, AL1, DB1, DG1 y GT1 reciben valor. La lista entera de lo que cambia, por familia y campo, está en `ga/SOLO-CAMBIA-ESTO.json` |
| **Las bases A1** | 8 de 40 | `María`, con tilde y MSH-18 vacío, pasa a `Maria`. Lo que A1 hace a propósito se queda |
| **El capítulo 3** | +7 | Los 7 fragmentos del estándar se quedan como están; cada uno lleva una copia completada con lo mínimo que le falta |
| **MDM, B36** | 1 base y sus 5 eventos | TXA-12 cabe en su LEN 30 (`DOC0036^CSSYN^2.999^ISO`) y conserva EI.2 a EI.4 |
| **Los gemelos** | +37 | Los 23 mensajes que sostienen las 12 nuevas sin apoyo decidible, y sus 14 controles, con el sistema de unidades en ISO+ y MSH-10 con «-ISO» |

**Cómo se comprueba:** `ga/solo_cambia_esto.py` da TODO BIEN.
- En GENADT, cada campo distinto está en la lista del diseño y se usan todos. El azar se llama las mismas veces en las dos
  versiones (8.803).
- En A1, solo cambia PID-5 de la familia de contactos.
- Los fragmentos son idénticos, y cada copia los contiene.
- En MDM solo cambia B36, en TXA-12.
- Cada gemelo solo difiere de su origen en el componente 3 de OBX-6 o RXA-7 y en MSH-10.

**Lo que no cambia:**
- **Los valores válidos pero fuera de los sugeridos de una tabla de usuario** (EVN-4 = `00`, PL.6 = `A`, NK1-3 = `SPOUSE`, …). Van
  anotados (P1, DV-GA-1).
- **La disposición de PL en PV1-3** (P2).
- **UCUM en las bases de ORU y VXU** (Q-GA-2).
- **TXA-3 = `TEXT` en los documentos de texto.** No tiene arreglo en v2.5:
  - el campo es obligatorio cuando hay OBX y su LEN es 2;
  - para el texto, la 0191 da `TEXT`, que no cabe, y `TX` y `FT`, «HL7 V2.2 only» (CH09.txt:825, 888-903).

  Para otro contenido sí hay valores que caben: `AP`, `AU` e `IM`. Con ellos, 8 bases de MDM con OBX ED o RP son válidas.
- **TXA-3 = `multipart` en B17,** un CDA como ED. Tampoco cabe en el LEN 2, y se queda: es lo que esa base prueba.

**La lista del corpus** (`ga/LISTA-CORPUS-V2.jsonl`, 767 filas) lleva el origen de cada mensaje y estas marcas:
- **inválido a propósito**, con su razón: S95, S90, S22 y MSH-12 en A1, y L17, el par de L-25 y M-35;
- **fragmento del estándar,** con su línea, y **copia completada**;
- **gemelo** de otro mensaje;
- **avisos y errores conocidos** del comprobador de tipos.

Su guarda da TODO BIEN: todo inválido y todo error lleva marca, y toda marca a propósito corresponde a un hallazgo.

## La validación de la versión 2

Con el aparato sellado de la etapa 30 (`iv/validar_iv.py` e `iv/lectura_iv.py`), sin tocarlo. Las cifras están en
`ga/CIFRAS-GA-A.json`.

| Corpus | Mensajes | Válidos | Inválidos | Sin decidir |
|---|---|---|---|---|
| ADT de la herramienta | 270 | 246 | 15 | 9 |
| ORU de la herramienta | 40 | 11 | 0 | 29 |
| VXU de la herramienta | 40 | 3 | 0 | 37 |
| MDM_T02 de la herramienta | 40 | 8 | 0 | 32 |
| Pares mínimos del estudio de conversores | 68 | 43 | 1 | 24 |
| Pares de VXU | 50 | 0 | 0 | 50 |
| Pares de MDM | 14 | 0 | 0 | 14 |
| Bases de MDM en sus cinco eventos | 200 | 40 | 0 | 160 |
| Pares de la auditoría | 8 | 4 | 0 | 4 |
| Gemelos con ISO+ | 37 | 37 | 0 | 0 |
| **Total** | **767** | **392** | **16** | **359** |

- **Lo que había en la 30:** 723 mensajes, con 277 válidos, 94 inválidos y 352 sin decidir.
- **Los 637 mensajes idénticos** byte a byte a los de la 30 dan el mismo veredicto que allí.
- **Las 72 bases de GENADT y las 8 de A1 que cambian** son válidas.
- **De las 7 copias completadas, 6 son válidas.** La del ejemplo veterinario queda sin decidir por XPN.8 = `D`, fuera de la 0465
  impresa. La copia lo deja tal como lo trae el ejemplo (P5).
- **B36, en T02 y en sus eventos,** pasa de inválida a sin decidir. Solo le queda TXA-3.
- **Los 37 gemelos son válidos.**
- **Los 16 inválidos:** 8 bases A1 con PV1-2 vacío, L17 y los 7 fragmentos del capítulo 3.
- **Los 4 sin decidir por otras causas:**
  - la copia del ejemplo veterinario, por la 0465;
  - y tres de ORU (B15, B39 y B40), por OBX-2 (su longitud o la 0125) u OBX-11 = `f`, junto con la 0396 o MSH-12.

## El comprobador de tipos

`ga/comprobar_tipos.py` es un instrumento nuevo. Mira lo que IRIS no ve:
- el tipo de cada campo y componente;
- las tablas de los componentes;
- la longitud de un componente;
- los escapes y el juego de caracteres.

Lee del texto de v2.5 las tablas de atributos de los segmentos y las de componentes de los tipos (CH02A), y del índice del Apéndice
A si una tabla es de HL7 o de usuario. Las decisiones de Jev: un `""` en un campo obligatorio es error (P3); un campo «(B) R» se trata
como B (P4); y la longitud de un componente es aviso (P8).

**Su control, antes de usarlo** (`ga/control_tipos.py`, `ga/CONTROL-TIPOS.json`): TODO BIEN.
- 93 mutantes de la base A01-001, cada uno de un solo campo: 47 que tiene que cazar y 46 que no.
- En la versión 1 encuentra cada error de tipo conocido, con su lugar. De los cuatro que nombraba el ANTES, GT1-3 con una
  dirección y PR1-2 con `PR1` no son errores de tipo por la letra (todo ST; un IS sin valores sugeridos), y no los caza (DV-GA-10).
- En las seis familias de GENADT que la 30 da por válidas, ninguno.
- UCUM da error en los 37 orígenes de los gemelos y no en los gemelos.

**Lo que encontró en la versión 1 que IRIS no ve,** en las tres familias de GENADT que se arreglan:
- GT1-2 lleva un nombre en un CX: CX.7, una fecha, vale `L`;
- UB1-2 lleva `B` en un NM;
- ACC-1 lleva `1` en un TS;
- PV1-37 lleva nueve componentes en un DLD, que tiene dos.

En la versión 2, esas familias no dan ningún error.

**Sus límites:**
- No ve sentido: un PR1-2 con `PR1`, un GT1-3 con una dirección o la disposición de PL pasan. Tampoco ve que la versión 2 escribe
  `DG1|1|I9|I10|…`: el método de codificación ICD-9 con un código que es de ICD-10.
- Un valor fuera de la lista impresa de una tabla de HL7 es error para el comprobador. Para la lectura de la 30 queda sin decidir
  (Q-IV-D-11), y los veredictos de validez son los de la lectura.
- Se pasó por todo el ADT de las dos versiones y, para las unidades, por los 37 orígenes de los gemelos y por los gemelos.
- No ve condiciones entre campos, salvo las que codifica (OBX-2 con OBX-11, HD, EI y MSG).
- No mira la estructura del mensaje, que es cosa de IRIS.

## Los conversores: la versión 2 frente a la 1

Los dos conversores del estudio corrieron sobre las dos versiones con el mismo juez, con los mínimos y con las 65 muestras de los
proyectos. Los resultados están en `ga/COMPARACION-GA.json` y `ga/CIFRAS-GA-B.json`.

- **El ruido:** dos corridas de la versión 1 dan lo mismo en los 516 casos de cada conversor.
- **Los 435 casos idénticos en las dos versiones,** de cada conversor, dan lo mismo.
- **Cambian 81 casos y hay 7 nuevos.**
  - En Microsoft, 30 pasan de rechazo a convertidos. En LinuxForHealth no cambia ninguna categoría.
- **En la frase del estudio no cambian** las 15 nuevas confirmadas, las 31 ya declaradas, las 16 convenciones, los 2 rechazos
  nuevos ni las 3 dudosas. Los mensajes pasan de 368 a 375.
- **Lo publicado del estudio describe la versión 1 y no se cambia** (Q-GA-4). Las cifras que en la versión 2 son otras son el
  número de mensajes y los casos de las clases de la tabla de abajo. Están en `ga/CIFRAS-GA-B.json` (`cifras_que_cambian`), cada
  una con el documento publicado donde sale.
- **Los pares mínimos confirman lo mismo en las dos:** 30 de 34.
- **Las clases que cambian de casos:**

| Clase | Qué es | Casos, versión 1 → 2 |
|---|---|---|
| M-11 | Apartada (defecto del corpus): Microsoft rechaza GENADT por el CX.7 = `L` de GT1-2 | 30 → 0 |
| M-1 | Ya declarada | 204 → 234 |
| M-17 | Ya declarada | 12 → 30 |
| M-5 | Ya declarada | 31 → 49 |
| M-2 | Ya declarada | 48 → 62 |
| M-6 | Ya declarada | 18 → 23 |
| L-2 | Ya declarada | 121 → 126 |
| L-3 | Ya declarada | 118 → 123 |
| M-8 | Ya declarada | 6 → 9 |
| L-4 | Ya declarada | 95 → 97 |
| M-16 | Ya declarada | 11 → 12 |

- **Las 5 clases con todos sus casos en mensajes que cambian** conservan su número de casos: L-10, L-8, M-10, M-12 y M-18. El
  arreglo no toca sus campos (PID-16, XTN, el nulo de ACC-1 en `nulos` y PDA).
- **Las 2 candidatas** (Q-GA-7: anotadas, sin confirmar; la etapa 36 da la de Microsoft por M-28, ya declarada, y la de
  LinuxForHealth por convención):
  - **Microsoft**, en los 30 mensajes de ADT que ahora convierte, emite una Observation (con el código `injury-incident`) que el
    juez no atribuye a ningún elemento del mensaje y da por recurso inventado. Sale en los 30, que llevan ACC, y en ningún ADT
    convertido sin ACC. El juez cita para ella una regla de ORU, así que puede ser del juez y no del conversor;
  - **LinuxForHealth**, en la copia completada del ejemplo veterinario, convierte PID-8 = `S` en `gender: unknown`. La 0001 es
    una tabla de usuario y `S` no está entre sus valores sugeridos; para el comprobador es un aviso.
- **B36 en sus cinco eventos:** las dos versiones dan lo mismo en los dos conversores.
- **VXU (etapa 20):** sus bases no cambian; las nueve se miran en sus gemelos, abajo.

## Las 27 nuevas

Están en `ga/CRUCE-GA.json`, `ga/GEMELOS-GA.json` y `ga/GEMELO-MDM.json`. La pregunta es si la nueva **sale** en algún mensaje
válido: por su mecanismo, no por el campo. La 30 asignaba el apoyo por el campo del hallazgo, y con ese criterio 13 tenían algún
apoyo válido. Con este son 12 de esas 13: MD-L3 tiene apoyos válidos por el campo (OBX-5), pero son bases con un OBX ED o RP, en las
que su mecanismo (el texto de un OBX TX tras un CE) no puede salir.

- **12 de las del estudio de conversores salen en mensajes válidos de la versión 2:**
  - 11 en casos de su clase, con la regla del estudio (`cv/cv3_clases.py`) sobre el juicio de la versión 2;
  - L-22, en su par mínimo, que se confirma en la versión 2 y es válido.
  - Los 3 apoyos de GENADT de M-18, que en la 30 eran inválidos, pasan a válidos. Cinco bases A1 de M-10, L-10 y L-11 cambian de
    bytes por la tilde; siguen válidas, y las tres clases conservan sus casos.
- **Las 12 sin apoyo decidible por la 0396 salen en sus gemelos con ISO+,** igual que en sus orígenes:
  - M-23, M-24 y L-18;
  - VX-M7, VX-M8, VX-M10, VX-M12, VX-M14, VX-M15, VX-L6, VX-L8 y VX-L9.

  Cada par mínimo se confirma con sus gemelos: el caso lo muestra y el control no. Cada base gemela muestra el hallazgo que
  muestra su origen.
- **MD-M5 sale en un gemelo de su par con contenido que no es texto** (Q-GA-8, Jev 0,80; `ga/gemelo_mdm.py`).
  - Del par MP1 cambian solo TXA-3 (`TEXT` → `AP`), el OBX (el de texto, por el OBX ED de la base válida B05) y MSH-10.
  - Los dos gemelos son válidos en v2.5. Microsoft rechaza entero el caso, que lleva TXA-8 repetido, igual que el original, y
    convierte el control.
  - Los gemelos no están entre los 767: se hicieron para esto, después de la corrida (DV-GA-12).
- **MD-L3 y MD-L5 no salen en ningún mensaje válido.** Su base y su par quedan sin decidir solo por TXA-3 = `TEXT`. Las dos tratan
  de cómo llega el texto (un OBX TX tras un CE, y un FT con sus órdenes de formato), y para el texto ningún valor de TXA-3 de v2.5
  cabe en su longitud.

## La previsión

Hubo dos previsiones, cada una sellada antes de correr lo que prevé.

**La A** (`ga/PREVISION-GA-A.json`, antes de pasar la versión 2 por IRIS) **acierta 9 de 9.** El margen fue corto, en hora
local del 5-nov:
- el corpus se construyó a las 18:33:17;
- la previsión, con su commit, es de las 18:33:45;
- la validación se lanzó después: la prueba de humo con 9 mensajes, a las 18:33:52, y la corrida entera, de las 18:34:03 a las
  18:34:30.

El repositorio guarda el commit y las horas de los ficheros; el orden de los lanzamientos sale del registro de la sesión.

**La B** (`ga/PREVISION-GA-B.json`, antes de correr los conversores sobre la versión 2) **acierta 9 de 9 con la comparación
corregida, y 8 de 9 con la sellada.**
- **El punto que cambia es PB8,** las 12 en sus gemelos. Con la comparación sellada salían 11, porque en VX-M10 su base VXU-B37
  muestra el hallazgo en el segundo NK1, como `NK1(2)-3`, y la comparación sellada buscaba `NK1-3` (DV-GA-5).
- **La corrección vale igual para el origen y para el gemelo.** Solo cambia VX-M10, y su par ya se confirmaba con la sellada.
- **La previsión B se apoyó en lo que dio la versión 1** (`ga/RIESGO-GA.json`): las clases con todos sus casos en mensajes que
  cambian. De ahí sale que M-11 desaparecería y las otras cinco no.

## Lo que pasó por el camino

**Jev:**
- **Q-GA-2, 5 y 6 salieron con confianza por debajo de 0,3, y se preguntaron otra vez** con los hechos que faltaban: que ningún
  conversor traduce ISO+ a una URL, que la línea del circuito no necesita IRIS y que L17 es el par de L-25.
  - Q-GA-5 cambió de «solo el apoyo» (0,49) a «la línea de los conversores» (0,47). Se aplicó la segunda.
- **Del diseño, P2, P6 y P11 se preguntaron otra vez por la misma razón.**
  - En P11 apareció una opción que la primera vez faltaba: el capítulo 3 usa `UP` en ROL-2 para A54.
  - Ganó `UC`.

**El control:**
- **El comprobador no miraba CE.1 contra la tabla del campo:** NK1-3 = `SPOUSE`, AL1-4 = `MODERATE` y ROL-3 = `IN` no daban aviso.
  Lo cazó la primera pasada sobre el corpus, antes del control, y se arregló.
- **La primera vuelta del control dio dos fallos, los dos de lo que esperaba el control:**
  - el mutante PID-8 = `M^F` da también longitud de campo, porque el LEN es 1;
  - los 7 fragmentos no estaban en la lista de lo marcado.

  Los dos se corrigieron en el control, no en el instrumento.

**La corrida:**
- **M-11 se entendió al mirar la versión 1:** el rechazo apartado como defecto del corpus era el CX.7 = `L` que el comprobador
  encontró en GT1-2.
- **El guion de las cifras de la B elegía mal los casos de M-11,** primero ninguno y después 48. Ahora los elige por su clase en la
  versión 1 (DV-GA-11), y son 30.

**La revisión a ciegas** (un lector, que solo vio los ficheros) pidió cambios en su primera pasada, con cuatro bloqueantes:
- **El estado de Q-GA-1 a 7 que leyó Jev decía que ningún MDM_T02 con contenido en OBX puede ser válido en v2.5.** Solo es cierto
  del contenido de texto: la versión 2 trae 8 MDM_T02 válidos con OBX ED o RP. Ninguna de las siete preguntas era sobre MDM. Con el
  hecho bien puesto, se preguntó Q-GA-8 (el gemelo de MD-M5).
- **El «25 de 27» de la primera versión del resultado contaba apoyos válidos por campo, no mensajes válidos donde sale la nueva.**
  Con ese criterio, MD-L3 estaba entre las que se reproducían, y no sale en ninguno de sus apoyos válidos. El cruce se rehízo por
  mecanismo: daba 24, y con el gemelo de MD-M5, 25.
- **Las bases de la integración continua no estaban rehechas.** El guion llevaba a mano el número de casos de la versión 1 y paraba
  (DV-GA-9).
- **Faltaba declarar DV-GA-10.**

Y con siete menores, todos aplicados: cifras mal contadas, frases que decían más de lo medido y el bloque 4 del sello.

La segunda pasada aprobó, con ocho menores, todos aplicados (el bloque 5 del sello):
- los 206 sin decidir por TXA-3 son 200 `TEXT` y 6 `multipart`;
- la receta del ejemplo pide hoy la versión 1;
- faltaba el registro de las bases nuevas;
- el gemelo de MD-M5 está fuera de los 767;
- TX y FT caben en el LEN 2, pero son solo de v2.2;
- las pruebas de la herramienta no miraban la versión 2, y ahora la miran;
- el guion de la publicación iba sin commit, y el guion de las bases del laboratorio, sin línea en el sello;
- y los nombres de las claves de `ga/COMPARACION-GA.json`.

**Un segundo lector a ciegas,** otro modelo, revisó la copia pública preparada. Jev lo pidió antes de publicar, dos veces
(confianza 0,25 y 0,26). Aprobó con cuatro menores, todos aplicados (el bloque 6 del sello):
- **La frase de las bases decía que la corrida mensaje a mensaje da lo mismo que en lote.** No es así: difieren en 23 casos de
  VXU, los mismos que antes.
- **El manual de la herramienta (`cv/VC.md`) no nombraba `--version-corpus`.**
- **La lista de segmentos de la sección del README dejaba fuera NK1, AL1 y DB1.**
- **El margen del sello de la previsión A:** 45 s antes de que acabara la validación de IRIS. Ahora consta el orden.

## Las desviaciones del diseño (DV-GA-n)

- **DV-GA-1:** los valores fuera de los sugeridos de una tabla de usuario no cambian tampoco en las familias que se arreglan (P1 se
  aplica igual).
- **DV-GA-2:** los gemelos no entran en el corpus por omisión de la herramienta. Son un instrumento de esta etapa, y 22 de sus 37
  orígenes son mitades de pares que la herramienta no junta (18 de VXU y 4 de la auditoría).
- **DV-GA-3:** son 37 gemelos, no 39. El diseño contó 16 controles, y son 14.
- **DV-GA-4:** las tablas de componentes se leen del texto (CH02A). Donde difieren de la tabla del diseño, manda el texto: XPN.1
  es O y CX.4 remite a la 0363.
- **DV-GA-5:** la comparación de los gemelos quita el número de aparición del hecho (`NK1(2)-3` es NK1-3); está contado en «La
  previsión». La sellada está en `ga/sellada/`.
- **DV-GA-6:** el control de la etapa 18 no se repite tal cual. Pide antes de correr el juez de la CV4, que ya no es el de hoy. En
  su lugar:
  - las pruebas de la herramienta (`cv/prueba_vc.py`) dan TODO BIEN, con 154 comprobaciones (`ga/PRUEBA-VC.txt`). Dos son
    nuevas y miran la versión 2: 270 ADT, y 390 casos sin los mínimos y 458 con ellos (`ga/parche_prueba_vc.py`);
  - con `--version-corpus 1`, la herramienta da la frase publicada.
- **DV-GA-7:** la lista del corpus la escribe `ga/lista_corpus_v2.py`, no la función que junta el corpus. Su versión pública no
  lleva el veredicto de cada mensaje (Q-IV-D-10 de la 30).
- **DV-GA-8:** hubo dos previsiones selladas, no una. La de la validación también se selló antes de correrla.
- **DV-GA-9:** las líneas base de la demostración (`cv/ci/hacer_bases.py`) llevaban a mano el número de casos de la versión 1 (383 y
  451). Ahora lo cuentan con lo que junta la herramienta, como la receta del ejemplo desde la etapa 27 (`ga/parche_bases_ga.py`).
- **DV-GA-10:** el ANTES pedía que, en la versión 1, el comprobador encontrara los errores de tipo de GT1-2, GT1-3, PR1-2 y UB1-2.
  GT1-3 con una dirección y PR1-2 con `PR1` no son errores de tipo por la letra, y el diseño ya lo decía: el comprobador no los caza.
  Los dos se arreglan igual en la versión 2.
- **DV-GA-11:** los guiones que puntúan y cruzan (`cifras_ga_a.py`, `cifras_ga_b.py` y `cruce_ga.py`) se escribieron después de
  correr, como en la etapa 30. El de la B elige los casos de M-11 por su clase en la versión 1, no por cómo salen en la 2. El cruce
  pasó de mirar el apoyo por campo a mirar por mecanismo tras la revisión.
- **DV-GA-12:** el gemelo de MD-M5 (Q-GA-8) no estaba en el ANTES. Se decidió después de la corrida, con la corrección del hecho de
  MDM.
- **DV-GA-13:** el pin del ejemplo no se mueve en el push de la etapa, sino en un segundo push. Tiene que apuntar a un commit ya
  publicado, como lo haría un tercero, y ese commit es el de la etapa.

## Lo que no dice

- **IRIS no es el estándar.** Cada error suyo pasó por la lectura de la 30, con su cita. El comprobador de tipos es del laboratorio
  y mide tipo y tabla, no sentido.
- **El comprobador se pasó por ADT y por los gemelos y sus orígenes;** por ORU, VXU y MDM, no.
- **Las bases de ORU y VXU siguen con UCUM,** y 141 mensajes quedan sin decidir solo por eso. Los gemelos dicen que las 12 nuevas
  no dependen de UCUM, no que UCUM sea válido en v2.5.
- **No se rehicieron:**
  - la línea del circuito de IRIS y del verificador (la concordancia de A1 y el rejuicio de la 14k), que se declara así (Q-GA-5);
  - el arrastre (etapa 21).
- **Las 2 candidatas no se han confirmado:** ni par mínimo, ni búsqueda en el proyecto, ni revisión adversaria. (Lo hizo la
  etapa 36.)
- **La deriva del juez desde lo publicado** (L-24, M-36, M-4 y el par L16) es la que ya declaró la etapa 21. Esta etapa compara las
  dos versiones con el mismo juez, el de hoy.
- **Los 7 fragmentos del capítulo 3 siguen siendo inválidos en v2.5,** como los escribe el estándar.
- **Las cifras publicadas del estudio de conversores, de VXU y de MDM** son las de la versión 1. Las de la 2 están aquí.

## La integración continua

- **La herramienta pasa a la versión 2,** así que la demostración (`demo-ci`) corre con ella.
  - Sus tres líneas base (el juguete, LinuxForHealth en lote y mensaje a mensaje) se rehicieron desde la copia pública con
    `cv/ci/hacer_bases.py`.
  - Llevan 390 casos sin los mínimos y 458 con ellos.
  - El guion comprueba dos corridas iguales, el «igual» frente a la base y un positivo sembrado en el juguete. Todo da bien
    (`ga/BASES-CI-33.json` y `ga/BASES-CI-33-HECHO.txt`).
  - La base mensaje a mensaje de LinuxForHealth difiere de la de lote en 23 casos, VXU-B18 a B40. Son los mismos que con las
    bases de antes: el estado que LinuxForHealth arrastra entre mensajes en lote (etapa 20). Esto se comprobó sobre las dos
    bases, no con el guion.
  - Frente a las de antes, cada caso que ya estaba conserva su entrada. Entran los 7 casos de las copias completadas, y cambian
    la huella del corpus y la de la herramienta.
- **El proyecto de ejemplo (`ejemplo-ci`) y el run en rojo** fijan un commit del laboratorio, como lo haría un tercero. Siguen en el
  de antes hasta que su pin sube, en un segundo push, al de esta etapa (DV-GA-13).
  - Su receta (`ejemplo-ci/ci/hacer_base.sh`) cuenta los casos con la función que junta el corpus, que da la versión 1 por
    omisión (P10). En ese segundo push, `esperado()` pasa a pedir la versión 2 (`version=2`), y su base se rehace con ella.

## Cómo se repite

Desde `verificador/`, con el texto de v2.5 en `../estandares/` y lo privado en `../privado/`, como en la etapa 30:
1. **La versión 2:**
   - `python3 ga/hacer_gen_adt_v2.py`;
   - `python3 ga/hacer_resto_v2.py`;
   - `python3 ga/solo_cambia_esto.py`.
2. **El comprobador:** `python3 ga/control_tipos.py`.
3. **La validación,** con un IRIS que tenga el esquema 2.5 y la clase de la 30:
   - `python3 ga/corpus_ga.py <corpus>`;
   - `python3 iv/validar_iv.py <corpus> <filas>`;
   - `python3 iv/lectura_iv.py <filas> <txt de v2.5> <carpeta>/LECTURAS-IV.json <corpus>`;
   - `python3 ga/cifras_ga_a.py <carpeta>/VEREDICTOS-IV.jsonl <corpus>/CORPUS-IV.json <cifras>`;
   - la lista: con esos veredictos copiados a `ga/VEREDICTOS-GA.jsonl`, `python3 ga/lista_corpus_v2.py <corpus>/CORPUS-IV.json <corpus>`.
4. **Los conversores:**
   - `python3 cv/verificar_conversor.py cv/adaptadores/<conversor>.json <salida> --artefactos <conversores> --muestras <muestras> --version-corpus 1`,
     dos veces, y una vez con `--version-corpus 2`;
   - los orígenes (`python3 ga/comparar_ga.py origenes <carpeta>`) y `ga/gemelos`, con `--corpus <carpeta> --sin-corpus-lab --sin-minimos`;
   - B36: sus cinco eventos de cada versión, con `--corpus`.
5. **La comparación:**
   - `python3 ga/comparar_ga.py ruido|comparar|gemelos …`;
   - `python3 ga/cifras_ga_b.py <corridas> <cifras>`;
   - `python3 ga/cruce_ga.py <carpeta de la comparación>`, después del paso 6.
6. **El gemelo de MD-M5:**
   - `python3 ga/gemelo_mdm.py`, que escribe `ga/gemelos-mdm/`;
   - sus cuatro mensajes, en un corpus del aparato de la 30 con sus cuatro filas, por `iv/validar_iv.py` y `iv/lectura_iv.py`;
   - Microsoft, con `--corpus ga/gemelos-mdm --sin-corpus-lab --sin-minimos`;
   - `python3 ga/juzgar_gemelo_mdm.py <VEREDICTOS-IV.jsonl de los cuatro> <corrida de Microsoft>`.

## Ficheros

- **La versión 2:**
  - `ga/bases_adt_v2.json` y `ga/gen_adt_v2.py`, que escribe `ga/hacer_gen_adt_v2.py`;
  - `ga/bases_a1_v2.json`, `ga/ejemplos_cap3_v2.json`, `ga/bases_mdm_v2.py` y `ga/gemelos/`, que escribe `ga/hacer_resto_v2.py`;
  - `ga/LISTA-CORPUS-V2.jsonl`.
- **El comprobador:** `ga/comprobar_tipos.py`, `ga/control_tipos.py` y `ga/CONTROL-TIPOS.json`.
- **Las comprobaciones:** `ga/solo_cambia_esto.py` y `ga/SOLO-CAMBIA-ESTO.json`.
- **La validación:** `ga/corpus_ga.py`, `ga/LECTURAS-GA.json`, `ga/cifras_ga_a.py` y `ga/CIFRAS-GA-A.json`.
- **Los conversores:**
  - `ga/comparar_ga.py`, `ga/riesgo_ga.py` y `ga/RIESGO-GA.json`;
  - `ga/RUIDO-*.json`, `ga/COMPARACION-GA.json`, `ga/CLASES-GA-v1.json` y `v2`, y `ga/minimos-GA-v1.json` y `v2`. En
    `ga/COMPARACION-GA.json`, `lote` y `mensaje` son la versión 1 y la 2: los nombres vienen de la comparación de la etapa 21, que
    se usa tal cual. `ga/CIFRAS-GA-B.json` los llama `v1` y `v2`;
  - `ga/GEMELOS-GA.json`, `ga/B36-*.json`, `ga/cifras_ga_b.py`, `ga/CIFRAS-GA-B.json`, `ga/cruce_ga.py` y `ga/CRUCE-GA.json`;
  - el gemelo de MD-M5: `ga/gemelo_mdm.py`, `ga/gemelos-mdm/`, `ga/juzgar_gemelo_mdm.py` y `ga/GEMELO-MDM.json`, con su decisión
    en `ga/decision-jev-ga8.md`.
- **La integración continua:** `ga/parche_bases_ga.py`, `ga/BASES-CI-33.json`, `ga/BASES-CI-33-HECHO.txt`,
  `ga/parche_prueba_vc.py`, `cv/prueba_vc.py` y `ga/PRUEBA-VC.txt`.
- **Las previsiones y el sello:** `ga/PREVISION-GA-A.json`, `ga/PREVISION-GA-B.json`, `ga/SELLO-GA.txt` y `ga/sellada/`.
- **La herramienta:** `cv/verificar_conversor.py`, con `--version-corpus` (el parche, en `ga/parche_vc_version.py`).
- **Las bases de la demostración en la integración continua:** `cv/ci/LINEA-BASE-*.json`, rehechas con la versión 2.
