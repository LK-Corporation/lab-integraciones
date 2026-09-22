#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprobaciones 6 y 7: lo previsto es lo que pasa.

Compara el bloque B (esperado, declarado ANTES de enviar) con el bloque C
(medido). Cualquier desacuerdo va a CUARENTENA.

NO REETIQUETA NADA. Reetiquetar al valor medido convertiria la verdad en "lo
que hizo el motor" y el experimento perderia la capacidad de descubrir bugs
del circuito, que es justo para lo que sirve.

Uso:  python3 comparar.py catalogo.json tabla_casos.tsv bloqueC.tsv [informe.tsv]
"""
import collections
import io
import json
import sys

import generador as G

BASES = {b["id"]: b for b in G.BASES}
NAK = ("AE", "AR", "CE", "CR", "SIN_ACK", "ACK_SIN_MSA")
CAMPOS = ("identifier", "family", "given", "gender", "birthDate")


def cargar(ruta):
    with io.open(ruta, encoding="utf-8") as fh:
        cols = fh.readline().rstrip("\n").split("\t")
        return [dict(zip(cols, l.rstrip("\n").split("\t"))) for l in fh if l.strip()]


def casa(esperado, medido):
    if esperado == "NAK_O_NINGUNO":
        return medido in NAK
    if esperado == "AR_O_AE":
        return medido in ("AR", "AE")
    if not esperado:
        return medido in ("", None)
    return medido in [x for x in esperado.split("o") if x] or medido == esperado


def casa_log(esperado, medido):
    tipos = set(t for t in medido.split(",") if t)
    if not esperado:
        return not tipos
    return bool(tipos) and tipos <= set(esperado.split("o"))


def esperado_canonico(fila, op):
    """Los cinco campos que el canonico DEBERIA llevar, segun la base y las
    diferencias que el operador declara en efecto_campos."""
    b = BASES[fila["base_id"]]
    d = {"identifier": fila["ident"],
         "family": b["apellido"].replace("&", " "),
         "given": b["nombre"] + (" " + b["medio"] if b["medio"] else ""),
         "gender": {"M": "male", "F": "female"}[b["sexo"]],
         "birthDate": b["fnac"][:4] + "-" + b["fnac"][4:6] + "-" + b["fnac"][6:]}
    # `efecto_campos` admite huecos con datos de la base, porque hay
    # operadores cuyo recurso correcto depende de ella: el apellido con
    # subcomponente o el sexo invertido no se pueden escribir como un valor
    # fijo para las cinco bases. Sigue siendo declarativo.
    huecos = {"apellido": d["family"], "dado": d["given"],
              "nombre": b["nombre"], "medio": b["medio"],
              "ident": d["identifier"], "fnac": d["birthDate"],
              "sexo_fhir": d["gender"],
              "sexo_fhir_invertido": ("female" if d["gender"] == "male"
                                      else "male")}
    for k, val in (op.get("efecto_campos") or {}).items():
        d[k] = val.format(**huecos) if isinstance(val, str) and "{" in val else val
    return d


def cargar_err8(ruta="err8_esperado.tsv"):
    """operador -> patron. Derivado del codigo del circuito congelado."""
    import os
    if not os.path.exists(ruta):
        return {}
    return {r["operador"]: r["patron"] for r in cargar(ruta)}


def canonico_medido(m):
    return {"identifier": m["can_identifier"], "family": m["can_family"],
            "given": m["can_given"], "gender": m["can_gender"],
            "birthDate": m["can_birthdate"]}


def main():
    cat = json.load(io.open(sys.argv[1], encoding="utf-8"))
    ops = {o["id"]: o for o in cat["operadores"]}
    b = {f["caso_id"]: f for f in cargar(sys.argv[2])}
    c = cargar(sys.argv[3])
    salida = sys.argv[4] if len(sys.argv) > 4 else None

    err8_esp = cargar_err8()
    filas, cuarentena = [], []
    por_op = collections.defaultdict(lambda: {"n": 0, "ok": 0})

    huerfanas = [m for m in c if m["caso_id"] not in b]
    c = [m for m in c if m["caso_id"] in b]
    if huerfanas:
        print("(%d filas medidas de casos que ya no estan en la tabla: se ignoran)"
              % len(huerfanas))
    for m in c:
        e = b[m["caso_id"]]
        op = ops[e["operador"]]
        motivos = []

        if not casa(e["esperado_ack"], m["medido_ack"]):
            motivos.append("ACK esperado %s, medido %s" % (e["esperado_ack"], m["medido_ack"]))
        if not casa(e["esperado_err3"], m["medido_err3"]):
            motivos.append("ERR-3 esperado %s, medido '%s'"
                           % (e["esperado_err3"] or "(vacio)", m["medido_err3"]))
        if not casa_log(e["esperado_log"], m["medido_log_tipos"]):
            motivos.append("log esperado %s, medido '%s'"
                           % (e["esperado_log"] or "(ninguno)", m["medido_log_tipos"]))

        # --- AGUJERO 1: el ERR-8, que nadie leia -------------------------
        patron = err8_esp.get(e["operador"])
        if patron:
            import re as _re
            if not _re.search(patron, m.get("medido_err8", "") or "", _re.I):
                motivos.append("ERR-8 deberia casar con /%s/ y dice %r"
                               % (patron, (m.get("medido_err8") or "")[:90]))

        # --- AGUJERO 2: el estado del mensaje ----------------------------
        # `medido_estado_msg` es la LISTA de estados distintos de la sesion
        # ("8,9" = un mensaje en error y otro completado), y lo declarado es
        # un solo estado: "2" si el mensaje se queda encolado, "9" si llega a
        # completarse. Asi que lo que hay que exigir es que el estado
        # declarado ESTE entre los medidos. La primera version comparaba las
        # cadenas y era estricta de mas ("9" != "8,9") y laxa de menos: se
        # saltaba los casos con medicion VACIA, que son los graves — ahi no
        # hay ni un mensaje con estado.
        if e.get("esperado_estado_msg"):
            vistos = set(x for x in (m.get("medido_estado_msg") or "").split(",") if x)
            if not vistos:
                motivos.append("estado esperado %s y no hay ningun mensaje con estado"
                               % e["esperado_estado_msg"])
            elif str(e["esperado_estado_msg"]) not in vistos:
                motivos.append("estado esperado %s, medidos %s"
                               % (e["esperado_estado_msg"], ",".join(sorted(vistos))))

        det, efecto = e["esperado_deteccion"], e["esperado_efecto"]
        esp, med = esperado_canonico(e, op), canonico_medido(m)
        difs = [k for k in CAMPOS if esp[k] != med[k]]

        if det == "NADA" and op["clase"] != "ENTORNO":
            if m["n_recurso_canonico"] != "1":
                motivos.append("sin efecto pero hay %s recursos con ese identificador"
                               % m["n_recurso_canonico"])
            if difs:
                motivos.append("sin efecto pero el canonico difiere en %s: %s"
                               % (",".join(difs), " / ".join("%s=%r" % (k, med[k]) for k in difs)))
        elif det == "SILENCIO":
            if op.get("perdida_silenciosa"):
                if m.get("n_recurso_ausente") not in ("0", 0, ""):
                    motivos.append("deberia haberse PERDIDO un paciente y existe (%s)"
                                   % m.get("n_recurso_ausente"))
                if difs:
                    motivos.append("el paciente que SI se procesa deberia ser el de la "
                                   "base y difiere en %s" % ",".join(difs))
            elif op.get("degradacion_en_recurso"):
                # La degradacion no esta en lo que se mando sino en lo que
                # quedo guardado: el canonico lleva los datos nuevos y el
                # recurso sigue con los viejos. Comparar el canonico con la
                # base no puede verlo, porque el mensaje es impecable.
                rec = {"family": m["rec_family"], "given": m["rec_given"],
                       "gender": m["rec_gender"], "birthDate": m["rec_birthdate"]}
                can = {k: med[k] for k in rec}
                if rec == can:
                    motivos.append("se esperaba que el recurso guardado NO reflejara "
                                   "el mensaje, y coincide con el canonico")
            elif efecto == "RECURSO_DEGRADADO":
                if not difs:
                    motivos.append("se esperaba resultado incorrecto silencioso y el "
                                   "canonico ha salido EXACTO al de la base")
            elif efecto == "VALOR_IMPOSIBLE_ACEPTADO":
                # AGUJERO 3. El circuito acepto sin comprobarlo un valor que
                # no puede ser cierto, y lo transmitio con FIDELIDAD. Asi que
                # no vale "difiere de la base": tiene que llevar EXACTAMENTE
                # lo que se mando, y eso lo declara el operador en
                # efecto_campos. Si el operador no lo declara, no se puede
                # comprobar y se dice, en vez de pasar en silencio.
                if not (op.get("efecto_campos") or {}):
                    motivos.append("efecto VALOR_IMPOSIBLE_ACEPTADO sin efecto_campos: "
                                   "no hay contra que comprobar el canonico")
                elif difs:
                    motivos.append("el canonico deberia llevar el valor imposible tal cual "
                                   "y difiere en %s: %s"
                                   % (",".join(difs),
                                      " / ".join("%s=%r" % (k, med[k]) for k in difs)))
            elif efecto == "RECURSO_CORRECTO" and difs:
                motivos.append("el silencio no estaba en el recurso y sin embargo "
                               "difiere en %s" % ",".join(difs))

        por_op[e["operador"]]["n"] += 1
        if not motivos:
            por_op[e["operador"]]["ok"] += 1
        else:
            cuarentena.append((e, m, motivos))
        filas.append((e, m, motivos))

    print("=" * 78)
    print("COMPROBACION 6 — lo previsto contra lo que pasa   (%d casos)" % len(c))
    print("=" * 78)
    ok = sum(1 for f in filas if not f[2])
    print("de acuerdo : %d  (%.1f %%)" % (ok, 100.0 * ok / len(filas)))
    print("cuarentena : %d  (%.1f %%)  en %d operadores"
          % (len(cuarentena), 100.0 * len(cuarentena) / len(filas),
             len(set(e["operador"] for e, _, _ in cuarentena))))
    print()
    conf = sorted(k for k, v in por_op.items() if v["ok"] == v["n"])
    print("CONFIRMAN LO DECLARADO: %d operadores de %d" % (len(conf), len(por_op)))
    print()
    print("EN CUARENTENA")
    disc = collections.defaultdict(list)
    for e, m, mot in cuarentena:
        disc[e["operador"]].append((e, m, mot))
    for opn in sorted(disc):
        casos = disc[opn]
        e0 = casos[0][0]
        print("  %-32s %d/%d  [%s]" % (opn, len(casos), por_op[opn]["n"],
                                       e0["estado_expectativa"]))
        for x in sorted(set(mm for _, _, ms in casos for mm in ms))[:3]:
            print("        %s" % x[:120])
    print()

    if salida:
        cols = ["caso_id", "operador", "estado_expectativa", "esperado_ack", "medido_ack",
                "esperado_err3", "medido_err3", "esperado_log", "medido_log_tipos",
                "esperado_deteccion", "esperado_efecto", "n_recurso_canonico",
                "n_recurso_ausente", "can_identifier", "can_family", "can_given",
                "can_gender", "can_birthdate", "medido_err8", "acuerdo", "motivos"]
        with io.open(salida, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\t".join(cols) + "\n")
            for e, m, mot in filas:
                d = dict(e)
                d.update(m)
                d["acuerdo"] = "SI" if not mot else "NO"
                d["motivos"] = " | ".join(mot)
                fh.write("\t".join(str(d.get(k, "")).replace("\t", " ") for k in cols) + "\n")
        print("informe -> %s" % salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
