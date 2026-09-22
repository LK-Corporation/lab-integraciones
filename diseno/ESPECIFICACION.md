# Especificación del agente de triaje — v5 (22-sep-2026)

**Estado: la escalera está SUBIDA y resuelta en el peldaño 1. Falta firmar 🧑 y confirmar en datos no vistos.**

La v1 se pasó por cuatro revisores externos y **los cuatro coincidieron en la misma crítica de
fondo**. La v2 la acepta y reordena el documento entero. Lo que sigue lleva marcado de dónde sale
cada cosa: 📏 de una medida, 🔍 de una revisión externa, 🧑 abierto.

---

## 0. Lo que la v1 hacía mal, y que esta versión corrige

🔍 **La evidencia respalda un cambio de pregunta, no una descomposición.** Lo demostrado es que
pedir un veredicto da 0/27 y preguntar por fidelidad da 20/27. Eso **no identifica** como variable
causal ni separar en subagentes, ni aislar contexto, ni forzar invocaciones, ni los artefactos
tipados, ni ocultar la taxonomía, ni quitarle el HL7 al clasificador. La v1 acumulaba **seis
intervenciones a la vez** y pretendía atribuir el efecto a «la separación». No habría podido.

**Corrección: §4 ya no propone una arquitectura. Propone una escalera, y gana la más barata que
funcione.**

🔍 **El control de separación fallaba por diseño.** El artefacto de cotejo de la v1 llevaba
`valor_origen` y `valor_canonico`. Quitarle el HL7 al clasificador y darle los valores es no
quitarle nada: puede rehacer el cotejo. **Corrección en §6.2: dos vistas del artefacto.**

🔍 **Una preinscripción con huecos no es una preinscripción.** Faltaban el techo de falsa alarma,
el agregador y la unidad de análisis — y el agregador *es* el clasificador de facto.
**Corrección: §6.3, §11.1 y §11.2, con números.**

🔍 **Riesgo de circularidad.** El generador, el oráculo de verdad, el comparador determinista y los
controles comparten una sola semántica. **Corrección: §12.**

🔍 **Error aritmético.** La v1 decía «reservado 58: 18 silenciosos, 22 limpios», y 18+22≠58. Al
contarlo: son **56 casos** (22 limpios, 18 silenciosos, 11 fallo de mensaje, 4 rechazo por
política, 1 canario que no puntúa). **El README dice 58 y está mal**; el documento de firma dice 56
y acierta.

📏 **«No mira» estaba de más.** Lo medido es que el modelo **no reporta** haber visto la
discrepancia: de 37, reporta y la llama fallo 5, reporta y no la llama 0, no reporta 32. Que no
reporte no prueba que no atienda. La redacción se corrige en todo el documento.

---

### 0.1 Y lo que la v2 hacía mal, corregido aquí

📏 **La escalera se subió, y la respuesta estaba en el primer peldaño.** La v2 la planteaba como
una hipótesis a ordenar por coste. Ya no es hipótesis: está medida, y los peldaños 2 a 5 —dos
turnos, contexto aislado, subagente comparador— **no se construyen**, porque un revisor dejó
escrita la regla de decisión antes de ver el resultado («si «binaria + veredicto» aguanta ≥ 15/27,
no hace falta subagente») y el resultado la supera con holgura.

📏 **Pero lo que funciona es una configuración, no un principio**, y eso la v2 no podía anticipar.
Ver §4.4.

📏 **Un artefacto de medida propio, cazado y arreglado.** La condición «lista de discrepancias sin
veredicto» salía como `0/27` en la tabla, y era falso por construcción: esa condición prohíbe el
veredicto, así que el normalizador rellena `NO_SE` en las 74 y el contador no puede pasar de cero.
Puntuada así habría dicho «pedir la lista sin veredicto tampoco recupera nada», que es lo
contrario de lo que pasa. El analizador ahora lo detecta y lo dice en vez de imprimir un cero.

---

## 1. El punto de partida, dicho con precisión

Trece condiciones sobre los mismos 74 casos (37 silenciosos + 37 limpios), pareadas, McNemar
exacto. Ordenadas por lo que enseñan:

| condición | fidelidad | falsa alarma | Youden |
|---|---|---|---|
| techo: las tres salidas en el prompt, tarea = veredicto | `SIN_PROBLEMA` a los 152 | | |
| base: el agente con el prompt completo | 0/27 | 0/37 | 0,000 |
| sin reglas · sin contrato · ACK oculto · dos campos · prompt de 903 car. · control de texto | 0/27 | 0/37 | 0,000 |
| obligar la comparación campo a campo | 3/27 | 0/37 | 0,081 |
| pedir discrepancias **además** del veredicto | 5/27 | 0/37 | 0,135 |
| preguntar solo «¿el recurso es fiel?», sin veredicto | 20/37 | 4/37 | 0,432 |
| **lista libre de discrepancias, sin veredicto** | — | **37/37** | **0,000** |
| **la binaria DESPUÉS del veredicto** | **0/27** | 0/37 | 0,000 |
| **DOS binarias (recurso y acuse) + veredicto** | **3/27** | 0/37 | 0,108 |
| **UNA binaria + veredicto, T=0,7** | **19/27** | 2/37 | **0,568** |
| **UNA binaria + veredicto, T=0,0** | **22/27** | 1/37 | **0,676** |

**Lo que esto identifica ahora que la escalera está subida:** hace falta **una pregunta binaria
cerrada, colocada antes del veredicto**. Las dos condiciones, y ninguna basta sola:

- quitarle la pregunta → 0/27 (seis condiciones distintas lo confirman);
- **la misma pregunta, con la misma redacción, detrás del veredicto → 0/27.** Esto confirma la
  hipótesis rival que planteó la quinta revisión: un modelo autorregresivo que empieza a emitir
  `{"veredicto": ...` ya se ha comprometido, y lo que venga después es racionalización;
- pero el orden solo tampoco basta: `discrepancias` y `comparar_antes` también ponían claves
  delante y se quedaron en 5 y en 3.

**Y la pregunta tiene que ser cerrada y única.** Abierta a enumeración, el modelo reporta
discrepancias en **37 de 37 limpios**: no falla por omisión, falla por invención. Y añadirle una
segunda binaria —sobre el acuse— hunde la primera de 19/27 a 3/27.

**El veredicto no apaga nada.** Esa era la conclusión del paso 22 y era demasiado fuerte: binaria
más veredicto da 19-22/27, por encima de la binaria suelta. Lo que hundía la condición
`discrepancias` era la enumeración, no el veredicto.

**El criterio original queda FALLIDO, no invalidado.** Es un resultado negativo y se publica como
tal.

---

## 2. Lo que no cambia

Contrato de salida, puntuación, herramientas, circuito congelado y banco de adversarios. Lo único
que se toca es la descomposición interna. Visto desde fuera —entra `traza_id`, sale JSON— es el
mismo sistema.

---

## 3. Observabilidad, y el denominador

`observabilidad.py` reconstruye el canónico que producen las reglas **publicadas** y lo coteja con
el observado, más acuse y log. 📏 **Control negativo: 0 de 120 limpios** (de entrada marcaba 15;
las tres causas eran defectos míos, y están en la cabecera del programa).

| predicado que revela el defecto | operadores |
|---|---|
| correspondencia mensaje ↔ canónico | 7 |
| coherencia del acuse | 1 |
| **otros predicados, sin clasificar todavía** | **10** |
| **no observable con la interfaz actual** | **1** |

### 3.1 El operador no identificable

`PID3_EXISTENTE_DATOS_DISTINTOS`. Mensaje perfecto, canónico **perfectamente fiel**, acuse `AA`, y
como única evidencia una línea de log que dice que el recurso ya existía por creación condicional
— **sin decir que lo guardado sea distinto**.

🔍 La formulación exacta: **dos mundos distintos producen la misma observación.** Si el recurso
previo tenía datos correctos no hay fallo; si los tenía viejos, lo hay. Ninguna política basada
solo en esas observaciones los separa. Penalizar al agente por fallarlo mide **acceso a estado
oculto**, no capacidad de detección.

**Decisión, unánime entre los revisores: fuera del endpoint primario, declarado no observable.**
No se le acepta `NO_SE` como acierto del endpoint de detección, porque eso cambia la pregunta de
«detectar» a «calibrar incertidumbre», que es otra métrica —legítima, y se reporta aparte—.

### 3.2 El defecto del arnés

📏 Al agente se le dice que el canónico lleva once propiedades. **`Traza()` le enseña ocho.**
`SendingApp`, `SendingFacility` y `ProcessingId` existen en `Lab.HL7.Msg.PatientRequest` y el SQL
del arnés no los selecciona. Comprobado por introspección del diccionario de clases.

**Decisión: no se toca el arnés en esta campaña.** Arreglarlo cambiaría la evidencia disponible y
haría incomparable el brazo (b) ya medido. Se declara el hueco, se fija **N = 8** propiedades
cotejables, y se apunta 🧑 para una fase futura. El contrato de evidencia (§6.1) lo dice por
escrito.

### 3.3 El denominador, y la contradicción que la v1 tenía

🔍 La v1 congelaba «18 observables» y a la vez dejaba 10 operadores sin clasificar. No pueden ser
las dos cosas. **Se resuelve así:**

- El **endpoint primario** se define sobre los **18 operadores que no son el no identificable**.
  Esa cifra sí está cerrada: 19 menos 1.
- La clasificación pendiente de los 10 **no cambia el denominador**: cambia a qué fase de la
  escalera se le atribuye cada detección, que es análisis secundario.
- Se publican tres cifras: la **heredada sobre 19** (marcada como mezcla), el **endpoint primario
  sobre 18**, y la **cobertura epistemológica**.

### 3.4 La unidad de análisis 🔍

«Sensibilidad sobre 18 operadores» no es una definición. **Se declara:** el endpoint primario es la
**media macro por operador** — por cada operador observable, la fracción de sus casos detectados;
después, la media sobre operadores. Es la misma agregación que ya usa el puntuador (caso →
operador → clase) y por eso es la que toca.

---

## 4. La escalera, subida: el diseño es el peldaño 1

🔍 La v2 planteó una escalera en vez de una arquitectura: se sube un peldaño solo si el anterior no
basta, y gana el primero que alcance el criterio. **Se subió. Bastó el primero.**

| # | peldaño | qué añade | resultado |
|---|---|---|---|
| **0** | **b** — monolito, veredicto directo | — | 📏 **0/27** |
| **1** | **b+** — misma sesión, un turno: una binaria cerrada antes del veredicto | solo el cambio de pregunta | 📏 **19-22/27 · falsa alarma 0,027-0,054** |
| 2 | c1 — dos turnos, misma sesión | secuenciar | **no se construye** |
| 3 | c2 — dos fases, contexto aislado | aislar contexto | **no se construye** |
| 4 | d1 — subagente comparador | subagente + artefacto | **no se construye** |
| 5 | d2 — subagente sobre pares extraídos | quitar la extracción | **no se construye** |
| — | e — comparador determinista | ningún modelo | adversario del banco, §4.3 |

🔍 **La regla de decisión la escribió un revisor externo antes de ver el resultado:** *«si «binaria
+ veredicto» aguanta ≥ 15/27, no hace falta subagente: basta el orden»*. Las dos pasadas la superan
con holgura. Los peldaños 2 a 5 **no se construyen**, y eso es un resultado, no un atajo: el
aparato multiagente de la v1 habría sido coste puro.

**Y el peldaño 1 conserva la pregunta de investigación.** 🔍 Lo avisó la quinta revisión: los
peldaños altos no son un agente autónomo sino un flujo con LLM en etapas, y la pregunta pasaría de
«¿puede este modelo triar con herramientas?» a «¿qué reparto entre modelo y arnés hace triable el
problema?». Mejor pregunta, pero otra. El peldaño 1 es un agente, una inferencia, sus herramientas:
la pregunta firmada sigue en pie.

**Lo único que cambia del contrato**: una clave más en el JSON, antes de `veredicto`, que el
puntuador no lee. Los seis campos puntuados no se tocan.

**Y una restricción sobre esa clave**, ya **confirmada** con predicción sellada antes (§4.6):
**la pregunta va en positivo**. «¿El recurso es fiel al mensaje?», con «SI» significando que todo está bien. Formulada
al revés, el efecto desaparece y la tasa de falsa alarma se multiplica por cinco.

### 4.4 El filo de cuchillo, que es el hallazgo que hay que decir en voz alta 📏

Lo que funciona **no es un principio, es una configuración**, y es estrecha:

```
   quitarle la pregunta               ->  0/27    (seis condiciones lo confirman)
   moverla DETRAS del veredicto       ->  0/27
   abrirla a enumeracion libre        ->  confabula: 37/37 limpios
   anadir una SEGUNDA binaria         ->  3/27
   ---------------------------------------------------------------
   UNA binaria cerrada, ANTES         ->  19-22/27
```

Las dos condiciones son necesarias y ninguna basta sola. Que la misma pregunta con la misma
redacción pase de 19/27 a 0/27 solo por ir detrás **confirma la hipótesis rival** que planteó la
quinta revisión: un modelo autorregresivo que empieza a emitir `{"veredicto": ...` ya se ha
comprometido. Pero el orden solo tampoco basta, porque `discrepancias` y `comparar_antes` también
iban delante y se quedaron en 5 y en 3.

**Consecuencias, y son tres:**

1. **No se puede prometer robustez.** El efecto es grande y replicado a dos temperaturas, pero
   sobrevive a muy pocos cambios. Cualquier documento que salga de aquí lo dice así.
2. **La confirmación en datos no vistos deja de ser higiene y pasa a ser imprescindible.** Un
   efecto frágil medido trece veces sobre los mismos 74 casos necesita un conjunto nuevo.
3. ~~Hay que medir la fragilidad~~ → **medido**. Ver §4.5.

### 4.5 La fragilidad, medida: no es la redacción, es la polaridad 📏

Diez paráfrasis encargadas **a ciegas** —a quien las escribió no se le dijo que la original
funciona ni cuánto— a dos modelos distintos, cinco cada uno. **Se usaron las diez**; elegir habría
sido sesgar. Corridas sobre el **conjunto de desarrollo**, 72 silenciosos y 72 limpios con muestra
estratificada y semilla, T=0, con la original como una condición más sobre los mismos casos.

| polaridad | n | macro primario |
|---|---|---|
| positiva | 8 | **0,578 – 0,760** (mediana 0,667) |
| **original** | 1 | **0,657** |
| **invertida** | **2** | **0,029 y 0,108** |

**El efecto es de la pregunta, no de esa redacción.** Las ocho de polaridad positiva conservan el
efecto y **la original cae en mitad de su rango**. Que una la mejore de forma significativa
(`opus1`, +8/−1, p=0,039) es la señal de que no hay sobreajuste a la redacción con la que se
encontró — si la original hubiera sido la mejor con diferencia, olería a casualidad.

**Pero las dos invertidas se desploman**, y con falsas alarmas de 31/72 y 22/72 contra 6/72 de la
original. La restricción no es la redacción en general: **es la polaridad.** La pregunta tiene que
ir en positivo («¿es fiel?»), no en negativo («¿se perdió algo?»).

**El mecanismo, comprobado, porque mi primera hipótesis era falsa.** Pensé que el modelo se liaba
al mapear su propia respuesta al veredicto. No: en las dos invertidas el mapeo es **correcto para
esa polaridad** —`fidelidad=SI → RESULTADO_INCORRECTO_SILENCIOSO` en 33 y 26 casos,
`fidelidad=NO → SIN_PROBLEMA` en 104 y 101—. Lo que se rompe es **contestar**: en `opus5`, sobre
72 casos con fallo real contesta «no» **70 veces**, y en los limpios reparte casi a la mitad. La
respuesta deja de seguir a la verdad.

~~Con qué cautela: post hoc y n=2~~ → **confirmado en §4.6.**

### 4.6 La polaridad, confirmada con la predicción sellada antes 📏

El contraste de §4.5 era post hoc y descansaba en dos redacciones. Se preinscribió
(`PRE-POLARIDAD.md`, sellado con hash **antes** de encargar nada) y se contrastó con **diez
redacciones nuevas de un tercer modelo**: cinco directas y cinco inversas, en el mismo encargo,
sin decirle qué orientación se espera que funcione. La polaridad la etiqueta **el autor**, en las
secciones de su propia respuesta.

| | macro primario |
|---|---|
| 5 directas | **0,637 – 0,794** |
| original (ancla) | 0,667 |
| 5 inversas | **0,000 – 0,206** |

**Las cuatro predicciones comprobables, una a una:**

| | predicción | |
|---|---|---|
| **P1** | las directas en [0,50 · 0,80] | ✅ 0,637–0,794 — **no hay efecto de lote**, que era lo que el control estaba puesto para detectar |
| **P2** | las inversas por debajo de 0,30 | ✅ todas |
| **P3** | separación completa | ✅ máxima inversa 0,206 < mínima directa 0,637 |
| **P4** | falsa alarma: inversas > 0,15, directas < 0,15 | ❌ **falla** |
| **P5** | el mapeo sigue correcto en las inversas, > 90 % | ✅ 92 %, 95 %, 100 %, 100 %, 100 % |

**Regla de decisión, la escrita antes: CONFIRMADA** (se cumplen P2 y P3).

**Juntando las dos baterías: 13 redacciones de polaridad positiva entre 0,578 y 0,794, y 7 de
polaridad inversa entre 0,000 y 0,206. Separación completa, con un hueco de 0,37.**

#### P4 falló, y enseña más que las que acerté

Predije que las inversas tendrían **más** falsas alarmas. Dos de las cinco no: `g06` hizo 0 de 72
—y también 0 de sensibilidad: contestó «no pasa nada» a todo— y `g07` hizo 9 de 72. Pero `g08`
hizo **61 de 72**.

Así que la polaridad inversa no falla en una dirección: **destruye la discriminación, y hacia
dónde colapsa varía por redacción** — unas al silencio total y otras a marcarlo todo. Mi
predicción suponía un único modo de fallo y era más estrecha que la realidad. Se deja escrita
porque una predicción fallada delimita mejor el hallazgo que tres acertadas.

#### P5, que es la parte mecanicista, replica

En las cinco inversas el modelo traduce su propia respuesta al veredicto **correctamente para esa
polaridad** en el 92–100 % de los casos. Lo que se rompe es **contestar**, no traducir. Ya salió
así en la primera batería con dos redacciones; con cinco nuevas y la predicción escrita antes,
deja de ser anécdota.

#### De regalo, la reproducibilidad

La original se corrió en las dos baterías, misma muestra y T=0: **0,657 y 0,667**. Esa diferencia
de 0,010 es el ruido de Ollama a temperatura cero, que no es determinista del todo. 🔍 Era la
medida 9 de la quinta revisión y queda contestada: el ruido es pequeño frente a los efectos que se
están midiendo, pero **no es cero** y las comparaciones pareadas lo llevan dentro.

⚠️ **Lo que esto sigue sin probar.** Un modelo, una temperatura, una tarea, un idioma. Confirma
que **en este montaje** la polaridad decide. No dice nada de otros modelos ni de otras tareas.

### 4.1 Las decisiones que sí se conservan, y de dónde salen

**La fase de adquisición la hace el orquestador.** 📏 `Lab.Fase12.Volcado` ya lo hace: llama a
`Mensaje/Traza/Log` en orden, de forma determinista, y es lo que genera `payloads_despues.json`.
No es trabajo nuevo. *Consecuencia*: la puerta de «Todavía no» desaparece sola, porque la
adquisición no pasa por `HerrB`.

**El comparador no conoce la taxonomía de veredictos**, en los peldaños que tengan comparador
separado. Es la lectura directa de la medida. Y 🔍 lleva su propio control (§10).

**El clasificador no recibe el HL7 completo** — ni, ahora, los valores (§6.2).

### 4.2 `d1`, `d2` y `e`: la frontera entre el agente y el arnés

Un revisor propuso que el orquestador extraiga los pares y el modelo solo juzgue. Para producto es
lo correcto. Para esta medida colapsa el brazo (d) sobre el (e): si el orquestador ya localizó
`PID-5.1` con los delimitadores de *este* mensaje y la regla de repetición, la parte cara está
hecha y el modelo compara dos cadenas.

Se conserva como variante, con **dos condiciones que la v1 no tenía**:

1. 🔍 **La extracción de `d2` tiene que ser byte-idéntica a la de `e`.** Si no, `d2 − e` no mide
   «lo que aporta el modelo sobre una regla»: mide la diferencia entre dos extractores. Es un
   invariante, y se comprueba con un test que compara las dos salidas carácter a carácter.
2. 🔍 **Se declara de antemano que `d2` tiene información esperada baja.** Si el orquestador extrae
   bien, comparar es casi igualdad de cadenas. Se mide porque es barato, no porque se espere
   sorpresa. **`d2` es el último peldaño, no el primero.**

### 4.3 `e` no es un competidor: es un adversario 🔍

Si `e` funciona, **el suelo sube**. El banco de adversarios ya existe y su suelo está en +0,486; un
comparador determinista que resuelva los 7 operadores de correspondencia es **una lectura mecánica
más de la misma evidencia**, que es exactamente lo que el criterio dice que hay que batir.

Y hay que decirlo con todas las letras: **`e` es parcialmente tautológico.** Implementa las mismas
reglas publicadas de las que se deriva la clave, así que acertar los 7 de correspondencia es casi
por construcción. **Por eso `e` va al banco como adversario y no a la tabla de brazos como rival.**

---

## 5. Lo que se congela, y lo que no se puede congelar

Se congela y se declara: modelo, versión de Ollama, cuantización, temperatura, semilla si la hay,
presupuesto de tokens e iteraciones, evidencia disponible por peldaño, contrato final, validación
del JSON, plazos y tratamiento de errores.

🔍 **No se puede congelar la política ante herramientas paralelas.** `qwen3-coder` llama en
paralelo y Ollama ignora `parallel_tool_calls: false`. La v1 la listaba entre las variables
congeladas y eso era falso. **Queda declarada como variable NO controlada**, y se registra por
ejecución cuántas llamadas en paralelo hubo, para poder mirarla después.

---

## 6. Contratos

### 6.1 El paquete de evidencia

Inmutable, con huella. `traza_id`, `mensaje_crudo`, `recorrido`, `canonico` (las 8 propiedades que
la traza muestra), `acuse`, `log`, y `delimitadores` **leídos de MSH-1 y MSH-2**. Este último sale
de un defecto real: la primera versión de `observabilidad.py` los daba por supuestos y marcaba
cinco casos limpios como defectuosos.

Declara por escrito, porque es la frase que faltaba:

> **La traza NO contiene el recurso FHIR enviado, ni el persistido, ni el código HTTP. Y no
> muestra `SendingApp`, `SendingFacility` ni `ProcessingId`, aunque el canónico las lleve.**

### 6.2 El artefacto de cotejo, en DOS vistas 🔍 — **NO SE CONSTRUYE**

> 📏 **Aviso.** Lo que sigue en §6.2 y §6.3 era el contrato de los peldaños 4 y 5, que la escalera
> declaró innecesarios (§4). **No se implementa.** Se conserva porque es el registro de un diseño
> descartado *por una medida* y no por una opinión, y porque si el peldaño 1 no confirmara en el
> conjunto reservado, esto es por donde se seguiría. Dos cosas de aquí sí valen y se mantienen: la
> distinción entre vista de auditoría y vista del clasificador, y la regla de que una discrepancia
> sin procedencia no vale.
>
> 📏 Y una que la medida contradice: el artefacto por filas pedía al modelo **generar**
> `valor_origen` y `valor_canonico`. Medido: pedirle enumerar discrepancias le hace reportarlas en
> **37 de 37 casos limpios**. La forma generativa no falla por omisión, falla por invención.


Una fila por propiedad, **N = 8 fijo e idéntico en todos los peldaños** — 🔍 si N varía entre
variantes, la tasa de falsa alarma es incomparable, porque más preguntas son mecánicamente más
oportunidades de falso positivo.

**Vista de auditoría** (se guarda, no se le pasa a nadie):

```json
{"version": "cotejo-2", "filas": [
  {"propiedad": "BirthDate", "origen_declarado": "PID-7",
   "valor_origen": "19920308", "valor_canonico": "1992-03-08",
   "resultado": "COINCIDE | NO_COINCIDE | NO_APLICA | INDETERMINADO"}]}
```

**Vista del clasificador** (lo único que cruza a la fase 2):

```json
{"version": "cotejo-2-red", "filas": [
  {"propiedad": "BirthDate", "origen_declarado": "PID-7", "resultado": "COINCIDE"}]}
```

**Sin los valores.** Con ellos, el clasificador puede rehacer la comparación y la separación es
ilusoria — 🔍 el control 10 de la v1 fallaba por diseño.

🔍 **Fuera el campo `por_que` por fila.** Generar texto entre filas rompe la premisa binaria y
altera la distribución de los tokens de las filas siguientes. Si hace falta justificación, va **una
sola, al final, después de todas las filas**, y no cruza a la fase 2.

### 6.3 El agregador, que es el clasificador de facto 🔍

De N filas a un predicado de caso. **Sin números mágicos:**

| filas | predicado de fidelidad | `locus` |
|---|---|---|
| ≥1 `NO_COINCIDE` | **NO es fiel** | la propiedad del primer `NO_COINCIDE` en orden **declarado y fijo**, no elegido por el modelo |
| 0 `NO_COINCIDE` y 0 `INDETERMINADO` | **es fiel** | vacío |
| 0 `NO_COINCIDE` y ≥1 `INDETERMINADO` | **indeterminado** → `NO_SE` | vacío |

Es conservador en la dirección correcta: ante duda, abstenerse antes que declarar limpio. El coste
—una tasa de `NO_SE` posiblemente alta— es un endpoint secundario declarado y se mide.

🔍 **`INDETERMINADO` necesita definición operacional o se convierte en refugio.** Se declara: solo
cuando la propiedad **no aparece** en el canónico observado o su campo de origen **no existe** en
el mensaje. Cualquier otro caso obliga a `COINCIDE` o `NO_COINCIDE`. Se mide su tasa por variante.

### 6.4 La salida final

La firmada, sin un carácter de cambio.

---

## 7. El modelo semántico

| propiedad | fuente | regla | normalización | ausencia |
|---|---|---|---|---|
| `Identifier` | PID-3 | repetición con PID-3.5 = `MR`; si ninguna, la primera no vacía; máx. 10 | componente 1 | — |
| `FamilyName` | PID-5.1 | repetición con PID-5.7 = `L`; si ninguna, la primera con nombre; máx. 10 | **subcomponentes unidos CON UN ESPACIO** | — |
| `GivenName` | PID-5.2 y 5.3 | misma repetición | unidos por espacio | — |
| `Gender` | PID-8 | tabla de búsqueda | → value set de FHIR | **vacío → `unknown`** |
| `BirthDate` | PID-7 | — | `YYYYMMDD` → `YYYY-MM-DD` | vacío |
| `MsgControlId` | MSH-10 | — | tal cual | — |
| `MsgEvent` | MSH-9.2 | — | tal cual | — |
| `Truncado` | — | bandera de la transformación | — | — |

Las dos celdas en negrita salen de defectos que el control negativo cazó: el prompt dice
«subcomponentes unidos» **sin precisar con qué** y el circuito usa un espacio; y «ausente» no es
«vacío» — PID-8 vacío produce `unknown`, y el prompt dice que eso es fidelidad, no pérdida.

🧑 **Pendiente**: HL7 distingue campo vacío (`||`, «no se envía información») de campo con comillas
(`|""|`, «bórrese el valor»). El modelo semántico no lo contempla. Comprobar si el corpus lo
contiene; si no, declararlo fuera de alcance por escrito.

---

## 8. La fase de clasificación: medida, no discutida 📏

Tres de los cuatro revisores decían que si las fases anteriores emiten JSON tipado con enums
cerrados y la tabla de decisión es una prioridad estricta, **meter un modelo ahí mide con cuánta
frecuencia el modelo falla al simular un `if`**.

**Ya no hace falta discutirlo: está medido.** La quinta revisión propuso operacionalizar la
frontera agente/arnés con *stubs* en vez de argumentarla, y el más informativo —`stub-copiar`: si
el binario dice `NO`, veredicto `RESULTADO_INCORRECTO_SILENCIOSO`; si no, `SIN_PROBLEMA`— se
calcula de las tandas ya hechas:

| tanda | modelo | `stub-copiar` | discrepan |
|---|---|---|---|
| peldaño 1, T=0,7 | 23/37 sens · 2/37 fa | 23/37 · 2/37 | **0 de 74** |
| peldaño 1, T=0,0 | 26/37 sens · 1/37 fa | 26/37 · 1/37 | **0 de 74** |

**Acoplamiento perfecto en 148 observaciones.** El veredicto del modelo es exactamente una función
determinista de su propio binario. Todo lo que el modelo aporta está en contestar la pregunta; el
paso de clasificar no añade ni quita nada.

**Decisión: la clasificación se queda en el modelo.** No porque aporte, sino porque no cuesta
—es el mismo turno, los mismos tokens— y sacarla obligaría a implementar y mantener la tabla de
§8 en código para no ganar nada medible. `stub-copiar` se conserva como control: si en el conjunto
reservado el modelo y el stub se separan, es que el estrato nuevo ejercita algo que este no.

⚠️ **El alcance de esto es estrecho y hay que decirlo.** El estrato de colisión solo contiene
`SIN_PROBLEMA` y `RESULTADO_INCORRECTO_SILENCIOSO`. Los otros cuatro veredictos —`FALLO_MENSAJE`,
`ENTORNO`, `RECHAZO_POLITICA`, `NO_SE`— **no se ejercitan aquí**, así que el acoplamiento perfecto
está demostrado para una distinción binaria y no para la taxonomía entera.

**La fase de clasificación es código.** La tabla, evaluada en orden:

1. evidencia insuficiente para el predicado del que depende el veredicto → `NO_SE`
2. fallo de infraestructura demostrado → `ENTORNO`
3. rechazo por política demostrado → `RECHAZO_POLITICA`
4. aceptado **y** predicado de fidelidad = NO → `RESULTADO_INCORRECTO_SILENCIOSO`
5. no aceptado por defecto del mensaje → `FALLO_MENSAJE`
6. evidencia completa y sin hallazgos → `SIN_PROBLEMA`

Con sus mapeos declarados: `propiedad → locus`, `tipo de hallazgo → categoria`, `veredicto →
accion`.

**Se mide también una variante con modelo, pero declarada por lo que es**: un diagnóstico de
obediencia a una tabla escrita, no un candidato a arquitectura. 🔍 Y con el aviso de que, si la
clasificación es código, el contraste `b` contra los peldaños altos **mezcla «separar» con
«sustituir modelo por regla»**, y hay que decirlo al interpretar.

---

## 9. Invariantes de seguridad metodológica

- Ningún componente ve etiquetas de verdad, catálogo ni causa esperada.
- No entra en ningún prompt un caso del conjunto reservado.
- El reservado no participa en: elección de peldaño, redacción de prompts, umbral de falsa alarma,
  la exclusión del operador no observable, ni la elección de agregador.
- La salida se valida sintácticamente sin alterar su contenido semántico.
- La extracción de `d2` es byte-idéntica a la de `e`, y hay un test que lo comprueba.

---

## 10. Los controles, separados por lo que son 🔍

La v1 los mezclaba, y casi todos estaban escritos contra la versión determinista —que ya los pasa—,
así que no decían nada del brazo que importa.

### 10.a Tests del arnés (código; tienen que pasar, no son experimentos)

| | |
|---|---|
| T1 | cotejo determinista sobre limpios: 0 falsos positivos *(ya pasa: 0/120)* |
| T2 | serialización distinta, misma semántica: delimitadores alternativos, escapes §2.7, subcomponentes *(ya cazó tres defectos)* |
| T3 | ausente frente a vacío, según la regla declarada |
| T4 | discrepancia única → exactamente ese `locus` |
| T5 | procedencia obligatoria: validación de esquema |
| T6 | si el comparador no corre o devuelve esquema inválido, el sistema **no puede** emitir `SIN_PROBLEMA`. Lo garantiza el orquestador, en código |
| T7 | la extracción de `d2` es byte-idéntica a la de `e` |

### 10.b Controles negativos del diseño (pueden fallar, y si fallan se para)

| | | por qué puede fallar |
|---|---|---|
| **C1** | **sesgo de posición**: poner el canónico antes del mensaje | los modelos tienen sesgo de posición documentado; si el veredicto cambia, el comparador completa patrones en vez de razonar. **Se hace el primero.** |
| **C2** | **fuga de taxonomía**: inyectar el enum de veredictos en el prompt del comparador | si la salida **no** cambia, la premisa central es falsa y separar no hace lo que se cree |
| **C3** | **ancla absurda**: un valor canónico imposible (`BirthDate: 3024-99-99`) | debe marcar `NO_COINCIDE` sin racionalizarlo como error de formato |
| **C4** | **artefacto adversario**: uno que declara discrepancia, y otro que declara coincidencia con texto incidental | prueba si el clasificador se deja arrastrar |
| **C5** | **ruido irrelevante**: filas de log largas y no causales | no deben crear hallazgos |
| **C6** | **el peldaño barato iguala al caro**: `b+` o `c1` dentro del intervalo de `d1` | si pasa, el multiagente es coste y se reporta como negativo |

**C2 y C6 son los que atacan la tesis propia.** La v1 no tenía ninguno de los dos.

---

## 11. La preinscripción, ahora con números

**Hipótesis primaria.** Algún peldaño de la escalera aumenta la sensibilidad macro por operador
para `RESULTADO_INCORRECTO_SILENCIOSO` frente al peldaño 0, sobre los 18 operadores observables,
sin pasar del techo de falsa alarma.

### 11.1 El techo de falsa alarma: **0,10**

No es arbitrario. La condición base midió **0 de 37** falsas alarmas, cuyo límite superior al 95 %
por la regla de tres es **0,081**. La pregunta binaria directa —el encuadre que la escalera toma
prestado— midió **4 de 37 = 0,108**. Poner el techo en **0,10** dice: *la arquitectura no puede ser
apreciablemente peor en falsas alarmas que el encuadre del que copia*. Un peldaño que lo pase no
gana aunque detecte más.

### 11.2 Endpoint primario y secundarios

**Primario, uno solo:** sensibilidad macro por operador sobre los 18 observables.

**Secundarios:** especificidad en limpios · exactitud de `categoria`, `locus` y `accion` ·
calibración de `confianza` con la descomposición de Murphy que ya existe · tasa de `NO_SE` correcto
· **tasa de `INDETERMINADO` por variante** · tasa de JSON inválido · latencia y tokens · llamadas
en paralelo observadas · fallos de orquestación.

### 11.3 Análisis

⚠️ **La multiplicidad, declarada antes de que nadie la pregunte.** Sobre los mismos 74 casos se
han corrido **trece condiciones**. Está declarado exploratorio y el conjunto ya estaba gastado
cuando empezó, pero trece miradas al mismo sitio es trece miradas: **ningún número de esta fase es
confirmatorio**. Los `p` que aparecen en la tabla de §1 son descriptivos. Lo confirmatorio empieza
en el conjunto de desarrollo y termina, una sola vez, en el reservado.

McNemar exacto pareado para la primaria. Diferencia de proporciones con intervalo. Multiplicidad
declarada si se prueba más de un peldaño en el reservado. **Se reportan todos los casos**,
incluidos plazos vencidos, JSON inválido y fallos de orquestación.

### 11.4 Los conjuntos

```
  estrato de colisión (152) + ablaciones (74)      ->  EXPLORATORIO. Ya gastado.
  conjunto de desarrollo NUEVO, tercera sal        ->  subir la escalera y parar
  conjunto reservado (56; 18 silenciosos, 22 limpios,
     11 fallo de mensaje, 4 politica, 1 canario)   ->  UNA evaluación, de UN peldaño
```

**Tamaño del conjunto de desarrollo: 8 casos por cada uno de los 18 operadores observables (144)
más limpios en proporción.** De las tres propuestas del panel —60–100, 100 y 294— se adopta la
tercera, porque su argumento es **cobertura por operador** y no solo potencia global: con 100
casos, una variante puede ganar por funcionar en dos o tres operadores frecuentes. Generar es
barato porque está automatizado.

### 11.5 Potencia

Se calcula **antes** de ejecutar: pares discordantes esperados, diferencia mínima detectable y
potencia de McNemar, con el tamaño ya fijado en §11.4. Si no hay potencia, se declara estimación
con intervalos y **no** prueba de superioridad.

---

## 12. La circularidad, declarada 🔍

El generador de casos, el oráculo de verdad (`rederivar.py`), el comparador determinista
(`observabilidad.py`) y los controles **comparten una sola semántica**: las reglas publicadas. Que
`observabilidad.py` tenga 0/120 falsos positivos valida que no se contradice a sí mismo; no valida
que reconstruya el circuito.

**Lo que sí es independiente, y hay que decirlo:** `comparar.py` contrasta lo previsto contra **lo
que el circuito hizo de verdad**, 327/327, y `observabilidad.py` coteja contra el canónico
**observado**, no contra la clave. Así que no es circularidad completa.

**Mitigación, y es obligatoria antes de usar `e` como adversario:** una **adjudicación manual
ciega** sobre una muestra estratificada —quien adjudique no ve ni la clave ni la salida de
`observabilidad.py`—, o una segunda implementación independiente del cotejo. Sin una de las dos,
`e` mide consistencia interna.

---

## 13. Abierto 🧑

**Para firmar antes de generar el conjunto de desarrollo:**

1. El techo de falsa alarma en **0,10** (§11.1) y la unidad de análisis (§3.4). El agregador de
   §6.3 decae con los peldaños altos: el peldaño 1 no tiene agregador, tiene una pregunta.
2. El **tamaño del conjunto de desarrollo**: ocho casos por operador, ~456 mensajes, más de tres
   horas de circuito. El generador está escrito y **no lanzado**.
3. ~~la lista de paráfrasis~~ → hecho y medido (§4.5). ~~confirmar la polaridad~~ →
   **CONFIRMADA** con predicción sellada antes (§4.6): 13 redacciones positivas entre 0,578 y
   0,794 frente a 7 inversas entre 0,000 y 0,206, separación completa.

**Resueltos desde la v2:**

- ~~clasificar los 10 operadores restantes~~ → hecho mecánicamente: 6 conformidad, 3 estructura,
  1 inferible, 1 no identificable. Control negativo 0/120.
- ~~corregir el README~~ → hecho: 56 casos, no 58.
- ~~elegir entre las formas del comparador~~ → la escalera lo resolvió antes de llegar ahí.

**Queda, y no es de esta campaña:**

4. La semántica de `|""|` frente a `||` (§7): comprobar si el corpus la contiene y, si no,
   declararla fuera de alcance.
5. El arnés no muestra `SendingApp`, `SendingFacility` ni `ProcessingId` aunque el canónico las
   lleve (§3.2). Arreglarlo cambiaría la evidencia y haría incomparable el brazo b ya medido.
6. El estrato del **acuse inservible sigue en 0/5** y la segunda pregunta no lo arregla: lo
   empeora todo. Es un hueco declarado de lo que el peldaño 1 puede prometer.
7. Las dos decisiones que venían de antes: la regla del margen, inalcanzable por potencia, y
   K3(iii), que mide sobre una confianza con un solo nivel.
