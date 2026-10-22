# VE1-d: en vivo, sin tocar los circuitos (22-oct-2026)

**Hecho.** Las tres medidas pasan, con el juez y los lectores nuevos (`ve/ve1d.py`, `labadt/adt.py piloto`).

| Medida | Qué | Resultado |
|---|---|---|
| **P-VE-10** (diseño §2.5), dos lectores | **(a)** censo → se escribe a mano un Encounter SIN identifier, con el paciente por referencia lógica → lectura. **(b)** se escribe → censo → lectura | **PASA en IRIS y en Mirth.** (a): sale nuevo, `n` = 1 y es el escrito; el juez lo caza como `fidelidad/almacen` PV1-2. (b): sale como previo y no hay nuevos; el juez da `correcto` con la nota `almacen_previos`. Borrado por id: 1, y no queda ninguno |
| **Piloto A3** (Q-VE-A-5): 10 sondas por el 2586, LABADT en exclusiva | El mismo piloto de A3, con el lector nuevo | **PASA 10/10**, todas `correcto` y con sus comprobaciones. S7 (A31 con PV1-2 = N) no toca el Encounter V1. S8 (AE 102) ahora se relee por los identificadores del mensaje: 0/0. **USER de vuelta:** EL CONGELADO, `MSA\|AA`. Limpieza por id |
| **Por paciente, en vivo** (`ve1d.py vivo`) | S1 y S7 de A3, mostrando `visitas_por_paciente` | S1: 1 Encounter por paciente, el mismo que por visita (se cuenta una vez), `correcto`. S7: 0, `correcto`. Sin fallos. USER de vuelta con `MSA\|AA` |

- **El `labadt/piloto.json` sellado en A3 (`2bac740`) no se toca.** La salida de esta vuelta está en `ve/piloto_a3_ve1d.json`, y el
  original se restauró: `git status` queda limpio.
- **Lo que vuelve a quedar escrito:** con `_lastUpdated`, el Encounter V1 de S1 no aparece en la ventana de S7, ni como previo,
  porque el circuito no lo tocó (DV-VE-9). Los `previos` solo aparecen cuando algo del paciente se tocó en el mismo segundo antes
  del envío, como en P-VE-10 (b).
- **Las sondas que escriben en FHIR** usan pacientes con valor propio (`VE1D-…`, `VE1DV…`, `A3…`) y se borran por id.

**Siguiente: VE2,** la previsión sellada y el rejuicio contra la línea base.
