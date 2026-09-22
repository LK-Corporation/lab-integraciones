/// Brazo (c) — SOLO TRAZA Y LOG, sin el mensaje.
///
/// Mide si se puede diagnosticar desde los sintomas sin la causa delante. Es
/// la situacion de quien recibe un aviso de madrugada y abre el Event Log
/// antes de ir a buscar el mensaje.
///
/// En este brazo hay muchos casos que NO se pueden diagnosticar, y esta bien
/// que asi sea: para ellos la respuesta correcta es abstenerse. La diferencia
/// (b)-(c) mide exactamente cuanto aporta tener el mensaje original.
///
/// Fase 12, 20-sep-2026.
Class Lab.Fase12.HerrC Extends %AI.ToolSet
{

XData Definition [ MimeType = application/xml ]
{
<ToolSet Name="TriajeSinMensaje">
  <Description>Lectura de la traza y el log de una traza de integracion.</Description>
  <Tool Name="traza" Method="traza">
    <Description>Devuelve el recorrido del mensaje por la produccion, el mensaje canonico que produjo la transformacion, y el ACK que se devolvio al emisor. Pasa trazaId, el identificador de traza que te han dado en la pregunta.</Description>
  </Tool>
  <Tool Name="log" Method="log">
    <Description>Devuelve las entradas del Event Log de esa traza, cada una con su tipo (ERROR, WARNING, INFO) y su texto. Pasa trazaId.</Description>
  </Tool>
</ToolSet>
}

ClassMethod traza(trazaId As %String) As %String
{
	Return ##class(Lab.Fase12.Datos).Traza(trazaId)
}

ClassMethod log(trazaId As %String) As %String
{
	Return ##class(Lab.Fase12.Datos).Log(trazaId)
}

}
