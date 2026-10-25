# Estado: cuatro decisiones de diseño de la etapa 21, el arrastre de estado (25-oct-2026)

Redactado el 25-oct-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

Un laboratorio publicó un estudio de dos conversores HL7 v2 → FHIR R4 juzgados por un verificador determinista. Uno de los
conversores, LinuxForHealth, se corrió en lote: un solo proceso Java convertía todos los mensajes de cada carpeta, uno tras otro.
Después se vio, en mensajes de vacunación, que ese conversor arrastra estado entre mensajes del mismo proceso: tras un mensaje con
un fabricante sin código, todos los siguientes salen sin fabricante.

La etapa, ya fijada antes de medir, pregunta si cambia algún veredicto del estudio publicado cuando LinuxForHealth convierte cada
mensaje en su propio proceso. Lo fijado no se discute:
- el corpus del estudio son 436 casos (263 ADT, 40 ORU, 68 mensajes mínimos en pares caso/control, 65 muestras de los proyectos);
- el mismo juez a los dos lados;
- un control positivo y uno negativo antes de usar el aparato, y una previsión sellada antes de correr;
- si cambia algo publicado, se corrige en público con fe de erratas; si no, una nota;
- la etapa para si el control negativo da diferencias que no se pueden separar del arrastre;
- tope: una sesión de trabajo.

## El aparato, ya diseñado

- **Mensaje a mensaje** se corre con un segundo adaptador de la herramienta pública: el mismo conversor, la misma caja y la misma
  huella, un proceso por mensaje.
- **Cuatro corridas completas:** dos en lote (L1, L2) y dos mensaje a mensaje (M1, M2). Un caso es «diferente» solo si L1 = L2,
  M1 = M2 y L1 ≠ M1. Si las dos corridas de un mismo modo no coinciden, el caso es «no determinista».
- **El veredicto que se compara:** estado de la salida, categoría, subtipo y el conjunto de hallazgos que cuentan.
- **Además, el Bundle crudo:** se compara aparte, con los identificadores aleatorios normalizados, solo para medir el ruido de
  fondo y para ver arrastre que no cambia el veredicto. No entra en las cifras.
- **Cada diferencia se aísla** con una bisección sobre los mensajes anteriores del lote hasta una secuencia mínima, repetida 3 de
  3. Si no se aísla dentro del tope, queda «no aislada» y no corrige ninguna cifra.
- **Lo que se espera del ruido:** cero diferencias de veredicto entre dos corridas del mismo modo. Así salió un control anterior
  en lote, con 368 casos.
- **El recálculo de cifras:** el estudio publicado tiene sus resultados sellados con su huella. La página web del estudio lee cada
  cifra de un fichero publicado y sus pruebas exigen que cada cifra tenga fuente.

## Las preguntas

1. **El umbral de ruido de veredicto que para la etapa.** El marco dice que dos corridas del mismo modo tienen que salir iguales,
   o que el ruido se mide y se declara, y que la etapa para si no se puede separar del arrastre; no fija cuánto.
   - (a) cero: cualquier caso con veredicto distinto entre dos corridas del mismo modo para la etapa;
   - (b) hasta el 2 % de los comparados (8 de 436): se declaran como no deterministas y se restan; por encima, para;
   - (c) hasta el 5 % (21 de 436), como (b).
2. **Cómo entran las correcciones en lo publicado, si cambia algún caso.**
   - (a) en sitio con fe de erratas: se corrigen las filas de los ficheros de resultados publicados, cada uno con una marca de
     erratum y el valor original; la página se regenera;
   - (b) ficheros nuevos, y la página apunta a ellos: los resultados sellados quedan intactos salvo una cabecera; la página lee
     las cifras corregidas de los nuevos; la fe de erratas va en los documentos;
   - (c) ficheros nuevos, y la página no cambia sus cifras: lleva un aviso de erratum que enlaza el resultado.
3. **Qué adaptador de LinuxForHealth queda de referencia en la herramienta pública después de la etapa.**
   - (a) sigue el de lote; el de mensaje se publica al lado y se explica;
   - (b) pasa a serlo el de mensaje (el de lote se renombra), y el informe de ejemplo se regenera mensaje a mensaje;
   - (c) (a) si no cambia ningún caso y (b) si cambia alguno.
4. **Las diferencias de Bundle que no cambian el veredicto.**
   - (a) se aíslan, acotado: la secuencia mínima solo para el primer caso de cada campo afectado; los demás prueban ese culpable;
   - (b) solo se cuentan y se listan, sin aislar;
   - (c) no se miden, salvo para medir el ruido.
