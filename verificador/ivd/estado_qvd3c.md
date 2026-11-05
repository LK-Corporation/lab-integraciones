# Estado: Q-VD-3 por tercera vez, con los hechos de los dos lados (5-nov-2026)

Redactado el 5-nov-2026, **después de correr**: el efecto de cada respuesta ya está medido, y se publica sea cual sea la
respuesta. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 32 valida las muestras públicas de los dos conversores con el esquema de IRIS de la versión que declaran. Q-VD-3 pregunta
si un segmento con más campos de los que define la estructura de su versión hace inválida la muestra.
- La primera vez (`estado_qvd.md`) salió «dentro» con 0,75; a su estado le faltaban las reglas del receptor.
- La segunda (`estado_qvd3b.md`) salió «aparte» con 0,95. Su estado traía las reglas del receptor, pero ningún hecho del otro
  lado.
- Un revisor a ciegas ha señalado que esa decisión mueve 13 de las 21 muestras válidas y que su estado solo traía hechos a favor
  de una respuesta.

## Hechos

1. **Lo que da IRIS:** «el segmento tiene más campos de los que permite la estructura». En su versión, lo dan 132 de las 223
   muestras:
   - 40 de la 2.5.1: 39 en MSH y 1 en PV1;
   - 67 de la 2.6: 45 en MSH, 16 en TXA, 4 en RXA y 2 en IN2;
   - 21 de la 2.8: 12 en ROL, 7 en OBX y 2 en ARV;
   - 4 de la 2.3.
2. **El efecto, medido:**
   - con «aparte», 21 válidas, 141 inválidas y 61 sin decidir;
   - con «dentro», 8 válidas, 174 inválidas y 41 sin decidir.
   - Las 13 que cambian de válidas a inválidas son de VXU de la 2.5.1. Su MSH trae 23 campos: MSH-22 y MSH-23 con valor, y en
     MSH-21 el perfil «Z22^CDCPHINVS». El texto de v2.5.1 define 21 campos en MSH.
3. **A favor de que no invalida, el texto:**
   - «Rules for the recipient» (v2.5.1, CH02.txt:908-911): el receptor ignora los segmentos, campos, componentes y repeticiones
     de más que no esperaba. El pasaje dice que se aplica al recibir los mensajes y convertir su contenido;
   - «Adding messages or message constituents» (v2.5.1, CH02.txt:1104-1108): el receptor, sea de la versión que sea, tiene que
     ignorar lo que no espera sin fallar;
   - «Early adoption of HL7 changes» (v2.5.1, CH02.txt:1300-1304): adoptar antes de tiempo cambios aprobados para la versión
     siguiente es práctica común y no está prohibido, pero tiene riesgo.
4. **A favor de que invalida, el texto:**
   - «Local extension rules for segments» (v2.5.1, CH02.txt:2168): no se puede modificar un segmento existente, salvo lo que dice
     la sección 2.8.2 (los cambios que hace el propio HL7 entre versiones);
   - en el mismo párrafo (CH02.txt:2170-2172): extender un segmento de HL7 con campos locales no está prohibido, pero es
     desaconsejable.
   - Ninguno de estos pasajes dice que un mensaje con campos de más no sea un mensaje de su versión, ni que lo sea.
5. **Lo que hizo el laboratorio antes:**
   - la etapa 31 puso aparte los segmentos que la versión no define (Q-MV-4, con las reglas del receptor) y midió aparte la
     pasada de repeticiones;
   - cuando el texto tira en dos sentidos y no hay forma de leerlo, el laboratorio ha dejado el caso sin decidir (OBX-2 «CWE» en
     la etapa 30, donde el estándar se contradice).
6. **Con «sin decidir»** (la opción c), las 13 pasarían de válidas a sin decidir: 8 válidas, 141 inválidas y 74 sin decidir.
7. **Sea cual sea la respuesta,** el resultado publica las tres cifras.

## La pregunta

- **Q-VD-3c.** Una muestra cuyo único problema es un segmento con más campos de los que define su versión, ¿cómo queda?
  - (a) Válida: los campos de más van aparte.
  - (b) Inválida: entra en el veredicto como error de estructura.
  - (c) Sin decidir: el texto no lo zanja.
