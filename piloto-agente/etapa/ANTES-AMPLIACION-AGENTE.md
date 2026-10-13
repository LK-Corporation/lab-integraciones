# ANTES de la ampliación del piloto del agente (AMP), 13-oct-2026

## Por qué

El piloto (AG0-AG4) dejó dos frases (`RESULTADO-AG2-AG3.md`):
- **Frase 1:** el agente funciona: localiza top-3 en 10/11 casos reales y arregla 6/11.
- **Frase 2:** es indeterminado frente a la referencia sin modelo en localizar, que es la medida primaria: Δ +0,36, McNemar 5 a 1,
  p = 0,22, con n = 11.

Toda la ventaja está en H (5/5 frente a 1/5); en R empatan (5/6). El diseño prohibía añadir casos dentro del piloto, porque
eso es mirar los datos para decidir n. **Víctor decide ampliar el corpus (13-oct)**, así que la ampliación es un estudio
nuevo, con diseño propio preinscrito.

## Alcance fijado por Víctor

- **Ampliar el corpus** con las fuentes medidas en `OPCIONES-TRAS-PILOTO.md`:
  - **H nuevos**, aislados por hunks (como DV-AG-2) desde los commits que cerraron deudas de los circuitos: la pieza común
    (`14e17de`) y la cabecera común. Previsto: 1-3.
  - **R nuevos** de las deudas vivas declaradas: CIR-ADT-7, CIR-ADT-8, CIR-MS-3, CIR-MS-4, CIR-MT1 y CIR-MT4. Las dos MT exigen
    una caja nueva para LABMULTI. Previsto: 4-6.
- **Lo mismo que en el piloto,** salvo que el diseño diga otra cosa y lo justifique:
  - los brazos AG (2 réplicas) y REF, la referencia congelada sin tocar;
  - la consigna, el lanzador, el evaluador, las puertas por caso y el formato de las dos frases.
- **El brazo DS** solo si alcanza el saldo, que hoy es unos 0,5 USD.

## Lo que el diseño tiene que resolver

1. **El análisis, sabiendo que n se amplió después de ver p = 0,22.** Si los 11 casos del piloto se juntan con los nuevos sin
   más, el p sale optimista: es la parada opcional. El diseño elige cómo analizar y lo justifica con su alternativa. Por
   ejemplo:
   - solo los casos nuevos, como réplica independiente;
   - juntos, con una corrección de diseño secuencial;
   - otra opción.

   Escribe la regla de decisión en números antes de medir, y di qué se publica si la ampliación y el piloto discrepan.
2. **Las puertas de los casos nuevos.** En particular, las que fallaron en el piloto:
   - una regresión sellada sin aceptados (L-AG-14, L-AG-16);
   - la firma que no es estable en ADT (DV-AG-16);
   - las pistas textuales del verificador (§6.2). Las deudas de los circuitos están descritas en `deudas_circuito_*`, que se
     quita de lo que ve el agente; hay que comprobar que no se filtran por otra vía.
3. **La caja LABMULTI:** cómo se crea, cómo se exporta su árbol y cómo se evalúa (puertos, una producción a la vez, restauración).
4. **El coste y las reglas de parada,** en números.

## Hecho cuando

- El diseño (`diseno-ampliacion-fable.md`) está escrito, sus Q-AMP están decididas (Jev; las de alcance, Víctor), y el sello AMP
  está commiteado **antes de la primera tirada**.
- Las tiradas REF y AG (y DS si alcanza) están hechas y evaluadas en sus cajas.
- `RESULTADO-AMP.md` da las dos frases con la regla preinscrita, aunque salgan «no aporta» o «indeterminado».

**Tope: 1,5 sesiones.** Si al pasar las puertas quedan menos de 4 casos nuevos que cuentan, se para y se publica eso
(«la ampliación no da casos»), sin buscar más fuentes.
