# Laboratorio de integraciones HL7 v2 → FHIR R4: un verificador y tres estudios de agentes

Un laboratorio personal de integraciones sanitarias sobre InterSystems IRIS for Health. Tiene tres piezas:
- **circuitos reales por MLLP:** ADT de ocho eventos → FHIR `Patient` y `Encounter`, y ORU → `DiagnosticReport` y
  `Observation`, con el circuito ADT repetido en Mirth Connect;
- **un verificador determinista**, que dice si cada circuito hizo lo que manda el estándar;
- **tres estudios** de si un agente de IA ayuda a triar los fallos de esos circuitos y a arreglarlos.

**Los tres estudios, en pocas líneas cada uno:**

1. **¿Puede un modelo local de 30B triar fallos de integración?** (septiembre)
   - **Funciona y no hace falta.** Detecta 10 de 18 operadores de fallo silencioso sin una sola falsa alarma en 22 casos
     limpios, sobre un conjunto reservado con las hipótesis selladas antes de abrirlo. Pero un script de expresiones
     regulares sin modelo lo bate **+0,873 contra +0,629**.
   - **Y lo que se lleva el trabajo es del método:** un banco construido con operadores de mutación declarativos **no puede
     contestar** si el modelo aporta, porque por construcción cada operador deja una firma mecánica.
2. **¿Localiza y arregla un agente los fallos de un circuito, guiado por el veredicto del verificador?** (12-13 oct)
   - Localiza 17 de 18 y arregla sin romper nada 8,5.
   - Frente a una búsqueda sin modelo aporta solo por acumulación de dos etapas, y no sin las pistas que declara el propio
     verificador.
3. **¿Arregla más si prueba sus parches contra el verificador antes de entregarlos?** (13-22 oct)
   - **Sí:** 14,5 de 18 frente a 8,5 (Δ +0,33, p = 0,016), sin colateral.

**El verificador** se publicó con su código el 22-oct. Es lo único de aquí que se puede correr: sus pruebas pasan solas, sin
el laboratorio.

👉 **Por dónde empezar:**
- **El primer estudio y el método:** [`INFORME.md`](INFORME.md). Es autocontenido y lleva sus límites escritos, y tiene una
  versión para leer en el navegador en
  [lk-corporation.github.io/lab-integraciones](https://lk-corporation.github.io/lab-integraciones/).
- **Los otros dos estudios:** [`piloto-agente/README.md`](piloto-agente/README.md).
- **El verificador:** [`verificador/README.md`](verificador/README.md).

---

## Qué hay aquí, y por qué

| carpeta | qué contiene |
|---|---|
| [`INFORME.md`](INFORME.md) | el informe. Si solo vas a leer una cosa, es esta |
| [`diseno/`](diseno/) | **cuatro versiones del diseño de la fase siguiente**, v1 → v4, cada una rota por el panel y reescrita. Más la especificación del agente y una nota sobre un modelo de decisión estructurada |
| [`encargos-y-revisiones/`](encargos-y-revisiones/) | los tres encargos al panel externo y **sus dieciséis revisiones** (un cuarto encargo no se publica porque nombra operadores del catálogo; su revisión lo dice en la cabecera). Cada ronda pedía explícitamente *rompedlo*, y lo rompieron |
| [`preinscripciones/`](preinscripciones/) | las **predicciones selladas con huella antes de medir**, incluida la que predice el propio fracaso del autor |
| [`medidas/`](medidas/) | las medidas con su control negativo: el prior, las dos mitades de la vía de oráculo independiente, y la auditoría de la interfaz de evidencia |
| [`codigo/`](codigo/) | el puntuador con sus dieciséis autopruebas, el banco de adversarios, el árbol que mide fuga por el arnés, la matriz de observabilidad, y las clases del arnés |
| [`piloto-agente/`](piloto-agente/) | **el segundo estudio (12-13 oct)**: un agente que, guiado por el veredicto de un verificador determinista, localiza y arregla fallos de circuitos de integración, frente a una búsqueda sin modelo. Funciona (localiza 17 de 18 y arregla la mitad) y aporta frente a la búsqueda solo por acumulación de dos etapas, y no sin las pistas que declara el propio verificador. Y **el tercero (13-22 oct)**, en [`piloto-agente/bucle/`](piloto-agente/bucle/): con una herramienta para probar sus parches contra el verificador antes de entregarlos, el mismo agente arregla 14,5 de 18 frente a 8,5 sin ella. Diseños, sellos y resultados, sin código |
| [`verificador/`](verificador/) | **el verificador determinista, con su código (22-oct)**: el juez que usan los dos estudios del agente. Dado el mensaje HL7 v2.5 enviado, el acuse y lo que el circuito registró y escribió en FHIR, da un veredicto con los hallazgos que lo sostienen, cada uno con su cita al estándar. Con la documentación de su última etapa, que cierra los huecos medidos del juez. **Es lo único de aquí que se puede correr:** sus pruebas pasan solas, sin el laboratorio |

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
también comercialmente, citando la fuente—.

**Lo que es de HL7 no lo cubre ninguna de las dos:** las tres tablas, las estructuras de v2.5 y el
principio de unos mensajes de ejemplo que el verificador necesita para correr. No es obra del autor.

El detalle está en [`LICENSE.md`](LICENSE.md): qué cubre cada licencia, qué pasa con las respuestas de
los modelos externos y con el material de HL7.

---

## Aviso

**En este repositorio no hay datos de ningún paciente.** Los mensajes que hay aquí son sintéticos o
ejemplos del propio estándar. El verificador se juzgó también contra una muestra privada de un sitio,
y de ella solo se publican recuentos agregados, sin un solo mensaje.

Septiembre-octubre de 2026.
