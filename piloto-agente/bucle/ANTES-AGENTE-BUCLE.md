# ANTES del estudio «agente con bucle de prueba» (BU), 13-oct-2026

## Por qué

El piloto del agente y su ampliación (`RESULTADO-AG2-AG3.md`, `RESULTADO-AMP.md`, publicados en `piloto-agente/`) dejaron esto:

- **Localizar ya está casi resuelto.** El agente localiza 17 de 18 casos reales.
- **Arreglar es donde se pierde.** El agente arregla sin colateral 8,5 de 18, y los parches que no se aceptan suelen ser
  **arreglos a medias**: 6 de 14, 3 de 14 y 5 de 11 disparadores. Arregla el mensaje que ve y no los demás que fallan por la
  misma causa. Un parche no compiló por un error de sintaxis que una carga en la caja habría cazado.
- **El agente casi no consulta al verificador.** Lo usa en 7 de 52 tiradas. `verificar_caso` juzga evidencias escritas a mano,
  no el circuito parcheado, así que preguntarle no le dice si su arreglo funciona.

Hipótesis: **si el agente puede probar su parche en la caja y leer el veredicto del juez sobre el circuito parcheado, arregla
más** sin aprender a contentar al juez.

## Alcance fijado por Víctor (13-oct)

- **Un solo factor:** el bucle de prueba. El agente de hoy, con una herramienta más, `probar_parche`. Aplica el parche en la
  caja, la carga y devuelve el veredicto del juez sobre los mensajes de prueba.
- **Las otras mejoras se quedan fuera de este estudio,** para que mida una sola cosa:
  - enseñar más casos del mismo fallo;
  - enriquecer el texto del juez;
  - una salida «decisión declarada»;
  - cargar los esquemas de las herramientas desde el principio.
- **Primero el eslabón débil: la latencia.** Hoy evaluar un parche cuesta 3-4 minutos y el presupuesto de una tirada es de 10.
  Si `probar_parche` no baja de un minuto, el bucle no cabe y hay que cambiar el diseño antes de gastar tiradas.
- **Fable diseña** a ciegas de los resultados por caso. Jev decide las preguntas de diseño; Víctor, las de alcance.

## Lo que el diseño tiene que resolver

1. **Que el agente no pueda adaptarse al juez.** Lo que el agente prueba no puede ser lo que decide la aceptación. Hay que
   separar los disparadores y la regresión de prueba de los de aceptación, decir cuántos ve, si ve el veredicto completo o solo
   la categoría, y seguir leyendo parches aceptados.
2. **El presupuesto con el bucle:** pruebas por tirada, tiempo y tokens. Y qué pasa con la caja mientras la tirada está abierta
   (una sola producción a la vez; el circuito congelado parado mientras dure).
3. **El corpus:** reutilizar los 18 casos reales (más los limpios) del piloto y la ampliación. El modelo no recuerda tiradas
   anteriores, pero esos casos ya se usaron para decidir cosas; el diseño dice qué implica y cómo se evita.
4. **La comparación y su regla:** el agente de hoy (ya medido) frente al agente con bucle. La medida primaria es **FIX**, que es
   donde está la ganancia, apareada por caso. La regla de decisión se escribe antes de medir.
5. **Seguridad:** el código que escribe el modelo corre solo en la caja; nunca en USER ni en los circuitos de producción del
   laboratorio.

## Hecho cuando

- El piloto de latencia está medido y escrito (BU-pre).
- El diseño (`diseno-bucle-fable.md`) está escrito y sus preguntas decididas, y el sello está commiteado **antes de la primera
  tirada**.
- Las tiradas están hechas y evaluadas, y `RESULTADO-BU.md` da la respuesta con la regla preinscrita, salga lo que salga.

**Tope: 1,5 sesiones.**

**Regla de parada del eslabón débil:** si `probar_parche` tarda más de 90 s en la caja más lenta con 3 disparadores y 5 de
regresión, y no se baja con una caja que se mantiene arrancada durante la tirada, se para y se publica eso («el bucle no cabe
en el presupuesto de una tirada»), sin cambiar el presupuesto para hacerlo caber.
