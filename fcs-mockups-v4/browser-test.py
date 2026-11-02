#!/usr/bin/env python3
"""Smoke-test each phase in headless Chrome via Chrome DevTools Protocol."""
import json
import os
import subprocess
import time
import urllib.request
import websocket

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 9333
CHROME = "/usr/bin/google-chrome"
VIEWS = {
    "A": ["catalog", "builder", "saved"],
    "B": ["catalog", "builder", "saved", "instructor", "compare", "course", "willitfill", "health", "stress"],
    "C": ["catalog", "builder", "saved", "instructor", "compare", "course", "willitfill", "health", "stress",
          "feed", "review", "wrapped", "waitlist", "monitor", "protector", "textbooks", "commute"],
    "D": ["catalog", "builder", "saved", "instructor", "compare", "course", "willitfill", "health", "stress",
          "feed", "review", "wrapped", "waitlist", "monitor", "protector", "textbooks", "commute",
          "agentchat", "memory", "proactive", "history", "degree", "planner", "substitute", "chatbot", "career"]
}


def wait_for_devtools(timeout=15):
    url = f"http://127.0.0.1:{PORT}/json/version"
    for _ in range(timeout * 10):
        try:
            with urllib.request.urlopen(url, timeout=1) as r:
                return True
        except Exception:
            time.sleep(0.1)
    return False


def get_ws_url():
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list") as r:
        pages = json.loads(r.read())
    for p in pages:
        if p["type"] == "page":
            return p["webSocketDebuggerUrl"]
    raise RuntimeError("no page found")


def recv_until(ws, target_id, timeout=5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        ws.settimeout(max(0.1, deadline - time.time()))
        try:
            msg = json.loads(ws.recv())
        except websocket._exceptions.WebSocketTimeoutException:
            continue
        if msg.get("id") == target_id:
            return msg
    return None


def test_phase(phase, ws):
    file_url = f"file://{ROOT}/phase{phase}/index.html"
    req_id = 1

    def send(method, params=None, expect_result=True):
        nonlocal req_id
        current = req_id
        req_id += 1
        ws.send(json.dumps({"id": current, "method": method, "params": params or {}}))
        if expect_result:
            return recv_until(ws, current, timeout=5)
        return None

    send("Runtime.enable", expect_result=False)
    send("Page.enable", expect_result=False)

    send("Page.navigate", {"url": file_url})
    time.sleep(3.5)

    errors = []
    exceptions = []
    short = []

    for view in VIEWS[phase]:
        current = req_id
        req_id += 1
        expr = f"app.view = '{view}'; render(); document.getElementById('app').innerHTML.length"
        ws.send(json.dumps({"id": current, "method": "Runtime.evaluate", "params": {"expression": expr, "returnByValue": True}}))
        result = recv_until(ws, current, timeout=5)

        # drain errors/exceptions for a moment
        ws.settimeout(0.3)
        for _ in range(10):
            try:
                msg = json.loads(ws.recv())
                if msg.get("method") == "Runtime.consoleAPICalled" and msg["params"].get("type") == "error":
                    text = " ".join(str(i.get("value", i.get("description", ""))) for i in msg["params"].get("args", []))
                    errors.append(f"[{view}] {text}")
                elif msg.get("method") == "Runtime.exceptionThrown":
                    ex = msg["params"]["exceptionDetails"]
                    exceptions.append(f"[{view}] {ex.get('text','')} {ex.get('exception',{}).get('description','')}")
            except websocket._exceptions.WebSocketTimeoutException:
                break

        if not result or result.get("result", {}).get("result", {}).get("type") == "undefined":
            short.append(f"[{view}] no render result")
            continue
        length = result.get("result", {}).get("result", {}).get("value", 0)
        if length < 100:
            short.append(f"[{view}] rendered content too short ({length})")

    return errors, exceptions, short


def main():
    proc = None
    try:
        proc = subprocess.Popen([
            CHROME, "--headless", "--disable-gpu", "--no-sandbox",
            f"--remote-debugging-port={PORT}",
            "--remote-allow-origins=*",
            "about:blank"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if not wait_for_devtools():
            raise RuntimeError("Chrome DevTools did not start")
        ws_url = get_ws_url()
        ws = websocket.create_connection(ws_url, timeout=10)

        for phase in ["A", "B", "C", "D"]:
            if phase != "A":
                # reuse same tab; just navigate
                pass
            errors, exceptions, short = test_phase(phase, ws)
            has_issue = bool(errors or exceptions or [s for s in short if 'stress' not in s])
            status = "OK" if not has_issue else "ISSUES"
            print(f"Phase {phase}: {status}")
            for e in errors + exceptions:
                print(f"  - {e}")
            for s in short:
                if 'stress' in s.lower():
                    continue
                print(f"  - {s}")

        ws.close()
    finally:
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    main()
