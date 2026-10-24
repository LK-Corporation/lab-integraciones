> *Copia pública: se quitaron las alusiones al trabajo del autor y la cola de lo que solo él decide. El resto es el original del laboratorio.*

# ANTES: etapa de conversores, el verificador juzga conversores HL7 v2 → FHIR de código abierto (14l, FIJADO el 23-oct-2026)

**Fijado en autónomo.** El 23-oct Víctor pidió preparar este ANTES y seguir sin preguntarle. Las Q-CV de alcance se toman con
la recomendación (tabla de abajo) y quedan revisables por él. Las de diseño van a Jev en CV0. El eslabón débil (CV-pre) ya se
midió: `RESULTADO-CV-PRE.md`.

## Por qué

El verificador solo ha juzgado circuitos hechos por el laboratorio: USER, LABADT, LABORU, LABMULTI y el canal Mirth. Es lo
que deja abierto `RESULTADO-ETAPA-VERIFICADOR.md`: no se sabe si encuentra algo que importe fuera de casa. El camino son terceros públicos: conversores HL7 v2 → FHIR de código
abierto que usa gente de verdad, juzgados contra la guía oficial v2-to-FHIR de HL7.

## La pregunta (fija)

> ¿Encuentra el verificador, en conversores HL7 v2 → FHIR de código abierto que el laboratorio no ha construido,
> discrepancias con la guía v2-to-FHIR o con FHIR R4 que se sostengan con cita, que cambien el significado del dato y que el
> proyecto no tenga ya declaradas?

## Punto de partida (medido el 23-oct)

| Proyecto | Licencia | Último push | Última versión | Cobertura HL7 v2 → FHIR | Commit leído |
|---|---|---|---|---|---|
| `microsoft/FHIR-Converter` | MIT | 23-sep-2026 | v7.0 (3-jun-2024) | 57 plantillas Liquid, «basadas en v2.8»: ADT (26 eventos), ORU_R01, SIU, MDM, VXU… | `70fd328` |
| `LinuxForHealth/hl7v2-fhir-converter` | Apache-2.0 | 11-feb-2026 | v1.1.1 (18-sep-2024) | 25 plantillas YAML, Java: ADT (A01, A02, A03, A04, A08, A28, A31, A34, A40), ORU_R01, MDM, VXU… | `2cb72c2` |
| `GoogleCloudPlatform/healthcare-data-harmonization` | Apache-2.0 | 13-oct-2026 | — | `mappings/hl7v2_fhir_r4` (Whistle) | — |
| `HL7/v2-to-fhir` (la guía) | Apache-2.0 | 23-sep-2026 | — | Hojas CSV de mensajes (13), segmentos, tipos de datos y vocabularios; muestras: 1 mensaje (MDM_T02) y 2 bundles | `873b331` |

- **Pruebas publicadas:**
  - Microsoft trae 139 mensajes de muestra (`data/SampleData/Hl7v2`) y salidas esperadas por tipo de mensaje en sus pruebas
    funcionales;
  - LinuxForHealth, 58 clases de prueba y 3 mensajes de muestra.
- **El verificador:** juez `b9788fab` en el laboratorio, `a2ee87fd` en la copia pública, servidor 1.1. Los puntos con
  mapeador son `adt_a01`, `adt_fhir` (8 eventos ADT) y `oru_fhir`. Sus proyecciones FHIR:
  - `proyeccion_fhir_adt`, 21 filas: Patient y Encounter;
  - `proyeccion_fhir_oru`, 30 filas: Observation y DiagnosticReport.
- **Corpus públicos y sintéticos que ya tiene el laboratorio**, en el repo público: las 263 entradas de A1, las 216 bases de
  E2 y las 40 bases ORU (`bases_oru.py`). Todo en v2.5.

## Condiciones que no se negocian

1. **Solo terceros públicos:** ningún sistema, dato ni material que no lo sea.
2. **El código de terceros corre en una caja aislada:** sin red, sin privilegios y en una versión fijada con su huella. Nunca
   en el circuito, en IRIS ni en el repo.
3. **Manda el estándar:**
   - HL7 v2 en la versión que declara el mensaje, FHIR R4 y la guía v2-to-FHIR en el commit leído;
   - una diferencia que el estándar permite es **convención** y no cuenta;
   - las S-n del laboratorio no cuentan contra un tercero.
4. **Cada discrepancia que cuente lleva su cita** y se contrasta con las pruebas y los issues del proyecto. Las ya declaradas
   se cuentan aparte, y sirven de control positivo: el verificador debe verlas.
5. **El juez del laboratorio no cambia para ganar casos.** Lo nuevo (lector, punto de entrada, perfil «guía») se añade con su
   prueba en rojo antes, y los resultados sellados conservan la huella de su juez.
6. **Nada sale fuera sin el visto bueno de Víctor:** ni se publica ni se reporta a los proyectos.

## Eslabón débil (CV-pre, solo lectura): hecho, ver `RESULTADO-CV-PRE.md`

| Sonda | Pregunta |
|---|---|
| E-CV-1 | Por cada elemento que proyecta el verificador, ¿lo saca la guía del mismo campo? ¿Y el valor esperado que el juez da a ese elemento se apoya en la guía? |
| E-CV-2 | ¿Qué mensajes de muestra públicos hay, de qué tipos y versiones? ¿Cuántos lee el verificador, y qué acuse espera? |
| E-CV-3 | ¿Corre cada conversor sin red en una caja, en una versión fijada? ¿Qué devuelve? **Pasa al principio de CV1**, porque exige ejecutar código de terceros |
| E-CV-4 | ¿Publican los conversores sus salidas esperadas o sus pruebas, para contrastar una discrepancia sin depender de nuestro juicio? |

**Reglas de parada:**
- Si en E-CV-1 menos de la mitad de los elementos proyectados coinciden con la guía, la etapa no sigue con el juez tal cual.
  CV0 diseña primero un perfil «guía», y si no cabe en el tope, se para y se declara.
  - **Medido: coinciden todos** (ADT 20 de 20, ORU 21 de 21).
  - **El hueco está en el valor esperado de ADT**: ninguna de sus 70 filas de contrato cita la guía. Por eso el perfil
    «guía» entra en CV0.
- **Si ningún conversor corre aislado (E-CV-3, al empezar CV1), la etapa para.**

## Preguntas de alcance (Q-CV), tomadas en autónomo con la recomendación

| Q | Decisión | Alternativa |
|---|---|---|
| Q-CV-1 qué conversores | **Microsoft y LinuxForHealth.** Google (Whistle) solo si los dos corren y queda tope | Los tres desde el principio |
| Q-CV-2 qué mensajes | **ADT de los 8 eventos de `adt_fhir` y ORU^R01.** Corpus principal: las bases públicas del laboratorio (A1, E2 y ORU), en v2.5 y con su esperado conocido. Secundario: las muestras de cada conversor que el juez acepta | Añadir SIU, MDM y VXU, que el juez hoy solo acusa, sin fidelidad |
| Q-CV-3 contra qué se juzga | **Un perfil «guía» nuevo,** que toma el valor esperado de los mapas de tipos de datos y vocabularios de la guía. En ORU ya cita el mapeo oficial `[M]` en 24 de 30 filas. Las S-n del laboratorio no cuentan | Juzgar con el perfil del laboratorio y contar solo lo que contradice FHIR R4 |
| Q-CV-4 reparto | **Fable diseña a ciegas** el punto de entrada de solo transformación, el lector de la salida de un conversor y el perfil «guía», sin ver lo que devuelven los conversores. **Jev** decide las Q de diseño y las S-n nuevas. Sin DeepSeek | — |
| Q-CV-5 qué se hace con lo que salga | **Un `RESULTADO` privado.** Publicarlo o abrir issues en los proyectos, solo con el visto bueno de Víctor | Abrir issues directamente |

## Fases

| Fase | Qué |
|---|---|
| CV-pre | Eslabón débil (E-CV-1, 2 y 4). Solo lectura. **Hecho** |
| CV0 | Diseño de Fable a ciegas: punto de entrada de solo transformación, lector de la salida y perfil «guía». Las Q de diseño, a Jev |
| CV1 | E-CV-3 primero: cada conversor en su caja, sin red, en versión fijada. Después, el lector y el perfil, con sus pruebas en rojo antes |
| CV2 | La previsión sellada por conversor y familia, antes de juzgar. Después, se juzga el corpus |
| CV3 | El contraste: cada discrepancia con su cita, frente a las pruebas e issues del proyecto. Clases: nueva, ya declarada o convención |
| CV4 | Cierre: `RESULTADO-CONVERSORES.md` con la frase fija, el MCP con lo nuevo declarado, las suites y la guarda en LIMPIO |

## Hecho cuando

- E-CV-1..4 contestadas.
- Cada conversor elegido juzgado sobre el mismo corpus, con la previsión sellada antes.
- Cada discrepancia que cuenta lleva su cita, su contraste con las pruebas e issues del proyecto y su clase (nueva, ya
  declarada o convención), y se reproduce con un mensaje público.
- Las suites del verificador siguen en verde. Lo nuevo tiene sus pruebas, y el juez de los resultados sellados no cambia.
- `RESULTADO-CONVERSORES.md` con la frase fija: «El verificador encuentra N discrepancias nuevas y confirmadas en K de 2
  conversores, sobre M mensajes públicos; además ve D de las ya declaradas, y C diferencias son convención».

## Tope

**Cuatro semanas de calendario, hasta el 20-nov-2026, y no más de cuatro sesiones de trabajo.** Fable hace un diseño y Jev
decide las Q de diseño. Gasto externo: 0 USD.

## Regla de pieza de portfolio (escrita antes de medir)

**Si al llegar al tope no hay al menos una discrepancia nueva y confirmada en un conversor de terceros**, el verificador se
declara **pieza de portfolio**. Confirmada quiere decir que tiene cita, cambia el significado del dato, el proyecto no la
tiene declarada y se reproduce con un mensaje público.

Si es pieza de portfolio:
- no se abren más etapas de producto sobre él;
- queda el repo público como está;
- la etapa se cierra con su `RESULTADO` y la frase.

Vale igual si la etapa para por una regla de parada sin alternativa que quepa en el tope.

**Si hay al menos una**, la etapa concluye que el verificador encuentra algo fuera del laboratorio. Lo siguiente (publicarlo,
abrir issues, otra etapa) lo decide Víctor.

## Fuera de la etapa

- Todo sistema, dato o material que no sea público.
- La conversión inversa, FHIR → v2.
- Los tipos que el juez solo acusa (SIU, MDM, VXU, ORM…).
- El rendimiento de los conversores.
- El motor propio con los patrones de Ensemble, que es otra línea, de otra sesión.
