> *Copia pública: las rutas de la máquina del laboratorio van cambiadas por las relativas a su raíz, su nombre por «la máquina del laboratorio», los nombres de sus cuadernos por «los cuadernos del laboratorio» y la carpeta de trabajo del diseñador por `<carpeta de trabajo>`; las carpetas temporales (`/tmp/…`) y el resto van literales.*

Eres el diseñador a ciegas de una etapa de un laboratorio de integración sanitaria (HL7 v2 → FHIR R4). Tu trabajo es DISEÑAR, no
programar ni publicar nada. Escribe en español.

## Contexto

El laboratorio tiene un juez (`conversion.py` y sus hermanos) que juzga lo que devuelven conversores HL7 v2 → FHIR frente a la guía
HL7 v2-to-FHIR. Con él publicó un estudio de dos conversores: 15 nuevas, 31 ya declaradas y 16 convenciones, en
`cv/RESULTADO-CV3.md`, con las clases en `cv/cv3_clases.py`.

La etapa anterior encontró dos conductas que el juez cuenta mal. La pregunta, las condiciones, lo que se mide y el «hecho cuando»
están fijados en el ANTES y no se discuten. Tu trabajo es diseñar el arreglo del juez y cómo se comprueba que solo cambia eso.

## Lo que puedes leer (en la máquina del laboratorio, desde la herramienta Bash, SOLO LECTURA)

- **Lo fijado:** `fase12/ANTES-ETAPA-JUEZ.md`. Empieza por aquí. Y `RESULTADO-CANDIDATAS.md`, el de la etapa
  anterior, que encontró las dos conductas.
- **El juez:**
  - `fase12/conversion.py`: la lectura del Bundle y los sobrantes (líneas 270-420), el PID-8 (680-705), la
    función de tablas (858-900), el perfil (1530-1560) y el final del juicio (1490-1535);
  - `conversion_vxu.py` y `conversion_mdm.py`, solo si tocan lo mismo.
- **Las pruebas del juez:** `prueba_conversion.py` (y las que la acompañen) y `cv/ci/prueba_ci.py`. Mira cómo se escriben.
- **Las clases del estudio:** `cv/cv3_clases.py`. Cómo junta hallazgos en clases por mecanismo y firma, y en particular M-28 y las
  clases de PID-8. Un cambio de texto o de clase en el juez puede mover un caso de clase.
- **El rejuicio:** `md/rejuicio_md.py` (línea base, comparación y control).
- **La integración continua:** `cv/ci/hacer_bases.py`, `base_nc.sh`, `cv/ci/CI.md` y `ejemplo-ci/ci/hacer_base.sh` en el clon público
  (`publicacion/`).
- **La guía:**
  - las hojas, en `fase12/cv/guia/*.csv` (por ejemplo `PID_Patient.csv` y `MSG_ADT_A01.csv`);
  - los ConceptMap, en `estandares/v2mappings/package/`.
- **El texto de HL7 v2.5:** `estandares/hl7v2/HL7_Messaging_v25/txt/`.

**NO leas nada más.** En particular:
- ni `privado/`;
- ni las salidas de los conversores;
- ni otros `RESULTADO-*` que no sean los dos citados;
- ni los cuadernos del laboratorio.

No corras nada que escriba fuera de `/tmp/disenador37/`, ni Docker. Si quieres probar el juez en un caso, hazlo sobre una copia tuya
de `fase12` en `/tmp/disenador37/`.

## Lo que tienes que entregar: un documento de diseño

Escríbelo con la herramienta Write en
`<carpeta de trabajo>\jz\diseno-jz-fable.md`.
Va a publicarse. No pongas rutas de la máquina; usa las relativas a la raíz del laboratorio.

Tiene que decir:

1. **Qué hace el juez después en cada caso,** con sus razones y sus citas (guía, v2.5, FHIR R4):
   - un valor de PID-8 fuera de la 0001, convertido a un código FHIR válido, a uno no válido, o no convertido;
   - lo mismo en otras tablas de usuario que el juez trate distinto, si las hay;
   - un recurso que sale de un segmento que la guía no mapea en ese mensaje (ACC, PDA en ADT, u otros): cómo lo reconoce, qué texto
     da, qué cita y si cuenta o es nota.
2. **Las decisiones que dejes abiertas,** numeradas `Q-JZ-n`, con sus opciones escritas en neutro y lo que implica cada una. Las
   decide otro (Jev): no pongas tu preferencia dentro de la pregunta. Sí puedes dar aparte tu recomendación, con su porqué.
3. **El cambio en el código,** a nivel de funciones.
4. **Las pruebas, en rojo antes,** y dónde van.
5. **Lo que puede cambiar en las clases del estudio** (`cv/cv3_clases.py`): qué clases se mueven o se vacían, y cómo se decide.
6. **El rejuicio:**
   - cómo se hace la línea base con el juez de antes y la comparación con el nuevo;
   - cómo se reconoce que cada diferencia es de una de las dos conductas;
   - y el control: un defecto inyectado que la comparación tiene que ver.
7. **La integración continua:** qué bases se rehacen, en qué orden y en qué pushes, con el ensayo y la comprobación de cada uno.
8. **Los riesgos,** y lo que el arreglo no puede ver.

Sé concreto y no especules: lo que no hayas podido comprobar, dilo. Al terminar, contesta con un resumen de diez líneas como mucho y
la lista de las `Q-JZ-n`.
