# Diseño a ciegas de la etapa 37: el juez deja de contar mal las dos conductas de la 36

Diseñador: Fable, a ciegas (7-nov-2026). Lo fijado está en `fase12/ANTES-ETAPA-JUEZ.md`; las dos conductas, en
`fase12/RESULTADO-CANDIDATAS.md`. Las rutas van relativas a la raíz del laboratorio; `fase12/` es la carpeta del juez (en el clon
público, `verificador/`). Las líneas citadas del juez son las del commit `16a9294` de `fase12`.

Lo que leí: el ANTES y el resultado de la 36; `conversion.py`, `conversion_vxu.py` y `conversion_mdm.py` en lo que toca a PID-8,
tablas y sobrantes; `prueba_conversion.py`, `prueba_conversion_vxu.py` (índice) y `cv/ci/prueba_ci.py` (lo que mira de las bases);
`cv/cv3_clases.py`; `md/rejuicio_md.py`; `cv/ci/hacer_bases.py`, `base_nc.sh`, `cv/ci/CI.md` y `ejemplo-ci/ci/hacer_base.sh`; las tres
bases publicadas de la CI; las hojas `PID_Patient.csv` y `MSG_ADT_A01.csv`; el ConceptMap de la 0001 y el de ADT_A01; y de v2.5,
la 0001, el ejemplo de la perra, las estructuras ADT y los segmentos ACC y PDA. **No leí** `cv/juzgar_cv2.py` ni
`cv/cv3_mecanismos.py` (no estaban en la lista): lo que dependa de cómo asignan mecanismo y firma va marcado como no comprobado.

## 0. Lo que el juez hace hoy, medido en el código

| Conducta | Dónde | Qué hace |
|---|---|---|
| PID-8 fuera de la 0001, convertido | `conversion.py:697-702` (`_genero`) | cuenta `valor_imposible_convertido` (clase `valor_imposible_aceptado`, `tabla=True`) y, si el código no es de FHIR, además `fhir_invalido`; los dos se funden en un hallazgo (`_fusionar`, 141-157) |
| PID-8 fuera de la 0001, no convertido | `conversion.py:696-703` | nada: ni cuenta ni nota |
| NK1-15 fuera de la 0001 (VXU) | `conversion_vxu.py:1011-1015` | lo mismo que PID-8, sin el `fhir_invalido` aparte (sale después, 1019) |
| PID-8 fuera de la 0001 y el conversor rechaza | `conversion.py:1382-1383` (`_imposibles`) | PID-8 es «valor imposible»: el rechazo es aceptable (Q-CV-D-7); VXU y MDM lo heredan (`conversion_vxu.py:189`, `conversion_mdm.py:223`) |
| Las demás tablas de usuario (0002, 0004, 0007, 0069, 0078; 0162, 0163, 0550, 0063 en VXU) | `_codigo_tabla` 863-880, `_uso` 639-658, `_tabla` y `_ruta_sitio` de VXU | fuera del ConceptMap: **nota** `convencion` (o `version` fuera de 2.5) |
| Las tablas HL7 con `required` (0085, 0123, 0322, 0271, 0136) | `_estado` 666-678, VXU `_status` 554-564, MDM 709, PID-30 734 | fuera de la tabla: `fhir_invalido` o `valor_imposible_convertido`; no cambian: son tablas HL7, no de usuario |
| Observation de más en ADT | `conversion.py:350-356` (`emparejar`) y `1527-1532` (`_juzgar`) | la k-ésima Observation con k ≥ número de OBX es sobrante `inventado`, hecho `OBX`; cuenta `recurso_inventado` con el texto «sin origen propio en el mensaje» y la cita de `C["OBX"]`, que es `[G MSG_ORU_R01.csv:67-69]` |
| Perfil de PID-8 | `conversion.py:1540` | «fuera de la 0001: ausente» |

Solo la 0001 recibe trato de tabla cerrada. Es la única tabla de usuario del juez con ese trato; la 0136 de PID-30 (M-35, L-25) es
tabla HL7 (`CH02.txt:6705`) y queda como está.

## 1. Qué hace el juez después, en cada caso

### 1.1 PID-8 fuera de la 0001 (y NK1-15 en VXU)

La 0001 es de usuario y sus valores son sugeridos (`Ch03.txt:5033-5044`: «Refer to User-defined Table 0001 … for suggested
values»); la `S` está en el ejemplo mismo de v2.5 (`Ch03.txt:10866`). La guía lleva PID-8 a `gender` por la 0001
(`PID_Patient.csv:14`) y su ConceptMap solo trae F, M, O, U, A y N, sin `unmapped` (`ConceptMap-table-hl70001-to-administrative-gender.json`).
`Patient.gender` lleva binding `required` a `administrative-gender`. Por la regla del estudio, lo que el estándar permite y la guía
no fija es convención. El juez pasa a tratar la 0001 como trata la 0002 o la 0007 (`_codigo_tabla`, 876-878):

| Caso | Después | Cita |
|---|---|---|
| Convertido a un código de `administrative-gender` (`S` → `unknown`, `other`…) | **nota** `convencion` en PID-8: «Patient.gender: 'unknown' para 'S', fuera del ConceptMap (la 0001 es user-defined)». Con MSH-12 ≠ 2.5, nota `version`, como en `_uso` | `[CM table-hl70001-to-administrative-gender]`, `[G PID_Patient.csv:14]`, `[E3 Ch03.txt:5034]` |
| Convertido a un código que no es de FHIR (`S` → `S`) | **cuenta** `fhir_invalido` en PID-8 (clase `fidelidad`), solo eso: «Patient.gender: 'S' fuera de administrative-gender (required)». No depende de la tabla: cuenta también fuera de 2.5, como hoy | `[F Patient.gender required]` |
| No convertido (`gender` ausente) | como hoy: nada (Q-JZ-5) | — |
| En minúscula de un código de la 0001 (`f`) | sin cambio (AMB-CV-1, J2) | — |
| El conversor rechaza el mensaje | según Q-JZ-1 | — |

La `fhir_invalido` ya la daba el juez; lo que desaparece es el `valor_imposible_convertido` y, con él, el sufijo
`aceptado_imposible` del veredicto (`conversion.py:1477-1478`) en esas evidencias. Una evidencia cuyo único hallazgo era ese pasa
de `fallo_silencioso` a `correcto`.

NK1-15 (`conversion_vxu.py:_genero`) recibe el mismo cambio: es la misma tabla, el mismo mecanismo y la misma guía
(`segment-nk1-to-relatedperson` por la 0001).

### 1.2 Las demás tablas de usuario

Ninguna otra recibe trato distinto: `_codigo_tabla`, `_uso`, `_tabla` y `_ruta_sitio` ya dan nota de convención. El cambio no las
toca. Las tablas HL7 con binding `required` (0085, 0123, 0322, 0271, 0136) no son tablas de usuario y quedan como están.

### 1.3 Un recurso de un segmento que la guía no mapea (ADT)

**Cómo lo reconoce.** La hoja de ADT_A01 lista ACC y PDA con la columna «Primary Target» vacía (`MSG_ADT_A01.csv:78` y `:81`); los
ConceptMap `message-adt-*-to-bundle` del paquete no los citan. Las estructuras de v2.5 los admiten: ACC en A01, A03, A04, A05, A08,
A13 y A31 (`Ch03.txt:269, 467, 565, 660, 986, 1359`); PDA en A01, A02, A03, A04, A08 y A13 (`Ch03.txt:275, 357, 469, 571, 992,
1365`); A11 (ADT_A09) no lleva ninguno. El juez tiene, como datos, la lista de segmentos que la hoja lista sin destino
(`SIN_DESTINO_ADT`, con la línea de la hoja de cada uno; alcance según Q-JZ-4) y reconoce una Observation sobrante como salida de
uno de ellos **por un dato igual** (Q-JZ-3): algún valor primitivo del recurso (fuera de `id`, `meta`, `fullUrl`, `reference`,
`system`, `url`, `display`, `text`: L-CV-9) coincide con un componente no vacío del segmento, con estas reglas:

- un TS del segmento (ACC-1, PDA-4, PDA-7) coincide con un `date`/`dateTime` del recurso si las partes que trae el TS
  (`MR.partes_dtm`) son las del valor FHIR, sin desplazar;
- un código (CE.1 o CE.4 de ACC-2, ACC-4, PDA-1) coincide con un `coding.code`;
- un texto (ST, XCN.1-3, PL.1-4, XAD.1-3) coincide literal, y solo si tiene tres caracteres o más;
- los ID de la 0136 (ACC-5, ACC-6, ACC-10, PDA-3, PDA-6, PDA-9) no sirven para reconocer: `Y` y `N` coinciden con cualquier cosa.

Microsoft saca de ACC una Observation `injury-incident` con `effectiveDateTime` = ACC-1 (`RESULTADO-CANDIDATAS.md`): la fecha la
reconoce. Lo que PDA produce en Microsoft no lo he visto (no leí salidas): si solo lleva indicadores Y/N, no se reconoce y sigue
como `recurso_inventado`; el rejuicio lo medirá (§6).

**Qué dice y qué cita.** Según Q-JZ-2. Con la recomendación (cuenta, subtipo nuevo):
- hecho: el segmento (`ACC`, `PDA`), no `OBX`;
- clase `fidelidad`, subtipo `recurso_sin_mapa`;
- texto: «Observation urn:uuid:… de ACC (ACC-1 = 20260102), que la guía lista sin destino en ADT»;
- citas, explícitas en el hallazgo y no por `C["OBX"]`: `[G MSG_ADT_A01.csv:78] ACC sin destino`, `[CM message-adt-a01-to-bundle:
  sin ACC]`, `[E3 Ch03.txt:269] ADT_A01 [ACC]`, `[E6 CH06.txt:5588] ACC`; para PDA, `[G MSG_ADT_A01.csv:81]`, `[E3 Ch03.txt:275]` y
  `[E3 Ch03.txt:8914]`.

Una Observation sobrante que no coincide con ningún segmento sin destino sigue siendo `recurso_inventado`, hecho `OBX`, con el
texto de hoy, y su cita pasa a ser la de ADT (`[G MSG_ADT_A01.csv:46-47] OBX → Observation[3]`) solo si Jev lo admite en Q-JZ-2
(opción con hecho nuevo); si no, no se toca, para no mover nada fuera de las dos conductas.

**Dónde no cambia.** ORU no tiene segmentos sin destino que den Observation: una Observation sin OBX sigue `inventada` (y L-CV-15).
VXU y MDM juzgan sus sobrantes en su módulo (`conversion_vxu.py:441-447`, `conversion_mdm.py:523-527`) y no cambian. La
Observation de PD1-7, que la guía sí mapea (`MSG_ADT_A01.csv:19`) y el juez hoy cuenta como inventada por no contarla en `n_obx`,
**no se arregla**: es otro fallo del juez (fuera de la etapa) y queda escrito como límite (L-CV-18).

## 2. Decisiones abiertas (las decide Jev)

**Q-JZ-1. PID-8 fuera de la 0001 en `_imposibles` (el rechazo aceptable).**
- A: se queda. Un conversor que rechaza un mensaje con PID-8 = `S` sigue en «rechazo aceptable» (Q-CV-D-7). El juez dice entonces
  que, con un valor fuera del mapa, tanto convertirlo (convención) como rechazarlo (aceptable) son defendibles; el cambio toca
  solo evidencias con Bundle. Hechos: ningún caso de las bases de la CI es un rechazo por PID-8; en las pruebas, el rechazo
  aceptable se ejercita con PID-7 (`prueba_conversion.py:210`).
- B: se quita (también en NK1-15, que no está en `_imposibles`, y en los `imposibles` de VXU y MDM, que lo heredan). Un rechazo
  por PID-8 = `S` pasa a `rechazo_incorrecto`. Hechos: la 0001 es de usuario (`Ch03.txt:5034`) y un valor local es legal en
  v2.5; pero el ANTES fija que cambien solo los veredictos de las dos conductas, y esta es la cara de rechazo de la primera: hay
  que decidir si es la misma conducta. Abre evidencias que no sé contar (no leí las de rechazo).

**Q-JZ-2. El recurso de un segmento sin destino: qué es.**
- A: cuenta, con subtipo nuevo `recurso_sin_mapa` (clase `fidelidad`), hecho el segmento, texto y citas nuevos. S-CV-5 pasa a
  nombrar nueve clases. En el rejuicio se reconoce por el subtipo. En `cv3_clases.py`, M-28 solo sigue teniendo casos si
  `juzgar_cv2.asignar` le da MC-ORU-7 al hallazgo nuevo; si no, hace falta un bloque 8 (§5).
- B: cuenta como `recurso_inventado`, con hecho el segmento y texto y citas nuevos. Sin subtipo nuevo; la palabra «inventado» queda
  para dos cosas distintas (sin origen y con origen sin mapa). Mismo riesgo con `asignar` por el hecho.
- C: nota `fuera_proyeccion` (no cuenta), como la de L-CV-7. Hechos: la guía calla y FHIR no prohíbe recursos de más; pero la 36
  dijo que la nota de L-CV-7 «no le cabe» (la guía no crea ese recurso), y el estudio tiene M-28 como ya declarada, que cuenta:
  M-28 se vacía en el corpus del estudio y D pasa de 31 a 30; el estudio sellado y la 36 se contradicen con una marca.
- D: nota `convencion`. Como C, y además C sube de 16 a 17 si el corpus del estudio tiene un caso (lo tiene: las muestras
  `ms-ADT` con ACC o PDA).

**Q-JZ-3. Cómo se reconoce el segmento de origen.**
- A: por un dato igual (§1.3). Una Observation de ACC o PDA sin ningún dato reconocible sigue como inventada (falso «inventado»).
- B: por presencia: toda Observation sobrante de un ADT que trae un segmento sin destino se atribuye a los que trae, listados. Una
  Observation inventada de verdad queda escondida en cuanto el mensaje lleva un ACC (falso «sin mapa»).
- C: por dato y, si no coincide y el mensaje trae un solo segmento sin destino, por presencia. Mezcla los dos errores, menos cada
  uno.

**Q-JZ-4. Qué segmentos reconoce.**
- A: solo ACC y PDA, los dos de la 36.
- B: los 18 que la hoja de ADT_A01 lista sin destino (ARV, UAC, OH1-OH4, PRT, DB1, IAM, DRG, GT1, IN2, AUT, RF1, UB1, UB2, ACC,
  PDA), con la línea de cada uno. Misma regla de dato igual; más oportunidades de coincidencia de texto (GT1 lleva nombres y
  direcciones).
- C: B y además cualquier segmento que la hoja no lista (Z y los de otras versiones). La guía «no mapea» también esos; su
  legalidad en la estructura no se juzga (L18, Q-MV-4).

**Q-JZ-5. PID-8 fuera de la 0001 y `gender` ausente.**
- A: nada, como hoy y como `_codigo_tabla` con un código fuera del ConceptMap sin coding. Cero diferencias en el rejuicio.
- B: nota `convencion` «ausente para 'S'». Aparecen notas nuevas en evidencias que hoy no cambian; entran en la conducta 1 y en
  la cuenta C del estudio.

**Mi recomendación, aparte:** Q-JZ-1 A (el cambio queda en las evidencias con Bundle y la asimetría es coherente: fuera del
mapa, convertir y rechazar son defendibles); Q-JZ-2 A (es lo que la 36 dejó fijado, cuenta y tiene nombre propio, y el rejuicio lo
reconoce por el subtipo sin leer textos); Q-JZ-3 A (el juez no adivina: lo que no puede ligar a un dato se queda como estaba, y la
medida dice cuánto queda); Q-JZ-4 B (la lista sale de la hoja, no de los dos casos vistos); Q-JZ-5 A.

## 3. El cambio en el código, por funciones

`fase12/conversion.py`:
- `Juicio.nota(self, subtipo, hecho, que, certeza="literal", citas=None)`: pasa `citas` a `_h`. Compatible: sin el argumento, lo
  de hoy.
- `_genero(J, m, v, obs)`, rama `t == FUERA` (697-702): si `obs is None`, nada (Q-JZ-5 A); si `obs in GENERO_FHIR`, nota
  `convencion` (o `version` si no `J.v25`) con las citas de §1.1; si no, `J.cuenta("fhir_invalido", …)` sola. **`C["PID-8"]` no se
  toca:** `_cit` alimenta las citas de todos los hallazgos de PID-8 y cambiarla movería `valor_distinto`, `dato_perdido`… fuera de
  las dos conductas. La cita de v2.5 va explícita en la nota.
- `_imposibles(m, familia)` (1382-1383): según Q-JZ-1.
- `SIN_DESTINO_ADT = {"ACC": ("[G MSG_ADT_A01.csv:78] …", …), "PDA": (…), …}` (alcance Q-JZ-4) y
  `_origen_sin_mapa(m, r) -> segmento | None`: los valores primitivos del recurso frente a los componentes de cada segmento presente
  con las reglas de §1.3. Devuelve el primer segmento que coincide, en el orden del mensaje.
- `emparejar`, rama `adt` (350-356): antes del recorrido por `k`, las Observation sobrantes que `_origen_sin_mapa` liga pasan a
  `sobrantes` con `motivo: "sin_mapa"`, `hecho: <segmento>` y el dato que las ligó; el resto sigue como hoy (`origen_guia` para
  `k < n_obx`, `inventado` después), con `k` contado sobre las que quedan.
- `_juzgar` (1527-1532): `motivo == "sin_mapa"` → `J.cuenta("recurso_sin_mapa", s["hecho"], texto, citas=SIN_DESTINO_ADT[seg])`
  (Q-JZ-2 A). Las demás ramas, intactas.
- `PERFIL_GUIA_ADT` (1540): «por la 0001; vacío: ausente (Q-CV-D-3); fuera de la 0001 (user-defined): convención; un código fuera
  de administrative-gender: FHIR inválido». Fila nueva: `Observation (de un segmento sin destino)`, campo `ACC/PDA…`, regla «la
  hoja lo lista sin destino: recurso sin mapa, reconocido por un dato igual», nivel `cuenta`, citas de `SIN_DESTINO_ADT`.
- `S_CV["S-CV-5"]`: añade «recurso sin mapa». `L_CV`: `L-CV-17` (solo se reconoce por un dato igual; sin dato, inventado) y
  `L-CV-18` (la Observation de PD1-7 no se empareja y sale inventada: fallo conocido, fuera de la 37). `C`: claves nuevas `ACC`
  y `PDA` con esas citas (añadir claves no cambia ningún hallazgo existente: ningún hecho se llama así hoy).
- La categoría (1472-1482) no cambia: `recurso_sin_mapa` es `fidelidad` → `convertido`.

`fase12/conversion_vxu.py`: `_genero` (1005-1020), la rama `FUERA`, igual que en ADT; `imposibles` solo si Q-JZ-1 B.
`fase12/conversion_mdm.py`: nada (el Patient lo juzga `CV._patient`; `imposibles` solo si Q-JZ-1 B).
`fase12/mcp_verificador.py`: nada; su huella cambia sola.

Nada más del juez se toca. En particular no se toca `_fusionar`, `_estado`, `_codigo_tabla` ni los sobrantes de ORU, VXU y MDM.

## 4. Las pruebas, en rojo antes

Se escriben y se corren **antes** de tocar el juez; la salida en rojo se guarda en `fase12/jz/ROJO-JZ.txt` (las líneas `MAL` de
cada prueba nueva y las que cambian); después, `TODO BIEN`, con las cifras del clon público.

`fase12/prueba_conversion.py`:
- **P-CV-29, PID-8 fuera de la 0001:** (a) `S` → `unknown`: `cuentan == []`, `convencion` en notas, categoría `correcto`;
  (b) `S` → `other`: lo mismo; (c) `S` → `S`: `cuentan == [("fidelidad", "fhir_invalido", "PID-8")]` y ningún
  `valor_imposible`; (d) `S` sin `gender`: según Q-JZ-5; (e) MSH-12 2.8 y `S` → `unknown`: nota `version`, `cuentan == []`;
  (f) con otro hallazgo de fidelidad al lado, el veredicto es `("fallo_silencioso", "convertido")`, sin `aceptado_imposible`;
  (g) controles sin cambio: `F` → `male` (`valor_distinto`) y `f` → `female` (nota AMB-CV-1); (h) el rechazo con PID-8 = `S`,
  según Q-JZ-1. Hoy fallan (a), (b), (c), (e), (f).
- **P-CV-30, Observation de un segmento sin destino:** (a) A01 con `ACC|20260102|…` y una Observation de más con
  `effectiveDateTime` 2026-01-02: `cuentan == [("fidelidad", "recurso_sin_mapa", "ACC")]`, cita `[G MSG_ADT_A01.csv:78]` en el
  hallazgo, y «sin origen propio» no está en su `que`; (b) la misma Observation sin ACC en el mensaje: `recurso_inventado` en
  `OBX` (control, no cambia); (c) ACC presente y una Observation que no comparte ningún dato: `recurso_inventado` (Q-JZ-3 A);
  (d) A02 con `PDA||||20260103…` y una Observation con esa fecha: `("fidelidad", "recurso_sin_mapa", "PDA")`; (e) A01 con un OBX,
  un ACC y dos Observation, la de ACC primera en el Bundle: la de ACC es `recurso_sin_mapa` y la del OBX, nota `origen_guia`, en
  ese orden y en el inverso; (f) MSH-12 2.8: (a) cuenta igual (no depende de las tablas de 2.5); (g) ORU con una Observation de
  más: `recurso_inventado` en `OBX`, sin cambio. Hoy fallan (a), (d), (e), (f).
- **P-CV-12** («control X fusionado», 417-420): pasa a esperar `{"fhir_invalido"}` solo. **P-CV-15** (457): el ejemplar de
  `valor_imposible_convertido` pasa a PID-30 `NO` → `deceasedBoolean false` (la 0136 es tabla HL7, `conversion.py:734`). Hoy, con
  el juez nuevo, fallarían como están: se cambian antes, y en rojo fallan contra el juez viejo.

`fase12/prueba_conversion_vxu.py`: **P-VX-24,** NK1-15 `S` → `gender unknown` en el RelatedPerson: nota `convencion`,
`cuentan` sin `NK1-15`; control `F` → `male`: `valor_distinto`.

`fase12/jz/prueba_rejuicio_jz.py`: el clasificador de §6 sobre una línea base sintética y un «ahora» sintético: una diferencia
de la conducta 1 (Microsoft: `valor_imposible_convertido+fhir_invalido` → `fhir_invalido`; LinuxForHealth: el hallazgo desaparece
y entra la nota), una de la conducta 2 (sale `(OBX, recurso_inventado)`, entra `(ACC, recurso_sin_mapa)`), una fuera (PID-5
`valor_distinto`) y una evidencia sin diferencia: espera 1, 1, 1 y la salida 1 por la de fuera; y el control de §6 sobre tres
evidencias sintéticas espera «fuera». En rojo, el módulo no existe.

`fase12/jz/comprobar_bases_jz.py` (§7) lleva su control negativo dentro: una copia de la base con un hallazgo ajeno añadido tiene que
salir con 1.

Convención de las pruebas de aquí: cada caso muta una sola cosa y lleva su control, los Bundles se escriben a mano
(`prueba_conversion.py:3-6`).

## 5. Lo que puede cambiar en las clases del estudio (`cv/cv3_clases.py`)

El guion sellado se corre tal cual sobre el juicio del corpus del estudio rejuzgado con el juez nuevo
(`python3 cv/cv3_clases.py <juicio nuevo> <minimos> <evidencias> fase12/jz/CLASES-JZ.json`) y se compara `frase`, `clases[*].casos`,
`sin_clase` y `convenciones` con el JSON sellado de la etapa 33 (`ga/CLASES-GA-v2.json`). Lo previsto, regla a regla:

| Clase | Mecanismo en `R` | Qué pasa |
|---|---|---|
| M-16 (Microsoft copia `S`) | `fuera:Patient.gender\|fhir_invalido` y `…\|fhir_invalido+valor_imposible_convertido` | el hallazgo fundido pasa a `fhir_invalido` solo: sigue encajando por el primer mecanismo; la cadena compuesta deja de aparecer, sin efecto. **Sigue ya declarada** |
| M-28 (Observation de PDA o ACC) | `MC-ORU-7`, casos `ms-ADT*` | depende de qué le da `juzgar_cv2.asignar` al hallazgo nuevo: **no comprobado**. Si sigue siendo `MC-ORU-7`, no cambia nada. Si da otra cosa (`fuera:Observation\|recurso_sin_mapa` o parecido), M-28 se queda sin casos, sale en `sin_clase` y D pasaría de 31 a 30. Remedio con precedente: un **bloque 8** en `cv3_clases.py`, bajo el sello de la 33 como el bloque 7 de la 36, que añade el mecanismo nuevo al conjunto de M-28; con él, D sigue en 31 |
| L-12 (`N` → `unknown`) | `fuera:Patient.gender\|valor_distinto` | `N` está en la 0001: no cambia |
| M-35, L-25 (PID-30 `NO`) | `…deceasedBoolean\|valor_imposible_convertido` | la 0136 es tabla HL7: no cambian |
| M-18 (PDA sin datos → deceasedBoolean) | `fuera:Patient.deceasedBoolean\|dato_inventado` | es un campo del Patient, no un recurso: no cambia |
| Convenciones (C = 16) | notas `convencion` por (conversor, hecho, firma) | entra una clave nueva de LinuxForHealth en PID-8 por cada firma distinta de la nota nueva, si el corpus del estudio tiene un PID-8 fuera de la 0001 convertido: el par mínimo `M02-genero-fuera-de-tabla` está en `minimos` y `cap3-36-A04-completada` en `adt` (las bases de la CI los traen). **Previsión: C pasa de 16 a 17** (una clave; más si `firma` no quita el valor, que no he comprobado). Microsoft no añade ninguna: copia `S` y eso cuenta |
| Nuevas (N = 15) | — | ninguna regla `nueva` depende de los dos mecanismos: **15 sigue** |
| `muestras_aceptadas` | por clase, en diez muestras de Microsoft | puede mover un hallazgo de M-16 (sigue en ya_declarada) y los de M-28 (según `asignar`) |

Cómo se decide: con la comparación de los dos JSON. Cada diferencia tiene que explicarse por una de las dos conductas (una clave
nueva de convención en PID-8; M-28 y su mecanismo). Lo que cambie en 15/31/16 va al `RESULTADO-JUEZ.md` y, con una marca, a
`cv/RESULTADO-CV3.md`, como hizo la 36 con M-28. `ga/CLASES-GA-v2.json` y `ga/CIFRAS-GA-B.json` no se tocan.

## 6. El rejuicio

**Herramienta:** `fase12/jz/rejuicio_jz.py`, que importa de `md/rejuicio_md.py` `evidencias`, `fila` y `CAMPOS` y no lo modifica.
Añade lo que la 26 no necesitaba: clasificar las diferencias. Normaliza la ruta de cada evidencia desde el segmento `privado/`,
para que la línea base pueda hacerse desde una copia del árbol de antes.

**Línea base con el juez de antes:** `python3 md/rejuicio_md.py linea_base privado/jz/base-antes.jsonl <las carpetas que rejuzgó la
26>` corrido con `conversion*.py` en el estado de `16a9294` (antes de tocar nada; `git status` limpio en los tres ficheros), y
`informes_base` igual. El registro guarda la huella del juez viejo (`ff9f10876b91…`, la de las bases de la CI). Si hay que
rehacerla después, desde un `git worktree` de ese commit: `rejuicio_jz.py` acepta la base con rutas de cualquiera de los dos
árboles.

**Comparación con el nuevo:** `python3 jz/rejuicio_jz.py comparar privado/jz/base-antes.jsonl <carpetas> -o privado/jz/REJUICIO-JZ.json`
rejuzga con el juez de la carpeta; para cada evidencia con `guardado` distinto saca el conjunto de hallazgos que salen y que entran
(tuplas de `CAMPOS`) y el cambio de veredicto, y la clasifica:

- **conducta 1** si todos los hallazgos que cambian tienen hecho `PID-8` o `NK1(…)-15`, sus subtipos están en
  {`valor_imposible_convertido`, `fhir_invalido`, `convencion`, `version`} y el veredicto, si cambia, solo pierde
  `+aceptado_imposible` o pasa de `fallo_silencioso` a `correcto` cuando no queda nada que cuente;
- **conducta 2** si el mensaje es ADT y trae un segmento de `SIN_DESTINO_ADT`, todos los hallazgos que cambian tienen hecho `OBX` o
  ese segmento con subtipos en {`recurso_inventado`, `recurso_sin_mapa`, `fuera_proyeccion`} (el caso (e) de P-CV-30: la del OBX
  deja de ser inventada), y el veredicto no cambia (con Q-JZ-2 C o D, además `fallo_silencioso` → `correcto`);
- **las dos**, si lo anterior se cumple por partes disjuntas;
- **fuera** en cualquier otro caso: nombra la evidencia, el conversor y lo que entra y sale. Una sola «fuera» es la regla de parada
  del ANTES; el guion sale con 1.

El resumen va por conducta × conversor × corpus (la ruta de la evidencia da `privado/<carpeta>/<conversor>/<corpus>/…`), y es lo
que el ANTES mide. `punto_vc` no debe cambiar en ninguna (el punto de entrada no se toca): se comprueba como en la 26.

**La previsión (se sella antes de correr con el juez nuevo):** conducta 1 en toda evidencia de LinuxForHealth con PID-8 fuera de la
0001 convertido (en el corpus de la CI son dos de 458: `adt/cap3-36-A04-completada` y `minimos/M02-genero-fuera-de-tabla-caso`,
`LINEA-BASE-linuxforhealth.json`), en toda la de Microsoft donde copia `S` (M-16; cambia el subtipo fundido, no la categoría) y
en los VXU con NK1-15 fuera de la 0001; conducta 2 en los ADT de Microsoft con ACC (los 30 del corpus del laboratorio que vio la
33, y las muestras `ms-ADT` con ACC o PDA) cuya Observation comparte un dato con el segmento. Cuántas son en total no lo sé desde
aquí: no leí las evidencias. El juguete no cambia en nada (sus bases no tienen PID-8 ni Observation sobrantes en ADT).

**El control:** `python3 jz/rejuicio_jz.py control privado/jz/base-antes.jsonl <carpetas>` inyecta, como `md/rejuicio_md.py:128-141`,
un `valor_distinto` en PID-5 (`CV._patient`) y otro en RXA-20 (`CVX._status`), y además una tercera inyección **dentro** de la
conducta 1 pero con el veredicto mal (un `valor_distinto` en PID-8). El control pasa solo si la comparación ve diferencias en
todas las evidencias con PID y con RXA, las clasifica **todas como «fuera»** (ninguna como conducta 1 ni 2) y sale con 1. Es el
control negativo del clasificador: un cambio ajeno a las dos conductas no se cuela como una de ellas. Se corre antes de la
comparación de verdad.

## 7. La integración continua

**Lo que cambia y lo previsto.** Las tres bases de la demostración se rehacen con `base_nc.sh` (unos 50 minutos; `hacer_bases.py` ya
exige dos corridas iguales, el `igual` y el positivo sembrado). Previsión, de las bases publicadas: en
`LINEA-BASE-linuxforhealth.json` y `LINEA-BASE-linuxforhealth-mensaje.json` cambian **dos casos** (`adt/cap3-36-A04-completada` y
`minimos/M02-genero-fuera-de-tabla-caso`): pierden el hallazgo `['PID-8', 'valor_imposible_aceptado', 'valor_imposible_convertido']`
y su `subtipo` pasa de `convertido+aceptado_imposible` a `convertido`; la categoría sigue `fallo_silencioso`; `n_casos` sigue en 458.
`LINEA-BASE-juguete.json` no cambia en ningún caso (390). En las tres cambia `creada_de.juez.huella`. Si la base guarda también las
notas (no leí `linea_base.py`), en esos dos casos entra además la nota de convención: también es conducta 1.

**La comprobación de cada base:** `fase12/jz/comprobar_bases_jz.py <base de HEAD> <base nueva>`: la diferencia campo a campo (la que
`base_nc.sh` imprime al final) tiene que caber en: `creada_de.juez.*`, y en `casos.<k>` solo hallazgos con hecho `PID-8`/`NK1…-15` y
los subtipos de la conducta 1, o hecho `OBX`/segmento sin destino con los de la 2, y los `subtipo` de veredicto previstos. Sale con
1 ante cualquier otra ruta. Se guarda su salida en `fase12/jz/BASES-JZ.json`.

**Pushes, por la opción B (guarda limpia, higiene, revisión a ciegas y Jev antes de cada uno):**

1. **Push 1, el laboratorio:** el juez y sus pruebas, las tres bases rehechas con su comprobación, `RESULTADO-JUEZ.md`,
   `RESULTADO-CANDIDATAS.md` con la línea de que el juez ya no cuenta mal, la marca en `cv/RESULTADO-CV3.md` (y el bloque 8 de
   `cv3_clases.py` si hace falta), `cv/ci/CI.md` (una línea en «lo que cambia desde…»: el juez cambió, regenera la base) y README y
   «About» al día. `prueba_ci.py` tiene que seguir en verde: p12 mira la huella del **conversor** y el nombre de la base, p14 el
   formato, el `n_casos` y el id; nada de eso cambia. Ensayo: `ensayo_flujo.py` sobre el índice para `demo-ci.yml` (sus tres jobs:
   el juguete `igual`, el sembrado `falla`, LinuxForHealth `igual` con la base nueva) y sobre el clon para `ejemplo-ci.yml` y
   `rojo-ci.yml`, que siguen fijados al commit viejo y corren el juez viejo: verde sin cambios. Después del push,
   `comprobar_publicado.py` con los tres `ENSAYO.json` y la corrida de Actions en verde.
2. **Push 2, el pin del ejemplo:** `uses:` y `laboratorio_ref` de `ejemplo-ci.yml` y `rojo-ci.yml` al commit del push 1;
   `ejemplo-ci/ci/LINEA-BASE.json` y `LINEA-BASE-propio.json` rehechas con `hacer_base.sh` (cuenta los casos sola; el defecto
   `F → male` de `DEFECTO.json` sigue dando `valor_distinto` en PID-8, que no cambia); la diferencia de las dos bases del ejemplo
   con las de antes, pasada por `comprobar_bases_jz.py` (lo previsto: solo la huella del juez, salvo que el conversor del ejemplo
   convierta un PID-8 fuera de la 0001, que no sé). Ensayo sobre el clon (el commit fijado tiene que estar en él) de los tres
   flujos; después del push, `comprobar_publicado.py` y Actions en verde. El run en rojo se lanza a mano una vez y tiene que fallar
   solo por su hallazgo.

Cada push lleva su `ENSAYO.json` y su `PUBLICADO.json` en `fase12/jz/`.

## 8. Riesgos y lo que el arreglo no ve

- **`juzgar_cv2.asignar` y `cv3_mecanismos.firma` no los leí.** Si el mecanismo del hallazgo nuevo no es MC-ORU-7, M-28 pierde sus
  casos hasta el bloque 8; si `firma` conserva el valor, C sube más de uno. Las dos cosas se ven al correr `cv3_clases.py`.
- **La cita por `C`.** Cualquier cambio en `C["PID-8"]` u `C["OBX"]` mueve las citas de hallazgos ajenos: la regla de parada. Las
  citas nuevas van explícitas en cada hallazgo (de ahí el parámetro `citas` de `Juicio.nota`).
- **El reconocimiento por dato** no ve una Observation de PDA que solo lleve indicadores, ni una de ACC sin ACC-1 ni código: siguen
  como inventadas (Q-JZ-3). Un texto corto repetido por casualidad puede ligar de más; el umbral de tres caracteres lo acota, no
  lo quita.
- **La Observation de PD1-7** sigue contándose como inventada (L-CV-18): es otro fallo del juez y queda fuera; si el mensaje trae
  además ACC, la de PD1-7 no se confunde con la de ACC porque no comparte dato con él.
- **El orden del Bundle:** hoy la k-ésima Observation se da por del k-ésimo OBX; el arreglo saca antes las ligadas a un segmento sin
  destino, y eso puede cambiar cuál queda como `origen_guia`. Entra en la conducta 2 solo en mensajes con ACC o PDA; fuera de
  ellos, el orden es el de hoy.
- **La cara de rechazo** (Q-JZ-1): con A, el juez admite convertir y rechazar un mismo valor; con B, cambian evidencias que no he
  contado.
- **Evidencias de otras versiones:** con MSH-12 ≠ 2.5 la nota es `version`, no `convencion`, y no entra en C.
- **Lo que no cambia y podría parecer que sí:** las tablas HL7 con `required` (PID-30, OBX-11, OBR-25, RXA-20, TXA-17) siguen dando
  `valor_imposible_convertido` o `fhir_invalido`; y las convenciones de minúscula (AMB-CV-1).
- **Tiempo:** el rejuicio de las 21.892 evidencias se corre tres veces (base, control, comparación) y las bases 50 minutos; en
  primer plano o con `systemd-run`, nunca fiándose del aviso.
