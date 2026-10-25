# Resultado de la etapa 21: el arrastre de estado de LinuxForHealth en el estudio publicado

**Convertidos mensaje a mensaje, los 436 casos del estudio dan los mismos veredictos que en lote.**

Lo publicado del estudio de conversores no cambia: ni la frase, ni las clases, ni los pares mínimos, ni las categorías por corpus.
El arrastre de estado de LinuxForHealth existe, pero en este corpus, al nivel del veredicto, solo se ve en VXU: los 23 casos de
F7 (`vx/VX2.md`).

La pregunta, fijada antes de medir en [`ANTES-ETAPA-ARRASTRE.md`](ANTES-ETAPA-ARRASTRE.md):

> ¿Cambia algún veredicto del estudio de conversores publicado cuando LinuxForHealth convierte cada mensaje en su propio proceso,
> en vez de todos en un solo proceso, como se hizo en el estudio?

## Qué se comparó

**Los 436 casos del estudio**, con el mismo juez (`bde94016ca58`) y el mismo conversor (LinuxForHealth v1.1.0, huella
`ac41f71b98ee`, imagen `sha256:7bb84a451705…`) a los dos lados:
- **en lote**, con el adaptador del estudio (`cv/adaptadores/linuxforhealth.json`): un proceso Java por corpus;
- **mensaje a mensaje**, con el adaptador nuevo (`cv/adaptadores/linuxforhealth-mensaje.json`): un proceso por mensaje. Lleva el
  mismo `id`, el mismo arnés y la misma huella.

**Dos corridas de cada modo:** L1 y L2 en lote, M1 y M2 mensaje a mensaje. Un caso es «diferente» solo si las dos de lote
coinciden, las dos de mensaje coinciden, y lote y mensaje no (S-AR-10). **El veredicto** es el estado de la salida, la categoría,
el subtipo y el conjunto de hallazgos que cuentan (hecho, clase y subtipo). Las 40 bases VXU viajan en las corridas como control
y no entran en N.

| Corpus | Casos | Iguales | Diferentes | No deterministas | Sin par o de caja |
|---|---|---|---|---|---|
| ADT | 263 | 263 | 0 | 0 | 0 |
| ORU | 40 | 40 | 0 | 0 | 0 |
| Mínimos | 68 | 68 | 0 | 0 | 0 |
| Muestras | 65 | 65 | 0 | 0 | 0 |
| **Total** | **436** | **436** | **0** | **0** | **0** |

En los mínimos, el caso de cada par va justo antes que su control en el mismo proceso de lote; tampoco ahí cambia nada.

**Tiempos:** cada corrida en lote tardó 21 s. Cada corrida mensaje a mensaje, unos 29 minutos, con las dos en paralelo.

## Los controles, antes de mirar el resultado

- **Positivo, la secuencia VL11.** Un VXU con RXA-17 sin código y después el nominal, en un solo proceso. Sale en las dos
  repeticiones: en lote el segundo pierde `manufacturer`, mensaje a mensaje no, y el nivel del Bundle ve la misma diferencia.
- **Positivo, el corpus VXU.** Los casos VXU que cambian entre modos son exactamente VXU-B18 a VXU-B40, los 23 de F7. En todos,
  lo único que cambia es que en lote se pierde el fabricante (RXA-17, `dato_perdido`), y mensaje a mensaje no se pierde nada.
  - **La primera vez no salió, por un defecto del criterio y no del aparato (DV-AR-11).** En B33, B34 y B35 hay varias vacunas
    en el mismo mensaje, y el juez nombra el hallazgo del segundo y del tercer grupo como `RXA(2)-17` y `RXA(3)-17`. El criterio
    del diseño pedía literalmente `RXA-17`.
  - Se arregló por la regla de parada 1: se declara y se arregla el aparato. Primero una prueba en rojo, P-AR-13, y después el
    criterio, que ahora admite el RXA-17 de cualquier grupo.
  - Cuando se vio, la comparación de los 436 ya estaba escrita. No depende de ese criterio, y salió igual al recalcularla. La
    comparación de aquel primer paso, con `controles.positivo_vxu` en `false`, se conserva en
    `cv/ar/COMPARACION-AR-primer-paso9.json`.
- **Negativo, dos corridas del mismo modo.** Cero veredictos distintos en lote y cero mensaje a mensaje, en 476 casos cada uno.
  Cero errores con otra firma. Ninguna caja falló y las cuatro corridas usaron la imagen del estudio. El umbral de parada era
  cero (Q-AR-D-1). Jev es el modelo de decisión con probabilidades calibradas al que se pasan las decisiones de diseño con un
  estado neutro (ver `../piloto-agente/README.md`).
- **El ruido del Bundle** solo se mide (Q-AR-D-4, Jev) y no entra en N. En cada modo hay 332 casos con alguna diferencia entre
  dos corridas, en las mismas 47 rutas; el número de casos por ruta cambia en algunas (en `Immunization.manufacturer.reference`,
  15 en lote y 38 mensaje a mensaje, que es F7). Todas son de dos clases:
  - **las referencias entre recursos:** LinuxForHealth antepone a cada id un número que cambia con el reloj, y la normalización
    del diseño solo quita los UUID;
  - **la marca de fecha de la conversión,** en `meta.extension[].valueDateTime`.

## Las cifras publicadas

**Ninguna cambia entre lote y mensaje a mensaje.** El recálculo ensambla Microsoft (rejuzgado con el juez actual) con
LinuxForHealth en lote, y aparte Microsoft con LinuxForHealth mensaje a mensaje. Después pasa los dos ensamblados por
`cv3_minimos.juzgar` y `cv3_clases.main`, sin tocarlos. Las dos clasificaciones salen idénticas (`cv/ar/CLASES-AR-lote.json` y
`cv/ar/CLASES-AR-mensaje.json`), y lo mismo los pares mínimos (`cv/ar/minimos-AR-*.json`).

**La deriva del juez se declara aparte y no se corrige aquí.** Comparando lo publicado (juez `54a90cd9` de CV3) con el lote y el
juez actual salen 8 filas en `cv/ar/CIFRAS-AR.json`. Todas son los cambios de CV4, ya documentados en
[`RESULTADO-CONVERSORES.md`](RESULTADO-CONVERSORES.md), en «Qué cambió en el juez durante la etapa»:
- **CX.4:**
  - L-24 y M-36 se quedan sin casos (3 de muestras);
  - el par `L16-cx-4-solo-nombre` deja de confirmarse;
  - los pares confirmados pasan de 31 a 30. Era el falso positivo del juez que CV4 arregló.
- **Q-CV-D-14:** M-4 pasa de 16 casos de ADT a 8. En los otros 8, el texto del hallazgo es ahora el de la descripción que
  contiene PL.9 sin serlo, y ninguna regla de `cv3_clases.py` lo recoge. En 6 de ellos cambió el subtipo, que es lo que cuenta
  el documento («6 casos de PL.9 pasan a `valor_distinto`»); los otros 2 ya lo llevaban.

**La frase del estudio no cambia en ninguno de los dos ejes.**

## Qué se hace con lo publicado

- **Una nota en `RESULTADO-CONVERSORES.md` y en el README del verificador.** Lo que se publicó en lote vale también mensaje a
  mensaje.
- **El adaptador de referencia sigue siendo el de lote** (Q-AR-D-3, Jev: según el resultado). El de mensaje se publica al lado.
- **La página web no cambia:** no cambia ninguna cifra.

## La previsión sellada, frente a lo que salió

La previsión se selló antes de cualquier corrida con Docker (`cv/ar/PREVISION-AR.json`, `cv/ar/SELLO-AR.txt`). Hay dos, cada una
con su autor.

| Qué | Programador | Jev | Salió |
|---|---|---|---|
| Al menos un caso cambia por arrastre | 0,3 (K = 0 lo más probable) | 0,79 | no (K = 0) |
| Alguna cifra publicada cambia | 0,22 | 0,85 | no |
| Si cambia, en las muestras | 0,6 | 0,89 | — |
| El control negativo pasa | 0,9 | — | sí |
| El positivo VL11 sale | 0,95 | — | sí |
| El corpus VXU da los 23 de F7 | 0,9 | — | sí, tras DV-AR-11 |
| El ruido del Bundle, en la fecha de la conversión | sí | — | sí, y además en todas las referencias |

**`SELLO-AR.txt` ya no verifica tres de sus ficheros:** `arrastre.py` y `prueba_ar.py` (DV-AR-11 y DV-AR-12) y `control_ar.py`
(DV-AR-12) cambiaron después del sello, y sus huellas no cuadran. Es lo esperado: el sello dice cómo estaban al sellar. La
previsión no cambió, y su huella sigue cuadrando.

## Límites

- **El orden del lote.** «Lote» es un proceso por corpus en el orden alfabético de los nombres, el de la herramienta y el del
  arnés. Otro orden, todo el corpus en un solo proceso o un servicio de larga vida pueden arrastrar distinto, y no se miden
  (L-AR-1). La invocación exacta del estudio no está en lo público. En el repositorio de trabajo, el estudio corrió una carpeta
  por corpus (ADT, ORU, las 65 muestras juntas y los 68 mínimos), como la herramienta; lo público lo apoya: `cv/corpus_cv2.py`
  escribe una sola carpeta de muestras, `cv/cv3_minimos.py` una de mínimos, y `cv/correr_conversor.py` lanza un proceso por
  carpeta. Que el lote de la herramienta
  dé los veredictos publicados se apoya en el control de la etapa 18 (los mismos veredictos que el estudio en los 368 casos) y
  en que la deriva de los mínimos es la de CV4.
- **Solo se ve lo que ve el juez.** El Bundle crudo se compara solo para medir el ruido (L-AR-2, Q-AR-D-4). Un arrastre que
  cambie algo que el juez no mira no se ve aquí; tampoco una referencia perdida que no cambie ningún hallazgo.
- **El veredicto es un conjunto, sin texto.** Dos hallazgos con el mismo hecho, clase y subtipo cuentan como uno, y el texto
  del hallazgo no cuenta. Un arrastre que cambie un valor dentro del mismo subtipo, o que pierda una repetición más de un campo
  que ya se pierde, no se ve. Las notas y las convenciones tampoco entran en el veredicto; las clasificaciones de los dos modos,
  que sí cuentan las convenciones, salen idénticas. En los errores, entre modos solo se compara la categoría, no el texto.
- **Un arrastre que coincida con un defecto propio del mensaje no se ve:** quitar un dato que el conversor ya pierde por sí
  solo no cambia el veredicto. En VXU se vio porque las bases B18 a B40 tenían fabricante por derecho propio.
- **El disparador tiene que estar en el corpus y antes del caso** (L-AR-4). Que no haya arrastre en ADT y ORU dice que este
  corpus no lo dispara, no que no se pueda disparar.
- **Los positivos prueban este tipo de arrastre:** una referencia anidada que se pierde (y, en el conversor de juguete, un
  campo). Otro tipo no queda probado (L-AR-5). Dos corridas por modo no descartan un no determinismo poco frecuente (L-AR-9). No
  se miden tiempos ni memoria (L-AR-15).
- **Microsoft queda fuera.** Convierte un mensaje por proceso por construcción (L-AR-7).
- **Las muestras de los proyectos no viajan con el repositorio.** Un tercero repite ADT, ORU y mínimos (371 de 436) (L-AR-14).

## Cómo repetir

Desde `verificador/`, con los artefactos del estudio (`lfh/lib`, `lfh/clases`, `lfh/Arnes.java`; ver `cv/CV1.md`).

1. **Las pruebas,** sin Docker: `python3 cv/ar/prueba_ar.py`.
2. **Una previsión sellada propia.** El orquestador no corre el corpus sin una previsión sellada en un commit. El sello publicado
   ya no verifica tres ficheros del aparato, que cambiaron después (DV-AR-11, DV-AR-12), así que quien repite sella la suya en
   otra carpeta: su cuerpo, con la forma de `cv/ar/prevision-cuerpo.json`; `sellar_prevision.py`, que se niega a pisar un sello
   que ya exista; y un commit.
3. **Una corrida de Microsoft con la herramienta,** con sus muestras, para el recálculo de cifras (unos 4 minutos; ver
   `cv/VC.md`).
4. **El control:**

```bash
python3 cv/ar/sellar_prevision.py <mi-cuerpo.json> <mi-carpeta>
python3 cv/ar/control_ar.py <artefactos> <muestras> <salida> --sello <mi-carpeta> --ms <corrida de Microsoft> --paralelo
```

**El aparato:** el diseño a ciegas de Fable está en `cv/ar/diseno-ar-fable.md` y su encargo en `cv/ar/ENCARGO-AR0.md`. Las
decisiones de Jev y las desviaciones del programador están en `cv/ar/decisiones-qar.md`. Los resultados por paso:
- `cv/ar/POSITIVO-AR.json`;
- `cv/ar/RUIDO-AR.json`;
- `cv/ar/COMPARACION-AR.json`;
- `cv/ar/ADJUDICACION-AR.json`;
- `cv/ar/CIFRAS-AR.json`;
- `cv/ar/CONTROL-AR.json`.
