# Un proyecto de conversor de ejemplo, con su integración continua

Es un proyecto de conversor HL7 v2 → FHIR R4 como lo tendría un tercero, dentro del repositorio del laboratorio. Su llamada al
flujo reutilizable del verificador es `.github/workflows/ejemplo-ci.yml`, por la forma remota y fijada a un commit del
laboratorio, como la escribiría cualquier proyecto. Su plantilla, con el commit por poner (`COMMIT_C1`), es
[`../verificador/cv/ci/github-ci2/ejemplo-ci.yml`](../verificador/cv/ci/github-ci2/ejemplo-ci.yml). La guía del flujo es
[`../verificador/cv/ci/CI.md`](../verificador/cv/ci/CI.md).

## Qué hay

- **[`conversor.py`](conversor.py):** el conversor, en Python con la biblioteca estándar. Lee ADT, ORU^R01 y VXU^V04 y escribe
  un Bundle por mensaje. Es determinista y pequeño. Hace a propósito lo justo, y lo que el verificador ve mal lo registra la
  línea base.
- **[`preparar.sh`](preparar.sh):** la orden «preparar» del proyecto. Deja el conversor en los artefactos.
- **[`corpus/`](corpus/):** seis mensajes sintéticos propios: tres ADT, dos ORU y un VXU.
- **[`ci/adaptador.json`](ci/adaptador.json):** el adaptador. El conversor corre en la imagen oficial `python:3.12-slim`,
  fijada por su digest.
- **Las dos líneas base:** [`ci/LINEA-BASE.json`](ci/LINEA-BASE.json), con el corpus del laboratorio más el propio, y
  [`ci/LINEA-BASE-propio.json`](ci/LINEA-BASE-propio.json), solo con el propio.
- **[`ci/hacer_base.sh`](ci/hacer_base.sh):** cómo se hicieron las bases, en un guion.
- **El defecto del run en rojo:** [`ci/DEFECTO.json`](ci/DEFECTO.json) y [`ci/sembrar.py`](ci/sembrar.py).

## Qué copiar a un proyecto propio

Copia la carpeta y cambia cuatro cosas: el conversor, la orden de `preparar.sh`, la imagen del adaptador con su digest y el
corpus. Después:
1. rehaz las bases con `ci/hacer_base.sh`;
2. copia la llamada de `ejemplo-ci.yml` a tu `.github/workflows/`, con el commit del laboratorio que quieras fijar en `uses:` y
   en `laboratorio_ref`.

El commit fijado se queda donde está hasta que lo subas a mano. Para subirlo, regenera las bases con ese commit.

## Cómo se hizo la base

Desde la raíz del repositorio, en una máquina con Docker:

```bash
bash ejemplo-ci/ci/hacer_base.sh <artefactos vacíos> <trabajo vacío>
```

El guion hace:
1. trae la imagen por su digest;
2. corre dos veces cada base y exige el mismo informe byte a byte;
3. crea las dos bases y compara la segunda corrida con ellas, con `igual`;
4. siembra el defecto y comprueba que la corrida sembrada falla, con `falla` y con `pasa`, solo por el hallazgo de
   `DEFECTO.json`;
5. deshace la siembra.

## El run en rojo

`.github/workflows/rojo-ci.yml` (su plantilla:
[`../verificador/cv/ci/github-ci2/rojo-ci.yml`](../verificador/cv/ci/github-ci2/rojo-ci.yml)) corre solo a mano. Siembra el defecto en la copia del
conversor que deja `preparar.sh` y llama al flujo en el modo normal. El job `rojo` tiene que fallar, y `rojo-comprobado`
comprueba desde fuera que falló por el hallazgo sembrado y solo por él. La corrida queda en rojo, porque tiene que estarlo.

En una máquina se repite con los pasos 8 a 10 de `ci/hacer_base.sh`: sembrar, la corrida sembrada y deshacer.
