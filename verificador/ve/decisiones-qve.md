# Decisiones Q-VE de VE0 (22-oct-2026)

El diseño es `ve/diseno-verificador-ve-fable.md`: Fable, a ciegas de los corpus de rejuicio, sobre la caja de
`ve/caja_ve0.py` (encargo `ve/ENCARGO-VE0.md`).

## De diseño: Jev (`ve/decision-jev-qve.md`)

Se le pasó un estado neutro, sin la recomendación de Fable (`ve/estado_qve.md`, `ve/preguntas_qve.json`).

| Q | Decisión de Jev | Confianza | ¿Como recomendó Fable? |
|---|---|---|---|
| Q-VE-D-1 | El canónico se exige con **AA y fila de éxito** | 0,78 | Sí |
| Q-VE-D-2 | Su ausencia es **`fallo_silencioso`** (`fidelidad/sin_canonico`); el fallo del lector va por su canal a `indeterminado` | 0,94 | Sí |
| Q-VE-D-3 | S22 sigue a la versión **escrita** (S103 aplicada al acuse) | 1 | Sí |
| Q-VE-D-4 | Un Encounter encontrado por el paciente sin PV1-19 **se compara** (cierra L-ADT-19 para la evidencia nueva) | 0,82 | Sí |
| Q-VE-D-5 | El canónico ADT queda **mapeado a FHIR** y se documenta | 0,98 | Sí |
| Q-VE-D-6 | Los Encounter **previos** al envío se **ignoran con nota** (L-ADT-12) | 0,88 | Sí |

**Limitación:** Jev juzga el estado que se le escribe. El estado lo redactó quien implementa, con las consecuencias de cada
opción tal como las describe el diseño. Las S-VE-1..4 se numeran como S-n al declararlas en el MCP, en VE1.

## De alcance: Víctor (Q-VE-A-1..5), el 22-oct

Víctor aceptó las cinco recomendaciones de Fable:

| Q | Decisión |
|---|---|
| Q-VE-A-1 | **No se levanta Mirth** para volver a medir en vivo. MMI-12, MMI-19 y los 15 mutantes se reproducen con evidencia sintética (L-VE-7) |
| Q-VE-A-2 | **Las cinco preguntas de D siguen pendientes,** bajo L-VE-2 |
| Q-VE-A-3 | **La versión se nombra `servidor 1.1` + `revision`,** además de la huella |
| Q-VE-A-4 | **El contrato público del canónico se genera desde el código,** con guarda |
| Q-VE-A-5 | **Se repite el piloto A3** (10 sondas) con LABADT y el lector nuevo, sin tocar el circuito |
