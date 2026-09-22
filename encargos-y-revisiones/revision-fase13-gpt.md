<!-- modelo: or:openai/gpt-5.6-terra-pro · via: openrouter.ai · encargo: encargo_fase13.md · 180 s · 51724 tokens -->

## 1. La pregunta

**Corrección principal:** «tipos de fallo para los que nadie ha escrito una regla» no es una propiedad experimental estable. Para cualquier conjunto finito de casos B, alguien puede escribir una regla *a posteriori*. Y que el autor de B no conozca A no implica que B sea semánticamente novedoso: puede recrear, por otra vía, la misma firma observable.

La pregunta original, por tanto, es demasiado fuerte:

> ¿Generaliza el modelo a tipos de fallo para los que nadie ha escrito una regla?

La pregunta que este laboratorio sí puede responder es:

> **¿Detecta el agente, sin adaptación específica a B, fallos silenciosos inyectados por autores independientes y disjuntos de las familias causales de A, mejor que un detector de reglas congelado desarrollado sólo con A, a igual tasa de falsas alarmas?**

Eso mide **transferencia zero-shot fuera de las familias de desarrollo**, no una propiedad general de “razonamiento” ni la inexistencia de una regla posible.

La distinción importa:

- Si el agente gana a reglas congeladas en B, hay evidencia de **robustez a novedad operacional**.
- No demuestra que el agente detecte fallos “no mecanizables”.
- Si las reglas congeladas ganan, puede significar que B comparte firmas con A, no que “las reglas generalizan” en general.
- Si ambos fallan, puede ser falta de observabilidad del fallo, no ausencia de generalización.

El universo objetivo debe limitarse explícitamente a:

1. fallos **silenciosos o semisilenciosos**: el circuito produce un resultado aparentemente válido;
2. fallos con evidencia disponible en las tres herramientas del agente;
3. fallos cuyo impacto pueda ser adjudicado independientemente del generador;
4. familias causales que no se solapen con A según una taxonomía previa.

No hace falta solicitar el catálogo A ni las mutaciones para fijar este diseño.

---

## 2. Cómo fracasaría esta fase y qué medida barata lo destaparía antes

### 2.1 B es “ciego”, pero reproduce las mismas familias de A

El autor de B puede no conocer A y, aun así, producir variantes de mecanismos ya presentes:

- errores de escape o codificación;
- campos HL7 obligatorios ausentes;
- ACK incompatibles;
- errores de correlación;
- transformaciones deterministas incorrectas;
- discrepancias entre entrada, canónico y salida.

Cambiar la sintaxis de la mutación no crea necesariamente una nueva familia causal.

**Consecuencia:** un buen resultado del adversario congelado no demostraría transferencia de reglas; demostraría solapamiento latente A–B.

**Medida barata previa: auditoría de disjunción de familias.**

Antes de ejecutar B:

1. Un árbitro técnico que **sí** puede ver A y B, pero no resultados de los brazos, asigna cada tipo a una taxonomía causal predefinida.
2. El árbitro no revela esa taxonomía ni sus decisiones al autor de B ni a quienes operan el agente y el adversario.
3. Se excluyen del endpoint primario los tipos B que compartan familia con A.
4. Se publica la matriz A–B de familias **después** del cierre.

La taxonomía debe estar por encima de la implementación. Por ejemplo:

- serialización/codificación;
- semántica clínica;
- correlación e identidad;
- orden, estado e idempotencia;
- ACK, transporte y protocolo;
- autenticación/autorización;
- configuración y concurrencia;
- observabilidad y trazabilidad;
- contrato FHIR;
- contrato HL7.

No hay que pedir al autor de B que “no sea mecánico”; hay que medir y controlar el solapamiento sin revelarle la respuesta.

---

### 2.2 B vuelve a contener firmas mecánicas obvias

La objeción que anticipas es correcta. Un autor independiente puede producir tipos nuevos que sean trivialmente detectables mediante:

- una expresión regular;
- una desigualdad entre dos campos;
- una ausencia de token;
- un código HTTP o ACK concreto;
- una condición de longitud, formato o cardinalidad.

En ese caso, que gane el adversario congelado no es muy informativo: sólo dice que sus reglas A ya cubrían una abstracción superficial aplicable a B.

**No se resuelve pidiendo “fallos no mecánicos”.** Eso filtra la hipótesis y empuja al autor a fabricar artificialmente casos favorables al LLM.

**Resolución: tratar la mecanicidad como moderador medido, no como criterio de selección.**

Crear un ensayo auxiliar de “descubribilidad por reglas”:

- Tres ingenieros independientes, que no escribieron A ni B y no ven resultados del agente, reciben sólo:
  - las trazas de una pequeña muestra de desarrollo de cada tipo B;
  - la documentación del circuito;
  - el contrato de transformación.
- No reciben la función Python, la entrada de catálogo ni las etiquetas de generación.
- Tienen un presupuesto fijo: por ejemplo, **60–90 minutos por tipo** y un límite de líneas de regla.
- Escriben reglas para detectar el fallo.
- Esas reglas se evalúan en variantes retenidas del mismo tipo B.

El resultado no cambia la composición de B. Clasifica retrospectivamente cada tipo, con una regla preinscrita:

- **mecánicamente descubrible:** al menos 2 de 3 ingenieros alcanzan sensibilidad y especificidad objetivo;
- **no mecánicamente descubrible bajo presupuesto:** no lo consiguen;
- **indeterminado:** desacuerdo o evidencia insuficiente.

Entonces se publican tres análisis:

1. endpoint primario: todos los tipos B disjuntos de A;
2. estrato exploratorio: tipos mecánicamente descubribles;
3. estrato exploratorio: tipos no descubribles bajo el presupuesto fijado.

Esto evita convertir “no mecánico” en una selección subjetiva hecha después de ver quién gana.

---

### 2.3 El fallo no es identificable desde las tres herramientas

Puede haber mutaciones reales y dañinas cuyo efecto no sea inferible desde:

- HL7 crudo;
- recorrido/canónico/acuse;
- log disponible.

Por ejemplo, dos causas distintas pueden producir el mismo rastro, o el daño puede estar aguas abajo de FHIR Patient y no quedar registrado.

**Consecuencia:** si ambos brazos fallan, no se sabe si no generalizan o si la información necesaria no existe.

**Medida barata previa: prueba de adjudicabilidad humana.**

En un piloto de 8–10 tipos B:

- dos revisores humanos independientes reciben exactamente la misma evidencia que el agente;
- deben decidir si existe fallo, cuál es su clase y qué evidencia lo sustenta;
- se mide acuerdo y exactitud contra una adjudicación de referencia.

Regla operativa:

- si revisores competentes no pueden alcanzar un umbral predefinido, por ejemplo 80% de detección y acuerdo sustancial, el tipo no pertenece al endpoint de “detección desde observables”;
- puede mantenerse como estrato de **no observabilidad**, pero no como fracaso del agente.

---

### 2.4 Fuga desde el generador, el orden o el identificador de trazas

El modelo o el script pueden beneficiarse de artefactos que no existirían en producción:

- prefijos de identificador;
- orden de ejecución;
- nombres de archivos;
- longitudes sistemáticas;
- campos de metadatos;
- diferencias entre corpus limpio y mutado;
- mensajes de log inducidos por el propio arnés.

**Consecuencia:** se mide reconocimiento del banco, no detección del fallo.

**Medidas baratas previas:**

- aleatorizar identificadores, orden, rutas y timestamps;
- usar controles limpios emparejados por plantilla, longitud y canal;
- eliminar cualquier metadato de generación de las herramientas del agente;
- ejecutar un clasificador trivial sólo con metadatos e indicadores superficiales;
- hacer una revisión de “diferencias prohibidas” entre limpio y mutado.

Si un clasificador sin contenido HL7/FHIR supera el azar, el banco está filtrando la etiqueta.

---

### 2.5 Los casos por tipo son réplicas casi idénticas

Ocho mutaciones de la misma plantilla no son ocho observaciones independientes de generalización. Son, como mucho, ocho estimaciones más precisas de la misma firma.

**Consecuencia:** se puede declarar potencia inflada y una ventaja aparente estable que depende de pocas familias causales.

**Medida barata previa: diseño de variantes independientes por tipo.**

Para cada tipo B, variar deliberadamente:

- mensaje base;
- paciente y datos clínicos no causales;
- orden de segmentos;
- valores periféricos;
- condición de activación;
- forma superficial del síntoma;
- ruta de ejecución cuando sea posible.

Y registrar qué dimensiones varían. Si todas las variantes comparten la misma evidencia decisiva, no son réplicas de transferencia, sólo réplicas de ejecución.

---

### 2.6 El autor de B selecciona tipos favorables sin darse cuenta

Aunque sea honesto y ciego respecto de A, un único autor puede preferir su estilo de errores:

- errores que sabe implementar;
- errores que cree interesantes;
- fallos especialmente visibles;
- fallos especialmente ambiguos.

**Medida barata previa: pluralidad y cuota previa.**

Usar al menos 3 autores independientes de B, o bien un autor y una selección aleatoria desde una taxonomía de cuotas preinscrita. Debe conservarse un registro sellado de:

- tipos propuestos;
- tipos descartados;
- motivo de descarte;
- fallos de implementación.

No se deben excluir tipos después de observar el rendimiento, salvo por criterios técnicos ya definidos: ejecución no reproducible, etiqueta inválida o no adjudicabilidad.

---

### 2.7 El modelo conoce B indirectamente

“B no visto por el equipo” no equivale a “B no visto por el modelo”. Un modelo preentrenado puede conocer patrones HL7, FHIR, IRIS, ACK, credenciales, concurrencia o fallos de integración comunes.

Eso no invalida el resultado si la afirmación es operacional —un agente local reconoce patrones nuevos para el equipo—, pero sí invalida afirmaciones sobre “razonamiento sobre tipos inéditos”.

**Medida: acotar la afirmación y congelar el sistema.**

Antes de B:

- congelar hash del modelo, prompt, herramientas, esquema JSON y política de decisión;
- registrar la fecha de corte y versiones;
- afirmar únicamente novedad respecto del **proceso de desarrollo experimental**, no respecto del preentrenamiento.

---

## 3. El adversario congelado

Sí: **es honesto congelarlo**, pero sólo si se presenta como lo que mide.

### Adversario congelado contra B

Mide:

> ¿Cuánto valor tiene el agente el día en que aparece una familia de fallo nueva, antes de que el integrador haya escrito una regla específica?

Es una medición válida y útil de:

- cobertura zero-shot;
- reducción de tiempo hasta la primera detección;
- robustez ante novedad;
- dependencia de mantenimiento manual.

No mide el rendimiento de un sistema de reglas bien mantenido a largo plazo.

### Adversario actualizado contra B

También debe medirse, pero responde otra pregunta:

> ¿Qué coste tiene para un sistema de reglas alcanzar una cobertura comparable una vez que se conoce el nuevo fallo?

El protocolo debe separar tres condiciones:

| Brazo | Información disponible | Pregunta |
|---|---|---|
| Reglas congeladas A | Sólo A | Cobertura zero-shot |
| Reglas actualizadas con incidente B | Ejemplares limitados y diagnóstico del incidente | Coste de adaptación realista |
| Reglas con especificación completa B | Definición formal del tipo B | Límite superior de mantenibilidad de reglas |

Para el brazo actualizado, no basta con medir recall final. Hay que medir:

- tiempo de ingeniería;
- número de ejemplos necesarios;
- líneas/reglas añadidas;
- cambios en reglas existentes;
- regresiones sobre A y limpios;
- sensibilidad en variantes B retenidas;
- coste de inferencia y operación.

El brazo actualizado debe desarrollarse en una partición de desarrollo de cada tipo B y evaluarse en variantes retenidas. Si se prueba sobre los mismos ejemplos que inspiraron la regla, sólo se mide memorización de implementación.

El agente también puede tener un brazo adaptado —por ejemplo, prompt o procedimiento revisado—, pero debe etiquetarse como tal. No comparar “reglas adaptadas” contra “LLM zero-shot” como si respondieran a la misma pregunta.

---

## 4. Endpoint y desglose obligatorio

No usaría una puntuación total agregada. Es exactamente el mecanismo que ocultó el hallazgo de Fase 12.

### Endpoint primario

**Diferencia pareada de sensibilidad macro por tipo de fallo B, en fallos silenciosos adjudicables y disjuntos de A, bajo una restricción fija de tasa de falsas alarmas.**

Formalmente, para cada tipo \(t\):

\[
R_t = \frac{\text{casos mutados correctamente detectados en }t}{\text{casos mutados evaluables en }t}
\]

y el endpoint es:

\[
\Delta = \frac{1}{T}\sum_{t=1}^{T}(R_{t,\mathrm{LLM}} - R_{t,\mathrm{reglas\ congeladas}})
\]

donde cada tipo pesa igual, no cada caso.

La comparación debe estar condicionada a que ambos sistemas cumplan una cota preinscrita de falsas alarmas en controles limpios, por ejemplo:

- FPR observada ≤ 5%, y
- límite superior de IC unilateral de FPR bajo un umbral acordado.

Si el agente detecta todo marcando todo como sospechoso, no ha ganado.

### Qué cuenta como “detección correcta”

Debe predefinirse un criterio jerárquico:

1. **detección de anomalía relevante**;
2. **clasificación correcta de la clase de impacto**, si esa es parte del objetivo;
3. **evidencia válida** en los artefactos observables;
4. opcionalmente, diagnóstico causal correcto.

No mezclar estos niveles en una sola etiqueta sin publicarlos por separado. Un agente que detecta un fallo pero atribuye una causa incorrecta puede ser útil para triaje, pero no para diagnóstico automatizado.

### Desglose obligatorio

Junto al endpoint primario deben publicarse, como mínimo:

1. sensibilidad por tipo B, no sólo media;
2. intervalo de confianza agrupado por tipo;
3. FPR global y por familia de controles limpios;
4. matriz de victorias, derrotas y empates por tipo;
5. rendimiento por familia causal B;
6. rendimiento en tipos disjuntos de A y en tipos con solapamiento detectado;
7. rendimiento por nivel de descubribilidad mecánica;
8. detección, clasificación e identificación causal por separado;
9. resultados del adversario congelado y actualizado por separado;
10. coste de actualización de reglas;
11. todos los tipos excluidos y el motivo de exclusión.

Además, publicar una tabla de casos donde:

- el LLM detecta y las reglas no;
- las reglas detectan y el LLM no;
- ambos fallan;
- ambos alertan falsamente.

La evidencia relevante debe ser revisable sin exponer la clave completa ni el catálogo de mutaciones.

---

## 5. Tamaño y potencia

La unidad de generalización es el **tipo de fallo**, no el caso individual. Los casos dentro de tipo sirven para estimar su sensibilidad, pero no multiplican linealmente la evidencia externa.

Un caso por tipo, como en Fase 12, es insuficiente: confunde el tipo con una realización concreta de su firma.

### Propuesta mínima defendible

| Elemento | Recomendación |
|---|---:|
| Tipos B disjuntos de A en endpoint primario | 50–60 |
| Autores independientes de B | 3 o más |
| Casos mutados por tipo | 8–12 |
| Controles limpios emparejados | 1 por caso mutado, como mínimo |
| Variantes retenidas por tipo para adaptación de reglas | 4–6 |
| Piloto no confirmatorio | 8–10 tipos |

Esto supone aproximadamente 400–720 casos mutados en el análisis principal, más controles. El coste relevante no es ejecutar esos casos, sino construir 50–60 tipos realmente diversos y adjudicables.

### Por qué 50–60 tipos

Para una prueba pareada de “gana LLM” frente a “gana reglas” a nivel de tipo, la potencia depende de los tipos discordantes.

Como aproximación con McNemar, si se espera:

- ventaja neta del LLM de 0,30 por tipo;
- proporción de discordancias de 0,45;
- alfa bilateral 0,05;

se necesitan aproximadamente:

- **40 tipos** para 80% de potencia;
- **53 tipos** para 90% de potencia.

Si el efecto relevante es menor, por ejemplo 0,20, la necesidad sube aproximadamente a:

- **80 tipos** para 80% de potencia;
- **100 o más** para 90% de potencia.

Por ello:

- con 20 tipos B sólo se puede hacer un piloto o detectar efectos muy grandes;
- con 40 tipos se puede sostener una conclusión moderada;
- con 50–60 tipos se puede distinguir razonablemente un hundimiento claro del adversario de fluctuación;
- si se quiere demostrar equivalencia práctica o no inferioridad, hacen falta más tipos y un margen explícito.

### “Los dos se hunden” requiere un test distinto

No basta con observar baja sensibilidad. Hay que predefinir qué significa “hundirse”, por ejemplo:

- sensibilidad macro < 0,40;
- y límite superior del IC 95% < 0,55.

Para afirmar que el LLM y las reglas son prácticamente equivalentes, hace falta una prueba de equivalencia o no inferioridad con margen explícito, no una diferencia no significativa.

### Análisis estadístico

- Estimación principal: diferencia macro pareada por tipo.
- IC: bootstrap agrupado por tipo o modelo binomial jerárquico con efecto aleatorio por tipo.
- Inferencia primaria: prueba pareada a nivel de tipo.
- No tratar los 400–700 casos como independientes.
- Las comparaciones por familia y mecanicidad son secundarias/exploratorias, salvo que se dimensione el estudio específicamente para ellas.

---

## 6. El estrato de fallos reales

Sí merece la pena, pero **no como evidencia confirmatoria de la hipótesis primaria**.

Tiene dos sesgos estructurales inevitables:

1. el autor del laboratorio los conoce;
2. fueron seleccionados porque ocurrieron, se documentaron o resultaron memorables.

Además, ocho o diez incidentes no dan potencia para inferencia estadística.

### Uso correcto

Reportarlo como:

> **Serie de casos histórica, contaminada por conocimiento del autor y no incluida en el endpoint confirmatorio.**

Puede aportar valor cualitativo para responder:

- ¿los patrones de fallo reales se parecen a los sintéticos?
- ¿las tres herramientas contienen evidencia suficiente?
- ¿el agente explica o sólo alerta?
- ¿qué clases operacionales faltan en B?

### Salvaguardas

- congelar agente, reglas y puntuador antes de ejecutar el estrato;
- que la adjudicación de salida la haga alguien que no haya construido esos fallos;
- ocultar al evaluador qué casos son “reales” y cuáles controles;
- publicar todos los casos candidatos, incluidos los no evaluables;
- no mezclar sus resultados en la media primaria B;
- informar cada incidente individualmente, con evidencia y limitaciones.

La formulación correcta no es “el modelo generaliza a fallos reales”, sino:

> “En una serie histórica contaminada de N incidentes, el agente detectó X; este resultado es descriptivo y no confirma la hipótesis de transferencia.”

Si se quiere una validación real confirmatoria, debe ser prospectiva: incidentes futuros, sellados antes de evaluar el sistema, con adjudicación independiente.

---

## 7. Lo que mediría en la primera semana para no construir sobre arena

1. **Congelación técnica**
   - Hash de modelo, prompt, herramientas, esquema JSON, script A y puntuador.
   - Registro de versión de IRIS, configuración del circuito y entorno de ejecución.
   - Política fija de conversión de JSON a alerta/no alerta.

2. **Piloto de 8–10 tipos B**
   - No entra en el análisis confirmatorio.
   - Comprueba ejecutabilidad, estabilidad, etiquetado y variación real entre casos.
   - Si falla, se corrige el protocolo, no se “arreglan” los resultados del conjunto final.

3. **Prueba de adjudicabilidad**
   - Dos revisores humanos con las mismas tres herramientas del agente.
   - Medir detección, acuerdo y evidencia disponible.
   - Excluir del endpoint primario tipos no identificables desde los observables.

4. **Auditoría de fuga**
   - Clasificador trivial con identificadores, orden, longitudes y metadatos.
   - Controles limpios emparejados.
   - Revisión de que ni agente ni script reciben atributos del generador.

5. **Auditoría de disjunción A–B**
   - Árbitro independiente asigna familias causales.
   - Matriz sellada antes de resultados.
   - Definir de antemano qué constituye solapamiento excluyente del endpoint principal.

6. **Ensayo de descubribilidad por reglas**
   - Dos o tres ingenieros independientes.
   - Presupuesto fijo de tiempo y ejemplos.
   - Evaluación en variantes retenidas.
   - Clasificar mecanicidad como resultado, no como filtro creativo.

7. **Chequeo de dependencia intratipo**
   - Verificar que los 8–12 casos por tipo no comparten exactamente la misma evidencia decisiva.
   - Documentar qué dimensiones se han variado por tipo.

8. **Simulación de potencia**
   - Antes de fabricar todos los tipos, simular decisiones con 40, 50 y 60 tipos bajo varios patrones de discordancia.
   - Fijar el tamaño final por el efecto mínimo de interés, no por conveniencia de construcción.

9. **Ensayo de actualización de reglas**
   - Definir desde la primera semana el presupuesto de tiempo, ejemplos y acceso para el brazo actualizado.
   - Si no se define entonces, el brazo actualizado se convertirá en una demostración artesanal imposible de comparar.

La condición de éxito de la primera semana no es que el LLM gane ni que las reglas fallen. Es demostrar que B será: **disjunto de A, adjudicable desde los observables, libre de fugas triviales y suficientemente diverso como para que “tipo nuevo” signifique algo experimentalmente.**