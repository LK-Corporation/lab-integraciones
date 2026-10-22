# ANTES: etapa del verificador, cerrar los huecos medidos del juez (14k, FIJADO el 22-oct-2026)

**Fijado.** Víctor aceptó el 22-oct las cinco recomendaciones Q-VE (tabla «Decisiones de Víctor», abajo). **La etapa no
empezaba hasta que se cerrara BU (14j)**, porque el verificador era su juez sellado. BU se cerró el 22-oct
(`RESULTADO-BU.md`, con la huella de este juez).

## Decisiones de Víctor (22-oct)

| Q | Decisión |
|---|---|
| Q-VE-1 | **Entran A y B:** MMI-12, MMI-19, Q-MS-9 y el contrato del canónico (Q-MI-V-9). D queda fuera, como límite declarado |
| Q-VE-2 | **La neutralidad de motor (C), fuera,** como límite declarado hasta el siguiente motor |
| Q-VE-3 | **Los resultados sellados no se rejuzgan.** Cada uno queda con la huella de su juez, y la etapa publica por corpus una tabla de qué cambiaría |
| Q-VE-4 | **Fable diseña los cambios a ciegas de los corpus de rejuicio; Jev decide las S-n nuevas.** Sin DeepSeek |
| Q-VE-5 | **Al cerrar, se prepara la publicación del verificador** en el repo público, con la guarda y el visto bueno de Víctor al diff |

Orden: ORU ✅ → ADT ✅ → modo sitio ✅ → Mirth ✅ → piloto del agente ✅ → BU ✅ → **verificador**.

## Por qué

Desde el 27-sep el verificador es el producto. Cuatro etapas (multi-tipo, modo sitio, Mirth y piloto) lo han usado como
referencia **sin tocarlo**. Eso las hizo comparables, pero cada una fue dejando preguntas «para la etapa del verificador»:

- **tres son huecos medidos:** el juez da `correcto` a algo que está mal, o se contradice, y hay un mutante o un mensaje real
  que lo demuestra;
- **el resto son preguntas** de contrato, de motor o de interpretación.

Esta etapa decide cada una: **o se cierra con su prueba, o pasa a límite declarado.** Ninguna queda como fleco.

## Punto de partida (leído el 22-oct)

- **El juez no ha cambiado desde `54d0eca`** (cierre del modo sitio). `git log 54d0eca..HEAD` sale vacío sobre sus ficheros
  de huella y sobre `mapeador_adt`, `almacen_adt`, `mapeador_oru`, `almacen_oru` y `estructuras_hl7`. La versión es la huella
  de esos ficheros (`mcp_verificador.py`, `_version`).
- **Suites al cierre de Mirth (MI4):**
  - `prueba_verificador` y `prueba_mcp_verificador`: TODO BIEN;
  - `prueba_adt` 27, `prueba_oru` 696, `prueba_multitipo` 705, `prueba_mutantes` 38 y `prueba_arnes` 11;
  - autopruebas: `mapeador_adt` 83, `almacen_adt` 17 y `almacen_oru` 345.
- **Preguntas que el MCP declara pendientes** (`prueba_mcp_verificador.py:601`): Q-AMB-10, Q-DV1, Q-MS-10 y Q-MS-9. Las
  Q-MI-V están en `RESULTADO-MIRTH.md` y en `diseno-mirth-fable.md` §11.2.
- **Corpus guardados para rejuzgar:**
  - las 263 entradas de A1: 216 bases de E2, 7 ejemplos del cap. 3 y 40 propias (`a1/`);
  - `mirth/mi2_lab.json`, `mirth/mi2_prevision.json`, `mirth/mi3.json` y `mirth/mi3_vivo.json`;
  - la muestra real, fuera de git (`privado/`).
  - La foto de regresión `/tmp/a1b` **no sobrevivió** a un reinicio (`RESULTADO-MIRTH.md`, MI4).

## Inventario: lo que llega a esta etapa

### A. Huecos medidos del juez (cambian veredictos)

| Pregunta | Qué pasa hoy | Medido en |
|---|---|---|
| **Q-MI-V-5 / MMI-12** | Con AA, una fila de éxito y `canonico_adt = null`, el veredicto es `correcto`. El juez no exige el canónico cuando el circuito dice haber escrito | Mirth MI3: 128 mordidos, **0 cazados** |
| **Q-MI-V-10 / MMI-19 / L-MI-14** | El almacén se relee solo por los identificadores del **canónico observado**. Un Encounter escrito sin visita en el canónico no se relee. Al circuito IRIS le pasa igual | Mirth MI3: 14 mordidos, **0 cazados** |
| **Q-MS-9 / VER-MS-1** | Con PID-8 fuera de la 0001, el acuse aplica la versión **asumida** (`acuse_referencia.py:502`) y el mapeador la **escrita** (`mapeador_referencia.py:480`, `mapeador_adt.py:546`). El acuse tolera el AA (S22), pero el mapeador lo da por «valor imposible aceptado»: con AA el circuito no puede acertar. Hoy se salva porque el circuito contesta AE 103 y S26 lo acepta | Modo sitio MS2: 3 mensajes reales |

### B. Contrato

- **Q-MI-V-9.** El contrato del canónico ADT no documenta su representación (DV-MI-2..4: códigos ya mapeados, `GivenName`,
  visita vacía con PV1-2 = N). Un circuito hecho solo con el contrato público difiere en 128 de 128 aceptados sin cambiar un
  ACK ni un recurso. No cambia veredictos: es documentación del contrato público y del MCP.

### C. Neutralidad de motor (salen de Mirth)

- **Q-MI-V-1 y Q-MI-V-4.** El vocabulario del log (L01-L16) es texto de IRIS. Con Mirth, el lector lo sintetiza, y funcionó:
  0 indeterminados en 1.497 casos en vivo. Pero es una traducción. ¿Se acepta una fila estructurada como terminal? ¿Se adjunta
  el log nativo aparte?
- **Q-MI-V-2.** L08 y L10 no existen en Mirth; «hubo conexión y expiró» se expresa como L07.
- **Q-MI-V-3.** L09 no es observable en Mirth. L-MT11 ya lo declara indistinguible: no cambia nada.
- **Q-MI-V-8.** L21 presupone reintentos y Mirth no reintenta. Según el diseño de Mirth, L21 sigue valiendo (ventana de una
  petición).

### D. Interpretación (sin caso real ni mutante que lo pida)

- **Q-MI-V-6.** El OperationOutcome de un 400/422 sí viaja en la evidencia de Mirth. ¿Se interpreta frente a ERR-3 (S21)?
  Hoy L3 y L22 dicen que no.
- **Q-MI-V-7.** Mirth devuelve MSA-2 íntegro y IRIS lo recorta a 199 (L-MS-3). AMB-7 acepta los dos.
- **Q-DV1.** Un código HTTP fuera de la tabla de P7. Hoy: 2xx es éxito y el resto AR 207 (ambigua). Alternativa:
  indeterminado.
- **Q-AMB-10.** MSH-18 declara un juego que no es latin-1, UTF-8 ni ASCII, y llegan bytes `<0xNN>`. Hoy se leen como latin-1
  (S9). Alternativa: decodificar con el juego declarado.
- **Q-MS-10 / L-MS-12.** La guía del sitio amplía la tabla 0004 con una clase propia. Ningún mensaje real la trae.

## Condiciones que no se negocian

1. **BU cerrado antes del primer cambio del juez.** Cumplido el 22-oct.
2. **Lo ya medido no se rejuzga en silencio.** Cada resultado sellado (A1, ADT, modo sitio, Mirth, piloto y BU) cita la huella
   del juez con que se midió. La versión nueva lleva su propia huella, y la etapa mide aparte cuántos veredictos de los corpus
   guardados cambia, con la previsión escrita antes.
3. **Cada cambio nace de una prueba que falla con el juez de hoy** (control negativo) y pasa con el nuevo.
4. **Manda el estándar** (HL7 v2.5 y FHIR R4). Lo que el estándar no decide va a Jev como S-n, con el estado neutro.
5. **Los circuitos no se tocan:** USER, LABADT, LABORU, LABMULTI, el canal Mirth y las cajas quedan como están.

## Eslabón débil (VE-pre, antes de diseñar; solo lectura)

Lo que puede tumbar la etapa es **MMI-12**. Exigir el canónico cuando hay AA y una fila de éxito puede dar falsas alarmas
donde el canónico falta con razón: puntos de entrada de solo acuse (L-MT1) o evidencias anteriores al campo. También **Q-MS-9**
cambia veredictos en tráfico real si se unifica la versión.

| Sonda | Pregunta |
|---|---|
| E-VE-1 | En los corpus guardados, ¿cuántas evidencias tienen AA, fila de éxito y canónico nulo, por punto de entrada? Las de un punto sin canónico son legítimas |
| E-VE-2 | ¿Cuántos mensajes de los corpus tocan Q-MS-9 (PID-8 fuera de la 0001 con versión asumida distinta de la escrita), y qué veredicto da cada lectura? |
| E-VE-3 | ¿Están guardadas las evidencias de MMI-12 y MMI-19 de forma que se puedan rejuzgar sin levantar Mirth? |
| E-VE-4 | ¿Se puede rehacer la línea base de regresión desde lo guardado, ahora que `/tmp/a1b` se perdió? |

**Reglas de parada:**
- Si MMI-12 no se puede cerrar sin falsas alarmas en evidencias legítimas, y ninguna regla del estándar o del contrato las
  separa, MMI-12 **pasa a límite declarado** y la etapa sigue con lo demás. No se fuerza.
- **Sin línea base (E-VE-4), no se cambia nada.**

## Preguntas de alcance para Víctor (Q-VE), con recomendación (contestadas: ver arriba)

| Q | Recomendación | Alternativa |
|---|---|---|
| Q-VE-1 qué entra | **A y B:** los tres huecos medidos (MMI-12, MMI-19 y Q-MS-9) y el contrato del canónico (Q-MI-V-9). Cada uno tiene una medida que lo demuestra, y cierran deuda del juez | Añadir D (Q-MI-V-6/7, Q-DV1, Q-AMB-10): más juez, pero sin un caso real ni un mutante que lo pida |
| Q-VE-2 la neutralidad de motor (C) | **Fuera, como límite declarado, hasta el siguiente motor.** La traducción del lector funciona (0 indeterminados en 1.497), y cambiar el esquema de evidencia toca a todos los lectores y al arnés | Entrar ya con la fila estructurada (Q-MI-V-1), pensando en la familia de motores |
| Q-VE-3 los resultados sellados | **No se rejuzgan.** Cada uno queda con la huella de su juez, y la etapa publica por corpus una tabla de qué cambiaría con el juez nuevo | Rejuzgar todo y reescribir los RESULTADO con la versión nueva |
| Q-VE-4 reparto | **Fable diseña los cambios** a ciegas de los corpus de rejuicio, desde el estándar, el contrato, las S-n y las medidas de MI3 y MS2. **Jev** decide las S-n nuevas. Sin DeepSeek (le quedan 0,08 USD) | Recargar DeepSeek para un oráculo ciego de los cambios |
| Q-VE-5 publicar | **Al cerrar, preparar la publicación del verificador** en el repo público, donde hoy no está, con la guarda y tu visto bueno al diff | Seguir sin publicarlo |

## Fases (propuesta; las reglas de parada se concretan en el diseño)

| Fase | Qué |
|---|---|
| VE-pre | Eslabón débil y línea base (E-VE-1..4). Solo lectura |
| VE0 | Diseño de Fable, y las Q-VE de diseño a Jev |
| VE1 | Implementación: cada cambio con la prueba que falla antes de hacerlo |
| VE2 | Rejuicio de los corpus guardados, con la previsión escrita antes |
| VE3 | Cierre: el MCP declara la versión, las S-n, los L-VE y lo que pasa a límite; suites; guarda LIMPIO; `RESULTADO-ETAPA-VERIFICADOR.md` |

## Hecho cuando

- Cada pregunta que entra queda cerrada con su prueba, o pasa a límite declarado (L-VE-n) con su motivo.
- MMI-12 y MMI-19 se cazan, y los 15 mutantes que MI3 ya cazaba siguen al 100 % con colateral 0.
- El rejuicio de los corpus guardados da 0 fuera de previsto, y LABADT y el canal Mirth siguen saliendo con la misma categoría
  entre sí.
- Las suites siguen en verde, salvo las pruebas que la etapa cambia a propósito, cada una declarada.
- `info_verificador.preguntas_pendientes` solo lleva lo que se decidió dejar abierto.

## Tope

**Dos sesiones de trabajo** (propuesta). Fable: un diseño. DeepSeek: 0 USD.

## Fuera de la etapa

- **Las deudas de los circuitos** (CIR-ADT-7/8, CIR-MS-3/4 y CIR-MT1/4). Son del circuito, no del juez, y además son casos R
  del piloto y de BU.
- **L-MI-15** (MMI-11 y los mutantes del lector), que es del lector de Mirth.
- **Los L-n que marcan la frontera de la v1** (L-ADT-1, L-ORU-2 y los demás de alcance): no son huecos, son alcance declarado.
