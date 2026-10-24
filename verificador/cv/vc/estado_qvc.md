# Estado: nueve decisiones de diseño de «verifica tu conversor en un comando» (24-oct-2026)

Redactado el 24-oct-2026. **A propósito NO incluye la recomendación de nadie**, tampoco la del diseñador.

## Contexto

Se va a escribir una herramienta de línea de órdenes, en Python con solo la biblioteca estándar. Pasa un conversor HL7 v2 → FHIR
R4 de un tercero por un verificador determinista ya existente (el «juez»), con un fichero de adaptador JSON y una orden, sin
escribir código.

La herramienta tiene cuatro pasos:
1. corre el conversor dentro de un contenedor Docker sin red, de solo lectura y sin privilegios;
2. escribe una evidencia por mensaje;
3. la juzga con el juez, sin cambiarlo;
4. escribe un informe.

**La condición de éxito:** con los adaptadores de los dos conversores de un estudio anterior (Microsoft FHIR-Converter y
LinuxForHealth hl7v2-fhir-converter), la herramienta debe dar **exactamente los mismos veredictos** que el estudio, caso por caso,
con el mismo juez, sobre el mismo corpus. Si hay una diferencia, debe explicarse.

En aquel estudio, cada conversor se corrió con un arnés escrito a mano. El diseño de la herramienta lo hizo a ciegas otro modelo,
y deja abiertas estas nueve preguntas.

## Hechos comprobados

- **El corpus del estudio:** 368 mensajes por conversor.
  - **Microsoft:** 294 salen con Bundle y 74 con error. Los 74 errores tienen código de salida 255.
  - **LinuxForHealth:** 229 salen con Bundle y 139 con error. Los 139 errores son excepciones que su arnés escribe a fichero.
  - Ningún mensaje quedó sin respuesta, por tiempo vencido o por muerte del contenedor.
  - Ningún mensaje terminó con código 0 sin escribir salida.
- **Microsoft envuelve el Bundle:** `{"Status": "OK", "FhirResource": {…}}`.
  - El arnés del estudio sacaba el Bundle con `json.loads` y lo volvía a escribir con `json.dumps`. Eso convierte un decimal
    como `1.20` en `1.2`.
  - El juez lee los números como texto (`parse_float=str`), y una decisión ya tomada dice que la precisión decimal cuenta.
  - En los 368 casos de Microsoft, el único hallazgo sobre un valor numérico es `.5` convertido en `5`, que la reescritura no
    produce. Ningún veredicto publicado depende de la reescritura.
  - No se sabe si alguna salida original de Microsoft llevaba un decimal con cero final: la evidencia guardada es ya la
    reescrita.
- **La huella del conversor:** la fórmula del estudio hace un sha256 del contenido de los ficheros, sin sus nombres. Las dos
  huellas publicadas del estudio están hechas con ella.
- **El estudio no puso límite de memoria al contenedor.** Puso el resto de restricciones: sin red, solo lectura, sin
  capacidades, usuario 65534.
- **Las imágenes del estudio:** se corrieron por etiqueta y se registró su digest.
- **Los 68 mensajes mínimos (34 pares caso/control)** se escribieron en el estudio para probar mecanismos concretos de esos dos
  conversores.
- **LinuxForHealth declara en su documentación que no convierte tres eventos ADT.**
  - Una decisión anterior, que no cambia, dice que el juez los cuenta como rechazo incorrecto.
  - En el estudio, eso fue parte de sus 95 rechazos incorrectos.
- **El juicio de cada caso:**
  - **Lo que da el juez:** una categoría (correcto, fallo silencioso, rechazo incorrecto, indeterminado, fuera de alcance), un
    subtipo y una lista de hallazgos que cuentan, cada uno con su campo, clase y subtipo.
  - **El texto de cada hallazgo** incluye los valores observados.
- **El control** compara con el juicio guardado del estudio.

## Las preguntas

1. **La fórmula de la huella del conversor.**
   - (a) La del estudio, sin nombres de fichero; comparable con las huellas publicadas.
   - (b) Con rutas y nombres: más fuerte, pero no comparable.
   - (c) La del estudio en la evidencia, y además la de nombres en el registro de la corrida y en el informe.
2. **Un conversor termina con código 0 sin escribir salida ni error. ¿Qué estado registra la herramienta?**
   - (a) «Vacío»: el juez dirá indeterminado.
   - (b) Error con código «0», como habría hecho el arnés del estudio: el juez dirá rechazo incorrecto, o correcto si el mensaje
     debía rechazarse.
3. **Los 68 mínimos con un conversor que no es ninguno de los dos.**
   - (a) Siempre, en una sección aparte que dice para qué conversor se escribió cada par.
   - (b) Solo si se pide con una opción.
   - (c) Solo con los dos conversores del estudio.
4. **La imagen del contenedor.**
   - (a) Exigir siempre el digest en el adaptador.
   - (b) Admitir la etiqueta, resolver el digest de la máquina y registrarlo; exigir igualdad solo si el adaptador da el
     digest.
   - (c) Admitir la etiqueta y solo avisar.
5. **Cómo se saca el Bundle de una salida envuelta.**
   - (a) Recortando el texto original por posiciones, sin reescribir: conserva `1.20`.
   - (b) `json.loads` + `json.dumps`, como el arnés del estudio: pierde los ceros finales.
   - (c) `json.loads` con los números como cadenas y luego `dumps`: los números salen escritos como cadenas.
6. **El límite de memoria por omisión del contenedor.**
   - (a) Ninguno, como el estudio, y siempre con límite de procesos.
   - (b) 2048 MB: la máquina Java de uno de los conversores tomaría por omisión 512 MB de montón.
   - (c) Obligatorio declararlo en el adaptador.
7. **Qué es «el mismo veredicto» en el control.**
   - (a) Categoría y subtipo.
   - (b) Además, el conjunto de hallazgos que cuentan, como (campo, clase, subtipo).
   - (c) Además, el texto de cada hallazgo.
8. **El adaptador declara tipos que el proyecto dice no convertir.**
   - (a) El juez no cambia; el informe separa esos rechazos de los demás.
   - (b) No se admite esa clave en el adaptador.
   - (c) Esos mensajes se quitan del corpus antes de correr.
9. **Varios mensajes van en un mismo contenedor y vence su tiempo. ¿Qué pasa con los que no tenían salida?**
   - (a) Todos quedan «sin respuesta», y se declara como límite.
   - (b) Se reintentan una vez, uno a uno, cada uno con su propio límite de tiempo.
