# Diseño de la etapa 24: lo abierto de la integración continua (diseño a ciegas, Fable, 26-oct-2026)

Encargo: `cv/ci/ENCARGO-CI20.md`. Marco fijado: `ANTES-ETAPA-CI2.md`. Leído solo el repositorio público en el commit
`0f85437` (el del resultado de la etapa 23) y el ANTES. Quien programe sigue este documento al pie de la letra; donde el
documento no decide, decide Jev (§11) o, si no hay pregunta, el programador anota una desviación DV-CI2-n en
`cv/ci/decisiones-qci2.md`, como en la etapa 23.

Convenciones: `C0` es `0f8543718e0ce004fb477bbd7da06cb7c44486ee`, el commit publicado del que parte la etapa; `C1` es el
commit del primer push de esta etapa (el flujo endurecido); `C2`, el del segundo (las llamadas por la forma remota). Donde un
YAML lleva `COMMIT_C1`, el programador escribe los 40 hex de `C1` cuando los conozca (§4.1). `SHA_CHECKOUT`,
`SHA_SETUP_PYTHON`, `SHA_UPLOAD` y `SHA_DOWNLOAD` son los commits de las cuatro acciones, obtenidos como dice §2.2, y
`DIGEST_PYTHON` el digest de `python:3.12-slim` obtenido como dice §3.3. En este documento las rutas de máquina van siempre
como `$VARIABLE/...`, por la guarda de rutas de la higiene; el programador las mantiene así en todo lo que publique.

## 0. Lo que se da por entendido de la etapa 23

- **El flujo** `verificador-conversor.yml` tiene un solo job, `verificar`, con diez pasos: checkout del proyecto en `proyecto/`;
  checkout del laboratorio (`inputs.laboratorio` en `inputs.laboratorio_ref`) en `lab/`; Python 3.12; «Entradas» (comprueba
  ficheros, `esperar`, el tipo de caja y el digest; crea `artefactos` y `trabajo/`); «Preparar» (la orden del proyecto, con red,
  con `LAB`, `PROYECTO`, `ARTEFACTOS` e `IMAGEN` en el entorno); «La imagen, por su digest» (`docker pull`, `fijar-imagen
  --etiquetar`, `docker tag`, `docker image inspect`); «El adaptador que corre» (proceso local); «Sembrar» (solo `juguete`);
  «Identidades» (`--solo-orden`, la huella, `huella_esperada`); «Verificar» (la herramienta, `set +e`, `rc` a `$GITHUB_OUTPUT`,
  0 y 4 siguen); «Veredicto» (`linea_base.py comparar`, el resumen a `$GITHUB_STEP_SUMMARY`, sale con 0 o 10); el artefacto
  `<nombre>-<intento>` con `if: always()`. Las siete salidas del job suben al `workflow_call`.
- **La demo** lo llama tres veces con `uses: ./.github/workflows/verificador-conversor.yml`, todo bajo `lab/`
  (`lab/verificador/cv/adaptadores/…`, `lab/verificador/cv/ci/LINEA-BASE-…`), `laboratorio_ref: ${{ github.sha }}`, y dos jobs
  de comprobación que leen `needs.<job>.outputs.*`. Corre en `push` a `main` y `pull_request` con `paths`, y a mano.
- **Lo que no se recorrió** (`RESULTADO-CI.md`, «Lo que no dice»): la forma remota con `proyecto/…` y un `preparar` propio; el
  modo `pasa`; `corpus`, `sin_corpus_lab`, `opciones`, `artefacto_completo`; `pull_request`; el camino en que el job se pone
  rojo (el positivo falla dentro del flujo y el job sale en verde).
- **Las cuatro observaciones de la revisión a ciegas:** (1) `${{ inputs.* }}` dentro de `run:`; (2) acciones por etiqueta;
  (3) `laboratorio_ref` por omisión `main`; (4) la demo nombra `LK-Corporation/lab-integraciones` por omisión y en un fork no
  funciona. **DV-CI-12:** GitHub corre `shell: bash` como `bash --noprofile --norc -eo pipefail`; los dos pasos que recogen un
  código llevan `set +e`, con P-CI-15 en rojo antes.
- **El ensayo** (`ensayo_flujo.py`) corre los pasos `run:` de los YAML en la máquina, evalúa `${{ }}` (inputs, steps, needs,
  jobs, github, `&&`, `||`, `!`, `==`, `!=`, `always()`, `success()`), emula `checkout` copiando el árbol, no emula
  `setup-python` ni `pip install`, lista lo que subiría `upload-artifact`. Solo admite `uses: ./…`, no evalúa `if:` de job, no
  conoce `download-artifact` ni `github.repository`, y lo que GitHub haga distinto (la propagación de salidas de un job
  fallido, la resolución del `uses:` remoto) no lo puede ver.

## 1. Las decisiones (S-CI2-n)

| Id | Decisión | Por qué, en una línea |
|---|---|---|
| S-CI2-1 | Cada paso `run:` recibe las entradas en su `env:`, con prefijo `IN_` (`IN_ADAPTADOR`, `IN_CORPUS`…), y **ningún `${{` queda dentro de ningún `run:` de ningún YAML del repositorio** (ni `inputs`, ni `steps`, ni `github`); `preparar` corre como `bash --noprofile --norc -euo pipefail -c "$IN_PREPARAR"` con `LAB`, `PROYECTO`, `ARTEFACTOS` e `IMAGEN` en el entorno, como antes | es la observación 1 llevada hasta donde una guarda estática la puede vigilar sin excepciones (P-CI-16) |
| S-CI2-2 | Toda acción va por commit de 40 hex con su etiqueta en comentario en la misma línea (`uses: actions/checkout@SHA_CHECKOUT  # v4.2.2`); el par `(sha, etiqueta)` y la orden con que se obtuvo quedan en `cv/ci/ACCIONES-CI.json`; se fija el commit al que apunta hoy la etiqueta mayor (`v4`, `v5`), que es el código que corrió en la etapa 23; también en `higiene.yml` | observación 2; fijar lo que ya corrió no cambia la conducta; la guarda (P-CI-17) exige el mismo sha para la misma acción en todos los YAML |
| S-CI2-3 | `laboratorio_ref` pasa a ser **obligatoria y un commit de 40 hex**; «Entradas» sale con 2 si no lo es; GitHub rechaza la llamada si falta. Rompe la compatibilidad con quien la omitía (corría `main` sin saberlo): se dice en `CI.md` y en `RESULTADO-CI2.md` | observación 3; una rama o etiqueta bajo un `uses:@sha` fijo vuelve a abrir el mismo agujero |
| S-CI2-4 | La demo pasa `laboratorio: ${{ github.repository }}` en sus tres `uses:`; el flujo conserva el valor por omisión `LK-Corporation/lab-integraciones` para terceros | observación 4; en un fork, `lab/` es el fork en su `github.sha`; un tercero sigue sin tener que escribirlo |
| S-CI2-5 | El proyecto de ejemplo vive en `ejemplo-ci/`, en la raíz, como lo tendría un tercero: `conversor.py` (Python, biblioteca estándar) que corre en `python:3.12-slim` por digest, `preparar.sh`, `ci/adaptador.json`, `corpus/*.hl7` (seis mensajes sintéticos propios), `ci/LINEA-BASE.json` y `ci/LINEA-BASE-propio.json`, `ci/DEFECTO.json`, `ci/sembrar.py`, `ci/hacer_base.sh`, `README.md` | `proceso_local` solo corre el juguete real (S-VC-4), así que el ejemplo va en Docker, que es lo que hará cualquier proyecto; una carpeta en la raíz se copia tal cual (Q-CI2-D-2) |
| S-CI2-6 | La forma remota se recorre desde `.github/workflows/ejemplo-ci.yml`, con `uses: LK-Corporation/lab-integraciones/.github/workflows/verificador-conversor.yml@C1` y `laboratorio_ref: C1`; `C1` es el commit del primer push, el que publica el flujo endurecido; por eso las llamadas van en un segundo push, `C2` | en `uses:` no caben expresiones y un commit no puede contener su propio hash; el flujo que se llama tiene que ser el endurecido |
| S-CI2-7 | `ejemplo-ci.yml` tiene dos llamadas: `ejemplo` (corpus del laboratorio más el propio, `opciones` por omisión, sin `artefacto_completo`) y `ejemplo-propio` (`sin_corpus_lab: true`, `opciones: '--sin-sensibilidad --json-solo'`, `artefacto_completo: true`), cada una con su base; `esperar` se omite en las dos (vale `pasa`) | así se recorren `corpus`, `sin_corpus_lab`, `opciones` y `artefacto_completo` y cada una tiene un efecto observable desde fuera (Q-CI2-D-5) |
| S-CI2-8 | Los jobs de comprobación (`ejemplo-comprobado`, `rojo-comprobado`) descargan el artefacto del flujo con `actions/download-artifact` y lo juzgan con `cv/ci/comprobar_ejemplo.py` y `cv/ci/comprobar_rojo.py`; las salidas `needs.*.outputs.*` se registran al lado y, en el run en rojo, no deciden | el artefacto existe aunque el job falle (`if: always()`), y no se sabe si GitHub propaga las salidas de un job llamado que falla (Q-CI2-D-4, L-CI2-2) |
| S-CI2-9 | El run en rojo es `.github/workflows/rojo-ci.yml`, fichero aparte, solo `workflow_dispatch`; siembra el defecto en `preparar`, sobre la copia del conversor en `$ARTEFACTOS`, nunca en `main`; llama al flujo con `esperar: pasa`; la corrida queda roja a propósito y `rojo-comprobado` (`needs: rojo`, `if: always()`) sale en verde si falló por lo sembrado y solo por eso | condición 5 del ANTES; un job `uses:` no admite `continue-on-error`, así que el rojo es rojo de verdad y se deja escrito |
| S-CI2-10 | El defecto sembrado del ejemplo: `F` sale como `male` (un `valor_distinto` en PID-8), un tipo distinto del de la etapa 23; el triple esperado de `DEFECTO.json` se confirma en el laboratorio con `comparar --esperar falla` antes de sellar, y si el juez da otro, se escribe el que dé | L-CI-8 decía que solo se había sembrado un dato perdido; el mecanismo es el de `sembrar_juguete.py` (Q-CI2-D-3) |
| S-CI2-11 | `pull_request` se recorre con una rama del propio repositorio que lleva el commit del resultado, abierta como PR y llevada a `main` por avance rápido, sin commit de fusión | ni fork ni repositorio nuevo; la historia de `main` sigue lineal (Q-CI2-D-1) |
| S-CI2-12 | Lo que no se rompe se comprueba por huella: `traer_resultados_ci.py --igual-a cv/ci/CORRIDA-CI-1.json` exige que `informe_sha256` de los tres artefactos de la demo en `C1` sea el de la etapa 23; antes del push, el ensayo local compara las mismas huellas | «los mismos informes byte a byte» ya está registrado en `CORRIDA-CI-1.json`; no hace falta la carpeta de trabajo del laboratorio |
| S-CI2-13 | Las pruebas nuevas son P-CI-16..27 en `cv/ci/prueba_ci.py`, sin Docker ni red, cada una con control negativo; P-CI-15 aprende a dar a cada paso su `env:` con los valores por omisión; P-CI-11..13 no cambian de fondo | «cada cambio del flujo, con su prueba en rojo antes» |
| S-CI2-14 | `ensayo_flujo.py` aprende: `--flujo`, el `uses:` remoto (lee el YAML de ese commit con `git show`), checkouts por commit (`git archive`), `github.repository`, `if:` de job, `download-artifact`, `--rojo <job>` y `--entrada k=v`; lo que no puede ensayar se escribe en su cabecera | el ensayo es lo que más pesó en la previsión de la 23 (DV-CI-10) |
| S-CI2-15 | La previsión se sella con `cv/ci/sellar_prevision_ci2.py` (copia adaptada del de la 23, sellos nuevos `PREVISION-CI2.json` y `SELLO-CI2.txt`) antes de `C1`; `cv/ci/github-ci2/` guarda los cuatro YAML tal como se sellan, `ejemplo-ci.yml` y `rojo-ci.yml` con el literal `COMMIT_C1`; en `C2`, P-CI-27 exige que los que corren sean esas plantillas con `COMMIT_C1` sustituido | lo que se sella es lo que corre, salvo los 40 hex que no pueden conocerse antes |
| S-CI2-16 | No cambian: el juez, `verificar_conversor.py`, `conversor_juguete.py`, `linea_base.py`, `sembrar_juguete.py`, `hacer_bases.py`, `POSITIVO-CI.json`, las tres bases de la 23, `cv/ci/github/` (las copias selladas de la 23) ni `SELLO-CI.txt` | condición 3 del ANTES; los sellos de la 23 no se tocan |
| S-CI2-17 | Dentro de la caja el conversor del ejemplo va en `/opt/conversor`; en documentos y guiones toda ruta de máquina va como `$VARIABLE/...` | la guarda de rutas de la higiene admite `/opt` y no admite una ruta que empiece por otra raíz ni la forma «nombre entre ángulos, barra, ruta» |
| S-CI2-18 | Pushes al público, cada uno por la opción B: `C1` (aparato y sello), `C2` (las dos llamadas remotas), la rama del resultado (`C3`, y `C4` con lo del PR) llevada a `main` por avance rápido, y `C5` con las corridas del commit publicado; tope, una sesión | el `uses:` remoto exige que `C1` exista; el PR exige una rama; el resultado del commit publicado solo se sabe después |

---

## 2. Los endurecimientos

### 2.1 Las entradas por variables de entorno

Regla: en `verificador-conversor.yml` (y en todos los YAML del repositorio) **ningún `run:` contiene la secuencia `${{`**. Cada
paso declara en `env:` lo que usa, con el prefijo `IN_` para las entradas del flujo y `RC_HERRAMIENTA` para el código de la
herramienta. Las expresiones siguen donde GitHub las evalúa sin pasar por un shell: `if:`, `with:` de una acción, `env:`,
`outputs:`, `name:`.

Consecuencias que el programador tiene que respetar:
- `preparar` es una orden del proyecto y se ejecuta como tal, pero desde una variable: `bash --noprofile --norc -euo pipefail
  -c "$IN_PREPARAR"`. Hereda el directorio de trabajo (`$GITHUB_WORKSPACE`) y las variables `LAB`, `PROYECTO`, `ARTEFACTOS`
  e `IMAGEN`, exactamente como antes. `CI.md` lo dice.
- `corpus` y `opciones` se parten por palabras con `read -ra`, que es la misma partición que hacía la interpolación sin
  comillas, sin expansión de comodines.
- `hallazgo_esperado` llega entero, entre comillas dobles; ya no depende de que el JSON no lleve comillas simples.
- Los nombres de los pasos y sus `id` no cambian: `entradas`, `identidades`, `verificar`, `veredicto` son los que leen P-CI-15 y
  el ensayo.

El YAML completo, `.github/workflows/verificador-conversor.yml` (copia sellada en `cv/ci/github-ci2/verificador-conversor.yml`):

```yaml
# Flujo reutilizable (etapa 23, endurecido en la etapa 24; verificador/cv/ci/CI.md): pasa un conversor HL7 v2 -> FHIR R4 por el
# verificador del laboratorio y falla solo si aparece un hallazgo que no esta en la linea base del proyecto. Sin secretos, solo
# lectura, sin escribir en ningun repositorio ni comentar en ningun PR. Las entradas llegan a cada paso por variables de
# entorno (ninguna ${{ }} dentro de un run:), las acciones van por commit y el laboratorio se fija a un commit obligatorio.
name: verificador-conversor

on:
  workflow_call:
    inputs:
      adaptador:          {type: string, required: true}
      artefactos:         {type: string, required: false, default: artefactos}
      preparar:           {type: string, required: false, default: ''}
      linea_base:         {type: string, required: true}
      imagen:             {type: string, required: false, default: ''}
      corpus:             {type: string, required: false, default: ''}
      sin_corpus_lab:     {type: boolean, required: false, default: false}
      opciones:           {type: string, required: false, default: '--sin-sensibilidad'}
      esperar:            {type: string, required: false, default: pasa}
      hallazgo_esperado:  {type: string, required: false, default: '[]'}
      huella_esperada:    {type: string, required: false, default: ''}
      laboratorio:        {type: string, required: false, default: LK-Corporation/lab-integraciones}
      laboratorio_ref:    {type: string, required: true}
      sembrar:            {type: string, required: false, default: ''}
      artefacto_completo: {type: boolean, required: false, default: false}
      nombre:             {type: string, required: false, default: verificador}
    outputs:
      resultado:        {value: "${{ jobs.verificar.outputs.resultado }}"}
      nuevos:           {value: "${{ jobs.verificar.outputs.nuevos }}"}
      nuevos_distintos: {value: "${{ jobs.verificar.outputs.nuevos_distintos }}"}
      arreglos:         {value: "${{ jobs.verificar.outputs.arreglos }}"}
      huella:           {value: "${{ jobs.verificar.outputs.huella }}"}
      imagen_digest:    {value: "${{ jobs.verificar.outputs.imagen_digest }}"}
      juez:             {value: "${{ jobs.verificar.outputs.juez }}"}

permissions:
  contents: read

env:
  TZ: UTC
  PYTHONDONTWRITEBYTECODE: "1"
  PYTHONHASHSEED: "0"

jobs:
  verificar:
    runs-on: ubuntu-latest
    timeout-minutes: 75
    outputs:
      resultado:        ${{ steps.veredicto.outputs.resultado }}
      nuevos:           ${{ steps.veredicto.outputs.nuevos }}
      nuevos_distintos: ${{ steps.veredicto.outputs.nuevos_distintos }}
      arreglos:         ${{ steps.veredicto.outputs.arreglos }}
      huella:           ${{ steps.veredicto.outputs.huella }}
      imagen_digest:    ${{ steps.veredicto.outputs.imagen_digest }}
      juez:             ${{ steps.veredicto.outputs.juez }}
    steps:
      - name: El proyecto (el repositorio que llama)
        uses: actions/checkout@SHA_CHECKOUT  # v4.2.2
        with:
          path: proyecto
          persist-credentials: false

      - name: El laboratorio, en el commit fijado
        uses: actions/checkout@SHA_CHECKOUT  # v4.2.2
        with:
          repository: ${{ inputs.laboratorio }}
          ref: ${{ inputs.laboratorio_ref }}
          path: lab
          persist-credentials: false

      - uses: actions/setup-python@SHA_SETUP_PYTHON  # v5.x.y
        with:
          python-version: "3.12"

      - name: Entradas
        id: entradas
        shell: bash
        env:
          IN_ADAPTADOR: ${{ inputs.adaptador }}
          IN_LINEA_BASE: ${{ inputs.linea_base }}
          IN_ESPERAR: ${{ inputs.esperar }}
          IN_IMAGEN: ${{ inputs.imagen }}
          IN_ARTEFACTOS: ${{ inputs.artefactos }}
          IN_LABORATORIO_REF: ${{ inputs.laboratorio_ref }}
        run: |
          set -euo pipefail
          if ! [[ "$IN_LABORATORIO_REF" =~ ^[0-9a-f]{40}$ ]]; then
            echo "laboratorio_ref tiene que ser un commit de 40 hex, el mismo que en uses: (era '$IN_LABORATORIO_REF')"; exit 2
          fi
          test -f "$IN_ADAPTADOR" || { echo "no existe el adaptador $IN_ADAPTADOR"; exit 2; }
          test -f "$IN_LINEA_BASE" || { echo "no existe la linea base $IN_LINEA_BASE"; exit 2; }
          case "$IN_ESPERAR" in pasa|igual|falla) ;; *) echo "esperar: pasa, igual o falla"; exit 2;; esac
          tipo=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["caja"]["tipo"])' "$IN_ADAPTADOR")
          echo "tipo=$tipo" >> "$GITHUB_OUTPUT"
          if [ "$tipo" = docker ] && ! [[ "$IN_IMAGEN" =~ ^[a-z0-9][a-z0-9._/:-]*@sha256:[0-9a-f]{64}$ ]]; then
            echo "con una caja de Docker hace falta la entrada imagen con digest: repo[:etiqueta]@sha256:<64 hex>"; exit 2
          fi
          mkdir -p "$IN_ARTEFACTOS" trabajo

      - name: Preparar el conversor (con red)
        if: inputs.preparar != ''
        shell: bash
        env:
          LAB: ${{ github.workspace }}/lab
          PROYECTO: ${{ github.workspace }}/proyecto
          ARTEFACTOS: ${{ github.workspace }}/${{ inputs.artefactos }}
          IMAGEN: ${{ inputs.imagen }}
          IN_PREPARAR: ${{ inputs.preparar }}
        run: |
          set -euo pipefail
          bash --noprofile --norc -euo pipefail -c "$IN_PREPARAR"

      - name: La imagen, por su digest
        if: steps.entradas.outputs.tipo == 'docker'
        shell: bash
        env:
          IN_ADAPTADOR: ${{ inputs.adaptador }}
          IN_IMAGEN: ${{ inputs.imagen }}
        run: |
          set -euo pipefail
          docker version --format '{{.Server.Version}}'
          docker pull "$IN_IMAGEN"
          python3 lab/verificador/cv/ci/linea_base.py fijar-imagen "$IN_ADAPTADOR" "$IN_IMAGEN" \
            -o trabajo/adaptador.json --etiquetar > trabajo/etiquetar.sh || { cat trabajo/etiquetar.sh; exit 2; }
          bash -euo pipefail trabajo/etiquetar.sh
          docker image inspect --format '{{index .RepoDigests 0}}' -- "$(python3 -c 'import json; print(json.load(open("trabajo/adaptador.json"))["caja"]["imagen"])')"

      - name: El adaptador que corre (proceso local)
        if: steps.entradas.outputs.tipo != 'docker'
        shell: bash
        env:
          IN_ADAPTADOR: ${{ inputs.adaptador }}
        run: |
          set -euo pipefail
          python3 lab/verificador/cv/ci/linea_base.py fijar-imagen "$IN_ADAPTADOR" "" -o trabajo/adaptador.json

      - name: Sembrar (solo el control positivo de la demostracion)
        if: inputs.sembrar == 'juguete'
        shell: bash
        run: python3 lab/verificador/cv/ci/sembrar_juguete.py lab/verificador/cv/conversor_juguete.py

      - name: Identidades, antes de la caja
        id: identidades
        shell: bash
        env:
          IN_ARTEFACTOS: ${{ inputs.artefactos }}
          IN_HUELLA_ESPERADA: ${{ inputs.huella_esperada }}
        run: |
          set -euo pipefail
          cd lab/verificador
          python3 cv/verificar_conversor.py "$GITHUB_WORKSPACE/trabajo/adaptador.json" "$GITHUB_WORKSPACE/trabajo/orden" \
            --artefactos "$GITHUB_WORKSPACE/$IN_ARTEFACTOS" --solo-orden | tee "$GITHUB_WORKSPACE/trabajo/solo-orden.txt"
          huella=$(sed -n 's/^\[3\/9\] huella del conversor: \([0-9a-f]\{64\}\)$/\1/p' "$GITHUB_WORKSPACE/trabajo/solo-orden.txt")
          test -n "$huella"
          echo "huella=$huella" >> "$GITHUB_OUTPUT"
          if [ -n "$IN_HUELLA_ESPERADA" ] && [ "$huella" != "$IN_HUELLA_ESPERADA" ]; then
            echo "la huella del conversor es $huella y se esperaba $IN_HUELLA_ESPERADA"; exit 11
          fi

      - name: Verificar (la caja de la herramienta, sin red, solo lectura, sin privilegios)
        id: verificar
        shell: bash
        env:
          IN_ARTEFACTOS: ${{ inputs.artefactos }}
          IN_CORPUS: ${{ inputs.corpus }}
          IN_SIN_CORPUS_LAB: ${{ inputs.sin_corpus_lab }}
          IN_OPCIONES: ${{ inputs.opciones }}
        run: |
          set +e                    # GitHub corre «bash -eo pipefail»: aqui el codigo se recoge, no corta el paso
          set -uo pipefail
          cd lab/verificador
          args=()
          read -ra corpus <<< "$IN_CORPUS"
          for c in "${corpus[@]}"; do args+=(--corpus "$GITHUB_WORKSPACE/$c"); done
          if [ "$IN_SIN_CORPUS_LAB" = "true" ]; then args+=(--sin-corpus-lab); fi
          read -ra opciones <<< "$IN_OPCIONES"
          python3 cv/verificar_conversor.py "$GITHUB_WORKSPACE/trabajo/adaptador.json" "$GITHUB_WORKSPACE/trabajo/corrida" \
            --artefactos "$GITHUB_WORKSPACE/$IN_ARTEFACTOS" "${args[@]}" "${opciones[@]}"
          rc=$?
          echo "rc=$rc" >> "$GITHUB_OUTPUT"
          echo "verificar_conversor salio con $rc"
          case $rc in 0|4) exit 0;; *) exit $rc;; esac

      - name: Veredicto frente a la linea base
        id: veredicto
        shell: bash
        env:
          IN_LINEA_BASE: ${{ inputs.linea_base }}
          IN_ESPERAR: ${{ inputs.esperar }}
          IN_HALLAZGO_ESPERADO: ${{ inputs.hallazgo_esperado }}
          RC_HERRAMIENTA: ${{ steps.verificar.outputs.rc }}
        run: |
          set +e                    # GitHub corre «bash -eo pipefail»: aqui el codigo se recoge, no corta el paso
          set -uo pipefail
          python3 lab/verificador/cv/ci/linea_base.py comparar trabajo/corrida "$IN_LINEA_BASE" \
            --esperar "$IN_ESPERAR" --hallazgo-esperado "$IN_HALLAZGO_ESPERADO" \
            --rc-herramienta "$RC_HERRAMIENTA" --github-output "$GITHUB_OUTPUT" -o trabajo/corrida
          rc=$?
          cat trabajo/corrida/VEREDICTO-CI.md >> "$GITHUB_STEP_SUMMARY"
          exit $rc

      - name: El informe, como artefacto
        if: always()
        uses: actions/upload-artifact@SHA_UPLOAD  # v4.x.y
        with:
          name: ${{ inputs.nombre }}-${{ github.run_attempt }}
          retention-days: 14
          if-no-files-found: warn
          path: |
            trabajo/corrida/INFORME.md
            trabajo/corrida/INFORME.json
            trabajo/corrida/juicio.jsonl
            trabajo/corrida/CORRIDA.json
            trabajo/corrida/ADAPTADOR.json
            trabajo/corrida/VEREDICTO-CI.json
            trabajo/corrida/VEREDICTO-CI.md
            trabajo/corrida/LINEA-BASE-propuesta.json
            trabajo/corrida/cajas/
            trabajo/solo-orden.txt
            ${{ inputs.artefacto_completo && 'trabajo/corrida/evidencias/' || '' }}
            ${{ inputs.artefacto_completo && 'trabajo/corrida/corpus/' || '' }}
```

Lo que cambia respecto a la 23, para que el programador lo vea de un vistazo: el comentario de cabecera; `laboratorio_ref`
sin `default` y con `required: true`; los tres `uses:` por sha; el bloque `env:` de los pasos «Entradas», «Preparar»
(`IN_PREPARAR`), «La imagen», «El adaptador», «Identidades», «Verificar» y «Veredicto»; la comprobación de 40 hex y el
nombre del segundo checkout; `read -ra` para `corpus` y `opciones`; `"$IN_HALLAZGO_ESPERADO"` entre comillas dobles. Nada más:
ni el orden de los pasos, ni los `id`, ni las salidas, ni la lista del artefacto, ni la caja.

### 2.2 Las acciones fijadas por commit

Cuatro acciones: `actions/checkout`, `actions/setup-python`, `actions/upload-artifact` y, nueva en esta etapa,
`actions/download-artifact`. El commit que se fija es **el que hoy resuelve la etiqueta mayor** (`v4`, `v5`, `v4`, `v4`): es el
código que corrió en la etapa 23 (y, para `download-artifact`, el que correría si se usara por etiqueta), así que fijarlo no
cambia la conducta. El programador tiene red; el diseñador no, y por eso los sha van aquí como `SHA_CHECKOUT`,
`SHA_SETUP_PYTHON`, `SHA_UPLOAD`, `SHA_DOWNLOAD`. Cómo se obtienen, acción por acción:

```bash
# 1. El commit al que apunta la etiqueta mayor. Si la etiqueta es anotada, el commit es la linea «^{}» (el objeto apuntado);
#    si no hay linea «^{}», el commit es el de la linea de la etiqueta.
git ls-remote --tags https://github.com/actions/checkout | grep -E 'refs/tags/v4(\^\{\})?$'
# 2. Todas las etiquetas que apuntan a ese commit: se toma la mas concreta, vX.Y.Z; es la que va en el comentario.
git ls-remote --tags https://github.com/actions/checkout | grep '<sha del paso 1>'
# 3. La comprobacion cruzada por la API, que tiene que dar el mismo commit:
gh api repos/actions/checkout/git/ref/tags/vX.Y.Z --jq '.object.type + " " + .object.sha'
#    si el tipo es «tag» (anotada), se desreferencia y el .object.sha resultante es el commit:
gh api repos/actions/checkout/git/tags/<sha del objeto tag> --jq '.object.sha'
#    y el commit existe en ese repositorio, con su fecha:
gh api repos/actions/checkout/commits/<sha> --jq '.sha + " " + .commit.committer.date'
```

Lo mismo con `actions/setup-python` (`v5`), `actions/upload-artifact` (`v4`) y `actions/download-artifact` (`v4`). Si para
alguna el paso 1 y el paso 3 no dan el mismo commit, no se fija nada y se para: se anota en `decisiones-qci2.md` y se pregunta
a Jev entre fijar el commit del `ls-remote` o el de la API.

El registro, `cv/ci/ACCIONES-CI.json` (formato `acciones-ci/1`; entra en `JSON_ADMITIDOS`):

```json
{
 "formato": "acciones-ci/1",
 "_que": "Las acciones de GitHub que usan los flujos del repositorio, fijadas por commit (etapa 24, S-CI2-2). P-CI-17 exige que cada uses: lleve este sha y esta etiqueta en comentario, y el mismo sha en todos los YAML.",
 "fecha": "2026-10-26",
 "como": "git ls-remote --tags https://github.com/<accion>: el commit al que apunta la etiqueta mayor ese dia, cruzado con gh api repos/ACCION/git/ref/tags/ETIQUETA",
 "acciones": {
  "actions/checkout":          {"etiqueta": "vX.Y.Z", "mayor": "v4", "sha": "<40 hex>", "ls_remote": ["<linea del paso 1>", "<linea del paso 2 con vX.Y.Z>"], "api": "<salida del paso 3>"},
  "actions/setup-python":      {"etiqueta": "vX.Y.Z", "mayor": "v5", "sha": "<40 hex>", "ls_remote": ["…"], "api": "…"},
  "actions/upload-artifact":   {"etiqueta": "vX.Y.Z", "mayor": "v4", "sha": "<40 hex>", "ls_remote": ["…"], "api": "…"},
  "actions/download-artifact": {"etiqueta": "vX.Y.Z", "mayor": "v4", "sha": "<40 hex>", "ls_remote": ["…"], "api": "…"}
 }
}
```

Forma exacta de cada `uses:` en todos los YAML (la guarda P-CI-17 lee la línea cruda): `uses: actions/<nombre>@<40 hex>  # vX.Y.Z`,
dos espacios antes de `#`, la etiqueta la de `ACCIONES-CI.json`. `higiene.yml` cambia sus dos `uses:` (`checkout` y
`setup-python`) y nada más.

Cómo se comprueba después (en `RESULTADO-CI2.md`, «Cómo repetirlo»): `git ls-remote --tags https://github.com/actions/checkout |
grep <sha>` tiene que listar la etiqueta del comentario; si GitHub moviera la etiqueta mayor, el flujo seguiría corriendo el
commit fijado, que es el objetivo.

### 2.3 `laboratorio_ref`

- **Obligatoria** (`required: true`, sin `default`) y **un commit de 40 hex** (lo comprueba «Entradas», código 2 con el motivo).
- **Quien ya lo usaba:** la demo siempre lo daba (`${{ github.sha }}`), y `CI.md` pedía a un tercero fijarlo a un commit; quien
  lo omitió corría `main` sin saberlo, y ahora su llamada no arranca (GitHub: «Required input 'laboratorio_ref' not
  provided») hasta que lo dé; quien lo daba como rama o etiqueta recibe el código 2 con el mensaje. Ninguno de los dos casos
  era una llamada que el laboratorio quisiera sostener. Es una ruptura de compatibilidad y se dice en `CI.md` («Lo que cambia
  desde la etapa 24») y en `RESULTADO-CI2.md`.
- **`CI.md`** cambia el ejemplo de llamada (`laboratorio_ref: <el mismo commit de 40 hex que en uses:>`), la viñeta «Fija el
  laboratorio a un commit» (ahora: «es obligatorio, y tiene que ser el commit entero; una rama o una etiqueta se rechazan») y
  añade la sección §14.1.

### 2.4 El repositorio del laboratorio en la demostración

En `demo-ci.yml`, los tres jobs `negativo`, `positivo` y `real` añaden una línea a su `with:`:

```yaml
      laboratorio: ${{ github.repository }}
```

En un fork, `lab/` es el fork en `github.sha`, el mismo árbol que `proyecto/`; en el repositorio del laboratorio es
`LK-Corporation/lab-integraciones`, como antes. Los otros cambios de `demo-ci.yml`: los `uses:` de acción por sha (`pruebas` y
`positivo-comprobado`), y el comentario del job `pruebas` pasa a «P-CI-1..27». La copia sellada va en
`cv/ci/github-ci2/demo-ci.yml`. `ejemplo-ci.yml` y `rojo-ci.yml` llevan `laboratorio: LK-Corporation/lab-integraciones` escrito
(no `github.repository`): en un fork, llamarían al laboratorio original en `C1`, que es exactamente lo que haría un tercero y
funciona porque `C1` existe allí.

---
## 3. El proyecto de ejemplo: `ejemplo-ci/`

Es lo que tendría un tercero, dentro del repositorio del laboratorio y con sus rutas de tercero (`proyecto/ejemplo-ci/…` en
el runner). Con Q-CI2-D-2 (b), todo lo de abajo se mueve a `verificador/cv/ci/ejemplo/` y cambian solo las rutas.

```
ejemplo-ci/
  README.md             que es, como copiarlo a un proyecto, como se hace la base, como se repite el run en rojo
  conversor.py          el conversor HL7 v2 -> FHIR R4 del ejemplo (Python 3, biblioteca estandar, determinista)
  preparar.sh           deja el conversor en $ARTEFACTOS/conv/conversor.py (la orden «preparar» del proyecto)
  corpus/
    EJ-ADT-A01.hl7      seis mensajes sinteticos propios (ver 3.4)
    EJ-ADT-A03.hl7
    EJ-ADT-A08.hl7
    EJ-ORU-R01.hl7
    EJ-ORU-R01-dos.hl7
    EJ-VXU-V04.hl7
  ci/
    adaptador.json      adaptador-vc/1, caja docker python:3.12-slim por digest
    LINEA-BASE.json     la base del corpus del laboratorio + el propio (343 + 6 casos)
    LINEA-BASE-propio.json   la base del corpus propio solo (6 casos), para la llamada con sin_corpus_lab
    DEFECTO.json        el defecto del run en rojo: reemplazo exacto y unico, y el triple esperado
    sembrar.py          aplica o deshace DEFECTO.json sobre un fichero (como cv/ci/sembrar_juguete.py, con el JSON por argumento)
    hacer_base.sh       crea y comprueba las dos bases y el defecto en una maquina con Docker (el recetario de CI.md, en un guion)
```

### 3.1 El conversor: `ejemplo-ci/conversor.py`

Un conversor de verdad en lo que importa (lee HL7 v2 y escribe Bundles FHIR R4), pequeño, sin dependencias, determinista. No
copia `conversor_juguete.py` ni importa nada del juez (CV1-b). Lo que hace, exactamente:

- **Invocación:** `python3 conversor.py <entrada_dir> <salida_dir>`; recorre `*.hl7` de la entrada en orden alfabético; por cada
  uno escribe `<salida_dir>/<base>.json` (el Bundle) o `<salida_dir>/<base>.error` (una línea con el motivo); imprime
  `<nombre> <ms> ms` por mensaje; sale con 0 siempre que la carpeta de salida sea escribible.
- **Lectura:** separa segmentos por `\r`, `\n` o `\r\n`; campos por `|` (MSH-1 es el propio `|`, MSH-2 son los separadores);
  componentes por `^`; de una repetición (`~`) solo la primera; los subcomponentes (`&`) no se interpretan. Accesos como
  `campo("PID", 7)` y `comp("PID", 3, 1)`, con `""` si no hay.
- **Fechas:** `YYYYMMDD` → `YYYY-MM-DD`; `YYYYMMDDHHMMSS[.s][+-ZZZZ]` → `YYYY-MM-DDTHH:MM:SS` más `+HH:MM` si lleva
  desplazamiento; `YYYYMM` → `YYYY-MM`; si no cabe en esas formas, el campo se omite.
- **Números:** cuando un valor numérico va al JSON (OBX-5 con OBX-2 = `NM`, RXA-6), se escribe **con el texto literal** del
  mensaje (`1.20` queda `1.20`), con el mismo truco del juguete: un marcador en el objeto y un reemplazo en el texto JSON ya
  serializado. Si el texto no es un número JSON válido, va como `valueString`.
- **Siempre, si hay PID:** un `Patient` (`id` `p1`): `identifier[0].value` = PID-3.1, `.type.coding[0]` =
  `{system: v2-0203, code: PID-3.5}` si PID-3.5; `name[0]` = `{family: PID-5.1, given: [PID-5.2, PID-5.3 si hay], use: "official"}`;
  `birthDate` de PID-7; `gender` por la tabla `GENERO` (abajo), omitido si PID-8 no está en ella; `address[0]` de PID-11
  (`line: [PID-11.1]`, `city` .3, `state` .4, `postalCode` .5, `country` .6) si PID-11.1; `telecom[0]`
  `{system: "phone", value: PID-13.12 o PID-13.1, use: "home"}` si alguno; `maritalStatus` `{v3-MaritalStatus, PID-16}` si PID-16.
- **ADT (MSH-9.1 = `ADT`) y hay PV1:** un `Encounter` (`id` `e1`): `status` `finished` si el evento (MSH-9.2) es `A03`, si no
  `in-progress`; `class` `{system: v3-ActCode, code: CLASE[PV1-2]}` con `CLASE = {"E": "EMER", "I": "IMP", "O": "AMB",
  "P": "PRENC"}`, omitido si no está; `identifier[0].value` = PV1-19.1 si hay; `subject` → `urn:uuid:p1`; `period.start` de
  PV1-44 y `period.end` de PV1-45 si hay; `serviceType` `{service-type, PV1-10}` si PV1-10.
- **ORU (MSH-9.1 = `ORU`):** por cada OBR un `DiagnosticReport` (`id` `d<n>`): `identifier` con PLAC (OBR-2.1) y FILL
  (OBR-3.1) si hay, `status` por `ESTADO_OBR = {"F": "final", "P": "preliminary", "C": "corrected", "X": "cancelled"}` sobre
  OBR-25 (si no está, `"unknown"`), `code` de OBR-4 (`code` .1, `display` .2, `system` `http://loinc.org` si .3 es `LN`),
  `subject`, `effectiveDateTime` de OBR-7, `issued` de OBR-22, `result` con las referencias de sus OBX. Por cada OBX, un
  `Observation` (`id` `o<n>`): `status` por la misma tabla sobre OBX-11, `code` de OBX-3 con la misma regla, `subject`,
  `effectiveDateTime` de OBX-14; valor: `valueQuantity {value: <literal>, unit: OBX-6.1, system: unitsofmeasure si OBX-6.3 es
  UCUM, code: OBX-6.1}` si OBX-2 es `NM`, `valueString` OBX-5 si no; `interpretation[0]` `{v3-ObservationInterpretation,
  OBX-8}` si OBX-8; `referenceRange[0].text` OBX-7 si OBX-7.
- **VXU (MSH-9.1 = `VXU`):** por cada RXA un `Immunization` (`id` `i<n>`): `status` `not-done` si RXA-20 es `RE` o RXA-18 no
  está vacío, si no `completed`; `vaccineCode` de RXA-5 (`system` `http://hl7.org/fhir/sid/cvx` si .3 es `CVX`);
  `patient` → `urn:uuid:p1`; `occurrenceDateTime` de RXA-3; `lotNumber` RXA-15; `expirationDate` de RXA-16;
  `doseQuantity {value: <literal RXA-6>, unit: RXA-7.1, system: unitsofmeasure si RXA-7.3 es UCUM, code: RXA-7.1}` si RXA-6;
  `route` `{http://terminology.hl7.org/CodeSystem/v2-0162, RXR-1.1}` y `site` `{v2-0163, RXR-2.1}` del RXR que sigue al RXA, si hay.
- **Otro MSH-9.1:** se escribe `<base>.error` con `tipo no soportado: <MSH-9>`.
- **El Bundle:** `{"resourceType": "Bundle", "type": "collection", "entry": [{"fullUrl": "urn:uuid:<id>", "resource": …}]}`,
  en el orden Patient, Encounter, DiagnosticReport, Observation…, Immunization…; `json.dumps(…, ensure_ascii=False,
  indent=1)` y después el reemplazo de los marcadores numéricos. Codificación UTF-8.
- **La tabla de género, en una línea propia y única del fichero**, porque es lo que siembra el run en rojo:

```python
GENERO = {"F": "female", "M": "male", "O": "other", "U": "unknown", "A": "other", "N": "other"}   # tabla 0001
```

Que el conversor haga muchas cosas mal a ojos del juez no importa: eso es lo que la base registra. Lo que importa es que sea
determinista (P-CI-24: dos corridas, mismos ficheros byte a byte) y que el único cambio del defecto sembrado sea el género.

### 3.2 `ejemplo-ci/preparar.sh`

```bash
#!/usr/bin/env bash
# El proyecto de ejemplo (etapa 24, verificador/cv/ci/CI.md): deja el conversor donde el adaptador lo espera,
# $ARTEFACTOS/conv/conversor.py. Es la orden «preparar» del proyecto; este conversor no necesita red ni construccion.
#   bash ejemplo-ci/preparar.sh <artefactos>
set -euo pipefail
ART=$(realpath "$1")
AQUI=$(dirname "$(realpath "$0")")
mkdir -p "$ART/conv"
cp "$AQUI/conversor.py" "$ART/conv/conversor.py"
echo "conv/conversor.py: $(sha256sum "$ART/conv/conversor.py" | cut -c1-16)"
```

(En el comentario la ruta va como `$ARTEFACTOS/conv/conversor.py`, con la variable delante, que es la forma que la guarda
de rutas admite; el programador no escribe variantes.)

### 3.3 El adaptador: `ejemplo-ci/ci/adaptador.json`

`DIGEST_PYTHON` se obtiene una vez, en una máquina con Docker y red:
`docker pull python:3.12-slim && docker image inspect --format '{{index .RepoDigests 0}}' python:3.12-slim` → `python@sha256:<64 hex>`.
Ese digest va aquí, en los dos YAML (§4.2, §5.1) y en `hacer_base.sh`; P-CI-23 exige que los cuatro coincidan. Si más adelante
se quiere otra imagen, se cambia en los cuatro sitios y se regeneran las bases (la base registra `imagen_digest`).

```json
{
 "formato": "adaptador-vc/1",
 "id": "ejemplo",
 "_que": "El proyecto de ejemplo de la integracion continua (etapa 24): un conversor en Python que corre en la imagen oficial de Python, sin red, un proceso para toda la carpeta. Las rutas son relativas a --artefactos, que preparar.sh rellena.",
 "conversor": {
  "nombre": "ejemplo-ci",
  "version": "1",
  "huella": {"partes": [{"carpeta": "conversor"}]},
  "declara": {"no_soporta": []}
 },
 "caja": {
  "tipo": "docker",
  "imagen": "python:3.12-slim",
  "imagen_digest": "sha256:DIGEST_PYTHON",
  "_imagen_digest": "el mismo que pasan ejemplo-ci.yml y rojo-ci.yml en la entrada imagen; con otro, la herramienta sale con 3",
  "montajes": {"conversor": {"origen": "conv", "destino": "/opt/conversor"}},
  "entorno": {"PYTHONDONTWRITEBYTECODE": "1"},
  "limites": {"segundos_por_mensaje": 5, "segundos_por_contenedor": 300, "pids": 64, "memoria_mb": null}
 },
 "invocacion": {
  "modo": "lote",
  "orden": ["python3", "/opt/conversor/conversor.py", "{entrada_dir}", "{salida_dir}"],
  "plantilla": null,
  "duracion_stdout": "^(?P<nombre>\\S+) (?P<ms>\\d+) ms$"
 },
 "salida": {"fichero": "{base}.json", "fichero_error": "{base}.error", "forma": "bundle", "envoltura": null, "codificacion": "utf-8"}
}
```

`{"carpeta": "conversor"}` es el nombre del montaje y `_parte` lo resuelve a `conv` bajo `--artefactos`; la huella es la del
contenido de `conv/`, es decir, del conversor. `/opt/conversor` es una raíz neutra para la guarda de rutas (S-CI2-17).

### 3.4 El corpus sintético propio: `ejemplo-ci/corpus/*.hl7`

Seis mensajes, uno por fichero, segmentos separados por salto de línea (`normal()` los pasa a `\r`), UTF-8, sin BOM. Son
calcos de la forma de `prueba_conversion.msg()`, `oru_msg()` y `bases_vxu.cable(BASES[0])`, con los valores cambiados para
que sean inconfundiblemente del ejemplo: identificadores `EJ-…`, apellido `Ejemplo`, sin correos, sin direcciones IP, sin
nombres de fabricantes reales. Al menos dos con PID-8 `F` y dos con `M`, para que el defecto sembrado toque a unos y no a
otros. El caso en el veredicto es `propio/<nombre sin .hl7>`.

```
EJ-ADT-A01.hl7
MSH|^~\&|EJ-HIS|EJ|LAB|LAB|20260301120000||ADT^A01^ADT_A01|EJ-ADT-A01|P|2.5
EVN|A01|20260301120000
PID|1||EJ-0001^^^EJ^MR||Ejemplo^Ana^^^^^L||19900101|F|||Calle Uno 1^^Madrid^M^28001^ES^H||^PRN^PH^^^^^^^^^+34600000001|||S
PV1|1|I|URG^101^A^HOSP|E|||123^Ejemplo^Luis^^^Dr|||MED||||7|||||EJ-V1|||||||||||||||||01||||||||20260301100000+0100

EJ-ADT-A03.hl7
MSH|^~\&|EJ-HIS|EJ|LAB|LAB|20260302180000||ADT^A03^ADT_A03|EJ-ADT-A03|P|2.5
EVN|A03|20260302180000
PID|1||EJ-0002^^^EJ^MR||Ejemplo^Pedro^Luis^^^^L||19751231|M|||Calle Dos 2^^Sevilla^SE^41001^ES^H|||||M
PV1|1|I|URG^102^B^HOSP|E|||123^Ejemplo^Luis^^^Dr|||MED||||7|||||EJ-V2|||||||||||||||||01||||||||20260301100000+0100|20260302180000+0100

EJ-ADT-A08.hl7
MSH|^~\&|EJ-HIS|EJ|LAB|LAB|20260303090000||ADT^A08^ADT_A08|EJ-ADT-A08|P|2.5
EVN|A08|20260303090000
PID|1||EJ-0003^^^EJ^MR||Ejemplo^Lucia^^^^^L||20100615|F|||Calle Tres 3^^Valencia^V^46001^ES^H||^PRN^PH^^^^^^^^^+34600000003|||S
PV1|1|O|CON^201^C^HOSP|R|||124^Ejemplo^Marta^^^Dra|||MED||||1|||||EJ-V3|||||||||||||||||||||||||20260303083000+0100

EJ-ORU-R01.hl7
MSH|^~\&|EJ-LIS|EJ|HIS|EJ|20260304080000||ORU^R01^ORU_R01|EJ-ORU-R01|P|2.5
PID|1||EJ-0001^^^EJ^MR||Ejemplo^Ana^^^^^L||19900101|F
OBR|1|EJ-PL1|EJ-FL1|A^Panel A^LN|||20260304070000+0100|20260304073000+0100||||||||||||||20260304080000+0100|||F
OBX|1|NM|2345-7^Glucosa^LN||5.30|mmol/L^mmol/L^UCUM|3.9-5.5|N|||F|||20260304070000+0100
OBX|2|ST|8251-1^Comentario^LN||sin incidencias||||||F

EJ-ORU-R01-dos.hl7
MSH|^~\&|EJ-LIS|EJ|HIS|EJ|20260305080000||ORU^R01^ORU_R01|EJ-ORU-R01-dos|P|2.5
PID|1||EJ-0002^^^EJ^MR||Ejemplo^Pedro^Luis^^^^L||19751231|M
OBR|1|EJ-PL2|EJ-FL2|B^Panel B^LN|||20260305070000+0100|20260305073000+0100||||||||||||||20260305080000+0100|||F
OBX|1|NM|718-7^Hemoglobina^LN||14.0|g/dL^g/dL^UCUM|13.0-17.0|N|||F|||20260305070000+0100
OBX|2|NM|6690-2^Leucocitos^LN||11.20|10*3/uL^10*3/uL^UCUM|4.0-10.0|H|||F|||20260305070000+0100
OBX|3|ST|8251-1^Comentario^LN||repetir en una semana||||||F

EJ-VXU-V04.hl7
MSH|^~\&|EJ-VAC|EJ|REGISTRO|SALUD|20260306110000||VXU^V04^VXU_V04|EJ-VXU-V04|P|2.5
PID|1||EJ-0004^^^EJ^MR||Ejemplo^Mateo^^^^^L||20230512|M
ORC|RE||EJ-VX-01^EJ-VAC
RXA|0|1|20260306100100|20260306100100|03^MMR^CVX|0.5|mL^^UCUM|||EJ-PR01^Ejemplo^Marta^^^DRA^^^EJ^L|||||EJ-LOT-01|202801|EJM^Fabricante Ejemplo^MVX|||CP|A|20260306101500
RXR|IM^Intramuscular^HL70162|LD^Deltoides izquierdo^HL70163
```

El programador los escribe tal cual (el `MSH-2` es `^~\&`, con la barra invertida literal). Si alguno sale `fuera de alcance`
o `indeterminado` en el juez, no se cambia: la base registra lo que el juez dijo. Lo que sí tiene que cumplirse (P-CI-23): seis
ficheros, cada uno empieza por `MSH|^~\&|`, MSH-9.1 en {ADT, ORU, VXU}, MSH-10 igual al nombre del fichero sin `.hl7`, y ninguno
contiene `@` ni una dirección IP.

### 3.5 El defecto: `ejemplo-ci/ci/DEFECTO.json` y `ejemplo-ci/ci/sembrar.py`

```json
{
 "formato": "defecto-ci/1",
 "fichero": "conversor.py",
 "de": "GENERO = {\"F\": \"female\", ",
 "a": "GENERO = {\"F\": \"male\", ",
 "hallazgo_esperado": [["PID-8", "fidelidad", "valor_distinto"]],
 "_que": "El run en rojo (etapa 24): la tabla de genero del conversor del ejemplo pasa a dar «male» para F. En cada caso con PID-8 = F y Patient en la salida, el juez ve PID-8 con otro valor; ningun otro triple cambia. Es el defecto de JUGUETE-GENERO (P-CI-3), sembrado en un conversor que no es el juguete.",
 "_confirmado": "<lo que dio comparar --esperar falla en el laboratorio: n de casos y nuevos_distintos; lo rellena hacer_base.sh>"
}
```

`hallazgo_esperado` es una hipótesis hasta que `hacer_base.sh` la confirma (§3.7, paso 9): si el juez da otro conjunto de
triples distintos (por ejemplo dos, uno por punto de entrada), el programador escribe en `hallazgo_esperado` **lo que dio**,
anota la diferencia en `_confirmado` y en `decisiones-qci2.md` (DV-CI2-n), y sigue: el run en rojo comprueba igualdad de
conjuntos, no que sea uno.

`sembrar.py` es `cv/ci/sembrar_juguete.py` con el JSON por argumento:
`python3 ejemplo-ci/ci/sembrar.py <fichero> <DEFECTO.json> [--deshacer]`; sale con 2 sin tocar nada si `de` no aparece
exactamente una vez; con 0 y el texto reemplazado si aparece una; `--deshacer` hace lo contrario. Solo biblioteca estándar.

### 3.6 Las dos bases

| Base | Corpus | Opciones de la corrida | Casos | Para qué llamada |
|---|---|---|---|---|
| `ci/LINEA-BASE.json` | el del laboratorio (ADT 263, ORU 40, VXU 40) + `corpus/` (6) | `--sin-sensibilidad --corpus ejemplo-ci/corpus` | 349 | `ejemplo` y `rojo` |
| `ci/LINEA-BASE-propio.json` | solo `corpus/` | `--sin-sensibilidad --json-solo --sin-corpus-lab --corpus ejemplo-ci/corpus` | 6 | `ejemplo-propio` |

Las dos salen del juez publicado (`b3f00f6a…`, el mismo que corre el runner: ni el juez ni `verificar_conversor.py` cambian
en esta etapa, así que `creada_de` es el de la 23), del conversor del ejemplo con su huella, y de la imagen por digest. Caben
bajo los 512 KB de la higiene (la del juguete, con 343 casos, ocupa 202 KB). Entran en `JSON_ADMITIDOS`.

### 3.7 Cómo se crea la base: `ejemplo-ci/ci/hacer_base.sh`

Corre en una máquina con Docker y la imagen, desde la raíz del repositorio público, una vez antes de sellar; es el recetario de
`CI.md` escrito en un guion, con las comprobaciones de `hacer_bases.py` (dos corridas iguales byte a byte, `igual` contra la
base, el defecto). Para en el primer paso que no cuadra.

```
bash ejemplo-ci/ci/hacer_base.sh <artefactos vacios> <trabajo vacio>
```

Pasos, en orden (`$ART`, `$TRABAJO`; las órdenes de la herramienta se lanzan con `cd verificador`):

1. `docker pull python:3.12-slim@sha256:DIGEST_PYTHON` y `docker tag python@sha256:DIGEST_PYTHON python:3.12-slim` (lo mismo que
   hará el flujo); `docker image inspect --format '{{index .RepoDigests 0}}' python:3.12-slim` tiene que contener el digest.
2. `bash ejemplo-ci/preparar.sh "$ART"`.
3. Corrida 1 completa: `python3 cv/verificar_conversor.py ../ejemplo-ci/ci/adaptador.json "$TRABAJO/ejemplo-1" --artefactos "$ART"
   --sin-sensibilidad --corpus ../ejemplo-ci/corpus`; código 0 y `CORRIDA.json` sin `sin_evidencia`.
4. Corrida 2, misma orden, en `$TRABAJO/ejemplo-2`; `cmp` de los dos `INFORME.json`.
5. `python3 cv/ci/linea_base.py crear "$TRABAJO/ejemplo-1" -o ../ejemplo-ci/ci/LINEA-BASE.json`; `n_casos` = 349.
6. `python3 cv/ci/linea_base.py comparar "$TRABAJO/ejemplo-2" ../ejemplo-ci/ci/LINEA-BASE.json --esperar igual -o "$TRABAJO/ejemplo-igual"` → 0.
7. Lo mismo (3-6) con `--json-solo --sin-corpus-lab` en `$TRABAJO/propio-1`, `propio-2`, base `LINEA-BASE-propio.json`,
   `n_casos` = 6.
8. `python3 ../ejemplo-ci/ci/sembrar.py "$ART/conv/conversor.py" ../ejemplo-ci/ci/DEFECTO.json` → 0.
9. Corrida sembrada en `$TRABAJO/ejemplo-sembrado` (como la 3);
   `comparar "$TRABAJO/ejemplo-sembrado" ../ejemplo-ci/ci/LINEA-BASE.json --esperar falla --hallazgo-esperado "$(python3 -c
   'import json; print(json.dumps(json.load(open("../ejemplo-ci/ci/DEFECTO.json"))["hallazgo_esperado"]))')" -o
   "$TRABAJO/ejemplo-sembrado-falla"` → 0; y `comparar … --esperar pasa -o "$TRABAJO/ejemplo-sembrado-pasa"` → **10**, con
   `motivos == ["hallazgo_nuevo"]` y `avisos` con `huella_distinta` y nada más. Si el primero da 10, se lee
   `nuevos_distintos` de `VEREDICTO-CI.json`, se escribe en `DEFECTO.json` (§3.5) y se repite el paso.
10. `sembrar.py … --deshacer`; `$ART/conv/conversor.py` vuelve a ser igual a `ejemplo-ci/conversor.py` (`cmp`).
11. Escribe `$TRABAJO/BASE-EJEMPLO.json`: huella del conversor, `huella_con_nombres`, digest, `n_casos` de las dos bases, las
    categorías por corpus, `rojo_n_casos` (casos con el triple en el paso 9) y `rojo_nuevos_distintos`. De ahí salen
    `rojo_n_casos_previsto` de la previsión y la cifra de `RESULTADO-CI2.md`. Ese fichero no entra en el repositorio;
    `DEFECTO.json._confirmado` recoge la cifra.

### 3.8 `ejemplo-ci/README.md`

Cuatro secciones cortas: qué es (un proyecto de conversor como lo tendría un tercero, con su llamada en
`.github/workflows/ejemplo-ci.yml`); qué copiar a un proyecto propio (`ci/adaptador.json`, `preparar.sh`, `ci/hacer_base.sh`, la
llamada, cambiando el conversor, la imagen con su digest y el corpus); cómo se hizo la base (§3.7, en dos órdenes); cómo se
repite el run en rojo (`rojo-ci.yml` a mano, y en una máquina: los pasos 8-10 de §3.7). Sin alusión a ninguna máquina ni sitio.

---

## 4. La forma remota

### 4.1 El commit que se fija y cuántos pushes

En `uses:` no caben expresiones y un commit no puede llevar dentro su propio hash. Por eso:

1. **Push 1 (`C1`):** el flujo endurecido, la demo con `laboratorio: ${{ github.repository }}`, `ejemplo-ci/`, las pruebas, la
   previsión sellada, `CI.md` y los READMEs. **Sin** `ejemplo-ci.yml` ni `rojo-ci.yml`. Corren `demo-ci` e `higiene`.
2. **Push 2 (`C2`):** `.github/workflows/ejemplo-ci.yml` y `rojo-ci.yml`, con `uses: …@C1` y `laboratorio_ref: C1` (los 40
   hex de `C1`, que ya existe), y P-CI-27 que lo exige. Corren `demo-ci`, `higiene` y `ejemplo-ci`; el flujo que llama
   `ejemplo-ci` es el de `C1`, idéntico al de `C2` (el push 2 no toca el flujo), así que lo que se mide es el flujo endurecido
   por la forma remota. `proyecto/` es el repositorio en `C2` y `lab/` es el repositorio en `C1`: dos refs distintas, como
   en una llamada de tercero.
3. **A mano, sobre `C2`:** `rojo-ci`.

El commit que queda fijado en el ejemplo es `C1`, y así se queda: si el flujo cambia después, el ejemplo seguirá llamando a
`C1` hasta que un commit posterior suba el pin, en dos pushes otra vez (L-CI2-12). `CI.md` lo dice: es lo que le pasa a
cualquier tercero.

Cómo conoce el programador `C1`: después del push 1, `git rev-parse HEAD` (o `git log -1 --format=%H`); los 40 hex se escriben
en los dos YAML con `sed "s/COMMIT_C1/$C1/g"` sobre las plantillas de `cv/ci/github-ci2/`, y P-CI-27 comprueba que el resultado
es esa sustitución y nada más.

### 4.2 `.github/workflows/ejemplo-ci.yml` (plantilla sellada en `cv/ci/github-ci2/ejemplo-ci.yml`, con `COMMIT_C1` literal)

```yaml
# El proyecto de ejemplo (etapa 24, ejemplo-ci/README.md): la llamada al flujo reutilizable por la forma remota, como la haria
# un tercero, fijada a un commit del laboratorio, con su adaptador, su linea base y su corpus, en el modo «pasa». Dos llamadas:
# con el corpus del laboratorio mas el propio, y solo con el propio (sin_corpus_lab, opciones y artefacto_completo). Un job de
# fuera descarga los artefactos y comprueba lo que tiene que salir.
name: ejemplo-ci

on:
  push:
    branches: [main]
    paths: ['ejemplo-ci/**', '.github/workflows/**', 'verificador/**']
  pull_request:
    paths: ['ejemplo-ci/**', '.github/workflows/**', 'verificador/**']
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ejemplo-ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  ejemplo:
    # el corpus del laboratorio mas el propio, contra ci/LINEA-BASE.json; esperar vale «pasa» por omision, como en un proyecto
    uses: LK-Corporation/lab-integraciones/.github/workflows/verificador-conversor.yml@COMMIT_C1
    permissions:
      contents: read
    with:
      adaptador: proyecto/ejemplo-ci/ci/adaptador.json
      linea_base: proyecto/ejemplo-ci/ci/LINEA-BASE.json
      preparar: bash "$PROYECTO/ejemplo-ci/preparar.sh" "$ARTEFACTOS"
      imagen: python:3.12-slim@sha256:DIGEST_PYTHON
      corpus: proyecto/ejemplo-ci/corpus
      laboratorio: LK-Corporation/lab-integraciones
      laboratorio_ref: COMMIT_C1
      nombre: ejemplo

  ejemplo-propio:
    # solo el corpus propio, sin INFORME.md y con evidencias y corpus en el artefacto, contra ci/LINEA-BASE-propio.json
    uses: LK-Corporation/lab-integraciones/.github/workflows/verificador-conversor.yml@COMMIT_C1
    permissions:
      contents: read
    with:
      adaptador: proyecto/ejemplo-ci/ci/adaptador.json
      linea_base: proyecto/ejemplo-ci/ci/LINEA-BASE-propio.json
      preparar: bash "$PROYECTO/ejemplo-ci/preparar.sh" "$ARTEFACTOS"
      imagen: python:3.12-slim@sha256:DIGEST_PYTHON
      corpus: proyecto/ejemplo-ci/corpus
      sin_corpus_lab: true
      opciones: '--sin-sensibilidad --json-solo'
      artefacto_completo: true
      laboratorio: LK-Corporation/lab-integraciones
      laboratorio_ref: COMMIT_C1
      nombre: ejemplo-propio

  ejemplo-comprobado:
    # desde fuera del flujo: los dos artefactos dicen lo que tienen que decir, y las salidas de los jobs cuadran con ellos
    needs: [ejemplo, ejemplo-propio]
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@SHA_CHECKOUT  # v4.2.2
        with:
          persist-credentials: false
      - uses: actions/download-artifact@SHA_DOWNLOAD  # v4.x.y
        with:
          name: ejemplo-${{ github.run_attempt }}
          path: artefacto-ejemplo
      - uses: actions/download-artifact@SHA_DOWNLOAD  # v4.x.y
        with:
          name: ejemplo-propio-${{ github.run_attempt }}
          path: artefacto-propio
      - shell: bash
        env:
          RESULTADO_EJEMPLO: ${{ needs.ejemplo.outputs.resultado }}
          HUELLA_EJEMPLO: ${{ needs.ejemplo.outputs.huella }}
          DIGEST_EJEMPLO: ${{ needs.ejemplo.outputs.imagen_digest }}
          RESULTADO_PROPIO: ${{ needs.ejemplo-propio.outputs.resultado }}
        run: |
          set -euo pipefail
          python3 verificador/cv/ci/comprobar_ejemplo.py artefacto-ejemplo artefacto-propio \
            ejemplo-ci/ci/LINEA-BASE.json ejemplo-ci/ci/LINEA-BASE-propio.json ejemplo-ci/ci/adaptador.json \
            --salidas "$RESULTADO_EJEMPLO" "$HUELLA_EJEMPLO" "$DIGEST_EJEMPLO" "$RESULTADO_PROPIO" -o comprobacion
      - if: always()
        uses: actions/upload-artifact@SHA_UPLOAD  # v4.x.y
        with:
          name: ejemplo-comprobado-${{ github.run_attempt }}
          retention-days: 14
          path: comprobacion/
```

(`needs.ejemplo-propio.outputs` con guion: GitHub lo admite en expresiones; si al validar el YAML lo rechazara, el job pasa a
llamarse `ejemplo_propio` y el artefacto `ejemplo_propio-<intento>`, y P-CI-21 y `traer_resultados_ci.py` usan ese nombre.)

### 4.3 Lo que tiene que salir, y cómo lo lee `cv/ci/comprobar_ejemplo.py`

`python3 cv/ci/comprobar_ejemplo.py <artefacto ejemplo> <artefacto propio> <LINEA-BASE.json> <LINEA-BASE-propio.json>
<adaptador.json> [--salidas <resultado> <huella> <digest> <resultado propio>] -o <carpeta>`; escribe
`<carpeta>/COMPROBACION-EJEMPLO.json` con cada comprobación y su valor, sale con 0 solo si todas son ciertas. Los artefactos
llegan sin el prefijo común `trabajo/` (como ya sabe `traer_resultados_ci.py`): `corrida/VEREDICTO-CI.json`, `solo-orden.txt`…

Del artefacto `ejemplo` (`corrida/VEREDICTO-CI.json`, `v`, y la base `B`):
- `v.esperado == "pasa"`, `v.resultado == "pasa"`, `v.pasa`, `v.veredicto_esperado`, `v.motivos == []`;
- `v.nuevos == []`, `v.arreglos == []`, `v.casos_nuevos == []`, `v.casos_ausentes == []`, `v.notas == []`,
  `v.cambios_de_categoria == []`, `v.avisos == {}` (ni `huella_distinta` ni `juez_distinto` ni `corpus_distinto` ni `imagen_distinta`:
  el conversor, el juez, el corpus y la imagen son los de la base);
- `v.n == {"base": B.n_casos, "corrida": B.n_casos, "comparados": B.n_casos}` y `B.n_casos == 349`;
- `v.identidades.huella == B.conversor.huella`, `v.identidades.imagen_digest == adaptador.caja.imagen_digest`,
  `v.identidades.juez == B.creada_de.juez.huella`;
- `corrida/INFORME.json` existe y su `corpus.n` es el de `B.corpus.n` (`propio` = 6, `adt` 263, `oru` 40, `vxu` 40, `minimos` 0,
  `muestras` 0); `corrida/INFORME.md` **existe** (sin `--json-solo`);
- el conjunto de rutas del artefacto es exactamente: `corrida/INFORME.md`, `corrida/INFORME.json`, `corrida/juicio.jsonl`,
  `corrida/CORRIDA.json`, `corrida/ADAPTADOR.json`, `corrida/VEREDICTO-CI.json`, `corrida/VEREDICTO-CI.md`,
  `corrida/LINEA-BASE-propuesta.json`, `solo-orden.txt`, y lo que haya bajo `corrida/cajas/`; **no** hay `corrida/evidencias/` ni
  `corrida/corpus/` («nada más»);
- `corrida/VEREDICTO-CI.md` empieza por `## Verificador: ejemplo · pasa · **PASA**`.

Del artefacto `ejemplo-propio` (`v2`, base `P`):
- las mismas igualdades del veredicto contra `P`, con `P.n_casos == 6` y todas las claves de `P.casos` con prefijo `propio/`;
- `corrida/INFORME.json` con `corpus.n == {"propio": 6}` y 0 en los demás (`sin_corpus_lab` quitó el laboratorio);
- **no** existe `corrida/INFORME.md` (`--json-solo` en `opciones`); el artefacto **tiene** `corrida/evidencias/` y
  `corrida/corpus/` con al menos un fichero cada una (`artefacto_completo`), y `corrida/corpus/` contiene exactamente los seis
  nombres del corpus propio;
- el resto del conjunto de rutas, como en `ejemplo`.

De `--salidas` (las salidas de los dos jobs, que en la 23 sí llegaron): `resultado == "pasa"` las dos, `huella ==
B.conversor.huella`, `digest == adaptador.caja.imagen_digest`. En este job las salidas **sí deciden** (los jobs salieron bien).

Eso cubre lo que mide el ANTES: «`corpus` con mensajes propios, `opciones` y `artefacto_completo` cambian lo que deben, y nada
más».

---
## 5. El run en rojo a propósito

### 5.1 `.github/workflows/rojo-ci.yml` (plantilla sellada en `cv/ci/github-ci2/rojo-ci.yml`, con `COMMIT_C1` literal)

Fichero aparte, solo a mano. El defecto se siembra en `preparar`, sobre la copia del conversor en `$ARTEFACTOS` que deja
`preparar.sh`: `main` no se toca, y es lo que le pasaría a un proyecto cuyo commit rompiera el género. Con `esperar: pasa`, la
comparación sale con 10, el job `rojo` queda en rojo, y `rojo-comprobado` lo lee desde fuera.

```yaml
# El run en rojo a proposito (etapa 24, verificador/cv/ci/CI.md): el proyecto de ejemplo con un defecto sembrado al preparar,
# llamado por la forma remota en el modo «pasa». El job «rojo» tiene que fallar; «rojo-comprobado» comprueba desde fuera que
# fallo por el hallazgo sembrado y solo por el, que dejo su resumen y que el artefacto lleva su veredicto. Solo a mano, nunca
# en cada push: la corrida queda roja a proposito.
name: rojo-ci

on:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: rojo-ci
  cancel-in-progress: false

jobs:
  rojo:
    # ejemplo-ci/ci/DEFECTO.json sembrado en la copia del conversor; la base es la de siempre; esperar vale «pasa» por omision
    uses: LK-Corporation/lab-integraciones/.github/workflows/verificador-conversor.yml@COMMIT_C1
    permissions:
      contents: read
    with:
      adaptador: proyecto/ejemplo-ci/ci/adaptador.json
      linea_base: proyecto/ejemplo-ci/ci/LINEA-BASE.json
      preparar: bash "$PROYECTO/ejemplo-ci/preparar.sh" "$ARTEFACTOS" && python3 "$PROYECTO/ejemplo-ci/ci/sembrar.py" "$ARTEFACTOS/conv/conversor.py" "$PROYECTO/ejemplo-ci/ci/DEFECTO.json"
      imagen: python:3.12-slim@sha256:DIGEST_PYTHON
      corpus: proyecto/ejemplo-ci/corpus
      laboratorio: LK-Corporation/lab-integraciones
      laboratorio_ref: COMMIT_C1
      nombre: rojo

  rojo-comprobado:
    # corre aunque «rojo» haya fallado (es lo que se espera): descarga su artefacto y lo juzga; las salidas del job se anotan
    needs: rojo
    if: always()
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@SHA_CHECKOUT  # v4.2.2
        with:
          persist-credentials: false
      - uses: actions/download-artifact@SHA_DOWNLOAD  # v4.x.y
        with:
          name: rojo-${{ github.run_attempt }}
          path: artefacto
      - shell: bash
        env:
          RESULTADO_JOB: ${{ needs.rojo.result }}
          RESULTADO: ${{ needs.rojo.outputs.resultado }}
          NUEVOS: ${{ needs.rojo.outputs.nuevos }}
          DISTINTOS: ${{ needs.rojo.outputs.nuevos_distintos }}
        run: |
          set -euo pipefail
          python3 verificador/cv/ci/comprobar_rojo.py artefacto ejemplo-ci/ci/DEFECTO.json ejemplo-ci/ci/LINEA-BASE.json \
            --resultado-job "$RESULTADO_JOB" --salidas "$RESULTADO" "$NUEVOS" "$DISTINTOS" -o comprobacion
      - if: always()
        uses: actions/upload-artifact@SHA_UPLOAD  # v4.x.y
        with:
          name: rojo-comprobado-${{ github.run_attempt }}
          retention-days: 14
          path: comprobacion/
```

### 5.2 Qué defecto lo pone en rojo

El de `DEFECTO.json` (§3.5): `F` → `male` en la tabla de género. Con `esperar: pasa`, cada caso de la base con PID-8 `F` y
`Patient` en la salida gana el triple `("PID-8", "fidelidad", "valor_distinto")`, que no estaba en su base → `hallazgo_nuevo`
→ `comparar` sale con 10 → el paso «Veredicto» escribe el resumen en la página y sale con 10 (P-CI-15) → el job `rojo`
falla → el artefacto `rojo-<intento>` se sube igual (`if: always()`). El conversor sembrado tiene otra huella, así que el
veredicto lleva además el aviso `huella_distinta`, que no decide en `pasa`: es la señal de que el flujo vio un conversor
cambiado, como en un commit real.

### 5.3 Cómo comprueba `rojo-comprobado` desde fuera: `cv/ci/comprobar_rojo.py`

`python3 cv/ci/comprobar_rojo.py <artefacto> <DEFECTO.json> <LINEA-BASE.json> --resultado-job <success|failure|cancelled|skipped>
[--salidas <resultado> <nuevos> <nuevos_distintos>] -o <carpeta>`. Escribe `<carpeta>/COMPROBACION-ROJO.json`
(`{"formato": "comprobacion-rojo/1", "comprobaciones": {<nombre>: true|false}, "salidas_del_job": …, "n_casos_con_el_hallazgo": n,
"todo_bien": bool}`) y sale con 0 solo si todas las comprobaciones son ciertas. Las comprobaciones, con su nombre:

| Nombre | Qué | Qué prueba |
|---|---|---|
| `job_fallido` | `--resultado-job == "failure"` | el job se puso rojo |
| `veredicto_en_el_artefacto` | existe `corrida/VEREDICTO-CI.json` y se lee | el artefacto lleva su veredicto aunque el job fallara |
| `esperaba_pasa` | `v.esperado == "pasa"` | era el modo de un proyecto, no `falla` |
| `fallo` | `v.resultado == "falla"`, `v.pasa == false`, `v.veredicto_esperado == false` | falló por la regla asimétrica |
| `solo_hallazgo_nuevo` | `v.motivos == ["hallazgo_nuevo"]`; `v.salida_perdida == []`, `v.indeterminado_nuevo == []`, `v.casos_ausentes == []` | no falló por la caja, ni por una salida perdida, ni por otra cosa |
| `el_hallazgo_esperado` | `sorted(v.nuevos_distintos) == sorted(DEFECTO.hallazgo_esperado)` como tuplas | por ese hallazgo y por ningún otro |
| `en_casos_de_la_base` | `len(v.nuevos) > 0`, cada `nuevos[i].caso` está en `B.casos`, y `v.casos_nuevos == []` | lo nuevo es nuevo en casos conocidos, no en casos que la base no tenía |
| `conversor_cambiado` | `"huella_distinta" in v.avisos` y ninguno de `juez_distinto`, `corpus_distinto`, `imagen_distinta` | cambió el conversor y nada más |
| `resumen` | existe `corrida/VEREDICTO-CI.md`, su primera línea es `## Verificador: ejemplo · pasa · **FALLA**` y contiene `### Hallazgos nuevos` | dejó su resumen: es el mismo texto que el paso vuelca en `$GITHUB_STEP_SUMMARY` antes de salir (P-CI-15) |
| `informe_y_propuesta` | existen `corrida/INFORME.json`, `corrida/juicio.jsonl` y `corrida/LINEA-BASE-propuesta.json`, y en la propuesta el primer caso de `v.nuevos` lleva el triple | el artefacto está entero y la propuesta recoge lo nuevo |

`--salidas` no decide: si `resultado` no está vacío, se comprueba que sea `falla`, que `nuevos` sea `len(v.nuevos)` y que
`nuevos_distintos` (JSON) sea `v.nuevos_distintos`, y una discrepancia sí hace fallar; si está vacío, se escribe
`"salidas_del_job": "vacias"` y no falla. Así la corrida registra si GitHub propaga las salidas de un job llamado que falla
(L-CI2-2), sin apostar el control a ello.

El resumen en la página del job no se puede leer por la API. Lo que se comprueba desde fuera es el fichero que lo produjo y
la mecánica que lo copia (P-CI-15); el programador, además, lo mira en la página de la corrida y lo anota en
`CORRIDA-CI2-3.json` (`"resumen_en_la_pagina": true`, visto a mano) — L-CI2-3.

### 5.4 Qué conclusión queda en la corrida

La corrida de `rojo-ci` queda **en rojo**: el job `rojo` falla (es el camino que el ANTES quiere ver), `rojo-comprobado` sale en
verde, y la conclusión de la corrida es `failure` porque un job `uses:` no admite `continue-on-error`. Eso es lo que se
publica: `CORRIDA-CI2-3.json` con `conclusion: failure`, `jobs.rojo / verificar: failure` con `pasos_fallidos: ["Veredicto frente
a la linea base"]` (solo ese paso), `jobs.rojo-comprobado: success`, y el `COMPROBACION-ROJO.json` del artefacto. En
`RESULTADO-CI2.md`: «el job se puso rojo por el hallazgo sembrado y solo por él, con su resumen y su artefacto; la corrida está
roja porque tiene que estarlo». No se borra ni se reintenta.

---

## 6. `pull_request`

Es Q-CI2-D-1. El diseño está escrito con la opción (a):

- **Qué se recorre:** `demo-ci` y `ejemplo-ci` tienen `on: pull_request` con `paths`; nunca han corrido con ese evento. Un PR del
  propio repositorio (una rama, ni fork ni repositorio nuevo) que toque `verificador/**` dispara los dos.
- **Cómo:** la rama `etapa-24-resultado` lleva `C3` (el resultado: `RESULTADO-CI2.md`, `CORRIDA-CI2-1..3.json`, los READMEs);
  se empuja y se abre el PR (`gh pr create --base main --head etapa-24-resultado`), con `permissions: contents: read` en todo
  lo que corre. Se leen las corridas del evento `pull_request` (dos: `demo-ci` y `ejemplo-ci`) y se traen con
  `traer_resultados_ci.py` a `CORRIDA-CI2-4.json` en un commit `C4` sobre la rama (el PR vuelve a correr, `synchronize`; de esa
  segunda corrida solo se anota la conclusión en `RESULTADO-CI2.md`).
- **Qué se hace con el PR después:** se lleva a `main` por avance rápido desde la máquina (`git checkout main && git merge
  --ff-only etapa-24-resultado && git push origin main`), no con el botón: así los commits publicados son exactamente `C3` y
  `C4`, sin commit de fusión ni reescritura, y GitHub marca el PR como fusionado al ver sus commits en `main`. La rama se borra
  (`git push origin --delete etapa-24-resultado`). La opción B se aplica a `C3` y a `C4` una vez, antes de empujar la rama;
  el avance rápido publica los mismos commits ya revisados.
- **Lo que GitHub hace distinto en un PR y hay que prever:** `github.sha` es el commit de fusión `refs/pull/N/merge`, y la demo lo
  pasa como `laboratorio_ref`; `actions/checkout` con `repository:` y ese sha tiene que poder traerlo (es alcanzable desde la
  ref del PR). Si fallara, el arreglo en `C4` sería `laboratorio_ref: ${{ github.event.pull_request.head.sha || github.sha }}`
  en la demo (y P-CI-13 cambia su igualdad); `ejemplo-ci` no se ve afectado porque fija `C1`. Es la causa de fallo n.º 1 de la
  previsión para este control.
- **Con (b)** (un PR con un cambio trivial, cerrado sin fusionar): la rama lleva un solo commit que cambia un comentario de
  `ejemplo-ci/README.md`; se leen las corridas, se cierra el PR sin fusionar y se borra la rama; el resultado va en `C3` a `main`
  como siempre. **Con (c):** no se recorre, se declara en `RESULTADO-CI2.md` y `CI.md` sigue describiendo `pull_request` sin
  control.

---

## 7. Lo que no puede romperse

Los tres controles de la etapa 23 siguen en verde, con los mismos informes byte a byte, en cada corrida de `demo-ci` de esta
etapa (`C1`, `C2`, el PR y el commit publicado). Cómo se comprueba:

1. **Antes del push 1, en la máquina:** `python3 cv/ci/ensayo_flujo.py <repositorio> $TRABAJO pruebas,negativo,positivo,real`
   con el YAML endurecido; los seis jobs en verde; y la huella de cada `INFORME.json` del ensayo igual a la de la etapa 23:
   `sha256sum $TRABAJO/negativo/trabajo/corrida/INFORME.json` (y `positivo`, `real`) frente a `informe_sha256` de
   `verificador-negativo-1`, `verificador-positivo-1` y `verificador-real-1` en `cv/ci/CORRIDA-CI-1.json`. El ensayo lo hace
   solo con `--informes-como cv/ci/CORRIDA-CI-1.json` (§9).
2. **En el runner, en cada corrida:** `traer_resultados_ci.py <run_id> $TRABAJO -o cv/ci/CORRIDA-CI2-<n>.json --igual-a
   cv/ci/CORRIDA-CI-1.json` añade a cada artefacto `verificador-*` la clave `igual_a_la_corrida_1` (su `informe_sha256` frente al
   de la 23, por nombre de control) y sale con 1 si alguno es `false`. El `INFORME.json` no lleva fechas ni rutas (S-VC-14), así
   que «igual» es byte a byte, como en la 23.
3. **Lo que no se toca** (S-CI2-16) se atestigua con `MANIFIESTO.txt` regenerado: las huellas del juez, de
   `verificar_conversor.py`, de `linea_base.py`, de `conversor_juguete.py`, de `sembrar_juguete.py` y de las tres bases de la 23
   son las de `C0`.
4. **El `pruebas` de la demo** sigue corriendo `prueba_ci.py` (ahora P-CI-1..27) y `prueba_vc.py`, los dos en verde.

Si en `C1` alguno de los tres controles no sale igual byte a byte, se para antes de `C2`: la causa se busca en el YAML
(`read -ra`, el `bash -c` de `preparar`, el `env:`), no en el juez, y el arreglo es un push más por la opción B.

---

## 8. Las pruebas en rojo: P-CI-16..27 en `cv/ci/prueba_ci.py`

Mismo estilo (`mira`, `grupo`, `PRUEBAS`, `rojo`); sin Docker ni red; PyYAML solo para los YAML. Cada una en rojo antes del
cambio que prueba, por la razón prevista, y cada guarda con su control negativo. `yaml_dir()` sigue apuntando a
`.github/workflows/`; las guardas estáticas recorren además `cv/ci/github-ci2/*.yml` (las plantillas), donde el literal
`COMMIT_C1` vale como commit. P-CI-15 cambia solo en el arnés: `entorno_de(d, id_paso, rc)` construye el `env:` del paso con
`${{ inputs.<k> }}` → el `default` declarado (los booleanos como `true`/`false`) y `${{ steps.verificar.outputs.rc }}` → `rc`, y
`paso_de_github` lo recibe; sus cuatro comprobaciones y su control no cambian.

| Prueba | Qué comprueba | Control negativo | Rojo antes de |
|---|---|---|---|
| P-CI-16 (estática) | en todo YAML de `.github/workflows/` y `cv/ci/github-ci2/`, ningún `run:` (de ningún paso de ningún job) contiene `${{`; se lee el valor cargado con PyYAML | un YAML en memoria con `run: echo ${{ inputs.x }}` → lo ve; con `run: echo $IN_X` → no | el `env:` de 2.1 |
| P-CI-17 (estática, línea cruda) | en los mismos YAML, toda línea `uses:` de paso casa con `^\s*-?\s*uses: actions/[\w-]+@([0-9a-f]{40})  # (v\d+\.\d+\.\d+)$`; el par `(sha, etiqueta)` es el de `ACCIONES-CI.json` para esa acción; la misma acción lleva el mismo sha en todos los ficheros; `ACCIONES-CI.json` tiene formato `acciones-ci/1`, las cuatro acciones, `sha` de 40 hex y `etiqueta` `vX.Y.Z`; todo `uses:` de job es `./.github/workflows/verificador-conversor.yml` o casa con `^LK-Corporation/lab-integraciones/\.github/workflows/verificador-conversor\.yml@(COMMIT_C1\|[0-9a-f]{40})$` | una línea `uses: actions/checkout@v4` → lo ve; un sha que no está en el JSON → lo ve; etiqueta distinta en el comentario → lo ve; `uses: otro/flujo.yml@main` de job → lo ve | los sha de 2.2 |
| P-CI-18 | en el flujo, `laboratorio_ref` tiene `required: true` y no tiene `default`; el cuerpo de «Entradas», corrido con el shell de GitHub y `entorno_de`, sale con 2 y escribe «40 hex» con `IN_LABORATORIO_REF=main` y con `v1.2`, y pasa de esa línea (llega a `no existe el adaptador`) con 40 hex; `ENTRADAS` de P-CI-11 sigue igual | un flujo con `default: main` → lo ve | 2.3 |
| P-CI-19 | en el flujo, para cada paso `run:`, toda variable `$IN_[A-Z_]+` o `${IN_…}` o `$RC_HERRAMIENTA` que aparece en el cuerpo está declarada en el `env:` de ese paso, y cada `IN_X` declarado vale `${{ inputs.<x en minúsculas> }}`; `RC_HERRAMIENTA` vale `${{ steps.verificar.outputs.rc }}` | quitar `IN_CORPUS` del `env:` de «Verificar» → lo ve; `IN_CORPUS: ${{ inputs.opciones }}` → lo ve | 2.1 |
| P-CI-20 | en `demo-ci.yml`, los jobs `negativo`, `positivo` y `real` llevan `laboratorio: ${{ github.repository }}`; el flujo conserva el `default` `LK-Corporation/lab-integraciones`; `ejemplo-ci.yml` y `rojo-ci.yml` (las plantillas) llevan `laboratorio: LK-Corporation/lab-integraciones` escrito | la demo con `laboratorio: LK-Corporation/lab-integraciones` → lo ve | 2.4 |
| P-CI-21 (estática) | la plantilla `cv/ci/github-ci2/ejemplo-ci.yml`: `on.push.branches == ["main"]`, `paths` con los tres patrones, `pull_request.paths` iguales, `workflow_dispatch`, `concurrency.cancel-in-progress`, `permissions == {"contents": "read"}` en el flujo y en cada job `uses:`; `ejemplo` y `ejemplo-propio` usan la forma remota con el mismo ref; `laboratorio_ref` igual a ese ref en los dos; `adaptador` y `linea_base` empiezan por `proyecto/ejemplo-ci/`; `corpus == "proyecto/ejemplo-ci/corpus"`; `esperar` ausente o `pasa`; `imagen` termina en `@sha256:` + el digest del adaptador; `nombre` `ejemplo` y `ejemplo-propio`; `ejemplo-propio` lleva `sin_corpus_lab: true`, `artefacto_completo: true` y `--json-solo` en `opciones`; `ejemplo` no lleva ninguna de las tres; `ejemplo-comprobado` tiene `needs` de los dos y descarga `ejemplo-${{ github.run_attempt }}` y `ejemplo-propio-${{ github.run_attempt }}` | `laboratorio_ref` distinto del ref del `uses:` → lo ve; `esperar: igual` → lo ve; `sin_corpus_lab` quitado → lo ve | 4.2 |
| P-CI-22 (estática) | la plantilla `rojo-ci.yml`: `on` tiene solo `workflow_dispatch` (ni `push` ni `pull_request` ni `schedule`); `rojo` usa la forma remota con el mismo ref que `ejemplo-ci.yml`, `laboratorio_ref` igual, `esperar` ausente o `pasa`, `preparar` contiene `preparar.sh` y `sembrar.py` y `DEFECTO.json`, `linea_base` la de `LINEA-BASE.json` (no la propia), `nombre: rojo`; `rojo-comprobado` tiene `needs: rojo`, `if: always()`, descarga `rojo-${{ github.run_attempt }}` y llama a `comprobar_rojo.py`; permisos de solo lectura | `on` con `push` → lo ve; `esperar: falla` → lo ve; `if` quitado → lo ve | 5.1 |
| P-CI-23 | el proyecto de ejemplo: `adaptador.json` pasa `leer_adaptador` con unos artefactos de prueba donde `conv/conversor.py` es una copia del conversor; `tipo` docker, `id` `ejemplo`, imagen `python:3.12-slim`, `imagen_digest` de 64 hex; el mismo digest aparece en `imagen` de las dos plantillas y en `hacer_base.sh`; `corpus/` tiene exactamente seis `.hl7`, cada uno empieza por `MSH\|^~\&\|`, MSH-9.1 en {ADT, ORU, VXU}, MSH-10 igual al nombre del fichero, sin `@` ni IP; las dos bases (si existen) tienen `formato`, `conversor.id == "ejemplo"`, `n_casos == len(casos)`, `LINEA-BASE.json` con `corpus.n.propio == 6` y `adt > 0`, `LINEA-BASE-propio.json` con solo `propio` y todas las claves con prefijo `propio/`; `DEFECTO.json` tiene formato `defecto-ci/1`, `fichero` `conversor.py`, `de` ≠ `a`, `hallazgo_esperado` lista no vacía de triples | una base con `id` `juguete` → lo ve; un digest distinto en una plantilla → lo ve | 3 |
| P-CI-24 | el conversor sin Docker: `python3 ejemplo-ci/conversor.py <corpus> <salida>` deja un `.json` por mensaje, cada uno un `Bundle` con un `Patient`, y `EJ-ORU-R01` lleva `"value": 5.30` literal; dos corridas iguales byte a byte; sobre una copia, `sembrar.py` con `DEFECTO.json` sale 0, la copia convierte `EJ-ADT-A01` (F) con `gender` `male` y `EJ-ADT-A03` (M) igual que antes, y las salidas de los seis solo difieren en `gender` en los de PID-8 `F`; `--deshacer` devuelve la copia byte a byte; un mensaje con MSH-9 `SIU^S12` da `.error` | `sembrar.py` sobre un fichero sin el texto → 2 y sin tocar; con el texto dos veces → 2 | 3.1, 3.5 |
| P-CI-25 | `comprobar_rojo.py` con artefactos sintéticos escritos por la prueba: uno bueno (veredicto `pasa`/`falla`, `motivos == ["hallazgo_nuevo"]`, `nuevos_distintos` el de `DEFECTO.json`, `huella_distinta`, el `.md` con su primera línea, informe, juicio y propuesta con el triple) y `--resultado-job failure` → 0 y `COMPROBACION-ROJO.json` con todo `true`; `--salidas` vacías → 0 y `"salidas_del_job": "vacias"`; `--salidas falla <n> <json>` cuadrando → 0 | `--resultado-job success` → 1; `motivos` con `caja` → 1; un triple de más en `nuevos_distintos` → 1; sin `VEREDICTO-CI.md` → 1; `esperado: falla` → 1; `--salidas pasa …` → 1 | 5.3 |
| P-CI-26 | `comprobar_ejemplo.py` con dos artefactos sintéticos buenos (el de `ejemplo` con `INFORME.md` y sin `evidencias/`; el propio sin `INFORME.md` y con `evidencias/` y `corpus/` con los seis nombres) y dos bases sintéticas → 0; y, si existen, los YAML que corren, `.github/workflows/verificador-conversor.yml` y `demo-ci.yml`, son byte a byte iguales a `cv/ci/github-ci2/` | `INFORME.md` en el propio → 1; `evidencias/` en el de `ejemplo` → 1; `n.corrida` distinto de `n_casos` → 1; `avisos` con `huella_distinta` → 1 | 4.3, 15 |
| P-CI-27 (se añade en `C2`, en rojo antes de escribir los YAML) | `.github/workflows/ejemplo-ci.yml` y `rojo-ci.yml` existen y cada uno es byte a byte la plantilla de `cv/ci/github-ci2/` con `COMMIT_C1` sustituido por un mismo sha de 40 hex, el mismo en los dos ficheros; ese sha no es `C0` (`0f85437…`) | un fichero con otro espacio cambiado → lo ve; dos sha distintos → lo ve | 4.1 |

Además, en `tests/test_repo_hygiene.py`: `SUFIJOS_TEXTO` gana `.hl7` (26-oct-2026: el corpus del proyecto de ejemplo);
`RAIZ_ADMITIDA` gana `ejemplo-ci`; `JSON_ADMITIDOS` gana `ejemplo-ci/ci/adaptador.json`, `ejemplo-ci/ci/LINEA-BASE.json`,
`ejemplo-ci/ci/LINEA-BASE-propio.json`, `ejemplo-ci/ci/DEFECTO.json`, `verificador/cv/ci/ACCIONES-CI.json`,
`verificador/cv/ci/preguntas_qci2.json`, `verificador/cv/ci/preguntas_prevision_ci2.json`,
`verificador/cv/ci/prevision-cuerpo-ci2.json`, `verificador/cv/ci/PREVISION-CI2.json` y `verificador/cv/ci/CORRIDA-CI2-1.json`
a `-5.json`. `LICENSE.md`: la fila del código añade «`ejemplo-ci/`»; la fila de los datos añade «los mensajes sintéticos
`.hl7` y los `.json` de `ejemplo-ci/`». `README.md`: una fila `ejemplo-ci/` en «Qué hay aquí», para que
`test_todo_documento_es_alcanzable_desde_el_readme` llegue a `ejemplo-ci/README.md`. Las guardas de rutas, correos y hosts se
pasan sobre todo lo nuevo antes de cada commit (`python -m pytest tests -q`).

---

## 9. El ensayo local: lo que aprende `cv/ci/ensayo_flujo.py`

Orden: `python3 cv/ci/ensayo_flujo.py <repositorio> <trabajo vacío> <job>[,<job>…] [--flujo demo-ci|ejemplo-ci|rojo-ci]
[--modo-real lote|mensaje] [--entrada k=v …] [--rojo <job>[,…]] [--evento push|pull_request]
[--informes-como <CORRIDA-CI-1.json>]`. Tras un job corre su `-comprobado` (`ejemplo-comprobado` tras `ejemplo` y
`ejemplo-propio`; `rojo-comprobado` tras `rojo`), como hoy.

1. **`--flujo`** elige el YAML que llama (`demo-ci.yml` por omisión); los jobs son los suyos.
2. **El `uses:` remoto.** `owner/repo/<ruta>@<ref>`: si `ref` es 40 hex y `git -C <repositorio> cat-file -e <ref>^{commit}`
   responde, el YAML llamado se saca con `git -C <repositorio> show <ref>:<ruta>` a `$TRABAJO/.runner/<ruta>`; si es
   `COMMIT_C1` (una plantilla) o un commit que no está, se usa `<repositorio>/<ruta>` del árbol y se imprime «forma remota:
   el commit <ref> no está en esta copia; se ensaya el YAML del árbol». `owner/repo` se imprime y no se resuelve (sin red).
3. **Los checkouts por commit.** En `actions/checkout`, si `with.ref` interpolado es 40 hex y existe, el destino se llena con
   `git -C <repositorio> archive <ref> | tar -x -C <destino>` (el árbol de ese commit, sin `.git`); si no (`ensayo`,
   `COMMIT_C1`), copia del árbol como hoy. `with.repository` se imprime y no se resuelve. Así, en `C2`, `proyecto/` es el árbol
   de trabajo y `lab/` el de `C1`.
4. **El contexto `github`** gana `repository: "LK-Corporation/lab-integraciones"`, `event_name` (`--evento`, `push` por
   omisión), `run_attempt: "1"`; `inputs` de `workflow_dispatch` vienen de `--entrada`.
5. **`if:` de job.** Antes de correr un job se evalúa su `if:` con `needs` (`always()`, `success()`, `needs.x.result ==
   'failure'`); si es falso, el job se marca `skipped` y no corre. Un job `uses:` cuyo flujo llamado falla da `result:
   failure` y **sus salidas se propagan igual** (lo que el ensayo no puede saber es si GitHub lo hace: se imprime una línea
   «salidas de un job fallido: el ensayo las pasa; GitHub puede no hacerlo»).
6. **`actions/download-artifact`.** Los `upload-artifact` registran `nombre → (workspace, rutas existentes)`; el download copia
   esas rutas a `<workspace>/<with.path>/` quitando el prefijo común (`trabajo/`), como hace la acción de verdad. Un nombre
   que no se subió es un fallo del paso.
7. **`--rojo <job>`.** Los jobs listados tienen que salir ROJO y los demás verde para que el ensayo salga con 0; `ENSAYO.json`
   lo anota (`"esperado_rojo": [...]`).
8. **`--informes-como`.** Para `negativo`, `positivo` y `real`, compara `sha256` de `$WS/trabajo/corrida/INFORME.json` (`$WS`, el workspace del job) con
   `informe_sha256` del artefacto `verificador-<job>-1` del JSON dado; una diferencia es un fallo del ensayo.
9. **El `read -ra` y el `bash -c`** no necesitan nada: son `run:` normales con su `env:` (el ensayo ya pasa el `env:` del paso).

Lo que queda fuera, en la cabecera del guion: la evaluación de GitHub de verdad; la resolución del `uses:` remoto y del
`repository:` de `checkout` (sin red); si GitHub propaga las salidas de un job llamado que falla; los permisos del token para
`download-artifact`; el commit de fusión de un PR; el Docker, el usuario y la red del runner. Para el run en rojo, el ensayo
sí recorre todo lo demás: la siembra en `preparar`, el 10 de `comparar`, el resumen, el artefacto, el `if: always()` y
`comprobar_rojo.py` sobre el artefacto emulado.

Qué se ensaya antes de cada push (§13): antes de `C1`, `--flujo demo-ci pruebas,negativo,positivo,real --informes-como
cv/ci/CORRIDA-CI-1.json` y, con las plantillas (`COMMIT_C1`, YAML del árbol), `--flujo ejemplo-ci ejemplo,ejemplo-propio` y
`--flujo rojo-ci rojo --rojo rojo`; antes de `C2`, los dos últimos otra vez con los YAML reales (el flujo se lee de `C1` con
`git show`).

---
## 10. La previsión que se sella

`cv/ci/prevision-cuerpo-ci2.json` (lo escribe el programador después del ensayo y de `hacer_base.sh`, antes del push 1) y
`cv/ci/sellar_prevision_ci2.py <cuerpo.json> <juez publicado> [<carpeta>]`, copia de `sellar_prevision_ci.py` con estos
cambios: escribe `PREVISION-CI2.json` y `SELLO-CI2.txt` (se niega a pisar `SELLO-CI2.txt`; no toca `SELLO-CI.txt`); la cabecera
del sello dice «etapa 24 (lo abierto de la integración continua)»; `conversor` es la huella del conversor del ejemplo (de
`BASE-EJEMPLO.json`) e `imagen_digest` el de Python; `APARATO` es la lista de abajo. `PREVISION-CI2.md` cuenta lo mismo en prosa,
como `PREVISION-CI.md`. Jev da su previsión con un estado neutro (`estado_prevision_ci2.md`, `preguntas_prevision_ci2.json` →
`decision-jev-prevision-ci2.md`) una vez, después del ensayo; si el programador quiere dos, como en la 23, se sellan las dos.

**Lo que se sella (`APARATO`):** `github-ci2/verificador-conversor.yml`, `github-ci2/demo-ci.yml`, `github-ci2/ejemplo-ci.yml`,
`github-ci2/rojo-ci.yml` (las dos últimas con `COMMIT_C1`), `ACCIONES-CI.json`, `prueba_ci.py`, `ensayo_flujo.py`,
`comprobar_ejemplo.py`, `comprobar_rojo.py`, `traer_resultados_ci.py`, `sellar_prevision_ci2.py`,
`../../../ejemplo-ci/conversor.py`, `../../../ejemplo-ci/preparar.sh`, `../../../ejemplo-ci/ci/adaptador.json`,
`../../../ejemplo-ci/ci/DEFECTO.json`, `../../../ejemplo-ci/ci/sembrar.py`, `../../../ejemplo-ci/ci/hacer_base.sh`,
`../../../ejemplo-ci/ci/LINEA-BASE.json`, `../../../ejemplo-ci/ci/LINEA-BASE-propio.json`, los seis
`../../../ejemplo-ci/corpus/*.hl7`, `../../../.github/workflows/higiene.yml`, `decision-jev-prevision-ci2.md`, más
`verificar_conversor.py` en `herramienta` como en la 23. Las rutas relativas salen de `CI_D`; `comprobar_sello` ya las
resuelve así.

**Claves (`CLAVES_PREVISION_CI2`, todas obligatorias):**

| Clave | Qué | Valor que propone el diseñador |
|---|---|---|
| `etapa` | texto fijo | «24, lo abierto de la integración continua: previsión sellada antes del primer push» |
| `fecha`, `juez`, `conversor`, `imagen_digest`, `herramienta` | los pone el sellador | juez `b3f00f6a…`; conversor, la huella del ejemplo; digest de Python |
| `base_de_la_prevision` | lo que se sabe antes de correr nada en Actions | las 27 pruebas en verde; las dos bases del ejemplo iguales en dos corridas; el defecto sembrado confirmado en el laboratorio con n casos; el ensayo con la demo (informes iguales a la 23), con `ejemplo-ci` y con `rojo-ci` (rojo esperado); lo no probado: GitHub de verdad, la forma remota, las salidas de un job fallido, `download-artifact`, el PR |
| `probabilidad_demo_verde_en_c1_a_la_primera` | los tres controles de la 23 verdes en el push 1 | 0,8 |
| `probabilidad_demo_informes_iguales` | cuando están verdes, `igual_a_la_corrida_1` en los tres | 0,97 |
| `probabilidad_ejemplo_verde_a_la_primera` | `ejemplo`, `ejemplo-propio` y `ejemplo-comprobado` verdes en el push 2 | 0,55 |
| `probabilidad_rojo_a_la_primera` | `rojo` en rojo solo por «Veredicto» y `rojo-comprobado` verde, en la primera corrida a mano | 0,5 |
| `probabilidad_salidas_de_job_fallido_llegan` | `needs.rojo.outputs.resultado` no vacío | 0,4 |
| `probabilidad_pull_request_verde_a_la_primera` | las dos corridas del PR verdes (si Q-CI2-D-1 es (a) o (b)) | 0,6 |
| `probabilidad_todo_en_una_sesion` | hecho cuando del ANTES, dentro del tope | 0,6 |
| `pushes_previstos`, `pushes_mas_probable` | pushes al público por la opción B hasta «hecho cuando» (contando la rama del PR y el ff como uno) | `[4, 7]`, más probable 5 (con (a)); `[3, 6]`, más probable 4, sin PR |
| `minutos_por_corrida_previstos` | `ejemplo-ci` y `rojo-ci`, de reloj | `[1, 4]` cada uno |
| `rojo_n_casos_previsto` | casos con el triple en el run en rojo | el n de `BASE-EJEMPLO.json`, exacto |
| `causas_de_fallo_previstas` | por orden | (1) `download-artifact` necesita `actions: read` o no ve el artefacto del job llamado; (2) las salidas del job llamado fallido llegan vacías (no decide, se anota); (3) `needs.ejemplo-propio` con guion en expresiones; (4) el `docker tag` de la imagen oficial de Python por digest (`python@sha256:…` → `python:3.12-slim`); (5) `read -ra` o el `bash -c` con el `preparar` compuesto con `&&`; (6) el checkout del laboratorio en el commit de fusión del PR; (7) un `.hl7` del corpus con una ruta o un correo que la higiene no admita |
| `diferencias_que_se_explicarian` | si el ejemplo no da lo de la base | ninguna prevista: el conversor es determinista y Python puro; una diferencia es un fallo del aparato |
| `regla_de_parada` | copiada del ANTES | «la forma remota no funciona, o el run en rojo no deja lo que tiene que dejar, y no se explica: se declara y se publican solo los endurecimientos» |
| `jev` | la previsión de Jev con estado neutro, al lado | las mismas probabilidades y los pushes, en `decision-jev-prevision-ci2.md` |

---

## 11. Las preguntas de diseño para Jev (Q-CI2-D)

Con estado neutro (`cv/ci/estado_qci2.md`, `cv/ci/preguntas_qci2.json`, el formato de `preguntas_qci.json`), sin la
recomendación; la recomendación va aquí, aparte, y el diseño está escrito con ella. Lo que el ANTES o el encargo ya deciden
(`laboratorio_ref` obligatoria, el fichero aparte del rojo, la forma remota desde el propio repositorio, el commit `C1`) no se
pregunta.

| Q | Pregunta | Opciones |
|---|---|---|
| Q-CI2-D-1 | Cómo se recorre el evento `pull_request`, sin forks ni repositorios nuevos | (a) un PR desde una rama del propio repositorio que lleva el commit del resultado, llevado a `main` por avance rápido y sin commit de fusión; (b) un PR con un cambio trivial, cerrado sin fusionar y con la rama borrada; (c) no se recorre en esta etapa: se declara |
| Q-CI2-D-2 | Dónde vive el proyecto de ejemplo | (a) `ejemplo-ci/` en la raíz, como una carpeta que un tercero copia tal cual; (b) `verificador/cv/ci/ejemplo/`, con la etapa, sin tocar la raíz ni la lista de carpetas admitidas |
| Q-CI2-D-3 | Qué defecto siembra el run en rojo | (a) `F` sale como `male`: un `valor_distinto` en PID-8, tipo nuevo respecto a la 23; (b) se pierde `birthDate`: el mismo tipo que la 23 (`dato_perdido`), ya probado en el juez; (c) los dos, en dos runs a mano |
| Q-CI2-D-4 | Qué decide en `rojo-comprobado` | (a) el artefacto descargado; las salidas del job se anotan y no deciden; (b) solo las salidas del job, como en `positivo-comprobado`, y si llegan vacías el control falla; (c) las dos cosas, y las dos tienen que cuadrar |
| Q-CI2-D-5 | Cómo se recorren `sin_corpus_lab`, `opciones` y `artefacto_completo` | (a) una segunda llamada, `ejemplo-propio`, con su propia base de seis casos; (b) en la única llamada `ejemplo` (`sin_corpus_lab` queda sin recorrer); (c) solo en el run en rojo |

**Recomendación del diseñador, aparte:** D-1 (a), porque es lo único que recorre el evento con contenido real y deja la historia
lineal; si el tope aprieta, (c) antes que (b). D-2 (a), porque un tercero copia una carpeta, no una ruta dentro del
verificador. D-3 (a), porque añade un tipo de defecto al que ya está medido y el mecanismo es el mismo; se confirma en el
laboratorio antes de sellar. D-4 (a), porque el artefacto existe aunque el job falle y no se sabe si las salidas llegan. D-5
(a), porque cada entrada tiene así un efecto observable desde fuera. Si Jev elige otra: D-1 cambia §6 y el plan; D-2, las rutas;
D-3, `DEFECTO.json` y P-CI-24; D-4, `comprobar_rojo.py --salidas` (pasa a decidir) y P-CI-25; D-5, `ejemplo-ci.yml` (un job
menos), `comprobar_ejemplo.py` y P-CI-21/26.

---

## 12. Los límites (L-CI2-n)

- **L-CI2-1.** La forma remota se recorre desde el propio repositorio del laboratorio: el mismo dueño, el mismo token de
  solo lectura. Un tercero en otra organización, un repositorio privado o un PR desde un fork (token restringido) quedan en la
  cola del autor (condición 1 del ANTES).
- **L-CI2-2.** No se sabe si GitHub propaga las salidas de un job `uses:` que falla; el control del rojo no depende de ello y
  la corrida lo registra (`salidas_del_job`).
- **L-CI2-3.** El resumen de la página del job no se puede leer por la API; lo que se comprueba desde fuera es el fichero que lo
  produce y la mecánica que lo copia (P-CI-15); que está en la página lo mira una persona y lo anota.
- **L-CI2-4.** El conversor del ejemplo es de juguete (Python puro, 100-200 líneas) en `python:3.12-slim` por digest; dice cómo
  se llama al flujo, no nada sobre conversores reales. El digest de la imagen envejece como los sha de las acciones.
- **L-CI2-5.** Un tipo de defecto sembrado en el rojo (un `valor_distinto` en PID-8), más el `dato_perdido` de la 23 en el
  positivo; otros tipos siguen probados solo sin Docker (P-CI-3, P-CI-6).
- **L-CI2-6.** La corrida del run en rojo queda roja en la historia de Actions, porque un job `uses:` no admite
  `continue-on-error`; GitHub no tiene forma de marcar un fallo como esperado.
- **L-CI2-7.** `pull_request` solo con una rama del propio repositorio; el evento de un fork no se recorre.
- **L-CI2-8.** Los sha de las acciones se fijan a mano y no se actualizan solos (nada de Dependabot: abriría PR, y es una
  escritura); subirlos es un commit con `ACCIONES-CI.json` al día.
- **L-CI2-9.** `laboratorio_ref` tiene que ser un commit de 40 hex: ramas y etiquetas se rechazan. Es una ruptura de
  compatibilidad con la 23, declarada.
- **L-CI2-10.** El ensayo no ve la resolución remota de GitHub, las salidas de un job fallido, los permisos de
  `download-artifact` ni el commit de fusión de un PR; la previsión los lleva como causas de fallo.
- **L-CI2-11.** `preparar` corre con `bash --noprofile --norc -euo pipefail -c`: la misma orden, el mismo directorio y las mismas
  variables que antes; lo que cambia es que ya no se interpola en el YAML. Sigue sin aislarse (L-CI-10).
- **L-CI2-12.** `ejemplo-ci.yml` y `rojo-ci.yml` fijan `C1` y se quedan ahí: cuando el flujo cambie, el ejemplo llamará al flujo
  viejo hasta que un commit suba el pin, en dos pushes. Es exactamente la situación de cualquier tercero, y `CI.md` lo dice.
- **L-CI2-13.** Los minutos: cada corrida de `ejemplo-ci` y de `rojo-ci` cuesta del orden de 1 a 4 minutos de reloj (la imagen de
  Python, la caja con 349 mensajes en un proceso, el juez); la cifra real se mide en la primera corrida.

---

## 13. El plan

Tope: una sesión. Cada push al público pasa por la opción B (guarda LIMPIO, higiene, revisión a ciegas y Jev). Lo que GitHub
responda solo se sabe tras cada push: el plan separa lo que cierra el laboratorio (0-8) de lo que exige el runner (9-14).

| Paso | Qué | Hecho cuando | Si falla |
|---|---|---|---|
| 0 | Q-CI2-D-1..5 a Jev con estado neutro (`estado_qci2.md`, `preguntas_qci2.json` → `decision-jev-qci2.md`, `decisiones-qci2.md`); `verificador/ANTES-ETAPA-CI2.md` copiado tal cual | decididas | — |
| 1 | Los sha de las acciones (§2.2) y el digest de Python (§3.3), con red, una vez; `ACCIONES-CI.json` | las cuatro acciones con `ls-remote` y API cuadrando | parar y preguntar a Jev (§2.2) |
| 2 | `prueba_ci.py` en rojo: P-CI-16..26 fallan por la razón prevista (los YAML sin `env:`, sin sha, `ejemplo-ci/` sin existir, los guiones sin existir); commit | cada una MAL por lo previsto | — |
| 3 | Código: el flujo endurecido, `demo-ci.yml` e `higiene.yml` por sha y con `laboratorio`, `ejemplo-ci/` entero (conversor, corpus, adaptador, `DEFECTO.json`, `sembrar.py`, `preparar.sh`, `hacer_base.sh`, README), `comprobar_ejemplo.py`, `comprobar_rojo.py`, las plantillas en `cv/ci/github-ci2/`, `ensayo_flujo.py` (§9), `traer_resultados_ci.py` (`--igual-a`, los artefactos `COMPROBACION-*`), `sellar_prevision_ci2.py`; `prueba_ci.py`, `prueba_vc.py` y `pytest tests` en verde (higiene al día: `.hl7`, `ejemplo-ci`, JSON, LICENSE, README); commit | todo verde; `MANIFIESTO.txt` atestigua lo que no se toca | — |
| 4 | **Las bases del ejemplo y el defecto** con `hacer_base.sh` (§3.7): dos corridas iguales, `crear`, `igual`, las dos bases, la siembra con `falla` → 0 y `pasa` → 10; `DEFECTO.json._confirmado` y `BASE-EJEMPLO.json` | las dos bases en el repositorio, P-CI-23 verde, n de casos del rojo anotado | si el triple no es el previsto, se escribe el que dio (DV); si la corrida no es determinista, parar: el ejemplo no va al runner |
| 5 | **El ensayo** (§9): demo con `--informes-como CORRIDA-CI-1.json`; `ejemplo-ci` y `rojo-ci --rojo rojo` con las plantillas | los jobs esperados verdes, `rojo` ROJO, las huellas de la 23 iguales | arreglar antes de sellar |
| 6 | `CI.md` (§14.1), `ejemplo-ci/README.md`, `verificador/README.md` (sección de la etapa 24), `README.md` (párrafo y fila), `LICENSE.md`; `MANIFIESTO.txt` regenerado | higiene verde | — |
| 7 | **Previsión sellada** (§10): cuerpo, Jev al lado, `sellar_prevision_ci2.py`, commit del sello antes del primer push | `SELLO-CI2.txt` en HEAD | no se hace push |
| 8 | **Push 1 (`C1`)** por la opción B. Se leen `demo-ci` e `higiene`; `traer_resultados_ci.py <run> … -o cv/ci/CORRIDA-CI2-1.json --igual-a cv/ci/CORRIDA-CI-1.json` | los seis jobs de la demo verdes y los tres informes iguales a la 23 | cada arreglo, un commit y un push por la opción B; si los informes no son iguales y no se explica, parar (§7) |
| 9 | P-CI-27 en rojo; `ejemplo-ci.yml` y `rojo-ci.yml` desde las plantillas con `sed "s/COMMIT_C1/$C1/g"`; P-CI-27 verde; **push 2 (`C2`)** por la opción B. Se leen `ejemplo-ci` (y `demo-ci`, que vuelve a correr); `CORRIDA-CI2-2.json` | `ejemplo`, `ejemplo-propio` y `ejemplo-comprobado` verdes, `COMPROBACION-EJEMPLO.json` todo `true` | un arreglo que toque el flujo obliga a un `C1'` nuevo y a volver a fijar (dos pushes); uno que toque solo las llamadas o los comprobadores es un push; tope de pushes, el de la previsión |
| 10 | **`rojo-ci` a mano** sobre `C2` («Run workflow»); `CORRIDA-CI2-3.json` con el `COMPROBACION-ROJO.json` y `resumen_en_la_pagina` visto a mano | `rojo` rojo solo por «Veredicto», `rojo-comprobado` verde, el artefacto con `VEREDICTO-CI.*`, `salidas_del_job` anotado | si falló por otra cosa (caja, preparar, download), arreglar y repetir a mano (no cuesta push si el arreglo no toca `main`… sí lo cuesta: todo arreglo es un commit); **regla de parada** si no se explica |
| 11 | `RESULTADO-CI2.md` (§14.3) con `CORRIDA-CI2-1..3`, los READMEs al día; con D-1 (a): rama `etapa-24-resultado` con `C3`, opción B, push de la rama y PR; se leen las dos corridas del PR → `CORRIDA-CI2-4.json` y `C4` en la rama (opción B); `git merge --ff-only` y push de `main`; rama borrada | el PR fusionado por avance rápido, `main` lineal | si el checkout en el commit de fusión falla, el arreglo de §6 en `C4` |
| 12 | Se leen las corridas de `main` en el commit publicado (`demo-ci`, `ejemplo-ci`, `higiene`) → `CORRIDA-CI2-5.json`; `RESULTADO-CI2.md` cierra la tabla; **push final (`C5`)** por la opción B | publicado, todo en verde en el commit publicado salvo el rojo a propósito | — |

**Lo que el plan no permite:** tocar el juez, `verificar_conversor.py`, `conversor_juguete.py`, `linea_base.py`,
`sembrar_juguete.py`, `hacer_bases.py`, `POSITIVO-CI.json`, las tres bases de la 23, `cv/ci/github/` ni `SELLO-CI.txt`; un push
sin `SELLO-CI2.txt` en un commit anterior; `ejemplo-ci.yml` o `rojo-ci.yml` apuntando a un commit que no sea el del flujo
endurecido; `rojo-ci.yml` con un disparador que no sea `workflow_dispatch`; `continue-on-error` en ningún sitio; un
`permissions` que no sea de solo lectura (`contents: read`, y solo si `download-artifact` lo exige, `actions: read` en el job de
comprobación, anotado como DV); issues o PR en los proyectos de los conversores; un run en rojo en `push` o en `schedule`.

**Orden de los eslabones débiles, por si el tope aprieta:** (1) la demo endurecida en `C1` (lo más barato y lo que no puede
romperse); (2) `ejemplo` por la forma remota (el `uses:` remoto, la imagen de Python, `proyecto/…`); (3) `ejemplo-propio`
y `ejemplo-comprobado` (`download-artifact`, `artefacto_completo`); (4) el rojo; (5) el PR. Si (2) no se consigue en el tope,
la regla de parada: se declara y se publican solo los endurecimientos con la demo en verde (y `ejemplo-ci/` se queda como
carpeta de ejemplo sin llamada, dicho en `CI.md`).

---

## 14. Los documentos

### 14.1 `cv/ci/CI.md`

Cambios exactos:
- En «Lo que pones en tu proyecto», punto 5: el YAML de ejemplo pasa a `uses: …@<commit de 40 hex del laboratorio>` y
  `laboratorio_ref: <el mismo commit de 40 hex>`; la viñeta «Fija el laboratorio a un commit» pasa a: «**`laboratorio_ref` es
  obligatoria y tiene que ser el mismo commit entero (40 hex) que en `uses:`.** Una rama o una etiqueta se rechazan con el
  código 2. El juez, la herramienta y el corpus son los de ese commit, y tu base se hizo con ellos.»
- Nueva sección **«Lo que cambia desde la etapa 24 (para quien ya lo usaba)»**, antes de «Lo que hace fallar el cambio»:
  `laboratorio_ref` obligatoria y de 40 hex (quien la omitía corría `main`: ahora la llamada no arranca; quien daba una rama,
  código 2); `preparar` corre con `bash --noprofile --norc -euo pipefail -c` con las mismas variables; las acciones fijadas por
  commit (`ACCIONES-CI.json`); las entradas llegan a las órdenes por variables de entorno y ninguna se interpola en un `run:`;
  el flujo y sus salidas no cambian en nada más.
- En «Lo que no hace», la viñeta «Las entradas se escriben tal cual en las órdenes del flujo» pasa a: «Las entradas llegan a
  las órdenes por variables de entorno; `preparar` es una orden tuya que se ejecuta tal cual, así que no pongas en ella texto
  que controle otro (`github.head_ref`, el título de un PR).»
- Nueva sección **«Un proyecto de ejemplo para copiar»**: `ejemplo-ci/` con su llamada en `.github/workflows/ejemplo-ci.yml`
  (forma remota, fijada a un commit, dos llamadas), qué copiar y cómo se hizo la base (`ci/hacer_base.sh`); y que el pin del
  ejemplo se queda en su commit hasta que se suba a mano, como le pasa a cualquier proyecto.
- Nueva sección **«El run en rojo, para verlo fallar»**: `rojo-ci.yml`, solo a mano; qué siembra, qué sale y cómo se repite
  en una máquina.
- «Un ejemplo completo» cita además `ejemplo-ci.yml` y `rojo-ci.yml`.

### 14.2 Los READMEs

- `README.md`: un párrafo «**Y lo abierto de la integración continua** (26-oct)» tras el de la 23, con la frase del hecho cuando
  si se cumple; una fila `ejemplo-ci/` en «Qué hay aquí» («un proyecto de conversor de ejemplo, con su llamada al flujo por la
  forma remota»); el enlace a `verificador/RESULTADO-CI2.md` en la lista de resultados.
- `verificador/README.md`: sección «Lo abierto de la integración continua (24, 26-oct-2026)» con la tabla de documentos, como la
  de la 23: `ANTES-ETAPA-CI2.md`, `cv/ci/ENCARGO-CI20.md`, `cv/ci/diseno-ci2-fable.md`, `cv/ci/decisiones-qci2.md`,
  `estado_qci2.md`, `preguntas_qci2.json`, `decision-jev-qci2.md`; el código (`prueba_ci.py`, `comprobar_ejemplo.py`,
  `comprobar_rojo.py`, `ensayo_flujo.py`, `ACCIONES-CI.json`, `github-ci2/`); el proyecto de ejemplo (`../ejemplo-ci/`); la
  previsión (`PREVISION-CI2.*`, `SELLO-CI2.txt`, `estado_prevision_ci2.md`, `preguntas_prevision_ci2.json`,
  `decision-jev-prevision-ci2.md`, `prevision-cuerpo-ci2.json`, `sellar_prevision_ci2.py`); las corridas (`CORRIDA-CI2-1..5.json`);
  el resultado (`RESULTADO-CI2.md`). Todo `.md` y `.txt` nuevo tiene que quedar enlazado desde aquí o desde el README raíz.

### 14.3 `verificador/RESULTADO-CI2.md`

Cabecera con la frase fija del ANTES en negrita (o la del resultado negativo); la pregunta fija; y estas secciones: «Los cuatro
endurecimientos» (uno por uno, con su prueba y lo que rompe); «La forma remota» (la tabla: `ejemplo`, `ejemplo-propio`,
`ejemplo-comprobado`, con lo esperado, lo que dio, la huella, el digest, los minutos; el commit fijado, `C1`); «El run en
rojo» (la corrida roja, el paso que falló, el n de casos, los triples, el resumen, el artefacto, `salidas_del_job`); «`pull_request`»
(lo que dio, o que no se recorrió); «Lo que no se rompe» (los tres controles en `C1`, `C2`, el PR y el commit publicado, con
`igual_a_la_corrida_1`); «Lo que cuesta» (minutos por corrida); «La previsión, frente a lo que salió» (la tabla, con Jev al
lado); «Antes del primer push» (el ensayo, la revisión a ciegas, el sello); «Lo que no dice» (L-CI2-1..13); «Cómo repetirlo»;
«Los documentos de la etapa». Los enlaces a las corridas llevan el `run_id`, y lo que caduca en GitHub queda en los
`CORRIDA-CI2-*.json`.
