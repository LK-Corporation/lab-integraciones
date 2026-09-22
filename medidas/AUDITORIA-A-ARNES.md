# Auditoría A — el arnés y la interfaz común de evidencia (22-sep-2026)

Es el **paso 0** del orden de `DISENO-FASE13-v4.md` §9, y lo que tiene que comprobar está escrito
allí: **que el agente, el `v3` congelado y los autores de reglas reciban exactamente lo mismo**,
salvo que la diferencia sea el objeto explícito de estudio.

**Resultado en una frase: la interfaz NO es común, y la diferencia cae justo donde vive el fallo
silencioso.** Para la Fase 12 no importó —está medido— pero para la Fase 13 hay que cerrarla **por
construcción**.

---

## 1. La estructura del arnés está bien, y conviene decirlo

`Lab.Fase12.HerrA`, `HerrB` y `HerrC` son **envoltorios finos** sobre `Lab.Fase12.Datos`: los
brazos se construyen **quitando herramientas**, no cambiando la lógica. Si cada brazo tuviera su
implementación, las diferencias entre brazos medirían el código en vez de la evidencia. Eso está
bien resuelto y no hay que tocarlo.

La lista blanca por traza se impone en `Datos.Autorizar()`, antes de devolver nada, así que un brazo
no puede leer la traza de otro caso ni por descuido ni a propósito.

---

## 2. Las fuentes versionadas están incompletas ⚠️

`HUELLA-ARNES.txt` cubre **dos ficheros**: `Lab.Fase12.Datos.cls` y `Lab.Fase12.HerrB.cls`.

En IRIS hay **ocho clases** `Lab.Fase12.*`. En `arnes/` hay **cinco ficheros**. O sea:

| | en IRIS | en `arnes/` | en la huella |
|---|---|---|---|
| `Datos` | sí | sí | **sí** |
| `HerrB` | sí | sí | **sí** |
| `HerrA` | sí | **no** | no |
| `HerrC` | sí | **no** | no |
| `AgenteA`, `AgenteB`, `AgenteC` | sí | sí | **no** |
| `Volcado` | sí | (en la raíz del repo) | no |

**No se puede afirmar que el arnés esté versionado con huella cuando dos de sus tres clases de
herramientas no están en las fuentes y tres más están sin hash.** Arreglo: exportar `HerrA` y
`HerrC`, y rehacer `HUELLA-ARNES.txt` sobre los cinco.

---

## 3. La puerta de orden está viva, y prácticamente sin probar 📏

`HerrB` impone que `traza` y `log` no contesten hasta haber llamado a `mensaje`, porque el modelo se
ancla en lo primero autoritativo y Ollama ignora `parallel_tool_calls: false`. El rechazo devuelve
un aviso y **no cuenta como llamada**, así que los contadores siguen midiendo lecturas de verdad.

**Cuántas veces llegó a actuar, contado sobre las tandas guardadas:**

| | activaciones de la puerta |
|---|---|
| `brazo_A.tsv`, `brazo_B.tsv`, `brazo_C.tsv` (456 casos × 3) | **0** |
| `reservado_b_contexto.jsonl` (55 casos) | **1** |

**Una vez en 511 casos.** Y en el reservado las llamadas salieron perfectas: **55 `mensaje`, 55
`traza`, 55 `log`**, una de cada por caso.

El fleco de la bitácora decía que «funciona por suerte de ordenación, no porque imponga nada». Con
el número delante hay que matizarlo: **sí impone** —la única vez que hizo falta, actuó— pero **la
situación que protege casi nunca se da**, así que su protección está verificada con n = 1. Si en la
Fase 13 se depende de ella, hay que **provocarla a propósito** y comprobar que el modelo se
recupera, en vez de confiar en una muestra de uno.

---

## 4. El arnés oculta 3 de las 11 propiedades del canónico 📏

Confirmado contra el diccionario de clases: `Lab.HL7.Msg.PatientRequest` tiene **11 propiedades** y
`Datos.Traza()` enseña **8**. Faltan exactamente `SendingApp`, `SendingFacility` y `ProcessingId`,
como estaba declarado.

Sigue sin arreglarse por la misma razón de siempre —cambiarlo haría incomparable lo ya medido— pero
ahora está **comprobado y no supuesto**.

---

## 5. La interfaz **no** es común, y la diferencia importa ⚠️⚠️

Es el hallazgo de esta auditoría.

El informe que leen los brazos de reglas (`bloqueC_total.tsv`) tiene **26 columnas**. El bundle del
agente —`mensaje`, `traza`, `log`— **no contiene 14 de ellas**:

```
rec_family  rec_given  rec_gender  rec_birthdate     <- el recurso FHIR REALMENTE ESCRITO
n_recurso_base  delta_pacientes                      <- el estado del almacen antes/despues
session_id                                           <- el id correlativo que el id opaco oculta
espera_s  nota_envio                                 <- metadatos del instrumento
hay_canonico  can_truncado  medido_n_headers  medido_iserror   <- derivables, pero no dados
```

**Las cuatro `rec_*` son la asimetría que importa.** El bundle enseña el **canónico intermedio** y
oculta a propósito el recurso final. Una regla que compare `can_family` contra `rec_family` pilla
`PID5_ESCAPE_HL7` y `PID5_LATIN1_EN_EL_CABLE` **trivialmente**, y el agente **estructuralmente no
puede**, porque no ve `rec_family`.

**El matiz, y es medido, no supuesto:** el brazo 3 del paso 29 reconstruyó el informe **solo desde
el payload del agente** y **0 de 456 veredictos cambiaron**, misma nota +0,875. O sea que `v3`
**no usa** esas columnas. La comparación de la Fase 12 fue justa **de hecho**.

**Pero eso no sirve para la Fase 13**, y la razón está en el propio diseño: los autores de reglas
serán **otros** —modelos nuevos en sesiones limpias, §11.2— y nada les impide usar `rec_*` si se las
damos. **La simetría tiene que imponerse por construcción, no comprobarse a posteriori.**

---

## 6. Y ninguno de los dos informes que existen sirve para un autor ciego ⚠️

| informe | qué filtra de más |
|---|---|
| `bloqueC_total.tsv` (el real) | el recurso escrito, el estado del almacén, el `session_id` |
| `brazos/informe_sintetico.tsv` (el del brazo 3) | **la clave**: `operador`, `esperado_ack`, `esperado_err3`, `esperado_log`, `esperado_deteccion`, `esperado_efecto`, `acuerdo`, `motivos` |

El sintético se construyó como artefacto de **análisis**, con la clave unida para poder puntuar. Es
correcto para lo que era y **es inservible como entrada de un autor de reglas ciego**.

**Falta un tercer artefacto** —el informe restringido a lo que contiene el bundle **y sin la
clave**— y es barato: es el sintético menos las ocho columnas de clave. Mientras no exista, no se
puede encargar el trabajo de la §4.9.

---

## 7. El enmascarado contra la fuga de orden sí está completo 📏

`aprendiz.py`, que mide si un árbol trivial acierta sin mirar el mensaje, **sigue dando fuga: macro
0,588 contra un suelo de 0,200**, con reloj e id de recurso. **Eso no es un fallo del arnés: es por
qué el arnés enmascara.** El programa consulta **IRIS directamente**, no el bundle.

Comprobado sobre los 327 payloads, que es lo que de verdad ve un brazo:

```
marcas de tiempo ABSOLUTAS visibles ....... 0     (relativas T+ en 319)
id de recurso FHIR visible ................ 0     (id=<oculto> en 220)
MSH-7 del ACK enmascarado ................. 311
session id filtrado ....................... 0
```

**Los dos canales que el paso 4 cerró siguen cerrados.** Lo que **no** se ha hecho es la versión
buena del experimento: entrenar el mismo árbol trivial **sobre rasgos extraídos del bundle** en vez
de de IRIS. Queda como la pieza que falta de esta auditoría.

---

## Lo que sale de aquí, en orden

1. **Construir el informe ciego** —bundle sin clave— o no se puede encargar nada a la §4.9. Barato.
2. **Exportar `HerrA` y `HerrC` y rehacer la huella** sobre los cinco ficheros.
3. **Escribir en el diseño que la simetría se impone por construcción**, con el informe ciego como
   la forma de imponerla, y no como auditoría a posteriori.
4. **Decidir qué hacer con la puerta de orden**: provocarla a propósito para verificarla, o declarar
   que su protección está apoyada en n = 1.
5. **Correr el árbol de fuga sobre el bundle**, que es la pieza que falta.
