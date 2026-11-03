# ANTES: etapa 29, auditar la validez de los corpus publicados de VXU y ORU (FIJADO el 31-oct-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). Jev la eligió con
0,98 (`decision-jev-ruta12.md`, no publicada).

## La pregunta (fija)

> Los mensajes sintéticos publicados de VXU y de ORU, y los pares mínimos que confirmaron las discrepancias nuevas de vacunación,
> ¿son válidos en HL7 v2.5, también en sus campos condicionales y en los valores que el estándar restringe según el evento o el
> estado? Si alguno no lo es, ¿qué resultado publicado se apoya en él, y qué cambia?

## Por qué (medido hoy)

En la etapa de documentos clínicos (26), dos defectos del corpus se le escaparon al diseño a ciegas y al programador, y los vio una
revisión:
- **un campo condicional sin valor:** TXA-22 con AU o LA;
- **estados que la tabla de transiciones no da para el evento:** TXA-19 OB o UN en T02.

El segundo obligó a retirar dos discrepancias publicadas. Los corpus de VXU (etapa 20) y de ORU (estudio de conversores) no se
revisaron con esa vara.

## Qué se audita

- **Las 40 bases de VXU** (`bases_vxu.py`) y los pares mínimos de VXU (`cv/cv3_minimos_vxu.py`).
- **Las 40 bases de ORU** (`bases_oru.py`) y los pares mínimos del estudio que son de ORU (`cv/cv3_minimos.py`).
- **Fuera:**
  - las bases de ADT (A1 y E2), que salen de los ejemplos del capítulo 3 y de otras etapas;
  - las muestras públicas de los proyectos, que no son nuestras y ya se juzgan con las banderas de validez.

## Cómo

1. **Un auditor a ciegas de los resultados** lee solo el estándar (capítulos 2, 3, 4 y 7 de v2.5) y los mensajes. Comprueba:
   - estructura y cardinalidad;
   - campos condicionales («C» en las tablas de atributos y las condiciones del texto);
   - valores de las tablas;
   - restricciones de valor por evento, estado u orden.

   No ve qué hallazgos se publicaron. Da, por mensaje, «válido» o el defecto con su cita.
2. **El cruce, después:** qué bases y pares defectuosos sostienen alguna discrepancia publicada, y si esa discrepancia también
   sale en mensajes válidos.
3. **Si algo publicado cae:** su clasificación pasa a Jev con un estado neutro, como en la corrección de la 26, y se corrige lo
   publicado con su marca.

## Hecho cuando

- **La auditoría,** con un veredicto y una cita por mensaje.
- **El cruce,** con cada discrepancia nueva publicada de VXU marcada como intacta o afectada.
- **`RESULTADO-AUDITORIA.md`** con la frase: «De los M mensajes sintéticos publicados de VXU y ORU, V son válidos en v2.5 también
  en condicionales y estados; de las 9 nuevas de VXU, K se apoyan solo en mensajes inválidos».
- **Publicado con la opción B,** con las correcciones que hagan falta.

## Tope

**Una sesión de trabajo.**
