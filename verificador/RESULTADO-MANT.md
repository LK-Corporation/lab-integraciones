# Resultado de la etapa 25: el mantenimiento de la integración continua

**Con las acciones en Node.js 24 y el ejemplo fijado a su nuevo commit, los controles de las etapas 23 y 24 dan lo mismo, con los
mismos informes byte a byte, y sin el aviso de Node.js 20.**

En GitHub Actions, y a la primera:
- **La demostración** siguió en verde en los dos pushes. Sus tres `INFORME.json` salieron iguales byte a byte a los de la corrida
  1 de la etapa 23.
- **El proyecto de ejemplo** ([`../ejemplo-ci/`](../ejemplo-ci/)) siguió en verde con el flujo viejo y con el nuevo. Sus tres
  artefactos salieron iguales a los de la etapa 24.
- **El run en rojo a propósito** falló solo en el paso de la comparación, en los mismos 164 casos. Su comprobación de fuera
  salió en verde.
- **El aviso de Node.js 20 desapareció** de todos los jobs con las acciones nuevas, en las siete corridas medidas. Solo quedó en
  los dos jobs que aún llamaban al flujo viejo, y se fue al subir el pin.

La pregunta, fijada antes de medir en [`ANTES-ETAPA-MANT.md`](ANTES-ETAPA-MANT.md):

> Al subir las acciones de los flujos a versiones que corren en Node.js 24, y el pin del proyecto de ejemplo al commit que las
> trae, ¿siguen los controles de las etapas 23 y 24 dando lo mismo, con los mismos informes byte a byte, y sin el aviso de Node.js
> 20?

## Las versiones

Las cuatro acciones subieron a la **mayor mínima con Node.js 24**, que fue lo que eligió Jev frente a la última, la que
recomendaba el diseño ([`cv/ci/decisiones-qmant.md`](cv/ci/decisiones-qmant.md)). Están fijadas por commit, cruzadas con la API y
con su `action.yml`, en [`cv/ci/ACCIONES-CI.json`](cv/ci/ACCIONES-CI.json), con la anterior al lado.

| Acción | Antes | Ahora | Lo que sus notas cambian para estos flujos |
|---|---|---|---|
| `checkout` | v4.4.0, node20 | v5.1.0, node24 | Node.js 24 y un runner mínimo que los hospedados superan. `allow-unsafe-pr-checkout`, que v5.1.0 marca como cambio incompatible, ya venía en v4.4.0 y solo toca `pull_request_target` y `workflow_run`, que no se usan |
| `setup-python` | v5.6.0, node20 | v6.3.0, node24 | Node.js 24; entradas nuevas y cambios de caché que no se usan |
| `upload-artifact` | v4.6.2, node20 | v6.0.0, node24 | Node.js 24 |
| `download-artifact` | v4.3.0, node20 | v7.0.0, node24 | v5 cambia la ruta al bajar por id; aquí se baja por nombre, que no cambia. v6 trae un soporte preliminar y sigue en node20; v7, Node.js 24 |

Son 16 usos en los cinco flujos. Además, el checkout de la higiene ya no persiste las credenciales, como los demás.

Fueron dos pushes, porque un commit no puede llevar su propio hash:
- **El primero** (`M1`, `e704b97`) subió las acciones. El ejemplo siguió llamando al flujo de la etapa 24, `5183b4e`.
- **El segundo** (`M2`, `aa0b7fa`) subió el pin del ejemplo y su `laboratorio_ref` a `M1`.

## Lo que no cambia

Cada artefacto se comparó por huella con el de la corrida registrada en su etapa
([`cv/ci/traer_resultados_ci.py`](cv/ci/traer_resultados_ci.py) `--igual-a`).

| Control | Corridas | Igual a | Qué dio |
|---|---|---|---|
| La demo: `negativo`, `positivo` y `real` | [en `M1`](https://github.com/LK-Corporation/lab-integraciones/actions/runs/41155838459), [en `M2`](https://github.com/LK-Corporation/lab-integraciones/actions/runs/41157546381) | [`cv/ci/CORRIDA-CI-1.json`](cv/ci/CORRIDA-CI-1.json), de la 23 | los tres `INFORME.json`, iguales byte a byte (`e7c2e65d…`, `2f89fa13…` y `488ee643…`); seis jobs en verde |
| El ejemplo: `ejemplo`, `ejemplo-propio` y su comprobación | [en `M1`](https://github.com/LK-Corporation/lab-integraciones/actions/runs/41155838502), con el flujo viejo; [en `M2`](https://github.com/LK-Corporation/lab-integraciones/actions/runs/41157546469), con el nuevo | [`cv/ci/CORRIDA-CI2-2.json`](cv/ci/CORRIDA-CI2-2.json), de la 24 | `pasa` en 349 y 6 casos, con los informes iguales (`c99e7ba3…` y `7c1b37be…`); la comprobación de fuera, la misma |
| El rojo, a mano | [sobre `M2`](https://github.com/LK-Corporation/lab-integraciones/actions/runs/41157678311) | [`cv/ci/CORRIDA-CI2-3.json`](cv/ci/CORRIDA-CI2-3.json), de la 24 | `rojo` falló solo en «Veredicto frente a la linea base», con `PID-8` en 164 casos y el informe igual (`30ddf4a7…`); `rojo-comprobado`, en verde con la misma comprobación |
| La higiene | en `M1` y en `M2` | — | en verde |

Las corridas están en [`cv/ci/CORRIDA-MANT-1.json`](cv/ci/CORRIDA-MANT-1.json) y
[`cv/ci/CORRIDA-MANT-1-ejemplo.json`](cv/ci/CORRIDA-MANT-1-ejemplo.json) (`M1`), en
[`cv/ci/CORRIDA-MANT-2-demo.json`](cv/ci/CORRIDA-MANT-2-demo.json) y [`cv/ci/CORRIDA-MANT-2.json`](cv/ci/CORRIDA-MANT-2.json) (`M2`),
y en [`cv/ci/CORRIDA-MANT-3.json`](cv/ci/CORRIDA-MANT-3.json) (el rojo).

En `M1`, el ejemplo llamaba al flujo de la 24, con las acciones viejas. Su job propio, con `download-artifact` v7, bajó sin
problema lo que habían subido sus dos llamadas con `upload-artifact` v4.6.2.

## El aviso

El aviso no está en los artefactos ni en los campos de `gh run view --json`: está en las anotaciones de cada job, que
`gh run view` sí enseña en modo texto. Las lee por la API
[`cv/ci/anotaciones_ci.py`](cv/ci/anotaciones_ci.py), que busca «Node.js 20» o «node20», y el resultado está en
[`cv/ci/AVISOS-MANT.json`](cv/ci/AVISOS-MANT.json).

| Corrida | Jobs | Con el aviso |
|---|---|---|
| `demo-ci` en `M1` y en `M2` | 6 y 6 | ninguno |
| `higiene` en `M1` y en `M2` | 1 y 1 | ninguno |
| `ejemplo-ci` en `M1` | 3 | `ejemplo / verificar` y `ejemplo-propio / verificar`, admitidos: llamaban al flujo de `5183b4e` |
| `ejemplo-ci` en `M2` | 3 | ninguno |
| `rojo-ci` sobre `M2` | 2 | ninguno |

Hay dos controles de que el lector ve el aviso cuando está:
- [una corrida de `ejemplo-ci` de la 24](https://github.com/LK-Corporation/lab-integraciones/actions/runs/41136715322), con el aviso
  en sus tres jobs;
- los dos jobs admitidos de `M1`, que lo llevan con el texto de hoy: «Node.js 20 is deprecated…», seguido de los tres commits
  viejos.

Un job admitido vale solo en su corrida y tiene que llevar el aviso. La orden falla si falta medida: una corrida sin acabar, un
job que no acabó en `success` ni en `failure`, o ninguna corrida.

Cada job lleva además una nota de GitHub: la etiqueta `ubuntu-latest` pasa a Ubuntu 26. No es el aviso de Node.js y no cuenta.

## `pull_request`

El PR que trae este documento recorre el evento `pull_request` con las acciones nuevas. Sus corridas se anotan en el commit
siguiente de la rama.

## Lo que cuesta

| Corrida | Minutos de reloj |
|---|---|
| `demo-ci` en `M1` / en `M2` | 1,8 / 1,5 |
| `ejemplo-ci` en `M1` / en `M2` | 0,5 / 0,5 |
| `rojo-ci` | 0,6 |

En la 24 fueron 1,3 a 1,5 la demo, 0,4 a 0,5 el ejemplo y 0,5 el rojo.

## La previsión, frente a lo que salió

La previsión se selló antes del primer push: [`cv/ci/PREVISION-MANT.md`](cv/ci/PREVISION-MANT.md) y
[`cv/ci/SELLO-MANT.txt`](cv/ci/SELLO-MANT.txt).

| | Programador | Jev | Salió |
|---|---|---|---|
| La demo en verde en el primer push | 0,9 | 0,84 | **sí** |
| Con los mismos informes | 0,97 | — | **sí, byte a byte** |
| El ejemplo en verde a la primera tras subir su pin | 0,85 | 0,87 | **sí** |
| El rojo como se espera a la primera | 0,85 | — | **sí** |
| Sin el aviso de Node.js 20 donde debe desaparecer | 0,85 | 0,75 | **sí** |
| Casos con el hallazgo del rojo | 164 | — | **164** |
| Minutos: demo 1 a 2; ejemplo y rojo, 0,3 a 1 | — | — | **dentro:** 1,5 a 1,8; 0,5 y 0,6 |
| Las corridas del PR en verde a la primera | 0,8 | 0,74 | se anota con el PR |
| Todo en una sesión | 0,7 | — | se anota con el PR |
| Pushes | de 4 a 6; lo más probable, 4 | cuatro o menos, 0,98 | se anota con el PR |

De las causas de fallo previstas no apareció ninguna. Entre ellas estaban una acción nueva que no cargara en el runner,
Python 3.12 en Ubuntu 26 y `download-artifact` v7 bajando lo de v4.6.2.

## Antes del primer push

- **El ensayo local** dio los mismos informes en la demo, el ejemplo en verde y el rojo en rojo. El ensayo emula las acciones
  por su nombre, sin correr su código.
- **La revisión a ciegas del primer push aprobó en dos pasadas.**
  - La primera cruzó con la API los 16 usos, sus etiquetas y su Node, y leyó las notas de versión.
  - Encontró que el lector del aviso podía dar «sin aviso» por error por cuatro caminos:
    - un job admitido por nombre valía en todas las corridas;
    - no miraba si la corrida había acabado;
    - no leía más de 30 anotaciones;
    - con ninguna corrida, daba bien.
  - La segunda pasada encontró un quinto: un job cancelado contaba como medido.
  - Los cinco se arreglaron con su control en rojo antes. Fue después del sello y antes de cualquier push, y la previsión no
    cambió (DV-MANT-6 en [`cv/ci/decisiones-qmant.md`](cv/ci/decisiones-qmant.md)). `SELLO-MANT.txt` guarda las huellas de cuando
    se selló.
- **La revisión del segundo push aprobó** sin hallazgos.

## Lo que no dice

- **El ensayo no corre el código de las acciones** (L-MANT-1). Lo que cambia una versión se vio en el runner, con estos flujos y
  estas entradas. Otras entradas de las mismas acciones quedan sin recorrer.
- **Los commits fijados vuelven a envejecer desde hoy** (L-MANT-2). El próximo aviso de GitHub será otra etapa como esta, porque
  las acciones no se actualizan solas.
- **«Sin aviso» es un patrón sobre el texto de GitHub** (L-MANT-3). Los dos controles lo prueban contra el texto de octubre de
  2026. Son corridas pasadas, así que casarán mientras existan. Si GitHub cambia el texto, el patrón dejaría de verlo sin que esos
  controles lo noten. Una medida futura necesita un control del mismo momento: una corrida con una acción en Node.js 20, como los
  dos admitidos de `M1`.
- **Un tercero fijado a un commit anterior sigue con las acciones viejas** hasta que suba su pin (L-MANT-4), como el ejemplo en
  `M1`. Como el juez y el corpus no cambiaron, su base no se rehace.
- **`ubuntu-latest` ya es Ubuntu 26 y no se controla aparte** (L-MANT-5). Su nota sigue en cada job.
- **Los límites del diseño que dependían de las otras opciones no aplican:** el PR sí se recorre, la higiene no persiste el token
  y `download-artifact` es v7, no v8 (L-MANT-6..8).

## Cómo repetirlo

- **Los commits de las acciones:** `git ls-remote --tags https://github.com/actions/checkout | grep fbc6f399` tiene que listar
  `v5.1.0`. Lo mismo con `setup-python` (`ece7cb06`), `upload-artifact` (`b7c566a7`) y `download-artifact` (`37930b1c`).
- **El aviso**, desde `verificador/` y con `gh` autenticado:
  `python3 cv/ci/anotaciones_ci.py <run_id>[,…] -o <json> [--admitir "<run_id>:<job>"]… --control 41136715322`.
- **Lo que no cambia:** `python3 cv/ci/traer_resultados_ci.py <run_id> <trabajo nuevo> -o <json> --igual-a cv/ci/CORRIDA-CI-1.json`,
  o la corrida de referencia que toque.

## Los documentos de la etapa

El índice está en la sección de la etapa 25 de [`README.md`](README.md).
