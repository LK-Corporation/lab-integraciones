#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 18 (cv/vc/diseno-vc-fable.md §5.2): P-VC-1..26, la herramienta cv/verificar_conversor.py ante el conversor de juguete
(cv/conversor_juguete.py) y ante un ejecutor espía que registra las órdenes de Docker sin correrlas. Corren sin Docker. Cada
prueba cambia una sola cosa y lleva su control negativo. Las decisiones de Jev (cv/vc/decision-jev-qvc.md) mandan.

Antes del código fallan todas por la misma razón: `import verificar_conversor` no encuentra el módulo.
  python3 cv/prueba_vc.py          -> TODO BIEN si no hay ningún MAL
  python3 cv/prueba_vc.py rojo     -> sale 0 solo si fallan las 26"""
import copy
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from contextlib import redirect_stdout

AQUI = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(AQUI)
sys.path[:0] = [AQUI, FASE]
sys.argv_guardado, sys.argv = sys.argv, ["x", "--silencio"]
import mcp_verificador as M  # noqa: E402
import verificador as V  # noqa: E402
from prueba_conversion import msg, oru_msg  # noqa: E402
try:
    import verificar_conversor as VC  # noqa: E402
except ImportError as ex:                                                   # en rojo: el módulo no existe todavía
    VC, ERROR_IMPORTACION = None, ex
sys.argv = sys.argv_guardado

mal, n_ok, grupo = [], [0], [None]
FALLAN = set()
RAIZ = tempfile.mkdtemp(prefix="prueba_vc_")
JUGUETE = os.path.join(AQUI, "conversor_juguete.py")


def mira(nombre, obtenido, esperado):
    if obtenido == esperado:
        n_ok[0] += 1
    else:
        print("  MAL %s %s: %r != %r" % (grupo[0], nombre, obtenido, esperado))
        mal.append(nombre)
        FALLAN.add(grupo[0])


def tmp(nombre="t"):
    return tempfile.mkdtemp(prefix=nombre + "_", dir=RAIZ)


def leer_json(ruta):
    return json.load(open(ruta, encoding="utf-8"))


def adaptador(nombre):
    return leer_json(os.path.join(AQUI, "adaptadores", nombre + ".json"))


def cambia(d, **cambios):
    """Copia de d con cambios por ruta con «__» («invocacion__modo»); el valor BORRA quita la clave."""
    d = copy.deepcopy(d)
    for ruta, v in cambios.items():
        partes = ruta.split("__")
        x = d
        for p in partes[:-1]:
            x = x.setdefault(p, {})
        if v == "BORRA":
            x.pop(partes[-1], None)
        else:
            x[partes[-1]] = v
    return d


def escribir_ad(d, carpeta=None):
    ruta = os.path.join(carpeta or tmp("ad"), "adaptador.json")
    with open(ruta, "w", encoding="utf-8") as g:
        g.write(d if isinstance(d, str) else json.dumps(d, ensure_ascii=False))
    return ruta


def con_msh8(t, directiva):
    segs = t.split("\r")
    p = segs[0].split("|")
    p += [""] * max(0, 8 - len(p))
    p[7] = directiva
    segs[0] = "|".join(p)
    return "\r".join(segs)


def con_msh10(t, v):
    segs = t.split("\r")
    p = segs[0].split("|")
    p[9] = v
    segs[0] = "|".join(p)
    return "\r".join(segs)


def adt(directiva="JUGUETE-NOMINAL", ev="A01", **k):
    return con_msh8(msg(ev, **k), directiva)


def oru(directiva="JUGUETE-NOMINAL"):
    return con_msh8(oru_msg(), directiva)


def artefactos_ms():
    """Las carpetas que pide el adaptador de Microsoft, vacías salvo un fichero (para las pruebas sin Docker)."""
    a = tmp("art")
    for d in ("ms/out", "ms/src/data/Templates/Hl7v2"):
        os.makedirs(os.path.join(a, d))
        open(os.path.join(a, d, "x.txt"), "w").write(d)
    open(os.path.join(a, "ms/src/data/Templates/Hl7v2/ADT_A01.liquid"), "w").write("{}")
    open(os.path.join(a, "ms/src/data/Templates/Hl7v2/ORU_R01.liquid"), "w").write("{}")
    return a


def artefactos_lfh():
    a = tmp("art")
    for d in ("lfh/lib", "lfh/clases"):
        os.makedirs(os.path.join(a, d))
        open(os.path.join(a, d, "x.txt"), "w").write(d)
    open(os.path.join(a, "lfh/Arnes.java"), "w").write("class Arnes {}")
    return a


def corpus_propio(mensajes):
    c = tmp("corpus")
    for nombre, t in mensajes.items():
        with open(os.path.join(c, nombre + ".hl7"), "w", encoding="utf-8", newline="") as g:
            g.write(t)
    return c


class Espia(VC.Ejecutor if VC else object):
    """Registra las órdenes sin correrlas. `consultar` contesta como un Docker con la imagen presente; `vence` simula un
    tiempo vencido en las corridas; `fallo` hace que la corrida cuyo texto contenga esa cadena lance CajaNoDisponible."""
    def __init__(self, vence=False, fallo=None, digest="mcr.microsoft.com/dotnet/runtime@sha256:" + "a" * 64):
        self.corridas, self.consultas, self.vence, self.fallo, self.digest = [], [], vence, fallo, digest
        self.matar = True

    def consultar(self, orden):
        self.consultas.append(orden)
        if orden[:2] == ["docker", "version"]:
            return 0, "27.0.0\n"
        if orden[:3] == ["docker", "image", "inspect"]:
            return 0, self.digest + "\n"
        return 0, ""

    def _run(self, orden, timeout):
        self.corridas.append(orden)
        if self.fallo and self.fallo in " ".join(orden):
            raise VC.CajaNoDisponible("fallo simulado")
        if self.vence:
            raise subprocess.TimeoutExpired(orden, timeout)
        return 0, ""


def correr(mensajes, ad=None, args=(), ejecutor=None, artefactos=AQUI, minimos=False):
    """Corre la herramienta con el juguete (o el adaptador dado) sobre los mensajes como corpus propio, sin el del laboratorio
    y, salvo minimos=True, sin los mínimos (con el adaptador de Microsoft entrarían por omisión: Q-VC-D-3)."""
    salida = os.path.join(tmp("salida"), "s")
    a = [escribir_ad(ad or adaptador("juguete")), salida, "--artefactos", artefactos, "--sin-corpus-lab",
         "--corpus", corpus_propio(mensajes)] + ([] if minimos else ["--sin-minimos"]) + list(args)
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = VC.main(a, ejecutor=ejecutor)
    return rc, salida, buf.getvalue()


def evid(salida, caso, corpus="propio", cid="juguete"):
    return leer_json(os.path.join(salida, "evidencias", cid, corpus, caso + ".json"))


def juicio(salida):
    return {(x["corpus"], x["caso"]): x for x in map(json.loads, open(os.path.join(salida, "juicio.jsonl"), encoding="utf-8"))}


def informe(salida):
    return leer_json(os.path.join(salida, "INFORME.json"))


def cat(fila):
    return (fila["categoria"], fila["subtipo"])


def cuentan(fila):
    return sorted((h["clase"], h["subtipo"], h["hecho"]) for h in fila["cuentan"])


def codigo(f, *a, **k):
    try:
        f(*a, **k)
        return None
    except VC.ErrorAdaptador as ex:
        return ex.codigo


# ---------------------------------------------------------------------------- P-VC-1..26
def p01():
    ad = VC.leer_adaptador(os.path.join(AQUI, "adaptadores", "juguete.json"), AQUI)
    mira("sin claves _", [k for k in json.dumps(ad) .split('"') if k.startswith("_")], [])
    mira("por omisión", (ad["salida"]["codificacion"], ad["invocacion"]["duracion_stdout"], ad["invocacion"]["plantilla"],
                         ad["caja"]["imagen_digest"], ad["conversor"]["declara"]), ("utf-8", None, None, None, {"no_soporta": []}))
    try:
        VC.leer_adaptador(cambia(adaptador("juguete"), conversor__nombre="BORRA"), AQUI)
        mira("sin nombre", "aceptado", "rechazo")
    except VC.ErrorAdaptador as ex:
        mira("sin nombre", ex.campo, "conversor.nombre")
    rc, _, _ = correr({"a": adt()}, cambia(adaptador("juguete"), conversor__nombre="BORRA"))
    mira("salida 2", rc, 2)


def p02():
    art = artefactos_ms()
    ms = adaptador("microsoft")
    malos = [
        ("json_invalido", "{no es json"),
        ("formato", cambia(ms, formato="adaptador-vc/9")),
        ("id", cambia(ms, id="Microsoft")),
        ("imagen_obligatoria", cambia(ms, caja__imagen="BORRA")),
        ("montaje_destino", cambia(ms, caja__montajes__codigo__destino="/in")),
        ("montaje_inexistente", cambia(ms, caja__montajes__codigo__origen="ms/nada")),
        ("entorno_reservado", cambia(ms, caja__entorno={"HOME": "/x"})),
        ("entorno_nombre", cambia(ms, caja__entorno={"1abc": "x"})),
        ("limite_fuera_de_rango", cambia(ms, caja__limites__segundos_por_mensaje=0)),
        ("marcador_desconocido", cambia(ms, invocacion__orden=["dotnet", "{foo}", "{entrada_fichero}"])),
        ("lote_marcador", cambia(ms, invocacion__modo="lote", invocacion__orden=["conv", "{entrada_dir}", "{base}"])),
        ("mensaje_sin_contenedor", cambia(ms, invocacion__contenedor="BORRA")),
        ("plantilla_sin_regla", cambia(ms, invocacion__plantilla=None)),
        ("envoltura_sin_ruta", cambia(ms, salida__envoltura__ruta_bundle=[])),
        ("clave_desconocida", cambia(ms, cajita=1)),
    ]
    for esperado, d in malos:
        mira("malo %s" % esperado, codigo(VC.leer_adaptador, escribir_ad(d), art), esperado)
    buenos = [ms, cambia(ms, formato="adaptador-vc/1"), cambia(ms, id="microsoft-2"), cambia(ms, caja__imagen="otra:1"),
              cambia(ms, caja__montajes__codigo__destino="/app2"), cambia(ms, caja__montajes__codigo__origen="ms/out"),
              cambia(ms, caja__entorno={"HOMEX": "/x"}), cambia(ms, caja__entorno={"ABC": "x"}),
              cambia(ms, caja__limites__segundos_por_mensaje=1),
              cambia(ms, invocacion__orden=["dotnet", "{plantilla}", "{entrada_fichero}"]),
              cambia(ms, invocacion__modo="lote", invocacion__contenedor="BORRA", invocacion__plantilla=None,
                     invocacion__orden=["conv", "{entrada_dir}", "{salida_dir}"]),
              cambia(ms, invocacion__contenedor="por_mensaje"),
              cambia(ms, invocacion__plantilla=None, invocacion__orden=["dotnet", "-r", "ADT_A01", "{entrada_fichero}"]),
              cambia(ms, salida__envoltura__ruta_bundle=["FhirResource"]), cambia(ms, _cajita=1)]
    mira("los corregidos pasan", [codigo(VC.leer_adaptador, escribir_ad(d), art) for d in buenos], [None] * 15)


def indice_secuencia(lista, secuencia):
    """Posición de la sublista contigua `secuencia` en `lista`, o -1."""
    for i in range(len(lista) - len(secuencia) + 1):
        if lista[i:i + len(secuencia)] == secuencia:
            return i
    return -1


def p03():
    art = artefactos_ms()
    ad = VC.leer_adaptador(adaptador("microsoft"), art)
    o = VC.orden_caja(ad, 1, "ADT_A01", "/T/in", "/T/out", art, ["a.hl7", "b.hl7"])
    mira("docker run", o[:2], ["docker", "run"])
    seq = [["--rm"], ["--network", "none"], ["--read-only"], ["--tmpfs", "/tmp"], ["--cap-drop", "ALL"],
           ["--security-opt", "no-new-privileges"], ["--user", "65534:65534"], ["-e", "HOME=/tmp"], ["--pids-limit", "1024"],
           ["--name", "vc-microsoft-1"]]
    pos = [indice_secuencia(o, s) for s in seq]
    mira("restricciones en orden", (all(p > 0 for p in pos), pos == sorted(pos)), (True, True))
    mira("una vez cada una", [sum(1 for i in range(len(o)) if o[i:i + len(s)] == s) for s in seq], [1] * len(seq))
    vs = [o[i + 1] for i in range(len(o)) if o[i] == "-v"]
    mira("montajes :ro", [v.endswith(":ro") for v in vs if not v.endswith(":/salida")], [True] * (len(vs) - 1))
    mira("entrada y salida", ("/T/in:/in:ro" in vs, "/T/out:/salida" in vs), (True, True))
    i = o.index("mcr.microsoft.com/dotnet/runtime:6.0")
    mira("sh -c", o[i + 1:i + 3], ["sh", "-c"])
    bucle = o[i + 3]
    mira("bucle", all(x in bucle for x in ("-r ADT_A01", '"$f"', '"/salida/$b.json"', '> "/salida/$b.log" 2>&1',
                                            'echo $? > "/salida/$b.rc"')), True)
    mira("privilegiado", codigo(VC.leer_adaptador, cambia(adaptador("microsoft"), caja__privilegiado=True), art), "clave_desconocida")
    mira("rw", codigo(VC.leer_adaptador, cambia(adaptador("microsoft"), caja__montajes__codigo__modo="rw"), art), "clave_desconocida")
    redes = [o[k + 1] for k in range(len(o) - 1) if o[k] == "--network"]
    mira("sin red ni privilegios", (redes, "--privileged" in o), (["none"], False))
    mira("«--» antes de la imagen", o[i - 1], "--")                  # revisión de VC4, hallazgo 1
    for im in ("--privileged", "--volume=/:/host:rw", "-v/:/h", "Mayusculas:1", "a b:1"):
        mira("imagen %r" % im, codigo(VC.leer_adaptador, cambia(adaptador("microsoft"), caja__imagen=im), art), "imagen_formato")
    for im in ("maven:3.9-eclipse-temurin-11", "localhost:5000/equipo/conv:1.2", "conv@sha256:" + "a" * 64):
        mira("control imagen %r" % im, codigo(VC.leer_adaptador, cambia(adaptador("microsoft"), caja__imagen=im), art), None)


def p04():
    ad = adaptador("juguete")
    mira("juguete aceptado", codigo(VC.leer_adaptador, ad, AQUI), None)
    mira("otro nombre", codigo(VC.leer_adaptador, cambia(ad, conversor__nombre="acme-conv"), AQUI), "proceso_local_solo_juguete")
    otro = tmp("otro")
    open(os.path.join(otro, "conversor_juguete.py"), "w").write("print(1)")
    mira("otro .py", codigo(VC.leer_adaptador, ad, otro), "proceso_local_solo_juguete")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def p05():
    import correr_conversor as CC
    a = tmp("huella")
    os.makedirs(os.path.join(a, "d", "sub"))
    for ruta, t in (("d/uno.txt", b"1"), ("d/sub/dos.txt", b"22"), ("d/tres.txt", b"333"), ("suelto.txt", b"s")):
        open(os.path.join(a, ruta), "wb").write(t)
    ad = cambia(adaptador("juguete"), conversor__huella__partes=[{"carpeta": "d"}, {"fichero": "suelto.txt"}])
    hd = CC.huella_carpeta(os.path.join(a, "d"))
    a_mano = sha((hd + sha(b"s")).encode())
    mira("fórmula del estudio", VC.huella(ad, a), a_mano)
    hn = VC.huella_con_nombres(ad, a)
    inv = cambia(ad, conversor__huella__partes=[{"fichero": "suelto.txt"}, {"carpeta": "d"}])
    mira("otro orden", VC.huella(inv, a) != a_mano, True)
    open(os.path.join(a, "d/uno.txt"), "wb").write(b"9")
    mira("un byte", VC.huella(ad, a) != a_mano, True)
    open(os.path.join(a, "d/uno.txt"), "wb").write(b"1")
    os.rename(os.path.join(a, "d/tres.txt"), os.path.join(a, "d/tres2.txt"))
    mira("renombrar: igual (L-VC-5)", VC.huella(ad, a), a_mano)
    mira("renombrar: con nombres cambia (Q-VC-D-1)", VC.huella_con_nombres(ad, a) != hn, True)


def manifiesto_cv2():
    return dict(reversed(x.split("  ", 1)) for x in open(os.path.join(AQUI, "CORPUS-CV2-MANIFIESTO.txt")).read().split("\n") if x)


def p06():
    import cv3_minimos as MIN
    c = os.path.join(tmp("corpus"), "c")
    co = VC.generar_corpus(c, lab=True, minimos=True)
    mira("n", co["n"], {"adt": 263, "oru": 40, "vxu": 40, "minimos": 68, "muestras": 0, "propio": 0})         # DV-VX-5: vxu
    man = manifiesto_cv2()
    lab = {k: v for k, v in man.items() if k.startswith(("adt/", "oru/"))}
    iguales = sum(1 for k, v in lab.items() if os.path.exists(os.path.join(c, k)) and sha(open(os.path.join(c, k), "rb").read()) == v)
    mira("303 líneas del manifiesto", (len(lab), iguales), (303, 303))
    m2 = tmp("min")
    with redirect_stdout(io.StringIO()):
        MIN.escribir(m2)
    distintos = [f for f in os.listdir(m2) if open(os.path.join(m2, f), "rb").read() != open(os.path.join(c, "minimos", f), "rb").read()]
    mira("68 mínimos byte a byte", (len(os.listdir(m2)), distintos), (68, []))
    normal = VC.normal
    try:
        VC.normal = lambda t: re.sub(r"\r\n|\n|\r", "\n", t.lstrip("﻿").strip()) + "\n"
        c2 = os.path.join(tmp("corpus"), "c")
        VC.generar_corpus(c2, lab=True, minimos=False)
        mal_ = sum(1 for k, v in lab.items() if sha(open(os.path.join(c2, k), "rb").read()) == v)
        mira("control LF: ninguna coincide", mal_, 0)
    finally:
        VC.normal = normal
    c3 = os.path.join(tmp("corpus"), "c")
    mira("sin mínimos", sum(VC.generar_corpus(c3, lab=True, minimos=False)["n"].values()), 343)       # DV-VX-5: 303 + 40 de VXU


def p07():
    d = tmp("propio")
    open(os.path.join(d, "a.hl7"), "wb").write(b"\xef\xbb\xbf" + msg().replace("\r", "\r\n").encode())
    open(os.path.join(d, "b.hl7"), "wb").write(oru_msg().replace("\r", "\n").encode())
    open(os.path.join(d, "c.hl7"), "wb").write(b"PID|1||X\n")
    open(os.path.join(d, "s.hl7"), "wb").write(msg(msh9="SIU^S12^SIU_S12").encode())
    c = os.path.join(tmp("corpus"), "c")
    co = VC.generar_corpus(c, lab=False, minimos=False, propios=[d])
    puntos = {x["caso"]: x["punto"] for x in co["casos"]}
    mira("puntos", puntos, {"a": "adt_conv", "b": "oru_conv", "s": "adt_conv"})
    a = open(os.path.join(c, "propio", "a.hl7"), "rb").read()
    mira("CR y sin BOM", (a[:3] != b"\xef\xbb\xbf", b"\n" not in a, a.endswith(b"\r")), (True, True, True))
    mira("sin MSH", co["sin_msh"], ["propio/c.hl7"])
    rc, salida, _ = correr({"s": con_msh8(msg(msh9="SIU^S12^SIU_S12"), "JUGUETE-NOMINAL")})
    mira("SIU fuera de alcance", cat(juicio(salida)[("propio", "s")]), ("fuera_de_alcance", None))


def p08():
    import correr_conversor as CC
    r = {"regla": "msh9_tipo_evento"}
    textos = [msg(), oru_msg(), msg().replace("|^~\\&|", "#$%*!#").replace("|", "#").replace("ADT^A01^ADT_A01", "ADT$A01$ADT_A01"),
              msg(msh9="adt^a01")]
    mira("tipo_evento", [VC.plantilla(t, r) for t in textos], ["ADT_A01", "ORU_R01", "ADT_A01", "ADT_A01"])
    mira("igual que el estudio", [VC.plantilla(t, r) for t in textos], [CC.plantilla(t) for t in textos])
    mira("tipo y fija", (VC.plantilla(msg(), {"regla": "msh9_tipo"}), VC.plantilla(msg(), {"regla": "fija", "valor": "X"})), ("ADT", "X"))
    art = artefactos_ms()
    e = Espia()
    rc, salida, _ = correr({"a05": msg("A05")}, adaptador("microsoft"), ejecutor=e, artefactos=art)
    s = evid(salida, "a05", cid="microsoft")["conversion"]["salida"]
    mira("sin plantilla", (s["estado"], s["error"]["codigo"], e.corridas), ("error", "sin_plantilla", []))
    open(os.path.join(art, "ms/src/data/Templates/Hl7v2/ADT_A05.liquid"), "w").write("{}")
    e = Espia()
    correr({"a05": msg("A05")}, adaptador("microsoft"), ejecutor=e, artefactos=art)
    mira("con plantilla, se llama", len(e.corridas), 1)


def p09():
    art = artefactos_ms()
    ms = {"a1": msg(), "a2": con_msh10(msg(), "M2"), "o1": oru_msg()}
    e = Espia()
    correr(ms, adaptador("microsoft"), ejecutor=e, artefactos=art)
    mira("dos grupos, por orden", [[x for x in o if x.startswith("for f")][0].split(" -r ")[1].split()[0] for o in e.corridas],
         ["ADT_A01", "ORU_R01"])
    mira("rc y log", all('.rc"' in o[-1] and '.log"' in o[-1] for o in e.corridas), True)
    e = Espia()
    correr(ms, cambia(adaptador("microsoft"), invocacion__contenedor="por_mensaje"), ejecutor=e, artefactos=art)
    mira("por_mensaje", (len(e.corridas), any("sh" in o for o in e.corridas)), (3, False))
    e = Espia()
    correr(ms, adaptador("linuxforhealth"), ejecutor=e, artefactos=artefactos_lfh())
    mira("lote", len(e.corridas), 1)


def p10():
    rc, salida, _ = correr({"n": adt(), "o": oru(), "g": adt("")})
    for caso in ("n", "o", "g"):
        e = evid(salida, caso)
        try:
            M.validar(e["conversion"], M.E_PROPS["conversion"], "conversion")
            ok = True
        except M.ErrorEntrada:
            ok = False
        mira("forma %s" % caso, (ok, e["conversion"]["salida"]["estado"], e["conversion"]["perfil_valor"]), (True, "bundle", "guia"))
        mira("sin rutas %s" % caso, ("/" + "tmp" in (e["conversion"]["conversor"].get("invocacion") or ""), RAIZ in json.dumps(e)), (False, False))
    mira("puntos", (evid(salida, "n")["punto_entrada"], evid(salida, "o")["punto_entrada"]), ("adt_conv", "oru_conv"))
    j = juicio(salida)
    mira("nominal", (cat(j[("propio", "n")]), cuentan(j[("propio", "n")])), (("correcto", None), []))
    rc, salida, _ = correr({"g": adt("JUGUETE-GENERO")})
    f = juicio(salida)[("propio", "g")]
    mira("control género", (cat(f), cuentan(f)), (("fallo_silencioso", "convertido"), [("fidelidad", "valor_distinto", "PID-8")]))


def p11():
    rc, salida, _ = correr({"e": adt("JUGUETE-ERROR"), "n": adt(), "f": adt("JUGUETE-ERROR", pid={7: "19801301"})})
    s = evid(salida, "e")["conversion"]["salida"]
    mira("error", (s["estado"], s["error"]["codigo"], "ErrorJuguete" in s["error"]["texto"], len(s["error"]["texto"]) <= 4000),
         ("error", "excepcion", True, True))
    j = juicio(salida)
    mira("rechazo incorrecto", cat(j[("propio", "e")]), ("rechazo_incorrecto", "error"))
    mira("control nominal", evid(salida, "n")["conversion"]["salida"]["estado"], "bundle")
    mira("control aceptable", (cat(j[("propio", "f")]), "aceptable" in j[("propio", "f")]["notas"]), (("correcto", None), True))
    pm = cambia(adaptador("juguete"), invocacion__modo="mensaje", invocacion__contenedor="por_mensaje",
                invocacion__orden=["python3", "conversor_juguete.py", "--fichero", "{entrada_fichero}", "--salida", "{salida_fichero}"])
    rc, salida, _ = correr({"r": adt("JUGUETE-RC3")}, pm)
    s = evid(salida, "r")["conversion"]["salida"]
    mira("rc3 por mensaje", (s["estado"], s["error"]["codigo"], "termina con 3" in s["error"]["texto"]), ("error", "3", True))


class Matado(VC.Ejecutor if VC else object):
    def _run(self, orden, timeout):
        return -9, "matado\n"


def p12():
    rc, salida, _ = correr({"v": adt("JUGUETE-NADA"), "n": adt()})
    mira("vacío", evid(salida, "v")["conversion"]["salida"]["estado"], "vacio")
    mira("indeterminado", cat(juicio(salida)[("propio", "v")]), ("indeterminado", "sin_salida"))
    rc, salida, _ = correr({"r": adt("JUGUETE-RC3"), "n": adt()})
    s = evid(salida, "r")["conversion"]["salida"]
    mira("rc3 en lote", (s["estado"], s["error"]["codigo"], evid(salida, "n")["conversion"]["salida"]["estado"]),
         ("sin_respuesta", "3", "bundle"))
    rc, salida, _ = correr({"n": adt()}, ejecutor=Matado())
    s = evid(salida, "n")["conversion"]["salida"]
    mira("matado", (s["estado"], s["error"]["codigo"]), ("sin_respuesta", "-9"))


def p13():
    lento = cambia(adaptador("juguete"), caja__limites={"segundos_por_mensaje": 1, "segundos_por_contenedor": 1, "pids": 64})
    t0 = time.time()
    rc, salida, _ = correr({"l": adt("JUGUETE-LENTO^5")}, lento)
    s = evid(salida, "l")["conversion"]["salida"]
    mira("timeout", (s["estado"], s["error"]["codigo"]), ("sin_respuesta", "timeout"))
    mira("rápido (reintento incluido, Q-VC-D-9)", time.time() - t0 < 4.5, True)
    mira("orden de matar", VC.orden_matar("vc-x-1"), ["docker", "kill", "vc-x-1"])
    e = Espia(vence=True)
    correr({"a": msg()}, adaptador("microsoft"), ejecutor=e, artefactos=artefactos_ms())
    mira("mata tras vencer", [o for o in e.consultas if o[:2] == ["docker", "kill"]][:1], [["docker", "kill", e.corridas[0][e.corridas[0].index("--name") + 1]]])
    mira("reintento uno a uno", (len(e.corridas), "sh" in e.corridas[1]), (2, False))
    holgado = cambia(adaptador("juguete"), caja__limites={"segundos_por_mensaje": 10, "segundos_por_contenedor": 20, "pids": 64})
    rc, salida, _ = correr({"l": adt("JUGUETE-LENTO^2")}, holgado)
    mira("control holgado", evid(salida, "l")["conversion"]["salida"]["estado"], "bundle")


def p14():
    env = cambia(adaptador("juguete"), salida__forma="envuelto",
                 salida__envoltura={"ruta_bundle": ["FhirResource"], "ruta_estado": ["Status"], "estado_ok": "OK"})
    rc, salida, _ = correr({"o": oru("JUGUETE-ENVUELTO")}, env)
    b = evid(salida, "o")["conversion"]["salida"]["bundle"]
    mira("recorte textual", ("1.20" in b, json.loads(b)["resourceType"]), (True, "Bundle"))
    reser = json.dumps(json.loads('{"Status": "OK", "FhirResource": %s}' % b)["FhirResource"], ensure_ascii=False)
    mira("distinto de reserializar", (b != reser, "1.20" in reser), (True, False))
    mira("el juez ve 1.20 (Q-VC-D-5)", cat(juicio(salida)[("propio", "o")]), ("correcto", None))
    rc, salida, _ = correr({"o": oru("JUGUETE-ENVUELTO-FALLO")}, env)
    s = evid(salida, "o")["conversion"]["salida"]
    mira("fallo envuelto", (s["estado"], s["error"]["codigo"], json.loads(s["error"]["texto"])["Status"]), ("error", "Fail", "Fail"))
    rc, salida, _ = correr({"o": oru("JUGUETE-ENVUELTO")})
    mira("forma bundle sobre envuelto", cat(juicio(salida)[("propio", "o")]), ("indeterminado", "lectura"))
    mira("recortar anidado", VC.recortar('{"a": {"b": [1, 2.50]}, "c": 1}', ["a", "b"]), "[1, 2.50]")
    mira("recortar ausente", VC.recortar('{"a": 1}', ["b"]), None)


def p15():
    rc, salida, _ = correr({"g": adt("JUGUETE-GRANDE^4000001")})
    s = evid(salida, "g")["conversion"]["salida"]
    mira("demasiado grande", (s["estado"], s["error"]["codigo"], s["error"]["texto"]), ("error", "demasiado_grande", "4000001 caracteres"))
    rc, salida, _ = correr({"g": adt("JUGUETE-GRANDE^3999999")})
    mira("control 3999999", evid(salida, "g")["conversion"]["salida"]["estado"], "bundle")


SEIS = {"n": adt(), "g": adt("JUGUETE-GENERO"), "e": adt("JUGUETE-ERROR"), "v": adt("JUGUETE-NADA"), "a05": adt(ev="A05"),
        "o": oru()}


def p16():
    rc, salida, _ = correr(SEIS)
    inf = informe(salida)
    mira("categorías", inf["por_corpus"]["propio"]["categorias"],
         {"correcto": 2, "fallo_silencioso": 1, "rechazo_incorrecto": 1, "indeterminado": 1, "fuera_de_alcance": 1})
    vd = inf["mecanismos"]["valor_distinto"]
    mira("valor_distinto", [(x["hecho"], x["n"], bool(x["citas"]), x["clase_cv"]) for x in vd], [("PID-8", 1, True, "sin_contraste")])
    mira("las otras siete, vacías", [k for k, v in inf["mecanismos"].items() if v and k != "valor_distinto"], [])
    mira("rechazos aparte", [x["n"] for x in inf["rechazos"]["incorrectos"]], [1])
    rc, salida, _ = correr(dict(SEIS, g=adt()))
    inf = informe(salida)
    mira("control", (inf["por_corpus"]["propio"]["categorias"]["correcto"], inf["mecanismos"]["valor_distinto"]), (3, []))


def p17():
    import cv3_minimos as MIN
    salida = os.path.join(tmp("salida"), "s")
    ad = VC.leer_adaptador(adaptador("juguete"), AQUI)
    with redirect_stdout(io.StringIO()):
        VC.correr(ad, salida, AQUI, VC.Ejecutor(), {"lab": False, "minimos": True})
    pm = informe(salida)["pares_minimos"]
    d = {x["id"]: x for x in pm["detalle"]}
    mira("M01 y L02", (d["M01-nm-punto-inicial"]["reproduce"], d["L02-estado-civil-a"]["reproduce"]), (True, True))
    mira("n y para quién", (pm["n"], [x["para_conversor"] for x in pm["detalle"]]), (34, [p[1] for p in MIN.PARES]))
    # DV-VC-3: el diseño preveía 2; el Bundle genérico del juguete omite campos y reproduce también los pares de «falta».
    mira("reproducidos (fijado al juguete)", sorted(x["id"] for x in pm["detalle"] if x["reproduce"]),
         ["L01-sin-location", "L02-estado-civil-a", "L03-pv1-10-med", "L08-tm", "L09-obx-11-d", "L10-obr-25-i", "L13-pv1-52",
          "L14-xpn-6-titulo", "L16-cx-4-solo-nombre", "M01-nm-punto-inicial", "M05-clase-b", "M07-oru-sin-pid", "M08-estado-civil-t"])
    mira("reproducidos = la lista", pm["reproducidos"], 13)
    filas = [json.loads(x) for x in open(os.path.join(salida, "juicio.jsonl"), encoding="utf-8")]
    caso = [f for f in filas if f["caso"] == "M01-nm-punto-inicial-caso"][0]
    filas = [dict(f, cuentan=caso["cuentan"]) if f["caso"] == "M01-nm-punto-inicial-control" else f for f in filas]
    mira("control: también en el control, no reproduce",
         {x["id"]: x["reproduce"] for x in VC.pares_minimos(filas)["detalle"]}["M01-nm-punto-inicial"], False)
    rc, salida, _ = correr({"n": adt()}, minimos=True)
    mira("Q-VC-D-3: solo con los dos del estudio", informe(salida)["pares_minimos"]["aplica"], False)


def p18():
    pg = cambia(adaptador("juguete"), invocacion__modo="mensaje", invocacion__contenedor="por_grupo",
                invocacion__plantilla={"regla": "msh9_tipo_evento"},
                invocacion__orden=["python3", "conversor_juguete.py", "--fichero", "{entrada_fichero}", "--salida", "{salida_fichero}"])
    rc, salida, _ = correr(dict(SEIS, sinmsh="PID|1"), pg, ejecutor=VC.Ejecutor())
    inf = informe(salida)
    nj = inf["no_juzgado"]
    mira("fuera de alcance", nj["fuera_de_alcance"], [{"caso": "propio/a05", "msh9": "ADT^A05^ADT_A05"}])
    mira("sin salida", nj["indeterminado"]["sin_salida"], ["propio/v"])
    mira("sin msh", nj["sin_msh"], ["propio/sinmsh.hl7"])
    mira("sin fallo de caja", (nj["sin_evidencia"], rc), ([], 0))
    rc, salida, _ = correr(SEIS, pg, ejecutor=Fallo())
    inf = informe(salida)
    se = inf["no_juzgado"]["sin_evidencia"]
    mira("fallo de caja", ([(x["grupo"], x["casos"]) for x in se], bool(se and se[0]["motivo"]), rc), ([("ORU_R01", ["propio/o"])], True, 4))
    t = inf["totales"]
    mira("cuadran", t["n"], t["juzgados"] + t["no_juzgados"])


class Fallo(VC.Ejecutor if VC else object):
    def _run(self, orden, timeout):
        if any(x.endswith("/o.hl7") for x in orden):
            raise VC.CajaNoDisponible("fallo simulado de la caja")
        return VC.Ejecutor._run(self, orden, timeout)


def p19():
    rc, salida, _ = correr(SEIS)
    inf = informe(salida)
    md = open(os.path.join(salida, "INFORME.md"), encoding="utf-8").read()
    mira("contraste no hecho", (inf["contraste_con_el_proyecto"]["hecho"], VC.FRASE_FIJA in md), (False, True))
    mira("sin_contraste", {x["clase_cv"] for v in inf["mecanismos"].values() for x in v}, {"sin_contraste"})
    mira("comprobar_informe", VC.comprobar_informe(md, inf), [])
    falso = md + "\nSe hallaron 3 discrepancias nuevas y confirmadas.\n"
    mira("control falso", bool(VC.comprobar_informe(falso, inf)), True)
    mira("control ruta", bool(VC.comprobar_informe(md + "\n/home/alguien/x\n", inf)), True)


def p20():
    _, s1, _ = correr(SEIS)
    _, s2, _ = correr(SEIS)
    b = lambda s, f: open(os.path.join(s, f), "rb").read()  # noqa: E731
    mira("INFORME igual", b(s1, "INFORME.json") == b(s2, "INFORME.json"), True)
    mira("juicio igual", b(s1, "juicio.jsonl") == b(s2, "juicio.jsonl"), True)
    c1, c2 = leer_json(os.path.join(s1, "CORRIDA.json")), leer_json(os.path.join(s2, "CORRIDA.json"))
    mira("CORRIDA: solo lo variable", sorted(k for k in c1 if c1[k] != c2[k]), sorted(k for k in VC.CORRIDA_VARIABLE if c1.get(k) != c2.get(k)))
    _, s3, _ = correr(SEIS, cambia(adaptador("juguete"), conversor__version="2"))
    i1, i3 = informe(s1), informe(s3)
    mira("control versión", ([k for k in i1 if i1[k] != i3[k]], [k for k in i1["conversor"] if i1["conversor"][k] != i3["conversor"][k]]),
         (["conversor"], ["version"]))


def p21():
    art = artefactos_ms()
    e = Espia()
    salida = os.path.join(tmp("salida"), "s")
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = VC.main([escribir_ad(adaptador("microsoft")), salida, "--artefactos", art, "--solo-orden", "--sin-minimos"], ejecutor=e)
    out = buf.getvalue()
    mira("solo orden", (rc, e.corridas, os.path.exists(os.path.join(salida, "evidencias"))), (0, [], False))
    mira("imprime la orden", all(x in out for x in ("docker run", "--network none", "-r ADT_A01", "<tin>:/in:ro")), True)
    e = Espia()
    correr({"a": msg()}, adaptador("microsoft"), ejecutor=e, artefactos=art)
    mira("control", len(e.corridas) > 0, True)


def p22():
    _, salida, _ = correr(SEIS)
    antes = open(os.path.join(salida, "INFORME.json"), "rb").read()
    os.remove(os.path.join(salida, "INFORME.json"))
    e = Espia()
    with redirect_stdout(io.StringIO()):
        rc = VC.main([escribir_ad(adaptador("juguete")), salida, "--artefactos", AQUI, "--desde-evidencias"], ejecutor=e)
    mira("desde evidencias", (rc, e.corridas, open(os.path.join(salida, "INFORME.json"), "rb").read() == antes), (0, [], True))
    vacia = os.path.join(tmp("vacia"), "s")
    os.makedirs(vacia)
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = VC.main([escribir_ad(adaptador("juguete")), vacia, "--artefactos", AQUI, "--desde-evidencias"], ejecutor=e)
    mira("sin evidencias", (rc, "evidencias" in buf.getvalue()), (1, True))
    ocupada = tmp("ocupada")                                           # revisión de VC4, hallazgo 6: un rechazo de entrada
    open(os.path.join(ocupada, "mio.txt"), "w").write("no es de la herramienta")
    with redirect_stdout(io.StringIO()):
        rc = VC.main([escribir_ad(adaptador("juguete")), ocupada, "--artefactos", AQUI, "--sin-corpus-lab", "--sin-minimos"])
    mira("salida ocupada: 2 y sin tocar", (rc, os.listdir(ocupada)), (2, ["mio.txt"]))


def docker_falso(contesta):
    d = tmp("bin")
    with open(os.path.join(d, "docker"), "w") as g:
        g.write("#!/bin/sh\n" + contesta)
    os.chmod(os.path.join(d, "docker"), 0o755)
    return d


def con_path(path, f):
    viejo = os.environ.get("PATH", "")
    os.environ["PATH"] = path
    try:
        return f()
    finally:
        os.environ["PATH"] = viejo


def p23():
    art = artefactos_ms()
    ad = adaptador("microsoft")
    sin_imagen = docker_falso('case "$1" in version) echo 27.0.0;; image) exit 1;; *) exit 0;; esac\n')
    rc, salida, out = con_path(sin_imagen + os.pathsep + "/usr/bin:/bin", lambda: correr({"a": msg()}, ad, ejecutor=VC.Ejecutor(), artefactos=art))
    mira("imagen ausente", (rc, "docker pull mcr.microsoft.com/dotnet/runtime:6.0" in out, os.path.exists(os.path.join(salida, "evidencias"))),
         (3, True, False))
    vacio = tmp("binvacio")
    rc, _, _ = con_path(vacio, lambda: correr({"a": msg()}, ad, ejecutor=VC.Ejecutor(), artefactos=art))
    mira("sin docker", rc, 3)
    dig = "mcr.microsoft.com/dotnet/runtime@sha256:" + "b" * 64
    con_imagen = docker_falso('case "$1" in version) echo 27.0.0;; image) echo %s;; *) exit 0;; esac\n' % dig)
    rc, salida, _ = con_path(con_imagen + os.pathsep + "/usr/bin:/bin", lambda: correr({"a": msg()}, ad, ejecutor=VC.Ejecutor(), artefactos=art))
    mira("con imagen", leer_json(os.path.join(salida, "CORRIDA.json"))["imagen_digest"], "sha256:" + "b" * 64)
    otro = cambia(ad, caja__imagen_digest="sha256:" + "c" * 64)
    rc, _, _ = con_path(con_imagen + os.pathsep + "/usr/bin:/bin", lambda: correr({"a": msg()}, otro, ejecutor=VC.Ejecutor(), artefactos=art))
    mira("digest distinto (Q-VC-D-4)", rc, 3)


def p24():
    _, salida, _ = correr(SEIS)
    filas = [json.loads(x) for x in open(os.path.join(salida, "juicio.jsonl"), encoding="utf-8")]
    c = VC.comparar(filas, copy.deepcopy(filas))
    mira("igual", (c["diferencias"], c["solo_en_corrida"], c["solo_en_referencia"]), ([], [], []))
    ref = copy.deepcopy(filas)
    ref[0]["subtipo"] = "otro"
    mira("subtipo distinto", [d["caso"] for d in VC.comparar(filas, ref)["diferencias"]], [filas[0]["caso"]])
    ref = copy.deepcopy(filas)
    for h in ref[1]["cuentan"]:
        h["que"] = ["otro texto"]
    mira("el texto no cuenta (Q-VC-D-7)", VC.comparar(filas, ref)["diferencias"], [])
    ref = copy.deepcopy(filas)
    g = [x for x in ref if x["caso"] == "g"][0]
    g["cuentan"] = [dict(h, subtipo="dato_perdido") for h in g["cuentan"]]
    mira("los hallazgos sí (Q-VC-D-7)", [d["caso"] for d in VC.comparar(filas, ref)["diferencias"]], ["g"])
    mira("falta en la referencia", VC.comparar(filas, filas[1:])["solo_en_corrida"], [[filas[0]["conversor"], filas[0]["corpus"], filas[0]["caso"]]])
    ref_f = os.path.join(tmp("ref"), "ref.jsonl")
    with open(ref_f, "w", encoding="utf-8") as g_:
        for x in filas[1:] + [dict(filas[0], categoria="otra")]:
            g_.write(json.dumps(x, ensure_ascii=False) + "\n")
    rc, _, _ = correr(SEIS, args=["--comparar", ref_f])
    mira("salida 5", rc, 5)


def p25():
    import correr_conversor as CC
    art_ms, art_lfh = artefactos_ms(), artefactos_lfh()
    ms = VC.leer_adaptador(adaptador("microsoft"), art_ms)
    lfh = VC.leer_adaptador(adaptador("linuxforhealth"), art_lfh)
    o = VC.orden_caja(ms, 1, "ADT_A01", "/T/in", "/T/out", art_ms, ["a.hl7"])
    bucle = ('for f in /in/*.hl7; do b=$(basename "$f" .hl7); dotnet /app/Microsoft.Health.Fhir.Liquid.Converter.Tool.dll convert '
             '-d /tpl -r %s -n "$f" -f "/salida/$b.json" > "/salida/$b.log" 2>&1; echo $? > "/salida/$b.rc"; done' % "ADT_A01")
    mira("microsoft: bucle del estudio", o[-1], bucle)
    mira("microsoft: montajes", [v.split(":", 1)[1] for v in (o[i + 1] for i in range(len(o)) if o[i] == "-v")],
         ["/app:ro", "/tpl:ro", "/in:ro", "/salida"])
    mira("microsoft: imagen y entorno", (CC.RUNTIME_MS in o, indice_secuencia(o, ["-e", "DOTNET_CLI_TELEMETRY_OPTOUT=1"]) > 0), (True, True))
    mira("microsoft: la caja del estudio", indice_secuencia(o, CC.CAJA), 2)
    o = VC.orden_caja(lfh, 1, None, "/T/in", "/T/out", art_lfh, None)
    mira("lfh: orden", o[-7:], ["maven:3.9-eclipse-temurin-11", "java", "-cp", "/clases:/lib2/*", "Arnes", "/in", "/salida"])
    mira("lfh: montajes", [v.split(":", 1)[1] for v in (o[i + 1] for i in range(len(o)) if o[i] == "-v")],
         ["/lib2:ro", "/clases:ro", "/in:ro", "/salida"])
    otro = VC.leer_adaptador(cambia(adaptador("linuxforhealth"), invocacion__modo="mensaje", invocacion__contenedor="por_mensaje",
                                    invocacion__orden=["java", "-cp", "/clases:/lib2/*", "Arnes", "{entrada_fichero}", "{salida_dir}"]), art_lfh)
    o2 = VC.orden_caja(otro, 1, None, "/T/in", "/T/out", art_lfh, ["a.hl7"])
    mira("control: por mensaje", (o2[-2:], o2 != o), (["/in/a.hl7", "/salida"], True))


def p26():
    art = artefactos_ms()
    ms = VC.leer_adaptador(adaptador("microsoft"), art)
    o = VC.orden_caja(ms, 1, "ADT_A01", "/T/in", "/T/out", art, ["a.hl7"])
    mira("telemetría y HOME", (indice_secuencia(o, ["-e", "DOTNET_CLI_TELEMETRY_OPTOUT=1"]) > 0, indice_secuencia(o, ["-e", "HOME=/tmp"]) > 0),
         (True, True))
    mira("sin memoria por omisión (Q-VC-D-6)", any(x.startswith("--memory") for x in o), False)
    m = VC.leer_adaptador(cambia(adaptador("microsoft"), caja__limites__memoria_mb=2048), art)
    mira("memoria declarada", indice_secuencia(VC.orden_caja(m, 1, "ADT_A01", "/T/in", "/T/out", art, ["a.hl7"]), ["--memory", "2048m"]) > 0, True)
    mira("HOME reservado", codigo(VC.leer_adaptador, cambia(adaptador("microsoft"), caja__entorno={"HOME": "/x"}), art), "entorno_reservado")
    q = VC.leer_adaptador(cambia(adaptador("microsoft"), caja__entorno={"X": "con 'comillas' y espacios"}), art)
    o = VC.orden_caja(q, 1, "ADT_A01", "/T/in", "/T/out", art, ["a.hl7"])
    mira("un solo argumento", indice_secuencia(o, ["-e", "X=con 'comillas' y espacios"]) > 0, True)


PRUEBAS = [p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23,
           p24, p25, p26]


def main():
    rojo = sys.argv[1:] == ["rojo"]
    if VC is None and not rojo:
        print("  verificar_conversor no se importa: %s" % ERROR_IMPORTACION)
    for p in PRUEBAS:
        grupo[0] = "P-VC-%d" % int(p.__name__[1:])
        try:
            p()
        except Exception as ex:                                             # en rojo, lo esperado es que el módulo no exista
            FALLAN.add(grupo[0])
            if not rojo:
                print("  EXCEPCIÓN %s: %s" % (grupo[0], "".join(traceback.format_exception(type(ex), ex, ex.__traceback__)[-3:]).strip()[:600]))
                mal.append(grupo[0])
    shutil.rmtree(RAIZ, ignore_errors=True)
    if rojo:
        print("PRUEBAS VC (rojo): fallan %d de %d %s" % (len(FALLAN), len(PRUEBAS), "(TODAS)" if len(FALLAN) == len(PRUEBAS) else ""))
        return 0 if len(FALLAN) == len(PRUEBAS) else 1
    print("PRUEBAS VC: %s (%d comprobaciones, %d pruebas)" % ("TODO BIEN" if not mal else "%d MAL" % len(mal), n_ok[0], len(PRUEBAS)))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
