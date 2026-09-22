<!-- modelo: deepseek-v4-pro · via: api.deepseek.com · encargo: encargo_fase13.md · 359 s · 21065 tokens -->

**Primero, el defecto de raíz que veo:** la Fase 13 propone corregir el *conocimiento* del catálogo, pero no corrige la *estructura* que mató la Fase 12. B seguirá siendo un catálogo cerrado de mutaciones declarativas encargado a un autor. Que el autor no vea A no impide que una mutación nueva tenga una firma mecánica igual de explotable. Eso no invalida la fase por sí solo, pero obliga a medir la novedad estructural de B y a no usar un solo caso por tipo.

---

## 1. La pregunta

Es la dirección correcta, pero hay que reformularla para que sea contestable sin caer en la trampa de la Fase 12.

No midas:

> ¿Generaliza el modelo a tipos para los que nadie ha escrito una regla?

Eso es demasiado absoluto: “nadie” es inverificable. Además, el modelo no es cero-shot; puede haber visto fallos similares durante el pretraining.

Mide:

> Congelados agente y adversario-A, y sobre un B generado independientemente de A, ¿el agente obtiene mayor sensibilidad por tipo que el adversario-A sin más falsos positivos en limpias, y esa ventaja se sostiene frente a un adversario actualizado contra B?

Esta pregunta separa dos cosas distintas:

- **Congelado**: ¿el agente captura lo que las reglas viejas no capturan?
- **Actualizado**: ¿el agente sigue aportando cuando un integrador escribe reglas nuevas para B?

La segunda es la que decide la operación. Un sistema de reglas puede no generalizar sin mantenimiento, pero si con 4 horas de mantenimiento iguala al modelo, el modelo solo vale para el periodo previo al mantenimiento. Eso debe quedar medido, no implícito.

---

## 2. Cómo fracasaría esta fase y qué medida barata lo destaparía antes

La Fase 13 puede fracasar por al menos cinco vías. La más importante es la primera.

### 2.1 B puede volver a ser mecánico aunque el autor sea ciego

El autor ciego no conoce A, pero conoce el circuito y el contrato de transformación. Eso le permite generar fallos por las mismas fuerzas sintácticas o contractuales de siempre:

- falta un campo obligatorio;
- código fuera de la tabla;
- escape mal formado;
- cardinalidad incorrecta;
- acuse `CE` en vez de `CA`.

Aunque no conozca las 63 reglas de A, muchas mutaciones de ese estilo son detectables con reglas genéricas. El adversario congelado volverá a ganar, o al menos no se hundirá, y la fase no habrá medido generalización de modelo sino re-etiquetado del mismo catálogo.

**Medida barata al principio:**

Genera un **B_pilot** de 3–5 tipos provisionales, *no* usados en el final. Sobre ese B_pilot ejecuta:

1. 10 reglas genéricas del contrato HL7/FHIR, escritas por un ingeniero que no ve B;
2. un Random Forest de n-gramas sobre HL7 crudo + log;
3. el adversario congelado;
4. el agente.

Si las reglas genéricas o el Random Forest ya detectan B_pilot con sensibilidad ≥ 0,30 a FPR = 0, o con AUC > 0,80, B es estructuralmente mecánico y no sirve para la pregunta primaria. No se lo digas al autor como criterio; simplemente descarta o regenera el conjunto.

### 2.2 B puede solaparse con A sin que el autor lo sepa

El autor ciego no ve A, pero el contrato es el mismo. Dos catálogos creados sobre el mismo contrato pueden compartir firmas.

**Medida barata:**

Calcula solapamiento de firmas entre A y B_pilot: tokens, posiciones de campo, códigos alterados, clases de mutación. Un solapamiento alto de características activas del adversario-A es señal de que B no es nuevo.

No uses el B_pilot para el análisis final si ha servido para validar el instrumento. Destina un pool separado.

### 2.3 El scorer puede no ser válido para B

El puntuador firmado con 16 autopruebas probablemente está calibrado contra A. B puede contener fallos que el scorer no detecta o clasifica ambiguamente.

**Medida barata:**

En B_pilot, compara el scorer contra etiqueta humana independiente. Si el acuerdo es menor de 90 %, o si hay más de un 10 % de casos con adjudicación ambigua, B no está listo.

### 2.4 Un caso por tipo repetiría el error de la Fase 12

La Fase 12 tenía un caso por operador. Eso hace imposible distinguir sensibilidad 0 de sensibilidad 1 salvo por un acierto binario. No lo repitas.

**Medida:** mínimo 5, recomendado 8 casos por tipo nuevo.

### 2.5 La agregación puede volver a esconder el resultado

Ya pasó en F12: un brazo ganaba en limpios y perdía en silenciosos, y la resta global parecía neutra.

**Medida:** endpoint por tipo, no total único. Lo detallo en el apartado 4.

---

Sobre el punto que ya veías:

> “El autor ciego puede escribir tipos igual de mecánicamente obvios, y pedirle que no sean mecánicos le filtra la respuesta.”

Se resuelve así:

- **No le hables de detección.** Al autor se le encarga documentar *incidentes operativos*: casos en los que el sistema falló o fallaría ante un consumidor downstream. No se le dice “evita que sea mecánico”.
- **Pídele narración causal, no solo función de mutación.** Cada tipo debe incluir: mecanismo de fallo, por qué un operador humano podría no verlo, y qué evidencia dejaría en las herramientas.
- **Prioriza fallos semánticos y de proceso, no sintácticos.** Por ejemplo: identificación ambigua de paciente, ACK aceptado sin persistencia real, credencial inexistente devolviendo 404 en vez de 401, `PoolSize=1` bloqueando el servicio.
- La mecanización no se evita pidiéndoselo al autor; se filtra después con la sonda estructural.

---

## 3. El adversario congelado

Congelar al adversario contra A es honesto, **siempre que se declare qué pregunta responde**.

- Adversario congelado = escenario “sin mantenimiento posterior al fallo nuevo”.
- Adversario actualizado contra B = escenario “el integrador ha escrito reglas para el fallo nuevo”.

Ambas comparaciones importan, pero requieren diseños distintos.

### 3.1 Congelado

Debe seguir exactamente el mismo umbral y las mismas reglas que se usaron contra A. Si el adversario tiene umbrales de decisión, re-calíbralos solo con limpias de A antes de abrir B. No lo re-calibres con B.

Si el adversario congelado se hunde en B, eso indica que sus reglas no cubren B, no necesariamente que las reglas mecánicas no podrían cubrirlo.

### 3.2 Actualizado contra B

Es la comparación que importa para operación, pero solo es válida si el autor de nuevas reglas **no ve B_test**.

Divide B en:

- **B_adapt**: 4–5 tipos para que el integrador escriba y ajuste reglas nuevas.
- **B_test**: 10–15 tipos para evaluación final.

El adversario actualizado se entrena o calibra con B_adapt. Luego se evalúa en B_test. Si le das B_test al autor de reglas, estarás repitiendo la Fase 12: sobreajuste por conocimiento del conjunto.

### 3.3 Interpretación de los tres resultados

| Resultado | Interpretación |
|---|---|
| Adversario-A se hunde y agente aguanta | El agente captura fallos no cubiertos por reglas viejas. Valor sin mantenimiento. |
| Adversario-A y agente se hunden | El agente reconocía firmas de A, no la semántica de fallo. |
| Adversario-A aguanta | Las reglas viejas generalizan a B. Publicable, pero no demuestra valor del modelo. |
| Adversario actualizado iguala o supera al agente | El valor del modelo es transitorio: solo el tiempo que tardas en actualizar reglas. |
| Agente supera también al adversario actualizado | Valor más robusto del modelo. |

Congelado y actualizado no deben mezclarse en un único endpoint. El actualizado es secundario o co-primario, pero con B_adapt separado.

---

## 4. Endpoint y desglose obligatorio

La Fase 12 se ahogó en un total. La Fase 13 debe ser por tipo.

### Endpoint primario propuesto

Para cada tipo \(t\) de B_test:

\[
D_t = R_{\text{agente},t} - R_{\text{advA},t}
\]

donde \(R\) es la sensibilidad por tipo calculada sobre los casos positivos de ese tipo.

Resumen primario: \(\bar D\), media de \(D_t\) sobre tipos B_test.

Hipótesis nula:

\[
H_0: \mathbb{E}[D_t] \le \delta
\]

con \(\delta\) preinscrita. Sugiero \(\delta = 0,15\) o \(0,20\). No uses 0 exacto: con pocos casos por tipo, una ventaja de 1 caso puede ser ruido.

### FPR en limpias

Ambos sistemas deben evaluarse con las limpias de B_test. El endpoint no es sensibilidad sola. Es sensibilidad por tipo **condicionada a FPR ≤ 0,05** en las limpias.

Si uno de los dos produce falsas alarmas en limpias, su sensibilidad no es comparable.

### Desglose obligatorio a publicar

Sin este desglose, la fase no es interpretable:

1. Tabla por tipo B_test:
   - familia de fallo;
   - número de casos positivos;
   - TP, FN, FP, TN para agente y adversario-A;
   - sensibilidad agente;
   - sensibilidad adversario-A;
   - \(D_t\);
   - intervalo de confianza binomial exacto para cada sensibilidad.

2. Tabla de limpias B:
   - N;
   - falsos positivos agente;
   - falsos positivos adversario-A.

3. Gráfico de \(D_t\) con IC por tipo, ordenado de mayor a menor ventaja del agente.

4. Análisis por familia o mecanismo de fallo, si hay al menos 3 tipos por familia.

5. Casos excluidos o inválidos, con causa: parseo imposible, scorer no definido, etc.

No publiques solo \(\bar D\) ni una media macro global. La media sin el desglose por tipo es la trampa de F12.

---

## 5. Tamaño y potencia

Un caso por tipo no sirve. Necesitas estimar sensibilidad por tipo.

### Recomendación

| Parámetro | Mínimo | Recomendado |
|---|---:|---:|
| Tipos B_test | 10 | 15 |
| Casos positivos por tipo | 5 | 8 |
| Total positivos B_test | 50 | 120 |
| Limpias B_test | 15 | 25–30 |

Con \(k=8\) casos por tipo y sensibilidad esperada en torno a 0,50, la desviación típica de la diferencia por tipo es \(\le 0,25\).

Con 15 tipos:

\[
SE(\bar D) \approx \frac{0,25}{\sqrt{15}} \approx 0,065
\]

Una ventaja media de 0,20–0,25 ya estaría en el límite de detectabilidad con potencia 80 % y \(\alpha = 0,05\). Si esperas una ventaja menor que 0,15, no montes esta fase con estos números.

Para detectar \(\delta = 0,15\) con seguridad, necesitarías más de 30 tipos o más de 10 casos por tipo, y probablemente no merece la pena.

### Análisis

No uses una prueba t si \(D_t\) es discreta y asimétrica. Usa una prueba de permutación o Wilcoxon por pares sobre los \(D_t\). Como secundario, un modelo logístico mixto con efecto aleatorio por tipo puede aprovechar mejor los datos, pero no lo uses como endpoint primario si hay menos de 15 tipos.

### Potencia para “el adversario se hunde”

Define “se hunde” operativamente, no como impresión:

- sensibilidad del adversario-A \(\le 0,25\);
- y agente \(\ge 0,60\) en el mismo tipo.

Eso exige \(k \ge 8\) para no confundir 0/1 con ruido.

---

## 6. El estrato de fallos reales

Sí merece la pena, pero **como validación secundaria y no primaria**.

El problema ya lo has identificado: el autor del laboratorio los conoce. Eso es contaminación directa. Por tanto, no sirven para demostrar que el agente generaliza a fallos no vistos.

Lo que sí sirven:

- detectar regresiones reales del agente;
- detectar puntos ciegos del scorer;
- dar un anclaje de validez ecológica;
- estudiar fallos de proceso que los catálogos sintéticos no cubren.

Reglas para reportarlos sin que contaminen la conclusión:

1. Se reportan **separados** de B_test.
2. No entran en el endpoint primario.
3. Se publican caso a caso, no como media.
4. Se etiquetan como “históricos, conocidos por el autor del laboratorio, no ciegos”.
5. Si se puede, que un tercero redacte o reconstruya los fallos reales a partir de notas antes de ver agente y adversario.

Si no puedes separar la contaminación, déjalos fuera del análisis inferencial y trátalos como anécdotas operativas.

---

## 7. Lo que mediría en la primera semana para no construir sobre arena

Antes de comprometer B_test:

1. **Generar B_pilot** con 3–5 tipos provisionales.
2. **Ejecutar las sondas**:
   - reglas genéricas de contrato;
   - Random Forest de n-gramas;
   - adversario congelado;
   - agente.
3. **Calcular solapamiento de firmas** con A.
4. **Validar el scorer** contra etiqueta humana independiente.
5. **Simular potencia** con los datos de B_pilot para fijar:
   - número final de tipos;
   - casos por tipo;
   - \(\delta\).
6. **Congelar preinscripción**:
   - endpoint primario;
   - criterio de exclusión de tipos;
   - umbrales de las sondas;
   - análisis estadístico.

Si en esa primera semana el adversario congelado o una regla genérica ya detecta B_pilot con fuerza, no sigas con ese B. Cambia la generación de B, no el umbral.

Bloquea B_test solo después de que el piloto haya validado que B no es un calco mecánico de A. Y no uses B_pilot en el análisis final.

---

## Razonamiento del modelo

We need answer in Spanish, Markdown, concrete, no filler. Need respond to user's request. Need analyze their proposed Phase 13 design, identify flaws, answer sections 5.1-5.6 plus maybe order by specified. Need be critical. Need likely discuss methodological issues with mutation testing/benchmark contamination, generalization, adversarial rules, endpoints, power.

Need think deeply. Need produce final only maybe with headings. Need not use analysis. We can reason here.

Let's parse prompt.

User is consultant senior. They present lab: ADT^A01 MLLP to FHIR Patient in IRIS, agent qwen3-coder triage reads tools and emits verdict JSON, scorer, adversary bank. Phase 12 measured agent works but unnecessary: regex script beats +0.873 vs +0.629, no own detections. Reason: corpus constructed by declarative mutation operators with mechanical signatures; closed set of 63; script knows all. They want Phase 13 to answer: "¿Generaliza el modelo a tipos de fallo para los que nadie ha escrito una regla?" Design: Set A 63 operators adversary and agent developed. Set B blind N new types commissioned to author who sees circuit and transformation contract but not adversary/catalog A/agent. Delivers catalog entry and Python mutation. Both run on B, adversary frozen on A. Three outcomes. Secondary stratum real failures known by lab author, contaminated.

They ask:
5.1 Is "generalize to unseen types" right question or better? critique. If still not answerable with this lab, say now.
5.2 What would make Phase 13 also unable to answer question. This most important. F12 invisible fatal construction. Tell flaws and cheap measure to uncover at beginning. At least one they see: blind author can write types equally mechanically obvious, then adversary wins and learn nothing. Asking "not mechanical" filters answer. How resolve without contaminating?
5.3 Frozen adversary. Honest? Measure both frozen and updated against B? meaning?
5.4 Endpoint without aggregation trap. Primary endpoint, unit, mandatory breakdown.
5.5 Size and power. How many new types, cases per type, power to distinguish "adversary sinks" from noise. F12 unit macro per operator, reserved one case per operator.
5.6 Real failure stratum worth despite contamination? If yes report to avoid contamination.
Format ordered: (1) question; (2) how fail and cheap measures; (3) frozen adversary; (4) endpoint/breakdown; (5) size/power; (6) real failures; (7) first week measurements.

Need provide concrete technical, maybe formulae.

Let's formulate.

First, identify possible fatal flaws. Need think of experimental design issues.

Question: "Does model generalize to types of failure for which nobody has written a rule?" This is valid but subtle. Need operationalization. We need define "type not seen" in terms of agent's training and adversary's rules? There is leakage from base model? qwen may have seen FHIR/HL7 failure patterns. But main question contrasts model vs regex adversary. Need avoid constructing B in a way that is a proxy for A. The fatal flaw in F12 was closed declarative mutation set, mechanical signatures, author knows full set. F13 with blind B still can fail because:
- The blind author, even without catalog A, can produce mutations that share low-level signatures with A (e.g., character replacements, missing fields, status codes) because the transformation contract implicitly defines all possible mutations. The space is finite; any mutation must alter input tokens, and mechanical features (regex patterns) can detect many.
- The adversary is frozen against A but not necessarily against the blind author's generation style. If author uses same generative style or if B types are implemented via same few synthetic mutators (e.g., string deletion, field removal), the frozen regex may generalize trivially.
- Selection of B may be biased by feasibility: author will produce types that are instantiable in Python and detectable by scoring; excludes ambiguous or semantic failures.
- The "new types" might not be new at the operational level; they may be relabeling of A types. Need independent classification, not just author's declaration.
- The model and adversary both may exploit dataset artifacts from circuit/simulator, not general failure semantics.
- The primary comparison may be undefined if both run on B and scoring same but "adversary frozen" maybe it has false positives on clean cases B? Need include clean cases.
- If adversary built against A using rules, it might output no detections for new types; "se hunde" could be because threshold/rule coverage not because rules can't generalize.
- Agent may fail due to distribution shift not due to generalization: B mutations may break parsing before reaching agent, or produce malformed HL7 causing tool failure. Need control.
- The endpoint may aggregate again: if using aggregate AUC or macro per type, could hide per-type results. Need per type, per family, and confidence intervals.
- Non-inferiority? We need decide what "model aporta" means. Need pre-register decision rule and non-inferiority margins for false alarms.
- Need adversarial development separation: If adversary frozen against A, but whoever evaluates B might adjust? Need blinding of evaluation.
- The blind author is also the generator; if they know the hypothesis, they may consciously/unconsciously create types that favor/disconfirm model? They know contract, not catalog. That's okay? But they likely want to demonstrate model generalization? Need prevent expectancy by having authors generate types with business rationale, not to prove point.
- "Pedirle 'que no sean mecánicos' le filtra la respuesta." Need solve by not asking for 'non-mechanical' but by defining unpredictability mechanically: require mutations that are stipulated as semantic/invariant? Or use an independent panel to classify the resulting signatures as "mechanically detectable" with a baseline model. Cheap measure: produce a battery of simple baselines (regex, tf-idf, random forest on token features) on B early; if baselines perform high, B is not testing generalization beyond shallow features. But that's after B. Before full experiment, generate B, then run cheap baseline probes (including "zero-shot" regex distilled from A? no). If simple baselines achieve high detection, you know B is mechanical. But then you've contaminated? Not really if never used by agent/adversary? But evaluation results can be seen? Need separation.

Need mention "construct validity" of B as unseen types. Need define an independent criterion of novelty: taxonomize failure surfaces (transport, syntax, semantics, orchestration, security) and require B types cover surfaces not represented in A, not just new parameters. The blind author could be asked to write a "field failure report" in natural language before seeing tools, with causal mechanism; then another engineer implements. The author should not know exact signatures? Hmm.

Question 5.1: Is "generalize to unseen types" right? Need maybe reframe: It asks whether model adds over rule system on failures whose signatures are not in training/adversary. But at test time any finite B still has some signature; the difference isn't "rule vs no rule" but "known rule vs unknown rule." The proper question might be: "Does the model exceed a rules baseline when both are evaluated on failure modes generated independently of the baseline's rule set, under a pre-specified novelty criterion?" That's okay. Better question: "¿Aporta el modelo precisión incremental sobre el mejor adversario de reglas cuando el tipo de fallo es nuevo para ambos y además el propio autor no sabe qué rasgos detectará el modelo?" But perhaps even better: compare not to regex but to a simple learned baseline trained on A. The critical question is generalization under distribution shift from A to B: "¿Se sostiene la ventaja (o no inferioridad) del agente frente a un adversario no actualizado cuando los tipos de fallo se muestrean de una distribución de fallos reales/semánticos independiente del catálogo?" Hmm.

Need maybe say: "Generalizar a tipos no vistos" is correct direction, but insufficient as stated. Need require:
- novelty of type, not just instance: B types must be derived from independent failure taxonomy, not recombinations of A transformations.
- no shared artifact: B generation must not use the same mutator code or catalog schema.
- evaluator blind to provenance.
- include negatives: clean cases and near-misses.
- pre-specified equivalence margin for false positives.

Need identify possible fatal flaws and cheap measures to uncover early.

Potential fatal flaws Phase 13:
1. **B is still a synthetic mutation catalog.** If author writes "catalog entry and Python function" per type, even blind, it recreates same declarative structure as A. The adversary may not need catalog: similar mutation functions produce detectable perturbations. The design might still answer "generalize to B synthetic types" but if B types are generated as mechanical perturbations, not actual novel failure mechanisms, conclusion won't extend to real operations. Cheap measure: During first week, generate B pilot (3-5 types) and run:
   - a zero-shot regex baseline (not updated) and
   - the frozen adversary
   - a shallow classifier (bag-of-words/random forest on HL7 and log tokens)
   - the agent.
   If shallow baselines or frozen adversary got high per-type detection on pilot, B types are not sufficiently novel; redesign author instructions before scaling. But see blinding: do not use same pilot for final. Need maybe allocate a "probe set" separate from final B. Could also compute "signature overlap": extract features used by adversary A and by simple baselines; check if B types can be detected by features. Cheap metric: n-gram overlap, edit distance distributions.
2. **The agent may have been trained or exposed to A, and B generated by same environment.** Need ensure B not leaked into agent training; qwen local may not have internet. But maybe fine-tuning on A? Need freeze agent too? They said agent? not explicit. Need freeze both agent and adversary. If agent can be updated? Should be frozen. If not, possible confound.
3. **Ratings/scorer may be designed around A.** The scorer with 16 self-tests maybe detects exact categories; B may include failures not captured by scoring schema. Need ensure scorer can grade B types fairly. If scorer's labels are derived from A's catalog, B may be invisible or trivially. Cheap measure: pilot B types and verify scorer inter-rater reliability with human labels, and that ground truth is well-defined.
4. **No clean controls in B** — false positives on B clean cases? Need include.
5. **Data size too small** — maybe 10 types with 1 case each yields zero power for detecting moderate differences. Need address in 5.5.
6. **The author of B, though blind to catalog A, may produce types that are simply not failures or not detectable by tools.** Need formal definition and inclusion criteria. Cheap measure: have two independent engineers validate each B type against contract: (i) it is a real failure (system should flag), (ii) it is feasible, (iii) it is not trivially visible in input. But if they know? Need separate panel from evaluator.
7. **Rule adversary frozen is not a fair baseline if its output is not adapted to B's base rate/format.** Could fail because it was tuned to A's distribution and outputs many alerts? Need recalibrate threshold on A only, but apply to B. Pre-register. Could have false positive on B clean.
8. **Aggregation hides within type results.** Endpoint must be per-type sensitivity at fixed false positive rate (or partial AUC) and exact McNemar per type. Need no totals as primary.

Need possibly say design can answer but only if B truly independent and you run a "cheap probe battery" early. Need maybe propose a two-stage design: a pilot phase generating B types, then run baseline probe to verify novelty prior to lock. But does that contaminate? Need separate B_pool: generate, probe, select? Hmm if you select B types after seeing baselines, that can bias toward harder ones (or easier). Need pre-register selection criteria not dependent on primary outcomes. Option: have author generate more B types than needed, say 20, then randomly sample 12 for final; do not drop based on results. But to uncover "mechanical obviousness", you need inspect pilot on a separate calibration set not used final. Could generate B_pilot from same author with instruction, not used final, only to check design. That is fine but costs. Or compute structural metrics before running agent/adversary: e.g., apply a generic feature extraction from all existing rules? Hmm.

Need think about their known issue: "blind author can write types equally mechanically obvious". How resolve without contaminating? Need answer:
- Do not tell author "avoid mechanical". Instead, change the authorship task from "write mutation function" to "report a real failure scenario in operational terms" and have a separate implementer who writes the mutation. But even implementer may produce mechanical signatures. However, if the failure emerges from an operational scenario (e.g., "downstream system drops the message after sending ACK; resulting patient isn't created"), the mutation function may need to simulate a sequence, not just syntactic edit. That may be less mechanical.
- Better: use an independent "failure mode discovery" process: interview or incident reports from real-world FHIR integrations, not from catalog. Create types from actual incident narratives. But still only 8-10 real.
- Or require B types to include two categories: (a) semantic failures that preserve syntactic validity (e.g., wrong patient chosen due to identifier matching ambiguity); (b) sequencing/resource failures. These are harder for regex.
- To avoid filtering answer, don't mention adversary/model/detection at all to author. Frame as "documenting failures for operational test suite". Give them business context: "produce failures that would affect a downstream consumer." They don't know it's to test mechanical rules.
- To verify not mechanical without contaminating: define a pre-experimental "mechanicity probe" that is run by a separate engineer, not author, and its output is not used to tell author to revise. Instead, if probe shows too many types are mechanically detectable by a simple generic rule set, the entire B set is discarded/re-generated with a different author, not tuned. Need avoid cherry-picking. Use a decision rule: e.g., if >50% of B types are detected by a baseline with sensitivity >0.5 at FPR=0, B is invalid; do not analyze further. But if you discard and regenerate, that is okay if pre-registered as pilot; final B is locked only after passing structural criteria. Need be careful with selection effects. The pilot can be non-final.

Another problem: the frozen adversary against A maybe still uses 63 rules. The B author may inadvertently produce a mutation that exactly matches one of those 63 types even if blind. Need run a "duplicate detection" comparison using embeddings/rules? Maybe.

Need maybe discuss the endpoint. In F12, aggregation hid. Proposed primary should be **per-type sensitivity at a fixed false positive rate (e.g., FPR=0.05)**, not overall. But small sample per type; maybe combine with paired comparisons. Need precision.

Need think in terms of diagnostic metrics. Each case classified: true positive per type. We need compare agent vs adversary across B types. Unit: type. For each B type with k cases, compute sensitivity (or detection rate). Pair types: difference in sensitivity agent - adversary. Primary endpoint: mean per-type difference in sensitivity over B types, at fixed global false-positive threshold. But if k small, difference can be -1,0,1. Need maybe use mixed-effects logistic regression: correct detection ~ system + (1|type) + (1|case). Then report odds ratio. But sample may be small.

Need propose primary: **proportion of B types where agent detects at least one case that the frozen adversary misses, minus proportion where adversary detects at least one case agent misses, with both required to maintain zero false positives on clean cases.** But with one case per type? Not enough. Could use multiple cases per type to estimate sensitivity.

Need handle false alarms: clean cases B must be included. Could define endpoint as partial AUC 0-0.05 FPR or mean sensitivity at FPR=0.05. But if clean B cases few, FPR estimates unstable.

Need "unidad" maybe "type-level recall at case-level false-positive rate = 0 on paired clean cases". Need mention: Disaggregation mandatory: per type, per category, per system, 2x2 contingency table (TP, FN, FP, TN) plus confidence intervals. No single total without per-type.

Need "endpoint primario" maybe:
- **Detección incremental del agente frente al adversario congelado**: \(D_j = \text{Recall agente}(T_j) - \text{Recall adversario}(T_j)\) for each new type \(T_j\). Primary summary: mean \(D_j\) across B types, but decision rule:
   - agent adds value if mean D > δ and no type where adversary significantly outperforms agent? Or if D positive and credible interval excludes 0.
- Must include **false positives on clean companion cases**. If any system produces any FP in clean cases, its recall is not interpretable. Use threshold chosen before B on A to achieve FPR=0 (or ≤1 clean misclassified) and applied unchanged.
- Maybe also report **coverage: types where agent detects all cases vs adversary detects all**.
- Because one case per type results zero/low precision, need k cases per type. For exact per-type comparison, k=8 or 16. Need sample size.

Need compute sample size. Let's think.

We need distinguish "adversary se hunde" from noise. Need think effect size. In F12, adversary got 16/18? Actually F12: regex +0.873 vs model +0.629, and agent detects 10 de 18 operators; regex 16 de 18? "script bate +0.873 contra +0.629" maybe macro per operator scores. Need know scoring. Could be +1 per operator if correctly? But no.

For Phase 13, we compare per-type recall. Suppose under alternative model generalizes, adversary performs poorly on B. We might expect agent recall e.g., 0.70, adversary 0.20. Difference 0.50 per type. Under null no difference. Need random effects.

If k cases per type, per-type recall has standard error sqrt(p(1-p)/k). For k=8, SE ~0.17. Difference SE ~0.24. But across 12 types, mean difference SE maybe 0.07 if independent; power good for 0.3. But if only 10 types and one case per type, difference binary, very low. Need maybe k=5? 8? Need propose "at least 12 B types, 8 cases per type = 96 B cases plus 24 clean cases." But is that too many? Need manageable.

Need use exact binomial/paired tests. For per-type comparison to detect difference of 50 points with 80% power at α/10=0.005 if Bonferroni, need? Let's approximate: McNemar? Actually paired cases detect difference in sensitivity. We can have k cases per type, compare two systems on same cases. For each case, outcome detection correct yes/no. Difference in paired proportions. For k=16, MC simulation can detect difference of .25 maybe. But let's propose continuous.

Need maybe include formula:
\[
N_{\text{types}} \cdot k \quad \text{with} \quad P(|D| > z_{\alpha/2} \text{SE}_{D}) \approx 0.8
\]
If expected mean difference = 0.30, SD of per-type difference maybe 0.35, using paired t across types requires n_types=12 for power 80% (assuming α=0.05, d=0.86). Need calculate. But if SD high, maybe 15.

Need maybe compute via simulation from binomial. Could state: "Con k=8 casos por tipo y 12 tipos, tienes 96 pruebas; una ventaja de 0,25 en recall por tipo con sd 0,20 da poder >80%". Need be plausible. Let's compute rough.

Use two-level: per-type difference \(D_j = rA_j - rAdv_j\). Each recall is binomial with k=8. Under null p=0.5 for both maybe difference mean 0, variance per type = p(1-p)/k + p(1-p)/k = 0.5*0.5/8 + 0.5*0.5/8 = 0.0625? Wait each recall sample from binom with p=0.5, SE=sqrt(0.25/8)=0.1768, variance 0.03125. Difference variance 0.0625, SD=0.25. Mean across 12 types SE = 0.25/√12 = 0.072. For power 80% at α=0.05 two-sided, need mean difference > 1.96*0.072 = 0.141? Actually under null mean 0, to detect mean 0.14 with SE 0.072 gives z = 0.14/0.072=1.94, power ~50%. For 80%, need mean = (z_1-α/2 + z_0.8)*SE = (1.96+0.84)*0.072=0.20. But this assumes p=0.5; worst-case p=0.5. If expected difference larger, e.g., 0.30, power 88%. So 12 types, 8 cases per type gives acceptable for difference >=0.25-0.30. If we expect adversary falls to 0.1 and agent 0.7, difference .6. But if conservative, maybe 15 types x 8.

Need also consider clustering by type and author. If all B types from one author, random effects. Could propose:
- Minimum: 12 B types, 6 cases per type = 72 positive plus 24 clean cases.
- Better: 15 B types, 8 cases per type = 120 positive plus 30 clean.
- But given lab cost, maybe "10 types, 5 cases each plus 20 clean" is borderline; F12 failure due to one case per operator. Need say one case per type is the original sin; do not repeat. At least 5 cases per type, ideally 8/10.
- Need justify 18? Hmm.

Need maybe specify two endpoints:
- Primary: **mean type-level recall advantage** of agent over frozen adversary at FPR=0.05 on clean B, with a one-sided paired t-test across types, α=0.05. Pre-register non-inferiority margin? Actually we want superiority. Might use Wilcoxon signed-rank if D not normal.
- Secondary: **per-type McNemar or exact binomial** and **coverage** (proportion of types with at least one true positive).
- Mandatory breakdown: per-type heatmap/table with 2x2 and confidence intervals, clean cases count, invalid/no-cases count, and B taxonomy.

Need diagnose "aggregation trap". Need mention "no uses media macro global sin intervalos; si das media, incluye mediana, IQR, y per-type plot."

Need perhaps stop and say if question not answerable. Is it? We can say "La pregunta es contestable en su forma condicional si se garantizan dos cosas: (1) B es independiente de A en generación y (2) el endpoint primario es a nivel de tipo. Si no, no." Perhaps mention "no será contestable si B vuelve a ser catálogo cerrado; el diseño aún no lo impide."

Need think of "strong adversary" type. If adversary frozen against A but we also update on B, that measures whether rules with adaptation beat model. We need address 5.3:
- Freezing is honest for measuring "what the model adds without rule maintenance." That's exactly the operational contrast: a static rule system vs model. But it's not fair if you want to show model can beat rules even when rules are maintained. Both have value.
- "Congelado" represents no-rule-update scenario; "actualizado" represents the realistic engineering response. If actualizado beats model on B, then model may still add value in latency/coverage of unknown before rules are written, but not in final capability. Pre-register both as two pre-specified comparisons:
   - \(H_1\): model > frozen rules on B (novelty without retraining).
   - \(H_2\): model non-inferior or superior to updated rules on B (incremental value after maintenance).
- Updated adversary must be built by an engineer who sees B but not the agent's outputs? Might be impossible because they need detect. They should see same B cases and clean labels, perhaps not agent's errors? They can build rules. But if they see agent results, they could overfit. Need blind them to agent predictions on final B. Could build updated adversary after all systems run but before unblinding. Need pre-register rule writing process and time/cap limit to avoid unfair advantage.
- Meaning: if frozen adversary sinks and model holds → value appears until rules updated; if updated adversary holds or wins → rules can be updated quickly, and model's advantage is only temporary; if both sink → need better model or more task-specific training. If updated adversary beats model, maybe rules still dominate.

Need perhaps include issue: a "strong adversary" already sees catalog A? They said frozen against A. Could also update to B after. Need perhaps define "frozen adversary" as "all rule patterns and thresholds fixed; no per-B thresholds." If it uses a threshold calibrated on A, it may output weird on B. Need include clean.

Need maybe mention "the regex adversary in F12 was not just rules; it likely had thresholds and patterns tuned to A. Freezing means no new patterns, but thresholds maybe invalid due to distribution shift. To avoid a strawman, recalibrate global threshold on A clean only, then freeze everything." That is important. If threshold is not adjusted for B, false positives may explode/sink. Use same threshold as A; report.

Need maybe discuss "author blind but sees transformation contract". The transformation contract may make some failure types obvious. Need define an external "red list" of known mechanical signatures? Hmm.

Need maybe propose first-week measurements:
- Build a "signature inventory" from A: automatically extract tokens/structures used by adversarial rules? Run a B probe with frozen adversary on a small non-final B_pilot. If frozen adversary already achieves >20% recall at FPR=0 on B_pilot, stop; B is not independent enough. Need be careful: not using final B.
- Evaluate scorer on B_pilot: inter-rater reliability between scorer and human label; percentage where ground truth unambiguous.
- Check model's "zero-shot" baseline: if model on B_pilot detects all, maybe B too easy or model already generalizes; but that's outcome? Hmm not necessarily a failure, but if both high then no difference. Need know can still show equivalence? If model and adversary both high, you learn B not discriminative. If both low, maybe B too hard or scoring wrong.
- Compute **leakage metrics**: representation overlap between B types and A catalog using rule feature set; if B type signatures overlap with known A rules, flag.
- Run an "oracle" based on raw HL7 tokens to estimate maximum mechanical detectability. If high, B is mechanical.

Need maybe answer in Spanish, with headings. Need be concrete and may be somewhat lengthy but not too much. Desired oververbosity 5. Need likely 2000-3000 words? The prompt asks "sin relleno", concrete. Need maybe produce around 2500 words. We can include tables and formulas.

Need parse user says "Cuando el encargo contiene un error de razonamiento, lo dices antes que nada." We must state if error at beginning. Is there an error? Maybe I should say upfront: "Hay un supuesto no defendible: suponer que B—por ser encargado a un autor ciego—es intrínsecamente no-mecánico. No lo es; lo único que cambia es quién conoce las reglas, no si las firmas son detectables." That could be the opening.

Need maybe mention "La Fase 13 puede fracasar por el mismo defecto de raíz: B seguirá siendo un catálogo de mutaciones declarativas, sólo que más pequeño y ciego." This is key.

Let's structure final:

```
# Fase 13: crítica de diseño y condiciones de validez

**Antes de nada:** el error ... no es que falte bloquear el catálogo A; es que el diseño de B repite la estructura de catálogo de mutación. Un tipo nuevo puede tener firma mecánica aunque el autor no conozca A. Por tanto, no basta con que el autor sea ciego.

## 1. La pregunta
...
```

Need maybe state in 1: "La pregunta es correcta como dirección, pero mal planteada si se formula como propiedad del modelo sola. Reformular." Then give precise question:
> "¿El agente congelado supera al adversario de reglas congelado en recall por tipo nuevo, sin pagar más falsos positivos en limpias, cuando los tipos B se generan desde una taxonomía de fallo independiente y no por reutilización de A?"

Maybe say this is contestable only with independent B and type-level endpoint.

Need maybe define "tipo no visto" operationally:
- Un tipo B es nuevo si no se puede obtener del conjunto A mediante renombrado, cambio de parámetros, o combinación trivial; la clasificación debe ser pre-registrada por un juez independiente.
- La novedad no es una propiedad binaria; mídela como distancia de firma.

Need "criticar: ¿hay una mejor que el montaje ya permite?" Maybe propose using real failures as primary, because they are truly independently generated. They admitted contamination: lab author knows them. But if real failures are from incidents, they offer better construct validity. But the author knows them and that contaminates. Could solve by having a second author not involved in agent/adversary collect/redact failures into B, and lab author not do it. But maybe they only have few. The best question might be a **two-arm generalization**: 
1. B_synthetic blind (for controlled novelty)
2. B_real incident (for external validity)
But real stratum has contamination. If you can blind the lab author from final labels? Hmm.

Need answer 5.2 in detail with table maybe:

| Riesgo fatal | Cómo se destapa barato y pronto | Medida preventiva |
| --- | --- | --- |
| B vuelve a ser mecánico | Ejecuta una batería de sondas no final (regex genérica, n-gramas, frozen adversary) sobre un B_pilot; si recall alta sin FP, B es inválido como novedad | Cambia la tarea del autor: narrativa de incidente, no función de mutación |
| Fugas o solapamiento con A | Extrae firmas de A (tokens, posiciones, reglas) y compara con B_pilot; solapamiento alto => invalid | Taxonomía independiente |
| Scorer no mide B | Acuerdo humano-scorer en B_pilot | Participación de un juez clínico/HL7 externo |
| B contiene casos irresolubles/ambiguos | Pre-registrar criterios de inclusión, pilot | Juez de adjudicación antes de evaluación |
| Un solo caso por tipo | No se destapa; es diseño | Mínimo 5-8 casos por tipo |
| Agregación | No se destapa; es análisis | Endpoint por tipo pre-registrado |

Need maybe explain "batería de sondas" not contaminating because on B_pilot (separate non-final from final B). But perhaps after B_pilot, if invalid, discard whole B and generate new? Need mention selection effect: "No se puede usar B_pilot como final si se decide en función de las sondas. Destina un pool de pre-B exclusivamente para validación de instrumentos; el B final se congela antes de abrir las salidas primarias."

Need maybe answer "¿cómo se resuelve sin contaminar el encargo?" Elaborate:
- Change task from mutation function to "incident report" in operational terms. The implementer engineering can be blind to adversarial rules but also not told to avoid "mechanically obvious". The important part: author's goal is not to create failures that fool detection; it's to reproduce real conditions. "No les digas ni la palabra 'detector' ni 'modelo'."
- If you need mutation function, have them base each type on a "field failure hypothesis" documented before seeing the circuit's log/HL7? Wait they see circuit and contract. Could see the contract but not trace tools. That may reduce mechanical signatures? Maybe.
- Use a multi-author panel: one writes narrative; another implements; third validates novelty. The first two do not see agent/adversary.
- After generation, run **structural novelty check** using features from A, but this check is executed by a separate statistician; if a type is too similar, it's excluded by pre-registered threshold, not by telling author to make it harder.

Need perhaps talk about "mecanicamente obvios" not binary. Define "firma mecánica" as features recoverable by linear rules from raw HL7/log tokens. The probe might be a "maximal mechanical baseline" but if the frozen adversary already has features, it's a strong probe.

Need on 5.3 adversarial frozen:
Could include:

| Comparación | Pregunta | Interpretación |
| --- | --- | --- |
| Agente congelado vs adversario congelado | ¿El modelo captura lo no reglado? | Si gana, no es solo reconocimiento de firmas A. |
| Agente congelado vs adversario actualizado contra B | ¿El modelo aguanta cuando las reglas reciben mantenimiento? | Si gana, valor robusto; si pierde, valor transitorio. |

Need mention "actualizado" must be artifact-only, same information as agent? Does adversary updater see B data labels? They need write rules to detect failures. They should have same access to B training/calibration cases (if using some) but not final test. Need maybe split B into adapt and test? If updated adversary sees full final B, overfitting. Need propose B split: B_dev for rule updater and agent? Agent frozen no need adapt. But rules updater uses B_dev to write B rules; final evaluation on B_test. That is important. If only one B set used to compare updated, updated rules overfit. Could have two subsets: B_adapt (not used for primary) and B_test. But then B_test numbers lower. Need maybe state "updated rules should be built on a B_adapt split; frozen rules and agent are then evaluated on B_test. If B is small, make this secondary." This is crucial.

Need perhaps answer: "Congelarlo es honesto si lo defines como escenario de 'sin mantenimiento'." But no, also need measure updated. We can advise.

Need compute sample size more carefully. Maybe create a table:

| Escenario | N tipos | k casos por tipo | Positivos B | Limpias B |
|---|---|---|---|---|
| Mínimo | 10 | 5 | 50 | 20 |
| Recomendado | 15 | 8 | 120 | 30 |
| Poder para detectar Delta media=0.30, sd=0.35 | 80% | - | - | - |

Need maybe justify with formula. Let's compute a more accurate sample size. Use paired per-type differences. We can say: "Con k=8 casos por tipo, la diferencia por tipo tiene desviación típica ≤ 0,25 si la sensibilidad base está en torno a 0,5; con 15 tipos, una ventaja media de 0,25 da z ≈ 0,25/(0,25/√15)=3,87, poder alto." Wait compute: SE = 0.25/√15=0.0645; z=3.87. That's for in-sample; need maybe adjust for between-type variation. If SD of true per-type differences is maybe 0.30, then SE across types = sqrt(0.30^2/15 + within variance/n?) hmm.

Better use simple formula:
\[
N_{\text{types}} = \frac{(z_{1-\alpha/2}+z_{1-\beta})^2 \times (\sigma_D^2 + 2 p(1-p)/k)}{\delta^2}
\]
Where \(\sigma_D^2\) is between-type variance of true differences. If \(\sigma_D=0.20\), \(p=0.5\), \(k=8\), \(\delta=0.25\), then \(\sigma_D^2 + 2p(1-p)/k = 0.04 + 0.0625=0.1025\). For α=0.05, β=0.20, numerator (1.96+0.84)^2=7.84; times 0.1025 /0.0625 = 12.86. So 13 types. If k=5 then within variance = 0.1, total 0.14, N = 17.5 -> 18 types. So 15 types x8 is reasonable. Need mention if you want to detect delta=0.25. If smallest meaningful effect is 0.15, need much larger sample: N = 7.84*(0.04+0.0625)/(0.0225)=35.7 -> 36 types. So choose minimum detectable effect (MDE) of 0.25 or 0.30.

But maybe unit is per-case not per-type. Could use mixed logistic regression with random intercept for type to gain power across cases. That would require around 100 positives total for odds ratio 2.5? Let's consider logistic with random effect: need simulation. But we can keep simpler per-type.

Need maybe address "F12 unit was macro per operator, one case per operator." Need say "one case per type is underpowered to estimate per-type recall; you cannot distinguish 0/1 from chance. Need at least 5; 8 is safer."

Need 5.6 real failure stratum:
- Yes worth it as an external validation, but do not make it primary. Use it as a pre-registered secondary "generalización a incidentes reales" with caveat: author contamination, small n, cannot establish independence. Report separate from primary B.
- To avoid contamination affecting conclusion:
  - Do not combine B and real failures in primary.
  - Report real failures as "exploratorio" due to possible overfitting by author.
  - If real failure set includes only 8-10 cases, report case-by-case, not aggregate metrics.
  - Have a third party redact or at least re-create the failures from lab notes? If the lab author knows them, that is exactly contamination; if you can, have someone independent reproduce or document them before seeing agent/adversary. If not, label them as non-clean.
- Could even exclude real failures from primary and use them as a "tie-breaker" or qualitative.

Need maybe first-week measurements (section 7):
List concrete:
1. Build B_pilot (3-5 provisional types from same author, never included final) and run:
   - Frozen adversary A.
   - Generic regex/random forest baseline.
   - Agent.
   - Human/scorer agreement.
2. Compute novelty metrics:
   - Feature overlap between B_pilot and A rules (e.g., Jaccard on tokens/rule triggers).
   - Detectability by "blind" rule set; if frozen adversary recall > 0.2 at zero false positives, or if random forest AUC > 0.9, stop and rework.
3. Check ground truth:
   - Percentage of cases where scorer labels exactly match independent human; target >90%.
4. Run sample-size simulation based on pilot variance to confirm target N.
5. Pre-register decision rules and primary endpoint before final B is generated.

Need maybe mention "No uses el B_pilot en el análisis final ni para ajustar reglas del adversario actualizado."

Need perhaps include a "checklist de validez" at end.

Potential additional fatal flaw: the question "generalize to types no one has written rule" may be undermined by qwen's training on public code; it may have seen similar failures. But for local agent, maybe no. We can mention: "No podemos garantizar que el modelo no haya visto fallos parecidos durante el pretraining. Fase 13 mide generalización de laboratorio, no de mundo. No lo vendas como 'generaliza a fallos no vistos por nadie', sino 'no vistos por el autor de reglas'." That is important. The question says "nadie ha escrito una regla". But qwen may have internal patterns. But "nadie" is false for the model? If model is pretrained on internet, maybe has seen HL7 error patterns. But "rule" specifically maybe not. Need nuance:
- The model's parameters may encode many failure patterns from training; compared to rules, this is still generalization to types not in A, but not "zero-shot".
- Therefore phrase endpoint as "fallos no incluidos en el desarrollo de A ni en las reglas del adversario", no "inmutados nadie".

Need maybe mention "El modelo y el adversario no están en igualdad de condiciones si el adversario está congelado y el modelo también; but the model is stochastic etc."

Need maybe think of "construct validity of B types" further. A new type can be just another category with its own mechanical signature. The frozen regex could fail if it has no matching rule. That is exactly "sink". But if it writes generic rules for some patterns, it might still detect. Need perhaps say "the outcome `adversary sinks and model holds` only demonstrates generalization if B types are not simply perturbed versions of A. That requires an independent panel to certify that B types were not generated from A. Otherwise same as F12."

Potential flaw: The author of B sees the circuit and contract, not A. But seeing transformation contract may be enough to enumerate all possible failures; there may be a finite set of fields and mutations. The adversary may also have generic rules (e.g., "missing required field") that cover B. In that case the adversary "aguanta" and conclusion "rules generalizan" may be overstated because B was generated from a set of generic rules implicitly. Need maybe require B types to be generated from a "failure mode taxonomy" not reducible to contract alone. That is hard.

Need maybe mention "use real incidents to anchor taxonomy." If possible, derive B types from external incident reports (e.g., HL7 FHIR integration failures in public repos/fora) and have blind author adapt them. That might produce non-mechanical types. But need no catalog leak.

Need maybe propose alternate design: Instead of trying to create B synthetically, use a **sequential holdout from real-world failures** collected over time. But time.

Need maybe address "No pidas el catálogo de mutaciones..." We won't.

Let's maybe draft final in Spanish.

Start:

```
**Primero lo de fondo:** El diseño propuesto corrige el conocimiento del catálogo, pero no corrige la estructura que mató la Fase 12: B sigue siendo un catálogo cerrado de mutaciones declarativas encargado a un autor. El punto no es quién conoce las firmas; es que una mutación nueva puede ser tan mecánicamente obvia como las de A. Por tanto, la Fase 13 puede repetir el fracaso si B se construye con el mismo formato.
```

Then:

```
## 1. La pregunta
Es la dirección correcta, pero con reformulación...
```

Need ensure all requested sections. Let's outline:

```
## 1. La pregunta: ¿es la correcta?
- Correcta como contraste de generalización no como propiedad absoluta.
- Reformulación operativa:
  ...
- Condiciones: B no derivado de A, endpoint por tipo.
- Limitación: modelo no es cero-shot; solo "no visto por el autor de reglas".
```

```
## 2. Cómo fracasaría la Fase 13 y medidas baratas
- Tabla con 5/6 fallos.
- Falla principal: B ciego no impide firma mecánica; cómo resolver sin contaminar:
   - cambiar tarea a narrativa
   - sonda estructural en B_pilot
   - juez externo
- Medida barata: en semana 1 B_pilot provisional; correr frozen adversary + random forest + n-gram; if recall >? stop. Compute overlap with A.
```

Need perhaps provide threshold: "si el adversario congelado o un Random Forest de n-gramas de HL7/log obtiene AUC > 0,80 o recall > 0,3 con FPR=0 en B_pilot, considero B inválido como 'no visto'." Need be precise: If frozen adversary has high recall, that's a sign B is not new. But if opponent rules genuinely generalize, that's a valid outcome. The probe before final must not be used as final; and if high, you can still run final and report "rules generalize" but then not answer model value? Hmm If pilot shows frozen adversary high, then final likely also high; maybe you still learn "rules generalize" to this B but not about model. Could be publishable but maybe not the intended question. The user's design says three outcomes not bad. So if adversary holds, it's publishable. But they want avoid "adversary gains due to mechanical obviousness". The pilot should classify mechanical obviousness to ensure the outcome is not just because B was trivial. If frozen adversary is high because rules generalizing to genuinely new types, that's different. How differentiate "mechanical obviousness" from "rule generalization"? It's tricky. Maybe we need define "mechanicity" independent of frozen adversary: use generic baseline not specific to A, e.g., a rule set derived from HL7/FHIR standard (not from A) or random forest. If even generic baselines achieve high, types are trivial; if only frozen adversary achieves high but generic baselines fail, that may be valid rule generalization. Need use multiple probes:
  - **Probe genérico**: random forest/ngrams on raw text, not trained on A.
  - **Probe A**: frozen adversary.
  - **Probe de contrato**: a small set of obvious contract rules (required fields, code sets).
If generic or contract probe detects B types, then B is mechanically obvious and not testing model generalization. If only A detects, maybe actual rule generalization. But if both A and generic high, still uninformative. Need maybe set thresholds.

Could propose cheap measure:
> "Genera un B_pilot de 3-5 tipos. Haz que un ingeniero no ciego a A extraiga 10 reglas genéricas del contrato FHIR/HL7 (campos obligatorios, códigos, cardinalidades, escapes) sin ver B. Si esas reglas detectan >20% de casos de B_pilot, los 'fallos nuevos' no son más que re-escrituras del contrato; rehaz B."
This avoids asking author to avoid mechanical; you evaluate after.

Need maybe mention "No filtres al autor; en su lugar filtra el conjunto B mediante criterios estructurales pre-registrados."

Need maybe discuss "fallos semánticos": The challenge is to create failures that are not field-level syntactic mutations. E.g., "wrong patient resource due to identifier duplication", "ACCEPT with no persist", "resource with mismatched MRN and medicare number". These require semantic reasoning. The author should write at this level.

Need perhaps answer 5.3 in section 3:

```
## 3. El adversario congelado
...
```

Need mention: "Actualizado contra B" must be built on B_adapt separate from B_test. Freeze agent and frozen adversary before B_test. There are three comparisons maybe:
1) M vs AdvA on B_test (principal).
2) M vs AdvB_adapt on B_test (secondary). AdvB_adapt trained/rule-written on B_adapt; same threshold calibrated on B_adapt clean.
3) M vs AdvA+AdvB_adapt (combined) maybe.
Interpretations.

Need maybe warn: "No uses el resultado de AdvB_adapt en B_test si el autor de reglas ha visto B_test. Eso sería tan tramposo como F12." This is important.

Need 5.4 endpoint:

```
## 4. Endpoint y desglose obligatorio
Primary: \Delta_j = sens_M(j) - sens_A(j) at FPR≤0.05 on clean B, per type j.
Global: mean \Delta_j; pre-register δ (e.g., 0.15) and α.
No total unweighted across all cases.
Mandatory table:
- type, family, n cases, TP/FN/FP/TN, sensitivity, exact binomial CI, \Delta_j, per-type p-value.
- global: mean, median, IQR, one-sided CI.
- clean false positives count per system.
- invalid/errors count.
```

Need maybe state "If false positive rate >0 on clean B, compare at matched FPR, not raw recall."

Need maybe define "no agregar AUC global" if class imbalance.

Need maybe mention "primary endpoint is type-level sensitivity difference, not total F1, not accuracy, not macro AUC without per-type."

Need 5.5 size/power:

```
## 5. Tamaño y potencia
- Avoid one case per type. Minimum 5, recommended 8 cases per type.
- B positive cases: 12-15 types x 8 cases = 96-120 positive.
- Clean B: 2-3 per type? Actually clean cases not per type; use 20-30 clean.
- Formula:
  N_types ≈ ...
- Give examples:
   - delta=0.25, sd=0.20, k=8 -> N=13 (power 80%).
   - delta=0.15 -> N≈36 -> not feasible.
   So pre-register MDE=0.25 or 0.30; don't claim smaller.
- Use exact binomial CIs; if k=8, lower bound large.
```

Need maybe include "per-type positives" also need cases per type >1; if some types have no detection by either, variance bigger. For rare failures, maybe require 8 cases to estimate 70% sensitivity. If model expected threshold 0.7 with 8, CI ~[0.35,0.93]; wide but still difference. Need mention.

Need maybe suggest "Use a mixed-effects logistic regression as secondary to borrow strength across types but require random intercept; if n_types small, random effects unstable."

Need maybe address "set B not one case per operator" strongly.

Need 5.6 real failure:

```
## 6. Estrato de fallos reales
- Yes, as secondary, not primary.
- Contamination admitted: lab author may have tuned the system to these or vice versa; cannot claim independent.
- Report separately as "incidentes históricos, no ciegos; evidencia cualitativa".
- If possible, have a neutral third party re-create them from incident notes before evaluating; or use only after primary B.
- Do not pool them with B.
```

Need perhaps answer if "mejor dejarlo fuera?" We can say "No lo excluyas del todo: es la única validación externa y cuesta poco; pero no lo conviertas en endpoint primario." Maybe due to contamination. If methodological strict, could leave out. Need maybe provide criterion: "Si solo quieres saber si el modelo aporta, B ciego responde; los reales contaminados no suman evidencia primaria. Si quieres tener un dato de cara a operación, reportalos como descriptivos."

Need section 7 first-week:
List with items.

Could also include a final "Preinscripción" maybe:
- Register: primary endpoint, MDE, inclusion/exclusion criteria for B types, probe thresholds, analysis scripts.
- Have an external review before opening B.

Need maybe include a note "No pidas al autor B que escriba 'nuevos fallos imposibles de detectar'; pide incidentes."

Let's think if there is any error in user's reasoning to mention upfront. The design says "El adversario fuerte va primero. Ya existe." But if the adversary is frozen against A and used to compare, it's already built. The flaw is that B may be constructed by one author who knows transformation contract, not A. The user themselves recognizes one flaw. We can reinforce: "No es solo un riesgo, es el defecto estructural no corregido." This is crucial.

Could mention "La Fase 13 no puede demostrar `nadie ha escrito una regla` porque las reglas del adversario no son el límite de la detectabilidad mecánica. Cualquier B puede tener firma mecánica aunque nadie haya escrito esa regla específica." This is maybe a deeper point. The question asks "tipos de fallo para los que nadie ha escrito una regla" but the hypothesis is model vs rules. If B types are mechanically obvious but not in A, a rule system could be updated easily; but that's a separate comparison. Need maybe say "lo que mide con adversario congelado es si reglas viejas generalizan, no si 'nadie' podria escribir regla." But the updated adversary comparison addresses this.

Potential issue: "el autor ciego puede escribir tipos que resulten igual de mecánicamente obvios" resolving: we can define "mechanically obvious" as captured by **generic rules** not specific to A. But if they are obvious to a generic baseline, then not testing high-level generalization. We need not tell author; instead measure it. Good.

Let's maybe formulate a "taxonomía de B" criterion: B types must be selected to cover:
- Nivel 1: sintáctico (malformed HL7) — likely mechanical; exclude or low weight.
- Nivel 2: contractual (schema violation) — still mechanical.
- Nivel 3: semántico (valid syntax and schema, wrong content) — relevant.
- Nivel 4: de proceso (ack sent but entity not persisted) — requires logs/state.
A blind author will gravitate to Nivel 1/2 because easier. Need explicit instruction with examples but not "mechanical" word: ask for incidents from operational clinics, prioritizing those where HL7 and FHIR both "look normal" at least partly. That biases away from mechanical without using detection language. Good.

Need maybe include "No uses B generated from mutator functions that just delete/replace/swap fields; require a causal mechanism." That's an instruction that may filter but not tell answer. It's okay because it's about realism.

Need maybe mention "one author sees circuit and contract but not adversary/catalog A. However, if they see the circuit, they may notice the same vulnerabilities as A. That's unavoidable. But ensure they don't see any A generated traces or logs." Already.

Need maybe think about "no pidas el catálogo de mutaciones..." The user says "Contaminación. No pidas el catálogo de mutaciones, la clave ni las mediciones caso a caso. Si crees que necesitas alguno, dilo en vez de suponerlo." We don't need. We can perhaps say "No necesito las claves ni mediciones para esta crítica; necesitaría la taxonomía de B para validar novedad." But maybe not necessary.

Need maybe maybe propose "el montaje ya permite" better question: "¿Cuánto mantenimiento de reglas hace falta para igualar al modelo?" That might be more decision-relevant than "generalize to unseen." Actually in 5.1, they ask if better question. Could say: 
> "Para Fase 13, mide dos preguntas: (i) con adversario congelado: generalización sin mantenimiento; (ii) con adversario actualizado: valor incremental tras mantenimiento. La que decide operación no es solo (i), sino (ii), porque si un ingeniero escribe reglas en 4 horas y iguala al modelo, el modelo no se justifica. La combinación es más fuerte."
But their question about model aporta vs rules: if rules updated can handle B, the model maybe still worth for unknown until updated. Need maybe mention.

Would a better question be: "¿Es el coste de actualizar reglas para B mayor que el coste de mantener el modelo?" Not measurable with one lab. So no.

Need maybe maybe answer: "La pregunta correcta no es si generaliza en abstracto, sino si su ventaja se sostiene frente a dos adversarios: el congelado y el actualizado. La Fase 13 debe preinscribir ambas comparaciones." That is a good critical point.

Let's now think through sample size more.

Could define in endpoint:
- For each B type \(t\) with \(k_t\) positive cases, \(S_M(t)\) and \(S_R(t)\) are case-level sensitivities.
- \(D_t = S_M(t) - S_R(t)\).
- Primary analysis: paired t-test of \(D_t\) across types; but with \(D_t\) proportions, non-normal. Use Wilcoxon signed-rank as primary, or a permutation test. Pre-register. For sample size, use simulation.

Need maybe specify a minimum per-type cases due to exact binomial: if k=8, sensitivity point estimate can take values 0, .125, .25, .375, ..., 1. The difference is discrete. With 12-15 types, paired t on discrete differences might be okay; permutation better. Could say use a permutation test of the null that system labels are exchangeable within case? But there is pairing per case; use exact McNemar stratified by type? Hmm.

Maybe define primary as type-level mean difference, use Wilcoxon signed rank on \(D_t\). That's robust. Power simulation based on expected distribution of \(D_t\).

Need perhaps not overcomplicate.

Potential confounding: the agent and adversary may have different outputs. The adversary (regex) maybe outputs binary detection per case; agent JSON verdict maybe includes classification. Need ensure scoring same.

Need maybe mention "the adversary froze but may not be probabilistic; if its output is binary, no threshold. Then compare binary sensitivity. If agent has probability, threshold set to achieve FPR=0 on A clean; freeze that threshold." The user may already have scorer. Need maybe include.

Need maybe include a "pre-flight checklist" in section 7:
- [ ] B_pilot generated, probes run.
- [ ] Scorer human agreement > 0.9 kappa.
- [ ] Inclusion criteria for B types pre-registered.
- [ ] Primary endpoint and MDE pre-registered.
- [ ] Analysis script passes simulation on pilot data.
- [ ] B_test frozen before adversary update.

Could provide.

Let's also maybe mention "avoid the same author for multiple B types if possible, or block by author in analysis." If one author generates all B types, if they have a style, that's a confound. Better: two or three authors produce types independently; final B includes equal number from each; report author as covariate. That might be overkill. But maybe useful.

Need maybe think about "catálogo cerrado" in B: the author will deliver a catalog entry and mutation function per type. If author writes all B from their own catalog, it's closed. The size N small; still closed. The issue is that the frozen adversary may see some. Could not have full open-ended distribution. Need acknowledge.

Maybe suggest "B should be sampled from a larger pool of candidate types, not the full set; then evaluate on all? But if sample chosen from larger pool, maybe." Actually if you generate 20 candidate B types and then randomly sample 12 for final, that prevents selecting easy/hard after seeing results. But the final set is still closed. The pilot probe could be run on the non-selected 8 candidates, while final 12 are untouched. This is a good idea:
- Author generates 20 types. Randomly split into B_probe (8) and B_final (12) before any detection. Use B_probe to validate novelty/mechanicity and scorer. If B_probe fails, regenerate entire pool. B_final is then clean. This solves selection effect. Nice.

Need include maybe as cheap measure.

Need perhaps mention "if B_final fails due to random split with easy types, that's okay; pre-register no redrawing after results."

Need maybe talk about real failures and contamination: "No uses el autor del laboratorio para crear el estrato real; si no hay alternativa, no lo consideres primario." Good.

Let's now maybe outline final thoroughly.

Potential final text:

```
**Primero, lo de fondo:** La Fase 13 corrige el conocimiento, no la estructura. B seguirá siendo un catálogo cerrado de mutaciones; el autor ciego no impide que una mutación nueva tenga firma mecánica. Si no se cambia la generación y se añade una sonda de novedad, la fase puede volver a nacer muerta.

## 1. La pregunta
...
**Reformulación (preinscribible)**:
> Congelados agente y adversario-A, y sobre un B generado de forma independiente de A, ¿el agente obtiene una sensibilidad por tipo superior al adversario-A sin aumentar los falsos positivos, y se sostiene frente a un adversario-B actualizado?

**No es pura "generalización a no visto"; es generalización a no visto por el sistema de reglas.** El modelo puede haber visto patrones en pretraining.

...
```

Need maybe in 2:
```
## 2. Cómo fracasaría y medidas baratas

**Fallo estructural 1: B mecánico sin intención.**
...
Medida: B_probe/B_final split; run probes...
```

Maybe a table:

| # | Falla | Detección barata | Corrección |
|---|---|---|---|
| 1 | B sigue siendo catálogo declarativo | Probar en B_pilot un Random Forest de n-gramas y 10 reglas de contrato; si AUC>0.80 o recall>0.30 a FPR=0, B no discrimina | Cambiar la tarea a incidentes; priorizar fallos semánticos/proceso |
| 2 | B contiene firmas de A | Calcular solapamiento de tokens/reglas A vs B; > Jaccard? | Excluir/rehacer |
| 3 | Scorer no válido para B | Evaluar acuerdo humano-scorer | Criterios de inclusión adjudicados |
| 4 | Evaluar actualizado sobre B_test | No se destapa; diseño | B_adapt/B_test split |
| 5 | Agregación | No se destapa; análisis | Endpoint por tipo |
| 6 | Un caso por tipo | No se destapa; poder | 5-8 casos/tipo |

Could be okay.

Need maybe say "no le pidas 'que no sean mecánicos'; pide incidentes y luego deja que una sonda estructural decida."

Need maybe 3:
```
## 3. Adversario congelado
...
```
Could include "Un adversario actualizado contra B solo es válido si el autor de reglas no ve B_test. Reparte B en B_adapt (4 tipos) y B_test (10-12 tipos). El adversario-B se escribe sobre B_adapt, no sobre B_test. Evalúa ambos en B_test."

Need maybe decide numbers: If need 15 B types for final, plus B_adapt maybe 5 types for update. Total B generated 20 types. That aligns with 20 candidate split. But B_adapt uses additional types not in primary. Could be okay. Need maybe mention cost.

Need maybe perhaps say "If B_total=20 types, split 8 for B_probe (validation) and 12 for final B_test. If you need B_adapt for updated adversary, allocate separate 4 types maybe, making 24. But that may be too many. Or use the same B_probe? No, that would be used for selection, cannot be final. Could use B_adapt drawn from calibration. Need maybe propose total B generation 18-20: 4 B_adapt for updated adversary, 6 B_pilot for structural probes, 10-12 B_test for primary. This is complicated but concrete.

Maybe maybe structure:
- Generate 20 B types and split: 4 B_adapt (for rule updater), 4 B_pilot (for instrument validation), 12 B_test (primary). But if you only have 12 B_test x8 cases = 96 positive, enough. Need clean cases maybe 24.

The user may prefer simpler: just freeze adversary and maybe secondary update; could say "Actualizado es deseable pero requiere B_adapt. Si no hay recursos, no lo hagas; no uses el B_test para actualizar." That's important.

Need maybe mention "La comparación principal congelado responde a la pregunta original. El actualizado responde a otra pregunta y requiere más muestra. No la mezcles."

Need perhaps use formulas:
\[
D_j = R_{\text{agente},j} - R_{\text{advA},j}
\]
\[
H_0: \mathbb{E}[D_j] \le 0,\quad H_1: \mathbb{E}[D_j] > \delta
\]
Need maybe mention one-sided? If difference can be two-sided? We want show agent better. Could use one-sided? The user describes three outcomes "adversary sinks and model holds"; but if model worse than adversary that's maybe not expected. Could still use two-sided to detect any difference. But main hypothesis is superiority. Pre-register a superiority margin \(\delta=0.10\) or \(0.15\). Use one-sided α=0.05. But with one-sided, if adversary better would not reject; but still report.

Need maybe "No definas 'se hunde' como 0/0; define hundirse como sensibilidad < 0.3 y/o diferencia ≥ 0.25 a favor del agente." Good.

Need maybe 6:
```
## 6. Fallos reales
```

Need maybe 7:
```
## 7. Primera semana
- Generate B_probe; run probes; scorer agreement; novelty metrics; sample-size simulation.
- Pre-register after first week? Need careful: If pre-register after seeing pilot, maybe okay if pilot not final. But should pre-register primary endpoint before any B_final results. Could say "Al final de la semana 1, congela B_test y preinscribe el análisis; la sonda piloto no entra en el análisis."
```

Need maybe final phrase.

Let's now generate final in proper Markdown. Need be concise but with enough detail. Avoid excessive filler. Use Spanish.

Let's write final.

We need maybe not mention "encargo" error at start maybe okay.

Potential final text:

---

**Primero, el defecto de raíz que veo:** La propuesta no corrige el fallo de construcción; solo lo desplaza. F12 fracasó porque el corpus era un catálogo cerrado de mutaciones declarativas. B, aunque ciego, sigue siéndolo. El autor ciego no garantiza no-mecanicidad; solo garantiza que no conoce las reglas A. Por tanto, el riesgo principal no es "el autor ciego puede escribir tipos obvios"; es que el diseño lo permite estructuralmente.

Then sections.

Need maybe ensure section 5.2 includes "qué medida barata destaparía al principio": I'll include a subsection "Las medidas baratas" with maybe bullet list.

Let's produce now. Ensure no disallowed requests for catalog etc. We don't.

Need maybe mention "No pido catálogo; para validar la Fase 13 necesitaría, si acaso, la taxonomía de B y el acuerdo del scorer." Could at end maybe.

Let's formulate elegantly.

Potential formulas for sample size:

```
Para k=8 y p=0.5:
SE(D_j) ≤ sqrt(2p(1-p)/k) = 0.25.
Con 12 tipos: SE(media D) = 0.25/sqrt(12)=0.072.
Efecto mínimo detectable con potencia 80% y α=0.05: δ ≥ (1.96+0.84)*0.072 ≈ 0.20.
```
Wait that's only within-type, no between-type variance. But okay if assume differences independent and no random type variance. Need maybe include "asumiendo varianza entre tipos moderada; si hay varianza, suben los tipos." Maybe maybe:
\[
\delta_{\min} = (z_{1-\alpha/2}+z_{1-\beta})\sqrt{\frac{2p(1-p)}{kN}+\frac{\sigma^2_{\tau}}{N}}
\]
Where N types. If \(\sigma_\tau=0.15\), δ_min maybe ... let's compute for N=15, k=8, p=0.5, \(\sigma_\tau=0.15\):
within variance per type = 0.25/8*2? Wait formula above maybe not exactly. Let's not overdo.

Need maybe maybe in sample section:
"Usa `simstudy`/simulation: simulate per-type detection probabilities with beta distribution; confirm power." That is concrete. But maybe enough.

Let's now write final content.

Need ensure all user's items included:
- 5.1 question.
- 5.2 how fail and measure.
- 5.3 adversary frozen.
- 5.4 endpoint.
- 5.5 size/power.
- 5.6 real failures.
- 5.7 first week.

Let's include headings numbered 1-7 as requested. Use "##".

Need maybe mention "puede ser publicable if adversary holds" but with rules generalization. Might be okay.

Let's maybe include a small "Conclusión" at end. Not necessary but fine.

Let's produce final.

Need consider if there is an inherent issue with "agente local qwen3-coder:30b" - as an LLM, its generalization might be influenced by prompt. The agent sees logs and produces JSON. Not much.

Potential issue: "The adversary is strong and exists." If we freeze, it may be overfit to A; if underperforms on B, maybe because it's brittle, not because rules can't generalize. But an updated adversary comparison addresses. Could mention "If frozen adversary fails, make sure it's not due to thresholds/tuning. Report its clean false positives. Recalibrate threshold on A clean before B." Need add maybe in 5.3/5.4.

Let's maybe include that in 5.3: "Recalibra el adversario congelado en A limpio; no en B. Si no, su mal rendimiento en B puede ser un artefacto de umbral."

Need maybe include "the model's outputs may have stochasticity; sample multiple times or temperature 0." Need maybe mention "fijar temperatura 0/seeds precliminar." Could be a footnote. Not vital.

Need maybe mention "Pre-register handling of invalid/errors cases; if agent cannot parse input, score as non-detection not exclusion." In F12 maybe not.

Potential final answer length about 2000-3000 words. Let's now write final.