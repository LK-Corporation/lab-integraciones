# Etapa 26: las decisiones de Jev y las desviaciones del programador

El diseño es `md/diseno-md.md`, hecho a ciegas. Las doce preguntas de su §9 se pasaron a Jev con un estado neutro
(`md/estado_qmd.md`, `md/preguntas_qmd.json`); la respuesta está en `md/decision-jev-qmd.md`.

## Las decisiones (Q-MD-D)

| Pregunta | Jev | Confianza | Recomendación del diseñador | En `ALTERNATIVA_MD` (confianza ≤ 0,52) |
|---|---|---|---|---|
| Q-MD-D-1, eventos | **(a) solo T02** | 0,32 | (b) | sí: (b), T02 y T04/T06/T08/T10 |
| Q-MD-D-2, Provenance y MessageHeader | **(a) nota** | 0,55 | (a) | no |
| Q-MD-D-3, tipo MIME | **(b) literal o registrado equivalente** | 0,19 | (b) | sí: (a), solo los literales |
| Q-MD-D-4, `docStatus` | **(b) literal o mapa, y el literal cuenta además como `fhir_invalido`** | 0,44 | (c) | sí: (c), sin penalizar el literal |
| Q-MD-D-5, varios OBX | **(a) cualquier reparto** si llega entero y en orden | 0,76 | (a) | no |
| Q-MD-D-6, `subject` y `context.encounter` ausentes | **(a) nota** | 0,18 | (a) | sí: (b), `dato_perdido` |
| Q-MD-D-7, varias órdenes | **(b) una referencia por orden** | 0,78 | (b) | no |
| Q-MD-D-8, `Observation` en el Bundle | **(a) nota** | 0,22 | (a) | sí: (b), `recurso_inventado` |
| Q-MD-D-9, TXA-19 = CA/OB/UN | **(b) extensión y además `status` coherente** | 0,46 | (a) | sí: (a), solo la extensión |
| Q-MD-D-10, ServiceRequest | **(a) básico** (R-MD-37..41) | 0,53 | (a) | no |
| Q-MD-D-11, TXA-10 repetido | **(b) cualquiera** | 0,10 | (b) | sí: (a), la primera |
| Q-MD-D-12, OBX sin fila | **(a) nota** | 0,22 | (a) | sí: (b), `dato_perdido` |

La alternativa de cada pregunta en `ALTERNATIVA_MD` es la segunda opción de Jev. MD2 da la N con la decisión y, aparte, con
cada alternativa, como se hizo en VXU.

## Las desviaciones (DV-MD-n)

- **DV-MD-0, el diseñador.** Fable se quedó sin cupo a mitad del encargo, sin escribir nada (31-oct, 05:00). Jev eligió que
  diseñara un modelo más pequeño y distinto, con la misma caja cerrada (0,61; esperar a Fable, 0,26; `md/decision-jev-md0-modelo.md`).
  El diseño lo hizo Sonnet, a ciegas, leyendo solo `/tmp/md0`.
- **DV-MD-1, el ServiceRequest y sus números (MD1-a).** En la clave `identifier` del §2.2 gana el ServiceRequest que comparte
  más números del grupo (PLAC y FILL, de ORC o de OBR); un empate se desempata por OBR-4, y solo si sigue el empate es ambiguo.
  Por qué: con la regla literal («`identifier.value` = OBR-3.1/ORC-3.1 u OBR-2.1/ORC-2.1»), la muestra `ms-MDM-T02-02` (dos grupos
  con distinto placer y el mismo filler `1-1`) salía `indeterminado/emparejamiento` en los dos conversores, aunque sus dos
  ServiceRequest se distinguen por el placer y por OBR-4. La salida es la cita (`privado/mdm/md1a/FORMA-MD1A.json`). Los tres
  grupos idénticos de `lfh-Hl7MDMMessageTest__L370` y `__L407` siguen saliendo indeterminados: es L-MD-10, como L-VX-14.
- **DV-MD-2, `mdm_conv` sin `conversion` (P-MD-24).** No es un error de esquema sino `indeterminado/sin_salida`, como hoy
  `adt_conv`, `oru_conv` y `vxu_conv`. Por qué: el esquema del MCP no exige `conversion` según el punto; hacerlo solo para
  `mdm_conv` sería incoherente, y para todos cambiaría ADT, ORU y VXU (condición 1).
- **DV-MD-3, las citas no se registran en `conversion.C`.** A diferencia de VXU (DV-VX-2), `conversion_mdm` no añade claves a
  `conversion.C`: cada hallazgo lleva sus citas y las de las funciones reutilizadas de `conversion.py` se corrigen al vuelo
  (`_reusa`). ORC-1, ORC-2, ORC-3, OBR-4, PID y PV1 van en `C_SEG`, porque ya son claves de ADT, ORU o VXU. Por qué: P-MD-25 (d)
  exige `conversion.C` igual antes y después, y el §4.6 del diseño pedía a la vez registrar las claves nuevas.
- **DV-MD-4, el corpus de MDM espera a MD2-a.** `CORPUS`, `generar_corpus` y `bases_mdm.py` no cambian en MD1: añadir la carpeta
  `mdm` sin `bases_mdm.py` rompería la herramienta. Quedan en rojo, declaradas, P-MD-24 (solo su parte del corpus) y P-MD-26.
  `punto()`, `L-VC-2` y el juguete sí entran en MD1.
- **DV-MD-5, `prueba_multitipo.py`.** Fija la lista de puntos de entrada de `info_verificador`, que gana `mdm_conv`; se añade a la
  lista (como DV-CV-6 y DV-VX-4). El diseño la daba entre los controles que no cambian (§8); es el único cambio, y la prueba
  sigue en verde con sus 705 comprobaciones.
- **DV-MD-6, TXA-7 y TXA-11 en las bases (MD2-a).** Las bases con TXA-17 distinto de DI llevan TXA-7 (fecha de transcripción) y
  TXA-11 (transcriptor), aunque el §5.2 solo los nombra en B33 y B35. Por qué, del estándar: TXA-7 es condicional y se exige «upon
  the presence of a value in TXA-17 of anything except "dictated"» ([E9 CH09.txt:1030-1035]), y TXA-11 «is required on all
  transcribed documents» (§9.6.1.11). El §5.1.4 pide todas las bases válidas; sin esos campos, un conversor que rechazara la base
  tendría razón y el juez lo contaría como rechazo incorrecto. B40 («solo TXA-1, 2, 3, 12 y 17») lleva TXA-17 DI, la única forma de
  ser válida con ese literal; B08 (DI) tampoco los lleva. La autoprueba de `bases_mdm.py` comprueba las cuatro condiciones de TXA
  (TXA-3 con OBX, TXA-7, TXA-11 y TXA-5 con TXA-4).

### MD3-r1: la repetición 1 de MD2-c (revisión adversaria de MD3)

Los arreglos que pide la revisión adversaria (`md/revision-adversaria-md3.json`). El corpus se toca por una razón del estándar; el
juez, solo en `conversion_mdm.py` (`conversion.py` no cambia y el rejuicio de ADT, ORU y VXU da 0 diferencias). Cada arreglo tiene su
prueba, en rojo antes (`b2a8f15`).

- **DV-MD-7, TXA-22 en las bases AU y LA (H17).**
  - Qué: las 33 bases con TXA-17 AU (31) o LA (2) que no lo llevaban ganan TXA-22: la persona de la primera repetición de TXA-10 y
    PPN.15, la fecha de la autenticación (`10:nn:30+0100`, entre TXA-7 y MSH-7).
  - Por qué, del estándar: «When the status of TXA-17 … is equal to AU … or LA …, all components are required»
    ([E9 CH09.txt:1798-1800]). Además, persona y fecha van juntas (:1795-1797). Sin ellos esas bases eran inválidas, y el rechazo de
    B33 por Microsoft no era incorrecto.
  - Lo que no cambia: B37 conserva su TXA-22, distinto de TXA-10 a propósito. Todas las bases AU/LA tienen TXA-10, así que no hubo que
    elegir a nadie. Las secundarias S01, S02 y S03 lo heredan.
  - La autoprueba lo comprueba: con AU o LA, TXA-22 con persona y fecha; y, si hay TXA-22, las dos.
- **DV-MD-8 (H8).** Con TXA-10 vacío, un `authenticator` que es la persona de TXA-22 es nota, no `dato_inventado`. Coincide si
  PPN.1 está en un `identifier` del Practitioner, si PPN.2 es su `family`, o si un `display` lleva el apellido o el identificador.
  - Por qué: v2.5 define TXA-22 como quien autenticó, y R4 define `authenticator` como quien autentica; la guía no da destino a TXA-22
    ni lo prohíbe.
  - Con TXA-10 valorado no cambia nada: B37 (H5) sigue contando.
- **DV-MD-9 (H10).** Con TXA-17 vacío, un `docStatus` igual al que da el ConceptMap de la guía para OBX-11 (0085) u OBR-25 (0123) es
  nota. Si no, sigue siendo `dato_inventado`.
  - Es el mapa de la guía (F → final, P → preliminary). La revisión proponía también C → amended, pero el ConceptMap da C → corrected,
    que no está en `composition-status`: no entra.
- **DV-MD-10 (H13).** R-MD-14 (`contentType` con TXA-3) cuenta solo si algún attachment lleva `data` o `url`. Sin ellos, R4 no exige
  `contentType` y la pérdida del contenido ya cuenta.
- **DV-MD-11 (H20).** Con TXA-19 CA u OB, un `status` incoherente da una sola cuenta: `valor_distinto`, con la pérdida del código en
  el `que`. Antes daba `dato_perdido+valor_distinto`. Con la alternativa de Q-MD-D-9 sigue siendo `dato_perdido`.
- **DV-MD-12 (H21).** Un ServiceRequest sobrante es el pedido padre, y queda como nota `pedido_padre`, no `recurso_inventado`, si
  cumple dos cosas: lleva en un `identifier` el número de OBR-29 o de ORC-8 (EIP.1 o EIP.2), y lo referencia `basedOn` desde un
  ServiceRequest emparejado. La guía lleva OBR-29 a `basedOn` ([G OBR_ServiceRequest.csv:43-46]).
- **DV-MD-13 (H22).** Dos grupos de orden son la misma orden si comparten el número de orden (ORC-2.1 u OBR-2.1, valorado) y además
  ORC-3, OBR-2, OBR-3 y OBR-4. Motivo: el número de placer «identifies an order uniquely» ([E4 CH04.txt:2353-2365]).
  - Se espera un ServiceRequest por orden distinta. Los grupos repetidos dan nota `orden_repetida`.
  - Los ServiceRequest iguales, hasta tantos como grupos, son nota: la guía crea uno por ORC. Los de más son `recurso_duplicado`.
  - Efecto en L-MD-10: esos grupos ya no dan `indeterminado/emparejamiento`. L-MD-10 queda para los grupos sin números que los
    separen y para las DocumentReference sin claves comunes.
  - El recuento gana `ordenes_distintas`.
- **DV-MD-14 (H7).** OBR-4 es CE en las versiones hasta 2.5 ([E4 CH04.txt:3448-3451], seis componentes); un componente de más se
  ignora ([E2 CH02.txt:932-935]), así que CWE.9 → `text` no se espera. Se hace en el camino de MDM: el campo se corta a seis
  componentes antes de llamar a `CV._codigo`, que no cambia para las demás familias. Desde 2.6 (CWE), sigue como antes; que OBR-4
  es CWE desde 2.6 es la lectura de la propia hoja de la guía, que sigue una versión posterior. MSH-12 vacío se juzga como 2.5.
- **H15 no cambia** (TXA-6 en `attachment.creation`): la guía lleva TXA-6 a `date`. Queda como dudoso.
