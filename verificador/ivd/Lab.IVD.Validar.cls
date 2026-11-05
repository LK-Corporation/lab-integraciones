/// Etapa 32 (ANTES-ETAPA-IVDECLARADA.md): Lab.IV.Validar de la etapa 30 con la versión como dato, escrita aparte para que la de
/// la 30 no cambie. "resolver" toma la versión del pedido (si no la trae, 2.5, como la 30), y "segmentos" da los segmentos que
/// trae el esquema de una versión (Q-MV-4 en las versiones sin texto). Solo valida: el resto va en el conductor.
Class Lab.IVD.Validar Extends %RegisteredObject
{

/// Lee pEntrada (JSONL en UTF-8; cada línea {"k", "op", ...}) y escribe pSalida (JSONL en UTF-8), una línea por pedido.
/// op "validar": {"k", "texto", "doctype", "spec"} -> {"k", "importado", "segs", "ok", "error"}
/// op "resolver": {"k", "tipo", "version"} (p. ej. "ADT_A04", "2.6") -> {"k", "doctype", "error"}
/// op "segmentos": {"k", "version"} -> {"k", "segmentos": [...]}
ClassMethod Lote(pEntrada As %String, pSalida As %String) As %Status
{
	Set tIn = ##class(%Stream.FileCharacter).%New()
	Set tIn.TranslateTable = "UTF8"
	Set tSC = tIn.LinkToFile(pEntrada)
	Quit:$system.Status.IsError(tSC) tSC
	Set tOut = ##class(%Stream.FileCharacter).%New()
	Set tOut.TranslateTable = "UTF8"
	Set tSC = tOut.LinkToFile(pSalida)
	Quit:$system.Status.IsError(tSC) tSC
	While 'tIn.AtEnd {
		Set tLinea = tIn.ReadLine()
		Continue:tLinea=""
		Set tP = {}.%FromJSON(tLinea)
		Set tR = {"k": (tP.k)}
		If tP.op = "resolver" {
			Set tV = $select(tP.version'="":tP.version, 1:"2.5")
			Set tDT = ##class(EnsLib.HL7.Schema).ResolveSchemaTypeToDocType(tV, tP.tipo, .tSCr)
			Set tR.doctype = tDT
			Set tR.error = $select($system.Status.IsError($get(tSCr, 1)):$system.Status.GetErrorText(tSCr), 1:"")
		} ElseIf tP.op = "segmentos" {
			Set tL = [], tS = ""
			For {
				Set tS = $order(^EnsHL7.Schema(tP.version, "SS", tS))
				Quit:tS=""
				Do tL.%Push(tS)
			}
			Set tR.segmentos = tL
		} Else {
			Set tTmp = ##class(%Stream.TmpCharacter).%New()
			Do tTmp.Write(tP.texto)
			Do tTmp.Rewind()
			Set tM = ##class(EnsLib.HL7.Message).ImportFromLibraryStream(tTmp, .tSCi)
			If '$isobject(tM) {
				Set tR.importado = 0
				Set tR.error = "import: "_$system.Status.GetErrorText(tSCi)
			} Else {
				Set tR.importado = 1
				Set tR.segs = tM.SegCount
				Set tM.DocType = tP.doctype
				Set tS = tM.Validate(tP.spec)
				Set tR.ok = $system.Status.IsOK(tS)
				Set tR.error = $select($system.Status.IsOK(tS):"", 1:$system.Status.GetErrorText(tS))
			}
		}
		Do tOut.WriteLine(tR.%ToJSON())
	}
	Quit tOut.%Save()
}

}
