<!-- modelo: or:openai/gpt-5.6-terra-pro · via: openrouter.ai · encargo: encargo_diseno13.md · 162 s · 59172 tokens -->

# Veredicto: no encarguéis B todavía

El diseño ha mejorado mucho respecto a Fase 12, pero conserva un defecto estructural: **no tiene una verdad de referencia independiente**.

Y tiene además una contradicción operativa: §9 pretende medir inductor, solapamiento A↔B y distribución del adversario sobre B **antes de encargar B**. Eso es imposible. Podéis construir y validar las herramientas en semana 1; el diagnóstico sobre B sólo existe después de recibir B.

---

## 1. El modo de fallo faltante: sesgo de medición común

### Nombre

**Oráculo de evaluación endógeno o sesgo de medición común.**

El mismo equipo/persona controla:

- el contrato que delimita qué cuenta como transformación válida;
- el circuito;
- el puntuador;
- el inductor de mecanicidad;
- la selección o aceptación de B;
- y probablemente la representación que entregará B al autor de reglas.

Entonces el experimento no mide necesariamente:

> «qué brazo detecta fallos reales de la interfaz».

Puede medir:

> «qué brazo produce salidas que el puntuador propio reconoce como evidencia de fallo, sobre mutaciones que el propio laboratorio considera fallos».

Eso es particularmente peligroso porque los cuatro brazos no producen la misma clase de evidencia:

- una regla puede devolver una condición booleana;
- el agente puede emitir diagnóstico textual, causalidad o clase de fallo;
- el inductor opera sobre pares limpio/mutado y diffs, con información que un detector en producción puede no tener;
- el puntuador puede premiar implícitamente una ontología de fallos alineada con el agente o con el contrato.

Si el puntuador tiene puntos ciegos, B puede contener fallos verdaderos que todos puntúan como “no detectados”. Si sus criterios semánticos coinciden con el lenguaje del agente, puede fabricar ventaja del agente. Si están alineados con firmas estructurales, puede fabricar ventaja de reglas.

La Fase 12 ya demostró que una propiedad del banco puede dominar completamente el resultado. Aquí esa propiedad puede estar en la **medición**, no en las mutaciones.

### Medida barata de primera semana

Antes de B, haced una **auditoría ciega de validez del puntuador**:

1. Construid 30–50 casos de calibración, no procedentes de A ni de B:
   - fallos indiscutibles;
   - limpios indiscutibles;
   - casos límite;
   - pares semánticamente equivalentes con sintaxis distinta;
   - pares sintácticamente muy parecidos con semántica distinta.
2. Que un adjudicador independiente, o dos con resolución de desacuerdos, etiquete:
   - si hay fallo;
   - qué contrato viola;
   - qué evidencia mínima debería bastar para acreditarlo.
3. Entregad al puntuador salidas anonimizadas y canonizadas:
   - sin identidad de brazo;
   - sin formato que revele si viene de LLM, regex o inductor.
4. Medid:
   - acuerdo puntuador–adjudicación;
   - acuerdo por estrato;
   - sensibilidad a paráfrasis de la explicación;
   - invariancia ante renombrados y cambios superficiales;
   - falsos negativos del propio puntuador.

**Criterio de parada:** si el puntuador no reproduce de forma alta y equilibrada la adjudicación independiente, no hay endpoint defendible. Hay que reparar o reemplazar el puntuador antes de construir B.

Esto no exige agente ni B. Es exactamente el tipo de prueba barata que habría evitado una conclusión ficticia.

---

# 2. Correcciones aparentemente incorporadas, pero todavía incompletas

## 2.1 Q1 frente a Q2: están separadas nominalmente, no experimentalmente

La distinción conceptual es correcta:

- Q1: congelado frente a agente;
- Q2: regla actualizada frente a agente.

Pero Q1 no está bien formulada como pregunta operativa.

Comparar un modelo congelado con una regla congelada **no mide coste de mantenimiento**. Mide degradación de cobertura de dos artefactos congelados. Para medir coste operativo necesitaríais, como mínimo:

- tiempo de actualización;
- número de iteraciones;
- perfil de quien mantiene;
- acceso permitido a B;
- coste de revisión;
- tasa de regresiones en A;
- coste de inferencia y latencia;
- coste de falsas alarmas;
- mantenimiento periódico, no una única actualización.

Tal como está, Q1 sólo puede llamarse:

> **Q1 revisada: robustez fuera del catálogo de artefactos congelados.**

No:

> «¿cuesta menos mantener el modelo?»

Además, Q1 contamina la lectura de Q2 si ambos resultados se presentan bajo la misma narrativa de “generalización”. Una victoria del modelo contra la regla congelada es casi esperable si B se selecciona por distancia respecto de A. No es evidencia de que el modelo detecte cosas no codificables.

### Recomendación

- Preinscribid Q2 como primaria.
- Reportad Q1 como descriptiva o como estudio de degradación.
- Si queréis responder Q1 operativa, diseñad otro experimento con presupuesto, tiempo y acceso idénticos para modelo y reglas.

---

## 2.2 El inductor no es todavía un oráculo de mecanicidad

El diseño reconoce la ambigüedad correcta:

> “No encuentro regla” puede significar “no es mecánico” o “mi inductor es débil”.

Eso invalida llamar al inductor “oráculo”. Es un **instrumento de medición con sensibilidad y especificidad desconocidas**.

Hay cuatro problemas adicionales.

### A. “Mecanicidad” no es una propiedad absoluta

Sólo existe respecto de:

- un lenguaje de reglas;
- una biblioteca de predicados;
- acceso a datos;
- presupuesto de complejidad;
- tiempo de desarrollo;
- capacidad del autor.

Una regla estática arbitraria puede incorporar un parser completo, un simulador del circuito, tablas, árboles de decisión o incluso modelos aprendidos. Sin delimitar el lenguaje, la afirmación “no se puede escribir una regla estática” no es falsable.

Hay que sustituir la pregunta metafísica por una operacional:

> “¿Puede inducirse o escribirse una regla en la DSL R, con acceso X, presupuesto Y y tiempo T, que alcance rendimiento Z en datos no vistos?”

### B. El inductor tiene información privilegiada

Recibe pares `(limpio, mutado)` y opera sobre su diff. Un detector desplegado puede no tener esa contrafactual limpia equivalente.

Si la regla actualizada no recibe exactamente esa misma información, el inductor no mide la dificultad del problema de detección; mide la facilidad de reconstruir la mutación una vez conocida la pareja.

### C. El inductor puede sobreajustar los cinco casos

Si induce y evalúa sobre los mismos cinco pares, “encuentra una regla” no demuestra generalización. Sólo demuestra que halló una descripción compatible con cinco ejemplos.

Debe inducir sobre una parte y evaluarse sobre instancias protegidas del mismo tipo.

### D. Los cuartiles internos son lógicamente inútiles para §5.1

Si los cuartiles se construyen **dentro de B**, siempre habrá aproximadamente 7–8 tipos por cuartil, aunque todos sean altamente mecánicos en términos absolutos.

Por tanto esta frase es falsa bajo la definición actual:

> “Si todo B cae en el cuartil mecánico, se sabe la primera semana.”

No puede caer “todo B” en un cuartil construido con B.

### Requisito mínimo para usarlo

1. Definir una DSL de reglas y presupuesto de búsqueda.
2. Crear un banco de calibración independiente para el inductor:
   - tipos con reglas conocidas y verificables;
   - tipos diseñados para requerir semántica no local, estado o ejecución;
   - tipos que el inductor debería declarar “abstención”.
3. Medir su sensibilidad, especificidad y tasa de abstención.
4. Fijar umbrales absolutos antes de ver B, no cuartiles internos.
5. Inducir sobre casos de desarrollo y evaluar sobre casos sellados.
6. Reportar “mecanicidad según el inductor R”, nunca “mecanicidad objetiva”.

Si no se hace esto, el eje central de Fase 13 no es interpretable.

---

## 2.3 El solapamiento A↔B: el problema no es sólo que el autor lo deduzca

Pedir repetidamente “más tipos” al autor sin explicar el motivo es practicable una vez. No es practicable como protocolo reiterado:

- el autor inferirá que sus entregas iniciales han sido rechazadas;
- cambiará su estrategia;
- intentará producir rareza o novedad;
- B dejará de ser una muestra de lo que ese autor habría generado bajo el contrato.

Pero el problema principal es más grave: **filtrar B según distancia a A construye la hipótesis dentro del banco**.

Si se acepta B sólo cuando el inductor dice que está lejos de A, entonces se ha seleccionado explícitamente un conjunto donde se espera que la regla congelada falle. Una victoria del modelo frente a regla congelada dejará de ser descubrimiento y será, parcialmente, consecuencia del criterio de inclusión.

### Diseño mejor

- Encargad un lote sobredimensionado, por ejemplo 45–60 tipos, en una sola entrega.
- Un tercero independiente aplica criterios de aceptación preinscritos.
- No devolváis feedback al autor.
- Conservad y reportad todos los tipos:
  - aceptados;
  - rechazados;
  - motivos de rechazo;
  - distribución de solapamiento.
- Si descartáis tipos, el endpoint debe declarar claramente que vale para la población condicionada:
  > “tipos nuevos con solapamiento bajo según el inductor R”.

La solución más limpia es separar conjuntos:

- **B-screening:** sirve para medir solapamiento y calibrar el instrumento;
- **C-evaluación:** se genera independientemente después de congelar criterios, y es el único conjunto usado en el endpoint.

---

# 3. El endpoint tiene trampas propias

## 3.1 La DiD no identifica la afirmación que queréis hacer

La DiD:

\[
[S_{modelo}(B)-S_{regla}(B)]-[S_{modelo}(A)-S_{regla}(A)]
\]

mide degradación diferencial entre A y B. No demuestra:

- que B contenga fallos no detectables por reglas;
- que las reglas sean intrínsecamente incapaces;
- que el modelo generalice semánticamente;
- que la diferencia sea causada por “salir del catálogo”.

A y B no son poblaciones intercambiables. A fue desarrollado, conocido y posiblemente usado durante construcción de los artefactos. B será generado, filtrado y estratificado por instrumentos ligados al estudio. No existe el supuesto análogo a “tendencias paralelas” que permitiría una interpretación causal fuerte de una diferencia de diferencias.

La interpretación defendible es más modesta:

> “Bajo esta distribución concreta de tipos y este protocolo de actualización, el rendimiento relativo cambia de A a B en X.”

Eso sigue siendo útil. No es una prueba de capacidad fundamental.

---

## 3.2 La regla actualizada no tiene protocolo de actualización

Ahora mismo “regla actualizada viendo B” es demasiado ambiguo. Puede significar desde añadir tres regex hasta construir un analizador semántico o memorizar identificadores de B.

Sin un protocolo, Q2 comparará:

- un agente congelado desde Fase 12;
- contra un humano que puede inspeccionar B, su función de mutación y posiblemente todos sus casos.

Eso no es necesariamente injusto —puede ser precisamente la pregunta operativa—, pero debe definirse.

Preinscribid:

| Dimensión | Debe fijarse |
|---|---|
| Información disponible | contrato, código, pares limpio/mutado, función de mutación, labels, trazas |
| Tiempo | horas efectivas y calendario |
| Personal | número, perfil y experiencia |
| Lenguaje permitido | regex, AST, DSL, código general, librerías |
| Presupuesto de complejidad | líneas, reglas, dependencias o revisión |
| Acceso a A | sí/no, y si puede probar regresiones |
| Acceso a evaluación | prohibido |
| Evidencia de desarrollo | commits y bitácora sellada |

Sin esto, “las reglas actualizadas no pudieron” sólo significa “este autor, bajo condiciones no especificadas, no lo hizo”.

---

## 3.3 Falta una partición de desarrollo y evaluación para B

Si el autor de la regla actualizada ve los cinco casos por tipo, y luego se evalúa sobre esos mismos cinco casos, hay fuga de evaluación.

Para cada tipo de B necesitáis al menos:

- `B_dev`: ejemplos y/o descripción expuestos al autor de reglas;
- `B_test`: realizaciones nuevas, selladas, generadas tras congelar la regla.

El autor puede conocer el **tipo** si esa es la pregunta, pero no las realizaciones de prueba, identificadores, combinaciones ni semillas de evaluación.

Lo mismo aplica al inductor: debe inducir en desarrollo y medirse en test.

---

## 3.4 Los cinco desgloses son necesarios, pero no suficientes

Añadiría como obligatorios:

6. **Intervalos de incertidumbre por brazo y cuartil**, preferiblemente bootstrap jerárquico por tipo/familia, no sólo p-valores de un modelo mixto.

7. **Resultados por familia causal de tipos**, no sólo por tipo. Treinta tipos pueden ser seis ideas repetidas con cinco variantes cada una.

8. **Todos los tipos excluidos y todas las decisiones de exclusión**, especialmente por solapamiento o mecanicidad.

9. **Matriz de confusión del puntuador frente a adjudicación independiente.**

10. **Regresiones en A tras actualizar reglas.** Si la regla actualizada mejora B pero degrada A o dispara falsas alarmas, eso es parte central del coste de mantenimiento.

11. **Disponibilidad de información por brazo.** Si el inductor ve pares y el agente sólo ve una entrada, no pueden interpretarse en el mismo eje de capacidad.

---

# 4. Tamaño: N=30, k=5 no está justificado para el análisis propuesto

## 4.1 La varianza de Fase 12 no basta para dimensionar Fase 13

Tenéis estimaciones observadas en 18 tipos de un banco que ahora declarais estructuralmente defectuoso. No son una base suficiente para dimensionar un banco deliberadamente distinto.

Faltan los parámetros críticos:

- tamaño mínimo de efecto relevante para Q2;
- correlación pareada modelo–regla dentro de tipo;
- correlación entre tipos de una misma familia;
- dispersión de la regla **actualizada**, que no es la de la congelada;
- distribución de mecanicidad en B;
- proporción de B que sobrevivirá al filtro de solapamiento;
- tasa de falsos positivos;
- correlación entre los cinco casos del mismo tipo.

La varianza intra-tipo cero de la regla de Fase 12 no implica que:

- toda regla futura sea binaria por tipo;
- cinco casos basten para la regla actualizada;
- la incertidumbre de cobertura futura sea cero.

Sólo dice que esa regla, en ese banco y con ocho casos, dio 0 u 1 por tipo.

---

## 4.2 Siete u ocho tipos por cuartil no sostienen un análisis confirmatorio

Con 7–8 tipos por cuartil:

- una observación extrema cambia fuertemente la media;
- un modelo mixto con interacción `brazo × estrato` será inestable;
- los cuartiles dependen de cortes arbitrarios;
- no hay potencia creíble para detectar heterogeneidad;
- no hay base para una curva de degradación.

Eso puede ser exploratorio. No puede ser el análisis que “importa”.

Si el análisis por mecanicidad es primario, usaría:

- mecanicidad como variable continua calibrada, no cuatro cuartiles;
- curvas con incertidumbre;
- y, si se mantiene estratificación, aspiraría al menos a 15–20 tipos independientes por estrato tras exclusiones.

Eso sugiere un N inicial mayor que 30, o abandonar los cuartiles como endpoint confirmatorio.

---

## 4.3 k=5 es probablemente poco para tipos parciales

Para una tasa binomial cercana a 0,5, con \(k=5\), el error estándar dentro de tipo es aproximadamente:

\[
\sqrt{0.5(1-0.5)/5} \approx 0.22
\]

Es grande. Además, los cinco casos generados por la misma función de mutación no son cinco observaciones independientes; pueden ser casi la misma mutación con valores distintos.

No hace falta subir k para estimar una regla que es verdaderamente binaria, pero sí para:

- detectar cobertura parcial del agente;
- evaluar generalización del autor de reglas a instancias nuevas;
- separar “el tipo es parcialmente detectable” de “tuve cinco ejemplos fáciles/difíciles”.

### Recomendación cuantitativa

No fijaría N ni k desde esas dos varianzas marginales. Haría:

1. un piloto independiente de 8–12 tipos;
2. separación `dev/test`;
3. estimación de covarianza pareada modelo–regla;
4. simulación jerárquica del endpoint exacto;
5. dimensionado contra un efecto mínimo predefinido.

Sin efecto mínimo relevante y sin simulación del diseño real, “N=30, k=5” es una preferencia logística, no un cálculo de potencia.

---

# 5. Otros fallos concretos en §5

## §5.1: criterio incorrecto

“Todo B resulta igual de mecánico” no puede detectarse con cuartiles internos. Necesitáis escala absoluta calibrada y un umbral preinscrito.

## §5.2: el solapamiento no es una única fracción

“Fracción de casos detectada por una regla inducida de A” mezcla:

- similitud sintáctica;
- transferencia de una regla;
- calidad del inductor;
- composición de casos;
- y criterio de detección.

Reportad al menos tres medidas separadas:

1. similitud estructural entre transformaciones;
2. transferencia A→B del inductor;
3. cobertura de la regla congelada real.

No son equivalentes.

## §5.4: bimodalidad no prueba que N sea insuficiente

Que una regla cubra tipos a 0 o 1 es exactamente lo esperable si la cobertura es una propiedad de tipo. Más N estima mejor la mezcla de tipos; no elimina bimodalidad.

El criterio debe ser un intervalo de incertidumbre sobre la proporción de tipos cubiertos, no “si veo dos modos, necesito más N”.

---

# 6. Qué haría distinto

## Diseño recomendado: dos niveles y tres cegamientos

### Nivel 1: validar instrumentos, antes de B

- Auditoría independiente del puntuador.
- Calibración del inductor contra un banco con verdad conocida.
- Definición de DSL, presupuesto y protocolo de actualización de reglas.
- Prueba de que entradas equivalentes reciben puntuaciones equivalentes.
- Prueba de que el inductor no depende de información que el detector evaluado no tiene.

Si falla cualquiera, no encarguéis el conjunto ciego.

### Nivel 2: separar descubrimiento de evaluación

Usad tres conjuntos:

| Conjunto | Uso | Quién lo ve |
|---|---|---|
| A | catálogo conocido y regresión | todos según protocolo |
| B-dev | desarrollo de regla actualizada y calibración de solapamiento | autor de reglas, no agente |
| C-test | evaluación final sellada | nadie que haya desarrollado reglas |

Para cada tipo:

- el autor de reglas puede ver descripción y ejemplos de desarrollo;
- las instancias de evaluación son nuevas y selladas;
- el agente permanece congelado;
- el puntuador recibe salidas anonimizadas;
- el análisis se ejecuta una vez sobre C-test.

### Población de interés explícita

Definid qué población queréis representar:

- mutaciones plausibles generadas bajo un contrato;
- fallos de implementación reales;
- tipos estructuralmente novedosos respecto de A;
- o fallos difíciles para una DSL concreta.

No son la misma población. No podéis filtrar B para que sea lejano de A y luego generalizar a “fallos nuevos” sin cualificarlo.

---

# Decisión recomendada

No aprobaría la v1 con N=30, k=5 ni encargaría B aún.

Aprobaría el encargo sólo tras añadir estas cuatro condiciones de parada:

1. **Puntuador validado independientemente** y ciego a identidad/formato del brazo.
2. **Inductor calibrado**, con DSL, presupuesto, tasa de abstención y umbrales absolutos preinscritos.
3. **B-dev/C-test separados**, de modo que la regla actualizada no pueda ajustar sobre la evaluación.
4. **Protocolo de actualización de reglas fijado**: información, tiempo, lenguaje, recursos y regresión en A.

Sin esas condiciones, un resultado positivo de Q2 no demostraría que el agente detecta fallos para los que no existe una regla estática. Demostraría algo mucho más débil y vulnerable:

> que este agente congelado superó a este autor de reglas, bajo un banco filtrado por instrumentos y puntuado por el mismo laboratorio que definió el problema.