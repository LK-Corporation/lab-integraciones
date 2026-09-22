/// Brazo (a) — SOLO EL MENSAJE.
///
/// Mide si el modelo sabe leer HL7. NO mide triaje: sin la traza no puede
/// saber si el motor acepto o rechazo, ni distinguir un fallo del mensaje de
/// uno del entorno.
///
/// Es un envoltorio fino sobre Lab.Fase12.Datos a proposito: los brazos se
/// construyen QUITANDO HERRAMIENTAS, no cambiando el prompt ni la logica. Si
/// cada brazo tuviera su propia implementacion, las diferencias entre brazos
/// medirian el codigo en vez de la evidencia.
///
/// Fase 12, 20-sep-2026.
Class Lab.Fase12.HerrA Extends %AI.ToolSet
{

XData Definition [ MimeType = application/xml ]
{
<ToolSet Name="TriajeSoloMensaje">
  <Description>Lectura del mensaje HL7 de una traza de integracion.</Description>
  <Tool Name="mensaje" Method="mensaje">
    <Description>Devuelve el mensaje HL7 tal como llego por el cable, un segmento por linea. Pasa trazaId, el identificador de traza que te han dado en la pregunta.</Description>
  </Tool>
</ToolSet>
}

ClassMethod mensaje(trazaId As %String) As %String
{
	Return ##class(Lab.Fase12.Datos).Mensaje(trazaId)
}

}
