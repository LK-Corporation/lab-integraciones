# Laboratorio de integraciones HL7 v2 → FHIR R4: un verificador, dos conversores de código abierto juzgados con él y tres estudios sobre agentes de IA

Un laboratorio personal de integraciones sanitarias sobre InterSystems IRIS for Health. Tiene cuatro piezas:
- **circuitos reales por MLLP:** el del primer estudio, `ADT^A01` → FHIR `Patient`, congelado con huella; y después ADT
  de ocho eventos → `Patient` y `Encounter`, y ORU → `DiagnosticReport` y `Observation`. El circuito ADT está repetido
  en Mirth Connect, que en el segundo estudio solo sirvió de control y en el tercero no entró;
- **un verificador determinista**, que dice si cada circuito hizo lo que manda el estándar;
- **un estudio de dos conversores HL7 v2 → FHIR de código abierto**, juzgados con ese verificador contra la guía oficial
  HL7 v2-to-FHIR;
- **tres estudios** de si un agente de IA ayuda a triar los fallos de esos circuitos y a arreglarlos.

**El estudio de conversores, en pocas líneas** (23-24 oct):
- **¿Encuentra el verificador algo que importe fuera del laboratorio?** Sí. En Microsoft FHIR-Converter (v7.0) y
  LinuxForHealth hl7v2-fhir-converter (v1.1.0), sobre 368 mensajes ADT y ORU^R01 públicos, encuentra **15 discrepancias
  nuevas y confirmadas** con la guía.
  - Cada una tiene su cita, cambia el significado del dato, no está declarada por el proyecto y se reproduce con un par
    de mensajes mínimos.
  - Siete son fuertes: un valor que se multiplica por diez, resultados que desaparecen, un estado civil «separado» que
    pasa a «anulado», un rango que pasa a ser un número.
  - Ve además 31 que los proyectos ya tenían declaradas, y 16 diferencias son convención.
  - En las ramas principales siguen 14; la otra la corrigió el propio proyecto después de la versión juzgada.
- **Cualquiera puede pasar su conversor por el mismo juez** con un adaptador JSON y una orden, sin escribir código. Con
  los dos conversores del estudio, la herramienta da los mismos veredictos que el estudio, con su juez final, en los
  368 casos.
- **El método es el de los estudios:** la previsión sellada antes de correr nada, el diseño a ciegas, una revisión
  adversaria que tumbó 10 de 25 candidatas, y los conversores aislados en una caja sin red.
- **Lo que no es:** una certificación. Es lo que ve un juez determinista con sus decisiones declaradas, en esas versiones y
  en esos dos tipos de mensaje.

**Después, vacunación** (VXU^V04, 25-oct). Con el mismo juez ampliado y los mismos dos conversores, sobre 125 mensajes VXU
públicos (40 bases sintéticas y 85 muestras de los propios proyectos), encuentra **9 discrepancias nuevas y confirmadas**
más.
- Cinco son fuertes: una vacuna rechazada y un registro anulado que salen como administrados, una dosis que se multiplica
  por diez, un lote que no existe y la relación de un tutor que se pierde.
- Ve además 26 ya declaradas, y 5 diferencias son convención.
- Está en [`verificador/RESULTADO-VXU.md`](verificador/RESULTADO-VXU.md).

**Y la comprobación del arrastre de estado** (25-oct). En la etapa de VXU se vio que LinuxForHealth arrastra estado entre
mensajes de un mismo proceso, y el estudio lo había corrido en lote. Convertidos mensaje a mensaje, con el mismo juez, **los
436 casos del estudio dan los mismos veredictos que en lote**: lo publicado no cambia. Está en
[`verificador/RESULTADO-ARRASTRE.md`](verificador/RESULTADO-ARRASTRE.md).

**Y las nueve de vacunación, en las ramas principales** (25-oct). Las nueve discrepancias de VXU siguen en la rama principal
de cada proyecto, y el arrastre de estado también; ninguna estaba reportada en su proyecto. Está en
[`verificador/RESULTADO-RAMAS-VXU.md`](verificador/RESULTADO-RAMAS-VXU.md).

**Y el verificador, en la integración continua de un conversor** (25-oct). Un flujo reutilizable de GitHub Actions pasa un
conversor por el verificador en cada cambio, en la misma caja sin red, y falla solo ante un hallazgo que no está en la línea
base del proyecto. Su demostración corre en este repositorio con tres controles: el conversor de juguete contra su base, el
juguete con un defecto sembrado y LinuxForHealth v1.1.0 traído en el runner. **Los tres salieron en verde en el primer push,
con los informes del runner iguales byte a byte a los del laboratorio.** La guía está en
[`verificador/cv/ci/CI.md`](verificador/cv/ci/CI.md), y el resultado en
[`verificador/RESULTADO-CI.md`](verificador/RESULTADO-CI.md).

**Y lo abierto de la integración continua** (26-oct). El flujo, endurecido: las entradas llegan a las órdenes por variables
de entorno, las acciones van fijadas por commit y el laboratorio se fija a un commit obligatorio. Con un proyecto de
conversor de ejemplo, [`ejemplo-ci/`](ejemplo-ci/). Sus llamadas al flujo por la forma remota, como las haría un tercero, y
un run en rojo a propósito. **En GitHub Actions, a la primera:** las dos llamadas del ejemplo pasaron, el run en rojo falló solo
por el hallazgo sembrado, comprobado desde fuera, y la demostración siguió con los mismos informes. Está en
[`verificador/RESULTADO-CI2.md`](verificador/RESULTADO-CI2.md).

**Y su mantenimiento** (31-oct). Las acciones de los flujos, subidas a versiones con Node.js 24 y fijadas por commit, y el
pin del ejemplo, en un segundo push. **En GitHub Actions, a la primera:** la demostración y el ejemplo dieron lo mismo, con los
mismos informes byte a byte, el run en rojo falló igual, y el aviso de Node.js 20 desapareció. Está en
[`verificador/RESULTADO-MANT.md`](verificador/RESULTADO-MANT.md).

**Y un cuarto tipo de mensaje: documentos clínicos** (MDM^T02, 31-oct). Con el juez ampliado otra vez y los mismos dos
conversores, **el verificador encuentra 3 discrepancias nuevas y confirmadas en MDM_T02 en 2 de 2 conversores, sobre 78
mensajes públicos; además ve 9 de las ya declaradas, y 3 diferencias son convención.**
- Dos son fuertes: un documento válido que se rechaza entero y el texto clínico que se pierde detrás de un OBX codificado.
- Las tres siguen en la rama principal de cada proyecto.
- **Corregido el 31-oct:** se retiraron dos de las cinco publicadas, que se apoyaban en estados que v2.5 no da para T02.
- Está en [`verificador/RESULTADO-MDM.md`](verificador/RESULTADO-MDM.md).

**Los tres estudios sobre agentes, en pocas líneas cada uno:**

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

**El verificador** se publicó con su código el 22-oct, con el juez de conversores el 24-oct, con VXU el 25-oct y con MDM el
31-oct. Es lo único de aquí que se
puede correr: sus pruebas pasan sin el
laboratorio (sin los perfiles privados, una se salta y otra espera menos casos; su README lo dice).

👉 **Por dónde empezar:**
- **El estudio de conversores, contado de corrido:** [`ARTICULO.md`](ARTICULO.md). Qué encontró el verificador en dos
  conversores de código abierto, cómo se buscó sin fiarse de ellos y qué no dice. Hay una versión para leer en el
  navegador, con el par de mensajes mínimos de cada discrepancia, en
  [lk-corporation.github.io/lab-integraciones/conversores](https://lk-corporation.github.io/lab-integraciones/conversores/).
- **El primer estudio y el método:** [`INFORME.md`](INFORME.md). Es autocontenido y lleva sus límites escritos. Hay una
  versión para leer en el navegador en
  [lk-corporation.github.io/lab-integraciones](https://lk-corporation.github.io/lab-integraciones/).
- **Los otros dos estudios:** [`piloto-agente/README.md`](piloto-agente/README.md).
- **El estudio de conversores:** [`verificador/RESULTADO-CONVERSORES.md`](verificador/RESULTADO-CONVERSORES.md).
- **La etapa de vacunación (VXU^V04):** [`verificador/RESULTADO-VXU.md`](verificador/RESULTADO-VXU.md).
- **La comprobación del arrastre de estado:** [`verificador/RESULTADO-ARRASTRE.md`](verificador/RESULTADO-ARRASTRE.md).
- **Las nueve de VXU en las ramas principales:** [`verificador/RESULTADO-RAMAS-VXU.md`](verificador/RESULTADO-RAMAS-VXU.md).
- **La etapa de documentos clínicos (MDM^T02):** [`verificador/RESULTADO-MDM.md`](verificador/RESULTADO-MDM.md).
- **El verificador:** [`verificador/README.md`](verificador/README.md).
- **Pasar tu propio conversor por él:** [`verificador/cv/VC.md`](verificador/cv/VC.md).
- **Pasarlo en cada cambio, en GitHub Actions:** [`verificador/cv/ci/CI.md`](verificador/cv/ci/CI.md); su resultado,
  [`verificador/RESULTADO-CI.md`](verificador/RESULTADO-CI.md).
- **Un proyecto de conversor de ejemplo para copiar, con su integración continua:** [`ejemplo-ci/`](ejemplo-ci/); su resultado,
  [`verificador/RESULTADO-CI2.md`](verificador/RESULTADO-CI2.md).

---

## Qué hay aquí

| carpeta | qué contiene |
|---|---|
| [`ARTICULO.md`](ARTICULO.md) | **el estudio de conversores en un artículo**: el problema, el juez, el método, lo que encontró con sus mensajes mínimos y sus límites |
| [`INFORME.md`](INFORME.md) | el informe del primer estudio. Si solo vas a leer una cosa del método, es esta |
| [`diseno/`](diseno/) | **cuatro versiones del diseño de la fase que habría seguido al primer estudio** (un banco de fallos sin firma mecánica), v1 → v4, cada una rota por el panel y reescrita; esa fase no se hizo, y el informe dice por qué. Más la especificación del agente de triaje y una nota sobre un modelo de decisión estructurada |
| [`encargos-y-revisiones/`](encargos-y-revisiones/) | los tres encargos al panel externo y **sus dieciséis revisiones** (de un cuarto encargo está solo su revisión, que lo dice en la cabecera). Cada ronda pedía explícitamente *rompedlo*, y lo rompieron |
| [`preinscripciones/`](preinscripciones/) | las **predicciones selladas con huella antes de medir**, incluida la que predice el propio fracaso del autor |
| [`medidas/`](medidas/) | las medidas con su control negativo: el prior, las dos mitades de la vía de oráculo independiente, y la auditoría de la interfaz de evidencia |
| [`codigo/`](codigo/) | el puntuador con sus dieciséis autopruebas, el banco de adversarios, el árbol que mide fuga por el arnés, la matriz de observabilidad, y las clases del arnés |
| [`piloto-agente/`](piloto-agente/) | **el segundo estudio (12-13 oct)** y, en [`piloto-agente/bucle/`](piloto-agente/bucle/), **el tercero (13-14 y 22 oct)**: la pregunta y los topes escritos antes, los diseños a ciegas, los sellos, las decisiones delegadas y los resultados con sus sensibilidades. Sin código, sin la clave de los casos y sin transcripciones |
| [`verificador/`](verificador/) | **el verificador determinista, con su código (22-oct)**: el juez de los dos estudios del agente. Dado el mensaje HL7 v2.5 enviado, el acuse y lo que el circuito registró y escribió en FHIR, da un veredicto con los hallazgos que lo sostienen, cada uno con su cita al estándar. Con la documentación de sus dos últimas etapas: la que cierra los huecos medidos del juez (22-oct) y **el estudio de conversores (23-24 oct)**, que juzga dos conversores de código abierto contra la guía HL7 v2-to-FHIR, su extensión a vacunación (VXU^V04, 25-oct), la comprobación de que no cambia al convertir mensaje a mensaje, la reproducción de las nueve de vacunación en las ramas principales, un flujo de GitHub Actions que pasa un conversor por él en cada cambio (25-oct) y un cuarto tipo de mensaje, los documentos clínicos (MDM^T02, 31-oct). **Es lo único de aquí que se puede correr** |
| [`ejemplo-ci/`](ejemplo-ci/) | **un proyecto de conversor de ejemplo (26-oct)**, como lo tendría un tercero: su conversor, su corpus sintético, su adaptador y sus líneas base, para llamar al flujo de integración continua del verificador por la forma remota. Se copia y se adapta |

**Lo que quizá sea lo más útil no es el resultado, son las cuatro versiones del diseño y las
revisiones que las tumbaron.** Se puede leer cómo un experimento se rompe y se rehace, con las
roturas dentro en vez de limadas.

---

## Lo que no está aquí

Esto es una selección del repositorio de trabajo, que es privado. No están:

- **del primer estudio:**
  - el catálogo de los 63 operadores de mutación y el programa que los aplica;
  - las tablas de casos y los 327 ficheros de mensaje;
  - los dos triadores que ganan el estudio;
  - los informes medidos y la bitácora de trabajo;
- **de los estudios del agente:** la clave de los casos, las transcripciones de las tiradas, los mensajes y el código del
  arnés y de los circuitos;
- **del verificador:** los circuitos y sus lectores, los corpus de los rejuicios, la evidencia guardada y los perfiles
  privados;
- **del estudio de conversores:** los conversores (Microsoft se construye desde su código; LinuxForHealth es su jar de
  Maven Central), sus salidas y el detalle por caso;
  están los agregados, los scripts y el generador de los mensajes mínimos.

**Con lo que hay, las medidas no se pueden volver a correr.** Se pueden leer el método, los instrumentos y los resultados.
Lo único que corre es el [verificador](verificador/), con sus pruebas.

### Nombres de operador y huellas

**Los nombres de operador.** En las medidas con tabla por operador van como etiquetas `op-NN`. Quedan **13 nombres de 63**
en los documentos, sin sus parámetros ni sus funciones de mutación. Cuatro de esos trece están en **documentos sellados**,
que se publican sin tocar.

**Las huellas.** Los `PRE-*.md` y `SELLO-RESERVADO.txt` se copiaron **verbatim**. Qué huella está citada dónde:

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

Todo está en español. Los términos del dominio —HL7, FHIR, los códigos de acuse— van en su forma
original.

---

## Licencias

**El código va bajo MIT** y **los documentos bajo CC BY 4.0** —puedes compartirlos y adaptarlos,
también comercialmente, citando la fuente—. Las fuentes tipográficas de la página van con la suya (SIL OFL).

**Lo que es de HL7 no lo cubre ninguna de ellas:** las filas de tres tablas de códigos (0003, 0004 y 0211), las
estructuras de mensaje de v2.5, el principio de unos mensajes de ejemplo del estándar, las citas breves que el
código del verificador lleva con su referencia, y los mapas de la guía v2-to-FHIR que lleva el juez de conversores
(que HL7 publica bajo CC0). No es obra del autor; el texto completo del estándar se obtiene de
HL7 International, con su licencia.

El detalle está en [`LICENSE.md`](LICENSE.md): qué cubre cada licencia, qué pasa con las respuestas de
los modelos externos y con el material de HL7.

---

## Aviso

**En este repositorio no hay datos de ningún paciente.** Los mensajes que hay aquí son sintéticos o
ejemplos del propio estándar.

**El verificador no es una herramienta de conformidad certificada.** Es una lectura del estándar con sus
supuestos, límites y preguntas abiertas declarados (`info_verificador`), y se publica sin garantía.

Septiembre-octubre de 2026.
