# Estado: tres preguntas de diseño que deja el contraste con los conversores (etapa 14l, CV3)

Redactado el 24-oct-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

Un verificador determinista (el juez) juzga dos conversores de código abierto, HL7 v2 → FHIR R4. Lo esperado sale de la guía
oficial HL7 v2-to-FHIR. Cada discrepancia se clasifica en una de tres clases:
- **cuenta:** cambia el significado del dato;
- **convención:** la guía o el estándar admiten lo observado, y no cuenta;
- **rechazo:** el conversor devuelve un error.

Las tres preguntas son casos donde la guía no decide sola. Lo que se decida se aplica al juez en la etapa siguiente. Los
resultados ya sellados conservan el juez con que se hicieron.

## Hechos

1. **Rechazo por tipo o evento no soportado.**
   - Un conversor devuelve error ante ADT^A02, ADT^A11 y ADT^A13, con el texto «Message type not yet supported». Son 92
     mensajes v2.5 válidos.
   - Su documentación publica la lista de tipos y eventos que soporta, y esos tres no están.
   - La tabla 0357 de HL7 v2.5 tiene los códigos 200 («Unsupported message type») y 201 («Unsupported event code»), con los
     que un receptor rechaza lo que no soporta.
   - Hoy el juez trata así los rechazos:
     - el rechazo por una versión de HL7 no soportada es aceptable, y sale solo como nota;
     - el rechazo de un mensaje válido por cualquier otra causa cuenta.
2. **PL.9, la descripción de la ubicación.**
   - La guía lleva PL.9 a Location.description, en la Location más granular.
   - Un conversor escribe en Location.description la concatenación de todos los componentes del PL, separados por «--»:
     «UCI--3--1--HOSP--Box 3», cuando PL.9 es «Box 3».
   - El texto de PL.9 está dentro, pero la descripción no es solo PL.9. Pasa en 16 mensajes.
3. **El formato del número de teléfono.**
   - La guía construye ContactPoint.value desde XTN.1, desde XTN.12, o desde los componentes XTN.5 (país), XTN.6 (área) y
     XTN.7 (número local), según cuáles vengan. No fija cómo se escribe la cadena.
   - El juez busca en ContactPoint.value los valores literales de esos componentes.
   - Ejemplos:
     - XTN.7 «4042808» se escribe «404 2808»: los mismos dígitos con un espacio;
     - XTN.5 «1», XTN.6 «555» y XTN.7 «5550123» se escriben «(555)555-0123», tomado de XTN.1: sin el código de país.
   - Pasa en 16 mensajes de muestra de los propios proyectos.

## Lo que se pregunta

Para cada hecho, si la diferencia cuenta o no.
