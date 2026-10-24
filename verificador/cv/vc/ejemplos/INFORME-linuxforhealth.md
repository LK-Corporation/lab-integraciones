# Verificación del conversor linuxforhealth-hl7v2-fhir-converter

- **Conversor:** linuxforhealth-hl7v2-fhir-converter, versión v1.1.0 (Maven Central; DV-CV-3); huella `ac41f71b98ee75ba` (con nombres `7ad4d5463640901a`).
- **Imagen:** maven:3.9-eclipse-temurin-11, digest `sha256:7bb84a451705605a47d24eb844d4d9ab03e33e131a507db76aafe25db3907f64`.
- **Juez:** huella `40bbc3ef439a5f2a`, servidor 1.2.
- **Corpus:** adt 263, oru 40, minimos 68; huella `27d179bcb6408dcd`.
- **Caja:** --network none, --read-only, --tmpfs /tmp, --cap-drop ALL, --security-opt no-new-privileges, --user 65534:65534, --pids-limit 1024; límites: 60 s por mensaje, 3600 s por contenedor.
- **Herramienta:** verificar_conversor 1.0, huella `1ea91cf28e2a2e83`.

## Lo que esta herramienta no puede saber

> Este informe dice qué hallazgos ve el juez y con qué cita. **No dice si el proyecto del conversor ya los tiene declarados** (salidas esperadas, pruebas, documentación o issues): ese contraste lo hace una persona, como en `cv/RESULTADO-CV3.md`, y hasta entonces ningún mecanismo de aquí es «nuevo» ni «confirmado». De las cuatro condiciones del estudio, la herramienta comprueba tres (cita, clase, par mínimo) y deja la cuarta sin hacer.

## Categorías por corpus

| corpus | n | estados | correcto | fallo_silencioso | rechazo_incorrecto | indeterminado | fuera_de_alcance |
|---|---|---|---|---|---|---|---|
| adt | 263 | bundle 162, error 101 | 11 (4.2 %) | 160 (60.8 %) | 92 (35.0 %) | 0 (0.0 %) | 0 (0.0 %) |
| oru | 40 | bundle 40 | 4 (10.0 %) | 36 (90.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) |

## Mecanismos que cuentan, por clase

Un hallazgo puede estar en dos clases; los casos no se suman entre clases. La columna «contraste» dice si una persona lo ha contrastado con el proyecto del conversor: aquí, siempre «sin hacer».

### valor_distinto

| hecho | ruta | n | corpus | ejemplo | citas | contraste |
|---|---|---|---|---|---|---|
| PV1-2 | Encounter.status | 108 | adt 108 | adt/A01-001: Encounter.status: esperado uno de ['in-progress'], observado 'unknown' | [CM table-hl70004-to-encounter-status] [CM table-hl70004-to-v3-actcode] [G PV1_Encounter.csv:5-6] | sin hacer |
| PID-11 | Patient.address.line | 5 | adt 5 | adt/A1-A01-02: Patient.address.line: esperado ['C/ Real 5', 'Piso 3', 'Puerta B', 'Esc 2'], observado ['C/ Real 5', 'Esc 2'] | [CM datatype-xad-to-address] [CM table-hl70190-to-address-use/-type] [G PID_Patient.csv:17] | sin hacer |
| OBX-5 | Observation.valueCodeableConcept.text | 1 | oru 1 | oru/ORU-B15: Observation.valueCodeableConcept.text: esperado 'E. coli' | [CM segment-obx-to-observation OBX-5] [G OBX_Observation.csv:8-26] | sin hacer |
| OBX-5 | Observation.value[x] | 1 | oru 1 | oru/ORU-B07: Observation.value[x] SN '^1^-^5': esperado valueRange, observado ['valueQuantity'] | [CM segment-obx-to-observation OBX-5] [G OBX_Observation.csv:8-26] | sin hacer |
| OBX-5 | Observation.value[x] | 1 | oru 1 | oru/ORU-B09: Observation.value[x] SN '<>^5': esperado valueString, observado ['valueQuantity'] | [CM segment-obx-to-observation OBX-5] [G OBX_Observation.csv:8-26] | sin hacer |
| PID-8 | Patient.gender | 1 | adt 1 | adt/A1-A04-15: Patient.gender: esperado 'other', observado 'unknown' | [CM table-hl70001-to-administrative-gender] [F Patient.gender required] [G PID_Patient.csv:14] | sin hacer |

### dato_perdido

| hecho | ruta | n | corpus | ejemplo | citas | contraste |
|---|---|---|---|---|---|---|
| PV1-3 | Encounter.location | 160 | adt 160 | adt/A01-001: Encounter.location: falta '^^ICU^001^HOSPITAL^A^B^1^' | [CM datatype-pl-to-location] [G PV1_Encounter.csv:7-9,12-13,27-31,68-69] | sin hacer |
| PV1-11 | Encounter.location | 20 | adt 20 | adt/A01-004: Encounter.location: falta '^^PRE^000^HOSPITAL^A^B^1^' | [CM datatype-pl-to-location] [G PV1_Encounter.csv:7-9,12-13,27-31,68-69] | sin hacer |
| PV1-6 | Encounter.location | 5 | adt 5 | adt/A1-A01-03: Encounter.location: falta 'URG^1^A' | [CM datatype-pl-to-location] [G PV1_Encounter.csv:7-9,12-13,27-31,68-69] | sin hacer |
| OBX-5 | Observation.valueString | 1 | oru 1 | oru/ORU-B11: Observation.valueString: falta (OBX-5 'Primera linea\\.br\\Segunda linea') | [CM segment-obx-to-observation OBX-5] [G OBX_Observation.csv:8-26] | sin hacer |
| OBX-5 | Observation.valueTime | 1 | oru 1 | oru/ORU-B13: Observation.valueTime: falta (OBX-5 '0715') | [CM segment-obx-to-observation OBX-5] [G OBX_Observation.csv:8-26] | sin hacer |

### dato_inventado

| hecho | ruta | n | corpus | ejemplo | citas | contraste |
|---|---|---|---|---|---|---|
| PV1-44 | Encounter.period.start | 120 | adt 120 | adt/A01-001: Encounter.period.start: '1988-10-28T02:16:07-05:00' presente sin PV1-44 | [G PV1_Encounter.csv:71] | sin hacer |

### codigo_mal_mapeado

| hecho | ruta | n | corpus | ejemplo | citas | contraste |
|---|---|---|---|---|---|---|
| OBX-8 | Observation.interpretation | 30 | oru 30 | oru/ORU-B01: Observation.interpretation: esperado ('http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', 'N') (de 'N'), observado [('http://terminology.hl7.org/CodeSystem/v2-0078', 'N')] | [CM table-hl70078-to-v3-observationinterpretation] [G OBX_Observation.csv:39] | sin hacer |
| PV1-2 | Encounter.status | 26 | adt 26 | adt/A1-A03-10: Encounter.status: esperado uno de ['finished', 'in-progress'], observado 'unknown' | [CM table-hl70004-to-encounter-status] [CM table-hl70004-to-v3-actcode] [G PV1_Encounter.csv:5-6] | sin hacer |
| PV1-10 | Encounter.serviceType | 15 | adt 15 | adt/A01-004: Encounter.serviceType: esperado ('http://terminology.hl7.org/CodeSystem/service-type', '382') (de 'MED'), observado [('http://terminology.hl7.org/CodeSystem/v2-0069', 'MED')] | [CM table-hl70069-to-service-type] [G PV1_Encounter.csv:26] | sin hacer |
| PID-13 | Patient.telecom | 5 | adt 5 | adt/A1-A01-02: Patient.telecom 'ana@hosp.es' use: 'home' para 'NET', sin destino | [CM datatype-xtn-to-contactpoint] [CM table-hl70201/0202] [G PID_Patient.csv:22-25] | sin hacer |
| PID-14 | Patient.telecom | 5 | adt 5 | adt/A1-A01-02: Patient.telecom '925999888' system: esperado 'fax' (de 'FX'), observado 'phone' | [G MSG_ADT_A01.csv:15] PID → Patient[1] | sin hacer |
| PV1-2 | Encounter.class | 4 | adt 4 | adt/A1-A08-20: Encounter.class: esperado ('http://terminology.hl7.org/CodeSystem/v2-0004', 'C') (de 'C'), observado [(None, 'C')] | [CM table-hl70004-to-encounter-status] [CM table-hl70004-to-v3-actcode] [G PV1_Encounter.csv:5-6] | sin hacer |
| OBR-25 | DiagnosticReport.status | 2 | oru 2 | oru/ORU-B22: DiagnosticReport.status: esperado 'registered' (de 'I'), observado 'unknown' | [CM table-hl70123-queries-to-diagnostic-report-status] | sin hacer |
| PID-16 | Patient.maritalStatus | 2 | adt 2 | adt/A1-A01-02: Patient.maritalStatus: esperado ('http://terminology.hl7.org/CodeSystem/v3-MaritalStatus', 'L') (de 'A'), observado [('http://terminology.hl7.org/CodeSystem/v3-MaritalStatus', 'A')] | [CM table-hl70002-to-v3-maritalstatus] [G PID_Patient.csv:27] | sin hacer |
| OBX-11 | Observation.status | 1 | oru 1 | oru/ORU-B20: Observation.status: esperado 'entered-in-error' (de 'D'), observado 'cancelled' | [CM table-hl70085-to-observation-status] [G OBX_Observation.csv:43-48] | sin hacer |

### valor_imposible_convertido

Ninguno.

### recurso

| hecho | ruta | n | corpus | ejemplo | citas | contraste |
|---|---|---|---|---|---|---|
| OBX-3 | falta | 3 | oru 3 | oru/ORU-B10: falta la Observation del OBX 1.1 | [G MSG_ORU_R01.csv:67-69] | sin hacer |

### referencia_rota

Ninguno.

### fhir_invalido

Ninguno.

## Rechazos

No son de las ocho clases. Los que el adaptador declara que el proyecto no convierte van aparte; el juez los cuenta igual (Q-CV-D-13).

| n | declarado por el adaptador | ejemplo |
|---|---|---|
| 92 | sí | adt/A02-001: el conversor devolvió error 'java.lang.UnsupportedOperationException: Message type not yet supported ADT_A02\n\tat io.github.linuxforhealth.hl7.HL7ToFHIRConverter.convertToBundle(HL7ToFHIRConverter.ja |

Rechazos aceptables (Q-CV-D-7): 9: PID 1, PID-8 5, PV1 3.

## Pares mínimos del laboratorio

34 sondas escritas en el estudio para Microsoft y LinuxForHealth (`cv/cv3_minimos.py`). Un par que se reproduce aquí quiere decir que este conversor muestra el mismo mecanismo; uno que no, nada más que eso. Se reproducen 19 de 34.

| par | escrito para | objetivo | caso | control | se reproduce |
|---|---|---|---|---|---|
| M01-nm-punto-inicial | microsoft | OBX-5 valor_distinto | bundle/correcto/no sale | bundle/correcto/no sale | no |
| M02-genero-fuera-de-tabla | microsoft | PID-8 fhir_invalido | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| M03-pda-sin-muerte | microsoft | PID-30 dato_inventado | error/rechazo_incorrecto/no sale | error/rechazo_incorrecto/no sale | no |
| M03b-pda-en-a01 | microsoft | PID-30 dato_inventado | bundle/fallo_silencioso/no sale | bundle/fallo_silencioso/no sale | no |
| M04-pv1-8-repetido | microsoft | PV1-8 dato_perdido | bundle/fallo_silencioso/no sale | bundle/fallo_silencioso/no sale | no |
| M05-clase-b | microsoft | PV1-2 codigo_mal_mapeado | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| M06-obx-tras-nte | microsoft | OBX(2)-3 recurso_ausente | bundle/correcto/no sale | bundle/correcto/no sale | no |
| M06b-dos-nte | microsoft | OBX(2)-3 recurso_ausente | bundle/correcto/no sale | bundle/correcto/no sale | no |
| M06c-nte-al-final | microsoft | OBX(2)-3 recurso_ausente | bundle/correcto/no sale | bundle/correcto/no sale | no |
| M06d-tres-obx | microsoft | OBX(2)-3 recurso_ausente | bundle/correcto/no sale | bundle/correcto/no sale | no |
| M07-oru-sin-pid | microsoft | ['PID-3', 'PID'] referencia_rota | bundle/correcto/no sale | bundle/correcto/no sale | no |
| M08-estado-civil-t | microsoft | PID-16 dato_perdido | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| M10-pl9-descripcion | microsoft | PV1-3 dato_perdido | bundle/fallo_silencioso/no sale | bundle/fallo_silencioso/no sale | no |
| M09-ft-br | microsoft | OBX-5 valor_distinto | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/sale | no |
| L01-sin-location | linuxforhealth | PV1-3 dato_perdido | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| L02-estado-civil-a | linuxforhealth | PID-16 codigo_mal_mapeado | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| L03-pv1-10-med | linuxforhealth | PV1-10 codigo_mal_mapeado | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| L04-sad-2-3 | linuxforhealth | PID-11 valor_distinto | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| L05-genero-n | linuxforhealth | PID-8 valor_distinto | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| L06-obx-sin-tipo | linuxforhealth | OBX-3 recurso_ausente | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| L07-ft | linuxforhealth | OBX-5 dato_perdido | bundle/fallo_silencioso/sale | bundle/correcto/no sale | sí |
| L08-tm | linuxforhealth | OBX-5 dato_perdido | bundle/fallo_silencioso/sale | bundle/correcto/no sale | sí |
| L09-obx-11-d | linuxforhealth | OBX-11 codigo_mal_mapeado | bundle/fallo_silencioso/sale | bundle/correcto/no sale | sí |
| L10-obr-25-i | linuxforhealth | OBR-25 codigo_mal_mapeado | bundle/fallo_silencioso/sale | bundle/correcto/no sale | sí |
| L11-sn-rango | linuxforhealth | OBX-5 valor_distinto | bundle/fallo_silencioso/sale | bundle/correcto/no sale | sí |
| L12-sn-distinto | linuxforhealth | OBX-5 valor_distinto | bundle/fallo_silencioso/sale | bundle/correcto/no sale | sí |
| L13-pv1-52 | linuxforhealth | PV1-52 dato_perdido | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| L14-xpn-6-titulo | linuxforhealth | PID-5 dato_perdido | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| L15-xtn-12 | linuxforhealth | PID-13 dato_perdido | bundle/fallo_silencioso/no sale | bundle/fallo_silencioso/no sale | no |
| L16-cx-4-solo-nombre | linuxforhealth | PID-3 dato_perdido | bundle/fallo_silencioso/no sale | bundle/fallo_silencioso/no sale | no |
| L17-pid-30-no | linuxforhealth | PID-30 valor_imposible_convertido | bundle/fallo_silencioso/sale | bundle/fallo_silencioso/no sale | sí |
| L18-unidad-cwe-2 | linuxforhealth | OBX-6 valor_distinto | bundle/fallo_silencioso/sale | bundle/correcto/no sale | sí |
| R01-nulo-en-dtm | microsoft | MSH-9 error | bundle/fallo_silencioso/no sale | bundle/fallo_silencioso/no sale | no |
| R02-nm-cero-inicial | microsoft | MSH-9 error | bundle/correcto/no sale | bundle/correcto/no sale | no |

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
| Q-CV-D-3 | 196 | 196 |
| Q-CV-D-5 | 196 | 196 |
| Q-CV-D-9 | 196 | 196 |

## Convenciones

Diferencias que la guía admite y no cuentan: 6.

| hecho | firma | n |
|---|---|---|
| OBX-11 | Observation.status: <v> para <v> (sin destino en el ConceptMap) | 2 |
| OBR-25 | DiagnosticReport.status: <v> para <v> (sin destino en el ConceptMap) | 1 |
| OBX-5 | OBX-<n> repetido (<n>): forma admitida por la guía (MSG_ORU_R01.csv:<n>-<n>) | 1 |
| OBX-8 | Observation.interpretation <v> para <v>, fuera del ConceptMap | 1 |
| PID-8 | Patient.gender: <v> mapeado desde <v> en minúscula (AMB-CV-<n>) | 1 |

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
python3 cv/verificar_conversor.py linuxforhealth.json <salida> --artefactos <carpeta de artefactos>
```
