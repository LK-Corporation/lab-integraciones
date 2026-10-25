#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 21 (cv/ar/diseno-ar-fable.md §7; decisiones de Jev en cv/ar/decision-jev-qar.md): P-AR-1..13, el aparato que compara
LinuxForHealth en lote con LinuxForHealth mensaje a mensaje. Corren sin Docker: el conversor de juguete (con su directiva
JUGUETE-ARRASTRE), un ejecutor espía copiado de cv/prueba_vc.py y filas de juicio fabricadas. Cada prueba cambia una sola cosa y
lleva su control negativo.

Antes del código fallaban las doce primeras: el adaptador mensaje, arrastre.py y control_ar.py no existían. P-AR-13 llegó con
DV-AR-11, y la parte de --sello de P-AR-12 con DV-AR-12, las dos en rojo antes de su arreglo.
  python3 cv/ar/prueba_ar.py          -> TODO BIEN si no hay ningún MAL
  python3 cv/ar/prueba_ar.py rojo     -> sale 0 solo si fallan todas"""
import copy
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import traceback
from contextlib import redirect_stdout

AR_D = os.path.dirname(os.path.abspath(__file__))
CVD = os.path.dirname(AR_D)
FASE = os.path.dirname(CVD)
sys.path[:0] = [AR_D, CVD, FASE]
sys.argv_guardado, sys.argv = sys.argv, ["x", "--silencio"]
import verificar_conversor as VC  # noqa: E402
from prueba_conversion import msg, oru_msg  # noqa: E402
try:
    import arrastre as AR  # noqa: E402
except ImportError as ex:                                                   # en rojo: el módulo no existe todavía
    AR, ERROR_AR = None, ex
try:
    import control_ar as CA  # noqa: E402
except ImportError as ex:
    CA, ERROR_CA = None, ex
sys.argv = sys.argv_guardado

mal, n_ok, grupo = [], [0], [None]
FALLAN = set()
RAIZ = tempfile.mkdtemp(prefix="prueba_ar_")
DIGEST = "sha256:7bb84a451705605a47d24eb844d4d9ab03e33e131a507db76aafe25db3907f64"
RXA17 = ["RXA-17", "fidelidad", "dato_perdido"]
PID8 = ["PID-8", "fidelidad", "dato_perdido"]
IN = "/in"                                                                  # compuesto, para la guarda de higiene


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
    return leer_json(os.path.join(CVD, "adaptadores", nombre + ".json"))


def cambia(d, **cambios):
    """Copia de d con cambios por ruta con «__»; el valor BORRA quita la clave (como en cv/prueba_vc.py)."""
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


def adt(directiva="JUGUETE-NOMINAL", ev="A01"):
    return con_msh8(msg(ev), directiva)


def oru(directiva="JUGUETE-NOMINAL"):
    return con_msh8(oru_msg(), directiva)


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


def juguete_mensaje():
    return cambia(adaptador("juguete"), invocacion__modo="mensaje", invocacion__contenedor="por_mensaje",
                  invocacion__orden=["python3", "conversor_juguete.py", "--fichero", "{entrada_fichero}", "--salida", "{salida_fichero}"])


class Espia(VC.Ejecutor):
    """Registra las órdenes sin correrlas, como el de cv/prueba_vc.py, y guarda lo que hay en la carpeta montada en /in."""
    def __init__(self, digest="maven:3.9-eclipse-temurin-11@" + DIGEST):
        self.corridas, self.consultas, self.digest, self.en_in = [], [], digest, []
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
        for i, x in enumerate(orden):
            if x == "-v" and orden[i + 1].endswith(":" + IN + ":ro"):
                self.en_in.append(sorted(os.listdir(orden[i + 1][:-len(":" + IN + ":ro")])))
        return 0, ""


def correr_vc(argv, ejecutor=None):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = VC.main(argv, ejecutor=ejecutor)
    return rc, buf.getvalue()


def correr_juguete(mensajes, ad, cid="juguete"):
    salida = os.path.join(tmp("salida"), "s")
    rc, _ = correr_vc([escribir_ad(ad), salida, "--artefactos", CVD, "--sin-corpus-lab", "--sin-minimos", "--sin-sensibilidad",
                       "--json-solo", "--corpus", corpus_propio(mensajes)])
    return rc, salida


def fila(corpus, caso, cuentan=(), estado="bundle", categoria=None, subtipo=None, que=None, conversor="linuxforhealth"):
    cu = [{"hecho": h, "clase": c, "subtipo": s, "que": [que or "%s: %s" % (h, s)]} for h, c, s in cuentan]
    if categoria is None:
        categoria, subtipo = ("fallo_silencioso", "convertido") if cu else ("correcto", None)
    return {"conversor": conversor, "corpus": corpus, "caso": caso, "estado": estado, "categoria": categoria, "subtipo": subtipo,
            "cuentan": cu}


def escribir_juicio(filas, carpeta=None):
    d = carpeta or tmp("corrida")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "juicio.jsonl"), "w", encoding="utf-8") as g:
        for f in filas:
            g.write(json.dumps(f, ensure_ascii=False) + "\n")
    return d


def casos_de(comp, clave):
    return sorted((x["corpus"], x["caso"]) for x in comp[clave])


# ---------------------------------------------------------------------------- P-AR-1..12
def p01():
    art = artefactos_lfh()
    ruta = os.path.join(CVD, "adaptadores", "linuxforhealth-mensaje.json")
    m = VC.leer_adaptador(ruta, art)
    lo = VC.leer_adaptador(os.path.join(CVD, "adaptadores", "linuxforhealth.json"), art)
    mira("identidad", (m["id"], m["invocacion"]["modo"], m["invocacion"]["contenedor"], m["caja"]["imagen_digest"]),
         ("linuxforhealth", "mensaje", "por_mensaje", DIGEST))
    mira("huellas iguales al lote", (VC.huella(m, art), VC.huella_con_nombres(m, art)), (VC.huella(lo, art), VC.huella_con_nombres(lo, art)))
    mira("bloques iguales", (m["conversor"], m["salida"], cambia(m["caja"], imagen_digest=None)), (lo["conversor"], lo["salida"], lo["caja"]))
    o = VC.orden_caja(m, 1, None, "/T/in", "/T/out", art, ["a.hl7"])
    mira("orden", o[-4:], ["Arnes", IN, "/salida", IN + "/a.hl7"])
    ol = VC.orden_caja(lo, 1, None, "/T/in", "/T/out", art, ["a.hl7"])
    corte = lambda x: x[:x.index("--")]  # noqa: E731
    mira("misma caja que el lote", [x.replace("vc-linuxforhealth-1", "N") for x in corte(o)],
         [x.replace("vc-linuxforhealth-1", "N") for x in corte(ol)])
    crudo = leer_json(ruta)
    try:
        VC.leer_adaptador(cambia(crudo, invocacion__modo="lote", invocacion__contenedor="BORRA"), art)
        mira("en lote", "aceptado", "lote_marcador")
    except VC.ErrorAdaptador as ex:
        mira("en lote", ex.codigo, "lote_marcador")
    try:
        VC.leer_adaptador(cambia(crudo, invocacion__orden=crudo["invocacion"]["orden"][:-1]), art)
        mira("sin fichero", "aceptado", "mensaje_sin_fichero")
    except VC.ErrorAdaptador as ex:
        mira("sin fichero", ex.codigo, "mensaje_sin_fichero")
    open(os.path.join(art, "lfh/lib/x.txt"), "a").write("!")
    mira("un byte en lib cambia la huella", VC.huella(m, art) != VC.huella(lo, artefactos_lfh()), True)


def p02():
    art = artefactos_lfh()
    ruta = os.path.join(CVD, "adaptadores", "linuxforhealth-mensaje.json")
    c = corpus_propio({"a1": adt(), "a2": adt(ev="A03"), "o1": oru()})
    es = Espia()
    rc, _ = correr_vc([ruta, os.path.join(tmp("s"), "s"), "--artefactos", art, "--sin-corpus-lab", "--sin-minimos", "--json-solo",
                       "--corpus", c], es)
    mira("tres corridas", len(es.corridas), 3)
    mira("un fichero en cada /in", es.en_in, [["a1.hl7"], ["a2.hl7"], ["o1.hl7"]])
    mira("el último argumento", [o[-1] for o in es.corridas], [IN + "/a1.hl7", IN + "/a2.hl7", IN + "/o1.hl7"])
    es2 = Espia()
    correr_vc([os.path.join(CVD, "adaptadores", "linuxforhealth.json"), os.path.join(tmp("s"), "s"), "--artefactos", art,
               "--sin-corpus-lab", "--sin-minimos", "--json-solo", "--corpus", c], es2)
    mira("control: el lote, una corrida con tres", (len(es2.corridas), es2.en_in), (1, [["a1.hl7", "a2.hl7", "o1.hl7"]]))
    s = os.path.join(tmp("s"), "s")
    correr_vc([ruta, s, "--artefactos", art, "--sin-corpus-lab", "--json-solo"], Espia())
    mira("con el id del estudio entran los 68 mínimos", leer_json(os.path.join(s, "CORRIDA.json"))["corpus"]["n"]["minimos"], 68)
    s2 = os.path.join(tmp("s"), "s")
    otro = escribir_ad(cambia(leer_json(ruta), id="linuxforhealth-mensaje"))
    correr_vc([otro, s2, "--artefactos", art, "--sin-corpus-lab", "--json-solo"], Espia())
    mira("control: con otro id, ninguno", leer_json(os.path.join(s2, "CORRIDA.json"))["corpus"]["n"]["minimos"], 0)
    a = [json.loads(x) for x in open(os.path.join(s2, "juicio.jsonl"), encoding="utf-8")]
    a += [fila("propio", "z", conversor="linuxforhealth-mensaje")]
    c_ = VC.comparar(a, [fila("propio", "z")])
    mira("otro id no casa nada", (c_["diferencias"], len(c_["solo_en_referencia"])), ([], 1))


def p03():
    L1 = [fila("adt", "A1"), fila("adt", "A2", [("PV1-52", "fidelidad", "dato_perdido")]), fila("adt", "A3"), fila("oru", "O1"),
          fila("oru", "O2"), fila("vxu", "VXU-B18", [tuple(RXA17)], que="manufacturer"), fila("muestras", "MU1")]
    L2 = copy.deepcopy(L1)
    L2[2] = fila("adt", "A3", [("PID-8", "fidelidad", "valor_distinto")])
    M1 = [fila("adt", "A1"), fila("adt", "A2"), fila("adt", "A3"), fila("oru", "O1"), fila("oru", "O2"), fila("vxu", "VXU-B18"),
          fila("muestras", "MU1", estado="sin_respuesta", categoria="indeterminado", subtipo="sin_salida")]
    M2 = copy.deepcopy(M1)
    M2[3] = fila("oru", "O1", [("OBX-5", "fidelidad", "valor_distinto")])
    del M2[4]
    c = AR.comparar_juicios(L1, L2, M1, M2)
    mira("diferentes", casos_de(c, "diferencias"), [("adt", "A2")])
    mira("solo en lote", c["diferencias"][0]["solo_en_lote"], [["PV1-52", "fidelidad", "dato_perdido"]])
    mira("solo en mensaje", c["diferencias"][0]["solo_en_mensaje"], [])
    mira("no deterministas", casos_de(c, "no_deterministas"), [("adt", "A3"), ("oru", "O1")])
    mira("sin par y caja", (casos_de(c, "sin_par"), casos_de(c, "caja")), ([("oru", "O2")], [("muestras", "MU1")]))
    mira("n sin vxu", (c["n"]["comparados"], c["n"]["iguales"], c["n"]["diferentes"], c["n"]["no_deterministas"],
                       c["n"]["sin_par"], c["n"]["caja"]), (6, 1, 1, 2, 1, 1))
    mira("vxu es control", c["control_vxu"]["diferentes"], ["VXU-B18"])
    mira("por corpus cuadra", sum(v["n"] for v in c["por_corpus"].values()), c["n"]["comparados"])
    L = [f for f in L1 if f["corpus"] != "muestras"]
    M = [f for f in M1 if f["corpus"] != "muestras"]
    c2 = AR.comparar_juicios(L, L, M, M)
    vc = sorted((d["corpus"], d["caso"]) for d in VC.comparar(M, L)["diferencias"])
    mira("como VC.comparar", sorted(casos_de(c2, "diferencias") + [("vxu", x) for x in c2["control_vxu"]["diferentes"]]), vc)
    c3 = AR.comparar_juicios(L1, L1, L1, L1)
    mira("control: cuatro iguales", (c3["n"]["diferentes"], c3["n"]["no_deterministas"], c3["n"]["iguales"]), (0, 0, 6))
    Mq = copy.deepcopy(L1)
    Mq[1]["cuentan"][0]["que"] = ["otro texto"]
    mira("control: solo el texto", AR.comparar_juicios(L1, L1, Mq, Mq)["n"]["diferentes"], 0)


def bundle(uuids, genero="female", extra=False, fecha="1980-02-15", orden=1):
    u1, u2 = uuids
    es = [{"fullUrl": "urn:uuid:" + u1, "resource": {"resourceType": "Patient", "id": u1, "gender": genero, "birthDate": fecha,
                                                      "managingOrganization": {"reference": "Organization/" + u2}}},
          {"fullUrl": "urn:uuid:" + u2, "resource": {"resourceType": "Organization", "id": u2, "name": "H"}}]
    if extra:
        es.append({"fullUrl": "urn:uuid:" + u2, "resource": {"resourceType": "Observation", "id": u2, "status": "final"}})
    return {"resourceType": "Bundle", "id": "1792881592720447000." + u1, "type": "collection", "entry": es[::orden]}


def p04():
    A = ("3deb314c-b7f5-4110-a0ba-71c52aaaaaaa", "11111111-2222-3333-4444-555555555555")
    B = ("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", "99999999-8888-7777-6666-555555555555")
    mira("iguales salvo UUID", AR.multiset_bundle(bundle(A)) == AR.multiset_bundle(bundle(B)), True)
    mira("permutadas", AR.multiset_bundle(bundle(A)) == AR.multiset_bundle(bundle(B, orden=-1)), True)
    mira("texto o dict", AR.multiset_bundle(json.dumps(bundle(A))) == AR.multiset_bundle(bundle(A)), True)
    mira("un gender", AR.diff_bundles(bundle(A), bundle(B, genero="male")), [("Patient", "gender", "female", "male")])
    mira("con máscara", AR.diff_bundles(bundle(A), bundle(B, genero="male"), {("Patient", "gender")}), [])
    d = AR.diff_bundles(bundle(A), bundle(B, extra=True))
    mira("un recurso de más", [x[:2] for x in d], [("Observation", "<recurso>")])
    mira("control: la fecha sin máscara", AR.diff_bundles(bundle(A), bundle(B, fecha="1980-02-16")),
         [("Patient", "birthDate", "1980-02-15", "1980-02-16")])
    mira("control: la máscara no tapa otra ruta",
         AR.diff_bundles(bundle(A), bundle(B, fecha="1980-02-16"), {("Patient", "gender")}) != [], True)


def vl11(lote_b=(RXA17,), que="Immunization.manufacturer: no está", mensaje_a=(), control_b=()):
    lote = {"1-L11a": fila("propio", "1-L11a"), "2-L11b": fila("propio", "2-L11b", [tuple(x) for x in lote_b], que=que)}
    mensaje = {"1-L11a": fila("propio", "1-L11a", [tuple(x) for x in mensaje_a]), "2-L11b": fila("propio", "2-L11b")}
    control = {"1-L11b": fila("propio", "1-L11b", [tuple(x) for x in control_b])}
    return lote, mensaje, control


def p05():
    mira("sale", AR.positivo_sale(*vl11())[0], True)
    mira("control: también en 1-L11a", AR.positivo_sale(*vl11(mensaje_a=(PID8,)))[0], False)
    mira("control: otro hecho", AR.positivo_sale(*vl11(lote_b=(PID8,)))[0], False)
    mira("control: sin diferencia", AR.positivo_sale(*vl11(lote_b=()))[0], False)
    mira("control: sin manufacturer en el texto", AR.positivo_sale(*vl11(que="RXA-17: otra cosa"))[0], False)
    mira("control: el control distinto del mensaje", AR.positivo_sale(*vl11(control_b=(PID8,)))[0], False)
    mira("control: algo más en la diferencia", AR.positivo_sale(*vl11(lote_b=(RXA17, PID8)))[0], False)


def p06():
    nom = {"1-n1": adt(), "2-arr": adt("JUGUETE-ARRASTRE"), "3-n3": adt(), "4-n4": adt()}
    _, L = correr_juguete(nom, adaptador("juguete"))
    _, M = correr_juguete(nom, juguete_mensaje())
    fl, fm = AR.filas(L), AR.filas(M)
    c = AR.comparar_juicios(fl, fl, fm, fm)
    mira("diferentes", casos_de(c, "diferencias"), [("propio", "3-n3"), ("propio", "4-n4")])
    mira("solo en lote", [d["solo_en_lote"] for d in c["diferencias"]], [[PID8], [PID8]])
    cat = {(f["caso"]): f["categoria"] for f in fl}
    mira("el disparador, correcto en los dos modos", (cat["2-arr"], {f["caso"]: f["categoria"] for f in fm}["2-arr"]), ("correcto", "correcto"))
    sin = dict(nom, **{"2-arr": adt()})
    _, L2 = correr_juguete(sin, adaptador("juguete"))
    mira("control: sin la directiva", AR.comparar_juicios(AR.filas(L2), AR.filas(L2), fm, fm)["n"]["diferentes"], 0)
    dos = dict(nom, **{"2-arr": adt("JUGUETE-ARRASTRE^2")})
    _, L3 = correr_juguete(dos, adaptador("juguete"))
    mira("control: ^2 con una sola", AR.comparar_juicios(AR.filas(L3), AR.filas(L3), fm, fm)["n"]["diferentes"], 0)


def p07():
    ad_l, ad_m = escribir_ad(adaptador("juguete")), escribir_ad(juguete_mensaje())
    textos = {"n1": adt(), "n2": adt(), "ARR": adt("JUGUETE-ARRASTRE"), "n3": adt(), "n4": adt(), "n5": adt(),
              "A1": adt("JUGUETE-ARRASTRE^2"), "A2": adt("JUGUETE-ARRASTRE^2")}
    sec, solo = AR.hacer_corredores(ad_l, ad_m, CVD, textos, tmp("trabajo"))
    P = ["n1", "n2", "ARR", "n3", "n4"]
    vl, vm = sec(P + ["n5"])["n5"], solo("n5")
    mira("referencias distintas", vl != vm, True)
    r = AR.aislar("n5", P, vl, vm, sec, solo)
    mira("arrastre", (r["tipo"], r["culpable"], r["secuencia_minima"]), ("arrastre", "ARR", ["ARR", "n5"]))
    mira("≤ 12 corridas", len(r["registro"]) <= 12, True)
    mira("repeticiones 3 y 3", (len(r["repeticiones"]["secuencia"]), len(r["repeticiones"]["solo"])), (3, 3))
    r2 = AR.aislar("n2", ["n1"], vl, vm, sec, solo)
    mira("el prefijo no reproduce", r2["tipo"], "otra_causa")
    P2 = ["A1", "n2", "A2", "n3", "n4"]
    vl2 = sec(P2 + ["n5"])["n5"]
    r3 = AR.aislar("n5", P2, vl2, vm, sec, solo)
    mira("estado acumulado, por poda", (r3["tipo"], r3["secuencia_minima"]), ("arrastre", ["A1", "A2", "n5"]))
    r4 = AR.aislar("n5", P, vl, vm, sec, solo, presupuesto=3)
    mira("tope", (r4["tipo"], len(r4["registro"]) > 0), ("no_aislada", True))
    r5 = AR.aislar("n5", P, vm, vm, sec, solo)
    mira("control: igual no se adjudica", (r5["tipo"], r5["registro"]), ("igual", []))


def p08():
    mira("arrastre", AR.adjudicar_caso("a", "a", "b", "b", {"tipo": "arrastre"}), "arrastre")
    mira("lo que diga el aislamiento", AR.adjudicar_caso("a", "a", "b", "b", {"tipo": "otra_causa"}), "otra_causa")
    mira("no determinista en lote", AR.adjudicar_caso("a", "c", "b", "b", {"tipo": "arrastre"}), "no_determinismo")
    mira("no determinista en mensaje", AR.adjudicar_caso("a", "a", "b", "c", None), "no_determinismo")
    mira("igual", AR.adjudicar_caso("a", "a", "a", "a", None), "igual")
    mira("control: diferente sin aislar", AR.adjudicar_caso("a", "a", "b", "b", None), "diferente")
    r = lambda n: {"veredicto": [["adt", "A%d" % i] for i in range(n)]}  # noqa: E731
    mira("9 de 436 al 2 %", AR.regla_parada(r(9), r(0), 436, 0.02), True)
    mira("8 de 436 al 2 %", AR.regla_parada(r(8), r(0), 436, 0.02), False)
    mira("los mismos casos en los dos modos cuentan una vez", AR.regla_parada(r(8), r(8), 436, 0.02), False)
    mira("Jev: umbral cero, uno para", AR.regla_parada(r(0), r(1), 436, AR.UMBRAL), True)
    mira("Jev: umbral cero, ninguno sigue", AR.regla_parada(r(0), r(0), 436, AR.UMBRAL), False)


def corrida_estudio(cid):
    """Una corrida de juguete con el id de un conversor del estudio (entran los 68 mínimos) y su corpus propio relabelado como adt."""
    ad = cambia(adaptador("juguete"), id=cid)
    salida = os.path.join(tmp("corrida"), cid)
    correr_vc([escribir_ad(ad), salida, "--artefactos", CVD, "--sin-corpus-lab", "--sin-sensibilidad", "--json-solo",
               "--corpus", corpus_propio({"x1": adt(), "x2": adt("JUGUETE-GENERO"), "x3": oru()})])
    ev = os.path.join(salida, "evidencias", cid)
    os.rename(os.path.join(ev, "propio"), os.path.join(ev, "adt"))
    fs = [json.loads(x) for x in open(os.path.join(salida, "juicio.jsonl"), encoding="utf-8")]
    for f in fs:
        f["corpus"] = "adt" if f["corpus"] == "propio" else f["corpus"]
    escribir_juicio(fs + [fila("vxu", "VXU-B01", conversor=cid)], salida)
    return salida


def p09():
    ms, lfh = corrida_estudio("microsoft"), corrida_estudio("linuxforhealth")
    arbol = tmp("arbol")
    AR.ensamblar(arbol, {"microsoft": ms, "linuxforhealth": lfh})
    mira("evidencias sin vxu ni mínimos", sorted(os.listdir(os.path.join(arbol, "evidencias", "linuxforhealth"))), ["adt"])
    mira("68 mínimos por conversor", [len(os.listdir(os.path.join(arbol, "minimos", c))) for c in ("microsoft", "linuxforhealth")], [68, 68])
    js = [json.loads(x) for x in open(os.path.join(arbol, "juicio.jsonl"), encoding="utf-8")]
    mira("juicio filtrado", sorted({(f["conversor"], f["corpus"]) for f in js}), [("linuxforhealth", "adt"), ("microsoft", "adt")])
    cl, mi = AR.juzgar_arbol(arbol)
    mira("los dos corren", (mi["de"], "frase" in cl), (34, True))
    pub = leer_json(os.path.join(CVD, "CLASES-CV3.json"))
    otra = copy.deepcopy(pub)
    for x in otra["clases"]:
        if x["id"] == "L-15":
            x["casos"]["oru"] = 1
    otra["frase"]["N_nuevas_confirmadas"] = 14
    d = AR.diferencias_cifras({"clases": pub}, {"clases": otra})
    mira("dos filas", [x["cifra"] for x in d], ["clases.L-15.casos.oru", "frase.N_nuevas_confirmadas"])
    mira("con su sitio", all(x["donde_se_publica"] for x in d), True)
    mira("control: copias idénticas", AR.diferencias_cifras({"clases": pub}, {"clases": copy.deepcopy(pub)}), [])


def control_md(k=0, nd=0, cifras=None):
    difs = [{"corpus": "adt", "caso": "A%02d" % i, "solo_en_lote": [PID8], "solo_en_mensaje": []} for i in range(k)]
    return {"n": 436, "juez": "b" * 64, "conversor": "ac41f71b",
            "comparacion": {"n": {"comparados": 436, "iguales": 436 - k - nd, "diferentes": k, "no_deterministas": nd, "sin_par": 0,
                                  "caja": 0},
                            "por_corpus": {"adt": {"n": 263}, "oru": {"n": 40}, "muestras": {"n": 65}, "minimos": {"n": 68}},
                            "diferencias": difs, "no_deterministas": [{"corpus": "oru", "caso": "B%02d" % i} for i in range(nd)],
                            "control_vxu": {"diferentes": ["VXU-B%02d" % i for i in range(18, 41)]}},
            "adjudicacion": [{"corpus": "adt", "caso": d["caso"], "tipo": "arrastre", "secuencia_minima": ["X", d["caso"]]} for d in difs],
            "cifras": cifras, "ruido": {"lote": {"veredicto": []}, "mensaje": {"veredicto": []}},
            "positivo": {"pasa_vl11": True, "pasa_vxu": True}}


def p10():
    md = AR.resultado_md(control_md())
    mira("frase con 0", "Convertidos mensaje a mensaje, los 436 casos del estudio dan los mismos veredictos que en lote" in md, True)
    md3 = AR.resultado_md(control_md(3, cifras=[{"cifra": "frase.N_nuevas_confirmadas", "lote": 15, "mensaje": 14, "publicado": 15,
                                                 "donde_se_publica": ["RESULTADO-CONVERSORES.md"]}]))
    mira("frase con 3", ("cambian 3 casos de 436, por arrastre de estado" in md3, "frase.N_nuevas_confirmadas" in md3), (True, True))
    mira("sin rutas de máquina", (VC.RUTA_MAQUINA.search(md), VC.RUTA_MAQUINA.search(md3)), (None, None))
    mira("vxu no entra en N", ("476" in md, "VXU" in md), (False, True))
    mira("no deterministas", "2 no deterministas" in AR.resultado_md(control_md(nd=2)), True)
    try:
        AR.resultado_md(control_md(3))
        mira("control: K > 0 sin cifras", "escrito", "excepción")
    except ValueError:
        mira("control: K > 0 sin cifras", "excepción", "excepción")


def prevision(d):
    p = {k: 1 for k in AR.CLAVES_PREVISION}
    open(os.path.join(d, "PREVISION-AR.json"), "w", encoding="utf-8").write(json.dumps(p))
    sha = hashlib.sha256(open(os.path.join(d, "PREVISION-AR.json"), "rb").read()).hexdigest()
    open(os.path.join(d, "SELLO-AR.txt"), "w", encoding="utf-8").write("# sello\n%s  PREVISION-AR.json\n" % sha)
    return p


def p11():
    d = tmp("sello")
    p = prevision(d)
    pj, st = os.path.join(d, "PREVISION-AR.json"), os.path.join(d, "SELLO-AR.txt")
    mira("cuadra", AR.comprobar_sello(pj, st, d), True)
    open(pj, "a").write(" ")
    mira("control: un byte", AR.comprobar_sello(pj, st, d), False)
    d2 = tmp("sello")
    prevision(d2)
    q = dict(p)
    q.pop("umbral_q_ar_d_1")
    open(os.path.join(d2, "PREVISION-AR.json"), "w", encoding="utf-8").write(json.dumps(q))
    sha = hashlib.sha256(open(os.path.join(d2, "PREVISION-AR.json"), "rb").read()).hexdigest()
    open(os.path.join(d2, "SELLO-AR.txt"), "w", encoding="utf-8").write("%s  PREVISION-AR.json\n" % sha)
    mira("control: una clave de menos", AR.comprobar_sello(os.path.join(d2, "PREVISION-AR.json"), os.path.join(d2, "SELLO-AR.txt"), d2), False)


def p12():
    base = tmp("cmp")
    fs = [fila("adt", "A1"), fila("vxu", "VXU-B01")]
    corr = [escribir_juicio(fs, os.path.join(base, n)) for n in ("L1", "L2", "M1", "M2")]
    sal = os.path.join(base, "trabajo")
    os.makedirs(sal)
    for n, v in (("POSITIVO-AR.json", False), ("RUIDO-AR.json", True)):
        open(os.path.join(sal, n), "w").write(json.dumps({"pasa": v}))
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = AR.main(["comparar"] + corr + [sal])
    mira("sin controles, 6", (rc, os.path.exists(os.path.join(sal, "COMPARACION-AR.json"))), (6, False))
    open(os.path.join(sal, "POSITIVO-AR.json"), "w").write(json.dumps({"pasa": True}))
    with redirect_stdout(buf):
        rc = AR.main(["comparar"] + corr + [sal])
    mira("control: con los dos, escribe", (rc, os.path.exists(os.path.join(sal, "COMPARACION-AR.json"))), (0, True))
    art, mu, sal2 = artefactos_lfh(), tmp("muestras"), tmp("control")
    es = Espia()
    git_mal = lambda carpeta: (False, "sin commit")  # noqa: E731
    with redirect_stdout(buf):
        rc = CA.main([art, mu, sal2, "--desde", "6", "--hasta", "7"], ejecutor=es, git=git_mal, carpeta_ar=tmp("ar"))
    mira("sin sello, 7 y nada corre", (rc, len(es.corridas)), (7, 0))
    ar_ok = tmp("ar")
    prevision(ar_ok)
    es2 = Espia()
    with redirect_stdout(buf):
        rc = CA.main([art, mu, sal2, "--desde", "6", "--hasta", "7"], ejecutor=es2, git=lambda carpeta: (True, "abc1234"), carpeta_ar=ar_ok)
    mira("control: con sello y commit, lanza", (rc, len(es2.corridas) > 0), (0, True))
    # DV-AR-12: quien repite sella su propia previsión en otra carpeta y la pasa con --sello
    with redirect_stdout(buf):
        rc = CA.main([art, mu, tmp("control"), "--desde", "6", "--hasta", "6", "--sello", ar_ok], ejecutor=Espia(), git=lambda carpeta: (True, "x"))
    mira("--sello con una previsión sellada", rc, 0)
    with redirect_stdout(buf):
        rc = CA.main([art, mu, tmp("control"), "--desde", "6", "--hasta", "6", "--sello", tmp("vacia")], ejecutor=Espia(), git=lambda carpeta: (True, "x"))
    mira("control: --sello sin previsión", rc, 7)


def comp_vxu(cambios=None, quitar=None):
    det = []
    for c in ["VXU-B%02d" % i for i in range(18, 41)]:
        d = {"caso": c, "solo_en_lote": [RXA17], "solo_en_mensaje": []}
        d.update((cambios or {}).get(c, {}))
        det.append(d)
    det = [d for d in det if d["caso"] != quitar]
    return {"control_vxu": {"diferentes": [d["caso"] for d in det], "no_deterministas": [], "sin_par": [], "detalle": det}}


def p13():
    """DV-AR-11: en un VXU con varias RXA, el juez nombra el hallazgo del grupo n como «RXA(n)-17» (B33-B35 de F7)."""
    mira("los 23 de F7", AR.positivo_vxu(comp_vxu()), True)
    rep = {"VXU-B33": {"solo_en_lote": [["RXA(2)-17", "fidelidad", "dato_perdido"], RXA17]},
           "VXU-B35": {"solo_en_lote": [["RXA(2)-17", "fidelidad", "dato_perdido"]]}}
    mira("con grupos repetidos", AR.positivo_vxu(comp_vxu(rep)), True)
    mira("control: otro hecho más", AR.positivo_vxu(comp_vxu({"VXU-B20": {"solo_en_lote": [RXA17, PID8]}})), False)
    mira("control: otro campo de la RXA", AR.positivo_vxu(comp_vxu({"VXU-B20": {"solo_en_lote": [["RXA(2)-15", "fidelidad", "dato_perdido"]]}})), False)
    mira("control: algo mensaje a mensaje", AR.positivo_vxu(comp_vxu({"VXU-B20": {"solo_en_mensaje": [RXA17]}})), False)
    mira("control: falta uno", AR.positivo_vxu(comp_vxu(quitar="VXU-B30")), False)
    mira("control: vacío", AR.positivo_vxu(comp_vxu({"VXU-B20": {"solo_en_lote": []}})), False)


PRUEBAS = [p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13]


def main():
    rojo = sys.argv[1:] == ["rojo"]
    if not rojo:
        for m, ex in ((AR, globals().get("ERROR_AR")), (CA, globals().get("ERROR_CA"))):
            if m is None:
                print("  no se importa: %s" % ex)
    for p in PRUEBAS:
        grupo[0] = "P-AR-%d" % int(p.__name__[1:])
        try:
            p()
        except Exception as ex:                                             # en rojo, lo esperado es que el código no exista
            FALLAN.add(grupo[0])
            if not rojo:
                print("  EXCEPCIÓN %s: %s" % (grupo[0], "".join(traceback.format_exception(type(ex), ex, ex.__traceback__)[-3:]).strip()[:600]))
                mal.append(grupo[0])
    shutil.rmtree(RAIZ, ignore_errors=True)
    if rojo:
        print("PRUEBAS AR (rojo): fallan %d de %d %s" % (len(FALLAN), len(PRUEBAS), "(TODAS)" if len(FALLAN) == len(PRUEBAS) else ""))
        return 0 if len(FALLAN) == len(PRUEBAS) else 1
    print("PRUEBAS AR: %s (%d comprobaciones, %d pruebas)" % ("TODO BIEN" if not mal else "%d MAL" % len(mal), n_ok[0], len(PRUEBAS)))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
