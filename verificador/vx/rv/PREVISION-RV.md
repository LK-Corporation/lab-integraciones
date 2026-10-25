# La previsión de la etapa 22, sellada antes de correr

Se escribió y se selló antes de cualquier corrida con Docker de esta etapa y antes de consultar GitHub (S-RV-12). Las cifras
exactas están en `PREVISION-RV.json`; su huella y la del aparato, en `SELLO-RV.txt`.

## Lo que se espera

- **Que sigan las nueve** (K = 9), con 0,73.
  - Cada una de Microsoft sigue con 0,98: de v7.0 a `main` no cambió nada de lo que convierte HL7 v2.
  - Las de LinuxForHealth siguen con 0,96. VX-L6, el registro anulado, con 0,9: es la más expuesta, porque `master` cambió
    estados en su tabla de v2 a FHIR, aunque no los de Immunization.
- **Que las ramas no hayan avanzado desde el 24-oct:** Microsoft 0,95 y LinuxForHealth 0,98.
- **Que el arrastre siga en `master`:** 0,9.
- **Que ninguna esté ya reportada:** alrededor de 0,98 cada una. El contraste de la etapa 20, de ayer, no encontró ninguna.
- **Que el control reproduzca la etapa 20:** 0,88; que lote y mensaje a mensaje den lo mismo con v1.1.0, 0,93.

## La previsión de Jev, al lado

Se le pasó a Jev un estado neutro (`estado_prevision_rv.md`) con tres preguntas, y su respuesta está en
`decision-jev-prevision-rv.md`:
- **Cuántas siguen:** siete u ocho, 0,59; las nueve, 0,41.
- **El arrastre sigue:** 1,0.
- **Alguna ya reportada:** 0,02.

La previsión del programador no se cambió al ver la de Jev.
