> *Copia pública: se quitaron las alusiones al trabajo del autor y la cola de lo que solo él decide. El resto es el original del laboratorio.*

# RESULTADO de la etapa de conversores (14l): el verificador juzga conversores HL7 v2 → FHIR de código abierto, 24-oct-2026. Cerrada

**CERRADA.**

> El verificador encuentra **15 discrepancias nuevas y confirmadas en 2 de 2 conversores, sobre 368 mensajes públicos**;
> además ve **31 de las ya declaradas**, y **16 diferencias son convención**.

**No es pieza de portfolio.** La regla se escribió antes de medir (`ANTES-ETAPA-CONVERSORES.md`), y pide al menos una
discrepancia nueva y confirmada. Hay 15, y 7 son fuertes. Después del cierre se decidió publicar el estudio, y esta copia es esa publicación. Los issues en los proyectos
quedan para el autor.

| | |
|---|---|
| Fechas | 23 y 24 de octubre, dentro del tope (20-nov y cuatro sesiones) |
| Conversores | **Microsoft FHIR-Converter:** v7.0 (`253307f`), huella `766f8938…`. **LinuxForHealth hl7v2-fhir-converter:** v1.1.0 de Maven Central (DV-CV-3), huella `ac41f71b…`. Los dos corrieron en una caja sin red, de solo lectura y sin privilegios |
| Referencia | Guía HL7 v2-to-FHIR 1.0.0 (hojas CSV de `873b331`, ConceptMap del paquete), HL7 v2.5 y FHIR R4 |
| Corpus | 368 mensajes públicos (`aa83359a…`): ADT 263 (216 bases de E2, 7 fragmentos de cap. 3 y 40 de A1), ORU 40 y 65 muestras de los propios proyectos |
| Juez de los resultados | **CV2:** `be73697f…`. **CV3**, la clasificación y la frase: `54a90cd9…`. Los resultados sellados conservan su huella |
| **Juez nuevo** | **Huella `40bbc3ef439a…`, servidor 1.2**: «etapa de conversores (14l)» |
| Servicio | `verificador-mcp`, reiniciado el 24-oct a las 09:23. Comprobado por HTTP: contesta 1.2 y `40bbc3ef`, con la información de conversores |

## La pregunta, y la respuesta

> ¿Encuentra el verificador, en conversores HL7 v2 → FHIR de código abierto que el laboratorio no ha construido,
> discrepancias con la guía v2-to-FHIR o con FHIR R4 que se sostengan con cita, que cambien el significado del dato y que el
> proyecto no tenga ya declaradas?

**Sí: 15, en los dos conversores.** Cada una cumple cuatro condiciones:
- tiene su fila CSV o su ConceptMap;
- cae en una de las ocho clases que cambian el significado (S-CV-5);
- no aparece en ninguna salida esperada, prueba, documentación, comentario de plantilla, issue ni comentario de issue del
  proyecto;
- se reproduce con un par mínimo (caso y control) en la caja.

Una revisión adversaria independiente tumbó 10 de las 25 candidatas antes de contarlas. **Las siete fuertes:**

| Conversor | Qué hace | Por qué importa |
|---|---|---|
| Microsoft | Un NM «.5» se escribe **5** | El valor se multiplica por diez |
| Microsoft | Las ORU sin PID llevan un `subject` a «Patient/364bf61f…», que no está en el Bundle | El id es el mismo para todos los mensajes sin PID: resultados de pacientes distintos quedan colgados del mismo paciente inexistente |
| Microsoft | En una A02, un PDA vacío da `deceasedBoolean: true` | El mensaje no dice que el paciente haya muerto |
| LinuxForHealth | PID-16 «A» (separado) se escribe en v3-MaritalStatus como «A» | En v3, «A» es **anulado** |
| LinuxForHealth | Un OBX sin OBX-2 no da Observation | Desaparecen los resultados pendientes o no obtenibles («X», «I») |
| LinuxForHealth | Los valores FT y TM no se escriben | Se pierde el resultado |
| LinuxForHealth | El rango SN «1-5» se escribe como valueQuantity 1 | Un rango pasa a ser un número |

**Las otras 8:**
- **Microsoft:**
  - de PV1-8 repetido, solo llega la primera repetición;
  - PID-16 «T» se pierde.
- **LinuxForHealth:**
  - no hay Encounter.location;
  - se pierden SAD.2 y SAD.3;
  - PID-8 «N» se escribe «unknown»;
  - OBX-11 «D» se escribe «cancelled»;
  - OBR-25 «I» se escribe «unknown»;
  - PV1-52 se pierde.

Las citas, los casos y los pares están en `cv/RESULTADO-CV3.md` y en `cv/CLASES-CV3.json`.

**Las 31 ya declaradas son el control positivo:** el verificador ve lo que los proyectos ya saben. En Microsoft:
- el Encounter.location al componente menos granular (issue #624, abierto);
- el choque de id entre OBX con el mismo código (`docs/HL7v2-ImportantPoints.md`, punto 5) y el comparador «<>» (#504);
- el OBX que se pierde tras una NTE (#325).

En LinuxForHealth:
- el period.start desde EVN (su prueba `testEncounterPeriod`);
- los eventos A02, A11 y A13, sin soporte (README);
- el ContactPoint (#524).

## «Hecho cuando» (`ANTES-ETAPA-CONVERSORES.md`)

| Condición | Estado |
|---|---|
| E-CV-1..4 contestadas | ✅ E-CV-1, 2 y 4 en `RESULTADO-CV-PRE.md`. E-CV-3 en CV1 (`cv/CV1.md`): los dos corren aislados |
| Cada conversor, juzgado sobre el mismo corpus con la previsión sellada antes | ✅ Previsión sellada en `ed1c341` con el juez `63d40cd0` antes de correr nada (`cv/SELLO-CV2.txt`). Los dos conversores, sobre los mismos 368 mensajes (`cv/RESULTADO-CV2.md`) |
| Cada discrepancia que cuenta, con su cita, su contraste, su clase y un mensaje público que la reproduce | ✅ `cv/RESULTADO-CV3.md`. Clasificación caso a caso, sin ningún hallazgo sin clase. 34 pares mínimos: confirman 31, y los tres que no lo hacen son diagnósticos o retiran una candidata |
| Suites en verde; lo nuevo con sus pruebas; el juez de los resultados sellados no cambia | ✅ P-CV-1..28, siempre en rojo antes del código. `ve/comprobar.sh` entero en verde en cada cambio: la regresión de 2.721 en CASA, la concordancia de A1 sin cambios y el contrato del canónico IGUAL. Los arreglos de CV4 llegan después de sellar los resultados |
| `RESULTADO-CONVERSORES.md` con la frase fija | ✅ Este documento |

## La previsión sellada, frente a lo que salió

**Fable acertó la forma del resultado, pero no las proporciones.**

- **Las categorías de CV2 se fueron de rango.**
  - En ADT, los `correcto` fueron del 2 al 4 %, frente al 30-65 % previsto. Hay un mecanismo sistemático por conversor: la
    ubicación del Encounter.
  - Los rechazos fueron del 27 y el 35 %, frente a un tope del 5-10 %. En Microsoft, 30 son un defecto del corpus E2 (GT1
    desplazado). En LinuxForHealth, son eventos sin soporte.
- **La frase prevista se cumple entera:**

  | | Previsto | Salió |
  |---|---|---|
  | N | ≥ 2 | 15 |
  | K | 1 o 2 | 2 |
  | D | ≥ 3 | 31 |
  | C | ≥ 10 | 16 |

- **Las muestras aceptadas** (las 10 en que el juez espera AA, todas de Microsoft) son ya declaradas en un 80,6 % para Microsoft,
  que son sus propias pruebas; la previsión pedía al menos el 70 %. Las 52 muestras de 2.8 no dan ningún hallazgo de tabla ni de
  estructura (L18).

## Qué cambió en el juez durante la etapa

| Fase | Huella | Qué |
|---|---|---|
| CV1 | `63d40cd0` | `conversion.py` (lector, emparejamiento por papel, perfil «guía», ocho clases) y los puntos de entrada `adt_conv` y `oru_conv`. El juez de siempre, idéntico |
| CV2, repetición 1 | `be73697f` | J1 (PID-12 a district), J2 (el género en minúscula), J3 (status 1..1) y J5 (OBX-5 repetido) |
| CV3, rejuicios 1 y 2 | `198cebdd`, `54a90cd9` | DV-CV-13 (NM «5.»), DV-CV-14 (FT `\.br\`), DV-CV-15 (PV1-19 «VN») y DV-CV-16 (PL «^^») |
| **CV4** | **`40bbc3ef`**, servidor 1.2 | **CX.4 en system** se compara sin espacios ni signos: eran falsos positivos en los dos conversores. **Q-CV-D-14:** la descripción que contiene PL.9 sin ser PL.9 es `valor_distinto`. **Una referencia rota sin PID** lleva el hecho «PID». Se declaran L-CV-14..16, AMB-CV-10 y las preguntas abiertas. Pruebas P-CV-26..28 |

**El rejuicio informativo del corpus con el juez de CV4** (`cv/RESULTADO-CV4-rejuicio.json`) cambia solo lo previsto:
- desaparecen los tres falsos positivos de CX.4, y la muestra LRI de Microsoft pasa a `correcto`;
- 6 casos de PL.9 pasan a `valor_distinto`;
- ORU-B30 lleva el hecho «PID».

Ninguna discrepancia nueva aparece ni desaparece: M-36 y L-24 ya estaban apartadas, y M-4 es ya declarada en los dos jueces.
**La frase no cambia.**

## Lo que el resultado no dice

- **No es una certificación de conformidad.** Es lo que un juez determinista, con decisiones declaradas, ve en estos mensajes y
  en estas versiones.
- **Solo cubre ADT** (los 8 eventos de los puntos de entrada) **y ORU^R01.** SIU, MDM, VXU y los demás quedaron fuera de la
  etapa.
- **Las versiones están fijadas.**
  - LinuxForHealth se juzgó en la v1.1.0, la última en Maven Central. GitHub tiene una v1.1.1 y una rama principal que soportan
    más eventos.
  - De Microsoft se juzgó la v7.0, y su rama principal ha seguido.
  - **Antes de reportar nada a un proyecto, hay que reproducirlo en su rama principal.** Se hizo después del cierre
    (`cv/RESULTADO-15A.md`): siguen 14 de las 15, y la otra la corrigió LinuxForHealth en su rama principal.
- **Los límites declarados siguen en pie** (L-CV-1..16, `INFO.conversores` del MCP). Los que deja esta etapa:
  - L-CV-14: la legalidad solo se mira en lo que se proyecta;
  - L-CV-15: el emparejamiento ORU es por código;
  - L-CV-16: los tipos de datos son los de v2.5, aunque las muestras de los proyectos son sobre todo de 2.8;
  - AMB-CV-10: el sufijo «&IMP» de OBX-3.
- **Dos preguntas siguen abiertas:**
  - Q-CV-D-15, el formato del teléfono (Jev dio un empate);
  - Q-CV-D-16, el comparador «<>» que LinuxForHealth declara filtrar.

## Lo que quedó para el autor

1. **Qué se hace con el resultado.**
   - **Publicarlo:** el perfil «guía», `conversion.py` y este resultado. Lo prevé Q-CV-A-6: se prepara el diff y se publica con
     su visto bueno, la guarda en LIMPIO, y al día el README principal y el «About».
   - **Abrir issues en los proyectos:** primero hay que reproducir en la rama principal (punto de arriba).
   - **Otra etapa:** por ejemplo, Google Whistle (Q-CV-A-3, solo si sobraba tope), o los tipos que hoy solo se acusan.
2. **Q-CV-D-15 y Q-CV-D-16**, si se quieren cerrar.

## Desviaciones y documentos de la etapa

| Fase | Documento | Desviaciones |
|---|---|---|
| CV-pre | `RESULTADO-CV-PRE.md` | DV-CV-1 (BOM en muestras), DV-CV-2 |
| CV0 | `cv/diseno-conversores-fable.md`, `cv/decisiones-qcv.md`, `cv/decision-jev-qcv.md` | — |
| CV1 | `cv/CV1.md` | DV-CV-3 (LinuxForHealth v1.1.0) a DV-CV-9 |
| CV2 | `cv/PREVISION-CV2.md`, `cv/RESULTADO-CV2.md` | DV-CV-10 (CR sin BOM), DV-CV-11 (Microsoft fichero a fichero), DV-CV-12 (MSH-9 con los separadores del mensaje); la repetición 1 del juez |
| CV3 | `cv/RESULTADO-CV3.md` | DV-CV-13..16 (los rejuicios), DV-CV-17 (la revisión con Opus porque Fable dio error 500), DV-CV-18 (los issues completos y con comentarios) |
| CV4 | este documento | — |

**Sueltos, ninguno bloquea:**
- el generador de E2 desplaza GT1 en las familias «comp» y «opci»;
- el `serverInfo.title` del MCP sigue diciendo «Verificador ADT^A01 → FHIR Patient»: es anterior a los puntos de entrada nuevos;
- dos muestras de LinuxForHealth están mal formadas (MSH-2 con dos barras, OBX-3 vacío);
- el `inspeccionar_cv2.py` y los scripts de CV3 son de la etapa y no forman parte del juez.

## Después: mensaje a mensaje (etapa 21, 25-oct)

Este estudio corrió LinuxForHealth en lote, un proceso por carpeta, y en la etapa de VXU se vio que ese conversor arrastra
estado entre mensajes del mismo proceso. Convertidos mensaje a mensaje, con el mismo juez, **los 436 casos del estudio (los 368
mensajes y los 68 mínimos) dan los mismos veredictos que en lote**: ninguna cifra de este documento cambia. Está en
[`RESULTADO-ARRASTRE.md`](RESULTADO-ARRASTRE.md).
