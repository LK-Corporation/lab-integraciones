# Estado: tres decisiones para subir las acciones de un flujo de integración continua a Node.js 24 (31-oct-2026)

Redactado el 31-oct-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

Un laboratorio tiene publicados varios flujos de GitHub Actions: un flujo reutilizable, su demostración, un proyecto de ejemplo
que lo llama como un tercero, un run en rojo a propósito y la higiene del repositorio. Todos están en verde. Usan cuatro
acciones oficiales de GitHub (checkout, setup-python, upload-artifact y download-artifact), fijadas por commit. GitHub ya avisa
de que corren en Node.js 20 y las fuerza a Node.js 24.

**Esta etapa sube las acciones a versiones con Node.js 24.** Exige que los controles den lo mismo, con los mismos informes byte
a byte, y que el aviso desaparezca. Cada push pasa por cuatro controles de publicación.

## Hechos

1. **De cada acción hay una mayor mínima con Node.js 24 y otra que es la última:**

   | Acción | Mínima con Node.js 24 | Última |
   |---|---|---|
   | checkout | v5.1.0 | v7.0.1 |
   | setup-python | v6.3.0 | v7.1.0 |
   | upload-artifact | v6.0.0 | v7.0.2 |
   | download-artifact | v7.0.0 | v8.0.2 |

2. **Lo que dicen sus notas de versión,** contrastadas una a una con las entradas que usan estos flujos:
   - ninguna novedad toca esas entradas;
   - la excepción es que download-artifact v8 pasa a fallar si la huella de lo bajado no es la que anuncia el servidor. Eso solo
     se ve en el runner, y es más estricto;
   - la última versión de varias acciones pasa a módulos ESM, lo que solo se ve en el runner.

   Elegir la mínima deja la siguiente subida de mayores para otra etapa igual.
3. **Si una acción cambiara un resultado,** hay una escalera escrita: esa acción baja a su mínima con Node.js 24 y, si tampoco
   sirve, a la de hoy.
4. **El flujo de la higiene es el único checkout sin `persist-credentials: false`.** Desde checkout v6, con persistencia el token
   va a un fichero aparte. Nada del job lo usa. Añadir la línea es una línea más y una guarda estática.
5. **El evento `pull_request` se recorrió en la etapa anterior con un PR,** y destapó un fallo de la higiene que nadie había
   previsto. Recorrerlo otra vez con las acciones nuevas cuesta un push y dos corridas más.

## Las preguntas

1. ¿Qué mayor se fija de cada acción?
2. ¿Se añade `persist-credentials: false` al checkout de la higiene?
3. ¿Se recorre otra vez el evento `pull_request` con las acciones nuevas?
