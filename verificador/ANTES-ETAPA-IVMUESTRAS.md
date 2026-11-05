> *Copia pública: el párrafo «Fijado en autónomo» marca como no publicadas la hoja de ruta y la decisión de ruta del laboratorio; el resto, la pregunta y el «Hecho cuando» incluidos, va literal. El veredicto por muestra que pide el «Hecho cuando» está en el laboratorio; aquí se publican sus agregados. La huella que cita `ivm/SELLO-IVM.txt` es la del original.*

# ANTES: etapa 31, las muestras públicas de los proyectos por el validador de IRIS (FIJADO el 4-nov-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). Jev la eligió con 0,87
(`decision-jev-ruta15.md`, no publicada); la segunda, pausar, 0,09.

## La pregunta (fija)

> ¿Qué dice el mismo validador de la etapa 30 (IRIS, con las mismas lecturas y decisiones) de las muestras públicas de los dos
> conversores en las que se apoyan los estudios? ¿Hay alguna discrepancia nueva publicada que se apoye solo en muestras inválidas
> por una regla que el estándar sostiene, o cuyo apoyo, con las muestras, quede sin ningún mensaje válido?

## Por qué

- **La etapa 30 dejó fuera las muestras.** Cinco nuevas (L-1, L-11 y L-22 de conversores, VX-M14 y VX-M15 de VXU) se apoyan en
  parte o del todo en ellas. El apoyo del laboratorio de las del estudio de conversores quedó marcado como incompleto.
- **El aparato ya existe y está probado:** `iv/validar_iv.py`, con su control en TODO BIEN, y la lectura de `iv/lectura_iv.py`.
- **La diferencia con la 30:** las muestras no son de v2.5. Son 229, y la mayoría de la 2.8 (conversores), la 2.6 (MDM) o la
  2.5.1 y la 2.6 (VXU). IRIS trae esquemas de muchas versiones, y el texto que el laboratorio tiene para leer es el de v2.5 y el de
  v2.5.1.

## Qué se valida

Las muestras de los dos conversores:
- las 65 del estudio de conversores (ADT y ORU);
- las 87 de VXU;
- las 77 de MDM.

Son las que el laboratorio extrajo de sus repositorios públicos.

## Cómo

1. **Las decisiones nuevas, a Jev:** contra qué versión se valida cada muestra, y qué se lee cuando no hay texto de esa versión.
   Las de la 30 se heredan.
2. **La previsión se sella antes de correr.** El aparato no cambia: si hiciera falta, vuelve a pasar el control.
3. **El cruce,** con las nuevas que se apoyan en muestras, sumando su apoyo del laboratorio de la 30.

## Hecho cuando

- **Un veredicto por muestra.**
- **Cada nueva con apoyo en muestras,** marcada como en la 30.
- **`RESULTADO-IVMUESTRAS.md`** con la frase: «De las M muestras públicas, IRIS da V por válidas, I por inválidas y D sin decidir;
  de las N nuevas que se apoyan en muestras, K quedan sin ningún mensaje válido».
- **Publicado con la opción B.**

## Tope

**Una sesión**, sin agentes más allá de una revisión a ciegas.
