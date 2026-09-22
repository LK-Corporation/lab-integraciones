<!-- modelo: or:anthropic/claude-opus-4.8 · via: openrouter.ai · encargo: encargo_diseno13b.md · 136 s · 18196 tokens -->

## Antes de romper nada: un error de razonamiento en el encargo

El encargo (y la §6) tratan **el residuo como el número que contesta la pregunta de la fase** y a la vez como el **endpoint primario** (§6.1: "la nota del agente sobre ese subconjunto va en portada"). Pero el residuo lo define **la vía (b)**: un tipo entra en el residuo cuando el autor de la regla actualizada declara que no puede cubrirlo con regla estática. Y la §4.1 admite que (b) imprime la firma del contrato. Entonces:

- Si "no cubrible con regla estática" ≈ "requiere estado / concurrencia / evidencia fuera de traza", el residuo es **una propiedad estructural del fallo**, no una medida de capacidad del modelo. El agente puede puntuar alto en el residuo por la misma razón por la que el v3 puntúa bajo —porque el residuo se **definió** por lo que el v3 no alcanza. Eso es condicionar en el desenlace del comparador: **es la rotura 1 de la v1 (el oráculo es un brazo) reintroducida por la puerta del endpoint.**

El residuo no puede ser a la vez la pregunta *y* estar definido por la incapacidad del brazo contra el que se compara. Lo desarrollo en el punto 3, que es donde más duele.

---

## 1. El séptimo modo de fallo

**F7 · El piloto y el primario se corren con la misma capa, y la capa se afinó viendo el piloto.**

La §9 pone el piloto (paso 2) y la tanda real (paso 9) sobre **la misma capa de perturbación**, escrita por el mismo autor (tú), separadas por los pasos 3–8. Entre medias, el paso 3 mide la distribución por familia y por vía, y F1/F2 **autorizan explícitamente a cambiar la capa** si el piloto sale mal ("hay que cambiar la capa antes de contratar a nadie"). Eso significa:

- El autor observa qué familias producen silenciosos y cuáles ruido.
- Ajusta la capa para producir más silenciosos (F1) y más diversidad de familias (F2).
- La capa ajustada es la que genera el B sobre el que se puntúa el agente.

El autor **conoce el agente** (lo afinó un mes) y **conoce los diez fallos de §2**. Al afinar la capa contra "produce banco silencioso", está —sin querer— afinándola hacia la clase de silencios que **se parecen a los diez que ya sabe que el agente detecta**. No es contaminación por etiquetas (F4 la cubre); es **contaminación por selección del generador**: la capa converge hacia el territorio donde el agente ya demostró fuerza, porque ese es el territorio que el autor sabe describir.

Es exactamente el patrón que mató a la v1 (§1.3: "pedirle más tipos al autor hasta que baje el solapamiento selecciona el banco contra el comparador") **movido del autor de tipos al autor de la capa.** La emergencia elimina la inversión de función a nivel de *tipo individual*, pero no a nivel de *distribución del generador*.

**La medida barata que lo destapa —y que ya salvó el diseño una vez (predecir el propio fracaso):**

> **Sella la capa de perturbación con huella ANTES del piloto, no después.** El piloto se corre sobre la capa sellada. Si el piloto dice "esto no produce banco", eso es **un resultado sobre el proceso** (§8 ya lo admite para N), no una licencia para reescribir la capa. Si hay que tocarla, se documenta como **capa v2, huella nueva, y el piloto se repite**, y la diferencia entre la tasa de silenciosos de la capa vieja y la nueva **se publica**: si sube mucho, el autor la afinó hacia el desenlace.

Coste: una línea en el protocolo de sellado y guardar dos huellas. Cero ejecuciones extra. Es la misma jugada de "predecir el fracaso antes de medir" que la Fase 12 usó como su única protección real.

---

## 2. ¿Emergencia de verdad, o contrato con otro nombre?

Publicar la proporción por vía **es necesario pero no basta.** El problema no es cuánto viene de cada vía; es que **las tres vías miden cosas distintas y la §6 las suma en un mismo B** sobre el que se computa una única macro por tipo.

**Sobre la vía (b) = operador leído al revés.** Tu propia pregunta es correcta y la respuesta es: **casi no se diferencian, con una excepción concreta.** Una relación metamórfica "NFC y NFD dan el mismo Patient" es funcionalmente idéntica a un operador de mutación "aplica NFD" leído al revés. La distinción real no está en *de dónde sale la regla* (estándar vs catálogo) sino en **quién no la ve**:

- Operador de mutación (v1): el autor de B escribe la firma → invertible → coste, no capacidad.
- Relación metamórfica (v2): el autor de B escribe una **invariante**, y el fallo es *cualquier violación de la invariante que él no enumeró.* La invariante "AA obliga a que el recurso exista" no dice *cómo* falla; captura el fallo #1 (CE espurio), el #10 (settings no aplicados) y N fallos que no imaginaste, con una sola regla.

Esa es la diferencia real, y **es genuina**: una invariante es más pobre que un operador (no dice el mecanismo), luego captura una clase más ancha que la que el autor pudo enumerar. Pero la diferencia **se evapora si escribes invariantes tan específicas que solo una violación las dispara.** No hay forma de medir esto con la proporción por vía. Necesitas:

> **Medida:** cuenta, por relación metamórfica, **cuántos tipos distintos de B la violan.** Una invariante que captura 1 tipo es un operador disfrazado. Una que captura 5 es emergencia real. Publica esa distribución. Si la mediana es 1, la vía (b) es la v1 con capa.

**Sobre la vía (a) = tu intuición es correcta y es grave.** (a) recoge caídas, resets, acuses ausentes: **ruido por definición**. El fallo que importa (§2 #1, #6, #7, #8, #10) es *silencioso*: acusa AA, escribe algo, y lo escrito está mal. (a) es ciega a todos ellos. Luego la vía sin sesgo es también la vía sin señal. Esto no invalida (a) —sirve como cota de "cuánto es ruido"— pero **desmonta el argumento de F3**: "la cuota de (a) es la prueba de que B no es solo el contrato leído al revés" es falso, porque (a) y (b) cubren conjuntos casi disjuntos. Una cuota alta de (a) no prueba nada sobre si (b) está sesgada; solo prueba que hubo mucho ruido.

**Sobre la vía (c) y la tasa base del 1 %.** Aquí hay aritmética dura que el diseño no hace. Si la tasa base de silenciosos es 1 %, para observar ~10 silenciosos (mínimo para estimar algo) el curador necesita adjudicar a mano **~1.000 ejecuciones**. Con κ entre dos codificadores, son 2.000 adjudicaciones humanas. A eso hay que ponerle número **antes** de contratar, porque decide la viabilidad:

> **Petición:** necesito la estimación de tasa base de silenciosos del piloto (paso 3) para calcular el tamaño de muestra de (c). Sin ella, "muestra aleatoria" (§4.1c) no tiene tamaño y F1 no está realmente cerrado. Para qué: si la tasa base es 1 % y el presupuesto de curación humana es <500 adjudicaciones, la vía (c) **no puede ver silencios** y el banco vuelve a medir solo (a)+(b) = ruido + contrato. Eso es F1 disfrazado de "sí produce banco".

**¿Cuarta vía?** Sí, y es barata: **oráculo diferencial contra una implementación de referencia.** El estándar HL7→FHIR tiene mapeadores públicos (p. ej. el de HAPI/LinuxForHealth). Corres el mismo mensaje perturbado por tu circuito y por el de referencia; **divergencia en el Patient producido = candidato a fallo, sin que tú escribas la firma.** Su sesgo es la firma del *mapeador de referencia*, no la tuya ni la del contrato —un sesgo **independiente** de todos los brazos, que es justo lo que ninguna de tus tres vías tiene. Captura silencios (a diferencia de (a)) sin que enumeres invariantes (a diferencia de (b)). Su límite: solo ve fallos donde la referencia acierta y tú no; comparten bugs quedan invisibles. Pero es la única vía que ve silencios **sin imprimir una firma tuya**.

---

## 3. El residuo: la rotura principal

Ya la anuncié arriba. Desarrollo por qué es fatal y cuál es el cambio mínimo.

**El residuo está definido por la incapacidad del brazo comparador.** El autor de la regla actualizada declara qué tipos no cubre. El primario es la nota del agente sobre esos tipos. Pero "no cubrible con regla estática" es correlato casi perfecto de "el v3 puntúa bajo aquí". Estás preguntando *"¿gana el modelo donde pierden las reglas?"* con el conjunto **definido** como "donde pierden las reglas". **Esto ya se sabía desde la Fase 12** —es literalmente la rotura 1 de la v1 que declaraste muerta.

**Las tres trampas que pides que busque, las tres existen:**

- **Declarar de más / de menos.** No lo acota ningún protocolo escrito, porque la declaración es *sobre una capacidad contrafáctica* ("no podría escribir una regla") que es inverificable por construcción. La protección que propones —"y por qué", bajo protocolo— no ayuda: el autor siempre puede dar un "por qué" plausible. La única cota real es **operacional, no declarativa**: no le preguntes qué *cree* que no puede cubrir; **hazle escribir las reglas y mide qué no cubre de hecho.** El residuo pasa de ser una declaración a ser un observable: *tipos donde el v3-actualizado, entregado y sellado, detecta <mitad de instancias fuera de muestra.* Eso es la trampa de la Fase 12 (el total) resuelta de la misma forma que se resolvió entonces: sustituyendo declaración por medida.

- **¿Cambia si el autor es un modelo?** Empeora. Un humano tiene incentivo mixto (derrota digna vs script potente); un modelo generando reglas **no tiene el incentivo pero tampoco tiene el freno**: producirá reglas hasta donde su capacidad llegue, y su "declaración de no cubrible" es simplemente "no se me ocurrió", que correlaciona con la capacidad del propio modelo generador, no con la estructura del fallo. Si el generador de reglas y el agente comparten familia de modelo, el residuo mide **diferencia de andamiaje entre dos instancias del mismo modelo**, no capacidad del agente. Registra la familia del autor de reglas igual que registras la del curador.

- **Residuo vacío.** Si todo B es cubrible con reglas, **es un resultado publicable y fuerte**: dice que la emergencia produjo fallos que las reglas alcanzan, es decir, que el modelo no aporta residuo en este dominio. No es "un banco que no puede contestar" (ese era el caso de la v1, donde el vacío estaba garantizado *por construcción*). Aquí el vacío es *medido*. La diferencia con la Fase 12: allí el vacío se sabía antes de correr; aquí no. **Publícalo como el negativo limpio que es.** Lo que sí sería un banco que no contesta es el caso simétrico: residuo = todo B, porque entonces (b) escribió invariantes tan específicas que el v3 no alcanza ninguna → mídelo con el diagnóstico del punto 2 (tipos por invariante).

**Cambio mínimo del endpoint:**

> Primario = detección del agente sobre **B entero, macro por tipo, con veto de falsas alarmas** (que ya tienes en §6). El residuo **baja al lado**, como descriptor, y se define **por medida** (lo que el v3-actualizado no alcanza fuera de muestra), no por declaración. La pregunta de la fase la contesta la conjunción: *"el agente detecta X% de B; de ese B, el Y% resultó no alcanzable por el v3 puesto al día; el agente detecta Z% de ese Y."* Tres números al lado, ninguno definido por el desenlace del otro. Portada = X con su veto.

Esto cuesta cero ejecuciones extra (el v3-actualizado ya se corre, §6.4) y quita el único mando del diseño que reintroduce la rotura que mató a la v1.

---

## 4. El brazo del prompt afinado

**El argumento de simetría es válido para el promedio y falso para la cola.** Los números del paso 29 lo dicen ellos mismos: fuera del silencioso, genérico ≥ afinado; **dentro del silencioso, afinado pasa de −0,229 a +0,500.** Si B por emergencia sobre-representa el silencioso (que es *el objetivo declarado de la fase*, §2), entonces el mes de afinado **sí** compra ventaja en B, y no es la ventaja del contrato: es ventaja en la clase que domina el primario.

La pregunta correcta no es "¿es simetría?" sino **"¿qué hay en los 17.136 caracteres que no sea el contrato?"** y tú no puedes contestarla desde este encargo porque no he visto el prompt. Pero el diseño puede contestarla barato:

> **Petición:** necesito el prompt afinado (17.136 car) y el genérico (1.174) para hacer un diff estructural. Para qué: separar cuánto del afinado es *contrato de la transformación* (que el autor de reglas también recibe → simetría legítima) y cuánto es *heurística de detección* (ejemplos de fallos, patrones de traza, pistas de dónde mirar → ventaja indebida, porque el autor de reglas no recibe heurísticas de detección, recibe el contrato). Si el afinado contiene ejemplos de los diez fallos de §2, es contaminación directa (F4) y el brazo justo es el genérico + contrato, no el afinado.

Mientras tanto, el brazo justo **no es "el afinado"** sino **"el afinado con la parte no-contrato tachada"**, que es exactamente el `v3-invariante` mental aplicado al prompt. Como no lo tienes construido, el sustituto barato es: **corre los dos (afinado y genérico) y reporta la diferencia por clase (ya está en §6.5).** Si el afinado gana *solo* en silencioso, has probado que el mes compró detección de silencio, no contrato —y eso es un hallazgo, no un defecto, siempre que lo llames por su nombre y no "simetría".

---

## 5. El tamaño que no se elige

La regla que cierra la puerta de "mirar primero, decidir después" no es un N fijo (no puedes fijarlo sin ver B) sino **fijar la función que va de N observado a decisión, antes de ver N.** Preinscribe una tabla, no un número:

> - N ≥ N_alto → primario se publica como primario.
> - N_bajo ≤ N < N_alto → primario se publica **con intervalo y etiqueta de baja potencia**, computado con la varianza entre-tipos heredada de la Fase 12 (0,43 / 0,31).
> - N < N_bajo → descriptivo, y "la capa no produce banco" es el resultado.
>
> N_alto y N_bajo se derivan **de la varianza de Fase 12**, no se eligen a mano: N_alto = el N que da IC de ±0,15 al 95% con σ_entre = 0,43; N_bajo = el N por debajo del cual el IC cubre tanto el negativo (25%) como un positivo trivial. Ambos son cálculos, no decisiones de 🧑.

Eso convierte el "🧑 pone el número" de §11.2 en "🧑 firma la tabla y la potencia diana"; el número sale de la aritmética. La puerta se cierra porque la **regla de decisión** está sellada antes del piloto, aunque el N no se conozca. Es el mismo principio que preinscribir un umbral sin conocer el dato.

Corolario que falta en §8: **k por tipo también entra en la potencia.** "Tipos con una instancia van aparte" (§8) es correcto, pero no dices el k mínimo para que un tipo cuente en la macro. Con σ_intra del agente = 0,057, k=2 ya distingue capacidad de azar a nivel de tipo; fíjalo en 2 y séllalo, o la macro la dominan tipos con k=1 promovidos por ruido.

---

## 6. El orden: qué falta, qué sobra, qué mata

**El que más probablemente mata la fase es el paso 2 (piloto), y ya está casi el primero. Bien.** Pero el paso 1 (relaciones metamórficas) debería ir **con** el sellado de la capa, no antes de él, por el F7 de arriba: si la capa se sella después del piloto, el piloto no protege nada.

**Falta un paso, y es barato y letal:** entre el 3 y el 4, **el oráculo diferencial contra referencia** (cuarta vía, punto 2). Es la única medida que puede decir, *antes de curar*, si existen silencios que ni (a) ni (b) ven. Si el diferencial contra HAPI encuentra ~0 divergencias que tus invariantes no cubrían ya, entonces (b) sí captura el silencio y la fase es viable; si encuentra muchas, tus invariantes son ciegas y el residuo va a estar mal medido. Cuesta una pasada del corpus por un mapeador de estantería. **Adelántalo al puesto 3.5.**

**Sobra, o mejor dicho está mal colocado, el paso 6 (el negativo firmado).** Firmar el 25% *antes* de conocer N y la varianza de B es firmar un umbral sobre una escala que no conoces. El negativo debe firmarse como **regla** en el paso 6 (la tabla del punto 5), pero el **número absoluto de tipos** que corresponde a ese 25% no existe hasta el paso 3. No lo muevas; **desdóblalo**: regla del negativo en 6, aritmética del negativo tras 3.

**Orden con los cambios mínimos:**

```
1. relaciones metamorficas + SELLADO DE LA CAPA con huella   <- sella la capa AQUI (F7)
2. capa sellada + PILOTO (~200)                              <- puede decir "no produce banco"
3. distribucion por familia y por via (a)/(b)/(c) + tasa base <- da el tamaño de muestra de (c)
3.5 oraculo diferencial vs referencia (cuarta via)           <- unica que ve silencio sin firma propia
4. inductor calibrado en A
5. adjudicacion, ideal_b, kappa
6. regla del negativo (tabla N->decision) + aritmetica tras paso 3
--- nada encargado hasta aqui ---
7. curacion a ciegas
8. congelar, preinscribir, sellar
9. UNA pasada
```

---

## Resumen de roturas y su coste

| # | rotura | gravedad | cambio mínimo | coste |
|---|--------|----------|---------------|-------|
| **A** | el residuo está definido por la incapacidad del v3 = rotura 1 de la v1 reintroducida en el endpoint | **mata la fase** | residuo baja a descriptor, se define por medida (v3-actualizado fuera de muestra), primario = B entero con veto | 0 ejecuciones |
| **F7** | la capa se afina viendo el piloto → generador seleccionado hacia la fuerza del agente | alta | sellar la capa antes del piloto, publicar diff si se rehace | 1 huella |
| **B** | vía (b) puede ser operador disfrazado si las invariantes son específicas | alta | medir tipos-por-invariante, exigir mediana >1 | 0 |
| **C** | vía (a) es ruido, (c) sin tamaño si tasa base 1% | alta | cuarta vía (diferencial); calcular muestra de (c) desde el piloto | 1 pasada |
| **D** | residuo por declaración es inverificable; peor si el autor es modelo | media | declaración → medida; registrar familia del autor de reglas | 0 |
| **E** | N y negativo firmados como números sin conocer la escala | media | firmar la tabla N→decisión y k≥2, no el número | 0 |
| **F** | afinado gana en silencioso ≠ simetría del contrato | media | diff del prompt; llamar al hallazgo por su nombre | necesito el prompt |

**Lo que pido para cerrar del todo:** (1) tasa base de silenciosos del piloto, para dimensionar (c); (2) el prompt afinado y el genérico, para el diff contrato/heurística. Ambos con su para-qué arriba. Nada más de A, agente, puntuador o reservado.

**Lo que no toco:** el veto de falsas alarmas (§6), el sellado de invariantes antes de correr, el estrato aparte de los diez, la herencia del §10. Están bien.