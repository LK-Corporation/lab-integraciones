> *Copia pública: se quitaron las alusiones al autor. El resto es el original del laboratorio.*

# ANTES: etapa 26, MDM_T02 en el juez de conversores (FIJADO el 31-oct-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). Jev eligió un cuarto tipo
de mensaje con 0,82 y, de los tipos, MDM_T02 con 1,0 (`decision-jev-ruta9.md`, no publicada). La segunda opción, dar la ruta
por cerrada, quedó en 0,10.

## La pregunta (fija)

> ¿Encuentra el verificador, en la conversión de mensajes de documentos clínicos **MDM_T02** de los dos conversores del estudio,
> discrepancias con la guía v2-to-FHIR o con FHIR R4 que se sostengan con cita, que cambien el significado del dato y que el
> proyecto no tenga ya declaradas?

## Punto de partida (medido el 31-oct)

- **El juez juzga conversiones ADT, ORU^R01 y VXU^V04** (`adt_conv`, `oru_conv` y `vxu_conv`). La herramienta de la etapa 18 lleva
  a `adt_conv` todo lo que no es ORU ni VXU, así que un MDM saldría hoy como fuera de alcance.
- **La guía cubre MDM_T02.** Su paquete 1.0.0 trae siete ConceptMap:
  - el del mensaje, `message-mdm-t02-to-bundle`, con 22 elementos;
  - TXA hacia `DocumentReference` (15) y hacia `Provenance` (8);
  - OBX (6) y NTE (3) hacia `DocumentReference`;
  - los tipos ED (4) y RP (2) hacia `DocumentReference`.

  Las hojas CSV del commit del estudio (`873b331`) existen para el mensaje, TXA (las dos), OBX y NTE, pero no están descargadas.
- **El estándar:** el capítulo 9 de v2.5, que tiene el laboratorio, define MDM_T02 (§9.5.2) y TXA (§9.6.1). En v2.5 la
  estructura ya lleva el grupo de la orden (ORC, TQ1, OBR) antes de TXA y uno o más OBX, como la que mapea la guía.
- **Los conversores:**
  - los dos traen plantilla de MDM_T02: `MDM_T02.liquid` en Microsoft, y `MDM_T02.yml` y `DocumentReference.yml` en LinuxForHealth;
  - Microsoft publica tres muestras de MDM_T02 (dos en v2.8 y una en v2.3) con sus salidas esperadas;
  - LinuxForHealth trae mensajes MDM en los literales de sus pruebas Java.
- **El laboratorio no tiene bases de MDM.** El corpus hay que escribirlo.

## Condiciones que no se negocian

1. **Solo terceros públicos:** ningún sistema, dato ni material que no lo sea.
2. **El código de terceros corre en la caja de siempre:** Docker sin red, solo lectura, sin privilegios ni capacidades. Corre
   con `cv/verificar_conversor.py` y en las versiones fijadas del estudio (Microsoft v7.0, LinuxForHealth v1.1.0); al final,
   en sus ramas principales.
3. **Manda el estándar:**
   - HL7 v2 en la versión que declara el mensaje, FHIR R4 y la guía v2-to-FHIR en el commit leído;
   - una diferencia que el estándar permite es convención y no cuenta.
4. **El juez no cambia para ganar casos.**
   - Lo nuevo (el punto `mdm_conv` y su perfil «guía» de `DocumentReference`) entra con sus pruebas en rojo antes.
   - **Los veredictos de ADT, ORU y VXU no cambian:** el juicio de los corpus publicados con el juez nuevo da 0 diferencias.
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

## Eslabón débil (MD-pre, solo lectura)

| Sonda | Pregunta |
|---|---|
| E-MD-1 | ¿Dan las hojas y los ConceptMap de la guía un valor esperado con cita para cada campo de TXA y OBX que llega a `DocumentReference`? |
| E-MD-2 | ¿Qué mensajes MDM_T02 públicos hay (de los proyectos y de otras fuentes públicas), de qué versión, y cuántos acepta el juez? |
| E-MD-3 | ¿Corren los dos conversores con MDM_T02 en la caja, con sus adaptadores tal cual? ¿Qué estado devuelven? |
| E-MD-4 | ¿Publican los proyectos salidas esperadas o pruebas de MDM contra las que contrastar, e issues sobre MDM o `DocumentReference`? |

**Reglas de parada:**
- **Si la guía no da cita para TXA-2 (el tipo), TXA-12 (el identificador único), TXA-17 (el estado de compleción) ni OBX-5 (el
  contenido),** el perfil no tiene con qué juzgar lo esencial. La etapa se para y se declara.
  - **Por los ConceptMap del paquete, medido el 31-oct, pasa:** TXA-2 → `type`, TXA-12 → `masterIdentifier`, TXA-17 →
    `docStatus` y OBX-5 → `content.attachment`. Falta la cita por fila de las hojas CSV.
- **Si ningún conversor corre MDM_T02 en la caja** (E-MD-3), la etapa se para.

## Fases

| Fase | Qué |
|---|---|
| MD-pre | El eslabón débil: E-MD-1, 2 y 4 de solo lectura; E-MD-3 en la caja, sin juzgar |
| MD0 | El diseño, de Fable a ciegas: el punto `mdm_conv`, el perfil «guía» de `DocumentReference` y el corpus sintético. Las preguntas de diseño, a Jev |
| MD1 | Las pruebas en rojo antes del código; el juez, con el punto nuevo; el rejuicio de los corpus publicados sin diferencias; la herramienta, que lleve MDM a `mdm_conv`, con su control repetido |
| MD2 | El corpus, y la previsión sellada con la huella del juez. Después, las corridas y el juicio |
| MD3 | El contraste con lo que cada proyecto ya sabe, los pares mínimos y la revisión adversaria |
| MD4 | La rama principal, el cierre con la frase, y la publicación con la opción B |

## Hecho cuando

- **E-MD-1..4,** contestadas.
- **El juez** tiene el punto `mdm_conv` con sus pruebas, y sus suites siguen en verde. El rejuicio de ADT, ORU y VXU da 0
  diferencias.
- **Los dos conversores, juzgados** con la herramienta sobre el mismo corpus, con la previsión sellada antes.
- **Cada discrepancia que cuenta** lleva su cita, su contraste y su clase (nueva, ya declarada o convención), y se reproduce
  con un par mínimo.
- **`RESULTADO-MDM.md`** con la frase fija: «El verificador encuentra N discrepancias nuevas y confirmadas en MDM_T02 en K de 2
  conversores, sobre M mensajes públicos; además ve D de las ya declaradas, y C diferencias son convención».
- **Publicado con la opción B.**

## Tope

**Cuatro sesiones de trabajo, y siempre antes del 20-nov-2026,** que es la parada global de la hoja de ruta. Fable hace un
diseño y Jev decide las preguntas de diseño. Gasto externo: 0 USD.

## Regla de resultado (escrita antes de medir)

- **Si al llegar al tope no hay al menos una discrepancia nueva y confirmada en MDM_T02,** se declara así: el juez ve MDM y no
  encuentra nada que cuente. El resultado negativo se cierra con su frase y se publica igual, si Jev lo aprueba.
- **Si hay al menos una,** la etapa concluye que el juez encuentra algo también en documentos clínicos. Lo siguiente (issues,
  otra etapa) sigue la hoja de ruta.

## Fuera de la etapa

- Los otros eventos de MDM (T01 y T03 a T11), aunque T04, T06, T08 y T10 compartan la estructura MDM_T02. Pueden entrar como
  corpus secundario; su semántica de cambio de estado, no.
- El contenido del documento en sí: decodificar Base64, RTF o PDF y juzgar su texto. Se juzga cómo se lleva el contenido, no
  lo que dice.
- Los documentos dentro de ORU y las consultas de documentos.
- Cambiar los veredictos de ADT, ORU y VXU.
- La conversión inversa, FHIR → v2.
