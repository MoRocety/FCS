#!/usr/bin/env python3
import json
import os
import subprocess
import time
import urllib.request
import base64
import websocket

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 9334
CHROME = "/usr/bin/google-chrome"
VIEWS = ['catalog','builder','saved','instructor','compare','course','willitfill','health','stress',
         'feed','review','wrapped','waitlist','monitor','protector','textbooks','commute',
         'agentchat','memory','proactive','history','degree','planner','substitute','chatbot','career']


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


def capture_view(ws, view, req_id):
    current = req_id[0]
    req_id[0] += 1
    expr = f"app.view = '{view}'; render(); 'ok'"
    ws.send(json.dumps({"id": current, "method": "Runtime.evaluate", "params": {"expression": expr, "returnByValue": True}}))
    recv_until(ws, current, timeout=5)
    time.sleep(0.8)
    current = req_id[0]
    req_id[0] += 1
    ws.send(json.dumps({"id": current, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
    result = recv_until(ws, current, timeout=5)
    data = result.get("result", {}).get("data", "")
    return base64.b64decode(data) if data else None


def main():
    proc = subprocess.Popen([
        CHROME, "--headless", "--disable-gpu", "--no-sandbox",
        f"--remote-debugging-port={PORT}",
        "--remote-allow-origins=*",
        "--window-size=1440,900",
        "about:blank"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        if not wait_for_devtools():
            raise RuntimeError("devtools did not start")
        ws_url = get_ws_url()
        ws = websocket.create_connection(ws_url, timeout=10)
        req_id = [1]
        # enable
        ws.send(json.dumps({"id": req_id[0], "method": "Page.enable"}))
        req_id[0] += 1
        recv_until(ws, req_id[0]-1, timeout=2)
        ws.send(json.dumps({"id": req_id[0], "method": "Runtime.enable"}))
        req_id[0] += 1
        recv_until(ws, req_id[0]-1, timeout=2)
        # navigate
        ws.send(json.dumps({"id": req_id[0], "method": "Page.navigate", "params": {"url": f"file://{ROOT}/phaseD/index.html"}}))
        req_id[0] += 1
        recv_until(ws, req_id[0]-1, timeout=5)
        time.sleep(2.5)

        out_dir = os.path.join(ROOT, "screenshots")
        os.makedirs(out_dir, exist_ok=True)
        for view in VIEWS:
            png = capture_view(ws, view, req_id)
            if png:
                path = os.path.join(out_dir, f"{view}.png")
                with open(path, "wb") as f:
                    f.write(png)
                print(f"saved {path}")
        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    main()
