# Resultado de la etapa 32: las muestras públicas en la versión que declaran

**De las 223 muestras que declaran otra versión que la 2.5, con el esquema de IRIS de la suya, 21 son válidas, 141 inválidas y 61
sin decidir; de las 5 nuevas que se apoyan en muestras, 2 siguen sin ningún mensaje válido: VX-M14 y VX-M15.** La pregunta y las
reglas se fijaron antes de correr, en [`ANTES-ETAPA-IVDECLARADA.md`](ANTES-ETAPA-IVDECLARADA.md). La etapa 31
([`RESULTADO-IVMUESTRAS.md`](RESULTADO-IVMUESTRAS.md)) validó las mismas muestras contra v2.5, como las lee el juez, y no salió
ninguna válida.

- **Las 21 válidas** son 20 de VXU y 1 de conversores: 14 de la 2.5.1 y 7 de la 2.6. De la 2.8 no sale ninguna.
- **13 de las 21 dependen de una regla del ANTES** (Q-VD-3, abajo): un segmento con más campos de los que define su versión va
  aparte. Son 13 de VXU de la 2.5.1 con MSH-22 y MSH-23 con valor. Si esos campos dejaran la muestra sin decidir, serían 8
  válidas, 141 inválidas y 74 sin decidir; si contaran como error, 8, 174 y 41.
- **En 179 de las 223** (las de la 2.3, la 2.4, la 2.6 y la 2.8) lo que cuenta es lo que dice el esquema de IRIS de esa versión,
  no el texto del estándar: el laboratorio no tiene ese texto.

## Qué se validó y cómo

- **Las muestras:** las 223 de la 31 que declaran en MSH-12 otra versión: 108 de la 2.6, 64 de la 2.8, 44 de la 2.5.1, 6 de la
  2.3 y 1 de la 2.4. La versión es el primer componente de MSH-12. Las 2 que declaran la 2.5 se quedan con su veredicto de la 31
  ([`ivd/CORPUS-IVD-lista.json`](ivd/CORPUS-IVD-lista.json)).
- **Las decisiones, de Jev:**
  - **Q-VD-1, las versiones sin texto** ([`ivd/estado_qvd.md`](ivd/estado_qvd.md),
    [`ivd/decision-jev-qvd.md`](ivd/decision-jev-qvd.md), 0,95). Cuentan la estructura, los obligatorios y las longitudes, como
    los da IRIS. Un valor que IRIS rechaza en una tabla que su esquema trae con valores queda sin decidir; en una que trae vacía
    es aviso (abajo, cómo se leyó «las de usuario»). Se apoya en lo medido en las etapas 30 y 31: frente al texto de v2.5, el
    esquema de v2.5 de IRIS acertó sus 130 errores de estructura, sus 960 de obligatorios y sus 932 de longitudes, y en las tablas
    rechazó valores que el estándar trae (874 de 1.098 en la 30).
  - **Q-VD-2, la 2.5.1** (0,99): se lee con el texto de v2.5.1, como la 30 con el de v2.5.
  - **Q-VD-3, un segmento con más campos de los que define su versión** (la pasada de repeticiones). Va aparte, como en la 31: es
    la regla del ANTES (Q-VD-3b, 0,95; [`ivd/estado_qvd3b.md`](ivd/estado_qvd3b.md),
    [`ivd/decision-jev-qvd3b.md`](ivd/decision-jev-qvd3b.md)). Se preguntó tres veces, y una cuarta, qué regla va en el titular:
    - antes de correr, «dentro» (0,75), con un estado sin las reglas del receptor;
    - antes de correr, «aparte» (0,95), con ellas, pero sin ningún hecho del otro lado. Es la que fijó el ANTES;
    - después de correr, tras la primera pasada de la revisión a ciegas, «sin decidir» (Q-VD-3c, 0,71;
      [`ivd/estado_qvd3c.md`](ivd/estado_qvd3c.md), [`ivd/decision-jev-qvd3c.md`](ivd/decision-jev-qvd3c.md)). En su segunda
      pasada, el revisor dio ese estado por no neutral. Le faltaban dos hechos a favor de «aparte»: que HL7 añade campos nuevos
      al final de un segmento (v2.5.1, CH02.txt:1117), y que MSH-22 y MSH-23 los definen los esquemas de IRIS de versiones
      posteriores, así que no son campos locales (los pasajes que citaba en contra tratan de extensiones locales). Le faltaba uno
      a favor de «dentro»: Q-VD-1 cuenta la estructura como la da IRIS. Y traía frases que empujaban hacia «sin decidir»;
    - con eso, qué regla va en el titular (Q-VD-3d, [`ivd/estado_qvd3d.md`](ivd/estado_qvd3d.md),
      [`ivd/decision-jev-qvd3d.md`](ivd/decision-jev-qvd3d.md)): la del ANTES (0,69, confianza 0,38), con las otras dos como
      sensibilidad.
  - **Se heredan las de la 30 y la 31,** con Q-MV-2 y Q-MV-4: un segmento que la versión no define va aparte. En la 2.5.1 es uno
    sin tabla de atributos en su texto; sin texto, uno que el esquema de IRIS de esa versión no trae.
- **El aparato es el de la 31 con la versión,** escrito aparte: el de la 31 no cambia.
  - Una copia de la clase de IRIS que resuelve la estructura en la versión pedida y lista los segmentos de su esquema
    ([`ivd/Lab.IVD.Validar.cls`](ivd/Lab.IVD.Validar.cls)).
  - Dos copias del conductor, hechas por [`ivd/hacer_validar_ivd.py`](ivd/hacer_validar_ivd.py):
    [`ivd/validar_ivd251.py`](ivd/validar_ivd251.py), con las tablas del texto de v2.5.1, y
    [`ivd/validar_ivdst.py`](ivd/validar_ivdst.py), sin texto.
  - Dos lecturas: la de la 31 con el texto de v2.5.1 ([`ivd/lectura_ivd251.py`](ivd/lectura_ivd251.py), de
    [`ivd/hacer_lectura_ivd.py`](ivd/hacer_lectura_ivd.py)), con sus citas fijas llevadas a sus líneas de v2.5.1; y la de Q-VD-1
    ([`ivd/lectura_ivdst.py`](ivd/lectura_ivdst.py)).
  - El texto de v2.5.1 se lee con los analizadores de la 30 por una carpeta de enlaces con los nombres de fichero de v2.5
    ([`ivd/hacer_vista_251.sh`](ivd/hacer_vista_251.sh), [`ivd/texto_ivd.py`](ivd/texto_ivd.py)). Sus tablas:
    [`ivd/TABLAS-TIPO-IVD251.json`](ivd/TABLAS-TIPO-IVD251.json); los valores no se publican.
- **El control** ([`ivd/control_ivd.py`](ivd/control_ivd.py), [`ivd/CONTROL-IVD.json`](ivd/CONTROL-IVD.json)) dio TODO BIEN
  antes de correr, y otra vez tras la revisión, con tres mutantes más:
  - 45 mutantes en bases de la 2.5.1, la 2.6 y la 2.8, cada uno con sus lugares, su clase y su «cuenta»;
  - las dos lecturas, sobre las filas del control: el veredicto de los 45 mutantes y de las 6 bases (51);
  - dos controles negativos de la versión, con el conductor de la 31: MSH-22 y MSH-24 con valor en la 2.8 (N-C1), y OBX-23 en la
    2.5.1 (N-C3). Con su versión no dan nada que cuente; contra v2.5, el error de más campos;
  - N-C2, en cada versión: MSH-30, que ninguna define, da solo el error de más campos, y la lectura lo pone aparte;
  - dos corridas iguales de cada conductor.
- **La previsión se selló antes de correr** ([`ivd/PREVISION-IVD.json`](ivd/PREVISION-IVD.json),
  [`ivd/estado_prevision_ivd.md`](ivd/estado_prevision_ivd.md),
  [`ivd/decision-jev-prevision-ivd.md`](ivd/decision-jev-prevision-ivd.md)), con todo lo anterior
  ([`ivd/SELLO-IVD.txt`](ivd/SELLO-IVD.txt)). Lo que cambió después tiene su versión sellada en [`ivd/sellada/`](ivd/sellada/),
  y la intermedia (la de «sin decidir», del segundo bloque del sello) en [`ivd/intermedia/`](ivd/intermedia/).
- **El cruce y las cifras:** [`ivd/cruce_ivd.py`](ivd/cruce_ivd.py), [`ivd/CRUCE-IVD.json`](ivd/CRUCE-IVD.json) y
  [`ivd/CIFRAS-IVD.json`](ivd/CIFRAS-IVD.json).

## Las cifras

| Versión | Muestras | Válidas | Inválidas | Sin decidir | Se lee con |
|---|---|---|---|---|---|
| 2.5.1 | 44 | 14 | 11 | 19 | el texto de v2.5.1 |
| 2.6 | 108 | 7 | 94 | 7 | el esquema de IRIS |
| 2.8 | 64 | 0 | 30 | 34 | el esquema de IRIS |
| 2.3 | 6 | 0 | 6 | 0 | el esquema de IRIS |
| 2.4 | 1 | 0 | 0 | 1 | el esquema de IRIS |
| **Total** | **223** | **21** | **141** | **61** | |

Por grupo: conversores, 1 válida, 34 inválidas y 28 sin decidir (63); VXU, 20, 39 y 26 (85); MDM, 0, 68 y 7 (75).

**Las tres respuestas a Q-VD-3** (`q_vd_3_las_tres_respuestas`):

| Q-VD-3 | Válidas | Inválidas | Sin decidir |
|---|---|---|---|
| **«aparte» (la del ANTES, en el titular)** | **21** | **141** | **61** |
| «sin decidir» (Q-VD-3c) | 8 | 141 | 74 |
| «dentro» | 8 | 174 | 41 |

Las 13 válidas que dependen de la respuesta (`validas_que_dependen_de_q_vd_3`) son de VXU de la 2.5.1. Su MSH trae 23 campos:
- MSH-22 y MSH-23 con valor, que v2.5.1 no define (MSH tiene 21 campos en su texto);
- en MSH-21, el perfil «Z22^CDCPHINVS».

## Frente a la 31

- **Ninguna inválida de la 31 sale válida.** 140 siguen inválidas.
- **21 pasan de sin decidir a válidas.** Son 21 de las 22 que la 31 dejaba sin decidir solo por MSH-12. La que falta, de VXU de
  la 2.6, queda sin decidir por PID-15 (tabla 0396): sin el texto de la 2.6, el valor no se lee.
- **29 pasan de inválidas a sin decidir:** 21 de conversores y 7 de MDM de la 2.8, y 1 de VXU de la 2.6. Lo que las hacía
  inválidas contra v2.5 venía de la versión; en la suya, lo que queda es una tabla sin decidir.
- **32 siguen sin decidir y 1 pasa a inválida:** una de VXU de la 2.3, por NK1-7 y ORC-7 (obligatorios según IRIS) y la longitud
  de PID-10.

## Por qué son inválidas

Los errores que cuentan son obligatorios (455), longitudes (117) y estructura (61) (`errores_sostenidos_por_clase`).
- **MDM de la 2.6, las 64,** con varios a la vez: TXA-12 vacío en 53, un error de estructura en EVN en 47, OBR-4 en 46 y PID-5
  en 45. Solo una lo es por un único lugar.
- **VXU de la 2.6:** RXA-4 en 14, RXA-6 en 11 y ORC-1 en 9.
  - En 4, lo único es que IRIS echa en falta PID donde hay un EVN, que VXU_V04 de la 2.6 no espera ahí.
  - En esas 4 y en `mdm/ms-MDM-T02-03.hl7` (2.3), la estructura se cierra en ese error y los campos quedan sin evaluar
    (`muestras_con_campos_sin_evaluar`). Las 5 son inválidas, y sus errores de campo son un mínimo.
- **Conversores de la 2.8:** OBX-4 en 21, 17 de ellas solo por eso; MRG-1 en 6. De esto trata el apartado siguiente.
- **La 2.5.1, leída con su texto:** RXA-4 en 6 y la longitud de MSH-10 en 6 (5 de VXU y 1 de conversores).

## El contraste con v2.5.1 (no es veredicto)

En las versiones sin texto, cuenta lo que el esquema de IRIS hace obligatorio. Frente a la OPT del mismo campo en el texto de
v2.5.1, la versión más cercana que el laboratorio tiene (`contraste_obligatorios_sin_texto_frente_a_v251`):
- **el esquema de la 2.8 hace obligatorio OBX-4** en 26 muestras (21 de conversores, 3 de MDM y 2 de VXU);
- **el de la 2.6 hace obligatorio OBX-5** en 33 (30 de MDM, 2 de conversores y 1 de VXU);
- en v2.5.1 los dos son condicionales (v2.5.1, CH07.txt:2531 y 2533), como en v2.5 (CH07.txt:2534 y 2536). Si la 2.6 o la 2.8
  los hicieron obligatorios no se puede leer: su texto no está;
- **20 inválidas lo son solo por OBX-4** (17 de conversores y 3 de MDM, de la 2.8). Sin él quedarían sin decidir, porque también
  tienen tablas sin decidir: ninguna válida cambia;
- y en la de VXU de la 2.3, NK1-7 y ORC-7, que v2.5.1 da como opcional y como «B».

Lo medido en la 30 y la 31 fue el esquema de v2.5 de IRIS. Esto es donde los de versiones posteriores se apartan del texto más
cercano.

## Sin decidir

- **Sistemas de codificación fuera de la 0396 impresa,** en el tercer componente de campos CE y CWE: PID-10 en 45, PID-22 en 39,
  PID-15 en 25, EVN-4 en 20, y OBR-31, OBR-4 y TQ1-3 en 7 u 8. En la 2.5.1 es Q-IV-D-11 de la 30 (el texto permite extender las
  tablas de HL7, v2.5.1, CH02.txt:542); sin texto, Q-VD-1.
- **MSH-9.3 sin estructura en el esquema de su versión,** en 23: se validan con la de la 0354, como en la 31, y MSH-9.3 queda sin
  decidir.

## Lo que va aparte

133 muestras tienen algo aparte, un 60 % (`muestras_con_algo_aparte`):
- **La pasada de repeticiones** (Q-VD-3b), medida en las filas, en la variante que manda, como en la 31
  (`pasada_de_repeticiones`). 132 muestras dan «el segmento tiene más campos de los que permite la estructura»:
  - 40 de la 2.5.1 (MSH en 39 y PV1 en 1);
  - 67 de la 2.6 (MSH en 45, TXA en 16, RXA en 4 e IN2 en 2);
  - 21 de la 2.8 (ROL en 12, OBX en 7 y ARV en 2);
  - 4 de la 2.3 (MSH en 3 y EVN en 1).

  De ellas, 99 son inválidas por otras causas, 20 quedan sin decidir y 13 son válidas.
- **8 PRT en `cv/ms-ORU-R01-01.hl7`** (2.5.1): v2.5.1 no lo define (no tiene tabla de atributos), y van aparte (Q-MV-2 y
  Q-MV-4). La muestra es inválida por otras causas.
- **2 errores con una forma que el conductor no reconoce** (`otras_formas_que_el_conductor_no_reconoce`). Las dos muestras son
  inválidas por otras causas, pero la pasada se cortó ahí, y sus errores de esa pasada son un mínimo:
  - en `vxu/lfh-Hl7ImmunizationFHIRConversionTest__L661.hl7` (2.5.1), de estructura: IRIS echa en falta un RXA dentro de un
    grupo;
  - en `cv/lfh-sample_unix.hl7` (2.6), de longitud, en MSH.

## Las nuevas

| Nueva | Campo | Muestras en su versión | Laboratorio (la 30) | Con algún válido | Estado |
|---|---|---|---|---|---|
| L-1 | PV1-3 | 2 inválidas por otra regla (PRB; OBX-4), 1 sin decidir | válidos | sí | intacta |
| L-11 | PID-11 | 3 inválidas por otra regla (OBX-3 y OBX-5; OBX-4) | válidos | sí | intacta |
| L-22 | PV1-52 | 2 inválidas por otra regla (OBX-4), 1 sin decidir | válido | sí | intacta |
| VX-M14 | RXA-6 | 1 inválida por otra regla (RXA-4, 2.6) | sin decidir | **no** | intacta |
| VX-M15 | RXA-20 | 6 inválidas por otra regla (RXA-1, RXA-2, RXA-4, OBX-11, ORC-1…; 5 de la 2.6 y 1 de la 2.5.1) | sin decidir | **no** | intacta |

- Ninguna queda afectada: ninguna muestra es inválida por una regla en el campo de la nueva.
- VX-M14 y VX-M15 siguen como en la 31: con su `nota_ivm` en `vx/CLASES-VX3.json`, que no cambia.
- La muestra de VX-M15 de la 2.5.1 se lee con su texto, y sigue inválida: MSH-10 más largo que su LEN, ORC-1, RXA-4 y RXA-6.
- Con cualquiera de las tres respuestas a Q-VD-3, VX-M14 y VX-M15 siguen sin ningún mensaje válido.

## La previsión

Acertó 10 de 11: 8 de 9 la propia y 2 de 2 la de Jev (`prevision` en CIFRAS-IVD.json).
- **Acertaron:**
  - las válidas por versión: 2.5.1, 32 %, en 10-70; 2.6, 6,5 %, en 0-50; 2.8, 0 %, en 0-40;
  - el total de válidas (9,4 %, en 3-45), de inválidas (63 %, en 15-80) y sin decidir (27 %, en 10-75);
  - lo que va aparte (59,6 %, en 0-60, por poco);
  - las nuevas sin ningún válido (2).
- **Los intervalos eran anchos:** los de porcentaje, de 40 puntos o más; el de las inválidas que salen válidas, de 5 a 70
  muestras.
- **Falló** cuántas inválidas de la 31 saldrían válidas: se previeron 25 (5 a 70) y son 0. Las válidas salieron de las que la 31
  dejaba sin decidir solo por MSH-12, no de las inválidas.
- **Jev** previó menos de un 20 % de válidas y las dos nuevas sin ningún válido.

## Lo que pasó por el camino

**Antes de sellar:**
- **El control cazó un fallo de la lectura sin texto.** Contaba como error un segmento que la versión no define, y la lectura de
  la 2.5.1 lo ponía aparte, como la 31. Ahora las dos lo ponen aparte.
- **El analizador de las tablas de atributos de la 30 no leía la fila de OBX-5.** Su tipo, «varies», no casaba con el patrón, y
  OBX-5 se quedaba con la fila de una tabla de ejemplo (CH07.txt:7624 en v2.5: TS, 26, R). Aquí admite «varies». En la 30 y la 31
  no hubo ningún error en OBX-5, así que lo publicado no cambia.

**Escrito después de correr** (fuera del sello): el cruce y sus cifras, con el contraste con v2.5.1.

**Tras la revisión a ciegas** (un lector, dos pasadas: la primera pidió cambios con dos bloqueantes; la segunda, con uno),
declarado en el sello:
- **Q-VD-3, dos preguntas más** (arriba). La primera versión de este resultado no decía que 13 de las 21 válidas dependían de
  ella. Tras la tercera pregunta («sin decidir») el resultado llegó a llevar 8 válidas en el titular. Con la cuarta vuelve la
  regla del ANTES, y las otras dos van como sensibilidad.
- **La lectura de la 2.5.1, que es la de la 31, descartaba la clase X sin anotarla.** Ahora anota aparte los campos de más y las
  otras formas que el conductor no reconoce, como la de sin texto. Ningún veredicto cambia: son los de la lectura sellada
  (`veredictos_iguales_que_la_lectura_sellada`).
- **La pasada de repeticiones se mide en las filas,** como en la 31. Las cifras de lo aparte de la primera versión de este
  resultado (94 muestras, un 42 %) no contaban las 40 de la 2.5.1.
- **Q-VD-1 decía «las de usuario, aviso», y el aparato lo leyó como «la tabla que el esquema de IRIS trae vacía, aviso».** El
  estado de Q-VD-1 decía que IRIS trae vacías las tablas de usuario, y no es exacto: trae algunas con valores, como la 0001 de
  PID-8 (el control lo midió antes de sellar, N-T4), y esas quedan sin decidir. Ningún veredicto cambia: ninguna muestra queda sin
  decidir solo por tablas que el índice de v2.5.1 da como de usuario (`sin_decidir_solo_por_tablas_de_usuario_en_v251`).
- **El control se amplió** con N-C2, N-C3 y el negativo de N-C3, y dio otra vez TODO BIEN.
- **Las versiones selladas** de lo que cambió (las dos lecturas, su generador, el control y su resultado) están en `ivd/sellada/`,
  y las intermedias, con el cruce, en `ivd/intermedia/`: así se pueden comprobar todos los bloques del sello.
- **Los menores:** la cifra de MSH-10, las 4 de VXU con PID, las dos formas que el conductor no reconoce, la versión de las citas
  de las reglas del receptor, el alcance del control, la frase de los intervalos y la redacción de las tablas en el README.

## Lo que no dice

- **«Según IRIS» no es «según el estándar».** En 179 muestras lo que cuenta es lo que da el esquema de IRIS de su versión. El
  contraste dice dónde ese esquema se aparta del texto más cercano.
- **13 de las 21 válidas dependen de Q-VD-3,** y la respuesta tiene argumentos en el texto en los dos sentidos. Las tres cifras
  están arriba.
- **Sin decidir no es válido,** ni inválido. Sin texto, una tabla que IRIS trae con valores queda siempre sin decidir.
- **El alcance del control:**
  - no tiene bases de la 2.3 ni de la 2.4 (7 muestras);
  - ningún mutante distingue en la lectura el texto de v2.5.1 del de v2.5 (N-C3 distingue el esquema);
  - el negativo que pedía el ANTES («una base de la 2.8») se hizo con un mutante de esa base (N-C1).
- **Las reglas del receptor** que cita el ANTES (CH02.txt:932-935 y 1143-1147) son líneas de v2.5; en v2.5.1 son
  CH02.txt:908-911 y 1104-1108.
- **El juez no cambia:** lee las muestras como v2.5. Esto dice qué son en su versión.
- **Las muestras son de prueba:** los proyectos las escribieron para ejercitar su conversor, no como mensajes completos.
- **El veredicto de cada muestra** está en el laboratorio. Como en la 30 y la 31, se publican sus agregados, el cruce y las
  cifras, no las filas.
- **La frase del «Hecho cuando»** es la primera de este resultado.
