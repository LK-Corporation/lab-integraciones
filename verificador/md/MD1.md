# MD1: el punto `mdm_conv` en el juez (etapa 26)

**Qué hay.** El diseño es `md/diseno-md.md`, hecho a ciegas por Sonnet (DV-MD-0), y las decisiones son las de Jev
(`md/decisiones-qmd.md`). Donde Jev y el diseñador difieren, manda Jev: Q-MD-D-1 (solo T02), Q-MD-D-4 (el literal de TXA-17 cuenta
además como `fhir_invalido`) y Q-MD-D-9 (CA y OB, además, con `status` coherente).

- **La gramática.** `MDM_T02` ya estaba en `estructuras_25.json`; no hubo nada que extraer.
- **El punto de entrada.** `mdm_conv` está en `puntos_entrada.py`, debajo de `vxu_conv` (§2.1). El punto `mdm` de acuse no cambia.
- **El juez de MDM.** Vive en `conversion_mdm.py`, que solo usa la biblioteca estándar. Tiene:
  - los grupos de orden y los documentos (un TXA con sus OBX y, a cada OBX, sus NTE);
  - el emparejamiento del §2.2, con DV-MD-1;
  - el perfil «guía» de DocumentReference y ServiceRequest del §4: 46 reglas, de las que 39 cuentan, 2 son convención, 4 nota y 1 forma;
  - las tablas del §4.5 (la 0272, cotejada con el paquete);
  - `PERFIL_GUIA_MDM`, `S_MD`, `L_MD`, `AMB_MD`, `DV_MD`, `DECISIONES_MD` y `ALTERNATIVA_MD` (las ocho Q con confianza ≤ 0,52).
- **Los ganchos.** Hay seis, en `conversion.py`, aplicados con `md/parche_conversion_mdm.py`. Cada uno es una rama `mdm` al lado de
  las de hoy.
- **El servidor MCP.** `mcp_verificador.py` gana `perfil_guia_mdm`, pasa a `SERVIDOR` 1.4, añade `conversion_mdm.py` a la huella y
  nombra `mdm_conv` en las dos descripciones (`md/parche_pe_mcp_mdm.py`).
- **La herramienta.** `punto()` lleva MDM a `mdm_conv` y `L-VC-2` lo dice. El juguete escribe el nominal de MDM y gana
  `JUGUETE-DOCSTATUS` y `JUGUETE-TEXTO` (`md/parche_vc_mdm.py`). `CORPUS` y el corpus de MDM esperan a MD2-a (DV-MD-4).
- **Las pruebas.** Están en `prueba_conversion_mdm.py`: P-MD-1..27, en rojo antes del código (`c103e4f`).

**Lo que no cambia.** El rejuicio (`md/rejuicio_md.py comparar`) da 0 diferencias en las 21.892 evidencias del estudio, y los
INFORME de las 137 corridas salen iguales. Todas las suites de hoy siguen en verde; la única que se toca es `prueba_multitipo.py`
(DV-MD-5).

Los commits son cuatro: `a0e80a2` (MD1-a), `c103e4f` (MD1-b, el rojo), `114aff0` (MD1-d, el código) y el de MD1-e (este informe).

## MD1-a: la salida real, sin perfil

`md/md1a_forma.py` construye el PE del §2.1 en memoria, sin tocar el juez, para que el rojo de MD1-b sea de verdad.

- **El PE.** Pasa `_afirmar`, `MDM_T02` tiene gramática y el contrato del punto `mdm` sale igual.
- **El emparejador.** Pasa un prototipo del §2.2 (el que MD1-d llevó a `conversion_mdm.py`) por las salidas guardadas de E-MD-3:
  los 38 MDM^T02 de las muestras públicas, en cada conversor. El detalle está en `privado/mdm/md1a/FORMA-MD1A.json`.

**Resultado.** Los 76 Bundles se leen. Ninguno pasa de 4.000.000 de caracteres (L-VC-12); el mayor tiene 57.579.

Con la regla literal del §2.2 salió un `indeterminado/emparejamiento` que no lo era. Es `ms-MDM-T02-02`: dos grupos con distinto
placer y el mismo filler `1-1`. Se corrigió el emparejador con esa salida como cita (DV-MD-1), sin tocar el perfil.

Quedan dos indeterminados, los dos en LinuxForHealth: `lfh-Hl7MDMMessageTest__L370` y `__L407`. Cada uno trae tres grupos de orden
idénticos, y sus tres ServiceRequest son iguales. Es lo que declara L-MD-10, como L-VX-14 en VXU.

**La forma del contenido de cada conversor.** Es para el informe de E-MD-3; no toca el perfil.

| | Microsoft | LinuxForHealth |
|---|---|---|
| Bundle y referencias | `fullUrl` `urn:uuid:`; referencias `Tipo/id` | `fullUrl` `Tipo/id`; referencias iguales al `fullUrl` |
| DocumentReference | una por TXA (37); ninguna en el T02 sin TXA (`lfh-…OrderRequest…L378`) | igual |
| `content` | ausente en 26 de 37; en 11, un attachment con solo `creation` (sin `data` ni `contentType`) | siempre uno, con `contentType` `text/plain`; `data` en Base64 solo si hay OBX TX (9) |
| Texto de los OBX TX | no llega a la DocumentReference (48 de 48 faltan); los OBX van a Observation (77) | todos los OBX TX del TXA en un solo attachment, unidos por LF: llegan enteros (48 de 48) |
| NTE bajo OBX | se pierden (3) | se pierden (3) |
| ED (uno, con ED.5 vacío) | sin `data` | sin `data` |
| `subject` / `context.encounter` | nunca / nunca | siempre al Patient / siempre al Encounter |
| `context.related` | nunca a un ServiceRequest (5 apuntan a un Practitioner) | a los ServiceRequest en 33 (5 también a un Practitioner) |
| `masterIdentifier` / `identifier` | 9 / 2 | 9 / 37 (con la copia de TXA-12, PLAC y FILL) |
| `type` | 15, sin `system` | 15 (13 con `v2-0270`) |
| `docStatus` | `preliminary` 13, `P` 2, ausente 22 | `final` 8, `preliminary` 17, ausente 12 |
| `status` | `current` 36, `entered-in-error` 1 | `current` 35, `superseded` 1, `entered-in-error` 1 |
| `author` / `authenticator` | PractitionerRole (22 / 3) | Practitioner (22 / 21) |
| `securityLabel` | v3-Confidentiality (5) | v2-0272 (5) |
| `date` | nunca | 11 |
| ServiceRequest | uno por grupo; con tres grupos idénticos, uno solo; uno de más desde OBR-29 (`ms-MDM-T02-03`) | uno por grupo |
| Otros recursos | MessageHeader, Provenance, Organization, Location, Specimen, Consent, Device, Account, Observation, DiagnosticReport | Observation (15) |

## Las pruebas

**Las 27 pruebas.** `prueba_conversion_mdm.py` tiene 27 pruebas, P-MD-1..27, y dos líneas base:

- **P-MD-1 base:** el contrato del punto `mdm` y la gramática.
- **P-MD-25 base:**
  - (a) las suites de conversiones, VXU y la herramienta;
  - (b) el rejuicio y su control;
  - (c) los INFORME de las corridas;
  - (d) las huellas de `conversion.C`, `conversion.INFO` sin `mdm`, `TIPOS_PROY`, `CVX.TIPOS`, los puntos sin `mdm_conv` y `MAPAS`,
    medidas antes de MDM.

**En rojo, `c103e4f`.** Fallan las 27, cada una por la razón prevista; las dos líneas base pasan.

| Pruebas | Por qué fallan |
|---|---|
| P-MD-2..23 | `PE.resolver` no conoce `mdm_conv` |
| P-MD-1 | `KeyError 'mdm_conv'` |
| P-MD-24 | `mdm_conv` no está en el esquema |
| P-MD-25 | la herramienta lleva MDM a `adt_conv` |
| P-MD-26 | falta `bases_mdm` |
| P-MD-27 | falta `conversion_mdm` |

**Con el código.** Pasan 25 de 27, con 255 comprobaciones. Siguen en rojo, declaradas, las dos que dependen de `bases_mdm.py`
(MD2-a, DV-MD-4):

- **P-MD-24:** solo su parte del corpus (tres comprobaciones). La del MCP, el esquema, `punto()` y el juguete está en verde.
- **P-MD-26:** entera.

La última línea de la suite lo dice: «TODO BIEN salvo lo de MD2-a, en rojo y declarado».

**Pruebas retocadas después del commit en rojo.**

- **P-MD-8 y P-MD-23.** El tercer Practitioner (`pr3`) sale del Bundle por omisión y entra solo donde se usa. Un Practitioner sin
  referencias salía en los `otros_tipos` de P-MD-18.
- **P-MD-20.** Al caso T06 con la alternativa de Q-MD-D-1 le faltaba el Bundle.
- **P-MD-4.** Gana tres comprobaciones de MD1-e (abajo).
- **El fichero.** Se había subido con CRLF; pasa a LF.

## Las suites

`md/suites_md.sh` corre lo de `ve/comprobar.sh` y, además:

- `prueba_conversion.py`, `prueba_conversion_vxu.py`, `cv/prueba_vc.py`, `cv/ar/prueba_ar.py`, `cv/ci/prueba_ci.py` y `vx/rv/prueba_rv.py`;
- las autopruebas de `conversion`, `conversion_vxu`, `bases_vxu`, `mcp_verificador` y `conversion_mdm`.

`ve/comprobar.sh` ya incluye la regresión de 2.721 y la concordancia de A1.

Todas estaban en verde antes del código (`privado/mdm/md1a/SUITES-ANTES.txt`) y siguen en verde después (`SUITES-MD1E.txt`):

- la regresión: 2.721 instancias, CASA;
- la concordancia de A1: 0 cambios;
- `prueba_conversion.py`: 28 pruebas y 116 comprobaciones;
- `prueba_conversion_vxu.py`: 23 pruebas y 153 comprobaciones;
- `cv/prueba_vc.py`: 26 pruebas y 152 comprobaciones.

El único cambio de una suite es el de `prueba_multitipo.py` (DV-MD-5), que sigue con sus 705 comprobaciones.

## MD1-e: el rejuicio

**El aparato.** `md/rejuicio_md.py` está adaptado de `vx/rejuicio_vx.py`. Por evidencia guarda dos cosas:

- el juicio con el punto que trae la evidencia, que tiene que salir igual byte a byte;
- el punto que le da la herramienta, que solo puede cambiar en los MDM.

Además rehace en memoria el INFORME y el juicio de cada corrida de la herramienta (`informes_*`, P-MD-25 c). Puede cambiar lo
declarado: `juez`, `herramienta.huella` y `L-VC-2`. La línea base se hizo antes de tocar nada, con el juez `bde94016ca58` (HEAD
`8502678`).

**El corpus.** 21.892 evidencias en 14 carpetas de `privado`:

- `cv/cv2/ev`, `cv/cv3/ev-minimos` y `ev-minimos-main`, `cv/cv1d`, `cv/vc`;
- `vx/vx2c`, `vx/vxpre`, `vx/vx3`, `vx/rv`;
- `ar`, `ci`, `ci2`, `mant`;
- `mdm/mdpre`.

**Resultado, con el juez final `7b5dab748075`.**

- **Diferencias: 0** en las 21.892 evidencias, contra la línea base. Por el punto guardado: `adt_conv` 16.179, `oru_conv` 3.272 y
  `vxu_conv` 2.441. De las de `adt_conv`, 150 son los MDM de MD-pre y 8 son los VXU de `vx/vxpre`, guardados así antes de VXU.
- **El punto de la herramienta** cambia en 150 evidencias, y las 150 son MDM; en ningún otro mensaje.
- **Las corridas:** 137 (18.830 evidencias), con el INFORME y el juicio iguales.
- **El control:** con un defecto inyectado en `conversion._patient` y otro en `conversion_vxu._status`, el rejuicio ve 17.927
  diferencias: 12.339 de ADT, 3.156 de ORU y 2.432 de VXU.
- **La línea base de VXU** (`privado/vx/rejuicio`, sellada el 25-oct): 1.008 evidencias, 0 diferencias.

**Los MDM de las muestras con su punto nuevo.** Son las 150 evidencias de MD-pre, 75 por conversor.

| Evento | Cuántos | Veredicto |
|---|---|---|
| T02 | 76 | 3 `correcto`, 71 `fallo_silencioso/convertido` y 2 `indeterminado/emparejamiento` (L-MD-10) |
| T05, T06, T09, T10 | 74 | `fuera_de_alcance` (Q-MD-D-1) |

**Las salidas de MD1-a con el perfil puesto.** Lo hace `md/md1e_salidas.py`; el detalle está en
`privado/mdm/md1a/JUICIO-MD1E.json`. Son los hallazgos que cuentan, por conversor y casos.

- **Microsoft (38 T02):** 3 `correcto` y 35 `fallo_silencioso`.
  - Los más frecuentes:
    - `dato_perdido ORC-1` en 33 casos (sin `context.related`);
    - `dato_perdido TXA-6` en 11 (sin `date`);
    - `dato_perdido TXA-3` en 10 (ningún `contentType`);
    - `fhir_invalido OBX-5` en 6 (sin `content`, R-MD-17);
    - `dato_perdido OBX-5` en 4 (el texto no llega).
  - Con menos casos:
    - `dato_perdido PV1-3` (4) y `PV1-6` (2);
    - `fhir_invalido TXA-17` (2: `docStatus` `P`);
    - `recurso_ausente ORC-1` (2: los tres grupos idénticos dan un solo ServiceRequest);
    - `codigo_mal_mapeado PV1-10`, `dato_perdido NTE-3` y `recurso_inventado ORC` (OBR-29), 1 cada uno;
    - `dato_perdido` y `valor_distinto TXA-19` (OB con `entered-in-error`), 1.
- **LinuxForHealth (38 T02):** 36 `fallo_silencioso` y 2 `indeterminado`.
  - Los más frecuentes:
    - `valor_distinto PV1-2` en 36 (Encounter `unknown`, el mecanismo de ADT);
    - `dato_inventado TXA-10` en 18 (`authenticator` desde TXA-22 con TXA-10 vacío);
    - `dato_inventado TXA-17` en 8 (`docStatus` con TXA-17 vacío).
  - Con menos casos:
    - `dato_inventado PV1-44` (4), `dato_perdido PV1-3` (4) y `PV1-6` (2);
    - `dato_perdido NTE-3` (2) y `TXA-16` (2);
    - `dato_inventado TXA-12` (1: EI.3 llevado a `value`, con EI.1 vacío);
    - `valor_distinto TXA-19` (1) y `OBR-4` (1);
    - en PID, 3 hallazgos de ADT.

**Un defecto del juez, no del conversor.** Apareció al rejuzgar y lleva una prueba que fue roja antes del arreglo.

- **El caso.** En `lfh-…DocumentReference…L488`, TXA-12 es `^SYSTEM^<BACKUPID>`: sin EI.1. Microsoft escribe un `masterIdentifier`
  con solo `system`, y el juez lo contaba como `dato_inventado`.
- **El arreglo.** La regla R-MD-3 es de `masterIdentifier.value`. Sin EI.1, un `system` o un `assigner` solos no inventan nada:
  `CV._identifier` tampoco mira CX.4 sin CX.1. Un `value` sin EI.1 sigue contando, y el `que` dice si es EI.2 o EI.3; es el caso de
  LinuxForHealth.
- **La prueba.** Son tres comprobaciones nuevas en P-MD-4; con el código de `114aff0` falla la primera.

**Robustez.** Los 75 mensajes de las muestras se juzgaron con tres salidas ajenas: un Bundle vacío, el genérico del juguete y un
`error`. Son 225 juicios y ninguna excepción.

## Desviaciones declaradas (DV-MD-n)

Están, con su porqué, en `md/decisiones-qmd.md`.

| DV | Qué | Por qué |
|---|---|---|
| DV-MD-0 | El diseño lo hizo Sonnet a ciegas, no Fable. | Fable se quedó sin cupo; Jev eligió un modelo más pequeño y distinto (0,61). |
| DV-MD-1 | En la clave `identifier` del ServiceRequest gana quien comparte más números del grupo; un empate se desempata por OBR-4. | Con la regla literal, `ms-MDM-T02-02` (mismo filler `1-1` en dos grupos) salía indeterminado en los dos conversores (MD1-a). |
| DV-MD-2 | `mdm_conv` sin `conversion` da `indeterminado/sin_salida`, no un error de esquema. | Es lo que hacen hoy `adt_conv`, `oru_conv` y `vxu_conv`. Cambiarlo solo para MDM sería incoherente; para todos, tocaría ADT, ORU y VXU. |
| DV-MD-3 | Las citas de MDM no se registran en `conversion.C`; ORC-1/2/3, OBR-4, PID y PV1 van en `C_SEG`. | P-MD-25 (d) exige `conversion.C` igual. Las funciones reutilizadas de `conversion.py` reciben las citas de MDM al vuelo (`_reusa`). |
| DV-MD-4 | `CORPUS`, `generar_corpus` y `bases_mdm.py` quedan para MD2-a. | Sin `bases_mdm.py`, la carpeta `mdm` rompería la herramienta. P-MD-24 (su parte del corpus) y P-MD-26, en rojo y declaradas. |
| DV-MD-5 | `prueba_multitipo.py` gana `mdm_conv` en la lista de puntos de `info_verificador`. | Como DV-CV-6 y DV-VX-4; el diseño la daba entre los controles que no cambian. |

## Lecturas tomadas al programar (el diseño callaba)

**El MIME y los escapes.**

- **Los parámetros del tipo MIME.** El `contentType` se compara por su tipo, en minúsculas y sin parámetros: `text/plain; charset=UTF-8`
  es `text/plain`. El ejemplo de R4 lleva `charset`.
- **R-MD-23, los escapes crudos.** En un FT son los escapes del OBX-5 original que aparecen tal cual en el texto del attachment.

**El contenido y sus hechos.**

- **Sin `content`.** R-MD-17 absorbe también R-MD-14 (TXA-3): P-MD-14 pide un solo hallazgo.
- **El hecho de R-MD-34.** Es el OBX cuyo texto se encontró en ese attachment; si no hay, el primer OBX con destino.
- **Los NTE.** Se numeran en todo el mensaje (`NTE(j)-3`), como los OBX.
- **ED.5 vacío.** No se espera nada. Es la muestra `ms-MDM-T02-01` (`^application^pdf^Base64^`).
- **Las causas de un ED distinto.** Son codificación doble, truncado o sin convertir, o «ninguna de las dos» si hay un attachment con
  otros octetos y el mismo subtipo. Si no hay ninguno de esos, es `dato_perdido`.
- **La alternativa de Q-MD-D-12.** Busca el valor del OBX en las cadenas de la DocumentReference y sus duplicadas, en los recursos que
  referencian y en el texto de los attachments.

**El ServiceRequest y las referencias.**

- **Los hechos del ServiceRequest.** `status` es `ORC(i)-5` e `intent` es `ORC(i)-1`. Una `context.related` que no resuelve es
  `referencia_rota` en `ORC-1`.
- **`context.encounter`.** Presente con PV1, debe resolver al Encounter; si el Encounter falta, es referencia rota, como en VXU.
  Ausente, es nota `sin_encounter`.

**TXA-17, TXA-18 y TXA-19 fuera de su tabla.**

- **TXA-17.** Con `docStatus`, es `valor_imposible_convertido` con L18, y además `fhir_invalido` si no es de `composition-status`
  (P-MD-21).
- **TXA-18 y TXA-19.** Dan nota (`fuera_de_tabla` o `version`). El diseño solo los nombra para el rechazo aceptable.

**El mensaje y el código.**

- **MSH-9.3 vacío.** Da la nota `estructura_declarada` (P-MD-21).
- **La alternativa de Q-MD-D-1.** Va en los tipos del punto: `conversion_mdm.PE_ALTERNATIVA_EVENTOS`, el mismo punto con T04, T06, T08
  y T10.
- **`recuentos`.** Recibe el emparejamiento entero (`lec`), no solo las entries, para contar el `content` de las emparejadas y las
  duplicadas.
- **P-MD-23, «ocho mutaciones de forma».** Se probaron diez, y cada una da 0 que cuentan.
