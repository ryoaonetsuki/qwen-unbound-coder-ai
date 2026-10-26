"""Gateway unit tests — they test auth/validation/proxy logic ONLY, using a
local fake upstream. They do NOT prove the real model works; see test_live.py.
Run: python3 -m unittest discover -s tests -v
"""
import json, os, sys, threading, unittest, urllib.error, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from http.server import BaseHTTPRequestHandler, HTTPServer
import gateway

class FakeLlama(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
        elif self.path == "/v1/models":
            body = json.dumps({"data": [{"id": "test"}]}).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(body)
    def do_POST(self):
        body = json.dumps({"choices": [{"message": {"content": "FAKE-UPSTREAM-ONLY"}}], "model": "x"}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(body)

class TestGateway(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake = HTTPServer(("127.0.0.1", 0), FakeLlama)
        threading.Thread(target=cls.fake.serve_forever, daemon=True).start()
        gateway.LLAMA_URL = f"http://127.0.0.1:{cls.fake.server_address[1]}"
        gateway.API_KEY = "test-key-123"
        cls.gw = HTTPServer(("127.0.0.1", 0), gateway.Handler)
        threading.Thread(target=cls.gw.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.gw.server_address[1]}"

    def _post(self, headers=None):
        req = urllib.request.Request(self.base + "/v1/chat/completions",
            data=json.dumps({"messages": [{"role": "user", "content": "hi"}]}).encode(),
            headers=headers or {}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as r: return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e: return e.code, json.loads(e.read())

    def test_health_online(self):
        with urllib.request.urlopen(self.base + "/health", timeout=10) as r:
            self.assertEqual(json.loads(r.read())["backend_reachable"], True)

    def test_auth_missing_fails(self):
        status, _ = self._post({"Content-Type": "application/json"})
        self.assertEqual(status, 401)

    def test_auth_wrong_fails(self):
        status, _ = self._post({"Content-Type": "application/json", "Authorization": "Bearer wrong"})
        self.assertEqual(status, 401)

    def test_auth_ok_proxies(self):
        status, data = self._post({"Content-Type": "application/json", "Authorization": "Bearer test-key-123"})
        self.assertEqual(status, 200)
        self.assertIn("FAKE-UPSTREAM-ONLY", json.dumps(data))

    def test_empty_messages_rejected(self):
        req = urllib.request.Request(self.base + "/v1/chat/completions",
            data=json.dumps({"messages": []}).encode(),
            headers={"Content-Type": "application/json", "Authorization": "Bearer test-key-123"}, method="POST")
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=10)
        self.assertEqual(cm.exception.code, 400)

if __name__ == "__main__":
    unittest.main()
