# La previsión de la etapa 24, sellada antes del primer push

Se escribió y se selló antes del primer push de la etapa, es decir, antes de que GitHub corra el flujo endurecido, el proyecto de
ejemplo o el run en rojo. Las cifras exactas están en `PREVISION-CI2.json`; su huella y la del aparato, en `SELLO-CI2.txt`.

Se selló dos veces, las dos antes del primer push y con las mismas cifras. La revisión a ciegas del primer push pidió cambiar los
teléfonos de dos mensajes del ejemplo y arreglar el ensayo (DV-CI2-9 en `decisiones-qci2.md`). Este es el segundo sello.

## Lo que se espera

- **La demostración endurecida, en verde en el primer push:** 0,85. Con los mismos informes byte a byte que en la etapa 23: 0,97.
- **El proyecto de ejemplo por la forma remota,** con sus dos llamadas y su comprobación en verde a la primera: 0,6.
- **El run en rojo como se espera a la primera** (el job rojo solo por la comparación, la comprobación en verde): 0,6, con el
  hallazgo sembrado en 164 casos.
- **Que lleguen las salidas del job llamado que falla:** 0,6. No decide el control del rojo; se anota.
- **El PR en verde a la primera:** 0,55.
- **Todo dentro del tope:** 0,65.
- **Pushes:** entre 4 y 7; lo más probable, 5. **Minutos por corrida** del ejemplo y del rojo: entre 1 y 4.
- **Lo más probable que falle,** por orden:
  1. la resolución del `uses:` remoto o el checkout del laboratorio en su commit;
  2. la descarga del artefacto;
  3. las salidas del job fallido;
  4. el guion de `ejemplo-propio` en una expresión;
  5. la imagen de Python por digest;
  6. el checkout del commit de fusión del PR;
  7. la higiene.

## La previsión de Jev, al lado

Se le pasó a Jev un estado neutro (`estado_prevision_ci2.md`) con cinco preguntas; su respuesta está en
`decision-jev-prevision-ci2.md`. Las cifras de arriba se fijaron antes de leerla y no se cambiaron. Es más optimista:

| | Programador | Jev |
|---|---|---|
| La demo en verde en el primer push | 0,85 | 0,88 |
| El ejemplo en verde a la primera | 0,6 | 0,87 |
| El rojo como se espera a la primera | 0,6 | 0,88 |
| Llegan las salidas del job fallido | 0,6 | 0,7 |
| Cuatro pushes o menos | por debajo de lo más probable (5) | 0,87 |
