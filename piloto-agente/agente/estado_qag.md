# Estado: diseño del piloto «agente que se apoya en el verificador» (Q-AG-8..17)

Redactado el 12-oct-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

Un laboratorio tiene un verificador determinista (el juez) de integraciones HL7 v2.5 → FHIR R4 y varios circuitos de
integración versionados en git: tres de IRIS (ObjectScript), uno de Mirth (JavaScript) y un circuito «congelado» de IRIS. El
piloto pregunta: dado un circuito que falla y el veredicto del juez, ¿un agente con modelo **localiza la causa** en el código
y **propone un parche que el juez acepta**, mejor que una búsqueda sin modelo (la «referencia»)?

Ya fijado por el responsable del laboratorio:
- **Cuentan los fallos reales:** H son unos 7 fallos históricos con su commit de arreglo; el caso se reconstruye con el árbol de
  antes del arreglo. R son 7 fallos vivos del congelado, sin arreglo de referencia.
- **Los mutantes (M) quedan de control.**
- Localizar y parchear, puntuados por separado. El parche lo juzga el juez en una caja aislada: debe arreglar los mensajes
  que fallaban sin romper una regresión.
- El agente es un subagente de Claude, con DeepSeek si el saldo alcanza (2,09 USD).
- La referencia es fuerte y se congela antes que el agente.
- El agente ve el veredicto, la fuente actual y las herramientas del juez; ni git ni la versión buena.
- Tope: 3 sesiones.

## Lo medido en el eslabón débil (dos casos)

- Un agente mínimo arregló un fallo de Mirth (11 de 11 mensajes, 0 colateral) y uno del congelado en IRIS (5 de 5, 0
  colateral). Compiló y no tocó git.
- Costó ~115-155 mil tokens por caso.
- Los dos agentes **usaron al juez como oráculo**: le pasaron variantes construidas antes de proponer.
- La reconstrucción manual de un caso dejó una huella (sangría sobrante) que el agente notó.
- La salida grande de una herramienta del juez salió de la carpeta del agente.
- **Los subagentes de Claude lanzados desde la sesión del laboratorio reciben la memoria del laboratorio.** Esa memoria
  incluye fichas que describen fallos reales de los circuitos, y al menos una corresponde a un caso H.

## Datos para las preguntas

- n ≈ 13 casos reales que cuentan (H + R), dos réplicas por agente.
- **LABADT y LABORU** son circuitos del laboratorio, normalmente parados, con huella comprobable. Ya se usaron para cargar
  mutantes y restaurar (con la huella como prueba). El congelado tiene ya una caja aparte, LABMUT.
- Un parche puede tocar `Storage` o globals.
- **El juez declara sus decisiones en un documento.** Algunas de ellas describen comportamientos de fallos vivos del
  congelado; es decir, dan pistas textuales de R.
- Los dos casos del eslabón débil (uno de R y el único de Mirth en H) ya los vio y resolvió un agente.
- Para localizar se puede puntuar por línea (±3) o por unidad (método o bloque).
  - Un fallo «por ausencia» (falta una comprobación) casi nunca acierta por línea.
- Coste estimado del diseño: ~9,5 M tokens de agente; tope de 12 M.
