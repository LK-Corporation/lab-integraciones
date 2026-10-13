# Sello AG1 del piloto del agente (12-oct-2026)

Este sello se commitea **antes de la primera tirada** de cualquier brazo (diseño `agente/diseno-agente-fable.md` §1.7). A partir de
aquí no se añade, quita ni cambia ningún caso, réplica, umbral, consigna, presupuesto ni línea de la referencia. Los cambios
obligados por un fallo de la caja se escriben como DV-AG nuevas, con fecha, antes de reanudar.

La clave (`privado/agente/ag1/ag1_clave.json`) no se publica: lleva los ids de los H, las zonas de R y el mapa opaco → caso.
Aquí va solo su huella.

## 1. Corpus sellado

| Corpus | Cuentan | Casos | Retirados (por las puertas del diseño, antes de ver nada del agente) |
|---|---|---|---|
| H, fallos históricos reales | **5** | H-ORU-1, H-ORU-2, H-ORU-4, H-ORU-5, H-ORU-6 | H-ADT-1 y H-ORU-7 (1 disparador; la puerta pide ≥ 3); H-COM-1 y H-COM-2 (0 disparadores) |
| R, fallos vivos del congelado (LABMUT) | **6** | R1, R2, R3 (con R3b como grupo), R4, R6, R7 | R5 no cuenta: es el caso de AG-pre (el agente ya lo vio) |
| M, mutantes de control | **12** | M01, M03, M04, M07, M09, M10 (LABMUT); MA1, MA10, MA11, MSM-8 (LABADTMUT); MMI-1, MMI-6 (Mirth) | — |
| L, limpios | **3** | uno por motor de IRIS: L-adt, L-oru, L-mut | — |

H + R = **11** (puerta ≥ 10). Las cajas llevan nombre opaco; la evidencia mostrada lleva MSH-10 sustituido por un testigo opaco
de la misma longitud (`gen_cajas.py opacar`).

## 2. Puertas de AG1 (diseño §5)

| Puerta | Umbral | Medido | |
|---|---|---|---|
| H que cuentan | ≥ 5 | 5 | ✓ |
| R que cuentan | ≥ 5 | 6 | ✓ |
| H + R | ≥ 10 | 11 | ✓ |
| M con caso mostrado | = 12 | 12 | ✓ |
| Limpios | = 3 | 3 | ✓ |
| Evaluador: separa sus 4 controles en todas las cajas | todas | 4 de 4 (tabla §3) | ✓ |
| MCP del agente lista `adt_fhir` y `oru_fhir` | sí | sí (enum de `punto_entrada`) | ✓ |
| Referencia: M top-3 | ≥ 9/12 | 9/12 | ✓ |
| Referencia: falsas alarmas en limpios | 0 | 0 | ✓ |
| Referencia: registro de lectura | limpio | 0 lecturas fuera de su carpeta, 0 sondas de más | ✓ |
| Referencia: clave barajada | ≤ azar + 0,10 (= 0,123) | **0,375** (azar 0,023) | ✗ **declarado** (Q-AG-18, L-AG-13) |
| AG-pre repetido con la cadena nueva | R5 5/5 y H-MI-1 11/11, colateral 0 | R5 5/5, colateral 0; H-MI-1 11/11, colateral 0 | ✓ |

**La clave barajada no pasa y se declara, no se corrige.** El diseño permite dos iteraciones; la primera (DV-AG-7: solo líneas con
un término propio del caso) dejó la tasa en 0,375 y bajó M a 8/12, y se deshizo. La causa es del corpus, no una fuga: las verdades
se concentran en pocas unidades «calientes» (el método que envía a FHIR, la transformación, el rechazo, la lectura del nombre) que
casos distintos comparten. Hacerla caer exigía quitar a la referencia lo que la hace fuerte en M, y un adversario más débil puede
dar un «aporta» falso. Jev decidió (Q-AG-18) **congelar y declarar**: la referencia se congela como está, y **0,375 se reporta
como el acierto «sin mirar el caso» de este corpus** junto a los resultados de los dos brazos (L-AG-13). Q-AG-18 queda en la
lista de Víctor (es_del_humano 0,54).

## 3. Controles del evaluador por caja (§4.2)

VACÍO = el árbol tal cual; FIX = el árbol bueno; INOCUO = cambia el texto de un comentario; DAÑINO = la operación devuelve AR 207
donde construía el AA. Pasa si VACÍO e INOCUO arreglan 0, FIX da 100 % sin colateral y DAÑINO deja colateral > 0.

| Caja | Caso | VACÍO | FIX | INOCUO | DAÑINO | |
|---|---|---|---|---|---|---|
| LABORUMUT | H-ORU-4 (10 disparadores, 20 de regresión) | 0/10 | 10/10, colateral 0 | 0/10 | colateral 7 | separa |
| LABMUT | R4 (10, 20) | 0/10 | — (R no tiene diff; el positivo es R5 con el parche de AG-pre: 5/5, colateral 0) | 0/10 | colateral 20 | separa |
| LABADTMUT | MA1 (10, 10) | 0/10 | 10/10, colateral 0 | 0/10 | colateral 5 | separa |
| Mirth (seco) | H-MI-1 (11, 60 sembrados) | 0/11 | 11/11, colateral 0 | 0/11 | colateral 27 | separa |

DAÑINO en Mirth: en `postproc.js`, la rama `http == 'seco' || 2xx` pasa de `codigo = 'AA'` a AR 207.

**Hallazgo al medir (DV-AG-8).** El primer control de Mirth se hizo sobre MMI-6 y DAÑINO dio colateral 0: MMI-6 (Gender crudo)
muerde todos los A01 aceptados, así que su regresión son solo rechazos y un parche que rompa el AA no tiene dónde dejar colateral.
El evaluador no falla (ese parche tampoco arregla los disparadores: FIX = 0), pero el caso no sirve de control negativo. El control
de la caja Mirth se rehízo sobre H-MI-1, cuya regresión lleva aceptados. Se declara como límite: **en los casos cuyo mutante muerde
todos los aceptados, el daño al AA solo se ve en los disparadores** (L-AG-14).

## 4. Lo que se congela (huellas al final)

- **Referencia sin modelo:** `agente/ref.py` (iteración 0) y `agente/unidades.py`; sus controles en
  `privado/agente/ag1/ref_controles.json` (agregados en §2).
- **Agente:** consigna `agente/CONSIGNA_AG1.md` (§2.2), lanzador `agente/lanzar_agente.py`, MCP
  `agente/mcp_verificador_agente.json` (solo el verificador, `--strict-mcp-config`; herramientas: Read, Glob, Grep, Write y
  `verificar_caso`, `ficha_experto`, `acuse_esperado`, `comparar_canonico`, `consultar_tabla`; sin `info_verificador`).
- **Evaluador:** `agente/ag1_eval.py` (IRIS) y `agente/ag1_eval_mirth.py` (Mirth).
- **Cajas:** `agente/gen_cajas.py`.
- **Guion de análisis:** §4 del diseño (`agente/diseno-agente-fable.md`), sin cambios.

## 5. Modelo, réplicas y presupuesto

| Brazo | Qué | Presupuesto |
|---|---|---|
| REF | referencia sin modelo, 1 pasada sobre los 31 casos | — |
| AG | `claude -p`, modelo `claude-opus-5-5`, aislado en una carpeta `ag-caja/<opaco>/` fuera del repositorio; 2 réplicas × 31, orden sembrado con `AG2|<huella de la clave>` | por tirada 200 000 tokens nuevos, 30 llamadas, 10 min; brazo ≤ 12 M tokens |
| DS | DeepSeek, 1 × (H + R + limpios) | ≤ 1,8 USD |

Una tirada cortada por presupuesto no se repite: cuenta «sin respuesta».

## 6. Reglas de parada de AG2 (números)

- El agente, en los **6 primeros M** por orden sembrado, localiza top-3 en **< 3** → se para y se va a AG3 con eso.
- Tiradas inválidas por la auditoría ≥ **3** → se arregla la caja (DV-AG nueva) y se reanuda; si vuelve a pasar, se para.
- Tokens del brazo AG ≥ **12 M** → se para el brazo.
- DeepSeek ≥ **1,8 USD** → se para ese brazo.
- Una restauración falla **dos veces** en la misma caja → se recrea la caja.

## 7. Regla de decisión (diseño §4.5, sin cambios)

Δ = acierto(AG) − acierto(REF) por caso. **Aporta** si Δ ≥ 0,20 y McNemar p < 0,10; **no aporta** si Δ ≤ 0,10; si no,
**indeterminado**. La tasa barajada de la referencia (0,375) se reporta al lado como acierto sin mirar el caso.

## 8. Desviaciones del diseño (DV-AG)

- **DV-AG-1.** Los sistemas de identificación de FHIR no cambian en las cajas (`urn:lab:integraciones:*`): la proyección de
  `adt_fhir`/`oru_fhir` los exige. El almacén se comparte con LABADT/LABORU parados y se limpia por identifier exacto.
- **DV-AG-2.** Dos commits arreglaron varios fallos a la vez (fb18ef8, f7d42d6) y uno de MS1 (22cf35d) mezcla cambios: el caso H
  se aísla por hunks sobre el árbol real de antes; los disparadores del otro fallo salen como «excluidos» (Q-AG-17).
- **DV-AG-3.** Los R de entorno (R1, R3/R3b) se inyectan solo en la copia que se carga, nunca en el árbol que ve el agente; la
  evidencia lleva la frase de entorno del vocabulario (A-18).
- **DV-AG-4.** Restauración: tras cada evaluación se recarga el árbol base completo y se exige la firma de 5 mensajes fijos; no se
  compara el fuente vivo byte a byte (IRIS lo normaliza).
- **DV-AG-5.** El banco ORU incluye los construidos de `laboru/q1.py` (la primera vuelta los olvidó y H-ORU-5 salió sin
  disparadores); todos los H de ORU se remidieron.
- **DV-AG-6.** El literal de la campaña de M07 delataba al mutante: se sustituye por uno neutro, el mismo en el árbol y en la
  evidencia. Un borrado quita la línea entera, sin dejar sangría.
- **DV-AG-7.** Iteración 1 de la referencia (solo líneas con término propio): medida y **deshecha** (no mejora la clave barajada
  y baja M a 8/12).
- **DV-AG-8.** Control de la caja Mirth sobre H-MI-1 en vez de un M (motivo en §3).

## 9. Limitaciones nuevas

- **L-AG-13.** La clave barajada de la referencia (0,375) no cae al umbral uniforme con verdades concentradas; se reporta como
  línea de base «sin mirar el caso».
- **L-AG-14.** En los casos cuyo mutante muerde todos los aceptados (MMI-6), la regresión no contiene aceptados: el daño al AA de
  un parche solo se ve en los disparadores.

## 10. Huellas (sha256)

| Fichero | sha256 |
|---|---|
| `privado/agente/ag1/ag1_clave.json` | `d4848056a16098f49a1d12d4cda08b084c7da5b8f1c14bf68459f7d47a8353e8` |
| `privado/agente/ag1/ref_controles.json` | `15aae7a94091e7b7a428103cfd9403c3dbeaec3fdd401725cb059902d5465e46` |
| `agente/ref.py` | `647853a578944216766353823486c2b9c5a89028bdd4ab04254c51cceb6b1451` |
| `agente/unidades.py` | `1d63e438eac11c9c125efbcce5016cdc5be88509019853e66222860f17723efa` |
| `agente/CONSIGNA_AG1.md` | `fe0fbca26469bb05a957423ea08e41d251c24557749c23b65c7f2605763f6723` |
| `agente/lanzar_agente.py` | `af5ccfa8319563657148b9c4e807d9b3110f23a14f56b705caed36668cc11a93` |
| `agente/mcp_verificador_agente.json` | `ef12da0bb832e9a310c1f913f511d956f21ec29e5087ae6518e4969c617382c8` |
| `agente/ag1_eval.py` | `63da01cd6e4d5a97480d4b32b5394ba738f462210a2a9c951cf23555b0917f6e` |
| `agente/ag1_eval_mirth.py` | `0f4f48a61eb53012bb925376221f122748e48ade2f50fdbea5587009620dab0e` |
| `agente/gen_cajas.py` | `2a05842e66926eeacb9eccadf6de3bb30a3e879df64dda92f383d32e6005a056` |
| `agente/diseno-agente-fable.md` | `48e21ba408bd7e6b1e056423bccc1af0bf5e2c9605638db08ca65271ebc8b67d` |
