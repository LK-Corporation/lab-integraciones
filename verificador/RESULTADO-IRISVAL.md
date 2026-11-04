# Resultado de la etapa 30: el validador de IRIS como segundo lector de los corpus publicados

**De los 723 mensajes sintéticos publicados, IRIS da 277 por válidos en las reglas que ve y que el estándar sostiene, y 94 por
inválidos.** Los inválidos son casi todos obligatorios vacíos en ADT. **Los 352 restantes quedan sin decidir**, porque el propio
texto de v2.5 no zanja lo que IRIS les marca:
- valores fuera de la lista impresa de una tabla de HL7, que el texto permite extender con valores locales: sobre todo UCUM en
  las unidades de ORU y VXU;
- TXA-3 en MDM, cuyo valor está en su tabla y no cabe en su LEN.

**De las 27 discrepancias nuevas publicadas, ninguna se apoya solo en mensajes inválidos**, ni con la pregunta del ANTES (cualquier
regla sostenida) ni con el criterio del cruce (Q-IV-D-6: una regla que toque su campo). 14 no tienen ningún mensaje de apoyo válido
de punta a punta, porque todos quedan sin decidir. Esas 14 llevan la salvedad en su clase (`nota_iv`), y las clases no cambian.

**Con los auditores de la etapa 29 coincide en 0 de 2 lugares.** De lo poco firme y comparable que vieron ellos, IRIS no mira una
cosa (un componente obligatorio), y la otra la ve pero la lectura la deja sin decidir.

La pregunta se fijó antes de mirar, en [`ANTES-ETAPA-IRISVAL.md`](ANTES-ETAPA-IRISVAL.md). La etapa 29 hizo la misma pregunta con
dos auditores que leyeron el texto de v2.5, y dijo de sí misma que eran lecturas, no un validador. Además, dejó fuera ADT y MDM.
Aquí el lector es un motor de integración de producción, InterSystems IRIS, con su esquema de HL7 v2.5. Es otra implementación,
de otro autor.

## Cómo se hizo

1. **El corpus: los 723 mensajes sintéticos publicados** ([`iv/corpus_iv.py`](iv/corpus_iv.py)), que son 683 distintos:
   - los 451 que junta la herramienta: 263 de ADT, 40 de ORU, 40 de VXU, 40 de MDM_T02 y 68 pares mínimos;
   - los pares de VXU, de MDM y de la auditoría;
   - las 40 bases de MDM en sus cinco eventos. 40 de esos 200 son copia de las de MDM_T02, así que esas bases pesan seis veces
     en las cuentas.

   Los pares de MDM y de la auditoría son, byte a byte, los que se corrieron con los conversores (CIFRAS-IV.json,
   `pares_comprobados_byte_a_byte`).
2. **El aparato lo diseñó Fable a ciegas** de lo publicado: [`iv/diseno-iv-fable.md`](iv/diseno-iv-fable.md). Las decisiones
   abiertas las tomó Jev:
   - las diez primeras, antes de correr nada ([`iv/decision-jev-qiv.md`](iv/decision-jev-qiv.md));
   - la 11, tras el control ([`iv/decision-jev-qiv11.md`](iv/decision-jev-qiv11.md)), y otra vez tras la revisión del segundo
     lector, con los hechos que faltaban ([`iv/decision-jev-qiv11b.md`](iv/decision-jev-qiv11b.md));
   - la 12 (dos veces) y la 13, tras la revisión del primer lector ([`iv/decision-jev-qiv12.md`](iv/decision-jev-qiv12.md) y
     [`iv/decision-jev-qiv12b.md`](iv/decision-jev-qiv12b.md)).
3. **IRIS valida bandera a bandera** ([`iv/validar_iv.py`](iv/validar_iv.py), con la clase
   [`iv/Lab.IV.Validar.cls`](iv/Lab.IV.Validar.cls)). Las banderas son estructura, campos obligatorios, longitudes y tablas. IRIS da
   un solo error por llamada, así que cada error se enmudece en una copia y se vuelve a validar, hasta que no queda ninguno.
4. **La lectura de cada error en el texto de v2.5**, con su cita de fichero y línea ([`iv/lectura_iv.py`](iv/lectura_iv.py),
   [`iv/LECTURAS-IV.json`](iv/LECTURAS-IV.json)).

   Cuentan:
   - un obligatorio, si su tabla de atributos lo hace R;
   - una longitud, si pasa el LEN del estándar, que es normativo (CH02.txt:426). Si el valor está en la tabla del campo y la
     tabla no trae un equivalente que quepa y valga en v2.5, queda sin decidir (Q-IV-D-12). El texto deja cambiar la longitud
     con un acuerdo entre las partes, como un perfil de conformidad (CH02.txt:426-428), y aquí no hay ninguno. Por eso cuenta,
     mientras que un valor fuera de la lista de una tabla de HL7 queda sin decidir: para extender la tabla, el texto no pide
     ningún acuerdo;
   - la estructura, con la tabla de la estructura del mensaje en su capítulo.

   Queda sin decidir un valor fuera de la lista impresa de una tabla que el índice del Apéndice A da como de HL7. El texto
   permite extender esas tablas con valores locales (CH02.txt:563-565; Q-IV-D-11).

   No cuentan:
   - las tablas de usuario según ese índice;
   - los segmentos Z al final del mensaje;
   - el nulo `""`;
   - un código de CE o CWE cuyo componente 3 nombra otro sistema;
   - un código de país de ISO 3166 en la 0399, que no trae lista impresa.
5. **Los controles se probaron antes de usar el aparato:** 19 mutantes, con un defecto de cada clase, dos combinados, uno de
   estructura discrepante y dos con otros separadores. Todos salen en su clase y su lugar, salvo el de repeticiones, del que IRIS
   no dice nada.
   - A las bases de los mutantes se les limpiaron antes sus propios defectos, y lo limpiado es el primer resultado sobre el
     corpus.
   - Dos corridas seguidas dan lo mismo: [`iv/control_iv.py`](iv/control_iv.py), [`iv/CONTROL-IV.json`](iv/CONTROL-IV.json).
   - Los controles prueban el aparato, no las reglas de lectura.
6. **La previsión se selló antes de correr el corpus:** [`iv/PREVISION-IV.json`](iv/PREVISION-IV.json), la de Jev en
   [`iv/decision-jev-prevision-iv.md`](iv/decision-jev-prevision-iv.md), y las huellas en [`iv/SELLO-IV.txt`](iv/SELLO-IV.txt),
   con el orden de cada bloque al final.
7. **Los cruces:** [`iv/cruce_iv.py`](iv/cruce_iv.py) cruza con los auditores y con las nuevas, y
   [`iv/cifras_iv.py`](iv/cifras_iv.py) da cada cifra de este documento ([`iv/CIFRAS-IV.json`](iv/CIFRAS-IV.json),
   [`iv/CRUCE-IV.json`](iv/CRUCE-IV.json)).

## Lo que dio, por corpus

| Corpus | Mensajes | Válidos | Inválidos | Sin decidir |
|---|---|---|---|---|
| ADT de la herramienta | 263 | 168 | 87 | 8 |
| ORU de la herramienta | 40 | 11 | 0 | 29 |
| VXU de la herramienta | 40 | 3 | 0 | 37 |
| MDM_T02 de la herramienta | 40 | 8 | 1 | 31 |
| Pares mínimos del estudio de conversores | 68 | 43 | 1 | 24 |
| Pares de VXU | 50 | 0 | 0 | 50 |
| Pares de MDM | 14 | 0 | 0 | 14 |
| Bases de MDM en sus cinco eventos | 200 | 40 | 5 | 155 |
| Pares de la auditoría | 8 | 4 | 0 | 4 |
| **Total** | **723** | **277** | **94** | **352** |

**Lo que hace inválidos a los mensajes** (por errores: 570 obligatorios, 9 de longitud y 7 de estructura; por mensajes: 86, 7 y
7):
- **Obligatorios vacíos y estructura en ADT** (87 mensajes; 86 con algún obligatorio vacío, y uno solo por estructura):
  - las tres variantes del generador con segmentos opcionales («comp», «nulo» y «opci», 72 mensajes) traen ROL, DG1, PR1, OBX,
    NK1, AL1 y GT1 sin sus campos R: ROL-2, ROL-4, DG1-6, PR1-5, OBX-11, OBX-3, los Set ID (DG1-1, NK1-1, AL1-1 y GT1-1) y el
    nombre del garante (GT1-3);
  - 8 bases A1 dejan PV1-2 vacío;
  - los 7 ejemplos tomados del capítulo 3 son fragmentos: les faltan segmentos (EVN, PV1, PID), campos de MSH o, en 4 de ellos,
    PID-5.
- **Longitudes en MDM:** TXA-12 en 6 mensajes y TXA-13 en 2 pasan su LEN de 30.
- **PID-30 = `NO`** pasa el LEN 1 en el caso de un par mínimo, que está hecho así a propósito.

**Lo que queda sin decidir:**
- **Valores fuera de la lista impresa de una tabla de HL7** (Q-IV-D-11):
  - UCUM en RXA-7 (96 errores) y OBX-6 (80), y SCT en SPM-4 y RXR-2, todos en la 0396. Lo llevan las unidades de ORU y de VXU
    y sus pares;
  - MSH-12 = `2.5.1` (8 bases A1) y `2.6` (ORU-B15), en la 0104;
  - OBX-11 = `f` en minúscula (ORU-B39), en la 0085;
  - `NO` en la 0136 y un valor `D` que no está en la 0465, en mensajes que ya son inválidos por otra regla.
- **TXA-3 en MDM** (Q-IV-D-12). Son 206 mensajes con un valor que no cabe en el LEN 2; 6 de ellos son además inválidos por TXA-12
  o TXA-13, y quedan 200 sin decidir. TXA-3 remite a la tabla 0191, que trae `TEXT` y `multipart`. El valor con la misma
  descripción que `TEXT` es `TX`, pero la 0191 lo da como solo de la 2.2, así que en v2.5 no hay uno que quepa.
- **OBX-2** = `XPN` en ORU-B40 (PN tiene otra descripción) y `CWE` en ORU-B15. La tabla impresa no trae `CWE`, y el texto de
  OBX-2 dice que vale cualquier tipo de HL7 salvo cuatro (CH07.txt:2590). ORU-B40 queda sin decidir también por UCUM, y ORU-B15
  por MSH-12 = `2.6`.

**Lo que IRIS dice y no cuenta:**
- 8.501 avisos contra tablas que el esquema de IRIS trae vacías, casi todos de tablas de usuario (MSH-3 a MSH-6 y las de PL).
  Incluyen los 9 de la 0399 que se leen más abajo;
- 874 valores que IRIS rechaza y el Apéndice A trae, por valor o por patrón;
- 682 valores de tablas de usuario según la mayoría del texto. Incluyen 3 de la 0162, que el índice da como de HL7 y se leen
  más abajo;
- 24 segmentos Z al final del mensaje;
- 24 nulos `""`;
- 6 códigos de CE o CWE de otro sistema (3 de ellos, los de la 0162);
- 9 códigos de país ISO 3166 en la 0399;
- 6 TXA-2 = `ZX`, de la 0270, que es de usuario.

El desglose por tabla está en CIFRAS-IV.json, `avisos_de_tabla_por_tabla`.

## El cruce con los auditores de la 29

Son los 162 mensajes de VXU y ORU auditados. Se cruzan en lo que los dos lectores pueden ver: estructura, obligatorios,
longitudes y tablas de HL7. Los defectos de los auditores se clasificaron y sellaron antes de correr el corpus, pero después del
control, que ya había pasado por IRIS dos de los mensajes auditados (ORU-B01 y VXU-B01):
[`iv/AUDITORES-CLASIFICADOS-IV.json`](iv/AUDITORES-CLASIFICADOS-IV.json).

- **IRIS da 22 de los 162 por válidos y deja 140 sin decidir.** Casi todos los que deja sin decidir son por UCUM, que el auditor
  de VXU leyó como admisible y el de ORU dejó en duda. No da ninguno por inválido.
- **En los 22 que deciden los dos, coinciden todos.** La kappa no se puede calcular, porque ningún lado da ninguno por inválido.
- **Pares de mensaje y campo que ven los dos: 0 de 2.** Que solo cuenta IRIS: 0. Que solo ven los auditores: 2.
  - **MSH-9 sin su tercer componente** en VXU-B39. MSG.3 es R en v2.5 (CH02A.txt:2809), así que la lectura les da la razón. Es un
    obligatorio de componente, que IRIS no mira: sin él, lo que miran los dos se queda en un solo par.
  - **OBX-11 = `f`** en ORU-B39. IRIS lo marca, igual que el auditor, y la lectura lo deja sin decidir por Q-IV-D-11.
- **La duda que ya tenía el auditor** (OBX-2 = `CWE` en ORU-B15) queda sin decidir también aquí.
- **Casi todo lo que encontraron los auditores es de lo que IRIS no ve:** la regla transversal del tipo XCN (88 defectos), los
  condicionales, las reglas del texto y los tipos de dato.
- **El cruce por mensaje y clase** está en CRUCE-IV.json, `por_mensaje_y_clase`.

## El cruce con las nuevas publicadas

Son las 27 nuevas publicadas: 15 del estudio de conversores, 9 de VXU y 3 de MDM. El apoyo de cada una son sus mensajes del
laboratorio; las muestras públicas de los proyectos no entran. Del estudio de conversores, el apoyo son sus ejemplos y su par, y
está marcado como incompleto (Q-IV-D-7).

| | Nuevas |
|---|---|
| Con algún mensaje de apoyo válido de punta a punta | 13 |
| Con todo su apoyo sin decidir | 14 |
| Con todo su apoyo inválido por alguna regla sostenida (la pregunta del ANTES) | 0 |
| Afectadas: todo su apoyo inválido por una regla que toca su campo (Q-IV-D-6) | 0 |

- **«Intacta» quiere decir que IRIS no invalida su apoyo,** no que la nueva quede confirmada.
- **Las 14 sin ningún apoyo válido** son L-18, M-23, M-24 y las nueve de VXU, todas por UCUM, y MD-L5 y MD-M5, por TXA-3.
- **Las 14 llevan la salvedad en su clase, como «nota_iv»** (Q-IV-D-13): [`cv/CLASES-CV3.json`](cv/CLASES-CV3.json),
  [`vx/CLASES-VX3.json`](vx/CLASES-VX3.json) y [`md/CLASES-MD3.json`](md/CLASES-MD3.json), con
  [`iv/parche_clases_iv.py`](iv/parche_clases_iv.py). La marca va en los ficheros de clases; los resultados de los estudios no
  se tocan.

## La previsión, frente a lo medido

**Acertó 14 de 28 cantidades selladas** ([`iv/CIFRAS-IV.json`](iv/CIFRAS-IV.json), clave `prevision`).
- **Las que se cumplen casi por construcción:** PV2 (todo mensaje trae algún aviso) y PV10 (antes del sello ya se sabía que los
  24 Z van al final).
- **PV6, el acuerdo por mensaje,** acierta en solo 22 mensajes.
- **Las tres de Jev** repiten otras con otro intervalo.
- **La cuenta depende de Q-IV-D-11, decidida después de la corrida.** Con su segunda respuesta aciertan PV6 (el acuerdo) y PV7
  (lo que solo cuenta IRIS), y fallan PV3, la kappa y PV8, que con la primera acertaban.

**Lo que falló:**
- **Por mucho, la proporción de válidos.** La previsión daba entre el 70 y el 100 % en cada corpus, y Jev más del 95 % en total.
  Salió el 38,3 % en total, y entre el 0 y el 64 % por corpus. La previsión daba por hecho que los corpus eran válidos en lo que
  IRIS ve, porque así lo dicen sus generadores. No contaba con que IRIS marcara UCUM y TXA-3, ni con los obligatorios de las
  variantes del generador de ADT.
- **Las dos clases mayores:** son obligatorios y longitudes, no obligatorios y tablas.
- **La kappa:** no se puede calcular.
- **PV8:** no se puede medir, porque no hay pares que vea solo IRIS.
- **Que hubiera nuevas indeterminadas:** todas tienen algún apoyo del laboratorio.

**Lo que acertó:**
- ningún mensaje pierde segmentos al importarse y ninguno queda incompleto;
- ninguna nueva afectada, también según Jev;
- los Z no cuentan y todos los tipos sin estructura se resuelven;
- menos del 20 % de lugares compartidos, como dijo Jev.

## Lo que pasó por el camino

**Antes de correr el corpus:**
- **El control mostró dos cosas del corpus antes de la corrida:** UCUM en las bases de ORU y VXU y `TEXT` en TXA-3 de MDM-B01.
  UCUM ya lo había publicado la 29. Se preguntó a Jev cómo contarlo (Q-IV-D-11), y la previsión no se tocó.
- **Insertar el segmento que falta fabricaba errores en cascada.** Lo vio el control, y el conductor dejó de insertar: un
  segmento obligatorio que falta cierra la estructura, y si IRIS lo echa en falta donde hay un Z, el error es del Z, fuera de
  lugar (Q-IV-D-8).
- **La primera corrida del corpus se paró:** 24 mensajes de ADT usan otros separadores en MSH-2, y el conductor partía con los
  de siempre. Se arregló, se añadieron dos mutantes con otros separadores, el control volvió a dar TODO BIEN y el aparato se
  reselló. Antes de pararse, aquella corrida enseñó el resumen de 12 mensajes de ADT; está escrito en el sello.

**Después de correr el corpus**, con revisiones a ciegas de dos lectores distintos, dos pasadas de cada uno. El ANTES fijaba una
sola revisión al publicar; se hicieron más porque Jev pidió la del segundo lector antes de publicar:
- **La lectura entera es posterior a la corrida** (`lectura_iv.py`, en el cuarto bloque del sello). Repite las reglas del
  conductor sellado y añade las de este documento.
- **Q-IV-D-12 se preguntó dos veces.** El primer estado no decía que el `TX` de la 0191 es solo de la 2.2. Con la primera
  respuesta, `TEXT` seguía contando.
- **Q-IV-D-11 se preguntó también dos veces.** El primer estado decía solo que la 29 lo dejó como duda; no traía que el texto
  permite extender las tablas de HL7, ni que admite otros sistemas para las unidades. La primera respuesta fue «cuenta», con 0,42
  (confianza 0,13); la segunda, «sin decidir siempre», con 0,77 (confianza 0,66).
  - Con las dos primeras respuestas eran 440 inválidos y 6 sin decidir.
  - Con la segunda de la 12 y la primera de la 11, 246 y 200.
- **El tipo de cada tabla se tomó primero por la mayoría de menciones en el texto.** La lectura usa el índice del Apéndice A,
  como dice este documento. Eso reclasificó 12 errores (0399 y 0162), y ninguno cuenta.

## Lo que no dice

- **IRIS no es el estándar,** y aquí no es el juez de nada. Cada error suyo pasó por la lectura del texto de v2.5 antes de
  contar. La lectura la hizo quien corrió la etapa (Q-IV-D-5) y lleva la cita, para que se pueda comprobar.
- **IRIS no ve** los condicionales, las reglas que cruzan campos o estados, los tipos de dato, la obligatoriedad de los
  componentes ni las repeticiones. Con la bandera de repeticiones no dijo nada en ningún mensaje, así que esa clase no se mide.
- **Los mensajes de los auditores se emparejan por nombre**, no por huella como pedía el diseño, porque las auditorías no guardan
  huellas. Salen de los mismos generadores deterministas.
- **Q-IV-D-8 dice «al final del grupo», y el código mira el final del mensaje.** Con estos datos da lo mismo: los 24 Z van al
  final del mensaje.
- **La kappa no lleva intervalo.**
- **El estado de la segunda Q-IV-D-11 solo traía los hechos a favor de dejarlo sin decidir.** No decía:
  - que el mismo pasaje de las unidades marca las locales como L o 99zzz (CH07.txt:2933);
  - que la 0396 tiene sus propios patrones locales;
  - que UCUM y SCT entraron en la tabla en versiones posteriores;
  - que `2.5.1` y `2.6` identifican otra versión, no un valor local.

  «Sin decidir» es lo que decidió esa pregunta, no una lectura de que el texto admita UCUM.
- **Dos estados que leyó Jev traían un error:**
  - el de las diez primeras decía que muchas longitudes de v2.5 son recomendadas, y el texto dice que son normativas
    (CH02.txt:426);
  - el de la 12 contaba los obligatorios de ADT entre las causas de las 14, y ninguna de las 14 es por eso.

  Además, la nota de la revisión de los auditores nombra el defecto 126, que el programa ya clasificaba como no comparable.
- **Los mensajes inválidos siguen en el corpus.** Pueden pesar en las cuentas de categorías y en las ya declaradas.
- **Las muestras públicas de los proyectos no se validaron.**
- **Lo que se puede repetir con lo publicado:**
  - el aparato, sobre los mensajes publicados (`corpus_iv.py` y `validar_iv.py`), con un IRIS que tenga el esquema 2.5;
  - la clasificación de las tablas y sus valores, que `tablas_iv.py` saca del texto de v2.5 y deja en `privado/iv/`, que es
    donde los buscan `validar_iv.py` y `lectura_iv.py`;
  - la lectura, los cruces y las cifras, desde las filas de esa corrida; `cifras_iv.py` lee además la lista del corpus
    (`privado/iv/corpus/CORPUS-IV.json`, que escribe `corpus_iv.py`).

## Ficheros

- **El estado y las preguntas de cada decisión de Jev:**
  - [`iv/estado_qiv.md`](iv/estado_qiv.md) y [`iv/preguntas_qiv.json`](iv/preguntas_qiv.json);
  - [`iv/estado_qiv11.md`](iv/estado_qiv11.md) y [`iv/preguntas_qiv11.json`](iv/preguntas_qiv11.json);
  - [`iv/estado_qiv11b.md`](iv/estado_qiv11b.md) y [`iv/preguntas_qiv11b.json`](iv/preguntas_qiv11b.json);
  - [`iv/estado_qiv12.md`](iv/estado_qiv12.md) y [`iv/preguntas_qiv12.json`](iv/preguntas_qiv12.json);
  - [`iv/estado_qiv12b.md`](iv/estado_qiv12b.md) y [`iv/preguntas_qiv12b.json`](iv/preguntas_qiv12b.json);
  - [`iv/estado_prevision_iv.md`](iv/estado_prevision_iv.md) y
    [`iv/preguntas_prevision_iv.json`](iv/preguntas_prevision_iv.json).
- **El tipo de cada tabla** en el texto de v2.5, solo número y tipo: [`iv/TABLAS-TIPO-IV.json`](iv/TABLAS-TIPO-IV.json), de
  [`iv/tablas_iv.py`](iv/tablas_iv.py).
- **Las sondas del primer día** ([`iv/sonda_validate.txt`](iv/sonda_validate.txt) y
  [`iv/sonda_validate2.txt`](iv/sonda_validate2.txt)), la carga de la clase ([`iv/cargar_iv.txt`](iv/cargar_iv.txt)) y su prueba
  mínima ([`iv/prueba_lote.py`](iv/prueba_lote.py)).
- **Los defectos de los auditores, clasificados:** [`iv/clasificar_auditores_iv.py`](iv/clasificar_auditores_iv.py), con la
  revisión a mano en [`iv/revision_auditores_iv.json`](iv/revision_auditores_iv.json). El resumen por lugar sale de
  [`iv/resumen_iv.py`](iv/resumen_iv.py).
- **Lo que no se publica:**
  - las filas de IRIS mensaje a mensaje (Q-IV-D-10);
  - los valores del Apéndice A.
