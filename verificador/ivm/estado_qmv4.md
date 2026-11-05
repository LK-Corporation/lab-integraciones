# Estado: un segmento que v2.5 no define y que hace que IRIS eche en falta otro (Q-MV-4) (4-nov-2026, noche)

Redactado el 4-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 31 validó contra v2.5 las 225 muestras públicas de los dos conversores, con el aparato de la etapa 30. Una tercera
revisión a ciegas, de otro lector, señala como bloqueante un caso que el aparato no resuelve como resuelve su análogo.

## Hechos

1. **Q-MV-2 decidió** que lo que no se puede leer con el texto de v2.5 va aparte y no entra en el veredicto. La lectura pone
   aparte, entre otras cosas, los errores de un segmento que v2.5 no define (PRT, ARV, IAR).
2. **En 14 muestras de conversores,** todas ADT de la 2.8, hay un ARV (un segmento que v2.5 no define) donde el esquema de v2.5
   espera PV1. IRIS no dice «segmento no reconocido», sino «Missing required PV1 element at segment 6 (ARV)». El PV1 está más
   abajo, en el segmento 9.
3. **El aparato lo toma como un error de estructura de PV1, que cuenta.** Además, en esas 14 la estructura queda rota en las
   pasadas de obligatorios, longitudes y tablas, y los campos que van detrás del ARV (PV1 entre ellos) quedan sin evaluar.
4. **En otra muestra (ADT_A60),** el mismo ARV sale como «Unrecognized Segment», el aparato lo quita y el error va aparte.
5. **El aparato de la 30 ya resuelve el caso análogo** de los segmentos Z: si IRIS echa en falta un segmento justo donde hay un Z,
   el error es del Z, y el Z se quita. Con los segmentos que v2.5 no define no lo hace, porque la 30 solo tenía mensajes de v2.5.
6. **El texto de v2.5 manda ignorar los segmentos no esperados** (CH02.txt:934-935 y 1145-1147).
7. **El ANTES dice:** «El aparato no cambia: si hiciera falta, vuelve a pasar el control.»
8. **El coste:** correr el control de la 30 lleva unos segundos, y la corrida de las 225 muestras, 38 s. Lo que ya está sellado
   queda como historia, y el cambio se declara.
9. **Lo que cambia con cada opción:**
   - **Con la regla en el aparato:** el ARV se quita como un segmento no reconocido, y en las 14 se evalúan los campos de detrás.
     Puede haber errores nuevos en PV1. Dos de las nuevas (L-1 y L-22) tienen el hallazgo en PV1, y sus muestras quedarían
     evaluadas en ese campo.
   - **Con la regla solo en la lectura (sin IRIS):** el error va aparte, pero los campos de detrás del ARV siguen sin evaluar.
   - **En las dos,** las 14 siguen inválidas por longitudes de segmentos de antes del ARV, y la frase del resultado no cambia.
     Según el revisor, cambian estas cifras publicadas: de 38 a 52 las inválidas solo por longitud, de 85 a 71 los errores de
     estructura, y de 3 a 17 las muestras con algo aparte.

## La pregunta

Q-MV-4, qué se hace con un segmento que v2.5 no define cuando IRIS echa en falta otro donde está él:
- (a) una regla en el aparato, como la de los Z: se quita el segmento, se pasa otra vez el control y se repite la corrida;
- (b) una regla solo en la lectura: el error va aparte y los campos de detrás quedan sin evaluar, declarado;
- (c) nada: se declara con su número y se corrigen las frases que dicen que esos segmentos van aparte.
