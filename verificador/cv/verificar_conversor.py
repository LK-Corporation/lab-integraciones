#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 18 (cv/vc/diseno-vc-fable.md; decisiones de Jev en cv/vc/decision-jev-qvc.md): verifica tu conversor HL7 v2 -> FHIR R4
con un fichero de adaptador y una orden, sin escribir código.

  python3 cv/verificar_conversor.py <adaptador.json> <carpeta de salida> [opciones]       # desde verificador/

Lee el adaptador (JSON declarativo, S-VC-2), corre el conversor en la caja de siempre (Docker sin red, solo lectura, usuario sin
privilegios ni capacidades; S-VC-3), escribe una evidencia por mensaje con la forma que lee el juez (S-CV-2), la juzga con
verificador.verificar sin tocarlo, agrega por las ocho clases de S-CV-5 y escribe INFORME.md e INFORME.json. El informe dice lo
que ve el juez y lo que la herramienta no puede saber: si el proyecto del conversor ya tenía declarada cada discrepancia
(L-VC-1). Solo biblioteca estándar; no descarga nada (S-VC-19).

Códigos de salida (S-VC-15): 0 todo juzgado; 1 error interno; 2 adaptador inválido; 3 caja no disponible; 4 la caja falló en
alguna corrida (hay informe, con lo no juzgado); 5 --comparar encontró diferencias."""
import argparse
import collections
import datetime
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(AQUI)
sys.path[:0] = [AQUI, FASE]
_argv, sys.argv = sys.argv, ["x", "--silencio"]
import bases_oru as BO  # noqa: E402
import bases_vxu as BV  # noqa: E402
import conversion as CV  # noqa: E402
import cv3_mecanismos as MEC  # noqa: E402
import cv3_minimos as MIN  # noqa: E402
import mcp_verificador as M  # noqa: E402
import puntos_entrada as PE  # noqa: E402
import verificador as V  # noqa: E402
sys.argv = _argv

VERSION = "1.0"
FORMATO = "adaptador-vc/1"
JUGUETE = os.path.join(AQUI, "conversor_juguete.py")
ESTUDIO = ("microsoft", "linuxforhealth")                       # Q-VC-D-3 (Jev: solo_estudio): los 68 mínimos, solo con estos
CAJA = ["--rm", "--network", "none", "--read-only", "--tmpfs", "/tmp", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
        "--user", "65534:65534", "-e", "HOME=/tmp"]                # la de cv/correr_conversor.py (E-CV-3); no es configurable
CORPUS = ("adt", "oru", "vxu", "muestras", "minimos", "propio")
MARCADORES = ("entrada_dir", "salida_dir", "entrada_fichero", "salida_fichero", "salida_error", "nombre", "base", "plantilla")
SOLO_LOTE = ("entrada_dir", "salida_dir")
CLASES8 = ("valor_distinto", "dato_perdido", "dato_inventado", "codigo_mal_mapeado", "valor_imposible_convertido", "recurso",
           "referencia_rota", "fhir_invalido")
MAX_BUNDLE = 4000000                                              # DV-CV-5
IMAGEN_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*(:[0-9]+)?(/[a-z0-9][a-z0-9._-]*)*(:[A-Za-z0-9_][A-Za-z0-9_.-]{0,127})?"
                       r"(@sha256:[0-9a-f]{64})?$")                  # la gramática de referencia de Docker, sin mayúsculas
LIMITES = {"segundos_por_mensaje": 60, "segundos_por_contenedor": 3600, "pids": 1024, "memoria_mb": None}
CORRIDA_VARIABLE = ("fecha", "duraciones", "rutas", "reintentos_s")
FRASE_FIJA = ("Este informe dice qué hallazgos ve el juez y con qué cita. **No dice si el proyecto del conversor ya los tiene "
              "declarados** (salidas esperadas, pruebas, documentación o issues): ese contraste lo hace una persona, como en "
              "`cv/RESULTADO-CV3.md`, y hasta entonces ningún mecanismo de aquí es «nuevo» ni «confirmado». De las cuatro "
              "condiciones del estudio, la herramienta comprueba tres (cita, clase, par mínimo) y deja la cuarta sin hacer.")
L_VC = {
    "L-VC-1": "La herramienta no sabe si una discrepancia la tiene declarada el proyecto: no lee salidas esperadas, pruebas, "
              "documentación ni issues. Aquí todo es «sin_contraste».",
    "L-VC-2": "Solo juzga lo que juzgan adt_conv, oru_conv y vxu_conv: ADT de los ocho eventos, ORU^R01 y VXU^V04. Otro tipo de "
              "mensaje entra en el corpus y el juez lo aparta como fuera de alcance.",
    "L-VC-3": "Solo conversores que corran como programa de línea de órdenes dentro de un contenedor Docker, leyendo y escribiendo "
              "ficheros. Un servicio HTTP, una biblioteca o un conversor que necesite red no caben en el adaptador.",
    "L-VC-4": "La imagen debe estar ya en la máquina: la herramienta no descarga nada y no comprueba de dónde salió; registra su "
              "digest.",
    "L-VC-5": "La huella del conversor con la fórmula del estudio no ve nombres ni rutas: renombrar ficheros no la cambia. Por eso "
              "va también la huella con nombres (Q-VC-D-1).",
    "L-VC-6": "«vacio» y «sin_respuesta» no distinguen la caja del conversor (L-CV-8). Tras un tiempo vencido, los mensajes sin "
              "salida se reintentan una vez, uno a uno (Q-VC-D-9).",
    "L-VC-7": "Las muestras de los proyectos no viajan con el repositorio: sin --muestras, el corpus son las bases A1/E2, las ORU "
              "y, con los dos conversores del estudio, los 68 mínimos; todo sintético y en v2.5.",
    "L-VC-8": "El control caso por caso exige el detalle del estudio, que no es público; desde la copia pública se comprueban las "
              "identidades, los agregados por categoría y los pares mínimos.",
    "L-VC-9": "Las restricciones de la caja se comprueban en la orden construida, no en el núcleo: un Docker sin raíz, con "
              "--userns-remap o con otro runtime puede comportarse distinto.",
    "L-VC-10": "duracion_ms es aproximado cuando varios mensajes comparten contenedor; la herramienta no mide rendimiento.",
    "L-VC-11": "No se comprueba que el conversor sea determinista; una corrida es una corrida.",
    "L-VC-12": "Un Bundle de más de 4.000.000 de caracteres no se juzga (error demasiado_grande, DV-CV-5).",
    "L-VC-13": "Un mensaje sin plantilla disponible (comprobar_fichero) se marca error sin_plantilla sin entrar en la caja.",
    "L-VC-14": "La herramienta hereda las decisiones, límites y ambigüedades del juez (Q-CV-D-n, L-CV-n, AMB-CV-n); no los cambia.",
    "L-VC-15": "Los 68 mínimos son sondas escritas para dos conversores concretos: que se reproduzca uno no dice que sea una "
               "discrepancia del conversor contrastada con su proyecto.",
}


class ErrorAdaptador(Exception):
    def __init__(self, codigo, campo, texto):
        Exception.__init__(self, "%s: %s" % (campo, texto))
        self.codigo, self.campo, self.texto = codigo, campo, texto


class CajaNoDisponible(Exception):
    pass


# ---------------------------------------------------------------------------- el adaptador (§2.1)
CLAVES = {"": {"formato", "id", "conversor", "caja", "invocacion", "salida"},
          "conversor": {"nombre", "version", "huella", "declara"}, "conversor.huella": {"partes"},
          "conversor.declara": {"no_soporta"},
          "caja": {"tipo", "imagen", "imagen_digest", "montajes", "entorno", "limites"},
          "caja.limites": set(LIMITES),
          "invocacion": {"modo", "contenedor", "orden", "plantilla", "duracion_stdout"},
          "invocacion.plantilla": {"regla", "valor", "comprobar_fichero"},
          "invocacion.plantilla.comprobar_fichero": {"montaje", "patron"},
          "salida": {"fichero", "fichero_error", "forma", "envoltura", "codificacion"},
          "salida.envoltura": {"ruta_bundle", "ruta_estado", "estado_ok"}}


def _limpiar(x):
    """S-VC-21: las claves que empiezan por «_» son comentarios."""
    if isinstance(x, dict):
        return {k: _limpiar(v) for k, v in x.items() if not (isinstance(k, str) and k.startswith("_"))}
    if isinstance(x, list):
        return [_limpiar(v) for v in x]
    return x


def _mal(codigo, campo, texto):
    raise ErrorAdaptador(codigo, campo, texto)


def _dict(d, campo, obligatorio=True):
    v = d
    for k in campo.split(".") if campo else []:
        v = v.get(k) if isinstance(v, dict) else None
    if v is None and not obligatorio:
        return {}
    if not isinstance(v, dict):
        _mal("campo_obligatorio" if v is None else "tipo_invalido", campo, "debe ser un objeto")
    extra = sorted(set(v) - CLAVES[campo])
    if extra:
        _mal("clave_desconocida", ("%s.%s" % (campo, extra[0])).lstrip("."), "clave no admitida")
    return v


def _texto(v, campo, maximo, obligatorio=True):
    if v is None and not obligatorio:
        return None
    if not isinstance(v, str) or not v:
        _mal("campo_obligatorio" if v is None else "tipo_invalido", campo, "debe ser un texto no vacío")
    if len(v) > maximo:
        _mal("tamano_excedido", campo, "más de %d caracteres" % maximo)
    return v


def _relativa(ruta, campo):
    if not isinstance(ruta, str) or not ruta or os.path.isabs(ruta) or ruta.startswith(("/", "\\")) or ".." in re.split(r"[\\/]", ruta):
        _mal("ruta_no_relativa", campo, "debe ser una ruta relativa a --artefactos, sin «..» (S-VC-18)")
    return ruta


def _marcadores(texto):
    return re.findall(r"\{([^{}]*)\}", texto)


def leer_adaptador(fuente, artefactos=None):
    """-> el adaptador validado y normalizado (sin claves «_», con los valores por omisión), o ErrorAdaptador."""
    if isinstance(fuente, dict):
        d = fuente
    else:
        try:
            d = json.loads(open(fuente, encoding="utf-8").read())
        except (OSError, ValueError) as ex:
            _mal("json_invalido", "", "no se lee como JSON (%s)" % str(ex)[:120])
        if artefactos is None:
            artefactos = os.environ.get("VC_ARTEFACTOS") or os.path.dirname(os.path.abspath(fuente))
    return validar_adaptador(_limpiar(d), artefactos or os.getcwd())


def validar_adaptador(d, artefactos):
    if not isinstance(d, dict):
        _mal("tipo_invalido", "", "el adaptador debe ser un objeto JSON")
    _dict(d, "")
    if d.get("formato") != FORMATO:
        _mal("formato", "formato", "debe ser %r" % FORMATO)
    if not isinstance(d.get("id"), str) or not re.match(r"^[a-z0-9-]{1,32}$", d["id"]):
        _mal("id", "id", "minúsculas, cifras y guiones, de 1 a 32")
    cv = _dict(d, "conversor")
    _texto(cv.get("nombre"), "conversor.nombre", 128)
    _texto(cv.get("version"), "conversor.version", 64)
    hu = _dict(d, "conversor.huella")
    decl = _dict(d, "conversor.declara", obligatorio=False)
    ns = decl.get("no_soporta", [])
    if not isinstance(ns, list) or not all(isinstance(x, str) and re.match(r"^[A-Z0-9]{3}\^[A-Z0-9]{2,3}$", x) for x in ns):
        _mal("declara", "conversor.declara.no_soporta", "lista de «TIPO^EVENTO» (Q-VC-D-8)")
    caja = _dict(d, "caja")
    tipo = caja.get("tipo")
    if tipo not in ("docker", "proceso_local"):
        _mal("caja_tipo", "caja.tipo", "docker o proceso_local")
    if tipo == "docker":
        _texto(caja.get("imagen"), "caja.imagen", 256) if caja.get("imagen") is not None else \
            _mal("imagen_obligatoria", "caja.imagen", "con docker hace falta la imagen (repositorio:etiqueta)")
        if not IMAGEN_RE.match(caja["imagen"]):                       # una «imagen» que empiece por «-» sería una bandera
            _mal("imagen_formato", "caja.imagen", "una referencia de imagen de Docker (repositorio[:etiqueta][@sha256:…])")
    dg = caja.get("imagen_digest")
    if dg is not None and not (isinstance(dg, str) and re.match(r"^sha256:[0-9a-f]{64}$", dg)):
        _mal("imagen_digest", "caja.imagen_digest", "null o «sha256:<64 hex>»")
    montajes = caja.get("montajes") or {}
    if not isinstance(montajes, dict):
        _mal("tipo_invalido", "caja.montajes", "debe ser un objeto")
    destinos = set()
    for nombre, m in montajes.items():
        campo = "caja.montajes.%s" % nombre
        if not re.match(r"^[a-z0-9_-]{1,32}$", nombre):
            _mal("montaje_nombre", campo, "minúsculas, cifras, «_» y «-»")
        if not isinstance(m, dict):
            _mal("tipo_invalido", campo, "debe ser un objeto {origen, destino}")
        extra = sorted(set(m) - {"origen", "destino"})
        if extra:
            _mal("clave_desconocida", "%s.%s" % (campo, extra[0]), "clave no admitida (los montajes son siempre de solo lectura)")
        de = m.get("destino")
        if not isinstance(de, str) or not de.startswith("/") or de.rstrip("/") in ("", "/in", "/salida", "/tmp", "/proc") or de in destinos:
            _mal("montaje_destino", campo + ".destino", "absoluto, distinto de /, /in, /salida, /tmp y /proc, y sin repetirse")
        destinos.add(de)
        o = _relativa(m.get("origen"), campo + ".origen")
        if not os.path.isdir(os.path.join(artefactos, o)):
            _mal("montaje_inexistente", campo + ".origen", "%r no es una carpeta bajo --artefactos" % o)
    entorno = caja.get("entorno") or {}
    if not isinstance(entorno, dict):
        _mal("tipo_invalido", "caja.entorno", "debe ser un objeto")
    for k, v in entorno.items():
        if k in ("HOME", "PATH", "LD_PRELOAD"):
            _mal("entorno_reservado", "caja.entorno.%s" % k, "lo pone la herramienta o no se admite")
        if not re.match(r"^[A-Z_][A-Z0-9_]*$", k):
            _mal("entorno_nombre", "caja.entorno.%s" % k, "mayúsculas, cifras y «_»")
        _texto(v, "caja.entorno.%s" % k, 256)
    lim = dict(LIMITES)
    lim.update(_dict(d, "caja.limites", obligatorio=False))
    for k in ("segundos_por_mensaje", "segundos_por_contenedor", "pids"):
        if not isinstance(lim[k], int) or isinstance(lim[k], bool):
            _mal("limite_fuera_de_rango", "caja.limites.%s" % k, "debe ser un entero")
    m_mb = lim["memoria_mb"]
    if not (1 <= lim["segundos_por_mensaje"] <= 600 and lim["segundos_por_mensaje"] <= lim["segundos_por_contenedor"] <= 7200
            and 16 <= lim["pids"] <= 4096 and (m_mb is None or (isinstance(m_mb, int) and m_mb >= 256))):
        _mal("limite_fuera_de_rango", "caja.limites", "1 ≤ s/mensaje ≤ 600, s/mensaje ≤ s/contenedor ≤ 7200, 16 ≤ pids ≤ 4096, "
             "memoria_mb null o ≥ 256")
    inv = _dict(d, "invocacion")
    modo = inv.get("modo")
    if modo not in ("lote", "mensaje"):
        _mal("modo", "invocacion.modo", "lote o mensaje")
    orden = inv.get("orden")
    if not isinstance(orden, list) or not orden or not all(isinstance(x, str) and x for x in orden):
        _mal("orden", "invocacion.orden", "lista de argumentos no vacíos (sin shell)")
    usados = [k for x in orden for k in _marcadores(x)]
    for k in usados:
        if k not in MARCADORES:
            _mal("marcador_desconocido", "invocacion.orden", "marcador {%s} desconocido" % k)
    sal = _dict(d, "salida")
    fich = _texto(sal.get("fichero"), "salida.fichero", 128)
    ferr = _texto(sal.get("fichero_error"), "salida.fichero_error", 128, obligatorio=False)
    for campo, p in (("salida.fichero", fich), ("salida.fichero_error", ferr)):
        if p is not None and (not re.match(r"^[A-Za-z0-9._{}-]+$", p) or any(k not in ("base", "nombre") for k in _marcadores(p))):
            _mal("salida_fichero", campo, "nombre de fichero con {base} o {nombre}, sin rutas")
    contenedor = inv.get("contenedor")
    if modo == "lote":
        if any(k not in SOLO_LOTE for k in usados) or not any(k in ("base", "nombre") for k in _marcadores(fich)):
            _mal("lote_marcador", "invocacion.orden", "en lote solo {entrada_dir} y {salida_dir}, y salida.fichero con {base} o {nombre}")
        contenedor = None
    else:
        if contenedor not in ("por_mensaje", "por_grupo"):
            _mal("mensaje_sin_contenedor", "invocacion.contenedor", "por_mensaje o por_grupo")
        if "entrada_fichero" not in usados:
            _mal("mensaje_sin_fichero", "invocacion.orden", "en modo mensaje la orden lleva {entrada_fichero}")
    pl = inv.get("plantilla")
    if pl is not None:
        pl = _dict(d, "invocacion.plantilla")
        if pl.get("regla") not in ("msh9_tipo_evento", "msh9_tipo", "fija"):
            _mal("plantilla_regla", "invocacion.plantilla.regla", "msh9_tipo_evento, msh9_tipo o fija")
        if pl["regla"] == "fija":
            _texto(pl.get("valor"), "invocacion.plantilla.valor", 128)
        cf = pl.get("comprobar_fichero")
        if cf is not None:
            cf = _dict(d, "invocacion.plantilla.comprobar_fichero")
            if cf.get("montaje") not in montajes or "{plantilla}" not in str(cf.get("patron") or ""):
                _mal("plantilla_comprobar", "invocacion.plantilla.comprobar_fichero", "un montaje del adaptador y un patrón con {plantilla}")
        pl = {"regla": pl["regla"], "valor": pl.get("valor"), "comprobar_fichero": cf}
    if "plantilla" in usados and pl is None:
        _mal("plantilla_sin_regla", "invocacion.plantilla", "{plantilla} en la orden exige la regla")
    ds = inv.get("duracion_stdout")
    if ds is not None:
        try:
            g = re.compile(ds).groupindex
        except (re.error, TypeError):
            g = {}
        if "nombre" not in g or "ms" not in g:
            _mal("duracion_stdout", "invocacion.duracion_stdout", "expresión regular con los grupos (?P<nombre>…) y (?P<ms>…)")
    forma = sal.get("forma")
    if forma not in ("bundle", "envuelto"):
        _mal("forma", "salida.forma", "bundle o envuelto")
    env = None
    if forma == "envuelto":
        env = _dict(d, "salida.envoltura", obligatorio=False)
        rb = env.get("ruta_bundle")
        if not isinstance(rb, list) or not rb or not all(isinstance(x, str) for x in rb):
            _mal("envoltura_sin_ruta", "salida.envoltura.ruta_bundle", "lista de claves no vacía")
        re_ = env.get("ruta_estado")
        if re_ is not None and (not isinstance(re_, list) or not all(isinstance(x, str) for x in re_)):
            _mal("tipo_invalido", "salida.envoltura.ruta_estado", "lista de claves o null")
        env = {"ruta_bundle": rb, "ruta_estado": re_, "estado_ok": env.get("estado_ok")}
    cod = sal.get("codificacion") or "utf-8"
    if cod not in ("utf-8", "utf-8-sig"):
        _mal("codificacion", "salida.codificacion", "utf-8 o utf-8-sig")
    if tipo == "proceso_local":
        if not str(cv["nombre"]).startswith("juguete-") or len(orden) < 2 or orden[0] != "python3" or \
                os.path.realpath(os.path.join(artefactos, orden[1])) != os.path.realpath(JUGUETE):
            _mal("proceso_local_solo_juguete", "caja.tipo", "proceso_local solo corre el conversor de juguete del laboratorio (S-VC-4)")
    partes = hu.get("partes")
    if not isinstance(partes, list) or not partes:
        _mal("huella_parte", "conversor.huella.partes", "lista no vacía de {carpeta} o {fichero}")
    ad = {"formato": FORMATO, "id": d["id"],
          "conversor": {"nombre": cv["nombre"], "version": cv["version"], "huella": {"partes": partes}, "declara": {"no_soporta": ns}},
          "caja": {"tipo": tipo, "imagen": caja.get("imagen"), "imagen_digest": dg, "montajes": montajes, "entorno": entorno,
                   "limites": lim},
          "invocacion": {"modo": modo, "contenedor": contenedor, "orden": orden, "plantilla": pl, "duracion_stdout": ds},
          "salida": {"fichero": fich, "fichero_error": ferr, "forma": forma, "envoltura": env, "codificacion": cod}}
    for i, p in enumerate(partes):
        _parte(ad, artefactos, p, "conversor.huella.partes[%d]" % i)
    return ad


# ---------------------------------------------------------------------------- la huella (§2.2, Q-VC-D-1: las dos)
def _parte(ad, artefactos, p, campo="conversor.huella.partes"):
    if not isinstance(p, dict) or len(p) != 1 or list(p)[0] not in ("carpeta", "fichero"):
        _mal("huella_parte", campo, "{carpeta: <montaje o ruta>} o {fichero: <ruta>}")
    k, v = list(p.items())[0]
    m = (ad.get("caja", {}).get("montajes") or {}).get(v) if k == "carpeta" else None
    ruta = os.path.join(artefactos, m["origen"] if m else _relativa(v, campo))
    if not (os.path.isdir(ruta) if k == "carpeta" else os.path.isfile(ruta)):
        _mal("huella_parte", campo, "%r no existe" % v)
    return k, ruta


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _huella_carpeta(d):
    """La de cv/correr_conversor.py: el contenido de cada fichero en orden de os.walk, sin nombres."""
    h = hashlib.sha256()
    for raiz, _, fs in sorted(os.walk(d)):
        for f in sorted(fs):
            h.update(_sha(open(os.path.join(raiz, f), "rb").read()).encode())
    return h.hexdigest()


def huella(ad, artefactos):
    return _sha("".join(_huella_carpeta(r) if k == "carpeta" else _sha(open(r, "rb").read())
                        for k, r in (_parte(ad, artefactos, p) for p in ad["conversor"]["huella"]["partes"])).encode())


def huella_con_nombres(ad, artefactos):
    """Además, la ruta relativa de cada fichero dentro de su parte (Q-VC-D-1, L-VC-5)."""
    h = hashlib.sha256()
    for p in ad["conversor"]["huella"]["partes"]:
        k, r = _parte(ad, artefactos, p)
        h.update(("%s:%s\n" % (k, list(p.values())[0])).encode())
        if k == "fichero":
            h.update(("%s\n" % _sha(open(r, "rb").read())).encode())
            continue
        for raiz, _, fs in sorted(os.walk(r)):
            for f in sorted(fs):
                rel = os.path.relpath(os.path.join(raiz, f), r).replace(os.sep, "/")
                h.update(("%s %s\n" % (rel, _sha(open(os.path.join(raiz, f), "rb").read()))).encode())
    return h.hexdigest()


# ---------------------------------------------------------------------------- el mensaje y la plantilla
def normal(t):
    """DV-CV-10: CR como separador de segmento y sin BOM."""
    return re.sub(r"\r\n|\n|\r", "\r", t.lstrip("\ufeff").strip()) + "\r"


def _msh9_partes(t):
    msh = t.lstrip("\ufeff").replace("\r\n", "\r").replace("\n", "\r").split("\r")[0]
    if not msh.startswith("MSH") or len(msh) < 5:
        return None
    p = msh.split(msh[3])
    comp = p[1][0] if len(p) > 1 and p[1] else "^"
    return (p[8] if len(p) > 8 else "").split(comp)


def msh9(t):
    """MSH-9 tal cual (con los separadores del mensaje, DV-CV-12), o None si no hay MSH."""
    c = _msh9_partes(t)
    return None if c is None else "^".join(c)


def punto(t):
    """S-VC-22 y S-VX-13: solo por MSH-9.1; ORU -> oru_conv, VXU -> vxu_conv, lo demás -> adt_conv."""
    c = _msh9_partes(t)
    if c is None:
        return None
    return "oru_conv" if c[0].upper().startswith("ORU") else "vxu_conv" if c[0].upper().startswith("VXU") else "adt_conv"


def plantilla(t, regla):
    """S-VC-7: como cv/correr_conversor.plantilla para msh9_tipo_evento."""
    if not regla:
        return None
    if regla["regla"] == "fija":
        return regla["valor"]
    c = _msh9_partes(t) or [""]
    if regla["regla"] == "msh9_tipo":
        return c[0].upper()
    return ("%s_%s" % (c[0], c[1]) if len(c) > 1 else c[0]).upper()


# ---------------------------------------------------------------------------- el corpus (§3 paso 4)
def generar_corpus(carpeta, lab=True, minimos=True, propios=(), muestras=None, limite=None):
    textos = collections.OrderedDict((c, []) for c in CORPUS)
    if lab:
        adt = json.load(open(os.path.join(FASE, "bases_adt", "bases_e2.json"), encoding="utf-8")) + \
            json.load(open(os.path.join(FASE, "a1", "ejemplos_cap3.json"), encoding="utf-8")) + \
            json.load(open(os.path.join(FASE, "a1", "bases_a1.json"), encoding="utf-8"))
        textos["adt"] = [(x["id"] + ".hl7", normal(x["mensaje"])) for x in adt]
        textos["oru"] = [("ORU-%s.hl7" % b["id"], normal(BO.cable(b))) for b in BO.BASES]
        textos["vxu"] = [("VXU-%s.hl7" % b["id"], normal(BV.cable(b))) for b in BV.BASES]     # etapa 20 (S-VX-13)
    if muestras:
        for c in ("ms", "lfh"):
            d = os.path.join(muestras, c)
            for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
                t = open(os.path.join(d, f), encoding="utf-8-sig", errors="replace").read()
                textos["muestras"].append(("%s-%s.hl7" % (c, os.path.splitext(f)[0]), normal(t)))
    if minimos:
        for pid, _, (caso, control), _ in MIN.PARES:                    # como cv3_minimos.escribir, byte a byte
            textos["minimos"] += [("%s-caso.hl7" % pid, caso + "\r"), ("%s-control.hl7" % pid, control + "\r")]
    for d in propios or ():
        for f in sorted(os.listdir(d)):
            if f.endswith(".hl7"):
                textos["propio"].append((f, normal(open(os.path.join(d, f), "rb").read().decode("utf-8", errors="replace"))))
    if os.path.exists(carpeta):
        shutil.rmtree(carpeta)
    casos, sin_msh, man, global_, por, cv2 = [], [], [], hashlib.sha256(), {}, hashlib.sha256()
    n = {}
    for c, fs in textos.items():
        fs = sorted(fs)[:limite] if limite else sorted(fs)
        n[c] = len(fs)
        hc = hashlib.sha256()
        if fs:
            os.makedirs(os.path.join(carpeta, c))
        for f, t in fs:
            with open(os.path.join(carpeta, c, f), "w", encoding="utf-8", newline="") as g:
                g.write(t)
            s = _sha(t.encode("utf-8"))
            man.append("%s  %s/%s" % (s, c, f))
            global_.update(s.encode())
            hc.update(s.encode())
            if c in ("adt", "oru", "muestras"):
                cv2.update(s.encode())
            pe = punto(t)
            if pe is None:
                sin_msh.append("%s/%s" % (c, f))
            else:
                casos.append({"corpus": c, "caso": os.path.splitext(f)[0], "fichero": "%s/%s" % (c, f), "punto": pe, "msh9": msh9(t)})
        if fs:
            por[c] = hc.hexdigest()
    os.makedirs(carpeta, exist_ok=True)
    open(os.path.join(carpeta, "MANIFIESTO.txt"), "w", encoding="utf-8").write("\n".join(man) + ("\n" if man else ""))
    co = {"casos": casos, "sin_msh": sin_msh, "n": n, "huella": global_.hexdigest(), "por_corpus": por,
          "huella_adt_oru_muestras": cv2.hexdigest()}
    json.dump(co, open(os.path.join(carpeta, "CASOS.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return co


# ---------------------------------------------------------------------------- la caja (§2.3-2.5)
class Ejecutor:
    """Corre órdenes. `consultar` para las preguntas a Docker; `correr` para el conversor, con tiempo y, al vencer, docker kill
    del contenedor por su nombre (S-VC-20). Las pruebas lo sustituyen por un espía."""
    matar = True

    def consultar(self, orden):
        if shutil.which(orden[0]) is None:
            return 127, ""
        try:
            r = subprocess.run(orden, capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as ex:
            return 127, str(ex)
        return r.returncode, r.stdout + r.stderr

    def _run(self, orden, timeout):
        try:
            r = subprocess.run(orden, capture_output=True, text=True, timeout=timeout, errors="replace")
        except FileNotFoundError as ex:
            raise CajaNoDisponible("no se encuentra %s (%s)" % (orden[0], ex))
        return r.returncode, (r.stdout or "") + (r.stderr or "")

    def correr(self, orden, timeout, nombre=None):
        """-> (rc o None, salida, vencido)."""
        try:
            rc, out = self._run(orden, timeout)
            return rc, out, False
        except subprocess.TimeoutExpired as ex:
            if nombre and self.matar:
                self.consultar(orden_matar(nombre))
            out = ex.output or b""
            out = out.decode("utf-8", "replace") if isinstance(out, bytes) else out
            return None, out, True


def orden_matar(nombre):
    return ["docker", "kill", nombre]


def _rellena(patron, f):
    return patron.replace("{base}", os.path.splitext(f)[0]).replace("{nombre}", f)


def _sustituir(arg, valores):
    return re.sub(r"\{([a-z_]+)\}", lambda m_: valores[m_.group(1)], arg)


def _valores(ad, pl, f, din="/in", dsal="/salida"):
    s = ad["salida"]
    v = {"entrada_dir": din, "salida_dir": dsal, "plantilla": pl or ""}
    if f is not None:
        v.update({"entrada_fichero": "%s/%s" % (din, f) if din == "/in" else os.path.join(din, f),
                  "salida_fichero": "%s/%s" % (dsal, _rellena(s["fichero"], f)) if dsal == "/salida" else os.path.join(dsal, _rellena(s["fichero"], f)),
                  "salida_error": ("%s/%s" % (dsal, _rellena(s["fichero_error"], f)) if dsal == "/salida" else os.path.join(dsal, _rellena(s["fichero_error"], f)))
                  if s["fichero_error"] else "",
                  "nombre": f, "base": os.path.splitext(f)[0]})
    return v


def _palabra_sh(arg, pl, ad):
    """Un argumento como palabra de sh dentro del bucle (S-VC-6): lo literal con shlex.quote; lo de cada fichero, entre comillas
    dobles con $f / $b; nunca se interpreta el contenido del mensaje."""
    s = ad["salida"]
    din = {"entrada_fichero": "$f", "nombre": "$b.hl7", "base": "$b",
           "salida_fichero": "/salida/" + s["fichero"].replace("{base}", "$b").replace("{nombre}", "$b.hl7"),
           "salida_error": "/salida/" + (s["fichero_error"] or "").replace("{base}", "$b").replace("{nombre}", "$b.hl7")}
    lit = {"entrada_dir": "/in", "salida_dir": "/salida", "plantilla": pl or ""}
    out = []
    for i, trozo in enumerate(re.split(r"(\{[a-z_]+\})", arg)):
        if i % 2 == 0:
            out.append(shlex.quote(trozo) if trozo else "")
        else:
            k = trozo[1:-1]
            out.append('"%s"' % din[k] if k in din else shlex.quote(lit[k]))
    return "".join(out)


def bucle(ad, pl):
    cmd = " ".join(_palabra_sh(a, pl, ad) for a in ad["invocacion"]["orden"])
    return ('for f in /in/*.hl7; do b=$(basename "$f" .hl7); %s > "/salida/$b.log" 2>&1; echo $? > "/salida/$b.rc"; done' % cmd)


def orden_caja(ad, n, pl, tin, tout, artefactos, ficheros, bucle_grupo=None):
    """La orden de Docker para un contenedor (función pura). ficheros: los del contenedor (uno en por_mensaje)."""
    c = ad["caja"]
    o = ["docker", "run"] + CAJA + ["--pids-limit", str(c["limites"]["pids"]), "--name", "vc-%s-%s" % (ad["id"], n)]
    for k, v in c["entorno"].items():
        o += ["-e", "%s=%s" % (k, v)]
    if c["limites"]["memoria_mb"]:
        o += ["--memory", "%dm" % c["limites"]["memoria_mb"]]
    for m in c["montajes"].values():
        o += ["-v", "%s:%s:ro" % (os.path.abspath(os.path.join(artefactos, m["origen"])), m["destino"])]
    o += ["-v", "%s:/in:ro" % tin, "-v", "%s:/salida" % tout, "--", c["imagen"]]      # «--»: nada tras él es una bandera
    inv = ad["invocacion"]
    if inv["modo"] == "mensaje" and inv["contenedor"] == "por_grupo" and (bucle_grupo is None or bucle_grupo):
        return o + ["sh", "-c", bucle(ad, pl)]
    v = _valores(ad, pl, ficheros[0] if inv["modo"] == "mensaje" and ficheros else None)
    return o + [_sustituir(a, v) for a in inv["orden"]]


def orden_local(ad, pl, tin, tout, f=None):
    """proceso_local (solo el juguete, S-VC-4): python3 -> el intérprete que corre la herramienta, rutas reales."""
    v = _valores(ad, pl, f, tin, tout)
    o = [_sustituir(a, v) for a in ad["invocacion"]["orden"]]
    return [sys.executable, os.path.realpath(JUGUETE)] + o[2:]


def comprobar_caja(ad, ejecutor):
    """-> (digest o None, None) si se puede correr; (None, texto) si no (salida 3)."""
    if ad["caja"]["tipo"] != "docker":
        return None, None
    rc, out = ejecutor.consultar(["docker", "version", "--format", "{{.Server.Version}}"])
    if rc != 0:
        return None, "Docker no está disponible (docker version: %s)" % (out.strip()[:200] or "no se encuentra docker")
    im = ad["caja"]["imagen"]
    rc, out = ejecutor.consultar(["docker", "image", "inspect", "--format", "{{index .RepoDigests 0}}", "--", im])
    m_ = re.search(r"sha256:[0-9a-f]{64}", out or "") if rc == 0 else None
    if m_ is None:
        rc2, out2 = ejecutor.consultar(["docker", "image", "inspect", "--format", "{{.Id}}", "--", im])
        m_ = re.search(r"sha256:[0-9a-f]{64}", out2 or "") if rc2 == 0 else None
    if m_ is None:
        return None, ("La imagen %s no está en esta máquina. La herramienta no descarga nada (S-VC-19); para traerla:\n"
                      "  docker pull %s" % (im, im))
    dg = m_.group(0)
    if ad["caja"]["imagen_digest"] and ad["caja"]["imagen_digest"] != dg:
        return None, "El digest de %s en esta máquina es %s y el adaptador pide %s (Q-VC-D-4)" % (im, dg, ad["caja"]["imagen_digest"])
    return dg, None


def agrupar(ad, casos, carpeta_corpus):
    """-> [(corpus, grupo, plantilla, [casos])]: un grupo por corpus en lote; por corpus y plantilla en por_grupo; uno por mensaje
    en por_mensaje. En orden de corpus y, dentro, de plantilla."""
    inv = ad["invocacion"]
    g = collections.OrderedDict()
    for x in casos:
        t = open(os.path.join(carpeta_corpus, x["fichero"]), encoding="utf-8").read()
        pl = plantilla(t, inv["plantilla"])
        x["plantilla"] = pl
        clave = (CORPUS.index(x["corpus"]), (pl or "") if inv["modo"] == "mensaje" else "", x["caso"] if inv["contenedor"] == "por_mensaje" else "")
        g.setdefault(clave, []).append(x)
    return [(v[0]["corpus"], v[0]["plantilla"] or v[0]["corpus"], v[0]["plantilla"], v) for k, v in sorted(g.items())]


def _cola(t, n=4000):
    return (t or "")[-n:]


def recortar(texto, ruta):
    """S-VC-8: el valor bajo `ruta` recortado del texto original, sin reserializar (conserva «1.20»). None si no está."""
    dec = json.JSONDecoder()
    i = 0
    for k, clave in enumerate(ruta):
        while i < len(texto) and texto[i].isspace():
            i += 1
        if i >= len(texto) or texto[i] != "{":
            return None
        i += 1
        encontrado = False
        while True:
            while i < len(texto) and texto[i] in " \t\r\n,":
                i += 1
            if i >= len(texto) or texto[i] == "}":
                return None
            try:
                nombre, i = dec.raw_decode(texto, i)
            except ValueError:
                return None
            while i < len(texto) and texto[i] in " \t\r\n:":
                i += 1
            try:
                _, fin = dec.raw_decode(texto, i)
            except ValueError:
                return None
            if nombre == clave:
                if k == len(ruta) - 1:
                    return texto[i:fin]
                encontrado = True
                break
            i = fin
        if not encontrado:
            return None
    return None


def _ruta_json(d, ruta):
    for k in ruta:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def leer_salida(ad, tout, f, reg_rc, reg_texto, rc_contenedor, salida_contenedor, vencido):
    """§2.3: el estado de un mensaje, en orden; nunca inventa un error (S-VC-9). reg_rc: el código registrado para este mensaje
    (.rc en por_grupo, el del proceso en por_mensaje) o None si no hay registro por mensaje."""
    s = ad["salida"]
    j = os.path.join(tout, _rellena(s["fichero"], f))
    if os.path.isfile(j):
        texto = open(j, "rb").read().decode(s["codificacion"], errors="replace")
        b = texto
        if s["forma"] == "envuelto":
            env = s["envoltura"]
            try:
                d = json.loads(texto)
            except ValueError:
                d = None
            if isinstance(d, dict):
                if env["ruta_estado"] is not None and _ruta_json(d, env["ruta_estado"]) != env["estado_ok"]:
                    return {"estado": "error", "error": {"codigo": str(_ruta_json(d, env["ruta_estado"]))[:64], "texto": texto[:4000]}}
                b = recortar(texto, env["ruta_bundle"]) or texto
        if len(b) > MAX_BUNDLE:
            return {"estado": "error", "error": {"codigo": "demasiado_grande", "texto": "%d caracteres" % len(b)}}
        return {"estado": "bundle", "bundle": b}
    if s["fichero_error"] and os.path.isfile(os.path.join(tout, _rellena(s["fichero_error"], f))):
        t = open(os.path.join(tout, _rellena(s["fichero_error"], f)), "rb").read().decode("utf-8", errors="replace")
        return {"estado": "error", "error": {"codigo": "excepcion", "texto": t[:4000]}}
    if reg_rc is not None:
        if reg_rc != 0:
            return {"estado": "error", "error": {"codigo": str(reg_rc), "texto": _cola(reg_texto)}}
        return {"estado": "vacio"}                                               # Q-VC-D-2 (Jev: vacio)
    if not vencido and rc_contenedor == 0 and ad["invocacion"]["modo"] == "lote":
        return {"estado": "vacio"}
    return {"estado": "sin_respuesta", "error": {"codigo": "timeout" if vencido else str(rc_contenedor), "texto": _cola(salida_contenedor)}}


def _ms_stdout(ad, salida_contenedor):
    r = ad["invocacion"]["duracion_stdout"]
    return {m_.group("nombre"): int(m_.group("ms")) for m_ in re.finditer(r, salida_contenedor or "", re.M)} if r else {}


def _tmp_caja():
    tin, tout = tempfile.mkdtemp(prefix="vc_in_"), tempfile.mkdtemp(prefix="vc_out_")
    os.chmod(tin, 0o755)
    os.chmod(tout, 0o777)                                       # el contenedor corre como 65534
    return tin, tout


def _copiar(carpeta_corpus, casos, tin):
    for x in casos:
        d = os.path.join(tin, os.path.basename(x["fichero"]))
        shutil.copyfile(os.path.join(carpeta_corpus, x["fichero"]), d)
        os.chmod(d, 0o644)


class Corrida:
    """El paso 5: corre cada grupo y devuelve por caso su salida, o lo deja en sin_evidencia si falla la caja."""
    def __init__(self, ad, artefactos, ejecutor, carpeta_cajas, carpeta_corpus):
        self.ad, self.art, self.ej, self.cajas, self.corpus = ad, artefactos, ejecutor, carpeta_cajas, carpeta_corpus
        self.k, self.salidas, self.sin_evidencia, self.reintentos, self.duraciones = 0, {}, [], [], {}

    def _limite(self, n):
        lim = self.ad["caja"]["limites"]
        return min(lim["segundos_por_contenedor"], lim["segundos_por_mensaje"] * n + 30)

    def _uno(self, orden, timeout, etiqueta, local=False):
        self.k += 1
        nombre = None if local else orden[orden.index("--name") + 1]
        t0 = time.time()
        rc, out, vencido = self.ej.correr(orden, timeout, nombre)
        if not local and rc in (125, 126, 127):
            raise CajaNoDisponible("docker run devolvió %d: %s" % (rc, _cola(out, 300).strip()))
        open(os.path.join(self.cajas, "%s.log" % etiqueta), "w", encoding="utf-8").write(out or "")
        open(os.path.join(self.cajas, "%s.rc" % etiqueta), "w").write("timeout\n" if vencido else "%s\n" % rc)
        return rc, out, vencido, time.time() - t0

    def _contenedor(self, corpus, pl, casos, multiple):
        """Un contenedor (o, en local, el bucle equivalente). -> {caso: salida}."""
        ad, inv = self.ad, self.ad["invocacion"]
        local = ad["caja"]["tipo"] == "proceso_local"
        tin, tout = _tmp_caja()
        try:
            _copiar(self.corpus, casos, tin)
            fs = [os.path.basename(x["fichero"]) for x in casos]
            etiqueta = "%s-%s-%d" % (corpus, re.sub(r"[^A-Za-z0-9_.-]", "_", pl or corpus), self.k + 1)
            T = self._limite(len(casos))
            reg = {}
            en_bucle = inv["modo"] == "mensaje" and inv["contenedor"] == "por_grupo" and multiple   # el reintento, uno a uno
            if local and inv["modo"] == "mensaje":
                rc, out, vencido, dt = 0, "", False, 0.0
                t0 = time.time()
                for f in fs:
                    queda = T - (time.time() - t0)
                    if queda <= 0:
                        vencido = True
                        break
                    r1, o1, v1, _ = self._uno(orden_local(ad, pl, tin, tout, f), queda, etiqueta + "-" + os.path.splitext(f)[0], True)
                    if v1:
                        vencido = True
                        break
                    reg[f] = (r1, o1)
                    out += o1
                dt = time.time() - t0
            elif local:
                rc, out, vencido, dt = self._uno(orden_local(ad, pl, tin, tout), T, etiqueta, True)
            else:
                rc, out, vencido, dt = self._uno(orden_caja(ad, "%d-%d" % (os.getpid(), self.k + 1), pl, tin, tout, self.art, fs,
                                                            bucle_grupo=en_bucle), T, etiqueta)
            ms = _ms_stdout(ad, out)
            res = {}
            for x, f in zip(casos, fs):
                if en_bucle and not local:
                    rcf = os.path.join(tout, os.path.splitext(f)[0] + ".rc")
                    lg = os.path.join(tout, os.path.splitext(f)[0] + ".log")
                    r_, t_ = (int(open(rcf).read().strip() or -1), open(lg, encoding="utf-8", errors="replace").read() if os.path.exists(lg) else "") \
                        if os.path.exists(rcf) else (None, None)
                elif inv["modo"] == "mensaje":
                    r_, t_ = reg.get(f, (None, None)) if local else ((None, None) if vencido else (rc, out))
                else:
                    r_, t_ = None, None
                s = leer_salida(ad, tout, f, r_, t_, rc, out, vencido)
                s["duracion_ms"] = ms.get(f, int(dt * 1000 / max(len(casos), 1)))
                res[x["caso"]] = s
            if vencido and multiple:                                           # Q-VC-D-9 (Jev: reintentar)
                for x in casos:
                    if res[x["caso"]]["estado"] == "sin_respuesta":
                        self.reintentos.append("%s/%s" % (x["corpus"], x["caso"]))
                        res[x["caso"]] = self._contenedor(corpus, pl, [x], False)[x["caso"]]
            self.duraciones[etiqueta] = round(dt, 1)
            return res
        finally:
            shutil.rmtree(tin, ignore_errors=True)
            shutil.rmtree(tout, ignore_errors=True)

    def correr(self, grupos):
        ad, inv = self.ad, self.ad["invocacion"]
        cf = (inv["plantilla"] or {}).get("comprobar_fichero")
        for corpus, grupo, pl, casos in grupos:
            if cf:
                m = ad["caja"]["montajes"][cf["montaje"]]
                if not os.path.isfile(os.path.join(self.art, m["origen"], cf["patron"].replace("{plantilla}", pl or ""))):
                    for x in casos:                                            # L-VC-13
                        self.salidas[(x["corpus"], x["caso"])] = {"estado": "error", "error": {"codigo": "sin_plantilla",
                                                                  "texto": "no hay plantilla %s" % pl}, "duracion_ms": 0}
                    continue
            try:
                res = self._contenedor(corpus, pl, casos, inv["modo"] == "lote" or inv["contenedor"] == "por_grupo")
            except CajaNoDisponible as ex:
                self.sin_evidencia.append({"corpus": corpus, "grupo": grupo, "casos": ["%s/%s" % (x["corpus"], x["caso"]) for x in casos],
                                           "motivo": str(ex)[:500]})
                continue
            for x in casos:
                self.salidas[(x["corpus"], x["caso"])] = res[x["caso"]]


def invocacion_texto(ad):
    return " ".join(ad["invocacion"]["orden"])[:1024]


def evidencia(ad, h, x, texto, salida):
    """S-VC-5: exactamente la forma de S-CV-2."""
    e = {"punto_entrada": x["punto"], "mensaje": texto,
         "conversion": {"conversor": {"nombre": ad["conversor"]["nombre"], "version": ad["conversor"]["version"], "huella": h,
                                      "plantilla": x.get("plantilla"), "invocacion": invocacion_texto(ad)},
                        "salida": salida, "perfil_valor": "guia"}}
    M.validar(e["conversion"], M.E_PROPS["conversion"], "conversion")
    return e


# ---------------------------------------------------------------------------- el juicio y la agregación (§3 pasos 7-8, §4)
def _ruta_que(q):
    return re.split(r"[\s:]", q.strip(), 1)[0]


def _hecho_base(h):
    return re.sub(r"\(\d+\)", "", h or "")


def clase8(subtipo):
    """S-VC-12: cada pieza del subtipo, a su clase de las ocho (recurso_* -> recurso)."""
    out = []
    for p in (subtipo or "").split("+"):
        c = "recurso" if p.startswith("recurso_") else p
        if c in CLASES8 and c not in out:
            out.append(c)
    return out


def juzgar(cid, x, e, sensibilidad=True):
    r = V.verificar(e)
    alt = {q: CV.verificar(e, PE.resolver(None, e), CV.con_alternativas(q)) for q in CV.ALTERNATIVA} if sensibilidad else {}
    cuentan = [h for h in r["hallazgos"] if h["cuenta"]]
    return {"conversor": cid, "corpus": x["corpus"], "caso": x["caso"], "punto": e["punto_entrada"],
            "estado": e["conversion"]["salida"]["estado"], "categoria": r["veredicto"]["categoria"],
            "subtipo": r["veredicto"].get("subtipo"),
            "cuentan": [{"hecho": h["hecho"], "clase": h["clase"], "subtipo": h["subtipo"], "que": h["que"],
                         "ruta": _ruta_que(h["que"][0]) if h["que"] else "", "firma": MEC.firma(h["que"][0]) if h["que"] else "",
                         "clase8": clase8(h["subtipo"]) if h["clase"] != "rechazo" else [], "citas": h.get("citas") or []}
                        for h in cuentan],
            "notas": sorted({h["subtipo"] for h in r["hallazgos"] if not h["cuenta"] and h["subtipo"]}),
            "convenciones": [{"hecho": h["hecho"], "que": h["que"][:1]} for h in r["hallazgos"] if not h["cuenta"] and h["subtipo"] == "convencion"],
            "aceptables": [h["hecho"] for h in r["hallazgos"] if not h["cuenta"] and h["clase"] == "rechazo" and h["subtipo"] == "aceptable"],
            "alternativas": {q: {"categoria": a["veredicto"]["categoria"], "cuentan": sum(1 for h in a["hallazgos"] if h["cuenta"])}
                             for q, a in alt.items()},
            "plantilla": e["conversion"]["conversor"].get("plantilla"), "msh9": x.get("msh9")}


def pares_minimos(filas):
    """La regla exacta de cv3_minimos.juzgar: sale el hecho objetivo con su texto en el caso y no en el control."""
    idx = {f["caso"]: f for f in filas if f["corpus"] == "minimos"}
    detalle = []
    for pid, conv, _, (hecho, subtipo, texto) in MIN.PARES:
        d = {"id": pid, "para_conversor": conv, "objetivo": {"hecho": list(hecho) if isinstance(hecho, tuple) else hecho,
                                                             "subtipo": subtipo, "texto": texto}}
        for suf in ("caso", "control"):
            f = idx.get("%s-%s" % (pid, suf))
            if f is None:
                d[suf] = None
                continue
            if subtipo == "error":
                sale = f["estado"] != "bundle"
                vistos = [h for h in f["cuentan"] if h["clase"] == "rechazo"]
            else:
                hechos = hecho if isinstance(hecho, tuple) else (hecho,)
                vistos = [h for h in f["cuentan"] if h["hecho"] in hechos and any(texto in q for q in h["que"])]
                sale = bool(vistos)
            d[suf] = {"estado": f["estado"], "categoria": f["categoria"], "sale": sale, "que": [q for h in vistos for q in h["que"]][:2]}
        d["reproduce"] = bool(d["caso"] and d["control"] and d["caso"]["sale"] and not d["control"]["sale"])
        detalle.append(d)
    return {"aplica": True, "n": len(detalle), "reproducidos": sum(1 for d in detalle if d["reproduce"]), "detalle": detalle}


def agregar(ad, info, filas, co, sin_evidencia):
    """INFORME.json (§4.1): determinista, sin fechas, tiempos ni rutas (S-VC-14)."""
    normales = [f for f in filas if f["corpus"] != "minimos"]
    por = collections.OrderedDict()
    for c in CORPUS:
        fs = [f for f in normales if f["corpus"] == c]
        if fs:
            cats = collections.Counter(f["categoria"] for f in fs)
            por[c] = {"n": len(fs), "estados": dict(sorted(collections.Counter(f["estado"] for f in fs).items())),
                      "categorias": dict(sorted(cats.items())),
                      "porcentajes": {k: round(100.0 * v / len(fs), 1) for k, v in sorted(cats.items())}}
    mec = {c: collections.OrderedDict() for c in CLASES8}
    for f in normales:
        for h in f["cuentan"]:
            for c in h["clase8"]:
                k = (_hecho_base(h["hecho"]), h["ruta"], h["firma"])
                fila = mec[c].setdefault(k, {"hecho": k[0], "ruta": k[1], "firma": k[2], "casos": set(), "corpus": collections.Counter(),
                                             "ejemplo": None, "citas": set(), "clase_cv": "sin_contraste"})
                if (f["corpus"], f["caso"]) not in fila["casos"]:
                    fila["casos"].add((f["corpus"], f["caso"]))
                    fila["corpus"][f["corpus"]] += 1
                ej = {"caso": "%s/%s" % (f["corpus"], f["caso"]), "que": h["que"][0] if h["que"] else ""}
                if fila["ejemplo"] is None or ej["caso"] < fila["ejemplo"]["caso"]:
                    fila["ejemplo"] = ej
                fila["citas"].update(h["citas"])
    mecanismos = {}
    for c in CLASES8:
        rows = []
        for v in mec[c].values():
            rows.append({"hecho": v["hecho"], "ruta": v["ruta"], "firma": v["firma"], "n": len(v["casos"]), "corpus": dict(sorted(v["corpus"].items())),
                         "ejemplo": v["ejemplo"], "citas": sorted(v["citas"]), "clase_cv": "sin_contraste"})
        mecanismos[c] = sorted(rows, key=lambda r: (-r["n"], r["hecho"], r["ruta"], r["firma"]))
    no_soporta = set(ad["conversor"]["declara"]["no_soporta"])
    rech = collections.OrderedDict()
    acept = collections.Counter()
    for f in normales:
        for h in f["cuentan"]:
            if h["clase"] == "rechazo":
                tev = "^".join((f.get("msh9") or "").split("^")[:2]).upper()
                k = (MEC.firma(h["que"][0]) if h["que"] else "", tev in no_soporta)
                r = rech.setdefault(k, {"firma_texto": k[0], "n": 0, "ejemplo": None, "declarado_por_adaptador": k[1]})
                r["n"] += 1
                ej = {"caso": "%s/%s" % (f["corpus"], f["caso"]), "texto": h["que"][0] if h["que"] else ""}
                if r["ejemplo"] is None or ej["caso"] < r["ejemplo"]["caso"]:
                    r["ejemplo"] = ej
        for a in f.get("aceptables", []):
            acept[_hecho_base(a)] += 1
    conv = collections.Counter()
    for f in normales:
        for c in f.get("convenciones", []):
            conv[(_hecho_base(c["hecho"]), MEC.firma(c["que"][0]) if c["que"] else "")] += 1
    nj = {"fuera_de_alcance": [{"caso": "%s/%s" % (f["corpus"], f["caso"]), "msh9": f.get("msh9")} for f in normales if f["categoria"] == "fuera_de_alcance"],
          "indeterminado": {}, "sin_evidencia": [x for x in sin_evidencia if x["corpus"] != "minimos"],
          "sin_msh": [x for x in co["sin_msh"] if not x.startswith("minimos/")],
          "muestras": ("n = %d" % co["n"]["muestras"]) if co["n"].get("muestras") else "no disponibles"}
    for sub in ("sin_salida", "lectura", "emparejamiento"):
        nj["indeterminado"][sub] = []
    for f in normales:
        if f["categoria"] == "indeterminado":
            nj["indeterminado"].setdefault(f["subtipo"] or "otro", []).append("%s/%s" % (f["corpus"], f["caso"]))
    juzgados = sum(1 for f in normales if f["categoria"] in ("correcto", "fallo_silencioso", "rechazo_incorrecto"))
    n_casos = sum(1 for x in co["casos"] if x["corpus"] != "minimos") + len(nj["sin_msh"])
    con_min = any(f["corpus"] == "minimos" for f in filas)
    sens = {}
    for q in CV.ALTERNATIVA:
        if any(q in f["alternativas"] for f in normales):
            sens[q] = {"fallo_silencioso_con_jev": sum(1 for f in normales if f["categoria"] == "fallo_silencioso"),
                       "con_alternativa": sum(1 for f in normales if f["alternativas"].get(q, {}).get("categoria") == "fallo_silencioso")}
    lim = ad["caja"]["limites"]
    return collections.OrderedDict([
        ("herramienta", {"nombre": "verificar_conversor", "version": VERSION, "huella": _sha(open(os.path.abspath(__file__), "rb").read())}),
        ("juez", {"huella": info["juez"]["huella"], "servidor": info["juez"]["servidor"], "revision": info["juez"]["revision"]}),
        ("conversor", {"id": ad["id"], "nombre": ad["conversor"]["nombre"], "version": ad["conversor"]["version"], "huella": info["huella"],
                       "huella_con_nombres": info["huella_con_nombres"], "imagen": ad["caja"]["imagen"], "imagen_digest": info["imagen_digest"]}),
        ("corpus", {"huella": co["huella"], "huella_adt_oru_muestras": co["huella_adt_oru_muestras"], "por_corpus": co["por_corpus"], "n": co["n"]}),
        ("caja", {"tipo": ad["caja"]["tipo"], "restricciones": (["--network none", "--read-only", "--tmpfs /tmp", "--cap-drop ALL",
                  "--security-opt no-new-privileges", "--user 65534:65534", "--pids-limit %d" % lim["pids"]]
                  + (["--memory %dm" % lim["memoria_mb"]] if lim["memoria_mb"] else [])) if ad["caja"]["tipo"] == "docker"
                  else ["proceso local: solo el conversor de juguete del laboratorio (S-VC-4)"], "limites": lim}),
        ("totales", {"n": n_casos, "juzgados": juzgados, "no_juzgados": n_casos - juzgados}),
        ("por_corpus", por),
        ("mecanismos", mecanismos),
        ("rechazos", {"incorrectos": sorted(rech.values(), key=lambda r: (-r["n"], r["firma_texto"])),
                      "aceptables": {"n": sum(acept.values()), "por_motivo": dict(sorted(acept.items()))}}),
        ("convenciones", {"n": sum(conv.values()), "detalle": [{"hecho": k[0], "firma": k[1], "n": v} for k, v in sorted(conv.items(), key=lambda t: (-t[1], t[0]))]}),
        ("pares_minimos", pares_minimos(filas) if con_min else {"aplica": False, "texto": "los 68 mínimos se juzgan solo con los dos conversores del estudio (Q-VC-D-3)"}),
        ("no_juzgado", nj),
        ("sensibilidad", sens),
        ("contraste_con_el_proyecto", {"hecho": False, "texto": FRASE_FIJA}),
        ("limites", {"L-CV": sorted(CV.L_CV, key=lambda k: int(k.split("-")[-1])), "L-VC": L_VC}),
    ])


# ---------------------------------------------------------------------------- el informe en Markdown (§4.3)
def _tabla(cab, filas):
    out = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    for f in filas:
        out.append("| " + " | ".join(str(x).replace("|", "\\|").replace("\n", " ") for x in f) + " |")
    return out


def informe_md(inf, adaptador_nombre="<adaptador.json>"):
    c, j, co, caja = inf["conversor"], inf["juez"], inf["corpus"], inf["caja"]
    L = ["# Verificación del conversor %s" % c["nombre"], "",
         "- **Conversor:** %s, versión %s; huella `%s` (con nombres `%s`)." % (c["nombre"], c["version"], c["huella"][:16], c["huella_con_nombres"][:16]),
         "- **Imagen:** %s." % ("%s, digest `%s`" % (c["imagen"], c["imagen_digest"]) if c["imagen"] else "ninguna (proceso local)"),
         "- **Juez:** huella `%s`, servidor %s." % (j["huella"][:16], j["servidor"]),
         "- **Corpus:** %s; huella `%s`." % (", ".join("%s %d" % (k, v) for k, v in co["n"].items() if v), co["huella"][:16]),
         "- **Caja:** %s; límites: %d s por mensaje, %d s por contenedor." % (", ".join(caja["restricciones"]), caja["limites"]["segundos_por_mensaje"],
                                                                              caja["limites"]["segundos_por_contenedor"]),
         "- **Herramienta:** verificar_conversor %s, huella `%s`." % (inf["herramienta"]["version"], inf["herramienta"]["huella"][:16]),
         "", "## Lo que esta herramienta no puede saber", "", "> " + FRASE_FIJA, "",
         "## Categorías por corpus", ""]
    cats = ("correcto", "fallo_silencioso", "rechazo_incorrecto", "indeterminado", "fuera_de_alcance")
    L += _tabla(["corpus", "n", "estados"] + list(cats),
                [[k, v["n"], ", ".join("%s %d" % e for e in v["estados"].items())] +
                 ["%d (%.1f %%)" % (v["categorias"].get(x, 0), v["porcentajes"].get(x, 0.0)) for x in cats] for k, v in inf["por_corpus"].items()])
    L += ["", "## Mecanismos que cuentan, por clase", "",
          "Un hallazgo puede estar en dos clases; los casos no se suman entre clases. La columna «contraste» dice si una persona "
          "lo ha contrastado con el proyecto del conversor: aquí, siempre «sin hacer».", ""]
    for cl in CLASES8:
        L.append("### %s" % cl)
        L.append("")
        rows = inf["mecanismos"][cl]
        if not rows:
            L += ["Ninguno.", ""]
            continue
        L += _tabla(["hecho", "ruta", "n", "corpus", "ejemplo", "citas", "contraste"],
                    [[r["hecho"], r["ruta"], r["n"], ", ".join("%s %d" % e for e in r["corpus"].items()),
                      "%s: %s" % (r["ejemplo"]["caso"], r["ejemplo"]["que"][:200]), " ".join(r["citas"][:4]), "sin hacer"] for r in rows])
        L.append("")
    re_ = inf["rechazos"]
    L += ["## Rechazos", "", "No son de las ocho clases. Los que el adaptador declara que el proyecto no convierte van aparte; el juez "
          "los cuenta igual (Q-CV-D-13).", ""]
    if re_["incorrectos"]:
        L += _tabla(["n", "declarado por el adaptador", "ejemplo"],
                    [[r["n"], "sí" if r["declarado_por_adaptador"] else "no", "%s: %s" % (r["ejemplo"]["caso"], r["ejemplo"]["texto"][:200])]
                     for r in re_["incorrectos"]])
    else:
        L.append("Ningún rechazo incorrecto.")
    L += ["", "Rechazos aceptables (Q-CV-D-7): %d%s." % (re_["aceptables"]["n"], (": " + ", ".join("%s %d" % e for e in re_["aceptables"]["por_motivo"].items()))
                                                         if re_["aceptables"]["n"] else ""), ""]
    pm = inf["pares_minimos"]
    L += ["## Pares mínimos del laboratorio", ""]
    if not pm["aplica"]:
        L += [pm["texto"] + ".", ""]
    else:
        L += ["34 sondas escritas en el estudio para Microsoft y LinuxForHealth (`cv/cv3_minimos.py`). Un par que se reproduce "
              "aquí quiere decir que este conversor muestra el mismo mecanismo; uno que no, nada más que eso. Se reproducen %d de %d."
              % (pm["reproducidos"], pm["n"]), ""]
        L += _tabla(["par", "escrito para", "objetivo", "caso", "control", "se reproduce"],
                    [[d["id"], d["para_conversor"], "%s %s" % (d["objetivo"]["hecho"], d["objetivo"]["subtipo"]),
                      "%s/%s/%s" % (d["caso"]["estado"], d["caso"]["categoria"], "sale" if d["caso"]["sale"] else "no sale") if d["caso"] else "—",
                      "%s/%s/%s" % (d["control"]["estado"], d["control"]["categoria"], "sale" if d["control"]["sale"] else "no sale") if d["control"] else "—",
                      "sí" if d["reproduce"] else "no"] for d in pm["detalle"]])
        L.append("")
    nj, t = inf["no_juzgado"], inf["totales"]
    L += ["## Lo que no se juzgó", "", "%d mensajes: %d juzgados y %d no juzgados." % (t["n"], t["juzgados"], t["no_juzgados"]), "",
          "- **Fuera de alcance:** %d%s." % (len(nj["fuera_de_alcance"]), (" (" + ", ".join("%s %s" % (x["caso"], x["msh9"]) for x in nj["fuera_de_alcance"][:20]) + ")") if nj["fuera_de_alcance"] else "")]
    for k, v in nj["indeterminado"].items():
        L.append("- **Indeterminado, %s:** %d%s." % (k, len(v), (" (" + ", ".join(v[:20]) + ")") if v else ""))
    L.append("- **Sin evidencia (falló la caja):** %d%s." % (sum(len(x["casos"]) for x in nj["sin_evidencia"]),
                                                            "".join(" Grupo %s: %s." % (x["grupo"], x["motivo"][:200]) for x in nj["sin_evidencia"])))
    L.append("- **Sin MSH legible:** %d%s." % (len(nj["sin_msh"]), (" (" + ", ".join(nj["sin_msh"][:20]) + ")") if nj["sin_msh"] else ""))
    L += ["- **Muestras de los proyectos:** %s." % nj["muestras"], "", "## Sensibilidad", ""]
    if inf["sensibilidad"]:
        L += _tabla(["decisión", "fallo silencioso con la de Jev", "con la alternativa"],
                    [[q, v["fallo_silencioso_con_jev"], v["con_alternativa"]] for q, v in inf["sensibilidad"].items()])
    else:
        L.append("No se calculó (--sin-sensibilidad).")
    cv_ = inf["convenciones"]
    L += ["", "## Convenciones", "", "Diferencias que la guía admite y no cuentan: %d." % cv_["n"], ""]
    if cv_["detalle"]:
        L += _tabla(["hecho", "firma", "n"], [[d["hecho"], d["firma"], d["n"]] for d in cv_["detalle"][:30]])
        L.append("")
    L += ["## Límites", "", "Los del juez: %s (`info_verificador`)." % ", ".join(inf["limites"]["L-CV"]), ""]
    L += ["- **%s:** %s" % (k, v) for k, v in inf["limites"]["L-VC"].items()]
    L += ["", "## Cómo repetir", "", "```", "python3 cv/verificar_conversor.py %s <salida> --artefactos <carpeta de artefactos>" % adaptador_nombre, "```", ""]
    return "\n".join(L)


PROHIBIDAS = re.compile(r"\b(nuev[oa]s?|confirmad[oa]s?|ya declarad[oa]s?)\b", re.I)
RUTA_MAQUINA = re.compile(r"(/(?:home|datos|tmp|Users|root)/|[A-Za-z]:\\)")


def comprobar_informe(md, inf):
    """-> lista de problemas (vacía si está bien): §4.3 y P-VC-19."""
    p = []
    if inf["contraste_con_el_proyecto"]["hecho"] is not False:
        p.append("contraste_con_el_proyecto.hecho no es false")
    if any(x["clase_cv"] != "sin_contraste" for v in inf["mecanismos"].values() for x in v):
        p.append("una fila con clase_cv distinta de sin_contraste")
    if FRASE_FIJA not in md:
        p.append("falta la frase fija")
    resto = md.replace(FRASE_FIJA, "")
    for m_ in PROHIBIDAS.finditer(resto):
        p.append("palabra prohibida: %r" % m_.group(0))
    if "discrepancias nuevas y confirmadas" in resto:
        p.append("la frase del estudio")
    for m_ in RUTA_MAQUINA.finditer(md + json.dumps(inf, ensure_ascii=False)):
        p.append("ruta de máquina: %r" % m_.group(0))
    return p


# ---------------------------------------------------------------------------- el control (§6)
def _valor(f):
    return {"estado": f["estado"], "categoria": f["categoria"], "subtipo": f.get("subtipo"),
            "hallazgos": sorted({(h["hecho"], h["clase"], h["subtipo"]) for h in f["cuentan"]})}


def comparar(filas, referencia):
    """Q-VC-D-7 (Jev: mas_hallazgos): (estado, categoria, subtipo, {(hecho, clase, subtipo)}) por (conversor, corpus, caso); el
    texto «que» no cuenta. Solo en los corpus que tiene la referencia."""
    clave = lambda f: (f["conversor"], f["corpus"], f["caso"])  # noqa: E731
    a = {clave(f): f for f in filas}
    b = {clave(f): f for f in referencia}
    corpus_ref = {k[1] for k in b}
    dif = []
    for k in sorted(set(a) & set(b)):
        va, vb = _valor(a[k]), _valor(b[k])
        if va != vb:
            dif.append({"conversor": k[0], "corpus": k[1], "caso": k[2], "corrida": va, "referencia": vb})
    return {"diferencias": json.loads(json.dumps(dif)), "solo_en_corrida": [list(k) for k in sorted(set(a) - set(b)) if k[1] in corpus_ref],
            "solo_en_referencia": [list(k) for k in sorted(set(b) - set(a))]}


# ---------------------------------------------------------------------------- la orden (§3)
def _escribir_json(ruta, d):
    with open(ruta, "w", encoding="utf-8") as g:
        g.write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")


def _paso(n, texto):
    print("[%d/9] %s" % (n, texto), flush=True)


def _preparar_salida(salida):
    if os.path.isdir(salida) and os.listdir(salida) and not os.path.exists(os.path.join(salida, "CORRIDA.json")):
        raise ErrorAdaptador("salida_ocupada", "salida", "la carpeta %s no está vacía y no es de una corrida anterior" % salida)
    for x in ("corpus", "cajas", "evidencias"):
        shutil.rmtree(os.path.join(salida, x), ignore_errors=True)
    for x in ("ADAPTADOR.json", "CORRIDA.json", "juicio.jsonl", "INFORME.json", "INFORME.md", "CONTROL.json"):
        if os.path.exists(os.path.join(salida, x)):
            os.remove(os.path.join(salida, x))
    os.makedirs(os.path.join(salida, "cajas"), exist_ok=True)


def _orden_tipo(ad):
    """La orden de la caja sin rutas de máquina, para CORRIDA.json."""
    if ad["caja"]["tipo"] != "docker":
        return "python3 conversor_juguete.py (proceso local, S-VC-4)"
    nombres = {m["destino"]: k for k, m in ad["caja"]["montajes"].items()}
    out = []
    for x in orden_caja(ad, "<n>", "<plantilla>", "<tin>", "<tout>", "", ["<fichero>"]):
        m_ = re.match(r"^.*:(/[^:]*):ro$", x)
        out.append("<%s>:%s:ro" % (nombres[m_.group(1)], m_.group(1)) if m_ and m_.group(1) in nombres else x)
    return " ".join(out)


def correr(ad, salida, artefactos, ejecutor, op, imagen_digest=None, adaptador_nombre="<adaptador.json>"):
    """Pasos 3-9. -> código de salida."""
    o = {"lab": True, "minimos": False, "propios": [], "muestras": None, "sensibilidad": True, "limite": None, "json_solo": False,
         "comparar": None}
    o.update(op)
    _preparar_salida(salida)
    _escribir_json(os.path.join(salida, "ADAPTADOR.json"), ad)
    _paso(3, "huella del conversor")
    info = {"juez": M._version(), "huella": huella(ad, artefactos), "huella_con_nombres": huella_con_nombres(ad, artefactos),
            "imagen_digest": imagen_digest}
    corrida = collections.OrderedDict([
        ("herramienta", {"version": VERSION, "huella": _sha(open(os.path.abspath(__file__), "rb").read())}),
        ("juez", {k: info["juez"][k] for k in ("huella", "servidor", "commit")}),
        ("conversor", {"id": ad["id"], "nombre": ad["conversor"]["nombre"], "version": ad["conversor"]["version"]}),
        ("huella", info["huella"]), ("huella_con_nombres", info["huella_con_nombres"]),
        ("imagen", ad["caja"]["imagen"]), ("imagen_digest", imagen_digest),
        ("caja", _orden_tipo(ad)), ("limites", ad["caja"]["limites"]),
        ("opciones", {k: (v if k not in ("propios", "muestras", "comparar") else bool(v)) for k, v in o.items()}),
        ("fecha", datetime.datetime.now().astimezone().isoformat(timespec="seconds")),
        ("rutas", {"salida": os.path.abspath(salida), "artefactos": os.path.abspath(artefactos)})])
    _escribir_json(os.path.join(salida, "CORRIDA.json"), corrida)
    _paso(4, "corpus")
    co = generar_corpus(os.path.join(salida, "corpus"), lab=o["lab"], minimos=o["minimos"], propios=o["propios"], muestras=o["muestras"],
                        limite=o["limite"])
    corrida["corpus"] = {"huella": co["huella"], "huella_adt_oru_muestras": co["huella_adt_oru_muestras"], "n": co["n"]}
    _paso(5, "caja: %d mensajes" % len(co["casos"]))
    grupos = agrupar(ad, co["casos"], os.path.join(salida, "corpus"))
    cr = Corrida(ad, artefactos, ejecutor, os.path.join(salida, "cajas"), os.path.join(salida, "corpus"))
    t0 = time.time()
    cr.correr(grupos)
    corrida.update({"sin_evidencia": cr.sin_evidencia, "reintentos": cr.reintentos,
                    "duraciones": {"total_s": round(time.time() - t0, 1), "contenedores": cr.duraciones}})
    _escribir_json(os.path.join(salida, "CORRIDA.json"), corrida)
    _paso(6, "evidencias")
    for x in co["casos"]:
        s = cr.salidas.get((x["corpus"], x["caso"]))
        if s is None:
            continue
        d = os.path.join(salida, "evidencias", ad["id"], x["corpus"])
        os.makedirs(d, exist_ok=True)
        texto = open(os.path.join(salida, "corpus", x["fichero"]), encoding="utf-8").read()
        _escribir_json(os.path.join(d, x["caso"] + ".json"), evidencia(ad, info["huella"], x, texto, s))
    return juzgar_y_escribir(ad, salida, info, co, cr.sin_evidencia, o, adaptador_nombre)


def juzgar_y_escribir(ad, salida, info, co, sin_evidencia, o, adaptador_nombre):
    """Pasos 7-9, también para --desde-evidencias."""
    _paso(7, "juicio")
    filas = []
    for x in co["casos"]:
        f = os.path.join(salida, "evidencias", ad["id"], x["corpus"], x["caso"] + ".json")
        if os.path.exists(f):
            filas.append(juzgar(ad["id"], x, json.load(open(f, encoding="utf-8")), o.get("sensibilidad", True)))
    with open(os.path.join(salida, "juicio.jsonl"), "w", encoding="utf-8") as g:
        for fila in filas:
            g.write(json.dumps(fila, ensure_ascii=False) + "\n")
    _paso(8, "agregados")
    inf = agregar(ad, info, filas, co, sin_evidencia)
    _escribir_json(os.path.join(salida, "INFORME.json"), inf)
    _paso(9, "informe")
    rc = 0
    if not o.get("json_solo"):
        md = informe_md(inf, adaptador_nombre)
        open(os.path.join(salida, "INFORME.md"), "w", encoding="utf-8").write(md)
        problemas = comprobar_informe(md, inf)
        if problemas:
            print("aviso: el informe no pasa su comprobación (%s)" % "; ".join(problemas[:5]))
    if sin_evidencia:
        rc = 4
    if o.get("comparar"):
        ref = [json.loads(x) for x in open(o["comparar"], encoding="utf-8") if x.strip()]
        c = comparar(filas, ref)
        _escribir_json(os.path.join(salida, "CONTROL.json"), c)
        print("comparación: %d diferencias, %d solo en la corrida, %d solo en la referencia" % (
            len(c["diferencias"]), len(c["solo_en_corrida"]), len(c["solo_en_referencia"])))
        if (c["diferencias"] or c["solo_en_corrida"] or c["solo_en_referencia"]) and rc == 0:
            rc = 5
    t = inf["totales"]
    print("verificar_conversor %s · juez %s · %d mensajes · juzgados %d · no juzgados %d · INFORME en %s" % (
        ad["id"], info["juez"]["huella"][:12], t["n"], t["juzgados"], t["no_juzgados"], os.path.join(salida, "INFORME.md")))
    return rc


def main(argv=None, ejecutor=None):
    p = argparse.ArgumentParser(prog="verificar_conversor", description="Verifica un conversor HL7 v2 -> FHIR R4 con un adaptador JSON.")
    p.add_argument("adaptador", help="el adaptador JSON (formato adaptador-vc/1)")
    p.add_argument("salida", help="la carpeta de salida: vacía o de una corrida anterior")
    p.add_argument("--artefactos", help="la base de las rutas del adaptador (o VC_ARTEFACTOS; por omisión, la carpeta del adaptador)")
    p.add_argument("--corpus", action="append", default=[], help="una carpeta con mensajes propios (*.hl7); se puede repetir")
    p.add_argument("--muestras", help="las muestras de los proyectos, en subcarpetas ms/ y lfh/, como en el estudio")
    p.add_argument("--sin-corpus-lab", action="store_true", help="sin las bases A1/E2 ni las ORU del laboratorio")
    p.add_argument("--sin-minimos", action="store_true", help="sin los 68 mínimos (solo entran con los dos conversores del estudio)")
    p.add_argument("--sin-sensibilidad", action="store_true", help="sin las alternativas de sensibilidad de Q-CV-D-3/5/9")
    p.add_argument("--limite-casos", type=int, metavar="N", help="solo los N primeros de cada corpus: una prueba de humo")
    p.add_argument("--solo-orden", action="store_true", help="valida, calcula la huella e imprime la orden del primer grupo; no corre nada")
    p.add_argument("--desde-evidencias", action="store_true", help="vuelve a juzgar las evidencias de una corrida anterior, sin correr")
    p.add_argument("--comparar", metavar="JUICIO", help="compara caso por caso con otro juicio.jsonl (sale con 5 si hay diferencias)")
    p.add_argument("--json-solo", action="store_true", help="no escribe INFORME.md")
    a = p.parse_args(argv)
    ejecutor = ejecutor or Ejecutor()
    artefactos = a.artefactos or os.environ.get("VC_ARTEFACTOS") or os.path.dirname(os.path.abspath(a.adaptador))
    _paso(1, "adaptador")
    try:
        ad = leer_adaptador(a.adaptador, artefactos)
    except ErrorAdaptador as ex:
        print("adaptador inválido: %s: %s" % (ex.campo, ex.texto))
        return 2
    op = {"lab": not a.sin_corpus_lab, "minimos": ad["id"] in ESTUDIO and not a.sin_minimos, "propios": a.corpus,
          "muestras": a.muestras, "sensibilidad": not a.sin_sensibilidad, "limite": a.limite_casos, "json_solo": a.json_solo,
          "comparar": a.comparar}
    nombre_ad = os.path.basename(a.adaptador)
    try:
        if a.desde_evidencias:
            ev = os.path.join(a.salida, "evidencias", ad["id"])
            if not os.path.isdir(ev) or not os.path.exists(os.path.join(a.salida, "corpus", "CASOS.json")):
                print("no hay evidencias en %s (ni corpus/CASOS.json): --desde-evidencias juzga una corrida anterior" % ev)
                return 1
            cr = json.load(open(os.path.join(a.salida, "CORRIDA.json"), encoding="utf-8"))
            co = json.load(open(os.path.join(a.salida, "corpus", "CASOS.json"), encoding="utf-8"))
            info = {"juez": M._version(), "huella": cr["huella"], "huella_con_nombres": cr["huella_con_nombres"],
                    "imagen_digest": cr.get("imagen_digest")}
            op["sensibilidad"] = cr.get("opciones", {}).get("sensibilidad", True) and op["sensibilidad"]
            return juzgar_y_escribir(ad, a.salida, info, co, cr.get("sin_evidencia", []), op, nombre_ad)
        if a.solo_orden:
            _paso(3, "huella del conversor: %s" % huella(ad, artefactos))
            d = tempfile.mkdtemp(prefix="vc_orden_")
            try:
                co = generar_corpus(os.path.join(d, "corpus"), lab=op["lab"], minimos=op["minimos"], propios=op["propios"],
                                    muestras=op["muestras"], limite=op["limite"])
                print("corpus: %s; huella %s" % (co["n"], co["huella"]))
                grupos = agrupar(ad, co["casos"], os.path.join(d, "corpus"))
            finally:
                shutil.rmtree(d, ignore_errors=True)
            if not grupos:
                print("no hay mensajes")
                return 0
            corpus, grupo, pl, casos = grupos[0]
            fs = [os.path.basename(x["fichero"]) for x in casos]
            o = orden_caja(ad, 1, pl, "<tin>", "<tout>", artefactos, fs) if ad["caja"]["tipo"] == "docker" else orden_local(ad, pl, "<tin>", "<tout>", fs[0])
            print("orden del primer grupo (%s, %s, %d mensajes):" % (corpus, grupo, len(casos)))
            print(" ".join(shlex.quote(x) for x in o))
            return 0
        _paso(2, "caja")
        dg, motivo = comprobar_caja(ad, ejecutor)
        if motivo:
            print(motivo)
            return 3
        return correr(ad, a.salida, artefactos, ejecutor, op, dg, nombre_ad)
    except ErrorAdaptador as ex:                                       # la carpeta de salida ocupada: un rechazo de entrada
        print("%s: %s" % (ex.campo, ex.texto))
        return 2
    except M.ErrorEntrada as ex:
        print("error interno: una evidencia no tiene la forma de S-CV-2 (%s)" % ex)
        return 1


if __name__ == "__main__":
    sys.exit(main())
