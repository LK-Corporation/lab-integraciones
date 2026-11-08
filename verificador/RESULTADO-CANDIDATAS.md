# RESULTADO de la etapa 36: las 2 candidatas de la etapa 33 (7-nov-2026)

**Completado el 8-nov (etapa 37):** el juez deja de contar mal las dos conductas de este resultado
([`RESULTADO-JUEZ.md`](RESULTADO-JUEZ.md)). La `S` a `unknown` de LinuxForHealth es ahora una nota de convención, y la
Observation de ACC, un «recurso sin mapa».

> **De las 2 candidatas de la etapa 33, ninguna es nueva.** La de Microsoft es M-28, una de las 31 ya declaradas del estudio de
> conversores, que el estudio ya contaba en las muestras de Microsoft. La de LinuxForHealth es una convención, y el juez la cuenta
> por error.
>
> - **Microsoft** saca de un ACC una Observation (`injury-incident`, con la fecha de ACC-1). La guía no mapea ACC.
>   - Es la conducta de M-28: el proyecto la declara en una salida esperada publicada, en su prueba y en su documentación.
>   - La descripción publicada de M-28, «Observation de PDA», se queda corta, y se corrige: también de ACC.
> - **LinuxForHealth** convierte PID-8 = `S` (un valor del ejemplo mismo de v2.5, en una tabla de usuario) en
>   `Patient.gender` = `unknown`. La guía no dice qué hacer con un valor fuera de su mapa de la 0001, y FHIR obliga a uno de cuatro
>   códigos.

La pregunta, fijada antes de medir, está en [`ANTES-ETAPA-CANDIDATAS.md`](ANTES-ETAPA-CANDIDATAS.md).

## Cómo se hizo

| | |
|---|---|
| El método | El de las etapas 20 y 26: par mínimo, contraste con lo que el proyecto ya sabe y revisión adversaria. Las clases: nueva, ya declarada, convención o fallo del juez |
| La previsión | Sellada antes de correr nada: [`ca/PREVISION-CA.json`](ca/PREVISION-CA.json), con la de Jev en [`ca/decision-jev-prevision-ca.md`](ca/decision-jev-prevision-ca.md) |
| Los pares mínimos | [`ca/pares/`](ca/pares/), de [`ca/pares_ca.py`](ca/pares_ca.py), con los dos conversores en su caja: [`ca/PARES-CA.json`](ca/PARES-CA.json). Las corridas en bruto no se publican |
| El contraste | Un agente por conversor, que lee las fuentes, las salidas esperadas, las pruebas, la documentación y los issues: [`ca/CONTRASTE-CA-microsoft.json`](ca/CONTRASTE-CA-microsoft.json) y [`ca/CONTRASTE-CA-linuxforhealth.json`](ca/CONTRASTE-CA-linuxforhealth.json) |
| La primera clasificación | [`ca/CLASIFICACION-CA.json`](ca/CLASIFICACION-CA.json): las dos, ya declaradas. La revisó otro modelo, que intentó tumbarla: [`ca/ADVERSARIA-CA.json`](ca/ADVERSARIA-CA.json). Fue Sonnet, según el registro de la sesión; el fichero no lo dice |
| Las decisiones de Jev | La clase de LinuxForHealth y lo que se hace con M-28: [`ca/decision-jev-ca.md`](ca/decision-jev-ca.md), [`ca2`](ca/decision-jev-ca2.md), [`ca3`](ca/decision-jev-ca3.md) y [`ca3b`](ca/decision-jev-ca3b.md), con sus estados ([`ca/estado_ca.md`](ca/estado_ca.md), [`ca2`](ca/estado_ca2.md) y [`ca3`](ca/estado_ca3.md)) |

**La regla cuando encajan dos clases:**
- una diferencia que el estándar permite es convención y no cuenta;
- las ya declaradas son discrepancias que cuentan y que el proyecto sabe;
- una conducta que ya tiene clase en el estudio es esa clase.

Las dos primeras son del ANTES del estudio de conversores (`ANTES-ETAPA-CONVERSORES.md:48-51`); la tercera es de esta etapa.

## Microsoft: ACC → Observation `injury-incident`, que es M-28

- **El par mínimo:** un ADT_A01 v2.5 con ACC (`MS-ACC-con`) y el mismo sin ACC (`MS-ACC-sin`).
  - Con ACC sale una Observation de más, con `code` = `injury-incident` y `effectiveDateTime` = ACC-1, y el juez cuenta un recurso
    «sin origen propio en el mensaje».
  - Sin ACC, ninguna de las dos cosas. Los demás hallazgos son los mismos en los dos.
  - LinuxForHealth no saca nada de ACC.
- **La guía calla:** ningún mapa de mensaje ni de segmento del paquete `v2mappings` 1.0.0 cita ACC. En ADT_A01, las Observation
  salen de OBX, y una de PD1-7 cuando viene.
- **El proyecto lo declara:**
  - la salida esperada de su muestra `ADT-A01-01` (con ACC) trae la misma Observation `injury-incident`, con `effectiveDateTime`
    = ACC-1 (`ADT-A01-01-expected.json:5550` y `5619`);
  - su prueba funcional compara la salida entera (`BaseConvertDataFunctionalTests.cs:27` y `307`);
  - su documentación lista ACC como origen de la Observation de ADT_A01 (`docs/HL7v2-templates.md:152`);
  - hay lo mismo en otras 18 salidas esperadas, y la rama principal no cambia. La muestra es de v2.8 y el par de v2.5, y sale de la
    misma plantilla.
- **Es M-28,** una clase ya declarada del estudio (`cv/cv3_clases.py:86`).
  - Tiene el mismo mecanismo, la misma firma y la misma declaración.
  - En el estudio solo miraba las muestras de Microsoft, y allí ya contaba esta Observation. En la muestra `ADT-A31-01`, que lleva
    ACC y no PDA, la Observation que cuenta es la `injury-incident`.
  - La etapa 33 la vio como candidata porque los 30 ADT con ACC son del corpus del laboratorio, que M-28 no miraba.
- **La descripción de M-28 se corrige,** de «Observation de PDA» a «Observation de PDA o de ACC».
  - **Lo decidió Jev en `Q-CA-2`,** dos veces con el mismo estado (`ca/estado_ca3.md`): por la tabla y el código, 0,50 y 0,51; solo
    la tabla, 0,36 y 0,35; con confianza 0,25 y 0,26. Casi un empate, y con esa decisión se reabre el sello de otra etapa.
  - **Una primera respuesta se descartó:** «corregir también el estudio» (0,97, `ca/decision-jev-ca2.md`). Su estado decía, sin
    ser cierto, que había que regenerar la página web, y le faltaba que `cv3_clases.py` está sellado.
  - La tabla de `cv/RESULTADO-CV3.md` lleva la marca.
  - `cv/cv3_clases.py` se corrige con un bloque nuevo, el 7, en el sello de la etapa 33 (`ga/SELLO-GA.txt`).
  - Los JSON de clases de las corridas pasadas se quedan con el texto de su etapa.
- **Lo que dice el juez:** la cuenta como recurso «sin origen propio en el mensaje», y cita para ella una hoja de ORU. Tiene origen en
  el mensaje (ACC-1). La guía no la crea, así que no le cabe la nota que el juez da a lo que la guía crea fuera de su sitio (L-CV-7).
  El estudio la cuenta como ya declarada.

**Clase: ya declarada (M-28).**

## LinuxForHealth: PID-8 = `S` → `Patient.gender` = `unknown`

- **El par mínimo:** la copia completada del ejemplo 1 de los veterinarios del capítulo 3 de v2.5, con PID-8 = `S`, `F` y `U`.
  - Con `S`, `unknown` y el hallazgo de PID-8.
  - Con `F`, `female`; con `U`, `unknown`; sin hallazgo de PID-8 en los dos.
- **El estándar y la guía:**
  - la 0001 de v2.5 es una tabla de usuario con valores sugeridos (F, M, O, U, A, N), y la `S` está en el ejemplo mismo de v2.5, el
    de una perra esterilizada (Ch03.txt:5034-5044 y 10863-10868);
  - la guía lleva PID-8 a `Patient.gender` con su mapa de la 0001, que no tiene `S` ni valor por omisión;
  - `Patient.gender` de FHIR R4 solo admite cuatro códigos.
- **El proyecto:** una prueba de su extractor, `get_adm_gender_value_unknow`, convierte «ABC», un valor fuera de su mapa, en
  `unknown` (`SimpleDataValueResolverTest.java`, en la v1.1.0 y en la rama principal). No hay ninguna con un mensaje entero.
- **La clase:**
  - el estándar permite el valor, la guía calla y `unknown` es una elección defendible, así que es convención por la regla del
    estudio;
  - la primera clasificación y la revisión adversaria la daban por ya declarada, y Jev también, la primera vez. Pero ese estado
    solo traía los hechos de un lado, y la revisión a ciegas lo señaló;
  - con la regla y los hechos del otro lado, Jev decidió convención (0,99, confianza 0,98). Ese segundo estado
    (`ca/estado_ca2.md`) tampoco estaba del todo equilibrado. Resumía la revisión a ciegas solo por la mitad (decía que encaja en
    convención, y no que encajaba en las dos y faltaba la regla), y no repetía el precedente del primero: «ya declarada» cuando lo
    declara una prueba. La regla de precedencia basta para decidir.
- **Lo que dice el juez:** la cuenta como «valor imposible convertido».
  - Su perfil de PID-8 dice «fuera de la 0001: ausente».
  - Su función para las demás tablas de usuario dice «fuera de la tabla (user-defined), convención».
  - Las 16 convenciones del estudio son notas de convención del juez, y esta no es una de ellas: el juez la cuenta.
  - **El juez se equivoca aquí:** por la regla, una convención no cuenta. El hallazgo seguirá saliendo, porque el juez no cambia en
    esta etapa (lo arregla la etapa 37).

**Clase: convención.**

## Lo que cambia en lo publicado

- **La descripción de M-28,** en la tabla de `cv/RESULTADO-CV3.md` y en `cv/cv3_clases.py`, con el bloque 7 del sello de la 33.
- **El resultado de la etapa 33** lleva una línea arriba, como hizo la 28 con el de la 26, y la marca donde dice que las
  candidatas no se confirmaron. También la marca su sección del README. Sus JSON sellados (`ga/CIFRAS-GA-B.json` y
  `ga/CLASES-GA-v2.json`) se quedan como están.
- **El juez no cambia en esta etapa** (lo fija el ANTES; lo cambia la etapa 37).
- **Las cifras del estudio no cambian.** De su texto, solo la descripción de M-28.
  - Las 15 nuevas, las 31 ya declaradas y las 16 convenciones de los conversores siguen igual.
  - La candidata de Microsoft era ya M-28, y la de LinuxForHealth es una convención que el juez cuenta por error, no una de las 16.

## La previsión

| | Jev | Lo que pasó |
|---|---|---|
| Microsoft | Nueva (0,90; confianza 0,87) | Ya declarada (M-28) |
| LinuxForHealth | Nueva (0,49, convención 0,37; confianza 0,32) | Convención |

No acertó ninguna. **Su estado** ([`ca/estado_prevision_ca.md`](ca/estado_prevision_ca.md)) **tampoco era neutral.**
- Su único dato de base empujaba hacia «nueva».
- No decía que en las etapas 14l, 20 y 26 hubo más ya declaradas que nuevas.
- Atribuía a la revisión el paso de 5 a 3 nuevas de la 26, que fue la corrección de la 28.
- El ANTES, ese estado y la primera clasificación decían, además, que en ADT_A01 las Observation salen de OBX: también sale una de
  PD1-7.

## Lo que se vio de paso

- **Microsoft pasa la `S` tal cual a `Patient.gender`,** que no es válido en FHIR R4. Es una clase que el estudio ya tenía: «copia a
  Patient.gender un PID-8 fuera de la 0001 o en minúscula: FHIR inválido».
- **El mapa de LinuxForHealth lleva `N` a `unknown`,** y el de la guía a `other`. Es L-12, una de las 15 nuevas del estudio, que el
  juez ya marca.

## Cómo se repite

Desde `verificador/`:
- `python3 ca/pares_ca.py <la carpeta lab/adt del corpus de la versión 2>` escribe los pares en `ca/pares/`;
- `python3 cv/verificar_conversor.py cv/adaptadores/<conversor>.json <salida> --artefactos <conversores> --corpus ca/pares
  --sin-corpus-lab --sin-minimos --json-solo` los corre con cada conversor;
- `python3 ca/parche_m28_ca.py`, `ca/parche_33_ca.py` y `ca/parche_33_ca2.py` hacen los cambios de lo publicado.
