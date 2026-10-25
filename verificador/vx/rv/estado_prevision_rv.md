# Estado: qué saldrá al reproducir en las ramas principales nueve discrepancias de VXU (25-oct-2026)

Redactado el 25-oct-2026, antes de correr nada. **A propósito NO incluye la previsión de nadie.**

## Contexto

Un verificador determinista encontró 9 discrepancias nuevas en la conversión de mensajes de vacunación (VXU^V04) a FHIR, en las
versiones publicadas de dos conversores: seis en Microsoft FHIR-Converter v7.0 y tres en LinuxForHealth v1.1.0. Cada una se
confirmó con un par de mensajes mínimos. Además, LinuxForHealth arrastra estado entre mensajes del mismo proceso: tras un mensaje
con el fabricante solo en texto, los siguientes salen sin fabricante.

Ahora se van a correr los mismos pares con la rama principal de cada proyecto y con el mismo juez.

## Hechos

1. **Las nueve:**
   - **en Microsoft:** el estado de la vacuna sale de un campo equivocado, una dosis «.5» se escribe 5, un lote repetido se
     concatena, la relación de tutor se queda sin código, el nombre del fabricante une dos componentes y una de dos indicaciones
     se pierde;
   - **en LinuxForHealth:** un registro anulado sale como administrado, uno de dos profesionales se pierde y una de dos
     indicaciones se pierde.
2. **Las ramas principales se construyeron un día antes,** el 24-oct.
   - **Microsoft:** de v7.0 a la rama hay 30 commits, y ninguno toca las plantillas HL7 v2, el analizador ni el postproceso.
     Su último commit era de junio.
   - **LinuxForHealth:** de v1.1.0 a la rama hay 15 commits. Cambian la tabla de estados de Observation, el ContactPoint y los
     estados de cita y de alergia. Su último commit era de febrero.
3. **El mismo ejercicio con 15 discrepancias de ADT y ORU,** hecho con esas ramas: siguieron 14. La otra, un estado de
   Observation en LinuxForHealth, la había corregido el proyecto en uno de esos 15 commits.
4. **Lo que tienen abierto los proyectos:** el contraste del 25-oct, sobre todos sus issues y PR con sus comentarios, no
   encontró ninguna de las nueve. El issue del arrastre sigue abierto.

## Las preguntas

1. ¿Cuántas de las nueve siguen en la rama principal de su conversor?
2. ¿Sigue el arrastre de estado en la rama de LinuxForHealth?
3. ¿Estará alguna de las nueve ya reportada en su proyecto, al mirarlo hoy?
