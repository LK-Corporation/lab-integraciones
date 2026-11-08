> *Copia pública: el párrafo «Fijado en autónomo» marca como no publicadas la hoja de ruta y la decisión de ruta del laboratorio; el resto va literal.*

# ANTES: etapa 39, lo que queda sin clase en el estudio de conversores (FIJADO el 8-nov-2026)

**Fijado en autónomo**, dentro de la hoja de ruta (`HOJA-DE-RUTA.md`, no publicada). Jev eligió esta etapa con 0,53 (`decision-jev-ruta22.md`, no publicada); el
fallo del juez con PD1-7 quedó en 0,29 y pausar en 0,16.

## La pregunta (fija)

> Con el juez y el aparato de hoy, ¿qué hallazgos que cuentan quedan sin clase en los corpus que clasifica `cv/cv3_clases.py`? ¿Y
> debe el aparato fallar cuando quede alguno, en vez de solo listarlo?

## Punto de partida (medido)

- **`cv/cv3_clases.py` dice que «comprueba que nada que cuente quede sin clase», pero solo lo lista** en su salida (`sin_clase`), y
  sale con 0.
  - Así pasaron sin verse, desde el 24-oct, 8 hallazgos de M-4. La etapa 38 lo arregló en la regla de M-4.
  - Con el juicio de hoy del estudio, después de la 38, no queda nada sin clase.
- **Lo usan varias etapas:**
  - la 33, sobre la versión 2 del corpus (`ga/`);
  - la 37 y la 38, sobre el estudio.

  Lo llaman `ga/comparar_ga.py`, `ga/cifras_ga_b.py`, `ga/cruce_ga.py`, `ga/riesgo_ga.py` y `cl/reproducir_clases_cl.py`.
- **Los JSON de clases de etapas pasadas se escribieron con lo sin clase no vacío.** `ga/CLASES-GA-v2.json` tiene 39:
  - 8 de M-4;
  - 30 de la Observation de ACC de Microsoft;
  - 1 de PID-8 de LinuxForHealth.

  Las 31 últimas son las 2 candidatas de la 33, que la 36 resolvió y la 37 llevó al juez y a M-28.
- **El aparato está sellado** en la etapa 33 (`ga/SELLO-GA.txt`, bloques 1 a 9).

## Condiciones que no se negocian

1. **Lo de siempre:**
   - el código de terceros corre en su caja;
   - los proyectos de los conversores no se tocan;
   - cada push, por la opción B, con el ensayo y la comprobación de después del push.
2. **Primero se mide, sin cambiar nada:** lo sin clase de hoy en cada corpus que clasifica el aparato, con el juez y el aparato de
   hoy.
3. **Si hay que cambiar código,** el diseño va a ciegas antes y cada cambio lleva su prueba en rojo antes. Un cambio del aparato va
   con un bloque nuevo en el sello de la 33.
4. **Los resultados sellados de etapas pasadas no se tocan:** sus JSON conservan lo que dieron.
5. **Si lo que queda sin clase es una clase nueva del estudio,** no se clasifica en esta etapa: se declara y es candidata a otra.

## Qué se mide

- **Lo sin clase de hoy,** en cada corpus que clasifica el aparato: el estudio y la versión 2 del corpus de la 33, por conversor,
  mecanismo y firma, con su causa.
- **Qué pasaría en cada guion que llama al aparato** si el aparato fallara con lo sin clase no vacío.

## Previsión (se sella antes de medir)

Cuántos hallazgos sin clase quedan hoy en cada corpus, y si el aparato debe fallar.

## Hecho cuando

- **Un documento de resultado,** `RESULTADO-SINCLASE.md`, con la frase: «Con el juez y el aparato de hoy quedan N hallazgos sin
  clase en los corpus que clasifica `cv/cv3_clases.py`; el aparato [falla / no falla] cuando queda alguno».
- **Si cambia algo publicado,** publicado con la opción B y comprobado después del push.

## Tope

**Una sesión, y un lector a ciegas** (hasta dos pasadas) si se publica.

## Regla de parada

- **Lo sin clase de hoy no se explica dentro del tope:** se declara lo medido y se publica eso.

## Fuera de la etapa

- Clasificar clases nuevas del estudio.
- Los cabos de la 37: PD1-7 y la lectura de los tipos de v2.6 y posteriores.
