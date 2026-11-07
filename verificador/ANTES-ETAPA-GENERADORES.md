> *Copia pública: el párrafo «Fijado en autónomo» marca como no publicadas la hoja de ruta y la decisión de ruta del laboratorio; el resto va literal. Lo que dice de MDM en «Por qué» lo corrige el resultado: solo vale para el contenido de texto.*

# ANTES: etapa 33, los generadores del corpus, arreglados (FIJADO el 5-nov-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). Jev la eligió con 0,51
(`decision-jev-ruta17.md`, no publicada); la segunda opción era pausar, con 0,30.

## La pregunta (fija)

> Con los generadores del corpus arreglados para que lo que escriben sea válido en v2.5 (estructura, obligatorios, longitudes,
> tipos y tablas), ¿cuántos mensajes de la versión nueva son válidos? Y, sobre esa versión, ¿cuántas de las 27 nuevas publicadas
> se reproducen en algún mensaje válido, y qué cambia en lo publicado de la línea de los conversores?

## Por qué

- **La etapa 30 dio 94 mensajes inválidos en los corpus del laboratorio.** De ellos, 78 son accidentales: 72 del generador de ADT
  y 6 de la base B36 de MDM. Otros 9 lo son a propósito (8 bases A1 con PV1-2 vacío, para S95, y el par L17). Los 7 restantes
  son los ejemplos del capítulo 3, fragmentos del propio estándar.
- **14 de las 27 nuevas no tienen ningún apoyo válido.**
  - 12 lo están solo porque sus mensajes llevan UCUM, que la 0396 de v2.5 no trae y que Q-IV-D-11 deja sin decidir. Ninguna de
    las 12 trata de unidades.
  - Las otras 2 son MD-L5 y MD-M5, por TXA-3. Ahí v2.5 se contradice (CH09.txt:825, 888-903) y no hay arreglo.
- **El corpus es lo que la herramienta da a quien la usa como datos de prueba.**

## Las decisiones (Jev)

Están en `ga/decision-jev-ga.md` y `ga/decision-jev-ga2.md`, con sus estados. Q-GA-2, 5 y 6 salieron con confianza por debajo
de 0,3 y se preguntaron otra vez, con los hechos que faltaban (sección 8 de `ga/estado_ga2.md`).

| | Decisión | Peso (confianza) |
|---|---|---|
| **Q-GA-1**, el alcance en ADT | También los tipos y tablas de cada campo que escriben los generadores, según sus tablas de atributos | 0,73 (0,46) |
| **Q-GA-2**, las unidades | Las bases siguen en UCUM; solo para el apoyo de las 12 se añade una copia con ISO+ (un gemelo) | 0,42 y 0,44 (0,13 y 0,16) |
| **Q-GA-3**, el capítulo 3 | Se quedan los 7 originales, marcados como fragmentos del estándar, y se añaden copias completadas | 0,59 (0,38) |
| **Q-GA-4**, la versión | Una versión nueva al lado de la vieja: la herramienta pasa a la nueva, y lo sellado sigue leyendo la vieja | 0,92 (0,84) |
| **Q-GA-5**, qué se rehace | La línea de los conversores: la herramienta y la CI, los estudios 14l, VXU y MDM, y la validación de la 30. La del circuito de IRIS y del verificador se declara como no rehecha | 0,47 (0,20); la primera vez, «solo el apoyo», 0,49 (0,24) |
| **Q-GA-6**, los inválidos a propósito | Se quedan, marcados como tales en la lista del corpus | 0,57 y 0,80 (0,14 y 0,60) |
| **Q-GA-7**, lo nuevo que dé el juez | Se anota como candidata, sin confirmarla en esta etapa | 0,68 (0,36) |

## Qué cambia: la versión 2 del corpus

1. **El generador de ADT (GENADT, 216 bases).**
   - Lo que escribe en cada segmento sigue su tabla de atributos de v2.5: los obligatorios con valor, cada valor de su tipo y
     los códigos de las tablas de HL7 dentro de la tabla.
   - Cada familia conserva su propósito. `nulos` sigue llevando `""`, pero no en lugar de un obligatorio.
   - Los valores nuevos no sacan números del azar. Con la misma semilla, lo demás de cada mensaje sale igual byte a byte, y
     una comprobación lo afirma campo a campo.
2. **Las 40 bases A1.** Lo mismo para sus errores accidentales, si los hay. Lo que hacen a propósito se queda: PV1-2 vacío (S95),
   valores fuera de tabla o en minúscula (S90 y S22) y MSH-12 = 2.5.1.
3. **El capítulo 3.** Los 7 originales siguen, y se añaden 7 copias completadas con lo mínimo que les falta para ser válidas.
4. **MDM.** En B36, TXA-12 cabe en su LEN 30 y conserva EI.2 a EI.4. Sus eventos de la 28 se derivan igual.
5. **Los gemelos con ISO+ (Q-GA-2).**
   - Son los 23 mensajes que sostienen las 12, y sus controles cuando son pares mínimos.
   - De cada uno solo cambia el campo de unidades: el sistema y el código de la unidad, a ISO+ (o ANS+ o local, donde ISO+ no
     tenga la unidad).
   - Una comprobación afirma que no cambia nada más.
6. **La lista del corpus.** Cada mensaje lleva su origen y su versión, y las marcas que le tocan: inválido a propósito (con su
   razón: S95, L-25 y M-35), fragmento del estándar, copia completada de un fragmento, o gemelo de otro mensaje.
7. **La herramienta** (`cv/verificar_conversor.py`) pasa a la versión 2. Lo sellado (`cv/corpus_cv2.py`, `ve/rejuicio.py`,
   `iv/`, …) sigue leyendo la 1, que no se toca.

**El diseño lo hace Fable, a ciegas.** Trabaja con el texto de v2.5 y los generadores, y no ve ni lo que hacen los conversores, ni
el juez, ni las discrepancias publicadas. También diseña el comprobador de tipos, que no existe: IRIS no ve los tipos de dato.
Yo implemento el diseño tal cual y declaro cada desviación (DV-GA-n).

## Qué se rehace (Q-GA-5)

1. **La validación de la 30 sobre la versión 2,** con el aparato sellado de la 30 y el comprobador de tipos nuevo.
2. **El estudio de conversores (14l)** sobre la versión 2:
   - los dos conversores corren en su caja, en lote, y los juzga el juez publicado;
   - se compara caso a caso con la versión 1, y por cada una de las 15 nuevas, las 31 ya declaradas y las 16 convenciones.
3. **VXU (20):** sus bases no cambian; se corren los gemelos de sus nueve.
4. **MDM (26 y 28):** se corre B36 en sus cinco eventos.
5. **La herramienta y la CI:**
   - la herramienta, con su corpus nuevo, y el control de la etapa 18;
   - las bases de `demo-ci`, rehechas;
   - el pin del ejemplo, movido.
6. **Lo que no se rehace, y se declara:**
   - la línea del circuito de IRIS y del verificador (la concordancia de A1 y el rejuicio de la 14k);
   - el arrastre (21).

## El control, antes de correr

- **El comprobador de tipos:**
  - en la versión 1 tiene que encontrar los errores de tipo ya conocidos de GENADT (GT1-2 y GT1-3, PR1-2 y UB1-2);
  - cada regla, con un mutante que tiene que cazar;
  - un mutante que no debe cazar (un control negativo de verdad).
- **La versión 2 frente a la 1:** solo cambian los campos que el diseño enumera. Los gemelos, solo el campo de unidades.
- **La validación de la 30 sobre la versión 2:** las únicas inválidas son las marcadas a propósito y los fragmentos originales.

## La previsión

Se sella antes de correr los conversores sobre la versión 2, con el aparato y la comparación ya escritos.

## Hecho cuando

- **La versión 2 del corpus,** con su lista y validada. La frase: «De los N mensajes de la versión 2, V son válidos, I inválidos
  (todos a propósito o fragmentos del estándar) y D sin decidir (TXA-3 y UCUM)».
- **Por cada una de las 27 nuevas,** su apoyo en la versión 2: si se reproduce en algún mensaje válido. Para las 12, en su
  gemelo.
- **Las cuentas de los estudios de la línea de los conversores,** en la versión 2 frente a la 1.
- **Las candidatas,** anotadas y sin confirmar.
- **La herramienta en la versión 2,** con la CI en verde sobre bases nuevas.
- **`RESULTADO-GENERADORES.md`,** publicado con la opción B.

## Tope y paradas

- **Tope:** dos sesiones. Sin agentes más allá del diseño de Fable y la revisión a ciegas, con hasta dos lectores.
- **Si el arreglo de GENADT obliga a sacar números nuevos del azar,** se para y se pregunta a Jev, porque cambiaría el resto de
  los mensajes.
- **Si las bases de la CI no caben en el tope,** la herramienta se queda en la versión 1 y se declara.
- **Las preguntas que el diseño deje abiertas** van a Jev, con sus hechos de los dos lados.
