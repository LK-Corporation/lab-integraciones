# Estado: qué saldrá al correr por primera vez un flujo de integración continua en GitHub Actions (25-oct-2026)

Redactado el 25-oct-2026, antes del primer push. **A propósito NO incluye la previsión de nadie.**

## Contexto

Un laboratorio ha escrito un flujo reutilizable de GitHub Actions que pasa un conversor HL7 v2 → FHIR por un verificador y falla
solo ante un hallazgo que no está en la línea base del proyecto. Lo acompaña una demostración con cuatro jobs:
- **unas pruebas** sin Docker;
- **un control negativo:** un conversor de juguete contra su base;
- **un control positivo:** el juguete con un defecto sembrado; el job tiene que comprobar que el flujo falla, y por ese defecto;
- **un control real:** un conversor de código abierto traído en el runner desde Maven Central, con su huella comprobada, contra
  una base sacada en el laboratorio.

Nunca se ha corrido en un runner.

## Hechos

1. **En el laboratorio todo cuadra:**
   - las 14 pruebas pasan;
   - las bases salen iguales en dos corridas;
   - el positivo sembrado falla en 303 de 343 casos, y solo por el defecto sembrado;
   - el conversor real, traído de cero desde Maven Central, da la misma huella que en el estudio.
2. **Lo que solo se sabe en el runner:**
   - si el flujo reutilizable recibe bien sus entradas y devuelve sus salidas al que lo llama;
   - si se puede traer la imagen de Docker por un digest de hace semanas;
   - si las banderas de la caja (sin red, solo lectura, usuario sin privilegios, límite de procesos) funcionan con el Docker del
     runner;
   - si el usuario sin privilegios puede escribir en la carpeta de salida montada.
3. **Cada arreglo es un nuevo push,** y cada push pasa por cuatro condiciones de publicación (guarda, higiene, revisión a ciegas y
   una decisión con estado neutro).

## Las preguntas

1. ¿Saldrán los tres controles en verde en el primer push?
2. ¿Cuántos pushes harán falta hasta que salgan los tres en verde?
3. Cuando el control real llegue a comparar, ¿dará los mismos veredictos que en el laboratorio?
