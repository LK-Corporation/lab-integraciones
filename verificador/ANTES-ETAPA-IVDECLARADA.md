> *Copia pública: el párrafo «Fijado en autónomo» marca como no publicadas la hoja de ruta y la decisión de ruta del laboratorio; el resto, la pregunta y el «Hecho cuando» incluidos, va literal. El veredicto por muestra que pide el «Hecho cuando» está en el laboratorio; aquí se publican sus agregados. La huella que cita `ivd/SELLO-IVD.txt` es la del original.*

# ANTES: etapa 32, las muestras públicas en la versión que declaran (FIJADO el 5-nov-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). Jev la eligió con 0,84
(`decision-jev-ruta16.md`, no publicada); la segunda, arreglar los generadores, 0,14.

## La pregunta (fija)

> Las muestras públicas de los dos conversores que declaran en MSH-12 otra versión que la 2.5, validadas por IRIS con el esquema
> de su versión: ¿cuántas son mensajes válidos de esa versión? ¿Alguna de las nuevas que se apoyan en muestras sigue sin ningún
> mensaje válido?

## Por qué

- **La etapa 31 las validó contra v2.5,** como las lee el juez: 0 válidas, 171 inválidas y 54 sin decidir. Dijo que no sabe si son
  válidas en su propia versión.
- **IRIS trae los esquemas de 2.1 a 2.8.2.** El laboratorio tiene el texto de v2.5 y el de v2.5.1, no el de las demás.
- **El juez no cambia:** lee las muestras como v2.5. Esto dice si lo que el juez lee como «fuera de versión» es, en su versión, un
  mensaje válido.

## Qué se valida

Las 223 muestras de la 31 que declaran otra versión: 108 de la 2.6, 64 de la 2.8, 44 de la 2.5.1, 6 de la 2.3 y 1 de la 2.4. La
versión es el primer componente de MSH-12 (una muestra trae «2.5.1^^^…»). Las 2 que declaran la 2.5 se quedan con su veredicto de
la 31.

## Las decisiones (Jev)

- **Q-VD-1, las versiones sin texto** (2.3, 2.4, 2.6 y 2.8; `ivd/decision-jev-qvd.md`, 0,95). Cuentan la estructura, los
  obligatorios y las longitudes, como los da IRIS. Las tablas de HL7 quedan sin decidir y las de usuario son aviso. Se apoya en lo
  medido en la 30 y la 31: frente al texto de v2.5, IRIS acertó todos sus errores de estructura, obligatorios y longitudes, y no
  los de tablas. El resultado lo dice como «según IRIS», no «según el estándar».
- **Q-VD-2, las de la 2.5.1** (0,99). Se leen con el texto de v2.5.1, como la 30 con el de v2.5: sus tablas de atributos, el
  índice y los valores de su Apéndice A.
- **Q-VD-3, la pasada de repeticiones** (`ivd/decision-jev-qvd3b.md`, 0,95, preguntada otra vez con las reglas del receptor,
  CH02.txt:932-935 y 1143-1147). Se mide aparte, como en la 31. La primera vez salió «dentro» (0,75), con un estado al que le
  faltaba ese pasaje.
- **Lo demás se hereda de la 30 y la 31,** incluidas Q-MV-2 y Q-MV-4. Un segmento que la versión no define va aparte, como en la
  31. En la 2.5.1 es uno sin tabla de atributos en su texto; sin texto, uno que el esquema de IRIS de esa versión no trae. La
  primera versión de la lectura sin texto lo contaba como error, y el control lo cazó antes de sellar.

## Cómo

1. **El aparato es el de la 31 con la versión de cada muestra,** escrito aparte para que el de la 31 no cambie:
   - una copia de la clase de IRIS que resuelve la estructura en la versión pedida;
   - el conductor, en dos copias: la de la 2.5.1, con las tablas de su texto, y la de sin texto, sin tablas, que deja a IRIS lo
     que Q-VD-1 le deja;
   - la lectura de la 31 para la 2.5.1, y una lectura con la regla de Q-VD-1 para las demás;
   - el texto de v2.5.1 se lee con los analizadores de la 30, por una carpeta de enlaces con los nombres de v2.5. No se copia;
   - un cambio en el analizador de las tablas de atributos: el tipo de dato admite «varies». Sin él, OBX-5 tomaba la fila de
     una tabla de ejemplo (CH07.txt:7624 en v2.5). En la 30 y la 31 no hubo errores en OBX-5, así que lo publicado no cambia.
2. **El control, antes de correr:**
   - los mutantes de la 31 en una base de cada versión (2.5.1, 2.6 y 2.8);
   - uno de un segmento que esa versión no define;
   - y un control negativo de la versión: una base de la 2.8 da con el conductor de la 31 errores que con el suyo no da.
3. **La previsión se sella antes de correr,** con el aparato y la lectura ya escritos.
4. **El cruce:**
   - cada muestra, frente a su veredicto de la 31;
   - cada nueva que se apoya en muestras, con su apoyo del laboratorio de la 30.

## Hecho cuando

- **Un veredicto por muestra en su versión,** con lo que cuenta según IRIS separado de lo que sostiene el texto.
- **Cada nueva con apoyo en muestras,** marcada como en la 31.
- **`RESULTADO-IVDECLARADA.md`** con la frase: «De las 223 muestras que declaran otra versión que la 2.5, con el esquema de IRIS de
  la suya, V son válidas, I inválidas y D sin decidir; de las 5 nuevas que se apoyan en muestras, K siguen sin ningún mensaje
  válido».
- **Publicado con la opción B.**

## Tope

**Una sesión.** Sin agentes más allá de la revisión a ciegas: hasta dos lectores, porque en la 30 y en la 31 cada lector nuevo
encontró un fallo de fondo.
