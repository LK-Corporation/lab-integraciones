<!-- modelo: deepseek-v4-pro · via: api.deepseek.com · encargo: encargo_diseno13b.md · 237 s · 25245 tokens -->

## Error de razonamiento antes de empezar

La v2 asume que **“emergente” implica “no invertible”**. No es cierto. Un fallo no diseñado, una vez curado y con sus trazas disponibles, es un tipo definido por sus características observables; si la evidencia discriminante está en la traza, un autor de reglas puede escribir una regla estática a posteriori que lo detecte. La emergencia no elimina la invertibilidad: solo la hace incierta.

La v2 lo reconoce parcialmente en §2, pero luego coloca el primario sobre **el residuo declarado por el autor de la regla actualizada**. Eso reintroduce la rotura de la v1: condicionar el endpoint en el desenlace del comparador. El residuo declarado es el nuevo oráculo de mecanicidad, pero ahora lo declara el propio comparador.

---

## 1. El séptimo modo de fallo

**F7 · El puntuador es un mando no clavado y contaminado por A.**

El puntuador decide qué es detección y qué es falsa alarma. Se hereda de la Fase 12, donde fue calibrado con el catálogo A. No aparece en la tabla de mandos de §6. Si sus umbrales, reglas de coincidencia o clases se optimizaron para A, imprimirá la firma de A en la evaluación de B. El agente afinado y el puntuador comparten historia: no hay independencia entre el instrumento y el objeto medido.

**Medida barata que lo destapa antes de contratar al curador:**  
congelar el puntuador con huella, publicar su código y umbrales, y pasarlo por una auditoría de calibración sobre un conjunto sintético derivado exclusivamente del contrato por un tercero, con juez humano ciego. Si la concordancia con el juez baja del 90%, el puntuador no es válido para B y hay que recalibrarlo o sustituirlo.

---

## 2. ¿Es emergencia de verdad o contrato con otro nombre?

**No basta con publicar la proporción.** La vía (b) es exactamente el contrato leído al revés si las relaciones metamórficas las escribe la misma persona que diseña la capa. El orden de §9 no lo salva: el diseño de la capa ya está en §4, visible antes de redactar las relaciones. La distinción entre “relación de invariancia” y “operador de mutación leído al revés” es solo de intención, no de efecto.

Para que la emergencia sea real, las relaciones deben ser escritas por alguien que **no vea la capa**, o derivarse de un estándar versionado con una herramienta independiente. De lo contrario, la vía (b) es una fábrica de fallos de contrato.

- **Vía (a):** solo captura ruidosos. No es un problema de validez, sino de utilidad: si todo B es ruidoso, la fase no contesta la pregunta.
- **Vía (c):** es la única insesgada para silenciosos. Con tasa base del 1%, se necesitan **299 ejecuciones** para tener un 95% de probabilidad de ver al menos un fallo (`ceil(log(0.05)/log(0.99))`). Para estimar la tasa con precisión ±1% con confianza del 95%, se necesitan ~380 ejecuciones. Una muestra de 200 solo tiene un 86,6% de ver al menos uno.
- **Cuarta vía que no está en el documento:** oráculo funcional de contrato por intervención causal. Provocar condiciones cuyo resultado el contrato especifica (rotar credencial → 401, apagar FHIR → AE, duplicar MSH-10 → rechazo) y comprobar el efecto. Es más rico que (a), distinto de (b), y su sesgo se puede declarar y sellar. No sustituye a (c), pero cubre silenciosos sin depender de equivalencias metamórficas.

Además, hay que definir si un fallo detectado por varias vías cuenta solo por la primera o por todas; si no, la proporción es manipulable.

---

## 3. El endpoint residuo

El residuo declarado repite el error de la v1: **es un oráculo de mecanicidad declarado, no medido**.

- El autor puede declarar de más (hace su derrota más digna) o de menos (hace su script más potente). No hay protocolo que lo acote sin filtrarle.
- Si el autor es un modelo, el sesgo es de prompt: puede alucinar cobertura o seguir la inercia del texto. Se necesitaría un humano para validar.
- La trampa propia: el subconjunto “no cubrible” se define por la habilidad del comparador, no por una propiedad del fallo. Es condicionar en el desenlace del comparador.
- Si el residuo sale vacío, es un resultado sobre el banco, no publicable como capacidad. Debe reportarse como “la capa no produjo fallos no reglables”.

**Cambio mínimo:** el primario debe ser la tasa del agente sobre **todo B curado**, no sobre el residuo. El residuo se reporta como secundario, y el subconjunto no cubrible lo determina un juez ciego que no sea el autor, antes de que el autor declare. Si la declaración del autor difiere del juez, se publica la discrepancia y se invalida el residuo. Alternativa: alinear incentivos del autor con penalizaciones por cada tipo mal clasificado (cubrible/no cubrible) según el juez.

---

## 4. El brazo del prompt afinado: ¿simetría o ventaja?

**No es simetría real.**

El prompt afinado se optimizó contra el catálogo A. El autor de la regla actualizada recibe el contrato, pero **no recibe ese conocimiento empírico**. El contrato es compartido; los 17.136 caracteres pueden contener ejemplos, heurísticas o firmas específicas de A. Los números del paso 29 muestran que la ventaja del afinado se concentra en **fallo silencioso**, exactamente la clase donde pudo memorizar firmas de A.

Para confirmarlo, habría que auditar el texto del prompt afinado. No lo tengo, pero el riesgo es suficiente para no aceptar la simetría sin evidencia.

**Cambio mínimo:** usar el prompt genérico como primario, o reportar ambos en portada y preinscribir que si la ventaja del afinado en B se concentra en tipos similares a A, se declara contaminación y el primario pasa al genérico.

---

## 5. Tamaño en B emergente

Hay que preinscribir una regla numérica **antes** de ver B, no dejarla a 🧑 después.

Propuesta concreta:  
> El primario se publica como primario si N ≥ 10 tipos, al menos 3 familias con ≥2 tipos cada una, k medio ≥ 3, y ningún tipo con k=1 entra al primario. Si no, la fase se reporta como descriptiva.

Esa regla se firma con huella junto con el negativo. Cualquier excepción se preinscribe también, no se decide tras ver la distribución.

---

## 6. Lo barato que falta o que sobra

**Falta un paso 0:** auditoría del puntuador y del prompt afinado. Es barato y puede matar la fase antes de montar nada.

**Sobra el paso 4** (inductor calibrado en A) en la fase temprana: no es necesario para decidir viabilidad; se puede posponer.

**El más probable de matar la fase es el paso 2/3** (piloto y distribución por familia/vía). Se puede adelantar un piloto de humo con **50 ejecuciones** y **2-3 relaciones metamórficas críticas** para evaluar F1 sin esperar a tener todas las relaciones ni toda la capa. Si no aparece ningún silencioso, se detiene.

---

## Cambios mínimos priorizados

1. **Clavar el puntuador** en §6 y auditarlo antes de curar.
2. **Cambiar el primario** a la tasa sobre todo B curado, no sobre el residuo declarado.
3. **Cegar la vía en la curación** y definir la contabilidad de vías.
4. **Independizar las relaciones metamórficas** de la capa.
5. **Preinscribir la regla de N mínimo** con umbrales numéricos.
6. **Auditar el prompt afinado** o degradar el primario al genérico.

---

## Razonamiento del modelo

Vamos a desglosar el encargo y el documento v2. Se nos pide romper la v2 antes de montar la capa de perturbación. Hay que contestar en español, Markdown, concreción técnica. Antes de nada, si hay error de razonamiento, decirlo. Luego atender por orden de importancia los puntos 1-6. No rediscutir Fase 12, no proponer B declarado, no diseño nuevo entero, cambios mínimos.

Necesito analizar profundamente el diseño v2 y encontrar fallos. El usuario da pistas: relaciones metamórficas las escribe él, del estándar; piloto lo corre él; curador ve contrato, estándar, ejecutor y relaciones, nada más; agente congelado desde Fase 12 con prompt afinado contra catálogo A; puntuador sigue siendo suyo.

Preguntas específicas:
1. Séptimo modo de fallo y medida barata que lo destape antes de contratar curador.
2. ¿Es emergencia de verdad o contrato con otro nombre? Evaluar vías (a),(b),(c), posible cuarta vía, tamaño muestra vía c con tasa base 1%.
3. Endpoint residuo: autor declara subconjunto no cubrible por regla estática. Riesgos de declarar de más o de menos, protocolo, si autor es modelo, trampa, residuo vacío.
4. Simetría del prompt afinado: ¿simetría real o ventaja? Analizar números paso 29, qué hay en 17.136 caracteres.
5. Tamaño en B emergente no se elige: cómo preinscribir análisis con tamaño desconocido, regla para N mínimo.
6. Pasos 1-6 baratos: cuál falta/sobra, más probable matar la fase, adelantar.

También hay que nombrar séptimo modo de fallo. Veamos la lista F1-F6:
F1 fuzzing solo ruidosos
F2 todo B misma familia
F3 oráculo metamórfico imprime firma
F4 contaminación diez conocidos
F5 curador no ciego
F6 el que no sabe ver.

Debemos encontrar F7. Posibles fallos:
- El puntuador es suyo (de Víctor). Podría estar sesgado, pero ya existente y con autopruebas. ¿Puede el puntuador filtrar? El curador no ve puntuador según F5. Pero el puntuador usado para evaluar agente podría tener sesgo hacia el agente afinado, especialmente si las clases y umbrales se calibraron en A. Pista: "el puntuador sigue siendo mío". Podría ser un mando discrecional no clavado. En §6 se clavan mandos, pero el puntuador no aparece. El puntuador decide qué es detección y falsa alarma, y si se calibró en A, su umbral favorece al agente afinado? En Fase 12 ya existía; podría ser un mando. La pista del usuario menciona "el puntuador sigue siendo mío" como algo relevante. Podría ser el séptimo modo de fallo: el puntuador, calibrado en A, traslada la firma de A a B a través del criterio de detección/falsa alarma. O el "detección propia" definida como mitad o más de instancias: ¿quién decide qué es una instancia detectada? El puntuador. Si el puntuador fue ajustado durante un mes contra A, puede estar sobreajustado a las firmas de A, y en B emergente dar ventaja indebida al agente o al revés. La vía barata: congelar el puntuador con huella, publicar su matriz de autopruebas, y correr una validación a ciegas sobre un subconjunto etiquetado por humanos sin ver salidas; o preinscribir umbrales antes de B. También el puntuador no es ciego al agente? Pero el puntuador es código determinista.

Otra posible falla: El "primario" es tasa de detección por tipo curado sobre B a exposición cero, macro por tipo, con veto de falsas alarmas comparadas con v3 congelado sobre limpios de B. Pero el v3 congelado podría tener cero falsas alarmas en limpios de B (o muy pocas) y el agente afinado podría tener más, así el veto es fuerte. Sin embargo, el punto es: ¿cómo se define "limpios de B"? Son ejecuciones sin fallo? El curador decide. Si el curador no es ciego al v3? Según F5 no ve v3. Pero los limpios pueden incluir casos que el v3 detectaría como fallo? El v3 congelado es script de regex, puede dar falsas alarmas en limpios. El veto exige que agente tenga <= falsas alarmas que v3 en limpios. Si v3 tiene muy pocas, es estricto. No es falla principal.

El séptimo modo podría ser "la capa de perturbación es construida por el mismo autor que escribe las relaciones metamórficas" y por tanto hay confusión entre generación y oráculo. El piloto lo corre él; las relaciones las escribe él. Si las relaciones metamórficas se escriben del estándar pero por la misma persona que diseña la capa de perturbación, puede (inconscientemente) elegir perturbaciones que sabe que violan las relaciones que escribió. Eso imprime firma de contrato. Pero F3 ya cubre oráculo metamórfico imprime firma. La medida es proporción por vía. Quizá el séptimo es más sutil: "las relaciones metamórficas se sellan antes de correr nada, pero se escriben después de diseñar la capa de perturbación". El diseño de la capa de perturbación está en §4: cinco familias. Si las relaciones se escriben del estándar pero conociendo la capa, pueden cubrir exactamente las perturbaciones planeadas. No es independiente. Medida barata: redactar las relaciones antes de fijar la capa, o derivarlas de un subconjunto del estándar seleccionado por tercero, o hacer que otra persona las escriba sin ver la capa.

Otra posible: "El agente congelado con prompt afinado contra A" puede tener el prompt con huella, pero el prompt afinado contiene ejemplos o descripciones de fallos de A. Eso es contaminación. F4 cubre los diez conocidos, no el catálogo A completo. El prompt afinado durante un mes contra el catálogo A podría contener información específica del catálogo A (no solo el contrato) que transfiera a B. En §5 se argumenta simetría porque compró el contrato, pero el paso 29 mostró que fuera de fallo silencioso el genérico es igual o mejor; dentro, el afinado pasa de -0.229 a +0.500. El afinado es mejor en fallo silencioso. ¿Eso es solo contrato o es conocimiento de A? Si el prompt afinado incluye ejemplos del catálogo A, no es simetría. El usuario pregunta en punto 4: ¿hay algo en esos 17.136 caracteres que no sea el contrato y que en B se convierta en ventaja indebida? Necesitamos responder: sí, probablemente el prompt afinado no solo incluye contrato sino ejemplos de A, heurísticas específicas, nombres de campos, códigos de error de A. El texto dice "prompt afinado con huella, sin reentrenar" y "lo que compró el mes fue el contrato de la transformación", pero no demuestra que el prompt solo contenga contrato. El paso 29 muestra que en fallo silencioso el afinado mejora mucho; eso podría deberse a que el prompt afinado codifica la firma de los fallos silenciosos de A (los diez conocidos o el catálogo A), no el contrato general. Si B emerge de ejecutar el sistema, los fallos silenciosos de B podrían parecerse a los de A? La Fase 12 era catálogo declarativo; A tenía fallos silenciosos específicos. El prompt afinado puede estar sobreajustado a esos. Para destaparlo barato: comparar el prompt afinado contra el genérico en un conjunto de fallos silenciosos generados por un tercero a partir del estándar pero no usados en el afinado, o auditar los 17.136 caracteres para ver si contienen ejemplos de A. Si contienen ejemplos, no es simetría. El usuario dice que no habéis visto el afinado, así que no podéis suponerlo? El control de contaminación dice que si necesitáis algo, pedidlo. Podemos pedir ver el prompt afinado y el genérico para determinar si hay información de A. Pero en la respuesta debemos señalar el riesgo.

Punto 6: "Lo barato que falta o sobra: pasos 1 a 6 de §9 no encargan nada y cualquiera puede matar la fase. ¿Falta alguno? ¿Sobra alguno? ¿Cuál tiene más probabilidad de matarla, y se puede adelantar al primer puesto?" Los pasos 1-6 son:
1. relaciones metamórficas escritas y selladas
2. capa de perturbación + tanda piloto (~200 ejecuciones)
3. distribución por familia y vía
4. inductor calibrado en A
5. regla de adjudicación e ideal_b, huella; kappa entre dos codificadores
6. el negativo firmado

Antes de contratar curador. ¿Cuál mata la fase? Probablemente el paso 2/3: el piloto puede mostrar que no hay silenciosos (F1) o que todo es de una familia (F2). Eso mataría la fase. ¿Se puede adelantar? El paso 1 es escribir relaciones metamórficas; si no hay relaciones, no se puede medir silenciosos en piloto. Pero se puede adelantar un mini-piloto con solo vía (a) y (b) existentes? Para evaluar silenciosos se necesitan las relaciones metamórficas. ¿Se puede adelantar la redacción de relaciones? Sí, es lo primero. Si las relaciones no producen silenciosos en el piloto, se mata. Quizá falta un paso 0: auditoría del prompt afinado para verificar simetría antes de montar nada. O un paso de comprobar que el agente congelado no está contaminado por B (no lo está porque B no existe). Podría faltar un paso de "congelar el puntuador y auditarlo", o "preinscribir la regla de detección propia".

El usuario pide: "¿Cuál tiene más probabilidad de matarla, y se puede adelantar al primer puesto?" Probablemente F1 (solo ruidosos) se destapa en el piloto, que es el paso 2/3. Para adelantarlo, se podría hacer una micro-tanda aún más barata, o usar los 10 fallos históricos como prueba de que hay silenciosos? Pero F1 se refiere al fuzzing actual. Se puede adelantar el piloto antes de escribir todas las relaciones metamórficas: bastan unas pocas relaciones para detectar silenciosos. O se puede simular mentalmente. La respuesta esperada: el paso 2/3 es el que mata; se puede adelantar haciendo un piloto de humo con una sola familia (codificación) y una relación metamórfica, sin esperar a todas.

Pero el encargo pide romper la v2, no solo responder preguntas. Hay que identificar fallas de diseño.

Examinemos con más detalle.

**Sobre la emergencia y el oráculo**

La v2 dice que B emerge de ejecutar el sistema. Pero la producción de B sigue dependiendo de un oráculo para decidir qué es fallo. La vía (b) metamórfica se escribe del estándar y del contrato, selladas antes de correr. La vía (a) no tiene oráculo pero solo captura fallos ruidosos. La vía (c) humana es insesgada pero cara.

El punto 2 pregunta: ¿basta publicar proporción? La respuesta es que no basta si la proporción se calcula después de curar y el curador conoce el origen de cada candidato? El curador ve el contrato, estándar, ejecutor y relaciones, nada más. Pero para adjudicar, el curador debe saber qué candidato vino de qué vía? Si sabe la vía, puede sesgar. En §4.2, "Un candidato entra en B solo si el curador puede señalar la cláusula que incumple." Si el curador sabe que un candidato vino de (b), entonces es más fácil que lo acepte porque ya viola una relación metamórfica, lo que infla la proporción de (b). Si no sabe la vía, ¿cómo se calcula la proporción? La proporción por vía se puede calcular automáticamente por el mecanismo que generó el candidato, pero el curador no necesita saberlo. Eso es importante: el diseño no especifica si el curador ve la vía. En §4.1 dice "La proporción de B que viene de cada vía se publica." No dice ciego a la vía. Eso podría ser un fallo: si el curador sabe que un candidato es de vía (b), el sesgo de confirmación es alto. Si no lo sabe, bien. Pero la adjudicación requiere que el curador evalúe todos los candidatos; si vienen etiquetados por vía, se rompe el cegamiento. Habría que enmascarar la vía durante la curación, y solo revelarla después. Eso es una medida barata.

Además, la vía (b) es "relaciones de invariancia sacadas del estándar y del contrato". Si un fallo solo entra en B cuando viola una invariante escrita por el autor, ¿en qué se diferencia de un operador de mutación leído al revés? La diferencia es sutil: un operador de mutación se escribe para producir fallos; una invariante se escribe para comprobar equivalencia. Pero si la capa de perturbación está diseñada para violar esas invariantes, entonces es lo mismo. La v2 no garantiza independencia entre la capa y las relaciones. El autor escribe ambas. Por tanto, la vía (b) puede ser una fábrica de fallos de contrato. La solución es que las relaciones las escriba alguien que no vea la capa, o usar un conjunto de relaciones preexistente, o generarlas automáticamente del estándar con una herramienta independiente. El usuario da pista: "las relaciones metamórficas las escribo yo, del estándar". Eso sugiere que hay conflicto de interés. El séptimo modo de fallo podría ser exactamente eso: "el mismo autor escribe el oráculo y la perturbación; la independencia es solo declarada". Medida barata: que las relaciones se deriven del estándar por una persona que no vea la capa, o que se congelen antes de diseñar la capa.

Pero el orden en §9 pone relaciones metamórficas (paso 1) antes de capa de perturbación (paso 2). Eso es bueno: se escriben antes. Sin embargo, el diseño de la capa ya está en §4, escrito antes de las relaciones. El autor ya sabe qué familias de perturbación usará. Por tanto, puede escribir relaciones que cubran exactamente esas familias. La secuencia en el documento ya revela la capa. Si el autor es honesto, no importa; pero el diseño busca proteger contra sesgos inconscientes. La medida barata: que las relaciones se escriban antes de leer la §4 o que otro las escriba. O que se seleccionen de un repositorio.

En cuanto a vía (a): solo ruidosos. ¿Tiene el problema contrario? Sí, recoge solo lo que ya es ruidoso, que es lo que no interesa porque el fallo que importa es silencioso. Pero no es un problema para la validez, sino para la utilidad. Si B se compone solo de ruidosos, la fase no contesta la pregunta. El piloto debe medir la proporción de silenciosos. Si es baja, se mata. El diseño ya lo contempla en F1.

Vía (c) humana sobre muestra: ¿qué tamaño de muestra la hace informativa, y qué pasa si la tasa base es del 1%? Si la tasa base de fallos es 1%, para detectar al menos un fallo con probabilidad 95% se necesitan n >= log(0.05)/log(0.99) ~ 299 ejecuciones. Para estimar la tasa con precisión, más. Una muestra de 200 no basta si la tasa es 1%. Pero la vía (c) no necesita detectar todos; es para acotar lo que (a) y (b) se dejan fuera. Si la tasa base es 1%, una muestra de 200 tiene ~86% de probabilidad de ver al menos uno (1 - 0.99^200 = 0.866). Para 95% se necesitan 299. Para una cota superior del 5% con confianza 95%, si no se ve ninguno en n, la regla de tres da n >= 59. Eso es factible. Pero la vía (c) es sobre una muestra aleatoria de ejecuciones; si la tasa es 1%, la mayoría serán limpios, y el curador tendrá que revisar muchas ejecuciones para encontrar un fallo. El coste es alto. Pero no es invalidante si se dimensiona.

¿Hay una cuarta vía? Posiblemente: usar un modelo de lenguaje como oráculo automático, pero congelado y sin acceso al estándar, como juez independiente. O usar discrepancia entre dos sistemas independientes (por ejemplo, el agente y un humano) como señal de fallo. O usar un oráculo basado en especificaciones formales. Pero el encargo pide si hay cuarta vía que no se me ocurre. Podríamos proponer: "diferencial entre el sistema y una implementación de referencia simple del contrato", pero eso es otra vez oráculo automático. O "oráculo de consenso entre múltiples modelos sobre la salida esperada", pero puede imprimir sesgo. Una cuarta vía real: **oráculo por discrepancia con el recurso FHIR resultante leído por un sistema externo** (por ejemplo, validar el Patient contra el perfil FHIR). Eso es metamórfico ampliado. O **oráculo de no regresión**: usar los 10 fallos conocidos como casos de prueba para asegurar que la capa es capaz de producirlos, lo que valida la capa. Pero no es para B.

Otra cuarta vía: **explotar la no identificabilidad declarada por la matriz de observabilidad**. La Fase 12 identificó dos operadores no identificables sin correr modelo. Se podría generar B justamente ahí: casos que la matriz dice no observables. Eso no es oráculo automático, sino selección de casos donde la evidencia no está en la traza. No es una vía de oráculo, sino de generación.

En el punto 2, la pregunta clave: "¿Basta publicar la proporción?" La respuesta: no basta, porque la proporción en sí es manipulable si el curador conoce la vía o si el autor de las relaciones y la capa es el mismo. Además, la proporción de B por vía no distingue entre "el fallo fue producido por la vía (a) y luego también viola una relación metamórfica". Un mismo fallo puede ser capturado por varias vías. El diseño dice "la proporción de B que viene de cada vía", pero no define si un fallo cuenta solo por la primera vía que lo detecta o por todas. Si un fallo silencioso viola una relación metamórfica y además produce un log de error, ¿de qué vía es? Eso puede inflar (b). Hay que definir una jerarquía o registro de vía de detección primaria.

**Sobre el endpoint residuo**

El primario es la nota del agente sobre el subconjunto que el autor de la regla actualizada declara no poder cubrir con una regla estática. Esto pone el endpoint en manos de una declaración humana. Preguntas:
- ¿Qué impide que declare de más o de menos? Si declara de más, incluye tipos difíciles para las reglas, y si el agente los detecta, la nota del agente en ese subconjunto es alta (buena para el agente). Si declara de menos, excluye tipos que la regla no cubre, haciendo que el residuo parezca pequeño y la actualizada parezca mejor. El autor de la regla actualizada tiene incentivos para declarar de más (hace su derrota más digna) y de menos (hace su script más potente). El diseño no especifica un protocolo que acote esto sin filtrarle nada. Se podría usar un mecanismo de incentivos: el autor no ve el agente, pero sabe que su declaración será auditada contra un panel independiente. O se puede hacer que la declaración sea preinscrita antes de que el autor vea B, y luego se verifique con un tercer codificador ciego. Pero el autor ve B para escribir las reglas, así que no es preinscrita.
- ¿Cambia si el autor es un modelo? Un modelo no tiene incentivos de dignidad, pero puede ser sensible al prompt y al contexto; puede alucinar cobertura. Habría que pedirle una lista con justificación por tipo, y medir su acuerdo con un humano.
- ¿Tiene su propia trampa, como el total o el DiD? Sí: el residuo declarado puede correlacionar con la dificultad percibida, no con la verdadera. Si el autor declara "no cubrible" para los tipos donde la regla falla, y el agente también falla ahí, la métrica es trivial. Es similar al DiD fabricado, pero al revés. El residuo es un subconjunto seleccionado por el comparador (el autor de la regla), no un subconjunto independiente. Es una forma de condicionar en el desenlace del comparador. La v1 ya fue rota por el oráculo de mecanicidad que condicionaba en el desenlace. Aquí el residuo es el equivalente: el autor declara no poder cubrir, lo cual es una función de su propia habilidad, no una propiedad del fallo. Es un "oráculo de mecanicidad" declarado por el autor. La medida barata: no usar el residuo como endpoint primario; en su lugar, usar el subconjunto de B que un panel independiente (o un tercer modelo) clasifica como no cubrible por reglas antes de ver al agente, o simplemente reportar la tasa sobre todo B. O, si se mantiene, preinscribir la lista de tipos no cubribles por un juez ciego que no sea el autor, y comparar con la declaración del autor.
- Si el residuo sale vacío: ¿es publicable o es un banco que no puede contestar? Si el autor de la regla actualizada declara que puede cubrir todos los tipos de B con reglas estáticas, entonces B no tiene residuo no cubrible, y la pregunta de si el agente detecta fallos que las reglas no alcanzan se queda sin subconjunto. Eso podría significar que la capa no produjo fallos genuinamente no reglables, o que el autor mintió. No es un resultado publicable sobre capacidad; es un resultado sobre el banco (no produjo el fenómeno). Se debe reportar como limitación del banco, no como victoria de las reglas.

**Sobre la simetría del prompt afinado**

El argumento de §5 es que el prompt afinado compró el contrato de transformación, que también recibe el autor de la regla actualizada. Pero hay una asimetría: el prompt afinado se optimizó contra el catálogo A, que incluye fallos específicos. El autor de la regla actualizada recibe el contrato, pero no el prompt afinado ni el catálogo A. Si el prompt afinado contiene ejemplos del catálogo A, entonces no es solo contrato. El texto dice "prompt afinado con huella" y "17.136 caracteres". No se muestra el contenido. La pista del usuario sugiere que "hay algo en esos 17.136 caracteres que no sea el contrato". Probablemente el prompt afinado incluye descripciones de los fallos de A, o heurísticas como "busca discrepancias entre MSH-18 y codificación real", que son específicas. El paso 29 muestra que en fallo silencioso el afinado mejora mucho, lo que sugiere que el afinado codifica conocimiento de fallos silenciosos de A, no solo contrato. Si B es emergente y no contiene esos fallos, el prompt afinado podría no transferir, o podría transferir sesgo. La simetría no es real: el autor de la regla actualizada recibe el contrato, pero no recibe el conocimiento empírico de A. El prompt afinado es un brazo con ventaja indebida porque fue entrenado/afinado con datos que el otro brazo no tiene. Para restaurar simetría, habría que dar al autor de la regla actualizada también el catálogo A o al menos el resumen de fallos de A, o usar el prompt genérico como primario. O congelar el prompt afinado pero auditarlo y declarar qué contiene. Medida barata: comparar el prompt afinado con el genérico en B y reportar la diferencia por clase; si la ventaja persiste solo en tipos similares a A, es contaminación.

Además, "el agente está congelado desde la Fase 12 con un prompt afinado durante un mes contra el catálogo A". Eso significa que el agente fue optimizado para A. Si B es emergente, la transferencia es la pregunta. Si el prompt afinado contiene información específica de A, entonces no es una medida justa de "capacidad" sino de "transferencia de A a B", que es una pregunta válida pero distinta. El diseño lo reconoce al incluir prompt genérico, pero el primario sigue siendo el afinado. El primario debería ser el prompt genérico porque es el que no tiene ventaja de A. O al menos reportar ambos en portada, no solo el afinado.

**Sobre el tamaño**

La v2 dice que N y k salen de la capa. Pregunta: cómo preinscribir un análisis cuyo tamaño se desconoce sin dejar puerta abierta a mirar primero y decidir después. La §8 fija N mínimo pero deja el número a 🧑. Se pide regla que lo cierre de verdad. Una regla podría ser: "El primario se publica solo si N >= 10 y cada familia contribuye al menos 2 tipos, y k medio >= 3. En caso contrario, se reporta como descriptivo y se publica el N efectivo." O mejor: preinscribir un protocolo de decisión basado en la distribución observada en el piloto, con umbrales numéricos fijados antes de ver B. Por ejemplo, "si el piloto produce >= 8 silenciosos de al menos 3 familias, se procede; si no, se detiene." Eso se puede firmar antes. El número N mínimo se puede fijar por criterio de potencia: para detectar una tasa del 25% con potencia 80% y alpha 5%, se necesitan al menos 7 tipos. Pero no es trivial. La clave es evitar la decisión post hoc. Se puede preinscribir una función de decisión que tome como entrada la distribución de tipos y produzca "publicable como primario" o "descriptivo", sin intervención humana.

**Sobre los pasos baratos**

Falta un paso: auditoría del prompt afinado y del puntuador antes de montar la capa. Sobra quizás el paso 4 (inductor calibrado en A) porque no es necesario para decidir si la fase es viable; se puede hacer después. El más probable de matar la fase es el paso 2/3 (piloto y distribución). Se puede adelantar haciendo un piloto de humo con una fracción de las relaciones metamórficas y una sola familia, para ver si hay silenciosos. O incluso usar los datos históricos de la bitácora como piloto: ya hay 10 fallos, de los cuales 4 son de carga/entorno, etc. Eso sugiere que la capa producirá silenciosos, pero no es garantía.

Además, el paso 1 (relaciones metamórficas) depende del autor, que es el mismo que diseña la capa. Si se adelanta el piloto, las relaciones ya deben estar selladas. Por tanto, no se puede adelantar más.

**Séptimo modo de fallo (F7)**

Basado en las pistas, creo que el séptimo modo es:

**El puntuador es un mando no clavado.** El diseño clava muchos mandos, pero el puntuador, que decide qué es detección y qué es falsa alarma, se hereda de la Fase 12 sin auditar su calibración. Si el puntuador fue ajustado (umbrales, clases, reglas de coincidencia) en A, imprime la firma de A en la evaluación de B. El agente afinado y el puntuador comparten historia: ambos se desarrollaron juntos en la Fase 12. Por tanto, la evaluación no es independiente. Es el equivalente al "oráculo es un brazo" pero en la métrica. Medida barata: congelar el puntuador con huella, publicar su código y autopruebas, y ejecutar una auditoría de umbrales contra un subconjunto de B etiquetado por humanos ciegos antes de aceptar resultados. O mejor: que el puntuador sea reescrito por un tercero a partir del contrato, sin ver A. Porque el puntuador actual fue validado contra A, y su criterio de "detección" puede estar sobreajustado a las firmas de A.

Otra posibilidad: **el autor del laboratorio es el mismo que escribe el estándar, las relaciones, la capa, el puntuador y el curador no es independiente**. Pero eso es más general.

El usuario da pistas: "el puntuador sigue siendo mío". Eso es una pista fuerte. Creo que F7 debe ser sobre el puntuador.

También podría ser: "la definición de 'detección propia' (mitad o más de instancias) es un mando discrecional que favorece al agente porque requiere múltiples instancias, lo que reduce la varianza pero puede excluir tipos con pocas instancias." No es tan grave.

O "la matriz de observabilidad usada en Fase 12 para identificar no identificables no se actualiza para B; si B incluye tipos no identificables, la evidencia no está en la traza y el agente no puede detectarlos, pero eso no se mide." Eso podría ser un fallo: el diseño no incorpora la matriz de observabilidad para clasificar los tipos de B en identificables/no identificables. Si B contiene tipos no observables, la tasa del agente bajará, pero no porque no sea capaz, sino porque la información no existe. La Fase 12 ya mostró que dos operadores no identificables eran exactamente los que el script fallaba. En B emergente, puede haber tipos no observables. El diseño no los separa. Eso es un fallo serio: la pregunta "¿detecta el modelo?" no distingue entre fallos con evidencia en la traza y sin ella. Para ser justo, habría que clasificar cada tipo de B según su observabilidad (usando la matriz o un panel) y reportar por separado. Si no, el agente puede fallar en tipos que ninguna regla ni modelo podría detectar, y se interpretará como falta de capacidad. Medida barata: aplicar la matriz de observabilidad a B (o una versión extendida) antes de curar, y preinscribir que los tipos no observables se reporten aparte. Esta podría ser una buena rotura.

El encargo menciona: "el agente funciona... y aun así no hace falta... los dos que falla son exactamente los dos que la matriz de observabilidad había declarado no identificables sin correr ningún modelo." Eso es contexto de Fase 12. En la v2, no se menciona cómo se maneja la observabilidad en B. Podría ser un fallo: la v2 repite el mismo error al no medir la observabilidad de los tipos emergentes. Si el agente falla en un tipo de B, no se sabe si es por falta de capacidad o por falta de información. La v2 debería incluir un análisis de observabilidad por tipo. El séptimo modo de fallo podría ser: **"B emergente contiene fallos no observables y el diseño no los separa, así que el endpoint confunde capacidad con observabilidad."** Medida barata: antes de curar, para cada candidato a fallo, registrar si la evidencia discriminante está en la traza (o en el estado interno) y clasificar; reportar la tasa del agente solo sobre los observables, o al menos desglosar. Eso es barato y no requiere curador.

¿Cuál es más plausible? El usuario da pistas: "las relaciones metamórficas las escribo yo, del estándar; el piloto lo corro yo; el curador ve..., nada más; el agente está congelado..., y el puntuador sigue siendo mío." La última cláusula "y el puntuador sigue siendo mío" es intrigante. En §6, la tabla de mandos incluye "cuál es el primario", "el prompt", "detección propia", pero no el puntuador. El puntuador es un mando discrecional no clavado. Además, en §5 los números del paso 29 dependen del puntuador. Si el puntuador está sesgado hacia el agente, los números están inflados. La Fase 12 ya tenía puntuador con 16 autopruebas, pero no se dice que sea ciego al agente. En Fases anteriores, es común que el puntuador se desarrolle junto con el agente. Por tanto, F7: **el puntuador no es un instrumento independiente; fue calibrado en A y puede trasladar la firma de A a la evaluación de B.** Medida barata: antes de contratar curador, congelar el puntuador, publicar su código y umbrales, y hacer una auditoría de sus autopruebas para verificar que no incluye casos de A. O mejor: ejecutar el puntuador sobre un conjunto de casos sintéticos generados por un tercero a partir del contrato y comparar con juicio humano. Si el puntuador está calibrado para A, se detectará.

Otra pista: el punto 4 pregunta específicamente sobre el prompt afinado y si hay algo en los 17.136 caracteres que no sea contrato. El punto 6 pregunta sobre pasos baratos. La pista del puntuador es directa. Creo que F7 debe ser sobre el puntuador.

También podría ser: "el piloto de 200 ejecuciones no es suficiente para estimar la tasa de silenciosos si es baja." Eso es F1, ya cubierto. No es nuevo.

Vamos a estructurar la respuesta.

Primero, señalar errores de razonamiento si los hay. ¿Hay algún error? La v2 dice "Con un B emergente, la regla actualizada ya no vale ≈ 1 por construcción." Eso es correcto en teoría, pero no suficiente. El error de razonamiento principal es asumir que la emergencia elimina la invertibilidad. Un fallo emergente, una vez observado y curado, es un tipo definido por sus características. Si el curador lo etiqueta, el autor de la regla actualizada puede inspeccionar las instancias y escribir una regla estática a posteriori. La invertibilidad no depende de si fue diseñado o emergente, sino de si la evidencia está en la traza. La v2 dice "Puede haber fallos cuya evidencia discriminante no esté en la traza..." pero no garantiza que los haya. Si la mayoría de los fallos emergentes tienen firma en la traza, la regla actualizada volverá a valer ≈1. La emergencia no rompe la invertibilidad por sí sola; solo cambia la probabilidad de que haya fallos no invertibles. El diseño no mide la invertibilidad de B antes de lanzar la fase. Ese es un error de razonamiento: confundir "no diseñado" con "no invertible". Un fallo no diseñado puede ser trivialmente invertible una vez visto. El paso 29 usó v3-invariante solo contrato publicado +0.705, pero sobre A declarativo. En B emergente, la regla actualizada podría seguir siendo muy alta si los fallos son superficiales. La v2 necesita un paso barato para estimar la cobertura de reglas estáticas sobre B antes de comprometer el endpoint. Eso es justamente el residuo, pero el residuo se declara después de curar y después de que el autor ve B. Falta una medición a priori.

Por tanto, el error de razonamiento: "la emergencia por sí misma no evita la invertibilidad; solo la hace incierta." La v2 lo reconoce parcialmente en §2, pero luego construye el endpoint sobre el residuo declarado, que es otra forma de condicionar en el desenlace del comparador. Es decir, la v2 reintroduce el mismo problema que mató la v1: el subconjunto sobre el que se evalúa al agente lo define el comparador (el autor de la regla actualizada), no un criterio independiente. Eso es similar a "el oráculo es un brazo" pero con el residuo. Debo señalarlo.

Entonces, responderé:

- Antes de todo, señalar el error de razonamiento: la emergencia no garantiza no invertibilidad; y el residuo declarado es un mando que condiciona el endpoint en el desenlace del comparador, repitiendo la rotura de la v1.
- Luego, el séptimo modo de fallo: probablemente el puntuador como mando no clavado, o la falta de medición de observabilidad/invertibilidad de B. Voy a elegir el más fuerte. El encargo pide "el séptimo modo de fallo" y pide "la medida barata que lo destaparía antes de contratar al curador". Puedo nombrar dos si es necesario, pero uno principal.

Revisemos la lista F1-F6: F1 solo ruidosos, F2 misma familia, F3 oráculo metamórfico imprime firma, F4 contaminación diez conocidos, F5 curador no ciego, F6 el que no sé ver. ¿Cuál no está? Falta el sesgo del puntuador. Así que F7: el puntuador, heredado de Fase 12, fue calibrado con A y puede trasladar la firma de A a la evaluación de B, inflando o desinflando la tasa del agente. Medida barata: auditoría del puntuador y sus umbrales contra un conjunto de casos B etiquetados por un juez ciego, o simplemente publicar la matriz de confusión del puntuador en A y verificar que no usa características específicas de A. Pero como B no existe aún, se puede auditar el código y las autopruebas, y preinscribir un umbral fijo. Otra medida barata: hacer que el puntuador sea reimplementado por un tercero solo con el contrato, sin ver A, antes de la fase. Eso cuesta poco comparado con la curación.

También mencionaré que el puntuador es un mando discrecional que en §6 no se clava, y que su dueño es el mismo que escribe las relaciones y la capa. Eso es un conflicto.

Ahora, abordar cada punto del encargo en orden.

**1. El séptimo modo de fallo**

F7: El puntuador es un mando no clavado y contaminado por A. Medida barata: auditoría del puntuador antes de curar, o reimplementación a ciegas. Si no se puede, preinscribir que cualquier resultado donde el puntuador muestre sesgo hacia el agente se reporte como no válido.

**2. ¿Es emergencia de verdad o contrato con otro nombre?**

Responder: No basta con publicar la proporción. La emergencia es real solo para vía (a) y (c) en parte, pero la vía (b) es exactamente el contrato leído al revés. La distinción entre relaciones metamórficas y operadores de mutación es falsa si el autor de las relaciones es el mismo que diseña la capa. Se necesita independencia: que las relaciones se escriban antes de ver la capa, o por un tercero. La vía (a) solo captura ruidosos, que no interesan; pero sirve como control de que B no es solo contrato. La vía (c) es la única insesgada para silenciosos, pero con tasa base 1% se necesitan al menos 300 ejecuciones para tener 95% de ver un fallo, y la muestra debe ser aleatoria sobre todas las ejecuciones, no solo las sospechosas. La cuarta vía: usar un oráculo de no observabilidad (matriz de observabilidad) para generar/evaluar casos sin depender del contrato; o usar discrepancia entre dos implementaciones independientes del contrato (pero eso es metamórfico). Propongo como cuarta vía: **oráculo por intervención**: provocar una condición que el contrato dice que debe producir un efecto observable, y comprobar si el efecto ocurre. Eso es similar a metamórfico pero basado en causalidad, no en invariancia. Por ejemplo, rotar credencial debe producir 401; apagar FHIR debe producir AE. Eso no es metamórfico puro, es funcional. El diseño ya lo tiene en vía (a) parcialmente (caídas, etc.) pero no lo formaliza. Otra cuarta vía: **usar el propio agente congelado como generador de candidatos a fallo** (sus falsas alarmas en limpios pueden ser fallos reales no etiquetados). Pero eso sesga.

**3. El endpoint residuo**

Explicar que el residuo declarado es un mando que repite el error de la v1: condiciona el endpoint en el desenlace del comparador. El autor de la regla actualizada puede declarar de más o de menos. No hay protocolo que lo acote sin filtrar. Si el autor es un modelo, el sesgo es diferente: puede alucinar cobertura o seguir instrucciones del prompt; se necesitaría un humano para validar. La trampa: es un "oráculo de mecanicidad" declarado, no medido. Si el residuo sale vacío, es un resultado sobre el banco, no sobre el modelo. Propuesta de cambio mínimo: el subconjunto de B no cubrible por reglas debe ser determinado por un juez ciego (o un panel) que no sea el autor de la regla, antes de que el autor vea B, o al menos antes de que se le permita declarar. O preinscribir que el primario sea la tasa sobre todo B, no sobre el residuo, y el residuo sea secundario.

**4. Simetría del prompt afinado**

No es simetría real. El prompt afinado fue optimizado contra A, por lo que contiene información empírica que el autor de la regla actualizada no tiene. El contrato es compartido, pero el afinado puede incluir ejemplos o heurísticas de A. El paso 29 muestra ventaja en fallo silencioso, que es exactamente la clase donde el afinado pudo memorizar firmas de A. Para restaurar simetría, se debería usar el prompt genérico como primario, o dar al autor de la regla actualizada el mismo prompt afinado (lo cual no tiene sentido), o auditar los 17.136 caracteres y declarar si contienen información de A. Si contienen, el primario está contaminado. Medida barata: leer el prompt afinado (pedirlo) y compararlo con el genérico; buscar tokens específicos de A.

**5. Tamaño**

Preinscribir una regla de decisión basada en umbrales numéricos antes de ver B. Por ejemplo: "El primario se publica si N >= 8 tipos, con al menos 2 familias representadas y k medio >= 3; si no, descriptivo." O mejor, una función de utilidad que no dependa de los datos. La regla debe fijarse en el protocolo, no dejarse a 🧑. Se puede usar un comité de preinscripción. La clave es que la decisión se tome sin ver los resultados.

**6. Pasos baratos**

Falta un paso 0: auditoría del puntuador y del prompt afinado. Sobra el paso 4 (inductor) en la fase temprana; se puede posponer. El más probable de matar la fase es el paso 2/3 (piloto y distribución). Se puede adelantar haciendo un piloto de humo con una sola familia y unas pocas relaciones metamórficas, o usando los datos históricos de la bitácora como validación de la capa. Pero el paso 1 ya es escribir relaciones; no se puede adelantar más sin ellas. En todo caso, se puede hacer un piloto mínimo con las relaciones ya existentes de la Fase 12 (si las hay) antes de escribir todas las nuevas.

Ahora redactar la respuesta en Markdown, concreta, sin relleno. Debe ser larga pero técnica. Primero el error de razonamiento. Luego las respuestas por puntos.

Debo recordar que el encargo pide no rediseñar entero, sino romper y proponer cambios mínimos. Seré directo.

Voy a redactar.

**Error de razonamiento principal:**

"B por emergencia no elimina la invertibilidad. Un fallo no diseñado, una vez curado, es un tipo definido por sus trazas; si la evidencia está en la traza, una regla escrita a posteriori lo invierte. La emergencia solo hace incierta la proporción de no invertibles. El diseño lo intuye pero no lo mide antes de comprometer el endpoint: el residuo declarado es exactamente el mando que condiciona el endpoint en el desenlace del comparador, repitiendo la rotura de la v1."

**F7:**

"El puntuador es un mando no clavado. Heredado de la Fase 12, fue calibrado con A. Si sus umbrales, reglas de coincidencia o clases se optimizaron para A, imprime la firma de A en la evaluación de B. El agente afinado y el puntuador comparten historia; no hay independencia entre el instrumento y el objeto medido. Medida barata: antes de curar, congelar el puntuador con huella, publicar código y umbrales, y ejecutar una auditoría de calibración sobre un conjunto de casos sintéticos derivados exclusivamente del contrato por un tercero. Si la concordancia con un juez humano ciego baja del umbral, el puntuador no es válido para B."

Luego, en el punto 2, detallar.

Necesito ser cuidadoso con las cifras de tasa base 1%. Para vía (c), si la tasa base es 1%, la probabilidad de no ver ningún fallo en n es 0.99^n. Para 95% de ver al menos uno, n = ceil(log(0.05)/log(0.99)) = 299. Para una cota superior de 3/n con 95% si no se ve ninguno, n=100 da cota 3%, n=200 da 1.5%. Si se quiere estimar una tasa con precisión ±1% con confianza 95%, se necesitan ~9604 ejecuciones. Pero la vía (c) no necesita estimar con precisión; necesita acotar lo que (a) y (b) se dejan. Una muestra de 300 ejecuciones aleatorias es factible. Pero si la tasa es 1%, en 300 ejecuciones se esperan 3 fallos; el curador debe revisar 300 ejecuciones, lo cual es caro pero no imposible. El diseño debe presupuestar eso.

Cuarta vía: "oráculo por intervención causal" — provocar condiciones donde el contrato exige una respuesta, y verificar si ocurre. No es metamórfico porque no compara dos ejecuciones equivalentes, sino que comprueba una propiedad funcional. Ejemplos: apagar FHIR debe producir AE en un tiempo límite; rotar credencial debe producir 401; PoolSize=1 con N conexiones debe rechazar con un código específico. Eso es vía (a) formalizada. También se puede usar "oráculo de no observabilidad": casos donde la matriz de observabilidad dice que la traza no tiene evidencia, generados a propósito para medir si el agente extrae algo. Eso es generación, no oráculo.

Para el punto 3, el cambio mínimo: eliminar el residuo declarado como primario; el primario debe ser la tasa sobre todo B curado, con el residuo reportado aparte. Si se mantiene, preinscribir que el subconjunto no cubrible lo determine un juez ciego que no sea el autor, y que la declaración del autor se compare con la del juez; si hay discrepancia, se reporta.

Para el punto 4, decir que no es simetría. El prompt afinado es un brazo con información de A. El autor de la regla actualizada recibe el contrato, no los ejemplos de A. Si el afinado contiene heurísticas derivadas de A, es ventaja indebida. Proponer: usar el prompt genérico como primario, o congelar el afinado y publicar su contenido para que el autor de la regla actualizada también lo reciba (aunque eso no tiene sentido porque es un modelo, no una persona). Mejor: reportar ambos en portada y preinscribir que si la ventaja del afinado sobre el genérico en B se concentra en tipos similares a A, se declara contaminación y el primario pasa al genérico.

Para el punto 5, regla concreta: "N mínimo ≥ 10, al menos 3 familias con ≥2 tipos cada una, k medio ≥ 3, y ningún tipo con k=1 entra al primario. Si no, se reporta descriptivo." Y preinscribir una función de decisión en el protocolo, no dejarla a 🧑 después de ver B.

Para el punto 6, decir que falta auditoría del puntuador y del prompt afinado; sobra el inductor antes del piloto; el paso más probable de matar es el piloto; se puede adelantar un piloto mínimo con 50 ejecuciones y 2 relaciones metamórficas para evaluar F1, antes de escribir todas las relaciones.

Ahora, redactar en Markdown.

Debo ajustar el tono: consultor senior, concreto, sin relleno. Usar secciones.

Incluiré referencias a las secciones del documento v2.

Voy a escribir la respuesta completa.

**Posible F7 alternativo:** "La v2 no mide la observabilidad de los tipos de B." ¿Debería incluirlo como parte del séptimo o como error de razonamiento? El error de razonamiento ya cubre la invertibilidad. Puedo mencionar que el diseño no separa tipos observables de no observables, y eso es parte del mismo problema. Pero el F7 específico del puntuador es más novedoso y encaja con las pistas.

El encargo dice: "Pistas de dónde mirar: ... y el puntuador sigue siendo mío." Eso es muy directo. Así que F7 será el puntuador.

Además, en la tabla de mandos de §6, no se clava el puntuador. Eso refuerza.

**Sobre el punto 2, la cuarta vía:** Propondré "oráculo por intervención causal" y "oráculo de no observabilidad". Pero debo asegurarme de que es una vía de oráculo, no de generación. La vía (a) es sin oráculo (caídas, etc.). La vía (b) es metamórfico. La vía (c) es humano. Cuarta vía: **oráculo funcional de contrato** — comprobar explícitamente resultados esperados para entradas que el contrato especifica (p.ej., si FHIR responde 201, el recurso debe existir; si MSH-10 duplicado, debe rechazarse con error). Eso es similar a (b) pero no es metamórfico; es un test de contrato directo. Podría imprimir firma, así que no es insesgado, pero es barato y cubre silenciosos que no son de invariancia. La incluiría como cuarta vía, con su sesgo declarado.

Pero el encargo pregunta: "¿Hay una cuarta vía que no se me ocurre?" Debo ofrecerla. Sí, la intervención causal o test funcional.

**Sobre el tamaño de muestra vía (c):** Calcularé con precisión: si tasa base p=0.01, n=200 => prob de al menos uno = 1 - (0.99)^200 = 0.866. Para 95% n=299. Para una cota superior del 5% si no se ve ninguno, n=59 (regla de tres: 3/59=5.1%). Pero para que la muestra sea informativa sobre la tasa de silenciosos, no basta ver uno; se necesita estimar. Si se quiere un intervalo de confianza para p con ancho ±0.005 (0.5%), n ~ 1521. Si ±0.01, n ~ 380. Ajustar: n = z^2 p(1-p)/E^2; para z=1.96, p=0.01, E=0.01 => n = 3.84*0.0099/0.0001 = 380. Para E=0.005 => n=1521. Eso es para estimar la tasa, no solo detectar. La vía (c) es para acotar, así que una muestra de 300-500 podría bastar. El diseño debe preinscribir n para vía (c) basado en la tasa base esperada del piloto.

**Sobre si el autor declara de más o de menos:** Propondré protocolo de "declaración preinscrita por un juez ciego" y "auditoría de la declaración" con penalización si miente. Por ejemplo, el autor puede ser incentivado alineando su pago con la exactitud de su declaración, no con el resultado del agente. Si declara de menos, el juez lo detecta y se reporta; si declara de más, el residuo incluye tipos que él no pudo cubrir, pero el juez verificará que realmente no son cubribles con reglas. El protocolo debe ser ciego: el autor no sabe qué tipos son difíciles para el agente. Eso es factible si el autor no ve los resultados del agente.

**Sobre si el autor es modelo:** Un modelo puede ser auditado de forma determinista, pero puede alucinar. Se le puede pedir que genere una lista con justificación y luego un humano la valida. La diferencia es que no hay incentivo de dignidad, pero sí sensibilidad al prompt; hay que fijar el prompt con huella y preinscribir la temperatura 0.

**Sobre residuo vacío:** Es un resultado sobre el banco, no publicable como capacidad. Debe reportarse como "la capa no produjo fallos no reglables".

Ahora, escribir.

Debo incluir el error de razonamiento al inicio, antes de las respuestas, como pide el encargo: "Cuando el encargo contiene un error de razonamiento, lo dices antes que nada."

Redacto:

---

**Error de razonamiento en la v2 antes de empezar**

La v2 asume que "emergente" implica "no invertible". No es cierto. Un fallo no diseñado, una vez curado y con sus trazas disponibles, es un tipo definido por sus características observables; si la evidencia discriminante está en la traza, un autor de reglas puede escribir una regla estática a posteriori que lo detecte. La emergencia no elimina la invertibilidad; solo la hace incierta. El diseño lo reconoce parcialmente (§2) pero luego coloca el primario sobre el residuo declarado por el autor de la regla actualizada, lo que reintroduce la rotura de la v1: condicionar el endpoint en el desenlace del comparador. El residuo declarado es el nuevo oráculo de mecanicidad, pero ahora declarado por el propio comparador.

---

Luego, secciones.

**1. F7**

**F7 · El puntuador es un mando no clavado y contaminado por A.**
El puntuador decide qué es detección y qué es falsa alarma. Se hereda de la Fase 12, donde fue calibrado con el catálogo A. No se audita ni se clava en la tabla de mandos de §6. Si sus umbrales, reglas de coincidencia o clases se optimizaron para A, imprimirá la firma de A en la evaluación de B. El agente afinado y el puntuador comparten historia; no hay independencia entre el instrumento y el objeto. Medida barata: antes de curar, congelar el puntuador con huella, publicar código y umbrales, y pasarlo por una auditoría de calibración sobre un conjunto sintético derivado exclusivamente del contrato por un tercero, con juez humano ciego. Si la concordancia baja del 90%, el puntuador no es válido para B.

**2. Emergencia vs contrato**

No basta publicar la proporción. La vía (b) es exactamente el contrato leído al revés si las relaciones las escribe la misma persona que diseña la capa. La secuencia de §9 no salva esto porque el diseño de la capa ya está en §4, visible antes de escribir las relaciones. Para que la emergencia sea real, las relaciones deben ser escritas por alguien que no vea la capa, o derivarse de un estándar versionado con una herramienta independiente. La vía (a) solo captura ruidosos; no es un problema de validez sino de utilidad: si todo B es ruidoso, la fase no contesta. La vía (c) es la única insesgada para silenciosos, pero si la tasa base es 1%, se necesitan ~299 ejecuciones para tener 95% de ver al menos un fallo, y ~380-1500 para estimar la tasa con precisión ±1%-±0.5%. La cuarta vía: oráculo funcional de contrato (intervención causal): provocar condiciones cuyo resultado el contrato especifica (rotar credencial -> 401, apagar FHIR -> AE, duplicar MSH-10 -> rechazo) y comprobar el resultado. Es más rico que (a) y distinto de (b), aunque imprime firma; se puede sellar y reportar su cuota.

**3. Endpoint residuo**

El residuo declarado es el error de la v1 con otro nombre. El autor puede declarar de más (hace su derrota más digna) o de menos (hace su script más potente). No hay protocolo que lo acote sin filtrar. Si el autor es un modelo, el sesgo es de prompt y puede alucinar cobertura. La trampa: es un oráculo de mecanicidad declarado, no medido. Si sale vacío, es un resultado sobre el banco, no publicable. Cambio mínimo: el primario debe ser la tasa del agente sobre todo B curado; el residuo se reporta como secundario y lo determina un juez ciego que no sea el autor, antes de que el autor declare. O preinscribir que si la declaración del autor difiere del juez, se reporta la discrepancia y se invalida el residuo.

**4. Simetría del prompt afinado**

No es simetría real. El prompt afinado se optimizó contra A; el autor de la regla actualizada no recibe ese conocimiento empírico. El contrato es compartido, pero el afinado puede contener heurísticas derivadas de A. Los números del paso 29 muestran que la ventaja se concentra en fallo silencioso, exactamente donde el afinado pudo memorizar firmas de A. Medida barata: pedir el texto del prompt afinado y auditarlo; si contiene tokens de A (nombres de tipos, códigos de error, etc.), el primario está contaminado. Cambio mínimo: usar el prompt genérico como primario, o reportar ambos en portada y preinscribir que si la ventaja del afinado en B se concentra en tipos similares a A, se declara contaminación.

**5. Tamaño**

Preinscribir una regla numérica antes de ver B, no dejarla a 🧑. Propuesta: primario publicable si N >= 10 tipos, al menos 3 familias con >= 2 tipos cada una, k medio >= 3, y ningún tipo con k=1 entra al primario. Si no, descriptivo. Esa regla se firma con huella.

**6. Pasos baratos**

Falta un paso 0: auditoría del puntuador y del prompt afinado. Sobra el paso 4 (inductor) antes del piloto; puede posponerse. El más probable de matar la fase es el paso 2/3 (piloto y distribución). Se puede adelantar un piloto de humo con 50 ejecuciones y 2 relaciones metamórficas para evaluar F1 antes de escribir todas las relaciones.

---

Eso es el esqueleto. Ahora expandir con más detalle y justificación técnica.

Necesito asegurarme de que no propongo un B declarado (no lo hago). Las propuestas son cambios mínimos: auditoría, cegamiento, cambiar primario, preinscripción numérica.

Debo incluir el control de contaminación: si necesito ver el prompt afinado, lo pido explícitamente. En la respuesta, en el punto 4, diré "Para confirmarlo habría que pedir el texto del prompt afinado; no lo tengo, pero el riesgo es suficiente para no aceptar la simetría sin evidencia."

También debo mencionar que el puntuador no es ciego al agente? En realidad el puntuador es código, pero fue escrito por el mismo autor. La independencia se logra con auditoría.

Incluiré una sección final de "Cambios mínimos priorizados".

Voy a redactar en Markdown.

Además, debo responder a la pregunta "¿Basta?" con un "No basta" y justificar.

Sobre la vía (c) tamaño de muestra: daré números concretos.

La pregunta "¿Qué tamaño de muestra la hace informativa, y qué pasa si la tasa base es del 1 %?" Responderé:

- Para detectar al menos un fallo con 95% de confianza, n = ceil(log(0.05)/log(0.99)) = 299.
- Para estimar la tasa de fallos con precisión ±1% con confianza 95%, n ~ 380.
- Para una cota superior del 5% si no se ve ninguno, n = 59.
- Si la tasa es 1%, una muestra de 200 tiene 86.6% de ver al menos uno; es insuficiente para los objetivos del piloto si se quiere descartar F1 con seguridad.
- El diseño debe preinscribir el n de la vía (c) en función de la tasa base observada en el piloto, no dejarlo abierto.

Sobre la cuarta vía: "oráculo funcional de contrato" y "oráculo de no observabilidad". Explicaré.

**Sobre el endpoint residuo, protocolo para acotar sin filtrar:**

Propongo un protocolo de "doble declaración": antes de que el autor de la regla actualizada vea B, un juez ciego (o un panel) examina los tipos curados y declara cuáles son cubribles por regla estática. Luego el autor escribe sus reglas y hace su propia declaración. Se comparan. Si difieren, se reporta. El autor no ve la declaración del juez. Eso acota sin filtrarle nada, porque el juez no sabe qué reglas escribirá el autor. Es factible con cegamiento.

Otra opción: incentivos: el autor recibe una penalización por cada tipo que declare "no cubrible" y que el juez determine que era cubrible con una regla simple, y por cada tipo que declare "cubrible" y que el juez determine que no lo era. Eso alinea incentivos.

Si el autor es un modelo, se le puede pedir que genere una lista con justificación, y un humano la valida a ciegas. La temperatura 0 y el prompt con huella.

**Sobre residuo vacío:** Si el residuo sale vacío, es un hallazgo sobre el banco: no produjo fallos no reglables. No es publicable como "el agente no aporta", sino "la capa no hizo emerger el fenómeno". Se debe reportar como limitación.

**Sobre la simetría del prompt afinado:** El argumento de que el mes compró el contrato es insuficiente. El paso 29 no separa conocimiento del contrato de conocimiento de A. Los 17.136 caracteres pueden incluir ejemplos de A. La ventaja en fallo silencioso sugiere que el afinado capturó la firma de los fallos silenciosos de A. Si B es emergente y no comparte esa firma, la ventaja puede desaparecer. Si comparte, es contaminación. Medida: pedir el prompt afinado y compararlo con el genérico; buscar términos específicos de A. Si no se puede, usar el genérico como primario.

**Sobre el tamaño:** La regla que propongo: N mínimo 10, al menos 3 familias con 2 tipos cada una, k medio >= 3. Eso es concreto. Pero debo justificar por qué 10 y no otro número: con 10 tipos se puede estimar una tasa con intervalo de confianza razonable; con menos, la macro por tipo es ruidosa. La Fase 12 usó 18 operadores; para B emergente, 10 es un mínimo conservador. Pero puedo dejarlo como ejemplo, diciendo que lo importante es preinscribir la regla antes de ver B.

**Sobre los pasos baratos:** El paso más probable de matar la fase es el piloto (paso 2/3). Se puede adelantar un piloto de humo: 50 ejecuciones dirigidas a las familias que históricamente dieron silenciosos (codificación, carga) y 2-3 relaciones metamórficas críticas. Si no aparece ningún silencioso, se detiene. Eso ahorra escribir todas las relaciones y montar toda la capa.

**Control de contaminación:** Al final, mencionar que para confirmar el riesgo del prompt afinado y del puntuador se necesita verlos, y pido acceso al prompt afinado y al código del puntuador para auditar.

Ahora, redactar la respuesta final.

Me aseguraré de que no sea demasiado extensa, pero el encargo pide concreción técnica. Unas 2000-3000 palabras está bien.

Voy a escribir.