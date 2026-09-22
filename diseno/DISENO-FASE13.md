# Fase 13 — Diseño, v1 (22-sep-2026)

**Estado: BORRADOR. Nada se construye hasta firmar 🧑 y hasta que pasen las tres medidas de la
§7, que se hacen la primera semana y sin agente.**

Lo escribe quien hizo la Fase 12, con las cinco revisiones externas del diseño delante. Cada
decisión lleva de dónde sale: 📏 de una medida, 🔍 de una revisión, 🧑 abierto.

---

## 1. Por qué hay una Fase 13

La Fase 12 concluyó con las cinco hipótesis preinscritas cumplidas y este resultado, que va en dos
frases que no se separan:

**El agente funciona** —10 de 18 operadores de fallo silencioso, cero falsas alarmas en 22
limpios, sobre un conjunto reservado— **y aun así no hace falta**: un script de expresiones
regulares lo bate **+0,873 contra +0,629** y no le queda ni una detección propia.

📏 **Y la causa no es el modelo, es el banco.** El corpus se construye con **operadores de mutación
declarativos**: por construcción cada uno deja una firma mecánica. Un detector escrito contra esas
firmas llega al **100 % de lo observable** (16 de 18 tipos a 8 de 8).

Dicho con precisión: **el script no ganó porque sus reglas sean mejores. Ganó porque el conjunto de
operadores está cerrado y el autor lo conoce entero.**

---

## 2. La pregunta, corregida por el panel

Mi propuesta era «¿generaliza el modelo a tipos de fallo para los que nadie ha escrito una regla?».

🔍 **Y una revisión la tumbó:** *«estás confundiendo coste de mantenimiento con capacidad de
detección. Si el modelo bate a un adversario congelado, solo has demostrado que las reglas hay que
actualizarlas. Actualizo el script y vuelve a ganar: tu LLM es un motor de expresiones regulares
lento, caro y probabilístico.»*

Tiene razón, y son **dos preguntas distintas que hay que medir por separado**:

| | pregunta | cómo se mide |
|---|---|---|
| **Q1 · operativa** | ¿cuesta menos mantener el modelo que las reglas? | modelo frente a adversario **congelado** |
| **Q2 · de capacidad** | ¿detecta el modelo cosas para las que no se puede escribir una regla estática? | modelo frente a adversario **actualizado contra B** |

**Q2 es la que tiene valor científico. Q1 es real y operativa, y no se puede vender como Q2.**

🔍 Y una reformulación mejor que las dos, porque convierte un sí/no frágil en una curva: **medir la
pendiente de degradación por distancia al catálogo.** Una curva es mucho más difícil de falsear por
accidente de construcción que un umbral.

---

## 3. El eje que lo hace posible: el oráculo de mecanicidad

Mi problema era: **el autor ciego puede escribir tipos igual de mecánicos, y pedirle que no lo sean
le filtra la respuesta.**

🔍 **La solución es no pedírselo: se mide sola, y después.**

Un **inductor de reglas ciego**: dado el par (entrada limpia, entrada mutada) de cada tipo, intenta
inducir un discriminador por **diff sintáctico**, sin ver el catálogo, ni el agente, ni el
adversario, ni la clave. Eso da un eje objetivo de **mecanicidad** que no depende de nada mío.

- El autor ciego **no recibe ninguna instrucción** sobre mecanicidad.
- B se clasifica **post hoc** en cuartiles de mecanicidad con el inductor.
- **La pregunta se contesta dentro de cada cuartil.**

📏 Y hay un dato de la Fase 12 que dice que este eje va a ser nítido: el adversario tiene
**varianza intra-tipo 0,0000** — los 18 tipos a 0 o a 1 exactos. Para una regla, cubrir un tipo es
**una propiedad binaria del tipo**, no una tasa. El agente, en cambio, tiene varianza intra-tipo
0,057 y seis tipos parciales.

---

## 4. El diseño

**Conjunto A** — los 63 operadores actuales. Adversario y agente se desarrollan contra él. Ya
existe.

**Conjunto B, ciego** — N tipos **nuevos**, encargados a un autor que ve el circuito y el contrato
de la transformación pero **no** ve el adversario, ni el catálogo de A, ni el agente. Entrega, por
tipo: entrada de catálogo y función de mutación.

**Cuatro brazos sobre B:**

| brazo | qué es |
|---|---|
| **modelo** | el agente de la Fase 12, con la variante congelada (`89ae1c8d`) |
| **regla congelada** | `triador_regex_v3.py`, tal cual, sin tocar |
| **regla actualizada** | el mismo, con reglas nuevas escritas **viendo B** por alguien que no ve el agente |
| **inductor** | el oráculo de mecanicidad, que además es el suelo automático |

---

## 5. Cómo fracasaría esta fase, y qué lo destapa antes 🔍

La Fase 12 tenía un defecto fatal invisible hasta el último día. Estos son los de ésta, con su
medida barata, **y las tres primeras corren sin agente y sin adversario**.

### 5.1 Todo B resulta igual de mecánico

Entonces el adversario vuelve a ganar y no se aprende nada.
**Lo destapa:** el inductor (§3). Si todo B cae en el cuartil mecánico, **se sabe la primera
semana**. Coste: un script de diffs.

### 5.2 El autor ciego reinventa los operadores de A — **el peor, y no lo había visto**

🔍 *«El contrato induce el catálogo: hay un número finito de cosas que pueden ir mal en un
ADT^A01→Patient, y 63 operadores ya cubren buena parte. Un autor competente reinventará operadores
de A sin verlos.»* Entonces B **es A con otros nombres**, el adversario congelado gana por
coincidencia de firmas, y se concluiría «las reglas generalizan» cuando lo cierto es **«B está
contenido en A»**.

**Lo destapa:** solapamiento de firmas A↔B con el mismo inductor aplicado a A. Para cada tipo de B,
¿qué fracción de sus casos los detecta una regla inducida **de A**? Si es alta, se le piden más
tipos al autor **sin decirle por qué** — solo «necesitamos N más».

### 5.3 El estrato de fallos reales contamina el endpoint

🔍 No es una contaminación menor: el adversario pudo afinarse, consciente o no, contra fallos que
el mismo autor conocía. **Va completamente aparte** (§8), nunca en el primario.

### 5.4 El adversario tiene cobertura desigual sobre B por azar

Con N pequeño, su resultado en B es **ruido de composición**: pilla unos tipos al 100 % y otros a
cero.
**Lo destapa:** correr solo el adversario congelado sobre B y mirar la **distribución tipo a tipo,
nunca la media**. Si es bimodal, N es insuficiente y se sabe gratis.

### 5.5 🧑 **El que yo no sé ver.** La Fase 12 enseñó que existe. Este diseño se pasa por el panel
otra vez **antes** de encargar B.

---

## 6. El endpoint, con la trampa de la agregación prohibida por escrito

📏 En la Fase 12 el total escondió el hallazgo: un brazo ganaba en limpios justo lo que perdía en
silenciosos y la resta salía casi cero.

**Primario — diferencia de diferencias**, en puntos del puntuador firmado, con la macro **por tipo**
como unidad:

```
DiD = [ S_modelo(B) − S_regla(B) ] − [ S_modelo(A) − S_regla(A) ]
```

Positivo = el modelo **degrada menos que las reglas** al salir del catálogo. Se calcula **dos
veces**: contra la regla congelada (Q1) y contra la actualizada (Q2).

**Desglose obligatorio, publicado AL LADO del endpoint y no debajo:**

1. **Silenciosos y limpios, nunca agregados.** La falsa alarma va como **secundario con veto**: un
   brazo con más falsas alarmas no puede «ganar» por detección aunque el DiD lo diga.
2. **DiD por cuartil de mecanicidad.** Aquí vive la respuesta de verdad.
3. **Distribución tipo a tipo del adversario en B**, cruda.
4. **Los dos adversarios lado a lado**, congelado y actualizado.
5. **Detecciones propias del modelo**: tipos donde el modelo detecta y **ningún** brazo de reglas
   —ni congelado ni actualizado— lo hace. 📏 En la Fase 12 fue **1 de 55, y ni siquiera era una
   detección**. Es el número más honesto que hay y va en portada.

🔍 **Regla anti-Fase-12, escrita aquí:** ningún número agregado sobre limpios + silenciosos aparece
en el resumen. La resta que salió «casi cero» queda **prohibida como endpoint**.

---

## 7. Tamaño, con la varianza medida y no supuesta

📏 Sacada de la Fase 12, 18 tipos con 8 casos cada uno:

| | tasa por tipo | desv. entre tipos | **varianza intra-tipo** |
|---|---|---|---|
| agente | 0,597 | 0,428 | **0,057** (6 tipos parciales) |
| regla | 0,889 | 0,314 | **0,0000** (los 18 a 0 o a 1) |

**Consecuencia para el dimensionado: toda la potencia viene de N, no de k.** Para una regla,
cubrir un tipo es binario; para el agente hay algo de varianza interna, pero la dispersión **entre**
tipos (0,43) la domina con mucho.

🧑 **Propuesta: N = 30 tipos, k = 5 casos por tipo** = 150 casos, más limpios en proporción.

- N = 30 deja **7-8 tipos por cuartil** de mecanicidad, que es el análisis que importa y parte N en
  cuatro. Con N = 20 quedarían 5 por cuartil, al límite de lo interpretable.
- k = 5 basta para estimar la varianza intra-tipo del agente y destapar §5.4; k = 8 no compra
  potencia para la regla, que no la tiene.
- Análisis: **modelo mixto** con efecto aleatorio por tipo y efecto fijo brazo×estrato.

🔍 **Y si el autor ciego no puede producir 30 tipos genuinamente distintos, eso es en sí un
resultado**: el dominio no admite más, la generalización tiene techo bajo, y hay que decirlo con
esas palabras en vez de rebajar N en silencio.

---

## 8. El estrato de fallos reales, aparte del todo

Los defectos que la bitácora apuntó **al construir el laboratorio**: un acuse `CE` no conforme al
modo declarado, entrada sin desescapar, una credencial inexistente devolviendo 404 en vez de 401,
el servicio bloqueándose con `PoolSize=1`. No tienen firma diseñada porque **nadie los diseñó**.

**Son ocho o diez y el autor del laboratorio los conoce.** Por eso:

- **fuera del endpoint primario**, sin excepción;
- se reportan como **estrato descriptivo**, con la contaminación escrita al lado;
- valen para una frase honesta —«así se comportan los dos brazos ante fallos que nadie diseñó»— y
  para nada más.

---

## 9. El orden, que es la lección de la Fase 12

```
  1. el adversario fuerte          ya existe: triador_regex_v3.py
  2. el inductor de mecanicidad    semana 1, sin agente
  3. el solapamiento A-B           semana 1, sin agente
  4. la distribucion del adversario sobre B, tipo a tipo
  -------------------------------- cualquiera de las tres puede decir
                                    «este banco tampoco sirve»
  5. encargar B a ciegas
  6. congelar, preinscribir, sellar
  7. UNA pasada
```

**Nunca más un mes de trabajo antes de saber si el banco puede contestar la pregunta.**

---

## 10. Lo que se hereda

El circuito congelado con su huella, el arnés (`Datos`, `HerrA/B/C`), las tres clases del agente,
el generador, el puntuador con sus 16 autopruebas, la maquinaria de sellado y `comparar.py`, la
matriz de observabilidad, el banco de adversarios y los tres triadores. **Un mes de trabajo que no
se repite.**

---

## 11. Abierto 🧑

1. **N = 30 y k = 5**, o los números que se decidan.
2. **A quién se le encarga B**, y con qué contexto exacto —el circuito y el contrato, nada más—.
3. **Quién escribe la regla actualizada** contra B. No puede ser quien vea el agente.
4. Si **Q1 y Q2 se preinscriben las dos** o solo Q2.
5. Pasar este diseño por el panel **antes** de encargar B (§5.5).
