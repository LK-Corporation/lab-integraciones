> *Copia pública: se quitaron las alusiones al autor y a su máquina. El resto es el original del laboratorio.*

# Encargo AR0: diseño del aparato de la etapa 21, el arrastre de estado de LinuxForHealth en el estudio publicado

Diseñas, sin programar, el aparato de medida de una etapa ya fijada. Quien lo programe será otro modelo y seguirá tu diseño al
pie de la letra; no podrá preguntarte. Responde en español.

## Dónde mirar

**Lee solo** estas dos cosas:
- `ANTES-ETAPA-ARRASTRE.md`, en una carpeta aparte: la etapa, fijada antes de medir. Es tu marco: la pregunta, las condiciones, lo que se
  mide, el «hecho cuando», el tope y la regla de parada no se negocian.
- el repositorio público, este (sobre todo `verificador/`).

No leas nada fuera de esas dos rutas, no modifiques nada, no ejecutes Docker ni Java, no corras conversores y no uses la red.
Puedes leer y correr `python3` solo para inspeccionar (por ejemplo, listar casos), nunca para escribir fuera de esa carpeta aparte.

**Lo que tienes que entender:**
- **`verificador/cv/verificar_conversor.py`:** la herramienta del estudio. Lee un adaptador JSON, corre el conversor en una caja
  de Docker, escribe evidencias, las juzga con el juez (`conversion.py`, sin tocarlo) y agrega. Mira sus dos modos de invocación
  (`lote` y `mensaje`, con `contenedor` `por_mensaje` o `por_grupo`), `agrupar`, la validación del adaptador, la huella del
  conversor, `--comparar` y `_valor`, y `--desde-evidencias`.
- **`verificador/cv/adaptadores/linuxforhealth.json` y `verificador/cv/lfh/Arnes.java`:** cómo corre LinuxForHealth: un
  contenedor y un solo proceso Java por carpeta, que convierte los ficheros en orden alfabético con el mismo objeto
  `HL7ToFHIRConverter`.
- **`verificador/cv/correr_conversor.py`:** cómo corrió el estudio original, antes de la herramienta.
- **`verificador/cv/VC.md` y `verificador/cv/vc/`:** el control de la etapa 18, que comparó caso por caso la herramienta con el
  estudio.
- **El arrastre ya visto:** `verificador/vx/VX2.md`, fila F7, y la secuencia VL11 en `verificador/cv/cv3_minimos_vxu.py`
  (`SECUENCIAS`, modo `secuencias`).
- **Lo publicado que podría cambiar:** `verificador/RESULTADO-CONVERSORES.md`, `verificador/cv/RESULTADO-CV3.md`,
  `verificador/cv/CLASES-CV3.json`, `verificador/cv/RESULTADO-CV3-minimos.json`, la página (`docs/conversores/` y su generador
  `codigo/hacer_pagina_conversores.py`) y `ARTICULO.md`.
- **El corpus:** cómo genera la herramienta las bases ADT, las ORU, los 68 mínimos (`cv/cv3_minimos.py`) y cómo entran las
  muestras de los proyectos (`--muestras`). Las muestras no están en el repositorio público: solo su forma.

## Lo que tienes que decidir y escribir

1. **Cómo se corre LinuxForHealth mensaje a mensaje** sin cambiar el juez, con la misma versión del conversor y la misma caja.
   Decide si basta un adaptador en modo `mensaje` (y qué orden lleva, dado que el arnés lee una carpeta), si hace falta otro
   arnés, o si se corre la herramienta sobre carpetas de un solo mensaje. Ten en cuenta:
   - que la clave de `--comparar` es `(conversor, corpus, caso)` y que los 68 mínimos solo entran con los identificadores del
     estudio;
   - la huella del conversor (qué partes cubre, y si un arnés nuevo la cambia);
   - el coste: unos 440 procesos Java, cada uno con su arranque.

   Escribe el adaptador o el procedimiento completo.
2. **La comparación caso a caso.** Qué se compara (el ANTES dice estado, categoría, subtipo y hallazgos que cuentan), con qué
   código, y cómo se tratan los casos que están en un lado y no en el otro. Decide si se compara también el Bundle crudo, y para
   qué.
3. **El control positivo** (VL11): procedimiento exacto, qué se compara y qué cuenta como «sale». Di si un solo positivo basta,
   o si hace falta otro dentro de los corpus ADT u ORU, sembrado, para saber que el aparato ve el arrastre allí y no solo en VXU.
4. **El control negativo:** en qué modo o modos, sobre qué población, cuántas corridas, y cómo se mide y se declara el ruido de
   fondo (por ejemplo, identificadores aleatorios en los textos de error). Di qué resultado del negativo dispara la regla de
   parada.
5. **La adjudicación de cada diferencia:** arrastre, no determinismo u otra causa. En particular:
   - cómo se reproduce una diferencia por arrastre con una secuencia mínima: qué mensajes previos del lote se prueban, en qué
     orden y con qué búsqueda (por ejemplo, bisección sobre los anteriores en el orden del lote), y cuándo se da por
     reproducida;
   - cómo se separa del no determinismo (qué se repite y cuántas veces);
   - qué se hace si la causa no se aísla dentro del tope.
6. **Cómo se pasa de diferencias de casos a cifras publicadas:** qué cifras de cada documento podrían cambiar y cómo se
   recalculan sin tocar el juez. Fíjate en qué depende de un caso concreto (un par mínimo, un mecanismo de `CLASES-CV3.json`, un
   recuento) y qué es agregado.
7. **Las pruebas en rojo antes del código** (P-AR-1, 2…), para todo el código nuevo, con su control negativo y qué deben dar en
   rojo. Deben correr sin Docker.
8. **Las preguntas de diseño para Jev** (Q-AR-D-1, 2…): solo las que ni el ANTES ni lo de arriba deciden, con dos o tres
   opciones cada una y tu recomendación aparte.
9. **Los límites** (L-AR-1, 2…): lo que este aparato no puede ver. Por ejemplo, si el orden del lote influye y cuál fue el orden
   del estudio.
10. **El plan,** en pasos, respetando el tope del ANTES: la previsión sellada va antes de la primera corrida del corpus.

## Qué devuelves

Un único documento de diseño, en Markdown, con estas secciones:
- las decisiones (S-AR-n, cada una con su porqué en una línea);
- cómo se corre mensaje a mensaje, con el adaptador o el procedimiento completo;
- la comparación;
- los controles, positivo y negativo;
- la adjudicación;
- de las diferencias a las cifras publicadas;
- las pruebas;
- las Q-AR-D;
- los límites;
- el plan.

Sé concreto: nombres de ficheros, opciones, formatos y órdenes. El programador no podrá preguntarte.
