# Resultado AG2 y AG3: el piloto del agente que se apoya en el verificador (12-oct-2026)

## Las dos frases (formato fijo de §4.5)

> El agente **funciona**: localiza top-3 en 10/11 casos reales (IC95 0,62-0,98; azar 0,02) y arregla sin colateral 6/11
> (IC95 0,28-0,79). El agente queda **indeterminado** frente a la búsqueda sin modelo: Δ localización +0,36 (IC 0,00-0,73;
> McNemar p = 0,22), Δ arreglo +0,55. La referencia sola localiza 6/11 y arregla 0/11. Coste: 42 040 tokens nuevos por tirada,
> 60 724 por arreglo aceptado.

Cómo leerlas:
- **Localizar.** Con 11 casos reales, una ventaja de 4 casos sobre la referencia no basta para la regla preinscrita, que pide
  Δ ≥ 0,20 **y** p < 0,10. El resultado no es «no aporta»: es «n insuficiente para la diferencia observada». Por regla, eso
  **no** dispara añadir casos en este piloto.
- **Arreglar** es secundario y se lee como descriptivo, sin corregir por multiplicidad. Ahí la diferencia es clara:
  - Δ +0,55, IC 0,27-0,82, McNemar 7 a 0, p = 0,016 → «aporta» con la misma regla.
  - Frente a VACÍO también aporta: FIX(AG) = 0,55 ≥ 0,30.
  - La referencia no produjo ningún parche. Sus tres plantillas mecánicas no casaron en ningún caso.

Corpus, sello y reglas: `etapa/SELLO-AG1.md` y `etapa/SELLO-AG2-ANTES.md` (DV-AG-9..16, L-AG-16). Detalle por caso:
`privado/agente/ag3/analisis.json`, que no se publica.

## Por brazo

| | AG (Opus 5.5, 2 réplicas) | REF (sin modelo) | DS (DeepSeek v4 pro, 1 réplica) |
|---|---|---|---|
| LOC3, H + R (n = 11) | **0,91** (IC 0,62-0,98) | 0,55 (0,28-0,79) | 0,82 (0,52-0,95) |
| — H (n = 5) | 1,00 | 0,20 | 0,80 |
| — R (n = 6) | 0,83 | 0,83 | 0,83 |
| FIX, H + R | **0,55** (0,28-0,79) | 0,00 (0-0,26) | 0,64 (0,35-0,85) |
| FIX parcial medio, H + R | 0,66 | 0 | 0,76 |
| Colateral medio por tirada, H + R | 0,05 (1 tirada con 1) | 0 | 0 |
| LOC3, M (n = 12) | 1,00 | 0,75 | — |
| FIX, M (12; los 8 con regresión) | 1,00; 1,00 | 0; 0 | — |
| Falsas alarmas en limpios | 0 de 6 | 0 de 3 | 0 de 3 |
| Negaciones falsas (dice «no hay fallo») | 2 (las dos en R) | 0 | 1 |
| No aplica / no compila | 0 / 1 | 0 / 0 | 0 / 0 |
| Sin respuesta o cortadas | 0 | 0 | 0 |
| Tiradas inválidas (auditoría) | 0 de 52 | — | 0 de 14 |
| Tokens nuevos por tirada (media / máx.) | 42 040 / 98 712 | 0 (3 sondas) | 89 842 / 136 093 |
| Coste | 2,19 M tokens nuevos (23 USD nominales) | segundos | 1,44 USD |

Reglas de parada de AG2:
- **Primeros 6 M:** 6 de 6 localizados (pedía ≥ 3).
- **Tokens del brazo AG:** 2,19 M (tope 12 M).
- **Inválidas:** 0.
- **DeepSeek:** se quedó en 1,44 USD (tope 1,8) y midió sus 14 casos.

## Sensibilidades preinscritas (LOC3, AG frente a REF)

| | Δ | IC95 | McNemar p | Lectura |
|---|---|---|---|---|
| Primario (R con la verdad ampliada) | +0,36 | 0,00-0,73 | 0,22 | indeterminado |
| (i) R con la verdad sellada | +0,36 | 0,00-0,73 | 0,22 | indeterminado (la ampliación no cambia nada) |
| (ii) solo H (n = 5) | +0,80 | 0,40-1,00 | 0,13 | indeterminado |
| (iii) sin R4 ni R6 (pista textual, DV-AG-15) | +0,44 | 0,00-0,89 | 0,22 | indeterminado |
| (iv) DS frente a REF | +0,27 | −0,09-0,64 | 0,38 | indeterminado |
| (v) «las dos réplicas» | +0,36 | 0,00-0,73 | 0,22 | indeterminado |

Las dos réplicas de AG coinciden caso a caso en localizar: «alguna» y «las dos» dan las dos 10/11. **Toda la ventaja de
localización está en H**: 5/5 frente a 1/5. En R los tres brazos empatan (5/6). La referencia es fuerte donde el hallazgo nombra
el campo y el código; los fallos históricos de ORU no lo hacen.

## Fragilidad (§6.4) y oráculo

- **(a) Consigna B** (otra redacción, misma información) en 3 M: 3/3 localizan, igual que la réplica 1. Estable.
- **(b) MCP con 3 llamadas** en otros 3 M: 3/3 localizan; no depende del oráculo. **Pero el límite no llegó a actuar.** El agente
  apenas usa el verificador:
  - AG: 11 llamadas al MCP en 52 tiradas, y solo 7 tiradas usan alguna;
  - DS: 31 llamadas en 14 tiradas;
  - las 3 tiradas de (b) no hicieron ninguna.

  Lo que se mide aquí es sobre todo **lectura de código guiada por el veredicto**, no un bucle con el juez como oráculo. El juez
  le sirve al agente por lo que dice en `caso.json`, no por lo que contesta.

## Lectura de 3 parches aceptados (AG3, L-AG-3)

Se sortearon 3 de los 12 parches aceptados de AG en H + R (`agente/ag3_lectura.py`). Jev juzgó los 3 como **«arregla la
causa»**, con confianza de 0,97 a 1 (`agente/decision-jev-ag3-lectura.md`). Mi lectura coincide:
- uno desescapa HL7 en el nombre y en el identificador, con la función que ya existía;
- otro conserva la precisión decimal de FHIR;
- otro deja de desglosar un SN de tipo texto.

Ninguno reconoce mensajes de prueba ni toca lo que se registra para contentar al juez. Esta lectura no cambia ninguna puntuación.

## Incidencias durante AG2, declaradas antes de leer el agregado

- **DV-AG-16. La restauración de la caja ADT falló, y era un artefacto.** La firma de un mismo mensaje cambia entre dos medidas
  idénticas del árbol base (4 de 5 fijos). En ADT la restauración pasa a juzgarse por el veredicto. El parche afectado se
  reevaluó con el mismo resultado: FIX 1, 10/10, colateral 0.
- **L-AG-16.** Cuatro M de LABMUT tienen la regresión sellada vacía (el mutante muerde todo). Por eso el FIX de M se da también
  con los 8 casos que sí tienen regresión. Da lo mismo: 1,00.
- **Un parche no compila, y es de verdad.** Es una poscondición `Return:(a) || (b) 1` sin paréntesis externos (error #1054 de
  IRIS). El evaluador lo cuenta como FIX 0. El diagnóstico (`agente/ag2_diag.py compila`) sacó el texto del error, que el
  evaluador sellado no guarda.

## Amenazas a la validez, con lo observado (§6)

- **n = 11.** La conclusión de localización es «indeterminado», no «iguales». El intervalo llega a +0,73.
- **Contaminación (§6.1).** H son arreglos reales de este laboratorio; el modelo pudo ver código parecido, pero no estos
  commits. DS (otro fabricante, sin memoria compartida) localiza H en 4/5 y arregla más que AG (0,64 frente a 0,55, con 1
  réplica). Eso no apoya que AG acierte H por haberlos visto.
- **El juez como oráculo (§6.3).** Apenas se usó (ver arriba), así que «el agente se adapta al juez por prueba y error» queda
  descartado en la práctica. La lectura de 3 parches no encuentra trampas.
- **Evaluador.** Separó sus cuatro controles en las cuatro cajas (AG1). La restauración dio «ok» en las 44 evaluaciones en que
  se midió: 36 por firma (LABMUT, LABORUMUT) y 8 por veredicto (LABADTMUT). Hay dos huecos:
  - en 9 evaluaciones de M sin regresión no había fijos con que medirla (L-AG-16);
  - Mirth no la necesita, porque cada medida arranca y quita su contenedor.
- **Coste.** El brazo AG gasta un 18 % de su tope y DS el 80 % del suyo.
