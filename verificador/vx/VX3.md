# VX3: contraste, clase, pares mínimos y revisión adversaria (etapa 20)

**La regla.** Es la del estudio de conversores (`cv/diseno-conversores-fable.md` §4.3, R-CV-9), escrita antes de medir:

- **`ya_declarada`.** La misma diferencia aparece en una salida esperada publicada, en una prueba que la afirma, en la
  documentación o en un issue. El código de las plantillas no cuenta.
- **`convencion`.** Releídos el ConceptMap y la hoja CSV, la guía admite lo observado. El perfil se corrige con un DV y se rejuzga.
- **`nueva`.** Cualquier otro caso. Es confirmada si se reproduce con un par mínimo.

**La clasificación.** Está en `vx/CLASES-VX3.json`, con la referencia exacta de cada mecanismo. El juez de los resultados es
`11a3754fb8b6`.

## Cómo se hizo

1. **El contraste, a ciegas de la clasificación.** Tres agentes leyeron en solo lectura, sin ejecutar código de terceros:
   - las salidas esperadas, las pruebas, la documentación y los 587 + 533 issues y PR de cada proyecto;
   - para los 40 mensajes del corpus, un agente por conversor;
   - otro, para lo que solo sale en las 85 muestras.

   Cada fila lleva la referencia y una cita de 15 palabras o menos.
2. **La revisión adversaria, a ciegas del contraste.** Un agente intentó tumbar los 23 hallazgos del corpus con la guía (ConceptMap,
   hojas CSV, texto de v2.5, perfiles de R4). Tumbó 1, dejó 4 en duda y sostuvo 18.
3. **Los pares mínimos.** Están en `cv/cv3_minimos_vxu.py`: 25 pares y una secuencia, corridos con los dos conversores en su caja.
   Se confirman 25 de 26. El que no se confirma es VL08 (`isSubpotent`), que pasó a convención.
4. **La adjudicación.** La hice yo, con los precedentes de `cv/CLASES-CV3.json` y anotando cada decisión dudosa.

## Lo que la revisión adversaria cambió en el juez (rejuicio 1 de 2, `f933020`)

| Hallazgo | Veredicto | Corrección |
|---|---|---|
| H19: `isSubpotent` con RXA-20 PA | tumbado | **DV-VX-8.** Deducido de RXA-20 PA (R4, comentario de `Immunization.isSubpotent`: «partial administration»), y `primarySource` deducido de RXA-9, son convención. Antes eran dato inventado por Q-VX-D-7, que habla de lo escrito «por omisión» |
| H2: uri de MVX | dudoso | **DV-VX-7.** CVX y MVX admiten también la uri de la tabla v2 que trae R4 (`v2-0292`, `v2-0227`). No cambia ningún resultado: Microsoft usa `example.com` |
| H10: teléfono con solo XTN.7 | dudoso | **DV-VX-9.** En NK1 el número vale también en la extensión `contactpoint-local`, que es donde lo lleva la guía (`datatype-xtn-to-contactpoint`, extension[3]). Microsoft no lo escribe en ninguno de los dos sitios: el hallazgo sigue. En PID (perfil de ADT) no se toca; queda anotado |
| H12 y H21: la condición del OBX de ORDER | dudoso | **AMB-VX-13.** El «AND» de `message-vxu-v04-to-bundle` se lee como el «OR» de PERSON_OBSERVATION; la alternativa queda declarada. Los mecanismos afectados son ya declarados |

**Avisos de la revisión que no cambian el juez:**
- **La licencia general de la guía.** La página `implementation_considerations.html` pide revisar todos los mapas de terminología.
  Leída como licencia general, tumbaría la ruta, el sitio, GRD y PV1-2. No se aplica, porque la vara son los mapas base, pero es el
  primer contraargumento que pondrá un tercero.
- **Las columnas que solo están en las hojas CSV.** «Data Type Mapping» y «References» (`partOf`) no están en el ConceptMap 1.0.0.
  El juez las toma de las CSV del commit `873b331`, igual que en el estudio de conversores.

## El resultado

| | Microsoft | LinuxForHealth | Total |
|---|---|---|---|
| **Nuevas y confirmadas** | 6 (4 fuertes) | 3 (1 fuerte) | **9** |
| Ya declaradas | 11 | 15 | **26** |
| Convención (notas) | 2 | 3 | **5** |
| Dudosas (no cuentan) | — | 1 (VX-L21) | 1 |
| Muestras inválidas (no cuentan) | 2 (VX-M19, VX-M20) | — | 2 |

**Las nueve nuevas** (par mínimo en `cv/cv3_minimos_vxu.py`):

| Id | Discrepancia | Fuerza |
|---|---|---|
| VX-M7 | El lote repetido se concatena: `LOT-A+DIL-B` | fuerte |
| VX-M10 | NK1-3 GRD: la relación de tutor queda sin código | fuerte |
| VX-M14 | RXA-6 `.5` se escribe 5: la dosis se multiplica por diez (misma causa que M-24, el NM `.5` del estudio de conversores) | fuerte |
| VX-M15 | El `status` sale de RXA-18 y no de RXA-20: una vacuna rechazada (RE) o no administrada (NA) sin RXA-18 sale `completed` | fuerte |
| VX-M8 | El nombre del fabricante une CE.2 y CE.5 con «--» | débil |
| VX-M12 | De dos RXA-19 solo llega una a `reasonCode` | débil |
| VX-L6 | RXA-21 = D (registro anulado) sale `completed` y no `entered-in-error` | fuerte |
| VX-L8 | De dos RXA-10 solo llega el primer profesional | débil |
| VX-L9 | De dos RXA-19 solo llega una a `reasonCode` | débil |

**Decisiones de adjudicación dudosas, todas en la dirección conservadora (hacia `ya_declarada`):**
- **Por la misma regla declarada en otro segmento, como ya hizo el estudio de conversores (L-26):**
  - VX-L4: la unidad de CE.1, declarada en OBX-6;
  - VX-M5: la unidad sin CE.2, por la misma plantilla que OBX-6.
- **Declaración genérica en la documentación:**
  - VX-M3: la URL ficticia;
  - VX-M13: la fusión por id repetido, como M-19 y M-20;
  - VX-M16: la limitación de `get_related_segment_list`, como M-21.
- **VX-L7:** el #344 declara RXA-22 → `recorded` sin condición.
- **VX-L11:** el README no incluye NK1 entre los segmentos soportados, como L-4.
- **VX-L14:** el estado arrastrado entre mensajes es el #348, abierto, aunque su arreglo provisional no cubre este disparador.

**El estado arrastrado de LinuxForHealth (VX-L14).** En el lote de 40 bases, tras convertir B17 (RXA-17 `^Laboratorio Sintetico^`,
sin código), todos los mensajes siguientes salen sin `manufacturer`.

- Convertidas una a una (`privado/vx/vx2c/lfh-por-mensaje/`), las 40 dan el mismo juicio que el lote, salvo esos 23 `RXA-17 dato_perdido`.
- La secuencia VL11 lo confirma: B17 y luego el nominal, en el mismo proceso, el nominal sale sin fabricante; el nominal solo, con él.
- El proyecto conoce el síntoma: #348, «Repeating messages do not completely reset internal variables». Su arreglo provisional
  (`condition: rxa17 NOT_NULL`) solo evita el caso de RXA-17 vacío dentro de un mensaje.

**Fuera de las cuentas de VXU.** Lo que cuenta en Patient y Encounter es el perfil de `adt_conv`, y ya lo clasificó el estudio de
conversores. En las bases es PV1-2 de B38 en LinuxForHealth, que es L-3 y L-5, ya declaradas. En las muestras aparecen PID-3/5/11/12/13/14
y PV1-2/3/6/10/42/44/52.

**Las muestras públicas.** De lo que cuenta en ellas y es propio de VXU, quitadas las inválidas y la convención, son ya declaradas:

| Conversor | Ya declaradas | Nuevas |
|---|---|---|
| Microsoft | 10 de 12 mecanismos (83 %) | VX-M14 y VX-M15 |
| LinuxForHealth | 12 de 12 (100 %) | ninguna; queda aparte la dudosa |

La previsión pedía al menos el 70 %.
