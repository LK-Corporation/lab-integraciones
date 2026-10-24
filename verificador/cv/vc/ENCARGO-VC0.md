> *Copia pública: se quitaron las alusiones al trabajo del autor y a su máquina. El resto es el original del laboratorio.*

# Encargo VC0: diseño de «verifica tu conversor en un comando» (etapa 18)

Diseñas, sin programar, una herramienta de línea de órdenes que permita a un tercero pasar su conversor HL7 v2 → FHIR por un
verificador determinista **con un fichero de adaptador y una orden**, sin escribir código. Quien la programe será otro modelo y
seguirá tu diseño. Responde en español.

## Dónde mirar

**Lee solo** el repositorio público (este). No leas nada fuera de él, no modifiques nada y no ejecutes red.

**Lo que tienes que entender:**
- **`verificador/README.md`:** qué es el verificador, los puntos de entrada `adt_conv` y `oru_conv`, y cómo se corren sus
  pruebas.
- **`verificador/conversion.py`:** el juez de conversiones. Mira la forma de la evidencia, las ocho clases y `verificar`.
- **`verificador/cv/correr_conversor.py`:** el arnés actual. Corre Microsoft y LinuxForHealth en una caja de Docker, con los
  dos conversores escritos en el código.
- **Cómo se juzga y se clasifica:** `verificador/cv/juzgar_cv2.py`, `verificador/cv/cv3_minimos.py` (genera los pares mínimos,
  caso y control, y los juzga) y `verificador/cv/cv3_clases.py`. Este último clasifica con reglas escritas a mano para esos dos
  conversores.
- **El estudio:** `verificador/RESULTADO-CONVERSORES.md` y `verificador/cv/RESULTADO-CV2.md`, para saber qué se obtuvo a mano.
- **El corpus público:** `verificador/a1/`, `verificador/bases_adt/`, `verificador/bases_oru.py` y los pares de
  `cv/cv3_minimos.py`.
- **La caja:** `verificador/cv/CV1.md`.

## La pregunta de la etapa (fija)

> ¿Puede un tercero pasar su conversor HL7 v2 → FHIR por el verificador con un fichero de adaptador y una orden, sin escribir
> código, y obtener el mismo juicio que obtuvo el laboratorio a mano en el estudio de conversores?

## Lo que no se negocia

1. **El código del conversor solo corre en una caja:** Docker sin red, sistema de ficheros de solo lectura, usuario sin
   privilegios, sin capacidades y sin nuevos privilegios.
2. **Solo biblioteca estándar de Python.** El adaptador es JSON.
3. **El juez no cambia.**
4. **Las pruebas se escriben en rojo antes del código**, y deben correr sin Docker. Para eso hace falta un conversor de juguete
   del propio laboratorio. Cómo se concilia eso con la condición 1 es una de tus decisiones.
5. **El control:** con adaptadores para Microsoft y LinuxForHealth, la herramienta debe dar caso por caso los mismos veredictos
   que el estudio, con el mismo juez.

## Lo que tienes que decidir y escribir

1. **El formato del adaptador.** Tienes que cubrir:
   - identidad y versión del conversor, y cómo se calcula su huella;
   - la caja: imagen, montajes y entorno;
   - cómo se invoca: un contenedor por mensaje o por lotes; cómo se elige la plantilla o el tipo de mensaje (Microsoft necesita
     el tipo de MSH-9); los marcadores de la orden;
   - cómo se lee la salida: un Bundle tal cual, o envuelto en otro JSON (Microsoft devuelve `{Status, FhirResource}`); cómo se
     distingue un error, una salida vacía y un fallo de la caja;
   - los límites de tiempo.

   Los dos adaptadores reales, el de Microsoft y el de LinuxForHealth, tienen que caber sin código extra. Escríbelos como
   ejemplo.
2. **La orden y sus pasos.** `verificar_conversor.py <adaptador.json> <salida>`, sus opciones, y qué hace en orden:
   - generar el corpus;
   - correr en la caja;
   - escribir las evidencias;
   - juzgar;
   - agregar;
   - el informe.
3. **El informe** (Markdown y JSON). Debe llevar:
   - las categorías por familia;
   - los mecanismos que cuentan, agrupados por las ocho clases, con un ejemplo y su cita;
   - los pares mínimos que se reproducen (caso sí y control no);
   - lo que no se juzgó.

   **Lo que la herramienta NO puede saber:** si una discrepancia ya la tiene declarada el proyecto. El informe tiene que
   decirlo y no aparentarlo.
4. **El conversor de juguete y las pruebas.** Numera las pruebas P-VC-1, 2… Para cada una, su control negativo y qué debe dar
   en rojo antes del código. Incluye:
   - adaptadores mal formados;
   - un conversor que devuelve error;
   - uno que no devuelve nada;
   - uno que tarda demasiado;
   - una salida envuelta;
   - el tipo de mensaje que elige plantilla;
   - que la caja se monte con todas sus restricciones (comprobable sin Docker, mirando la orden que se construye).
5. **El control con los dos conversores reales:** cómo se compara caso por caso con el estudio y qué se hace con una diferencia.
6. **Las preguntas de diseño para Jev** (Q-VC-D-1, 2…): solo las que ni la pregunta ni lo de arriba deciden, con dos o tres
   opciones cada una y tu recomendación aparte.
7. **Los límites** (L-VC-1, 2…) y **el plan:** las pruebas en rojo, el código, el control y la publicación.

## Qué devuelves

Un único documento de diseño, en Markdown, con estas secciones:
- las decisiones (S-VC-n, cada una con su porqué en una línea);
- el formato del adaptador, con los dos ejemplos completos;
- la orden;
- el informe;
- las pruebas;
- el control;
- las Q-VC-D;
- los límites;
- el plan.

Sé concreto: el programador no podrá preguntarte.
