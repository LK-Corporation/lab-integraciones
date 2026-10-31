# Etapa 25: las decisiones de Jev y las desviaciones del programador

El diseño es `diseno-mant-fable.md` (Fable, a ciegas). Las tres preguntas de su §7 se pasaron a Jev con un estado neutro
(`estado_qmant.md`, `preguntas_qmant.json`); la respuesta está en `decision-jev-qmant.md`.

## Las decisiones (Q-MANT-D)

| Pregunta | Jev | Confianza | Recomendación del diseñador | Qué cambia |
|---|---|---|---|---|
| Q-MANT-D-1, qué mayor | **la mínima con Node.js 24**: checkout v5.1.0, setup-python v6.3.0, upload-artifact v6.0.0, download-artifact v7.0.0 | 0,37 | la última | los commits de §2.2, columna «mínima»; la escalera de §3 empieza en la mínima y su único peldaño es la de la 24 |
| Q-MANT-D-2, `persist-credentials` en la higiene | **sí** | 0,92 | igual | una línea en `higiene.yml`; P-CI-29 cubre los siete checkouts (DV-MANT-7) |
| Q-MANT-D-3, `pull_request` otra vez | **sí**: la rama del resultado como PR, integrada por avance rápido | 0,48 | no | `M3` va a una rama con su PR, como en la 24, y sus corridas a `CORRIDA-MANT-4*.json` |

## Las desviaciones (DV-MANT-n)

- **DV-MANT-1, `yaml_dir()`** busca primero las plantillas de la 25 (`github-mant/`), después las de la 24 y por último las de la 23.
  Así, en el laboratorio, P-CI-1..31 leen los YAML de la etapa.
- **DV-MANT-2, P-CI-28 y P-CI-31 salieron en verde en el rojo.** `ACCIONES-CI.json` se escribió en el paso 1, con red, antes de
  las pruebas, como pide el plan; y P-CI-31 vigila entradas que los YAML ya cumplían. Sus controles negativos son los que
  prueban que muerden.
- **DV-MANT-3, la comparación de `traer_resultados_ci.py`.** Mira el artefacto con el mismo nombre del primer intento de la
  referencia (`<control>-1`), como hacía con los `verificador-*`. Así una corrida relanzada se compara igual.
- **DV-MANT-4, el control del aviso, medido antes de sellar.** `anotaciones_ci.py` sobre la corrida de `ejemplo-ci` de la 24
  (41136715322) ve el aviso en sus tres jobs. El texto de GitHub empieza «Node.js 20 is deprecated…», y el patrón casa sin
  ajustarlo.
- **DV-MANT-5, una nota de checkout que el diseño no cita.** `v5.1.0` trae «[BREAKING] backport `allow-unsafe-pr-checkout`
  to v5»; el §2.1 lo atribuye solo a `v7.0.0`. No cambia nada aquí: `v4.4.0`, la versión de la 24, ya lo traía (el mismo
  aviso en sus notas y la misma entrada en su `action.yml`), y ningún flujo usa `pull_request_target` ni `workflow_run`.
  Lo vio la revisión a ciegas de `M1`; se comprobó con `gh api` en los dos commits.
- **DV-MANT-6, `anotaciones_ci.py` endurecido tras la revisión a ciegas de `M1`, después del sello y antes del primer push.**
  La revisión encontró cuatro caminos por los que daba «sin aviso» o «bien» por error. Ahora:
  - un job se admite como `<run_id>:<job>` y vale solo en esa corrida; lo admitido tiene que llevar el aviso, y en `M1` los
    dos `verificar` de `ejemplo-ci`, que llaman al flujo viejo, son un segundo control del mismo momento;
  - una corrida sin acabar, un job que no acabó en `success` ni en `failure` (saltado, cancelado…), una corrida sin jobs o
    ninguna corrida hacen fallar la orden; `failure` es medida porque el rojo falla a propósito (el cancelado lo vio la
    segunda pasada de la revisión);
  - las anotaciones se leen todas, con `--paginate`.

  P-CI-30 lleva un control por camino, y en rojo con el lector viejo dio 8 MAL. La orden del §4 pasa a
  `--admitir "<run_id de ejemplo-ci en M1>:ejemplo / verificar" --admitir "<el mismo>:ejemplo-propio / verificar"`.
  `SELLO-MANT.txt` guarda las huellas de `anotaciones_ci.py` y `prueba_ci.py` de cuando se selló (las del commit del sello);
  la previsión no cambia.
- **DV-MANT-7, los checkouts.** Son siete en los cinco YAML: dos en la demo, dos en el flujo, uno en el ejemplo, uno en el
  rojo y uno en la higiene. El §2.1 habla de «los siete checkouts de los cuatro flujos del verificador», que son seis; con
  el de la higiene, siete.
