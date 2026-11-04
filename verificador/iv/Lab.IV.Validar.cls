/// Etapa 30 (iv/diseno-iv-fable.md §1.2): valida por lotes con el esquema de HL7 v2.5 de IRIS. Solo valida: la enumeración de
/// errores, el enmudecer y la clasificación van en iv/validar_iv.py. Importa siempre por stream (ImportFromString pierde
/// segmentos con texto no ASCII) y devuelve el recuento de segmentos para que el conductor lo compare.
Class Lab.IV.Validar Extends %RegisteredObject
{

/// Lee pEntrada (JSONL en UTF-8; cada línea {"k", "op", ...}) y escribe pSalida (JSONL en UTF-8), una línea por pedido.
/// op "validar": {"k", "texto", "doctype", "spec"} -> {"k", "importado", "segs", "ok", "error"}
/// op "resolver": {"k", "tipo"} (p. ej. "ADT_A04") -> {"k", "doctype", "error"}
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
			Set tDT = ##class(EnsLib.HL7.Schema).ResolveSchemaTypeToDocType("2.5", tP.tipo, .tSCr)
			Set tR.doctype = tDT
			Set tR.error = $select($system.Status.IsError($get(tSCr, 1)):$system.Status.GetErrorText(tSCr), 1:"")
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
