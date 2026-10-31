> *Copia pública: se quitaron las alusiones al autor. El resto es el original del laboratorio.*

# Estado: ¿quién hace el diseño a ciegas de la etapa 26 (MDM_T02)? (31-oct-2026, 05:07)

Redactado el 31-oct-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

El laboratorio amplía su juez de conversores HL7 v2 → FHIR a un cuarto tipo de mensaje, MDM_T02. El método de las etapas
anteriores pide que el diseño lo haga otro modelo, a ciegas: lee solo una carpeta cerrada con el juez, el estándar y la guía,
sin nada de lo que devuelven los conversores. Ese diseñador ha sido siempre Fable. El programador, otro modelo, sigue el diseño;
las preguntas de diseño las decide Jev.

La parada global es el 20-nov (quedan 20 días). La
etapa tiene un tope de cuatro sesiones.

## Hechos

1. **Fable se quedó sin cupo a mitad del encargo.** Había leído la carpeta entera y no llegó a escribir nada. No se sabe cuándo
   vuelve a tener cupo: puede ser en horas.
2. **La carpeta cerrada está montada y comprobada** (340 ficheros, sin nada de los conversores). Cualquier modelo nuevo puede
   leerla igual de a ciegas.
3. **El ANTES de la etapa pide «diseño a ciegas por otro modelo, que no vea lo que devuelven los conversores».** No nombra
   a Fable. La memoria del proyecto sí dice que diseña Fable.
4. **Los otros modelos disponibles:**
   - el mismo modelo que programa, en un contexto nuevo que solo lee la carpeta; sería otra instancia del mismo modelo;
   - un modelo más pequeño y distinto, que es otro modelo pero con menos capacidad.

   El diseño de la etapa parecida anterior (VXU) ocupó unos 115 KB y lo programó otro modelo sin problemas.
5. **Esperar** deja parada la etapa hasta que vuelva el cupo. Mientras tanto, solo se pueden adelantar tareas que no dependen
   del diseño.
6. **Hay un uso de cupo en juego.** Cualquier diseño consume cupo. El mismo encargo
   con otro modelo puede costar parecido.

## La pregunta

¿Quién hace el diseño a ciegas de MDM_T02?
- (a) **Esperar a Fable** y retomarlo cuando vuelva el cupo.
- (b) **El mismo modelo que programa,** en un contexto nuevo y con la misma carpeta cerrada, declarándolo como desviación.
- (c) **Un modelo más pequeño y distinto,** con la misma carpeta, declarándolo como desviación.
