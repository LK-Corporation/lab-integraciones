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
       uses: LK-Corporation/lab-integraciones/.github/workflows/verificador-conversor.yml@<commit del laboratorio>
       permissions:
         contents: read
       with:
         adaptador: proyecto/ci/adaptador.json
         linea_base: proyecto/ci/LINEA-BASE.json
         preparar: cd "$PROYECTO" && ./gradlew -q jar && mkdir -p "$ARTEFACTOS/lib" && cp build/libs/*.jar "$ARTEFACTOS/lib/"
         imagen: eclipse-temurin:11-jre@sha256:<64 hex>
         laboratorio_ref: <el mismo commit del laboratorio>
   ```

   En el workspace del runner, `proyecto/` es tu repositorio y `lab/` el laboratorio.
   - **Fija el laboratorio a un commit,** en `uses: …@<commit>` y en `laboratorio_ref`. El juez, la herramienta y el corpus son
     los de ese commit, y tu base se hizo con ellos.
   - **Cuando subas de commit, regenera la base.** Un juez distinto se avisa y la base propuesta lo marca (`juez_cambiado`).

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
- **Las entradas se escriben tal cual en las órdenes del flujo.** No pases en ellas texto que controle otro, como
  `github.head_ref` o el título de un PR.
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

## Cómo repetirlo en tu máquina

```bash
python3 cv/verificar_conversor.py ci/adaptador.json <salida> --artefactos <artefactos> --sin-sensibilidad
python3 cv/ci/linea_base.py comparar <salida> ci/LINEA-BASE.json
```

`comparar` sale con 0 si el veredicto es el esperado y con 10 si no; `VEREDICTO-CI.md` lo cuenta.
