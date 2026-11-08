# Estado: dos decisiones de la etapa 39, lo sin clase del estudio (8-nov-2026)

Redactado el 8-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

`cv/cv3_clases.py` aplica las reglas de clase del estudio de conversores y lista lo que queda sin clase (`sin_clase`), sin fallar.
La etapa 39 midió lo sin clase de hoy, con el juez y el aparato de hoy (`sc/SINCLASE-SC.json`). Su ANTES dice que, si hay que
cambiar código, el diseño va a ciegas antes, con prueba en rojo y un bloque nuevo en el sello de la 33. También dice que una clase
nueva del estudio no se clasifica en esta etapa.

## Hechos (medidos)

1. **En el estudio** y en la versión 1 del corpus de la 33: nada sin clase.
2. **En la versión 2, con el juez de hoy: 30 sin clase.** Son las Observation de ACC de Microsoft en 30 ADT del corpus del
   laboratorio, que el juez cuenta como «recurso sin mapa» desde la 37.
   - La etapa 36 las clasificó como M-28, ya declarada: «la vio como candidata porque los 30 ADT con ACC son del corpus del
     laboratorio, que M-28 no miraba» (`RESULTADO-CANDIDATAS.md`).
   - La regla de M-28 reconoce ese mecanismo desde la 37 (bloque 8), pero solo en los casos que empiezan por `ms-ADT`, las muestras.
     La 36 corrigió su descripción y no tocó ese límite.
   - La regla de M-28 lleva también otro mecanismo, MC-ORU-7, que en otros corpus es de otras clases. Por eso no basta quitar el
     límite sin más.
   - La frase de la versión 2 no depende de esto: M-28 ya tiene casos en las muestras.
3. **La frase de la versión 2 da hoy 17 convenciones,** y la 33 publicó 16 con el juez de entonces. La nueva es la de
   LinuxForHealth con PID-8 fuera de la 0001, que la 36 clasificó como convención y la 37 llevó al juez. No es de lo sin clase.
4. **Lo sin clase es también un canal.** `ga/comparar_ga.py` (etapa 33) toma como candidatas nuevas lo que queda sin clase en la
   versión 2 y no en la 1. Los 8 de M-4 que arregló la 38 estaban en las dos versiones, y por eso nadie los vio.
5. **Lo usan más guiones:** `ga/cifras_ga_b.py`, `ga/cruce_ga.py`, `ga/riesgo_ga.py` y `cl/reproducir_clases_cl.py`.
6. **La previsión sellada** decía «ninguno» en la versión 2 (0,50; confianza 0,25) y «avisar sin fallar» (0,72).

## Las preguntas

**Q-SC-1.** ¿Qué se hace con los 30 de la versión 2?
- (a) Que la regla de M-28 reconozca también el corpus del laboratorio para el hallazgo de ACC, sin que su otro mecanismo (MC-ORU-7)
  alcance otros corpus: diseño a ciegas, prueba en rojo y bloque nuevo en el sello de la 33.
- (b) Declararlo, y dejar la regla en las muestras: la versión 2 sigue con 30 sin clase, que son M-28 por la etapa 36.

**Q-SC-2.** ¿Qué hace el aparato con lo sin clase?
- (a) Fallar (salir con un código distinto de 0) cuando quede alguno; los guiones que lo usan como canal lo piden de forma
  explícita.
- (b) No fallar, pero avisar al final y contarlo en la salida, para que no pase sin verse.
- (c) Nada: dejarlo como está.
