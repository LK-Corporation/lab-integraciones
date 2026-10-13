# Opciones tras el piloto del agente (13-oct-2026)

El orden fijado tras ORU está completo: ORU → ADT → modo sitio → Mirth → piloto del agente. Lo que sigue lo decide Víctor. Aquí
van los hechos medidos para decidir, **sin recomendación**.

## 1. Salir del «indeterminado» en localizar

El piloto da Δ +0,36 con 11 casos (5 discordantes a favor del agente y 1 en contra; McNemar p = 0,22). Si la proporción se
mantuviera, el p preinscrito (< 0,10) se alcanzaría así:

| n (H + R) | discordantes (a favor / en contra) | p |
|---|---|---|
| 11 (hoy) | 5 / 1 | 0,22 |
| 15 | 7 / 1 | 0,07 |
| 18 | 8 / 2 | 0,11 |
| 20 | 9 / 2 | 0,065 |
| 22 | 10 / 2 | 0,04 |

Es una extrapolación; la proporción puede cambiar. Además, la ventaja de hoy está toda en H (5/5 frente a 1/5) y en R empatan.

**De dónde saldrían casos nuevos (medido hoy):**
- **H se ha agotado.** En git, los circuitos tienen muy pocos commits: LABADT 7, LABORU 8, Mirth 2 y el congelado 1. Los arreglos
  ya están usados o retirados por las puertas. Quedan dos posibles:
  - el commit de la pieza común (`14e17de`), que cerró CIR-MT2/MT3/ADT-6/ORU-1/ORU-2;
  - el de la cabecera común, que cerró CIR-MS-1/1b/2.

  Son refactorizaciones grandes. Aislar sus hunks como en DV-AG-2 daría quizá **1-3 casos H**.
- **Defectos vivos declarados (R ampliado)**, abiertos hoy:

  | Deuda | Circuito | Caja |
  |---|---|---|
  | CIR-ADT-7 (acusa con MSH-15/16 = NE) | LABADT | existe |
  | CIR-ADT-8 (latin-1 leído como UTF-8) | LABADT | existe |
  | CIR-MS-3 (AE 103 por OBR-25 compuesto) | LABORU | existe |
  | CIR-MS-4 (AE 101 por OBR-4 sin CE.1) | LABORU | existe |
  | CIR-MT1 (no comprueba MSH-12) | LABMULTI | hay que crearla |
  | CIR-MT4 (no valida contenido) | LABMULTI | hay que crearla |

  Ojo: estas deudas están descritas en el verificador, en `deudas_circuito_*`, que se quita de lo que ve el agente; habría que
  volver a mirar las pistas (§6.2).
- **Total realista:** n ≈ 11 + 1-3 H + 4-6 R ≈ **16-20**. Con la proporción de hoy queda en la frontera de p < 0,10.

**Coste aproximado:** 1-1,5 sesiones (sellar los casos nuevos, la caja LABMULTI, las tiradas y el análisis) y unos 0,6 M tokens
del agente (2 réplicas × ~8 casos × ~42 000).

## 2. Publicar el piloto en el repo público

- El público (`LK-Corporation/lab-integraciones`, último commit `61af89d`) no lleva nada posterior a la fase 12: ni el
  verificador ni el MCP, ni ORU/ADT/Mirth, ni el piloto.
- Lo que el diseño prevé publicar en AG4: el diseño, el sello y los resultados agregados. No se publican la clave ni las
  transcripciones con datos.
- Antes hay que añadir a mano a `publicacion_extra/publicables.txt` lo que entre (deny por defecto) y pasar la guarda. La guarda
  da hoy LIMPIO sobre el público tal como está.

## 3. Otros rumbos ya anotados

- **Arreglar las deudas vivas de los circuitos** (CIR-ADT-7/8, CIR-MS-3/4, CIR-MT1/4). Choca con la opción 1: arreglarlas
  antes elimina los casos R nuevos.
- **Más motores** (la familia de laboratorios: Mirth ya está; los demás no).
- **Preguntas abiertas para Víctor:** Q-MI-11, Q-AG-8/14 (contra Jev por el alcance), Q-AG-10/11/16 (a cara o cruz en Jev) y
  Q-AG-18.
