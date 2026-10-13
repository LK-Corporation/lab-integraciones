# Estado: el control de «clave barajada» de la referencia sin modelo no cae (Q-AG-18)

Redactado el 12-oct-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

Un piloto compara un agente con modelo con una «referencia» determinista sin modelo. Las dos localizan, en el código de circuitos
de integración, la causa de un fallo que un juez ya detectó. La localización se puntúa por **unidad** (método o bloque): acierta si
alguna de sus tres propuestas cae en una unidad de la verdad. La referencia busca en el código los campos HL7 del hallazgo, sus
nombres canónicos y los códigos de acuse. Suma términos genéricos según la clase del fallo (acuse, fidelidad) y da un peso extra a
los ficheros según su papel por el nombre (Transform/Util para fidelidad, Ack/Rechazo para acuse, Operation/Fhir para almacén).

Antes de congelarla, el diseño exige tres controles. Uno es la **clave barajada**: se le da el caso de un fallo A con el código del
caso B y se mira si acierta la verdad de B. Su tasa debe caer a «azar + 0,10», con azar = 3 / número de unidades del árbol
(≈ 0,02). Según el diseño, «si no cae, hay una fuga (p. ej. una regla que acierta por el nombre del fichero más probable) y se
corrige antes de congelar», con un máximo de dos iteraciones.

## Lo medido

- **Corpus:** 23 casos con fallo (5 históricos reales, 6 fallos vivos, 12 mutantes de control). Casi todos los fallos vivos y la
  mitad de los mutantes están en el MISMO árbol de código.
- **La referencia:** localiza 9 de 12 mutantes (la barra de «adversario fuerte» del diseño es ≥ 9), 0 falsas alarmas en los casos
  limpios, y su registro de lectura está limpio (no lee nada fuera de su carpeta).
- **Clave barajada: 0,375 (9 de 24 pares), frente a un azar de 0,023.**
  - Con árbol distinto, 3 de 11.
  - Con el mismo árbol, 6 de 13.
- **Los aciertos se explican así:**
  - Las verdades del corpus se concentran en pocas unidades «calientes» del código que procesa los campos (el método que
    envía a FHIR, la transformación, el que decide el rechazo, el que lee el nombre). Casos distintos comparten unidad.
  - Hay verdades de 3 a 5 unidades.
  - La referencia no lee la clave.
- **Iteración 1** (solo pueden salir líneas con un término propio del caso): la clave barajada sigue en 0,375 y los mutantes bajan
  a 8 de 12. Se deshizo.
- **Para que el control cayera** habría que quitarle a la referencia lo que la hace fuerte en los mutantes (el peso por papel del
  fichero y los términos de clase). La lección del laboratorio dice que un adversario más débil puede dar un falso positivo a favor
  del agente («aporta» sin aportar); uno más fuerte, solo un falso negativo.
