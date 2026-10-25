> *Copia pública: se quitaron las alusiones al autor y a su máquina. El resto es el original del laboratorio.*

# Diseño de la etapa 23: el verificador en la integración continua de un conversor (diseño a ciegas, Fable, 25-oct-2026)

Leído: el ANTES de la etapa (`ANTES-ETAPA-CI.md`) y el repositorio público (`cv/verificar_conversor.py`, `cv/VC.md`, `cv/CV1.md`, `cv/adaptadores/`, `cv/conversor_juguete.py`, `cv/lfh/`, `cv/vc/CONTROL-VC.md`, `RESULTADO-ARRASTRE.md`, `cv/prueba_vc.py`, `cv/ar/sellar_prevision.py`, `.github/workflows/higiene.yml`, `tests/test_repo_hygiene.py`). Nada se corrió salvo `--solo-orden` con el juguete y `mcp_verificador._version()`. Hechos medidos que el diseño usa:

- La herramienta es `cv/verificar_conversor.py` 1.0 (huella hoy `f4e29e1d…`, la del manifiesto). Códigos 0/1/2/3/4/5. `--comparar` es simétrico: cualquier diferencia sale con 5. El veredicto por caso, según Q-VC-D-7, es `(estado, categoria, subtipo, {(hecho, clase, subtipo) de los hallazgos que cuentan})`; es la función `comparar._valor`.
- `juicio.jsonl`: una fila por caso con `conversor, corpus, caso, punto, estado, categoria, subtipo, cuentan[{hecho, clase, subtipo, que, ruta, firma, clase8, citas}], notas, convenciones, aceptables, alternativas, plantilla, msh9`. `INFORME.json` no lleva fechas, tiempos ni rutas; `CORRIDA.json` sí (`fecha`, `rutas`, `duraciones`, `imagen_digest`).
- El juez publicado tiene huella `b3f00f6ad63f26a0edacd1f21eddefbcd7b5d616a39a74bc6fd6d65c75fb1958` (servidor 1.3); el del laboratorio, `bde94016…`. Difieren por `medida/encargo_medida.md` (extracto) y por el corte C19; sus veredictos son los mismos (`MANIFIESTO.txt`, `README.md` §«En qué difiere»).
- Corpus público con el juguete: adt 263, oru 40, vxu 40 (343), huella `d333f3d6…`; con `id` `linuxforhealth` entran además los 68 mínimos (411). Huella del juguete `ae5ca436…`.
- LinuxForHealth v1.1.0: huella `ac41f71b98ee75bac637ecd4b68f58b463f0798bf66cfa941f4194cb2a50acf2` (partes `lib` + `lfh/Arnes.java`; la fórmula no ve nombres), `huella_con_nombres` `7ad4d546…`, imagen `maven:3.9-eclipse-temurin-11@sha256:7bb84a451705605a47d24eb844d4d9ab03e33e131a507db76aafe25db3907f64`. El jar y 77 dependencias salen de `mvn dependency:copy-dependencies` con `cv/lfh/pom.xml`; el arnés `cv/lfh/Arnes.java` se compila contra `lib`. En lote tarda 17-21 s; mensaje a mensaje, 29 min (`RESULTADO-ARRASTRE.md`).
- `proceso_local` solo corre el juguete por su ruta real (`S-VC-4`): un defecto sembrado tiene que escribirse en `cv/conversor_juguete.py` de la copia que corre, no en otra copia.
- Si el juguete deja de escribir `birthDate` con PID-7 válido, el juez da `cuenta("dato_perdido", "PID-7", …)` con `clase="fidelidad"` (`conversion.py:_fecha`): el triple es `("PID-7", "fidelidad", "dato_perdido")`.
- La higiene (`tests/test_repo_hygiene.py`) admite `.yml` en `.github/`, exige que cada `.json` nuevo esté en `JSON_ADMITIDOS`, que cada `.md`/`.txt` sea alcanzable desde `README.md`, que no haya rutas `/home/…` ni `~/x`, ni `docker inspect X`, ni `ssh x`, y ficheros ≤ 512 KB.

---

## 1. Las decisiones (S-CI-n)

| Id | Decisión | Por qué, en una línea |
|---|---|---|
| S-CI-1 | La línea base es un JSON propio (`linea-base-ci/1`), derivado de `juicio.jsonl` + `INFORME.json`, con el veredicto de cada caso en la forma de Q-VC-D-7 y nada más (sin `que`, sin citas, sin fechas) | es lo que el control de la etapa 18 llamó «el mismo veredicto»; cabe bajo los 512 KB de la higiene y se puede leer en un diff |
| S-CI-2 | La comparación vive en un guion aparte, `cv/ci/linea_base.py`; `verificar_conversor.py` no cambia ni una línea | `--comparar` es simétrico (cualquier diferencia → 5) y la CI necesita una regla asimétrica; la huella de la herramienta está sellada en `SELLO-AR.txt` y `CONTROL-VC.md` y no conviene moverla; el juez no se toca (condición 4) |
| S-CI-3 | «Hallazgo nuevo» = un triple `(hecho, clase, subtipo)` que cuenta en la corrida y no estaba en la línea base de ese caso; un caso sin línea base cuenta cada triple suyo como nuevo | es la pregunta fija del ANTES, leída al pie de la letra; un caso nuevo con hallazgos no se acepta en silencio |
| S-CI-4 | Hacen fallar, además: perder la salida (`bundle` → otro estado), pasar a `indeterminado`, un caso de la base que no aparece, y cualquier código ≠ 0 de la herramienta | son regresiones que no añaden triple (el juez no juzga lo que no ve) y la caja rota no es un «pasa» |
| S-CI-5 | Lo que desaparece es un `arreglo`: se lista, no falla; el flujo deja `LINEA-BASE-propuesta.json` para que el proyecto la adopte con un commit | «falle solo si aparece un hallazgo que no estaba»; actualizar la base es un acto del proyecto, no del runner (sin escrituras, condición 3) |
| S-CI-6 | Tres expectativas: `pasa` (regla asimétrica), `igual` (cualquier diferencia falla) y `falla` (debe fallar y solo por los triples esperados) | el negativo y un proyecto usan `pasa`; el real usa `igual` («los mismos veredictos»); el positivo usa `falla` y así el job sale en verde comprobando que el flujo falla |
| S-CI-7 | El flujo reutilizable es `.github/workflows/verificador-conversor.yml` (`on: workflow_call`), sin secretos, `permissions: contents: read`, sin `pull-requests`/`issues` | condiciones 1 y 3 |
| S-CI-8 | El conversor se prepara con una orden del proyecto (`preparar`), que corre con red antes de la caja; después, ninguna red salvo la del `docker pull` por digest | «la red solo para traer el conversor, como al construirlo» |
| S-CI-9 | La imagen se fija por digest: el flujo hace `docker pull <repo>@sha256:<d>`, la etiqueta con el nombre que pone el adaptador, y escribe `caja.imagen_digest` en una copia del adaptador; la herramienta sale con 3 si no coincide (Q-VC-D-4) | se reutiliza la garantía que la herramienta ya tiene; el runner no puede correr otra imagen sin que se note |
| S-CI-10 | La caja en el runner es la de la herramienta (`CAJA`, no configurable); el flujo no añade ni quita banderas, y el informe las registra | condición 2; L-VC-9 se declara (Docker del runner, no el del laboratorio) |
| S-CI-11 | La huella del conversor se comprueba antes de correr nada con `--solo-orden` (`huella_esperada`, opcional) | es el paso 1 de `CONTROL-VC.md`: identidades antes que corridas; el real la exige |
| S-CI-12 | El positivo siembra el defecto con `cv/ci/sembrar_juguete.py`: un reemplazo exacto y único en `cv/conversor_juguete.py` (deja de escribir `birthDate`); el triple esperado está en `cv/ci/POSITIVO-CI.json` | `proceso_local` solo corre el juguete real (S-VC-4); un reemplazo con cuenta = 1 es verificable sin Docker (P-CI) |
| S-CI-13 | El control real corre `cv/adaptadores/linuxforhealth.json` (lote) sin muestras, con los 68 mínimos, `--sin-sensibilidad`, y su línea base sale de la copia pública en el laboratorio con el juez `b3f00f6a…` | lote cuesta segundos y mensaje a mensaje media hora; la base debe compararse con el mismo juez que corre el runner |
| S-CI-14 | La demostración son cuatro jobs en `.github/workflows/demo-ci.yml`: `pruebas` (P-CI, sin Docker), `negativo`, `positivo` y `real`; los tres últimos llaman al flujo reutilizable del mismo commit | «se prueba en el sitio donde va a vivir»; el positivo no puede usar `continue-on-error` en un job `uses:` |
| S-CI-15 | La demo corre en `push` y `pull_request` solo cuando cambian `verificador/**`, `.github/workflows/**` o `tests/**`, más `workflow_dispatch`; `concurrency` cancela la anterior; `timeout-minutes` en cada job; la caché de Maven por huella del `pom.xml` | minutos de runner: ~10 por corrida completa |
| S-CI-16 | Las salidas del flujo son `outputs` del job (`resultado`, `nuevos`, `arreglos`, `huella`, `imagen_digest`, `juez`), el informe como artefacto y un resumen en `$GITHUB_STEP_SUMMARY` | el ANTES pide informe y resumen; los outputs permiten que la demo compruebe el positivo desde fuera del flujo |
| S-CI-17 | Las pruebas P-CI-1..14 van en `cv/ci/prueba_ci.py`, en el estilo de `prueba_vc.py`; validan los YAML con PyYAML (única dependencia, de pruebas) y cada guarda lleva control negativo | sin Docker ni red; la higiene de `tests/` no cambia salvo `JSON_ADMITIDOS` |
| S-CI-18 | Python 3.12 en el runner y `TZ=UTC` en el proceso de la herramienta; la caja no hereda la zona del anfitrión | el laboratorio usa 3.12; dentro del contenedor la JVM ya corre en UTC en los dos sitios |
| S-CI-19 | El flujo no lee `muestras` (L-VC-7) ni construye Microsoft (fuera de la etapa); la guía lo describe sin control | ANTES: fuera de la etapa |
| S-CI-20 | Toda ruta en YAML y en los documentos es relativa al workspace o empieza por `/tmp`, `/opt` o `$HOME` | la guarda de rutas de máquina de la higiene |

---

## 2. La línea base

### 2.1 Formato: `linea-base-ci/1`

Un único JSON con claves ordenadas (`sort_keys=True`, `indent=1`, `ensure_ascii=False`, salto final), escrito por `linea_base.py crear`:

```json
{
 "formato": "linea-base-ci/1",
 "creada_de": {"herramienta": {"version": "1.0", "huella": "<sha256 de verificar_conversor.py>"},
               "juez": {"huella": "<huella>", "servidor": "1.3"},
               "opciones": {"lab": true, "minimos": true, "propios": false, "sensibilidad": false}},
 "conversor": {"id": "linuxforhealth", "nombre": "…", "version": "…", "huella": "<64 hex>", "huella_con_nombres": "<64 hex>",
               "imagen": "maven:3.9-eclipse-temurin-11", "imagen_digest": "sha256:…", "modo": "lote", "contenedor": null},
 "corpus": {"huella": "<64 hex>", "n": {"adt": 263, "oru": 40, "vxu": 40, "muestras": 0, "minimos": 68, "propio": 0},
            "por_corpus": {"adt": "<64 hex>", "…": "…"}},
 "casos": {
  "adt/A1-A01-00": {"estado": "bundle", "categoria": "fallo_silencioso", "subtipo": "dato_perdido",
                    "hallazgos": [["PV1-3", "fidelidad", "dato_perdido"], ["PV1-7", "fidelidad", "codigo_mal_mapeado"]]},
  "minimos/L01-…-caso": {"estado": "error", "categoria": "rechazo_incorrecto", "subtipo": "incorrecto",
                         "hallazgos": [["MSH-9", "rechazo", "incorrecto"]]}
 },
 "n_casos": 411
}
```

- La clave de caso es `corpus/caso` (el `conversor` se fija en `conversor.id`; `comparar` exige que coincida con el de la corrida).
- `hallazgos` es la lista ordenada y sin repetidos de `(hecho, clase, subtipo)` de `cuentan`, **tal cual los da el juez** (con `(2)` de ocurrencia si lo lleva): exactamente `comparar._valor` de la herramienta. No entran `notas`, `convenciones`, `aceptables`, `alternativas` ni el texto `que`.
- `creada_de`, `conversor` y `corpus` salen de `INFORME.json` (sin fechas ni rutas) y de `ADAPTADOR.json` (`invocacion.modo`, `invocacion.contenedor`). `imagen_digest` sale de `INFORME.json.conversor.imagen_digest` (null con `proceso_local`).
- Tamaño previsto: 411 casos × ~150 bytes ≈ 60-90 KB (bajo 512 KB).

### 2.2 Cómo se crea

```bash
cd verificador
python3 cv/verificar_conversor.py <adaptador.json> <salida> --artefactos <artefactos> --sin-sensibilidad [--corpus …]
python3 cv/ci/linea_base.py crear <salida> -o LINEA-BASE.json          # lee <salida>/{juicio.jsonl,INFORME.json,ADAPTADOR.json}
```

`crear` se niega (código 2) si `INFORME.json.no_juzgado.sin_evidencia` no está vacío o si la carpeta no es de una corrida de la herramienta (falta `CORRIDA.json`): una base no se crea de una corrida con la caja rota. Con `--permitir-sin-evidencia` se crea igual y lo anota en `creada_de.sin_evidencia`.

### 2.3 Regla de comparación (`linea_base.py comparar <salida> <LINEA-BASE.json>`)

Para cada clave `corpus/caso` de la unión de los dos lados, con `B` = base y `C` = corrida:

| Situación | Código del caso | Hace fallar (`pasa`) | Fallo en `igual` |
|---|---|---|---|
| triple en `C.hallazgos` y no en `B.hallazgos` | `hallazgo_nuevo` | **sí** | sí |
| caso en `C` y no en `B`, con `hallazgos` no vacíos | `hallazgo_nuevo` (todos sus triples) | **sí** | sí |
| caso en `C` y no en `B`, sin hallazgos | `caso_nuevo` | no | sí |
| caso en `B` y no en `C` | `caso_ausente` | **sí** | sí |
| `B.estado == "bundle"` y `C.estado != "bundle"` | `salida_perdida` | **sí** | sí |
| `C.categoria == "indeterminado"` y `B.categoria != "indeterminado"` | `indeterminado_nuevo` | **sí** | sí |
| triple en `B` y no en `C` | `arreglo` | no | sí |
| `B.estado != "bundle"` y `C.estado == "bundle"`, o `B.categoria != "correcto"` y `C.categoria == "correcto"`, sin triple nuevo | `arreglo` | no | sí |
| mismos triples y categoría, `subtipo` distinto | `nota` | no | sí |
| mismos triples, `estado` o `categoria` distintos sin encajar arriba | `cambio_de_categoria` | no | sí |

Y fuera de los casos:

| Situación | Código | `pasa` | `igual` |
|---|---|---|---|
| la herramienta salió con 4 (`--rc-herramienta 4`) o hay `sin_evidencia` en `INFORME.json` | `caja` | **sí** | sí |
| la herramienta salió con 1, 2 o 3 | el flujo para antes de comparar | **sí** | sí |
| `conversor.id` distinto | `conversor_distinto` (código 2 del guion) | **sí** | sí |
| `juez.huella` distinta | `juez_distinto` (aviso) | no | sí |
| `corpus.huella` distinta | `corpus_distinto` (aviso) | no | sí |
| `conversor.huella` distinta | `huella_distinta` (aviso; es lo normal en un proyecto) | no | no (se declara en el resumen) |
| `imagen_digest` distinto | `imagen_distinta` (aviso) | no | sí |

Un cambio de categoría sin hallazgo nuevo no falla en `pasa` porque toda categoría «peor» que cuenta añade un triple (`fallo_silencioso` y `rechazo_incorrecto` lo exigen por construcción: `conversion.py:1469`), salvo `indeterminado` y la pérdida de salida, que van aparte.

**Expectativa `falla`** (`--esperar falla --hallazgo-esperado <JSON>`): el veredicto se calcula como en `pasa`; el guion sale con 0 **solo si** hay al menos un `hallazgo_nuevo`, el conjunto de triples nuevos distintos es exactamente el esperado, y no hay `caso_ausente`, `salida_perdida`, `indeterminado_nuevo` ni `caja`. Cualquier otra cosa (no falló; falló por otro triple; falló por el esperado y otro) sale con 10. Así el positivo comprueba «falla, y por ese hallazgo y no por otro».

**Códigos de `linea_base.py`:** 0 el veredicto es el esperado; 2 entrada inválida (formato, `conversor_distinto`, carpeta sin corrida); 10 el veredicto no es el esperado (regresión en `pasa`, diferencia en `igual`, o en `falla` lo de arriba); 1 error interno.

**Lo que escribe** (en `-o <carpeta>`, por omisión la carpeta de la corrida):
- `VEREDICTO-CI.json`: `{"formato": "veredicto-ci/1", "esperado": "pasa", "resultado": "pasa|falla", "pasa": true, "motivos": ["hallazgo_nuevo", …], "nuevos": [{"caso": "adt/…", "hecho": "PID-7", "clase": "fidelidad", "subtipo": "dato_perdido"}], "nuevos_distintos": [["PID-7", "fidelidad", "dato_perdido"]], "arreglos": [...], "casos_nuevos": [...], "casos_ausentes": [...], "salida_perdida": [...], "indeterminado_nuevo": [...], "notas": [...], "avisos": {"juez_distinto": {"base": "…", "corrida": "…"}, …}, "identidades": {"juez", "huella", "huella_con_nombres", "imagen_digest", "corpus", "herramienta"}, "n": {"base": 411, "corrida": 411, "comparados": 411}}` (sin fechas ni rutas; determinista byte a byte).
- `VEREDICTO-CI.md`: la tabla del resumen (§3.5).
- `LINEA-BASE-propuesta.json`: `crear` sobre la misma corrida, para que el proyecto la adopte.
- Con `--github-output <fichero>`: añade `resultado=`, `nuevos=<n>`, `nuevos_distintos=<JSON en una línea>`, `arreglos=<n>`, `huella=`, `imagen_digest=`, `juez=`.

### 2.4 Cómo se actualiza cuando el proyecto acepta un cambio

1. El flujo deja `LINEA-BASE-propuesta.json` en el artefacto `verificador-<id>` de la corrida (pase o falle).
2. Quien acepta el cambio la descarga, la copia a la ruta de `linea_base` de su proyecto y la sube **en el mismo PR** que el cambio del conversor. Sin acción del runner y sin escrituras (condición 3).
3. `comparar` admite `--actualizar`: escribe la propuesta sobre la ruta dada y sale con 0 aunque haya regresión; es una orden local, no se usa en el flujo. La guía (§7) lo dice.

Con `igual` y un `arreglo`, el proyecto hace lo mismo: la base refleja el estado que acepta.

---

## 3. El flujo reutilizable: `.github/workflows/verificador-conversor.yml`

### 3.1 Entradas

| Entrada | Tipo | Omisión | Qué |
|---|---|---|---|
| `adaptador` | string | obligatoria | ruta del adaptador JSON, relativa al workspace: `proyecto/ci/adaptador.json` (del proyecto) o `lab/verificador/cv/adaptadores/linuxforhealth.json` (del laboratorio) |
| `artefactos` | string | `artefactos` | carpeta (relativa al workspace) que `preparar` deja lista; es `--artefactos` |
| `preparar` | string | `''` | orden `bash` que construye o trae el conversor en `artefactos`; corre con red, en el workspace, con `LAB`, `PROYECTO`, `ARTEFACTOS` e `IMAGEN` en el entorno. Vacía: no se prepara nada (el juguete) |
| `linea_base` | string | obligatoria | ruta de `LINEA-BASE.json` (relativa al workspace) |
| `imagen` | string | `''` | la imagen con digest, `repo[:etiqueta]@sha256:<64 hex>`; obligatoria si el adaptador es `docker`; vacía con `proceso_local` |
| `corpus` | string | `''` | carpetas con `*.hl7` propios, separadas por espacios (cada una va en `--corpus`) |
| `sin_corpus_lab` | boolean | `false` | `--sin-corpus-lab` |
| `opciones` | string | `--sin-sensibilidad` | opciones más de la herramienta (`--limite-casos N`, `--sin-minimos`…); nunca `--comparar` ni `--muestras` |
| `esperar` | string | `pasa` | `pasa`, `igual` o `falla` |
| `hallazgo_esperado` | string | `[]` | JSON: lista de triples `[hecho, clase, subtipo]`; solo con `esperar: falla` |
| `huella_esperada` | string | `''` | si se da, el flujo para (antes de la caja) cuando la huella del conversor no coincide |
| `laboratorio` | string | `LK-Corporation/lab-integraciones` | el repositorio del verificador |
| `laboratorio_ref` | string | `''` | commit o etiqueta del laboratorio; vacía: `github.job_workflow_sha`, el commit del propio flujo |
| `sembrar` | string | `''` | solo para el control positivo de la demostración: `juguete` siembra el defecto de `POSITIVO-CI.json` en la copia del juguete que va a correr |
| `artefacto_completo` | boolean | `false` | si es `true`, el artefacto lleva también `evidencias/` y `corpus/` |

Salidas (`outputs`): `resultado` (`pasa`/`falla`), `nuevos` (n), `nuevos_distintos` (JSON), `arreglos` (n), `huella`, `imagen_digest`, `juez`.

### 3.2 El YAML completo

```yaml
# Flujo reutilizable (etapa 23): pasa un conversor HL7 v2 -> FHIR R4 por el verificador del laboratorio y falla solo si hay un
# hallazgo que no esta en la linea base del proyecto. Sin secretos, solo lectura, sin escribir en ningun repositorio.
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
      laboratorio_ref:    {type: string, required: false, default: ''}
      sembrar:            {type: string, required: false, default: ''}
      artefacto_completo: {type: boolean, required: false, default: false}
    outputs:
      resultado:        {value: ${{ jobs.verificar.outputs.resultado }}}
      nuevos:           {value: ${{ jobs.verificar.outputs.nuevos }}}
      nuevos_distintos: {value: ${{ jobs.verificar.outputs.nuevos_distintos }}}
      arreglos:         {value: ${{ jobs.verificar.outputs.arreglos }}}
      huella:           {value: ${{ jobs.verificar.outputs.huella }}}
      imagen_digest:    {value: ${{ jobs.verificar.outputs.imagen_digest }}}
      juez:             {value: ${{ jobs.verificar.outputs.juez }}}

permissions:
  contents: read

env:
  TZ: UTC
  PYTHONDONTWRITEBYTECODE: "1"
  PYTHONHASHSEED: "0"

jobs:
  verificar:
    runs-on: ubuntu-latest
    timeout-minutes: 30
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
        uses: actions/checkout@v4
        with:
          path: proyecto
          persist-credentials: false

      - name: El laboratorio, en el commit del flujo
        uses: actions/checkout@v4
        with:
          repository: ${{ inputs.laboratorio }}
          ref: ${{ inputs.laboratorio_ref != '' && inputs.laboratorio_ref || github.job_workflow_sha }}
          path: lab
          persist-credentials: false

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Entradas
        id: entradas
        shell: bash
        run: |
          set -euo pipefail
          test -f "${{ inputs.adaptador }}" || { echo "no existe el adaptador ${{ inputs.adaptador }}"; exit 2; }
          test -f "${{ inputs.linea_base }}" || { echo "no existe la linea base ${{ inputs.linea_base }}"; exit 2; }
          case "${{ inputs.esperar }}" in pasa|igual|falla) ;; *) echo "esperar: pasa, igual o falla"; exit 2;; esac
          tipo=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["caja"]["tipo"])' "${{ inputs.adaptador }}")
          echo "tipo=$tipo" >> "$GITHUB_OUTPUT"
          if [ "$tipo" = docker ] && ! [[ "${{ inputs.imagen }}" =~ ^[a-z0-9][a-z0-9._/:-]*@sha256:[0-9a-f]{64}$ ]]; then
            echo "con caja docker hace falta la entrada imagen con digest: repo[:etiqueta]@sha256:<64 hex>"; exit 2
          fi
          mkdir -p "${{ inputs.artefactos }}" trabajo

      - name: Preparar el conversor (con red)
        if: inputs.preparar != ''
        shell: bash
        env:
          LAB: ${{ github.workspace }}/lab
          PROYECTO: ${{ github.workspace }}/proyecto
          ARTEFACTOS: ${{ github.workspace }}/${{ inputs.artefactos }}
          IMAGEN: ${{ inputs.imagen }}
        run: |
          set -euo pipefail
          ${{ inputs.preparar }}

      - name: La imagen, por su digest
        if: steps.entradas.outputs.tipo == 'docker'
        shell: bash
        run: |
          set -euo pipefail
          docker version --format '{{.Server.Version}}'
          docker pull "${{ inputs.imagen }}"
          python3 lab/verificador/cv/ci/linea_base.py fijar-imagen "${{ inputs.adaptador }}" "${{ inputs.imagen }}" \
            -o trabajo/adaptador.json --etiquetar | bash -euo pipefail
          docker image inspect --format '{{index .RepoDigests 0}}' -- "$(python3 -c 'import json; print(json.load(open("trabajo/adaptador.json"))["caja"]["imagen"])')"

      - name: El adaptador que corre (proceso local)
        if: steps.entradas.outputs.tipo != 'docker'
        shell: bash
        run: |
          set -euo pipefail
          python3 lab/verificador/cv/ci/linea_base.py fijar-imagen "${{ inputs.adaptador }}" "" -o trabajo/adaptador.json

      - name: Sembrar (solo el control positivo de la demostracion)
        if: inputs.sembrar == 'juguete'
        shell: bash
        run: python3 lab/verificador/cv/ci/sembrar_juguete.py lab/verificador/cv/conversor_juguete.py

      - name: Identidades, antes de la caja
        id: identidades
        shell: bash
        run: |
          set -euo pipefail
          cd lab/verificador
          python3 cv/verificar_conversor.py "$GITHUB_WORKSPACE/trabajo/adaptador.json" "$GITHUB_WORKSPACE/trabajo/orden" \
            --artefactos "$GITHUB_WORKSPACE/${{ inputs.artefactos }}" --solo-orden | tee "$GITHUB_WORKSPACE/trabajo/solo-orden.txt"
          huella=$(sed -n 's/^\[3\/9\] huella del conversor: \([0-9a-f]\{64\}\)$/\1/p' "$GITHUB_WORKSPACE/trabajo/solo-orden.txt")
          test -n "$huella"
          echo "huella=$huella" >> "$GITHUB_OUTPUT"
          if [ -n "${{ inputs.huella_esperada }}" ] && [ "$huella" != "${{ inputs.huella_esperada }}" ]; then
            echo "la huella del conversor es $huella y se esperaba ${{ inputs.huella_esperada }}"; exit 11
          fi

      - name: Verificar (la caja: sin red, solo lectura, sin privilegios)
        id: verificar
        shell: bash
        run: |
          set -uo pipefail
          cd lab/verificador
          args=()
          for c in ${{ inputs.corpus }}; do args+=(--corpus "$GITHUB_WORKSPACE/$c"); done
          if [ "${{ inputs.sin_corpus_lab }}" = "true" ]; then args+=(--sin-corpus-lab); fi
          python3 cv/verificar_conversor.py "$GITHUB_WORKSPACE/trabajo/adaptador.json" "$GITHUB_WORKSPACE/trabajo/corrida" \
            --artefactos "$GITHUB_WORKSPACE/${{ inputs.artefactos }}" "${args[@]}" ${{ inputs.opciones }}
          rc=$?
          echo "rc=$rc" >> "$GITHUB_OUTPUT"
          echo "verificar_conversor salio con $rc"
          case $rc in 0|4) exit 0;; *) exit $rc;; esac

      - name: Veredicto frente a la linea base
        id: veredicto
        shell: bash
        run: |
          set -uo pipefail
          python3 lab/verificador/cv/ci/linea_base.py comparar trabajo/corrida "${{ inputs.linea_base }}" \
            --esperar "${{ inputs.esperar }}" --hallazgo-esperado '${{ inputs.hallazgo_esperado }}' \
            --rc-herramienta "${{ steps.verificar.outputs.rc }}" --github-output "$GITHUB_OUTPUT" -o trabajo/corrida
          rc=$?
          cat trabajo/corrida/VEREDICTO-CI.md >> "$GITHUB_STEP_SUMMARY"
          exit $rc

      - name: El informe, como artefacto
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: verificador-${{ github.job }}-${{ github.run_attempt }}
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

Notas para el programador:
- `${{ inputs.preparar }}` se interpola dentro de un `run:` a propósito: es la orden del proyecto, como un `run` suyo. El resto de entradas se usan solo como argumentos entre comillas.
- `github.job` dentro de un flujo reutilizable es el id del job del que llama; con dos llamadas en la misma demo, los nombres de artefacto no chocan (`verificador-negativo-1`, `verificador-positivo-1`, `verificador-real-1`). Si GitHub lo resolviera como `verificar`, usar `${{ github.job }}-${{ github.run_id }}-${{ strategy.job-index }}`: lo decide la primera corrida y se anota.
- `linea_base.py fijar-imagen <adaptador> <imagen@digest> -o <copia> [--etiquetar]`: valida que el repositorio de `imagen` (antes de `@`, sin etiqueta) sea el mismo que el de `caja.imagen` del adaptador (si no, código 2); escribe la copia con `caja.imagen_digest = sha256:…`; con `--etiquetar` imprime por stdout la orden `docker tag <repo>@sha256:<d> <caja.imagen>` si `caja.imagen` no lleva ya `@sha256:` (si la lleva, imprime `true`). Con `imagen` vacía y `proceso_local`, copia el adaptador sin cambios. **Las rutas relativas del adaptador siguen resolviéndose con `--artefactos`**, así que la copia puede vivir en `trabajo/`.
- `--etiquetar` hace falta porque un `docker pull repo@sha256:…` no crea la etiqueta `repo:etiqueta` que el adaptador nombra, y la herramienta hace `docker image inspect` por ese nombre (L-VC-4). Tras el `tag`, `RepoDigests[0]` es `repo@sha256:<d>` y `comprobar_caja` lo compara con `imagen_digest` (Q-VC-D-4): si el runner tuviera otra cosa bajo esa etiqueta, la etiqueta se mueve al digest pedido; si el digest no se puede traer, el `pull` falla y el job con él.
- `--solo-orden` no pregunta a Docker (DV-VC-8): la huella y la validación del adaptador salen antes de que exista ningún contenedor. El guion detecta la huella por la línea `[3/9] huella del conversor: <hex>`.
- El código 4 de la herramienta no para el paso de verificar: hay informe y lo no juzgado; es `comparar --rc-herramienta 4` quien lo convierte en `caja` y en fallo.
- El paso de veredicto corre siempre que la herramienta haya salido con 0 o 4; con 1, 2 o 3 el job ya ha fallado y el resumen no se escribe (el registro del paso lo dice).

### 3.3 Permisos y lo que deja

- `permissions: contents: read` en el flujo; el que llama debe tener al menos eso (y no más hace falta). `persist-credentials: false` en los dos checkouts: ningún paso posterior tiene el token.
- Deja el artefacto `verificador-<job>-<intento>` (14 días) y el resumen de §3.5 en la página del job. No comenta, no etiqueta, no escribe.

### 3.4 Código de salida y la caja en el runner

- El job sale con el código de `linea_base.py comparar`: 0 si el veredicto es el esperado; 10 si no; 2 con entrada inválida. Antes de eso: 2 si falta un fichero o `esperar` no vale; 11 si la huella no es la esperada; 1/2/3 de la herramienta; el `docker pull` falla con el suyo.
- La caja es exactamente la de `verificar_conversor.CAJA` (`--network none --read-only --tmpfs /tmp --cap-drop ALL --security-opt no-new-privileges --user 65534:65534 --pids-limit N`, `HOME=/tmp`, montajes `:ro`, `--` antes de la imagen). El flujo no construye ninguna orden de Docker para el conversor: solo `pull`, `tag` e `inspect`. `INFORME.json.caja.restricciones` queda en el artefacto como testigo.
- Docker en `ubuntu-latest` es el del runner (Docker CE con cgroup v2): todas las banderas de `CAJA` existen en él. Es L-VC-9 en el runner: se declara en L-CI-2.

### 3.5 El resumen en la página del job (`VEREDICTO-CI.md`)

```
## Verificador: <id> · <esperado> · **PASA|FALLA**
| | |
|---|---|
| Hallazgos nuevos | 0 (0 triples distintos) |
| Arreglos | 0 |
| Casos nuevos / ausentes | 0 / 0 |
| Salida perdida / indeterminado nuevo | 0 / 0 |
| Caja | bien (rc 0) |
| Casos comparados | 411 de 411 (base 411) |
| Conversor | <nombre> <version>, huella `<16>` (base `<16>`: igual/distinta) |
| Imagen | <imagen> `<digest 19>` (base: igual) |
| Juez | `<16>` (base: igual) · herramienta 1.0 |
| Corpus | adt 263, oru 40, vxu 40, minimos 68; huella `<16>` (base: igual) |
### Hallazgos nuevos (hasta 50)
| caso | hecho | clase | subtipo |
### Arreglos (hasta 50)
...
### Avisos
- juez_distinto: ...
```

Sin fechas, sin rutas, sin texto de hallazgos (`que`): solo triples y casos, para que el resumen no lleve valores del mensaje.

---

## 4. La demostración en el repositorio del laboratorio: `.github/workflows/demo-ci.yml`

### 4.1 Los ficheros nuevos que usa

| Fichero | Qué |
|---|---|
| `verificador/cv/ci/LINEA-BASE-juguete.json` | línea base del juguete sobre el corpus público (343 casos), hecha en el laboratorio desde la copia pública con `juguete.json` y `--sin-sensibilidad` |
| `verificador/cv/ci/LINEA-BASE-linuxforhealth.json` | línea base del control real (§6): 411 casos |
| `verificador/cv/ci/POSITIVO-CI.json` | la siembra y el triple esperado (§4.3) |
| `verificador/cv/ci/sembrar_juguete.py` | aplica la siembra de `POSITIVO-CI.json`; sale con 2 si el reemplazo no aparece exactamente una vez |
| `verificador/cv/ci/preparar_lfh.sh` | trae LinuxForHealth v1.1.0 en el runner como en CV1 (§4.4) |

### 4.2 El YAML completo

```yaml
# Demostracion de la etapa 23: los tres controles del ANTES, en el sitio donde el flujo va a vivir.
name: demo-ci

on:
  push:
    branches: [main]
    paths: ['verificador/**', '.github/workflows/**', 'tests/**']
  pull_request:
    paths: ['verificador/**', '.github/workflows/**', 'tests/**']
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: demo-ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  pruebas:
    # P-CI-1..14 sin Docker ni red; valida los dos YAML y los guiones antes de gastar un minuto de caja
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python3 -m pip install --quiet pyyaml
      - run: python3 cv/ci/prueba_ci.py
        working-directory: verificador
      - run: python3 cv/prueba_vc.py
        working-directory: verificador

  negativo:
    # el juguete contra su propia linea base: pasa
    needs: pruebas
    uses: ./.github/workflows/verificador-conversor.yml
    permissions:
      contents: read
    with:
      adaptador: lab/verificador/cv/adaptadores/juguete.json
      artefactos: lab/verificador/cv
      linea_base: lab/verificador/cv/ci/LINEA-BASE-juguete.json
      laboratorio_ref: ${{ github.sha }}
      esperar: igual

  positivo:
    # el juguete con el defecto sembrado: el flujo falla, y solo por el triple esperado; entonces el job sale en verde
    needs: pruebas
    uses: ./.github/workflows/verificador-conversor.yml
    permissions:
      contents: read
    with:
      adaptador: lab/verificador/cv/adaptadores/juguete.json
      artefactos: lab/verificador/cv
      linea_base: lab/verificador/cv/ci/LINEA-BASE-juguete.json
      laboratorio_ref: ${{ github.sha }}
      sembrar: juguete
      esperar: falla
      hallazgo_esperado: '[["PID-7", "fidelidad", "dato_perdido"]]'

  positivo-comprobado:
    # segunda comprobacion, fuera del flujo: lo que el flujo dice que hizo fallar es exactamente el triple sembrado
    needs: positivo
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - shell: bash
        env:
          RESULTADO: ${{ needs.positivo.outputs.resultado }}
          NUEVOS: ${{ needs.positivo.outputs.nuevos }}
          DISTINTOS: ${{ needs.positivo.outputs.nuevos_distintos }}
        run: |
          set -euo pipefail
          python3 - "$RESULTADO" "$NUEVOS" "$DISTINTOS" <<'EOF'
          import json, sys
          resultado, nuevos, distintos = sys.argv[1], int(sys.argv[2]), json.loads(sys.argv[3])
          esperado = json.load(open("verificador/cv/ci/POSITIVO-CI.json"))["hallazgo_esperado"]
          assert resultado == "falla", resultado
          assert nuevos > 0, nuevos
          assert sorted(map(tuple, distintos)) == sorted(map(tuple, esperado)), (distintos, esperado)
          print("positivo: el flujo fallo por", esperado, "en", nuevos, "casos, y por nada mas")
          EOF

  real:
    # LinuxForHealth v1.1.0 traido en el runner, con su huella comprobada, contra la linea base del laboratorio: igual
    needs: pruebas
    uses: ./.github/workflows/verificador-conversor.yml
    permissions:
      contents: read
    with:
      adaptador: lab/verificador/cv/adaptadores/linuxforhealth.json
      artefactos: artefactos
      preparar: bash "$LAB/verificador/cv/ci/preparar_lfh.sh" "$ARTEFACTOS"
      imagen: maven:3.9-eclipse-temurin-11@sha256:7bb84a451705605a47d24eb844d4d9ab03e33e131a507db76aafe25db3907f64
      huella_esperada: ac41f71b98ee75bac637ecd4b68f58b463f0798bf66cfa941f4194cb2a50acf2
      linea_base: lab/verificador/cv/ci/LINEA-BASE-linuxforhealth.json
      laboratorio_ref: ${{ github.sha }}
      esperar: igual

  real-comprobado:
    # las identidades que el ANTES pide, leidas desde fuera del flujo
    needs: real
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - shell: bash
        env:
          HUELLA: ${{ needs.real.outputs.huella }}
          DIGEST: ${{ needs.real.outputs.imagen_digest }}
          RESULTADO: ${{ needs.real.outputs.resultado }}
          ARREGLOS: ${{ needs.real.outputs.arreglos }}
          NUEVOS: ${{ needs.real.outputs.nuevos }}
        run: |
          set -euo pipefail
          test "$RESULTADO" = pasa
          test "$NUEVOS" = 0 && test "$ARREGLOS" = 0
          test "$HUELLA" = ac41f71b98ee75bac637ecd4b68f58b463f0798bf66cfa941f4194cb2a50acf2
          test "$DIGEST" = sha256:7bb84a451705605a47d24eb844d4d9ab03e33e131a507db76aafe25db3907f64
          echo "real: los mismos veredictos que el laboratorio, con la huella y la imagen del estudio"
```

En el negativo y en el real `esperar: igual`, no `pasa`: el ANTES pide «los mismos veredictos», y un `arreglo` que apareciera sin tocar nada sería una diferencia que explicar, no un pase. Un proyecto normal usa `pasa`.

### 4.3 El positivo sembrado: `POSITIVO-CI.json`

```json
{
 "formato": "positivo-ci/1",
 "fichero": "cv/conversor_juguete.py",
 "de": "    if fecha(m.campo(\"PID\", 7)):\n        p[\"birthDate\"] = fecha(m.campo(\"PID\", 7))\n",
 "a": "    if False and fecha(m.campo(\"PID\", 7)):                      # SEMBRADO (etapa 23): pierde PID-7 a proposito\n        p[\"birthDate\"] = fecha(m.campo(\"PID\", 7))\n",
 "hallazgo_esperado": [["PID-7", "fidelidad", "dato_perdido"]],
 "_que": "El juguete deja de escribir Patient.birthDate en su Bundle generico; el juez da dato_perdido en PID-7 (conversion.py _fecha) en cada caso del corpus con PID-7 valido, y ningun otro triple cambia."
}
```

`sembrar_juguete.py <ruta>`: lee `POSITIVO-CI.json` (en su carpeta), exige `texto.count(de) == 1`, escribe el reemplazo y sale con 0; con 0 o más de 1 apariciones sale con 2 sin tocar nada; `--deshacer` hace lo contrario. Solo cambia `generico()`: los nominales (`JUGUETE-NOMINAL`…) no se tocan, así que `prueba_vc.py` sigue en verde aunque la siembra quedara aplicada (P-CI-9 lo comprueba y lo deshace). La huella del juguete cambia con la siembra (`huella_distinta`, aviso), como cambiaría la de cualquier conversor en un commit.

Por qué ese defecto y no otro: es un `dato_perdido` en un campo que la guía manda convertir y que el corpus lleva en casi todos los mensajes; no es un código (evita la duda `valor_distinto`/`codigo_mal_mapeado`); no toca ORU ni VXU más que por el mismo campo del Patient; y el juguete ya pierde PID-7 cuando no tiene 8 cifras, de modo que esos casos ya están en la base y no aparecen como nuevos. La lista exacta de casos que lo muestran la fija la corrida del laboratorio y queda en `RESULTADO-CI.md` (n, no los nombres).

### 4.4 El real: `preparar_lfh.sh <artefactos>`

```bash
#!/usr/bin/env bash
# Etapa 23: LinuxForHealth v1.1.0 como en cv/CV1.md (E-CV-3), dentro de la misma imagen del estudio y con red solo aqui.
# Deja <artefactos>/lfh/lib (el jar y sus dependencias), <artefactos>/lfh/clases (Arnes compilado) y <artefactos>/lfh/Arnes.java.
set -euo pipefail
ART=$(realpath "$1"); LAB=${LAB:-$(realpath "$(dirname "$0")/../../..")}
IMAGEN=${IMAGEN:-maven:3.9-eclipse-temurin-11@sha256:7bb84a451705605a47d24eb844d4d9ab03e33e131a507db76aafe25db3907f64}
M2=${M2:-$ART/.m2}                                   # la cache de Maven; actions/cache la guarda entre corridas
mkdir -p "$ART/lfh/lib" "$ART/lfh/clases" "$M2"
cp "$LAB/verificador/cv/lfh/Arnes.java" "$ART/lfh/Arnes.java"
docker pull "$IMAGEN"
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e MAVEN_OPTS=-Duser.home=/tmp \
  -v "$ART:/w" -v "$LAB/verificador/cv/lfh/pom.xml:/w/pom.xml:ro" -- "$IMAGEN" sh -euc '
    mvn -q -B -f /w/pom.xml -Dmaven.repo.local=/w/.m2 dependency:copy-dependencies -DoutputDirectory=/w/lfh/lib &&
    javac --release 11 -d /w/lfh/clases -cp "/w/lfh/lib/*" /w/lfh/Arnes.java'
n=$(ls "$ART/lfh/lib"/*.jar | wc -l)
echo "lfh/lib: $n jar; Arnes.class: $(ls "$ART/lfh/clases")"
test "$n" -ge 70
rm -rf "$ART/.m2/.cache"                          # no entra en la huella (no esta bajo lib), pero no hace falta en el artefacto
```

- `lib` solo recibe lo que copia `dependency:copy-dependencies` con el mismo `pom.xml` del estudio (DV-CV-3: `v1.1.0` de Maven Central, artefactos inmutables): la huella `ac41f71b…` es la del contenido de `lib` más `Arnes.java`, sin nombres (L-VC-5), y `huella_con_nombres` `7ad4d546…` fija también los nombres. Si Central devolviera otro byte, `--solo-orden` lo para (código 11) antes de la caja.
- `clases` no entra en la huella: compilar con el JDK 11 de la imagen da el mismo comportamiento del arnés, que es trivial, y evita depender del JDK del runner.
- Las dependencias de Maven **se cachean** en el job de la demo, no en el flujo: la caché es del proyecto. El programador añade al job `real` de la demo, si GitHub lo admite en un job `uses:`, un job previo `cache-lfh` que corra `preparar_lfh.sh` con `actions/cache@v4` (`path: artefactos/.m2`, `key: lfh-m2-${{ hashFiles('verificador/cv/lfh/pom.xml') }}`) y suba `artefactos/` como artefacto; si no, se acepta el coste (~1-2 min) y se anota en L-CI-6. Lo recomendado: aceptar el coste en la primera corrida y medirlo.

### 4.5 Cuándo corre y cuánto cuesta

- **Eventos:** `push` a `main` y `pull_request`, solo con cambios bajo `verificador/**`, `.github/workflows/**` o `tests/**`; y `workflow_dispatch` para repetir a mano. Un cambio en `README.md`, `docs/` o `piloto-agente/` no la lanza. La higiene (`higiene.yml`) sigue corriendo en todo push.
- **Coste previsto por corrida** (4 vCPU de `ubuntu-latest`): `pruebas` 1-2 min; `negativo` y `positivo` 2-3 min cada uno (343 casos del juguete, juicio en Python, sin Docker); `real` 5-8 min (checkout 0,5; `docker pull` de la imagen de Maven ~0,5; Maven 1-2; la caja 0,5-1 con 4 contenedores; el juicio de 411 casos 1-2; artefacto 0,2). Total ≈ 10-15 min de runner por push que toque `verificador/`. Se mide en la primera corrida y se escribe en `RESULTADO-CI.md`.
- **Cómo no gastar de más:** `paths`; `concurrency` con `cancel-in-progress`; `timeout-minutes` (30 en el flujo, 10 en `pruebas`, 5 en las comprobaciones); `pruebas` delante de los tres controles (`needs`), así un YAML roto o un guion roto no llega a la caja; `--sin-sensibilidad`; retención de artefactos 14 días; los tres controles en paralelo. El repositorio es público: los minutos no se cobran, pero cuentan en la cola.

---

## 5. El determinismo: qué puede cambiar en el runner y cómo se neutraliza

| Qué | Riesgo | Neutralización | Cómo se ve si falla |
|---|---|---|---|
| **La imagen** | otra `maven:3.9-eclipse-temurin-11` (la etiqueta se mueve) daría otra JVM | `pull` por digest, `tag` y `caja.imagen_digest` en la copia del adaptador: la herramienta sale con 3 si no coincide (S-CI-9); `imagen_digest` va en la base y en el resumen | `imagen_distinta` o código 3 |
| **El conversor** | Maven Central devuelve otro jar o un jar de más/menos | huella de `lib` + `Arnes.java` antes de la caja (`huella_esperada`, S-CI-11); `huella_con_nombres` en la base | código 11 antes de correr |
| **El juez y la herramienta** | otra copia del laboratorio | el flujo saca el laboratorio por `job_workflow_sha` (o `laboratorio_ref`); `juez.huella` y `herramienta.huella` van en la base y se comparan | `juez_distinto` (aviso, o fallo en `igual`) |
| **El corpus** | otra versión de `bases_*.py`, `cv3_minimos.py`, o `--corpus` distinto | la herramienta regenera el corpus y escribe su huella; la base la lleva; con `igual`, distinta = fallo | `corpus_distinto` |
| **La zona horaria** | fechas con desplazamiento distinto | la caja no monta `/etc/localtime` ni pasa `TZ`: la JVM corre en UTC en el laboratorio y en el runner por igual; el proceso Python lleva `TZ=UTC` (solo afecta a `CORRIDA.json.fecha`, que no entra en nada) | con `igual`, un `valor_distinto` en campos de fecha; se adjudica |
| **El orden de los ficheros** | el arrastre de estado de LinuxForHealth depende del orden dentro del proceso (`RESULTADO-ARRASTRE.md`, L-AR-1) | la herramienta copia los `.hl7` con nombres fijos y agrupa por corpus en orden fijo; `Arnes` ordena con `sorted()`; `os.walk` ordenado en las huellas. El mismo lote da los mismos veredictos en dos corridas (ruido 0 en 476 casos) | `hallazgo_nuevo`/`arreglo` en VXU-B18..B40 (los de F7) |
| **La red** | un conversor que necesite red se comportaría distinto | `--network none` en la caja, como en el laboratorio; la red solo en `preparar` y en el `pull` | el conversor falla igual en los dos sitios |
| **Lote o mensaje** | distinto arrastre | la base registra `modo`/`contenedor` y el flujo corre el mismo adaptador (`linuxforhealth.json`, lote); el de mensaje no se usa en la demo por coste (S-CI-13) | `modo` distinto es `conversor_distinto` → código 2 |
| **Docker del runner** | otro runtime, rootless, `userns-remap` | no se neutraliza: se declara (L-VC-9, L-CI-2); `INFORME.json.caja.restricciones` y `cajas/*.log` van en el artefacto | lo que salga se adjudica |
| **Memoria y CPU** | la JVM con menos memoria podría fallar en un mensaje | `memoria_mb: null` como en el laboratorio; `segundos_por_mensaje 60`, contenedor 3600; el reintento uno a uno de Q-VC-D-9 | `sin_respuesta`/`caja`; `CORRIDA.json.reintentos` |
| **Python** | otra versión cambia ordenaciones o `json` | `setup-python` 3.12, `PYTHONHASHSEED=0`; la herramienta ordena todo lo que escribe (S-VC-14) | `INFORME.json` distinto byte a byte, que no ocurre con la misma versión |
| **Codificación y locale** | `LANG` distinto en el runner | la herramienta lee y escribe UTF-8 explícito; `Arnes` usa `StandardCharsets.UTF_8`; la caja no hereda `LANG` | `lectura` indeterminada |
| **Ruido del conversor** | LinuxForHealth escribe ids con reloj y la fecha de conversión | el juez no los mira (`RESULTADO-ARRASTRE.md`: 0 veredictos distintos entre corridas) | no se ve en el veredicto por construcción |

Lo que no es determinista por construcción y se acepta: `CORRIDA.json` (fecha, duraciones, rutas), `cajas/*.log` (tiempos de `Arnes`), y el texto de algunos errores (Microsoft, no LinuxForHealth). Nada de eso entra en la base ni en el veredicto.

---

## 6. La línea base del control real

- **De qué corrida sale.** De una corrida en la máquina del laboratorio, **desde la copia pública** (`publicacion/verificador`, el mismo árbol que se va a publicar, en el commit anterior al push de la etapa), con el juez publicado `b3f00f6a…` y la herramienta tal como está en el manifiesto. No del repositorio de trabajo: su juez (`bde94016…`) daría `juez_distinto` en el runner.
- **Con qué.** `cv/adaptadores/linuxforhealth.json` (lote, `id` `linuxforhealth`), los artefactos del estudio (`lfh/lib`, `lfh/clases`, `lfh/Arnes.java`: huella `ac41f71b…`, imagen digest `7bb84a45…`), corpus público: adt 263, oru 40, vxu 40 y los 68 mínimos (411), **sin muestras** (L-VC-7) y con `--sin-sensibilidad`. Exactamente las opciones del job `real`.

```bash
cd publicacion/verificador
for i in 1 2; do python3 cv/verificar_conversor.py cv/adaptadores/linuxforhealth.json <S>/lfh-$i --artefactos <artefactos> --sin-sensibilidad; done
cmp <S>/lfh-1/INFORME.json <S>/lfh-2/INFORME.json                                                      # iguales byte a byte
python3 cv/ci/linea_base.py crear <S>/lfh-1 -o cv/ci/LINEA-BASE-linuxforhealth.json
python3 cv/ci/linea_base.py comparar <S>/lfh-2 cv/ci/LINEA-BASE-linuxforhealth.json --esperar igual      # 0
```

- **Cómo se comprueba antes de publicarla** (cada paso para si no cuadra; se anota en `RESULTADO-CI.md`):
  1. Las dos corridas salen con 0, `sin_evidencia` vacío, `reintentos` vacío, `imagen_digest` `sha256:7bb84a45…`, huella `ac41f71b…` y `huella_con_nombres` `7ad4d546…` (`CORRIDA.json`), juez `b3f00f6a…`.
  2. `INFORME.json` de las dos corridas es igual byte a byte (P-VC-20, L-VC-11: dos corridas, no una).
  3. `comparar` de la 2.ª contra la base de la 1.ª con `igual` sale con 0: `nuevos 0, arreglos 0, notas 0`.
  4. La base cuadra con lo publicado: en adt y oru, `categorias` por corpus iguales a `cv/vc/ejemplos/INFORME-linuxforhealth.json` (adt: correcto 11, fallo_silencioso 160, rechazo_incorrecto 92; oru: 4 y 36); los pares mínimos de LinuxForHealth que reproduce, iguales a `cv/ar/minimos-AR-lote.json`; en vxu, los 23 casos B18..B40 con `("RXA-17"|"RXA(n)-17", "fidelidad", "dato_perdido")` (el arrastre del lote, F7), como dice `RESULTADO-ARRASTRE.md`. Si el juez publicado y el del laboratorio difieren en alguna categoría, se explica en el documento antes de publicar.
  5. `n_casos == 411` y las claves de `casos` son las de `corpus/CASOS.json` menos `sin_msh`.
  6. El fichero pasa la higiene (está en `JSON_ADMITIDOS`, < 512 KB, sin rutas ni correos) y `python3 cv/ci/prueba_ci.py` en verde.
  7. La base del juguete, igual: dos corridas con `juguete.json --sin-sensibilidad`, `crear` de la primera, `comparar --esperar igual` de la segunda (0), y además `sembrar_juguete.py` + tercera corrida + `comparar --esperar falla --hallazgo-esperado` (0), y `--deshacer`. El n de casos con el triple sembrado se escribe en `RESULTADO-CI.md`.
- **Qué registra `RESULTADO-CI.md`** de esa corrida: fecha, juez, herramienta, huellas, digest, n por corpus, segundos, y las categorías por corpus de la base (sin rutas de máquina).

---

## 7. La guía para un tercero: `verificador/cv/ci/CI.md`

Contenido que el programador escribe (en español, sin rutas de máquina, sin «nuevo/confirmado» fuera de la frase fija; las partes en cursiva son instrucciones, no texto):

> # Pasa tu conversor por el verificador en cada cambio
>
> Un flujo reutilizable de GitHub Actions corre tu conversor en la caja del laboratorio (Docker sin red, solo lectura, sin privilegios), lo juzga con el verificador sobre el corpus público y **falla solo si aparece un hallazgo que no está en tu línea base**. No escribe en tu repositorio ni comenta en tus PR: necesita `permissions: contents: read` y ningún secreto.
>
> ## Lo que pones en tu proyecto
> 1. **Un adaptador** (`ci/adaptador.json`), como los de `cv/adaptadores/` (formato `adaptador-vc/1`, §2 de `cv/vc/diseno-vc-fable.md`). Las rutas de los montajes y de la huella son relativas a la carpeta de artefactos.
> 2. **Una orden que prepare los artefactos** (`preparar`): lo que construye o descarga tu conversor en `$ARTEFACTOS`. Corre con red; después, nada tiene red.
> 3. **La imagen con digest** (`imagen`): `docker pull <repo>:<etiqueta>` y `docker image inspect --format '{{index .RepoDigests 0}}' <repo>:<etiqueta>` te dan `repo@sha256:…`. El flujo la trae por el digest y exige que sea esa.
> 4. **La línea base** (`ci/LINEA-BASE.json`). La primera vez se hace en tu máquina:
>    ```bash
>    git clone https://github.com/LK-Corporation/lab-integraciones && cd lab-integraciones/verificador
>    python3 cv/verificar_conversor.py <tu adaptador> <salida> --artefactos <tus artefactos> --sin-sensibilidad
>    python3 cv/ci/linea_base.py crear <salida> -o <tu repo>/ci/LINEA-BASE.json
>    ```
>    o, más simple, lanzas el flujo con una base vacía (`{"formato": "linea-base-ci/1", "casos": {}}`): falla, y en el artefacto queda `LINEA-BASE-propuesta.json`, que subes como base.
> 5. **El flujo**, en `.github/workflows/verificador.yml`:
>    ```yaml
>    name: verificador
>    on:
>      pull_request:
>      push:
>        branches: [main]
>    permissions:
>      contents: read
>    jobs:
>      verificar:
>        uses: LK-Corporation/lab-integraciones/.github/workflows/verificador-conversor.yml@<commit del laboratorio>
>        permissions:
>          contents: read
>        with:
>          adaptador: proyecto/ci/adaptador.json
>          linea_base: proyecto/ci/LINEA-BASE.json
>          preparar: cd "$PROYECTO" && ./gradlew -q jar && cp build/libs/*.jar "$ARTEFACTOS/lib/"
>          imagen: eclipse-temurin:11-jre@sha256:<64 hex>
>          corpus: proyecto/ci/mensajes
>    ```
>    `proyecto/` es tu repositorio y `lab/` el laboratorio, los dos en el workspace. Fija el laboratorio a un commit (`@<sha>`): el juez, la herramienta y el corpus son los de ese commit, y tu base se hizo con ellos. Cuando lo subas, regenera la base.
>
> ## Lo que hace fallar el cambio
> *(la tabla de §2.3, columna `pasa`)* Un hallazgo que no estaba, un caso que pierde su salida o pasa a indeterminado, un caso de la base que ya no está, o la caja que no pudo correr. Lo que desaparece es un arreglo: se lista y no falla.
>
> ## Lo que te deja
> El resumen en la página del job y el artefacto `verificador-<job>-<n>` con `INFORME.md`, `INFORME.json`, `juicio.jsonl`, `VEREDICTO-CI.json` y `LINEA-BASE-propuesta.json`.
>
> ## Cómo aceptas un cambio
> Descarga `LINEA-BASE-propuesta.json` del artefacto, cópiala sobre `ci/LINEA-BASE.json` y súbela en el mismo PR. Lo que la base registra son veredictos del juez, no tu opinión: aceptar un hallazgo en la base no lo convierte en correcto; lo convierte en conocido.
>
> ## Lo que no hace
> No sabe si tu proyecto ya tenía declarado cada hallazgo (L-VC-1); no admite servicios HTTP ni bibliotecas (L-VC-3); no lee las muestras de los proyectos del estudio (L-VC-7); corre en `ubuntu-latest` con su Docker (L-VC-9); juzga ADT (ocho eventos), ORU^R01 y VXU^V04 (L-VC-2); una corrida es una corrida (L-VC-11). Microsoft FHIR-Converter se puede preparar con `dotnet publish` en `preparar` (ver `cv/CV1.md`), pero no es un control de esta etapa.
>
> ## Un ejemplo completo
> *(el `demo-ci.yml` del laboratorio, con el job `real` explicado línea a línea: `preparar_lfh.sh`, la imagen por digest, `huella_esperada`, y `esperar: igual` frente a `pasa`)*
>
> ## Cómo repetirlo en tu máquina
> ```bash
> python3 cv/verificar_conversor.py ci/adaptador.json <salida> --artefactos <artefactos> --sin-sensibilidad
> python3 cv/ci/linea_base.py comparar <salida> ci/LINEA-BASE.json          # 0 pasa, 10 falla; VEREDICTO-CI.md lo cuenta
> ```

`CI.md` se enlaza desde `cv/VC.md` («Pasa tu conversor en cada cambio») y desde `verificador/README.md` (sección nueva de la etapa 23), y `RESULTADO-CI.md` y `ANTES-ETAPA-CI.md` desde `verificador/README.md` y el `README.md` raíz (por la guarda de alcanzabilidad).

---

## 8. La previsión que se sella

`cv/ci/prevision-cuerpo-ci.json` (el cuerpo que escribe el programador antes de la primera corrida en GitHub Actions) y `cv/ci/sellar_prevision_ci.py <cuerpo> [<carpeta>]`, calcado de `cv/ar/sellar_prevision.py`: añade `fecha`, `juez` (el publicado), `conversor` (`ac41f71b…`), `imagen_digest`, `herramienta` (huellas de `verificar_conversor.py`, `linea_base.py`, `sembrar_juguete.py`, `preparar_lfh.sh`, los dos YAML) y escribe `PREVISION-CI.json` y `SELLO-CI.txt` (huellas de la previsión, los guiones, los YAML, las dos bases y `POSITIVO-CI.json`; se niega a pisar un sello). Después, un commit; el push de la demo es el que sella de verdad (la primera corrida en Actions es posterior al commit del sello por construcción).

Claves (`CLAVES_PREVISION_CI`, todas obligatorias):

| Clave | Qué | Valor que propone el diseñador |
|---|---|---|
| `etapa` | texto fijo | «23, el verificador en la CI de un conversor» |
| `base_de_la_prevision` | lo que se sabe antes de correr nada en Actions | el control de la etapa 18 (0 diferencias), el ruido 0 del arrastre, el juguete sin Docker; nunca se ha corrido el flujo en un runner |
| `probabilidad_pruebas_verdes_a_la_primera` | P-CI en verde en Actions sin retocar | 0,75 |
| `probabilidad_negativo_a_la_primera` | el job `negativo` verde en la primera corrida | 0,70 |
| `probabilidad_positivo_a_la_primera` | `positivo` y `positivo-comprobado` verdes | 0,60 |
| `probabilidad_real_a_la_primera` | `real` y `real-comprobado` verdes | 0,40 |
| `probabilidad_real_mismos_veredictos` | cuando `real` llega a comparar, `nuevos = arreglos = 0` | 0,85 |
| `probabilidad_real_huella_cuadra` | la huella en el runner es `ac41f71b…` | 0,85 |
| `probabilidad_los_tres_verdes_en_una_sesion` | la etapa cierra en su tope | 0,55 |
| `pushes_previstos` | pushes al público hasta los tres en verde, cada uno por la opción B | `[1, 4]`, más probable 2 |
| `minutos_por_corrida_previstos` | runner, los cuatro jobs | `[8, 16]` |
| `positivo_n_casos_previsto` | casos del juguete con el triple sembrado | `[300, 343]` |
| `causas_de_fallo_previstas` | ordenadas por probabilidad | `job_workflow_sha` no resuelve en el checkout; `github.job` en el nombre del artefacto; el `tag` tras el `pull` por digest; permisos de `tout` (0777) con el Docker del runner; `--pids-limit` sin cgroup; PyYAML; la caché de Maven |
| `diferencias_que_se_explicarian` | si el real difiere | fechas con desplazamiento (TZ), un reintento por tiempo vencido en la JVM, otro orden del lote |
| `regla_de_parada` | copiada del ANTES | «resultado no determinista o que no cuadra y no se explica → solo la demostración con el juguete» |
| `jev` | la previsión de Jev con estado neutro, al lado | `{probabilidad_real_a_la_primera, probabilidad_real_mismos_veredictos, pushes_previstos}` |

---

## 9. Las pruebas en rojo: `cv/ci/prueba_ci.py`, P-CI-1..14

Estilo de `prueba_vc.py` (`mira`, `grupo`, `PRUEBAS`, `rojo`): `python3 cv/ci/prueba_ci.py` → `PRUEBAS CI: TODO BIEN (n comprobaciones, 14 pruebas)`; `python3 cv/ci/prueba_ci.py rojo` sale 0 solo si fallan las 14. En rojo, `import linea_base`, `import sembrar_juguete` y los YAML no existen, y cada prueba falla por eso. Sin Docker, sin red; el juguete como conversor (corpus propio de 3-6 mensajes de `prueba_conversion.msg`/`oru_msg`, con `--sin-corpus-lab --sin-minimos --sin-sensibilidad` como `prueba_vc.correr`). Dependencia de pruebas: PyYAML (`import yaml`; si falta, P-CI-10..13 marcan `MAL: instala pyyaml`, no se saltan).

| Prueba | Qué comprueba | Control negativo |
|---|---|---|
| P-CI-1 | `crear` desde una corrida del juguete da `linea-base-ci/1` con claves ordenadas, `casos` = los de `juicio.jsonl` con `(estado, categoria, subtipo, hallazgos)` idénticos a `verificar_conversor.comparar._valor`, identidades de `INFORME.json`, `modo` de `ADAPTADOR.json`, sin fechas ni rutas; dos `crear` seguidos dan el mismo fichero byte a byte | una carpeta sin `CORRIDA.json` → código 2; con `sin_evidencia` simulado en `INFORME.json` → 2, y 0 con `--permitir-sin-evidencia` |
| P-CI-2 | `comparar` de una corrida contra su propia base: `pasa`, 0 nuevos, 0 arreglos, código 0; `igual` también 0; `VEREDICTO-CI.json` determinista | una base con un triple de más → `arreglo`, código 0 en `pasa` y 10 en `igual` |
| P-CI-3 | hallazgo nuevo: corrida con `JUGUETE-GENERO` en un caso cuya base era el nominal → `hallazgo_nuevo` con el triple de PID-8, código 10, `nuevos_distintos` = ese triple, `motivos` = `["hallazgo_nuevo"]` | el mismo triple ya en la base → 0 |
| P-CI-4 | caso nuevo: un caso de la corrida que no está en la base; con hallazgos → `hallazgo_nuevo` (10); sin hallazgos (nominal `correcto`) → `caso_nuevo`, 0 en `pasa` y 10 en `igual` | — |
| P-CI-5 | caso ausente: la base con un caso que la corrida no tiene → `caso_ausente`, 10 | quitarlo de la base → 0 |
| P-CI-6 | `salida_perdida` (base `bundle`, corrida `JUGUETE-ERROR` → estado `error`) e `indeterminado_nuevo` (corrida `JUGUETE-NADA` → `vacio`/indeterminado) → 10 cada uno; y lo contrario (base `error`, corrida `bundle`) → `arreglo`, 0 | — |
| P-CI-7 | `--rc-herramienta 4` → `caja`, 10 aunque los casos cuadren; `conversor.id` distinto → 2; `juez`/`corpus`/`imagen_digest`/`huella` distintos → avisos, 0 en `pasa`; en `igual`, 10 salvo `huella_distinta` | — |
| P-CI-8 | `--esperar falla --hallazgo-esperado '[[PID-8…]]'`: con la corrida de P-CI-3 → 0; con una corrida que pasa → 10; con un triple nuevo distinto del esperado → 10; con el esperado y otro más → 10; con `caso_ausente` además → 10 | — |
| P-CI-9 | `sembrar_juguete.py` sobre una copia de `conversor_juguete.py`: cuenta 1, escribe, y el juguete copiado pierde `birthDate` en `generico()` (se importa la copia y se llama a `convertir` con un A01 sin directiva: el Bundle no lleva `birthDate`; con `JUGUETE-NOMINAL`, sí); `--deshacer` devuelve el fichero byte a byte; sobre un fichero sin el texto o con dos apariciones → 2 y sin tocar | — |
| P-CI-10 (extremo a extremo, sin Docker) | con `juguete.json` sobre 4 mensajes: corrida A → `crear`; siembra **del juguete real** (el adaptador exige su ruta real; se deshace en `finally`, como P-CI-9) → corrida B → `comparar --esperar falla --hallazgo-esperado` el de `POSITIVO-CI.json` → 0; y `nuevos_distintos == [["PID-7","fidelidad","dato_perdido"]]` | corrida B contra la base con `pasa` → 10; corrida A contra la base con `falla` → 10 |
| P-CI-11 (YAML, estático) | los dos YAML se cargan con `yaml.safe_load`; `verificador-conversor.yml` tiene `on.workflow_call` con exactamente las entradas de §3.1 (nombres, tipos, obligatorias) y las 7 salidas; `permissions == {"contents": "read"}` en los dos ficheros y en cada job `uses:` de la demo; ningún `secrets`, ningún `pull-requests`/`issues`/`contents: write`; todo `uses:` de acción está fijado (`@v4`/`@v5` o un sha) y pertenece a `actions/`; `runs-on: ubuntu-latest`; `timeout-minutes` en todo job con `steps` | el YAML con `contents: write` inyectado → la guarda lo ve; con una entrada menos → lo ve; con `uses: otro/accion@main` → lo ve |
| P-CI-12 (YAML, la caja) | en `verificador-conversor.yml` ningún `run:` contiene `docker run`; los únicos `docker` son `version`, `pull`, `image inspect` y el `tag` que imprime `fijar-imagen`; el paso de verificar llama a `cv/verificar_conversor.py` sin `--comparar` ni `--muestras`; el paso de veredicto escribe en `$GITHUB_STEP_SUMMARY` y usa `--github-output` | un `docker run` añadido → lo ve |
| P-CI-13 (YAML, la demo) | `demo-ci.yml`: `on.push.branches == ["main"]`, `paths` con los tres patrones, `concurrency.cancel-in-progress`, `workflow_dispatch`; los jobs `negativo`, `positivo` y `real` usan `./.github/workflows/verificador-conversor.yml` y `laboratorio_ref: ${{ github.sha }}`; `positivo` lleva `sembrar: juguete`, `esperar: falla` y `hallazgo_esperado` igual al de `POSITIVO-CI.json`; `real` lleva `imagen` con el digest `7bb84a45…`, `huella_esperada` `ac41f71b…`, `esperar: igual` y `linea_base` `LINEA-BASE-linuxforhealth.json`; `negativo`/`real` llevan `esperar: igual`; `positivo-comprobado` y `real-comprobado` tienen `needs` del job que comprueban | `hallazgo_esperado` cambiado en el YAML → lo ve; `esperar: pasa` en el positivo → lo ve |
| P-CI-14 | `fijar-imagen`: con `maven:3.9-eclipse-temurin-11@sha256:<d>` y el adaptador `linuxforhealth.json` (artefactos de `prueba_vc.artefactos_lfh`) escribe la copia con `imagen_digest` = `sha256:<d>` y, con `--etiquetar`, imprime `docker tag maven@sha256:<d> maven:3.9-eclipse-temurin-11`; con `proceso_local` e imagen vacía, copia sin cambios; la copia pasa `leer_adaptador` con `--artefactos`; y las bases publicadas (`LINEA-BASE-juguete.json`, `LINEA-BASE-linuxforhealth.json`, si existen) tienen el formato, `n_casos` = `len(casos)` y `conversor.id` el del adaptador | otro repositorio (`python@sha256:…` con el adaptador de Maven) → 2; digest mal formado → 2 |

Además, `tests/test_repo_hygiene.py` gana en `JSON_ADMITIDOS` las entradas `verificador/cv/ci/LINEA-BASE-juguete.json`, `verificador/cv/ci/LINEA-BASE-linuxforhealth.json`, `verificador/cv/ci/POSITIVO-CI.json`, `verificador/cv/ci/prevision-cuerpo-ci.json`, `verificador/cv/ci/PREVISION-CI.json` y `verificador/cv/ci/preguntas_qci.json`. Las guardas de ruta y de `docker inspect` ya admiten lo que estos YAML usan (`docker image inspect` no casa con `docker\s+(inspect|…)`; `/tmp` y `$HOME` son neutros). `.sh` no está en `SUFIJOS_ADMITIDOS`: el programador añade `.sh` a `SUFIJOS_TEXTO` (y a la fila MIT de `LICENSE.md`); alternativa, si se prefiere no tocar la higiene: `preparar_lfh.py` en Python, que llama a `docker` con `subprocess` (mismo contenido). Recomendado: `.sh` admitido, porque es lo que un tercero copiará.

---

## 10. Las preguntas de diseño para Jev (Q-CI-D)

Se pasan con estado neutro (`cv/ci/estado_qci.md`, `cv/ci/preguntas_qci.json`, el formato de `cv/ar/preguntas_qar.json`), sin la recomendación. La recomendación va aquí, aparte.

| Q | Pregunta | Opciones |
|---|---|---|
| Q-CI-D-1 | Un caso que está en la corrida y no en la base, **con** hallazgos que cuentan (el proyecto añadió un mensaje propio, o subió la ref del laboratorio y el corpus creció) | (a) falla: cada triple suyo es nuevo; (b) no falla: se lista como `caso_nuevo` y entra en la propuesta; (c) falla solo si el caso es del corpus `propio` (lo añadió el proyecto) |
| Q-CI-D-2 | Un caso de la base que no está en la corrida (`caso_ausente`) | (a) falla; (b) aviso y la propuesta lo quita; (c) falla solo si la huella del corpus es la misma que la de la base (desapareció sin que cambiara el corpus) |
| Q-CI-D-3 | El modo del control real con LinuxForHealth | (a) lote, el adaptador de referencia del estudio (≈1 min de caja); (b) mensaje a mensaje (≈30 min por corrida, sin arrastre); (c) lote en cada push y mensaje a mensaje solo en `workflow_dispatch` |
| Q-CI-D-4 | La huella del juez distinta de la de la base, en modo `pasa` | (a) aviso: la comparación sigue y lo que salga nuevo falla; (b) falla siempre: el proyecto regenera la base al subir el laboratorio; (c) aviso, y la propuesta se marca «juez cambiado» |
| Q-CI-D-5 | Qué lleva el artefacto por omisión | (a) informe, juicio, veredicto, propuesta y los registros de las cajas (sin evidencias ni corpus); (b) además `evidencias/` y `corpus/` (más pesado; lleva los mensajes); (c) solo informe y veredicto |
| Q-CI-D-6 | Cuándo corre la demostración en el repositorio del laboratorio | (a) `push` a `main` y PR, solo con `paths` de `verificador/**`, `.github/workflows/**`, `tests/**`, y `workflow_dispatch`; (b) en todo push, como la higiene; (c) solo `workflow_dispatch` y un `schedule` semanal |

**Recomendación del diseñador, aparte:** Q-CI-D-1 (a), porque la pregunta fija del ANTES dice «un hallazgo que no estaba en su línea base» y un mensaje nuevo con un hallazgo es exactamente eso; Q-CI-D-2 (a), la pérdida de cobertura no debe pasar en silencio y actualizar la base es un commit; Q-CI-D-3 (a), por coste y porque la base registra el modo; Q-CI-D-4 (a), la deriva del juez ya aparece como hallazgos nuevos si los hay; Q-CI-D-5 (a); Q-CI-D-6 (a). El diseño de arriba está escrito con (a) en todas; si Jev elige otra, cambia una rama de `comparar` (D-1, D-2, D-4), un adaptador y una línea de la demo (D-3), la lista de `path` del artefacto (D-5) o el bloque `on:` (D-6), y nada más.

---

## 11. Los límites (L-CI-n)

- **L-CI-1.** El flujo distingue lo nuevo de lo conocido al nivel de Q-VC-D-7: el triple `(hecho, clase, subtipo)` por caso. Un cambio de valor dentro del mismo subtipo, una repetición más de un campo ya perdido, o un cambio en notas y convenciones no se ve (como L-AR-3).
- **L-CI-2.** La caja en el runner es la de la herramienta con el Docker de `ubuntu-latest`; no se comprueba el núcleo (L-VC-9). Otro runner (`self-hosted`, rootless, otro runtime) queda fuera.
- **L-CI-3.** Solo GitHub Actions. Otro CI reutiliza `linea_base.py` y la herramienta, no el YAML.
- **L-CI-4.** El control real es LinuxForHealth v1.1.0 en lote sobre el corpus público (411 casos, sin muestras: L-VC-7). Microsoft no se construye en el runner (fuera de la etapa); el de mensaje a mensaje no corre en la demo (coste).
- **L-CI-5.** Una corrida por push: el flujo no comprueba que el conversor sea determinista (L-VC-11). Un conversor no determinista dará nuevos/arreglos intermitentes; el proyecto lo verá en el resumen y es su decisión.
- **L-CI-6.** Los minutos: ≈10-15 por corrida de la demo, con Maven sin caché en el flujo. El coste real se mide en la primera corrida.
- **L-CI-7.** La línea base registra veredictos del juez, no contrastes con el proyecto (L-VC-1): «conocido» no es «declarado» ni «correcto». `CI.md` lo dice y el resumen no usa «nuevo» en el sentido del estudio: usa «hallazgo nuevo» como «no estaba en la base», y la frase fija de la herramienta sigue en `INFORME.md`.
- **L-CI-8.** El positivo prueba un `dato_perdido` en un campo de fecha; otro tipo de defecto (un código mal mapeado, un rechazo) queda probado solo por P-CI-3/6, sin Docker, no en el runner.
- **L-CI-9.** La base del real sale del juez publicado; la deriva entre el juez del laboratorio y el publicado no entra (ya está medida: solo el extracto y C19, `MANIFIESTO.txt`).
- **L-CI-10.** `preparar` corre lo que el proyecto diga, con red, en el runner del proyecto: el flujo no lo aísla (es su propio código, como en cualquier CI). La caja es solo para el conversor cuando convierte.
- **L-CI-11.** Un proyecto que necesite más de 30 minutos (el `timeout-minutes` del flujo) o un contenedor por mensaje con JVM no cabe sin cambiar el tope; se declara en `CI.md`.
- **L-CI-12.** Lo que el flujo comprueba de sí mismo (`esperar: falla`) lo vuelve a comprobar `positivo-comprobado` desde los outputs; si GitHub no propagara los outputs de un job `uses:`, queda solo la comprobación interna y se declara.
- **L-CI-13.** El tercero debe fijar el laboratorio a un commit; con `@main` el juez y el corpus podrían moverse bajo su base y lo vería como `juez_distinto`/`corpus_distinto` y, quizá, hallazgos nuevos que no son suyos.

---

## 12. El plan

Tope: una sesión. Cada push al público pasa por la opción B (guarda LIMPIO, higiene, revisión a ciegas y Jev). Lo que GitHub Actions responda solo se sabe tras un push: el plan separa lo que se cierra en el laboratorio (pasos 0-7) de lo que exige el runner (8-10).

| Paso | Qué | Hecho cuando | Si falla |
|---|---|---|---|
| 0 | Q-CI-D-1..6 a Jev con estado neutro (`estado_qci.md`, `preguntas_qci.json` → `decision-jev-qci.md`, `decisiones-qci.md`) | decididas | — |
| 1 | `cv/ci/prueba_ci.py` en rojo: P-CI-1..14 fallan por la razón prevista; commit | `rojo` sale 0 | — |
| 2 | Código: `linea_base.py` (`crear`, `comparar`, `fijar-imagen`), `sembrar_juguete.py`, `POSITIVO-CI.json`, `preparar_lfh.sh`, los dos YAML, `sellar_prevision_ci.py`; `prueba_ci.py` verde; `prueba_vc.py`, `prueba_ar.py`, `prueba_rv.py` y `pytest tests` verdes (con `JSON_ADMITIDOS` y `.sh` al día); commit | todo verde, sin tocar `verificar_conversor.py` ni el juez (`MANIFIESTO.txt` lo atestigua) | — |
| 3 | **Bases del juguete** desde la copia pública: dos corridas, `crear`, `comparar --esperar igual` (0); siembra, tercera corrida, `comparar --esperar falla` (0), `--deshacer`; n de casos sembrados anotado | `LINEA-BASE-juguete.json` en el repo y P-CI-14 verde | parar: el positivo no sale en el laboratorio, no se va al runner |
| 4 | **Base del real** desde la copia pública (§6, pasos 1-6), con los artefactos del estudio | `LINEA-BASE-linuxforhealth.json` con juez `b3f00f6a…`, huella `ac41f71b…`, digest `7bb84a45…`, 411 casos; `INFORME.json` igual en dos corridas | parar y declarar: el real no determinista en el laboratorio no va al runner |
| 5 | **Humo de `preparar_lfh.sh` en el laboratorio** (con red, una vez): en una carpeta vacía, la huella que sale es `ac41f71b…` y `huella_con_nombres` `7ad4d546…` | las dos cuadran | arreglar el guion (es el eslabón débil del real: Maven en el runner) |
| 6 | `ANTES-ETAPA-CI.md` en `verificador/`, `cv/ci/CI.md`, enlaces en `cv/VC.md`, `verificador/README.md` (sección de la etapa 23) y `README.md`; `LICENSE.md` con `.sh`; `MANIFIESTO.txt` regenerado | higiene verde | — |
| 7 | **Previsión sellada** (§8): cuerpo, Jev al lado, `sellar_prevision_ci.py`, commit del sello **antes del primer push** | `SELLO-CI.txt` en HEAD | no se hace push (como en AR: código 7) |
| 8 | **Push 1** por la opción B: se publica el aparato con la demo. Se lee Actions: los cuatro jobs. Se anota `minutos` y cada fallo con su causa | `pruebas` verde y, si hay suerte, los tres controles | cada arreglo es un commit nuevo y un push por la opción B; el tope de pushes es el de la previsión (4); si el real falla por algo que no sea del aparato (Docker del runner, Maven), ver 9 |
| 9 | **Adjudicar el real**: `nuevos`/`arreglos` del resumen caso por caso contra la base; cada diferencia se explica (TZ, orden, reintento, JVM) o no | 0 diferencias, o todas explicadas en `RESULTADO-CI.md` | **regla de parada:** no determinista o no cuadra sin explicación → se declara, se quita el job `real` de la demo (queda en `CI.md` como ejemplo) y se publica solo el juguete |
| 10 | `RESULTADO-CI.md` con la frase fija del ANTES (o la del resultado negativo), la tabla de los tres controles con su enlace a la corrida (`run_id`), los minutos, la previsión frente a lo que salió, los límites y cómo repetir; nota en `cv/VC.md` y en `verificador/README.md`; push final por la opción B | publicado, los tres en verde en la corrida del commit publicado | — |

**Lo que el plan no permite:** tocar `verificar_conversor.py`, `conversor_juguete.py` (salvo la siembra en el runner, que no se publica aplicada), `cv/lfh/*`, `cv/ar/*` ni el juez; un push sin `SELLO-CI.txt` en un commit; publicar `LINEA-BASE-linuxforhealth.json` sin los pasos 1-6 de §6; abrir issues o PR en los proyectos de los conversores; usar `continue-on-error` o un `permissions` distinto de `contents: read`.

**Orden de los eslabones débiles, por si el tope aprieta:** (1) el checkout del laboratorio por `job_workflow_sha` y los outputs de un job `uses:` (lo prueba `pruebas` + `negativo`, lo más barato); (2) la siembra y el `falla` (`positivo`); (3) Maven y la huella en el runner (`real`, paso de identidades, antes de la caja); (4) la caja con el Docker del runner; (5) la comparación. Si (3) o (4) fallan y no se arreglan en el tope, la regla de parada se aplica y la demo queda con el juguete.

---

