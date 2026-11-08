# RESULTADO de la etapa 38: las clases publicadas del estudio de conversores (8-nov-2026)

> **Las clases publicadas del estudio de conversores se reproducen con su receta; la diferencia de M-4, M-36 y L-24 viene del juez
> de CV4 y, en M-4, también de su regla, que no reconocía el texto nuevo del juez.**
>
> - **Con el juicio del estudio** (CV3, juez `54a90cd9`), `cv/cv3_clases.py` vuelve a escribir `cv/CLASES-CV3.json`: las mismas
>   clases, casos y ejemplos, las mismas convenciones y la misma frase. Nada queda sin clase. Solo difieren el campo del juez, las
>   notas que le añadieron las etapas 29 y 30 y, con el guion de hoy, la descripción de M-28 (abajo, «Lo medido»).
> - **El juez cambió en CV4,** el mismo 24-oct, después de escribirse las clases. `RESULTADO-CONVERSORES.md` lo declara:
>   - CX.4 se compara sin espacios ni signos, y desaparecen tres falsos positivos. Por eso M-36 y L-24, que eran esos falsos
>     positivos y estaban apartados, se quedan sin casos;
>   - PL.9 dentro de la descripción pasa a «valor distinto», con un texto nuevo.
> - **La regla de M-4 solo reconocía el texto de CV3.** Con el juez publicado desde CV4, el hallazgo de PL.9 de 8 de sus 16 casos
>   quedaba sin clase (esos casos conservan sus otras clases). Desde esta etapa reconoce los dos textos, y M-4 vuelve a sus 16
>   casos.
>
> La frase del estudio no cambia: 15 nuevas, 31 ya declaradas y 16 convenciones.

La pregunta, fijada antes de medir, está en [`ANTES-ETAPA-CLASES.md`](ANTES-ETAPA-CLASES.md).

## Cómo se hizo

| | |
|---|---|
| La previsión | De Jev, sellada antes de medir la causa: [`cl/PREVISION-CL.json`](cl/PREVISION-CL.json), con su huella en [`cl/SELLO-CL.txt`](cl/SELLO-CL.txt) y su estado en [`cl/estado_prevision_cl.md`](cl/estado_prevision_cl.md) |
| La reproducción | [`cl/reproducir_clases_cl.py`](cl/reproducir_clases_cl.py) calcula las clases con cada juicio y las compara con el JSON publicado: de cada clase, su clase, casos, ejemplos y conversor; la frase; y lo que queda sin clase. Y caso a caso, con el de la receta. Salidas: [`cl/REPRODUCCION-CL.json`](cl/REPRODUCCION-CL.json), con la regla de antes, y [`cl/REPRODUCCION-CL-despues.json`](cl/REPRODUCCION-CL-despues.json), con la nueva. La primera la escribió una versión anterior del guion, que no guardaba lo sin clase; está rehecha con el guion publicado y la regla de antes. Los juicios no van al repositorio |
| La decisión | Arreglar la regla de M-4 o solo decirlo: Jev, arreglarla (0,84; [`cl/estado_cl.md`](cl/estado_cl.md), [`cl/decision-jev-cl.md`](cl/decision-jev-cl.md)) |
| El diseño | A ciegas, por Fable: [`cl/diseno-cl-fable.md`](cl/diseno-cl-fable.md), con su encargo en [`cl/encargo-diseno-cl.md`](cl/encargo-diseno-cl.md). Cita un guion de preparación del laboratorio, que no va al repositorio |
| La prueba, en rojo antes | [`cv/prueba_cv3_clases.py`](cv/prueba_cv3_clases.py), nueva. Contra la regla de antes caen 2 de 10 comprobaciones ([`cl/ROJO-CL.txt`](cl/ROJO-CL.txt)): el texto de CV4 no tenía clase (lo que preveía el diseño), y ninguna regla llevaba una tupla de textos. Después, TODO BIEN ([`cl/PRUEBA-CLASES.txt`](cl/PRUEBA-CLASES.txt)). El rojo y el arreglo van en el mismo commit; que el rojo fue antes lo dicen las horas de los ficheros. La prueba mira la regla de M-4 y sus vecinas; que el cambio no mueve nada más lo mide la reproducción. Tras la revisión cambió el docstring de la prueba, y no su lógica: el rojo se corrió con la versión anterior, el registro de después lleva la hora en que se volvió a correr, y el segundo bloque de `cl/SELLO-CL.txt` se rehízo con las huellas nuevas |
| El arreglo | [`cl/parche_m4_cl.py`](cl/parche_m4_cl.py) en `cv/cv3_clases.py`, con el bloque 9 del sello de la etapa 33 (`ga/SELLO-GA.txt`) |

## Lo medido

**Los juicios:**
- el del estudio, CV3;
- el de CV4, del mismo 24-oct;
- el de hoy, con el juez de la etapa 37.

El de hoy difiere del de CV4 en 13 de sus 736 casos, todos de las dos conductas de la etapa 37.

**El JSON entero.** Con el juicio del estudio, el JSON calculado solo difiere del publicado en esto:
- el campo `juez`, que el guion pone con el juez de la carpeta;
- las notas de las etapas 29 y 30: `nota_iv` en M-23, M-24 y L-18; `nota_auditoria` en L-15 y L-19; y `par_valido` en L-19;
- con el guion de hoy, además, la descripción de M-28, que corrigió la etapa 36.

Con el `cv/cv3_clases.py` del estudio, ni eso último.

| Juicio | Regla de M-4 | Sin clase | Clases que difieren del JSON publicado | Frase |
|---|---|---:|---|---|
| CV3 | de antes | 0 | ninguna | igual |
| CV3 | nueva | 0 | ninguna | igual |
| CV4 | de antes | 8 | M-4 (16 → 8), M-36 (1 → 0), L-24 (2 → 0) | igual |
| CV4 | nueva | 0 | M-36 y L-24 | igual |
| De hoy | de antes | 8 | M-4, M-36, L-24, y L-4 (92 → 96 en ADT, por la etapa 37) | igual |
| De hoy | nueva | 0 | M-36, L-24 y L-4 | igual |

- **Lo que cambió el juez de CV4 en el estudio:** 12 casos de 736.
  - **PID-3 (CX.4):** tres falsos positivos desaparecen. Son las muestras `ms-LRI_2.0-NG_CBC_Typ_Message` de los dos conversores y
    `ms-ORU-R01-01` de LinuxForHealth, que eran M-36 y L-24. La de Microsoft pasa a correcta.
  - **PV1-3 (PL.9):** 8 casos de Microsoft cambian el texto de su hallazgo, de «falta la descripción '…' (PL.9)» a «la descripción '…'
    contiene PL.9 '…' sin ser PL.9». En 6 el subtipo pasa además a «dato perdido + valor distinto», y los otros 2 ya lo eran.
  - **ORU-B30:** su referencia rota lleva el hecho «PID».
- **Los 8 casos de M-4** son `A1-A01-03`, `A1-A02-08`, `A1-A03-13`, `A1-A04-18`, `A1-A08-23`, `A1-A11-28`, `A1-A13-33` y `A1-A31-38`.
  - Con la regla de antes, su hallazgo de PL.9 no casaba con ninguna regla. La de M-4 es la última de Microsoft para su mecanismo, y
    pedía «falta la descripción».
  - Los otros 8 casos de M-4 (`A1-A01-04`, `A1-A02-09`… `A1-A31-39`) siguen con el texto de CV3. Su descripción lleva una
    secuencia de escape (`\S\`).
- **Lo que dice lo publicado:** el resultado de CV4 dice que «M-36 y L-24 ya estaban apartadas, y M-4 es ya declarada en los dos
  jueces», y que la frase no cambia. Es cierto de las clases. Del aparato, se quedaba corto: con el juez de CV4, la regla de M-4
  reconocía 8 de sus 16 hallazgos.
- **Los JSON de clases de etapas pasadas** se escribieron con el juez de después de CV4 y la regla de antes, y llevan M-4 con 8
  casos:
  - `ga/CLASES-GA-v1.json`, `jz/CLASES-JZ-antes.json` y `jz/CLASES-JZ-despues.json`, con estos 8 hallazgos sin clase;
  - `ga/CLASES-GA-v2.json`, con 39 sin clase: estos 8 y los 31 de las 2 candidatas de la etapa 33, que la 36 resolvió.

  Se quedan como se escribieron.

## La previsión

| | Jev | Lo medido |
|---|---|---|
| De dónde viene la diferencia | Más de una causa (0,64; la entrada, 0,31), con confianza 0,52 | Más de una: el juez de CV4 en las tres clases y, en M-4, también la regla |
| Si cambia la frase | No (0,77), con confianza 0,54 | No |

Acertó las dos, con un estado al que le faltaba el hecho decisivo (abajo).

## Lo que llevaban mal los estados y el encargo

- **El estado de la previsión** ([`cl/estado_prevision_cl.md`](cl/estado_prevision_cl.md)) no traía la causa.
  - Daba como cambios del juez desde el 24-oct los de las etapas 20, 26, el 4-nov y la 37, y omitía el de CV4, del mismo 24-oct.
  - No decía que `jz/CLASES-JZ-*.json` ya listaban los 8 hallazgos sin clase.
- **El ANTES** dice que el JSON lo escribió por última vez la etapa 30. Las 29 y 30 solo le añadieron notas: los casos son del
  estudio (CV3).
- **El estado de Q-CL-1, el encargo y el diseño** dicen que el juicio de hoy es idéntico al de CV4 en los 736 casos. Difieren 13,
  los de la etapa 37. El encargo añade que ninguna otra clase cambia salvo M-36 y L-24, y también cambia L-4 (92 → 96). Ninguna
  de las dos cosas toca la decisión, que era sobre M-4.

## Lo que cambia en lo publicado

- **`cv/cv3_clases.py`:** la regla de M-4 acepta los dos textos (una tupla, de los que basta uno), y `regla()` admite tuplas. Ninguna
  otra regla cambia. Va con el bloque 9 del sello de la etapa 33.
- **`cv/prueba_cv3_clases.py`,** nueva, con 10 comprobaciones.
- **Las marcas, sin reescribir lo sellado:**
  - en `cv/RESULTADO-CV3.md`, la de la etapa 38;
  - en `RESULTADO-CONVERSORES.md`, una nota junto a «M-4 es ya declarada en los dos jueces»;
  - en `RESULTADO-JUEZ.md`, una línea en «Lo que se vio de paso».
- **Lo que no cambia:** `cv/CLASES-CV3.json`, que se reproduce con su receta, y los JSON de clases de etapas pasadas.

## Lo que se vio de paso

- **`cv/cv3_clases.py` dice que «comprueba que nada que cuente quede sin clase», pero solo lo lista, sin fallar.** Así pasaron sin
  verse los 8 de M-4, también en las clases que calculó la etapa 37. Hacerlo fallar cambia un aparato sellado que usan otras
  etapas; queda fuera de esta. Desde esta etapa, `cl/reproducir_clases_cl.py` guarda lo que queda sin clase.
  *Etapa 39 (8-nov):* el aparato ya lo cuenta en su salida (`n_sin_clase`) y avisa al final, sin fallar
  ([`RESULTADO-SINCLASE.md`](RESULTADO-SINCLASE.md)).
- **Los 8 casos de M-4 cuya descripción lleva una secuencia de escape** siguen con el texto de CV3: el juez no la encuentra en la
  descripción de Microsoft. Cuentan como M-4 con las dos reglas. Si deberían llevar el texto de CV4 es cosa del juez, y queda fuera.

## Cómo se repite

Desde `verificador/`:
- la prueba: `python3 cv/prueba_cv3_clases.py`;
- la reproducción, con los juicios de la herramienta (`cv/juzgar_cv2.py`):
  `python3 cl/reproducir_clases_cl.py <salida.json> <juicio de la receta> <evidencias> <otro juicio> [...]`.
