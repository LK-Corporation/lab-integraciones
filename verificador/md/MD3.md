# MD3: contraste, clase, pares mínimos y revisión adversaria (etapa 26)

> **Corregido el 31-oct (etapa 28, DV-MD-15):** MD-M8, MD-L7 y MD-M7 se retiraron, porque se apoyaban en T02 con TXA-19 «OB»
> o «UN», estados que la figura 9-2 de v2.5 no da para T02. La cuenta es 3 nuevas y 9 ya declaradas
> (`md/CLASES-MD3.json`). Lo de abajo es el documento de antes de la corrección.

**La regla.** Es la del estudio de conversores y la de VX3 (`cv/diseno-conversores-fable.md` §4.3, R-CV-9), escrita antes de medir:
- **`ya_declarada`.** La misma diferencia aparece en una salida esperada publicada, en una prueba que la afirma, en la
  documentación o en un issue. El código de las plantillas no cuenta.
- **`convencion`.** Releídos el ConceptMap y la hoja CSV, la guía admite lo observado.
- **`nueva`.** Cualquier otro caso. Es confirmada si se reproduce con un par mínimo.

## Cómo se hizo

1. **La lista.**
   - **Primera corrida:** `md/hallazgos_md3.py` numeró 23 hallazgos de MDM (`md/HALLAZGOS-MD3.json`). PV1 y PID quedan fuera:
     son el perfil de `adt_conv`, ya clasificado en `cv/CLASES-CV3.json`.
   - **Tras la repetición 1:** quedan 17 (`md/HALLAZGOS-MD3-r1.json`).
2. **El contraste, a ciegas de la clasificación.**
   - **Agentes:** dos, uno por conversor, en solo lectura y sin ejecutar código de terceros.
   - **Qué leyeron:** salidas esperadas, pruebas, documentación e issues (`md/contraste-md3-*.json`).
   - **Microsoft:** 8 declaradas, 3 no y 1 dudosa.
   - **LinuxForHealth:** 7 declaradas, 3 no y 1 dudosa.
3. **La revisión adversaria, a ciegas del contraste** (`md/revision-adversaria-md3.json`).
   - Un agente intentó tumbar los 23 con la guía y el estándar: tumbó 6, dejó 2 en duda y sostuvo 15.
   - El hallazgo más serio fue del corpus: 33 bases sin TXA-22, que v2.5 exige con AU y LA. Se arregló con la repetición 1
     (DV-MD-7..14, `md/MD2.md`).
4. **Los pares mínimos** (`md/pares_mdm.py`).
   - Son siete pares sobre la base B26, cada uno con la diferencia mínima, corridos con los dos conversores en su caja.
   - Los siete confirman su hallazgo en el conversor candidato: en las versiones fijadas (`md/RESULTADO-MD3-pares.json`) y en las
     ramas principales (`md/RESULTADO-MD3-pares-main.json`).
5. **La adjudicación.** La hice yo, con los precedentes del estudio y de VXU, en `md/CLASES-MD3.json`.

## El resultado

| | Microsoft | LinuxForHealth | Total |
|---|---|---|---|
| **Nuevas y confirmadas** | 2 (2 fuertes) | 3 (2 fuertes) | **5** |
| Ya declaradas | 5 | 5 | **10** |
| Convención (notas del juez final) | 1 | 2 | **3** |
| Dudosas (no cuentan) | 1 (MD-M6) | 1 (MD-L6) | 2 |
| Muestras inválidas (no cuentan) | 1 (MD-M9) | — | 1 |

**Las cinco nuevas:**
- **MD-M5,** rechazo con TXA-8 repetido;
- **MD-M8,** «OB» que sale como `entered-in-error`;
- **MD-L3,** el texto TX perdido detrás de un OBX CE;
- **MD-L7,** «UN» que sale como `current`;
- **MD-L5,** el FT con formato crudo.

**Ninguna depende solo de una decisión de confianza baja de Jev.**

**MD-M7 frente a MD-L7.** «UN» sale como `current` en los dos conversores. En Microsoft está declarado por una salida esperada
de otro mensaje (OUL_R22); en LinuxForHealth, no.
