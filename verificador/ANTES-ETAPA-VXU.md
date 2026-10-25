> *Copia pública: se quitaron las alusiones al autor y la cola de lo que solo él decide. El resto es el original del laboratorio.*

# ANTES: etapa 20, VXU_V04 en el juez de conversores (FIJADO el 25-oct-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). Jev lo dejó como la
extensión siguiente tras la página (un tercer tipo de mensaje 0,42; de los tipos, VXU_V04 0,54; `decision-jev-ruta3.md`, no
publicada). El autor dio el visto bueno a arrancarla el 25-oct.

## La pregunta (fija)

> ¿Encuentra el verificador, en la conversión de mensajes de vacunación **VXU_V04** de los dos conversores del estudio,
> discrepancias con la guía v2-to-FHIR o con FHIR R4 que se sostengan con cita, que cambien el significado del dato y que el
> proyecto no tenga ya declaradas?

## Punto de partida (medido el 25-oct)

- **El juez solo juzga conversiones ADT y ORU^R01** (`adt_conv` y `oru_conv`). De VXU solo juzga el acuse, en circuitos.
- **La guía cubre VXU:**
  - en su paquete 1.0.0 hay ConceptMaps del mensaje (`message-vxu-v04-to-bundle`), de RXA, RXR y ORC hacia Immunization, y
    de las tablas 0322 (estado del registro), 0162 (vía) y 0163 (sitio);
  - las hojas CSV del mismo commit del estudio (`873b331`) no están descargadas.
- **El estándar:** el capítulo 4 de v2.5 que tiene el laboratorio define VXU_V04 (§4.17.6, con un ejemplo en §4.19.4) y RXA
  (§4.14).
- **Los conversores:**
  - los dos traen plantilla de VXU_V04: `VXU_V04.liquid` en Microsoft, `VXU_V04.yml` e `Immunization.yml` en LinuxForHealth;
  - Microsoft publica muestras de VXU (`VXU*.hl7`, `IZ_*.hl7`).
- **La herramienta de la etapa 18** decide el punto de entrada por MSH-9.1 (ORU → `oru_conv`, lo demás → `adt_conv`). Un VXU
  saldría hoy como fuera de alcance.
- **El laboratorio no tiene bases de VXU.** El corpus hay que escribirlo.

## Condiciones que no se negocian

1. **Solo terceros públicos:** ningún sistema, dato ni material que no lo sea.
2. **El código de terceros corre en la caja de siempre:** Docker sin red, solo lectura, sin privilegios ni capacidades. Corre
   con `cv/verificar_conversor.py` y en las versiones fijadas del estudio (Microsoft v7.0, LinuxForHealth v1.1.0); al final,
   en sus ramas principales.
3. **Manda el estándar:**
   - HL7 v2 en la versión que declara el mensaje, FHIR R4 y la guía v2-to-FHIR en el commit leído;
   - una diferencia que el estándar permite es convención y no cuenta.
4. **El juez no cambia para ganar casos.**
   - Lo nuevo (el punto `vxu_conv` y su perfil «guía») entra con sus pruebas en rojo antes.
   - **Los veredictos de ADT y ORU no cambian:** el juicio del corpus del estudio con el juez nuevo da 0 diferencias.
   - Los resultados sellados conservan la huella de su juez.
5. **El método del estudio:**
   - diseño a ciegas por otro modelo, que no vea lo que devuelven los conversores;
   - preguntas de diseño a Jev, con un estado neutro;
   - previsión sellada antes de correr nada;
   - contraste con lo que el proyecto ya sabe;
   - un par mínimo por cada nueva;
   - revisión adversaria;
   - la rama principal.
6. **Publicación con la opción B** (guarda, higiene, revisión a ciegas y Jev). Los issues en los proyectos siguen siendo
   del autor.

## Eslabón débil (VX-pre, solo lectura)

| Sonda | Pregunta |
|---|---|
| E-VX-1 | ¿Dan las hojas y los ConceptMap de la guía un valor esperado con cita para cada campo de RXA, RXR y ORC que llega a Immunization? |
| E-VX-2 | ¿Qué mensajes VXU públicos hay (de los proyectos y de otras fuentes públicas), de qué versión, y cuántos acepta el juez? |
| E-VX-3 | ¿Corren los dos conversores con VXU en la caja, con sus adaptadores tal cual? ¿Qué estado devuelven? |
| E-VX-4 | ¿Publican los proyectos salidas esperadas o pruebas de VXU contra las que contrastar? |

**Reglas de parada:**
- **Si la guía no da cita para RXA-5 (la vacuna), RXA-3 (la fecha) ni RXA-20 (el estado),** el perfil no tiene con qué juzgar
  lo esencial. La etapa se para y se declara.
  - **Por los ConceptMap del paquete, medido el 25-oct, pasa:** RXA-3 → `occurrenceDateTime`, RXA-5 → `vaccineCode` y
    RXA-20 → `status`, en un mapa de RXA de 18 elementos. Falta la cita por fila de las hojas CSV.
- **Si ningún conversor corre VXU en la caja** (E-VX-3), la etapa se para.

## Fases

| Fase | Qué |
|---|---|
| VX-pre | El eslabón débil: E-VX-1, 2 y 4 de solo lectura; E-VX-3 en la caja, sin juzgar |
| VX0 | El diseño, de Fable a ciegas: el punto `vxu_conv`, el perfil «guía» de Immunization y el corpus sintético. Las preguntas de diseño, a Jev |
| VX1 | Las pruebas en rojo antes del código; el juez, con el punto nuevo; el rejuicio del corpus del estudio sin diferencias; la herramienta, que lleve VXU a `vxu_conv`, con su control repetido |
| VX2 | El corpus, y la previsión sellada con la huella del juez. Después, las corridas y el juicio |
| VX3 | El contraste con lo que cada proyecto ya sabe, los pares mínimos y la revisión adversaria |
| VX4 | La rama principal, el cierre con la frase, y la publicación con la opción B |

## Hecho cuando

- **E-VX-1..4,** contestadas.
- **El juez** tiene el punto `vxu_conv` con sus pruebas, y sus suites siguen en verde. El rejuicio de ADT y ORU da 0
  diferencias.
- **Los dos conversores, juzgados** con la herramienta sobre el mismo corpus, con la previsión sellada antes.
- **Cada discrepancia que cuenta** lleva su cita, su contraste y su clase (nueva, ya declarada o convención), y se reproduce
  con un par mínimo.
- **`RESULTADO-VXU.md`** con la frase fija: «El verificador encuentra N discrepancias nuevas y confirmadas en VXU_V04 en K de 2
  conversores, sobre M mensajes públicos; además ve D de las ya declaradas, y C diferencias son convención».
- **Publicado con la opción B.**

## Tope

**Cuatro sesiones de trabajo, y siempre antes del 20-nov-2026,** que es la parada global de la hoja de ruta. Fable hace un
diseño y Jev decide las preguntas de diseño. Gasto externo: 0 USD.

## Regla de resultado (escrita antes de medir)

- **Si al llegar al tope no hay al menos una discrepancia nueva y confirmada en VXU,** se declara así: el juez ve VXU y no
  encuentra nada que cuente. El resultado negativo se cierra con su frase y se publica igual, si Jev lo aprueba.
- **Si hay al menos una,** la etapa concluye que el juez encuentra algo también en vacunación. Lo siguiente (issues, otra
  etapa) sigue la hoja de ruta.

## Fuera de la etapa

- Las consultas de vacunación (QBP, RSP) y los recursos ImmunizationEvaluation e ImmunizationRecommendation.
- Lo que añade la guía de implementación de inmunización de los CDC (v2.5.1) por encima del estándar. Sus mensajes de prueba
  públicos pueden entrar como corpus secundario; sus reglas, no.
- Cambiar los veredictos de ADT y ORU.
- La conversión inversa, FHIR → v2.
