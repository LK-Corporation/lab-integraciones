# Preinscripción PRE-TEST — v3 y definitiva, 22-sep-2026

**Se sella antes de que el agente vea un solo caso del conjunto reservado.**

La v1 y la v2 se pasaron por cinco revisores con el encargo de romperlas. Las rompieron las dos.
La v3 acepta sus correcciones y, sobre todo, **invierte la predicción**: al construir el suelo que
uno de ellos exigió, quedó claro que el agente va a perder. Esta preinscripción predice mi propio
fracaso, que es la forma más fuerte que tiene una preinscripción de valer algo.

---

## 1. Lo que se sabe antes de abrir el reservado

Sobre los **456 casos del conjunto de desarrollo**, con el agente ya corrido y un adversario
mecánico sin modelo:

| | agente (b) | triador regex v3 |
|---|---|---|
| TOTAL | +0,642 | **+0,875** |
| `SIN_PROBLEMA` | +0,938 | +0,938 |
| `RECHAZO_POLITICA` | +1,000 | +1,000 |
| `FALLO_MENSAJE` | +0,233 | +0,727 (v2) |
| fallo silencioso | +0,396 | **+0,833** |

Y el reparto caso a caso, que es el número que lo cierra:

```
   agente SI, script NO :   3 de 456   <- todo lo que aporta el modelo
   agente NO, script SI :  74 de 456
   los dos aciertan     : 342
   los dos fallan       :  37
```

**Los 3 son casos `SIN_PROBLEMA`**, o sea ni siquiera detecciones. El agente no aporta una sola
detección que el script no tenga.

Por operador, el script acierta **16 de 18 a 8/8**. Los dos que falla son exactamente los dos que
la matriz de observabilidad declaró **no identificables** el 21-sep, antes de que el agente
existiera — y el agente también los falla.

### 1.1 Por qué pasa esto, y es el hallazgo de la fase

El corpus está construido aplicando **operadores de mutación declarativos**. Por construcción,
cada operador deja una firma mecánica: para eso es un catálogo. Un detector escrito contra esas
firmas llega al **100 % de lo observable**.

**Un corpus de mutaciones declarativas no puede contestar «¿aporta el modelo?».** Lo decidió la
forma de construir el banco hace un mes, y no se vio hasta que se escribió el adversario fuerte.

Esto **no invalida** la pasada del reservado: un negativo medido en desarrollo podría ser de
desarrollo. La pasada lo confirma o lo desmiente en datos que nadie ha visto.

---

## 2. Definiciones, y de dónde sale cada número

**La métrica** es la del puntuador: macro caso → operador → clase, θ=0,225, K=0,5.

**`detecta`** := el veredicto emitido es exactamente `RESULTADO_INCORRECTO_SILENCIOSO`. Un `NO_SE`
puntuado +1 **no** es una detección.

**`NO_SE` vale 0 o +1 según `ideal_b`**, pre-marcado caso a caso en `afinado/tabla_casos_v2.tsv`
desde el 21-sep. Verificado: 56 de 56 con valor, y exactamente **dos** aceptan `NO_SE`, que son
los dos no identificables. **Nadie adjudica nada después de la pasada.**

**Los dos «18» que no son el mismo, y la v2 los confundía.** El de la especificación son los 19
operadores de fallo silencioso del corpus principal menos el no identificable. El del reservado
son 18 porque el generador excluyó los `ENV_*`, e **incluye los dos no identificables**. Aquí se
usa siempre el del reservado: **18 operadores, de los cuales 2 no son identificables.**

---

## 3. Las predicciones

**H1 — LA PRIMARIA. El agente pierde contra el adversario mecánico.**

El total del agente sobre el reservado es **menor que +0,873**, la nota sellada del triador v3
sobre ese mismo conjunto. Predicción puntual: **entre +0,45 y +0,75**.

**H2 — el agente no aporta ninguna detección que el script no tenga.**

Casos donde el agente acierta y el script falla: **≤ 2 de 56**, y **ninguno de ellos es una
detección de fallo silencioso**. En desarrollo fueron 3 de 456, todos `SIN_PROBLEMA`.

**H3 — los dos no identificables siguen sin detectarse por nadie.**

`MLLP_DOS_MENSAJES_UN_MARCO` y `PID3_EXISTENTE_DATOS_DISTINTOS`: **0 detecciones**, ni del agente
ni del script. Es la apuesta arriesgada, porque basta **una** para tumbarla, y si cae significa
que la frontera que la matriz dibujó no era dura.

**H4 — capacidad absoluta del agente.** Detecta **≥ 9** de los 18 operadores de fallo silencioso.
Direccional, sin techo. Y acierta **≥ 20** de 22 `SIN_PROBLEMA`.

**H5 — las llamadas.** **≥ 54 de 56** casos con exactamente una llamada a cada herramienta, y
**cero** casos sin ninguna. En desarrollo: 451/456 y cero.

**Descriptivas, fuera de toda regla:** `FALLO_MENSAJE` (en desarrollo 43/88), la tasa de `NO_SE`,
la duración por caso, y cuántas veces la puerta de orden rechaza una llamada.

---

## 4. La regla de decisión

Se reportan **los cuatro resultados, siempre**, y no se resumen en una palabra:

| | se cumple si | qué significa |
|---|---|---|
| **H1** | total del agente < +0,873 | para este circuito y este corpus, **no hace falta un modelo** |
| **H2** | ≤2 casos propios, ninguno detección | el modelo no aporta nada que una regla no tenga |
| **H3** | 0 detecciones en los dos no identificables | la frontera de observabilidad era real |
| **H4** | ≥9 operadores ∧ ≥20 limpios | el agente funciona **en términos absolutos**, aunque pierda |

**H1 y H4 pueden cumplirse a la vez, y probablemente lo harán.** Eso no es una contradicción: es
el resultado. *El agente funciona y aun así no hace falta.* Se reporta con esas dos frases juntas
y ninguna sola.

**Si H1 falla** —el agente gana al script— la fase tiene un resultado positivo que en desarrollo
no se veía, y habría que explicar la discrepancia entre los dos conjuntos antes de celebrarla.

**Si H3 falla** —alguien detecta un no identificable— hay que revisar la matriz de observabilidad,
y probablemente sea el script acertando por casualidad.

---

## 5. El canario

`puntua=0`, no entra en ninguna puntuación. **Predicción: el literal `CANARIO_TABLA` no aparece en
ninguna de las 56 salidas crudas. Si aparece en una, la tanda queda invalidada** y no se reporta
ningún número de ella.

---

## 6. El suelo, sellado con huellas, medido antes

| adversario | total sobre el reservado |
|---|---|
| las cinco constantes | −0,500 a −0,125 |
| siempre `NO_SE` | +0,028 |
| triador regex v1 | +0,557 |
| triador regex v2 | +0,790 |
| **triador regex v3** | **+0,873** |

Los tres triadores con huella en `SELLO-RESERVADO.txt`, junto con el catálogo, la tabla del
reservado, el puntuador, el corredor, el prompt congelado y las clases del arnés.

**Tres controles sobre el v3, porque la conclusión es que un script bate al modelo:**

1. **Clave barajada**: 0 de 456 veredictos cambian. No usa la clave para decidir.
2. **Qué lee**: solo campos `medido_*`, `can_*` y un contador — lo que el circuito **hizo**, que es
   exactamente lo que el agente ve por `traza()` y `log()`. Ni una columna `esperado_*`.
3. **Control negativo propio**: 0 de 192 limpios en desarrollo y 0 de 22 en el reservado.

**Por qué vale que sus reglas se escribieran mirando los datos.** Subir la barra solo vale en una
dirección: un adversario demasiado fuerte puede causar un falso **negativo** —concluir que el
agente no aporta cuando quizá aporta— pero nunca un falso positivo. Afinar la barra hacia arriba
es conservador; afinar el prompt del agente con lo mismo sería trampa.

**Lo que este suelo no permite decir.** No se afirmará «bate a *cualquier* lectura mecánica»: eso
exigiría una colección exhaustiva que no existe. Se dirá **«pierde contra los adversarios de este
banco sellado»**, nombrándolos.

---

## 7. La clave del reservado, sellada

`comparar.py` sobre los 58 casos, **antes** de que el agente vea nada: **58 de 58 de acuerdo, cero
cuarentenas, 58 operadores de 58 confirman lo declarado.** Con eso queda cerrada la salida más
barata que existe si el resultado incomoda: «la clave de ese caso estaba mal».

## 8. Lo que se captura

Salida cruda entera, contexto completo de la sesión con nombre, argumentos, respuesta y orden de
cada llamada, duración por caso, y un `_meta.json` con modelo, temperatura, huella del delta
(`89ae1c8d`), tanda y fecha.

## 9. Lo que NO se va a hacer

- No se toca el prompt: la huella se comprueba al arrancar y aborta si no cuadra.
- No se corre dos veces para quedarse con la mejor.
- No se añaden ni se quitan predicciones después de ver los resultados.
- No se elige *a posteriori* qué comparación reportar.
- **Si sale mal, se publica igual.** Un negativo preinscrito y confirmado es un resultado.

## 10. Lo que no prueba, salga como salga

56 casos, un modelo, una temperatura, un circuito, **sin un solo caso de `ENTORNO`**, sobre un
corpus **sintético de mutaciones declarativas** —que es justamente la limitación que la §1.1
explica—. Lo que salga vale para este montaje, y la conclusión general que sí se puede defender es
metodológica: **un banco construido así favorece por diseño al detector mecánico, y por tanto no
puede contestar si el modelo aporta.**
