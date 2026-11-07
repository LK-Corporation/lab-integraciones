# Diseño a ciegas de la etapa 34: el ensayo local ensaya lo que se publica

Diseño para la pregunta fijada en `ANTES-ETAPA-ENSAYO.md`: que `cv/ci/ensayo_flujo.py` deje de dar verde sobre algo distinto
de lo que se va a publicar, sin cambiar lo que da cuando lo ensayado y lo publicado coinciden. Diseña Fable, a ciegas: ha leído
el ANTES, el ensayo de hoy, `prueba_ci.py`, `CI.md` y los flujos del clon público, y ha probado el comportamiento de git en
una copia del clon. No ha leído ningún resultado ni ninguna nota de cómo se descubrió el fallo. Las decisiones abiertas van
numeradas `Q-EN-n` para Jev; la recomendación va aparte, al final de cada una.

Rutas: relativas a la raíz del repositorio público (`.github/workflows/`, `verificador/`, `ejemplo-ci/`) o a `verificador/`
(`cv/ci/…`). «El clon» es la copia del repositorio público sobre la que se lanza el ensayo; «la carpeta de trabajo» es el
segundo argumento del ensayo.

## 0. Lo comprobado antes de diseñar

- **Cómo emula hoy un checkout** (`copiar_repo`): si el `ref` es un commit de 40 hex que está en el clon, `git archive <ref>`;
  si no, `shutil.copytree` del árbol de trabajo sin `.git` ni `__pycache__`. `github.sha` es `git rev-parse HEAD` si hay
  `.git`; si no, `e0`×20. La demo pasa `github.sha` como `laboratorio_ref`, así que su checkout del laboratorio cae en
  `git archive HEAD` aunque el índice lleve otra cosa: es el caso de la etapa 33.
- **Git, probado en una copia del clon** (git 2.43, `core.filemode=true`):
  - el estado del control positivo (`HEAD` en `371937c`, `git read-tree -u --reset 54e8b9f`) deja 124 rutas distintas en el
    índice, ninguna sin `git add` y ninguna sin seguimiento;
  - `GIT_INDEX_FILE=<copia del índice> git write-tree` da el árbol `c92b44f2…`, que es `54e8b9f^{tree}` y no
    `HEAD^{tree}` (`fa2da2d8…`), sin tocar el índice del clon; escribe un objeto árbol en `.git/objects` (colgante, inocuo);
  - `git archive <árbol>` funciona igual que con un commit y conserva el modo 755 de los tres `.sh`; `git cat-file -e
    <árbol>^{commit}` falla, así que `hay_commit` rechaza un árbol; `write-tree` más `archive` tardan 0,05 s (11 MB);
  - la única diferencia visible entre archivar un commit y su árbol es el mtime de los ficheros (el del commit frente a
    «ahora»);
  - el repositorio no tiene `.gitattributes` ni enlaces simbólicos; los únicos ignorados presentes en el clon limpio son
    `__pycache__/`, que `copytree` ya excluye. `.gitignore` también ignora `verificador/bases_oru/`, que regenera
    `bases_oru.py` antes de las pruebas: hoy se copiaría si existiera; con el arreglo no;
  - `git status --porcelain` distingue lo que hace falta: `M ` (índice), ` M` (sin add), `MM` (las dos), `??` (sin
    seguimiento); los ignorados solo salen con `--ignored`.
- **Las pruebas:** `prueba_ci.py` llama a cada `pNN` y pone el grupo `P-CI-NN` a partir del nombre; carga módulos del
  directorio con `importlib` (`cargar_anotaciones`); corre bash como GitHub (`paso_de_github`). Nada llama a `ensayo_flujo.py`.
- **Los flujos:** `demo-ci.yml` (job `pruebas`: `prueba_ci.py` y `prueba_vc.py`, sin Docker ni red), `ejemplo-ci.yml` y
  `rojo-ci.yml` fijados a `54e8b9f` (en `origin/main`), `verificador-conversor.yml` con los dos checkouts (`proyecto` sin
  `ref`, `lab` con `ref: inputs.laboratorio_ref`) y la comprobación `^[0-9a-f]{40}$` de `laboratorio_ref`. No cambian.
- **La guía:** `CI.md` no menciona el ensayo. Lo menciona `verificador/README.md` (líneas 413 y 448: «Un ensayo local antes
  del primer push: `cv/ci/ensayo_flujo.py` corre en una máquina los pasos…»). `ENSAYO.json` lo leen también
  `cv/ci/sellar_prevision_ci.py`, `sellar_prevision_ci2.py` y `sellar_prevision_mant.py` (no leídos): el arreglo conserva sus
  claves y solo añade.
- **El ensayo del laboratorio y el publicado son el mismo fichero** (diff vacío), última modificación en `5183b4e`.

## 1. Qué es «lo que se publica» y qué hace el ensayo en cada estado

**Definición.** Lo que se publica es el árbol del próximo commit: el índice del clon. Si el índice coincide con `HEAD`, ese
commit ya existe y es `HEAD`. Un fichero sin `git add`, uno sin seguimiento o uno ignorado no entra en el commit y por tanto
no se publica; un commit que ya está en el repositorio (el `ref` fijado del ejemplo) se publica tal cual está, y el índice no
le afecta.

**El objeto publicado** (`clon["publicado"]`): `HEAD` si `write-tree(índice) == HEAD^{tree}`; si no, el árbol del índice.
`github.sha` es `HEAD` en el primer caso y, en el segundo, el id de ese árbol (Q-EN-4): 40 hex que pasan la comprobación del
flujo, que no es ningún commit del clon, y que identifica en el registro lo que se ensayó.

**Cada checkout** (`actions/checkout`, en `correr_pasos`), por este orden:

| `ref` del checkout | Con `.git` | Sin `.git` |
|---|---|---|
| ninguno (el repositorio que llama: `proyecto`, el checkout de `pruebas`, de `positivo-comprobado`, de los `*-comprobado`) | `git archive <publicado>` | copia de la carpeta, como hoy |
| igual a `github.sha` (la demo: `laboratorio_ref: ${{ github.sha }}`) | `git archive <publicado>`, el mismo objeto | no se da: `github.sha` es `e0`×20 y ningún checkout lo lleva (si lo llevara, es la fila de abajo) |
| un commit de 40 hex que está en el clon (el ejemplo y el rojo: `54e8b9f`) | `git archive <commit>`, como hoy: es un commit publicado y el índice no lo cambia | copia de la carpeta con aviso en la línea: «el commit … no se puede resolver sin `.git`» (Q-EN-6) |
| cualquier otra cosa (`COMMIT_C1` de una plantilla, un commit que no está) | `git archive <publicado>`, con aviso: «el commit … no está en esta copia: se ensaya lo que se publica» | copia de la carpeta con el mismo aviso |

El primer caso y el segundo son el mismo: la fila está separada porque hoy se tratan distinto (copia del árbol frente a
`git archive HEAD`) y con el arreglo pasan a ser lo mismo. Lo que hoy copia el árbol de trabajo pasa a exportar el índice; lo
que hoy archiva un commit fijado sigue igual.

**Cada estado del clon**, decidido una vez al empezar (`estado_del_clon`), antes de correr ningún job:

1. **Índice distinto del `HEAD`** (hay entradas `M `, `A `, `D `, `R ` en `git status --porcelain`; es el estado normal
   antes del commit, y el de la etapa 33): se ensaya el árbol del índice (Q-EN-1). Cabecera: «lo que se publica: el árbol
   del índice `c92b44f2f344` (HEAD `371937c9fb43`, 124 rutas distintas); `github.sha` es ese árbol, no un commit». La línea
   de cada checkout sin `ref` o con `ref` igual a `github.sha` dice «árbol del índice `c92b44f2f344`, no el HEAD
   `371937c9fb43`». La última línea y `ENSAYO.json` repiten sobre qué se ensayó. Razón: es lo que se va a publicar, y el
   commit todavía no existe; exigir el commit (Q-EN-1 b) obliga a rehacerlo si el ensayo sale rojo.
2. **Cambios sin `git add`** (` M`, `MM`, ` D`, y también los no fusionados `UU`): el ensayo **para con el código 2 sin
   correr ningún job** (Q-EN-2), con la lista de rutas y la salida: «no se ensaya: N cambios sin `git add` (…): no entrarían
   en lo publicado. `git add` lo que vaya, `git stash -u` lo que no, o ensaya una exportación del índice (`git checkout-index
   -a --prefix=<carpeta>/`)». Razón: el ensayo del índice ignoraría esos cambios y daría verde sobre otra cosa que lo que el
   autor cree estar ensayando; la etapa 33 enseñó que un aviso en una línea no basta. Una entrada `MM` tiene parte en el
   índice y parte fuera: para por la parte de fuera.
3. **Ficheros sin seguimiento** (`??`): lo mismo que el 2, con el mismo código y la misma frase («… y M ficheros sin
   seguimiento»). Razón: es un fichero nuevo que se olvidó añadir, o basura; en los dos casos, lo que se ensaya tiene que
   coincidir con lo que se publica, y el autor decide cuál de las dos cosas es. **Ignorados** (`!!`): no paran, no se avisan
   y no entran en el checkout (hoy entran todos menos `__pycache__`). Razón: están ignorados a propósito y nunca se publican.
4. **Clon limpio** (índice igual al `HEAD`, nada sin add ni sin seguimiento): `publicado = HEAD`, `github.sha = HEAD`, todo
   checkout con `ref` igual a `github.sha` o con un commit fijado hace exactamente lo de hoy (`git archive <commit>`, la
   misma orden, el mismo texto en la línea). El checkout sin `ref` pasa de copiar el árbol a `git archive HEAD`: el mismo
   contenido salvo los ignorados (en el clon limpio de hoy, solo `__pycache__`, que tampoco se copiaba) y los mtimes (los del
   commit en vez de los del disco). Cabecera: «lo que se publica: el commit HEAD `74a6a99a3ba4` (índice igual)». Razón: es
   la condición 4 del ANTES; se cumple por construcción en el checkout con `ref` y por el contenido en el checkout sin `ref`,
   y el control negativo lo mide.
5. **Carpeta sin `.git`** (una exportación del índice o un `git archive` desplegado): se ensaya tal cual, copiando la
   carpeta como hoy, con `github.sha = e0`×20 como hoy. Cabecera: «la carpeta no tiene `.git`: se ensaya tal cual; quien la
   exportó responde de que sea lo que se publica». El `ref` fijado que no se puede resolver se copia también, con aviso
   (Q-EN-6). Razón: el ensayo no puede saber de dónde salió la carpeta y la condición 4 exige que dé lo mismo que hoy; el
   aviso es lo único que añade. Si el clon tiene `.git` pero ningún commit (`rev-parse HEAD` falla), para con «el clon no
   tiene commits» y el código 2 (no se prueba: no es un estado del laboratorio).

**Lo que no cambia, y por qué:** el YAML del flujo (`.github/workflows/<flujo>.yml` o su plantilla en
`cv/ci/github-ci2/`) y el YAML del `uses: ./…` se siguen leyendo del árbol de trabajo. Tras la guarda del punto 2 y 3, el
árbol de trabajo coincide con el índice en todo lo que tiene seguimiento y no hay nada sin seguimiento, así que leerlo del
índice (`git show :<ruta>`) daría lo mismo y no tendría prueba en rojo. La forma remota (`git show <commit>:<ruta>`) tampoco
cambia.

## 2. Decisiones abiertas (para Jev)

**Q-EN-1. Con el índice distinto del `HEAD`.**
- (a) Se ensaya el árbol del índice; `github.sha` no es un commit. Implica: el ensayo sirve antes del commit, como en la 33,
  y es lo que la regla de parada del ANTES llama «la exportación del índice», sin exportar a mano.
- (b) Se para con el código 2 y se pide el commit. Implica: `github.sha` es siempre un commit de verdad y la emulación es
  más fiel; cada ensayo rojo obliga a `commit --amend` o a un commit de arreglo; la 33 habría parado en vez de dar verde.
- (c) Como (b), salvo con una opción explícita (`--indice`) que hace (a). Implica: dos modos y una opción más que
  documentar.
Recomendación: (a). Lo que se publica es el índice; el commit lo copia. Y (a) es lo que hizo el ensayo correcto de la 33.

**Q-EN-2. Cambios sin `git add` y ficheros sin seguimiento.**
- (a) Parar con el código 2 antes de correr ningún job, con la lista. Implica: para ensayar con basura al lado hay que
  apartarla (`stash -u`) o exportar el índice; ningún ensayo verde sale de un clon en el que lo ensayado y lo que el autor
  tiene delante difieren.
- (b) Avisar (cabecera, última línea y `ENSAYO.json`) y seguir con el índice. Implica: el aviso puede perderse, como se
  perdió la línea «git archive 371937c9fb43».
- (c) Parar solo si las rutas tocan lo que los flujos usan (`verificador/`, `ejemplo-ci/`, `.github/`, `tests/`); avisar
  con el resto. Implica: una lista de rutas que hay que mantener, y una nota suelta en la raíz no para.
Recomendación: (a). La escapatoria existe y no necesita opción: la exportación del índice, que es el estado 5.

**Q-EN-3. Cómo se exporta el índice.**
- (a) `git write-tree` sobre una copia del índice (`GIT_INDEX_FILE`) y `git archive <árbol> | tar -x`. Implica: un solo
  camino para commits y árboles, un id de 40 hex para `github.sha` y el registro; deja un objeto árbol colgante en
  `.git/objects` del clon (lo mismo que hace `git commit` antes de escribir el commit; `gc` lo quita).
- (b) `git checkout-index -a --prefix=<destino>/`. Implica: no escribe nada en `.git`; no da ningún id, así que `github.sha`
  sería un marcador fijo o un hash de `git ls-files -s` que no es un objeto de git; dos caminos de exportación.
Recomendación: (a), por el id y por el camino único.

**Q-EN-4. `github.sha` cuando lo publicado no es un commit.**
- (a) El id del árbol del índice. Implica: 40 hex que pasan la comprobación del flujo, que no resuelven a ningún commit en
  el clon y que dicen qué se ensayó; si algún informe guardara `laboratorio_ref`, llevaría un árbol en vez de un commit.
- (b) Un marcador fijo, como `e0`×20 sin `.git`. Implica: el registro no distingue dos ensayos de índices distintos.
- (c) `HEAD`, con la regla «`ref` igual a `HEAD` → índice». Implica: en el push del pin (el ejemplo fija `HEAD` y el índice
  lleva el pin), el laboratorio del ejemplo se ensayaría con el índice y no con el commit fijado, que es lo publicado.
Recomendación: (a).

**Q-EN-5. El commit fijado está en el clon pero no en `origin/main`** (sin push, o un `fetch` pendiente; fuera de la
pregunta estricta del ANTES).
- (a) Nada, como hoy. Implica: el ensayo da verde y GitHub no puede traer ese commit.
- (b) Avisar en la línea del checkout, con `git merge-base --is-ancestor <commit> origin/main`. Implica: sin red, mira la
  referencia local, que puede estar atrasada; cuesta un proceso por checkout.
- (c) Parar.
Recomendación: (b), si cabe en la sesión; si no, (a) y una línea en «lo que no ve».

**Q-EN-6. Sin `.git`, un `ref` que no se puede resolver.**
- (a) Copiar la carpeta, como hoy, con el aviso en la línea del checkout. Implica: la exportación da los mismos trabajos y
  veredictos que hoy (condición 4); el laboratorio del ejemplo se ensaya con la exportación y no con `54e8b9f`.
- (b) Parar. Implica: la exportación solo sirve para la demo, no para el ejemplo ni el rojo.
Recomendación: (a).

**Q-EN-7. Dónde van las pruebas `P-EN-n`.**
- (a) En `cv/ci/prueba_ci.py`, como grupo nuevo (`en1`… con la etiqueta `P-EN-n`), al final. Implica: un fichero de 1235
  líneas crece unas 150; `main` aprende a etiquetar dos prefijos.
- (b) En un fichero nuevo `cv/ci/prueba_ensayo.py` que `prueba_ci.py` importa y cuyas funciones añade a `PRUEBAS`. Implica:
  `mira`, `tmp` y `grupo` tienen que pasarse o importarse en círculo.
Recomendación: (a).

**Q-EN-8. Cómo se comparan los controles.**
- (a) Un guion publicado (`cv/ci/comparar_ensayos.py`) con su prueba en rojo. Implica: más código y otra prueba en la
  sesión.
- (b) `diff -r` entre las dos carpetas de trabajo, con lo apartado listado a mano en el resultado (§5). Implica: ningún
  código nuevo; el resultado lleva el diff entero.
Recomendación: (b), por el tope de una sesión.

## 3. El cambio en el código (`cv/ci/ensayo_flujo.py`)

Con las recomendaciones (a)/(a)/(a)/(a)/(b)/(a)/(a)/(b). Si Jev decide otra cosa, cambia lo indicado en cada función.

**`estado_del_clon(repo, temporal)` (nueva).** Devuelve un diccionario:
```
{"git": True, "head": "<40 hex>", "arbol": "<40 hex>", "publicado": "<40 hex>", "tipo": "commit" | "arbol",
 "indice_distinto": ["M verificador/README.md", …], "sin_add": ["README.md", …], "sin_seguimiento": ["nuevo.txt", …]}
```
o `{"git": False}` si no hay `.git`. Hace, en este orden: `git status --porcelain` (una línea por ruta; `XY ruta`, los
renombrados `R  a -> b`); reparte por las dos columnas (`X` en `MADRCT` → `indice_distinto`; `Y` distinta de espacio y de
`?` → `sin_add`; `??` → `sin_seguimiento`; `U` en cualquiera → `sin_add`); `git rev-parse HEAD` (si falla: «el clon no tiene
commits», código 2); copia `.git/index` a `temporal` y `GIT_INDEX_FILE=<copia> git write-tree`; `git rev-parse
HEAD^{tree}`; `publicado = head` si los dos árboles coinciden, si no `arbol`. Nunca modifica el índice del clon.

**`copiar_repo(repo, destino, ref, clon)` (cambia la firma y el cuerpo).** Devuelve el texto de la línea del checkout:
- sin `.git`: `copytree` como hoy; texto «copia del árbol», y si `ref` es algo y no vacío: «copia del árbol; el commit
  `<ref12>` no se puede resolver sin .git»;
- `ref` vacío o igual a `clon["sha"]`: `exportar(repo, destino, clon["publicado"])`; texto «git archive `<head12>`» si
  `tipo == "commit"` (el mismo texto que hoy), o «árbol del índice `<arbol12>`, no el HEAD `<head12>`»;
- `hay_commit(repo, ref)`: `exportar(repo, destino, ref)`; texto «git archive `<ref12>`», el mismo que hoy;
- si no: `exportar(repo, destino, clon["publicado"])`; texto «el commit `<ref>` no está en esta copia: » seguido del texto
  del segundo punto.

**`exportar(repo, destino, objeto)` (nueva; es el cuerpo de hoy de `git archive | tar -x`).** `git -C repo archive
<objeto>` y `tar -x -C destino`, con `check=True` como hoy.

**`main`.**
1. Tras comprobar que la carpeta de trabajo está vacía, `clon = estado_del_clon(repo, <trabajo>/.runner/indice)`.
2. Si `clon["sin_add"]` o `clon["sin_seguimiento"]`: imprime «== NO SE ENSAYA: N cambios sin git add (hasta 20 rutas, y
   «… y K más») y M ficheros sin seguimiento (…): no entrarían en lo publicado. git add lo que vaya, git stash -u lo que no,
   o ensaya una exportación del índice (git checkout-index -a --prefix=<carpeta>/)»; escribe `ENSAYO.json` con `{"flujo":
   …, "jobs": {}, "esperado_rojo": [], "como_se_esperaba": {}, "informes_iguales": {}, "needs": {}, "no_ensayado": "clon
   sucio", "clon": clon}`; devuelve 2.
3. Imprime la cabecera «== lo que se publica: …» de §1 (uno de los tres textos: commit, árbol, sin `.git`).
4. `sha = clon["head"]` si `tipo == "commit"`, `clon["arbol"]` si `tipo == "arbol"`, `e0`×20 sin `.git`; `clon["sha"] = sha`.
   `base_ctx` lleva `_clon: clon` además de `_repo`.
5. Lo demás, igual. La última línea pasa de «ensayo: …» a «ensayo sobre el commit HEAD `<head12>`: …», «ensayo sobre el
   árbol del índice `<arbol12>` (≠ HEAD `<head12>`): …» o «ensayo sobre la carpeta sin .git: …». `ENSAYO.json` conserva
   todas sus claves y añade `"clon"` (sin la copia del índice; `indice_distinto` como lista de rutas).

**`correr_pasos`.** En la rama `actions/checkout@`, `copiar_repo(ctx["_repo"], destino, w.get("ref"), ctx["_clon"])`.
Nada más.

**Códigos de salida.** 0: todo como se esperaba (igual que hoy). 1: algún job no dio lo esperado o un informe distinto
(igual que hoy), y los `SystemExit("ENSAYO: …")` de hoy. **2 (nuevo):** no se ensayó nada (clon sucio o sin commits).

**El docstring** (líneas 7-8) pasa a decir: «Los `actions/checkout` se emulan con lo que se publica: con un `ref` de 40 hex
que esté en el repositorio, `git archive` de ese commit; sin `ref` o con `github.sha`, el índice del clon (`git archive` del
árbol de `write-tree`, o el HEAD si coinciden); sin `.git`, la carpeta tal cual. Con cambios sin `git add` o ficheros sin
seguimiento no se ensaya nada: sale con 2».

**Coste.** `git status`, `rev-parse` ×2 y `write-tree` sobre la copia: unas decenas de milisegundos; `git archive` del
árbol en lugar de `copytree` para el checkout sin `ref`: medido 0,05 s para 11 MB, no más que la copia. Las pruebas nuevas en
`pruebas`: unos segundos (§4).

## 4. Las pruebas, en rojo antes (`P-EN-n`, en `cv/ci/prueba_ci.py`)

**Montaje común (`repo_minimo()`).** Un repositorio de git en `tmp("en")`: `git -c init.defaultBranch=main init -q`, los
commits con `-c user.name=ensayo -c user.email=ensayo@localhost -c commit.gpgsign=false` (nada depende de la configuración
global del runner ni de la máquina); `.github/workflows/mini.yml` con dos jobs sin `uses:`:
- `uno`: `actions/checkout@<40 hex>` sin `ref`, y un paso `run` con `env: SHA: ${{ github.sha }}` que hace `cat MARCA; echo
  "sha=$SHA"; ls`;
- `dos`: `actions/checkout@<40 hex>` con `ref: <COMMIT1>` y `path: lab`, otro sin `ref`, y `cat lab/MARCA ./MARCA`.
Más `MARCA` con `v1` y `.gitignore` con `*.log`, en el commit 1. El ensayo se carga con `importlib` (como
`cargar_anotaciones`) y se llama `main([repo, tmp("w"), "uno", "--flujo", "mini"])` bajo `redirect_stdout`; se lee la salida
capturada, `<w>/uno/.runner/registro-N.txt` (lo que imprimió el paso) y `<w>/ENSAYO.json`. Ninguna prueba necesita Docker ni
red; necesitan `git`, `bash` y `tar`, que `ubuntu-latest` tiene. Los checkouts del mini no tienen `verificador/`, así que
cada uno copia (la rama «ya estaba» no entra).

| Prueba | Monta | Hoy (rojo) | Con el arreglo |
|---|---|---|---|
| **P-EN-1** índice distinto del HEAD | `MARCA` = `v2`, `git add`; árbol de trabajo igual al índice | el paso imprime `v1` (archivó el HEAD); `sha` = HEAD; no hay clave `clon` | imprime `v2`; `sha` = `clon.publicado` = `git rev-parse` del árbol que da `write-tree` en el repo de prueba, distinto de HEAD; `clon.tipo == "arbol"`; la línea del checkout dice «árbol del índice» y no «git archive <HEAD12>»; devuelve 0 |
| **P-EN-2** cambio sin `git add` | `MARCA` = `v2` sin `add`; control: `MM` (`v2` añadido, `v3` encima) | devuelve 0 y el paso imprime `v2` (copió el árbol de trabajo) | devuelve 2, no existe `<w>/uno/`, la salida lleva `NO SE ENSAYA` y `MARCA`; `ENSAYO.json["no_ensayado"]`; el control `MM` también para |
| **P-EN-3** fichero sin seguimiento | `nuevo.txt` sin `add` | devuelve 0 y `nuevo.txt` está en el checkout | devuelve 2, lista `nuevo.txt`, ningún job corre |
| **P-EN-4** ignorado | `x.log` (ignorado por `.gitignore`) | `x.log` aparece en el `ls` del paso | devuelve 0, `x.log` no aparece, y no para ni avisa |
| **P-EN-5** clon limpio (control y claves nuevas) | nada tras el commit 1 | devuelve 0, imprime `v1`, `sha` = HEAD, la línea del checkout con `ref` igual a `github.sha` dice «git archive <HEAD12>» (verde: es el control de que nada cambia); falta `clon` (rojo) | lo mismo, más `clon.tipo == "commit"` y `clon.publicado == HEAD`; la línea del checkout sin `ref` dice «git archive <HEAD12>» (hoy «copia del árbol») |
| **P-EN-6** sin `.git` | `git archive HEAD \| tar -x` en otra carpeta | devuelve 0, `v1`, `sha` = `e0`×20, «copia del árbol» (verde: control); con `ref: <COMMIT1>` no avisa (rojo) | lo mismo, con `clon.git == False`, y con un `ref` de 40 hex la línea lleva «no se puede resolver sin .git» |
| **P-EN-7** commit fijado con el índice distinto | job `dos`; `MARCA` = `v2` añadido | `lab/MARCA` = `v1` y `./MARCA` = `v2` (verde: control, porque el árbol de trabajo es el índice); con `ref: "ab"×20` (no está) la línea dice «copia del árbol» (rojo) | lo mismo en contenido; con el `ref` que no está, `./MARCA` = `v2` y la línea dice «no está en esta copia: árbol del índice» |
| **P-EN-8** `ENSAYO.json` conserva las claves | cualquiera de las anteriores que ensaye | las seis claves de hoy están (verde: control) | las seis claves, en el mismo orden, más `clon`; con el código 2, `jobs == {}` y `no_ensayado` |

Las comprobaciones marcadas «control» son verdes hoy y tienen que seguirlo; cada cambio del §3 tiene al menos una
comprobación roja hoy: la exportación del índice (P-EN-1), la guarda (P-EN-2, P-EN-3), los ignorados (P-EN-4), las claves y
los textos nuevos (P-EN-5, P-EN-6, P-EN-7, P-EN-8). `prueba_ci.py rojo` sigue significando lo de la etapa 23 (sin el código
fallan todas) y no se usa aquí.

**Cambio en `main` de `prueba_ci.py`:** `PRUEBAS` añade `en1`…`en8`; la etiqueta del grupo pasa a `"P-EN-%d" %
int(nombre[2:])` si el nombre empieza por `en`, y `"P-CI-%d" % int(nombre[1:])` si no. El cómputo de «N comprobaciones, M
pruebas» no cambia. **Cómo corren en `pruebas`:** `demo-ci.yml` ya ejecuta `python3 cv/ci/prueba_ci.py` en `verificador/`
sin Docker ni red; el flujo no se toca. Dentro del ensayo local, el job `pruebas` corre a su vez estas pruebas, que levantan
repositorios de git de dos ficheros en `tempfile`: unos segundos más.

## 5. Los dos controles del ANTES, exactos

**Las dos versiones del ensayo:** «hoy» es `git show 74a6a99:verificador/cv/ci/ensayo_flujo.py`, guardado fuera del clon
(es byte a byte el del laboratorio antes del arreglo); «arreglo» es `cv/ci/ensayo_flujo.py` tras el §3. Las dos se lanzan por
su ruta, no desde el clon, así que el ensayo que corre no depende del estado del clon.

**Las órdenes de ensayo**, las mismas para cada versión y cada estado, con la carpeta de trabajo **fuera del clon** y **con
el mismo nombre absoluto** para «hoy» y «arreglo» (se corre «hoy», se mueve la carpeta a `hoy/`, se corre «arreglo» en la
misma ruta y se mueve a `arreglo/`): así ninguna ruta temporal difiere entre las dos corridas.
- demo: `ensayo_flujo.py <clon> <trabajo> pruebas,negativo,positivo` (corren también `positivo-comprobado`; `real` no se
  pide: necesita red);
- ejemplo: `… --flujo ejemplo-ci ejemplo,ejemplo-propio` (y `ejemplo-comprobado`);
- rojo: `… --flujo rojo-ci rojo --rojo rojo` (y `rojo-comprobado`).
Los tres necesitan el Docker de la máquina del laboratorio (el ensayo corre los pasos `docker pull` y la caja tal cual).

**El control positivo** (el caso de la 33):
```
cp -r <clon limpio> <copia>; cd <copia>
git -c advice.detachedHead=false checkout -q 371937c
git read-tree -u --reset 54e8b9f
git status --porcelain | grep -v '^[MADR]  '      # tiene que no imprimir nada: nada sin add ni sin seguimiento
```
Se corre la demo con «hoy» y con «arreglo». Se decide con tres hechos:
1. `ENSAYO.json`: con «arreglo», `clon.tipo == "arbol"` y `clon.publicado == git rev-parse 54e8b9f^{tree}` (`c92b44f2…`);
   la línea del checkout `negativo/verificar` del laboratorio dice «árbol del índice c92b44f2f344, no el HEAD 371937c9fb43»
   y en ninguna línea aparece «git archive 371937c9fb43». Con «hoy» aparece «git archive 371937c9fb43» (lo medido el 7-nov).
2. El `INFORME.json` de `negativo` (y el de `positivo`) con «arreglo» es **distinto** del de «hoy» sobre este mismo estado,
   porque `54e8b9f` cambió `LINEA-BASE-juguete.json` y el corpus (versión 2); y es **igual**, informe a informe por §5
   abajo, al de «hoy» sobre un clon limpio en `54e8b9f` (el mismo árbol, ya con commit). Ese triángulo es la prueba de que el
   arreglo ensayó el índice y no el HEAD, y de que ensayar el índice es ensayar el commit que saldría de él.
3. Los cuatro jobs dan verde en los dos: el arreglo no cambia el color, cambia sobre qué se da.

**El control negativo** (dos estados, tres flujos, dos versiones: doce corridas):
```
git clone -q <clon limpio> <limpio>; git -C <limpio> status --porcelain          # vacío; HEAD 74a6a99
mkdir <export>; git -C <limpio> checkout-index -a --prefix=<export>/            # la exportación sin .git
```
Para cada flujo y cada estado, «hoy» y «arreglo» tienen que dar: la misma lista de jobs en `ENSAYO.json["jobs"]` con los
mismos valores, el mismo `como_se_esperaba`, el mismo `needs` (salidas incluidas: `resultado`, `nuevos`, `huella`,
`imagen_digest`, `juez`…), y, **informe a informe**, los mismos ficheros con el mismo sha256 en `<trabajo>/<job>/trabajo/corrida/`
(`INFORME.md`, `INFORME.json`, `juicio.jsonl`, `CORRIDA.json`, `ADAPTADOR.json`, `VEREDICTO-CI.json`, `VEREDICTO-CI.md`,
`LINEA-BASE-propuesta.json`, `cajas/`), `<trabajo>/<job>/trabajo/solo-orden.txt`, `<trabajo>/<job>-comprobado/comprobacion/`,
y `<trabajo>/<job>/.runner/resumen.md`. Se compara con `diff -r hoy/ arreglo/` sobre esas rutas (y, aparte, sobre
`.runner/registro-*.txt` y las salidas del ensayo mismo, donde se esperan los textos nuevos de §3 y el ensayo de más en
`pruebas`).

**Lo que puede variar entre dos corridas iguales, y cómo se aparta sin esconderlo:**
- rutas temporales: no deben variar, porque la carpeta de trabajo tiene el mismo nombre absoluto en las dos corridas y el
  clon es el mismo; si aun así aparece una (`tempfile` dentro de `pruebas`), sale en el diff y se lista;
- fechas, horas y duraciones dentro de los informes (donde las haya: se espera en `CORRIDA.json` y en las cabeceras de los
  `INFORME.*`; no se ha comprobado en este diseño): cada línea distinta del diff se lista en el resultado; se admite una
  línea como variable **solo si** difiere únicamente en un valor que casa con un patrón de fecha-hora ISO o de duración, y
  el resultado dice qué ficheros y cuántas líneas se admitieron así; cualquier otra línea distinta es «no da lo mismo»;
- mtimes de los ficheros exportados (commit frente a disco): no están en los informes que se comparan; si algún fichero
  comparado cambiara por ellos, es «no da lo mismo» y se explica;
- `github.sha`: en los dos estados del control negativo es `74a6a99` (limpio) o `e0`×20 (export), igual en «hoy» y
  «arreglo», así que no varía aquí; si algún informe lo lleva, se verá en el control positivo (donde el arreglo pone un
  árbol) y se dice.

**La regla de decisión:** «lo mismo, informe a informe» es diff vacío en las rutas de arriba, salvo las líneas admitidas
como variables y listadas. Si queda una diferencia que no se explica, se aplica la regla de parada del ANTES.

## 6. Lo que cambia en la guía

`CI.md` no habla del ensayo. Se añade una sección corta antes de «Cómo repetirlo en tu máquina», **«Antes de cada push: el
ensayo local»**, con estas frases:
- «`cv/ci/ensayo_flujo.py` corre en una máquina los pasos `run:` de un flujo y emula los checkouts **con lo que se va a
  publicar**: un `ref` de 40 hex que está en el clon se saca con `git archive` de ese commit; sin `ref`, o con
  `github.sha`, se saca el índice del clon (el HEAD si coinciden). Lo que no está en el índice no se ensaya, porque no se
  publica.»
- «Con cambios sin `git add` o ficheros sin seguimiento no ensaya nada y sale con 2, con la lista: añádelos, apártalos
  (`git stash -u`) o ensaya una exportación del índice (`git checkout-index -a --prefix=<carpeta>/`), que se ensaya tal cual.»
- «La primera línea y la última dicen sobre qué se ensayó (el commit, el árbol del índice o una carpeta sin `.git`);
  `ENSAYO.json` lo guarda en `clon`. La carpeta de trabajo va fuera del clon.»
- «Códigos: 0, todo como se esperaba; 1, algún job no; 2, no se ensayó.»
- «Lo que el ensayo no ve: lo de siempre (GitHub de verdad, la red, Docker del runner, los permisos del token, el commit de
  fusión de un PR) y, además, si el commit fijado está ya en GitHub.»

En `verificador/README.md`, la frase de la línea 448 («Un ensayo local antes del primer push: `cv/ci/ensayo_flujo.py` corre
en una máquina los pasos…») añade «…y emula los checkouts con lo que se publica (el índice del clon); con cambios sin `git
add` no ensaya», y la lista de la 413 («ahora con la forma remota, los checkouts por commit, el `if:`…») añade «y, desde la
etapa 34, el índice como lo que se publica».

## 7. Los riesgos

**Lo que el arreglo puede romper en los flujos que ya están en verde** (los YAML no cambian; lo único que corre en GitHub y
cambia es el job `pruebas`):
- las `P-EN` levantan repositorios de git y corren bash y tar en el runner: si el runner tuviera una configuración global
  de git que estorbe (firma, plantillas de hooks), fallarían ahí y no en la máquina del laboratorio; por eso cada orden lleva
  sus `-c` y ninguna depende de `HOME`;
- `prueba_ci.py` corre también dentro del ensayo local (job `pruebas`): las `P-EN` ejecutan el ensayo dentro del ensayo, en
  carpetas de `tempfile`, nunca en el clon; si una dejara basura en el clon, la guarda del ensayo siguiente pararía (lo
  vería, no lo esconde);
- `sellar_prevision_*.py` leen `ENSAYO.json`: se conservan las claves y el orden, solo se añade `clon`;
- el checkout sin `ref` pasa de copiar el árbol a `git archive HEAD`: en el clon limpio de hoy no hay ignorados fuera de
  `__pycache__`, pero `verificador/bases_oru/` está ignorada y la regenera `bases_oru.py`; si en la máquina existiera, hoy
  se copiaría y con el arreglo no. El control negativo lo mide; si se ve, se explica;
- los mtimes de los ficheros del checkout sin `ref` pasan a ser los del commit: no deberían llegar a ningún informe, pero no
  se ha comprobado en este diseño; el control negativo lo mide;
- un ensayo con la carpeta de trabajo dentro del clon dejaría ficheros sin seguimiento y el ensayo siguiente pararía: la
  guía lo dice, y el mensaje de parada lista las rutas.

**Lo que el ensayo no puede ver aunque se arregle:**
- si el commit que fija el ejemplo está en GitHub (Q-EN-5 lo acerca con la referencia local de `origin/main`, que puede
  estar atrasada sin red); si `HEAD` o el índice llegan a publicarse tal cual (un `commit --amend` o un `add` posterior al
  ensayo lo cambian: el ensayo da verde sobre el índice de ese momento, y `ENSAYO.json["clon"]` deja el árbol para
  compararlo con `git rev-parse <commit publicado>^{tree}` después del push, que es la comprobación que cierra el círculo);
- el valor real de `github.sha` (el ensayo pone el árbol del índice cuando no hay commit; lo único que lo mira en los flujos
  es la comprobación de 40 hex);
- si una carpeta sin `.git` es de verdad una exportación del índice;
- que lo que está en el índice del clon es lo que el laboratorio quería copiar desde su carpeta de trabajo (`fase12/` →
  `verificador/`): el ensayo mira el clon, no el laboratorio;
- si alguien añadiera `.gitattributes` con `export-ignore`, `git archive` lo aplicaría y el checkout de GitHub no: hoy no
  hay ninguno;
- todo lo que el docstring ya lista: la evaluación de GitHub de verdad, la resolución remota, las salidas de un job llamado
  que falla, los permisos del token, el commit de fusión de un PR, y el Docker, el usuario y la red del runner.

**Mi estimación, aparte de la previsión que se sella:** que el control positivo deje de dar verde sobre lo viejo, muy
probable (0,95: es por construcción, salvo un error de código que las `P-EN` cazan). Que el control negativo dé lo mismo byte
a byte a la primera, probable pero no seguro (0,7): lo que puede fallar es lo que este diseño no pudo mirar (fechas en los
informes y mtimes), y está listado en §5 para apartarlo a la vista.
