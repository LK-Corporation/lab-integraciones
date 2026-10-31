# ANTES: etapa 28, los otros eventos de MDM (T04, T06, T08 y T10) en el juez de conversores (FIJADO el 31-oct-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). Jev la eligió con
0,73 (`decision-jev-ruta11.md`, no publicada); un
quinto tipo de mensaje quedó en 0,15.

## La pregunta (fija)

> En los eventos de MDM que comparten la estructura MDM_T02 (T04, cambio de estado; T06, añadido; T08, edición; T10, sustitución),
> ¿tratan los dos conversores el documento igual que en T02? Y donde no, ¿hay discrepancias nuevas con la guía o con FHIR R4,
> con cita, que cambien el significado del dato y que el proyecto no tenga declaradas?

## Punto de partida (medido el 31-oct)

- **El juez juzga MDM^T02** (`mdm_conv`, etapa 26). Ya trae la alternativa de Q-MD-D-1 (b): el mismo punto con T04, T06, T08 y
  T10, con una nota del evento (`conversion_mdm.PE_ALTERNATIVA_EVENTOS`). Hay cuatro bases secundarias escritas (S01..S04).
- **La guía** solo trae el mapa del mensaje MDM_T02. Esos cuatro eventos tienen la estructura MDM_T02 (v2.5 §9.5). La guía no da
  destino a TXA-13 (documento padre), TXA-14, TXA-15 ni TXA-21 (motivo del cambio). El sentido propio de cada evento queda, por
  tanto, sin cita.
- **v2.5** exige TXA-13 en T06 y en T10 (§9.6.1.13).
- **Los conversores:**
  - Microsoft trae plantillas de T06 y T10, pero no de T04 ni de T08;
  - LinuxForHealth trae las cuatro;
  - en las muestras públicas hay 29 T06 de LinuxForHealth (v2.6) y 2 T06 y 2 T10 de Microsoft (v2.8). LinuxForHealth no convierte
    los T10 de v2.8.

## Condiciones que no se negocian

1. **Las de la etapa 26:**
   - solo terceros públicos;
   - el código de terceros, en su caja;
   - manda el estándar;
   - el juez no cambia para ganar casos, y ADT, ORU, VXU y MDM^T02 no cambian (el rejuicio da 0 diferencias);
   - previsión sellada, contraste, pares mínimos y revisión adversaria;
   - publicación con la opción B.
2. **Cada mensaje del corpus es válido en v2.5 para su evento,** también en sus campos condicionales. Es la lección de la 26
   (TXA-22).
3. **Un conversor sin plantilla para un evento** da `sin_plantilla` (L-VC-13): no corre ese evento, y eso no es una discrepancia.
4. **No se juzga lo que la guía no mapea:** el documento padre, el motivo del cambio ni las transiciones de estado.

## Qué se mide

- **Por conversor y evento:** si corre el evento y con qué categorías.
- **Por base:** los hallazgos que cuentan en el evento frente a los de la misma base en T02. Las diferencias son lo propio del
  evento.
- **Las discrepancias nuevas y confirmadas,** con la regla de la 26 (contraste, revisión adversaria y par mínimo).

## Hecho cuando

- **El juez** juzga los cuatro eventos con su prueba, y el rejuicio de lo publicado da 0 diferencias.
- **Los dos conversores, juzgados** sobre el corpus de los cuatro eventos, con la previsión sellada antes.
- **`RESULTADO-MDMEV.md`** con la frase: «En T04, T06, T08 y T10, los conversores tratan el documento como en T02 salvo en D
  diferencias; de ellas, N son discrepancias nuevas y confirmadas en K de 2 conversores».
- **Publicado con la opción B,** con las líneas base de la integración continua rehechas si cambian el juez o el corpus.

## Tope

**Una sesión de trabajo,** y siempre antes del 20-nov-2026.

## Regla de resultado (escrita antes de medir)

- **Si no hay diferencias con T02,** se declara así: los conversores tratan el documento igual en los cinco eventos. Se publica
  igual.
- **Si las hay,** cada una se clasifica: nueva, ya declarada o convención.

## Fuera de la etapa

- T01, T03, T05, T07, T09 y T11, que tienen otra estructura.
- El sentido de los eventos: el documento padre, las transiciones de estado y el motivo del cambio.
