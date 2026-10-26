# Estado: cinco decisiones de diseño para cerrar lo abierto de un flujo de integración continua (26-oct-2026)

Redactado el 26-oct-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

Un laboratorio publicó un flujo reutilizable de GitHub Actions que pasa un conversor HL7 v2 → FHIR por un verificador y falla
solo ante un hallazgo nuevo frente a la línea base del proyecto. Su demostración corre en el repositorio del laboratorio, que lo
llama con `uses: ./…` y con todo bajo su propia carpeta. Los tres controles salieron en verde.

**La etapa nueva recorre lo que no se recorrió:**
- **la llamada como la haría un tercero:** por referencia remota fijada a un commit, con su adaptador, su base y su corpus, y en
  el modo normal (falla ante lo nuevo);
- **las entradas que no se usaron:** un corpus propio, sustituir el del laboratorio, opciones de la herramienta y un artefacto
  completo con evidencias;
- **el evento `pull_request`;**
- **un run en rojo a propósito**, solo a mano, comprobado desde fuera.

También aplica cuatro endurecimientos que pidió una revisión.

**Condiciones fijas:**
- sin crear repositorios ni forks;
- nada en los proyectos de terceros;
- sin secretos y con permisos de solo lectura;
- cada push al repositorio público pasa por cuatro controles de publicación;
- el run en rojo solo corre a mano.

## Hechos

1. **Un proyecto de ejemplo:** un conversor pequeño en Python, en una imagen de Docker por digest, con seis mensajes
   sintéticos propios, su adaptador y su línea base. Lo llama un fichero de flujo que usa la forma remota fijada al commit que
   publica el flujo endurecido. Por eso hacen falta al menos dos pushes.
2. **Dónde puede vivir el ejemplo:**
   - en una carpeta propia en la raíz del repositorio, que un tercero copiaría tal cual; hay que admitirla en la higiene del
     repositorio, que hoy fija las carpetas de la raíz;
   - o dentro de la carpeta del verificador, junto a la etapa.
3. **El evento `pull_request` solo se recorre con un PR.** Sin forks, tiene que ser una rama del propio repositorio:
   - una opción lleva a esa rama el commit del resultado y la integra en la principal por avance rápido, sin commit de fusión;
   - otra abre un PR con un cambio trivial y lo cierra sin fusionar;
   - o se declara sin recorrer.
4. **El run en rojo siembra un defecto en el conversor del ejemplo:**
   - la etapa anterior ya probó en el runner un dato perdido (la fecha de nacimiento);
   - un valor distinto (el sexo F que sale como masculino) sería un tipo nuevo para el runner;
   - los dos en dos runs a mano duplican el coste y la comprobación.
5. **Comprobar el rojo desde fuera:**
   - el artefacto del flujo existe aunque el job falle, y se puede descargar desde otro job;
   - no se sabe si GitHub propaga las salidas de un job llamado que falla;
   - el control de la etapa anterior usó las salidas, porque allí el job no fallaba.
6. **Las entradas sin recorrer** se pueden recorrer:
   - en una segunda llamada, con su propia base, cada una con un efecto que se ve desde fuera;
   - o en la única llamada, que no puede quitar el corpus del laboratorio y usar a la vez el suyo con la misma base;
   - o solo en el run en rojo.

## Las preguntas

1. ¿Cómo se recorre `pull_request`?
2. ¿Dónde vive el proyecto de ejemplo?
3. ¿Qué defecto siembra el run en rojo?
4. ¿Qué decide en la comprobación del rojo?
5. ¿Cómo se recorren las entradas que no se usaron?
