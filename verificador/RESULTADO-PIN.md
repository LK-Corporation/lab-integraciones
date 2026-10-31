# Resultado de la etapa 27: subir el pin del proyecto de ejemplo como lo haría un tercero

**Siguiendo la guía, un proyecto sube el pin al commit que trae un tipo de mensaje nuevo cambiando el pin y rehaciendo su base,
después de corregir la receta, que llevaba el número de casos a mano. Sin rehacerla, en el ensayo local, el flujo sigue en verde
mientras el juez nuevo no cambie los casos que ya estaban: con avisos y 40 casos nuevos sin juzgar, y solo la comprobación de
fuera lo ve.**

En GitHub Actions, a la primera, con el pin en `c9d49d9` (el commit con MDM):
- **`ejemplo-ci`** salió en verde ([corrida](https://github.com/LK-Corporation/lab-integraciones/actions/runs/41186811736),
  [`pin/CORRIDA-PIN-1.json`](pin/CORRIDA-PIN-1.json)):
  - las dos llamadas pasan frente a sus bases rehechas, con 389 y 6 casos y 0 nuevos;
  - la comprobación de fuera sale TODO BIEN.
- **El run en rojo a mano** falló solo en «Veredicto frente a la linea base», con `PID-8` en 164 casos, y `rojo-comprobado` salió
  en verde ([corrida](https://github.com/LK-Corporation/lab-integraciones/actions/runs/41186955970),
  [`pin/CORRIDA-PIN-2.json`](pin/CORRIDA-PIN-2.json)).
- **La demostración y la higiene** siguieron en verde.

La pregunta, fijada antes de medir en [`ANTES-ETAPA-PIN.md`](ANTES-ETAPA-PIN.md):

> Un proyecto que llama al flujo fijado a un commit anterior, ¿puede subir el pin al commit que trae un tipo de mensaje nuevo
> siguiendo solo la guía publicada (`CI.md`): cambiar el pin, rehacer su línea base con la receta y nada más? ¿Siguen sus dos
> llamadas en verde y el run en rojo cayendo solo por su defecto? ¿Y qué ve quien sube el pin sin rehacer la base?

## Sin rehacer la base

En el ensayo local, con el pin nuevo y las bases viejas:

| Job | Qué dio |
|---|---|
| `ejemplo / verificar` | **pasa**, con avisos `juez_distinto` y `corpus_distinto` y 40 casos nuevos anotados. Son los MDM, que el conversor de ejemplo rechaza |
| `ejemplo-propio / verificar` | **pasa**, con el aviso `juez_distinto` |
| `ejemplo-comprobado` | **falla**: `nada_nuevo`, `sin_avisos`, `todos_los_casos` e `identidades` salen falsos |

En el modo `pasa`, un caso que no estaba en la base solo se anota y los avisos no hacen fallar. Por eso el flujo sigue en verde
mientras el juez nuevo no cambie los casos que ya estaban; aquí no los cambió. Lo dice ahora la guía,
[`cv/ci/CI.md`](cv/ci/CI.md).

## Rehaciendo la base

**La receta del ejemplo** (`ejemplo-ci/ci/hacer_base.sh`), corrida tal cual con el pin nuevo, se paraba en el primer paso:
«ejemplo: 389 casos y se esperaban 349». El número iba a mano.
- **El arreglo, que decidió Jev** ([`pin/estado_qpin.md`](pin/estado_qpin.md)): la receta cuenta los casos que junta la herramienta
  en el commit fijado. La parada se queda para cuando no cuadran, y la guía explica que el número cambia con el corpus.
- **Con el arreglo,** la receta hizo las dos bases con dos corridas iguales, y el defecto sembrado dio `PID-8` en 164 casos, los
  mismos de antes. Los 40 MDM los rechaza el conversor, así que el defecto no los toca.

## La previsión sellada, frente a lo que salió

La previsión se selló antes de medir: [`pin/prevision-pin.json`](pin/prevision-pin.json) (programador) y
[`pin/decision-jev-prevision-pin.md`](pin/decision-jev-prevision-pin.md) (Jev).

| | Programador | Jev | Salió |
|---|---|---|---|
| Sin rehacer la base, la llamada principal pasa | 0,8 | 0,62 | **sí** |
| Sin rehacer la base, la comprobación de fuera falla | 0,85 | 0,87 | **sí** |
| La receta basta sin tocar la guía | 0,75 | — | **no**: se paraba |
| Casos del ejemplo con la base rehecha | 389 | — | **389** |
| Casos del run en rojo | 164 | los mismos, 0,87 | **164** |
| Todo en verde a la primera en GitHub | 0,85 el ejemplo y 0,85 el rojo | no, 0,79 | **sí** |
| Pushes | de 1 a 3; lo más probable, 2 | — | **2** (el pin y este resultado) |

## Lo que no dice

- **El ejemplo vive en el mismo repositorio que el laboratorio.** Un tercero en otro repositorio haría lo mismo, pero no se ha
  recorrido.
- **El conversor de ejemplo rechaza MDM,** así que los 40 casos nuevos son rechazos. Con un conversor que convierta MDM, la base
  nueva llevaría sus hallazgos de MDM.
- **«Sigue en verde sin rehacer la base»** vale mientras el juez nuevo no cambie los casos que ya estaban. Si los cambia, el flujo
  cae por `hallazgo_nuevo`, que es lo que debe hacer.
