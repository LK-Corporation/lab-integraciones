# Estado: con qué datos se afina la referencia sin modelo (Q-AG-16, segunda vuelta)

Redactado el 12-oct-2026. **A propósito NO incluye la recomendación de nadie.** En la primera vuelta faltaban los datos de
abajo; el resultado fue 0,54 contra 0,46.

## Contexto (igual que en la primera vuelta)

El piloto compara un agente con modelo con una «referencia» sin modelo (una búsqueda determinista del hallazgo del juez al
código). Las dos localizan la causa de fallos reales de circuitos de integración y la referencia se congela antes que el
agente. Cuentan para la métrica unos 13 casos reales: unos 7 de H (fallos históricos con su arreglo conocido en git) y unos 6
de R (fallos vivos sin arreglo de referencia). Unos 12 mutantes (M) sirven de control.

## Datos que faltaban

- **Quien escribe y afina la referencia conoce los arreglos de los 7 casos de H.** Los ha hecho él.
- **Los casos de H que se usaran para afinar no quedan fuera de la medida.** Son los mismos que cuentan: no hay un H de
  reserva.
- Uno de los controles de la referencia es **barajar la clave**: si la referencia acierta igual con la verdad cambiada de
  caso, hace trampa. Con reglas afinadas sobre los casos que cuentan, ese control deja de discriminar.
- La lección del laboratorio dice: «un adversario mecánico más fuerte solo puede causar un falso negativo (concluir que el
  modelo no aporta cuando quizá aporta), nunca un falso positivo; por eso es legítimo escribir sus reglas mirando los datos».
  Esa lección se aprendió con un banco de mutantes donde los datos para escribir las reglas no eran los casos que contaban
  para el veredicto final.
