# Contrato del canónico ADT (`sesiones[].canonico_adt`, punto de entrada `adt_fhir`)

*Generado por `contratos/generar_contrato.py` desde `mapeador_adt.CONTRATO_CANONICO`, la misma fuente que lee el
verificador. No se edita a mano.*

Es lo que el circuito registra de cada mensaje antes de escribir en FHIR y que el verificador compara **literalmente** con
lo que esperaba. Reglas comunes:

- **Vacío es `""`**, nunca `null`, en lo esperado. Un `None` en lo esperado quiere decir «imposible»: ese campo no se
  juzga (S10).
- **Sin visita** (PV1-2 = N, `TieneVisita` = 0), **todos** los campos de visita van vacíos, también `ClaseCode`.
- **Los códigos van ya mapeados a FHIR**, por los ConceptMap oficiales v2-to-FHIR y las tablas indicadas, no crudos.
- **El mensaje se lee truncado** al LEN de v2.5 del punto de entrada (S3); si algo se truncó, `Truncado` = 1.

## cabecera (objeto)

| Campo | Origen HL7 | Tipo | Valor | Cita |
|---|---|---|---|---|
| `MsgControlId` | MSH-10 | texto | MSH-10 entero, truncado al LEN del punto | S3 |
| `SendingApp` | MSH-3 | texto | MSH-3.1 |  |
| `SendingFacility` | MSH-4 | texto | MSH-4.1 |  |
| `MsgEvent` | MSH-9 | texto | MSH-9.2 (el evento) |  |
| `ProcessingId` | MSH-11 | texto | MSH-11.1 escrito | DV-MI-7 |
| `VersionId` | MSH-12 | texto | MSH-12.1 ESCRITO; vacío si no viene (la versión asumida del perfil no entra) | DV-MI-6, S103 |
| `Estructura` | MSH-9 | texto | la estructura con que se lee el mensaje: MSH-9.3 o, si falta, la de la tabla 0354 | AMB-MT-1 |
| `Identifier` | PID-3 | texto | Patient.identifier.value: CX.1 de la repetición con CX.5 = MR (si no hay, la primera con CX.1), desescapado | S80 |
| `IdentifierTipo` | PID-3 | texto | CX.5 de esa repetición (Patient.identifier.type) |  |
| `NumIdentificadores` | PID-3 | entero | repeticiones de PID-3 con CX.1 |  |
| `FamilyName` | PID-5 | texto | XPN.1 de la repetición elegida (S74), desescapado | S74 |
| `GivenName` | PID-5 | texto | XPN.2 y XPN.3 de la repetición elegida (S74), unidos por un espacio | S74, DV-MI-3 |
| `Gender` | PID-8 | texto | código AdministrativeGender por la 0001 (ConceptMap oficial); None si es imposible | S22, S103 |
| `BirthDate` | PID-7 | texto | date FHIR con la precisión del TS de PID-7; None si es imposible | S8 |
| `DeceasedDateTime` | PID-29 | texto | dateTime FHIR con la zona del emisor; None si es imposible | S66 |
| `DeceasedBoolean` | PID-30 | texto | "true" o "false" por la 0136; vacío si no viene; None si es imposible |  |
| `MaritalCode` | PID-16 | texto | Patient.maritalStatus.coding.code por la 0002 |  |
| `MaritalSystem` | PID-16 | texto | Patient.maritalStatus.coding.system |  |
| `NumNombres` | PID-5 | entero | filas de «nombres» |  |
| `NumDirecciones` | PID-11 | entero | filas de «direcciones» |  |
| `NumTelecoms` | PID-13 | entero | filas de «telecoms» (PID-13 y PID-14) |  |
| `NumParticipantes` | PV1-7 | entero | filas de «participantes»; 0 sin visita |  |
| `TieneVisita` | PV1-2 | entero | 1 si hay Encounter; 0 con PV1-2 = N | S77 |
| `VisitaId` | PV1-19 | texto | Encounter.identifier.value (PV1-19.1); vacío sin visita o sin PV1-19 | S78 |
| `ClaseCode` | PV1-2 | texto | Encounter.class.code por la 0004 (v3-ActCode o v2-0004); vacío sin visita, no el mapeo de N; None si es imposible | DV-MI-4 |
| `ClaseSystem` | PV1-2 | texto | Encounter.class.system |  |
| `Estado` | PV1-2 | texto | Encounter.status (encounter-status), por el evento y PV1-45 |  |
| `TipoAdmision` | PV1-4 | texto | Encounter.type.coding.code |  |
| `Servicio` | PV1-10 | texto | Encounter.serviceType.coding.code |  |
| `OrigenIngreso` | PV1-14 | texto | Encounter.hospitalization.admitSource.coding.code |  |
| `DisposicionAlta` | PV1-36 | texto | Encounter.hospitalization.dischargeDisposition.coding.code |  |
| `Inicio` | PV1-44 | texto | Encounter.period.start, dateTime FHIR con la zona del emisor; None si es imposible | S66 |
| `Fin` | PV1-45 | texto | Encounter.period.end, dateTime FHIR con la zona del emisor; None si es imposible | S66 |
| `Ubicacion` | PV1-3 | texto | identifier de la Location: PL.1^PL.2^PL.3^PL.4.1 |  |
| `UbicacionDescripcion` | PV1-3 | texto | Location.description |  |
| `UbicacionPrevia` | PV1-6 | texto | identifier de la Location previa (completed) |  |
| `UbicacionPreviaDescripcion` | PV1-6 | texto | su description |  |
| `UbicacionTemporal` | PV1-11 | texto | identifier de la Location temporal |  |
| `UbicacionTemporalDescripcion` | PV1-11 | texto | su description |  |
| `Truncado` | longitud | entero | 1 si algún campo se truncó al LEN de v2.5; 0 si no | S3 |

## Auxiliares de la cabecera (no se comparan)

| Campo | Origen HL7 | Tipo | Valor | Cita |
|---|---|---|---|---|
| `Pid7Crudo` | PID-7 | texto | PID-7 crudo (para la causa y la ficha; no se compara) |  |
| `Pid8Crudo` | PID-8 | texto | PID-8 crudo (no se compara) |  |
| `ClaseCruda` | PV1-2 | texto | PV1-2 crudo (no se compara) |  |
| `VisitaIdTipo` | PV1-19 | texto | CX.5 de PV1-19 crudo (no se compara) |  |

## nombres (lista; el orden es dato)

| Campo | Origen HL7 | Tipo | Valor | Cita |
|---|---|---|---|---|
| `Orden` | PID-5 | entero | 1..n en el orden de las repeticiones con XPN.1, XPN.2 o XPN.3 | D-ADT-5 |
| `Family` | PID-5.1 | texto | FN.1..n unidos por un espacio, desescapados |  |
| `Given` | PID-5.2 | texto | XPN.2 entero | S96 |
| `Otros` | PID-5.3 | texto | XPN.3 entero | S96 |
| `Prefix` | PID-5.5 | texto | XPN.5 |  |
| `Suffix` | PID-5.4 | texto | XPN.4 |  |
| `Grado` | PID-5.6 | texto | XPN.6 |  |
| `Uso` | PID-5.7 | texto | XPN.7 mapeado por la 0200 a name-use de FHIR; vacío si no está en la tabla | DV-MI-2 |
| `Elegido` | PID-5 | entero | 1 en la repetición elegida por S74; 0 en las demás | S74 |

## direcciones (lista; el orden es dato)

| Campo | Origen HL7 | Tipo | Valor | Cita |
|---|---|---|---|---|
| `Orden` | PID-11 | entero | 1..n en el orden de Patient.address | D-ADT-5 |
| `Linea1` | PID-11 | texto | address.line[0] |  |
| `Linea2` | PID-11 | texto | address.line[1] |  |
| `Linea3` | PID-11 | texto | address.line[2] |  |
| `Linea4` | PID-11 | texto | address.line[3] |  |
| `Ciudad` | PID-11.3 | texto | address.city |  |
| `Provincia` | PID-11.4 | texto | address.state |  |
| `Codigo` | PID-11.5 | texto | address.postalCode |  |
| `Pais` | PID-11.6 | texto | address.country |  |
| `Uso` | PID-11.7 | texto | address.use de FHIR, ya mapeado | DV-MI-2 |
| `Tipo` | PID-11.7 | texto | address.type de FHIR, ya mapeado | DV-MI-2 |

## telecoms (lista; el orden es dato)

| Campo | Origen HL7 | Tipo | Valor | Cita |
|---|---|---|---|---|
| `Orden` | PID-13 | entero | 1..n: primero PID-13, luego PID-14 | D-ADT-5 |
| `Campo` | PID-13 | entero | 13 o 14 |  |
| `Valor` | PID-13 | texto | ContactPoint.value |  |
| `Uso` | PID-13 | texto | ContactPoint.use de FHIR, ya mapeado | DV-MI-2 |
| `Sistema` | PID-13 | texto | ContactPoint.system de FHIR, ya mapeado | DV-MI-2 |

## participantes (lista; el orden es dato)

| Campo | Origen HL7 | Tipo | Valor | Cita |
|---|---|---|---|---|
| `Orden` | PV1-7 | entero | 1..n en el orden de Encounter.participant; ninguno sin visita | D-ADT-5 |
| `Campo` | PV1-7 | entero | el campo de PV1 del que sale (7, 8, 17...) |  |
| `Id` | PV1-7 | texto | Practitioner.identifier.value (XCN.1) |  |
| `Family` | PV1-7 | texto | Practitioner.name.family (XCN.2) |  |
| `Given` | PV1-7.3 | texto | XCN.3 entero |  |
| `Otros` | PV1-7.4 | texto | XCN.4 entero |  |
| `Prefix` | PV1-7 | texto | Practitioner.name.prefix |  |
| `Suffix` | PV1-7 | texto | Practitioner.name.suffix |  |
