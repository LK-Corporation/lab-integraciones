Include %occInclude

/// Fase 12 — el arnes del agente de triaje. La parte que toca los datos.
///
/// TRES HERRAMIENTAS DE SOLO LECTURA, ACOTADAS POR TRAZA. Lab.Fase12.HerrA,
/// HerrB y HerrC son envoltorios finos sobre esto: los brazos del experimento
/// se construyen QUITANDO HERRAMIENTAS, no cambiando el prompt, asi que la
/// logica tiene que vivir en un solo sitio o los brazos dejarian de ser
/// comparables entre si.
///
/// EL ACOTADO SE IMPONE AQUI, NO SE PIDE POR FAVOR. Si el agente pudiera
/// consultar la traza de otro caso, los tres brazos se derrumbarian: con ver
/// una sesion vecina ya sabria si la suya es rara. Cada llamada resuelve el
/// identificador contra la lista blanca de la tanda y, si no esta, devuelve un
/// aviso sin tocar un solo dato.
///
/// SE CUENTAN LAS LLAMADAS, por traza y por herramienta. Eso convierte "que
/// miro antes de contestar" en una variable MEDIDA: cero llamadas en el brazo
/// que tiene las tres herramientas significa que contesto de memoria, y eso
/// hay que poder verlo en los resultados.
///
/// TODO VA POR TANDA (^Lab.Fase12.Permiso(tanda, traza)) y NADA SE BORRA. Una
/// tanda nueva usa una clave nueva, asi que los permisos viejos quedan
/// inertes en vez de haber que matarlos. Ademas de evitar el borrado, deja los
/// contadores de tandas anteriores disponibles para el informe.
///
/// El identificador que ve el agente es OPACO (T + hex). No es el SessionId ni
/// el MSH-10: el MSH-10 lo repiten dos operadores a proposito, y el SessionId
/// es correlativo, lo que filtraria el orden de envio.
///
/// PASO 4 (20-sep): EL IDENTIFICADOR OPACO NO BASTABA. El orden de envio se
/// colaba igual por dos sitios que nadie habia mirado: las marcas de tiempo
/// ABSOLUTAS del Event Log y el id del recurso FHIR que aparece en su texto
/// ("id=2704"), que es un contador. Los operadores de ENTORNO se enviaron
/// juntos al final —habia que romper el entorno para provocarlos—, asi que
/// "envio tarde => ENTORNO" era una regla ganadora sin mirar el mensaje.
/// MEDIDO con aprendiz.py: un arbol de decision de tres niveles sobre esos
/// DOS NUMEROS saca macro 0,597 en la particion de evaluacion, contra un
/// suelo de 0,200 y un regex completo de 0,714. Desde este paso, los tiempos
/// son RELATIVOS al primer apunte de la sesion y los contadores van ocultos.
/// Las DURACIONES se conservan, que es lo que si es evidencia: los 67 s entre
/// creacion y proceso del servicio bloqueado se siguen viendo.
///
/// Fase 12, 20-sep-2026.
Class Lab.Fase12.Datos Extends %RegisteredObject
{

/// Tope de caracteres de cualquier herramienta. Un mensaje de este
/// laboratorio cabe de sobra; el tope esta para que un caso patologico no
/// inunde el contexto del modelo ni desnivele los brazos.
Parameter MAXSALIDA = 8000;

/// Declara cual es la tanda en curso. Todo lo demas cuelga de aqui.
ClassMethod AbrirTanda(pTanda As %String) As %Status
{
	Return:pTanda="" $$$ERROR($$$GeneralError, "identificador de tanda vacio")
	Set ^Lab.Fase12.Tanda = pTanda
	Return $$$OK
}

ClassMethod TandaActual() As %String
{
	Return $get(^Lab.Fase12.Tanda, "")
}

/// Mete una traza en la lista blanca de la tanda en curso.
ClassMethod Permitir(pTraza As %String, pSesion As %Integer) As %Status
{
	Set tTanda = ..TandaActual()
	Return:tTanda="" $$$ERROR($$$GeneralError, "no hay tanda abierta")
	Return:pTraza="" $$$ERROR($$$GeneralError, "identificador de traza vacio")
	Set ^Lab.Fase12.Permiso(tTanda, pTraza) = pSesion
	Return $$$OK
}

/// La sesion que corresponde a una traza, o vacio si no esta permitida.
ClassMethod Sesion(pTraza As %String) As %String
{
	Set tTanda = ..TandaActual()
	Return:tTanda="" ""
	Return $get(^Lab.Fase12.Permiso(tTanda, pTraza), "")
}

/// Cuantas llamadas ha recibido esa traza en la tanda en curso.
ClassMethod Llamadas(pTraza As %String) As %Integer
{
	Set tTanda = ..TandaActual()
	Return:tTanda="" 0
	Return $get(^Lab.Fase12.Llamadas(tTanda, pTraza), 0)
}

/// Cuantas veces se ha llamado a UNA herramienta concreta de esa traza.
/// La usa HerrB para imponer el orden de lectura (paso 4).
ClassMethod LlamadasDe(pTraza As %String, pHerramienta As %String) As %Integer
{
	Set tTanda = ..TandaActual()
	Return:tTanda="" 0
	Return $get(^Lab.Fase12.Llamadas(tTanda, pTraza, pHerramienta), 0)
}

/// Desglose "mensaje=2,traza=1,log=0" para el informe.
ClassMethod Desglose(pTraza As %String) As %String
{
	Set tTanda = ..TandaActual()
	Return:tTanda="" ""
	Set tSalida = "", tH = ""
	For {
		Set tH = $order(^Lab.Fase12.Llamadas(tTanda, pTraza, tH))
		Quit:tH=""
		Set tSalida = tSalida _ $select(tSalida="":"", 1:",") _ tH _ "=" _ ^Lab.Fase12.Llamadas(tTanda, pTraza, tH)
	}
	Return tSalida
}

/// Cuenta la llamada y comprueba el permiso, en un solo sitio. Devuelve la
/// sesion, o cadena vacia si la traza no esta permitida.
ClassMethod Autorizar(pTraza As %String, pHerramienta As %String) As %String
{
	Set tTanda = ..TandaActual()
	Return:tTanda="" ""
	Set ^Lab.Fase12.Llamadas(tTanda, pTraza) = $get(^Lab.Fase12.Llamadas(tTanda, pTraza), 0) + 1
	Set ^Lab.Fase12.Llamadas(tTanda, pTraza, pHerramienta) = $get(^Lab.Fase12.Llamadas(tTanda, pTraza, pHerramienta), 0) + 1
	Return ..Sesion(pTraza)
}

ClassMethod Denegado(pTraza As %String) As %String
{
	Return "No hay ninguna traza con el identificador '" _ pTraza _ "'. Solo puedes consultar la traza que te han dado en la pregunta."
}

ClassMethod Recortar(pTexto As %String) As %String
{
	Return:$length(pTexto)'>..#MAXSALIDA pTexto
	Return $extract(pTexto, 1, ..#MAXSALIDA) _ $char(10) _ "[...recortado...]"
}

/// Segundos absolutos de un %TimeStamp, para poder restarlos. Se parte a
/// mano en vez de con $ZDATETIMEH con firma posicional larga: aqui solo
/// interesan DIFERENCIAS dentro de una sesion, y una conversion que explote
/// por un formato inesperado no debe tumbar la herramienta entera.
ClassMethod Segundos(pMarca As %String) As %Numeric
{
	Return:pMarca="" 0
	Set tDias = 0
	Try {
		Set tDias = $zdateh($piece(pMarca, " ", 1), 3)
	} Catch {
		Set tDias = 0
	}
	Set tHora = $piece(pMarca, " ", 2)
	Set tSeg = ($piece(tHora, ":", 1) * 3600) + ($piece(tHora, ":", 2) * 60) + $piece(tHora, ":", 3)
	Return (tDias * 86400) + tSeg
}

/// Oculta los contadores que delatan el orden de envio: "id=2704" pasa a
/// "id=<oculto>". El id del recurso FHIR es monotono, asi que decia por si
/// solo si el caso se envio pronto o tarde.
ClassMethod OcultarContadores(pTexto As %String) As %String
{
	Return:pTexto'["id=" pTexto
	Set tSalida = $piece(pTexto, "id=", 1)
	For tI = 2:1:$length(pTexto, "id=") {
		Set tTrozo = $piece(pTexto, "id=", tI)
		Set tNum = ""
		For tJ = 1:1:$length(tTrozo) {
			Quit:$extract(tTrozo, tJ)'?1N
			Set tNum = tNum _ $extract(tTrozo, tJ)
		}
		Set tSalida = tSalida _ "id=" _ $select(tNum="":"", 1:"<oculto>") _ $extract(tTrozo, $length(tNum) + 1, *)
	}
	Return tSalida
}

/// Sustituye MSH-7 por un marcador en las lineas MSH de un mensaje. La hora
/// del ACK la pone el motor al procesarlo, asi que es un reloj absoluto mas.
ClassMethod OcultarMsh7(pTexto As %String) As %String
{
	Set tSalida = ""
	For tI = 1:1:$length(pTexto, $char(10)) {
		Set tLinea = $piece(pTexto, $char(10), tI)
		If $extract(tLinea, 1, 4) = "MSH|" {
			Set $piece(tLinea, "|", 7) = "<hora oculta>"
		}
		Set tSalida = tSalida _ $select(tI=1:"", 1:$char(10)) _ tLinea
	}
	Return tSalida
}

/// El mensaje HL7 tal como llego por el cable, un segmento por linea.
ClassMethod Mensaje(pTraza As %String) As %String
{
	Set tSesion = ..Autorizar(pTraza, "mensaje")
	Return:tSesion="" ..Denegado(pTraza)

	Set tId = ..CuerpoDe(tSesion, "EnsLib.HL7.Message", "AdtTcpIn", "")
	Return:tId="" "No se conserva el mensaje de entrada de esa traza."

	Set tMsg = ##class(EnsLib.HL7.Message).%OpenId(tId)
	If '$IsObject(tMsg) { Return "No se pudo abrir el mensaje de entrada." }
	Return ..Recortar($replace(tMsg.OutputToString(), $char(13), $char(10)))
}

/// El recorrido de la sesion, el canonico que produjo la transformacion y el
/// ACK que se devolvio al emisor.
ClassMethod Traza(pTraza As %String) As %String
{
	Set tSesion = ..Autorizar(pTraza, "traza")
	Return:tSesion="" ..Denegado(pTraza)

	Set tSalida = "RECORRIDO DEL MENSAJE" _ $char(10)
	Set tRs = ##class(%SQL.Statement).%ExecDirect(, "SELECT SourceConfigName, TargetConfigName, MessageBodyClassName, Status, IsError FROM Ens.MessageHeader WHERE SessionId = ? ORDER BY ID", tSesion)
	Set tHay = 0
	While tRs.%Next() {
		Set tHay = tHay + 1
		Set tSalida = tSalida _ "  " _ tRs.%Get("SourceConfigName") _ " -> " _ tRs.%Get("TargetConfigName") _ "   [" _ tRs.%Get("MessageBodyClassName") _ "]  estado=" _ tRs.%Get("Status") _ $select(tRs.%Get("IsError"):"  ERROR", 1:"") _ $char(10)
	}
	If 'tHay { Return "Esa traza no tiene ningun mensaje registrado: el mensaje pudo no llegar a entrar." }

	Set tSalida = tSalida _ $char(10) _ "MENSAJE CANONICO PRODUCIDO POR LA TRANSFORMACION" _ $char(10)
	Set tCan = ##class(%SQL.Statement).%ExecDirect(, "SELECT TOP 1 p.Identifier, p.FamilyName, p.GivenName, p.Gender, p.BirthDate, p.MsgControlId, p.MsgEvent, p.Truncado FROM Lab_HL7_Msg.PatientRequest p JOIN Ens.MessageHeader h ON h.MessageBodyId = p.ID WHERE h.SessionId = ? AND h.MessageBodyClassName = 'Lab.HL7.Msg.PatientRequest' ORDER BY p.ID DESC", tSesion)
	If tCan.%Next() {
		Set tSalida = tSalida _ "  Identifier   : " _ tCan.%Get("Identifier") _ $char(10)
		Set tSalida = tSalida _ "  FamilyName   : " _ tCan.%Get("FamilyName") _ $char(10)
		Set tSalida = tSalida _ "  GivenName    : " _ tCan.%Get("GivenName") _ $char(10)
		Set tSalida = tSalida _ "  Gender       : " _ tCan.%Get("Gender") _ $char(10)
		Set tSalida = tSalida _ "  BirthDate    : " _ tCan.%Get("BirthDate") _ $char(10)
		Set tSalida = tSalida _ "  MsgControlId : " _ tCan.%Get("MsgControlId") _ $char(10)
		Set tSalida = tSalida _ "  MsgEvent     : " _ tCan.%Get("MsgEvent") _ $char(10)
		Set tSalida = tSalida _ "  Truncado     : " _ tCan.%Get("Truncado") _ $char(10)
	} Else {
		Set tSalida = tSalida _ "  (no se produjo mensaje canonico)" _ $char(10)
	}

	Set tSalida = tSalida _ $char(10) _ "ACK DEVUELTO AL EMISOR" _ $char(10)
	Set tAck = ..CuerpoDe(tSesion, "EnsLib.HL7.Message", "", "AdtTcpIn")
	If tAck = "" {
		Set tSalida = tSalida _ "  (no se devolvio ningun ACK de aplicacion)" _ $char(10)
	} Else {
		Set tMsg = ##class(EnsLib.HL7.Message).%OpenId(tAck)
		If '$IsObject(tMsg) {
			Set tSalida = tSalida _ "  (no se pudo abrir el ACK)" _ $char(10)
		} Else {
			Set tSalida = tSalida _ ..OcultarMsh7($replace(tMsg.OutputToString(), $char(13), $char(10))) _ $char(10)
		}
	}
	Return ..Recortar(..OcultarContadores(tSalida))
}

/// Las filas del Event Log de esa sesion, con el tiempo RELATIVO al primer
/// apunte. Ver la nota del paso 4 en la cabecera de la clase.
ClassMethod Log(pTraza As %String) As %String
{
	Set tSesion = ..Autorizar(pTraza, "log")
	Return:tSesion="" ..Denegado(pTraza)

	Set tSalida = "", tCero = ""
	Set tRs = ##class(%SQL.Statement).%ExecDirect(, "SELECT TimeLogged, Type, ConfigName, Text FROM Ens_Util.Log WHERE SessionId = ? ORDER BY ID", tSesion)
	While tRs.%Next() {
		Set tTipo = $case(tRs.%Get("Type"), 1:"ASSERT", 2:"ERROR", 3:"WARNING", 4:"INFO", 5:"TRACE", 6:"ALERT", :"TIPO?")
		Set tAhora = ..Segundos(tRs.%Get("TimeLogged"))
		Set:tCero="" tCero = tAhora
		Set tRel = "T+" _ $fnumber(tAhora - tCero, "", 3) _ "s"
		Set tSalida = tSalida _ $justify(tRel, 12) _ "  " _ $justify(tTipo, 8) _ "  " _ tRs.%Get("ConfigName") _ ": " _ tRs.%Get("Text") _ $char(10)
	}
	Return:tSalida="" "El Event Log no tiene ninguna entrada para esa traza."
	Return ..Recortar(..OcultarContadores(tSalida))
}

/// Id del cuerpo del primer header de la sesion que case con la clase y, si se
/// dan, con el origen o el destino. Cadena vacia si no hay ninguno.
ClassMethod CuerpoDe(pSesion As %Integer, pClase As %String, pOrigen As %String = "", pDestino As %String = "") As %String
{
	Set tSql = "SELECT TOP 1 MessageBodyId FROM Ens.MessageHeader WHERE SessionId = ? AND MessageBodyClassName = ?"
	If pOrigen '= "" { Set tSql = tSql _ " AND SourceConfigName = ?" }
	If pDestino '= "" { Set tSql = tSql _ " AND TargetConfigName = ?" }
	Set tSql = tSql _ " ORDER BY ID"
	If pOrigen '= "" {
		Set tRs = ##class(%SQL.Statement).%ExecDirect(, tSql, pSesion, pClase, pOrigen)
	} ElseIf pDestino '= "" {
		Set tRs = ##class(%SQL.Statement).%ExecDirect(, tSql, pSesion, pClase, pDestino)
	} Else {
		Set tRs = ##class(%SQL.Statement).%ExecDirect(, tSql, pSesion, pClase)
	}
	If tRs.%Next() { Return tRs.%Get("MessageBodyId") }
	Return ""
}

}
