#!/usr/bin/env python3
"""Qwen Unbound Coder AI — auth + validation gateway (Python standard library only).

It does NOT generate text itself and it never invents a model reply.
It forwards OpenAI-compatible requests to a real llama-server instance and
returns a clear 503 when that backend is not reachable, so the frontend can
never show "online" unless a real health check succeeded.

Run:
    QWEN_API_KEY=choose-a-long-random-key \
    LLAMA_URL=http://127.0.0.1:8080 \
    GATEWAY_PORT=8000 python3 backend/gateway.py

Endpoints:
    GET  /health                 -> gateway + llama-server reachability
    GET  /v1/models              -> proxied from llama-server, or 503
    POST /v1/chat/completions    -> proxied, streaming passed through
"""
import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODEL = os.environ.get(
    "QWEN_MODEL", "JonathanColetti/Qwen3.8-27B-Uncensored-GGUF:Q4_K_M")
LLAMA_URL = os.environ.get("LLAMA_URL", "http://127.0.0.1:8080").rstrip("/")
API_KEY = os.environ.get("QWEN_API_KEY", "")
PORT = int(os.environ.get("GATEWAY_PORT", "8000"))
TIMEOUT = float(os.environ.get("GATEWAY_TIMEOUT", "300"))


def _json(handler, status, payload):
    body = json.dumps(payload).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def _llama_ok():
    try:
        req = urllib.request.Request(LLAMA_URL + "/health", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def _check_auth(handler):
    if not API_KEY:
        return True  # No key configured: gateway is open ONLY on localhost/notebook use.
    auth = handler.headers.get("Authorization", "")
    return auth == "Bearer " + API_KEY


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep notebook logs readable
        pass

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            ok = _llama_ok()
            return _json(self, 200, {
                "status": "online" if ok else "offline",
                "gateway": "ok",
                "model": MODEL,
                "backend_url": LLAMA_URL,
                "backend_reachable": ok,
            })
        if self.path == "/v1/models":
            if not _check_auth(self):
                return _json(self, 401, {"error": "unauthorized: missing or wrong API key"})
            if not _llama_ok():
                return _json(self, 503, {"error": "model backend offline"})
            try:
                req = urllib.request.Request(LLAMA_URL + "/v1/models")
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return _json(self, 200, json.loads(resp.read() or b"{}"))
            except Exception as exc:
                return _json(self, 502, {"error": f"backend error: {exc}"})
        return _json(self, 404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            return _json(self, 404, {"error": "not found"})
        if not _check_auth(self):
            return _json(self, 401, {"error": "unauthorized: missing or wrong API key"})
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            return _json(self, 400, {"error": "invalid JSON body"})
        messages = payload.get("messages")
        if not isinstance(messages, list) or not messages:
            return _json(self, 400, {"error": "messages must be a non-empty list"})
        for msg in messages:
            if not isinstance(msg, dict) or "content" not in msg or "role" not in msg:
                return _json(self, 400, {"error": "each message needs role and content"})
        # Force the configured model; the client may not silently swap models.
        payload["model"] = MODEL
        if not _llama_ok():
            return _json(self, 503, {"error": "model backend offline"})
        try:
            req = urllib.request.Request(
                LLAMA_URL + "/v1/chat/completions",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                if payload.get("stream"):
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    while True:
                        chunk = resp.read(4096)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                else:
                    body = resp.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(body)
        except urllib.error.HTTPError as exc:
            return _json(self, exc.code, {"error": f"backend returned HTTP {exc.code}"})
        except Exception as exc:
            return _json(self, 502, {"error": f"backend error: {exc}"})


if __name__ == "__main__":
    print(f"Gateway on :{PORT} -> {LLAMA_URL} | model={MODEL} | auth={'on' if API_KEY else 'off (set QWEN_API_KEY)'}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
