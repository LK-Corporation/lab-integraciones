# Etapa 22: las decisiones de Jev y las desviaciones del programador

El diseño es `diseno-rv-fable.md` (Fable, a ciegas). Las cinco preguntas de su §10 se pasaron a Jev con un estado neutro
(`estado_qrv.md`, `preguntas_qrv.json`); la respuesta está en `decision-jev-qrv.md`.

## Las decisiones (Q-RV-D)

| Pregunta | Jev | Confianza | Recomendación del diseñador | Qué cambia |
|---|---|---|---|---|
| Q-RV-D-1, una «cambiada» | **fila aparte**, sin borrador | 0,66 | igual | `estado_nueve` la separa en `cambiadas` y no cuenta en K. No salió ninguna |
| Q-RV-D-2, el borrador de la dosis «.5» | **propio, que remite** al de la cola del estudio | 0,73 | igual | VXU-MS-5 lleva una nota para el autor que remite a MS-1 |
| Q-RV-D-3, cerrada pero sigue | **comentario pidiendo reabrir** | 0,76 | igual | no salió ninguna |
| Q-RV-D-4, solo cambia el texto | **no cuenta**, se lista | 0,48 | bloquear hasta explicarlo | `comparar_control` lista el texto sin bloquear. Salieron 0 diferencias de texto |
| Q-RV-D-5, lote en la rama | **no** | 0,42 | sí, como control | en la rama, LinuxForHealth corre los pares solo mensaje a mensaje; la secuencia VL11, en los dos modos |

## Las desviaciones (DV-RV-n)

- **DV-RV-1.** El registro de las ramas (`RAMAS-RV.json`) se completa con un guion aparte, `completar_ramas.py`, porque
  `ramas_vxu.py` ya estaba sellado. Añade el commit de hoy, su fecha, si se reconstruyó, la versión y la huella. La suborden
  `ramas` de `ramas_vxu.py` solo escribe la decisión.
- **DV-RV-2, después del sello y de las corridas.** Al revisar el inglés de los borradores, se cambiaron tres cosas de
  `borradores()`:
  - la línea «Actual» ya no pega el texto del juez, que está en español: dice que lo observado es igual en la versión fijada y
    en la rama;
  - la nota de VX-M14 para el autor queda fuera del texto que se copia;
  - el comentario al #348 dice que el issue trata de grupos dentro de un mensaje, y lo de aquí es entre mensajes.

  No cambia ninguna corrida ni ningún juicio. `SELLO-RV.txt` ya no verifica `ramas_vxu.py`, y es lo esperado.
  - **El sello deja de verificar como conjunto.** `comprobar_sello_rv` sobre lo publicado da `False`, así que
    `ramas_vxu.py correr --sello vx/rv` saldría con 7. Quien repite sella su propia previsión en otra carpeta.
  - **La versión sellada de `ramas_vxu.py` no se publica.** Que solo cambió `borradores()` descansa en esta declaración.
  - **Lo que sí se comprueba:** `cv3_minimos_vxu.py` y `verificar_conversor.py`, los que producen los juicios, coinciden con
    el sello, y el código publicado recalcula desde los JSON publicados el control, el estado de las nueve y los dos veredictos
    de VL11.
  - **DV-RV-1 pierde la protección que invocaba:** el guion aparte se escribió para no tocar un fichero sellado que DV-RV-2 tocó
    después.
- **DV-RV-3.** Las decisiones del contraste se escribieron con `decidir_contraste.py`, que afirma que cada número citado está
  entre los candidatos de su discrepancia.
- **DV-RV-4.** El paso 5 (el control) exige además que la secuencia VL11 salga con la versión fijada. Así el control prueba
  también el aparato del arrastre.
- **DV-RV-5.** `RESULTADO-RAMAS-VXU.md` amplía a mano el documento que escribe `ramas_vxu.py resultado`. Añade la tabla de las
  ramas con «avanzó» y «construcción», el contraste, la previsión, los límites y «cómo repetir». La frase es la del generador,
  carácter a carácter, y todo lo demás sale de los JSON de `vx/rv/`.
- **DV-RV-6. Una fecha mal en un documento sellado.** `PREVISION-RV.md` dice «el contraste de la etapa 20, de ayer». Es del
  25-oct, el mismo día, como dicen `PREVISION-RV.json` y `prevision-cuerpo-rv.json`. Como está sellado, no se toca.
- **DV-RV-7.** `ESTADO-RV.json` no lleva todas las claves del §2.4 del diseño:
  - las ramas van en `RAMAS-RV.json`;
  - lote frente a mensaje a mensaje va en `CONTROL-RV.json` (`contaminacion_etapa_20`);
  - `que_main` es una lista.

  No se pierde nada.
- **DV-RV-8, tras la revisión a ciegas (25-oct).** La revisión no aprobó por una fuga leve: el nombre de un fichero del
  repositorio de trabajo, con el nombre de pila del autor, en el ANTES y en el diseño. Se arregló, con estos cambios:
  - **la redacción** quita esa referencia, y el escáner del preparador ya no distingue mayúsculas;
  - **`CORRIDAS-RV.json`:** lo que registra cada corrida (conversor, huella, imagen y su digest, juez, fecha, mensajes y
    segundos), sin rutas;
  - **`RAMAS-RV.json`** gana la imagen con la que corrió cada rama y su digest;
  - **el contraste** dice cuándo se fusionó cada PR relacionado, y que en `master` la plantilla de Immunization lee `reasonCode`
    de RXA-19 sin `generateList`. El borrador «relacionada» dice en inglés por qué lo es; es un cambio pequeño en
    `borradores()`.
