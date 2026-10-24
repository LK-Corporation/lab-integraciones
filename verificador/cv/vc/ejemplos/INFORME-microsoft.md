# Verificación del conversor microsoft-fhir-converter

- **Conversor:** microsoft-fhir-converter, versión v7.0 (253307f); huella `766f8938d0c12c38` (con nombres `1118ff9a574e49e4`).
- **Imagen:** mcr.microsoft.com/dotnet/runtime:6.0, digest `sha256:75752d6e7d17246d939d8f0717a2daf14ca276e1fd6921caa489a70e24498881`.
- **Juez:** huella `40bbc3ef439a5f2a`, servidor 1.2.
- **Corpus:** adt 263, oru 40, minimos 68; huella `27d179bcb6408dcd`.
- **Caja:** --network none, --read-only, --tmpfs /tmp, --cap-drop ALL, --security-opt no-new-privileges, --user 65534:65534, --pids-limit 1024; límites: 60 s por mensaje, 3600 s por contenedor.
- **Herramienta:** verificar_conversor 1.0, huella `1ea91cf28e2a2e83`.

## Lo que esta herramienta no puede saber

> Este informe dice qué hallazgos ve el juez y con qué cita. **No dice si el proyecto del conversor ya los tiene declarados** (salidas esperadas, pruebas, documentación o issues): ese contraste lo hace una persona, como en `cv/RESULTADO-CV3.md`, y hasta entonces ningún mecanismo de aquí es «nuevo» ni «confirmado». De las cuatro condiciones del estudio, la herramienta comprueba tres (cita, clase, par mínimo) y deja la cuarta sin hacer.

## Categorías por corpus

| corpus | n | estados | correcto | fallo_silencioso | rechazo_incorrecto | indeterminado | fuera_de_alcance |
|---|---|---|---|---|---|---|---|
| adt | 263 | bundle 191, error 72 | 6 (2.3 %) | 185 (70.3 %) | 72 (27.4 %) | 0 (0.0 %) | 0 (0.0 %) |
| oru | 40 | bundle 39, error 1 | 33 (82.5 %) | 6 (15.0 %) | 1 (2.5 %) | 0 (0.0 %) | 0 (0.0 %) |

## Mecanismos que cuentan, por clase

Un hallazgo puede estar en dos clases; los casos no se suman entre clases. La columna «contraste» dice si una persona lo ha contrastado con el proyecto del conversor: aquí, siempre «sin hacer».

### valor_distinto

| hecho | ruta | n | corpus | ejemplo | citas | contraste |
|---|---|---|---|---|---|---|
| PV1-3 | Encounter.location | 57 | adt 57 | adt/A03-001: Encounter.location '^^MED^001^HOSPITAL^A^B^1^': la cadena de Location no conserva ['001', 'B', '1'] | [CM datatype-pl-to-location] [G PV1_Encounter.csv:7-9,12-13,27-31,68-69] | sin hacer |
| PV1-2 | Encounter.status | 16 | adt 16 | adt/A04-019: Encounter.status: esperado uno de ['finished', 'planned'], observado 'in-progress' | [CM table-hl70004-to-encounter-status] [CM table-hl70004-to-v3-actcode] [G PV1_Encounter.csv:5-6] | sin hacer |
| PV1-11 | Encounter.location | 12 | adt 12 | adt/A02-004: Encounter.location '^^PRE^000^HOSPITAL^A^B^1^': la cadena de Location no conserva ['000', 'B', '1'] | [CM datatype-pl-to-location] [G PV1_Encounter.csv:7-9,12-13,27-31,68-69] | sin hacer |
| OBX-5 | Observation.valueQuantity.comparator | 1 | oru 1 | oru/ORU-B09: Observation.valueQuantity.comparator: esperado '<', observado '<>' | [CM segment-obx-to-observation OBX-5] [G OBX_Observation.csv:8-26] | sin hacer |
| OBX-5 | Observation.valueQuantity.value | 1 | oru 1 | oru/ORU-B29: Observation.valueQuantity.value: esperado '.5', observado '5' (la precisión cuenta: Q-CV-D-10) | [CM segment-obx-to-observation OBX-5] [G OBX_Observation.csv:8-26] | sin hacer |
| OBX-5 | Observation.valueString | 1 | oru 1 | oru/ORU-B11: Observation.valueString: esperado ['Primera linea\\.br\\Segunda linea'], observado 'Primera linea\\nSegunda linea' | [CM segment-obx-to-observation OBX-5] [G OBX_Observation.csv:8-26] | sin hacer |
| PV1-6 | Encounter.location | 1 | adt 1 | adt/A1-A11-28: Encounter.location 'URG^1^A': la cadena de Location no conserva ['1', 'A'] | [CM datatype-pl-to-location] [G PV1_Encounter.csv:7-9,12-13,27-31,68-69] | sin hacer |

### dato_perdido

| hecho | ruta | n | corpus | ejemplo | citas | contraste |
|---|---|---|---|---|---|---|
| PV1-3 | Encounter.location | 184 | adt 184 | adt/A01-001: Encounter.location '^^ICU^001^HOSPITAL^A^B^1^': la cadena de Location no conserva ['001', 'B', '1'] | [CM datatype-pl-to-location] [G PV1_Encounter.csv:7-9,12-13,27-31,68-69] | sin hacer |
| PV1-11 | Encounter.location | 14 | adt 14 | adt/A02-004: Encounter.location '^^PRE^000^HOSPITAL^A^B^1^': la cadena de Location no conserva ['000', 'B', '1'] | [CM datatype-pl-to-location] [G PV1_Encounter.csv:7-9,12-13,27-31,68-69] | sin hacer |
| PV1-6 | Encounter.location | 11 | adt 11 | adt/A02-004: Encounter.location '^^OLD^002^HOSPITAL^A^B^1^': la cadena de Location no conserva ['002', 'B', '1'] | [CM datatype-pl-to-location] [G PV1_Encounter.csv:7-9,12-13,27-31,68-69] | sin hacer |
| PV1-8 | Encounter.participant | 8 | adt 8 | adt/A1-A01-03: Encounter.participant REF: falta 'D21^Otro^Ana' | [G MSG_ADT_A01.csv:36] PV1 → Encounter[1] | sin hacer |
| PID-12 | Patient.address.district | 6 | adt 6 | adt/A02-004: Patient.address.district: falta '03' | [G MSG_ADT_A01.csv:15] PID → Patient[1] | sin hacer |
| PV1-45 | Encounter.period.end | 5 | adt 5 | adt/A1-A13-31: Encounter.period.end: falta (PV1-45 = '202603151200') | [G PV1_Encounter.csv:72-73] | sin hacer |
| PID-16 | Patient.maritalStatus | 1 | adt 1 | adt/A1-A13-32: Patient.maritalStatus: falta ('http://terminology.hl7.org/CodeSystem/v3-NullFlavor', 'NAVU') | [CM table-hl70002-to-v3-maritalstatus] [G PID_Patient.csv:27] | sin hacer |

### dato_inventado

| hecho | ruta | n | corpus | ejemplo | citas | contraste |
|---|---|---|---|---|---|---|
| PID-30 | Patient.deceasedBoolean | 5 | adt 5 | adt/A02-016: Patient.deceasedBoolean: True sin PID-30 | [CM table-hl70136-to-special-values] [G PID_Patient.csv:51] | sin hacer |

### codigo_mal_mapeado

| hecho | ruta | n | corpus | ejemplo | citas | contraste |
|---|---|---|---|---|---|---|
| PV1-10 | Encounter.serviceType | 14 | adt 14 | adt/A02-004: Encounter.serviceType: esperado ('http://terminology.hl7.org/CodeSystem/service-type', '382') (de 'MED'), observado [(None, 'MED')] | [CM table-hl70069-to-service-type] [G PV1_Encounter.csv:26] | sin hacer |
| PV1-2 | Encounter.class | 2 | adt 2 | adt/A1-A04-15: Encounter.class: esperado ('http://terminology.hl7.org/CodeSystem/v2-0004', 'B') (de 'B'), observado [('http://terminology.hl7.org/CodeSystem/v3-ActCode', 'OBS')] | [CM table-hl70004-to-encounter-status] [CM table-hl70004-to-v3-actcode] [G PV1_Encounter.csv:5-6] | sin hacer |

### valor_imposible_convertido

| hecho | ruta | n | corpus | ejemplo | citas | contraste |
|---|---|---|---|---|---|---|
| PID-8 | Patient.gender | 2 | adt 2 | adt/A1-A11-25: Patient.gender: 'X' convertido desde 'X', fuera de la 0001 | [CM table-hl70001-to-administrative-gender] [F Patient.gender required] [G PID_Patient.csv:14] | sin hacer |

### recurso

| hecho | ruta | n | corpus | ejemplo | citas | contraste |
|---|---|---|---|---|---|---|
| OBX-3 | falta | 3 | oru 3 | oru/ORU-B09: falta la Observation del OBX 1.2 | [G MSG_ORU_R01.csv:67-69] | sin hacer |
| OBX | Observation | 1 | oru 1 | oru/ORU-B14: Observation urn:uuid:e7f80a26-e33e-cc27-eaa8-1377fc8fa1b5 sin origen propio en el mensaje | [G MSG_ORU_R01.csv:67-69] | sin hacer |

### referencia_rota

| hecho | ruta | n | corpus | ejemplo | citas | contraste |
|---|---|---|---|---|---|---|
| OBR | DiagnosticReport.result | 1 | oru 1 | oru/ORU-B14: DiagnosticReport.result {'reference': 'Observation/e7f80a26-e33e-cc27-eaa8-1377fc8fa1b5'}: no es una Observation de su OBR | [G MSG_ORU_R01.csv:67-69] | sin hacer |
| PID | Observation.subject | 1 | oru 1 | oru/ORU-B30: Observation.subject: {'reference': 'Patient/364bf61f-d0ac-3b9a-d91c-dbc2d9d9f46f'} apunta a un Patient que no está en el Bundle, y el mensaje no trae PID | [F Bundle «Resolving references in Bundles»] | sin hacer |

### fhir_invalido

| hecho | ruta | n | corpus | ejemplo | citas | contraste |
|---|---|---|---|---|---|---|
| PID-8 | Patient.gender | 8 | adt 8 | adt/A1-A01-04: Patient.gender: 'Z' fuera de administrative-gender (required) | [CM table-hl70001-to-administrative-gender] [F Patient.gender required] [G PID_Patient.csv:14] | sin hacer |
| PID-8 | Patient.gender | 2 | adt 2 | adt/A1-A11-25: Patient.gender: 'X' convertido desde 'X', fuera de la 0001 | [CM table-hl70001-to-administrative-gender] [F Patient.gender required] [G PID_Patient.csv:14] | sin hacer |
| PID-8 | Patient.gender | 1 | adt 1 | adt/A1-A08-20: Patient.gender: 'f' para 'f' | [CM table-hl70001-to-administrative-gender] [F Patient.gender required] [G PID_Patient.csv:14] | sin hacer |

## Rechazos

No son de las ocho clases. Los que el adaptador declara que el proyecto no convierte van aparte; el juez los cuenta igual (Q-CV-D-13).

| n | declarado por el adaptador | ejemplo |
|---|---|---|
| 73 | no | adt/A01-004: el conversor devolvió error 'Process failed: The format of Date or DateTime is invalid: L.\n' con un mensaje que la guía convierte |

Rechazos aceptables (Q-CV-D-7): 0.

## Pares mínimos del laboratorio

34 sondas escritas en el estudio para Microsoft y LinuxForHealth (`cv/cv3_minimos.py`). Un par que se reproduce aquí quiere decir que este conversor muestra el mismo mecanismo; uno que no, nada más que eso. Se reproducen 18 de 34.

| par | escrito para | objetivo | caso | control | se reproduce |
|---|---|---|---|---|---|
| M01-nm-punto-inicial | microsoft | OBX-5 valor_distinto | bundle/fallo_silencioso/sale | bundle/correcto/no sale | sí |
| M02-genero-fuera-de-tabla | microsoft | PID-8 fhir_invalido | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| M03-pda-sin-muerte | microsoft | PID-30 dato_inventado | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| M03b-pda-en-a01 | microsoft | PID-30 dato_inventado | bundle/fallo_silencioso/no sale | bundle/fallo_silencioso/no sale | no |
| M04-pv1-8-repetido | microsoft | PV1-8 dato_perdido | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| M05-clase-b | microsoft | PV1-2 codigo_mal_mapeado | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| M06-obx-tras-nte | microsoft | OBX(2)-3 recurso_ausente | bundle/fallo_silencioso/sale | bundle/correcto/no sale | sí |
| M06b-dos-nte | microsoft | OBX(2)-3 recurso_ausente | bundle/fallo_silencioso/sale | bundle/correcto/no sale | sí |
| M06c-nte-al-final | microsoft | OBX(2)-3 recurso_ausente | bundle/correcto/no sale | bundle/correcto/no sale | no |
| M06d-tres-obx | microsoft | OBX(2)-3 recurso_ausente | bundle/fallo_silencioso/sale | bundle/correcto/no sale | sí |
| M07-oru-sin-pid | microsoft | ['PID-3', 'PID'] referencia_rota | bundle/fallo_silencioso/sale | bundle/correcto/no sale | sí |
| M08-estado-civil-t | microsoft | PID-16 dato_perdido | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| M10-pl9-descripcion | microsoft | PV1-3 dato_perdido | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| M09-ft-br | microsoft | OBX-5 valor_distinto | bundle/fallo_silencioso/sale | bundle/correcto/no sale | sí |
| L01-sin-location | linuxforhealth | PV1-3 dato_perdido | bundle/fallo_silencioso/sale | bundle/correcto/no sale | sí |
| L02-estado-civil-a | linuxforhealth | PID-16 codigo_mal_mapeado | bundle/fallo_silencioso/no sale | bundle/fallo_silencioso/no sale | no |
| L03-pv1-10-med | linuxforhealth | PV1-10 codigo_mal_mapeado | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| L04-sad-2-3 | linuxforhealth | PID-11 valor_distinto | bundle/fallo_silencioso/no sale | bundle/fallo_silencioso/no sale | no |
| L05-genero-n | linuxforhealth | PID-8 valor_distinto | bundle/fallo_silencioso/no sale | bundle/fallo_silencioso/no sale | no |
| L06-obx-sin-tipo | linuxforhealth | OBX-3 recurso_ausente | bundle/correcto/no sale | bundle/correcto/no sale | no |
| L07-ft | linuxforhealth | OBX-5 dato_perdido | bundle/correcto/no sale | bundle/correcto/no sale | no |
| L08-tm | linuxforhealth | OBX-5 dato_perdido | bundle/correcto/no sale | bundle/correcto/no sale | no |
| L09-obx-11-d | linuxforhealth | OBX-11 codigo_mal_mapeado | bundle/correcto/no sale | bundle/correcto/no sale | no |
| L10-obr-25-i | linuxforhealth | OBR-25 codigo_mal_mapeado | bundle/correcto/no sale | bundle/correcto/no sale | no |
| L11-sn-rango | linuxforhealth | OBX-5 valor_distinto | bundle/correcto/no sale | bundle/correcto/no sale | no |
| L12-sn-distinto | linuxforhealth | OBX-5 valor_distinto | bundle/fallo_silencioso/sale | bundle/correcto/no sale | sí |
| L13-pv1-52 | linuxforhealth | PV1-52 dato_perdido | bundle/fallo_silencioso/no sale | bundle/fallo_silencioso/no sale | no |
| L14-xpn-6-titulo | linuxforhealth | PID-5 dato_perdido | bundle/fallo_silencioso/no sale | bundle/fallo_silencioso/no sale | no |
| L15-xtn-12 | linuxforhealth | PID-13 dato_perdido | bundle/fallo_silencioso/no sale | bundle/fallo_silencioso/no sale | no |
| L16-cx-4-solo-nombre | linuxforhealth | PID-3 dato_perdido | bundle/fallo_silencioso/no sale | bundle/fallo_silencioso/no sale | no |
| L17-pid-30-no | linuxforhealth | PID-30 valor_imposible_convertido | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| L18-unidad-cwe-2 | linuxforhealth | OBX-6 valor_distinto | bundle/correcto/no sale | bundle/fallo_silencioso/sale | no |
| R01-nulo-en-dtm | microsoft | MSH-9 error | error/rechazo_incorrecto/sale | bundle/fallo_silencioso/no sale | sí |
| R02-nm-cero-inicial | microsoft | MSH-9 error | error/rechazo_incorrecto/sale | bundle/fallo_silencioso/no sale | sí |

## Lo que no se juzgó

303 mensajes: 303 juzgados y 0 no juzgados.

- **Fuera de alcance:** 0.
- **Indeterminado, sin_salida:** 0.
- **Indeterminado, lectura:** 0.
- **Indeterminado, emparejamiento:** 0.
- **Sin evidencia (falló la caja):** 0.
- **Sin MSH legible:** 0.
- **Muestras de los proyectos:** no disponibles.

## Sensibilidad

| decisión | fallo silencioso con la de Jev | con la alternativa |
|---|---|---|
| Q-CV-D-3 | 191 | 191 |
| Q-CV-D-5 | 191 | 191 |
| Q-CV-D-9 | 191 | 191 |

## Convenciones

Diferencias que la guía admite y no cuentan: 7.

| hecho | firma | n |
|---|---|---|
| OBX-11 | Observation.status: <v> para <v> (sin destino en el ConceptMap) | 3 |
| OBX-5 | OBX-<n> repetido (<n>): forma admitida por la guía (MSG_ORU_R01.csv:<n>-<n>) | 2 |
| OBR-25 | DiagnosticReport.status: <v> para <v> (sin destino en el ConceptMap) | 1 |
| OBX-8 | Observation.interpretation <v> para <v>, fuera del ConceptMap | 1 |

## Límites

Los del juez: L-CV-1, L-CV-2, L-CV-3, L-CV-4, L-CV-5, L-CV-6, L-CV-7, L-CV-8, L-CV-9, L-CV-10, L-CV-11, L-CV-12, L-CV-13, L-CV-14, L-CV-15, L-CV-16 (`info_verificador`).

- **L-VC-1:** La herramienta no sabe si una discrepancia la tiene declarada el proyecto: no lee salidas esperadas, pruebas, documentación ni issues. Aquí todo es «sin_contraste».
- **L-VC-2:** Solo juzga lo que juzgan adt_conv y oru_conv: ADT de los ocho eventos y ORU^R01. Otro tipo de mensaje entra en el corpus y el juez lo aparta como fuera de alcance.
- **L-VC-3:** Solo conversores que corran como programa de línea de órdenes dentro de un contenedor Docker, leyendo y escribiendo ficheros. Un servicio HTTP, una biblioteca o un conversor que necesite red no caben en el adaptador.
- **L-VC-4:** La imagen debe estar ya en la máquina: la herramienta no descarga nada y no comprueba de dónde salió; registra su digest.
- **L-VC-5:** La huella del conversor con la fórmula del estudio no ve nombres ni rutas: renombrar ficheros no la cambia. Por eso va también la huella con nombres (Q-VC-D-1).
- **L-VC-6:** «vacio» y «sin_respuesta» no distinguen la caja del conversor (L-CV-8). Tras un tiempo vencido, los mensajes sin salida se reintentan una vez, uno a uno (Q-VC-D-9).
- **L-VC-7:** Las muestras de los proyectos no viajan con el repositorio: sin --muestras, el corpus son las bases A1/E2, las ORU y, con los dos conversores del estudio, los 68 mínimos; todo sintético y en v2.5.
- **L-VC-8:** El control caso por caso exige el detalle del estudio, que no es público; desde la copia pública se comprueban las identidades, los agregados por categoría y los pares mínimos.
- **L-VC-9:** Las restricciones de la caja se comprueban en la orden construida, no en el núcleo: un Docker sin raíz, con --userns-remap o con otro runtime puede comportarse distinto.
- **L-VC-10:** duracion_ms es aproximado cuando varios mensajes comparten contenedor; la herramienta no mide rendimiento.
- **L-VC-11:** No se comprueba que el conversor sea determinista; una corrida es una corrida.
- **L-VC-12:** Un Bundle de más de 4.000.000 de caracteres no se juzga (error demasiado_grande, DV-CV-5).
- **L-VC-13:** Un mensaje sin plantilla disponible (comprobar_fichero) se marca error sin_plantilla sin entrar en la caja.
- **L-VC-14:** La herramienta hereda las decisiones, límites y ambigüedades del juez (Q-CV-D-n, L-CV-n, AMB-CV-n); no los cambia.
- **L-VC-15:** Los 68 mínimos son sondas escritas para dos conversores concretos: que se reproduzca uno no dice que sea una discrepancia del conversor contrastada con su proyecto.

## Cómo repetir

```
python3 cv/verificar_conversor.py microsoft.json <salida> --artefactos <carpeta de artefactos>
```
