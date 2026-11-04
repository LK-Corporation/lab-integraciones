# Estado: la previsión de la etapa 30, antes de correr (4-nov-2026, noche)

Redactado el 4-nov-2026. **A propósito NO incluye la previsión de nadie.**

## Contexto

Se van a pasar 723 mensajes HL7 v2.5 sintéticos publicados por el laboratorio (ADT, ORU, VXU y MDM, con sus pares mínimos) por el
validador de InterSystems IRIS. Solo cuentan los errores que el estándar sostiene: estructura del mensaje, campos obligatorios,
longitudes por encima de la del estándar y valores fuera de una tabla de HL7. Las tablas de usuario y los segmentos Z al final
son aviso. Después se cruza con dos auditores que leyeron el estándar en VXU y ORU (162 mensajes): por mensaje, y por lugar
exacto (segmento y campo). Y se mira si alguna discrepancia nueva publicada sobre conversores de terceros se apoya solo en
mensajes inválidos por una regla que toca su campo.

## Hechos

1. **Los mensajes se escribieron para ser válidos en v2.5.** Lo dicen sus generadores. Los auditores encontraron muchos inválidos en
   VXU y ORU, pero sobre todo por reglas que IRIS no ve: campos condicionales, cruces entre campos y una regla transversal de un
   tipo de dato.
2. **IRIS ve** la estructura, los obligatorios, las longitudes y las tablas de HL7, con su propio esquema, que no es el estándar.
3. **Lo medido antes de correr:** 24 mensajes de ADT llevan un segmento Z al final, 22 llevan texto no ASCII y 3 traen MSH-9 sin
   estructura.

## Las preguntas

- ¿Qué proporción de los 723 sale válida en lo que cuenta?
- De los lugares que marca como defecto alguno de los dos lectores (IRIS o los auditores) en lo que los dos pueden ver, ¿qué
  proporción marcan los dos?
- ¿Cuántas discrepancias nuevas publicadas salen afectadas?
