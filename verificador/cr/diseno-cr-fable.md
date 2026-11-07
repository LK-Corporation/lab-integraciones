# Diseño a ciegas de la etapa 35: cerrar el círculo del ensayo

Diseño para la pregunta fijada en `ANTES-ETAPA-CIRCULO.md`: después del push, comprobar que el árbol publicado es el que se
ensayó, de forma que la comprobación caiga cuando no lo es y pase cuando lo es. Diseña Fable, a ciegas: ha leído el ANTES,
`cv/ci/ensayo_flujo.py` (lo que escribe en `ENSAYO.json`), las `P-EN-n` de `cv/ci/prueba_ci.py`, la sección del ensayo de
`cv/ci/CI.md`, el diseño de la etapa 34 (`en/diseno-en-fable.md`) y su guion de controles (`en/controles_en.sh`), los cinco
flujos de `.github/workflows/` y el `git log` del clon público; y ha probado el comportamiento de git en repositorios suyos,
con un repositorio vacío (`git init --bare`) haciendo de remoto. No ha leído ningún resultado ni ninguna nota de la etapa 34
aparte de lo que el ANTES cuenta. Las decisiones abiertas van numeradas `Q-CR-n` para Jev; la recomendación va aparte, al
final de cada una.

Rutas: relativas a la raíz del repositorio público (`.github/workflows/`, `verificador/`, `ejemplo-ci/`) o a `verificador/`
(`cv/ci/…`, `cr/…`). «El clon» es la copia del repositorio público desde la que se ensaya y se hace el push; «la carpeta de
trabajo» de un ensayo es su segundo argumento, fuera del clon, y es donde queda su `ENSAYO.json`.

## 0. Lo comprobado antes de diseñar

- **Lo que el ensayo deja en `ENSAYO.json["clon"]`** (`estado_del_clon`): `git` (true/false), `head` (el commit HEAD),
  `arbol` (el árbol del índice, por `write-tree` sobre una copia del índice), `publicado` (`head` si `arbol ==
  HEAD^{tree}`, si no `arbol`), `tipo` (`commit` o `arbol`), `indice_distinto`, `sin_add`, `sin_seguimiento`, y `sha`
  (lo que valió `github.sha`). **`arbol` está siempre que hay `.git` y el ensayo llegó a correr**, sea `tipo` `commit` o
  `arbol`: es el dato que cierra el círculo. Sin `.git`, `clon` es `{"git": false, "sha": "e0"×20}` y no dice qué árbol se
  ensayó. Con el código 2 hay `no_ensayado` y `jobs == {}`. Las seis claves de siempre (`flujo`, `jobs`, `esperado_rojo`,
  `como_se_esperaba`, `informes_iguales`, `needs`) siguen ahí: `flujo` dice qué flujo se ensayó y `como_se_esperaba` si
  cada job dio lo que se esperaba.
- **Lo que un commit publica** es su árbol (`git rev-parse <commit>^{tree}`). El ensayo y el commit salen del mismo índice:
  si nada toca el índice entre el ensayo y el `git commit`, `write-tree` y el commit dan el mismo id de árbol (es el mismo
  cálculo sobre el mismo índice). Es la razón de que la comparación sea de árboles y no de commits.
- **Git, probado en repositorios míos** (git 2.43, el de la máquina del laboratorio):
  - ensayo sobre el índice, `commit`, `push`: el árbol del commit publicado es byte a byte el `arbol` del ensayo;
  - un `git add` de más después del ensayo: otro árbol; el árbol ensayado **sigue en el clon** como objeto colgante
    (`git cat-file -t <arbol>` → `tree`), así que `git diff --stat <arbol ensayado> <arbol publicado>` da la lista de rutas
    (`OTRO | 1 +`). El clon público lleva hoy cuatro árboles colgantes, los de los ensayos de la etapa 34: `gc` los quita
    pasadas dos semanas (`gc.pruneExpire`), no antes;
  - `commit --amend` con cambio de árbol: otro árbol y otro commit; el commit ensayado sigue en el clon y **no está en el
    remoto**; `diff --stat` entre los dos árboles da la ruta;
  - `commit --amend` solo del mensaje (`--no-edit` o `--trailer`): otro commit, **el mismo árbol**;
  - push de varios commits: `git rev-list <antes>..<después>` los cuenta; GitHub corre el flujo sobre la cabeza;
  - `git ls-remote <remoto> refs/heads/<rama>` da el commit que el remoto tiene, sin escribir nada; con un remoto local
    cuesta 8 ms. Un commit que otro empujó no está en el clon hasta `git fetch`;
  - `git merge-tree --write-tree <base> <rama>` (2.38+) da el árbol que tendría la fusión: igual al de la rama si la base no
    avanzó, y otro si avanzó;
  - un árbol que no existe en el clon (ensayo hecho en otra copia con otro contenido) da `fatal: could not get object info`;
    si la otra copia tenía el mismo contenido, el id es el mismo y el objeto existe;
  - `git commit --trailer "Ensayado: <árbol>"` y `git interpret-trailers --parse` funcionan (por si Jev elige el testigo de
    GitHub, Q-CR-1 b).
- **Los PR del repositorio** (`917ff18`, etapa 24; `b4009b7`, etapa 25) son commits de un solo padre con un árbol distinto
  del padre: se fusionaron por *squash*, no con commit de fusión. El árbol de un *squash* es el de la fusión: igual al de
  la rama si `main` no avanzó entre medias.
- **Los flujos:** `demo-ci.yml` y `ejemplo-ci.yml` corren en `push` a `main` con filtros `paths:` (`verificador/**`,
  `.github/workflows/**`, `tests/**`; y `ejemplo-ci/**`, `.github/workflows/**`, `verificador/**`) y en `pull_request`;
  `rojo-ci.yml` solo a mano; `higiene.yml` en todo push y PR; el job `pruebas` de la demo corre `cv/ci/prueba_ci.py` sin
  Docker ni red. Nada en los flujos sabe del ensayo. No cambian.
- **Las pruebas:** `prueba_ci.py` ya monta repositorios de git mínimos (`repo_minimo`, con `GIT_C` para no depender de la
  configuración global), carga el ensayo con `importlib` (`cargar_ensayo`) y lo corre sobre el flujo `mini` capturando la
  salida (`ensayar`); `main` etiqueta `P-EN-n` o `P-CI-n` por el prefijo del nombre.
- **Los controles de la etapa 34** (`en/controles_en.sh`) ensayan cada flujo con la misma orden que el laboratorio usa antes
  de un push: demo `pruebas,negativo,positivo --flujo demo-ci`; ejemplo `ejemplo,ejemplo-propio --flujo ejemplo-ci`; rojo
  `rojo --flujo rojo-ci --rojo rojo`; cada uno con su carpeta de trabajo, que se mueve a `res/<estado>/<flujo>/`. Así que
  un push lleva **tres `ENSAYO.json`**, uno por flujo, en tres carpetas. Lo que costó cada ensayo no lo he leído.
- **Lo que no he podido mirar:** `verificador/README.md` (la etapa 34 tocó dos frases suyas sobre el ensayo); el coste en
  minutos de los tres ensayos; `ls-remote` contra GitHub (contra un remoto local, 8 ms; contra GitHub será del orden de un
  segundo, no medido); qué leen de `ENSAYO.json` los `sellar_prevision_*.py` (la comprobación no lo modifica, así que no les
  afecta).

## 1. Dónde vive la comprobación y cuándo corre

**Una orden local, después del push, en el clon desde el que se hizo:**

```
python3 cv/ci/comprobar_publicado.py <clon> <ENSAYO.json> [<ENSAYO.json> …] [--remoto origin] [--rama main]
        [--flujos demo-ci,ejemplo-ci,rojo-ci] [--base <rama>] [-o <carpeta>]
```

- **Lo ensayado le llega por los `ENSAYO.json`** de las carpetas de trabajo de los ensayos del push (uno por flujo). No va
  nada en el commit ni en su mensaje: el árbol de un commit no puede contener su propio id, y el mensaje solo podría llevar
  una afirmación (Q-CR-1 b).
- **Lo publicado lo lee del remoto:** `git ls-remote <remoto> refs/heads/<rama>` da el commit que el remoto tiene ahora; si
  el objeto no está en el clon (lo empujó otro), `git fetch <remoto> <rama>` lo trae. Solo lectura del remoto; ningún
  permiso nuevo. Después, todo es local: `git rev-parse <commit>^{tree}`.
- **Qué se compara:** el árbol del commit publicado con `clon.arbol` de cada `ENSAYO.json`. Iguales, pasa; distintos, cae.
  El commit no cuenta (`clon.head` y `clon.publicado` solo se usan para decir si además es el mismo commit o uno nuevo sobre
  el mismo árbol).
- **Cuándo:** justo después de cada `git push`, con los tres `ENSAYO.json` de ese push; y, con `--local` si Jev lo quiere
  (Q-CR-5), también antes del push sobre el HEAD del clon, sin red.
- **Qué deja:** las líneas de abajo y `PUBLICADO.json` en `-o` (fuera del clon), que es lo que el resultado de la etapa
  cita.

Un trabajo en GitHub no puede ver `ENSAYO.json`. Lo único que podría ver es una afirmación escrita en el commit (un
*trailer* en el mensaje) y compararla con el árbol que tiene delante; va como opción en Q-CR-1 (b), con su coste.

## 2. Qué hace en cada caso

Con las recomendaciones de §3 (estricto; los tres flujos; un ensayo en rojo cae). «Pasa» es código 0 y la última línea
«círculo cerrado»; «cae» es código 1 y «CÍRCULO ABIERTO: …» con el porqué; «avisa» es una línea `aviso:` sin cambiar el
código.

| Caso | Qué ve la comprobación | Pasa / cae / avisa | Por qué |
|---|---|---|---|
| **Publicado igual que lo ensayado** (ensayo sobre el índice, `commit`, `push`; o ensayo sobre el HEAD y `push`) | `clon.arbol == <publicado>^{tree}` en los tres `ENSAYO.json` | **pasa.** Línea por flujo: «demo-ci: ensayo sobre el árbol del índice `160eb33a95a0` (HEAD `74a6a99a3ba4`): el mismo árbol; el commit `464bbb2eb4e4` es nuevo sobre él» (o «es el mismo commit» si `clon.tipo == commit` y `clon.head` es el publicado) | el árbol es lo que corre en el runner; que el commit sea nuevo es lo normal cuando se ensaya antes de hacerlo |
| **Un `git add` de más después del ensayo** | el árbol publicado tiene una ruta más (o distinta); el árbol ensayado existe en el clon | **cae:** «demo-ci: ensayo sobre el árbol `f8f2a3299492`; publicado el árbol `63ed84922f2c`: 1 ruta difiere (A `cr/DE-MAS.txt`)»; propone la orden para re-ensayar | lo que se ensayó no es lo que corre |
| **Un `commit --amend` después del ensayo** que cambia el árbol | otro árbol; si el ensayo fue `tipo commit`, además «el commit ensayado `f13b70faab36` ya no está en `main`» | **cae,** con la ruta que difiere (`M verificador/…`) y esa frase | lo mismo; la frase distingue el amend de un add |
| `commit --amend` que solo cambia el mensaje | el mismo árbol, otro commit | **pasa,** con «el commit es nuevo sobre el mismo árbol» | el runner corre el árbol, no el mensaje |
| **Un ensayo sobre otra copia** con otro contenido | `clon.arbol` no es el árbol publicado y **no existe en el clon** (`cat-file` falla) | **cae:** «el árbol ensayado `…` no es el publicado `…` y no está en este clon: se ensayó en otra copia o ya se purgó; no se puede listar la diferencia» | no es lo publicado; sin el objeto no hay `diff`, y se dice |
| Un ensayo sobre otra copia **con el mismo contenido** | el id del árbol es el mismo y el objeto existe | **pasa** | el árbol es el contenido; de qué copia salió no cambia lo que corre. Se avisa si el commit publicado no desciende de `clon.head` («otra historia») |
| **Ningún ensayo** (no se da `ENSAYO.json` de un flujo, o el fichero no existe) | falta el flujo en la lista `--flujos` | **cae:** «no hay ensayo de ejemplo-ci» | sin ensayo no hay círculo que cerrar |
| Un `ENSAYO.json` con `no_ensayado` (el ensayo paró con 2), o sin `clon` (anterior a la etapa 34), o con `clon.git == false` (una exportación sin `.git`) | no dice qué árbol ensayó | **cae:** «demo-ci: el ensayo no ensayó nada (…)» / «no dice qué árbol ensayó: ensayo anterior a la etapa 34 o sobre una carpeta sin .git» | no hay árbol con el que comparar; se dice cuál es el caso |
| Un `ENSAYO.json` en rojo (`como_se_esperaba` o `informes_iguales` con algún falso) sobre el árbol publicado | el árbol coincide, el ensayo no dio lo esperado | **cae** (Q-CR-4 a): «rojo-ci: el ensayo salió en rojo (rojo-comprobado)» | se publicó algo que el ensayo no aprobó; el círculo no es solo el árbol |
| **La demo ensayada sobre el árbol publicado y el ejemplo (y el rojo) sobre otro anterior** (el caso de la etapa 34) | demo igual; ejemplo y rojo distintos, con las rutas (textos de `verificador/`) | **cae** (Q-CR-3 a), nombrando los dos flujos y las rutas que difieren en cada uno | el ejemplo también corre en GitHub con ese push (`verificador/**` está en sus `paths:`), sobre un árbol que no se ensayó. Con Q-CR-3 (b) tampoco pasaría: las rutas distintas caen dentro de `verificador/**` |
| **Un push de varios commits** | la cabeza es el árbol ensayado; `git rev-list clon.head..<publicado>` da más de uno | **pasa, y avisa:** «3 commits nuevos desde el HEAD del ensayo; solo la cabeza está ensayada, que es lo que GitHub corre» | el runner corre la cabeza; los intermedios no corren en ningún sitio |
| Un push de varios commits en que la cabeza **no** es el árbol ensayado (el ensayo fue de un commit intermedio) | distinto | **cae,** con las rutas | lo que corre no se ensayó |
| **Un PR:** push de la rama (`--rama <rama>`), antes de fusionar | el árbol de la rama frente a los ensayos; con `--base main`, además `git merge-tree --write-tree <remoto>/main <publicado>` | **pasa o cae por la rama como en un push.** Con `--base`: si el árbol de la fusión es el ensayado, lo dice; si no (`main` avanzó), **avisa:** «el commit de fusión del PR tendría el árbol `…`, que no está ensayado: las corridas de `pull_request` corren sobre él» | el ensayo no ve el commit de fusión (lo dice la guía); la comprobación lo predice con `merge-tree`, que es lo más que se puede hacer sin GitHub |
| Un PR fusionado por *squash* en `main` (como los dos del repositorio) | `--rama main` después de fusionar: el árbol del *squash* es el de la rama si `main` no avanzó | **pasa** con los mismos `ENSAYO.json` de la rama; si `main` avanzó, **cae** (otro árbol) y hay que ensayar la fusión | es un push más a `main` |
| El remoto tiene otra cosa (otro empujó, o el push no llegó) | el árbol publicado no es ninguno de los ensayados | **cae** (si el contenido difiere) o **pasa** con el aviso de «otra historia» | se compara con lo que el remoto tiene, no con lo que el clon cree haber empujado |
| El remoto no responde, la rama no existe, un `ENSAYO.json` no es JSON | no se puede leer un lado | **código 2:** «no se pudo comprobar: …» | ni cerrado ni abierto: no se sabe |

## 3. Decisiones abiertas (para Jev)

**Q-CR-1. Dónde vive la comprobación.**
- (a) Una orden local después del push (§1), y nada en GitHub. Implica: ve `ENSAYO.json` y puede listar la diferencia; los
  flujos no cambian (condición 5 por construcción); corre solo si se corre; su registro es local (`PUBLICADO.json`) y lo
  publica el resultado de la etapa.
- (b) La orden local más un testigo en GitHub: la orden, en modo `--local` antes del commit, imprime una línea
  `Ensayado: <árbol>` que se pone como *trailer* del mensaje del commit (`git commit --trailer`); un flujo nuevo
  `.github/workflows/circulo.yml` (`push` a `main` y `pull_request`, `permissions: contents: read`, sin secretos) lee con
  `git interpret-trailers --parse` el mensaje del commit (`github.sha` en push; `github.event.pull_request.head.sha` en PR,
  por `env:`, nunca dentro de un `run:`) y lo compara con `git rev-parse <commit>^{tree}`. Implica: GitHub cae si el
  *trailer* no es el árbol (add o amend después de escribirlo); con un commit sin *trailer* (un tercero, un fork, un PR
  ajeno) solo puede avisar, no caer, salvo que se limite a `github.repository == 'LK-Corporation/lab-integraciones'`; un
  ensayo `tipo commit` obliga a un amend de mensaje para poner el *trailer*; el *trailer* es una afirmación escrita por la
  orden, no una comprobación (GitHub no ve `ENSAYO.json`), y no se firma (fuera de la etapa); el flujo nuevo no se ensaya
  con `ensayo_flujo.py` (el checkout emulado no tiene `.git` ni mensaje) y se prueba por su guion con `P-CR`; un flujo
  más que mantener y que puede ponerse en rojo por su cuenta.
- (c) Solo el testigo de GitHub, sin orden local. Implica: nada compara con `ENSAYO.json`; el *trailer* se escribe a mano
  o por la orden, y «ningún ensayo» es indistinguible de «sin *trailer*»; el control con un remoto local no se puede hacer.
Recomendación: (a). Es lo que la pregunta del ANTES pide (después del push, con lo que se ensayó), cabe en una sesión y no
toca ningún flujo. (b) añade un segundo lector público, que es valioso, pero su «cae» depende de que el *trailer* se haya
escrito, y la etapa deja fuera firmar afirmaciones; si Jev lo quiere, que sea con la limitación al repositorio propio y como
flujo aparte, para que un rojo suyo no toque la demo.

**Q-CR-2. Qué flujos tienen que estar ensayados para que pase.**
- (a) Siempre los tres: `demo-ci`, `ejemplo-ci` y `rojo-ci` (`--flujos`, con ese valor por omisión). Implica: un push sin
  ensayo del rojo cae aunque el rojo solo corra a mano; es lo que el laboratorio ya ensaya en cada push (los controles de
  la 34 lo hacen así); ninguna lógica de rutas.
- (b) Los que GitHub dispararía con el push: los flujos con `on.push.paths` cuyo filtro casa con `git diff --name-only
  clon.head..<publicado>`; `rojo-ci` (sin `push`) como aviso si falta. Implica: emular los `paths:` de GitHub (`**`, `*`,
  negaciones), con sus pruebas; un error ahí es un verde falso; un push que solo toca `README.md` no exige ningún ensayo.
- (c) Los que se den, con un aviso por cada uno de los tres que falte. Implica: «ningún ensayo» no cae nunca; solo avisa.
Recomendación: (a). Es mecánico y es lo que ya se hace; (b) mete la emulación de `paths:` justo donde un fallo no se ve.

**Q-CR-3. Un ensayo sobre un árbol distinto del publicado.**
- (a) Cae siempre, con las rutas que difieren (hasta 20 y «… y K más») y la orden para re-ensayar ese flujo. Implica: un
  cambio de un texto después del ensayo obliga a re-ensayar los tres flujos (lo que cuestan); ninguna regla sobre qué
  rutas «no importan».
- (b) Pasa con aviso si todas las rutas distintas quedan fuera de `on.push.paths` del flujo (leídos del árbol publicado);
  cae si alguna cae dentro. Implica: la misma emulación de `paths:` que Q-CR-2 (b); en el caso de la etapa 34 habría caído
  igual (los textos estaban en `verificador/`).
Recomendación: (a). La etapa nace de dar por «solo textos» una diferencia que nadie comprobó; la regla estricta es la
única que no exige juicio. Lo que cuesta es el precio de la pregunta del ANTES.

**Q-CR-4. Un `ENSAYO.json` en rojo** (`como_se_esperaba` o `informes_iguales` con algún falso) **sobre el árbol
publicado.**
- (a) Cae: «el ensayo salió en rojo (jobs …)». Implica: el círculo exige ensayo verde, no solo el mismo árbol; cuesta una
  comprobación de dos claves.
- (b) Solo compara árboles, y avisa. Implica: el círculo es estrictamente «el mismo árbol»; publicar sobre un ensayo rojo
  pasa con una línea de aviso.
Recomendación: (a).

**Q-CR-5. La comprobación antes del push.**
- (a) Solo después del push, como fija el ANTES. Implica: un modo, una red de seguridad que detecta pero no evita.
- (b) El mismo guion admite `--local`: compara `HEAD^{tree}` del clon con los `ENSAYO.json`, sin red, para correrlo justo
  antes de `git push`; el «después» sigue siendo obligatorio porque solo el remoto dice qué se publicó. Implica: una opción,
  una rama en el código (de dónde sale el commit) y una prueba más; evita el push malo en vez de solo verlo; con Q-CR-1 (b)
  es el modo que imprime el *trailer*.
Recomendación: (b). Cuesta una opción y previene lo que el «después» solo señala; la medida de la etapa sigue siendo la de
después.

**Q-CR-6. Dónde queda el registro del caso real** (el push de la etapa).
- (a) Un segundo commit, «el resultado del push de la etapa 35», con `cr/PUBLICADO-PUSH.json` (la salida de la
  comprobación sobre el primer push) y la línea en `RESULTADO-CIRCULO.md`; el segundo push se ensaya y se comprueba igual,
  y su registro queda local (o en la etapa siguiente). Implica: dos pushes, como en las etapas 23, 24 y 25; tres ensayos
  más para un commit de un JSON.
- (b) Un solo push; el registro se guarda fuera del repositorio público y el resultado lo cita por su contenido (el commit
  y el árbol) sin publicar el fichero. Implica: la frase del «hecho cuando» se apoya en algo que no está en el repositorio.
Recomendación: (a), por la costumbre de la casa y porque el registro es pequeño.

**Q-CR-7. Qué jobs tiene que haber ensayado cada flujo.**
- (a) Cualquiera: basta con que `jobs` no esté vacío. Implica: un ensayo de solo `pruebas` de la demo cierra el círculo de
  la demo.
- (b) Una lista mínima por flujo, fija en el guion: demo `pruebas, negativo, positivo, positivo-comprobado`; ejemplo
  `ejemplo, ejemplo-propio, ejemplo-comprobado`; rojo `rojo, rojo-comprobado`. Falta alguno, cae: «demo-ci: el ensayo no
  corrió negativo». `real` no entra (necesita red y no se ensaya). Implica: una tabla de tres entradas que hay que tocar si
  cambian los jobs; un ensayo a medias no cierra el círculo.
Recomendación: (b); la tabla cabe en tres líneas y es lo que los controles de la 34 ya corrían.

## 4. El cambio en el código

Con las recomendaciones (a)/(a)/(a)/(a)/(b)/(a)/(b). Si Jev decide otra cosa, cambia lo indicado en cada función.

**`cv/ci/comprobar_publicado.py` (nuevo).** Sin dependencias fuera de la biblioteca estándar y `git`. Funciones:

- `git(repo, *args)`: `subprocess.run(["git", "-C", repo, …], capture_output=True)`, como en el ensayo.
- `leer_ensayo(ruta)` → `{"flujo", "arbol", "head", "tipo", "git", "no_ensayado", "jobs", "verde"}` o un motivo de
  caída. `verde = all(como_se_esperaba.values()) and all(informes_iguales.values()) and jobs`. Devuelve `None` y el motivo
  si el fichero no existe (`no hay ensayo`), si no es JSON (código 2), si tiene `no_ensayado`, si no tiene `clon`, o si
  `clon.git` es falso.
- `publicado(repo, remoto, rama)` → `(commit, arbol)`: `git ls-remote <remoto> refs/heads/<rama>` (si falla o no da una
  línea, código 2: «no se pudo leer <remoto> <rama>: …»); si `git cat-file -e <commit>^{commit}` falla, `git fetch <remoto>
  <rama>` y se repite (si sigue faltando, código 2); `git rev-parse <commit>^{tree}`. Con `--local`: `git rev-parse
  HEAD` y `HEAD^{tree}` del clon, sin tocar el remoto.
- `diferencia(repo, arbol_ensayado, arbol_publicado)` → lista de `"<estado>\t<ruta>"` de `git diff --name-status
  <a> <b>` si `git cat-file -e <a>` existe; si no, `None` («no está en este clon»).
- `comparar(repo, ens, commit, arbol)` → `{"flujo", "igual", "mismo_commit", "diferencia", "motivo", "commits_nuevos",
  "otra_historia"}`: `igual = ens["arbol"] == arbol`; `mismo_commit = ens["tipo"] == "commit" and ens["head"] == commit`;
  `commits_nuevos = len(git rev-list ens.head..commit)` y `otra_historia = not merge-base --is-ancestor ens.head commit`;
  si `ens["tipo"] == "commit"` y no `is-ancestor ens.head commit`, el motivo añade «el commit ensayado … ya no está en
  <rama>» (un amend).
- `fusion(repo, remoto, base, commit)` (solo con `--base`): `git merge-tree --write-tree <remoto>/<base> <commit>` (tras
  `git fetch <remoto> <base>`); devuelve el árbol o `None` si hay conflicto (aviso).
- `main(argv)`: lee los argumentos; `publicado(...)`; por cada flujo de `--flujos`, busca el `ENSAYO.json` cuyo `flujo` es
  ese (si hay dos del mismo flujo, código 2: «dos ensayos de demo-ci»; si ninguno, cae); comprueba los jobs mínimos del
  flujo (la tabla `JOBS_MINIMOS` de Q-CR-7 b; `--jobs-minimos <flujo>=<job>,<job>` la sustituye para un flujo, que es lo
  que usan las pruebas con `mini`); `comparar`; imprime una línea por flujo; con `--base`, la predicción de la fusión;
  escribe `<-o>/PUBLICADO.json`; imprime la última línea; devuelve el código.

**Lo que imprime,** en el orden en que lo decide:

```
== lo publicado: origin refs/heads/main → commit 464bbb2eb4e4, árbol 160eb33a95a0 (el clon está en el mismo commit)
   demo-ci:    ensayo sobre el árbol del índice 160eb33a95a0 (HEAD 74a6a99a3ba4), 4 jobs verdes: el mismo árbol; el commit es nuevo sobre él
   ejemplo-ci: ensayo sobre el commit 74a6a99a3ba4 (árbol 0678cbf0a1b2), 3 jobs verdes: OTRO ÁRBOL: 3 rutas difieren
               (M verificador/RESULTADO-ENSAYO.md, M verificador/README.md, A verificador/en/…); re-ensaya:
               python3 cv/ci/ensayo_flujo.py <clon> <carpeta vacía> ejemplo,ejemplo-propio --flujo ejemplo-ci
   rojo-ci:    no hay ensayo
   aviso: 1 commit nuevo desde el HEAD del ensayo de demo-ci; solo la cabeza está ensayada, que es lo que GitHub corre
CÍRCULO ABIERTO: ejemplo-ci se ensayó sobre otro árbol; rojo-ci sin ensayo
```

y, cuando todo cuadra, la última línea es `círculo cerrado: los 3 flujos se ensayaron sobre el árbol 160eb33a95a0, el del
commit 464bbb2eb4e4 en origin main`.

**`PUBLICADO.json`:** `{"remoto", "rama", "local" (bool), "commit", "arbol", "flujos": {"demo-ci": {"ensayo": <ruta>,
"arbol_ensayado", "head_ensayado", "tipo", "igual", "mismo_commit", "jobs", "verde", "diferencia": [...] | null,
"motivo"}, …}, "commits_nuevos", "fusion": {"base", "arbol", "igual"} | null, "cerrado": bool, "codigo": 0|1|2}`.

**Códigos de salida.** **0:** cerrado (todos los flujos de `--flujos` con ensayo, verde, sobre el árbol publicado). **1:**
abierto: algún flujo sin ensayo, con ensayo que no ensayó o no dice su árbol, en rojo, o sobre otro árbol. **2:** no se pudo
comprobar: el remoto o la rama no se leen, un `ENSAYO.json` no es JSON, dos ensayos del mismo flujo, o git falla. Los avisos
(commits intermedios, otra historia, fusión con otro árbol, el clon en otro commit que el remoto) no cambian el código.

**`cv/ci/prueba_ci.py`:** las `P-CR-n` de §5, como grupo `cr1`…; `main` etiqueta por prefijo con una tabla
(`{"en": "P-EN", "cr": "P-CR"}`, y `P-CI` si no) en lugar de los dos casos de hoy. Nada más cambia.

**`cv/ci/ensayo_flujo.py`:** no cambia. Su docstring de «lo que el ensayo no ve» puede citar la comprobación en una frase;
no es necesario.

**Coste por push:** un `ls-remote` (contra GitHub, del orden de un segundo; no medido), un `fetch` solo si falta el
objeto, y una decena de órdenes de git locales de milisegundos. Lo que cuesta de verdad es lo que ya costaba: re-ensayar
cuando cae.

## 5. Las pruebas, en rojo antes (`P-CR-n`, en `cv/ci/prueba_ci.py`)

**Montaje común.** `repo_minimo()` de la etapa 34 (el flujo `mini`, `MARCA` = `v1`, `GIT_C`), más un remoto:
`git init --bare -q <tmp>/remoto.git` y `git remote add origin <ruta>` en el repo. El ensayo se obtiene con `ensayar(repo)`
(ya existe: corre `ensayo_flujo.main` sobre `mini` y devuelve el `ENSAYO.json`); la comprobación se carga con `importlib`
(`cargar_comprobacion()`, como `cargar_ensayo`) y se llama `main([repo, <ENSAYO.json>…, "--flujos", "mini", "-o",
tmp()])` bajo `redirect_stdout`. Sin Docker ni red: el remoto es una ruta; `git push`, `ls-remote` y `fetch` sobre ella
funcionan sin red. Hoy, `cargar_comprobacion` lanza una excepción (el fichero no existe) y las trece caen, que es lo que
`prueba_ci.py rojo` espera de cada grupo.

| Prueba | Monta | Hoy (rojo) | Con el cambio |
|---|---|---|---|
| **P-CR-1** negativo, ensayo del HEAD | clon limpio; `ensayar`; `push origin main` | no existe el guion | código 0; la línea de `mini` dice «el mismo commit»; `PUBLICADO.json["cerrado"]` y `flujos.mini.igual` verdaderos; la última línea empieza por «círculo cerrado» |
| **P-CR-2** negativo, ensayo del índice | `MARCA` = `v2`, `git add`; `ensayar` (`tipo arbol`); `commit`; `push` | ídem | 0; «el commit es nuevo sobre él»; `mismo_commit` falso, `igual` verdadero |
| **P-CR-3** `git add` de más | como P-CR-2, y después `OTRO` añadido antes del `commit` | ídem | 1; la línea lleva «OTRO ÁRBOL», «1 ruta» y `A\tOTRO`; `diferencia == ["A\tOTRO"]`; última línea «CÍRCULO ABIERTO» |
| **P-CR-4** `commit --amend` con cambio | `commit`; `ensayar` (`tipo commit`); `MARCA` = `v3`, `add`, `commit --amend --no-edit`; `push` | ídem | 1; `M\tMARCA`; la línea dice «el commit ensayado … ya no está en main» |
| **P-CR-5** amend solo de mensaje | `commit`; `ensayar`; `commit --amend -m otro`; `push` | ídem | 0; «el commit es nuevo sobre él» (mismo árbol) |
| **P-CR-6** sin ensayo y ensayos que no valen | (i) ningún `ENSAYO.json`; (ii) una ruta que no existe; (iii) `ENSAYO.json` con `no_ensayado` (de `ensayar` sobre un repo con `nuevo.txt` sin seguimiento); (iv) sin la clave `clon`; (v) `clon.git == false` (de `ensayar` sobre una exportación) | ídem | 1 en los cinco, con «no hay ensayo de mini», «no ensayó nada», «no dice qué árbol ensayó» según el caso; (vi) un fichero que no es JSON: 2 |
| **P-CR-7** otra copia | (i) `ENSAYO.json` con `clon.arbol` = un id de 40 hex que no existe: 1 y «no está en este clon»; `diferencia` es `null`; (ii) un segundo clon del remoto con el mismo contenido, su `ensayar`, comprobado desde el primero: 0 | ídem | lo dicho |
| **P-CR-8** dos flujos, dos árboles | `ensayar` en `v1` (`ENSAYO.json` copiado con `flujo` = `otro`); `MARCA` = `v2`, `add`, `ensayar` (`mini`); `commit`; `push`; `--flujos mini,otro` | ídem | 1; `mini` igual, `otro` «OTRO ÁRBOL» con `M\tMARCA`; la última línea nombra solo `otro` |
| **P-CR-9** varios commits | `MARCA` = `v2` y `OTRO`, los dos con `add`; `ensayar` (árbol `T`, `clon.head` = el commit 1); `git commit -m a -- MARCA` (commit a, solo `MARCA`); `git commit -m b` (commit b, el resto: árbol `T`); `push` | ídem | 0 con `aviso: 2 commits nuevos desde el HEAD del ensayo`; `commits_nuevos == 2`; variante: `ensayar` del HEAD y dos commits más con cambios: 1, con las rutas |
| **P-CR-10** PR | rama `r` con un commit; `ensayar`; `push origin r`; `--rama r --base main`: 0 y «la fusión tendría el mismo árbol»; `main` avanza (otro commit en `main` empujado); otra vez: 0 con `aviso: el commit de fusión … no está ensayado`; `fusion.igual` falso | ídem | lo dicho |
| **P-CR-11** `--local` (Q-CR-5 b) | `ensayar` del índice; `commit` sin `push`; `--local`: 0; `OTRO` añadido y `commit --amend`: 1 | ídem | lo dicho; `PUBLICADO.json["local"]` verdadero |
| **P-CR-12** no se puede comprobar | `--remoto` una ruta que no existe; `--rama` que no está en el remoto | ídem | 2 en los dos, con «no se pudo leer» |
| **P-CR-13** ensayo en rojo y jobs que faltan (Q-CR-4 a, Q-CR-7 b) | `ENSAYO.json` con `como_se_esperaba: {"uno": false}`; otro con `informes_iguales: {"negativo": false}`; con `--jobs-minimos mini=uno,dos` y solo `uno` ensayado | ídem | 1, con «salió en rojo» / «no corrió dos» |

**Dónde corren:** en el job `pruebas` de `demo-ci.yml`, que ya ejecuta `python3 cv/ci/prueba_ci.py` en `verificador/` sin
Docker ni red; el flujo no se toca. Necesitan `git`, `bash` y `tar`, como las `P-EN`. Dentro del ensayo local, `pruebas`
las corre a su vez: unos segundos más (cada una levanta uno o dos repositorios de dos ficheros y un remoto vacío).

## 6. Los controles del ANTES, exactos

Un guion `cr/controles_cr.sh <clon limpio del público, en el HEAD de la etapa> <carpeta vacía fuera del clon>`, como
`en/controles_en.sh`. No toca el clon ni `origin`: trabaja en copias y en un remoto local.

**El remoto de prueba y la copia:**
```
git clone -q --bare <clon> <B>/remoto.git          # hace de remoto; lleva los commits fijados (54e8b9f) y main
git clone -q <B>/remoto.git <B>/copia              # origin = el remoto de prueba
```

**El estado ensayado,** uno solo para los tres controles: en `<B>/copia`, un cambio pequeño pero real en un fichero que
los flujos leen (por ejemplo una línea nueva en `verificador/cv/ci/CI.md`, para que cualquier texto cuente), `git add`, y
el ensayo de los tres flujos con las órdenes de siempre (demo `pruebas,negativo,positivo --flujo demo-ci`; ejemplo
`ejemplo,ejemplo-propio --flujo ejemplo-ci`; rojo `rojo --flujo rojo-ci --rojo rojo`), cada uno en su carpeta
`<B>/ens/<flujo>/`. Los tres tienen que salir con 0 y `clon.tipo == "arbol"`; el árbol `T` es `clon.arbol`, el mismo en
los tres (se comprueba). Es el estado normal del laboratorio antes de un push. Los tres ensayos se hacen una sola vez: los
tres controles comparten los mismos `ENSAYO.json`, que es exactamente lo que pasa en un push real.

**El control negativo:** `git commit -q -m "control negativo"` (árbol `T`), `git push -q origin HEAD:refs/heads/negativo`,
y `python3 cv/ci/comprobar_publicado.py <B>/copia <B>/ens/*/ENSAYO.json --rama negativo -o <B>/res/negativo`. **Tiene que
dar 0,** con «el mismo árbol; el commit es nuevo sobre él» en las tres líneas y `cerrado: true`.

**El control positivo, `git add` de más:** desde el mismo estado (el commit del negativo está hecho; se vuelve al índice
ensayado con `git reset -q --soft HEAD~1`, que deja el índice en `T`), `echo … > verificador/cr/DE-MAS.txt`, `git add`,
`git commit -q -m "control positivo add"`, `git push -q origin HEAD:refs/heads/positivo-add`, y la comprobación con
`--rama positivo-add`. **Tiene que dar 1,** con «OTRO ÁRBOL: 1 ruta difiere (A verificador/cr/DE-MAS.txt)» en las tres
líneas, `diferencia == ["A\tverificador/cr/DE-MAS.txt"]` en los tres flujos y «CÍRCULO ABIERTO» nombrando los tres.

**El control positivo, `commit --amend`:** desde el commit del negativo (`git checkout -q negativo` o `git reset -q --hard
<ese commit>`), un cambio en un fichero ya ensayado (`verificador/cv/ci/CI.md`, otra línea), `git add`, `git commit -q
--amend --no-edit`, `git push -q origin HEAD:refs/heads/positivo-amend`, y la comprobación con `--rama positivo-amend`.
**Tiene que dar 1,** con «OTRO ÁRBOL: 1 ruta difiere (M verificador/cv/ci/CI.md)» y `diferencia == ["M\tverificador/cv/ci/CI.md"]`.
Como el ensayo fue del índice (`tipo arbol`), la frase «el commit ensayado ya no está» no sale aquí; la variante con el
ensayo de un commit la cubre P-CR-4 con el flujo `mini` (sin coste de Docker). Si Jev quiere el amend sobre un ensayo
`tipo commit` también en el control, cuesta tres ensayos más: commit primero, ensayo del HEAD, amend, push.

**Qué se compara y cómo se decide,** en `cr/CONTROLES-CR.json` escrito por el guion: por control, el código, la última
línea, `PUBLICADO.json` entero y, para los positivos, `diferencia` de cada flujo. Pasa el control positivo si los dos dan
1 y `diferencia` es exactamente la ruta tocada; pasa el negativo si da 0 y los tres `igual` son verdaderos. Cualquier otra
cosa es la regla de parada del ANTES. No hay nada que apartar como variable: los ids de árbol y de commit son los que son,
y el guion los guarda.

**El caso real:** el push de la etapa a `origin main`, con los tres `ENSAYO.json` de ese push (los de los ensayos que la
opción B exige, sobre el índice del clon con todo lo de la etapa añadido: el guion, las pruebas, la guía,
`RESULTADO-CIRCULO.md` con los controles y la previsión sellada). Justo después del `git push`:
`python3 cv/ci/comprobar_publicado.py <clon> <ens>/demo/ENSAYO.json <ens>/ejemplo/ENSAYO.json <ens>/rojo/ENSAYO.json -o
<res>`. **Tiene que dar 0** y `cerrado: true`; `PUBLICADO.json` va al segundo commit como `cr/PUBLICADO-PUSH.json`
(Q-CR-6 a), con su propio push ensayado y comprobado. Si da 1, el push de la etapa no está comprobado: se re-ensaya y se
publica un commit de arreglo, y el resultado lo cuenta.

**Lo que cuesta,** medido por el guion con `date` antes y después de cada orden: los tres ensayos (lo de siempre) y las
tres comprobaciones (segundos). La cifra de más por push es la de la comprobación.

## 7. Lo que cambia en la guía (`cv/ci/CI.md`)

Una sección nueva, después de «Antes de cada push: el ensayo local» y antes de «Cómo repetirlo en tu máquina»:
**«Después del push: la comprobación»**, con estas frases:

- «El ensayo no sabe qué se publicó después: un `git add` o un `commit --amend` posteriores cambian el árbol sin aviso.
  `cv/ci/comprobar_publicado.py` cierra el círculo: lee el commit que el remoto tiene (`git ls-remote`), saca su árbol y
  lo compara con el que cada `ENSAYO.json` dice haber ensayado (`clon.arbol`).»
- «`python3 cv/ci/comprobar_publicado.py <clon> <ENSAYO.json de la demo> <del ejemplo> <del rojo> [--rama main] [-o
  <carpeta>]`. Pasa (0) si los tres ensayos son verdes y del mismo árbol que el commit publicado; cae (1) si falta un
  ensayo, si no ensayó nada, si salió en rojo o si ensayó otro árbol, y entonces lista las rutas que difieren y la orden
  para re-ensayar ese flujo; 2 si no pudo leer el remoto.»
- «El commit no cuenta, el árbol sí: un amend que solo cambia el mensaje pasa; un push de varios commits pasa si la cabeza
  es el árbol ensayado, con un aviso por los intermedios, que GitHub no corre.»
- «En un PR, compruébalo sobre la rama (`--rama <rama>`); con `--base main` predice el árbol del commit de fusión con `git
  merge-tree` y avisa si `main` avanzó: ese árbol no está ensayado. Tras fusionar, compruébalo sobre `main` con los mismos
  `ENSAYO.json`.»
- (con Q-CR-5 b) «Antes del push, `--local` hace lo mismo con el HEAD del clon, sin red; no sustituye al de después, que es
  el único que lee lo publicado.»
- «Lo que no ve: si los `ENSAYO.json` son los últimos (un ensayo viejo sobre el mismo árbol pasa, porque el árbol es el
  contenido), el commit de fusión real de un PR, y nada de lo que pasa en el runner. `PUBLICADO.json` guarda lo comparado.»

En la sección del ensayo, la frase «El ensayo no ve lo de siempre: …» añade al final: «Lo que se publique después del
ensayo lo mira la comprobación de la sección siguiente.» En `verificador/README.md`, la frase que cita el ensayo (no la he
leído; la etapa 34 la tocó) añade «…y, después del push, `comprobar_publicado.py` comprueba que el árbol publicado es el
ensayado».

## 8. Los riesgos

**Lo que puede romper en los flujos que ya están en verde** (los YAML no cambian; lo único que corre en GitHub y cambia es
el job `pruebas` de la demo, con las `P-CR`):

- las `P-CR` hacen `git push`, `ls-remote` y `fetch` contra un repositorio vacío en `tempfile`, en el runner: sin red, pero
  si el runner tuviera un `git` con `protocol.file.allow` restringido fallarían ahí; en 2.38+ las rutas locales directas
  (`<ruta>` sin `file://`) no pasan por esa guarda, y el remoto se añade como ruta; se prueba en la máquina del laboratorio
  (git 2.43) y, si en el runner fallara, es `pruebas` en rojo, que se ve;
- cada orden de git de las pruebas lleva `GIT_C` (nombre, correo, sin firma, sin hooks), como las `P-EN`, para no depender
  de `HOME` del runner;
- `prueba_ci.py` corre también dentro del ensayo local: las `P-CR` corren el ensayo dentro del ensayo, en `tempfile`, nunca
  en el clon; si una dejara basura en el clon, la guarda del ensayo siguiente pararía;
- el guion nuevo no lo importa nadie más y no toca `ENSAYO.json`, así que `sellar_prevision_*.py` no cambian;
- con Q-CR-1 (b), un flujo nuevo puede ponerse en rojo por su cuenta (un commit sin *trailer*, un PR ajeno) sin tocar los
  demás; por eso iría aparte y limitado al repositorio propio.

**Lo que la comprobación no puede ver:**

- si los `ENSAYO.json` que se le dan son los del último ensayo: compara contenido, y un ensayo viejo sobre el mismo árbol es
  un ensayo válido de ese árbol; lo que no puede ser es un ensayo de otro árbol;
- si `ENSAYO.json` se editó a mano: no es una guarda contra la mala fe, es contra el descuido (el ANTES no pide más);
- el commit de fusión real de un PR: `merge-tree` lo predice con el `main` del momento; si `main` avanza entre la
  comprobación y la fusión, el árbol es otro. Tras fusionar, la comprobación sobre `main` sí lo ve;
- un push después de la comprobación (`push -f`, otro commit): hay que volver a correrla; no vigila;
- que GitHub haya corrido en verde: eso lo dice la CI, y es otra cosa;
- lo que el ensayo mismo no ve (la guía lo lista): un círculo cerrado dice que el runner corre lo ensayado, no que el ensayo
  se parezca al runner en lo que no emula;
- que el `ensayo_flujo.py` que ensayó sea el publicado: no lo mira (fuera de la etapa; `ENSAYO.json` no lleva su huella).

**Mi estimación, aparte de la previsión que se sella:** que el control positivo caiga en los dos casos y el negativo pase
a la primera, muy probable (0,95): es la igualdad de dos ids de 40 hex, y las `P-CR` la cazan antes en el flujo `mini`. Que
el push de la etapa pase a la primera, probable (0,8): lo que puede fallar es el orden de las cosas en el push real (un
texto tocado después del ensayo, que es justo lo que la comprobación caza), y entonces la etapa cae por lo mismo que mide.
