# Estado: qué saldrá al convertir mensaje a mensaje el corpus de un estudio de conversores (25-oct-2026)

Redactado el 25-oct-2026, antes de correr nada. **A propósito NO incluye la previsión de nadie.**

## Contexto

Un laboratorio publicó un estudio de dos conversores HL7 v2 → FHIR R4 juzgados por un verificador determinista. Uno de ellos,
LinuxForHealth (Java), se corrió en lote: un proceso por carpeta convertía todos los mensajes de esa carpeta, uno tras otro, con el
mismo objeto conversor. El juez mira cada Bundle frente a un perfil de la guía HL7 v2-to-FHIR y da un veredicto por mensaje
(categoría y hallazgos que cuentan).

Ahora se va a convertir el mismo corpus mensaje a mensaje, un proceso por mensaje, y comparar caso a caso con el lote, con el
mismo juez. El corpus son 436 casos: 263 ADT sintéticos, 40 ORU sintéticos, 68 mensajes mínimos (34 pares caso/control, y en cada
par el caso va justo antes que su control en el mismo proceso) y 65 muestras de los propios proyectos.

## Hechos

1. **Ese conversor arrastra estado entre mensajes del mismo proceso, al menos en un caso medido.** En mensajes de vacunación (VXU),
   tras un mensaje cuyo fabricante (RXA-17) llevaba solo texto y ningún código, todos los mensajes siguientes del proceso salieron
   sin fabricante. Mensaje a mensaje, no. El fabricante es un recurso Organization anidado, referenciado desde la vacuna. El
   proyecto tiene un issue abierto que habla de variables internas que no se reinician.
2. **No se conoce el mecanismo** ni si otros campos lo disparan. Leído el código sin ejecutarlo: el conversor comparte entre
   conversiones las plantillas y sus expresiones; la plantilla de Organization tiene un comentario sobre evitar que una aseguradora
   «sangre» en otra dentro del mismo mensaje.
3. **En ADT y ORU** el conversor crea Organization desde campos como el centro de atención primaria del paciente, las
   aseguradoras, la organización que hizo una prueba y partes de la ubicación, y Practitioner desde los profesionales de la visita,
   la orden y la observación. El juez solo mira una parte de eso (los profesionales de la visita y los recursos de su perfil).
4. **Las bases sintéticas** llevan pocos campos con solo texto donde el conversor crea esos recursos; **las muestras de los
   proyectos**, más.
5. **Antes**, la herramienta del estudio en lote dio los mismos veredictos que la corrida original del estudio, también en lote,
   en los 368 casos de ADT, ORU y muestras.

## Las preguntas

1. ¿Cuántos casos de los 436 cambiarán de veredicto por arrastre de estado (reproducido con una secuencia mínima)?
2. Si alguno cambia, ¿en qué corpus estará la mayoría?
3. ¿Cambiará alguna cifra publicada del estudio (un recuento de casos de un mecanismo, una categoría por corpus, un par mínimo)?
