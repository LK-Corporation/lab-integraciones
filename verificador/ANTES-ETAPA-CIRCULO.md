> *Copia pública: el párrafo «Fijado en autónomo» marca como no publicadas la hoja de ruta y la decisión de ruta del laboratorio; el resto va literal.*

# ANTES: etapa 35, cerrar el círculo del ensayo (FIJADO el 7-nov-2026)

**Fijado en autónomo**, dentro de la hoja de ruta (`HOJA-DE-RUTA.md`, no publicada). Jev eligió hacer en orden esta etapa y después las 2
candidatas de la 33, con 0,95 (`decision-jev-ruta19c.md`, no publicada). Dos preguntas antes, sin lo que cuesta cada una, habían salido con
confianza baja y cruzadas.

## La pregunta (fija)

> Después del push, ¿se puede comprobar que el árbol publicado es el que se ensayó, de forma que la comprobación caiga cuando no
> lo es y pase cuando lo es?

## Punto de partida (medido)

- **Desde la etapa 34, el ensayo local guarda lo que ensayó:** `ENSAYO.json` lleva en `clon` el árbol del índice o el commit
  HEAD. Con cambios sin `git add` o ficheros sin seguimiento no ensaya y sale con 2.
- **Nada compara ese árbol con el del commit que se publica.**
  - Un `git add` o un `commit --amend` posterior al ensayo cambian lo publicado sin aviso.
  - También lo cambia un ensayo hecho sobre otra copia, o uno que no se hizo.
  - La guía (`cv/ci/CI.md`) lo pone entre lo que el ensayo no ve.
- **En la etapa 34, lo comparé a mano después de publicar.**
  - El árbol de `464bbb2` es `160eb33…`, el de la última demo que se ensayó.
  - El ejemplo y el rojo se habían ensayado sobre el árbol anterior (`0678cbf…`), que difería en textos.
  - Antes del push, nada lo comprobó.
- **El flujo de GitHub** no sabe nada del ensayo local. Lo que corre en el runner es lo publicado.

## Condiciones que no se negocian

1. **Lo de siempre:**
   - el juez, la herramienta y las bases no cambian;
   - el código de terceros va en su caja;
   - cada push, por la opción B.
2. **El diseño, a ciegas,** antes de escribir código (Fable), y las decisiones abiertas a Jev.
3. **Cada cambio, con su prueba en rojo antes.** Las cifras de las pruebas se dan del repositorio publicado.
4. **Sin secretos ni permisos nuevos en los flujos.** Si la comprobación va en GitHub, con permisos de solo lectura.
5. **Lo que ya está en verde sigue en verde:** la demo, el ejemplo y el rojo dan lo mismo.

## Qué se mide

- **El control positivo:** se ensaya, se cambia algo después (un `git add` de más y, aparte, un `commit --amend`) y se publica en
  un repositorio de prueba local, nunca en el público. La comprobación tiene que caer, y decir por qué.
- **El control negativo:** se ensaya y se publica tal cual en el repositorio de prueba. La comprobación tiene que pasar.
- **El caso real:** el push de esta misma etapa pasa la comprobación.
- **Lo que cuesta:** tiempo de más por push.

## Previsión (se sella antes de correr los controles)

La probabilidad de que el control positivo caiga en los dos casos y de que el negativo pase, a la primera; y de que el push de
la etapa pase la comprobación a la primera.

## Hecho cuando

- **Publicado, con la CI en verde:** la comprobación y sus pruebas, y la guía, que la cuenta.
- **El push de la etapa, comprobado.**
- **Un documento de resultado,** `RESULTADO-CIRCULO.md`, con la frase: «Después del push, la comprobación dice si el árbol
  publicado es el ensayado: cae cuando no lo es y pasa cuando lo es».

## Tope

**Una sesión, y un lector a ciegas** (hasta dos pasadas). Cada push, por la opción B.

## Regla de parada

- **Si la comprobación no puede caer en el control positivo sin dar falsos rojos en el negativo:** se declara, no se publica y se
  sigue con las candidatas.

## Fuera de la etapa

- Cambiar el juez, la herramienta, las bases o los conversores.
- Firmar commits o atestaciones.
- Comprobar ensayos de etapas anteriores.
