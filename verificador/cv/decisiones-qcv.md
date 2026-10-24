> *Copia pública: se quitaron las alusiones al trabajo del autor y la cola de lo que solo él decide. El resto es el original del laboratorio.*

# Decisiones Q-CV de CV0 (23-oct-2026)

**El diseño:** `cv/diseno-conversores-fable.md`, de Fable, a ciegas de lo que devuelven los conversores. Pasó el escáner de la
guarda en LIMPIO y no alude a ningún sitio real.

**Cómo se decidió:**
- **Q-CV-D:** las 12 de diseño las decidió Jev, sobre un estado neutral, sin la recomendación de nadie (`cv/estado_qcv.md`,
  `cv/preguntas_qcv.json` y `cv/decision-jev-qcv.md`).
- **Q-CV-A:** las 6 de alcance se tomaron en autónomo, con la recomendación, por delegación de Víctor del 23-oct. Quedan
  revisables por él.

## Q-CV-D: diseño (Jev)

| Q | Decisión | Confianza | ¿Como recomendó Fable? |
|---|---|---|---|
| Q-CV-D-1 | **Dos puntos de entrada**, `adt_conv` y `oru_conv`, cada uno con el contrato de su familia | 1 | Sí |
| Q-CV-D-2 | La categoría se sigue llamando **`fallo_silencioso`**, con subtipos de conversión | 0,70 | Sí |
| Q-CV-D-3 | PID-8 vacío y `gender: unknown` es **dato inventado**, y cuenta | 0,50 | Sí |
| Q-CV-D-4 | El orden de `result[]`, `name[]`, `identifier[]` y `coding[]` es **forma** | 0,88 | Sí |
| Q-CV-D-5 | Una entrada de más en un elemento repetible es una **nota** | 0,42 | Sí |
| Q-CV-D-6 | PV1-2 = N sin Encounter es **recurso ausente**, y cuenta | 0,68 | **No:** Fable recomendaba convención |
| Q-CV-D-7 | Un error del conversor ante un valor imposible es **rechazo aceptable** | 0,98 | Sí |
| Q-CV-D-8 | Un código `unmatched` mapeado a un `use` es **código mal mapeado**, y cuenta | 0,80 | Sí |
| Q-CV-D-9 | En `family` se admite **solo FN.1** | 0,52 | **No:** Fable admitía las dos lecturas |
| Q-CV-D-10 | Un decimal reescrito con otra precisión **cuenta** | 1 | Sí |
| Q-CV-D-11 | En A11 con PV1-45 se admiten **las dos**: `cancelled` y `finished` | 0,86 | Sí |
| Q-CV-D-12 | Las muestras en otras versiones **se juzgan**, con la marca L18 en lo que dependa de v2.5 | 1 | Sí |

**Dos decisiones contrarias a Fable.** La implementación sigue a Jev, y el diseño se lee con dos cambios: AMB-CV-5 (PV1-2 = N)
y AMB-CV-2 (los subcomponentes de FN) dejan de ser convención. Se declaran como DV-CV al implementarlas.

**Sensibilidad preinscrita para las de confianza baja.** Son Q-CV-D-3, 5 y 9, con confianza de 0,52 o menos. CV2 juzga con la
decisión de Jev, pero el `RESULTADO` dará también N con la alternativa de cada una. Si una discrepancia «nueva» depende solo de
una de esas tres, se dice en la frase.

## Q-CV-A: alcance (en autónomo, con la recomendación)

| Q | Decisión |
|---|---|
| Q-CV-A-1, la 0354 de v2.8 | **Queda como nota L18.** El texto de v2.8 se descarga de HL7 con registro, y una cuenta no la crea Claude. **Opcional, para el autor:** si lo descarga, CV1 lo coteja antes del `RESULTADO` y cita la sección sin copiar el texto |
| Q-CV-A-2, OBX bajo SPM y grupos de más | **Solo recuento** (L-CV-7). Cabe en el tope |
| Q-CV-A-3, Google (Whistle) | **Solo si sobra tope** tras CV3, como Q-CV-1 |
| Q-CV-A-4, hojas XTN y 0396 de la guía | **Se traen en CV1** desde `HL7/v2-to-fhir` (`873b331`), si cuesta menos de 15 minutos, para cerrar L-CV-2 y L-CV-3 |
| Q-CV-A-5, issues de los proyectos | **Sí:** CV3 los lee con `gh api`, en solo lectura y fuera de la caja, y los guarda como referencias en el `RESULTADO` privado. No se escribe nada en los proyectos |
| Q-CV-A-6, publicar el perfil «guía» | **Se prepara en CV4 y se publica solo con el visto bueno de Víctor al diff**, como manda la condición 6 del ANTES |

## Siguiente: CV1

1. **E-CV-3, como mucho 1,5 h:** cada conversor en su caja, sin red, en una versión fijada con su huella. Si ninguno corre, la
   etapa para.
2. Las pruebas P-CV-1..18 en rojo.
3. El código: `conversion.py`, los dos puntos de entrada y una línea en `verificador.verificar`.
4. El primer Bundle real por el lector, antes del perfil.
