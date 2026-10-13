# ANTES: piloto del agente que se apoya en el verificador (14h, FIJADO el 12-oct-2026)

**Fijado.** Víctor contestó Q-AG-1..7 el 12-oct y aceptó las siete recomendaciones:

| Q | Decisión |
|---|---|
| Q-AG-1 | Cuentan **H + R** (fallos reales); **M** solo como control y calibración |
| Q-AG-2 | **Localizar** (top-3) **y parchear**, puntuados por separado; el parche lo juzga el verificador en la caja |
| Q-AG-3 | **Subagente de Claude** en una carpeta cerrada; un segundo brazo con DeepSeek si el saldo alcanza |
| Q-AG-4 | **Referencia sin modelo fuerte**, construida, controlada y congelada antes que el agente |
| Q-AG-5 | El agente ve **el veredicto, la fuente actual y el MCP**; ni git, ni diffs, ni huellas, ni la versión buena |
| Q-AG-6 | **Fable diseña** a ciegas de los arreglos de H; Jev decide las Q del diseño |
| Q-AG-7 | **Tres sesiones**; Fable un diseño; el agente ≤ 70 casos × 2 réplicas; DeepSeek ≤ 2 USD |

Orden acordado con Víctor el 4-oct: ORU ✅ → familia ADT ✅ → modo sitio ✅ → Mirth ✅ → **piloto del agente**.

## La pregunta

El verificador ya dice **qué** está mal en una integración: el veredicto, el hallazgo, el campo HL7 y la cita del estándar. No
dice **dónde está el fallo en el código del circuito** ni **cómo se arregla**. El piloto pregunta:

> Dado un circuito que falla y el veredicto del verificador, ¿un agente con modelo **localiza la causa en el código** y
> **propone un arreglo que el propio verificador da por bueno**, mejor que una búsqueda sin modelo?

El verificador es el juez y el agente es el diagnosticador; el agente no juzga nada. El arreglo también lo puntúa el
verificador: debe dar `correcto` en los casos que fallaban y no romper ninguno de los que pasaban.

## Por qué así (lo que ya está medido y obliga al diseño)

- **Fase 12 (22-sep): «el agente funciona y no hace falta».** Un script sin modelo batió al agente de triaje (+0,873 frente a
  +0,629), porque el banco estaba hecho con operadores de mutación y **cada caso dejaba una firma mecánica**. De ahí sale la
  regla: el adversario mecánico fuerte se construye **antes** que el agente (memoria `corpus-mutaciones-favorece-lo-mecanico`).
- **Un mutante de una línea también tiene firma.** El hallazgo nombra el campo («fidelidad/guardado PID-8») y una búsqueda
  del campo en el código encuentra la línea. Con solo mutantes, lo más probable es que gane la búsqueda. Por eso hace falta
  además un corpus de **fallos reales**, que nadie diseñó para ser encontrados.
- **Fase 13 (aparcada el 27-sep):** la pregunta «¿aporta la IA?» sin un corpus sin firma mecánica no tiene respuesta. Este
  piloto es más estrecho: no pregunta si el agente detecta fallos, sino si localiza y arregla los que el verificador ya
  detectó.

## Punto de partida (medido el 12-oct)

**Circuitos con fuente versionada y juzgados por el verificador:**

| Circuito | Motor | Lenguaje | Puerto |
|---|---|---|---|
| LABADT | IRIS | ObjectScript | 2586 |
| LABORU | IRIS | ObjectScript | 2585 |
| LABMULTI | IRIS | ObjectScript | 2580-2584 |
| Pieza común `comun/fuente` | IRIS | ObjectScript | — |
| Canal Mirth `adt_fhir` | Mirth | JavaScript | 2600 |
| EL CONGELADO (USER) | IRIS | ObjectScript | 2575 |

**Corpus posibles:**

| Corpus | Qué es | Cuántos | Verdad de referencia |
|---|---|---|---|
| **M**, mutantes | Los ya medidos: `mutacion.py` (circuito congelado, en LABMUT), A5 de LABADT (`labadt/adt.py`, 12), MS3 de la pieza común (`comun/ms3.py`, 13) y MI3 de Mirth (`mirth/mi3.py`, 18) | ~50 | El mutante (fichero y línea) |
| **H**, fallos históricos reales | Fallos de los circuitos hallados por la medida y arreglados en un commit: P2c de LABADT (`00e3d6f`), CIR-ORU-1/2 (`fb18ef8`), CIR-ORU-4 (`83cd02f`), CIR-ORU-5/6 (`f7d42d6`), ORC suelto (`eda3b5f`), `ImportFromString` con texto no ASCII (`22cf35d`), el nulo `""` del canal Mirth (`af217b9`) | ~9 | El diff del arreglo. El caso se construye revirtiéndolo |
| **R**, fallos vivos sin arreglar | Los 7 fallos reales del circuito congelado (`CONOCIDOS-ANTES-DEL-SELLO.md`): `MSA\|CE`, no desescapa, 4xx → 102, MAXREP = 10, PV1 antes de PID → 101, SINID, ERR-3 = 104 | 7 | No hay diff. Vale el arreglo que el verificador da por bueno sin colateral, y la localización se adjudica después |

**Lo que ya hay para el agente:**
- el MCP del verificador (`verificar_caso`, `ficha_experto`, `acuse_esperado`, `comparar_canonico`, `consultar_tabla`);
- la fuente de cada circuito;
- un arnés que carga un circuito con un cambio y lo mide: LABMUT para IRIS (`mutacion.py`) y `mi3.py` para Mirth.

**Presupuesto de modelos:** el saldo de DeepSeek es 2,09 USD. Fable y Jev se usan como hasta ahora.

## Preguntas de alcance para Víctor (Q-AG), con recomendación (contestadas: ver arriba)

| Q | Recomendación | Alternativa |
|---|---|---|
| Q-AG-1 corpus | **H + R como corpus que cuenta** (fallos reales, sin firma de diseño), y **M solo como control y calibración**: si el agente no localiza ni los mutantes, el resto no se mide | Solo M: más barato y grande, pero lo más probable es que gane la búsqueda y no se aprenda nada nuevo |
| Q-AG-2 qué se le pide | **Localizar** (fichero y línea, top-3) **y proponer un parche**, puntuados por separado. El parche lo aplica el arnés en la caja (LABMUT o el contenedor de Mirth) y lo juzga el verificador | Solo localizar: más barato; no mide si el diagnóstico sirve para arreglar |
| Q-AG-3 qué modelo hace de agente | **Un subagente de Claude** en una carpeta cerrada (como Fable en los diseños), con solo el MCP del verificador, la fuente del circuito y la evidencia del caso. Un segundo brazo con DeepSeek si el saldo lo permite | DeepSeek solo (barato e independiente del que diseña, pero el saldo es de 2,09 USD); el qwen local (medido: pierde campos al copiar la evidencia) |
| Q-AG-4 la referencia sin modelo | **Construida y congelada antes que el agente:** del hallazgo (campo, subtipo) a una búsqueda ordenada en la fuente (nombre del campo, índices, propiedades del canónico), más un «parche» mecánico de plantilla donde exista. Con tres controles: clave barajada, columnas que lee y casos limpios | Una búsqueda simple por texto del campo (más débil: un adversario débil solo puede dar un falso positivo a favor del agente) |
| Q-AG-5 qué ve el agente | **El veredicto y los hallazgos del caso, la fuente actual del circuito y el MCP.** Ni el historial de git, ni los diffs, ni las huellas, ni la versión buena | Darle también la versión anterior (convierte la tarea en un diff: no mide diagnóstico) |
| Q-AG-6 quién diseña | **Fable diseña** el piloto: tareas, métrica, regla de parada y la referencia sin modelo, a ciegas de los arreglos reales de H. Jev decide las Q del diseño | Diseñarlo yo: más rápido, pero yo conozco los arreglos de H |
| Q-AG-7 tope | **Tres sesiones** (como Mirth y el modo sitio). Modelos: un diseño de Fable, el agente en ≤ 70 casos × 2 réplicas, y DeepSeek ≤ 2 USD | Una sesión con solo M |

## Fases (propuesta; las reglas de parada se concretan en el diseño)

| Fase | Qué |
|---|---|
| AG-pre | **Eslabón débil, antes de diseñar:** un caso de H de punta a punta. Se revierte el arreglo en la caja, el verificador falla, un agente mínimo recibe la evidencia y propone un parche, el arnés lo aplica y el verificador vuelve a juzgar. ¿Cabe la tarea en un contexto? ¿El arnés aplica un parche ajeno sin tocar git? |
| AG0 | Diseño de Fable, con las Q a Jev. **Regla de parada escrita fuera y antes** |
| AG1 | Corpus M + H + R sellado (la clave fuera de la caja del agente), y **la referencia sin modelo construida, controlada y congelada** |
| AG2 | Las tareas por la referencia y por el agente (dos réplicas), en la caja; parches aplicados y juzgados por el verificador |
| AG3 | Análisis según lo preinscrito: localización (top-1/top-3), arreglo aceptado (`correcto` en lo que fallaba y 0 colateral en la regresión del circuito), coste. **Las dos frases juntas: «funciona» y «hace falta»** |
| AG4 | Cierre: circuitos y arneses como estaban, guarda LIMPIO |

## Hecho cuando

- Cada caso de H y R tiene un resultado de la referencia y del agente, puntuado por el verificador y con la regla preinscrita.
- Se reportan las dos frases, «el agente funciona» y «el agente hace o no hace falta», con su intervalo, y el «no aporta» es un
  resultado válido.
- Cada parche aceptado tiene su control negativo: sin el parche, el caso sigue fallando.
- Nada del agente toca git, los circuitos de producción del laboratorio ni EL CONGELADO. Todo pasa en la caja (LABMUT o un
  contenedor Mirth efímero).

## Tope

Tres sesiones (Q-AG-7). Fable: un diseño. El agente: ≤ 70 casos × 2 réplicas. DeepSeek: ≤ 2 USD.

## Fuera de la etapa

- Que el agente decida veredictos: eso lo hace el verificador.
- Arreglar el verificador: Q-MS-9/10 y Q-MI-V-1..10 son de su etapa.
- Circuitos que no estén en git.
- Aplicar parches en producción.
- La Fase 13 completa (detección de tipos nuevos).
