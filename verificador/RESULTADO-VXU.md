> *Copia pública: se quitaron las alusiones al autor y la cola de lo que solo él decide. El resto es el original del laboratorio.*

# RESULTADO de la etapa de VXU (20): el verificador juzga la conversión de mensajes de vacunación VXU^V04, 25-oct-2026. Cerrada

**CERRADA.**

> El verificador encuentra **9 discrepancias nuevas y confirmadas en VXU_V04 en 2 de 2 conversores, sobre 125 mensajes públicos**;
> además ve **26 de las ya declaradas**, y **5 diferencias son convención**.

**Cómo se cuenta.** N y D cuentan mecanismos. C cuenta notas de convención del juez por conversor, hecho y firma, como en el
estudio de conversores: `primarySource` y `reportOrigin` deducidos de RXA-9 en los dos, e `isSubpotent` deducido de PA en
LinuxForHealth.

**La regla de resultado** se escribió antes de medir (`ANTES-ETAPA-VXU.md`). Pedía al menos una discrepancia nueva y confirmada; hay
9, y 5 son fuertes. La etapa concluye que **el juez encuentra algo también en vacunación**.

| | |
|---|---|
| Fecha | 25 de octubre, en la primera de las cuatro sesiones del tope (antes del 20-nov) |
| Conversores | **Microsoft FHIR-Converter:** v7.0 (`253307f`). **LinuxForHealth hl7v2-fhir-converter:** v1.1.0 (Maven Central). Son las mismas versiones y la misma caja del estudio de conversores: sin red, de solo lectura y sin privilegios |
| Referencia | Guía HL7 v2-to-FHIR 1.0.0 (hojas CSV de `873b331`, ConceptMap del paquete), HL7 v2.5 y FHIR R4 |
| Corpus | 125 mensajes públicos: 40 bases sintéticas válidas en v2.5 (`bases_vxu.py`, huella `5734cc3b9d6d`) y 85 muestras de los propios proyectos (4 de Microsoft y 81 sacadas de las pruebas de LinuxForHealth, casi todas 2.5.1 y 2.6) |
| Herramienta | `cv/verificar_conversor.py` (etapa 18), con VXU → `vxu_conv` |
| Juez de los resultados | `11a3754fb8b6`, servidor 1.3: «etapa de VXU (20)». La previsión se selló con el de `ec37fa7` |

## La pregunta, y la respuesta

> ¿Encuentra el verificador, en la conversión de mensajes de vacunación VXU^V04 por conversores de código abierto, discrepancias con
> la guía v2-to-FHIR o con FHIR R4 que se sostengan con cita, que cambien el significado del dato y que el proyecto no tenga ya
> declaradas?

**Sí: 9, en los dos conversores.** Cada una cumple cuatro condiciones:

- tiene su fila CSV o su ConceptMap;
- cae en una de las ocho clases que cambian el significado;
- no está en las salidas esperadas, las pruebas, la documentación ni los issues de su proyecto;
- se reproduce con un par mínimo de mensajes públicos, en el que el caso la muestra y el control no.

| Id | Conversor | Discrepancia | Guía | Par | Fuerza |
|---|---|---|---|---|---|
| VX-M15 | Microsoft | El `status` sale de RXA-18 (motivo de rechazo) y no de RXA-20. Una vacuna **rechazada (RE) o no administrada (NA)** sin RXA-18 sale **`completed`** | `RXA_Immunization.csv:25-26`; CM `table-hl70322-to-event-status` (RE, NA → not-done) | VM15 | fuerte |
| VX-L6 | LinuxForHealth | Con RXA-21 = D (registro **anulado**) sale `completed` y no `entered-in-error`: el registro borrado aparece como vacuna administrada | `RXA_Immunization.csv:27` | VL04 | fuerte |
| VX-M14 | Microsoft | RXA-6 `.5` se escribe 5: **la dosis se multiplica por diez**. Es la misma causa que M-24 del estudio de conversores, aquí en la dosis administrada | `RXA_Immunization.csv:9`; `CH02A.txt` (NM admite «.5») | VM14 | fuerte |
| VX-M7 | Microsoft | RXA-15 repetido (vacuna y diluyente) se concatena: `LOT-A+DIL-B`, un lote que no existe | `RXA_Immunization.csv:20` (RXA-15 → `lotNumber`, 0..1) | VM07 | fuerte |
| VX-M10 | Microsoft | NK1-3 GRD (tutor) da un `relationship.coding` sin código: la relación se pierde | CM `table-hl70063-to-v3-rolecode` (GRD, identidad v2-0063) | VM10 | fuerte |
| VX-M8 | Microsoft | El nombre del fabricante une CE.2 y CE.5 de RXA-17: `Merck--Merck S.A.` | CM `datatype-cwe-to-organization` (CWE.2 → `name`) | VM08 | débil |
| VX-M12 | Microsoft | De dos repeticiones de RXA-19 (indicación) solo una llega a `reasonCode` | `RXA_Immunization.csv:24` | VM12 | débil |
| VX-L9 | LinuxForHealth | Lo mismo que VX-M12 | `RXA_Immunization.csv:24` | VL07 | débil |
| VX-L8 | LinuxForHealth | De dos repeticiones de RXA-10 solo llega el primer profesional a `performer` | `RXA_Immunization.csv:13-15` | VL06 | débil |

**Lo que ya estaba declarado.** Las 26 ya declaradas, con su referencia exacta, están en `vx/CLASES-VX3.json`. Entre ellas:

- **Microsoft:** los systems ficticios (`example.com`) de CVX, MVX, la ruta y el sitio; la unidad perdida cuando RXA-7 no trae
  texto; las Observation de la vacuna sin `partOf`; y la fusión de dos grupos ORDER con el mismo id.
- **LinuxForHealth:** ORC-3 perdido, la ruta en v2-0162, NK1 sin convertir y los OBX absorbidos en la Immunization.

**Un hallazgo más, ya declarado con un matiz (VX-L14).** LinuxForHealth arrastra estado entre mensajes del mismo proceso.

- **El síntoma:** tras un mensaje con el fabricante sin código (RXA-17 = `^Laboratorio Sintetico^`), todos los siguientes salen sin
  `manufacturer`.
- **La prueba:** convertidos uno a uno, salen bien. La secuencia mínima lo reproduce: un mensaje así y luego uno normal.
- **Lo que declara el proyecto:** el síntoma está en su issue abierto #348, «Repeating messages do not completely reset internal
  variables». Su arreglo provisional no cubre este disparador.

## «Hecho cuando» (`ANTES-ETAPA-VXU.md`)

| Condición | Estado |
|---|---|
| E-VX-1..4 contestadas | ✅ `vx/VX-PRE.md` |
| El juez tiene `vxu_conv` con sus pruebas, las suites en verde, y el rejuicio de ADT y ORU da 0 diferencias | ✅ P-VX-1..23 (`prueba_conversion_vxu.py`). `prueba_conversion.py` (28) sin editar. `ve/comprobar.sh` verde, con la regresión de 2.721 en CASA. El rejuicio de las 1.008 evidencias del estudio de conversores da 0 diferencias, y las filas `adt`, `oru` y `minimos` del informe de la herramienta son idénticas a las publicadas |
| Los dos conversores, juzgados con la herramienta sobre el mismo corpus, con la previsión sellada antes | ✅ `vx/prevision-vxu.json`, sellada en `073870e` antes de juzgar; `vx/VX2.md` |
| Cada discrepancia con su cita, su contraste, su clase y su par mínimo | ✅ `vx/CLASES-VX3.json`; 25 de 26 pares confirmados (`vx/RESULTADO-VX3-minimos.json`); el que no, pasó a convención |
| `RESULTADO-VXU.md` con la frase fija | ✅ Este documento |
| Publicado con la opción B | la guarda, la higiene, la revisión a ciegas y Jev, en VX4 |

## La previsión sellada, frente a lo que salió

**Las categorías cayeron en su rango:**

| Categoría | Previsto | Microsoft | LinuxForHealth |
|---|---|---|---|
| `correcto` | 0-5 % | 0 % | 0 % |
| `fallo_silencioso` | 85-100 % | 100 % | 100 % |
| `rechazo_incorrecto` | 0-10 % | 0 % | 0 % |
| `indeterminado` | ≤ 2 % | 0 % | 0 % |

El `indeterminado` de Microsoft llegó a 2,5 % antes de arreglar el emparejador (F0 en `vx/VX2.md`).

**Los mecanismos previstos** cayeron dentro del rango de 6 a 11 en los dos (9 y 8). Sobre lo que pasó con cada previsión concreta:

- **La más probable del diseño,** la ruta en v2-0162 (MC-VX-1), salió en LinuxForHealth. El proyecto la tiene declarada.
- **El `primarySource` por omisión** (MC-VX-17, previsto con 0,95) no salió. En las muestras de E-VX-3 los conversores lo deducían
  de RXA-9, y las bases no lo llevan.
- **Mecanismos fuera de previsto:** hubo varios, y cada uno se adjudicó con cita en `vx/VX2.md`. Dos eran defectos del
  emparejador del juez (F0 y F0b) y se arreglaron. En la misma repetición se arregló la huella del juez, que no cubría el módulo
  nuevo (DV-VX-6).
- **La probabilidad de al menos una nueva confirmada** era 0,8 en alguno de los dos. Salió en los dos.
- **Las muestras públicas:** de lo que cuenta en ellas y es propio de VXU, es ya declarado el 83 % en Microsoft y el 100 % en
  LinuxForHealth, frente al 70 % previsto.

**La sensibilidad a las decisiones de Jev** (las siete de confianza baja, una a una): solo Q-VX-D-5, que deja NK1 fuera del perfil,
mueve la N. Ninguna nueva depende de una decisión de Jev.

## Qué cambió en el juez durante la etapa

| Fase | Commit | Qué |
|---|---|---|
| VX1-a | `f6c9825` | La gramática `VXU_V04` en `estructuras_25.json`, del texto de v2.5.1 (idéntico al de v2.5). DV-VX-1 |
| VX1-d | `7f84f47` | `conversion_vxu.py`: grupos ORDER, emparejamiento, perfil «guía» de Immunization, tablas de la guía comprobadas contra el paquete. Cinco ganchos en `conversion.py` que con ADT y ORU dan lo mismo que antes. El punto `vxu_conv`. DV-VX-2..4 |
| VX1-e | `2f08d24` | Con los primeros Bundles reales, dos defectos del emparejador: Observation por partOf antes que por código, y RelatedPerson de GT1/IN1 |
| VX2a | `3e11bae` | Una ruta local declarada ya no es valor imposible (base B29). DV-VX-5 |
| VX2-c, repetición 1 | `1ec2b64` | Emparejamiento de Immunization por claves para todos los grupos (B35), desempate de NK1 por la relación (B39) y la huella del juez que no cubría `conversion_vxu.py` (DV-VX-6) |
| VX3, rejuicio 1 | `f933020` | La revisión adversaria: DV-VX-7 (uris v2 de CVX/MVX), DV-VX-8 (`primarySource`/`isSubpotent` deducidos), DV-VX-9 (teléfono en `contactpoint-local`) y AMB-VX-13 |
| VX3 | `91e35bb` | Textos del perfil, INFO y REVISION. **Juez `11a3754fb8b6`** |

**Cada arreglo llevó su prueba, roja antes del arreglo.** El rejuicio final con `11a3754fb8b6` da los mismos veredictos que el de
`f933020` (rejuicio 1, juez `fa469425e04f`) en los 4 juicios.

**El juez que se publica** solo cambia un texto del servidor MCP respecto al de los resultados: la lista `REVISION` pasa a
L-VX-1..14 y AMB-VX-1..13. Ningún veredicto puede cambiar por eso. Sus huellas están en la cabecera de `MANIFIESTO.txt`.

## Lo que el resultado no dice

- **No es una certificación de conformidad.** Es lo que un juez determinista, con decisiones declaradas, ve en estos mensajes y en
  estas versiones.
- **Solo cubre VXU^V04** contra la guía base. Las reglas de la guía de inmunización de los CDC (RXA-9, el 999, los OBX de
  elegibilidad) no entran (L-VX-9). Por eso varias diferencias que un sistema de vacunación estadounidense espera se cuentan como ya
  declaradas o como convención.
- **Las versiones están fijadas.** Antes de reportar nada a un proyecto, hay que reproducirlo en su rama principal, como se hizo
  con el estudio de conversores (`cv/RESULTADO-15A.md`).
- **El contraargumento más probable de un tercero:** la página informativa de la guía pide revisar todos los mapas de terminología.
  Leída como licencia general, tumbaría la ruta y el sitio. Aquí la vara son los mapas base.
- **Los límites declarados siguen en pie** (L-VX-1..14 en `info_verificador`):
  - VXU se juzga con el perfil reducido de NK1 y sin PD1;
  - dos grupos ORDER idénticos no se distinguen (L-VX-14).
- **Queda una dudosa:** LinuxForHealth no da Immunization en las dos muestras 2.8 de Microsoft, y la causa no se separó en el tope.

## Lo que quedó para el autor

**Los issues en los proyectos.** Las nueve nuevas y el matiz del #348 de LinuxForHealth. Antes, hay que reproducirlos en la
rama principal de cada proyecto.

**Reproducidas el 25-oct en la rama principal de cada proyecto** (etapa 22): siguen las nueve y el arrastre, y ninguna estaba
reportada. Está en [`RESULTADO-RAMAS-VXU.md`](RESULTADO-RAMAS-VXU.md). Los borradores esperan en la cola del autor.

## Desviaciones y documentos de la etapa

| Fase | Documento | Desviaciones |
|---|---|---|
| VX-pre | `vx/VX-PRE.md` | — |
| VX0 | `vx/ENCARGO-VX0.md`, `vx/caja_vx0.py`, `vx/diseno-vx-fable.md`; las decisiones en `vx/estado_qvx.md`, `vx/preguntas_qvx.json`, `vx/decision-jev-qvx.md` y `vx/decisiones-qvx.md` | — |
| VX1 | `vx/VX1.md` | DV-VX-1..5 |
| VX2 | `vx/prevision-vxu.json`, `vx/VX2.md` | DV-VX-6; L-VX-14 |
| VX3 | `vx/VX3.md`, `vx/CLASES-VX3.json`, `vx/RESULTADO-VX3-minimos.json`, `cv/cv3_minimos_vxu.py` | DV-VX-7..9; AMB-VX-13 |
| VX4 | este documento | — |

**Sueltos, ninguno bloquea:**
- **Las muestras sacadas de las pruebas de LinuxForHealth** se re-extrajeron con un lexer que ignora los comentarios.
  - Pasaron de 79 a 81.
  - Dos mensajes se habían corregido a mano antes, y coinciden byte a byte con la re-extracción.
  - Una muestra (`CodeableConceptTest__L101`) es un esqueleto: la prueba mete por variable un trozo del mensaje.
  - Las 85 se juzgaron con el juez final: Microsoft 33 `correcto`, 50 `fallo_silencioso` y 2 rechazos; LinuxForHealth 25, 58
    y 2 `indeterminado` (`vx/VX2.md`).
- **El gasto externo** fueron las llamadas a Jev, por debajo de una milésima de dólar.
- **El teléfono de PID con solo XTN.7** (perfil de ADT) tiene la misma lectura que DV-VX-9. No se tocó, porque cambiaría los
  veredictos de ADT (fuera de la etapa).
