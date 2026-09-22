#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El triador sin cerebro: expresiones regulares sobre el ACK y el log.

ESTO ES UNA LINEA BASE, NO UN AGENTE. Es lo que haria un integrador que mira
el ACK, ve un codigo y aplica una tabla, sin entender nada del mensaje.

SE ESCRIBE ANTES DE VER UNA SOLA SALIDA DEL AGENTE y se congela por hash. Si
se escribiera despues, se podria afinar hasta que el agente ganara — y
entonces no mediria nada.

Ve exactamente lo mismo que el brazo (b): mensaje, ACK y log. No ve la tabla.

PARA QUE SIRVE: el titular de la Fase 12 NO es la puntuacion del agente, es
cuanto le gana a esto DONDE ESTO FALLA. El regex acertara casi todos los
rechazos con ERR-3, porque el ERR-3 se lo dice. Lo que no puede acertar es un
fallo silencioso: ahi no hay nada que leer, hay que comparar el mensaje con
el resultado. Si el agente no gana ahi, es un regex con mas pasos.

Uso:  python3 triador_regex.py tabla_casos.tsv bloqueC.tsv respuestas_regex.tsv
"""
import hashlib
import io
import re
import sys

REGLAS = [
    # (patron sobre el ERR-8, veredicto, categoria, locus, accion, confianza)
    (r"401|Unauthorized|no autorizado", "ENTORNO", "ENTORNO", "ENTORNO:credencial",
     "ESCALAR_ENTORNO", 0.8),
    (r"404|Not Found", "ENTORNO", "ENTORNO", "ENTORNO:ruta", "ESCALAR_ENTORNO", 0.8),
    (r"ErrFailureTimeout|connection|Connect|no devolvio respuesta|timeout",
     "ENTORNO", "ENTORNO", "ENTORNO:conexion", "REINTENTAR", 0.8),
    (r"Tipo de mensaje no soportado", "RECHAZO_POLITICA", "CODIGO", "MSH:9", "NADA", 0.9),
    (r"Falta el identificador", "FALLO_MENSAJE", "OBLIGATORIO_VACIO", "PID:3",
     "CORREGIR_EMISOR", 0.9),
    (r"Falta el nombre", "FALLO_MENSAJE", "OBLIGATORIO_VACIO", "PID:5",
     "CORREGIR_EMISOR", 0.9),
    (r"excede la longitud", "FALLO_MENSAJE", "TIPO", "PID:3", "CORREGIR_EMISOR", 0.8),
    (r"FHIR devolvio 4\d\d", "FALLO_MENSAJE", "TIPO", "PID:7", "CORREGIR_EMISOR", 0.7),
    (r"FHIR devolvio 5\d\d", "ENTORNO", "ENTORNO", "ENTORNO:fhir", "REINTENTAR", 0.7),
]

# Sin senal de error, el regex no tiene nada que leer. Contesta lo unico que
# puede contestar, y esa es exactamente su limitacion.
SIN_SENAL = ("SIN_PROBLEMA", "NINGUNA", "", "NADA", 0.6)


def cargar(ruta):
    with io.open(ruta, encoding="utf-8") as fh:
        cols = fh.readline().rstrip("\n").split("\t")
        return [dict(zip(cols, l.rstrip("\n").split("\t"))) for l in fh if l.strip()]


def triar(ack, err3, err8, log_tipos):
    texto = " ".join([ack or "", err3 or "", err8 or ""])
    if ack in ("AA", "CA", "") and not [t for t in log_tipos.split(",") if t]:
        return SIN_SENAL
    for patron, v, c, l, a, conf in REGLAS:
        if re.search(patron, texto, re.I):
            return v, c, l, a, conf
    if ack in ("AR", "AE", "CE", "CR", "SIN_ACK"):
        return "FALLO_MENSAJE", "ESTRUCTURA", "", "CORREGIR_EMISOR", 0.5
    return SIN_SENAL


def main():
    tab = {f["caso_id"]: f for f in cargar(sys.argv[1])}
    med = cargar(sys.argv[2])
    salida = sys.argv[3]

    cols = ["caso_id", "veredicto", "categoria", "locus", "accion", "confianza", "causa"]
    with io.open(salida, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(cols) + "\n")
        n = 0
        for m in med:
            if m["caso_id"] not in tab:
                continue
            v, c, l, a, conf = triar(m["medido_ack"], m["medido_err3"],
                                     m["medido_err8"], m["medido_log_tipos"])
            fh.write("\t".join([m["caso_id"], v, c, l, a, str(conf),
                                "regla de expresion regular"]) + "\n")
            n += 1
    h = hashlib.sha256(io.open(__file__, "rb").read()).hexdigest()
    print("respuestas del triador de regex: %d -> %s" % (n, salida))
    print("SHA256 DEL TRIADOR (congelado): %s" % h)
    return 0


if __name__ == "__main__":
    sys.exit(main())
