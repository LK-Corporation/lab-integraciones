# ¿Puede un modelo local de 30B triar fallos de integración HL7?

Un laboratorio personal de integraciones sanitarias: un circuito real
**`ADT^A01` por MLLP → FHIR `Patient`** sobre InterSystems IRIS for Health, un banco de fallos, y
una medida de si un agente de IA local tría esos fallos mejor que una lectura mecánica de la misma
evidencia.

**El resultado son dos frases y no se separan. El agente funciona** —detecta 10 de 18 operadores de
fallo silencioso sin una sola falsa alarma en 22 casos limpios, sobre un conjunto reservado con las
hipótesis selladas antes de abrirlo— **y aun así no hace falta**, porque un script de expresiones
regulares sin modelo lo bate **+0,873 contra +0,629**.

**Pero lo que se lleva el trabajo no es del modelo, es del método:** un banco construido con
operadores de mutación declarativos **no puede contestar** si el modelo aporta, porque por
construcción cada operador deja una firma mecánica.

👉 **Empieza por [`INFORME.md`](INFORME.md).** Es autocontenido y cuenta el laboratorio entero, con
sus límites escritos.

---

## Qué hay aquí, y por qué

| carpeta | qué contiene |
|---|---|
| [`INFORME.md`](INFORME.md) | el informe. Si solo vas a leer una cosa, es esta |
| [`diseno/`](diseno/) | **cuatro versiones del diseño de la fase siguiente**, v1 → v4, cada una rota por el panel y reescrita. Más la especificación del agente y una nota sobre un modelo de decisión estructurada |
| [`encargos-y-revisiones/`](encargos-y-revisiones/) | los encargos al panel externo y **sus diecinueve revisiones**. Cada ronda pedía explícitamente *rompedlo*, y lo rompieron |
| [`preinscripciones/`](preinscripciones/) | las **predicciones selladas con huella antes de medir**, incluida la que predice el propio fracaso del autor |
| [`medidas/`](medidas/) | las medidas con su control negativo: el prior, las dos mitades de la vía de oráculo independiente, y la auditoría de la interfaz de evidencia |
| [`codigo/`](codigo/) | el puntuador con sus dieciséis autopruebas, el banco de adversarios, el árbol que mide fuga por el arnés, la matriz de observabilidad, y las clases del arnés |

**Lo que quizá sea lo más útil no es el resultado, son las cuatro versiones del diseño y las
revisiones que las tumbaron.** Se puede leer cómo un experimento se rompe y se rehace, con las
roturas dentro en vez de limadas.

---

## Lo que **no** está aquí, y por qué

Esto no es el repositorio de trabajo: es una selección. El repositorio de trabajo es **privado a
propósito** porque lleva dentro **la clave del banco**, y publicarla es irreversible —cualquier
modelo futuro podría haberla visto, y entonces el banco deja de servir para una medición limpia—.

Quedan fuera, deliberadamente:

- **el catálogo de los 63 operadores** de mutación y el programa que los aplica;
- **las tablas de casos** y los 327 ficheros de mensaje;
- **los dos triadores que ganan la fase**: sus reglas están derivadas del catálogo, así que
  publicarlas lo reconstruiría en buena parte;
- **los informes medidos** y la bitácora de trabajo, que cita rutas y máquinas concretas.

**Consecuencia honesta: este repositorio no es reproducible.** Puedes leer el método, los
instrumentos y los resultados, y puedes auditar el razonamiento; no puedes volver a correr las
medidas. Esa ausencia es el precio de que el banco siga limpio, y se prefiere declararla a
disimularla.

### Dos cosas más sobre la criba

**Los nombres de operador.** En las medidas con tabla por operador se han sustituido por etiquetas
`op-NN`, porque el hallazgo no depende de cuál es cuál. Quedan **13 nombres de 63** en documentos
donde la narración depende de que signifiquen algo —sin sus parámetros ni sus funciones de
mutación—. Cuatro de esos trece están en **documentos sellados**, que no se tocan: un documento de
preinscripción vale porque su huella verifica, y alterarlo para anonimizarlo lo dejaría sin valor.

**Las huellas.** Los `PRE-*.md` y `SELLO-RESERVADO.txt` se copiaron **verbatim**. Sus `sha256`
aparecen citados en los documentos que los referencian, y siguen verificando.

---

## Sobre el idioma

Todo está en español, que es la lengua en la que se hizo el trabajo. Los términos del dominio —HL7,
FHIR, los códigos de acuse— van en su forma original.

---

## Licencias

**El código va bajo MIT** y **los documentos bajo CC BY 4.0** —puedes compartirlos y adaptarlos,
también comercialmente, citando la fuente—. El detalle, con qué cubre cada una y qué pasa con las
respuestas de los modelos externos, está en [](LICENSE.md).

---

## Aviso

Todos los datos clínicos utilizados son **sintéticos**. Ni un dato de ningún paciente real.

Septiembre de 2026.
