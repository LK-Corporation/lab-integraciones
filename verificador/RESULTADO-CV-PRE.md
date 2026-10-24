# CV-pre: el eslabón débil de la etapa de conversores (23-oct-2026)

**La etapa sigue.** Los elementos que proyecta el verificador coinciden con la guía v2-to-FHIR en todos los casos, así que la
regla de parada de E-CV-1 no salta. El hueco es otro y se conocía a medias: en ADT, el valor esperado es convención del
laboratorio. CV0 tiene que diseñar el perfil «guía».

Las muestras públicas de los conversores sirven poco como corpus. El juez solo espera AA en 10 de 65, y el corpus principal
serán las bases públicas del laboratorio (Q-CV-2). E-CV-3 pasa al principio de CV1, porque exige ejecutar código de terceros.

Programas: `cv/cv_pre.py` (E-CV-1) y `cv/cv_pre_e2.py` (E-CV-2), con su salida en `cv/CV-PRE-E1.json` y `cv/CV-PRE-E2.json`.
Las hojas de la guía, del commit `873b331` de `HL7/v2-to-fhir`, están en `cv/guia/`. Todo en solo lectura: el juez no cambia.

## E-CV-1: ¿lo que proyecta el juez es lo que mapea la guía?

**Elemento a elemento, sí.** Por cada fila de la proyección se mira si la guía saca ese elemento FHIR del mismo campo v2. Las
hojas usadas son PID[Patient], PV1[Encounter], OBX[Observation] y OBR[DiagnosticReport].

| Familia | Filas | Alineadas | Referencias (`subject`) | Sin campo (constantes) | Otro campo / sin mapeo |
|---|---|---|---|---|---|
| ADT (Patient, Encounter) | 21 | **20 de 20** | 1 | 0 | 0 |
| ORU (Observation, DiagnosticReport) | 30 | **21 de 21** | 2 | 7 | 0 |

- Una «referencia» es `subject`: la guía la resuelve en la hoja del mensaje, no en la del segmento.
- La guía también saca `Encounter.status` de PV1-2, si PV1-45 no viene, como el juez.

**Del valor esperado, no.** Es lo que de verdad decide si una diferencia con un conversor es un fallo o una convención.

| Familia | De dónde sale el valor esperado |
|---|---|
| ADT | De las 70 filas del contrato del canónico que salen de esos campos, **ninguna cita la guía**. 25 son decisiones del laboratorio (S-n, D-ADT, DV-MI, AMB) y 45 no llevan cita |
| ORU | **24 de 30 filas citan el mapeo oficial `[M]`**, los ConceptMap del paquete de la guía. Las otras 6 son decisiones del laboratorio, como `[D-ORU-1]`, el identifier propio de cada Observation |

**Qué quiere decir:**
- **ORU se puede juzgar casi tal cual.** Hay que apartar las 6 filas de convención.
- **ADT necesita el perfil «guía».** Que una fila no tenga cita no quiere decir que contradiga la guía; quiere decir que nadie la
  ha cotejado. CV0 tiene que cotejar cada valor con los mapas que da la guía:
  - **tipos de datos:** CX → Identifier, XPN → HumanName, XAD → Address, XTN → ContactPoint, PL → location y
    XCN → Practitioner;
  - **vocabularios:** AdministrativeSex, MaritalStatus, PatientClass → EncounterClass y EncounterStatus, AdmissionType,
    HospitalService y DischargeDisposition.

## E-CV-2: las muestras públicas de los conversores

**Muestras leídas:**
- **Microsoft, 62 ficheros:** las ADT, ORU, LAB-ORU y LRI de `data/SampleData/Hl7v2`, en el commit `70fd328`;
- **LinuxForHealth, 3 ficheros** (`src/test/resources`, `2cb72c2`).

En total, 65 mensajes, uno por fichero. Antes de juzgar, los saltos de línea se normalizan a CR y se quita el BOM, y cada
mensaje va a su punto (ADT a `adt_fhir`, ORU a `oru_fhir`). **El juez lee los 65 sin error.**

| | Mensajes |
|---|---|
| Versión MSH-12 | 2.8: 52 · 2.3: 4 · 2.5.1: 3 · 2.6: 3 · 2.5: 2 · 2.4: 1 |
| Acuse que espera el juez | AA 10 (7 ADT, 3 ORU) · CA 3 · AE 2 · AR 48 · sin acuse 2 |
| ERR-3 de los AR y AE | 201 evento no soportado: 36 · 200 tipo de mensaje no soportado: 10 · 203 versión no soportada: 4 · 101: 2 |

- **201:** 36 son eventos que `adt_fhir` no cubre (A05, A06, A07, A09, A10, A14…). Fuera del alcance de la etapa (Q-CV-2).
- **200, el hallazgo inesperado.** Las 10 muestras de Microsoft de A04, A08, A11, A13 y A31, que sí son eventos de
  `adt_fhir`, escriben en MSH-9.3 la estructura `ADT_A04`, `ADT_A08`, `ADT_A11`, `ADT_A13` o `ADT_A31`.
  - En la tabla 0354 de v2.5, esos eventos usan `ADT_A01`, `ADT_A09` o `ADT_A05`, y el juez lo marca en MSH-9.3.
  - Las muestras declaran v2.8. **Antes de contarlo como discrepancia hay que cotejarlo con la 0354 de v2.8**, que el
    laboratorio no tiene. Es una pregunta para CV0, y es de las muestras, no de la conversión.
- **203:** las 4 muestras en v2.3. El juez no las admite en `adt_fhir`.

**Consecuencia:** como corpus para juzgar la conversión, las muestras de los conversores dan poco: 10 mensajes que el juez
acepta. El corpus principal son las bases públicas del laboratorio (A1, E2 y ORU, en v2.5), como decidió Q-CV-2. Las muestras
quedan como corpus secundario.

## E-CV-3: ¿corre cada conversor aislado?

**Pasa al principio de CV1.** Contestarla exige descargar y ejecutar código de terceros: la imagen o el binario de .NET de
Microsoft, y el jar de LinuxForHealth. La condición 2 del ANTES pide hacerlo en una caja sin red, en una versión fijada. La
regla de parada se mantiene: si ninguno corre aislado, la etapa para.

## E-CV-4: ¿publican sus pruebas?

**Sí, los dos.**
- **Microsoft** trae salidas esperadas por tipo de mensaje en sus pruebas funcionales
  (`src/Microsoft.Health.Fhir.Liquid.Converter.FunctionalTests/TestData/Expected/Hl7v2/`): ADT_A01 4, ADT_A04 5, ORU_R01 5…
  Una discrepancia que ya esté en su salida esperada es **comportamiento querido** del proyecto. Se clasifica como «ya
  declarada».
- **LinuxForHealth** trae 58 clases de prueba en Java, con los mensajes dentro, y 3 mensajes de muestra.

Los issues abiertos de cada proyecto no se han mirado todavía: son lo primero de CV3.

## Desviaciones

- **DV-CV-1.** La primera pasada de E-CV-2 se saltó sin avisar 8 ficheros con BOM UTF-8: dio 57 mensajes en vez de 65. Se
  vio al cuadrar ficheros contra mensajes. `cv_pre_e2.py` lee con `utf-8-sig` y cuenta los ficheros sin ningún mensaje leído:
  0.
- **DV-CV-2.** La primera pasada de E-CV-1 normalizaba los elementos de forma tosca. No reconocía los polimórficos (`value[x]`
  frente a `valueQuantity`, `effective`), leía «identifier[] PLAC» como un nombre y trataba `subject` como hueco. Daba ORU 16
  de 23. Corregido antes de dar ninguna cifra; la tabla de arriba es la corregida.

## Siguiente: CV0

El diseño de Fable, a ciegas de lo que devuelven los conversores:
- el punto de entrada de solo transformación, sin MLLP ni acuse;
- el lector de la salida de un conversor (un Bundle);
- el perfil «guía», que coteje cada valor de ADT con los mapas de la guía y aparte las 6 filas de convención de ORU;
- la pregunta de la 0354 de v2.8.

Las Q de diseño, a Jev.
