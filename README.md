# Laboratorio de integraciones HL7 v2 → FHIR R4: un verificador y tres estudios sobre agentes de IA

Un laboratorio personal de integraciones sanitarias sobre InterSystems IRIS for Health. Tiene tres piezas:
- **circuitos reales por MLLP:** el del primer estudio, `ADT^A01` → FHIR `Patient`, congelado con huella; y después ADT
  de ocho eventos → `Patient` y `Encounter`, y ORU → `DiagnosticReport` y `Observation`. El circuito ADT está repetido
  en Mirth Connect, que en el segundo estudio solo sirvió de control y en el tercero no entró;
- **un verificador determinista**, que dice si cada circuito hizo lo que manda el estándar;
- **tres estudios** de si un agente de IA ayuda a triar los fallos de esos circuitos y a arreglarlos.

**Los tres estudios, en pocas líneas cada uno:**

1. **¿Puede un modelo local de 30B triar fallos de integración?** (septiembre)
   - **Funciona y no hace falta.** Detecta 10 de 18 operadores de fallo silencioso sin una sola falsa alarma en 22 casos
     limpios, sobre un conjunto reservado con las hipótesis selladas antes de abrirlo. Pero un script de expresiones
     regulares sin modelo lo bate **+0,873 contra +0,629**, y al agente no le queda ni una detección propia.
   - **Y el hallazgo que se lleva el trabajo es del método:** un banco construido con operadores de mutación declarativos
     **no puede contestar** si el modelo aporta, porque por construcción cada operador deja una firma mecánica.
2. **¿Localiza y arregla un agente los fallos de esos circuitos, guiado por el veredicto del verificador?** (12-13 oct)
   - Localiza la causa entre sus tres primeras propuestas en 17 de 18, y arregla sin romper nada 8,5 de 18.
   - Frente a una búsqueda sin modelo aporta solo sumando sus dos etapas (ninguna basta sola), y el «aporta» desaparece
     sin los casos en que el propio verificador declara una pista del fallo, y también sin los fallos que el circuito
     tiene a propósito.
3. **¿Arregla más si prueba sus parches contra el verificador antes de entregarlos?** (13-14 y 22 oct)
   - **Sí, en los mismos 18 casos:** 14,5 de 18 frente a 8,5 (Δ +0,33, p = 0,016 a una cola), sin romper nada, y sin
     depender esta vez de los fallos a propósito. Quien puntúa el arreglo es el mismo juez que el agente consulta.

**El verificador** se publicó con su código el 22-oct. Es lo único de aquí que se puede correr: sus pruebas pasan sin el
laboratorio (sin el perfil del sitio, una se salta y otra espera menos casos; su README lo dice).

👉 **Por dónde empezar:**
- **El primer estudio y el método:** [`INFORME.md`](INFORME.md). Es autocontenido y lleva sus límites escritos. Hay una
  versión para leer en el navegador en
  [lk-corporation.github.io/lab-integraciones](https://lk-corporation.github.io/lab-integraciones/).
- **Los otros dos estudios:** [`piloto-agente/README.md`](piloto-agente/README.md).
- **El verificador:** [`verificador/README.md`](verificador/README.md).

---

## Qué hay aquí, y por qué

| carpeta | qué contiene |
|---|---|
| [`INFORME.md`](INFORME.md) | el informe. Si solo vas a leer una cosa, es esta |
| [`diseno/`](diseno/) | **cuatro versiones del diseño de la fase que habría seguido al primer estudio** (un banco de fallos sin firma mecánica), v1 → v4, cada una rota por el panel y reescrita; esa fase no se hizo, y el informe dice por qué. Más la especificación del agente de triaje y una nota sobre un modelo de decisión estructurada |
| [`encargos-y-revisiones/`](encargos-y-revisiones/) | los tres encargos al panel externo y **sus dieciséis revisiones** (un cuarto encargo no se publica porque nombra operadores del catálogo; su revisión lo dice en la cabecera). Cada ronda pedía explícitamente *rompedlo*, y lo rompieron |
| [`preinscripciones/`](preinscripciones/) | las **predicciones selladas con huella antes de medir**, incluida la que predice el propio fracaso del autor |
| [`medidas/`](medidas/) | las medidas con su control negativo: el prior, las dos mitades de la vía de oráculo independiente, y la auditoría de la interfaz de evidencia |
| [`codigo/`](codigo/) | el puntuador con sus dieciséis autopruebas, el banco de adversarios, el árbol que mide fuga por el arnés, la matriz de observabilidad, y las clases del arnés |
| [`piloto-agente/`](piloto-agente/) | **el segundo estudio (12-13 oct)** y, en [`piloto-agente/bucle/`](piloto-agente/bucle/), **el tercero (13-14 y 22 oct)**: la pregunta y los topes escritos antes, los diseños a ciegas, los sellos, las decisiones delegadas y los resultados con sus sensibilidades. Sin código, sin la clave de los casos y sin transcripciones |
| [`verificador/`](verificador/) | **el verificador determinista, con su código (22-oct)**: el juez de los dos estudios del agente. Dado el mensaje HL7 v2.5 enviado, el acuse y lo que el circuito registró y escribió en FHIR, da un veredicto con los hallazgos que lo sostienen, cada uno con su cita al estándar. Con la documentación de su última etapa, que cierra los huecos medidos del juez. **Es lo único de aquí que se puede correr** |

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
- **los informes medidos** y la bitácora de trabajo, que cita rutas y máquinas concretas;
- **de los estudios del agente y del verificador**, lo que dicen sus propios README: la clave de los casos, las
  transcripciones de las tiradas, el código de los circuitos y de sus lectores, y el perfil del sitio.

**Consecuencia honesta: este repositorio no es reproducible.** Puedes leer el método, los
instrumentos y los resultados, y puedes auditar el razonamiento; no puedes volver a correr las
medidas. Esa ausencia es el precio de que el banco siga limpio, y se prefiere declararla a
disimularla. La excepción, desde el 22-oct, es el [verificador](verificador/): no lleva nada del
banco, y sus pruebas corren solas.

### Dos cosas más sobre la criba

**Los nombres de operador.** En las medidas con tabla por operador se han sustituido por etiquetas
`op-NN`, porque el hallazgo no depende de cuál es cuál. Quedan **13 nombres de 63** en documentos
donde la narración depende de que signifiquen algo —sin sus parámetros ni sus funciones de
mutación—. Cuatro de esos trece están en **documentos sellados**, que no se tocan: un documento de
preinscripción vale porque su huella verifica, y alterarlo para anonimizarlo lo dejaría sin valor.

**Las huellas.** Los `PRE-*.md` y `SELLO-RESERVADO.txt` se copiaron **verbatim**; qué huella
está citada dónde, sin redondear:

- `PRE-TEST.md` tiene su `sha256` completa dentro de `SELLO-RESERVADO.txt`, y la línea `CONJUNTA`
  del sello verifica;
- `PRE-VIA-D.md` y `PRE-VIA-D-V2.md` se citan por un prefijo en las medidas que los contrastan;
- `PRE-POLARIDAD.md` y el propio `SELLO-RESERVADO.txt` **no tienen su huella citada en ningún
  documento de este repositorio**. Su sello es un commit del repositorio de trabajo (`f1d9792`,
  21-sep-2026 23:05, y `694b64e`, 22-sep 15:26), que desde aquí no se puede comprobar.

El testigo público empieza con el primer commit de este repositorio (22-sep-2026).
[`preinscripciones/HUELLAS.sha256`](preinscripciones/HUELLAS.sha256), añadido el 30-sep, recoge
las cinco huellas para comprobarlas con `sha256sum -c HUELLAS.sha256` desde esa carpeta: atestigua que los ficheros no han cambiado
desde que se publicaron, no la fecha en que se sellaron.

---

## Sobre el idioma

Todo está en español, que es la lengua en la que se hizo el trabajo. Los términos del dominio —HL7,
FHIR, los códigos de acuse— van en su forma original.

---

## Licencias

**El código va bajo MIT** y **los documentos bajo CC BY 4.0** —puedes compartirlos y adaptarlos,
también comercialmente, citando la fuente—. Las fuentes tipográficas de la página van con la suya (SIL OFL).

**Lo que es de HL7 no lo cubre ninguna de ellas:** las filas de tres tablas de códigos (0003, 0004 y 0211), las
estructuras de mensaje de v2.5, el principio de unos mensajes de ejemplo del estándar, y las citas breves que el
código del verificador lleva con su referencia. No es obra del autor; el texto completo del estándar se obtiene de
HL7 International, con su licencia.

El detalle está en [`LICENSE.md`](LICENSE.md): qué cubre cada licencia, qué pasa con las respuestas de
los modelos externos y con el material de HL7.

---

## Aviso

**En este repositorio no hay datos de ningún paciente.** Los mensajes que hay aquí son sintéticos o
ejemplos del propio estándar. El verificador se juzgó también contra una muestra privada de mensajes de un
sitio real, que no se describe: de ella solo se publican recuentos agregados, sin un solo mensaje.

**El verificador no es una herramienta de conformidad certificada.** Es una lectura del estándar con sus
supuestos, límites y preguntas abiertas declarados (`info_verificador`), y se publica sin garantía.

Septiembre-octubre de 2026.
