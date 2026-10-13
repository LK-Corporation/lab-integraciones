# Encargo AG0: diseño del piloto «agente que se apoya en el verificador»

Eres el diseñador. Otro (Claude) implementará tu diseño tal cual, declarará cada desviación (DV-AG-n) y fijará en git la
regla de parada **antes** de medir nada. Tu diseño es la referencia contra la que se medirá todo. Importa más que cada
decisión esté escrita, justificada y con su alternativa que el que sea breve.

## Reglas de trabajo

- **Lee solo dentro de esta carpeta** (la que contiene este fichero). No uses red, ni ssh, ni otras rutas del disco, ni git.
  No ejecutes nada contra servidores; leer código sí.
- **Estás a ciegas de los arreglos del corpus H, a propósito** (Q-AG-6): no sabes qué cambió en cada uno. No intentes
  adivinarlo; diseña el piloto para cualquier fallo real de estos circuitos.
- Donde el ANTES y estas reglas no decidan, no decides en silencio: escribes una **Q-AG-n** (numera desde la 8; las 1-7 ya
  están contestadas) con tu recomendación, la alternativa y qué cambia en la medida según la respuesta.
- Escribe el diseño en **`diseno-agente-fable.md`, en esta carpeta** (con la herramienta de escritura). Es **público**: sin
  credenciales ni datos de pacientes.

Al terminar, devuelve un resumen de 15 líneas como máximo:
- secciones;
- la regla de parada en una frase;
- el número de Q-AG y de L-AG;
- los 3 riesgos que más te preocupan;
- el coste estimado en tokens de agente.

## Qué hay en la carpeta

| Ruta | Qué es |
|---|---|
| `etapa/ANTES-PILOTO-AGENTE.md` | **Léelo primero.** La pregunta, el alcance fijado por Víctor (Q-AG-1..7), los corpus, las fases AG-pre..AG4, «hecho cuando» y tope. La lista de H está resumida a propósito |
| `etapa/RESULTADO-AGPRE.md` | El eslabón débil ya medido: dos casos de punta a punta (Mirth e IRIS) y **los 7 puntos que obligan al diseño** |
| `etapa/CONOCIDOS-ANTES-DEL-SELLO.md` | El corpus R: los fallos vivos del circuito congelado, con sus disparadores |
| `lecciones/LECCIONES.md` | Lo medido antes en este laboratorio que condiciona el diseño (Fase 12: el script batió al agente) |
| `agpre/{mirth,iris}/` | Las consignas que recibió el agente mínimo en AG-pre y sus respuestas |
| `circuitos/` | La fuente **actual** de los circuitos: LABADT (`labadt/fuente`, ObjectScript), LABORU (`laboru/fuente`), LABMULTI (`multi/fuente`), la pieza común (`comun/fuente`), el circuito congelado en su copia de LABMUT (`congelado_labmut`) y el canal Mirth (`mirth/canal_adt`, JavaScript) |
| `arneses/` | Las cajas y los mutantes. `mutacion.py`: LABMUT, carga de clases, parar/arrancar, `pool()` de 120 basales, `correr()`. `agpre_iris.py` y `agpre.py`: los evaluadores de parche de AG-pre. `mi3.py`: los mutantes del canal Mirth. `ms3.py`: los de la pieza común. `adt.py`: los de LABADT (lista `MUTANTES`) |
| `verificador/info_verificador.json` | Lo que el juez declara: decisiones S-n, leyenda de categorías, puntos de entrada y contratos |

## Qué debe contener el diseño

1. **Los corpus, caso a caso como plantilla.**
   - **H:** cómo se reconstruye el circuito de antes del arreglo **sin dejar huella** (punto 1 de AG-pre); qué disparadores
     y qué regresión lleva cada caso; cómo se comprueba que el caso falla antes y que el arreglo de referencia lo arregla.
   - **R:** los 7 fallos vivos (o los que quepan), con sus disparadores y su regresión.
   - **M:** qué mutantes entran de control y calibración, y para qué decisión sirven.

   Incluye el sellado: la clave (verdad de referencia, disparadores ocultos) fuera de la caja del agente, con huellas.
2. **El protocolo del agente:**
   - qué ve: el caso, la fuente, el MCP (punto 2: la salida grande que sale de la caja);
   - la consigna fija y preinscrita;
   - el modelo y sus réplicas;
   - el presupuesto por caso;
   - qué hace si no encuentra nada;
   - cómo se impide que vea la clave, git o la versión buena.
3. **La referencia sin modelo** (Q-AG-4), construida y congelada **antes** que el agente:
   - qué hace exactamente para localizar (del hallazgo a líneas ordenadas);
   - qué hace para «parchear», si hace algo;
   - si puede consultar al juez como el agente (punto 3) y cómo se iguala la comparación;
   - sus tres controles.
4. **La métrica y la regla de decisión, preinscritas:**
   - localización (top-1 y top-3) con una regla de adjudicación para R y para los parches que tocan varios sitios (punto 4);
   - arreglo aceptado = `correcto` en los disparadores **y** 0 colateral en la regresión del circuito, con sus controles
     (parche vacío y arreglo de referencia, ya probados en AG-pre);
   - coste;
   - el tratamiento estadístico con n pequeño (~15 casos reales que cuentan): intervalos, réplicas, qué diferencia cuenta
     como «aporta» y qué como «no aporta»;
   - las dos frases juntas.
5. **El plan AG1-AG4**, con la regla de parada concreta de cada fase, escrita como número antes de medir.
6. **Las amenazas a la validez**:
   - contaminación (¿pudo el modelo ver estos fallos?);
   - huellas en el corpus;
   - el agente que usa al juez como oráculo;
   - fragilidad de la consigna;
   - un evaluador que no discrimina;
   - el coste (punto 5).
7. **Q-AG-n** (desde la 8) para Jev, cada una con recomendación y alternativa; **L-AG-n**, límites declarados de entrada.

Etiquetas: S-AG (decisión propuesta), Q-AG (pregunta), L-AG (límite), DV-AG (reservada para la implementación).
