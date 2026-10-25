# La previsión de la etapa 23, sellada antes del primer push

Se escribió y se selló antes del primer push al repositorio público, es decir, antes de cualquier corrida del flujo en GitHub
Actions. Las cifras exactas están en `PREVISION-CI.json`; su huella y la del aparato, en `SELLO-CI.txt`.

Se selló dos veces, las dos antes del primer push y con las mismas cifras. La revisión a ciegas encontró un defecto del flujo en
el camino de fallo, que los tres controles no recorren (DV-CI-12 en `decisiones-qci.md`). Se arregló, y este es el segundo
sello, el del flujo arreglado.

## Lo que se espera

- **Los tres controles en verde en el primer push:** 0,5. El más frágil es el real (0,6 a la primera), porque depende de la red
  del runner hacia Maven Central y Docker Hub y de la caja con su Docker.
- **Que acaben en verde dentro del tope:** 0,85.
- **Pushes hasta los tres en verde:** entre 1 y 3; lo más probable, 1.
- **Cuando el real llegue a comparar, los mismos veredictos que en el laboratorio:** 0,92. La huella del conversor traído en el
  runner, la del estudio: 0,95.
- **El positivo sembrado:** falla en 303 casos, los mismos que en el laboratorio, y solo por PID-7.
- **Lo más probable que falle,** por orden:
  1. la mecánica del flujo reutilizable, en lo que GitHub haga distinto del ensayo;
  2. los montajes de la caja con el Docker y el usuario del runner;
  3. la red del runner;
  4. una bandera de la caja;
  5. el entorno de Python de las pruebas.

## Lo que cambió el ensayo local

El primer borrador de esta previsión se escribió antes del ensayo local (`ensayo_flujo.py`). El ensayo corre en la máquina del
laboratorio los pasos de shell de los dos YAML, con sus expresiones evaluadas, y salió todo en verde. El borrador no se selló;
sus cifras están en `PREVISION-CI.json` (`antes_del_ensayo`):
- **los tres en verde en una sesión:** 0,75;
- **el real a la primera:** 0,45;
- **pushes:** entre 1 y 4, lo más probable 2.

## La previsión de Jev, al lado

Se le pasaron a Jev dos estados neutros con las mismas tres preguntas: uno antes del ensayo (`estado_prevision_ci.md`) y otro
después (`estado_prevision_ci_2.md`). Sus respuestas están en `decision-jev-prevision-ci.md` y `decision-jev-prevision-ci-2.md`.
La previsión de arriba no se cambió al verlas.

| | Antes del ensayo | Después |
|---|---|---|
| Los tres en verde en el primer push | 0,18 | 0,46 |
| Más de cuatro pushes, o no se consigue | 0,8 | 0,67 |
| Un solo push | 0,03 | 0,18 |
| El real da los mismos veredictos | 0,61 | 0,84 |
