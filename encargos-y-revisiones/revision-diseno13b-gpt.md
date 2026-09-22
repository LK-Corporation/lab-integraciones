<!-- modelo: or:openai/gpt-5.6-terra-pro · via: openrouter.ai · encargo: encargo_diseno13b.md · 168 s · 74459 tokens -->

## Error de razonamiento principal, antes de nada

La v2 aún confunde tres cosas distintas:

1. **Fallo emergente del sistema**: nadie escribió esa manifestación concreta.
2. **Distribución de descubrimiento diseñada**: alguien eligió perturbaciones, parámetros, presupuestos, relaciones metamórficas, timeouts, deduplicación y criterio de entrada.
3. **Fallo desconocido para el agente**: el agente no recibió información semánticamente equivalente durante su afinado.

La emergencia resuelve parcialmente (1). No demuestra (3), y deja (2) como una fuente fuerte de sesgo. Por tanto, hoy no pueden afirmar:

> “un fallo que nadie diseñó” = “un fallo que el modelo nunca vio ni fue preparado para reconocer”.

Sólo pueden afirmar, si el protocolo se cierra bien:

> “un fallo no preespecificado individualmente, descubierto bajo una distribución de perturbaciones preinscrita”.

Además, hay una contradicción temporal en §4.2:

> “la regla de adjudicación y el `ideal_b` de B se escriben y sellan antes de curar”.

La **regla de adjudicación** puede sellarse antes. El `ideal_b` específico de cada tipo o ejecución no puede existir antes de descubrir y curar B. Si se pretende lo contrario, o es sólo una plantilla de etiqueta —entonces no es `ideal_b`—, o se está declarando una imposibilidad.

La corrección mínima es separar:

- **rúbrica y esquema de salida**: sellados antes de ejecutar;
- **instanciación de `ideal_b` por caso**: creada tras congelar candidatos y por adjudicadores ciegos a todos los brazos;
- **puntuador**: probado y sellado antes, sin acceso a las decisiones de adjudicación ni capacidad de reinterpretar etiquetas.

---

# 1. F7: la capa de emergencia es un brazo adaptativo contaminado

## F7 · El generador de B, su selección y su medición son un brazo

La v2 retiró el oráculo como brazo explícito, pero dejó una cadena completa bajo control de quien conoce el objetivo, A, el afinado y previsiblemente los resultados históricos:

- escribe las relaciones metamórficas;
- define las cinco familias;
- fija sus parámetros, distribuciones, semillas, presupuestos y umbrales;
- ejecuta el piloto;
- decide si “cambiar la capa” tras ver el piloto;
- determina qué constituye un candidato, un tipo distinto, una repetición o un disputado;
- posee el puntuador;
- conoce que la ventaja histórica del prompt afinado se concentra en el fallo silencioso.

Eso convierte la distribución final de B en un **tratamiento experimental elegido por un experimentador no ciego al brazo modelo**. No hace falta que el curador vea el agente para que haya sesgo: basta con que quien diseña y ajusta la fábrica de candidatos sepa qué clase de casos sería favorable o desfavorable.

Es el análogo estructural de la rotura de v1:

> antes, el oráculo era un brazo;  
> ahora, la distribución de generación y selección de B puede ser un brazo.

## Por qué F1–F5 no lo detectan

- F1 mide si hay silenciosos, no si fueron seleccionados hacia una taxonomía favorable al prompt.
- F2 mide concentración por familia, no concentración por mecanismo semántico.
- F3 publica la vía de entrada, no la adaptatividad de su diseño.
- F4 excluye diez coincidencias exactas, no parentescos causales o semánticos con A.
- F5 ciega al curador, pero no ciega a quien define la máquina que le entrega los casos ni al propietario del puntuador.

## Medida barata antes de contratar

Crear y sellar un **manifiesto de generación y análisis** antes del piloto final:

1. Familias, parámetros, rangos, distribuciones y presupuesto de ejecuciones.
2. Semillas o mecanismo verificable de generación de semillas.
3. Timeouts, definición de caída, cuelgue, “nunca se escribió”, fuera de orden, duplicado y tipo distinto.
4. Algoritmo de deduplicación/canonización de tipos.
5. Política de repetición: cuántas reproducciones se intentan por candidato.
6. Relaciones metamórficas completas.
7. Rúbrica de adjudicación.
8. Versión y pruebas del puntuador.
9. Regla de parada y tratamiento del piloto.

Y, crucialmente:

- **el piloto no puede entrenar la distribución que se puntúa**;
- o bien se descarta entero del análisis final;
- o bien se parte antes en `pilot` y `confirmatorio`, con semillas disjuntas;
- cualquier modificación posterior a la capa abre una nueva fase de piloto y hace inválido el bloque anterior para inferencia confirmatoria.

La comprobación barata es una **re-ejecución independiente y ciega del manifiesto**, con hashes, por otra persona. No necesita curador ni contratar a nadie.

## Auditoría adicional necesaria: contaminación semántica con A

F4 excluye los diez fallos conocidos por identidad. Es insuficiente. El riesgo es que B produzca variantes de arquetipos ya presentes en A:

- mismo mecanismo causal, distinta condición de activación;
- misma invariante, distinto campo HL7;
- mismo patrón de discrepancia `AA`/recurso/no-recurso;
- mismo tipo de error de codificación, con otra representación;
- mismo fallo de estado o concurrencia, con otra carga.

Para evaluar esto de verdad necesito, bajo acceso controlado:

- catálogo A;
- prompt afinado completo;
- relaciones metamórficas;
- manifiesto de perturbación;
- rúbrica de adjudicación;
- código o especificación del puntuador.

**Finalidad:** hacer una auditoría de solapamiento semántico y causal, no una revisión de resultados. Debe producir una matriz sellada de “arquetipos presentes en A” frente a “mecanismos que puede producir B”. Si el auditor no puede hacer esa matriz, tampoco se puede defender “exposición cero”.

---

# 2. ¿Emergencia real o contrato con otro nombre?

## 2.1 Vía (b): las relaciones metamórficas son un oráculo contractual, no una vía neutra

La distinción con v1 es real pero limitada.

No son un catálogo explícito de fallos del tipo:

\[
\text{operador de mutación} \rightarrow \text{regla inversa}.
\]

Pero sí definen:

\[
(x, T(x)) \mapsto \text{predicado de discrepancia}.
\]

Eso es un **oráculo relacional**. Si entra en B porque viola una relación que usted escribió, B está condicionado por propiedades que usted decidió observar.

La diferencia frente a v1 es:

- en v1, el fallo era creado y etiquetado por el operador;
- aquí, el fallo es una discrepancia empírica del sistema frente a una relación declarada.

Eso sí permite descubrir comportamientos no enumerados previamente. Pero no justifica decir que la vía está libre de firma. Su firma es la clase de invariantes elegidas.

La afirmación de §4.1 debería cambiar de:

> “la firma que (b) imprime es la del contrato, y eso no favorece a ningún brazo”.

a:

> “la vía (b) selecciona discrepancias expresables por las relaciones contractuales selladas. Es una fuente sesgada hacia esa clase de fallos; la simetría con reglas depende de que ambos brazos dispongan de la misma observabilidad y de la misma capacidad operacional para evaluar relaciones.”

Esa última condición no está demostrada.

### El problema comparativo oculto

Una relación metamórfica puede requerir:

- dos ejecuciones correlacionadas;
- estado previo;
- concurrencia;
- comparación de recursos FHIR;
- logs;
- tiempos;
- reintentos;
- acceso a efectos externos.

Si el agente ve una traza enriquecida y el `v3 actualizado` se limita a una traza individual, no se está midiendo “modelo frente a regla estática”; se está dando al agente una observabilidad distinta.

La corrección mínima es fijar una **interfaz común de evidencia**:

| Elemento | Agente | v3 actualizado |
|---|---:|---:|
| mensaje de entrada | igual | igual |
| ACK/NAK | igual | igual |
| trazas de red | igual | igual |
| logs | igual | igual |
| estado FHIR | igual | igual |
| par metamórfico | igual | igual |
| historial de sesión | igual | igual |
| reloj / timeouts | igual | igual |

Si una regla no puede usar una señal que el agente sí usa, el resultado mide capacidad bajo herramientas asimétricas, no capacidad de detección.

## 2.2 Vía (a): “sin oráculo y sin sesgo” es falso

No hay ausencia de oráculo. Hay un oráculo de liveness/observabilidad:

- excepción;
- caída;
- conexión reseteada;
- timeout;
- recurso ausente;
- ACK ausente;
- orden inesperado.

Además, “un recurso nunca se escribe” ya presupone una expectativa sobre qué recurso debería existir y cuándo. Eso es contrato, aunque sea implícito.

El sesgo de (a) no es ausencia de sesgo: es sesgo hacia fallos con señal operacional fuerte y hacia condiciones observables con la instrumentación actual. Puede dejar fuera precisamente:

- corrupción silenciosa;
- transformación semánticamente errónea pero válida;
- recursos escritos con contenido incorrecto;
- estado incorrecto que finalmente converge;
- errores compensados;
- degradación de calidad sin caída.

La vía (a) es útil, pero debe etiquetarse como:

> “descubrimiento por anomalía operacional”, no “descubrimiento sin sesgo”.

## 2.3 Vía (c): una muestra humana al 1 % exige miles, no decenas

Hay dos preguntas distintas que ahora están mezcladas:

1. ¿Cuál es la tasa de ejecuciones con fallo silencioso?
2. ¿Qué proporción de **tipos distintos** de fallo silencioso deja fuera (a)+(b)?

Si la tasa base por ejecución es \(p=1\%\):

- Para tener un 95 % de probabilidad de ver al menos un caso:

\[
n \ge \frac{\log(0.05)}{\log(0.99)} \approx 299.
\]

- Para esperar unas 10 observaciones, hacen falta aproximadamente 1.000 ejecuciones.
- Para estimar una tasa del 1 % con semianchura aproximada de ±0,5 puntos porcentuales al 95 %:

\[
n \approx \frac{1.96^2 \cdot 0.01 \cdot 0.99}{0.005^2} \approx 1521.
\]

Y eso supone independencia, que probablemente no existe: ejecuciones de un mismo mecanismo causal estarán agrupadas. Para diversidad de **tipos**, 1.500 ejecuciones puede seguir produciendo sólo uno o dos mecanismos repetidos.

Por tanto, una muestra humana es informativa si se preinscribe como:

- muestra aleatoria sobre **todas las ejecuciones**, no sólo sobre candidatos;
- estratificada por familia de perturbación;
- con probabilidades de inclusión conocidas;
- con análisis ponderado;
- con un tamaño orientado a una precisión declarada, no al número que “parezca manejable”.

Si el presupuesto no soporta al menos ~1.500 adjudicaciones aleatorias para detectar/estimar una tasa del 1 %, no se puede presentar (c) como estimador serio de tasa base. Sólo como auditoría cualitativa de omisiones.

## 2.4 Cuarta vía: diferencial contra una implementación independiente

La cuarta vía útil es un **oráculo diferencial**, no derivado de una invariante escrita como relación metamórfica:

- ejecutar el mismo estímulo contra una implementación independiente;
- comparar contra un adaptador alternativo;
- comparar contra un intérprete HL7/FHIR de referencia;
- comparar contra una versión anterior o posterior con comportamiento documentado, si el desacuerdo se adjudica contra estándar.

No es libre de sesgo: selecciona discrepancias entre implementaciones. Pero tiene una firma distinta de:

- anomalía operacional de (a);
- invariante contractual de (b);
- inspección humana de (c).

Debe publicarse como vía separada, con su propia proporción y tasa de falsos positivos. No debe fundirse con (b).

---

# 3. El residuo: no es un endpoint verificable tal como está definido

Hay además una discrepancia interna: §6 declara como primario la detección del agente sobre todo B y coloca el residuo “al lado”; el encargo lo presenta como endpoint primario. Debe elegirse una sola jerarquía. No es un detalle editorial: cambia qué control de error y qué potencia se necesitan.

## 3.1 Qué impide declarar de más o de menos

Hoy, nada suficiente.

Un autor puede declarar “no cubrible” porque:

- no quiere invertir tiempo;
- interpreta “regla estática” de forma restrictiva;
- no dispone de la misma evidencia que el agente;
- teme producir una regla frágil;
- quiere preservar reputación;
- o, en sentido contrario, escribe una regla sobreadaptada tras ver las dos instancias de entrenamiento.

La declaración de incapacidad no es una variable observable. Es una mezcla de capacidad, presupuesto, lenguaje de reglas, herramientas, tiempo y conducta estratégica.

## 3.2 Cambio mínimo: el residuo debe ser un residuo bajo recursos fijados

No puede llamarse simplemente “lo que no cubre una regla estática”. Debe definirse como:

> tipos no cubiertos por un autor de reglas bajo lenguaje \(L\), interfaz de evidencia \(I\), presupuesto temporal \(T\), datos de exposición \(e\), y criterio de éxito \(C\), todos preinscritos.

Protocolo mínimo:

1. Definir formalmente el lenguaje de reglas permitido.
2. Igualar interfaz de evidencia con el agente.
3. Fijar presupuesto por tipo y total.
4. Obligar al autor a emitir para cada tipo una de tres salidas:
   - regla candidata;
   - abstención razonada con código de motivo;
   - “no reproducible”.
5. Ejecutar automáticamente la regla contra el holdout de instancias.
6. Medir cobertura, falsas alarmas y tiempo.
7. Publicar abstenciones y reglas fallidas por separado.

Aun así, no se mide una incapacidad metafísica de las reglas. Se mide:

> “residuo frente a este sistema de reglas, esta interfaz y este presupuesto”.

Eso es publicable y honesto.

## 3.3 Si el autor es un modelo

Empeora, no mejora:

- el modelo es otro brazo con distribución de entrenamiento desconocida;
- puede estar contaminado por documentación, ejemplos o A si A circuló;
- su estocasticidad exige semillas, versión y temperatura selladas;
- puede variar entre corridas;
- su “declaración de no poder” carece de interpretación psicológica y operativa estable.

Si se usa un modelo, debe ser tratado como comparador reproducible, no como árbitro de capacidad de reglas. Se fijan:

- versión;
- prompt;
- herramientas;
- temperatura;
- semillas;
- presupuesto de tokens, iteraciones y tiempo;
- política de reparación;
- interfaz de evidencia.

## 3.4 ¿Tiene trampa propia?

Sí: el residuo es susceptible a una **trampa de abstención**.

En Fase 12 el total ocultaba que el banco estaba construido para una clase de reglas. Aquí el residuo puede ocultar que la definición de “regla estática” está construida para no representar memoria, concurrencia, relaciones entre ejecuciones o efectos externos.

Un residuo grande puede significar cualquiera de estas cosas:

1. hay fallos que requieren razonamiento/modelado no capturado por reglas;
2. el lenguaje de reglas es demasiado pobre;
3. el comparador no recibe la misma evidencia;
4. el presupuesto de actualización es demasiado pequeño;
5. el tipo no es reproducible;
6. la taxonomía de “tipo” junta mecanismos distintos;
7. la regla sí existe, pero no fue encontrada.

No debe venderse como “residuo de las reglas” sin ese condicionamiento.

## 3.5 Si el residuo es vacío

Hay tres casos:

| Situación | Interpretación |
|---|---|
| B está vacío | La capa no produjo fallos adjudicables. No contesta la pregunta sobre el agente. Resultado negativo sobre el proceso de generación. |
| B existe, pero todo B es cubrible bajo el protocolo | Resultado publicable: en esta distribución y bajo estos recursos no se observó residuo frente a reglas. No demuestra que no exista en el dominio. |
| B existe, pero el autor cubre todo sólo sobre exposición y falla en holdout | No hay residuo vacío; hay sobreajuste del autor. |

---

# 4. Prompt afinado: no hay simetría demostrada

Dar el contrato al autor de reglas no equivale automáticamente a dar al autor de reglas lo que el prompt afinado contiene.

Los 17.136 caracteres pueden codificar, además del contrato:

- taxonomías de error aprendidas de A;
- prioridades de inspección;
- heurísticas de causalidad;
- ejemplos implícitos;
- criterios de relevancia;
- umbrales de sospecha;
- formato de salida alineado con el puntuador;
- conocimiento sobre qué señales ignorar;
- lenguaje que activa conocimiento latente del modelo sobre HL7/FHIR;
- sesgos sobre la distribución del laboratorio.

El resultado del paso 29 es precisamente una señal de que existe información o política no trivial: la mejora se concentra en una clase concreta, el fallo silencioso. No prueba que sea contaminación, pero hace imposible asumir que es “sólo contrato”.

El prompt genérico no es un control suficiente: cambia simultáneamente longitud, instrucciones, descomposición, foco, formato, prioridades y probablemente conocimiento operacional activado.

## Cambio mínimo

Hacer una auditoría de partición de información del prompt:

1. **Contrato explícito:** cada afirmación del prompt debe apuntar a cláusula de contrato o estándar.
2. **Procedimiento neutral:** instrucciones de formato y ejecución que no contienen conocimiento de A.
3. **Contenido derivado de A o del laboratorio:** ejemplos, heurísticas, clases de error, prioridades y reglas de decisión.

Después ejecutar, como mínimo, tres brazos de prompt:

- genérico;
- contrato reconstruido independientemente desde contrato/estándar;
- afinado completo congelado.

Y publicar la diferencia:

\[
\text{afinando completo} - \text{prompt de contrato reconstruido}.
\]

Si esa diferencia persiste en B, no puede atribuirse sin más al contrato.

La simetría real exige además entregar al autor de reglas:

- el mismo contrato;
- la misma interfaz de evidencia;
- las mismas relaciones observables;
- el mismo acceso a estado, pares metamórficos y secuencias;
- una especificación explícita de aquello que el prompt usa como procedimiento.

No hace falta dar al autor “un prompt”; hace falta darle la **información operacional equivalente**.

---

# 5. Tamaño y preinscripción con B emergente

“N y k salen de lo que produzca la capa” es compatible con preinscripción sólo si se fijan previamente:

1. presupuesto total de ejecuciones \(E\);
2. configuración, semillas y distribuciones del generador;
3. regla de parada;
4. definición canónica de tipo;
5. política de reproducción;
6. umbral mínimo de tipos;
7. regla para declarar análisis descriptivo;
8. análisis estadístico válido para el N resultante.

Ahora falta al menos el punto 4: si la definición de “tipo genuinamente distinto” se ajusta tras ver B, N es manipulable.

## Regla concreta

Preinscribir:

- un presupuesto fijo \(E\) de ejecuciones confirmatorias;
- una partición `pilot` / `confirmatorio` por semillas disjuntas;
- una taxonomía de tipo basada en una firma canónica sellada, por ejemplo:
  - cláusula incumplida;
  - familia de perturbación;
  - mecanismo causal reproducible;
  - firma de salida/estado;
- \(r\) reintentos de reproducción por candidato, por ejemplo \(r=5\);
- \(k_{\min}=3\) o \(5\) instancias reproducidas para entrar en análisis por tipo;
- tipos con \(k<k_{\min}\): sólo descriptivos;
- \(N_{\min}\) derivado de precisión, no de conveniencia.

Para una proporción de detección por tipo cerca de 25 %, una semianchura aproximada de ±10 puntos porcentuales requiere del orden de:

\[
N \approx \frac{1.96^2 \cdot 0.25 \cdot 0.75}{0.10^2} \approx 72
\]

tipos aproximadamente independientes. Si el diseño acepta una precisión peor, puede bajar; si espera dependencia fuerte entre tipos, necesita más o debe abandonar intervalos binomiales simples y usar bootstrap por familia/mecanismo.

No recomiendo fijar “N = 30” por herencia. Recomiendo fijar una **precisión mínima aceptable** y deducir \(N_{\min}\) de ella. Si la capa no llega, el análisis queda descriptivo tal como ya prevé §8.

---

# 6. Lo barato que falta, sobra y debe adelantarse

## Falta

### A. Auditoría de interfaz común de evidencia

Debe verificarse antes de generar B que el agente, v3 congelado y v3 actualizado reciben exactamente la misma evidencia operacional, salvo que la diferencia sea el objeto explícito de estudio.

Sin esto, el residuo puede ser simplemente una diferencia de instrumentos.

### B. Auditoría del puntuador

“El puntuador sigue siendo mío” es una alarma metodológica, no una acusación de mala fe.

Antes de contratar:

- conjunto de pruebas adversariales nuevo;
- casos frontera;
- casos con salidas semánticamente equivalentes;
- errores de formato;
- resultados ambiguos;
- doble implementación o revisión independiente de la lógica de puntuación;
- puntuación ciega a brazo y orden aleatorizado de resultados.

La propiedad que interesa comprobar es:

\[
\text{score}(y, ideal_b)
\]

invariante ante brazo, orden, formato irrelevante y conocimiento del origen.

### C. Definición de negativos

“Limpios de B” no está suficientemente definido. Si B contiene fallos curados, no puede a la vez contener controles limpios sin una partición explícita.

Hace falta un conjunto de negativos generado bajo las mismas familias y condiciones operacionales:

- entradas válidas;
- perturbaciones semánticamente equivalentes;
- recuperaciones esperadas;
- rechazos correctos;
- errores de transporte correctamente manejados.

De otro modo, el veto de falsas alarmas se estima sobre una población distinta y puede ser irrelevante.

### D. Auditoría de contaminación semántica A–prompt–B

Es la medida necesaria para sostener “exposición cero”, descrita en F7.

## Sobra o debe degradarse

### “Si una familia aporta más del 60 %, se declara y se reporta”

Reportarlo no arregla nada. El 60 % es un umbral narrativo, no una garantía metodológica. Si la familia dominante coincide con la clase donde el prompt afinado ganó en el paso 29, el primario queda comprometido aunque se declare.

Debe convertirse en regla de interpretación:

- estimar y reportar por familia;
- no usar macro global como afirmación de generalidad si una sola familia domina;
- exigir al menos \(m\) familias con un mínimo de tipos para un resultado transversal;
- o declarar que el alcance es sólo la familia dominante.

## El paso con mayor probabilidad de matar la fase

**Primero: auditoría de contaminación y simetría de información.**

No el piloto de 200 ejecuciones.

La razón: si el prompt contiene conocimiento semántico de A/laboratorio que reaparece en B, o si la distribución de perturbación fue afinada indirectamente hacia esos arquetipos, entonces una tasa alta del agente no responde a H4 aunque B produzca muchos silenciosos y muchos tipos.

Orden mínimo revisado:

```text
0. auditoría independiente A ↔ prompt ↔ relaciones ↔ generador ↔ puntuador
1. definir interfaz común de evidencia y lenguaje/presupuesto de reglas
2. sellar manifiesto de generación, deduplicación, reproducción y análisis
3. validar puntuador y construir negativos
4. relaciones metamórficas selladas
5. piloto separado por semillas; nunca reutilizable como confirmatorio
6. decidir viabilidad de la capa
7. curación ciega y análisis confirmatorio
```

---

# Dictamen

La v2 mejora sustancialmente v1: un B emergente sí puede descubrir discrepancias no preespecificadas individualmente y evita la inversión trivial de un operador de mutación.

Pero todavía no está lista para montar la capa porque conserva cuatro amenazas no cerradas:

1. **F7:** la máquina que produce, selecciona y mide B es un brazo adaptativo potencialmente contaminado.
2. **La vía (b) sigue siendo un oráculo contractual**, no una fuente neutra; su comparabilidad exige interfaz de evidencia igualada.
3. **El residuo declarado no es una variable verificable** sin fijar lenguaje, herramientas, presupuesto y prueba holdout.
4. **El prompt afinado no es simétrico por mera afirmación**; debe auditarse qué información distinta de contrato transporta.

El cambio mínimo no es volver a B declarado. Es sellar y separar:

- generación;
- selección;
- adjudicación;
- puntuación;
- comparación;
- y auditoría de contaminación.

Sin esa separación, B puede emerger del sistema, pero la conclusión seguirá emergiendo del diseño.