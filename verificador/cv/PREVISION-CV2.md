# Previsión sellada de CV2 (etapa 14l, 23-oct-2026)

**Sellada antes de correr ningún conversor sobre el corpus.** La versión que manda es `cv/PREVISION-CV2.json`, con su huella
en `cv/SELLO-CV2.txt`. Este documento la explica.

## De dónde sale

- **La previsión de Fable, a ciegas, sin tocar sus probabilidades ni sus rangos** (`cv/diseno-conversores-fable.md` §7.1 y
  §7.2), con tres cambios:
  1. **DV-CV-7.** El corpus de ADT son 263 mensajes, no 479: A1 ya incluye las 216 bases de E2.
  2. **Dos mecanismos que salen de las decisiones de Jev contrarias a Fable,** con probabilidad baja y marcados como añadidos
     al sellar:
     - **MC-ADT-13:** PV1-2 = N sin Encounter, que con Q-CV-D-6 cuenta;
     - **MC-ADT-14:** FN con subcomponentes unidos en `family`, que con Q-CV-D-9 cuenta.
  3. **La regla de asignación,** escrita ahora, antes de ver nada: dice qué hallazgo cae en qué mecanismo, para que la
     comparación con lo observado sea mecánica.
- **Las cuentas del corpus** (`cv/CUENTAS-CV2.json`): en cuántos mensajes puede morder cada mecanismo. Es la cota de lo que
  puede salir.
- **Lo visto antes de sellar:** solo los recuentos del lector de CV1-d sobre 4 Bundles (emparejamiento, sobrantes, otros
  tipos), ningún hallazgo del perfil. La previsión no se ha movido por ello.

## Identidad

| | |
|---|---|
| Juez | `63d40cd0…`, servidor 1.1 |
| Microsoft | v7.0 (`253307f`), huella `766f8938…` |
| LinuxForHealth | v1.1.0 (Maven Central), huella `ac41f71b…` |
| Corpus | `aa83359a…`: ADT 263, ORU 40 y 65 muestras (DV-CV-10: normalizadas a CR y sin BOM antes de convertir) |
| Decisiones | Las de Jev. La sensibilidad se calcula con la alternativa de Q-CV-D-3, 5 y 9 |

## El corpus en cuentas

- **ADT (263):**
  - por evento: A01 33 · A02 34 · A03 33 · A04 35 · A08 32 · A11 32 · A13 32 · A31 32;
  - 11 con un PID-8 fuera de la 0001;
  - 7 sin PV1: los principios de mensaje del cap. 3, 2 de ellos también sin PID.
- **ORU (40):** 1 con un NM imposible, 1 sin PID y 1 con un OBX fuera de OBR.

| Mecanismo | Qué | Prob. Microsoft / LinuxForHealth | Oportunidad |
|---|---|---|---|
| MC-ADT-1 | PV1-2 → `class` literal v2-0004 | M / M | 208 |
| MC-ADT-2 | PID-8 vacío → `gender unknown` | M / M | 4 |
| MC-ADT-3 | PL → una sola Location o solo PL.1 | M-A / M | 256 |
| MC-ADT-4 | PID-16 → v2-0002 literal | M / M | 8 |
| MC-ADT-5 | PV1-10 MED/URO → v2-0069 literal | M / M | 24 |
| MC-ADT-6 | PID-7 de menos precisión → fecha completada | B-M / B-M | 32 |
| MC-ADT-7 | XPN.7 unmatched → `use` inventado | M / B | 32 |
| MC-ADT-8 | telecom: XTN.1 antes que XTN.12; XTN.4 sin `email` | M / M | 8 |
| MC-ADT-9 | `Encounter.status` fuera del conjunto | B / B-M | 65 |
| MC-ADT-10 | participantes: solo PV1-7, o solo `display` | M / M | 32 |
| MC-ADT-11 | rechazo por segmentos fuera de sitio o Z | B / B-M | 32 |
| MC-ADT-12 | DTM sin zona → `dateTime` sin zona o fecha | B / B-M | 36 |
| MC-ADT-13 | PV1-2 = N sin Encounter (Q-CV-D-6, añadido) | B / B | 27 |
| MC-ADT-14 | FN unido en `family` (Q-CV-D-9, añadido) | B-M / B-M | 8 |
| MC-ORU-1 | `1.20` → `1.2` | A / A | 2 |
| MC-ORU-2 | SN mal ramificado o comparador perdido | M-A / M | 4 |
| MC-ORU-3 | OBX-6: unit, code o system | M / M | 26 |
| MC-ORU-4 | OBX-8 → system v2-0078 | M / M | 31 |
| MC-ORU-5 | OBR-8 → solo `effectiveDateTime` | M / M | 1 |
| MC-ORU-6 | TX/FT: escapes o repeticiones | M / M | 2 |
| MC-ORU-7 | `result[]` cruzados u Observation de más | B / B-M | 2 |

## Categorías, por conversor y familia (rangos de Fable)

| | correcto | fallo_silencioso | rechazo_incorrecto | indeterminado |
|---|---|---|---|---|
| Microsoft · ADT | 35-65 % | 30-60 % | 0-5 % | ≤ 2 % |
| Microsoft · ORU | 20-50 % | 45-80 % | 0-5 % | ≤ 2 % |
| LinuxForHealth · ADT | 30-60 % | 35-65 % | 0-10 % | ≤ 2 % |
| LinuxForHealth · ORU | 20-50 % | 45-80 % | 0-10 % | ≤ 2 % |

**Mecanismos distintos que cuentan,** por conversor: de 3 a 6 en ADT y de 2 a 5 en ORU.

**Lo que no se prevé y sería la señal buena:** un `recurso_inventado`, una `referencia_rota` en `subject` o un `fhir_invalido`
masivo.

## Fuera de previsto

Cuenta como fuera de previsto cualquiera de estas cosas:
- un mecanismo que cuenta y no casa con ninguno de la lista;
- un porcentaje de categoría fuera de su rango;
- un indeterminado por encima del 2 %;
- un conversor que rechaza más del 10 % del corpus 2.5;
- un número de mecanismos distintos fuera del rango.

Cada uno se adjudica antes de CV3 al juez, al perfil, al corpus o a la caja, con su cita. Si es un defecto del juez, se
arregla con su prueba y CV2 se repite entero, como mucho dos veces.

## La frase prevista (para CV4)

N ≥ 2, K entre 1 y 2, D ≥ 3, C ≥ 10. Al menos una nueva confirmada en alguno de los dos: 0,8.
