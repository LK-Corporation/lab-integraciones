> *Copia pública: se quitaron las alusiones al autor y a su máquina. El resto es el original del laboratorio.*

# ANTES: etapa 21, el arrastre de estado de LinuxForHealth en el estudio publicado (FIJADO el 25-oct-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). El autor pidió elegir la
siguiente etapa con Jev, y Jev eligió esta (0,82; confianza 0,78; la segunda, las nueve de VXU en las ramas principales, 0,18;
`decision-jev-ruta4.md`, no publicada).

## La pregunta (fija)

> ¿Cambia algún veredicto del estudio de conversores publicado cuando LinuxForHealth convierte cada mensaje en su propio proceso,
> en vez de todos en un solo proceso, como se hizo en el estudio?

## Punto de partida (medido el 25-oct)

- **El arrastre existe.** En la etapa de VXU, LinuxForHealth v1.1.0, convirtiendo una carpeta en un solo proceso, arrastró estado
  entre mensajes: tras uno con RXA-17 sin código, todos los siguientes salieron sin `manufacturer`. Mensaje a mensaje, no
  (`vx/VX2.md`, F7; la secuencia mínima VL11 en `cv/cv3_minimos_vxu.py`). Es el síntoma de su issue abierto #348.
- **El estudio corrió LinuxForHealth en lote:** `cv/correr_conversor.py` y el adaptador de la herramienta lanzan
  `Arnes <entrada_dir> <salida_dir>`, un proceso por carpeta. Fue así sobre el corpus ADT (263), ORU (40) y los 68 mínimos, y
  sobre las muestras (65). Nunca se comparó con mensaje a mensaje.
- **Microsoft no puede arrastrar estado entre mensajes:** su adaptador lanza un proceso `dotnet … convert` por fichero.
- **La herramienta no tiene modo mensaje a mensaje.** Hoy se consigue corriéndola sobre carpetas de un solo mensaje, que es como
  se hizo en VXU.

## Condiciones que no se negocian

1. **Solo terceros públicos.**
2. **El código de terceros corre en la caja de siempre**, en la versión fijada del estudio (LinuxForHealth v1.1.0, el jar de
   Maven Central).
3. **El mismo juez a los dos lados.** Se compara lote frente a mensaje a mensaje con un solo juez, así que una diferencia solo
   puede venir de la salida del conversor.
4. **El aparato se prueba antes de usarlo.**
   - **Control positivo:** la secuencia VL11 tiene que salir distinta en lote y mensaje a mensaje.
   - **Control negativo:** dos corridas en el mismo modo tienen que salir iguales, o la diferencia de fondo se mide y se declara
     (identificadores aleatorios en los textos de error, ya conocidos de la etapa 18).
5. **Si cambia algo publicado, se corrige en público**, con fe de erratas y la opción B. Nada se calla.

## Qué se mide

- **El corpus:** el del estudio, ADT (263), ORU (40), los mínimos (68) y las muestras (65).
- **La comparación:** caso a caso, el estado de la salida, la categoría, el subtipo y los hallazgos que cuentan (hecho y
  subtipo), con el mismo juez en lote y mensaje a mensaje.
- **Cada diferencia se adjudica:**
  - arrastre: se reproduce con una secuencia mínima;
  - no determinismo: sale distinta también en dos corridas del mismo modo;
  - u otra causa, que se busca.
- **Si hay arrastre, se dice qué cifras publicadas cambian:** las de `RESULTADO-CONVERSORES.md`, `cv/CLASES-CV3.json`, la página
  y el artículo.

## Previsión (se sella antes de correr)

Antes de la primera corrida se escribe y se sella en un commit la probabilidad de al menos una diferencia por arrastre, y qué
mecanismos del estudio podrían cambiar.

## Hecho cuando

- **Los dos controles,** positivo y negativo, pasan.
- **El corpus entero,** comparado caso a caso, con cada diferencia adjudicada.
- **Un documento de resultado** (`RESULTADO-ARRASTRE.md`), con una de estas dos frases:
  - «Convertidos mensaje a mensaje, los N casos del estudio dan los mismos veredictos que en lote»;
  - o «cambian K casos de N, por arrastre de estado; las cifras publicadas que cambian son estas».
- **Lo publicado, al día con la opción B:**
  - con 0 diferencias, una nota en `RESULTADO-CONVERSORES.md` y en el README del verificador;
  - si cambia algo, la fe de erratas y las cifras corregidas.

## Tope

**Una sesión, y siempre antes del 20-nov.** Gasto externo: las llamadas a Jev.

## Regla de parada

- **El control positivo no sale:** el aparato no ve el arrastre y no se sigue. Se declara y se arregla el aparato.
- **El control negativo da diferencias que no se pueden separar del arrastre:** se declara y la etapa para con ese resultado.

## Fuera de la etapa

- Los veredictos de Microsoft.
- Arreglar el conversor.
- Abrir el issue, que es del autor: queda en su cola si hace falta.
