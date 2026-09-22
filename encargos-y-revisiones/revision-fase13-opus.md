<!-- modelo: or:anthropic/claude-opus-4.8 · via: openrouter.ai · encargo: encargo_fase13.md · 100 s · 8700 tokens -->

# Fase 13 — crítica de diseño

Antes de nada, un error de razonamiento en el encargo que hay que corregir porque contamina casi todo lo demás.

**El diseño propuesto confunde dos preguntas distintas y las mete en el mismo Conjunto B.** «¿Generaliza el modelo a fallos sin regla escrita?» y «¿el adversario congelado aguanta fuera de su dominio?» no son la misma medición, y peor: la primera no es contestable sin una condición que el diseño no impone. Si el autor ciego escribe tipos de B que *también* tienen firma mecánica (tu propio punto 5.2), entonces "generalizar a B" y "reconocer firmas nuevas del mismo tipo" son indistinguibles, y vuelves a la Fase 12 con más pasos. La pregunta correcta no es sobre B en abstracto: es sobre **una partición de B que ni el autor ciego controla ni tú controlas**. Lo desarrollo abajo.

---

## 1. La pregunta

**«¿Generaliza a tipos no vistos?» está mal planteada como binario, y el laboratorio permite una mejor.**

El problema de "generalizar a lo no visto" es que "no visto" es una propiedad del *entrenamiento*, y aquí no hay entrenamiento: `qwen3-coder:30b` es un modelo congelado que no vio ni A ni B. Lo "no visto" es respecto al **autor del adversario y del catálogo**, no respecto al modelo. Entonces la pregunta real es:

> **¿Depende el rendimiento del modelo de que exista una regla escrita para ese tipo de fallo, o no?**

Y esa sí la contesta el montaje, pero solo si se mide como **diferencia de diferencias**, no como nivel:

- Δ_adversario = rendimiento(A) − rendimiento(B)
- Δ_modelo = rendimiento(A) − rendimiento(B)
- **El endpoint es Δ_adversario − Δ_modelo.**

Si el adversario cae mucho de A a B y el modelo cae poco, esa brecha *es* el valor del modelo, y es inmune a que B resulte fácil o difícil en términos absolutos. Lo que te salva del sesgo de la Fase 12 no es medir en B: es medir la **degradación relativa** entre A y B de cada brazo. Un B fácil hunde el numerador de ambos por igual; la resta sobrevive.

**Pregunta mejor, que el montaje permite gratis:** en lugar de "¿generaliza?", mide **la pendiente de degradación por distancia al catálogo**. Requiere que el autor ciego etiquete cada tipo de B con algo que definirás en §2. Convierte un sí/no frágil en una curva, y una curva es mucho más difícil de falsear por accidente de construcción.

---

## 2. Cómo fracasaría esta fase, y la medida barata que lo destapa antes

Cuatro modos de fallo. El primero es el tuyo; los otros tres no los has nombrado y al menos uno es tan letal como el de la Fase 12.

### 2.1 El autor ciego escribe tipos igual de mecánicos (el que ya ves)

Tu instinto es correcto y tu miedo también: pedirle "que no sean mecánicos" le filtra la respuesta. La solución no es instruirle sobre la propiedad que mides, sino **hacer que la propiedad se mida sola, después, sin que él la conozca**.

**Medida barata (semana 1, antes de correr nada):** define un **oráculo de mecanicidad ciego al veredicto**. Es un tercer brazo trivial —un generador de reglas *automático*— que, dado el par (entrada limpia, entrada mutada) de cada tipo de B, intenta inducir un discriminador por diff sintáctico sin ver el catálogo. Mides, por tipo de B, si ese inductor lo pilla. Eso te da un eje objetivo "mecanicidad" que **no depende de tu adversario ni del modelo**. Ahora:

- El autor ciego no recibe ninguna instrucción sobre mecanicidad.
- Tú clasificas B post-hoc en cuartiles de mecanicidad usando el inductor.
- La pregunta de §1 se responde **dentro de cada cuartil**.

Si todo B cae en el cuartil mecánico, no has aprendido nada nuevo — **pero lo sabes en la semana 1 y no el último día**, porque el inductor corre sin agente y sin adversario. Coste: un script de diffs. Ese es el destapador barato que te faltaba.

### 2.2 El autor ciego, sin querer, replica operadores de A (el fallo simétrico, y peor)

Le das "el circuito y el contrato". El contrato *induce* el catálogo: hay un número finito de cosas que pueden ir mal en un ADT^A01→Patient, y 63 operadores ya cubren buena parte. Un autor competente reinventará operadores de A **sin verlos**, porque el dominio es pequeño. Entonces B no es ciego respecto al adversario: es A con otros nombres, y el adversario congelado gana porque las firmas coinciden. Interpretarías "las reglas generalizan" cuando en realidad "B ⊆ A semánticamente".

**Medida barata:** solapamiento de firmas A↔B, calculado con el mismo inductor de §2.1 aplicado ahora a A. Para cada tipo de B, ¿qué fracción de sus casos los detecta una regla inducida *de A*? Si es alta, B está semánticamente contaminado por A y hay que devolvérselo al autor pidiendo tipos adicionales — sin decirle por qué, solo "necesitamos más N". Esto también es semana 1, sin agente.

### 2.3 El estrato secundario (fallos reales) mata la fase entera si se mezcla

Ya lo admites: el autor del laboratorio los conoce. Eso no es "una contaminación menor": si entran en el endpoint primario, **reintroducen exactamente el sesgo de la Fase 12** porque el adversario congelado pudo haber sido afinado, consciente o no, contra fallos que el mismo autor conocía. Va aparte por completo (§6).

### 2.4 El adversario congelado tiene cobertura desigual sobre B por azar

Con N tipos y un adversario de 63 reglas, es probable que **algunas reglas de A disparen sobre algunos tipos de B por coincidencia estructural** y otras no. El resultado agregado de "el adversario en B" será una mezcla de aciertos-por-suerte y ceros. Si N es pequeño, el resultado del adversario en B es casi puro ruido de composición.

**Medida barata:** antes de correr el agente, corre solo el adversario congelado sobre B y **mira la distribución tipo a tipo**, no la media. Si es bimodal (pilla 4 tipos al 100%, 0% en el resto), sabes que tu N es demasiado pequeño para que la media signifique algo, y lo sabes gratis.

---

## 3. El adversario congelado

**No es deshonesto congelarlo; sería deshonesto reportar *solo* el congelado.** Miden cosas distintas y ambas son la verdad:

| Brazo | Qué mide | Qué respondería |
|---|---|---|
| Adversario **congelado** (contra A) | valor del modelo *hoy*, frente a un sistema de reglas que nadie ha tocado | "¿el modelo aporta sin mantenimiento?" |
| Adversario **actualizado** (reglas escritas contra B tras verlo) | el techo de lo que un integrador diligente lograría con reglas | "¿el modelo aporta *incluso con* mantenimiento?" |

El congelado es el brazo honesto para la pregunta de §1 (regla-escrita vs no). El actualizado es el **límite superior de la competencia**: si el modelo pierde contra el adversario actualizado pero gana contra el congelado, tu conclusión es *"el modelo vale exactamente lo que cuesta escribir las reglas que le faltan"* — que es la conclusión operativa real y mucho más útil que un sí/no.

**Condición de honestidad del actualizado:** quien escribe las reglas nuevas ve B **pero no ve los veredictos del modelo sobre B**. Si no, ajusta contra el agente y no contra el dominio. Y se congela *antes* de destapar el reservado, igual que en Fase 12.

**Contradicción a tu diseño:** propones el congelado como "el núcleo". Es el núcleo del *procedimiento* (va primero, ya existe), pero no debe ser el núcleo del *reporte*. Sin el actualizado, no puedes distinguir "el modelo generaliza" de "las reglas eran perezosas".

---

## 4. Endpoint y desglose obligatorio

**Endpoint primario:** diferencia de diferencias en **detección de fallo silencioso**, en **puntos del puntuador firmado**, con la macro por tipo como unidad:

```
DiD = [S_modelo(B) − S_adversario(B)] − [S_modelo(A) − S_adversario(A)]
```

En unidades del puntuador (los +0,873/+0,629 de Fase 12). Positivo = el modelo degrada menos que las reglas al salir del catálogo = el valor buscado.

**Desglose obligatorio, publicado junto al endpoint, no debajo:**

1. **Dos estratos nunca agregados:** silenciosos y limpios. La lección literal de la Fase 12 es que agregar mata el hallazgo. La tasa de falsa alarma en limpios va como endpoint *secundario con veto*: un brazo con más falsas alarmas no puede "ganar" por detección aunque el DiD lo diga.
2. **DiD por cuartil de mecanicidad** (§2.1). Es aquí donde vive la respuesta de verdad.
3. **Distribución tipo a tipo del adversario en B**, cruda (§2.4).
4. **Los dos adversarios** (congelado y actualizado) lado a lado.
5. **Detecciones propias del modelo:** los tipos de B donde el modelo detecta y *ningún* brazo de reglas —congelado ni actualizado— lo hace. En Fase 12 esto fue 1 de 55 y ni siquiera contaba. Es el número más honesto de todos y debe ir en portada.

**Regla anti-Fase-12:** ningún número agregado sobre limpios+silenciosos aparece en el abstract. La resta que salió "casi cero" está prohibida como endpoint.

---

## 5. Tamaño y potencia

Aquí hay un problema estructural que debes aceptar antes de calcular nada.

**La unidad de Fase 12 era la macro por operador con *un caso por operador* en el reservado.** Eso significa que cada "media por operador" era un solo Bernoulli. No tenías potencia dentro de operador; toda tu potencia venía de tener 18 operadores. Con ese diseño, N tipos de B con 1 caso cada uno te da un test sobre N observaciones binarias pareadas (modelo vs adversario por tipo). Para detectar "el adversario se hunde" (digamos modelo detecta ~55%, adversario ~15% en B) con un test de McNemar pareado, potencia 0.8, α 0.05:

- necesitas del orden de **N ≈ 15–20 tipos** *si* el efecto es tan grande como sugieres, con **≥1 caso por tipo** — pero eso te deja ciego al ruido intra-tipo del §2.4.

**Recomendación firme:** rompe la herencia de "un caso por operador". Pon **k ≥ 5 casos por tipo** (variando el paciente/mensaje base, no la regla), y usa un **modelo mixto: efecto aleatorio por tipo, efecto fijo brazo×estrato**. Esto te da:

- estimación de la varianza intra-tipo (destapa §2.4 estadísticamente),
- potencia para el DiD por cuartil, que es el análisis que importa y que parte N en 4.

**Números concretos para preinscribir:** N = 20 tipos, k = 8 casos/tipo = 160 casos en B, más 22 limpios equivalentes. Con 20 tipos repartidos en 4 cuartiles de mecanicidad quedan 5 tipos/cuartil — al límite de lo interpretable. Si el análisis por cuartil es central (lo es), sube a **N = 28–32**. Si el autor ciego no puede producir tantos tipos genuinamente distintos, esa es en sí una señal (§2.2): el dominio no admite más, y entonces la pregunta de generalización tiene techo bajo y hay que decirlo.

**El cálculo de potencia debe hacerse sobre el DiD, no sobre "el adversario en B".** Preinscribe el MDE en puntos del puntuador. Sin banco no puedo darte la varianza real; **pide la varianza intra-operador de A de la Fase 12** para anclar el cálculo — eso no es catálogo ni clave, es una dispersión ya medida, y sin ella el número de potencia es inventado.

---

## 6. El estrato de fallos reales

**Merece la pena, pero jamás en el endpoint, y no como "estrato" sino como sección aparte con estatus epistémico distinto.**

La contaminación es real y no removible: el autor los conoce y pudo haber sesgado el adversario contra ellos. Por tanto:

- **No entra en el DiD.** Ni en el congelado ni en el actualizado como fuente de reglas.
- Se reporta como **estudio de caso, n pequeño, cualitativo**, con una tabla de "qué detectó cada brazo" caso a caso, sin agregación y sin test.
- **Valor real:** es el único sitio donde ves fallos *sin firma diseñada por nadie* — precisamente lo que B intenta simular artificialmente. Si el modelo pilla el `CE` no conforme o el 404-donde-tocaba-401 y el adversario no, eso es evidencia *ilustrativa* fuerte aunque no inferencial.
- **Blindaje contra la contaminación en la conclusión:** la frase que redactes solo puede decir "en 8 fallos reales observados, el modelo detectó X, el adversario Y" — nunca "el modelo generaliza a fallos reales". La contaminación mata la generalización pero no mata la observación puntual.

Si tuviera que elegir: **dentro, como apéndice observacional etiquetado, fuera del claim principal.** Tirarlo pierde el único dato con validez ecológica que tienes.

---

## 7. Qué mediría la primera semana para no construir sobre arena

Todo esto corre **sin el agente y sin destapar nada**, y cualquiera de los cuatro puede abortar la fase antes de gastar el mes:

1. **Inductor de mecanicidad sobre A** (§2.1). Confirma que reproduce el resultado de Fase 12 (reglas automáticas ≈ 100% sobre A). Si no lo reproduce, tu instrumento de "mecanicidad" está roto y todo lo demás es humo. *Coste: 1 día.*
2. **Solapamiento semántico A↔B** (§2.2). Inductor de A aplicado a B. Si >50% de B es cubierto por reglas de A, B no es ciego; se devuelve pidiendo más N sin explicar. *Coste: medio día una vez B existe.*
3. **Distribución del adversario congelado sobre B, tipo a tipo** (§2.4). Bimodal → N insuficiente, súbelo antes de correr el agente. *Coste: horas.*
4. **Cuartilización de B por mecanicidad y conteo por cuartil.** Si B entero cae en un cuartil, la pregunta de §1 es incontestable con este B — y lo sabes ahora. *Coste: horas.*

Y una comprobación de proceso, no de datos: **confirma que el adversario actualizado se puede escribir sin ver los veredictos del modelo.** Si el flujo de trabajo no lo permite físicamente (mismo repo, mismos logs), estás a un descuido de recontaminar el brazo que más importa.

---

**Resumen de las tres cosas que cambiaría de tu diseño:**

1. El endpoint no es "rendimiento en B", es **diferencia de diferencias A↔B**, estratificada por un eje de **mecanicidad medido automáticamente y ciego al veredicto** — eso resuelve tu §5.2 sin filtrarle nada al autor.
2. El adversario congelado no basta: **hay que reportar también el actualizado**, porque la conclusión útil no es "el modelo generaliza" sino "el modelo vale lo que cuestan las reglas que le faltan".
3. Rompe la herencia de **un caso por operador**: sin varianza intra-tipo no puedes distinguir "el adversario se hunde" del ruido de composición del §2.4.

Lo que **no** cambiaría: el orden (adversario primero) y sacar los fallos reales del claim principal. Eso ya lo tienes bien.