# RESULTADO de la etapa 34: el ensayo local que ensaya lo que se publica (7-nov-2026)

> **Con el índice distinto del commit que emula, el ensayo ya no da verde sobre lo viejo; cuando coinciden, da lo mismo que
> antes, informe a informe.**
>
> - En el estado de la etapa 33 (el HEAD en el commit publicado y la etapa nueva en el índice), el ensayo de antes sacaba el
>   laboratorio del HEAD y daba verde con la herramienta y las bases viejas. El arreglado saca el árbol del índice, y su informe
>   es el mismo que da el ensayo de antes sobre un clon limpio del commit que se publicó después.
> - En un clon limpio y en su exportación sin `.git`, los tres flujos dan los mismos trabajos, veredictos, salidas e informes
>   que antes. Cambian la fecha y los tiempos de `CORRIDA.json`, que cambian entre dos corridas cualesquiera, y lo que se
>   enumera abajo.
> - Con cambios sin `git add` o ficheros sin seguimiento, el ensayo no ensaya nada y sale con 2, con la lista.

La pregunta, fijada antes de diseñar, está en [`ANTES-ETAPA-ENSAYO.md`](ANTES-ETAPA-ENSAYO.md).

## Cómo se hizo

| | |
|---|---|
| El porqué | Lo medido en la etapa 33: el ensayo dio verde sobre el commit ya publicado, con la etapa nueva en el índice |
| El diseño | Fable, a ciegas de los resultados ([`en/diseno-en-fable.md`](en/diseno-en-fable.md); encargo en [`en/encargo-diseno-en.md`](en/encargo-diseno-en.md)). Conocía el caso de la 33, que cuenta el ANTES |
| Las decisiones | Jev, ocho (`Q-EN-1` a `8`): [`en/decision-jev-en.md`](en/decision-jev-en.md), con su estado [`en/estado_en.md`](en/estado_en.md) |
| Las pruebas, en rojo antes | `P-EN-1` a `8`, en [`cv/ci/prueba_ci.py`](cv/ci/prueba_ci.py): 21 comprobaciones en rojo con el ensayo de antes ([`en/ROJO-EN.txt`](en/ROJO-EN.txt)). `P-EN-9` y `10`, tras la revisión, en rojo con el arreglo de antes de DV-EN-3 ([`en/ROJO-EN-2.txt`](en/ROJO-EN-2.txt)) |
| La previsión | Sellada antes de correr los controles con el arreglo: [`en/PREVISION-EN.json`](en/PREVISION-EN.json), con las huellas del arreglo, las pruebas y el guion de los controles |
| Los controles | [`en/controles_en.sh`](en/controles_en.sh): 15 corridas del ensayo, todas con 0 ([`en/CODIGOS-EN.txt`](en/CODIGOS-EN.txt)); lo comparado, en [`en/CONTROLES-EN.json`](en/CONTROLES-EN.json). Repetidas con la versión final, tras DV-EN-3: lo mismo ([`en/CODIGOS-EN-2.txt`](en/CODIGOS-EN-2.txt) y [`en/CONTROLES-EN-2.json`](en/CONTROLES-EN-2.json)) |

## Lo que cambia en el ensayo

[`cv/ci/ensayo_flujo.py`](cv/ci/ensayo_flujo.py) mira el estado del clon una vez, al empezar, y emula cada checkout con lo que se
publica.

| El checkout | Con `.git` | Sin `.git` |
|---|---|---|
| Sin `ref`, o con `github.sha` | `git archive` del árbol del índice (`git write-tree` sobre una copia del índice, que no se toca), o del HEAD si coinciden | La carpeta, copiada como antes |
| Con un commit de 40 hex que está en el clon (el del ejemplo y el rojo) | `git archive` de ese commit, como antes | La carpeta, con un aviso: el commit no se puede resolver |
| Con un `ref` que no está | El árbol del índice, con un aviso | La carpeta, con el mismo aviso |

- **`github.sha`** es el HEAD si el índice coincide con él; si no, el id del árbol del índice, que no es un commit; sin `.git`,
  el marcador de antes.
- **Con cambios sin `git add` o ficheros sin seguimiento,** no ensaya nada y sale con 2, con la lista de rutas. Los ignorados no
  paran y no entran en el checkout.
- **La primera línea y la última dicen sobre qué se ensayó.** `ENSAYO.json` conserva sus seis claves, en orden, y añade `clon`.
- **Los códigos:**
  - 0, todo como se esperaba;
  - 1, algún job no, o un error del propio ensayo o de git al mirar el clon;
  - 2, no se ensayó por el estado del clon: cambios sin `git add`, ficheros sin seguimiento o un HEAD sin commit.
- **La guía,** [`cv/ci/CI.md`](cv/ci/CI.md), lleva una sección nueva: «Antes de cada push: el ensayo local».

Las decisiones de Jev fueron las recomendadas por el diseño salvo una: con un commit fijado que está en el clon pero no en
`origin/main`, el ensayo no hace nada, como antes (`Q-EN-5`, 0,61). Lo dice la guía entre lo que el ensayo no ve.

El estado de `Q-EN-4` daba por hecho que ningún informe comparado guarda `github.sha`, y entonces no estaba medido. Lo confirmó
el control positivo: los informes del triángulo coinciden con `github.sha` distinto.

## Las pruebas

Las diez levantan repositorios de git mínimos, sin Docker ni red, y corren en el trabajo `pruebas` de la demo. Cada repositorio
tiene tres ficheros (cuatro en P-EN-9), y P-EN-6 ensaya su exportación.

| Prueba | Qué monta | Con el ensayo de antes | Con el arreglo |
|---|---|---|---|
| P-EN-1 | El índice distinto del HEAD | El laboratorio sale del HEAD (`v1`) | Sale del índice (`v2`); `github.sha` es el árbol |
| P-EN-2 | Un cambio sin `git add`, y uno con parte añadida y parte no | Ensaya y da 0 | Sale con 2, sin correr ningún job |
| P-EN-3 | Un fichero sin seguimiento | Ensaya y lo copia | Sale con 2, con la lista |
| P-EN-4 | Un fichero ignorado | Lo copia | Ni para ni lo copia |
| P-EN-5 | Un clon limpio | El checkout sin `ref` copia el árbol | Sale del HEAD; lo demás, igual (control) |
| P-EN-6 | Una carpeta sin `.git` | Copia, sin aviso | Copia, con aviso para un `ref` de 40 hex |
| P-EN-7 | Un commit fijado con el índice distinto | Saca el commit fijado (control) | Igual; un `ref` que no está, con aviso |
| P-EN-8 | Las claves de `ENSAYO.json` | Las seis (control) | Las seis y `clon`; con 2, sin jobs |
| P-EN-9 | Un renombrado marcado con `git add -N` (git da la R en la segunda columna) | — | Sale con 2, sin rutas inventadas |
| P-EN-10 | Una rama huérfana | — | Sale con 2: «el HEAD no apunta a ningún commit» |

P-EN-9 y 10 llegaron con la revisión a ciegas. Con el arreglo de antes de DV-EN-3, P-EN-9 rompía con una excepción y P-EN-10 no
daba el mensaje. A P-EN-6 se le añadieron entonces dos comprobaciones: que el marcador de `github.sha` no avisa (DV-EN-1), y la
cabecera y la última línea sin `.git`, juntas. Las dos miran lo que el arreglo ya hacía y no tienen rojo previo.

Las cifras, en el repositorio publicado (`cd verificador && python3 cv/ci/prueba_ci.py`):
- **Antes del arreglo:** 21 comprobaciones en rojo y 171 en verde, de 192, con todos los controles en verde. El juego cuenta solo
  las que pasan.
- **Con el arreglo:** TODO BIEN, con 198 comprobaciones en 41 pruebas.
- **En el laboratorio** las mismas pruebas cuentan menos (164 y 191), porque P-CI-26 y 27 comprueban más cuando están los flujos
  de `.github/`.
- **Las de la herramienta** (`cv/prueba_vc.py`) siguen igual, con 154 en 26.

## Los controles

**El negativo:** un clon limpio del repositorio público en `74a6a99` y su exportación sin `.git`, con la demo (pruebas, negativo
y positivo), el proyecto de ejemplo y el run en rojo. Cada flujo se corrió con el ensayo de antes y con el arreglado, con la
misma carpeta de trabajo, y se comparó con `diff -r`. En los seis pares, los trabajos, lo esperado, las salidas de los jobs y
todos los informes (`INFORME.json`, `INFORME.md`, `juicio.jsonl`, `VEREDICTO-CI.*`, `LINEA-BASE-propuesta.json`, los
resúmenes y las comprobaciones de fuera) son iguales byte a byte. En las carpetas de trabajo, lo único que difiere:

| Qué | Dónde | Por qué |
|---|---|---|
| `fecha` y los tiempos (`total_s` y por caso) de `CORRIDA.json` | En los seis pares | Cambian entre dos corridas cualesquiera: también en la exportación, donde las dos versiones hacen lo mismo |
| La clave `clon` de `ENSAYO.json` | En los seis pares | Es nueva |
| Los `.pyc` del trabajo `pruebas` (31) | En el clon limpio, en la demo | Guardan la fecha de modificación de su fuente: `git archive` pone la del commit y la copia del árbol, la del disco. El resto de cada fichero es igual |
| Una carpeta `.runner` vacía en la carpeta de trabajo | En el clon limpio, en la demo | La deja la copia temporal del índice. En el ejemplo y el rojo ya estaba |

En `CORRIDA.json` se admitieron como fecha o duración 28 líneas en la primera tanda (16 de `fecha`, 2 de `total_s` y 10 de
tiempos por caso) y 18 en la segunda. No hubo ninguna otra línea distinta.

La salida del propio ensayo cambia solo donde lo pide el arreglo ([`en/SALIDAS-EN.txt`](en/SALIDAS-EN.txt)):
- la cabecera nueva y la última línea, que dicen sobre qué se ensayó;
- en el clon limpio, los checkouts sin `ref`, que pasan de «copia del árbol» a «git archive 74a6a99a3ba4»;
- en la exportación, el ejemplo y el rojo, con el aviso de que `54e8b9f` no se puede resolver sin `.git`.

**El positivo:** el estado de la etapa 33, con el HEAD en `371937c` y el índice y el árbol de trabajo en `54e8b9f`. Ninguna ruta
sin `git add` ni sin seguimiento.

| | Ensayo de antes, en ese estado | Ensayo arreglado, en ese estado | Ensayo de antes, en un clon limpio en `54e8b9f` |
|---|---|---|---|
| El laboratorio | `git archive 371937c9fb43` | Árbol del índice `c92b44f2f344` (el de `54e8b9f`) | `git archive 54e8b9f9017e` |
| `INFORME.json` de `negativo` | `1c8bf463…` | `5118717e…` | `5118717e…` |
| `INFORME.json` de `positivo` | `a385a852…` | `2ab260f6…` | `2ab260f6…` |
| Los cuatro trabajos | En verde | En verde | En verde |

El arreglo no cambia el color: cambia sobre qué se da.

**La segunda tanda,** con la versión final (tras DV-EN-3) y sobre un clon limpio nuevo en `74a6a99`, dio lo mismo:
- las 15 corridas, con 0;
- los mismos ficheros distintos en cada par;
- los mismos informes del control positivo.

## Lo que cuesta

Nada que se note. Por la hora de cada salida:
- **En la demo con `.git`,** el arreglado tarda unos 0,2 s más, en las dos tandas y siempre en el mismo sentido: en el clon limpio
  y en el estado de la 33.
- **En la exportación, el ejemplo y el rojo,** dura lo mismo, con 0,1 s arriba o abajo.
- **Las duraciones:** la demo tarda unos 8 s, el ejemplo de 5,35 a 5,81 s y el rojo de 3,4 a 3,6 s.
- **`write-tree` y `git archive` del árbol** tardan 0,05 s para 11 MB, según midió el diseñador.

## La previsión

| | Jev | El diseñador | Lo que pasó |
|---|---|---|---|
| El negativo da lo mismo, informe a informe, a la primera | Media, de 0,6 a 0,9 (confianza 0,92) | 0,7 | Sí |
| El positivo deja de dar verde sobre lo viejo | Alta, 0,9 o más (confianza 0,73) | 0,95 | Sí |

Las huellas de `PREVISION-EN.json` son las de lo sellado. El ensayo y sus pruebas cambiaron después, con DV-EN-3. Sus versiones
selladas, con esas huellas, están en [`en/sellada/`](en/sellada/).

## Las desviaciones del diseño (DV-EN-n)

- **DV-EN-1:** sin `.git`, el checkout cuyo `ref` es el marcador de `github.sha` no avisa. Lo pone el propio ensayo, y el
  laboratorio de la demo lo lleva. El diseño lo daba por un caso que no se da.
- **DV-EN-2:** las frases del README de las etapas 23 y 24 sobre el ensayo se quedan como están, porque cuentan su etapa. Lo nuevo
  lo dicen la sección de la 34 y la guía.
- **DV-EN-3, tras la revisión a ciegas:**
  - **El renombrado:** el origen se salta también cuando la R o la C van en la segunda columna, como con `git add -N`. Antes se
    leía como otra entrada: salía una ruta inventada o una excepción. Nunca daba verde, porque la entrada real ya paraba el
    ensayo.
  - **Un HEAD sin commit** se dice como es («un clon sin commits o una rama huérfana»). Antes decía «el clon no tiene commits»,
    también en una rama huérfana.
  - **Con P-EN-9 y 10 en rojo antes.** Los controles se repitieron con esta versión.

## Lo que el ensayo sigue sin ver

- Lo de siempre: GitHub de verdad, la red, el Docker del runner, los permisos del token y el commit de fusión de un PR.
- Si el commit fijado está ya en GitHub (`Q-EN-5`).
- Si lo ensayado llega a publicarse tal cual: un `git add` o un `commit --amend` posterior lo cambia. `ENSAYO.json` guarda el
  árbol, para compararlo con el del commit publicado.
- Si una carpeta sin `.git` es de verdad una exportación del índice. Y en una exportación, los commits fijados (el del ejemplo y
  el rojo) no se sacan: se ensaya la carpeta, con un aviso en la línea del checkout. Lo dice la guía.
- Los cambios en ficheros marcados con `skip-worktree` o `assume-unchanged`, que `git status` no enseña.

## Cómo se repite

Desde `verificador/`:
- `python3 cv/ci/prueba_ci.py` corre las pruebas, también las `P-EN`.
- `bash en/controles_en.sh <clon limpio en 74a6a99> <ensayo de antes> <ensayo arreglado> <carpeta vacía fuera del clon>` corre
  los controles. El ensayo de antes es `git show 74a6a99:verificador/cv/ci/ensayo_flujo.py`. El guion escribe `res/` con los
  registros, `CODIGOS.txt` y `CONTROLES-EN.json`, y necesita el Docker de la máquina. El clon tiene que estar limpio; si tiene
  algo en el índice, sirve uno nuevo con `git clone`.

## Ficheros

- **El ensayo, sus pruebas y la guía:** [`cv/ci/ensayo_flujo.py`](cv/ci/ensayo_flujo.py), [`cv/ci/prueba_ci.py`](cv/ci/prueba_ci.py)
  y [`cv/ci/CI.md`](cv/ci/CI.md).
- **Los parches que los cambiaron,** cada uno con su comprobación de texto: [`en/parche_prueba_en.py`](en/parche_prueba_en.py),
  [`en/parche_ensayo_en.py`](en/parche_ensayo_en.py), [`en/parche_guia_en.py`](en/parche_guia_en.py) y, tras la revisión,
  [`en/parche_prueba_en2.py`](en/parche_prueba_en2.py), [`en/parche_ensayo_en2.py`](en/parche_ensayo_en2.py) y
  [`en/parche_guia_en2.py`](en/parche_guia_en2.py). Aplicados en ese orden sobre los de `74a6a99`, dan los publicados.
- **El diseño, las decisiones, la previsión y los controles,** en [`en/`](en/).
