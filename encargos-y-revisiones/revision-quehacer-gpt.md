<!-- modelo: or:openai/gpt-5.6-terra-pro · via: openrouter.ai · encargo: encargo_quehacer.md · 149 s · 85865 tokens -->

## Primero: el «prior = 0» está mal formulado

No se ha medido que \(P(E2)=0\). Se ha observado **0 operadores E2 bajo una operacionalización concreta, en 18 operadores de A**, y además con una ambigüedad importante:

- Si E1 significa «expresable como predicado a partir del **contrato publicado**», entonces los ocho `E1 catálogo` **no están clasificados**: `v3-completo` demuestra que alguien puede escribir una regla conociendo A; no demuestra que el predicado se derive del contrato.
- Si E1 significa «expresable por alguna regla tras ver el catálogo», entonces la medida sí encuentra `E2 = 0`, pero E2 deja de ser «lo que no expresa el contrato» y pasa a ser «lo que ni siquiera cubre una regla post-hoc informada por A». Es otra pregunta, mucho más exigente para que E2 exista.

Además, 0/18 no es evidencia de probabilidad cero. Si los 18 tipos fuesen independientes y representativos —supuestos fuertes y probablemente falsos—, el límite superior unilateral al 95 % es aproximadamente:

\[
p_{E2} < 1 - 0.05^{1/18} \approx 15.3\%
\]

Con dependencia entre operadores de una misma familia, el límite es peor.

La conclusión defendible es más estrecha:

> En A, no apareció ningún operador que el agente detectase y que escapase simultáneamente a `v3-invariante` y a `v3-completo`. Esto reduce mucho la justificación para financiar directamente una Fase 13 completa, pero no demuestra que E2 sea vacía ni que `v3-invariante` haya separado expresabilidad de cobertura inventada post-hoc.

---

# 1. Qué hacer: elegiría **B, pero modificada y con puerta de salida predefinida**

No A. Tampoco C todavía.

La opción correcta es una **B diagnóstica**, cuyo propósito no es publicar una comparación definitiva ni probar superioridad del agente. Su propósito es responder, barato, a una sola pregunta que A no puede responder:

> ¿Aparece al menos un tipo reproducible, no preespecificado individualmente, cuya evidencia discriminante esté dentro del bundle y que sea detectado por el agente pero no sea cubierto por reglas derivadas del contrato bajo un protocolo fijado?

La medida actual hace que sea irracional gastar ya el coste de A: curador, adjudicación masiva, aproximadamente 72 tipos y una pasada confirmatoria. Pero el resultado nulo procede precisamente del banco que el informe reconoce como más favorable a reglas declarativas. Cerrar ahora confundiría:

- «A no contiene E2 observada»;
- con «no hay E2 en fallos emergentes».

B es el experimento que separa ambas cosas.

## B no debe ser exactamente la B propuesta

Tal como está escrita —mismo autor diseña capa, relaciones y análisis; sin preinscripción, reserva ni curación independiente— no puede cerrar «la pregunta del laboratorio con un resultado más fuerte». Puede producir una señal de escalado, pero no una conclusión limpia.

Propongo llamarla explícitamente:

> **B0 — estudio de factibilidad y falsación de la hipótesis E2.**

Y firmar antes una regla de decisión.

### Regla para pasar de B0 a A

Montaría A solo si B0 produce, como mínimo:

1. **Tres tipos E2 candidatos distintos**, no tres instancias del mismo mecanismo;
2. reproducidos en al menos \(k=3\) instancias cada uno;
3. distribuidos en **al menos dos familias** de perturbación;
4. con evidencia necesaria y suficiente dentro del bundle, revisada por adjudicación humana ciega;
5. detectados por el agente bajo el criterio predefinido;
6. no cubiertos por dos autores de reglas independientes, limitados al contrato, la misma interfaz y el mismo presupuesto \(T\);
7. y con una proyección conservadora de que el presupuesto confirmatorio puede producir \(N_{\text{bajo}}\) tipos, no solo uno o dos hallazgos anecdóticos.

El punto 7 debe ser una ecuación firmada, no una impresión. Por ejemplo:

\[
\widehat{\lambda}_{E2,\mathrm{L}} \times E_{\mathrm{confirmatorio}} \geq N_{\mathrm{bajo}}
\]

donde \(\widehat{\lambda}_{E2,\mathrm{L}}\) es un límite inferior predefinido para la tasa de tipos E2 por ejecución o por candidato curado, según la unidad elegida.

### Regla para cerrar tras B0

Cerraría si, tras un presupuesto B0 fijado —por ejemplo, las ~300 ejecuciones del piloto completo, con semillas disjuntas y las vías declaradas—:

- no hay ningún E2 validado; o
- los únicos aparentes E2 se explican por:
  - fallo del puntuador;
  - información no común entre brazos;
  - fuga desde el prompt o desde A;
  - evidencia fuera del bundle;
  - o reglas que un autor independiente cubre dentro del presupuesto fijado;
- o B0 no produce suficientes silenciosos/tipos reproducibles para que A pueda alcanzar \(N_{\text{bajo}}\).

En tal caso, el resultado no es «el agente no sirve». Es:

> Bajo esta arquitectura, esta interfaz de evidencia y esta distribución de perturbaciones, no se encontró la clase E2 que justificaría una comparación confirmatoria costosa.

---

# 2. Ataque a la medida actual

## 2.1 `v3-invariante` no es todavía un proxy válido de «expresable por el contrato»

Es un proxy razonable para una pregunta más modesta:

> «¿Qué cubrió este autor, usando solo el contrato, antes de consultar explícitamente el catálogo?»

No basta para la pregunta fuerte:

> «¿Es expresable como predicado del contrato?»

La diferencia es crucial. La expresabilidad es una propiedad de un lenguaje, una interfaz y un presupuesto. La cobertura escrita por una persona es una mezcla de:

- expresabilidad;
- ocurrencia o no ocurrencia de la idea;
- tiempo dedicado;
- habilidad del autor;
- conocimiento previo;
- y sesgo de disponibilidad.

### Sesgo por conocer A

El autor conoce el catálogo aunque prometa no usarlo al escribir `v3-invariante`. Eso introduce sobre todo sesgo **contra E2**, es decir, hacia concluir que E2 es menor de lo que realmente es.

Puede recordar patrones, campos, familias de errores y formas de fallo de A, y convertir esa memoria en reglas aparentemente derivadas del contrato. No hace falta copiar un operador literalmente para que exista contaminación semántica.

El sesgo puede tener dirección secundaria opuesta —un autor puede evitar conscientemente ideas del catálogo y quedar artificialmente corto—, pero ese sesgo no salva la medida: vuelve la cobertura no interpretable. No hay una garantía verificable de separación cognitiva.

## 2.2 Separarlo barato: sí, pero no se puede probar la no-expresabilidad absoluta

No se puede demostrar barato —ni probablemente nunca— que un fallo **no** es expresable por ningún predicado razonable. Sí se puede medir algo publicable:

> cobertura por reglas bajo lenguaje \(L\), interfaz \(I\), presupuesto \(T\), exposición \(e\) y acceso informativo \(K\).

Protocolo barato:

1. Definir formalmente el lenguaje \(L\): por ejemplo, regex, extracción HL7, condiciones sobre canónico/ACK/log, agregados temporales permitidos y reglas de secuencia.
2. Definir la interfaz \(I\): exactamente los campos y trazas disponibles al agente.
3. Fijar un presupuesto por tipo y total: tiempo, número de reglas, número de ejemplos vistos.
4. Usar **dos autores independientes** de reglas que:
   - no hayan visto A, el catálogo, el prompt afinado ni los resultados de la Fase 12;
   - reciban contrato, estándar, documentación del bundle y una muestra permitida de instancias;
   - trabajen con tipos anonimizados o con candidatos de B0 sin nombres de operador.
5. Puntuar automáticamente las reglas en instancias retenidas.
6. Publicar cobertura, falsas alarmas, coste y desacuerdo entre autores.

Esto separa parcialmente:

- **«hay un testigo constructivo»**: una regla independiente cubre el tipo;
- de **«no se le ocurrió al autor original»**.

No permite afirmar «inexpresable». Permite afirmar:

> No fue cubierto por dos implementaciones independientes del sistema de reglas especificado, dentro del presupuesto declarado.

Eso sí es una definición experimental defendible de residuo.

## 2.3 Problema adicional: `v3-completo` no clasifica E1 contractual

La tabla mezcla dos taxonomías:

| Etiqueta usada | Lo que realmente demuestra |
|---|---|
| `E1 contrato` | Hay al menos una regla derivada del contrato que cubre el operador. |
| `E1 catálogo` | Hay al menos una regla que cubre el operador tras conocer A. |
| `E2 = 0` | Ningún operador detectado por el agente escapó de `v3-completo`. |

La segunda fila no demuestra E1 bajo la definición contractual. Demuestra cobertura post-hoc informada por A.

Por tanto, la tabla debe relabelarse antes de publicarse:

- `C1`: cubierto por reglas de contrato;
- `C2`: cubierto solo por reglas informadas por catálogo;
- `C3`: no cubierto por reglas disponibles;
- `O0`: no observable/detectable con el bundle.

Después se puede discutir si `C2` es coste de descubrimiento, pero no llamarlo E1 sin cambiar la definición.

## 2.4 El criterio binario por caso puede alterar radicalmente la conclusión

El evento que se está midiendo es compuesto:

\[
\text{E2 observado} =
\text{agente acierta}
\land
\text{reglas fallan}
\land
\text{puntuador valida ambos juicios}
\]

Si `ideal_b` o el puntuador son demasiado laxos:

- puede inflar aciertos del agente;
- puede inflar aciertos de reglas;
- puede ocultar falsas alarmas;
- y puede hacer que una coincidencia superficial cuente como detección.

Si son demasiado estrictos:

- pueden castigar detecciones útiles del agente;
- pueden convertir discrepancias de formato en fallos;
- pueden reducir la cobertura de las reglas por detalles irrelevantes;
- y pueden fabricar aparentes E2.

La dirección neta no es deducible sin una matriz de errores por brazo y por clase de caso. Que el mismo criterio fuese usado en el resultado publicado `16/18 a 8/8` garantiza consistencia histórica; **no valida semánticamente el criterio**.

### Validación mínima del puntuador

Antes de usarlo para justificar B0 o A:

- muestra estratificada de positivos, limpios, silenciosos, ACK erróneos, casos disputados y tipos que el agente/reglas discrepan;
- juez humano ciego al brazo y al orden;
- sensibilidad, especificidad y desacuerdo por estrato, no solo acuerdo global;
- la regla v3 de «<90 % no vale» debe aplicarse con intervalos y por clase relevante.

Un 90 % global puede ser engañoso si casi todo son negativos fáciles.

## 2.5 Qué me haría decir que esta medida no vale

Diría que **no vale como medida del prior E2** si ocurre cualquiera de estas condiciones:

1. **Contaminación de información:** `v3-invariante` usa, directa o indirectamente, identificadores, patrones, ejemplos o conocimiento operativo no contenido en contrato y bundle.
2. **Interfaz desigual:** reglas y agente no reciben exactamente la misma evidencia, o el agente recibe información semánticamente equivalente desde prompt, estado oculto, orden, metadatos o herramientas.
3. **Puntuador insuficiente:** la concordancia con jueces ciegos cae por debajo de 90 % en los estratos relevantes, o hay errores sistemáticos en silenciosos/disputados.
4. **Unidad mal definida:** se cuentan 18 operadores correlacionados como 18 observaciones independientes sin análisis por familia/mecanismo.
5. **Clasificación semánticamente errónea:** se etiqueta como E1 contractual un operador cubierto solo por una regla informada por catálogo.
6. **No hay prueba de evidencia en bundle:** el agente aparenta detectar un caso, pero no se demuestra mediante revisión o ablación que la señal discriminante está en el bundle.
7. **El cero depende de sobreajuste:** una segunda implementación independiente de reglas, limitada al contrato, revela cobertura muy distinta de `v3-invariante`.

Cualquiera de 1–3 invalida la inferencia principal. Los puntos 4–7 la vuelven mucho más débil y exigen relabelarla.

---

# 3. Qué sellar en B0 para que diga algo publicable

Sin curador ciego, conjunto reservado ni preinscripción, B0 no puede sostener una afirmación confirmatoria. Pero puede ser publicable como estudio de factibilidad si se sellan estas piezas **antes de ejecutar la primera semilla B0**.

## Mínimo imprescindible

### 1. Manifiesto con huella y fecha verificable

Debe contener:

- familias, rangos, distribuciones y semillas;
- separación de semillas `B0` / confirmatorio;
- presupuesto de ejecuciones;
- relaciones metamórficas;
- definición de tipo, deduplicación y \(k_{\min}\);
- definición de limpios;
- criterio de candidato;
- regla de parada;
- regla de escalado B0 → A y regla de cierre;
- versión del circuito, arnés, agente, prompts, reglas y puntuador.

### 2. Puntuador congelado y auditado

No basta su hash. Debe incluir:

- batería adversaria;
- muestra con juez humano ciego;
- informe de errores por estrato;
- prohibición de cambios tras ver B0.

### 3. Separación mínima de roles

Aunque no haya curador completo, debe haber al menos:

- quien escribe relaciones metamórficas no ve la capa;
- quien evalúa candidatos no ve salidas por brazo;
- dos adjudicadores ciegos entre sí para los candidatos E2 y una muestra de negativos/disputados;
- dos autores independientes de reglas para los candidatos E2.

Si no se puede pagar o conseguir esta separación, B0 sigue siendo útil internamente, pero no debe presentarse como evidencia de E2.

### 4. Evidencia y trazabilidad inmutables

Por ejecución:

- bundle bruto;
- semilla y configuración;
- versión de todos los artefactos;
- salida de cada oráculo;
- salida de cada brazo;
- razones de inclusión/exclusión;
- reglas candidatas y tiempo empleado.

### 5. Retención real

El autor de reglas puede ver solo las instancias permitidas por tipo; la puntuación se hace sobre instancias retenidas. Sin esto, una regla escrita post-hoc puede memorizar el tipo y la comparación no mide nada.

## Qué no podrá afirmar B0 aunque salga limpia

No podrá afirmar:

- que el agente detecta fallos que «nunca vio»;
- que tiene exposición cero a arquetipos de A;
- que el agente supera a reglas en una población representativa;
- una tasa precisa de ventaja;
- generalidad a otros circuitos, estándares o implementaciones;
- que E2 es intrínsecamente no expresable;
- que un resultado positivo no depende de la distribución de perturbaciones diseñada;
- que el hallazgo sería reproducible sin una pasada confirmatoria con curación y conjunto reservado.

Podrá afirmar, como máximo:

> Bajo una distribución de perturbaciones sellada y un protocolo de exploración declarado, se observaron —o no se observaron— tipos candidatos reproducibles compatibles con la definición operacional de E2.

---

# 4. Si se elige C: afirmación defendible

> En el banco A, compuesto por operadores de mutación declarativa y evaluado con el mismo criterio usado en la Fase 12, no se observó ningún operador que el agente detectase y que escapase simultáneamente a las reglas disponibles, incluidas reglas escritas con conocimiento del catálogo. Los resultados muestran que, en esta población, la cobertura de reglas y la disponibilidad del catálogo explican más de la detectabilidad observada que una capacidad exclusiva del agente; además, el agente falló por completo en tres operadores que reglas cubrieron a 8/8. Dado que no se ha validado una población emergente con evidencia dentro del bundle y residuo medido frente a reglas bajo recursos fijados, el laboratorio no justifica el coste de una Fase 13 confirmatoria.

## Lo que **no** puede afirmar

- No puede afirmar que E2 no exista fuera de A.
- No puede afirmar que el agente no detecte fallos emergentes.
- No puede afirmar que todos los fallos observables sean expresables desde el contrato publicado.
- No puede afirmar que los ocho `E1 catálogo` sean E1 contractual.
- No puede afirmar que el agente sea inútil en producción.
- No puede afirmar que las reglas sean globalmente superiores al agente.
- No puede afirmar que el prompt afinado esté libre de contaminación desde A.
- No puede afirmar exposición cero ni independencia semántica entre A y una eventual B.
- No puede afirmar una tasa poblacional de E2 igual a cero.
- No puede convertir 0 de 18 en evidencia de imposibilidad.

---

# 5. ¿Cambia el orden de prioridad?

## Para una Fase 13 completa: la auditoría sigue siendo indispensable

La auditoría C de contaminación semántica sigue sirviendo para una cosa que el cero actual no contesta:

> determinar si una aparente ventaja del agente en B sería evidencia de detección nueva o reutilización de arquetipos de A presentes en el prompt afinado.

Si se quiere afirmar «exposición cero» o interpretar el brazo afinado frente al contrato reconstruido, la auditoría no es opcional. El resultado 0/18 no sustituye esa auditoría: solo reduce la expectativa de que haya señal suficiente para merecerla inmediatamente.

## Pero para decidir B0, sí cambia el orden

Antes, el principal riesgo era gastar en una fase que luego no pudiera interpretarse por contaminación. Ahora el principal riesgo inmediato es más básico:

> que no exista señal E2 operacional ni siquiera fuera de A, o que el cero actual sea artefacto del proxy.

Por tanto, reordenaría así:

1. **Auditoría corta de validez de la medida E1/E2 actual**
   - definición E1 contractual frente a catálogo;
   - procedencia de `v3-invariante`;
   - igualdad de interfaces;
   - puntuador en discrepancias.
2. **Sellar B0**
   - manifiesto, semillas, puntuador, reglas de parada y de escalado.
3. **Relaciones metamórficas independientes y capa sellada.**
4. **B0: piloto de humo + piloto completo.**
5. **Miniadjudicación ciega y doble autor de reglas sobre los candidatos E2.**
6. **Solo si B0 pasa el umbral:** auditoría completa de contaminación A ↔ B y auditoría del prompt afinado.
7. **Solo entonces:** curación, preinscripción final y Fase 13 A.

La auditoría de contaminación ya no debe bloquear un B0 estrecho que no promete exposición cero. Sí debe bloquear cualquier transición a A y cualquier afirmación fuerte sobre novedad semántica.

---

# Accesos que pediría antes de firmar la interpretación de la medida

Para decidir B frente a A no necesito más que el material entregado. Para validar el resultado `E2 = 0` y publicar su interpretación, pediría acceso controlado a:

1. **Código y diff de `v3-invariante` y `v3-completo`**, con historial de commits: comprobar contaminación de catálogo y definir exactamente \(L\).
2. **Contrato publicado y especificación de la interfaz del agente/reglas:** comprobar igualdad informativa.
3. **Prompt afinado y su partición trazable** entre contrato, procedimiento y material derivado de A: evaluar exposición y fugas.
4. **Puntuador, `ideal_b`, pruebas y casos de desacuerdo:** auditar el criterio que define «detección».
5. **Catálogo A y matriz operador → familia/mecanismo:** estimar dependencia efectiva y corregir la falsa impresión de \(n=18\) independiente.
6. **Bundles brutos de los 18 operadores:** verificar que la evidencia de cada etiqueta realmente está dentro del bundle.

Sin esos accesos, mi recomendación sigue siendo B0 y no A, pero el «prior medido en cero» debe publicarse como un hallazgo limitado, no como una clausura ontológica de E2.