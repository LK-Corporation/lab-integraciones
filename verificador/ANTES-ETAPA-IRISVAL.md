> *Copia pública: la segunda línea marca como no publicadas la hoja de ruta y la decisión de ruta del laboratorio; el resto, la pregunta y el «Hecho cuando» incluidos, va literal. La huella que cita `iv/SELLO-IV.txt` es la del original.*

# ANTES: etapa 30, el validador de IRIS como segundo lector de los corpus publicados (FIJADO el 4-nov-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). Jev la eligió con 0,96
(`decision-jev-ruta14.md`, no publicada); la segunda, auditar ADT y MDM con auditores a ciegas, 0,04.

## La pregunta (fija)

> ¿Qué dice un validador de producción, el de InterSystems IRIS con su esquema de HL7 v2.5, de los mensajes sintéticos publicados
> (ADT, ORU, VXU y MDM, con sus pares mínimos)? Donde los auditores de la etapa 29 también miraron, ¿coinciden en las reglas que
> los dos ven? ¿Se apoya alguna discrepancia nueva publicada solo en mensajes que IRIS da por inválidos por una regla que el
> estándar sostiene?

## Por qué (medido hoy)

- **La auditoría de la 29 se declara lectura, no validador:** dos auditores a ciegas leyeron el texto de v2.5. No se auditaron las
  bases de ADT ni el corpus de MDM.
- **IRIS valida, y se midió qué ve** (`Validate` de `EnsLib.HL7.Message`, en `iris-ai`, sondas de hoy):
  - la estructura del mensaje (`m`), los campos obligatorios (`r`), las longitudes (`l`) y los valores de las tablas de HL7 (`t`);
  - un solo error por llamada y por bandera;
  - las tablas de usuario vienen vacías en el esquema y dan falsos positivos con `t` (MSH-3 frente a la 0361);
  - no ve los campos condicionales ni las reglas que cruzan campos o estados.
- **Es otra implementación, de otro autor:** un tercer lector, mecánico, para el oráculo N-versión del laboratorio.

## Qué se valida

- **El corpus del laboratorio que junta la herramienta** (`cv/verificar_conversor.generar_corpus`, con los mínimos): 451
  mensajes, 263 de ADT, 40 de ORU, 40 de VXU, 40 de MDM_T02 y 68 pares mínimos del estudio de conversores.
- **Los otros pares publicados:** los de VXU (`cv/cv3_minimos_vxu.py`), los de MDM (`md/pares_mdm.py`), las bases de los otros
  eventos de MDM (`mev/bases_mdmev.py`) y los de la auditoría (`au/pares_auditoria.py`).
- **Fuera:** las muestras públicas de los proyectos, que no son del laboratorio.

## Cómo

1. **El aparato lo diseña Fable a ciegas** de lo publicado y de la auditoría: solo con lo medido hoy, las interfaces y el
   estándar. Las decisiones abiertas, a Jev.
2. **Los controles se prueban antes de usarlo:** un defecto inyectado de cada clase tiene que salir, y un mensaje limpio no.
3. **La previsión se sella antes de correr nada.**
4. **El cruce, después:** con los veredictos de los auditores de la 29 por clase de regla, y con los mensajes que sostienen cada
   discrepancia nueva publicada. Lo que IRIS vea y nadie más se lee en el estándar: IRIS es un lector, no la verdad.
5. **Si algo publicado cae,** su clasificación pasa a Jev con un estado neutro, como en la 26 y la 29.

## Hecho cuando

- **Un veredicto de IRIS por mensaje,** con sus errores por clase.
- **El cruce con la 29** por clase de regla, y cada discrepancia nueva publicada marcada como intacta o afectada.
- **`RESULTADO-IRISVAL.md`** con la frase: «De los M mensajes sintéticos publicados, IRIS da V por válidos en las reglas que ve;
  coincide con los auditores en C de A; de las N nuevas publicadas, K se apoyan solo en mensajes que IRIS invalida por una regla
  del estándar».
- **Publicado con la opción B.**

## Tope

**Una sesión de trabajo.** Sin agentes más allá del diseño y de una revisión a ciegas al publicar.
