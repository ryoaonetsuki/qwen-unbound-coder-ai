#!/usr/bin/env python3
"""Real-model smoke test. Sends ONE prompt to a running gateway and prints
the genuine reply. It never contains a canned answer: an empty or error
reply is a FAIL, not a pass. Usage:
  GATEWAY_URL=https://... QWEN_API_KEY=... python3 scripts/test_live.py
"""
import json, os, sys, urllib.request

url = os.environ.get("GATEWAY_URL", "http://127.0.0.1:8000").rstrip("/")
key = os.environ.get("QWEN_API_KEY", "")
headers = {"Content-Type": "application/json"}
if key:
    headers["Authorization"] = "Bearer " + key
payload = {"messages": [{"role": "user", "content": "Write a Python function add(a, b) and return only code."}],
           "temperature": 0.2, "max_tokens": 128, "stream": False}
req = urllib.request.Request(url + "/v1/chat/completions",
                             data=json.dumps(payload).encode(), headers=headers, method="POST")
try:
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())
except Exception as exc:
    print(f"FAIL: request failed: {exc}"); sys.exit(1)
content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
print("MODEL:", data.get("model"))
print("REPLY:\n" + content)
if not content.strip():
    print("FAIL: empty reply"); sys.exit(1)
print("PASS: genuine non-empty model reply received")
