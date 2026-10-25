#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 21 (cv/ar/diseno-ar-fable.md §10): el orquestador del aparato. Encadena los pasos y para en el primer fallo; cada paso
deja su resultado en <salida>/CONTROL-AR.json, sin rutas de máquina (las corridas se nombran L1, L2, M1, M2).

  python3 cv/ar/control_ar.py <artefactos> <muestras> <salida> [--desde N] [--hasta N] [--ms <corrida de Microsoft>] [--paralelo]
                              [--sello <carpeta con PREVISION-AR.json y SELLO-AR.txt>]

Pasos: 3 identidades (sin Docker); 4 humo; 5 positivo VL11; 6 el sello de la previsión, en un commit; 7 L1 y L2 (lote) y su
ruido; 8 M1 y M2 (mensaje a mensaje) y su ruido -> RUIDO-AR.json; 9-10 la comparación y el positivo VXU; 11 la adjudicación;
12 el recálculo de cifras (con --ms: la corrida de Microsoft del control de la etapa 18, que se copia y se rejuzga con el juez
actual); 13 RESULTADO-ARRASTRE.md.
Códigos: 0 todo; 1 identidades; 2 humo; 3 positivo VL11; 4 ruido; 5 positivo VXU; 6 comparación sin controles; 7 sello;
8 inseparable en la adjudicación; 9 reloj de la adjudicación agotado."""
import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout

AR_D = os.path.dirname(os.path.abspath(__file__))
CVD = os.path.dirname(AR_D)
FASE = os.path.dirname(CVD)
sys.path[:0] = [AR_D, CVD, FASE]
import arrastre as AR  # noqa: E402

VC = AR.VC
ESPERADO = {"huella": "ac41f71b98ee75bac637ecd4b68f58b463f0798bf66cfa941f4194cb2a50acf2",
            "huella_con_nombres": "7ad4d5463640901ae4eccd12afd34d6a6ce70c7fa169575caca148c8232db6aa",
            "n": {"adt": 263, "oru": 40, "vxu": 40, "muestras": 65, "minimos": 68, "propio": 0},
            "imagen_digest": "sha256:7bb84a451705605a47d24eb844d4d9ab03e33e131a507db76aafe25db3907f64"}
SELLADOS = ("PREVISION-AR.json", "SELLO-AR.txt")


def git_por_omision(carpeta):
    """-> (en un commit y sin cambios, commit): los ficheros del sello están en HEAD y no tienen cambios sin commit."""
    aparato = [os.path.relpath(p, carpeta) for p in (os.path.join(AR_D, "arrastre.py"), os.path.join(AR_D, "control_ar.py"),
                                                      AR.AD_LOTE, AR.AD_MENSAJE)]
    try:
        h = subprocess.run(["git", "-C", carpeta, "log", "-1", "--format=%h %cI", "--"] + list(SELLADOS), capture_output=True,
                           text=True, timeout=60).stdout.strip()
        st = subprocess.run(["git", "-C", carpeta, "status", "--porcelain", "--"] + list(SELLADOS) + aparato,
                            capture_output=True, text=True, timeout=60).stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as ex:
        return False, str(ex)
    return bool(h) and not st, h or "sin commit"


def _correr(argv, ejecutor):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = VC.main(argv, ejecutor=ejecutor)
    return rc, buf.getvalue()


def corrida(nombre, ad, art, muestras, salida, ejecutor, comparar=None):
    argv = [ad, os.path.join(salida, nombre), "--artefactos", art, "--muestras", muestras, "--json-solo"]
    if comparar:
        argv += ["--comparar", comparar]
    rc, out = _correr(argv, ejecutor)
    if rc not in (0, 5):
        raise AR.ErrorAparato("%s salió con %d: %s" % (nombre, rc, out[-1500:]))
    cr = json.load(open(os.path.join(salida, nombre, "CORRIDA.json"), encoding="utf-8"))
    return {"rc": rc, "sin_evidencia": cr.get("sin_evidencia", []), "reintentos": cr.get("reintentos", []),
            "imagen_digest": cr.get("imagen_digest"), "corpus": cr.get("corpus", {}).get("n"), "juez": cr["juez"]["huella"],
            "huella": cr["huella"], "segundos": cr.get("duraciones", {}).get("total_s")}


def corridas_paralelas(nombres, ad, art, muestras, salida):
    """Las dos corridas mensaje a mensaje a la vez, cada una en su proceso (los contenedores llevan el PID en el nombre)."""
    ps = []
    for n in nombres:
        log = open(os.path.join(salida, n + ".log"), "w")
        ps.append((n, subprocess.Popen([sys.executable, os.path.join(CVD, "verificar_conversor.py"), ad, os.path.join(salida, n),
                                        "--artefactos", art, "--muestras", muestras, "--json-solo"], stdout=log, stderr=subprocess.STDOUT), log))
    out = {}
    for n, p, log in ps:
        rc = p.wait()
        log.close()
        if rc not in (0, 5):
            raise AR.ErrorAparato("%s salió con %d (ver %s.log)" % (n, rc, n))
        cr = json.load(open(os.path.join(salida, n, "CORRIDA.json"), encoding="utf-8"))
        out[n] = {"rc": rc, "sin_evidencia": cr.get("sin_evidencia", []), "imagen_digest": cr.get("imagen_digest"),
                  "corpus": cr.get("corpus", {}).get("n"), "juez": cr["juez"]["huella"], "huella": cr["huella"],
                  "segundos": cr.get("duraciones", {}).get("total_s")}
    return out


def identidades(art, muestras):
    r = {"juez": VC.M._version()["huella"]}
    for clave, ad in (("lote", AR.AD_LOTE), ("mensaje", AR.AD_MENSAJE)):
        a = VC.leer_adaptador(ad, art)
        r[clave] = {"huella": VC.huella(a, art), "huella_con_nombres": VC.huella_con_nombres(a, art)}
    r["huella"] = r["lote"]["huella"]
    d = tempfile.mkdtemp(prefix="ar_ident_")
    try:
        co = VC.generar_corpus(os.path.join(d, "corpus"), lab=True, minimos=True, muestras=muestras)
        gen = dict(reversed(x.split("  ", 1)) for x in open(os.path.join(d, "corpus", "MANIFIESTO.txt")).read().split("\n") if x)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    man = dict(reversed(x.split("  ", 1)) for x in open(os.path.join(CVD, "CORPUS-CV2-MANIFIESTO.txt")).read().split("\n") if x)
    r["manifiesto"] = {"lineas_estudio": len(man), "iguales": sum(1 for k, v in man.items() if gen.get(k) == v)}
    r["n"] = co["n"]
    rc, out = _correr([AR.AD_MENSAJE, "/nada", "--artefactos", art, "--muestras", muestras, "--solo-orden"], None)
    r["orden_mensaje"] = [x for x in out.split("\n") if "Arnes" in x][-1:] if rc == 0 else ["rc %d" % rc]
    r["cuadra"] = (all(r[c]["huella"] == ESPERADO["huella"] and r[c]["huella_con_nombres"] == ESPERADO["huella_con_nombres"]
                       for c in ("lote", "mensaje"))
                   and r["n"] == ESPERADO["n"] and r["manifiesto"]["iguales"] == r["manifiesto"]["lineas_estudio"] == 368
                   and any(x.rstrip().endswith("Arnes /in /salida /in/A01-001.hl7") for x in r["orden_mensaje"]))
    return r


def humo(art, salida, ejecutor):
    rc, out = _correr([AR.AD_MENSAJE, os.path.join(salida, "humo"), "--artefactos", art, "--limite-casos", "1", "--json-solo"], ejecutor)
    cr = json.load(open(os.path.join(salida, "humo", "CORRIDA.json"), encoding="utf-8"))
    estados = [json.loads(x)["estado"] for x in open(os.path.join(salida, "humo", "juicio.jsonl"), encoding="utf-8")]
    return {"rc": rc, "imagen_digest": cr.get("imagen_digest"), "estados": estados,
            "cuadra": rc == 0 and cr.get("imagen_digest") == ESPERADO["imagen_digest"] and bool(estados)
            and all(e in ("bundle", "error") for e in estados)}


def main(argv=None, ejecutor=None, git=None, carpeta_ar=AR_D):
    p = argparse.ArgumentParser(prog="control_ar")
    p.add_argument("artefactos")
    p.add_argument("muestras")
    p.add_argument("salida")
    p.add_argument("--desde", type=int, default=3)
    p.add_argument("--hasta", type=int, default=13)
    p.add_argument("--ms")
    p.add_argument("--paralelo", action="store_true")
    p.add_argument("--sello", help="la carpeta con PREVISION-AR.json y SELLO-AR.txt (por omisión, cv/ar/); quien repite sella la suya")
    a = p.parse_args(argv)
    git = git or git_por_omision
    carpeta_ar = a.sello or carpeta_ar
    os.makedirs(a.salida, exist_ok=True)
    ruta_ctl = os.path.join(a.salida, "CONTROL-AR.json")
    ctl = json.load(open(ruta_ctl, encoding="utf-8")) if os.path.exists(ruta_ctl) else {}
    art, mu, sal = a.artefactos, a.muestras, a.salida

    def paso(n):
        return a.desde <= n <= a.hasta

    def fin(rc, motivo, paso_):
        ctl["fin"] = {"rc": rc, "paso": paso_, "motivo": motivo}
        AR._escribir(ruta_ctl, ctl)
        print("control_ar: paso %d, %s (%d)" % (paso_, motivo, rc), flush=True)
        return rc

    try:
        if paso(3):
            ctl["identidades"] = identidades(art, mu)
            AR._escribir(ruta_ctl, ctl)
            if not ctl["identidades"]["cuadra"]:
                return fin(1, "las identidades no cuadran", 3)
        if paso(4):
            ctl["humo"] = humo(art, sal, ejecutor)
            if not ctl["humo"]["cuadra"]:
                return fin(2, "el humo no cuadra", 4)
        if paso(5):
            r = AR.positivo_vl11(art, sal, ejecutor)
            AR._escribir(os.path.join(sal, "POSITIVO-AR.json"), r)
            ctl["positivo_vl11"] = r["pasa_vl11"]
            if not r["pasa_vl11"]:
                return fin(3, "el positivo VL11 no sale (regla de parada 1)", 5)
        if a.desde <= 7 <= a.hasta or a.desde <= 8 <= a.hasta or paso(6):
            ok_s = AR.comprobar_sello(os.path.join(carpeta_ar, "PREVISION-AR.json"), os.path.join(carpeta_ar, "SELLO-AR.txt"))
            ok_g, commit = git(carpeta_ar)
            ctl["sello"] = {"verifica": ok_s, "en_commit": ok_g, "commit": commit}
            if not (ok_s and ok_g):
                return fin(7, "la previsión no está sellada en un commit", 6)
        if paso(7):
            ctl["corridas"] = ctl.get("corridas", {})
            for n in ("L1", "L2"):
                ctl["corridas"][n] = corrida(n, AR.AD_LOTE, art, mu, sal, ejecutor)
            ctl["ruido_lote"] = AR.ruido(os.path.join(sal, "L1"), os.path.join(sal, "L2"))
            AR._escribir(ruta_ctl, ctl)
            if ctl["ruido_lote"]["veredicto"] or ctl["ruido_lote"]["faltan"]:
                return fin(4, "dos corridas en lote no dan los mismos veredictos (regla de parada 2)", 7)
        if paso(8):
            ctl["corridas"] = ctl.get("corridas", {})
            if a.paralelo and ejecutor is None:
                ctl["corridas"].update(corridas_paralelas(("M1", "M2"), AR.AD_MENSAJE, art, mu, sal))
            else:
                for n in ("M1", "M2"):
                    ctl["corridas"][n] = corrida(n, AR.AD_MENSAJE, art, mu, sal, ejecutor)
            ctl["ruido_mensaje"] = AR.ruido(os.path.join(sal, "M1"), os.path.join(sal, "M2"))
            n = sum(v for k, v in ESPERADO["n"].items() if k not in AR.CONTROL)
            para = AR.regla_parada(ctl["ruido_lote"], ctl["ruido_mensaje"], n) or bool(ctl["ruido_mensaje"]["faltan"])
            dig = {k: v.get("imagen_digest") for k, v in ctl["corridas"].items() if k.startswith("M")}
            caja = {k: len(v.get("sin_evidencia") or []) for k, v in ctl["corridas"].items()}
            ruido = {"pasa": not para and all(x == ESPERADO["imagen_digest"] for x in dig.values()) and not any(caja.values()),
                     "umbral_q_ar_d_1": AR.UMBRAL, "n": n, "lote": ctl["ruido_lote"], "mensaje": ctl["ruido_mensaje"],
                     "imagen_digest": dig, "sin_evidencia": caja}
            AR._escribir(os.path.join(sal, "RUIDO-AR.json"), ruido)
            AR._escribir(ruta_ctl, ctl)
            if not ruido["pasa"]:
                return fin(4, "el control negativo no pasa (regla de parada 2)", 8)
        if paso(9) or paso(10):
            rc = AR.comparar(*[os.path.join(sal, x) for x in ("L1", "L2", "M1", "M2")], sal)
            if rc:
                return fin(6, "comparación sin los dos controles", 10)
            comp = json.load(open(os.path.join(sal, "COMPARACION-AR.json"), encoding="utf-8"))
            pos = json.load(open(os.path.join(sal, "POSITIVO-AR.json"), encoding="utf-8"))
            pos["pasa_vxu"] = comp["controles"]["positivo_vxu"]
            AR._escribir(os.path.join(sal, "POSITIVO-AR.json"), pos)
            ctl["comparacion"] = comp["n"]
            if not pos["pasa_vxu"]:
                return fin(5, "el corpus VXU no da los 23 de F7 (regla de parada 1)", 9)
        if paso(11):
            r = AR.adjudicar(sal, art, ejecutor)
            ctl["adjudicacion"] = r["por_tipo"]
            if r["inseparables"]:
                return fin(8, "diferencias que no se separan del no determinismo: %s" % r["inseparables"], 11)
            if r["reloj_agotado"]:
                return fin(9, "el reloj de la adjudicación se agotó", 11)
        if paso(12):
            if not a.ms:
                return fin(1, "el recálculo necesita --ms", 12)
            ms = os.path.join(sal, "MS")
            shutil.rmtree(ms, ignore_errors=True)
            shutil.copytree(a.ms, ms)
            rc, out = _correr([AR.AD_MS, ms, "--artefactos", art, "--desde-evidencias", "--json-solo"], ejecutor)
            if rc not in (0, 4):
                return fin(1, "Microsoft no se rejuzga (%d)" % rc, 12)
            r = AR.recalcular(sal, ms)
            ctl["cifras"] = len(r["cifras"])
            ctl["deriva_del_juez"] = len(r["deriva_del_juez"])
        if paso(13):
            AR.main(["resultado", sal, os.path.join(sal, "RESULTADO-ARRASTRE.md")])
    except AR.ErrorAparato as ex:
        return fin(1, "error del aparato: %s" % ex, -1)
    return fin(0, "hecho", a.hasta)


if __name__ == "__main__":
    sys.exit(main())
