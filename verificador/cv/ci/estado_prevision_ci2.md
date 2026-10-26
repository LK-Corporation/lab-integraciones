# Estado: qué saldrá al correr en GitHub Actions un flujo endurecido, un proyecto de ejemplo y un run en rojo a propósito (26-oct-2026)

Redactado el 26-oct-2026, antes del primer push de la etapa. **A propósito NO incluye la previsión de nadie.**

## Contexto

Un laboratorio publicó un flujo reutilizable de GitHub Actions que pasa un conversor HL7 v2 → FHIR por un verificador. Su
demostración salió en verde al primer push. Ahora:
- **endurece el flujo:**
  - las entradas, por variables de entorno;
  - las acciones, fijadas por commit;
  - el commit del laboratorio, obligatorio;
  - la demo, válida en un fork;
- **añade un proyecto de conversor de ejemplo,** en Python y en una imagen de Docker por digest. Lo llama un fichero de flujo por
  la referencia remota fijada a un commit, como lo haría un tercero, con dos llamadas y un job que descarga sus artefactos y los
  comprueba;
- **añade un run en rojo a propósito,** solo a mano: siembra un defecto en el conversor del ejemplo, el job tiene que fallar, y otro
  job comprueba desde fuera que falló por ese defecto;
- **recorre el evento `pull_request`** con una rama del propio repositorio, integrada después por avance rápido.

Hacen falta varios pushes, por fuerza:
1. el primero publica el flujo endurecido;
2. el segundo, las llamadas fijadas al commit del primero;
3. después, la rama del PR y el resultado.

Cada push pasa por cuatro condiciones de publicación.

## Hechos

1. **En el laboratorio todo cuadra:**
   - las 26 pruebas pasan;
   - las dos bases del ejemplo salen iguales en dos corridas (349 y 6 casos);
   - el defecto sembrado da el hallazgo previsto en 164 casos, y en el modo normal la comparación falla solo por él.
2. **Un ensayo local** de los YAML corre sus pasos de shell con las expresiones de GitHub evaluadas, en la máquina del
   laboratorio. Esta vez sabe de la referencia remota, de los checkouts por commit, del `if:` de job y de la descarga de artefactos:
   - la demostración endurecida sale en verde, con los mismos informes byte a byte que en GitHub en la etapa anterior;
   - las dos llamadas del ejemplo y su comprobación salen en verde;
   - el run en rojo falla solo en el paso de la comparación, y su comprobación sale en verde.
3. **El ensayo ya se equivocó una vez:** no seguía la regla de GitHub de que un `if:` sin función de estado lleva implícito «si todo
   fue bien», y se arregló antes de este estado.
4. **Lo que solo se sabe en GitHub:**
   - la resolución de la referencia remota;
   - si las salidas de un job llamado que falla llegan al job siguiente;
   - los permisos para descargar un artefacto del mismo run;
   - el checkout del commit de fusión de un PR;
   - el Docker y la red del runner.
5. **La etapa anterior** salió en verde en el primer push. Entonces se previó 0,5 para eso, y otro previsor 0,46.

## Las preguntas

1. ¿Saldrá la demostración endurecida en verde en el primer push, con los mismos informes?
2. ¿Saldrán las dos llamadas del ejemplo y su comprobación en verde a la primera?
3. ¿Saldrá el run en rojo como se espera a la primera: el job rojo solo por la comparación y la comprobación en verde?
4. ¿Llegarán al job siguiente las salidas del job llamado que falla?
5. ¿Cuántos pushes harán falta hasta cerrar la etapa?
