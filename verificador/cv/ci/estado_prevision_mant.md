# Estado: qué saldrá al subir a Node.js 24 las acciones de unos flujos de integración continua (31-oct-2026)

Redactado el 31-oct-2026, antes del primer push. **A propósito NO incluye la previsión de nadie.**

## Contexto

Un laboratorio tiene en GitHub Actions varios flujos en verde, comprobados contra huellas registradas:
- una demostración;
- un proyecto de ejemplo que llama al flujo como un tercero;
- un run en rojo a propósito;
- la higiene.

**Esta etapa sube las cuatro acciones que usan a la mayor mínima que corre en Node.js 24.** Exige que todo dé lo mismo, byte a
byte, y que desaparezca el aviso de Node.js 20 que GitHub pone en cada corrida.

Los pushes van en este orden:
1. el primero cambia las acciones;
2. el segundo, el pin del proyecto de ejemplo al commit del primero;
3. el resultado va por una rama con su PR, integrada por avance rápido.

Cada push pasa por cuatro controles de publicación.

## Hechos

1. **En el laboratorio todo cuadra:**
   - las 31 pruebas pasan;
   - las acciones están cruzadas con la API y declaran Node.js 24;
   - un ensayo local de los YAML nuevos da los mismos informes y las mismas comprobaciones;
   - el lector del aviso lo ve en una corrida antigua que lo lleva.
2. **El ensayo no corre el código de las acciones,** solo los pasos de los YAML. Lo que cambie una versión solo se ve en el runner.
3. **Las notas de versión,** contrastadas con las entradas que usan estos flujos, no cambian nada de lo que usan.
4. **En la etapa anterior,** todo salió a la primera en GitHub. El único fallo fue el de un evento que nunca se había recorrido.

## Las preguntas

1. ¿Saldrá la demostración en verde en el primer push, con los mismos informes?
2. ¿Saldrá el proyecto de ejemplo en verde a la primera tras subir su pin?
3. ¿Desaparecerá el aviso de Node.js 20 en todas las corridas donde debe desaparecer?
4. ¿Saldrán en verde a la primera las corridas del PR?
5. ¿Cuántos pushes harán falta hasta cerrar la etapa?
