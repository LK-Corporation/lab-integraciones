# Estado: dos decisiones de la etapa 41, la Observation de PD1-7 en un ORU (8-nov-2026)

Redactado el 8-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 41 quiere que el juez empareje con su campo la Observation que la guía crea desde PD1-7 en un ORU, como la 40 hizo en
ADT. El diseño a ciegas (`po/diseno-po-fable.md`) la aparta antes de casar las Observation de los OBX y la juzga con lo de la 40.
Deja dos decisiones abiertas.

## Hechos comunes

- **La guía** crea la misma Observation en ADT_A01 (`MSG_ADT_A01.csv:19`) y en ORU_R01 (`MSG_ORU_R01.csv:17`), con una sola
  referencia: su `subject` al Patient. En ORU la fila está dentro de PATIENT, no de ORDER_OBSERVATION.
- **Ninguna de las 4.424 evidencias de ORU guardadas lleva PD1-7 valorado,** ni ninguna de ADT. Ninguna opción cambia el rejuicio,
  ni las cifras del estudio, ni ningún caso de las bases.
- **La etapa cambia la huella del juez de todos modos** (`conversion.py` y `mcp_verificador.py`): las bases se rehacen con
  cualquiera de las opciones.

## Q-PO-1. La Observation de PD1-7 referida desde `DiagnosticReport.result`

**Hecho medido con el juez de hoy:** si el DiagnosticReport de un OBR lleva en `result` la Observation de PD1-7, el juez cuenta
`referencia_rota` del OBR («no es una Observation de su OBR»), además de la Observation como inventada. Con el juez nuevo la
Observation pasa a ser la de PD1-7; la pregunta es qué pasa con la referencia.

- **(a) Sigue siendo `referencia_rota` del OBR, que cuenta, como hoy.**
  - A favor: la hoja de ORU solo pone en `result` las Observation de los OBX de su OBR (`MSG_ORU_R01.csv:67-73`), y la fila de PD1-7
    solo da `subject`; el perfil de ORU del juez dice «exactamente las Observation de los OBX de su OBR»; en FHIR R4, `result` son
    las Observation que forman parte del informe.
  - En contra: la Observation existe y es la que la guía crea; el conversor solo la cuelga del informe, sin perder ni inventar el
    dato, y eso cuenta como un fallo de fidelidad.
  - Toca: nada del código del juez para ese caso; el texto de L-CV-18 y una prueba que fija lo que ya hace.
- **(b) Una nota de convención, que no cuenta, en vez de la referencia rota.**
  - A favor: no cuenta como fallo algo que no pierde ni inventa datos.
  - En contra: añade una forma nueva a la conducta (una nota de OBR que entra), y con ella una regla más en el clasificador del
    rejuicio y un mutante más; la guía no pone esa Observation en `result`.
  - Toca: el juicio del informe en `conversion.py`, L-CV-18, las pruebas y el clasificador.

## Q-PO-2. Las citas de los hallazgos de PD1-7

**Hecho:** hoy los hallazgos de PD1-7 citan `C["PD1-7"]`, que lleva la hoja de ADT (`[G MSG_ADT_A01.csv:19]`). En un ORU esa cita
es la de otra hoja.

- **(a) Una lista: `C["PD1-7"]` gana también la hoja de ORU.**
  - A favor: las dos filas son ciertas para esa Observation; un solo cambio.
  - En contra: los hallazgos de PD1-7 de un ADT ganan una cita de la hoja de ORU, así que un ADT ya no sale igual byte a byte
    (solo en las citas; ninguna evidencia lo trae); cambia la huella de `C` que fija P-MD-25 (d).
- **(b) Por familia:** `C["PD1-7"]` queda como está y los hallazgos de un ORU citan la misma lista con la hoja de ORU en el sitio de
  la de ADT.
  - A favor: un ADT sale igual byte a byte, hasta las citas; cada hallazgo cita la fila que lo crea; la huella de `C` no cambia.
  - En contra: más código (las citas pasan como parámetro a tres funciones del juez, una de ellas la del sujeto, que usan otras
    partes) y un mutante más que probar.
