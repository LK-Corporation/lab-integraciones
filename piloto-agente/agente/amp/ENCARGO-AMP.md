# Encargo AMP: diseño de la ampliación del piloto del agente

Eres el diseñador, como en AG0, donde escribiste `piloto/agente/diseno-agente-fable.md`. Otro (Claude) implementará tu diseño
tal cual, declarará cada desviación (DV-AMP-n) y fijará en git la regla de parada **antes** de medir nada.

## Reglas de trabajo

- **Lee solo dentro de esta carpeta** (la que contiene este fichero). No uses red, ni ssh, ni git, ni otras rutas del disco. No
  ejecutes nada.
- **No ves resultados por caso del piloto, a propósito.** Solo tienes los agregados de `piloto/RESULTADO-AG2-AG3.md`. Diseña la
  ampliación sin intentar adivinar qué casos acertó cada brazo.
- Donde el ANTES y estas reglas no decidan, no decides en silencio: escribe una **Q-AMP-n** con tu recomendación, la
  alternativa y qué cambia en la medida según la respuesta.
- Escribe el diseño en **`diseno-ampliacion-fable.md`, en esta carpeta** (con la herramienta de escritura). Puede acabar en el
  repositorio público: sin credenciales ni datos de pacientes.

Al terminar, devuelve un resumen de 15 líneas como máximo:
- las secciones;
- la regla de decisión en una frase;
- cuántos casos nuevos esperas que pasen las puertas;
- el número de Q-AMP;
- los 3 riesgos que más te preocupan;
- el coste estimado en tokens de agente.

## Qué hay en la carpeta

| Ruta | Qué es |
|---|---|
| `etapa/ANTES-AMPLIACION-AGENTE.md` | **Léelo primero.** Por qué se amplía, el alcance fijado por Víctor, lo que el diseño tiene que resolver, «hecho cuando» y tope |
| `piloto/` | El diseño del piloto, su sello y la adenda (DV-AG-1..16, L-AG-13..16), el resultado agregado, las opciones medidas tras el piloto y los fallos vivos del congelado |
| `circuitos/` | La fuente actual de LABADT, LABORU, LABMULTI y la pieza común |
| `arneses/` | El arnés del piloto: las cajas (`ag1_cajas.py`), los evaluadores, los corpus R y M, la orquestación (`ag2.py`), el análisis (`ag3.py`), la referencia (`ref.py`), las unidades, el lanzador, `mutacion.py`, `multi.py` (LABMULTI) y `adt.py` |
| `verificador/info_verificador.json` | Lo que el juez declara **completo**, con `deudas_circuito_*`. El agente no ve esas secciones |

## Qué debe contener el diseño

1. **Los casos nuevos, uno a uno, como plantilla.**
   - **H, desde los commits de cierre de deudas** (la pieza común y la cabecera común). No conoces los diffs. Diseña cómo se
     aíslan por hunks y qué puertas pasan, sin suponer que salgan.
   - **R, desde las deudas vivas** (CIR-ADT-7, CIR-ADT-8, CIR-MS-3, CIR-MS-4, CIR-MT1 y CIR-MT4): disparadores, regresión con
     aceptados, zona preinscrita, y si alguna es en realidad de entorno o de perfil y no del código.
   - **Lo que se aprendió en el piloto:** regresión sin aceptados, firma no estable, pistas textuales.
2. **La caja LABMULTI:** creación, exportación del árbol, evaluación y restauración, con una producción a la vez.
3. **El análisis con la ampliación decidida después de ver el resultado.** La parada opcional, con su regla de decisión en
   números, preinscrita, y qué se publica en cada combinación de resultados (piloto frente a ampliación).
4. **Brazos, réplicas, presupuesto y reglas de parada**, en números. Lo mínimo que cambia respecto al piloto, y por qué.
5. **Amenazas a la validez** nuevas, frente a las del piloto.
6. **El plan AMP0-AMP3**, con «hecho cuando» y tope por fase. El tope total es 1,5 sesiones.
