# Estado: seis decisiones de diseño de la etapa 23, el verificador en la integración continua (25-oct-2026)

Redactado el 25-oct-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

Un laboratorio publicó un verificador determinista que juzga conversores HL7 v2 → FHIR R4, y una herramienta que pasa cualquier
conversor por él con un adaptador y una orden. Esta etapa, ya fijada, hace un flujo reutilizable de GitHub Actions: un proyecto
de conversor lo llama en cada cambio, el flujo corre el conversor en una caja de Docker sin red, lo juzga sobre un corpus público
y falla solo si aparece un hallazgo que no estaba en la línea base del proyecto.

Lo fijado no se discute:
- **la línea base** guarda, por caso, el veredicto del juez: estado de la salida, categoría, subtipo y el conjunto de
  hallazgos que cuentan (hecho, clase y subtipo);
- **lo que desaparece** es un arreglo: no falla, y el flujo deja una base propuesta para que el proyecto la adopte en su PR;
- **sin secretos y con permisos de solo lectura;**
- **los controles corren en GitHub Actions:** negativo, positivo sembrado y uno real con un conversor de código abierto (unos
  411 mensajes; en lote cuesta un minuto de caja, y mensaje a mensaje unos 30 minutos, porque ese conversor arrastra estado
  entre mensajes del mismo proceso);
- **tope:** una sesión.

## Las preguntas

1. **Un caso que está en la corrida y no en la base, con hallazgos que cuentan.** Por ejemplo, el proyecto añadió un mensaje
   propio, o subió la versión del laboratorio y el corpus creció.
   - (a) falla: cada hallazgo suyo es nuevo;
   - (b) no falla: se lista como caso nuevo y entra en la base propuesta;
   - (c) falla solo si el caso es de los mensajes propios del proyecto.
2. **Un caso de la base que no está en la corrida.**
   - (a) falla;
   - (b) aviso, y la base propuesta lo quita;
   - (c) falla solo si el corpus es el mismo que el de la base (desapareció sin que cambiara el corpus).
3. **El modo del control real con el conversor que arrastra estado.**
   - (a) en lote, el modo de referencia del estudio (un minuto de caja);
   - (b) mensaje a mensaje (unos 30 minutos por corrida, sin arrastre);
   - (c) en lote en cada cambio, y mensaje a mensaje solo cuando se lance a mano.
4. **La huella del juez es distinta de la de la base,** en el modo normal de un proyecto.
   - (a) aviso: la comparación sigue, y lo que salga nuevo falla;
   - (b) falla siempre: el proyecto regenera la base al subir la versión del laboratorio;
   - (c) aviso, y la base propuesta se marca «juez cambiado».
5. **Qué lleva el artefacto que deja el flujo, por omisión.**
   - (a) el informe, el juicio, el veredicto, la base propuesta y los registros de las cajas, sin las evidencias ni el corpus;
   - (b) además las evidencias y el corpus (más pesado; lleva los mensajes);
   - (c) solo el informe y el veredicto.
6. **Cuándo corre la demostración en el repositorio del laboratorio.**
   - (a) en cada push a la rama principal y en cada PR, solo si cambian el verificador, los flujos o las pruebas; y a mano;
   - (b) en todo push, como la higiene;
   - (c) solo a mano y una vez por semana.
