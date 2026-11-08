# Diseño a ciegas de la etapa 39: M-28 en el corpus del laboratorio y el aviso de lo sin clase

Diseñado el 8-nov-2026 sobre `sc/decision-jev-sc.md` (Q-SC-1 a, Q-SC-2 b) y `ANTES-ETAPA-SINCLASE.md`. Todo lo de abajo se midió
sobre copias de `fase12` y de los dos árboles de la etapa 33, sin tocar nada del laboratorio. **La frase del estudio no se mueve:**
con el juicio de hoy del estudio, el aparato cambiado da las mismas clases, los mismos casos y la misma frase (15 nuevas, 31 ya
declaradas, 16 convenciones, 368 mensajes), y nada sin clase.

## 1. El cambio de M-28: el límite de casos, por mecanismo

**Qué hay hoy.** La fila de M-28 en `cv/cv3_clases.py` lleva dos mecanismos y un solo límite de casos para los dos:

    ("M-28", MS, {"MC-ORU-7", "fuera:Observation|recurso_sin_mapa"}, None, ("ms-ADT",), "ya_declarada", …)

Los dos mecanismos no son del mismo juez:
- **`fuera:Observation|recurso_sin_mapa`** lo escribe el juez desde la etapa 37: «Observation … de ACC (ACC-1 = …), que la hoja de
  ADT_A01 de la guía lista sin destino», con el segmento por hecho (`ACC`, `PDA` o `ACC/PDA`). Con el juez de hoy, Microsoft lo
  produce **solo** en 7 muestras `ms-ADT` del estudio y en 30 ADT del corpus del laboratorio de la versión 2; en ningún ORU, en
  ninguna otra muestra, nunca en LinuxForHealth (medido en el juicio de hoy del estudio y en los dos árboles rejuzgados hoy). Es,
  literalmente, la conducta de M-28: una Observation de un segmento que la guía no mapea.
- **`MC-ORU-7`** («Observation … sin origen propio en el mensaje») es el mecanismo por el que el juez de antes de la 37 veía esa
  misma Observation, y por eso hace falta para reproducir `cv/CLASES-CV3.json` con su receta. Pero en otros corpus es de otras
  clases: `ORU-B14` (M-22, ambigüedad), `lfh-ORU-*` (M-29, muestra inválida), y en el corpus del laboratorio de la versión 2, con
  el juicio guardado, son los 30 ADT que la 33 dejó como candidatas. Si se quitara el límite sin más, M-28 se los llevaría a todos
  (M-22 va antes en `R`, pero M-29 va después).

**El cambio.** `casos` admite, además de `None`, conjunto o tupla de prefijos, **un diccionario por mecanismo** con esas mismas
formas como valores, y `regla()` escoge la entrada del mecanismo con el que ha casado. Es el mismo gesto que la 38 hizo con
`texto` (una tupla de la que basta uno): una forma más del mismo campo, explícita en la fila, sin tocar la firma de `regla()`.

    ("M-28", MS, {"MC-ORU-7", "fuera:Observation|recurso_sin_mapa"}, None,
     {"MC-ORU-7": ("ms-ADT",), "fuera:Observation|recurso_sin_mapa": None}, "ya_declarada", …)

    def regla(conv, mc, q, caso):
        for r in R:
            …
            if isinstance(casos, dict):   # etapa 39: el límite de casos, por mecanismo (M-28: MC-ORU-7 solo en las muestras)
                casos = casos[mc]
            if casos is not None and not (caso in casos if isinstance(casos, set) else caso.startswith(casos)):
                continue
            return r

`casos[mc]` y no `casos.get(mc)`: si una fila olvidara un mecanismo, que falle a la vista, no que lo trate como «cualquier caso»
(la prueba P-SC-4 exige que las claves sean exactamente los mecanismos de la fila). El comentario de cabecera de `R` dice la
forma nueva. Ninguna otra fila cambia. `MC-ORU-7` sigue limitado a `ms-ADT`, así que no alcanza ningún otro corpus: medido abajo,
M-22 y M-29 conservan sus casos (1 en `oru`, 2 en `muestras`) y, con el juicio guardado de la versión 2, los 30 ADT con
`MC-ORU-7` siguen sin clase, como deben (son del juez que ya no existe; su JSON sellado no se toca).

**Medido** (aparato de hoy frente al aparato con el cambio; «hoy» = juicio nuevo con el juez de hoy, huella `7a9bf9b7…`):

| Corpus y juicio | Frase (N / D / C / M) | Sin clase: antes → después | Clases cuyos casos cambian | Casos que cambian de clase |
|---|---|---|---|---|
| Estudio, juicio de hoy | 15 / 31 / 16 / 368, igual | 0 → 0 | ninguna | 0 |
| Estudio, juicio de CV2 (`privado/cv/cv2/juicio.jsonl`) | 15 / 31 / 16 / 368, igual | 34 → 34 | ninguna | 0 |
| Versión 1, juicio guardado | 15 / 31 / 16 / 368, igual | 0 → 0 | ninguna | 0 |
| Versión 1, juicio de hoy | 15 / 31 / 16 / 368, igual | 0 → 0 | ninguna | 0 |
| Versión 2, juicio guardado | 15 / 31 / 17 / 375, igual | 31 → 31 | ninguna | 0 |
| **Versión 2, juicio de hoy** | 15 / 31 / 17 / 375, igual | **30 → 0** | **solo M-28:** `muestras` 7 → `muestras` 7 + `adt` 30 | 30, todos de `sin_clase` a M-28 |

Los 30 son los ADT con ACC del corpus del laboratorio: `-004`, `-005`, `-006`, `-022` y `-024` de A01, A03, A04, A08, A13 y A31
(5 por evento); cada uno conserva sus otras clases (M-1, M-2, M-5, M-6, M-8, M-17). Las convenciones no dependen de `R` (se
recalculan del juez sobre las evidencias), por eso la versión 2 sigue en 17 con el juez de hoy.

## 2. El aviso: lo sin clase no para el aparato, pero no pasa sin verse

**Qué escribe.**
- **En la salida JSON,** una clave nueva de primer nivel, `"n_sin_clase"`: la suma de `sin_clase` (0 cuando no queda nada). Al
  lado de `sin_clase`, que sigue igual (`conversor | mecanismo | firma: n`). **No va dentro de `frase`:** `cl/reproducir_clases_cl.py`
  compara la frase clave a clave con el JSON publicado, y una clave nueva ahí rompería la reproducción. Fuera de `frase`, nadie
  la compara: `cv/ar/arrastre._planas` y `reproducir.comparar` leen claves concretas (medido: la única diferencia entre los JSON de
  antes y de después, en los seis corpus, es esa clave).
- **Al final de su ejecución,** si `sin` no está vacío, una línea **por la salida de error** (stderr), la última cosa que escribe:

      AVISO cv3_clases: 30 hallazgos sin clase (1 mecanismos) en arbol-v2/CLASES-AR.json: {"microsoft | fuera:Observation|recurso_sin_mapa | Observation <id> de ACC (…)": 30}

  Con el fichero de salida (sus dos últimos componentes de ruta, porque `ga/comparar_ga.py` escribe `CLASES-AR.json` en dos
  árboles seguidos y hay que saber de cuál es el aviso) y el diccionario `sin_clase` completo. Por stderr y no por stdout porque
  **todos los que lo llaman sin consola redirigen solo stdout:** `cv/ar/arrastre.juzgar_arbol` (y con él `ga/comparar_ga.py` y
  `sc/medir_sinclase_sc.py`) y `cl/reproducir_clases_cl.py`; stderr les llega a la consola. Y no mira `--silencio`: ese argumento
  lo ponen los llamadores para callar al juez, y si el aviso lo respetara, callaría en todos ellos, que es justo donde pasaron los 8
  de M-4. La línea `sin clase: {...}` de stdout se queda como está.
- **El texto de cabecera** deja de decir que «comprueba que nada que cuente quede sin clase» (lo que el ANTES señala): dice que lo
  lista, avisa al final y lo cuenta en su salida, sin fallar.

**Qué no cambia.**
- **El código de salida:** `main()` no devuelve nada y el `__main__` no llama a `sys.exit`; sigue saliendo con 0. Un guion que
  capture stderr lo verá como texto, no como fallo.
- **El canal de `ga/comparar_ga.py`:** sigue leyendo `sin_clase` de la versión 1 y de la 2 y dando por candidatas las de la 2 que
  no están en la 1. Con el juez de hoy, tras el cambio de §1, da 0 candidatas en la versión 2 (medido): es lo correcto, porque las
  2 de la 33 están resueltas (la 36 y la 37). El aviso cubre lo que el canal no ve: lo que está en las dos versiones.
- **`ga/cifras_ga_b.py`, `ga/cruce_ga.py` y `ga/riesgo_ga.py`** importan `cv3_clases` por `R` y `regla()`, no llaman a `main()`:
  ni ven el aviso ni les cambia nada (sus casos de M-28 en la versión 1 son los mismos; en la 2 ganan los 30 ADT solo si se
  recalculan, y sus JSON sellados no se recalculan).
- **`sc/medir_sinclase_sc.py`** calcula su `n_sin_clase` sumando `sin_clase`; sigue valiendo tal cual.

## 3. La prueba en rojo antes

Se amplía `cv/prueba_cv3_clases.py` (la de la 38), con el mismo patrón: hallazgos sintéticos con textos literales del juez, sin
leer juicios ni evidencias, más una pasada de `main()` sobre un juicio de dos filas en una carpeta temporal. Textos: el de ACC de
`ms-ADT-A01-01` y el de PDA de `ms-ADT-A02-01` del juicio de hoy (subtipo `recurso_sin_mapa`), y el de `MC-ORU-7` del juicio
guardado («Observation … sin origen propio en el mensaje», hecho `OBX`, subtipo `recurso_inventado`).

| Id | Comprueba | Hoy |
|---|---|---|
| P-SC-1 | la Observation de ACC sin mapa en `A01-004` es M-28; la de PDA en `A02-007`, también | **MAL** (`None`) |
| P-SC-2 | control: el mismo texto en `ms-ADT-A01-01` sigue siendo M-28, y `asignar` le da `fuera:Observation\|recurso_sin_mapa` | bien |
| P-SC-3 | `MC-ORU-7` no alcanza otros corpus: en `ms-ADT-A01-01` es M-28, en `ORU-B14` M-22, en `lfh-ORU-multiline-short` M-29, y en `A01-004` y `ORU-B09` no tiene clase; el texto de ACC en LinuxForHealth no tiene clase | bien |
| P-SC-4 | la forma de `R`: cada `casos` es `None`, conjunto, tupla o diccionario cuyas claves son exactamente los mecanismos de la fila (valores de esas formas); solo M-28 lleva el diccionario | **MAL** (ninguna fila lo lleva) |
| P-SC-5 | `main()` con un hallazgo que ninguna regla conoce: `n_sin_clase` = 1, `sin_clase` con una firma, «AVISO cv3_clases: 1 hallazgos sin clase (1 mecanismos)» en stderr, y `n_sin_clase` no está en `frase` | **MAL** (sin clave, sin aviso) |
| P-SC-6 | `main()` sin nada sin clase: `n_sin_clase` = 0 y ningún AVISO en stderr | **MAL** (sin clave) |

Medido con un borrador de esas comprobaciones contra el `cv3_clases.py` de hoy (huella `eea9c119f8f5…`): **6 MAL de 11**; contra
la copia con el cambio: **TODO BIEN, 17 comprobaciones**, y las 10 de la 38 siguen en TODO BIEN. P-SC-1, P-SC-4 y P-SC-5/6 caen
hoy por lo que arregla cada parte (el límite de casos, la forma, el aviso); P-SC-2 y P-SC-3 son los controles de que no se rompe
lo que ya iba bien. El rojo se guarda como la 38: `sc/ROJO-SC.txt` con la salida contra la huella de antes, y `sc/PRUEBA-SC.txt`
con la salida de después.

Y la medida de §1 se repite con el guion de la etapa, `sc/medir_sinclase_sc.py`, tras el cambio, a un fichero nuevo
(`sc/SINCLASE-SC-despues.json`): hecho cuando dice 0 en la versión 2 con el juez de hoy, 0 en el estudio, 0 en la versión 1, y las
tres frases iguales a las de `sc/SINCLASE-SC.json`. `sc/SINCLASE-SC.json` no se toca: es lo medido antes.

## 4. El sello

**Bloque 10 de `ga/SELLO-GA.txt`,** como los bloques 8 y 9 (lo escribe el parche de la etapa, `sc/parche_sc.py`, idempotente,
afirmando cada texto y conservando CRLF, en el laboratorio y en las copias del clon público):

    SELLO DE LA ETAPA 33, bloque 10 (<fecha>): desde la etapa 39, M-28 reconoce el corpus del laboratorio para la Observation sin mapa, y el aparato avisa de lo sin clase (sc/decision-jev-sc.md, Q-SC-1 a y Q-SC-2 b)
    # M-28: casos ("ms-ADT",) -> {"MC-ORU-7": ("ms-ADT",), "fuera:Observation|recurso_sin_mapa": None}, y regla() admite un diccionario de casos por mecanismo; main() escribe n_sin_clase y avisa por stderr al final; la clase, su texto y su referencia no cambian, ni el código de salida
    <huella>  cv/cv3_clases.py

**El sello propio de la etapa,** `sc/SELLO-SC.txt` (como `cl/SELLO-CL.txt`): `sc/parche_sc.py`, `cv/prueba_cv3_clases.py`
ampliada, `sc/ROJO-SC.txt`, `sc/PRUEBA-SC.txt`, `sc/SINCLASE-SC.json` y `sc/SINCLASE-SC-despues.json`, y la huella nueva de
`cv/cv3_clases.py`.

**No se toca:** `cv/CLASES-CV3.json` (se reproduce con su receta, §6), `ga/CLASES-GA-v1.json` y `ga/CLASES-GA-v2.json` (la v2
conserva sus 39 sin clase: así lo dio su juez), `jz/CLASES-JZ-*.json`, `cl/REPRODUCCION-CL*.json`, `sc/SINCLASE-SC.json`, ni
ningún bloque anterior del sello.

## 5. Qué se dice en lo publicado

Marcas al final, como las de la 37 y la 38; ningún resultado sellado se reescribe.

- **`RESULTADO-SINCLASE.md`** (nuevo, el del «hecho cuando»): «Con el juez y el aparato de hoy quedan 0 hallazgos sin clase en los
  corpus que clasifica `cv/cv3_clases.py`; el aparato no falla cuando queda alguno: lo cuenta en su salida (`n_sin_clase`) y avisa
  al final». Y, medido antes del cambio, los 30 de la versión 2, qué eran y por qué quedaban (el límite de M-28 a las muestras),
  la tabla de §1, la previsión sellada frente a lo medido («ninguno» con 0,50 no acertó: eran 30), y lo que no se resuelve (§6).
- **`cv/RESULTADO-CV3.md`,** «Marca de la etapa 39»: la Observation sin mapa de ACC o PDA es M-28 en cualquier corpus de
  Microsoft, no solo en las muestras (bloque 10); `MC-ORU-7` sigue limitado a las muestras; en el estudio nada cambia (M-28 sigue
  con sus 7 muestras); y el aparato avisa de lo sin clase sin fallar.
- **`RESULTADO-CANDIDATAS.md`,** una línea en la nota de la candidata de Microsoft («… que M-28 no miraba»): desde la etapa 39 la
  regla también mira el corpus del laboratorio para ese hallazgo, y los 30 ADT caen en M-28 con el juez de hoy.
- **`RESULTADO-GENERADORES.md`,** en la nota de cabecera (la de «Completado el 7-nov»): con el juez y el aparato de hoy, la
  versión 2 da 0 sin clase y 17 convenciones; las cifras publicadas (16 convenciones, 2 candidatas) son las del juez de entonces y
  no se reescriben. La decimoséptima es la de LinuxForHealth con PID-8 fuera de la 0001, que la 36 dio por convención y la 37 llevó
  al juez; no es de lo sin clase.
- **`RESULTADO-CLASES.md`,** «Marca de la etapa 39»: el cabo que dejó («solo lo lista, sin fallar… queda fuera de esta») se cierra
  con el aviso y la cuenta.
- **El clon público:** el parche aplica lo mismo en sus copias (`verificador/cv/cv3_clases.py`, `verificador/cv/prueba_cv3_clases.py`
  y `verificador/cv/RESULTADO-CV3.md`), como hicieron `jz/parche_m28_jz.py` y `cl/parche_m4_cl.py`.

## 6. Lo que no resuelvo y por qué

- **La reproducción de `cv/CLASES-CV3.json` con su receta** (`privado/cv/cv3/juicio-rejuicio2.jsonl`, juez de CV3) no la corrí:
  ese fichero no estaba entre los que podía leer. Por construcción no cambia: el cambio solo afecta a hallazgos de Microsoft con
  mecanismo `fuera:Observation|recurso_sin_mapa` fuera de `ms-ADT`, y ese mecanismo lo escribe el juez desde la 37; los juicios de
  antes (el «antes» de la 37, el guardado de la versión 1 y el de la 2) no lo producen ni una vez (medido). Con el juicio de CV2
  del mismo corpus, por la misma razón, 0 casos cambian de clase. Aun así, el «hecho cuando» del cambio debe incluir
  `cl/reproducir_clases_cl.py` con la receta: `se_reproduce` verdadero.
- **La regla no mira el segmento.** Con el cambio, cualquier Observation «recurso sin mapa» de Microsoft, en cualquier corpus, es
  M-28. Hoy solo la producen ACC y PDA (hechos `ACC`, `PDA`, `ACC/PDA`), que es lo que M-28 declara. Si un juez futuro la diera
  para otro segmento sin destino (UB1, UB2…), caería en M-28 sin avisar. La guarda barata, un `texto` («de ACC», «de PDA»), la
  descarto: la fila también casa por `MC-ORU-7` con otro texto («sin origen propio») en la receta, y un `texto` por fila rompería
  la reproducción o exigiría acoplar la regla a tres textos. Si hiciera falta, el sitio es una fila nueva antes de M-28 (la regla
  toma la primera que casa), con su prueba.
- **Con el juicio guardado de la versión 2** quedan 31 sin clase (los 30 ADT por `MC-ORU-7` y el PID-8 de LinuxForHealth): son
  de un juez que ya no existe, y no es lo que mide la etapa («el juez de hoy»). El aviso los mostrará si alguien vuelve a clasificar
  ese juicio; eso es lo que Jev pidió.
- **Fallar en vez de avisar** (Q-SC-2 a) queda descartado por Jev; si algún día se quiere, el sitio es el `__main__` con
  `sys.exit(1 if sin else 0)`, y los llamadores que usan `main()` como función no lo notarían.
