#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lectura de la evidencia (log, entorno, conexión) con el vocabulario real: implementación de la Parte 1 de
`diseno-verificador-fable.md` (Fable, segunda entrega, a ciegas). Patrones exactos sobre el texto
normalizado; lo desconocido pregunta, no decide. Determinista.

Desviaciones declaradas:
  DV-L1: una fila F1/F2 sin MSH-10 se atribuye a la sesión; si el caso tiene un solo mensaje, cuenta
         como suya (el diseño no dice a quién se atribuye una fila no reconocida).
  DV-L2: E06 sin «desde» (credencial vacía desde el principio) decide solo si no hay fila terminal,
         igual que E07-E09 (§1.6 paso 2).
  DV-L3: [S42] (diseno-s42-s43-fable.md) una fila F3 sin MSH-10 se atribuye a todo mensaje sin fila terminal, con uno
         o con varios mensajes; S42 vale para toda F3 (Info, Warning o sin tipo), no solo Info, y también con L08 o
         con un entorno decisivo (no son filas terminales).
Multi-tipo [S50] (diseno-multitipo-fable.md §5): un punto de entrada sin destino escribe L13 «Mensaje aceptado sin
destino (MSH-10=…): punto <pe>» (terminal, destino éxito sin escritura: no hay almacén, L-MT1) y L14 «Mensaje rechazado
por el punto <pe> (MSH-10=…): …» (terminal, no_intentado, opinión del circuito como L03). Ningún texto de los bundles
congelados casa con L13/L14 (empiezan distinto).

Uso: python3 lectura_evidencia.py --autoprueba (las pruebas de la lectura van en verificador.py, junto
con las del acuse, porque sus esperados son acuses).
"""
import re
import unicodedata


def norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn").strip()


# ---------------------------------------------------------------------------- log §1.3
L = [
    ("L01", "exito_creado", r"^patient creado en fhir: id=\S+ desde msh-10=(?P<id>\S+) \(http 201\)$"),
    ("L02", "exito_existente", r"^patient ya existia \(creacion condicional\) en fhir: id=\S+ desde msh-10=(?P<id>\S+) \(http 200\)$"),
    ("L03", "opinion_rechazo_previo", r"^mensaje rechazado antes de fhir \(msh-10=(?P<id>[^)]*)\): (?P<motivo>.+)$"),
    ("L04", "opinion_tipo_no_soportado", r"^mensaje rechazado a proposito \(msh-10=(?P<id>[^)]*)\): tipo de mensaje no soportado: (?P<tipo>.+?) \(doctype (?P<doctype>[^)]*)\)"),
    ("L05", "rechazo_fhir", r"^fhir rechazo el recurso \(msh-10=(?P<id>[^)]*)\): fhir devolvio (?P<http>[1-5]\d\d):?(?P<cuerpo>.*)$"),
    ("L06", "fallo_servidor_fhir", r"^fhir fallo del lado servidor \(msh-10=(?P<id>[^)]*)\): fhir devolvio (?P<http>[1-5]\d\d):?(?P<cuerpo>.*)$"),
    ("L07", "fhir_inalcanzable_socket", r"^no se pudo hablar con fhir \(msh-10=(?P<id>[^)]*)\): (?P<detalle>.*)$"),
    ("L08", "timeout_interno", r"errfailuretimeout: failuretimeout of (?P<seg>\d+) seconds exceeded in (?P<comp>\S+)"),
    ("L09", "acuse_fabricado_por_servicio", r"^constructing ack with code (?P<codigo>[a-z]{2}) because "),
    ("L10", "conexion_perdida_al_responder", r"^error <ens>erroutconnectionlost: lost hl7 write connection to "),
    ("L11", "resto_descartado", r"^discarding leftover input '(?P<resto>.*?)'?$"),
    ("L12", "irrelevante", r"^disconnecting from \d+<-[\d.]+:\d+$"),
    ("L13", "exito_sin_destino", r"^mensaje aceptado sin destino \(msh-10=(?P<id>[^)]*)\): punto (?P<pe>\S+)$"),           # [S50]
    ("L14", "opinion_rechazo_pe", r"^mensaje rechazado por el punto (?P<pe>\S+) \(msh-10=(?P<id>[^)]*)\): (?P<motivo>.+)$"),  # [S50]
    # diseno-oru-fable.md §4.5/§5.3: la operación FhirResultados (LABORU) escribe L15 al terminar la transacción FHIR
    ("L15", "exito_oru_transaccion", r"^resultados escritos en fhir \(msh-10=(?P<id>[^)]*)\): creados=(?P<c>\d+) existentes=(?P<e>\d+) \(http (?P<http>2\d\d)\)$"),
    # diseno-adt-fable.md §4.4: la operación FhirAdt (LABADT) escribe L16 al terminar la transacción FHIR
    ("L16", "exito_adt_transaccion", r"^paciente y visita escritos en fhir \(msh-10=(?P<id>[^)]*)\): patient=(?P<p>\w+) encounter=(?P<e>\w+) \(http (?P<http>2\d\d)\)$"),
]
TERMINALES = {"L01", "L02", "L03", "L04", "L05", "L06", "L07", "L13", "L14", "L15", "L16"}


def _submotivo(m, pe=None):
    """Hecho que el circuito dice haber rechazado (L03). DV-ORU-3: con el punto oru_fhir, tras los tres patrones de siempre, el
    genérico SEG-n de _submotivo_pe («OBX 2: OBX-11 … vacio» -> OBX-11); con los demás puntos, como hoy (regresión intacta)."""
    if re.search(r"falta el identificador del paciente \(pid-3", m):
        return "PID-3"
    if re.search(r"falta el nombre del paciente \(pid-5\)", m):
        return "PID-5"
    if re.search(r"excede la longitud maxima", m):
        return "longitud"
    if pe in ("oru_fhir", "adt_fhir"):                                # DV-ADT-5
        mo = re.search(r"\b([a-z][a-z0-9]{2})-(\d+)", m)
        if mo:
            return "%s-%s" % (mo.group(1).upper(), mo.group(2))
    return "otro"


def _submotivo_pe(m):
    """Hecho que el punto de entrada dice haber rechazado (L14): el campo SEG-n que nombre, «estructura» si habla de
    segmentos/estructura, o «otro». Es la opinión del circuito: no decide."""
    mo = re.search(r"\b([a-z][a-z0-9]{2})-(\d+)", m)
    if mo:
        return "%s-%s" % (mo.group(1).upper(), mo.group(2))
    if re.search(r"estructura|segment|docType|doctype|validate|orden|ausente|falta", m):
        return "estructura"
    return "otro"


def clasificar_fila(fila, pe=None):
    """-> dict {id, clase, msh10|None, datos, texto, tipo}. pe: nombre del punto de entrada (solo cambia el hecho de L03 en oru_fhir)."""
    # un motivo de varias líneas (IRIS une varios errores de Validate con CRLF) es la misma fila: los saltos cuentan como
    # espacio para casar el patrón (O4 de la rebanada ORU: sin esto un L03 conocido quedaba como vocabulario nuevo)
    t, tipo = re.sub(r"\s*[\r\n]+\s*", " ", norm(fila.get("texto"))), (fila.get("tipo") or "")
    for i, clase, pat in L:
        m = re.search(pat, t) if i == "L08" else re.match(pat, t)
        if not m:
            continue
        d = {k: v for k, v in m.groupdict().items() if v is not None}
        out = {"id": i, "clase": clase, "msh10": None, "datos": d, "texto": fila.get("texto"), "tipo": tipo}
        if "id" in d:
            # el MSH-10 capturado viene normalizado (minúsculas): se recupera del texto original
            mo = re.search(r"MSH-10=([^)\s]*)", fila.get("texto") or "", re.I)
            out["msh10"] = mo.group(1) if mo else d["id"]
        if i == "L03":
            d["hecho"] = _submotivo(d.get("motivo", ""), pe)
        if i == "L15":
            d["c"], d["e"], d["http"] = int(d["c"]), int(d["e"]), int(d["http"])
        if i == "L16":
            d["http"] = int(d["http"])
        if i == "L14":
            d["hecho"] = _submotivo_pe(d.get("motivo", ""))
        if i in ("L05", "L06"):
            d["http"] = int(d["http"])
            c = re.search(r'"code":\s*"(?P<code>[a-z-]+)"', d.get("cuerpo", ""))
            g = re.search(r'"diagnostics":\s*"(?P<diag>[^"]*)', d.get("cuerpo", ""))
            d["code"] = c.group("code") if c else None
            d["diag"] = g.group("diag") if g else None
        if i == "L11":                                   # [S15] el segundo mensaje del marco también espera acuse [A-3]
            resto = fila.get("texto") or ""
            k = resto.find("'")
            resto = resto[k + 1:].rstrip("'") if k >= 0 else resto
            if resto.startswith("MSH") and len(resto) > 4:
                partes = resto.split(resto[3])
                out["msh10"] = partes[9] if len(partes) > 9 else None
            out["datos"]["resto"] = resto
        return out
    m = re.search(r"\b(?:http\s*/?\s*|devolvio\s+)(?P<http>[1-5]\d\d)\b", t)
    mo = re.search(r"MSH-10=([^)\s]*)", fila.get("texto") or "", re.I)
    if m:
        return {"id": "F1", "clase": "http_no_reconocido", "msh10": mo.group(1) if mo else None,
                "datos": {"http": int(m.group("http"))}, "texto": fila.get("texto"), "tipo": tipo}
    if tipo.lower() in ("error", "alert"):
        return {"id": "F2", "clase": "sistema_no_reconocido", "msh10": mo.group(1) if mo else None,
                "datos": {}, "texto": fila.get("texto"), "tipo": tipo}
    return {"id": "F3", "clase": "desconocido", "msh10": mo.group(1) if mo else None, "datos": {},
            "texto": fila.get("texto"), "tipo": tipo}


# ---------------------------------------------------------------------------- entorno §1.4
# Los textos con ' son los del arnés desde el 30-sep (diseno-entorno-exacto-fable.md): describen el plan con su ventana.
# E01, E02 y E03 sin ' son los antiguos, que siguen en los bundles congelados: E02 era inexacto (callaba la ventana
# por_peticion) y se lee como legado que no decide [A-18][S41].
E = [
    ("E01'", "fhir_retraso", r"^las peticiones post del circuito a fhir \(reintentos incluidos\) se retrasaron (?P<seg>\d+) s antes de llegar a fhir, cada una con probabilidad (?P<p>[\d.]+); fhir las atendio con normalidad$"),
    ("E01", "fhir_retraso", r"^las peticiones del circuito a fhir se retrasaron (?P<seg>\d+) s, cada una con probabilidad (?P<p>[\d.]+)$"),
    ("E02'", "fhir_error_inyectado", r"^fhir contesto con error (?P<http>5\d\d), con probabilidad (?P<p>[\d.]+), solo a (?:la primera peticion|las (?P<n>\d+) primeras peticiones) post del circuito en el lote \(reintentos incluidos\); a las demas las atendio con normalidad$"),
    ("E02", "fhir_error_inyectado", r"^fhir contesto a las peticiones del circuito con error (?P<http>5\d\d), cada una con probabilidad (?P<p>[\d.]+)$"),
    ("E03'", "receptor_reiniciado", r"^el circuito entero \(la produccion\) se paro(?: tras el mensaje (?P<desde>\d+))? y se volvio a arrancar(?: (?P<seg>\d+) s despues)?, durante el lote$"),
    ("E03", "receptor_reiniciado", r"^el servicio se paro y se volvio a arrancar durante el lote"),
    ("E04", "tabla_sexo_alterada", r"^una fila de la tabla de consulta del sexo cambio: (?P<de>\S+) -> ['«\"](?P<a>[^'»\"]*)['»\"]$"),
    ("E04b", "tabla_sexo_borrada", r"^la fila (?P<de>\S+) de la tabla de consulta del sexo se borro"),
    ("E05", "tabla_sexo_alterada", r"^en la tabla de consulta del sexo, las filas (?P<filas>.+?) daban ['«\"](?P<a>[^'»\"]*)['»\"]$"),
    ("E06", "credencial_invalida", r"^la credencial con la que el circuito llama a fhir (?:estaba vacia|paso a ser (?P<auth>vacia|erronea|la de un usuario que no existe) tras el mensaje (?P<desde>\d+))$"),
    ("E07", "fhir_inalcanzable", r"^el puerto de fhir al que llama el circuito estaba cerrado"),
    ("E08", "fhir_ruta_inexistente", r"^la ruta de fhir a la que llama el circuito no existia$"),
    ("E09", "destino_deshabilitado", r"^el componente que escribe en fhir estaba deshabilitado$"),
]


def clasificar_entorno(z):
    t = norm(z if isinstance(z, str) else str(z))
    for i, clase, pat in E:
        m = re.match(pat, t)
        if m:
            d = {k: v for k, v in m.groupdict().items() if v is not None}
            if i == "E02'":
                d.setdefault("n", "1")
            if i == "E02":
                d["legado"] = True
            # [A-18] decide solo lo que afecta a toda la sesión sin ventana. El 5xx inyectado lleva siempre ventana de
            # peticiones y no decide, ni con p = 1.0; su texto antiguo tampoco (callaba la ventana).
            decide = i in ("E07", "E08", "E09") or (i == "E06" and "desde" not in d)
            return {"id": i, "clase": clase, "datos": d, "decide": decide, "texto": z}
    return {"id": "EF", "clase": "entorno_desconocido", "datos": {}, "decide": False, "texto": z}


# ---------------------------------------------------------------------------- conexión §1.5
X = [
    ("X01", "establecida", r"^conexion establecida$"),
    ("X02", "ack_recibido", r"^ack recibido a los (?P<t>[\d.]+) s del envio$"),
    ("X03", "no_establecida_rechazada", r"^la conexion no se establecio: connectionrefusederror"),
    ("X04", "no_establecida_reiniciada", r"^la conexion no se establecio: connectionreseterror"),
    ("X05", "reiniciada_tras_establecer", r"^error en el emisor: connectionreseterror"),
    ("X06", "sin_ack_por_tiempo", r"^no llego ack \((?:el emisor dejo de esperar a los|sin respuesta; el emisor espero) (?P<t>[\d.]+) s\)$"),
]


def clasificar_conexion(z):
    t = norm(z)
    for i, clase, pat in X:
        m = re.match(pat, t)
        if m:
            return {"id": i, "clase": clase, "datos": {k: v for k, v in m.groupdict().items() if v}, "texto": z}
    return {"id": "XF", "clase": "conexion_desconocida", "datos": {}, "texto": z}


def explica_gender(lec, pid8, observado):
    """[S20] -> la alteración declarada de la tabla del sexo que explica este Gender guardado, o None:
    misma fila de PID-8 (en mayúsculas, S4) y mismo valor guardado. [S41] Una fila borrada (a = None) explica
    cualquier valor guardado para esa fila: el circuito se quedó sin traducción."""
    for z in lec.get("tabla_sexo") or []:
        if (pid8 or "").upper() in z["de"] and (z["a"] is None or norm(observado if isinstance(observado, str) else "") == z["a"]):
            return z
    return None


# ---------------------------------------------------------------------------- composición §1.6
def leer(e, msh10s, pe=None):
    """-> lectura del caso. msh10s: los MSH-10 de los mensajes del cable, en orden. pe: nombre del punto de entrada (por omisión
    el del bundle); solo oru_fhir cambia algo (DV-ORU-3)."""
    pe = pe or e.get("punto_entrada")
    filas = [clasificar_fila(f, pe) for s in e.get("sesiones") or [] for f in s.get("log") or []]
    ent = [clasificar_entorno(z) for z in e.get("entorno") or []]
    con = [clasificar_conexion(z) for z in e.get("conexion") or []]
    ids_con = {c["id"] for c in con}
    hay_sesion = bool([s for s in e.get("sesiones") or [] if s.get("log") or s.get("canonico")])
    lec = {"filas": filas, "entorno": ent, "conexion": con, "vocabulario_nuevo": [], "notas": [],
           "contradictorio": [], "arnes_inexacto": [], "lectura_hallazgos": [], "por_mensaje": {}, "tabla_sexo": []}
    for f in filas:
        if f["id"] in ("F2", "F3"):
            lec["vocabulario_nuevo"].append("log: " + (f["texto"] or ""))
        if f["id"] == "F2":
            lec["lectura_hallazgos"].append("fila no reconocida con tipo %s: %r" % (f["tipo"], f["texto"]))
    for z in ent:
        if z["id"] == "EF":
            lec["vocabulario_nuevo"].append("entorno: " + str(z["texto"]))
        elif z["id"] == "E04":                                           # [S20] qué fila y a qué valor
            lec["tabla_sexo"].append({"id": "E04", "de": {z["datos"]["de"].upper()}, "a": z["datos"]["a"], "texto": z["texto"]})
        elif z["id"] == "E04b":                                          # [S41] fila borrada: cualquier valor
            lec["tabla_sexo"].append({"id": "E04b", "de": {z["datos"]["de"].upper()}, "a": None, "texto": z["texto"]})
        elif z["id"] == "E02":                                           # [A-18] texto antiguo, sin ventana
            lec["arnes_inexacto"].append("descripción antigua del entorno sin la ventana de peticiones (bundle anterior "
                                         "al 30-sep-2026): no decide [A-18]")
        elif z["id"] == "E05":
            de = {f.upper() for f in re.split(r"[,\s]+|\by\b", z["datos"]["filas"]) if f.strip() and f != "y"}
            lec["tabla_sexo"].append({"id": "E05", "de": de, "a": z["datos"]["a"], "texto": z["texto"]})
    for z in con:
        if z["id"] == "XF":
            lec["vocabulario_nuevo"].append("conexion: " + str(z["texto"]))
    # P0.a: X03/X04; X05 sin sesión
    lec["p0"] = bool(ids_con & {"X03", "X04"}) or ("X05" in ids_con and not hay_sesion)
    if "X05" in ids_con and not hay_sesion:
        lec["notas"].append("X05 sin sesión: tratado como no recibido (P0.a') [A-17]")
    unico = len(msh10s) == 1
    decisivos = [z for z in ent if z["decide"]]
    for k, m10 in enumerate(msh10s):
        propias = [f for f in filas if f["msh10"] == m10 or (unico and f["msh10"] is None and f["id"] in ("F1", "F2"))]
        term = [f for f in propias if f["id"] in TERMINALES or f["id"] == "F1"]
        r = {"msh10": m10, "terminal": None, "intentos_previos": [], "opinion": None, "destino": "sin_evidencia",
             "http": None, "code": None, "ambigua": [], "notas": [], "causas_d0": [], "fabricado": None}
        if term:
            ult = term[-1]                                               # [A-16] gana la última
            r["terminal"] = ult
            r["intentos_previos"] = [f["id"] + ":" + str(f["datos"].get("http", "")) for f in term[:-1]]
            i = ult["id"]
            if i == "L01":
                r["destino"] = "exito"
            elif i == "L02":
                r["destino"] = "exito"
                r["notas"].append("L5': el recurso ya existía; no se escribió nada (almacén no observable)")
            elif i == "L13":                                             # [S50] punto de entrada sin destino: aceptado
                r["destino"] = "exito"
                r["notas"].append("L5'': aceptado por el punto %s; no hay destino ni almacén que observar (L-MT1)" % ult["datos"].get("pe"))
            elif i == "L15":                                             # ORU: transacción FHIR escrita (§4.5); con creados=0, L5'
                r["destino"] = "exito"
                if ult["datos"].get("c") == 0:
                    r["notas"].append("L5': los recursos ya existían (ifNoneExist); no se escribió nada (almacén no observable)")
            elif i == "L16":                                             # ADT: transacción FHIR escrita (§4.4); almacén leído
                r["destino"] = "exito"
            elif i in ("L03", "L04", "L14"):
                r["destino"] = "no_intentado"
                r["opinion"] = ult
            elif i in ("L05", "L06", "F1"):
                r["destino"] = "http"
                r["http"], r["code"] = ult["datos"]["http"], ult["datos"].get("code")
                if i == "F1":
                    r["ambigua"].append("texto no reconocido (F1)")
            elif i == "L07":
                r["destino"] = "sistema"
        else:
            sesion = [f for f in filas if f["msh10"] is None]
            if any(f["id"] == "L08" for f in sesion):
                r["destino"] = "sistema"
                r["notas"].append("L15: la petición pudo completarse en FHIR tras el timeout (no observable)")
            elif decisivos:
                r["destino"] = "sistema"
            elif any(f["id"] == "F2" for f in propias):
                r["destino"] = "sistema"
                r["ambigua"].append("fila Error/Alert no reconocida (F2)")
            elif any(z["id"] == "EF" for z in ent):
                r["destino"] = "sin_evidencia"
                lec["lectura_hallazgos"].append("entorno no reconocido y sin fila terminal")
            else:
                r["notas"].append("L5: sin evidencia de que el destino fuera alcanzado")
            # [S42] una fila desconocida (F3) sin ninguna fila terminal pregunta: pudo ser la terminal que falta. [DV-L3] la
            # F3 sin MSH-10 se atribuye a todo mensaje sin terminal, con uno o con varios mensajes.
            for f in [f for f in propias if f["id"] == "F3"] + [f for f in filas if f["id"] == "F3" and f["msh10"] is None]:
                lec["lectura_hallazgos"].append("fila de log no reconocida (tipo %s) sin ninguna fila terminal del destino "
                                                "para MSH-10=%s: %r [S42]" % (f["tipo"] or "sin tipo", m10, f["texto"]))
        if any(z["id"] in ("E02'", "E02") for z in ent) and (r["destino"] == "sin_evidencia" or r["intentos_previos"]):
            r["notas"].append("L21: el entorno describe el plan (una ventana de peticiones POST, reintentos incluidos); "
                              "qué petición de este mensaje cayó en ella no está en la evidencia [L21]")
        # coherencia §1.6.3. [S12] una fila E es la descripción del arnés; si el log la contradice, decide el log
        # (nota, no contradicción). Dos observaciones incompatibles (X03/X04 frente a éxito) siguen siendo contradicción.
        if r["terminal"] and r["terminal"]["id"] in ("L01", "L02", "L15", "L16"):
            for z in decisivos:
                t = "entorno contradicho por el log: descripción del arnés inexacta [S12] (%s frente a %s)" % (
                    z["id"], r["terminal"]["id"])
                if t not in r["notas"]:
                    r["notas"].append(t)
                    lec["arnes_inexacto"].append(t)
        if r["terminal"] and r["terminal"]["id"] in ("L01", "L02", "L13", "L15", "L16") and ids_con & {"X03", "X04"}:
            lec["contradictorio"].append("éxito en el log con una conexión que lo hace imposible")
        # §1.6.3 en cualquier orden (N24: antes solo si el L03/L04 era la última fila)
        if any(f["id"] in ("L03", "L04") for f in propias) and any(f["id"] in ("L01", "L02", "L05", "L06", "L07", "L15", "L16", "F1") for f in propias):
            lec["contradictorio"].append("rechazo previo del circuito y llamada a FHIR para el mismo MSH-10")
        if any(f["id"] == "L14" for f in propias) and any(f["id"] == "L13" for f in propias):          # [S50]
            lec["contradictorio"].append("el punto de entrada rechazó y aceptó el mismo MSH-10")
        if any(f["id"] == "L14" for f in propias) and any(f["id"] in ("L01", "L02", "L05", "L06", "L07", "L15", "L16", "F1") for f in propias):
            lec["contradictorio"].append("el punto de entrada rechazó y hubo llamada a FHIR para el mismo MSH-10")  # D4
        # causas §1.7
        if "X06" in ids_con:                                             # [S11] ACK perdido por el plazo del emisor
            r["causas_d0"].append("entorno:tiempo")
        if "X05" in ids_con and hay_sesion:
            r["causas_d0"].append("entorno:conexion")
        if unico and any(f["id"] == "L10" for f in filas):
            r["causas_d0"].append("entorno:conexion")
        if any(f["id"] == "L11" and f["msh10"] == m10 for f in filas):
            r["causas_d0"].append("trama")
        fab = [f for f in filas if f["id"] == "L09" and (f["msh10"] == m10 or (unico and f["msh10"] is None))]
        if fab:
            r["fabricado"] = fab[-1]["datos"]["codigo"].upper()
        lec["por_mensaje"][k] = r
    return lec
