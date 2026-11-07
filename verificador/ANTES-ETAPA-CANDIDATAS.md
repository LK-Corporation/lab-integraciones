> *Copia pública: el párrafo «Fijado en autónomo» marca como no publicadas la hoja de ruta y la decisión de ruta del laboratorio; el resto va literal.*

# ANTES: etapa 36, las 2 candidatas de la etapa 33 (FIJADO el 7-nov-2026)

**Fijado en autónomo**, dentro de la hoja de ruta (`HOJA-DE-RUTA.md`, no publicada). Jev eligió hacer en orden la etapa 35 y después esta, con
0,95 (`decision-jev-ruta19c.md`, no publicada).

## La pregunta (fija)

> Las 2 candidatas que dejó la etapa 33, ¿son discrepancias nuevas con la guía v2-to-FHIR, ya declaradas, convenciones que la guía
> permite, o un fallo del juez?

## Punto de partida (medido)

- **Microsoft, en los 30 ADT con ACC de la versión 2 del corpus:**
  - emite una Observation (código `injury-incident`) que el juez da por recurso sin origen en el mensaje, con la regla MC-ORU-7,
    que es de ORU;
  - sale en los 30 con ACC y en ninguno de los ADT convertidos sin ACC;
  - antes de la etapa 33, Microsoft rechazaba esos 30 mensajes por un error de tipo del generador en GT1-2 (M-11).
- **Lo que dice la guía de ACC** (el paquete `v2mappings` 1.0.0 del laboratorio): nada.
  - Ningún mapa de mensaje ADT ni de segmento cita ACC.
  - En ADT_A01, las Observation salen de OBX.
- **LinuxForHealth, en la copia completada del ejemplo 1 de los veterinarios del capítulo 3** (`cap3-36-A04-completada`):
  - convierte PID-8 = `S` en `gender: unknown`;
  - el juez lo da por valor fuera de su tabla convertido.
- **Lo que dicen el estándar y la guía de `S`:**
  - el `S` está en el ejemplo mismo de v2.5, el de una perra esterilizada (Ch03.txt:10863-10868);
  - la tabla 0001 es de usuario y sus valores son sugeridos (Ch03.txt:5034-5044): F, M, O, U, A, N;
  - el mapa de la guía para la 0001 (`table-hl70001-to-administrative-gender`, 1.0.0) lleva esos seis y no dice nada de `S`;
  - `Patient.gender` de FHIR R4 solo admite `male`, `female`, `other` y `unknown`.
- **El método de las etapas 20 y 26** clasifica cada candidata como nueva, ya declarada o convención, con:
  - el contraste con lo que el proyecto ya sabe;
  - un par mínimo;
  - una revisión adversaria.

  Aquí cabe una cuarta clase: un fallo del juez.

## Condiciones que no se negocian

1. **Lo de siempre:**
   - el código de terceros corre en su caja;
   - los proyectos de los conversores no se tocan;
   - los issues en ellos siguen siendo del autor;
   - cada push, por la opción B, con el ensayo y la comprobación de después del push.
2. **El juez no cambia en esta etapa.** Si una candidata es un fallo del juez, se declara y se anota en su clase; corregir el juez
   (que cambia su huella y obliga a rehacer las bases de la integración continua) es otra etapa.
3. **Cada clasificación, con su cita:** de la guía, del texto de v2.5 o de lo que el proyecto declara, con fichero y línea.
4. **Un par mínimo por candidata,** corrido con los dos conversores en su caja:
   - el mismo ADT con ACC y sin él;
   - el mismo ADT con PID-8 = `S` y con un valor de la tabla.
5. **Una revisión adversaria** de cada clasificación, por otro modelo que no la haya hecho.

## Qué se mide

- **Por candidata:** qué dice la guía, qué dice o hace el proyecto (contraste), qué da el par mínimo, la clase y la revisión
  adversaria.
- **Lo que cambia en lo publicado:** las clases de la etapa 33 y la frase de su resultado, que hoy dice «2 candidatas, sin
  confirmar».

## Previsión (se sella antes de correr los pares y el contraste)

La clase más probable de cada candidata, con su probabilidad.

## Hecho cuando

- **Un documento de resultado,** `RESULTADO-CANDIDATAS.md`, con la frase: «De las 2 candidatas de la etapa 33, …» (cuántas son
  nuevas, ya declaradas, convenciones o fallos del juez).
- **Las clases de la 33 anotadas** con lo que se decida, y la frase de la 33 corregida si hace falta.
- **Publicado con la opción B,** la CI en verde y el push comprobado.

## Tope

**Una sesión, y un lector a ciegas** (hasta dos pasadas). Agentes: uno de contraste por conversor y uno de revisión adversaria.

## Regla de parada

- **Si el contraste no se puede hacer** (el código o la documentación del proyecto no lo aclaran): se declara y se clasifica con
  la guía, el estándar y el par mínimo.

## Fuera de la etapa

- Corregir el juez.
- Abrir issues en los proyectos de los conversores.
- Otras candidatas u otros conversores.
