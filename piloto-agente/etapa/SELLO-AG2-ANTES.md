# Adenda al sello AG1, antes de la primera tirada de AG2 (12-oct-2026)

Se commitea antes de cualquier tirada. No cambia la clave, la referencia, la consigna ni el evaluador sellados en
`SELLO-AG1.md`; corrige una cifra de ese sello, fija el arnés de las tiradas y escribe lo que el diseño pedía y faltaba.

## DV-AG nuevas

- **DV-AG-9. El número de casos es 26, no 31.** `SELLO-AG1.md` §5 dice «los 31 casos», que era la previsión del diseño. Lo sellado
  son 26 casos que cuentan: 5 H, 6 R, 12 M y 3 limpios (R5 no cuenta). Por tanto:
  - el brazo AG hace 2 × 26 = **52 tiradas**;
  - REF hace 26;
  - DS hace 14 (H + R + limpios).
- **DV-AG-10. La segunda redacción de la consigna (§6.4 a) no quedó escrita en AG1; se escribe ahora**, antes de ver ninguna
  tirada: `agente/CONSIGNA_AG1_B.md`.
  - Lleva la misma información y los mismos campos que la sellada, en otro orden y con otras palabras.
  - El subestudio (a) toma 3 M y el (b) otros 3 M, elegidos por `sha256("AG2F|<huella>|<caso>")`.
  - El límite de (b) lo pone un proxy del MCP (`agente/mcp_limitado.py`): a partir de la 4.ª llamada contesta un error. Está
    probado: las llamadas 1-3 pasan y la 4.ª da error.
- **DV-AG-11. Nombre de la carpeta por réplica:** `sha256("AG2|<huella>|<caso>|<réplica>")[:8]`, bajo la carpeta de cajas del agente (fuera del repositorio) en Windows.
  Lo pedía §1.7 punto 2; las plantillas de AG1 usan un opaco por caso.
- **DV-AG-12. Modelo del brazo AG.**
  - El lanzador sellado no pasa `--model`, así que usa el modelo por defecto de `claude -p`. En AG0 era `claude-opus-5-5`, el
    del sello.
  - Cada tirada registra el modelo que declara la sesión. Una tirada con otro modelo es **inválida** y cuenta para la regla
    de parada de las inválidas.
- **DV-AG-13. Presupuesto por tirada:** el lanzador corta por turnos (30) y por reloj (10 min), y mide los tokens nuevos y las
  llamadas al terminar. Una tirada con más de 200 000 tokens nuevos o más de 30 llamadas cuenta como **«sin respuesta»**: es lo
  que dice el sello, una tirada cortada por presupuesto. Se reporta aparte, como sensibilidad, lo que habría puntuado.
- **DV-AG-14. Brazo DS** (`agente/ag2_ds.py`).
  - Modelo `deepseek-v4-pro`, por la API directa, con un adaptador mínimo.
  - Las mismas herramientas que el agente, confinadas a la carpeta: leer, buscar ficheros, buscar texto y escribir solo
    `respuesta.json`. También las cinco del verificador, servidas por el mismo `mcp_verificador.py`.
  - El mismo mensaje inicial que `lanzar_agente.PROMPT` y el mismo presupuesto por tirada.
  - El gasto se mide con el saldo de la API antes y después de cada tirada; tope 1,8 USD (saldo al empezar: 1,96 USD).
  - **Comprobado antes de enviar:** las 14 cajas que verá DS se pasaron por los detectores de `antes_de_publicar.py` (0
    hallazgos) y por los nombres del namespace privado y de los perfiles del sitio. Solo coincide uno, que ya es público.
  - Toda la evidencia mostrada sale de bases sintéticas (A1, O4, Q1 y las basales del generador).

## Orden y reglas, en el arnés

- `agente/ag2.py orden`: orden de las 52 tiradas AG por `sha256("AG2|<huella>|<caso>|<réplica>")`. Hay 5 M entre las 12
  primeras.
- **Reglas de parada (`ag2.py estado`, antes de cada tirada AG):**
  - menos de 3 LOC3 en las 6 primeras tiradas M del orden;
  - 12 M tokens nuevos en el brazo;
  - 3 tiradas inválidas.
- **Evaluación FIX (`ag2.py evaluar`).**
  - El árbol que se parchea es el `fuente/` de la plantilla, comprobado contra la huella de cada fichero en la clave.
  - Los cables de H se comprueban contra su sha256 sellado.
  - La restauración se mira con 5 fijos de la regresión (§1.5).
  - R3 se evalúa con sus dos grupos (R3 y R3b): FIX solo si los dos dan FIX.
- La localización se puntúa contra la verdad **sellada**. La verdad ampliada de R (§4.1) se calcula en AG3.

## Huellas (sha256)

| Fichero | sha256 |
|---|---|
| `agente/ag2.py` | `62dc59208870827d53ab8bf1e3c21541af52532a119f463d628f52591173ebd6` |
| `agente/ag2_tiradas.py` | `f56ef7d77c71c2b27166ac522a125cff35fe608f6ab94cf397efe0ce041fff97` |
| `agente/ag2_ds.py` | `00378444547e9fa3525b3d5cc7dbaaeccfc91abd08aadd0124fac2d72ef25487` |
| `agente/CONSIGNA_AG1_B.md` | `52a6b061fa462fe47172690542b870916a099f11a5046244565e0a513a9f99f7` |
| `agente/mcp_limitado.py` | `ede6d1e9e6b48cb224cb32474d4f8ec015b4f6b9a391b02824b177ccbd1b71da` |
| `agente/mcp_verificador_limitado.json` | `9d9adbc9158516e04d8fce86f149c4993ba1afdb9a8ca2fe579b05e4487543f7` |
| `privado/agente/ag2/orden.json` | `d33f46d4e3baa841e0650bad7c852e210297bc84fe9c580781146edf5a7f4a60` |
| `privado/agente/ag2/frag_a.json` | `0ce734ada507e795ad780719c39ab4503dde6f219f4125a5d7470b5c9c7af778` |
| `privado/agente/ag2/frag_b.json` | `bf16ff9425cee0e76273dfd6e38e15ba21cbcccb4cd05f25319857b794a23be7` |

## DV-AG-15 (añadida tras la 1.ª tirada AG, que era un M, y antes de ver ninguna de R)

La sensibilidad (iii) de §4.5 («quitando los casos de R con pista textual en `verificador.json`», §6.2) exigía una lista hecha en
AG1, y no se hizo. Se fija con la lectura del propio diseño: **R4** (la decisión «V», el límite de 10 repeticiones) y **R6** (S100,
L-MT11). L23 y L-MS-4 describen el congelado sin señalar un caso concreto, y no se usan.

## L-AG-16 (hallado durante AG2, al evaluar los primeros parches; no cambia ninguna puntuación)

Cuatro M de LABMUT (M01, M07, M09 y M10) tienen la regresión sellada **vacía**: su mutante muerde todos los candidatos, igual que
MMI-6 en L-AG-14 pero sin ningún aceptado que quede. En ellos FIX solo exige los disparadores, y el colateral no se mide.
MSM-8 (4) y MMI-1 (2) la tienen corta. M es control y no entra en el primario. AG3 da el FIX de M de dos formas: con los 12 casos
y restringido a los 8 que tienen regresión.

## DV-AG-16 (durante AG2, al fallar la restauracion en la caja ADT)

La restauración de la caja LABADTMUT dio «FALLA» al evaluar el primer parche de ADT. El diagnóstico (`agente/ag2_diag.py
firma`) midió dos veces el árbol base sin parche: 4 de los 5 fijos cambian de firma entre esas dos medidas, con el mismo veredicto
`correcto`. La firma de ADT lleva valores propios de cada pasada, así que no sirve para juzgar la restauración en esa caja; la caja
no estaba mal. En ADT (y solo en ADT) la restauración se juzga por el **veredicto** de los 5 fijos, con dos intentos (`ag2.py
evaluar`). El parche afectado se reevalúa. Su primera evaluación (FIX 1, 10/10, colateral 0) se guarda aparte.
