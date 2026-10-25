# Estado: qué saldrá al correr por primera vez un flujo de integración continua en GitHub Actions, tras un ensayo local (25-oct-2026)

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
2. **Hay un ensayo local de los dos YAML,** hecho después:
   - un programa del laboratorio lee los dos ficheros y corre en la máquina del laboratorio sus pasos de shell, en orden;
   - evalúa las expresiones de GitHub que usan (entradas, salidas de pasos y de jobs, condiciones) y emula los checkouts
     copiando el árbol del repositorio;
   - los cuatro jobs y los dos que comprueban sus salidas salen en verde: el positivo falla en 303 casos, solo por el defecto
     sembrado, y el real trae el conversor por la red, comprueba su huella y la imagen por su digest y da los mismos veredictos
     que la base.
3. **El digest de la imagen** se resolvió en el registro de Docker Hub el mismo día.
4. **Lo que el ensayo no puede probar,** porque solo se sabe en el runner:
   - cómo evalúa GitHub de verdad las expresiones y si pasa las salidas de un flujo reutilizable al que lo llama;
   - el Docker del runner, su usuario y su imagen de Ubuntu;
   - la red del runner hacia Maven Central y Docker Hub.
5. **Cada arreglo es un nuevo push,** y cada push pasa por cuatro condiciones de publicación (guarda, higiene, revisión a ciegas y
   una decisión con estado neutro).

## Las preguntas

1. ¿Saldrán los tres controles en verde en el primer push?
2. ¿Cuántos pushes harán falta hasta que salgan los tres en verde?
3. Cuando el control real llegue a comparar, ¿dará los mismos veredictos que en el laboratorio?
