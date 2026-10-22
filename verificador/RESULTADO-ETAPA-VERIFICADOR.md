> *Copia pública: la procedencia y el desglose por origen de la muestra privada del sitio están redactados (punto 4 de la revisión de la publicación). Los totales y el mecanismo son los del original.*

# RESULTADO de la etapa del verificador (14k): cerrar los huecos medidos del juez, 22-oct-2026. Cerrada

**CERRADA.** Las cuatro preguntas que entraban (Q-VE-1) están cerradas con su prueba, y lo que quedaba fuera pasa a límite
declarado. Se hizo en una sesión de las dos de tope.

| | |
|---|---|
| Juez viejo | huella `73d36c38…` (commit de la línea base `22e57eb`) |
| **Juez nuevo** | **huella `b9788fab94b9…`, servidor 1.1**, «etapa del verificador (14k): S104-S107, L-VE-1..8, DV-VE-1..14» |
| Servicio | `verificador-mcp` reiniciado con el juez nuevo |

## La respuesta

**El juez ya no da por bueno lo que no puede ver, y deja de contradecirse con la versión de HL7.**
- **MMI-12 (S104).** Con AA y una fila de éxito, que falte el canónico es `fallo_silencioso` en los tres puntos con mapeador.
  - Antes, «ninguna sesión trae canónico» se trataba como fuera de alcance.
  - El hueco era más ancho que en MI3: también lo tenían el circuito congelado (adt_a01) y ORU, y en un caso de ORU escondía
    un fallo real.
  - **Ahora se cazan las 136 entradas de A1 sin canónico.**
- **MMI-19 (S106).** El problema no estaba en el juez sino en el lector, que releía solo por el canónico.
  - Los dos lectores (IRIS y Mirth) releen ahora por los identificadores del mensaje y por el paciente.
  - El FHIR de IRIS no busca por paciente (`subject:identifier` da 400), así que la relectura usa una ventana de
    `_lastUpdated` desde el reloj del servidor.
  - **Se cazan los 13 casos de A1, y P-VE-10 pasa en vivo en los dos lectores.**
- **Q-MS-9 (S105).** El acuse y los mapeadores leen la misma versión, la escrita.
  - **Con MSH-12 vacío en el perfil del sitio, 38 mensajes de la muestra privada del sitio dejan de condenarse a sí mismos**: lo
    esperado es AE 103, que es lo que ya contestan los circuitos.
- **Q-MI-V-9 (S107).** El contrato del canónico ADT, 77 campos con su valor y su cita, sale ahora del mismo código que lee el
  juez. La guarda impide publicar uno que no sea su generación.

## «Hecho cuando» (ANTES-ETAPA-VERIFICADOR.md)

| Condición | Estado |
|---|---|
| Cada pregunta que entra, cerrada con su prueba o pasada a L-VE | ✅ MMI-12 → S104; MMI-19 → S106; Q-MS-9 → S105; Q-MI-V-9 → S107. C y D → L-VE-1 y L-VE-2 |
| MMI-12 y MMI-19 se cazan; los 15 de MI3 siguen al 100 % con colateral 0 | ✅ 136 y 13 cazados en VE2, reproducidos con evidencia sintética. Los 15 de MI3 no se vuelven a medir en vivo (Q-VE-A-1, L-VE-7). Ninguna regla nueva salta en la regresión ni en la evidencia exacta con canónico |
| Rejuicio de los corpus guardados con 0 fuera de previsto; LABADT y Mirth con la misma categoría | ✅ **0 tras la adjudicación; 3 con la previsión sellada, los tres de la previsión** (`ve/RESULTADO-VE2.md`). LABADT y Mirth comparten juez y contrato de lector, y P-VE-10 pasa en los dos. Mirth no se levantó en vivo (L-VE-7) |
| Suites en verde, salvo las pruebas cambiadas a propósito, declaradas | ✅ Todas en verde. Cambiadas: la autoprueba de almacen_adt sobre S78 (DV-VE-10) y P29 del MCP (la lista de pendientes). Añadidas: el contrato en mapeador_adt (84) y `ve/prueba_ve.py` (21) |
| `preguntas_pendientes` solo con lo que se decidió dejar abierto | ✅ Q-AMB-10, Q-DV1, Q-MI-V-6, Q-MI-V-7 y Q-MS-10 (Q-VE-A-2). Q-MS-9, cerrada |

## Fases

| Fase | Documento | Resultado |
|---|---|---|
| VE-pre | `RESULTADO-VE-PRE.md` | La línea base rehecha. MMI-12 reproducido. 0 evidencias legítimas sin canónico. Q-MS-9 en 39 de 12.419 |
| VE0 | `ve/diseno-verificador-ve-fable.md`, `ve/decisiones-qve.md` | Diseño de Fable a ciegas. Jev decidió 6/6 como Fable y Víctor 5/5 como Fable |
| VE1-a | `ve/SONDAS-VE1A.md` | El FHIR no admite `subject:identifier`, pero sí `_lastUpdated`. Las cotas abiertas cerradas (0 y 39) |
| VE1-b | `ve/PRUEBAS-VE1B.md` | 21 pruebas: 14 en rojo por la razón prevista y 7 controles |
| VE1-c | `ve/CODIGO-VE1C.md` | Cinco commits, uno por mecanismo. 21/21 y regresión CASA |
| VE1-d | `ve/VIVO-VE1D.md` | P-VE-10 en los dos lectores. Piloto A3 10/10. Relectura por paciente en vivo |
| VE2 | `ve/RESULTADO-VE2.md` | Rejuicio de 17.368 casos: 0 fuera de previsto tras la adjudicación |
| VE3 | este documento | MCP 1.1, servicio reiniciado, guarda con el contrato, publicación preparada |

## Lo sellado no se rejuzga: qué cambiaría con el juez nuevo (Q-VE-3)

Cada resultado anterior queda juzgado con `73d36c38…` (o con su propia huella). Con `b9788fab…` cambiaría esto (detalle en
`ve/TABLA-VE2.json`):

| Resultado sellado | Con el juez nuevo |
|---|---|
| A1 (`RESULTADO-A1.md`, `RESULTADO-A1B.md`) | N3 0, N2 0. En N1 solo cambian notas del lector nuevo (210 en lab, 201 en sitio) y 1 MS9 |
| Regresión de 2.721 (fase 13, B0) | Nada: CASA, fichas incluidas |
| Etapa ADT (`RESULTADO-ADT.md`, A4 y A5) y modo sitio (`RESULTADO-MODO-SITIO.md`, MS2) | **Muestra privada del sitio, en su perfil:** con evidencia exacta, 38 de `fallo_silencioso` a `correcto`; los circuitos ya contestaban AE 103. En lab, nada. **Seco:** SIN EXPLICAR 0, con LABMULTI en el sitio en +69 diferencias de CIR-MT4 (MS9 en los puntos de solo acuse, DV-VE-13) |
| Mirth (`RESULTADO-MIRTH.md`) | MMI-12 y MMI-19 pasan de puntos ciegos a cazados. Los 15 cazados, por construcción |
| Piloto del agente y BU (`RESULTADO-AG2-AG3.md`, `RESULTADO-AMP.md`, `RESULTADO-BU.md`) | En la evidencia guardada de los agentes, N3 0 y N2 0, y 1 nota L-VE-3. Su juez sellado era `73d36c38…` |

## Límites nuevos (L-VE) y desviaciones (DV-VE)

- **L-VE-1..8** están en el MCP (`info_verificador.limites`):
  - la neutralidad de motor y la interpretación quedan fuera;
  - la relectura por paciente solo existe en la evidencia nueva y va por `_lastUpdated`;
  - el lector de adt_a01 no tiene canal de fallos;
  - el modificador `:identifier`, medido y no admitido;
  - un AA sin fila de éxito no exige canónico;
  - MI3 no se vuelve a medir en vivo;
  - previos solo del mismo segundo.
- **L-ADT-19:** cerrado para la evidencia con `visitas_por_paciente`.
- **DV-VE-1..14** están en el MCP (`info_verificador.desviaciones_ve`) y en cada documento de fase. La más importante para leer
  VE2 es la DV-VE-14: la primera pasada del rejuicio dio 267 fuera de previsto por la firma por caso, y la corregida, 3.

## Publicación (Q-VE-5)

**Preparada, no publicada:** `ve/PUBLICACION-VE3.md`. Subirla al repo público espera al visto bueno de Víctor al diff,
junto con la de BU, que sigue pendiente.
