#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificador unificado: implementación de la Parte 2 de `diseno-verificador-fable.md` (Fable, a ciegas).
Corre la lectura (lectura_evidencia), el acuse de referencia y el mapeador de referencia; fusiona los
hallazgos por (mensaje, hecho); emite un veredicto por caso y una ficha para la persona experta.
El agente, si entra, solo explica este informe: no añade hallazgos ni cambia veredictos [S5].

Desviaciones declaradas:
  DV-V1: «no hay canónico para este mensaje» (mapeador, varios mensajes en un marco): si la lectura da
         causa `trama` para ese mensaje, es una faceta del hallazgo de trama (hecho `existencia`); si no,
         `fidelidad` con hecho `existencia`. El diseño no lo lista en la tabla de solapes.
  DV-V2: (retirada) el segundo PID lo decide S14: AE 100, cuenta; ya no hay estado «disputado».
  DV-V3: el alcance ampliado del mapeador (canónico sin AA observado) se obtiene llamando a
         mapeador_referencia.revisar con un acuse AA sintético y descartando lo que diga de MSA-2.
  DV-V4: [S43] (diseno-s42-s43-fable.md) con HTTP 400/422 (L05 o F1, por código) y canónico, la misma llamada sintética;
         de esos mensajes solo se quedan las diferencias campo a campo (fuera imposibles, estructura, MSA-2 y
         tolerancias), que salen como fidelidad/transformado con causa «transformacion»; nunca ponen el alcance
         ampliado; cuentan solo si el mensaje ya tiene otro hallazgo que cuenta, y no cambian la categoría: la anotan
         con «+transformado». Sin diferencias, una nota S43 que no cuenta.

Decisiones del sitio S6-S18 (diseno-s6-s16-fable.md): certezas literales para S10, S11, S14, S15 y S16; sin D5
(S13); orden de veredicto contradictorio -> sin_intercambio -> lectura (S12); evidencia descodificado /
escape_sin_resolver / invisible (S7-S9).
  DV-S8: la nota «PID-7 no contrastable … (límite L16)» la escribe el acuse (notas), no el mapeador: la lista
         `estructura` del mapeador se convierte en discrepancia y el diseño pide «sin discrepancia».

Decisiones S19-S29 (diseno-s19-s21-fable.md): Gender alterado por la tabla de consulta = hallazgo entorno/tabla [S20],
fallo_entorno con cualquier MSA-1 y ambos con subtipo <datos>+<resto> [S23]; tolerancias S21/S22/S26/S28; contenido
no acusado por fallo del sistema, que cuenta solo si el circuito respondió AA [S25]; línea SEGMENTOS en la ficha.

S31-S37 (diseno-s31-s34-fable.md): tolerancias de nombres con varias etiquetas ([S30][S32][S33][S34]), C8 con los
recortes de blancos, alternativas de trama S31/S35/S36 como tolerancias, ACK sobrante como nota, línea TRAMA en la ficha.

Multi-tipo (diseno-multitipo-fable.md §1.3, §5): `verificar(e, pe=None)` resuelve el punto de entrada (parámetro >
e["punto_entrada"] > adt_a01) y lo pasa al acuse; con un PE distinto de adt_a01 no hay mapeador ni canónico (L-MT1) y la
ficha lleva la línea PUNTO. Con adt_a01 la salida es la de siempre, byte a byte.

ORU -> FHIR (diseno-oru-fable.md §5.2): el PE con `mapeador = "oru"` (oru_fhir) despacha a mapeador_oru.revisar sobre
`sesiones[].canonico_oru` con las mismas rutas DV-V3/DV-V4; sus diferencias campo a campo son fidelidad/guardado con hecho
OBX-n/OBR-n (hecho sin índice del OBX: varios OBX con el mismo campo mal se fusionan en un hallazgo, DV-ORU-4); un OBX u OBR
que no llegó al canónico es fidelidad/recuento (subtipo NUEVO, que _subs cuenta como «guardado»). Con cualquier otro PE,
idéntico a antes.

Almacén FHIR v1.1 (diseno-oru-v11-fable.md §3-§4; S65, S67-S72): solo con mapeador `oru` Y `sesiones[].almacen_oru` presente,
almacen_oru.evaluar compara lo releído del servidor con la proyección FHIR del esperado: fidelidad/almacen|duplicado|ausente (origen
`almacen`, literal, causa transformacion/escritura/transformacion+escritura por la comparación a tres), acuse/rechazo_con_escritura
(hecho destino) y notas almacen_extra/almacen_vacio_tras_rechazo/almacen_no_leido/almacen_canonico/AMB-ORU-7; `fallos` del almacén
van a lectura (indeterminado/lectura). `fusionar` cruza mapeador y almacén por (mensaje, hecho) sin código nuevo; `escritura` en
veredicto() también es verdadera cuando el almacén muestra n > 0. Sin almacen_oru (bundles ORU v1) el JSON de verificar es idéntico;
la ficha gana la línea «ALMACÉN  no leído (L-ORU-1)» solo en oru_fhir [S70].

Uso: python3 verificador.py --autoprueba
     python3 verificador.py --ficha <bundles.jsonl> <instancia>
"""
import json
import re
import sys
import unicodedata

import acuse_referencia as AR
import almacen_adt as AA2
import almacen_oru as AO
import hechos_normativos as H
import lectura_evidencia as LE
import mapeador_adt as MA
import mapeador_oru as MO
import mapeador_referencia as MR
import puntos_entrada as PE

PRECEDENCIA = ["valor_imposible_aceptado", "fidelidad", "estructura", "contenido", "acuse", "entorno", "trama", "lectura"]
CLASES_14 = {"valor_imposible_aceptado", "fidelidad", "estructura", "contenido"}
CLASES_57 = {"acuse", "entorno", "trama"}
CERTEZA = ["literal", "declarado D", "declarado", "supuesto", "ambiguedad", "decision_pendiente", "lectura"]  # «declarado <regla>»: perfil
GRAVEDAD = ["ambos", "fallo_silencioso", "acuse_incorrecto", "fallo_entorno", "indeterminado", "correcto", "sin_intercambio"]
CAMPO_A_HECHO = {"Gender": "PID-8", "Identifier": "PID-3", "FamilyName": "PID-5", "GivenName": "PID-5", "BirthDate": "PID-7",
                 "MsgControlId": "MSH-10", "SendingApp": "MSH-3", "SendingFacility": "MSH-4", "MsgEvent": "MSH-9",
                 "ProcessingId": "MSH-11", "Truncado": "longitud"}
REGLA_CLASE = {"P2a": "estructura", "P2b": "estructura", "P2c": "estructura", "P3.3": "estructura", "P3.4": "estructura",
               "P3.5": "estructura",
               "P4": "contenido", "P5": "contenido", "P5'": "contenido", "P5f": "contenido"}


def _rango(c):
    return next(i for i, p in enumerate(CERTEZA) if c.startswith(p))


def _debil(cs):
    return max(cs, key=_rango) if cs else "literal"


def _h(k, clase, subtipo, hecho, que, origen, cuenta=True, certeza="literal", causa=None, alternativa=None, nivel=None,
       opinion=None, evidencia=None):
    return {"mensaje": k, "clase": clase, "subtipo": subtipo, "hecho": hecho, "que": [que], "origen": [origen],
            "cuenta": cuenta, "certeza": certeza, "causa": causa, "alternativa": alternativa, "nivel": nivel,
            "estado": "firme", "opinion_circuito": opinion, "evidencia": evidencia or {}}


def _invisible(s):
    """[S7] algún carácter de categoría Cf (anchura cero) que no sea el BOM inicial."""
    return isinstance(s, str) and any(unicodedata.category(c) == "Cf" for c in s.lstrip("\ufeff"))


def _no_ascii_de(s):
    return [c for c in s if ord(c) > 0x7f] if isinstance(s, str) else []


def evidencia_fidelidad(m, hecho, ve, vo, descod=None):
    """Banderas de evidencia de un hallazgo de fidelidad (diseno-citas-s38-s39-fable.md §1). Solo eligen citas: no
    tocan veredicto, clase, certeza ni texto. hecho = "SEG-n"; ve/vo = esperado y observado (cadena o tupla)."""
    ev = {}
    seg, _, n = hecho.partition("-")
    s = (m.segmentos(seg) or [None])[0] if seg and n.isdigit() else None
    crudo = m.campo(s, int(n)) if s is not None else ""
    if any("%s-%s" % (d["seg"], d["n"]) == hecho and d["via"] in ("utf-8", "latin-1") for d in m.descodificados):
        ev["descodificado"] = True                                                    # [S9]
    if m.e and m.e in crudo:
        ev["escape_en_entrada"] = True                                                # [E2 §2.7]
    if isinstance(vo, str) and m.e in vo and not (isinstance(ve, str) and m.e in ve) and ev.get("escape_en_entrada"):
        ev["escape_sin_resolver"] = True                                              # [S8]
    if _invisible(ve):
        ev["invisible"] = True                                                        # [S7] solo si el esperado lo lleva
    elif _invisible(vo):
        ev["invisible_observado"] = True                                              # informativo: no cita
    if (_no_ascii_de(ve) and isinstance(vo, str) and vo and _no_ascii_de(ve) != _no_ascii_de(vo)
            and not ev.get("descodificado")):
        ev["no_ascii_distinto"] = True                                                # [S38]
    ev["clase_msh18"] = (descod or {}).get("clase_msh18") or AR.clase_msh18(m)[0]
    if isinstance(ve, tuple) and "male" in ve:
        ev["valueset"] = True                                                         # [S22]
    return ev


def _obs_ack(e, m10s):
    obs = MR.mensajes(e.get("ack") or "")
    libres, out = list(obs), []
    for m10 in m10s:
        a = next((o for o in libres if o.segmentos("MSA") and o.campo(o.segmentos("MSA")[0], 2) == m10), None)
        if a is None and libres:                                     # D7: el primer ACK libre, salvo el que acusa a OTRO mensaje
            a = next((o for o in libres if not (o.segmentos("MSA") and o.campo(o.segmentos("MSA")[0], 2) in set(m10s) - {m10})), None)
        if a is not None:
            libres.remove(a)
            msa = a.segmentos("MSA")
            errs = [(a.campo(z, 3).split(a.c)[0], a.campo(z, 4).split(a.c)[0]) for z in a.segmentos("ERR")]
            out.append({"msa1": (a.campo(msa[0], 1) if msa else "").upper(), "msa2": a.campo(msa[0], 2) if msa else "",
                        "err": errs, "msh9": a.campo(a.segs[0], 9)})
        else:
            out.append(None)
    return out


def _k_de(z):
    m = re.match(r"mensaje (\d+): (.*)$", z)
    return (int(m.group(1)) - 1, m.group(2)) if m else (0, z)


def _mapeador(e, ms, lec, revisar=MR.revisar, clave="canonico", obs=None):
    """-> (discrepancias por k, tolerancias por k, alcance_ampliado, ruta S43 por k). `revisar`/`clave`: el mapeador y la clave
    del canónico en las sesiones (adt_a01: MR.revisar/canonico; oru_fhir: mapeador_oru/canonico_oru, §5.2). `obs`: los ACK
    observados por mensaje; con AA y fila de éxito el canónico se exige (S-VE-1)."""
    canon = [s.get(clave) if isinstance(s.get(clave), dict) else None for s in e.get("sesiones") or []]   # D8: alineados por mensaje
    exigidos = [k for k in range(len(ms)) if obs and k < len(obs) and obs[k] and AR.equiv_msa1(obs[k]["msa1"]) == "AA"
                and (lec["por_mensaje"].get(k) or {}).get("destino") == "exito" and (k >= len(canon) or canon[k] is None)]
    if not any(isinstance(c, dict) for c in canon) and not exigidos:
        canon = []                                                    # sin ningún canónico ni ninguno exigido: fuera de alcance
    elif exigidos and len(canon) < len(ms):
        canon += [None] * (len(ms) - len(canon))                      # [S-VE-1] alineada, para que el que falta se vea
    r = revisar(e.get("mensaje"), canon, e.get("ack"))
    ampliado = False
    escrito = any(v.get("destino") == "exito" for v in lec["por_mensaje"].values())      # IMPL-1: solo si se escribió
    rechazado = {k: v for k, v in lec["por_mensaje"].items() if v.get("destino") == "http" and v.get("http") in (400, 422)}
    s43 = {}
    if r is None and canon and ms and (escrito or rechazado):                           # DV-V3; DV-V4 [S43]
        falso = "MSH|^~\\&|X|X|X|X|t||ACK^A01^ACK|X|P|2.5\rMSA|AA|" + ms[0].campo(ms[0].segs[0], 10)
        r = revisar(e.get("mensaje"), canon, falso)
        if r is not None:
            for k, v in rechazado.items():
                s43[k] = {"http": v["http"], "code": v.get("code"), "lineas": []}
            d_ = []
            for z in r[0]:
                if z.startswith("MSA-2"):
                    continue
                k, txt = _k_de(z)
                if k not in rechazado:
                    d_.append(z)
                elif re.match(r"^[^:]+: esperado .*, observado .*$", txt):    # solo campo a campo: fuera imposibles y estructura
                    s43[k]["lineas"].append(txt)
            t_ = [z for z in r[1] if _k_de(z)[0] not in rechazado]                 # las tolerancias de la ruta S43 no salen
            r = (d_, t_) if escrito else None
            ampliado = escrito                                                  # S43 nunca pone el alcance ampliado
    disc, tol = {}, {}
    if r is None:
        return disc, tol, ampliado, s43
    for lista, dest in ((r[0], disc), (r[1], tol)):
        for z in lista:
            k, txt = _k_de(z)
            dest.setdefault(k, []).append(txt)
    return disc, tol, ampliado, s43


def _campo(k, z, ms, esp, lec, ampliado):
    """Hallazgo de una diferencia campo a campo del mapeador («Campo: esperado X, observado Y»): tolerancia C8, entorno/tabla
    [S20] o fidelidad/guardado. Lo usan el bloque del mapeador y la ruta S43."""
    campo = z.split(":")[0]
    cert = "literal"
    # C8: el acuse truncó ese campo [S3] y lo observado es el esperado recortado -> tolerancia
    mv = re.match(r"[^:]+: esperado (.*), observado (.*)$", z)          # «Campo:» o «OBX j (código) Campo:» (§5.2)
    if mv and k < len(esp) and CAMPO_A_HECHO.get(campo) in [t.split(":")[0] for t in esp[k].get("truncados", [])]:
        import ast
        try:
            ve, vo = ast.literal_eval(mv.group(1)), ast.literal_eval(mv.group(2))
        except (ValueError, SyntaxError):
            ve, vo = None, None
        cands = [ve] if isinstance(ve, str) else []
        if campo in ("FamilyName", "GivenName") and isinstance(ve, str) and k < len(ms):     # [S30]-[S34]
            pid_c = ms[k].segmentos("PID")
            partes = MR.partes_nombre(ms[k], pid_c[0] if pid_c else "")[0 if campo == "FamilyName" else 1]
            cands = sorted(MR.recortes(partes), key=len, reverse=True)
        v = next((c for c in cands if isinstance(vo, str) and vo and c.startswith(vo)), None)
        if v is not None:
            b = MR.blancos(ve, v, partes) if v != ve else None
            extra = "" if b is None else " " + "".join("[%s]" % d_ for d_ in b["decisiones"])
            return _h(k, "tolerancia", "truncado_S3", CAMPO_A_HECHO[campo], z + extra, "mapeador", cuenta=False)
    if campo == "FamilyName" and k < len(ms):
        pid = ms[k].segmentos("PID")
        if pid and ms[k].s in ms[k].campo(pid[0], 5).split(ms[k].c)[0]:
            cert = "declarado D"
    hecho = CAMPO_A_HECHO.get(campo) or MO.hecho_de(z) or MA.hecho_de(z) or campo   # hecho_de: ORU (§5.2) y ADT (§7.1), si no None
    ev = {"alcance_ampliado": ampliado}
    alt = None
    ent = None
    if campo == "Gender" and mv and k < len(ms):                                   # [S20] solo si la alteración lo explica
        import ast
        try:
            vo_g = ast.literal_eval(mv.group(2))
        except (ValueError, SyntaxError):
            vo_g = None
        pid_k = ms[k].segmentos("PID")
        pid8_k = ms[k].desescapa(ms[k].campo(pid_k[0], 8)) if pid_k else ""
        ent = LE.explica_gender(lec, pid8_k, vo_g)
        if ent is None and lec.get("tabla_sexo"):
            ev["entorno_no_explica"] = "; ".join("%s: %s" % (x["id"], x["texto"]) for x in lec["tabla_sexo"])
            z = z + " (el entorno declara una alteración que no explica este valor)"
    if ent is not None:
        ev["entorno"] = "%s: %s" % (ent["id"], ent["texto"])
        return _h(k, "entorno", "tabla", "PID-8", z, "mapeador", causa="entorno:tabla", evidencia=ev)
    if k < len(ms):
        ve, vo = None, None
        if mv:
            try:
                import ast
                ve, vo = ast.literal_eval(mv.group(1)), ast.literal_eval(mv.group(2))
            except (ValueError, SyntaxError):
                ve, vo = None, None
        ev.update(evidencia_fidelidad(ms[k], hecho, ve, vo, esp[k].get("descodificacion") if k < len(esp) else None))
        if ev.get("descodificado") and k < len(esp) and (esp[k].get("descodificacion") or {}).get("certeza") == "ambiguedad AMB-10":
            cert, alt = "ambiguedad AMB-10", "correcto"
    return _h(k, "fidelidad", "guardado", hecho, z, "mapeador", certeza=cert, alternativa=alt, evidencia=ev)


def verificar(e, pe=None):
    pe = PE.resolver(pe, e)                                                             # §1.3
    ms = MR.mensajes(e.get("mensaje"))
    m10s = [m.campo(m.segs[0], 10) for m in ms]
    lec = LE.leer(e, m10s, pe["nombre"])
    esp = AR.calcular(e, lec, pe=pe)
    ds = AR.comparar(e, esp, pe=pe)
    obs = _obs_ack(e, m10s) if ms else []
    oru = pe.get("mapeador") == "oru"
    adt = pe.get("mapeador") == "adt"                                             # diseno-adt-fable.md §7.3
    if pe["nombre"] == "adt_a01":
        disc, tol, ampliado, s43 = _mapeador(e, ms, lec, obs=obs)
    elif oru:                                                                           # diseno-oru-fable.md §5.2
        disc, tol, ampliado, s43 = _mapeador(e, ms, lec, lambda t, c, a: MO.revisar(t, c, a, pe), "canonico_oru", obs)
    elif adt:                                                                           # diseno-adt-fable.md §7.3
        disc, tol, ampliado, s43 = _mapeador(e, ms, lec, lambda t, c, a: MA.revisar(t, c, a, pe), "canonico_adt", obs)
    else:
        disc, tol, ampliado, s43 = {}, {}, False, {}                                    # L-MT1: sin mapeador ni canónico
    hs = []
    # --- mapeador
    for k, lista in disc.items():
        for z in lista:
            if z.startswith("MSA-2"):
                continue                                                               # C7: vale el D4 del acuse
            # [S10] también MSH-n / PID-n; ORU: «OBX j: OBX-5 '1,5' no es un NM válido y se aceptó» (sin el prefijo «OBX j: »)
            m = re.match(r"^((?:PID|MSH|OBX|OBR|PV1)-\d+) .* y se aceptó$", re.sub(r"^OB[XR] \d+: ", "", z))   # PV1: adt_fhir
            mr = re.match(r"^(Informes|Observaciones): esperado (\d+), observado (\d+)$", z)
            if "no es ADT^A01 y se aceptó" in z or "no es ORU^R01 y se aceptó" in z:
                hs.append(_h(k, "estructura", "tipo", "MSH-9", z, "mapeador"))
            elif mr:                                                                    # fidelidad/recuento (§5.2): un OBX/OBR descartado
                hs.append(_h(k, "fidelidad", "recuento", "OBR" if mr.group(1) == "Informes" else "OBX", z, "mapeador",
                             evidencia={"alcance_ampliado": ampliado, "esperado": int(mr.group(2)), "observado": int(mr.group(3))}))
            elif m:
                hs.append(_h(k, "valor_imposible_aceptado", "aceptado_imposible", m.group(1), z, "mapeador"))
            elif "exactamente un PID" in z:
                hs.append(_h(k, "estructura", "pid_repetido", "PID", z, "mapeador"))
            elif z.startswith("no hay canónico"):                                           # DV-V1 (ajustado)
                trama = "trama" in (lec["por_mensaje"].get(k) or {}).get("causas_d0", [])
                o_k = obs[k] if k < len(obs) else None
                if trama:
                    hs.append(_h(k, "trama", "trama", "existencia", z, "mapeador"))                    # [S15]
                elif o_k is None:
                    hs.append(_h(k, "acuse", "recuento", "existencia", z, "mapeador"))
                elif AR.equiv_msa1(o_k["msa1"]) != "AA":
                    continue                                                                    # S-VE-1: sin AA no se compara (L24)
                elif (lec["por_mensaje"].get(k) or {}).get("destino") == "exito":              # S-VE-1: AA y fila de éxito
                    hs.append(_h(k, "fidelidad", "sin_canonico", "existencia", z + ": el circuito acusó AA y declaró haber escrito "
                                 "sin registrar lo que escribió; el punto %s lo exige (S-VE-1)" % pe["nombre"], "mapeador", causa="escritura"))
                else:
                    hs.append(_h(k, "nota", "sin_canonico", "existencia", z + ": AA sin fila de éxito, el canónico no se exige (L5)",
                                 "mapeador", cuenta=False))
            else:
                hs.append(_campo(k, z, ms, esp, lec, ampliado))
    for k, lista in tol.items():
        for z in lista:
            if oru or adt:                                                              # ORU/ADT: «[Sn] OBX j: OBX-n …» tolerancia; «[AMB-ORU-n]…» nota
                mo_ = re.match(r"^\[([^\]]+)\] (?:mensaje \d+: )?(?:OB[XR] \d+: )?(.*)$", z)
                etq = mo_.group(1) if mo_ else "S4"
                mh = re.search(r"\b((?:OBX|OBR|PID|MSH|PV1)-\d+)", z)
                hs.append(_h(k, "tolerancia" if etq in ("S4", "S22") else "nota", etq, mh.group(1) if mh else "canonico", z, "mapeador",
                             cuenta=False))
                continue
            if z.startswith("[L24] "):                                                    # D10: límite de alcance, no tolerancia
                hs.append(_h(k, "nota", "L24", "MSA", z, "mapeador", cuenta=False))
                continue
            mt = re.match(r"\[(S\d+)\]", z)
            mc = re.match(r"^((?:\[S\d+\])+) (\w+):", z)                                 # [S30]-[S34] campo y etiquetas
            hecho_t = CAMPO_A_HECHO.get(mc.group(2), "PID-8") if mc else "PID-8"
            ev_t = {"decisiones": re.findall(r"S\d+", mc.group(1))} if mc else {}
            hs.append(_h(k, "tolerancia", mt.group(1) if mt else "S4", hecho_t, z, "mapeador", cuenta=False, evidencia=ev_t))
    # --- almacén FHIR (diseno-oru-v11-fable.md §3-§4.1): solo con mapeador oru y alguna sesión con almacen_oru [S65]
    escrito_alm, alm_res = {}, {}
    clave_alm, mod_alm = ("almacen_oru", AO) if oru else ("almacen_adt", AA2) if adt else (None, None)    # adt: §5.5
    if mod_alm and any(isinstance(s.get(clave_alm), dict) for s in e.get("sesiones") or [] if isinstance(s, dict)):
        m1s = [AR.equiv_msa1(o["msa1"]) if o else None for o in obs]
        alm_res = mod_alm.evaluar(e, ms, m1s, pe, lec["por_mensaje"])
        for k, res in alm_res.items():
            escrito_alm[k] = res["escrito"]
            for z in res["lineas"]:
                hs.append(_h(k, z["clase"], z["subtipo"], z["hecho"], z["que"], "almacen", cuenta=z["cuenta"], causa=z["causa"]))
            lec["lectura_hallazgos"] += res["fallos"]                                   # §3.5: lectura fallida -> indeterminado
            pm = lec["por_mensaje"].get(k)
            if pm:                                                                      # §4.2: L5' deja de decir «no observable»
                pm["notas"] = [t.replace("(almacén no observable)", "(almacén leído tras el ACK: v1.1)") if t.startswith("L5'") else t
                               for t in pm["notas"]]
    # --- acuse
    por_k = {}
    sin_ack = [k for k in range(len(esp)) if k >= len(obs) or obs[k] is None]
    for z in ds:
        if z.get("id") == "nota":                                                       # AP-1: P0.b sin MSH
            continue
        k = z.get("k")
        if k is None:                                                                   # IMPL-2: el D0 «recuento»
            k = sin_ack[-1] if sin_ack else len(esp) - 1
        por_k.setdefault(k, []).append(z)
    for k, x in enumerate(esp):
        if x.get("sin_intercambio") or x.get("debe_haber_ack") == "indeterminado":
            continue
        dst = x.get("destino") or {}
        amb = [a for a in x.get("ambiguedades", [])]
        amb_tag = next((re.match(r"(AMB-\d+|A-\d+|DV\d)", a).group(1) for a in amb if re.match(r"(AMB-\d+|A-\d+|DV\d)", a)), None)
        for t in x.get("tolerancias", []):
            mt = re.match(r"(?:\[(S\d+)\] )?([A-Z][A-Z0-9]{2}-\d+)", t)
            hs.append(_h(k, "tolerancia", (mt.group(1) if mt else None) or "S4", mt.group(2) if mt else "PID-8", t,
                         "acuse", cuenta=False))
        c39 = (x.get("descodificacion") or {}).get("contradiccion")                   # [S39] nota que no cuenta
        if c39:
            hs.append(_h(k, "nota", "S39", "MSH-18", c39["texto"], "acuse", cuenta=False, evidencia=dict(c39)))
        dk = por_k.get(k, [])
        codigo = [z for z in dk if z["id"] in ("D1", "D2", "D3")]
        mayores = [z for z in codigo if z["cuenta"]]
        o = obs[k] if k < len(obs) else None
        if mayores:
            m1 = AR.equiv_msa1(o["msa1"]) if o else ""
            prim = x["err"][0] if x.get("err") else None
            regla = prim["regla"] if prim else None
            hecho = (prim["donde"].split(".")[0] if prim else "ACK")
            if hecho == "destino":
                hecho = "destino"
            causa = next((z["causa"] for z in dk if z.get("causa")), None)
            certeza, alt, nivel = "literal", None, prim["nivel"] if prim else None
            if m1 == "AA" and x.get("msa1_aplicacion") in ("AE", "AR") and regla in REGLA_CLASE:
                clase, sub = REGLA_CLASE[regla], ("aceptado_imposible" if REGLA_CLASE[regla] == "contenido" else "estructura")
            elif m1 == "AA" and x.get("msa1_aplicacion") == "AR" and regla == "P7":
                clase, sub = "acuse", "aceptacion_falsa"
            elif m1 in ("AE", "AR") and x.get("msa1_aplicacion") == "AA":
                clase, sub = "acuse", "falso_rechazo"
                op = dst.get("opinion")
                hecho = (op["datos"].get("hecho") if op and op["datos"].get("hecho") not in (None, "otro", "longitud") else
                         ("longitud" if op and op["datos"].get("hecho") == "longitud" else "ACK"))
            elif m1 in ("CA", "CE", "CR") and (x.get("modo") == "original" or dst.get("fabricado")):
                clase, sub, hecho = "acuse", "fabricado", "ACK"
            else:
                clase, sub = "acuse", "codigo"
            f2 = any("(F2)" in a for a in amb)
            if f2:                                    # V16: depende de una fila no reconocida -> no cuenta hasta que se lea
                certeza, alt = "lectura", None
            elif nivel == "estricto" and clase in ("contenido", "estructura"):     # solo con nivel estricto a petición
                certeza, alt = "literal", "correcto"
            elif regla == "P5'":                                                      # [S10]
                certeza, alt = "literal", None
            elif x.get("perfil_reglas"):                                              # el esperado sale de una regla del perfil
                certeza = "declarado " + x["perfil_reglas"][0]
            elif amb_tag:
                certeza = ("supuesto " if amb_tag.startswith("A-") else "ambiguedad ") + amb_tag
            que = "; ".join(z["que"] for z in codigo)
            if nivel == "estricto" and clase in ("contenido", "estructura"):
                que += "; calculado en nivel estricto a petición; bajo S6 (nivel consumido) no cuenta"
            hs.append(_h(k, clase, sub, hecho, que, "acuse", certeza=certeza, causa=causa,
                         alternativa=alt, nivel=nivel, cuenta=not f2,
                         opinion=(dst.get("opinion") or {}).get("texto"),
                         evidencia={"esperado": "%s %s" % (x.get("msa1_aplicacion"), prim["err3"] if prim else ""),
                                    "observado": "%s %s" % (m1, ",".join(c for c, _ in (o or {}).get("err", [])))}))
        elif codigo:
            prim = x["err"][0] if x.get("err") else None
            for z in codigo:
                if z.get("causa") == "rechazo_del_destino":                             # [S21] [S24]
                    hs.append(_h(k, "tolerancia", "S21", prim["donde"].split(".")[0] if prim else "ACK", z["que"], "acuse",
                                 cuenta=False, causa=z["causa"],
                                 evidencia={"esperado": "AE %s" % (prim["err3"] if prim else ""),
                                            "observado": "AR %s" % ",".join(c for c, _ in (o or {}).get("err", [])),
                                            "http": dst.get("http")}))
                elif (z.get("causa") or "").startswith("alternativa_"):                 # [S26] [S28]
                    mw = re.search(r"sobre (\S+?)( |\)|$)", z["que"])
                    hs.append(_h(k, "tolerancia", z["causa"][len("alternativa_"):], mw.group(1) if mw else "ACK", z["que"], "acuse",
                                 cuenta=False, causa=z["causa"],
                                 evidencia={"esperado": "%s %s" % (x.get("msa1_aplicacion"), prim["err3"] if prim else ""),
                                            "observado": "%s %s" % ((o or {}).get("msa1"), ",".join(c for c, _ in (o or {}).get("err", [])))}))
                else:
                    hs.append(_h(k, "acuse", "menor", "ACK", z["que"], "acuse", cuenta=False))
        if o is not None and o.get("msa1") == "AA":                                     # [S25] contenido no acusado y aceptado
            p7 = (x.get("err") or [{}])[0].get("err3", "207")
            for cna in x.get("contenido_no_acusado") or []:
                cl = REGLA_CLASE.get(cna["regla"], "contenido")
                hs.append(_h(k, cl, "aceptado_imposible" if cl == "contenido" else "estructura", cna["donde"].split(".")[0],
                             "contenido no acusado [S25]: %s %s; aceptado con AA" % (cna["err3"], cna["donde"]), "acuse",
                             nivel=cna["nivel"], evidencia={"esperado": "AR %s [S25]; con destino sano AE %s" % (p7, cna["err3"]),
                                                            "observado": "AA"}))
        for z in dk:
            if z["id"] == "D0":
                causa = z.get("causa")
                if causa in ("entorno:tiempo", "entorno:conexion"):
                    hs.append(_h(k, "entorno", "ausente", "existencia", z["que"], "acuse", causa=causa, cuenta=z["cuenta"],
                                 certeza="literal" if causa == "entorno:tiempo" else "supuesto A-17"))      # [S11]
                elif causa == "trama":                                                                     # [S15]; ACK sobrante [S31]
                    hs.append(_h(len(esp) - 1 if "recuento" in z["que"] else k, "trama", "trama", "existencia", z["que"], "acuse",
                                 causa="trama", cuenta=z["cuenta"]))
                else:
                    hs.append(_h(k, "acuse", "ausente" if "ausente" in z["que"] else "recuento", "existencia", z["que"], "acuse",
                                 cuenta=z["cuenta"]))
            elif z["id"] == "D4":
                hs.append(_h(k, "acuse", "inservible", "ACK.MSA-2", z["que"], "acuse"))
            elif z["id"] == "D6":                                                           # D5 no existe [S13]
                hs.append(_h(k, "acuse", "cabecera", "ACK.D6", z["que"], "acuse", cuenta=False))
            elif z["id"] == "N":                                                            # nota del perfil del sitio
                hs.append(_h(k, "nota", "perfil", "ACK", z["que"], "acuse", cuenta=False))
    # --- [S43] con 400/422 el canónico se compara con el esperado para atribuir la causa (DV-V4); atribuye, no detecta
    for k, s_ in sorted(s43.items()):
        base_k = any(h["cuenta"] and h["mensaje"] == k and h["clase"] not in ("lectura", "tolerancia", "nota") for h in hs)
        nuevos = [_campo(k, z, ms, esp, lec, False) for z in s_["lineas"]]
        for h in nuevos:
            h["evidencia"].pop("alcance_ampliado", None)
            h["evidencia"].update({"alcance_s43": True, "http": s_["http"], "code": s_["code"]})
            if h["clase"] == "tolerancia":
                continue
            if h["clase"] == "fidelidad":
                h["subtipo"], h["causa"] = "transformado", "transformacion"
            h["que"].append("[S43] FHIR rechazó con HTTP %d (nada se guardó): el canónico que el circuito construyó difiere "
                            "del esperado; la transformación es causa del caso (L22)" % s_["http"])
            h["cuenta"] = base_k
            if not base_k:
                h["que"].append("no cuenta: el acuse fue el esperado y nada se guardó; S43 atribuye, no detecta [S44] (L22)")
        hs += nuevos
        if not s_["lineas"]:
            hs.append(_h(k, "nota", "S43", "canonico", "[S43] con HTTP %d se comparó el canónico con el esperado del mapeador: "
                         "sin diferencias en los campos comparables; el rechazo de FHIR no se atribuye a la transformación "
                         "(L22)" % s_["http"], "mapeador", cuenta=False, evidencia={"http": s_["http"], "code": s_["code"]}))
    for t in lec["lectura_hallazgos"] + lec["contradictorio"]:
        hs.append(_h(0, "lectura", "lectura", "lectura", t, "lectura", cuenta=False, certeza="lectura"))
    hs = fusionar(hs)
    ver = veredicto(hs, esp, obs, lec, ms, ampliado, escrito_alm)
    return {"mensajes": [{"k": k, "msh10": m10} for k, m10 in enumerate(m10s)], "lectura": {
                "resultado_destino": [dict((kk, v) for kk, v in r.items() if kk not in ("terminal", "opinion")) for r in lec["por_mensaje"].values()],
                "entorno": [z["id"] + ":" + z["clase"] for z in lec["entorno"]],
                "conexion": [z["id"] + ":" + z["clase"] for z in lec["conexion"]],
                "opiniones_circuito": [r["opinion"]["texto"] for r in lec["por_mensaje"].values() if r.get("opinion")],
                "contradictorio": lec["contradictorio"], "arnes_inexacto": lec.get("arnes_inexacto", []),
                "vocabulario_nuevo": lec["vocabulario_nuevo"],
                "tabla_sexo": [{"id": z["id"], "de": sorted(z["de"]), "a": z["a"], "texto": z["texto"]} for z in lec.get("tabla_sexo") or []]},
            "esperado": [{"msa1": x.get("msa1"), "msa1_aplicacion": x.get("msa1_aplicacion"), "err": x.get("err"),
                          "debe_haber_ack": x.get("debe_haber_ack"), "notas": x.get("notas", []),
                          "descodificacion": x.get("descodificacion"), "version_msh12": x.get("version_msh12"),
                          "alternativas_aceptadas": x.get("alternativas_aceptadas", []),
                          "contenido_no_acusado": x.get("contenido_no_acusado", [])} for x in esp],
            "observado": obs, "hallazgos": hs, "veredicto": ver, "hechos_de_tabla": H.hechos(e),
            "trama": (esp[0].get("trama") if esp else None) or {k_: v_ for k_, v_ in MR.trama(e.get("mensaje")).items() if k_ != "marcos"},
            "punto_entrada": pe["nombre"], **({"almacen": {k: res["resumen"] for k, res in alm_res.items()}} if alm_res else {})}


def fusionar(hs):
    """Clave (mensaje, hecho): un hallazgo por clave; clase de mayor precedencia; certeza la más débil."""
    cuentan = [h for h in hs if h["cuenta"]]
    resto = [h for h in hs if not h["cuenta"]]
    grupos, orden = {}, []
    for h in cuentan:
        c = (h["mensaje"], h["hecho"]) + (("S43",) if (h.get("evidencia") or {}).get("alcance_s43") else ())  # [S43] aparte:
        if c not in grupos:                                                    # no arrastra al hallazgo base (DV-V4)
            grupos[c] = []
            orden.append(c)
        grupos[c].append(h)
    out = []
    for c in orden:
        g = sorted(grupos[c], key=lambda h: PRECEDENCIA.index(h["clase"]))
        f = dict(g[0])
        f["que"] = [q for h in g for q in h["que"]]
        f["origen"] = sorted({o for h in g for o in h["origen"]})
        f["certeza"] = _debil([h["certeza"] for h in g])
        f["alternativa"] = next((h["alternativa"] for h in g if h["alternativa"]), None)
        f["causa"] = next((h["causa"] for h in g if h["causa"]), None)
        f["opinion_circuito"] = next((h["opinion_circuito"] for h in g if h["opinion_circuito"]), None)
        for h in g[1:]:
            f["evidencia"] = dict(f.get("evidencia") or {}, **{"faceta_" + (h.get("origen") or [""])[0]: h.get("evidencia") or h.get("que")})   # N12
        out.append(f)
    orden_salida = sorted(out, key=lambda h: (not h["cuenta"], PRECEDENCIA.index(h["clase"])))
    for i, h in enumerate(orden_salida + resto, 1):
        h["id"] = "H%d" % i
    return orden_salida + resto


def _subs(hs):
    """Subtipos de un fallo silencioso (o de la parte de datos de ambos), ordenados."""
    return sorted({"guardado" if h["clase"] == "fidelidad" else
                   ("aceptacion_falsa" if h["subtipo"] == "aceptacion_falsa" else
                    ("inservible" if h["subtipo"] == "inservible" else "aceptado_imposible")) for h in hs})


def veredicto(hs, esp, obs, lec, ms, ampliado, escrito_alm=None):
    lect = {"categoria": "indeterminado", "subtipo": "lectura", "por": [h["id"] for h in hs if h["clase"] == "lectura"],
            "certeza": "lectura", "alternativa": None}
    if lec["contradictorio"]:                                     # [S12] §1.6.3: antes que sin_intercambio (N23)
        return lect
    if not esp or esp[0].get("sin_intercambio") or esp[0].get("debe_haber_ack") == "indeterminado":
        return {"categoria": "sin_intercambio", "subtipo": None, "por": [], "certeza": "literal", "alternativa": None}
    if lec["lectura_hallazgos"]:
        return {"categoria": "indeterminado", "subtipo": "lectura", "por": [h["id"] for h in hs if h["clase"] == "lectura"],
                "certeza": "lectura", "alternativa": None}
    por_msg = []
    for k, x in enumerate(esp):
        F = [h for h in hs if h["mensaje"] == k and h["cuenta"] and h["estado"] == "firme"]
        F_s43 = [h for h in F if (h.get("evidencia") or {}).get("alcance_s43")]          # [S43] no cambia la categoría
        F = [h for h in F if h not in F_s43]
        disp = [h for h in hs if h["mensaje"] == k and h["estado"] == "disputado"]
        o = obs[k] if k < len(obs) else None
        m1 = AR.equiv_msa1(o["msa1"]) if o else None
        escritura = (lec["por_mensaje"][k].get("destino") == "exito") or ampliado or bool((escrito_alm or {}).get(k))   # v1.1 §3.2
        clases = {h["clase"] for h in F}
        datos = [h for h in F if h["clase"] in CLASES_14]
        resto = [h for h in F if h["clase"] not in CLASES_14]
        if not F:
            cat, sub = "correcto", None
        elif clases == {"entorno"}:                                    # [S11] [S20] con cualquier MSA-1
            cat, sub = "fallo_entorno", "+".join(sorted({h["subtipo"] for h in F}))
        elif m1 == "AA":
            no_ent = [h for h in F if h["clase"] != "entorno"]
            ent = sorted({h["subtipo"] for h in F if h["clase"] == "entorno"})
            if ent and datos:                                            # [S23]
                cat, sub = "ambos", "+".join(_subs(datos) + ent)
            else:
                cat, sub = "fallo_silencioso", "+".join(_subs(no_ent) + ent)
        elif escritura and clases & CLASES_14 and clases & CLASES_57:
            cat, sub = "ambos", "+".join(_subs(datos) + sorted({h["subtipo"] for h in resto}))
        elif clases <= CLASES_57:
            cat, sub = "acuse_incorrecto", "+".join(sorted({h["subtipo"] for h in F}))
        else:
            cat, sub = "indeterminado", "defecto del verificador (caso residual §2.4)"
        if F_s43 and F:
            sub = "+".join(([sub] if sub else []) + sorted({"transformado" if h["clase"] == "fidelidad" else h["subtipo"]
                                                            for h in F_s43}))
        det = (F + F_s43) or disp
        cert = _debil([h["certeza"] for h in det]) if det else "literal"
        alt = next((h["alternativa"] for h in det if h["alternativa"] and h["certeza"] == cert), None)
        por_msg.append({"categoria": cat, "subtipo": sub, "por": [h["id"] for h in det], "certeza": cert, "alternativa": alt,
                        "mensaje": k})
    return min(por_msg, key=lambda v: GRAVEDAD.index(v["categoria"]))


# ---------------------------------------------------------------------------- ficha §2.5
def ficha(caso, r, e, pe=None):
    v = r["veredicto"]
    pe = PE.resolver(pe or r.get("punto_entrada"), e)
    ls = ["CASO %s" % caso] + (["PERFIL   %s" % AR.PERFILES[AR.PERFIL].get("linea_ficha", AR.PERFIL)] if AR.PERFIL != "lab" else []) + (
          ["PUNTO    %s (puerto %d)" % (pe["nombre"], pe["puerto"])] if pe["nombre"] != "adt_a01" else []) + [        # §1.3: solo si no es adt_a01
          "VEREDICTO PROPUESTO: %s%s  (certeza: %s%s)" % (v["categoria"], "/" + v["subtipo"] if v.get("subtipo") else "",
                                                           v["certeza"], "; alternativa: %s" % v["alternativa"] if v.get("alternativa") else ""),
          ""]
    ms = MR.mensajes(e.get("mensaje"))
    tr = MR.trama(e.get("mensaje"))                                                   # [S31] línea TRAMA
    if len(tr["marcos"]) > 1 or tr["anomalias"]:
        piezas = []
        for mc in tr["marcos"]:
            nombres = " ".join(AR._nombre_visible(s) for s in mc["segmentos"])
            piezas.append("[%d] %s" % (mc["n"], nombres if mc["msh"] else "sin MSH: %s (no es mensaje; L9/S31)" % nombres))
        ls.append("TRAMA    %d marco%s: %s%s" % (len(tr["marcos"]), "" if len(tr["marcos"]) == 1 else "s", "  ".join(piezas),
                                                  " | anomalías: " + "; ".join(tr["anomalias"]) if tr["anomalias"] else ""))
    for m in ms:
        msh, pid = m.segs[0], (m.segmentos("PID") or [""])[0]
        ls.append("MENSAJE  MSH-9=%s  MSH-10=%s  MSH-11/12=%s/%s  MSH-15/16=%s/%s  MSH-18=%s" % (           # [S39]
            m.campo(msh, 9), m.campo(msh, 10), m.campo(msh, 11), m.campo(msh, 12), m.campo(msh, 15), m.campo(msh, 16),
            m.campo(msh, 18)))
        ls.append("SEGMENTOS  " + AR.resumen_segmentos(m, pe))
        if pid:
            ls.append("         PID-3=%s  PID-5=%s  PID-7=%s  PID-8=%s" % (m.campo(pid, 3)[:60], m.campo(pid, 5)[:60],
                                                                          m.campo(pid, 7), m.campo(pid, 8)))
    for o in r["observado"]:
        ls.append("ACK      %s" % ("ausente" if o is None else "MSA-1=%s MSA-2=%s ERR=%s MSH-9=%s" % (o.get("msa1"), (o.get("msa2") or "")[:25], o.get("err"), o.get("msh9"))))
    for s in e.get("sesiones") or []:
        if isinstance(s.get("canonico"), dict):
            ls.append("CANÓNICO " + ", ".join("%s=%s" % (k, v2) for k, v2 in s["canonico"].items()))
        if isinstance(s.get("canonico_oru"), dict):                                     # diseno-oru-fable.md §5.5
            co = s["canonico_oru"]
            ls.append("CANÓNICO " + ", ".join("%s=%s" % (k, v2) for k, v2 in (co.get("cabecera") or {}).items()))
            for inf in co.get("informes") or []:
                ls.append("  OBR %s  Codigo=%s Estado=%s Efectivo=%s Emitido=%s NumObx=%s" % (inf.get("Orden"), inf.get("CodigoCode"),
                          inf.get("Estado"), inf.get("Efectivo"), inf.get("Emitido"), inf.get("NumObx")))
            for ob in co.get("observaciones") or []:
                val = next((str(ob.get(c_)) for c_ in ("ValorNumero", "ValorTexto", "ValorCodigo", "ValorFecha", "ValorCrudo") if ob.get(c_) not in (None, "")), "")
                ls.append("  OBX %s (%s)  %s Codigo=%s Valor=%s Unidad=%s Estado=%s Fecha=%s" % (ob.get("Orden"), ob.get("Informe"), ob.get("Tipo") or "",
                          ob.get("CodigoCode"), val[:40], ob.get("UnidadTexto") or "", ob.get("Estado"), ob.get("Fecha")))
        if isinstance(s.get("canonico_adt"), dict):                                     # diseno-adt-fable.md §7.4
            ca = s["canonico_adt"].get("cabecera") or {}
            ls.append("CANÓNICO paciente " + ", ".join("%s=%s" % (k, ca.get(k)) for k in ("Identifier", "FamilyName", "GivenName", "Gender", "BirthDate")))
            ls.append("         visita   " + ", ".join("%s=%s" % (k, ca.get(k)) for k in ("TieneVisita", "VisitaId", "ClaseCode", "Estado", "Inicio", "Fin", "Ubicacion")))
            ls.append("         recuentos " + ", ".join("%s=%s" % (k, ca.get(k)) for k in ("NumNombres", "NumDirecciones", "NumTelecoms", "NumParticipantes", "Truncado")))
    if pe.get("mapeador") == "adt":                                                      # §7.4: línea ALMACÉN en adt_fhir
        alm = r.get("almacen") or {}
        if not alm:
            ls.append("ALMACÉN  no leído (sin almacen_adt)")
        for k in sorted(alm, key=str):
            pp = (" por paciente nuevos=%s previos=%s" % (alm[k]["EncounterPaciente"], alm[k]["previos"])) if "EncounterPaciente" in alm[k] else ""
            ls.append("ALMACÉN  leído tras ACK: Patient n=%s Encounter n=%s%s; fallos %d" % (alm[k]["Patient"], alm[k]["Encounter"], pp, alm[k]["fallos"]))
    if pe.get("mapeador") == "oru":                                                      # v1.1 §4.1: línea ALMACÉN solo en oru_fhir [S70]
        alm = r.get("almacen") or {}
        if not alm:
            ls.append("ALMACÉN  no leído (L-ORU-1)")
        for k in sorted(alm, key=str):
            z = alm[k]
            ls.append("ALMACÉN  leído tras ACK: Observation n=%s DiagnosticReport n=%s; fallos %d" % (z["Observation"], z["DiagnosticReport"], z["fallos"]))
    for z in r["lectura"]["resultado_destino"]:
        ls.append("DESTINO  %s%s" % (z["destino"], " HTTP %s %s" % (z["http"], z.get("code") or "") if z.get("http") else ""))
    for s in e.get("sesiones") or []:
        for f in s.get("log") or []:
            ls.append("  log    %s | %s" % (f.get("tipo"), (f.get("texto") or "")[:140]))
    for z in (e.get("entorno") or []) + (e.get("conexion") or []):
        ls.append("  ent/cx %s" % z)
    notas = []
    for z in r["lectura"].get("arnes_inexacto", []) + [n for d in r["lectura"]["resultado_destino"] for n in d.get("notas", [])]:
        if z not in notas:
            notas.append(z)
    if notas:
        ls.append("NOTAS    " + " | ".join(notas))
    ls.append("")
    for h in r["hallazgos"]:
        if h["clase"] in ("tolerancia", "nota") or not h["cuenta"] and h["estado"] != "disputado":
            continue
        ls.append("[%s] %s/%s  hecho=%s  certeza=%s  origen=%s%s%s" % (h["id"], h["clase"], h["subtipo"], h["hecho"], h["certeza"],
                  "+".join(h["origen"]), "  causa=%s" % h["causa"] if h["causa"] else "",
                  "  (DISPUTADO)" if h["estado"] == "disputado" else ""))
        for q in h["que"]:
            ls.append("      - %s" % q)
        if h["opinion_circuito"]:
            ls.append("      el circuito dijo: %s" % h["opinion_circuito"][:150])
        if (h.get("evidencia") or {}).get("entorno"):
            ls.append("      el entorno dijo: %s" % h["evidencia"]["entorno"][:150])
        ls.append("      ¿Confirmas? sí / no: no es fallo / no: otra clase / no: otra localización / no sé (O0)")
    menores = [h for h in r["hallazgos"] if not h["cuenta"] and h["estado"] != "disputado"]
    if menores:
        ls.append("menores, tolerancias y notas: " + "; ".join("%s %s" % (h["clase"], (h["que"][0] if h.get("que") else "")[:60]) for h in menores))
    if r["lectura"]["vocabulario_nuevo"]:
        ls.append("VOCABULARIO NUEVO (¿qué clase?): " + " | ".join(r["lectura"]["vocabulario_nuevo"]))
    ls.append("VEREDICTO FINAL: confirmar / elegir otra categoría; localización confirmada: ______")
    return "\n".join(ls)
