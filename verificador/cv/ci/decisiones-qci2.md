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
