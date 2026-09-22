<!-- modelo: deepseek-v4-pro · via: api.deepseek.com · encargo: encargo_diseno13.md · 360 s · 24818 tokens -->

## Veredicto

El diseño está mucho mejor que la Fase 12, pero **tiene un quinto modo de fallo que no está en §5** y que no es menor. Lo llamaría:

> **Estratificación endógena: el eje de mecanicidad que decide dónde se lee el resultado lo estimas con un instrumento propio, no calibrado, y lo puntúas con otro instrumento también propio.**

No es exactamente §5.1 (“todo B es mecánico”) ni §5.2 (“B es A con otros nombres”). Es más profundo: **aunque B sea bueno, el criterio con el que partes B en cuartiles puede fabricar la señal que buscas.** El inductor de mecanicidad y el puntuador son tuyos; el autor de la regla actualizada ve B; el agente no se reentrena. Con esa estructura, hay una asimetría que domina la conclusión:

- El inductor no es un oráculo: es una heurística con error de clasificación desconocido.
- El cuartil “no mecánico” se define *después* de ver B.
- El endpoint se calcula *dentro* de ese cuartil.
- El puntuador, también tuyo, puede reforzar —sin querer— las mismas regularidades que el inductor no ve.

Eso puede producir un falso positivo de capacidad: basta con que el inductor sea flojo justo en los tipos donde el modelo puntúa algo, o con que el autor de la regla actualizada no llegue al techo en B, para que el modelo parezca ganar en “no mecanicidad” sin que haya detectado nada que una regla no pudiera detectar con otro autor u otro espacio de reglas.

### Medida barata de primera semana

Antes de encargar B, dadme:

1. **Un banco de calibración del inductor** con tipos construidos por vosotros donde la mecanicidad es conocida: firmas sintácticas implantadas a propósito frente a fallos semánticos implantados a propósito.  
   El inductor debe separarlos. Si no alcanza sensibilidad/especificidad muy alta a nivel de tipo, no puede ser juez de cuartiles.

2. **Un ejercicio de auto-falsación con A partido**: usad A como pseudo-B y corred el análisis completo DiD+cuartiles. Si el diseño produce una señal positiva donde sabéis que no hay capacidad nueva, el problema es el análisis, no B.

Eso se hace en un día, no en un mes.

---

# 2. ¿Están de verdad incorporadas las correcciones?

## Q1 frente a Q2

**La separación en la tabla es real.** Pero no basta.

Q1 y Q2 comparten B, comparten agente y pueden convivir en el resumen. Si Q1 se preinscribe también, o si se publica al lado de Q2, contamina la lectura. La corrección solo queda real si:

- **Q2 es el único endpoint primario.**
- Q1 se preinscribe como secundario operativo y no entra en la portada ni en el veredicto principal.
- Ningún gráfico comunica Q1 y Q2 como si fueran dos confirmaciones del mismo fenómeno.

Además, hay una asimetría que la separación no arregla: en Q2 la regla actualizada **ve B**, mientras el agente está congelado y no ve B. Eso no es un combate de capacidad simétrica; es:

> **un humano que ve el examen contra un alumno que no lo ve.**

Si lo que quieres medir es si una regla estática *existe*, el comparador correcto no es un humano que la escribe viendo B, es un **inductor automático con espacio de reglas cerrado y búsqueda exhaustiva**. El humano puede quedarse corto; y su insuficiencia se confundirá con capacidad del modelo.

## El oráculo de mecanicidad

No es implementable como oráculo. Es implementable como **heurística con sensibilidad desconocida**.

La frase:

> “el inductor no encuentra regla”

tiene dos lecturas:

1. No existe regla en su espacio de búsqueda.
2. Existe regla, pero mi inductor no la sabe buscar.

Con un solo inductor por diff sintáctico, esas dos cosas son indistinguibles. Por tanto, **no hay evidencia de que el cuartil no mecánico sea no mecánico**. Solo es “no mecánico para este inductor”.

Lo rompe, además, lo siguiente: si tú escribes el inductor después de la Fase 12, ya sabes dónde ganó el agente, ya sabes qué tipos eran mecánicos, ya conoces el catálogo A. Aunque en runtime no le enseñes el catálogo, **el inductor no es ciego en su diseño**.

Para que sea defendible, necesitarías:

- Un espacio de reglas formalizado, no “diff sintáctico”.
- Búsqueda exhaustiva hasta una complejidad prefijada.
- Dos o tres inductores independientes con rasgos distintos: diff textual, diff AST, atributos semánticos.
- Calibración previa con mecanicismos implantados.

Si no, “cuartil de mecanicidad” es un rasgo blando, no un eje objetivo.

## El solapamiento A↔B

Pedir más tipos al autor “sin decirle por qué” **no es realmente practicable sin filtración**. Si le pides más después de ver solapamiento, el propio hecho de pedir más es información: el autor puede deducir que su lote anterior no era suficientemente distinto.

La alternativa no es fingir que no ha pasado. Es:

- Pedir **desde el principio** N + M tipos, con M destinado a descarte por redundancia.
- No iterar.
- Usar al menos dos autores ciegos.
- Filtrar redundancia *después* con el inductor.
- Si el dominio no da más tipos distintos, reportarlo como resultado, como ya dice el diseño en §7.

La intención es correcta; el procedimiento “pido más sin decirte por qué” es una ceguera de teatro.

---

# 3. El endpoint

Sí, tiene su trampa.

La anti-Fase-12 prohíbe agregar limpios + silenciosos. Buena regla. Pero no prohíbe agregar **tipos**. El DiD con macro por tipo:

```
DiD = [S_modelo(B) − S_regla(B)] − [S_modelo(A) − S_regla(A)]
```

sigue siendo una media de diferencias. Puede salir positiva aunque el modelo no tenga ninguna detección real en el subconjunto que responde a Q2.

La trampa concreta es esta:

> **Q2 no se mide con el DiD global; se mide dentro del subconjunto donde la regla actualizada falla.**

El diseño deja que el DiD global conteste una pregunta de capacidad. Eso es lo que hace la Fase 12 en limpios+silenciosos: la resta agregada escondió el mecanismo. Aquí, la resta por tipos puede esconder que el modelo solo gana en los tipos fáciles o por escala, no en los tipos sin regla.

La regla de los cinco desgloses obligatorios **no basta**. Son obligatorios visuales, pero el endpoint primario sigue siendo la media agregada. Hay que añadir un sexto desglose, y ojalá convertirlo en el primario:

> **Mismo análisis restringido al subconjunto de tipos donde la regla actualizada y el inductor fallan.**

Otro problema: el DiD asume que pasar de A a B afecta igual a todos los brazos salvo por capacidad. No es cierto. La regla congelada está cerca del techo en A; en B solo puede bajar. El modelo está más lejos del techo en A; su degradación tiene forma distinta. Eso produce DiD positivo por artefacto de escala, no por generalización.

Y la falsa alarma como veto es débil. Si el modelo en B sube detecciones a costa de más falsas alarmas, el veto solo lo excluye si es descarado. Un coste asimétrico no está escrito y el puntuador es tuyo.

---

# 4. El tamaño

Los números no aguantan para la pregunta central.

**N = 30 puede valer para el DiD total** si esperas un efecto grande. Con dispersión entre tipos 0,43, una diferencia entre brazos de 0,4–0,5 es detectable.

Pero la pregunta central no es el total: **es la curva por cuartil de mecanicidad**. Y ahí N no es 30; es 7–8 por cuartil.

Con 7–8 tipos por cuartil, el error estándar de una puntuación de brazo es:

\[
SE \approx \frac{0,43}{\sqrt{7,5}} \approx 0,16
\]

Para una diferencia entre brazos o entre A y B dentro del mismo cuartil, el error es mayor: 0,20–0,25. Un efecto plausible de 0,2–0,3 queda bajo. No hay potencia.

Y si quieres el DiD dentro de cada cuartil, también necesitas A dentro de cada cuartil. A solo tiene 18 tipos: tocan a 4–5 por cuartil. Eso no es interpretable para un modelo mixto.

**Mi recomendación:** si el cuartil es el análisis primario, no pongas N = 30 total. Necesitas al menos **15–20 tipos por cuartil**, es decir N total 60–80 como mínimo. Mejor aún: no uses cuartiles; trata la mecanicidad como variable continua y preinscribe una interacción brazo×mecanicidad. Eso requiere N total del orden de 60–100, pero no puedes fingir que 30 repartidos en cuatro celdas es un experimento con potencia.

**k = 5:** para la regla está bien, porque es binaria. Para el agente no. Con 5 casos, una tasa real de 0,6 tiene un intervalo de confianza enorme. No vas a estimar varianza intra-tipo ni vas a poder acreditar una “detección propia” convincente con 1 de 5.

Si queréis poder decir “este tipo lo detecta el modelo y ninguna regla”, exigid cobertura completa o casi completa en ese tipo, y usad k ≥ 8 o repeticiones con semillas distintas.

Y las varianzas traídas de la Fase 12 son del catálogo mecánico. En B pueden ser mayores. El cálculo es optimista.

---

# 5. Lo que haría distinto

No reescribiría todo desde cero; el esqueleto A/B y la separación Q1/Q2 son defendibles. Pero cambiaría estas cosas:

1. **Eliminar el análisis por cuartiles.**  
   Sustituirlo por un modelo continuo de mecanicidad estimado por varios inductores independientes y pre-registrado.

2. **No llamar oráculo al inductor.**  
   Llamarlo detector de reglas con gramática limitada. Calibrarlo antes de B.

3. **Redefinir el endpoint primario Q2.**  
   No el DiD global. El primario debe ser:

   > ¿Qué hace el modelo en el subconjunto de B donde la regla actualizada y/o el inductor no detectan?

   El DiD queda como secundario descriptivo.

4. **Subir N.**  
   Si el análisis central es por mecanicidad, encargad 60–80 tipos B, no 30. O aceptad que 30 solo sirve para una lectura global débil.

5. **Automatizar la regla actualizada.**  
   El patrón oro de Q2 no debe ser una persona viendo B. Debe ser un inductor automático con espacio de reglas cerrado y búsqueda exhaustiva. El humano es evidencia adicional, no juez.

6. **Varias pasadas del agente.**  
   Si el agente es probabilístico, una pasada única no estima tasa por tipo. Con k = 5 y una pasada, estáis añadiendo ruido innecesario.

7. **Mantener la lección de la Fase 12.**  
   El total, sea de limpios+silenciosos o de tipos, puede mentir. No pongáis una media como el número de portada. El número de portada debe ser:

   > En tipos donde ninguna regla escrita o inducida detecta, ¿cuántos detecta el modelo con cobertura completa y sin falsas alarmas?

Este diseño, tal como está, todavía puede publicar un hallazgo de capacidad que no existe. No está roto entero, pero el parágrafo §5.5 está justificado.

La Fase 12 se salvó por construir el adversario fuerte. Esta fase no se salvará solo con un adversario fuerte; necesita un **juez de mecanicidad calibrado** y un **endpoint directo al subconjunto objetivo**. Las dos cosas se pueden arreglar antes de encargar B.

---

## Razonamiento del modelo

We need answer in Spanish, Markdown, technical, no filler. We need "romper diseño" for Fase 13. Need analyze. User asks us as senior consultant. Need identify fifth failure mode not in §5, assess if revisions incorporated, endpoint trap, sample size, different approach. Need be harsh. We need reason carefully.

We need understand design. There is a lab with corpus of "mutaciones declarativas" 63 operators in A. Fase 12 showed regex beats LLM agent because corpus constructed with declarative mutation operators leaving mechanical signature. Fase 13 designs new blind set B of N=30 new types from author who sees circuit and transformation contract but not A, agent, adversary. Four arms: model frozen, regex frozen, regex updated seeing B, inductor. Endpoint DiD: (S_model(B)-S_regla(B)) - (S_model(A)-S_regla(A)), positive means model degrades less than rules. Calculated twice: Q1 frozen regex, Q2 updated regex. Oráculo mecanicidad: inductor blind over diff syntactic, classify B post hoc into quartiles. They mention variances from Fase 12: intra-type rule 0, model 0.057, between types 0.43/0.31. N=30, k=5. Analysis by quartile with 7-8 types. Three measures first week without agent: inductor, solapamiento A-B, distribution of adversary over B type-by-type. §5 failure modes: all mechanical; author reinvents A; real fault contamination; coverage unequal by chance; unknown.

We need "nombrar modo de fallo que no está" and cheap measure first week. Pistas: inductor is mine and I write it; author of updated rule has to see B; agent frozen from Fase 12 not retrained; four arms scored with scorer also mine. Need infer failure. The fifth may be "the oracle/inductor is part of the intervention/design, and can itself leak/be gamed/be correlated with endpoint causing a measurement artifact" or "score is scored with a scorer also mine" -> scorer bias/leakage? Let's think.

We need find mode not named. They listed:
- all B equally mechanical -> inductor reveals.
- author reinvents A -> overlap A-B.
- real faults contamination -> separated.
- adversary coverage uneven -> run adversary frozen on B distribution.

What's omitted? Potential:
1. The *inductor* is written by the same author as the lab, maybe unconsciously tuned to A? It can be weak/strong; if weak then mechanical B appears non-mechanical, but the regex updated (human seeing B) maybe similar? Need failure: **The mecha oracle and the endpoint share a generator (the lab author)**, inducing correlation between the stratifier and the outcome. If the inductor fails to find a rule, a type classified "non-mechanical" may be just outside the inductor's rule space, but the human updating regex with B may still find it, or the model may detect it. Consequence: false Q2 effect appears in the "non-mechanical" quartile because the updated regex cannot pick up those types that the inductor calls non-mechanical but that are actually mechanical for the human regex writer. Wait: If inductor is weak, some mechanical types classified non-mechanical. In that quartile, frozen regex likely fails. Updated regex written by human seeing B may succeed (because human can write regex), so model vs updated regex Q2 difference may be negative (rules win), not false positive model. Or if inductor classifies non-mechanical but human updated regex wins, Q2 may show model degrades more? Hmm.

Need understand endpoint. S_model vs S_regla per type macro. For Q2, regla actualizada written seeing B. If updated regex can cover many B types, then model degrades vs updated? Actually S_regla(B) high. Model S_model(B) maybe lower. DiD = (S_model(B)-S_regla(B)) - (S_model(A)-S_regla(A)). In A, regla likely beats model by 0.284? Fase 12: regla +0.873, model +0.629 -> (model - regla)(A) = -0.244. In B, if updated regla high and model moderate, difference maybe negative larger -> negative DiD. If model better for nonmechanical, maybe positive.

Fifth failure may relate to **the endpoint's double comparison with a scorer "also mine"**. Scorer may contain biases/targets that align with model or rules? Let's inspect.

Puntuador firmado from Fase 12. The score per type: perhaps detection rate, false positives, etc. The "puntuador" is also written by lab author. If the score is correlated with mech inducer or with regex, could systematically favor model. For example scorer gives partial credit to detections even if false? Not clear.

Another possible fifth mode: **The blind B author is not the same person as the person writing the updated rule? Actually updated rule writer sees B. The lab author writes the inductor. The B author may be selected by lab author and could share mental schema. More importantly, *the actual cause in Fase 12 was a closed set known to the script author*. Here updated regex is written seeing B, so Q2 compares a model not trained/adapted to B against a human/regex tailored to B. That's an unfair setup for capability: updating regex after seeing B essentially gives the regex arm access to the test distribution, while model is frozen. The question Q2 says "¿detecta el modelo cosas para las que no se puede escribir una regla estática?" But if you compare against a human updated after seeing B, what counts as "cosas para las que no se puede escribir una regla estática" is conditional on the human/regex writer's skill and all of B. The endpoint Q2 can be gamed simply by the updated regex being weak, not by model capacity. If the updated regex author is bad or constrained, the model may "win" on nonmechanical quartile even if it detects only mechanical signatures. This is a **weak adversary problem**? Actually updated adversary is not necessarily "fuerte"; it's whoever writes rules seeing B. The panel correction earlier said Q2 vs adversary actualizado. But the design treats "regla actualizada" as strongest possible static rule, yet it depends on human. If the human is not exhaustive, the model can win not due to non-mechanical generalization but because the human failed to write a regex for a mechanical type. And the mech oracle could be used to post-hoc identify such types, but if the oracle and human regex author have different coverage, mismatches. The fifth failure: **the updated regex arm is not guaranteed to be the strongest rule-based competitor; if it underfits B, Q2 confuses "can't write a static rule" with "the author didn't write one"**. Cheap measure: after B is delivered, have the inductor also produce a discriminative regex automatically for each type; this serves as a grounded lower/upper bound for what a static rule can do, and compare human updated rules against inductor rules. Actually they have "inductor as automatic floor". But they don't pit inductor as a formal baseline? They call it "suelo automático" of mech oracle. Maybe could use the inductor as the strongest static rule? But if the inductor is weak, not.

Let's read text: §3 "inductor de reglas ciego: dado par (limpia, mutada) de cada tipo, intenta inducir un discriminador por diff sintáctico ... da eje mecanicidad. ... clasificarse post hoc." The "inductor" also in four arms as "suelo automático". So updated rule is separate human. A mismatch between inductor and updated rule could be a failure: **The post-hoc quartile used for primary analysis is defined by the inductor, but the endpoint compares against a different rule arm (regex updated by a human).** If the human updated rule and the inductor disagree, the quartile "non-mechanical" may contain types where the human could not write a regex but the inductor made it mechanical, or vice versa. This contaminates the interpretation. Cheap measure: use the inductor itself as the Q2 rule baseline in addition to human updated regex. If the inductor (automatic) recovers the type, then the type is mechanical and should be excluded from "true non-mechanical" for Q2. Actually the design already uses inductor as "suelo automático" but not in endpoint explicitly. They may include? "inductor" brazo but not endpoint? It says four arms; in endpoint uses S_regla (congelada/actualizada), not S_inductor. That's a gap. The failure: **the mech axis and the Q2 rule competitor are two different rule systems with different expressive power; non-mechanical according to inductor may still be mechanical for the human updated regex, or vice versa.** Could produce false interpretation. Cheap measure: since inductor is already implemented in week 1, after B is available, compare inductor with human updated rule, and define the primary stratum as types where **neither** the updated regex nor the inductor can produce a working rule (or maybe where updated regex fails). Hmm.

But user hints: "el inductor de mecanicidad es mío y lo escribo yo; el autor de la regla actualizada tiene que ver B; el agente está congelado desde la Fase 12 y no se reentrena; y los cuatro brazos se puntúan con un puntuador que también es mío." They may want us to see **the same person writes the inductor and the scorer**; that's a single-person bias/leak: the oracle that defines the stratification and the outcome measure share author. Could be the fifth mode: **the inductor and scorer can be tuned to make the model look good in the quartile where it wins**, because the "mechanicity" axis is not pre-registered; it is constructed by you. Since you also score, you might unconsciously choose features/diffs that correlate with model strengths. Cheap measure: pre-register/pseudo-it? But measure cheap first week: **blind calibration of inductor against A and synthetic mechanically generated types before B**, and ensure the score doesn't have access to diff features? Hmm.

Let's parse clues:
- The user says: "el inductor de mecanicidad es mío y lo escribo yo; el autor de la regla actualizada tiene que ver B; el agente está congelado desde la Fase 12 y no se reentrena; y los cuatro brazos se puntúan con un puntuador que también es mío."
They expect us to identify mode related to author collusion? "the experimenter is everywhere" maybe.

Potential modes:
A. **The oracle/inductor leaks the answer** to the analysis: If the endpoint is "within each quartile," and the quartile is estimated from the same data used for endpoint, there's a regression to the mean / selection artifact. For types in the extreme quartiles, the DiD within each quartile has bias due to conditioning on a variable (mechanicity) that is related to the outcome. Especially with N=30 and 7-8 per quartile, conditioning on an estimated classifier may create false differences. This is a statistical issue not in §5: **post-hoc stratification on an imperfect classifier produces Stein's paradox / regression to the mean / selection bias**. Cheap measure first week: apply the same analysis to A (known catalogue) where we know no generalization? Simulate? But maybe mode is "the quartile analysis is still an aggregate within quartile; with 7-8 types, one or two types dominate; does not meet the anti-Fase-12 rule." They forbid aggregated over clean+silent, but DiD per quartile is still aggregated macro over types; maybe with 7-8 types, one high-leverage type can flip quartile. But they also require distribution type-to-type. Hmm.

B. **The blind author B can infer the adversary/regex signatures from the scoring or from the circuit?** They ask "¿es practicable sin que lo deduzca?" in §2. The author doesn't see A but may deduce all mutation operators because they are natural. The overlap measure after B catches if B=A. But if author deduces the *regex* style instead of A? That's a failure? Not as severe.

C. **The model is frozen from Fase 12 and was trained/selected on A**. The DiD from A to B compares baseline difference to new; but the model's advantage over rules in B may arise from model being similarly weak everywhere, not from "degrading less." A difference-in-differences with unbalanced starting points is confounded by ceiling/floor effects: the model has more room to improve relative to rules? Need examine. DiD = (M_B - R_B) - (M_A - R_A). If rule is already near 1 on A, it can only degrade on B. Model is 0.6 on A, could also degrade or stay; so positive DiD may simply reflect rule's ceiling/overfit to A, not model's capacity. This is a big confound: **regression to the mean for the stronger baseline**—rules were optimized on A, so they have less room to improve and thus must degrade; the model was not as good on A, but if it remains mediocre, DiD positive. Q2 against updated regex is supposed to fix by updating on B, but if updated regex is written seeing B, it may approach ceiling on B too, but maybe not. For Q1 (frozen) this is obvious: the frozen regex is overfit to A, so it will degrade. But they know Q1 is operational? They may still misinterpret.

D. If the goal is "model detects things for which no static rule can be written," comparing against an updated regex after seeing B is confounded by the **human rule author seeing B** and thus possibly using the same diff signatures as the inductor; but also, the ground truth of "can't write static rule" is unknowable. The fifth mode could be: **The oracle of mech is also the plan: by using an automatic diff-based inductor as ground truth, you are measuring "mechanicity" with exactly the same class of systems you're trying to beat.** The inductor's ceiling is similar to regex arms; if the model beats that, but the inductor is weak, not enough.

Need perhaps identify the single most important fatal flaw: **The design's internal definitions are circular**:
- Q2 wants to know if model detects things for which no static rule can be written.
- “No static rule can be written” is operationalized by the inductor (cannot induce a diff-based discriminator) or updated regex (human cannot write).
- But the induction procedure is rule-based and static. The set of things it cannot find is just "failures outside the syntactic feature space." It does not distinguish "non-mechanical" from "my inductor is weak."
- The design admits these are different in prompt’s Q1 frente a Q2: "Un inductor por diff sintáctico que no encuentre regla puede significar «el tipo no es mecánico» o «mi inductor es flojo»" and asks if implementable. We need answer: It is not solvable with one inductor; you need **multiple independent inductors with different feature spaces** and a formal notion of "no rule" based on a known search space (e.g., regular languages over tokens). But even then, "no static rule" is not well-defined.

Maybe the fifth mode is something they didn't see: **B is not a random sample of "new types"; it is another convenience sample from the same author with the same generator's constraints. The DiD between A and B is uninterpretable because A and B differ not by "out of catalogue" but by author/time/context. Any observed difference can be due to selection of B, not capacity.** The design uses A and B as two levels of "distance from catalogue," but B is created after the design to be new; there is no metric of distance except the mech oracle. If B turns out mechanically different because author intentionally avoids declarative signatures (even without instruction), then DiD positive for model may reflect B being easier/harder, not model generalization. But maybe endpoint accounts by DiD? Let's think.

Maybe the fifth mode: **The model was already the best at non-mechanical types in Fase 12? No.**

We need think from clues. They mention "el inductor de mecanicidad es mío y lo escribo yo; el autor de la regla actualizada tiene que ver B; el agente está congelado desde la Fase 12 y no se reentrena; y los cuatro brazos se puntúan con un puntuador que también es mío." This reads: the weak points are:
- inductor is written by you -> it may encode your beliefs of what is mechanical; no independent validation. If it fails to find rule, you might have made it weak.
- updated rule writer seeing B -> possible contamination of adversary? Actually updated rule must see B to be fair. 
- agent frozen -> maybe it is not adapted to B, so any positive result is robust; but if negative, can say model wasn't trained on B. But Q2 is about zero-shot? The phase does not re-train model. "congelado desde Fase 12 y no se reentrena" -> If the question is whether model can detect new types, you test only zero-shot transfer, not maintenance (Q1). For Q1 maintenance, no retraining might be okay? Actually Q1 asks "does it cost less to maintain model than rules?" But the model is frozen; maintaining a model could involve retraining, but here not allowed. So the design's Q1 is only "zero-shot maintenance" not actual maintenance. Is that a failure? Hmm.

- scorer is yours -> same author bias.

Could be **the entire chain from mech oracle to score uses the same hidden labels generated by B author**, and if the lab author wrote the inductor with knowledge of how he writes mutation operators, then the "mechanicity" axis is not independent of the endpoint's scoring. That can create an artifactual correlation.

We need provide maybe multiple failures? User wants "nombradlo" singular. But can list one main and maybe additional.

Need also answer §2 corrections real? Need verify each.

- Q1 vs Q2: are they separated? The table separates, but DiD calculated against frozen for Q1 and updated for Q2. However in analysis, Q1 and Q2 may be mixed? Need read: primary "DiD ... calculado dos veces: contra regla congelada (Q1) y contra actualizada (Q2)." That separation seems real. But Q1 still contaminates conclusion if Q1 and Q2 both reported? Maybe if they preinscriben both, Q1 may leak into summary. They must decide. But question asks "¿basta separarlas, o Q1 sigue contaminando la conclusión?" Need answer: Separation by arm is necessary but not sufficient. Q1 still can contaminate because Q1 is the frozen rule, an adversarial baseline that is known to degrade when observations are out of its training set; any model that is less overfit to A will have a positive Q1 DiD even if it has zero ability to detect non-mechanical failures. If the summary reports Q1 with Q2 adjacency, or if Q2 uses the same type-level errors as Q1, drift can leak. More concretely: The four arms include both frozen and updated rule; but the "regla" in the primary DiD when not specified might be ambiguous. They should pre-register Q2 as sole primary, Q1 as secondary, and no Q1/Q2 combined figure. Also need a common baseline (same B types) and maybe compare against a "re-trained regex" that is not merely human updated but automatic.

- Oracle: implementable? We need break it. It is **not** implementable as a valid measurement because "mechanicity" is relative to the inductor's feature space/search procedure. There is no ground truth for "no rule can be written." A diff syntactic inductor only tests one restricted family. Its failures cannot be interpreted as "non-mechanical"; they are always "outside the inductor's grammar." To make it real, you need:
  - Define the exact search space of allowed rules (e.g., regular expressions over token streams) and the exact induction algorithm (e.g., enumeration up to complexity length, with a completeness proof within that space). Then "no rule found" means "no rule within this finite space found by exhaustive search," not "no static rule."
  - Multiple independent inductor variants (syntactic diff, attribute-level, AST edit script, etc.) to triangulate. A single inductor is a single instrument with unknown sensitivity.
  - Calibration: run on A and synthetics; measure sensitivity/specificity against known mechanical/non-mechanical constructed types.
  - Precommit: if the inductor fails to find a rule, the team must not later use that failure as proof; it's a lower bound.
  - Also stop calling it "oráculo" because an oracle implies ground truth; it's just another heuristic arm.

- Solapamiento A-B: "pedirle más tipos al autor sin decirle por qué" is not practicable because the author may infer why from context; but more importantly, the overlap measure itself may be weak if B is not literally same operator but just uses same *signature categories*. The failure §5.2 asks if high overlap, ask for more types undirected. But if the author has a finite set of types, asking more may produce semantic variants, not genuinely different; increases N but not diversity. Also the author might deduce that you kept asking for more because previous ones were too close to something; or if you ask "sin decirle por qué" after showing overlap, it violates blind author's ignorance? The author is blind to A but may know you are testing generalization. Need answer: It is not reliably practicable; you need a stopping rule and an independent diversity criterion, not just repeated requests. Maybe use multiple independent authors, adversarial author, or change contract to ask for categories far apart.

- Endpoint trap: The difference-in-differences with macro by type calculated twice. Has its own trap? Yes, there are several:
   1. **Aggregation over types via macro still averages the score over types; with N=30 and high between-type variance, the DiD can be driven by a handful of outlier types.** They require type-to-type distribution, but the endpoint itself is still the mean over types. If distribution is bimodal, the mean is misleading; the primary should be a pre-registered test on the distribution of type-level differences (paired Wilcoxon/permutation), not just point estimate. The fifth required breakdown is not enough.
   2. **Ceiling/floor effects**: The baseline A difference (M-A - R-A) is not a stable counterfactual; the regla congelada may be near ceiling on A, so it can only degrade on B. The DiD double subtraction assumes additive bias, but task difficulty changes across A/B can affect the rule and model differently (difficulty × arm interaction). No design can remove that without randomized assignment of item difficulty, which is not possible.
   3. **Using the same B types for both Q1 and Q2 and across quartiles leads to multiple comparisons and post-hoc subgroup selection.** The quartile subgroup is an estimated moderator; the DiD per quartile is confounded by conditioning on an outcome-related classifier. Need pre-register quartile boundaries from A? Better: pre-specify an independent holdout set for defining mech quartiles? But that uses B.
   4. **Falsa alarma as secondary with veto**: The veto is one-sided. A model with zero false positives on A may produce false positives on B; if the score includes false positives linearly, DiD can be positive due to riskier model on B even if it has no real detections. Secondary veto may not be enough if it's only the endpoint? Need define false-positive penalty in the score as a cost, not just veto.
   5. **Detecciones propias**: Asking for number of types where model detects and no rule detects. With k=5 and model's intra-type variance, one case could be chance; because if a model makes a probabilistic error, a type can be "partial"; they should require model detects all k cases or a statistically improbable detection rate above chance, not just any detection. In Fase 12 was 1/55 and no real detection; as they note. For B, "detección propia" as all cases? The prompt mentions "tipos donde el modelo detecta y ningún brazo de reglas lo hace"; not enough. Need pre-specify criterion: e.g., model covers ≥4/5 mutated cases in that type and zero false positives in clean, and maybe re-run with different seeds if agent probabilistic.
   6. **DiD as difference of differences with an updated human regex on B may be confounded by the fact that the updated regex has been fitted on B, so it may do as well as possible; if it does not reach ceiling on non-mechanical types, that's either because no static rule exists or because human didn't find one. The endpoint cannot distinguish these.** This is central.

- Sample size: N=30, k=5. Does it hold? We need check numbers. They measured between-type variance for agent 0.43, for rule 0.31; intra-type 0.057, 0.0000. They say power from N. We need estimate required N. The endpoint is difference of differences: the effect of interest is interaction arm×environment (A/B). For each type score difference D_type = model - rule; compare between A and B. Need variance of D difference. The variance of D_type across types in A = Var(M) + Var(R) - 2 Cov(M,R) maybe. Values: model 0.43^2 = 0.1849; rule 0.31^2 = 0.0961. If independent, sum = 0.281, sd = 0.53. N=18 observed maybe. For B unknown. For N=30 per group, standard error of mean difference A-B = sqrt(0.281/18 + 0.281/30) = sqrt(0.0156+0.0094)=0.158. Thus a DiD of 0.2 would be 1.27 SE; 0.4 would 2.53. Perhaps enough for large effect. But they are subgroup splitting by quartiles: per quartile N=7-8; if the total N=30. For each quartile, difference between A and B within that quartile? But do they have A within same quartile? Need match A types by mech quartile. N=30 B gives 7-8 per quartile, but A has only 18 total, maybe 4-5 per quartile. The power for within-quartile DiD is much lower. Also between-type variance likely non-normal, bimodal; analytic mixed model with 7-8 clusters may be unstable. Need perhaps estimate:
    - For total DiD with N=18 A, 30 B, sd of difference within group ≈ 0.5. SE = sqrt(0.25/18+0.25/30)=sqrt(0.0139+0.0083)=0.149. A difference of 0.3 gives t≈2.0; with multiple covariates maybe OK. But for per quartile: N_B=7.5, N_A maybe 4.5, sd perhaps 0.5. SE = sqrt(0.25/7.5+0.25/4.5)=sqrt(0.0333+0.0556)=0.298. A difference of 0.3 gives t=1.0. So quartile analysis is underpowered. And they say N=30 leaves 7-8 per quartile, "which is the analysis that matters." But they compare within quartile against what? Need know. If no within-quartile A baseline? They could compute S_model(B)-S_regla(B) per quartile only, not DiD. But to claim "model degrades less", need compare to A's quartile? They may have only 18 A types; not enough. This is a serious issue: the primary answer is within quartile, but N for each quartile is 7-8/4? They need perhaps N=30 per quartile, not total. The measured variance between types 0.43 means the standard error of a mean of 7.5 types is 0.43/sqrt(7.5)=0.157 if just one arm's score. Difference between arms paired maybe. But for DiD with quartile strata, need SE maybe larger. So N=30 is insufficient for the central question if quartiles are the analysis. They might need at least 30 types per quartile? That's 120 B types, not 30. Or use continuous mech as covariate and fit interaction, requiring more total N (e.g., 80-100) with the variance/effect size. We can compute approximate power: Assume difference between model and rule D_type has sd across types ~0.5. For within a quartile, SD of mean difference in B for 7.5 types is 0.5/sqrt(7.5)=0.183. If comparing quartiles (slope), to detect a difference between top and bottom quartile of maybe 0.5, SE of difference between two means ~0.26, t≈1.9. Might be borderline. But for total N=30 across four quartiles, the quartile comparison of means is noisy. Need perhaps simulate. But we can say N=30 is enough for overall DiD but not for quartile-centered inference; 7-8 per quartile is not enough for a robust random-effects model with between-type variance 0.43, and A has too few to condition. They need either N per quartile ≥20, or choose continuous mech covariate with pre-specified model and no quartile split. Also k=5 may be okay for coverage, but k is not the limiting factor; their argument that k=5 can estimate intra-type variance is partly true, but with k=5 and binary outcomes, parameter estimates are unstable (especially for variance). If the model has intra-type variance 0.057, with k=5 the binomial detection rate has large CI: if true rate 0.6, observed 3/5; CI 0.15-0.95. For partial types, 5 cases gives very little information. But k=5 may be sufficient to distinguish binary 0/1 vs constant partial, not to estimate variance well. They should use k=8 or more for model partial types if they care about estimating partial detection rates; but cost maybe okay. Use k=5 maybe okay for rule (binary) but not for model. They mention k=8 no buy for rule, but for model and variance intra-tipo 0.057, k=5 may not estimate variance reliably. Need mention.
   - Power for detecting opposite coverage: To detect a type as partial vs full, 5 cases gives exact binomial; with 5 cases, if true coverage 0.6, probability of observing 0 or 5 (censored) is 0.4^5 + 0.6^5 = 0.0102+0.0778=0.088; okay. But CI wide. For comparing model vs rule in a type with 5 cases, the paired Mc Nemar? Not sure.

- What would do different: Maybe we need propose alternative better design. They asked "Si el diseño entero está mal encaminado..." Need answer maybe partly. We can propose:
   - Instead of trying to define mechanicity post hoc with an inductor, **construct B** with a pre-registered, independent taxonomy of "mechanicalness" and sample explicitly across it. E.g., use multiple blinded authors, each asked to produce types from deliberately different categories: syntactic transformations of messages vs semantic inconsistencies vs state/timing failures vs config errors. But that leaks? Hmm they didn't want to tell author. But you can stratify by source/contract, not by "mechanicity." Or use existing real failure strata.
   - Use **real production failures** as a separate out-of-distribution test (they have some). While not definitive, they avoid construction bias.
   - Use **synthetic generators with tunable distance**: generate families from A with increasing mutation depth/randomness; but maybe.
   - For Q2, use a **fully automatic rule-induction algorithm as the "static rule" baseline**, not a human. If the algorithm is complete within a specified language class, then its failure is a lower bound. Human updated regex is not a well-specified rule class.
   - The ideal experiment for generalization is not A/B with only two sets; it is a **gradient of distance from A** with continuous mech index and many built B sets. They already want curve; but one B set of 30 doesn't give a reliable curve if the mech axis is within B.
   - Use **multiple independent labs/authors** to create B; summary across authors.
   - Pre-register an analysis as a **per-type paired difference** and use a permutation test matching types by mech, not a DiD aggregate.

Need perhaps structure answer:
1. Identify fifth failure mode clearly: likely "**El oráculo de mecanicidad y el resultado comparten los mismos rasgos; el experimento define la variable de estratificación con el mismo observador que mide el resultado, y el análisis por cuartiles a posteriori introduce un sesgo de selección/regresión a la media. We'll call it: stratification-confounder (or 'mechanicity is a post-hoc outcome-correlated covariate measured without error model').**"
But maybe they expect something else. We need ensure matches their hints. Let's further analyze possible fifth mode hidden:
- Inductor is mine and I write it -> may overfit to A? Actually if the inductor is developed on A (known A), then when applied to B, mech classification of B uses rules trained on A? It says "sin ver catálogo" but developer sees A? The lab author has A. Could unconsciously use A in inductor design. If inductor is written seeing A, "oráculo" is not blind to A, despite saying "sin ver catálogo" at runtime. It may classify B types as non-mechanical if they don't match **A's specific signatures**, not if they are not mechanical. That is exactly §5.2 but inverted? §5.2 handles B reinvents A; but not inductor contamination from A. If inductor is too aligned to A's features, then B types that are mechanical in new way will look non-mechanical. Then the "non-mechanical" quartile is contaminated with mechanical-but-novel types. The model may detect some of them if they share things with its training? Actually model trained on A, maybe not. More importantly, the updated regex writer seeing B might detect them, so Q2 model vs updated may fail. But for Q1, frozen regex might fail and model maybe detect? Could create false model win in nonmechanical quartile due to induction failure. This is the known "inductor weak" but with nuance: **inductor developed by same author as A and scorer, without an independent benchmark, can be tuned to label as non-mechanical exactly the types where you expect model to win.** But could be.

Maybe the most specific hidden failure:
**The design uses B as a test set, but the "non-mechanical" type stratum is *defined* by the inductor after seeing B. The primary endpoint is computed within that stratum. This is a form of "cherry-picking"/data-dependent subgrouping.** They avoid declaring quartiles before B. Since the inductor is built by the lab author, it can be influenced by the B results (even unintentionally) to produce quartile boundaries that flatter the model. The cheap measure first week without B? Hmm but B not yet. The measure in first week: **pre-register the inductor and its hyperparameters against A and synthetic mechanical/non-mechanical benchmarks before B exists; then freeze it, and compute quartile boundaries from A only or from a separate calibration set.** Wait, if B not yet, you can freeze inductor but not quartile boundaries. But if inductor is frozen before B, still post-hoc extraction can be data-dependent. To prevent, freeze also the analysis script and quartile thresholds using the A distribution? But B types may shift. Maybe you can't define B quartiles before seeing B. But you can freeze the method, not the boundaries. Yet exploratory post-hoc subgroup with N=30 is problematic. The cheap measure in first week: **simulate B by constructing synthetic folds from A and applying the pre-registered analysis pipeline; if the pipeline can produce a false positive DiD in a known "no capacity" scenario, fix it.** Hmm.

Could be the fifth mode: **the endpoint is not protected against the model's score on B being inflated by one or two "detecciones propias" which are actually random partial credits, because the scoring is tied to the oracle's mech features?** Not likely.

Let's read prompt carefully in §5.5: "Pistas de dónde mirar...: el inductor de mecanicidad es mío y lo escribo yo; el autor de la regla actualizada tiene que ver B; el agente está congelado desde la Fase 12 y no se reentrena; y los cuatro brazos se puntúan con un puntuador que también es mío."

This is likely a clue to "conflict of interest/observer bias" across all components. The omitted failure might be: **Tus elecciones de diseño (inductor, scorer) comparten autor, y eso puede inducir un sesgo de autor común en la dirección favorable al agente. No hay separación entre quién define la dificultad del ítem y quién lo evalúa.** More precise:
- The inductor (mechanicity) may inherit the same implicit notion of "what model can't do" because you've seen the model's outputs from Fase 12. If you write the inductor after seeing model results, you may define non-mechanical as what model detects.
- The scorer (also yours) can reward model-typical outputs.
- Since the agent is frozen and not re-trained, any leakage from model behavior to B labels via you can be direct.
- The updated rule writer sees B but not agent, so can't game agent; but not independent.
The cheap measure: **have the mech oracle written by a different person (or based on pre-existing formal features) and never see agent outputs until after freezing; run an adversarial calibration where the inductor must recover known synthetic signatures; blind yourself to model outputs when writing the inductor and scorer.** But they ask "medida barata que lo destaparía en la primera semana": perhaps **run a "red team" on the inductor before B: generate N synthetic type pairs with ground-truth mechanicity, and ask a third party to shuffle labels.** Not first week? Could.

Potential fifth mode: **The model arm is frozen from Fase 12 and not retrained, but the scoring function is built by the same person who has seen model failures. The model may have learned the scorer's preferences rather than actual faults; on B it may score by output format not detecting.** But no.

Let's maybe identify a more technical flaw with DiD that is not listed:
**Regression to the mean due to selecting the endpoint after seeing the Fase 12 result.** The design selects N=30 and builds B with the intent to find a positive difference for model. The same author who saw the Fase 12 failure knows the one type where model had "own detection" and may (unconsciously) construct B to include similar types. No blinding of B author? B author doesn't see agent, but lab author designs contract. The lab author may include examples/words that hint "semantic" vs "syntactic"? They said "autor sees circuit and transformation contract, nothing more." But the lab author writes contract; if contract is written by someone who knows what model is good at, it could leak. The fifth failure could be **the contract itself is a hidden channel to the blind author**: terms like "contrato de transformación" can be written to elicit types the model detects. But maybe less direct.

Need answer with "nombradlo" maybe say: **El quinto modo es el "auto-examen": la Fase 13 usa el mismo laboratorio, el mismo generador y el mismo diseñador para construir el eje que separa el resultado. Llámalo "endogeneidad del estrato de mecanicidad" / "estratificación post-hoc con instrumento no calibrado".**

Could include: "Es el modo de fallo que no está en §5 porque §5 trata de B, del autor, del adversario, y de la distribución; no trata del inductor ni del puntuador. Las pistas que das lo localizan: el inductor y el puntuador son tuyos. El fallo es que el criterio de división (mecanicidad) y el criterio de éxito (score) pueden compartir autor, rasgos y errores; el análisis dentro de cuartiles convierte un índice post hoc en un diseño preinscrito. Si el inductor es flojo en las direcciones donde el agente ya es bueno, el cuartil no-mecánico se llena de tipos mecánicos no descubiertos, y el DiD por cuartil produce el falso positivo que la Fase 12 temía."

But we also need cheap first-week measure:
- Construir un **benchmark de calibración del inductor** con A + tipos sintéticos cuya mecanicidad es conocida por construcción (firma implantada). Calcular sensibilidad y especificidad. If the inductor doesn't achieve near 100% on implanted signatures, it's not usable as an oracle; no B needed. Also run the same DiD calculation on A alone with fake "B" folds to see false positive rate. Specifically: split A into half, treat one half as B, compute quartile DiD; if significant, design is broken.
- Or "The plant: no experiment with B; use synthetic types generated by two independent methods, one mechanical and one semantic; run the intended analysis; it must separate them. If not, stop." Hmm.

Need answer Q1/Q2 revision check more concretely:
- "Separar Q1/Q2: la tabla es real. Pero no basta porque el brazo de regla actualizada introduce una ventaja de entrenamiento injusta en Q2: al ver B, puede sobrescribir la dificultad de los tipos. Dependiendo de la capacidad del autor de reglas, Q2 mide la diferencia de capacidad del autor, no del modelo. Además Q1 y Q2 comparten B; cualquier análisis que use Q1 para validar Q2 puede contaminar. Propuesta: Q2 es primario y el resto no entra en el resumen."
- "El oráculo: no implementable como oráculo. Es implementable como *heurístico con sensibilidad desconocida*. Lo rompe la confusión entre 'no hay regla' y 'mi inductor no la encuentra'. Sin un espacio de reglas cerrado y una búsqueda exhaustiva, el cero del inductor no es cero. Además al hacer búsqueda sintáctica por diff, puede no captar reglas que usan atributos semánticos o patrones compuestos; el humano actualizado puede superarlo; por tanto el cuartil no-mecánico incluirá mecánicos."
- "Solapamiento A-B: pedir más tipos sin explicar es frágil. El autor puede inferir que su lote anterior se consideró redundante; y si su catálogo mental es finito, entregará variantes, no diversidad. Lo practicable es: tener un criterio de sobregeneración pre-registrado, encargar a dos autores ciegos, y filtrar por solapamiento con un umbral antes de incluir; no iterar pidiendo N más sin criterio."

Endpoint traps:
- "La macro por tipo sigue siendo una agregación. La anti-Fase-12 prohíbe agregar limpios+silenciosos, pero no prohíbe agregar tipos dentro de un cuartil. Con 7-8 tipos, la media es vulnerable a un único tipo extremo; el desglose obligatorio no evita que el endpoint sea la media."
- "DiD tiene supuestos de interacciones no cruzadas: cualquier cambio de dificultad entre A y B que afecte distinto al modelo y a la regla produce DiD. La regla congelada es un caso particular: está en techo en A; solo puede bajar. Eso infla DiD Q1 por artefacto. Contra la regla actualizada, el efecto depende de que el humano alcance el techo en B; si no lo hace, Q2 mide el hueco del humano, no capacidad."
- "La regla de los cinco desgloses no basta: no incluye la comparación *por tipo en q2 contra el inductor*, ni el análisis de sensibilidad al umbral de mecanicidad, ni un test de significación con permutación tipográfica. Deberían preinscribir un modelo continuo de mecanicidad como covariable, no cuartiles."

Sample size:
- "N=30 para el total puede alcanzar diferencias grandes, pero no para la cuestión central por cuartiles. Con 0.43 sd entre tipos, la SE de la media en un cuartil de 7.5 es 0.157 para una sola puntuación; para diferencias de brazos con correlación quizá 0.2-0.25. Un efecto plausible 0.2 queda bajo. No basta. Si lo central es el cuartil, N debe ser por cuartil, no total; yo no bajaría de 12-15 tipos por cuartil y, si se quiere estimar interacción, 20. Eso es N total 60-80 si cuatro cuartiles. k=5 para tipos binarios está bien, pero para el agente con varianza intra-tipo y pocos parciales, k=5 produce intervalos enormes en la probabilidad de detección; si quieren 'detecciones propias' convincentes necesitan k≥8 o repeticiones independientes del agente."
- "El análisis por cuartiles con 7-8 tipos no es estable; un modelo mixto con pocos clusters subestima varianza de efectos aleatorios y los intervalos son anticonservadores."

Alternative design:
- Maybe propose "no uses cuartiles; usa un índice continuo de mecanicidad medido por varios inductores; usa N≈60-80 tipos; usa un regla automática con espacio de búsqueda cerrado como adversario Q2; usa autores múltiples; usa solo Q2 preinscrito; y agrega fallos reales como evidencia cualitativa."
- Or if design entire wrong: "La pregunta Q2 es casi inverificable con un solo laboratorio; la respuesta honesta sería un benchmark de tipos con gradiente de distancia y un adversario automático, no un humano." But need not say entire wrong? We can say "Mejor que cuartiles: modelo continuo, no cuartil."

Need maybe discuss whether "Q2 is the one with scientific value" but they might be wrong: Q2 may not be meaningful because "no se puede escribir regla estática" is not a property of type; it's relative to a language class and author. The whole framing might be flawed. If I think design entire mal, I can say: "Sí, hay una parte mal encaminada: la variable clave no es mecanicidad binaria/cuartiles, es distancia al catálogo definida por espacio de reglas; el diseño quiere estimar un efecto no paramétrico con un instrumento no validado. Reescribir: usar generadores programáticos de B con nivel de ruido/distorsión continuo, no un autor ciego."

But the prompt says "Este encargo es para que su defecto, si lo tiene, salga hoy." Need be direct.

Let's think deeper about possible mode failure and size.

Maybe there is a statistical trap in using the same measured variance from Fase 12 to plan B. The Fase 12 variance estimates are from a corpus of 18 types where the rule was at ceiling 16/18 and model partial. The variance between types is 0.43 for model, 0.31 for rule. But those types were designed to be mechanically simple; on B, variance between types could be larger (adversarial harder). The power calculations may underestimate variance. Also, if the model has six partial types, intra-type variance 0.057 is likely due to those partial types; on B with new unseen hard types, model may be more variable, perhaps producing more partials. Need mention.
Could compute detection of DiD with paired design. But maybe enough.

Let's consider exact endpoint formula:
```
DiD = [ S_modelo(B) − S_regla(B) ] − [ S_modelo(A) − S_regla(A) ]
```
This uses macro per type. Suppose four arms: model, regla congelada, regla actualizada, inductor. For Q1: S_regla(B) is frozen. For Q2: S_regla(B) is updated. They calculate twice. They also have distribution of adversary over B. The per-type score may be e.g., a scalar 0-1 or maybe +1 for detections - penalty false alarms. The difference model-rule per type could be negative/positive. The DiD compares this difference between A and B. The model and rule are paired on same types. The A difference is maybe model-rule -0.244. If B difference is +0.1, DiD = +0.344. Good.

Potential trap: **If the same frozen model is used on both A and B, and frozen model was selected/tuned on A, then A difference for model is not a clean baseline; the model has seen A (or was selected on A). Thus DiD may underestimate model's degradation because model may already be partially overfit to A.** Actually Fase 12 model developed on A? The prompt says A is upstream; adversary and agent developed against A. So model has been trained on A; rule too. That's analogous: both are "fitted" to A. Then B out-of-sample. So DiD controls for that. For Q2, updated rule is refitted on B while model remains fitted on A, making model compete with an unfair refitted comparator. This is important.

Could the fifth mode be **lack of an independent holdout for A**? They use A both to derive variance and as comparison baseline. The A dataset was used in Fase 12 and likely both model and rule are overfit to its types. The DiD difference between A and B might reflect overfitting to A rather than generalization. But maybe that's the intended regression-to-mean? Actually if both fitted on A, using A as baseline will produce optimistic results (both performed well on A). If model is less overfit to A, the DiD will be positive even if model has no generalization. This is a fundamental confound absent in §5.5. It says "el agente está congelado desde la Fase 12 y no se reentrena" clue. The model's A performance is selected from Fase 12; B is new; the rule is given a chance to refit. In Q2, the rule updated sees B, so not overfit to A, but the model remains selected on A. That asymmetry can produce a negative DiD (rules look better) rather than false positive. But for Q1, positive false.

Maybe hidden mode: **Q2's "actualizado viendo B" is not actually a static rule; it's a human who has seen all B. This is an oracle with unlimited look at the test set. In machine learning terms, the test-set labels of B are seen by one of the algorithms (the human regex author). The model is frozen and not given the same access. This violates equal treatment; Q2 becomes "human can write rules after seeing the answer vs model zero-shot." The answer to Q2 "cosas para las que no se puede escribir regla estática" cannot be derived from such a contest unless you also create a version of the model re-trained/adapted to B or at least few-shot, which the design forbids.** That may be the missing mode. Let's evaluate:
- Q2 asks: "¿detecta el modelo cosas para las que no se puede escribir una regla estática?" A "regla estática" is written with full knowledge of B. In that sense, it is a human oracle. If model is frozen, it gets no B knowledge. But Q2 isn't asking if model is better than rules; it's if model detects non-rule types. A direct comparison is not needed; you could simply report model's detections among inductor-defined non-mechanical types. But they use DiD as endpoint. The comparison to updated rules may be necessary to avoid base rate. But if updated rule succeeds on a type, then that type is mechanically rule-writable by a human; Q2 should focus on types where updated rule fails. Then the critical number is "model detections among types where updated rule fails." The DiD subtracts A and may obscure this. So maybe fifth mode: **The endpoint doesn't directly measure Q2; Q2 requires first defining the subset of types where updated rule fails, and then judging the model's performance within that subset. The DiD aggregate can be positive even if the model has zero detections in that subset due to the A/B scaling.**

Yes! That seems plausible. Let's articulate:
- Q2's scientific claim is centered on "types where no static rule can be written" (or where updated rule does not detect).
- The endpoint DiD across all B averages types where rules work and where they fail. If the model degrades less overall due to other confounds (score scaling, difficulty), DiD can be positive without any model detections in the "no rule" types. Conversely, if you restrict to non-mechanical quartile, maybe not enough.
- Missing failure: **The primary endpoint doesn't condition on Q2's target set first; it uses the entire B set, so the claimed capacity can be manufactured by degradation differences in the mechanical region.** The anti-aggregation rule prohibits clean+silent but not mech/non-mech; the report might headline DiD instead of the direct non-mechanical detection rate.
- Cheap measure first week: **run a pre-registered "target-set" analysis on A: treat types for which the updated rule fails as the target; show that the proposed DiD is not driven by target-set performance. Or, simpler, make the primary endpoint the model's detection rate in the subset where both updated rule and inductor fail; not DiD.**
But user asks "el modo de fallo que no está en §5" maybe this is not listed. Pistas: "el autor de la regla actualizada tiene que ver B" -> if updated rule sees B, it may succeed on many types, leaving a small target subset. If target subset tiny, the DiD across all B swamps it. "cuatro brazos se puntúan con puntuador que también es mío" less relevant.

Let's think of clues:
- "el inductor de mecanicidad es mío y lo escribo yo" -> the stratifier is custom.
- "el autor de la regla actualizada tiene que ver B" -> updated rules are fitted to B; target set depends on their skill.
- "el agente está congelado desde la Fase 12 y no se reentrena" -> model has no B knowledge; Q2 is zero-shot.
- "los cuatro brazos se puntúan con un puntuador que también es mío" -> scorer custom.

Maybe the failure they don't see is **there is no independent validation of B's "newness" beyond the overlap A-B, and the primary endpoint is based on an actualized adversary that might be either too weak or too strong.** Hmm.

Let's maybe combine several failures under umbrella but one primary.

We need decide final answer. We can structure:
1. **Resumen ejecutivo**: The design has a fifth mode: "El estrato que define Q2 se estima con un instrumento no validado y a posteriori; el endpoint DiD agregado no condiciona al subconjunto objetivo. Nombre: *sesgo de auto-instrumento* o *estratificación endógena por mecanicidad*." 
   - Cheap first-week measure: **Calibración adversarial del inductor contra A y contra tipos construidos con firma inyectada y con firma semántica; además, ejercicio de "anti-DiD" en A: split A into pseudo-B and test if the method produces Q2-like false positives. If fails, stop.**
2. **¿Correcciones reales?**:
   - Q1/Q2: separation real, but Q2 can still be contaminated by Q1 if both in summary; Q2's arm is not an equal comparator because updated rule sees B while model frozen.
   - Oracle: Not implementable as oracle; only heuristic. Need multiple independent inductors and a completeness statement; "no encuentra regla" is always lower bound.
   - Solapamiento A-B: measure useful, but iterative "send more without telling why" leaks and conflates N with diversity.
3. **Endpoint**: Has its own trap: DiD is an aggregate; it doesn't measure target subset; data-dependent quartile analysis; inflated by regression to mean; not fixed by five breakdowns. Propose primary endpoint: model's type-level detection rate in the subset where updated rule (or inductor) fails, with A calibration, and permutation test.
4. **Tamaño**: N=30 not enough for quartile primary; need 15-20 per quartile if using quartiles, or continuous model with N ~60-100; k=5 okay for rule but too small for model's partial rate; use k≥8 or repeated passes.
5. **Alternativa**: Rewrite using generator-based distance gradient and an automatic rule induction baseline; or if use human author, multiple authors and pre-registered continuous mech analysis.

Need maybe include exact power calculations. Let's maybe do some approximate calculations to be concrete. We can invent assumptions:
- Difference D = model - rule within type. In A, observed mean maybe -0.244 (since 0.597 vs 0.889? Actually model rate 0.597? They say phase 12 10/18 = 0.597? yes. Rule 0.889? 16/18? 0.889. Difference -0.292? Wait 0.597-0.889=-0.292? But summary says +0.629 vs +0.873? Maybe score not rate? In §7 rates 0.597, 0.889. The scores maybe different. Anyway.)
- Cross-type SD of D: If model and rule independent, sqrt(0.43^2+0.31^2)=0.53. But could be correlated; assume paired SD of D perhaps 0.4-0.6.
- For N=18 A and N=30 B, SE for difference in means = sqrt(0.5^2/18+0.5^2/30)=sqrt(0.0139+0.0083)=0.149. A DiD of 0.3 is ~2 SE; 0.4 is 2.7. That might be okay.
- For within-quartile B N=7.5, the SE of one arm score is 0.43/sqrt(7.5)=0.157. Difference between model and rule with paired SD maybe 0.4/sqrt(7.5)=0.146. But to compare across A and B within same quartile, A quartile N maybe 4.5, SE = sqrt(0.4^2/7.5+0.4^2/4.5)=sqrt(0.0213+0.0356)=0.238. A DiD of 0.3 is t=1.26, no power. If effect 0.5, t=2.1 with 10 df maybe borderline. This shows inadequacy.
- If the within-quartile contrast is the one they'll use, they need ~15 per quartile for SE ~0.3/sqrt(15)=0.077? Actually maybe.
Let's compute needed N per quartile: For 80% power, 5% significance, effect size of 0.5 with SD=0.4, we need n per group per stratum about 16 per group? Use formula 2*(z_0.975+z_0.8)^2 * (sd/effect)^2 = 2*(1.96+0.84)^2*(0.4/0.5)^2 = 2*7.84*0.64=10.0. So 10 per group per stratum? Wait for two independent groups per stratum; but paired maybe less. For comparing A and B within a quartile, need n per group per stratum around 11 for a large effect 0.5. They have 4-5 A and 7-8 B, too small. For a moderate effect 0.3, n ≈28 per group. So they need maybe 15-20 per stratum, total 60-80 per group (A and B). That is significant.
- But if they use continuous mech as covariate and don't split quartiles, need about N=30 per group? Interaction effect? For an interaction with continuous variable, sample size roughly 4 times? But not necessary.

Need mention "cuartiles con 7-8 tipos" maybe maybe acceptable for descriptive, not inferential.

Potential issue with k=5:
- To estimate intra-type variance of model 0.057, with 5 Bernoulli observations, the standard error of the variance estimate is huge. Simpler: detection rate for a type with true p=0.6 observed in 5 cases has 95% CI 0.147-0.947. If you need to distinguish partial p=0.6 from full p=1 or zero, k=5 can exclude full/zero with small p-value: P(X=5 | p? Actually if null p=1, any miss rejects; if p=0, any hit rejects. For partial intermediate, no issue. But to distinguish p=0.4 vs p=0.6 impossible. For intra-type variance and partial coverage, k=5 gives very noisy estimates; "seis tipos parciales" may become censored 0/1 on B. k=8 better for estimating partial rate. Recommendation k≥8 and maybe multiple agent runs (temperature sampling) to reduce variance.

Need maybe address "la varianza medida aguanta?" We can say:
- The two variances are driven by Fase 12's construction (types mechanical and rule at ceiling). They are not necessarily valid for B. In particular, between-type sd 0.43/0.31 for score/rate can be lower bound if B is harder or less homogeneous. So sample size calculation is optimistic.
- The intra-type rule variance 0.000 may be a consequence of the rule's design; but if B includes non-mechanical, the rule's within-type score may also become partial? Actually a regex rule as a deterministic function should be binary per type if the cases inside a type are generated by a single mutation operator; since each type produces identical signature, rule detection may still be 0/1. But if a type is partially detected due to fragile regex across variants, maybe not. Still binary expected. 
- The model's intra-type variance 0.057 likely decreased due to averaging over 8 cases; with k=5, not same.

Need include answer to "¿Y la regla de los cinco desgloses obligatorios basta para evitarla?" We'll say no; because all five are descriptive adjacent to the endpoint, but none removes the DiD aggregate as primary. The veto is weak: it only blocks a win if a brazo has more false alarms; it doesn't calibrate the score or test the significance. Need add a sixth: **condición de subconjunto objetivo**: all primary Q2 statements must be accompanied by the same DiD restricted to types where updated rule fails/inductor fails; and a permutation CI. Or define endpoint as that.

Let's maybe propose an explicit alternative endpoint:
Let T = types in B where regla actualizada (and maybe inductor) does not detect (e.g., score below threshold, say 0). Let the primary Q2 be:
\[
P = \frac{1}{|T|}\sum_{i\in T} S_{modelo}(i)
\]
against a null distribution of model performance on A types where the same rule fails; or better:
\[
D = \frac{1}{|T|}\sum_{i\in T} [S_modelo(i) - S_regla(i)]
\]
not an A-to-B DiD. But if T is small, N matters. To avoid selection bias, T must be defined by pre-registered rules, and model's false alarm rate within T must be reported. Also compare with an automatic inductor. The Q2 endpoint should be **direct model hit rate on the target subset**, with binomial/permutation test; the DiD is a secondary supportive analysis for degradation.

Could the user expect "Detecciones propias del modelo" number goes on cover, but with k=5 one detection own may be chance; need require all k cases. We can mention.

Need answer "No seáis amables" so direct. Use maybe "Este diseño no está mal en su esqueleto, pero tiene un error de validez en la medida central" not overly harsh.

Let's craft final response with clear sections.

Need ensure Spanish correct, Markdown. The final maybe:

```
## Veredicto

El quinto modo de fallo es ...
```

But user asked "encargo: rompe este diseño..." Need maybe start "Lo rompo por aquí: ..."

Let's shape:

**Quinto modo (nombre y medida barata)**

Name: **Estrato de mecanicidad endógeno y a posteriori.** Or "El oráculo es un brazo más, no un juez; el juez tiene dueño." Expand:
- The design relies on a custom inductor to split B into quartiles, but the inductor and scorer are written by the same person who has seen Fase 12 and knows what the model can do. There is no independent definition of "mecánico."
- When you split by an estimated variable after seeing B and then compute within-stratum endpoint, you are effectively doing subgroup analysis with an instrument that has unknown classification error. That can create a false "model wins in non-mechanical quartile" due to misclassification or due to the updated-rule writer being worse than the inductor on certain non-syntactic mechanical types.
- The agent frozen and rule updated see asymmetric information; the updated rule seeing B means its failure on a type is due to author skill, not impossibility; the endpoint does not distinguish.
- Specifically, the missing mode is not "oracle weak" but **the quartile variable is not pre-registered and is produced by the same mechanism that scores the outcome**. If the inductor's "no rule found" errors are correlated with the scorer's features, the analysis is circular.

_Cheap measure first week without B or agent_:
- Build a calibration set of synthetic types with known (pre-implanted) mechanical signatures and non-mechanical semantic faults. Run the inductor; require sensitivity ≥0.95 and specificity ≥0.95 at the *type* level. If not, inductor cannot be "oráculo."
- Additionally, run the intended DiD+quartile analysis on A split into pseudo-B (e.g., half the A types by author/operator) with the known result "no new capacity"; if it yields a significant Q2-like positive, the analysis itself is broken. This is cheap and no agent needed? Wait the model required. But agent exists. They can run using A. It's not week 1 without agent? They said first week without agent. But could be cheap with existing agent? They wanted "sin agente"; perhaps can simulate with score? Hmm. The calibration of inductor doesn't need agent. But the false positive run needs agent and rule. Maybe not first week. We can say "before B, using A only" maybe includes agent. But they said three measures run without agent and without adversary; we can propose measure with agent maybe second? Better maybe "sin encargar B" is enough. We can say "barata en A con el agente ya existente" but they want first week without agent. Maybe "For the inductor calibration: synthetic mechanical types with known signatures; if fails stop." That's enough.

Need maybe mention "destaparía en la primera semana": run the inductor on a **planted corpus** where mechanicity is known. If it cannot identify planted non-mechanical types, then any post-hoc quartile is garbage. This directly addresses.

Let's now structure final answer.

Need maybe include "¿Están de verdad incorporadas las correcciones?" Section:
- **Q1 frente a Q2**: "La separación de preguntas es real; tabla y DiD doble la reflejan. Lo que no es real es la simetría de los comparadores. Q2 usa un brazo entrenado en B (regla actualizada) contra un agente congelado. Eso convierte Q2 en un test de 'humano que ve el examen contra alumno que no lo ve'. Para Q2 el comparador debe ser un inductor automático con espacio de reglas cerrado, no una persona. Además, si Q1 y Q2 comparten B y el resumen, Q1 filtra: hay que preinscribir Q2 como único primario y Q1 como operativo."
- **Oráculo**: "No implementable como oráculo; es un detector con sensibilidad desconocida. Su fallo 'sin regla' es un límite de su gramática. Para que sea válido, hay que: (a) definir el espacio de reglas permitido; (b) usar búsqueda exhaustiva, no heurística por diff; (c) calibrarlo con tipos de firma implantada; (d) usar al menos dos inductores independientes con rasgos distintos. Si no, la frase 'cuartil no mecánico' no tiene valor."
- **Solapamiento A-B**: "Pedir N más sin decir por qué no es ignorable: el propio acto de pedir más después de ver solapamiento es información. Es practicable si se pre-registra la regla de parada y se pide un lote inicial de N + M sin condiciones; pero no como bucle. Alternativa: encargar a dos autores y filtrar redundancia **después** con el inductor; no iterar."

Endpoint section:
- "Sí, tiene trampa. La anti-Fase-12 prohíbe agregar clean+silent, pero no agrega **tipos**. El DiD por macro por tipo es una media de diferencias de tipos; un solo tipo extremo puede dominar. La regla de cinco desgloses obligatorios no evita esto; solo obliga a exhibir la distribución. El endpoint primario sigue siendo la media, e incluso puede ser positiva sin ninguna detección en el subconjunto no mecánico."
- "Trampa específica: el DiD global no condiciona en el subconjunto objetivo. La Q2 es '¿modelo detecta lo que la regla actualizada no?' Si eso es lo que se quiere, el primario debe ser el rendimiento del modelo **dentro de los tipos donde la regla actualizada y/o el inductor no detectan**, no la resta global."
- "Trampa de escala/techo: la regla congelada está cerca de techo en A; en B solo puede bajar. Modelo en A tiene más recorrido. La resta doble no identifica capacidad."
Maybe avoid duplicating.

Size section:
- Provide rough numbers. "Con 0.43 de dispersión entre tipos, un cuartil de 7-8 tiene una SE de 0.15-0.17 para una puntuación; para dos brazos y diferencias es 0.20-0.25. Un efecto de interés de 0.2-0.3 queda bajo. Necesitas 20+ tipos por cuartil si quieres inferencia; N=30 es solo suficiente para el DiD total, no para la pregunta por mech."
- "Además, A solo tiene 18 tipos; para un DiD por cuartil necesitas A y B dentro del mismo cuartil; con A repartido son 4-5 por cuartil, insuficiente."
- "k=5: para la regla binaria okay; para el modelo, con 5 casos, una tasa de 0.6 tiene CI 0.15-0.95; no puedes estimar varianza intra-tipo ni acreditar 'detección propia' con 5 casos. Usa k=8 o múltiples pasadas con semillas."
- "Las varianzas traídas de Fase 12 son del catálogo mecánico y no se transfieren a B. La varianza entre tipos en B puede ser mayor."

Alternative:
- "No usar cuartiles. Modelar mecanicidad como covariable continua (primer componente de varios inductores) y pre-registrar una interacción brazo×mecanicidad con N total no inferior a 60–80."
- "Para B, encarga a dos autores ciegos y sobremuestrea 40-50 tipos; no pidas N más iterativamente."
- "Para Q2, el comparador debe ser un inductor automático con espacio de reglas cerrado y búsqueda exhaustiva, no solo un humano. El humano actualizado es una evidencia más, no el patrón oro."
- "El primario podría ser: proporción de tipos del subconjunto no cubierto por regla actualizada donde el modelo cubre ≥k−1 casos, con intervalo de permutación y con veto de falsas alarmas. DiD como secundario."

Need maybe mention "el diseño entero no está mal encaminado; está mejor que Fase 12 en que separa Q1/Q2 y define medidas previas; pero la pregunta Q2 sigue sin ser medible con un solo inductor." This is balanced.

Let's now craft final in Spanish.

Need be careful with direct quotes and numbers. The prompt has "puntuador firmado" not defined. We'll not overdo.

Let's maybe include "No seáis amables" -> "Lo digo sin eufemismos."

Potential alternative if we misidentify fifth? Need maybe hedge: "El modo que yo nombraría —y que no está en §5— es..." not "the only one."

Let's think if there is an even more crucial flaw:
**The endpoint Q2 against updated rule sees B, but the model is frozen. The design doesn't allow re-training or fine-tuning the model on A or B; so Q2 asks "does a model trained on A detect new non-mechanical types?" which is fine as capacity. But if the model was frozen and not retrained, then any performance in B is "zero-shot generalization." The claim from DiD "degrada menos" might be merely about stability, not capacity.**
Maybe we can mention as secondary.

Need maybe answer "¿Y la regla de los cinco desgloses obligatorios basta para evitarla?" We'll say no. Maybe propose "sexto desglose obligatorio: el mismo DiD restringido al subconjunto donde la regla actualizada no detecta; y la distribución de la puntuación modelo por tipo en ese subconjunto completa, no media."

Let's include specific phrase "Q2 no se mide con DiD; se mide con la tasa de detección del modelo condicionada a que el adversario actualizado falle. Si la condicionas no hay base para DiD." This might be a strong memo.

Let's maybe write "La medida barata que lo destaparía en la primera semana" as an explicit bullet:
1. **Banco de calibración del inductor**, planted mechanical signatures and semantic non-mechanical.
2. **Ejercicio de falsos positivos con A partido**: use `A1` as training/development and `A2` as pseudo-B; if the Q2 pipeline yields positive in `A2` due to quartile misclassification, the design's internal validity is null. But this uses agent and existing models; still no B.
Actually first week without agent maybe impossible for second. But we can suggest "esto se hace con el agente ya congelado en un día; no encarga B." That's fine.

Need maybe include "No basta que el inductor 'no vea el catálogo' en runtime; tú lo escribes viendo el catálogo y viendo los resultados del agente. Eso no es un oráculo ciego."

Let's now produce final. Need ensure Markdown and not too long? We can be thorough but concise. The desired oververbosity 5. We can present around maybe 1000-1500 words. Let's aim 1500-2000 words? User asked many things, so maybe around 1800 words. Use bullets.

Let's draft in Spanish:

```
## Veredicto
El diseño no es una farsa, pero el quinto modo de fallo es...
```

Let's start:

"El quinto modo que no está en §5 lo llamaría **estratificación endógena**: el eje de mecanicidad que decide dónde se lee el resultado se estima con un instrumento propio, no calibrado, después de ver B, y lo puntúa la misma persona. ..."

Need maybe say "No es exactamente §5.2 (B está contenido en A) ni §5.1; es el instrumento que define el cuartil el que puede fabricar la señal."

Then under "medida barata":
- "Creadme veinte tipos con firma inyectada mecánica y diez con falla semántica implantada; que el inductor los clasifique a ciegas. Si no separa, no hay Fase 13. Es un día de trabajo."

Let's now compose.

Need maybe include math calculations:
- For within quartile:
\[
SE_{\text{cuartil}} \approx \frac{0.43}{\sqrt{7.5}} \approx 0.157
\]
for one arm; difference paired maybe \(SE \approx 0.20\). To detect 0.20? Hmm maybe no. Use "no basta".

Potential issue: difference of model-rule in B within quartile might have sd not 0.43. But enough.

Let's include "N=30 no para cuartiles; N=30 es para una media total. Si el análisis central es por cuartiles, el N central es 7-8, no 30."

Need maybe answer "¿Los números aguantan?" with "Aguantan para el DiD total si esperas un efecto grande (≥0.4); no aguantan para los cuartiles."

Let's maybe include "k=5 no compra potencia para la regla, pero no es la regla el límite: para el agente y para 'detecciones propias' necesitas k mayor. Una detección en 1 de 5 no es evidencia."

Let's also address "endpoint tiene su propia trampa como el total la tuvo en Fase 12?" Yes: "El total de agregación aquí es la macro por tipo dentro de cuartil y el DiD. La distribución tipo a tipo se pide al lado, pero el endpoint es la media. Es análoga: una media de diferencias puede esconder dos regímenes."

Let's now write final answer fully. Use "No seáis amables": maybe "No firmes así."

Let's ensure all requested points are covered explicitly:
1. Fifth mode named + cheap measure first week.
2. Checks Q1/Q2, oracle, overlap.
3. Endpoint trap.
4. Size.
5. What would do different.

Let's write.