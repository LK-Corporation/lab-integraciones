# Resultado de la ampliación del piloto del agente (AMP, 13-oct-2026). Última etapa

## Las dos frases (formato fijo, `agente/amp/diseno-ampliacion-fable.md` §3.5)

> Con la ampliación (n = 11 + 7), el agente **funciona**: localiza top-3 en 17/18 casos reales (IC95 0,74-0,99; azar ≈ 0,02) y
> arregla sin colateral 8,5/18 (IC95 0,27-0,69). Frente a la búsqueda sin modelo **aporta** (combinado de dos etapas: Z = 1,92,
> Δ +0,44, IC 0,17-0,72); piloto Δ +0,36 (5/1, p 0,22); casos nuevos Δ +0,57 (4/0, p₂ 0,06 a una cola); agregado ingenuo p 0,02,
> optimista. Esta es la última etapa. Coste: 57 376 tokens por tirada, 183 603 por arreglo aceptado.

**Cómo leerlo (§3.3 y §5.2, escrito antes de medir):**
- **Aporta por acumulación.** La etapa 2 sola, como réplica con la regla del piloto, no basta: 4/0, p = 0,125 a dos colas, que
  da «indeterminado». Sumada a la etapa 1 con los pesos fijados antes de medir, cruza la regla preinscrita.
- **El «aporta» depende de dos grupos de casos:**
  - **los casos con pista textual del juez.** Sin ellos, sensibilidad (iii-amp), es indeterminado. Es decir, aporta **con las
    pistas que el juez declara**;
  - **las deudas por decisión.** Sin ellas, sensibilidad (ix), también es indeterminado.

  Esos casos (R-ADT-7, R-ADT-8, R-MT1, R-MT4, y R4 y R6 en el piloto) son la mayoría de los R nuevos.
- **La ventaja del agente cambió de sitio.** En el piloto estaba en H (5/5 frente a 1/5) y en R empataban. En la ampliación
  está en R: el agente localiza 6/6 y la referencia 3/6. La referencia no tiene filas para `AckMode`, el juego de caracteres
  por omisión o una guarda de modo (L-AMP-3).

Detalle por caso en `privado/agente/amp3/analisis.json`, que no se publica.

## Las tres columnas (LOC3, AG frente a REF; «alguna réplica» para los pares)

| | Piloto (etapa 1) | Casos nuevos (etapa 2) | Combinado (primario) | Agregado ingenuo (C) |
|---|---|---|---|---|
| n | 11 | 7 | 18 | 18 |
| Discordantes (a favor / en contra) | 5 / 1 | 4 / 0 | — | 9 / 1 |
| p | 0,109 (una cola) | 0,0625 (una cola); 0,125 (dos) | Z = 1,918 (umbral 1,645) | 0,02 (dos colas), optimista |
| Δ | +0,36 | +0,57 (IC 0,14-0,86) | +0,44 (IC 0,17-0,72) | +0,44 |
| Decisión | indeterminado | indeterminado (como réplica, A) | **aporta** | aporta, optimista |

**FIX** (secundario, descriptivo):
- **Combinado:** Z = 2,61, Δ +0,47 (IC 0,28-0,69), «aporta».
- **Etapa 2 sola:** 3/0, p = 0,25, «indeterminado».
- **REF** no arregló ninguno de los 18.

## Por brazo, en la etapa 2

| | AG (Opus 5.5, 2 réplicas, 16 tiradas) | REF | DS (DeepSeek v4 pro) |
|---|---|---|---|
| LOC3 en los 7 nuevos | **7/7** (H 1/1, R 6/6) | 3/7 (H 0/1, R 3/6) | 2 medidos, los dos cortados por presupuesto de llamadas: 0 |
| FIX en los 7 nuevos (media de réplicas) | 2,5/7 (5 tiradas aceptadas de 14) | 0 | — |
| Colateral | 2 en una tirada (las demás, 0) | — | — |
| Limpio L-multi | 0 falsas alarmas (2 tiradas) | 0 | no medido |
| Negaciones falsas | 0 | 0 | — |
| Tokens nuevos | 918 018 en total (57 376 por tirada) | 3 sondas por caso | — |
| Coste | ≈ 10 USD nominales | segundos | 0,39 USD |

**Por caja (sensibilidad x):**

| Caja | Casos | LOC3 AG | LOC3 REF | FIX AG |
|---|---|---|---|---|
| LABADTMUT | 2 | 1,0 | 0 | 0,25 |
| LABORUMUT | 3 | 1,0 | 0,67 | 0,33 |
| LABMULTIMUT | 2 | 1,0 | 0,5 | 0,5 |

En LABMULTIMUT el FIX se decide solo por el acuse (L-AMP-4).

**Brazo DS: casi no medido.**
- La 1.ª tirada falló por un corte de red (`IncompleteRead`). Desde entonces el adaptador reintenta 3 veces (DV-AMP-7).
- Las 2 siguientes se cortaron por las 30 llamadas.
- Después se agotó el **saldo** de la cuenta: 0,08 USD restantes, con 0,39 de 0,45 gastados. Las otras 6 dan error HTTP y
  quedan **no medidas**.

Recargar el saldo es una decisión de Víctor, y no se hace dentro del estudio. La sensibilidad (iv) DS frente a REF
(«no aporta», con n₂ = 2) no dice nada útil.

## Sensibilidades (LOC3, combinado de dos etapas)

| | n (etapa 1 + 2) | Discordantes etapa 2 | Z | Δ | Lectura |
|---|---|---|---|---|---|
| Primario | 11 + 7 | 4 / 0 | 1,92 | +0,44 | aporta |
| (i) R con la verdad sellada | 11 + 7 | 4 / 0 | 1,92 | +0,44 | aporta |
| (ii) solo H | 5 + 1 | 1 / 0 | 1,40 | +0,83 | indeterminado |
| **(iii-amp) sin pista textual en el juez** | 9 + 3 | 1 / 0 | 1,07 | +0,42 | **indeterminado** |
| (v) «las dos réplicas» | 11 + 7 | 4 / 0 | 1,92 | +0,44 | aporta |
| (vi) = (A), solo nuevos | 7 | 4 / 0 | — | +0,57 | indeterminado |
| (vii) = (C), agregado ingenuo | 18 | 9 / 1 | — | +0,44 | aporta (optimista) |
| (viii) sin comentario de código que nombre la deuda | 11 + 5 | 3 / 0 | 1,66 | +0,44 | aporta |
| **(ix) sin deudas por decisión** | 11 + 3 | 1 / 0 | 1,09 | +0,36 | **indeterminado** |

## Lectura de 2 parches aceptados nuevos (§6, AMP3)

Se sortearon 2 de los 5 parches aceptados de AG en la etapa 2. Jev juzgó los dos como **«arregla la causa»**, con confianza 0,97
y 1 (`agente/amp/decision-jev-amp3-lectura.md`):
- **R-MT1:** quita la guarda del modo sitio, igual que el parche del implementador.
- **R-MS-4:** el AE 101 solo salta si OBR-4 viene vacío del todo.

Ninguno se adapta al juez. La lectura no cambia ninguna puntuación.

## Incidencias, declaradas

- **DV-AMP-6 (Q-AMP-11, Jev 0,88).** Una respuesta de AG traía un tabulador literal dentro de una cadena. Se decidió leer con un
  lector tolerante para todas las tiradas, antes de mirar qué localizaba esa respuesta. Con el lector estricto, esa tirada
  contaría como «sin respuesta». En el piloto no hubo ninguna respuesta así.
- **DV-AMP-7.** Reintentos de red en el adaptador de DS.
- **DV-AMP-1..5.** En el sello: los C0 en R-MT4, H-CAB-2 y H-COM-MT2 sin construir, la caja «multi» en `ag1_cajas.py`, y las
  categorías medidas en R-ADT-8.

**Restauración:**
- dio «ok» en las 11 evaluaciones con parche: 10 por firma (LABORUMUT, LABMULTIMUT) y 1 por veredicto (LABADTMUT). Las
  tiradas sin parche no cargan nada;
- el juez no cambió desde el sello del piloto.

## Amenazas, con lo observado (§5)

1. **Parada opcional.** Está corregida en el cálculo (combinado con pesos fijos), pero la decisión de ampliar se tomó a la vista
   de un p prometedor (L-AMP-6). La réplica sola no llega.
2. **Pistas.** El «aporta» no sobrevive sin los casos con pista en el juez (iii-amp). Ese es el resultado más importante de la
   ampliación.
3. **Deudas por decisión.** Tampoco sobrevive sin ellas (ix). Aun así, el agente no negó ninguna: localizó las 4 y aceptó el
   veredicto del juez.
4. **REF no calibrada para ajustes** (L-AMP-3). La ventaja de la etapa 2 está en R de configuración y de ausencia, donde la
   referencia es débil por construcción.
5. **n pequeño.** Con 7 casos nuevos, cada uno vale 0,14 de Δ₂.

**Esta es la última etapa (S-AMP-9).** Ningún resultado abre otra ampliación.
