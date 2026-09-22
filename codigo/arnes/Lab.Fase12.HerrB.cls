/// Brazo (b) — MENSAJE, TRAZA Y LOG. El brazo principal.
///
/// Es lo que se ve un lunes en el Visual Trace y el Event Log. Y es el unico
/// de los tres que permite detectar un fallo silencioso, porque el fallo
/// silencioso NO esta en el mensaje ni en el log: esta en la DISCREPANCIA
/// entre lo que venia en el HL7 y lo que produjo la transformacion. Hace falta
/// tener los dos delante.
///
/// El resultado informativo del experimento no es la nota de este brazo, son
/// las diferencias (b)-(a) y (b)-(c). Si (b) se parece a (a), el agente no usa
/// el motor y "triaje" es un nombre bonito para "leer HL7". Si (b) se parece a
/// (c), no lee el mensaje.
///
/// PASO 4 (20-sep): LA PUERTA DE ORDEN DE LECTURA. El prompt pide leer el
/// mensaje crudo y juzgarlo ANTES de mirar el ACK, porque un modelo de 30B se
/// ancla en lo primero que parece autoritativo — y si lee el ACK primero, no
/// detecta ni un silencioso. Eso NO SE PUEDE PEDIR: medido el 20-sep,
/// qwen3-coder:30b pide `mensaje` y `log` EN PARALELO, en la misma vuelta,
/// antes de leer ninguna de las dos; y Ollama IGNORA `parallel_tool_calls:
/// false`. Asi que el orden se impone aqui: `traza` y `log` no contestan
/// hasta que se haya llamado a `mensaje` de esa traza.
///
/// LA PUERTA VIVE EN ESTE BRAZO Y SOLO EN ESTE. En HerrA solo hay `mensaje`,
/// y en HerrC NO HAY `mensaje`: ponerla alli dejaria el brazo (c) muerto y
/// (b)-(c) sin sentido. Por eso esta aqui y no en Lab.Fase12.Datos, que es
/// comun a los tres.
///
/// El rechazo NO cuenta como llamada: se comprueba antes de Autorizar(), asi
/// que los contadores del informe siguen midiendo lecturas de verdad.
///
/// Fase 12, 20-sep-2026.
Class Lab.Fase12.HerrB Extends %AI.ToolSet
{

XData Definition [ MimeType = application/xml ]
{
<ToolSet Name="TriajeCompleto">
  <Description>Lectura del mensaje, la traza y el log de una traza de integracion.</Description>
  <Tool Name="mensaje" Method="mensaje">
    <Description>Devuelve el mensaje HL7 tal como llego por el cable, un segmento por linea. Llamala SIEMPRE LA PRIMERA: las otras dos no contestan hasta que la hayas leido. Pasa trazaId, el identificador de traza que te han dado en la pregunta.</Description>
  </Tool>
  <Tool Name="traza" Method="traza">
    <Description>Devuelve el recorrido del mensaje por la produccion, el mensaje canonico que produjo la transformacion, y el ACK que se devolvio al emisor. NO devuelve el HL7 de entrada: para eso esta mensaje(). Requiere haber llamado antes a mensaje() con esa misma traza. Pasa trazaId.</Description>
  </Tool>
  <Tool Name="log" Method="log">
    <Description>Devuelve las entradas del Event Log de esa traza, cada una con su tipo (ERROR, WARNING, INFO), su texto y el tiempo transcurrido desde el primer apunte. Requiere haber llamado antes a mensaje() con esa misma traza. Pasa trazaId.</Description>
  </Tool>
</ToolSet>
}

/// El aviso que sustituye a la respuesta cuando aun no se ha leido el mensaje.
ClassMethod Pendiente(pHerramienta As %String) As %String
{
	Return "Todavia no. Lee primero el mensaje HL7 crudo con mensaje(trazaId) y juzgalo por tu cuenta; " _ pHerramienta _ "(trazaId) contesta despues. El mensaje es el hecho; lo que devuelven las otras dos herramientas es lo que el circuito opina de ese hecho, y conviene formarse un criterio antes de leer una opinion."
}

ClassMethod YaLeyoMensaje(pTraza As %String) As %Boolean
{
	Return ##class(Lab.Fase12.Datos).LlamadasDe(pTraza, "mensaje") > 0
}

ClassMethod mensaje(trazaId As %String) As %String
{
	Return ##class(Lab.Fase12.Datos).Mensaje(trazaId)
}

ClassMethod traza(trazaId As %String) As %String
{
	Return:'..YaLeyoMensaje(trazaId) ..Pendiente("traza")
	Return ##class(Lab.Fase12.Datos).Traza(trazaId)
}

ClassMethod log(trazaId As %String) As %String
{
	Return:'..YaLeyoMensaje(trazaId) ..Pendiente("log")
	Return ##class(Lab.Fase12.Datos).Log(trazaId)
}

}
