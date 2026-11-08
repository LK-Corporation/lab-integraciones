# RESULTADO de la etapa 39: lo que queda sin clase en el estudio de conversores (8-nov-2026)

> **Con el juez y el aparato de hoy quedan 0 hallazgos sin clase en los corpus que clasifica `cv/cv3_clases.py`; el aparato no
> falla cuando queda alguno: lo cuenta en su salida y avisa al final.**
>
> - **Antes del cambio quedaban 30,** todos en la versión 2 del corpus de la etapa 33: la Observation de ACC de Microsoft en 30 ADT
>   del corpus del laboratorio.
>   - La etapa 36 la dio por M-28, ya declarada.
>   - La regla de M-28 solo miraba los casos `ms-ADT` (las muestras ADT de Microsoft). Ahora la mira en cualquier corpus de
>     Microsoft, para el hallazgo que el juez escribe desde la etapa 37.
> - **El aparato decía que «comprueba que nada que cuente quede sin clase», y solo lo listaba.** Ahora:
>   - escribe en su salida cuántas entradas quedan sin clase (`n_sin_clase`);
>   - si queda alguna, avisa al final por la salida de error;
>   - sigue saliendo con 0 (Jev: avisar, no fallar).
>
> La frase del estudio no cambia: 15 nuevas, 31 ya declaradas y 16 convenciones.

La pregunta, fijada antes de medir, está en [`ANTES-ETAPA-SINCLASE.md`](ANTES-ETAPA-SINCLASE.md).

## Cómo se hizo

| | |
|---|---|
| La previsión | De Jev, sellada antes de medir: [`sc/PREVISION-SC.json`](sc/PREVISION-SC.json), con su huella en [`sc/SELLO-SC.txt`](sc/SELLO-SC.txt) y su estado en [`sc/estado_prevision_sc.md`](sc/estado_prevision_sc.md). La primera pregunta salió con confianza 0,25, se repreguntó con el mismo estado y dio 0,20 |
| La medida | [`sc/medir_sinclase_sc.py`](sc/medir_sinclase_sc.py), sobre copias: de cada corpus que clasifica el aparato, lo sin clase y la frase. La versión 1 y la 2 del corpus de la 33 se miden con su juicio guardado y con el juez de hoy; el estudio, con el juez de hoy. Antes del cambio, [`sc/SINCLASE-SC.json`](sc/SINCLASE-SC.json); después, [`sc/SINCLASE-SC-despues.json`](sc/SINCLASE-SC-despues.json). Las evidencias no van al repositorio |
| Las decisiones | Jev, con los hechos medidos ([`sc/estado_sc.md`](sc/estado_sc.md), [`sc/decision-jev-sc.md`](sc/decision-jev-sc.md)): que M-28 mire también el corpus del laboratorio para ese hallazgo, sin que su otro mecanismo alcance otros corpus (0,93); y avisar sin fallar (0,78; fallar, 0,19). Lo que ese estado llevaba mal está abajo |
| El diseño | A ciegas, por Fable: [`sc/diseno-sc-fable.md`](sc/diseno-sc-fable.md), con su encargo en [`sc/encargo-diseno-sc.md`](sc/encargo-diseno-sc.md) |
| La prueba, en rojo antes | [`cv/prueba_cv3_clases.py`](cv/prueba_cv3_clases.py), ampliada con P-SC-1 a P-SC-8. Su primera versión, contra el aparato de antes, dio 6 MAL ([`sc/ROJO-SC.txt`](sc/ROJO-SC.txt)); la publicada da 8. Tras la revisión a ciegas cambió el texto del aviso (el diseño trae el de antes, «hallazgos … mecanismos»), y entraron P-SC-7 y P-SC-8 (lo que cuenta el aviso, y el aparato como proceso), con su rojo contra el primer arreglo, 3 MAL ([`sc/ROJO-SC-2.txt`](sc/ROJO-SC-2.txt)). Después, TODO BIEN, 29 comprobaciones ([`sc/PRUEBA-SC.txt`](sc/PRUEBA-SC.txt)) |
| El arreglo | [`sc/parche_sc.py`](sc/parche_sc.py) en `cv/cv3_clases.py`, con el bloque 10 del sello de la etapa 33 (`ga/SELLO-GA.txt`) |
| La reproducción del estudio | Después del cambio, `cl/reproducir_clases_cl.py` con la receta de `cv/CLASES-CV3.json`: se reproduce, ninguna clase difiere y nada queda sin clase ([`sc/REPRODUCCION-SC.json`](sc/REPRODUCCION-SC.json)). El fichero trae también la comparación con el juicio de hoy, donde difieren L-4, L-24 y M-36: es la misma de `cl/REPRODUCCION-CL-despues.json`, y la explica `RESULTADO-CLASES.md` |

El diseño, el rojo, el cambio y el resultado van en el mismo commit; el orden lo dicen las horas de los ficheros (diseño, prueba y
rojo a las 15:53; el aparato cambiado, a las 15:54).

## Lo medido

| Corpus | Juicio | Sin clase, antes del cambio | Sin clase, después | Frase (N / D / C / M) |
|---|---|---:|---:|---|
| El estudio | con el juez de hoy | 0 | 0 | 15 / 31 / 16 / 368 |
| Versión 1 del corpus de la 33 | el guardado | 0 | 0 | 15 / 31 / 16 / 368 |
| Versión 1 | con el juez de hoy | 0 | 0 | 15 / 31 / 16 / 368 |
| Versión 2 | el guardado (juez de la 33) | 31 | 31 | 15 / 31 / 17 / 375 (*) |
| **Versión 2** | **con el juez de hoy** | **30** | **0** | 15 / 31 / 17 / 375 |

(*) Las convenciones las recalcula el aparato con el juez de hoy, sea cual sea el juicio. Por eso también aquí salen 17.

- **Los 30** son la Observation de ACC de Microsoft en 30 ADT del corpus del laboratorio. Desde la etapa 37, el juez la escribe como
  «recurso sin mapa», con el segmento por hecho.
  - La etapa 36 la clasificó como M-28: «la vio como candidata porque los 30 ADT con ACC son del corpus del laboratorio, que M-28 no
    miraba».
  - La regla de M-28 reconocía ese hallazgo desde la 37 (bloque 8 del sello), pero solo en los casos `ms-ADT`.
- **Los 31 del juicio guardado de la versión 2** son de un juez que ya no es el de hoy:
  - 30 son la misma Observation, vista como «sin origen propio»;
  - 1 es el PID-8 de LinuxForHealth.

  Son las 2 candidatas de la etapa 33. El JSON sellado de la 33 conserva lo que dio su juez, y el aviso los muestra si alguien
  vuelve a clasificar ese juicio.

## El cambio

- **M-28:** su límite de casos es ahora por mecanismo.
  - La Observation «recurso sin mapa» (`fuera:Observation|recurso_sin_mapa`) es M-28 en cualquier caso de Microsoft.
  - El mecanismo con que la veía el juez de antes de la 37 (`MC-ORU-7`) sigue limitado a los casos `ms-ADT`. Ese límite protege a
    M-29 (`lfh-ORU-*`, del mismo corpus de muestras), que va después de M-28 en las reglas. M-22 va antes y no depende de él.
  - Con el juicio guardado de la versión 2, los 30 que `MC-ORU-7` deja sin clase son los mismos 30 ADT, y con ese juez siguen sin
    clase. En el corpus del laboratorio sale además en ORU-B14, que es M-22.
  - `regla()` admite un diccionario de casos por mecanismo. Solo M-28 lo lleva.
- **El aviso:**
  - `main()` escribe `n_sin_clase` en su salida, fuera de la frase, que es lo que se compara con los JSON publicados. Cuenta
    entradas (textos del «que»), no hallazgos, como la lista `sin_clase`;
  - si queda alguna, la última línea va por la salida de error: «AVISO cv3_clases: N entradas sin clase (K firmas) en …», con el
    fichero de salida y el detalle. Una firma es conversor, mecanismo y texto sin valores. Va por esa salida porque
    `cv/ar/arrastre.py`, por el que lo llaman los guiones de la 33, redirige la salida normal y no la de error;
  - el código de salida sigue en 0;
  - el canal de la etapa 33 (`ga/comparar_ga.py`, que toma por candidatas lo sin clase de la versión 2 que no está en la 1) no
    cambia.

## Qué pasaría si el aparato fallara

El ANTES pedía medirlo, y el estado que se dio a Jev no lo traía.
- **Quién lo llama.** Los tres que llaman a `main()` lo hacen como función, no como proceso:
  - `cv/ar/arrastre.py`, que usan `ga/comparar_ga.py` y `sc/medir_sinclase_sc.py`;
  - `cl/reproducir_clases_cl.py`;
  - la propia medida de esta etapa.
- **Un código de salida** en la orden del aparato no les llegaría.
- **Una excepción dentro de `main()`** pararía `ga/comparar_ga.py` y la medida de la versión 2 con su juicio guardado, que tiene 31
  sin clase.

## La previsión

| | Jev | Lo medido |
|---|---|---|
| Sin clase en la versión 2, con el juez de hoy | Ninguno (0,50, confianza 0,25; repreguntada, 0,47 y 0,20) | 30 |
| Qué hace el aparato | Avisar sin fallar, y que los guiones que lo usan lo lean (0,72) | Jev decidió avisar sin fallar (0,78); ningún guion lee `n_sin_clase` |

Falló en la primera. En la segunda, la decisión se tomó con la previsión delante (el estado la daba como hecho), y sin la medida de
qué pasaría si el aparato fallara.

## Lo que llevaba mal el estado de las decisiones

- **El estado** ([`sc/estado_sc.md`](sc/estado_sc.md)) decía que `MC-ORU-7`, «en otros corpus, es de otras clases», y no era exacto.
  Lo exacto es lo de «El cambio»: el límite protege a M-29; los 30 que `MC-ORU-7` deja sin clase en el corpus del laboratorio son
  los mismos 30 ADT, y sale además en ORU-B14, que es M-22.
- **No traía la medida** de «Qué pasaría si el aparato fallara».
- **Sí traía la previsión de Jev** para la misma pregunta.

## Lo que cambia en lo publicado

- **`cv/cv3_clases.py`:** M-28 y el aviso, con el bloque 10 del sello de la etapa 33.
- **`cv/prueba_cv3_clases.py`,** con 29 comprobaciones.
- **Las marcas, sin reescribir lo sellado:**
  - en `cv/RESULTADO-CV3.md`, la de la etapa 39;
  - en `RESULTADO-CANDIDATAS.md`, una línea en «que M-28 no miraba»;
  - en `RESULTADO-GENERADORES.md`, una nota en su cabecera;
  - en `RESULTADO-CLASES.md`, una línea en «Lo que se vio de paso».
- **Lo que no cambia:** `cv/CLASES-CV3.json`, los JSON de clases de etapas pasadas y lo medido antes (`sc/SINCLASE-SC.json`).

## Lo que se vio de paso

- **La versión 2 da hoy 17 convenciones, y la 33 publicó 16.**
  - La decimoséptima es la de LinuxForHealth con PID-8 fuera de la 0001, que la 36 dio por convención y la 37 llevó al juez.
  - No es de lo sin clase.
  - Con el juez de hoy y el aparato de antes de esta etapa, el canal de `ga/comparar_ga.py` daría 1 candidata, la Observation sin
    mapa; las 0 de hoy necesitan también el cambio de M-28. Lo dice una nota en `RESULTADO-GENERADORES.md`.
- **La regla de M-28 no mira el segmento:** cualquier Observation «recurso sin mapa» de Microsoft es M-28. Hoy solo la producen ACC
  y PDA, que es lo que M-28 declara. Si un juez futuro la diera para otro segmento, caería en M-28 sin aviso.

## Cómo se repite

Desde `verificador/`:
- la prueba: `python3 cv/prueba_cv3_clases.py`;
- la medida, con los árboles de la herramienta y unas evidencias:
  `python3 sc/medir_sinclase_sc.py <salida.json> <árbol v1> <árbol v2> <evidencias del estudio>`.
