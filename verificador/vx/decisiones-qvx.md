# Las decisiones de diseño de VXU_V04 (Q-VX-D), 25-oct-2026

**El diseño:** `vx/diseno-vx-fable.md`, de Fable, a ciegas de lo que devuelven los conversores. Pasó el escáner de cajas.

**Las decisiones:** las tomó Jev (`typesafe/jev-1.13`) sobre un estado sin recomendación (`vx/estado_qvx.md`); su salida está
en `vx/decision-jev-qvx.md`. El programador implementa lo de Jev, no la recomendación del diseñador (§8.1 del diseño).

| Q | Decisión de Jev | Confianza | La del diseñador | Entra en `ALTERNATIVA_VX` |
|---|---|---|---|---|
| Q-VX-D-1 | **Se fijan** las uris de CVX y MVX; un sistema distinto cuenta | 0,60 | igual | no |
| Q-VX-D-2 | **Las dos tablas** (0163 y 0550), según dónde esté el código | 0,45 | igual | sí: solo la 0550 |
| Q-VX-D-3 | **Manda RXA-22** cuando RXA-21 es «A»; si no, ORC-9 | 0,10 | cualquiera de los dos | sí: cualquiera de los dos |
| Q-VX-D-4 | Un OBX de la vacuna absorbido en la Immunization, sin Observation, es **recurso ausente** | 0,42 | convención | sí: convención |
| Q-VX-D-5 | **NK1 sí**, con perfil reducido; **PD1 fuera** | 0,19 | igual | sí: ninguno |
| Q-VX-D-6 | La función del profesional ausente: **convención con uno, dato perdido con dos** que no se distinguen | 0,43 | igual | sí: siempre dato perdido |
| Q-VX-D-7 | «Fuente primaria» y «subpotente» por omisión son **dato inventado** | 0,90 | igual | no |
| Q-VX-D-8 | RXA-15 repetido: **convención** | 0,18 | la primera repetición | sí: la primera |
| Q-VX-D-9 | La Immunization sin referencia al Encounter: **convención** | 0,24 | igual | sí: dato perdido |
| Q-VX-D-10 | Los OBX de la vacuna, **con todas las reglas** de `oru_conv` | 0,68 | igual | no |

**Las alternativas.** Siete preguntas salieron con confianza ≤ 0,52. Por la regla preinscrita en el diseño (§8.1), entran en
`ALTERNATIVA_VX`, y VX2 da también la N con la alternativa de cada una. La alternativa es la segunda opción con más
probabilidad.

**Una rareza, declarada.** En Q-VX-D-3 la opción elegida por Jev («RXA-22», 0,39) no es la de más probabilidad («cualquiera»,
0,40). Se implementa lo que Jev eligió, y «cualquiera» queda como su alternativa.
