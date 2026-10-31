# RESULTADO de la etapa de MDM (26): el verificador juzga la conversión de documentos clínicos MDM^T02, 31-oct-2026. Cerrada

**CERRADA. Corregida el 31-oct (etapa 28):** se retiraron dos de las cinco nuevas (MD-M8 y MD-L7) y una ya declarada
(MD-M7). Se apoyaban en mensajes T02 con TXA-19 «OB» o «UN», estados que la tabla de transiciones del estándar (v2.5,
figura 9-2) no da para T02, que solo admite «Available». Lo decidió Jev (`md/decision-jev-correccion-mdm.md`).

> El verificador encuentra **3 discrepancias nuevas y confirmadas en MDM_T02 en 2 de 2 conversores, sobre 78 mensajes públicos**;
> además ve **9 de las ya declaradas**, y **3 diferencias son convención**.

**Cómo se cuenta.** Como en VXU:
- **N y D cuentan mecanismos.**
- **C cuenta las notas de convención del juez final, por conversor y hecho:**
  - el estado del documento que sale del mapa de la tabla 0271, en los dos conversores;
  - en LinuxForHealth, además, el autenticador tomado de TXA-22 cuando TXA-10 viene vacío.

**La regla de resultado** se escribió antes de medir (`ANTES-ETAPA-MDM.md`). Pedía al menos una discrepancia nueva y confirmada; hay
3, y 2 son fuertes. La etapa concluye que **el juez encuentra algo también en documentos clínicos**.

| | |
|---|---|
| Fecha | 31 de octubre, en la primera de las cuatro sesiones del tope (antes del 20-nov) |
| Conversores | **Microsoft FHIR-Converter:** v7.0 (`253307f`). **LinuxForHealth hl7v2-fhir-converter:** v1.1.0 (Maven Central). Son las mismas versiones y la misma caja del estudio de conversores: sin red, de solo lectura y sin privilegios. Al final, también sus ramas principales: Microsoft `main` (`70fd328`) y LinuxForHealth `master` (`2cb72c2`) |
| Referencia | Guía HL7 v2-to-FHIR 1.0.0 (hojas CSV de `873b331`, ConceptMap del paquete), HL7 v2.5 y FHIR R4 |
| Corpus | 78 mensajes públicos: 40 bases sintéticas en v2.5, válidas en estructura (`bases_mdm.py`, huella `f954ee625d06`); seis llevan en TXA-17 o TXA-19 un
estado que la tabla de transiciones del capítulo 9 no da para T02 (B08 a B12 y B40) y 38 MDM_T02 de los propios proyectos (3 de Microsoft, en v2.8 y v2.3, y 35 sacados de las pruebas de LinuxForHealth, en v2.6) |
| Herramienta | `cv/verificar_conversor.py` (etapa 18), con MDM → `mdm_conv` |
| Juez de los resultados | `4f9118445c22`, servidor 1.4: «etapa de MDM (26)». La previsión se selló con el de `597bd53` (`f4fef60400e2`) |

## La pregunta, y la respuesta

> ¿Encuentra el verificador, en la conversión de mensajes de documentos clínicos MDM_T02 de los dos conversores del estudio,
> discrepancias con la guía v2-to-FHIR o con FHIR R4 que se sostengan con cita, que cambien el significado del dato y que el
> proyecto no tenga ya declaradas?

**Sí: 3, en los dos conversores.** Cada una cumple cuatro condiciones:
- tiene su cita en la guía o en el estándar;
- la revisión adversaria no la tumbó, salvo MD-M5, que tumbó por un defecto del corpus (B33 sin TXA-22). Con la base ya
  corregida, el rechazo sigue, en la corrida nueva y en el par MP1;
- el proyecto no la declara en sus salidas esperadas, sus pruebas, su documentación ni sus issues;
- se reproduce con un par mínimo, en la versión fijada y en la rama principal.

| Id | Conversor | Discrepancia | Fuerza |
|---|---|---|---|
| MD-M5 | Microsoft | Rechaza entero un MDM_T02 válido cuando TXA-8 (fecha de edición, repetible en v2.5) trae dos repeticiones: el documento no llega | fuerte |
| MD-L3 | LinuxForHealth | Con un OBX codificado (CE) delante, el texto de los OBX TX tampoco llega al documento: se pierde el texto clínico | fuerte |
| MD-L5 | LinuxForHealth | Un FT junto a un TX llega con sus órdenes de formato crudas (`\.br\`) en el adjunto `text/plain` | débil |

Los pares mínimos están en `md/pares_mdm.py` y sus resultados, en `md/RESULTADO-MD3-pares.json` (versiones fijadas) y
`md/RESULTADO-MD3-pares-main.json` (ramas principales).

**Retiradas en la corrección.** MD-M8 (Microsoft: TXA-19 «OB» sale `entered-in-error`) y MD-L7 (LinuxForHealth: TXA-19 «UN»,
que la tabla 0273 define como «Unavailable for patient care», sale `current`) se reproducían con sus pares, pero sobre un T02
con un estado que v2.5 no da para T02. «OB» solo cabe en T04, que Microsoft no convierte; «UN» solo en los eventos sin
contenido, que LinuxForHealth no convierte. No cuentan.

**Lo que ya estaba declarado.** Las 9 ya declaradas, con su referencia exacta, están en `md/CLASES-MD3.json`. Entre ellas:
- **Microsoft:**
  - el texto de los OBX va a `Observation` y no al documento;
  - el documento no lleva `date` ni enlace a la orden;
  - todo eso consta en sus propias salidas esperadas de MDM_T02.
- **LinuxForHealth:**
  - los OBX que no son TX no llegan al documento;
  - TXA-16 va a `description`;
  - con TXA-19 vacío, el estado sale de OBR-25;
  - todo eso lo afirman sus pruebas.

**Dos dudosas, que no cuentan:**
- **LinuxForHealth toma el autenticador de TXA-22 aunque TXA-10 traiga otra persona.** La guía lleva TXA-10 a `authenticator`;
  v2.5 define TXA-22 como quien autenticó, que encaja con FHIR, y el proyecto declara leer TXA-22.
- **Microsoft escribe un `DocumentReference` sin `content` cuando falta TXA-6.** Tiene el mismo origen que lo ya declarado.

## La previsión sellada, frente a lo que salió

| | Previsto | Salió |
|---|---|---|
| Categorías, Microsoft | `fallo_silencioso` 90-100 %, `rechazo_incorrecto` 0-5 % | 39 de 40 y 1 de 40: **dentro** |
| Categorías, LinuxForHealth | `fallo_silencioso` 85-100 % | 40 de 40: **dentro** |
| Al menos una nueva confirmada en alguno | programador 0,9; Jev 0,87 | **sí** |
| Cuántas | Jev: siete o más, 0,71; de tres a seis, 0,02 | **3** tras la corrección (5 antes) |
| En los dos conversores | Jev 0,78 | **sí** |
| Al menos una nueva, por conversor | programador: Microsoft 0,8; LinuxForHealth 0,7 | **sí** en los dos |
| Mecanismos distintos que cuentan | programador: Microsoft 7-13; LinuxForHealth 6-12 | 9 y 8: **dentro** |
| La nueva más probable, según el diseño | `docStatus` desde TXA-17 | **no salió**: ninguno escribe el código de la 0271 ni lo pierde |

**Fuera de previsto:** ninguno en la primera corrida. **Lo que la revisión cambió** es lo que sigue.

**Las cuentas son las de la segunda corrida.** Los dos conversores se volvieron a correr sobre el corpus corregido y con el juez
final (la repetición 1, `md/MD2.md`). Las categorías salieron iguales que en la primera.

## Qué cambió en el juez y en el corpus durante la etapa

**La revisión adversaria,** a ciegas del contraste, tumbó 6 de los 23 hallazgos de la primera corrida y dejó 2 en duda.

**Lo más serio fue del corpus.**
- **El defecto:** v2.5 exige TXA-22 (quién autenticó y cuándo) cuando TXA-17 es AU o LA (§9.6.1.22), y 33 de las 40 bases no lo
  llevaban. Ni el diseño ni el programador lo vieron.
- **El arreglo** (DV-MD-7): se añadió TXA-22, con su prueba en la autoprueba del corpus.
- **Su efecto en B33:** la base era inválida y su rechazo no era incorrecto. Ya corregida, Microsoft la sigue rechazando por
  TXA-8, y eso es MD-M5.

**Los demás arreglos** fueron solo en el código de MDM (DV-MD-8..14), cada uno con su prueba en rojo antes:
- el autenticador tomado de TXA-22 cuando TXA-10 viene vacío;
- el estado del documento que sale de OBX-11 cuando falta TXA-17;
- la orden padre de OBR-29;
- las órdenes idénticas;
- el `contentType` de un adjunto sin datos;
- una cuenta doble en TXA-19;
- OBR-4 en versiones donde es CE.

**El rejuicio de ADT, ORU y VXU** con el juez final da 0 diferencias en 21.892 evidencias. Fue la repetición 1 de las 2 que
permite la regla.

## Lo que el resultado no dice

- **El juez no comprueba las tablas de transiciones de estados del capítulo 9.** Un estado que v2.5 no da para el
  evento no se marca como entrada inválida; se vio en la corrección.
- **El diseño a ciegas no lo hizo el diseñador habitual,** que se quedó sin cupo a mitad del encargo. Lo hizo otro modelo, más
  pequeño, con la misma carpeta cerrada (DV-MD-0).
- **Solo se juzga MDM^T02.** T04, T06, T08 y T10 comparten estructura, pero la guía solo trae el mapa de T02.
- **El contenido del documento no se interpreta:** se juzga cómo se lleva (tipo, codificación, que llegue entero), no lo que dice.
- **Las muestras públicas no están en v2.5,** así que su legalidad de tablas no cuenta. Una de ellas trae un estado fuera de la
  tabla y no cuenta.
- **Lo que la guía calla** (el mapa de TXA-17, el tipo MIME de TX y FT, TXA-19 CA/OB/UN, el paciente del documento) está escrito
  como decisiones de Jev con su alternativa. Ninguna de las 3 nuevas depende solo de una de ellas.

## Desviaciones y documentos de la etapa

`md/decisiones-qmd.md` (DV-MD-0..14), `md/MD-PRE.md`, `md/diseno-md.md`, `md/MD1.md`, `md/MD2.md`, `md/MD3.md`,
`md/CLASES-MD3.json`, `md/prevision-mdm.json`.
