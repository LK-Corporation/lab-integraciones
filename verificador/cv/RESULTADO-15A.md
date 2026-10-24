# 15a: las 15 nuevas en la rama principal de cada conversor (24-oct-2026)

**Hecho.**
- **Microsoft:** en `main`, siguen las 5 nuevas y los 2 rechazos.
- **LinuxForHealth:** en `master`, siguen 9 de las 10. **L-18** (OBX-11 «D» → «cancelled») **está corregida**, en el commit del
  10-feb-2026 «Observation Status Update». Ninguna versión publicada la lleva.

El proyecto confirmó la discrepancia por su cuenta, sin saber de este laboratorio, y la arregló.

Las dos ramas se construyeron desde su código, con red solo en ese paso. Corrieron en la caja de siempre: sin red, solo lectura,
`nobody` y sin capacidades. Los 34 pares mínimos se juzgaron con el juez de CV4, `40bbc3ef`. Construir los dos llevó 74
segundos, muy por debajo del tope de 1,5 h por conversor.

| | Microsoft | LinuxForHealth |
|---|---|---|
| Rama y commit | `main`, `70fd328` (3-jun-2026) | `master`, `2cb72c2` (11-feb-2026) |
| Cómo se construye | `dotnet publish` de la herramienta en `mcr.microsoft.com/dotnet/sdk:8.0` (`sha256:738f72af…`); `main` usa .NET 8, la v7.0 usaba .NET 6 | `./gradlew jar` en `maven:3.9-eclipse-temurin-11`, con un script de inicio (`copiar-libs.gradle`) que copia las 77 dependencias sin tocar el repositorio |
| Cómo corre | `mcr.microsoft.com/dotnet/runtime:8.0` (`sha256:1b2f288e…`), en la caja | El mismo arnés (`cv/lfh/Arnes.java`), compilado contra `master` |
| Huella | `38c6d32b…` | `28c16067…` |
| Lanzador | `CV_VARIANTE=main python3 cv/correr_conversor.py <conversor> cv/cv3/minimos <salida>` | igual |

**Antes de construir, se compararon las ramas con las versiones fijadas** (`gh api …/compare`):
- **Microsoft:** de v7.0 a `main` hay 30 commits, y **ninguno toca las plantillas HL7 v2** ni el analizador ni el postproceso.
  Cambian filtros de colecciones y segmentos, la conversión FHIR → v2 y la construcción.
- **LinuxForHealth:** de v1.1.0 a `master` hay 15 commits. Cambian la tabla de estados de Observation (D, I, R, S, X, U), el
  ContactPoint (su #524) y los estados de cita y de alergia.

## Cada nueva, en la versión fijada y en la rama principal

| Id | Conversor | Discrepancia | Versión fijada | Rama principal |
|---|---|---|---|---|
| M-24 | Microsoft | NM «.5» → 5 | sale | **sigue** |
| M-23 | Microsoft | ORU sin PID → subject a un Patient inexistente | sale | **sigue** |
| M-18 | Microsoft | A02 con PDA vacío → deceasedBoolean true | sale | **sigue** |
| M-7 | Microsoft | PV1-8 repetido → solo la primera | sale | **sigue** |
| M-10 | Microsoft | PID-16 «T» sin maritalStatus | sale | **sigue** |
| M-12 (rechazo) | Microsoft | rechaza «""» en un DTM | sale | **sigue** |
| M-15 (rechazo) | Microsoft | NM «01.20» → JSON inválido | sale | **sigue** |
| L-10 | LinuxForHealth | estado civil «A» → v3 «A» (anulado) | sale | **sigue** |
| L-15 | LinuxForHealth | OBX sin OBX-2 → sin Observation | sale | **sigue** |
| L-16 | LinuxForHealth | FT y TM sin valor | sale | **sigue** |
| L-20 | LinuxForHealth | SN rango → valueQuantity | sale | **sigue** |
| L-1 | LinuxForHealth | sin Encounter.location | sale | **sigue** |
| L-11 | LinuxForHealth | SAD.2 y SAD.3 perdidos | sale | **sigue** |
| L-12 | LinuxForHealth | PID-8 «N» → «unknown» | sale | **sigue** |
| L-18 | LinuxForHealth | OBX-11 «D» → «cancelled» | sale | **corregida** (`master` da «entered-in-error») |
| L-19 | LinuxForHealth | OBR-25 «I» → «unknown» | sale | **sigue** |
| L-22 | LinuxForHealth | PV1-52 perdido | sale | **sigue** |

**En los 68 mensajes, las dos ramas se diferencian solo en dos:**
- el caso de L-18;
- el control de L-15, que pasa a `correcto` porque `master` ya traduce OBX-11 «X» a «cancelled».

**Lo demás, comprobado igual:**
- los dos diagnósticos (el PDA en A01 y la NTE al final) dan lo mismo que en la versión fijada;
- la sonda de CX.4 (L-24) ya no sale en ninguna de las dos: era el falso positivo del juez, arreglado en CV4.

Resultados en `cv/RESULTADO-15A-minimos-fijada.json` y `cv/RESULTADO-15A-minimos-main.json`. Los artefactos están en
`privado/cv/conversores/ms-main/` y `lfh-main/`.

**Para el texto público y para los issues:** de las 15 nuevas, 14 siguen en la rama principal y una está corregida allí.
