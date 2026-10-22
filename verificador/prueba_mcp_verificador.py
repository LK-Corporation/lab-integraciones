#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Autoprueba del servidor MCP (diseno-mcp-fable.md §7.1, P01-P30; diseno-s6-s16-fable.md, P26b y P31-P35;
diseno-s19-s21-fable.md, P36-P43;
diseno-s30-fable.md, P44; diseno-s31-s34-fable.md, P45-P46): lanza el servidor como subproceso, le
escribe peticiones JSON-RPC línea a línea y comprueba la FORMA de las respuestas (y los bytes en P22).
Uso: python3 mcp_verificador.py --autoprueba"""
import http.client
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time

import acuse_referencia as AR

B = list(AR.B)
L01 = {"tipo": "Info", "componente": "FhirPatient", "texto": "Patient creado en FHIR: id=<oculto> desde MSH-10=MSG1 (HTTP 201)"}
CAN = {"Identifier": "ID1", "FamilyName": "Apellido", "GivenName": "Nombre", "Gender": "male", "BirthDate": "1960-09-10",
       "MsgControlId": "MSG1", "SendingApp": "LAB_SYS", "SendingFacility": "CLINICA_B", "MsgEvent": "A01", "ProcessingId": "P", "Truncado": 0}
ACK = "MSH|^~\\&|LABFHIR|LAB|LAB_SYS|CLINICA_B|<hora oculta>||ACK^A01^ACK|X1|P|2.5\nMSA|AA|MSG1"
CX = ["conexión establecida", "ACK recibido a los 0.016 s del envío"]
mal = []


def mira(nombre, ok, detalle=""):
    sys.stderr.write(("  ok  " if ok else "  MAL ") + nombre + ("" if ok else ": " + str(detalle)[:300]) + "\n")
    if not ok:
        mal.append(nombre)


def cable(segs):
    return "<VT>" + "\n".join(segs) + "\n<FS>"


def bundle(segs=None, canon=CAN, **kw):
    b = {"mensaje": cable(segs or B), "ack": ACK, "sesiones": [{"log": [L01], "canonico": dict(canon)}], "conexion": CX, "entorno": []}
    b.update(kw)
    return b


class Proc:
    def __init__(self, servidor):
        self.p = subprocess.Popen([sys.executable, "-u", servidor], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, cwd=os.path.dirname(os.path.abspath(servidor)))
        self.salida = []

    def envia(self, obj, espera=True):
        linea = obj if isinstance(obj, (bytes, str)) else json.dumps(obj, ensure_ascii=False)
        if isinstance(linea, str):
            linea = linea.encode("utf-8")
        self.p.stdin.write(linea + b"\n")
        self.p.stdin.flush()
        if not espera:
            return None
        r = self.p.stdout.readline()
        self.salida.append(r)
        return json.loads(r)

    def llama(self, i, herramienta, args, meta=None):
        p = {"name": herramienta, "arguments": args}
        if meta:
            p["_meta"] = meta
        return self.envia({"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": p})

    def cierra(self):
        t0 = time.time()
        self.p.stdin.close()
        codigo = self.p.wait(timeout=5)
        err = self.p.stderr.read().decode("utf-8", "replace")
        return codigo, time.time() - t0, err


def init(pr, v="2025-06-18"):
    return pr.envia({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                     "params": {"protocolVersion": v, "capabilities": {}, "clientInfo": {"name": "autoprueba", "version": "1"}}})


# ============================================================ transporte HTTP (diseno-demo-n8n-fable.md §1.7, P53-P77)
class ProcHTTP:
    def __init__(self, servidor, *extra, direccion="127.0.0.1:0"):
        self.log = tempfile.NamedTemporaryFile(delete=False, suffix=".log")
        self.p = subprocess.Popen([sys.executable, "-u", servidor, "--http", direccion] + list(extra), stdin=subprocess.DEVNULL,
                                  stdout=subprocess.DEVNULL, stderr=self.log, cwd=os.path.dirname(os.path.abspath(servidor)))
        self.puerto = None
        t0 = time.time()
        while time.time() - t0 < 15 and self.puerto is None and self.p.poll() is None:
            for l in open(self.log.name, encoding="utf-8", errors="replace"):
                if l.startswith("escuchando 127.0.0.1:"):
                    self.puerto = int(l.strip().rsplit(":", 1)[1])
            time.sleep(0.05)

    def registro(self):
        return open(self.log.name, encoding="utf-8", errors="replace").read()

    def pide(self, metodo="POST", cuerpo=None, cab=None, ruta="/mcp", crudo=None, cl=True):
        c = http.client.HTTPConnection("127.0.0.1", self.puerto, timeout=15)
        h = {"Host": "127.0.0.1:%d" % self.puerto, "Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        h.update(cab or {})
        body = crudo if crudo is not None else (json.dumps(cuerpo, ensure_ascii=False).encode("utf-8") if cuerpo is not None else None)
        c.putrequest(metodo, ruta, skip_host=True, skip_accept_encoding=True)
        for k, v in h.items():
            if v is not None:
                c.putheader(k, v)
        if body is not None and cl and "Content-Length" not in h:
            c.putheader("Content-Length", str(len(body)))
        c.endheaders(body if (body is not None and cl) else None)
        r = c.getresponse()
        data = r.read()
        c.close()
        try:
            j = json.loads(data) if data else None
        except ValueError:
            j = None
        return r.status, r.headers, j, data

    def inicia(self, v="2025-11-25", cab=None):
        s, h, j, _ = self.pide(cuerpo={"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                       "params": {"protocolVersion": v, "capabilities": {}, "clientInfo": {"name": "autoprueba", "version": "1"}}}, cab=cab)
        sid = h.get("Mcp-Session-Id")
        if sid:
            self.pide(cuerpo={"jsonrpc": "2.0", "method": "notifications/initialized"}, cab={"Mcp-Session-Id": sid})
        return s, h, j, sid

    def llama(self, sid, i, herramienta, args, cab=None):
        c = {"Mcp-Session-Id": sid, "MCP-Protocol-Version": "2025-11-25"}
        c.update(cab or {})
        return self.pide(cuerpo={"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": herramienta, "arguments": args}}, cab=c)

    def para(self):
        t0 = time.time()
        self.p.send_signal(signal.SIGTERM)
        try:
            codigo = self.p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.p.kill()
            codigo = None
        return codigo, time.time() - t0


def pruebas_http(servidor):
    b6 = bundle(AR._con({("PID", 8): "X"}), canon=dict(CAN, Gender="unknown"))
    hp = ProcHTTP(servidor)
    mira("P53-arranque servidor HTTP en un puerto libre", hp.puerto is not None, hp.registro()[-300:])
    if hp.puerto is None:
        hp.p.kill()
        return
    s, h, j, d = hp.pide("GET")
    mira("P53 GET: 405, Allow, cuerpo vacío", s == 405 and h.get("Allow") == "POST, DELETE" and d == b"", (s, dict(h)))
    s, h, j, sid = hp.inicia()
    res = (j or {}).get("result", {})
    mira("P54 initialize 2025-11-25: 200, json, Mcp-Session-Id, versión, instructions",
         s == 200 and (h.get("Content-Type") or "").startswith("application/json") and sid and len(sid) >= 22
         and all(0x21 <= ord(ch) <= 0x7E for ch in sid) and res.get("protocolVersion") == "2025-11-25"
         and "El verificador decide" in res.get("instructions", ""), (s, dict(h), res.get("protocolVersion")))
    s2, h2, j2, sid2 = hp.inicia("2024-11-05")
    mira("P54b initialize 2024-11-05 -> 2025-06-18", (j2 or {}).get("result", {}).get("protocolVersion") == "2025-06-18", j2)
    s, h, j, d = hp.pide(cuerpo={"jsonrpc": "2.0", "method": "notifications/initialized"}, cab={"Mcp-Session-Id": sid})
    mira("P55 notificación: 202 sin cuerpo", s == 202 and h.get("Content-Length") == "0" and d == b"", (s, dict(h)))
    s, h, j, d = hp.pide(cuerpo={"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, cab={"Mcp-Session-Id": sid, "MCP-Protocol-Version": "2025-11-25"})
    nombres = [t["name"] for t in (j or {}).get("result", {}).get("tools", [])]
    mira("P56 tools/list: 6 en orden, sin resultType", s == 200 and nombres == ["verificar_caso", "ficha_experto", "acuse_esperado",
         "comparar_canonico", "consultar_tabla", "info_verificador"] and "resultType" not in j["result"], (s, nombres))
    s, h, j, d = hp.llama(sid, 3, "consultar_tabla", {"tabla": "0008"})
    mira("P57 consultar_tabla 0008", s == 200 and j["result"]["structuredContent"]["tabla"] == "0008" and j["result"]["isError"] is False, (s, j))
    # P58 paridad stdio / HTTP
    casos = [b6, {"mensaje": cable(B), "ack": ACK}, {"mensaje": "hola"}]
    ruta_b = os.path.join(os.path.dirname(os.path.abspath(servidor)), "capa", "ampliacion_r5", "bundles.jsonl")
    if os.path.exists(ruta_b):
        with open(ruta_b, encoding="utf-8") as fb:
            for _ in range(3):
                casos.append(json.loads(fb.readline())["estructura"])
    pr = Proc(servidor)
    init(pr, "2025-11-25")
    pr.envia({"jsonrpc": "2.0", "method": "notifications/initialized"}, espera=False)
    iguales = 0
    for k, c in enumerate(casos):
        rs = pr.llama(100 + k, "verificar_caso", c)["result"]
        ra = hp.llama(sid, 200 + k, "verificar_caso", c)[2]["result"]
        rb = hp.llama(sid2, 300 + k, "verificar_caso", c)[2]["result"]
        f = [json.dumps(x.get("structuredContent"), sort_keys=True, ensure_ascii=False) for x in (rs, ra, rb)]
        t = [x["content"][0]["text"] for x in (rs, ra, rb)]
        iguales += len(set(f)) == 1 and len(set(t)) == 1
    n_esp = 6 if os.path.exists(ruta_b) else 3                       # el corpus de la fase 13 no viaja al repo público (VE3)
    mira("P58 paridad stdio / HTTP (dos sesiones): %d casos" % len(casos), iguales == len(casos) and len(casos) == n_esp, iguales)
    # P75 tools/list e info_verificador
    ls = pr.envia({"jsonrpc": "2.0", "id": 400, "method": "tools/list"})["result"]
    lh = hp.pide(cuerpo={"jsonrpc": "2.0", "id": 400, "method": "tools/list"}, cab={"Mcp-Session-Id": sid})[2]["result"]
    iss = pr.llama(401, "info_verificador", {})["result"]["structuredContent"]
    ih = hp.llama(sid, 401, "info_verificador", {})[2]["result"]["structuredContent"]
    mira("P75 tools/list e info_verificador idénticos por stdio y HTTP", json.dumps(ls, sort_keys=True) == json.dumps(lh, sort_keys=True)
         and json.dumps(iss, sort_keys=True) == json.dumps(ih, sort_keys=True), None)
    # P76 AP-4
    rs = pr.llama(402, "verificar_caso", {"mensaje": 5})["result"]
    ra = hp.llama(sid, 402, "verificar_caso", {"mensaje": 5})[2]["result"]
    er = [json.loads(x["content"][0]["text"])["error"] for x in (rs, ra)]
    mira("P76 AP-4: isError sin structuredContent, error en content por stdio y HTTP",
         all(x["isError"] is True and "structuredContent" not in x for x in (rs, ra)) and all(e["codigo"] == "tipo_invalido" for e in er)
         and all("5" not in json.dumps({k: v for k, v in e.items() if k != "version"}) for e in er), (rs, ra))
    pr.cierra()
    s, h, j, d = hp.llama(sid, 403, "ficha_experto", b6)
    mira("P77 ficha_experto por HTTP: texto y structuredContent.ficha iguales", s == 200 and j["result"]["content"][0]["type"] == "text"
         and j["result"]["structuredContent"]["ficha"] == j["result"]["content"][0]["text"], None)
    s, h, j, d = hp.pide(cuerpo={"jsonrpc": "2.0", "id": 5, "method": "tools/list"}, cab={"Mcp-Session-Id": "no-existe"})
    mira("P59 sesión inexistente: 404 -32001 id null", s == 404 and j["error"]["code"] == -32001 and j["id"] is None, (s, j))
    s, h, j, d = hp.pide(cuerpo={"jsonrpc": "2.0", "id": 6, "method": "tools/list"})
    mira("P60 sin sesión: 400 -32600 con supported", s == 400 and j["error"]["code"] == -32600 and "2025-11-25" in j["error"]["data"]["supported"]
         and "2026-07-28" in j["error"]["data"]["supported"], (s, j))
    s, h, j, d = hp.inicia(cab={"Origin": "https://ajeno.example"})
    s2, h2, j2, d2 = hp.inicia(cab={"Origin": "http://localhost:5678"})
    mira("P61 Origin ajeno: 403 sin sesión; Origin localhost: 200", s == 403 and j["id"] is None and not h.get("Mcp-Session-Id") and s2 == 200, (s, s2))
    s, h, j, d = hp.inicia(cab={"Origin": "null"})
    mira("P61b Origin null: 403", s == 403, s)
    s, h, j, d = hp.inicia(cab={"Host": "ajeno.example:%d" % hp.puerto})
    s2 = hp.pide(cuerpo={"jsonrpc": "2.0", "id": 7, "method": "ping"})[0]
    mira("P62 Host ajeno: 421 y el servidor sigue vivo", s == 421 and s2 == 200, (s, s2))
    s, h, j, d = hp.pide(crudo=b"", cab={"Content-Length": "3145728"}, cl=False)
    s2 = hp.pide(cuerpo={"jsonrpc": "2.0", "id": 8, "method": "ping"})[0]
    mira("P63 cuerpo de 3 MiB: 413 -32600, y sigue", s == 413 and (j or {}).get("error", {}).get("code") == -32600 and s2 == 200, (s, s2))
    s = hp.pide(crudo=b'{"jsonrpc":"2.0","id":1,"method":"ping"}', cl=False)[0]
    mira("P63b sin Content-Length: 411", s == 411, s)
    s, h, j, d = hp.pide(crudo=b'{"jsonrpc":"2.0",')
    mira("P63c JSON roto: 400 -32700 id null", s == 400 and j["error"]["code"] == -32700 and j["id"] is None, (s, j))
    s, h, j, d = hp.pide(crudo=b'[{"jsonrpc":"2.0","id":1,"method":"ping"}]')
    mira("P63d lote: 400 -32600", s == 400 and j["error"]["code"] == -32600, (s, j))
    s1 = hp.pide(cuerpo={"jsonrpc": "2.0", "id": 9, "method": "ping"}, cab={"Content-Type": "text/plain"})[0]
    s2 = hp.pide(cuerpo={"jsonrpc": "2.0", "id": 9, "method": "ping"}, cab={"Accept": "text/html"})[0]
    s3 = hp.inicia(cab={"Accept": None})[0]
    mira("P65 Content-Type 415, Accept 406, sin Accept 200", (s1, s2, s3) == (415, 406, 200), (s1, s2, s3))
    s, h, j, d = hp.pide(cuerpo={"jsonrpc": "2.0", "id": 10, "method": "tools/list"}, cab={"Mcp-Session-Id": sid, "MCP-Protocol-Version": "1999-01-01"})
    s2 = hp.pide(cuerpo={"jsonrpc": "2.0", "id": 10, "method": "tools/list"}, cab={"Mcp-Session-Id": sid})[0]
    mira("P66 MCP-Protocol-Version inválida 400; ausente 200", s == 400 and "2025-11-25" in j["error"]["data"]["supported"] and s2 == 200, (s, s2))
    meta = {"io.modelcontextprotocol/protocolVersion": "2026-07-28"}
    cm = {"MCP-Protocol-Version": "2026-07-28", "Mcp-Method": "server/discover"}
    s, h, j, d = hp.pide(cuerpo={"jsonrpc": "2.0", "id": "m1", "method": "server/discover", "params": {"_meta": meta}}, cab=cm)
    mira("P67 moderna server/discover: 200 complete, sin sesión", s == 200 and j["result"]["resultType"] == "complete" and not h.get("Mcp-Session-Id"), (s, j))
    pc = {"jsonrpc": "2.0", "id": "m2", "method": "tools/call", "params": {"name": "consultar_tabla", "arguments": {"tabla": "0008"}, "_meta": meta}}
    ct = {"MCP-Protocol-Version": "2026-07-28", "Mcp-Method": "tools/call"}
    r1 = hp.pide(cuerpo=pc, cab=dict(ct, **{"Mcp-Name": "consultar_tabla"}))
    r2 = hp.pide(cuerpo=pc, cab=dict(ct, **{"Mcp-Name": "otra"}))
    r3 = hp.pide(cuerpo=pc, cab={"MCP-Protocol-Version": "2026-07-28", "Mcp-Name": "consultar_tabla"})
    r4 = hp.pide(cuerpo=pc, cab=dict(ct, **{"Mcp-Name": "=?base64?Y29uc3VsdGFyX3RhYmxh?="}))
    mira("P67b cabeceras espejo: 200 / 400 -32020 / 400 -32020 / 200 (base64)",
         (r1[0], r2[0], r3[0], r4[0]) == (200, 400, 400, 200) and r2[2]["error"]["code"] == -32020 and r3[2]["error"]["code"] == -32020,
         (r1[0], r2[0], r3[0], r4[0]))
    pv = dict(pc, params=dict(pc["params"], _meta={"io.modelcontextprotocol/protocolVersion": "2025-11-25"}))
    r1 = hp.pide(cuerpo=pv, cab=dict(ct, **{"Mcp-Name": "consultar_tabla"}))
    r2 = hp.pide(cuerpo=pv, cab={"MCP-Protocol-Version": "2025-11-25", "Mcp-Method": "tools/call", "Mcp-Name": "consultar_tabla"})
    mira("P67c cabecera distinta de _meta: -32020; _meta 2025-11-25: -32022",
         r1[0] == 400 and r1[2]["error"]["code"] == -32020 and r2[0] == 400 and r2[2]["error"]["code"] == -32022
         and r2[2]["error"]["data"]["supported"] == ["2026-07-28"], (r1[0], r1[2], r2[0], r2[2]))
    r1 = hp.pide(cuerpo={"jsonrpc": "2.0", "id": "m3", "method": "resources/list", "params": {"_meta": meta}},
                 cab={"MCP-Protocol-Version": "2026-07-28", "Mcp-Method": "resources/list"})
    r2 = hp.pide(cuerpo={"jsonrpc": "2.0", "id": "m4", "method": "server/discover", "params": {"_meta": meta}}, cab=dict(cm, **{"Mcp-Session-Id": "x"}))
    mira("P67d método desconocido 404 -32601; Mcp-Session-Id ignorada", r1[0] == 404 and r1[2]["error"]["code"] == -32601 and r2[0] == 200, (r1[0], r2[0]))
    s, h, j, sid3 = hp.inicia()
    d1 = hp.pide("DELETE", cab={"Mcp-Session-Id": sid3})[0]
    d2 = hp.pide(cuerpo={"jsonrpc": "2.0", "id": 11, "method": "tools/list"}, cab={"Mcp-Session-Id": sid3})[0]
    d3 = hp.pide("DELETE")[0]
    d4 = hp.pide("DELETE", cab={"Mcp-Session-Id": "no-existe"})[0]
    mira("P68 DELETE: 204, luego 404; sin cabecera 400; desconocida 404", (d1, d2, d3, d4) == (204, 404, 400, 404), (d1, d2, d3, d4))
    s1 = hp.pide(cuerpo={"jsonrpc": "2.0", "id": 12, "method": "ping"}, ruta="/otra")[0]
    s2 = hp.pide("PUT", cuerpo={"jsonrpc": "2.0", "id": 12, "method": "ping"})[0]
    mira("P69 otra ruta 404; PUT 405", (s1, s2) == (404, 405), (s1, s2))
    # P70 concurrencia
    refs = {}
    for nv in ("estricto", "consumido"):
        _, _, _, sref = hp.inicia()
        refs[nv] = hp.llama(sref, 500, "verificar_caso", dict(b6, nivel=nv))[3]
    res70 = [None] * 16

    def uno(k):
        nv = "estricto" if k % 2 else "consumido"
        _, _, _, sk = hp.inicia()
        res70[k] = (nv, hp.llama(sk, 500, "verificar_caso", dict(b6, nivel=nv))[3])
    hilos = [threading.Thread(target=uno, args=(k,)) for k in range(16)]
    for t in hilos:
        t.start()
    for t in hilos:
        t.join(30)
    ok70 = all(x is not None and x[1] == refs[x[0]] and json.loads(x[1])["result"]["structuredContent"]["version"]["nivel"] == x[0] for x in res70)
    mira("P70 concurrencia: 16 respuestas idénticas a su referencia secuencial", ok70, [x[0] if x else None for x in res70])
    # P70b cola de escucha: con el proceso detenido nadie acepta, así que el kernel solo completa el saludo TCP
    # de las conexiones que caben en la cola de listen(); listen(5) dejaba la 7.ª sin saludo (y, con carrera, RST).
    socks, conectadas = [], 0
    hp.p.send_signal(signal.SIGSTOP)
    try:
        for _ in range(32):
            k = socket.socket()
            socks.append(k)
            k.settimeout(0.5)                        # el SYN descartado por cola llena se reintenta al cabo de 1 s
            try:
                k.connect(("127.0.0.1", hp.puerto))
            except OSError:
                break
            conectadas += 1
    finally:
        hp.p.send_signal(signal.SIGCONT)
    ping = b'{"jsonrpc": "2.0", "id": 1, "method": "ping"}'
    cab = ("POST /mcp HTTP/1.1\r\nHost: 127.0.0.1:%d\r\nContent-Type: application/json\r\nContent-Length: %d\r\n\r\n"
           % (hp.puerto, len(ping))).encode("ascii")
    estados = []
    for k in socks[:conectadas]:
        try:
            k.settimeout(15)
            k.sendall(cab + ping)
            r = http.client.HTTPResponse(k)
            r.begin()
            estados.append(r.status if json.loads(r.read()).get("result") == {} else "cuerpo")
        except (OSError, ValueError, http.client.HTTPException) as ex:
            estados.append(type(ex).__name__)
    for k in socks:
        k.close()
    mira("P70b ráfaga de 32 conexiones sin aceptar: todas completan el saludo y responden 200", conectadas == 32
         and estados == [200] * 32, (conectadas, [e for e in estados if e != 200][:4]))
    # P70c concurrencia que ve la carrera: sin NUCLEO, P70 seguía en verde porque el veredicto de b6 no depende del
    # nivel (version.nivel sale de la variable local) y dura ~1 ms, menos que el turno del GIL (5 ms). Aquí el
    # veredicto sí depende de AR.NIVEL (EVN-2 vacío, S6), dura ~17 ms (49 mensajes) y las 16 llamadas salen a la vez.
    b49 = dict(bundle(AR._con({("EVN", 2): ""})),
               mensaje="".join(cable(AR._con({("EVN", 2): ""})).replace("MSG1", "MSG%d" % i) for i in range(49)))
    _, _, _, sref = hp.inicia()
    refs49 = {nv: hp.llama(sref, 600, "verificar_caso", dict(b49, nivel=nv))[3] for nv in ("estricto", "consumido")}
    sesiones = [hp.inicia()[3] for _ in range(16)]
    salida = threading.Barrier(16)
    res70c = [None] * 16

    def larga(k):
        nv = "estricto" if k % 2 else "consumido"
        try:
            salida.wait(15)
        except threading.BrokenBarrierError:
            pass
        res70c[k] = (nv, hp.llama(sesiones[k], 600, "verificar_caso", dict(b49, nivel=nv))[3])
    hilos = [threading.Thread(target=larga, args=(k,)) for k in range(16)]
    for t in hilos:
        t.start()
    for t in hilos:
        t.join(60)
    defecto = json.loads(hp.llama(sref, 601, "verificar_caso", b6)[3])["result"]["structuredContent"]["version"]["nivel"]
    mira("P70c concurrencia con llamadas largas (49 mensajes): 16 respuestas idénticas a su referencia; nivel por defecto intacto",
         refs49["estricto"] != refs49["consumido"] and defecto == "consumido"
         and all(x is not None and x[1] == refs49[x[0]] for x in res70c),
         (defecto, [x[0] if x else None for x in res70c if not x or x[1] != refs49[x[0]]]))
    reg = hp.registro()
    mira("P71 registro sin datos personales ni valores rechazados; con http=", not any(x in reg for x in ("MSG1", "Apellido", "ID1", "ajeno.example"))
         and "http=" in reg, reg[-400:])
    codigo, dur = hp.para()
    lib = socket.socket()
    lib.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)        # como lo enlaza el servidor al rearrancar (TIME_WAIT)
    try:
        lib.bind(("127.0.0.1", hp.puerto))
        rebind = True
    except OSError:
        rebind = False
    lib.close()
    mira("P73 SIGTERM: salida 0 en < 2 s y puerto libre", codigo == 0 and dur < 2 and rebind, (codigo, dur, rebind))
    # P64 token
    dtok = tempfile.mkdtemp()
    ftok = os.path.join(dtok, "token")
    token = "t" * 20 + "0123456789abcdefghijklmnop"
    with open(ftok, "w") as ft:
        ft.write(token)
    os.chmod(ftok, 0o600)
    hp = ProcHTTP(servidor, "--token-fichero", ftok)
    s1, h1 = hp.inicia()[:2]
    s2 = hp.inicia(cab={"Authorization": "Bearer malo"})[0]
    s3 = hp.inicia(cab={"Authorization": "Bearer " + token})[0]
    mira("P64 token: sin 401 + WWW-Authenticate, malo 401, bueno 200, token fuera del registro",
         s1 == 401 and (h1.get("WWW-Authenticate") or "").startswith("Bearer") and s2 == 401 and s3 == 200 and token not in hp.registro(), (s1, s2, s3))
    hp.para()
    os.chmod(ftok, 0o644)
    p = subprocess.run([sys.executable, "-u", servidor, "--http", "127.0.0.1:0", "--token-fichero", ftok], capture_output=True, timeout=20,
                       cwd=os.path.dirname(os.path.abspath(servidor)))
    mira("P64b token legible por otros: no arranca, salida 2, sin el token", p.returncode == 2 and token not in p.stderr.decode("utf-8", "replace"), p.returncode)
    # P72 caducidad
    hp = ProcHTTP(servidor, "--sesion-ttl", "1")
    sid4 = hp.inicia()[3]
    time.sleep(1.5)
    s, h, j, d = hp.pide(cuerpo={"jsonrpc": "2.0", "id": 13, "method": "tools/list"}, cab={"Mcp-Session-Id": sid4})
    mira("P72 sesión caducada: 404 -32001", s == 404 and j["error"]["code"] == -32001, (s, j))
    hp.para()
    # P78 esquema compacto (compatibilidad con clientes que generan gramáticas: Ollama/llama.cpp)
    hp = ProcHTTP(servidor, "--esquema-compacto")
    sid5 = hp.inicia()[3]
    tl = hp.pide(cuerpo={"jsonrpc": "2.0", "id": 14, "method": "tools/list"}, cab={"Mcp-Session-Id": sid5})[2]["result"]["tools"]
    txt = json.dumps(tl)
    r17 = hp.llama(sid5, 15, "verificar_caso", {"mensaje": "M" * 300000})[2]["result"]
    ok5 = hp.llama(sid5, 16, "verificar_caso", b6)[2]["result"]
    mira("P78 --esquema-compacto: sin límites publicados, mismos nombres, límites aplicados igual, resultado igual",
         not any(k in txt for k in ('"maxLength"', '"maxItems"', '"minLength"', '"minItems"')) and len(tl) == 6
         and r17["isError"] and err_de({"result": r17}).get("codigo") == "tamano_excedido"
         and json.dumps(ok5["structuredContent"]["veredicto"], sort_keys=True) == json.dumps(
             json.loads(refs["consumido"])["result"]["structuredContent"]["veredicto"], sort_keys=True), (txt[:200], r17))
    hp.para()
    # P74 direcciones prohibidas
    rc = []
    for dirx in ("0.0.0.0:8765", "192.168.1.10:8765"):
        p = subprocess.run([sys.executable, "-u", servidor, "--http", dirx], capture_output=True, timeout=20, cwd=os.path.dirname(os.path.abspath(servidor)))
        rc.append((p.returncode, "solo 127.0.0.1, ::1 o 100.64.0.0/10" in p.stderr.decode("utf-8", "replace")))
    mira("P74 0.0.0.0 y LAN rechazadas: salida 2 con el motivo", rc == [(2, True), (2, True)], rc)


def err_de(r):
    """AP-4: el error va en content[0].text y no hay structuredContent."""
    if "structuredContent" in r["result"]:
        return {}
    return json.loads(r["result"]["content"][0]["text"]).get("error", {})


def main(servidor):
    salidas, errores = [], []
    pr = Proc(servidor)
    r = pr.envia({"jsonrpc": "2.0", "id": 0, "method": "ping"})
    mira("P01 ping antes de initialize", r.get("result") == {}, r)
    r = init(pr)
    res = r.get("result", {})
    mira("P02 initialize 2025-06-18", res.get("protocolVersion") == "2025-06-18" and res["capabilities"]["tools"]["listChanged"] is False
         and res["serverInfo"]["name"] and "no cambies el veredicto" in res.get("instructions", "") + " no cambies el veredicto", r)
    pr.envia({"jsonrpc": "2.0", "method": "notifications/initialized"}, espera=False)
    r = pr.envia({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    ts = r["result"]["tools"]
    mira("P03/P04 tools/list: 6 en orden, readOnly, sin nextCursor ni resultType",
         [t["name"] for t in ts] == ["verificar_caso", "ficha_experto", "acuse_esperado", "comparar_canonico", "consultar_tabla", "info_verificador"]
         and all(t["inputSchema"]["type"] == "object" and t["annotations"]["readOnlyHint"] and not t["annotations"]["destructiveHint"] for t in ts)
         and "nextCursor" not in r["result"] and "resultType" not in r["result"], r)
    r = pr.llama(3, "verificar_caso", bundle())
    sc = r["result"]["structuredContent"]
    mira("P05 verificar_caso correcto, completo, content = structuredContent",
         not r["result"]["isError"] and sc["veredicto"]["categoria"] == "correcto" and sc["hallazgos"] == []
         and sc["entrada"]["base_de_evidencia"] == "completa" and json.loads(r["result"]["content"][0]["text"]) == sc, sc.get("veredicto"))
    b6 = bundle(AR._con({("PID", 8): "X"}), canon=dict(CAN, Gender="unknown"))
    r = pr.llama(4, "verificar_caso", b6)
    sc6 = r["result"]["structuredContent"]
    h = sc6["hallazgos"][0] if sc6["hallazgos"] else {}
    et = [c["etiqueta"] for c in h.get("citas", [])]
    mira("P06 PID-8 X: fallo_silencioso, fusionado, citas 103 y [M]/[T0001]",
         sc6["veredicto"]["categoria"] == "fallo_silencioso" and h.get("hecho") == "PID-8" and h.get("origen") == ["acuse", "mapeador"]
         and "[T0357] 103" in et and ("[M]" in et or "[T0001]" in et) and sc6["resumen_mecanico"].startswith("fallo_silencioso/"), (sc6["veredicto"], et))
    salidas.append(json.dumps(sc6, sort_keys=True))
    r = pr.llama(5, "verificar_caso", dict(b6, nivel="estricto"))
    r2 = pr.llama(6, "verificar_caso", b6)
    mira("P06b nivel estricto a petición y consumido por defecto [S6]", r["result"]["structuredContent"]["version"]["nivel"] == "estricto"
         and r2["result"]["structuredContent"]["version"]["nivel"] == "consumido", None)
    salidas.append(json.dumps(r2["result"]["structuredContent"], sort_keys=True))
    r = pr.llama(7, "verificar_caso", {"mensaje": cable(B), "ack": ACK})
    sc = r["result"]["structuredContent"]
    ne = " ".join(sc["entrada"]["no_evaluado"])
    mira("P07 solo mensaje y ack: correcto, parcial, no evaluado fidelidad y destino",
         sc["veredicto"]["categoria"] == "correcto" and sc["entrada"]["base_de_evidencia"] == "parcial" and "fidelidad" in ne and "destino" in ne, sc["veredicto"])
    r = pr.llama(8, "verificar_caso", {"mensaje": cable(B)})
    sc = r["result"]["structuredContent"]
    mira("P07b solo mensaje: acuse_incorrecto/ausente, «sin ACK»",
         sc["veredicto"]["categoria"] == "acuse_incorrecto" and "ausente" in (sc["veredicto"]["subtipo"] or "")
         and "sin ACK" in " ".join(sc["entrada"]["no_evaluado"]), sc["veredicto"])
    r = pr.llama(9, "acuse_esperado", {"mensaje": cable(AR._con({("PID", 8): "X"})), "ack": ACK})
    sc = r["result"]["structuredContent"]
    m0 = sc["mensajes"][0]
    ids = [d["id"] for d in m0["discrepancias"]]
    mira("P08 acuse_esperado: AE 103, D1 y D2, discrepa, sin veredicto",
         m0["esperado"]["msa1"] == "AE" and m0["esperado"]["err"][0]["err3"] == "103" and "D1" in ids and "D2" in ids
         and m0["acuse"] == "discrepa" and "veredicto" not in sc, m0)
    r = pr.llama(10, "acuse_esperado", {"mensaje": cable(B)})
    m0 = r["result"]["structuredContent"]["mensajes"][0]
    mira("P08b sin ack: sin_ack_observado con D0", m0["acuse"] == "sin_ack_observado" and "D0" in [d["id"] for d in m0["discrepancias"]], m0)
    r = pr.llama(11, "acuse_esperado", {"mensaje": cable(AR._con({("MSH", 15): "NE", ("MSH", 16): "NE"})), "ack": ACK})
    m0 = r["result"]["structuredContent"]["mensajes"][0]
    mira("P08c NE/NE: no_solicitado y D0", m0["esperado"]["debe_haber_ack"] == "no" and m0["acuse"] == "no_solicitado"
         and any("no solicitado" in d["que"] for d in m0["discrepancias"]), m0)
    r = pr.llama(12, "consultar_tabla", {"tabla": "0357", "valor": "104"})
    sc = r["result"]["structuredContent"]
    mira("P09 tabla 0357 valor 104", sc["consulta"]["presente_literal"] is False and len(sc["entradas"]) == 13 and sc["version_hl7"] == "2.5", sc)
    r = pr.llama(13, "consultar_tabla", {"tabla": "mapeo_0001", "valor": "m"})
    c = r["result"]["structuredContent"]["consulta"]
    mira("P09b mapeo m -> male con [S4]", not c["presente_literal"] and c["presente_en_mayusculas"] and c["destino_fhir"] == "male"
         and "[S4]" in c["nota"], c)
    r = pr.llama(14, "consultar_tabla", {"tabla": "9999"})
    mira("P09c tabla inexistente: isError valor_invalido", r["result"]["isError"] and err_de(r).get("codigo") == "valor_invalido", r)
    r = pr.llama(15, "comparar_canonico", {"mensaje": cable(B), "canonico": dict(CAN, Gender="female"), "ack": ACK})
    sc = r["result"]["structuredContent"]
    d = sc["mensajes"][0]["discrepancias"]
    mira("P10 comparar_canonico Gender", sc["alcance"] == "aceptado" and len(d) == 1 and d[0]["campo"] == "Gender" and d[0]["esperado"] == "male"
         and d[0]["observado"] == "female" and "[M]" in [c["etiqueta"] for c in d[0]["citas"]], sc)
    r = pr.llama(16, "comparar_canonico", {"mensaje": cable(B), "canonico": dict(CAN, Gender="female")})
    sc = r["result"]["structuredContent"]
    mira("P10b sin ack", sc["alcance"] == "sin_ack" and sc["mensajes"][0]["discrepancias"][0]["campo"] == "Gender" and sc["msa2"] is None, sc)
    r = pr.llama(17, "comparar_canonico", {"mensaje": cable(B), "canonico": CAN, "ack": ACK.replace("MSA|AA", "MSA|AR")})
    sc = r["result"]["structuredContent"]
    mira("P10c AR: fuera_de_alcance, sin discrepancias", sc["alcance"] == "fuera_de_alcance" and "canonico_esperado" in sc["mensajes"][0]
         and "discrepancias" not in sc["mensajes"][0], sc)
    r = pr.llama(18, "ficha_experto", b6)
    t = r["result"]["content"][0]
    mira("P11 ficha", t["type"] == "text" and t["text"].startswith("CASO ") and "VEREDICTO PROPUESTO: fallo_silencioso/aceptado_imposible" in t["text"]
         and r["result"]["structuredContent"]["ficha"] == t["text"], t["text"][:200])
    r = pr.envia({"jsonrpc": "2.0", "id": 19, "method": "tools/call", "params": {"name": "no_existe"}})
    mira("P12 herramienta desconocida -32602 con nombres", r.get("error", {}).get("code") == -32602 and len(r["error"]["data"]["herramientas"]) == 6, r)
    r = pr.envia({"jsonrpc": "2.0", "id": 20, "method": "tools/call", "params": {"name": "consultar_tabla", "arguments": "x"}})
    mira("P12b arguments no objeto -32602", r.get("error", {}).get("code") == -32602, r)
    r = pr.envia({"jsonrpc": "2.0", "id": 21, "method": "resources/list"})
    mira("P13 resources/list -32601", r.get("error", {}).get("code") == -32601, r)
    r = pr.envia(b'{"jsonrpc":"2.0",')
    mira("P14 JSON roto -32700 id null", r.get("error", {}).get("code") == -32700 and r["id"] is None, r)
    r = pr.envia('[{"jsonrpc":"2.0","id":9,"method":"ping"}]')
    mira("P15 lote -32600 id null", r.get("error", {}).get("code") == -32600 and r["id"] is None, r)
    r = pr.llama(22, "verificar_caso", {"mensaje": 5})
    er = err_de(r)
    mira("P16 mensaje=5: tipo_invalido sin eco", r["result"]["isError"] and er.get("codigo") == "tipo_invalido" and er.get("campo") == "mensaje"
         and "5" not in json.dumps({k: v for k, v in er.items() if k != "version"}).replace("mensaje", ""), r["result"])
    r = pr.llama(23, "verificar_caso", {"mensaje": cable(B), "sesiones": [{"log": ["cadena"]}]})
    er = err_de(r)
    mira("P16b fila de log string", r["result"]["isError"] and er.get("codigo") == "tipo_invalido" and er.get("campo") == "sesiones[0].log[0]", er)
    r = pr.llama(24, "verificar_caso", {"mensaje": cable(B), "conexion": [123]})
    mira("P16c conexion [123]", r["result"]["isError"] and err_de(r).get("codigo") == "tipo_invalido", r["result"])
    r = pr.llama(25, "verificar_caso", {"mensaje": "M" * 300000})
    mira("P17 mensaje de 300000: tamano_excedido", r["result"]["isError"] and err_de(r).get("codigo") == "tamano_excedido", None)
    r = pr.llama(26, "verificar_caso", {"mensaje": cable(B), "entorno": ["x"] * 101})
    mira("P17b 101 entornos", r["result"]["isError"] and err_de(r).get("codigo") == "tamano_excedido", None)
    pr.envia({"jsonrpc": "2.0", "method": "notifications/loquesea"}, espera=False)
    pr.envia({"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 1}}, espera=False)
    pr.envia({"jsonrpc": "2.0", "id": 7, "result": {}}, espera=False)
    r = pr.envia({"jsonrpc": "2.0", "id": 27, "method": "ping"})
    mira("P21/P21b notificaciones y respuestas del cliente sin respuesta", r.get("id") == 27, r)
    r = pr.llama(28, "verificar_caso", {"mensaje": "hola"})
    sc = r["result"]["structuredContent"]
    mira("P23 hola: sin_intercambio con P0.b", not r["result"]["isError"] and sc["veredicto"]["categoria"] == "sin_intercambio"
         and any("P0.b" in n for n in sc["notas"]), sc.get("veredicto"))
    r = pr.llama(29, "acuse_esperado", {"mensaje": "hola"})
    mira("P23b acuse_esperado hola: sin_mensaje_hl7", r["result"]["isError"] and err_de(r).get("codigo") == "sin_mensaje_hl7", None)
    r = pr.llama(30, "verificar_caso", bundle(AR._con({("EVN", 2): ""})))
    v = r["result"]["structuredContent"]["veredicto"]
    q = r["result"]["structuredContent"]["preguntas_abiertas"]
    mira("P26 EVN-2 vacío [S6]: correcto, sin preguntas, no provisional", v["categoria"] == "correcto" and q == [] and v["provisional"] is False,
         (v, q))
    r = pr.llama(300, "verificar_caso", dict(bundle(AR._con({("EVN", 2): ""})), nivel="estricto"))
    sc = r["result"]["structuredContent"]
    v = sc["veredicto"]
    mira("P26b EVN-2 vacío con nivel estricto: fallo_silencioso literal, alternativa correcto",
         v["categoria"] == "fallo_silencioso" and v["certeza"] == "literal" and v["alternativa"] == "correcto" and v["pregunta_pendiente"] is None
         and sc["version"]["nivel"] == "estricto", v)
    r = pr.llama(31, "verificar_caso", bundle(B[:3] + ["PID|1||ID2^^^HOSP^MR||Otro^Uno||19600910|M"] + B[3:]))
    sc = r["result"]["structuredContent"]
    mira("P27 segundo PID [S14]: fallo_silencioso, firme, sin pregunta", sc["veredicto"]["categoria"] == "fallo_silencioso" and sc["hallazgos"]
         and sc["hallazgos"][0]["estado"] == "firme" and sc["veredicto"]["pregunta_pendiente"] is None
         and "[S14]" in [c["etiqueta"] for c in sc["hallazgos"][0]["citas"]], sc["veredicto"])
    # --- S6-S18
    mu = dict(CAN, FamilyName="Muñoz", GivenName="Ana")
    r = pr.llama(310, "verificar_caso", bundle(AR._con({("PID", 5): "Mu<0xF1>oz^Ana"}), canon=mu))
    sc = r["result"]["structuredContent"]
    mira("P31 [S9] <0xF1> y Muñoz: correcto, tolerancia S9 con cita", sc["veredicto"]["categoria"] == "correcto"
         and any(x["subtipo"] == "S9" and "[S9]" in [c["etiqueta"] for c in x["citas"]] for x in sc["tolerancias"]), sc["veredicto"])
    r = pr.llama(311, "verificar_caso", bundle(AR._con({("PID", 5): "Mu<0xF1>oz^Ana"}), canon=dict(mu, FamilyName="Mu?oz")))
    sc = r["result"]["structuredContent"]
    mira("P31b Mu?oz: fallo_silencioso, cita [S9]", sc["veredicto"]["categoria"] == "fallo_silencioso"
         and "[S9]" in [c["etiqueta"] for c in sc["hallazgos"][0]["citas"]], sc["veredicto"])
    r = pr.llama(312, "verificar_caso", bundle(AR._con({("PID", 5): "Mu<0xF1>oz^Ana", ("MSH", 18): "ISO IR87"}), canon=dict(mu, FamilyName="Mu?oz")))
    sc = r["result"]["structuredContent"]
    mira("P31c ISO IR87: pregunta Q-AMB-10", sc["veredicto"]["pregunta_pendiente"] == "Q-AMB-10"
         and [x["id"] for x in sc["preguntas_abiertas"]] == ["Q-AMB-10"], sc["veredicto"])
    r = pr.llama(320, "verificar_caso", bundle(AR._con({("PID", 5): "<0xC0><0x80>Señor^Ana"}), canon=dict(CAN, FamilyName="Señor", GivenName="Ana")))
    sc = r["result"]["structuredContent"]
    et = [c["etiqueta"] for c in sc["hallazgos"][0]["citas"]] if sc["hallazgos"] else []
    mira("P32 [S10] NUL overlong aceptado: fallo_silencioso, citas [S10] y [E2A §2.A.74], sin preguntas",
         sc["veredicto"]["categoria"] == "fallo_silencioso" and "[S10]" in et and "[E2A §2.A.74]" in et and sc["preguntas_abiertas"] == [], et)
    b33 = bundle(entorno=["FHIR contestó a las peticiones del circuito con error 503, cada una con probabilidad 1.0"])
    r = pr.llama(330, "verificar_caso", b33)
    sc = r["result"]["structuredContent"]
    mira("P33 [A-18] texto antiguo del 5xx (legado) con 201: correcto, una nota [A-18] en arnes_inexacto, sin contradicción",
         sc["veredicto"]["categoria"] == "correcto" and any("[A-18]" in n for n in sc["notas"])
         and sc["lectura"]["contradictorio"] == [] and len(sc["lectura"]["arnes_inexacto"]) == 1, (sc["veredicto"], sc["notas"]))
    r = pr.llama(331, "verificar_caso", bundle(entorno=["FHIR contestó con error 503, con probabilidad 1.0, solo a la primera petición "
                                                       "POST del circuito en el lote (reintentos incluidos); a las demás las atendió con normalidad"],
                                               sesiones=[{"log": []}]))
    sc = r["result"]["structuredContent"]
    mira("P33b 5xx con ventana, sin log: correcto, límites L5 y L21, sin preguntas",
         (sc["veredicto"]["categoria"], {"L5", "L21"} <= set(sc["limites"]), sc["preguntas_abiertas"]), ("correcto", True, []))
    r = pr.llama(340, "verificar_caso", bundle(AR._con({("MSH", 15): "AL", ("MSH", 16): "AL"})))
    sc = r["result"]["structuredContent"]
    mira("P34 [S13] AL/AL con AA: correcto, sin menores, nota S13", sc["veredicto"]["categoria"] == "correcto" and sc["menores"] == []
         and any("[S13]" in n for n in sc["notas"]), sc["veredicto"])
    L422 = {"tipo": "Warning", "componente": "FhirPatient", "texto": "FHIR rechazo el recurso (MSH-10=MSG1): FHIR devolvio 422:"}
    b35 = bundle()
    b35["sesiones"][0]["log"] = [L422]
    r = pr.llama(350, "verificar_caso", b35)
    sc = r["result"]["structuredContent"]
    et = [c["etiqueta"] for c in sc["hallazgos"][0]["citas"]] if sc["hallazgos"] else []
    mira("P35 [S16] 422 con AA: sin preguntas, no provisional, cita [S16]", sc["preguntas_abiertas"] == [] and sc["veredicto"]["provisional"] is False
         and "[S16]" in et, (sc["veredicto"], et))
    r = pr.llama(32, "verificar_caso", dict(b6, ocultar_datos_personales=True))
    s = json.dumps(r["result"]["structuredContent"]["hallazgos"] + [r["result"]["structuredContent"]["hechos_de_tabla"]], ensure_ascii=False)
    todo = json.dumps(r["result"]["structuredContent"], ensure_ascii=False).replace(json.dumps(r["result"]["structuredContent"]["version"]), "")
    mira("P28 ocultar datos personales", not any(x in todo for x in ("Apellido", "Nombre", "ID1", "19600910"))
         and [h["id"] for h in r["result"]["structuredContent"]["hallazgos"]] == [h["id"] for h in sc6["hallazgos"]], [x for x in ("Apellido", "Nombre", "ID1", "19600910") if x in todo])
    r = pr.llama(33, "info_verificador", {})
    sc = r["result"]["structuredContent"]
    import mcp_verificador as M
    largas = [k for k, c in M.CITAS.items() if c["texto"] and len(c["texto"].split()) > 25]
    mira("P29 info: preguntas, leyenda de 6 certezas, citas ≤ 25 palabras, S6-S29, L17-L18, A-7/A-14/AMB-5 cerrados",
         "Q-AMB-3" not in sc["preguntas_pendientes"]
         and sc["preguntas_pendientes"] == ["Q-AMB-10", "Q-DV1", "Q-MI-V-6", "Q-MI-V-7", "Q-MS-10"]    # 14k: Q-MS-9 cerrada (S105); Q-VE-A-2
         and len(sc["leyenda"]["certeza"]) == 6
         and not largas and "L19" in sc["limites"] and "[E2 §2.9]" in M.CITAS and "S36" in sc["limites"]["L9"] and "S37" in sc["limites"]["L19"]
         and all("[S%d]" % n in M.CITAS for n in range(6, 47)) and sc["ambiguedades_cerradas"].get("AMB-3") == "S14"
         and "<0x0A>" in sc["limites"]["L1"] and "byte de control" in M.DECISIONES["S31"]
         and sc["ambiguedades_cerradas"].get("AMB-5") == "S25" and "L17" in sc["limites"] and "L18" in sc["limites"]
         and "[T0104]" in M.CITAS and sc["supuestos"]["A-7"].startswith("Cerrado por S19")
         and sc["supuestos"]["A-14"].startswith("Cerrado por S25")
         and sc["version"]["nivel"] == "consumido", (largas, sc["preguntas_pendientes"]))
    # --- S19-S29 y ficha (diseno-s19-s21-fable.md)
    E04 = "una fila de la tabla de consulta del sexo cambió: F -> 'male'"
    L05_400 = {"tipo": "Warning", "componente": "FhirPatient", "texto": 'FHIR rechazo el recurso (MSH-10=MSG1): FHIR devolvio 400: {"resourceType":"OperationOutcome","issue":[{"severity":"error","code":"invalid","diagnostics":"<HSFHIRErr>IllegalControlChar"}]}'}
    L06 = {"tipo": "Error", "componente": "FhirPatient", "texto": 'FHIR fallo del lado servidor (MSH-10=MSG1): FHIR devolvio 503: {"resourceType": "OperationOutcome", "issue": [{"severity": "error", "code": "transient"}]}'}
    L07 = {"tipo": "Error", "componente": "FhirPatient", "texto": "No se pudo hablar con FHIR (MSH-10=MSG1): ERROR #6059: Unable to open TCP/IP socket to server localhost:59999"}
    AH = ACK.split("\n")[0] + "\n"

    def bb(segs=None, log=(L01,), canon=CAN, ack=ACK, entorno=()):
        s = {"log": list(log)}
        if canon is not None:
            s["canonico"] = dict(canon)
        return {"mensaje": cable(segs or B), "ack": ack, "sesiones": [s], "conexion": CX, "entorno": list(entorno)}

    def et(x):
        return [c["etiqueta"] for c in x.get("citas", [])]
    F_ = AR._con({("PID", 8): "F"})
    sc = pr.llama(360, "verificar_caso", bb(F_, canon=dict(CAN, Gender="male"), entorno=[E04]))["result"]["structuredContent"]
    v, h0 = sc["veredicto"], (sc["hallazgos"] or [{}])[0]
    mira("P36 [S20] tabla alterada: fallo_entorno/tabla, entorno con [S20] y [M], tabla_sexo",
         v["categoria"] == "fallo_entorno" and v["subtipo"] == "tabla" and v["provisional"] is False and sc["preguntas_abiertas"] == []
         and h0.get("clase") == "entorno" and h0.get("causa") == "entorno:tabla" and "[S20]" in et(h0) and "[M]" in et(h0)
         and len(sc["lectura"]["tabla_sexo"]) == 1, (v, et(h0)))
    sc = pr.llama(361, "comparar_canonico", {"mensaje": cable(F_), "canonico": dict(CAN, Gender="male"), "ack": ACK})["result"]["structuredContent"]
    d = sc["mensajes"][0]["discrepancias"]
    mira("P36b comparar_canonico sin entorno: discrepancia de Gender", len(d) == 1 and d[0]["campo"] == "Gender" and d[0]["esperado"] == "female"
         and d[0]["observado"] == "male", d)
    sc = pr.llama(362, "verificar_caso", bb(F_, canon=dict(CAN, Gender="male", FamilyName="Apelido"), entorno=[E04]))["result"]["structuredContent"]
    mira("P36c [S23] ambos/guardado+tabla con cita [S23]", sc["veredicto"]["categoria"] == "ambos" and sc["veredicto"]["subtipo"] == "guardado+tabla"
         and sc["resumen_mecanico"].startswith("ambos/guardado+tabla") and "[S23]" in et(sc["veredicto"]), sc["veredicto"])
    sc = pr.llama(370, "verificar_caso", bb(AR._con({("MSH", 12): "2.6"})))["result"]["structuredContent"]
    mira("P37 [S19] 2.6: correcto, nota S19, L17, version_msh12", sc["veredicto"]["categoria"] == "correcto" and any("[S19]" in n for n in sc["notas"])
         and "L17" in sc["limites"] and sc["acuse"]["esperado"][0]["version_msh12"]["aceptada"] is True, (sc["veredicto"], sc["limites"]))
    sc = pr.llama(371, "acuse_esperado", {"mensaje": cable(AR._con({("MSH", 12): "2.3"})), "ack": AH + "MSA|AR|MSG1\nERR|||203|E"})["result"]["structuredContent"]
    m0 = sc["mensajes"][0]
    mira("P37b 2.3 + AR 203: coincide, citas [S19] [T0104] [E2 §2.9.2.1 b]", m0["acuse"] == "coincide"
         and all(c in et(m0["esperado"]["err"][0]) for c in ("[S19]", "[T0104]", "[E2 §2.9.2.1 b]")), m0)
    sc = pr.llama(380, "consultar_tabla", {"tabla": "0104", "valor": "2.6"})["result"]["structuredContent"]
    mira("P38 tabla 0104 valor 2.6: 8 códigos, no literal, nota S19 aceptada", len(sc["entradas"]) == 8 and sc["consulta"]["presente_literal"] is False
         and "[S19]" in (sc["consulta"]["nota"] or "") and "aceptad" in (sc["consulta"]["nota"] or ""), sc["consulta"])
    sc = pr.llama(381, "consultar_tabla", {"tabla": "0104", "valor": "2.3"})["result"]["structuredContent"]
    mira("P38b 0104 valor 2.3: literal, no aceptada", sc["consulta"]["presente_literal"] is True and "no aceptada" in (sc["consulta"]["nota"] or ""),
         sc["consulta"])
    f02 = [B[0], " " + B[1], B[3], B[2]]
    sc = pr.llama(390, "verificar_caso", dict(bb(f02), incluir_ficha=True))["result"]["structuredContent"]
    lin = "MSH «·EVN»? PV1 PID! | faltan: EVN  (? no reconocido, ! fuera de orden, + repetido; orden [E3 §3.3.1]: MSH EVN PID PV1)"
    mira("P39 segmentos en entrada y ficha; hallazgo EVN", sc["entrada"]["mensajes"][0]["segmentos"] == lin and ("SEGMENTOS  " + lin) in sc["ficha"]
         and sc["hallazgos"][0]["hecho"] == "EVN", sc["entrada"]["mensajes"][0].get("segmentos"))
    f05 = [B[0], B[1], "PID1||XY9^^^HOSP^MR||Apellido^Nombre", B[3]]
    s = json.dumps(pr.llama(391, "verificar_caso", dict(bb(f05, canon=None), ocultar_datos_personales=True))["result"]["structuredContent"], ensure_ascii=False)
    mira("P39b ocultar sobre F05: sin Apellido ni XY9", "Apellido" not in s and "XY9" not in s, [x for x in ("Apellido", "XY9") if x in s])
    NUL = AR._con({("PID", 5): "<0xC0><0x80>Señor^Ana"})
    sc = pr.llama(400, "verificar_caso", bb(NUL, log=[L05_400], canon=None, ack=AH + "MSA|AR|MSG1\nERR|||102|E"))["result"]["structuredContent"]
    t21 = [x for x in sc["tolerancias"] if x["subtipo"] == "S21"]
    mira("P40 [S21] NUL + 400 + AR 102: correcto, tolerancia S21 con [S21] y [F §3.1.0.8] 400",
         sc["veredicto"]["categoria"] == "correcto" and sc["hallazgos"] == [] and t21 and "[S21]" in et(t21[0])
         and "[F §3.1.0.8] 400" in et(t21[0]) and sc["preguntas_abiertas"] == [] and sc["veredicto"]["provisional"] is False,
         (sc["veredicto"], [et(x) for x in t21]))
    m0 = pr.llama(401, "acuse_esperado", {"mensaje": cable(NUL), "ack": AH + "MSA|AR|MSG1\nERR|||102|E", "sesiones": [{"log": [L05_400]}]}
                  )["result"]["structuredContent"]["mensajes"][0]
    d1 = [d for d in m0["discrepancias"] if d["id"] == "D1"]
    mira("P40b acuse_esperado: coincide, D1 tolerado con [S21]", m0["acuse"] == "coincide" and d1 and d1[0]["cuenta"] is False
         and d1[0]["causa"] == "rechazo_del_destino" and "[S21]" in et(d1[0]), m0["discrepancias"])
    sc = pr.llama(402, "verificar_caso", bb(NUL, log=[], canon=None, ack=AH + "MSA|AR|MSG1\nERR|||102|E"))["result"]["structuredContent"]
    mira("P40c NUL sin log + AR 102: acuse_incorrecto, sin tolerancia S21", sc["veredicto"]["categoria"] == "acuse_incorrecto"
         and not [x for x in sc["tolerancias"] if x["subtipo"] == "S21"], sc["veredicto"])
    X_ = AR._con({("PID", 8): "X"})
    sc = pr.llama(410, "verificar_caso", bb(X_, log=[L06], canon=None, ack=AH + "MSA|AR|MSG1\nERR|||207|E"))["result"]["structuredContent"]
    mira("P41 [S25] X + 503 + AR 207: correcto, nota S25, contenido no acusado", sc["veredicto"]["categoria"] == "correcto"
         and sc["preguntas_abiertas"] == [] and sc["veredicto"]["provisional"] is False and any("[S25]" in n for n in sc["notas"])
         and len(sc["acuse"]["esperado"][0]["contenido_no_acusado"]) == 1, sc["veredicto"])
    sc = pr.llama(411, "verificar_caso", bb(X_, log=[L06], canon=dict(CAN, Gender="unknown")))["result"]["structuredContent"]
    hd = [h for h in sc["hallazgos"] if h["hecho"] == "destino"]
    hp = [h for h in sc["hallazgos"] if h["hecho"] == "PID-8"]
    mira("P41b X + 503 + AA: destino con [S25] y [E2 §2.9.2.2 c]; PID-8 con [T0357] 103 y [S25]",
         sc["veredicto"]["categoria"] == "fallo_silencioso" and hd and "[S25]" in et(hd[0]) and "[E2 §2.9.2.2 c]" in et(hd[0])
         and hp and "[T0357] 103" in et(hp[0]) and "[S25]" in et(hp[0]), ([et(h) for h in hd], [et(h) for h in hp]))
    m0 = pr.llama(412, "acuse_esperado", {"mensaje": cable(X_), "sesiones": [{"log": [L07]}]})["result"]["structuredContent"]["mensajes"][0]
    mira("P41c acuse_esperado X + L07: AR 207 con [S25], contenido 103", m0["esperado"]["msa1"] == "AR" and m0["esperado"]["err"][0]["err3"] == "207"
         and "[S25]" in et(m0["esperado"]["err"][0]) and m0["esperado"]["contenido_no_acusado"][0]["err3"] == "103", m0["esperado"])
    X26 = AR._con({("MSH", 12): "2.6", ("PID", 8): "X"})
    sc = pr.llama(420, "verificar_caso", bb(X26, canon=dict(CAN, Gender="unknown")))["result"]["structuredContent"]
    t22 = [x for x in sc["tolerancias"] if x["subtipo"] == "S22"]
    mira("P42 [S22] 2.6 + X: correcto, tolerancia S22 con [S22] y [E2 §2.8], límites L17 y L18",
         sc["veredicto"]["categoria"] == "correcto" and t22 and "[S22]" in et(t22[0]) and "[E2 §2.8]" in et(t22[0])
         and "L17" in sc["limites"] and "L18" in sc["limites"], (sc["limites"], [et(x) for x in t22]))
    d = pr.llama(421, "comparar_canonico", {"mensaje": cable(X26), "canonico": dict(CAN, Gender="X"), "ack": ACK}
                 )["result"]["structuredContent"]["mensajes"][0]["discrepancias"]
    mira("P42b comparar_canonico 2.6 + Gender X: cita [F AdministrativeGender]", len(d) == 1 and d[0]["campo"] == "Gender" and d[0]["observado"] == "X"
         and "[F AdministrativeGender]" in et(d[0]), d)
    sc = pr.llama(430, "verificar_caso", bb(X26, log=[], canon=None, ack=AH + "MSA|AE|MSG1\nERR|||103|E"))["result"]["structuredContent"]
    t26 = [x for x in sc["tolerancias"] if x["subtipo"] == "S26"]
    mira("P43 [S26] 2.6 + X + AE 103: correcto, tolerancia S26 con [S26] [S22] [T0357] 103, una alternativa",
         sc["veredicto"]["categoria"] == "correcto" and t26 and all(c in et(t26[0]) for c in ("[S26]", "[S22]", "[T0357] 103"))
         and sc["preguntas_abiertas"] == [] and len(sc["acuse"]["esperado"][0]["alternativas_aceptadas"]) == 1, [et(x) for x in t26])
    m0 = pr.llama(431, "acuse_esperado", {"mensaje": cable(X_), "ack": AH + "MSA|AE|MSG1\nERR|||103|E", "sesiones": [{"log": [L06]}]}
                  )["result"]["structuredContent"]["mensajes"][0]
    al = m0["esperado"]["alternativas_aceptadas"]
    d1 = [d for d in m0["discrepancias"] if d["id"] == "D1"]
    mira("P43b [S28] acuse_esperado X + 503 + AE 103: AR 207, alternativa S28, D1 no cuenta, coincide",
         m0["esperado"]["msa1"] == "AR" and m0["esperado"]["err"][0]["err3"] == "207" and al
         and {k: al[0][k] for k in ("msa1", "err3", "donde", "por")} == {"msa1": "AE", "err3": "103", "donde": "PID-8", "por": "S28"}
         and "[S28]" in et(al[0]) and d1 and d1[0]["cuenta"] is False and d1[0]["causa"] == "alternativa_S28" and m0["acuse"] == "coincide", m0)
    m0 = pr.llama(432, "acuse_esperado", {"mensaje": cable(X_), "ack": AH + "MSA|AE|MSG1\nERR|||102|E", "sesiones": [{"log": [L06]}]}
                  )["result"]["structuredContent"]["mensajes"][0]
    mira("P43c AE 102: discrepa, D1 y D2 cuentan", m0["acuse"] == "discrepa"
         and sorted((d["id"], d["cuenta"]) for d in m0["discrepancias"]) == [("D1", True), ("D2", True)], m0["discrepancias"])
    # --- S30 (diseno-s30-fable.md)
    FER = AR._con({("PID", 5): "     Fernández^María Elena^Lucia^^^^L"})
    CFER = dict(CAN, FamilyName="Fernández", GivenName="María Elena Lucia")
    sc = pr.llama(440, "verificar_caso", bb(FER, canon=CFER))["result"]["structuredContent"]
    t30 = sc["tolerancias"][0] if sc["tolerancias"] else {}
    mira("P44 [S30] caso origen: correcto, tolerancia S30 en PID-5 con [S30] y [C] nombres, L19",
         sc["veredicto"]["categoria"] == "correcto" and sc["veredicto"]["provisional"] is False and sc["preguntas_abiertas"] == []
         and sc["hallazgos"] == [] and t30.get("subtipo") == "S30" and t30.get("hecho") == "PID-5"
         and "[S30]" in et(t30) and "[C] nombres" in et(t30) and "L19" in sc["limites"], (sc["veredicto"], t30, sc["limites"]))
    m0 = pr.llama(441, "comparar_canonico", {"mensaje": cable(FER), "canonico": CFER, "ack": ACK})["result"]["structuredContent"]["mensajes"][0]
    mira("P44b comparar_canonico: sin discrepancias, tolerancia S30 con cita, esperado con blancos",
         m0["discrepancias"] == [] and m0["tolerancias"][0]["que"].startswith("[S30] FamilyName") and "[S30]" in et(m0["tolerancias"][0])
         and m0["canonico_esperado"]["FamilyName"] == "     Fernández", m0)
    sc = pr.llama(442, "verificar_caso", bb(AR._con({("PID", 5): "Fernández   ^María Elena^Lucia^^^^L"}), canon=CFER))["result"]["structuredContent"]
    v = sc["veredicto"]
    t0 = sc["tolerancias"][0] if sc["tolerancias"] else {}
    mira("P45e [S32] blancos finales: correcto, tolerancia S32 con [S32] y [C] nombres", v["categoria"] == "correcto"
         and v["provisional"] is False and sc["preguntas_abiertas"] == [] and t0.get("subtipo") == "S32"
         and "[S32]" in et(t0) and "[C] nombres" in et(t0), (v, t0))
    sc = pr.llama(443, "verificar_caso", dict(bb(FER, canon=CFER), ocultar_datos_personales=True))["result"]["structuredContent"]
    todo = json.dumps(sc, ensure_ascii=False).replace(json.dumps(sc["version"], ensure_ascii=False), "")
    mira("P44d ocultar sobre S30: sin Fernández, María ni Lucia", not any(x in todo for x in ("Fernández", "María", "Lucia"))
         and sc["tolerancias"] and sc["tolerancias"][0]["subtipo"] == "S30", [x for x in ("Fernández", "María", "Lucia") if x in todo])
    d = pr.llama(444, "comparar_canonico", {"mensaje": cable(AR._con({("PID", 5): "Fernández^María Elena^ Lucia^^^^L"})), "canonico": CFER,
                                           "ack": ACK})["result"]["structuredContent"]["mensajes"][0]["discrepancias"]
    m0 = pr.llama(445, "comparar_canonico", {"mensaje": cable(AR._con({("PID", 5): "Fernández^María Elena^ Lucia^^^^L"})), "canonico": CFER,
                                            "ack": ACK})["result"]["structuredContent"]["mensajes"][0]
    mira("P45f [S34] comparar_canonico PID-5.3 con blanco: tolerancia S34", d == [] and m0["tolerancias"][0]["que"].startswith("[S34] GivenName")
         and "[S34]" in et(m0["tolerancias"][0]) and "[C] nombres" in et(m0["tolerancias"][0]), m0)
    # --- S31, S35, S36, S37
    L03 = {"tipo": "Warning", "componente": "FhirPatient", "texto": "Mensaje rechazado antes de FHIR (MSH-10=MSG1): Falta el identificador del paciente (PID-3.1): no se puede crear un Patient sin identificador"}
    ORIGEN = "<VT><VT>" + B[0] + "\n<FS>\n<VT>" + "\n".join(B[1:]) + "\n<FS>\n<FS>"
    PARTIDA_PV1 = "<VT>" + "\n".join(B[:3]) + "\n<FS><VT>" + B[3] + "\n<FS>"
    AK101 = AH + "MSA|AR|MSG1\nERR|||101|E"
    OR = {"mensaje": ORIGEN, "ack": AK101, "sesiones": [{"log": [L03]}], "conexion": CX, "entorno": []}
    sc = pr.llama(450, "verificar_caso", OR)["result"]["structuredContent"]
    t0 = sc["tolerancias"][0] if sc["tolerancias"] else {}
    mira("P45 [S31] caso origen: correcto, tolerancia S31 en trama con citas, trama, marco, L9, nota",
         sc["veredicto"]["categoria"] == "correcto" and sc["veredicto"]["provisional"] is False and sc["preguntas_abiertas"] == []
         and sc["hallazgos"] == [] and t0.get("subtipo") == "S31" and t0.get("hecho") == "trama"
         and all(c in et(t0) for c in ("[S31]", "[E3 §3.3.1]", "[T0357] 100", "[T0357] 101", "[E2 §2.9]"))
         and sc["entrada"]["trama"] == {"marcos": 2, "sin_msh": [2], "anomalias": ["marcador <VT> repetido (marco 1)", "marcador <FS> repetido (tras el marco 2)"]}
         and sc["entrada"]["mensajes"][0]["marco"] == 1 and sc["entrada"]["mensajes"][0]["segmentos"] == "MSH | faltan: EVN PID PV1"
         and "L9" in sc["limites"] and any(n.startswith("[S31]") for n in sc["notas"]), (sc["veredicto"], t0, sc["entrada"].get("trama"), sc["limites"]))
    sc = pr.llama(451, "acuse_esperado", OR)["result"]["structuredContent"]
    m0 = sc["mensajes"][0]
    d1 = [d for d in m0["discrepancias"] if d["id"] == "D1"]
    al = m0["esperado"]["alternativas_aceptadas"]
    mira("P45b acuse_esperado: coincide, D1 S31, esperado AE 100, alternativas, marco, trama", m0["acuse"] == "coincide" and d1
         and d1[0]["cuenta"] is False and d1[0]["causa"] == "alternativa_S31" and "[S31]" in et(d1[0]) and m0["esperado"]["msa1"] == "AE"
         and m0["esperado"]["err"][0]["err3"] == "100" and al and (al[0]["msa1"], al[0]["err3"], al[0]["donde"], al[0]["por"]) == ("AR", "101", "trama", "S31")
         and m0["esperado"]["marco"]["solo_msh"] is True and sc["trama"]["sin_msh"] == [2], m0)
    sc = pr.llama(452, "verificar_caso", dict(OR, ack=AH + "MSA|AE|MSG1\nERR|||101|E"))["result"]["structuredContent"]
    t0 = sc["tolerancias"][0] if sc["tolerancias"] else {}
    mira("P45c [S35] AE 101: correcto, tolerancia S35 con [S35], [S31], [T0357] 101", sc["veredicto"]["categoria"] == "correcto"
         and sc["veredicto"]["provisional"] is False and sc["preguntas_abiertas"] == [] and t0.get("subtipo") == "S35" and t0.get("hecho") == "trama"
         and all(c in et(t0) for c in ("[S35]", "[S31]", "[T0357] 101")), (sc["veredicto"], t0))
    sc = pr.llama(453, "verificar_caso", dict(bb(), mensaje="\n".join(B) + "\n<FS>"))["result"]["structuredContent"]
    mira("P45d SIN_VT: correcto, nota [A-2], un marco", sc["veredicto"]["categoria"] == "correcto" and "[A-2] trama: marco 1 sin <VT>" in sc["notas"]
         and sc["entrada"]["trama"]["marcos"] == 1, (sc["veredicto"], sc["notas"]))
    sc = pr.llama(454, "verificar_caso", bb(AR._con({("PID", 5): "\u2028Fernández^María Elena^Lucia^^^^L"}), canon=CFER))["result"]["structuredContent"]
    t0 = sc["tolerancias"][0] if sc["tolerancias"] else {}
    mira("P45g [S37] U+2028: correcto, tolerancia S30 con [S30] [S33] [S37] [C] nombres", sc["veredicto"]["categoria"] == "correcto"
         and t0.get("subtipo") == "S30" and all(c in et(t0) for c in ("[S30]", "[S33]", "[S37]", "[C] nombres")), (sc["veredicto"], t0))
    sc = pr.llama(455, "verificar_caso", bb(AR._con({("PID", 5): "  Fernández  ^María Elena^ Lucia\u00a0^^^^L"}), canon=CFER))["result"]["structuredContent"]
    mira("P45h combinado: correcto, S30 y S32, la segunda con [S32] [S33] [S34]", sc["veredicto"]["categoria"] == "correcto"
         and [x["subtipo"] for x in sc["tolerancias"]] == ["S30", "S32"] and all(c in et(sc["tolerancias"][1]) for c in ("[S32]", "[S33]", "[S34]")),
         [(x["subtipo"], et(x)) for x in sc["tolerancias"]])
    sc = pr.llama(456, "verificar_caso", dict(OR, ocultar_datos_personales=True, incluir_ficha=True))["result"]["structuredContent"]
    lt = [l for l in sc["ficha"].split("\n") if l.startswith("TRAMA")]
    mira("P45i ocultar: línea TRAMA sin datos, trama igual", lt and not any(x in lt[0] for x in ("Apellido", "Nombre", "ID1"))
         and sc["entrada"]["trama"]["sin_msh"] == [2], lt)
    sc = pr.llama(460, "verificar_caso", dict(OR, ack=AH + "MSA|AR|MSG1\nERR|||100|E"))["result"]["structuredContent"]
    t0 = sc["tolerancias"][0] if sc["tolerancias"] else {}
    mira("P46 [S35] AR 100: correcto, tolerancia S35 con [S35] [S31] [T0357] 100", sc["veredicto"]["categoria"] == "correcto"
         and sc["veredicto"]["provisional"] is False and t0.get("subtipo") == "S35" and all(c in et(t0) for c in ("[S35]", "[S31]", "[T0357] 100")), t0)
    P36B = {"mensaje": PARTIDA_PV1, "ack": AK101, "sesiones": [{"log": [L03]}], "conexion": CX}
    sc = pr.llama(461, "verificar_caso", P36B)["result"]["structuredContent"]
    t0 = sc["tolerancias"][0] if sc["tolerancias"] else {}
    mira("P46b [S36] PARTIDA_PV1: correcto, tolerancia S36 con [S36] [S31] [E3 §3.3.1], trama, nota", sc["veredicto"]["categoria"] == "correcto"
         and t0.get("subtipo") == "S36" and all(c in et(t0) for c in ("[S36]", "[S31]", "[E3 §3.3.1]")) and sc["entrada"]["trama"]["sin_msh"] == [2]
         and any(n.startswith("[S36]") for n in sc["notas"]), (sc["veredicto"], t0, sc["notas"]))
    m0 = pr.llama(462, "acuse_esperado", P36B)["result"]["structuredContent"]["mensajes"][0]
    al = m0["esperado"]["alternativas_aceptadas"]
    mira("P46c acuse_esperado S36: coincide, tres alternativas con [S36], D1 S36", m0["acuse"] == "coincide" and len(al) == 3
         and all(z["por"] == "S36" and "[S36]" in et(z) for z in al) and m0["discrepancias"]
         and (m0["discrepancias"][0]["id"], m0["discrepancias"][0]["cuenta"], m0["discrepancias"][0]["causa"]) == ("D1", False, "alternativa_S36"), m0)
    sc = pr.llama(463, "verificar_caso", bb(B[:3], log=[], ack=AK101, canon=None))["result"]["structuredContent"]
    mira("P46d sin partición + AR 101: acuse_incorrecto sin tolerancias de trama", sc["veredicto"]["categoria"] == "acuse_incorrecto"
         and not [x for x in sc["tolerancias"] if x["hecho"] == "trama"], sc["veredicto"])
    m0 = pr.llama(464, "comparar_canonico", {"mensaje": cable(AR._con({("PID", 5): "\u2028Pérez^Ana^Luz^^^^L"})),
                                            "canonico": dict(CAN, FamilyName="Pérez", GivenName="Ana Luz"), "ack": ACK})["result"]["structuredContent"]["mensajes"][0]
    mira("P46e comparar_canonico U+2028: tolerancia [S30][S33] con [S33] y [S37]", m0["discrepancias"] == []
         and m0["tolerancias"][0]["que"].startswith("[S30][S33] FamilyName") and all(c in et(m0["tolerancias"][0]) for c in ("[S33]", "[S37]")), m0)
    # --- arreglo solo_msh (diseno-arreglo-solo-msh-fable.md); base con MSH-18 al final (desviación declarada)
    BL = [B[0] + "||||||UNICODE UTF-8"] + B[1:]
    LF1 = "<VT>" + "<0x0A>".join(BL) + "<0x0A><FS>\n"
    LFB = {"mensaje": LF1, "ack": AH + "MSA|AR|MSG1\nERR|||101|E", "sesiones": [{"log": [L03]}], "conexion": CX, "entorno": []}
    sc = pr.llama(470, "verificar_caso", LFB)["result"]["structuredContent"]
    mira("P47 [E2 §2.5.4] LF en un marco con AR 101: acuse_incorrecto/codigo, sin tolerancias, segmentos, nota, L1",
         sc["veredicto"]["categoria"] == "acuse_incorrecto" and sc["veredicto"]["subtipo"] == "codigo" and sc["veredicto"]["provisional"] is False
         and sc["tolerancias"] == [] and sc["hallazgos"] and sc["hallazgos"][0]["hecho"] == "EVN"
         and sc["entrada"]["mensajes"][0]["segmentos"].endswith("tras control no CR: EVN PID PV1")
         and any(n.startswith("[E2 §2.5.4] el marco 1 trae ") for n in sc["notas"]) and "L1" in sc["limites"], (sc["veredicto"], sc["tolerancias"], sc["limites"]))
    m0 = pr.llama(471, "acuse_esperado", LFB)["result"]["structuredContent"]["mensajes"][0]
    mira("P47b acuse_esperado LF: sin alternativas, AE 100 x3, discrepa D1 y D2 que cuentan",
         m0["esperado"]["marco"]["solo_msh"] is False and m0["esperado"]["alternativas_aceptadas"] == [] and m0["esperado"]["msa1"] == "AE"
         and [e_["err3"] for e_ in m0["esperado"]["err"]] == ["100", "100", "100"] and m0["acuse"] == "discrepa"
         and [d["id"] for d in m0["discrepancias"]] == ["D1", "D2"] and all(d["cuenta"] for d in m0["discrepancias"]), m0)
    sc = pr.llama(472, "verificar_caso", OR)["result"]["structuredContent"]
    mira("P47c control S31 (= P45): correcto, tolerancia S31", sc["veredicto"]["categoria"] == "correcto" and sc["tolerancias"][0]["subtipo"] == "S31", sc["veredicto"])
    # --- HL7 V2 ACK Guidance (diseno-ack-guidance-fable.md; S40, A-19, L20)
    sc = pr.llama(700, "info_verificador", {})["result"]["structuredContent"]
    mira("P79f info: L21, S41 y el A-18 nuevo publicados; [A-18] y [S41] citables",
         "L21" in sc["limites"] and "S41" in sc["decisiones_sitio"] and "sin ventana" in sc["supuestos"]["A-18"]
         and "[A-18]" in M.CITAS and "[S41]" in M.CITAS, (list(sc["limites"])[-3:], sorted(sc["decisiones_sitio"])[-3:]))
    mira("P79 info: A-19, L20 y S40 publicados", "A-19" in sc["supuestos"] and "L20" in sc["limites"] and "S40" in json.dumps(sc["decisiones_sitio"], ensure_ascii=False),
         (list(sc["supuestos"])[-3:], list(sc["limites"])[-3:]))
    ackg = {k: v for k, v in M.CITAS.items() if k.startswith("[ACKG")}
    mira("P79d citas [ACKG]: todas con texto y fuente «no normativa»", len(ackg) == 14 and all(v["texto"] and "no normativa" in v["fuente"] for v in ackg.values()),
         [k for k, v in ackg.items() if not (v["texto"] and "no normativa" in v["fuente"])])
    m0 = pr.llama(701, "acuse_esperado", {"mensaje": cable(B[:3]), "ack": AH + "MSA|AE|MSG1\nERR|||100|E"})["result"]["structuredContent"]["mensajes"][0]
    e0 = [c["etiqueta"] for c in m0["esperado"]["err"][0]["citas"]] if m0["esperado"]["err"] else []
    mira("P79b error de contenido (falta PV1): el esperado cita AIRA AE, Base AE y A-19", {"[ACKG AIRA] AE", "[ACKG base] AE", "[A-19]"} <= set(e0), e0)
    sc = pr.llama(702, "verificar_caso", b35)["result"]["structuredContent"]
    e1 = [c["etiqueta"] for c in sc["hallazgos"][0]["citas"]] if sc["hallazgos"] else []
    mira("P79c [S16] 422: cita S16, AIRA AR, Lab AR y S40", {"[S16]", "[ACKG AIRA] AR", "[ACKG lab] AR", "[S40]"} <= set(e1), e1)
    sc = pr.llama(703, "verificar_caso", bundle())["result"]["structuredContent"]
    mira("P79e control: caso correcto sin citas [ACKG]", sc["veredicto"]["categoria"] == "correcto" and "[ACKG" not in json.dumps(sc["hallazgos"] + sc["menores"]), None)
    # --- S42 y S43 (diseno-s42-s43-fable.md)
    F3X = {"tipo": "Info", "componente": "FhirPatient", "texto": "algo nunca visto"}
    sc = pr.llama(800, "verificar_caso", bundle(sesiones=[{"log": [F3X], "canonico": dict(CAN)}]))["result"]["structuredContent"]
    mira("P80 [S42] fila desconocida sin terminal: indeterminado, cita [S42], límite L5",
         sc["veredicto"]["categoria"] == "indeterminado" and "[S42]" in [c["etiqueta"] for c in sc["veredicto"].get("citas", [])]
         and "L5" in sc["limites"] and "[S42]" in sc["resumen_mecanico"], (sc["veredicto"], sc["limites"], sc["resumen_mecanico"]))
    L05_INV = {"tipo": "Warning", "componente": "FhirPatient", "texto": 'FHIR rechazo el recurso (MSH-10=MSG1): FHIR devolvio 400: {"resourceType":"OperationOutcome","issue":[{"severity":"error","code":"invalid","diagnostics":"Invalid date"}]}'}
    P7B = AR._con({("PID", 7): "19600925"})
    sc = pr.llama(801, "verificar_caso", bundle(P7B, ack=AH + "MSA|AR|MSG1\nERR|||102|E",
                                                sesiones=[{"log": [L05_INV], "canonico": dict(CAN, BirthDate="1960-25-09")}]))["result"]["structuredContent"]
    h43 = [h for h in sc["hallazgos"] if h["subtipo"] == "transformado"]
    e43 = [c["etiqueta"] for c in h43[0]["citas"]] if h43 else []
    mira("P81 [S43] M03b: transformado con citas S43, BirthDate, 2.A.77 y 400; L22; resumen con +transformado; esperado «transformado»",
         {"[S43]", "[C] BirthDate", "[E2A §2.A.77]", "[F §3.1.0.8] 400"} <= set(e43) and "L22" in sc["limites"]
         and sc["resumen_mecanico"].startswith("acuse_incorrecto/codigo+transformado") and h43 and "transformado" in (h43[0]["esperado"] or {}),
         (e43, sc["limites"], sc["resumen_mecanico"]))
    sc = pr.llama(802, "verificar_caso", bundle(P7B, ack=AH + "MSA|AR|MSG1\nERR|||102|E",
                                                sesiones=[{"log": [L05_INV], "canonico": dict(CAN, BirthDate="1960-09-25")}]))["result"]["structuredContent"]
    n43 = [z for z in sc["menores"] if z["clase"] == "nota" and z["subtipo"] == "S43"]
    mira("P81b [S43] canónico bien: nota S43 en menores con cita [S43]; sigue acuse_incorrecto/codigo",
         n43 and "[S43]" in [c["etiqueta"] for c in n43[0]["citas"]] and sc["veredicto"]["subtipo"] == "codigo", (n43, sc["veredicto"]))
    sc = pr.llama(803, "info_verificador", {})["result"]["structuredContent"]
    mira("P82 info: S42, S43 y L22 publicados; L5 nombra S42; [S42] y [S43] citables",
         "S42" in sc["decisiones_sitio"] and "S43" in sc["decisiones_sitio"] and "L22" in sc["limites"] and "S42" in sc["limites"]["L5"]
         and "[S42]" in M.CITAS and "[S43]" in M.CITAS, (sorted(sc["decisiones_sitio"])[-3:], list(sc["limites"])[-3:]))
    m0 = pr.llama(804, "acuse_esperado", {"mensaje": cable(B), "ack": ACK})["result"]["structuredContent"]["mensajes"][0]
    mira("P83 acuse_esperado con solo mensaje y ACK: AA sin discrepancias (S42 no lo toca)",
         m0["esperado"]["msa1"] == "AA" and m0["acuse"] != "discrepa" and "S42" not in json.dumps(m0, ensure_ascii=False), m0)
    # --- citas, S38, S39 y MSH-18 (diseno-citas-s38-s39-fable.md)
    GARCIA = "García^Lucía^Óscar^^^^L"
    MOJI = dict(CAN, FamilyName="García".encode("utf-8").decode("latin-1"), GivenName="Lucía Óscar".encode("utf-8").decode("latin-1"))

    def c38(msh18, pid5=GARCIA, canon=MOJI):
        campos = {("PID", 5): pid5}
        if msh18 is not None:
            campos[("MSH", 18)] = msh18
        return dict(bb(AR._con(campos), canon=canon), incluir_ficha=True)

    def etq(z):
        return [c["etiqueta"] for c in z["citas"]]
    sc = pr.llama(480, "verificar_caso", c38("ASCII"))["result"]["structuredContent"]
    h0 = sc["hallazgos"][0] if sc["hallazgos"] else {"citas": []}
    n39 = [z for z in sc["menores"] if z["clase"] == "nota" and z["subtipo"] == "S39"]
    mira("P48 caso real: citas [S38] y MSH-18, sin [S7] ni [E2 §2.7]; nota S39; ficha; contradicción en el acuse",
         sc["veredicto"]["categoria"] == "fallo_silencioso" and sc["veredicto"]["subtipo"] == "guardado" and h0.get("hecho") == "PID-5"
         and {"[C] nombres", "[S38]", "[E2 §2.15.9.18]", "[T0211] ASCII"} <= set(etq(h0))
         and not {"[S7]", "[E2 §2.7]", "[S9]"} & set(etq(h0))
         and len(n39) == 1 and n39[0]["hecho"] == "MSH-18" and {"[S39]", "[E2 §2.15.9.18]", "[T0211] ASCII"} <= set(etq(n39[0]))
         and "MSH-18=ASCII" in sc.get("ficha", "")
         and sc["acuse"]["esperado"][0]["descodificacion"]["contradiccion"]["motivo"] == "utf8_multibyte", (etq(h0), sc["menores"]))
    sc = pr.llama(481, "verificar_caso", c38(None))["result"]["structuredContent"]
    n39 = [z for z in sc["menores"] if z["subtipo"] == "S39"]
    mira("P48b sin MSH-18: mismas citas; nota «ausente»", {"[S38]", "[T0211] ASCII"} <= set(etq(sc["hallazgos"][0]))
         and len(n39) == 1 and "ausente" in n39[0]["que"][0], (etq(sc["hallazgos"][0]), sc["menores"]))
    sc = pr.llama(482, "verificar_caso", c38("UNICODE UTF-8"))["result"]["structuredContent"]
    mira("P48c UNICODE UTF-8: [T0211] UNICODE UTF-8, sin menores", "[T0211] UNICODE UTF-8" in etq(sc["hallazgos"][0]) and sc["menores"] == [],
         (etq(sc["hallazgos"][0]), sc["menores"]))
    sc = pr.llama(483, "verificar_caso", c38("ASCII", canon=dict(CAN, FamilyName="García", GivenName="Lucía Óscar")))["result"]["structuredContent"]
    mira("P48d ASCII + UTF-8 bien guardado: correcto con la nota S39", sc["veredicto"]["categoria"] == "correcto" and sc["hallazgos"] == []
         and [z["subtipo"] for z in sc["menores"]] == ["S39"], (sc["veredicto"], sc["menores"]))
    sc = pr.llama(484, "verificar_caso", c38("ASCII", pid5="Garcia^Lucia^^^^^L", canon=dict(CAN, FamilyName="Garca", GivenName="Lucia")))["result"]["structuredContent"]
    mira("P48e ASCII puro, letra perdida: solo [C] nombres, sin menores", etq(sc["hallazgos"][0]) == ["[C] nombres"] and sc["menores"] == [],
         (etq(sc["hallazgos"][0]), sc["menores"]))
    sc = pr.llama(485, "verificar_caso", bb(AR._con({("PID", 5): "Ferr\\S\\Soler^Ana"}), canon=dict(CAN, FamilyName="Ferr\\S\\Soler", GivenName="Ana")))["result"]["structuredContent"]
    e = etq(sc["hallazgos"][0])
    mira("P49 escape sin resolver: [S8] y [E2 §2.7], sin [S7] ni [S38]", "[S8]" in e and "[E2 §2.7]" in e and "[S7]" not in e and "[S38]" not in e, e)
    sc = pr.llama(486, "verificar_caso", bb(AR._con({("PID", 5): "Ferr\\S\\Soler^Ana"}), canon=dict(CAN, FamilyName="Ferr^Sole", GivenName="Ana")))["result"]["structuredContent"]
    e = etq(sc["hallazgos"][0])
    mira("P49b escape resuelto y letra perdida: [E2 §2.7] sin [S8]", "[E2 §2.7]" in e and "[S8]" not in e, e)
    sc = pr.llama(487, "verificar_caso", bb(AR._con({("PID", 5): "Apellido\u200b^Nombre"}), canon=dict(CAN, FamilyName="Apellido")))["result"]["structuredContent"]
    e = etq(sc["hallazgos"][0])
    mira("P50 invisible en la entrada: [S7], sin [E2 §2.7]", "[S7]" in e and "[E2 §2.7]" not in e, e)
    sc = pr.llama(488, "verificar_caso", bb(AR._con({("PID", 5): "Apellido^Nombre"}), canon=dict(CAN, FamilyName="Apellido\u200b")))["result"]["structuredContent"]
    mira("P50b invisible solo en lo guardado: sin [S7]", "[S7]" not in etq(sc["hallazgos"][0]), etq(sc["hallazgos"][0]))
    sc = pr.llama(489, "verificar_caso", bb(AR._con({("PID", 5): "Mu<0xF1>oz^Ana"}), canon=dict(CAN, FamilyName="Mu?oz", GivenName="Ana")))["result"]["structuredContent"]
    e = etq(sc["hallazgos"][0])
    n39 = [z for z in sc["menores"] if z["subtipo"] == "S39"]
    mira("P51 byte F1 (S9): [S9] y [E2 §2.15.9.18]; nota S39 callada por S9", "[S9]" in e and "[E2 §2.15.9.18]" in e and n39 == [],
         (e, sc["menores"]))
    m0 = pr.llama(490, "comparar_canonico", {"mensaje": cable(AR._con({("MSH", 18): "ASCII", ("PID", 5): GARCIA})), "canonico": MOJI, "ack": ACK})["result"]["structuredContent"]["mensajes"][0]
    e = [c["etiqueta"] for c in m0["discrepancias"][0]["citas"]] if m0["discrepancias"] else []
    mira("P52 comparar_canonico del caso real: [C] nombres y [S38], sin [E2 §2.7] ni [S7]",
         {"[C] nombres", "[S38]"} <= set(e) and "[E2 §2.7]" not in e and "[S7]" not in e, m0)
    r1 = init(pr)
    r = pr.envia({"jsonrpc": "2.0", "id": 34, "method": "tools/list"})
    mira("P30 initialize dos veces", r1["result"]["protocolVersion"] == "2025-06-18" and len(r["result"]["tools"]) == 6, None)
    codigo, dur, err = pr.cierra()
    lineas_ok = all(json.loads(l).get("jsonrpc") == "2.0" for l in pr.salida if l)
    mira("P24 stdout solo JSON-RPC; stderr sin datos de la evidencia", lineas_ok and not any(x in err for x in ("MSG1", "Apellido", "ID1")),
         [x for x in ("MSG1", "Apellido", "ID1") if x in err])
    mira("P25 EOF: salida 0 en < 1 s", codigo == 0 and dur < 1, (codigo, dur))
    # procesos nuevos
    for v, esperado, nom in (("2024-11-05", "2025-06-18", "P02b"), ("2099-01-01", "2025-11-25", "P02c")):
        p2 = Proc(servidor)
        mira(nom + " negociación %s -> %s" % (v, esperado), init(p2, v)["result"]["protocolVersion"] == esperado, None)
        p2.cierra()
    p2 = Proc(servidor)
    r = p2.envia({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    mira("P18 tools/list sin initialize: -32600 con versiones", r.get("error", {}).get("code") == -32600
         and "2025-06-18" in r["error"]["data"]["supported"] and "2026-07-28" in r["error"]["data"]["supported"], r)
    r = p2.envia({"jsonrpc": "2.0", "id": 2, "method": "server/discover"})
    mira("P20b server/discover sin _meta: -32600", r.get("error", {}).get("code") == -32600, r)
    p2.cierra()
    p3 = Proc(servidor)
    meta = {"io.modelcontextprotocol/protocolVersion": "2026-07-28"}
    r = p3.envia({"jsonrpc": "2.0", "id": "d1", "method": "server/discover", "params": {"_meta": meta}})
    res = r.get("result", {})
    mira("P19 server/discover moderno", res.get("resultType") == "complete" and res.get("supportedVersions") == ["2026-07-28"]
         and res["_meta"]["io.modelcontextprotocol/serverInfo"]["name"] and res.get("ttlMs") and res.get("cacheScope") == "public", r)
    r = p3.envia({"jsonrpc": "2.0", "id": "d2", "method": "tools/list", "params": {"_meta": meta}})
    mira("P19b tools/list moderno", r["result"].get("resultType") == "complete" and len(r["result"]["tools"]) == 6 and r["result"].get("ttlMs"), None)
    r = p3.llama("d3", "consultar_tabla", {"tabla": "0008"}, meta=meta)
    mira("P19c tools/call moderno", r["result"].get("resultType") == "complete" and r["result"]["structuredContent"]["tabla"] == "0008"
         and "io.modelcontextprotocol/serverInfo" in r["result"]["_meta"], None)
    r = p3.llama("d4", "consultar_tabla", {"tabla": "0008"}, meta={"io.modelcontextprotocol/protocolVersion": "2025-11-25"})
    mira("P20 moderno mal versionado: -32022", r.get("error", {}).get("code") == -32022 and r["error"]["data"]["supported"] == ["2026-07-28"]
         and r["error"]["data"]["requested"] == "2025-11-25", r)
    p3.cierra()
    p4 = Proc(servidor)
    init(p4)
    r = p4.llama(1, "verificar_caso", b6)
    salidas.append(json.dumps(r["result"]["structuredContent"], sort_keys=True))
    p4.cierra()
    mira("P22 determinismo: tres salidas idénticas (dos en el mismo proceso, una en otro)", len(set(salidas)) == 1, len(set(salidas)))
    if os.name == "posix":
        pruebas_http(servidor)
    sys.stderr.write("AUTOPRUEBA DE mcp_verificador: " + ("TODO BIEN" if not mal else "FALLAN %d" % len(mal)) + "\n")
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_verificador.py")))
