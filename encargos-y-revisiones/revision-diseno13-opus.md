<!-- modelo: or:anthropic/claude-opus-4.8 · via: openrouter.ai · encargo: encargo_diseno13.md · 95 s · 12214 tokens -->

# Rompiendo la v1 de la Fase 13

Voy directo. Hay un error de razonamiento en la base del dimensionado que contamina §3, §4 y §7 a la vez. Lo pongo primero porque cambia el resto.

---

## 0. El error que hay que decir antes que nada: el inductor y el adversario son el mismo instrumento medido dos veces

El diseño trata dos cosas como independientes cuando son la misma:

- **El adversario congelado** (`triador_regex_v3.py`) detecta un tipo ⟺ ese tipo tiene una firma sintáctica capturable por regex.
- **El inductor de mecanicidad** clasifica un tipo como mecánico ⟺ ese tipo tiene una firma sintáctica inducible por diff.

Son operacionalmente **casi la misma medida**. Un tipo mecánico según el inductor es, por construcción, un tipo que un adversario actualizado va a pillar. Entonces:

> El "DiD por cuartil de mecanicidad" (§6.2, "donde vive la respuesta") es, en el cuartil mecánico, **una tautología**: ahí el adversario gana por definición del cuartil. Y en el cuartil no-mecánico, el resultado depende enteramente de si el inductor es débil o si el tipo es genuinamente no-mecánico — la ambigüedad que tú mismo señalas en §5.5/pista 2 y que el diseño **no resuelve**.

Consecuencia dura: **la curva de degradación por mecanicidad no puede distinguir "el modelo generaliza" de "mi inductor es más flojo que triador_regex_v3.py".** Si el inductor es más débil que el adversario actualizado (muy probable: el adversario lo escribe un humano viendo B, el inductor es diffs automáticos), entonces habrá tipos que el inductor llama "no mecánicos" y el adversario actualizado sí pilla. En esos tipos el modelo perderá contra la regla actualizada, y la curva parecerá plana o negativa — no porque el modelo no generalice, sino porque **calibraste el eje x con un instrumento más débil que el brazo contra el que compites en el eje y.**

Esto es exactamente el fallo de la Fase 12 con otra cara: entonces el instrumento de construcción (operadores declarativos) definía lo detectable; ahora el instrumento de medida del eje (inductor) define lo "no mecánico", y **el mismo autor controla ambos ejes**.

---

## 1. El quinto modo de fallo, con su medida barata

**Modo de fallo #5: el inductor y el adversario tienen distinta capacidad, y esa diferencia se lee como señal de generalización.**

Formulado como te salvó en la Fase 12 — es un defecto de **construcción del instrumento**, no del modelo:

> El eje de mecanicidad y el brazo adversario son dos regex-inductores de fuerza desconocida y distinta. El endpoint (§6.2) mide implícitamente `capacidad(adversario_actualizado) − capacidad(inductor)`, no `capacidad(modelo) − capacidad(reglas)`. Un modelo que no generaliza nada dará DiD positivo en el cuartil "no mecánico" si el inductor es más flojo que el adversario.

**La medida barata, semana 1, sin agente:**

Corre **inductor y adversario actualizado sobre A** (63 operadores, ya existen, con clave conocida) y compara **tipo a tipo cuáles detecta cada uno.**

- Si detectan el mismo conjunto de tipos → los instrumentos están calibrados; el eje es usable.
- Si el adversario pilla tipos que el inductor no (esperado) → **mide el gap sobre A y publícalo como banda de incertidumbre del eje x.** Cualquier DiD dentro de esa banda no es interpretable.
- Si el gap es grande → el eje de mecanicidad **no sirve como está** y hay que arreglarlo antes de encargar B.

Coste: cero construcción nueva. Los cuatro artefactos ya existen. Es un `join` de dos columnas de detección sobre A.

Además, esto ataca directamente tu pista ("un inductor por diff que no encuentre regla puede ser 'no mecánico' o 'inductor flojo'"): **el gap inductor↔adversario sobre A es precisamente la cuantificación de la flojera del inductor.** Sin esa medida no puedes leer la curva.

---

## 2. ¿Correcciones incorporadas o tapadas?

### Q1 vs Q2 (§2): Q1 contamina, y peor de lo que crees

Separarlas en la tabla no basta. El problema es la **asimetría de fecha de congelación**:

- Adversario congelado: escrito contra A, ciego a B → juega en desventaja legítima.
- Adversario actualizado: escrito **viendo B** → juega con ventaja total.
- Modelo: congelado en Fase 12, ciego a B → misma desventaja que el congelado.

Q2 compara modelo-ciego-a-B contra regla-que-vio-B. Eso es lo que **querías** (¿detecta el modelo lo que no se puede escribir en regla?), pero el resultado honesto de Q2 casi seguro será **negativo**, y no por falta de capacidad del modelo: un humano que ve los 30 tipos de B y escribe regex específicas es, salvo tipos genuinamente no-mecánicos, imbatible. **Q2 está diseñada para que el modelo pierda salvo que exista un residuo no-mecánico real** — que es justo lo que §6.5 (detecciones propias) mide de forma mucho más limpia.

Recomendación: **Q2 como está no aporta sobre §6.5.** El número honesto es §6.5 (tipos que el modelo pilla y ningún brazo de reglas pilla). Q2 es §6.5 vestida de contraste continuo y arrastrando el problema del inductor. **Preinscribe §6.5 como primario de capacidad, no el DiD-Q2.**

### El oráculo de mecanicidad (§3): implementable, pero mal especificado

Es implementable (diffs sintácticos, sí). Lo que lo rompe, además del §1:

1. **No hay definición de "regla inducida".** ¿Un solo diff literal? ¿Una familia de diffs con hueco? ¿Cuántos ejemplos ve el inductor por tipo — 1, 5, todos? Con k=5 casos, un inductor que ve los 5 puede sobreajustar y llamar "mecánico" a casi todo; uno que ve 1 llamará "no mecánico" a casi todo. **La fuerza del inductor es un hiperparámetro libre que decides tú, el mismo que escribe el puntuador.** Eso es un grado de libertad de investigador sin preinscribir.
2. **"Cuartiles de mecanicidad" presupone que la mecanicidad es continua y ordenable.** Pero acabas de decir (§7, §3) que para una regla cubrir un tipo es **binario** (varianza intra 0,0000). Entonces la mecanicidad medida por el inductor será **también casi binaria** — no vas a tener cuartiles, vas a tener dos montones. El "análisis por cuartiles con 7-8 tipos" se cae: tendrás ~15 mecánicos y ~15 no, y la partición en 4 será artificial.

Arreglo mínimo: **preinscribe la fuerza del inductor** (cuántos ejemplos ve, qué clase de diff admite) **y valídala contra A antes de tocar B** (§1). Y sustituye "cuartiles" por **"score continuo del inductor + binario detectado/no por el adversario congelado"**, y reporta el DiD como regresión sobre el score, no en 4 cajas.

### Solapamiento A↔B "sin decirle por qué" (§5.2): no es practicable

Pedir "N más sin decir por qué" a un autor competente **no funciona dos veces**. La primera vez cuela. Si vuelves con "necesitamos 10 más" después de recibir 30, el autor infiere que algo de los 30 no valió, y la hipótesis obvia que se le ocurre es "se parecían demasiado a algo" → empieza a buscar novedad deliberadamente → **contaminas el eje de mecanicidad en la dirección contraria** y ya no es ciego. La deducción es casi inevitable con un autor competente, que es justo el que quieres.

Además, medir solapamiento A↔B **con el mismo inductor** hereda el problema §1: mides "el inductor de A reproduce el de B", no "B ⊂ A conceptualmente".

Arreglo: **sobre-encarga desde el principio.** Pide 40 tipos, filtra post-hoc por solapamiento, analiza sobre los ~30 que sobreviven, y **preinscribe el criterio de exclusión** (p.ej. "se excluye todo tipo cuya firma coincida >X% con una firma inducida de A"). Nunca vuelvas a por más. El coste marginal de 10 tipos extra es una fracción del riesgo de romper la ceguera.

---

## 3. El endpoint (§6): tiene su propia trampa, distinta de la Fase 12

El DiD por tipo con macro está bien pensado contra el fallo de la Fase 12 (agregación limpios+silenciosos). Pero introduce uno nuevo:

**La macro por tipo con detección binaria por-regla convierte el DiD en una diferencia de dos proporciones de tipos, y con N=30 eso es ruidoso y sensible a la composición.**

Como la regla tiene varianza intra 0 (cubre o no cubre un tipo), `S_regla(B)` es literalmente **la fracción de tipos de B que la regla cubre**. `S_regla(A)` igual sobre A. El DiD contra la regla es entonces:

```
DiD = [S_mod(B) − frac_tipos_B_cubiertos] − [S_mod(A) − frac_tipos_A_cubiertos]
```

El término `frac_tipos_B_cubiertos` **depende enteramente de la composición mecánica de B**, que es lo que el inductor supuestamente mide pero que tiene su propia varianza de muestreo con N=30. Es decir: **el endpoint y el eje de estratificación comparten la misma fuente de ruido (qué tipos entraron en B).** Los cinco desgloses obligatorios ayudan pero **no** cortan esto, porque el desglose #2 (DiD por cuartil) hereda el problema §1 y el #3 (distribución del adversario) es descriptivo.

Lo que **sí** falta en los cinco desgloses: **el intervalo de confianza del DiD que propague la incertidumbre de composición de B.** Con N=30 y detección binaria por tipo, un bootstrap sobre tipos te dará un IC ancho. Si el IC cruza cero (probable), la respuesta es "no concluyente con este N", no un signo. Añade eso como desglose #6 obligatorio.

---

## 4. El tamaño (§7): los números no aguantan para lo que quieres medir

El razonamiento "toda la potencia viene de N" es **correcto** dado varianza intra 0 en la regla. El problema no es la potencia global, es el **análisis por cuartiles**, que es donde dices que vive la respuesta.

- 7-8 tipos por cuartil, con métrica **binaria por tipo** para la regla → cada cuartil estima una proporción con n=7-8. El error estándar de una proporción con n=8 es ~0,18. **No puedes distinguir un cuartil al 0,25 de uno al 0,50.** La "curva de degradación por mecanicidad", que era el argumento estrella de §2 ("una curva es más difícil de falsear que un umbral"), **no tiene resolución con N=30.**
- Peor con el §2 del inductor casi-binario: si la mecanicidad sale bimodal, no tienes 4 cuartiles, tienes 2 grupos, y la "pendiente" es una recta entre 2 puntos.

Números que sí aguantan: el **global** (§6.5 detecciones propias, y DiD global con bootstrap) es razonable con N=30. Lo que no aguanta es la **estratificación en 4**, que es tu endpoint principal declarado.

Decisión honesta: o subes N (a ~48-60 para 12-15 por cuartil, coste real en encargo de tipos), o **bajas la ambición del endpoint** de "curva/cuartiles" a "detecciones propias + DiD global con IC". Yo bajaría la ambición: la curva era ilusoria por §1 de todos modos.

k=5 está bien. El argumento es correcto.

---

## 5. Lo que haría distinto

El diseño está **bien encaminado en método** (orden de la Fase 12, medidas baratas primero, ceguera) pero **mal encaminado en la pregunta**, porque intenta rescatar Q2/DiD/cuartiles cuando el instrumento que los sostiene (el inductor) es un regex-inductor de fuerza libre controlado por el mismo autor. Estás reconstruyendo el sesgo de la Fase 12 en el eje de medida en vez de en el corpus.

**Reescritura que costaría una tarde y contesta la pregunta real:**

1. **Elimina el eje de mecanicidad como instrumento propio.** No inventes un tercer regex-inductor. **Usa el adversario actualizado como definición operativa de "mecánico".** Un tipo es mecánico ⟺ un humano competente que ve B puede escribir una regex que lo pilla. Eso es honesto, no tiene fuerza libre oculta, y es exactamente la frontera que importa ("¿se puede escribir una regla?").

2. **El endpoint es un único número, §6.5 elevado a primario:** de los N tipos de B, ¿en cuántos el modelo detecta **y el adversario actualizado (humano viendo B) no puede**? Ese conjunto es, por definición, "fallos detectables sin regla estática escribible". Si es >0 y replicable, Q2 tiene respuesta positiva **sin ninguna curva ni cuartil ni inductor**. Si es 0, la respuesta es negativa y limpia.

3. **Q1 aparte, como operativa:** modelo vs regla congelada, DiD global con bootstrap. Sin pretensión científica.

4. **La única medida semana-1 que de verdad importa** pasa a ser: adversario actualizado vs inductor... no — pasa a ser **el solapamiento conceptual A↔B juzgado por dos personas ciegas entre sí**, no por diffs. Porque el riesgo #5.2 (B⊂A) es real y ningún regex-inductor lo detecta bien (mide firma, no concepto).

Con esto desaparecen: el hiperparámetro de fuerza del inductor, la tautología del cuartil mecánico, la falta de resolución de N=30 en cuartiles, y la ambigüedad "no-mecánico vs inductor-flojo" — **los cuatro problemas salen del mismo sitio: haber introducido un instrumento de medida bajo tu control para calibrar el eje contra el que compites.**

---

## Resumen accionable

| # | problema | gravedad | arreglo | cuándo |
|---|---|---|---|---|
| §1/§5 | inductor y adversario son el mismo instrumento con fuerza distinta; el DiD por cuartil mide el gap entre ellos, no el modelo | **fatal** | medir gap inductor↔adversario sobre A; si es grande, eliminar el eje | sem 1 |
| §2-Q2 | Q2 diseñada para que el modelo pierda; redundante con §6.5 | alto | §6.5 como primario de capacidad, no DiD-Q2 | diseño |
| §3 | fuerza del inductor = hiperparámetro libre no preinscrito; mecanicidad será binaria, no cuartilable | alto | preinscribir fuerza + validar en A, o eliminar inductor | sem 1 |
| §5.2 | "N más sin decir por qué" no es practicable dos veces | medio-alto | sobre-encargar 40, excluir post-hoc con criterio preinscrito | diseño |
| §6 | macro por tipo comparte fuente de ruido (composición de B) con el eje | medio | desglose #6: IC del DiD por bootstrap sobre tipos | diseño |
| §7 | N=30 no da resolución para cuartiles (el endpoint estrella) | alto | bajar ambición a global+detecciones propias, o subir N a ~50 | diseño |

La firma 🧑 no debería caer hasta que corra la medida de §1 sobre A. Es la barata que este mes te ahorra el mes.