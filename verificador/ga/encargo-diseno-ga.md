> *Copia pública: las rutas de la máquina del laboratorio van cambiadas por las relativas a su raíz, y la de la carpeta de trabajo del diseñador, por `<carpeta de trabajo>`; el resto va literal.*

Eres el diseñador a ciegas de una etapa de un laboratorio de integración sanitaria (HL7 v2 → FHIR). Tu trabajo es DISEÑAR, no
programar ni correr nada. Escribe en español.

## Contexto

El laboratorio tiene generadores deterministas de mensajes HL7 v2.5 de prueba (ADT, ORU, VXU, MDM). Esos mensajes son los datos de
prueba de una herramienta que juzga conversores HL7 v2 → FHIR. Un validador (el de InterSystems IRIS, con el esquema 2.5, más una
lectura del texto de v2.5) ha encontrado que muchos no son válidos en v2.5. La etapa arregla los generadores en una **versión 2 del
corpus**, al lado de la versión 1, que no se toca. La fuente de la verdad es el texto de HL7 v2.5.

Las decisiones de alcance ya están tomadas y no se discuten:
- **El arreglo de ADT** cubre los obligatorios, las longitudes, la estructura, y además el tipo y la tabla de **cada campo que
  escriben los generadores**, según las tablas de atributos de v2.5.
- **Las unidades.** Los corpus de ORU y VXU siguen con UCUM en las unidades. Solo para una lista de mensajes (abajo, «gemelos»)
  se hace una copia con el sistema de unidades de v2.5 (ISO+; o ANS+ o local donde ISO+ no tenga la unidad).
- **Los 7 ejemplos del capítulo 3** se quedan como están, marcados como fragmentos del estándar, y se añaden 7 copias completadas
  con lo mínimo para ser válidas.
- **Versión nueva al lado.** La herramienta pasa a la versión 2, y lo sellado sigue leyendo la versión 1.
- **Los inválidos a propósito se quedan,** marcados en la lista del corpus: las bases A1 que dejan PV1-2 vacío, para una regla que
  tolera PV1-2 vacío; las que llevan valores fuera de tabla o en minúscula; las que llevan MSH-12 = 2.5.1.

## Lo que puedes leer (en la máquina del laboratorio, SOLO LECTURA)

- `estandares/hl7v2/HL7_Messaging_v25/txt/`: el texto de v2.5, entero.
- En `fase12/`:
  - `bases_adt/gen_adt.py` (GENADT: 216 bases, 8 eventos × 9 familias × 3, semilla 1; `bases(1)` reproduce `bases_e2.json` byte
    a byte) y `bases_adt/bases_e2.json`;
  - `a1/gen_bases_a1.py`, `a1/bases_a1.json` y `a1/ejemplos_cap3.json`;
  - `bases_mdm.py` (solo para la base B36) y `mev/bases_mdmev.py` (cómo se derivan T04, T06, T08 y T10 de cada base T02);
  - `estructuras_hl7.py` y `estructuras_25.json` (gramáticas de mensajes de v2.5);
  - `iv/tablas_iv.py` y `iv/TABLAS-TIPO-IV.json`, y `privado/iv/TABLAS-VALORES-IV.json` (las tablas y sus
    valores, sacados del texto de v2.5);
  - `cv/verificar_conversor.py`, **solo las líneas 400 a 475** (la función `generar_corpus`, que junta el corpus).
- `/tmp/ga_gemelos/`: los 23 mensajes para los gemelos (`Gnn-original.hl7`) y, cuando el mensaje es la mitad «caso» de un par
  mínimo, sus controles (`Gnn-control-k.hl7`).

**NO leas nada más.** En particular, ni `RESULTADO-*`, ni `ARTICULO.md`, ni `INFORME.md`, ni `publicacion/`, ni el resto de
`privado/`. Tampoco el resto de `cv/`, ni `vx/`, `md/`, `au/`, `ve/`, el resto de `iv/`, `verificador.py`, `mapeador_*.py`,
`oraculo_*`, ni ninguna salida de un conversor. El diseño tiene que salir del estándar, no de lo que hacen los conversores ni de lo
que juzga el juez. No corras nada que escriba, ni Docker, ni IRIS. Puedes leer con cat, sed, grep o un `python3 -c` que solo lea.

## Lo que encontró el validador en la versión 1 (los hechos de partida)

- **GENADT, las familias `completo`, `nulos` y `opcionales`** (72 mensajes; las demás familias salen válidas). Obligatorios vacíos:
  ROL-2, ROL-4, OBX-3, OBX-11, DG1-1, DG1-6, PR1-5, NK1-1, AL1-1, GT1-1 y GT1-3. El validador NO ve tipos de dato. A la vista hay
  errores de tipo que no marca: GT1-2 (CX) lleva un nombre y GT1-3 (XPN) una dirección; PR1-2 lleva «PR1»; UB1-2 (NM) lleva «B».
  Puede haber más.
- **A1:** PV1-2 vacío en 8 bases, a propósito. De sus otros campos, el validador no marcó nada, pero tampoco ve tipos.
- **Los 7 ejemplos del capítulo 3:** les faltan EVN, PV1 o PID, MSH-10, MSH-11 o MSH-12 y, en 4, PID-5.
- **MDM, B36:** TXA-12 lleva EI.1 a EI.4 a propósito y pasa el LEN 30. En los eventos T06 y T10 también TXA-13, que se forma con
  TXA-12 y «-PADRE».
- **Gemelos:** los 23 mensajes solo quedan sin decidir porque llevan UCUM en OBX-6 (ORU) o en RXA-7 (VXU), que la tabla 0396 de
  v2.5 no trae.

## Lo que tienes que entregar: un documento de diseño

Escríbelo con la herramienta Write en
`<carpeta de trabajo>\ga\diseno-ga-fable.md`.
Va a publicarse:
- cita el estándar como `FICHERO.txt:línea`, sin copiar pasajes largos (como mucho una frase corta entre comillas);
- puedes dar números de tabla, estructuras y valores de tabla;
- no nombres personas; si hace falta, «el autor».

Las secciones:

1. **GENADT v2.** Por cada segmento y campo que escribe (MSH, EVN, PID, PV1 y todos los opcionales), y por familia:
   - la fila de la tabla de atributos (SEQ, LEN, DT, OPT, TBL), con su cita;
   - el valor de la versión 1, y si es válido en tipo, tabla y longitud;
   - el valor de la versión 2, con su razón.
   Además:
   - el propósito de cada familia, sacado del código, y cómo lo conserva la versión 2. `nulos` usa `""`: di dónde puede ir un
     nulo y dónde no, con cita;
   - la regla de que los valores nuevos **no sacan números del azar**, y cómo se garantiza;
   - **la lista exacta de lugares (segmento-campo, por familia) que pueden cambiar entre la versión 1 y la 2**. Es la que
     afirmará la comprobación «solo cambia esto».
2. **A1 v2.** Sus errores accidentales de tipo o tabla, si los hay, con el arreglo. Y la lista de lo que hace a propósito, que
   se queda.
3. **Las copias completadas del capítulo 3:** por ejemplo, qué se añade, con qué valores y por qué es lo mínimo, y su id.
4. **B36 v2:** el TXA-12 nuevo, que conserva EI.2 a EI.4 y cabe en 30, y el TXA-13 que darán T06 y T10.
5. **Los gemelos:**
   - por cada `Gnn-original` y cada control, el campo de unidades de la versión 1 y el del gemelo, con el código ISO+ citado de
     la figura de v2.5 donde esté, o ANS+ o local, con su razón;
   - qué más tiene que quedar igual;
   - cómo se nombran.
6. **El comprobador de tipos.** Es un instrumento nuevo de medida:
   - las reglas por tipo de dato, para los tipos que aparecen en los campos que escriben los generadores de ADT, a nivel de
     componente donde el tipo lo defina; y la pertenencia a tabla, distinguiendo tablas de HL7 y de usuario;
   - qué cuenta como error y qué como aviso;
   - su control antes de usarlo: en la versión 1 tiene que encontrar los errores de tipo conocidos de arriba; cada regla con un
     mutante que tiene que cazar; y al menos un mutante válido que no debe cazar.
7. **La lista del corpus v2:** el esquema de cada fila (id, origen, versión, fichero, huella) y sus marcas (a propósito y por
   qué, fragmento del estándar, copia completada de, gemelo de).
8. **Cómo convive la versión 2 con la 1:**
   - los nombres de los ficheros y módulos nuevos;
   - cómo elige versión `generar_corpus`, con la 2 por omisión;
   - qué de la versión 1 no debe cambiar ni un byte (por ejemplo, `bases_mdm.py` lo leen resultados sellados).
9. **Las preguntas abiertas.** Lo que el estándar no decide y tiene que decidir otro. Por cada una, las opciones y los hechos de
   los dos lados, con su cita.

Al terminar, contesta con un resumen corto (diez líneas como mucho) y la lista de preguntas abiertas. El documento entero va en el
fichero, no en la respuesta.
