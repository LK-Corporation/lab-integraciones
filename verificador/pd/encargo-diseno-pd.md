> *Copia pública: las rutas de la máquina del laboratorio van cambiadas por las relativas a su raíz, su nombre por «la máquina del laboratorio», los nombres de sus cuadernos por «los cuadernos del laboratorio» y la carpeta de trabajo del diseñador por `<carpeta de trabajo>`; las carpetas temporales (`/tmp/…`) y el resto van literales.*

Eres el diseñador a ciegas de una etapa de un laboratorio de integración sanitaria (HL7 v2 → FHIR R4). Tu trabajo es DISEÑAR, no
programar ni publicar nada. Escribe en español.

## Contexto

El laboratorio tiene un juez (`conversion.py` y sus hermanos) que juzga lo que devuelven conversores HL7 v2 → FHIR frente a la guía
HL7 v2-to-FHIR. En ADT_A01, la guía crea una Observation desde PD1-7 cuando viene, y el juez no la empareja con su campo: la toma
por la de un OBX, por orden, y sin OBX la cuenta como inventada. La pregunta, las condiciones, lo que se mide y el «hecho cuando»
están fijados en el ANTES y no se discuten. Tu trabajo es diseñar el arreglo del juez y cómo se comprueba que solo cambia eso.

## Lo que puedes leer (en la máquina del laboratorio, desde la herramienta Bash, SOLO LECTURA)

- **Lo fijado:** `fase12/ANTES-ETAPA-PD17.md`. Empieza por aquí. Y `RESULTADO-JUEZ.md` (la etapa 37, que
  tocó la misma zona del juez: los segmentos sin destino, ACC y PDA, y su regla de la 0136, L-CV-17).
- **El juez:**
  - `fase12/conversion.py`: la lectura del Bundle y el emparejamiento de los recursos de un ADT
    (`emparejar`, `_origen_sin_mapa` y lo que los rodea), el perfil «guía» de ADT, el juicio de los sobrantes (`_juzgar`) y las listas
    de decisiones y límites (S-CV, L-CV);
  - `conversion_vxu.py` y `conversion_mdm.py`, solo si tocan lo mismo.
- **Las pruebas del juez:** `prueba_conversion.py` (P-CV-30 y P-CV-32 son de la 37) y las que la acompañen. Mira cómo se escriben.
- **El rejuicio de la 37:** `jz/rejuicio_jz.py` y `jz/prueba_rejuicio_jz.py`, y `md/rejuicio_md.py`.
- **La integración continua:** `cv/ci/hacer_bases.py`, `base_nc.sh`, `cv/ci/CI.md` y `ejemplo-ci/ci/hacer_base.sh` en el clon público
  (`publicacion/`).
- **La guía:**
  - las hojas, en `fase12/cv/guia/*.csv` (en particular `MSG_ADT_A01.csv` y la del mapa de segmento de PD1 a
    la Observation de LivingWill);
  - los ConceptMap, en `estandares/v2mappings/package/`.
- **El texto de HL7 v2.5:** `estandares/hl7v2/HL7_Messaging_v25/txt/`.

**NO leas nada más.** En particular:
- ni `privado/`;
- ni las salidas de los conversores;
- ni otros `RESULTADO-*` que no sean los dos citados;
- ni los cuadernos del laboratorio.

No corras nada que escriba fuera de `/tmp/disenador40/`, ni Docker. Si quieres probar el juez en un caso, hazlo sobre una copia tuya
de `fase12` en `/tmp/disenador40/`, y borra al final lo que hayas creado, carpeta a carpeta, sin comodines.

## Lo que tienes que entregar: un documento de diseño

Escríbelo con la herramienta Write en
`<carpeta de trabajo>\pd\diseno-pd-fable.md`.
Va a publicarse. No pongas rutas de la máquina; usa las relativas a la raíz del laboratorio.

Tiene que decir:

1. **Qué hace el juez después,** con sus razones y sus citas (guía, v2.5, FHIR R4): cómo reconoce la Observation de PD1-7 (por su
   código, su valor, o ambos, según la hoja de la guía), qué juzga de ella (valor distinto, dato perdido, recurso ausente…), y qué
   pasa en cada caso:
   - PD1-7 con valor y la Observation como la crea la guía, con otro valor, o sin ella;
   - con OBX y sin OBX;
   - con ACC o PDA en el mismo mensaje (la regla de la 0136 de la 37);
   - en v2.5 y en otras versiones.
2. **Las decisiones abiertas,** si las hay, como preguntas para Jev, con sus opciones y los hechos de los dos lados.
3. **Las pruebas, en rojo antes:** qué casos sintéticos, en qué fichero y por qué caen con el juez de hoy.
4. **El rejuicio:** cómo se clasifica cada diferencia como de la conducta de PD1-7 o «fuera», mirando el caso y no solo la forma del
   hallazgo; y un control que siembre defectos con la forma de esa conducta que no lo sean.
5. **La previsión:** qué esperas del rejuicio de las evidencias guardadas y de las bases (ninguna evidencia de ADT guardada lleva
   PD1-7) y por qué.
6. **Lo que arrastra:** la huella, las bases, el pin del ejemplo, la información del juez (S-CV, L-CV y el texto de versión del
   servidor, que tiene una entrada por etapa) y las pruebas que fijan huellas.
7. **Lo que no resuelves y por qué,** si algo.

Sé concreto y breve. Nada de lo que propongas puede cambiar la frase del estudio de conversores (15 nuevas, 31 ya declaradas, 16
convenciones): si lo hiciera, dilo y para.
