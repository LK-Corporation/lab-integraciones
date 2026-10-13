# RESULTADO AG0: diseño del piloto del agente y decisiones, 12-oct-2026

- **Diseño:** `agente/diseno-agente-fable.md`, de Fable, a ciegas de los arreglos de H, con el encargo en
  `agente/ENCARGO-AG0.md`. Tiene 608 líneas, S-AG-1..10, Q-AG-8..17 y L-AG-1..12.
- **La carpeta de Fable:**
  - el ANTES, con la lista de H sin commits ni descripción de los arreglos;
  - RESULTADO-AGPRE y las lecciones;
  - la fuente actual de los circuitos, los arneses y el corpus R.

  Se comprobó que no llevaba el nombre del namespace privado ni ningún commit de H.

## Regla de parada (del diseño, §4.5 y §5)

- **AG1 pasa** con:
  - ≥ 5 H, ≥ 5 R, y H + R ≥ 10;
  - 12 M con su caso y 3 casos limpios;
  - el evaluador separando sus 4 controles en todas las cajas;
  - la referencia congelada con sus 3 controles;
  - AG-pre repetido con la cadena nueva, dando los mismos números.
- **AG2 para** si:
  - el agente localiza menos de 3 de los 6 primeros mutantes;
  - hay ≥ 3 tiradas inválidas;
  - se llega a 12 M de tokens o a 1,8 USD de DeepSeek.
- **La decisión:**
  - «aporta» si Δ ≥ 0,20 y McNemar da p < 0,10;
  - «no aporta» si Δ ≤ 0,10;
  - en medio, «indeterminado», sin añadir casos.

## Q-AG-8..17: Jev y lo que queda

`agente/estado_qag.md`, `preguntas_qag.json`, `decision-jev-qag.md`. Segunda vuelta de Q-AG-16: `estado_qag16.md`,
`decision-jev-qag16.md`.

| Q | Jev | Confianza | Queda | Por qué |
|---|---|---|---|---|
| Q-AG-8 cajas de LABADT/LABORU | en el namespace del circuito | 0,68 | **namespaces caja aparte (LABADTMUT, LABORUMUT)**, contra Jev | El «hecho cuando» del ANTES, fijado por Víctor, dice que nada del agente toca los circuitos del laboratorio |
| Q-AG-9 el juez como oráculo de la referencia | tres sondas fijas | 0,32 | tres sondas fijas | |
| Q-AG-10 ¿cuenta R5 (AG-pre)? | no cuenta | 0,02 | no cuenta | Moneda al aire; coincide con el diseño |
| Q-AG-11 granularidad | unidad, top-3 | 0,08 | unidad, top-3 | Moneda al aire; coincide con el diseño |
| Q-AG-12 réplicas | 2, y una 3.ª condicional | 0,88 | 2, y una 3.ª condicional | |
| Q-AG-13 brazos | Claude y DeepSeek | 0,56 | Claude y DeepSeek | |
| Q-AG-14 memoria del subagente | desde la sesión (hereda la memoria) | 0,98 | **aislado**, contra Jev | Q-AG-5 de Víctor: el agente no ve los arreglos. La memoria del laboratorio describe al menos el de un caso H |
| Q-AG-15 umbral | Δ y McNemar | 0,66 | Δ ≥ 0,20 y McNemar p < 0,10 | |
| Q-AG-16 afinar la referencia | 1.ª vuelta: también con H (0,54); **2.ª vuelta, con el dato que faltaba**: solo M y R público (0,54) | 0,08 | solo M y R público | Indeciso las dos veces. Al estado le faltaba que quien afina conoce los arreglos y que H no tiene casos de reserva |
| Q-AG-17 H con otros fallos vivos | excluir esos mensajes de la regresión | 0,30 | excluir esos mensajes | |
| ¿Lo decide una persona? | 0,63 | | **Para Víctor:** Q-AG-8 y Q-AG-14 (contra Jev, por el alcance que fijó él) y las monedas al aire (10, 11, 16) | |

## Eslabón de Q-AG-14, medido: el agente aislado

`claude -p` (Claude Code 2.1.286), lanzado desde una carpeta fuera del laboratorio, con `--mcp-config` (solo el verificador),
`--strict-mcp-config` y las herramientas acotadas (`--allowedTools`; Bash y web, prohibidos):
- **No tiene memoria del laboratorio:** dice que no tiene notas sobre LABADT, ImportFromString ni el congelado. Solo ve las
  instrucciones del MCP del verificador.
- Sus MCP son solo las seis herramientas del verificador.
- `info_verificador` desborda (~69.000 caracteres) y la salida va a un fichero. Confirma el punto 2 de AG-pre y S-AG-3: esa
  herramienta se quita y se da en la caja una copia recortada.

Es viable. Los agentes de AG2 se lanzan así, no con la herramienta Agent de la sesión del laboratorio.

## Siguiente

**AG1:**
- cajas LABADTMUT y LABORUMUT;
- el exportador desde git;
- H con sus tres puertas, R con sus disparadores, M y los casos limpios;
- el evaluador con 4 controles por caja;
- la referencia y sus 3 controles;
- `SELLO-AG1.md`.
