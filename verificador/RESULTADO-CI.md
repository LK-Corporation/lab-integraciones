# Resultado de la etapa 23: el verificador en la integración continua de un conversor

**Un proyecto puede pasar su conversor por el verificador en cada cambio con un flujo reutilizable de GitHub Actions; con el
conversor de juguete y LinuxForHealth v1.1.0, el flujo falla solo ante un hallazgo que no está en la línea base.**

Los tres controles salieron en verde en GitHub Actions en el primer push, el del commit `981b004`. Los informes del runner son
iguales byte a byte a los del laboratorio. Una corrida de la demostración tardó minuto y medio.

La pregunta, fijada antes de medir en [`ANTES-ETAPA-CI.md`](ANTES-ETAPA-CI.md):

> ¿Puede un proyecto de conversor HL7 v2 → FHIR pasar su conversor por el verificador en cada cambio, con un flujo reutilizable
> de GitHub Actions, de forma que el cambio falle solo si aparece un hallazgo que no estaba en su línea base?

**Qué es «un hallazgo que no está en la línea base»** (Q-CI-D-1, Jev). Es un hallazgo `(hecho, clase, subtipo)` nuevo en un caso
que ya estaba en la base. También hacen fallar el cambio un caso que pierde su salida, un caso que pasa a indeterminado y una caja
que no pudo correr. No lo hacen fallar, y se listan en el resumen y en la base propuesta:
- un arreglo: un hallazgo de la base que desaparece;
- un caso nuevo, aunque traiga hallazgos;
- un caso de la base que ya no está;
- otro juez, otro corpus, otra huella del conversor u otra imagen.

La guía para usarlo es [`cv/ci/CI.md`](cv/ci/CI.md).

## Los tres controles, en el runner

La corrida es la del push: [`demo-ci` n.º 1](https://github.com/LK-Corporation/lab-integraciones/actions/runs/40215114769),
evento `push` y `ubuntu-latest`. Lo que se trajo de ella está en [`cv/ci/CORRIDA-CI-1.json`](cv/ci/CORRIDA-CI-1.json).

| Control | Qué espera | Qué dio | Informe frente al laboratorio | Minutos del job |
|---|---|---|---|---|
| negativo: el juguete contra su base | `igual` | pasa: 0 nuevos y 0 arreglos en 343 casos | igual byte a byte | 0,2 |
| positivo: el juguete con PID-7 sembrado | `falla`, solo por `("PID-7", "fidelidad", "dato_perdido")` | falla, por ese hallazgo y solo por él, en 303 casos | igual byte a byte | 0,1 |
| real: LinuxForHealth v1.1.0 traído en el runner | `igual` | pasa: 0 nuevos y 0 arreglos en 411 casos | igual byte a byte | 1,1 |

- **El positivo se comprobó dos veces:**
  - dentro del flujo, con `esperar: falla`;
  - fuera, en `positivo-comprobado`, que lee las salidas del flujo reutilizable: `resultado` falla, 303 nuevos, y los distintos
    son exactamente el hallazgo sembrado.
- **En el real, `real-comprobado` leyó desde fuera, en las salidas del flujo:**
  - que pasa, con 0 nuevos y 0 arreglos;
  - que la huella del conversor traído de Maven Central es la del estudio, `ac41f71b…`;
  - que la imagen es la del digest `sha256:7bb84a45…`.

  El veredicto del artefacto da además la huella con nombres, `7ad4d546…`, y el juez, el publicado: `b3f00f6a…`.
- **La caja del runner es la de la herramienta:** `--network none --read-only --tmpfs /tmp --cap-drop ALL --security-opt
  no-new-privileges --user 65534:65534 --pids-limit 1024`, con los montajes de solo lectura. Corrió sin reintentos ni casos sin
  evidencia. LinuxForHealth estuvo 30 segundos en sus cuatro contenedores.
- **«Igual byte a byte»:** el `INFORME.json` de cada artefacto es idéntico al de la corrida del laboratorio del mismo control.
  - En el negativo y el real, es la corrida de la que salió la base.
  - En el positivo, es la corrida sembrada del laboratorio.
  - Ese fichero no lleva fechas, tiempos ni rutas. Las categorías, los hallazgos y los mínimos son los mismos, sin que la
    comparación tuviera que perdonar nada.

## Mensaje a mano

**Mensaje a mensaje (Q-CI-D-3, Jev):** a mano, con `workflow_dispatch` y `modo_real: mensaje`, sobre el mismo commit. La corrida
es [`demo-ci` n.º 2](https://github.com/LK-Corporation/lab-integraciones/actions/runs/40215376109), y lo traído de ella está en
[`cv/ci/CORRIDA-CI-2.json`](cv/ci/CORRIDA-CI-2.json).
- **Los seis jobs, en verde.**
- **El real** corre un proceso Java por mensaje, 411 en total, contra `LINEA-BASE-linuxforhealth-mensaje.json`. Da 0 nuevos y 0
  arreglos, y el informe es igual byte a byte al de la corrida mensaje a mensaje del laboratorio.
- **Que se comparó con la base de mensaje y no con la de lote** lo dice el resultado mismo: con `esperar: igual`, la de lote
  habría dado los 23 arreglos del arrastre (VXU-B18 a VXU-B40).
- **Costó 41,8 minutos de job,** 41 de ellos de caja, dentro del tope de 75 del flujo (DV-CI-5). Por eso no corre en cada push.

## Lo que cuesta

La corrida de la demostración por push tardó **1,5 minutos** de reloj. Los jobs corren a la vez:

| Job | Minutos |
|---|---|
| `pruebas` | 0,3 |
| `negativo` | 0,2 |
| `positivo` | 0,1 |
| `positivo-comprobado` | 0,1 |
| `real` | 1,1 |
| `real-comprobado` | 0,0 |

El job `real` incluye traer de Maven Central el jar con sus dependencias y la imagen por su digest, y compilar el arnés. La previsión
esperaba de 5 a 15 minutos por corrida y salió por debajo. Mensaje a mensaje, a mano, son 42 minutos.

## La previsión, frente a lo que salió

La previsión se selló antes del primer push: [`cv/ci/PREVISION-CI.md`](cv/ci/PREVISION-CI.md) y
[`cv/ci/SELLO-CI.txt`](cv/ci/SELLO-CI.txt). Desde la etapa 24, `cv/ci/prueba_ci.py` y `cv/ci/ensayo_flujo.py` son otros:
el sello verifica sus versiones del commit `0f85437`. Desde la etapa 26, también las tres líneas base, rehechas con el juez
y el corpus de MDM: el sello verifica las del commit `b4009b7`.

| | Programador | Jev, antes del ensayo | Jev, después del ensayo | Salió |
|---|---|---|---|---|
| Los tres en verde en el primer push | 0,5 | 0,18 | 0,46 | **sí** |
| Pushes hasta los tres en verde | 1 a 3, lo más probable 1 | más de cuatro, 0,8 | más de cuatro, 0,67; uno, 0,18 | **1** |
| El real da los mismos veredictos | 0,92 | 0,61 | 0,84 | **sí, byte a byte** |
| La huella del real cuadra | 0,95 | — | — | **sí** |
| El positivo falla en 303 casos, solo por PID-7 | 303 | — | — | **303** |
| Minutos por corrida | 5 a 15 | — | — | **1,5**, fuera del intervalo |

**Lo que más pesó en la previsión fue el ensayo local** ([`cv/ci/ensayo_flujo.py`](cv/ci/ensayo_flujo.py), DV-CI-10). Corrió los
pasos de los dos YAML en la máquina del laboratorio antes del primer push.
- **El programador:** del borrador al sello, el real a la primera pasó de 0,45 a 0,6, y los pushes más probables de 2 a 1.
- **Jev:** los tres en verde en el primer push pasaron de 0,18 a 0,46. Después del ensayo seguía dando más de cuatro pushes como
  lo más probable.

## Antes del primer push

- **El ensayo local salió en verde a la primera** con los seis jobs. No vio nada que arreglar, porque los tres controles solo
  recorren el camino en que todo sale con 0.
- **La revisión a ciegas sí vio un defecto,** en el camino de fallo (DV-CI-12 en
  [`cv/ci/decisiones-qci.md`](cv/ci/decisiones-qci.md)).
  - GitHub corre los pasos como `bash -eo pipefail`, y dos pasos que recogen un código de salida se cortaban antes de tiempo.
    Cuando el cambio fallaba, la página del job se quedaba sin resumen, y una caja rota no daba su motivo.
  - Se arregló con una prueba en rojo primero (P-CI-15), y la previsión se volvió a sellar con las mismas cifras.

## Lo que no dice

- **Ningún otro repositorio ha llamado al flujo.** La demostración lo llama desde el propio laboratorio, con
  `uses: ./.github/workflows/…`, y con los adaptadores y las bases bajo `lab/`. En el runner no se recorrieron:
  - la llamada que describe `CI.md`, `uses: LK-Corporation/lab-integraciones/…@<commit>` desde otro repositorio, con
    `proyecto/ci/…` y un `preparar` propio;
  - el modo `esperar: pasa`, que es el que usaría un proyecto;
  - las entradas `corpus`, `sin_corpus_lab`, `opciones` y `artefacto_completo`;
  - el evento `pull_request`.

  Fuera del runner, sin GitHub:
  - el modo `pasa` lo cubren las pruebas de la comparación (P-CI-2 a P-CI-8);
  - `--corpus` y `--sin-corpus-lab`, las de la herramienta.

  De las entradas del YAML solo se comprueba que existen (P-CI-11). La llamada desde otro repositorio, `artefacto_completo` y
  `pull_request` no las cubre ninguna prueba.
- **El camino en que el job se pone rojo no se recorrió en el runner.**
  - El positivo falla dentro del flujo y el job sale en verde, porque es lo que espera.
  - Que un cambio con un hallazgo nuevo pone el job en rojo, con su resumen, lo prueban P-CI-15 y las pruebas de la comparación,
    en el laboratorio y en el job `pruebas` del runner.
- **Un solo tipo de defecto sembrado:** un dato perdido en una fecha. Otros tipos, como un código mal mapeado o un rechazo, los
  prueban P-CI-3 y P-CI-6 sin Docker (L-CI-8).
- **«Conocido» no es «correcto».** La base registra veredictos del juez, no lo que el proyecto tenga declarado (L-CI-7, L-VC-1).
- **Solo `ubuntu-latest` y su Docker**, en una corrida por push (L-CI-2, L-CI-5). Otro runner o un conversor no determinista
  quedan fuera.
- **Solo GitHub Actions** (L-CI-3). Otro CI puede reutilizar `linea_base.py` y la herramienta, no el YAML.
- **Microsoft FHIR-Converter no se construye en el runner** (fuera de la etapa). `CI.md` dice cómo se prepararía.
- **Lo que hay detrás del enlace caduca.** La página de la corrida se queda, pero GitHub borra los registros (a los 90 días, por
  omisión) y los artefactos (a los 14). `CORRIDA-CI-1.json` y `CORRIDA-CI-2.json` guardan lo que se comprobó de ellos.

## Cómo repetirlo

- **En GitHub:** cada push a `main` que toque `verificador/**`, `.github/workflows/**` o `tests/**` corre la demostración. A mano,
  con «Run workflow» en `demo-ci`, se elige el modo del real.
- **En una máquina,** desde `verificador/`:
  - `python3 cv/ci/hacer_bases.py <esta carpeta> <artefactos> <trabajo> juguete lote mensaje` rehace las bases, con los
    artefactos que prepara `cv/ci/preparar_lfh.sh`;
  - `python3 cv/ci/ensayo_flujo.py <repositorio> <carpeta vacía> pruebas,negativo,positivo,real` ensaya los jobs.

## Los documentos de la etapa

El índice está en la sección de la etapa 23 de [`README.md`](README.md).
- **El diseño a ciegas:** [`cv/ci/diseno-ci-fable.md`](cv/ci/diseno-ci-fable.md).
- **Las decisiones de Jev y las desviaciones del programador:** [`cv/ci/decisiones-qci.md`](cv/ci/decisiones-qci.md).
- **Las corridas:** [`cv/ci/CORRIDA-CI-1.json`](cv/ci/CORRIDA-CI-1.json) y [`cv/ci/CORRIDA-CI-2.json`](cv/ci/CORRIDA-CI-2.json), que
  trajo [`cv/ci/traer_resultados_ci.py`](cv/ci/traer_resultados_ci.py).
