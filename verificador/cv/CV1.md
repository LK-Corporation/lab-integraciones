# CV1: los conversores aislados, las pruebas en rojo, el código y el primer Bundle real (23-oct-2026)

**CV1 hecho.**
- Los dos conversores corren aislados (E-CV-3).
- Las 18 P-CV se escribieron en rojo y pasan.
- El juez nuevo no cambia nada de lo de antes: todas las suites en verde, la regresión de 2.721 en CASA y la concordancia de A1
  igual.
- El lector lee sin indeterminado los primeros Bundles reales de los dos conversores.

No se ha juzgado nada: CV2 empieza por sellar la previsión.

## CV1-a, E-CV-3: cada conversor en su caja

**Los dos corren aislados, en 6 minutos (16:16-16:22). La regla de parada no salta.** La caja de los dos es la misma:

- **Sin red:** `--network none`.
- **Sistema de ficheros:** en solo lectura (`--read-only`), con `/tmp` en memoria.
- **Usuario y privilegios:** `nobody` (65534), `--cap-drop ALL` y `no-new-privileges`.
- **Montajes:** el código y las plantillas, en solo lectura.

| | Microsoft FHIR-Converter | LinuxForHealth hl7v2-fhir-converter |
|---|---|---|
| Versión | etiqueta `v7.0`, commit `253307f`, construida desde el código | `v1.1.0` publicado en Maven Central (DV-CV-3) |
| Cómo se construye (con red, una vez) | `dotnet publish` de `Microsoft.Health.Fhir.Liquid.Converter.Tool` en `mcr.microsoft.com/dotnet/sdk:6.0` | `mvn dependency:copy-dependencies` (el jar y 77 dependencias) en `maven:3.9-eclipse-temurin-11`; SHA-1 del jar igual al de Central |
| Cómo corre (sin red) | `dotnet Tool.dll convert -d <plantillas> -r <MSH-9> -i <entrada> -o <salida>` en `dotnet/runtime:6.0` | `cv/lfh/Arnes.java` (copia de la que corre en `privado/cv/conversores/lfh/`): un `main` que llama a `HL7ToFHIRConverter.convert(String)` |
| Huella | publicado `48ff53b4…`, plantillas Hl7v2 (64) `b1abbd0f…` | jar `67d707cb…`, lib `4077cb25…`, arnés `3fea5b3c…` |
| Imagen | runtime `sha256:75752d6e…`, sdk `sha256:c8fdd06e…` | `maven@sha256:7bb84a45…` |
| Una muestra A01 | 1,1 s; `{Status, FhirResource}` con un Bundle `batch` de 119 entries y `fullUrl` `urn:uuid:` | 3,5 s con el arranque de la JVM; Bundle `collection` con `fullUrl` relativos (`MessageHeader/<id>`) |

> El comentario de cabecera de `cv/lfh/Arnes.java` dice «1.1.1»: es de antes de DV-CV-3. Lo que corre es la v1.1.0, y el
> fichero no se toca porque entra en la huella del arnés.

Los artefactos viven fuera de git, en `privado/cv/conversores/`. El arnés que los corre es `cv/correr_conversor.py`: escribe
una evidencia por mensaje con la forma que lee el juez (S-CV-2) y la huella de cada conversor.

## CV1-b, las pruebas en rojo (`cce6b63`)

**`prueba_conversion.py`, P-CV-1..18: fallan las 18 antes del código, por la razón prevista.** El punto de entrada `adt_conv`
no existía y el módulo `conversion` tampoco.
- Los Bundles de prueba se escriben a mano. No salen del perfil, para que un error de la proyección no se confirme a sí mismo.
- Cada prueba cambia una sola cosa y lleva su control negativo.
- Mandan las decisiones de Jev: Q-CV-D-6 y Q-CV-D-9, contra la recomendación de Fable.

## CV1-c, el código

| Pieza | Qué |
|---|---|
| `conversion.py` (nuevo, 1.522 líneas) | El lector del Bundle, el emparejamiento por papel, el perfil «guía» por elemento, las ocho clases, el veredicto y el perfil como datos (`PERFIL_GUIA_ADT`, `PERFIL_GUIA_ORU`). Más `INFO`: S-CV-1..6, L-CV-1..13, AMB-CV-1..9, las decisiones de Jev y la sensibilidad. Los 16 mapas de vocabulario se generan desde el paquete (`cv/extraer_mapas.py`), y `--autoprueba` los compara con él: IGUALES |
| `puntos_entrada.py` | `adt_conv` y `oru_conv`: puerto 0, `solo_transformacion`, `familia`, con el contrato de `adt_fhir` y `oru_fhir` |
| `verificador.py` | Una línea: con `solo_transformacion`, `verificar` despacha a `conversion.verificar` antes de leer acuse, log o canónico |
| `mcp_verificador.py` | `conversion` en el esquema (con tope de 4 MB para el Bundle, DV-CV-5) y `verificar_caso` con su salida propia. Además, `consultar_tabla` con `perfil_guia_adt` y `perfil_guia_oru`, `info_verificador.conversores` y `conversion.py` en la huella |
| `cv/parche_cv1.py` | El enganche, con reemplazos exactos que se afirman una sola vez; idempotente |

**Comprobado tras el código:**
- `prueba_conversion` en verde: 86 comprobaciones, 18 pruebas.
- `conversion --autoprueba`: TODO BIEN.
- `ve/comprobar.sh` entero en verde:
  - `prueba_verificador`, MCP, `prueba_adt` (27), `prueba_oru` (696), `prueba_multitipo` (705), mutantes (38) y arnés (11);
  - las autopruebas de los mapeadores y los almacenes;
  - el contrato del canónico IGUAL;
  - la concordancia de A1, sin cambios frente a git;
  - **la regresión de 2.721, CASA**;
  - `prueba_ve`: 21/21.
- `prueba_mcp_verificador`: TODO BIEN.

**La huella del juez pasa a `63d40cd0…`,** porque `conversion.py` entra en la huella. El laboratorio estaba en `b9788fab…`, y
los resultados sellados conservan la suya. El servidor sigue declarando 1.1 hasta CV4, y el servicio `verificador-mcp` sigue
con el juez anterior hasta entonces.

## CV1-d, el primer Bundle real por el lector (`cv/cv1d.py`)

Un A01 de A1 (`A1-A01-00`) y un ORU (`bases_oru/B01`), por cada conversor, pasados solo por el lector, sin el perfil.

| | Microsoft | LinuxForHealth |
|---|---|---|
| A01 | Patient y Encounter `unico`; 0 referencias sin resolver; otros tipos: MessageHeader 1, Provenance 2, Organization 2, Location 3 | Patient y Encounter `unico`; 0 referencias sin resolver; otros tipos: ninguno |
| ORU (1 OBR, 3 OBX) | Patient `unico`, DiagnosticReport por `identifier`, las 3 Observation por `referencia`; otros tipos: MessageHeader 1, Provenance 1, Organization 2 | igual, sin otros tipos |

**El lector lee los cuatro sin indeterminado, sin ambigüedad y sin sobrantes.** No hizo falta tocarlo.

## Desviaciones (DV-CV)

- **DV-CV-1 y DV-CV-2:** son de CV-pre (`RESULTADO-CV-PRE.md`).
- **DV-CV-3, versión de LinuxForHealth.** La etiqueta v1.1.1 de GitHub no está en Maven Central, donde la última publicada es
  `v1.1.0`, con la v. Se usa la publicada, que es lo que recibe quien lo usa. Entre las dos cambian 7 líneas de código
  (`HL7ToFHIRConverter` y `ExpressionUtility`).
- **DV-CV-4, claves de los PE.** Los PE de conversión no llevan `mapeador`, aunque el diseño lo ponía:
  - así `comparar_canonico` y las ramas que miran `mapeador` siguen sin tocarse;
  - la familia va en `familia`;
  - `oru_conv` no lleva `todas_las_ocurrencias`, que no usa y que `prueba_oru.py:70` prohíbe en otros PE.
- **DV-CV-5, tope del Bundle.** El esquema lo limita a 4 MB; el diseño decía 70.000 caracteres. El Bundle real de Microsoft
  para una sola muestra A01 tiene 161.370. El control negativo de P-CV-18 usa 4.000.001.
- **DV-CV-6, pruebas cambiadas a propósito:**
  - **`prueba_multitipo.py`:** excluye los PE de conversión del bucle de acuse («punto equivocado → AR 200»), porque no
    acusan, igual que ya excluía `adt_fhir` y `oru_fhir`, y pone al día dos listas fijas de nombres de PE;
  - **en `prueba_conversion.py`:** P-CV-18 lee `entradas`, la clave de siempre de `consultar_tabla`, y valida con el esquema
    de la herramienta; P-CV-4 espera `unico` para un Encounter solo, como dice §2.2 (la tabla de P-CV-4 decía «referencia»).
- **DV-CV-7, corpus de ADT.** Son 263 mensajes, no 479: A1 ya incluye las 216 bases de E2, y la previsión de Fable (§7.2)
  las contaba dos veces. Se corrige en la previsión sellada de CV2.
- **DV-CV-8, formas en P-CV-15.** Las ocho formas se comprueban con «0 hallazgos que cuentan», no con «8 notas», porque no
  toda forma deja nota (el orden de las entries, por ejemplo).
- **DV-CV-9, `oras`.** La construcción de Microsoft descargó también el binario `oras` de su gestión de plantillas. No se usa
  al convertir.
- **Nombres de hecho en ORU.** Con más de una ocurrencia, el hecho lleva su número, `OBX(2)-5` y `OBR(2)`, como DV-ORU-1. La
  primera va sin número.

## Siguiente: CV2

1. **Completar la previsión de §7 con las cuentas del corpus y sellarla con su huella antes de juzgar.** Las cuentas son los
   n por evento, por PID-3 múltiple, por PL completo, por SN… El corpus es A1 (263) y ORU (40), más las 10 muestras aceptadas
   y las 52 de 2.8, con las marcas L18.
2. Después, juzgar con los dos conversores y adjudicar lo que salga fuera de previsto.
