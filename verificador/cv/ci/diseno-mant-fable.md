# Diseño de la etapa 25: el mantenimiento del flujo de integración continua (diseño a ciegas, Fable, 31-oct-2026)

Encargo: `cv/ci/ENCARGO-MANT0.md`. Marco: `ANTES-ETAPA-MANT.md`, que no se negocia. Leído: `MAYORES.txt`, las notas de las doce
mayores (datos de terceros) y el repositorio público en `917ff18`. Quien programe sigue esto al pie de la letra; lo que GitHub
responda solo se sabe tras cada push.

Notación: `C1` = `5183b4edeb2fff421cd441b248f141ccd52852bc` (el pin de hoy en el ejemplo); `M1`, `M2`, `M3`, los pushes de esta
etapa. Los sha son los de `MAYORES.txt` (31-oct); el programador los vuelve a cruzar el día del push (§2.3).

## 1. Las decisiones (S-MANT-n)

| Id | Decisión | Por qué |
|---|---|---|
| S-MANT-1 | Se fijan las cuatro acciones a **la última mayor**: checkout `v7.0.1`, setup-python `v7.1.0`, upload-artifact `v7.0.2`, download-artifact `v8.0.2`, todas `runs.using: node24` (Q-MANT-D-1; si Jev elige la mínima, §2.2 da los sha y nada más cambia) | ninguna novedad de sus notas toca una entrada que estos flujos usen (§2.1); cierra la deuda de una vez y es lo que copiaría hoy un tercero |
| S-MANT-2 | Los 16 `uses:` de los cinco YAML que corren cambian **solo** sus 40 hex y su etiqueta; ninguna otra línea cambia, salvo lo que decida Q-MANT-D-2 en `higiene.yml` | «nada cambia» se demuestra byte a byte contra las plantillas nuevas (P-CI-26/27) |
| S-MANT-3 | `ACCIONES-CI.json` sigue en `acciones-ci/1`, con `fecha` nueva y, por acción, `node` (el `runs.using` del `action.yml` en ese sha, leído por la API) y `anterior` (`etiqueta` y `sha` de la 24) | el registro dice qué corre y de dónde viene; P-CI-28 exige `node24` y un sha distinto del anterior |
| S-MANT-4 | Plantillas nuevas en `cv/ci/github-mant/`: los cinco YAML tal como se sellan, `ejemplo-ci.yml` y `rojo-ci.yml` con el literal `COMMIT_M1`; `cv/ci/github-ci2/` no se toca y P-CI-28 comprueba que sus huellas siguen siendo las de `SELLO-CI2.txt`; `plantillas_dir()` pasa a `github-mant` | las de la 24 están selladas |
| S-MANT-5 | Dos pushes para el pin, como dice el ANTES: `M1` sube las acciones en los cinco YAML y el pin del ejemplo sigue en `C1`; `M2` sube el pin a `M1` en `ejemplo-ci.yml` y `rojo-ci.yml`, y nada más; `M3` publica el resultado | un commit no puede llevar su propio hash; el flujo que llama el ejemplo tiene que ser el de las acciones nuevas |
| S-MANT-6 | «Nada cambia» se mide por huella: `traer_resultados_ci.py --igual-a` deja de limitarse a `verificador-*` y compara todo artefacto por nombre con la referencia (`informe_sha256`; los `COMPROBACION-*`, como objetos JSON): `CORRIDA-CI-1.json` (demo), `CORRIDA-CI2-2.json` (ejemplo), `CORRIDA-CI2-3.json` (rojo) | lo registrado en la 23 y la 24 ya lleva las huellas; nada que rehacer en el laboratorio |
| S-MANT-7 | El aviso de Node.js 20 se lee por la API de anotaciones de cada job con un guion nuevo, `cv/ci/anotaciones_ci.py` → `AVISOS-MANT.json`; su control negativo es una corrida de la 24, que tiene que llevarlo | no está en los artefactos ni en `gh run view --json`; sin control negativo, «no hay aviso» no vale nada |
| S-MANT-8 | `ensayo_flujo.py` no cambia: emula las cuatro acciones por su nombre, sin mirar la versión; lo que la versión cambia solo se ve en el runner (§2.4) | el ensayo prueba que el texto de los YAML sigue haciendo lo mismo; no corre el código de las acciones |
| S-MANT-9 | Las bases del ejemplo no se regeneran: juez, herramienta, conversor e imagen son los mismos; `CI.md` lo precisa («regenera la base» vale cuando cambia el juez) | el pin sube a un commit que solo cambia los YAML |
| S-MANT-10 | No cambian: el juez, `verificar_conversor.py`, `linea_base.py`, los conversores, `ejemplo-ci/` salvo su README, `comprobar_ejemplo.py`, `comprobar_rojo.py`, `cv/ci/github/`, `cv/ci/github-ci2/`, `SELLO-CI.txt`, `SELLO-CI2.txt`; `MANIFIESTO.txt` regenerado lo atestigua | condición 1 del ANTES |
| S-MANT-11 | La previsión se sella antes de `M1` con `sellar_prevision_mant.py` (copia del de la 24, §6); `prueba_ci.py` cambia en `M2` (la constante del pin) y el sello deja de verificarlo, como en DV-CI2-10 | lo que corre es lo sellado, salvo los 40 hex que no se conocen antes |
| S-MANT-12 | Sin PR en esta etapa (Q-MANT-D-3): `M3` va a `main`; el evento `pull_request` con las acciones nuevas queda sin recorrer y se declara | ninguna nota cambia nada propio de ese evento en estos flujos; un push y dos corridas menos |

## 2. Las versiones

### 2.1 Lo que las notas cambian para estos flujos

Lo que estos flujos piden a cada acción, y nada más: **checkout**: `path`, `persist-credentials: false` (los siete checkouts de
los cuatro flujos del verificador), `repository` + `ref` (el laboratorio), y en `higiene.yml` `fetch-depth: 0` sin
`persist-credentials`; **setup-python**: `python-version: "3.12"`, sin `cache`; **upload-artifact**: `name`, `retention-days`,
`if-no-files-found`, `path` multilínea con prefijo común `trabajo/`; **download-artifact**: `name` + `path`, de artefactos
subidos en la misma corrida por el job `verificar` del flujo llamado.

**checkout** (hoy `v4.4.0`, node20).
- `v5.0.0`: node24; runner mínimo 2.327.1 (los hospedados lo superan). Sin más efecto.
- `v6.0.0`: «Persist creds to a separate file»: con `persist-credentials: true` el token deja de ir a `.git/config` y va a un
  fichero aparte. Con `false` no se persiste nada: **los siete checkouts del verificador, sin efecto**. En `higiene.yml` (por
  omisión, `true`) cambia dónde queda el token; nada del job lo usa después (`pytest` lee `git log` local). Es Q-MANT-D-2.
- `v7.0.0`: bloquea el checkout de un PR de fork en `pull_request_target` y `workflow_run` (ningún flujo usa esos eventos);
  módulo ESM y dependencias; texto de errores. Sin efecto.

**setup-python** (hoy `v5.6.0`, node20).
- `v6.0.0`: node24; entradas nuevas `pip-version`, `.python-version`, `Pipfile` (no se usan: `python-version` explícita); la
  caché sin directorio pasa de error a aviso (sin `cache`, no aplica). Sin efecto.
- `v7.0.0`: ESM; quita `pip-install` (no se usa); los avisos de stderr salen como `warning` y no como `error` en las
  anotaciones (no toca el resultado; `anotaciones_ci.py` las registra todas, así que se vería); reintenta el manifiesto;
  `@actions/cache` 6.2.0 (sin `cache`, no aplica); quita versiones EOL de sus *fixtures* (3.12 no lo es). Sin efecto.
- **La caché de Python:** ninguno de los tres `setup-python` pide `cache:`. Nada que probar ni declarar.

**upload-artifact** (hoy `v4.6.2`, node20).
- `v5.0.0`: `@actions/artifact` 4.0.0; **sigue en node20** (`MAYORES.txt`): no sirve.
- `v6.0.0`: node24; arreglo del aviso de `punycode`. Sin efecto.
- `v7.0.0`: ESM; `archive: false` sube un fichero sin comprimir e ignora `name`, solo si se pide: no se pide. La raíz del
  artefacto sigue siendo el antecesor común de los `path` (`trabajo/` se quita: `corrida/…` y `solo-orden.txt`), que es lo que
  leen los comprobadores. Sin efecto.

**download-artifact** (hoy `v4.3.0`, node20).
- `v5.0.0`: rompe el `path` de un artefacto bajado **por id** (`artifact-ids`): deja de anidarse. **Por nombre, «unchanged»:**
  `name: X`, `path: D` → `D/` directo. Los tres `download-artifact` bajan por nombre: `artefacto-ejemplo/corrida/INFORME.json`,
  `artefacto-propio/…`, `artefacto/corrida/…`, como hoy. Sigue en node20.
- `v6.0.0`: `@actions/artifact` 4.0.0; node20.
- `v7.0.0`: node24; `punycode`. Sin efecto.
- `v8.0.0`: ESM; no descomprime lo que no venga comprimido (mira `Content-Type`; lo nuestro lo comprime upload-artifact y se
  descomprime igual); `skip-decompress` (no se usa); **`digest-mismatch` pasa a `error` por omisión**: si la huella de lo
  bajado no es la que anuncia el servidor, el paso falla. Más estricto a nuestro favor; solo se ve en el runner; un fallo ahí es
  un artefacto dañado, no algo que silenciar.
- **Artefactos de un job llamado:** `verificar` sube `<nombre>-<intento>`; `ejemplo-comprobado` y `rojo-comprobado` lo bajan
  en la misma corrida. Ninguna nota cambia el alcance (misma corrida, sin `run-id` ni token); ya funcionó en la 24.

### 2.2 Las dos ternas

| Acción | Última (S-MANT-1) | Mínima con node24 |
|---|---|---|
| `actions/checkout` | `3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1` | `fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09  # v5.1.0` |
| `actions/setup-python` | `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0  # v7.1.0` | `ece7cb06caefa5fff74198d8649806c4678c61a1  # v6.3.0` |
| `actions/upload-artifact` | `cf430e030ddbb5b0abf93d22962f4752f3646cd9  # v7.0.2` | `b7c566a772e6b6bfb58ed0dc250532a479d7789f  # v6.0.0` |
| `actions/download-artifact` | `9000827ccba6bdab643e8b6fd33ac0654aef8333  # v8.0.2` | `37930b1c2abaa49bbe596cd826c3c89aef350131  # v7.0.0` |

Forma exacta de cada línea, la que lee P-CI-17: `uses: actions/<nombre>@<40 hex>  # vX.Y.Z` (dos espacios antes de `#`).

### 2.3 Cómo se fijan (con red, una vez, el día de `M1`)

Como en §2.2 del diseño de la 24 (`ls-remote` de la etiqueta mayor, la etiqueta `vX.Y.Z` del mismo commit, cruce con
`git/ref/tags` y `commits/<sha>`), más el Node: `gh api repos/actions/<a>/contents/action.yml?ref=<sha> --jq .content | base64 -d
| grep 'using:'` tiene que dar `node24`, y va a `node` del JSON. Si `ls-remote` y API no cuadran, o `using` no es `node24`, o
la etiqueta mayor ya no apunta al sha de `MAYORES.txt`: se para y se pregunta a Jev (fijar el sha de `MAYORES.txt` o el de
hoy). `anterior` se copia de la 24. El campo `como` sigue en una sola línea y conserva el texto
`gh api repos/<accion>/git/ref/tags/<etiqueta>` (es la excepción de la higiene para ese fichero).

### 2.4 Qué prueba el ensayo y qué solo el runner

- **El ensayo** (sin cambios, S-MANT-8): con los YAML nuevos, la demo da los tres `INFORME.json` iguales a `CORRIDA-CI-1.json`
  (`--informes-como`); `ejemplo` y `ejemplo-propio` verdes con `ejemplo-comprobado`; `rojo` ROJO solo por «Veredicto» con
  `rojo-comprobado` verde. Prueba que el texto cambiado solo cambia los `uses:` y que los `path` por nombre y la raíz de los
  artefactos (lo que emula) siguen siendo lo que leen los comprobadores.
- **Solo en el runner:** que las acciones cargan en node24 y como ESM; que el aviso desaparece; 3.12 en Ubuntu 26; la huella
  de download v8; dónde deja el token checkout v6+ con `true` (`higiene.yml`); la raíz real de los artefactos; los minutos.

## 3. Los pushes y el pin

**`M1` (push 1).** Los 16 `uses:` con los sha nuevos: `verificador-conversor.yml` (4), `demo-ci.yml` (3), `higiene.yml` (2),
`ejemplo-ci.yml` (4, en `ejemplo-comprobado`), `rojo-ci.yml` (3, en `rojo-comprobado`). El pin del ejemplo **sigue en `C1`**.
Más: `ACCIONES-CI.json`, `github-mant/`, `prueba_ci.py` (§5), `traer_resultados_ci.py`, `anotaciones_ci.py`,
`sellar_prevision_mant.py` y el sello, la higiene, `CI.md`, los README, `MANIFIESTO.txt`. Corren `demo-ci`, `ejemplo-ci` e
`higiene`. Lo esperado: la demo igual a la 23 y sin aviso en sus seis jobs; `ejemplo-ci` igual a `CORRIDA-CI2-2.json`, **con el
aviso en `ejemplo / verificar` y `ejemplo-propio / verificar`** (llaman al flujo de `C1`, con las acciones viejas: se admite y
se declara) y sin aviso en `ejemplo-comprobado` (download v8 bajando lo que subió upload `v4.6.2`); la higiene verde y sin aviso.

Cómo se hace: una sustitución por acción sobre los cinco YAML, `sed -i 's|actions/<a>@<sha viejo>  # <etiqueta vieja>|actions/<a>@<sha
nuevo>  # <etiqueta nueva>|'`; `grep -c` de los sha nuevos en `.github/workflows/*.yml` tiene que dar 16 y el de los viejos, 0.
Las plantillas: copia de los cinco, y en `ejemplo-ci.yml` y `rojo-ci.yml` `sed "s/$C1/COMMIT_M1/g"`.

**`M2` (push 2).** Solo `ejemplo-ci.yml` y `rojo-ci.yml`, desde las plantillas: `sed "s/COMMIT_M1/$M1/g"` con `M1 = git
rev-parse` del push 1; y en `prueba_ci.py` la constante `M1` (§5). Corren `ejemplo-ci`, `demo-ci` e `higiene`. Lo esperado:
`ejemplo-ci` igual a `CORRIDA-CI2-2.json` y sin aviso en ningún job; la demo igual; la higiene verde. **A mano sobre `M2`:**
`rojo-ci`, igual a `CORRIDA-CI2-3.json` y sin aviso.

**`M3` (push 3).** `RESULTADO-MANT.md`, los `CORRIDA-MANT-*.json`, `AVISOS-MANT.json`, los README, `MANIFIESTO.txt`. Sus corridas
quedan en Actions (DV-CI2-15).

**La escalera, si una acción cambia un resultado y no se explica** (regla de parada): esa acción baja a su mayor mínima con
node24 (§2.2); si tampoco, a la de la 24 (su aviso se queda, declarado). Cada peldaño es un commit por la opción B y, si toca el
flujo, un `M1'` nuevo y volver a fijar. El tope de pushes es el de la previsión.

## 4. Lo que no cambia, y cómo se comprueba

| Control | Orden | Igual a | Lo que tiene que dar |
|---|---|---|---|
| demo en `M1`, `M2` | `traer_resultados_ci.py <run> <t> -o cv/ci/CORRIDA-MANT-1.json --igual-a cv/ci/CORRIDA-CI-1.json` (y `-2-demo`) | `verificador-{negativo,positivo,real}-1`: `e7c2e65d…`, `2f89fa13…`, `488ee643…` | seis jobs verdes; `igual_a_la_referencia` cierto en los tres; `COMPROBACION-*` ausentes (la demo no los sube) |
| ejemplo en `M1`, `M2` | `… -o cv/ci/CORRIDA-MANT-1-ejemplo.json --igual-a cv/ci/CORRIDA-CI2-2.json` (y `-2`) | `ejemplo-1` `c99e7ba3…` (349 casos), `ejemplo-propio-1` `7c1b37be…` (6), `ejemplo-comprobado-1` el mismo `COMPROBACION-EJEMPLO` (26 ciertas) | los tres verdes; `igual_a_la_referencia` cierto en los tres |
| rojo sobre `M2` | `… -o cv/ci/CORRIDA-MANT-3.json --igual-a cv/ci/CORRIDA-CI2-3.json` | `rojo-1` `30ddf4a7…`; `rojo-comprobado-1` el mismo `COMPROBACION-ROJO` (11 ciertas, 164 casos, `resultado_job` `failure`, salidas llegadas) | `rojo` rojo solo en «Veredicto», `rojo-comprobado` verde; `igual_a_la_referencia` cierto en los dos |
| aviso de Node.js 20 | `anotaciones_ci.py <runs> -o cv/ci/AVISOS-MANT.json --admitir "ejemplo / verificar" --admitir "ejemplo-propio / verificar" --control 41136715322` | la corrida de la 24 lleva el aviso | sale 0: ningún job sin admitir lleva el aviso, y el control sí |

**`traer_resultados_ci.py`,** el cambio exacto: en el bloque de `--igual-a`, quitar la condición `nombre.startswith("verificador-")`;
un artefacto con `informe_sha256` es igual si coincide con el de `<control>-1` de la referencia; uno `sin_veredicto`, si cada
objeto `COMPROBACION-*` es `==` al de la referencia; la clave pasa a `igual_a_la_referencia` y el JSON gana `"referencia":
<nombre del fichero>`; sale 1 si alguno es falso. Un nombre que no esté en la referencia se anota (`sin_referencia`) y no
decide. En la corrida roja, `conclusion` `failure` es lo esperado y no cuenta como fallo de la orden.

**`anotaciones_ci.py`** (`python3 cv/ci/anotaciones_ci.py <run_id>[,…] -o <json> [--admitir "<job>"]… [--control <run_id>]`):
por corrida, `gh run view <id> --repo … --json databaseId,headSha,workflowName,jobs`; por job, `gh api
repos/LK-Corporation/lab-integraciones/check-runs/<jobs[].databaseId>/annotations` (los mismos ids que `actions/runs/<run>/jobs`).
`PATRON = re.compile(r"Node\.js 20|node20", re.I)` sobre `message` y `title`. Escribe `{"formato": "avisos-ci/1", "patron": …,
"admitidos": […], "control": {"run_id", "jobs", "jobs_con_aviso", "mensaje": <el primero, 300 caracteres>}, "corridas": {<run_id>:
{"commit", "flujo", "jobs": {<nombre>: {"anotaciones": n, "node20": [mensajes], "aviso_node20": bool}}}}}`. Sale 1 si un job no
admitido lleva aviso o si el control no lleva ninguno (el patrón ya no casa con GitHub); 0 si no. La lógica (`avisos_de`,
`veredicto`) va separada de las llamadas a `gh`, para P-CI-30. Se corre al final con las siete corridas (`M1`: demo, ejemplo,
higiene; `M2`: las tres; el rojo), y antes las veces que haga falta. Antes de sellar, el control sobre `41136715322` tiene que
ver el aviso en sus tres jobs; si el texto real no casa, se ajusta el patrón **antes** del sello y se anota.

**Antes de cada push,** el ensayo de §2.4 en verde, con `--flujo ejemplo-ci` y `--flujo rojo-ci --rojo rojo`. En `M1` el `uses:`
remoto resuelve `C1` en la copia (`git show`): se ensaya el flujo viejo, que es lo que correrá; en `M2` resuelve `M1`.

## 5. Las pruebas en rojo

**Lo que cambia en las de la 24.** `plantillas_dir()` → `cv/ci/github-mant`. **P-CI-16** y **P-CI-17**: leen los YAML que corren
más `github-mant/*.yml`; P-CI-17 pasa en cuanto `ACCIONES-CI.json` y los 16 `uses:` llevan los sha nuevos; `LK_REMOTO` admite
`COMMIT_M1` además de `COMMIT_C1`. **P-CI-26**: `verificador-conversor.yml`, `demo-ci.yml` e `higiene.yml` que corren, byte a
byte iguales a `github-mant/`. **P-CI-27**: `ejemplo-ci.yml` y `rojo-ci.yml` que corren son las plantillas de `github-mant/` con
`COMMIT_M1` sustituido por `PIN_ESPERADO`, el mismo en los dos y distinto de `C0`; con `C1 = "5183b4ed…"`, `M1 = None` en `M1` y
`M1 = "<sha>"` en `M2`, `PIN_ESPERADO = M1 or C1`. Los cuatro controles de `comprobar_vivos` siguen. P-CI-20..23 leen las
plantillas nuevas sin cambiar.

| Prueba | Qué comprueba | Control negativo | Rojo antes de |
|---|---|---|---|
| P-CI-28 | `ACCIONES-CI.json`: por acción, `node == "node24"`; el número de `mayor` ≥ el mínimo con node24 (`checkout` 5, `setup-python` 6, `upload-artifact` 6, `download-artifact` 7); `etiqueta` empieza por `mayor + "."`; `sha != anterior.sha`; `anterior.sha` 40 hex; `api` contiene `sha`. Y las cinco huellas de `github-ci2/*.yml` son las de `SELLO-CI2.txt` | `node20` → lo ve; `download-artifact` con `mayor` `v6` → lo ve; `sha == anterior.sha` → lo ve; una copia de `github-ci2/demo-ci.yml` con un espacio más → lo ve | S-MANT-3, 4 |
| P-CI-29 | todo paso `actions/checkout@` de todo YAML (los que corren y `github-mant/`) lleva `persist-credentials: false`; con Q-MANT-D-2 (b), `higiene.yml` se exime por nombre | un paso sin la clave → lo ve | Q-MANT-D-2 |
| P-CI-30 | `anotaciones_ci.py` sin red: `avisos_de` sobre una lista sintética con un `message` «Node.js 20 actions are deprecated…» → 1 y el mensaje; sin él → 0; `veredicto`: un job con aviso no admitido → 1; admitido → 0; control sin aviso → 1 | `message` «Node.js 24» → 0 | S-MANT-7 |
| P-CI-31 | las entradas de cada acción en todo YAML son las revisadas en las notas: checkout ⊆ {`path`, `persist-credentials`, `repository`, `ref`, `fetch-depth`}; setup-python ⊆ {`python-version`}; upload-artifact ⊆ {`name`, `path`, `retention-days`, `if-no-files-found`}; download-artifact == {`name`, `path`} | `archive: false` → lo ve; `artifact-ids` → lo ve; `cache: pip` → lo ve | §2.1 |

**La higiene:** `JSON_ADMITIDOS` gana `verificador/cv/ci/AVISOS-MANT.json`, `PREVISION-MANT.json`, `prevision-cuerpo-mant.json`,
`preguntas_qmant.json`, `preguntas_prevision_mant.json`, `CORRIDA-MANT-1.json`, `CORRIDA-MANT-1-ejemplo.json`,
`CORRIDA-MANT-2.json`, `CORRIDA-MANT-2-demo.json`, `CORRIDA-MANT-3.json`. Todo `.md` y `.txt` nuevo, enlazado desde
`verificador/README.md`. `pytest tests -q` antes de cada commit.

## 6. La previsión que se sella

`cv/ci/prevision-cuerpo-mant.json` + `cv/ci/sellar_prevision_mant.py <cuerpo> <juez publicado>` → `PREVISION-MANT.json`,
`SELLO-MANT.txt` (se niega a pisarlo; no toca los sellos de la 23 ni la 24); `PREVISION-MANT.md` en prosa. `APARATO`:
`github-mant/*.yml` (5), `ACCIONES-CI.json`, `prueba_ci.py`, `ensayo_flujo.py`, `traer_resultados_ci.py`, `anotaciones_ci.py`,
`sellar_prevision_mant.py`, `decision-jev-prevision-mant.md`; `verificar_conversor.py` en `herramienta`. Sin los ficheros del
ejemplo (no cambian; sus huellas están en `SELLO-CI2.txt`). Jev da su previsión con estado neutro (`estado_prevision_mant.md`,
`preguntas_prevision_mant.json`: demo verde en `M1`; ejemplo verde en `M2`; rojo a la primera; sin aviso en todas; pushes
`tres` / `cuatro_o_cinco` / `seis_o_mas`), una vez, después del ensayo.

| Clave (`CLAVES_PREVISION_MANT`, obligatorias) | Valor que propone el diseñador |
|---|---|
| `etapa` | «25, el mantenimiento de la integración continua: previsión sellada antes del primer push» |
| `fecha`, `juez`, `herramienta` | los pone el sellador; juez `b3f00f6a…` |
| `acciones` | las cuatro `(etiqueta, sha, node)` fijadas: lo que se mide |
| `base_de_la_prevision` | las 31 pruebas en verde; el ensayo con los YAML nuevos; el control del aviso sobre la 24; lo no probado: las acciones en node24/ESM, la huella de download v8, 3.12 en Ubuntu 26 |
| `probabilidad_demo_verde_en_m1_a_la_primera` / `probabilidad_demo_informes_iguales` | 0,85 / 0,97 |
| `probabilidad_ejemplo_verde_en_m2_a_la_primera` / `probabilidad_rojo_a_la_primera` | 0,85 / 0,85 |
| `probabilidad_sin_aviso_node20` (todas las corridas desde `M1`, salvo los dos `verificar` admitidos de `M1`) | 0,9 |
| `probabilidad_todo_en_una_sesion` | 0,75 |
| `pushes_previstos`, `pushes_mas_probable` | `[3, 5]`, 3 |
| `minutos_por_corrida_previstos` | demo `[1, 2]`; ejemplo y rojo `[0.3, 1]` cada uno |
| `rojo_n_casos_previsto` | 164 |
| `causas_de_fallo_previstas` | (1) download v8: `digest-mismatch` o `Content-Type` en los comprobados; (2) una acción ESM que no carga; (3) setup-python v7 sin 3.12 en Ubuntu 26; (4) el patrón del aviso no casa (lo ve el control antes del sello); (5) el sha de `M1` mal copiado en `M2` (P-CI-27 lo ve antes del push); (6) la higiene con los JSON nuevos; (7) `higiene.yml` con `persist-credentials: false` y `fetch-depth: 0` (si Q-MANT-D-2 es (a)) |
| `diferencias_que_se_explicarian` | ninguna: las acciones no tocan lo que produce `INFORME.json`; una diferencia es un fallo del aparato o de la acción, y entra en la escalera |
| `regla_de_parada` | la del ANTES, copiada |
| `jev` | su previsión con estado neutro, al lado |

## 7. Las preguntas para Jev (Q-MANT-D)

Con estado neutro (`cv/ci/estado_qmant.md`, `cv/ci/preguntas_qmant.json` → `decision-jev-qmant.md`; `decisiones-qmant.md`), sin
la recomendación. Lo que el ANTES ya decide (node24, por commit y cruzado, dos pushes, sin Dependabot) no se pregunta.

| Q | Pregunta | Opciones |
|---|---|---|
| Q-MANT-D-1 | Qué mayor se fija de cada acción | (a) la mínima con node24: checkout `v5.1.0`, setup-python `v6.3.0`, upload `v6.0.0`, download `v7.0.0`; (b) la última: `v7.0.1`, `v7.1.0`, `v7.0.2`, `v8.0.2`; (c) la última salvo download-artifact en `v7.0.0`, sin la huella forzada |
| Q-MANT-D-2 | `higiene.yml`, el único checkout sin `persist-credentials: false` | (a) se añade la línea en `M1`, y P-CI-29 cubre los ocho checkouts; (b) solo cambia su sha; con v6+ el token va a un fichero aparte y se declara |
| Q-MANT-D-3 | El evento `pull_request` con las acciones nuevas | (a) no se recorre: `M3` va a `main` y se declara; (b) la rama del resultado como PR llevado a `main` por avance rápido, como en la 24: un push y dos corridas más |

**Recomendación del diseñador, aparte:** D-1 (b): cada novedad de las notas se ha contrastado con las entradas que estos flujos
usan y ninguna las toca, salvo la huella forzada de download v8, más estricta a nuestro favor; la mínima deja dos mayores de
deuda para otra etapa igual, y la escalera de §3 ya baja a (a) acción por acción si algo no se explica. D-2 (a): una línea, guarda
estática, y nada que declarar sobre un token que nadie usa. D-3 (a): ninguna nota toca ese evento en estos flujos, y la etapa es
de mantenimiento. Si Jev elige otra: D-1 (a) o (c) cambian los sha de §2.2 y nada más; D-2 (b) exime `higiene.yml` en P-CI-29 y
añade L-MANT-7; D-3 (b) añade al plan la rama y el PR de §6 de la 24, con `CORRIDA-MANT-4.json`.

## 8. Los límites (L-MANT-n)

- **L-MANT-1.** El ensayo no corre el código de las acciones: lo que cambia una versión solo se ve en el runner (§2.4).
- **L-MANT-2.** Los sha vuelven a envejecer desde el día del push; el siguiente aviso de GitHub es otra etapa como esta
  (nada de Dependabot, por el ANTES).
- **L-MANT-3.** «Sin aviso» es un patrón sobre el texto de GitHub, anclado al control de la 24; si GitHub cambia el texto después,
  el patrón deja de verlo.
- **L-MANT-4.** En `M1`, `ejemplo-ci` llama al flujo de `C1` con las acciones viejas: sus dos `verificar` llevan el aviso; es lo que
  le pasa a cualquier tercero hasta que sube el pin.
- **L-MANT-5.** `ubuntu-latest` ya es Ubuntu 26 desde la 24; no se controla aparte.
- **L-MANT-6.** El evento `pull_request` con las acciones nuevas queda sin recorrer (Q-MANT-D-3 (a)).
- **L-MANT-7.** Solo con Q-MANT-D-2 (b): el token de `higiene.yml` se persiste en un fichero aparte y nadie lo usa.
- **L-MANT-8.** La huella forzada de download v8 solo se ejercita en su camino bueno; que falle ante un artefacto dañado no se prueba.

## 9. El plan

Tope: una sesión. Cada push por la opción B (guarda LIMPIO, higiene, revisión a ciegas, Jev).

| Paso | Qué | Hecho cuando | Si falla |
|---|---|---|---|
| 0 | Q-MANT-D-1..3 a Jev; `verificador/ANTES-ETAPA-MANT.md` copiado; encargo y diseño en `cv/ci/` | decididas | — |
| 1 | Con red, una vez: los sha cruzados y el `node` (§2.3) → `ACCIONES-CI.json` | las cuatro cuadran, `node24` | parar y preguntar a Jev |
| 2 | `prueba_ci.py` en rojo: P-CI-28..31 fallan por lo previsto; P-CI-16/17/26/27 fallan al apuntar a `github-mant/` inexistente; commit | cada una MAL por lo previsto | — |
| 3 | Los 16 `uses:` (§3), `higiene.yml` (Q-2), `github-mant/`, `traer_resultados_ci.py`, `anotaciones_ci.py`, `sellar_prevision_mant.py`, higiene, `CI.md`, README; `prueba_ci.py`, `prueba_vc.py`, `pytest` verdes; `MANIFIESTO.txt` | todo verde; el manifiesto atestigua S-MANT-10 | — |
| 4 | El ensayo (§2.4) con los tres flujos; `anotaciones_ci.py --control 41136715322` ve el aviso | verde, rojo donde toca, informes iguales; control cierto | arreglar antes de sellar |
| 5 | Previsión sellada (§6): cuerpo, Jev al lado, sello; commit | `SELLO-MANT.txt` en HEAD | no hay push |
| 6 | **Push `M1`** por la opción B. Se leen `demo-ci` → `CORRIDA-MANT-1.json`, `ejemplo-ci` → `CORRIDA-MANT-1-ejemplo.json`, `higiene`; anotaciones | §4: iguales; sin aviso salvo los dos `verificar` | la escalera de §3; si no se explica, regla de parada |
| 7 | `M1 = rev-parse`; P-CI-27 en rojo con la constante puesta; `sed COMMIT_M1`; P-CI-27 verde; ensayo de `ejemplo-ci` y `rojo-ci` con el pin nuevo; **push `M2`** por la opción B. Se leen `ejemplo-ci` → `CORRIDA-MANT-2.json`, `demo-ci` → `CORRIDA-MANT-2-demo.json`, `higiene` | iguales; sin aviso en ningún job | un arreglo del flujo es un `M1'` y volver a fijar |
| 8 | **`rojo-ci` a mano** sobre `M2` → `CORRIDA-MANT-3.json` | `rojo` rojo solo por «Veredicto», `rojo-comprobado` verde, igual a la 24, sin aviso | repetir a mano tras el arreglo; regla de parada si no se explica |
| 9 | `AVISOS-MANT.json` con las siete corridas y el control; `RESULTADO-MANT.md`; README; `MANIFIESTO.txt`; **push `M3`** por la opción B | publicado; sus corridas en Actions | — |

**Lo que el plan no permite:** tocar lo de S-MANT-10; un `uses:` de acción con un sha que no esté en `ACCIONES-CI.json`; una
entrada de acción fuera de P-CI-31; el pin del ejemplo en `M2` distinto de `M1`; un push sin `SELLO-MANT.txt` en un commit
anterior; `permissions` que no sea `contents: read`; un run en rojo fuera de `workflow_dispatch`.

## 10. Los documentos

- **`cv/ci/CI.md`:** la viñeta de «Lo que no hace» sobre las acciones: fijadas el 31-oct a versiones en Node.js 24
  (`ACCIONES-CI.json`, con la anterior al lado); las plantillas, las de `github-mant/`; el pin del ejemplo se subió en la 25 en
  dos pushes; «regenera la base» precisa «si cambia el juez».
- **`ejemplo-ci/README.md`:** sus dos enlaces a plantillas pasan a `github-mant/`; `SELLO-CI2.txt` deja de verificarlo (como
  DV-CI2-7; se dice en `decisiones-qmant.md`).
- **`verificador/README.md`:** sección «El mantenimiento de la integración continua (25, 31-oct-2026)» con la frase y la tabla
  de la 24 adaptada. **`README.md`:** un párrafo tras el de la 24 y el enlace a `verificador/RESULTADO-MANT.md`.
- **`verificador/RESULTADO-MANT.md`:** la frase del ANTES (o la negativa); la pregunta; «Las versiones» (antes/después con
  `node` y lo que las notas cambiaban); «Lo que no cambia» (la tabla de §4 con lo que dio); «El aviso» (por corrida y job, con
  el control); «Lo que cuesta»; «La previsión, frente a lo que salió» (con Jev); «Lo que no dice» (L-MANT-1..8); «Cómo
  repetirlo» (`ls-remote | grep <sha>` por acción, `anotaciones_ci.py`); «Los documentos de la etapa».
