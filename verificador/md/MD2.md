# MD2: el corpus, la previsión y las corridas de MDM (etapa 26)

## MD2-a: el corpus

**Qué hay.** Las bases son las del §5 de `md/diseno-md.md`, el diseño escrito a ciegas de lo que devuelven los conversores. Ninguna
sale de la salida real de MD-pre, y ningún conversor ha corrido sobre ellas: eso es MD2-c, después de la previsión sellada.

- **`bases_mdm.py`.** Tiene la forma de `bases_vxu.py` y escribe dos cosas:
  - las 40 bases B01..B40 del §5.2, en `bases_mdm/BNN.hl7`, segmentos separados por CR y sin MLLP;
  - su índice, `bases_mdm.jsonl`.
- **Las cargas binarias.** Se generan con `base64` y `binascii` desde cadenas sintéticas (`SINTETICO-NN-…`); ninguna se escribe a mano.
- **El texto.** Cada OBX, cada línea y cada NTE lleva su palabra ancla única, `ZetaNNKKJJ`.
- **Las órdenes.** `--lista`, `--firma`, `--cobertura`, `--autoprueba` y `--longitudes`. Esta última es informativa.
- **Las cuatro secundarias.** `--secundario` escribe S01..S04 en `bases_mdm_secundario/`, para la alternativa de Q-MD-D-1. Son B01, B02,
  B05 y B08 como MDM^T04, T06, T08 y T10, con estructura MDM_T02. Cambian MSH-9.2, EVN-1 y MSH-10.
  - En T06 y T10 llevan además TXA-13, que ahí es obligatorio. El padre es otro documento (`DOC0902`, `DOC0908`), no el propio TXA-12.
  - No entran en las 40, ni en la huella, ni en `n["mdm"]`.
  - Con la decisión de Jev (solo T02) salen fuera de alcance. Se juzgan con `conversion_mdm.PE_ALTERNATIVA_EVENTOS`, que es la
    alternativa.
- **La herramienta** (`md/parche_corpus_mdm.py`, DV-MD-4):
  - `CORPUS` gana `mdm` al final;
  - `generar_corpus` escribe la carpeta `mdm` con las 40 bases, todas por `mdm_conv`;
  - `prueba_vc.p06` cuenta 40 más (343 → 383 sin mínimos). Es el cambio declarado del §7.

**Las cifras.**

| | |
|---|---|
| Bases | 40 (B01..B40), 350 segmentos, 61 OBX; 2 en UTF-8 (B22, B39) |
| Autoprueba | TODO BIEN, 1.096 comprobaciones |
| Firma mínima entre pares | 12 campos distintos (B07-B18), sin MSH-7, MSH-10 ni EVN-2; ningún par difiere solo en lo que ejercita una de las dos |
| Huella del conjunto (`bases_mdm.HUELLA`) | `601bd787aa4bf28b88a9fb6ea00c6d599c7216faac970374ab5c221974099050` |
| Huella de la carpeta `mdm` en el corpus (`por_corpus["mdm"]`) | `eb0064ab52fd…` |
| Huella conjunta del corpus del laboratorio, sin mínimos | `842f80f67007…`; cambia porque entra `mdm`, como estaba declarado |
| `adt`, `oru`, `vxu` y `huella_adt_oru_muestras` | iguales a las de antes: `7b4e7cfba041`, `b5be5675b204`, `3bcb0eefe4dd`, `f2321d41fe7e`; n = 263, 40 y 40 |
| `CORPUS.index` de los seis de antes | sin cambio (0..5) |

**La autoprueba (§5.1.4).** Cada base:

- se lee como un solo mensaje;
- da `MDM_T02` con `mdm_conv` y se empareja con la gramática sin ausentes ni fuera de orden;
- tiene EVN-1 = MSH-9.2 y TS válidos (también PPN.15 y TQ1-7);
- tiene en sus tablas TXA-3, 17, 18 y 19, OBX-2, ED.2/RP.3, ED.3/RP.4 y ED.4;
- tiene cada ED.5 válido para su ED.4 y de 65.536 caracteres como mucho;
- solo lleva texto no ASCII con MSH-18 UTF-8, y los apellidos son de la lista cerrada;
- cumple las cuatro condiciones de TXA: TXA-3 con OBX, TXA-7 si TXA-17 no es DI, TXA-11 si hay TXA-7, y TXA-5 si hay TXA-4 (DV-MD-6).

Las secundarias pasan lo mismo con el punto de acuse `mdm`, que las acepta. Además se comprueban la firma, la cobertura, el
determinismo y la huella.

**La cobertura.** `--cobertura`, contra `PERFIL_GUIA_MDM`, sale completa.

- **Las filas que cuentan.** Las 39 tienen una base con el campo valorado y, si es opcional en 2.5, otra con el campo vacío. «OBX-n (T)»
  se lee por tipo: una base con un OBX de tipo T y otra sin él. ORC y OBR, opcionales como grupo, faltan en B08 y B40.
- **Las tablas.**
  - 0271 entera: AU 32, LA 2, DI 2, y PA, IP, DO e IN, una cada uno.
  - 0272: U 36, R 1, V 1 y vacío 2.
  - 0273: AV 35, vacío 2, y UN, CA y OB, una cada uno.
  - 0299: Base64, A (B14) y Hex (B15).
  - TXA-3: TEXT 31, IM 5, AP 3 y multipart 1.
- **Los tipos de OBX.** Bases con cada tipo: TX 27, ED 9, FT 4 y RP 3, más CE y ST (B25).
- **Los recuentos.**

  | Qué | Valores en el corpus |
  |---|---|
  | Grupos de orden | 0 (B08, B40), 1 (36 bases), 2 (B28), 3 (B29) |
  | NTE bajo un OBX | 0, 1 (B26), 2 (B27) |
  | Repeticiones de TXA-9 y de TXA-10 | 0 (B40), 1, 2 (B35) |

  TXA-2 toma catorce valores: los trece de la 0270 que usa el corpus y el local `ZX`.

**Lecturas tomadas al escribir las bases (el §5.2 callaba).**

- **El documento corriente.** Las bases que no ejercitan esos campos llevan lo de un documento real:
  - TXA-6 con hora y zona `+0100`;
  - un autor (TXA-9) y un autenticador asignado (TXA-10);
  - el fichero (TXA-16, `/docs/<año>/<tipo><NNNN>.<ext>`, que en B01 es `/docs/2023/alta0001.txt`);
  - TXA-18 U, TXA-19 AV y TXA-17 AU («AU B01 y otras», §5.2).

  El §5.3 dice que `txa()` tiene por omisión vacíos salvo 1, 2, 3, 12 y 17; lo demás lo pasa cada base, y B40 es la que no pasa nada.
  Las ocho de control llevan todo lo mapeado (§5.1.3).
- **ORC-1.** Es `RE` en todas, y `SC` en B32: ORC-5 se usa con ORC-1 SC o SR ([E4 CH04.txt:2475-2478]).
- **Los pacientes.** Son seis, `DOC0001`..`DOC0006` (`mateo` es el del §5.3); dos llevan una segunda repetición PI. En B01, PID-3 y TXA-12
  valen los dos `DOC0001`, como en las piezas comunes del diseño.
- **B30.** El NTE bajo OBR lleva su propia ancla, `Zeta300000`.

**Lo que no se tocó, aunque llama la atención.** Ninguno de estos puntos es una desviación; quedan para MD3 si hiciera falta.

- **Las longitudes de 2.5.** TXA-3 tiene longitud 2, pero la propia 0191 trae `TEXT` y `multipart`: pasa en 38 bases, y es una
  incoherencia del estándar. El TXA-12 de B36 (`DOC0036^CSSYN^1.2.840.113619.2.1^ISO`, el literal del diseño) tiene 36 caracteres
  frente a 30. La autoprueba no exige longitudes; `--longitudes` las lista.
- **CA y OB en un T02 (B11 y B12).** Según la figura 9-2, un T02 deja el documento disponible o no disponible. CA y OB son de la tabla
  0273, pero raros en un original. Se mantienen porque son la rama de R-MD-8 que el diseño quiere ejercitar.

**Desviación declarada.**

| DV | Qué | Por qué |
|---|---|---|
| DV-MD-6 | Las bases con TXA-17 distinto de DI llevan TXA-7 (transcripción) y TXA-11 (transcriptor). B40, «solo TXA-1, 2, 3, 12 y 17», lleva TXA-17 DI. | El estándar los exige: TXA-7 con TXA-17 distinto de «dictated» ([E9 CH09.txt:1030-1035]), TXA-11 en todo documento transcrito (§9.6.1.11). El §5.1.4 pide todas las bases válidas; sin ellos, un rechazo del conversor sería legítimo y el juez lo contaría como incorrecto. Es del estándar, no de la salida de ningún conversor. |

**Las suites.** `md/suites_md.sh` sale entero en verde (`privado/mdm/md1a/SUITES-MD2A.txt`); la suite gana la autoprueba de
`bases_mdm`.

- `prueba_conversion_mdm.py`: las 27 pruebas, con 261 comprobaciones. P-MD-24 y P-MD-26 pasan a verde.
- `cv/prueba_vc.py`: 152 comprobaciones.
- El resto, como en MD1: la regresión de 2.721 sale CASA, y la concordancia de A1 no cambia.

**El rejuicio.** Con el juez de MD2-a (`f4fef60400e2`):

- **Evidencias:** 21.892, con 0 diferencias.
- **El punto de la herramienta:** solo cambia en los 150 MDM.
- **Las corridas:** 137, con el INFORME y el juicio iguales.

La huella del juez cambia respecto a MD1 (`7b5dab748075`) por dos textos: DV-MD-6 en `conversion_mdm.DV_MD` y la REVISION del MCP
(DV-MD-0..6). Es la huella con la que se sella la previsión.

## MD2-b: la previsión sellada

`md/prevision-mdm.json` quedó sellada en `2de3064` (sha256 `b24d3ae28f16…`) antes de que ningún conversor viera las 40 bases.
Lleva el juez `f4fef60400e2` y el corpus `601bd787aa4b`.
- **La del programador** (`md/prevision-cuerpo-mdm.json`, sha256 `8bcd52504deb…`) es la tabla de §6.2 del diseño. Se corrigió solo
  con lo visto en E-MD-3 y MD1-a, sobre los 38 MDM_T02 públicos, y se fijó antes de leer a Jev. Da 0,9 a al menos una nueva
  confirmada en alguno de los dos.
- **La de Jev,** con un estado neutro (`md/estado_prevision_mdm.md`):
  - al menos una nueva y confirmada, «sí» con 0,87;
  - siete o más, 0,71, y ninguna, 0,26;
  - en los dos conversores, 0,78.

## MD2-c: las corridas y el juicio

Los dos conversores, en su caja, con `cv/verificar_conversor.py` sobre el corpus del laboratorio, ya con `mdm`, sin mínimos y sin
sensibilidad de conversión. La salida está en `privado/mdm/md2c/`: Microsoft tardó 3,2 min y LinuxForHealth 17 s, con 383 casos
cada uno.

**Las categorías en las 40 bases:**

| | `correcto` | `fallo_silencioso` | `rechazo_incorrecto` | `indeterminado` | Previsto |
|---|---|---|---|---|---|
| Microsoft | 0 | 39 | 1 (B33) | 0 | fallo 90-100 %, rechazo 0-5 %: **dentro** |
| LinuxForHealth | 0 | 40 | 0 | 0 | fallo 85-100 %: **dentro** |

**Lo que cuenta, por mecanismo (bases):**
- **Microsoft:**
  - **MC-MD-21:** `PV1-3 dato_perdido` en 38 bases.
  - **MC-MD-11:** `TXA-3 dato_perdido` en 38, sin `contentType`.
  - **MC-MD-9, 14, 15 y 17:** `OBX-5 dato_perdido` en 38. El contenido no llega; el texto va a `Observation`.
  - **MC-MD-6:** `TXA-6 dato_perdido` en 37, sin `date`.
  - **MC-MD-19:** `ORC-1 dato_perdido` en 37, sin `context.related`.
  - **MC-MD-18:** `NTE-3` en 2 (B26 y B27).
  - **MC-MD-2:** `TXA-19` en 2. En B10, UN sin conservar; en B12, OB con `entered-in-error`.
  - **MC-MD-22:** `MSH-9 incorrecto` en B33. Microsoft rechaza un TS repetido (`…+0100~…+0100`).
  - **MC-MD-17:** `OBX-5 fhir_invalido` en B40, sin `content`.
- **LinuxForHealth:**
  - **MC-MD-21:** `PV1-2 valor_distinto` en 40, `PV1-44 dato_inventado` en 40 y `PV1-3 dato_perdido` en 39.
  - **MC-MD-5:** `TXA-16 dato_perdido` en 39.
  - **MC-MD-9, 14 y 15:** `OBX-5 dato_perdido` en 16. El FT, el ED y el RP no llegan.
  - **MC-MD-18:** `NTE-3` en 2 (B26 y B27).
  - **MC-MD-2:** `TXA-19` en B10.
  - **MC-MD-12:** `OBX-5 valor_distinto` en B24, `\.br\` crudo con un tipo que no es `text/hl7v2`.
  - **MC-MD-7:** `TXA-10 valor_distinto` en B37. El autenticador sale de TXA-22. El texto del hallazgo dice «la primera»
    porque TXA-10 tiene una sola repetición; la lógica es la de Q-MD-D-11 (b).

**Fuera de previsto: ninguno.**
- Las categorías caen dentro de sus rangos y no hay indeterminados.
- Cada mecanismo que cuenta está en la lista de la previsión.
- Los de PV1 son los ya declarados del estudio de ADT (`cv/CLASES-CV3.json`: M-1, L-2, L-3 y L-5).
- No apareció nada de «lo que no preveo».

**Previsto que no apareció:**
- **MC-MD-1** (`docStatus`). Era la nueva más probable para el diseño, y ninguno de los dos escribe el literal de la 0271 ni
  lo pierde.
- MC-MD-3, 4, 8, 10, 13, 16 y 20.

**La sensibilidad** (`md/sensibilidad_md.py`, en `privado/mdm/md2c/SENSIBILIDAD-MD.json`). Se rejuzgan las evidencias con cada
alternativa de `ALTERNATIVA_MD`:
- **Q-MD-D-6 (b):** con Microsoft aparece `PID-3 dato_perdido` en 39 bases (sin `subject`).
- **Q-MD-D-8 (b):** aparece `OBX recurso_inventado` en 39 bases con Microsoft y en 16 con LinuxForHealth (los `Observation`).
- **Q-MD-D-3 (a):** con LinuxForHealth aparece `OBX-2 valor_distinto` en 26 (`text/plain`).
- **Q-MD-D-9 (a):** el caso B12 de Microsoft cambia de subtipo.
- **Sin efecto en las 40:** Q-MD-D-4, Q-MD-D-11 y Q-MD-D-12. Q-MD-D-1 no puede tenerlo, porque las 40 son T02.

## MD3-r1: la repetición 1 de MD2-c (los arreglos de la revisión adversaria)

Las DV-MD-7..14 están en `md/decisiones-qmd.md`. En este paso no se corrió ningún conversor; las corridas de la repetición van en el apartado siguiente.

**Las pruebas, en rojo antes (`b2a8f15`).** Fallaban 14 comprobaciones de las P-MD y 36 de la autoprueba de `bases_mdm.py`: las 33
bases AU/LA y las secundarias S01, S02 y S03. Con los arreglos pasan las 27 P-MD, con 278 comprobaciones.

| Arreglo | DV | Prueba que cambia |
|---|---|---|
| TXA-22 en las bases AU/LA (H17) | DV-MD-7 | P-MD-26 (TXA-22 en las AU/LA) y la autoprueba de `bases_mdm.py` |
| `authenticator` de TXA-22 con TXA-10 vacío (H8) | DV-MD-8 | P-MD-8: dos casos nuevos (por referencia y solo `display`) y dos controles (otra persona; con TXA-10, H5 sigue contando) |
| `docStatus` de OBX-11/OBR-25 con TXA-17 vacío (H10) | DV-MD-9 | P-MD-2: dos casos nuevos; el control «sin TXA-17» pasa a un `docStatus` sin origen |
| R-MD-14 solo con `data` o `url` (H13) | DV-MD-10 | P-MD-5: un caso nuevo |
| Una cuenta por un `status` equivocado (H20) | DV-MD-11 | P-MD-3: el control «CA con current sin extensión» espera solo `valor_distinto` |
| El pedido padre de OBR-29 (H21) | DV-MD-12 | P-MD-17: un caso y dos controles |
| Grupos idénticos con el mismo número de orden (H22) | DV-MD-13 | P-MD-17: dos casos (uno y tres ServiceRequest) y un control (cuatro, `recurso_duplicado`) |
| OBR-4 CE hasta 2.5 (H7) | DV-MD-14 | P-MD-17: dos casos (2.3 y 2.5) y un control (2.6) |

**El corpus nuevo.**

| | |
|---|---|
| Bases con TXA-22 | 34: las 33 nuevas y B37 |
| Autoprueba | TODO BIEN, 1.205 comprobaciones |
| Firma mínima entre pares | 13 (B07-B18) |
| Cobertura | completa |
| `bases_mdm.HUELLA` | `f954ee625d06cd4030b44a0abb94ff1886a91d0d38349684e1c6a60fff665396` |
| `por_corpus["mdm"]` | `ebb095e3fdfe…` |
| Huella conjunta, sin mínimos | `cd2e753be895…` |
| `adt`, `oru`, `vxu`, `huella_adt_oru_muestras` | iguales |

**El juez nuevo.** Huella `4f9118445c224283c80e1f1a45c08bd0616cfb56e0513c274e202bf0257c507e`; REVISION nombra DV-MD-0..14.

- **Suites:** `md/suites_md.sh` en verde (`privado/mdm/md1a/SUITES-MD3R1.txt`).
- **Rejuicio de ADT, ORU y VXU:** 21.892 evidencias con 0 diferencias. Las 137 corridas dan el INFORME y el juicio iguales, y la línea
  base de VXU (1.008) sigue en 0.
- **Los MDM de MD-pre con su punto:** los dos indeterminados de L370 y L407 desaparecen (H22). Quedan 3 `correcto` y 73
  `fallo_silencioso` en T02.

**Lo que cambia en las evidencias ya guardadas de MD2-c** (`md/r1_diferencias.py`, sin correr conversores; detalle en
`privado/mdm/rejuicio/DIFERENCIAS-R1-MD2C.txt`). Cada arreglo toca lo suyo y nada más.

- **Microsoft:**
  - dejan de contar `dato_perdido TXA-3` en 48 casos (H13), `recurso_ausente ORC-1` 4 veces (H22, dos muestras) y
    `recurso_inventado ORC` una vez (H21);
  - en 2 casos (H20), `dato_perdido` sale de la cuenta doble de TXA-19, que queda solo como `valor_distinto`.
- **LinuxForHealth:**
  - dejan de contar `dato_inventado TXA-10` en 18 casos (H8), `dato_inventado TXA-17` en 8 (H10) y `valor_distinto OBR-4` en 1 (H7);
  - las dos muestras de L370 y L407 pasan de indeterminado a juzgarse (H22) y dejan ver `valor_distinto PV1-2`, el mecanismo de
    ADT que el indeterminado tapaba.
- **Efecto de DV-MD-7 en la repetición:** las bases nuevas llevan en TXA-22 la misma persona que en TXA-10. Si LinuxForHealth
  sigue leyendo TXA-22, su `authenticator` coincidirá con TXA-10 en esas bases; H5 seguirá viéndose en B37.

### Las corridas de la repetición 1

Los dos conversores, en su caja y con el juez final (`4f9118445c22`), se volvieron a correr sobre el corpus del laboratorio con las
40 bases corregidas (`privado/mdm/md2c-r1/`) y sobre las muestras públicas (`privado/mdm/md2c-muestras-r1/`).
- **Microsoft:** 39 `fallo_silencioso` y 1 `rechazo_incorrecto`. Es B33, ya válida con TXA-22, que sigue rechazando por TXA-8
  repetido.
- **LinuxForHealth:** 40 `fallo_silencioso`.

Los 17 hallazgos de MDM que salen están en `md/HALLAZGOS-MD3-r1.json` y son los que clasifica `md/CLASES-MD3.json`. La línea base
de la demostración de integración continua, hecha con el mismo corpus y LinuxForHealth, da los mismos mecanismos y bases.
