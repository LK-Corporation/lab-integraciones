# Resultado de la etapa 24: lo abierto de la integración continua

**Llamado como lo llamaría un tercero, por referencia remota fijada a un commit y con su adaptador, su base y su corpus, el flujo
pasa cuando no hay nada nuevo y pone el cambio en rojo, con su resumen, cuando aparece un hallazgo nuevo.**

En GitHub Actions, y a la primera:
- **El proyecto de ejemplo** ([`../ejemplo-ci/`](../ejemplo-ci/)) llamó al flujo por la forma remota. Sus dos llamadas pasaron y
  su comprobación de fuera salió en verde.
- **El run en rojo a propósito** falló solo en el paso de la comparación, por el hallazgo sembrado, en 164 casos. Su
  comprobación de fuera salió en verde.
- **La demostración endurecida** siguió en verde, con los mismos informes byte a byte que en la etapa 23.

La pregunta, fijada antes de medir en [`ANTES-ETAPA-CI2.md`](ANTES-ETAPA-CI2.md):

> Llamado como lo llamaría un tercero (por referencia remota fijada a un commit, con su adaptador, su línea base y su corpus, en
> el modo `pasa`), ¿pasa el flujo cuando no hay nada nuevo y pone el cambio en rojo, con su resumen, cuando aparece un hallazgo
> nuevo? ¿Y aguanta las cuatro observaciones de endurecimiento de la revisión a ciegas de la etapa 23?

## Los cuatro endurecimientos

| Endurecimiento | Qué cambió | Su prueba | Lo que rompe |
|---|---|---|---|
| Las entradas, por variables de entorno | cada paso `run:` declara en `env:` lo que usa; ningún `run:` de los flujos que corren ni de las plantillas lleva `${{ }}` | P-CI-16 y P-CI-19 | `corpus` y `opciones` se parten con `read -ra`, sin comillas ni comodines |
| Las acciones, por commit | las cuatro, fijadas al commit de su etiqueta mayor el 26-oct, cruzado con la API ([`cv/ci/ACCIONES-CI.json`](cv/ci/ACCIONES-CI.json)) | P-CI-17 | nada: es el código que ya corría |
| `laboratorio_ref`, obligatoria y de 40 hex | sin valor por omisión; «Entradas» sale con 2 ante una rama o una etiqueta | P-CI-18 | quien la omitía corría `main` sin saberlo y ahora su llamada no arranca; está dicho en [`cv/ci/CI.md`](cv/ci/CI.md) |
| La demo, en un fork | `laboratorio: ${{ github.repository }}` | P-CI-20 | nada |

## La forma remota

El primer push de la etapa (`C1`, `5183b4e`) publicó el flujo endurecido. El segundo (`C2`, `7a44e27`) publicó
`.github/workflows/ejemplo-ci.yml` y `rojo-ci.yml`. Los dos llaman a
`LK-Corporation/lab-integraciones/.github/workflows/verificador-conversor.yml@5183b4e…` con `laboratorio_ref` igual. En el runner,
`proyecto/` es el repositorio en `C2` y `lab/` el laboratorio en `C1`: dos commits distintos, como en una llamada de tercero.

La corrida es la del push de `C2`: [`ejemplo-ci` n.º 1](https://github.com/LK-Corporation/lab-integraciones/actions/runs/41136715322),
en [`cv/ci/CORRIDA-CI2-2.json`](cv/ci/CORRIDA-CI2-2.json).

| Job | Qué espera | Qué dio | Minutos |
|---|---|---|---|
| `ejemplo` | el corpus del laboratorio más el propio contra su base, `pasa` | pasa: 0 nuevos y 0 arreglos en 349 casos, sin avisos | 0,2 |
| `ejemplo-propio` | solo el corpus propio (`sin_corpus_lab`), `--json-solo`, `artefacto_completo` | pasa: 0 nuevos en 6 casos; sin `INFORME.md`; con evidencias y los seis mensajes en el artefacto | 0,2 |
| `ejemplo-comprobado` | descarga los dos artefactos y los juzga desde fuera | las 26 comprobaciones de [`cv/ci/comprobar_ejemplo.py`](cv/ci/comprobar_ejemplo.py), ciertas | 0,1 |

Las identidades de los dos artefactos son las de las bases:
- el conversor del ejemplo, `af1f387d…`;
- la imagen `python:3.12-slim` por su digest, `sha256:a0f57064…`;
- el juez publicado, `b3f00f6a…`.

Cada entrada hizo lo que debía y nada más: `sin_corpus_lab` quitó el corpus del laboratorio, `--json-solo` quitó `INFORME.md` y
`artefacto_completo` añadió las evidencias y el corpus.

## El run en rojo

A mano, sobre `C2`: [`rojo-ci` n.º 1](https://github.com/LK-Corporation/lab-integraciones/actions/runs/41136916498), en
[`cv/ci/CORRIDA-CI2-3.json`](cv/ci/CORRIDA-CI2-3.json).
- **El job `rojo` falló, y solo en «Veredicto frente a la linea base»,** con el código 10. El defecto de
  [`../ejemplo-ci/ci/DEFECTO.json`](../ejemplo-ci/ci/DEFECTO.json) (`F` sale como `male`) se sembró en `preparar`, sobre la copia
  del conversor, y la comparación en el modo `pasa` dio `("PID-8", "fidelidad", "valor_distinto")` en 164 casos, todos de la base.
- **`rojo-comprobado` salió en verde,** con las 11 comprobaciones de [`cv/ci/comprobar_rojo.py`](cv/ci/comprobar_rojo.py) ciertas:
  - el job falló;
  - el artefacto lleva su veredicto;
  - se esperaba `pasa`;
  - el único motivo fue `hallazgo_nuevo`;
  - el hallazgo es el sembrado y ningún otro, en casos de la base;
  - solo cambió el conversor;
  - `VEREDICTO-CI.md`, el texto que el paso vuelca en el resumen, lleva su cabecera de **FALLA** y sus hallazgos nuevos;
  - el informe y la propuesta están, y la propuesta recoge lo nuevo;
  - las salidas cuadran.
- **Las salidas de un job llamado que falla sí llegan al job siguiente:** `resultado` falla, 164 nuevos y el triple.
- **La corrida queda en rojo**, porque un job que llama a un flujo reutilizable no admite `continue-on-error`. Tiene que estarlo.

## `pull_request`

El PR que trajo este documento, [LK-Corporation/lab-integraciones#1](https://github.com/LK-Corporation/lab-integraciones/pull/1),
recorrió el evento desde una rama del propio repositorio. Se integra en `main` por avance rápido, sin commit de fusión.
- **`demo-ci` y `ejemplo-ci` salieron en verde a la primera** con el evento `pull_request`:
  [`demo-ci`](https://github.com/LK-Corporation/lab-integraciones/actions/runs/41141069854) y
  [`ejemplo-ci`](https://github.com/LK-Corporation/lab-integraciones/actions/runs/41141069947), en
  [`cv/ci/CORRIDA-CI2-4-demo.json`](cv/ci/CORRIDA-CI2-4-demo.json) y [`cv/ci/CORRIDA-CI2-4.json`](cv/ci/CORRIDA-CI2-4.json).
  - En un PR, `github.sha` es el commit de fusión que crea GitHub, y la demo lo pasa como `laboratorio_ref`. El checkout del
    laboratorio en ese commit funcionó.
  - Los tres `INFORME.json` de la demo salieron iguales a los de la etapa 23.
- **La higiene falló,** y por algo que nunca se había recorrido: el repositorio no había tenido ningún PR.
  - En un `pull_request`, el checkout es ese commit de fusión sintético. Su committer es el correo genérico «noreply» de GitHub,
    y la prueba de correos solo admite los `@users.noreply.github.com`.
  - No había fuga. El commit siguiente de la rama arregló la prueba. Exime ese committer, y solo ese, solo cuando HEAD es el
    commit de fusión del PR: `GITHUB_SHA`, con la cabeza del PR del evento como segundo padre. El autor de la fusión se sigue
    mirando.
  - El arreglo se probó en el laboratorio con una fusión hecha como la de GitHub. La fusión pasa, y fallan los cinco controles:
    - la misma fusión fuera de un PR;
    - otro `GITHUB_SHA`;
    - un autor real en la fusión;
    - un correo real dentro de la rama;
    - el texto sin el arreglo.
  - La corrida de ese commit quedó en el PR.
  - En los dos JSON, `commit` es la cabeza del PR (`6a2199b`), que es lo que da GitHub. El checkout fue el commit de fusión,
    `2c881db`.

## Lo que no se rompe

Los tres controles de la etapa 23 siguieron en verde en cada corrida de `demo-ci` de la etapa. En cada una, el `INFORME.json` de los
tres salió igual byte a byte al de la corrida 1 de la etapa 23 (`igual_a_la_corrida_1`):
- en `C1`: [`demo-ci` en `5183b4e`](https://github.com/LK-Corporation/lab-integraciones/actions/runs/40321059680),
  [`cv/ci/CORRIDA-CI2-1.json`](cv/ci/CORRIDA-CI2-1.json);
- en `C2`: [`demo-ci` en `7a44e27`](https://github.com/LK-Corporation/lab-integraciones/actions/runs/41136715185),
  [`cv/ci/CORRIDA-CI2-2-demo.json`](cv/ci/CORRIDA-CI2-2-demo.json);
- en el PR: [`demo-ci` en el commit de fusión](https://github.com/LK-Corporation/lab-integraciones/actions/runs/41141069854),
  [`cv/ci/CORRIDA-CI2-4-demo.json`](cv/ci/CORRIDA-CI2-4-demo.json).

## Lo que cuesta

| Corrida | Minutos de reloj |
|---|---|
| `demo-ci` en `C1` / en `C2` / en el PR | 1,5 / 1,3 / 1,5 |
| `ejemplo-ci` en el PR | 0,5 |
| `ejemplo-ci` | 0,4 |
| `rojo-ci` | 0,5 |

## La previsión, frente a lo que salió

La previsión se selló antes del primer push: [`cv/ci/PREVISION-CI2.md`](cv/ci/PREVISION-CI2.md) y
[`cv/ci/SELLO-CI2.txt`](cv/ci/SELLO-CI2.txt).

| | Programador | Jev | Salió |
|---|---|---|---|
| La demo en verde en el primer push | 0,85 | 0,88 | **sí** |
| Con los mismos informes | 0,97 | — | **sí, byte a byte** |
| El ejemplo en verde a la primera | 0,6 | 0,87 | **sí** |
| El rojo como se espera a la primera | 0,6 | 0,88 | **sí** |
| Las salidas del job fallido llegan | 0,6 | 0,7 | **sí** |
| Casos con el hallazgo sembrado | 164 | — | **164** |
| Minutos por corrida del ejemplo y del rojo | 1 a 4 | — | **0,4 y 0,5**, por debajo |
| Todo en una sesión | 0,65 | — | **no**: dos paradas ajenas a la etapa la partieron en tres sesiones |
| El PR en verde a la primera (`demo-ci` y `ejemplo-ci`) | 0,55 | — | **sí**; la higiene, no |
| Pushes hasta cerrar la etapa | 4 a 7; lo más probable, 5 | cuatro o menos, 0,87 | **5** al repositorio; **4** contando la rama y el avance rápido como uno, la regla de la tabla de la previsión del diseño (§10 de [`cv/ci/diseno-ci2-fable.md`](cv/ci/diseno-ci2-fable.md)). Sin el quinto commit del diseño (DV-CI2-15): con él, habrían sido 5 |

Jev acertó más que el programador en todas las filas que los dos previeron. De las siete causas de fallo previstas no apareció
ninguna, tampoco la del commit de fusión del PR. Lo que falló no estaba en la lista: la prueba de correos de la higiene ante el
commit de fusión sintético.

## Antes del primer push

- **Con el ensayo local arreglado** (dos fallos del propio ensayo, DV-CI2-8 en
  [`cv/ci/decisiones-qci2.md`](cv/ci/decisiones-qci2.md)), los tres flujos salieron en verde en la máquina del laboratorio.
- **La revisión a ciegas del primer push aprobó en dos pasadas,** con hallazgos menores, y se volvió a sellar la previsión con
  las mismas cifras (DV-CI2-9). Entre ellos:
  - los teléfonos de dos mensajes del ejemplo, que tenían forma de móvil real;
  - textos en presente sobre flujos del segundo push.
- **La del segundo push aprobó** y pidió que el control de P-CI-27 ejercitara la prueba de verdad: se arregló antes del push.

## Lo que no dice

- **La forma remota se recorrió desde el propio repositorio del laboratorio:** el mismo dueño y el mismo token de solo lectura.
  Un tercero en otra organización, un repositorio privado o un PR desde un fork, con el token restringido, quedan sin recorrer
  (L-CI2-1).
- **El resumen en la página del job no se pudo ver desde fuera:** GitHub no se lo enseña a un visitante sin sesión. Lo que se
  comprobó es el fichero que el paso vuelca (`VEREDICTO-CI.md`, en el artefacto) y la mecánica que lo copia (P-CI-15, en el
  job `pruebas` del runner) (L-CI2-3).
- **El conversor del ejemplo es de juguete** (Python puro, unas 250 líneas). Dice cómo se llama al flujo, no nada sobre
  conversores reales. «Las dos llamadas pasaron» quiere decir que no hubo nada nuevo frente a su base, no que convierta bien: en su
  base, 3 de los 349 casos son `correcto`. El digest de su imagen envejece como los commits de las acciones (L-CI2-4).
- **`preparar` sigue sin aislarse:** corre la orden del proyecto, con red, en el runner (L-CI2-11, L-CI-10).
- **Un solo tipo de defecto en el rojo** (un valor distinto en PID-8), más el dato perdido de la etapa 23 en el positivo
  (L-CI2-5).
- **Las acciones fijadas por commit no se actualizan solas** (L-CI2-8). GitHub ya avisa de que las cuatro corren en Node.js 20 y
  las fuerza a Node.js 24. `ubuntu-latest` pasa a Ubuntu 26 desde el 19-oct-2026. Subirlas es un commit con
  `ACCIONES-CI.json` al día.
- **Relanzar solo el job de comprobación no funciona:** busca el artefacto del intento nuevo, y el job que lo sube no se relanzó.
  Hay que relanzar todos los jobs. `rojo-comprobado` corre también si la corrida se cancela, y entonces falla.
- **El ejemplo se queda fijado a `5183b4e`** hasta que un commit suba el pin, en dos pushes, como le pasaría a cualquier tercero
  (L-CI2-12).

## Cómo repetirlo

- **En GitHub:** `ejemplo-ci` corre en cada push a `main` que toque `ejemplo-ci/**`, `.github/workflows/**` o `verificador/**`, y
  a mano. `rojo-ci` solo corre a mano, con «Run workflow».
- **En una máquina:**
  - `bash ejemplo-ci/ci/hacer_base.sh <artefactos vacíos> <trabajo vacío>`, desde la raíz, rehace las bases y el defecto;
  - `python3 cv/ci/ensayo_flujo.py <repositorio> <trabajo vacío> ejemplo,ejemplo-propio --flujo ejemplo-ci`, desde `verificador/`,
    y lo mismo con `rojo --flujo rojo-ci --rojo rojo`, ensaya los flujos.
- **Los commits de las acciones:** `git ls-remote --tags https://github.com/actions/checkout | grep 11d5960a`, y lo mismo con las
  otras tres, tienen que listar la etiqueta de `ACCIONES-CI.json`.

## Los documentos de la etapa

El índice está en la sección de la etapa 24 de [`README.md`](README.md).
