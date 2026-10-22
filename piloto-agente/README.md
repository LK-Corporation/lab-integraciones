# Piloto: un agente que se apoya en un verificador para arreglar circuitos de integración

Segundo estudio del laboratorio (12 y 13-oct-2026). El primero, en [`INFORME.md`](../INFORME.md), medía si un modelo **tría**
fallos mejor que una lectura mecánica, y un script de expresiones regulares lo batía. Este mide otra cosa: si un agente con
modelo, guiado por el veredicto de un **verificador determinista**, **localiza la causa en el código y la arregla** mejor que una
búsqueda sin modelo que recibe exactamente lo mismo.

## El resultado, en las dos frases preinscritas

> **Con la ampliación (n = 11 + 7), el agente funciona:**
> - localiza la causa entre sus tres primeras propuestas en **17 de 18** fallos reales (IC95 0,74-0,99; al azar, ≈ 0,02);
> - arregla sin romper nada en **8,5 de 18** (IC95 0,27-0,69);
> - no da falsas alarmas en los casos limpios.
>
> **Frente a la búsqueda sin modelo, aporta, pero por acumulación:**
> - el combinado de dos etapas da Z = 1,92 y Δ +0,44 (IC 0,17-0,72);
> - **ninguna de las dos etapas lo consigue sola**: el piloto da Δ +0,36 (p 0,22) y los casos nuevos Δ +0,57 (p 0,125);
> - **el «aporta» desaparece** si se quitan los casos en que el propio verificador declara una pista del fallo, y también si
>   se quitan los fallos que el circuito tiene a propósito.

Los resultados completos, con sus límites: [`RESULTADO-AG2-AG3.md`](RESULTADO-AG2-AG3.md) (el piloto) y
[`RESULTADO-AMP.md`](RESULTADO-AMP.md) (la ampliación, última etapa).

## Lo que sacamos en claro

1. **Arreglar no es triar.** En la fase anterior, clasificar fallos era trabajo mecánico y un script ganaba. Aquí la referencia
   sin modelo **localiza** bastante (la mitad de los casos), pero **no arregla ninguno**: sus plantillas de parche no casaron en
   ninguno de los 18 casos. El agente arregla la mitad, con colateral casi nulo. Los 5 parches aceptados que se sortearon para
   leerlos a mano corrigen la causa según Jev, un modelo de decisión calibrada; ninguno engaña al juez.
2. **La ventaja al localizar es real pero estrecha, y depende de dónde se mire.**
   - En el piloto estaba en los fallos históricos (5/5 frente a 1/5). En la ampliación está en defectos de configuración y de
     comprobaciones ausentes, donde la referencia es débil por construcción.
   - No sobrevive sin las pistas que el verificador declara. Es lo que más importa para quien quiera usar un agente así:
     **el agente lee bien lo que el juez dice**, y ahí está buena parte de su ventaja.
3. **El agente casi no usa al verificador como oráculo.** Puede preguntarle cuanto quiera, y en 52 tiradas del piloto lo hizo en
   7. Lo que se ha medido es lectura de código guiada por el veredicto escrito, no prueba y error contra el juez.
4. **El método aguantó porque se rompió por escrito.** Las puertas, los controles y los sellos cazaron, antes o durante la
   medida:
   - **regresiones sin un solo mensaje aceptado**, donde un parche que rompe el AA no tiene dónde verse;
   - **una firma que no es estable** en una de las cajas;
   - **un control dañino ciego por el caso elegido**, no por el evaluador;
   - **un JSON del agente con tabuladores literales.**

   Cada uno quedó como una desviación (DV) fechada y decidida antes de mirar su efecto. Ninguno cambió una conclusión.
5. **Ampliar después de ver un p prometedor tiene un precio, y se paga en el cálculo.** La ampliación se decidió a la vista del
   piloto. Por eso su análisis no es un McNemar sobre los 18 casos (que daría p = 0,02 y sería optimista). Es una combinación
   de dos etapas con pesos fijados antes de medir la segunda, y esta etapa se declaró la última.
6. **Un laboratorio joven se queda pronto sin fallos históricos.** Los arreglos reales aislables en git se agotaron en 6. Para
   seguir midiendo hacen falta defectos vivos declarados, y esos vienen con su diagnóstico ya escrito en el verificador.

**Coste:**
- **Agente:** 42 000-57 000 tokens nuevos por tirada, y de 60 000 a 180 000 por arreglo aceptado.
- **Contraste con otro fabricante** (DeepSeek, una réplica): en el piloto queda cerca del agente; en la ampliación se quedó sin
  saldo.

## Qué hay aquí

| Ruta | Qué es |
|---|---|
| [`ANTES-PILOTO-AGENTE.md`](ANTES-PILOTO-AGENTE.md), [`etapa/ANTES-AMPLIACION-AGENTE.md`](etapa/ANTES-AMPLIACION-AGENTE.md) | La pregunta, el alcance fijado por el responsable, «hecho cuando» y topes, escritos antes de empezar |
| [`agente/diseno-agente-fable.md`](agente/diseno-agente-fable.md), [`agente/amp/diseno-ampliacion-fable.md`](agente/amp/diseno-ampliacion-fable.md) | Los dos diseños, escritos por un modelo distinto del que implementa, a ciegas de los arreglos y de los resultados por caso. Sus encargos: [`agente/ENCARGO-AG0.md`](agente/ENCARGO-AG0.md) y [`agente/amp/ENCARGO-AMP.md`](agente/amp/ENCARGO-AMP.md) |
| [`agente/CONSIGNA_AG1.md`](agente/CONSIGNA_AG1.md), [`agente/CONSIGNA_AG1_B.md`](agente/CONSIGNA_AG1_B.md) | La consigna que recibió el agente, fija, y su segunda redacción para la prueba de fragilidad |
| [`etapa/SELLO-AG1.md`](etapa/SELLO-AG1.md), [`etapa/SELLO-AG2-ANTES.md`](etapa/SELLO-AG2-ANTES.md), [`etapa/SELLO-AMP.md`](etapa/SELLO-AMP.md) | Los sellos, commiteados antes de la primera tirada: corpus, puertas, controles del evaluador, reglas de decisión y de parada, desviaciones, y las huellas de lo congelado |
| [`RESULTADO-AGPRE.md`](RESULTADO-AGPRE.md), [`RESULTADO-AG0.md`](RESULTADO-AG0.md), [`RESULTADO-AG1.md`](RESULTADO-AG1.md) | El eslabón débil medido antes de diseñar, el diseño decidido y el sellado |
| [`RESULTADO-AG2-AG3.md`](RESULTADO-AG2-AG3.md), [`OPCIONES-TRAS-PILOTO.md`](OPCIONES-TRAS-PILOTO.md), [`RESULTADO-AMP.md`](RESULTADO-AMP.md) | Los resultados del piloto, las opciones medidas tras él y el resultado de la ampliación |
| [`agente/`](agente/) y [`agente/amp/`](agente/amp/) | Las decisiones de diseño delegadas en Jev, un modelo de decisión calibrada del panel: el estado neutral que se le escribió, sin la recomendación de nadie, y lo que contestó con su probabilidad |

## El tercer estudio: el agente con bucle de prueba (BU, 13-14 y 22-oct-2026)

El piloto y la ampliación dejaron localizar casi resuelto y arreglar a medias: los parches que no se aceptaban solían arreglar
el mensaje que el agente veía y no los demás que fallaban por la misma causa. BU cambia un solo factor. Le da al agente de hoy
una herramienta más, `probar_parche`, que aplica su parche en la caja y le devuelve el veredicto del verificador mensaje a
mensaje antes de entregarlo. Y lo compara con el agente de hoy, remedido, en los mismos 18 casos.

> **Con el bucle de prueba, el agente arregla sin colateral 14,5 de 18** (IC95 0,58-0,93) **frente a 8,5 de 18** sin él:
> **aporta** (Δ +0,33, IC 0,14-0,53; 6 casos a favor y 0 en contra, p = 0,016 a una cola). La regla, sellada antes de la
> primera tirada, pedía p ≤ 0,05 y Δ ≥ 0,20.

- **Supera la previsión.** El diseño preveía «indeterminado», con un techo realista de unos 6 casos, y el bucle convierte
  exactamente 6. Ninguno va al revés.
- **La ganancia es del bucle, no del modelo.** El agente de hoy, remedido, da 8,5 de 18, lo mismo que en el piloto y la
  ampliación.
- **No contenta a lo que ve ni daña.** Hay sobreajuste en 2 tiradas (el umbral era 3) y el colateral medio es 0. De 7 parches
  aceptados que leyó Jev, 7 arreglan la causa.
- **A diferencia de la ampliación, no depende de las deudas por decisión:** sin ellas sigue «aporta».
- **Coste:** 53 045 tokens por tirada y 65 849 por arreglo aceptado.

El resultado completo, con sus sensibilidades preinscritas y el detalle por caso: [`bucle/RESULTADO-BU.md`](bucle/RESULTADO-BU.md).

| Ruta | Qué es |
|---|---|
| [`bucle/ANTES-AGENTE-BUCLE.md`](bucle/ANTES-AGENTE-BUCLE.md), [`bucle/RESULTADO-BU-PRE.md`](bucle/RESULTADO-BU-PRE.md) | La pregunta, el alcance, «hecho cuando» y topes, y el eslabón débil medido antes: la latencia de `probar_parche` |
| [`bucle/diseno-bucle-fable.md`](bucle/diseno-bucle-fable.md) | El diseño, escrito a ciegas por un modelo distinto del que implementa |
| [`bucle/decisiones-qbu.md`](bucle/decisiones-qbu.md), [`bucle/decision-jev-qbu.md`](bucle/decision-jev-qbu.md), [`bucle/decision-jev-qbu9.md`](bucle/decision-jev-qbu9.md) | Las preguntas de diseño y lo que decidieron el responsable y Jev |
| [`bucle/SELLO-BU.md`](bucle/SELLO-BU.md) | El sello, commiteado antes de la primera tirada (con la huella de la clave, no la clave) |
| [`bucle/RESULTADO-BU.md`](bucle/RESULTADO-BU.md) | El resultado |
| [`bucle/decision-jev-bu3-lectura.md`](bucle/decision-jev-bu3-lectura.md), [`bucle/decision-jev-bu3-lectura-control.md`](bucle/decision-jev-bu3-lectura-control.md) | La lectura que hizo Jev de los parches aceptados, y su control |

**De BU no está:** la clave, las transcripciones, `pruebas.jsonl` ni los estados que se le escribieron a Jev para la lectura,
porque llevan el texto de los parches.

## Lo que no está, y por qué

- **El código del arnés y de los circuitos.** Este paquete no es reproducible por sí solo, como el resto del repositorio. El
  del verificador sí está, desde el 22-oct, en [`../verificador/`](../verificador/).
- **La clave de los casos.** Lleva qué arreglo real corresponde a cada caso histórico y la zona de cada defecto vivo.
- **Las transcripciones de las tiradas.**
- **Los mensajes.** Toda la evidencia que vio el agente era sintética, pero no se publica.

Los sellos citan huellas de ficheros que viven en el repositorio de trabajo y no aquí. Las copias de esta carpeta son las mismas
que se sellaron, salvo los cambios de higiene que lista [`CAMBIOS-DE-PUBLICACION.md`](CAMBIOS-DE-PUBLICACION.md) (rutas de
máquina sustituidas).
