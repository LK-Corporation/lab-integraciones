# Predicción sellada antes de montar la vía (d) — 22-sep-2026

**Se escribe y se sella ANTES de instalar el validador y antes de correrlo.** La Fase 12 enseñó que
la única protección real contra reinterpretar un resultado es haber predicho el propio fracaso por
escrito y con antelación. Esto es lo mismo, en pequeño.

## Qué se va a montar

La vía (d) de la §4.3: un oráculo **cuya firma no sea la mía**. Primer peldaño decidido en la §11.5:
el **validador oficial de FHIR** (`validator_cli`) sobre el recurso `Patient` **realmente escrito**
por el circuito congelado, contra el perfil, más un validador de conformidad v2 sobre el acuse.

Los oráculos no son brazos, así que (d) **sí** puede leer el recurso final, que es justo lo que a
los brazos se les oculta —el bundle solo enseña el canónico intermedio—.

## Qué se va a medir, y con qué control

El control positivo de la §11.6: **cinco fallos reales siguen vivos en el circuito congelado**. Dos
de ellos dejan su huella dentro del recurso FHIR y por tanto están al alcance de (d):

| fallo vivo | lo que quedó escrito en el `Patient` |
|---|---|
| la entrada sin desescapar | `family` = `Ferrándiz\S\Soler`, con la secuencia de escape literal |
| `MAXREP=10` descarta el `MR` de la repetición 11 | `identifier` = el primer `PI` en vez del `MR` |

Y uno más del catálogo, de la misma familia:

| `PID5_LATIN1_EN_EL_CABLE` | `family` = `Ferr?diz`, con el carácter de sustitución |

Los otros tres fallos vivos —el acuse `CE` no conforme, el `AE` que no llega y el 4xx contestado
`AR` con `ERR-3=102`— **no dejan huella en el recurso**: o no se escribe recurso, o el fallo está en
el acuse. Quedan fuera del alcance de esta mitad de (d) y corresponden al validador de conformidad
v2 sobre el acuse.

## La predicción 🔮

**H1 — el validador no verá ninguno de los tres.** Contra el perfil base de `Patient` de R4,
`Ferrándiz\S\Soler` es un `string` perfectamente válido, `Ferr?diz` también, y un `identifier` con
el valor equivocado es un `Identifier` bien formado. **Predicción puntual: 0 de 3.**

**H2 — sobre el corpus entero no encontrará casi nada**, y lo que encuentre será de conformidad
general —`meta.profile` ausente, avisos de terminología, cardinalidades— y **no estará
correlacionado con qué operador se aplicó**.

**H3, que es la que importa y la que puede tumbar la decisión §11.5** — si H1 y H2 se cumplen,
entonces **el peldaño barato de la vía (d) es ciego al fallo silencioso**, que es el objeto de la
fase. Su valor quedaría limitado a la familia estructural, y lo que de verdad haría falta para (d)
es el **mapeador de referencia** desde el IG normativo — que **lo escribiría yo**, y eso le devuelve
mi firma, que es exactamente lo que (d) existía para evitar.

**Si H3 se cumple, hay que decirlo en el diseño y no disimularlo:** la vía (d), tal como se decidió,
no aporta lo que se le pidió, y o se paga el mapeador de referencia asumiendo su sesgo declarado, o
se acepta que ninguna vía ve el silencio sin firma propia.

## Lo que falsaría la predicción

Que el validador señale **cualquiera** de los tres casos por una razón sustantiva —no por un aviso
genérico que también salte en los limpios—. Basta uno. Y el control de que la prueba puede salir
mal: si el validador no señala **nada en absoluto**, ni siquiera en los limpios, entonces no está
funcionando y no se ha medido nada.

## Cómo se comprueba que discrimina

Se valida también una **muestra de casos limpios**. Si los avisos son idénticos en fallos y en
limpios, el validador está midiendo el perfil y no el fallo, y eso es H2 confirmado.
