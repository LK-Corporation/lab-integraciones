#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CV2, adjudicación: enseña ejemplos de un mecanismo (el «que» del juez, el campo del mensaje y lo que trae el recurso emparejado)
para decidir si es del juez, del perfil, del corpus o del conversor. Uso:
  python3 cv/inspeccionar_cv2.py <evidencias> <detalle.jsonl> <conversor> <corpus> <mecanismo> [n] [ruta.json del recurso]"""
import json
import os
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, FASE)
import conversion as CV  # noqa: E402
import mapeador_referencia as MR  # noqa: E402


def main(ev, detalle, conv, corpus, mec, n="2"):
    filas = [json.loads(l) for l in open(detalle, encoding="utf-8")]
    xs = [x for x in filas if x["conversor"] == conv and x["corpus"] == corpus and mec in x["mcs"]][:int(n)]
    for x in xs:
        e = json.load(open(os.path.join(ev, conv, corpus, x["caso"] + ".json"), encoding="utf-8"))
        m = MR.mensajes(e["mensaje"])[0]
        print("=" * 100)
        print("%s %s %s" % (conv, x["caso"], x["categoria"]))
        hs = [h for h in x["cuentan"] if mec in h["mc"]]
        hechos = sorted({h["hecho"] for h in hs})
        for h in hs:
            for q in h["que"]:
                print("  QUE [%s] %s" % (h["hecho"], q[:300]))
        for hc in hechos:
            seg = hc.split("-")[0].split("(")[0]
            for s in m.segmentos(seg)[:1]:
                print("  MSG %s: %s" % (seg, s[:300]))
        s = e["conversion"]["salida"]
        if s.get("bundle"):
            lec = CV.leer_y_emparejar(m, s["bundle"], "oru" if e["punto_entrada"] == "oru_conv" else "adt")
            for r in lec["recursos"]:
                if r["entry"] and any(t in (" ".join(q for h in hs for q in h["que"])) for t in (r["rol"].split("#")[0],)):
                    obs = r["entry"]["r"]
                    rutas = [q.split(":")[0].split(" ")[0] for h in hs for q in h["que"]]
                    claves = {x.split(".", 1)[1].split(".")[0] for x in rutas if "." in x}
                    print("  OBS %s: %s" % (r["rol"], json.dumps({k: obs.get(k) for k in claves}, ensure_ascii=False)[:900]))
                    if "location" in claves:
                        for le in obs.get("location") or []:
                            x2, forma = CV.resolver(lec["entries"], le.get("location"), r["entry"], "Location")
                            cad = []
                            while x2 is not None and len(cad) < 6:
                                cad.append({k: x2["r"].get(k) for k in ("identifier", "name", "physicalType", "partOf")})
                                x2 = CV.resolver(lec["entries"], x2["r"].get("partOf"), x2, "Location")[0]
                            print("    cadena: %s" % json.dumps(cad, ensure_ascii=False)[:900])
                        otras = [e2["r"] for e2 in lec["entries"] if e2["tipo"] == "Location"]
                        print("    Location del Bundle: %s" % json.dumps([{k: o.get(k) for k in ("id", "identifier", "name", "partOf")} for o in otras], ensure_ascii=False)[:900])


if __name__ == "__main__":
    main(*sys.argv[1:7])
