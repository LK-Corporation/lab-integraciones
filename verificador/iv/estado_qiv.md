> *Copia pública: una frase del contexto, acortada; el resto es lo que leyó Jev.*

# Estado: las decisiones abiertas del diseño de la etapa 30 (4-nov-2026, noche)

Redactado el 4-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 30 pasa los mensajes sintéticos publicados del laboratorio (HL7 v2.5: ADT, ORU, VXU y MDM, con sus pares mínimos) por el
validador de InterSystems IRIS con su esquema de v2.5. Lo cruza con dos auditores de una etapa anterior, que leyeron el texto del
estándar a ciegas pero solo en VXU y ORU (162 mensajes). Después marca cada discrepancia «nueva» publicada sobre conversores de
terceros como intacta o afectada, según los mensajes en que se apoya. El estándar es la verdad, e IRIS es un lector más. El
aparato lo ha diseñado un diseñador a ciegas, que deja estas diez decisiones abiertas. El autor prefiere lo parecido a producción
y lo que cierra deuda. El cupo de agentes es escaso; correr en la máquina del laboratorio no lo gasta.

## Hechos

1. **El corpus.** Son 723 mensajes, ya escritos:
   - 451 de la herramienta (263 ADT, 40 ORU, 40 VXU, 40 MDM y 68 pares del estudio de conversores);
   - 50 de pares de VXU, 14 de pares de MDM y 8 de pares de la auditoría;
   - 200 de otros eventos de MDM, que son las 40 bases repetidas en cinco eventos; 40 de ellos son copia de las de MDM.

   Los pares de MDM y de la auditoría coinciden byte a byte con los que se usaron de verdad.
2. **El tipo de mensaje.** Algunos mensajes traen MSH-9 sin estructura (ADT^A04, VXU^V04), y el esquema la resuelve con la tabla
   0354 del estándar.
3. **Las tablas.** El esquema de IRIS trae vacías las tablas de usuario (falso positivo seguro). Algunas tablas que el estándar
   define como de usuario (tipo IS, como la 0001 del sexo en PID-8) sí traen valores en IRIS. En el estándar, un valor fuera de
   una tabla de usuario no hace inválido el mensaje: cada sitio define los suyos.
4. **Las longitudes.** El esquema de IRIS trae sus propias longitudes; en v2.5, muchas son recomendadas y no normativas.
5. **Los segmentos Z.** El estándar permite segmentos definidos localmente (Z).
6. **El apoyo de las nuevas.** Para el estudio de conversores, el fichero de clases solo trae recuentos por corpus, unos ejemplos
   con nombre y el par mínimo; el juicio caso a caso está en el laboratorio y se puede leer. Para VXU y MDM, el apoyo está nombrado.
7. **Lo que IRIS ve y nadie más** se tiene que leer en el estándar con una cita antes de contarlo. Puede leerlo quien corre la
   etapa, que sabe quién vio qué, o un lector nuevo a ciegas, que gasta cupo de agentes.
8. **Lo que se publica.** Los textos de error son de IRIS, no del estándar, que no se puede redistribuir.

## Las preguntas

- **Q-IV-D-1, el alcance:** (a) solo los 451 de la herramienta; (b) más todos los pares (523); (c) todo, con los otros eventos de MDM
  (723).
- **Q-IV-D-2, la estructura cuando MSH-9.3 falta o contradice la 0354:** (a) manda el esquema y la contradicción es error de
  estructura que cuenta; (b) manda MSH-9.3 cuando viene y la contradicción es aviso; (c) se valida con las dos y se publican ambas.
- **Q-IV-D-3, las tablas de usuario con valores en el esquema:** (a) no cuentan nunca, son aviso; (b) cuentan solo si el auditor
  también lo señaló; (c) cuentan como discrepancia y van a lectura.
- **Q-IV-D-4, la unidad de la frase publicada** (las tres se publican igual): (a) el mensaje; (b) mensaje por clase de regla;
  (c) el lugar exacto (segmento y campo).
- **Q-IV-D-5, quién lee el estándar en las discrepancias:** (a) quien corre la etapa, con cita; (b) un lector nuevo a ciegas;
  (c) dos lectores, y se publica su desacuerdo.
- **Q-IV-D-6, cuándo una nueva está «afectada»:** (a) todos sus mensajes de apoyo inválidos por cualquier regla sostenida; (b) por
  una regla sostenida que toca el campo del hallazgo; (c) como (a), y además cuenta el control del par.
- **Q-IV-D-7, el apoyo del estudio de conversores:** (a) los ejemplos y el par, marcado incompleto; (b) reconstruirlo entero desde el
  juicio caso a caso del laboratorio; (c) dejar ese estudio fuera del cruce de nuevas.
- **Q-IV-D-8, los segmentos Z:** (a) aviso; (b) error de estructura si no van al final del grupo; (c) no se miran.
- **Q-IV-D-9, las longitudes:** (a) cuentan solo si el valor supera la longitud del estándar, leída en su tabla; (b) cuentan como las
  diga el esquema; (c) se registran y no cuentan nunca.
- **Q-IV-D-10, qué se publica:** (a) la matriz, las cifras y la lista de discrepancias con su cita breve; (b) además las filas por
  mensaje enteras; (c) solo las cifras.
