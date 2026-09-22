# Jev (`typesafe/jev-1.13`): adversario del banco, no brazo del experimento

**Fecha: 22-sep-2026. Decisión tomada, pendiente de ejecutar.**

## Qué es, comprobado y no leído

Modelo de decisión estructurada de TypeSafe, en OpenRouter por un **endpoint aparte**
(`POST /api/alpha/decisions`, no `chat/completions`) — por eso no aparece en el catálogo de
`/api/v1/models`, donde buscarlo da cero.

No genera texto: recibe un **estado** y un mapa de **preguntas tipadas**, y devuelve decisiones con
probabilidad. Tipos: `noul` (sí/no), `choice` (una de varias) y `score` (ordinal). Llamada real:

```json
"answers": {
  "urgente": {"type": "noul", "noul": 0.98},
  "equipo":  {"type": "choice", "choice": "tecnico",
              "probabilities": {"tecnico": 1, "ventas": 0, "facturacion": 0},
              "confidence": 1}
}
"usage": {"input_tokens": 381, "output_tokens": 62, "cost": 1.6002e-05}
```

Cada pregunta lleva `instructions` (cadena) y, en `choice`, `criteria` como **registro**
`opción → descripción` — no una lista ni una cadena JSON, que es donde se atascan los primeros
intentos.

## Por qué NO es un brazo del experimento

**1. Contesta otra pregunta.** La fase pregunta por un **30B local con herramientas**. Jev es
alojado, no genera texto y no llama a herramientas.

**2. No sabe leer HL7, y eso lo coloca del lado del arnés.** Necesita el estado ya estructurado.
Para alimentarlo hay que parsear el mensaje, elegir la repetición de PID-5 con la regla publicada y
normalizar la fecha — y eso lo haría `observabilidad.py`. En el marco de niveles de la quinta
revisión eso es **N2: el arnés produce el hecho de dominio y el modelo solo lo clasifica**. Un
brazo así mediría la extracción del arnés, no la capacidad del modelo.

**3. Haría desaparecer el problema sin explicarlo.** Todo lo medido estos dos días —que la pregunta
tiene que ir antes del veredicto, que la polaridad decide, que el modelo no cruza si no se le
pregunta— es una propiedad de la **generación autorregresiva de texto**. Jev no genera texto: su
superficie de fallo es otra. Cambiar de modelo para que el fenómeno no aparezca no es resolverlo.

## Por qué SÍ es un adversario, y de los buenos

El criterio firmado exige batir **cualquier lectura mecánica de la misma evidencia**. El suelo del
banco está en **+0,486**, puesto por «el prompt ejecutado por un script».

Jev alimentado con los rasgos **`F_msg`** —publicados y con huella `6a23e8f0f3022e902cf03824`, o
sea disponibles para cualquier atacante— es exactamente una lectura mecánica, y probablemente
buena. **Si puntúa alto, el suelo sube y el listón del agente se pone más alto.** Esa es la
dirección correcta: un resultado que sobrevive a un suelo más alto vale más que uno que no se ha
puesto a prueba.

Coste estimado: los 464 casos del conjunto de desarrollo salen por **~0,01 $**.

## Y un uso que puede desatascar una decisión 🧑

**K3(iii)** lleva días parada: la confianza verbalizada de `qwen3-coder:30b` tiene **un solo nivel**
en 152 casos (AUC 0,500), y la derivada de logprobs discrimina (AUC 0,90) pero con magnitudes en el
cuarto decimal. No hay con qué comparar.

Jev emite **probabilidades calibradas de fábrica**. No arregla la confianza de qwen —son modelos
distintos— pero da el **punto de referencia** que falta para decidir si el criterio es medible en
esta tarea o hay que sustituirlo por inalcanzable.

## Cuándo

**Después** de la taxonomía y del agente. Se apunta ahora para no perderlo y no se toca hasta
entonces: meterlo en medio sería cambiar de tema con una medida a medias.
