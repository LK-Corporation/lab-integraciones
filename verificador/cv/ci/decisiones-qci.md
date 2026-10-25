# Etapa 23: las decisiones de Jev y las desviaciones del programador

El diseño es `diseno-ci-fable.md` (Fable, a ciegas). Las seis preguntas de su §10 se pasaron a Jev con un estado neutro
(`estado_qci.md`, `preguntas_qci.json`); la respuesta está en `decision-jev-qci.md`.

## Las decisiones (Q-CI-D)

| Pregunta | Jev | Confianza | Recomendación del diseñador | Qué cambia |
|---|---|---|---|---|
| Q-CI-D-1, un caso nuevo con hallazgos | **se lista**, no falla, y entra en la propuesta | 0,46 | que falle | `comparar` lo pone en `casos_nuevos` y no en `motivos`; con `esperar: igual` sí falla |
| Q-CI-D-2, un caso de la base que falta | **aviso**, y la propuesta lo quita | 0,61 | que falle | `casos_ausentes` va en `avisos`; con `igual` falla |
| Q-CI-D-3, el modo del control real | **lote en cada push; mensaje a mensaje, a mano** | 0,55 | solo lote | la demo tiene una entrada `modo_real` en `workflow_dispatch`, y hay una segunda base, `LINEA-BASE-linuxforhealth-mensaje.json` |
| Q-CI-D-4, otro juez | **aviso**, y la propuesta lleva `"juez_cambiado": true` | 0,51 | solo aviso | lo que salga nuevo sigue fallando |
| Q-CI-D-5, el artefacto | **sin evidencias ni corpus** | 0,97 | igual | `artefacto_completo: true` los añade |
| Q-CI-D-6, cuándo corre la demo | **push y PR con `paths`, y a mano** | 0,95 | igual | — |

**Lo que eso significa para quien lo use.** Con la opción por omisión, `esperar: pasa`, el flujo falla si un caso que ya estaba en
la base gana un hallazgo nuevo, y también si pierde su salida, si pasa a indeterminado o si la caja se rompe. No falla por un caso
que no estaba en la base, aunque traiga hallazgos (D-1): ese caso aparece en el resumen y entra en la propuesta, y el proyecto lo
acepta o no con un commit. No falla tampoco por un caso que falta (D-2) ni por otro juez (D-4): los dos salen como avisos.

## Las desviaciones (DV-CI-n)

- **DV-CI-1, en las pruebas.** El caso al revés de P-CI-6 se escribió primero con un ADT genérico, que ya trae hallazgos en el
  juguete y no servía para lo que se probaba. Se cambió al mensaje nominal del juguete, `JUGUETE-NOMINAL`. Se arregló antes de
  escribir el código, con la prueba en rojo por la razón prevista.
- **DV-CI-2, la entrada `nombre`.** El diseño nombraba el artefacto `verificador-${{ github.job }}-…`. En un flujo reutilizable,
  `github.job` es el id del job llamado (`verificar`), así que los tres controles de la demo subirían tres artefactos con el mismo
  nombre en la misma corrida, y `upload-artifact@v4` no lo admite. Hay una entrada `nombre` (por omisión `verificador`) y la demo
  da uno a cada control.
- **DV-CI-3, `laboratorio_ref` por omisión `main`.** El diseño usaba `github.job_workflow_sha` cuando la entrada iba vacía. Esa
  propiedad no aparece en la documentación del contexto `github` de las expresiones; `job_workflow_sha` es una reclamación del
  token OIDC. La entrada vale `main` por omisión. La demo la fija a `${{ github.sha }}`, y `CI.md` pide a un tercero que la fije a
  un commit (L-CI-13).
- **DV-CI-4, los `outputs` entre comillas.** En un mapa de flujo de YAML, `{value: ${{ … }}}` abre otro mapa y no se lee. Los
  siete valores van entre comillas dobles. Lo comprueba P-CI-1 al cargar el YAML.
- **DV-CI-5, `timeout-minutes` 75 en el flujo y 15 en `pruebas`.** El diseño ponía 30 y 10. Con D-3, el control real en modo
  mensaje tarda unos 30 minutos por corrida en el laboratorio, y en el runner puede tardar más. El tope sigue siendo un tope: no
  hay `continue-on-error`.
- **DV-CI-6, `hacer_bases.py`.** Los pasos de §6 se escribieron en un guion: dos corridas desde la copia pública, `INFORME.json`
  igual byte a byte, `crear` de la primera y `comparar --esperar igual` de la segunda. En el juguete, además, siembra, tercera
  corrida, `comparar --esperar falla` y `--deshacer`. Deja `BASES-CI.json` con lo que hizo en la carpeta de trabajo, fuera del
  repositorio.
- **DV-CI-7, la base en modo mensaje.** La saca `hacer_bases.py … mensaje` con el adaptador `linuxforhealth-mensaje.json` de la
  etapa 21, de una sola corrida (`dos=False`), porque cada una tarda unos 22 minutos. La segunda corrida se hizo aparte, con la
  misma orden: `INFORME.json` sale igual byte a byte y `comparar --esperar igual` da 0. Frente a la base de lote cambian
  exactamente los 23 casos del arrastre, de VXU-B18 a VXU-B40, y ninguno cambia de categoría. En todos desaparece el `RXA-17` de
  algún grupo (`fidelidad`, `dato_perdido`):
  - el del primer grupo, en 22;
  - en VXU-B35, solo el del segundo, `RXA(2)-17`;
  - en VXU-B33 y VXU-B34, también los de otros grupos.

  Es lo que dice `RESULTADO-ARRASTRE.md`.
- **DV-CI-8, el `INFORME.md` en el artefacto.** El diseño ya lo listaba. Se anota porque el resumen de la página del job no repite
  la frase fija de la herramienta, y la frase está en ese fichero (L-CI-7).
- **DV-CI-9, comentarios y nombres de pasos.** Algunos comentarios y nombres de pasos de los dos YAML dicen «los mismos
  veredictos» donde el diseño decía «igual», y «el hallazgo» donde decía «el triple». No cambia nada de lo que corre.
- **DV-CI-10, un ensayo local antes del primer push.** El diseño iba del laboratorio al runner sin paso intermedio, y cada
  arreglo en el runner cuesta un push por la opción B. `ensayo_flujo.py` corre en la máquina del laboratorio los pasos de shell
  de los dos YAML, en orden. Evalúa sus expresiones, pasa las salidas entre pasos, entre jobs y del flujo reutilizable al que
  lo llama, y emula los checkouts copiando el árbol. Los seis jobs salieron en verde a la primera del ensayo:
  - **el positivo** falló en 303 casos, solo por PID-7;
  - **el real** trajo LinuxForHealth por la red y dio la huella `ac41f71b…`, la imagen por su digest y 0 diferencias con la base.

  Lo que no prueba está en su cabecera: la evaluación de GitHub de verdad, el Docker, el usuario y la red del runner.
- **DV-CI-11, la previsión se rehízo tras el ensayo, antes de sellarla.** El primer borrador, escrito antes del ensayo, queda en
  `PREVISION-CI.json` (`antes_del_ensayo`). A Jev se le preguntó dos veces, con un estado antes del ensayo y otro después, y se
  sellan las dos respuestas.
- **DV-CI-12, la revisión a ciegas, y un segundo sello antes del primer push.** La primera pasada no aprobó.
  - **El defecto:** GitHub corre los pasos con `shell: bash` como `bash --noprofile --norc -eo pipefail`, y el `set -uo pipefail`
    de los pasos «Verificar» y «Veredicto» no quita el `-e`.
    - Cuando la comparación salía con 10, el paso se cortaba antes de escribir el resumen de la página del job.
    - Cuando la herramienta salía con 4, el paso se cortaba antes de dejar su código, y el veredicto no llegaba a dar el motivo
      `caja`.
    - El estado del job era el correcto; se perdía el diagnóstico. Ni el laboratorio ni el ensayo pasan por ese camino, porque
      los tres controles salen con 0.
  - **El arreglo:** P-CI-15 en rojo primero (corre el cuerpo de los dos pasos con el shell de GitHub y una orden que falla) y
    `set +e` en los dos pasos.
  - **Los menores:**
    - la orden de etiquetar la imagen va a un fichero antes de ejecutarla, para que un error de `linea_base.py` no se tome por
      una orden;
    - `CI.md` dice que `INFORME.*` y `juicio.jsonl` llevan valores de los campos juzgados;
    - el comentario de la demo apunta a `CI.md`;
    - esta DV-CI-7 da el grupo de cada `RXA-17`.
  - **El segundo sello:** el primero (25-oct, 17:08, en el historial del laboratorio) cubría el YAML con el defecto. Se volvió a
    sellar con el flujo arreglado y las mismas cifras de la previsión; los dos sellos son anteriores al primer push.
    - El cuerpo de la previsión no se tocó, así que `base_de_la_prevision` sigue diciendo «las 14 pruebas»; con P-CI-15 son 15.
    - Lo mismo el comentario del job `pruebas` en `demo-ci.yml` («P-CI-1..14»).
  - **La segunda pasada de la revisión aprobó.**
