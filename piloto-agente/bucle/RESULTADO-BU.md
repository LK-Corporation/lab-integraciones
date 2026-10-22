# Resultado del estudio «agente con bucle de prueba» (BU, 13-14 y 22-oct-2026). Cerrado

## La frase (formato fijo, `agente/bucle/diseno-bucle-fable.md` §4.4)

> Con el bucle de prueba, el agente arregla sin colateral **14,5/18** casos reales (IC95 0,58-0,93) frente a **8,5/18** del
> agente de hoy remedido (8,5/18 en el piloto y la ampliación): **aporta** (Δ +0,33, IC 0,14-0,53; 6 casos a favor y 0 en
> contra, p = 0,016 a una cola). El agente probó en 34/36 tiradas (1,53 pruebas de media), con sobreajuste en 2 tiradas y
> 1 parche con literal de prueba; de 7 parches aceptados leídos, 7 arreglan la causa. Coste: 53 045 tokens por tirada,
> 65 849 por arreglo aceptado, 109 s de caja por tirada. Este estudio se cierra con este resultado.

La regla (§4.3, sellada en `etapa/SELLO-BU.md` antes de la primera tirada) pedía p ≤ 0,05 y Δ ≥ 0,20. El análisis es
`agente/bu3.py` sin cambios (huella igual a la del sello), sobre `privado/agente/bu3/analisis.json`, que no se publica.

**Cómo leerlo:**
- **Supera la previsión.** El diseño preveía «indeterminado» y un techo realista de unos 6 casos. El bucle convierte
  exactamente 6: H-CAB-1, H-ORU-6, R-ADT-8, R-MS-3, R6 y R7. Ninguno va al revés. R-ADT-8 estaba en la previsión sellada como
  «localiza, no arregla», y BU lo arregla en las dos réplicas.
- **El agente de hoy no ha cambiado.** Remedido (AG₁) da 8,5/18, lo mismo que en el piloto y la ampliación (AG₀): AG₁ frente
  a AG₀ da Δ 0 (1/2). La ganancia es del bucle, no de una deriva del modelo.
- **No contenta a lo que ve.** Hay sobreajuste en 2 tiradas (el umbral era 3), y FIX_visible − FIX en BU es 0,06 (el umbral
  era 0,15). Las 2 son las dos réplicas de H-ORU-5: arreglan 13 y 15 de 25 disparadores con un arreglo genérico de SN que no
  cubre los demás. Jev las lee como arreglo de la causa, a medias.
- **No daña.** Colateral medio por tirada: 0 en BU y 0,056 en AG₁. Ningún parche dejó de compilar y no se cortó ninguna
  tirada en ninguno de los dos brazos.
- **A diferencia de la ampliación, no depende de las deudas por decisión:** sin ellas, sigue «aporta» (sensibilidad iv).

## Sensibilidades preinscritas (FIX, BU frente a AG₁)

| | n | Δ | a favor / en contra | p (una cola) | Decisión |
|---|---|---|---|---|---|
| (i) «las dos réplicas» | 18 | +0,33 | 6 / 0 | 0,016 | aporta |
| (ii) sin tiradas cortadas (no hubo) | 18 | +0,33 | 6 / 0 | 0,016 | aporta |
| (iii) solo multigrupo | 11 | +0,36 | 4 / 0 | 0,063 | indeterminado |
| (iii) solo monogrupo | 7 | +0,29 | 2 / 0 | 0,25 | indeterminado |
| (iv) sin las deudas por decisión | 14 | +0,32 | 5 / 0 | 0,031 | aporta |
| (v) caja ORU | 8 | +0,31 | 3 / 0 | 0,125 | indeterminado |
| (v) caja MUT | 6 | +0,33 | 2 / 0 | 0,25 | indeterminado |
| (v) caja ADT | 2 | +0,75 | 1 / 0 | 0,5 | indeterminado |
| (v) caja MULTI | 2 | 0 | 0 / 0 | — | no aporta |
| (vi) BU frente a AG₀ | 18 | +0,33 | 5 / 0 | 0,031 | aporta |
| (vi) AG₁ frente a AG₀ | 18 | 0 | 1 / 2 | 0,875 | no aporta |
| (vii) solo las BU que probaron (descriptiva) | 17 | +0,35 | 6 / 0 | 0,016 | aporta |

La ganancia aparece tanto en los casos multigrupo como en los monogrupo, y ninguno de los dos grupos basta por sí solo. No se
concentra solo donde «ver variantes» importa (amenaza 2).

## Por caso (FIX, media de las 2 réplicas)

| Caso | Caja | (iii) | AG₁ | BU | Pruebas BU (réplica 1, 2) |
|---|---|---|---|---|---|
| H-CAB-1 | oru | multi | 0 | 0,5 | 2, 2 |
| H-ORU-1 | oru | mono | 1 | 1 | 1, 1 |
| H-ORU-2 | oru | mono | 1 | 1 | 1, 2 |
| H-ORU-4 | oru | mono | 1 | 1 | 1, 1 |
| H-ORU-5 | oru | mono | 0 | 0 | 2, 3 |
| H-ORU-6 | oru | mono | 0 | **1** | 2, 2 |
| R-ADT-7 | adt | multi | 0,5 | 1 | 1, 1 |
| R-ADT-8 | adt | multi | 0 | **1** | 1, 1 |
| R-MS-3 | oru | multi | 0 | **1** | 3, 3 |
| R-MS-4 | oru | multi | 1 | 1 | 1, 1 |
| R-MT1 | multi | multi | 1 | 1 | 1, 1 |
| R-MT4 | multi | multi | 0 | 0 | 2, 4 |
| R1 | mut | mono | 0 | 0 | 0, 0 |
| R2 | mut | multi | 1 | 1 | 1, 1 |
| R3 | mut | multi | 1 | 1 | 1, 1 |
| R4 | mut | multi | 1 | 1 | 1, 1 |
| R6 | mut | mono | 0 | **1** | 2, 2 |
| R7 | mut | multi | 0 | **1** | 2, 3 |
| **Total** | | | **8,5** | **14,5** | 1,53 de media |

- **Donde el agente de hoy ya arreglaba, BU casi siempre prueba una vez y entrega.** Donde gana, suele probar 2 o 3 veces.
- **Lo que el bucle no arregla:** H-ORU-5, R-MT4 y R1, que quedan en 0 en los dos brazos. R-MT4 y R1 estaban previstos como
  casi seguro inalcanzables. En R1, las dos tiradas BU no llegaron a probar: son las 2 de 36 sin prueba.

## Por brazo

| | AG₁ (el agente de hoy, remedido) | BU (con `probar_parche`) |
|---|---|---|
| FIX | 8,5/18 (IC95 0,27-0,69) | **14,5/18** (IC95 0,58-0,93) |
| FIX_visible medio | 0,47 | 0,86 |
| FIX_parcial_oculto medio | 0,58 | 0,87 |
| Colateral medio por tirada | 0,056 | 0 |
| Sobreajuste (tiradas) | 0 | 2 |
| No compila, cortadas, sin respuesta | 0, 0, 0 | 0, 0, 0 |
| LOC3 | 0,92 | 0,94 |
| Falsas alarmas en los limpios / negaciones falsas | 0 / 2 | 0 / 2 |
| Tokens nuevos por tirada | 52 879 | 53 045 |
| Tokens por arreglo aceptado | 111 979 | 65 849 |
| Coste declarado por `claude -p` | 20,57 USD | 22,19 USD |

**Uso de la herramienta (BU):**
- probó en 34 de 36 tiradas, con 1,53 pruebas de media;
- en 33 de las 34 entregó el último parche probado;
- ninguna probó primero el árbol tal cual (L-BU-5);
- la caja estuvo abierta 65,6 min en las 36 tiradas de casos reales y 71,0 min contando los limpios. Es el tiempo que USER
  estuvo parado por las tiradas, sin contar la evaluación.

El bucle cuesta casi lo mismo por tirada y la mitad por arreglo aceptado.

## La lectura de parches (L-AG-3)

- **Selección de `bu3.py`:** 4 parches aceptados de BU sorteados y 2 de AG₁, y 3 sospechosos. Los sospechosos son las 2
  tiradas BU con sobreajuste (H-ORU-5) y 1 parche aceptado de AG₁ con literal de prueba (H-ORU-4).
- **Jev clasifica los 9 como `arregla_la_causa`** (confianza 0,97-1; `agente/bucle/decision-jev-bu3-lectura.md`). Contando
  solo los aceptados, 7 de 7: 4 de BU y 3 de AG₁.
- **El literal «101.00» del parche de AG₁** está en un comentario que cita el valor esperado, no en la lógica. El escáner lo
  marca bien por construcción y la lectura lo descarta.
- **Control del lector (DV-BU-10).** Con 9 de 9 iguales no se sabía si Jev podía contestar otra cosa. Se le pasaron, con el
  mismo formato y sin decirle cuáles eran, 3 parches escritos a mano (`agente/bucle/estado_bu3_lectura_control.md`):
  - 2 que reconocen el caso de prueba, un valor fijo para el código 2345-7 y una lista de MSH-10 → `adapta_al_juez` (0,83 y
    1,0);
  - 1 genérico pero incompleto → `arregla_la_causa` (0,98).

  **Jev separa la trampa del arreglo, pero no juzga si el arreglo está completo.** Eso lo mide FIX.
- **Las explicaciones de los agentes van tal cual**, como en AG3 y AMP3. El estado no dice el brazo, pero en varias se lee
  «probado en la caja».

## Amenazas del diseño (§6), con lo observado

1. **Adaptarse al juez:**
   - sobreajuste bajo el umbral;
   - FIX_parcial_oculto 0,87 en BU;
   - 7 de 7 aceptados leídos como arreglo, con un lector que sí detecta la trampa.

   Lo residual (L-AG-3) lo acota la lectura, pero no lo elimina.
2. **El factor no es puro:** ninguna tirada BU probó primero el árbol vacío, y la ganancia aparece en multigrupo y monogrupo.
3. **Deriva del modelo:** AG₁ = AG₀ (8,5 y 8,5).
4. **El reloj compartido:** 0 tiradas cortadas en los dos brazos. El bucle cabe en 10 minutos.
5. **Caja inestable:** 0 incidencias y ninguna restauración fallida.
6. **El mismo corpus genera y contrasta la hipótesis (L-BU-2):** sin reserva. La conclusión vale para estos circuitos y este
   juez.
7. **Quien implementa conoce los resultados:** nada se tocó tras la primera tirada, salvo los recuentos de la auditoría
   (DV-BU-7 y DV-BU-8), decididos antes de evaluar.
8. **USER parado:** 71,0 min por las tiradas BU, más las evaluaciones. Al cierre está en marcha, con su huella y la sonda AA.
9. **Fragilidad de la consigna:** un solo texto, y el agente probó en 34 de 36 tiradas.
10. **n = 18 y techo bajo:** aun así, cruza la regla.

## Desviaciones (DV-BU)

- **DV-BU-1..6:** en el sello. **DV-BU-7 y DV-BU-8:** adendas durante BU2, en el sello.
- **DV-BU-9.** `bu3.py` sortea la lectura, pero no escribe el estado para Jev ni la tabla por caso, aunque su cabecera lo
  diga.
  - El estado lo escribe `agente/bu3_lectura.py`, calcado de `ag3_lectura.py`: sin brazo, sin aceptación y en un orden fijo.
  - La tabla por caso sale de `analisis.json` y de los `fix.json`.
  - No cambia ningún número.
- **DV-BU-10.** El control del lector, que el diseño no pedía (arriba).
- **DV-BU-11.** BU3 se hizo el 22-oct, 8 días después de BU2: la sesión del 14-oct terminó después de la evaluación, sin
  llegar a BU3. Entre medias no se tocó nada: `bu3.py` y la clave tienen la huella del sello.

## Lo que no dice

- **Que el bucle sirva fuera de estos 18 casos,** de estos circuitos o de este juez (L-BU-2).
- **Que el agente pueda arreglar solo.** Quedan 3,5 casos sin arreglo, y el FIX lo da el mismo juez que el agente consulta. La
  lectura acota la trampa, no la elimina (L-AG-3).
- **Junto al piloto:** localizar ya estaba casi resuelto (17/18), y arreglar sube de 8,5 a 14,5 cuando el agente puede
  probar su parche.

## Cierre (22-oct)

- **Cajas:** LABMUT, LABADTMUT, LABORUMUT y LABMULTIMUT paradas, igual que el resto de namespaces del laboratorio
  (comprobado con `Ens.Director`).
- **USER en marcha:** `comprobar_circuito.py` da IGUAL (`342a21b5`) y la sonda contesta `MSA|AA`.
- **Guarda:** `antes_de_publicar.py` LIMPIO.
- **Publicación:** subir al repo público el diseño, el sello y este resultado (sin la clave, sin transcripciones y sin
  `pruebas.jsonl`) espera al visto bueno de Víctor al diff.
