# Resultado AG1: sellado del piloto del agente (12-oct-2026)

**AG1 pasa, con una puerta declarada.** Todas las puertas del diseño (§5) se cumplen salvo el control de clave barajada de la
referencia sin modelo, que Jev decidió congelar y declarar (Q-AG-18). El sello está en [`etapa/SELLO-AG1.md`](etapa/SELLO-AG1.md)
y se commitea antes de cualquier tirada.

## Lo que queda sellado

- **Corpus:** 5 H (fallos históricos reales de ORU, árbol exacto de antes del arreglo), 6 R (fallos vivos del congelado), 12 M
  (mutantes en LABMUT, LABADTMUT y Mirth) y 3 limpios. H + R = 11. Se retiraron 4 H por las puertas (1 o 0 disparadores),
  antes de ver nada del agente.
- **Referencia sin modelo:** 9/12 en M, 0 falsas alarmas, registro limpio. Clave barajada 0,375 contra un azar de 0,023: las
  verdades del corpus se concentran en pocas unidades que comparten casos distintos. Se reporta como acierto «sin mirar el caso».
- **Evaluador:** separa sus cuatro controles (vacío, fix, inocuo, dañino) en las cuatro cajas: LABORUMUT, LABMUT, LABADTMUT y Mirth.
- **Cadena nueva:** repite AG-pre (R5 5/5 y H-MI-1 11/11, colateral 0). El MCP del agente lista `adt_fhir` y `oru_fhir`.

## Lo aprendido al sellar

1. **Un control negativo puede ser ciego por el caso, no por el evaluador.** El parche dañino sobre MMI-6 dejó 0 colateral porque
   ese mutante muerde todos los aceptados y su regresión son solo rechazos. Se rehízo el control sobre H-MI-1 (DV-AG-8) y se
   declara el límite (L-AG-14): en esos casos, el daño al AA solo se ve en los disparadores.
2. **Un fichero de resultados puede quedarse atrás del código.** `ref_controles.json` llevaba los números de la iteración 1 de la
   referencia (8/12), ya deshecha. Se rehízo con la referencia congelada (9/12) antes de tomar su huella.
3. **Los permisos importan en la caja Mirth.** Corrida como root, no encuentra la clave del usuario FHIR, y un log de root no lo
   puede sobrescribir el usuario. La caja Mirth corre con `systemd-run --user`.

## Lo siguiente (AG2)

Por el orden del diseño: REF sobre los 31 casos, luego AG con 2 réplicas en orden sembrado, luego DS. Falta preparar el adaptador
del brazo DeepSeek. Siguen abiertas para Víctor Q-MI-11, Q-AG-8/14 (contra Jev por su alcance), Q-AG-10/11/16 (a cara o cruz en
Jev) y Q-AG-18.
