# Etapa 24: las decisiones de Jev y las desviaciones del programador

El diseño es `diseno-ci2-fable.md` (Fable, a ciegas). Las cinco preguntas de su §11 se pasaron a Jev con un estado neutro
(`estado_qci2.md`, `preguntas_qci2.json`); la respuesta está en `decision-jev-qci2.md`. Las cinco coinciden con la
recomendación del diseñador.

## Las decisiones (Q-CI2-D)

| Pregunta | Jev | Confianza | Qué cambia |
|---|---|---|---|
| Q-CI2-D-1, `pull_request` | **un PR desde una rama del propio repositorio**, con el commit del resultado, llevado a `main` por avance rápido | 0,72 | §6 tal cual |
| Q-CI2-D-2, dónde vive el ejemplo | **`ejemplo-ci/` en la raíz** | 0,40 | la higiene admite la carpeta |
| Q-CI2-D-3, el defecto del rojo | **`F` sale como `male`**, un valor distinto en PID-8 | 0,89 | `DEFECTO.json` |
| Q-CI2-D-4, qué decide en el rojo | **el artefacto descargado**; las salidas se anotan | 0,86 | `comprobar_rojo.py` |
| Q-CI2-D-5, las entradas sin recorrer | **una segunda llamada,** `ejemplo-propio` | 0,98 | `ejemplo-ci.yml` |

## Las desviaciones (DV-CI2-n)

- **DV-CI2-1, dónde viven los documentos.** El encargo y el diseño se dejaron primero en `cv/ci2/` y se movieron a `cv/ci/`, como
  pide el diseño. `cv/ci2/` guarda solo los guiones de una sola vez del laboratorio (la preparación de la publicación y los
  parches), que no se publican.
- **DV-CI2-2, el proyecto de ejemplo en el laboratorio y el sello.** En el repositorio público `ejemplo-ci/` está en la raíz; en
  el árbol del laboratorio, que es el de `verificador/`, está en `ejemplo-ci/` dentro de ese árbol.
  - **Las rutas del sello:** las del diseño (`../../../ejemplo-ci/…`) no resolverían en los dos sitios. `SELLO-CI2.txt` las
    escribe como `@ejemplo-ci/…`, y `sellar_prevision_ci2.py` las resuelve donde esté la carpeta.
  - **La higiene:** el diseño sellaba `../../../.github/workflows/higiene.yml`, que no existe en el laboratorio. Se sella su
    plantilla, `github-ci2/higiene.yml`, y P-CI-26 exige que la que corre sea igual byte a byte.
- **DV-CI2-3, los YAML que leen P-CI-1..15.** `yaml_dir()` busca primero `.github/workflows/`, después las plantillas de la 24
  (`github-ci2/`) y por último las de la 23 (`github/`). En el rojo, P-CI-1..15 siguieron leyendo los YAML de la 23 y pasando;
  P-CI-16..26 fallaban por la razón prevista.
- **DV-CI2-4, `comprobar_ejemplo.py` no fija 349 casos.** Comprueba que el veredicto cubre todos los casos de su base y que el
  corpus del informe, sin contar los ceros, es el de la base. Así las pruebas P-CI-26 pueden usar bases sintéticas pequeñas.
- **DV-CI2-5, el README del ejemplo enlaza las plantillas.** `.github/workflows/ejemplo-ci.yml` y `rojo-ci.yml` no existen hasta
  el segundo push, y la higiene exige que los enlaces resuelvan. `ejemplo-ci/README.md` y `CI.md` nombran los ficheros que
  corren y enlazan sus plantillas de `github-ci2/`.
- **DV-CI2-6, las etiquetas de las acciones.** El diseño ponía `# v4.2.2` como ejemplo. Las etiquetas mayores apuntan hoy a
  `v4.4.0` (checkout), `v5.6.0` (setup-python), `v4.6.2` (upload-artifact) y `v4.3.0` (download-artifact), cruzadas con la API
  (`ACCIONES-CI.json`).
- **DV-CI2-7, el sello de la 23 deja de verificar dos ficheros.** La etapa 24 amplía `prueba_ci.py` y `ensayo_flujo.py`, que
  `SELLO-CI.txt` sellaba. Sus versiones selladas están en el historial del repositorio público (`0f85437`); el sello de la 23 no
  se toca (S-CI2-16), y el de la 24 sella las versiones nuevas. `RESULTADO-CI.md` lo dice junto a su referencia al sello.
- **DV-CI2-8, dos fallos del ensayo, arreglados antes de sellar.**
  - **El `if:` implícito.** No aplicaba la regla de GitHub de que un `if:` sin función de estado lleva delante `success() &&`, y
    corría un paso después de otro fallido.
  - **El `github.sha`.** Valía `ensayo`, y la demo endurecida lo pasa como `laboratorio_ref`, que ahora exige 40 hex. Vale el
    `HEAD` del repositorio si hay `.git`, y si no, un commit de 40 hex que no está.
- **DV-CI2-9, la revisión a ciegas de C1, y un segundo sello antes del primer push.** La revisión aprobó, con hallazgos menores.
  - **Fuera de lo pedido, el revisor corrió el job `real` con Docker y red.** El ensayo añadía por su cuenta todo job cuyas
    dependencias estuvieran corridas, y `real` solo depende de `pruebas`. Ahora solo añade los jobs de comprobación, los que no
    llaman al flujo. Corrió en una carpeta temporal y con la caja de siempre, y el clon no se tocó.
  - **Los teléfonos de dos mensajes del ejemplo tenían forma de móvil real.** Pasan a `+34000000001` y `+34000000003`, que no se
    pueden asignar. Las dos bases se rehicieron con `hacer_base.sh` y dieron lo mismo: 349 y 6 casos, y el defecto en 164.
  - **Textos que hablaban en presente de los flujos del segundo push,** en `CI.md` y los README: ahora dicen que llegan en el
    segundo push. `ejemplo-ci/README.md` va sellado y se deja: lo que dice es cierto desde el segundo push.
  - **La receta para copiar el ejemplo** dice ahora qué hay que cambiar en `hacer_base.sh`, y que corre desde un clon del
    laboratorio. `CI.md` dice que `read -ra` cambia la partición de `corpus` y `opciones`.
  - **El sello:** el primero (el commit `3c0b9c2` del laboratorio, no publicado) cubría el corpus con los teléfonos y el ensayo sin
    el arreglo. Sus huellas: `SELLO-CI2.txt` `b953eb39…` y `PREVISION-CI2.json` `96562759…`. Se volvió a sellar con las mismas
    cifras; los dos sellos son anteriores al primer push.
  - **La segunda pasada aprobó,** con dos hallazgos bajos, arreglados en `CI.md` y aquí.
- **DV-CI2-10, P-CI-27 llega en el segundo push,** como pide el diseño: en rojo en el clon antes de escribir los dos YAML.
  `SELLO-CI2.txt` deja entonces de verificar `prueba_ci.py`; la versión sellada es la del primer push.
- **DV-CI2-11, el comentario del job `pruebas` en `demo-ci.yml`** dice «P-CI-1..27» desde el primer push, en el que hay 26. Va
  sellado y se deja.
- **DV-CI2-12, la revisión del segundo push.** Aprobó con tres hallazgos sin bloqueo:
  - **el control de P-CI-27 no la ejercitaba:** su lógica pasó a `comprobar_vivos()`, con cuatro controles sobre copias
    temporales, antes del push;
  - **relanzar solo `ejemplo-comprobado` buscaría el artefacto del intento nuevo:** se declara en `CI.md` y en el resultado;
  - **`rojo-comprobado` corre también si la corrida se cancela:** se declara. `!cancelled()` habría exigido volver a sellar la
    plantilla.
- **DV-CI2-13, el resumen en la página no se vio.** El diseño pedía mirarlo a mano. GitHub no enseña los resúmenes de los jobs a
  un visitante sin sesión, y la sesión es del autor: no se inició. Lo comprobado es el fichero que se vuelca y la mecánica que lo
  copia.
- **DV-CI2-14, la corrida de `demo-ci` en `C2`** va aparte, en `CORRIDA-CI2-2-demo.json`, porque el diseño numeraba una corrida
  por push y en `C2` corrieron dos flujos.
- **DV-CI2-15, sin un quinto commit.** El diseño traía las corridas de `main` en el commit publicado a un `CORRIDA-CI2-5.json`, en un
  push más. Ese commit es el último de la rama del PR, que ya corrió en el PR. Las corridas de `main` quedan en la pestaña Actions
  y en el laboratorio, sin otro ciclo de publicación.
- **DV-CI2-16, la higiene admite `CORRIDA-CI2-4.json` un commit antes de que exista:** lo trae el commit del PR.
- **DV-CI2-17, la revisión del commit del resultado** aprobó, con matices arreglados antes de empujar la rama:
  - las filas del PR y de los pushes en la tabla de la previsión, como pendientes;
  - dos límites que faltaban, L-CI2-4 y L-CI2-11;
  - cuatro frases.
