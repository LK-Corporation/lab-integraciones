# Pasa tu conversor por el verificador en cada cambio

Un flujo reutilizable de GitHub Actions corre tu conversor HL7 v2 → FHIR R4 en la caja del laboratorio: Docker sin red, sistema
de ficheros de solo lectura y usuario sin privilegios. Lo juzga con el verificador sobre el corpus público y **falla solo si
aparece un hallazgo que no está en tu línea base**.
- **Lo que pide:** `permissions: contents: read` y ningún secreto.
- **Lo que no hace:** no escribe en tu repositorio ni comenta en tus PR.

La herramienta que corre por debajo es la de [`VC.md`](../VC.md): un adaptador JSON y una orden. Este flujo le añade la línea
base, para separar lo que ya conoces de lo que acaba de aparecer.

## Lo que pones en tu proyecto

1. **Un adaptador** (`ci/adaptador.json`), como los de [`../adaptadores/`](../adaptadores/), en el formato `adaptador-vc/1`
   descrito en [`VC.md`](../VC.md). Las rutas de los montajes y de la huella son relativas a la carpeta de artefactos.
2. **Una orden que prepare los artefactos** (`preparar`): construye o descarga tu conversor en `$ARTEFACTOS`. Corre con red;
   después, el conversor corre sin red.
3. **La imagen con su digest** (`imagen`). La sacas con `docker pull <repo>:<etiqueta>` y
   `docker image inspect --format '{{index .RepoDigests 0}}' <repo>:<etiqueta>`, que dan `repo@sha256:…`. El flujo trae la imagen
   por ese digest y exige que sea esa.
4. **La línea base** (`ci/LINEA-BASE.json`). La primera vez se hace en tu máquina:

   ```bash
   git clone https://github.com/LK-Corporation/lab-integraciones && cd lab-integraciones/verificador
   git checkout <el commit de 40 hex que vas a fijar en uses:>
   python3 cv/verificar_conversor.py <tu adaptador> <salida> --artefactos <tus artefactos> --sin-sensibilidad
   python3 cv/ci/linea_base.py crear <salida> -o <tu repo>/ci/LINEA-BASE.json
   ```

   O lanzas el flujo con una base vacía (`{"formato": "linea-base-ci/1", "conversor": {"id": "<el id de tu adaptador>"},
   "creada_de": {"juez": {"huella": null}}, "corpus": {}, "casos": {}, "n_casos": 0}`). Todos los casos salen como nuevos, el
   flujo no falla, y en el artefacto queda `LINEA-BASE-propuesta.json`, que subes como base.
5. **El flujo,** en `.github/workflows/verificador.yml`:

   ```yaml
   name: verificador
   on:
     pull_request:
     push:
       branches: [main]
   permissions:
     contents: read
   jobs:
     verificar:
       uses: LK-Corporation/lab-integraciones/.github/workflows/verificador-conversor.yml@<commit de 40 hex del laboratorio>
       permissions:
         contents: read
       with:
         adaptador: proyecto/ci/adaptador.json
         linea_base: proyecto/ci/LINEA-BASE.json
         preparar: cd "$PROYECTO" && ./gradlew -q jar && mkdir -p "$ARTEFACTOS/lib" && cp build/libs/*.jar "$ARTEFACTOS/lib/"
         imagen: eclipse-temurin:11-jre@sha256:<64 hex>
         laboratorio_ref: <el mismo commit de 40 hex>
   ```

   En el workspace del runner, `proyecto/` es tu repositorio y `lab/` el laboratorio.
   - **`laboratorio_ref` es obligatoria y tiene que ser el mismo commit entero (40 hex) que en `uses:`.** Una rama o una
     etiqueta se rechazan con el código 2. El juez, la herramienta y el corpus son los de ese commit, y tu base se hizo con ellos.
   - **Cuando subas de commit, regenera la base.** Un juez distinto se avisa y la base propuesta lo marca (`juez_cambiado`).

## Lo que cambia desde la etapa 24 (para quien ya lo usaba)

- **`laboratorio_ref` es obligatoria y un commit de 40 hex.** Quien la omitía corría `main` sin saberlo: ahora GitHub no arranca
  la llamada. Quien daba una rama o una etiqueta recibe el código 2.
- **`preparar` corre con `bash --noprofile --norc -euo pipefail -c`,** con las mismas variables (`LAB`, `PROYECTO`, `ARTEFACTOS`,
  `IMAGEN`) y en el mismo directorio.
- **Las entradas llegan a las órdenes por variables de entorno.** Ninguna se escribe ya dentro de un `run:`.
- **Las acciones van fijadas por commit,** las de [`ACCIONES-CI.json`](ACCIONES-CI.json): el mismo código que corría por
  etiqueta.
- **`corpus` y `opciones` se parten por espacios con `read -ra`,** sin interpretar comillas ni comodines. Una opción con espacios
  dentro, o entre comillas, ya no se parte como antes.

El flujo y sus salidas no cambian en nada más.

## Lo que hace fallar el cambio

En el modo normal (`esperar: pasa`), falla el cambio si pasa alguna de estas cosas:
- **un hallazgo que no estaba en la base de ese caso:** un hecho, una clase o un subtipo nuevos;
- **un caso que pierde su salida** o que pasa a indeterminado;
- **la caja,** si no pudo correr.

Lo demás se lista y no falla:
- **un arreglo:** lo que desaparece;
- **un caso nuevo,** aunque traiga hallazgos;
- **un caso de la base que ya no está;**
- **otro juez, otro corpus u otra huella del conversor.**

Todo eso entra en la base propuesta.

Hay otros dos modos:
- **`igual`:** cualquier diferencia falla. Es el que usan los controles del laboratorio.
- **`falla`:** el flujo tiene que fallar, y solo por los hallazgos de `hallazgo_esperado`. Sirve para probar que el flujo ve un
  defecto sembrado.

## Lo que te deja

El resumen en la página del job y el artefacto `<nombre>-<intento>`, con `INFORME.md`, `INFORME.json`, `juicio.jsonl`,
`VEREDICTO-CI.json`, `VEREDICTO-CI.md` y `LINEA-BASE-propuesta.json`. Las evidencias y el corpus solo van si los pides
(`artefacto_completo: true`), porque llevan los mensajes enteros.

`INFORME.*` y `juicio.jsonl` llevan los valores de los campos que juzga cada hallazgo. En un repositorio público, cualquiera puede
descargar el artefacto. Si añades mensajes propios con `corpus`, que sean sintéticos.

## Cómo aceptas un cambio

Descarga `LINEA-BASE-propuesta.json` del artefacto, cópiala sobre `ci/LINEA-BASE.json` y súbela en el mismo PR. **Lo que la base
registra son veredictos del juez, no tu opinión:** aceptar un hallazgo en la base no lo convierte en correcto; lo convierte en
conocido.

## Lo que no hace

- **No sabe si tu proyecto ya tenía declarado cada hallazgo** (L-VC-1).
- **Solo cabe un conversor de línea de órdenes** que lea y escriba ficheros, no un servicio HTTP ni una biblioteca (L-VC-3).
- **El corpus son las bases sintéticas del laboratorio** (ADT de ocho eventos, ORU^R01 y VXU^V04) y los mensajes que añadas con
  `corpus`; no las muestras de los proyectos del estudio (L-VC-2, L-VC-7).
- **El veredicto es un conjunto de hallazgos, sin texto.** Un cambio de valor dentro del mismo subtipo no se ve (L-CI-1).
- **Corre en `ubuntu-latest`, con su Docker** (L-CI-2).
- **Una corrida es una corrida:** un conversor no determinista dará hallazgos y arreglos intermitentes (L-CI-5).
- **Las entradas llegan a las órdenes por variables de entorno,** pero `preparar` es una orden tuya que se ejecuta tal cual. No
  pongas en ella texto que controle otro, como `github.head_ref` o el título de un PR.
- **Las acciones van fijadas por commit y no se actualizan solas.** En octubre de 2026 GitHub ya avisa de que corren en Node.js
  20 y las fuerza a Node.js 24, y `ubuntu-latest` pasa a Ubuntu 26. Subirlas es un commit con `ACCIONES-CI.json` al día.
- **Si un job de comprobación descarga el artefacto del flujo, relanza todos los jobs, no solo el que falló.** El relanzado
  busca el artefacto de su intento, y el job que lo sube no se relanzó.
- **Microsoft FHIR-Converter** se puede preparar con `dotnet publish` en `preparar` (ver [`../CV1.md`](../CV1.md)), pero no es un
  control de la etapa.

## Un ejemplo completo

La demostración del laboratorio, [`../../../.github/workflows/demo-ci.yml`](../../../.github/workflows/demo-ci.yml), tiene tres
controles:
- **negativo:** el conversor de juguete contra su propia base, con `esperar: igual`;
- **positivo:** el juguete con un defecto sembrado, que pierde la fecha de nacimiento, con `esperar: falla`;
- **real:** LinuxForHealth v1.1.0, traído en el runner desde Maven Central con
  [`preparar_lfh.sh`](preparar_lfh.sh), con la imagen por digest, la huella del estudio en `huella_esperada` y
  `esperar: igual`. A mano (`workflow_dispatch`) se puede correr mensaje a mensaje.

Las dos llamadas del proyecto de ejemplo son `.github/workflows/ejemplo-ci.yml` y `.github/workflows/rojo-ci.yml`.
- **Cuándo llegan:** en el segundo push de la etapa 24, con el commit del primero fijado en `uses:`.
- **Sus plantillas,** con el commit por poner: [`github-ci2/ejemplo-ci.yml`](github-ci2/ejemplo-ci.yml) y
  [`github-ci2/rojo-ci.yml`](github-ci2/rojo-ci.yml).

## Un proyecto de ejemplo para copiar

[`../../../ejemplo-ci/`](../../../ejemplo-ci/) es un proyecto de conversor como lo tendría un tercero:
- **lo que tiene:** su conversor (Python, en la imagen oficial `python:3.12-slim` por digest), su `preparar.sh`, su adaptador,
  seis mensajes sintéticos propios y dos líneas base;
- **su llamada:** `.github/workflows/ejemplo-ci.yml`, por la forma remota y fijada a un commit del laboratorio, con dos llamadas.
  La primera usa el corpus del laboratorio más el propio. La segunda, solo el propio (`sin_corpus_lab`), con `--json-solo` en
  `opciones` y `artefacto_completo`;
- **su comprobación:** un job de fuera descarga los dos artefactos y comprueba que cada entrada hizo lo que debe, y nada más
  ([`comprobar_ejemplo.py`](comprobar_ejemplo.py)).

Para copiarlo:
1. copia la carpeta;
2. cambia el conversor, `preparar.sh`, la imagen del adaptador con su digest y el corpus;
3. rehaz las bases con `ci/hacer_base.sh`. Corre desde un clon del laboratorio, con la carpeta copiada en su raíz, y para si algo
   no cuadra. Antes hay que cambiar en el guion cuatro cosas:
   - el digest (`DIGEST`) y el nombre de la imagen que etiqueta;
   - la comprobación de entrada, que exige `ejemplo-ci/conversor.py`;
   - los casos que espera de cada base: 349 y 6 en el ejemplo;
   - el defecto de `DEFECTO.json`, o quitar los pasos 8 a 11: siembran el defecto, lo deshacen y leen su veredicto.

El commit fijado en el ejemplo se queda donde está hasta que se suba a mano, en dos pasos: un commit nuevo del laboratorio y
otro que suba el pin. Es lo que le pasa a cualquier proyecto.

## El run en rojo, para verlo fallar

`.github/workflows/rojo-ci.yml`, que llega en el segundo push, corre solo a mano. Siembra en la copia del conversor del ejemplo
un defecto
([`../../../ejemplo-ci/ci/DEFECTO.json`](../../../ejemplo-ci/ci/DEFECTO.json): `F` sale como `male`) y llama al flujo en el modo
normal, `pasa`. El job `rojo` falla por ese hallazgo, con su resumen y su artefacto. `rojo-comprobado` lo comprueba desde fuera
([`comprobar_rojo.py`](comprobar_rojo.py)). La corrida queda en rojo: un job que llama a un flujo reutilizable no admite
`continue-on-error`.

En una máquina se repite con los pasos 8 a 10 de `ejemplo-ci/ci/hacer_base.sh`.

## Cómo repetirlo en tu máquina

```bash
python3 cv/verificar_conversor.py ci/adaptador.json <salida> --artefactos <artefactos> --sin-sensibilidad
python3 cv/ci/linea_base.py comparar <salida> ci/LINEA-BASE.json
```

`comparar` sale con 0 si el veredicto es el esperado y con 10 si no; `VEREDICTO-CI.md` lo cuenta.
